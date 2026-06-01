# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QWidget

from ..widgets.industrial_sidebar import IndustrialSidebar
from src.ui.ui_scale import current_ui_profile
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class LeftPanelBuilder:

    SIDEBAR_MIN_WIDTH = 180
    SIDEBAR_MAX_WIDTH = 320

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

    @staticmethod
    def build(parent, action_handler, ui_profile=None) -> IndustrialSidebar:
        profile = ui_profile or current_ui_profile(parent)
        sidebar = IndustrialSidebar(parent, action_handler=action_handler, ui_profile=profile)
        return sidebar
