"""Spec 相关 DTO 定义"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SpecCenterDTO:
    overview: dict[str, Any]
    index_items: list[dict[str, Any]]
    check_items: list[dict[str, Any]]
    drift_items: list[dict[str, Any]]
