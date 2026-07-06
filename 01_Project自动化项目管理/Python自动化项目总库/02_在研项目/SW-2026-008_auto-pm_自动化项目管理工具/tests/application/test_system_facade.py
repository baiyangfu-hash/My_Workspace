from unittest.mock import MagicMock

from auto_pm.application.system_facade import SystemFacade


def test_system_facade_get_pm_session_view():
    mock_pm = MagicMock()
    mock_pm.generate_view.return_value = {"status": "ok"}
    facade = SystemFacade(pm_session_service=mock_pm)
    
    res = facade.get_pm_session_view()
    assert res.success is True
    assert res.payload is not None
    assert res.payload == {"status": "ok"}

def test_system_facade_run_pm_session_check():
    mock_pm = MagicMock()
    mock_pm.check.return_value = {"errors": 0}
    facade = SystemFacade(pm_session_service=mock_pm)
    
    res = facade.run_pm_session_check()
    assert res.success is True
    assert res.payload is not None
    assert res.payload == {"errors": 0}

def test_system_facade_list_templates():
    mock_tpl = MagicMock()
    mock_tpl.list_templates.return_value = ["tpl1", "tpl2"]
    facade = SystemFacade(pm_session_service=None, template_service=mock_tpl)
    
    res = facade.list_templates()
    assert res.success is True
    assert res.payload is not None
    assert res.payload == ["tpl1", "tpl2"]

def test_system_facade_no_service_returns_false():
    facade = SystemFacade(pm_session_service=None, template_service=None)
    
    assert facade.get_pm_session_view().success is False
    assert facade.run_pm_session_check().success is False
    assert facade.list_templates().success is False
    assert facade.get_template_path("tpl1").success is False
    assert facade.apply_template("proj1", "tpl1").success is False

def test_system_facade_handles_exceptions():
    mock_pm = MagicMock()
    mock_pm.generate_view.side_effect = ValueError("Test error")
    facade = SystemFacade(pm_session_service=mock_pm)
    
    res = facade.get_pm_session_view()
    assert res.success is False
    assert res.message == "Test error"
