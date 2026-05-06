# -*- coding: utf-8 -*-
"""
测试运行器面板组件

提供PLC测试的完整UI界面，包括：
- 测试用例树形展示（按文件分组）
- 测试执行控制（运行/停止/刷新）
- 实时日志监控和结果汇总
- 用例详情查看和源码跳转
- 执行配置管理

架构设计：
- 采用MVP模式，Panel作为View层
- 通过信号槽与Service层交互
- 使用QThread实现异步执行
- 支持实时状态更新和进度显示

依赖项：
- PyQt5: UI框架
- TestManagementService: 测试执行服务
- SCLTestParser: 测试文件解析器
- 数据模型: TestSuite/TestCase/TestResult/TestRunSummary

作者：双栖资深开发
版本：1.0.0
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QTabWidget,
    QTextEdit,
    QLabel,
    QPushButton,
    QComboBox,
    QSpinBox,
    QCheckBox,
    QLineEdit,
    QGroupBox,
    QListWidget,
    QListWidgetItem,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QSplitter,
    QProgressBar,
    QFileDialog,
    QMessageBox,
    QMenu,
    QApplication,
    QFrame,
)
from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    QThread,
    QTimer,
    QSize,
)
from PyQt5.QtGui import (
    QIcon,
    QFont,
    QColor,
    QTextCursor,
    QPalette,
)

from src.utils.logger import setup_logger
from src.services.test_management_service import (
    TestManagementService,
    TestExecutionConfig,
)
from src.models.test_case import TestCase, TestSuite, StepType
from src.models.test_result import (
    TestResult,
    TestRunSummary,
    TestStatus,
    AssertionResult,
)

logger = setup_logger(__name__)


# ============================================================================
# 常量定义
# ============================================================================

# 状态图标映射（使用Unicode字符）
STATUS_ICONS = {
    'pending': '\u23F3',      # ⏳ 等待
    'running': '\u25B6',      # ▶️ 运行中
    'passed': '\u2705',       # ✅ 通过
    'failed': '\u274C',       # ❌ 失败
    'error': '\u26A0\uFE0F',   # ⚠️ 错误
    'skipped': '\u23ED',      # ⏭️ 跳过
}

# 步骤类型图标
STEP_ICONS = {
    StepType.SET: '\uD83D\uDD27',        # 🔧 SET
    StepType.WAIT_CYCLES: '\u23F1\uFE0F', # ⏱️ WAIT
    StepType.ASSERT: '\u2713',           # ✓ ASSERT
}

# 日志颜色映射
LOG_COLORS = {
    'INFO': '#000000',
    'WARNING': '#FFA500',
    'ERROR': '#FF0000',
    'DEBUG': '#808080',
}

# 运行模式
RUN_MODES = {
    'all': '全部运行',
    'selected': '仅运行选中',
    'failed_retry': '重试失败项',
}

# 数据角色（用于存储自定义数据到QTreeWidgetItem）
ROLE_TEST_CASE = Qt.UserRole + 1
ROLE_TEST_RESULT = Qt.UserRole + 2
ROLE_FILE_PATH = Qt.UserRole + 3
ROLE_SUITE = Qt.UserRole + 4


# ============================================================================
# 工作线程类（异步执行测试）
# ============================================================================

class TestExecutionWorker(QThread):
    """
    测试执行工作线程

    在后台线程中执行测试任务，避免阻塞UI主线程。
    通过信号向主线程报告进度和结果。
    """

    # 信号定义
    test_started = pyqtSignal(str)                    # 单个测试开始 (case_name)
    test_finished = pyqtSignal(object)                # 单个测试完成 (TestResult)
    all_finished = pyqtSignal(object)                 # 全部完成 (TestRunSummary)
    output_received = pyqtSignal(str)                 # 接收到输出文本
    error_occurred = pyqtSignal(str)                  # 发生错误

    def __init__(
        self,
        service: TestManagementService,
        suite: TestSuite,
        test_names: Optional[List[str]] = None,
        parent=None
    ):
        """
        初始化工作线程

        Args:
            service: 测试管理服务实例
            suite: 要执行的测试套件
            test_names: 指定要执行的测试名称列表（None=全部）
            parent: 父对象
        """
        super().__init__(parent)
        self._service = service
        self._suite = suite
        self._test_names = test_names
        self._is_cancelled = False

    def run(self):
        """线程主函数 - 执行测试"""
        try:
            # 设置回调函数
            self._service.set_progress_callback(self._on_progress)
            self._service.set_complete_callback(self._on_complete)
            self._service.set_output_callback(self._on_output)

            # 执行测试（同步调用，但在本线程中）
            summary = self._service.run_tests(
                self._suite,
                self._test_names
            )

            # 如果被取消，发出完成信号
            if not self._is_cancelled:
                self.all_finished.emit(summary)

        except Exception as e:
            logger.error(f"测试执行异常: {e}")
            self.error_occurred.emit(str(e))

    def cancel(self):
        """请求取消执行"""
        self._is_cancelled = True
        self._service.cancel_running_tests()

    def _on_progress(self, progress_data: Dict[str, Any]):
        """进度回调处理"""
        current = progress_data.get('current', 0)
        total = progress_data.get('total', 0)
        test_name = progress_data.get('current_test', '')

        if current > 0 and test_name:
            self.test_started.emit(test_name)

    def _on_complete(self, summary: TestRunSummary):
        """完成回调处理"""
        for result in summary.test_results:
            self.test_finished.emit(result)

        if not self._is_cancelled:
            self.all_finished.emit(summary)

    def _on_output(self, output: str):
        """输出回调处理"""
        if output:
            self.output_received.emit(output)


# ============================================================================
# 主面板类
# ============================================================================

class TestRunnerPanel(QWidget):
    """
    测试运行器面板

    提供完整的PLC测试执行界面，包括测试用例管理、
    执行控制、日志监控和结果展示。

    主要功能区域：
    1. 顶部控制栏：运行/停止按钮、模式选择、状态显示
    2. 左侧测试树：按文件分组的用例列表
    3. 右侧Tab面板：详情/日志/结果/设置
    4. 底部状态栏：进度、计时器、当前用例

    使用示例：
        >>> panel = TestRunnerPanel()
        >>> panel.set_project_path(Path("/path/to/project"))
        >>> panel.show()
    """

    # ===== 信号定义 =====
    tests_started = pyqtSignal()                      # 测试开始执行
    test_case_started = pyqtSignal(str)                # 单个用例开始 (case_name)
    test_case_finished = pyqtSignal(object)            # 单个用例完成 (TestResult)
    all_tests_finished = pyqtSignal(object)            # 全部完成 (TestRunSummary)
    source_jump_requested = pyqtSignal(str, int)       # 跳转源码请求 (file_path, line)

    def __init__(self, parent=None):
        """
        初始化测试运行器面板

        Args:
            parent: 父窗口部件
        """
        super().__init__(parent)

        # 核心数据
        self._project_path: Optional[Path] = None
        self._service: Optional[TestManagementService] = None
        self._suites: List[TestSuite] = []
        self._worker: Optional[TestExecutionWorker] = None
        self._is_running = False
        self._results: List[TestResult] = []
        self._summary: Optional[TestRunSummary] = None
        self._start_time: Optional[datetime] = None
        self._timer: Optional[QTimer] = None

        # 配置参数
        self._config = TestExecutionConfig()

        # 初始化UI
        self._init_ui()

        logger.info("TestRunnerPanel初始化完成")

    # ========================================================================
    # UI初始化方法
    # ========================================================================

    def _init_ui(self):
        """初始化用户界面布局"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(6)

        # 1. 顶部控制栏
        self._init_toolbar(main_layout)

        # 2. 中间工作区（左右分割）
        splitter = QSplitter(Qt.Horizontal)
        self._init_test_tree(splitter)
        self._init_right_panel(splitter)
        splitter.setSizes([400, 600])  # 左40% 右60%
        main_layout.addWidget(splitter, stretch=1)

        # 3. 底部状态栏
        self._init_status_bar(main_layout)

    def _init_toolbar(self, parent_layout: QVBoxLayout):
        """
        初始化顶部工具栏

        Args:
            parent_layout: 父布局
        """
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        # 运行测试按钮（绿色主操作）
        self._btn_run = QPushButton('\u25B6 运行测试')
        self._btn_run.setToolTip('运行选中的测试用例')
        self._btn_run.setStyleSheet(
            'QPushButton {'
            '  background-color: #4CAF50;'
            '  color: white;'
            '  border: none;'
            '  padding: 6px 16px;'
            '  border-radius: 4px;'
            '  font-weight: bold;'
            '}'
            'QPushButton:hover {'
            '  background-color: #45a049;'
            '}'
            'QPushButton:disabled {'
            '  background-color: #cccccc;'
            '}'
        )
        self._btn_run.clicked.connect(self.run_tests)
        toolbar.addWidget(self._btn_run)

        # 停止按钮（灰色，默认禁用）
        self._btn_stop = QPushButton('\u25FC 停止')
        self._btn_stop.setToolTip('停止正在运行的测试')
        self._btn_stop.setEnabled(False)
        self._btn_stop.setStyleSheet(
            'QPushButton {'
            '  background-color: #757575;'
            '  color: white;'
            '  border: none;'
            '  padding: 6px 16px;'
            '  border-radius: 4px;'
            '}'
            'QPushButton:hover {'
            '  background-color: #616161;'
            '}'
        )
        self._btn_stop.clicked.connect(self.stop_tests)
        toolbar.addWidget(self._btn_stop)

        # 刷新按钮
        self._btn_refresh = QPushButton('\uD83D\uDD04 刷新')
        self._btn_refresh.setToolTip('扫描并刷新测试用例列表')
        self._btn_refresh.clicked.connect(self.refresh_test_tree)
        toolbar.addWidget(self._btn_refresh)

        # 分隔符
        toolbar.addSpacing(16)

        # 运行模式选择
        mode_label = QLabel('运行模式:')
        toolbar.addWidget(mode_label)

        self._combo_mode = QComboBox()
        self._combo_mode.addItems(list(RUN_MODES.values()))
        self._combo_mode.setCurrentIndex(1)  # 默认"仅运行选中"
        self._combo_mode.setMinimumWidth(120)
        toolbar.addWidget(self._combo_mode)

        # 弹性空间
        toolbar.addStretch()

        # 状态标签
        self._lbl_status = QLabel('\U0001F7E2 就绪')
        self._lbl_status.setStyleSheet(
            'font-size: 11pt; '
            'padding: 4px 12px; '
            'background-color: #f0f0f0; '
            'border-radius: 4px;'
        )
        toolbar.addWidget(self._lbl_status)

        parent_layout.addLayout(toolbar)

    def _init_test_tree(self, parent_splitter: QSplitter):
        """
        初始化左侧测试用例树

        Args:
            parent_splitter: 父分割器
        """
        # 树控件容器
        tree_container = QWidget()
        tree_layout = QVBoxLayout(tree_container)
        tree_layout.setContentsMargins(0, 0, 0, 0)
        tree_layout.setSpacing(4)

        # 树标题栏
        tree_header = QHBoxLayout()
        tree_title = QLabel('\uD83D\uDCC1 测试用例')
        tree_title.setStyleSheet('font-weight: bold; font-size: 10pt;')
        tree_header.addWidget(tree_title)
        tree_header.addStretch()

        # 选择操作按钮
        btn_select_all = QPushButton('全选')
        btn_select_all.setMaximumWidth(50)
        btn_select_all.clicked.connect(self._select_all_cases)
        tree_header.addWidget(btn_select_all)

        btn_deselect_all = QPushButton('反选')
        btn_deselect_all.setMaximumWidth(50)
        btn_deselect_all.clicked.connect(self._deselect_all_cases)
        tree_header.addWidget(btn_deselect_all)

        btn_select_failed = QPushButton('失败项')
        btn_select_failed.setMaximumWidth(55)
        btn_select_failed.clicked.connect(self._select_failed_cases)
        tree_header.addWidget(btn_select_failed)

        tree_layout.addLayout(tree_header)

        # 树控件
        self._tree_tests = QTreeWidget()
        self._tree_tests.setHeaderLabels(['测试用例', '描述'])
        self._tree_tests.setColumnWidth(0, 200)
        self._tree_tests.setColumnWidth(1, 180)
        self._tree_tests.setAlternatingRowColors(True)
        self._tree_tests.setSortingEnabled(False)
        self._tree_tests.itemChanged.connect(self._on_tree_item_changed)
        self._tree_tests.itemSelectionChanged.connect(
            self._on_tree_selection_changed
        )
        self._tree_tests.setContextMenuPolicy(Qt.CustomContextMenu)
        self._tree_tests.customContextMenuRequested.connect(
            self._show_tree_context_menu
        )

        tree_layout.addWidget(self._tree_tests)

        parent_splitter.addWidget(tree_container)

    def _init_right_panel(self, parent_splitter: QSplitter):
        """
        初始化右侧Tab面板

        Args:
            parent_splitter: 父分割器
        """
        self._tab_widget = QTabWidget()

        # Tab 1: 用例详情
        self._init_detail_tab()

        # Tab 2: 执行日志
        self._init_log_tab()

        # Tab 3: 结果汇总
        self._init_result_tab()

        # Tab 4: 设置
        self._init_settings_tab()

        parent_splitter.addWidget(self._tab_widget)

    def _init_detail_tab(self):
        """初始化用例详情Tab"""
        detail_widget = QWidget()
        layout = QVBoxLayout(detail_widget)
        layout.setContentsMargins(8, 8, 8, 8)

        # 信息卡片组
        info_group = QGroupBox('用例信息')
        info_layout = QVBoxLayout(info_group)

        # 用例名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel('用例名称:'))
        self._lbl_case_name = QLabel('-')
        self._lbl_case_name.setStyleSheet('font-weight: bold; font-size: 11pt;')
        name_layout.addWidget(self._lbl_case_name)
        name_layout.addStretch()
        info_layout.addLayout(name_layout)

        # 文件路径
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel('文件路径:'))
        self._lbl_file_path = QLabel('-')
        self._lbl_file_path.setWordWrap(True)
        self._lbl_file_path.setTextInteractionFlags(
            Qt.TextSelectableByMouse
        )
        file_layout.addWidget(self._lbl_file_path)
        info_layout.addLayout(file_layout)

        # 测试目标
        target_label = QLabel('测试目标:')
        info_layout.addWidget(target_label)
        self._txt_target = QTextEdit()
        self._txt_target.setMaximumHeight(80)
        self._txt_target.setReadOnly(True)
        self._txt_target.setPlaceholderText('选择一个测试用例查看详情...')
        info_layout.addWidget(self._txt_target)

        layout.addWidget(info_group)

        # 测试步骤列表
        steps_group = QGroupBox('测试步骤')
        steps_layout = QVBoxLayout(steps_group)

        self._list_steps = QListWidget()
        self._list_steps.setAlternatingRowColors(True)
        steps_layout.addWidget(self._list_steps)

        layout.addWidget(steps_group, stretch=1)

        self._tab_widget.addTab(detail_widget, '\uD83D\uDCDD 用例详情')

    def _init_log_tab(self):
        """初始化执行日志Tab"""
        log_widget = QWidget()
        layout = QVBoxLayout(log_widget)
        layout.setContentsMargins(8, 8, 8, 8)

        # 日志文本框
        self._txt_log = QTextEdit()
        self._txt_log.setReadOnly(True)
        self._txt_log.setFont(QFont('Consolas', 9))
        self._txt_log.setPlaceholderText(
            '测试执行日志将在此处显示...'
        )
        layout.addWidget(self._txt_log, stretch=1)

        # 操作按钮栏
        log_toolbar = QHBoxLayout()

        self._btn_clear_log = QPushButton('\uD83D\uDDD1 清空日志')
        self._btn_clear_log.clicked.connect(self._clear_log)
        log_toolbar.addWidget(self._btn_clear_log)

        self._btn_save_log = QPushButton('\uD83D\uDCBE 保存日志')
        self._btn_save_log.clicked.connect(self._save_log)
        log_toolbar.addWidget(self._btn_save_log)

        log_toolbar.addStretch()
        layout.addLayout(log_toolbar)

        self._tab_widget.addTab(log_widget, '\uD83D\uDCFA 执行日志')

    def _init_result_tab(self):
        """初始化结果汇总Tab"""
        result_widget = QWidget()
        layout = QVBoxLayout(result_widget)
        layout.setContentsMargins(8, 8, 8, 8)

        # 总览统计卡片
        summary_group = QGroupBox('执行总览')
        summary_layout = QVBoxLayout(summary_group)

        # 统计标签
        stats_layout = QHBoxLayout()

        self._lbl_total = QLabel('总计: 0')
        stats_layout.addWidget(self._lbl_total)

        self._lbl_passed = QLabel('通过: 0')
        self._lbl_passed.setStyleSheet('color: #4CAF50; font-weight: bold;')
        stats_layout.addWidget(self._lbl_passed)

        self._lbl_failed = QLabel('失败: 0')
        self._lbl_failed.setStyleSheet('color: #F44336; font-weight: bold;')
        stats_layout.addWidget(self._lbl_failed)

        self._lbl_rate = QLabel('通过率: 0%')
        stats_layout.addWidget(self._lbl_rate)

        self._lbl_duration = QLabel('耗时: 0.0s')
        stats_layout.addWidget(self._lbl_duration)

        stats_layout.addStretch()
        summary_layout.addLayout(stats_layout)

        # 进度条
        self._progress_bar = QProgressBar()
        self._progress_bar.setVisible(False)
        summary_layout.addWidget(self._progress_bar)

        layout.addWidget(summary_group)

        # 结果表格
        table_group = QGroupBox('详细结果')
        table_layout = QVBoxLayout(table_group)

        self._table_results = QTableWidget()
        self._table_results.setColumnCount(4)
        self._table_results.setHorizontalHeaderLabels([
            '用例名', '状态', '耗时(s)', '断言数'
        ])
        self._table_results.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.Stretch
        )
        self._table_results.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeToContents
        )
        self._table_results.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeToContents
        )
        self._table_results.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeToContents
        )
        self._table_results.setAlternatingRowColors(True)
        self._table_results.setSelectionBehavior(
            QTableWidget.SelectRows
        )
        self._table_results.itemDoubleClicked.connect(
            self._on_result_item_double_clicked
        )
        table_layout.addWidget(self._table_results)

        layout.addWidget(table_group, stretch=1)

        self._tab_widget.addTab(result_widget, '\uD83D\uDCCA 结果汇总')

    def _init_settings_tab(self):
        """初始化设置Tab"""
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)
        layout.setContentsMargins(8, 8, 8, 8)

        # 基本设置组
        basic_group = QGroupBox('基本设置')
        basic_layout = QVBoxLayout(basic_group)

        # plccheck路径
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel('plccheck路径:'))
        self._edit_plccheck = QLineEdit()
        self._edit_plccheck.setPlaceholderText(
            'plccheck 或完整可执行文件路径'
        )
        path_layout.addWidget(self._edit_plccheck)

        btn_browse = QPushButton('浏览...')
        btn_browse.setMaximumWidth(60)
        btn_browse.clicked.connect(self._browse_plccheck_path)
        path_layout.addWidget(btn_browse)

        basic_layout.addLayout(path_layout)

        # 超时时间
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel('超时时间(秒):'))
        self._spin_timeout = QSpinBox()
        self._spin_timeout.setRange(10, 3600)
        self._spin_timeout.setValue(300)
        self._spin_timeout.setSuffix(' 秒')
        timeout_layout.addWidget(self._spin_timeout)
        timeout_layout.addStretch()
        basic_layout.addLayout(timeout_layout)

        layout.addWidget(basic_group)

        # 高级设置组
        adv_group = QGroupBox('高级选项')
        adv_layout = QVBoxLayout(adv_group)

        # 并行执行
        self._chk_parallel = QCheckBox('并行执行多个测试')
        self._chk_parallel.setToolTip(
            '启用后可同时运行多个独立测试用例'
        )
        adv_layout.addWidget(self._chk_parallel)

        # 失败重试次数
        retry_layout = QHBoxLayout()
        retry_layout.addWidget(QLabel('失败重试次数:'))
        self._spin_retry = QSpinBox()
        self._spin_retry.setRange(0, 5)
        self._spin_retry.setValue(0)
        retry_layout.addWidget(self._spin_retry)
        retry_layout.addStretch()
        adv_layout.addLayout(retry_layout)

        # 日志详细程度
        verbose_layout = QHBoxLayout()
        verbose_layout.addWidget(QLabel('日志级别:'))
        self._combo_verbose = QComboBox()
        self._combo_verbose.addItems(['简洁', '标准', '详细'])
        self._combo_verbose.setCurrentIndex(1)
        verbose_layout.addWidget(self._combo_verbose)
        verbose_layout.addStretch()
        adv_layout.addLayout(verbose_layout)

        layout.addWidget(adv_group)

        # 应用按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_apply = QPushButton('\u2713 应用设置')
        btn_apply.setStyleSheet(
            'QPushButton {'
            '  background-color: #2196F3;'
            '  color: white;'
            '  border: none;'
            '  padding: 6px 20px;'
            '  border-radius: 4px;'
            '}'
        )
        btn_apply.clicked.connect(self._apply_settings)
        btn_layout.addWidget(btn_apply)

        layout.addLayout(btn_layout)
        layout.addStretch()

        self._tab_widget.addTab(settings_widget, '\u2699\uFE0F 设置')

    def _init_status_bar(self, parent_layout: QVBoxLayout):
        """
        初始化底部状态栏

        Args:
            parent_layout: 父布局
        """
        status_frame = QFrame()
        status_frame.setFrameShape(QFrame.StyledPanel)
        status_frame.setStyleSheet(
            'QFrame {'
            '  background-color: #f5f5f5;'
            '  border-top: 1px solid #ddd;'
            '  padding: 4px;'
            '}'
        )
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(8, 4, 8, 4)

        # 当前用例
        self._lbl_current_case = QLabel('当前用例: -')
        self._lbl_current_case.setMinimumWidth(200)
        status_layout.addWidget(self._lbl_current_case)

        # 进度文字
        self._lbl_progress_text = QLabel('进度: 0/0')
        status_layout.addWidget(self._lbl_progress_text)

        # 弹性空间
        status_layout.addStretch()

        # 计时器
        self._lbl_elapsed = QLabel('已用时: 00:00.000')
        status_layout.addWidget(self._lbl_elapsed)

        parent_layout.addWidget(status_frame)

        # 创建计时器
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_timer_display)

    # ========================================================================
    # 公共API方法
    # ========================================================================

    def set_project_path(self, project_path: Path):
        """
        设置项目路径并初始化服务

        Args:
            project_path: 项目根目录路径
        """
        self._project_path = Path(project_path).resolve()

        # 初始化测试管理服务
        try:
            self._service = TestManagementService(
                self._project_path,
                config=self._config
            )
            logger.info(f"项目路径已设置: {self._project_path}")

            # 自动刷新测试树
            self.refresh_test_tree()

        except Exception as e:
            logger.error(f"初始化测试服务失败: {e}")
            QMessageBox.critical(
                self,
                '错误',
                f'无法初始化测试服务:\n{str(e)}'
            )

    def scan_test_files(self, project_path: Optional[Path] = None) -> List[Path]:
        """
        扫描项目中的.scltest文件

        Args:
            project_path: 搜索路径（None则使用当前项目路径）

        Returns:
            找到的文件路径列表
        """
        search_path = project_path or self._project_path
        if not search_path or not self._service:
            return []

        return self._service.scan_test_files(search_path)

    def refresh_test_tree(self):
        """刷新测试用例树"""
        if not self._service:
            return

        # 清空现有内容
        self._tree_tests.clear()
        self._suites.clear()

        try:
            # 扫描并解析所有测试文件
            files = self.scan_test_files()
            self._suites = self._service.parse_all_test_files(files)

            # 构建树结构
            for suite in self._suites:
                self._add_suite_to_tree(suite)

            # 更新状态
            total_cases = sum(s.test_case_count for s in self._suites)
            self._update_status_label(
                f'\U0001F7E2 已加载 {len(self._suites)} 个文件, '
                f'{total_cases} 个用例'
            )
            logger.info(
                f"测试树已刷新: {len(self._suites)} 文件, "
                f"{total_cases} 用例"
            )

        except Exception as e:
            logger.error(f"刷新测试树失败: {e}")
            self._update_status_label(
                f'\U0001F534 刷新失败: {str(e)}'
            )

    def run_tests(self, mode: Optional[str] = None):
        """
        运行测试

        Args:
            mode: 运行模式 ('all'/'selected'/'failed_retry')，
                  None则从下拉框获取当前选择
        """
        if self._is_running:
            logger.warning("测试已在运行中")
            return

        if not self._suites:
            QMessageBox.warning(
                self,
                '提示',
                '没有可用的测试用例，请先刷新列表'
            )
            return

        # 确定运行模式
        if mode is None:
            mode_index = self._combo_mode.currentIndex()
            mode = list(RUN_MODES.keys())[mode_index]

        # 收集要运行的测试用例
        test_names = self._collect_test_names(mode)

        if not test_names:
            QMessageBox.information(
                self,
                '提示',
                '请先选择要运行的测试用例'
            )
            return

        # 开始执行
        self._start_execution(test_names)

    def stop_tests(self):
        """停止正在运行的测试"""
        if not self._is_running or not self._worker:
            return

        logger.info("用户请求停止测试")
        self._worker.cancel()
        self._update_ui_for_stopping()

    def get_selected_test_case(self) -> Optional[TestCase]:
        """
        获取当前选中的测试用例

        Returns:
            选中的TestCase对象，未选中返回None
        """
        selected = self._tree_tests.selectedItems()
        if not selected:
            return None

        item = selected[0]
        case = item.data(0, ROLE_TEST_CASE)
        if isinstance(case, TestCase):
            return case
        return None

    def clear_results(self):
        """清除之前的测试结果"""
        self._results.clear()
        self._summary = None
        self._clear_result_table()
        self._reset_tree_icons()

    # ========================================================================
    # 内部实现方法 - 测试执行
    # ========================================================================

    def _start_execution(self, test_names: List[str]):
        """
        启动测试执行

        Args:
            test_names: 要运行的测试名称列表
        """
        # 合并所有suite的测试用例（简化实现：取第一个有选中用例的suite）
        target_suite = None
        for suite in self._suites:
            suite_case_names = [tc.name for tc in suite.test_cases]
            if any(name in suite_case_names for name in test_names):
                target_suite = suite
                break

        if not target_suite:
            QMessageBox.warning(self, '错误', '无法找到匹配的测试套件')
            return

        # 更新UI状态为运行中
        self._update_ui_for_running()

        # 重置结果
        self.clear_results()
        self._start_time = datetime.now()
        self._timer.start(100)  # 每100ms更新一次计时器

        # 创建并启动工作线程
        self._worker = TestExecutionWorker(
            self._service,
            target_suite,
            test_names,
            parent=self
        )

        # 连接信号
        self._worker.test_started.connect(self._on_test_started)
        self._worker.test_finished.connect(self._on_test_finished)
        self._worker.all_finished.connect(self._on_all_tests_finished)
        self._worker.output_received.connect(self._on_output_received)
        self._worker.error_occurred.connect(self._on_error_occurred)
        self._worker.finished.connect(self._on_worker_finished)

        # 发出全局信号
        self.tests_started.emit()

        # 启动线程
        logger.info(f"开始执行测试: {len(test_names)} 个用例")
        self._worker.start()

    def _collect_test_names(self, mode: str) -> List[str]:
        """
        根据模式收集要运行的测试名称

        Args:
            mode: 运行模式

        Returns:
            测试名称列表
        """
        names = []

        if mode == 'all':
            # 全部用例
            for suite in self._suites:
                for tc in suite.test_cases:
                    names.append(tc.name)

        elif mode == 'selected':
            # 仅选中的用例
            root = self._tree_tests.invisibleRootItem()
            for i in range(root.childCount()):
                file_item = root.child(i)
                for j in range(file_item.childCount()):
                    case_item = file_item.child(j)
                    if case_item.checkState(0) == Qt.Checked:
                        case = case_item.data(0, ROLE_TEST_CASE)
                        if isinstance(case, TestCase):
                            names.append(case.name)

        elif mode == 'failed_retry':
            # 仅之前失败的用例
            for result in self._results:
                if result.status in (TestStatus.FAILED, TestStatus.ERROR):
                    names.append(result.test_case_name)

        return names

    def _update_ui_for_running(self):
        """更新UI为运行状态"""
        self._is_running = True

        # 按钮状态
        self._btn_run.setEnabled(False)
        self._btn_stop.setEnabled(True)
        self._btn_refresh.setEnabled(False)

        # 状态标签
        self._update_status_label('\U0001F534 运行中...')

        # 显示进度条
        self._progress_bar.setVisible(True)
        self._progress_bar.setRange(0, 0)  # 不确定进度模式

        # 切换到日志Tab
        self._tab_widget.setCurrentIndex(1)  # 日志Tab

    def _update_ui_for_stopping(self):
        """更新UI为停止中状态"""
        self._update_status_label('\u26A0\uFE0F 正在停止...')

    def _update_ui_for_completed(self):
        """更新UI为完成状态"""
        self._is_running = False

        # 按钮状态
        self._btn_run.setEnabled(True)
        self._btn_stop.setEnabled(False)
        self._btn_refresh.setEnabled(True)

        # 隐藏进度条
        self._progress_bar.setVisible(False)

        # 停止计时器
        if self._timer and self._timer.isActive():
            self._timer.stop()

    # ========================================================================
    # 回调处理方法
    # ========================================================================

    def _on_test_started(self, case_name: str):
        """
        单个测试开始的回调

        Args:
            case_name: 测试用例名称
        """
        logger.debug(f"测试开始: {case_name}")

        # 更新状态栏
        self._lbl_current_case.setText(f'当前用例: {case_name}')

        # 更新树的节点图标
        self._set_tree_item_status(case_name, 'running')

        # 发出信号
        self.test_case_started.emit(case_name)

        # 追加日志
        self.append_log(f'开始执行: {case_name}', 'INFO')

    def _on_test_finished(self, result: TestResult):
        """
        单个测试完成的回调

        Args:
            result: 测试结果对象
        """
        logger.info(f"测试完成: {result}")

        # 保存结果
        self._results.append(result)

        # 更新树的节点图标和状态
        status_key = result.status.name.lower()
        self._set_tree_item_status(result.test_case_name, status_key, result)

        # 更新进度
        completed = len(self._results)
        total = len(self._collect_test_names('selected')) or len(self._results)
        self._lbl_progress_text.setText(f'进度: {completed}/{total}')

        # 发出信号
        self.test_case_finished.emit(result)

        # 追加日志
        status_icon = STATUS_ICONS.get(status_key, '?')
        self.append_log(
            f'{status_icon} {result.test_case_name} - '
            f'{result.status.name} ({result.duration_seconds:.3f}s)',
            'PASSED' if result.is_passed else 'ERROR' if result.has_error else 'WARNING'
        )

    def _on_all_tests_finished(self, summary: TestRunSummary):
        """
        所有测试完成的回调

        Args:
            summary: 运行摘要对象
        """
        logger.info(f"所有测试完成: {summary}")
        self._summary = summary

        # 更新结果汇总Tab
        self._update_result_summary(summary)

        # 更新UI状态
        self._update_ui_for_completed()

        # 更新状态标签
        if summary.all_passed:
            self._update_status_label(
                f'\u2705 全部通过 ({summary.total_tests} 个用例)'
            )
        else:
            self._update_status_label(
                f'\u274C 完成 ({summary.passed_tests}/{summary.total_tests} 通过)'
            )

        # 切换到结果Tab
        self._tab_widget.setCurrentIndex(2)  # 结果Tab

        # 发出信号
        self.all_tests_finished.emit(summary)

        # 最终日志
        self.append_log('=' * 60, 'INFO')
        self.append_log(
            f'执行完成: {summary.passed_tests}/{summary.total_tests} 通过, '
            f'耗时 {summary.total_duration_seconds:.3f}s',
            'INFO'
        )
        self.append_log('=' * 60, 'INFO')

    def _on_output_received(self, output: str):
        """
        接收到输出的回调

        Args:
            output: 输出文本
        """
        # 将输出按行追加到日志
        for line in output.strip().splitlines():
            if line.strip():
                self.append_log(line, 'INFO')

    def _on_error_occurred(self, error_msg: str):
        """
        发生错误的回调

        Args:
            error_msg: 错误信息
        """
        logger.error(f"测试执行错误: {error_msg}")
        self.append_log(f'ERROR: {error_msg}', 'ERROR')

        # 更新UI
        self._update_ui_for_completed()
        self._update_status_label(f'\u274C 错误: {error_msg}')

    def _on_worker_finished(self):
        """工作线程结束的清理"""
        logger.debug("工作线程已结束")
        self._worker = None

    # ========================================================================
    # 内部实现方法 - 测试树操作
    # ========================================================================

    def _add_suite_to_tree(self, suite: TestSuite):
        """
        将测试套件添加到树中

        Args:
            suite: 测试套件对象
        """
        # 创建文件节点
        file_item = QTreeWidgetItem(self._tree_tests)
        file_item.setText(0, f'\uD83D\uDCC1 {suite.file_path.name}')
        file_item.setData(0, ROLE_FILE_PATH, suite.file_path)
        file_item.setData(0, ROLE_SUITE, suite)
        file_item.setExpanded(True)
        file_item.setCheckState(0, Qt.Checked)
        file_item.setForeground(0, QColor('#1976D2'))

        # 添加子节点（测试用例）
        for tc in suite.test_cases:
            case_item = QTreeWidgetItem(file_item)
            case_item.setText(0, f'{STATUS_ICONS["pending"]} {tc.name}')
            case_item.setText(1, tc.description[:30] if tc.description else '')
            case_item.setData(0, ROLE_TEST_CASE, tc)
            case_item.setCheckState(0, Qt.Checked)

    def _set_tree_item_status(
        self,
        case_name: str,
        status: str,
        result: Optional[TestResult] = None
    ):
        """
        设置树节点的状态图标

        Args:
            case_name: 测试用例名称
            status: 状态键 ('pending'/'running'/'passed'/'failed'等)
            result: 测试结果对象（可选）
        """
        icon = STATUS_ICONS.get(status, STATUS_ICONS['pending'])

        root = self._tree_tests.invisibleRootItem()
        for i in range(root.childCount()):
            file_item = root.child(i)
            for j in range(file_item.childCount()):
                case_item = file_item.child(j)
                case = case_item.data(0, ROLE_TEST_CASE)
                if isinstance(case, TestCase) and case.name == case_name:
                    # 更新图标
                    case_item.setText(0, f'{icon} {case_name}')

                    # 存储结果数据
                    if result:
                        case_item.setData(0, ROLE_TEST_RESULT, result)
                    return

    def _reset_tree_icons(self):
        """重置所有树节点图标为等待状态"""
        root = self._tree_tests.invisibleRootItem()
        for i in range(root.childCount()):
            file_item = root.child(i)
            for j in range(file_item.childCount()):
                case_item = file_item.child(j)
                case = case_item.data(0, ROLE_TEST_CASE)
                if isinstance(case, TestCase):
                    case_item.setText(
                        0,
                        f'{STATUS_ICONS["pending"]} {case.name}'
                    )
                    case_item.setData(0, ROLE_TEST_RESULT, None)

    def _find_tree_item_by_name(self, case_name: str) -> Optional[QTreeWidgetItem]:
        """
        根据用例名查找树节点

        Args:
            case_name: 测试用例名称

        Returns:
            QTreeWidgetItem或None
        """
        root = self._tree_tests.invisibleRootItem()
        for i in range(root.childCount()):
            file_item = root.child(i)
            for j in range(file_item.childCount()):
                case_item = file_item.child(j)
                case = case_item.data(0, ROLE_TEST_CASE)
                if isinstance(case, TestCase) and case.name == case_name:
                    return case_item
        return None

    def _on_tree_item_changed(self, item: QTreeWidgetItem, column: int):
        """
        树节点复选框变化处理

        Args:
            item: 变化的节点
            column: 列号
        """
        if column != 0:
            return

        # 如果是文件节点，同步子节点
        case = item.data(0, ROLE_TEST_CASE)
        suite = item.data(0, ROLE_SUITE)

        if suite and not case:
            # 文件节点：同步所有子节点
            state = item.checkState(0)
            for i in range(item.childCount()):
                child = item.child(i)
                child.setCheckState(0, state)

    def _on_tree_selection_changed(self):
        """树选择变化处理 - 更新详情Tab"""
        case = self.get_selected_test_case()
        if case:
            self.show_case_detail(case)

    def _show_tree_context_menu(self, position):
        """
        显示右键上下文菜单

        Args:
            position: 鼠标位置
        """
        item = self._tree_tests.itemAt(position)
        if not item:
            return

        case = item.data(0, ROLE_TEST_CASE)
        if not isinstance(case, TestCase):
            return

        menu = QMenu(self)

        # 运行动作
        action_run = menu.addAction('\u25B6 运行此用例')
        action_run.triggered.connect(
            lambda: self._run_single_case(case.name)
        )

        menu.addSeparator()

        # 查看详情动作
        action_detail = menu.addAction('\uD83D\uDCDD 查看详情')
        action_detail.triggered.connect(
            lambda: self.show_case_detail(case)
        )

        # 跳转到源码动作
        action_jump = menu.addAction('\uD83D\uDD17 跳转到源码')
        action_jump.triggered.connect(
            lambda: self.jump_to_source(
                case.file_path,
                case.start_line
            )
        )

        menu.exec_(self._tree_tests.viewport().mapToGlobal(position))

    def _select_all_cases(self):
        """全选所有用例"""
        self._set_all_check_states(Qt.Checked)

    def _deselect_all_cases(self):
        """取消全选"""
        self._set_all_check_states(Qt.Unchecked)

    def _select_failed_cases(self):
        """选择失败的用例"""
        # 先全不选
        self._set_all_check_states(Qt.Unchecked)

        # 再选中失败的
        failed_names = {
            r.test_case_name
            for r in self._results
            if r.status in (TestStatus.FAILED, TestStatus.ERROR)
        }

        root = self._tree_tests.invisibleRootItem()
        for i in range(root.childCount()):
            file_item = root.child(i)
            for j in range(file_item.childCount()):
                case_item = file_item.child(j)
                case = case_item.data(0, ROLE_TEST_CASE)
                if isinstance(case, TestCase) and case.name in failed_names:
                    case_item.setCheckState(0, Qt.Checked)

    def _set_all_check_states(self, state: Qt.CheckState):
        """
        设置所有用例节点的复选框状态

        Args:
            state: 目标状态
        """
        root = self._tree_tests.invisibleRootItem()
        for i in range(root.childCount()):
            file_item = root.child(i)
            file_item.setCheckState(0, state)
            for j in range(file_item.childCount()):
                case_item = file_item.child(j)
                case_item.setCheckState(0, state)

    def _run_single_case(self, case_name: str):
        """
        运行单个测试用例

        Args:
            case_name: 要运行的用例名称
        """
        # 临时设置只运行这一个
        original_mode = self._combo_mode.currentIndex()
        self._combo_mode.setCurrentIndex(1)  # 选中模式

        # 先只勾选这个用例
        self._set_all_check_states(Qt.Unchecked)
        item = self._find_tree_item_by_name(case_name)
        if item:
            item.setCheckState(0, Qt.Checked)

        # 执行
        self.run_tests('selected')

        # 恢复原来的选择状态（简化处理：实际可能需要保存恢复）

    # ========================================================================
    # 内部实现方法 - 详情Tab
    # ========================================================================

    def show_case_detail(self, test_case: TestCase):
        """
        显示用例详情到详情Tab

        Args:
            test_case: 测试用例对象
        """
        if not test_case:
            return

        # 切换到详情Tab
        self._tab_widget.setCurrentIndex(0)

        # 更新基本信息
        self._lbl_case_name.setText(test_case.name)

        file_info = str(test_case.file_path) if test_case.file_path else '-'
        if test_case.start_line and test_case.end_line:
            file_info += f':{test_case.start_line}-{test_case.end_line}'
        self._lbl_file_path.setText(file_info)

        # 测试目标（描述）
        if test_case.description:
            self._txt_target.setPlainText(test_case.description)
        else:
            self._txt_target.setPlainText('(无描述)')

        # 清空并填充步骤列表
        self._list_steps.clear()
        for idx, step in enumerate(test_case.steps, 1):
            icon = STEP_ICONS.get(step.step_type, '?')
            step_text = str(step)
            item = QListWidgetItem(f'{idx}. {icon} {step_text}')
            item.setToolTip(step.raw_line or step_text)

            # 根据步骤类型设置颜色
            if step.step_type == StepType.ASSERT:
                item.setForeground(QColor('#1976D2'))
            elif step.step_type == StepType.SET:
                item.setForeground(QColor('#388E3C'))

            self._list_steps.addItem(item)

    # ========================================================================
    # 内部实现方法 - 日志Tab
    # ========================================================================

    def append_log(self, message: str, level: str = 'INFO'):
        """
        追加日志到日志Tab

        Args:
            message: 日志消息
            level: 日志级别 ('INFO'/'WARNING'/'ERROR'/'DEBUG')
        """
        timestamp = datetime.now().strftime('%H:%M:%S.') + \
                    f'{datetime.now().microsecond // 1000:03d}'
        color = LOG_COLORS.get(level, '#000000')

        formatted = f'<span style="color:#888;">[{timestamp}]</span> ' \
                   f'<span style="color:{color};font-weight:bold;">{level}</span> ' \
                   f'<span style="color:{color};">{message}</span>'

        self._txt_log.append(formatted)

        # 自动滚动到底部
        scrollbar = self._txt_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _clear_log(self):
        """清空日志"""
        self._txt_log.clear()
        self.append_log('日志已清空', 'INFO')

    def _save_log(self):
        """保存日志到文件"""
        if not self._txt_log.toPlainText().strip():
            QMessageBox.information(self, '提示', '日志为空，无需保存')
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            '保存日志',
            f'test_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
            'Log Files (*.log);;Text Files (*.txt);;All Files (*)'
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self._txt_log.toPlainText())
                QMessageBox.information(
                    self,
                    '成功',
                    f'日志已保存至:\n{file_path}'
                )
                logger.info(f"日志已保存: {file_path}")
            except Exception as e:
                QMessageBox.critical(
                    self,
                    '错误',
                    f'保存日志失败:\n{str(e)}'
                )

    # ========================================================================
    # 内部实现方法 - 结果Tab
    # ========================================================================

    def _update_result_summary(self, summary: TestRunSummary):
        """
        更新结果汇总Tab

        Args:
            summary: 运行摘要对象
        """
        # 更新统计标签
        self._lbl_total.setText(f'总计: {summary.total_tests}')
        self._lbl_passed.setText(f'通过: {summary.passed_tests}')
        self._lbl_failed.setText(f'失败: {summary.failed_tests + summary.error_tests}')
        self._lbl_rate.setText(f'通过率: {summary.success_rate:.1f}%')
        self._lbl_duration.setText(f'耗时: {summary.total_duration_seconds:.3f}s')

        # 更新进度条
        self._progress_bar.setVisible(True)
        self._progress_bar.setRange(0, summary.total_tests)
        self._progress_bar.setValue(summary.total_tests)

        # 更新结果表格
        self._populate_result_table(summary.test_results)

    def _populate_result_table(self, results: List[TestResult]):
        """
        填充结果表格

        Args:
            results: 测试结果列表
        """
        self._table_results.setRowCount(len(results))

        for row, result in enumerate(results):
            # 用例名
            name_item = QTableWidgetItem(result.test_case_name)
            name_item.setData(Qt.UserRole, result)
            self._table_results.setItem(row, 0, name_item)

            # 状态
            status_icon = STATUS_ICONS.get(
                result.status.name.lower(),
                '?'
            )
            status_item = QTableWidgetItem(
                f'{status_icon} {result.status.name}'
            )
            if result.is_passed:
                status_item.setForeground(QColor('#4CAF50'))
            elif result.is_failed:
                status_item.setForeground(QColor('#F44336'))
            else:
                status_item.setForeground(QColor('#FF9800'))
            self._table_results.setItem(row, 1, status_item)

            # 耗时
            time_item = QTableWidgetItem(f'{result.duration_seconds:.3f}')
            self._table_results.setItem(row, 2, time_item)

            # 断言数
            assert_item = QTableWidgetItem(
                f'{result.passed_assertions}/{result.assertion_count}'
            )
            self._table_results.setItem(row, 3, assert_item)

    def _clear_result_table(self):
        """清空结果表格"""
        self._table_results.setRowCount(0)
        self._lbl_total.setText('总计: 0')
        self._lbl_passed.setText('通过: 0')
        self._lbl_failed.setText('失败: 0')
        self._lbl_rate.setText('通过率: 0%')
        self._lbl_duration.setText('耗时: 0.0s')

    def _on_result_item_double_clicked(self, item: QTableWidgetItem):
        """
        结果表格行双击事件

        Args:
            item: 被点击的表格项
        """
        row = item.row()
        result_item = self._table_results.item(row, 0)
        if result_item:
            result = result_item.data(Qt.UserRole)
            if isinstance(result, TestResult):
                # 查找对应的TestCase并显示详情
                for suite in self._suites:
                    tc = suite.get_test_case_by_name(result.test_case_name)
                    if tc:
                        self.show_case_detail(tc)
                        break

    # ========================================================================
    # 内部实现方法 - 设置Tab
    # ========================================================================

    def _apply_settings(self):
        """应用设置Tab中的配置"""
        # 更新配置对象
        self._config.plccheck_path = self._edit_plccheck.text().strip() or None
        self._config.timeout_seconds = self._spin_timeout.value()
        self._config.verbose = self._combo_verbose.currentIndex() >= 2

        # 如果服务存在，重新应用配置
        if self._service:
            self._service.config = self._config

        QMessageBox.information(
            self,
            '成功',
            '设置已应用'
        )
        logger.info("测试执行配置已更新")

    def _browse_plccheck_path(self):
        """浏览选择plccheck可执行文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            '选择plccheck可执行文件',
            '',
            'Executable Files (*.exe);;All Files (*)'
        )

        if file_path:
            self._edit_plccheck.setText(file_path)

    # ========================================================================
    # 辅助方法
    # ========================================================================

    def jump_to_source(self, file_path: Path, line_number: int):
        """
        跳转到源码位置

        Args:
            file_path: 文件路径
            line_number: 行号
        """
        logger.info(f"请求跳转源码: {file_path}:{line_number}")
        self.source_jump_requested.emit(str(file_path), line_number)

    def _update_status_label(self, text: str):
        """
        更新状态标签

        Args:
            text: 状态文本
        """
        self._lbl_status.setText(text)

    def _update_timer_display(self):
        """更新计时器显示"""
        if self._start_time:
            elapsed = datetime.now() - self._start_time
            total_seconds = elapsed.total_seconds()
            minutes = int(total_seconds // 60)
            seconds = total_seconds % 60
            self._lbl_elapsed.setText(
                f'已用时: {minutes:02d}:{seconds:06.3f}'
            )


# ============================================================================
# 主程序入口（用于测试）
# ============================================================================

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # 创建面板
    panel = TestRunnerPanel()
    panel.setWindowTitle('PLC测试运行器 - TestRunnerPanel')
    panel.resize(1100, 700)

    # 设置项目路径（如果提供了命令行参数）
    if len(sys.argv) > 1:
        panel.set_project_path(Path(sys.argv[1]))

    panel.show()

    sys.exit(app.exec_())
