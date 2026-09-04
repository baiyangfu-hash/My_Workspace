# -*- coding: utf-8 -*-
"""
审批历史模型
"""
from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from .base import BaseModel

class ApprovalHistory(BaseModel):
    """审批历史模型"""
    __tablename__ = "approval_histories"
    
    history_id = Column(String(32), unique=True, nullable=False, comment="历史记录ID")
    change_id = Column(String(32), ForeignKey("changes.change_id"), nullable=False, comment="变更单ID")
    approver = Column(String(50), nullable=False, comment="审批人")
    action = Column(String(20), nullable=False, comment="审批动作: approve, reject")
    comment = Column(Text, comment="审批意见")
    approved_at = Column(DateTime, comment="审批时间")
    
    # 关系
    change = relationship("Change", backref="approval_histories")
    
    def __repr__(self) -> str:
        return f"<ApprovalHistory {self.history_id} for change {self.change_id}>"
