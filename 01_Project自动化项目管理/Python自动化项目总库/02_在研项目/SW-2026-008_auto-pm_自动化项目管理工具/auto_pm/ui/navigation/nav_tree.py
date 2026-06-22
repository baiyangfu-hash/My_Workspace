"""导航树组件

QTreeWidget 树形导航：总库分类（PLC/Python）→ 阶段子节点 → 功能节点。
支持项目计数徽标和点击信号发射。

树形结构：
::

    📂 PLC 总库 (count)
      🟦 在研项目 (count)
      🟨 调试中 (count)
      🟩 生产中 (count)
      ⬜ 已归档 (count)
    📂 Python 总库 (count)
      🟦 在研项目 (count)
      ...
    ────────────────────
    📋 全部项目
    🔄 变更中心
    📐 规范中心
    📦 模板管理
    📊 报告中心
    ⚙️ 系统设置
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem

from auto_pm.models import ProjectInfo
from auto_pm.ui.navigation.nav_model import NavNode

# 总库定义：(stack_value, label, icon)
_STACK_DEFS: list[tuple[str, str, str]] = [
    ("plc", "PLC 总库", "📂"),
    ("python", "Python 总库", "📂"),
]

# 阶段定义：(phase_value, label, icon, color)
_PHASE_DEFS: list[tuple[str, str, str, str]] = [
    ("developing", "在研项目", "🟦", "#3498db"),
    ("commissioning", "调试中", "🟨", "#f1c40f"),
    ("production", "生产中", "🟩", "#2ecc71"),
    ("archived", "已归档", "⬜", "#95a5a6"),
]

# 功能节点定义：(page_id, label)
_FUNCTION_DEFS: list[tuple[str, str]] = [
    ("all_projects", "📋 全部项目"),
    ("change_center", "🔄 变更中心"),
    ("spec_center", "📐 规范中心"),
    ("template", "📦 模板管理"),
    ("report", "📊 报告中心"),
    ("settings", "⚙️ 系统设置"),
]


class NavigationTree(QTreeWidget):
    """导航树

    树形结构：
    - 总库节点（PLC/Python）→ 阶段子节点（在研/调试/生产/归档）
    - 分隔线
    - 功能节点（全部项目/变更中心/规范中心/模板管理/报告中心/系统设置）

    Signals:
        project_filter_requested(str, str): 点击总库/阶段节点时发射
            参数为 (stack, phase)，phase 为空字符串表示仅按 stack 筛选
        page_switch_requested(str): 点击功能节点时发射，参数为 page_id
    """

    project_filter_requested = Signal(str, str)
    page_switch_requested = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("navTree")
        self.setHeaderHidden(True)
        self.setIndentation(16)
        self.setFixedWidth(180)
        # 节点引用，便于更新计数和测试
        self._stack_nodes: dict[str, QTreeWidgetItem] = {}
        self._phase_nodes: dict[tuple[str, str], QTreeWidgetItem] = {}
        self._function_nodes: dict[str, QTreeWidgetItem] = {}
        self._build_tree()
        self.itemClicked.connect(self._on_item_clicked)

    # ── UI 构建 ────────────────────────────────────────────

    def _build_tree(self) -> None:
        """构建树形结构"""
        # 1. 总库节点 + 阶段子节点
        for stack_value, stack_label, stack_icon in _STACK_DEFS:
            stack_node = NavNode(
                node_type="stack",
                label=stack_label,
                filter_stack=stack_value,
            )
            stack_item = QTreeWidgetItem(self)
            stack_item.setData(0, Qt.UserRole, stack_node)
            stack_item.setText(0, f"{stack_icon} {stack_label} (0)")
            stack_item.setForeground(0, QColor("#2c3e50"))

            # 阶段子节点
            for phase_value, phase_label, phase_icon, phase_color in _PHASE_DEFS:
                phase_node = NavNode(
                    node_type="phase",
                    label=phase_label,
                    filter_stack=stack_value,
                    filter_phase=phase_value,
                )
                phase_item = QTreeWidgetItem(stack_item)
                phase_item.setData(0, Qt.UserRole, phase_node)
                phase_item.setText(0, f"{phase_icon} {phase_label} (0)")
                phase_item.setForeground(0, QColor(phase_color))
                self._phase_nodes[(stack_value, phase_value)] = phase_item

            self._stack_nodes[stack_value] = stack_item
            self.expandItem(stack_item)

        # 2. 分隔线（不可选、不可点击）
        sep_item = QTreeWidgetItem(self)
        sep_item.setText(0, "─" * 20)
        sep_item.setFlags(Qt.NoItemFlags)

        # 3. 功能节点
        for page_id, label in _FUNCTION_DEFS:
            func_node = NavNode(
                node_type="function",
                label=label,
                page_id=page_id,
            )
            func_item = QTreeWidgetItem(self)
            func_item.setData(0, Qt.UserRole, func_node)
            func_item.setText(0, label)
            self._function_nodes[page_id] = func_item

    # ── 计数更新 ──────────────────────────────────────────

    def update_counts(self, projects: list[ProjectInfo]) -> None:
        """接收项目列表，更新计数徽标

        - 按 stack 分组计数 → 总库节点
        - 按 stack+phase 分组计数 → 阶段子节点

        Args:
            projects: 项目列表（仅统计 stack 为 plc/python 的项目）
        """
        stack_counts: dict[str, int] = {}
        phase_counts: dict[tuple[str, str], int] = {}

        for proj in projects:
            stack = proj.stack or ""
            phase = proj.phase or ""
            if stack not in self._stack_nodes:
                continue
            stack_counts[stack] = stack_counts.get(stack, 0) + 1
            if phase and (stack, phase) in self._phase_nodes:
                phase_counts[(stack, phase)] = phase_counts.get((stack, phase), 0) + 1

        # 更新总库节点
        for stack_value, stack_label, stack_icon in _STACK_DEFS:
            item = self._stack_nodes.get(stack_value)
            if item is not None:
                count = stack_counts.get(stack_value, 0)
                item.setText(0, f"{stack_icon} {stack_label} ({count})")

        # 更新阶段子节点
        for phase_value, phase_label, phase_icon, _ in _PHASE_DEFS:
            for stack_value, _, _ in _STACK_DEFS:
                item = self._phase_nodes.get((stack_value, phase_value))
                if item is not None:
                    count = phase_counts.get((stack_value, phase_value), 0)
                    item.setText(0, f"{phase_icon} {phase_label} ({count})")

    # ── 点击处理 ──────────────────────────────────────────

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """点击节点处理

        - 总库节点 → 发射 project_filter_requested(stack, '')
        - 阶段子节点 → 发射 project_filter_requested(stack, phase)
        - 功能节点 → 发射 page_switch_requested(page_id)
        """
        node: NavNode | None = item.data(0, Qt.UserRole)
        if node is None:
            return
        if node.node_type == "stack":
            self.project_filter_requested.emit(node.filter_stack or "", "")
        elif node.node_type == "phase":
            self.project_filter_requested.emit(
                node.filter_stack or "", node.filter_phase or ""
            )
        elif node.node_type == "function":
            self.page_switch_requested.emit(node.page_id or "")
