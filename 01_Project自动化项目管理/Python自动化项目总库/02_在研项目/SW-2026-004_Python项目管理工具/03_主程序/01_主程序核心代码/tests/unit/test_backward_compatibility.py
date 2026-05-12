# -*- coding: utf-8 -*-
"""
向后兼容性测试
"""

import pytest
from src.services.project_service import ProjectService
from src.api.auth import UserStore, generate_token, verify_token
from src.utils.security import hash_password, verify_password


class TestBackwardCompatibility:
    """测试向后兼容性"""
    
    def test_project_service_static_methods(self):
        """测试ProjectService的静态方法调用"""
        # 测试静态方法调用（向后兼容）
        result = ProjectService.generate_project_code("DEV")
        assert result is not None
        assert isinstance(result, tuple)
        
        # 测试统计方法
        stats = ProjectService.get_statistics()
        assert isinstance(stats, dict)
    
    def test_user_store_backward_compatibility(self):
        """测试UserStore的向后兼容性"""
        # 测试无参数初始化
        user_store = UserStore()
        assert user_store is not None
        
        # 测试用户验证
        assert user_store.verify_password("admin", "admin123") is True
        assert user_store.verify_password("admin", "wrong") is False
    
    def test_auth_functions_backward_compatibility(self):
        """测试认证函数的向后兼容性"""
        # 测试生成Token
        token = generate_token("admin")
        assert token is not None
        assert isinstance(token, str)
        
        # 测试验证Token
        payload = verify_token(token)
        assert payload is not None
        assert isinstance(payload, dict)
        assert payload["username"] == "admin"
    
    def test_security_functions_backward_compatibility(self):
        """测试安全函数的向后兼容性"""
        # 测试密码加密
        password = "test_password_123"
        hashed = hash_password(password)
        assert hashed != password
        assert hashed.startswith("$2")
        
        # 测试密码验证
        assert verify_password(password, hashed) is True
        assert verify_password("wrong", hashed) is False
    
    def test_project_service_instance_methods(self):
        """测试ProjectService的实例方法调用"""
        # 测试实例化
        project_service = ProjectService()
        assert project_service is not None
        
        # 测试实例方法
        result = project_service.generate_project_code("DEV")
        assert result is not None
        assert isinstance(result, tuple)
        
        # 测试统计方法
        stats = project_service.get_statistics()
        assert isinstance(stats, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
