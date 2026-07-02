"""迭代1 GUI 交互测试

真实操作 widget（点击、输入、信号验证），不使用 mock。
覆盖迭代1交付的 NavigationTree / ProjectListView / ProjectCard / MainWindow 集成 / 状态栏。

测试内容：
- NavigationTree 点击 → ProjectListView 筛选生效（PLC/Python 总库 + 阶段子节点）
- NavigationTree 功能节点点击 → 页面切换（全部项目/变更中心/系统设置）
- ProjectListView 分组模式切换（总库+业务线/总库+阶段/业务线/阶段）
- ProjectListView 视图模式切换（卡片/列表）
- 顶部工具栏搜索框 → 实时过滤
- 顶部工具栏业务线下拉 → 联动筛选
- 项目卡片点击 → 进入工作区（QStackedWidget 切换）
- 状态栏工作空间路径 / 扫描时间
- NavigationTree 计数徽标

遵循项目现有测试模式：自定义 qapp fixture + QT_QPA_PLATFORM=offscreen。
"""

from __future__ import annotations

import os
from pathlib import Path

# 必须在导入 PySide6 前设置离屏渲染，避免无显示环境报错
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from auto_pm.models import ProjectInfo  # noqa: E402
from auto_pm.ui.main_window import MainWindow  # noqa: E402
from auto_pm.ui.project_list.group_header import GroupHeader  # noqa: E402
from auto_pm.ui.project_list.list_view import ProjectListView  # noqa: E402
from auto_pm.ui.project_list.project_card import ProjectCard  # noqa: E402


def _make_project(
    project_id: str,
    name: str,
    stack: str = "python",
    phase: str = "developing",
    description: str = "",
    business_line: str = "",
) -> ProjectInfo:
    """构造测试用 ProjectInfo"""
    return ProjectInfo(
        project_id=project_id,
        name=name,
        path=f"/tmp/{project_id}",
        stack=stack,
        version="V1.0.0",
        description=description or f"测试项目 {project_id}",
        source="copier",
        phase=phase,
        business_line=business_line,
    )


def _make_sample_projects() -> list[ProjectInfo]:
    """构造覆盖多技术栈/阶段/业务线的样本项目（用于筛选/分组测试）"""
    return [
        _make_project("DJ-2026-001", "PLC单机A", "plc", "developing", business_line="DJ"),
        _make_project("DJ-2026-002", "PLC单机B", "plc", "commissioning", business_line="DJ"),
        _make_project("SW-2026-003", "Python软件A", "python", "developing", business_line="SW"),
        _make_project("ZD-2026-004", "PLC整线A", "plc", "production", business_line="ZD"),
        _make_project("SW-2026-005", "Python软件B", "python", "archived", business_line="SW"),
    ]


def _find_cards(view: ProjectListView) -> list[ProjectCard]:
    """从卡片视图内容容器中收集所有 ProjectCard"""
    cards: list[ProjectCard] = []
    for i in range(view._content_layout.count()):
        item = view._content_layout.itemAt(i)
        w = item.widget() if item is not None else None
        if isinstance(w, GroupHeader) or w is None:
            continue
        grid = w.layout()
        if grid is None:
            continue
        for j in range(grid.count()):
            child_item = grid.itemAt(j)
            cw = child_item.widget() if child_item is not None else None
            if isinstance(cw, ProjectCard):
                cards.append(cw)
    return cards


def _inject_projects(window: MainWindow, projects: list[ProjectInfo]) -> None:
    """向 MainWindow 注入测试项目数据（绕过文件系统扫描）"""
    window._project_list_view.set_projects(projects)
    window._nav_tree.update_counts(projects)
    window._update_statusbar(projects)


# ── NavigationTree 点击 → ProjectListView 筛选 ────────────


