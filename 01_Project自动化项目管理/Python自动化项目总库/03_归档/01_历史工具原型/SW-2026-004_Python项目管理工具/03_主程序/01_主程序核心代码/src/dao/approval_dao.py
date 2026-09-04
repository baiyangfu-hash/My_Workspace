# -*- coding: utf-8 -*-
"""
审批历史数据访问对象
"""
from typing import List, Optional

from .database import db
from src.models.approval import ApprovalHistory
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ApprovalDAO:
    """审批历史数据访问类"""
    
    @staticmethod
    def create(approval_history: ApprovalHistory) -> ApprovalHistory:
        """创建审批历史记录"""
        with db.get_session() as session:
            session.add(approval_history)
            session.commit()
            session.refresh(approval_history)
            return approval_history
    
    @staticmethod
    def list_by_change(change_id: str) -> List[ApprovalHistory]:
        """根据变更单ID查询审批历史"""
        with db.get_session() as session:
            return session.query(ApprovalHistory).filter(
                ApprovalHistory.change_id == change_id
            ).order_by(ApprovalHistory.approved_at.asc()).all()
    
    @staticmethod
    def get_by_id(history_id: str) -> Optional[ApprovalHistory]:
        """根据历史记录ID查询"""
        with db.get_session() as session:
            return session.query(ApprovalHistory).filter(
                ApprovalHistory.history_id == history_id
            ).first()
