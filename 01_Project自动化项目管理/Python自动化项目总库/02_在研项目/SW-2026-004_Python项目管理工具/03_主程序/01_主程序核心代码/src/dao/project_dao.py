# -*- coding: utf-8 -*-
"""
项目数据访问对象
"""
from typing import List, Optional, Tuple
from datetime import datetime

from .database import db
from src.models.project import Project
from src.core.constants import ProjectStatus, BusinessLine
from src.utils.logger import setup_logger
from src.utils.cache import cache
from sqlalchemy import func

logger = setup_logger(__name__)

class ProjectDAO:
    """项目数据访问类"""
    
    @staticmethod
    def create(project: Project) -> Project:
        """创建新项目"""
        with db.get_session() as session:
            session.add(project)
            session.commit()
            session.refresh(project)
            cache.clear(namespace="projects")
            return project
    
    @staticmethod
    def get_by_id(project_id: str) -> Optional[Project]:
        """根据项目ID查询"""
        cache_key = f"id:{project_id}"
        cached = cache.get(cache_key, namespace="projects")
        if cached is not None:
            return cached
        
        with db.get_session() as session:
            project = session.query(Project).filter(Project.project_id == project_id).first()
            if project:
                cache.set(cache_key, project.to_dict(), ttl=120, namespace="projects")
            return project
    
    @staticmethod
    def get_by_code(code: str) -> Optional[Project]:
        """根据项目编号查询"""
        cache_key = f"code:{code}"
        cached = cache.get(cache_key, namespace="projects")
        if cached is not None:
            return cached
        
        with db.get_session() as session:
            project = session.query(Project).filter(Project.code == code).first()
            if project:
                cache.set(cache_key, project.to_dict(), ttl=120, namespace="projects")
            return project
    
    @staticmethod
    def list(
        status: Optional[ProjectStatus] = None,
        business_line: Optional[BusinessLine] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[Project], int]:
        """分页查询项目列表"""
        with db.get_session() as session:
            query = session.query(Project)
            
            if status:
                query = query.filter(Project.status == status)
            
            if business_line:
                query = query.filter(Project.business_line == business_line)
            
            if keyword:
                keyword = f"%{keyword}%"
                query = query.filter(
                    (Project.name.like(keyword)) |
                    (Project.code.like(keyword)) |
                    (Project.manager.like(keyword))
                )
            
            total = query.count()
            offset = (page - 1) * size
            projects = query.order_by(Project.created_at.desc()).offset(offset).limit(size).all()
            
            return projects, total
    
    @staticmethod
    def update(project_id: str, data: dict) -> Optional[Project]:
        """更新项目信息"""
        with db.get_session() as session:
            project = session.query(Project).filter(Project.project_id == project_id).first()
            if not project:
                return None
            
            project.update_from_dict(data)
            project.updated_at = datetime.now()
            session.commit()
            session.refresh(project)
            cache.clear(namespace="projects")
            return project
    
    @staticmethod
    def delete(project_id: str, hard_delete: bool = False) -> bool:
        """删除项目
        Args:
            project_id: 项目ID
            hard_delete: 是否硬删除，True=彻底删除记录，False=软删除标记为已归档
        """
        with db.get_session() as session:
            project = session.query(Project).filter(Project.project_id == project_id).first()
            if not project:
                return False
            
            if hard_delete:
                from src.models.change import Change
                from src.models.library import LibraryProject

                # 先清理library_projects关联表（避免级联删除报错）
                session.query(LibraryProject).filter(
                    LibraryProject.project_id == project_id
                ).delete(synchronize_session=False)

                # 再清理变更记录
                session.query(Change).filter(Change.project_id == project_id).delete()

                # 最后删除项目本身
                session.delete(project)
            else:
                project.status = ProjectStatus.ARCHIVED
                project.updated_at = datetime.now()
            
            session.commit()
            cache.clear(namespace="projects")
            return True
    
    @staticmethod
    def get_max_sequence(business_line: BusinessLine, year: int) -> int:
        """获取指定业务线和年份的最大序号"""
        with db.get_session() as session:
            # 使用数据库无关的方式提取年份
            from sqlalchemy import extract
            try:
                # 尝试使用extract函数（适用于大多数数据库）
                max_seq = session.query(func.max(Project.sequence))\
                    .filter(Project.business_line == business_line)\
                    .filter(extract('year', Project.created_at) == year)\
                    .scalar()
            except Exception:
                #  fallback：使用字符串比较（适用于SQLite等）
                year_str = str(year)
                max_seq = session.query(func.max(Project.sequence))\
                    .filter(Project.business_line == business_line)\
                    .filter(Project.created_at.like(f"{year_str}%"))\
                    .scalar()
            
            return max_seq or 0
    
    @staticmethod
    def count_by_status(status: Optional[ProjectStatus] = None) -> int:
        """统计指定状态的项目数量"""
        cache_key = f"count:{status or 'all'}"
        cached = cache.get(cache_key, namespace="projects")
        if cached is not None:
            return cached
        
        with db.get_session() as session:
            query = session.query(Project)
            if status:
                query = query.filter(Project.status == status)
            count = query.count()
            cache.set(cache_key, count, ttl=60, namespace="projects")
            return count
