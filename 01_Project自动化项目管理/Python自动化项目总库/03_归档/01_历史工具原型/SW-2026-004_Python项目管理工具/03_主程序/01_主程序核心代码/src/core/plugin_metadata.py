# -*- coding: utf-8 -*-
"""
插件元数据规范

定义插件plugin.json文件的完整规范，支持插件市场功能
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class PluginPermission(Enum):
    """插件权限枚举"""
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    NETWORK_ACCESS = "network_access"
    PROJECT_ACCESS = "project_access"
    SYSTEM_INFO = "system_info"
    EXECUTE_CODE = "execute_code"
    DATABASE_ACCESS = "database_access"


@dataclass
class PluginMetadata:
    """插件元数据类"""
    
    plugin_id: str
    plugin_name: str
    plugin_version: str
    plugin_author: str
    plugin_description: str
    
    permissions: List[str] = field(default_factory=list)
    default_config: Dict[str, Any] = field(default_factory=dict)
    config_schema: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    python_packages: List[str] = field(default_factory=list)
    is_builtin: bool = False
    
    download_url: Optional[str] = None
    repository: Optional[str] = None
    homepage: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    icon: Optional[str] = None
    min_app_version: Optional[str] = None
    max_app_version: Optional[str] = None
    changelog: Optional[str] = None
    license: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'plugin_id': self.plugin_id,
            'plugin_name': self.plugin_name,
            'plugin_version': self.plugin_version,
            'plugin_author': self.plugin_author,
            'plugin_description': self.plugin_description,
            'permissions': self.permissions,
            'default_config': self.default_config,
            'config_schema': self.config_schema,
            'dependencies': self.dependencies,
            'python_packages': self.python_packages,
            'is_builtin': self.is_builtin,
            'download_url': self.download_url,
            'repository': self.repository,
            'homepage': self.homepage,
            'tags': self.tags,
            'icon': self.icon,
            'min_app_version': self.min_app_version,
            'max_app_version': self.max_app_version,
            'changelog': self.changelog,
            'license': self.license,
        }
    
    def to_json(self, indent: int = 2) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginMetadata':
        """从字典创建"""
        return cls(
            plugin_id=data.get('plugin_id', ''),
            plugin_name=data.get('plugin_name', ''),
            plugin_version=data.get('plugin_version', '1.0.0'),
            plugin_author=data.get('plugin_author', ''),
            plugin_description=data.get('plugin_description', ''),
            permissions=data.get('permissions', []),
            default_config=data.get('default_config', {}),
            config_schema=data.get('config_schema', {}),
            dependencies=data.get('dependencies', []),
            python_packages=data.get('python_packages', []),
            is_builtin=data.get('is_builtin', False),
            download_url=data.get('download_url'),
            repository=data.get('repository'),
            homepage=data.get('homepage'),
            tags=data.get('tags', []),
            icon=data.get('icon'),
            min_app_version=data.get('min_app_version'),
            max_app_version=data.get('max_app_version'),
            changelog=data.get('changelog'),
            license=data.get('license'),
        )
    
    @classmethod
    def from_json_file(cls, file_path: str) -> 'PluginMetadata':
        """从JSON文件加载"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    def validate(self) -> tuple[bool, List[str]]:
        """验证元数据完整性"""
        errors = []
        
        if not self.plugin_id:
            errors.append("plugin_id 不能为空")
        elif not self._is_valid_id(self.plugin_id):
            errors.append("plugin_id 只能包含字母、数字、下划线和连字符")
        
        if not self.plugin_name:
            errors.append("plugin_name 不能为空")
        
        if not self.plugin_version:
            errors.append("plugin_version 不能为空")
        elif not self._is_valid_version(self.plugin_version):
            errors.append("plugin_version 格式无效，应为 x.y.z 格式")
        
        if not self.plugin_author:
            errors.append("plugin_author 不能为空")
        
        if not self.plugin_description:
            errors.append("plugin_description 不能为空")
        
        for perm in self.permissions:
            if perm not in [p.value for p in PluginPermission]:
                errors.append(f"未知权限: {perm}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _is_valid_id(plugin_id: str) -> bool:
        """验证插件ID格式"""
        import re
        return bool(re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', plugin_id))
    
    @staticmethod
    def _is_valid_version(version: str) -> bool:
        """验证版本号格式"""
        import re
        return bool(re.match(r'^\d+\.\d+\.\d+$', version))


class PluginMetadataSchema:
    """插件元数据JSON Schema"""
    
    SCHEMA = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Plugin Metadata",
        "description": "插件元数据规范",
        "type": "object",
        "required": [
            "plugin_id",
            "plugin_name", 
            "plugin_version",
            "plugin_author",
            "plugin_description"
        ],
        "properties": {
            "plugin_id": {
                "type": "string",
                "pattern": "^[a-zA-Z][a-zA-Z0-9_-]*$",
                "maxLength": 32,
                "description": "插件唯一标识符"
            },
            "plugin_name": {
                "type": "string",
                "maxLength": 100,
                "description": "插件显示名称"
            },
            "plugin_version": {
                "type": "string",
                "pattern": "^\\d+\\.\\d+\\.\\d+$",
                "description": "插件版本号（语义化版本）"
            },
            "plugin_author": {
                "type": "string",
                "maxLength": 50,
                "description": "插件作者"
            },
            "plugin_description": {
                "type": "string",
                "description": "插件功能描述"
            },
            "permissions": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": [p.value for p in PluginPermission]
                },
                "description": "所需权限列表"
            },
            "default_config": {
                "type": "object",
                "description": "默认配置"
            },
            "config_schema": {
                "type": "object",
                "description": "配置项定义（JSON Schema格式）"
            },
            "dependencies": {
                "type": "array",
                "items": {"type": "string"},
                "description": "依赖的其他插件ID"
            },
            "python_packages": {
                "type": "array",
                "items": {"type": "string"},
                "description": "依赖的Python包（支持版本约束）"
            },
            "is_builtin": {
                "type": "boolean",
                "default": False,
                "description": "是否为内置插件"
            },
            "download_url": {
                "type": "string",
                "format": "uri",
                "description": "插件下载地址"
            },
            "repository": {
                "type": "string",
                "format": "uri",
                "description": "代码仓库地址"
            },
            "homepage": {
                "type": "string",
                "format": "uri",
                "description": "插件主页地址"
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "标签列表，用于搜索和分类"
            },
            "icon": {
                "type": "string",
                "description": "插件图标路径（相对于插件目录）"
            },
            "min_app_version": {
                "type": "string",
                "description": "支持的最低应用版本"
            },
            "max_app_version": {
                "type": "string",
                "description": "支持的最高应用版本"
            },
            "changelog": {
                "type": "string",
                "description": "更新日志（Markdown格式）"
            },
            "license": {
                "type": "string",
                "description": "许可证类型"
            }
        }
    }
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """获取Schema"""
        return cls.SCHEMA
    
    @classmethod
    def validate(cls, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """验证数据是否符合Schema"""
        try:
            import jsonschema
            jsonschema.validate(data, cls.SCHEMA)
            return True, []
        except ImportError:
            metadata = PluginMetadata.from_dict(data)
            return metadata.validate()
        except Exception as e:
            return False, [str(e)]


PLUGIN_METADATA_TEMPLATE = {
    "plugin_id": "my_plugin",
    "plugin_name": "我的插件",
    "plugin_version": "1.0.0",
    "plugin_author": "作者名称",
    "plugin_description": "插件功能描述",
    "permissions": ["file_read"],
    "default_config": {},
    "config_schema": {},
    "dependencies": [],
    "python_packages": [],
    "is_builtin": False,
    "download_url": "",
    "repository": "",
    "homepage": "",
    "tags": ["工具"],
    "icon": "",
    "min_app_version": "1.0.0",
    "max_app_version": "",
    "changelog": "## v1.0.0\n- 初始版本",
    "license": "MIT"
}
