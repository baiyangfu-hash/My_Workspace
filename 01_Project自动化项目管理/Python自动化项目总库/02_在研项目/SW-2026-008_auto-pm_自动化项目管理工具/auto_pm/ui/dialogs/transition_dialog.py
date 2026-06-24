"""状态流转确认对话框

显示变更单编号/当前状态/目标状态，收集审批人/备注/验证结论，
调用 ChangeService.transition_status 完成状态流转。
成功后发射 transition_completed(change_number) 信号。

current_status / target_status 使用 CHG-040 规范的英文状态码
（如 draft/submitted/.../completed），界面显示对应中文标签
（STATUS_LABELS）。当目标状态为 completed 时显示"验证结论"字段。
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
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
from auto_pm.change.models import STATUS_LABELS
from auto_pm.logging.logging import setup_logger

log = setup_logger(log_level="INFO", app_name="auto_pm")

_DIALOG_STYLE = """
QDialog { background: #fafafa; }
QLabel#dialogTitle { font-size: 16px; font-weight: bold; color: #222; }
QLabel#readonlyField {
    font-size: 13px; color: #333;
    background: #ecf0f1; padding: 4px 8px;
    border-radius: 3px; border: 1px solid #d0d0d0;
}
"""


class TransitionDialog(QDialog):
    """状态流转确认对话框

    调用 ChangeService.transition_status 完成流转。
    成功后发射 transition_completed(change_number)。
    """

    transition_completed = Signal(str)

    def __init__(
        self,
        change_number: str,
        current_status: str,
        target_status: str,
        change_service: ChangeService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._change_number = change_number
        self._current_status = current_status
        self._target_status = target_status
        self._change_service = change_service
        self._requires_verification = target_status == "completed"
        self._build_ui()

    # ── UI 构建 ────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.setWindowTitle("状态流转确认")
        self.setMinimumWidth(520)
        self.setStyleSheet(_DIALOG_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        title = QLabel("状态流转确认")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(8)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self._number_label = QLabel(self._change_number)
        self._number_label.setObjectName("readonlyField")
        form.addRow("变更单编号", self._number_label)

        self._current_label = QLabel(
            STATUS_LABELS.get(self._current_status, self._current_status)
        )
        self._current_label.setObjectName("readonlyField")
        form.addRow("当前状态", self._current_label)

        self._target_label = QLabel(
            STATUS_LABELS.get(self._target_status, self._target_status)
        )
        self._target_label.setObjectName("readonlyField")
        form.addRow("目标状态", self._target_label)

        self._approver_edit = QLineEdit()
        self._approver_edit.setText("fubai")
        form.addRow("审批人", self._approver_edit)

        self._comment_edit = QTextEdit()
        self._comment_edit.setPlaceholderText("备注（选填）")
        self._comment_edit.setMaximumHeight(80)
        form.addRow("备注", self._comment_edit)

        # 验证结论：仅当目标状态为 completed 时显示
        self._verification_edit = QTextEdit()
        self._verification_edit.setPlainText("全部通过")
        self._verification_edit.setMaximumHeight(80)
        self._verification_label = QLabel("验证结论")
        form.addRow(self._verification_label, self._verification_edit)
        if not self._requires_verification:
            self._verification_label.setVisible(False)
            self._verification_edit.setVisible(False)

        layout.addLayout(form)

        self._button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self._button_box.button(QDialogButtonBox.StandardButton.Ok).setText("确认流转")
        self._button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("取消")
        self._button_box.accepted.connect(self._on_confirm)
        self._button_box.rejected.connect(self.reject)
        layout.addWidget(self._button_box)

    # ── 数据收集 ──────────────────────────────────────────

    def get_transition_data(self) -> dict[str, Any]:
        """返回 {approver, comment, verification_conclusion}"""
        if self._requires_verification:
            conclusion = self._verification_edit.toPlainText().strip() or "全部通过"
        else:
            conclusion = "全部通过"
        return {
            "approver": self._approver_edit.text().strip(),
            "comment": self._comment_edit.toPlainText().strip(),
            "verification_conclusion": conclusion,
        }

    # ── 确认流转按钮 ──────────────────────────────────────

    def _on_confirm(self) -> None:
        """确认流转按钮：调用 ChangeService.transition_status"""
        data = self.get_transition_data()
        try:
            result = self._change_service.transition_status(
                change_number=self._change_number,
                new_status=self._target_status,
                approver=data["approver"],
                comment=data["comment"],
                verification_conclusion=data["verification_conclusion"],
            )
        except Exception as e:
            log.error("状态流转失败: %s", e, exc_info=True)
            QMessageBox.critical(self, "流转失败", f"状态流转时出错:\n{e}")
            return

        if result is None:
            QMessageBox.critical(
                self, "流转失败", f"未找到变更单: {self._change_number}"
            )
            return

        log.info(
            "状态流转成功: %s -> %s", self._change_number, self._target_status
        )
        self.transition_completed.emit(self._change_number)
        self.accept()
