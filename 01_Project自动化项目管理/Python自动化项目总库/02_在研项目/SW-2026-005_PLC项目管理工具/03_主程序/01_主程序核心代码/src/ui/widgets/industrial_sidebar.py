# -*- coding: utf-8 -*-
from typing import Callable, Dict, List, Optional, Tuple

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QFrame,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..widgets.project_tree import ProjectTreeWidget
from src.ui.ui_scale import UIProfile, current_ui_profile


_SECTION_DEFS: List[Dict] = [
    {
        "title": "项目管理",
        "icon": "\U0001F4C1",
        "always_expanded": True,
        "buttons": [],
    },
    {
        "title": "文档管理",
        "icon": "\U0001F4DD",
        "always_expanded": False,
        "buttons": [
            ("\u65B0\u5EFA\u6587\u6863", 2),
            ("\u6A21\u677F\u7BA1\u7406", 2),
            ("\u6253\u5F00\u6587\u6863", 2),
        ],
    },
    {
        "title": "PLC\u5DE5\u5177",
        "icon": "\u26A1",
        "always_expanded": False,
        "buttons": [
            ("ST\u4EE3\u7801\u7F16\u8F91\u5668", 4),
            ("IO\u5206\u914D\u8868", 4),
            ("\u53D8\u91CF\u68C0\u67E5\u5668", 4),
        ],
    },
    {
        "title": "\u53D8\u66F4\u7BA1\u7406",
        "icon": "\U0001F504",
        "always_expanded": False,
        "buttons": [
            ("\u5237\u65B0\u53D8\u66F4\u5355\u5217\u8868", 3),
        ],
    },
    {
        "title": "\u89C4\u8303\u4E2D\u5FC3",
        "icon": "\u2705",
        "always_expanded": False,
        "buttons": [
            ("\u89C4\u8303\u68C0\u67E5", 5),
            ("\u6DF1\u5EA6\u8BCA\u65AD (F6)", 5),
            ("\u751F\u6210\u62A5\u544A", 5),
            None,
            ("\u7248\u672C\u68C0\u67E5", None),
            ("\u751F\u6210CHG\u6587\u6863", None),
            ("\u751F\u6210IFC\u6587\u6863", None),
        ],
    },
    {
        "title": "\u7CFB\u7EDF\u8BBE\u7F6E",
        "icon": "\u2699",
        "always_expanded": False,
        "buttons": [
            ("\u6253\u5F00\u8BBE\u7F6E (Ctrl+,)", None),
            ("\u4E3B\u9898\u5207\u6362", None),
            ("\u5173\u4E8E", None),
        ],
    },
]


