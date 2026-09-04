# -*- coding: utf-8 -*-
"""
依赖注入容器测试
"""

import pytest
from src.core.container import container, Container
from src.utils.security import SecurityUtils
from src.api.auth import UserStore, TokenManager


class TestContainer:
    """测试依赖注入容器"""

    def test_container_initialization(self):
        """测试容器初始化"""
        assert container is not None
        assert isinstance(container, Container)

    def test_security_utils_injection(self):
        """测试安全工具依赖注入"""
        security_utils = container.security_utils
        assert security_utils is not None
        assert isinstance(security_utils, SecurityUtils)

    def test_user_store_injection(self):
        """测试用户存储依赖注入"""
        user_store = container.user_store
        assert user_store is not None
        assert isinstance(user_store, UserStore)
        assert hasattr(user_store, 'security_utils')
        assert isinstance(user_store.security_utils, SecurityUtils)

    def test_token_manager_injection(self):
        """测试Token管理器依赖注入"""
        token_manager = container.token_manager
        assert token_manager is not None
        assert isinstance(token_manager, TokenManager)

    def test_singleton_behavior(self):
        """测试单例行为"""
        utils1 = container.security_utils
        utils2 = container.security_utils
        assert utils1 is utils2

        user_store1 = container.user_store
        user_store2 = container.user_store
        assert user_store1 is user_store2

        token_manager1 = container.token_manager
        token_manager2 = container.token_manager
        assert token_manager1 is token_manager2

    def test_user_store_functionality(self):
        """测试用户存储功能"""
        user_store = container.user_store

        # 测试获取用户
        admin_user = user_store.get_user("admin")
        assert admin_user is not None
        assert admin_user["role"] == "admin"

        # 测试密码验证
        assert user_store.verify_password("admin", "admin123") is True
        assert user_store.verify_password("admin", "wrong_password") is False

        # 测试添加用户
        try:
            user_store.add_user("test_user", "Test@123", "user")
            test_user = user_store.get_user("test_user")
            assert test_user is not None
            assert test_user["role"] == "user"
        finally:
            # 清理测试用户
            if "test_user" in user_store._users:
                del user_store._users["test_user"]

    def test_token_manager_functionality(self):
        """测试Token管理器功能"""
        token_manager = container.token_manager

        # 测试生成Token
        token = token_manager.generate_token("admin")
        assert token is not None
        assert isinstance(token, str)

        # 测试验证Token
        payload = token_manager.verify_token(token)
        assert payload is not None
        assert payload["username"] == "admin"

    def test_config_dict(self):
        """测试配置字典"""
        config = container.config_dict
        assert config is not None
        assert "app" in config
        assert "database" in config
        assert "security" in config


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
