# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QWidget, QTabWidget

from src.core.settings import SettingsManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class NavigationController:

    TAB_DASHBOARD = 0
    TAB_PROJECT = 1
    TAB_DOCUMENT = 2
    TAB_CHANGE_MGMT = 3
    TAB_PLC_TOOLS = 4
    TAB_SPEC_CHECK = 5

    TOOL_PROJECT = 0
    TOOL_DOCUMENT = 1
    TOOL_CHANGE_MGMT = 2
    TOOL_PLC = 3
    TOOL_SPEC = 4
    TOOL_SETTINGS = 5

    SIDEBAR_TO_TAB = {
        TOOL_PROJECT: TAB_DASHBOARD,
        TOOL_DOCUMENT: TAB_DOCUMENT,
        TOOL_CHANGE_MGMT: TAB_CHANGE_MGMT,
        TOOL_PLC: TAB_PLC_TOOLS,
        TOOL_SPEC: TAB_SPEC_CHECK,
        TOOL_SETTINGS: None,
    }

    TAB_TO_SIDEBAR = {
        TAB_DASHBOARD: TOOL_PROJECT,
        TAB_PROJECT: TOOL_PROJECT,
        TAB_DOCUMENT: TOOL_DOCUMENT,
        TAB_CHANGE_MGMT: TOOL_CHANGE_MGMT,
        TAB_PLC_TOOLS: TOOL_PLC,
        TAB_SPEC_CHECK: TOOL_SPEC,
    }

    SIDEBAR_ACTION_MAP = {
        "open_settings": "settings",
        "toggle_theme": "theme",
        "show_about": "about",
        "version_check": "version_check",
        "generate_chg": "generate_chg",
        "generate_ifc": "generate_ifc",
    }

    def __init__(self, sidebar: QWidget, tab_widget: QTabWidget,
                 menu_manager=None, sync_handler: callable = None,
                 project_info_handler: callable = None):
        self._sidebar = sidebar
        self._tab_widget = tab_widget
        self._menu_manager = menu_manager
        self._sync_handler = sync_handler
        self._project_info_handler = project_info_handler

    def connect(self):
        if self._sidebar and self._tab_widget:
            if hasattr(self._sidebar, 'currentChanged'):
                self._sidebar.currentChanged.connect(self._on_sidebar_changed)
            self._tab_widget.currentChanged.connect(self._on_tab_changed)

    def _on_sidebar_changed(self, sidebar_idx: int):
        tab_idx = self.SIDEBAR_TO_TAB.get(sidebar_idx)
        if tab_idx is not None and self._tab_widget:
            self._tab_widget.blockSignals(True)
            self._tab_widget.setCurrentIndex(tab_idx)
            self._tab_widget.blockSignals(False)

    def _on_tab_changed(self, tab_idx: int):
        sidebar_idx = self.TAB_TO_SIDEBAR.get(tab_idx)
        if sidebar_idx is not None and self._sidebar:
            if hasattr(self._sidebar, 'setCurrentIndex'):
                self._sidebar.blockSignals(True)
                self._sidebar.setCurrentIndex(sidebar_idx)
                self._sidebar.blockSignals(False)

    def navigate_to_tab(self, tab_index: int):
        if self._tab_widget and 0 <= tab_index < self._tab_widget.count():
            self._tab_widget.setCurrentIndex(tab_index)
        sidebar_idx = self.TAB_TO_SIDEBAR.get(tab_index)
        if sidebar_idx is not None and self._sidebar and hasattr(self._sidebar, 'setCurrentIndex'):
            self._sidebar.setCurrentIndex(sidebar_idx)

    def on_sidebar_action(self, action_text: str):
        action_key = None
        for key, keyword in self.SIDEBAR_ACTION_MAP.items():
            if keyword in action_text.lower():
                action_key = key
                break

        if action_key == "open_settings":
            if self._menu_manager:
                self._menu_manager._on_settings()
        elif action_key == "toggle_theme":
            if self._menu_manager:
                current = SettingsManager.get("theme", "light")
                new_theme = "dark" if current == "light" else "light"
                self._menu_manager._switch_theme(new_theme)
        elif action_key == "show_about":
            if self._menu_manager:
                self._menu_manager._on_about()
        elif action_key == "version_check":
            if self._sync_handler:
                self._sync_handler("version_check")
        elif action_key == "generate_chg":
            if self._sync_handler:
                self._sync_handler("generate_chg")
        elif action_key == "generate_ifc":
            if self._sync_handler:
                self._sync_handler("generate_ifc")
        else:
            logger.debug(f"未处理的侧边栏操作: {action_text}")

    def on_project_tree_navigate(self, tab_index: int, context: dict = None):
        self.navigate_to_tab(tab_index)
        if context and tab_index == self.TAB_PROJECT:
            if self._project_info_handler:
                self._project_info_handler(context)
