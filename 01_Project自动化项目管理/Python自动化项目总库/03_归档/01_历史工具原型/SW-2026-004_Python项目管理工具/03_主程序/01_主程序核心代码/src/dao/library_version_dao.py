# -*- coding: utf-8 -*-
"""
总库版本数据访问对象
"""
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, or_, desc
import uuid
from datetime import datetime

from src.models.library_version import LibraryVersion, LibraryVersionProject
from src.dao.database import Database

class LibraryVersionDAO:
    """总库版本数据访问类"""
    
    @staticmethod
    def create(version: LibraryVersion) -> LibraryVersion:
        """创建总库版本"""
        session = Database.get_session()
        try:
            session.add(version)
            session.commit()
            session.refresh(version)
            return version
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def get_by_id(version_id: str) -> Optional[LibraryVersion]:
        """根据ID获取总库版本"""
        session = Database.get_session()
        try:
            return session.query(LibraryVersion).filter_by(version_id=version_id).first()
        finally:
            session.close()
    
    @staticmethod
    def get_by_library_and_version(library_id: str, version_number: str) -> Optional[LibraryVersion]:
        """根据总库ID和版本号获取总库版本"""
        session = Database.get_session()
        try:
            return session.query(LibraryVersion).filter_by(
                library_id=library_id,
                version_number=version_number
            ).first()
        finally:
            session.close()
    
    @staticmethod
    def list(
        library_id: Optional[str] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[LibraryVersion], int]:
        """查询总库版本列表"""
        session = Database.get_session()
        try:
            query = session.query(LibraryVersion)
            
            if library_id:
                query = query.filter_by(library_id=library_id)
            
            if status:
                query = query.filter_by(status=status)
            
            if keyword:
                query = query.filter(
                    or_(
                        LibraryVersion.version_number.like(f"%{keyword}%"),
                        LibraryVersion.description.like(f"%{keyword}%")
                    )
                )
            
            total = query.count()
            
            versions = query.order_by(desc(LibraryVersion.created_at))\
                .offset((page - 1) * size)\
                .limit(size)\
                .all()
            
            return versions, total
        finally:
            session.close()
    
    @staticmethod
    def update(version_id: str, data: dict) -> Optional[LibraryVersion]:
        """更新总库版本信息"""
        session = Database.get_session()
        try:
            version = session.query(LibraryVersion).filter_by(version_id=version_id).first()
            if not version:
                return None
            
            for key, value in data.items():
                setattr(version, key, value)
            
            session.commit()
            session.refresh(version)
            return version
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def delete(version_id: str) -> bool:
        """删除总库版本"""
        session = Database.get_session()
        try:
            # 先删除关联的项目
            session.query(LibraryVersionProject).filter_by(version_id=version_id).delete()
            
            # 再删除版本
            result = session.query(LibraryVersion).filter_by(version_id=version_id).delete()
            session.commit()
            return result > 0
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def add_project(version_id: str, project_id: str, project_version: Optional[str] = None) -> bool:
        """向总库版本添加项目"""
        session = Database.get_session()
        try:
            # 检查是否已存在
            existing = session.query(LibraryVersionProject).filter_by(
                version_id=version_id,
                project_id=project_id
            ).first()
            
            if existing:
                return True
            
            # 创建关联
            association = LibraryVersionProject(
                id=f"LVP-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}",
                version_id=version_id,
                project_id=project_id,
                project_version=project_version
            )
            
            session.add(association)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def remove_project(version_id: str, project_id: str) -> bool:
        """从总库版本移除项目"""
        session = Database.get_session()
        try:
            result = session.query(LibraryVersionProject).filter_by(
                version_id=version_id,
                project_id=project_id
            ).delete()
            session.commit()
            return result > 0
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def list_version_projects(version_id: str) -> List[LibraryVersionProject]:
        """获取总库版本包含的项目列表"""
        session = Database.get_session()
        try:
            return session.query(LibraryVersionProject).filter_by(version_id=version_id).all()
        finally:
            session.close()
    
    @staticmethod
    def count_by_library(library_id: str) -> int:
        """统计总库的版本数量"""
        session = Database.get_session()
        try:
            return session.query(LibraryVersion).filter_by(library_id=library_id).count()
        finally:
            session.close()
    
    @staticmethod
    def get_latest_version(library_id: str) -> Optional[LibraryVersion]:
        """获取总库的最新版本"""
        session = Database.get_session()
        try:
            return session.query(LibraryVersion)\
                .filter_by(library_id=library_id)\
                .order_by(desc(LibraryVersion.created_at))\
                .first()
        finally:
            session.close()
