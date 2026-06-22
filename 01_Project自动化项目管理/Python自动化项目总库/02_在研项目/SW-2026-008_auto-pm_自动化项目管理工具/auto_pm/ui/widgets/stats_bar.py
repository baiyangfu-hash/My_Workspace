"""统计栏组件

展示项目统计数据：总数、各阶段分布、各技术栈分布、各业务线分布。
横向分组排列，通过 set_stat(key, value) 更新单项。
"""

from __future__ import annotations

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

_STYLE = """
QFrame#StatsBar {
    background: #f5f6f8;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
}
QLabel#statGroupTitle { font-size: 10px; color: #999; }
QLabel#statItem { font-size: 11px; color: #555; }
QLabel#statValue { font-size: 13px; font-weight: bold; color: #222; }
QLabel#statSep { color: #ccc; font-size: 16px; }
"""

# 阶段分布项
_PHASE_KEYS: list[str] = ["developing", "commissioning", "production", "archived"]
_PHASE_LABELS: dict[str, str] = {
    "developing": "开发中",
    "commissioning": "调试中",
    "production": "生产中",
    "archived": "已归档",
}

# 技术栈分布项
_STACK_KEYS: list[str] = ["plc", "python", "unknown"]
_STACK_LABELS: dict[str, str] = {"plc": "PLC", "python": "Python", "unknown": "未知"}

# 业务线分布项
_BL_KEYS: list[str] = ["SW", "DJ", "ZD", "XT", "WX"]


class StatsBar(QFrame):
    """统计栏

    横向分组排列：总计 / 阶段分布 / 技术栈分布 / 业务线分布。
    通过 set_stat(key, value) 更新单项，key 形如 total/phase_developing/stack_plc/bl_SW。
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("StatsBar")
        self.setStyleSheet(_STYLE)
        self._values: dict[str, QLabel] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(12)

        self._add_group(layout, "总计", [("total", "项目")])
        layout.addWidget(self._make_sep())

        phase_items = [(f"phase_{k}", _PHASE_LABELS[k]) for k in _PHASE_KEYS]
        self._add_group(layout, "阶段", phase_items)
        layout.addWidget(self._make_sep())

        stack_items = [(f"stack_{k}", _STACK_LABELS[k]) for k in _STACK_KEYS]
        self._add_group(layout, "技术栈", stack_items)
        layout.addWidget(self._make_sep())

        bl_items = [(f"bl_{k}", k) for k in _BL_KEYS]
        self._add_group(layout, "业务线", bl_items)

        layout.addStretch(1)

    def _add_group(
        self,
        parent_layout: QHBoxLayout,
        title: str,
        items: list[tuple[str, str]],
    ) -> None:
        """添加一个统计分组（标题 + 横向指标项）"""
        group = QWidget()
        v = QVBoxLayout(group)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(2)

        title_label = QLabel(title)
        title_label.setObjectName("statGroupTitle")
        v.addWidget(title_label)

        h = QHBoxLayout()
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(8)
        for key, label_text in items:
            item = QWidget()
            ih = QHBoxLayout(item)
            ih.setContentsMargins(0, 0, 0, 0)
            ih.setSpacing(2)
            lbl = QLabel(label_text)
            lbl.setObjectName("statItem")
            val = QLabel("0")
            val.setObjectName("statValue")
            ih.addWidget(lbl)
            ih.addWidget(val)
            h.addWidget(item)
            self._values[key] = val
        v.addLayout(h)
        parent_layout.addWidget(group)

    @staticmethod
    def _make_sep() -> QLabel:
        sep = QLabel("|")
        sep.setObjectName("statSep")
        return sep

    def set_stat(self, key: str, value: int | str) -> None:
        """更新指定统计项的值"""
        label = self._values.get(key)
        if label is not None:
            label.setText(str(value))
