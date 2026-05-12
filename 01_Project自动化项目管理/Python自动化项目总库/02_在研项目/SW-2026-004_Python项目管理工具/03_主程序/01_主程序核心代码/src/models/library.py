# -*- coding: utf-8 -*-
"""
总库数据模型
"""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import BaseModel, Base

class Library(BaseModel):
    """总库模型"""
    __tablename__ = "libraries"
    
    library_id = Column(String(32), unique=True, nullable=False, comment="总库唯一ID")
    name = Column(String(100), nullable=False, comment="总库名称")
    description = Column(Text, comment="总库描述")
    root_path = Column(String(500), nullable=False, comment="总库根路径")
    status = Column(String(20), default="active", comment="总库状态")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系
    # 修复P2-#21: 添加overlaps参数解决relationship冲突警告
    projects = relationship("Project", backref="library", secondary="library_projects", overlaps="projects,library")
    categories = relationship("Category", back_populates="library", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Library {self.name}>"

class LibraryProject(Base):
    """总库与项目的关联模型"""
    __tablename__ = "library_projects"
    
    library_id = Column(String(32), ForeignKey("libraries.library_id"), primary_key=True, comment="总库ID")
    project_id = Column(String(32), ForeignKey("projects.project_id"), primary_key=True, comment="项目ID")
    added_at = Column(DateTime, default=datetime.now, comment="添加时间")
    category_id = Column(String(32), ForeignKey("categories.category_id"), comment="分类ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

class Category(BaseModel):
    """项目分类模型"""
    __tablename__ = "categories"
    
    category_id = Column(String(32), unique=True, nullable=False, comment="分类唯一ID")
    library_id = Column(String(32), ForeignKey("libraries.library_id"), nullable=False, comment="总库ID")
    name = Column(String(50), nullable=False, comment="分类名称")
    description = Column(Text, comment="分类描述")
    parent_id = Column(String(32), ForeignKey("categories.category_id"), comment="父分类ID")
    
    # 关系
    library = relationship("Library", back_populates="categories")
    parent = relationship("Category", remote_side=[category_id], backref="children")
    
    def __repr__(self) -> str:
        return f"<Category {self.name}>"
