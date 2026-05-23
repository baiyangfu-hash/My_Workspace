# -*- coding: utf-8 -*-
"""
变更请求数据模型

作为变更管理服务的轻量级领域对象，描述单张变更单的核心字段。
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List

from src.core.constants import ChangeStatus


@dataclass
class ChangeRequest:
    """变更请求"""

    change_id: str
    category: str
    title: str
    project_path: str
    status: str = field(default_factory=lambda: ChangeStatus.DRAFT.value)
    description: str = ""
    affected_paths: List[str] = field(default_factory=list)
    created_at: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    def to_dict(self) -> Dict[str, object]:
        """转换为字典"""
        return {
            "change_id": self.change_id,
            "category": self.category,
            "title": self.title,
            "project_path": self.project_path,
            "status": self.status,
            "description": self.description,
            "affected_paths": list(self.affected_paths),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
