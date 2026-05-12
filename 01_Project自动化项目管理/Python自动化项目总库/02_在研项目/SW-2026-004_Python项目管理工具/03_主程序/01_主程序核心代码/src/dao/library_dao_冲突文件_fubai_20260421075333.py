# -*- coding: utf-8 -*-
"""
总库数据访问对象
"""
from typing import List, Optional, Dict, Tuple
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import func, and_, or_

from src.models.library import Library, LibraryProject, Category
from src.models.project import Project
from src.dao.database import Database
from src.utils.logger import setup_logger
from src.utils.cache import cache

logger = setup_logger(__name__)

class LibraryDAO:
    """总库数据访问类"""
    
    @staticmethod
    def get_session() -> Session:
        """获取数据库会话"""
        db = Database()
        return db.get_session()
    
    @staticmethod
    def create(library: Library) -> Library:
        """创建总库"""
        session = LibraryDAO.get_session()
        try:
            session.add(library)
            session.commit()
            session.refresh(library)
            return library
        except Exception as e:
            session.rollback()
            logger.exception(f"创建总库失败: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def get_by_id(library_id: str) -> Optional[Library]:
        """根据ID获取总库"""
        session = LibraryDAO.get_session()
        try:
            return session.query(Library).filter(Library.library_id == library_id).first()
        finally:
            session.close()
    
    @staticmethod
    def list(
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[Library], int]:
        """查询总库列表"""
        session = LibraryDAO.get_session()
        try:
            query = session.query(Library)
            
            if status:
                query = query.filter(Library.status == status)
            
            if keyword:
                query = query.filter(
                    or_(
                        Library.name.like(f"%{keyword}%"),
                        Library.description.like(f"%{keyword}%")
                    )
                )
            
            total = query.count()
            libraries = query.offset((page - 1) * size).limit(size).all()
            
            return libraries, total
        finally:
            session.close()
    
    @staticmethod
    def update(library_id: str, data: dict) -> Optional[Library]:
        """更新总库信息"""
        session = LibraryDAO.get_session()
        try:
            library = session.query(Library).filter(Library.library_id == library_id).first()
            if not library:
                return None
            
            for key, value in data.items():
                setattr(library, key, value)
            
            session.commit()
            session.refresh(library)
            return library
        except Exception as e:
            session.rollback()
            logger.exception(f"更新总库失败: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def delete(library_id: str, hard_delete: bool = False) -> bool:
        """删除总库"""
        session = LibraryDAO.get_session()
        try:
            library = session.query(Library).filter(Library.library_id == library_id).first()
            if not library:
                return False
            
            if hard_delete:
                session.delete(library)
            else:
                library.status = "archived"
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.exception(f"删除总库失败: {e}")
            return False
        finally:
            session.close()
    
    @staticmethod
    def add_project(library_id: str, project_id: str, category_id: Optional[str] = None) -> bool:
        """添加项目到总库"""
        session = LibraryDAO.get_session()
        try:
            library_project = LibraryProject(
                library_id=library_id,
                project_id=project_id,
                category_id=category_id
            )
            session.add(library_project)
            session.commit()
            # 清除项目统计缓存（因为总库项目数发生变化）
            cleared_count = cache.clear(namespace="projects")
            logger.info(f"添加项目 {project_id} 到总库 {library_id} 后清除缓存: {cleared_count} 条")
            return True
        except Exception as e:
            session.rollback()
            logger.exception(f"添加项目到总库失败: {e}")
            return False
        finally:
            session.close()
    
    @staticmethod
    def remove_project(library_id: str, project_id: str) -> bool:
        """从总库中移除项目"""
        session = LibraryDAO.get_session()
        try:
            library_project = session.query(LibraryProject).filter(
                and_(
                    LibraryProject.library_id == library_id,
                    LibraryProject.project_id == project_id
                )
            ).first()

            if library_project:
                session.delete(library_project)
                session.commit()
                # 清除项目统计缓存（因为总库项目数发生变化）
                cleared_count = cache.clear(namespace="projects")
                logger.info(f"从总库 {library_id} 移除项目 {project_id} 后清除缓存: {cleared_count} 条")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.exception(f"从总库中移除项目失败: {e}")
            return False
        finally:
            session.close()
    
    @staticmethod
    def is_project_in_library(library_id: str, project_id: str) -> bool:
        """检查项目是否在总库中"""
        session = LibraryDAO.get_session()
        try:
            count = session.query(LibraryProject).filter(
                and_(
                    LibraryProject.library_id == library_id,
                    LibraryProject.project_id == project_id
                )
            ).count()
            return count > 0
        finally:
            session.close()
    
    @staticmethod
    def list_projects(
        library_id: str,
        category_id: Optional[str] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[Project], int]:
        """查询总库中的项目列表"""
        session = LibraryDAO.get_session()
        try:
            query = session.query(Project).join(
                LibraryProject, Project.project_id == LibraryProject.project_id
            ).filter(LibraryProject.library_id == library_id)
            
            if category_id:
                query = query.filter(LibraryProject.category_id == category_id)
            
            if status:
                query = query.filter(Project.status == status)
            
            if keyword:
                query = query.filter(
                    or_(
                        Project.name.like(f"%{keyword}%"),
                        Project.code.like(f"%{keyword}%"),
                        Project.description.like(f"%{keyword}%")
                    )
                )
            
            total = query.count()
            projects = query.offset((page - 1) * size).limit(size).all()
            
            return projects, total
        finally:
            session.close()
    
    @staticmethod
    def count_projects(library_id: str) -> int:
        """统计总库中的项目数量"""
        session = LibraryDAO.get_session()
        try:
            return session.query(LibraryProject).filter(
                LibraryProject.library_id == library_id
            ).count()
        finally:
            session.close()
    
    @staticmethod
    def create_category(category: Category) -> Category:
        """创建分类"""
        session = LibraryDAO.get_session()
        try:
            session.add(category)
            session.commit()
            session.refresh(category)
            return category
        except Exception as e:
            session.rollback()
            logger.exception(f"创建分类失败: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def get_category(category_id: str) -> Optional[Category]:
        """根据ID获取分类"""
        session = LibraryDAO.get_session()
        try:
            return session.query(Category).filter(Category.category_id == category_id).first()
        finally:
            session.close()
    
    @staticmethod
    def list_categories(library_id: str) -> List[Category]:
        """查询总库的分类列表"""
        session = LibraryDAO.get_session()
        try:
            return session.query(Category).filter(
                Category.library_id == library_id
            ).all()
        finally:
            session.close()
    
    @staticmethod
    def count_categories(library_id: str) -> int:
        """统计总库中的分类数量"""
        session = LibraryDAO.get_session()
        try:
            return session.query(Category).filter(
                Category.library_id == library_id
            ).count()
        finally:
            session.close()
    
    @staticmethod
    def get_project_statistics(library_id: str) -> Dict:
        """获取总库项目统计信息"""
        session = LibraryDAO.get_session()
        try:
            logger.debug(f"查询总库 {library_id} 的项目统计信息")

            # 总项目数
            total = session.query(LibraryProject).filter(
                LibraryProject.library_id == library_id
            ).count()

            # 状态分布
            status_distribution = {}
            status_results = session.query(
                Project.status,
                func.count(Project.project_id)
            ).join(
                LibraryProject, Project.project_id == LibraryProject.project_id
            ).filter(
                LibraryProject.library_id == library_id
            ).group_by(Project.status).all()

            for status, count in status_results:
                status_distribution[status.value if hasattr(status, 'value') else status] = count

            # 业务线分布
            business_line_distribution = {}
            bl_results = session.query(
                Project.business_line,
                func.count(Project.project_id)
            ).join(
                LibraryProject, Project.project_id == LibraryProject.project_id
            ).filter(
                LibraryProject.library_id == library_id
            ).group_by(Project.business_line).all()

            for bl, count in bl_results:
                business_line_distribution[bl.value if hasattr(bl, 'value') else bl] = count

            stats = {
                "total": total,
                "status_distribution": status_distribution,
                "business_line_distribution": business_line_distribution
            }

            logger.debug(f"总库 {library_id} 统计结果: total={total}, statuses={len(status_distribution)}, business_lines={len(business_line_distribution)}")
            return stats
        finally:
            session.close()

    @staticmethod
    def list_unassociated_projects(library_id: str, page: int = 1, size: int = 100) -> Tuple[List[Project], int]:
        """
        获取未关联到指定总库的项目列表

        Args:
            library_id: 总库ID
            page: 页码
            size: 每页大小

        Returns:
            (项目列表, 总数)
        """
        session = LibraryDAO.get_session()
        try:
            # 子查询：获取已关联到该总库的项目ID
            associated_project_ids = session.query(LibraryProject.project_id).filter(
                LibraryProject.library_id == library_id
            ).subquery()

            # 查询不在已关联列表中的项目
            query = session.query(Project).filter(
                ~Project.project_id.in_(associated_project_ids)
            )

            total = query.count()
            projects = query.offset((page - 1) * size).limit(size).all()

            return projects, total
        finally:
            session.close()
