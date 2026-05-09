# -*- coding: utf-8 -*-
"""
工作流检查点数据模型
"""
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class WorkflowCheckpoint:
    """项目工作流阶段检查点"""

    stage: str
    label: str
    passed: bool
    required_assets: List[str] = field(default_factory=list)
    missing_assets: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        """转换为字典"""
        return {
            "stage": self.stage,
            "label": self.label,
            "passed": self.passed,
            "required_assets": list(self.required_assets),
            "missing_assets": list(self.missing_assets),
            "notes": list(self.notes),
        }
