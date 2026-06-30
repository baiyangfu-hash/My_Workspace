"""导航树测试

验证 NavigationTree 的 page_switch_requested 与 project_filter_requested 信号
能正确驱动 MainWindow 切换页面栈索引与项目筛选状态。
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication

from tests.gui.helpers.assertions import assert_stack_index
from tests.gui.helpers.interactions import click_nav_filter, click_nav_page

if TYPE_CHECKING:
    from auto_pm.ui.main_window import MainWindow


@pytest.mark.gui
class TestNavigation:
    """导航树切换与筛选测试"""

    def test_click_all_projects(self, main_window: MainWindow, app: QApplication) -> None:
        """点击 'all_projects' 导航项，页面栈切换到索引 0（项目列表）"""
        click_nav_page(main_window, "all_projects", app)
        assert_stack_index(main_window, 0)

    def test_click_change_center(self, main_window: MainWindow, app: QApplication) -> None:
        """点击 'change_center' 导航项，页面栈切换到索引 3（变更中心）"""
        click_nav_page(main_window, "change_center", app)
        assert_stack_index(main_window, 3)

    def test_click_report(self, main_window: MainWindow, app: QApplication) -> None:
        """点击 'report' 导航项，页面栈切换到索引 4（报告中心）"""
        click_nav_page(main_window, "report", app)
        assert_stack_index(main_window, 4)

    def test_click_template(self, main_window: MainWindow, app: QApplication) -> None:
        """点击 'template' 导航项，页面栈切换到索引 5（模板管理）"""
        click_nav_page(main_window, "template", app)
        assert_stack_index(main_window, 5)

    def test_click_settings(self, main_window: MainWindow, app: QApplication) -> None:
        """点击 'settings' 导航项，页面栈切换到索引 6（系统设置）"""
        click_nav_page(main_window, "settings", app)
        assert_stack_index(main_window, 6)

    def test_click_spec_center(self, main_window: MainWindow, app: QApplication) -> None:
        """点击 'spec_center' 导航项，页面栈切换到索引 7（规范中心）"""
        click_nav_page(main_window, "spec_center", app)
        assert_stack_index(main_window, 7)

    def test_filter_plc_stack(self, main_window: MainWindow, app: QApplication) -> None:
        """emit project_filter_requested('plc', 'all')，验证项目列表 _filter_stack=='plc'"""
        click_nav_filter(main_window, "plc", "all", app)
        actual = main_window._project_list_view._filter_stack
        assert actual == "plc", f"项目列表 _filter_stack 预期 'plc'，实际 '{actual}'"

    def test_filter_developing_phase(self, main_window: MainWindow, app: QApplication) -> None:
        """emit project_filter_requested('plc', 'developing')，验证不崩溃且筛选状态更新"""
        click_nav_filter(main_window, "plc", "developing", app)
        # 验证筛选后不崩溃：_filter_stack 与 _filter_phase 已更新
        plv = main_window._project_list_view
        assert plv._filter_stack == "plc", (
            f"筛选后 _filter_stack 预期 'plc'，实际 '{plv._filter_stack}'"
        )
        assert plv._filter_phase == "developing", (
            f"筛选后 _filter_phase 预期 'developing'，实际 '{plv._filter_phase}'"
        )
