"""Tab4 Frontmatter - 批量预览/应用（dry-run/apply）

对接 FrontmatterService（通过 SpecCenterAdapter），列出每个规范的 frontmatter 状态，
支持预览将添加的 frontmatter，以及实际应用写入。
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from auto_pm.logging.logging import setup_logger
from auto_pm.ui.global_pages.spec_center_dto import (
    FrontmatterPreviewDTO,
    SpecCenterAdapter,
)

log = setup_logger(log_level="INFO", app_name="auto_pm")

__all__ = ["FrontmatterTab"]

# 状态中文标签
_STATUS_LABELS: dict[str, str] = {
    "pending": "待添加",
    "applied": "已应用",
    "skipped": "已跳过",
    "error": "错误",
}

_STATUS_COLORS: dict[str, str] = {
    "pending": "#f0ad4e",
    "applied": "#5cb85c",
    "skipped": "#999999",
    "error": "#d9534f",
}


class FrontmatterTab(QWidget):
    """Tab4 Frontmatter：批量预览/应用"""

    def __init__(
        self,
        adapter: SpecCenterAdapter,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._adapter = adapter
        self._items: list[FrontmatterPreviewDTO] = []
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        # 标题
        title = QLabel("Frontmatter 同步")
        title.setObjectName("specTitle")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #222;")
        layout.addWidget(title)

        # 摘要栏
        summary = QWidget()
        h = QHBoxLayout(summary)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(12)

        self._total_label = QLabel("总数: 0")
        self._total_label.setStyleSheet("font-size: 13px; color: #333; font-weight: bold;")
        h.addWidget(self._total_label)

        self._pending_label = QLabel("待添加: 0")
        self._pending_label.setStyleSheet("font-size: 13px; color: #f0ad4e; font-weight: bold;")
        h.addWidget(self._pending_label)

        self._applied_label = QLabel("已应用: 0")
        self._applied_label.setStyleSheet("font-size: 13px; color: #5cb85c; font-weight: bold;")
        h.addWidget(self._applied_label)

        self._error_label = QLabel("错误: 0")
        self._error_label.setStyleSheet("font-size: 13px; color: #d9534f; font-weight: bold;")
        h.addWidget(self._error_label)

        h.addStretch(1)
        layout.addWidget(summary)

        # 工具栏
        toolbar = QWidget()
        h2 = QHBoxLayout(toolbar)
        h2.setContentsMargins(0, 0, 0, 0)
        h2.setSpacing(8)

        self._preview_btn = QPushButton("预览")
        self._preview_btn.setStyleSheet(
            "QPushButton { background: #4a90d9; color: white; border: none; "
            "border-radius: 4px; padding: 6px 14px; }"
            "QPushButton:hover { background: #3a7bc8; }"
        )
        self._preview_btn.clicked.connect(self.preview)
        h2.addWidget(self._preview_btn)

        self._apply_btn = QPushButton("应用（写入）")
        self._apply_btn.setStyleSheet(
            "QPushButton { background: #f5f5f5; border: 1px solid #d0d0d0; "
            "border-radius: 4px; padding: 6px 14px; }"
        )
        self._apply_btn.clicked.connect(self.apply)
        self._apply_btn.setEnabled(False)
        h2.addWidget(self._apply_btn)

        h2.addStretch(1)
        layout.addWidget(toolbar)

        # 结果表格
        self._table = QTableWidget(0, 5)
        self._table.setHorizontalHeaderLabels(["spec_id", "标题/路径", "状态", "已有FM", "新FM预览"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setStyleSheet(
            "QTableWidget { background: #ffffff; border: 1px solid #e0e0e0; "
            "border-radius: 4px; font-size: 12px; }"
            "QHeaderView::section { background: #f5f5f5; padding: 4px; border: none; "
            "border-bottom: 1px solid #e0e0e0; font-weight: bold; }"
        )
        layout.addWidget(self._table, 1)

    def preview(self) -> None:
        """预览 Frontmatter"""
        try:
            self._items = self._adapter.preview_frontmatter()
            self._render(self._items)
            pending_count = sum(1 for i in self._items if i.status == "pending")
            self._apply_btn.setEnabled(pending_count > 0)
        except Exception as e:
            log.error("预览 Frontmatter 失败: %s", e)
            QMessageBox.critical(self, "预览失败", str(e))

    def apply(self) -> None:
        """应用 Frontmatter（实际写入）"""
        if not self._items:
            return
        pending = [i for i in self._items if i.status == "pending"]
        if not pending:
            QMessageBox.information(self, "无操作", "没有待应用的 Frontmatter 项")
            return

        reply = QMessageBox.question(
            self,
            "确认应用",
            f"将向 {len(pending)} 个规范文件写入 Frontmatter，确认继续？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            modified, skipped, errors = self._adapter.apply_frontmatter(self._items)
            QMessageBox.information(
                self,
                "应用完成",
                f"应用完成：修改 {modified}，跳过 {skipped}，错误 {errors}",
            )
            # 刷新预览
            self.preview()
        except Exception as e:
            log.error("应用 Frontmatter 失败: %s", e)
            QMessageBox.critical(self, "应用失败", str(e))

    def _render(self, items: list[FrontmatterPreviewDTO]) -> None:
        """渲染 Frontmatter 预览"""
        # 摘要
        total = len(items)
        pending = sum(1 for i in items if i.status == "pending")
        applied = sum(1 for i in items if i.status == "applied")
        errors = sum(1 for i in items if i.status == "error")
        self._total_label.setText(f"总数: {total}")
        self._pending_label.setText(f"待添加: {pending}")
        self._applied_label.setText(f"已应用: {applied}")
        self._error_label.setText(f"错误: {errors}")

        # 表格
        self._table.setRowCount(len(items))
        for row, item in enumerate(items):
            id_item = QTableWidgetItem(item.spec_id)
            id_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self._table.setItem(row, 0, id_item)

            # 路径或标题（取文件名）
            from pathlib import Path
            name = Path(str(item.file_path)).name if item.file_path else ""
            path_item = QTableWidgetItem(name)
            path_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self._table.setItem(row, 1, path_item)

            status_text = _STATUS_LABELS.get(item.status, item.status)
            status_item = QTableWidgetItem(status_text)
            color = _STATUS_COLORS.get(item.status, "#333")
            status_item.setForeground(QColor(color))
            status_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self._table.setItem(row, 2, status_item)

            has_fm_text = "是" if item.has_frontmatter else "否"
            fm_item = QTableWidgetItem(has_fm_text)
            fm_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self._table.setItem(row, 3, fm_item)

            preview_text = item.new_frontmatter[:80] + "..." if len(item.new_frontmatter) > 80 else item.new_frontmatter
            preview_item = QTableWidgetItem(preview_text)
            preview_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self._table.setItem(row, 4, preview_item)

    # ── 属性（便于测试访问） ─────────────────────────────

    @property
    def preview_button(self) -> QPushButton:
        return self._preview_btn

    @property
    def apply_button(self) -> QPushButton:
        return self._apply_btn

    @property
    def table(self) -> QTableWidget:
        return self._table

    @property
    def total_label(self) -> QLabel:
        return self._total_label

    @property
    def pending_label(self) -> QLabel:
        return self._pending_label

    @property
    def items(self) -> list[FrontmatterPreviewDTO]:
        return self._items

    def render_dto(self, items: list[FrontmatterPreviewDTO]) -> None:
        """公开渲染方法（供测试使用）"""
        self._items = items
        self._render(items)