class TestNavClickFilter:
    """NavigationTree 点击总库/阶段节点 → ProjectListView 筛选生效"""

    def test_nav_click_plc_stack(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """点击 PLC总库节点 → ProjectListView 只显示 PLC 项目"""
        window = MainWindow(workspace_root=str(tmp_path))
        _inject_projects(window, _make_sample_projects())

        # 模拟点击 PLC 总库节点（通过信号触发，等价于真实点击）
        window._nav_tree._on_item_clicked(window._nav_tree._stack_nodes["plc"], 0)
        qapp.processEvents()

        assert window._project_list_view._filter_stack == "plc"
        stacks = {p.stack for p in window._project_list_view._filtered_projects}
        assert stacks == {"plc"}
        assert len(window._project_list_view._filtered_projects) == 3
        window.deleteLater()
        qapp.processEvents()

    def test_nav_click_plc_commissioning(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """点击 PLC总库>调试中 → 只显示 PLC 调试中项目"""
        window = MainWindow(workspace_root=str(tmp_path))
        _inject_projects(window, _make_sample_projects())

        window._nav_tree._on_item_clicked(
            window._nav_tree._phase_nodes[("plc", "commissioning")], 0
        )
        qapp.processEvents()

        assert window._project_list_view._filter_stack == "plc"
        assert window._project_list_view._filter_phase == "commissioning"
        filtered = window._project_list_view._filtered_projects
        assert len(filtered) == 1
        assert filtered[0].project_id == "DJ-2026-002"
        assert filtered[0].stack == "plc"
        assert filtered[0].phase == "commissioning"
        window.deleteLater()
        qapp.processEvents()

    def test_nav_click_python_stack(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """点击 Python总库节点 → 只显示 Python 项目"""
        window = MainWindow(workspace_root=str(tmp_path))
        _inject_projects(window, _make_sample_projects())

        window._nav_tree._on_item_clicked(window._nav_tree._stack_nodes["python"], 0)
        qapp.processEvents()

        assert window._project_list_view._filter_stack == "python"
        stacks = {p.stack for p in window._project_list_view._filtered_projects}
        assert stacks == {"python"}
        assert len(window._project_list_view._filtered_projects) == 2
        window.deleteLater()
        qapp.processEvents()

    def test_nav_click_all_projects(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """点击"全部项目" → 切换到项目列表页并显示所有项目"""
        window = MainWindow(workspace_root=str(tmp_path))
        _inject_projects(window, _make_sample_projects())

        # 先切到 GlobalView，再点"全部项目"验证能切回列表页
        window._stack.setCurrentIndex(2)
        window._nav_tree._on_item_clicked(
            window._nav_tree._function_nodes["all_projects"], 0
        )
        qapp.processEvents()

        assert window._stack.currentIndex() == 0
        assert window._project_list_view._filter_stack == "all"
        assert len(window._project_list_view._filtered_projects) == 5
        window.deleteLater()
        qapp.processEvents()


# ── NavigationTree 功能节点 → 页面切换 ────────────────────


class TestNavClickPageSwitch:
    """NavigationTree 点击功能节点 → QStackedWidget 页面切换"""

    def test_nav_click_change_center(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """点击"变更中心" → 切换到 ChangeCenterView (index 3)"""
        window = MainWindow(workspace_root=str(tmp_path))
        assert window._stack.currentIndex() == 0

        window._nav_tree._on_item_clicked(
            window._nav_tree._function_nodes["change_center"], 0
        )
        qapp.processEvents()

        assert window._stack.currentIndex() == 3
        assert window._stack.currentWidget() is window._change_center_view
        window.deleteLater()
        qapp.processEvents()

    def test_nav_click_settings(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """点击"系统设置" → 切换到 SettingsPage (index 6)"""
        window = MainWindow(workspace_root=str(tmp_path))
        assert window._stack.currentIndex() == 0

        window._nav_tree._on_item_clicked(
            window._nav_tree._function_nodes["settings"], 0
        )
        qapp.processEvents()

        assert window._stack.currentIndex() == 6
        assert window._stack.currentWidget() is window._settings_page
        window.deleteLater()
        qapp.processEvents()


# ── ProjectListView 分组模式切换 ──────────────────────────


class TestGroupModeSwitch:
    """ProjectListView 分组模式切换 → 分组结构正确"""

    def test_group_mode_switch_stack_bl(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """切换分组为"总库+业务线" → 分组结构正确"""
        window = MainWindow(workspace_root=str(tmp_path))
        _inject_projects(window, _make_sample_projects())

        # 通过 ViewControls 下拉框切换（真实操作）
        window._project_list_view._view_controls.set_group_mode("stack_bl")
        qapp.processEvents()

        assert window._project_list_view._group_mode == "stack_bl"
        groups = window._project_list_view._apply_grouping()
        group_names = [g[1] for g in groups]
        assert "PLC 总库 · 单机 (DJ)" in group_names
        assert "PLC 总库 · 整线 (ZD)" in group_names
        assert "Python 总库 · 软件 (SW)" in group_names
        window.deleteLater()
        qapp.processEvents()

    def test_group_mode_switch_stack_phase(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """切换分组为"总库+阶段" → 分组结构正确"""
        window = MainWindow(workspace_root=str(tmp_path))
        _inject_projects(window, _make_sample_projects())

        window._project_list_view._view_controls.set_group_mode("stack_phase")
        qapp.processEvents()

        assert window._project_list_view._group_mode == "stack_phase"
        groups = window._project_list_view._apply_grouping()
        group_names = [g[1] for g in groups]
        assert "PLC 总库 · 开发中" in group_names
        assert "PLC 总库 · 调试中" in group_names
        assert "PLC 总库 · 生产中" in group_names
        assert "Python 总库 · 开发中" in group_names
        assert "Python 总库 · 已归档" in group_names
        window.deleteLater()
        qapp.processEvents()

    def test_group_mode_switch_bl(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """切换分组为"业务线" → 分组结构正确"""
        window = MainWindow(workspace_root=str(tmp_path))
        _inject_projects(window, _make_sample_projects())

        window._project_list_view._view_controls.set_group_mode("bl")
        qapp.processEvents()

        assert window._project_list_view._group_mode == "bl"
        groups = window._project_list_view._apply_grouping()
        group_names = [g[1] for g in groups]
        assert "单机 (DJ)" in group_names
        assert "软件 (SW)" in group_names
        assert "整线 (ZD)" in group_names
        # DJ 业务线应有 2 个项目
        dj_group = next(g for g in groups if g[1] == "单机 (DJ)")
        assert len(dj_group[2]) == 2
        window.deleteLater()
        qapp.processEvents()

    def test_group_mode_switch_phase(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """切换分组为"阶段" → 分组结构正确"""
        window = MainWindow(workspace_root=str(tmp_path))
        _inject_projects(window, _make_sample_projects())

        window._project_list_view._view_controls.set_group_mode("phase")
        qapp.processEvents()

        assert window._project_list_view._group_mode == "phase"
        groups = window._project_list_view._apply_grouping()
        group_names = [g[1] for g in groups]
        assert "开发中" in group_names
        assert "调试中" in group_names
        assert "生产中" in group_names
        assert "已归档" in group_names
        # 开发中应有 2 个项目
        dev_group = next(g for g in groups if g[1] == "开发中")
        assert len(dev_group[2]) == 2
        window.deleteLater()
        qapp.processEvents()


# ── ProjectListView 视图模式切换 ──────────────────────────


class TestViewModeSwitch:
    """ProjectListView 卡片/列表视图切换"""

    def test_view_mode_switch_card(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """切换到卡片视图 → 卡片网格显示（content_stack index 0）"""
        window = MainWindow(workspace_root=str(tmp_path))
        _inject_projects(window, _make_sample_projects())

        # 先切到列表，再切回卡片，验证切换生效
        window._project_list_view._view_controls._list_btn.click()
        qapp.processEvents()
        assert window._project_list_view._content_stack.currentIndex() == 1

        window._project_list_view._view_controls._card_btn.click()
        qapp.processEvents()

        assert window._project_list_view._view_mode == "card"
        assert window._project_list_view._content_stack.currentIndex() == 0
        # 卡片网格应渲染出卡片
        cards = _find_cards(window._project_list_view)
        assert len(cards) == 5
        window.deleteLater()
        qapp.processEvents()

    def test_view_mode_switch_list(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """切换到列表视图 → 表格显示（content_stack index 1）"""
        window = MainWindow(workspace_root=str(tmp_path))
        _inject_projects(window, _make_sample_projects())

        window._project_list_view._view_controls._list_btn.click()
        qapp.processEvents()

        assert window._project_list_view._view_mode == "list"
        assert window._project_list_view._content_stack.currentIndex() == 1
        # 表格应包含全部 5 个项目
        assert window._project_list_view._table_view.rowCount() == 5
        window.deleteLater()
        qapp.processEvents()


# ── 顶部工具栏筛选 ────────────────────────────────────────


class TestToolbarFilter:
    """顶部工具栏搜索框 / 业务线下拉联动筛选"""

    def test_search_filter(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """搜索框输入项目编号 → 实时过滤"""
        window = MainWindow(workspace_root=str(tmp_path))
        _inject_projects(window, _make_sample_projects())

        # 模拟在搜索框输入 "DJ-2026-001"（textChanged 信号触发）
        window._search_edit.setText("DJ-2026-001")
        qapp.processEvents()

        filtered = window._project_list_view._filtered_projects
        assert len(filtered) == 1
        assert filtered[0].project_id == "DJ-2026-001"
        window.deleteLater()
        qapp.processEvents()

    def test_search_filter_by_name(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """搜索框输入项目名称关键字 → 实时过滤"""
        window = MainWindow(workspace_root=str(tmp_path))
        _inject_projects(window, _make_sample_projects())

        window._search_edit.setText("Python软件")
        qapp.processEvents()

        filtered = window._project_list_view._filtered_projects
        assert len(filtered) == 2
        for p in filtered:
            assert p.stack == "python"
        window.deleteLater()
        qapp.processEvents()

    def test_business_line_filter(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """业务线下拉选择 → 联动筛选"""
        window = MainWindow(workspace_root=str(tmp_path))
        _inject_projects(window, _make_sample_projects())

        # 业务线下拉框选择"单机设备 (DJ)"（index 2）
        # _BUSINESS_LINE_OPTIONS: all(0), SW(1), DJ(2), ZD(3), XT(4), WX(5)
        window._business_combo.setCurrentIndex(2)
        qapp.processEvents()

        filtered = window._project_list_view._filtered_projects
        assert len(filtered) == 2
        for p in filtered:
            assert p.project_id.startswith("DJ-")
        window.deleteLater()
        qapp.processEvents()


# ── 项目卡片点击 → 进入工作区 ─────────────────────────────


class TestProjectCardClick:
    """项目卡片点击 → QStackedWidget 切换到工作区"""

    def test_project_card_click(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """点击项目卡片 → 进入工作区（QStackedWidget 切换到 index 1）"""
        window = MainWindow(workspace_root=str(tmp_path))
        _inject_projects(window, _make_sample_projects())

        # 当前应在项目列表页
        assert window._stack.currentIndex() == 0

        # 找到第一张卡片并触发点击
        cards = _find_cards(window._project_list_view)
        assert len(cards) > 0
        first_card = cards[0]
        target_id = first_card.project.project_id

        # 通过 projectSelected 信号触发主窗口的 _on_project_selected
        window._project_list_view.projectSelected.emit(target_id)
        qapp.processEvents()

        # 应切换到工作区页（index 1）
        assert window._stack.currentIndex() == 1
        assert window._stack.currentWidget() is window._workspace_view
        # 工作区应加载了该项目
        assert window._workspace_view._project is not None
        assert window._workspace_view._project.project_id == target_id
        window.deleteLater()
        qapp.processEvents()


# ── 状态栏 ────────────────────────────────────────────────


class TestStatusBar:
    """状态栏显示工作空间路径 / 扫描时间"""

    def test_statusbar_workspace(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """状态栏显示工作空间路径"""
        window = MainWindow(workspace_root=str(tmp_path))
        _inject_projects(window, _make_sample_projects())

        text = window._status_workspace.text()
        assert "工作空间" in text
        # V0.5.3: _abbreviate_path 会缩略长路径，完整路径存在 toolTip 中
        tip = window._status_workspace.toolTip()
        assert str(tmp_path) == tip or str(tmp_path) in tip
        window.deleteLater()
        qapp.processEvents()

    def test_statusbar_scan_time(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """状态栏显示扫描时间（或"—"）"""
        window = MainWindow(workspace_root=str(tmp_path))
        _inject_projects(window, _make_sample_projects())

        text = window._status_scan.text()
        assert "上次扫描" in text
        # 无 ScanLog 记录时应为 "—"，有记录时应为时间字符串
        assert "—" in text or ":" in text
        window.deleteLater()
        qapp.processEvents()


# ── NavigationTree 计数徽标 ───────────────────────────────


class TestNavTreeCounts:
    """NavigationTree 计数徽标正确性"""

    def test_nav_tree_counts(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """NavigationTree 计数徽标应正确反映项目分布"""
        window = MainWindow(workspace_root=str(tmp_path))
        _inject_projects(window, _make_sample_projects())

        nav = window._nav_tree
        # 总库计数：plc=3, python=2
        assert "(3)" in nav._stack_nodes["plc"].text(0)
        assert "(2)" in nav._stack_nodes["python"].text(0)

        # 阶段计数
        # plc: developing=1, commissioning=1, production=1, archived=0
        assert "(1)" in nav._phase_nodes[("plc", "developing")].text(0)
        assert "(1)" in nav._phase_nodes[("plc", "commissioning")].text(0)
        assert "(1)" in nav._phase_nodes[("plc", "production")].text(0)
        assert "(0)" in nav._phase_nodes[("plc", "archived")].text(0)
        # python: developing=1, archived=1
        assert "(1)" in nav._phase_nodes[("python", "developing")].text(0)
        assert "(1)" in nav._phase_nodes[("python", "archived")].text(0)
        window.deleteLater()
        qapp.processEvents()

    def test_nav_tree_counts_update_on_refresh(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """刷新后 NavigationTree 计数应同步更新"""
        window = MainWindow(workspace_root=str(tmp_path))
        # 初始注入 5 个项目
        _inject_projects(window, _make_sample_projects())
        assert "(3)" in window._nav_tree._stack_nodes["plc"].text(0)

        # 重新注入更少的项目
        new_projects = [
            _make_project("DJ-2026-001", "PLC单机A", "plc", "developing"),
        ]
        _inject_projects(window, new_projects)

        assert "(1)" in window._nav_tree._stack_nodes["plc"].text(0)
        assert "(0)" in window._nav_tree._stack_nodes["python"].text(0)
        window.deleteLater()
        qapp.processEvents()
