"""Change 相关 Command 定义"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CreateChangeCommand:
    project_id: str
    title: str
    domain: str
    nature: str
    background: str
    necessity: str
    applicant: str

@dataclass(frozen=True)
class TransitionChangeCommand:
    change_id: str
    target_status: str
    operator: str
    note: str | None
    allow_partial_verification: bool
