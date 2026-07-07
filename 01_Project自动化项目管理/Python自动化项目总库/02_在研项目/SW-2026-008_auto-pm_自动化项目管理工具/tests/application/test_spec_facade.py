"""SpecFacade 单元测试

覆盖 SpecFacade 的 3 个方法：
- run_spec_check
- get_spec_center_overview
- list_spec_center_entries
"""

from types import SimpleNamespace
from typing import Any

from auto_pm.application.spec_facade import SpecFacade
from auto_pm.ui.contracts.dto.spec_dto import (
    SpecCenterEntryDTO,
    SpecCenterOverviewDTO,
    SpecCheckResultDTO,
)

# ── mock helpers ──────────────────────────────────────


def _make_check_output(**overrides: Any) -> SimpleNamespace:
    """构造 spec check 输出 mock（含 error_count/warning_count/info_count/exit_code/results）"""
    severity = overrides.get("severity", SimpleNamespace(name="ERROR"))
    result = SimpleNamespace(
        check_id=overrides.get("check_id", "CHK-001"),
        severity=severity,
        message=overrides.get("message", "sample message"),
        details=overrides.get("details", {"key": "value"}),
        fix_suggestion=overrides.get("fix_suggestion", "suggestion"),
    )
    return SimpleNamespace(
        error_count=overrides.get("error_count", 1),
        warning_count=overrides.get("warning_count", 2),
        info_count=overrides.get("info_count", 3),
        exit_code=overrides.get("exit_code", 1),
        results=overrides.get("results", [result]),
    )


def _make_overview(**overrides: Any) -> SimpleNamespace:
    """构造 spec center overview mock（含 spec_count/domain_counts/lifecycle_counts/health_summary）"""
    health = SimpleNamespace(
        error_count=overrides.get("health_error_count", 0),
        warning_count=overrides.get("health_warning_count", 1),
        info_count=overrides.get("health_info_count", 2),
        exit_code=overrides.get("health_exit_code", 0),
    )
    return SimpleNamespace(
        spec_count=overrides.get("spec_count", 10),
        domain_counts=overrides.get("domain_counts", {"PLC": 5, "Python": 5}),
        lifecycle_counts=overrides.get("lifecycle_counts", {"active": 8, "draft": 2}),
        health_summary=health,
    )


def _make_entry(**overrides: Any) -> SimpleNamespace:
    """构造 spec center entry mock（含 spec_id/title/number/domain/lifecycle/canonical_path/version/file_exists）"""
    return SimpleNamespace(
        spec_id=overrides.get("spec_id", "SW-2026-001"),
        title=overrides.get("title", "Sample Spec"),
        number=overrides.get("number", "001"),
        domain=overrides.get("domain", "PLC"),
        lifecycle=overrides.get("lifecycle", "active"),
        canonical_path=overrides.get("canonical_path", "/specs/sample.md"),
        version=overrides.get("version", "1.0.0"),
        file_exists=overrides.get("file_exists", True),
    )


def _raise(exc: Exception):
    """返回一个调用即抛出指定异常的函数（兼容任意参数签名）"""

    def _fn(*_args, **_kwargs):
        raise exc

    return _fn


# ── run_spec_check 测试 ──────────────────────────────────────


def test_run_spec_check_success():
    """正常调用返回 SpecCheckResultDTO 且字段正确"""
    output = _make_check_output()
    service = SimpleNamespace(run=lambda: output)
    facade = SpecFacade(spec_check_service=service)

    result = facade.run_spec_check()

    assert result.success is True
    assert isinstance(result.payload, SpecCheckResultDTO)
    assert result.payload.error_count == 1
    assert result.payload.warning_count == 2
    assert result.payload.info_count == 3
    assert result.payload.exit_code == 1
    assert len(result.payload.results) == 1
    item = result.payload.results[0]
    assert item["check_id"] == "CHK-001"
    assert item["severity"] == "ERROR"
    assert item["message"] == "sample message"
    assert item["details"] == {"key": "value"}
    assert item["fix_suggestion"] == "suggestion"


def test_run_spec_check_no_service():
    """spec_check_service=None 时返回 success=False + payload=None"""
    facade = SpecFacade(spec_check_service=None)

    result = facade.run_spec_check()

    assert result.success is False
    assert result.payload is None
    assert "No spec_check_service" in result.message


