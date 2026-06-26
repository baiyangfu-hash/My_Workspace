"""变更中心 GUI 集成测试

测试内容：
- 切换到变更中心页面
- 变更中心视图及子面板初始化
- 状态 Tab 切换（不崩溃）
- 创建变更单对话框弹出与关闭
- 变更中心刷新（不崩溃）

使用 tests/gui/conftest.py 提供的 main_window / app fixture，
通过 helpers 辅助函数操作 GUI。
"""

from __future__ import annotations

import os

# 必须在导入 PySide6 前设置离屏渲染，避免无显示环境报错
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402
from PySide6.QtCore import QTimer  # noqa: E402
from PySide6.QtTest import QTest  # noqa: E402
from PySide6.QtWidgets import QDialog  # noqa: E402

from tests.gui.helpers.assertions import assert_stack_index  # noqa: E402
from tests.gui.helpers.interactions import click_nav_page  # noqa: E402


@pytest.mark.gui
class TestChangeCenter:
    """变更中心 GUI 集成测试"""

    def test_switch_to_change_center(self, main_window, app):
        """点击导航切换到变更中心，验证页面栈索引为 3"""
        click_nav_page(main_window, "change_center", app)
        assert_stack_index(main_window, 3)

    def test_change_center_initialized(self, main_window, app):
        """验证变更中心视图已初始化"""
        click_nav_page(main_window, "change_center", app)
        assert main_window._change_center_view is not None, "变更中心视图未初始化"

    def test_change_center_list_panel(self, main_window, app):
        """验证变更中心列表面板已初始化"""
        click_nav_page(main_window, "change_center", app)
        view = main_window._change_center_view
        assert view is not None
        assert view._list_panel is not None, "变更列表面板未初始化"

    def test_change_center_detail_panel(self, main_window, app):
        """验证变更中心详情面板已初始化"""
        click_nav_page(main_window, "change_center", app)
        view = main_window._change_center_view
        assert view is not None
        assert view._detail_panel is not None, "变更详情面板未初始化"

    def test_status_tab_switch(self, main_window, app):
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

    def test_create_change_dialog_from_center(self, main_window, app):
        """点击创建变更单按钮，验证对话框弹出后关闭

        注意：CreateChangeDialog 使用 dialog.exec() 模态阻塞，
        需通过 QTimer.singleShot 在模态事件循环中调度关闭。
        """
        click_nav_page(main_window, "change_center", app)
        view = main_window._change_center_view
        assert view is not None

        found: list[bool] = [False]

        def find_and_reject(retries: int = 100) -> None:
            """在模态事件循环中查找并关闭对话框

            注意：QWizard 改造后，reject_dialog 内的 QTest.qWait(300) 嵌套事件循环
            会吞掉 wizard.done() 的退出请求，导致 exec() 不退出。改为直接调用
            wizard.reject() 规避此问题。
            """
            for w in app.topLevelWidgets():
                if (
                    isinstance(w, QDialog)
                    and w.isVisible()
                    and "创建变更单" in w.windowTitle()
                ):
                    found[0] = True
                    w.reject()
                    app.processEvents()
                    return
            if retries > 0:
                QTimer.singleShot(10, lambda: find_and_reject(retries - 1))

        # 在 click() 触发 exec() 阻塞前调度对话框关闭
        QTimer.singleShot(0, find_and_reject)
        view._create_btn.click()
        app.processEvents()

        assert found[0], "创建变更单对话框未弹出"

    def test_refresh_change_center(self, main_window, app):
        """调用变更中心 refresh()，验证不崩溃"""
        click_nav_page(main_window, "change_center", app)
        view = main_window._change_center_view
        assert view is not None

        view.refresh()
        app.processEvents()
        QTest.qWait(500)
