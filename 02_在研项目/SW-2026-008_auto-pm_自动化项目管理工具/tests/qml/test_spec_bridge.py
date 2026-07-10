"""SpecBridge 单元测试（M4 第 1 批新增）

约束（与 tests/qml/conftest.py 一致）：
- qapp fixture 引用 tests/conftest.py 的 session 级 QApplication
- 不重新定义 qapp
- 全部用 Mock Facade，无文件系统/DB 依赖
- mock facade 用自定义 Mock 类（不使用 MagicMock），便于追踪调用参数

覆盖 SpecBridge 的 3 个 Slot：
- runSpecCheck() → dict + emit specCheckCompleted 信号
- getSpecOverview() → dict
- listSpecEntries(filter_domain) → list[dict]
"""

from auto_pm.ui.contracts.dto.spec_dto import (
    SpecCenterEntryDTO,
    SpecCenterOverviewDTO,
    SpecCheckResultDTO,
)
from auto_pm.ui.contracts.result import CommandResult, QueryResult


class _MockSpecFacade:
    """Mock SpecFacade，记录方法调用并返回预设结果。

    用自定义类替代 MagicMock，便于显式追踪 list_spec_center_entries
    的调用参数（filter_domain 透传验证）。
    """

    def __init__(
        self,
        run_check_result=None,
        overview_result=None,
        list_entries_result=None,
    ) -> None:
        self._run_check_result = run_check_result
        self._overview_result = overview_result
        self._list_entries_result = list_entries_result
        self.list_entries_calls: list[str | None] = []

    def run_spec_check(self):
        return self._run_check_result

    def get_spec_center_overview(self):
        return self._overview_result

    def list_spec_center_entries(self, filter_domain=None):
        self.list_entries_calls.append(filter_domain)
        return self._list_entries_result


def _make_check_result_dto(**overrides):
    return SpecCheckResultDTO(
        error_count=overrides.get("error_count", 2),
        warning_count=overrides.get("warning_count", 3),
        info_count=overrides.get("info_count", 1),
        exit_code=overrides.get("exit_code", 0),
        results=overrides.get("results", []),
    )


def _make_overview_dto(**overrides):
    return SpecCenterOverviewDTO(
        spec_count=overrides.get("spec_count", 10),
        domain_counts=overrides.get("domain_counts", {"plc": 6, "python": 4}),
        lifecycle_counts=overrides.get("lifecycle_counts", {"draft": 2, "active": 8}),
        health_summary=overrides.get(
            "health_summary",
            {
                "error_count": 2,
                "warning_count": 3,
                "info_count": 1,
                "exit_code": 0,
            },
        ),
    )


def _make_entry_dto(**overrides):
    return SpecCenterEntryDTO(
        spec_id=overrides.get("spec_id", "SW-2026-006"),
        title=overrides.get("title", "SpecMgr 规范管理"),
        number=overrides.get("number", "006"),
        domain=overrides.get("domain", "python"),
        lifecycle=overrides.get("lifecycle", "active"),
        canonical_path=overrides.get("canonical_path", "/specs/SW-2026-006.md"),
        version=overrides.get("version", "1.0.0"),
        file_exists=overrides.get("file_exists", True),
    )


def test_spec_bridge_run_check(qapp):
    """runSpecCheck() 返回 dict + emit specCheckCompleted 信号"""
    from PySide6.QtTest import QSignalSpy

    from auto_pm.ui.qml.bridges.spec_bridge import SpecBridge

    dto = _make_check_result_dto(error_count=2, warning_count=3, info_count=1)
    mock_facade = _MockSpecFacade(
        run_check_result=CommandResult(success=True, message="OK", payload=dto)
    )
    bridge = SpecBridge(facade=mock_facade)

    spy = QSignalSpy(bridge.specCheckCompleted)
    result = bridge.runSpecCheck()

    # 返回 dict（asdict 转换），字段与 DTO 一致
    assert isinstance(result, dict)
    assert result["error_count"] == 2
    assert result["warning_count"] == 3
    assert result["info_count"] == 1
    assert result["exit_code"] == 0
    assert result["results"] == []
    # 信号 emit 一次，参数为 (error_count, warning_count, info_count)
    assert spy.count() == 1
    args = spy.at(0)
    assert int(args[0]) == 2
    assert int(args[1]) == 3
    assert int(args[2]) == 1


def test_spec_bridge_get_overview(qapp):
    """getSpecOverview() 返回 dict"""
    from auto_pm.ui.qml.bridges.spec_bridge import SpecBridge

    dto = _make_overview_dto(spec_count=10)
    mock_facade = _MockSpecFacade(
        overview_result=QueryResult(success=True, message="OK", payload=dto)
    )
    bridge = SpecBridge(facade=mock_facade)
    result = bridge.getSpecOverview()

    assert isinstance(result, dict)
    assert result["spec_count"] == 10
    assert result["domain_counts"] == {"plc": 6, "python": 4}
    assert result["lifecycle_counts"] == {"draft": 2, "active": 8}
    assert result["health_summary"]["error_count"] == 2
    assert result["health_summary"]["exit_code"] == 0


def test_spec_bridge_list_entries(qapp):
    """listSpecEntries() 返回 list[dict]"""
    from auto_pm.ui.qml.bridges.spec_bridge import SpecBridge

    entries = [
        _make_entry_dto(spec_id="SW-2026-006", domain="python"),
        _make_entry_dto(
            spec_id="SW-2026-008", domain="python", title="auto-pm 项目管理"
        ),
    ]
    mock_facade = _MockSpecFacade(
        list_entries_result=QueryResult(
            success=True, message="OK", payload=entries
        )
    )
    bridge = SpecBridge(facade=mock_facade)
    result = bridge.listSpecEntries("python")

    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], dict)
    assert result[0]["spec_id"] == "SW-2026-006"
    assert result[0]["domain"] == "python"
    assert result[0]["file_exists"] is True
    assert result[1]["spec_id"] == "SW-2026-008"
    assert result[1]["title"] == "auto-pm 项目管理"
    # 验证 filter_domain 透传给 Facade
    assert mock_facade.list_entries_calls == ["python"]


def test_spec_bridge_no_facade(qapp):
    """facade=None 时 3 个 Slot 都返回降级值，不抛异常"""
    from auto_pm.ui.qml.bridges.spec_bridge import SpecBridge

    bridge = SpecBridge(facade=None)
    # runSpecCheck 降级
    assert bridge.runSpecCheck() == {"error_count": -1, "message": "未初始化"}
    # getSpecOverview 降级
    assert bridge.getSpecOverview() == {}
    # listSpecEntries 降级
    assert bridge.listSpecEntries("") == []


def test_spec_bridge_run_check_failure(qapp):
    """Facade 返回失败时，runSpecCheck 返回 {"error_count": -1, "message": ...}"""
    from PySide6.QtTest import QSignalSpy

    from auto_pm.ui.qml.bridges.spec_bridge import SpecBridge

    mock_facade = _MockSpecFacade(
        run_check_result=CommandResult(
            success=False, message="Spec check failed", payload=None
        )
    )
    bridge = SpecBridge(facade=mock_facade)

    spy = QSignalSpy(bridge.specCheckCompleted)
    result = bridge.runSpecCheck()

    assert result == {"error_count": -1, "message": "Spec check failed"}
    # 失败时不 emit 信号
    assert spy.count() == 0
