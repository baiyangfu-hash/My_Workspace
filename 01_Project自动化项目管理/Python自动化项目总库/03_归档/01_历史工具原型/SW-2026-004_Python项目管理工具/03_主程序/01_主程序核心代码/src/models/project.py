# -*- coding: utf-8 -*-
"""
项目数据模型
"""
from sqlalchemy import Column, String, Text, Enum, Integer, DateTime
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import BaseModel, SafeJSON
from src.core.constants import ProjectStatus, BusinessLine

class Project(BaseModel):
    """项目模型"""
    __tablename__ = "projects"
    
    project_id = Column(String(32), unique=True, nullable=False, comment="项目唯一ID")
    code = Column(String(32), unique=True, nullable=False, comment="项目编号")
    name = Column(String(100), nullable=False, comment="项目名称")
    business_line = Column(Enum(BusinessLine), nullable=False, comment="业务线类型")
    template_id = Column(String(32), nullable=False, comment="模板ID")
    manager = Column(String(50), comment="项目负责人")
    status = Column(Enum(ProjectStatus), default=ProjectStatus.ACTIVE, comment="项目状态")
    description = Column(Text, comment="项目描述")
    path = Column(String(500), nullable=False, comment="项目本地路径")
    sequence = Column(Integer, nullable=False, comment="当年序号")
    document_specs = Column(SafeJSON, default=lambda: {}, comment="文档规范追踪 {file_path: {spec_id, spec_version, updated_at}}")
    applied_template_version = Column(String(20), comment="创建时应用的模板版本")
    
    # 关系
    # 修复P2-#21: 添加overlaps参数解决relationship冲突警告
    libraries = relationship("Library", backref="project", secondary="library_projects", overlaps="projects")
    
    @hybrid_property
    def full_name(self) -> str:
        """项目全称"""
        return f"{self.code}_{self.name}"

    @hybrid_property
    def safe_document_specs(self) -> dict:
        """安全获取 document_specs，确保返回字典类型（兼容旧数据）"""
        if self.document_specs is None:
            return {}
        if isinstance(self.document_specs, dict):
            return self.document_specs
        # 处理空字符串或其他异常情况
        if isinstance(self.document_specs, str) and not self.document_specs.strip():
            return {}
        try:
            import json
            return json.loads(self.document_specs) if isinstance(self.document_specs, str) else dict(self.document_specs)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def __repr__(self) -> str:
        return f"<Project {self.code} {self.name}>"
