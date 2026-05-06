# -*- coding: utf-8 -*-
"""
Variable数据模型 - PLC变量数据模型

定义PLC变量的完整属性结构，包含地址、类型、描述等。
支持IO分配表和变量清单的数据承载。
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class VariableModel:
    """
    变量数据模型

    描述一个PLC变量的完整信息，
    用于变量清单、IO表和HMI映射等场景。
    """

    var_id: str = ""
    name: str = ""
    address: str = ""               # IEC地址如 %IX0.0, %QW64
    data_type: str = "BOOL"
    category: str = ""               # INPUT/OUTPUT/GLOBAL/LOCAL
    description: str = ""
    unit: str = ""                   # 单位 (rpm, °C, %, etc.)
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    initial_value: str = ""
    plc_brand: str = ""
    hmi_control_type: str = ""       # HMI控件类型
    hmi_page_id: str = ""            # 关联HMI页面ID
    alarm_enabled: bool = False      # 是否关联报警
    alarm_code: str = ""             # 报警码
    alarm_message: str = ""          # 报警消息
    source_pou: str = ""             # 来源POU名
    comment: str = ""

    # 扩展字段
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        base = {
            "var_id": self.var_id,
            "name": self.name,
            "address": self.address,
            "data_type": self.data_type,
            "category": self.category,
            "description": self.description,
            "unit": self.unit,
            "initial_value": self.initial_value,
            "plc_brand": self.plc_brand,
            "hmi_control_type": self.hmi_control_type,
            "hmi_page_id": self.hmi_page_id,
            "alarm_enabled": self.alarm_enabled,
            "alarm_code": self.alarm_code,
            "alarm_message": self.alarm_message,
            "source_pou": self.source_pou,
            "comment": self.comment,
        }
        if self.min_value is not None:
            base["min_value"] = self.min_value
        if self.max_value is not None:
            base["max_value"] = self.max_value
        base.update(self.extra)
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VariableModel":
        """从字典创建实例"""
        filtered = {k: v for k, v in data.items()
                    if k in cls.__dataclass_fields__ or k == "extra"}
        return cls(**filtered)

    @property
    def is_io_variable(self) -> bool:
        """检查是否为IO变量 (有IEC地址)"""
        return bool(self.address) and (
            self.address.startswith("%I") or
            self.address.startswith("%Q")
        )

    @property
    def display_info(self) -> str:
        """获取显示用的简短信息"""
        parts = [self.name]
        if self.address:
            parts.append(f"@{self.address}")
        parts.append(f"[{self.data_type}]")
        if self.description:
            parts.append(self.description[:30])
        return " ".join(parts)
