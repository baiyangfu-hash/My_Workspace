# -*- coding: utf-8 -*-
from typing import Dict, List, Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from src.ui.ui_scale import UIProfile, current_ui_profile

_ACTIVITY_DEFS: List[Dict[str, str]] = [
    {"id": "dashboard", "icon": "\U0001F4CA", "tooltip": "\u4EEA\u8868\u76D8"},
    {"id": "project", "icon": "\U0001F4C1", "tooltip": "\u9879\u76EE\u7BA1\u7406"},
    {"id": "document", "icon": "\U0001F4DD", "tooltip": "\u6587\u6863\u7BA1\u7406"},
    {"id": "change", "icon": "\U0001F504", "tooltip": "\u53D8\u66F4\u7BA1\u7406"},
    {"id": "plc-tools", "icon": "\u26A1", "tooltip": "PLC\u5DE5\u5177"},
    {"id": "spec", "icon": "\u2705", "tooltip": "\u89C4\u8303\u4E2D\u5FC3"},
    {"id": "settings", "icon": "\u2699", "tooltip": "\u8BBE\u7F6E"},
]

_BTN_SIZE = 40
_BAR_WIDTH = 48


class ActivityBar(QWidget):

    activity_changed = pyqtSignal(str)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        ui_profile: Optional[UIProfile] = None,
    ):
        super().__init__(parent)
        self._profile = ui_profile or current_ui_profile(parent)
        self._buttons: Dict[str, QPushButton] = {}
        self._active_id: Optional[str] = None

        self.setObjectName("ActivityBar")
        self.setFixedWidth(self._profile.scale_px(_BAR_WIDTH))
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, self._profile.spacing_sm, 0, self._profile.spacing_sm)
        self._layout.setSpacing(self._profile.spacing_xs)

        self._build_buttons()

    def _build_buttons(self) -> None:
        settings_def = None
        for activity_def in _ACTIVITY_DEFS:
            if activity_def["id"] == "settings":
                settings_def = activity_def
                continue
            self._add_button(activity_def)

        self._layout.addStretch()

        if settings_def:
            self._add_button(settings_def)

    def _add_button(self, activity_def: Dict[str, str]) -> None:
        btn = QPushButton(activity_def["icon"])
        btn.setFixedSize(
            self._profile.scale_px(_BTN_SIZE),
            self._profile.scale_px(_BTN_SIZE),
        )
        btn.setToolTip(activity_def["tooltip"])
        btn.setCursor(Qt.PointingHandCursor)
        btn.setCheckable(True)
        btn.setProperty("ActivityBtn", True)
        activity_id = activity_def["id"]
        btn.clicked.connect(
            lambda checked, aid=activity_id: self._on_btn_clicked(aid)
        )
        self._buttons[activity_id] = btn
        self._layout.addWidget(
            btn, 0, Qt.AlignHCenter
        )

    def _on_btn_clicked(self, activity_id: str) -> None:
        self.set_active_activity(activity_id)
        self.activity_changed.emit(activity_id)

    def set_active_activity(self, activity_id: str) -> None:
        if self._active_id == activity_id:
            return
        if self._active_id:
            prev_btn = self._buttons.get(self._active_id)
            if prev_btn:
                prev_btn.setChecked(False)
                prev_btn.setProperty("ActiveActivity", False)
                prev_btn.style().unpolish(prev_btn)
                prev_btn.style().polish(prev_btn)
        btn = self._buttons.get(activity_id)
        if btn:
            btn.setChecked(True)
            btn.setProperty("ActiveActivity", True)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            self._active_id = activity_id

    @property
    def active_activity(self) -> Optional[str]:
        return self._active_id