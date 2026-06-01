# -*- coding: utf-8 -*-
from typing import Dict, List, Optional, Tuple

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtGui import QFont


_SIDEBAR_WIDTH = 260


def _make_item_btn(text: str) -> QPushButton:
    btn = QPushButton(text)
    btn.setProperty("SidebarItem", True)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setCheckable(True)
    return btn


def _make_item_with_badge(text: str, badge_text: str,
                          badge_trae: bool = False,
                          badge_hybrid: bool = False) -> Tuple[QWidget, QPushButton, QLabel]:
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(4)

    btn = _make_item_btn(text)
    layout.addWidget(btn, 1)

    badge = QLabel(badge_text)
    badge.setProperty("Badge", True)
    if badge_trae:
        badge.setProperty("BadgeTrae", True)
    if badge_hybrid:
        badge.setProperty("BadgeHybrid", True)
    layout.addWidget(badge)

    return container, btn, badge


def _make_item_with_dev_badge(text: str) -> Tuple[QWidget, QPushButton]:
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(4)

    btn = _make_item_btn(text)
    layout.addWidget(btn, 1)

    dev_label = QLabel("\u5F00\u53D1\u4E2D")
    dev_label.setProperty("DevBadge", True)
    layout.addWidget(dev_label)

    return container, btn


def _make_separator() -> QFrame:
    sep = QFrame()
    sep.setFrameShape(QFrame.HLine)
    sep.setProperty("SidebarSeparator", True)
    return sep


def _wrap_scroll(content_widget: QWidget) -> QScrollArea:
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    scroll.setFrameShape(QFrame.NoFrame)
    scroll.setWidget(content_widget)
    return scroll


class _SectionWidget(QWidget):

    def __init__(self, title: str, icon: str, expanded: bool = True,
                 badge_text: Optional[str] = None, parent=None):
        super().__init__(parent)
        self._expanded = expanded
        self._title = title
        self._icon = icon
        self._badge_label: Optional[QLabel] = None

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)

        arrow = "\u25BC" if expanded else "\u25B6"
        self._header_btn = QPushButton(f"  {icon}  {title}  {arrow}")
        self._header_btn.setProperty("SidebarSectionHeader", True)
        self._header_btn.setCursor(Qt.PointingHandCursor)
        self._header_btn.setCheckable(True)
        self._header_btn.setChecked(expanded)
        self._header_btn.clicked.connect(self._toggle)
        header_layout.addWidget(self._header_btn, 1)

        if badge_text:
            self._badge_label = QLabel(badge_text)
            self._badge_label.setProperty("Badge", True)
            header_layout.addWidget(self._badge_label)
            header_layout.addSpacing(6)

        root.addWidget(header_container)

        self._content = QWidget()
        self._content.setProperty("SidebarSectionContent", True)
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(0, 4, 0, 4)
        self._content_layout.setSpacing(1)
        self._content.setVisible(expanded)
        root.addWidget(self._content)

    @property
    def badge_label(self) -> Optional[QLabel]:
        return self._badge_label

    @property
    def content_layout(self) -> QVBoxLayout:
        return self._content_layout

    @property
    def expanded(self) -> bool:
        return self._expanded

    def set_expanded(self, expanded: bool) -> None:
        self._expanded = expanded
        arrow = "\u25BC" if expanded else "\u25B6"
        self._header_btn.setText(f"  {self._icon}  {self._title}  {arrow}")
        self._header_btn.setChecked(expanded)
        self._content.setVisible(expanded)

    def _toggle(self, checked: bool) -> None:
        self.set_expanded(checked)

    def add_item(self, widget_or_btn, btn: Optional[QPushButton] = None) -> QPushButton:
        if btn is not None:
            self._content_layout.addWidget(widget_or_btn)
            return btn
        self._content_layout.addWidget(widget_or_btn)
        return widget_or_btn

    def add_widget(self, widget: QWidget) -> None:
        self._content_layout.addWidget(widget)


