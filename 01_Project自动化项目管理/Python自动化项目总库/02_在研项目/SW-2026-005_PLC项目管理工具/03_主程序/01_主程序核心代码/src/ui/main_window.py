# -*- coding: utf-8 -*-
"""
SW-2026-005 PLC项目管理工具 - 主窗口 (薄壳设计)

基于QMainWindow构建的应用主窗口，采用薄壳架构模式:
- 只负责UI组件的组装和协调
- 所有业务逻辑委托给对应的Manager和Service
- 通过EventBus实现模块间松耦合通信

布局结构:
    QMainWindow
    └── centralWidget (QWidget with QHBoxLayout)
        ├── left_panel (QToolBox, 220px)   - 导航面板
        │   ├── 项目管理 (ProjectTreeWidget)
        │   ├── 文档管理 (占位符)
        │   ├── PLC工具 (占位符)
        │   ├── HMI工具 (占位符)
        │   ├── 规范中心 (占位符)
        │   └── 系统设置 (占位符)
        └── right_panel (QTabWidget)        - 内容区域
            ├── 仪表盘 (DashboardPage)
            ├── 项目视图 (占位符)
            ├── 文档编辑器 (占位符)
            ├── PLC代码工具 (占位符)
            ├── HMI变量映射 (占位符)
            └── 规范检查 (占位符)

重构说明 (Phase 0):
    - 原文件817行 -> 重构后 < 300行
    - 提取菜单逻辑到 MenuManager
    - 提取工具栏逻辑到 ToolBarManager
    - 提取设置对话框到 SettingsDialog
    - 引入 EventBus 实现事件解耦
"""
from pathlib import Path
from typing import TYPE_CHECKING

from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QTabWidget,
    QToolBox,
    QLabel,
    QStatusBar,
    QMessageBox,
    QDockWidget,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

if TYPE_CHECKING:
    from PyQt5.QtGui import QCloseEvent

