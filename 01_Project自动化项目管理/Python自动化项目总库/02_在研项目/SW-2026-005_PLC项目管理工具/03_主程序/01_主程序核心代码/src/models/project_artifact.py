# -*- coding: utf-8 -*-
"""
项目资产数据模型

描述DJ单机项目中的目录、源码、文档、测试和交付类资产。
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class ProjectArtifact:
    """项目资产元数据"""

    artifact_id: str
    artifact_type: str
    name: str
    relative_path: str
    absolute_path: str
    category: str = ""
    exists: bool = True
    is_dir: bool = False
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    discovered_at: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type,
            "name": self.name,
            "relative_path": self.relative_path,
            "absolute_path": self.absolute_path,
            "category": self.category,
            "exists": self.exists,
            "is_dir": self.is_dir,
            "tags": list(self.tags),
            "metadata": dict(self.metadata),
            "discovered_at": self.discovered_at,
        }
