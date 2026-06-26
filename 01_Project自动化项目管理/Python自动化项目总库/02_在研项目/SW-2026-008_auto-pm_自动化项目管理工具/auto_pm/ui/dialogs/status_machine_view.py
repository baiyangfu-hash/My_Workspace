"""状态机可视化视图（M3-4 T77）

水平展示变更单状态机的 12 个状态节点 + 箭头，支持一键流转：
- 当前状态：蓝色边框 + 浅蓝背景
- 目标状态：绿色填充 + 白色文字
- 可达状态（STATUS_FLOW[current] 中的）：白色背景，可点击
- 不可达状态：灰色，不可点击

节点点击发射 target_selected(status) 信号，由 TransitionDialog 接收后
联动更新目标状态字段和验证结论显隐。

状态顺序对齐 PM-042 V2.3.0 §5.2 状态机主流程 + 分支：
    draft → submitted → under_review → approved → implementing
                                    ↘               ↘
                          conditionally_approved   pending_acceptance → accepting → completed → closed
                                    ↘                                       ↘          ↘
                                     rejected                                 implementing  archived
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from auto_pm.change.models import STATUS_FLOW, STATUS_LABELS

__all__ = ["StatusMachineView"]

# 状态节点展示顺序（主流程 + 分支交错排列，对齐 §5.2 状态机图）
_STATUS_ORDER: list[str] = [
    "draft",
    "submitted",
    "under_review",
    "approved",
    "conditionally_approved",
    "rejected",
    "implementing",
    "pending_acceptance",
    "accepting",
    "completed",
    "closed",
    "archived",
]

# 节点样式
_STYLE_CURRENT = (
    "QPushButton { border: 2px solid #4a90d9; background: #e6f0ff; "
    "color: #222; font-weight: bold; padding: 4px 8px; border-radius: 3px; }"
)
_STYLE_TARGET = (
    "QPushButton { border: 2px solid #27ae60; background: #27ae60; "
    "color: #ffffff; font-weight: bold; padding: 4px 8px; border-radius: 3px; }"
)
_STYLE_REACHABLE = (
    "QPushButton { background: #ffffff; color: #333; "
    "padding: 4px 8px; border: 1px solid #d0d0d0; border-radius: 3px; }"
    "QPushButton:hover { background: #f0f5ff; border-color: #4a90d9; }"
)
_STYLE_UNREACHABLE = (
    "QPushButton { background: #f5f5f5; color: #bbb; "
    "padding: 4px 8px; border: 1px solid #e8e8e8; border-radius: 3px; }"
    "QPushButton:disabled { background: #f5f5f5; color: #bbb; }"
)

# 箭头样式
_ARROW_TEXT = "→"
_ARROW_REACHABLE = f'<span style="color:#27ae60;font-weight:bold;">{_ARROW_TEXT}</span>'
_ARROW_NORMAL = f'<span style="color:#999;">{_ARROW_TEXT}</span>'


class StatusMachineView(QWidget):
    """状态机可视化视图

    水平展示 12 个状态节点，当前状态蓝色边框，目标状态绿色填充，
    可达状态可点击（点击发射 target_selected 信号），不可达状态灰色禁用。
    """

    target_selected = Signal(str)

    def __init__(
        self,
        current_status: str,
        target_status: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._current = current_status
        self._target = target_status
        self._buttons: dict[str, QPushButton] = {}
        self._arrows: list[QLabel] = []
        self._build_ui()
        self._refresh_styles()

    # ── UI 构建 ────────────────────────────────────────────

    def _build_ui(self) -> None:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        container = QWidget()
        row = QHBoxLayout(container)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(2)

        for i, status in enumerate(_STATUS_ORDER):
            if i > 0:
                arrow = QLabel(_ARROW_NORMAL)
                arrow.setTextFormat(Qt.TextFormat.RichText)
                row.addWidget(arrow)
                self._arrows.append(arrow)

            label = STATUS_LABELS.get(status, status)
            btn = QPushButton(label)
            btn.setFixedHeight(28)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, s=status: self._on_node_clicked(s))
            row.addWidget(btn)
            self._buttons[status] = btn

        scroll.setWidget(container)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(2)
        title = QLabel("状态机概览（点击可达状态节点一键流转）")
        title.setStyleSheet("color: #666; font-size: 11px;")
        outer.addWidget(title)
        outer.addWidget(scroll)

    # ── 公开方法 ──────────────────────────────────────────

    def set_current(self, current: str) -> None:
        """更新当前状态，刷新节点样式"""
        self._current = current
        self._refresh_styles()

    def set_target(self, target: str) -> None:
        """更新目标状态，刷新节点样式"""
        self._target = target
        self._refresh_styles()

    def get_reachable_targets(self) -> set[str]:
        """返回当前状态的可达目标状态集合"""
        return set(STATUS_FLOW.get(self._current, set()))

    # ── 内部逻辑 ──────────────────────────────────────────

    def _on_node_clicked(self, status: str) -> None:
        """节点点击：仅可达状态发射信号"""
        if status in self.get_reachable_targets():
            self.target_selected.emit(status)

    def _refresh_styles(self) -> None:
        """根据 current/target 刷新所有节点和箭头样式"""
        reachable = self.get_reachable_targets()
        for status, btn in self._buttons.items():
            if status == self._target and status != self._current:
                btn.setStyleSheet(_STYLE_TARGET)
                btn.setEnabled(True)
            elif status == self._current:
                btn.setStyleSheet(_STYLE_CURRENT)
                btn.setEnabled(False)
            elif status in reachable:
                btn.setStyleSheet(_STYLE_REACHABLE)
                btn.setEnabled(True)
            else:
                btn.setStyleSheet(_STYLE_UNREACHABLE)
                btn.setEnabled(False)

        # 箭头颜色：相邻两节点中任一为当前/目标/可达则高亮，否则灰色
        for i, arrow in enumerate(self._arrows):
            left = _STATUS_ORDER[i]
            right = _STATUS_ORDER[i + 1]
            highlight = (
                left == self._current
                or right == self._current
                or left == self._target
                or right == self._target
                or left in reachable
                or right in reachable
            )
            arrow.setText(_ARROW_REACHABLE if highlight else _ARROW_NORMAL)
