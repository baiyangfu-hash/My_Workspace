"""主窗口工具栏 GUI 测试

验证工具栏的刷新/同步操作、状态栏内容与搜索/筛选控件存在性。
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtTest import QTest

from tests.gui.helpers.assertions import assert_statusbar_contains


@pytest.mark.gui
def test_refresh_list(main_window):
    """调用工具栏刷新列表方法，验证不崩溃"""
    main_window._on_refresh()
    QTest.qWait(1000)
    # 未抛出异常即通过


@pytest.mark.gui
def test_sync_cache(main_window):
    """调用工具栏同步缓存方法，验证不崩溃"""
    main_window._on_sync()
    QTest.qWait(1000)
    # 未抛出异常即通过


@pytest.mark.gui
def test_statusbar_workspace(main_window):
    """验证状态栏工作空间标签含'工作空间'"""
    assert_statusbar_contains(main_window, "workspace", "工作空间")


@pytest.mark.gui
def test_statusbar_project(main_window):
    """验证状态栏项目标签含'项目'"""
    assert_statusbar_contains(main_window, "project", "项目")


@pytest.mark.gui
def test_search_box_exists(main_window):
    """验证顶部搜索框控件存在"""
    assert main_window._search_edit is not None


@pytest.mark.gui
def test_business_combo_exists(main_window):
    """验证业务线筛选下拉框控件存在"""
    assert main_window._business_combo is not None
