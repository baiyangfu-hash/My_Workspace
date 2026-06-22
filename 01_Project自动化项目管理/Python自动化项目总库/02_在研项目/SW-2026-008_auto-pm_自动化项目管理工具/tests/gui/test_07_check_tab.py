"""检查 Tab GUI 集成测试

测试内容：
- 切换到检查 Tab
- 执行检查并验证摘要栏
- 检查结果分组渲染
- 自动修复预览（不崩溃）
- 标准化命名预览（不崩溃）

使用 tests/gui/conftest.py 提供的 main_window / app / test_project_id fixture，
通过 helpers 辅助函数操作 GUI。
"""

from __future__ import annotations

import os

# 必须在导入 PySide6 前设置离屏渲染，避免无显示环境报错
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402
from PySide6.QtTest import QTest  # noqa: E402

from tests.gui.helpers.interactions import (  # noqa: E402
    dismiss_message_boxes,
    enter_workspace,
    switch_workspace_tab,
)


@pytest.mark.gui
class TestCheckTab:
    """检查 Tab GUI 集成测试"""

    def test_switch_to_check_tab(self, main_window, app, test_project_id):
        """进入工作区后切换到检查 Tab，验证 _check_tab 已初始化"""
        enter_workspace(main_window, test_project_id, app)
        switch_workspace_tab(main_window, "check", app)

        check_tab = main_window._workspace_view._check_tab
        assert check_tab is not None, "检查 Tab 未初始化"

    def test_run_check(self, main_window, app, test_project_id):
        """点击执行检查按钮，验证摘要栏显示通过/失败/警告计数"""
        enter_workspace(main_window, test_project_id, app)
        switch_workspace_tab(main_window, "check", app)

        check_tab = main_window._workspace_view._check_tab
        assert check_tab is not None

        check_tab._check_btn.click()
        app.processEvents()
        QTest.qWait(1000)

        summary = check_tab._summary_label.text()
        assert summary, "检查摘要栏文本为空"
        assert any(
            kw in summary for kw in ["通过", "失败", "警告"]
        ), f"检查摘要未包含状态关键词: {summary}"

    def test_check_renders_groups(self, main_window, app, test_project_id):
        """执行检查后验证分组卡片已渲染（至少 1 个分组）"""
        enter_workspace(main_window, test_project_id, app)
        switch_workspace_tab(main_window, "check", app)

        check_tab = main_window._workspace_view._check_tab
        assert check_tab is not None

        check_tab._check_btn.click()
        app.processEvents()
        QTest.qWait(1000)

        cards = check_tab._get_group_cards()
        assert len(cards) >= 1, f"分组卡片数预期 >=1，实际 {len(cards)}"

    def test_auto_repair_preview(self, main_window, app, test_project_id):
        """点击自动修复按钮，验证不崩溃并清理弹窗"""
        enter_workspace(main_window, test_project_id, app)
        switch_workspace_tab(main_window, "check", app)

        check_tab = main_window._workspace_view._check_tab
        assert check_tab is not None

        check_tab._repair_btn.click()
        app.processEvents()
        QTest.qWait(1000)

        # 清理可能出现的消息框（验证不崩溃为主）
        dismiss_message_boxes(app)

    def test_standardize_preview(self, main_window, app, test_project_id):
        """点击标准化命名按钮，验证不崩溃"""
        enter_workspace(main_window, test_project_id, app)
        switch_workspace_tab(main_window, "check", app)

        check_tab = main_window._workspace_view._check_tab
        assert check_tab is not None

        check_tab._standardize_btn.click()
        app.processEvents()
        QTest.qWait(1000)

        # 清理可能出现的消息框（验证不崩溃为主）
        dismiss_message_boxes(app)
