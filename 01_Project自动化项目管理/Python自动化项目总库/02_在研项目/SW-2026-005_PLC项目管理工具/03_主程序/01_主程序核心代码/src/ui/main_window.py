# -*- coding: utf-8 -*-
from pathlib import Path

from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QSplitter,
    QTabWidget,
    QToolBox,
    QStatusBar,
    QMessageBox,
    QDockWidget,
)
from PyQt5.QtGui import QCloseEvent, QGuiApplication
from PyQt5.QtCore import Qt

from src.core.constants import APP_NAME, VERSION
from src.core.settings import SettingsManager
from src.core.event_bus import EventBus
from src.ui.controllers import ProjectController, SyncController, DashboardController
from src.ui.controllers.navigation_controller import NavigationController
from src.ui.builders import LeftPanelBuilder, RightPanelBuilder, StyleBuilder, DockPanelBuilder
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class MainWindow(QMainWindow):

    WINDOW_TITLE = f"{APP_NAME} V{VERSION}"
    MIN_WIDTH = 1200
    MIN_HEIGHT = 800
    SIDEBAR_DEFAULT_WIDTH = 240
    SIDEBAR_MIN_WIDTH = 180
    SIDEBAR_MAX_WIDTH = 320

    TAB_DASHBOARD = 0
    TAB_PROJECT = 1
    TAB_DOCUMENT = 2
    TAB_CHANGE_MGMT = 3
    TAB_PLC_TOOLS = 4
    TAB_SPEC_CHECK = 5

    def __init__(self, parent=None):
        super().__init__(parent)

        self._event_bus: EventBus = None
        self._menu_manager = None
        self._toolbar_manager = None
        self._tool_box: QToolBox = None
        self._tab_widget: QTabWidget = None
        self._splitter: QSplitter = None
        self._nav_ctrl: NavigationController = None

        self._spec_check_dock: QDockWidget = None
        self._diagnostic_dock: QDockWidget = None
        self._spec_check_panel = None
        self._diagnostic_panel = None

        self._dashboard_page = None
        self._project_info_widget = None
        self._document_editor = None
        self._change_mgmt_panel = None
        self._plc_tools_tabs = None
        self._st_editor = None
        self._spec_check_tab_panel = None
        self._project_tree_widget = None
        self._project_info_labels = {}

        self._project_ctrl: ProjectController = None
        self._sync_ctrl: SyncController = None
        self._dashboard_ctrl: DashboardController = None

        self.setWindowTitle(self.WINDOW_TITLE)
        self._apply_initial_geometry()

        self._init_core_services()

        theme = SettingsManager.get("theme", "light")
        StyleBuilder.apply(self, theme)
        self._build_central_widget()
        self._build_left_panel()
        self._build_right_panel()
        self._build_managers()
        self._build_dock_panels()
        self._connect_events()

        self._load_initial_data()

        logger.info("主窗口初始化完成 (薄壳架构)")

    def _apply_initial_geometry(self):
        screen = self.screen() or QGuiApplication.primaryScreen()
        if not screen:
            self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)
            self.resize(max(self.MIN_WIDTH, 1200), max(self.MIN_HEIGHT, 800))
            return

        available = screen.availableGeometry()
        target_w = int(available.width() * 0.92)
        target_h = int(available.height() * 0.92)
        target_w = max(800, min(target_w, available.width()))
        target_h = max(600, min(target_h, available.height()))
        min_w = min(self.MIN_WIDTH, available.width())
        min_h = min(self.MIN_HEIGHT, available.height())
        self.setMinimumSize(min_w, min_h)
        x = available.x() + max(0, (available.width() - target_w) // 2)
        y = available.y() + max(0, (available.height() - target_h) // 2)
        self.setGeometry(x, y, target_w, target_h)

    def _on_splitter_moved(self, pos: int, index: int):
        try:
            if not self._splitter:
                return
            sizes = self._splitter.sizes()
            if sizes:
                SettingsManager.set("sidebar_width", int(sizes[0]))
        except Exception:
            pass

    def _init_core_services(self):
        self._event_bus = EventBus.get_instance()
        self._project_ctrl = ProjectController(self)
        self._sync_ctrl = SyncController(self)
        self._dashboard_ctrl = DashboardController(self)

    def _build_central_widget(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        self._splitter = QSplitter(Qt.Horizontal)

    def _build_left_panel(self):
        self._tool_box = LeftPanelBuilder.build(self, self._on_action)
        self._project_tree_widget = self._tool_box._project_tree_widget
        self._project_tree_widget.navigation_requested.connect(
            self._on_project_tree_navigate
        )
        self._splitter.addWidget(self._tool_box)

    def _build_right_panel(self):
        result = RightPanelBuilder.build(self, jump_handler=self._jump_to_source)
        self._tab_widget = result["tab_widget"]
        self._dashboard_page = result["dashboard_page"]
        self._project_info_widget = result["project_info_widget"]
        self._document_editor = result["document_editor"]
        self._change_mgmt_panel = result["change_mgmt_panel"]
        self._plc_tools_tabs = result["plc_tools_tabs"]
        self._st_editor = result["st_editor"]
        self._spec_check_tab_panel = result["spec_check_tab_panel"]
        self._project_info_labels = result["project_info_labels"]

        if hasattr(self._spec_check_tab_panel, '_open_spec_check_btn'):
            self._spec_check_tab_panel._open_spec_check_btn.clicked.connect(
                self._show_spec_check_dock
            )

        self._splitter.addWidget(self._tab_widget)
        self._splitter.setStretchFactor(0, 0)
        self._splitter.setStretchFactor(1, 1)

        saved_width = SettingsManager.get("sidebar_width", self.SIDEBAR_DEFAULT_WIDTH)
        try:
            saved_width = int(saved_width)
        except Exception:
            saved_width = self.SIDEBAR_DEFAULT_WIDTH

        sidebar_width = max(
            self.SIDEBAR_MIN_WIDTH,
            min(saved_width, self.SIDEBAR_MAX_WIDTH)
        )
        right_width = max(800, self.width() - sidebar_width)
        self._splitter.setSizes([sidebar_width, right_width])
        self._splitter.splitterMoved.connect(self._on_splitter_moved)
        self.centralWidget().layout().addWidget(self._splitter)

    def _build_managers(self):
        from .managers.menu_manager import MenuManager
        self._menu_manager = MenuManager(self, self._event_bus)
        self._menu_manager.build()

        from .managers.toolbar_manager import ToolBarManager
        self._toolbar_manager = ToolBarManager(self, self._event_bus)
        self._toolbar_manager.build()

        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        status_bar.showMessage(
            "\u2705 \u5C31\u7EEA - SW-2026-005 PLC\u9879\u76EE\u7BA1\u7406\u5DE5\u5177 V1.0.0"
        )

    def _build_dock_panels(self):
        result = DockPanelBuilder.build(self)
        self._diagnostic_panel = result["diagnostic_panel"]
        self._diagnostic_dock = result["diagnostic_dock"]
        self._spec_check_panel = result["spec_check_panel"]
        self._spec_check_dock = result["spec_check_dock"]

    def _show_spec_check_dock(self):
        if self._spec_check_dock:
            self._spec_check_dock.show()
            self._spec_check_dock.raise_()

    def _jump_to_source(self, file_path: str, line_number: int):
        try:
            logger.info(f"收到跳转请求: {file_path}:{line_number}")
            if self._nav_ctrl:
                self._nav_ctrl.navigate_to_tab(self.TAB_PLC_TOOLS)
            if self._plc_tools_tabs and self._st_editor:
                self._plc_tools_tabs.setCurrentWidget(self._st_editor)
                if hasattr(self._st_editor, 'open_file'):
                    self._st_editor.open_file(file_path, line_number)
                elif hasattr(self._st_editor, 'load_file'):
                    self._st_editor.load_file(file_path)
                    if hasattr(self._st_editor, 'goto_line'):
                        self._st_editor.goto_line(line_number)
            self.statusBar().showMessage(
                f"\U0001F517 已定位到: {Path(file_path).name}:{line_number}", 5000
            )
        except Exception as e:
            logger.exception(f"跳转到源码位置失败: {e}")

    def _connect_events(self):
        self._event_bus.project_created.connect(self._on_project_created)
        self._event_bus.project_opened.connect(self._on_project_opened)
        self._event_bus.document_open_request.connect(self._on_document_open)
        self._event_bus.spec_check_request.connect(self._on_spec_check_request)
        self._event_bus.variable_check_request.connect(self._on_variable_check_request)
        self._event_bus.theme_changed.connect(self._on_theme_changed)
        self._event_bus.settings_changed.connect(self._on_settings_changed)

        self._nav_ctrl = NavigationController(
            self._tool_box, self._tab_widget,
            menu_manager=self._menu_manager,
            sync_handler=self._on_sync_action,
            project_info_handler=self._project_ctrl.update_project_info,
        )
        self._nav_ctrl.connect()

        if self._dashboard_page:
            self._dashboard_page.action_triggered.connect(self._on_dashboard_action)

    def _on_action(self, action):
        if isinstance(action, int):
            if self._nav_ctrl:
                self._nav_ctrl.navigate_to_tab(action)
        elif isinstance(action, str):
            if self._nav_ctrl:
                self._nav_ctrl.on_sidebar_action(action)

    def _on_project_tree_navigate(self, tab_index: int, context: dict = None):
        if self._nav_ctrl:
            self._nav_ctrl.on_project_tree_navigate(tab_index, context)

    def _on_sync_action(self, action_key: str):
        if action_key == "version_check":
            self._sync_ctrl.on_sync_version_check()
        elif action_key == "generate_chg":
            self._sync_ctrl.on_sync_generate_chg()
        elif action_key == "generate_ifc":
            self._sync_ctrl.on_sync_generate_ifc()

    def _load_initial_data(self):
        init_errors = []
        try:
            SettingsManager.initialize()
        except Exception as e:
            logger.warning(f"用户设置初始化失败: {e}")
            init_errors.append(f"设置初始化异常: {str(e)}")
        try:
            from src.services.template_service import TemplateService
            TemplateService.initialize_builtin_templates()
        except Exception as e:
            logger.exception(f"模板初始化失败: {e}")
            init_errors.append(f"模板初始化失败: {str(e)}")
        try:
            self._refresh_dashboard_data()
        except Exception as e:
            logger.warning(f"Dashboard数据初始刷新失败: {e}")
        if init_errors:
            error_summary = "\n".join([f"\u2022 {err}" for err in init_errors])
            QMessageBox.warning(
                self, "\u26A0\uFE0F 提示",
                f"部分数据加载未就绪:\n{error_summary}\n\n程序将继续运行，部分功能可能不可用",
            )

    def _on_project_created(self, path: str):
        self._project_ctrl.on_project_created(path)
        if self._change_mgmt_panel:
            self._change_mgmt_panel.set_project_path(path)

    def _on_project_opened(self, path: str):
        self._project_ctrl.on_project_opened(path)
        if self._change_mgmt_panel:
            self._change_mgmt_panel.set_project_path(path)

    def _on_document_open(self, path: str):
        logger.info(f"收到文档打开请求: {path}")

    def _on_spec_check_request(self, config: dict):
        self._show_spec_check_dock()

    def _on_variable_check_request(self):
        if self._nav_ctrl:
            self._nav_ctrl.navigate_to_tab(self.TAB_PLC_TOOLS)
        self.statusBar().showMessage(
            "\U0001F9EA 变量检查功能开发中，请使用规范检查替代", 5000
        )

    def _on_theme_changed(self, theme: str):
        StyleBuilder.apply(self, theme)
        logger.info(f"主题已切换为: {theme}")

    def _on_settings_changed(self):
        logger.debug("检测到设置变更")

    def _on_dashboard_action(self, action_id: str):
        self._dashboard_ctrl.on_dashboard_action(action_id)

    def _refresh_dashboard_data(self):
        self._dashboard_ctrl.refresh_dashboard_data()

    def get_dashboard_page(self):
        return self._dashboard_page

    def get_menu_manager(self):
        return self._menu_manager

    def get_project_tree_widget(self):
        return self._project_tree_widget

    def get_project_info_labels(self):
        return self._project_info_labels

    def closeEvent(self, event: QCloseEvent):
        reply = QMessageBox.question(
            self, "\u2753 确认退出", "确定要退出 PLC项目管理工具 吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self._cleanup_resources()
            try:
                SettingsManager.save()
            except Exception:
                pass
            logger.info("用户确认退出应用")
            event.accept()
        else:
            event.ignore()

    def _cleanup_resources(self):
        cleanup_targets = [
            self._diagnostic_panel,
            self._spec_check_panel,
            self._spec_check_tab_panel,
            self._change_mgmt_panel,
        ]
        for target in cleanup_targets:
            if target and hasattr(target, 'cleanup'):
                try:
                    target.cleanup()
                except Exception:
                    pass
