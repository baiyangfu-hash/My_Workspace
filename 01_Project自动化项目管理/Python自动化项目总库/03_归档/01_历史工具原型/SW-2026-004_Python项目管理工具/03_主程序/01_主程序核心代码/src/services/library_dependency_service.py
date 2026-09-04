# -*- coding: utf-8 -*-
"""
总库依赖管理服务
"""
import uuid
from datetime import datetime
from typing import List, Optional, Tuple, Dict
from pathlib import Path
import networkx as nx

from src.dao.library_dependency_dao import LibraryDependencyDAO
from src.dao.library_dao import LibraryDAO
from src.dao.project_dao import ProjectDAO
from src.models.library_dependency import LibraryDependency
from src.models.project import Project
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class LibraryDependencyService:
    """总库依赖管理服务类"""
    
    @staticmethod
    def create_dependency(
        library_id: str,
        project_id: str,
        dependency_project_id: str,
        dependency_type: str = "runtime",
        version_constraint: Optional[str] = None,
        description: Optional[str] = None
    ) -> tuple[Optional[LibraryDependency], str]:
        """
        创建总库依赖
        
        Returns:
            (依赖对象, 错误信息)，创建成功时错误信息为空
        """
        # 验证总库是否存在
        library = LibraryDAO.get_by_id(library_id)
        if not library:
            return None, "总库不存在"
        
        # 验证项目是否存在
        project = ProjectDAO.get_by_id(project_id)
        if not project:
            return None, "项目不存在"
        
        # 验证依赖项目是否存在
        dependency_project = ProjectDAO.get_by_id(dependency_project_id)
        if not dependency_project:
            return None, "依赖项目不存在"
        
        # 检查项目是否在总库中
        if not LibraryDAO.is_project_in_library(library_id, project_id):
            return None, "项目不在总库中"
        
        if not LibraryDAO.is_project_in_library(library_id, dependency_project_id):
            return None, "依赖项目不在总库中"
        
        # 检查依赖关系是否已存在
        existing = LibraryDependencyDAO.get_by_projects(library_id, project_id, dependency_project_id)
        if existing:
            return None, "依赖关系已存在"
        
        # 检查循环依赖
        if LibraryDependencyService._check_circular_dependency(library_id, project_id, dependency_project_id):
            return None, "检测到循环依赖"
        
        # 创建依赖ID
        dependency_id = f"LD-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
        
        # 创建依赖对象
        dependency = LibraryDependency(
            dependency_id=dependency_id,
            library_id=library_id,
            project_id=project_id,
            dependency_project_id=dependency_project_id,
            dependency_type=dependency_type,
            version_constraint=version_constraint,
            description=description
        )
        
        try:
            # 保存到数据库
            dependency = LibraryDependencyDAO.create(dependency)
            logger.info(f"总库依赖创建成功: {project.code} -> {dependency_project.code}")
            return dependency, ""
            
        except Exception as e:
            logger.exception(f"创建总库依赖失败: {e}")
            return None, f"创建总库依赖失败: {str(e)}"
    
    @staticmethod
    def get_dependency(dependency_id: str) -> Optional[LibraryDependency]:
        """获取总库依赖详情"""
        return LibraryDependencyDAO.get_by_id(dependency_id)
    
    @staticmethod
    def list_dependencies(
        library_id: Optional[str] = None,
        project_id: Optional[str] = None,
        dependency_project_id: Optional[str] = None,
        dependency_type: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[LibraryDependency], int]:
        """查询总库依赖列表"""
        return LibraryDependencyDAO.list(
            library_id=library_id,
            project_id=project_id,
            dependency_project_id=dependency_project_id,
            dependency_type=dependency_type,
            page=page,
            size=size
        )
    
    @staticmethod
    def get_dependencies(library_id: str, **kwargs) -> List[LibraryDependency]:
        """
        获取总库的依赖列表 (兼容性方法)
        
        Args:
            library_id: 总库ID
            **kwargs: 可选过滤条件 (project_id, dependency_project_id, dependency_type)
            
        Returns:
            依赖对象列表
        """
        dependencies, _ = LibraryDependencyService.list_dependencies(
            library_id=library_id,
            **kwargs
        )
        return dependencies
    
    @staticmethod
    def update_dependency(dependency_id: str, data: dict) -> tuple[Optional[LibraryDependency], str]:
        """更新总库依赖信息"""
        try:
            dependency = LibraryDependencyDAO.update(dependency_id, data)
            if not dependency:
                return None, "依赖不存在"
            
            logger.info(f"总库依赖更新成功: {dependency.dependency_id}")
            return dependency, ""
            
        except Exception as e:
            logger.exception(f"更新总库依赖失败: {e}")
            return None, f"更新总库依赖失败: {str(e)}"
    
    @staticmethod
    def delete_dependency(dependency_id: str) -> tuple[bool, str]:
        """删除总库依赖"""
        try:
            # 先获取依赖信息
            dependency = LibraryDependencyDAO.get_by_id(dependency_id)
            if not dependency:
                return False, "依赖不存在"
            
            # 删除依赖
            success = LibraryDependencyDAO.delete(dependency_id)
            if not success:
                return False, "删除依赖失败"
            
            logger.info(f"总库依赖已删除: {dependency.dependency_id}")
            return True, ""
            
        except Exception as e:
            logger.exception(f"删除总库依赖失败: {e}")
            return False, f"删除总库依赖失败: {str(e)}"
    
    @staticmethod
    def get_project_dependencies(library_id: str, project_id: str) -> List[LibraryDependency]:
        """获取项目的所有依赖"""
        return LibraryDependencyDAO.get_dependencies_for_project(library_id, project_id)
    
    @staticmethod
    def get_project_dependents(library_id: str, project_id: str) -> List[LibraryDependency]:
        """获取依赖项目的所有项目"""
        return LibraryDependencyDAO.get_dependents_for_project(library_id, project_id)
    
    @staticmethod
    def _check_circular_dependency(library_id: str, project_id: str, dependency_project_id: str) -> bool:
        """
        检查是否存在循环依赖
        
        Returns:
            True 如果存在循环依赖，False 否则
        """
        try:
            # 构建依赖图
            G = nx.DiGraph()
            
            # 添加当前依赖
            G.add_edge(project_id, dependency_project_id)
            
            # 添加所有现有依赖
            dependencies, _ = LibraryDependencyDAO.list(library_id=library_id)
            for dep in dependencies:
                G.add_edge(dep.project_id, dep.dependency_project_id)
            
            # 检查是否存在环
            cycles = list(nx.simple_cycles(G))
            return len(cycles) > 0
        except Exception as e:
            logger.exception(f"检查循环依赖失败: {e}")
            return False
    
    @staticmethod
    def build_dependency_graph(library_id: str) -> Dict:
        """
        构建总库依赖关系图谱
        
        Returns:
            依赖图数据，包含节点和边
        """
        G = nx.DiGraph()
        
        # 获取所有依赖
        dependencies, _ = LibraryDependencyDAO.list(library_id=library_id)
        
        # 添加节点和边
        for dep in dependencies:
            # 添加项目节点
            project = ProjectDAO.get_by_id(dep.project_id)
            if project:
                G.add_node(dep.project_id, name=project.name, code=project.code)
            
            # 添加依赖项目节点
            dependency_project = ProjectDAO.get_by_id(dep.dependency_project_id)
            if dependency_project:
                G.add_node(dep.dependency_project_id, name=dependency_project.name, code=dependency_project.code)
            
            # 添加边
            G.add_edge(dep.project_id, dep.dependency_project_id, 
                      dependency_type=dep.dependency_type,
                      version_constraint=dep.version_constraint)
        
        # 转换为前端可用的格式
        nodes = []
        edges = []
        
        for node_id, node_data in G.nodes(data=True):
            nodes.append({
                "id": node_id,
                "name": node_data.get("name", node_id),
                "code": node_data.get("code", "")
            })
        
        for u, v, edge_data in G.edges(data=True):
            edges.append({
                "source": u,
                "target": v,
                "dependency_type": edge_data.get("dependency_type", "runtime"),
                "version_constraint": edge_data.get("version_constraint", "")
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "total_nodes": len(nodes),
            "total_edges": len(edges)
        }
    
    @staticmethod
    def analyze_dependency_health(library_id: str) -> Dict:
        """
        分析总库依赖健康状态
        
        Returns:
            依赖健康分析结果
        """
        try:
            # 构建依赖图
            graph_data = LibraryDependencyService.build_dependency_graph(library_id)
            
            # 检查循环依赖
            G = nx.DiGraph()
            for edge in graph_data["edges"]:
                G.add_edge(edge["source"], edge["target"])
            
            cycles = []
            try:
                cycles = list(nx.simple_cycles(G))
            except Exception as e:
                logger.exception(f"检查循环依赖失败: {e}")
            
            has_circular_dependencies = len(cycles) > 0
            
            # 检查孤立节点（没有依赖也没有被依赖的项目）
            isolated_nodes = [node for node in G.nodes() if G.degree(node) == 0]
            
            # 检查依赖深度
            max_depth = 0
            try:
                if nx.is_directed_acyclic_graph(G):
                    max_depth = nx.dag_longest_path_length(G, weight=None)
            except Exception as e:
                logger.exception(f"计算依赖深度失败: {e}")
            
            # 计算依赖统计
            total_dependencies = len(graph_data["edges"])
            total_projects = len(graph_data["nodes"])
            avg_dependencies_per_project = total_dependencies / total_projects if total_projects > 0 else 0
            
            # 健康状态评估
            health_score = 100
            if has_circular_dependencies:
                health_score -= 30
            if len(isolated_nodes) > total_projects * 0.5:
                health_score -= 20
            if max_depth > 5:
                health_score -= 20
            if avg_dependencies_per_project > 10:
                health_score -= 10
            
            health_status = "健康" if health_score >= 80 else "警告" if health_score >= 60 else "危险"
            
            return {
                "health_score": max(0, health_score),
                "health_status": health_status,
                "circular_dependencies": {
                    "exists": has_circular_dependencies,
                    "count": len(cycles),
                    "cycles": cycles
                },
                "isolated_nodes": {
                    "count": len(isolated_nodes),
                    "nodes": isolated_nodes
                },
                "dependency_depth": {
                    "max": max_depth,
                    "avg": avg_dependencies_per_project
                },
                "statistics": {
                    "total_projects": total_projects,
                    "total_dependencies": total_dependencies,
                    "avg_dependencies_per_project": round(avg_dependencies_per_project, 2)
                }
            }
        except Exception as e:
            logger.exception(f"分析依赖健康状态失败: {e}")
            return {
                "health_score": 0,
                "health_status": "错误",
                "error": str(e)
            }
    
    @staticmethod
    def get_dependency_statistics(library_id: str) -> dict:
        """获取总库依赖统计信息"""
        try:
            # 验证总库是否存在
            library = LibraryDAO.get_by_id(library_id)
            if not library:
                return {}
            
            # 获取依赖统计
            total_dependencies = LibraryDependencyDAO.count_by_library(library_id)
            
            # 获取各类型依赖数量
            dependencies, _ = LibraryDependencyDAO.list(library_id=library_id, page=1, size=1000)
            type_count = {}
            for dep in dependencies:
                type_count[dep.dependency_type] = type_count.get(dep.dependency_type, 0) + 1
            
            # 获取项目依赖统计
            project_dependency_count = {}
            for dep in dependencies:
                project_dependency_count[dep.project_id] = project_dependency_count.get(dep.project_id, 0) + 1
            
            # 获取依赖最多的项目
            top_dependent_projects = sorted(
                project_dependency_count.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            return {
                "total_dependencies": total_dependencies,
                "type_distribution": type_count,
                "top_dependent_projects": [
                    {
                        "project_id": project_id,
                        "dependency_count": count,
                        "project_name": ProjectDAO.get_by_id(project_id).name if ProjectDAO.get_by_id(project_id) else project_id
                    }
                    for project_id, count in top_dependent_projects
                ]
            }
        except Exception as e:
            logger.exception(f"获取总库依赖统计信息失败: {e}")
            return {}
