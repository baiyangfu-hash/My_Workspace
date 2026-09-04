# -*- coding: utf-8 -*-
"""
任务数据访问层
"""
from typing import List, Optional

from sqlalchemy import or_

from .database import Database, db
from src.models.task import Task
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class TaskDAO:
    """任务数据访问对象"""
    
    @staticmethod
    def create(task: Task) -> Task:
        """创建任务"""
        session = db.get_session()
        try:
            session.add(task)
            session.commit()
            session.refresh(task)
            logger.info(f"任务创建成功: {task.task_id}")
            return task
        except Exception as e:
            session.rollback()
            logger.exception(f"创建任务失败: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def get_by_id(task_id: str) -> Optional[Task]:
        """根据任务ID查询"""
        session = db.get_session()
        try:
            return session.query(Task).filter(Task.task_id == task_id).first()
        finally:
            session.close()
    
    @staticmethod
    def list_by_project(project_id: str) -> List[Task]:
        """查询项目的任务列表"""
        session = db.get_session()
        try:
            return session.query(Task).filter(
                Task.project_id == project_id
            ).order_by(Task.sequence).all()
        finally:
            session.close()
    
    @staticmethod
    def list_by_milestone(milestone_id: str) -> List[Task]:
        """查询里程碑的任务列表"""
        session = db.get_session()
        try:
            return session.query(Task).filter(
                Task.milestone_id == milestone_id
            ).order_by(Task.sequence).all()
        finally:
            session.close()
    
    @staticmethod
    def list_by_parent(parent_id: str) -> List[Task]:
        """查询子任务列表"""
        session = db.get_session()
        try:
            return session.query(Task).filter(
                Task.parent_id == parent_id
            ).order_by(Task.sequence).all()
        finally:
            session.close()
    
    @staticmethod
    def update(task: Task) -> Task:
        """更新任务"""
        session = db.get_session()
        try:
            session.merge(task)
            session.commit()
            logger.info(f"任务更新成功: {task.task_id}")
            return task
        except Exception as e:
            session.rollback()
            logger.exception(f"更新任务失败: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def delete(task_id: str) -> bool:
        """删除任务"""
        session = db.get_session()
        try:
            task = session.query(Task).filter(Task.task_id == task_id).first()
            if task:
                session.delete(task)
                session.commit()
                logger.info(f"任务删除成功: {task_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.exception(f"删除任务失败: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def count_by_project(project_id: str) -> int:
        """统计项目任务数量"""
        session = db.get_session()
        try:
            return session.query(Task).filter(Task.project_id == project_id).count()
        finally:
            session.close()
