"""全局功能页

规范中心/模板管理/报告中心/系统设置。V2.0 占位。
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QTabWidget, QVBoxLayout, QWidget

# 全局功能页 Tab 标识 → 中文标签
GLOBAL_TAB_LABELS: dict[str, str] = {
    "spec_center": "规范中心",
    "template": "模板管理",
    "report": "报告中心",
    "settings": "系统设置",
}

# 全局功能页 Tab 默认顺序
GLOBAL_TAB_ORDER: list[str] = [
    "spec_center",
    "template",
    "report",
    "settings",
]

# 全局功能页 Tab → 计划交付版本（V2.0 占位提示）
GLOBAL_TAB_VERSION: dict[str, str] = {
    "spec_center": "V2.2",
    "template": "V2.4",
    "report": "V2.4",
    "settings": "V2.5",
}


class GlobalView(QWidget):
    """全局功能页

    Tab 导航：规范中心/模板管理/报告中心/系统设置。
    V2.0 仅占位。
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._tab_indices: dict[str, int] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        self._tab_widget = QTabWidget()
        for tab_id in GLOBAL_TAB_ORDER:
            page = self._make_placeholder(tab_id)
            idx = self._tab_widget.addTab(page, GLOBAL_TAB_LABELS[tab_id])
            self._tab_indices[tab_id] = idx
        layout.addWidget(self._tab_widget)

    def _make_placeholder(self, tab_id: str) -> QWidget:
        page = QWidget()
        v = QVBoxLayout(page)
        v.setContentsMargins(20, 20, 20, 20)
        version = GLOBAL_TAB_VERSION.get(tab_id, "后续版本")
        label = QLabel(f"{GLOBAL_TAB_LABELS[tab_id]} 功能将在 {version} 交付")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #999; font-size: 14px;")
        v.addWidget(label)
        v.addStretch(1)
        return page

    def show_tab(self, tab_id: str) -> None:
        """切换到指定 Tab（侧边栏导航触发，强制可见）"""
        if tab_id in self._tab_indices:
            idx = self._tab_indices[tab_id]
            self._tab_widget.setTabVisible(idx, True)
            self._tab_widget.setCurrentIndex(idx)
