"""Tab1 概览 - 规范统计 + 健康摘要

展示规范总数、各域数量、生命周期分布、健康检查摘要。
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from auto_pm.logging.logging import setup_logger
from auto_pm.ui.global_pages.spec_center_dto import (
    SpecCenterAdapter,
    SpecOverviewDTO,
)

log = setup_logger(log_level="INFO", app_name="auto_pm")

__all__ = ["OverviewTab"]

# 域中文标签
_DOMAIN_LABELS: dict[str, str] = {
    "pm": "项目管理域 (PM)",
    "plc": "PLC自动化域 (PLC)",
    "python": "Python开发域 (Python)",
    "cross-domain": "跨域通用 (Cross-Domain)",
    "unknown": "未分类",
}

# 生命周期中文标签
_LIFECYCLE_LABELS: dict[str, str] = {
    "stable": "🟢 活跃 (stable)",
    "draft": "🔵 草稿 (draft)",
    "deprecated": "🟡 已废弃 (deprecated)",
    "archived": "⚪ 已归档 (archived)",
    "unknown": "未分类",
}

_LIFECYCLE_ORDER = ["stable", "draft", "deprecated", "archived", "unknown"]


class OverviewTab(QWidget):
    """Tab1 概览：规范统计 + 健康摘要"""

    def __init__(
        self,
        adapter: SpecCenterAdapter,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._adapter = adapter
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        # 标题
        title = QLabel("规范中心概览")
        title.setObjectName("specTitle")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #222;")
        layout.addWidget(title)

        # 总数卡片 + 健康摘要
        top_box = QGroupBox("规范统计")
        top_layout = QGridLayout(top_box)
        top_layout.setContentsMargins(12, 16, 12, 12)
        top_layout.setSpacing(8)

        self._total_label = QLabel("0")
        self._total_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #4a90d9;")
        self._total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_layout.addWidget(QLabel("规范总数"), 0, 0)
        top_layout.addWidget(self._total_label, 1, 0)

        self._error_label = QLabel("0")
        self._error_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #d9534f;")
        self._error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_layout.addWidget(QLabel("健康错误"), 0, 1)
        top_layout.addWidget(self._error_label, 1, 1)

        self._warning_label = QLabel("0")
        self._warning_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #f0ad4e;")
        self._warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_layout.addWidget(QLabel("健康警告"), 0, 2)
        top_layout.addWidget(self._warning_label, 1, 2)

        layout.addWidget(top_box)

        # 域分布
        self._domain_box = QGroupBox("按域分布")
        self._domain_layout = QVBoxLayout(self._domain_box)
        self._domain_layout.setContentsMargins(12, 16, 12, 12)
        self._domain_layout.setSpacing(4)
        layout.addWidget(self._domain_box)

        # 生命周期分布
        self._lifecycle_box = QGroupBox("按生命周期分布")
        self._lifecycle_layout = QVBoxLayout(self._lifecycle_box)
        self._lifecycle_layout.setContentsMargins(12, 16, 12, 12)
        self._lifecycle_layout.setSpacing(4)
        layout.addWidget(self._lifecycle_box)

        # 工具栏：刷新按钮
        toolbar = QWidget()
        h = QHBoxLayout(toolbar)
        h.setContentsMargins(0, 0, 0, 0)
        h.addStretch(1)
        self._refresh_btn = QPushButton("刷新概览")
        self._refresh_btn.setObjectName("toolBtn")
        self._refresh_btn.clicked.connect(self.refresh)
        h.addWidget(self._refresh_btn)
        layout.addWidget(toolbar)

        layout.addStretch(1)

    def refresh(self) -> None:
        """刷新概览数据"""
        try:
            dto = self._adapter.get_overview()
            self._render(dto)
        except Exception as e:
            log.error("刷新概览失败: %s", e)

    def _render(self, dto: SpecOverviewDTO) -> None:
        """渲染 DTO"""
        self._total_label.setText(str(dto.spec_count))
        self._error_label.setText(str(dto.health_summary.error_count))
        self._warning_label.setText(str(dto.health_summary.warning_count))

        # 域分布
        self._clear_layout(self._domain_layout)
        for domain_key in sorted(dto.domain_counts.keys()):
            label = _DOMAIN_LABELS.get(domain_key, domain_key)
            count = dto.domain_counts[domain_key]
            row = QLabel(f"{label}：{count} 个")
            row.setStyleSheet("font-size: 13px; color: #333;")
            self._domain_layout.addWidget(row)
        if not dto.domain_counts:
            self._domain_layout.addWidget(QLabel("（无数据）"))

        # 生命周期分布
        self._clear_layout(self._lifecycle_layout)
        for lc_key in _LIFECYCLE_ORDER:
            if lc_key not in dto.lifecycle_counts:
                continue
            label = _LIFECYCLE_LABELS.get(lc_key, lc_key)
            count = dto.lifecycle_counts[lc_key]
            row = QLabel(f"{label}：{count} 个")
            row.setStyleSheet("font-size: 13px; color: #333;")
            self._lifecycle_layout.addWidget(row)
        if not dto.lifecycle_counts:
            self._lifecycle_layout.addWidget(QLabel("（无数据）"))

    @staticmethod
    def _clear_layout(layout: QVBoxLayout) -> None:
        """清空 layout 内所有控件"""
        while layout.count():
            item = layout.takeAt(0)
            if item is None:
                continue
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    @property
    def refresh_button(self) -> QPushButton:
        return self._refresh_btn

    @property
    def total_label(self) -> QLabel:
        return self._total_label

    @property
    def error_label(self) -> QLabel:
        return self._error_label

    @property
    def warning_label(self) -> QLabel:
        return self._warning_label