def test_run_spec_check_exception():
    """service.run() 抛异常时返回 success=False + payload=None"""
    service = SimpleNamespace(run=_raise(Exception("check boom")))
    facade = SpecFacade(spec_check_service=service)

    result = facade.run_spec_check()

    assert result.success is False
    assert result.payload is None
    assert "check boom" in result.message


# ── get_spec_center_overview 测试 ────────────────────────────


def test_get_spec_center_overview_success():
    """正常调用返回 SpecCenterOverviewDTO 且字段正确"""
    overview = _make_overview()
    service = SimpleNamespace(get_overview=lambda: overview)
    facade = SpecFacade(spec_center_service=service)

    result = facade.get_spec_center_overview()

    assert result.success is True
    assert isinstance(result.payload, SpecCenterOverviewDTO)
    assert result.payload.spec_count == 10
    assert result.payload.domain_counts == {"PLC": 5, "Python": 5}
    assert result.payload.lifecycle_counts == {"active": 8, "draft": 2}
    assert result.payload.health_summary == {
        "error_count": 0,
        "warning_count": 1,
        "info_count": 2,
        "exit_code": 0,
    }


def test_get_spec_center_overview_no_service():
    """spec_center_service=None 时返回 success=False + payload=None"""
    facade = SpecFacade(spec_center_service=None)

    result = facade.get_spec_center_overview()

    assert result.success is False
    assert result.payload is None
    assert "No spec_center_service" in result.message


def test_get_spec_center_overview_exception():
    """service.get_overview() 抛异常时返回 success=False + payload=None"""
    service = SimpleNamespace(get_overview=_raise(Exception("overview boom")))
    facade = SpecFacade(spec_center_service=service)

    result = facade.get_spec_center_overview()

    assert result.success is False
    assert result.payload is None
    assert "overview boom" in result.message


# ── list_spec_center_entries 测试 ────────────────────────────


def test_list_spec_center_entries_success():
    """正常调用返回 list[SpecCenterEntryDTO] 且字段正确"""
    entries = [
        _make_entry(spec_id="SW-001"),
        _make_entry(spec_id="SW-002", file_exists=False, domain="Python"),
    ]
    service = SimpleNamespace(list_entries=lambda filter_domain=None: entries)
    facade = SpecFacade(spec_center_service=service)

    result = facade.list_spec_center_entries()

    assert result.success is True
    assert isinstance(result.payload, list)
    assert len(result.payload) == 2
    assert all(isinstance(item, SpecCenterEntryDTO) for item in result.payload)
    assert result.payload[0].spec_id == "SW-001"
    assert result.payload[0].title == "Sample Spec"
    assert result.payload[0].number == "001"
    assert result.payload[0].domain == "PLC"
    assert result.payload[0].lifecycle == "active"
    assert result.payload[0].canonical_path == "/specs/sample.md"
    assert result.payload[0].version == "1.0.0"
    assert result.payload[0].file_exists is True
    assert result.payload[1].spec_id == "SW-002"
    assert result.payload[1].file_exists is False
    assert result.payload[1].domain == "Python"


def test_list_spec_center_entries_with_filter():
    """带 filter_domain 参数调用，验证 filter_domain 透传给 service.list_entries()"""
    captured: dict = {}

    def _list_entries(filter_domain=None):
        captured["filter_domain"] = filter_domain
        return [_make_entry(domain="PLC")]

    service = SimpleNamespace(list_entries=_list_entries)
    facade = SpecFacade(spec_center_service=service)

    result = facade.list_spec_center_entries(filter_domain="PLC")

    assert result.success is True
    assert captured["filter_domain"] == "PLC"
    assert isinstance(result.payload, list)
    assert len(result.payload) == 1
    assert isinstance(result.payload[0], SpecCenterEntryDTO)
    assert result.payload[0].domain == "PLC"


def test_list_spec_center_entries_no_service():
    """spec_center_service=None 时返回 success=False + payload=[]"""
    facade = SpecFacade(spec_center_service=None)

    result = facade.list_spec_center_entries()

    assert result.success is False
    assert result.payload == []
    assert "No spec_center_service" in result.message


def test_list_spec_center_entries_exception():
    """service.list_entries() 抛异常时返回 success=False + payload=[]"""
    service = SimpleNamespace(list_entries=_raise(Exception("entries boom")))
    facade = SpecFacade(spec_center_service=service)

    result = facade.list_spec_center_entries()

    assert result.success is False
    assert result.payload == []
    assert "entries boom" in result.message
