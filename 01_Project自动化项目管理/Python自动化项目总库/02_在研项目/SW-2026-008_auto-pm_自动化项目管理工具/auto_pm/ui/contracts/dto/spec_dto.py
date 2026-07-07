"""Spec 相关 DTO 定义"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SpecCenterDTO:
    overview: dict[str, Any]
    index_items: list[dict[str, Any]]
    check_items: list[dict[str, Any]]
    drift_items: list[dict[str, Any]]


@dataclass(frozen=True)
class SpecCheckResultDTO:
    """规范检查结果（对应 run_spec_check 返回，M4 第 1 批新增）"""
    error_count: int
    warning_count: int
    info_count: int
    exit_code: int
    results: list[dict[str, Any]]  # 检查项明细（保留 dict，因为字段动态）


@dataclass(frozen=True)
class SpecCenterOverviewDTO:
    """规范中心概览（对应 get_spec_center_overview 返回，M4 第 1 批新增）"""
    spec_count: int
    domain_counts: dict[str, int]
    lifecycle_counts: dict[str, int]
    health_summary: dict[str, Any]  # 含 error_count/warning_count/info_count/exit_code


@dataclass(frozen=True)
class SpecCenterEntryDTO:
    """规范中心条目（对应 list_spec_center_entries 返回的每个条目，M4 第 1 批新增）"""
    spec_id: str
    title: str
    number: str
    domain: str
    lifecycle: str
    canonical_path: str
    version: str
    file_exists: bool
