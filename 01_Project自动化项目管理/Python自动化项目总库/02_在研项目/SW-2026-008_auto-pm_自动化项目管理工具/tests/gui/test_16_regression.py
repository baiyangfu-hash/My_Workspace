"""GUI 回归测试

验证已知 bug 不复发：项目路径非空、同步/刷新不崩溃、导航树空列表计数、
特殊字符搜索安全。
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

# V0.5.2: 默认可见模式（用户要求）；offscreen 仅通过 QT_QPA_PLATFORM=offscreen 环境变量设置

import pytest

from tests.gui.helpers.interactions import (
    enter_workspace,
    refresh_list,
    search_projects,
    sync_cache,
)

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication

    from auto_pm.ui.main_window import MainWindow


@pytest.mark.gui
def test_bug1_project_path_not_none(main_window: MainWindow, test_project_id: str, app: QApplication) -> None:
    """回归：进入工作区后 _workspace_view._project.path 非空"""
    enter_workspace(main_window, test_project_id, app)
    project = main_window._workspace_view._project
    assert project is not None
    assert project.path != ""


@pytest.mark.gui
def test_bug2_sync_no_crash(main_window: MainWindow, app: QApplication) -> None:
    """回归：同步缓存操作不崩溃"""
    sync_cache(main_window, app)
    # 未抛出异常即通过


@pytest.mark.gui
def test_bug3_refresh_no_crash(main_window: MainWindow, app: QApplication) -> None:
    """回归：刷新列表操作不崩溃"""
    refresh_list(main_window, app)
    # 未抛出异常即通过


@pytest.mark.gui
def test_bug4_nav_tree_counts(main_window: MainWindow) -> None:
    """回归：导航树 update_counts 传入空列表不崩溃"""
    assert main_window._nav_tree is not None
    main_window._nav_tree.update_counts([])
    # 未抛出异常即通过


@pytest.mark.gui
def test_bug5_search_special_chars(main_window: MainWindow, app: QApplication) -> None:
    """回归：特殊字符搜索安全，不崩溃"""
    search_projects(main_window, "<script>alert(1)</script>", app)
    # 未抛出异常即通过
