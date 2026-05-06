# -*- coding: utf-8 -*-
"""
Project数据模型 - 轻量级项目信息模型

定义PLC项目的基础数据结构，用于UI展示和数据传递。
与src/core/project.py中的完整Project模型配合使用，
本模块提供更轻量级的视图模型。
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class ProjectModel:
    """
    项目数据模型 (轻量级)

    用于列表展示和快速访问的场景，
    不包含完整的文档树等重量级数据。
    """

    project_id: str = ""
    code: str = ""
    name: str = ""
    description: str = ""
    business_line: str = "DJ"
    status: str = "planning"
    plc_brand: str = "Codesys"
    hmi_brand: str = "Weinview"
    manager: str = ""
    created_at: str = ""
    updated_at: str = ""
    path: str = ""
    template_id: str = ""
    document_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "project_id": self.project_id,
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "business_line": self.business_line,
            "status": self.status,
            "plc_brand": self.plc_brand,
            "hmi_brand": self.hmi_brand,
            "manager": self.manager,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "path": self.path,
            "template_id": self.template_id,
            "document_count": self.document_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectModel":
        """从字典创建实例"""
        return cls(**{k: v for k, v in data.items()
                      if k in cls.__dataclass_fields__})

    @property
    def display_name(self) -> str:
        """获取显示名称 (编号 + 名称)"""
        if self.code and self.name:
            return f"[{self.code}] {self.name}"
        return self.name or self.code or "未命名项目"

    @property
    def is_active(self) -> bool:
        """检查项目是否处于活跃状态"""
        return self.status in ("active", "testing")
