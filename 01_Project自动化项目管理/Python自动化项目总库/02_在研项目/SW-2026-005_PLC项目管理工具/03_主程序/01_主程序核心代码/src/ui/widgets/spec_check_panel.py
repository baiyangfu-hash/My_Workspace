# -*- coding: utf-8 -*-
import os
from pathlib import Path
from typing import List, Optional, Dict, Any

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
    QCheckBox,
    QGridLayout,
    QScrollArea,
)
from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    QThread,
    QMutex,
)
from PyQt5.QtGui import QColor, QFont, QCursor

from src.utils.logger import setup_logger
from src.checkers.rule_registry import RuleRegistry
from src.models.check_result import CheckReport, Violation
from src.checkers.base_checker import Severity

logger = setup_logger(__name__)

CHECKERS = [
    {"id": "syntax", "name": "语法检查", "icon": "📝", "engine": "trae",
     "desc": "SCL语法错误·关键字·括号匹配·类型推断", "stats": "0违规·218通过", "default": True},
    {"id": "comment", "name": "注释检查", "icon": "📝", "engine": "trae",
     "desc": "中文标点·嵌套注释·注释完整性", "stats": "2警告·156通过", "default": True},
    {"id": "naming", "name": "命名规范", "icon": "🧱", "engine": "python",
     "desc": "变量/函数块/常量命名·前缀后缀规则", "stats": "0违规·453通过", "default": False},
    {"id": "variable", "name": "变量检查", "icon": "📦", "engine": "hybrid",
     "desc": "声明未使用·类型一致性·作用域分析", "stats": "3警告·201通过", "default": True},
    {"id": "config", "name": "配置检查", "icon": "⚙", "engine": "python",
     "desc": "项目配置完整性·路径有效性·依赖版本", "stats": "0违规·89通过", "default": False},
    {"id": "timer", "name": "定时器检查", "icon": "⏱", "engine": "python",
     "desc": "TON/TOF/TP使用模式·预设值范围", "stats": "0违规·42通过", "default": False},
    {"id": "fb_iface", "name": "FB接口调用", "icon": "🔗", "engine": "hybrid",
     "desc": "OB1调用参数匹配·缺参/多参·IN_OUT对齐", "stats": "0违规·67通过", "default": True},
]


class CheckerCard(QFrame):
    toggled = pyqtSignal(str, bool)

    def __init__(self, checker_id: str, name: str, icon: str, engine_type: str,
                 description: str, stats_text: str, checked: bool = True, parent=None):
        super().__init__(parent)
        self._checker_id = checker_id
        self._engine_type = engine_type

        self.setProperty("CheckerCard", "selected" if checked else "unselected")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(72)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)

        self._checkbox = QCheckBox()
        self._checkbox.setChecked(checked)
        self._checkbox.setFixedSize(18, 18)
        self._checkbox.setStyleSheet("""
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #555;
                border-radius: 3px;
                background: transparent;
            }
            QCheckBox::indicator:checked {
                background: #4EC9B0;
                border-color: #4EC9B0;
                image: url(none);
            }
            QCheckBox::indicator:checked::after {
                content: "✓";
                color: white;
                font-weight: bold;
            }
        """)
        layout.addWidget(self._checkbox)

        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)

        name_row = QHBoxLayout()
        name_row.setSpacing(6)

        icon_label = QLabel(icon)
        icon_label.setFixedSize(16, 16)
        icon_label.setAlignment(Qt.AlignCenter)
        name_row.addWidget(icon_label)

        name_label = QLabel(name)
        name_label.setProperty("cardName", True)
        name_row.addWidget(name_label)

        name_row.addStretch()
        content_layout.addLayout(name_row)

        desc_label = QLabel(description)
        desc_label.setProperty("cardDesc", True)
        desc_label.setWordWrap(True)
        content_layout.addWidget(desc_label)

        stats_label = QLabel(stats_text)
        stats_label.setProperty("cardStats", True)
        content_layout.addWidget(stats_label)

        layout.addLayout(content_layout, stretch=1)

        badge = QLabel(engine_type.upper())
        badge.setProperty("EngineBadge", engine_type)
        badge.setAlignment(Qt.AlignCenter)
        badge.setMinimumWidth(50)
        layout.addWidget(badge)

        self._checkbox.toggled.connect(self._on_checkbox_toggled)
        self.mousePressEvent = self._on_mouse_press

    def _on_checkbox_toggled(self, checked: bool):
        state = "selected" if checked else "unselected"
        self.setProperty("CheckerCard", state)
        self.style().unpolish(self)
        self.style().polish(self)
        self.toggled.emit(self._checker_id, checked)

    def _on_mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self._checkbox.setChecked(not self._checkbox.isChecked())

    @property
    def checker_id(self) -> str:
        return self._checker_id

    @property
    def is_checked(self) -> bool:
        return self._checkbox.isChecked()

    def set_checked(self, checked: bool):
        self._checkbox.blockSignals(True)
        self._checkbox.setChecked(checked)
        self._checkbox.blockSignals(False)
        state = "selected" if checked else "unselected"
        self.setProperty("CheckerCard", state)
        self.style().unpolish(self)
        self.style().polish(self)

    def update_stats(self, stats_text: str):
        stats_label = self.findChild(QLabel, "stats_label") or None
        for child in self.findChildren(QLabel):
            if child.property("cardStats"):
                child.setText(stats_text)
                break


