"""QML 数据桥（V0.6.0 重构 / V0.8.0 Phase 1+2 扩展）

QmlBridge(QObject) 暴露后端 Service 为 QML 可调用属性，是 Python↔QML 数据桥。
- 暴露 ProjectService/ChangeService/SpecService 为 QML 可调用 property
- 提供 signals 通知 QML 数据变更
- 不修改后端 Service 接口（后端零改动约束）

W1：仅暴露 ProjectService（PoC）
W2：扩展 ChangeService + SpecService（W1 验证项 ③ 补齐）
V0.8.0 Phase 1：扩展 ReportService/TemplateService/PmSessionService/DashboardService/
AssetSummaryService/DocRefreshService（CHG-090，为 4 个新 QML 页面做前置准备）
V0.8.0 Phase 2：补齐 6 个 Slot（getTemplateDetail/getSettingsSummary/clearCache/
rebuildIndex/getSpecOverview/listSpecEntries）+ SpecCenterAdapter 注入（CHG-091）

设计参考：02_设计/GUI原型设计.md §15.5 Python↔QML 数据桥设计
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, cast

import yaml
from PySide6.QtCore import Property, QObject, Signal, Slot

from auto_pm.change.change_service import ChangeService
from auto_pm.core.project_service import ProjectService

# ── Phase 2 静态映射（CHG-091）─────────────────────────────

# 模板名前缀 → 技术栈
_TEMPLATE_STACK: dict[str, str] = {
    "plc": "plc",
    "python": "python",
}


def _infer_stack(template_name: str) -> str:
    """根据模板名推断技术栈"""
    name_lower = template_name.lower()
    for prefix, stack in _TEMPLATE_STACK.items():
        if prefix in name_lower:
            return stack
    return "unknown"


def _read_template_description(template_path: str) -> str:
    """从 copier.yml 首行注释提取模板描述"""
    copier_yml = os.path.join(template_path, "copier.yml")
    try:
        with open(copier_yml, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#"):
                    if " - " in line:
                        return line.split(" - ", 1)[1].strip()
                    return line.lstrip("# ").strip()
                if line:
                    break
    except OSError:
        return ""
    return ""


def _read_template_version(template_path: str) -> str:
    """读取模板版本（copier.yml 无版本字段时返回默认 v1.0）"""
    copier_yml = os.path.join(template_path, "copier.yml")
    try:
        with open(copier_yml, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        version = data.get("_version", "")
        if version:
            return str(version)
    except (OSError, yaml.YAMLError):
        return "v1.0"
    return "v1.0"


class QmlBridge(QObject):
    """Python↔QML 数据桥

    暴露后端 Service 为 QML 可调用属性，QML 端通过 bridge.xxx 调用。
    W2 起接口冻结：新增 Service 必须通过 Property 暴露，禁止 QML 直接访问私有字段。

    后端零改动约束：本类只读取 Service 数据，不修改 Service 接口。
    """

    # signals：数据变更通知 QML
    projectsChanged = Signal()
    changesChanged = Signal()
    specCheckCompleted = Signal(int, int, int)  # error_count, warning_count, info_count
    projectSelected = Signal(str, str)  # project_id, project_name（点击项目卡片时发）

    def __init__(
        self,
        project_service: ProjectService,
        change_service: ChangeService | None = None,
        spec_check_service: Any | None = None,
        report_service: Any | None = None,
        template_service: Any | None = None,
        pm_session_service: Any | None = None,
        dashboard_service: Any | None = None,
        asset_summary_service: Any | None = None,
        doc_refresh_service: Any | None = None,
        spec_center_service: Any | None = None,  # V0.8.0 Phase 2（CHG-091）
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._project_service = project_service
        self._change_service = change_service
        self._spec_check_service = spec_check_service
        # V0.8.0 Phase 1 新增 6 个 Service（CHG-090）
        self._report_service = report_service
        self._template_service = template_service
        self._pm_session_service = pm_session_service
        self._dashboard_service = dashboard_service
        self._asset_summary_service = asset_summary_service
        self._doc_refresh_service = doc_refresh_service
        # V0.8.0 Phase 2 新增 SpecCenterAdapter（CHG-091）
        self._spec_center_service = spec_center_service
        self._projects_cache: list[Any] = []
        self._changes_cache: list[Any] = []
        # 变更详情缓存：change_number → ChangeRequest dict
        self._change_detail_cache: dict[str, dict[str, Any]] = {}

    # ── QML 可调用 Slots（项目） ──────────────────────────

    @Slot(result=list)
    def listProjects(self) -> list[Any]:
        """返回项目列表（QML 端调用 bridge.listProjects()）

        返回 ProjectInfo 列表，QML 端通过 ProjectListModel 包装展示。
        缓存结果，避免重复扫描文件系统。
        """
        if not self._projects_cache:
            self._projects_cache = self._project_service.list_projects()
            self.projectsChanged.emit()
        return self._projects_cache

    @Slot(str, result="QVariant")
    def getProjectById(self, project_id: str) -> dict[str, Any]:
        """按 project_id 查询项目（QML 端调用 bridge.getProjectById(id)）

        W2 实现：返回 ProjectInfo 的字段字典（QML 端可直接用 .field 访问）。
        找不到时返回空 dict。
        """
        project = self._project_service.get_project(project_id)
        if project is None:
            return {}
        return self._project_to_dict(project)

    @Slot()
    def refreshProjects(self) -> None:
        """强制刷新项目缓存（QML 端调用 bridge.refreshProjects()）

        清空缓存，下次 listProjects() 调用时重新扫描。
        """
        self._projects_cache = []
        self.projectsChanged.emit()

    @Slot(str, str)
    def selectProject(self, project_id: str, project_name: str) -> None:
        """通知 QML 项目被选中（点击卡片时调用，触发工作区跳转）"""
        self.projectSelected.emit(project_id, project_name)

    # ── QML 可调用 Slots（变更） ──────────────────────────

    @Slot(result=list)
    def listAllChanges(self) -> list[dict[str, Any]]:
        """返回所有变更单摘要（变更中心列表用）

        W2 实现：调用 ChangeService.list_all_changes()，返回 ChangeSummary 字段字典列表。
        无 ChangeService 注入时返回空列表。
        """
        if self._change_service is None:
            return []
        if not self._changes_cache:
            summaries = self._change_service.list_all_changes()
            self._changes_cache = [self._summary_to_dict(s) for s in summaries]
            self.changesChanged.emit()
        return self._changes_cache

    @Slot(str, result=list)
    def listChanges(self, project_id: str) -> list[dict[str, Any]]:
        """返回指定项目的变更单摘要列表（项目工作区变更 Tab 用）"""
        if self._change_service is None:
            return []
        summaries = self._change_service.list_change_requests(project_id)
        return [self._summary_to_dict(s) for s in summaries]

    @Slot(str, result="QVariant")
    def getChangeRequest(self, change_number: str) -> dict[str, Any]:
        """按 change_number 查询变更单完整内容（详情面板用）

        返回扁平化字段字典，包含 §3-§10 主要字段。找不到时返回空 dict。
        """
        if self._change_service is None:
            return {}
        if change_number in self._change_detail_cache:
            return self._change_detail_cache[change_number]
        cr = self._change_service.get_change_request(change_number)
        if cr is None:
            return {}
        detail = self._change_request_to_dict(cr)
        self._change_detail_cache[change_number] = detail
        return detail

    @Slot()
    def refreshChanges(self) -> None:
        """强制刷新变更缓存"""
        self._changes_cache = []
        self._change_detail_cache.clear()
        self.changesChanged.emit()

    # ── QML 可调用 Slots（规范检查） ─────────────────────

    @Slot(result="QVariant")
    def runSpecCheck(self) -> dict[str, Any]:
        """运行工作空间规范检查（检查 Tab 用）

        返回字典 {error_count, warning_count, info_count, exit_code, results: [...]}。
        无 SpecCheckService 注入时返回 {error_count: -1, message: "未启用"}。
        """
        if self._spec_check_service is None:
            return {"error_count": -1, "message": "未启用规范检查服务"}
        try:
            output = self._spec_check_service.run()
            results = [
                {
                    "check_id": r.check_id,
                    "severity": r.severity.name if hasattr(r.severity, "name") else str(r.severity),
                    "message": r.message,
                    "details": r.details,
                    "fix_suggestion": r.fix_suggestion,
                }
                for r in output.results
            ]
            payload = {
                "error_count": output.error_count,
                "warning_count": output.warning_count,
                "info_count": output.info_count,
                "exit_code": output.exit_code,
                "results": results,
            }
            self.specCheckCompleted.emit(
                output.error_count, output.warning_count, output.info_count
            )
            return payload
        except Exception as exc:  # noqa: BLE001
            return {"error_count": -1, "message": f"检查失败: {exc}"}

    # ── QML 可调用 Slots（V0.8.0 Phase 1 新增 6 Service） ─

    @Slot(result="QVariant")
    def getProjectReport(self) -> dict[str, Any]:
        """项目报告（报告中心用，CHG-090 V0.8.0）"""
        if self._report_service is None:
            return {"error": "未启用报告服务"}
        try:
            return cast(dict[str, Any], self._report_service.get_project_overview())
        except Exception as exc:  # noqa: BLE001
            return {"error": f"报告生成失败: {exc}"}

    @Slot(result="QVariant")
    def getChangeReport(self) -> dict[str, Any]:
        """变更报告（报告中心用，CHG-090 V0.8.0）"""
        if self._report_service is None:
            return {"error": "未启用报告服务"}
        try:
            return cast(dict[str, Any], self._report_service.get_change_overview())
        except Exception as exc:  # noqa: BLE001
            return {"error": f"报告生成失败: {exc}"}

    @Slot(result="QVariant")
    def getSpecReport(self) -> dict[str, Any]:
        """规范报告（报告中心用，CHG-090 V0.8.0）"""
        if self._report_service is None:
            return {"error": "未启用报告服务"}
        try:
            return cast(dict[str, Any], self._report_service.get_spec_report())
        except Exception as exc:  # noqa: BLE001
            return {"error": f"报告生成失败: {exc}"}

    @Slot(result="QVariant")
    def getScanReport(self) -> dict[str, Any]:
        """扫描报告（报告中心用，CHG-090 V0.8.0）"""
        if self._report_service is None:
            return {"error": "未启用报告服务"}
        try:
            return cast(dict[str, Any], self._report_service.get_scan_report())
        except Exception as exc:  # noqa: BLE001
            return {"error": f"报告生成失败: {exc}"}

    @Slot(result=list)
    def listTemplates(self) -> list[str]:
        """列出所有可用模板（模板管理用，CHG-090 V0.8.0）"""
        if self._template_service is None:
            return []
        try:
            return cast(list[str], self._template_service.list_templates())
        except Exception:  # noqa: BLE001
            return []

    @Slot(str, result=str)
    def getTemplatePath(self, template_name: str) -> str:
        """获取模板路径（模板管理用，CHG-090 V0.8.0）"""
        if self._template_service is None:
            return ""
        try:
            return cast(str, self._template_service.get_template_path(template_name))
        except Exception:  # noqa: BLE001
            return ""

    @Slot(result="QVariant")
    def getPmSessionView(self) -> dict[str, Any]:
        """生成 PM_SESSION 只读视图（设置-PM_SESSION 用，CHG-090 V0.8.0）"""
        if self._pm_session_service is None:
            return {"error": "未启用 PM_SESSION 服务"}
        try:
            # PmSessionService.generate_view() → dict（含 §2/§3 视图内容）
            return cast(dict[str, Any], self._pm_session_service.generate_view())
        except Exception as exc:  # noqa: BLE001
            return {"error": f"视图生成失败: {exc}"}

    @Slot(result="QVariant")
    def runPmSessionCheck(self) -> dict[str, Any]:
        """运行 PM_SESSION 健康检查（设置-PM_SESSION 用，CHG-090 V0.8.0）"""
        if self._pm_session_service is None:
            return {"error": "未启用 PM_SESSION 服务"}
        try:
            # PmSessionCheckService.check(file_path) → CheckResult
            return cast(dict[str, Any], self._pm_session_service.check())
        except Exception as exc:  # noqa: BLE001
            return {"error": f"检查失败: {exc}"}

    @Slot(result="QVariant")
    def getDashboardSummary(self) -> dict[str, Any]:
        """获取驾驶舱摘要（首页/状态栏用，CHG-090 V0.8.0）"""
        if self._dashboard_service is None:
            return {"error": "未启用驾驶舱服务"}
        try:
            summary = self._dashboard_service.get_summary()
            # DashboardSummaryDTO → dict
            return {
                "total_projects": summary.total_projects,
                "phase_counts": dict(summary.phase_counts),
                "open_change_count": summary.open_change_count,
                "failed_check_project_count": summary.failed_check_project_count,
                "failed_check_project_ids": list(summary.failed_check_project_ids),
                "not_applicable_project_count": summary.not_applicable_project_count,
                "not_applicable_project_ids": list(summary.not_applicable_project_ids),
                "recent_activities": list(summary.recent_activities),
                "risk_hints": list(summary.risk_hints),
            }
        except Exception as exc:  # noqa: BLE001
            return {"error": f"驾驶舱数据获取失败: {exc}"}

    @Slot(str, result="QVariant")
    def getAssetSummary(self, project_id: str) -> dict[str, Any]:
        """获取项目工程资产摘要（工作区-概览用，CHG-090 V0.8.0）"""
        if self._asset_summary_service is None:
            return {"error": "未启用工程资产服务"}
        try:
            project = self._project_service.get_project(project_id)
            if project is None:
                return {"error": f"项目不存在: {project_id}"}
            # stack 可能是 Literal str（真实 Project）或 Enum（兼容旧 mock），统一转 str
            stack = str(getattr(project.stack, "value", project.stack))
            return cast(
                dict[str, Any],
                self._asset_summary_service.build_summary(
                    project_path=project.path,
                    stack=stack,
                    project_type=project.project_type,
                ),
            )
        except Exception as exc:  # noqa: BLE001
            return {"error": f"资产摘要获取失败: {exc}"}

    @Slot(str, bool, result="QVariant")
    def refreshProjectDocs(self, project_id: str, dry_run: bool) -> dict[str, Any]:
        """刷新项目文档自动区（工作区-文档用，CHG-090 V0.8.0）"""
        if self._doc_refresh_service is None:
            return {"error": "未启用文档刷新服务"}
        try:
            project = self._project_service.get_project(project_id)
            if project is None:
                return {"error": f"项目不存在: {project_id}"}
            result = self._doc_refresh_service.refresh_project_documents(
                project=project,
                dry_run=dry_run,
            )
            return cast(dict[str, Any], result.to_dict())
        except Exception as exc:  # noqa: BLE001
            return {"error": f"文档刷新失败: {exc}"}

    # ── V0.8.0 Phase 2 新增 6 个 Slot（CHG-091）──────────────

    @Slot(str, result="QVariant")
    def getTemplateDetail(self, template_name: str) -> dict[str, Any]:
        """模板详情（模板管理页用，CHG-091 V0.8.0 Phase 2）

        返回字段：name / version / description / stack / usage_count / path。
        内部完成 copier.yml 读取 + 项目使用数统计，避免 TemplateService 改动。
        """
        if self._template_service is None:
            return {"error": "未启用模板服务"}
        try:
            path = self._template_service.get_template_path(template_name)
            if not path:
                return {"error": f"模板路径不存在: {template_name}"}
            version = _read_template_version(path)
            description = _read_template_description(path)
            stack = _infer_stack(template_name)
            usage_count = self._count_template_usage(template_name)
            return {
                "name": template_name,
                "version": version,
                "description": description,
                "stack": stack,
                "usage_count": usage_count,
                "path": path,
            }
        except Exception as exc:  # noqa: BLE001
            return {"error": f"模板详情获取失败: {exc}"}

    @Slot(result="QVariant")
    def getSettingsSummary(self) -> dict[str, Any]:
        """设置页摘要（设置页用，CHG-091 V0.8.0 Phase 2）

        返回字段：workspace_root / db_path / project_count / change_count / last_sync。
        始终可用（基于 project_service），不依赖可选 Service 注入。
        """
        try:
            db = getattr(self._project_service, "db", None)
            db_path = ""
            project_count = 0
            change_count = 0
            last_sync = "—"

            if db is not None:
                db_path = str(getattr(db, "db_path", ""))
                try:
                    repo = getattr(self._project_service, "_repo", None)
                    if repo is not None and hasattr(repo, "count"):
                        project_count = int(repo.count())
                    else:
                        project_count = len(self._project_service.list_projects_cached())
                except Exception:  # noqa: BLE001
                    project_count = 0

                if self._change_service is not None:
                    try:
                        change_count = len(self._change_service.list_all_changes())
                    except Exception:  # noqa: BLE001
                        change_count = 0

                try:
                    last_sync = self._project_service.get_last_sync_time()
                except Exception:  # noqa: BLE001
                    last_sync = "—"

            return {
                "workspace_root": self._project_service.workspace_root,
                "db_path": db_path,
                "project_count": project_count,
                "change_count": change_count,
                "last_sync": last_sync,
                "db_available": db is not None,
            }
        except Exception as exc:  # noqa: BLE001
            return {"error": f"设置摘要获取失败: {exc}"}

    @Slot(result="QVariant")
    def clearCache(self) -> dict[str, Any]:
        """清除 DB 缓存（设置页用，CHG-091 V0.8.0 Phase 2）

        删除 DB 文件 + WAL/SHM 辅助文件 + 重新 init_schema。
        返回 {success: bool, message: str}。
        """
        db = getattr(self._project_service, "db", None)
        if db is None:
            return {"success": False, "message": "DB 未初始化，无需清除"}
        try:
            db_path = str(getattr(db, "db_path", ""))
            for suffix in ("", "-wal", "-shm"):
                file_path = db_path + suffix
                if os.path.isfile(file_path):
                    os.remove(file_path)
            if hasattr(db, "init_schema"):
                db.init_schema()
            return {"success": True, "message": "缓存已清除并重新初始化"}
        except Exception as exc:  # noqa: BLE001
            return {"success": False, "message": f"清除缓存失败: {exc}"}

    @Slot(result="QVariant")
    def rebuildIndex(self) -> dict[str, Any]:
        """重建索引（设置页用，CHG-091 V0.8.0 Phase 2）

        调用 ProjectService.sync_to_cache(force_full=True)，返回
        {projects_found: int, changes_found: int, message: str}。
        """
        db = getattr(self._project_service, "db", None)
        if db is None:
            return {
                "projects_found": 0,
                "changes_found": 0,
                "message": "DB 未初始化，无法重建索引",
            }
        try:
            result = self._project_service.sync_to_cache(force_full=True)
            projects_found = int(result.get("projects_found", 0))
            changes_found = int(result.get("changes_found", 0))
            return {
                "projects_found": projects_found,
                "changes_found": changes_found,
                "message": f"重建完成：发现 {projects_found} 个项目，{changes_found} 条变更单",
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "projects_found": 0,
                "changes_found": 0,
                "message": f"重建索引失败: {exc}",
            }

    @Slot(result="QVariant")
    def getSpecOverview(self) -> dict[str, Any]:
        """规范概览（规范中心-概览 Tab 用，CHG-091 V0.8.0 Phase 2）

        返回 {spec_count, domain_counts, lifecycle_counts, health_summary}。
        无 SpecCenterAdapter 注入时返回空数据（spec_count=0）。
        """
        if self._spec_center_service is None:
            return {
                "spec_count": 0,
                "domain_counts": {},
                "lifecycle_counts": {},
                "health_summary": {"error_count": 0, "warning_count": 0, "info_count": 0, "exit_code": 0},
                "error": "未启用规范中心服务",
            }
        try:
            overview = self._spec_center_service.get_overview()
            health = overview.health_summary
            return {
                "spec_count": overview.spec_count,
                "domain_counts": dict(overview.domain_counts),
                "lifecycle_counts": dict(overview.lifecycle_counts),
                "health_summary": {
                    "error_count": health.error_count,
                    "warning_count": health.warning_count,
                    "info_count": health.info_count,
                    "exit_code": health.exit_code,
                },
            }
        except Exception as exc:  # noqa: BLE001
            return {"error": f"规范概览获取失败: {exc}"}

    @Slot(str, result=list)
    def listSpecEntries(self, domain: str) -> list[dict[str, Any]]:
        """规范索引条目（规范中心-索引 Tab 用，CHG-091 V0.8.0 Phase 2）

        Args:
            domain: 过滤域（"all"/"pm"/"plc"/"python"），"all" 或空字符串返回全部

        Returns:
            [{spec_id, title, number, domain, lifecycle, canonical_path, version, file_exists}, ...]
        """
        if self._spec_center_service is None:
            return []
        try:
            filter_domain: str | None = None if (domain == "all" or not domain) else domain
            entries = self._spec_center_service.list_entries(filter_domain)
            return [
                {
                    "spec_id": e.spec_id,
                    "title": e.title,
                    "number": e.number,
                    "domain": e.domain,
                    "lifecycle": e.lifecycle,
                    "canonical_path": e.canonical_path,
                    "version": e.version,
                    "file_exists": e.file_exists,
                }
                for e in entries
            ]
        except Exception:  # noqa: BLE001
            return []

    # ── QML Property（只读） ──────────────────────────────

    def _project_service_prop(self) -> ProjectService:
        return self._project_service

    projectService = Property(QObject, _project_service_prop, constant=True)

    def _change_service_prop(self) -> QObject:
        return self._change_service if self._change_service is not None else QObject()  # type: ignore[return-value]

    changeService = Property(QObject, _change_service_prop, constant=True)

    def _spec_service_prop(self) -> QObject:
        return self._spec_check_service if self._spec_check_service is not None else QObject()

    specService = Property(QObject, _spec_service_prop, constant=True)

    def _has_project_service_prop(self) -> bool:
        return self._project_service is not None

    hasProjectService = Property(bool, _has_project_service_prop, constant=True)

    def _has_change_service_prop(self) -> bool:
        return self._change_service is not None

    hasChangeService = Property(bool, _has_change_service_prop, constant=True)

    def _has_spec_service_prop(self) -> bool:
        return self._spec_check_service is not None

    hasSpecService = Property(bool, _has_spec_service_prop, constant=True)

    # ── V0.8.0 Phase 1 新增 12 Property（6 service + 6 hasXxxService） ─

    def _report_service_prop(self) -> QObject:
        return self._report_service if self._report_service is not None else QObject()

    reportService = Property(QObject, _report_service_prop, constant=True)

    def _has_report_service_prop(self) -> bool:
        return self._report_service is not None

    hasReportService = Property(bool, _has_report_service_prop, constant=True)

    def _template_service_prop(self) -> QObject:
        return self._template_service if self._template_service is not None else QObject()

    templateService = Property(QObject, _template_service_prop, constant=True)

    def _has_template_service_prop(self) -> bool:
        return self._template_service is not None

    hasTemplateService = Property(bool, _has_template_service_prop, constant=True)

    def _pm_session_service_prop(self) -> QObject:
        return self._pm_session_service if self._pm_session_service is not None else QObject()

    pmSessionService = Property(QObject, _pm_session_service_prop, constant=True)

    def _has_pm_session_service_prop(self) -> bool:
        return self._pm_session_service is not None

    hasPmSessionService = Property(bool, _has_pm_session_service_prop, constant=True)

    def _dashboard_service_prop(self) -> QObject:
        return self._dashboard_service if self._dashboard_service is not None else QObject()

    dashboardService = Property(QObject, _dashboard_service_prop, constant=True)

    def _has_dashboard_service_prop(self) -> bool:
        return self._dashboard_service is not None

    hasDashboardService = Property(bool, _has_dashboard_service_prop, constant=True)

    def _asset_summary_service_prop(self) -> QObject:
        return self._asset_summary_service if self._asset_summary_service is not None else QObject()

    assetSummaryService = Property(QObject, _asset_summary_service_prop, constant=True)

    def _has_asset_summary_service_prop(self) -> bool:
        return self._asset_summary_service is not None

    hasAssetSummaryService = Property(bool, _has_asset_summary_service_prop, constant=True)

    def _doc_refresh_service_prop(self) -> QObject:
        return self._doc_refresh_service if self._doc_refresh_service is not None else QObject()

    docRefreshService = Property(QObject, _doc_refresh_service_prop, constant=True)

    def _has_doc_refresh_service_prop(self) -> bool:
        return self._doc_refresh_service is not None

    hasDocRefreshService = Property(bool, _has_doc_refresh_service_prop, constant=True)

    # ── V0.8.0 Phase 2 新增 2 Property（CHG-091）──────────

    def _spec_center_service_prop(self) -> QObject:
        return self._spec_center_service if self._spec_center_service is not None else QObject()

    specCenterService = Property(QObject, _spec_center_service_prop, constant=True)

    def _has_spec_center_service_prop(self) -> bool:
        return self._spec_center_service is not None

    hasSpecCenterService = Property(bool, _has_spec_center_service_prop, constant=True)

    # ── 内部辅助 ──────────────────────────────────────────

    @staticmethod
    def _project_to_dict(project: Any) -> dict[str, Any]:
        """ProjectInfo → dict（QML 端可直接 .field 访问）"""
        return {
            "project_id": project.project_id,
            "name": project.name,
            "path": project.path,
            "stack": project.stack.value if hasattr(project.stack, "value") else str(project.stack),
            "version": project.version,
            "phase": project.phase.value if hasattr(project.phase, "value") else str(project.phase),
            "business_line": project.business_line.value
            if hasattr(project.business_line, "value")
            else str(project.business_line),
            "project_type": project.project_type,
            "equipment_type": project.equipment_type,
            "plc_vendor": project.plc_vendor,
            "plc_model": project.plc_model,
            "description": project.description,
        }

    @staticmethod
    def _summary_to_dict(summary: Any) -> dict[str, Any]:
        """ChangeSummary → dict"""
        return {
            "change_number": summary.change_number,
            "project_id": summary.project_id,
            "project_name": summary.project_name,
            "domain": summary.domain.value if hasattr(summary.domain, "value") else str(summary.domain),
            "business_nature": summary.business_nature.value
            if hasattr(summary.business_nature, "value")
            else str(summary.business_nature),
            "impact_scope": [s.value if hasattr(s, "value") else str(s) for s in summary.impact_scope],
            "status": summary.status.value if hasattr(summary.status, "value") else str(summary.status),
            "applicant": summary.applicant,
            "apply_date": summary.apply_date,
            "title": summary.title,
            "urgency": summary.urgency.value if hasattr(summary.urgency, "value") else str(summary.urgency),
        }

    @staticmethod
    def _change_request_to_dict(cr: Any) -> dict[str, Any]:
        """ChangeRequest → 扁平化字段字典（包含 §3-§10 主要字段）"""
        sections = getattr(cr, "sections", {}) or {}
        return {
            "change_number": cr.change_number,
            "project_id": cr.project_id,
            "project_name": cr.project_name,
            "domain": cr.domain.value if hasattr(cr.domain, "value") else str(cr.domain),
            "business_nature": cr.business_nature.value
            if hasattr(cr.business_nature, "value")
            else str(cr.business_nature),
            "impact_scope": [s.value if hasattr(s, "value") else str(s) for s in cr.impact_scope],
            "status": cr.status.value if hasattr(cr.status, "value") else str(cr.status),
            "applicant": cr.applicant,
            "apply_date": cr.apply_date,
            "planned_date": cr.planned_date,
            "urgency": cr.urgency.value if hasattr(cr.urgency, "value") else str(cr.urgency),
            "background": cr.background,
            "necessity": cr.necessity,
            "references": cr.references,
            "risk_level": cr.risk_level,
            "mitigation": cr.mitigation,
            "propagation_chain": cr.propagation_chain,
            "file_path": cr.file_path,
            "sections": sections,
        }

    def _count_template_usage(self, template_name: str) -> int:
        """统计使用指定模板的项目数（CHG-091 V0.8.0 Phase 2）

        Args:
            template_name: 模板名称（与 _src_path 末尾匹配）

        Returns:
            使用该模板的项目数。加载失败返回 0。
        """
        try:
            projects = self._project_service.list_projects_cached()
        except Exception:  # noqa: BLE001
            return 0
        count = 0
        for proj in projects:
            src_path = str(getattr(proj, "extra", {}).get("_src_path", ""))
            if not src_path:
                continue
            if os.path.basename(src_path) == template_name:
                count += 1
        return count


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

        templates_dir = Path(workspace_root) / "templates"
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
) -> Any | None:
    """工厂函数：构造 DashboardService（CHG-090 V0.8.0）

    Args:
        project_service: 已实例化的 ProjectService
        change_service: 已实例化的 ChangeService
        plc_service: 可选的 PlcService

    Returns:
        DashboardService 实例或 None
    """
    try:
        from auto_pm.core.dashboard_service import DashboardService

        return DashboardService(
            project_service=project_service,
            change_service=change_service,
            plc_service=plc_service,
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
