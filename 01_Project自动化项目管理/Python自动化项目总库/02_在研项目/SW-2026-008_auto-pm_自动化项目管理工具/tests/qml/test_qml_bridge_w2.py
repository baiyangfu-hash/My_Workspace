"""QmlBridge W2 单元测试（V0.6.0 W2-S5）

覆盖 W2 新增 Slots/Properties/Static methods：
- listAllChanges()：变更中心列表（无 ChangeService 时返回 []）
- listChanges(project_id)：项目工作区变更 Tab
- getChangeRequest(change_number)：详情面板（含缓存）
- refreshChanges()：清空缓存 + emit changesChanged
- runSpecCheck()：规范检查（无 SpecService 时返回未启用）
- hasChangeService / hasSpecService 属性
- changeService / specService 属性
- _summary_to_dict / _change_request_to_dict 静态转换方法

测试策略：
- Mock ChangeService（MagicMock）+ 内存 ChangeSummary
- Mock SpecCheckService（MagicMock）+ 内存 CheckResult/CheckOutput
- 信号监听用 qapp.processEvents 同步处理
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import QTimer

from auto_pm.models import ChangeRequest, ChangeSummary
from auto_pm.ui.qml.qml_bridge import QmlBridge

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication


# ── fixture：内存构造 ChangeSummary / ChangeRequest ────────


def _make_summary(
    change_number: str = "CHG-SCPT-2026-086",
    project_id: str = "SW-2026-008",
    status: str = "draft",
    title: str = "QML 重构",
) -> ChangeSummary:
    return ChangeSummary(
        change_number=change_number,
        project_id=project_id,
        project_name="auto-pm",
        domain="SCPT",
        business_nature="OPT",
        impact_scope=["MODULE"],
        status=status,  # type: ignore[arg-type]
        applicant="glm",
        apply_date="2026-07-04",
        title=title,
        urgency="normal",  # type: ignore[arg-type]
    )


def _make_change_request(
    change_number: str = "CHG-SCPT-2026-086",
) -> ChangeRequest:
    return ChangeRequest(
        change_number=change_number,
        project_id="SW-2026-008",
        project_name="auto-pm",
        domain="SCPT",  # type: ignore[arg-type]
        business_nature="OPT",  # type: ignore[arg-type]
        impact_scope=["MODULE"],  # type: ignore[arg-type]
        status="draft",  # type: ignore[arg-type]
        applicant="glm",
        apply_date="2026-07-04",
        planned_date="2026-08-01",
        urgency="normal",  # type: ignore[arg-type]
        background="W2 QML 重构背景",
        necessity="提升 UI 维护性",
        references="02_设计/GUI原型设计.md",
        risk_level="low",
        mitigation="分阶段切换",
        propagation_chain="UI → Bridge",
        file_path="c:/tmp/CHG-SCPT-2026-086.md",
    )


@dataclass
class _FakeCheckResult:
    """模拟 CheckResult（避免依赖 Severity 枚举）"""

    check_id: str
    severity: Any  # 实际为 Severity 枚举
    message: str
    details: str
    fix_suggestion: str


@dataclass
class _FakeCheckOutput:
    """模拟 CheckOutput"""

    results: list[_FakeCheckResult]
    error_count: int
    warning_count: int
    info_count: int
    exit_code: int


@pytest.fixture
def mock_change_service() -> MagicMock:
    """Mock ChangeService：list_all_changes 返回 3 条摘要"""
    service = MagicMock()
    service.list_all_changes.return_value = [
        _make_summary(change_number="CHG-SCPT-2026-086", status="draft"),
        _make_summary(
            change_number="CHG-PLC-2026-001",
            project_id="DJ-2026-005",
            status="implementing",
            title="输送线逻辑",
        ),
        _make_summary(
            change_number="CHG-DOCU-2026-010",
            project_id="DJ-2026-010",
            status="closed",
            title="操作手册",
        ),
    ]
    service.list_change_requests.return_value = [
        _make_summary(change_number="CHG-SCPT-2026-086"),
    ]
    service.get_change_request.return_value = _make_change_request()
    return service


@pytest.fixture
def mock_spec_check_service() -> MagicMock:
    """Mock SpecCheckService：run() 返回 1 error + 2 warning"""
    from enum import Enum

    class _Severity(Enum):
        ERROR = "ERROR"
        WARNING = "WARNING"
        INFO = "INFO"

    output = _FakeCheckOutput(
        results=[
            _FakeCheckResult("SHC-001", _Severity.ERROR, "err1", "d1", "f1"),
            _FakeCheckResult("SHC-002", _Severity.WARNING, "warn1", "d2", "f2"),
            _FakeCheckResult("SHC-003", _Severity.WARNING, "warn2", "d3", "f3"),
        ],
        error_count=1,
        warning_count=2,
        info_count=0,
        exit_code=1,
    )
    service = MagicMock()
    service.run.return_value = output
    return service


@pytest.fixture
def empty_project_service() -> MagicMock:
    """Mock ProjectService（W2 测试不关心项目，但 QmlBridge 构造需要）"""
    service = MagicMock()
    service.list_projects.return_value = []
    return service


# ── hasChangeService / hasSpecService 属性 ─────────────────


def test_hasChangeService_false_when_no_service(
    qapp: QApplication, empty_project_service: MagicMock
) -> None:
    """未注入 ChangeService 时 hasChangeService 为 False"""
    bridge = QmlBridge(project_service=empty_project_service)  # type: ignore[arg-type]
    assert bridge.hasChangeService is False


def test_hasChangeService_true_when_service_injected(
    qapp: QApplication, empty_project_service: MagicMock, mock_change_service: MagicMock
) -> None:
    """注入 ChangeService 后 hasChangeService 为 True"""
    bridge = QmlBridge(
        project_service=empty_project_service,  # type: ignore[arg-type]
        change_service=mock_change_service,  # type: ignore[arg-type]
    )
    assert bridge.hasChangeService is True


def test_hasSpecService_false_when_no_service(
    qapp: QApplication, empty_project_service: MagicMock
) -> None:
    """未注入 SpecCheckService 时 hasSpecService 为 False"""
    bridge = QmlBridge(project_service=empty_project_service)  # type: ignore[arg-type]
    assert bridge.hasSpecService is False


def test_hasSpecService_true_when_service_injected(
    qapp: QApplication,
    empty_project_service: MagicMock,
    mock_spec_check_service: MagicMock,
) -> None:
    """注入 SpecCheckService 后 hasSpecService 为 True"""
    bridge = QmlBridge(
        project_service=empty_project_service,  # type: ignore[arg-type]
        spec_check_service=mock_spec_check_service,  # type: ignore[arg-type]
    )
    assert bridge.hasSpecService is True


# ── listAllChanges() ───────────────────────────────────────


def test_listAllChanges_returns_empty_when_no_service(
    qapp: QApplication, empty_project_service: MagicMock
) -> None:
    """无 ChangeService 时 listAllChanges 返回 []"""
    bridge = QmlBridge(project_service=empty_project_service)  # type: ignore[arg-type]
    assert bridge.listAllChanges() == []


def test_listAllChanges_returns_dict_list_and_caches(
    qapp: QApplication,
    empty_project_service: MagicMock,
    mock_change_service: MagicMock,
) -> None:
    """有 ChangeService 时返回 dict 列表，首次 emit + 缓存"""
    bridge = QmlBridge(
        project_service=empty_project_service,  # type: ignore[arg-type]
        change_service=mock_change_service,  # type: ignore[arg-type]
    )

    result1 = bridge.listAllChanges()
    assert len(result1) == 3
    assert result1[0]["change_number"] == "CHG-SCPT-2026-086"
    assert result1[0]["domain"] == "SCPT"
    assert result1[0]["status"] == "draft"

    # 二次调用应返回缓存
    result2 = bridge.listAllChanges()
    assert result2 is result1
    assert mock_change_service.list_all_changes.call_count == 1


def test_listAllChanges_emits_changesChanged(
    qapp: QApplication,
    empty_project_service: MagicMock,
    mock_change_service: MagicMock,
) -> None:
    """首次 listAllChanges 应 emit changesChanged"""
    bridge = QmlBridge(
        project_service=empty_project_service,  # type: ignore[arg-type]
        change_service=mock_change_service,  # type: ignore[arg-type]
    )

    emit_count = 0

    def _on_changed() -> None:
        nonlocal emit_count
        emit_count += 1

    bridge.changesChanged.connect(_on_changed)
    bridge.listAllChanges()
    qapp.processEvents()
    QTimer.singleShot(0, lambda: None)
    qapp.processEvents()

    assert emit_count == 1


# ── listChanges(project_id) ────────────────────────────────


def test_listChanges_returns_dict_list(
    qapp: QApplication,
    empty_project_service: MagicMock,
    mock_change_service: MagicMock,
) -> None:
    """listChanges(project_id) 返回指定项目的变更 dict 列表"""
    bridge = QmlBridge(
        project_service=empty_project_service,  # type: ignore[arg-type]
        change_service=mock_change_service,  # type: ignore[arg-type]
    )

    result = bridge.listChanges("SW-2026-008")
    assert len(result) == 1
    assert result[0]["change_number"] == "CHG-SCPT-2026-086"
    mock_change_service.list_change_requests.assert_called_once_with("SW-2026-008")


def test_listChanges_empty_when_no_service(
    qapp: QApplication, empty_project_service: MagicMock
) -> None:
    """无 ChangeService 时 listChanges 返回 []"""
    bridge = QmlBridge(project_service=empty_project_service)  # type: ignore[arg-type]
    assert bridge.listChanges("SW-2026-008") == []


# ── getChangeRequest() ─────────────────────────────────────


def test_getChangeRequest_returns_dict_and_caches(
    qapp: QApplication,
    empty_project_service: MagicMock,
    mock_change_service: MagicMock,
) -> None:
    """getChangeRequest 返回扁平化字段 dict，二次调用命中缓存"""
    bridge = QmlBridge(
        project_service=empty_project_service,  # type: ignore[arg-type]
        change_service=mock_change_service,  # type: ignore[arg-type]
    )

    result1 = bridge.getChangeRequest("CHG-SCPT-2026-086")
    assert isinstance(result1, dict)
    assert result1["change_number"] == "CHG-SCPT-2026-086"
    assert result1["background"] == "W2 QML 重构背景"
    assert result1["risk_level"] == "low"
    assert result1["file_path"] == "c:/tmp/CHG-SCPT-2026-086.md"

    # 二次调用应命中缓存（不再调用 Service）
    result2 = bridge.getChangeRequest("CHG-SCPT-2026-086")
    assert result2 is result1
    assert mock_change_service.get_change_request.call_count == 1


def test_getChangeRequest_empty_when_no_service(
    qapp: QApplication, empty_project_service: MagicMock
) -> None:
    """无 ChangeService 时返回空 dict"""
    bridge = QmlBridge(project_service=empty_project_service)  # type: ignore[arg-type]
    assert bridge.getChangeRequest("CHG-XXX") == {}


def test_getChangeRequest_empty_when_not_found(
    qapp: QApplication,
    empty_project_service: MagicMock,
    mock_change_service: MagicMock,
) -> None:
    """Service 返回 None 时返回空 dict"""
    mock_change_service.get_change_request.return_value = None
    bridge = QmlBridge(
        project_service=empty_project_service,  # type: ignore[arg-type]
        change_service=mock_change_service,  # type: ignore[arg-type]
    )
    assert bridge.getChangeRequest("CHG-NOT-EXIST") == {}


# ── refreshChanges() ───────────────────────────────────────


def test_refreshChanges_clears_cache(
    qapp: QApplication,
    empty_project_service: MagicMock,
    mock_change_service: MagicMock,
) -> None:
    """refreshChanges 清空缓存，下次 listAllChanges 重新扫描"""
    bridge = QmlBridge(
        project_service=empty_project_service,  # type: ignore[arg-type]
        change_service=mock_change_service,  # type: ignore[arg-type]
    )

    emit_count = 0

    def _on_changed() -> None:
        nonlocal emit_count
        emit_count += 1

    bridge.changesChanged.connect(_on_changed)
    bridge.listAllChanges()
    qapp.processEvents()

    bridge.refreshChanges()
    qapp.processEvents()

    bridge.listAllChanges()
    qapp.processEvents()

    assert mock_change_service.list_all_changes.call_count == 2
    assert emit_count >= 2


# ── runSpecCheck() ─────────────────────────────────────────


def test_runSpecCheck_returns_disabled_when_no_service(
    qapp: QApplication, empty_project_service: MagicMock
) -> None:
    """无 SpecCheckService 时返回 error_count=-1"""
    bridge = QmlBridge(project_service=empty_project_service)  # type: ignore[arg-type]
    result = bridge.runSpecCheck()
    assert result["error_count"] == -1
    assert "未启用" in result["message"]


def test_runSpecCheck_returns_payload_and_emits_signal(
    qapp: QApplication,
    empty_project_service: MagicMock,
    mock_spec_check_service: MagicMock,
) -> None:
    """有 SpecCheckService 时返回 payload 并 emit specCheckCompleted"""
    bridge = QmlBridge(
        project_service=empty_project_service,  # type: ignore[arg-type]
        spec_check_service=mock_spec_check_service,  # type: ignore[arg-type]
    )

    captured: list[tuple[int, int, int]] = []

    def _on_completed(e: int, w: int, i: int) -> None:
        captured.append((e, w, i))

    bridge.specCheckCompleted.connect(_on_completed)
    result = bridge.runSpecCheck()
    qapp.processEvents()

    assert result["error_count"] == 1
    assert result["warning_count"] == 2
    assert result["info_count"] == 0
    assert result["exit_code"] == 1
    assert len(result["results"]) == 3
    assert result["results"][0]["check_id"] == "SHC-001"

    assert len(captured) == 1
    assert captured[0] == (1, 2, 0)


def test_runSpecCheck_handles_exception(
    qapp: QApplication,
    empty_project_service: MagicMock,
    mock_spec_check_service: MagicMock,
) -> None:
    """Service 抛异常时返回 error_count=-1 + 错误消息"""
    mock_spec_check_service.run.side_effect = RuntimeError("boom")
    bridge = QmlBridge(
        project_service=empty_project_service,  # type: ignore[arg-type]
        spec_check_service=mock_spec_check_service,  # type: ignore[arg-type]
    )

    result = bridge.runSpecCheck()
    assert result["error_count"] == -1
    assert "检查失败" in result["message"]
    assert "boom" in result["message"]


# ── 静态转换方法 _summary_to_dict / _change_request_to_dict ──


def test_summary_to_dict_converts_all_fields(qapp: QApplication) -> None:
    """_summary_to_dict 应转换所有 ChangeSummary 字段（含枚举 .value）"""
    summary = _make_summary()
    d = QmlBridge._summary_to_dict(summary)
    assert d["change_number"] == "CHG-SCPT-2026-086"
    assert d["project_id"] == "SW-2026-008"
    assert d["domain"] == "SCPT"
    assert d["status"] == "draft"
    assert d["urgency"] == "normal"
    assert d["impact_scope"] == ["MODULE"]


def test_change_request_to_dict_converts_full_fields(qapp: QApplication) -> None:
    """_change_request_to_dict 应转换 §3-§10 主要字段"""
    cr = _make_change_request()
    d = QmlBridge._change_request_to_dict(cr)
    assert d["change_number"] == "CHG-SCPT-2026-086"
    assert d["background"] == "W2 QML 重构背景"
    assert d["necessity"] == "提升 UI 维护性"
    assert d["risk_level"] == "low"
    assert d["mitigation"] == "分阶段切换"
    assert d["propagation_chain"] == "UI → Bridge"
    assert d["file_path"] == "c:/tmp/CHG-SCPT-2026-086.md"
    # sections 字段应存在（可能为空 dict）
    assert "sections" in d


# ── make_spec_check_service 工厂函数 ─────────────────────


def test_make_spec_check_service_returns_none_for_nonexistent_path(
    qapp: QApplication, tmp_path: Any
) -> None:
    """make_spec_check_service 对不存在的工作空间返回 None"""
    from auto_pm.ui.qml.qml_bridge import make_spec_check_service

    result = make_spec_check_service(str(tmp_path / "nonexistent"))
    assert result is None


# ── changeService / specService property（fallback 为 QObject） ─


def test_changeService_property_returns_qobject_when_no_service(
    qapp: QApplication, empty_project_service: MagicMock
) -> None:
    """无 ChangeService 时 changeService property 返回空 QObject（非 None）"""
    from PySide6.QtCore import QObject

    bridge = QmlBridge(project_service=empty_project_service)  # type: ignore[arg-type]
    service = bridge.changeService
    assert isinstance(service, QObject)


def test_specService_property_returns_qobject_when_no_service(
    qapp: QApplication, empty_project_service: MagicMock
) -> None:
    """无 SpecCheckService 时 specService property 返回空 QObject（非 None）"""
    from PySide6.QtCore import QObject

    bridge = QmlBridge(project_service=empty_project_service)  # type: ignore[arg-type]
    service = bridge.specService
    assert isinstance(service, QObject)
