"""Spec 相关 Command 定义"""

from dataclasses import dataclass


@dataclass(frozen=True)
class RunSpecCheckCommand:
    target_path: str
    auto_fix: bool
    scope: str
