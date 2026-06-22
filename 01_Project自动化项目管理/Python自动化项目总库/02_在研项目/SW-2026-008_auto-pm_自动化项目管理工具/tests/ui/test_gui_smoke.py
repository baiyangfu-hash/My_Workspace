"""PySide6 GUI 冒烟测试

测试 GUI 组件实例化与基本交互（不调用 .show()，避免实际显示窗口）：
- MainWindow / ProjectListView / ProjectWorkspaceView / OverviewTab
- NewProjectDialog / EditProjectDialog / DeleteProjectDialog / ImportProjectDialog
- ProjectCard / StatsBar / FilterBar
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

# 必须在导入 PySide6 前设置离屏渲染，避免无显示环境报错
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from auto_pm.models import ProjectInfo  # noqa: E402
from auto_pm.ui.dialogs import (  # noqa: E402
    DeleteProjectDialog,
    EditProjectDialog,
    ImportProjectDialog,
    NewProjectDialog,
)
from auto_pm.ui.main_window import MainWindow  # noqa: E402
from auto_pm.ui.global_pages.global_view import GlobalView  # noqa: E402
from auto_pm.ui.navigation.nav_tree import NavigationTree  # noqa: E402
from auto_pm.ui.project_list.list_view import ProjectListView  # noqa: E402
from auto_pm.ui.project_list.project_card import ProjectCard  # noqa: E402
from auto_pm.ui.workspace.overview_tab import OverviewTab  # noqa: E402
from auto_pm.ui.workspace.workspace_view import ProjectWorkspaceView  # noqa: E402
from auto_pm.ui.widgets import FilterBar, StatsBar  # noqa: E402


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """提供全局 QApplication 实例（session 级复用）"""
    app = QApplication.instance() or QApplication([])
    yield app


def _make_project(
    project_id: str = "SW-2026-008",
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
        description="冒烟测试项目",
        source="copier",
        phase=phase,
    )


# ── 主窗口与视图测试 ─────────────────────────────────────


class TestMainWindow:
    """MainWindow 实例化测试"""

    def test_main_window_instantiation(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """MainWindow 应能正常实例化（不调用 show）"""
        window = MainWindow(workspace_root=str(tmp_path))
        assert window.windowTitle() == "auto-pm 项目管理工具"
        assert window._project_list_view is not None
        assert window._workspace_view is not None
        assert window._global_view is not None
        window.deleteLater()
        qapp.processEvents()

    def test_main_window_has_toolbar_and_statusbar(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """MainWindow 应包含工具栏和状态栏"""
        window = MainWindow(workspace_root=str(tmp_path))
        assert window.findChild(type(window.statusBar())) is not None
        assert window._search_edit is not None
        assert window._business_combo is not None
        window.deleteLater()
        qapp.processEvents()

    def test_main_window_has_navigation_tree(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """MainWindow 应包含 NavigationTree 实例（替代 navList）"""
        window = MainWindow(workspace_root=str(tmp_path))
        assert isinstance(window._nav_tree, NavigationTree)
        assert window._nav_tree.objectName() == "navTree"
        window.deleteLater()
        qapp.processEvents()

    def test_nav_tree_page_switch_to_global(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """点击 NavigationTree 功能节点应切换到对应独立页面"""
        window = MainWindow(workspace_root=str(tmp_path))
        # spec_center → SpecCenterView (index 7)
        window._nav_tree.page_switch_requested.emit("spec_center")
        qapp.processEvents()
        assert window._stack.currentIndex() == 7
        # report → ReportPage (index 4)
        window._nav_tree.page_switch_requested.emit("report")
        qapp.processEvents()
        assert window._stack.currentIndex() == 4
        # template → TemplatePage (index 5)
        window._nav_tree.page_switch_requested.emit("template")
        qapp.processEvents()
        assert window._stack.currentIndex() == 5
        # settings → SettingsPage (index 6)
        window._nav_tree.page_switch_requested.emit("settings")
        qapp.processEvents()
        assert window._stack.currentIndex() == 6
        window.deleteLater()
        qapp.processEvents()

    def test_nav_tree_page_switch_to_project_list(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """点击 'all_projects' 节点应切换到项目列表页并重置筛选"""
        window = MainWindow(workspace_root=str(tmp_path))
        # 先切到 GlobalView，再切回项目列表
        window._stack.setCurrentIndex(2)
        window._nav_tree.page_switch_requested.emit("all_projects")
        qapp.processEvents()
        assert window._stack.currentIndex() == 0
        assert window._project_list_view._filter_stack == "all"
        window.deleteLater()
        qapp.processEvents()

    def test_nav_tree_filter_updates_project_list(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """点击 NavigationTree 总库/阶段节点应筛选项目列表"""
        window = MainWindow(workspace_root=str(tmp_path))
        window._project_list_view.set_projects(
            [_make_project("SW-2026-001", "项目A", "python", "developing")]
        )
        window._nav_tree.project_filter_requested.emit("python", "developing")
        qapp.processEvents()
        assert window._project_list_view._filter_stack == "python"
        assert window._project_list_view._filter_phase == "developing"
        window.deleteLater()
        qapp.processEvents()

    def test_nav_tree_update_counts(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """update_counts 应更新导航树总库节点计数"""
        window = MainWindow(workspace_root=str(tmp_path))
        projects = [
            _make_project("SW-2026-001", "项目A", "python", "developing"),
            _make_project("SW-2026-002", "项目B", "python", "developing"),
            _make_project("DJ-2026-003", "项目C", "plc", "production"),
        ]
        window._nav_tree.update_counts(projects)
        python_item = window._nav_tree._stack_nodes.get("python")
        assert python_item is not None
        assert "(2)" in python_item.text(0)
        plc_item = window._nav_tree._stack_nodes.get("plc")
        assert plc_item is not None
        assert "(1)" in plc_item.text(0)
        window.deleteLater()
        qapp.processEvents()

    def test_statusbar_has_workspace_label(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """状态栏应包含工作空间路径标签"""
        window = MainWindow(workspace_root=str(tmp_path))
        assert window._status_workspace is not None
        assert "工作空间" in window._status_workspace.text()
        window.deleteLater()
        qapp.processEvents()


class TestProjectListView:
    """ProjectListView 实例化与渲染测试"""

    def test_instantiation(self, qapp: QApplication) -> None:
        """ProjectListView 应能正常实例化"""
        view = ProjectListView()
        assert view is not None
        view.deleteLater()
        qapp.processEvents()

    def test_set_projects_renders_cards(self, qapp: QApplication) -> None:
        """set_projects 后应渲染项目卡片"""
        view = ProjectListView()
        projects = [
            _make_project("SW-2026-001", "项目A", "plc"),
            _make_project("DJ-2026-002", "项目B", "python"),
            _make_project("ZD-2026-003", "项目C", "unknown"),
        ]
        view.set_projects(projects)
        assert len(view._all_projects) == 3
        view.deleteLater()
        qapp.processEvents()

    def test_get_project_by_id(self, qapp: QApplication) -> None:
        """get_project 应返回已设置的项目"""
        view = ProjectListView()
        proj = _make_project("SW-2026-001", "项目A")
        view.set_projects([proj])
        assert view.get_project("SW-2026-001") is proj
        assert view.get_project("NOT-EXIST") is None
        view.deleteLater()
        qapp.processEvents()

    def test_set_search_text(self, qapp: QApplication) -> None:
        """set_search_text 应更新筛选条件"""
        view = ProjectListView()
        view.set_projects([_make_project("SW-2026-001", "Alpha项目")])
        view.set_search_text("alpha")
        assert view._search_text == "alpha"
        view.deleteLater()
        qapp.processEvents()


class TestProjectWorkspaceView:
    """ProjectWorkspaceView 实例化与加载测试"""

    def test_instantiation(self, qapp: QApplication) -> None:
        """ProjectWorkspaceView 应能正常实例化"""
        view = ProjectWorkspaceView()
        assert view is not None
        view.deleteLater()
        qapp.processEvents()

    def test_load_project(self, qapp: QApplication) -> None:
        """load_project 应更新标题和徽标"""
        view = ProjectWorkspaceView()
        proj = _make_project("SW-2026-008", "测试项目", "python", "developing")
        view.load_project(proj)
        assert view._title_label.text() == "测试项目"
        assert view._id_label.text() == "SW-2026-008"
        view.deleteLater()
        qapp.processEvents()


class TestOverviewTab:
    """OverviewTab 实例化与加载测试"""

    def test_instantiation(self, qapp: QApplication) -> None:
        """OverviewTab 应能正常实例化"""
        tab = OverviewTab()
        assert tab is not None
        tab.deleteLater()
        qapp.processEvents()

    def test_load_project(self, qapp: QApplication, tmp_path: Path) -> None:
        """load_project 应能加载真实项目（不抛异常）"""
        tab = OverviewTab()
        # 使用真实路径以便立项表/活动解析
        proj = ProjectInfo(
            project_id="SW-2026-008",
            name="测试项目",
            path=str(tmp_path),
            stack="python",
            version="V1.0.0",
            description="概览测试",
            source="copier",
            phase="developing",
        )
        tab.load_project(proj)
        assert tab._project is not None
        tab.deleteLater()
        qapp.processEvents()


class TestGlobalView:
    """GlobalView 实例化测试"""

    def test_instantiation(self, qapp: QApplication) -> None:
        """GlobalView 应能正常实例化"""
        view = GlobalView()
        assert view is not None
        view.deleteLater()
        qapp.processEvents()


# ── 对话框测试 ───────────────────────────────────────────


class TestNewProjectDialog:
    """NewProjectDialog 实例化测试"""

    def test_instantiation(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """NewProjectDialog 应能正常实例化"""
        dialog = NewProjectDialog(workspace_root=str(tmp_path))
        assert dialog is not None
        assert dialog.windowTitle() == "新建项目"
        dialog.deleteLater()
        qapp.processEvents()


class TestEditProjectDialog:
    """EditProjectDialog 实例化测试"""

    def test_instantiation(
        self, qapp: QApplication, tmp_workspace: Path
    ) -> None:
        """EditProjectDialog 应能加载真实项目并实例化"""
        dialog = EditProjectDialog(
            project_id="DJ-2026-TEST",
            workspace_root=str(tmp_workspace),
        )
        assert dialog is not None
        assert dialog.windowTitle() == "编辑项目"
        # 应加载到项目（tmp_workspace 含 DJ-2026-TEST）
        assert dialog._project is not None
        assert dialog._id_label.text() == "DJ-2026-TEST"
        dialog.deleteLater()
        qapp.processEvents()


class TestDeleteProjectDialog:
    """DeleteProjectDialog 实例化测试"""

    def test_instantiation(
        self, qapp: QApplication, tmp_workspace: Path
    ) -> None:
        """DeleteProjectDialog 应能加载真实项目并实例化"""
        dialog = DeleteProjectDialog(
            project_id="DJ-2026-TEST",
            workspace_root=str(tmp_workspace),
        )
        assert dialog is not None
        assert dialog.windowTitle() == "删除项目"
        # 应加载到项目路径
        assert dialog._project_path is not None
        dialog.deleteLater()
        qapp.processEvents()


class TestImportProjectDialog:
    """ImportProjectDialog 实例化测试"""

    def test_instantiation(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """ImportProjectDialog 应能正常实例化"""
        dialog = ImportProjectDialog(workspace_root=str(tmp_path))
        assert dialog is not None
        assert dialog.windowTitle() == "导入项目"
        dialog.deleteLater()
        qapp.processEvents()


# ── 组件测试 ─────────────────────────────────────────────


class TestProjectCard:
    """ProjectCard 实例化与信号测试"""

    def test_instantiation(self, qapp: QApplication) -> None:
        """ProjectCard 应能正常实例化"""
        proj = _make_project("SW-2026-008", "测试项目", "python")
        card = ProjectCard(proj)
        assert card is not None
        assert card.project.project_id == "SW-2026-008"
        card.deleteLater()
        qapp.processEvents()

    def test_clicked_signal_emission(self, qapp: QApplication) -> None:
        """clicked 信号应能正确发射 project_id"""
        proj = _make_project("SW-2026-008", "测试项目")
        card = ProjectCard(proj)

        received: list[str] = []
        card.clicked.connect(received.append)
        card.clicked.emit("SW-2026-008")

        assert received == ["SW-2026-008"]
        card.deleteLater()
        qapp.processEvents()

    def test_edit_signal_emission(self, qapp: QApplication) -> None:
        """editRequested 信号应能正确发射"""
        proj = _make_project("DJ-2026-001", "编辑测试")
        card = ProjectCard(proj)

        received: list[str] = []
        card.editRequested.connect(received.append)
        card.editRequested.emit("DJ-2026-001")

        assert received == ["DJ-2026-001"]
        card.deleteLater()
        qapp.processEvents()

    def test_delete_signal_emission(self, qapp: QApplication) -> None:
        """deleteRequested 信号应能正确发射"""
        proj = _make_project("DJ-2026-002", "删除测试")
        card = ProjectCard(proj)

        received: list[str] = []
        card.deleteRequested.connect(received.append)
        card.deleteRequested.emit("DJ-2026-002")

        assert received == ["DJ-2026-002"]
        card.deleteLater()
        qapp.processEvents()


class TestStatsBar:
    """StatsBar 实例化测试"""

    def test_instantiation(self, qapp: QApplication) -> None:
        """StatsBar 应能正常实例化"""
        bar = StatsBar()
        assert bar is not None
        bar.deleteLater()
        qapp.processEvents()

    def test_set_stat(self, qapp: QApplication) -> None:
        """set_stat 应更新统计值"""
        bar = StatsBar()
        bar.set_stat("total", 5)
        assert bar._values["total"].text() == "5"
        bar.deleteLater()
        qapp.processEvents()


class TestFilterBar:
    """FilterBar 实例化测试"""

    def test_instantiation(self, qapp: QApplication) -> None:
        """FilterBar 应能正常实例化"""
        bar = FilterBar()
        assert bar is not None
        bar.deleteLater()
        qapp.processEvents()

    def test_set_business_line(self, qapp: QApplication) -> None:
        """set_business_line 应联动业务线下拉框"""
        bar = FilterBar()
        bar.set_business_line("SW")
        assert bar._bl_combo.currentData() == "SW"
        bar.deleteLater()
        qapp.processEvents()

    def test_reset(self, qapp: QApplication) -> None:
        """reset 应重置所有筛选条件"""
        bar = FilterBar()
        bar.set_business_line("DJ")
        bar.reset()
        assert bar._stack_combo.currentData() == "all"
        assert bar._phase_combo.currentData() == "all"
        assert bar._bl_combo.currentData() == "all"
        bar.deleteLater()
        qapp.processEvents()
