"""NavigationTree 导航树单元测试

测试内容：
- NavNode 数据模型默认值
- 树形结构构建（节点数量、层级、NavNode 数据）
- 点击总库节点 → project_filter_requested(stack, '') 信号
- 点击阶段子节点 → project_filter_requested(stack, phase) 信号
- 点击功能节点 → page_switch_requested(page_id) 信号
- update_counts() 徽标更新（总库/阶段/空列表/unknown 技术栈/空阶段）

遵循项目现有测试模式：自定义 qapp fixture + QT_QPA_PLATFORM=offscreen。
"""

from __future__ import annotations

import os

import pytest

# 必须在导入 PySide6 前设置离屏渲染，避免无显示环境报错
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from auto_pm.models import ProjectInfo  # noqa: E402
from auto_pm.ui.navigation import NavigationTree, NavNode  # noqa: E402


def _make_project(
    project_id: str = "SW-2026-001",
    name: str = "测试项目",
    stack: str = "python",
    phase: str = "developing",
) -> ProjectInfo:
    """构造测试用 ProjectInfo"""
    return ProjectInfo(
        project_id=project_id,
        name=name,
        path=f"/tmp/{project_id}",
        stack=stack,
        version="V1.0.0",
        description="导航树测试项目",
        source="copier",
        phase=phase,
    )


# ── NavNode 数据模型测试 ─────────────────────────────────


class TestNavNode:
    """NavNode dataclass 测试"""

    def test_default_values(self) -> None:
        """NavNode 默认值应为 None/0/空列表"""
        node = NavNode(node_type="stack", label="PLC 总库")
        assert node.node_type == "stack"
        assert node.label == "PLC 总库"
        assert node.filter_stack is None
        assert node.filter_phase is None
        assert node.page_id is None
        assert node.badge_count == 0
        assert node.children == []

    def test_full_construction(self) -> None:
        """NavNode 应支持完整字段构造"""
        child = NavNode(node_type="phase", label="在研项目")
        node = NavNode(
            node_type="stack",
            label="PLC 总库",
            filter_stack="plc",
            filter_phase=None,
            page_id=None,
            badge_count=5,
            children=[child],
        )
        assert node.filter_stack == "plc"
        assert node.badge_count == 5
        assert len(node.children) == 1
        assert node.children[0] is child

    def test_children_independent(self) -> None:
        """每个 NavNode 的 children 应独立（default_factory）"""
        a = NavNode(node_type="root", label="a")
        b = NavNode(node_type="root", label="b")
        a.children.append(NavNode(node_type="function", label="x"))
        assert len(b.children) == 0


# ── 树形结构构建测试 ─────────────────────────────────────


