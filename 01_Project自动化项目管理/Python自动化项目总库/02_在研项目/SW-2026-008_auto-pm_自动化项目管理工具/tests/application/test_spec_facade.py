from unittest.mock import MagicMock

from auto_pm.application.spec_facade import SpecFacade


def test_spec_facade_run_spec_check():
    mock_service = MagicMock()
    mock_output = MagicMock()
    mock_output.error_count = 0
    mock_output.warning_count = 1
    mock_output.info_count = 2
    mock_output.exit_code = 0
    mock_output.results = []
    mock_service.run.return_value = mock_output
    
    facade = SpecFacade(spec_check_service=mock_service)
    res = facade.run_spec_check()
    
    assert res.success is True
    assert res.payload is not None
    assert res.payload["error_count"] == 0

def test_spec_facade_get_overview():
    mock_center = MagicMock()
    mock_overview = MagicMock()
    mock_overview.spec_count = 10
    mock_overview.domain_counts = {"PLC": 5}
    mock_overview.lifecycle_counts = {"active": 10}
    mock_overview.health_summary.error_count = 0
    mock_overview.health_summary.warning_count = 0
    mock_overview.health_summary.info_count = 0
    mock_overview.health_summary.exit_code = 0
    
    mock_center.get_overview.return_value = mock_overview
    
    facade = SpecFacade(spec_center_service=mock_center)
    res = facade.get_spec_center_overview()
    
    assert res.success is True
    assert res.payload is not None
    assert res.payload["spec_count"] == 10

def test_spec_facade_no_service():
    facade = SpecFacade(spec_check_service=None, spec_center_service=None)
    
    assert facade.run_spec_check().success is False
    assert facade.get_spec_center_overview().success is False
    assert facade.list_spec_center_entries().success is False
