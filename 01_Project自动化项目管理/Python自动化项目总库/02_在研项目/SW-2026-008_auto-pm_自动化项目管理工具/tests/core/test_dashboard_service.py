"""DashboardService 单元测试

验证 Week 1 首页驾驶舱摘要数据：
- 项目总数
- 阶段分布
- 未关闭变更数
- PLC 检查失败项目数
"""

from __future__ import annotations

from pathlib import Path

import pytest

from auto_pm.change.change_service import ChangeService
from auto_pm.core.dashboard_service import DashboardService
from auto_pm.core.project_service import ProjectService
from auto_pm.db.connection import DatabaseManager
from auto_pm.db.repository import ChangeRequestRepository
from auto_pm.models import ChangeSummary, ProjectRecord


class _FakeCheckResult:
    def __init__(self, fail_count: int) -> None:
        self.fail_count = fail_count


class _FakePlcService:
    def __init__(self, fail_counts: dict[str, int] | None = None) -> None:
        self._fail_counts = fail_counts or {}

    def check(self, project_path: str) -> _FakeCheckResult:
        return _FakeCheckResult(self._fail_counts.get(project_path, 0))


@pytest.fixture
def db(tmp_path: Path) -> DatabaseManager:
    d = DatabaseManager(str(tmp_path))
    d.init_schema()
    return d


@pytest.fixture
def project_service(tmp_path: Path, db: DatabaseManager) -> ProjectService:
    return ProjectService(str(tmp_path), db=db)


@pytest.fixture
def change_service(tmp_path: Path, db: DatabaseManager) -> ChangeService:
    return ChangeService(str(tmp_path), db=db)


def _make_project_record(
    project_id: str,
    name: str = "",
    stack: str = "plc",
    phase: str = "developing",
    business_line: str = "",
    file_mtime: float = 1000.0,
) -> ProjectRecord:
    return ProjectRecord(
        project_id=project_id,
        name=name or project_id,
        path=f"/tmp/{project_id}",
        stack=stack,
        version="V1.0.0",
        description="",
        source="copier",
        phase=phase,
        business_line=business_line,
        extra={},
        file_mtime=file_mtime,
        last_scanned="2026-01-01",
    )


def _make_change_summary(
    change_number: str,
    project_id: str = "SW-2026-001",
    status: str = "draft",
    apply_date: str = "2026-01-01",
) -> ChangeSummary:
    return ChangeSummary(
        change_number=change_number,
        project_id=project_id,
        project_name=project_id,
        domain="PLC",
        business_nature="REQ",
        impact_scope=["LOCAL"],
        status=status,
        applicant="张三",
        apply_date=apply_date,
        title="测试变更",
    )


class TestDashboardService:
    def test_get_summary_empty_data(
        self, project_service: ProjectService, change_service: ChangeService
    ) -> None:
        service = DashboardService(project_service, change_service)

        result = service.get_summary()

        assert result.total_projects == 0
        assert result.phase_counts == {
            "developing": 0,
            "commissioning": 0,
            "production": 0,
            "archived": 0,
        }
        assert result.open_change_count == 0
        assert result.failed_check_project_count == 0
        assert result.recent_activities == []
        assert result.risk_hints == ["当前未发现高优先级风险"]

    def test_get_summary_with_projects_changes_and_failed_checks(
        self,
        project_service: ProjectService,
        change_service: ChangeService,
        db: DatabaseManager,
    ) -> None:
        projects = [
            _make_project_record("DJ-2026-001", "PLC单机A", "plc", "developing", "DJ", file_mtime=1751000000.0),
            _make_project_record("DJ-2026-002", "PLC单机B", "plc", "commissioning", "DJ", file_mtime=1750900000.0),
            _make_project_record("SW-2026-003", "软件A", "python", "developing", "SW", file_mtime=1782535000.0),
            _make_project_record("SW-2026-004", "软件B", "python", "archived", "SW", file_mtime=1750800000.0),
        ]
        for record in projects:
            project_service._repo.upsert(record)

        change_repo = ChangeRequestRepository(db)
        change_repo.upsert(
            _make_change_summary(
                "CHG-PLC-2026-001",
                project_id="DJ-2026-001",
                status="draft",
                apply_date="2026-06-25",
            )
        )
        change_repo.upsert(
            _make_change_summary(
                "CHG-PLC-2026-002",
                project_id="DJ-2026-001",
                status="implementing",
                apply_date="2026-06-27",
            )
        )
        change_repo.upsert(
            _make_change_summary(
                "CHG-PLC-2026-003",
                project_id="DJ-2026-002",
                status="closed",
                apply_date="2026-06-20",
            )
        )

        fake_plc_service = _FakePlcService(
            {
                "/tmp/DJ-2026-001": 2,
                "/tmp/DJ-2026-002": 0,
            }
        )
        service = DashboardService(project_service, change_service, plc_service=fake_plc_service)

        result = service.get_summary()

        assert result.total_projects == 4
        assert result.phase_counts["developing"] == 2
        assert result.phase_counts["commissioning"] == 1
        assert result.phase_counts["archived"] == 1
        assert result.open_change_count == 2
        assert result.failed_check_project_count == 1
        assert result.failed_check_project_ids == ["DJ-2026-001"]
        assert len(result.recent_activities) == 4
        assert result.recent_activities[0].startswith("[项目] SW-2026-003")
        assert any("CHG-PLC-2026-002" in item for item in result.recent_activities)
        assert result.risk_hints[0] == "存在 2 条未关闭变更，建议优先清理实施中和待验收项"
        assert result.risk_hints[1] == "PLC 检查失败项目: DJ-2026-001"
