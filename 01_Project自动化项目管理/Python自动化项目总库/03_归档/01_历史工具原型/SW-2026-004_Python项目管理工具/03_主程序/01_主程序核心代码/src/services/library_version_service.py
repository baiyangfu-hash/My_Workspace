# -*- coding: utf-8 -*-
"""
总库版本管理服务
"""
import uuid
import re
from datetime import datetime
from typing import List, Optional, Tuple, Dict
from pathlib import Path

from src.dao.library_version_dao import LibraryVersionDAO
from src.dao.library_dao import LibraryDAO
from src.dao.project_dao import ProjectDAO
from src.models.library_version import LibraryVersion
from src.models.project import Project
from src.utils.validators import validate_version_number
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class LibraryVersionService:
    """总库版本管理服务类"""
    
    @staticmethod
    def create_version(
        library_id: str,
        version_number: str,
        description: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> tuple[Optional[LibraryVersion], str]:
        """
        创建总库版本
        
        Returns:
            (版本对象, 错误信息)，创建成功时错误信息为空
        """
        # 验证输入
        valid, msg = validate_version_number(version_number)
        if not valid:
            return None, msg
        
        # 验证总库是否存在
        library = LibraryDAO.get_by_id(library_id)
        if not library:
            return None, "总库不存在"
        
        # 检查版本号是否已存在
        existing = LibraryVersionDAO.get_by_library_and_version(library_id, version_number)
        if existing:
            return None, "版本号已存在"
        
        # 创建版本ID
        version_id = f"LV-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
        
        # 创建版本对象
        version = LibraryVersion(
            version_id=version_id,
            library_id=library_id,
            version_number=version_number,
            description=description,
            status="draft",
            created_by=created_by
        )
        
        try:
            # 保存到数据库
            version = LibraryVersionDAO.create(version)
            logger.info(f"总库版本创建成功: {version_number}")
            return version, ""
            
        except Exception as e:
            logger.exception(f"创建总库版本失败: {e}")
            return None, f"创建总库版本失败: {str(e)}"
    
    @staticmethod
    def get_version(version_id: str) -> Optional[LibraryVersion]:
        """获取总库版本详情"""
        return LibraryVersionDAO.get_by_id(version_id)
    
    @staticmethod
    def list_versions(
        library_id: Optional[str] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[LibraryVersion], int]:
        """查询总库版本列表"""
        return LibraryVersionDAO.list(
            library_id=library_id,
            status=status,
            keyword=keyword,
            page=page,
            size=size
        )
    
    @staticmethod
    def update_version(version_id: str, data: dict) -> tuple[Optional[LibraryVersion], str]:
        """更新总库版本信息"""
        # 验证输入
        if "version_number" in data:
            valid, msg = validate_version_number(data["version_number"])
            if not valid:
                return None, msg
        
        try:
            version = LibraryVersionDAO.update(version_id, data)
            if not version:
                return None, "版本不存在"
            
            logger.info(f"总库版本更新成功: {version.version_number}")
            return version, ""
            
        except Exception as e:
            logger.exception(f"更新总库版本失败: {e}")
            return None, f"更新总库版本失败: {str(e)}"
    
    @staticmethod
    def delete_version(version_id: str) -> tuple[bool, str]:
        """删除总库版本"""
        try:
            # 先获取版本信息
            version = LibraryVersionDAO.get_by_id(version_id)
            if not version:
                return False, "版本不存在"
            
            # 检查状态，只有草稿状态的版本可以删除
            if version.status != "draft":
                return False, "只有草稿状态的版本可以删除"
            
            # 删除版本
            success = LibraryVersionDAO.delete(version_id)
            if not success:
                return False, "删除版本失败"
            
            logger.info(f"总库版本已删除: {version.version_number}")
            return True, ""
            
        except Exception as e:
            logger.exception(f"删除总库版本失败: {e}")
            return False, f"删除总库版本失败: {str(e)}"
    
    @staticmethod
    def add_project_to_version(version_id: str, project_id: str, project_version: Optional[str] = None) -> tuple[bool, str]:
        """向总库版本添加项目"""
        try:
            # 验证版本是否存在
            version = LibraryVersionDAO.get_by_id(version_id)
            if not version:
                return False, "版本不存在"
            
            # 验证项目是否存在
            project = ProjectDAO.get_by_id(project_id)
            if not project:
                return False, "项目不存在"
            
            # 检查项目是否在总库中
            library = LibraryDAO.get_by_id(version.library_id)
            if not library:
                return False, "总库不存在"
            
            if not LibraryDAO.is_project_in_library(version.library_id, project_id):
                return False, "项目不在总库中"
            
            # 添加项目到版本
            success = LibraryVersionDAO.add_project(version_id, project_id, project_version)
            if not success:
                return False, "添加项目失败"
            
            logger.info(f"项目 {project.code} 已添加到版本 {version.version_number}")
            return True, ""
            
        except Exception as e:
            logger.exception(f"添加项目到版本失败: {e}")
            return False, f"添加项目失败: {str(e)}"
    
    @staticmethod
    def remove_project_from_version(version_id: str, project_id: str) -> tuple[bool, str]:
        """从总库版本移除项目"""
        try:
            # 验证版本是否存在
            version = LibraryVersionDAO.get_by_id(version_id)
            if not version:
                return False, "版本不存在"
            
            # 移除项目
            success = LibraryVersionDAO.remove_project(version_id, project_id)
            if not success:
                return False, "移除项目失败"
            
            logger.info(f"项目已从版本 {version.version_number} 移除")
            return True, ""
            
        except Exception as e:
            logger.exception(f"从版本移除项目失败: {e}")
            return False, f"移除项目失败: {str(e)}"
    
    @staticmethod
    def list_version_projects(version_id: str) -> List[Project]:
        """获取总库版本包含的项目列表"""
        session = LibraryVersionDAO.list_version_projects(version_id)
        projects = []
        for association in session:
            project = ProjectDAO.get_by_id(association.project_id)
            if project:
                projects.append(project)
        return projects
    
    @staticmethod
    def publish_version(version_id: str, published_by: str) -> tuple[bool, str]:
        """发布总库版本"""
        try:
            # 获取版本信息
            version = LibraryVersionDAO.get_by_id(version_id)
            if not version:
                return False, "版本不存在"
            
            # 检查状态
            if version.status == "published":
                return False, "版本已发布"
            
            # 检查是否包含项目
            projects = LibraryVersionService.list_version_projects(version_id)
            if not projects:
                return False, "版本必须包含至少一个项目"
            
            # 更新状态
            data = {
                "status": "published",
                "updated_at": datetime.now()
            }
            version = LibraryVersionDAO.update(version_id, data)
            if not version:
                return False, "更新版本状态失败"
            
            logger.info(f"总库版本已发布: {version.version_number}")
            return True, ""
            
        except Exception as e:
            logger.exception(f"发布总库版本失败: {e}")
            return False, f"发布总库版本失败: {str(e)}"
    
    @staticmethod
    def get_version_statistics(library_id: str) -> dict:
        """获取总库版本统计信息"""
        try:
            # 验证总库是否存在
            library = LibraryDAO.get_by_id(library_id)
            if not library:
                return {}
            
            # 获取版本统计
            total_versions = LibraryVersionDAO.count_by_library(library_id)
            
            # 获取各状态版本数量
            versions, _ = LibraryVersionDAO.list(library_id=library_id, page=1, size=100)
            status_count = {}
            for version in versions:
                status_count[version.status] = status_count.get(version.status, 0) + 1
            
            # 获取最新版本
            latest_version = LibraryVersionDAO.get_latest_version(library_id)
            latest_version_info = {
                "version_number": latest_version.version_number if latest_version else None,
                "created_at": latest_version.created_at.isoformat() if latest_version else None
            }
            
            return {
                "total_versions": total_versions,
                "status_distribution": status_count,
                "latest_version": latest_version_info
            }
        except Exception as e:
            logger.exception(f"获取总库版本统计信息失败: {e}")
            return {}
    
    @staticmethod
    def generate_next_version(current_version: str, version_type: str = "patch") -> str:
        """
        生成下一个版本号
        
        Args:
            current_version: 当前版本号
            version_type: 版本类型 (major, minor, patch)
        
        Returns:
            下一个版本号
        """
        # 解析当前版本号
        match = re.match(r"^(\d+)\.(\d+)\.(\d+)", current_version)
        if not match:
            return "1.0.0"
        
        major, minor, patch = map(int, match.groups())
        
        # 根据版本类型生成下一个版本号
        if version_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif version_type == "minor":
            minor += 1
            patch = 0
        else:  # patch
            patch += 1
        
        return f"{major}.{minor}.{patch}"
