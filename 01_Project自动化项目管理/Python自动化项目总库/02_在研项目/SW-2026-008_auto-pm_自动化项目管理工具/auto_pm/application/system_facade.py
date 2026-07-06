"""System Facade 接口层"""

from typing import Any

from auto_pm.core.protocols import ProjectServiceProtocol
from auto_pm.ui.contracts.result import CommandResult, QueryResult


class SystemFacade:
    """提供给 UI 层的 System (配置/状态/索引) 用例聚合入口"""

    def __init__(
        self,
        pm_session_service: Any,
        template_service: Any = None,
        project_service: ProjectServiceProtocol | None = None
    ):
        self._pm_session_service = pm_session_service
        self._template_service = template_service
        self._project_service = project_service

    @property
    def has_template_service(self) -> bool:
        return self._template_service is not None

    @property
    def has_pm_session_service(self) -> bool:
        return self._pm_session_service is not None

    def get_pm_session_view(self) -> QueryResult[dict]:
        try:
            if not self._pm_session_service:
                return QueryResult(success=False, message="No pm_session_service", payload={})
            view = self._pm_session_service.generate_view()
            return QueryResult(success=True, message="Success", payload=view)
        except Exception as e:
            return QueryResult(success=False, message=str(e), payload={})

    def run_pm_session_check(self) -> CommandResult[dict]:
        try:
            if not self._pm_session_service:
                return CommandResult(success=False, message="No pm_session_service", payload={})
            result = self._pm_session_service.check()
            return CommandResult(success=True, message="Success", payload=result)
        except Exception as e:
            return CommandResult(success=False, message=str(e), payload={})

    def list_templates(self) -> QueryResult[list[str]]:
        try:
            if not self._template_service:
                return QueryResult(success=False, message="No template_service", payload=[])
            templates = self._template_service.list_templates()
            return QueryResult(success=True, message="Success", payload=templates)
        except Exception as e:
            return QueryResult(success=False, message=str(e), payload=[])

    def get_template_path(self, template_name: str) -> QueryResult[str]:
        try:
            if not self._template_service:
                return QueryResult(success=False, message="No template_service", payload="")
            path = self._template_service.get_template_path(template_name)
            return QueryResult(success=True, message="Success", payload=path)
        except Exception as e:
            return QueryResult(success=False, message=str(e), payload="")

    def get_template_detail(self, template_name: str) -> QueryResult[dict]:
        try:
            if not self._template_service:
                return QueryResult(success=False, message="No template_service", payload={})
            
            path = self._template_service.get_template_path(template_name)
            if not path:
                return QueryResult(success=False, message=f"模板路径不存在: {template_name}", payload={})
            
            from pathlib import Path

            import yaml
            
            # Read version and description
            copier_yml = Path(path) / "copier.yml"
            version = "unknown"
            description = "暂无描述"
            if copier_yml.exists():
                try:
                    with open(copier_yml, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                        if data and isinstance(data, dict):
                            version = str(data.get("_commit", data.get("_min_copier_version", "unknown")))
                            description = str(data.get("_description", description))
                except Exception:
                    pass
            
            # Infer stack
            stack = "pm"
            if "python" in template_name.lower():
                stack = "python"
            elif "plc" in template_name.lower() or "portal" in template_name.lower():
                stack = "plc"

            # Count usage
            usage_count = 0
            if self._project_service:
                projects = self._project_service.list_projects()
                for p in projects:
                    try:
                        stack_val = str(p.stack).lower()
                        if stack_val == stack:
                            usage_count += 1
                    except Exception:
                        pass

            payload = {
                "name": template_name,
                "version": version,
                "description": description,
                "stack": stack,
                "usage_count": usage_count,
                "path": str(path),
            }
            return QueryResult(success=True, message="Success", payload=payload)
        except Exception as e:
            return QueryResult(success=False, message=str(e), payload={})

    def apply_template(self, project_id: str, template_name: str) -> CommandResult[dict]:
        try:
            if not self._template_service:
                return CommandResult(success=False, message="No template_service", payload={})
            result = self._template_service.apply_template(project_id, template_name)
            return CommandResult(success=True, message="Success", payload=result)
        except Exception as e:
            return CommandResult(success=False, message=str(e), payload={})
