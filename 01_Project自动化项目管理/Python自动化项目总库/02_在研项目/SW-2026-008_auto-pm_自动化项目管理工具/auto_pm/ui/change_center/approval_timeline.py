"""变更中心 - 审批时间线 QWidget（M3-3 T71/T72）

垂直展示变更单状态流转历史，数据来自 ChangeService.list_approval_history()。
每条 ApprovalRecord 渲染为一个时间节点：彩色圆点 + 连接线 + 状态流转 + 审批人 + 意见 + 日期。
空历史显示"暂无审批记录"。

节点视觉示例：
  ●──┬─ 草稿 → 已提交
     │   审批人: fubai  |  2026-06-25 14:30
     │   提交审批，请审核
     │
  ●──┬─ 已提交 → 审核中
     │   审批人: reviewer1  |  2026-06-25 15:00
     │
  ●──── 审核中 → 已审批
         审批人: pm_lead  |  2026-06-25 16:00
         审批通过
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from auto_pm.change.change_service import ChangeService
from auto_pm.change.models import STATUS_LABELS
from auto_pm.models import ApprovalRecord

__all__ = ["ApprovalTimeline"]

# 节点圆点颜色（对齐 change_detail_panel._STATUS_BADGE_COLOR 的背景色）
_STATUS_DOT_COLOR: dict[str, str] = {
    "draft": "#95a5a6",
    "submitted": "#4a90d9",
    "under_review": "#4a90d9",
    "approved": "#27ae60",
    "conditionally_approved": "#27ae60",
    "rejected": "#e74c3c",
    "implementing": "#f39c12",
    "pending_acceptance": "#f39c12",
    "accepting": "#f39c12",
    "completed": "#16a085",
    "closed": "#7f8c8d",
    "archived": "#7f8c8d",
}

_TIMELINE_STYLE = """
QFrame#timelineNode {
    background: transparent;
}
QFrame#nodeConnector {
    background: #d0d0d0;
    min-width: 2px;
    max-width: 2px;
}
QLabel#nodeTransition {
    font-size: 12px;
    font-weight: bold;
    color: #333;
}
QLabel#nodeMeta {
    font-size: 11px;
    color: #888;
}
QLabel#nodeComment {
    font-size: 11px;
    color: #555;
    background: #f8f9fa;
    padding: 4px 6px;
    border-radius: 3px;
    border: 1px solid #e8e8e8;
}
QLabel#emptyHint {
    color: #999;
    font-size: 12px;
    padding: 20px;
}
"""


class ApprovalTimeline(QWidget):
    """审批时间线 - 垂直展示变更单状态流转历史

    数据来自 ChangeService.list_approval_history()。
    每条记录渲染为一个时间节点：圆点 + 连接线 + 状态流转信息。
    """

    def __init__(
        self,
        change_service: ChangeService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._change_service = change_service
        self._change_number: str | None = None
        self._build_ui()

    # ── UI 构建 ────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.setStyleSheet(_TIMELINE_STYLE)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(8, 4, 8, 4)
        self._layout.setSpacing(0)
        self._show_empty()

    def _clear(self) -> None:
        """清空时间线布局中的所有 widget"""
        while self._layout.count():
            item = self._layout.takeAt(0)
            assert item is not None
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _show_empty(self) -> None:
        """显示空状态提示"""
        self._clear()
        hint = QLabel("暂无审批记录")
        hint.setObjectName("emptyHint")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(hint)
        self._layout.addStretch(1)

    # ── 数据加载 ──────────────────────────────────────────

    def load_history(self, change_number: str) -> None:
        """加载并渲染审批历史"""
        self._change_number = change_number
        records = self._change_service.list_approval_history(change_number)
        self._clear()
        if not records:
            self._show_empty()
            return
        for i, record in enumerate(records):
            is_last = i == len(records) - 1
            self._add_timeline_node(record, is_last)
        self._layout.addStretch(1)

    # ── 节点渲染 ─────────────────────────────────────────

    def _add_timeline_node(self, record: ApprovalRecord, is_last: bool) -> None:
        """添加一个时间节点

        节点结构：
            [圆点]  状态流转（from → to）
            [  |  ]  审批人 | 日期
            [  |  ]  审批意见（若有）
        """
        node_frame = QFrame()
        node_frame.setObjectName("timelineNode")
        node_layout = QVBoxLayout(node_frame)
        node_layout.setContentsMargins(0, 0, 0, 0)
        node_layout.setSpacing(4)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(10)

        # 左侧列：圆点 + 连接线（连接线填充至节点底部，对齐下一节点圆点）
        dot_column = QVBoxLayout()
        dot_column.setContentsMargins(0, 2, 0, 0)
        dot_column.setSpacing(0)

        dot = QLabel()
        dot.setObjectName("nodeDot")
        color = _STATUS_DOT_COLOR.get(record.to_status, "#95a5a6")
        dot.setStyleSheet(
            f"background: {color}; border-radius: 7px; "
            "min-width: 14px; max-width: 14px; "
            "min-height: 14px; max-height: 14px;"
        )
        dot_column.addWidget(dot, alignment=Qt.AlignmentFlag.AlignHCenter)

        if not is_last:
            connector = QFrame()
            connector.setObjectName("nodeConnector")
            dot_column.addWidget(connector, 1, alignment=Qt.AlignmentFlag.AlignHCenter)

        row.addLayout(dot_column)

        # 右侧列：状态流转 + 审批人/日期 + 意见
        content = QVBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(2)

        from_label = STATUS_LABELS.get(record.from_status, record.from_status or "—")
        to_label = STATUS_LABELS.get(record.to_status, record.to_status)
        transition = QLabel(f"{from_label} → {to_label}")
        transition.setObjectName("nodeTransition")
        content.addWidget(transition)

        meta_parts: list[str] = []
        if record.approver:
            meta_parts.append(f"审批人: {record.approver}")
        if record.transition_date:
            meta_parts.append(record.transition_date[:16].replace("T", " "))
        if meta_parts:
            meta = QLabel("  |  ".join(meta_parts))
            meta.setObjectName("nodeMeta")
            content.addWidget(meta)

        if record.comment:
            comment = QLabel(record.comment)
            comment.setObjectName("nodeComment")
            comment.setWordWrap(True)
            content.addWidget(comment)

        row.addLayout(content, 1)
        node_layout.addLayout(row)
        self._layout.addWidget(node_frame)
