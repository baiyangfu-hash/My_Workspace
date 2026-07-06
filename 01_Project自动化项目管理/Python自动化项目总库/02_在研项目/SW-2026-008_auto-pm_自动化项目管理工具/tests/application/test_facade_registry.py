"""Facade Registry 单元测试"""

from unittest.mock import MagicMock

from auto_pm.ui.registry import FacadeRegistry


def test_registry_initialization():
    """验证 FacadeRegistry 能成功装配 5 个 Facades 且无循环依赖报错"""
    # Arrange
    registry = FacadeRegistry()
    
    mock_services = {
        "dashboard_service": MagicMock(),
        "project_service": MagicMock(),
        "asset_summary_service": MagicMock(),
        "change_service": MagicMock(),
        "spec_check_service": MagicMock(),
        "spec_center_service": MagicMock(),
        "doc_refresh_service": MagicMock(),
        "report_service": MagicMock(),
        "pm_session_service": MagicMock(),
    }
    
    # Act
    registry.initialize(mock_services)
    
    # Assert
    assert registry.workbench_facade is not None
    assert registry.change_facade is not None
    assert registry.spec_facade is not None
    assert registry.delivery_facade is not None
    assert registry.system_facade is not None
    
    # 验证底层服务正确注入
    assert registry.workbench_facade._dashboard_service == mock_services["dashboard_service"]
    assert registry.change_facade._change_service == mock_services["change_service"]
    assert registry.spec_facade._spec_check_service == mock_services["spec_check_service"]
    assert registry.delivery_facade._doc_refresh_service == mock_services["doc_refresh_service"]
    assert registry.system_facade._pm_session_service == mock_services["pm_session_service"]
