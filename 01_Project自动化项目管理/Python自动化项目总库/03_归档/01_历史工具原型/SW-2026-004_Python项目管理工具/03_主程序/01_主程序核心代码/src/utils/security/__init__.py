# -*- coding: utf-8 -*-
"""
安全工具模块
提供密码加密、验证等安全相关功能
"""

import bcrypt
import secrets
import string
from typing import Optional

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class SecurityUtils:
    """安全工具类，提供密码加密、验证等安全相关功能"""
    
    def hash_password(self, password: str, rounds: int = 12) -> str:
        if not password:
            raise ValueError("密码不能为空")
        salt = bcrypt.gensalt(rounds=rounds)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        if not password or not hashed:
            return False
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            logger.error(f"密码验证失败: {e}")
            return False
    
    def generate_secret_key(self, length: int = 32) -> str:
        alphabet = string.ascii_letters + string.digits + "_-"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def generate_api_key(self) -> str:
        prefix = "pm_"
        random_part = secrets.token_urlsafe(32)
        return f"{prefix}{random_part}"
    
    def generate_secure_token(self, length: int = 32) -> str:
        return secrets.token_urlsafe(length)
    
    def is_strong_password(self, password: str) -> tuple[bool, str]:
        if len(password) < 8:
            return False, "密码长度至少8位"
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        if not has_upper:
            return False, "密码必须包含大写字母"
        if not has_lower:
            return False, "密码必须包含小写字母"
        if not has_digit:
            return False, "密码必须包含数字"
        if not has_special:
            return False, "密码必须包含特殊字符"
        return True, "密码强度符合要求"
    
    def sanitize_input(self, input_str: str, max_length: int = 255) -> str:
        if not input_str:
            return ""
        input_str = input_str[:max_length]
        input_str = ''.join(char for char in input_str if ord(char) >= 32 or char in '\n\r\t')
        return input_str.strip()
    
    def migrate_plain_password(self, username: str, plain_password: str) -> str:
        logger.info(f"迁移用户 {username} 的密码")
        return self.hash_password(plain_password)


_security_utils_instance = None

def _get_security_utils_instance():
    global _security_utils_instance
    if _security_utils_instance is None:
        _security_utils_instance = SecurityUtils()
    return _security_utils_instance


def hash_password(password: str, rounds: int = 12) -> str:
    return _get_security_utils_instance().hash_password(password, rounds)

def verify_password(password: str, hashed: str) -> bool:
    return _get_security_utils_instance().verify_password(password, hashed)

def generate_secret_key(length: int = 32) -> str:
    return _get_security_utils_instance().generate_secret_key(length)

def generate_api_key() -> str:
    return _get_security_utils_instance().generate_api_key()

def generate_secure_token(length: int = 32) -> str:
    return _get_security_utils_instance().generate_secure_token(length)

def is_strong_password(password: str) -> tuple[bool, str]:
    return _get_security_utils_instance().is_strong_password(password)

def sanitize_input(input_str: str, max_length: int = 255) -> str:
    return _get_security_utils_instance().sanitize_input(input_str, max_length)

def migrate_plain_password(username: str, plain_password: str) -> str:
    return _get_security_utils_instance().migrate_plain_password(username, plain_password)


__all__ = [
    "SecurityUtils",
    "hash_password",
    "verify_password",
    "generate_secret_key",
    "generate_api_key",
    "generate_secure_token",
    "is_strong_password",
    "sanitize_input",
    "migrate_plain_password",
]

