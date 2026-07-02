"""创建变更单对话框（M3-4 改为 QWizard 分步向导）

3 步向导收集变更单字段并调用 ChangeService.create_change_request：
  Step 1 基本信息: 项目/领域/性质/范围/申请人/紧急度/计划日期
  Step 2 变更描述: 背景（必填）/必要性（选填）
  Step 3 提交确认: 汇总展示，Finish 触发创建

成功后发射 change_created(project_id) 信号。
字段合法值对齐 CHG-040 规范常量（auto_pm/change/models.py）。

兼容性：保留 CreateChangeDialog 别名 + 构造函数签名 + change_created 信号 +
get_change_data() 方法 + 内部控件属性（_project_combo 等），调用点零改动。
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QWizard,
    QWizardPage,
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
from auto_pm.ui.styles import BASE_WIDGET_STYLE

log = setup_logger(log_level="INFO", app_name="auto_pm")

__all__ = ["CreateChangeWizard", "CreateChangeDialog"]

_WIZARD_STYLE = BASE_WIDGET_STYLE + """
QWizard { background: #fafafa; }
QWizardPage { background: #fafafa; }
QLabel#pageHint { font-size: 12px; color: #888; }
QLabel#summaryHeader {
    font-size: 13px; font-weight: bold; color: #333;
    border-bottom: 1px solid #e0e0e0;
    padding-bottom: 4px;
}
QLabel#summaryLabel { font-size: 12px; color: #333; }
"""


# ── Step 1: 基本信息 ──────────────────────────────────────


class BasicInfoPage(QWizardPage):
    """Step 1: 基本信息（项目/领域/性质/范围/申请人/紧急度/计划日期）"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setTitle("基本信息")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QFormLayout(self)
        layout.setSpacing(8)
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self._project_combo = QComboBox()
        layout.addRow("项目 *", self._project_combo)

        self._domain_combo = QComboBox()
        for code, label in DOMAINS.items():
            self._domain_combo.addItem(f"{code} {label}", code)
        layout.addRow("领域 *", self._domain_combo)

        self._nature_combo = QComboBox()
        for code, label in BUSINESS_NATURES.items():
            self._nature_combo.addItem(f"{code} {label}", code)
        layout.addRow("性质 *", self._nature_combo)

        self._scope_combo = QComboBox()
        for code, label in IMPACT_SCOPES.items():
            self._scope_combo.addItem(f"{code} {label}", code)
        layout.addRow("范围 *", self._scope_combo)

        self._applicant_edit = QLineEdit()
        self._applicant_edit.setText("fubai")
        layout.addRow("申请人 *", self._applicant_edit)

        self._urgency_combo = QComboBox()
        for code, label in URGENCY_LEVELS.items():
            self._urgency_combo.addItem(label, code)
        layout.addRow("紧急度", self._urgency_combo)

        self._planned_date_edit = QDateEdit()
        self._planned_date_edit.setCalendarPopup(True)
        self._planned_date_edit.setDate(QDate.currentDate())
        self._planned_date_edit.setDisplayFormat("yyyy-MM-dd")
        layout.addRow("计划日期", self._planned_date_edit)

        # 联动必填校验
        self._project_combo.currentIndexChanged.connect(self.completeChanged)
        self._applicant_edit.textChanged.connect(self.completeChanged)

    def isComplete(self) -> bool:
        return bool(
            self._project_combo.currentData()
            and self._applicant_edit.text().strip()
        )


# ── Step 2: 变更描述 ──────────────────────────────────────


class DescriptionPage(QWizardPage):
    """Step 2: 变更描述（背景必填/必要性选填）"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setTitle("变更描述")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        hint = QLabel("请详细描述变更背景和必要性，背景为必填项。")
        hint.setObjectName("pageHint")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        form = QFormLayout()
        form.setSpacing(8)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self._background_edit = QTextEdit()
        self._background_edit.setPlaceholderText("变更背景（必填）")
        self._background_edit.setMaximumHeight(120)
        form.addRow("背景 *", self._background_edit)

        self._necessity_edit = QTextEdit()
        self._necessity_edit.setPlaceholderText("变更必要性（选填）")
        self._necessity_edit.setMaximumHeight(120)
        form.addRow("必要性", self._necessity_edit)

        layout.addLayout(form)

        self._background_edit.textChanged.connect(self.completeChanged)

    def isComplete(self) -> bool:
        return bool(self._background_edit.toPlainText().strip())


# ── Step 3: 提交确认 ──────────────────────────────────────


class ConfirmPage(QWizardPage):
    """Step 3: 提交确认（汇总展示 + Finish 触发创建）"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setTitle("提交确认")
        self._get_data: Callable[[], dict[str, Any]] | None = None
        self._on_finish: Callable[[], bool] | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        header = QLabel('请确认以下信息无误，点击"完成"创建变更单。')
        header.setObjectName("summaryHeader")
        header.setWordWrap(True)
        layout.addWidget(header)

        self._summary_label = QLabel("")
        self._summary_label.setObjectName("summaryLabel")
        self._summary_label.setWordWrap(True)
        self._summary_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        layout.addWidget(self._summary_label)
        layout.addStretch(1)

    def initializePage(self) -> None:
        if self._get_data is None:
            return
        data = self._get_data()
        scope_label = "—"
        if data["impact_scope"]:
            scope_label = IMPACT_SCOPES.get(data["impact_scope"][0], data["impact_scope"][0])
        lines = [
            f"<b>项目编号:</b> {data['project_id']}",
            f"<b>技术领域:</b> {DOMAINS.get(data['domain'], data['domain'])}",
            f"<b>业务性质:</b> {BUSINESS_NATURES.get(data['business_nature'], data['business_nature'])}",
            f"<b>影响范围:</b> {scope_label}",
            f"<b>申请人:</b> {data['applicant']}",
            f"<b>紧急程度:</b> {URGENCY_LEVELS.get(data['urgency'], data['urgency'])}",
            f"<b>计划日期:</b> {data['planned_date']}",
            f"<b>变更背景:</b> {data['background']}",
            f"<b>变更必要性:</b> {data['necessity'] or '—'}",
        ]
        self._summary_label.setText("<br>".join(lines))

    def validatePage(self) -> bool:
        if self._on_finish is None:
            return True
        return self._on_finish()


# ── 主向导 ────────────────────────────────────────────────


class CreateChangeWizard(QWizard):
    """创建变更单向导（3 步分步收集）

    成功后发射 change_created(project_id) 信号。
    构造函数签名与原 CreateChangeDialog 一致，调用点无需改动。
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
        self.setWindowTitle("创建变更单")
        self.setMinimumWidth(580)
        self.setStyleSheet(_WIZARD_STYLE)
        self.setWizardStyle(QWizard.WizardStyle.ClassicStyle)

        # 按钮文案中文化
        self.setButtonText(QWizard.WizardButton.NextButton, "下一步 >")
        self.setButtonText(QWizard.WizardButton.BackButton, "< 上一步")
        self.setButtonText(QWizard.WizardButton.FinishButton, "完成创建")
        self.setButtonText(QWizard.WizardButton.CancelButton, "取消")

        # 兼容属性：QDialogButtonBox（供旧测试访问 Ok 按钮启用状态）
        self._compat_button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        self._compat_button_box.button(
            QDialogButtonBox.StandardButton.Ok
        ).setEnabled(False)
        self._compat_button_box.rejected.connect(self.reject)

        # 创建页面
        self._basic_page = BasicInfoPage()
        self._desc_page = DescriptionPage()
        self._confirm_page = ConfirmPage()
        self._confirm_page._get_data = self.get_change_data
        self._confirm_page._on_finish = self._on_create
        self.addPage(self._basic_page)
        self.addPage(self._desc_page)
        self.addPage(self._confirm_page)

        # 加载项目 + 初始化兼容按钮状态
        self._load_projects()
        self._update_compat_button()

        # 联动兼容按钮（信号绑定到控件，而非 property）
        self._basic_page._project_combo.currentIndexChanged.connect(
            self._update_compat_button
        )
        self._basic_page._applicant_edit.textChanged.connect(
            self._update_compat_button
        )
        self._desc_page._background_edit.textChanged.connect(
            self._update_compat_button
        )

    # ── 兼容属性（供测试和旧调用方访问内部控件） ──────────

    @property
    def _project_combo(self) -> QComboBox:
        return self._basic_page._project_combo

    @property
    def _domain_combo(self) -> QComboBox:
        return self._basic_page._domain_combo

    @property
    def _nature_combo(self) -> QComboBox:
        return self._basic_page._nature_combo

    @property
    def _scope_combo(self) -> QComboBox:
        return self._basic_page._scope_combo

    @property
    def _applicant_edit(self) -> QLineEdit:
        return self._basic_page._applicant_edit

    @property
    def _urgency_combo(self) -> QComboBox:
        return self._basic_page._urgency_combo

    @property
    def _planned_date_edit(self) -> QDateEdit:
        return self._basic_page._planned_date_edit

    @property
    def _background_edit(self) -> QTextEdit:
        return self._desc_page._background_edit

    @property
    def _necessity_edit(self) -> QTextEdit:
        return self._desc_page._necessity_edit

    @property
    def _button_box(self) -> QDialogButtonBox:
        """兼容属性：返回虚拟 QDialogButtonBox，Ok 按钮状态联动必填校验"""
        return self._compat_button_box

    # ── 数据加载 ──────────────────────────────────────────

    def _load_projects(self) -> None:
        """从 ProjectService 加载项目列表到下拉框"""
        self._basic_page._project_combo.clear()
        try:
            projects = self._project_service.list_projects()
        except Exception as e:
            log.error("加载项目列表失败: %s", e, exc_info=True)
            QMessageBox.critical(self, "加载失败", f"加载项目列表时出错:\n{e}")
            return
        for proj in projects:
            display = f"{proj.project_id} {proj.name}".strip()
            self._basic_page._project_combo.addItem(display, proj.project_id)

    # ── 联动校验 ──────────────────────────────────────────

    def _update_compat_button(self) -> None:
        """更新兼容 Ok 按钮启用状态（项目+申请人+背景全部满足才启用）"""
        ok = bool(
            self._basic_page._project_combo.currentData()
            and self._basic_page._applicant_edit.text().strip()
            and self._desc_page._background_edit.toPlainText().strip()
        )
        self._compat_button_box.button(
            QDialogButtonBox.StandardButton.Ok
        ).setEnabled(ok)

    # ── 数据收集 ──────────────────────────────────────────

    def get_change_data(self) -> dict[str, Any]:
        """返回表单数据（跨页面收集）"""
        scope = self._basic_page._scope_combo.currentData()
        return {
            "project_id": self._basic_page._project_combo.currentData() or "",
            "domain": self._basic_page._domain_combo.currentData() or "",
            "business_nature": self._basic_page._nature_combo.currentData() or "",
            "impact_scope": [scope] if scope else [],
            "applicant": self._basic_page._applicant_edit.text().strip(),
            "background": self._desc_page._background_edit.toPlainText().strip(),
            "necessity": self._desc_page._necessity_edit.toPlainText().strip(),
            "urgency": self._basic_page._urgency_combo.currentData() or "normal",
            "planned_date": self._basic_page._planned_date_edit.date().toString("yyyy-MM-dd"),
        }

    # ── 创建按钮 ──────────────────────────────────────────

    def _on_create(self) -> bool:
        """创建变更单，成功返回 True（供 ConfirmPage.validatePage 调用）"""
        data = self.get_change_data()
        if not data["project_id"]:
            QMessageBox.warning(self, "输入错误", "请选择项目。")
            return False
        if not data["applicant"]:
            QMessageBox.warning(self, "输入错误", "请输入申请人。")
            return False
        if not data["background"]:
            QMessageBox.warning(self, "输入错误", "请填写变更背景。")
            return False

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
            return True
        except Exception as e:
            log.error("创建变更单失败: %s", e, exc_info=True)
            QMessageBox.critical(self, "创建失败", f"创建变更单时出错:\n{e}")
            return False


# 向后兼容别名：旧调用方 import CreateChangeDialog 仍然有效
CreateChangeDialog = CreateChangeWizard