from src.core.config import ConfigLoader
from src.core.constants import APP_NAME, VERSION
from src.core.settings import SettingsManager
from src.core.event_bus import EventBus
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class MainWindow(QMainWindow):
    """
    应用主窗口 (薄壳设计)

    职责:
    - 组装UI布局结构
    - 协调各Manager和Panel组件
    - 连接EventBus信号到槽函数
    - 处理窗口级别的事件 (关闭、初始化等)

    设计原则:
    - 单一职责: 只负责组装和协调
    - 高内聚低耦合: 通过EventBus通信
    - 可测试性: 核心逻辑可独立测试
    """

    # 常量定义
    WINDOW_TITLE = f"{APP_NAME} V{VERSION}"
    MIN_WIDTH = 1400
    MIN_HEIGHT = 900
    SIDEBAR_DEFAULT_WIDTH = 220

    def __init__(self, parent=None):
        """
        初始化主窗口

        Args:
            parent: 父窗口 (通常为None)
        """
        super().__init__(parent)

        # 核心组件引用
        self._event_bus: EventBus = None
        self._menu_manager = None
        self._toolbar_manager = None
        self._tool_box: QToolBox = None
        self._tab_widget: QTabWidget = None
        self._splitter: QSplitter = None

        # 新增面板实例（DockWidget）
        self._spec_check_dock: QDockWidget = None
        self._diagnostic_dock: QDockWidget = None
        self._test_runner_dock: QDockWidget = None
        self._spec_check_panel = None
        self._diagnostic_panel = None
        self._test_runner_panel = None

        # 基础窗口设置
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)
        self.resize(1500, 950)

        # 初始化核心服务
        self._init_core_services()

        # 按顺序组装UI (委托给各Manager)
        self._setup_styles()           # 加载主题样式
        self._build_central_widget()   # 中央部件: 水平分割器
        self._build_left_panel()       # 左侧ToolBox导航
        self._build_right_panel()      # 右侧TabWidget内容区
        self._build_managers()         # 菜单/工具栏/状态栏
        self._build_dock_panels()      # 新增：创建DockWidget面板
        self._connect_events()         # 连接EventBus信号

        # 加载初始数据
        self._load_initial_data()

        logger.info("主窗口初始化完成 (薄壳架构)")

    def _init_core_services(self):
        """初始化核心服务"""
        # 获取EventBus单例
        self._event_bus = EventBus.get_instance()

    def _setup_styles(self):
        """
        设置窗口全局样式 - Material Design风格

        优先级:
        1. 外部QSS主题文件 (resources/styles/material_{theme}.qss)
        2. 内置默认样式回退
        """
        font = QFont("Microsoft YaHei", 10)
        self.setFont(font)

        # 尝试加载外部QSS主题文件
        theme = SettingsManager.get("theme", "light")
        qss_path = (
            Path(__file__).parent.parent.parent.parent
            / "resources"
            / "styles"
            / f"material_{theme}.qss"
        )

        if qss_path.exists():
            try:
                with open(qss_path, 'r', encoding='utf-8') as f:
                    qss_content = f.read()
                    self.setStyleSheet(qss_content)
                logger.debug(f"已加载主题样式: {qss_path}")
                return
            except IOError as e:
                logger.warning(f"主题文件读取失败: {e}")

        # 内置默认样式回退
        self.setStyleSheet(self._get_default_stylesheet())

    @staticmethod
    def _get_default_stylesheet() -> str:
        """获取内置默认样式表 (Material Design风格)"""
        return """
            QMainWindow { background-color: #FAFAFA; }
            QTabWidget {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                margin: 8px;
            }
            QTabBar::tab {
                background-color: #F5F5F5;
                color: #616161;
                padding: 10px 24px;
                margin-right: 4px;
                border-radius: 6px 6px 0 0;
                font-size: 10pt;
                min-width: 80px;
            }
            QTabBar::tab:hover { background-color: #E8E8E8; }
            QTabBar::tab:selected {
                background-color: #FFFFFF;
                color: #1976D2;
                border-bottom: 3px solid #1976D2;
            }
            QToolBox {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
            QToolBox::tab {
                background-color: #F5F5F5;
                color: #424242;
                padding: 12px 16px;
                font-size: 10pt;
                font-weight: bold;
            }
            QToolBox::tab:selected { background-color: #E3F2FD; color: #1976D2; }
            QPushButton {
                background-color: #1976D2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 9pt;
            }
            QPushButton:hover { background-color: #1565C0; }
            QPushButton:pressed { background-color: #0D47A1; }
            QPushButton:disabled { background-color: #BDBDBD; color: #757575; }
            QLineEdit, QTextEdit, QPlainTextEdit {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 6px 10px;
                background-color: #FFFFFF;
                selection-background-color: #BBDEFB;
            }
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
                border-color: #1976D2;
            }
            QComboBox {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 6px 10px;
                background-color: #FFFFFF;
            }
            QComboBox:focus { border-color: #1976D2; }
            QTableWidget {
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                background-color: #FFFFFF;
                gridline-color: #EEEEEE;
            }
            QTableWidget::item { padding: 6px; }
            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: #0D47A1;
            }
            QHeaderView::section {
                background-color: #FAFAFA;
                color: #616161;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #E0E0E0;
                font-weight: bold;
            }
            QMenuBar {
                background-color: #FFFFFF;
                border-bottom: 1px solid #E0E0E0;
                padding: 2px 0;
            }
            QMenuBar::item { padding: 8px 16px; color: #424242; }
            QMenuBar::item:selected { background-color: #E3F2FD; color: #1976D2; }
            QMenu {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 4px 0;
            }
            QMenu::item { padding: 8px 24px; color: #424242; font-size: 9pt; }
            QMenu::item:selected { background-color: #E3F2FD; color: #0D47A1; }
            QStatusBar {
                background-color: #FFFFFF;
                border-top: 1px solid #E0E0E0;
                padding: 4px 16px;
                font-size: 9pt;
                color: #757575;
            }
            QToolBar {
                background-color: #FFFFFF;
                border-bottom: 1px solid #E0E0E0;
                padding: 4px 8px;
                spacing: 4px;
            }
            QScrollBar:vertical {
                width: 10px;
                background-color: #F5F5F5;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #BDBDBD;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover { background-color: #9E9E9E; }
        """

    def _build_central_widget(self):
        """构建中央部件: 水平分割器容器"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # 创建水平分割器
        self._splitter = QSplitter(Qt.Horizontal)

    def _build_left_panel(self):
        """
        构建左侧导航面板 (QToolBox)

        导航页面:
        - 项目管理: ProjectTreeWidget (已实现)
        - 文档管理: 占位符 (TODO Phase 1)
        - PLC工具: 占位符 (TODO Phase 2)
        - HMI工具: 占位符 (TODO Phase 4)
        - 规范中心: 占位符 (TODO Phase 4)
        - 系统设置: 占位符 (TODO Phase 0.4后替换)
        """
        self._tool_box = QToolBox()
        self._tool_box.setMinimumWidth(200)
        self._tool_box.setMaximumWidth(300)

        # 页面1: 项目管理 (使用实际组件)
        from .widgets.project_tree import ProjectTreeWidget
        
        project_page = QWidget()
        project_layout = QVBoxLayout(project_page)
        project_layout.setContentsMargins(8, 8, 8, 8)
        self._project_tree_widget = ProjectTreeWidget()
        project_layout.addWidget(self._project_tree_widget)
        self._tool_box.addItem(project_page, "  \u25B7 项目管理  ")

        # 页面2-6: 占位符 (后续Phase实现)
        placeholder_pages = [
            ("文档管理", "文档模板与列表\n\n(开发中...)"),
            ("PLC工具", "ST代码编辑器\n变量检查器\nIO分配表\n\n(开发中...)"),
            ("HMI工具", "HMI变量映射\n报警配置\n\n(开发中...)"),
            ("规范中心", "801规范校验\n文档规范检查\n\n(开发中...)"),
            ("系统设置", "主题切换\n编辑器配置\n路径设置\n\n(开发中...)"),
        ]

        for title, content in placeholder_pages:
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setContentsMargins(8, 8, 8, 8)
            layout.addWidget(QLabel(content))
            self._tool_box.addItem(page, f"  \u25B7 {title}  ")

        # 添加到分割器
        self._splitter.addWidget(self._tool_box)

    def _build_right_panel(self):
        """
        构建右侧内容区域 (QTabWidget)

        内容页面:
        - 仪表盘: DashboardPage (已实现)
        - 其他页面: 占位符 (后续Phase实现)
        """
        from .dashboard import DashboardPage

        self._tab_widget = QTabWidget()
        self._tab_widget.setTabPosition(QTabWidget.North)
        self._tab_widget.setTabShape(QTabWidget.Rounded)
        self._tab_widget.setElideMode(Qt.ElideRight)

        # Tab 1: 仪表盘 (使用实际组件)
        self._dashboard_page = DashboardPage()
        self._tab_widget.addTab(self._dashboard_page, "\u2630 仪表盘")

        # Tab 2-6: 占位符 (后续Phase实现)
        placeholder_tabs = [
            ("\uD83D\uDCC1 项目",),
            ("\uD83D\uDCDD 文档",),
            ("\u26A1 PLC工具",),
            ("\uD83D\uDDA5 HMI映射",),
            ("\u2705 规范检查",),
        ]

        for tab_title in placeholder_tabs:
            self._tab_widget.addTab(QWidget(), tab_title[0])

        # 添加到分割器并设置比例
        self._splitter.addWidget(self._tab_widget)
        self._splitter.setStretchFactor(0, 0)
        self._splitter.setStretchFactor(1, 1)
        self._splitter.setSizes([self.SIDEBAR_DEFAULT_WIDTH, 1200])

        # 将分割器添加到中央部件布局
        self.centralWidget().layout().addWidget(self._splitter)

    def _build_managers(self):
        """
        构建菜单、工具栏和状态栏 (委托给Manager)

        创建顺序:
        1. MenuManager - 构建完整菜单栏
        2. ToolBarManager - 构建主工具栏
        3. StatusBar - 构建状态栏
        """
        # 菜单管理器
        from .managers.menu_manager import MenuManager
        self._menu_manager = MenuManager(self, self._event_bus)
        self._menu_manager.build()

        # 工具栏管理器
        from .managers.toolbar_manager import ToolBarManager
        self._toolbar_manager = ToolBarManager(self, self._event_bus)
        self._toolbar_manager.build()

        # 状态栏
        self._build_status_bar()

    def _build_status_bar(self):
        """初始化状态栏"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        status_bar.showMessage(
            "\u2705 \u5C31\u7EEA - SW-2026-005 PLC\u9879\u76EE\u7BA1\u7406\u5DE5\u5177 V1.0.0"
        )

    def _build_dock_panels(self):
        """
        创建三个DockWidget面板（新增功能）

        面板列表：
        1. SpecCheckPanel - 规范检查面板
        2. DiagnosticPanel - 深度诊断面板
        3. TestRunnerPanel - 测试运行器面板

        所有面板都作为QDockWidget添加到主窗口，
        支持浮动、停靠和关闭功能。
        """
        try:
            # ===== 1. 创建规范检查面板 =====
            from .widgets.spec_check_panel import SpecCheckPanel

            self._spec_check_panel = SpecCheckPanel()
            self._spec_check_dock = QDockWidget(
                "\U0001F50D \u89C4\u8303\u68C0\u67E5", self
            )
            self._spec_check_dock.setWidget(self._spec_check_panel)
            self._spec_check_dock.setMinimumWidth(600)
            self._spec_check_dock.setMinimumHeight(400)
            # 设置初始位置：右侧
            self.addDockWidget(Qt.RightDockWidgetArea, self._spec_check_dock)

            # 连接信号
            self._spec_check_panel.source_jump_requested.connect(
                self._jump_to_source
            )
            logger.info("规范检查面板已创建")

            # ===== 2. 创建深度诊断面板 =====
            from .widgets.diagnostic_panel import DiagnosticPanel

            self._diagnostic_panel = DiagnosticPanel()
            self._diagnostic_dock = QDockWidget(
                "\U0001F52C \u6DF1\u5EA6\u8BCA\u65AD", self
            )
            self._diagnostic_dock.setWidget(self._diagnostic_panel)
            self._diagnostic_dock.setMinimumWidth(700)
            self._diagnostic_dock.setMinimumHeight(450)
            # 设置初始位置：底部（在规范检查下方）
            self.addDockWidget(
                Qt.BottomDockWidgetArea, self._diagnostic_dock
            )

            # 连接信号
            self._diagnostic_panel.source_jump_requested.connect(
                self._jump_to_source
            )
            logger.info("深度诊断面板已创建")

            # ===== 3. 创建测试运行器面板 =====
            from .widgets.test_runner_panel import TestRunnerPanel

            self._test_runner_panel = TestRunnerPanel()
            self._test_runner_dock = QDockWidget(
                "\u25B6 \u6D4B\u8BD5\u8FD0\u884C\u5668", self
            )
            self._test_runner_dock.setWidget(self._test_runner_panel)
            self._test_runner_dock.setMinimumWidth(650)
            self._test_runner_dock.setMinimumHeight(400)
            # 设置初始位置：底部（与诊断面板并列）
            self.addDockWidget(
                Qt.BottomDockWidgetArea, self._test_runner_dock
            )

            # 连接信号
            self._test_runner_panel.source_jump_requested.connect(
                self._jump_to_source
            )
            logger.info("测试运行器面板已创建")

            # 将诊断面板和测试面板选项卡化（并排显示）
            self.tabifyDockWidget(
                self._diagnostic_dock, self._test_runner_dock
            )

            # 默认隐藏这些面板（用户可通过菜单或视图打开）
            self._spec_check_dock.hide()
            self._diagnostic_dock.hide()
            self._test_runner_dock.hide()

            logger.info("所有DockWidget面板创建完成")

        except ImportError as e:
            logger.error(f"无法导入面板组件: {e}")
        except Exception as e:
            logger.exception(f"创建DockWidget面板失败: {e}")

    def _jump_to_source(self, file_path: str, line_number: int):
        """
        跳转到源码位置（槽函数）

        响应各面板发出的source_jump_requested信号，
        打开指定文件并定位到指定行号。

        Args:
            file_path: 源文件路径
            line_number: 行号（从1开始）
        """
        try:
            logger.info(
                f"\u6536\u5230\u8DF3\u8F6C\u8BF7\u6C42: "
                f"{file_path}:{line_number}"
            )

            # TODO Phase 2: 实现真正的代码编辑器跳转功能
            # 这里可以：
            # 1. 切换到代码编辑器Tab
            # 2. 打开指定的ST源文件
            # 3. 定位到指定行并高亮显示

            # 当前实现：显示提示信息
            self.statusBar().showMessage(
                f"\U0001F517 \u8DF3\u8F6C\u5230: {file_path}:{line_number}",
                5000  # 显示5秒
            )

            QMessageBox.information(
                self,
                "\U0001F517 \u6E90\u7801\u8DF3\u8F6C",
                f"\u8BF7\u6C42\u8DF3\u8F6C\u5230:\n\n"
                f"\u6587\u4EF6: {file_path}\n"
                f"\u884C\u53F7: {line_number}\n\n"
                f"\uFF08\u4EE3\u7801\u7F16\u8F91\u529F\u80FD\u5373\u5C06\u63A8\u51FA\uFF09",
                QMessageBox.Ok,
            )

        except Exception as e:
            logger.exception(f"跳转到源码位置失败: {e}")

    def _connect_events(self):
        """
        连接EventBus信号到槽函数

        监听的事件:
        - project_created: 新项目创建完成
        - project_opened: 项目被打开
        - document_open_request: 文档打开请求
        - theme_changed: 主题切换
        - settings_changed: 设置变更
        """
        self._event_bus.project_created.connect(self._on_project_created)
        self._event_bus.project_opened.connect(self._on_project_opened)
        self._event_bus.document_open_request.connect(self._on_document_open)
        self._event_bus.theme_changed.connect(self._on_theme_changed)
        self._event_bus.settings_changed.connect(self._on_settings_changed)

    def _load_initial_data(self):
        """
        加载初始数据（增强容错处理）

        初始化项:
        - 用户设置 (SettingsManager)
        - 内置模板 (TemplateService)
        """
        init_errors = []

        try:
            SettingsManager.initialize()
            logger.debug("用户设置已初始化")
        except Exception as e:
            logger.warning(f"用户设置初始化失败: {e}")
            init_errors.append(f"设置初始化异常: {str(e)}")

        try:
            from src.services.template_service import TemplateService
            TemplateService.initialize_builtin_templates()
            logger.debug("内置模板已初始化")
        except Exception as e:
            logger.exception(f"模板初始化失败: {e}")
            init_errors.append(f"模板初始化失败: {str(e)}")

        if init_errors:
            error_summary = "\n".join([f"\u2022 {err}" for err in init_errors])
            QMessageBox.warning(
                self,
                "\u26A0\uFE0F 提示",
                f"部分数据加载未就绪:\n{error_summary}\n\n"
                f"程序将继续运行，部分功能可能不可用",
            )

    # ===== EventBus 事件处理方法 =====

    def _on_project_created(self, path: str):
        """
        新项目创建完成事件处理

        Args:
            path: 新建项目的根路径
        """
        try:
            # 尝试加载新项目到项目树
            from src.services.project_service import ProjectService
            from src.core.project import Project

            created_project = None
            for proj in ProjectService.get_all_projects():
                if getattr(proj, 'path', '') == path:
                    created_project = proj
                    break

            if created_project:
                self._project_tree_widget.load_project(created_project)
                logger.info(f"项目树已刷新: {created_project.name}")
            else:
                # 如果缓存中没有，尝试从路径加载
                project, error = ProjectService.load_project_from_path(path)
                if project:
                    self._project_tree_widget.load_project(project)
                    logger.info(f"从路径加载并刷新项目树: {project.name}")
                else:
                    logger.warning(f"无法加载项目到树: {error}")

        except Exception as e:
            logger.warning(f"刷新项目树时出错 (非致命): {e}")

    def _on_project_opened(self, path: str):
        """
        项目打开事件处理

        Args:
            path: 打开的项目路径
        """
        # 可以在这里添加额外的打开后处理逻辑
        pass

    def _on_document_open(self, path: str):
        """
        文档打开请求事件处理

        Args:
            path: 文档路径
        """
        # TODO Phase 1: 切换到文档编辑Tab并打开文档
        logger.info(f"收到文档打开请求: {path}")

    def _on_theme_changed(self, theme: str):
        """
        主题切换事件处理

        Args:
            theme: 主题名称 ('light' | 'dark')
        """
        self._setup_styles()
        logger.info(f"主题已切换为: {theme}")

    def _on_settings_changed(self):
        """设置变更事件处理"""
        # 可以在这里添加设置变更后的刷新逻辑
        logger.debug("检测到设置变更")

    # ===== 窗口事件处理 =====

    def closeEvent(self, event: QCloseEvent):
        """
        窗口关闭事件处理

        Args:
            event: 关闭事件对象
        """
        reply = QMessageBox.question(
            self,
            "\u2753 确认退出",
            "确定要退出 PLC项目管理工具 吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            # 保存窗口状态
            try:
                SettingsManager.save()
            except Exception:
                pass
            logger.info("用户确认退出应用")
            event.accept()
        else:
            event.ignore()
