# -*- coding: utf-8 -*-
import os
from pathlib import Path

from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QTabWidget,
    QStatusBar,
    QMessageBox,
    QLabel,
    QGroupBox,
    QFormLayout,
    QTextEdit,
    QSplitter,
    QFrame,
    QComboBox,
    QSpinBox,
    QCheckBox,
    QPushButton,
    QLineEdit,
    QFileDialog,
    QSizePolicy,
)
from PyQt5.QtGui import QCloseEvent, QGuiApplication, QFont
from PyQt5.QtCore import Qt

from src.core.constants import APP_NAME, VERSION
from src.core.settings import SettingsManager
from src.core.event_bus import EventBus
from src.ui.controllers import ProjectController, SyncController, DashboardController
from src.ui.builders import StyleBuilder
from src.ui.ui_scale import current_ui_profile
from src.ui.widgets.activity_bar import ActivityBar
from src.ui.widgets.context_sidebar import ContextSidebar
from src.ui.widgets.tab_system import TabSystem, DASHBOARD_TAB_ID, DASHBOARD_TAB_TITLE
from src.ui.widgets.bottom_panel import BottomPanel
from src.ui.widgets.title_bar import TitleBar
from src.ui.dashboard import DashboardPage
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class MainWindow(QMainWindow):

    WINDOW_TITLE = f"{APP_NAME} V{VERSION}"
    MIN_WIDTH = 1320
    MIN_HEIGHT = 900
    SIDEBAR_DEFAULT_WIDTH = 280
    SIDEBAR_MIN_WIDTH = 210
    SIDEBAR_MAX_WIDTH = 400

    TAB_DASHBOARD = 0
    TAB_PROJECT = 1
    TAB_DOCUMENT = 2
    TAB_CHANGE_MGMT = 3
    TAB_PLC_TOOLS = 4
    TAB_SPEC_CHECK = 5

    _TAB_INDEX_TO_ACTIVITY = {
        TAB_DASHBOARD: "dashboard",
        TAB_PROJECT: "project",
        TAB_DOCUMENT: "document",
        TAB_CHANGE_MGMT: "change",
        TAB_PLC_TOOLS: "plc-tools",
        TAB_SPEC_CHECK: "spec",
    }

    _RESIZE_MARGIN = 4

    def __init__(self, parent=None):
        super().__init__(parent)

        self._event_bus: EventBus = None
        self._menu_manager = None
        self._toolbar_manager = None
        self._sidebar: ContextSidebar = None
        self._tab_system: TabSystem = None
        self._activity_bar: ActivityBar = None
        self._bottom_panel: BottomPanel = None
        self._title_bar: TitleBar = None

        self._dashboard_page = None
        self._project_info_widget = None
        self._document_editor = None
        self._change_mgmt_panel = None
        self._plc_tools_tabs = None
        self._st_editor = None
        self._spec_check_tab_panel = None
        self._auto_fix_panel = None
        self._excel_export_panel = None
        self._project_tree_widget = None
        self._project_info_labels = {}

        self._status_project_label = None
        self._status_spec_label = None
        self._status_warning_label = None
        self._status_encoding_label = None
        self._status_resolution_label = None

        self._project_ctrl: ProjectController = None
        self._sync_ctrl: SyncController = None
        self._dashboard_ctrl: DashboardController = None
        self._ui_profile = current_ui_profile(QGuiApplication.primaryScreen())

        try:
            SettingsManager.initialize()
        except Exception as e:
            logger.warning(f"用户设置预初始化失败，使用默认配置: {e}")

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)

        self.setWindowTitle(self.WINDOW_TITLE)
        self._apply_initial_geometry()

        self._init_core_services()

        theme = SettingsManager.get("theme", "ide_dark")
        StyleBuilder.apply(self, theme)
        self._build_ide_layout()
        self._build_managers()
        self._connect_events()

        self._load_initial_data()

        self._activity_bar.set_active_activity("dashboard")
        self._sidebar.setVisible(True)

        logger.info("主窗口初始化完成 (IDE五区布局+FramelessWindow)")

    def _apply_initial_geometry(self):
        profile = self._ui_profile
        screen = self.screen() or QGuiApplication.primaryScreen()
        if not screen:
            self.setMinimumSize(profile.window_min_width, profile.window_min_height)
            self.resize(profile.window_min_width, profile.window_min_height)
            return

        available = screen.availableGeometry()
        target_w = int(available.width() * 0.94)
        target_h = int(available.height() * 0.94)
        target_w = max(profile.window_min_width, min(target_w, available.width()))
        target_h = max(profile.window_min_height, min(target_h, available.height()))
        min_w = min(profile.window_min_width, available.width())
        min_h = min(profile.window_min_height, available.height())
        self.setMinimumSize(min_w, min_h)
        x = available.x() + max(0, (available.width() - target_w) // 2)
        y = available.y() + max(0, (available.height() - target_h) // 2)
        self.setGeometry(x, y, target_w, target_h)

    def _init_core_services(self):
        self._event_bus = EventBus.get_instance()
        self._project_ctrl = ProjectController(self)
        self._sync_ctrl = SyncController(self)
        self._dashboard_ctrl = DashboardController(self)

    def _build_ide_layout(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self._title_bar = TitleBar(self.WINDOW_TITLE)
        self._title_bar.minimize_requested.connect(self.showMinimized)
        self._title_bar.maximize_requested.connect(self._toggle_maximize)
        self._title_bar.close_requested.connect(self.close)
        root_layout.addWidget(self._title_bar)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._activity_bar = ActivityBar(ui_profile=self._ui_profile)
        self._activity_bar.setFixedWidth(48)
        main_layout.addWidget(self._activity_bar)

        self._sidebar = ContextSidebar()
        self._sidebar.setMaximumWidth(260)
        self._sidebar.setVisible(False)
        main_layout.addWidget(self._sidebar)

        content_panel = QWidget()
        content_layout = QVBoxLayout(content_panel)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self._tab_system = TabSystem()
        content_layout.addWidget(self._tab_system, 1)

        self._bottom_panel = BottomPanel()
        self._bottom_panel.setMinimumHeight(100)
        self._bottom_panel.setMaximumHeight(16777215)
        self._bottom_panel.resize(self._bottom_panel.width(), 200)
        content_layout.addWidget(self._bottom_panel)

        main_layout.addWidget(content_panel, 1)

        root_layout.addLayout(main_layout)

        self._dashboard_page = DashboardPage(ui_profile=self._ui_profile)
        self._dashboard_page.action_triggered.connect(self._on_dashboard_action)

        dash_info = self._tab_system._tabs[DASHBOARD_TAB_ID]
        placeholder = dash_info["widget"]
        dash_idx = self._tab_system.indexOf(placeholder)
        self._tab_system.removeTab(dash_idx)
        dash_info["widget"] = self._dashboard_page
        self._tab_system.insertTab(dash_idx, self._dashboard_page, DASHBOARD_TAB_TITLE)
        self._tab_system.setCurrentIndex(dash_idx)

    def _build_managers(self):
        from .managers.menu_manager import MenuManager
        self._menu_manager = MenuManager(self, self._event_bus)
        self._menu_manager.build()

        from .managers.toolbar_manager import ToolBarManager
        self._toolbar_manager = ToolBarManager(self, self._event_bus)
        self._toolbar_manager.build()

        self._build_status_bar()

    def _build_status_bar(self):
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        status_bar.setSizeGripEnabled(False)

        ready_label = QLabel("\u25B6 \u5C31\u7EEA")
        ready_label.setProperty("StatusBarReady", True)
        status_bar.addWidget(ready_label)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        spacer.setFixedWidth(16)
        status_bar.addWidget(spacer)

        self._status_project_label = QLabel("\U0001F4C1 -")
        self._status_project_label.setProperty("StatusBarItem", True)
        status_bar.addPermanentWidget(self._status_project_label)

        self._status_spec_label = QLabel("\u2705 \u89C4\u8303: -/-")
        self._status_spec_label.setProperty("StatusBarItem", True)
        status_bar.addPermanentWidget(self._status_spec_label)

        self._status_warning_label = QLabel("\u26A0 \u8B66\u544A: 0")
        self._status_warning_label.setProperty("StatusBarItem", True)
        status_bar.addPermanentWidget(self._status_warning_label)

        self._status_encoding_label = QLabel("\U0001F524 UTF-8")
        self._status_encoding_label.setProperty("StatusBarItem", True)
        status_bar.addPermanentWidget(self._status_encoding_label)

        self._status_resolution_label = QLabel("\u2195 -\u00D7-")
        self._status_resolution_label.setProperty("StatusBarItem", True)
        status_bar.addPermanentWidget(self._status_resolution_label)

        self._update_status_resolution()

    def _update_status_resolution(self):
        screen = self.screen() or QGuiApplication.primaryScreen()
        if screen:
            geo = screen.geometry()
            dpr = screen.devicePixelRatio()
            logical_w = int(geo.width())
            logical_h = int(geo.height())
            self._status_resolution_label.setText(f"\u2195 {logical_w}\u00D7{logical_h}")

    def update_status_project(self, project_id: str):
        if self._status_project_label:
            self._status_project_label.setText(f"\U0001F4C1 {project_id}")

    def update_status_spec(self, passed: int, total: int):
        if self._status_spec_label:
            self._status_spec_label.setText(f"\u2705 \u89C4\u8303: {passed}/{total}")

    def update_status_warnings(self, count: int):
        if self._status_warning_label:
            self._status_warning_label.setText(f"\u26A0 \u8B66\u544A: {count}")

    def _toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
            self._title_bar.set_maximized_state(False)
        else:
            self.showMaximized()
            self._title_bar.set_maximized_state(True)

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == event.WindowStateChange and self._title_bar:
            self._title_bar.set_maximized_state(self.isMaximized())

    def nativeEvent(self, eventType, message):
        if os.name == "nt":
            try:
                from PyQt5.QtCore import QByteArray
                result = super().nativeEvent(eventType, message)
                return result
            except Exception:
                return super().nativeEvent(eventType, message)
        return super().nativeEvent(eventType, message)

    def _connect_events(self):
        self._event_bus.project_created.connect(self._on_project_created)
        self._event_bus.project_opened.connect(self._on_project_opened)
        self._event_bus.document_open_request.connect(self._on_document_open)
        self._event_bus.spec_check_request.connect(self._on_spec_check_request)
        self._event_bus.variable_check_request.connect(self._on_variable_check_request)
        self._event_bus.theme_changed.connect(self._on_theme_changed)
        self._event_bus.settings_changed.connect(self._on_settings_changed)

        self._activity_bar.activity_changed.connect(self._on_activity_changed)
        self._sidebar.navigate_requested.connect(self._on_sidebar_navigate)
        self._tab_system.tab_changed.connect(self._on_tab_changed)
        self._tab_system.tab_closed.connect(self._on_tab_closed)

    def _on_activity_changed(self, activity_id: str):
        self._sidebar.set_activity(activity_id)
        self._sidebar.setVisible(True)
        self._sidebar.set_collapsed(False)

        tab_map = {
            "dashboard": "dashboard",
            "project": "project",
            "document": "document",
            "change": "change",
            "plc-tools": "plc-tools",
            "spec": "spec",
            "settings": "settings",
        }
        tab_id = tab_map.get(activity_id, activity_id)

        if not self._tab_system.tab_exists(tab_id):
            widget = self._create_tab_widget(tab_id)
            if widget is None:
                return
            titles = {
                "dashboard": "\U0001F4CA \u4EEA\u8868\u76D8",
                "project": "\U0001F4C1 \u9879\u76EE\u8BE6\u60C5",
                "document": "\U0001F4DD \u6587\u6863\u7F16\u8F91",
                "change": "\U0001F504 \u53D8\u66F4\u7BA1\u7406",
                "plc-tools": "\u26A1 PLC\u5DE5\u5177",
                "spec": "\u2705 \u89C4\u8303\u4E2D\u5FC3",
                "settings": "\u2699 \u8BBE\u7F6E",
            }
            title = titles.get(tab_id, tab_id)
            self._tab_system.open_tab(tab_id, title, "", widget)
        else:
            self._tab_system.switch_to_tab(tab_id)

    def _on_sidebar_navigate(self, tab_id: str, context: dict):
        action_map = {
            "new_project": self._handle_new_project,
            "open_project": self._handle_open_project,
            "spec_check": lambda: self._on_activity_changed("spec"),
            "version_sync": lambda: self._on_sync_action("version_check"),
            "st_editor": lambda: self._on_activity_changed("plc-tools"),
            "doc_editor": lambda: self._on_activity_changed("document"),
            "change_list": lambda: self._on_activity_changed("change"),
            "auto_fix": self._handle_auto_fix_navigate,
            "excel_export": self._handle_excel_export_navigate,
            "new_document": self._handle_new_document,
            "dashboard": lambda: self._on_activity_changed("dashboard"),
            "project_detail": lambda: self._on_activity_changed("project"),
            "version_sync_check": lambda: self._on_sync_action("version_check"),
            "generate_chg": lambda: self._on_sync_action("generate_chg"),
            "generate_ifc": lambda: self._on_sync_action("generate_ifc"),
            "variable_checker": lambda: self._on_activity_changed("plc-tools"),
            "select_checker": lambda: self._on_activity_changed("spec"),
        }

        handler = action_map.get(tab_id)
        if handler:
            handler()

    def _handle_new_project(self):
        if self._menu_manager:
            self._menu_manager._on_new_project()

    def _handle_open_project(self):
        if self._menu_manager:
            self._menu_manager._on_open_project()

    def _handle_new_document(self):
        if self._menu_manager and hasattr(self._menu_manager, '_on_new_document'):
            self._menu_manager._on_new_document()
        else:
            self._on_activity_changed("document")

    def _handle_auto_fix_navigate(self):
        if not self._tab_system.tab_exists("auto_fix"):
            widget = self._create_tab_widget("auto_fix")
            if widget:
                self._tab_system.open_tab("auto_fix", "\U0001F527 \u81EA\u52A8\u4FEE\u590D", "", widget)
        else:
            self._tab_system.switch_to_tab("auto_fix")

    def _handle_excel_export_navigate(self):
        if not self._tab_system.tab_exists("excel_export"):
            widget = self._create_tab_widget("excel_export")
            if widget:
                self._tab_system.open_tab("excel_export", "\U0001F4CA Excel\u5BFC\u51FA", "", widget)
        else:
            self._tab_system.switch_to_tab("excel_export")

    def _on_sync_action(self, action_key: str):
        if action_key == "version_check":
            self._sync_ctrl.on_sync_version_check()
        elif action_key == "generate_chg":
            self._sync_ctrl.on_sync_generate_chg()
        elif action_key == "generate_ifc":
            self._sync_ctrl.on_sync_generate_ifc()

    def _on_tab_changed(self, new_id: str, old_id: str):
        activity_id = new_id
        if new_id in ("auto_fix", "excel_export"):
            activity_id = "spec"
        if new_id == "project":
            activity_id = "project"
        self._sidebar.set_active_item(activity_id)

    def _on_tab_closed(self, tab_id: str):
        if tab_id == "auto_fix" and self._auto_fix_panel:
            self._auto_fix_panel = None
        elif tab_id == "excel_export" and self._excel_export_panel:
            self._excel_export_panel = None

    def _create_tab_widget(self, tab_id: str):
        if tab_id == "dashboard":
            return self._dashboard_page
        elif tab_id == "project":
            return self._create_project_tab()
        elif tab_id == "document":
            return self._create_document_tab()
        elif tab_id == "change":
            return self._create_change_mgmt_tab()
        elif tab_id == "plc-tools":
            return self._create_plc_tools_tab()
        elif tab_id == "spec":
            return self._create_spec_tab()
        elif tab_id == "settings":
            return self._create_settings_tab()
        elif tab_id == "auto_fix":
            return self._create_auto_fix_tab()
        elif tab_id == "excel_export":
            return self._create_excel_export_tab()
        else:
            placeholder = QLabel(f"\U0001F6E0\uFE0F {tab_id} \u529F\u80FD\u5F00\u53D1\u4E2D...")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setProperty("emptyState", True)
            return placeholder

    def _create_project_tab(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        splitter = QSplitter(Qt.Horizontal)

        try:
            from src.ui.widgets.project_tree import ProjectTreeWidget
            self._project_tree_widget = ProjectTreeWidget()
            self._project_tree_widget.setFixedWidth(280)
            self._project_tree_widget.setMinimumWidth(210)
            splitter.addWidget(self._project_tree_widget)
        except ImportError as e:
            logger.warning(f"ProjectTreeWidget加载失败: {e}")
            fallback = QLabel("\U0001F4C1 \u9879\u76EE\u6D4F\u89C8\u5668\u52A0\u8F7D\u5931\u8D25")
            fallback.setAlignment(Qt.AlignCenter)
            fallback.setFixedWidth(280)
            splitter.addWidget(fallback)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(20, 16, 20, 16)
        right_layout.setSpacing(0)

        header_frame = QFrame()
        header_frame.setFixedHeight(60)
        header_frame.setProperty("ProjectHeader", True)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(12, 8, 12, 8)
        header_layout.setSpacing(4)

        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        icon_label = QLabel("\U0001F4C1")
        icon_label.setStyleSheet("font-size: 28px;")
        title_row.addWidget(icon_label)

        self._lbl_project_title = QLabel("-")
        title_font = QFont("Microsoft YaHei UI", 16, QFont.DemiBold)
        self._lbl_project_title.setFont(title_font)
        self._lbl_project_title.setStyleSheet("color: #E0E0E0;")
        title_row.addWidget(self._lbl_project_title)
        title_row.addStretch()
        header_layout.addLayout(title_row)

        meta_row = QHBoxLayout()
        meta_row.setSpacing(16)
        self._lbl_meta_type = QLabel("-")
        self._lbl_meta_type.setStyleSheet("font-size: 11px; color: #6A6A6A;")
        meta_row.addWidget(self._lbl_meta_type)

        sep1 = QLabel("|")
        sep1.setStyleSheet("font-size: 11px; color: #6A6A6A;")
        meta_row.addWidget(sep1)

        self._lbl_meta_version = QLabel("-")
        self._lbl_meta_version.setStyleSheet("font-size: 11px; color: #6A6A6A;")
        meta_row.addWidget(self._lbl_meta_version)

        sep2 = QLabel("|")
        sep2.setStyleSheet("font-size: 11px; color: #6A6A6A;")
        meta_row.addWidget(sep2)

        self._lbl_meta_status = QLabel("-")
        self._lbl_meta_status.setStyleSheet("font-size: 11px; color: #6A6A6A;")
        meta_row.addWidget(self._lbl_meta_status)
        meta_row.addStretch()
        header_layout.addLayout(meta_row)

        right_layout.addWidget(header_frame)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #3E3E42; max-height: 1px;")
        right_layout.addWidget(line)

        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 16, 0, 16)
        form_layout.setSpacing(12)

        row_id = QHBoxLayout()
        row_id.setSpacing(8)
        lbl_id = QLabel("\u9879\u76EE\u7F16\u53F7:")
        lbl_id.setProperty("FormLabel", "true")
        lbl_id.setFixedWidth(80)
        row_id.addWidget(lbl_id)
        self._edit_project_id = QLineEdit()
        self._edit_project_id.setReadOnly(True)
        self._edit_project_id.setStyleSheet(
            "background-color: #2D2D30; border-radius: 2px; padding: 6px 10px;"
        )
        row_id.addWidget(self._edit_project_id)
        form_layout.addLayout(row_id)

        row_type = QHBoxLayout()
        row_type.setSpacing(8)
        lbl_type = QLabel("\u9879\u76EE\u7C7B\u578B:")
        lbl_type.setProperty("FormLabel", "true")
        lbl_type.setFixedWidth(80)
        row_type.addWidget(lbl_type)
        self._combo_project_type = QComboBox()
        self._combo_project_type.addItems(["DJ", "SW", "\u901A\u7528"])
        self._combo_project_type.setStyleSheet("border-radius: 2px; padding: 6px 10px;")
        row_type.addWidget(self._combo_project_type)
        form_layout.addLayout(row_type)

        row_name = QHBoxLayout()
        row_name.setSpacing(8)
        lbl_name = QLabel("\u9879\u76EE\u540D\u79F0:")
        lbl_name.setProperty("FormLabel", "true")
        lbl_name.setFixedWidth(80)
        row_name.addWidget(lbl_name)
        self._edit_project_name = QLineEdit()
        self._edit_project_name.setPlaceholderText("\u8F93\u5165\u9879\u76EE\u540D\u79F0...")
        self._edit_project_name.setStyleSheet("border-radius: 2px; padding: 6px 10px;")
        row_name.addWidget(self._edit_project_name)
        form_layout.addLayout(row_name)

        row_version = QHBoxLayout()
        row_version.setSpacing(8)
        lbl_version = QLabel("\u7248\u672C:")
        lbl_version.setProperty("FormLabel", "true")
        lbl_version.setFixedWidth(80)
        row_version.addWidget(lbl_version)
        self._edit_project_version = QLineEdit()
        self._edit_project_version.setPlaceholderText("V1.0.0")
        self._edit_project_version.setStyleSheet("border-radius: 2px; padding: 6px 10px;")
        row_version.addWidget(self._edit_project_version)
        form_layout.addLayout(row_version)

        row_path = QHBoxLayout()
        row_path.setSpacing(8)
        lbl_path = QLabel("\u9879\u76EE\u8DEF\u5F84:")
        lbl_path.setProperty("FormLabel", "true")
        lbl_path.setFixedWidth(80)
        row_path.addWidget(lbl_path)
        self._edit_project_path = QLineEdit()
        self._edit_project_path.setReadOnly(True)
        self._edit_project_path.setStyleSheet(
            "background-color: #2D2D30; border-radius: 2px; padding: 6px 10px;"
        )
        row_path.addWidget(self._edit_project_path)
        browse_btn = QPushButton("\u6D4F\u89C8...")
        browse_btn.setFixedWidth(70)
        browse_btn.setProperty("SecondaryBtn", "true")
        browse_btn.clicked.connect(self._on_browse_project_path)
        row_path.addWidget(browse_btn)
        form_layout.addLayout(row_path)

        row_desc = QHBoxLayout()
        row_desc.setSpacing(8)
        lbl_desc = QLabel("\u63CF\u8FF0:")
        lbl_desc.setProperty("FormLabel", "true")
        lbl_desc.setFixedWidth(80)
        lbl_desc.setAlignment(Qt.AlignTop)
        row_desc.addWidget(lbl_desc)
        self._edit_project_desc = QTextEdit()
        self._edit_project_desc.setFixedHeight(72)
        self._edit_project_desc.setPlaceholderText("\u8F93\u5165\u9879\u76EE\u63CF\u8FF0...")
        self._edit_project_desc.setStyleSheet("border-radius: 2px; padding: 6px 10px;")
        row_desc.addWidget(self._edit_project_desc)
        form_layout.addLayout(row_desc)

        right_layout.addWidget(form_container)

        right_layout.addStretch()

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        save_btn = QPushButton("\uD83D\uDCE6 \u4FDD\u5B58")
        save_btn.setProperty("PrimaryBtn", "true")
        save_btn.clicked.connect(self._on_save_project_detail)
        btn_row.addWidget(save_btn)

        refresh_btn = QPushButton("\uD83D\uDD04 \u5237\u65B0")
        refresh_btn.setProperty("SecondaryBtn", "true")
        refresh_btn.clicked.connect(self._on_refresh_project_detail)
        btn_row.addWidget(refresh_btn)

        close_btn = QPushButton("\u5173\u95ED\u9879\u76EE")
        close_btn.setProperty("DangerBtn", "true")
        close_btn.clicked.connect(self._on_close_current_project)
        btn_row.addWidget(close_btn)

        right_layout.addLayout(btn_row)

        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)

        self._project_info_labels = {
            "name": self._edit_project_name,
            "id": self._edit_project_id,
            "type": self._combo_project_type,
            "version": self._edit_project_version,
            "path": self._edit_project_path,
            "desc": self._edit_project_desc,
            "title": self._lbl_project_title,
            "meta_type": self._lbl_meta_type,
            "meta_version": self._lbl_meta_version,
            "meta_status": self._lbl_meta_status,
        }
        self._project_info_widget = right_widget

        return container

    def _on_browse_project_path(self):
        path = QFileDialog.getExistingDirectory(self, "\u9009\u62E9\u9879\u76EE\u8DEF\u5F84")
        if path:
            self._edit_project_path.setText(path)

    def _on_save_project_detail(self):
        try:
            project = getattr(self._project_ctrl, '_current_project', None)
            if not project:
                self.statusBar().showMessage("\u26A0\uFE0F \u6CA1\u6709\u6253\u5F00\u7684\u9879\u76EE", 3000)
                return
            if hasattr(project, 'name'):
                project.name = self._edit_project_name.text().strip()
            if hasattr(project, 'project_type'):
                project.project_type = self._combo_project_type.currentText()
            if hasattr(project, 'version'):
                project.version = self._edit_project_version.text().strip()
            if hasattr(project, 'description'):
                project.description = self._edit_project_desc.toPlainText().strip()
            if hasattr(project, 'save'):
                project.save()
            self.statusBar().showMessage("\u2705 \u9879\u76EE\u4FE1\u606F\u5DF2\u4FDD\u5B58", 3000)
        except Exception as e:
            logger.exception(f"\u4FDD\u5B58\u9879\u76EE\u8BE6\u60C5\u5931\u8D25: {e}")
            QMessageBox.warning(self, "\u4FDD\u5B58\u5931\u8D25", f"\u65E0\u6CD5\u4FDD\u5B58\u9879\u76EE\u4FE1\u606F:\n{e}")

    def _on_refresh_project_detail(self):
        try:
            project = getattr(self._project_ctrl, '_current_project', None)
            if not project:
                return
            if hasattr(project, 'name') and self._edit_project_name:
                self._edit_project_name.setText(getattr(project, 'name', ''))
            if hasattr(project, 'project_id') and self._edit_project_id:
                self._edit_project_id.setText(getattr(project, 'project_id', ''))
            if hasattr(project, 'project_type') and self._combo_project_type:
                idx = self._combo_project_type.findText(getattr(project, 'project_type', 'DJ'))
                if idx >= 0:
                    self._combo_project_type.setCurrentIndex(idx)
            if hasattr(project, 'version') and self._edit_project_version:
                self._edit_project_version.setText(getattr(project, 'version', 'V1.0.0'))
            if hasattr(project, 'path') and self._edit_project_path:
                self._edit_project_path.setText(getattr(project, 'path', ''))
            if hasattr(project, 'description') and self._edit_project_desc:
                self._edit_project_desc.setPlainText(getattr(project, 'description', ''))
            self._update_project_header(project)
            self.statusBar().showMessage("\uD83D\uDD04 \u9879\u76EE\u4FE1\u606F\u5DF2\u5237\u65B0", 2000)
        except Exception as e:
            logger.warning(f"\u5237\u65B0\u9879\u76EE\u8BE6\u60C5\u5931\u8D25: {e}")

    def _on_close_current_project(self):
        reply = QMessageBox.question(
            self, "\u5173\u95ED\u9879\u76EE",
            "\u786E\u5B9A\u8981\u5173\u95ED\u5F53\u524D\u9879\u76EE\u5417\uff1F",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            if hasattr(self._project_ctrl, 'close_project'):
                self._project_ctrl.close_project()
            self._clear_project_form()

    def _update_project_header(self, project):
        if not project:
            return
        name = getattr(project, 'name', '-')
        pid = getattr(project, 'project_id', '-')
        display_name = f"{pid} {name}" if pid != '-' else name
        if self._lbl_project_title:
            self._lbl_project_title.setText(display_name)
        ptype = getattr(project, 'project_type', '-')
        version = getattr(project, 'version', '-')
        status = getattr(project, 'status', '\u672A\u77E5')
        type_map = {"DJ": "PLC\u9879\u76EE", "SW": "\u8F6F\u4EF6\u9879\u76EE", "\u901A\u7528": "\u901A\u7528\u9879\u76EE"}
        if self._lbl_meta_type:
            self._lbl_meta_type.setText(type_map.get(ptype, ptype))
        if self._lbl_meta_version:
            self._lbl_meta_version.setText(version)
        if self._lbl_meta_status:
            self._lbl_meta_status.setText(status)

    def _clear_project_form(self):
        for widget in [
            self._edit_project_name, self._edit_project_id,
            self._edit_project_version, self._edit_project_path,
            self._edit_project_desc,
        ]:
            if widget:
                if isinstance(widget, QTextEdit):
                    widget.clear()
                else:
                    widget.setText("")
        if self._lbl_project_title:
            self._lbl_project_title.setText("-")
        for lbl in [self._lbl_meta_type, self._lbl_meta_version, self._lbl_meta_status]:
            if lbl:
                lbl.setText("-")

    def _create_document_tab(self):
        try:
            from src.ui.widgets.document_editor import DocumentEditor
            self._document_editor = DocumentEditor()
            return self._document_editor
        except ImportError as e:
            logger.warning(f"DocumentEditor加载失败: {e}")
            return self._create_fallback_widget("\u6587\u6863\u7F16\u8F91\u5668\u52A0\u8F7D\u5931\u8D25")

    def _create_change_mgmt_tab(self):
        try:
            from src.ui.widgets.change_management_panel import ChangeManagementPanel
            self._change_mgmt_panel = ChangeManagementPanel()
            return self._change_mgmt_panel
        except ImportError as e:
            logger.warning(f"ChangeManagementPanel加载失败: {e}")
            return self._create_fallback_widget("\u53D8\u66F4\u7BA1\u7406\u9762\u677F\u52A0\u8F7D\u5931\u8D25")

    def _create_plc_tools_tab(self):
        from PyQt5.QtWidgets import QTabWidget as InnerTabWidget

        container = InnerTabWidget()
        container.setTabPosition(InnerTabWidget.North)
        container.setDocumentMode(True)

        try:
            from src.ui.widgets.st_editor import STEditor
            self._st_editor = STEditor(show_dependency_notice=True)
        except ImportError as e:
            logger.warning(f"STEditor加载失败: {e}")
            self._st_editor = self._create_fallback_widget("ST\u7F16\u8F91\u5668\u52A0\u8F7D\u5931\u8D25")
        container.addTab(self._st_editor, "ST\u7F16\u8F91\u5668")

        self._plc_tools_tabs = container
        return container

    def _create_spec_tab(self):
        try:
            from src.ui.widgets.spec_check_panel import SpecCheckPanel
            self._spec_check_tab_panel = SpecCheckPanel()
            self._spec_check_tab_panel.source_jump_requested.connect(self._jump_to_source)
            return self._spec_check_tab_panel
        except ImportError as e:
            logger.warning(f"SpecCheckPanel加载失败: {e}")
            return self._create_fallback_widget("\u89C4\u8303\u68C0\u67E5\u9762\u677F\u52A0\u8F7D\u5931\u8D25")

    def _create_auto_fix_tab(self):
        try:
            from src.ui.widgets.auto_fix_panel import AutoFixPanel
            self._auto_fix_panel = AutoFixPanel()
            self._auto_fix_panel.source_jump_requested.connect(self._jump_to_source)
            return self._auto_fix_panel
        except ImportError as e:
            logger.warning(f"AutoFixPanel加载失败: {e}")
            return self._create_fallback_widget("\u81EA\u52A8\u4FEE\u590D\u9762\u677F\u52A0\u8F7D\u5931\u8D25")

    def _create_excel_export_tab(self):
        try:
            from src.ui.widgets.excel_export_panel import ExcelExportPanel
            self._excel_export_panel = ExcelExportPanel()
            self._excel_export_panel.file_open_requested.connect(self._on_excel_file_open)
            return self._excel_export_panel
        except ImportError as e:
            logger.warning(f"ExcelExportPanel加载失败: {e}")
            return self._create_fallback_widget("Excel\u5BFC\u51FA\u9762\u677F\u52A0\u8F7D\u5931\u8D25")

    def _create_settings_tab(self):
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        center_widget = QWidget()
        center_widget.setMaximumWidth(720)
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(24, 24, 24, 24)
        center_layout.setSpacing(20)

        center_layout.addStretch()

        general_group, general_layout = self._create_settings_group("\u5E38\u89C4\u8BBE\u7F6E", "\uD83D\uDDA5")
        self._edit_default_path = QLineEdit()
        self._edit_default_path.setFixedWidth(280)
        self._edit_default_path.setText(SettingsManager.get("default_project_path", ""))
        browse_btn = QPushButton("\u6D4F\u89C8...")
        browse_btn.setFixedWidth(60)
        browse_btn.setProperty("settingsBrowseButton", True)
        browse_btn.clicked.connect(self._on_browse_default_path)
        path_row = QHBoxLayout()
        path_row.setSpacing(8)
        path_row.addWidget(self._edit_default_path)
        path_row.addWidget(browse_btn)
        general_layout.addLayout(path_row)

        self._chk_auto_save = QCheckBox("\u81EA\u52A8\u4FDD\u5B58")
        self._chk_auto_save.setChecked(SettingsManager.get("auto_backup", True))
        general_layout.addWidget(self._chk_auto_save)

        log_level_row = self._create_form_row("\u65E5\u5FD7\u7EA7\u522B", QComboBox())
        self._combo_log_level = log_level_row.itemAt(1).widget()
        self._combo_log_level.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        current_log = SettingsManager.get("log_level", "INFO")
        idx = self._combo_log_level.findText(current_log)
        if idx >= 0:
            self._combo_log_level.setCurrentIndex(idx)
        general_layout.addLayout(log_level_row)
        center_layout.addWidget(general_group)

        editor_group, editor_layout = self._create_settings_group("\u7F16\u8F91\u5668", "\uD83D\uDCDD")
        font_row = self._create_form_row("\u5B57\u4F53", QComboBox())
        self._combo_font_family = font_row.itemAt(1).widget()
        self._combo_font_family.addItems(["Microsoft YaHei UI", "Consolas", "Cascadia Code", "Source Code Pro"])
        current_font = SettingsManager.get("editor_font_family", "Consolas")
        idx = self._combo_font_family.findText(current_font)
        if idx >= 0:
            self._combo_font_family.setCurrentIndex(idx)
        editor_layout.addLayout(font_row)

        size_row = self._create_form_row("\u5B57\u53F7", QSpinBox())
        self._spin_font_size = size_row.itemAt(1).widget()
        self._spin_font_size.setFixedWidth(80)
        self._spin_font_size.setRange(8, 24)
        self._spin_font_size.setValue(SettingsManager.get("editor_font_size", 13))
        editor_layout.addLayout(size_row)

        tab_row = self._create_form_row("\u5236\u8868\u7B26\u5BBD\u5EA6", QSpinBox())
        self._spin_tab_width = tab_row.itemAt(1).widget()
        self._spin_tab_width.setFixedWidth(80)
        self._spin_tab_width.setRange(2, 8)
        self._spin_tab_width.setValue(SettingsManager.get("editor_tab_width", 4))
        editor_layout.addLayout(tab_row)
        center_layout.addWidget(editor_group)

        appearance_group, appearance_layout = self._create_settings_group("\u5916\u89C2", "\uD83C\uDFA8")
        theme_row = self._create_form_row("\u4E3B\u9898", QComboBox())
        self._combo_theme = theme_row.itemAt(1).widget()
        self._combo_theme.addItem("\u6DF1\u8272\u5DE5\u4E1A\u98CE", "ide_dark")
        self._combo_theme.addItem("\u6D45\u8272\u4E13\u4E1A\u98CE", "light")
        current_theme = SettingsManager.get("theme", "ide_dark")
        for i in range(self._combo_theme.count()):
            if self._combo_theme.itemData(i) == current_theme:
                self._combo_theme.setCurrentIndex(i)
                break
        appearance_layout.addLayout(theme_row)

        density_row = self._create_form_row("UI\u5BC6\u5EA6", QComboBox())
        self._combo_ui_density = density_row.itemAt(1).widget()
        self._combo_ui_density.addItems(["\u7D27\u51D1", "\u6807\u51C6", "\u8212\u9002", "\u5DE5\u63A7\u673A\u6A21\u5F0F"])
        current_density = SettingsManager.get("ui_density", "standard")
        density_map = {"compact": 0, "standard": 1, "comfortable": 2, "target_machine": 3}
        idx = density_map.get(current_density, 1)
        self._combo_ui_density.setCurrentIndex(idx)
        appearance_layout.addLayout(density_row)
        center_layout.addWidget(appearance_group)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        reset_btn = QPushButton("\u6062\u590D\u9ED8\u8BA4")
        reset_btn.setProperty("settingsSecondaryButton", True)
        reset_btn.clicked.connect(self._on_reset_settings)
        save_btn = QPushButton("\uD83D\uDCE6\u4FDD\u5B58\u8BBE\u7F6E")
        save_btn.setProperty("settingsPrimaryButton", True)
        save_btn.clicked.connect(self._on_save_settings)
        btn_row.addWidget(reset_btn)
        btn_row.addWidget(save_btn)
        center_layout.addLayout(btn_row)

        center_layout.addStretch()

        main_layout.addWidget(center_widget, 0, Qt.AlignCenter)
        return container

    def _create_settings_group(self, title, icon):
        group = QFrame()
        group.setProperty("IndustrialGroup", "true")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(16, 20, 16, 16)
        layout.setSpacing(12)
        header = QLabel(f"{icon} {title}")
        header.setProperty("SettingsGroupTitle", "true")
        layout.addWidget(header)
        return group, layout

    def _create_form_row(self, label_text, widget):
        row = QHBoxLayout()
        row.setSpacing(8)
        lbl = QLabel(label_text)
        lbl.setFixedWidth(100)
        lbl.setProperty("FormLabel", "true")
        row.addWidget(lbl)
        row.addWidget(widget)
        row.addStretch()
        return row

    def _on_browse_default_path(self):
        path = QFileDialog.getExistingDirectory(self, "\u9009\u62E9\u9ED8\u8BA4\u9879\u76EE\u8DEF\u5F84")
        if path:
            self._edit_default_path.setText(path)

    def _on_save_settings(self):
        SettingsManager.set("default_project_path", self._edit_default_path.text().strip())
        SettingsManager.set("auto_backup", self._chk_auto_save.isChecked())
        SettingsManager.set("log_level", self._combo_log_level.currentText())
        SettingsManager.set("editor_font_family", self._combo_font_family.currentText())
        SettingsManager.set("editor_font_size", self._spin_font_size.value())
        SettingsManager.set("editor_tab_width", self._spin_tab_width.value())
        theme_value = self._combo_theme.currentData()
        SettingsManager.set("theme", theme_value)
        density_map = {0: "compact", 1: "standard", 2: "comfortable", 3: "target_machine"}
        SettingsManager.set("ui_density", density_map.get(self._combo_ui_density.currentIndex(), "standard"))
        SettingsManager.save()
        self._event_bus.theme_changed.emit(theme_value)
        self.statusBar().showMessage("\u2705 \u8BBE\u7F6E\u5DF2\u4FDD\u5B58", 3000)

    def _on_reset_settings(self):
        reply = QMessageBox.question(
            self, "\u786E\u8BA4\u91CD\u7F6E",
            "\u786E\u5B9A\u8981\u6062\u590D\u6240\u6709\u8BBE\u7F6E\u4E3A\u9ED8\u8BA4\u503C\u5417\uff1F",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            SettingsManager.reset_to_defaults()
            self._reload_settings_ui()
            self.statusBar().showMessage("\u2705 \u5DF2\u6062\u590D\u9ED8\u8BA4\u8BBE\u7F6E", 3000)

    def _reload_settings_ui(self):
        self._edit_default_path.setText(SettingsManager.get("default_project_path", ""))
        self._chk_auto_save.setChecked(SettingsManager.get("auto_backup", True))
        log_idx = self._combo_log_level.findText(SettingsManager.get("log_level", "INFO"))
        if log_idx >= 0:
            self._combo_log_level.setCurrentIndex(log_idx)
        font_idx = self._combo_font_family.findText(SettingsManager.get("editor_font_family", "Consolas"))
        if font_idx >= 0:
            self._combo_font_family.setCurrentIndex(font_idx)
        self._spin_font_size.setValue(SettingsManager.get("editor_font_size", 13))
        self._spin_tab_width.setValue(SettingsManager.get("editor_tab_width", 4))
        current_theme = SettingsManager.get("theme", "ide_dark")
        for i in range(self._combo_theme.count()):
            if self._combo_theme.itemData(i) == current_theme:
                self._combo_theme.setCurrentIndex(i)
                break
        density_map = {"compact": 0, "standard": 1, "comfortable": 2, "target_machine": 3}
        density_idx = density_map.get(SettingsManager.get("ui_density", "standard"), 1)
        self._combo_ui_density.setCurrentIndex(density_idx)

    def _create_fallback_widget(self, message: str):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addStretch()
        label = QLabel(f"\u26A0\uFE0F {message}")
        label.setAlignment(Qt.AlignCenter)
        label.setProperty("emptyState", True)
        layout.addWidget(label)
        layout.addStretch()
        return widget

    def _navigate_to_tab(self, tab_index: int):
        activity_id = self._TAB_INDEX_TO_ACTIVITY.get(tab_index)
        if activity_id:
            self._on_activity_changed(activity_id)

    def _jump_to_source(self, file_path: str, line_number: int):
        try:
            logger.info(f"收到跳转请求: {file_path}:{line_number}")
            from src.services.companion_service import CompanionService

            success, error = CompanionService.jump_to_file(file_path, line_number)
            if success:
                self.statusBar().showMessage(
                    f"\U0001F517 已跳转: {Path(file_path).name}:{line_number or '*'}", 5000
                )
            else:
                logger.warning(f"跳转失败: {error}")
                self._navigate_to_tab(self.TAB_PLC_TOOLS)
                if self._plc_tools_tabs and self._st_editor:
                    self._plc_tools_tabs.setCurrentWidget(self._st_editor)
                    if hasattr(self._st_editor, 'open_file'):
                        self._st_editor.open_file(file_path, line_number)
                    elif hasattr(self._st_editor, 'load_file'):
                        self._st_editor.load_file(file_path)
                        if hasattr(self._st_editor, 'goto_line'):
                            self._st_editor.goto_line(line_number)
                self.statusBar().showMessage(
                    f"\U0001F517 降级内嵌编辑器: {Path(file_path).name}:{line_number}", 5000
                )
        except Exception as e:
            logger.exception(f"跳转到源码位置失败: {e}")

    def _on_excel_file_open(self, file_path: str):
        try:
            from src.services.companion_service import CompanionService
            success, error = CompanionService.jump_to_file(file_path)
            if success:
                self.statusBar().showMessage(
                    f"\U0001F4C1 已打开文件: {Path(file_path).name}", 5000
                )
            else:
                logger.error(f"打开文件失败: {error}")
        except Exception as e:
            logger.error(f"打开文件失败: {e}")

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
        if self._auto_fix_panel and hasattr(self._auto_fix_panel, 'set_project_path'):
            self._auto_fix_panel.set_project_path(path)
        if self._excel_export_panel and hasattr(self._excel_export_panel, 'set_project_path'):
            self._excel_export_panel.set_project_path(path)

    def _on_project_opened(self, path: str):
        self._project_ctrl.on_project_opened(path)
        if self._change_mgmt_panel:
            self._change_mgmt_panel.set_project_path(path)
        if self._auto_fix_panel and hasattr(self._auto_fix_panel, 'set_project_path'):
            self._auto_fix_panel.set_project_path(path)
        if self._excel_export_panel and hasattr(self._excel_export_panel, 'set_project_path'):
            self._excel_export_panel.set_project_path(path)
        project = getattr(self._project_ctrl, '_current_project', None)
        if project and hasattr(project, 'project_id'):
            self.update_status_project(project.project_id)

    def _on_document_open(self, path: str):
        logger.info(f"收到文档打开请求: {path}")

    def _on_spec_check_request(self, config: dict):
        self._bottom_panel.expand()
        self._bottom_panel.switch_tab("problems")
        self.statusBar().showMessage(
            "\U0001F50D 规范检查结果已输出到底部面板", 5000
        )

    def _on_variable_check_request(self):
        self._navigate_to_tab(self.TAB_PLC_TOOLS)
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
            self._spec_check_tab_panel,
            self._change_mgmt_panel,
            self._auto_fix_panel,
            self._excel_export_panel,
        ]
        for target in cleanup_targets:
            if target and hasattr(target, 'cleanup'):
                try:
                    target.cleanup()
                except Exception:
                    pass