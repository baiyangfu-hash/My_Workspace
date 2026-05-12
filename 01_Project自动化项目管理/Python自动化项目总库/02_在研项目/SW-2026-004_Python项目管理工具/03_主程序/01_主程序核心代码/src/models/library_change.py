# -*- coding: utf-8 -*-
"""
总库变更模型
"""
from sqlalchemy import Column, String, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship

from .base import BaseModel
from src.core.constants import ChangeType, ChangeStatus

class LibraryChange(BaseModel):
    """总库变更模型"""
    __tablename__ = "library_changes"
    
    change_id = Column(String(32), unique=True, nullable=False, comment="变更ID")
    library_id = Column(String(32), ForeignKey("libraries.library_id"), nullable=False, comment="总库ID")
    change_type = Column(Enum(ChangeType), nullable=False, comment="变更类型")
    status = Column(Enum(ChangeStatus), default=ChangeStatus.PENDING, comment="变更状态")
    title = Column(String(100), nullable=False, comment="变更标题")
    description = Column(Text, comment="变更描述")
    requested_by = Column(String(50), comment="申请人")
    approved_by = Column(String(50), comment="审批人")
    impact_assessment = Column(Text, comment="影响评估")
    implementation_plan = Column(Text, comment="实施计划")
    
    # 关系
    library = relationship("Library", backref="changes")
    
    def __repr__(self) -> str:
        return f"<LibraryChange {self.change_id} {self.title}>"
