"""Workbench 相关 DTO 定义"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DashboardSnapshotDTO:
    total_projects: int
    phase_counts: dict[str, int]
    open_change_count: int
    failed_check_project_count: int
    not_applicable_project_count: int
    recent_activities: list[dict[str, Any]]
    risk_hints: list[dict[str, Any]]
    failed_check_project_ids: list[str]
    not_applicable_project_ids: list[str]

@dataclass(frozen=True)
class ProjectCardDTO:
    project_id: str
    name: str
    stack: str
    phase: str
    version: str
    health_status: str
    open_change_count: int
    last_activity_at: str | None
    path: str
    business_line: str

@dataclass(frozen=True)
class ProjectWorkspaceDTO:
    project_id: str
    summary: dict[str, Any]
    asset_summary: dict[str, Any] | None
    document_status: dict[str, Any] | None
    vartable_status: dict[str, Any] | None
    pending_actions: list[dict[str, Any]]
