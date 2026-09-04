# -*- coding: utf-8 -*-
"""
缺陷DAO
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.models.defect import Defect, DefectStatus
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class DefectDAO:
    """缺陷数据访问对象"""
    
    @staticmethod
    def create(session: Session, defect_data: dict) -> Defect:
        """创建缺陷"""
        try:
            defect = Defect(**defect_data)
            session.add(defect)
            session.commit()
            session.refresh(defect)
            logger.info(f"创建缺陷成功: {defect.id}")
            return defect
        except Exception as e:
            session.rollback()
            logger.error(f"创建缺陷失败: {e}")
            raise
    
    @staticmethod
    def get_by_id(session: Session, defect_id: int) -> Optional[Defect]:
        """根据ID获取缺陷"""
        return session.query(Defect).filter(Defect.id == defect_id).first()
    
    @staticmethod
    def get_all(session: Session, **filters) -> List[Defect]:
        """获取所有缺陷"""
        query = session.query(Defect)
        
        # 应用过滤条件
        if filters.get('status'):
            query = query.filter(Defect.status == filters['status'])
        if filters.get('priority'):
            query = query.filter(Defect.priority == filters['priority'])
        if filters.get('severity'):
            query = query.filter(Defect.severity == filters['severity'])
        if filters.get('project_id'):
            query = query.filter(Defect.project_id == filters['project_id'])
        if filters.get('library_id'):
            query = query.filter(Defect.library_id == filters['library_id'])
        if filters.get('reporter'):
            query = query.filter(Defect.reporter == filters['reporter'])
        if filters.get('assignee'):
            query = query.filter(Defect.assignee == filters['assignee'])
        if filters.get('keyword'):
            keyword = f"%{filters['keyword']}%"
            query = query.filter(
                or_(
                    Defect.title.like(keyword),
                    Defect.description.like(keyword),
                    Defect.steps_to_reproduce.like(keyword)
                )
            )
        
        # 排序
        query = query.order_by(Defect.created_at.desc())
        
        return query.all()
    
    @staticmethod
    def update(session: Session, defect_id: int, update_data: dict) -> Optional[Defect]:
        """更新缺陷"""
        try:
            defect = session.query(Defect).filter(Defect.id == defect_id).first()
            if defect:
                defect.update_from_dict(update_data)
                session.commit()
                session.refresh(defect)
                logger.info(f"更新缺陷成功: {defect_id}")
                return defect
            return None
        except Exception as e:
            session.rollback()
            logger.error(f"更新缺陷失败: {e}")
            raise
    
    @staticmethod
    def delete(session: Session, defect_id: int) -> bool:
        """删除缺陷"""
        try:
            defect = session.query(Defect).filter(Defect.id == defect_id).first()
            if defect:
                session.delete(defect)
                session.commit()
                logger.info(f"删除缺陷成功: {defect_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"删除缺陷失败: {e}")
            raise
    
    @staticmethod
    def get_statistics(session: Session) -> dict:
        """获取缺陷统计信息"""
        try:
            total = session.query(Defect).count()
            open_count = session.query(Defect).filter(Defect.status == DefectStatus.OPEN).count()
            in_progress_count = session.query(Defect).filter(Defect.status == DefectStatus.IN_PROGRESS).count()
            fixed_count = session.query(Defect).filter(Defect.status == DefectStatus.FIXED).count()
            verified_count = session.query(Defect).filter(Defect.status == DefectStatus.VERIFIED).count()
            closed_count = session.query(Defect).filter(Defect.status == DefectStatus.CLOSED).count()
            rejected_count = session.query(Defect).filter(Defect.status == DefectStatus.REJECTED).count()
            
            return {
                'total': total,
                'open': open_count,
                'in_progress': in_progress_count,
                'fixed': fixed_count,
                'verified': verified_count,
                'closed': closed_count,
                'rejected': rejected_count
            }
        except Exception as e:
            logger.error(f"获取缺陷统计失败: {e}")
            return {}
