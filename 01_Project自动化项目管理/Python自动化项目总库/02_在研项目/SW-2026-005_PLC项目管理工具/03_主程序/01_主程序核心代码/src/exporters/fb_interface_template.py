# -*- coding: utf-8 -*-
"""FB接口变量数据模型 - 用于Excel导出的结构化数据定义"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class FBInterfaceVariable:
    """FB/FC接口变量行模型（对应Excel一行）"""

    seq_no: int
    category: str
    name: str
    data_type: str
    hidden: str
    initial_value: str
    retain_type: str
    comment: str

    def to_row(self) -> list:
        return [
            self.seq_no,
            self.category,
            self.name,
            self.data_type,
            self.hidden,
            self.initial_value,
            self.retain_type,
            self.comment,
        ]


@dataclass
class FBInterfaceExport:
    """FB/FC完整接口导出模型"""

    fb_name: str
    fb_type: str
    variables: List[FBInterfaceVariable] = field(default_factory=list)
    source_file: str = ""
    total_inputs: int = 0
    total_outputs: int = 0
    total_vars: int = 0

    def recalculate_totals(self):
        self.total_inputs = sum(
            1 for v in self.variables if v.category == "IN"
        )
        self.total_outputs = sum(
            1 for v in self.variables if v.category == "OUT"
        )
        self.total_vars = sum(
            1 for v in self.variables if v.category == "VAR"
        )
