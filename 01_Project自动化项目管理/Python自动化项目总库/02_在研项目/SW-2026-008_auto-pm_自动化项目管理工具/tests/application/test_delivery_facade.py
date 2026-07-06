from unittest.mock import MagicMock

from auto_pm.application.delivery_facade import DeliveryFacade


def test_delivery_facade_refresh_project_docs():
    mock_refresh = MagicMock()
    mock_refresh.refresh_project_documents.return_value = {"refreshed": True}
    
    facade = DeliveryFacade(doc_refresh_service=mock_refresh)
    res = facade.refresh_project_docs("PROJ-001")
    
    assert res.success is True
    assert res.payload is not None
    assert res.payload == {"refreshed": True}
    mock_refresh.refresh_project_documents.assert_called_with("PROJ-001", dry_run=False)

def test_delivery_facade_get_reports():
    mock_report = MagicMock()
    mock_report.get_project_overview.return_value = {"projects": 5}
    mock_report.get_change_overview.return_value = {"changes": 10}
    mock_report.get_spec_report.return_value = {"specs": 2}
    mock_report.get_scan_report.return_value = {"scans": 1}
    
    facade = DeliveryFacade(report_service=mock_report)
    
    pr = facade.get_project_report()
    assert pr.success is True and pr.payload is not None
    assert pr.payload == {"projects": 5}
    
    cr = facade.get_change_report()
    assert cr.success is True and cr.payload is not None
    assert cr.payload == {"changes": 10}
    
    sr = facade.get_spec_report()
    assert sr.success is True and sr.payload is not None
    assert sr.payload == {"specs": 2}
    
    scr = facade.get_scan_report()
    assert scr.success is True and scr.payload is not None
    assert scr.payload == {"scans": 1}

def test_delivery_facade_asset_summary():
    mock_asset = MagicMock()
    mock_asset.refresh_all.return_value = {"refreshed": True}
    mock_asset.get_summary.return_value = {"assets": 100}
    
    facade = DeliveryFacade(asset_summary_service=mock_asset)
    
    ras = facade.refresh_asset_summary()
    assert ras.success is True and ras.payload is not None
    assert ras.payload == {"refreshed": True}
    
    gas = facade.get_asset_summary()
    assert gas.success is True and gas.payload is not None
    assert gas.payload == {"assets": 100}

def test_delivery_facade_no_services():
    facade = DeliveryFacade()
    
    assert facade.refresh_project_docs("PROJ").success is False
    assert facade.get_project_report().success is False
    assert facade.get_change_report().success is False
    assert facade.get_spec_report().success is False
    assert facade.get_scan_report().success is False
    assert facade.refresh_asset_summary().success is False
    assert facade.get_asset_summary().success is False
