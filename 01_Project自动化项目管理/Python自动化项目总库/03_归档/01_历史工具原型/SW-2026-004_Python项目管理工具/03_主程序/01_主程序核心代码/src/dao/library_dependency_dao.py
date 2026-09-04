# -*- coding: utf-8 -*-
"""
总库依赖数据访问对象
"""
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, or_, desc
import uuid
from datetime import datetime

from src.models.library_dependency import LibraryDependency
from src.dao.database import Database

class LibraryDependencyDAO:
    """总库依赖数据访问类"""
    
    @staticmethod
    def create(dependency: LibraryDependency) -> LibraryDependency:
        """创建总库依赖"""
        session = Database.get_session()
        try:
            session.add(dependency)
            session.commit()
            session.refresh(dependency)
            return dependency
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def get_by_id(dependency_id: str) -> Optional[LibraryDependency]:
        """根据ID获取总库依赖"""
        session = Database.get_session()
        try:
            return session.query(LibraryDependency).filter_by(dependency_id=dependency_id).first()
        finally:
            session.close()
    
    @staticmethod
    def get_by_projects(library_id: str, project_id: str, dependency_project_id: str) -> Optional[LibraryDependency]:
        """根据总库ID、项目ID和依赖项目ID获取依赖关系"""
        session = Database.get_session()
        try:
            return session.query(LibraryDependency).filter_by(
                library_id=library_id,
                project_id=project_id,
                dependency_project_id=dependency_project_id
            ).first()
        finally:
            session.close()
    
    @staticmethod
    def list(
        library_id: Optional[str] = None,
        project_id: Optional[str] = None,
        dependency_project_id: Optional[str] = None,
        dependency_type: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[LibraryDependency], int]:
        """查询总库依赖列表"""
        session = Database.get_session()
        try:
            query = session.query(LibraryDependency)
            
            if library_id:
                query = query.filter_by(library_id=library_id)
            
            if project_id:
                query = query.filter_by(project_id=project_id)
            
            if dependency_project_id:
                query = query.filter_by(dependency_project_id=dependency_project_id)
            
            if dependency_type:
                query = query.filter_by(dependency_type=dependency_type)
            
            total = query.count()
            
            dependencies = query.order_by(desc(LibraryDependency.created_at))\
                .offset((page - 1) * size)\
                .limit(size)\
                .all()
            
            return dependencies, total
        finally:
            session.close()
    
    @staticmethod
    def update(dependency_id: str, data: dict) -> Optional[LibraryDependency]:
        """更新总库依赖信息"""
        session = Database.get_session()
        try:
            dependency = session.query(LibraryDependency).filter_by(dependency_id=dependency_id).first()
            if not dependency:
                return None
            
            for key, value in data.items():
                setattr(dependency, key, value)
            
            session.commit()
            session.refresh(dependency)
            return dependency
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def delete(dependency_id: str) -> bool:
        """删除总库依赖"""
        session = Database.get_session()
        try:
            result = session.query(LibraryDependency).filter_by(dependency_id=dependency_id).delete()
            session.commit()
            return result > 0
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def count_by_library(library_id: str) -> int:
        """统计总库的依赖数量"""
        session = Database.get_session()
        try:
            return session.query(LibraryDependency).filter_by(library_id=library_id).count()
        finally:
            session.close()
    
    @staticmethod
    def count_by_project(project_id: str) -> int:
        """统计项目的依赖数量"""
        session = Database.get_session()
        try:
            return session.query(LibraryDependency).filter_by(project_id=project_id).count()
        finally:
            session.close()
    
    @staticmethod
    def get_dependencies_for_project(library_id: str, project_id: str) -> List[LibraryDependency]:
        """获取项目的所有依赖"""
        session = Database.get_session()
        try:
            return session.query(LibraryDependency)\
                .filter_by(library_id=library_id, project_id=project_id)\
                .all()
        finally:
            session.close()
    
    @staticmethod
    def get_dependents_for_project(library_id: str, project_id: str) -> List[LibraryDependency]:
        """获取依赖项目的所有项目"""
        session = Database.get_session()
        try:
            return session.query(LibraryDependency)\
                .filter_by(library_id=library_id, dependency_project_id=project_id)\
                .all()
        finally:
            session.close()
    
    @staticmethod
    def check_dependency_exists(library_id: str, project_id: str, dependency_project_id: str) -> bool:
        """检查依赖关系是否存在"""
        session = Database.get_session()
        try:
            count = session.query(LibraryDependency).filter_by(
                library_id=library_id,
                project_id=project_id,
                dependency_project_id=dependency_project_id
            ).count()
            return count > 0
        finally:
            session.close()
