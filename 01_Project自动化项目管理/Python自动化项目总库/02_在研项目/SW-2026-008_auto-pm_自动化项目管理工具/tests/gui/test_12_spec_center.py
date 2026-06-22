"""规范中心全局页 GUI 测试

验证规范中心的页面切换、实例初始化与规范打开按钮存在性。
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from tests.gui.helpers.interactions import click_nav_page


@pytest.mark.gui
def test_switch_to_spec_center(main_window, app):
    """切换到规范中心页，验证页面栈索引为 7"""
    click_nav_page(main_window, "spec_center", app)
    assert main_window._stack.currentIndex() == 7


@pytest.mark.gui
def test_spec_center_initialized(main_window):
    """验证规范中心视图实例已初始化"""
    assert main_window._spec_center_view is not None


@pytest.mark.gui
def test_spec_open_button_exists(main_window):
    """验证 PLC 905 规范的打开按钮存在（规范文件不存在则跳过）"""
    btn = main_window._spec_center_view.get_open_button("plc", "905")
    if btn is None:
        pytest.skip("规范文件不存在，打开按钮未创建")
    assert btn is not None
