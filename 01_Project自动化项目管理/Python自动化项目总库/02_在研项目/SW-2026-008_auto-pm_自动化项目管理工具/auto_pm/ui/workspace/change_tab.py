"""项目工作区 - 变更 Tab

展示当前项目的变更单列表，支持创建/筛选/详情展开/状态流转。

布局：
    ┌─────────────────────────────────────────────────────────┐
    │ [+ 创建变更单]    筛选: [全部状态▼] [全部领域▼]            │
    ├─────────────────────────────────────────────────────────┤
    │ ┌─ CHG-XXX-001 ─────────────── [状态徽标] ───┐          │
    │ │ 领域: 代码 | 性质: 修正 | 范围: 局部          │          │
    │ │ 申请人: fubai | 创建: 2026-06-18             │          │
    │ │ 背景: 修复...                                │          │
    │ │ [详情] [流转]                                 │          │
    │ └─────────────────────────────────────────────┘          │
    └─────────────────────────────────────────────────────────┘

信号：
    change_updated() - 变更单有变动时发射（通知 MainWindow 刷新计数）
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
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
    STATUS_FLOW,
    STATUS_LABELS,
    ChangeSummary,
)
from auto_pm.core.project_service import ProjectService
from auto_pm.logging.logging import setup_logger
from auto_pm.ui.dialogs.create_change_dialog import CreateChangeDialog
from auto_pm.ui.dialogs.transition_dialog import TransitionDialog

log = setup_logger(log_level="INFO", app_name="auto_pm")

__all__ = ["ChangeTab"]

# 状态徽标颜色：(背景色, 前景色)
# 对齐任务要求：草稿灰/待审批蓝/已审批黄/实施中蓝/已完成绿/已归档灰
_STATUS_BADGE_COLOR: dict[str, tuple[str, str]] = {
    "draft": ("#95a5a6", "#ffffff"),  # 灰
    "submitted": ("#4a90d9", "#ffffff"),  # 蓝
    "under_review": ("#4a90d9", "#ffffff"),  # 蓝
    "approved": ("#f39c12", "#ffffff"),  # 黄
    "conditionally_approved": ("#f39c12", "#ffffff"),  # 黄
    "rejected": ("#e74c3c", "#ffffff"),  # 红
    "implementing": ("#4a90d9", "#ffffff"),  # 蓝
    "pending_acceptance": ("#4a90d9", "#ffffff"),  # 蓝
    "accepting": ("#4a90d9", "#ffffff"),  # 蓝
    "completed": ("#27ae60", "#ffffff"),  # 绿
    "closed": ("#95a5a6", "#ffffff"),  # 灰
}

# 状态筛选选项：(标签, 状态码或 None)
_STATUS_FILTER_OPTIONS: list[tuple[str, str | None]] = [
    ("全部状态", None),
    ("草稿", "draft"),
    ("待审批", "submitted"),
    ("已审批", "approved"),
    ("实施中", "implementing"),
    ("已完成", "completed"),
    ("已归档", "closed"),
]

_TAB_STYLE = """
QFrame#changeTab { background: #fafafa; }
QPushButton#createBtn {
    font-size: 13px; color: #ffffff;
    background: #4a90d9; border: none;
    border-radius: 4px; padding: 6px 16px;
}
QPushButton#createBtn:hover { background: #357abd; }
QLabel#filterLabel { font-size: 12px; color: #555; }
QComboBox { font-size: 12px; padding: 4px 8px; }
QFrame#changeCard {
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
}
QFrame#changeCard:hover { border-color: #4a90d9; }
QLabel#changeNumber { font-size: 14px; font-weight: bold; color: #222; }
QLabel#changeMeta { font-size: 12px; color: #666; }
QLabel#changeSummary { font-size: 12px; color: #555; }
QLabel#detailSection {
    font-size: 12px; color: #444;
    background: #f8f9fa; padding: 8px;
    border-radius: 4px; border: 1px solid #e8e8e8;
}
QLabel#emptyHint {
    color: #999; font-size: 14px;
    padding: 60px;
}
QPushButton#cardBtn {
    font-size: 11px; color: #4a90d9;
    background: #ffffff; border: 1px solid #4a90d9;
    border-radius: 3px; padding: 3px 10px;
}
QPushButton#cardBtn:hover { background: #f0f5ff; }
QPushButton#cardBtn:disabled { color: #ccc; border-color: #ddd; }
"""

# 背景摘要最大字符数（约 2 行）
_SUMMARY_MAX_CHARS = 100


def _truncate(text: str, max_chars: int = _SUMMARY_MAX_CHARS) -> str:
    """截断文本到指定长度，超出追加省略号；折叠空白为单空格。"""
    if not text:
        return ""
    cleaned = " ".join(text.split())
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[:max_chars] + "…"


def _make_status_badge_label(status: str, parent: QWidget | None = None) -> QLabel:
    """创建状态徽标 QLabel（彩色背景）"""
    label = QLabel(parent)
    text = STATUS_LABELS.get(status, status)
    bg, fg = _STATUS_BADGE_COLOR.get(status, ("#95a5a6", "#ffffff"))
    label.setText(text)
    label.setStyleSheet(
        f"background: {bg}; color: {fg}; "
        "font-size: 10px; font-weight: bold; "
        "padding: 2px 8px; border-radius: 3px;"
    )
    return label


def _format_impact_scope(scopes: list[str]) -> str:
    """格式化影响范围列表为中文标签字符串"""
    if not scopes:
        return "—"
    parts = [IMPACT_SCOPES.get(s, s) for s in scopes]
    return "、".join(parts)


class _ChangeCard(QFrame):
    """变更单卡片

    展示变更单摘要信息，支持详情展开和状态流转。
    流转按钮点击时发射 transition_requested(change_number) 信号。
    """

    transition_requested = Signal(str)

    def __init__(
        self,
        summary: ChangeSummary,
        change_service: ChangeService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("changeCard")
        self._summary = summary
        self._change_service = change_service
        self._detail_visible = False
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(6)

        # 第一行：编号（加粗） + 状态徽标（右对齐）
        top_row = QHBoxLayout()
        top_row.setSpacing(8)
        number_label = QLabel(self._summary.change_number)
        number_label.setObjectName("changeNumber")
        top_row.addWidget(number_label)
        top_row.addStretch(1)
        badge = _make_status_badge_label(self._summary.status, self)
        top_row.addWidget(badge)
        layout.addLayout(top_row)

        # 第二行：领域 / 性质 / 范围
        domain_text = DOMAINS.get(self._summary.domain, self._summary.domain or "—")
        nature_text = BUSINESS_NATURES.get(
            self._summary.business_nature, self._summary.business_nature or "—"
        )
        scope_text = _format_impact_scope(self._summary.impact_scope)
        meta1 = QLabel(f"领域: {domain_text} | 性质: {nature_text} | 范围: {scope_text}")
        meta1.setObjectName("changeMeta")
        layout.addWidget(meta1)

        # 第三行：申请人 / 创建日期
        applicant = self._summary.applicant or "—"
        apply_date = self._summary.apply_date or "—"
        meta2 = QLabel(f"申请人: {applicant} | 创建: {apply_date}")
        meta2.setObjectName("changeMeta")
        layout.addWidget(meta2)

        # 第四行：背景摘要（2 行截断）
        summary_text = _truncate(self._summary.title)
        if summary_text:
            summary_label = QLabel(summary_text)
            summary_label.setObjectName("changeSummary")
            summary_label.setWordWrap(True)
            summary_label.setMaximumHeight(40)
            layout.addWidget(summary_label)

        # 详情展开区域（默认隐藏）
        self._detail_section = QWidget()
        self._detail_section.setVisible(False)
        self._detail_layout = QVBoxLayout(self._detail_section)
        self._detail_layout.setContentsMargins(0, 4, 0, 0)
        self._detail_layout.setSpacing(4)
        layout.addWidget(self._detail_section)

        # 按钮行
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self._detail_btn = QPushButton("详情")
        self._detail_btn.setObjectName("cardBtn")
        self._detail_btn.clicked.connect(self._toggle_detail)
        btn_row.addWidget(self._detail_btn)

        self._transition_btn = QPushButton("流转")
        self._transition_btn.setObjectName("cardBtn")
        self._transition_btn.clicked.connect(self._on_transition_clicked)
        available = STATUS_FLOW.get(self._summary.status, set())
        if not available:
            self._transition_btn.setEnabled(False)
        btn_row.addWidget(self._transition_btn)
        btn_row.addStretch(1)
        layout.addLayout(btn_row)

    def _toggle_detail(self) -> None:
        """展开/收起详情"""
        self._detail_visible = not self._detail_visible
        self._detail_btn.setText("收起" if self._detail_visible else "详情")
        if self._detail_visible:
            self._load_detail()
        self._detail_section.setVisible(self._detail_visible)

    def _load_detail(self) -> None:
        """加载完整详情（背景/必要性/影响范围）"""
        self._clear_detail()

        try:
            cr = self._change_service.get_change_request(self._summary.change_number)
        except Exception as e:
            log.warning("加载变更单详情失败 %s: %s", self._summary.change_number, e)
            cr = None

        if cr is None:
            label = QLabel("详情加载失败")
            label.setObjectName("detailSection")
            self._detail_layout.addWidget(label)
            return

        sections = [
            ("背景", cr.background or "—"),
            ("必要性", cr.necessity or "—"),
            ("影响范围", _format_impact_scope(cr.impact_scope)),
        ]
        for title, content in sections:
            label = QLabel(f"【{title}】\n{content}")
            label.setObjectName("detailSection")
            label.setWordWrap(True)
            self._detail_layout.addWidget(label)

    def _clear_detail(self) -> None:
        """清空详情区域"""
        while self._detail_layout.count():
            item = self._detail_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _on_transition_clicked(self) -> None:
        """流转按钮点击 → 发射 transition_requested 信号"""
        self.transition_requested.emit(self._summary.change_number)


class ChangeTab(QWidget):
    """项目工作区 - 变更 Tab

    展示当前项目的变更单列表，支持创建/筛选/详情展开/状态流转。
    变更有变动时发射 change_updated() 信号。
    """

    change_updated = Signal()

    def __init__(
        self,
        change_service: ChangeService,
        project_service: ProjectService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._change_service = change_service
        self._project_service = project_service
        self._project_id: str | None = None
        self._status_filter: str | None = None
        self._domain_filter: str | None = None
        self._build_ui()

    # ── UI 构建 ────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.setObjectName("changeTab")
        self.setStyleSheet(_TAB_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        toolbar = self._build_toolbar()
        layout.addWidget(toolbar)

        # 变更单列表（滚动区域）
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)

        self._list_container = QWidget()
        self._list_layout = QVBoxLayout(self._list_container)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(8)
        self._list_layout.addStretch(1)
        self._scroll.setWidget(self._list_container)
        layout.addWidget(self._scroll, 1)

        # 空状态提示
        self._empty_hint = QLabel("暂无变更单")
        self._empty_hint.setObjectName("emptyHint")
        self._empty_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_hint.setVisible(False)
        layout.addWidget(self._empty_hint)

    def _build_toolbar(self) -> QWidget:
        """构建顶部工具栏：创建按钮 + 筛选下拉"""
        toolbar = QWidget()
        h = QHBoxLayout(toolbar)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(10)

        self._create_btn = QPushButton("+ 创建变更单")
        self._create_btn.setObjectName("createBtn")
        self._create_btn.clicked.connect(self._on_create_change)
        h.addWidget(self._create_btn)

        h.addStretch(1)

        status_label = QLabel("筛选:")
        status_label.setObjectName("filterLabel")
        h.addWidget(status_label)

        self._status_combo = QComboBox()
        for label, status_code in _STATUS_FILTER_OPTIONS:
            self._status_combo.addItem(label, status_code)
        self._status_combo.currentIndexChanged.connect(self._on_status_filter_changed)
        h.addWidget(self._status_combo)

        self._domain_combo = QComboBox()
        self._domain_combo.addItem("全部领域", None)
        for code, label in DOMAINS.items():
            self._domain_combo.addItem(f"{code} {label}", code)
        self._domain_combo.currentIndexChanged.connect(self._on_domain_filter_changed)
        h.addWidget(self._domain_combo)

        return toolbar

    # ── 数据加载 ──────────────────────────────────────────

    def load_project(self, project_id: str) -> None:
        """加载指定项目的变更单"""
        self._project_id = project_id
        log.info("变更Tab加载项目: %s", project_id)
        self._refresh_list()

    def _refresh_list(self) -> None:
        """刷新变更单列表"""
        if self._project_id is None:
            return

        self._clear_list()

        try:
            summaries = self._change_service.list_change_requests(
                self._project_id,
                status=self._status_filter,
                domain=self._domain_filter,
            )
        except Exception as e:
            log.error("变更Tab加载变更单列表失败: %s", e, exc_info=True)
            summaries = []

        if not summaries:
            self._scroll.setVisible(False)
            self._empty_hint.setVisible(True)
            return

        self._scroll.setVisible(True)
        self._empty_hint.setVisible(False)

        for summary in summaries:
            card = _ChangeCard(summary, self._change_service, self._list_container)
            card.transition_requested.connect(self._on_transition)
            self._list_layout.insertWidget(self._list_layout.count() - 1, card)

    def _clear_list(self) -> None:
        """清空列表中的卡片（保留底部弹簧）"""
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def _get_cards(self) -> list[_ChangeCard]:
        """获取当前列表中的所有卡片（用于测试/外部检查）"""
        cards: list[_ChangeCard] = []
        for i in range(self._list_layout.count()):
            item = self._list_layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if isinstance(widget, _ChangeCard):
                    cards.append(widget)
        return cards

    # ── 筛选 ─────────────────────────────────────────────

    def _on_status_filter_changed(self, _index: int) -> None:
        """状态筛选下拉变化"""
        self._status_filter = self._status_combo.currentData()
        self._refresh_list()

    def _on_domain_filter_changed(self, _index: int) -> None:
        """领域筛选下拉变化"""
        self._domain_filter = self._domain_combo.currentData()
        self._refresh_list()

    # ── 创建变更单 ───────────────────────────────────────

    def _on_create_change(self) -> None:
        """创建变更单按钮 → 弹出 CreateChangeDialog"""
        log.info("变更Tab: 打开创建变更单对话框")
        dialog = CreateChangeDialog(
            project_service=self._project_service,
            change_service=self._change_service,
            parent=self,
        )
        dialog.change_created.connect(self._on_change_created)
        dialog.exec()

    def _on_change_created(self, project_id: str) -> None:
        """变更单创建成功 → 刷新列表 + 发射 change_updated()"""
        log.info("变更Tab: 变更单已创建（项目 %s），刷新列表", project_id)
        self._refresh_list()
        self.change_updated.emit()

    # ── 状态流转 ─────────────────────────────────────────

    def _on_transition(self, change_number: str) -> None:
        """流转按钮点击 → 弹出 TransitionDialog"""
        log.info("变更Tab: 发起状态流转 %s", change_number)
        try:
            cr = self._change_service.get_change_request(change_number)
        except Exception as e:
            log.error("加载变更单失败 %s: %s", change_number, e, exc_info=True)
            return

        if cr is None:
            log.warning("变更单未找到: %s", change_number)
            return

        available_targets = STATUS_FLOW.get(cr.status, set())
        if not available_targets:
            log.info("变更单 %s 处于终态 %s，无可用流转", change_number, cr.status)
            return

        if len(available_targets) == 1:
            target = next(iter(available_targets))
            self._open_transition_dialog(change_number, cr.status, target)
        else:
            menu = QMenu(self)
            for target in sorted(available_targets):
                label = STATUS_LABELS.get(target, target)
                action = menu.addAction(f"→ {label}")
                action.triggered.connect(
                    lambda checked=False, t=target: self._open_transition_dialog(
                        change_number, cr.status, t
                    )
                )
            menu.exec(QCursor.pos())

    def _open_transition_dialog(
        self, change_number: str, current_status: str, target_status: str
    ) -> None:
        """打开状态流转对话框"""
        dialog = TransitionDialog(
            change_number=change_number,
            current_status=current_status,
            target_status=target_status,
            change_service=self._change_service,
            parent=self,
        )
        dialog.transition_completed.connect(self._on_transition_completed)
        dialog.exec()

    def _on_transition_completed(self, change_number: str) -> None:
        """状态流转完成 → 刷新列表 + 发射 change_updated()"""
        log.info("变更Tab: 状态流转完成 %s，刷新列表", change_number)
        self._refresh_list()
        self.change_updated.emit()
