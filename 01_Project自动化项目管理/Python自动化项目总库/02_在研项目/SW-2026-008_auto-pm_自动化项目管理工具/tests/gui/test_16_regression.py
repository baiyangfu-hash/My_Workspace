"""GUI 回归测试

验证已知 bug 不复发：项目路径非空、同步/刷新不崩溃、导航树空列表计数、
特殊字符搜索安全。
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from tests.gui.helpers.interactions import (
    enter_workspace,
    refresh_list,
    search_projects,
    sync_cache,
)


@pytest.mark.gui
def test_bug1_project_path_not_none(main_window, test_project_id, app):
    """回归：进入工作区后 _workspace_view._project.path 非空"""
    enter_workspace(main_window, test_project_id, app)
    project = main_window._workspace_view._project
    assert project is not None
    assert project.path != ""


@pytest.mark.gui
def test_bug2_sync_no_crash(main_window, app):
    """回归：同步缓存操作不崩溃"""
    sync_cache(main_window, app)
    # 未抛出异常即通过


@pytest.mark.gui
def test_bug3_refresh_no_crash(main_window, app):
    """回归：刷新列表操作不崩溃"""
    refresh_list(main_window, app)
    # 未抛出异常即通过


@pytest.mark.gui
def test_bug4_nav_tree_counts(main_window):
    """回归：导航树 update_counts 传入空列表不崩溃"""
    assert main_window._nav_tree is not None
    main_window._nav_tree.update_counts([])
    # 未抛出异常即通过


@pytest.mark.gui
def test_bug5_search_special_chars(main_window, app):
    """回归：特殊字符搜索安全，不崩溃"""
    search_projects(main_window, "<script>alert(1)</script>", app)
    # 未抛出异常即通过
