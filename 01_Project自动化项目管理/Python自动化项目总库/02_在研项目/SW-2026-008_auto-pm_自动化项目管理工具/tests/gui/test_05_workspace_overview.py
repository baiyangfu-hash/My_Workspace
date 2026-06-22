"""工作区概览 GUI 测试

覆盖进入工作区、头部信息展示、概览 Tab 加载、返回列表等交互流程。
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from tests.gui.helpers.interactions import (
    back_to_list,
    enter_workspace,
    switch_workspace_tab,
)


@pytest.mark.gui
def test_enter_workspace(main_window, app, test_project_id):
    """测试从项目列表进入项目工作区后页面栈切换到工作区"""
    enter_workspace(main_window, test_project_id, app)
    assert main_window._stack.currentIndex() == 1


@pytest.mark.gui
def test_workspace_header(main_window, app, test_project_id):
    """测试工作区头部显示当前项目编号"""
    enter_workspace(main_window, test_project_id, app)
    id_text = main_window._workspace_view._id_label.text()
    assert test_project_id in id_text, f"头部编号预期含 '{test_project_id}'，实际 '{id_text}'"


@pytest.mark.gui
def test_workspace_title(main_window, app, test_project_id):
    """测试工作区头部显示项目名称（非空且非占位文本）"""
    enter_workspace(main_window, test_project_id, app)
    title_text = main_window._workspace_view._title_label.text()
    assert title_text, "工作区标题为空"
    assert title_text != "未选择项目", f"工作区标题仍为占位文本: '{title_text}'"


@pytest.mark.gui
def test_overview_tab_loaded(main_window, app, test_project_id):
    """测试切换到概览 Tab 后项目数据已加载到工作区"""
    enter_workspace(main_window, test_project_id, app)
    switch_workspace_tab(main_window, "overview", app)
    project = main_window._workspace_view._project
    assert project is not None, "工作区未加载项目"
    assert project.project_id == test_project_id


@pytest.mark.gui
def test_back_to_list(main_window, app, test_project_id):
    """测试从工作区返回项目列表后页面栈切换回列表页"""
    enter_workspace(main_window, test_project_id, app)
    assert main_window._stack.currentIndex() == 1
    back_to_list(main_window, app)
    assert main_window._stack.currentIndex() == 0
