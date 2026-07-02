"""新建项目对话框

收集项目编号/名称/技术栈/模板/描述/作者/业务线，
调用 TemplateService.copy_template 生成项目骨架。
成功后发射 projectCreated(project_id) 信号。
"""

from __future__ import annotations

import os
import re

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
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

from auto_pm.core.constants import (
    BUSINESS_LINE_OPTIONS,
    EQUIPMENT_TYPE_OPTIONS,
    PLC_VENDOR_OPTIONS,
    PROJECT_TYPE_OPTIONS,
    STACK_TEMPLATE_MAP,
)
from auto_pm.core.paths import WORKSPACE_PROJECTS_SUBDIR
from auto_pm.core.template_service import TemplateService
from auto_pm.logging.logging import setup_logger
from auto_pm.ui.styles import BASE_WIDGET_STYLE

log = setup_logger(log_level="INFO", app_name="auto_pm")

# 技术栈 → 模板名（M3-Iter7: 从 core.constants 读取）
_STACK_TEMPLATE_MAP = STACK_TEMPLATE_MAP

# 业务线选项：(value, label)（M3-Iter7: 从 core.constants 读取）
_BUSINESS_LINE_OPTIONS = BUSINESS_LINE_OPTIONS

# 项目编号格式：字母-年份-序号（如 SW-2026-008）
_PROJECT_ID_RE = re.compile(r"^[A-Z]+-\d{4}-\d{3}$")

# 项目目录子路径（工作空间根目录下的标准项目存放目录）
# M3-Iter6: 从 core.paths 读取，消除硬编码
_PROJECTS_SUBDIR = WORKSPACE_PROJECTS_SUBDIR

_DIALOG_STYLE = BASE_WIDGET_STYLE + """
QDialog { background: #fafafa; }
QLabel#dialogTitle { font-size: 16px; font-weight: bold; color: #222; }
QLabel#pathPreview {
    font-size: 12px; color: #555;
    background: #ecf0f1; padding: 6px 10px;
    border-radius: 4px; border: 1px solid #d0d0d0;
}
"""


