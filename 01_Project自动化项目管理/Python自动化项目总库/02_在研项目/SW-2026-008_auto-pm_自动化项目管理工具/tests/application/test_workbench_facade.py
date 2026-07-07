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


# ── list_project_cards 测试 ──────────────────────────────

def test_list_project_cards_empty():
    """空列表时返回 success + []"""
    mock_project_service = MagicMock()
    mock_project_service.list_projects_with_change_count.return_value = []

    facade = WorkbenchFacade(
        dashboard_service=MagicMock(),
        project_service=mock_project_service,
        asset_summary_service=MagicMock(),
    )

    result = facade.list_project_cards()

    assert result.success is True
    assert result.payload == []


def test_list_project_cards_normal():
    """正常列表，验证 ProjectCardDTO 字段映射（含 change_count）"""
    mock_item = MagicMock()
    mock_item.project_id = "SW-2026-001"
    mock_item.name = "Test Project"
    mock_item.stack = "python"
    mock_item.phase = "developing"
    mock_item.version = "0.1.0"
    mock_item.change_count = 3
    mock_item.path = "/tmp/test"
    mock_item.business_line = "SW"

    mock_project_service = MagicMock()
    mock_project_service.list_projects_with_change_count.return_value = [mock_item]

    facade = WorkbenchFacade(
        dashboard_service=MagicMock(),
        project_service=mock_project_service,
        asset_summary_service=MagicMock(),
    )

    result = facade.list_project_cards()

    assert result.success is True
    assert len(result.payload) == 1
    card = result.payload[0]
    assert card.project_id == "SW-2026-001"
    assert card.name == "Test Project"
    assert card.open_change_count == 3
    assert card.health_status == "Unknown"
    assert card.path == "/tmp/test"
    assert card.business_line == "SW"


def test_list_project_cards_service_exception():
    """Service 抛异常时返回 success=False"""
    mock_project_service = MagicMock()
    mock_project_service.list_projects_with_change_count.side_effect = Exception("DB Error")

    facade = WorkbenchFacade(
        dashboard_service=MagicMock(),
        project_service=mock_project_service,
        asset_summary_service=MagicMock(),
    )

    result = facade.list_project_cards()

    assert result.success is False
    assert "DB Error" in result.message


def test_list_project_cards_no_db_fallback():
    """无 DB 时降级为 list_projects() + change_count=0"""
    mock_project = MagicMock()
    mock_project.project_id = "SW-2026-002"
    mock_project.name = "Fallback Project"
    mock_project.stack = "plc"
    mock_project.phase = "production"
    mock_project.version = "1.0.0"
    mock_project.path = "/tmp/fallback"
    mock_project.business_line = "DJ"

    mock_project_service = MagicMock()
    # list_projects_with_change_count 抛 RuntimeError（无 DB）
    mock_project_service.list_projects_with_change_count.side_effect = RuntimeError("未注入 DatabaseManager")
    mock_project_service.list_projects.return_value = [mock_project]

    facade = WorkbenchFacade(
        dashboard_service=MagicMock(),
        project_service=mock_project_service,
        asset_summary_service=MagicMock(),
    )

    result = facade.list_project_cards()

    assert result.success is True
    assert len(result.payload) == 1
    card = result.payload[0]
    assert card.project_id == "SW-2026-002"
    assert card.open_change_count == 0  # 降级时 change_count=0


# ── get_project_workspace 测试 ──────────────────────────────

def test_get_project_workspace_not_found():
    """项目不存在时返回 success=False"""
    mock_project_service = MagicMock()
    mock_project_service.get_project.return_value = None

    facade = WorkbenchFacade(
        dashboard_service=MagicMock(),
        project_service=mock_project_service,
        asset_summary_service=MagicMock(),
    )

    result = facade.get_project_workspace("NOT-EXIST")

    assert result.success is False
    assert "Project not found" in result.message


def test_get_project_workspace_normal():
    """正常项目，验证 summary + asset_summary"""
    mock_project = MagicMock()
    mock_project.project_id = "SW-2026-001"
    mock_project.stack = "plc"
    mock_project.path = "/tmp/plc_project"
    mock_project.project_type = "standard"
    mock_project.model_dump.return_value = {"project_id": "SW-2026-001", "name": "PLC Project"}

    mock_project_service = MagicMock()
    mock_project_service.get_project.return_value = mock_project

    mock_asset_service = MagicMock()
    mock_asset_service.build_summary.return_value = {"status": "healthy", "total_issues": 0}

    facade = WorkbenchFacade(
        dashboard_service=MagicMock(),
        project_service=mock_project_service,
        asset_summary_service=mock_asset_service,
    )

    result = facade.get_project_workspace("SW-2026-001")

    assert result.success is True
    assert result.payload.project_id == "SW-2026-001"
    assert result.payload.asset_summary["status"] == "healthy"
    assert result.payload.document_status is None  # TODO M3/M4
    assert result.payload.pending_actions == []  # TODO M3


