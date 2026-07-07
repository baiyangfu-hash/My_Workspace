"""Workbench Bridge 单元测试

验证 Bridge 的 Slot 方法能正确委托给 Facade 并返回 dict 给 QML。
facade=None 时所有 Slot 应降级返回空值，不抛异常。
"""

from unittest.mock import MagicMock

from auto_pm.ui.contracts.dto.workbench_dto import (
    DashboardSnapshotDTO,
    ProjectCardDTO,
)
from auto_pm.ui.contracts.result import QueryResult
from auto_pm.ui.qml.bridges.workbench_bridge import WorkbenchBridge


def _make_card(project_id="SW-2026-001", name="Test", open_change_count=2):
    return ProjectCardDTO(
        project_id=project_id,
        name=name,
        stack="python",
        phase="developing",
        version="0.1.0",
        health_status="Unknown",
        open_change_count=open_change_count,
        last_activity_at=None,
        path="/tmp/test",
        business_line="SW",
    )


def _make_dashboard_snapshot():
    return DashboardSnapshotDTO(
        total_projects=5,
        phase_counts={"developing": 3},
        open_change_count=2,
        failed_check_project_count=1,
        not_applicable_project_count=0,
        recent_activities=[],
        risk_hints=[],
        failed_check_project_ids=["P-001"],
        not_applicable_project_ids=[],
    )


def test_workbench_bridge_list_projects(qapp):
    """Bridge.listProjects() 返回 list[dict]"""
    mock_facade = MagicMock()
    mock_facade.list_project_cards.return_value = QueryResult(
        success=True, message="Success", payload=[_make_card()]
    )

    bridge = WorkbenchBridge(facade=mock_facade)
    result = bridge.listProjects()

    assert len(result) == 1
    assert result[0]["project_id"] == "SW-2026-001"
    assert result[0]["open_change_count"] == 2


def test_workbench_bridge_dashboard_summary(qapp):
    """Bridge.getDashboardSummary() 返回 dict"""
    mock_facade = MagicMock()
    mock_facade.get_dashboard_snapshot.return_value = QueryResult(
        success=True, message="Success", payload=_make_dashboard_snapshot()
    )

    bridge = WorkbenchBridge(facade=mock_facade)
    result = bridge.getDashboardSummary()

    assert result["total_projects"] == 5
    assert result["open_change_count"] == 2
    assert result["failed_check_project_ids"] == ["P-001"]


def test_workbench_bridge_no_facade(qapp):
    """facade=None 时所有 Slot 降级返回空值，不抛异常"""
    bridge = WorkbenchBridge(facade=None)

    assert bridge.listProjects() == []
    assert bridge.getDashboardSummary() == {}
    assert bridge.getSettingsSummary() == {}
    assert bridge.clearCache() == {"success": False, "message": "未初始化"}
    assert bridge.rebuildIndex() == {"success": False, "message": "未初始化"}
