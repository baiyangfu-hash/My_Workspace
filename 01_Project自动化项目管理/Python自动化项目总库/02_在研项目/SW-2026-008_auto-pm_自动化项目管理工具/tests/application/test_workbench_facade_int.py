import os
import shutil

import pytest

from auto_pm.application.workbench_facade import WorkbenchFacade
from auto_pm.core.project_service import ProjectService
from auto_pm.db.connection import DatabaseManager


@pytest.fixture
def temp_workspace(tmp_path):
    ws_dir = tmp_path / "workspace"
    ws_dir.mkdir()
    
    # Create a mock project
    proj_dir = ws_dir / "02_在研项目" / "SW-2026-001_Test"
    proj_dir.mkdir(parents=True)
    (proj_dir / ".copier-answers.yml").write_text("project_id: SW-2026-001\nname: Test Project", encoding="utf-8")
    
    yield str(ws_dir)
    shutil.rmtree(ws_dir, ignore_errors=True)

@pytest.fixture
def workbench_facade(temp_workspace):
    db_path = os.path.join(temp_workspace, "auto_pm.db")
    db = DatabaseManager(db_path)
    db.init_schema()
    
    project_service = ProjectService(workspace_root=temp_workspace)
    project_service.inject_db(db)
    
    return WorkbenchFacade(
        dashboard_service=None,
        project_service=project_service,
        asset_summary_service=None,
    )

def test_workbench_facade_rebuild_index_and_stats(workbench_facade):
    # 1. Test rebuild index
    res = workbench_facade.rebuild_index()
    assert res.success is True
    assert res.payload["projects_found"] == 1
    
    # 2. Test get_settings_summary for DB stats
    summary_res = workbench_facade.get_settings_summary()
    assert summary_res.success is True
    payload = summary_res.payload
    assert payload["db_available"] is True
    assert payload["project_count"] == 1
    assert "auto_pm.db" in payload["db_path"]
