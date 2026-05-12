# -*- coding: utf-8 -*-
"""
审批历史服务
"""
import uuid
from datetime import datetime
from typing import List, Optional

from src.dao.approval_dao import ApprovalDAO
from src.models.approval import ApprovalHistory
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ApprovalService:
    """审批历史服务"""
    
    @staticmethod
    def create_approval_history(
        change_id: str,
        approver: str,
        action: str,
        comment: str = ""
    ) -> Optional[ApprovalHistory]:
        """创建审批历史记录"""
        try:
            history_id = f"APR-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
            
            approval_history = ApprovalHistory(
                history_id=history_id,
                change_id=change_id,
                approver=approver,
                action=action,
                comment=comment,
                approved_at=datetime.now()
            )
            
            approval_history = ApprovalDAO.create(approval_history)
            logger.info(f"审批历史记录创建成功: {history_id}")
            return approval_history
            
        except Exception as e:
            logger.exception(f"创建审批历史记录失败: {e}")
            return None
    
    @staticmethod
    def get_approval_history(change_id: str) -> List[ApprovalHistory]:
        """获取变更单的审批历史"""
        try:
            return ApprovalDAO.list_by_change(change_id)
        except Exception as e:
            logger.exception(f"获取审批历史失败: {e}")
            return []
    
    @staticmethod
    def get_latest_approval(change_id: str) -> Optional[ApprovalHistory]:
        """获取最新的审批记录"""
        try:
            histories = ApprovalDAO.list_by_change(change_id)
            if histories:
                return histories[-1]
            return None
        except Exception as e:
            logger.exception(f"获取最新审批记录失败: {e}")
            return None
