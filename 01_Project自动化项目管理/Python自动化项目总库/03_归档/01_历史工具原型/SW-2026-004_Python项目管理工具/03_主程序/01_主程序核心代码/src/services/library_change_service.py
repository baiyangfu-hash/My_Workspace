# -*- coding: utf-8 -*-
"""
总库变更管理服务
"""
import uuid
from datetime import datetime
from typing import List, Optional, Tuple

from src.dao.library_change_dao import LibraryChangeDAO
from src.dao.library_dao import LibraryDAO
from src.models.library_change import LibraryChange
from src.core.constants import ChangeType, ChangeStatus
from src.utils.validators import validate_change_title
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class LibraryChangeService:
    """总库变更管理服务类"""
    
    @staticmethod
    def create_change(
        library_id: str,
        change_type: str,
        title: str,
        description: Optional[str] = None,
        requested_by: Optional[str] = None,
        impact_assessment: Optional[str] = None,
        implementation_plan: Optional[str] = None
    ) -> tuple[Optional[LibraryChange], str]:
        """
        创建总库变更
        
        Returns:
            (变更对象, 错误信息)，创建成功时错误信息为空
        """
        # 验证输入
        valid, msg = validate_change_title(title)
        if not valid:
            return None, msg
        
        # 验证总库是否存在
        library = LibraryDAO.get_by_id(library_id)
        if not library:
            return None, "总库不存在"
        
        # 验证变更类型
        try:
            change_type_enum = ChangeType(change_type)
        except ValueError:
            return None, f"无效的变更类型"
        
        # 创建变更ID
        change_id = f"LCHG-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
        
        # 创建变更对象
        change = LibraryChange(
            change_id=change_id,
            library_id=library_id,
            change_type=change_type_enum,
            status=ChangeStatus.PENDING,
            title=title,
            description=description,
            requested_by=requested_by,
            impact_assessment=impact_assessment,
            implementation_plan=implementation_plan
        )
        
        try:
            # 保存到数据库
            change = LibraryChangeDAO.create(change)
            logger.info(f"总库变更创建成功: {title}")
            return change, ""
            
        except Exception as e:
            logger.exception(f"创建总库变更失败: {e}")
            return None, f"创建总库变更失败: {str(e)}"
    
    @staticmethod
    def get_change(change_id: str) -> Optional[LibraryChange]:
        """获取总库变更详情"""
        return LibraryChangeDAO.get_by_id(change_id)
    
    @staticmethod
    def list_changes(
        library_id: Optional[str] = None,
        status: Optional[str] = None,
        change_type: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[LibraryChange], int]:
        """查询总库变更列表"""
        return LibraryChangeDAO.list(
            library_id=library_id,
            status=status,
            change_type=change_type,
            keyword=keyword,
            page=page,
            size=size
        )
    
    @staticmethod
    def get_recent_changes(limit: int = 10, **kwargs) -> List[LibraryChange]:
        """
        获取最近的变更列表 (兼容性方法)
        
        Args:
            limit: 返回数量限制
            **kwargs: 可选过滤条件 (library_id, status, change_type)
            
        Returns:
            变更对象列表
        """
        changes, _ = LibraryChangeService.list_changes(
            page=1,
            size=limit,
            **kwargs
        )
        return changes
    
    @staticmethod
    def update_change(change_id: str, data: dict) -> tuple[Optional[LibraryChange], str]:
        """更新总库变更信息"""
        # 验证输入
        if "title" in data:
            valid, msg = validate_change_title(data["title"])
            if not valid:
                return None, msg
        
        try:
            change = LibraryChangeDAO.update(change_id, data)
            if not change:
                return None, "变更不存在"
            
            logger.info(f"总库变更更新成功: {change.change_id}")
            return change, ""
            
        except Exception as e:
            logger.exception(f"更新总库变更失败: {e}")
            return None, f"更新总库变更失败: {str(e)}"
    
    @staticmethod
    def delete_change(change_id: str) -> tuple[bool, str]:
        """删除总库变更"""
        try:
            # 先获取变更信息
            change = LibraryChangeDAO.get_by_id(change_id)
            if not change:
                return False, "变更不存在"
            
            # 检查状态，只有待审批的变更可以删除
            if change.status != ChangeStatus.PENDING:
                return False, "只有待审批的变更可以删除"
            
            # 删除数据库记录
            success = LibraryChangeDAO.delete(change_id)
            if not success:
                return False, "删除数据库记录失败"
            
            logger.info(f"总库变更已删除: {change_id}")
            return True, ""
            
        except Exception as e:
            logger.exception(f"删除总库变更失败: {e}")
            return False, f"删除总库变更失败: {str(e)}"
    
    @staticmethod
    def approve_change(change_id: str, approved_by: str, comments: Optional[str] = None) -> tuple[bool, str]:
        """审批总库变更"""
        try:
            # 获取变更信息
            change = LibraryChangeDAO.get_by_id(change_id)
            if not change:
                return False, "变更不存在"
            
            # 检查状态
            if change.status != ChangeStatus.PENDING:
                return False, "只有待审批的变更可以审批"
            
            # 更新状态
            data = {
                "status": ChangeStatus.APPROVED,
                "approved_by": approved_by
            }
            if comments:
                data["implementation_plan"] = (change.implementation_plan or "") + f"\n\n审批意见: {comments}"
            
            change = LibraryChangeDAO.update(change_id, data)
            if not change:
                return False, "更新变更状态失败"
            
            logger.info(f"总库变更已审批: {change_id}")
            return True, ""
            
        except Exception as e:
            logger.exception(f"审批总库变更失败: {e}")
            return False, f"审批总库变更失败: {str(e)}"
    
    @staticmethod
    def reject_change(change_id: str, rejected_by: str, comments: Optional[str] = None) -> tuple[bool, str]:
        """拒绝总库变更"""
        try:
            # 获取变更信息
            change = LibraryChangeDAO.get_by_id(change_id)
            if not change:
                return False, "变更不存在"
            
            # 检查状态
            if change.status != ChangeStatus.PENDING:
                return False, "只有待审批的变更可以拒绝"
            
            # 更新状态
            data = {
                "status": ChangeStatus.REJECTED,
                "approved_by": rejected_by
            }
            if comments:
                data["implementation_plan"] = (change.implementation_plan or "") + f"\n\n拒绝原因: {comments}"
            
            change = LibraryChangeDAO.update(change_id, data)
            if not change:
                return False, "更新变更状态失败"
            
            logger.info(f"总库变更已拒绝: {change_id}")
            return True, ""
            
        except Exception as e:
            logger.exception(f"拒绝总库变更失败: {e}")
            return False, f"拒绝总库变更失败: {str(e)}"
    
    @staticmethod
    def get_change_statistics(library_id: Optional[str] = None) -> dict:
        """获取总库变更统计信息"""
        try:
            total = LibraryChangeDAO.count_by_status(library_id)
            pending = LibraryChangeDAO.count_by_status(library_id, ChangeStatus.PENDING)
            approved = LibraryChangeDAO.count_by_status(library_id, ChangeStatus.APPROVED)
            rejected = LibraryChangeDAO.count_by_status(library_id, ChangeStatus.REJECTED)
            implemented = LibraryChangeDAO.count_by_status(library_id, ChangeStatus.IMPLEMENTED)
            
            return {
                "total": total,
                "pending": pending,
                "approved": approved,
                "rejected": rejected,
                "implemented": implemented
            }
        except Exception as e:
            logger.exception(f"获取总库变更统计信息失败: {e}")
            return {}
