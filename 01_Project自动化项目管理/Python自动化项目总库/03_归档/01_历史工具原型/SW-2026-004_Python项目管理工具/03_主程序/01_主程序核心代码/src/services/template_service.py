# -*- coding: utf-8 -*-
"""
模板管理服务

V2.8.0 优化:
- 内置模板从 config/templates/*.yaml 加载（数据与代码分离）
- 自定义模板ID生成改为 TPL-CUSTOM-{YYYYMMDD}-{4位hex}（避免冲突）
- 新增 get_template_for_project() 方法（供 ProjectService 解耦使用）
- 新增 resolve_template() 方法（支持继承合并）
- 新增 check_template_updates() 方法（模板版本管理）
"""
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

from src.dao.template_dao import TemplateDAO
from src.models.template import Template
from src.core.constants import DEFAULT_TEMPLATES
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class TemplateService:
    """模板管理服务类"""

    # 内置模板 YAML 目录
    TEMPLATE_DIR = Path(__file__).parent.parent.parent / "config" / "templates"

    # ──────────────────────────────────────────────
    # 内置模板加载
    # ──────────────────────────────────────────────

    @staticmethod
    def _load_builtin_templates_from_yaml() -> list[dict[str, Any]]:
        """从 config/templates/ 目录加载所有内置模板 YAML 文件"""
        try:
            import yaml
        except ImportError:
            logger.error("PyYAML 未安装，回退到 DEFAULT_TEMPLATES 常量")
            return list(DEFAULT_TEMPLATES)

        template_dir = TemplateService.TEMPLATE_DIR
        if not template_dir.exists():
            logger.warning(f"模板数据目录不存在: {template_dir}，回退到 DEFAULT_TEMPLATES 常量")
            return list(DEFAULT_TEMPLATES)

        templates = []
        for yaml_file in sorted(template_dir.glob("TPL-*.yaml")):
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data and isinstance(data, dict):
                        data["_source_file"] = yaml_file.name
                        templates.append(data)
            except Exception as e:
                logger.error(f"加载模板文件失败 {yaml_file.name}: {e}")

        if not templates:
            logger.warning("YAML 目录为空，回退到 DEFAULT_TEMPLATES 常量")
            return list(DEFAULT_TEMPLATES)

        return templates

    @staticmethod
    def initialize_builtin_templates():
        """初始化内置模板到数据库"""
        try:
            builtin_templates = TemplateService._load_builtin_templates_from_yaml()

            # 清理不在当前内置模板列表中的旧内置模板记录
            valid_builtin_ids = {t.get("id") for t in builtin_templates}
            existing = TemplateDAO.list_all()
            for t in existing:
                if getattr(t, 'is_builtin', False) and getattr(t, 'template_id', '') not in valid_builtin_ids:
                    TemplateDAO.force_delete(getattr(t, 'template_id', ''))

            for template_data in builtin_templates:
                template_id = template_data.get("id", "")
                if not TemplateDAO.exists(template_id):
                    template = Template(
                        template_id=template_id,
                        name=template_data["name"],
                        version=template_data["version"],
                        compiler=template_data.get("compiler"),
                        scene=template_data.get("scene"),
                        description=template_data.get("description", ""),
                        structure=template_data["structure"],
                        templates=template_data.get("templates", []),
                        is_builtin=template_data.get("is_builtin", True),
                        business_lines=template_data.get("business_lines", []),
                        schema_version=template_data.get("schema_version", "1.0"),
                        base_template_id=template_data.get("base_template_id"),
                    )
                    TemplateDAO.create(template)
                    logger.info(f"内置模板已加载: {template_id} {template_data['name']}")
                else:
                    # 已存在的内置模板：更新 schema_version 等新字段
                    existing_tmpl = TemplateDAO.get_by_id(template_id)
                    if existing_tmpl and not getattr(existing_tmpl, 'schema_version', None):
                        TemplateDAO.update(template_id, {
                            "schema_version": template_data.get("schema_version", "1.0"),
                            "base_template_id": template_data.get("base_template_id"),
                        })

            logger.info("所有内置模板初始化完成")
        except Exception as e:
            logger.exception(f"初始化内置模板失败: {e}")

    # ──────────────────────────────────────────────
    # 模板 ID 生成
    # ──────────────────────────────────────────────

    @staticmethod
    def _generate_template_id() -> str:
        """生成唯一自定义模板ID

        格式: TPL-CUSTOM-{YYYYMMDD}-{4位hex}
        示例: TPL-CUSTOM-20260614-A3F2
        """
        date_str = datetime.now().strftime("%Y%m%d")
        short_id = uuid.uuid4().hex[:4].upper()
        candidate = f"TPL-CUSTOM-{date_str}-{short_id}"

        # 极低概率冲突保护
        max_attempts = 10
        attempts = 0
        while TemplateDAO.exists(candidate) and attempts < max_attempts:
            short_id = uuid.uuid4().hex[:4].upper()
            candidate = f"TPL-CUSTOM-{date_str}-{short_id}"
            attempts += 1

        return candidate

    # ──────────────────────────────────────────────
    # CRUD
    # ──────────────────────────────────────────────

    @staticmethod
    def get_template(template_id: str) -> Optional[Template]:
        """获取模板详情"""
        return TemplateDAO.get_by_id(template_id)

    @staticmethod
    def get_template_for_project(template_id: str) -> Optional[dict]:
        """获取模板详情（含继承合并），供 ProjectService 使用

        Returns:
            模板字典（含合并后的 structure/templates），模板不存在返回 None
        """
        resolved = TemplateService.resolve_template(template_id)
        if resolved:
            return resolved

        # 回退：直接从数据库获取
        template = TemplateDAO.get_by_id(template_id)
        if template:
            return template.to_dict()
        return None

    @staticmethod
    def list_templates(
        compiler: Optional[str] = None,
        scene: Optional[str] = None,
        is_builtin: Optional[bool] = None
    ) -> List[Template]:
        """查询模板列表"""
        return TemplateDAO.list(
            compiler=compiler,
            scene=scene,
            is_builtin=is_builtin
        )

    @staticmethod
    def create_template(data: dict) -> tuple[Optional[Template], str]:
        """创建自定义模板"""
        try:
            required_fields = ["name", "version", "structure"]
            for field in required_fields:
                if field not in data:
                    return None, f"缺少必填字段: {field}"

            template_id = data.get("id") or data.get("template_id")
            if template_id:
                if TemplateDAO.exists(template_id):
                    return None, f"模板ID已存在: {template_id}"
            else:
                template_id = TemplateService._generate_template_id()

            # 验证 base_template_id
            base_template_id = data.get("base_template_id")
            if base_template_id and not TemplateDAO.exists(base_template_id):
                return None, f"父模板不存在: {base_template_id}"

            template = Template(
                template_id=template_id,
                name=data["name"],
                version=data["version"],
                compiler=data.get("compiler"),
                scene=data.get("scene"),
                description=data.get("description", ""),
                structure=data["structure"],
                templates=data.get("templates", []),
                is_builtin=data.get("is_builtin", False),
                business_lines=data.get("business_lines", []),
                schema_version=data.get("schema_version", "1.0"),
                base_template_id=base_template_id,
            )

            template = TemplateDAO.create(template)
            logger.info(f"自定义模板创建成功: {template_id} {data['name']}")
            return template, ""

        except Exception as e:
            logger.exception(f"创建模板失败: {e}")
            return None, f"创建模板失败: {str(e)}"

    @staticmethod
    def update_template(template_id: str, data: dict) -> tuple[Optional[Template], str]:
        """更新模板信息"""
        try:
            # 处理传入ORM对象的情况（兼容GUI层调用）
            if hasattr(template_id, 'template_id'):
                template_id = template_id.template_id

            template = TemplateDAO.get_by_id(template_id)
            if not template:
                return None, "模板不存在"

            # 内置模板允许修改非标识字段
            protected_fields = {'template_id', 'is_builtin'}
            invalid_fields = [k for k in data.keys() if k in protected_fields]
            if invalid_fields:
                return None, f"以下字段不允许修改: {', '.join(invalid_fields)}"

            updated_template = TemplateDAO.update(template_id, data)
            logger.info(f"模板更新成功: {template_id}")
            return updated_template, ""

        except Exception as e:
            logger.exception(f"更新模板失败: {e}")
            return None, f"更新模板失败: {str(e)}"

    @staticmethod
    def delete_template(template_id: str) -> tuple[bool, str]:
        """删除模板"""
        try:
            success = TemplateDAO.delete(template_id)
            if not success:
                return False, "模板不存在或为内置模板"

            logger.info(f"模板删除成功: {template_id}")
            return True, ""

        except Exception as e:
            logger.exception(f"删除模板失败: {e}")
            return False, f"删除模板失败: {str(e)}"

    # ──────────────────────────────────────────────
    # 导入/导出
    # ──────────────────────────────────────────────

    @staticmethod
    def export_template(template_id: str) -> tuple[Optional[str], str]:
        """导出模板为JSON字符串"""
        try:
            template = TemplateDAO.get_by_id(template_id)
            if not template:
                return None, "模板不存在"

            template_dict = template.to_dict()
            # 移除不需要的字段
            for field in ["id", "created_at", "updated_at", "is_active"]:
                template_dict.pop(field, None)

            return json.dumps(template_dict, indent=4, ensure_ascii=False), ""

        except Exception as e:
            logger.exception(f"导出模板失败: {e}")
            return None, f"导出模板失败: {str(e)}"

    @staticmethod
    def import_template(json_data: str) -> tuple[Optional[Template], str]:
        """从JSON导入模板"""
        try:
            data = json.loads(json_data)

            required_fields = ["name", "version", "structure"]
            for field in required_fields:
                if field not in data:
                    return None, f"模板数据缺少必填字段: {field}"

            template_id = data.get("id") or data.get("template_id")
            if template_id and TemplateDAO.exists(template_id):
                template_id = TemplateService._generate_template_id()
            elif not template_id:
                template_id = TemplateService._generate_template_id()

            for field in ["id", "created_at", "updated_at"]:
                data.pop(field, None)

            template = Template(
                template_id=template_id,
                name=data["name"],
                version=data["version"],
                compiler=data.get("compiler"),
                scene=data.get("scene"),
                description=data.get("description", ""),
                structure=data["structure"],
                templates=data.get("templates", []),
                is_builtin=False,
                business_lines=data.get("business_lines", []),
                schema_version=data.get("schema_version", "1.0"),
                base_template_id=data.get("base_template_id"),
            )
            template = TemplateDAO.create(template)

            logger.info(f"模板导入成功: {template_id} {data['name']}")
            return template, ""

        except json.JSONDecodeError:
            return None, "JSON格式错误"
        except Exception as e:
            logger.exception(f"导入模板失败: {e}")
            return None, f"导入模板失败: {str(e)}"

    # ──────────────────────────────────────────────
    # 验证
    # ──────────────────────────────────────────────

    @staticmethod
    def validate_template_structure(structure: list) -> tuple[bool, str]:
        """验证模板结构是否合法"""
        if not isinstance(structure, list):
            return False, "结构必须是列表"

        for i, item in enumerate(structure):
            if not isinstance(item, dict):
                return False, f"第{i}项必须是字典"

            if "path" not in item:
                return False, f"第{i}项缺少path字段"

            if not isinstance(item["path"], str):
                return False, f"第{i}项path必须是字符串"

            # 检查路径格式
            if "\\" in item["path"]:
                return False, f"路径必须使用正斜杠: {item['path']}"

            if item["path"].startswith("/") or item["path"].endswith("/"):
                return False, f"路径不能以/开头或结尾: {item['path']}"

        return True, "验证通过"

    # ──────────────────────────────────────────────
    # 模板类型（兼容性方法）
    # ──────────────────────────────────────────────

    @staticmethod
    def get_template_types() -> List[Dict]:
        """获取模板类型列表（按编译器分组）"""
        try:
            templates = TemplateService.list_templates()

            types = {}
            for template in templates:
                compiler = template.compiler or "通用"
                if compiler not in types:
                    types[compiler] = {
                        "type": compiler,
                        "name": compiler,
                        "count": 0,
                        "templates": []
                    }
                types[compiler]["count"] += 1
                types[compiler]["templates"].append({
                    "id": template.template_id,
                    "name": template.name,
                    "version": template.version
                })

            return list(types.values())
        except Exception as e:
            logger.exception(f"获取模板类型失败: {e}")
            return []

    # ──────────────────────────────────────────────
    # 重置与清理
    # ──────────────────────────────────────────────

    @staticmethod
    def reset_builtin_templates():
        """重置所有内置模板为YAML定义的默认值"""
        try:
            existing = TemplateDAO.list_all()
            for t in existing:
                if getattr(t, 'is_builtin', False):
                    TemplateDAO.force_delete(getattr(t, 'template_id', ''))
            TemplateService.initialize_builtin_templates()
            return True, None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def cleanup_orphan_templates():
        """清理数据库中不在DEFAULT_TEMPLATES中的非内置(自定义)模板"""
        try:
            valid_ids = {t.get("id") for t in DEFAULT_TEMPLATES}
            existing = TemplateDAO.list_all()
            deleted = []
            for t in existing:
                tid = getattr(t, 'template_id', '')
                is_builtin = getattr(t, 'is_builtin', False)
                if not is_builtin and tid not in valid_ids:
                    TemplateDAO.force_delete(tid)
                    deleted.append(tid)
            return len(deleted), deleted, None
        except Exception as e:
            return 0, [], str(e)

    # ──────────────────────────────────────────────
    # V2.8.0 新增：模板继承与合并
    # ──────────────────────────────────────────────

    @staticmethod
    def resolve_template(template_id: str, _depth: int = 0) -> Optional[dict]:
        """解析模板（含继承合并）

        递归合并父模板的 structure/templates，子模板覆盖同名项。
        最大继承深度 3 层，防止循环引用。

        Args:
            template_id: 模板ID
            _depth: 当前递归深度（内部使用）

        Returns:
            合并后的模板字典，不存在返回 None
        """
        if _depth > 3:
            logger.warning(f"模板继承深度超过3层，停止解析: {template_id}")
            return None

        template = TemplateDAO.get_by_id(template_id)
        if not template:
            return None

        result = template.to_dict()

        # 如果有父模板，递归合并
        base_id = getattr(template, 'base_template_id', None)
        if base_id:
            parent = TemplateService.resolve_template(base_id, _depth + 1)
            if parent:
                result = TemplateService._merge_templates(parent, result)

        return result

    @staticmethod
    def _merge_templates(base: dict, override: dict) -> dict:
        """合并父子模板

        规则:
        - 顶层字段: 子覆盖父
        - structure: 按 path 合并，子模板同名 path 覆盖父模板
        - templates: 按 path 合并，子模板同名 path 覆盖父模板
        """
        # structure: 按 path 合并
        base_paths = {s["path"]: s for s in base.get("structure", [])}
        for s in override.get("structure", []):
            base_paths[s["path"]] = s  # 同路径覆盖，新路径追加

        # templates: 按 path 合并
        base_files = {t["path"]: t for t in base.get("templates", [])}
        for t in override.get("templates", []):
            base_files[t["path"]] = t

        merged = {**base, **override}  # 顶层字段子覆盖父
        merged["structure"] = sorted(base_paths.values(), key=lambda x: x["path"])
        merged["templates"] = sorted(base_files.values(), key=lambda x: x["path"])
        merged["base_template_id"] = override.get("base_template_id")  # 保留继承链

        return merged

    # ──────────────────────────────────────────────
    # V2.8.0 新增：模板版本管理
    # ──────────────────────────────────────────────

    @staticmethod
    def check_template_updates(project) -> dict:
        """检查项目所用模板是否有更新版本

        Args:
            project: Project ORM 对象

        Returns:
            dict: {
                has_update: bool,
                current_version: str,
                latest_version: str,
                template_name: str,
                diff: list  # 变更的 path 列表
            }
        """
        template = TemplateDAO.get_by_id(getattr(project, 'template_id', ''))
        if not template:
            return {"has_update": False, "reason": "模板不存在"}

        current = getattr(project, 'applied_template_version', None) or "1.0"
        latest = getattr(template, 'schema_version', None) or "1.0"

        if current < latest:
            return {
                "has_update": True,
                "current_version": current,
                "latest_version": latest,
                "template_name": template.name,
                "diff": TemplateService._diff_template_versions(current, latest, template)
            }
        return {
            "has_update": False,
            "current_version": current,
            "latest_version": latest
        }

    @staticmethod
    def _diff_template_versions(current: str, latest: str, template: Template) -> list:
        """比较模板版本差异（简化实现：返回当前模板的所有 structure path）"""
        # TODO: 未来可存储历史版本结构，做精确 diff
        return [s.get("path", "") for s in (template.structure or [])]
