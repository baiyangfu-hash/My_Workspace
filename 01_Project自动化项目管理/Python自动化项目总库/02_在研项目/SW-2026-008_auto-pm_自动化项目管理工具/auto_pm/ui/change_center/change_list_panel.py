"""变更中心 - 变更单列表面板

顶部状态 Tab 筛选栏（全部/草稿/待审批/已审批/实施中/已完成/已归档），
下方变更单列表（QListWidget + 自定义 widget），每项展示编号/状态徽标/
项目/领域/性质/创建日期/背景摘要。点击发射 change_selected(change_number)。

状态 Tab 与 STATUS_FLOW 状态码映射（简化分组，对齐 GUI 原型设计 V2.0 §6）：
    全部 → None
    草稿 → draft
    待审批 → submitted
    已审批 → approved
    实施中 → implementing
    已完成 → completed
    已归档 → closed
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from auto_pm.change.change_service import ChangeService
from auto_pm.change.models import (
    BUSINESS_NATURES,
    DOMAINS,
    STATUS_LABELS,
    ChangeSummary,
)
from auto_pm.logging.logging import setup_logger

log = setup_logger(log_level="INFO", app_name="auto_pm")

__all__ = ["ChangeListPanel"]

# 状态 Tab：(tab_id, 中文标签, 对应状态码或 None)
# 顺序对齐任务要求：全部/草稿/待审批/已审批/实施中/已完成/已归档
_STATUS_TABS: list[tuple[str, str, str | None]] = [
    ("all", "全部", None),
    ("draft", "草稿", "draft"),
    ("submitted", "待审批", "submitted"),
    ("approved", "已审批", "approved"),
    ("implementing", "实施中", "implementing"),
    ("completed", "已完成", "completed"),
    ("closed", "已归档", "closed"),
]

# 状态徽标颜色：(背景色, 前景色)
_STATUS_BADGE_COLOR: dict[str, tuple[str, str]] = {
    "draft": ("#95a5a6", "#ffffff"),       # 灰色
    "submitted": ("#4a90d9", "#ffffff"),   # 蓝色
    "under_review": ("#4a90d9", "#ffffff"),
    "approved": ("#27ae60", "#ffffff"),    # 绿色
    "conditionally_approved": ("#27ae60", "#ffffff"),
    "rejected": ("#e74c3c", "#ffffff"),    # 红色
    "implementing": ("#f39c12", "#ffffff"),  # 橙色
    "pending_acceptance": ("#f39c12", "#ffffff"),
    "accepting": ("#f39c12", "#ffffff"),
    "completed": ("#16a085", "#ffffff"),   # 深绿
    "closed": ("#7f8c8d", "#ffffff"),      # 深灰
}

_PANEL_STYLE = """
QFrame#changeListPanel { background: #fafafa; }
QLabel#panelTitle { font-size: 14px; font-weight: bold; color: #222; }
QPushButton#statusTab {
    font-size: 12px; color: #555;
    padding: 4px 10px; border: 1px solid #d0d0d0;
    border-radius: 3px; background: #ffffff;
}
QPushButton#statusTab:hover { background: #f0f5ff; border-color: #4a90d9; }
QPushButton#statusTab:checked {
    background: #4a90d9; color: #ffffff;
    border-color: #4a90d9; font-weight: bold;
}
QListWidget#changeList {
    background: #fafafa; border: none;
    outline: none;
}
QListWidget#changeList::item {
    border-bottom: 1px solid #e8e8e8;
    padding: 0px;
}
QListWidget#changeList::item:selected {
    background: #e6f0ff;
}
QFrame#changeItem {
    background: transparent;
    border: none;
}
QFrame#changeItem:hover { background: #f5f9ff; }
QLabel#itemNumber { font-size: 13px; font-weight: bold; color: #222; }
QLabel#itemMeta { font-size: 11px; color: #666; }
QLabel#itemDate { font-size: 11px; color: #999; }
QLabel#itemSummary {
    font-size: 11px; color: #555;
}
QLabel#emptyHint {
    color: #999; font-size: 13px;
    padding: 40px;
}
"""

# 背景摘要最大字符数（单行截断）
_SUMMARY_MAX_CHARS = 50


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
        "padding: 2px 6px; border-radius: 3px;"
    )
    return label


class _ChangeItemWidget(QFrame):
    """变更单列表项 widget（展示编号/状态/项目/领域/性质/日期/背景摘要）"""

    def __init__(self, summary: ChangeSummary, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("changeItem")
        self._summary = summary
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        # 第一行：编号（加粗） + 状态徽标（右对齐）
        top_row = QHBoxLayout()
        top_row.setSpacing(6)
        number_label = QLabel(self._summary.change_number)
        number_label.setObjectName("itemNumber")
        top_row.addWidget(number_label)
        top_row.addStretch(1)
        badge = _make_status_badge_label(self._summary.status, self)
        top_row.addWidget(badge)
        layout.addLayout(top_row)

        # 第二行：项目编号 + 项目名
        project_text = self._summary.project_id
        if self._summary.project_name and self._summary.project_name != self._summary.project_id:
            project_text = f"{self._summary.project_id} · {self._summary.project_name}"
        project_label = QLabel(project_text)
        project_label.setObjectName("itemMeta")
        layout.addWidget(project_label)

        # 第三行：领域 / 性质
        domain_label_text = DOMAINS.get(self._summary.domain, self._summary.domain)
        nature_label_text = BUSINESS_NATURES.get(
            self._summary.business_nature, self._summary.business_nature
        )
        meta_label = QLabel(f"{domain_label_text} / {nature_label_text}")
        meta_label.setObjectName("itemMeta")
        layout.addWidget(meta_label)

        # 第四行：创建日期
        date_label = QLabel(f"创建: {self._summary.apply_date}")
        date_label.setObjectName("itemDate")
        layout.addWidget(date_label)

        # 第五行：背景摘要（1 行截断）
        summary_text = _truncate(self._summary.title)
        if summary_text:
            summary_label = QLabel(summary_text)
            summary_label.setObjectName("itemSummary")
            summary_label.setWordWrap(False)
            layout.addWidget(summary_label)


class ChangeListPanel(QWidget):
    """变更单列表面板

    顶部状态 Tab 筛选栏 + 变更单列表。点击列表项发射 change_selected(change_number)。
    """

    change_selected = Signal(str)

    def __init__(
        self,
        change_service: ChangeService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._change_service = change_service
        self._summaries: list[ChangeSummary] = []
        self._current_status: str | None = None  # 当前状态筛选（None=全部）
        self._current_domain: str | None = None  # 当前领域筛选（None=全部）
        self._build_ui()

    # ── UI 构建 ────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.setObjectName("changeListPanel")
        self.setStyleSheet(_PANEL_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # 状态 Tab 筛选栏
        tab_row = QHBoxLayout()
        tab_row.setSpacing(4)
        tab_row.setContentsMargins(0, 0, 0, 0)
        self._status_tabs: dict[str, QPushButton] = {}
        for tab_id, label, status_code in _STATUS_TABS:
            btn = QPushButton(label)
            btn.setObjectName("statusTab")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked=False, s=status_code: self.set_status_filter(s))
            self._status_tabs[tab_id] = btn
            tab_row.addWidget(btn)
        tab_row.addStretch(1)
        layout.addLayout(tab_row)

        # 变更单列表
        self._list_widget = QListWidget()
        self._list_widget.setObjectName("changeList")
        self._list_widget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self._list_widget.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self._list_widget, 1)

        # 空状态提示
        self._empty_hint = QLabel("暂无变更单")
        self._empty_hint.setObjectName("emptyHint")
        self._empty_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_hint.setVisible(False)
        layout.addWidget(self._empty_hint)

        # 默认选中"全部" Tab
        self._status_tabs["all"].setChecked(True)

    # ── 数据加载 ──────────────────────────────────────────

    def refresh(self) -> None:
        """加载所有变更单（应用当前状态/领域筛选）"""
        try:
            self._summaries = self._change_service.list_all_changes(
                status=self._current_status,
                domain=self._current_domain,
            )
        except Exception as e:
            log.error("变更中心加载变更单列表失败: %s", e, exc_info=True)
            self._summaries = []
        self._render_list()

    def _render_list(self) -> None:
        """重新渲染列表"""
        self._list_widget.clear()

        if not self._summaries:
            self._list_widget.setVisible(False)
            self._empty_hint.setVisible(True)
            return

        self._list_widget.setVisible(True)
        self._empty_hint.setVisible(False)

        for summary in self._summaries:
            item = QListWidgetItem(self._list_widget)
            widget = _ChangeItemWidget(summary, self._list_widget)
            item.setSizeHint(widget.sizeHint())
            item.setData(Qt.ItemDataRole.UserRole, summary.change_number)
            self._list_widget.addItem(item)
            self._list_widget.setItemWidget(item, widget)

    # ── 筛选 ─────────────────────────────────────────────

    def set_status_filter(self, status: str | None) -> None:
        """设置状态筛选（None=全部），刷新 Tab 选中态并重新加载"""
        self._current_status = status
        # 更新 Tab 选中态
        for tab_id, _label, status_code in _STATUS_TABS:
            btn = self._status_tabs[tab_id]
            btn.setChecked(status_code == status)
        self.refresh()

    def set_domain_filter(self, domain: str | None) -> None:
        """设置领域筛选（None=全部）并重新加载"""
        self._current_domain = domain
        self.refresh()

    # ── 信号处理 ─────────────────────────────────────────

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        """列表项点击 → 发射 change_selected(change_number)"""
        change_number = item.data(Qt.ItemDataRole.UserRole)
        if change_number:
            log.debug("选中变更单: %s", change_number)
            self.change_selected.emit(change_number)

    # ── 辅助 ─────────────────────────────────────────────

    def get_current_selection(self) -> str | None:
        """获取当前选中的变更单编号（无选中返回 None）"""
        items = self._list_widget.selectedItems()
        if not items:
            return None
        return items[0].data(Qt.ItemDataRole.UserRole)

    def select_change(self, change_number: str) -> bool:
        """选中指定变更单（用于外部联动），返回是否选中成功"""
        for i in range(self._list_widget.count()):
            item = self._list_widget.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == change_number:
                self._list_widget.setCurrentItem(item)
                return True
        return False