class TestNavigationTreeStructure:
    """NavigationTree 结构构建测试"""

    def test_instantiation(self, qapp: QApplication) -> None:
        """NavigationTree 应能正常实例化"""
        tree = NavigationTree()
        assert tree is not None
        assert tree.objectName() == "navTree"
        tree.deleteLater()
        qapp.processEvents()

    def test_top_level_item_count(self, qapp: QApplication) -> None:
        """顶层节点数：2 总库 + 1 分隔线 + 6 功能 = 9"""
        tree = NavigationTree()
        assert tree.topLevelItemCount() == 9
        tree.deleteLater()
        qapp.processEvents()

    def test_stack_nodes_have_phase_children(self, qapp: QApplication) -> None:
        """每个总库节点应有 4 个阶段子节点"""
        tree = NavigationTree()
        for stack in ("plc", "python"):
            item = tree._stack_nodes[stack]
            assert item.childCount() == 4
        tree.deleteLater()
        qapp.processEvents()

    def test_stack_node_nav_data(self, qapp: QApplication) -> None:
        """总库节点的 NavNode 应正确设置 filter_stack"""
        tree = NavigationTree()
        for stack in ("plc", "python"):
            item = tree._stack_nodes[stack]
            node = item.data(0, Qt.UserRole)
            assert node is not None
            assert node.node_type == "stack"
            assert node.filter_stack == stack
            assert node.filter_phase is None
            assert node.page_id is None
        tree.deleteLater()
        qapp.processEvents()

    def test_phase_node_nav_data(self, qapp: QApplication) -> None:
        """阶段子节点的 NavNode 应正确设置 filter_stack 和 filter_phase"""
        tree = NavigationTree()
        expected_phases = ["developing", "commissioning", "production", "archived"]
        for stack in ("plc", "python"):
            for phase in expected_phases:
                item = tree._phase_nodes[(stack, phase)]
                node = item.data(0, Qt.UserRole)
                assert node is not None
                assert node.node_type == "phase"
                assert node.filter_stack == stack
                assert node.filter_phase == phase
        tree.deleteLater()
        qapp.processEvents()

    def test_function_node_nav_data(self, qapp: QApplication) -> None:
        """功能节点的 NavNode 应正确设置 page_id"""
        tree = NavigationTree()
        expected_pages = [
            "all_projects",
            "change_center",
            "spec_center",
            "template",
            "report",
            "settings",
        ]
        assert set(tree._function_nodes.keys()) == set(expected_pages)
        for page_id in expected_pages:
            item = tree._function_nodes[page_id]
            node = item.data(0, Qt.UserRole)
            assert node is not None
            assert node.node_type == "function"
            assert node.page_id == page_id
            assert node.filter_stack is None
            assert node.filter_phase is None
        tree.deleteLater()
        qapp.processEvents()

    def test_separator_is_non_interactive(self, qapp: QApplication) -> None:
        """分隔线节点应无 UserRole 数据且 flags 为 NoItemFlags"""
        tree = NavigationTree()
        # 分隔线是第 3 个顶层节点（index 2）
        sep_item = tree.topLevelItem(2)
        assert sep_item.data(0, Qt.UserRole) is None
        assert sep_item.flags() == Qt.NoItemFlags
        tree.deleteLater()
        qapp.processEvents()

    def test_stack_items_expanded_by_default(self, qapp: QApplication) -> None:
        """总库节点默认应展开"""
        tree = NavigationTree()
        for stack in ("plc", "python"):
            item = tree._stack_nodes[stack]
            index = tree.indexFromItem(item)
            assert tree.isExpanded(index) is True
        tree.deleteLater()
        qapp.processEvents()

    def test_initial_count_is_zero(self, qapp: QApplication) -> None:
        """初始构建后所有节点计数应为 0"""
        tree = NavigationTree()
        for stack in ("plc", "python"):
            assert "(0)" in tree._stack_nodes[stack].text(0)
        for item in tree._phase_nodes.values():
            assert "(0)" in item.text(0)
        tree.deleteLater()
        qapp.processEvents()


# ── 信号发射测试 ─────────────────────────────────────────


