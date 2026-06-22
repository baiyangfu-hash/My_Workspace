"""筛选栏组件

提供技术栈/阶段/业务线三维筛选，发射 filterChanged(stack, phase, business_line)。
业务线支持联动设置（来自主窗口工具栏）。
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QLabel, QWidget


class FilterBar(QFrame):
    """筛选栏

    技术栈 + 阶段 + 业务线三维筛选。
    筛选条件变化时发射 filterChanged(stack, phase, business_line)。
    """

    filterChanged = Signal(str, str, str)

    _STACK_OPTIONS: list[tuple[str, str]] = [
        ("all", "全部技术栈"),
        ("plc", "PLC"),
        ("python", "Python"),
        ("unknown", "未知"),
    ]

    _PHASE_OPTIONS: list[tuple[str, str]] = [
        ("all", "全部阶段"),
        ("developing", "开发中"),
        ("commissioning", "调试中"),
        ("production", "生产中"),
        ("archived", "已归档"),
    ]

    _BL_OPTIONS: list[tuple[str, str]] = [
        ("all", "全部业务线"),
        ("SW", "SW 软件"),
        ("DJ", "DJ 单机"),
        ("ZD", "ZD 整线"),
        ("XT", "XT 升级"),
        ("WX", "WX 维保"),
    ]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        layout.addWidget(QLabel("技术栈:"))
        self._stack_combo = QComboBox()
        for value, label in self._STACK_OPTIONS:
            self._stack_combo.addItem(label, value)
        self._stack_combo.currentIndexChanged.connect(self._on_filter_changed)
        layout.addWidget(self._stack_combo)

        layout.addWidget(QLabel("阶段:"))
        self._phase_combo = QComboBox()
        for value, label in self._PHASE_OPTIONS:
            self._phase_combo.addItem(label, value)
        self._phase_combo.currentIndexChanged.connect(self._on_filter_changed)
        layout.addWidget(self._phase_combo)

        layout.addWidget(QLabel("业务线:"))
        self._bl_combo = QComboBox()
        for value, label in self._BL_OPTIONS:
            self._bl_combo.addItem(label, value)
        self._bl_combo.currentIndexChanged.connect(self._on_filter_changed)
        layout.addWidget(self._bl_combo)

        layout.addStretch(1)

    def _on_filter_changed(self) -> None:
        stack = self._stack_combo.currentData() or "all"
        phase = self._phase_combo.currentData() or "all"
        bl = self._bl_combo.currentData() or "all"
        self.filterChanged.emit(stack, phase, bl)

    def set_business_line(self, line: str) -> None:
        """联动设置业务线筛选（来自主窗口工具栏）"""
        for i in range(self._bl_combo.count()):
            if self._bl_combo.itemData(i) == line:
                self._bl_combo.setCurrentIndex(i)
                return

    def reset(self) -> None:
        """重置筛选条件"""
        self._stack_combo.setCurrentIndex(0)
        self._phase_combo.setCurrentIndex(0)
        self._bl_combo.setCurrentIndex(0)
