"""Tab6 对比 - 保留旧对比功能，迁移到新 IndexService

基于 SpecCenterAdapter.compare_specs()，对比两个规范的文件内容。
用户从两个下拉框选择规范（spec_id），点击对比按钮查看差异。
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
from auto_pm.ui.global_pages.spec_center_dto import (
    CompareResultDTO,
    SpecCenterAdapter,
)

log = setup_logger(log_level="INFO", app_name="auto_pm")

__all__ = ["CompareTab"]


class CompareTab(QWidget):
    """Tab6 对比：对比两个规范文件内容"""

    def __init__(
        self,
        adapter: SpecCenterAdapter,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._adapter = adapter
        self._last_diff: CompareResultDTO | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        # 标题
        title = QLabel("规范对比")
        title.setObjectName("specTitle")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #222;")
        layout.addWidget(title)

        # 提示
        hint = QLabel("从下方下拉框选择两个规范，点击『对比』按钮查看差异")
        hint.setStyleSheet("font-size: 12px; color: #888;")
        layout.addWidget(hint)

        # 选择栏
        from PySide6.QtWidgets import QComboBox

        sel_bar = QWidget()
        h = QHBoxLayout(sel_bar)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(8)

        h.addWidget(QLabel("左侧:"))
        self._left_combo = QComboBox()
        self._left_combo.setStyleSheet(
            "QComboBox { border: 1px solid #d0d0d0; border-radius: 4px; padding: 4px 8px; min-width: 200px; }"
        )
        h.addWidget(self._left_combo)

        h.addWidget(QLabel("右侧:"))
        self._right_combo = QComboBox()
        self._right_combo.setStyleSheet(
            "QComboBox { border: 1px solid #d0d0d0; border-radius: 4px; padding: 4px 8px; min-width: 200px; }"
        )
        h.addWidget(self._right_combo)

        self._compare_btn = QPushButton("对比")
        self._compare_btn.setStyleSheet(
            "QPushButton { background: #4a90d9; color: white; border: none; "
            "border-radius: 4px; padding: 6px 14px; }"
            "QPushButton:hover { background: #3a7bc8; }"
            "QPushButton:disabled { background: #cccccc; color: #888; }"
        )
        self._compare_btn.clicked.connect(self.compare)
        self._compare_btn.setEnabled(False)
        h.addWidget(self._compare_btn)

        self._refresh_btn = QPushButton("刷新列表")
        self._refresh_btn.setStyleSheet(
            "QPushButton { background: #f5f5f5; border: 1px solid #d0d0d0; "
            "border-radius: 4px; padding: 6px 14px; }"
        )
        self._refresh_btn.clicked.connect(self.refresh)
        h.addWidget(self._refresh_btn)

        h.addStretch(1)
        layout.addWidget(sel_bar)

        # 结果展示
        self._result_text = QTextEdit()
        self._result_text.setReadOnly(True)
        self._result_text.setStyleSheet(
            "QTextEdit { background: #ffffff; border: 1px solid #e0e0e0; "
            "border-radius: 4px; font-family: Consolas, 'Courier New', monospace; font-size: 12px; }"
        )
        self._result_text.setPlaceholderText("选择两个规范后点击『对比』按钮...")
        layout.addWidget(self._result_text, 1)

    def refresh(self) -> None:
        """刷新规范列表（填充下拉框）"""
        try:
            entries = self._adapter.list_entries()
            self._left_combo.clear()
            self._right_combo.clear()
            for entry in entries:
                label = f"{entry.spec_id} - {entry.title}"
                self._left_combo.addItem(label, entry.spec_id)
                self._right_combo.addItem(label, entry.spec_id)
            self._compare_btn.setEnabled(len(entries) >= 2)
        except Exception as e:
            log.error("刷新规范列表失败: %s", e)

    def compare(self) -> None:
        """对比两个规范"""
        left_id = self._left_combo.currentData()
        right_id = self._right_combo.currentData()
        if not left_id or not right_id:
            return
        if left_id == right_id:
            QMessageBox.warning(self, "对比失败", "请选择两个不同的规范")
            return

        try:
            diff = self._adapter.compare_specs(left_id, right_id)
            self._last_diff = diff
            self._render(diff)
        except FileNotFoundError as e:
            QMessageBox.warning(self, "对比失败", f"规范文件不存在：\n{e}")
        except Exception as e:
            log.error("对比失败: %s", e)
            QMessageBox.critical(self, "对比失败", str(e))

    def _render(self, dto: CompareResultDTO) -> None:
        """渲染对比结果"""
        if dto.same:
            text = (
                f"规范 {dto.left_spec_id} 与 {dto.right_spec_id} 内容完全相同。\n\n"
                f"行数: {len(dto.left_lines)}"
            )
            self._result_text.setPlainText(text)
            return

        text_parts = [
            f"规范对比: {dto.left_spec_id} vs {dto.right_spec_id}",
            "",
            f"左侧文件: {dto.left_path} ({len(dto.left_lines)} 行)",
            f"右侧文件: {dto.right_path} ({len(dto.right_lines)} 行)",
            "",
            f"新增行（{dto.right_spec_id} 有而 {dto.left_spec_id} 无）：{len(dto.added)}",
            f"删除行（{dto.left_spec_id} 有而 {dto.right_spec_id} 无）：{len(dto.removed)}",
            "",
            "— 新增行预览（前 20 行）—",
            "\n".join(dto.added[:20]) if dto.added else "（无）",
            "",
            "— 删除行预览（前 20 行）—",
            "\n".join(dto.removed[:20]) if dto.removed else "（无）",
        ]
        self._result_text.setPlainText("\n".join(text_parts))

    # ── 属性（便于测试访问） ─────────────────────────────

    @property
    def left_combo(self):  # type: ignore[no-untyped-def]
        return self._left_combo

    @property
    def right_combo(self):  # type: ignore[no-untyped-def]
        return self._right_combo

    @property
    def compare_button(self) -> QPushButton:
        return self._compare_btn

    @property
    def refresh_button(self) -> QPushButton:
        return self._refresh_btn

    @property
    def result_text(self) -> QTextEdit:
        return self._result_text

    @property
    def last_diff(self) -> CompareResultDTO | None:
        return self._last_diff

    def render_dto(self, dto: CompareResultDTO) -> None:
        """公开渲染方法（供测试使用）"""
        self._last_diff = dto
        self._render(dto)
