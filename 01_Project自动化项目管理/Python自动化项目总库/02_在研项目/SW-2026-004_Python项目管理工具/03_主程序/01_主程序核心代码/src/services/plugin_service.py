# -*- coding: utf-8 -*-
"""
插件管理服务
"""
import importlib
import sys
from pathlib import Path
from typing import List, Optional, Any

from src.dao.plugin_dao import PluginDAO
from src.models.plugin import Plugin
from src.core.constants import PluginStatus
from src.utils.file_utils import read_json
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class PluginService:
    """插件管理服务类"""
    
    _plugins: dict = {}  # 已加载的插件实例
    
    @staticmethod
    def load_plugins():
        """加载所有已启用的插件"""
        try:
            enabled_plugins = PluginDAO.list(status=PluginStatus.ENABLED)
            
            for plugin in enabled_plugins:
                try:
                    PluginService._load_plugin(plugin)
                    logger.info(f"插件加载成功: {plugin.plugin_id} {plugin.name}")
                except Exception as e:
                    logger.exception(f"加载插件失败 {plugin.plugin_id}: {e}")
                    PluginDAO.update_status(plugin.plugin_id, PluginStatus.ERROR)
            
            logger.info(f"共加载 {len(PluginService._plugins)} 个插件")
            
        except Exception as e:
            logger.exception(f"加载插件失败: {e}")
    
    @staticmethod
    def _load_plugin(plugin: Plugin):
        """加载单个插件"""
        plugin_path = Path(plugin.path)

        if getattr(sys, 'frozen', False):
            base_path = Path(sys._MEIPASS)
            resolved_path = base_path / plugin_path
        elif plugin_path.is_absolute():
            resolved_path = plugin_path
        else:
            # 相对路径基于程序根目录解析
            base_path = Path(__file__).resolve().parent.parent.parent
            resolved_path = base_path / plugin_path

        if not resolved_path.exists():
            raise RuntimeError(f"插件路径不存在: {resolved_path}")

        parent_dir = str(resolved_path.parent)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

        module_name = resolved_path.name
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            try:
                module = importlib.import_module(f"{module_name}.main")
            except ImportError as e:
                raise RuntimeError(f"无法导入插件模块: {module_name}, 错误: {e}")

        plugin_class = None
        for attr in dir(module):
            value = getattr(module, attr)
            if isinstance(value, type) and hasattr(value, "plugin_id"):
                plugin_class = value
                break

        if not plugin_class:
            raise RuntimeError(f"未找到插件主类: {plugin.plugin_id}")

        plugin_instance = plugin_class()

        if hasattr(plugin_instance, "initialize"):
            if not plugin_instance.initialize(plugin.config):
                raise RuntimeError(f"插件初始化失败: {plugin.plugin_id}")

        PluginService._plugins[plugin.plugin_id] = {
            "model": plugin,
            "instance": plugin_instance
        }
    
    @staticmethod
    def get_plugin(plugin_id: str) -> Optional[dict]:
        """获取插件信息"""
        return PluginService._plugins.get(plugin_id)
    
    @staticmethod
    def install_plugin(plugin_path: str) -> tuple[Optional[Plugin], str]:
        """安装插件"""
        try:
            path = Path(plugin_path)
            if not path.exists() or not path.is_dir():
                return None, "插件目录不存在"
            
            # 读取插件元信息
            meta_file = path / "plugin.json"
            if not meta_file.exists():
                return None, "缺少plugin.json文件"
            
            meta = read_json(meta_file)
            required_fields = ["plugin_id", "plugin_name", "plugin_version", "plugin_author", "plugin_description"]
            for field in required_fields:
                if field not in meta:
                    return None, f"plugin.json缺少必填字段: {field}"
            
            plugin_id = meta["plugin_id"]
            
            # 检查是否已安装
            if PluginDAO.exists(plugin_id):
                return None, "插件已安装"
            
            # 创建插件记录
            plugin = Plugin(
                plugin_id=plugin_id,
                name=meta["plugin_name"],
                version=meta["plugin_version"],
                author=meta["plugin_author"],
                description=meta["plugin_description"],
                path=str(path),
                status=PluginStatus.INSTALLED,
                permissions=meta.get("permissions", []),
                config=meta.get("default_config", {}),
                config_schema=meta.get("config_schema", {}),
                dependencies=meta.get("dependencies", []),
                python_packages=meta.get("python_packages", []),
                is_builtin=meta.get("is_builtin", False),
                download_url=meta.get("download_url"),
                repository=meta.get("repository"),
                homepage=meta.get("homepage"),
                tags=meta.get("tags", []),
                icon=meta.get("icon"),
                min_app_version=meta.get("min_app_version"),
                max_app_version=meta.get("max_app_version"),
                changelog=meta.get("changelog"),
            )
            
            plugin = PluginDAO.create(plugin)
            logger.info(f"插件安装成功: {plugin_id} {meta['plugin_name']}")
            return plugin, ""
            
        except Exception as e:
            logger.exception(f"安装插件失败: {e}")
            return None, f"安装插件失败: {str(e)}"
    
    @staticmethod
    def enable_plugin(plugin_id: str) -> tuple[bool, str]:
        """启用插件"""
        try:
            plugin = PluginDAO.get_by_id(plugin_id)
            if not plugin:
                return False, "插件不存在"
            
            if plugin.status == PluginStatus.ENABLED:
                return True, "插件已启用"
            
            # 检查依赖
            for dep_id in plugin.dependencies:
                dep = PluginDAO.get_by_id(dep_id)
                if not dep or dep.status != PluginStatus.ENABLED:
                    return False, f"依赖插件未安装或未启用: {dep_id}"
            
            # 加载插件
            try:
                PluginService._load_plugin(plugin)
            except Exception as e:
                return False, f"加载插件失败: {str(e)}"
            
            # 更新状态
            PluginDAO.update_status(plugin_id, PluginStatus.ENABLED)
            logger.info(f"插件已启用: {plugin_id}")
            return True, ""
            
        except Exception as e:
            logger.exception(f"启用插件失败: {e}")
            return False, f"启用插件失败: {str(e)}"
    
    @staticmethod
    def disable_plugin(plugin_id: str) -> tuple[bool, str]:
        """禁用插件"""
        try:
            plugin = PluginDAO.get_by_id(plugin_id)
            if not plugin:
                return False, "插件不存在"
            
            if plugin.status != PluginStatus.ENABLED:
                return True, "插件未启用"
            
            # 检查是否有其他插件依赖此插件
            dependent_plugins = PluginDAO.list()
            for p in dependent_plugins:
                if p.status == PluginStatus.ENABLED and plugin_id in p.dependencies:
                    return False, f"插件 {p.plugin_id} 依赖此插件，无法禁用"
            
            # 清理插件实例
            if plugin_id in PluginService._plugins:
                plugin_instance = PluginService._plugins[plugin_id]["instance"]
                if hasattr(plugin_instance, "cleanup"):
                    plugin_instance.cleanup()
                del PluginService._plugins[plugin_id]
            
            # 更新状态
            PluginDAO.update_status(plugin_id, PluginStatus.DISABLED)
            logger.info(f"插件已禁用: {plugin_id}")
            return True, ""
            
        except Exception as e:
            logger.exception(f"禁用插件失败: {e}")
            return False, f"禁用插件失败: {str(e)}"
    
    @staticmethod
    def uninstall_plugin(plugin_id: str) -> tuple[bool, str]:
        """卸载插件"""
        try:
            plugin = PluginDAO.get_by_id(plugin_id)
            if not plugin:
                return False, "插件不存在"
            
            if plugin.is_builtin:
                return False, "内置插件不能卸载"
            
            # 先禁用插件
            if plugin.status == PluginStatus.ENABLED:
                success, msg = PluginService.disable_plugin(plugin_id)
                if not success:
                    return False, msg
            
            # 删除数据库记录
            success = PluginDAO.delete(plugin_id)
            if not success:
                return False, "删除插件记录失败"
            
            logger.info(f"插件已卸载: {plugin_id}")
            return True, ""
            
        except Exception as e:
            logger.exception(f"卸载插件失败: {e}")
            return False, f"卸载插件失败: {str(e)}"
    
    @staticmethod
    def execute_plugin(plugin_id: str, action: str, params: dict = None) -> tuple[Any, str]:
        """执行插件功能"""
        try:
            if plugin_id not in PluginService._plugins:
                return None, "插件未安装或未启用"
            
            plugin_info = PluginService._plugins[plugin_id]
            plugin_instance = plugin_info["instance"]
            
            # 支持execute_action或execute方法
            if hasattr(plugin_instance, "execute_action"):
                result, error = plugin_instance.execute_action(action, params or {})
                return result, error
            elif hasattr(plugin_instance, "execute"):
                result = plugin_instance.execute(action, params or {})
                return result, ""
            else:
                return None, "插件不支持执行功能"
            
        except Exception as e:
            logger.exception(f"执行插件失败: {e}")
            return None, f"执行插件失败: {str(e)}"
    
    @staticmethod
    def list_plugins(status: Optional[str] = None) -> List[Plugin]:
        """获取插件列表"""
        status_enum = PluginStatus(status) if status else None
        return PluginDAO.list(status=status_enum)
    
    @staticmethod
    def update_plugin_config(plugin_id: str, config: dict) -> tuple[bool, str]:
        """更新插件配置"""
        try:
            plugin = PluginDAO.get_by_id(plugin_id)
            if not plugin:
                return False, "插件不存在"
            
            new_config = {**plugin.config, **config}
            updated_plugin = PluginDAO.update(plugin_id, {"config": new_config})
            
            if plugin_id in PluginService._plugins:
                plugin_instance = PluginService._plugins[plugin_id]["instance"]
                if hasattr(plugin_instance, "initialize"):
                    plugin_instance.initialize(new_config)
            
            logger.info(f"插件配置已更新: {plugin_id}")
            return True, ""
            
        except Exception as e:
            logger.exception(f"更新插件配置失败: {e}")
            return False, f"更新插件配置失败: {str(e)}"
    
    @staticmethod
    def update_plugin(plugin_id: str, new_version: str, new_path: str = None) -> tuple[bool, str]:
        """更新插件到新版本"""
        try:
            plugin = PluginDAO.get_by_id(plugin_id)
            if not plugin:
                return False, "插件不存在"
            
            if plugin.is_builtin:
                return False, "内置插件不支持在线更新"
            
            was_enabled = plugin.status == PluginStatus.ENABLED
            
            if was_enabled:
                success, msg = PluginService.disable_plugin(plugin_id)
                if not success:
                    return False, f"禁用插件失败: {msg}"
            
            if new_path:
                meta = read_json(Path(new_path) / "plugin.json")
                PluginDAO.update(plugin_id, {
                    "version": new_version,
                    "path": new_path,
                    "name": meta.get("plugin_name", plugin.name),
                    "description": meta.get("plugin_description", plugin.description),
                    "config": meta.get("default_config", plugin.config),
                    "changelog": meta.get("changelog"),
                })
            else:
                PluginDAO.update(plugin_id, {"version": new_version})
            
            if was_enabled:
                success, msg = PluginService.enable_plugin(plugin_id)
                if not success:
                    return False, f"重新启用插件失败: {msg}"
            
            logger.info(f"插件已更新: {plugin_id} -> {new_version}")
            return True, ""
            
        except Exception as e:
            logger.exception(f"更新插件失败: {e}")
            return False, f"更新插件失败: {str(e)}"
    
    @staticmethod
    def get_plugin_info(plugin_id: str) -> Optional[dict]:
        """获取插件详细信息"""
        plugin = PluginDAO.get_by_id(plugin_id)
        if not plugin:
            return None
        
        info = plugin.to_dict()
        
        if plugin_id in PluginService._plugins:
            plugin_instance = PluginService._plugins[plugin_id]["instance"]
            info["loaded"] = True
            info["actions"] = []
            
            if hasattr(plugin_instance, "get_actions"):
                info["actions"] = plugin_instance.get_actions()
        else:
            info["loaded"] = False
            info["actions"] = []
        
        return info
    
    @staticmethod
    def initialize_builtin_plugins():
        """初始化内置插件"""
        try:
            plugins_dir = Path(__file__).parent.parent / "plugins"
            
            if not plugins_dir.exists():
                logger.warning("插件目录不存在")
                return
            
            for plugin_dir in plugins_dir.iterdir():
                if not plugin_dir.is_dir():
                    continue
                
                meta_file = plugin_dir / "plugin.json"
                if not meta_file.exists():
                    continue
                
                try:
                    meta = read_json(meta_file)
                    
                    if not meta.get("is_builtin", False):
                        continue
                    
                    plugin_id = meta["plugin_id"]
                    
                    if PluginDAO.exists(plugin_id):
                        continue
                    
                    plugin = Plugin(
                        plugin_id=plugin_id,
                        name=meta["plugin_name"],
                        version=meta["plugin_version"],
                        author=meta["plugin_author"],
                        description=meta["plugin_description"],
                        path=str(plugin_dir),
                        status=PluginStatus.ENABLED,
                        permissions=meta.get("permissions", []),
                        config=meta.get("default_config", {}),
                        config_schema=meta.get("config_schema", {}),
                        dependencies=meta.get("dependencies", []),
                        python_packages=meta.get("python_packages", []),
                        is_builtin=True,
                        download_url=meta.get("download_url"),
                        repository=meta.get("repository"),
                        homepage=meta.get("homepage"),
                        tags=meta.get("tags", []),
                        icon=meta.get("icon"),
                        min_app_version=meta.get("min_app_version"),
                        max_app_version=meta.get("max_app_version"),
                        changelog=meta.get("changelog"),
                    )
                    
                    PluginDAO.create(plugin)
                    logger.info(f"内置插件已注册: {plugin_id}")
                    
                except Exception as e:
                    logger.error(f"初始化内置插件失败 {plugin_dir.name}: {e}")
            
        except Exception as e:
            logger.exception(f"初始化内置插件失败: {e}")
    
    @staticmethod
    def get_plugins() -> List[Plugin]:
        """获取所有插件（测试用）"""
        try:
            return PluginDAO.list()
        except Exception as e:
            logger.exception(f"获取插件列表失败: {e}")
            return []
    
    @staticmethod
    def get_installed_plugins() -> List[Plugin]:
        """获取已安装的插件"""
        try:
            from src.core.constants import PluginStatus
            return PluginDAO.list(status=PluginStatus.INSTALLED)
        except Exception as e:
            logger.exception(f"获取已安装插件失败: {e}")
            return []
