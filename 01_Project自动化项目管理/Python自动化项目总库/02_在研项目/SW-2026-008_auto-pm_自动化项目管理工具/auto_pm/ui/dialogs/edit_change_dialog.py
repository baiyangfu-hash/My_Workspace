"""编辑变更单对话框（M3-1）

双 Tab 结构编辑变更单字段：
- Tab1 基本信息: background/necessity/references/planned_date/urgency
- Tab2 影响分析: 风险等级/缓解措施/约束影响/领域影响/传播链

加载 ChangeService.get_change_request 填充表单，
保存时调用 ChangeService.update_change_request 更新 Markdown + DB（M2 已实现 DB 同步）。
成功后发射 change_updated(change_number) 信号。

字段合法值对齐 CHG-040 规范常量（auto_pm/change/models.py）。
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from auto_pm.change.change_service import ChangeService
from auto_pm.change.models import (
    DOMAINS,
    URGENCY_LEVELS,
    ChangeRequest,
)
from auto_pm.logging.logging import setup_logger
from auto_pm.ui.styles import BASE_WIDGET_STYLE

log = setup_logger(log_level="INFO", app_name="auto_pm")

__all__ = ["EditChangeDialog"]

_DIALOG_STYLE = BASE_WIDGET_STYLE + """
QDialog { background: #fafafa; }
QLabel#dialogTitle { font-size: 16px; font-weight: bold; color: #222; }
QLabel#tabHeader {
    font-size: 13px; font-weight: bold; color: #333;
    border-bottom: 1px solid #e0e0e0;
    padding-bottom: 4px;
}
QTableWidget {
    font-size: 12px;
    border: 1px solid #e0e0e0;
    border-radius: 3px;
}
QTableWidget::item { padding: 4px; }
QHeaderView::section {
    background: #f0f0f0;
    border: none;
    border-right: 1px solid #e0e0e0;
    padding: 4px;
    font-weight: bold;
}
"""

# §6.1 项目约束维度（与 parser.py _parse_constraint_impacts 对齐）
_CONSTRAINT_DIMENSIONS: list[tuple[str, str]] = [
    ("范围", "范围(Scope)"),
    ("进度", "进度(Schedule)"),
    ("成本", "成本(Cost)"),
    ("质量", "质量(Quality)"),
    ("风险", "风险(Risk)"),
]

# 影响程度选项
_IMPACT_LEVELS = ["无", "低", "中", "高"]

# 风险等级选项（code, label）
_RISK_LEVELS: list[tuple[str, str]] = [
    ("none", "无"),
    ("low", "低"),
    ("medium", "中"),
    ("high", "高"),
]


class EditChangeDialog(QDialog):
    """编辑变更单对话框

    双 Tab 结构编辑变更单字段，保存时调用 ChangeService.update_change_request。
    成功后发射 change_updated(change_number)。
    """

    change_updated = Signal(str)

    def __init__(
        self,
        change_number: str,
        change_service: ChangeService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._change_number = change_number
        self._change_service = change_service
        self._cr: ChangeRequest | None = None
        self._build_ui()
        self._load_change()

    # ── UI 构建 ────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.setWindowTitle(f"编辑变更单 - {self._change_number}")
        self.setMinimumWidth(640)
        self.setMinimumHeight(560)
        self.setStyleSheet(_DIALOG_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        title = QLabel("编辑变更单")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        # 双 Tab 结构
        self._tab_widget = QTabWidget()
        self._tab_widget.addTab(self._build_basic_tab(), "基本信息")
        self._tab_widget.addTab(self._build_impact_tab(), "影响分析")
        layout.addWidget(self._tab_widget, 1)

        # 按钮区
        self._button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self._button_box.button(QDialogButtonBox.StandardButton.Ok).setText("保存")
        self._button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("取消")
        self._button_box.accepted.connect(self._on_save)
        self._button_box.rejected.connect(self.reject)
        layout.addWidget(self._button_box)

    def _build_basic_tab(self) -> QWidget:
        """构建基本信息 Tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        header = QLabel("基本信息（§4 变更原因 + §3.4 申请信息）")
        header.setObjectName("tabHeader")
        layout.addWidget(header)

        form = QFormLayout()
        form.setSpacing(8)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self._background_edit = QTextEdit()
        self._background_edit.setPlaceholderText("变更背景")
        self._background_edit.setMaximumHeight(100)
        form.addRow("变更背景", self._background_edit)

        self._necessity_edit = QTextEdit()
        self._necessity_edit.setPlaceholderText("变更必要性")
        self._necessity_edit.setMaximumHeight(100)
        form.addRow("变更必要性", self._necessity_edit)

        self._references_edit = QTextEdit()
        self._references_edit.setPlaceholderText("参考依据")
        self._references_edit.setMaximumHeight(80)
        form.addRow("参考依据", self._references_edit)

        self._urgency_combo = QComboBox()
        for code, label in URGENCY_LEVELS.items():
            self._urgency_combo.addItem(label, code)
        form.addRow("紧急程度", self._urgency_combo)

        self._planned_date_edit = QDateEdit()
        self._planned_date_edit.setCalendarPopup(True)
        self._planned_date_edit.setDisplayFormat("yyyy-MM-dd")
        form.addRow("计划日期", self._planned_date_edit)

        layout.addLayout(form)
        layout.addStretch(1)
        return tab

    def _build_impact_tab(self) -> QWidget:
        """构建影响分析 Tab（§6）"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        header = QLabel("影响分析（§6 变更影响分析）")
        header.setObjectName("tabHeader")
        layout.addWidget(header)

        # 风险等级 + 缓解措施
        form = QFormLayout()
        form.setSpacing(8)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self._risk_level_combo = QComboBox()
        for code, label in _RISK_LEVELS:
            self._risk_level_combo.addItem(label, code)
        form.addRow("风险等级", self._risk_level_combo)

        self._mitigation_edit = QTextEdit()
        self._mitigation_edit.setPlaceholderText("缓解措施（风险应对策略）")
        self._mitigation_edit.setMaximumHeight(80)
        form.addRow("缓解措施", self._mitigation_edit)

        self._propagation_chain_edit = QLineEdit()
        self._propagation_chain_edit.setPlaceholderText(
            "传播链路径，如: SCPT -> PLC -> HMI"
        )
        form.addRow("传播链", self._propagation_chain_edit)

        layout.addLayout(form)

        # 约束影响表格（§6.1）
        layout.addWidget(QLabel("§6.1 项目约束影响"))
        self._constraint_table = QTableWidget(len(_CONSTRAINT_DIMENSIONS), 2)
        self._constraint_table.setHorizontalHeaderLabels(["约束维度", "影响程度"])
        self._constraint_table.verticalHeader().setVisible(False)
        self._constraint_table.horizontalHeader().setStretchLastSection(True)
        for row, (dim_key, dim_label) in enumerate(_CONSTRAINT_DIMENSIONS):
            dim_item = QTableWidgetItem(dim_label)
            dim_item.setFlags(dim_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            dim_item.setData(Qt.ItemDataRole.UserRole, dim_key)
            self._constraint_table.setItem(row, 0, dim_item)
            combo = QComboBox()
            combo.addItems(_IMPACT_LEVELS)
            self._constraint_table.setCellWidget(row, 1, combo)
        self._constraint_table.resizeColumnsToContents()
        layout.addWidget(self._constraint_table)

        # 领域影响表格（§6.2）
        layout.addWidget(QLabel("§6.2 技术领域影响"))
        self._domain_table = QTableWidget(len(DOMAINS), 3)
        self._domain_table.setHorizontalHeaderLabels(
            ["受影响领域", "是否受影响", "具体影响内容"]
        )
        self._domain_table.verticalHeader().setVisible(False)
        self._domain_table.horizontalHeader().setStretchLastSection(True)
        for row, (domain_code, domain_name) in enumerate(DOMAINS.items()):
            domain_item = QTableWidgetItem(f"{domain_code} {domain_name}")
            domain_item.setFlags(domain_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            domain_item.setData(Qt.ItemDataRole.UserRole, domain_code)
            self._domain_table.setItem(row, 0, domain_item)
            combo = QComboBox()
            combo.addItem("否", False)
            combo.addItem("是", True)
            self._domain_table.setCellWidget(row, 1, combo)
            content_item = QTableWidgetItem("")
            self._domain_table.setItem(row, 2, content_item)
        self._domain_table.resizeColumnsToContents()
        layout.addWidget(self._domain_table)

        layout.addStretch(1)
        return tab

    # ── 数据加载 ──────────────────────────────────────────

    def _load_change(self) -> None:
        """从 ChangeService 加载变更单数据填充表单"""
        try:
            cr = self._change_service.get_change_request(self._change_number)
        except Exception as e:
            log.error("加载变更单失败 %s: %s", self._change_number, e, exc_info=True)
            QMessageBox.critical(self, "加载失败", f"加载变更单时出错:\n{e}")
            self.reject()
            return

        if cr is None:
            QMessageBox.warning(self, "未找到", f"变更单 {self._change_number} 不存在")
            self.reject()
            return

        self._cr = cr
        self._fill_form(cr)
        log.info("编辑变更单已加载: %s", self._change_number)

    def _fill_form(self, cr: ChangeRequest) -> None:
        """用 ChangeRequest 数据填充表单"""
        # Tab1 基本信息
        self._background_edit.setPlainText(cr.background or "")
        self._necessity_edit.setPlainText(cr.necessity or "")
        self._references_edit.setPlainText(cr.references or "")

        # 紧急程度
        for i in range(self._urgency_combo.count()):
            if self._urgency_combo.itemData(i) == cr.urgency:
                self._urgency_combo.setCurrentIndex(i)
                break

        # 计划日期
        if cr.planned_date:
            try:
                date = QDate.fromString(cr.planned_date, "yyyy-MM-dd")
                if date.isValid():
                    self._planned_date_edit.setDate(date)
            except Exception:
                log.warning("解析计划日期失败: %s", cr.planned_date)

        # Tab2 影响分析
        # 风险等级
        for i in range(self._risk_level_combo.count()):
            if self._risk_level_combo.itemData(i) == cr.risk_level:
                self._risk_level_combo.setCurrentIndex(i)
                break

        # 缓解措施
        self._mitigation_edit.setPlainText(cr.mitigation or "")

        # 传播链
        self._propagation_chain_edit.setText(cr.propagation_chain or "")

        # 约束影响
        for row in range(self._constraint_table.rowCount()):
            dim_item = self._constraint_table.item(row, 0)
            if dim_item is None:
                continue
            dim_key = dim_item.data(Qt.ItemDataRole.UserRole)
            level = cr.constraint_impacts.get(dim_key, "无")
            combo = self._constraint_table.cellWidget(row, 1)
            if isinstance(combo, QComboBox):
                idx = combo.findText(level)
                if idx >= 0:
                    combo.setCurrentIndex(idx)

        # 领域影响
        for row in range(self._domain_table.rowCount()):
            domain_item = self._domain_table.item(row, 0)
            if domain_item is None:
                continue
            domain_code = domain_item.data(Qt.ItemDataRole.UserRole)
            info = cr.domain_impacts.get(domain_code, {})
            affected = bool(info.get("affected", False))
            content = info.get("content", "")

            combo = self._domain_table.cellWidget(row, 1)
            if isinstance(combo, QComboBox):
                combo.setCurrentIndex(1 if affected else 0)

            content_item = self._domain_table.item(row, 2)
            if content_item is not None:
                content_item.setText(content or "")

    # ── 数据收集 ──────────────────────────────────────────

    def get_edit_data(self) -> dict[str, Any]:
        """返回表单数据，可直接传给 ChangeService.update_change_request"""
        # 约束影响
        constraint_impacts: dict[str, str] = {}
        for row in range(self._constraint_table.rowCount()):
            dim_item = self._constraint_table.item(row, 0)
            if dim_item is None:
                continue
            dim_key = dim_item.data(Qt.ItemDataRole.UserRole)
            combo = self._constraint_table.cellWidget(row, 1)
            if isinstance(combo, QComboBox):
                constraint_impacts[dim_key] = combo.currentText()

        # 领域影响
        domain_impacts: dict[str, dict[str, Any]] = {}
        for row in range(self._domain_table.rowCount()):
            domain_item = self._domain_table.item(row, 0)
            if domain_item is None:
                continue
            domain_code = domain_item.data(Qt.ItemDataRole.UserRole)
            combo = self._domain_table.cellWidget(row, 1)
            affected = False
            if isinstance(combo, QComboBox):
                affected = bool(combo.currentData())
            content_item = self._domain_table.item(row, 2)
            content = content_item.text() if content_item is not None else ""
            domain_impacts[domain_code] = {
                "affected": affected,
                "content": content,
            }

        return {
            # §4/§3.4 基本字段
            "background": self._background_edit.toPlainText().strip(),
            "necessity": self._necessity_edit.toPlainText().strip(),
            "references": self._references_edit.toPlainText().strip(),
            "urgency": self._urgency_combo.currentData() or "normal",
            "planned_date": self._planned_date_edit.date().toString("yyyy-MM-dd"),
            # §6 影响分析字段
            "risk_level": self._risk_level_combo.currentData() or "none",
            "mitigation": self._mitigation_edit.toPlainText().strip(),
            "propagation_chain": self._propagation_chain_edit.text().strip(),
            "constraint_impacts": constraint_impacts,
            "domain_impacts": domain_impacts,
        }

    # ── 保存按钮 ──────────────────────────────────────────

    def _on_save(self) -> None:
        """保存按钮：调用 ChangeService.update_change_request"""
        if self._cr is None:
            QMessageBox.warning(self, "错误", "变更单数据未加载")
            return

        data = self.get_edit_data()

        # 基本校验：background 必填
        if not data["background"]:
            QMessageBox.warning(self, "输入错误", "变更背景不能为空")
            return

        try:
            result = self._change_service.update_change_request(
                self._change_number,
                **data,
            )
        except Exception as e:
            log.error("修改变更单失败: %s", e, exc_info=True)
            QMessageBox.critical(self, "保存失败", f"修改变更单时出错:\n{e}")
            return

        if result is None:
            QMessageBox.critical(
                self, "保存失败", f"未找到变更单: {self._change_number}"
            )
            return

        log.info("变更单已修改: %s", self._change_number)
        self.change_updated.emit(self._change_number)
        self.accept()
