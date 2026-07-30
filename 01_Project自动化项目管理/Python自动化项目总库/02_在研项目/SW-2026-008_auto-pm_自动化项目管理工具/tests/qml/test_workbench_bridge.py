"""Workbench Bridge 单元测试

验证 Bridge 的 Slot 方法能正确委托给 Facade 并返回 dict 给 QML。
facade=None 时所有 Slot 应降级返回空值，不抛异常。
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

from auto_pm.ui.contracts.dto.workbench_dto import (
    DashboardSnapshotDTO,
    ProjectCardDTO,
)
from auto_pm.ui.contracts.result import CommandResult, QueryResult
from auto_pm.ui.qml.bridges.workbench_bridge import WorkbenchBridge


def _make_card(project_id="SW-2026-001", name="Test", open_change_count=2) -> Any:  # type: ignore[no-untyped-def]
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


def _make_dashboard_snapshot() -> Any:
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


def test_workbench_bridge_list_projects(qapp) -> None:  # type: ignore[no-untyped-def]
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


def test_workbench_bridge_dashboard_summary(qapp) -> None:  # type: ignore[no-untyped-def]
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


def test_workbench_bridge_no_facade(qapp) -> None:  # type: ignore[no-untyped-def]
    """facade=None 时所有 Slot 降级返回空值，不抛异常"""
    bridge = WorkbenchBridge(facade=None)

    assert bridge.listProjects() == []
    assert bridge.getDashboardSummary() == {}
    assert bridge.getSettingsSummary() == {}
    assert bridge.clearCache() == {"success": False, "message": "未初始化"}
    assert bridge.rebuildIndex() == {"success": False, "message": "未初始化"}
    # CHG-106: getActiveChangeStatus 降级返回空状态机
    active_status = bridge.getActiveChangeStatus("SW-2026-008")
    assert active_status["active"] is False
    assert active_status["state_machine"]["current_node"] == 0


def test_workbench_bridge_active_change_status(qapp) -> None:  # type: ignore[no-untyped-def]
    """Bridge.getActiveChangeStatus() 返回状态机 dict（CHG-106）"""
    mock_facade = MagicMock()
    mock_facade.get_active_change_status.return_value = QueryResult(
        success=True,
        message="Success",
        payload={
            "active": True,
            "change_number": "CHG-SCPT-2026-106",
            "title": "工作台 KPI",
            "status": "implementing",
            "apply_date": "2026-07-09",
            "state_machine": {
                "current_node": 2,
                "current_node_name": "实施中 (Implementing)",
                "progress": 50,
                "nodes": [
                    {"name": "需求澄清 (Draft)", "icon": "pencil-simple", "status": "done"},
                    {"name": "方案评审 (Review)", "icon": "paper-plane-tilt", "status": "done"},
                    {"name": "实施中 (Implementing)", "icon": "code", "status": "active"},
                    {"name": "闭环归档 (Closed)", "icon": "check", "status": "pending"},
                ],
            },
        },
    )

    bridge = WorkbenchBridge(facade=mock_facade)
    result = bridge.getActiveChangeStatus("SW-2026-008")

    assert result["active"] is True
    assert result["change_number"] == "CHG-SCPT-2026-106"
    assert result["state_machine"]["current_node"] == 2
    assert result["state_machine"]["progress"] == 50
    assert len(result["state_machine"]["nodes"]) == 4


def test_workbench_bridge_detect_project(qapp) -> None:  # type: ignore[no-untyped-def]
    """Bridge.detectProject() 通过 Facade.detect_project 检测项目"""
    mock_facade = MagicMock()
    mock_facade.detect_project.return_value = CommandResult(
        success=True,
        message="",
        payload={"project_id": "SW-2026-008", "name": "auto-pm", "stack": "python"},
    )

    bridge = WorkbenchBridge(facade=mock_facade)
    result = bridge.detectProject("/tmp/SW-2026-008")

    assert result["success"] is True
    assert result["project_id"] == "SW-2026-008"
    assert result["name"] == "auto-pm"
    assert result["stack"] == "python"


def test_workbench_bridge_detect_project_not_found(qapp) -> None:  # type: ignore[no-untyped-def]
    """Bridge.detectProject() 路径无效时返回失败"""
    mock_facade = MagicMock()
    mock_facade.detect_project.return_value = CommandResult(
        success=False,
        message="无法在此路径下识别到有效的项目元数据文件",
        payload=None,
    )

    bridge = WorkbenchBridge(facade=mock_facade)
    result = bridge.detectProject("/tmp/not_a_project")

    assert result["success"] is False
    assert "无法" in result["message"]


def test_workbench_bridge_detect_project_no_facade(qapp) -> None:  # type: ignore[no-untyped-def]
    """facade=None 时 detectProject 降级返回失败"""
    bridge = WorkbenchBridge(facade=None)
    result = bridge.detectProject("/tmp/any")

    assert result["success"] is False
    assert result["message"] == "服务未启用"


def test_workbench_bridge_detect_project_error(qapp) -> None:  # type: ignore[no-untyped-def]
    """Bridge.detectProject() Facade 返回错误时降级返回失败"""
    mock_facade = MagicMock()
    mock_facade.detect_project.return_value = CommandResult(
        success=False,
        message="Scanner error",
        payload=None,
    )

    bridge = WorkbenchBridge(facade=mock_facade)
    result = bridge.detectProject("/tmp/error_path")

    assert result["success"] is False
    assert "Scanner error" in result["message"]


# ── editProject / deleteProject 测试（M4 CHG-115 新增） ──


def test_workbench_bridge_edit_project_success(qapp) -> None:  # type: ignore[no-untyped-def]
    """Bridge.editProject() 成功编辑项目元数据"""
    mock_facade = MagicMock()
    mock_facade.edit_project.return_value = CommandResult(
        success=True,
        message="项目元数据已更新: SW-2026-001",
        payload={"project_id": "SW-2026-001", "fields": {"phase": "production"}},
    )

    bridge = WorkbenchBridge(facade=mock_facade)
    result = bridge.editProject("SW-2026-001", {"phase": "production"})

    assert result["success"] is True
    assert "已更新" in result["message"]
    mock_facade.edit_project.assert_called_once_with("SW-2026-001", phase="production")


def test_workbench_bridge_edit_project_not_found(qapp) -> None:  # type: ignore[no-untyped-def]
    """Bridge.editProject() 项目不存在时返回失败"""
    mock_facade = MagicMock()
    mock_facade.edit_project.return_value = CommandResult(
        success=False,
        message="项目不存在: NOT-EXIST",
        payload=None,
    )

    bridge = WorkbenchBridge(facade=mock_facade)
    result = bridge.editProject("NOT-EXIST", {"phase": "developing"})

    assert result["success"] is False
    assert "项目不存在" in result["message"]


def test_workbench_bridge_edit_project_no_facade(qapp) -> None:  # type: ignore[no-untyped-def]
    """facade=None 时 editProject 降级返回未初始化"""
    bridge = WorkbenchBridge(facade=None)
    result = bridge.editProject("SW-2026-001", {"phase": "developing"})

    assert result["success"] is False
    assert result["message"] == "未初始化"


def test_workbench_bridge_delete_project_success(qapp) -> None:  # type: ignore[no-untyped-def]
    """Bridge.deleteProject() 成功删除项目"""
    mock_facade = MagicMock()
    mock_facade.delete_project.return_value = CommandResult(
        success=True,
        message="项目已删除: SW-2026-001",
        payload={"project_id": "SW-2026-001", "name": "Test Project"},
    )

    bridge = WorkbenchBridge(facade=mock_facade)
    result = bridge.deleteProject("SW-2026-001")

    assert result["success"] is True
    assert "已删除" in result["message"]
    mock_facade.delete_project.assert_called_once_with("SW-2026-001")


def test_workbench_bridge_delete_project_not_found(qapp) -> None:  # type: ignore[no-untyped-def]
    """Bridge.deleteProject() 项目不存在时返回失败"""
    mock_facade = MagicMock()
    mock_facade.delete_project.return_value = CommandResult(
        success=False,
        message="项目不存在: NOT-EXIST",
        payload=None,
    )

    bridge = WorkbenchBridge(facade=mock_facade)
    result = bridge.deleteProject("NOT-EXIST")

    assert result["success"] is False
    assert "项目不存在" in result["message"]


def test_workbench_bridge_delete_project_no_facade(qapp) -> None:  # type: ignore[no-untyped-def]
    """facade=None 时 deleteProject 降级返回未初始化"""
    bridge = WorkbenchBridge(facade=None)
    result = bridge.deleteProject("SW-2026-001")

    assert result["success"] is False
    assert result["message"] == "未初始化"


def test_workbench_bridge_initialize_project_pm_success(qapp) -> None:  # type: ignore[no-untyped-def]
    """Bridge.initializeProjectPm() 成功初始化项目 PM 规范"""
    mock_facade = MagicMock()
    mock_facade.initialize_project_pm.return_value = CommandResult(
        success=True,
        message="项目 PM 与变更管理规范初始化成功",
        payload={"success": True, "project_id": "SW-2026-001"},
    )

    bridge = WorkbenchBridge(facade=mock_facade)
    result = bridge.initializeProjectPm("SW-2026-001")

    assert result["success"] is True
    assert "初始化成功" in result["message"]
    mock_facade.initialize_project_pm.assert_called_once_with("SW-2026-001")


def test_workbench_bridge_initialize_project_pm_no_facade(qapp) -> None:  # type: ignore[no-untyped-def]
    """facade=None 时 initializeProjectPm 降级返回未初始化"""
    bridge = WorkbenchBridge(facade=None)
    result = bridge.initializeProjectPm("SW-2026-001")

    assert result["success"] is False
    assert result["message"] == "未初始化"


def test_workbench_bridge_save_workspace_root_observable_states(qapp) -> None:  # type: ignore[no-untyped-def]
    """saveWorkspaceRoot() 透传配置保存/运行态重载双状态。"""
    mock_facade = MagicMock()
    mock_facade.save_workspace_root.return_value = CommandResult(
        success=False,
        message="配置已保存，但运行态重载失败: reload error",
        payload={
            "config_saved": True,
            "runtime_reloaded": False,
            "workspace_root": "D:/workspace",
            "reload_message": "reload error",
        },
    )

    bridge = WorkbenchBridge(facade=mock_facade)
    result = bridge.saveWorkspaceRoot("D:/workspace")

    assert result["success"] is False
    assert result["config_saved"] is True
    assert result["runtime_reloaded"] is False
    assert result["workspace_root"] == "D:/workspace"
    assert result["reload_message"] == "reload error"
