"""Tab3 健康检查 - 10 项 SHC 检查结果展示 + 自动修复按钮

对接 CheckService（通过 SpecCenterAdapter），运行 10 项 SHC 健康检查，
展示检查结果，支持自动修复可修复项（SHC-002/007）。
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from auto_pm.logging.logging import setup_logger
from auto_pm.spec.core.checker_base import Severity
from auto_pm.ui.global_pages.spec_center_dto import (
    HealthCheckOutputDTO,
    HealthCheckResultDTO,
    SpecCenterAdapter,
)

log = setup_logger(log_level="INFO", app_name="auto_pm")

__all__ = ["CheckTab"]

_SEVERITY_LABELS = {
    Severity.ERROR: "🔴 错误",
    Severity.WARNING: "🟡 警告",
    Severity.INFO: "🟢 提示",
}

_SEVERITY_COLORS = {
    Severity.ERROR: "#d9534f",
    Severity.WARNING: "#f0ad4e",
    Severity.INFO: "#5cb85c",
}


class CheckTab(QWidget):
    """Tab3 健康检查：10 项 SHC 检查结果 + 自动修复"""

    def __init__(
        self,
        adapter: SpecCenterAdapter,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._adapter = adapter
        self._last_output: HealthCheckOutputDTO | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        # 标题
        title = QLabel("规范健康检查")
        title.setObjectName("specTitle")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #222;")
        layout.addWidget(title)

        # 摘要栏
        summary = QWidget()
        h = QHBoxLayout(summary)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(12)

        self._error_label = QLabel("错误: 0")
        self._error_label.setStyleSheet("font-size: 13px; color: #d9534f; font-weight: bold;")
        h.addWidget(self._error_label)

        self._warning_label = QLabel("警告: 0")
        self._warning_label.setStyleSheet("font-size: 13px; color: #f0ad4e; font-weight: bold;")
        h.addWidget(self._warning_label)

        self._info_label = QLabel("提示: 0")
        self._info_label.setStyleSheet("font-size: 13px; color: #5cb85c; font-weight: bold;")
        h.addWidget(self._info_label)

        h.addStretch(1)
        layout.addWidget(summary)

        # 工具栏
        toolbar = QWidget()
        h2 = QHBoxLayout(toolbar)
        h2.setContentsMargins(0, 0, 0, 0)
        h2.setSpacing(8)

        self._run_btn = QPushButton("运行检查")
        self._run_btn.setStyleSheet(
            "QPushButton { background: #4a90d9; color: white; border: none; "
            "border-radius: 4px; padding: 6px 14px; }"
            "QPushButton:hover { background: #3a7bc8; }"
        )
        self._run_btn.clicked.connect(self.run_checks)
        h2.addWidget(self._run_btn)

        self._fix_btn = QPushButton("自动修复（dry-run）")
        self._fix_btn.setStyleSheet(
            "QPushButton { background: #f5f5f5; border: 1px solid #d0d0d0; "
            "border-radius: 4px; padding: 6px 14px; }"
        )
        self._fix_btn.clicked.connect(self.run_auto_fix_dry_run)
        self._fix_btn.setEnabled(False)
        h2.addWidget(self._fix_btn)

        self._apply_fix_btn = QPushButton("应用修复")
        self._apply_fix_btn.setStyleSheet(
            "QPushButton { background: #f5f5f5; border: 1px solid #d0d0d0; "
            "border-radius: 4px; padding: 6px 14px; }"
        )
        self._apply_fix_btn.clicked.connect(self.run_auto_fix_apply)
        self._apply_fix_btn.setEnabled(False)
        h2.addWidget(self._apply_fix_btn)

        h2.addStretch(1)
        layout.addWidget(toolbar)

        # 结果展示区
        self._result_text = QTextEdit()
        self._result_text.setReadOnly(True)
        self._result_text.setStyleSheet(
            "QTextEdit { background: #ffffff; border: 1px solid #e0e0e0; "
            "border-radius: 4px; font-family: Consolas, 'Courier New', monospace; font-size: 12px; }"
        )
        self._result_text.setPlaceholderText("点击『运行检查』开始检查...")
        layout.addWidget(self._result_text, 1)

    def run_checks(self) -> None:
        """运行健康检查"""
        try:
            output = self._adapter.run_checks()
            self._last_output = output
            self._render(output)
            # 启用修复按钮（仅当存在可自动修复项时）
            has_fixable = any(r.auto_fixable for r in output.results)
            self._fix_btn.setEnabled(has_fixable)
            self._apply_fix_btn.setEnabled(has_fixable)
        except Exception as e:
            log.error("运行健康检查失败: %s", e)
            QMessageBox.critical(self, "检查失败", str(e))

    def run_auto_fix_dry_run(self) -> None:
        """自动修复 dry-run（预览）"""
        self._run_auto_fix(dry_run=True)

    def run_auto_fix_apply(self) -> None:
        """自动修复 apply（实际写入）"""
        self._run_auto_fix(dry_run=False)

    def _run_auto_fix(self, dry_run: bool) -> None:
        """执行自动修复"""
        try:
            output = self._adapter.run_checks(auto_fix=True, dry_run=dry_run)
            self._last_output = output
            self._render(output)
            mode = "预览" if dry_run else "应用"
            fix_count = len(output.fix_results)
            applied_count = sum(1 for fr in output.fix_results if fr.applied)
            QMessageBox.information(
                self,
                f"修复{mode}完成",
                f"修复{mode}完成：共 {fix_count} 项，应用 {applied_count} 项",
            )
        except Exception as e:
            log.error("自动修复失败: %s", e)
            QMessageBox.critical(self, "修复失败", str(e))

    def _render(self, dto: HealthCheckOutputDTO) -> None:
        """渲染检查结果"""
        self._error_label.setText(f"错误: {dto.error_count}")
        self._warning_label.setText(f"警告: {dto.warning_count}")
        self._info_label.setText(f"提示: {dto.info_count}")

        if not dto.results:
            self._result_text.setPlainText("✅ 所有检查通过！")
            return

        lines: list[str] = []
        lines.append(f"检查汇总：错误 {dto.error_count} | 警告 {dto.warning_count} | 提示 {dto.info_count}")
        lines.append("=" * 60)
        lines.append("")

        for r in dto.results:
            label = _SEVERITY_LABELS.get(r.severity, str(r.severity))
            fixable_tag = " [可自动修复]" if r.auto_fixable else ""
            lines.append(f"{label} [{r.check_id}]{fixable_tag}: {r.message}")
            if r.details:
                lines.append(f"    详情: {r.details}")
            if r.fix_suggestion:
                lines.append(f"    建议: {r.fix_suggestion}")
            lines.append("")

        if dto.fix_results:
            lines.append("=" * 60)
            lines.append("修复结果：")
            for fr in dto.fix_results:
                status = "✅" if fr.applied else "⏭️"
                lines.append(f"    {status} [{fr.check_id}] {fr.message}")

        self._result_text.setPlainText("\n".join(lines))

    # ── 属性（便于测试访问） ─────────────────────────────

    @property
    def run_button(self) -> QPushButton:
        return self._run_btn

    @property
    def fix_button(self) -> QPushButton:
        return self._fix_btn

    @property
    def apply_fix_button(self) -> QPushButton:
        return self._apply_fix_btn

    @property
    def error_label(self) -> QLabel:
        return self._error_label

    @property
    def warning_label(self) -> QLabel:
        return self._warning_label

    @property
    def info_label(self) -> QLabel:
        return self._info_label

    @property
    def result_text(self) -> QTextEdit:
        return self._result_text

    @property
    def last_output(self) -> HealthCheckOutputDTO | None:
        return self._last_output

    def render_dto(self, dto: HealthCheckOutputDTO) -> None:
        """公开渲染方法（供测试使用）"""
        self._render(dto)

    def render_result(self, result: HealthCheckResultDTO) -> str:
        """渲染单个检查结果为字符串（供测试使用）"""
        label = _SEVERITY_LABELS.get(result.severity, str(result.severity))
        return f"{label} [{result.check_id}]: {result.message}"
