# -*- coding: utf-8 -*-
"""
总库版本模型
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import BaseModel

class LibraryVersion(BaseModel):
    """总库版本模型"""
    __tablename__ = "library_versions"
    
    version_id = Column(String(32), unique=True, nullable=False, comment="版本唯一ID")
    library_id = Column(String(32), ForeignKey("libraries.library_id"), nullable=False, comment="总库ID")
    version_number = Column(String(20), nullable=False, comment="版本号")
    description = Column(Text, comment="版本描述")
    status = Column(String(20), default="draft", comment="版本状态")
    created_by = Column(String(50), comment="创建人")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系
    library = relationship("Library", backref="versions")
    
    def __repr__(self) -> str:
        return f"<LibraryVersion {self.version_number}>"

class LibraryVersionProject(BaseModel):
    """总库版本与项目的关联模型"""
    __tablename__ = "library_version_projects"
    
    id = Column(String(32), primary_key=True, comment="主键ID")
    version_id = Column(String(32), ForeignKey("library_versions.version_id"), nullable=False, comment="版本ID")
    project_id = Column(String(32), ForeignKey("projects.project_id"), nullable=False, comment="项目ID")
    project_version = Column(String(20), comment="项目版本")
    added_at = Column(DateTime, default=datetime.now, comment="添加时间")
