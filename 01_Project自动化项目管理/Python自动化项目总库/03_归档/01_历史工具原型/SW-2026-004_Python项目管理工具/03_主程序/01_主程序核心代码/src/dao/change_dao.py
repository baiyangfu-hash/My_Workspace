# -*- coding: utf-8 -*-
"""
变更记录数据访问对象
"""
from typing import List, Optional, Tuple

from .database import db
from src.models.change import Change
from src.core.constants import ChangeStatus, Domain, Nature, Scope
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ChangeDAO:
    """变更数据访问类"""
    
    @staticmethod
    def create(change: Change) -> Change:
        """创建变更单"""
        with db.get_session() as session:
            session.add(change)
            session.commit()
            session.refresh(change)
            return change
    
    @staticmethod
    def get_by_id(change_id: str) -> Optional[Change]:
        """根据变更单ID查询"""
        with db.get_session() as session:
            return session.query(Change).filter(Change.change_id == change_id).first()
    
    @staticmethod
    def list_by_project(
        project_id: str,
        status: Optional[ChangeStatus] = None,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[Change], int]:
        """查询项目的变更单列表"""
        with db.get_session() as session:
            query = session.query(Change).filter(Change.project_id == project_id)
            
            if status:
                query = query.filter(Change.status == status)
            
            total = query.count()
            offset = (page - 1) * size
            changes = query.order_by(Change.created_at.desc()).offset(offset).limit(size).all()
            
            return changes, total
    
    @staticmethod
    def update(change_id: str, data: dict) -> Optional[Change]:
        """更新变更单信息"""
        with db.get_session() as session:
            change = session.query(Change).filter(Change.change_id == change_id).first()
            if not change:
                return None
            
            change.update_from_dict(data)
            session.commit()
            session.refresh(change)
            return change
    
    @staticmethod
    def update_status(change_id: str, status: ChangeStatus, approver: Optional[str] = None) -> bool:
        """更新变更状态"""
        with db.get_session() as session:
            change = session.query(Change).filter(Change.change_id == change_id).first()
            if not change:
                return False
            
            change.status = status
            if approver and status in [ChangeStatus.APPROVED, ChangeStatus.REJECTED]:
                change.approver = approver
            
            session.commit()
            return True
    
    @staticmethod
    def delete(change_id: str) -> bool:
        """删除变更单"""
        with db.get_session() as session:
            change = session.query(Change).filter(Change.change_id == change_id).first()
            if not change or change.status != ChangeStatus.DRAFT:  # 只有草稿可以删除
                return False
            
            session.delete(change)
            session.commit()
            return True
    
    @staticmethod
    def count_by_project(project_id: str, status: Optional[ChangeStatus] = None) -> int:
        """统计项目的变更单数量"""
        with db.get_session() as session:
            query = session.query(Change).filter(Change.project_id == project_id)
            if status:
                query = query.filter(Change.status == status)
            return query.count()
    
    @staticmethod
    def get_by_date_range(project_id: str, start_date, end_date) -> List[Change]:
        """根据日期范围获取变更"""
        with db.get_session() as session:
            return session.query(Change).filter(
                Change.project_id == project_id,
                Change.created_at >= start_date,
                Change.created_at <= end_date
            ).all()
    
    @staticmethod
    def get_statistics(project_id: str) -> dict:
        """V2.1.0: 获取变更统计信息 (4D: status + domain + nature + scope)"""
        with db.get_session() as session:
            query = session.query(Change).filter(Change.project_id == project_id)
            total = query.count()

            result = {"total": total}

            # 按状态统计 (原有)
            for status in ChangeStatus:
                result[status.value] = query.filter(Change.status == status).count()

            # V2.1.0: 按领域统计 (新增)
            for domain in Domain:
                result[f"domain_{domain.value}"] = query.filter(Change.domain == domain).count()

            # V2.1.0: 按性质统计 (新增)
            for nature in Nature:
                result[f"nature_{nature.value}"] = query.filter(Change.nature == nature).count()

            # V2.1.0: 按范围统计 (新增)
            for scope in Scope:
                result[f"scope_{scope.value}"] = query.filter(Change.scope == scope).count()

            return result

    @staticmethod
    def list_by_domain(project_id: str, domain: Domain) -> List[Change]:
        """V2.1.0: 按技术领域查询"""
        with db.get_session() as session:
            return session.query(Change).filter(
                Change.project_id == project_id,
                Change.domain == domain
            ).order_by(Change.created_at.desc()).all()

    @staticmethod
    def list_by_nature(project_id: str, nature: Nature) -> List[Change]:
        """V2.1.0: 按业务性质查询"""
        with db.get_session() as session:
            return session.query(Change).filter(
                Change.project_id == project_id,
                Change.nature == nature
            ).order_by(Change.created_at.desc()).all()

    @staticmethod
    def list_by_scope(project_id: str, scope: Scope) -> List[Change]:
        """V2.1.0: 按影响范围查询"""
        with db.get_session() as session:
            return session.query(Change).filter(
                Change.project_id == project_id,
                Change.scope == scope
            ).order_by(Change.created_at.desc()).all()

    @staticmethod
    def find_propagation_chain(change_id: str) -> List[Change]:
        """V2.1.0: 查找某变更的所有关联变更 (通过related_changes字段)"""
        with db.get_session() as session:
            change = session.query(Change).filter(Change.change_id == change_id).first()
            if not change or not change.related_changes:
                return []

            related_ids = change.related_changes
            return session.query(Change).filter(
                Change.change_id.in_(related_ids)
            ).all()
    
    @staticmethod
    def count_by_type(project_id: str) -> dict:
        """按类型统计变更"""
        with db.get_session() as session:
            query = session.query(Change).filter(Change.project_id == project_id)
            types = session.query(Change.type).distinct().all()
            result = {}
            for (change_type,) in types:
                result[change_type] = query.filter(Change.type == change_type).count()
            return result
    
    @staticmethod
    def count_by_status(project_id: str) -> dict:
        """按状态统计变更"""
        with db.get_session() as session:
            query = session.query(Change).filter(Change.project_id == project_id)
            result = {}
            for status in ChangeStatus:
                result[status.value] = query.filter(Change.status == status).count()
            return result
