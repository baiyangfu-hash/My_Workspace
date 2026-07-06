"""Change 相关 DTO 定义"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ChangeSummaryDTO:
    change_number: str
    project_id: str
    project_name: str
    domain: str
    business_nature: str
    impact_scope: list[str]
    status: str
    applicant: str
    apply_date: str
    title: str
    urgency: str

@dataclass(frozen=True)
class ChangeRequestDTO:
    change_number: str
    project_id: str
    project_name: str
    domain: str
    business_nature: str
    impact_scope: list[str]
    status: str
    applicant: str
    apply_date: str
    planned_date: str
    urgency: str
    background: str
    necessity: str
    references: str
    risk_level: str
    mitigation: str
    propagation_chain: str
    file_path: str
    sections: dict[str, Any]
