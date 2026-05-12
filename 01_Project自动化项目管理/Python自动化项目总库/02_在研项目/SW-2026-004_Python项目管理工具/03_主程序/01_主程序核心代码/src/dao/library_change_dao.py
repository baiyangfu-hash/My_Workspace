# -*- coding: utf-8 -*-
"""
总库变更数据访问对象
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import and_, or_

from src.models.library_change import LibraryChange
from src.models.library import Library
from src.dao.database import Database
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class LibraryChangeDAO:
    """总库变更数据访问类"""
    
    @staticmethod
    def get_session() -> Session:
        """获取数据库会话"""
        db = Database()
        return db.get_session()
    
    @staticmethod
    def create(change: LibraryChange) -> LibraryChange:
        """创建总库变更"""
        session = LibraryChangeDAO.get_session()
        try:
            session.add(change)
            session.commit()
            session.refresh(change)
            return change
        except Exception as e:
            session.rollback()
            logger.exception(f"创建总库变更失败: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def get_by_id(change_id: str) -> Optional[LibraryChange]:
        """根据ID获取总库变更"""
        session = LibraryChangeDAO.get_session()
        try:
            return session.query(LibraryChange).filter(LibraryChange.change_id == change_id).first()
        finally:
            session.close()
    
    @staticmethod
    def list(
        library_id: Optional[str] = None,
        status: Optional[str] = None,
        change_type: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[LibraryChange], int]:
        """查询总库变更列表"""
        session = LibraryChangeDAO.get_session()
        try:
            query = session.query(LibraryChange)
            
            if library_id:
                query = query.filter(LibraryChange.library_id == library_id)
            
            if status:
                query = query.filter(LibraryChange.status == status)
            
            if change_type:
                query = query.filter(LibraryChange.change_type == change_type)
            
            if keyword:
                query = query.filter(
                    or_(
                        LibraryChange.title.like(f"%{keyword}%"),
                        LibraryChange.description.like(f"%{keyword}%")
                    )
                )
            
            total = query.count()
            changes = query.order_by(LibraryChange.created_at.desc()).offset((page - 1) * size).limit(size).all()
            
            return changes, total
        finally:
            session.close()
    
    @staticmethod
    def update(change_id: str, data: dict) -> Optional[LibraryChange]:
        """更新总库变更信息"""
        session = LibraryChangeDAO.get_session()
        try:
            change = session.query(LibraryChange).filter(LibraryChange.change_id == change_id).first()
            if not change:
                return None
            
            for key, value in data.items():
                setattr(change, key, value)
            
            session.commit()
            session.refresh(change)
            return change
        except Exception as e:
            session.rollback()
            logger.exception(f"更新总库变更失败: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def delete(change_id: str) -> bool:
        """删除总库变更"""
        session = LibraryChangeDAO.get_session()
        try:
            change = session.query(LibraryChange).filter(LibraryChange.change_id == change_id).first()
            if not change:
                return False
            
            session.delete(change)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.exception(f"删除总库变更失败: {e}")
            return False
        finally:
            session.close()
    
    @staticmethod
    def count_by_status(library_id: Optional[str] = None, status: Optional[str] = None) -> int:
        """统计总库变更数量"""
        session = LibraryChangeDAO.get_session()
        try:
            query = session.query(LibraryChange)
            
            if library_id:
                query = query.filter(LibraryChange.library_id == library_id)
            
            if status:
                query = query.filter(LibraryChange.status == status)
            
            return query.count()
        finally:
            session.close()