class _SectionWidget(QWidget):

    def __init__(
        self,
        section_index: int,
        title: str,
        icon: str,
        always_expanded: bool,
        buttons: List[Optional[Tuple[str, Optional[int]]]],
        action_handler: Callable,
        profile: UIProfile,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self._section_index = section_index
        self._always_expanded = always_expanded
        self._expanded = always_expanded
        self._action_handler = action_handler
        self._profile = profile
        self._active_btn: Optional[QPushButton] = None

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._header_btn = QPushButton(f"  {icon}  {title}  \u25BC")
        self._header_btn.setProperty("SidebarSectionHeader", True)
        self._header_btn.setCursor(Qt.PointingHandCursor)
        self._header_btn.setCheckable(True)
        self._header_btn.setChecked(always_expanded)
        self._header_btn.clicked.connect(self._toggle_section)
        root.addWidget(self._header_btn)

        self._content = QWidget()
        self._content.setProperty("SidebarSectionContent", True)
        content_layout = QVBoxLayout(self._content)
        content_layout.setContentsMargins(
            profile.spacing_md,
            profile.spacing_sm,
            profile.spacing_md,
            profile.spacing_sm,
        )
        content_layout.setSpacing(profile.spacing_xs)

        if section_index == 0:
            self._project_tree_widget = ProjectTreeWidget()
            self._project_tree_widget.navigation_requested.connect(
                lambda tab_index, ctx=None: action_handler(tab_index)
            )
            content_layout.addWidget(self._project_tree_widget)
        else:
            self._project_tree_widget = None
            for action_item in buttons:
                if action_item is None:
                    separator = QFrame()
                    separator.setFrameShape(QFrame.HLine)
                    separator.setProperty("IndustrialSeparator", True)
                    content_layout.addWidget(separator)
                    continue

                action_text, target_tab = action_item
                btn = QPushButton(f"  {action_text}")
                btn.setProperty("SidebarBtn", True)
                btn.setCursor(Qt.PointingHandCursor)
                btn.setCheckable(True)
                if target_tab is not None:
                    btn.clicked.connect(
                        lambda checked, t=target_tab, b=btn: self._on_btn_clicked(b, t)
                    )
                else:
                    btn.clicked.connect(
                        lambda checked, a=action_text, b=btn: self._on_action_btn_clicked(b, a)
                    )
                content_layout.addWidget(btn)

        content_layout.addStretch()
        root.addWidget(self._content)

        if not always_expanded:
            self._content.setVisible(False)
            self._header_btn.setText(f"  {icon}  {title}  \u25B6")

    @property
    def project_tree_widget(self) -> Optional[ProjectTreeWidget]:
        return self._project_tree_widget

    @property
    def is_expanded(self) -> bool:
        return self._expanded

    def set_expanded(self, expanded: bool) -> None:
        if self._always_expanded:
            return
        self._expanded = expanded
        self._content.setVisible(expanded)
        title = self._header_btn.text()
        if expanded:
            if title.endswith("\u25B6"):
                self._header_btn.setText(title[:-1] + "\u25BC")
        else:
            if title.endswith("\u25BC"):
                self._header_btn.setText(title[:-1] + "\u25B6")
        self._header_btn.setChecked(expanded)

    def _toggle_section(self, checked: bool) -> None:
        if self._always_expanded:
            self._header_btn.setChecked(True)
            return
        self.set_expanded(checked)

    def _on_btn_clicked(self, btn: QPushButton, tab_index: int) -> None:
        self._clear_active_btn()
        btn.setChecked(True)
        btn.setProperty("SidebarBtnActive", True)
        btn.style().unpolish(btn)
        btn.style().polish(btn)
        self._active_btn = btn
        self._action_handler(tab_index)

    def _on_action_btn_clicked(self, btn: QPushButton, action_text: str) -> None:
        self._clear_active_btn()
        btn.setChecked(True)
        btn.setProperty("SidebarBtnActive", True)
        btn.style().unpolish(btn)
        btn.style().polish(btn)
        self._active_btn = btn
        self._action_handler(action_text)

    def _clear_active_btn(self) -> None:
        if self._active_btn is not None:
            self._active_btn.setChecked(False)
            self._active_btn.setProperty("SidebarBtnActive", False)
            self._active_btn.style().unpolish(self._active_btn)
            self._active_btn.style().polish(self._active_btn)
            self._active_btn = None

    def clear_active(self) -> None:
        self._clear_active_btn()


class IndustrialSidebar(QWidget):

    currentChanged = pyqtSignal(int)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        action_handler: Optional[Callable] = None,
        ui_profile: Optional[UIProfile] = None,
    ):
        super().__init__(parent)
        self._profile = ui_profile or current_ui_profile(parent)
        self._action_handler = action_handler or (lambda x: None)
        self._current_index = 0
        self._sections: List[_SectionWidget] = []

        self.setProperty("IndustrialSidebar", True)
        self.setMinimumWidth(self._profile.sidebar_min_width)
        self.setMaximumWidth(self._profile.sidebar_max_width)

        self._root_layout = QVBoxLayout(self)
        self._root_layout.setContentsMargins(0, 0, 0, 0)
        self._root_layout.setSpacing(0)

        self._build_sections()
        self._root_layout.addStretch()

        self._project_tree_widget = self._sections[0].project_tree_widget

    def _build_sections(self) -> None:
        for idx, section_def in enumerate(_SECTION_DEFS):
            section = _SectionWidget(
                section_index=idx,
                title=section_def["title"],
                icon=section_def["icon"],
                always_expanded=section_def["always_expanded"],
                buttons=section_def["buttons"],
                action_handler=self._action_handler,
                profile=self._profile,
                parent=self,
            )
            self._sections.append(section)
            self._root_layout.addWidget(section)

    def setCurrentIndex(self, index: int) -> None:
        if not (0 <= index < len(self._sections)):
            return
        old_index = self._current_index
        self._current_index = index
        section = self._sections[index]
        if not section.is_expanded:
            section.set_expanded(True)
        if old_index != index:
            self.currentChanged.emit(index)

    def currentIndex(self) -> int:
        return self._current_index
