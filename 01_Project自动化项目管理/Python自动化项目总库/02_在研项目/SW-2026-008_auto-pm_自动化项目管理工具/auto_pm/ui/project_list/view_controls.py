"""视图控制栏组件

提供视图模式切换（卡片/列表）、排序、分组模式选择。
发射 view_mode_changed / sort_changed / group_mode_changed 信号。
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QToolButton,
    QWidget,
)

__all__ = ["ViewControls"]

# 视图模式
VIEW_MODE_CARD = "card"
VIEW_MODE_LIST = "list"

# 排序模式
SORT_ID_ASC = "id_asc"
SORT_ID_DESC = "id_desc"
SORT_PHASE = "phase"
SORT_MTIME = "mtime"

# 分组模式
GROUP_STACK_BL = "stack_bl"
GROUP_STACK_PHASE = "stack_phase"
GROUP_BL = "bl"
GROUP_PHASE = "phase"
GROUP_NONE = "none"


class ViewControls(QFrame):
    """视图控制栏

    包含三组控件：
    - 视图切换按钮组（卡片视图 / 列表视图，互斥）
    - 排序下拉框（编号↑ / 编号↓ / 阶段 / 修改时间）
    - 分组下拉框（总库+业务线 / 总库+阶段 / 业务线 / 阶段 / 不分组）

    Signals:
        view_mode_changed(str): 'card' | 'list'
        sort_changed(str): 'id_asc' | 'id_desc' | 'phase' | 'mtime'
        group_mode_changed(str): 'stack_bl' | 'stack_phase' | 'bl' | 'phase' | 'none'
    """

    view_mode_changed = Signal(str)
    sort_changed = Signal(str)
    group_mode_changed = Signal(str)

    _SORT_OPTIONS: list[tuple[str, str]] = [
        (SORT_ID_ASC, "编号↑"),
        (SORT_ID_DESC, "编号↓"),
        (SORT_PHASE, "阶段"),
        (SORT_MTIME, "修改时间"),
    ]

    _GROUP_OPTIONS: list[tuple[str, str]] = [
        (GROUP_STACK_BL, "总库+业务线"),
        (GROUP_STACK_PHASE, "总库+阶段"),
        (GROUP_BL, "业务线"),
        (GROUP_PHASE, "阶段"),
        (GROUP_NONE, "不分组"),
    ]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # 视图切换按钮组
        self._card_btn = QToolButton()
        self._card_btn.setText("卡片")
        self._card_btn.setToolTip("卡片视图")
        self._card_btn.setCheckable(True)
        self._card_btn.setChecked(True)
        self._card_btn.setMinimumWidth(50)

        self._list_btn = QToolButton()
        self._list_btn.setText("列表")
        self._list_btn.setToolTip("列表视图")
        self._list_btn.setCheckable(True)
        self._list_btn.setMinimumWidth(50)

        self._view_group = QButtonGroup(self)
        self._view_group.setExclusive(True)
        self._view_group.addButton(self._card_btn, 0)
        self._view_group.addButton(self._list_btn, 1)
        self._view_group.idClicked.connect(self._on_view_mode_clicked)

        layout.addWidget(self._card_btn)
        layout.addWidget(self._list_btn)

        layout.addWidget(self._make_sep())

        # 排序下拉框
        layout.addWidget(QLabel("排序:"))
        self._sort_combo = QComboBox()
        self._sort_combo.setMinimumWidth(80)
        self._sort_combo.setMaximumWidth(120)
        for value, label in self._SORT_OPTIONS:
            self._sort_combo.addItem(label, value)
        self._sort_combo.currentIndexChanged.connect(self._on_sort_changed)
        layout.addWidget(self._sort_combo)

        layout.addWidget(self._make_sep())

        # 分组下拉框
        layout.addWidget(QLabel("分组:"))
        self._group_combo = QComboBox()
        self._group_combo.setMinimumWidth(80)
        self._group_combo.setMaximumWidth(140)
        for value, label in self._GROUP_OPTIONS:
            self._group_combo.addItem(label, value)
        self._group_combo.currentIndexChanged.connect(self._on_group_changed)
        layout.addWidget(self._group_combo)

        layout.addStretch(1)

    @staticmethod
    def _make_sep() -> QLabel:
        sep = QLabel("|")
        sep.setStyleSheet("color: #ccc;")
        return sep

    # ── 事件处理 ──────────────────────────────────────────

    def _on_view_mode_clicked(self, btn_id: int) -> None:
        mode = VIEW_MODE_CARD if btn_id == 0 else VIEW_MODE_LIST
        self.view_mode_changed.emit(mode)

    def _on_sort_changed(self, _index: int) -> None:
        value = self._sort_combo.currentData() or SORT_ID_ASC
        self.sort_changed.emit(value)

    def _on_group_changed(self, _index: int) -> None:
        value = self._group_combo.currentData() or GROUP_STACK_BL
        self.group_mode_changed.emit(value)

    # ── 外部设置 ──────────────────────────────────────────

    def set_view_mode(self, mode: str) -> None:
        """编程式切换视图模式"""
        if mode == VIEW_MODE_CARD:
            self._card_btn.setChecked(True)
        elif mode == VIEW_MODE_LIST:
            self._list_btn.setChecked(True)

    def set_sort_mode(self, mode: str) -> None:
        """编程式设置排序模式"""
        for i in range(self._sort_combo.count()):
            if self._sort_combo.itemData(i) == mode:
                self._sort_combo.setCurrentIndex(i)
                return

    def set_group_mode(self, mode: str) -> None:
        """编程式设置分组模式"""
        for i in range(self._group_combo.count()):
            if self._group_combo.itemData(i) == mode:
                self._group_combo.setCurrentIndex(i)
                return
