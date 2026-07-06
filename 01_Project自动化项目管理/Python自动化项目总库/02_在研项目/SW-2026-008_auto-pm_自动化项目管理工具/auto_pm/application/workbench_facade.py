"""Workbench Facade 接口层"""

from typing import Any

from auto_pm.core.protocols import ProjectServiceProtocol
from auto_pm.ui.contracts.dto.workbench_dto import (
    DashboardSnapshotDTO,
    ProjectCardDTO,
    ProjectWorkspaceDTO,
)
from auto_pm.ui.contracts.result import CommandResult, QueryResult


class WorkbenchFacade:
    """提供给 UI 层的 Workbench 用例聚合入口"""

    def __init__(
        self,
        dashboard_service: Any,
        project_service: ProjectServiceProtocol,
        asset_summary_service: Any,
    ):
        self._dashboard_service = dashboard_service
        self._project_service = project_service
        self._asset_summary_service = asset_summary_service

    @property
    def has_project_service(self) -> bool:
        return self._project_service is not None

    @property
    def has_dashboard_service(self) -> bool:
        return self._dashboard_service is not None

    def get_dashboard_snapshot(self) -> QueryResult[DashboardSnapshotDTO]:
        """获取驾驶舱摘要数据"""
        try:
            summary = self._dashboard_service.get_summary()
            dto = DashboardSnapshotDTO(
                total_projects=summary.total_projects,
                phase_counts=summary.phase_counts,
                open_change_count=summary.open_change_count,
                failed_check_project_count=summary.failed_check_project_count,
                not_applicable_project_count=summary.not_applicable_project_count,
                recent_activities=summary.recent_activities,
                risk_hints=summary.risk_hints,
                failed_check_project_ids=list(summary.failed_check_project_ids),
                not_applicable_project_ids=list(summary.not_applicable_project_ids),
            )
            return QueryResult(success=True, message="Success", payload=dto)
        except Exception as e:
            return QueryResult(success=False, message=str(e), errors=[str(e)])

    def list_project_cards(self) -> QueryResult[list[ProjectCardDTO]]:
        """获取项目列表卡片"""
        try:
            projects = self._project_service.list_projects()
            cards = []
            for p in projects:
                cards.append(ProjectCardDTO(
                    project_id=p.project_id,
                    name=p.name,
                    stack=str(p.stack),
                    phase=str(p.phase),
                    version=p.version,
                    health_status="Unknown",  # To be enriched later if needed
                    open_change_count=0,      # To be enriched later if needed
                    last_activity_at=None,
                    path=p.path,
                    business_line=str(p.business_line),
                ))
            return QueryResult(success=True, message="Success", payload=cards)
        except Exception as e:
            return QueryResult(success=False, message=str(e), errors=[str(e)])

    def get_project_workspace(self, project_id: str) -> QueryResult[ProjectWorkspaceDTO]:
        """获取单个项目的工作台聚合信息"""
        try:
            project = self._project_service.get_project(project_id)
            if not project:
                return QueryResult(success=False, message=f"Project not found: {project_id}", errors=["ProjectNotFound"])
            
            summary = project.model_dump() if hasattr(project, "model_dump") else {}
            # stack 等枚举类型转字符串以匹配旧的行为
            for k, v in summary.items():
                if hasattr(v, "value"):
                    summary[k] = str(v.value)
            
            asset_summary = None
            if self._asset_summary_service:
                stack_str = str(project.stack)
                asset_summary = self._asset_summary_service.build_summary(
                    project_path=project.path,
                    stack=stack_str,
                    project_type=project.project_type,
                )
            
            dto = ProjectWorkspaceDTO(
                project_id=project_id,
                summary=summary,
                asset_summary=asset_summary,
                document_status=None,
                vartable_status=None,
                pending_actions=[],
            )
            return QueryResult(success=True, message="Success", payload=dto)
        except Exception as e:
            return QueryResult(success=False, message=str(e), errors=[str(e)])

    def get_settings_summary(self) -> QueryResult[dict]:
        """获取设置页摘要基本信息（除 change_count 以外）"""
        try:
            if not self._project_service:
                return QueryResult(success=False, message="No project_service", payload={})
            
            db_path = self._project_service.get_db_path()
            db_available = self._project_service.is_cache_available()
            project_count = self._project_service.get_project_count()
                
            try:
                last_sync = self._project_service.get_last_sync_time()
            except Exception:
                last_sync = "—"
                
            payload = {
                "workspace_root": self._project_service.workspace_root,
                "db_path": db_path,
                "project_count": project_count,
                "last_sync": last_sync,
                "db_available": db_available,
            }
            return QueryResult(success=True, message="Success", payload=payload)
        except Exception as e:
            return QueryResult(success=False, message=str(e), payload={})

    def clear_cache(self) -> CommandResult[dict]:
        """清除 DB 缓存并重新初始化"""
        try:
            if not self._project_service:
                return CommandResult(success=False, message="No project_service", payload={})
            
            if not self._project_service.is_cache_available():
                return CommandResult(success=False, message="DB 未初始化，无需清除", payload={"success": False, "message": "DB 未初始化，无需清除"})
            
            import os
            db_path = self._project_service.get_db_path()
            for suffix in ("", "-wal", "-shm"):
                file_path = db_path + suffix
                if os.path.isfile(file_path):
                    os.remove(file_path)
            
            db = getattr(self._project_service, "db", None)
            if hasattr(db, "init_schema"):
                db.init_schema()
            return CommandResult(success=True, message="缓存已清除并重新初始化", payload={"success": True, "message": "缓存已清除并重新初始化"})
        except Exception as e:
            return CommandResult(success=False, message=str(e), payload={"success": False, "message": f"清除缓存失败: {e}"})

    def rebuild_index(self) -> CommandResult[dict]:
        """重建 DB 索引"""
        try:
            if not self._project_service:
                return CommandResult(success=False, message="No project_service", payload={})
            
            if not self._project_service.is_cache_available():
                return CommandResult(success=False, message="DB 未初始化，无法重建索引", payload={"projects_found": 0, "changes_found": 0, "message": "DB 未初始化，无法重建索引"})
            
            result = self._project_service.sync_to_cache(force_full=True)
            projects_found = int(result.get("projects_found", 0))
            changes_found = int(result.get("changes_found", 0))
            payload = {
                "projects_found": projects_found,
                "changes_found": changes_found,
                "message": f"重建完成：发现 {projects_found} 个项目，{changes_found} 条变更单",
            }
            return CommandResult(success=True, message="Success", payload=payload)
        except Exception as e:
            return CommandResult(success=False, message=str(e), payload={"projects_found": 0, "changes_found": 0, "message": f"重建索引失败: {e}"})
