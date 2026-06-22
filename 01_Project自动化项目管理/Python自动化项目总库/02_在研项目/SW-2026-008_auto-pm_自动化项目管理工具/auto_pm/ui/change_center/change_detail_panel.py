"""变更中心 - 变更单详情面板

显示变更单完整详情：编号+状态徽标、基本信息（项目/领域/性质/范围/申请人/
创建日期/计划日期/紧急度）、背景全文、必要性全文、参考依据、状态流转按钮。

状态流转按钮根据当前状态显示可用流转目标（对齐任务要求）：
    draft → [提交审批] → submitted
    submitted → [审批通过] → approved, [驳回] → rejected
    approved → [开始实施] → implementing
    implementing → [完成验收] → pending_acceptance
    completed → [归档] → closed
    closed → 无按钮

点击流转按钮弹出 TransitionDialog 收集审批人/备注/验证结论，
流转成功后发射 transition_completed(change_number) 信号。
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from auto_pm.change.change_service import ChangeService
from auto_pm.change.models import (
    BUSINESS_NATURES,
    DOMAINS,
    IMPACT_SCOPES,
    STATUS_LABELS,
    URGENCY_LEVELS,
    ChangeRequest,
)
from auto_pm.logging.logging import setup_logger
from auto_pm.ui.dialogs.transition_dialog import TransitionDialog

log = setup_logger(log_level="INFO", app_name="auto_pm")

__all__ = ["ChangeDetailPanel"]

# 状态徽标颜色：(背景色, 前景色)
_STATUS_BADGE_COLOR: dict[str, tuple[str, str]] = {
    "draft": ("#95a5a6", "#ffffff"),
    "submitted": ("#4a90d9", "#ffffff"),
    "under_review": ("#4a90d9", "#ffffff"),
    "approved": ("#27ae60", "#ffffff"),
    "conditionally_approved": ("#27ae60", "#ffffff"),
    "rejected": ("#e74c3c", "#ffffff"),
    "implementing": ("#f39c12", "#ffffff"),
    "pending_acceptance": ("#f39c12", "#ffffff"),
    "accepting": ("#f39c12", "#ffffff"),
    "completed": ("#16a085", "#ffffff"),
    "closed": ("#7f8c8d", "#ffffff"),
}

# 状态流转按钮配置：(当前状态, [(按钮文案, 目标状态), ...])
# 对齐任务要求 + 实际 STATUS_FLOW（submitted → under_review → approved 不能跳过）
# 任务要求的简化映射：
#   draft → [提交审批]
#   submitted → [审批通过] [驳回]  （实际 STATUS_FLOW 需先经 under_review）
#   approved → [开始实施]
#   implementing → [完成验收]
#   completed → [归档]
#   archived(closed) → 无按钮
# 完整映射（覆盖所有可流转状态，确保按钮点击都能成功）：
_TRANSITION_BUTTONS: dict[str, list[tuple[str, str]]] = {
    "draft": [("提交审批", "submitted")],
    "submitted": [("开始审核", "under_review")],  # submitted → under_review（不能直接到 approved）
    "under_review": [("审批通过", "approved"), ("驳回", "rejected")],
    "approved": [("开始实施", "implementing")],
    "conditionally_approved": [("开始实施", "implementing")],
    "implementing": [("完成验收", "pending_acceptance")],
    "pending_acceptance": [("开始验收", "accepting")],
    "accepting": [("验证通过", "completed"), ("返工", "implementing")],
    "completed": [("归档", "closed")],
    "rejected": [("退回草稿", "draft")],
    # closed: 无按钮（终态）
}

_PANEL_STYLE = """
QFrame#changeDetailPanel { background: #ffffff; }
QLabel#detailTitle { font-size: 16px; font-weight: bold; color: #222; }
QLabel#detailNumber { font-size: 14px; font-weight: bold; color: #222; }
QLabel#sectionHeader {
    font-size: 13px; font-weight: bold; color: #333;
    border-bottom: 1px solid #e0e0e0;
    padding-bottom: 4px;
}
QLabel#fieldLabel { font-size: 12px; color: #888; }
QLabel#fieldValue { font-size: 12px; color: #333; }
QLabel#fullText {
    font-size: 12px; color: #333;
    background: #f8f9fa; padding: 8px;
    border-radius: 4px; border: 1px solid #e8e8e8;
}
QLabel#emptyHint {
    color: #999; font-size: 14px;
    padding: 60px;
}
QPushButton#transitionBtn {
    font-size: 12px; color: #ffffff;
    background: #4a90d9; border: none;
    border-radius: 3px; padding: 6px 14px;
}
QPushButton#transitionBtn:hover { background: #357abd; }
QPushButton#transitionBtn#rejectBtn {
    background: #e74c3c;
}
QPushButton#transitionBtn#rejectBtn:hover { background: #c0392b; }
QFrame#infoRow {
    border-bottom: 1px solid #f0f0f0;
}
"""


def _make_status_badge_label(status: str, parent: QWidget | None = None) -> QLabel:
    """创建状态徽标 QLabel（彩色背景）"""
    label = QLabel(parent)
    text = STATUS_LABELS.get(status, status)
    bg, fg = _STATUS_BADGE_COLOR.get(status, ("#95a5a6", "#ffffff"))
    label.setText(text)
    label.setStyleSheet(
        f"background: {bg}; color: {fg}; "
        "font-size: 11px; font-weight: bold; "
        "padding: 3px 8px; border-radius: 3px;"
    )
    return label


def _format_impact_scope(scopes: list[str]) -> str:
    """格式化影响范围列表为中文标签字符串"""
    if not scopes:
        return "—"
    parts = [IMPACT_SCOPES.get(s, s) for s in scopes]
    return "、".join(parts)


def _format_urgency(urgency: str) -> str:
    """格式化紧急程度为中文标签"""
    return URGENCY_LEVELS.get(urgency, urgency or "—")


class ChangeDetailPanel(QWidget):
    """变更单详情面板

    显示变更单完整详情，提供状态流转按钮。
    流转成功后发射 transition_completed(change_number) 信号。
    """

    transition_completed = Signal(str)

    def __init__(
        self,
        change_service: ChangeService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._change_service = change_service
        self._current_change: ChangeRequest | None = None
        self._build_ui()

    # ── UI 构建 ────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.setObjectName("changeDetailPanel")
        self.setStyleSheet(_PANEL_STYLE)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 12, 16, 12)
        outer.setSpacing(8)

        # 滚动区域包裹详情内容
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)

        self._content_widget = QWidget()
        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(10)
        self._scroll.setWidget(self._content_widget)
        outer.addWidget(self._scroll, 1)

        # 空状态提示
        self._empty_hint = QLabel("请从左侧选择变更单查看详情")
        self._empty_hint.setObjectName("emptyHint")
        self._empty_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(self._empty_hint)

        # 初始为空状态
        self._show_empty(True)

    def _show_empty(self, empty: bool) -> None:
        """切换空状态/详情内容显示"""
        self._scroll.setVisible(not empty)
        self._empty_hint.setVisible(empty)

    # ── 数据加载 ──────────────────────────────────────────

    def load_change(self, change_number: str) -> None:
        """加载变更单详情"""
        try:
            cr = self._change_service.get_change_request(change_number)
        except Exception as e:
            log.error("加载变更单详情失败 %s: %s", change_number, e, exc_info=True)
            cr = None

        if cr is None:
            log.warning("变更单未找到: %s", change_number)
            self._current_change = None
            self._clear_content()
            self._show_empty(True)
            return

        self._current_change = cr
        self._clear_content()
        self._render_detail(cr)
        self._show_empty(False)

    def clear(self) -> None:
        """清空显示"""
        self._current_change = None
        self._clear_content()
        self._show_empty(True)

    def _clear_content(self) -> None:
        """清空详情内容布局中的所有 widget"""
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    # ── 详情渲染 ─────────────────────────────────────────

    def _render_detail(self, cr: ChangeRequest) -> None:
        """渲染变更单详情"""
        # 标题行：编号 + 状态徽标
        header_row = QHBoxLayout()
        header_row.setSpacing(8)
        number_label = QLabel(cr.change_number)
        number_label.setObjectName("detailNumber")
        header_row.addWidget(number_label)
        badge = _make_status_badge_label(cr.status, self._content_widget)
        header_row.addWidget(badge)
        header_row.addStretch(1)
        self._content_layout.addLayout(header_row)

        # 基本信息
        self._add_section_header("基本信息")
        self._add_info_row("项目编号", cr.project_id)
        self._add_info_row("项目名称", cr.project_name or "—")
        self._add_info_row("技术领域", DOMAINS.get(cr.domain, cr.domain or "—"))
        self._add_info_row(
            "业务性质",
            BUSINESS_NATURES.get(cr.business_nature, cr.business_nature or "—"),
        )
        self._add_info_row("影响范围", _format_impact_scope(cr.impact_scope))
        self._add_info_row("申请人", cr.applicant or "—")
        self._add_info_row("创建日期", cr.apply_date or "—")
        self._add_info_row("计划日期", cr.planned_date or "—")
        self._add_info_row("紧急程度", _format_urgency(cr.urgency))

        # 背景全文
        self._add_section_header("变更背景")
        self._add_full_text(cr.background or "—")

        # 必要性全文
        self._add_section_header("变更必要性")
        self._add_full_text(cr.necessity or "—")

        # 参考依据
        self._add_section_header("参考依据")
        self._add_full_text(cr.references or "—")

        # 状态流转按钮
        self._render_transition_buttons(cr)

        # 底部弹簧
        self._content_layout.addStretch(1)

    def _add_section_header(self, title: str) -> None:
        """添加章节标题"""
        label = QLabel(title)
        label.setObjectName("sectionHeader")
        self._content_layout.addWidget(label)

    def _add_info_row(self, label_text: str, value_text: str) -> None:
        """添加一行信息（标签: 值）"""
        row = QHBoxLayout()
        row.setSpacing(8)
        label = QLabel(label_text)
        label.setObjectName("fieldLabel")
        label.setFixedWidth(80)
        value = QLabel(value_text)
        value.setObjectName("fieldValue")
        value.setWordWrap(True)
        row.addWidget(label)
        row.addWidget(value, 1)
        self._content_layout.addLayout(row)

    def _add_full_text(self, text: str) -> None:
        """添加全文展示（带背景的文本块）"""
        label = QLabel(text)
        label.setObjectName("fullText")
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._content_layout.addWidget(label)

    def _render_transition_buttons(self, cr: ChangeRequest) -> None:
        """根据当前状态渲染流转按钮"""
        buttons_config = _TRANSITION_BUTTONS.get(cr.status, [])
        if not buttons_config:
            return

        self._add_section_header("状态流转")
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        for label_text, target_status in buttons_config:
            btn = QPushButton(label_text)
            btn.setObjectName("transitionBtn")
            if target_status == "rejected":
                btn.setObjectName("rejectBtn")
            btn.clicked.connect(
                lambda checked=False, t=target_status: self._on_transition_clicked(t)
            )
            btn_row.addWidget(btn)
        btn_row.addStretch(1)
        self._content_layout.addLayout(btn_row)

    # ── 流转处理 ─────────────────────────────────────────

    def _on_transition_clicked(self, target_status: str) -> None:
        """流转按钮点击 → 弹出 TransitionDialog"""
        if self._current_change is None:
            log.warning("流转按钮点击但当前无选中变更单")
            return

        change_number = self._current_change.change_number
        current_status = self._current_change.status
        log.info(
            "发起状态流转: %s %s → %s",
            change_number, current_status, target_status,
        )

        dialog = TransitionDialog(
            change_number=change_number,
            current_status=current_status,
            target_status=target_status,
            change_service=self._change_service,
            parent=self,
        )
        dialog.transition_completed.connect(self._on_transition_done)
        dialog.exec()

    def _on_transition_done(self, change_number: str) -> None:
        """TransitionDialog 流转成功回调 → 重新加载详情 + 发射信号"""
        log.info("状态流转完成，刷新详情: %s", change_number)
        self.load_change(change_number)
        self.transition_completed.emit(change_number)
