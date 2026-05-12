# -*- coding: utf-8 -*-
"""
项目管理服务
"""
import uuid
from datetime import datetime
from typing import List, Optional, Tuple
from pathlib import Path

from src.dao.project_dao import ProjectDAO
from src.dao.template_dao import TemplateDAO
from src.models.project import Project
from src.core.constants import BusinessLine, ProjectStatus, BUSINESS_LINE_DESC
from src.core.config import Config
from src.utils.path_utils import get_project_path, ensure_directory
from src.utils.validators import validate_project_name, validate_business_line, validate_template_id
from src.utils.logger import setup_logger

# 延迟导入 SpecService 避免循环依赖

logger = setup_logger(__name__)

class ProjectService:
    """项目管理服务类"""
    
    @staticmethod
    def _resolve_template_path(file_def: dict, template_vars: dict) -> Path:
        """
        解析模板文件路径，替换其中的占位符
        
        Args:
            file_def: 模板文件定义字典（包含path字段）
            template_vars: 模板变量字典
            
        Returns:
            解析后的Path对象
        """
        raw_path = file_def.get("path", "")
        
        # 替换所有模板变量
        resolved_path = raw_path
        for var_name, var_value in template_vars.items():
            placeholder = f"{{{var_name}}}"
            if placeholder in resolved_path:
                resolved_path = resolved_path.replace(placeholder, str(var_value))
        
        return Path(resolved_path)
    
    def __init__(self, project_dao=None, template_dao=None, config=None):
        """初始化项目服务
        
        Args:
            project_dao: 项目数据访问对象
            template_dao: 模板数据访问对象
            config: 配置对象
        """
        self.project_dao = project_dao or ProjectDAO
        self.template_dao = template_dao or TemplateDAO
        self.config = config or Config
    
    def create_project(
        self,
        business_line: str,
        name: str,
        template_id: str,
        manager: Optional[str] = None,
        description: Optional[str] = None,
        custom_path: Optional[str] = None,
        library_id: Optional[str] = "LIB-DEFAULT-001"  # 新增参数，默认关联默认总库
    ) -> tuple[Optional[Project], str]:
        """
        创建新项目
        
        Returns:
            (项目对象, 错误信息)，创建成功时错误信息为空
        """
        # 验证输入
        valid, msg = validate_business_line(business_line)
        if not valid:
            return None, msg
        
        valid, msg = validate_project_name(name)
        if not valid:
            return None, msg
        
        valid, msg = validate_template_id(template_id)
        if not valid:
            return None, msg
        
        # 验证模板是否存在
        template = self.template_dao.get_by_id(template_id)
        if not template:
            return None, "模板不存在"
        
        try:
            business_line_enum = BusinessLine(business_line)
        except ValueError:
            return None, "无效的业务线类型"
        
        # 生成项目ID
        project_id = f"PRJ-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
        
        # 生成项目编号（使用事务确保原子性）
        year = datetime.now().year
        
        # 尝试生成唯一的项目编号，处理并发冲突
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                # 获取最大序号并加1
                max_seq = self.project_dao.get_max_sequence(business_line_enum, year)
                sequence = max_seq + 1
                project_code = f"{business_line}-{year}-{sequence:03d}"
                
                # 生成项目路径（带自动回退）
                base_path = custom_path or self.config.get("default_project_path")

                # 验证并回退无效的基础路径
                validated_base_path = None
                fallback_used = False
                fallback_reason = ""

                if base_path:
                    # 尝试使用传入的自定义路径或配置路径
                    test_path = Path(base_path)
                    if test_path.exists() and test_path.is_dir():
                        # 检查是否可写
                        try:
                            test_file = test_path / ".write_test_tmp"
                            test_file.touch()
                            test_file.unlink()
                            validated_base_path = base_path
                        except Exception as e:
                            fallback_reason = f"原路径不可写: {str(e)}"
                            logger.warning(f"基础路径不可写: {base_path}, 原因: {e}")
                            fallback_used = True
                    else:
                        fallback_reason = f"基础路径不存在: {base_path}"
                        logger.warning(f"基础路径不存在: {base_path}")
                        fallback_used = True

                # 如果原始路径无效，尝试自动检测可用路径
                if not validated_base_path:
                    logger.info("开始自动检测可用的项目基础路径...")

                    try:
                        from src.services.library_service import LibraryService
                        detected_path = LibraryService._detect_project_base_path()

                        # 验证检测到的路径
                        if detected_path:
                            test_detected = Path(detected_path)
                            try:
                                test_file = test_detected / ".write_test_tmp"
                                test_file.touch()
                                test_file.unlink()
                                validated_base_path = detected_path
                                logger.info(f"使用自动检测到的路径: {detected_path}")
                            except Exception as e:
                                logger.warning(f"检测到的路径也不可写: {detected_path}, 错误: {e}")
                    except Exception as detect_error:
                        logger.exception(f"自动检测路径失败: {detect_error}")

                # 最终兜底：使用用户主目录
                if not validated_base_path:
                    home_dir = Path.home()
                    validated_base_path = str(home_dir / "PythonProjects")
                    logger.warning(f"所有路径检测失败，最终使用用户主目录: {validated_base_path}")

                # 生成完整的项目路径
                project_path = get_project_path(validated_base_path, project_code, name)

                # 记录是否使用了回退路径
                if fallback_used or (custom_path and validated_base_path != custom_path):
                    logger.info(f"⚠️ 项目路径已自动调整:")
                    logger.info(f"   原始路径: {custom_path or 'N/A'}")
                    logger.info(f"   实际使用: {validated_base_path}")
                    if fallback_reason:
                        logger.info(f"   回退原因: {fallback_reason}")

                # 检查路径是否已存在
                if project_path.exists():
                    logger.warning(f"项目路径已存在: {project_path}，尝试重新生成序号")
                    continue

                # 检查项目编号是否已存在
                if self.project_dao.get_by_code(project_code):
                    logger.warning(f"项目编号已存在: {project_code}，尝试重新生成序号")
                    continue

                # 创建项目对象
                project = Project(
                    project_id=project_id,
                    code=project_code,
                    name=name,
                    business_line=business_line_enum,
                    template_id=template_id,
                    manager=manager,
                    description=description,
                    path=str(project_path),
                    sequence=sequence
                )

                # 创建项目目录结构（使用新的返回值格式）
                success, dir_error = ensure_directory(project_path)
                if not success:
                    error_msg = f"创建项目目录失败: {dir_error}"
                    logger.error(error_msg)

                    # 提供更友好的错误提示
                    if "权限不足" in dir_error:
                        user_msg = "权限不足：无法创建项目目录，请检查文件夹权限设置"
                    elif "路径不存在" in dir_error or "路径无效" in dir_error:
                        user_msg = "目标路径不存在，请选择有效的保存位置"
                    elif "路径过长" in dir_error:
                        user_msg = "项目路径过长（超过260字符），请使用较短的项目名称"
                    elif "磁盘空间" in dir_error:
                        user_msg = "磁盘空间不足，无法创建项目目录"
                    else:
                        user_msg = f"创建项目目录失败：{dir_error}"

                    return None, user_msg

                logger.info(f"✅ 将在以下路径创建项目: {project_path}")
                
                # 根据模板生成目录结构
                for dir_def in template.structure:
                    dir_path = project_path / dir_def["path"]
                    if not ensure_directory(dir_path):
                        logger.warning(f"创建目录失败: {dir_path}")
                
                # 生成模板文件
                create_date = datetime.now().strftime("%Y-%m-%d")
                business_line_desc = BUSINESS_LINE_DESC.get(business_line_enum, business_line_enum.value)
                
                # 模板变量
                template_vars = {
                    "project_code": project_code,
                    "project_name": name,
                    "business_line": business_line_desc,
                    "manager": manager or "",
                    "description": description or "",
                    "create_date": create_date,
                    "template_id": template_id,
                    "template_name": template.name,
                    # 新增：支持模板中使用的中文变量名（向后兼容）
                    "序号": "001",                    # 变更单默认序号
                    "current_date": create_date,      # 编制日期别名
                    "seq_no": "001",                  # 英文别名（推荐新模板使用）
                }
                
                # 生成文件（优先使用规范中心模板）
                from src.services.spec_service import SpecService

                # 文档规范追踪字典
                doc_specs = {}

                for file_def in template.templates:
                    try:
                        file_path = project_path / ProjectService._resolve_template_path(file_def, template_vars)
                        # 确保父目录存在
                        ensure_directory(file_path.parent)

                        # 优先从规范中心获取内容
                        content = None
                        source_spec_id = None
                        source_spec_version = None

                        if "spec_id" in file_def:
                            spec_content, _ = SpecService.get_spec_content(file_def["spec_id"])
                            if spec_content:
                                content = spec_content.format(**template_vars)
                                source_spec_id = file_def["spec_id"]
                                # 获取规范版本
                                spec_obj = SpecService.get_spec(file_def["spec_id"])
                                source_spec_version = spec_obj.version if spec_obj else "UNKNOWN"
                                logger.info(f"文档 {file_def['path']} 使用规范 {file_def['spec_id']} V{source_spec_version}")
                            else:
                                logger.warning(f"规范 {file_def['spec_id']} 未找到，使用fallback模板: {file_def['path']}")

                        # Fallback: 使用硬编码内容
                        if content is None:
                            content = file_def["content"].format(**template_vars)

                        # 写入文件
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(content)
                        logger.info(f"生成模板文件: {file_path}")

                        # 记录文档元数据到追踪字典
                        if source_spec_id:
                            doc_specs[str(file_path.relative_to(project_path))] = {
                                "spec_id": source_spec_id,
                                "spec_version": source_spec_version,
                                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }

                    except Exception as e:
                        logger.warning(f"生成模板文件失败 {file_def['path']}: {e}")

                # 保存文档规范元数据到项目对象
                if doc_specs:
                    project.document_specs = doc_specs
                
                # 自动为空目录生成README占位符 (解决空壳问题)
                readme_count = 0
                for dir_def in template.structure:
                    dir_path = project_path / dir_def["path"]
                    if not dir_path.exists():
                        continue
                    
                    # 检查目录是否已有非配置文件
                    existing_files = [
                        f for f in dir_path.iterdir() 
                        if f.is_file() and f.name not in ['.gitignore', '.gitkeep', 'README.md']
                    ]
                    
                    # 如果目录为空或只有.gitignore，自动生成README
                    if not existing_files:
                        readme_path = dir_path / "README.md"
                        if not readme_path.exists():
                            dir_description = dir_def.get("description", dir_path.name)
                            readme_content = f"""# {dir_description}

## 目录说明
- **用途**: {dir_description}
- **状态**: 待填充
- **创建时间**: {create_date}

## 文件清单
(暂无文件，请根据项目需要添加相关文档)

## 使用指南
1. 根据项目实际情况在此目录添加相关文件
2. 建议遵循项目命名规范
3. 重要文件请及时提交版本控制

---
**所属项目**: {project_code} - {name}
**生成工具**: SW-2026-004 Python项目管理工具 V2.1.0
"""
                            try:
                                with open(readme_path, 'w', encoding='utf-8') as f:
                                    f.write(readme_content)
                                readme_count += 1
                                logger.debug(f"自动生成README: {readme_path}")
                            except Exception as readme_error:
                                logger.warning(f"生成README失败 {readme_path}: {readme_error}")
                
                if readme_count > 0:
                    logger.info(f"已为 {readme_count} 个空目录自动生成README占位符")
                
                # 保存到数据库
                project = self.project_dao.create(project)
                logger.info(f"项目创建成功: {project_code} {name}")
                
                # 关联到总库
                if library_id and project:
                    from src.services.library_service import LibraryService
                    # 先确保总库存在（如果传入的是默认ID但总库还没初始化）
                    lib = LibraryService.get_library(library_id)
                    if not lib and library_id == "LIB-DEFAULT-001":
                        lib, _ = LibraryService.initialize_default_library()
                    
                    if lib:
                        # ✅ FIX: 使用实际获取到的总库 ID，而不是硬编码的参数值
                        actual_library_id = lib.library_id
                        add_ok, add_msg = LibraryService.add_project_to_library(
                            library_id=actual_library_id,  # ✓ 使用正确的 ID
                            project_id=project.project_id
                        )
                        if add_ok:
                            logger.info(f"项目 {project.code} 已自动归档到总库 {lib.name} (ID={actual_library_id})")
                        else:
                            logger.error(f"⚠️ 项目归档到总库失败: {add_msg} (目标总库ID: {actual_library_id})")
                
                # 初始化变更管理目录和初始文件（增强版）
                try:
                    self._initialize_change_management(project, template)
                    logger.info(f"✅ 项目 {project_code} 变更管理模块初始化成功")
                except Exception as chg_err:
                    # 变更管理初始化失败不应阻止项目创建，但需要明确记录
                    logger.error(f"⚠️ 项目 {project_code} 变更管理初始化失败（项目已创建但变更管理功能可能受限）: {chg_err}")
                    # 可以考虑在这里添加一个标志到 project 对象，标记变更管理未初始化
                    # 以便后续功能检查时可以提示用户

                return project, ""
                
            except Exception as e:
                logger.exception(f"创建项目失败 (尝试 {attempt+1}/{max_attempts}): {e}")
                
                # 回滚：删除已创建的目录
                if 'project_path' in locals() and project_path.exists():
                    import shutil
                    try:
                        shutil.rmtree(project_path, ignore_errors=True)
                        logger.info(f"已清理临时目录: {project_path}")
                    except Exception as cleanup_error:
                        logger.warning(f"清理临时目录失败: {cleanup_error}")
                
                # 分析异常类型，提供更具体的错误信息
                error_message = "创建项目失败"
                import traceback
                error_info = traceback.format_exc()
                
                if "permission denied" in str(e).lower():
                    error_message = "权限不足：无法创建项目目录，请检查权限设置"
                elif "no such file or directory" in str(e).lower():
                    error_message = "路径不存在：无法创建项目目录，请检查路径是否正确"
                elif "already exists" in str(e).lower():
                    error_message = "项目已存在：该项目编号或路径已被使用"
                elif "database" in str(e).lower():
                    error_message = "数据库错误：无法保存项目信息，请检查数据库连接"
                else:
                    error_message = f"创建项目失败: {str(e)}"
                
                # 如果是最后一次尝试，返回错误
                if attempt == max_attempts - 1:
                    return None, error_message
                
                # 等待一段时间后重试
                import time
                time.sleep(0.1)
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """获取项目详情"""
        return self.project_dao.get_by_id(project_id)
    
    def get_project_by_code(self, code: str) -> Optional[Project]:
        """根据项目编号获取项目"""
        return self.project_dao.get_by_code(code)
    
    def list_projects(
        self,
        status: Optional[str] = None,
        business_line: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[Project], int]:
        """查询项目列表"""
        status_enum = ProjectStatus(status) if status else None
        business_line_enum = BusinessLine(business_line) if business_line else None
        
        return self.project_dao.list(
            status=status_enum,
            business_line=business_line_enum,
            keyword=keyword,
            page=page,
            size=size
        )
    
    def update_project(self, project_id: str, data: dict) -> tuple[Optional[Project], str]:
        """更新项目信息"""
        # 验证输入
        if "name" in data:
            valid, msg = validate_project_name(data["name"])
            if not valid:
                return None, msg
        
        if "business_line" in data:
            valid, msg = validate_business_line(data["business_line"])
            if not valid:
                return None, msg
        
        try:
            project = self.project_dao.update(project_id, data)
            if not project:
                return None, "项目不存在"
            
            logger.info(f"项目更新成功: {project.code}")
            return project, ""
            
        except Exception as e:
            logger.exception(f"更新项目失败: {e}")
            return None, f"更新项目失败: {str(e)}"
    
    def delete_project(self, project_id: str, hard_delete: bool = False, delete_local_files: bool = False) -> tuple[bool, str]:
        """删除项目
        Args:
            project_id: 项目ID
            hard_delete: 是否硬删除，True=彻底删除数据库记录
            delete_local_files: 是否删除本地项目文件
        """
        import shutil
        from pathlib import Path
        
        try:
            # 先获取项目信息
            project = self.project_dao.get_by_id(project_id)
            if not project:
                return False, "项目不存在"
            
            project_path = Path(project.path)
            
            # 删除本地文件
            if delete_local_files and project_path.exists():
                try:
                    shutil.rmtree(project_path)
                    logger.info(f"已删除本地项目文件: {project_path}")
                except Exception as e:
                    logger.warning(f"删除本地文件失败: {e}")
                    return False, f"删除本地文件失败: {str(e)}"
            
            # 删除数据库记录
            success = self.project_dao.delete(project_id, hard_delete=hard_delete)
            if not success:
                return False, "删除数据库记录失败"
            
            if hard_delete:
                logger.info(f"项目已彻底删除: {project.code}")
            else:
                logger.info(f"项目已归档: {project.code}")
            
            return True, ""
            
        except Exception as e:
            logger.exception(f"删除项目失败: {e}")
            return False, f"删除项目失败: {str(e)}"
    
    def generate_project_code(self, business_line: str) -> tuple[Optional[str], str]:
        """生成项目编号（不创建项目）"""
        valid, msg = validate_business_line(business_line)
        if not valid:
            return None, msg
        
        try:
            business_line_enum = BusinessLine(business_line)
            year = datetime.now().year
            max_seq = self.project_dao.get_max_sequence(business_line_enum, year)
            sequence = max_seq + 1
            project_code = f"{business_line}-{year}-{sequence:03d}"
            return project_code, ""
            
        except Exception as e:
            logger.exception(f"生成项目编号失败: {e}")
            return None, f"生成项目编号失败: {str(e)}"
    
    def get_statistics(self) -> dict:
        """获取项目统计信息"""
        try:
            total = self.project_dao.count_by_status()
            active = self.project_dao.count_by_status(ProjectStatus.ACTIVE)
            completed = self.project_dao.count_by_status(ProjectStatus.COMPLETED)
            archived = self.project_dao.count_by_status(ProjectStatus.ARCHIVED)
            paused = self.project_dao.count_by_status(ProjectStatus.PAUSED)
            
            return {
                "total": total,
                "active": active,
                "completed": completed,
                "archived": archived,
                "paused": paused
            }
        except Exception as e:
            logger.exception(f"获取统计信息失败: {e}")
            return {}
    
    def import_project(
        self,
        business_line: str,
        name: str,
        template_id: str,
        path: str,
        manager: Optional[str] = None,
        description: Optional[str] = None
    ) -> tuple[Optional[Project], str]:
        """
        导入现有项目
        
        Args:
            business_line: 业务线类型
            name: 项目名称
            template_id: 模板ID
            path: 项目路径
            manager: 项目负责人
            description: 项目描述
            
        Returns:
            (项目对象, 错误信息)，导入成功时错误信息为空
        """
        # 验证输入
        valid, msg = validate_business_line(business_line)
        if not valid:
            return None, msg
        
        valid, msg = validate_project_name(name)
        if not valid:
            return None, msg
        
        valid, msg = validate_template_id(template_id)
        if not valid:
            return None, msg
        
        # 验证模板是否存在
        template = self.template_dao.get_by_id(template_id)
        if not template:
            return None, "模板不存在"
        
        # 验证路径是否存在
        project_path = Path(path)
        if not project_path.exists():
            return None, f"项目路径不存在: {path}"
        
        try:
            business_line_enum = BusinessLine(business_line)
        except ValueError:
            return None, "无效的业务线类型"
        
        # 生成项目编号
        year = datetime.now().year
        max_seq = self.project_dao.get_max_sequence(business_line_enum, year)
        sequence = max_seq + 1
        project_code = f"{business_line}-{year}-{sequence:03d}"
        
        # 检查项目编号是否已存在
        if self.project_dao.get_by_code(project_code):
            return None, f"项目编号已存在: {project_code}"
        
        # 创建项目ID
        project_id = f"PRJ-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
        
        # 创建项目对象
        project = Project(
            project_id=project_id,
            code=project_code,
            name=name,
            business_line=business_line_enum,
            template_id=template_id,
            manager=manager,
            description=description,
            path=str(project_path),
            sequence=sequence
        )
        
        try:
            # 保存到数据库
            project = self.project_dao.create(project)
            logger.info(f"项目导入成功: {project_code} {name}")
            return project, ""
            
        except Exception as e:
            logger.exception(f"导入项目失败: {e}")
            return None, f"导入项目失败: {str(e)}"
    
    def scan_and_import_projects(self, root_path: str, business_line: str, template_id: str) -> tuple[List[Project], List[str]]:
        """
        扫描指定目录并导入所有Python项目
        
        Args:
            root_path: 根目录路径
            business_line: 业务线类型
            template_id: 模板ID
            
        Returns:
            (成功导入的项目列表, 失败的项目列表)
        """
        success_projects = []
        failed_projects = []
        
        root = Path(root_path)
        if not root.exists():
            failed_projects.append(f"根目录不存在: {root_path}")
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
                    project, msg = self.import_project(
                        business_line=business_line,
                        name=project_name,
                        template_id=template_id,
                        path=project_path
                    )
                    
                    if project:
                        success_projects.append(project)
                    else:
                        failed_projects.append(f"{project_name}: {msg}")
        
        return success_projects, failed_projects
    
    def change_template(self, project_id: str, template_id: str) -> tuple[Optional[Project], str]:
        """
        为现有项目更改模板
        
        Args:
            project_id: 项目ID
            template_id: 新模板ID
            
        Returns:
            (项目对象, 错误信息)，更改成功时错误信息为空
        """
        # 验证模板是否存在
        template = self.template_dao.get_by_id(template_id)
        if not template:
            return None, "模板不存在"
        
        # 获取项目信息
        project = self.project_dao.get_by_id(project_id)
        if not project:
            return None, "项目不存在"
        
        try:
            project_path = Path(project.path)
            if not project_path.exists():
                return None, "项目路径不存在"
            
            # 生成模板变量
            create_date = project.created_at.strftime("%Y-%m-%d") if project.created_at else datetime.now().strftime("%Y-%m-%d")
            business_line_desc = BUSINESS_LINE_DESC.get(project.business_line, project.business_line.value)
            
            template_vars = {
                "project_code": project.code,
                "project_name": project.name,
                "business_line": business_line_desc,
                "manager": project.manager or "",
                "description": project.description or "",
                "create_date": create_date,
                "template_id": template_id,
                "template_name": template.name,
                # 新增：支持模板中使用的中文变量名（向后兼容）
                "序号": "001",                    # 变更单默认序号
                "current_date": create_date,      # 编制日期别名
                "seq_no": "001",                  # 英文别名（推荐新模板使用）
            }

            # 根据新模板生成目录结构
            for dir_def in template.structure:
                dir_path = project_path / dir_def["path"]
                if not ensure_directory(dir_path):
                    logger.warning(f"创建目录失败: {dir_path}")
            
            # 生成模板文件（优先使用规范中心模板）
            from src.services.spec_service import SpecService

            # 文档规范追踪字典
            doc_specs = {}

            for file_def in template.templates:
                try:
                    file_path = project_path / ProjectService._resolve_template_path(file_def, template_vars)
                    # 确保父目录存在
                    ensure_directory(file_path.parent)

                    # 优先从规范中心获取内容
                    content = None
                    source_spec_id = None
                    source_spec_version = None

                    if "spec_id" in file_def:
                        spec_content, _ = SpecService.get_spec_content(file_def["spec_id"])
                        if spec_content:
                            content = spec_content.format(**template_vars)
                            source_spec_id = file_def["spec_id"]
                            # 获取规范版本
                            spec_obj = SpecService.get_spec(file_def["spec_id"])
                            source_spec_version = spec_obj.version if spec_obj else "UNKNOWN"
                            logger.info(f"文档 {file_def['path']} 使用规范 {file_def['spec_id']} V{source_spec_version}")
                        else:
                            logger.warning(f"规范 {file_def['spec_id']} 未找到，使用fallback模板: {file_def['path']}")

                    # Fallback: 使用硬编码内容
                    if content is None:
                        content = file_def["content"].format(**template_vars)

                    # 写入文件
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    logger.info(f"生成模板文件: {file_path}")

                    # 记录文档元数据到追踪字典
                    if source_spec_id:
                        doc_specs[str(file_path.relative_to(project_path))] = {
                            "spec_id": source_spec_id,
                            "spec_version": source_spec_version,
                            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }

                except Exception as e:
                    logger.warning(f"生成模板文件失败 {file_def['path']}: {e}")

            # 更新项目的模板ID和文档规范元数据
            update_data = {"template_id": template_id}
            if doc_specs:
                update_data["document_specs"] = doc_specs

            project = self.project_dao.update(project_id, update_data)
            if not project:
                return None, "更新项目模板ID失败"
            
            logger.info(f"项目模板变更成功: {project.code} {project.name} -> 模板 {template_id}")
            return project, ""

        except Exception as e:
            logger.exception(f"更改模板失败: {e}")
            return None, f"更改模板失败: {str(e)}"

    def _initialize_change_management(self, project, template):
        """
        初始化变更管理目录和初始文件（增强版）

        Args:
            project: 项目对象
            template: 使用的模板对象
        """
        from pathlib import Path
        from datetime import datetime

        base_chg_path = Path(project.path) / "00_项目管理" / "04_变更管理"

        try:
            # 0. 验证项目路径是否存在
            if not Path(project.path).exists():
                logger.error(f"❌ 变更管理初始化失败: 项目路径不存在 {project.path}")
                return

            logger.info(f"📁 开始初始化变更管理目录: {base_chg_path}")

            # 1. 创建基础目录（确保父目录存在）
            try:
                base_chg_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"✅ 创建基础目录成功: {base_chg_path}")
            except Exception as dir_err:
                logger.error(f"❌ 创建基础目录失败: {base_chg_path}, 错误: {dir_err}")
                raise

            # 2. 创建必需子目录
            subdirs = [
                ("01_变更单", True),
                ("04_变更记录", True)
            ]

            for subdir_name, required in subdirs:
                subdir_path = base_chg_path / subdir_name
                try:
                    subdir_path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"  ✅ 创建子目录: {subdir_name}")
                except Exception as sub_err:
                    if required:
                        logger.error(f"  ❌ 创建必需子目录失败: {subdir_name}, 错误: {sub_err}")
                        raise
                    else:
                        logger.warning(f"  ⚠️ 创建可选子目录失败: {subdir_name}, 错误: {sub_err}")

            # 3. 创建 .gitkeep 保持 01_变更单 目录结构
            gitkeep_path = base_chg_path / "01_变更单" / ".gitkeep"
            try:
                if not gitkeep_path.exists():
                    gitkeep_path.write_text("# 变更单存放目录\n", encoding='utf-8')
                    logger.info(f"  ✅ 创建 .gitkeep 文件")
            except Exception as gitkeep_err:
                logger.warning(f"  ⚠️ 创建 .gitkeep 失败: {gitkeep_err}")
                # 非致命错误，继续执行

            # 4. 生成初始台帐
            try:
                ledger_content = self._generate_initial_ledger_content(project)
                ledger_path = base_chg_path / "04_变更记录" / f"041_{project.code}_版本变更台帐_CHG-V2.1.0.md"
                if not ledger_path.exists():
                    # 确保父目录存在
                    ledger_path.parent.mkdir(parents=True, exist_ok=True)
                    ledger_path.write_text(ledger_content, encoding='utf-8')
                    logger.info(f"  ✅ 生成初始变更台帐: {ledger_path.name}")
            except Exception as ledger_err:
                logger.error(f"  ❌ 生成初始台帐失败: {ledger_err}")
                raise

            # 5. (可选) 创建 03_变更管理规范/ 目录 - 仅完整版模板
            full_template_ids = ['TPL-FULLLINE-AUTO-001', 'TPL-SINGLE-ROBOT-001',
                               'TPL-UPGRADE-STD-001', 'TPL-UPPER-STD-001']
            if template.template_id in full_template_ids:
                spec_dir = base_chg_path / "03_变更管理规范"
                try:
                    spec_dir.mkdir(exist_ok=True)
                    logger.info(f"  ✅ 创建变更管理规范目录（完整版模板）")
                except Exception as spec_err:
                    logger.warning(f"  ⚠️ 创建变更管理规范目录失败: {spec_err}")

            # 6. 生成 README
            try:
                readme_content = self._generate_change_mgmt_readme(project)
                readme_path = base_chg_path / "README.md"
                if not readme_path.exists():
                    readme_path.write_text(readme_content, encoding='utf-8')
                    logger.info(f"  ✅ 生成变更管理 README")
            except Exception as readme_err:
                logger.warning(f"  ⚠️ 生成 README 失败: {readme_err}")
                # 非致命错误，继续执行

            # 7. 最终验证：确认关键目录和文件已创建
            validation_errors = []
            critical_paths = [
                (base_chg_path / "01_变更单", "目录"),
                (base_chg_path / "04_变更记录", "目录"),
                (base_chg_path / "04_变更记录" / f"041_{project.code}_版本变更台帐_CHG-V2.1.0.md", "文件"),
            ]

            for check_path, path_type in critical_paths:
                if not check_path.exists():
                    validation_errors.append(f"{path_type}不存在: {check_path.name}")

            if validation_errors:
                error_msg = f"变更管理初始化验证失败: {'; '.join(validation_errors)}"
                logger.error(f"❌ {error_msg}")
                # 抛出异常让调用者知道初始化未完全成功
                raise RuntimeError(error_msg)
            else:
                logger.info(f"✅ 变更管理初始化完成并通过验证: {base_chg_path}")

        except Exception as e:
            # 区分致命错误和非致命错误
            error_msg = f"⚠️ 变更管理初始化失败（可能影响功能）: {e}"
            logger.exception(error_msg)
            # 不再静默吞掉异常，使用 ERROR 级别记录，但仍然不阻止项目创建
            # 这样可以让用户在日志中看到明确的错误信息

    def _generate_initial_ledger_content(self, project):
        """生成初始台帐内容"""
        from datetime import datetime

        return f"""# {project.code} 版本变更台帐

## 1. 项目信息
- **项目代码**: {project.code}
- **项目名称**: {project.name}
- **项目版本**: V1.0.0

## 2. 变更记录
| 变更单号 | 变更类型 | 变更标题 | 申请日期 | 申请人 | 审批状态 | 实施日期 | 影响文件数 |
|---------|---------|---------|---------|--------|---------|---------|-----------|
| (暂无变更记录) | | | | | | | |

## 3. 版本统计
| 版本 | 变更单数 | 变更日期范围 | 主要变更内容 |
|------|---------|-------------|-------------|
| V1.0.0 | 0 | - | 初始版本 |

---
**文档版本**: CHG-V2.1.0
**编制日期**: {datetime.now().strftime('%Y-%m-%d')}
**编制人**: 系统
"""

    def _generate_change_mgmt_readme(self, project):
        """生成变更管理 README"""
        from datetime import datetime

        return f"""# 变更管理目录

## 目录结构

本目录按照 Obsidian 规范 06_项目模板规范 组织。

### 01_变更单/
存放所有变更单文件，采用扁平结构（按序号排列）。
- 命名格式：`040_{{project_code}}_变更单{{序号}}_CHG-V2.0.0.md`
- 示例：`040_{project.code}_变更单 001_CHG-V2.0.0.md`

### 03_变更管理规范/ （可选）
存放变更管理流程规范说明文件。

### 04_变更记录/
存放版本变更台帐文件。
- 文件名：`041_{{project_code}}_版本变更台帐_CHG-V2.1.0.md`
- 记录所有变更历史和版本统计

## 使用方式
1. 创建变更单 → 工具自动生成到 `01_变更单/`
2. 更新台帐 → 工具自动刷新 `04_变更记录/` 下的台帐文件

---
**最后更新**: {datetime.now().strftime('%Y-%m-%d')}
"""

    def diagnose_and_fix_change_management(self, project_id: str) -> tuple[bool, str, list]:
        """
        诊断并修复现有项目中缺失的变更管理目录

        Args:
            project_id: 项目ID

        Returns:
            (是否需要修复, 修复结果描述, 修复的操作列表) 元组
        """
        from pathlib import Path

        # 获取项目信息
        project = self.get_project(project_id)
        if not project:
            return False, "项目不存在", []

        # 获取模板信息
        template = self.template_dao.get_by_id(project.template_id)
        if not template:
            return False, f"模板不存在: {project.template_id}", []

        project_path = Path(project.path)
        if not project_path.exists():
            return False, f"项目路径不存在: {project.path}", []

        base_chg_path = project_path / "00_项目管理" / "04_变更管理"

        # 检查缺失的组件
        missing_items = []
        required_components = [
            ("01_变更单", "directory"),
            ("01_变更单/.gitkeep", "file"),
            ("04_变更记录", "directory"),
            (f"04_变更记录/041_{project.code}_版本变更台帐_CHG-V2.1.0.md", "file"),
            ("README.md", "file"),
        ]

        # 检查可选组件
        full_template_ids = ['TPL-FULLLINE-AUTO-001', 'TPL-SINGLE-ROBOT-001',
                           'TPL-UPGRADE-STD-001', 'TPL-UPPER-STD-001']
        if template.template_id in full_template_ids:
            required_components.append(("03_变更管理规范", "directory"))

        for component_name, comp_type in required_components:
            comp_path = base_chg_path / component_name
            if comp_type == "directory":
                if not comp_path.is_dir():
                    missing_items.append((component_name, comp_type))
            else:  # file
                if not comp_path.is_file():
                    missing_items.append((component_name, comp_type))

        if not missing_items:
            return True, "✅ 变更管理目录完整，无需修复", []

        # 执行修复
        fix_operations = []
        try:
            logger.info(f"🔧 开始修复项目 {project.code} 的变更管理目录...")

            # 创建基础目录
            if not base_chg_path.exists():
                base_chg_path.mkdir(parents=True, exist_ok=True)
                fix_operations.append(f"创建基础目录: {base_chg_path}")

            # 修复每个缺失的组件
            for component_name, comp_type in missing_items:
                comp_path = base_chg_path / component_name
                try:
                    if comp_type == "directory":
                        comp_path.mkdir(parents=True, exist_ok=True)
                        fix_operations.append(f"✅ 创建目录: {component_name}")
                        logger.info(f"  修复: 创建目录 {component_name}")

                    elif component_name == "01_变更单/.gitkeep":
                        comp_path.write_text("# 变更单存放目录\n", encoding='utf-8')
                        fix_operations.append(f"✅ 创建文件: {component_name}")
                        logger.info(f"  修复: 创建 .gitkeep")

                    elif component_name.endswith("_版本变更台帐_CHG-V2.1.0.md"):
                        ledger_content = self._generate_initial_ledger_content(project)
                        comp_path.parent.mkdir(parents=True, exist_ok=True)
                        comp_path.write_text(ledger_content, encoding='utf-8')
                        fix_operations.append(f"✅ 生成文件: {component_name}")
                        logger.info(f"  修复: 生成初始台帐")

                    elif component_name == "README.md":
                        readme_content = self._generate_change_mgmt_readme(project)
                        comp_path.write_text(readme_content, encoding='utf-8')
                        fix_operations.append(f"✅ 生成文件: {component_name}")
                        logger.info(f"  修复: 生成 README")

                    elif component_name == "03_变更管理规范":
                        comp_path.mkdir(exist_ok=True)
                        fix_operations.append(f"✅ 创建目录: {component_name}")
                        logger.info(f"  修复: 创建变更管理规范目录")

                except Exception as fix_err:
                    error_msg = f"❌ 修复失败 [{component_name}]: {fix_err}"
                    fix_operations.append(error_msg)
                    logger.error(f"  {error_msg}")

            success_count = sum(1 for op in fix_operations if op.startswith("✅"))
            total_fixes = len(missing_items)

            if success_count == total_fixes:
                result_msg = f"✅ 变更管理目录修复完成 ({success_count}/{total_fixes} 项成功)"
                logger.info(f"{result_msg} - 项目: {project.code}")
                return True, result_msg, fix_operations
            else:
                result_msg = f"⚠️ 变更管理目录部分修复 ({success_count}/{total_fixes} 项成功)"
                logger.warning(f"{result_msg} - 项目: {project.code}")
                return False, result_msg, fix_operations

        except Exception as e:
            error_msg = f"❌ 变更管理目录修复过程出错: {e}"
            logger.exception(error_msg)
            return False, error_msg, fix_operations


_project_service_instance = None

def _get_project_service_instance():
    global _project_service_instance
    if _project_service_instance is None:
        _project_service_instance = ProjectService()
    return _project_service_instance

_original_methods = {
    'create_project': ProjectService.create_project,
    'get_project': ProjectService.get_project,
    'get_project_by_code': ProjectService.get_project_by_code,
    'list_projects': ProjectService.list_projects,
    'update_project': ProjectService.update_project,
    'delete_project': ProjectService.delete_project,
    'generate_project_code': ProjectService.generate_project_code,
    'get_statistics': ProjectService.get_statistics,
    'import_project': ProjectService.import_project,
    'scan_and_import_projects': ProjectService.scan_and_import_projects,
    'change_template': ProjectService.change_template,
    'diagnose_and_fix_change_management': ProjectService.diagnose_and_fix_change_management,
}

for _method_name, _method in _original_methods.items():
    @classmethod
    def _static_wrapper(cls, *args, __method=_method, **kwargs):
        return __method(_get_project_service_instance(), *args, **kwargs)
    setattr(ProjectService, _method_name, _static_wrapper)
