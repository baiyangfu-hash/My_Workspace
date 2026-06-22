"""编辑项目元数据对话框

从 ProjectService.get_project 加载当前值，编辑阶段/版本/描述。
确定后调用 ProjectService.update_project_meta 写入。
成功后发射 projectUpdated(project_id) 信号。
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
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

from auto_pm.core.project_service import ProjectService
from auto_pm.logging.logging import setup_logger
from auto_pm.models import ProjectInfo

log = setup_logger(log_level="INFO", app_name="auto_pm")

# 阶段选项：(value, label)
_PHASE_OPTIONS: list[tuple[str, str]] = [
    ("", "未设置"),
    ("developing", "开发中"),
    ("commissioning", "调试中"),
    ("production", "生产中"),
    ("archived", "已归档"),
]

_DIALOG_STYLE = """
QDialog { background: #fafafa; }
QLabel#dialogTitle { font-size: 16px; font-weight: bold; color: #222; }
QLabel#readonlyField {
    font-size: 13px; color: #333;
    background: #ecf0f1; padding: 4px 8px;
    border-radius: 3px; border: 1px solid #d0d0d0;
}
"""


class EditProjectDialog(QDialog):
    """编辑项目元数据对话框

    加载项目当前元数据，允许编辑阶段/版本/描述。
    成功后发射 projectUpdated(project_id)。
    """

    projectUpdated = Signal(str)

    def __init__(
        self,
        project_id: str,
        workspace_root: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._project_id = project_id
        self._workspace_root = workspace_root
        self._project: ProjectInfo | None = None
        self._build_ui()
        self._load_project()

    # ── UI 构建 ────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.setWindowTitle("编辑项目")
        self.setMinimumWidth(520)
        self.setStyleSheet(_DIALOG_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        title = QLabel("编辑项目元数据")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(8)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self._id_label = QLabel()
        self._id_label.setObjectName("readonlyField")
        form.addRow("项目编号", self._id_label)

        self._name_label = QLabel()
        self._name_label.setObjectName("readonlyField")
        form.addRow("项目名称", self._name_label)

        self._stack_label = QLabel()
        self._stack_label.setObjectName("readonlyField")
        form.addRow("技术栈", self._stack_label)

        self._phase_combo = QComboBox()
        for value, label in _PHASE_OPTIONS:
            self._phase_combo.addItem(label, value)
        form.addRow("阶段", self._phase_combo)

        self._version_edit = QLineEdit()
        self._version_edit.setPlaceholderText("如 V1.0.0")
        form.addRow("版本", self._version_edit)

        self._desc_edit = QTextEdit()
        self._desc_edit.setPlaceholderText("项目描述")
        self._desc_edit.setMaximumHeight(100)
        form.addRow("描述", self._desc_edit)

        layout.addLayout(form)

        self._button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self._button_box.button(QDialogButtonBox.StandardButton.Ok).setText("确定")
        self._button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("取消")
        self._button_box.accepted.connect(self._on_accept)
        self._button_box.rejected.connect(self.reject)
        layout.addWidget(self._button_box)

    # ── 数据加载 ──────────────────────────────────────────

    def _load_project(self) -> None:
        """从 ProjectService 加载项目当前元数据"""
        try:
            svc = ProjectService(self._workspace_root)
            proj = svc.get_project(self._project_id)
        except Exception as e:
            log.error("加载项目失败: %s", e, exc_info=True)
            QMessageBox.critical(self, "加载失败", f"加载项目时出错:\n{e}")
            self._button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
            return

        if proj is None:
            QMessageBox.critical(
                self, "项目不存在", f"未找到项目: {self._project_id}"
            )
            self._button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
            return

        self._project = proj
        self._id_label.setText(proj.project_id)
        self._name_label.setText(proj.name)
        self._stack_label.setText(proj.stack)

        for i in range(self._phase_combo.count()):
            if self._phase_combo.itemData(i) == proj.phase:
                self._phase_combo.setCurrentIndex(i)
                break

        self._version_edit.setText(proj.version)
        self._desc_edit.setPlainText(proj.description)

    # ── 确定按钮 ──────────────────────────────────────────

    def _on_accept(self) -> None:
        """确定按钮：写入更新后的元数据"""
        if self._project is None:
            return

        phase = self._phase_combo.currentData() or ""
        version = self._version_edit.text().strip()
        description = self._desc_edit.toPlainText().strip()

        kwargs: dict[str, str] = {
            "phase": phase,
            "version": version,
            "description": description,
        }

        try:
            svc = ProjectService(self._workspace_root)
            svc.update_project_meta(self._project_id, **kwargs)
            log.info("项目元数据已更新: %s", self._project_id)
            self.projectUpdated.emit(self._project_id)
            self.accept()
        except FileNotFoundError as e:
            QMessageBox.critical(self, "项目不存在", str(e))
        except Exception as e:
            log.error("更新项目失败: %s", e, exc_info=True)
            QMessageBox.critical(self, "更新失败", f"更新项目时出错:\n{e}")
