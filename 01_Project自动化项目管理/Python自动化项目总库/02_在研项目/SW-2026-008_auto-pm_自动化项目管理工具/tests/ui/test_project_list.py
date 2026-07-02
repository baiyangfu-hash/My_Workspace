"""ProjectListView 重构单元测试

测试内容：
- ViewControls 信号发射（视图模式/排序/分组）
- GroupHeader 折叠/展开
- ProjectListView.set_filter('plc', '') → 只显示 PLC 项目
- ProjectListView.set_filter('plc', 'commissioning') → 只显示 PLC 调试中
- 分组模式切换 → 分组结构正确
- 视图模式切换 → 卡片/列表显示
- 项目卡片点击 → 信号发射
- ProjectTableView 行点击 → project_clicked 信号

遵循项目现有测试模式：自定义 qapp fixture + QT_QPA_PLATFORM=offscreen。
"""

from __future__ import annotations

import os

# 必须在导入 PySide6 前设置离屏渲染，避免无显示环境报错
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QEvent, QPointF, Qt  # noqa: E402
from PySide6.QtGui import QMouseEvent  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from auto_pm.models import DashboardSummaryDTO, ProjectInfo  # noqa: E402
from auto_pm.ui.project_list.group_header import GroupHeader  # noqa: E402
from auto_pm.ui.project_list.list_view import ProjectListView  # noqa: E402
from auto_pm.ui.project_list.project_card import ProjectCard  # noqa: E402
from auto_pm.ui.project_list.table_view import ProjectTableView  # noqa: E402
from auto_pm.ui.project_list.view_controls import ViewControls  # noqa: E402


def _make_project(
    project_id: str,
    name: str,
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
        description=f"测试项目 {project_id}",
        source="copier",
        phase=phase,
    )