class TestNavigationTreeSignals:
    """NavigationTree 点击信号测试"""

    def test_click_stack_node_emits_filter(
        self, qapp: QApplication
    ) -> None:
        """点击总库节点 → project_filter_requested(stack, '')"""
        tree = NavigationTree()
        received: list[tuple[str, str]] = []
        tree.project_filter_requested.connect(lambda s, p: received.append((s, p)))

        tree._on_item_clicked(tree._stack_nodes["plc"], 0)
        assert received == [("plc", "")]

        tree._on_item_clicked(tree._stack_nodes["python"], 0)
        assert received == [("plc", ""), ("python", "")]

        tree.deleteLater()
        qapp.processEvents()

    def test_click_phase_node_emits_filter(
        self, qapp: QApplication
    ) -> None:
        """点击阶段子节点 → project_filter_requested(stack, phase)"""
        tree = NavigationTree()
        received: list[tuple[str, str]] = []
        tree.project_filter_requested.connect(lambda s, p: received.append((s, p)))

        tree._on_item_clicked(tree._phase_nodes[("plc", "developing")], 0)
        assert received == [("plc", "developing")]

        tree._on_item_clicked(tree._phase_nodes[("python", "production")], 0)
        assert received == [("plc", "developing"), ("python", "production")]

        tree.deleteLater()
        qapp.processEvents()

    def test_click_function_node_emits_page(
        self, qapp: QApplication
    ) -> None:
        """点击功能节点 → page_switch_requested(page_id)"""
        tree = NavigationTree()
        received: list[str] = []
        tree.page_switch_requested.connect(lambda p: received.append(p))

        tree._on_item_clicked(tree._function_nodes["spec_center"], 0)
        assert received == ["spec_center"]

        tree.deleteLater()
        qapp.processEvents()

    def test_all_function_nodes_emit_correct_page(
        self, qapp: QApplication
    ) -> None:
        """所有功能节点点击都应发射正确的 page_id"""
        tree = NavigationTree()
        received: list[str] = []
        tree.page_switch_requested.connect(lambda p: received.append(p))

        for page_id, item in tree._function_nodes.items():
            received.clear()
            tree._on_item_clicked(item, 0)
            assert received == [page_id]

        tree.deleteLater()
        qapp.processEvents()

    def test_all_phase_nodes_emit_correct_filter(
        self, qapp: QApplication
    ) -> None:
        """所有阶段子节点点击都应发射正确的 (stack, phase)"""
        tree = NavigationTree()
        received: list[tuple[str, str]] = []
        tree.project_filter_requested.connect(lambda s, p: received.append((s, p)))

        for (stack, phase), item in tree._phase_nodes.items():
            received.clear()
            tree._on_item_clicked(item, 0)
            assert received == [(stack, phase)]

        tree.deleteLater()
        qapp.processEvents()

    def test_click_separator_no_signal(self, qapp: QApplication) -> None:
        """点击分隔线不应发射任何信号"""
        tree = NavigationTree()
        filter_received: list[tuple[str, str]] = []
        page_received: list[str] = []
        tree.project_filter_requested.connect(lambda s, p: filter_received.append((s, p)))
        tree.page_switch_requested.connect(lambda p: page_received.append(p))

        sep_item = tree.topLevelItem(2)
        tree._on_item_clicked(sep_item, 0)
        assert filter_received == []
        assert page_received == []

        tree.deleteLater()
        qapp.processEvents()

    def test_item_clicked_signal_triggers_handler(
        self, qapp: QApplication
    ) -> None:
        """itemClicked 信号应触发 _on_item_clicked 处理器（集成测试）"""
        tree = NavigationTree()
        received: list[tuple[str, str]] = []
        tree.project_filter_requested.connect(lambda s, p: received.append((s, p)))

        # 通过 emit 模拟点击
        tree.itemClicked.emit(tree._stack_nodes["plc"], 0)
        assert received == [("plc", "")]

        tree.deleteLater()
        qapp.processEvents()


# ── 计数徽标更新测试 ─────────────────────────────────────


