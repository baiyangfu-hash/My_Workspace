"""QmlBridge V0.8.0 Phase 2 单元测试（CHG-091）

覆盖 V0.8.0 Phase 2 新增的 6 个 Slot + 2 个 Property + 4 个 QML 页面加载：
- getTemplateDetail：模板详情（含 copier.yml 解析 + 项目使用数统计）
- getSettingsSummary：设置页摘要（workspace/db_path/project_count/change_count）
- clearCache：清除 DB 缓存（删除 db + wal + shm + init_schema）
- rebuildIndex：重建索引（调用 sync_to_cache(force_full=True)）
- getSpecOverview：规范概览（spec_count/domain_counts/lifecycle_counts/health_summary）
- listSpecEntries：规范索引条目（按 domain 过滤）

配套 2 个 Property：specCenterService + hasSpecCenterService

4 个 QML 页面加载验证：SpecCenterView/ReportView/TemplateView/SettingsView
1 个新组件加载验证：BarRow

测试策略：
- 未注入时验证 Slot 返回默认值（空数据 / error dict）
- Mock 注入时验证 Slot 调用转发正确 + 返回数据结构正确
- QML 文件加载用 QQmlComponent 验证语法无错
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from auto_pm.ui.qml import qml_bridge as qml_bridge_module
from auto_pm.ui.qml.qml_bridge import QmlBridge

# ── 路径常量 ───────────────────────────────────────────────

_QML_DIR = (
    Path(__file__).resolve().parents[2]
    / "auto_pm"
    / "ui"
    / "qml"
)
_VIEWS_DIR = _QML_DIR / "views"
_COMPONENTS_DIR = _QML_DIR / "components"


# ── Mock helpers ─────────────────────────────────────────


def _make_mock_project_service() -> MagicMock:
    """Mock ProjectService（V0.6 兼容，含 list_projects_cached 返回空）

    注意：必须显式设置 db=None / _repo=None，否则 MagicMock 会自动创建
    MagicMock 属性，导致 getSettingsSummary/clearCache/rebuildIndex 的
    getattr(..., None) 检查返回 truthy 而非 None。
    """
    service = MagicMock()
    service.workspace_root = "/tmp/workspace"
    service.list_projects.return_value = []
    service.list_projects_cached.return_value = []
    service.get_last_sync_time.return_value = "2026-07-04 10:00:00"
    # 显式禁用 db / _repo，模拟未初始化 DB 的场景
    service.db = None
    service._repo = None
    return service


def _make_mock_spec_overview() -> Any:
    """构造 mock SpecOverviewDTO"""

    @dataclass
    class _MockHealth:
        error_count: int = 0
        warning_count: int = 2
        info_count: int = 5
        exit_code: int = 0

    @dataclass
    class _MockOverview:
        spec_count: int = 50
        domain_counts: dict[str, int] = field(
            default_factory=lambda: {"plc": 20, "python": 15, "pm": 10, "cross-domain": 5}
        )
        lifecycle_counts: dict[str, int] = field(
            default_factory=lambda: {"active": 45, "draft": 3, "deprecated": 2}
        )
        health_summary: Any = None

        def __post_init__(self) -> None:
            if self.health_summary is None:
                self.health_summary = _MockHealth()

    return _MockOverview()


def _make_mock_spec_entry(spec_id: str, domain: str = "plc") -> Any:
    """构造单个 mock SpecEntryDTO"""

    @dataclass
    class _MockEntry:
        spec_id: str
        title: str = "示例规范"
        number: str = "LSP-001"
        domain: str = "plc"
        lifecycle: str = "active"
        canonical_path: str = "spec/plc/lsp-001.md"
        version: str = "1.0"
        file_exists: bool = True

    return _MockEntry(spec_id=spec_id, domain=domain)


def _make_mock_spec_center_service() -> MagicMock:
    """构造 mock SpecCenterAdapter"""
    service = MagicMock()
    service.get_overview.return_value = _make_mock_spec_overview()
    service.list_entries.return_value = [
        _make_mock_spec_entry("LSP-001", "plc"),
        _make_mock_spec_entry("LSP-002", "plc"),
        _make_mock_spec_entry("CODE-001", "python"),
    ]
    return service


def _make_mock_template_service() -> MagicMock:
    """Mock TemplateService（get_template_path 返回固定路径）"""
    service = MagicMock()
    service.list_templates.return_value = ["plc-standard", "python-tool"]
    service.get_template_path.return_value = "/tmp/templates/plc-standard"
    return service


def _make_mock_change_service() -> MagicMock:
    """Mock ChangeService（list_all_changes 返回空）"""
    service = MagicMock()
    service.list_all_changes.return_value = []
    return service


# ── fixtures ─────────────────────────────────────────────


@pytest.fixture
def bridge_phase2_minimal(qapp: Any) -> QmlBridge:
    """仅注入 project_service 的 QmlBridge（Phase 2 默认值测试用）"""
    return QmlBridge(project_service=_make_mock_project_service())


@pytest.fixture
def bridge_phase2_full(qapp: Any, monkeypatch: pytest.MonkeyPatch) -> QmlBridge:
    """注入 Phase 2 全部 Service 的 QmlBridge

    使用 monkeypatch 替换模块级 _read_template_version/_read_template_description，
    避免依赖真实 copier.yml 文件。
    """
    monkeypatch.setattr(
        qml_bridge_module, "_read_template_version", lambda path: "v1.2"
    )
    monkeypatch.setattr(
        qml_bridge_module,
        "_read_template_description",
        lambda path: "PLC 标准模板",
    )
    return QmlBridge(
        project_service=_make_mock_project_service(),
        change_service=_make_mock_change_service(),
        spec_check_service=MagicMock(),
        report_service=MagicMock(),
        template_service=_make_mock_template_service(),
        pm_session_service=MagicMock(),
        dashboard_service=MagicMock(),
        asset_summary_service=MagicMock(),
        doc_refresh_service=MagicMock(),
        spec_center_service=_make_mock_spec_center_service(),
    )


# ── QML 加载 fixture ─────────────────────────────────────


@pytest.fixture
def qml_engine(qapp: Any) -> Any:
    """QQmlEngine（含 Theme.qml import 路径）"""
    from PySide6.QtQml import QQmlEngine

    engine = QQmlEngine()
    engine.addImportPath(str(_QML_DIR))
    return engine


def _load_component(engine: Any, qml_file: Path) -> Any:
    """加载 QML 组件并返回根对象实例"""
    from PySide6.QtCore import QUrl
    from PySide6.QtQml import QQmlComponent

    url = QUrl.fromLocalFile(str(qml_file))
    component = QQmlComponent(engine, url)
    if component.isError():
        errors = "\n".join(f"  - {e.toString()}" for e in component.errors())
        raise AssertionError(f"加载 QML 组件失败 {qml_file.name}:\n{errors}")
    obj = component.create()
    assert obj is not None, f"创建 QML 组件实例失败: {qml_file.name}"
    setattr(obj, "_component_ref", component)
    return obj


# ── 1. getTemplateDetail Slot ────────────────────────────


class TestGetTemplateDetail:
    """getTemplateDetail Slot 测试"""

    def test_returns_error_when_no_template_service(
        self, bridge_phase2_minimal: QmlBridge
    ) -> None:
        """未注入 TemplateService 时返回 '未启用模板服务'"""
        result = bridge_phase2_minimal.getTemplateDetail("plc-standard")
        assert result == {"error": "未启用模板服务"}

    def test_returns_detail_when_template_service_injected(
        self, bridge_phase2_full: QmlBridge
    ) -> None:
        """注入 TemplateService 时返回完整详情"""
        result = bridge_phase2_full.getTemplateDetail("plc-standard")
        assert result["name"] == "plc-standard"
        assert result["version"] == "v1.2"
        assert result["description"] == "PLC 标准模板"
        assert result["stack"] == "plc"
        assert result["usage_count"] == 0
        assert result["path"] == "/tmp/templates/plc-standard"

    def test_returns_error_when_path_empty(
        self, bridge_phase2_full: QmlBridge
    ) -> None:
        """TemplateService.get_template_path 返回空时返回 '路径不存在'"""
        bridge_phase2_full._template_service.get_template_path.return_value = ""
        result = bridge_phase2_full.getTemplateDetail("nonexistent")
        assert "error" in result
        assert "模板路径不存在" in result["error"]


# ── 2. getSettingsSummary Slot ──────────────────────────


class TestGetSettingsSummary:
    """getSettingsSummary Slot 测试"""

    def test_returns_summary_without_db(
        self, bridge_phase2_minimal: QmlBridge
    ) -> None:
        """project_service 无 db 属性时仍返回摘要（db_available=False）"""
        result = bridge_phase2_minimal.getSettingsSummary()
        assert result["workspace_root"] == "/tmp/workspace"
        assert result["db_available"] is False
        assert result["db_path"] == ""
        assert result["project_count"] == 0
        assert result["change_count"] == 0

    def test_returns_summary_with_db(
        self, bridge_phase2_full: QmlBridge
    ) -> None:
        """注入含 db 属性的 project_service 时返回 db 路径"""
        # bridge_phase2_full 的 mock project_service 默认 db=None
        # 模拟有 db 的情况
        mock_db = MagicMock()
        mock_db.db_path = "/tmp/cache.db"
        bridge_phase2_full._project_service.db = mock_db
        bridge_phase2_full._project_service._repo = MagicMock()
        bridge_phase2_full._project_service._repo.count.return_value = 13

        result = bridge_phase2_full.getSettingsSummary()
        assert result["db_path"] == "/tmp/cache.db"
        assert result["project_count"] == 13
        assert result["change_count"] == 0  # change_service 默认返回空
        assert result["db_available"] is True


# ── 3. clearCache Slot ──────────────────────────────────


class TestClearCache:
    """clearCache Slot 测试"""

    def test_returns_failure_when_no_db(
        self, bridge_phase2_minimal: QmlBridge
    ) -> None:
        """无 db 时返回 success=False"""
        result = bridge_phase2_minimal.clearCache()
        assert result["success"] is False
        assert "DB 未初始化" in result["message"]

    def test_clears_db_files_when_db_present(
        self, bridge_phase2_full: QmlBridge, tmp_path: Path
    ) -> None:
        """有 db 时删除 db + wal + shm 文件并 init_schema"""
        # 准备真实文件
        db_file = tmp_path / "cache.db"
        wal_file = tmp_path / "cache.db-wal"
        shm_file = tmp_path / "cache.db-shm"
        db_file.write_text("db")
        wal_file.write_text("wal")
        shm_file.write_text("shm")

        mock_db = MagicMock()
        mock_db.db_path = str(db_file)
        bridge_phase2_full._project_service.db = mock_db

        result = bridge_phase2_full.clearCache()
        assert result["success"] is True
        assert "缓存已清除" in result["message"]
        assert not db_file.exists()
        assert not wal_file.exists()
        assert not shm_file.exists()
        mock_db.init_schema.assert_called_once()


# ── 4. rebuildIndex Slot ────────────────────────────────


class TestRebuildIndex:
    """rebuildIndex Slot 测试"""

    def test_returns_failure_when_no_db(
        self, bridge_phase2_minimal: QmlBridge
    ) -> None:
        """无 db 时返回 projects_found=0"""
        result = bridge_phase2_minimal.rebuildIndex()
        assert result["projects_found"] == 0
        assert result["changes_found"] == 0
        assert "DB 未初始化" in result["message"]

    def test_rebuilds_when_db_present(
        self, bridge_phase2_full: QmlBridge
    ) -> None:
        """有 db 时调用 sync_to_cache 并返回统计"""
        mock_db = MagicMock()
        bridge_phase2_full._project_service.db = mock_db
        bridge_phase2_full._project_service.sync_to_cache.return_value = {
            "projects_found": 13,
            "changes_found": 20,
        }

        result = bridge_phase2_full.rebuildIndex()
        assert result["projects_found"] == 13
        assert result["changes_found"] == 20
        assert "13" in result["message"]
        assert "20" in result["message"]


# ── 5. getSpecOverview Slot ────────────────────────────


class TestGetSpecOverview:
    """getSpecOverview Slot 测试"""

    def test_returns_empty_when_no_spec_center(
        self, bridge_phase2_minimal: QmlBridge
    ) -> None:
        """未注入 SpecCenterAdapter 时返回 spec_count=0 + error 字段"""
        result = bridge_phase2_minimal.getSpecOverview()
        assert result["spec_count"] == 0
        assert result["domain_counts"] == {}
        assert result["lifecycle_counts"] == {}
        assert "error" in result
        assert "未启用规范中心服务" in result["error"]

    def test_returns_overview_when_injected(
        self, bridge_phase2_full: QmlBridge
    ) -> None:
        """注入 SpecCenterAdapter 时返回完整 overview"""
        result = bridge_phase2_full.getSpecOverview()
        assert result["spec_count"] == 50
        assert result["domain_counts"]["plc"] == 20
        assert result["domain_counts"]["python"] == 15
        assert result["lifecycle_counts"]["active"] == 45
        assert result["health_summary"]["error_count"] == 0
        assert result["health_summary"]["warning_count"] == 2
        assert result["health_summary"]["info_count"] == 5


# ── 6. listSpecEntries Slot ─────────────────────────────


class TestListSpecEntries:
    """listSpecEntries Slot 测试"""

    def test_returns_empty_when_no_spec_center(
        self, bridge_phase2_minimal: QmlBridge
    ) -> None:
        """未注入 SpecCenterAdapter 时返回空列表"""
        assert bridge_phase2_minimal.listSpecEntries("all") == []

    def test_returns_all_entries_when_domain_all(
        self, bridge_phase2_full: QmlBridge
    ) -> None:
        """domain='all' 时返回全部条目（不过滤）"""
        result = bridge_phase2_full.listSpecEntries("all")
        assert len(result) == 3
        assert result[0]["spec_id"] == "LSP-001"
        assert result[0]["domain"] == "plc"
        assert result[0]["file_exists"] is True

    def test_filters_by_domain(self, bridge_phase2_full: QmlBridge) -> None:
        """domain='plc' 时仅返回 plc 域条目"""
        # SpecCenterAdapter.list_entries 收到 'plc' 参数
        bridge_phase2_full.listSpecEntries("plc")
        # mock 返回全部 3 条，验证 filter_domain 传递正确
        bridge_phase2_full._spec_center_service.list_entries.assert_called_once_with("plc")


# ── 7. hasSpecCenterService Property ───────────────────


class TestSpecCenterServiceProperty:
    """specCenterService / hasSpecCenterService Property 测试"""

    def test_has_spec_center_false_when_not_injected(
        self, bridge_phase2_minimal: QmlBridge
    ) -> None:
        assert bridge_phase2_minimal.hasSpecCenterService is False

    def test_has_spec_center_true_when_injected(
        self, bridge_phase2_full: QmlBridge
    ) -> None:
        assert bridge_phase2_full.hasSpecCenterService is True


# ── 8. QML 页面加载验证 ─────────────────────────────────


class TestQMLViewLoad:
    """4 个 Phase 2 QML 页面 + BarRow 组件加载验证"""

    def test_report_view_loads(
        self, qapp: Any, qml_engine: Any
    ) -> None:
        """ReportView.qml 能成功加载（无语法错误）"""
        view = _load_component(qml_engine, _VIEWS_DIR / "ReportView.qml")
        assert view is not None

    def test_template_view_loads(
        self, qapp: Any, qml_engine: Any
    ) -> None:
        """TemplateView.qml 能成功加载"""
        view = _load_component(qml_engine, _VIEWS_DIR / "TemplateView.qml")
        assert view is not None

    def test_settings_view_loads(
        self, qapp: Any, qml_engine: Any
    ) -> None:
        """SettingsView.qml 能成功加载"""
        view = _load_component(qml_engine, _VIEWS_DIR / "SettingsView.qml")
        assert view is not None

    def test_spec_center_view_loads(
        self, qapp: Any, qml_engine: Any
    ) -> None:
        """SpecCenterView.qml 能成功加载"""
        view = _load_component(qml_engine, _VIEWS_DIR / "SpecCenterView.qml")
        assert view is not None

    def test_bar_row_component_loads(
        self, qapp: Any, qml_engine: Any
    ) -> None:
        """BarRow.qml 组件能成功加载"""
        comp = _load_component(qml_engine, _COMPONENTS_DIR / "BarRow.qml")
        assert comp is not None


# ── 9. 向后兼容（V0.8 Phase 1 + V0.6 既有功能零回归） ────


class TestBackwardCompatibleWithV08Phase1:
    """Phase 2 注入不影响 Phase 1 + V0.6 既有功能"""

    def test_phase1_report_slots_still_work(
        self, bridge_phase2_full: QmlBridge
    ) -> None:
        """Phase 1 的 ReportService Slot 仍正常"""
        bridge_phase2_full._report_service.get_project_overview.return_value = {"total": 13}
        result = bridge_phase2_full.getProjectReport()
        assert result["total"] == 13

    def test_phase1_template_list_still_works(
        self, bridge_phase2_full: QmlBridge
    ) -> None:
        """Phase 1 的 listTemplates Slot 仍正常"""
        templates = bridge_phase2_full.listTemplates()
        assert templates == ["plc-standard", "python-tool"]

    def test_v06_list_projects_still_works(
        self, bridge_phase2_minimal: QmlBridge
    ) -> None:
        """V0.6 既有 listProjects Slot 仍正常"""
        result = bridge_phase2_minimal.listProjects()
        assert isinstance(result, list)

    def test_v06_has_project_service_true(
        self, bridge_phase2_minimal: QmlBridge
    ) -> None:
        """V0.6 既有 hasProjectService Property 仍为 True"""
        assert bridge_phase2_minimal.hasProjectService is True
