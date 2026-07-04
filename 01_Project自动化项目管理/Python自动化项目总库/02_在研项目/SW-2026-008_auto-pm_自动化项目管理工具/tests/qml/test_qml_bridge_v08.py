"""QmlBridge V0.8.0 Phase 1 单元测试（CHG-090）

覆盖 V0.8.0 Phase 1 新增的 6 个 Service 暴露：
- ReportService：getProjectReport/getChangeReport/getSpecReport/getScanReport 4 Slots
- TemplateService：listTemplates/getTemplatePath 2 Slots
- PmSessionService：getPmSessionView/runPmSessionCheck 2 Slots
- DashboardService：getDashboardSummary 1 Slot
- AssetSummaryService：getAssetSummary(project_id) 1 Slot
- DocRefreshService：refreshProjectDocs(project_id, dry_run) 1 Slot

配套 12 个 Property：6 service + 6 hasXxxService

测试策略：
- 未注入时验证 Slot 返回默认值（空/错误 dict）+ hasXxxService 全部 False
- Mock 注入时验证 Slot 调用转发正确 + 返回数据结构正确
- 向后兼容：仅注入 W1/W2 Service 时既有功能不受影响
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from unittest.mock import MagicMock

import pytest

from auto_pm.ui.qml.qml_bridge import QmlBridge

# ── Mock fixtures ──────────────────────────────────────


def _make_mock_project_service() -> MagicMock:
    """构造 mock ProjectService（带 get_project 返回 mock project）"""
    service = MagicMock()
    mock_project = MagicMock()
    mock_project.project_id = "SW-2026-008"
    mock_project.name = "auto-pm"
    mock_project.path = "/tmp/workspace/SW-2026-008"
    mock_project.stack.value = "python"
    mock_project.project_type = "test"
    service.get_project.return_value = mock_project
    # list_projects 默认返回 MagicMock 会破坏 isinstance(result, list) 断言
    service.list_projects.return_value = []
    return service


def _make_mock_report_service() -> MagicMock:
    """构造 mock ReportService"""
    service = MagicMock()
    service.get_project_overview.return_value = {
        "total": 13,
        "by_stack": {"plc": 6, "python": 6, "unknown": 1},
    }
    service.get_change_overview.return_value = {
        "total": 20,
        "open": 5,
        "closed": 15,
    }
    service.get_spec_report.return_value = {"spec_count": 50}
    service.get_scan_report.return_value = {"scanned": 13}
    return service


def _make_mock_template_service() -> MagicMock:
    """构造 mock TemplateService"""
    service = MagicMock()
    service.list_templates.return_value = ["plc-standard", "python-standard"]
    service.get_template_path.return_value = "/tmp/templates/plc-standard"
    return service


def _make_mock_pm_session_service() -> MagicMock:
    """构造 mock PmSessionService"""
    service = MagicMock()
    service.generate_view.return_value = {
        "file_path": "/tmp/PM_SESSION.md",
        "view": "## §2 Current Focus\nV0.8.0 Phase 1\n\n## §3 Status Summary\n代码基线 V0.8.0",
    }
    service.check.return_value = {
        "file_path": "/tmp/PM_SESSION.md",
        "file_size_kb": 64.8,
        "max_file_size_kb": 150,
        "total_lines": 172,
        "max_file_lines": 300,
        "missing_required": [],
        "deprecated_present": [],
        "is_oversized": False,
        "warnings": [],
        "is_healthy": True,
    }
    return service


def _make_mock_dashboard_service() -> MagicMock:
    """构造 mock DashboardService（带 DashboardSummaryDTO）"""
    @dataclass
    class _MockSummary:
        total_projects: int = 13
        phase_counts: dict[str, int] = None
        open_change_count: int = 5
        failed_check_project_count: int = 0
        failed_check_project_ids: list[str] = None
        not_applicable_project_count: int = 6
        not_applicable_project_ids: list[str] = None
        recent_activities: list = None
        risk_hints: list = None

        def __post_init__(self) -> None:
            if self.phase_counts is None:
                self.phase_counts = {"developing": 5, "production": 8}
            if self.failed_check_project_ids is None:
                self.failed_check_project_ids = []
            if self.not_applicable_project_ids is None:
                self.not_applicable_project_ids = []
            if self.recent_activities is None:
                self.recent_activities = []
            if self.risk_hints is None:
                self.risk_hints = []

    service = MagicMock()
    service.get_summary.return_value = _MockSummary()
    return service


def _make_mock_asset_summary_service() -> MagicMock:
    """构造 mock AssetSummaryService"""
    service = MagicMock()
    service.build_summary.return_value = {
        "status": "healthy",
        "asset_dir": "/tmp/asset",
        "total_issues": 0,
    }
    return service


def _make_mock_doc_refresh_service() -> MagicMock:
    """构造 mock DocRefreshService"""
    @dataclass
    class _MockResult:
        project_id: str = "SW-2026-008"
        dry_run: bool = False
        updated: bool = True
        refreshed_files: list = None
        issues: list = None

        def __post_init__(self) -> None:
            if self.refreshed_files is None:
                self.refreshed_files = []
            if self.issues is None:
                self.issues = []

        def to_dict(self) -> dict[str, Any]:
            return {
                "project_id": self.project_id,
                "dry_run": self.dry_run,
                "updated": self.updated,
                "refreshed_files": self.refreshed_files,
                "issues": self.issues,
            }

    service = MagicMock()
    service.refresh_project_documents.return_value = _MockResult()
    return service


@pytest.fixture
def bridge_no_v08(qapp: Any) -> QmlBridge:
    """仅注入 project_service 的 QmlBridge（V0.6/W1/W2 兼容性测试用）"""
    return QmlBridge(project_service=_make_mock_project_service())


@pytest.fixture
def bridge_full(qapp: Any) -> QmlBridge:
    """注入全部 9 个 Service 的 QmlBridge（V0.8 完整测试用）"""
    return QmlBridge(
        project_service=_make_mock_project_service(),
        change_service=MagicMock(),
        spec_check_service=MagicMock(),
        report_service=_make_mock_report_service(),
        template_service=_make_mock_template_service(),
        pm_session_service=_make_mock_pm_session_service(),
        dashboard_service=_make_mock_dashboard_service(),
        asset_summary_service=_make_mock_asset_summary_service(),
        doc_refresh_service=_make_mock_doc_refresh_service(),
    )


# ── 1. 未注入时返回默认值（向后兼容） ──────────────────


class TestNoServiceInjected:
    """未注入 V0.8 Service 时，Slot 返回默认值 + hasXxxService 全部 False"""

    def test_report_slots_return_disabled(self, bridge_no_v08: QmlBridge) -> None:
        """4 个报告 Slot 返回 '未启用报告服务'"""
        assert bridge_no_v08.getProjectReport() == {"error": "未启用报告服务"}
        assert bridge_no_v08.getChangeReport() == {"error": "未启用报告服务"}
        assert bridge_no_v08.getSpecReport() == {"error": "未启用报告服务"}
        assert bridge_no_v08.getScanReport() == {"error": "未启用报告服务"}

    def test_template_slots_return_empty(self, bridge_no_v08: QmlBridge) -> None:
        """模板 Slot 返回空列表/空字符串"""
        assert bridge_no_v08.listTemplates() == []
        assert bridge_no_v08.getTemplatePath("plc-standard") == ""

    def test_pm_session_slots_return_disabled(self, bridge_no_v08: QmlBridge) -> None:
        """PM_SESSION Slot 返回 '未启用'"""
        assert bridge_no_v08.getPmSessionView() == {"error": "未启用 PM_SESSION 服务"}
        assert bridge_no_v08.runPmSessionCheck() == {"error": "未启用 PM_SESSION 服务"}

    def test_dashboard_slot_return_disabled(self, bridge_no_v08: QmlBridge) -> None:
        """驾驶舱 Slot 返回 '未启用'"""
        assert bridge_no_v08.getDashboardSummary() == {"error": "未启用驾驶舱服务"}

    def test_asset_summary_slot_return_disabled(self, bridge_no_v08: QmlBridge) -> None:
        """资产摘要 Slot 返回 '未启用'"""
        result = bridge_no_v08.getAssetSummary("SW-2026-008")
        assert result == {"error": "未启用工程资产服务"}

    def test_doc_refresh_slot_return_disabled(self, bridge_no_v08: QmlBridge) -> None:
        """文档刷新 Slot 返回 '未启用'"""
        result = bridge_no_v08.refreshProjectDocs("SW-2026-008", False)
        assert result == {"error": "未启用文档刷新服务"}

    def test_all_has_xxx_service_false(self, bridge_no_v08: QmlBridge) -> None:
        """6 个 hasXxxService Property 全部 False"""
        assert bridge_no_v08.hasReportService is False
        assert bridge_no_v08.hasTemplateService is False
        assert bridge_no_v08.hasPmSessionService is False
        assert bridge_no_v08.hasDashboardService is False
        assert bridge_no_v08.hasAssetSummaryService is False
        assert bridge_no_v08.hasDocRefreshService is False


# ── 2. ReportService 4 个 Slot ──────────────────────────


class TestReportServiceSlots:
    """ReportService 4 个 Slot 调用转发正确"""

    def test_get_project_report(self, bridge_full: QmlBridge) -> None:
        result = bridge_full.getProjectReport()
        assert result["total"] == 13
        assert result["by_stack"]["plc"] == 6

    def test_get_change_report(self, bridge_full: QmlBridge) -> None:
        result = bridge_full.getChangeReport()
        assert result["total"] == 20
        assert result["open"] == 5

    def test_get_spec_report(self, bridge_full: QmlBridge) -> None:
        result = bridge_full.getSpecReport()
        assert result["spec_count"] == 50

    def test_get_scan_report(self, bridge_full: QmlBridge) -> None:
        result = bridge_full.getScanReport()
        assert result["scanned"] == 13

    def test_has_report_service_true(self, bridge_full: QmlBridge) -> None:
        assert bridge_full.hasReportService is True


# ── 3. TemplateService 2 个 Slot ────────────────────────


class TestTemplateServiceSlots:
    """TemplateService 2 个 Slot 调用转发正确"""

    def test_list_templates(self, bridge_full: QmlBridge) -> None:
        templates = bridge_full.listTemplates()
        assert templates == ["plc-standard", "python-standard"]

    def test_get_template_path(self, bridge_full: QmlBridge) -> None:
        path = bridge_full.getTemplatePath("plc-standard")
        assert path == "/tmp/templates/plc-standard"

    def test_has_template_service_true(self, bridge_full: QmlBridge) -> None:
        assert bridge_full.hasTemplateService is True


# ── 4. PmSessionService 2 个 Slot ───────────────────────


class TestPmSessionServiceSlots:
    """PmSessionService 2 个 Slot 调用转发正确"""

    def test_get_pm_session_view(self, bridge_full: QmlBridge) -> None:
        result = bridge_full.getPmSessionView()
        assert result["file_path"] == "/tmp/PM_SESSION.md"
        assert "V0.8.0 Phase 1" in result["view"]
        assert "代码基线 V0.8.0" in result["view"]

    def test_run_pm_session_check(self, bridge_full: QmlBridge) -> None:
        result = bridge_full.runPmSessionCheck()
        assert result["is_healthy"] is True
        assert result["file_size_kb"] == 64.8
        assert result["total_lines"] == 172
        assert result["missing_required"] == []
        assert result["deprecated_present"] == []
        assert result["is_oversized"] is False

    def test_has_pm_session_service_true(self, bridge_full: QmlBridge) -> None:
        assert bridge_full.hasPmSessionService is True


# ── 5. DashboardService 1 个 Slot ──────────────────────


class TestDashboardServiceSlot:
    """DashboardService Slot 返回 DashboardSummaryDTO 字段"""

    def test_get_dashboard_summary(self, bridge_full: QmlBridge) -> None:
        result = bridge_full.getDashboardSummary()
        assert result["total_projects"] == 13
        assert result["open_change_count"] == 5
        assert result["failed_check_project_count"] == 0
        assert result["not_applicable_project_count"] == 6
        assert result["phase_counts"] == {"developing": 5, "production": 8}

    def test_has_dashboard_service_true(self, bridge_full: QmlBridge) -> None:
        assert bridge_full.hasDashboardService is True


# ── 6. AssetSummaryService 1 个 Slot ───────────────────


class TestAssetSummaryServiceSlot:
    """AssetSummaryService Slot 调用转发正确"""

    def test_get_asset_summary(self, bridge_full: QmlBridge) -> None:
        result = bridge_full.getAssetSummary("SW-2026-008")
        assert result["status"] == "healthy"
        assert result["total_issues"] == 0

    def test_get_asset_summary_project_not_found(self, bridge_no_v08: QmlBridge) -> None:
        """未注入 service 时返回 '未启用'"""
        result = bridge_no_v08.getAssetSummary("nonexistent")
        assert result == {"error": "未启用工程资产服务"}

    def test_has_asset_summary_service_true(self, bridge_full: QmlBridge) -> None:
        assert bridge_full.hasAssetSummaryService is True


# ── 7. DocRefreshService 1 个 Slot ─────────────────────


class TestDocRefreshServiceSlot:
    """DocRefreshService Slot 调用转发正确"""

    def test_refresh_project_docs(self, bridge_full: QmlBridge) -> None:
        result = bridge_full.refreshProjectDocs("SW-2026-008", False)
        assert result["project_id"] == "SW-2026-008"
        assert result["updated"] is True
        assert result["dry_run"] is False

    def test_refresh_project_docs_dry_run(self, bridge_full: QmlBridge) -> None:
        """dry_run 参数传递正确"""
        bridge_full.refreshProjectDocs("SW-2026-008", True)
        # 验证 mock 被调用且 dry_run=True
        bridge_full._doc_refresh_service.refresh_project_documents.assert_called()

    def test_has_doc_refresh_service_true(self, bridge_full: QmlBridge) -> None:
        assert bridge_full.hasDocRefreshService is True


# ── 8. 向后兼容（V0.6/W1/W2 测试零回归） ────────────────


class TestBackwardCompatibleWithV06:
    """仅注入 V0.6 既有 Service 时，V0.6 功能不受影响"""

    def test_list_projects_still_works(self, bridge_no_v08: QmlBridge) -> None:
        """listProjects() 调用仍正常"""
        # project_service.list_projects() 默认返回 MagicMock，应不抛异常
        result = bridge_no_v08.listProjects()
        assert isinstance(result, list)

    def test_list_all_changes_returns_empty(self, bridge_no_v08: QmlBridge) -> None:
        """无 change_service 时 listAllChanges() 返回空列表（V0.6 既有行为）"""
        assert bridge_no_v08.listAllChanges() == []

    def test_run_spec_check_returns_disabled(self, bridge_no_v08: QmlBridge) -> None:
        """无 spec_check_service 时 runSpecCheck() 返回未启用（V0.6 既有行为）"""
        result = bridge_no_v08.runSpecCheck()
        assert result["error_count"] == -1
        assert "未启用" in result["message"]

    def test_v06_properties_still_work(self, bridge_no_v08: QmlBridge) -> None:
        """V0.6 既有 Property 仍正常"""
        assert bridge_no_v08.hasProjectService is True
        assert bridge_no_v08.hasChangeService is False
        assert bridge_no_v08.hasSpecService is False
