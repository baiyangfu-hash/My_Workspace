"""Tab5 报告 - markdown/json 格式选择 + 生成 + 保存

对接 ReportService（通过 SpecCenterAdapter），生成规范元数据汇总报告，
支持 markdown 和 json 两种格式，提供保存对话框。
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from auto_pm.logging.logging import setup_logger
from auto_pm.ui.global_pages.spec_center_dto import (
    ReportOutputDTO,
    SpecCenterAdapter,
)

log = setup_logger(log_level="INFO", app_name="auto_pm")

__all__ = ["ReportTab"]

_FORMAT_LABELS: dict[str, str] = {
    "markdown": "Markdown (.md)",
    "json": "JSON (.json)",
}


class ReportTab(QWidget):
    """Tab5 报告：生成 + 保存"""

    def __init__(
        self,
        adapter: SpecCenterAdapter,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._adapter = adapter
        self._last_output: ReportOutputDTO | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        # 标题
        title = QLabel("规范元数据汇总报告")
        title.setObjectName("specTitle")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #222;")
        layout.addWidget(title)

        # 工具栏
        toolbar = QWidget()
        h = QHBoxLayout(toolbar)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(8)

        h.addWidget(QLabel("格式:"))
        self._format_combo = QComboBox()
        for fmt, label in _FORMAT_LABELS.items():
            self._format_combo.addItem(label, fmt)
        self._format_combo.setStyleSheet(
            "QComboBox { border: 1px solid #d0d0d0; border-radius: 4px; padding: 4px 8px; }"
        )
        h.addWidget(self._format_combo)

        self._generate_btn = QPushButton("生成报告")
        self._generate_btn.setStyleSheet(
            "QPushButton { background: #4a90d9; color: white; border: none; "
            "border-radius: 4px; padding: 6px 14px; }"
            "QPushButton:hover { background: #3a7bc8; }"
        )
        self._generate_btn.clicked.connect(self.generate)
        h.addWidget(self._generate_btn)

        self._save_btn = QPushButton("另存为...")
        self._save_btn.setStyleSheet(
            "QPushButton { background: #f5f5f5; border: 1px solid #d0d0d0; "
            "border-radius: 4px; padding: 6px 14px; }"
        )
        self._save_btn.clicked.connect(self.save_as)
        self._save_btn.setEnabled(False)
        h.addWidget(self._save_btn)

        h.addStretch(1)
        layout.addWidget(toolbar)

        # 报告路径标签
        self._path_label = QLabel("尚未生成")
        self._path_label.setStyleSheet("font-size: 12px; color: #888;")
        layout.addWidget(self._path_label)

        # 报告内容展示
        self._content_text = QTextEdit()
        self._content_text.setReadOnly(True)
        self._content_text.setStyleSheet(
            "QTextEdit { background: #ffffff; border: 1px solid #e0e0e0; "
            "border-radius: 4px; font-family: Consolas, 'Courier New', monospace; font-size: 12px; }"
        )
        self._content_text.setPlaceholderText("点击『生成报告』开始生成...")
        layout.addWidget(self._content_text, 1)

    def generate(self) -> None:
        """生成报告"""
        fmt = self._format_combo.currentData() or "markdown"
        try:
            output = self._adapter.generate_report(fmt=fmt)
            self._last_output = output
            self._render(output)
            self._save_btn.setEnabled(True)
        except Exception as e:
            log.error("生成报告失败: %s", e)
            QMessageBox.critical(self, "生成失败", str(e))

    def save_as(self) -> None:
        """另存为对话框"""
        if self._last_output is None:
            return
        fmt = self._last_output.fmt
        default_suffix = ".md" if fmt == "markdown" else ".json"
        default_name = f"规范元数据汇总报告{default_suffix}"
        default_path = str(self._adapter.workspace / default_name)

        path, _ = QFileDialog.getSaveFileName(
            self,
            "保存报告",
            default_path,
            f"{'Markdown' if fmt == 'markdown' else 'JSON'} 文件 (*{default_suffix});;所有文件 (*.*)",
        )
        if not path:
            return

        try:
            out_path = Path(path)
            out_path.write_text(self._last_output.content, encoding="utf-8")
            QMessageBox.information(self, "保存成功", f"报告已保存到：\n{out_path}")
        except OSError as e:
            log.error("保存报告失败: %s", e)
            QMessageBox.critical(self, "保存失败", str(e))

    def _render(self, dto: ReportOutputDTO) -> None:
        """渲染报告"""
        self._content_text.setPlainText(dto.content)
        self._path_label.setText(f"已保存到: {dto.saved_path}")

    # ── 属性（便于测试访问） ─────────────────────────────

    @property
    def format_combo(self) -> QComboBox:
        return self._format_combo

    @property
    def generate_button(self) -> QPushButton:
        return self._generate_btn

    @property
    def save_button(self) -> QPushButton:
        return self._save_btn

    @property
    def path_label(self) -> QLabel:
        return self._path_label

    @property
    def content_text(self) -> QTextEdit:
        return self._content_text

    @property
    def last_output(self) -> ReportOutputDTO | None:
        return self._last_output

    def render_dto(self, dto: ReportOutputDTO) -> None:
        """公开渲染方法（供测试使用）"""
        self._last_output = dto
        self._render(dto)
        self._save_btn.setEnabled(True)
