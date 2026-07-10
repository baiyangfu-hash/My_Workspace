from pathlib import Path
from typing import Any


def make_spec_check_service(workspace_root: str) -> Any | None:
    """工厂函数：构造 SpecCheckService（避免硬依赖，方便测试 mock）

    返回 None 表示工作空间无 spec_registry.json，SpecService 不可用。
    """
    try:
        from auto_pm.spec.services.check_svc import CheckService

        workspace = Path(workspace_root)
        if not workspace.exists():
            return None
        return CheckService(workspace=workspace)
    except Exception:  # noqa: BLE001
        return None


# ── V0.8.0 Phase 1 新增 6 个工厂函数（CHG-090） ──────────────


def make_report_service(
    project_service: Any,
    change_service: Any,
    workspace_root: str,
    db: Any | None = None,
) -> Any | None:
    """工厂函数：构造 ReportService（CHG-090 V0.8.0）

    Args:
        project_service: 已实例化的 ProjectService
        change_service: 已实例化的 ChangeService
        workspace_root: 工作空间根路径
        db: 可选的 DatabaseManager

    Returns:
        ReportService 实例或 None（构造失败时）
    """
    try:
        from auto_pm.core.report_service import ReportService

        return ReportService(
            project_service=project_service,
            change_service=change_service,
            workspace_root=workspace_root,
            db=db,
        )
    except Exception:  # noqa: BLE001
        return None


def make_template_service(workspace_root: str) -> Any | None:
    """工厂函数：构造 TemplateService（CHG-090 V0.8.0）

    Args:
        workspace_root: 工作空间根路径（用于推导 templates_dir）

    Returns:
        TemplateService 实例或 None（无 templates/ 目录时）
    """
    try:
        from auto_pm.core.template_service import TemplateService

        templates_dir = Path(__file__).parent.parent / "templates"
        if not templates_dir.is_dir():
            return None
        return TemplateService(templates_dir=str(templates_dir))
    except Exception:  # noqa: BLE001
        return None


def make_pm_session_service(workspace_root: str) -> Any | None:
    """工厂函数：构造 PmSessionService（CHG-090 V0.8.0）

    返回一个聚合了 PmSessionParser/PmSessionCheckService/PmSessionArchiveService
    的视图对象，暴露 generate_view() 和 check() 方法供 QmlBridge 调用。

    Returns:
        PmSessionViewAggregator 实例或 None
    """
    try:
        from auto_pm.core.pm_session_service import (
            MAX_FILE_LINES,
            MAX_FILE_SIZE_KB,
            PmSessionCheckService,
            PmSessionParser,
            generate_view,
        )

        class _PmSessionViewAggregator:
            """聚合 PM_SESSION 视图生成 + 健康检查（QML 用）"""

            def __init__(self, workspace_root: str) -> None:
                self._workspace_root = workspace_root

            def _find_pm_session(self) -> Path | None:
                """在工作空间根或一级子目录中查找 PM_SESSION_*.md"""
                workspace = Path(self._workspace_root)
                pm_session_files = list(workspace.glob("PM_SESSION_*.md"))
                if not pm_session_files:
                    for sub in workspace.iterdir():
                        if sub.is_dir():
                            pm_session_files.extend(sub.glob("PM_SESSION_*.md"))
                            if pm_session_files:
                                break
                return pm_session_files[0] if pm_session_files else None

            def generate_view(self) -> dict[str, Any]:
                """生成 PM_SESSION 只读视图"""
                file_path = self._find_pm_session()
                if file_path is None:
                    return {"error": "未找到 PM_SESSION_*.md 文件"}
                parser = PmSessionParser()
                parse_result = parser.parse_file(file_path)
                view_str = generate_view(parse_result)
                return {
                    "file_path": str(file_path),
                    "view": view_str,
                }

            def check(self) -> dict[str, Any]:
                """运行 PM_SESSION 健康检查"""
                file_path = self._find_pm_session()
                if file_path is None:
                    return {"error": "未找到 PM_SESSION_*.md 文件"}
                checker = PmSessionCheckService()
                result = checker.check(file_path)
                return {
                    "file_path": str(result.file_path),
                    "file_size_kb": result.file_size_kb,
                    "max_file_size_kb": MAX_FILE_SIZE_KB,
                    "total_lines": result.total_lines,
                    "max_file_lines": MAX_FILE_LINES,
                    "missing_required": list(result.missing_required),
                    "deprecated_present": list(result.deprecated_present),
                    "is_oversized": result.is_oversized,
                    "warnings": list(result.warnings),
                    "is_healthy": result.is_healthy,
                }

        return _PmSessionViewAggregator(workspace_root)
    except Exception:  # noqa: BLE001
        return None


def make_dashboard_service(
    project_service: Any,
    change_service: Any,
    plc_service: Any | None = None,
    workspace_root: str | None = None,
) -> Any | None:
    """工厂函数：构造 DashboardService（CHG-090 V0.8.0）

    Args:
        project_service: 已实例化的 ProjectService
        change_service: 已实例化的 ChangeService
        plc_service: 可选的 PlcService
        workspace_root: 工作空间根目录（CHG-106 新增，用于定位 006 报告和 .pytest_cache）

    Returns:
        DashboardService 实例或 None
    """
    try:
        from auto_pm.core.dashboard_service import DashboardService

        return DashboardService(
            project_service=project_service,
            change_service=change_service,
            plc_service=plc_service,
            workspace_root=workspace_root,
        )
    except Exception:  # noqa: BLE001
        return None


def make_asset_summary_service() -> Any | None:
    """工厂函数：构造 AssetSummaryService（CHG-090 V0.8.0）

    AssetSummaryService 无构造参数，直接实例化。

    Returns:
        AssetSummaryService 实例或 None
    """
    try:
        from auto_pm.core.asset_summary_service import AssetSummaryService

        return AssetSummaryService()
    except Exception:  # noqa: BLE001
        return None


def make_doc_refresh_service(workspace_root: str) -> Any | None:
    """工厂函数：构造 DocRefreshService（CHG-090 V0.8.0）

    Args:
        workspace_root: 工作空间根路径

    Returns:
        DocRefreshService 实例或 None
    """
    try:
        from auto_pm.core.doc_refresh_service import DocRefreshService

        return DocRefreshService(workspace_root=workspace_root)
    except Exception:  # noqa: BLE001
        return None


# ── V0.8.0 Phase 2 新增工厂函数（CHG-091）─────────────────────


def make_spec_center_service(workspace_root: str) -> Any | None:
    """工厂函数：构造 SpecCenterAdapter（CHG-091 V0.8.0 Phase 2）

    SpecCenterAdapter 聚合 IndexService/CheckService/FrontmatterService/ReportService
    4 个 Spec 子系统 Service，提供 get_overview()/list_entries()/run_checks() 等方法。

    Args:
        workspace_root: 工作空间根路径（需含 spec_registry.json）

    Returns:
        SpecCenterAdapter 实例或 None（无 spec_registry.json 时）
    """
    try:
        from auto_pm.ui.global_pages.spec_center_dto import SpecCenterAdapter

        workspace = Path(workspace_root)
        if not workspace.exists():
            return None
        return SpecCenterAdapter(workspace=workspace)
    except Exception:  # noqa: BLE001
        return None
