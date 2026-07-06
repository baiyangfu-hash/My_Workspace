from unittest.mock import MagicMock

import pytest

from auto_pm.application.change_facade import ChangeFacade
from auto_pm.change.change_service import ChangeService
from auto_pm.ui.contracts.commands.change_commands import (
    CreateChangeCommand,
)


@pytest.fixture
def mock_change_service():
    return MagicMock(spec=ChangeService)

@pytest.fixture
def change_facade(mock_change_service):
    return ChangeFacade(mock_change_service)

def test_list_change_requests(change_facade, mock_change_service):
    mock_summary = MagicMock()
    mock_summary.change_number = "CHG-123"
    mock_summary.project_id = "PRJ-123"
    mock_summary.project_name = "Project 123"
    mock_summary.domain = "ELEC"
    mock_summary.business_nature = "DEF"
    mock_summary.impact_scope = []
    mock_summary.status = "draft"
    mock_summary.applicant = "user"
    mock_summary.apply_date = "2026-07-06"
    mock_summary.title = "Title"
    mock_summary.urgency = "normal"
    
    mock_change_service.list_all_changes.return_value = [mock_summary]
    
    result = change_facade.list_change_requests()
    assert result.success is True
    assert len(result.payload) == 1
    assert result.payload[0].change_number == "CHG-123"

def test_get_change_detail(change_facade, mock_change_service):
    mock_request = MagicMock()
    mock_request.change_number = "CHG-123"
    mock_request.project_id = "PRJ-123"
    mock_request.project_name = "Project 123"
    mock_request.domain = "ELEC"
    mock_request.business_nature = "DEF"
    mock_request.impact_scope = []
    mock_request.status = "draft"
    mock_request.applicant = "user"
    mock_request.apply_date = "2026-07-06"
    mock_request.planned_date = "2026-07-07"
    mock_request.urgency = "normal"
    
    mock_change_service.get_change_request.return_value = mock_request
    
    result = change_facade.get_change_detail("CHG-123")
    assert result.success is True
    assert result.payload.change_number == "CHG-123"

def test_create_change_request(change_facade, mock_change_service):
    cmd = CreateChangeCommand(
        project_id="PRJ-123",
        title="Test Title",
        domain="ELEC",
        nature="DEF",
        background="bg",
        necessity="nec",
        applicant="user"
    )
    
    mock_cr = MagicMock()
    mock_cr.change_number = "CHG-123"
    mock_cr.project_id = "PRJ-123"
    mock_cr.project_name = "Project 123"
    mock_cr.domain = "ELEC"
    mock_cr.business_nature = "DEF"
    mock_cr.impact_scope = []
    mock_cr.status = "draft"
    mock_cr.applicant = "user"
    mock_cr.apply_date = "2026-07-06"
    mock_cr.urgency = "normal"
    
    mock_change_service.create_change_request.return_value = mock_cr
    
    result = change_facade.create_change_request(cmd)
    assert result.success is True
    assert result.payload.change_number == "CHG-123"
    mock_change_service.create_change_request.assert_called_once()