class ContextSidebar(QWidget):

    sidebar_collapsed = pyqtSignal(bool)
    navigate_requested = pyqtSignal(str, dict)

    ACTIVITIES = [
        "dashboard", "project", "document", "plc-tools", "change", "spec", "settings"
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._activity_id: str = "dashboard"
        self._collapsed: bool = False
        self._templates: Dict[str, QWidget] = {}
        self._all_item_btns: Dict[str, Dict[str, QPushButton]] = {}
        self._active_item_key: Dict[str, Optional[str]] = {}
        self._badge_labels: Dict[str, QLabel] = {}

        self.setObjectName("ContextSidebar")
        self.setMinimumWidth(0)
        self.setMaximumWidth(_SIDEBAR_WIDTH)

        self._setup_ui()
        self.set_activity("dashboard")

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        title_bar = QWidget()
        title_bar.setFixedHeight(36)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(8, 0, 4, 0)
        title_layout.setSpacing(0)

        self._title_label = QLabel("\u5BFC\u822A")
        self._title_label.setProperty("SidebarTitle", True)
        title_layout.addWidget(self._title_label, 1)

        self._collapse_btn = QPushButton("\u25C0")
        self._collapse_btn.setProperty("SidebarCollapseBtn", True)
        self._collapse_btn.setCursor(Qt.PointingHandCursor)
        self._collapse_btn.setFixedSize(28, 28)
        self._collapse_btn.clicked.connect(self.toggle_collapse)
        title_layout.addWidget(self._collapse_btn)

        root.addWidget(title_bar)

        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll_area.setFrameShape(QFrame.NoFrame)
        root.addWidget(self._scroll_area, 1)

    def _on_item_clicked(self, tab_id: str, btn: QPushButton) -> None:
        self.set_active_item(tab_id)
        self.navigate_requested.emit(tab_id, {})

    def _connect_item(self, btn: QPushButton, tab_id: str) -> None:
        btn.clicked.connect(lambda checked, tid=tab_id, b=btn: self._on_item_clicked(tid, b))

    def _set_item_active(self, btn: QPushButton, active: bool) -> None:
        btn.setChecked(active)
        if active:
            btn.setProperty("Active", True)
        else:
            btn.setProperty("Active", False)
        btn.style().unpolish(btn)
        btn.style().polish(btn)

    def _store_activity_items(self, activity_id: str, items: Dict[str, QPushButton]) -> None:
        self._all_item_btns[activity_id] = items
        self._active_item_key[activity_id] = None

    def _build_dashboard_content(self) -> QWidget:
        activity_id = "dashboard"
        items: Dict[str, QPushButton] = {}
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        section1 = _SectionWidget("\u9879\u76EE\u7BA1\u7406", "\U0001F4CA", expanded=True)
        btn1 = _make_item_btn("  \U0001F4CA\u9879\u76EE\u4EEA\u8868\u76D8")
        self._set_item_active(btn1, True)
        self._connect_item(btn1, "dashboard")
        items["dashboard"] = btn1
        section1.add_item(btn1)

        btn2 = _make_item_btn("  \U0001F4CB\u9879\u76EE\u8BE6\u60C5")
        self._connect_item(btn2, "project_detail")
        items["project_detail"] = btn2
        section1.add_item(btn2)

        btn3 = _make_item_btn("  \U0001F4C2\u6253\u5F00\u9879\u76EE")
        self._connect_item(btn3, "open_project")
        items["open_project"] = btn3
        section1.add_item(btn3)
        layout.addWidget(section1)

        section2 = _SectionWidget("\u5FEB\u901F\u64CD\u4F5C", "\u26A1", expanded=True)
        btn4 = _make_item_btn("  \U0001F4DD\u65B0\u5EFA\u6587\u6863")
        self._connect_item(btn4, "new_document")
        items["new_document"] = btn4
        section2.add_item(btn4)

        btn5 = _make_item_btn("  \U0001F50D\u8FD0\u884C\u89C4\u8303\u68C0\u67E5")
        self._connect_item(btn5, "spec_check")
        items["spec_check"] = btn5
        section2.add_item(btn5)

        btn6 = _make_item_btn("  \U0001F504\u7248\u672C\u540C\u6B65\u68C0\u67E5")
        self._connect_item(btn6, "version_sync")
        items["version_sync"] = btn6
        section2.add_item(btn6)
        layout.addWidget(section2)

        layout.addStretch()
        self._store_activity_items(activity_id, items)
        self._active_item_key[activity_id] = "dashboard"
        return container

    def _build_project_content(self) -> QWidget:
        activity_id = "project"
        items: Dict[str, QPushButton] = {}
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        section = _SectionWidget("\u9879\u76EE\u6D4F\u89C8", "\U0001F333", expanded=True)

        ws_container, ws_btn, ws_badge = _make_item_with_badge(
            "  \U0001F333\u5DE5\u4F5C\u7A7A\u95F4", "3")
        self._connect_item(ws_btn, "workspace")
        items["workspace"] = ws_btn
        self._badge_labels["project_workspace"] = ws_badge
        section.add_item(ws_container, ws_btn)

        btn1 = _make_item_btn("    \U0001F4CB DJ-2026-005")
        self._set_item_active(btn1, True)
        self._connect_item(btn1, "DJ-2026-005")
        items["DJ-2026-005"] = btn1
        section.add_item(btn1)

        btn2 = _make_item_btn("    \U0001F4CB SW-2026-007")
        self._connect_item(btn2, "SW-2026-007")
        items["SW-2026-007"] = btn2
        section.add_item(btn2)

        btn3 = _make_item_btn("    \U0001F4CB SW-2026-008")
        self._connect_item(btn3, "SW-2026-008")
        items["SW-2026-008"] = btn3
        section.add_item(btn3)
        layout.addWidget(section)

        layout.addWidget(_make_separator())

        btn4 = _make_item_btn("  \u2795\u65B0\u5EFA\u9879\u76EE...")
        self._connect_item(btn4, "new_project")
        items["new_project"] = btn4
        layout.addWidget(btn4)

        btn5 = _make_item_btn("  \U0001F4C2\u6253\u5F00\u9879\u76EE...")
        self._connect_item(btn5, "open_project")
        items["open_project"] = btn5
        layout.addWidget(btn5)

        btn6 = _make_item_btn("  \U0001F510\u6302\u8F7D\u5DE5\u4F5C\u7A7A\u95F4...")
        self._connect_item(btn6, "mount_workspace")
        items["mount_workspace"] = btn6
        layout.addWidget(btn6)

        layout.addStretch()
        self._store_activity_items(activity_id, items)
        self._active_item_key[activity_id] = "DJ-2026-005"
        return container

    def _build_document_content(self) -> QWidget:
        activity_id = "document"
        items: Dict[str, QPushButton] = {}
        template_names = [
            "\U0001F4C4 \u9879\u76EE\u9700\u6C42\u6587\u6863",
            "\U0001F4C4 \u7CFB\u7EDF\u67B6\u6784\u6587\u6863",
            "\U0001F4C4 PLC\u7A0B\u5E8F\u6587\u6863",
            "\U0001F4C4 HMI\u754C\u9762\u6587\u6863",
            "\U0001F4C4 IO\u5206\u914D\u8868\u6587\u6863",
            "\U0001F4C4 \u901A\u4FE1\u534F\u8BAE\u6587\u6863",
            "\U0001F4C4 \u6D4B\u8BD5\u62A5\u544A\u6587\u6863",
        ]
        template_ids = [
            "tpl_requirements", "tpl_architecture", "tpl_plc_program",
            "tpl_hmi", "tpl_io_table", "tpl_communication", "tpl_test_report",
        ]

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        section = _SectionWidget("\u6587\u6863\u6A21\u677F", "\U0001F4C4", expanded=True)
        for i, (name, tid) in enumerate(zip(template_names, template_ids)):
            btn = _make_item_btn(f"  {name}")
            self._connect_item(btn, tid)
            items[tid] = btn
            section.add_item(btn)
        layout.addWidget(section)

        layout.addWidget(_make_separator())

        btn_editor = _make_item_btn("  \u270F\uFE0F\u6587\u6863\u7F16\u8F91\u5668")
        self._connect_item(btn_editor, "doc_editor")
        items["doc_editor"] = btn_editor
        layout.addWidget(btn_editor)

        btn_new = _make_item_btn("  \u2795\u4ECE\u6A21\u677F\u65B0\u5EFA...")
        self._connect_item(btn_new, "new_from_template")
        items["new_from_template"] = btn_new
        layout.addWidget(btn_new)

        btn_open = _make_item_btn("  \U0001F4BE\u6253\u5F00\u6587\u6863...")
        self._connect_item(btn_open, "open_document")
        items["open_document"] = btn_open
        layout.addWidget(btn_open)

        layout.addStretch()
        self._store_activity_items(activity_id, items)
        return container

    def _build_plc_tools_content(self) -> QWidget:
        activity_id = "plc-tools"
        items: Dict[str, QPushButton] = {}
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        section = _SectionWidget("PLC\u5F00\u53D1\u5DE5\u5177", "\u26A1", expanded=True)

        btn_st = _make_item_btn("  \U0001F4DDST\u4EE3\u7801\u7F16\u8F91\u5668")
        self._set_item_active(btn_st, True)
        self._connect_item(btn_st, "st_editor")
        items["st_editor"] = btn_st
        section.add_item(btn_st)

        io_container, io_btn = _make_item_with_dev_badge("  \U0001F50CIO\u5206\u914D\u8868")
        self._connect_item(io_btn, "io_table")
        items["io_table"] = io_btn
        section.add_item(io_container, io_btn)

        btn_var = _make_item_btn("  \U0001F50D\u53D8\u91CF\u68C0\u67E5\u5668")
        self._connect_item(btn_var, "variable_checker")
        items["variable_checker"] = btn_var
        section.add_item(btn_var)
        layout.addWidget(section)

        layout.addWidget(_make_separator())

        btn_syslib = _make_item_btn("  \U0001F4DASysLib\u5E93\u6D4F\u89C8\u5668")
        self._connect_item(btn_syslib, "syslib_browser")
        items["syslib_browser"] = btn_syslib
        layout.addWidget(btn_syslib)

        btn_fb = _make_item_btn("  \U0001F517FB\u63A5\u53E3\u68C0\u67E5")
        self._connect_item(btn_fb, "fb_interface_check")
        items["fb_interface_check"] = btn_fb
        layout.addWidget(btn_fb)

        layout.addStretch()
        self._store_activity_items(activity_id, items)
        self._active_item_key[activity_id] = "st_editor"
        return container

    def _build_change_content(self) -> QWidget:
        activity_id = "change"
        items: Dict[str, QPushButton] = {}
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        section = _SectionWidget("\u53D8\u66F4\u7BA1\u7406", "\U0001F504", expanded=True)

        cl_container, cl_btn, cl_badge = _make_item_with_badge(
            "  \U0001F4CB\u53D8\u66F4\u5355\u5217\u8868", "5")
        self._set_item_active(cl_btn, True)
        self._connect_item(cl_btn, "change_list")
        items["change_list"] = cl_btn
        self._badge_labels["change_list_badge"] = cl_badge
        section.add_item(cl_container, cl_btn)

        btn_new = _make_item_btn("  \u2795\u65B0\u5EFA\u53D8\u66F4\u5355")
        self._connect_item(btn_new, "new_change")
        items["new_change"] = btn_new
        section.add_item(btn_new)
        layout.addWidget(section)

        layout.addWidget(_make_separator())

        btn_vs = _make_item_btn("  \U0001F50D\u7248\u672C\u540C\u6B65\u68C0\u67E5")
        self._connect_item(btn_vs, "version_sync_check")
        items["version_sync_check"] = btn_vs
        layout.addWidget(btn_vs)

        btn_chg = _make_item_btn("  \U0001F4DD\u751F\u6210CHG\u6587\u6863")
        self._connect_item(btn_chg, "generate_chg")
        items["generate_chg"] = btn_chg
        layout.addWidget(btn_chg)

        btn_ifc = _make_item_btn("  \U0001F4DD\u751F\u6210IFC\u6587\u6863")
        self._connect_item(btn_ifc, "generate_ifc")
        items["generate_ifc"] = btn_ifc
        layout.addWidget(btn_ifc)

        btn_report = _make_item_btn("  \U0001F4CA\u540C\u6B65\u62A5\u544A")
        self._connect_item(btn_report, "sync_report")
        items["sync_report"] = btn_report
        layout.addWidget(btn_report)

        layout.addStretch()
        self._store_activity_items(activity_id, items)
        self._active_item_key[activity_id] = "change_list"
        return container

    def _build_spec_content(self) -> QWidget:
        activity_id = "spec"
        items: Dict[str, QPushButton] = {}
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        section = _SectionWidget("\u68C0\u67E5\u5668", "\u2705", expanded=True, badge_text="7")

        btn_select = _make_item_btn("  \U0001F50D\u9009\u62E9\u68C0\u67E5\u5668")
        self._set_item_active(btn_select, True)
        self._connect_item(btn_select, "select_checker")
        items["select_checker"] = btn_select
        section.add_item(btn_select)

        syn_container, syn_btn, syn_badge = _make_item_with_badge(
            "  \U0001F4DD\u8BED\u6CD5\u68C0\u67E5", "Trae", badge_trae=True)
        self._connect_item(syn_btn, "syntax_check")
        items["syntax_check"] = syn_btn
        section.add_item(syn_container, syn_btn)

        cmt_container, cmt_btn, cmt_badge = _make_item_with_badge(
            "  \U0001F4AC\u6CE8\u91CA\u68C0\u67E5", "Trae", badge_trae=True)
        self._connect_item(cmt_btn, "comment_check")
        items["comment_check"] = cmt_btn
        section.add_item(cmt_container, cmt_btn)

        btn_naming = _make_item_btn("  \U0001F3F7\u547D\u540D\u89C4\u8303")
        self._connect_item(btn_naming, "naming_check")
        items["naming_check"] = btn_naming
        section.add_item(btn_naming)

        var_container, var_btn, var_badge = _make_item_with_badge(
            "  \U0001F4E6\u53D8\u91CF\u68C0\u67E5", "\u6DF7\u5408", badge_hybrid=True)
        self._connect_item(var_btn, "variable_check")
        items["variable_check"] = var_btn
        section.add_item(var_container, var_btn)

        btn_config = _make_item_btn("  \u2699\u914D\u7F6E\u68C0\u67E5")
        self._connect_item(btn_config, "config_check")
        items["config_check"] = btn_config
        section.add_item(btn_config)

        btn_timer = _make_item_btn("  \u23F1\u5B9A\u65F6\u5668\u68C0\u67E5")
        self._connect_item(btn_timer, "timer_check")
        items["timer_check"] = btn_timer
        section.add_item(btn_timer)

        fb_container, fb_btn, fb_badge = _make_item_with_badge(
            "  \U0001F517FB\u63A5\u53E3\u8C03\u7528", "\u6DF7\u5408", badge_hybrid=True)
        self._connect_item(fb_btn, "fb_interface_check")
        items["fb_interface_check"] = fb_btn
        section.add_item(fb_container, fb_btn)
        layout.addWidget(section)

        layout.addWidget(_make_separator())

        btn_fix = _make_item_btn("  \U0001F527\u81EA\u52A8\u4FEE\u590D")
        self._connect_item(btn_fix, "auto_fix")
        items["auto_fix"] = btn_fix
        layout.addWidget(btn_fix)

        btn_export = _make_item_btn("  \U0001F4CAExcel\u5BFC\u51FA")
        self._connect_item(btn_export, "excel_export")
        items["excel_export"] = btn_export
        layout.addWidget(btn_export)

        layout.addStretch()
        self._store_activity_items(activity_id, items)
        self._active_item_key[activity_id] = "select_checker"
        return container

    def _build_settings_content(self) -> QWidget:
        activity_id = "settings"
        items: Dict[str, QPushButton] = {}
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        section = _SectionWidget("\u8BBE\u7F6E", "\u2699", expanded=True)

        btn_general = _make_item_btn("  \U0001F5A5\u5E38\u89C4\u8BBE\u7F6E")
        self._set_item_active(btn_general, True)
        self._connect_item(btn_general, "general")
        items["general"] = btn_general
        section.add_item(btn_general)

        btn_editor = _make_item_btn("  \U0001F4DD\u7F16\u8F91\u5668")
        self._connect_item(btn_editor, "editor")
        items["editor"] = btn_editor
        section.add_item(btn_editor)

        btn_theme = _make_item_btn("  \U0001F3A8\u5916\u89C2")
        self._connect_item(btn_theme, "appearance")
        items["appearance"] = btn_theme
        section.add_item(btn_theme)

        btn_keys = _make_item_btn("  \u2318\u5FEB\u6377\u952E")
        self._connect_item(btn_keys, "shortcuts")
        items["shortcuts"] = btn_keys
        section.add_item(btn_keys)
        layout.addWidget(section)

        layout.addStretch()
        self._store_activity_items(activity_id, items)
        self._active_item_key[activity_id] = "general"
        return container

    def set_activity(self, activity_id: str) -> None:
        if activity_id not in self.ACTIVITIES:
            return
        if activity_id not in self._templates:
            method_name = f"_build_{activity_id.replace('-', '_')}_content"
            builder = getattr(self, method_name, None)
            if builder is None:
                return
            content = builder()
            self._templates[activity_id] = _wrap_scroll(content)
        current_widget = self._scroll_area.takeWidget()
        if current_widget:
            current_widget.setParent(None)
        self._scroll_area.setWidget(self._templates[activity_id])
        self._activity_id = activity_id

    def set_active_item(self, tab_id: str) -> None:
        activity_items = self._all_item_btns.get(self._activity_id, {})
        prev_key = self._active_item_key.get(self._activity_id)
        if prev_key and prev_key in activity_items:
            self._set_item_active(activity_items[prev_key], False)
        if tab_id in activity_items:
            self._set_item_active(activity_items[tab_id], True)
            self._active_item_key[self._activity_id] = tab_id

    def clear_active_items(self) -> None:
        activity_items = self._all_item_btns.get(self._activity_id, {})
        for btn in activity_items.values():
            self._set_item_active(btn, False)
        self._active_item_key[self._activity_id] = None

    def toggle_collapse(self) -> None:
        self.set_collapsed(not self._collapsed)

    def set_collapsed(self, collapsed: bool) -> None:
        if self._collapsed == collapsed:
            return
        self._collapsed = collapsed
        if collapsed:
            self.setMinimumWidth(0)
            self.setMaximumWidth(0)
            self._collapse_btn.setText("\u25B6")
        else:
            self.setMinimumWidth(0)
            self.setMaximumWidth(_SIDEBAR_WIDTH)
            self._collapse_btn.setText("\u25C0")
        self.sidebar_collapsed.emit(collapsed)

    def update_badge(self, section: str, count: int) -> None:
        badge = self._badge_labels.get(section)
        if badge is not None:
            badge.setText(str(count))