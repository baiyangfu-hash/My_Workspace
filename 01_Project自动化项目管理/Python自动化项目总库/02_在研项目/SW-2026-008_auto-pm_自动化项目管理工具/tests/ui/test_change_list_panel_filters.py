"""ChangeListPanel 筛选测试（M3-4 T79）

测试内容：
- 4 维度筛选：状态 Tab / 领域 / 紧急程度 / 项目
- 组合筛选（多维度同时）
- 项目下拉选项动态更新
- 下拉切换触发筛选刷新
- set_xxx_filter 方法与下拉联动
- 清空筛选恢复全部

使用真实 ChangeService + 临时工作空间（不 mock）。
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

# 必须在导入 PySide6 前设置离屏渲染，避免无显示环境报错
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from auto_pm.change.change_service import ChangeService  # noqa: E402
from auto_pm.ui.change_center.change_list_panel import ChangeListPanel  # noqa: E402

# ── fixtures ─────────────────────────────────────────────


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """提供全局 QApplication 实例（session 级复用）"""
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def filter_workspace(tmp_path: Path) -> Path:
    """临时工作空间，含 2 个项目

    项目目录命名遵循 {project_id}_{name} 约定：
    - TEST-2026-001 项目A
    - TEST-2026-002 项目B
    """
    for pid, name in [("TEST-2026-001", "项目A"), ("TEST-2026-002", "项目B")]:
        proj = tmp_path / f"{pid}_{name}"
        proj.mkdir()
        (proj / ".copier-answers.yml").write_text(
            f"project_id: {pid}\n"
            f"project_name: {name}\n"
            "version: V1.0.0\n"
            "_src_path: templates/python-tool\n"
            "business_line: SW\n",
            encoding="utf-8",
        )
    return tmp_path


@pytest.fixture
def panel_with_changes(
    qapp: QApplication, filter_workspace: Path
) -> ChangeListPanel:
    """创建含 4 个变更单的 ChangeListPanel

    变更单分布：
    - TEST-2026-001 / PLC / DEF / normal
    - TEST-2026-001 / DOCU / REQ / urgent
    - TEST-2026-002 / PLC / DEF / critical
    - TEST-2026-002 / PLC / DEF / normal
    """
    cs = ChangeService(str(filter_workspace))
    # 创建 4 个变更单
    cs.create_change_request(
        project_id="TEST-2026-001", domain="PLC", business_nature="DEF",
        impact_scope=["LOCAL"], applicant="fubai", background="bg1", necessity="n1",
        urgency="normal",
    )
    cs.create_change_request(
        project_id="TEST-2026-001", domain="DOCU", business_nature="REQ",
        impact_scope=["LOCAL"], applicant="fubai", background="bg2", necessity="n2",
        urgency="urgent",
    )
    cs.create_change_request(
        project_id="TEST-2026-002", domain="PLC", business_nature="DEF",
        impact_scope=["LOCAL"], applicant="fubai", background="bg3", necessity="n3",
        urgency="critical",
    )
    cs.create_change_request(
        project_id="TEST-2026-002", domain="PLC", business_nature="DEF",
        impact_scope=["LOCAL"], applicant="fubai", background="bg4", necessity="n4",
        urgency="normal",
    )

    panel = ChangeListPanel(cs)
    panel.refresh()
    qapp.processEvents()
    return panel


# ── 测试用例 ─────────────────────────────────────────────


class TestChangeListPanelFilters:
    """ChangeListPanel 4 维度筛选测试"""

    def test_initial_load_all(self, panel_with_changes: ChangeListPanel) -> None:
        """初始加载全部 4 条变更单"""
        assert panel_with_changes._list_widget.count() == 4

    def test_project_combo_options(
        self, panel_with_changes: ChangeListPanel
    ) -> None:
        """项目下拉包含全部 + 2 个项目"""
        combo = panel_with_changes._project_combo
        assert combo.count() == 3  # 全部 + 2 项目
        assert combo.itemData(0) is None  # 全部
        assert combo.itemData(1) is not None
        assert combo.itemData(2) is not None

    def test_domain_combo_options(
        self, panel_with_changes: ChangeListPanel
    ) -> None:
        """领域下拉包含全部 + DOMAINS 所有领域"""
        from auto_pm.change.models import DOMAINS

        combo = panel_with_changes._domain_combo
        assert combo.count() == 1 + len(DOMAINS)
        assert combo.itemData(0) is None  # 全部

    def test_urgency_combo_options(
        self, panel_with_changes: ChangeListPanel
    ) -> None:
        """紧急程度下拉包含全部 + URGENCY_LEVELS 所有等级"""
        from auto_pm.change.models import URGENCY_LEVELS

        combo = panel_with_changes._urgency_combo
        assert combo.count() == 1 + len(URGENCY_LEVELS)
        assert combo.itemData(0) is None  # 全部


class TestDomainFilter:
    """领域筛选测试"""

    def test_filter_plc(
        self, qapp: QApplication, panel_with_changes: ChangeListPanel
    ) -> None:
        """领域=PLC 筛选 3 条"""
        panel_with_changes.set_domain_filter("PLC")
        qapp.processEvents()
        assert panel_with_changes._list_widget.count() == 3

    def test_filter_docu(
        self, qapp: QApplication, panel_with_changes: ChangeListPanel
    ) -> None:
        """领域=DOCU 筛选 1 条"""
        panel_with_changes.set_domain_filter("DOCU")
        qapp.processEvents()
        assert panel_with_changes._list_widget.count() == 1

    def test_clear_domain(
        self, qapp: QApplication, panel_with_changes: ChangeListPanel
    ) -> None:
        """清空领域筛选恢复 4 条"""
        panel_with_changes.set_domain_filter("PLC")
        qapp.processEvents()
        assert panel_with_changes._list_widget.count() == 3

        panel_with_changes.set_domain_filter(None)
        qapp.processEvents()
        assert panel_with_changes._list_widget.count() == 4

    def test_domain_combo_signal(
        self, qapp: QApplication, panel_with_changes: ChangeListPanel
    ) -> None:
        """领域下拉切换触发筛选"""
        # 找到 PLC 的索引
        plc_idx = panel_with_changes._domain_combo.findData("PLC")
        assert plc_idx > 0
        panel_with_changes._domain_combo.setCurrentIndex(plc_idx)
        qapp.processEvents()
        assert panel_with_changes._list_widget.count() == 3


class TestUrgencyFilter:
    """紧急程度筛选测试"""

    def test_filter_critical(
        self, qapp: QApplication, panel_with_changes: ChangeListPanel
    ) -> None:
        """紧急程度=critical 筛选 1 条"""
        panel_with_changes.set_urgency_filter("critical")
        qapp.processEvents()
        assert panel_with_changes._list_widget.count() == 1

    def test_filter_urgent(
        self, qapp: QApplication, panel_with_changes: ChangeListPanel
    ) -> None:
        """紧急程度=urgent 筛选 1 条"""
        panel_with_changes.set_urgency_filter("urgent")
        qapp.processEvents()
        assert panel_with_changes._list_widget.count() == 1

    def test_filter_normal(
        self, qapp: QApplication, panel_with_changes: ChangeListPanel
    ) -> None:
        """紧急程度=normal 筛选 2 条"""
        panel_with_changes.set_urgency_filter("normal")
        qapp.processEvents()
        assert panel_with_changes._list_widget.count() == 2

    def test_clear_urgency(
        self, qapp: QApplication, panel_with_changes: ChangeListPanel
    ) -> None:
        """清空紧急程度筛选恢复 4 条"""
        panel_with_changes.set_urgency_filter("critical")
        qapp.processEvents()
        panel_with_changes.set_urgency_filter(None)
        qapp.processEvents()
        assert panel_with_changes._list_widget.count() == 4


class TestProjectFilter:
    """项目筛选测试"""

    def test_filter_project_001(
        self, qapp: QApplication, panel_with_changes: ChangeListPanel
    ) -> None:
        """项目=TEST-2026-001 筛选 2 条"""
        panel_with_changes.set_project_filter("TEST-2026-001")
        qapp.processEvents()
        assert panel_with_changes._list_widget.count() == 2

    def test_filter_project_002(
        self, qapp: QApplication, panel_with_changes: ChangeListPanel
    ) -> None:
        """项目=TEST-2026-002 筛选 2 条"""
        panel_with_changes.set_project_filter("TEST-2026-002")
        qapp.processEvents()
        assert panel_with_changes._list_widget.count() == 2

    def test_clear_project(
        self, qapp: QApplication, panel_with_changes: ChangeListPanel
    ) -> None:
        """清空项目筛选恢复 4 条"""
        panel_with_changes.set_project_filter("TEST-2026-001")
        qapp.processEvents()
        panel_with_changes.set_project_filter(None)
        qapp.processEvents()
        assert panel_with_changes._list_widget.count() == 4

    def test_project_combo_signal(
        self, qapp: QApplication, panel_with_changes: ChangeListPanel
    ) -> None:
        """项目下拉切换触发筛选"""
        idx = panel_with_changes._project_combo.findData("TEST-2026-001")
        assert idx > 0
        panel_with_changes._project_combo.setCurrentIndex(idx)
        qapp.processEvents()
        assert panel_with_changes._list_widget.count() == 2


class TestCombinedFilter:
    """组合筛选测试"""

    def test_project_and_domain(
        self, qapp: QApplication, panel_with_changes: ChangeListPanel
    ) -> None:
        """项目=001 + 领域=PLC 筛选 1 条"""
        panel_with_changes.set_project_filter("TEST-2026-001")
        qapp.processEvents()
        panel_with_changes.set_domain_filter("PLC")
        qapp.processEvents()
        assert panel_with_changes._list_widget.count() == 1

    def test_project_and_urgency(
        self, qapp: QApplication, panel_with_changes: ChangeListPanel
    ) -> None:
        """项目=002 + 紧急程度=normal 筛选 1 条"""
        panel_with_changes.set_project_filter("TEST-2026-002")
        qapp.processEvents()
        panel_with_changes.set_urgency_filter("normal")
        qapp.processEvents()
        assert panel_with_changes._list_widget.count() == 1

    def test_domain_and_urgency(
        self, qapp: QApplication, panel_with_changes: ChangeListPanel
    ) -> None:
        """领域=PLC + 紧急程度=critical 筛选 1 条"""
        panel_with_changes.set_domain_filter("PLC")
        qapp.processEvents()
        panel_with_changes.set_urgency_filter("critical")
        qapp.processEvents()
        assert panel_with_changes._list_widget.count() == 1

    def test_all_three_filters(
        self, qapp: QApplication, panel_with_changes: ChangeListPanel
    ) -> None:
        """三维度组合：项目=002 + 领域=PLC + 紧急程度=normal 筛选 1 条"""
        panel_with_changes.set_project_filter("TEST-2026-002")
        qapp.processEvents()
        panel_with_changes.set_domain_filter("PLC")
        qapp.processEvents()
        panel_with_changes.set_urgency_filter("normal")
        qapp.processEvents()
        assert panel_with_changes._list_widget.count() == 1

    def test_clear_all_filters(
        self, qapp: QApplication, panel_with_changes: ChangeListPanel
    ) -> None:
        """清空全部筛选恢复 4 条"""
        panel_with_changes.set_project_filter("TEST-2026-001")
        panel_with_changes.set_domain_filter("PLC")
        panel_with_changes.set_urgency_filter("normal")
        qapp.processEvents()

        panel_with_changes.set_project_filter(None)
        panel_with_changes.set_domain_filter(None)
        panel_with_changes.set_urgency_filter(None)
        qapp.processEvents()
        assert panel_with_changes._list_widget.count() == 4


class TestStatusTabWithFilters:
    """状态 Tab 与筛选下拉共存测试"""

    def test_status_tab_and_domain(
        self, qapp: QApplication, panel_with_changes: ChangeListPanel
    ) -> None:
        """状态 Tab=草稿 + 领域=PLC 筛选 3 条（全部 draft）"""
        panel_with_changes.set_status_filter("draft")
        qapp.processEvents()
        panel_with_changes.set_domain_filter("PLC")
        qapp.processEvents()
        assert panel_with_changes._list_widget.count() == 3
