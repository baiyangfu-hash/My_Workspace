# -*- coding: utf-8 -*-
"""
总库仪表盘服务
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from src.dao.library_dao import LibraryDAO
from src.dao.library_version_dao import LibraryVersionDAO
from src.dao.library_dependency_dao import LibraryDependencyDAO
from src.dao.library_change_dao import LibraryChangeDAO
from src.dao.project_dao import ProjectDAO
from src.services.library_dependency_service import LibraryDependencyService
from src.services.library_version_service import LibraryVersionService
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class LibraryDashboardService:
    """总库仪表盘服务类"""
    
    @staticmethod
    def get_library_dashboard(library_id: str) -> Dict:
        """
        获取总库仪表盘数据
        
        Returns:
            总库仪表盘数据，包含健康状态、统计信息和趋势
        """
        try:
            # 验证总库是否存在
            library = LibraryDAO.get_by_id(library_id)
            if not library:
                return {}
            
            # 获取基本信息
            basic_info = {
                "library_id": library.library_id,
                "name": library.name,
                "description": library.description,
                "status": library.status,
                "created_at": library.created_at.isoformat(),
                "updated_at": library.updated_at.isoformat()
            }
            
            # 获取项目统计
            project_stats = LibraryDashboardService._get_project_statistics(library_id)
            
            # 获取版本统计
            version_stats = LibraryVersionService.get_version_statistics(library_id)
            
            # 获取依赖统计
            dependency_stats = LibraryDependencyService.get_dependency_statistics(library_id)
            
            # 获取依赖健康分析
            dependency_health = LibraryDependencyService.analyze_dependency_health(library_id)
            
            # 获取变更统计
            change_stats = LibraryDashboardService._get_change_statistics(library_id)
            
            # 获取趋势数据
            trends = LibraryDashboardService._get_trends(library_id)
            
            # 计算整体健康评分
            overall_health = LibraryDashboardService._calculate_overall_health(
                dependency_health, version_stats, change_stats
            )
            
            return {
                "basic_info": basic_info,
                "project_stats": project_stats,
                "version_stats": version_stats,
                "dependency_stats": dependency_stats,
                "dependency_health": dependency_health,
                "change_stats": change_stats,
                "trends": trends,
                "overall_health": overall_health
            }
        except Exception as e:
            logger.exception(f"获取总库仪表盘数据失败: {e}")
            return {}
    
    @staticmethod
    def _get_project_statistics(library_id: str) -> Dict:
        """获取项目统计信息"""
        try:
            # 获取总库中的项目列表
            projects, total = LibraryDAO.list_projects(library_id=library_id, page=1, size=1000)
            
            # 按状态统计
            status_count = {}
            for project in projects:
                status_count[project.status] = status_count.get(project.status, 0) + 1
            
            # 按业务线统计
            business_line_count = {}
            for project in projects:
                business_line_count[project.business_line] = business_line_count.get(project.business_line, 0) + 1
            
            return {
                "total": total,
                "status_distribution": status_count,
                "business_line_distribution": business_line_count
            }
        except Exception as e:
            logger.exception(f"获取项目统计信息失败: {e}")
            return {}
    
    @staticmethod
    def _get_change_statistics(library_id: str) -> Dict:
        """获取变更统计信息"""
        try:
            # 获取总库的变更列表
            changes, total = LibraryChangeDAO.list(library_id=library_id, page=1, size=1000)
            
            # 按状态统计
            status_count = {}
            for change in changes:
                status_count[change.status] = status_count.get(change.status, 0) + 1
            
            # 按类型统计
            type_count = {}
            for change in changes:
                type_count[change.change_type] = type_count.get(change.change_type, 0) + 1
            
            return {
                "total": total,
                "status_distribution": status_count,
                "type_distribution": type_count
            }
        except Exception as e:
            logger.exception(f"获取变更统计信息失败: {e}")
            return {}
    
    @staticmethod
    def _get_trends(library_id: str) -> Dict:
        """获取趋势数据"""
        try:
            # 最近30天的项目添加趋势
            project_trend = LibraryDashboardService._get_project_trend(library_id)
            
            # 最近30天的变更趋势
            change_trend = LibraryDashboardService._get_change_trend(library_id)
            
            # 最近30天的版本发布趋势
            version_trend = LibraryDashboardService._get_version_trend(library_id)
            
            return {
                "project_trend": project_trend,
                "change_trend": change_trend,
                "version_trend": version_trend
            }
        except Exception as e:
            logger.exception(f"获取趋势数据失败: {e}")
            return {}
    
    @staticmethod
    def _get_project_trend(library_id: str) -> List[Dict]:
        """获取项目添加趋势"""
        try:
            # 这里简化处理，实际应该从数据库中查询每天的项目添加数量
            # 由于当前模型没有记录项目添加时间，所以返回模拟数据
            trend = []
            today = datetime.now()
            for i in range(30):
                date = today - timedelta(days=i)
                trend.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "count": 0  # 实际应该从数据库查询
                })
            return list(reversed(trend))
        except Exception as e:
            logger.exception(f"获取项目趋势失败: {e}")
            return []
    
    @staticmethod
    def _get_change_trend(library_id: str) -> List[Dict]:
        """获取变更趋势"""
        try:
            # 获取最近30天的变更
            changes, _ = LibraryChangeDAO.list(library_id=library_id, page=1, size=1000)
            
            # 按日期统计
            date_count = {}
            today = datetime.now()
            for i in range(30):
                date = today - timedelta(days=i)
                date_count[date.strftime("%Y-%m-%d")] = 0
            
            for change in changes:
                date_str = change.created_at.strftime("%Y-%m-%d")
                if date_str in date_count:
                    date_count[date_str] += 1
            
            # 转换为列表
            trend = []
            for date_str, count in sorted(date_count.items()):
                trend.append({
                    "date": date_str,
                    "count": count
                })
            
            return trend
        except Exception as e:
            logger.exception(f"获取变更趋势失败: {e}")
            return []
    
    @staticmethod
    def _get_version_trend(library_id: str) -> List[Dict]:
        """获取版本发布趋势"""
        try:
            # 获取最近30天的版本
            versions, _ = LibraryVersionDAO.list(library_id=library_id, page=1, size=1000)
            
            # 按日期统计
            date_count = {}
            today = datetime.now()
            for i in range(30):
                date = today - timedelta(days=i)
                date_count[date.strftime("%Y-%m-%d")] = 0
            
            for version in versions:
                date_str = version.created_at.strftime("%Y-%m-%d")
                if date_str in date_count:
                    date_count[date_str] += 1
            
            # 转换为列表
            trend = []
            for date_str, count in sorted(date_count.items()):
                trend.append({
                    "date": date_str,
                    "count": count
                })
            
            return trend
        except Exception as e:
            logger.exception(f"获取版本趋势失败: {e}")
            return []
    
    @staticmethod
    def _calculate_overall_health(dependency_health: Dict, version_stats: Dict, change_stats: Dict) -> Dict:
        """计算总库整体健康评分"""
        try:
            # 依赖健康评分（权重40%）
            dependency_score = dependency_health.get("health_score", 0)
            
            # 版本管理评分（权重30%）
            version_score = 0
            if version_stats.get("total_versions", 0) > 0:
                published_versions = version_stats.get("status_distribution", {}).get("published", 0)
                version_score = (published_versions / version_stats["total_versions"]) * 100
            
            # 变更管理评分（权重30%）
            change_score = 0
            if change_stats.get("total", 0) > 0:
                completed_changes = change_stats.get("status_distribution", {}).get("implemented", 0)
                change_score = (completed_changes / change_stats["total"]) * 100
            
            # 计算总分
            overall_score = dependency_score * 0.4 + version_score * 0.3 + change_score * 0.3
            overall_score = max(0, min(100, overall_score))
            
            # 健康状态
            if overall_score >= 80:
                status = "健康"
            elif overall_score >= 60:
                status = "警告"
            else:
                status = "危险"
            
            return {
                "score": round(overall_score, 2),
                "status": status,
                "components": {
                    "dependency_health": round(dependency_score, 2),
                    "version_management": round(version_score, 2),
                    "change_management": round(change_score, 2)
                }
            }
        except Exception as e:
            logger.exception(f"计算整体健康评分失败: {e}")
            return {
                "score": 0,
                "status": "未知",
                "components": {
                    "dependency_health": 0,
                    "version_management": 0,
                    "change_management": 0
                }
            }
    
    @staticmethod
    def get_all_libraries_dashboard() -> List[Dict]:
        """
        获取所有总库的仪表盘数据
        
        Returns:
            所有总库的仪表盘数据列表
        """
        try:
            # 获取所有总库
            libraries, _ = LibraryDAO.list(page=1, size=100)
            
            dashboard_data = []
            for library in libraries:
                library_dashboard = LibraryDashboardService.get_library_dashboard(library.library_id)
                if library_dashboard:
                    dashboard_data.append(library_dashboard)
            
            return dashboard_data
        except Exception as e:
            logger.exception(f"获取所有总库仪表盘数据失败: {e}")
            return []
    
    @staticmethod
    def get_dashboard_data() -> Dict:
        """
        获取仪表盘汇总数据 (兼容性方法)
        
        Returns:
            仪表盘汇总数据字典
        """
        try:
            all_dashboards = LibraryDashboardService.get_all_libraries_dashboard()
            
            total_libraries = len(all_dashboards)
            total_projects = sum(d.get('project_count', 0) for d in all_dashboards)
            total_changes = sum(d.get('change_count', 0) for d in all_dashboards)
            total_versions = sum(d.get('version_count', 0) for d in all_dashboards)
            
            return {
                "total_libraries": total_libraries,
                "total_projects": total_projects,
                "total_changes": total_changes,
                "total_versions": total_versions,
                "libraries": all_dashboards
            }
        except Exception as e:
            logger.exception(f"获取仪表盘数据失败: {e}")
            return {"total_libraries": 0, "total_projects": 0, "total_changes": 0, "total_versions": 0}
