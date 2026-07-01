"""报告中心全局页 GUI 测试

验证报告中心的页面切换、卡片可见性、刷新与内容渲染。
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

# V0.5.2: 默认可见模式（用户要求）；offscreen 仅通过 QT_QPA_PLATFORM=offscreen 环境变量设置

import pytest
from PySide6.QtTest import QTest

from tests.gui.helpers.assertions import assert_report_cards_visible
from tests.gui.helpers.interactions import click_nav_page

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication

    from auto_pm.ui.main_window import MainWindow


@pytest.mark.gui
def test_switch_to_report(main_window: MainWindow, app: QApplication) -> None:
    """切换到报告中心页，验证页面栈索引为 4"""
    click_nav_page(main_window, "report", app)
    assert main_window._stack.currentIndex() == 4


@pytest.mark.gui
def test_report_page_initialized(main_window: MainWindow) -> None:
    """验证报告中心页实例已初始化"""
    assert main_window._report_page is not None


@pytest.mark.gui
def test_report_cards_visible(main_window: MainWindow) -> None:
    """验证报告中心 4 个统计卡片均存在"""
    assert_report_cards_visible(main_window._report_page)


@pytest.mark.gui
def test_report_refresh(main_window: MainWindow) -> None:
    """调用报告中心 refresh 重新加载数据，验证不崩溃"""
    main_window._report_page.refresh()
    QTest.qWait(500)
    # 未抛出异常即通过


@pytest.mark.gui
def test_report_project_card_has_content(main_window: MainWindow) -> None:
    """验证项目概览卡片标题非空或包含子控件"""
    card = main_window._report_page._project_card
    layout = card.layout()
    assert card.title() != "" or (layout is not None and layout.count() > 0)
