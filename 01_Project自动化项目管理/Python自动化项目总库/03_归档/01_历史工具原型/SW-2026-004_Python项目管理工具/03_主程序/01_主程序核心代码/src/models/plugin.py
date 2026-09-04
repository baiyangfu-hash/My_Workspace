# -*- coding: utf-8 -*-
"""
插件数据模型
"""
from sqlalchemy import Column, String, Text, Enum, JSON, Boolean, Float, Integer, DateTime
from datetime import datetime

from .base import BaseModel
from src.core.constants import PluginStatus

class Plugin(BaseModel):
    """插件模型"""
    __tablename__ = "plugins"
    
    plugin_id = Column(String(32), unique=True, nullable=False, comment="插件ID")
    name = Column(String(100), nullable=False, comment="插件名称")
    version = Column(String(20), nullable=False, comment="版本号")
    author = Column(String(50), comment="作者")
    description = Column(Text, comment="插件描述")
    path = Column(String(500), nullable=False, comment="插件安装路径")
    status = Column(Enum(PluginStatus), default=PluginStatus.INSTALLED, comment="插件状态")
    permissions = Column(JSON, default=list, comment="权限列表")
    config = Column(JSON, default=dict, comment="插件配置")
    config_schema = Column(JSON, default=dict, comment="配置定义")
    dependencies = Column(JSON, default=list, comment="依赖插件ID列表")
    python_packages = Column(JSON, default=list, comment="依赖Python包列表")
    is_builtin = Column(Boolean, default=False, comment="是否内置插件")
    
    download_url = Column(String(500), comment="下载地址")
    repository = Column(String(500), comment="代码仓库地址")
    homepage = Column(String(500), comment="主页地址")
    tags = Column(JSON, default=list, comment="标签列表")
    icon = Column(String(200), comment="图标路径")
    min_app_version = Column(String(20), comment="最低应用版本")
    max_app_version = Column(String(20), comment="最高应用版本")
    changelog = Column(Text, comment="更新日志")
    rating = Column(Float, default=0.0, comment="评分(0-5)")
    download_count = Column(Integer, default=0, comment="下载次数")
    installed_at = Column(DateTime, default=datetime.now, comment="安装时间")
    
    def __repr__(self) -> str:
        return f"<Plugin {self.plugin_id} {self.name}>"
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'plugin_id': self.plugin_id,
            'name': self.name,
            'version': self.version,
            'author': self.author,
            'description': self.description,
            'path': self.path,
            'status': self.status.value if self.status else None,
            'permissions': self.permissions or [],
            'config': self.config or {},
            'config_schema': self.config_schema or {},
            'dependencies': self.dependencies or [],
            'python_packages': self.python_packages or [],
            'is_builtin': self.is_builtin,
            'download_url': self.download_url,
            'repository': self.repository,
            'homepage': self.homepage,
            'tags': self.tags or [],
            'icon': self.icon,
            'min_app_version': self.min_app_version,
            'max_app_version': self.max_app_version,
            'changelog': self.changelog,
            'rating': self.rating,
            'download_count': self.download_count,
            'installed_at': self.installed_at.isoformat() if self.installed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
