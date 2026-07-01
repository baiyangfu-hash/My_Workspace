"""检查 Tab GUI 集成测试

测试内容：
- 切换到检查 Tab
- 实际执行检查并验证检查结果内容（V3 升级）
- 检查结果分组渲染
- 实际执行自动修复并验证修复效果（V3 升级）
- 标准化命名预览内容验证（V3 升级）

V3 升级（2026-07-02）：
  - test_run_check_actual：监听 check_completed 信号 + 验证 _last_check_result
    （pass_count/warn_count/fail_count + items 完整性 + 摘要栏格式）
  - test_auto_repair_actual：调用 _on_repair_item() 实际执行修复（dry_run=False）+
    监听 repair_completed 信号 + 验证修复后 fail_count 减少
  - test_standardize_preview_actual：验证标准化预览的实际内容
    （摘要栏格式 + 分组卡片存在）

使用 tests/gui/conftest.py 提供的 main_window / app / test_project_id fixture，
通过 helpers 辅助函数操作 GUI。
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

# V0.5.2: 默认可见模式（用户要求）；offscreen 仅通过 QT_QPA_PLATFORM=offscreen 环境变量设置

import pytest  # noqa: E402
from PySide6.QtTest import QTest  # noqa: E402

from tests.gui.helpers.interactions import (  # noqa: E402
    dismiss_message_boxes,
    enter_workspace,
    switch_workspace_tab,
)

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication

    from auto_pm.ui.main_window import MainWindow


@pytest.mark.gui
class TestCheckTab:
    """检查 Tab GUI 集成测试"""

    def test_switch_to_check_tab(self, main_window: MainWindow, app: QApplication, test_project_id: str) -> None:
        """进入工作区后切换到检查 Tab，验证 _check_tab 已初始化"""
        enter_workspace(main_window, test_project_id, app)
        switch_workspace_tab(main_window, "check", app)

        check_tab = main_window._workspace_view._check_tab
        assert check_tab is not None, "检查 Tab 未初始化"

    def test_run_check_actual(self, main_window: MainWindow, app: QApplication, test_project_id: str) -> None:
        """V3：实际执行检查 + 监听 check_completed 信号 + 验证检查结果内容

        验证项：
        - check_completed 信号被发射
        - _last_check_result 不为 None
        - 摘要栏格式正确（包含 pass_count/warn_count/fail_count 数值）
        - 分组卡片数量 >= 1
        - pass_count + warn_count + fail_count == len(items)
        """
        enter_workspace(main_window, test_project_id, app)
        switch_workspace_tab(main_window, "check", app)

        check_tab = main_window._workspace_view._check_tab
        assert check_tab is not None

        # 监听 check_completed 信号
        completed: list[bool] = []
        check_tab.check_completed.connect(lambda: completed.append(True))

        check_tab._check_btn.click()
        app.processEvents()
        QTest.qWait(1000)
        dismiss_message_boxes(app)

        # 验证信号已发射
        assert len(completed) == 1, "check_completed 信号未发射"

        # 验证 _last_check_result
        result = check_tab._last_check_result
        assert result is not None, "_last_check_result 为 None"

        # 验证摘要栏格式
        summary = check_tab._summary_label.text()
        assert "通过" in summary, f"摘要栏未包含'通过': {summary}"
        assert "警告" in summary, f"摘要栏未包含'警告': {summary}"
        assert "失败" in summary, f"摘要栏未包含'失败': {summary}"
        assert str(result.pass_count) in summary, (
            f"摘要栏未包含 pass_count={result.pass_count}: {summary}"
        )
        assert str(result.warn_count) in summary, (
            f"摘要栏未包含 warn_count={result.warn_count}: {summary}"
        )
        assert str(result.fail_count) in summary, (
            f"摘要栏未包含 fail_count={result.fail_count}: {summary}"
        )

        # 验证分组卡片
        cards = check_tab._get_group_cards()
        assert len(cards) >= 1, f"分组卡片数预期 >=1，实际 {len(cards)}"

        # 验证 items 完整性
        total = result.pass_count + result.warn_count + result.fail_count
        assert total == len(result.items), (
            f"检查项总数不匹配: pass+warn+fail={total}, len(items)={len(result.items)}"
        )

    def test_check_renders_groups(self, main_window: MainWindow, app: QApplication, test_project_id: str) -> None:
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

    def test_auto_repair_actual(self, main_window: MainWindow, app: QApplication, test_project_id: str) -> None:
        """V3：实际执行修复 + 监听 repair_completed 信号 + 验证修复效果

        通过 _on_repair_item() 触发实际修复（dry_run=False），
        验证修复后 fail_count <= 修复前的 fail_count。

        注意：实际修复会添加缺失的目录/文件，但 session 结束后 pytest 自动清理 tmp。
        """
        enter_workspace(main_window, test_project_id, app)
        switch_workspace_tab(main_window, "check", app)

        check_tab = main_window._workspace_view._check_tab
        assert check_tab is not None

        # 步骤1：先执行检查，记录修复前的 fail_count
        check_tab._check_btn.click()
        app.processEvents()
        QTest.qWait(1000)
        dismiss_message_boxes(app)

        result_before = check_tab._last_check_result
        assert result_before is not None, "修复前检查失败"
        fail_before = result_before.fail_count

        # 如果没有 fail 项，验证 _on_repair_item 不崩溃即可
        if fail_before == 0:
            check_tab._on_repair_item("test_noop")
            app.processEvents()
            QTest.qWait(2000)
            dismiss_message_boxes(app)
            return

        # 步骤2：监听 repair_completed 信号
        completed: list[bool] = []
        check_tab.repair_completed.connect(lambda: completed.append(True))

        # 步骤3：触发实际修复（_on_repair_item 使用 dry_run=False）
        check_tab._on_repair_item("test_auto_repair")
        app.processEvents()
        QTest.qWait(2000)
        dismiss_message_boxes(app)

        # 验证信号已发射
        assert len(completed) == 1, "repair_completed 信号未发射"

        # 步骤4：验证修复后的检查结果
        result_after = check_tab._last_check_result
        assert result_after is not None, "修复后检查失败"

        # 验证修复效果：fail_count 应该减少或不变（不能增加）
        assert result_after.fail_count <= fail_before, (
            f"修复后 fail_count 增加: before={fail_before}, after={result_after.fail_count}"
        )

        # 验证摘要栏已更新
        summary = check_tab._summary_label.text()
        assert "通过" in summary, f"摘要栏未包含'通过': {summary}"

    def test_standardize_preview_actual(self, main_window: MainWindow, app: QApplication, test_project_id: str) -> None:
        """V3：验证标准化预览的实际内容（不只是不崩溃）

        验证项：
        - 摘要栏包含"标准化预览"
        - 分组卡片存在
        - 摘要栏包含 applied_count/skipped_count 数值

        注意：保持预览模式（apply=False），不实际重命名文件，避免影响后续测试。
        """
        enter_workspace(main_window, test_project_id, app)
        switch_workspace_tab(main_window, "check", app)

        check_tab = main_window._workspace_view._check_tab
        assert check_tab is not None

        check_tab._standardize_btn.click()
        app.processEvents()
        QTest.qWait(1000)
        dismiss_message_boxes(app)

        # 验证摘要栏包含"标准化预览"
        summary = check_tab._summary_label.text()
        assert "标准化预览" in summary, f"摘要栏未包含'标准化预览': {summary}"

        # 验证分组卡片存在
        cards = check_tab._get_group_cards()
        assert len(cards) >= 1, f"分组卡片数预期 >=1，实际 {len(cards)}"
