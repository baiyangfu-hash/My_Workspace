# -*- coding: utf-8 -*-
"""
Document数据模型 - 文档元数据模型

定义工程文档的基本属性，包括类型、版本、状态等。
支持文档的版本追踪和变更历史记录。
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class DocumentModel:
    """
    文档数据模型

    描述一个工程文档的完整元信息。
    """

    doc_id: str = ""
    name: str = ""
    doc_type: str = ""              # REQ/DSN/IFC/UM 等
    version: str = "V1.0.0"
    author: str = ""
    status: str = "draft"           # draft/review/approved/released
    file_path: str = ""
    project_id: str = ""
    created_at: str = ""
    updated_at: str = ""
    content_preview: str = ""       # 前200字符预览
    word_count: int = 0
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        """后初始化处理"""
        if not self.doc_id:
            import uuid
            self.doc_id = str(uuid.uuid4())[:8]
        if not self.created_at:
            self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not self.updated_at:
            self.updated_at = self.created_at

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "doc_id": self.doc_id,
            "name": self.name,
            "doc_type": self.doc_type,
            "version": self.version,
            "author": self.author,
            "status": self.status,
            "file_path": self.file_path,
            "project_id": self.project_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "word_count": self.word_count,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentModel":
        """从字典创建实例"""
        return cls(**{k: v for k, v in data.items()
                      if k in cls.__dataclass_fields__})

    @property
    def full_name(self) -> str:
        """获取完整文件名"""
        suffix = f"_{self.version}" if self.version else ""
        return f"{self.name}{suffix}.md"

    @property
    def is_released(self) -> bool:
        """检查文档是否已发布"""
        return self.status == "released"
