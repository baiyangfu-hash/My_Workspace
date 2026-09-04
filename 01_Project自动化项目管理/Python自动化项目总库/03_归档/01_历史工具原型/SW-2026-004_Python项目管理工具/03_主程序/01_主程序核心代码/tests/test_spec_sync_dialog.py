# -*- coding: utf-8 -*-
"""
规范同步对话框测试用例
"""
import pytest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTimer
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.gui.spec_sync_dialog import SpecSyncDialog


@pytest.fixture
def app():
    """创建QApplication实例"""
    return QApplication([])


def test_spec_sync_dialog_initialization(app, qtbot):
    """测试规范同步对话框初始化"""
    # 创建对话框
    dialog = SpecSyncDialog()
    qtbot.addWidget(dialog)
    
    # 测试窗口标题
    assert dialog.windowTitle() == "规范同步中心"
    
    # 测试窗口大小
    assert dialog.size().width() >= 900
    assert dialog.size().height() >= 700
    
    # 测试窗口是否可见
    assert dialog.isVisible() == False
    
    # 显示对话框
    dialog.show()
    qtbot.waitForWindowShown(dialog)
    assert dialog.isVisible() == True


def test_spec_sync_dialog_check_updates(app, qtbot):
    """测试检查更新功能"""
    dialog = SpecSyncDialog()
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.waitForWindowShown(dialog)
    
    # 点击检查更新按钮
    check_btn = dialog.findChild(lambda w: w.text() == "检查更新")
    assert check_btn is not None
    
    # 使用QTimer避免UI阻塞
    def check_done():
        # 检查日志是否有更新信息
        log_text = dialog.log_text.toPlainText()
        assert "检查更新" in log_text
    
    QTimer.singleShot(2000, check_done)
    qtbot.mouseClick(check_btn, Qt.LeftButton)
    qtbot.wait(3000)  # 等待检查完成


def test_spec_sync_dialog_sync_all(app, qtbot):
    """测试同步所有规范功能"""
    dialog = SpecSyncDialog()
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.waitForWindowShown(dialog)
    
    # 点击同步所有按钮
    sync_all_btn = dialog.findChild(lambda w: w.text() == "同步所有")
    assert sync_all_btn is not None
    
    # 使用QTimer避免UI阻塞
    def sync_done():
        # 检查日志是否有同步信息
        log_text = dialog.log_text.toPlainText()
        assert "同步" in log_text
    
    QTimer.singleShot(3000, sync_done)
    qtbot.mouseClick(sync_all_btn, Qt.LeftButton)
    qtbot.wait(5000)  # 等待同步完成


def test_spec_sync_dialog_close(app, qtbot):
    """测试关闭对话框"""
    dialog = SpecSyncDialog()
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.waitForWindowShown(dialog)
    
    # 点击关闭按钮
    close_btn = dialog.findChild(lambda w: w.text() == "关闭")
    assert close_btn is not None
    
    qtbot.mouseClick(close_btn, Qt.LeftButton)
    qtbot.waitUntil(lambda: not dialog.isVisible(), timeout=5000)
    assert dialog.isVisible() == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
