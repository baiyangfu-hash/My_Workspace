"""GUI 边界测试

验证搜索框与导航在极端输入下的健壮性：空串、超长串、特殊字符、
Unicode、快速切换、快速修改、清空恢复。
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from tests.gui.helpers.interactions import (
    clear_search,
    click_nav_page,
    search_projects,
)


@pytest.mark.gui
def test_empty_search(main_window, app):
    """空字符串搜索，验证不崩溃"""
    search_projects(main_window, "", app)
    # 未抛出异常即通过


@pytest.mark.gui
def test_long_search(main_window, app):
    """超长字符串（1000 个 A）搜索，验证不崩溃"""
    search_projects(main_window, "A" * 1000, app)
    # 未抛出异常即通过


@pytest.mark.gui
def test_special_char_search(main_window, app):
    """特殊字符（XSS payload）搜索，验证不崩溃"""
    search_projects(main_window, "<script>alert(1)</script>", app)
    # 未抛出异常即通过


@pytest.mark.gui
def test_unicode_search(main_window, app):
    """Unicode 字符（中文+emoji）搜索，验证不崩溃"""
    search_projects(main_window, "中文搜索测试🎉", app)
    # 未抛出异常即通过


@pytest.mark.gui
def test_rapid_nav_switch(main_window, app):
    """连续 5 次切换不同功能页面，验证不崩溃"""
    pages = ["all_projects", "report", "template", "settings", "spec_center"]
    for page_id in pages:
        click_nav_page(main_window, page_id, app)
    # 未抛出异常即通过


@pytest.mark.gui
def test_rapid_search_change(main_window, app):
    """连续 5 次修改搜索框内容，验证不崩溃"""
    texts = ["A", "B", "C", "中文", "🎉"]
    for text in texts:
        main_window._search_edit.setText(text)
        app.processEvents()
    # 未抛出异常即通过


@pytest.mark.gui
def test_clear_search_restores(main_window, app):
    """搜索后清空搜索框，验证 _filtered_projects 恢复到初始数量"""
    list_view = main_window._project_list_view
    initial_count = len(list_view._filtered_projects)
    search_projects(main_window, "ZZZZ_NOT_EXIST_ZZZZ", app)
    clear_search(main_window, app)
    restored_count = len(list_view._filtered_projects)
    assert restored_count == initial_count
