# -*- coding: utf-8 -*-
"""
插件数据访问对象
"""
from typing import List, Optional

from .database import db
from src.models.plugin import Plugin
from src.core.constants import PluginStatus
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class PluginDAO:
    """插件数据访问类"""
    
    @staticmethod
    def create(plugin: Plugin) -> Plugin:
        """创建插件记录"""
        with db.get_session() as session:
            session.add(plugin)
            session.commit()
            session.refresh(plugin)
            return plugin
    
    @staticmethod
    def get_by_id(plugin_id: str) -> Optional[Plugin]:
        """根据插件ID查询"""
        with db.get_session() as session:
            return session.query(Plugin).filter(Plugin.plugin_id == plugin_id).first()
    
    @staticmethod
    def list(
        status: Optional[PluginStatus] = None,
        is_builtin: Optional[bool] = None
    ) -> List[Plugin]:
        """查询插件列表"""
        with db.get_session() as session:
            query = session.query(Plugin)
            
            if status:
                query = query.filter(Plugin.status == status)
            
            if is_builtin is not None:
                query = query.filter(Plugin.is_builtin == is_builtin)
            
            return query.order_by(Plugin.is_builtin.desc(), Plugin.name).all()
    
    @staticmethod
    def update(plugin_id: str, data: dict) -> Optional[Plugin]:
        """更新插件信息"""
        with db.get_session() as session:
            plugin = session.query(Plugin).filter(Plugin.plugin_id == plugin_id).first()
            if not plugin:
                return None
            
            plugin.update_from_dict(data)
            session.commit()
            session.refresh(plugin)
            return plugin
    
    @staticmethod
    def update_status(plugin_id: str, status: PluginStatus) -> bool:
        """更新插件状态"""
        with db.get_session() as session:
            plugin = session.query(Plugin).filter(Plugin.plugin_id == plugin_id).first()
            if not plugin:
                return False
            
            plugin.status = status
            session.commit()
            return True
    
    @staticmethod
    def delete(plugin_id: str) -> bool:
        """删除插件记录"""
        with db.get_session() as session:
            plugin = session.query(Plugin).filter(Plugin.plugin_id == plugin_id).first()
            if not plugin or plugin.is_builtin:  # 内置插件不能删除
                return False
            
            session.delete(plugin)
            session.commit()
            return True
    
    @staticmethod
    def exists(plugin_id: str) -> bool:
        """检查插件是否已安装"""
        with db.get_session() as session:
            return session.query(Plugin).filter(Plugin.plugin_id == plugin_id).first() is not None
