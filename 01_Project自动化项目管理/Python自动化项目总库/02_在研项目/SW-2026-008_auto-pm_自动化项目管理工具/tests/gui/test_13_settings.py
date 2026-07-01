"""系统设置全局页 GUI 测试

验证系统设置页的页面切换、信息加载、控件交互与刷新操作。
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

# V0.5.2: 默认可见模式（用户要求）；offscreen 仅通过 QT_QPA_PLATFORM=offscreen 环境变量设置

import pytest
from PySide6.QtCore import QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QMessageBox

from tests.gui.helpers.assertions import assert_settings_loaded
from tests.gui.helpers.interactions import click_nav_page, dismiss_message_boxes

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication

    from auto_pm.ui.main_window import MainWindow


@pytest.mark.gui
def test_switch_to_settings(main_window: MainWindow, app: QApplication) -> None:
    """切换到系统设置页，验证页面栈索引为 6"""
    click_nav_page(main_window, "settings", app)
    assert main_window._stack.currentIndex() == 6


@pytest.mark.gui
def test_settings_page_initialized(main_window: MainWindow) -> None:
    """验证系统设置页实例已初始化"""
    assert main_window._settings_page is not None


@pytest.mark.gui
def test_settings_loaded(main_window: MainWindow) -> None:
    """验证系统设置页已加载工作空间路径与 DB 路径信息"""
    assert_settings_loaded(main_window._settings_page)


@pytest.mark.gui
def test_settings_workspace_path(main_window: MainWindow) -> None:
    """验证工作空间路径输入框文本非空"""
    assert main_window._settings_page.workspace_edit.text() != ""


@pytest.mark.gui
def test_settings_depth_spin(main_window: MainWindow) -> None:
    """验证扫描深度 SpinBox 当前值 >= 1"""
    assert main_window._settings_page.depth_spin.value() >= 1


@pytest.mark.gui
def test_settings_modify_depth(main_window: MainWindow) -> None:
    """设置扫描深度为 3，验证值可正确回读"""
    main_window._settings_page.depth_spin.setValue(3)
    assert main_window._settings_page.depth_spin.value() == 3


@pytest.mark.gui
def test_settings_rebuild_index_cancel(main_window: MainWindow, app: QApplication) -> None:
    """点击重建索引按钮，弹窗选否取消重建，验证不崩溃"""
    settings_page = main_window._settings_page

    def _reject_boxes() -> None:
        """关闭所有可见 QMessageBox（选否/取消）"""
        for w in app.topLevelWidgets():
            if isinstance(w, QMessageBox) and w.isVisible():
                w.reject()
        app.processEvents()

    # 弹窗为模态，需在点击前调度关闭（选否取消重建）
    QTimer.singleShot(0, _reject_boxes)
    settings_page.rebuild_button.click()
    QTest.qWait(500)
    dismiss_message_boxes(app)
    # 未抛出异常即通过


@pytest.mark.gui
def test_settings_refresh(main_window: MainWindow) -> None:
    """调用系统设置页 refresh 重新加载统计，验证不崩溃"""
    main_window._settings_page.refresh()
    QTest.qWait(500)
    # 未抛出异常即通过
