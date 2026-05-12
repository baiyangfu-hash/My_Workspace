# -*- coding: utf-8 -*-
"""
里程碑数据访问层
"""
from typing import List, Optional

from sqlalchemy import or_

from .database import Database, db
from src.models.milestone import Milestone
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class MilestoneDAO:
    """里程碑数据访问对象"""
    
    @staticmethod
    def create(milestone: Milestone) -> Milestone:
        """创建里程碑"""
        session = db.get_session()
        try:
            session.add(milestone)
            session.commit()
            session.refresh(milestone)
            logger.info(f"里程碑创建成功: {milestone.milestone_id}")
            return milestone
        except Exception as e:
            session.rollback()
            logger.exception(f"创建里程碑失败: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def get_by_id(milestone_id: str) -> Optional[Milestone]:
        """根据里程碑ID查询"""
        session = db.get_session()
        try:
            return session.query(Milestone).filter(Milestone.milestone_id == milestone_id).first()
        finally:
            session.close()
    
    @staticmethod
    def list_by_project(project_id: str) -> List[Milestone]:
        """查询项目的里程碑列表"""
        session = db.get_session()
        try:
            return session.query(Milestone).filter(
                Milestone.project_id == project_id
            ).order_by(Milestone.sequence).all()
        finally:
            session.close()
    
    @staticmethod
    def update(milestone: Milestone) -> Milestone:
        """更新里程碑"""
        session = db.get_session()
        try:
            session.merge(milestone)
            session.commit()
            logger.info(f"里程碑更新成功: {milestone.milestone_id}")
            return milestone
        except Exception as e:
            session.rollback()
            logger.exception(f"更新里程碑失败: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def delete(milestone_id: str) -> bool:
        """删除里程碑"""
        session = db.get_session()
        try:
            milestone = session.query(Milestone).filter(Milestone.milestone_id == milestone_id).first()
            if milestone:
                session.delete(milestone)
                session.commit()
                logger.info(f"里程碑删除成功: {milestone_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.exception(f"删除里程碑失败: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def count_by_project(project_id: str) -> int:
        """统计项目里程碑数量"""
        session = db.get_session()
        try:
            return session.query(Milestone).filter(Milestone.project_id == project_id).count()
        finally:
            session.close()
