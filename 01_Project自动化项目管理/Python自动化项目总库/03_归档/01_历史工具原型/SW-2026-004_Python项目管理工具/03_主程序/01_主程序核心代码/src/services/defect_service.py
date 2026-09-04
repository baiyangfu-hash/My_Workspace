# -*- coding: utf-8 -*-
"""
缺陷管理服务
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from src.dao.database import db as database
from src.dao.defect_dao import DefectDAO
from src.models.defect import Defect, DefectStatus, DefectPriority, DefectSeverity
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class DefectService:
    """缺陷管理服务"""
    
    @staticmethod
    def create_defect(defect_data: dict) -> Defect:
        """创建缺陷"""
        with database.get_session() as session:
            return DefectDAO.create(session, defect_data)
    
    @staticmethod
    def get_defect(defect_id: int) -> Optional[Defect]:
        """获取缺陷详情"""
        with database.get_session() as session:
            return DefectDAO.get_by_id(session, defect_id)
    
    @staticmethod
    def get_defects(**filters) -> List[Defect]:
        """获取缺陷列表"""
        with database.get_session() as session:
            return DefectDAO.get_all(session, **filters)
    
    @staticmethod
    def update_defect(defect_id: int, update_data: dict) -> Optional[Defect]:
        """更新缺陷"""
        with database.get_session() as session:
            return DefectDAO.update(session, defect_id, update_data)
    
    @staticmethod
    def delete_defect(defect_id: int) -> bool:
        """删除缺陷"""
        with database.get_session() as session:
            return DefectDAO.delete(session, defect_id)
    
    @staticmethod
    def get_defect_statistics() -> dict:
        """获取缺陷统计信息"""
        with database.get_session() as session:
            return DefectDAO.get_statistics(session)
    
    @staticmethod
    def change_defect_status(defect_id: int, status: str) -> Optional[Defect]:
        """变更缺陷状态"""
        try:
            # 验证状态是否有效
            status_enum = DefectStatus(status)
            with database.get_session() as session:
                return DefectDAO.update(session, defect_id, {"status": status_enum})
        except ValueError as e:
            logger.error(f"无效的缺陷状态: {e}")
            return None
    
    @staticmethod
    def assign_defect(defect_id: int, assignee: str) -> Optional[Defect]:
        """分配缺陷"""
        with database.get_session() as session:
            return DefectDAO.update(session, defect_id, {"assignee": assignee})
    
    @staticmethod
    def resolve_defect(defect_id: int, resolution: str, fix_version: str) -> Optional[Defect]:
        """解决缺陷"""
        with database.get_session() as session:
            update_data = {
                "resolution": resolution,
                "fix_version": fix_version,
                "status": DefectStatus.FIXED
            }
            return DefectDAO.update(session, defect_id, update_data)
    
    @staticmethod
    def get_defects_by_project(project_id: int) -> List[Defect]:
        """获取项目相关的缺陷"""
        with database.get_session() as session:
            return DefectDAO.get_all(session, project_id=project_id)
    
    @staticmethod
    def get_defects_by_library(library_id: int) -> List[Defect]:
        """获取库相关的缺陷"""
        with database.get_session() as session:
            return DefectDAO.get_all(session, library_id=library_id)
    
    @staticmethod
    def search_defects(keyword: str) -> List[Defect]:
        """搜索缺陷"""
        with database.get_session() as session:
            return DefectDAO.get_all(session, keyword=keyword)
