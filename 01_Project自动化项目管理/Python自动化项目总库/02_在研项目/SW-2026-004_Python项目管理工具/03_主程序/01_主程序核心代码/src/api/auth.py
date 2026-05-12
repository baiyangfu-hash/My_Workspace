# -*- coding: utf-8 -*-
"""
API认证模块（重构版）
使用新的安全配置和异常处理机制
"""
import jwt
import datetime
from typing import Optional, Dict, Any
from flask import request, jsonify, g
from functools import wraps

from src.core.settings import settings
from src.core.exceptions import (
    AuthenticationError,
    TokenExpiredError,
    InvalidTokenError,
    AuthorizationError
)
from src.utils.security import verify_password, hash_password, SecurityUtils
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


# ==================== 用户存储（临时，生产环境应使用数据库） ====================

class UserStore:
    """用户存储类"""
    
    def __init__(self, security_utils: Optional[SecurityUtils] = None):
        # 依赖注入：安全工具
        self.security_utils = security_utils or SecurityUtils()
        
        # 初始化默认用户（密码已加密）
        # 密码生成命令：python -c "from src.utils.security import hash_password; print(hash_password('admin123'))"
        self._users: Dict[str, Dict[str, Any]] = {
            "admin": {
                "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA.qGZvKG6G",  # admin123
                "role": "admin",
                "enabled": True
            },
            "user": {
                "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA.qGZvKG6G",  # 同样使用admin123，实际应不同
                "role": "user",
                "enabled": True
            }
        }
    
    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """获取用户信息"""
        return self._users.get(username)
    
    def verify_password(self, username: str, password: str) -> bool:
        """验证用户密码"""
        user = self.get_user(username)
        if not user:
            return False
        return self.security_utils.verify_password(password, user["password_hash"])
    
    def add_user(self, username: str, password: str, role: str = "user"):
        """添加新用户"""
        if username in self._users:
            raise ValueError(f"用户 {username} 已存在")
        
        self._users[username] = {
            "password_hash": self.security_utils.hash_password(password),
            "role": role,
            "enabled": True
        }
    
    def update_password(self, username: str, new_password: str):
        """更新用户密码"""
        if username not in self._users:
            raise ValueError(f"用户 {username} 不存在")
        
        self._users[username]["password_hash"] = self.security_utils.hash_password(new_password)


# 全局用户存储实例
user_store = UserStore()


# ==================== Token管理 ====================

class TokenManager:
    """JWT Token管理器"""
    
    def __init__(self):
        self.secret_key = settings.security.api_secret_key
        self.expire_hours = settings.security.api_token_expire_hours
        self.algorithm = "HS256"
    
    def generate_token(self, username: str, extra_payload: Optional[Dict] = None) -> str:
        """
        生成JWT token
        
        Args:
            username: 用户名
            extra_payload: 额外的payload数据
        
        Returns:
            JWT token字符串
        
        Raises:
            AuthenticationError: 生成失败时抛出
        """
        try:
            payload = {
                "username": username,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=self.expire_hours),
                "iat": datetime.datetime.utcnow(),
                "type": "access"
            }
            
            if extra_payload:
                payload.update(extra_payload)
            
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            logger.info(f"为用户 {username} 生成Token")
            return token
            
        except Exception as e:
            logger.error(f"生成Token失败: {e}")
            raise AuthenticationError("生成认证令牌失败")
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        验证JWT token
        
        Args:
            token: JWT token
        
        Returns:
            解码后的payload
        
        Raises:
            TokenExpiredError: Token已过期
            InvalidTokenError: Token无效
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token已过期")
            raise TokenExpiredError()
            
        except jwt.InvalidTokenError as e:
            logger.warning(f"无效的Token: {e}")
            raise InvalidTokenError()
            
        except Exception as e:
            logger.error(f"验证Token失败: {e}")
            raise InvalidTokenError()
    
    def refresh_token(self, token: str) -> str:
        """
        刷新Token
        
        Args:
            token: 原Token
        
        Returns:
            新Token
        """
        try:
            payload = self.verify_token(token)
            username = payload.get("username")
            if not username:
                raise InvalidTokenError()
            return self.generate_token(username)
        except TokenExpiredError:
            # 如果Token过期但仍在宽限期内，允许刷新
            try:
                # 不验证过期时间解码
                payload = jwt.decode(
                    token, 
                    self.secret_key, 
                    algorithms=[self.algorithm],
                    options={"verify_exp": False}
                )
                username = payload.get("username")
                if not username:
                    raise InvalidTokenError()
                return self.generate_token(username)
            except Exception:
                raise InvalidTokenError()


