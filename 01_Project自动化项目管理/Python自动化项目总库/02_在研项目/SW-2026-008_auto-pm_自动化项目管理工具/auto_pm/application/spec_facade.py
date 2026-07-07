"""Spec Facade 接口层

M4 第 1 批重构：从"转发层"升级为"用例编排层"，返回带类型 DTO。
"""

from auto_pm.core.protocols import SpecCenterServiceProtocol, SpecCheckServiceProtocol
from auto_pm.ui.contracts.dto.spec_dto import (
    SpecCenterEntryDTO,
    SpecCenterOverviewDTO,
    SpecCheckResultDTO,
)
from auto_pm.ui.contracts.result import CommandResult, QueryResult


class SpecFacade:
    """提供给 UI 层的 Spec 用例聚合入口"""

    def __init__(
        self,
        spec_check_service: SpecCheckServiceProtocol | None = None,
        spec_center_service: SpecCenterServiceProtocol | None = None,
    ):
        self._spec_check_service = spec_check_service
        self._spec_center_service = spec_center_service

    @property
    def has_spec_check_service(self) -> bool:
        return self._spec_check_service is not None

    @property
    def has_spec_center_service(self) -> bool:
        return self._spec_center_service is not None

    def run_spec_check(self) -> CommandResult[SpecCheckResultDTO | None]:
        try:
            if not self._spec_check_service:
                return CommandResult(success=False, message="No spec_check_service", payload=None)
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

            dto = SpecCheckResultDTO(
                error_count=output.error_count,
                warning_count=output.warning_count,
                info_count=output.info_count,
                exit_code=output.exit_code,
                results=results,
            )
            return CommandResult(success=True, message="Success", payload=dto)
        except Exception as e:
            return CommandResult(success=False, message=str(e), payload=None)

    def get_spec_center_overview(self) -> QueryResult[SpecCenterOverviewDTO | None]:
        try:
            if not self._spec_center_service:
                return QueryResult(success=False, message="No spec_center_service", payload=None)
            overview = self._spec_center_service.get_overview()
            health = overview.health_summary
            dto = SpecCenterOverviewDTO(
                spec_count=overview.spec_count,
                domain_counts=dict(overview.domain_counts),
                lifecycle_counts=dict(overview.lifecycle_counts),
                health_summary={
                    "error_count": health.error_count,
                    "warning_count": health.warning_count,
                    "info_count": health.info_count,
                    "exit_code": health.exit_code,
                },
            )
            return QueryResult(success=True, message="Success", payload=dto)
        except Exception as e:
            return QueryResult(success=False, message=str(e), payload=None)

    def list_spec_center_entries(self, filter_domain: str | None = None) -> QueryResult[list[SpecCenterEntryDTO]]:
        try:
            if not self._spec_center_service:
                return QueryResult(success=False, message="No spec_center_service", payload=[])
            entries = self._spec_center_service.list_entries(filter_domain)
            dtos = [
                SpecCenterEntryDTO(
                    spec_id=e.spec_id,
                    title=e.title,
                    number=e.number,
                    domain=e.domain,
                    lifecycle=e.lifecycle,
                    canonical_path=e.canonical_path,
                    version=e.version,
                    file_exists=e.file_exists,
                )
                for e in entries
            ]
            return QueryResult(success=True, message="Success", payload=dtos)
        except Exception as e:
            return QueryResult(success=False, message=str(e), payload=[])
