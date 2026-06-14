# -*- coding: utf-8 -*-
"""
依赖注入容器（纯Python实现，移除dependency-injector依赖）

提供手动DI容器，保持与原Container接口兼容。
所有Service均使用静态方法模式，无需通过容器实例化。
容器仅负责管理需要单例的组件（SecurityUtils/UserStore/TokenManager）。
"""

from .settings import settings
from .config import Config
from ..api.auth import TokenManager, UserStore
from ..utils.security import SecurityUtils


class Container:
    """主依赖注入容器（纯Python实现）"""

    def __init__(self):
        self._instances = {}
        self._config = {}

    @property
    def security_utils(self) -> SecurityUtils:
        if 'security_utils' not in self._instances:
            self._instances['security_utils'] = SecurityUtils()
        return self._instances['security_utils']

    @property
    def user_store(self) -> UserStore:
        if 'user_store' not in self._instances:
            self._instances['user_store'] = UserStore(security_utils=self.security_utils)
        return self._instances['user_store']

    @property
    def token_manager(self) -> TokenManager:
        if 'token_manager' not in self._instances:
            self._instances['token_manager'] = TokenManager()
        return self._instances['token_manager']

    @property
    def config_dict(self) -> dict:
        return self._config

    def configure(self, config: dict):
        """配置容器"""
        self._config = config


# 创建全局容器实例
container = Container()

# 配置容器
container.configure({
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
