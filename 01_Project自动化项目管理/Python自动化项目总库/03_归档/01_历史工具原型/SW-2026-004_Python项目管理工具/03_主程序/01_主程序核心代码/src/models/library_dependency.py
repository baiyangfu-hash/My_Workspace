# -*- coding: utf-8 -*-
"""
总库依赖模型
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import BaseModel

class LibraryDependency(BaseModel):
    """总库依赖模型"""
    __tablename__ = "library_dependencies"
    
    dependency_id = Column(String(32), unique=True, nullable=False, comment="依赖唯一ID")
    library_id = Column(String(32), ForeignKey("libraries.library_id"), nullable=False, comment="总库ID")
    project_id = Column(String(32), ForeignKey("projects.project_id"), nullable=False, comment="项目ID")
    dependency_project_id = Column(String(32), ForeignKey("projects.project_id"), nullable=False, comment="依赖项目ID")
    dependency_type = Column(String(20), default="runtime", comment="依赖类型")
    version_constraint = Column(String(50), comment="版本约束")
    description = Column(Text, comment="依赖描述")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系
    library = relationship("Library", backref="dependencies")
    project = relationship("Project", foreign_keys=[project_id], backref="dependencies")
    dependency_project = relationship("Project", foreign_keys=[dependency_project_id], backref="dependents")
    
    def __repr__(self) -> str:
        return f"<LibraryDependency {self.project_id} -> {self.dependency_project_id}>"
