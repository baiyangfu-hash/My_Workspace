# -*- coding: utf-8 -*-
"""
模板管理服务
"""
import json
from typing import List, Optional
from pathlib import Path

from src.dao.template_dao import TemplateDAO
from src.models.template import Template
from src.core.constants import DEFAULT_TEMPLATES
from src.utils.file_utils import read_json, write_json
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class TemplateService:
    """模板管理服务类"""
    
    @staticmethod
    def initialize_builtin_templates():
        """初始化内置模板到数据库（已存在的也会更新为最新定义）"""
        import datetime
        start_time = datetime.datetime.now()
        logger.info(f"========== 开始初始化内置模板 ==========")
        logger.info(f"当前时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"DEFAULT_TEMPLATES 定义了 {len(DEFAULT_TEMPLATES)} 个内置模板")

        try:
            valid_builtin_ids = {t["id"] for t in DEFAULT_TEMPLATES}
            logger.info(f"有效内置模板ID列表: {valid_builtin_ids}")

            existing = TemplateDAO.list_all()
            logger.info(f"数据库中现有 {len(existing)} 个模板")

            # ========== 清理无效的内置模板 (增强版) ==========
            deleted_count = 0
            logger.info(f"========== 开始模板清理扫描 ==========")

            for t in existing:
                tid = getattr(t, 'template_id', '')
                is_builtin = getattr(t, 'is_builtin', False)
                is_valid = tid in valid_builtin_ids
                is_tpl_format = tid.startswith('TPL-')

                # 详细日志：打印每个模板的状态
                logger.debug(f"  扫描模板: {tid} | is_builtin={is_builtin} | 在有效列表={is_valid} | TPL格式={is_tpl_format}")

                # 增强的清理条件（方案A：多维度判断）
                should_delete = False
                delete_reason = ""

                if is_tpl_format and not is_valid:
                    # 条件1: TPL格式但不在新有效列表中 → 必须删除（无论is_builtin值如何）
                    should_delete = True
                    delete_reason = f"TPL格式ID不在有效列表中 (is_builtin={is_builtin})"
                elif is_builtin and not is_valid:
                    # 条件2: 标记为内置但不在有效列表中 → 删除
                    should_delete = True
                    delete_reason = f"is_builtin=True但不在有效列表中"

                if should_delete:
                    logger.warning(f"[清理] 发现过期内置模板: {tid} | 原因: {delete_reason} | 正在删除...")
                    try:
                        result = TemplateDAO.force_delete(tid)
                        if result:
                            deleted_count += 1
                            logger.info(f"[清理成功] 已删除: {tid}")
                        else:
                            logger.error(f"[清理失败] force_delete返回False: {tid} (模板可能不存在)")
                    except Exception as del_err:
                        logger.exception(f"[清理异常] 删除模板 {tid} 时出错: {del_err}")
                else:
                    if is_valid:
                        logger.debug(f"  [保留] {tid} - 有效内置模板")
                    elif not is_tpl_format:
                        logger.debug(f"  [保留] {tid} - 自定义模板(非TPL格式)")
                    else:
                        logger.debug(f"  [保留] {tid} - 无需处理")

            if deleted_count > 0:
                logger.warning(f"========== 共清理 {deleted_count} 个无效内置模板 ==========")
            else:
                logger.info(f"========== 模板清理完成，无需删除 ==========")

            if deleted_count > 0:
                logger.info(f"共清理 {deleted_count} 个无效内置模板")

            # 创建或更新内置模板
            created_count = 0
            updated_count = 0
            for template_data in DEFAULT_TEMPLATES:
                template_id = template_data["id"]
                existing_tmpl = TemplateDAO.get_by_id(template_id)

                if existing_tmpl is None:
                    template = Template(
                        template_id=template_data["id"],
                        name=template_data["name"],
                        version=template_data["version"],
                        compiler=template_data["compiler"],
                        scene=template_data["scene"],
                        description=template_data["description"],
                        structure=template_data["structure"],
                        templates=template_data.get("templates", []),
                        is_builtin=template_data["is_builtin"],
                        business_lines=template_data.get("business_lines", [])
                    )
                    TemplateDAO.create(template)
                    created_count += 1
                    logger.info(f"[创建] 内置模板: {template_data['id']} - {template_data['name']}")
                else:
                    existing_tmpl.name = template_data["name"]
                    existing_tmpl.version = template_data["version"]
                    existing_tmpl.compiler = template_data["compiler"]
                    existing_tmpl.scene = template_data["scene"]
                    existing_tmpl.description = template_data["description"]
                    existing_tmpl.structure = template_data["structure"]
                    existing_tmpl.templates = template_data.get("templates", [])
                    existing_tmpl.business_lines = template_data.get("business_lines", [])
                    TemplateDAO.update(template_id, existing_tmpl.to_dict())
                    updated_count += 1
                    # 修复双V问题：version值可能已包含V前缀，需去重
                    clean_version = template_data['version']
                    if str(clean_version).startswith('V'):
                        clean_version = str(clean_version)[1:]  # 移除已有的V前缀
                    logger.info(f"[更新] 内置模板: {template_id} → V{clean_version}")

            end_time = datetime.datetime.now()
            duration = (end_time - start_time).total_seconds()

            logger.info(f"========== 内置模板初始化完成 ==========")
            logger.info(f"统计: 创建 {created_count} 个, 更新 {updated_count} 个, 删除 {deleted_count} 个")
            logger.info(f"耗时: {duration:.3f} 秒")
            logger.info(f"预期总数: {len(DEFAULT_TEMPLATES)} 个内置模板")

            # 验证实际数量
            final_count = len(TemplateDAO.list_all())
            builtin_final_count = sum(1 for t in TemplateDAO.list_all() if getattr(t, 'is_builtin', False))
            logger.info(f"数据库实际状态: 总计 {final_count} 个模板 (其中 {builtin_final_count} 个内置)")

            if builtin_final_count < len(DEFAULT_TEMPLATES):
                logger.warning(f"⚠️ 内置模板数量异常: 预期 {len(DEFAULT_TEMPLATES)}, 实际 {builtin_final_count}")

        except Exception as e:
            end_time = datetime.datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.exception(f"✗✗✗ 初始化内置模板失败 (耗时 {duration:.3f}s): {e}")
            import traceback
            traceback.print_exc()
            raise  # 重新抛出异常，让调用者知道初始化失败
    
    @staticmethod
    def get_template(template_id: str) -> Optional[Template]:
        """获取模板详情"""
        return TemplateDAO.get_by_id(template_id)
    
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
                count = TemplateDAO.count()
                template_id = f"TPL-{count + 1:03d}"
            
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
                business_lines=data.get("business_lines", [])
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
            # GUI层的_edit_template()回调从表格获取的是完整ORM对象而非字符串ID
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
                count = TemplateDAO.count()
                template_id = f"TPL-{count + 1:03d}"
            elif not template_id:
                count = TemplateDAO.count()
                template_id = f"TPL-{count + 1:03d}"
            
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
                business_lines=data.get("business_lines", [])
            )
            template = TemplateDAO.create(template)
            
            logger.info(f"模板导入成功: {template_id} {data['name']}")
            return template, ""
            
        except json.JSONDecodeError:
            return None, "JSON格式错误"
        except Exception as e:
            logger.exception(f"导入模板失败: {e}")
            return None, f"导入模板失败: {str(e)}"
    
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
    
    @staticmethod
    def get_template_types() -> List[Dict]:
        """
        获取模板类型列表 (兼容性方法)
        
        Returns:
            模板类型列表
        """
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

    @staticmethod
    def reset_builtin_templates():
        """重置所有内置模板为DEFAULT_TEMPLATES定义的默认值"""
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
            valid_ids = {t["id"] for t in DEFAULT_TEMPLATES}
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
