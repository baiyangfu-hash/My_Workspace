"""可折叠分组标题组件

展示分组名称和项目计数，点击切换展开/折叠状态。
箭头图标 ▶（折叠）/ ▼（展开）。
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget

__all__ = ["GroupHeader"]

_STYLE = """
QFrame#GroupHeader {
    background: #eef1f5;
    border: 1px solid #d8dce3;
    border-radius: 4px;
}
QFrame#GroupHeader:hover {
    background: #e4e9f0;
}
QLabel#groupArrow { font-size: 12px; color: #555; }
QLabel#groupName { font-size: 13px; font-weight: bold; color: #222; }
QLabel#groupCount { font-size: 11px; color: #888; }
"""

_ARROW_EXPANDED = "▼"
_ARROW_COLLAPSED = "▶"


class GroupHeader(QFrame):
    """可折叠分组标题

    点击切换展开/折叠，发射 toggled(bool) 信号。
    通过 set_expanded(bool) 编程式控制。

    Signals:
        toggled(bool): 展开/折叠状态变化，True=展开
    """

    toggled = Signal(bool)

    def __init__(
        self,
        name: str = "",
        count: int = 0,
        expanded: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("GroupHeader")
        self.setStyleSheet(_STYLE)
        self.setCursor(Qt.PointingHandCursor)
        self._expanded = expanded
        self._count = count
        self._build_ui()
        self.set_name(name)
        self.set_count(count)
        self._update_arrow()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(6)

        self._arrow_label = QLabel(_ARROW_EXPANDED)
        self._arrow_label.setObjectName("groupArrow")
        layout.addWidget(self._arrow_label)

        self._name_label = QLabel("")
        self._name_label.setObjectName("groupName")
        layout.addWidget(self._name_label)

        self._count_label = QLabel("(0)")
        self._count_label.setObjectName("groupCount")
        layout.addWidget(self._count_label)

        layout.addStretch(1)

    # ── 鼠标交互 ──────────────────────────────────────────

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.LeftButton:
            self.set_expanded(not self._expanded)
        super().mousePressEvent(event)

    # ── 公开方法 ──────────────────────────────────────────

    def set_name(self, name: str) -> None:
        """设置分组名称"""
        self._name_label.setText(name)

    def set_count(self, count: int) -> None:
        """设置项目计数"""
        self._count = count
        self._count_label.setText(f"({count})")

    @property
    def name(self) -> str:
        return self._name_label.text()

    @property
    def count(self) -> int:
        return self._count

    @property
    def is_expanded(self) -> bool:
        return self._expanded

    def set_expanded(self, expanded: bool) -> None:
        """设置展开/折叠状态，并发射 toggled 信号"""
        if expanded == self._expanded:
            return
        self._expanded = expanded
        self._update_arrow()
        self.toggled.emit(expanded)

    # ── 内部方法 ──────────────────────────────────────────

    def _update_arrow(self) -> None:
        self._arrow_label.setText(_ARROW_EXPANDED if self._expanded else _ARROW_COLLAPSED)