class TestNavigationTreeCounts:
    """NavigationTree update_counts() 测试"""

    def test_update_counts_stack(self, qapp: QApplication) -> None:
        """update_counts 应正确更新总库节点计数"""
        tree = NavigationTree()
        projects = [
            _make_project("SW-2026-001", "A", "plc", "developing"),
            _make_project("SW-2026-002", "B", "plc", "production"),
            _make_project("SW-2026-003", "C", "python", "developing"),
        ]
        tree.update_counts(projects)

        assert tree._stack_nodes["plc"].text(0) == "📂 PLC 总库 (2)"
        assert tree._stack_nodes["python"].text(0) == "📂 Python 总库 (1)"

        tree.deleteLater()
        qapp.processEvents()

    def test_update_counts_phase(self, qapp: QApplication) -> None:
        """update_counts 应正确更新阶段子节点计数"""
        tree = NavigationTree()
        projects = [
            _make_project("SW-2026-001", "A", "plc", "developing"),
            _make_project("SW-2026-002", "B", "plc", "developing"),
            _make_project("SW-2026-003", "C", "plc", "production"),
            _make_project("SW-2026-004", "D", "python", "archived"),
        ]
        tree.update_counts(projects)

        assert tree._phase_nodes[("plc", "developing")].text(0) == "🟦 在研项目 (2)"
        assert tree._phase_nodes[("plc", "commissioning")].text(0) == "🟨 调试中 (0)"
        assert tree._phase_nodes[("plc", "production")].text(0) == "🟩 生产中 (1)"
        assert tree._phase_nodes[("plc", "archived")].text(0) == "⬜ 已归档 (0)"
        assert tree._phase_nodes[("python", "archived")].text(0) == "⬜ 已归档 (1)"
        assert tree._phase_nodes[("python", "developing")].text(0) == "🟦 在研项目 (0)"

        tree.deleteLater()
        qapp.processEvents()

    def test_update_counts_empty_list(self, qapp: QApplication) -> None:
        """空项目列表应将所有计数归零"""
        tree = NavigationTree()
        # 先设置非零计数
        tree.update_counts([_make_project("SW-2026-001", "A", "plc", "developing")])
        # 再清空
        tree.update_counts([])

        for stack in ("plc", "python"):
            assert "(0)" in tree._stack_nodes[stack].text(0)
        for item in tree._phase_nodes.values():
            assert "(0)" in item.text(0)

        tree.deleteLater()
        qapp.processEvents()

    def test_update_counts_unknown_stack_ignored(
        self, qapp: QApplication
    ) -> None:
        """unknown 技术栈的项目不应计入任何总库"""
        tree = NavigationTree()
        projects = [
            _make_project("SW-2026-001", "A", "unknown", "developing"),
        ]
        tree.update_counts(projects)

        assert tree._stack_nodes["plc"].text(0) == "📂 PLC 总库 (0)"
        assert tree._stack_nodes["python"].text(0) == "📂 Python 总库 (0)"

        tree.deleteLater()
        qapp.processEvents()

    def test_update_counts_empty_phase_counted_in_stack_only(
        self, qapp: QApplication
    ) -> None:
        """phase 为空的项目应计入总库但不计入任何阶段"""
        tree = NavigationTree()
        projects = [
            _make_project("SW-2026-001", "A", "plc", ""),
        ]
        tree.update_counts(projects)

        assert tree._stack_nodes["plc"].text(0) == "📂 PLC 总库 (1)"
        for phase in ("developing", "commissioning", "production", "archived"):
            assert "(0)" in tree._phase_nodes[("plc", phase)].text(0)

        tree.deleteLater()
        qapp.processEvents()

    def test_update_counts_all_phases(self, qapp: QApplication) -> None:
        """所有阶段都应有正确的计数（全覆盖测试）"""
        tree = NavigationTree()
        projects = [
            _make_project("SW-2026-001", "A", "plc", "developing"),
            _make_project("SW-2026-002", "B", "plc", "commissioning"),
            _make_project("SW-2026-003", "C", "plc", "production"),
            _make_project("SW-2026-004", "D", "plc", "archived"),
            _make_project("SW-2026-005", "E", "python", "developing"),
            _make_project("SW-2026-006", "F", "python", "commissioning"),
            _make_project("SW-2026-007", "G", "python", "production"),
            _make_project("SW-2026-008", "H", "python", "archived"),
        ]
        tree.update_counts(projects)

        assert tree._stack_nodes["plc"].text(0) == "📂 PLC 总库 (4)"
        assert tree._stack_nodes["python"].text(0) == "📂 Python 总库 (4)"
        for stack in ("plc", "python"):
            for phase in ("developing", "commissioning", "production", "archived"):
                assert "(1)" in tree._phase_nodes[(stack, phase)].text(0)

        tree.deleteLater()
        qapp.processEvents()

    def test_update_counts_incremental(self, qapp: QApplication) -> None:
        """多次调用 update_counts 应以最新数据为准（非累加）"""
        tree = NavigationTree()
        tree.update_counts([_make_project("SW-2026-001", "A", "plc", "developing")])
        assert tree._stack_nodes["plc"].text(0) == "📂 PLC 总库 (1)"

        tree.update_counts([
            _make_project("SW-2026-001", "A", "plc", "developing"),
            _make_project("SW-2026-002", "B", "plc", "developing"),
            _make_project("SW-2026-003", "C", "plc", "production"),
        ])
        assert tree._stack_nodes["plc"].text(0) == "📂 PLC 总库 (3)"
        assert tree._phase_nodes[("plc", "developing")].text(0) == "🟦 在研项目 (2)"
        assert tree._phase_nodes[("plc", "production")].text(0) == "🟩 生产中 (1)"

        tree.deleteLater()
        qapp.processEvents()
