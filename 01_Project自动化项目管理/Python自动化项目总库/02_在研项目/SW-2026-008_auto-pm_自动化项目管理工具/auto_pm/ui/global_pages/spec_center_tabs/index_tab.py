"""Tab2 索引 - 三域规范列表 + 打开文件 + 搜索框

对接 IndexService（通过 SpecCenterAdapter），列出 PM/PLC/Python 三域规范，
支持搜索框过滤和"打开"按钮调用系统默认程序打开规范文件。
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from auto_pm.logging.logging import setup_logger
from auto_pm.ui.global_pages.spec_center_dto import (
    SpecCenterAdapter,
    SpecEntryDTO,
)

log = setup_logger(log_level="INFO", app_name="auto_pm")

__all__ = ["IndexTab"]

# 域中文标签 + 顺序
_DOMAIN_LABELS: dict[str, str] = {
    "pm": "项目管理域 (PM)",
    "plc": "PLC自动化域 (PLC)",
    "python": "Python开发域 (Python)",
    "cross-domain": "跨域通用 (Cross-Domain)",
}
_DOMAIN_ORDER = ["pm", "plc", "python", "cross-domain"]


class IndexTab(QWidget):
    """Tab2 索引：三域规范列表 + 搜索 + 打开文件"""

    def __init__(
        self,
        adapter: SpecCenterAdapter,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._adapter = adapter
        # 规范行容器：{spec_id: row_widget}
        self._spec_rows: dict[str, QWidget] = {}
        # 打开按钮：{spec_id: button}
        self._open_buttons: dict[str, QPushButton] = {}
        # 缓存的 DTO 列表
        self._entries: list[SpecEntryDTO] = []
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        # 标题
        title = QLabel("规范索引")
        title.setObjectName("specTitle")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #222;")
        layout.addWidget(title)

        # 工具栏：搜索框 + 刷新按钮
        toolbar = QWidget()
        h = QHBoxLayout(toolbar)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(8)

        self._search_box = QLineEdit()
        self._search_box.setObjectName("searchBox")
        self._search_box.setPlaceholderText("搜索规范（spec_id/标题/域）...")
        self._search_box.setStyleSheet(
            "QLineEdit { border: 1px solid #d0d0d0; border-radius: 4px; padding: 4px 8px; font-size: 12px; }"
        )
        self._search_box.textChanged.connect(self._on_search_changed)
        h.addWidget(self._search_box, 1)

        self._refresh_btn = QPushButton("刷新索引")
        self._refresh_btn.setObjectName("toolBtn")
        self._refresh_btn.setStyleSheet(
            "QPushButton { background: #f5f5f5; border: 1px solid #d0d0d0; border-radius: 4px; padding: 4px 12px; }"
        )
        self._refresh_btn.clicked.connect(self.refresh)
        h.addWidget(self._refresh_btn)

        layout.addWidget(toolbar)

        # 分区容器（按域分组）
        self._groups: dict[str, QGroupBox] = {}
        self._group_layouts: dict[str, QVBoxLayout] = {}
        for domain_key in _DOMAIN_ORDER:
            label = _DOMAIN_LABELS[domain_key]
            group = QGroupBox(label)
            group.setStyleSheet(
                "QGroupBox { background: #ffffff; border: 1px solid #e0e0e0; "
                "border-radius: 6px; margin-top: 14px; font-weight: bold; }"
                "QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; "
                "padding: 2px 8px; color: #4a90d9; }"
            )
            v = QVBoxLayout(group)
            v.setContentsMargins(12, 16, 12, 12)
            v.setSpacing(6)
            self._groups[domain_key] = group
            self._group_layouts[domain_key] = v
            layout.addWidget(group)

        layout.addStretch(1)

    def refresh(self) -> None:
        """刷新规范索引"""
        try:
            self._entries = self._adapter.list_entries()
            self._rebuild_rows()
        except Exception as e:
            log.error("刷新规范索引失败: %s", e)

    def _rebuild_rows(self) -> None:
        """根据 _entries 重建所有规范行"""
        # 清空旧行
        for row in self._spec_rows.values():
            row.deleteLater()
        self._spec_rows.clear()
        self._open_buttons.clear()

        # 按域分组
        grouped: dict[str, list[SpecEntryDTO]] = {}
        for entry in self._entries:
            grouped.setdefault(entry.domain, []).append(entry)

        # 渲染
        for domain_key in _DOMAIN_ORDER:
            entries = grouped.get(domain_key, [])
            for entry in entries:
                row = self._build_spec_row(entry)
                self._group_layouts[domain_key].addWidget(row)

        # 应用当前搜索过滤
        self._apply_filter(self._search_box.text())

    def _build_spec_row(self, entry: SpecEntryDTO) -> QWidget:
        """构建单个规范行：[spec_id] [标题] ... [打开]"""
        row = QWidget()
        h = QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(12)

        id_label = QLabel(entry.spec_id)
        id_label.setObjectName("specCode")
        id_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #4a90d9;")
        id_label.setMinimumWidth(110)
        h.addWidget(id_label)

        title_label = QLabel(entry.title)
        title_label.setStyleSheet("font-size: 13px; color: #333;")
        h.addWidget(title_label, 1)

        version_label = QLabel(entry.version or "—")
        version_label.setStyleSheet("font-size: 12px; color: #888;")
        version_label.setMinimumWidth(70)
        h.addWidget(version_label)

        open_btn = QPushButton("打开")
        open_btn.setStyleSheet(
            "QPushButton { background: #4a90d9; color: white; border: none; "
            "border-radius: 4px; padding: 4px 12px; font-size: 12px; }"
            "QPushButton:hover { background: #3a7bc8; }"
            "QPushButton:disabled { background: #cccccc; color: #888; }"
        )
        open_btn.setEnabled(entry.file_exists)
        if not entry.file_exists:
            open_btn.setToolTip("未找到规范文件")
        open_btn.clicked.connect(
            lambda checked=False, sid=entry.spec_id: self._on_open_spec(sid)
        )
        h.addWidget(open_btn)

        self._spec_rows[entry.spec_id] = row
        self._open_buttons[entry.spec_id] = open_btn
        return row

    # ── 交互 ─────────────────────────────────────────────

    def _on_open_spec(self, spec_id: str) -> None:
        """打开规范文件（调用系统默认程序）"""
        info = self._adapter.registry.get_spec(spec_id)
        if info is None or not info.canonical_path:
            log.warning("规范文件未找到: %s", spec_id)
            return
        path = self._adapter.workspace / info.canonical_path
        if not path.exists():
            log.warning("规范文件不存在: %s", path)
            return
        url = QUrl.fromLocalFile(str(path))
        if not QDesktopServices.openUrl(url):
            log.error("打开规范文件失败: %s", path)

    def _on_search_changed(self, text: str) -> None:
        """搜索框文本变化时过滤规范行"""
        self._apply_filter(text)

    def _apply_filter(self, text: str) -> None:
        """应用搜索过滤"""
        keyword = text.strip().lower()
        for spec_id, row in self._spec_rows.items():
            if not keyword:
                row.setHidden(False)
                continue
            # 在缓存的 entries 中查找
            entry = next((e for e in self._entries if e.spec_id == spec_id), None)
            if entry is None:
                row.setHidden(True)
                continue
            match = (
                keyword in entry.spec_id.lower()
                or keyword in entry.title.lower()
                or keyword in entry.domain.lower()
            )
            row.setHidden(not match)

    # ── 属性（便于测试访问） ─────────────────────────────

    @property
    def search_box(self) -> QLineEdit:
        return self._search_box

    @property
    def refresh_button(self) -> QPushButton:
        return self._refresh_btn

    @property
    def spec_rows(self) -> dict[str, QWidget]:
        return self._spec_rows

    @property
    def open_buttons(self) -> dict[str, QPushButton]:
        return self._open_buttons

    def get_open_button(self, spec_id: str) -> QPushButton | None:
        return self._open_buttons.get(spec_id)

    def get_spec_row(self, spec_id: str) -> QWidget | None:
        return self._spec_rows.get(spec_id)

    @property
    def entries(self) -> list[SpecEntryDTO]:
        return self._entries

    def find_spec_file(self, spec_id: str) -> Path | None:
        """查找规范文件路径（用于测试）"""
        info = self._adapter.registry.get_spec(spec_id)
        if info is None or not info.canonical_path:
            return None
        path = self._adapter.workspace / info.canonical_path
        return path if path.exists() else None
