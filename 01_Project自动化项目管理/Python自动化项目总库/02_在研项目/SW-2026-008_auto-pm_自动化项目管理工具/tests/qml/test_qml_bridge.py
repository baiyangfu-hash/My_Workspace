"""QmlBridge 单元测试

覆盖 QmlBridge(QObject) 的 slot 和 property 行为：
- listProjects()：首次调用扫描并缓存，再次调用返回缓存
- refreshProjects()：清空缓存，触发 projectsChanged 信号
- projectService property：返回构造时注入的 ProjectService
- getProjectById()：Week 1 PoC 桩函数返回 None

测试策略：
- 用 mock_project_service（MagicMock）注入，避免依赖文件系统扫描
- 用 qapp fixture 确保 Qt 事件循环可用
- 信号监听用 QTimer.singleShot + qapp.processEvents 同步处理
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

from PySide6.QtCore import QTimer

from auto_pm.models import ProjectInfo
from auto_pm.ui.qml.qml_bridge import QmlBridge

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication


# ── listProjects() ─────────────────────────────────────────


def test_listProjects_returns_projects_and_caches(
    qapp: QApplication,
    mock_project_service: MagicMock,
    sample_projects: list[ProjectInfo],
) -> None:
    """listProjects() 应返回项目列表并缓存（再次调用不再扫描）"""
    bridge = QmlBridge(project_service=mock_project_service)  # type: ignore[arg-type]

    # 首次调用：触发扫描
    result1 = bridge.listProjects()
    assert len(result1) == 3
    assert result1[0].project_id == "SW-2026-008"

    # 二次调用：应返回缓存，不再触发 list_projects
    result2 = bridge.listProjects()
    assert result2 is result1  # 同一对象引用（缓存）

    # list_projects 只被调用一次（首次扫描）
    assert mock_project_service.list_projects.call_count == 1


def test_listProjects_emits_projectsChanged_on_first_call(
    qapp: QApplication,
    mock_project_service: MagicMock,
    sample_projects: list[ProjectInfo],
) -> None:
    """首次 listProjects() 应触发 projectsChanged 信号"""
    bridge = QmlBridge(project_service=mock_project_service)  # type: ignore[arg-type]

    signal_emitted = False

    def _on_changed() -> None:
        nonlocal signal_emitted
        signal_emitted = True

    bridge.projectsChanged.connect(_on_changed)
    bridge.listProjects()

    # 同步处理信号
    qapp.processEvents()
    # 给 Qt 一次事件循环机会（信号可能在下一次事件循环派发）
    QTimer.singleShot(0, lambda: None)
    qapp.processEvents()

    assert signal_emitted, "projectsChanged 信号未触发"


def test_listProjects_does_not_emit_on_cached_call(
    qapp: QApplication,
    mock_project_service: MagicMock,
    sample_projects: list[ProjectInfo],
) -> None:
    """缓存命中时不再触发 projectsChanged"""
    bridge = QmlBridge(project_service=mock_project_service)  # type: ignore[arg-type]

    emit_count = 0

    def _on_changed() -> None:
        nonlocal emit_count
        emit_count += 1

    bridge.projectsChanged.connect(_on_changed)
    bridge.listProjects()  # 首次：扫描 + emit
    qapp.processEvents()
    bridge.listProjects()  # 二次：缓存命中，不 emit
    qapp.processEvents()

    assert emit_count == 1, f"缓存命中不应再次 emit，实际 emit {emit_count} 次"


# ── refreshProjects() ──────────────────────────────────────


def test_refreshProjects_clears_cache_and_emits(
    qapp: QApplication,
    mock_project_service: MagicMock,
    sample_projects: list[ProjectInfo],
) -> None:
    """refreshProjects() 应清空缓存，下次 listProjects 重新扫描"""
    bridge = QmlBridge(project_service=mock_project_service)  # type: ignore[arg-type]

    emit_count = 0

    def _on_changed() -> None:
        nonlocal emit_count
        emit_count += 1

    bridge.projectsChanged.connect(_on_changed)

    # 首次扫描
    bridge.listProjects()
    qapp.processEvents()
    assert mock_project_service.list_projects.call_count == 1

    # refresh：清空缓存 + emit
    bridge.refreshProjects()
    qapp.processEvents()

    # 下次 listProjects 应重新扫描
    bridge.listProjects()
    qapp.processEvents()
    assert mock_project_service.list_projects.call_count == 2

    # emit 应至少 2 次（首次 listProjects + refresh）
    assert emit_count >= 2, f"应至少 emit 2 次，实际 {emit_count} 次"


# ── projectService property ───────────────────────────────


def test_projectService_property_returns_service(
    qapp: QApplication,
    mock_project_service: MagicMock,
) -> None:
    """bridge.projectService 应返回构造时注入的 ProjectService"""
    bridge = QmlBridge(project_service=mock_project_service)  # type: ignore[arg-type]

    # 通过 property getter 访问
    service = bridge.projectService
    assert service is mock_project_service


# ── getProjectById() W2 实现 ─────────────────────────────


def test_getProjectById_returns_dict_when_found(
    qapp: QApplication,
    mock_project_service: MagicMock,
    sample_projects: list[ProjectInfo],
) -> None:
    """W2 实现：getProjectById 应返回 ProjectInfo 字段 dict（找不到返回空 dict）"""
    mock_project_service.get_project.return_value = sample_projects[0]
    bridge = QmlBridge(project_service=mock_project_service)  # type: ignore[arg-type]

    result = bridge.getProjectById("SW-2026-008")
    assert isinstance(result, dict)
    assert result["project_id"] == "SW-2026-008"
    assert result["name"] == "auto-pm"
    assert result["stack"] == "python"
    assert result["phase"] == "developing"
    assert result["business_line"] == "SW"


def test_getProjectById_returns_empty_dict_when_not_found(
    qapp: QApplication,
    mock_project_service: MagicMock,
) -> None:
    """项目不存在时返回空 dict（向后兼容 QML 端 .field 访问返回 undefined）"""
    mock_project_service.get_project.return_value = None
    bridge = QmlBridge(project_service=mock_project_service)  # type: ignore[arg-type]

    result = bridge.getProjectById("NOT-EXIST")
    assert result == {}


def test_selectProject_emits_signal(
    qapp: QApplication,
    mock_project_service: MagicMock,
) -> None:
    """selectProject(id, name) 应触发 projectSelected 信号"""
    bridge = QmlBridge(project_service=mock_project_service)  # type: ignore[arg-type]

    captured: list[tuple[str, str]] = []

    def _on_selected(pid: str, pname: str) -> None:
        captured.append((pid, pname))

    bridge.projectSelected.connect(_on_selected)
    bridge.selectProject("SW-2026-008", "auto-pm")
    qapp.processEvents()

    assert len(captured) == 1
    assert captured[0] == ("SW-2026-008", "auto-pm")
