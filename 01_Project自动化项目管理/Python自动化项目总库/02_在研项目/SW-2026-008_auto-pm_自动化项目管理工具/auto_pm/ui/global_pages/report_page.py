"""报告中心全局页

展示项目概览与变更统计的柱状图卡片：
    ┌─ 项目概览 ─┐ ┌─ 阶段分布 ─┐
    ┌─ 业务线分布 ─┐ ┌─ 变更统计 ─┐

柱状图用 QProgressBar（水平条）实现，简单可靠。
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from auto_pm.core.report_service import ReportService
from auto_pm.logging.logging import setup_logger

log = setup_logger(log_level="INFO", app_name="auto_pm")

__all__ = ["ReportPage"]

# ── 中文映射 ──────────────────────────────────────────────

# 技术栈
_STACK_LABELS: dict[str, str] = {
    "plc": "PLC",
    "python": "Python",
    "unknown": "未知",
}
_STACK_ORDER: list[str] = ["plc", "python", "unknown"]

# 阶段
_PHASE_LABELS: dict[str, str] = {
    "developing": "开发中",
    "commissioning": "调试中",
    "production": "生产中",
    "archived": "已归档",
}
_PHASE_ORDER: list[str] = ["developing", "commissioning", "production", "archived"]

# 业务线
_BL_ORDER: list[str] = ["SW", "DJ", "ZD", "XT", "WX"]

# 变更状态
_STATUS_LABELS: dict[str, str] = {
    "draft": "草稿",
    "submitted": "已提交",
    "under_review": "审核中",
    "approved": "已批准",
    "conditionally_approved": "有条件批准",
    "rejected": "已驳回",
    "implementing": "实施中",
    "pending_acceptance": "待验收",
    "accepting": "验收中",
    "completed": "已完成",
    "closed": "已关闭",
}
# 状态展示顺序（常见状态优先）
_STATUS_ORDER: list[str] = [
    "draft",
    "submitted",
    "under_review",
    "approved",
    "implementing",
    "pending_acceptance",
    "accepting",
    "completed",
    "closed",
    "conditionally_approved",
    "rejected",
]

# ── 样式 ──────────────────────────────────────────────────

_PAGE_STYLE = """
QWidget#reportPage { background: #fafafa; }
QLabel#reportTitle { font-size: 18px; font-weight: bold; color: #222; }
QLabel#reportSubtitle { font-size: 12px; color: #999; }
QLabel#summaryLabel { font-size: 14px; font-weight: bold; color: #222; }
QLabel#rowLabel { font-size: 12px; color: #555; }
QLabel#countLabel { font-size: 12px; font-weight: bold; color: #222; }
QLabel#emptyHint { color: #999; font-size: 13px; }
QGroupBox#reportCard {
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    margin-top: 14px;
    font-size: 13px;
    font-weight: bold;
    color: #333;
}
QGroupBox#reportCard::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 8px;
    color: #4a90d9;
}
QProgressBar#statBar {
    border: 1px solid #d0d0d0;
    border-radius: 3px;
    background: #f0f0f0;
    text-align: center;
    height: 14px;
}
QProgressBar#statBar::chunk {
    background: #4a90d9;
    border-radius: 2px;
}
"""


class ReportPage(QWidget):
    """报告中心全局页

    2×2 卡片布局展示项目/变更统计柱状图。
    通过 ReportService 加载数据，refresh() 重新渲染。
    """

    def __init__(self, report_service: ReportService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._report_service = report_service
        self._build_ui()

    # ── UI 构建 ────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.setObjectName("reportPage")
        self.setStyleSheet(_PAGE_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        # 标题
        title = QLabel("报告中心")
        title.setObjectName("reportTitle")
        layout.addWidget(title)

        subtitle = QLabel("项目与变更统计概览")
        subtitle.setObjectName("reportSubtitle")
        layout.addWidget(subtitle)

        # 2×2 卡片网格
        cards_widget = QWidget()
        grid = QGridLayout(cards_widget)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(10)

        self._project_card = self._make_card("项目概览")
        self._phase_card = self._make_card("阶段分布")
        self._bl_card = self._make_card("业务线分布")
        self._change_card = self._make_card("变更统计")

        grid.addWidget(self._project_card, 0, 0)
        grid.addWidget(self._phase_card, 0, 1)
        grid.addWidget(self._bl_card, 1, 0)
        grid.addWidget(self._change_card, 1, 1)

        # 等宽列
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setRowStretch(0, 1)
        grid.setRowStretch(1, 1)

        layout.addWidget(cards_widget, 1)

    @staticmethod
    def _make_card(title: str) -> QGroupBox:
        """创建统计卡片容器（QGroupBox）"""
        card = QGroupBox(title)
        card.setObjectName("reportCard")
        v = QVBoxLayout(card)
        v.setContentsMargins(12, 16, 12, 12)
        v.setSpacing(6)
        return card

    # ── 公共方法 ─────────────────────────────────────────

    def refresh(self) -> None:
        """重新加载数据并渲染所有卡片"""
        log.info("报告中心刷新")
        try:
            project_data = self._report_service.get_project_overview()
            change_data = self._report_service.get_change_overview()
        except Exception as e:
            log.error("报告中心加载数据失败: %s", e)
            self._render_error(self._project_card, str(e))
            self._render_error(self._phase_card, str(e))
            self._render_error(self._bl_card, str(e))
            self._render_error(self._change_card, str(e))
            return

        self._render_project_overview(project_data)
        self._render_phase_distribution(project_data)
        self._render_bl_distribution(project_data)
        self._render_change_overview(change_data)

    # ── 渲染方法 ─────────────────────────────────────────

    def _render_project_overview(self, data: dict) -> None:
        """渲染项目概览卡片（总数 + 按 stack）"""
        self._clear_card(self._project_card)
        v = self._project_card.layout()

        total = data.get("total", 0)
        v.addWidget(self._make_summary_label(f"总项目数: {total}"))

        by_stack: dict = data.get("by_stack", {})
        max_val = max(by_stack.values()) if by_stack else 0
        for key in _STACK_ORDER:
            count = by_stack.get(key, 0)
            label = _STACK_LABELS.get(key, key)
            v.addWidget(self._make_bar_row(label, count, max_val))

        v.addStretch(1)

    def _render_phase_distribution(self, data: dict) -> None:
        """渲染阶段分布卡片（按 phase）"""
        self._clear_card(self._phase_card)
        v = self._phase_card.layout()

        by_phase: dict = data.get("by_phase", {})
        max_val = max(by_phase.values()) if by_phase else 0
        for key in _PHASE_ORDER:
            count = by_phase.get(key, 0)
            label = _PHASE_LABELS.get(key, key)
            v.addWidget(self._make_bar_row(label, count, max_val))

        v.addStretch(1)

    def _render_bl_distribution(self, data: dict) -> None:
        """渲染业务线分布卡片（按 business_line）"""
        self._clear_card(self._bl_card)
        v = self._bl_card.layout()

        by_bl: dict = data.get("by_business_line", {})
        max_val = max(by_bl.values()) if by_bl else 0
        for key in _BL_ORDER:
            count = by_bl.get(key, 0)
            v.addWidget(self._make_bar_row(key, count, max_val))

        v.addStretch(1)

    def _render_change_overview(self, data: dict) -> None:
        """渲染变更统计卡片（总数 + 按状态）"""
        self._clear_card(self._change_card)
        v = self._change_card.layout()

        total = data.get("total", 0)
        v.addWidget(self._make_summary_label(f"总变更: {total}"))

        by_status: dict = data.get("by_status", {})
        max_val = max(by_status.values()) if by_status else 0
        # 按预定义顺序渲染存在的状态
        rendered_keys: set[str] = set()
        for key in _STATUS_ORDER:
            if key in by_status:
                count = by_status[key]
                label = _STATUS_LABELS.get(key, key)
                v.addWidget(self._make_bar_row(label, count, max_val))
                rendered_keys.add(key)
        # 渲染未在预定义顺序中的状态（兜底）
        for key, count in by_status.items():
            if key not in rendered_keys:
                label = _STATUS_LABELS.get(key, key or "未设置")
                v.addWidget(self._make_bar_row(label, count, max_val))

        v.addStretch(1)

    # ── 行组件构造 ───────────────────────────────────────

    @staticmethod
    def _make_summary_label(text: str) -> QLabel:
        """创建摘要标签（如"总项目数: 8"）"""
        lbl = QLabel(text)
        lbl.setObjectName("summaryLabel")
        return lbl

    @staticmethod
    def _make_bar_row(label_text: str, value: int, max_value: int) -> QWidget:
        """创建柱状图行：[标签] [进度条] [数值]

        Args:
            label_text: 行标签文本（如"PLC"）
            value: 当前值
            max_value: 该组最大值（用于进度条比例）
        """
        row = QWidget()
        h = QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(8)

        lbl = QLabel(label_text)
        lbl.setObjectName("rowLabel")
        lbl.setMinimumWidth(70)
        lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        h.addWidget(lbl)

        bar = QProgressBar()
        bar.setObjectName("statBar")
        # max_value 为 0 时设为 1，避免进度条满格
        bar.setMaximum(max_value if max_value > 0 else 1)
        bar.setValue(value)
        bar.setTextVisible(False)
        h.addWidget(bar, 1)

        count = QLabel(str(value))
        count.setObjectName("countLabel")
        count.setMinimumWidth(30)
        count.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        h.addWidget(count)

        return row

    @staticmethod
    def _make_empty_hint(text: str) -> QLabel:
        """创建空状态提示"""
        lbl = QLabel(text)
        lbl.setObjectName("emptyHint")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return lbl

    def _render_error(self, card: QGroupBox, message: str) -> None:
        """渲染错误状态"""
        self._clear_card(card)
        v = card.layout()
        v.addWidget(self._make_empty_hint(f"加载失败: {message}"))
        v.addStretch(1)

    @staticmethod
    def _clear_card(card: QGroupBox) -> None:
        """清空卡片内的所有子组件

        setParent(None) 立即从父组件分离（findChildren 不再命中），
        deleteLater() 随后释放内存。
        """
        v = card.layout()
        while v.count():
            item = v.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
