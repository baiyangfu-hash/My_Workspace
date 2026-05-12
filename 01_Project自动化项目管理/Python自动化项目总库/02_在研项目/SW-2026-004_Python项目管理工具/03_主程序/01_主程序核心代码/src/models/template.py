# -*- coding: utf-8 -*-
"""
模板数据模型
"""
from sqlalchemy import Column, String, Text, Boolean, JSON

from .base import BaseModel

class Template(BaseModel):
    """项目模板模型"""
    __tablename__ = "templates"
    
    template_id = Column(String(32), unique=True, nullable=False, comment="模板ID")
    name = Column(String(100), nullable=False, comment="模板名称")
    version = Column(String(20), nullable=False, comment="版本号")
    compiler = Column(String(50), comment="适用编译器/平台")
    scene = Column(String(100), comment="适用场景")
    description = Column(Text, comment="模板描述")
    structure = Column(JSON, nullable=False, comment="目录结构定义")
    templates = Column(JSON, default=list, comment="模板文件映射")
    is_builtin = Column(Boolean, default=False, comment="是否内置模板")
    is_active = Column(Boolean, default=True, comment="是否可用")
    business_lines = Column(JSON, default=list, comment="适用业务线")
    
    def __repr__(self) -> str:
        return f"<Template {self.template_id} {self.name}>"
