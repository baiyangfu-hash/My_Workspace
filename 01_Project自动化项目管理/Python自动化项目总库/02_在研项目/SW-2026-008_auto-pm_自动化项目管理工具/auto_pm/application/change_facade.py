"""Change Facade 接口层"""

from typing import Any

from auto_pm.core.protocols import ChangeServiceProtocol
from auto_pm.ui.contracts.commands.change_commands import (
    CreateChangeCommand,
    TransitionChangeCommand,
)
from auto_pm.ui.contracts.dto.change_dto import ChangeRequestDTO, ChangeSummaryDTO
from auto_pm.ui.contracts.result import CommandResult, QueryResult


class ChangeFacade:
    """提供给 UI 层的 Change 用例聚合入口"""

    def __init__(self, change_service: ChangeServiceProtocol | None = None):
        self._change_service = change_service

    @property
    def has_service(self) -> bool:
        return self._change_service is not None

    def _summary_to_dto(self, summary: Any) -> ChangeSummaryDTO:
        return ChangeSummaryDTO(
            change_number=summary.change_number,
            project_id=summary.project_id,
            project_name=summary.project_name,
            domain=str(summary.domain),
            business_nature=str(summary.business_nature),
            impact_scope=[str(s) for s in summary.impact_scope],
            status=str(summary.status),
            applicant=summary.applicant,
            apply_date=summary.apply_date,
            title=summary.title,
            urgency=str(summary.urgency),
        )

    def _request_to_dto(self, cr: Any) -> ChangeRequestDTO:
        sections = getattr(cr, "sections", {}) or {}
        return ChangeRequestDTO(
            change_number=cr.change_number,
            project_id=cr.project_id,
            project_name=cr.project_name,
            domain=str(cr.domain),
            business_nature=str(cr.business_nature),
            impact_scope=[str(s) for s in cr.impact_scope],
            status=str(cr.status),
            applicant=cr.applicant,
            apply_date=cr.apply_date,
            planned_date=getattr(cr, "planned_date", ""),
            urgency=str(cr.urgency),
            background=getattr(cr, "background", ""),
            necessity=getattr(cr, "necessity", ""),
            references=getattr(cr, "references", ""),
            risk_level=getattr(cr, "risk_level", ""),
            mitigation=getattr(cr, "mitigation", ""),
            propagation_chain=getattr(cr, "propagation_chain", ""),
            file_path=getattr(cr, "file_path", ""),
            sections=sections,
        )

    def list_change_requests(self, project_id: str | None = None) -> QueryResult[list[ChangeSummaryDTO]]:
        try:
            if not self._change_service:
                return QueryResult(success=False, message="No change_service", payload=[])
            if project_id:
                summaries = self._change_service.list_change_requests(project_id)
            else:
                summaries = self._change_service.list_all_changes()
            dtos = [self._summary_to_dto(s) for s in summaries]
            return QueryResult(success=True, message="Success", payload=dtos)
        except Exception as e:
            return QueryResult(success=False, message=str(e), payload=[])

    def get_change_detail(self, change_id: str) -> QueryResult[ChangeRequestDTO | None]:
        try:
            if not self._change_service:
                return QueryResult(success=False, message="No change_service", payload=None)
            cr = self._change_service.get_change_request(change_id)
            if cr is None:
                return QueryResult(success=False, message=f"Change {change_id} not found", payload=None)
            return QueryResult(success=True, message="Success", payload=self._request_to_dto(cr))
        except Exception as e:
            return QueryResult(success=False, message=str(e), payload=None)

    def create_change_request(self, command: CreateChangeCommand) -> CommandResult[ChangeRequestDTO | None]:
        try:
            if not self._change_service:
                return CommandResult(success=False, message="No change_service", payload=None)
            # ChangeService.create_change_request requires:
            # project_id, domain, business_nature, impact_scope, applicant, background, necessity
            # plus optional ones. We extract from command.
            cr = self._change_service.create_change_request(
                project_id=command.project_id,
                domain=command.domain,
                business_nature=command.nature,
                impact_scope=[],  # TODO: CreateChangeCommand 暂未携带 impact_scope，待 GUI 支持后补齐
                applicant=command.applicant,
                background=command.background,
                necessity=command.necessity,
            )
            return CommandResult(success=True, message="Created successfully", payload=self._request_to_dto(cr))
        except Exception as e:
            return CommandResult(success=False, message=str(e), payload=None)

    def transition_change(self, command: TransitionChangeCommand) -> CommandResult[ChangeRequestDTO | None]:
        try:
            if not self._change_service:
                return CommandResult(success=False, message="No change_service", payload=None)
            self._change_service.transition_status(
                change_number=command.change_id,
                new_status=command.target_status,
                approver=command.operator,
                comment=command.note or "",
                allow_partial_verification=command.allow_partial_verification,
            )
            # Re-fetch after transition
            cr = self._change_service.get_change_request(command.change_id)
            if cr is None:
                return CommandResult(success=False, message="Transitioned but could not fetch", payload=None)
            return CommandResult(success=True, message="Transitioned successfully", payload=self._request_to_dto(cr))
        except Exception as e:
            return CommandResult(success=False, message=str(e), payload=None)
