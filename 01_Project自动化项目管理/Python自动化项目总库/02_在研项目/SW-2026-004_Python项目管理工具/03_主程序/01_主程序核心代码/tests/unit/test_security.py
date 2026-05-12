# -*- coding: utf-8 -*-
"""
安全模块单元测试
测试密码加密、Token生成等功能
"""

import pytest
import time
from datetime import datetime, timedelta

from src.utils.security import (
    hash_password,
    verify_password,
    generate_secret_key,
    generate_api_key,
    generate_secure_token,
    is_strong_password,
    sanitize_input
)
from src.core.exceptions import (
    AuthenticationError,
    TokenExpiredError,
    InvalidTokenError
)


class TestPasswordHashing:
    """密码加密测试"""
    
    def test_hash_password_success(self):
        """测试密码加密成功"""
        password = "my_secure_password123!"
        hashed = hash_password(password)
        
        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed != password  # 加密后不应等于原密码
        assert hashed.startswith("$2")  # bcrypt哈希以$2开头
    
    def test_verify_password_correct(self):
        """测试正确密码验证"""
        password = "test_password_123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """测试错误密码验证"""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_verify_password_empty(self):
        """测试空密码验证"""
        assert verify_password("", "some_hash") is False
        assert verify_password("password", "") is False
        assert verify_password("", "") is False
    
    def test_hash_password_empty_raises(self):
        """测试空密码加密应抛出异常"""
        with pytest.raises(ValueError, match="密码不能为空"):
            hash_password("")
    
    def test_same_password_different_hash(self):
        """测试相同密码产生不同哈希（因为盐不同）"""
        password = "same_password"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2  # 两次加密结果应不同
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestTokenGeneration:
    """Token生成测试"""
    
    def test_generate_secret_key(self):
        """测试密钥生成"""
        key1 = generate_secret_key(32)
        key2 = generate_secret_key(32)
        
        assert len(key1) == 32
        assert len(key2) == 32
        assert key1 != key2  # 每次生成应不同
        assert key1.isalnum() or "_" in key1 or "-" in key1
    
    def test_generate_api_key(self):
        """测试API密钥生成"""
        key = generate_api_key()
        
        assert key.startswith("pm_")
        assert len(key) > 10  # 应该有足够长度
    
    def test_generate_secure_token(self):
        """测试安全令牌生成"""
        token1 = generate_secure_token(32)
        token2 = generate_secure_token(32)
        
        assert len(token1) > 32  # base64编码后长度会增加
        assert token1 != token2  # 每次生成应不同


class TestPasswordStrength:
    """密码强度测试"""
    
    def test_strong_password(self):
        """测试强密码"""
        password = "Strong@123"
        is_strong, message = is_strong_password(password)
        
        assert is_strong is True
        assert "符合要求" in message
    
    def test_weak_password_too_short(self):
        """测试密码太短"""
        password = "Short1!"
        is_strong, message = is_strong_password(password)
        
        assert is_strong is False
        assert "至少8位" in message
    
    def test_weak_password_no_upper(self):
        """测试没有大写字母"""
        password = "lowercase123!"
        is_strong, message = is_strong_password(password)
        
        assert is_strong is False
        assert "大写字母" in message
    
    def test_weak_password_no_lower(self):
        """测试没有小写字母"""
        password = "UPPERCASE123!"
        is_strong, message = is_strong_password(password)
        
        assert is_strong is False
        assert "小写字母" in message
    
    def test_weak_password_no_digit(self):
        """测试没有数字"""
        password = "NoDigitsHere!"
        is_strong, message = is_strong_password(password)
        
        assert is_strong is False
        assert "数字" in message
    
    def test_weak_password_no_special(self):
        """测试没有特殊字符"""
        password = "NoSpecialChars123"
        is_strong, message = is_strong_password(password)
        
        assert is_strong is False
        assert "特殊字符" in message


class TestInputSanitization:
    """输入清理测试"""
    
    def test_sanitize_normal_input(self):
        """测试正常输入"""
        input_str = "  Hello World  "
        result = sanitize_input(input_str)
        
        assert result == "Hello World"
    
    def test_sanitize_control_chars(self):
        """测试控制字符"""
        input_str = "Hello\x00World\x01Test"
        result = sanitize_input(input_str)
        
        assert "\x00" not in result
        assert "\x01" not in result
    
    def test_sanitize_empty_input(self):
        """测试空输入"""
        assert sanitize_input("") == ""
        assert sanitize_input(None) == ""
    
    def test_sanitize_max_length(self):
        """测试最大长度限制"""
        long_input = "a" * 300
        result = sanitize_input(long_input, max_length=255)
        
        assert len(result) == 255


class TestAuthModule:
    """认证模块测试"""
    
    def test_user_store_add_and_verify(self):
        """测试用户存储添加和验证"""
        from src.api.auth import user_store
        
        # 添加新用户
        username = "test_user_123"
        password = "Test@123456"
        
        user_store.add_user(username, password, role="tester")
        
        # 验证密码
        assert user_store.verify_password(username, password) is True
        assert user_store.verify_password(username, "wrong_password") is False
        
        # 验证用户信息
        user = user_store.get_user(username)
        assert user is not None
        assert user["role"] == "tester"
        assert user["enabled"] is True
    
    def test_user_store_duplicate_user(self):
        """测试重复用户"""
        from src.api.auth import user_store
        
        username = "duplicate_test_user"
        user_store.add_user(username, "password123")
        
        with pytest.raises(ValueError, match="已存在"):
            user_store.add_user(username, "another_password")
    
    def test_token_manager_generate_and_verify(self):
        """测试Token生成和验证"""
        from src.api.auth import token_manager
        
        username = "test_user"
        token = token_manager.generate_token(username)
        
        assert token is not None
        
        # 验证Token
        payload = token_manager.verify_token(token)
        assert payload["username"] == username
        assert payload["type"] == "access"
    
    def test_token_manager_expired_token(self):
        """测试过期Token"""
        from src.api.auth import token_manager
        import jwt
        from src.core.settings import settings
        
        # 生成一个已过期Token（通过修改时间）
        payload = {
            "username": "test_user",
            "exp": datetime.utcnow() - timedelta(hours=1),  # 已过期
            "iat": datetime.utcnow() - timedelta(hours=2),
            "type": "access"
        }
        expired_token = jwt.encode(
            payload,
            settings.security.api_secret_key,
            algorithm="HS256"
        )
        
        with pytest.raises(TokenExpiredError):
            token_manager.verify_token(expired_token)
    
    def test_token_manager_invalid_token(self):
        """测试无效Token"""
        from src.api.auth import token_manager
        
        with pytest.raises(InvalidTokenError):
            token_manager.verify_token("invalid.token.here")
    
    def test_login_success(self):
        """测试登录成功"""
        from src.api.auth import login, user_store
        
        # 使用默认用户测试
        result = login("admin", "admin123")
        
        assert result["success"] is True
        assert "token" in result
        assert result["user"]["username"] == "admin"
    
    def test_login_wrong_password(self):
        """测试错误密码"""
        from src.api.auth import login
        
        result = login("admin", "wrong_password")
        
        assert result["success"] is False
        assert "token" not in result
    
    def test_login_nonexistent_user(self):
        """测试不存在的用户"""
        from src.api.auth import login
        
        result = login("nonexistent_user_12345", "password")
        
        assert result["success"] is False
    
    def test_login_disabled_user(self):
        """测试被禁用的用户"""
        from src.api.auth import login, user_store
        
        # 创建并禁用用户
        username = "disabled_user"
        user_store.add_user(username, "password123")
        user_store._users[username]["enabled"] = False
        
        result = login(username, "password123")
        
        assert result["success"] is False
        assert "禁用" in result["message"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
