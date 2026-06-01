# -*- coding: utf-8 -*-
"""
模板服务 - 管理内置和自定义项目模板

提供项目结构模板的定义、加载和应用功能。
支持JSON格式的模板配置文件。
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class TemplateService:
    """模板服务类 - 管理PLC项目结构模板"""

    _templates: Dict[str, Dict] = {}
    _initialized: bool = False

    @classmethod
    def initialize_builtin_templates(cls):
        """初始化内置模板"""
        if cls._initialized:
            return

        template_dir = (
            Path(__file__).parent.parent
            / "templates"
            / "project_structures"
        )

        if template_dir.exists():
            for json_file in template_dir.glob("*.json"):
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        tpl_data = json.load(f)
                        tpl_id = tpl_data.get("id", json_file.stem)
                        cls._templates[tpl_id] = tpl_data
                        logger.debug(f"已加载模板: {tpl_id} from {json_file.name}")
                except (json.JSONDecodeError, IOError) as e:
                    logger.warning(f"模板文件加载失败 {json_file}: {e}")

        cls._initialized = True
        logger.info(f"模板初始化完成, 共 {len(cls._templates)} 个模板")

    @classmethod
    def get_template(cls, template_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取模板定义"""
        if not cls._initialized:
            cls.initialize_builtin_templates()
        return cls._templates.get(template_id)

    @classmethod
    def get_all_templates(cls) -> List[Dict[str, Any]]:
        """获取所有可用模板列表"""
        if not cls._initialized:
            cls.initialize_builtin_templates()
        return list(cls._templates.values())

    @classmethod
    def get_template_metadata(cls) -> List[Dict[str, Any]]:
        """获取模板元数据摘要（不含完整结构定义）"""
        if not cls._initialized:
            cls.initialize_builtin_templates()

        metadata = []
        for tpl_id, tpl_data in cls._templates.items():
            metadata.append({
                "id": tpl_id,
                "name": tpl_data.get("name", tpl_id),
                "version": tpl_data.get("version", "V1.0.0"),
                "description": tpl_data.get("description", ""),
                "business_lines": tpl_data.get("business_lines", []),
                "is_builtin": tpl_data.get("is_builtin", True),
            })
        return metadata

    @classmethod
    def apply_template(
        cls,
        template_id: str,
        target_path: str,
        variables: Dict[str, str] = None,
    ) -> tuple:
        """
        应用模板到目标路径

        Args:
            template_id: 模板ID
            target_path: 目标项目路径
            variables: 模板变量替换字典

        Returns:
            tuple: (success: bool, message: str)
        """
        template = cls.get_template(template_id)
        if not template:
            return False, f"模板不存在: {template_id}"

        try:
            structure = template.get("structure", {})
            variables = variables or {}

            # 遍历模板结构创建目录和文件
            cls._apply_structure(structure, Path(target_path), variables)

            return True, f"模板 '{template.get('name', template_id)}' 已应用"
        except Exception as e:
            logger.exception(f"模板应用失败: {e}")
            return False, str(e)

    @classmethod
    def _apply_structure(
        cls,
        structure,
        base_path: Path,
        variables: Dict[str, str],
    ):
        """递归应用目录结构"""
        if isinstance(structure, list):
            dirs = structure
            files = []
        else:
            dirs = structure.get("directories", [])
            files = structure.get("files", [])

        # 创建子目录
        for dir_info in dirs:
            dir_name = dir_info.get("name", "")
            dir_path = base_path / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)

            # 递归处理嵌套结构
            if "structure" in dir_info:
                cls._apply_structure(dir_info["structure"], dir_path, variables)

        # 创建文件
        for file_info in files:
            file_name = cls._replace_variables(file_info.get("name", ""), variables)
            file_path = base_path / file_name

            content = file_info.get("content", "")
            if content:
                content = cls._replace_variables(content, variables)

            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

    @staticmethod
    def _replace_variables(text: str, variables: Dict[str, str]) -> str:
        """替换模板变量占位符"""
        result = text
        for key, value in variables.items():
            result = result.replace(f"{{{{{key}}}}}", value)
        return result
