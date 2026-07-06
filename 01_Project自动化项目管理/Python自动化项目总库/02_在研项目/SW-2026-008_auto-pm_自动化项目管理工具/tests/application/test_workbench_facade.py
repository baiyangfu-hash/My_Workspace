"""Workbench Facade 单元测试"""

from unittest.mock import MagicMock

from auto_pm.application.workbench_facade import WorkbenchFacade


def test_get_dashboard_snapshot_success():
    """验证从 DashboardService 获取的数据能正确映射为 DashboardSnapshotDTO"""
    # Arrange
    mock_dashboard_service = MagicMock()
    
    # 模拟底座的返回
    mock_summary = MagicMock()
    mock_summary.total_projects = 10
    mock_summary.phase_counts = {"developing": 5}
    mock_summary.open_change_count = 3
    mock_summary.failed_check_project_count = 1
    mock_summary.failed_check_project_ids = ["P-001"]
    mock_summary.not_applicable_project_count = 2
    mock_summary.not_applicable_project_ids = ["P-002", "P-003"]
    mock_summary.recent_activities = [{"action": "test"}]
    mock_summary.risk_hints = [{"risk": "high"}]
    mock_dashboard_service.get_summary.return_value = mock_summary
    
    facade = WorkbenchFacade(
        dashboard_service=mock_dashboard_service,
        project_service=MagicMock(),
        asset_summary_service=MagicMock()
    )
    
    # Act
    result = facade.get_dashboard_snapshot()
    
    # Assert
    assert result.success is True
    assert result.payload is not None
    assert result.payload.total_projects == 10
    assert result.payload.phase_counts == {"developing": 5}
    assert result.payload.open_change_count == 3
    assert result.payload.failed_check_project_count == 1
    assert result.payload.not_applicable_project_count == 2
    assert result.payload.recent_activities == [{"action": "test"}]
    assert result.payload.risk_hints == [{"risk": "high"}]

def test_get_dashboard_snapshot_failure():
    """验证服务抛出异常时能被 QueryResult 正确捕获"""
    # Arrange
    mock_dashboard_service = MagicMock()
    mock_dashboard_service.get_summary.side_effect = Exception("DB Connection Error")
    
    facade = WorkbenchFacade(
        dashboard_service=mock_dashboard_service,
        project_service=MagicMock(),
        asset_summary_service=MagicMock()
    )
    
    # Act
    result = facade.get_dashboard_snapshot()
    
    # Assert
    assert result.success is False
    assert result.payload is None
    assert result.message == "DB Connection Error"
    assert "DB Connection Error" in result.errors
