# -*- coding: utf-8 -*-
"""
规范检查面板组件

基于PyQt5实现的完整规范检查面板UI。
提供项目级/文件级的PLC代码规范检查功能，
集成规则注册表、多线程检查引擎和结果可视化。

主要功能:
- 工具栏控制: 启动检查、范围选择、类别过滤
- 实时统计: 错误/警告/提示数量及通过率
- 结果列表: 支持排序、过滤、右键菜单、双击跳转
- 问题详情: 显示违规详情、代码片段、修复建议
- 后台检查: 使用QThread避免阻塞UI线程
"""
import os
from pathlib import Path
from typing import List, Optional

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTreeWidget,
    QTreeWidgetItem,
    QPushButton,
    QGroupBox,
    QTextBrowser,
    QLineEdit,
    QComboBox,
    QProgressBar,
    QMenu,
    QApplication,
    QFrame,
    QSizePolicy,
)
from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    QThread,
    QMutex,
    QWaitCondition,
)
from PyQt5.QtGui import QColor, QFont, QIcon, QCursor

from src.utils.logger import setup_logger
from src.checkers.rule_registry import RuleRegistry
from src.models.check_result import CheckReport, Violation
from src.checkers.base_checker import Severity

logger = setup_logger(__name__)


class CheckWorker(QThread):
    """
    检查工作线程

    在后台线程中执行规范检查任务，
    避免长时间检查操作阻塞UI线程。
    通过信号机制与主界面通信进度和结果。

    Attributes:
        project_path: 项目根目录路径
        file_path: 单文件检查时的目标文件路径（可选）
        category_filter: 规则类别过滤条件（空字符串表示不限制）
        _mutex: 线程安全互斥锁
        _is_cancelled: 取消标志
    """

    progress_updated = pyqtSignal(int, str)  # 进度百分比, 状态消息
    file_checked = pyqtSignal(str, int)  # 文件路径, 违规数
    check_completed = pyqtSignal(object)  # CheckReport对象
    error_occurred = pyqtSignal(str)  # 错误信息

    def __init__(
        self,
        project_path: str,
        file_path: Optional[str] = None,
        category_filter: str = "",
        parent=None,
    ):
        """
        初始化检查工作线程

        Args:
            project_path: 项目根目录路径
            file_path: 单文件检查路径（None表示全项目检查）
            category_filter: 规则类别过滤
            parent: 父对象
        """
        super().__init__(parent)
        self._project_path = project_path
        self._file_path = file_path
        self._category_filter = category_filter
        self._mutex = QMutex()
        self._is_cancelled = False
        logger.info(
            f"检查工作线程初始化完成 - "
            f"模式: {'单文件' if file_path else '全项目'}"
        )

    def run(self):
        """执行检查任务的主体方法"""
        try:
            registry = RuleRegistry.get_instance()

            # 获取适用的检查器列表
            if self._category_filter:
                checkers = registry.get_checkers_by_category(
                    self._category_filter
                )
                checkers = [c for c in checkers if c.is_enabled()]
            else:
                checkers = registry.get_all_checkers(enabled_only=True)

            total_checkers = len(checkers)

            if total_checkers == 0:
                self.progress_updated.emit(0, "未找到可用的检查器")
                report = CheckReport(
                    project_name=Path(self._project_path).name,
                    project_path=self._project_path,
                )
                self.check_completed.emit(report)
                return

            # 创建报告对象
            report = CheckReport(
                project_name=Path(self._project_path).name,
                project_path=self._project_path,
            )

            # 确定要检查的文件列表
            if self._file_path:
                files_to_check = [self._file_path]
            else:
                files_to_check = self._collect_st_files(self._project_path)

            total_files = len(files_to_check)

            if total_files == 0:
                self.progress_updated.emit(
                    100, "未找到ST源码文件"
                )
                self.check_completed.emit(report)
                return

            logger.info(f"开始检查 {total_files} 个文件, "
                       f"{total_checkers} 个规则")

            # 逐文件逐规则执行检查
            for file_idx, file_path in enumerate(files_to_check):
                # 检查取消状态
                self._mutex.lock()
                if self._is_cancelled:
                    self._mutex.unlock()
                    logger.info("检查任务被用户取消")
                    break
                self._mutex.unlock()

                # 更新进度
                progress = int((file_idx / total_files) * 100)
                file_name = Path(file_path).name
                self.progress_updated.emit(
                    progress,
                    f"正在检查: {file_name} ({file_idx + 1}/{total_files})",
                )

                # 读取文件内容
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        source_code = f.read()
                except Exception as e:
                    logger.error(f"读取文件失败: {file_path} - {e}")
                    continue

                # 执行所有检查器
                from src.models.check_result import CheckResult

                file_result = CheckResult(source_file=file_path)

                for checker in checkers:
                    # 再次检查取消状态
                    self._mutex.lock()
                    if self._is_cancelled:
                        self._mutex.unlock()
                        break
                    self._mutex.unlock()

                    try:
                        violations = checker.check(
                            source_code,
                            file_path=file_path,
                        )
                        if violations:
                            file_result.add_violations(violations)
                    except Exception as e:
                        logger.error(
                            f"检查器执行异常: "
                            f"{checker.rule_info.rule_id} - {e}"
                        )

                # 添加文件结果到报告
                report.add_result(file_result)

                # 发送单文件完成信号
                self.file_checked.emit(file_path, file_result.total_violations)

            # 检查完成
            final_progress = 100 if not self._is_cancelled else progress
            status_msg = "检查已完成" if not self._is_cancelled else "检查已取消"
            self.progress_updated.emit(final_progress, status_msg)
            self.check_completed.emit(report)

            logger.info(
                f"检查完成 - 总计: {report.total_violations}个问题, "
                f"错误:{report.total_errors}, "
                f"警告:{report.total_warnings}, "
                f"提示:{report.total_infos}"
            )

        except Exception as e:
            error_msg = f"检查过程发生异常: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)

    def cancel(self):
        """请求取消当前检查任务"""
        self._mutex.lock()
        self._is_cancelled = True
        self._mutex.unlock()
        logger.info("收到取消检查请求")

    def _collect_st_files(self, project_path: str) -> List[str]:
        """
        收集项目中所有的ST源码文件

        Args:
            project_path: 项目根目录

        Returns:
            List[str]: ST文件路径列表
        """
        st_extensions = {".st", ".TcPOU", ".st7"}
        st_files = []

        project_dir = Path(project_path)
        if not project_dir.exists():
            logger.warning(f"项目目录不存在: {project_path}")
            return st_files

        # 递归查找ST源码文件
        for ext in st_extensions:
            st_files.extend(
                [
                    str(p)
                    for p in project_dir.rglob(f"*{ext}")
                    if p.is_file()
                ]
            )

        # 排除测试文件和示例文件
        st_files = [
            f for f in st_files
            if "_test" not in f.lower()
               and "test_" not in f.lower()
               and "example" not in f.lower()
        ]

        logger.info(f"在项目中找到 {len(st_files)} 个ST源码文件")
        return sorted(st_files)