def _make_sample_projects() -> list[ProjectInfo]:
    """构造覆盖多技术栈/阶段/业务线的样本项目"""
    return [
        _make_project("DJ-2026-001", "PLC单机A", "plc", "developing"),
        _make_project("DJ-2026-002", "PLC单机B", "plc", "commissioning"),
        _make_project("SW-2026-003", "Python软件A", "python", "developing"),
        _make_project("ZD-2026-004", "PLC整线A", "plc", "production"),
        _make_project("SW-2026-005", "Python软件B", "python", "archived"),
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


def _make_dashboard_summary() -> DashboardSummaryDTO:
    return DashboardSummaryDTO(
        total_projects=5,
        phase_counts={
            "developing": 2,
            "commissioning": 1,
            "production": 1,
            "archived": 1,
        },
        open_change_count=3,
        failed_check_project_count=1,
        failed_check_project_ids=["DJ-2026-001"],
        recent_activities=[
            "[项目] SW-2026-003 于 2026-06-27 09:30 更新",
            "[变更] CHG-PLC-2026-002 (implementing) 申请日期 2026-06-27",
        ],
        risk_hints=[
            "存在 3 条未关闭变更，建议优先清理实施中和待验收项",
            "PLC 检查失败项目: DJ-2026-001",
        ],
    )


# ── ViewControls 测试 ────────────────────────────────────


class TestViewControls:
    """ViewControls 信号发射测试"""

    def test_instantiation(self, qapp: QApplication) -> None:
        """ViewControls 应能正常实例化，默认卡片视图"""
        vc = ViewControls()
        assert vc is not None
        assert vc._card_btn.isChecked() is True
        vc.deleteLater()
        qapp.processEvents()

    def test_view_mode_changed_to_list(self, qapp: QApplication) -> None:
        """点击列表视图按钮 → view_mode_changed('list')"""
        vc = ViewControls()
        received: list[str] = []
        vc.view_mode_changed.connect(received.append)

        vc._list_btn.click()
        assert received == ["list"]
        assert vc._list_btn.isChecked() is True
        vc.deleteLater()
        qapp.processEvents()

    def test_view_mode_changed_to_card(self, qapp: QApplication) -> None:
        """点击卡片视图按钮 → view_mode_changed('card')"""
        vc = ViewControls()
        received: list[str] = []
        vc.view_mode_changed.connect(received.append)

        vc._list_btn.click()
        received.clear()
        vc._card_btn.click()
        assert received == ["card"]
        vc.deleteLater()
        qapp.processEvents()

    def test_sort_changed(self, qapp: QApplication) -> None:
        """切换排序下拉框 → sort_changed 发射对应值"""
        vc = ViewControls()
        received: list[str] = []
        vc.sort_changed.connect(received.append)

        # 切换到「阶段」(index 2)
        vc._sort_combo.setCurrentIndex(2)
        assert received == ["phase"]

        # 切换到「编号↓」(index 1)
        received.clear()
        vc._sort_combo.setCurrentIndex(1)
        assert received == ["id_desc"]
        vc.deleteLater()
        qapp.processEvents()

    def test_group_mode_changed(self, qapp: QApplication) -> None:
        """切换分组下拉框 → group_mode_changed 发射对应值"""
        vc = ViewControls()
        received: list[str] = []
        vc.group_mode_changed.connect(received.append)

        # 切换到「阶段」(index 3)
        vc._group_combo.setCurrentIndex(3)
        assert received == ["phase"]

        # 切换到「不分组」(index 4)
        received.clear()
        vc._group_combo.setCurrentIndex(4)
        assert received == ["none"]
        vc.deleteLater()
        qapp.processEvents()


# ── GroupHeader 测试 ─────────────────────────────────────


class TestGroupHeader:
    """GroupHeader 折叠/展开测试"""

    def test_instantiation(self, qapp: QApplication) -> None:
        """GroupHeader 应正确初始化名称/计数/展开状态"""
        header = GroupHeader("PLC 总库 · 单机 (DJ)", 5, expanded=True)
        assert header.name == "PLC 总库 · 单机 (DJ)"
        assert header.count == 5
        assert header.is_expanded is True
        header.deleteLater()
        qapp.processEvents()

    def test_set_expanded_false_emits_toggled(self, qapp: QApplication) -> None:
        """set_expanded(False) → toggled(False)"""
        header = GroupHeader("组A", 3, expanded=True)
        received: list[bool] = []
        header.toggled.connect(received.append)

        header.set_expanded(False)
        assert received == [False]
        assert header.is_expanded is False
        header.deleteLater()
        qapp.processEvents()

    def test_set_expanded_true_emits_toggled(self, qapp: QApplication) -> None:
        """set_expanded(True) → toggled(True)"""
        header = GroupHeader("组B", 2, expanded=False)
        received: list[bool] = []
        header.toggled.connect(received.append)

        header.set_expanded(True)
        assert received == [True]
        assert header.is_expanded is True
        header.deleteLater()
        qapp.processEvents()

    def test_set_expanded_same_no_signal(self, qapp: QApplication) -> None:
        """状态未变化时不发射 toggled 信号"""
        header = GroupHeader("组C", 1, expanded=True)
        received: list[bool] = []
        header.toggled.connect(received.append)

        header.set_expanded(True)
        assert received == []
        header.deleteLater()
        qapp.processEvents()

    def test_click_toggles_state(self, qapp: QApplication) -> None:
        """鼠标点击应切换展开/折叠状态"""
        header = GroupHeader("组D", 4, expanded=True)
        received: list[bool] = []
        header.toggled.connect(received.append)

        # 模拟鼠标左键点击 → 折叠（使用带 globalPos 的非弃用构造函数）
        event = QMouseEvent(
            QEvent.Type.MouseButtonPress,
            QPointF(5, 5),
            QPointF(5, 5),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        header.mousePressEvent(event)
        assert received == [False]
        assert header.is_expanded is False
        header.deleteLater()
        qapp.processEvents()


# ── ProjectListView 筛选测试 ─────────────────────────────


class TestProjectListViewFilter:
    """ProjectListView.set_filter 筛选测试"""

    def test_set_filter_plc_only(self, qapp: QApplication) -> None:
        """set_filter('plc', '') → 只显示 PLC 项目"""
        view = ProjectListView()
        view.set_projects(_make_sample_projects())
        view.set_filter("plc", "")

        stacks = {p.stack for p in view._filtered_projects}
        assert stacks == {"plc"}
        assert len(view._filtered_projects) == 3
        view.deleteLater()
        qapp.processEvents()


class TestDashboardBanner:
    """首页驾驶舱横幅测试"""

    def test_dashboard_banner_hidden_by_default(self, qapp: QApplication) -> None:
        view = ProjectListView()
        assert view._dashboard_banner.isHidden() is True
        view.deleteLater()
        qapp.processEvents()

    def test_set_dashboard_summary_renders_banner(self, qapp: QApplication) -> None:
        view = ProjectListView()

        view.set_dashboard_summary(_make_dashboard_summary())
        qapp.processEvents()

        assert view._dashboard_banner.isHidden() is False
        assert view._dashboard_banner._total_label.text() == "项目总数: 5"
        assert "开发中 2 / 调试中 1 / 生产中 1 / 已归档 1" in view._dashboard_banner._phase_label.text()
        assert view._dashboard_banner._change_label.text() == "未关闭变更: 3"
        assert view._dashboard_banner._check_label.text() == "检查失败项目: 1"
        assert "DJ-2026-001" in view._dashboard_banner._check_label.toolTip()
        assert "SW-2026-003 于 2026-06-27 09:30 更新" in view._dashboard_banner._recent_label.text()
        assert "存在 3 条未关闭变更" in view._dashboard_banner._risk_label.text()
        view.deleteLater()
        qapp.processEvents()

    def test_set_filter_plc_commissioning(self, qapp: QApplication) -> None:
        """set_filter('plc', 'commissioning') → 只显示 PLC 调试中"""
        view = ProjectListView()
        view.set_projects(_make_sample_projects())
        view.set_filter("plc", "commissioning")

        assert len(view._filtered_projects) == 1
        proj = view._filtered_projects[0]
        assert proj.stack == "plc"
        assert proj.phase == "commissioning"
        assert proj.project_id == "DJ-2026-002"
        view.deleteLater()
        qapp.processEvents()

    # ── V0.4.1 Step 3: not_applicable UI 展示测试 ──────────

    def test_not_applicable_label_displayed(self, qapp: QApplication) -> None:
        """V0.4.1 Step 3: 横幅应展示「检查不适用: N（Python 项目）」"""
        view = ProjectListView()
        summary = DashboardSummaryDTO(
            total_projects=2,
            phase_counts={"developing": 2, "commissioning": 0, "production": 0, "archived": 0},
            open_change_count=0,
            failed_check_project_count=0,
            failed_check_project_ids=[],
            not_applicable_project_count=1,
            not_applicable_project_ids=["SW-2026-003"],
            recent_activities=[],
            risk_hints=["PLC 检查不适用项目: 1 个（Python 项目，已跳过 PLC 检查）"],
        )

        view.set_dashboard_summary(summary)
        qapp.processEvents()

        # 检查不适用标签应可见且文本正确
        label = view._dashboard_banner._not_applicable_label
        assert label.text() == "检查不适用: 1（Python 项目）"
        assert "SW-2026-003" in label.toolTip()
        view.deleteLater()
        qapp.processEvents()

    def test_not_applicable_label_zero(self, qapp: QApplication) -> None:
        """V0.4.1 Step 3: 无不适用项目时显示 0 且无工具提示"""
        view = ProjectListView()
        summary = DashboardSummaryDTO(
            total_projects=1,
            phase_counts={"developing": 1, "commissioning": 0, "production": 0, "archived": 0},
            open_change_count=0,
            failed_check_project_count=0,
            failed_check_project_ids=[],
            not_applicable_project_count=0,
            not_applicable_project_ids=[],
            recent_activities=[],
            risk_hints=["当前未发现高优先级风险"],
        )

        view.set_dashboard_summary(summary)
        qapp.processEvents()

        label = view._dashboard_banner._not_applicable_label
        assert label.text() == "检查不适用: 0（Python 项目）"
        assert label.toolTip() == ""
        view.deleteLater()
        qapp.processEvents()

    def test_set_filter_empty_shows_all(self, qapp: QApplication) -> None:
        """set_filter('', '') → 不筛选，显示全部"""
        view = ProjectListView()
        view.set_projects(_make_sample_projects())
        view.set_filter("", "")

        assert len(view._filtered_projects) == 5
        view.deleteLater()
        qapp.processEvents()

    def test_set_filter_all_shows_all(self, qapp: QApplication) -> None:
        """set_filter('all', '') → 不筛选，显示全部"""
        view = ProjectListView()
        view.set_projects(_make_sample_projects())
        view.set_filter("all", "")

        assert len(view._filtered_projects) == 5
        view.deleteLater()
        qapp.processEvents()

    def test_set_filter_python_developing(self, qapp: QApplication) -> None:
        """set_filter('python', 'developing') → 只显示 Python 开发中"""
        view = ProjectListView()
        view.set_projects(_make_sample_projects())
        view.set_filter("python", "developing")

        assert len(view._filtered_projects) == 1
        assert view._filtered_projects[0].project_id == "SW-2026-003"
        view.deleteLater()
        qapp.processEvents()

    def test_set_filter_no_match_empty_state(self, qapp: QApplication) -> None:
        """set_filter 无匹配项目 → 进入空状态"""
        view = ProjectListView()
        view.set_projects(_make_sample_projects())
        view.set_filter("python", "production")

        assert view._filtered_projects == []
        assert view._state == "empty"
        view.deleteLater()
        qapp.processEvents()


# ── ProjectListView 分组测试 ─────────────────────────────


class TestProjectListViewGrouping:
    """ProjectListView 分组模式测试"""

    def test_group_none_single_group(self, qapp: QApplication) -> None:
        """分组模式 'none' → 单个「全部项目」组"""
        view = ProjectListView()
        view.set_projects(_make_sample_projects())
        view._group_mode = "none"

        groups = view._apply_grouping()
        assert len(groups) == 1
        assert groups[0][1] == "全部项目"
        assert len(groups[0][2]) == 5
        view.deleteLater()
        qapp.processEvents()

    def test_group_by_phase(self, qapp: QApplication) -> None:
        """分组模式 'phase' → 按阶段分组，组名含中文"""
        view = ProjectListView()
        view.set_projects(_make_sample_projects())
        view._group_mode = "phase"

        groups = view._apply_grouping()
        group_names = [g[1] for g in groups]
        # 4 个阶段各对应一组
        assert "开发中" in group_names
        assert "调试中" in group_names
        assert "生产中" in group_names
        assert "已归档" in group_names

        # 开发中应有 2 个项目
        dev_group = next(g for g in groups if g[1] == "开发中")
        assert len(dev_group[2]) == 2
        view.deleteLater()
        qapp.processEvents()

    def test_group_by_stack_bl(self, qapp: QApplication) -> None:
        """分组模式 'stack_bl' → 按 (总库, 业务线) 分组"""
        view = ProjectListView()
        view.set_projects(_make_sample_projects())
        view._group_mode = "stack_bl"

        groups = view._apply_grouping()
        group_names = [g[1] for g in groups]

        # PLC 单机 (DJ) 有 2 个项目
        assert "PLC 总库 · 单机 (DJ)" in group_names
        plc_dj = next(g for g in groups if g[1] == "PLC 总库 · 单机 (DJ)")
        assert len(plc_dj[2]) == 2

        # PLC 整线 (ZD) 有 1 个项目
        assert "PLC 总库 · 整线 (ZD)" in group_names

        # Python 软件 (SW) 有 2 个项目
        assert "Python 总库 · 软件 (SW)" in group_names
        py_sw = next(g for g in groups if g[1] == "Python 总库 · 软件 (SW)")
        assert len(py_sw[2]) == 2
        view.deleteLater()
        qapp.processEvents()

    def test_group_by_stack_phase(self, qapp: QApplication) -> None:
        """分组模式 'stack_phase' → 按 (总库, 阶段) 分组"""
        view = ProjectListView()
        view.set_projects(_make_sample_projects())
        view._group_mode = "stack_phase"

        groups = view._apply_grouping()
        group_names = [g[1] for g in groups]

        assert "PLC 总库 · 开发中" in group_names
        assert "PLC 总库 · 调试中" in group_names
        assert "PLC 总库 · 生产中" in group_names
        assert "Python 总库 · 开发中" in group_names
        assert "Python 总库 · 已归档" in group_names
        view.deleteLater()
        qapp.processEvents()

    def test_group_by_bl(self, qapp: QApplication) -> None:
        """分组模式 'bl' → 按业务线分组"""
        view = ProjectListView()
        view.set_projects(_make_sample_projects())
        view._group_mode = "bl"

        groups = view._apply_grouping()
        group_names = [g[1] for g in groups]

        assert "单机 (DJ)" in group_names
        assert "软件 (SW)" in group_names
        assert "整线 (ZD)" in group_names

        dj_group = next(g for g in groups if g[1] == "单机 (DJ)")
        assert len(dj_group[2]) == 2
        view.deleteLater()
        qapp.processEvents()

    def test_group_mode_switch_via_controls(self, qapp: QApplication) -> None:
        """通过 ViewControls 切换分组模式 → _group_mode 更新"""
        view = ProjectListView()
        view.set_projects(_make_sample_projects())

        # 切换到「不分组」
        view._view_controls.set_group_mode("none")
        assert view._group_mode == "none"

        # 切换到「阶段」
        view._view_controls.set_group_mode("phase")
        assert view._group_mode == "phase"
        view.deleteLater()
        qapp.processEvents()


# ── ProjectListView 视图模式测试 ─────────────────────────


class TestProjectListViewViewMode:
    """ProjectListView 卡片/列表视图切换测试"""

    def test_default_card_view(self, qapp: QApplication) -> None:
        """默认应为卡片视图（content_stack index 0）"""
        view = ProjectListView()
        view.set_projects(_make_sample_projects())
        assert view._view_mode == "card"
        assert view._content_stack.currentIndex() == 0
        view.deleteLater()
        qapp.processEvents()

    def test_switch_to_list_view(self, qapp: QApplication) -> None:
        """切换到列表视图 → content_stack 显示表格（index 1）"""
        view = ProjectListView()
        view.set_projects(_make_sample_projects())

        view._view_controls._list_btn.click()
        qapp.processEvents()

        assert view._view_mode == "list"
        assert view._content_stack.currentIndex() == 1
        # 表格应包含全部 5 个项目
        assert view._table_view.rowCount() == 5
        view.deleteLater()
        qapp.processEvents()

    def test_switch_back_to_card_view(self, qapp: QApplication) -> None:
        """从列表切回卡片视图 → content_stack 显示卡片（index 0）"""
        view = ProjectListView()
        view.set_projects(_make_sample_projects())

        view._view_controls._list_btn.click()
        qapp.processEvents()
        assert view._content_stack.currentIndex() == 1

        view._view_controls._card_btn.click()
        qapp.processEvents()
        assert view._view_mode == "card"
        assert view._content_stack.currentIndex() == 0
        view.deleteLater()
        qapp.processEvents()

    def test_list_view_respects_filter(self, qapp: QApplication) -> None:
        """列表视图应反映当前筛选结果"""
        view = ProjectListView()
        view.set_projects(_make_sample_projects())
        view.set_filter("plc", "")

        view._view_controls._list_btn.click()
        qapp.processEvents()

        assert view._table_view.rowCount() == 3
        view.deleteLater()
        qapp.processEvents()


# ── ProjectListView 卡片点击测试 ─────────────────────────


class TestProjectListViewCardClick:
    """ProjectListView 卡片点击信号测试"""

    def test_card_click_emits_project_selected(self, qapp: QApplication) -> None:
        """点击项目卡片 → projectSelected 信号发射 project_id"""
        view = ProjectListView()
        view.set_projects(_make_sample_projects())

        received: list[str] = []
        view.projectSelected.connect(received.append)

        cards = _find_cards(view)
        assert len(cards) > 0

        # 触发第一张卡片的 clicked 信号
        first_card = cards[0]
        first_card.clicked.emit(first_card.project.project_id)
        assert received == [first_card.project.project_id]
        view.deleteLater()
        qapp.processEvents()

    def test_card_count_matches_filtered(self, qapp: QApplication) -> None:
        """渲染的卡片数应等于筛选后的项目数"""
        view = ProjectListView()
        view.set_projects(_make_sample_projects())

        cards = _find_cards(view)
        assert len(cards) == 5

        # 筛选后卡片数应减少
        view.set_filter("plc", "")
        cards = _find_cards(view)
        assert len(cards) == 3
        view.deleteLater()
        qapp.processEvents()


# ── ProjectTableView 测试 ────────────────────────────────


class TestProjectTableView:
    """ProjectTableView 表格测试"""

    def test_set_projects_loads_rows(self, qapp: QApplication) -> None:
        """set_projects 应加载对应行数"""
        table = ProjectTableView()
        table.set_projects(_make_sample_projects())
        assert table.rowCount() == 5
        table.deleteLater()
        qapp.processEvents()

    def test_cell_click_emits_project_clicked(self, qapp: QApplication) -> None:
        """点击表格行 → project_clicked 信号发射 project_id"""
        table = ProjectTableView()
        table.set_projects(_make_sample_projects())

        received: list[str] = []
        table.project_clicked.connect(received.append)

        # 模拟点击第 0 行
        table.cellClicked.emit(0, 0)
        assert len(received) == 1
        assert received[0] == "DJ-2026-001"
        table.deleteLater()
        qapp.processEvents()

    def test_clear_projects(self, qapp: QApplication) -> None:
        """clear_projects 应清空表格"""
        table = ProjectTableView()
        table.set_projects(_make_sample_projects())
        assert table.rowCount() == 5

        table.clear_projects()
        assert table.rowCount() == 0
        table.deleteLater()
        qapp.processEvents()

    def test_change_count_displayed(self, qapp: QApplication) -> None:
        """变更数应正确显示在表格中"""
        from auto_pm.models.dto import ProjectCardDTO

        table = ProjectTableView()
        dto = ProjectCardDTO(
            project_id="SW-2026-001",
            name="测试",
            stack="python",
            phase="developing",
            version="V1.0.0",
            business_line="SW",
            change_count=7,
            path="/tmp/sw-001",
        )
        from auto_pm.models import ProjectInfo

        proj = ProjectInfo(
            project_id=dto.project_id,
            name=dto.name,
            path=dto.path,
            stack=dto.stack,
            phase=dto.phase,
            version=dto.version,
            business_line=dto.business_line,
        )
        table.set_projects([proj], {dto.project_id: dto.change_count})

        # 变更数列（index 6）应显示 7
        change_item = table.item(0, 6)
        assert change_item is not None
        assert change_item.text() == "7"
        table.deleteLater()
        qapp.processEvents()


# ── ProjectListView 兼容性测试 ───────────────────────────


class TestProjectListViewCompat:
    """ProjectListView 公共接口兼容性测试（不破坏 main_window 引用）"""

    def test_get_project_returns_same_object(self, qapp: QApplication) -> None:
        """get_project 应返回 set_projects 传入的同一对象"""
        view = ProjectListView()
        proj = _make_project("SW-2026-001", "项目A")
        view.set_projects([proj])
        assert view.get_project("SW-2026-001") is proj
        assert view.get_project("NOT-EXIST") is None
        view.deleteLater()
        qapp.processEvents()

    def test_all_projects_attribute(self, qapp: QApplication) -> None:
        """_all_projects 应保存全部项目"""
        view = ProjectListView()
        projects = _make_sample_projects()
        view.set_projects(projects)
        assert len(view._all_projects) == 5
        view.deleteLater()
        qapp.processEvents()

    def test_search_text_attribute(self, qapp: QApplication) -> None:
        """set_search_text 应更新 _search_text"""
        view = ProjectListView()
        view.set_projects([_make_project("SW-2026-001", "Alpha项目")])
        view.set_search_text("alpha")
        assert view._search_text == "alpha"
        view.deleteLater()
        qapp.processEvents()

    def test_set_business_line_filters(self, qapp: QApplication) -> None:
        """set_business_line 应按业务线筛选"""
        view = ProjectListView()
        view.set_projects(_make_sample_projects())
        view.set_business_line("DJ")

        assert len(view._filtered_projects) == 2
        for p in view._filtered_projects:
            assert p.project_id.startswith("DJ-")
        view.deleteLater()
        qapp.processEvents()

    def test_set_business_line_all_clears_filter(self, qapp: QApplication) -> None:
        """set_business_line('all') 应清除业务线筛选"""
        view = ProjectListView()
        view.set_projects(_make_sample_projects())
        view.set_business_line("DJ")
        assert len(view._filtered_projects) == 2

        view.set_business_line("all")
        assert len(view._filtered_projects) == 5
        view.deleteLater()
        qapp.processEvents()

    def test_loading_and_error_states(self, qapp: QApplication) -> None:
        """set_loading / set_error 应切换状态"""
        view = ProjectListView()
        view.set_loading()
        assert view._state == "loading"
        # offscreen 模式下未 show() 的窗口 isVisible() 不可靠，用 isHidden 验证显式标志
        assert not view._progress.isHidden()

        view.set_error("扫描失败")
        assert view._state == "error"
        assert not view._status_label.isHidden()
        assert view._progress.isHidden()
        view.deleteLater()
        qapp.processEvents()


class TestProjectListViewNewProjectButton:
    """V0.5.3 Fix 4: 空状态"新建项目"按钮测试"""

    def test_empty_state_no_filter_shows_new_button(
        self, qapp: QApplication
    ) -> None:
        """V0.5.3 Fix 4: 空状态 + 无筛选 → 新建按钮可见"""
        view = ProjectListView()
        view.set_projects([])  # 空项目列表

        assert view._state == "empty"
        assert not view._empty_new_btn.isHidden()
        view.deleteLater()
        qapp.processEvents()

    def test_empty_state_with_filter_hides_new_button(
        self, qapp: QApplication
    ) -> None:
        """V0.5.3 Fix 4: 空状态 + 有筛选 → 新建按钮隐藏"""
        view = ProjectListView()
        # 先加载项目，再设置筛选使结果为空
        view.set_projects(_make_sample_projects())
        view.set_filter("python", "production")  # 无匹配 → 空状态

        assert view._state == "empty"
        assert view._empty_new_btn.isHidden()
        view.deleteLater()
        qapp.processEvents()

    def test_loading_state_hides_new_button(
        self, qapp: QApplication
    ) -> None:
        """V0.5.3 Fix 4: 加载状态 → 新建按钮隐藏"""
        view = ProjectListView()
        view.set_loading()

        assert view._state == "loading"
        assert view._empty_new_btn.isHidden()
        view.deleteLater()
        qapp.processEvents()

    def test_ready_state_hides_new_button(
        self, qapp: QApplication
    ) -> None:
        """V0.5.3 Fix 4: ready 状态 → 新建按钮隐藏"""
        view = ProjectListView()
        view.set_projects(_make_sample_projects())

        assert view._state == "ready"
        assert view._empty_new_btn.isHidden()
        view.deleteLater()
        qapp.processEvents()

    def test_new_project_button_emits_signal(
        self, qapp: QApplication
    ) -> None:
        """V0.5.3 Fix 4: 点击新建按钮 → 发射 newProjectRequested 信号"""
        view = ProjectListView()
        view.set_projects([])  # 空状态

        received: list[None] = []
        view.newProjectRequested.connect(lambda: received.append(None))

        view._empty_new_btn.click()

        assert len(received) == 1
        view.deleteLater()
        qapp.processEvents()
