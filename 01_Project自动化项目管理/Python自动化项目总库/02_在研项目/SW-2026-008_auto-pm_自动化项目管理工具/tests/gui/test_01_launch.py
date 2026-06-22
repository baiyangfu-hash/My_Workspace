"""启动与窗口测试

验证 MainWindow 启动后的基础属性：窗口标题、尺寸、状态栏、关键控件存在性。
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from tests.gui.helpers.assertions import (
    assert_statusbar_contains,
    assert_window_title,
)


@pytest.mark.gui
class TestLaunch:
    """启动与窗口基础测试"""

    def test_window_title(self, main_window, app):
        """验证窗口标题为 'auto-pm 项目管理工具'"""
        assert_window_title(main_window, "auto-pm 项目管理工具")

    def test_window_size(self, main_window, app):
        """验证窗口尺寸 width>=1280, height>=800"""
        w = main_window.width()
        h = main_window.height()
        assert w >= 1280, f"窗口宽度预期 >=1280，实际 {w}"
        assert h >= 800, f"窗口高度预期 >=800，实际 {h}"

    def test_statusbar_initialized(self, main_window, app):
        """验证状态栏 _status_workspace 文本含 '工作空间'"""
        assert_statusbar_contains(main_window, "workspace", "工作空间")

    def test_nav_tree_exists(self, main_window, app):
        """验证导航树 _nav_tree 不为 None"""
        assert main_window._nav_tree is not None, "导航树 _nav_tree 为 None"

    def test_project_list_view_exists(self, main_window, app):
        """验证项目列表视图 _project_list_view 不为 None"""
        assert main_window._project_list_view is not None, (
            "项目列表视图 _project_list_view 为 None"
        )

    def test_stack_has_pages(self, main_window, app):
        """验证中央页面栈 _stack.count() >= 8"""
        count = main_window._stack.count()
        assert count >= 8, f"页面栈数量预期 >=8，实际 {count}"
