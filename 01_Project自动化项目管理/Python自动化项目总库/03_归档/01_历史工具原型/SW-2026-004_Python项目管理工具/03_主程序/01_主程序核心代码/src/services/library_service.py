# -*- coding: utf-8 -*-
"""
总库管理服务
"""
import os
import uuid
from datetime import datetime
from typing import List, Optional, Tuple, Dict
from pathlib import Path

from src.dao.library_dao import LibraryDAO
from src.dao.project_dao import ProjectDAO
from src.models.library import Library, Category
from src.models.project import Project
from src.utils.path_utils import ensure_directory
from src.utils.validators import validate_library_name, validate_category_name
from src.utils.logger import setup_logger
from src.core.constants import BusinessLine, BUSINESS_LINE_DESC

logger = setup_logger(__name__)

class LibraryService:
    """总库管理服务类"""
    
    @staticmethod
    def create_library(
        name: str,
        root_path: str,
        description: Optional[str] = None
    ) -> tuple[Optional[Library], str]:
        """
        创建总库
        
        Returns:
            (总库对象, 错误信息)，创建成功时错误信息为空
        """
        # 验证输入
        valid, msg = validate_library_name(name)
        if not valid:
            return None, msg
        
        # 验证路径
        root_path_obj = Path(root_path)
        if not root_path_obj.exists():
            try:
                ensure_directory(root_path_obj)
            except Exception as e:
                return None, f"创建根目录失败: {str(e)}"
        
        # 创建总库ID
        library_id = f"LIB-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
        
        # 创建总库对象
        library = Library(
            library_id=library_id,
            name=name,
            description=description,
            root_path=str(root_path_obj)
        )
        
        try:
            # 保存到数据库
            library = LibraryDAO.create(library)
            logger.info(f"总库创建成功: {name}")
            return library, ""
            
        except Exception as e:
            logger.exception(f"创建总库失败: {e}")
            return None, f"创建总库失败: {str(e)}"
    
    @staticmethod
    def get_library(library_id: str) -> Optional[Library]:
        """获取总库详情"""
        return LibraryDAO.get_by_id(library_id)
    
    @staticmethod
    def list_libraries(
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[Library], int]:
        """查询总库列表"""
        return LibraryDAO.list(
            status=status,
            keyword=keyword,
            page=page,
            size=size
        )
    
    @staticmethod
    def update_library(library_id: str, data: dict) -> tuple[Optional[Library], str]:
        """更新总库信息"""
        # 验证输入
        if "name" in data:
            valid, msg = validate_library_name(data["name"])
            if not valid:
                return None, msg
        
        try:
            library = LibraryDAO.update(library_id, data)
            if not library:
                return None, "总库不存在"
            
            logger.info(f"总库更新成功: {library.name}")
            return library, ""
            
        except Exception as e:
            logger.exception(f"更新总库失败: {e}")
            return None, f"更新总库失败: {str(e)}"
    
    @staticmethod
    def delete_library(library_id: str, hard_delete: bool = False) -> tuple[bool, str]:
        """删除总库"""
        try:
            # 先获取总库信息
            library = LibraryDAO.get_by_id(library_id)
            if not library:
                return False, "总库不存在"
            
            # 检查是否有关联项目
            if LibraryDAO.count_projects(library_id) > 0:
                return False, "总库中存在项目，无法删除"
            
            # 删除数据库记录
            success = LibraryDAO.delete(library_id, hard_delete=hard_delete)
            if not success:
                return False, "删除数据库记录失败"
            
            if hard_delete:
                logger.info(f"总库已彻底删除: {library.name}")
            else:
                logger.info(f"总库已归档: {library.name}")
            
            return True, ""
            
        except Exception as e:
            logger.exception(f"删除总库失败: {e}")
            return False, f"删除总库失败: {str(e)}"
    
    @staticmethod
    def add_project_to_library(library_id: str, project_id: str, category_id: Optional[str] = None) -> tuple[bool, str]:
        """将项目添加到总库"""
        try:
            # 验证总库是否存在
            library = LibraryDAO.get_by_id(library_id)
            if not library:
                return False, "总库不存在"
            
            # 验证项目是否存在
            project = ProjectDAO.get_by_id(project_id)
            if not project:
                return False, "项目不存在"
            
            # 验证分类是否存在
            if category_id:
                category = LibraryDAO.get_category(category_id)
                if not category or category.library_id != library_id:
                    return False, "分类不存在或不属于指定总库"
            
            # 检查项目是否已在总库中
            if LibraryDAO.is_project_in_library(library_id, project_id):
                return False, "项目已在总库中"
            
            # 添加项目到总库
            success = LibraryDAO.add_project(library_id, project_id, category_id)
            if not success:
                return False, "添加项目失败"
            
            logger.info(f"项目 {project.code} 已添加到总库 {library.name}")
            return True, ""
            
        except Exception as e:
            logger.exception(f"添加项目到总库失败: {e}")
            return False, f"添加项目失败: {str(e)}"
    
    @staticmethod
    def remove_project_from_library(library_id: str, project_id: str) -> tuple[bool, str]:
        """从总库中移除项目"""
        try:
            # 验证总库是否存在
            library = LibraryDAO.get_by_id(library_id)
            if not library:
                return False, "总库不存在"
            
            # 验证项目是否存在
            project = ProjectDAO.get_by_id(project_id)
            if not project:
                return False, "项目不存在"
            
            # 检查项目是否在总库中
            if not LibraryDAO.is_project_in_library(library_id, project_id):
                return False, "项目不在总库中"
            
            # 从总库中移除项目
            success = LibraryDAO.remove_project(library_id, project_id)
            if not success:
                return False, "移除项目失败"
            
            logger.info(f"项目 {project.code} 已从总库 {library.name} 移除")
            return True, ""
            
        except Exception as e:
            logger.exception(f"从总库中移除项目失败: {e}")
            return False, f"移除项目失败: {str(e)}"
    
    @staticmethod
    def list_library_projects(
        library_id: str,
        category_id: Optional[str] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[Project], int]:
        """查询总库中的项目列表"""
        return LibraryDAO.list_projects(
            library_id=library_id,
            category_id=category_id,
            status=status,
            keyword=keyword,
            page=page,
            size=size
        )

    @staticmethod
    def get_unassociated_projects(library_id: str, page: int = 1, size: int = 100) -> Tuple[List[Project], int]:
        """
        获取未关联到指定总库的项目列表

        Args:
            library_id: 总库ID
            page: 页码
            size: 每页大小

        Returns:
            (项目列表, 总数)
        """
        try:
            # 验证总库是否存在
            library = LibraryDAO.get_by_id(library_id)
            if not library:
                return [], 0

            return LibraryDAO.list_unassociated_projects(library_id, page, size)

        except Exception as e:
            logger.exception(f"获取未关联项目失败: {e}")
            return [], 0
    
    @staticmethod
    def create_category(
        library_id: str,
        name: str,
        description: Optional[str] = None,
        parent_id: Optional[str] = None
    ) -> tuple[Optional[Category], str]:
        """创建分类"""
        # 验证输入
        valid, msg = validate_category_name(name)
        if not valid:
            return None, msg
        
        try:
            # 验证总库是否存在
            library = LibraryDAO.get_by_id(library_id)
            if not library:
                return None, "总库不存在"
            
            # 验证父分类是否存在
            if parent_id:
                parent = LibraryDAO.get_category(parent_id)
                if not parent or parent.library_id != library_id:
                    return None, "父分类不存在或不属于指定总库"
            
            # 创建分类ID
            category_id = f"CAT-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
            
            # 创建分类对象
            category = Category(
                category_id=category_id,
                library_id=library_id,
                name=name,
                description=description,
                parent_id=parent_id
            )
            
            # 保存到数据库
            category = LibraryDAO.create_category(category)
            logger.info(f"分类创建成功: {name}")
            return category, ""
            
        except Exception as e:
            logger.exception(f"创建分类失败: {e}")
            return None, f"创建分类失败: {str(e)}"
    
    @staticmethod
    def list_categories(library_id: str) -> List[Category]:
        """查询总库的分类列表"""
        return LibraryDAO.list_categories(library_id)
    
    @staticmethod
    def get_library_statistics(library_id: str) -> dict:
        """获取总库统计信息"""
        try:
            # 验证总库是否存在
            library = LibraryDAO.get_by_id(library_id)
            if not library:
                return {}
            
            # 获取项目统计
            project_stats = LibraryDAO.get_project_statistics(library_id)
            
            # 获取分类统计
            category_count = LibraryDAO.count_categories(library_id)
            
            return {
                "project_count": project_stats.get("total", 0),
                "category_count": category_count,
                "status_distribution": project_stats.get("status_distribution", {}),
                "business_line_distribution": project_stats.get("business_line_distribution", {})
            }
        except Exception as e:
            logger.exception(f"获取总库统计信息失败: {e}")
            return {}
    
    @staticmethod
    def scan_and_import_projects(
        library_id: str,
        scan_path: str,
        business_line: str,
        template_id: str,
        category_id: Optional[str] = None
    ) -> tuple[List[Project], List[str]]:
        """
        扫描指定目录并导入所有Python项目到总库
        
        Args:
            library_id: 总库ID
            scan_path: 扫描路径
            business_line: 业务线类型
            template_id: 模板ID
            category_id: 分类ID
            
        Returns:
            (成功导入的项目列表, 失败的项目列表)
        """
        from src.services.project_service import ProjectService
        
        success_projects = []
        failed_projects = []
        
        # 验证总库是否存在
        library = LibraryDAO.get_by_id(library_id)
        if not library:
            failed_projects.append("总库不存在")
            return success_projects, failed_projects

        # 扫描目录
        root = Path(scan_path)
        if not root.exists():
            failed_projects.append(f"扫描路径不存在: {scan_path}")
            return success_projects, failed_projects

        # 扫描目录
        for item in root.iterdir():
            if item.is_dir():
                # 检查是否为Python项目（包含setup.py或pyproject.toml或__init__.py）
                has_python_files = any(
                    (item / "setup.py").exists() or
                    (item / "pyproject.toml").exists() or
                    any(p.is_file() and p.suffix == ".py" for p in item.iterdir())
                )

                if has_python_files:
                    project_name = item.name
                    project_path = str(item)

                    # 导入项目
                    project, msg = ProjectService.import_project(
                        business_line=business_line,
                        name=project_name,
                        template_id=template_id,
                        path=project_path
                    )

                    if project:
                        # 添加到总库
                        add_success, add_msg = LibraryService.add_project_to_library(
                            library_id=library_id,
                            project_id=project.project_id,
                            category_id=category_id
                        )
                        if add_success:
                            success_projects.append(project)
                        else:
                            failed_projects.append(f"{project_name}: 添加到总库失败 - {add_msg}")
                    else:
                        failed_projects.append(f"{project_name}: 导入失败 - {msg}")

        return success_projects, failed_projects

    @staticmethod
    def _detect_project_base_path() -> str:
        """
        检测项目基础路径：向上搜索工作区根目录，定位到总库的0100_项目目录

        策略：
        1. 优先确定基准目录：冻结环境用exe目录，开发环境用cwd
        2. 从基准目录开始，逐级向上查找包含 '01_Project自动化项目管理' 的祖先目录
        3. 找到后拼接 /Python自动化项目总库/0100_项目
        4. 若找不到标准结构，fallback 到 {base_search}/projects 并记录 WARNING
        5. 如果fallback也失败，使用临时目录作为最后兜底
        """
        import os
        import sys

        MARKER_DIR = "01_Project自动化项目管理"
        LIBRARY_NAME = "Python自动化项目总库"
        PROJECT_SUBDIR = "0100_项目"

        # 优先确定基准目录：冻结环境用exe目录，开发环境用cwd
        if getattr(sys, 'frozen', False):
            base_search = Path(sys.executable).parent
            logger.info(f"检测到PyInstaller冻结环境，使用exe所在目录作为搜索起点: {base_search}")
        else:
            base_search = Path(os.getcwd())
            logger.info(f"开发环境，使用当前工作目录作为搜索起点: {base_search}")

        # 策略1: 从基准目录向上搜索工作区结构
        search_path = str(base_search)
        while True:
            candidate = os.path.join(search_path, MARKER_DIR, LIBRARY_NAME)
            if os.path.isdir(candidate):
                base = os.path.join(candidate, PROJECT_SUBDIR)
                try:
                    os.makedirs(base, exist_ok=True)
                    logger.info(f"检测到工作区结构，项目根路径: {base}")
                    return base
                except Exception as e:
                    logger.warning(f"创建标准项目目录失败: {e}，将尝试fallback路径")

            parent = os.path.dirname(search_path)
            if parent == search_path:  # 到达根目录
                break
            search_path = parent

        # 策略2: 使用exe所在目录（或cwd）下的 projects 子目录
        fallback = os.path.join(str(base_search), "projects")
        try:
            os.makedirs(fallback, exist_ok=True)
            logger.warning(f"未找到标准工作区结构({MARKER_DIR})，使用fallback路径: {fallback}")
            return fallback
        except Exception as e:
            logger.error(f"创建fallback项目目录失败: {e}")

        # 策略3: 最后兜底 - 使用临时目录
        import tempfile
        temp_base = os.path.join(tempfile.gettempdir(), "Python项目管理工具_projects")
        try:
            os.makedirs(temp_base, exist_ok=True)
            logger.warning(f"使用临时目录作为项目根路径: {temp_base}")
            return temp_base
        except Exception as e:
            logger.critical(f"所有路径检测策略均失败: {e}")
            raise RuntimeError(f"无法确定项目基础路径: {str(e)}")

    @staticmethod
    def initialize_default_library() -> tuple[Optional[Library], str]:
        """
        初始化默认总库（幂等操作）

        首次启动时自动创建默认总库"Python自动化项目总库"
        以及按BusinessLine枚举值创建分类。
        如果已存在则跳过。

        修复：使用直接SQLAlchemy查询确保幂等性，并清理重复的总库

        Returns:
            (默认总库对象或None, 错误信息)
        """
        DEFAULT_LIBRARY_NAME = "Python自动化项目总库"

        try:
            # 1. 直接用DAO精确查询是否存在默认总库（避免分页和LIKE匹配的问题）
            session = LibraryDAO.get_session()
            try:
                # 查询所有同名总库
                existing_libraries = session.query(Library).filter(
                    Library.name == DEFAULT_LIBRARY_NAME
                ).order_by(Library.created_at).all()

                if existing_libraries:
                    # 如果存在多个重复的总库，只保留第一个（创建时间最早的），删除其余的
                    if len(existing_libraries) > 1:
                        logger.warning(f"发现 {len(existing_libraries)} 个重复的默认总库，开始清理...")
                        primary_library = existing_libraries[0]

                        for duplicate_lib in existing_libraries[1:]:
                            logger.info(f"删除重复总库: {duplicate_lib.library_id} (创建于 {duplicate_lib.created_at})")
                            session.delete(duplicate_lib)

                        session.commit()
                        logger.info(f"重复总库清理完成，保留主总库: {primary_library.library_id}")
                        return primary_library, ""
                    else:
                        # 只有一个，检查并补全 root_path
                        existing = existing_libraries[0]

                        # 补全逻辑：确保幂等性，只在 root_path 为空时才补全
                        if not existing.root_path:
                            existing.root_path = LibraryService._detect_project_base_path()
                            session.commit()
                            logger.info(f"补全默认总库root_path: {existing.root_path}")

                        logger.info(f"默认总库已存在，跳过初始化 (ID={existing.library_id})")
                        return existing, ""
            finally:
                session.close()

            # 2. 获取项目根目录（通过工作区检测定位到总库的项目目录）
            root_path = LibraryService._detect_project_base_path()

            # 3. 创建默认总库
            library, error_msg = LibraryService.create_library(
                name=DEFAULT_LIBRARY_NAME,
                root_path=root_path,
                description="系统默认总库，用于统一管理所有自动化项目"
            )

            if not library:
                return None, f"创建默认总库失败: {error_msg}"

            logger.info(f"默认总库创建成功: {library.name} ({library.library_id})")

            # 4. 为每个 BusinessLine 枚举值创建分类
            for business_line in BusinessLine:
                category_name = BUSINESS_LINE_DESC.get(business_line, business_line.value)
                category, cat_error = LibraryService.create_category(
                    library_id=library.library_id,
                    name=category_name,
                    description=f"{category_name}分类"
                )

                if not category:
                    logger.warning(f"创建分类失败 [{business_line.value}]: {cat_error}")
                else:
                    logger.info(f"分类创建成功: {category_name}")

            logger.info("默认总库及分类初始化完成")
            return library, ""

        except Exception as e:
            logger.exception(f"初始化默认总库失败: {e}")
            return None, f"初始化默认总库失败: {str(e)}"
