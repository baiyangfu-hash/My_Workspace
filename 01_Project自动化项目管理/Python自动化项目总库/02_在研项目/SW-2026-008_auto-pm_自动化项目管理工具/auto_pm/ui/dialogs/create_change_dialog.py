"""创建变更单对话框

收集变更单字段（项目/领域/性质/范围/申请人/背景/必要性/紧急度/计划日期），
调用 ChangeService.create_change_request 创建变更单。
成功后发射 change_created(project_id) 信号。

字段合法值对齐 CHG-040 规范常量（auto_pm/change/models.py）：
  领域 DOMAINS / 性质 BUSINESS_NATURES / 范围 IMPACT_SCOPES / 紧急度 URGENCY_LEVELS。
"""

from __future__ import annotations

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
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from auto_pm.change.change_service import ChangeService
from auto_pm.change.models import (
    BUSINESS_NATURES,
    DOMAINS,
    IMPACT_SCOPES,
    URGENCY_LEVELS,
)
from auto_pm.core.project_service import ProjectService
from auto_pm.logging.logging import setup_logger

log = setup_logger(log_level="INFO", app_name="auto_pm")

_DIALOG_STYLE = """
QDialog { background: #fafafa; }
QLabel#dialogTitle { font-size: 16px; font-weight: bold; color: #222; }
"""


class CreateChangeDialog(QDialog):
    """创建变更单对话框

    收集变更单字段并调用 ChangeService.create_change_request。
    成功后发射 change_created(project_id)。
    """

    change_created = Signal(str)

    def __init__(
        self,
        project_service: ProjectService,
        change_service: ChangeService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._project_service = project_service
        self._change_service = change_service
        self._build_ui()
        self._load_projects()
        self._update_create_button()

    # ── UI 构建 ────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.setWindowTitle("创建变更单")
        self.setMinimumWidth(560)
        self.setStyleSheet(_DIALOG_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        title = QLabel("创建变更单")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(8)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self._project_combo = QComboBox()
        self._project_combo.currentIndexChanged.connect(self._update_create_button)
        form.addRow("项目 *", self._project_combo)

        self._domain_combo = QComboBox()
        for code, label in DOMAINS.items():
            self._domain_combo.addItem(f"{code} {label}", code)
        form.addRow("领域 *", self._domain_combo)

        self._nature_combo = QComboBox()
        for code, label in BUSINESS_NATURES.items():
            self._nature_combo.addItem(f"{code} {label}", code)
        form.addRow("性质 *", self._nature_combo)

        self._scope_combo = QComboBox()
        for code, label in IMPACT_SCOPES.items():
            self._scope_combo.addItem(f"{code} {label}", code)
        form.addRow("范围 *", self._scope_combo)

        self._applicant_edit = QLineEdit()
        self._applicant_edit.setText("fubai")
        self._applicant_edit.textChanged.connect(self._update_create_button)
        form.addRow("申请人 *", self._applicant_edit)

        self._background_edit = QTextEdit()
        self._background_edit.setPlaceholderText("变更背景（必填）")
        self._background_edit.setMaximumHeight(80)
        self._background_edit.textChanged.connect(self._update_create_button)
        form.addRow("背景 *", self._background_edit)

        self._necessity_edit = QTextEdit()
        self._necessity_edit.setPlaceholderText("变更必要性（选填）")
        self._necessity_edit.setMaximumHeight(80)
        form.addRow("必要性", self._necessity_edit)

        self._urgency_combo = QComboBox()
        for code, label in URGENCY_LEVELS.items():
            self._urgency_combo.addItem(label, code)
        form.addRow("紧急度", self._urgency_combo)

        self._planned_date_edit = QDateEdit()
        self._planned_date_edit.setCalendarPopup(True)
        self._planned_date_edit.setDate(QDate.currentDate())
        self._planned_date_edit.setDisplayFormat("yyyy-MM-dd")
        form.addRow("计划日期", self._planned_date_edit)

        layout.addLayout(form)

        self._button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self._button_box.button(QDialogButtonBox.StandardButton.Ok).setText("创建")
        self._button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("取消")
        self._button_box.accepted.connect(self._on_create)
        self._button_box.rejected.connect(self.reject)
        layout.addWidget(self._button_box)

    # ── 数据加载 ──────────────────────────────────────────

    def _load_projects(self) -> None:
        """从 ProjectService 加载项目列表到下拉框"""
        self._project_combo.clear()
        try:
            projects = self._project_service.list_projects()
        except Exception as e:
            log.error("加载项目列表失败: %s", e, exc_info=True)
            QMessageBox.critical(self, "加载失败", f"加载项目列表时出错:\n{e}")
            return
        for proj in projects:
            display = f"{proj.project_id} {proj.name}".strip()
            self._project_combo.addItem(display, proj.project_id)

    # ── 联动校验 ──────────────────────────────────────────

    def _update_create_button(self) -> None:
        """必填字段为空时禁用"创建"按钮"""
        ok = bool(
            self._project_combo.currentData()
            and self._applicant_edit.text().strip()
            and self._background_edit.toPlainText().strip()
        )
        self._button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(ok)

    # ── 数据收集 ──────────────────────────────────────────

    def get_change_data(self) -> dict:
        """返回表单数据"""
        scope = self._scope_combo.currentData()
        return {
            "project_id": self._project_combo.currentData() or "",
            "domain": self._domain_combo.currentData() or "",
            "business_nature": self._nature_combo.currentData() or "",
            "impact_scope": [scope] if scope else [],
            "applicant": self._applicant_edit.text().strip(),
            "background": self._background_edit.toPlainText().strip(),
            "necessity": self._necessity_edit.toPlainText().strip(),
            "urgency": self._urgency_combo.currentData() or "normal",
            "planned_date": self._planned_date_edit.date().toString("yyyy-MM-dd"),
        }

    # ── 创建按钮 ──────────────────────────────────────────

    def _on_create(self) -> None:
        """创建按钮：校验输入并调用 ChangeService 创建变更单"""
        data = self.get_change_data()
        if not data["project_id"]:
            QMessageBox.warning(self, "输入错误", "请选择项目。")
            return
        if not data["applicant"]:
            QMessageBox.warning(self, "输入错误", "请输入申请人。")
            return
        if not data["background"]:
            QMessageBox.warning(self, "输入错误", "请填写变更背景。")
            return

        try:
            cr = self._change_service.create_change_request(
                project_id=data["project_id"],
                domain=data["domain"],
                business_nature=data["business_nature"],
                impact_scope=data["impact_scope"],
                applicant=data["applicant"],
                background=data["background"],
                necessity=data["necessity"] or "待补充",
                planned_date=data["planned_date"],
                urgency=data["urgency"],
            )
            log.info("变更单创建成功: %s", cr.change_number)
            self.change_created.emit(data["project_id"])
            self.accept()
        except Exception as e:
            log.error("创建变更单失败: %s", e, exc_info=True)
            QMessageBox.critical(self, "创建失败", f"创建变更单时出错:\n{e}")
