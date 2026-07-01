"""变更中心 GUI 集成测试

测试内容：
- 切换到变更中心页面
- 变更中心视图及子面板初始化
- 状态 Tab 切换（不崩溃）
- 创建变更单对话框弹出与关闭（复用修复后的 find_dialog 支持嵌套）
- 变更中心刷新（不崩溃）

V3 升级（2026-07-01）：
  - test_create_change_dialog_from_center 改用 helpers.find_dialog（支持嵌套 QDialog）
  - 所有 error 分支调用 close_all_modal_widgets 防止残留弹窗阻塞
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

# 必须在导入 PySide6 前设置离屏渲染，避免无显示环境报错
# V0.5.2: 默认可见模式（用户要求）；offscreen 仅通过 QT_QPA_PLATFORM=offscreen 环境变量设置

import pytest  # noqa: E402
from PySide6.QtCore import QTimer  # noqa: E402
from PySide6.QtTest import QTest  # noqa: E402

from tests.gui.helpers.assertions import assert_stack_index  # noqa: E402
from tests.gui.helpers.interactions import (  # noqa: E402
    click_nav_page,
    close_all_modal_widgets,
    find_dialog,
)

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication

    from auto_pm.ui.main_window import MainWindow


@pytest.mark.gui
class TestChangeCenter:
    """变更中心 GUI 集成测试"""

    def test_switch_to_change_center(self, main_window: MainWindow, app: QApplication) -> None:
        """点击导航切换到变更中心，验证页面栈索引为 3"""
        click_nav_page(main_window, "change_center", app)
        assert_stack_index(main_window, 3)

    def test_change_center_initialized(self, main_window: MainWindow, app: QApplication) -> None:
        """验证变更中心视图已初始化"""
        click_nav_page(main_window, "change_center", app)
        assert main_window._change_center_view is not None, "变更中心视图未初始化"

    def test_change_center_list_panel(self, main_window: MainWindow, app: QApplication) -> None:
        """验证变更中心列表面板已初始化"""
        click_nav_page(main_window, "change_center", app)
        view = main_window._change_center_view
        assert view is not None
        assert view._list_panel is not None, "变更列表面板未初始化"

    def test_change_center_detail_panel(self, main_window: MainWindow, app: QApplication) -> None:
        """验证变更中心详情面板已初始化"""
        click_nav_page(main_window, "change_center", app)
        view = main_window._change_center_view
        assert view is not None
        assert view._detail_panel is not None, "变更详情面板未初始化"

    def test_status_tab_switch(self, main_window: MainWindow, app: QApplication) -> None:
        """遍历状态 Tab 按钮逐个点击，验证不崩溃"""
        click_nav_page(main_window, "change_center", app)
        view = main_window._change_center_view
        assert view is not None

        status_tabs = view._list_panel._status_tabs
        assert len(status_tabs) > 0, "状态 Tab 列表为空"

        for btn in status_tabs.values():
            btn.click()
            app.processEvents()
            QTest.qWait(200)

    def test_create_change_dialog_from_center(self, main_window: MainWindow, app: QApplication) -> None:
        """点击创建变更单按钮，验证对话框弹出后关闭

        V3 升级：改用 helpers.find_dialog（支持嵌套 QDialog，findChildren 递归查找），
        替代原 topLevelWidgets 遍历（找不到有 parent 的 QWizard）。
        """
        click_nav_page(main_window, "change_center", app)
        view = main_window._change_center_view
        assert view is not None

        found: list[bool] = [False]

        def _verify_and_close() -> None:
            dlg = find_dialog(app, "创建变更单", timeout_ms=2000)
            if dlg is not None:
                found[0] = True
                # 直接 reject 避免 reject_dialog 内 qWait 嵌套事件循环吞掉 done()
                dlg.reject()
                app.processEvents()
                return
            # 兜底：关闭可能残留的弹窗
            close_all_modal_widgets(app)

        QTimer.singleShot(100, _verify_and_close)
        view._create_btn.click()
        app.processEvents()
        # 确保 exec() 退出后清理残留
        close_all_modal_widgets(app)

        assert found[0], "创建变更单对话框未弹出"

    def test_refresh_change_center(self, main_window: MainWindow, app: QApplication) -> None:
        """调用变更中心 refresh()，验证不崩溃"""
        click_nav_page(main_window, "change_center", app)
        view = main_window._change_center_view
        assert view is not None

        view.refresh()
        app.processEvents()
        QTest.qWait(500)
