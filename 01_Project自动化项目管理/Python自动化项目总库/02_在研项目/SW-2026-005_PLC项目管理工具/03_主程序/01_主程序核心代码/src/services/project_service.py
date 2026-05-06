# -*- coding: utf-8 -*-
"""
项目服务 - 提供项目的CRUD操作和业务逻辑

负责PLC项目的创建、查询、更新、删除等生命周期管理，
以及项目目录结构的初始化。
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from src.core.project import Project
from src.core.constants import BusinessLine, ProjectStatus, TEMPLATE_METADATA, PLCBrand, HMIBrand
from src.services.template_service import TemplateService
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ProjectService:
    """项目服务类 - 管理PLC工程项目的完整生命周期"""

    _projects: dict = {}  # 内存中的项目缓存 (project_id -> Project)

    @classmethod
    def create_project(
        cls,
        name: str,
        business_line: BusinessLine,
        template_id: str,
        manager: str = "",
        description: str = "",
        plc_brand=None,
        hmi_brand=None,
        custom_path: str = None,
    ) -> Tuple[Optional[Project], Optional[str]]:
        """
        创建新项目

        Args:
            name: 项目名称
            business_line: 业务线类型
            template_id: 使用的模板ID
            manager: 项目负责人
            description: 项目描述
            plc_brand: PLC品牌 (默认Codesys)
            hmi_brand: HMI品牌 (默认Weinview)
            custom_path: 自定义存储路径

        Returns:
            Tuple[Project | None, str | None]: (创建的项目对象, 错误信息)
        """
        try:
            # 确定基础路径
            from src.core.config import ConfigLoader
            base_path = Path(custom_path or ConfigLoader.get("default_project_root", "./Projects"))
            base_path.mkdir(parents=True, exist_ok=True)

            # 创建项目实例
            project = Project(
                name=name,
                description=description,
                business_line=business_line,
                manager=manager,
                template_id=template_id,
                path=str(base_path / name),
                plc_brand=plc_brand,
                hmi_brand=hmi_brand,
            )

            # 生成项目编号
            date_str = datetime.now().strftime("%Y%m")
            project.code = f"{business_line.value}-2026-{date_str}-{len(name):03d}"

            # 初始化项目目录结构
            init_error = cls._initialize_project_structure(project)
            if init_error:
                return None, init_error

            # 保存项目元数据
            meta_path = Path(project.path) / "project.json"
            project.save_to_file(str(meta_path))

            # 加入缓存
            cls._projects[project.project_id] = project

            logger.info(f"项目创建成功: {project.code} - {project.name}")
            return project, None

        except Exception as e:
            logger.exception(f"项目创建失败: {e}")
            return None, str(e)

    @classmethod
    def _initialize_project_structure(cls, project: Project) -> Optional[str]:
        """
        根据模板初始化项目目录结构

        Args:
            project: 项目对象

        Returns:
            Optional[str]: 错误信息，None表示成功
        """
        try:
            base = Path(project.path)
            base.mkdir(parents=True, exist_ok=True)

            # 标准PLC项目目录结构
            directories = [
                "01_ProjectInfo",
                "02_Documents",
                "02_Documents/Requirements",
                "02_Documents/Design",
                "02_Documents/Interface",
                "02_Documents/UserManual",
                "03_PLC_Program",
                "03_PLC_Program/Pou",
                "03_PLC_Program/Gvl",
                "04_HMI_Config",
                "05_Variables",
                "06_IO_Allocation",
                "07_Alarms",
                "08_TestReports",
            ]

            for dir_name in directories:
                (base / dir_name).mkdir(parents=True, exist_ok=True)

            # 创建.gitkeep保持空目录
            for dir_name in directories:
                gitkeep = base / dir_name / ".gitkeep"
                if not gitkeep.exists():
                    gitkeep.touch()

            logger.debug(f"项目目录已初始化: {base}")
            return None

        except OSError as e:
            return f"目录创建失败: {e}"

    @classmethod
    def get_project(cls, project_id: str) -> Optional[Project]:
        """根据ID获取项目"""
        return cls._projects.get(project_id)

    @classmethod
    def get_all_projects(cls) -> List[Project]:
        """获取所有已加载的项目列表"""
        return list(cls._projects.values())

    @classmethod
    def load_project_from_path(cls, project_path: str) -> Tuple[Optional[Project], Optional[str]]:
        """
        从路径加载已有项目

        Args:
            project_path: 项目根目录路径

        Returns:
            Tuple[Project | None, str | None]
        """
        meta_file = Path(project_path) / "project.json"
        if not meta_file.exists():
            return None, f"未找到项目文件: {meta_file}"

        try:
            project = Project.load_from_file(str(meta_file))
            if project:
                cls._projects[project.project_id] = project
                logger.info(f"项目已加载: {project.name}")
            return project, None
        except Exception as e:
            return None, f"加载失败: {e}"

    @classmethod
    def delete_project(cls, project_id: str) -> Tuple[bool, Optional[str]]:
        """删除项目（仅从缓存移除，不删除文件）"""
        if project_id in cls._projects:
            del cls._projects[project_id]
            return True, None
        return False, "项目不存在"

    @classmethod
    def scan_projects_directory(cls, directory: str = None) -> List[Project]:
        """
        扫描指定目录下的所有项目

        Args:
            directory: 扫描目录，默认使用配置的默认路径

        Returns:
            List[Project]: 发现的项目列表
        """
        from src.core.config import ConfigLoader
        scan_dir = Path(directory or ConfigLoader.get("default_project_root", "./Projects"))

        projects = []
        if not scan_dir.exists():
            return projects

        for item in scan_dir.iterdir():
            if item.is_dir():
                meta_file = item / "project.json"
                if meta_file.exists():
                    project, error = cls.load_project_from_path(str(item))
                    if project and not error:
                        projects.append(project)

        logger.info(f"目录扫描完成: {scan_dir}, 发现 {len(projects)} 个项目")
        return projects

    @classmethod
    def create_new_project(cls, project_info: Dict[str, Any]) -> Tuple[Optional[Path], Optional[str]]:
        """
        通过向导收集的信息创建新项目

        这是 NewProjectDialog 向导调用的核心创建方法。
        接收向导收集的完整项目信息字典，执行以下操作:
        1. 验证必填字段
        2. 构建项目根目录路径
        3. 加载并应用模板JSON (M001_full.json 或 S001_lite.json)
        4. 根据模板创建目录结构
        5. 创建文档占位文件
        6. 生成 .plc_project.json 元数据文件
        7. 返回创建的项目根路径

        Args:
            project_info: 向导收集的项目信息字典, 包含:
                - project_id (str): 项目编号, 如 "DJ-2026-006"
                - project_name (str): 项目名称, 如 "边框缓存机"
                - parent_dir (str): 父目录路径
                - device_type (str): 设备类型标识
                - device_type_display (str): 设备类型显示名
                - plc_brand (PLCBrand): PLC品牌枚举
                - hmi_brand (HMIBrand|None): HMI品牌枚举
                - io_scale (str): IO规模 ("small"/"medium"/"large")
                - template_id (str): 模板ID
                - owner (str): 项目负责人
                - description (str): 项目描述

        Returns:
            Tuple[Path | None, str | None]: (项目根路径, 错误信息)
                成功时返回 (Path对象, None)
                失败时返回 (None, 错误描述字符串)
        """
        try:
            # ========== Step 1: 验证必填字段 ==========
            required_fields = {
                "project_id": "项目编号",
                "project_name": "项目名称",
                "parent_dir": "父目录",
                "template_id": "模板ID",
            }

            for field, display_name in required_fields.items():
                value = project_info.get(field)
                if not value or (isinstance(value, str) and not value.strip()):
                    return None, f"缺少必填字段: {display_name} ({field})"

            # ========== Step 2: 构建项目根目录路径 ==========
            project_id = project_info["project_id"].strip()
            project_name = project_info["project_name"].strip()
            parent_dir = Path(project_info["parent_dir"].strip())

            if not parent_dir.exists():
                return None, f"父目录不存在: {parent_dir}"

            # 项目根目录格式: {parent_dir}/{project_id}_{project_name}
            project_root = parent_dir / f"{project_id}_{project_name}"
            logger.info(f"准备创建项目目录: {project_root}")

            # ========== Step 3: 确保模板服务已初始化 ==========
            TemplateService.initialize_builtin_templates()

            # ========== Step 4: 加载模板 ==========
            template_id = project_info.get("template_id", "TPL-SINGLE-PLC-M001")
            template = TemplateService.get_template(template_id)

            if not template:
                # 回退到M001完整版
                logger.warning(f"模板 {template_id} 未找到，回退到 M001")
                template = TemplateService.get_template("TPL-SINGLE-PLC-M001")
                if not template:
                    return None, f"无法加载任何项目模板"

            logger.info(f"使用模板: {template.get('name', template_id)}")

            # ========== Step 5: 创建物理目录结构 ==========
            structure = template.get("structure", {})
            directories = structure.get("directories", [])
            created_dirs = cls._create_directory_structure(project_root, directories)
            logger.info(f"已创建 {created_dirs} 个标准目录")

            # ========== Step 6: 创建文档占位文件 ==========
            doc_count = cls._create_document_placeholders(
                project_root,
                template_id,
                project_info,
            )
            logger.info(f"已创建 {doc_count} 个文档占位文件")

            # ========== Step 7: 生成 .plc_project.json 元数据 ==========
            metadata = cls._build_metadata(project_info, template_id)
            meta_path = project_root / ".plc_project.json"

            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            logger.info(f"元数据文件已写入: {meta_path}")

            # ========== Step 8: 创建/更新 Project 对象并加入缓存 ==========
            project = Project(
                name=project_name,
                description=project_info.get("description", ""),
                business_line=BusinessLine.DEVICE,  # 向导创建的都是单机设备项目
                manager=project_info.get("owner", ""),
                template_id=template_id,
                path=str(project_root),
                plc_brand=project_info.get("plc_brand"),
                hmi_brand=project_info.get("hmi_brand"),
            )
            project.code = project_id

            cls._projects[project.project_id] = project

            logger.info(
                f"项目创建成功: {project_id}_{project_name} "
                f"@ {project_root} (模板: {template_id})"
            )

            return project_root, None

        except PermissionError as e:
            error_msg = f"没有写入权限: {e}"
            logger.error(error_msg)
            return None, error_msg
        except OSError as e:
            error_msg = f"文件系统错误: {e}"
            logger.error(error_msg)
            return None, error_msg
        except Exception as e:
            error_msg = f"项目创建异常: {e}"
            logger.exception(error_msg)
            return None, error_msg

    @classmethod
    def _create_directory_structure(
        cls,
        base_path: Path,
        directories: List[Dict],
    ) -> int:
        """
        递归创建模板定义的目录结构

        Args:
            base_path: 基础路径
            directories: 目录定义列表, 每项包含 name 和可选的 structure(嵌套子目录)

        Returns:
            int: 实际创建的目录数量
        """
        count = 0

        for dir_info in directories:
            dir_name = dir_info.get("name", "")
            if not dir_name:
                continue

            dir_path = base_path / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            count += 1

            # 创建 .gitkeep 保持空目录被版本控制跟踪
            gitkeep = dir_path / ".gitkeep"
            if not gitkeep.exists():
                gitkeep.touch(encoding="utf-8")

            # 递归处理嵌套子目录结构
            if "structure" in dir_info:
                nested_count = cls._create_directory_structure(
                    dir_path,
                    dir_info["structure"],
                )
                count += nested_count

        return count

    @classmethod
    def _create_document_placeholders(
        cls,
        project_root: Path,
        template_id: str,
        project_info: Dict[str, Any],
    ) -> int:
        """
        根据模板类型创建文档占位文件

        M001 完整版会创建更多占位文件, S001 精简版只创建核心文件。

        Args:
            project_root: 项目根路径
            template_id: 模板ID
            project_info: 项目信息 (用于填充模板变量)

        Returns:
            int: 创建的文件数量
        """
        count = 0

        # 准备模板变量替换字典
        variables = {
            "PROJECT_ID": project_info.get("project_id", ""),
            "PROJECT_NAME": project_info.get("project_name", ""),
            "DEVICE_TYPE": project_info.get("device_type_display", ""),
            "PLC_BRAND": project_info.get("plc_brand_display", ""),
            "OWNER": project_info.get("owner", ""),
            "DATE": datetime.now().strftime("%Y-%m-%d"),
        }

        if template_id == "TPL-SINGLE-PLC-M001":
            # M001 完整版: 创建完整的占位文件集合
            placeholder_files = [
                {
                    "path": "00_项目基础信息/README.md",
                    "content": (
                        "# {PROJECT_ID} {PROJECT_NAME}\n\n"
                        "> 设备类型: {DEVICE_TYPE}\n"
                        "> PLC品牌: {PLC_BRAND}\n"
                        "> 负责人: {OWNER}\n"
                        "> 创建日期: {DATE}\n\n"
                        "## 项目概述\n\n"
                        "(待补充)\n\n"
                        "---\n"
                        "*由 PLC项目管理工具 自动生成*\n"
                    ).format(**variables),
                },
                {
                    "path": "01_项目文档/01_启动过程/01_项目立项/PRD.md",
                    "content": (
                        "# 产品需求文档 (PRD)\n\n"
                        "**项目**: {PROJECT_ID} {PROJECT_NAME}\n"
                        "**版本**: V1.0.0\n"
                        "**日期**: {DATE}\n\n"
                        "## 1. 背景与目标\n\n(待补充)\n\n"
                        "## 2. 功能需求\n\n(待补充)\n\n"
                        "## 3. 非功能需求\n\n(待补充)\n\n"
                        "---\n"
                        "*由 PLC项目管理工具 自动生成*\n"
                    ).format(**variables),
                },
                {
                    "path": "02_发布说明/RELEASE_NOTES.md",
                    "content": (
                        "# 版本发布说明\n\n"
                        "## V1.0.0 ({DATE})\n\n"
                        "- 初始版本创建\n"
                        "- 基于 TPL-SINGLE-PLC-M001 模板\n\n"
                        "---\n"
                        "*由 PLC项目管理工具 自动生成*\n"
                    ).format(**variables),
                },
                {
                    "path": "05_变量清单/VAR_LIST.md",
                    "content": (
                        "# 全局变量清单\n\n"
                        "**项目**: {PROJECT_ID} {PROJECT_NAME}\n"
                        "**PLC品牌**: {PLC_BRAND}\n\n"
                        "| 变量名 | 数据类型 | 地址 | 描述 |\n"
                        "|--------|----------|------|------|\n"
                        "| (待定义) | | | |\n\n"
                        "---\n"
                        "*由 PLC项目管理工具 自动生成*\n"
                    ).format(**variables),
                },
                {
                    "path": "06_IO分配表/IO_ALLOCATION.md",
                    "content": (
                        "# IO分配表\n\n"
                        "**项目**: {PROJECT_ID} {PROJECT_NAME}\n\n"
                        "## 数字输入 (DI)\n\n"
                        "| 地址 | 符号名 | 描述 | 模块/槽号 |\n"
                        "|------|--------|------|----------|\n"
                        "| (待分配) | | | |\n\n"
                        "## 数字输出 (DO)\n\n"
                        "| 地址 | 符号名 | 描述 | 模块/槽号 |\n"
                        "|------|--------|------|----------|\n"
                        "| (待分配) | | | |\n\n"
                        "## 模拟输入 (AI)\n\n"
                        "| 地址 | 符号名 | 描述 | 范围 |\n"
                        "|------|--------|------|------|\n"
                        "| (待分配) | | | |\n\n"
                        "## 模拟输出 (AO)\n\n"
                        "| 地址 | 符号名 | 描述 | 范围 |\n"
                        "|------|--------|------|------|\n"
                        "| (待分配) | | | |\n\n"
                        "---\n"
                        "*由 PLC项目管理工具 自动生成*\n"
                    ).format(**variables),
                },
                {
                    "path": "07_报警定义/ALARM_CODES.md",
                    "content": (
                        "# 报警码定义\n\n"
                        "**项目**: {PROJECT_ID} {PROJECT_NAME}\n\n"
                        "| 报警码 | 级别 | 触发条件 | 恢复条件 | 描述 |\n"
                        "|--------|------|----------|----------|------|\n"
                        "| (待定义) | | | | |\n\n"
                        "### 报警级别说明\n\n"
                        "- **FATAL** (致命): 需要立即停机\n"
                        "- **ERROR** (错误): 影响功能运行\n"
                        "- **WARNING** (警告): 需要注意但不影响运行\n"
                        "- **INFO** (信息): 状态变化通知\n\n"
                        "---\n"
                        "*由 PLC项目管理工具 自动生成*\n"
                    ).format(**variables),
                },
                {
                    "path": "08_测试报告/TEST_REPORT.md",
                    "content": (
                        "# 测试报告\n\n"
                        "**项目**: {PROJECT_ID} {PROJECT_NAME}\n"
                        "**测试人员**: {OWNER}\n"
                        "**日期**: {DATE}\n\n"
                        "## 1. 测试环境\n\n(待补充)\n\n"
                        "## 2. 功能测试\n\n"
                        "| 用例ID | 测试项 | 预期结果 | 实际结果 | 状态 |\n"
                        "|--------|--------|----------|----------|------|\n"
                        "| TC-001 | (待定义) | | | 待测 |\n\n"
                        "## 3. IO点对点测试\n\n(待补充)\n\n"
                        "## 4. 问题清单\n\n| ID | 问题描述 | 严重程度 | 状态 |\n"
                        "|----|----------|----------|------|\n"
                        "| (待记录) | | | |\n\n"
                        "---\n"
                        "*由 PLC项目管理工具 自动生成*\n"
                    ).format(**variables),
                },
            ]
        else:
            # S001 精简版: 只创建核心文件
            placeholder_files = [
                {
                    "path": "01_Documents/README.md",
                    "content": (
                        "# {PROJECT_ID} {PROJECT_NAME}\n\n"
                        "> 设备类型: {DEVICE_TYPE}\n"
                        "> 创建日期: {DATE}\n\n"
                        "## 项目概述\n\n(待补充)\n\n"
                        "---\n"
                        "*由 PLC项目管理工具 自动生成 (S001精简版)*\n"
                    ).format(**variables),
                },
                {
                    "path": "04_Variables/VAR_LIST.md",
                    "content": (
                        "# 变量清单\n\n"
                        "**项目**: {PROJECT_ID} {PROJECT_NAME}\n\n"
                        "(待定义)\n\n"
                        "---\n"
                        "*由 PLC项目管理工具 自动生成*\n"
                    ).format(**variables),
                },
            ]

        # 写入所有占位文件
        for file_info in placeholder_files:
            file_rel_path = file_info["path"]
            file_content = file_info["content"]

            file_path = project_root / file_rel_path
            file_path.parent.mkdir(parents=True, exist_ok=True)

            if not file_path.exists():
                file_path.write_text(file_content, encoding="utf-8")
                count += 1

        return count

    @classmethod
    def _build_metadata(
        cls,
        project_info: Dict[str, Any],
        template_id: str,
    ) -> Dict[str, Any]:
        """
        构建 .plc_project.json 元数据内容

        Args:
            project_info: 项目信息字典
            template_id: 使用的模板ID

        Returns:
            dict: 元数据字典
        """
        plc_brand = project_info.get("plc_brand")
        hmi_brand = project_info.get("hmi_brand")

        metadata = {
            # ===== 基本信息 =====
            "project_id": project_info.get("project_id", "").strip(),
            "name": project_info.get("project_name", "").strip(),
            "description": project_info.get("description", "").strip(),

            # ===== 设备与技术选型 =====
            "device_type": project_info.get("device_type", ""),
            "device_type_display": project_info.get("device_type_display", ""),
            "plc_brand": plc_brand.value if plc_brand else "",
            "plc_brand_display": project_info.get("plc_brand_display", ""),
            "hmi_brand": hmi_brand.value if hmi_brand else "",
            "hmi_brand_display": project_info.get("hmi_brand_display", ""),

            # ===== IO规模 =====
            "io_scale": project_info.get("io_scale", ""),

            # ===== 模板信息 =====
            "template": template_id,
            "template_display_name": project_info.get("template_display_name", ""),

            # ===== 人员 =====
            "owner": project_info.get("owner", "").strip(),

            # ===== 状态与版本 =====
            "status": "planning",
            "version": "1.0.0",

            # ===== 时间戳 =====
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        return metadata
