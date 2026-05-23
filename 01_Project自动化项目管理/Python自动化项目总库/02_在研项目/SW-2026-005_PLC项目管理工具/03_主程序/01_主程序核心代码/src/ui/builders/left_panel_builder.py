# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QToolBox,
    QLabel,
    QPushButton,
    QFrame,
)
from PyQt5.QtCore import Qt

from ..widgets.project_tree import ProjectTreeWidget
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
    def build(parent, action_handler) -> QToolBox:
        tool_box = QToolBox(parent)
        tool_box.setMinimumWidth(LeftPanelBuilder.SIDEBAR_MIN_WIDTH)
        tool_box.setMaximumWidth(LeftPanelBuilder.SIDEBAR_MAX_WIDTH)

        project_page = QWidget()
        project_layout = QVBoxLayout(project_page)
        project_layout.setContentsMargins(8, 8, 8, 8)
        project_tree_widget = ProjectTreeWidget()
        project_tree_widget.navigation_requested.connect(
            lambda tab_index, ctx=None: action_handler(tab_index)
        )
        project_layout.addWidget(project_tree_widget)
        tool_box.addItem(project_page, "  \u25B7 项目管理  ")

        tool_box._project_tree_widget = project_tree_widget

        LeftPanelBuilder._create_sidebar_tool_page(
            tool_box,
            "文档管理",
            "\U0001F4DD",
            [
                ("\U0001F4C4 新建文档", LeftPanelBuilder.TAB_DOCUMENT),
                ("\U0001F4C1 模板管理", LeftPanelBuilder.TAB_DOCUMENT),
                ("\U0001F4C2 打开文档", LeftPanelBuilder.TAB_DOCUMENT),
            ],
            action_handler,
        )
        LeftPanelBuilder._create_sidebar_tool_page(
            tool_box,
            "PLC工具",
            "\u26A1",
            [
                ("\U0001F4DD ST代码编辑器", LeftPanelBuilder.TAB_PLC_TOOLS),
                ("\U0001F4CF IO分配表", LeftPanelBuilder.TAB_PLC_TOOLS),
                ("\U0001F9EA 变量检查器", LeftPanelBuilder.TAB_PLC_TOOLS),
            ],
            action_handler,
        )
        LeftPanelBuilder._create_change_mgmt_page(tool_box, action_handler)
        LeftPanelBuilder._create_sidebar_tool_page(
            tool_box,
            "规范中心",
            "\u2705",
            [
                ("\U0001F50D 规范检查", LeftPanelBuilder.TAB_SPEC_CHECK),
                ("\U0001F52C 深度诊断 (F6)", LeftPanelBuilder.TAB_SPEC_CHECK),
                ("\U0001F4CB 生成报告", LeftPanelBuilder.TAB_SPEC_CHECK),
                None,
                ("\U0001F504 版本检查", None),
                ("\U0001F4DD 生成CHG文档", None),
                ("\U0001F4C4 生成IFC文档", None),
            ],
            action_handler,
        )
        LeftPanelBuilder._create_sidebar_tool_page(
            tool_box,
            "系统设置",
            "\u2699\uFE0F",
            [
                ("\u2699\uFE0F 打开设置 (Ctrl+,)", None),
                ("\U0001F3A8 主题切换", None),
                ("\u2139\uFE0F 关于", None),
            ],
            action_handler,
        )

        return tool_box

    @staticmethod
    def _create_sidebar_tool_page(tool_box, title, icon, actions, action_handler):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        header = QLabel(f"{icon} {title}")
        header.setProperty("SidebarHeader", True)
        layout.addWidget(header)

        for action_item in actions:
            if action_item is None:
                separator = QFrame()
                separator.setFrameShape(QFrame.HLine)
                separator.setStyleSheet(
                    "background-color: #E0E0E0; max-height: 1px; margin: 4px 0;"
                )
                layout.addWidget(separator)
                continue

            action_text, target_tab = action_item
            btn = QPushButton(f"  {action_text}")
            btn.setProperty("SidebarBtn", True)
            btn.setCursor(Qt.PointingHandCursor)
            if target_tab is not None:
                btn.clicked.connect(
                    lambda checked, t=target_tab: action_handler(t)
                )
            else:
                btn.clicked.connect(
                    lambda checked, a=action_text: action_handler(a)
                )
            layout.addWidget(btn)

        layout.addStretch()
        tool_box.addItem(page, f"  \u25B7 {title}  ")

    @staticmethod
    def _create_change_mgmt_page(tool_box, action_handler):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        header = QLabel("\U0001F504 变更管理")
        header.setProperty("SidebarHeader", True)
        layout.addWidget(header)

        btn_refresh = QPushButton("  \U0001F504 刷新变更单列表")
        btn_refresh.setProperty("SidebarBtn", True)
        btn_refresh.setCursor(Qt.PointingHandCursor)
        btn_refresh.clicked.connect(
            lambda checked: action_handler(LeftPanelBuilder.TAB_CHANGE_MGMT)
        )
        layout.addWidget(btn_refresh)

        layout.addStretch()
        tool_box.addItem(page, "  \u25B7 变更管理  ")
