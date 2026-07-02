"""删除项目对话框（带二次确认）

红色警告风格，要求用户输入项目编号以确认删除。
确认后调用 shutil.rmtree 删除项目目录。
成功后发射 projectDeleted(project_id) 信号。
"""

from __future__ import annotations

import shutil

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from auto_pm.core.project_service import ProjectService
from auto_pm.logging.logging import setup_logger
from auto_pm.ui.styles import BASE_WIDGET_STYLE

log = setup_logger(log_level="INFO", app_name="auto_pm")

_DIALOG_STYLE = BASE_WIDGET_STYLE + """
QDialog { background: #fafafa; }
QLabel#deleteTitle { font-size: 16px; font-weight: bold; color: #c0392b; }
QLabel#deleteWarning {
    font-size: 13px; color: #c0392b; font-weight: bold;
    background: #fdf2f2; padding: 8px 12px;
    border-radius: 4px; border: 1px solid #f5c6c6;
}
QLabel#infoLabel { font-size: 12px; color: #555; }
QLabel#infoValue { font-size: 12px; color: #222; }
QPushButton#confirmDelete {
    background: #e74c3c; color: #ffffff;
    border: none; padding: 6px 16px;
    border-radius: 4px; font-weight: bold;
}
QPushButton#confirmDelete:hover { background: #c0392b; }
QPushButton#confirmDelete:disabled { background: #bdc3c7; color: #ecf0f1; }
"""


class DeleteProjectDialog(QDialog):
    """删除项目对话框

    要求用户输入项目编号以确认删除，防止误操作。
    成功后发射 projectDeleted(project_id)。
    """

    projectDeleted = Signal(str)

    def __init__(
        self,
        project_id: str,
        workspace_root: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._project_id = project_id
        self._workspace_root = workspace_root
        self._project_path: str | None = None
        self._build_ui()
        self._load_project()

    # ── UI 构建 ────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.setWindowTitle("删除项目")
        self.setMinimumWidth(480)
        self.setStyleSheet(_DIALOG_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        title = QLabel("删除项目")
        title.setObjectName("deleteTitle")
        layout.addWidget(title)

        warning = QLabel(
            "此操作将永久删除项目目录及其所有内容，不可恢复！"
        )
        warning.setObjectName("deleteWarning")
        warning.setWordWrap(True)
        layout.addWidget(warning)

        form = QFormLayout()
        form.setSpacing(6)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        id_label = QLabel(self._project_id)
        id_label.setObjectName("infoValue")
        form.addRow("项目编号:", id_label)

        self._name_label = QLabel("—")
        self._name_label.setObjectName("infoValue")
        form.addRow("项目名称:", self._name_label)

        self._path_label = QLabel("—")
        self._path_label.setObjectName("infoValue")
        self._path_label.setWordWrap(True)
        form.addRow("项目路径:", self._path_label)

        layout.addLayout(form)

        confirm_hint = QLabel(
            f'请输入项目编号 "{self._project_id}" 以确认删除：'
        )
        confirm_hint.setObjectName("infoLabel")
        layout.addWidget(confirm_hint)

        self._confirm_edit = QLineEdit()
        self._confirm_edit.setPlaceholderText(self._project_id)
        self._confirm_edit.textChanged.connect(self._on_confirm_changed)
        layout.addWidget(self._confirm_edit)

        self._button_box = QDialogButtonBox()
        cancel_btn = self._button_box.addButton(
            "取消", QDialogButtonBox.ButtonRole.RejectRole
        )
        cancel_btn.clicked.connect(self.reject)
        self._delete_btn = QPushButton("确认删除")
        self._delete_btn.setObjectName("confirmDelete")
        self._delete_btn.setEnabled(False)
        self._delete_btn.clicked.connect(self._on_accept)
        self._button_box.addButton(self._delete_btn, QDialogButtonBox.ButtonRole.AcceptRole)
        layout.addWidget(self._button_box)

    # ── 数据加载 ──────────────────────────────────────────

    def _load_project(self) -> None:
        """加载项目信息用于展示"""
        try:
            svc = ProjectService(self._workspace_root)
            proj = svc.get_project(self._project_id)
        except Exception as e:
            log.error("加载项目失败: %s", e, exc_info=True)
            QMessageBox.critical(self, "加载失败", f"加载项目时出错:\n{e}")
            self._delete_btn.setEnabled(False)
            return

        if proj is None:
            QMessageBox.critical(
                self, "项目不存在", f"未找到项目: {self._project_id}"
            )
            self._delete_btn.setEnabled(False)
            return

        self._project_path = proj.path
        self._name_label.setText(proj.name)
        self._path_label.setText(proj.path)

    # ── 联动逻辑 ──────────────────────────────────────────

    def _on_confirm_changed(self, text: str) -> None:
        """确认输入框文本变化时启用/禁用删除按钮"""
        self._delete_btn.setEnabled(text.strip() == self._project_id)

    # ── 确认删除 ──────────────────────────────────────────

    def _on_accept(self) -> None:
        """确认删除：执行 shutil.rmtree"""
        if self._project_path is None:
            return

        try:
            shutil.rmtree(self._project_path)
            log.info("项目已删除: %s", self._project_path)
            self.projectDeleted.emit(self._project_id)
            self.accept()
        except FileNotFoundError as e:
            QMessageBox.critical(self, "删除失败", f"目录不存在:\n{e}")
        except OSError as e:
            log.error("删除项目失败: %s", e, exc_info=True)
            QMessageBox.critical(self, "删除失败", f"删除项目时出错:\n{e}")
