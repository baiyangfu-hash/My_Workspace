"""StatusMachineView 单元测试（M3-4 T79）

测试内容：
- 12 个状态节点 + 11 个箭头渲染
- 当前状态节点禁用 + 蓝色边框样式
- 目标状态节点启用 + 绿色填充样式
- 可达状态节点启用
- 不可达状态节点禁用
- 节点点击发射 target_selected 信号（仅可达）
- 不可达点击不发射信号
- set_current 更新可达状态集合
- set_target 更新目标样式
- get_reachable_targets 返回正确集合
"""

from __future__ import annotations

import os

import pytest

# 必须在导入 PySide6 前设置离屏渲染，避免无显示环境报错
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from auto_pm.change.models import STATUS_FLOW  # noqa: E402
from auto_pm.ui.dialogs.status_machine_view import (  # noqa: E402
    _STATUS_ORDER,
    StatusMachineView,
)

# ── fixtures ─────────────────────────────────────────────


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """提供全局 QApplication 实例（session 级复用）"""
    app = QApplication.instance() or QApplication([])
    yield app


# ── 测试用例 ─────────────────────────────────────────────


class TestStatusMachineViewRender:
    """StatusMachineView 渲染测试"""

    def test_node_count_12(self, qapp: QApplication) -> None:
        """12 个状态节点"""
        view = StatusMachineView(current_status="draft")
        assert len(view._buttons) == 12
        assert len(_STATUS_ORDER) == 12

    def test_arrow_count_11(self, qapp: QApplication) -> None:
        """11 个箭头（节点间）"""
        view = StatusMachineView(current_status="draft")
        assert len(view._arrows) == 11

    def test_node_labels_from_status_labels(self, qapp: QApplication) -> None:
        """节点文字来自 STATUS_LABELS 中文标签"""
        from auto_pm.change.models import STATUS_LABELS

        view = StatusMachineView(current_status="draft")
        for status, btn in view._buttons.items():
            assert btn.text() == STATUS_LABELS.get(status, status)

    def test_all_status_covered(self, qapp: QApplication) -> None:
        """_STATUS_ORDER 覆盖 STATUS_FLOW 全部状态"""
        flow_statuses = set(STATUS_FLOW.keys())
        order_statuses = set(_STATUS_ORDER)
        assert flow_statuses == order_statuses


class TestStatusMachineViewState:
    """StatusMachineView 状态高亮测试"""

    def test_current_node_disabled(self, qapp: QApplication) -> None:
        """当前状态节点禁用"""
        view = StatusMachineView(current_status="draft", target_status="submitted")
        assert not view._buttons["draft"].isEnabled()

    def test_target_node_enabled_with_green_style(self, qapp: QApplication) -> None:
        """目标状态节点启用 + 绿色填充样式"""
        view = StatusMachineView(current_status="draft", target_status="submitted")
        btn = view._buttons["submitted"]
        assert btn.isEnabled()
        style = btn.styleSheet()
        assert "#27ae60" in style  # 绿色填充

    def test_current_node_blue_border_style(self, qapp: QApplication) -> None:
        """当前状态节点蓝色边框样式"""
        view = StatusMachineView(current_status="draft", target_status="submitted")
        style = view._buttons["draft"].styleSheet()
        assert "#4a90d9" in style  # 蓝色边框
        assert "#e6f0ff" in style  # 浅蓝背景

    def test_reachable_node_enabled(self, qapp: QApplication) -> None:
        """可达状态节点启用（draft 可达 submitted）"""
        view = StatusMachineView(current_status="draft")
        # draft 可达 {submitted}
        assert view._buttons["submitted"].isEnabled()

    def test_unreachable_node_disabled(self, qapp: QApplication) -> None:
        """不可达状态节点禁用（draft 不可达 approved）"""
        view = StatusMachineView(current_status="draft")
        assert not view._buttons["approved"].isEnabled()
        assert not view._buttons["completed"].isEnabled()
        assert not view._buttons["closed"].isEnabled()

    def test_terminal_state_no_reachable(self, qapp: QApplication) -> None:
        """终态（closed）无可达状态"""
        view = StatusMachineView(current_status="closed")
        assert view.get_reachable_targets() == set()
        # 所有节点都不可达（除当前状态）
        for status, btn in view._buttons.items():
            if status == "closed":
                continue
            assert not btn.isEnabled(), f"{status} should be disabled"

    def test_get_reachable_targets_draft(self, qapp: QApplication) -> None:
        """draft 可达 {submitted}"""
        view = StatusMachineView(current_status="draft")
        assert view.get_reachable_targets() == {"submitted"}

    def test_get_reachable_targets_submitted(self, qapp: QApplication) -> None:
        """submitted 可达 {under_review, draft}"""
        view = StatusMachineView(current_status="submitted")
        assert view.get_reachable_targets() == {"under_review", "draft"}

    def test_get_reachable_targets_under_review(self, qapp: QApplication) -> None:
        """under_review 可达 {approved, conditionally_approved, rejected, submitted}"""
        view = StatusMachineView(current_status="under_review")
        assert view.get_reachable_targets() == {
            "approved",
            "conditionally_approved",
            "rejected",
            "submitted",
        }


class TestStatusMachineViewSignal:
    """StatusMachineView 信号测试"""

    def test_reachable_click_emits_signal(self, qapp: QApplication) -> None:
        """点击可达状态节点发射 target_selected 信号"""
        view = StatusMachineView(current_status="draft")
        received: list[str] = []
        view.target_selected.connect(lambda s: received.append(s))

        view._on_node_clicked("submitted")
        assert received == ["submitted"]

    def test_unreachable_click_no_signal(self, qapp: QApplication) -> None:
        """点击不可达状态节点不发射信号"""
        view = StatusMachineView(current_status="draft")
        received: list[str] = []
        view.target_selected.connect(lambda s: received.append(s))

        view._on_node_clicked("approved")
        view._on_node_clicked("completed")
        assert received == []

    def test_current_click_no_signal(self, qapp: QApplication) -> None:
        """点击当前状态节点不发射信号"""
        view = StatusMachineView(current_status="draft")
        received: list[str] = []
        view.target_selected.connect(lambda s: received.append(s))

        view._on_node_clicked("draft")
        assert received == []


class TestStatusMachineViewUpdate:
    """StatusMachineView 动态更新测试"""

    def test_set_target_updates_style(self, qapp: QApplication) -> None:
        """set_target 更新目标节点样式"""
        view = StatusMachineView(current_status="draft")
        # 初始无目标
        assert "#27ae60" not in view._buttons["submitted"].styleSheet()

        view.set_target("submitted")
        assert "#27ae60" in view._buttons["submitted"].styleSheet()

    def test_set_current_updates_reachable(self, qapp: QApplication) -> None:
        """set_current 更新可达状态集合"""
        view = StatusMachineView(current_status="draft")
        assert view._buttons["submitted"].isEnabled()
        assert not view._buttons["approved"].isEnabled()

        view.set_current("approved")
        # approved 可达 {implementing}
        assert view._buttons["implementing"].isEnabled()
        assert not view._buttons["submitted"].isEnabled()

    def test_set_target_clear_resets_style(self, qapp: QApplication) -> None:
        """set_target('') 清空目标，节点恢复可达样式"""
        view = StatusMachineView(current_status="draft", target_status="submitted")
        assert "#27ae60" in view._buttons["submitted"].styleSheet()

        view.set_target("")
        assert "#27ae60" not in view._buttons["submitted"].styleSheet()
        # submitted 仍是可达，应启用
        assert view._buttons["submitted"].isEnabled()
