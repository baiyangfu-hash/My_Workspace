# -*- coding: utf-8 -*-
"""
里程碑数据模型
"""
from sqlalchemy import Column, String, Text, Date, Integer, ForeignKey
from sqlalchemy.orm import relationship

from .base import BaseModel

class Milestone(BaseModel):
    """里程碑模型"""
    __tablename__ = "milestones"
    
    milestone_id = Column(String(32), unique=True, nullable=False, comment="里程碑ID")
    project_id = Column(String(32), ForeignKey("projects.project_id"), nullable=False, comment="所属项目ID")
    name = Column(String(100), nullable=False, comment="里程碑名称")
    description = Column(Text, comment="描述")
    start_date = Column(Date, comment="开始日期")
    end_date = Column(Date, comment="结束日期")
    status = Column(String(20), default="pending", comment="状态: pending/in_progress/completed/delayed")
    progress = Column(Integer, default=0, comment="进度百分比")
    sequence = Column(Integer, default=0, comment="排序序号")
    
    project = relationship("Project", backref="milestones")
    
    def __repr__(self) -> str:
        return f"<Milestone {self.milestone_id} {self.name}>"
