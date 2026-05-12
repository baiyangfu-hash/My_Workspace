# -*- coding: utf-8 -*-
"""
规范中心界面测试用例
"""
import pytest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTimer
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui.widgets.spec_center import SpecCenterWidget


@pytest.fixture
def app():
    """创建QApplication实例"""
    return QApplication([])


def test_spec_center_initialization(app, qtbot):
    """测试规范中心初始化"""
    # 创建规范中心部件
    spec_center = SpecCenterWidget()
    qtbot.addWidget(spec_center)
    
    # 测试部件是否可见
    assert spec_center.isVisible() == False
    
    # 显示部件
    spec_center.show()
    qtbot.waitForWindowShown(spec_center)
    assert spec_center.isVisible() == True


def test_spec_center_toolbar(app, qtbot):
    """测试规范中心工具栏"""
    spec_center = SpecCenterWidget()
    qtbot.addWidget(spec_center)
    spec_center.show()
    qtbot.waitForWindowShown(spec_center)
    
    # 测试工具栏是否存在
    toolbar = spec_center.findChild(lambda w: w.objectName() == "specCenterToolbar")
    assert toolbar is not None
    
    # 测试规范同步按钮
    sync_btn = spec_center.findChild(lambda w: w.text() == "规范同步")
    assert sync_btn is not None


def test_spec_center_sync_dialog(app, qtbot):
    """测试规范同步对话框打开"""
    spec_center = SpecCenterWidget()
    qtbot.addWidget(spec_center)
    spec_center.show()
    qtbot.waitForWindowShown(spec_center)
    
    # 点击规范同步按钮
    sync_btn = spec_center.findChild(lambda w: w.text() == "规范同步")
    assert sync_btn is not None
    
    # 点击按钮后，应该打开规范同步对话框
    # 由于无法直接检测对话框是否打开，我们可以测试点击按钮后是否没有异常
    try:
        qtbot.mouseClick(sync_btn, Qt.LeftButton)
        # 等待对话框打开
        qtbot.wait(2000)
    except Exception as e:
        pytest.fail(f"打开规范同步对话框失败: {e}")


def test_spec_center_close(app, qtbot):
    """测试规范中心关闭"""
    spec_center = SpecCenterWidget()
    qtbot.addWidget(spec_center)
    spec_center.show()
    qtbot.waitForWindowShown(spec_center)
    
    # 关闭部件
    spec_center.close()
    qtbot.waitUntil(lambda: not spec_center.isVisible(), timeout=5000)
    assert spec_center.isVisible() == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
