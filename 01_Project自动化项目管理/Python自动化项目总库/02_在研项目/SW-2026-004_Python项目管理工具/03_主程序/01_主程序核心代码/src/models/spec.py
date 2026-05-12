# -*- coding: utf-8 -*-
"""
规范数据模型
"""
from sqlalchemy import Column, String, Text, JSON, Boolean

from .base import BaseModel

class Spec(BaseModel):
    """规范模型"""
    __tablename__ = "specs"
    
    spec_id = Column(String(32), unique=True, nullable=False, comment="规范ID")
    name = Column(String(100), nullable=False, comment="规范名称")
    category = Column(String(50), nullable=False, comment="规范分类")
    version = Column(String(20), nullable=False, comment="版本号")
    content = Column(Text, comment="规范内容")
    check_rules = Column(JSON, default=list, comment="检查规则")
    is_active = Column(Boolean, default=True, comment="是否启用")
    
    def __repr__(self) -> str:
        return f"<Spec {self.spec_id} {self.name}>"
