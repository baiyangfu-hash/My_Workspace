# -*- coding: utf-8 -*-
"""
任务数据模型
"""
from sqlalchemy import Column, String, Text, Date, Integer, ForeignKey
from sqlalchemy.orm import relationship

from .base import BaseModel

class Task(BaseModel):
    """任务模型"""
    __tablename__ = "tasks"
    
    task_id = Column(String(32), unique=True, nullable=False, comment="任务ID")
    project_id = Column(String(32), ForeignKey("projects.project_id"), nullable=False, comment="所属项目ID")
    milestone_id = Column(String(32), ForeignKey("milestones.milestone_id"), comment="所属里程碑ID")
    parent_id = Column(String(32), ForeignKey("tasks.task_id"), comment="父任务ID")
    name = Column(String(100), nullable=False, comment="任务名称")
    description = Column(Text, comment="描述")
    assignee = Column(String(50), comment="负责人")
    start_date = Column(Date, comment="开始日期")
    end_date = Column(Date, comment="结束日期")
    status = Column(String(20), default="pending", comment="状态: pending/in_progress/completed/delayed")
    progress = Column(Integer, default=0, comment="进度百分比")
    priority = Column(String(10), default="medium", comment="优先级: high/medium/low")
    sequence = Column(Integer, default=0, comment="排序序号")
    
    project = relationship("Project", backref="tasks")
    milestone = relationship("Milestone", backref="tasks")
    
    def __repr__(self) -> str:
        return f"<Task {self.task_id} {self.name}>"