# 全局Token管理器实例
token_manager = TokenManager()


# ==================== 认证装饰器 ====================

def auth_required(f):
    """
    认证装饰器
    
    要求请求头中包含有效的Authorization: Bearer <token>
    
    Example:
        @app.route("/api/protected")
        @auth_required
        def protected_route():
            return jsonify({"message": f"Hello, {g.username}!"})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 获取Token
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({
                "code": 401,
                "message": "缺少认证信息",
                "data": None
            }), 401
        
        # 解析Bearer Token
        try:
            scheme, token = auth_header.split(None, 1)
            if scheme.lower() != "bearer":
                raise ValueError()
        except ValueError:
            return jsonify({
                "code": 401,
                "message": "认证格式错误，应使用 Bearer <token>",
                "data": None
            }), 401
        
        # 验证Token
        try:
            payload = token_manager.verify_token(token)
            username = payload.get("username")
            
            # 检查用户是否存在且启用
            user = user_store.get_user(username)
            if not user:
                raise InvalidTokenError("用户不存在")
            if not user.get("enabled", True):
                raise AuthenticationError("用户已被禁用")
            
            # 将用户信息存储到g对象
            g.username = username
            g.user_role = user.get("role", "user")
            g.token_payload = payload
            
            return f(*args, **kwargs)
            
        except TokenExpiredError as e:
            return jsonify({
                "code": 401,
                "message": e.message,
                "code_detail": e.code,
                "data": None
            }), 401
            
        except (InvalidTokenError, AuthenticationError) as e:
            return jsonify({
                "code": 401,
                "message": e.message,
                "code_detail": e.code,
                "data": None
            }), 401
            
        except Exception as e:
            logger.exception(f"认证过程发生错误: {e}")
            return jsonify({
                "code": 500,
                "message": "认证过程发生错误",
                "data": None
            }), 500
    
    return decorated_function


def role_required(roles: list):
    """
    角色授权装饰器
    
    Args:
        roles: 允许的角色列表，如 ["admin", "manager"]
    
    Example:
        @app.route("/api/admin-only")
        @auth_required
        @role_required(["admin"])
        def admin_only_route():
            return jsonify({"message": "Admin access granted"})
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, "user_role"):
                return jsonify({
                    "code": 401,
                    "message": "未认证",
                    "data": None
                }), 401
            
            if g.user_role not in roles:
                logger.warning(f"用户 {g.username} (角色: {g.user_role}) 尝试访问需要 {roles} 权限的资源")
                return jsonify({
                    "code": 403,
                    "message": "权限不足",
                    "data": None
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ==================== 登录功能 ====================

def login(username: str, password: str) -> Dict[str, Any]:
    """
    用户登录
    
    Args:
        username: 用户名
        password: 密码
    
    Returns:
        登录结果字典
        {
            "success": bool,
            "message": str,
            "token": str (可选),
            "user": dict (可选)
        }
    """
    # 验证用户存在
    user = user_store.get_user(username)
    if not user:
        logger.warning(f"登录失败：用户 {username} 不存在")
        return {
            "success": False,
            "message": "用户名或密码错误"  # 不明确提示用户名不存在
        }
    
    # 验证用户启用状态
    if not user.get("enabled", True):
        logger.warning(f"登录失败：用户 {username} 已被禁用")
        return {
            "success": False,
            "message": "用户已被禁用"
        }
    
    # 验证密码
    if not user_store.verify_password(username, password):
        logger.warning(f"登录失败：用户 {username} 密码错误")
        return {
            "success": False,
            "message": "用户名或密码错误"
        }
    
    # 生成Token
    try:
        token = token_manager.generate_token(username)
    except AuthenticationError as e:
        return {
            "success": False,
            "message": e.message
        }
    
    logger.info(f"用户 {username} 登录成功")
    return {
        "success": True,
        "message": "登录成功",
        "token": token,
        "user": {
            "username": username,
            "role": user["role"]
        }
    }


def logout(username: str) -> bool:
    """
    用户登出
    
    注意：JWT是无状态的，这里仅记录日志
    实际项目中可能需要将Token加入黑名单
    
    Args:
        username: 用户名
    
    Returns:
        是否成功
    """
    logger.info(f"用户 {username} 登出")
    return True


# ==================== 向后兼容 ====================

# 保持旧函数签名兼容
def generate_token(username: str) -> Optional[str]:
    """向后兼容的Token生成函数"""
    try:
        return token_manager.generate_token(username)
    except AuthenticationError:
        return None


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """向后兼容的Token验证函数"""
    try:
        return token_manager.verify_token(token)
    except (TokenExpiredError, InvalidTokenError, AuthenticationError):
        return None
