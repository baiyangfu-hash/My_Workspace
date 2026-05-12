# -*- coding: utf-8 -*-
"""
影响评估模型
"""
from sqlalchemy import Column, String, Text, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship

from .base import BaseModel
from src.core.constants import ImpactLevel

class ImpactAssessment(BaseModel):
    """影响评估模型"""
    __tablename__ = "impact_assessments"
    
    assessment_id = Column(String(32), unique=True, nullable=False, comment="评估ID")
    change_id = Column(String(32), ForeignKey("changes.change_id"), nullable=False, comment="变更单ID")
    affected_components = Column(JSON, default=list, comment="受影响的组件")
    risk_level = Column(Enum(ImpactLevel), default=ImpactLevel.LOW, comment="风险等级")
    mitigation_plan = Column(Text, comment="缓解措施")
    
    # 关系
    change = relationship("Change", backref="impact_assessment")
    
    def __repr__(self) -> str:
        return f"<ImpactAssessment {self.assessment_id} for change {self.change_id}>"
