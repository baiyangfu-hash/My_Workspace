# -*- coding: utf-8 -*-
"""
依赖注入容器
"""

from dependency_injector import containers, providers
from .settings import settings
from .config import Config
from ..api.auth import TokenManager, UserStore
from ..utils.security import SecurityUtils
from ..services.project_service import ProjectService
from ..dao.project_dao import ProjectDAO
from ..dao.template_dao import TemplateDAO


class Container(containers.DeclarativeContainer):
    """主依赖注入容器"""
    
    # 配置
    config = providers.Configuration()
    
    # 安全工具
    security_utils = providers.Singleton(
        SecurityUtils
    )
    
    # 用户存储
    user_store = providers.Singleton(
        UserStore,
        security_utils=security_utils
    )
    
    # Token管理器
    token_manager = providers.Singleton(
        TokenManager
    )
    
    # 项目服务
    project_service = providers.Singleton(
        ProjectService,
        project_dao=ProjectDAO,
        template_dao=TemplateDAO,
        config=Config
    )
    

# 创建全局容器实例
container = Container()

# 配置容器
container.config.from_value({
    "app": {
        "name": settings.app_name,
        "version": settings.app_version,
        "debug": settings.debug_mode
    },
    "database": {
        "url": settings.database.url,
        "pool_size": settings.database.pool_size
    },
    "security": {
        "api_secret_key": settings.security.api_secret_key,
        "bcrypt_rounds": settings.security.bcrypt_rounds
    }
})
