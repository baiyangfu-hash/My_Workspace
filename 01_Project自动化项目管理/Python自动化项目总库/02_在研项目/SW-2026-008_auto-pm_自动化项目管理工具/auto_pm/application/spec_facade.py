"""Spec Facade 接口层"""

from typing import Any

from auto_pm.ui.contracts.result import CommandResult, QueryResult


class SpecFacade:
    """提供给 UI 层的 Spec 用例聚合入口"""

    def __init__(
        self,
        spec_check_service: Any = None,
        spec_center_service: Any = None,
    ):
        self._spec_check_service = spec_check_service
        self._spec_center_service = spec_center_service

    @property
    def has_spec_check_service(self) -> bool:
        return self._spec_check_service is not None

    @property
    def has_spec_center_service(self) -> bool:
        return self._spec_center_service is not None

    def run_spec_check(self) -> CommandResult[dict]:
        try:
            if not self._spec_check_service:
                return CommandResult(success=False, message="No spec_check_service", payload={"error_count": -1, "message": "未启用规范检查服务"})
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
            return CommandResult(success=True, message="Success", payload=payload)
        except Exception as e:
            return CommandResult(success=False, message=str(e), payload={"error_count": -1, "message": str(e)})

    def get_spec_center_overview(self) -> QueryResult[dict]:
        try:
            if not self._spec_center_service:
                return QueryResult(success=False, message="No spec_center_service", payload={})
            overview = self._spec_center_service.get_overview()
            health = overview.health_summary
            payload = {
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
            return QueryResult(success=True, message="Success", payload=payload)
        except Exception as e:
            return QueryResult(success=False, message=str(e), payload={})

    def list_spec_center_entries(self, filter_domain: str | None = None) -> QueryResult[list[dict]]:
        try:
            if not self._spec_center_service:
                return QueryResult(success=False, message="No spec_center_service", payload=[])
            entries = self._spec_center_service.list_entries(filter_domain)
            payload = [
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
            return QueryResult(success=True, message="Success", payload=payload)
        except Exception as e:
            return QueryResult(success=False, message=str(e), payload=[])
