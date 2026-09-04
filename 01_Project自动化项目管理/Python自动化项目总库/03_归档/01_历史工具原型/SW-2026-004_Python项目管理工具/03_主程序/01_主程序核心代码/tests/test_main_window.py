# -*- coding: utf-8 -*-
"""
主窗口测试用例
"""
import pytest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTimer
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui.main_window import MainWindow


@pytest.fixture
def app():
    """创建QApplication实例"""
    return QApplication([])


def test_main_window_initialization(app, qtbot):
    """测试主窗口初始化"""
    # 创建主窗口
    window = MainWindow()
    qtbot.addWidget(window)
    
    # 测试窗口标题
    assert window.windowTitle() == "Python项目管理工具"
    
    # 测试窗口大小
    assert window.size().width() > 800
    assert window.size().height() > 600
    
    # 测试窗口是否可见
    assert window.isVisible() == False
    
    # 显示窗口
    window.show()
    qtbot.waitForWindowShown(window)
    assert window.isVisible() == True


def test_main_window_menu(app, qtbot):
    """测试主窗口菜单"""
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    qtbot.waitForWindowShown(window)
    
    # 测试文件菜单
    file_menu = window.menuBar().findChild(lambda w: w.title() == "文件")
    assert file_menu is not None
    
    # 测试编辑菜单
    edit_menu = window.menuBar().findChild(lambda w: w.title() == "编辑")
    assert edit_menu is not None
    
    # 测试视图菜单
    view_menu = window.menuBar().findChild(lambda w: w.title() == "视图")
    assert view_menu is not None
    
    # 测试帮助菜单
    help_menu = window.menuBar().findChild(lambda w: w.title() == "帮助")
    assert help_menu is not None


def test_main_window_toolbar(app, qtbot):
    """测试主窗口工具栏"""
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    qtbot.waitForWindowShown(window)
    
    # 测试工具栏是否存在
    toolbar = window.findChild(lambda w: w.objectName() == "mainToolBar")
    assert toolbar is not None
    
    # 测试工具栏按钮
    buttons = toolbar.findChildren(lambda w: w.objectName().endswith("Btn"))
    assert len(buttons) > 0


def test_main_window_close(app, qtbot):
    """测试主窗口关闭"""
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    qtbot.waitForWindowShown(window)
    
    # 关闭窗口
    window.close()
    qtbot.waitUntil(lambda: not window.isVisible(), timeout=5000)
    assert window.isVisible() == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
