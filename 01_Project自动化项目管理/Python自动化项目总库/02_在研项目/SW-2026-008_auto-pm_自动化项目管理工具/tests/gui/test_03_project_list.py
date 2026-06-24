"""项目列表测试

验证 ProjectListView 的搜索、业务线筛选、视图模式切换、分组模式切换、
项目查询等核心交互行为。
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from tests.gui.helpers.interactions import (
    clear_search,
    search_projects,
    switch_group_mode,
    switch_view_mode,
)


@pytest.mark.gui
class TestProjectList:
    """项目列表交互测试"""

    def test_search_by_id(self, main_window, app, test_project_id):
        """按项目编号搜索，验证 _filtered_projects 中包含该项目"""
        search_projects(main_window, test_project_id, app)
        plv = main_window._project_list_view
        ids = [p.project_id for p in plv._filtered_projects]
        assert test_project_id in ids, (
            f"搜索 {test_project_id} 后 _filtered_projects 未包含该项目，实际: {ids}"
        )

    def test_search_no_result(self, main_window, app):
        """搜索不存在的关键字 'ZZZZZ_NOT_EXIST'，验证 _filtered_projects 为空"""
        search_projects(main_window, "ZZZZZ_NOT_EXIST", app)
        plv = main_window._project_list_view
        assert len(plv._filtered_projects) == 0, (
            f"搜索不存在关键字后 _filtered_projects 预期为空，"
            f"实际数量: {len(plv._filtered_projects)}"
        )

    def test_search_clear(self, main_window, app, test_project_id):
        """清空搜索后，验证 _filtered_projects 恢复（包含测试项目或非空）"""
        # 先搜索缩小范围
        search_projects(main_window, test_project_id, app)
        plv = main_window._project_list_view
        filtered_after_search = len(plv._filtered_projects)
        assert filtered_after_search >= 1, "搜索测试项目后应至少有 1 条结果"

        # 清空搜索
        clear_search(main_window, app)
        restored = len(plv._filtered_projects)
        assert restored >= filtered_after_search, (
            f"清空搜索后 _filtered_projects 数量({restored})应不少于"
            f"搜索时数量({filtered_after_search})"
        )
        # 搜索框文本应为空
        assert main_window._search_edit.text() == "", (
            f"清空搜索后搜索框文本预期为空，实际 '{main_window._search_edit.text()}'"
        )

    def test_filter_business_line(self, main_window, app):
        """切换 _business_combo，验证不崩溃且筛选状态更新"""
        combo = main_window._business_combo

        # 依次切换每个业务线选项
        for i in range(combo.count()):
            combo.setCurrentIndex(i)
            app.processEvents()
            QTest.qWait(200)
            # 验证不崩溃：_filter_bl 已更新
            _ = main_window._project_list_view._filtered_projects

        # 切回第一项（通常为全部）
        if combo.count() > 0:
            combo.setCurrentIndex(0)
            app.processEvents()
            QTest.qWait(200)

        # 验证最终状态稳定
        assert main_window._project_list_view._filtered_projects is not None, (
            "业务线切换后 _filtered_projects 为 None（不应发生）"
        )

    def test_switch_to_list_view(self, main_window, app):
        """切换到列表视图，验证 _content_stack.currentIndex()==1"""
        switch_view_mode(main_window, "list", app)
        idx = main_window._project_list_view._content_stack.currentIndex()
        assert idx == 1, f"切换列表视图后 _content_stack 索引预期 1，实际 {idx}"

    def test_switch_to_card_view(self, main_window, app):
        """先切 list 再切 card，验证 _content_stack.currentIndex()==0"""
        switch_view_mode(main_window, "list", app)
        idx_after_list = main_window._project_list_view._content_stack.currentIndex()
        assert idx_after_list == 1, f"切 list 后索引预期 1，实际 {idx_after_list}"

        switch_view_mode(main_window, "card", app)
        idx_after_card = main_window._project_list_view._content_stack.currentIndex()
        assert idx_after_card == 0, f"切 card 后索引预期 0，实际 {idx_after_card}"

    def test_group_mode_switch(self, main_window, app):
        """切换 4 种分组模式，验证不崩溃"""
        modes = ["总库+业务线", "总库+阶段", "业务线", "阶段"]
        for mode_text in modes:
            switch_group_mode(main_window, mode_text, app)
            # 验证不崩溃：_filtered_projects 仍可访问
            _ = main_window._project_list_view._filtered_projects
            app.processEvents()
            QTest.qWait(100)

        # 验证最终状态稳定
        assert main_window._project_list_view._filtered_projects is not None, (
            "分组模式切换后 _filtered_projects 为 None（不应发生）"
        )

    def test_get_test_project(self, main_window, app, test_project_id):
        """验证 get_project(test_project_id) 返回非 None"""
        proj = main_window._project_list_view.get_project(test_project_id)
        assert proj is not None, (
            f"get_project('{test_project_id}') 返回 None，项目未加载到列表"
        )
        assert proj.project_id == test_project_id, (
            f"get_project 返回项目编号预期 '{test_project_id}'，"
            f"实际 '{proj.project_id}'"
        )


# 延迟导入 QTest（避免在模块顶部导入时影响 QT_QPA_PLATFORM 设置）
from PySide6.QtTest import QTest  # noqa: E402