class CheckWorker(QThread):

    progress_updated = pyqtSignal(int, str)
    file_checked = pyqtSignal(str, int)
    check_completed = pyqtSignal(object)
    error_occurred = pyqtSignal(str)

    def __init__(
        self,
        project_path: str,
        file_path: Optional[str] = None,
        category_filter: str = "",
        selected_checkers: Optional[List[str]] = None,
        parent=None,
    ):
        super().__init__(parent)
        self._project_path = project_path
        self._file_path = file_path
        self._category_filter = category_filter
        self._selected_checkers = selected_checkers or []
        self._mutex = QMutex()
        self._is_cancelled = False
        logger.info(
            f"检查工作线程初始化完成 - "
            f"模式: {'单文件' if file_path else '全项目'}"
        )

    def run(self):
        try:
            registry = RuleRegistry.get_instance()

            if self._category_filter:
                checkers = registry.get_checkers_by_category(
                    self._category_filter
                )
                checkers = [c for c in checkers if c.is_enabled()]
            else:
                checkers = registry.get_all_checkers(enabled_only=True)

            if self._selected_checkers:
                checkers = [c for c in checkers if getattr(c, 'checker_id', '') in self._selected_checkers]

            total_checkers = len(checkers)

            if total_checkers == 0:
                self.progress_updated.emit(0, "未找到可用的检查器")
                report = CheckReport(
                    project_name=Path(self._project_path).name,
                    project_path=self._project_path,
                )
                self.check_completed.emit(report)
                return

            report = CheckReport(
                project_name=Path(self._project_path).name,
                project_path=self._project_path,
            )

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

            for file_idx, file_path in enumerate(files_to_check):
                self._mutex.lock()
                if self._is_cancelled:
                    self._mutex.unlock()
                    logger.info("检查任务被用户取消")
                    break
                self._mutex.unlock()

                progress = int((file_idx / total_files) * 100)
                file_name = Path(file_path).name
                self.progress_updated.emit(
                    progress,
                    f"正在检查: {file_name} ({file_idx + 1}/{total_files})",
                )

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        source_code = f.read()
                except Exception as e:
                    logger.error(f"读取文件失败: {file_path} - {e}")
                    continue

                from src.models.check_result import CheckResult

                file_result = CheckResult(source_file=file_path)

                for checker in checkers:
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

                report.add_result(file_result)

                self.file_checked.emit(file_path, file_result.total_violations)

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
        self._mutex.lock()
        self._is_cancelled = True
        self._mutex.unlock()
        logger.info("收到取消检查请求")

    def _collect_st_files(self, project_path: str) -> List[str]:
        st_extensions = {".st", ".TcPOU", ".st7"}
        st_files = []

        project_dir = Path(project_path)
        if not project_dir.exists():
            logger.warning(f"项目目录不存在: {project_path}")
            return st_files

        for ext in st_extensions:
            st_files.extend(
                [
                    str(p)
                    for p in project_dir.rglob(f"*{ext}")
                    if p.is_file()
                ]
            )

        st_files = [
            f for f in st_files
            if "_test" not in f.lower()
               and "test_" not in f.lower()
               and "example" not in f.lower()
        ]

        logger.info(f"在项目中找到 {len(st_files)} 个ST源码文件")
        return sorted(st_files)