class NewProjectDialog(QDialog):
    """新建项目对话框

    收集项目元数据，调用 Copier 模板生成项目骨架。
    成功后发射 projectCreated(project_id)。
    """

    projectCreated = Signal(str)

    def __init__(
        self,
        workspace_root: str,
        parent: QWidget | None = None,
        stack: str = "plc",
    ) -> None:
        super().__init__(parent)
        self._workspace_root = workspace_root
        self._templates_dir = self._resolve_templates_dir()
        self._build_ui()
        # 预选技术栈（非法值回退 plc）
        target = stack if stack in ("plc", "python") else "plc"
        for i in range(self._stack_combo.count()):
            if self._stack_combo.itemData(i) == target:
                if self._stack_combo.currentIndex() != i:
                    self._stack_combo.setCurrentIndex(i)
                break
        self._sync_project_metadata_defaults()
        self._update_path_preview()
        self._update_template_combo()

    @staticmethod
    def _resolve_templates_dir() -> str:
        """推断模板目录（auto_pm 包的上级目录下的 templates/）"""
        import auto_pm

        package_dir = os.path.dirname(os.path.abspath(auto_pm.__file__))
        project_root = os.path.dirname(package_dir)
        return os.path.join(project_root, "templates")

    # ── UI 构建 ────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.setWindowTitle("新建项目")
        self.setMinimumWidth(520)
        self.setStyleSheet(_DIALOG_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        title = QLabel("新建项目")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(8)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self._id_edit = QLineEdit()
        self._id_edit.setPlaceholderText("如 SW-2026-008")
        self._id_edit.textChanged.connect(self._on_field_changed)
        form.addRow("项目编号 *", self._id_edit)

        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("如 auto-pm_自动化项目管理工具")
        self._name_edit.textChanged.connect(self._on_field_changed)
        form.addRow("项目名称 *", self._name_edit)

        self._stack_combo = QComboBox()
        self._stack_combo.addItem("PLC", "plc")
        self._stack_combo.addItem("Python", "python")
        self._stack_combo.currentIndexChanged.connect(self._on_stack_changed)
        form.addRow("技术栈", self._stack_combo)

        self._template_combo = QComboBox()
        form.addRow("模板", self._template_combo)

        self._project_type_combo = QComboBox()
        self._project_type_combo.addItem("未设置", "")
        for value, label in PROJECT_TYPE_OPTIONS:
            self._project_type_combo.addItem(label, value)
        form.addRow("项目类型", self._project_type_combo)

        self._equipment_type_combo = QComboBox()
        self._equipment_type_combo.addItem("未设置", "")
        for value, label in EQUIPMENT_TYPE_OPTIONS:
            self._equipment_type_combo.addItem(label, value)
        form.addRow("设备类型", self._equipment_type_combo)

        self._plc_vendor_combo = QComboBox()
        self._plc_vendor_combo.addItem("未设置", "")
        for value, label in PLC_VENDOR_OPTIONS:
            self._plc_vendor_combo.addItem(label, value)
        form.addRow("PLC 品牌", self._plc_vendor_combo)

        self._plc_model_edit = QLineEdit()
        self._plc_model_edit.setPlaceholderText("如 S7-1200 / FX5U")
        form.addRow("PLC 型号", self._plc_model_edit)

        self._desc_edit = QTextEdit()
        self._desc_edit.setPlaceholderText("项目描述（可选）")
        self._desc_edit.setMaximumHeight(80)
        form.addRow("项目描述", self._desc_edit)

        self._author_edit = QLineEdit()
        self._author_edit.setPlaceholderText("作者名（可选）")
        form.addRow("作者", self._author_edit)

        self._bl_combo = QComboBox()
        for value, label in _BUSINESS_LINE_OPTIONS:
            self._bl_combo.addItem(label, value)
        form.addRow("业务线", self._bl_combo)

        layout.addLayout(form)

        self._path_label = QLabel()
        self._path_label.setObjectName("pathPreview")
        self._path_label.setWordWrap(True)
        layout.addWidget(self._path_label)

        self._dry_run_check = QCheckBox("仅预览（dry-run，不实际创建）")
        layout.addWidget(self._dry_run_check)

        self._button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self._button_box.button(QDialogButtonBox.StandardButton.Ok).setText("确定")
        self._button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("取消")
        self._button_box.accepted.connect(self._on_accept)
        self._button_box.rejected.connect(self.reject)
        layout.addWidget(self._button_box)

    # ── 联动逻辑 ──────────────────────────────────────────

    def _on_field_changed(self) -> None:
        """字段变化时更新路径预览和业务线推断"""
        self._update_path_preview()
        self._infer_business_line()

    def _on_stack_changed(self) -> None:
        """技术栈变化时更新模板选项"""
        self._update_template_combo()
        self._sync_project_metadata_defaults()

    def _update_template_combo(self) -> None:
        """根据技术栈更新模板下拉选项"""
        stack = self._stack_combo.currentData() or "plc"
        template_name = _STACK_TEMPLATE_MAP.get(stack, "")
        self._template_combo.clear()
        if template_name:
            self._template_combo.addItem(template_name, template_name)

    def _sync_project_metadata_defaults(self) -> None:
        """根据技术栈同步 Week 2 元数据默认值"""
        stack = self._stack_combo.currentData() or "plc"
        if stack == "plc":
            self._set_combo_by_data(self._project_type_combo, "single_machine")
        else:
            self._set_combo_by_data(self._project_type_combo, "")
            self._set_combo_by_data(self._equipment_type_combo, "")
            self._set_combo_by_data(self._plc_vendor_combo, "")
            self._plc_model_edit.clear()

    @staticmethod
    def _set_combo_by_data(combo: QComboBox, target: str) -> None:
        """按 itemData 设置下拉框当前项"""
        for i in range(combo.count()):
            if combo.itemData(i) == target:
                combo.setCurrentIndex(i)
                return

    def _update_path_preview(self) -> None:
        """更新路径预览标签"""
        project_id = self._id_edit.text().strip()
        project_name = self._name_edit.text().strip()
        if project_id and project_name:
            rel_path = os.path.join(
                _PROJECTS_SUBDIR, f"{project_id}_{project_name}"
            )
            self._path_label.setText(f"创建路径: {rel_path}/")
        else:
            self._path_label.setText(
                f"创建路径: {_PROJECTS_SUBDIR}/<编号>_<名称>/"
            )

    def _infer_business_line(self) -> None:
        """从项目编号前缀推断业务线并联动下拉框"""
        project_id = self._id_edit.text().strip()
        if "-" in project_id:
            prefix = project_id.split("-", 1)[0].upper()
            for i in range(self._bl_combo.count()):
                if self._bl_combo.itemData(i) == prefix:
                    self._bl_combo.setCurrentIndex(i)
                    return

    # ── 确定按钮 ──────────────────────────────────────────

    def _on_accept(self) -> None:
        """确定按钮：校验输入并创建项目"""
        project_id = self._id_edit.text().strip()
        project_name = self._name_edit.text().strip()

        if not project_id:
            QMessageBox.warning(self, "输入错误", "请输入项目编号。")
            return
        if not project_name:
            QMessageBox.warning(self, "输入错误", "请输入项目名称。")
            return
        if not _PROJECT_ID_RE.match(project_id):
            QMessageBox.warning(
                self,
                "格式错误",
                "项目编号格式应为: 字母-年份-序号（如 SW-2026-008）",
            )
            return

        stack = self._stack_combo.currentData() or "plc"
        template_name = _STACK_TEMPLATE_MAP.get(stack, "")
        if not template_name:
            QMessageBox.critical(self, "错误", f"技术栈 {stack} 无对应模板。")
            return

        project_dir = f"{project_id}_{project_name}"
        dest_path = os.path.join(
            self._workspace_root, _PROJECTS_SUBDIR, project_dir
        )

        if os.path.exists(dest_path):
            QMessageBox.critical(
                self, "路径已存在", f"目标路径已存在:\n{dest_path}"
            )
            return

        if self._dry_run_check.isChecked():
            QMessageBox.information(
                self,
                "预览（dry-run）",
                f"将创建项目:\n  编号: {project_id}\n  名称: {project_name}\n"
                f"  技术栈: {stack}\n  模板: {template_name}\n  路径: {dest_path}",
            )
            return

        data: dict[str, str] = {
            "project_id": project_id,
            "project_name": project_name,
            "description": self._desc_edit.toPlainText().strip() or project_name,
            "version": "V1.0.0",
            "stack": stack,
            "business_line": self._bl_combo.currentData() or "",
        }
        if stack == "plc":
            data["mode"] = "standard-project"
        for key, value in (
            ("project_type", self._project_type_combo.currentData() or ""),
            ("equipment_type", self._equipment_type_combo.currentData() or ""),
            ("plc_vendor", self._plc_vendor_combo.currentData() or ""),
            ("plc_model", self._plc_model_edit.text().strip()),
        ):
            if value:
                data[key] = value
        author = self._author_edit.text().strip()
        if author:
            data["author"] = author

        try:
            os.makedirs(
                os.path.join(self._workspace_root, _PROJECTS_SUBDIR),
                exist_ok=True,
            )
            tpl_svc = TemplateService(self._templates_dir)
            tpl_svc.copy_template(template_name, dest_path, data)
            log.info("项目创建成功: %s", dest_path)
            self.projectCreated.emit(project_id)
            self.accept()
        except FileExistsError as e:
            QMessageBox.critical(self, "路径已存在", str(e))
        except FileNotFoundError as e:
            QMessageBox.critical(self, "模板不存在", str(e))
        except Exception as e:
            log.error("创建项目失败: %s", e, exc_info=True)
            QMessageBox.critical(self, "创建失败", f"创建项目时出错:\n{e}")
