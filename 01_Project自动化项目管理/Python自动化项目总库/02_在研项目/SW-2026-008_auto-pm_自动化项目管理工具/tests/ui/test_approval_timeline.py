"""ApprovalTimeline 单元测试（M3-3 T75）

测试内容：
- 空历史显示提示文案
- 单条/多条记录渲染节点数 + 连接线
- 节点状态流转文案（from → to 中文）
- 节点审批人 + 审批意见
- 圆点颜色对齐 to_status
- 无 DB 时 ChangeService.list_approval_history 返回空列表不崩溃

使用 MagicMock 控制 list_approval_history 返回值，聚焦 widget 渲染逻辑。
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# 必须在导入 PySide6 前设置离屏渲染，避免无显示环境报错
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QFrame, QLabel  # noqa: E402

from auto_pm.change.change_service import ChangeService  # noqa: E402
from auto_pm.change.models import STATUS_LABELS  # noqa: E402
from auto_pm.models import ApprovalRecord  # noqa: E402
from auto_pm.ui.change_center.approval_timeline import (  # noqa: E402
    _STATUS_DOT_COLOR,
    ApprovalTimeline,
)

# ── fixtures ─────────────────────────────────────────────


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """提供全局 QApplication 实例（session 级复用）"""
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def mock_service() -> MagicMock:
    """Mock ChangeService，list_approval_history 默认返回空列表"""
    svc = MagicMock(spec=ChangeService)
    svc.list_approval_history.return_value = []
    return svc


def _make_record(
    from_status: str = "draft",
    to_status: str = "submitted",
    approver: str = "fubai",
    comment: str = "提交审批，请审核",
    transition_date: str = "2026-06-25T14:30:00",
) -> ApprovalRecord:
    """构造 ApprovalRecord 测试数据"""
    return ApprovalRecord(
        change_number="CHG-TEST-001",
        from_status=from_status,
        to_status=to_status,
        approver=approver,
        comment=comment,
        transition_date=transition_date,
    )


# ── 测试用例 ─────────────────────────────────────────────


def test_empty_history_shows_hint(qapp: QApplication, mock_service: MagicMock) -> None:
    """无审批记录时显示'暂无审批记录'"""
    mock_service.list_approval_history.return_value = []
    timeline = ApprovalTimeline(mock_service)
    timeline.load_history("CHG-TEST-001")

    hint = timeline.findChild(QLabel, "emptyHint")
    assert hint is not None
    assert "暂无审批记录" in hint.text()
    # 无节点
    assert timeline.findChildren(QFrame, "timelineNode") == []


def test_single_record_renders_one_node(qapp: QApplication, mock_service: MagicMock) -> None:
    """1 条记录渲染 1 个节点，无连接线"""
    mock_service.list_approval_history.return_value = [_make_record()]
    timeline = ApprovalTimeline(mock_service)
    timeline.load_history("CHG-TEST-001")

    nodes = timeline.findChildren(QFrame, "timelineNode")
    assert len(nodes) == 1
    # 单条记录为最后一个节点，不应有连接线
    connectors = timeline.findChildren(QFrame, "nodeConnector")
    assert len(connectors) == 0


def test_multiple_records_render_connectors(qapp: QApplication, mock_service: MagicMock) -> None:
    """3 条记录渲染 3 节点，前 2 个有连接线，最后 1 个无连接线"""
    records = [
        _make_record(from_status="draft", to_status="submitted", comment="提交"),
        _make_record(from_status="submitted", to_status="under_review", comment="审核中"),
        _make_record(from_status="under_review", to_status="approved", comment="通过"),
    ]
    mock_service.list_approval_history.return_value = records
    timeline = ApprovalTimeline(mock_service)
    timeline.load_history("CHG-TEST-001")

    nodes = timeline.findChildren(QFrame, "timelineNode")
    assert len(nodes) == 3
    # 3 条记录 → 2 条连接线（最后一条无连接线）
    connectors = timeline.findChildren(QFrame, "nodeConnector")
    assert len(connectors) == 2


def test_node_shows_status_transition(qapp: QApplication, mock_service: MagicMock) -> None:
    """节点显示 from → to 中文状态流转"""
    mock_service.list_approval_history.return_value = [
        _make_record(from_status="draft", to_status="submitted"),
    ]
    timeline = ApprovalTimeline(mock_service)
    timeline.load_history("CHG-TEST-001")

    transitions = timeline.findChildren(QLabel, "nodeTransition")
    assert len(transitions) == 1
    expected = f"{STATUS_LABELS['draft']} → {STATUS_LABELS['submitted']}"
    assert transitions[0].text() == expected


def test_node_shows_approver_and_comment(qapp: QApplication, mock_service: MagicMock) -> None:
    """节点显示审批人 + 审批意见"""
    mock_service.list_approval_history.return_value = [
        _make_record(approver="reviewer1", comment="审批通过，可实施"),
    ]
    timeline = ApprovalTimeline(mock_service)
    timeline.load_history("CHG-TEST-001")

    metas = timeline.findChildren(QLabel, "nodeMeta")
    assert len(metas) == 1
    assert "reviewer1" in metas[0].text()

    comments = timeline.findChildren(QLabel, "nodeComment")
    assert len(comments) == 1
    assert comments[0].text() == "审批通过，可实施"


def test_node_dot_color_matches_to_status(qapp: QApplication, mock_service: MagicMock) -> None:
    """圆点 stylesheet 包含 to_status 对应的颜色"""
    mock_service.list_approval_history.return_value = [
        _make_record(to_status="approved"),
    ]
    timeline = ApprovalTimeline(mock_service)
    timeline.load_history("CHG-TEST-001")

    dots = timeline.findChildren(QLabel, "nodeDot")
    assert len(dots) == 1
    expected_color = _STATUS_DOT_COLOR["approved"]
    assert expected_color in dots[0].styleSheet()


def test_load_history_without_db_returns_empty(
    qapp: QApplication,
    tmp_path: Path,
) -> None:
    """ChangeService 无 DB 注入时 list_approval_history 返回空列表，widget 不崩溃"""
    # 构造真实 ChangeService（不注入 DB），_repo 为 None
    project_dir = tmp_path / "TEST-2026-001_测试项目"
    project_dir.mkdir()
    (project_dir / ".copier-answers.yml").write_text(
        "project_id: TEST-2026-001\n"
        "project_name: 测试项目\n"
        "version: V1.0.0\n"
        "_src_path: templates/python-tool\n"
        "business_line: SW\n",
        encoding="utf-8",
    )
    svc = ChangeService(str(tmp_path))
    # 无 DB → list_approval_history 返回 []
    assert svc.list_approval_history("CHG-NONEXIST") == []

    timeline = ApprovalTimeline(svc)
    timeline.load_history("CHG-NONEXIST")
    # 应显示空状态提示
    hint = timeline.findChild(QLabel, "emptyHint")
    assert hint is not None
    assert "暂无审批记录" in hint.text()