class FBIFCCheckWorker(QThread):

    fb_ifc_check_completed = pyqtSignal(object)
    error_occurred = pyqtSignal(str)

    def __init__(
        self,
        ob1_path: str,
        project_path: str,
        syslib_path: Optional[str] = None,
        parent=None,
    ):
        super().__init__(parent)
        self._ob1_path = ob1_path
        self._project_path = project_path
        self._syslib_path = syslib_path
        logger.info(
            f"FB接口检查工作线程初始化完成 - "
            f"OB1: {os.path.basename(ob1_path)}"
        )

    def run(self):
        try:
            from src.checkers.fb_interface_checker import FBInterfaceChecker

            checker = FBInterfaceChecker()

            with open(self._ob1_path, "r", encoding="utf-8") as f:
                source = f.read()

            violations = checker.check(
                source,
                file_path=self._ob1_path,
                context={
                    "project_path": self._project_path,
                    "syslib_path": self._syslib_path,
                },
            )

            logger.info(
                f"FB接口检查完成 - 发现 {len(violations)} 个问题"
            )
            self.fb_ifc_check_completed.emit(violations)

        except Exception as e:
            error_msg = f"FB接口检查异常: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)


class SpecCheckPanel(QWidget):

    check_started = pyqtSignal()
    check_finished = pyqtSignal(object)
    source_jump_requested = pyqtSignal(str, int)
    checker_toggled = pyqtSignal(str, bool)

    SEVERITY_NAMES = {
        Severity.ERROR: "\u9519\u8BEF",
        Severity.WARNING: "\u8B66\u544A",
        Severity.INFO: "\u63D0\u793A",
    }

    SEVERITY_ICONS = {
        Severity.ERROR: "\u274C",
        Severity.WARNING: "\u26A0\uFE0F",
        Severity.INFO: "\u2139\uFE0F",
    }

    SEVERITY_COLORS = {
        Severity.ERROR: "#FFEBEE",
        Severity.WARNING: "#FFF3E0",
        Severity.INFO: "#E3F2FD",
    }

    SEVERITY_FOREGROUND = {
        Severity.ERROR: "#C62828",
        Severity.WARNING: "#EF6C00",
        Severity.INFO: "#1565C0",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_report: Optional[CheckReport] = None
        self._check_worker: Optional[CheckWorker] = None
        self._all_violations: List[Violation] = []
        self._filtered_violations: List[Violation] = []
        self._current_project_path: Optional[str] = None
        self._checker_cards: Dict[str, CheckerCard] = {}
        self._init_ui()
        self._connect_signals()
        logger.info("规范检查面板初始化完成")

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        title_label = QLabel("\U0001F50D \u89C4\u8303\u68C0\u67E5")
        title_label.setProperty("panelTitle", True)
        main_layout.addWidget(title_label)

        cards_container = self._create_checker_cards_grid()
        main_layout.addWidget(cards_container)

        action_bar = self._create_action_bar()
        main_layout.addLayout(action_bar)

        result_panel = self._create_result_panel()
        main_layout.addWidget(result_panel, stretch=1)

    def _create_checker_cards_grid(self) -> QWidget:
        container = QWidget()
        grid_layout = QGridLayout(container)
        grid_layout.setHorizontalSpacing(10)
        grid_layout.setVerticalSpacing(10)

        for idx, checker_def in enumerate(CHECKERS):
            card = CheckerCard(
                checker_id=checker_def["id"],
                name=checker_def["name"],
                icon=checker_def["icon"],
                engine_type=checker_def["engine"],
                description=checker_def["desc"],
                stats_text=checker_def["stats"],
                checked=checker_def["default"],
            )
            card.toggled.connect(self._on_checker_card_toggled)
            self._checker_cards[checker_def["id"]] = card

            row = idx // 3
            col = idx % 3
            grid_layout.addWidget(card, row, col)

        return container

    def _create_action_bar(self) -> QHBoxLayout:
        action_bar = QHBoxLayout()
        action_bar.setSpacing(8)

        self._btn_start_check = QPushButton("\U0001F50D \u5F00\u59CB\u68C0\u67E5")
        selected_count = sum(1 for c in self._checker_cards.values() if c.is_checked)
        total_count = len(self._checker_cards)
        self._btn_start_check.setText(f"\U0001F50D \u5F00\u59CB\u68C0\u67E5 ({selected_count}/{total_count})")
        self._btn_start_check.setMinimumHeight(32)
        self._btn_start_check.setMinimumWidth(140)
        self._btn_start_check.setProperty("PrimaryBtn", True)
        action_bar.addWidget(self._btn_start_check)

        self._btn_select_all = QPushButton("\u2705 \u5168\u9009")
        self._btn_select_all.setMinimumHeight(32)
        self._btn_select_all.setProperty("SecondaryBtn", True)
        action_bar.addWidget(self._btn_select_all)

        self._btn_deselect_all = QPushButton("\u2610 \u53D6\u6D88\u5168\u9009")
        self._btn_deselect_all.setMinimumHeight(32)
        self._btn_deselect_all.setProperty("SecondaryBtn", True)
        action_bar.addWidget(self._btn_deselect_all)

        action_bar.addStretch()

        self._btn_auto_fix = QPushButton("\U0001F527 \u81EA\u52A8\u4FEE\u590D(N)")
        self._btn_auto_fix.setMinimumHeight(32)
        self._btn_auto_fix.setProperty("SecondaryBtn", True)
        action_bar.addWidget(self._btn_auto_fix)

        self._btn_export_excel = QPushButton("\U0001F4CA \u5BFC\u51FAExcel")
        self._btn_export_excel.setMinimumHeight(32)
        self._btn_export_excel.setProperty("SecondaryBtn", True)
        action_bar.addWidget(self._btn_export_excel)

        self._progress_bar = QProgressBar()
        self._progress_bar.setVisible(False)
        self._progress_bar.setMinimumHeight(20)
        self._progress_bar.setMaximumWidth(200)
        self._progress_bar.setTextVisible(True)
        self._progress_bar.setFormat("%p%")
        action_bar.addWidget(self._progress_bar)

        self._status_label = QLabel("\u51C6\u5907\u5C31\u7EEA")
        self._status_label.setProperty("treeStatus", True)
        self._status_label.setMinimumWidth(150)
        action_bar.addWidget(self._status_label)

        return action_bar

    def _create_result_panel(self) -> QGroupBox:
        result_group = QGroupBox("\U0001F4CB \u68C0\u67E5\u7ED3\u679C")
        result_group.setProperty("IndustrialGroup", True)

        result_layout = QVBoxLayout(result_group)
        result_layout.setContentsMargins(8, 18, 8, 8)
        result_layout.setSpacing(8)

        header_layout = QHBoxLayout()
        header_title = QLabel("\U0001F4CB \u68C0\u67E5\u7ED3\u679C")
        header_title.setProperty("sectionTitle", True)
        header_layout.addWidget(header_title)

        self._result_summary = QLabel("\U0001F534 0\u9519\u8BEF \U0001F7E1 5\u8B66\u544A \U0001F535 12\u63D0\u793A")
        self._result_summary.setProperty("resultSummary", True)
        header_layout.addWidget(self._result_summary)

        header_layout.addStretch()
        result_layout.addLayout(header_layout)

        self._result_tree = QTreeWidget()
        self._result_tree.setHeaderLabels([
            "\u4E25\u91CD\u5EA6",
            "\u6587\u4EF6",
            "\u884C\u53F7",
            "\u89C4\u5219ID",
            "\u63CF\u8FF0",
        ])

        column_widths = [80, 180, 60, 100, 300]
        for i, width in enumerate(column_widths):
            self._result_tree.setColumnWidth(i, width)

        self._result_tree.setAlternatingRowColors(True)
        self._result_tree.setSelectionBehavior(
            QTreeWidget.SelectRows
        )
        self._result_tree.setSortingEnabled(True)
        self._result_tree.sortByColumn(0, Qt.DescendingOrder)
        self._result_tree.setContextMenuPolicy(Qt.CustomContextMenu)

        result_layout.addWidget(self._result_tree)

        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(8)

        search_icon = QLabel("\u641C\u7D22:")
        filter_layout.addWidget(search_icon)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText(
            "\u641C\u7D22\u95EE\u9898\u63CF\u8FF0..."
        )
        self._search_input.setMinimumWidth(180)
        filter_layout.addWidget(self._search_input)

        filter_layout.addStretch()

        severity_label = QLabel("\u4E25\u91CD\u7EA7\u522B:")
        severity_label.setProperty("sectionTitle", True)
        filter_layout.addWidget(severity_label)

        self._severity_filter = QComboBox()
        self._severity_filter.addItems([
            "\u5168\u90E8",
            "\u9519\u8BEF",
            "\u8B66\u544A",
            "\u63D0\u793A",
        ])
        self._severity_filter.setMinimumWidth(80)
        filter_layout.addWidget(self._severity_filter)

        result_layout.addLayout(filter_layout)

        self._result_count_label = QLabel(
            "\u5171 0 \u6761\u8BB0\u5F55"
        )
        self._result_count_label.setProperty("treeStatus", True)
        self._result_count_label.setAlignment(
            Qt.AlignRight | Qt.AlignVCenter
        )
        result_layout.addWidget(self._result_count_label)

        detail_group = QGroupBox("\u95EE\u9898\u8BE6\u60C5")
        detail_group.setProperty("IndustrialGroup", True)

        detail_layout = QVBoxLayout(detail_group)
        detail_layout.setContentsMargins(8, 18, 8, 8)

        self._detail_browser = QTextBrowser()
        self._detail_browser.setOpenExternalLinks(False)
        self._detail_browser.setMinimumHeight(120)
        detail_layout.addWidget(self._detail_browser)

        result_layout.addWidget(detail_group)

        return result_group

    def _connect_signals(self):
        self._btn_start_check.clicked.connect(self._on_start_check)
        self._btn_select_all.clicked.connect(self.select_all)
        self._btn_deselect_all.clicked.connect(self.deselect_all)
        self._btn_auto_fix.clicked.connect(self.on_auto_fix_clicked)
        self._btn_export_excel.clicked.connect(self.on_excel_export_clicked)

        self._search_input.textChanged.connect(self.apply_filter)
        self._severity_filter.currentIndexChanged.connect(self.apply_filter)

        self._result_tree.itemClicked.connect(
            self._on_item_selected
        )
        self._result_tree.itemDoubleClicked.connect(
            self._on_item_double_clicked
        )
        self._result_tree.customContextMenuRequested.connect(
            self._show_context_menu
        )

    def _on_checker_card_toggled(self, checker_id: str, checked: bool):
        selected_count = sum(1 for c in self._checker_cards.values() if c.is_checked)
        total_count = len(self._checker_cards)
        self._btn_start_check.setText(f"\U0001F50D \u5F00\u59CB\u68C0\u67E5 ({selected_count}/{total_count})")
        self.checker_toggled.emit(checker_id, checked)

    def get_selected_checkers(self) -> List[str]:
        return [cid for cid, card in self._checker_cards.items() if card.is_checked]

    def select_all(self):
        for card in self._checker_cards.values():
            card.set_checked(True)
        selected_count = len(self._checker_cards)
        total_count = len(self._checker_cards)
        self._btn_start_check.setText(f"\U0001F50D \u5F00\u59CB\u68C0\u67E5 ({selected_count}/{total_count})")
        logger.info("全选所有检查器")

    def deselect_all(self):
        for card in self._checker_cards.values():
            card.set_checked(False)
        selected_count = 0
        total_count = len(self._checker_cards)
        self._btn_start_check.setText(f"\U0001F50D \u5F00\u59CB\u68C0\u67E5 ({selected_count}/{total_count})")
        logger.info("取消全选所有检查器")

    def start_check(
        self,
        project_path: str,
        file_path: Optional[str] = None,
    ):
        self._current_project_path = project_path

        if self._check_worker and self._check_worker.isRunning():
            self._on_stop_check()
            self._check_worker.finished.connect(
                lambda: self.start_check(project_path, file_path)
            )
            return

        selected_checkers = self.get_selected_checkers()
        if not selected_checkers:
            self._status_label.setText("⚠ 请至少选择一个检查器")
            logger.warning("未选择任何检查器，无法启动检查")
            return

        self._clear_results()
        self._set_checking_ui_state(True)
        self.check_started.emit()

        self._check_worker = CheckWorker(
            project_path=project_path,
            file_path=file_path,
            category_filter="",
            selected_checkers=selected_checkers,
        )

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

        self._check_worker.start()

        logger.info(
            f"检查任务已启动 - "
            f"路径: {project_path}, "
            f"选中检查器: {selected_checkers}"
        )

    def on_check_finished(self, report: CheckReport):
        self._current_report = report

        self._all_violations = []
        for result in report.results:
            self._all_violations.extend(result.violations)

        self.apply_filter()
        self._update_statistics(report)
        self._update_result_category_filter()
        self._set_checking_ui_state(False)

        errors = report.total_errors
        warnings = report.total_warnings
        infos = report.total_infos
        self._result_summary.setText(
            f"\U0001F534 {errors}\u9519\u8BEF "
            f"\U0001F7E1 {warnings}\u8B66\u544A "
            f"\U0001F535 {infos}\u63D0\u793A"
        )

        self._status_label.setText(
            f"\u68C0\u67E5\u5B8C\u6210 - "
            f"\u5171{report.total_violations}\u4E2A\u95EE\u9898"
        )

        self.check_finished.emit(report)

        logger.info(
            f"检查完成回调处理完毕 - "
            f"总计: {len(self._all_violations)} 条记录"
        )

    def apply_filter(self):
        if not self._all_violations:
            self._filtered_violations = []
            self._refresh_result_tree()
            return

        search_text = self._search_input.text().strip().lower()
        severity_index = self._severity_filter.currentIndex()

        severity_map = {
            0: None,
            1: Severity.ERROR,
            2: Severity.WARNING,
            3: Severity.INFO,
        }
        target_severity = severity_map.get(severity_index)

        filtered = []

        for violation in self._all_violations:
            if target_severity is not None:
                if violation.severity != target_severity:
                    continue

            if search_text:
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
        self._result_tree.setUpdatesEnabled(False)

        current_item = self._result_tree.currentItem()
        selected_data = None
        if current_item:
            selected_data = current_item.data(0, Qt.UserRole)

        self._result_tree.clear()

        for violation in self._filtered_violations:
            item = self._create_tree_item(violation)
            self._result_tree.addTopLevelItem(item)

            if selected_data and selected_data == id(violation):
                self._result_tree.setCurrentItem(item)

        count = len(self._filtered_violations)
        total = len(self._all_violations)
        self._result_count_label.setText(
            f"\u663E\u793A {count} / {total} \u6761\u8BB0\u5F55"
        )

        self._result_tree.setUpdatesEnabled(True)

    def _create_tree_item(self, violation: Violation) -> QTreeWidgetItem:
        item = QTreeWidgetItem()

        severity_icon = self.SEVERITY_ICONS.get(
            violation.severity, "?"
        )
        severity_name = self.SEVERITY_NAMES.get(
            violation.severity, "\u672A\u77E5"
        )
        item.setText(0, f"{severity_icon} {severity_name}")

        file_name = Path(violation.file_path).name if violation.file_path else "-"
        file_label = QLabel(f'<a href="{violation.file_path}" style="color:#1565C0;text-decoration:none;">{file_name}</a>')
        file_label.setCursor(Qt.PointingHandCursor)
        self._result_tree.setItemWidget(item, 1, file_label)

        line_str = str(violation.line_number) if violation.line_number > 0 else "-"
        item.setText(2, line_str)

        item.setText(3, violation.rule_id)

        description = violation.message
        if len(description) > 50:
            description = description[:47] + "..."
        item.setText(4, description)
        item.setToolTip(4, violation.message)

        bg_color = self.SEVERITY_COLORS.get(
            violation.severity, "#FFFFFF"
        )
        fg_color = self.SEVERITY_FOREGROUND.get(
            violation.severity, "#424242"
        )
        for col in range(5):
            if col != 1:
                item.setBackground(col, QColor(bg_color))
                item.setForeground(col, QColor(fg_color))

        item.setData(0, Qt.UserRole, id(violation))
        item.setData(0, Qt.UserRole + 1, violation)

        return item

    def _update_statistics(self, report: CheckReport):
        pass

    def _update_result_category_filter(self):
        pass

    def _on_progress_updated(self, progress: int, message: str):
        self._progress_bar.setValue(progress)
        self._status_label.setText(message)

    def _on_file_checked(self, file_path: str, violation_count: int):
        file_name = Path(file_path).name
        logger.debug(
            f"文件检查完成: {file_name} - {violation_count} 个问题"
        )

    def _on_item_selected(self, item: QTreeWidgetItem, column: int):
        violation = item.data(0, Qt.UserRole + 1)
        if isinstance(violation, Violation):
            self._show_violation_detail(violation)

    def _on_item_double_clicked(
        self, item: QTreeWidgetItem, column: int
    ):
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
        item = self._result_tree.itemAt(position)
        if not item:
            return

        menu = QMenu(self)

        jump_action = menu.addAction(
            "\u8DF3\u8F6C\u5230\u6E90\u7801\u4F4D\u7F6E"
        )
        jump_action.triggered.connect(
            lambda: self._on_item_double_clicked(item, 0)
        )

        copy_action = menu.addAction(
            "\U0001F4CB \u590D\u5236\u95EE\u9898\u63CF\u8FF0"
        )
        copy_action.triggered.connect(lambda: self._copy_issue_description(item))

        menu.addSeparator()

        locate_action = menu.addAction(
            "\U0001F50D \u5B9A\u4F4D\u6B64\u6587\u4EF6\u7684\u5168\u90E8\u95EE\u9898"
        )
        locate_action.triggered.connect(
            lambda: self._locate_file_issues(item)
        )

        menu.exec_(self._result_tree.mapToGlobal(position))

    def _copy_issue_description(self, item: QTreeWidgetItem):
        violation = item.data(0, Qt.UserRole + 1)
        if isinstance(violation, Violation):
            clipboard = QApplication.clipboard()
            text = f"[{violation.rule_id}] {violation.message}"
            clipboard.setText(text)
            logger.info("已复制问题描述到剪贴板")

    def _locate_file_issues(self, item: QTreeWidgetItem):
        violation = item.data(0, Qt.UserRole + 1)
        if isinstance(violation, Violation) and violation.file_path:
            file_name = Path(violation.file_path).name
            self._search_input.setText(file_name)
            logger.info(f"定位文件: {file_name}")

    def _show_violation_detail(self, violation: Violation):
        severity_name = self.SEVERITY_NAMES.get(
            violation.severity, "\u672A\u77E5"
        )
        severity_icon = self.SEVERITY_ICONS.get(
            violation.severity, "?"
        )

        html_content = f"""
        <div style="font-family: 'Microsoft YaHei UI', sans-serif;">
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

        if violation.code_snippet:
            escaped_snippet = violation.code_snippet.replace(
                "<", "&lt;"
            ).replace(">", "&gt;")
            html_content += f"""
            <div style="margin-top: 12px;">
                <b>\u4EE3\u7801\u7247\u6BB5:</b>
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

        if violation.suggestion:
            html_content += f"""
            <div style="margin-top: 12px;">
                <b>\u4FEE\u590D\u5EFA\u8BAE:</b>
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
        self._btn_start_check.setEnabled(not is_checking)
        self._btn_select_all.setEnabled(not is_checking)
        self._btn_deselect_all.setEnabled(not is_checking)
        self._progress_bar.setVisible(is_checking)

        if is_checking:
            self._status_label.setText("\u6B63\u5728\u68C0\u67E5...")
            self._progress_bar.setValue(0)

    def _clear_results(self):
        self._current_report = None
        self._all_violations = []
        self._filtered_violations = []
        self._result_tree.clear()
        self._detail_browser.clear()
        self._search_input.clear()
        self._severity_filter.setCurrentIndex(0)

        self._result_count_label.setText("\u5171 0 \u6761\u8BB0\u5F55")
        self._result_summary.setText(
            "\U0001F534 0\u9519\u8BEF "
            "\U0001F7E1 0\u8B66\u544A "
            "\U0001F535 0\u63D0\u793A"
        )

    def _on_start_check(self):
        if self._current_project_path:
            self.start_check(self._current_project_path)
        else:
            from src.core.settings import SettingsManager
            recent = SettingsManager.get_recent_projects()
            if recent:
                self.start_check(recent[0].get("path", ""))
            else:
                self._status_label.setText("⚠ 请先打开一个项目再执行检查")
                logger.warning("未设置项目路径，无法启动检查")

    def _on_stop_check(self):
        if self._check_worker and self._check_worker.isRunning():
            self._check_worker.cancel()
            logger.info("用户请求停止检查")

    def _on_check_error(self, error_message: str):
        self._set_checking_ui_state(False)
        self._status_label.setText(f"\u274C \u68C0\u67E5\u51FA\u9519: {error_message}")
        logger.error(f"检查出错: {error_message}")

    def on_auto_fix_clicked(self):
        logger.info("自动修复按钮点击事件触发")

    def on_excel_export_clicked(self):
        logger.info("导出Excel按钮点击事件触发")

    def get_current_report(self) -> Optional[CheckReport]:
        return self._current_report

    def clear_all(self):
        self._clear_results()
        self._status_label.setText("\u51C6\u5907\u5C07\u7EEA")

    def cleanup(self):
        if self._check_worker and self._check_worker.isRunning():
            self._check_worker.cancel()
            self._check_worker.finished.disconnect()
            self._check_worker.wait(2000)
            self._check_worker = None