def test_get_project_workspace_python_project():
    """Python 项目 asset_summary 为 not_applicable"""
    mock_project = MagicMock()
    mock_project.project_id = "SW-2026-003"
    mock_project.stack = "python"
    mock_project.path = "/tmp/py_project"
    mock_project.project_type = "standard"
    mock_project.model_dump.return_value = {"project_id": "SW-2026-003"}

    mock_project_service = MagicMock()
    mock_project_service.get_project.return_value = mock_project

    mock_asset_service = MagicMock()
    mock_asset_service.build_summary.return_value = {
        "status": "not_applicable",
        "total_issues": 0,
        "issue_messages": ["仅 PLC 项目支持工程资产摘要"],
    }

    facade = WorkbenchFacade(
        dashboard_service=MagicMock(),
        project_service=mock_project_service,
        asset_summary_service=mock_asset_service,
    )

    result = facade.get_project_workspace("SW-2026-003")

    assert result.success is True
    assert result.payload.asset_summary["status"] == "not_applicable"


# ── get_settings_summary 测试 ──────────────────────────────

def test_get_settings_summary_no_db():
    """无 DB 时 db_available=False"""
    mock_project_service = MagicMock()
    mock_project_service.workspace_root = "/tmp/ws"
    mock_project_service.get_db_path.return_value = ""
    mock_project_service.is_cache_available.return_value = False
    mock_project_service.get_project_count.return_value = 0
    mock_project_service.get_last_sync_time.return_value = "—"

    facade = WorkbenchFacade(
        dashboard_service=MagicMock(),
        project_service=mock_project_service,
        asset_summary_service=MagicMock(),
    )

    result = facade.get_settings_summary()

    assert result.success is True
    assert result.payload.db_available is False
    assert result.payload.project_count == 0
    assert result.payload.workspace_root == "/tmp/ws"


def test_get_settings_summary_with_db():
    """有 DB 时返回正确统计 + DTO 字段"""
    mock_project_service = MagicMock()
    mock_project_service.workspace_root = "/tmp/ws"
    mock_project_service.get_db_path.return_value = "/tmp/ws/auto_pm.db"
    mock_project_service.is_cache_available.return_value = True
    mock_project_service.get_project_count.return_value = 5
    mock_project_service.get_last_sync_time.return_value = "2026-07-07 10:00"

    facade = WorkbenchFacade(
        dashboard_service=MagicMock(),
        project_service=mock_project_service,
        asset_summary_service=MagicMock(),
    )

    result = facade.get_settings_summary()

    assert result.success is True
    assert result.payload.db_available is True
    assert result.payload.project_count == 5
    assert "auto_pm.db" in result.payload.db_path
    assert result.payload.last_sync == "2026-07-07 10:00"


def test_get_settings_summary_exception():
    """异常降级"""
    mock_project_service = MagicMock()
    mock_project_service.get_db_path.side_effect = Exception("FS Error")

    facade = WorkbenchFacade(
        dashboard_service=MagicMock(),
        project_service=mock_project_service,
        asset_summary_service=MagicMock(),
    )

    result = facade.get_settings_summary()

    assert result.success is False
    assert "FS Error" in result.message


# ── clear_cache 测试 ──────────────────────────────

def test_clear_cache_no_db():
    """无 DB 时 success=False"""
    mock_project_service = MagicMock()
    mock_project_service.is_cache_available.return_value = False

    facade = WorkbenchFacade(
        dashboard_service=MagicMock(),
        project_service=mock_project_service,
        asset_summary_service=MagicMock(),
    )

    result = facade.clear_cache()

    assert result.success is False
    assert result.payload.success is False
    assert "DB 未初始化" in result.payload.message


def test_clear_cache_success():
    """正常清除后验证 db 重建"""
    mock_project_service = MagicMock()
    mock_project_service.is_cache_available.return_value = True
    mock_project_service.clear_cache.return_value = {
        "success": True,
        "message": "缓存已清除并重新初始化",
    }

    facade = WorkbenchFacade(
        dashboard_service=MagicMock(),
        project_service=mock_project_service,
        asset_summary_service=MagicMock(),
    )

    result = facade.clear_cache()

    assert result.success is True
    assert result.payload.success is True
    assert "缓存已清除" in result.payload.message


# ── rebuild_index 测试 ──────────────────────────────

def test_rebuild_index_no_db():
    """无 DB 时 success=False"""
    mock_project_service = MagicMock()
    mock_project_service.is_cache_available.return_value = False

    facade = WorkbenchFacade(
        dashboard_service=MagicMock(),
        project_service=mock_project_service,
        asset_summary_service=MagicMock(),
    )

    result = facade.rebuild_index()

    assert result.success is False
    assert result.payload.projects_found == 0
    assert result.payload.changes_found == 0


def test_rebuild_index_success():
    """正常重建后验证 projects_found/changes_found"""
    mock_project_service = MagicMock()
    mock_project_service.is_cache_available.return_value = True
    mock_project_service.sync_to_cache.return_value = {
        "projects_found": 3,
        "changes_found": 2,
    }

    facade = WorkbenchFacade(
        dashboard_service=MagicMock(),
        project_service=mock_project_service,
        asset_summary_service=MagicMock(),
    )

    result = facade.rebuild_index()

    assert result.success is True
    assert result.payload.projects_found == 3
    assert result.payload.changes_found == 2
    assert "发现 3 个项目" in result.payload.message
