"""SpecCenterView 规范中心全局页单元测试（V2.2 Week3 T14 重写）

测试内容（适配新 6 Tab 结构）：
- SpecCenterView 主容器：实例化 / 6 Tab 渲染 / Tab 标签 / 空工作空间 / 工作空间切换
- Tab1 Overview：DTO 渲染 / refresh 按钮触发
- Tab2 Index：条目渲染 / 搜索过滤 / 打开按钮启用状态
- Tab3 Check：检查结果渲染 / 空结果渲染
- Tab4 Frontmatter：预览项渲染 / 表格行数
- Tab5 Report：报告 DTO 渲染 / 格式下拉框
- Tab6 Compare：对比结果渲染（相同/不同）/ 刷新填充下拉框
- 集成测试：真实 workspace 下 Overview/Index/Compare 端到端

设计原则：
- 单元测试用 DTO 直接调用 render() 方法（避免真实 Service 依赖）
- 集成测试用真实 workspace（含 spec_registry.json + 规范文件）
- 遵循项目 qapp fixture（session 级，tests/conftest.py）
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# 必须在导入 PySide6 前设置离屏渲染，避免无显示环境报错
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QUrl  # noqa: E402
from PySide6.QtWidgets import QApplication, QTabWidget  # noqa: E402

from auto_pm.spec.core.checker_base import Severity  # noqa: E402
from auto_pm.ui.global_pages.spec_center import SpecCenterView  # noqa: E402
from auto_pm.ui.global_pages.spec_center_dto import (  # noqa: E402
    CompareResultDTO,
    FrontmatterPreviewDTO,
    HealthCheckOutputDTO,
    HealthCheckResultDTO,
    HealthSummaryDTO,
    ReportOutputDTO,
    SpecEntryDTO,
    SpecOverviewDTO,
)
from auto_pm.ui.global_pages.spec_center_tabs import (  # noqa: E402
    CheckTab,
    CompareTab,
    FrontmatterTab,
    IndexTab,
    OverviewTab,
    ReportTab,
)

# ── 测试用样本数据 ───────────────────────────────────────

_SAMPLE_SPECS: list[dict[str, Any]] = [
    {
        "spec_id": "LSP-905",
        "title": "SCL编程规范",
        "number": "905",
        "canonical_path": "0100_PLC自动化/00_通用规范/PLC编程/905_SCL编程规范_LSP.md",
        "version": "V1.0.3",
        "type_prefix": "LSP",
        "domain": "plc",
        "lifecycle": "stable",
        "sub_domain": "PLC编程",
        "tags": [],
        "replaces": [],
        "replaced_by": [],
    },
    {
        "spec_id": "LSP-904",
        "title": "SCL注释规范",
        "number": "904",
        "canonical_path": "0100_PLC自动化/00_通用规范/PLC编程/904_SCL注释规范_LSP.md",
        "version": "V1.2.0",
        "type_prefix": "LSP",
        "domain": "plc",
        "lifecycle": "stable",
        "sub_domain": "PLC编程",
        "tags": [],
        "replaces": [],
        "replaced_by": [],
    },
    {
        "spec_id": "CODE-210",
        "title": "Python编程规范",
        "number": "210",
        "canonical_path": "01_Project自动化项目管理/00_通用规范/Python开发/210_Python编程规范_DEV.md",
        "version": "V1.1.0",
        "type_prefix": "CODE",
        "domain": "python",
        "lifecycle": "stable",
        "sub_domain": "Python开发",
        "tags": [],
        "replaces": [],
        "replaced_by": [],
    },
    {
        "spec_id": "CODE-211",
        "title": "Python代码审查规范",
        "number": "211",
        "canonical_path": "01_Project自动化项目管理/00_通用规范/Python开发/211_Python代码审查规范_DEV.md",
        "version": "V1.0.0",
        "type_prefix": "CODE",
        "domain": "python",
        "lifecycle": "draft",
        "sub_domain": "Python开发",
        "tags": [],
        "replaces": [],
        "replaced_by": [],
    },
]


def _make_overview_dto(
    spec_count: int = 4,
    domain_counts: dict[str, int] | None = None,
    lifecycle_counts: dict[str, int] | None = None,
    error_count: int = 0,
    warning_count: int = 1,
) -> SpecOverviewDTO:
    """构造 SpecOverviewDTO"""
    return SpecOverviewDTO(
        spec_count=spec_count,
        domain_counts=domain_counts or {"plc": 2, "python": 2},
        lifecycle_counts=lifecycle_counts or {"stable": 3, "draft": 1},
        health_summary=HealthSummaryDTO(
            error_count=error_count,
            warning_count=warning_count,
            info_count=2,
            exit_code=0,
        ),
    )


def _make_entry(
    spec_id: str = "LSP-905",
    title: str = "SCL编程规范",
    domain: str = "plc",
    lifecycle: str = "stable",
    file_exists: bool = True,
) -> SpecEntryDTO:
    """构造 SpecEntryDTO"""
    return SpecEntryDTO(
        spec_id=spec_id,
        title=title,
        number=spec_id.split("-")[-1],
        domain=domain,
        lifecycle=lifecycle,
        canonical_path=f"fake/{spec_id}.md",
        version="V1.0.0",
        file_exists=file_exists,
    )


def _make_check_result(
    check_id: str = "SHC-001",
    severity: Severity = Severity.WARNING,
    message: str = "规范文件缺失",
    auto_fixable: bool = False,
) -> HealthCheckResultDTO:
    """构造 HealthCheckResultDTO"""
    return HealthCheckResultDTO(
        check_id=check_id,
        severity=severity,
        message=message,
        details="详情信息",
        fix_suggestion="修复建议",
        auto_fixable=auto_fixable,
    )


def _make_frontmatter_item(
    spec_id: str = "LSP-905",
    status: str = "pending",
    has_frontmatter: bool = False,
) -> FrontmatterPreviewDTO:
    """构造 FrontmatterPreviewDTO"""
    return FrontmatterPreviewDTO(
        spec_id=spec_id,
        file_path=Path(f"/fake/{spec_id}.md"),
        has_frontmatter=has_frontmatter,
        is_deprecated=False,
        file_exists=True,
        new_frontmatter=f"---\nspec_id: {spec_id}\n---\n",
        status=status,
    )


def _make_report_dto(fmt: str = "markdown", content: str = "# 报告内容") -> ReportOutputDTO:
    """构造 ReportOutputDTO"""
    return ReportOutputDTO(
        fmt=fmt,
        content=content,
        saved_path=Path("/fake/report.md"),
    )


def _make_compare_dto(
    left_spec_id: str = "LSP-905",
    right_spec_id: str = "LSP-904",
    same: bool = False,
) -> CompareResultDTO:
    """构造 CompareResultDTO"""
    left_lines = ["line1", "line2", "line3"]
    right_lines = ["line1", "line2", "line4"] if not same else left_lines
    return CompareResultDTO(
        left_spec_id=left_spec_id,
        right_spec_id=right_spec_id,
        left_path=f"/fake/{left_spec_id}.md",
        right_path=f"/fake/{right_spec_id}.md",
        left_lines=left_lines,
        right_lines=right_lines,
        added=[ln for ln in right_lines if ln not in left_lines],
        removed=[ln for ln in left_lines if ln not in right_lines],
        same=same,
    )


# ── fixtures ─────────────────────────────────────────────


def _create_spec_file(spec_dir: Path, code: str, name_suffix: str, content: str = "") -> Path:
    """在指定目录创建模拟规范文件"""
    spec_dir.mkdir(parents=True, exist_ok=True)
    file_path = spec_dir / f"{code}_{name_suffix}.md"
    file_path.write_text(content or f"# {code} 规范\n\n测试规范内容\n", encoding="utf-8")
    return file_path


def _create_registry(workspace: Path, specs: list[dict[str, Any]] | None = None) -> Path:
    """在工作空间下创建 spec_registry.json"""
    registry_dir = workspace / "00_Obsidian_Base全局规范文件仓库"
    registry_dir.mkdir(parents=True, exist_ok=True)
    registry_path = registry_dir / "spec_registry.json"

    specs_to_write = specs if specs is not None else _SAMPLE_SPECS
    data = {
        "version": "1.0.0",
        "last_updated": "2026-06-30",
        "workspace_root": str(workspace),
        "domains": {
            "pm": "项目管理域",
            "plc": "PLC自动化域",
            "python": "Python开发域",
            "cross-domain": "跨域通用",
        },
        "lifecycle_states": {
            "stable": "稳定",
            "draft": "草稿",
            "deprecated": "已废弃",
            "archived": "已归档",
        },
        "specs": {s["spec_id"]: {k: v for k, v in s.items() if k != "spec_id"} for s in specs_to_write},
        "project_copies": [],
    }
    registry_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return registry_path


@pytest.fixture
def spec_workspace(tmp_path: Path) -> Path:
    """临时工作空间，含 spec_registry.json + 4 个规范文件

    布局：
        tmp_path/
        ├── 00_Obsidian_Base全局规范文件仓库/spec_registry.json
        ├── 0100_PLC自动化/00_通用规范/PLC编程/
        │   ├── 905_SCL编程规范_LSP.md
        │   └── 904_SCL注释规范_LSP.md
        └── 01_Project自动化项目管理/00_通用规范/Python开发/
            ├── 210_Python编程规范_DEV.md
            └── 211_Python代码审查规范_DEV.md
    """
    _create_registry(tmp_path, _SAMPLE_SPECS)

    plc_dir = tmp_path / "0100_PLC自动化" / "00_通用规范" / "PLC编程"
    py_dir = tmp_path / "01_Project自动化项目管理" / "00_通用规范" / "Python开发"

    _create_spec_file(plc_dir, "905", "SCL编程规范_LSP", "# 905 SCL 编程规范\n\nPLC 编程规范内容\n")
    _create_spec_file(plc_dir, "904", "SCL注释规范_LSP", "# 904 SCL 注释规范\n\nPLC 注释规范内容\n")
    _create_spec_file(py_dir, "210", "Python编程规范_DEV", "# 210 Python 编程规范\n\nPython 规范内容\n")
    _create_spec_file(py_dir, "211", "Python代码审查规范_DEV", "# 211 Python 代码审查规范\n\n审查规范内容\n")

    return tmp_path


def _build_mock_adapter(
    overview: SpecOverviewDTO | None = None,
    entries: list[SpecEntryDTO] | None = None,
    health_output: HealthCheckOutputDTO | None = None,
    frontmatter_items: list[FrontmatterPreviewDTO] | None = None,
    report_output: ReportOutputDTO | None = None,
    compare_result: CompareResultDTO | None = None,
) -> MagicMock:
    """构造 Mock Adapter，返回预设 DTO"""
    adapter = MagicMock()
    adapter.get_overview.return_value = overview or _make_overview_dto()
    adapter.list_entries.return_value = entries or [
        _make_entry(spec_id="LSP-905", title="SCL编程规范", domain="plc"),
        _make_entry(spec_id="LSP-904", title="SCL注释规范", domain="plc"),
        _make_entry(spec_id="CODE-210", title="Python编程规范", domain="python"),
    ]
    adapter.run_checks.return_value = health_output or HealthCheckOutputDTO(
        results=[_make_check_result()],
        error_count=0,
        warning_count=1,
        info_count=1,
        exit_code=0,
        fix_results=[],
    )
    adapter.preview_frontmatter.return_value = frontmatter_items or [
        _make_frontmatter_item(spec_id="LSP-905"),
        _make_frontmatter_item(spec_id="CODE-210", status="applied", has_frontmatter=True),
    ]
    adapter.generate_report.return_value = report_output or _make_report_dto()
    adapter.compare_specs.return_value = compare_result or _make_compare_dto()
    adapter.workspace = Path("/fake/workspace")
    # registry.get_spec 返回 None（用于 IndexTab._on_open_spec 测试）
    adapter.registry.get_spec.return_value = None
    return adapter


# ── SpecCenterView 主容器测试 ────────────────────────────


class TestSpecCenterViewStructure:
    """SpecCenterView 实例化与基础结构测试"""

    def test_instantiation(self, qapp: QApplication) -> None:
        """SpecCenterView 应能正常实例化"""
        view = SpecCenterView()
        assert view is not None
        assert view.objectName() == "specCenterPage"
        assert view.tab_count == 6
        view.deleteLater()
        qapp.processEvents()

    def test_has_six_tabs(self, qapp: QApplication) -> None:
        """应包含 6 个 Tab"""
        view = SpecCenterView()
        assert view.tab_count == 6
        assert isinstance(view.tab_widget, QTabWidget)
        # 验证 Tab 类型
        assert isinstance(view.get_tab(0), OverviewTab)
        assert isinstance(view.get_tab(1), IndexTab)
        assert isinstance(view.get_tab(2), CheckTab)
        assert isinstance(view.get_tab(3), FrontmatterTab)
        assert isinstance(view.get_tab(4), ReportTab)
        assert isinstance(view.get_tab(5), CompareTab)
        view.deleteLater()
        qapp.processEvents()

    def test_tab_labels(self, qapp: QApplication) -> None:
        """Tab 标签应为中文：概览/规范索引/健康检查/Frontmatter/报告/对比"""
        view = SpecCenterView()
        expected_labels = ["概览", "规范索引", "健康检查", "Frontmatter", "报告", "对比"]
        for i, label in enumerate(expected_labels):
            assert view.tab_widget.tabText(i) == label
        view.deleteLater()
        qapp.processEvents()

    def test_empty_workspace_adapter_is_none(self, qapp: QApplication) -> None:
        """workspace_root 为空时 adapter 应为 None"""
        view = SpecCenterView()
        assert view.adapter is None
        assert view.workspace_root == ""
        view.deleteLater()
        qapp.processEvents()

    def test_refresh_with_empty_workspace_no_crash(self, qapp: QApplication) -> None:
        """空 workspace 时 refresh 不应抛异常"""
        view = SpecCenterView()
        view.refresh()  # 应仅记录警告，不抛异常
        view.deleteLater()
        qapp.processEvents()


class TestSpecCenterViewSetWorkspace:
    """set_workspace_root 切换工作空间测试"""

    def test_set_workspace_root_updates_adapter(
        self, qapp: QApplication, spec_workspace: Path
    ) -> None:
        """set_workspace_root 应创建新 adapter"""
        view = SpecCenterView()
        assert bool(view.adapter is None)

        view.set_workspace_root(str(spec_workspace))
        assert view.adapter is not None
        assert view.workspace_root == str(spec_workspace)
        view.deleteLater()
        qapp.processEvents()

    def test_set_empty_workspace_clears_adapter(
        self, qapp: QApplication, spec_workspace: Path
    ) -> None:
        """set_workspace_root 传空字符串应清空 adapter"""
        view = SpecCenterView(str(spec_workspace))
        assert bool(view.adapter is not None)

        view.set_workspace_root("")
        assert view.adapter is None
        view.deleteLater()
        qapp.processEvents()


# ── Tab1 Overview 测试 ──────────────────────────────────


class TestOverviewTab:
    """Tab1 概览测试"""

    def test_render_overview_dto(self, qapp: QApplication) -> None:
        """应正确渲染 Overview DTO"""
        adapter = _build_mock_adapter()
        tab = OverviewTab(adapter)
        dto = _make_overview_dto(
            spec_count=10,
            domain_counts={"plc": 4, "python": 6},
            lifecycle_counts={"stable": 8, "draft": 2},
            error_count=3,
            warning_count=5,
        )
        # OverviewTab 未公开 render()，直接调用 _render
        tab._render(dto)
        qapp.processEvents()

        assert tab.total_label.text() == "10"
        assert tab.error_label.text() == "3"
        assert tab.warning_label.text() == "5"
        tab.deleteLater()
        qapp.processEvents()

    def test_refresh_calls_adapter(self, qapp: QApplication) -> None:
        """refresh 应调用 adapter.get_overview"""
        adapter = _build_mock_adapter()
        tab = OverviewTab(adapter)
        tab.refresh()
        qapp.processEvents()
        adapter.get_overview.assert_called_once()
        # 验证渲染了返回的 DTO
        dto = adapter.get_overview.return_value
        assert tab.total_label.text() == str(dto.spec_count)
        tab.deleteLater()
        qapp.processEvents()

    def test_refresh_button_triggers_refresh(self, qapp: QApplication) -> None:
        """点击刷新按钮应触发 refresh"""
        adapter = _build_mock_adapter()
        tab = OverviewTab(adapter)
        with patch.object(tab, "refresh") as mock_refresh:
            tab.refresh_button.click()
            qapp.processEvents()
            mock_refresh.assert_called_once()
        tab.deleteLater()
        qapp.processEvents()


# ── Tab2 Index 测试 ─────────────────────────────────────


class TestIndexTab:
    """Tab2 索引测试"""

    def test_render_entries(self, qapp: QApplication) -> None:
        """应渲染规范条目（每个条目一行 + 一个打开按钮）"""
        adapter = _build_mock_adapter()
        entries = [
            _make_entry(spec_id="LSP-905", title="SCL编程规范", domain="plc", file_exists=True),
            _make_entry(spec_id="CODE-210", title="Python编程规范", domain="python", file_exists=False),
        ]
        adapter.list_entries.return_value = entries

        tab = IndexTab(adapter)
        tab.refresh()
        qapp.processEvents()

        assert len(tab.spec_rows) == 2
        assert "LSP-905" in tab.spec_rows
        assert "CODE-210" in tab.spec_rows
        # 文件存在的按钮启用，不存在禁用
        btn_905 = tab.get_open_button("LSP-905")
        assert btn_905 is not None and btn_905.isEnabled() is True
        btn_210 = tab.get_open_button("CODE-210")
        assert btn_210 is not None and btn_210.isEnabled() is False
        tab.deleteLater()
        qapp.processEvents()

    def test_search_filter_by_spec_id(self, qapp: QApplication) -> None:
        """按 spec_id 搜索应过滤规范行"""
        adapter = _build_mock_adapter()
        entries = [
            _make_entry(spec_id="LSP-905", title="SCL编程规范", domain="plc"),
            _make_entry(spec_id="LSP-904", title="SCL注释规范", domain="plc"),
            _make_entry(spec_id="CODE-210", title="Python编程规范", domain="python"),
        ]
        adapter.list_entries.return_value = entries

        tab = IndexTab(adapter)
        tab.refresh()
        qapp.processEvents()

        # 搜索 "905"
        tab.search_box.setText("905")
        qapp.processEvents()

        row = tab.get_spec_row("LSP-905")
        assert row is not None and row.isHidden() is False
        row = tab.get_spec_row("LSP-904")
        assert row is not None and row.isHidden() is True
        row = tab.get_spec_row("CODE-210")
        assert row is not None and row.isHidden() is True
        tab.deleteLater()
        qapp.processEvents()

    def test_search_clear_restores_all(self, qapp: QApplication) -> None:
        """清空搜索框应恢复所有行可见"""
        adapter = _build_mock_adapter()
        entries = [
            _make_entry(spec_id="LSP-905", title="SCL编程规范", domain="plc"),
            _make_entry(spec_id="CODE-210", title="Python编程规范", domain="python"),
        ]
        adapter.list_entries.return_value = entries

        tab = IndexTab(adapter)
        tab.refresh()
        qapp.processEvents()

        tab.search_box.setText("plc")
        qapp.processEvents()
        row = tab.get_spec_row("CODE-210")
        assert row is not None and row.isHidden() is True

        tab.search_box.setText("")
        qapp.processEvents()
        row = tab.get_spec_row("LSP-905")
        assert row is not None and row.isHidden() is False
        row = tab.get_spec_row("CODE-210")
        assert row is not None and row.isHidden() is False
        tab.deleteLater()
        qapp.processEvents()

    def test_search_filter_by_title(self, qapp: QApplication) -> None:
        """按标题搜索应过滤规范行（不区分大小写）"""
        adapter = _build_mock_adapter()
        entries = [
            _make_entry(spec_id="LSP-905", title="SCL编程规范", domain="plc"),
            _make_entry(spec_id="LSP-904", title="SCL注释规范", domain="plc"),
            _make_entry(spec_id="CODE-210", title="Python编程规范", domain="python"),
        ]
        adapter.list_entries.return_value = entries

        tab = IndexTab(adapter)
        tab.refresh()
        qapp.processEvents()

        tab.search_box.setText("scl")
        qapp.processEvents()

        # 两个 SCL 规范可见，Python 不可见
        row = tab.get_spec_row("LSP-905")
        assert row is not None and row.isHidden() is False
        row = tab.get_spec_row("LSP-904")
        assert row is not None and row.isHidden() is False
        row = tab.get_spec_row("CODE-210")
        assert row is not None and row.isHidden() is True
        tab.deleteLater()
        qapp.processEvents()


# ── Tab3 Check 测试 ─────────────────────────────────────


class TestCheckTab:
    """Tab3 健康检查测试"""

    def test_render_check_output_with_results(self, qapp: QApplication) -> None:
        """应渲染检查结果（含错误/警告/提示计数）"""
        adapter = _build_mock_adapter()
        tab = CheckTab(adapter)
        dto = HealthCheckOutputDTO(
            results=[
                _make_check_result(check_id="SHC-001", severity=Severity.ERROR, message="规范文件缺失"),
                _make_check_result(check_id="SHC-002", severity=Severity.WARNING, message="frontmatter 缺失", auto_fixable=True),
            ],
            error_count=1,
            warning_count=1,
            info_count=0,
            exit_code=1,
            fix_results=[],
        )
        tab.render_dto(dto)
        qapp.processEvents()

        assert tab.error_label.text() == "错误: 1"
        assert tab.warning_label.text() == "警告: 1"
        assert tab.info_label.text() == "提示: 0"
        # 结果文本应包含 check_id 和 message
        text = tab.result_text.toPlainText()
        assert "SHC-001" in text
        assert "规范文件缺失" in text
        assert "SHC-002" in text
        assert "[可自动修复]" in text
        tab.deleteLater()
        qapp.processEvents()

    def test_render_check_output_empty(self, qapp: QApplication) -> None:
        """空检查结果应显示『所有检查通过』"""
        adapter = _build_mock_adapter()
        tab = CheckTab(adapter)
        dto = HealthCheckOutputDTO(
            results=[],
            error_count=0,
            warning_count=0,
            info_count=0,
            exit_code=0,
            fix_results=[],
        )
        tab.render_dto(dto)
        qapp.processEvents()

        assert "所有检查通过" in tab.result_text.toPlainText()
        tab.deleteLater()
        qapp.processEvents()

    def test_run_checks_calls_adapter(self, qapp: QApplication) -> None:
        """run_checks 应调用 adapter.run_checks"""
        adapter = _build_mock_adapter()
        tab = CheckTab(adapter)
        # 抑制 QMessageBox
        with patch("auto_pm.ui.global_pages.spec_center_tabs.check_tab.QMessageBox"):
            tab.run_checks()
            qapp.processEvents()
        adapter.run_checks.assert_called_once()
        assert tab.last_output is not None
        tab.deleteLater()
        qapp.processEvents()


# ── Tab4 Frontmatter 测试 ───────────────────────────────


class TestFrontmatterTab:
    """Tab4 Frontmatter 测试"""

    def test_render_frontmatter_items(self, qapp: QApplication) -> None:
        """应渲染 Frontmatter 预览项（表格行数 + 摘要）"""
        adapter = _build_mock_adapter()
        tab = FrontmatterTab(adapter)
        items = [
            _make_frontmatter_item(spec_id="LSP-905", status="pending", has_frontmatter=False),
            _make_frontmatter_item(spec_id="CODE-210", status="applied", has_frontmatter=True),
            _make_frontmatter_item(spec_id="CODE-211", status="error", has_frontmatter=False),
        ]
        tab.render_dto(items)
        qapp.processEvents()

        # 表格行数 = 项数
        assert tab.table.rowCount() == 3
        # 摘要计数
        assert tab.total_label.text() == "总数: 3"
        assert tab.pending_label.text() == "待添加: 1"
        # 第一列应为 spec_id
        item_0 = tab.table.item(0, 0)
        assert item_0 is not None and item_0.text() == "LSP-905"
        item_1 = tab.table.item(1, 0)
        assert item_1 is not None and item_1.text() == "CODE-210"
        tab.deleteLater()
        qapp.processEvents()

    def test_preview_calls_adapter(self, qapp: QApplication) -> None:
        """preview 应调用 adapter.preview_frontmatter"""
        adapter = _build_mock_adapter()
        tab = FrontmatterTab(adapter)
        with patch("auto_pm.ui.global_pages.spec_center_tabs.frontmatter_tab.QMessageBox"):
            tab.preview()
            qapp.processEvents()
        adapter.preview_frontmatter.assert_called_once()
        assert tab.table.rowCount() == len(adapter.preview_frontmatter.return_value)
        tab.deleteLater()
        qapp.processEvents()


# ── Tab5 Report 测试 ────────────────────────────────────


class TestReportTab:
    """Tab5 报告测试"""

    def test_render_report_dto(self, qapp: QApplication) -> None:
        """应渲染报告 DTO 内容"""
        adapter = _build_mock_adapter()
        tab = ReportTab(adapter)
        dto = _make_report_dto(fmt="markdown", content="# 规范报告\n\n规范总数: 10")
        tab.render_dto(dto)
        qapp.processEvents()

        assert tab.content_text.toPlainText() == "# 规范报告\n\n规范总数: 10"
        assert tab.save_button.isEnabled() is True
        assert "report.md" in tab.path_label.text()
        tab.deleteLater()
        qapp.processEvents()

    def test_format_combo_options(self, qapp: QApplication) -> None:
        """格式下拉框应包含 markdown 和 json 两个选项"""
        adapter = _build_mock_adapter()
        tab = ReportTab(adapter)
        assert tab.format_combo.count() == 2
        # 第一项是 markdown
        assert tab.format_combo.itemData(0) == "markdown"
        assert tab.format_combo.itemData(1) == "json"
        tab.deleteLater()
        qapp.processEvents()

    def test_generate_calls_adapter(self, qapp: QApplication) -> None:
        """generate 应调用 adapter.generate_report"""
        adapter = _build_mock_adapter()
        tab = ReportTab(adapter)
        with patch("auto_pm.ui.global_pages.spec_center_tabs.report_tab.QMessageBox"):
            tab.generate()
            qapp.processEvents()
        adapter.generate_report.assert_called_once()
        assert tab.last_output is not None
        tab.deleteLater()
        qapp.processEvents()


# ── Tab6 Compare 测试 ───────────────────────────────────


class TestCompareTab:
    """Tab6 对比测试"""

    def test_render_compare_dto_same(self, qapp: QApplication) -> None:
        """相同规范对比应显示『内容完全相同』"""
        adapter = _build_mock_adapter()
        tab = CompareTab(adapter)
        dto = _make_compare_dto(same=True)
        tab.render_dto(dto)
        qapp.processEvents()

        text = tab.result_text.toPlainText()
        assert "内容完全相同" in text
        tab.deleteLater()
        qapp.processEvents()

    def test_render_compare_dto_different(self, qapp: QApplication) -> None:
        """不同规范对比应显示新增/删除行数"""
        adapter = _build_mock_adapter()
        tab = CompareTab(adapter)
        dto = _make_compare_dto(same=False)
        tab.render_dto(dto)
        qapp.processEvents()

        text = tab.result_text.toPlainText()
        assert "LSP-905" in text
        assert "LSP-904" in text
        assert "新增行" in text
        assert "删除行" in text
        tab.deleteLater()
        qapp.processEvents()

    def test_refresh_populates_combos(self, qapp: QApplication) -> None:
        """refresh 应将规范列表填充到两个下拉框"""
        adapter = _build_mock_adapter()
        entries = [
            _make_entry(spec_id="LSP-905", title="SCL编程规范", domain="plc"),
            _make_entry(spec_id="LSP-904", title="SCL注释规范", domain="plc"),
            _make_entry(spec_id="CODE-210", title="Python编程规范", domain="python"),
        ]
        adapter.list_entries.return_value = entries

        tab = CompareTab(adapter)
        tab.refresh()
        qapp.processEvents()

        assert tab.left_combo.count() == 3
        assert tab.right_combo.count() == 3
        # 对比按钮应启用（>=2 项）
        assert tab.compare_button.isEnabled() is True
        # 第一项 data 应为 spec_id
        assert tab.left_combo.itemData(0) == "LSP-905"
        tab.deleteLater()
        qapp.processEvents()

    def test_compare_same_spec_shows_warning(self, qapp: QApplication) -> None:
        """对比相同规范应提示警告（不调用 adapter）"""
        adapter = _build_mock_adapter()
        entries = [
            _make_entry(spec_id="LSP-905", title="SCL编程规范", domain="plc"),
            _make_entry(spec_id="LSP-904", title="SCL注释规范", domain="plc"),
        ]
        adapter.list_entries.return_value = entries

        tab = CompareTab(adapter)
        tab.refresh()
        qapp.processEvents()

        # 选择相同的规范
        tab.left_combo.setCurrentIndex(0)
        tab.right_combo.setCurrentIndex(0)
        with patch("auto_pm.ui.global_pages.spec_center_tabs.compare_tab.QMessageBox") as mock_box:
            tab.compare()
            qapp.processEvents()
            # 应显示警告，不调用 compare_specs
            mock_box.warning.assert_called_once()
        adapter.compare_specs.assert_not_called()
        tab.deleteLater()
        qapp.processEvents()


# ── 集成测试（真实 workspace） ─────────────────────────


class TestSpecCenterViewIntegration:
    """SpecCenterView 与真实 workspace 集成测试"""

    def test_overview_tab_shows_real_data(
        self, qapp: QApplication, spec_workspace: Path
    ) -> None:
        """真实 workspace 下 OverviewTab 应显示 4 个规范"""
        view = SpecCenterView(str(spec_workspace))
        qapp.processEvents()

        overview = view.overview_tab
        assert overview.total_label.text() == "4"
        # 域分布：plc 2 + python 2
        assert overview.error_label.text() == "0"
        view.deleteLater()
        qapp.processEvents()

    def test_index_tab_lists_real_specs(
        self, qapp: QApplication, spec_workspace: Path
    ) -> None:
        """真实 workspace 下 IndexTab 应列出 4 个规范"""
        view = SpecCenterView(str(spec_workspace))
        qapp.processEvents()

        index = view.index_tab
        assert len(index.spec_rows) == 4
        assert "LSP-905" in index.spec_rows
        assert "LSP-904" in index.spec_rows
        assert "CODE-210" in index.spec_rows
        assert "CODE-211" in index.spec_rows
        # 所有规范文件都存在，按钮应启用
        for spec_id in ["LSP-905", "LSP-904", "CODE-210", "CODE-211"]:
            btn = index.get_open_button(spec_id)
            assert btn is not None and btn.isEnabled() is True
        view.deleteLater()
        qapp.processEvents()

    def test_compare_tab_real_compare(
        self, qapp: QApplication, spec_workspace: Path
    ) -> None:
        """真实 workspace 下 CompareTab 应能对比两个规范"""
        view = SpecCenterView(str(spec_workspace))
        qapp.processEvents()

        compare = view.compare_tab
        # 下拉框应有 4 个规范
        assert compare.left_combo.count() == 4
        assert compare.right_combo.count() == 4

        # 选择 LSP-905 和 LSP-904 进行对比
        compare.left_combo.setCurrentIndex(0)  # LSP-904（按 spec_id 排序后）
        compare.right_combo.setCurrentIndex(1)  # LSP-905
        with patch("auto_pm.ui.global_pages.spec_center_tabs.compare_tab.QMessageBox"):
            compare.compare()
            qapp.processEvents()

        # 应有对比结果
        assert compare.last_diff is not None
        text = compare.result_text.toPlainText()
        assert "LSP-904" in text or "LSP-905" in text
        view.deleteLater()
        qapp.processEvents()

    def test_open_spec_calls_open_url(
        self, qapp: QApplication, spec_workspace: Path
    ) -> None:
        """点击打开按钮应调用 QDesktopServices.openUrl"""
        view = SpecCenterView(str(spec_workspace))
        qapp.processEvents()

        index = view.index_tab
        with patch(
            "auto_pm.ui.global_pages.spec_center_tabs.index_tab.QDesktopServices.openUrl"
        ) as mock_open:
            index._on_open_spec("LSP-905")
            qapp.processEvents()
            assert mock_open.called
            url = mock_open.call_args[0][0]
            assert isinstance(url, QUrl)
            assert url.toString().startswith("file:")
        view.deleteLater()
        qapp.processEvents()


# ── DTO 层单元测试 ──────────────────────────────────────


class TestSpecCenterDto:
    """spec_center_dto.py 转换函数测试"""

    def test_build_overview_dto(self) -> None:
        """build_overview_dto 应正确聚合统计"""
        from auto_pm.spec.core.registry import SpecInfo
        from auto_pm.ui.global_pages.spec_center_dto import build_overview_dto

        specs = [
            SpecInfo(spec_id="LSP-905", title="A", number="905", canonical_path="", version="", type_prefix="LSP", domain="plc", lifecycle="stable", sub_domain="", tags=[], replaces=[], replaced_by=[]),
            SpecInfo(spec_id="CODE-210", title="B", number="210", canonical_path="", version="", type_prefix="CODE", domain="python", lifecycle="draft", sub_domain="", tags=[], replaces=[], replaced_by=[]),
        ]
        dto = build_overview_dto(specs, health=None)
        assert dto.spec_count == 2
        assert dto.domain_counts == {"plc": 1, "python": 1}
        assert dto.lifecycle_counts == {"stable": 1, "draft": 1}
        assert dto.health_summary.error_count == 0

    def test_build_compare_dto_same(self) -> None:
        """build_compare_dto 相同内容应标记 same=True"""
        from auto_pm.ui.global_pages.spec_center_dto import build_compare_dto

        content = "line1\nline2\nline3"
        dto = build_compare_dto("LSP-905", "LSP-904", "/a.md", "/b.md", content, content)
        assert dto.same is True
        assert dto.added == []
        assert dto.removed == []

    def test_build_compare_dto_different(self) -> None:
        """build_compare_dto 不同内容应计算 added/removed"""
        from auto_pm.ui.global_pages.spec_center_dto import build_compare_dto

        left = "line1\nline2\nline3"
        right = "line1\nline4"
        dto = build_compare_dto("LSP-905", "LSP-904", "/a.md", "/b.md", left, right)
        assert dto.same is False
        assert "line2" in dto.removed
        assert "line3" in dto.removed
        assert "line4" in dto.added
