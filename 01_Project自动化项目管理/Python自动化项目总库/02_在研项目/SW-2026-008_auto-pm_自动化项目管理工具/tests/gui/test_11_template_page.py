"""模板管理全局页 GUI 测试

验证模板管理页的页面切换、实例初始化与刷新操作。
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtTest import QTest

from tests.gui.helpers.interactions import click_nav_page


@pytest.mark.gui
def test_switch_to_template(main_window, app):
    """切换到模板管理页，验证页面栈索引为 5"""
    click_nav_page(main_window, "template", app)
    assert main_window._stack.currentIndex() == 5


@pytest.mark.gui
def test_template_page_initialized(main_window):
    """验证模板管理页实例已初始化"""
    assert main_window._template_page is not None


@pytest.mark.gui
def test_template_refresh(main_window):
    """调用模板管理页 refresh 重新加载模板列表，验证不崩溃"""
    main_window._template_page.refresh()
    QTest.qWait(500)
    # 未抛出异常即通过