class SpecCheckPanel(QWidget):
    """
    规范检查面板主组件

    提供完整的PLC代码规范检查UI界面，
    包括工具栏控制、统计摘要、结果列表、过滤器和详情展示。

    Signals:
        check_started: 开始检查时发出
        check_finished: 检查完成时发出，携带CheckReport对象
        source_jump_requested: 用户请求跳转到源码位置时发出

    Usage:
        panel = SpecCheckPanel()
        panel.start_check("/path/to/project")
    """

    check_started = pyqtSignal()
    check_finished = pyqtSignal(object)  # CheckReport
    source_jump_requested = pyqtSignal(str, int)  # 文件路径, 行号

    # 严重级别到中文的映射
    SEVERITY_NAMES = {
        Severity.ERROR: "\u9519\u8BEF",
        Severity.WARNING: "\u8B66\u544A",
        Severity.INFO: "\u63D0\u793A",
    }

    # 严重级别对应的图标Unicode
    SEVERITY_ICONS = {
        Severity.ERROR: "\u274C",
        Severity.WARNING: "\u26A0\uFE0F",
        Severity.INFO: "\u2139\uFE0F",
    }

    # 严重级别对应的背景色
    SEVERITY_COLORS = {
        Severity.ERROR: "#FFEBEE",  # 红色背景
        Severity.WARNING: "#FFF3E0",  # 橙色背景
        Severity.INFO: "#E3F2FD",  # 蓝色背景
    }

    # 严重级别对应的前景色
    SEVERITY_FOREGROUND = {
        Severity.ERROR: "#C62828",
        Severity.WARNING: "#EF6C00",
        Severity.INFO: "#1565C0",
    }

    def __init__(self, parent=None):
        """
        初始化规范检查面板

        Args:
            parent: 父窗口组件
        """
        super().__init__(parent)
        self._current_report: Optional[CheckReport] = None
        self._check_worker: Optional[CheckWorker] = None
        self._all_violations: List[Violation] = []
        self._filtered_violations: List[Violation] = []
        self._init_ui()
        self._connect_signals()
        logger.info("规范检查面板初始化完成")

    def _init_ui(self):
        """初始化UI布局"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # ===== 1. 工具栏区域 =====
        toolbar = self._create_toolbar()
        main_layout.addLayout(toolbar)

        # ===== 2. 统计摘要区域 =====
        stats_group = self._create_stats_area()
        main_layout.addWidget(stats_group)

        # ===== 3. 过滤搜索栏 =====
        filter_bar = self._create_filter_bar()
        main_layout.addLayout(filter_bar)

        # ===== 4. 结果列表区域 =====
        result_group = self._create_result_list()
        main_layout.addWidget(result_group, stretch=1)

        # ===== 5. 问题详情区域 =====
        detail_group = self._create_detail_area()
        main_layout.addWidget(detail_group)

    def _create_toolbar(self) -> QHBoxLayout:
        """
        创建工具栏布局

        Returns:
            QHBoxLayout: 工具栏布局对象
        """
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        # 标题标签
        title_label = QLabel("\U0001F50D \u89C4\u8303\u68C0\u67E5\u9762\u677F")
        title_label.setStyleSheet(
            "font-size: 13pt; font-weight: bold; color: #1976D2;"
        )
        toolbar.addWidget(title_label)

        toolbar.addStretch()

        # 检查范围选择
        scope_label = QLabel("\u68C0\u67E5\u8303\u56F4:")
        scope_label.setStyleSheet("font-size: 10pt; color: #424242;")
        toolbar.addWidget(scope_label)

        self._scope_combo = QComboBox()
        self._scope_combo.addItems([
            "\u6574\u4E2A\u9879\u76EE",
            "\u5F53\u524D\u6587\u4EF6",
        ])
        self._scope_combo.setMinimumWidth(100)
        self._scope_combo.setStyleSheet("""
            QComboBox {
                padding: 4px 8px;
                border: 1px solid #BDBDBD;
                border-radius: 3px;
                background: white;
            }
            QComboBox:hover { border-color: #1976D2; }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #757575;
                margin-right: 5px;
            }
        """)
        toolbar.addWidget(self._scope_combo)

        # 规则类别过滤器
        category_label = QLabel("\u89C4\u5219\u7C7B\u522B:")
        category_label.setStyleSheet("font-size: 10pt; color: #424242;")
        toolbar.addWidget(category_label)

        self._category_combo = QComboBox()
        self._category_combo.setMinimumWidth(120)
        self._populate_category_combo()
        self._category_combo.setStyleSheet(self._scope_combo.styleSheet())
        toolbar.addWidget(self._category_combo)

        # 开始检查按钮（蓝色主按钮）
        self._btn_start_check = QPushButton(
            "\U0001F50D \u5F00\u59CB\u68C0\u67E5"
        )
        self._btn_start_check.setMinimumHeight(32)
        self._btn_start_check.setMinimumWidth(110)
        self._btn_start_check.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                border-radius: 4px;
                padding: 0 16px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover { background-color: #1565C0; }
            QPushButton:pressed { background-color: #0D47A1; }
            QPushButton:disabled {
                background-color: #BDBDBD;
                color: #757575;
            }
        """)
        toolbar.addWidget(self._btn_start_check)

        # 停止按钮（初始隐藏）
        self._btn_stop = QPushButton("\u23F9 \u505C\u6B62")
        self._btn_stop.setMinimumHeight(32)
        self._btn_stop.setMinimumWidth(70)
        self._btn_stop.setVisible(False)
        self._btn_stop.setStyleSheet("""
            QPushButton {
                background-color: #D32F2F;
                color: white;
                border-radius: 4px;
                padding: 0 12px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #B71C1C; }
        """)
        toolbar.addWidget(self._btn_stop)

        toolbar.addSpacing(10)

        # 进度条
        self._progress_bar = QProgressBar()
        self._progress_bar.setVisible(False)
        self._progress_bar.setMinimumHeight(20)
        self._progress_bar.setMaximumWidth(200)
        self._progress_bar.setTextVisible(True)
        self._progress_bar.setFormat("%p%")
        self._progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #BDBDBD;
                border-radius: 3px;
                text-align: center;
                background: #FAFAFA;
                color: #424242;
                font-size: 9pt;
            }
            QProgressBar::chunk {
                background-color: #1976D2;
                border-radius: 2px;
            }
        """)
        toolbar.addWidget(self._progress_bar)

        # 状态标签
        self._status_label = QLabel("\u51C6\u5907\u5C31\u7EEA")
        self._status_label.setStyleSheet(
            "font-size: 10pt; color: #757575;"
        )
        self._status_label.setMinimumWidth(150)
        toolbar.addWidget(self._status_label)

        return toolbar

    def _populate_category_combo(self):
        """填充规则类别下拉框"""
        self._category_combo.clear()
        self._category_combo.addItem("\u5168\u90E8\u7C7B\u522B", "")

        try:
            registry = RuleRegistry.get_instance()
            categories = registry.get_all_categories()
            for cat in sorted(categories):
                display_name = self._get_category_display_name(cat)
                self._category_combo.addItem(display_name, cat)
        except Exception as e:
            logger.warning(f"获取规则类别失败: {e}")

    @staticmethod
    def _get_category_display_name(category: str) -> str:
        """
        获取类别的中文显示名称

        Args:
            category: 英文类别标识

        Returns:
            str: 中文显示名称
        """
        category_names = {
            "naming": "\u547D\u540D\u89C4\u8303",
            "syntax": "\u8BED\u6CD5\u68C0\u67E5",
            "structure": "\u7ED3\u6784\u89C4\u8303",
            "safety": "\u5B89\u5168\u89C4\u5219",
            "comment": "\u6CE8\u91CA\u89C4\u8303",
            "config": "\u914D\u7F6E\u68C0\u67E5",
            "timer": "\u5B9A\u65F6\u5668\u68C0\u67E5",
        }
        return category_names.get(category, category)

    def _create_stats_area(self) -> QGroupBox:
        """
        创建统计摘要区域

        包含4个指标卡片：错误数、警告数、提示数、通过率

        Returns:
            QGroupBox: 统计摘要分组框
        """
        stats_group = QGroupBox("\U0001F4CA \u7EDF\u8BA1\u6458\u8981")
        stats_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 11pt;
                color: #424242;
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                margin-top: 8px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        stats_layout = QHBoxLayout(stats_group)
        stats_layout.setContentsMargins(10, 15, 10, 10)
        stats_layout.setSpacing(10)

        # 错误数卡片
        self._error_card = self._create_stat_card(
            title="\u9519\u8BEF\u6570",
            value="0",
            icon="\u274C",
            bg_color="#FFEBEE",
            fg_color="#C62828",
        )
        stats_layout.addWidget(self._error_card)

        # 警告数卡片
        self._warning_card = self._create_stat_card(
            title="\u8B66\u544A\u6570",
            value="0",
            icon="\u26A0\uFE0F",
            bg_color="#FFF3E0",
            fg_color="#EF6C00",
        )
        stats_layout.addWidget(self._warning_card)

        # 提示数卡片
        self._info_card = self._create_stat_card(
            title="\u63D0\u793A\u6570",
            value="0",
            icon="\u2139\uFE0F",
            bg_color="#E3F2FD",
            fg_color="#1565C0",
        )
        stats_layout.addWidget(self._info_card)

        # 通过率卡片
        self._pass_rate_card = self._create_stat_card(
            title="\u901A\u8FC7\u7387",
            value="100%",
            icon="\u2705",
            bg_color="#E8F5E9",
            fg_color="#2E7D32",
        )
        stats_layout.addWidget(self._pass_rate_card)

        return stats_group

    @staticmethod
    def _create_stat_card(
        title: str,
        value: str,
        icon: str,
        bg_color: str,
        fg_color: str,
    ) -> QFrame:
        """
        创建单个统计卡片

        Args:
            title: 卡片标题
            value: 初始值
            icon: 图标字符
            bg_color: 背景颜色
            fg_color: 前景颜色

        Returns:
            QFrame: 卡片框架
        """
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 6px;
                padding: 8px;
            }}
        """)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        # 标题行
        header = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 16pt;")
        header.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setStyleSheet(
            f"font-size: 10pt; color: {fg_color}; font-weight: bold;"
        )
        header.addWidget(title_label)
        header.addStretch()
        layout.addLayout(header)

        # 数值行
        value_label = QLabel(value)
        value_label.setObjectName("value_label")
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet(
            f"font-size: 22pt; font-weight: bold; color: {fg_color};"
        )
        layout.addWidget(value_label)

        return card

    def _update_stat_card(self, card: QFrame, new_value: str):
        """
        更新统计卡片的数值

        Args:
            card: 卡片控件
            new_value: 新的数值字符串
        """
        value_label = card.findChild(QLabel, "value_label")
        if value_label:
            value_label.setText(new_value)

    def _create_filter_bar(self) -> QHBoxLayout:
        """
        创建过滤搜索栏

        Returns:
            QHBoxLayout: 过滤栏布局
        """
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(8)

        # 搜索框
        search_icon = QLabel("\U0001F50D")
        search_icon.setStyleSheet("font-size: 12pt;")
        filter_layout.addWidget(search_icon)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText(
            "\u641C\u7D22\u95EE\u9898\u63CF\u8FF0..."
        )
        self._search_input.setMinimumWidth(200)
        self._search_input.setStyleSheet("""
            QLineEdit {
                padding: 5px 10px;
                border: 1px solid #BDBDBD;
                border-radius: 3px;
                background: white;
            }
            QLineEdit:focus { border-color: #1976D2; }
        """)
        filter_layout.addWidget(self._search_input)

        filter_layout.addStretch()

        # 严重级别过滤
        severity_label =QLabel("\u4E25\u91CD\u7EA7\u522B:")
        severity_label.setStyleSheet("font-size: 10pt; color: #424242;")
        filter_layout.addWidget(severity_label)

        self._severity_filter = QComboBox()
        self._severity_filter.addItems([
            "\u5168\u90E8",
            "\u9519\u8BEF",
            "\u8B66\u544A",
            "\u63D0\u793A",
        ])
        self._severity_filter.setMinimumWidth(80)
        self._severity_filter.setStyleSheet("""
            QComboBox {
                padding: 4px 8px;
                border: 1px solid #BDBDBD;
                border-radius: 3px;
                background: white;
            }
            QComboBox:hover { border-color: #1976D2; }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #757575;
                margin-right: 5px;
            }
        """)
        filter_layout.addWidget(self._severity_filter)

        # 类别过滤
        category_filter_label = QLabel("\u7C7B\u522B:")
        category_filter_label.setStyleSheet(
            "font-size: 10pt; color: #424242;"
        )
        filter_layout.addWidget(category_filter_label)

        self._result_category_filter = QComboBox()
        self._result_category_filter.addItem("\u5168\u90E8", "")
        self._result_category_filter.setMinimumWidth(100)
        self._result_category_filter.setStyleSheet(
            self._severity_filter.styleSheet()
        )
        filter_layout.addWidget(self._result_category_filter)

        return filter_layout

    def _create_result_list(self) -> QGroupBox:
        """
        创建结果列表区域

        Returns:
            QGroupBox: 结果列表分组框
        """
        result_group = QGroupBox("\U0001F4CB \u68C0\u67E5\u7ED3\u679C\u5217\u8868")
        result_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 11pt;
                color: #424242;
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                margin-top: 8px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        result_layout = QVBoxLayout(result_group)
        result_layout.setContentsMargins(8, 18, 8, 8)

        self._result_tree = QTreeWidget()
        self._result_tree.setHeaderLabels([
            "\u72B6\u6001",
            "\u4E25\u91CD\u7EA7\u522B",
            "\u89C4\u5219ID",
            "\u95EE\u9898\u63CF\u8FF0",
            "\u6587\u4EF6\u540D",
            "\u884C\u53F7",
        ])

        # 设置列宽
        column_widths = [60, 80, 100, 280, 160, 60]
        for i, width in enumerate(column_widths):
            self._result_tree.setColumnWidth(i, width)

        # 设置树形控件样式
        self._result_tree.setAlternatingRowColors(True)
        self._result_tree.setSelectionBehavior(
            QTreeWidget.SelectRows
        )
        self._result_tree.setSortingEnabled(True)
        self._result_tree.sortByColumn(1, Qt.DescendingOrder)  # 默认按严重级别降序
        self._result_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self._result_tree.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #E0E0E0;
                border-radius: 3px;
                background: white;
                gridline-color: #F5F5F5;
            }
            QTreeWidget::item {
                padding: 4px;
                min-height: 24px;
            }
            QTreeWidget::item:selected {
                background-color: #E3F2FD;
                color: #1565C0;
            }
            QTreeWidget::item:hover {
                background-color: #F5F5F5;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                padding: 6px;
                border: none;
                border-bottom: 2px solid #E0E0E0;
                font-weight: bold;
                font-size: 10pt;
                color: #424242;
            }
        """)

        result_layout.addWidget(self._result_tree)

        # 结果计数标签
        self._result_count_label = QLabel(
            "\u5171 0 \u6761\u8BB0\u5F55"
        )
        self._result_count_label.setStyleSheet(
            "font-size: 9pt; color: #757575;"
        )
        self._result_count_label.setAlignment(
            Qt.AlignRight | Qt.AlignVCenter
        )
        result_layout.addWidget(self._result_count_label)

        return result_group

    def _create_detail_area(self) -> QGroupBox:
        """
        创建问题详情区域

        Returns:
            QGroupBox: 详情区域分组框
        """
        detail_group = QGroupBox(
            "\U0001F4DD \u95EE\u9898\u8BE6\u60C5"
        )
        detail_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 11pt;
                color: #424242;
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                margin-top: 8px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        detail_layout = QVBoxLayout(detail_group)
        detail_layout.setContentsMargins(8, 18, 8, 8)

        self._detail_browser = QTextBrowser()
        self._detail_browser.setOpenExternalLinks(False)
        self._detail_browser.setMinimumHeight(140)
        self._detail_browser.setStyleSheet("""
            QTextBrowser {
                border: 1px solid #E0E0E0;
                border-radius: 3px;
                background: #FAFAFA;
                padding: 8px;
                font-family: "Consolas", "Courier New", monospace;
                font-size: 10pt;
            }
        """)
        detail_layout.addWidget(self._detail_browser)

        return detail_group

    def _connect_signals(self):
        """连接所有信号槽"""
        # 工具栏按钮
        self._btn_start_check.clicked.connect(self._on_start_check)
        self._btn_stop.clicked.connect(self._on_stop_check)

        # 过滤器
        self._search_input.textChanged.connect(self.apply_filter)
        self._severity_filter.currentIndexChanged.connect(self.apply_filter)
        self._result_category_filter.currentIndexChanged.connect(
            self.apply_filter
        )

        # 结果列表交互
        self._result_tree.itemClicked.connect(
            self._on_item_selected
        )
        self._result_tree.itemDoubleClicked.connect(
            self._on_item_double_clicked
        )
        self._result_tree.customContextMenuRequested.connect(
            self._show_context_menu
        )

    def start_check(
        self,
        project_path: str,
        file_path: Optional[str] = None,
    ):
        """
        启动后台检查线程

        Args:
            project_path: 项目根目录路径
            file_path: 单文件检查路径（可选）
        """
        # 如果已有检查在进行中，先停止
        if self._check_worker and self._check_worker.isRunning():
            self._on_stop_check()
            import time
            time.sleep(0.3)  # 等待线程停止

        # 获取过滤参数
        scope_index = self._scope_combo.currentIndex()
        target_file = file_path if scope_index == 1 else None

        category_data = self._category_combo.currentData()
        category_filter = category_data if category_data else ""

        # 清空之前的结果
        self._clear_results()

        # 更新UI状态为检查中
        self._set_checking_ui_state(True)

        # 发出开始检查信号
        self.check_started.emit()

        # 创建并启动工作线程
        self._check_worker = CheckWorker(
            project_path=project_path,
            file_path=target_file,
            category_filter=category_filter,
        )

        # 连接工作线程信号
        self._check_worker.progress_updated.connect(
            self._on_progress_updated
        )
        self._check_worker.file_checked.connect(
            self._on_file_checked
        )
        self._check_worker.check_completed.connect(
            self.on_check_finished
        )
        self._check_worker.error_occurred.connect(
            self._on_check_error
        )

        # 启动线程
        self._check_worker.start()

        logger.info(
            f"检查任务已启动 - "
            f"路径: {project_path}, "
            f"模式: {'单文件' if target_file else '全项目'}"
        )

    def on_check_finished(self, report: CheckReport):
        """
        检查完成回调

        Args:
            report: 检查报告对象
        """
        # 保存报告引用
        self._current_report = report

        # 提取所有违规记录
        self._all_violations = []
        for result in report.results:
            self._all_violations.extend(result.violations)

        # 应用过滤并更新UI
        self.apply_filter()

        # 更新统计卡片
        self._update_statistics(report)

        # 更新结果类别过滤器
        self._update_result_category_filter()

        # 恢复UI状态
        self._set_checking_ui_state(False)

        # 更新状态文本
        self._status_label.setText(
            f"\u68C0\u67E5\u5B8C\u6210 - "
            f"\u5171{report.total_violations}\u4E2A\u95EE\u9898"
        )

        # 发出检查完成信号
        self.check_finished.emit(report)

        logger.info(
            f"检查完成回调处理完毕 - "
            f"总计: {len(self._all_violations)} 条记录"
        )

    def apply_filter(self):
        """
        应用过滤条件

        根据搜索关键词、严重级别和类别过滤违规记录列表，
        并更新结果显示。

        性能优化说明：
        - 使用生成器表达式而非列表推导式减少内存分配
        - 提前计算searchable_text避免重复字符串拼接
        - 短路求值：优先检查快速条件（严重级别），后检查慢速条件（文本搜索）
        - 对于大型项目（>1000条违规），建议考虑使用QSortFilterProxyModel替代
        """
        if not self._all_violations:
            self._filtered_violations = []
            self._refresh_result_tree()
            return

        # 获取过滤条件
        search_text = self._search_input.text().strip().lower()
        severity_index = self._severity_filter.currentIndex()
        category_data = self._result_category_filter.currentData()

        # 严重级别映射
        severity_map = {
            0: None,  # 全部
            1: Severity.ERROR,
            2: Severity.WARNING,
            3: Severity.INFO,
        }
        target_severity = severity_map.get(severity_index)

        # 执行过滤
        filtered = []

        for violation in self._all_violations:
            # [性能优化点1] 快速条件前置：严重级别判断是O(1)操作
            if target_severity is not None:
                if violation.severity != target_severity:
                    continue

            # [性能优化点2] 中等速度条件：类别前缀提取
            if category_data:
                # 从规则ID提取类别前缀
                rule_category = violation.rule_id.split("_")[0].lower()
                if rule_category != category_data.lower():
                    continue

            # [性能优化点3] 慢速条件后置：文本搜索仅在需要时执行
            if search_text:
                # 预拼接可搜索文本，避免多次属性访问
                searchable_text = (
                    f"{violation.message} "
                    f"{violation.rule_id} "
                    f"{violation.file_path} "
                    f"{violation.suggestion or ''}"
                ).lower()
                if search_text not in searchable_text:
                    continue

            filtered.append(violation)

        self._filtered_violations = filtered
        self._refresh_result_tree()

    def _refresh_result_tree(self):
        """刷新结果列表显示"""
        self._result_tree.setUpdatesEnabled(False)

        # 保存当前选中项
        current_item = self._result_tree.currentItem()
        selected_data = None
        if current_item:
            selected_data = current_item.data(0, Qt.UserRole)

        # 清空列表
        self._result_tree.clear()

        # 填充过滤后的数据
        for violation in self._filtered_violations:
            item = self._create_tree_item(violation)
            self._result_tree.addTopLevelItem(item)

            # 恢复选中状态
            if selected_data and selected_data == id(violation):
                self._result_tree.setCurrentItem(item)

        # 更新计数标签
        count = len(self._filtered_violations)
        total = len(self._all_violations)
        self._result_count_label.setText(
            f"\u663E\u793A {count} / {total} \u6761\u8BB0\u5F55"
        )

        self._result_tree.setUpdatesEnabled(True)

    def _create_tree_item(self, violation: Violation) -> QTreeWidgetItem:
        """
        创建单个违规记录的树形项

        Args:
            violation: 违规记录对象

        Returns:
            QTreeWidgetItem: 树形项
        """
        item = QTreeWidgetItem()

        # 状态图标
        severity_icon = self.SEVERITY_ICONS.get(
            violation.severity, "?"
        )
        item.setText(0, severity_icon)

        # 严重级别
        severity_name = self.SEVERITY_NAMES.get(
            violation.severity, "\u672A\u77E5"
        )
        item.setText(1, severity_name)

        # 规则ID
        item.setText(2, violation.rule_id)

        # 问题描述（截断过长文本）
        description = violation.message
        if len(description) > 50:
            description = description[:47] + "..."
        item.setText(3, description)
        item.setToolTip(3, violation.message)

        # 文件名
        file_name = Path(violation.file_path).name if violation.file_path else "-"
        item.setText(4, file_name)
        item.setToolTip(4, violation.file_path or "")

        # 行号
        line_str = str(violation.line_number) if violation.line_number > 0 else "-"
        item.setText(5, line_str)

        # 设置背景色
        bg_color = self.SEVERITY_COLORS.get(
            violation.severity, "#FFFFFF"
        )
        fg_color = self.SEVERITY_FOREGROUND.get(
            violation.severity, "#424242"
        )
        for col in range(6):
            item.setBackground(col, QColor(bg_color))
            item.setForeground(col, QColor(fg_color))

        # 存储原始数据用于后续访问
        item.setData(0, Qt.UserRole, id(violation))
        item.setData(0, Qt.UserRole + 1, violation)

        return item

    def _update_statistics(self, report: CheckReport):
        """
        更新统计摘要卡片

        Args:
            report: 检查报告
        """
        # 更新错误数
        self._update_stat_card(
            self._error_card, str(report.total_errors)
        )

        # 更新警告数
        self._update_stat_card(
            self._warning_card, str(report.total_warnings)
        )

        # 更新提示数
        self._update_stat_card(
            self._info_card, str(report.total_infos)
        )

        # 更新通过率
        pass_rate = f"{report.pass_rate:.1f}%"
        self._update_stat_card(
            self._pass_rate_card, pass_rate
        )

    def _update_result_category_filter(self):
        """根据检查结果更新结果类别过滤器"""
        # 收集中出现的类别
        categories = set()
        for v in self._all_violations:
            if "_" in v.rule_id:
                cat = v.rule_id.split("_")[0]
                categories.add(cat)

        # 保存当前选择
        current_data = self._result_category_filter.currentData()

        # 重建选项
        self._result_category_filter.blockSignals(True)
        self._result_category_filter.clear()
        self._result_category_filter.addItem("\u5168\u90E8", "")

        for cat in sorted(categories):
            display_name = self._get_category_display_name(cat)
            self._result_category_filter.addItem(display_name, cat)

        # 尝试恢复选择
        if current_data:
            index = self._result_category_filter.findData(current_data)
            if index >= 0:
                self._result_category_filter.setCurrentIndex(index)

        self._result_category_filter.blockSignals(False)

    def _on_progress_updated(self, progress: int, message: str):
        """
        处理进度更新信号

        Args:
            progress: 进度百分比 (0-100)
            message: 状态消息
        """
        self._progress_bar.setValue(progress)
        self._status_label.setText(message)

    def _on_file_checked(self, file_path: str, violation_count: int):
        """
        处理单文件检查完成信号

        Args:
            file_path: 已检查的文件路径
            violation_count: 发现的违规数
        """
        file_name = Path(file_path).name
        logger.debug(
            f"文件检查完成: {file_name} - {violation_count} 个问题"
        )

    def _on_item_selected(self, item: QTreeWidgetItem, column: int):
        """
        处理结果项选中事件

        Args:
            item: 选中的树形项
            column: 点击的列索引
        """
        violation = item.data(0, Qt.UserRole + 1)
        if isinstance(violation, Violation):
            self._show_violation_detail(violation)

    def _on_item_double_clicked(
        self, item: QTreeWidgetItem, column: int
    ):
        """
        处理结果项双击事件，触发源码跳转

        Args:
            item: 双击的树形项
            column: 双击的列索引
        """
        violation = item.data(0, Qt.UserRole + 1)
        if isinstance(violation, Violation):
            if violation.file_path and violation.line_number > 0:
                self.source_jump_requested.emit(
                    violation.file_path,
                    violation.line_number,
                )
                logger.info(
                    f"请求跳转到源码: {violation.file_path}:"
                    f"{violation.line_number}"
                )

    def _show_context_menu(self, position):
        """
        显示右键上下文菜单

        Args:
            position: 鼠标点击位置
        """
        item = self._result_tree.itemAt(position)
        if not item:
            return

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                border: 1px solid #E0E0E0;
                border-radius: 3px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 2px;
            }
            QMenu::item:selected {
                background-color: #E3F2FD;
                color: #1565C0;
            }
        """)

        # 跳转到源码
        jump_action = menu.addAction(
            "\U0001F517 \u8DF3\u8F6C\u5230\u6E90\u7801\u4F4D\u7F6E"
        )
        jump_action.triggered.connect(
            lambda: self._on_item_double_clicked(item, 0)
        )

        # 复制问题描述
        copy_action = menu.addAction(
            "\U0001F4CB \u590D\u5236\u95EE\u9898\u63CF\u8FF0"
        )
        copy_action.triggered.connect(lambda: self._copy_issue_description(item))

        menu.addSeparator()

        # 定位到此文件的全部问题
        locate_action = menu.addAction(
            "\U0001F50D \u5B9A\u4F4D\u6B64\u6587\u4EF6\u7684\u5168\u90E8\u95EE\u9898"
        )
        locate_action.triggered.connect(
            lambda: self._locate_file_issues(item)
        )

        menu.exec_(self._result_tree.mapToGlobal(position))

    def _copy_issue_description(self, item: QTreeWidgetItem):
        """
        复制问题描述到剪贴板

        Args:
            item: 树形项
        """
        violation = item.data(0, Qt.UserRole + 1)
        if isinstance(violation, Violation):
            clipboard = QApplication.clipboard()
            text = f"[{violation.rule_id}] {violation.message}"
            clipboard.setText(text)
            logger.info("已复制问题描述到剪贴板")

    def _locate_file_issues(self, item: QTreeWidgetItem):
        """
        定位并高亮显示指定文件的所有问题

        Args:
            item: 树形项
        """
        violation = item.data(0, Qt.UserRole + 1)
        if isinstance(violation, Violation) and violation.file_path:
            # 在搜索框中输入文件名进行过滤
            file_name = Path(violation.file_path).name
            self._search_input.setText(file_name)
            logger.info(f"定位文件: {file_name}")

    def _show_violation_detail(self, violation: Violation):
        """
        显示违规问题的详细信息

        Args:
            violation: 违规记录对象
        """
        severity_name = self.SEVERITY_NAMES.get(
            violation.severity, "\u672A\u77E5"
        )
        severity_icon = self.SEVERITY_ICONS.get(
            violation.severity, "?"
        )

        html_content = f"""
        <div style="font-family: 'Microsoft YaHei', sans-serif;">
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="background-color: #F5F5F5;">
                    <td style="padding: 8px; font-weight: bold; width: 100px;">
                        {severity_icon} \u4E25\u91CD\u7EA7\u522B:
                    </td>
                    <td style="padding: 8px; color: {self.SEVERITY_FOREGROUND.get(violation.severity, '#424242')};
                        font-weight: bold;">
                        {severity_name}
                    </td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold;">\u89C4\u5219ID:</td>
                    <td style="padding: 8px;">{violation.rule_id}</td>
                </tr>
                <tr style="background-color: #F5F5F5;">
                    <td style="padding: 8px; font-weight: bold;">\u63CF\u8FF0:</td>
                    <td style="padding: 8px;">{violation.message}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold;">\u4F4D\u7F6E:</td>
                    <td style="padding: 8px;">{violation.location_str}</td>
                </tr>
            </table>
        """

        # 代码片段
        if violation.code_snippet:
            escaped_snippet = violation.code_snippet.replace(
                "<", "&lt;"
            ).replace(">", "&gt;")
            html_content += f"""
            <div style="margin-top: 12px;">
                <b>\U0001F4DD \u4EE3\u7801\u7247\u6BB5:</b>
                <pre style="
                    background-color: #263238;
                    color: #ECEFF1;
                    padding: 10px;
                    border-radius: 4px;
                    overflow-x: auto;
                    font-family: Consolas, monospace;
                    font-size: 10pt;
                    margin: 6px 0;
                ">{escaped_snippet}</pre>
            </div>
            """

        # 修复建议
        if violation.suggestion:
            html_content += f"""
            <div style="margin-top: 12px;">
                <b>\U0001F4A1 \u4FEE\u590D\u5EFA\u8BAE:</b>
                <div style="
                    background-color: #E8F5E9;
                    color: #2E7D32;
                    padding: 10px;
                    border-radius: 4px;
                    margin: 6px 0;
                    border-left: 4px solid #4CAF50;
                ">{violation.suggestion}</div>
            </div>
            """

        html_content += "</div>"

        self._detail_browser.setHtml(html_content)

    def _set_checking_ui_state(self, is_checking: bool):
        """
        设置检查中的UI状态

        Args:
            is_checking: 是否处于检查状态
        """
        self._btn_start_check.setEnabled(not is_checking)
        self._btn_start_check.setVisible(not is_checking)
        self._btn_stop.setVisible(is_checking)
        self._progress_bar.setVisible(is_checking)

        if is_checking:
            self._status_label.setText("\u6B63\u5728\u68C0\u67E5...")
            self._progress_bar.setValue(0)

    def _clear_results(self):
        """清空所有检查结果"""
        self._current_report = None
        self._all_violations = []
        self._filtered_violations = []
        self._result_tree.clear()
        self._detail_browser.clear()
        self._search_input.clear()
        self._severity_filter.setCurrentIndex(0)
        self._result_category_filter.setCurrentIndex(0)

        # 重置统计卡片
        self._update_stat_card(self._error_card, "0")
        self._update_stat_card(self._warning_card, "0")
        self._update_stat_card(self._info_card, "0")
        self._update_stat_card(self._pass_rate_card, "100%")

        self._result_count_label.setText("\u5171 0 \u6761\u8BB0\u5F55")

    def _on_start_check(self):
        """处理开始检查按钮点击事件"""
        # 此方法通常由外部调用start_check()触发
        # 这里仅作为备用入口
        logger.info("开始检查按钮被点击")

    def _on_stop_check(self):
        """处理停止按钮点击事件"""
        if self._check_worker and self._check_worker.isRunning():
            self._check_worker.cancel()
            logger.info("用户请求停止检查")

    def _on_check_error(self, error_message: str):
        """
        处理检查过程中的错误

        Args:
            error_message: 错误信息
        """
        self._set_checking_ui_state(False)
        self._status_label.setText(f"\u274C \u68C0\u67E5\u51FA\u9519: {error_message}")
        logger.error(f"检查出错: {error_message}")

    def get_current_report(self) -> Optional[CheckReport]:
        """
        获取当前的检查报告

        Returns:
            Optional[CheckReport]: 当前报告对象，无报告时返回None
        """
        return self._current_report

    def clear_all(self):
        """公开接口：清空所有数据和UI状态"""
        self._clear_results()
        self._status_label.setText("\u51C6\u5907\u5C31\u7EEA")
