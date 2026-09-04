# -*- coding: utf-8 -*-
"""
应用配置管理模块（使用Pydantic Settings）
支持从环境变量和.env文件加载配置
"""

from typing import Optional
from pathlib import Path
from functools import lru_cache

from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """数据库配置"""
    model_config = SettingsConfigDict(env_prefix="DATABASE_")
    
    url: str = Field(default="sqlite:///data/project_manager.db", description="数据库连接URL")
    echo: bool = Field(default=False, description="是否打印SQL语句")
    pool_size: int = Field(default=5, description="连接池大小")
    max_overflow: int = Field(default=10, description="连接池最大溢出数")
    
    # MySQL配置（可选）
    type: str = Field(default="sqlite", description="数据库类型")
    host: Optional[str] = Field(default=None, description="数据库主机")
    port: Optional[int] = Field(default=None, description="数据库端口")
    user: Optional[str] = Field(default=None, description="数据库用户名")
    password: Optional[str] = Field(default=None, description="数据库密码")
    name: Optional[str] = Field(default=None, description="数据库名称")
    
    @validator("url")
    def validate_url(cls, v, values):
        """验证数据库URL"""
        if not v:
            # 如果URL为空，尝试构建MySQL URL
            if values.data.get("type") == "mysql":
                host = values.data.get("host", "localhost")
                port = values.data.get("port", 3306)
                user = values.data.get("user", "root")
                password = values.data.get("password", "")
                name = values.data.get("name", "project_manager")
                return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}?charset=utf8mb4"
        return v


class SecuritySettings(BaseSettings):
    """安全配置"""
    model_config = SettingsConfigDict(env_prefix="")
    
    api_secret_key: str = Field(
        default="dev-secret-key-must-be-changed",
        description="API密钥（生产环境必须修改）",
        alias="API_SECRET_KEY"
    )
    api_token_expire_hours: int = Field(
        default=24,
        description="JWT Token过期时间（小时）",
        alias="API_TOKEN_EXPIRE_HOURS"
    )
    bcrypt_rounds: int = Field(
        default=12,
        description="bcrypt加密轮数",
        alias="BCRYPT_ROUNDS"
    )
    
    @validator("api_secret_key")
    def validate_secret_key(cls, v):
        """验证密钥强度"""
        if len(v) < 16:
            raise ValueError("API_SECRET_KEY长度必须至少16位")
        insecure_keys = {
            "dev-secret-key-must-be-changed",
            "CHANGE_ME_generate_with_python_secrets_token_urlsafe",
            "pm-dev-secret-key-change-in-production-2024",
        }
        if v in insecure_keys:
            import warnings
            warnings.warn(
                "正在使用不安全的API密钥，请在生产环境中修改！"
                "生成随机密钥: python -c \"import secrets; print(secrets.token_urlsafe(32))\"",
                RuntimeWarning
            )
        return v


class APISettings(BaseSettings):
    """API配置"""
    model_config = SettingsConfigDict(env_prefix="API_")
    
    host: str = Field(default="127.0.0.1", description="API服务主机")
    port: int = Field(default=5000, description="API服务端口")
    cors_enabled: bool = Field(default=True, description="是否启用CORS")


class LogSettings(BaseSettings):
    """日志配置"""
    model_config = SettingsConfigDict(env_prefix="LOG_")
    
    level: str = Field(default="INFO", description="日志级别")
    file: str = Field(default="logs/app.log", description="日志文件路径")
    
    @validator("level")
    def validate_level(cls, v):
        """验证日志级别"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"无效的日志级别: {v}，必须是 {valid_levels}")
        return v.upper()


class Settings(BaseSettings):
    """
    应用主配置类
    
    配置优先级（从高到低）：
    1. 环境变量
    2. .env 文件
    3. 默认值
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # 忽略未定义的配置项
    )
    
    # 应用基本信息
    app_name: str = Field(default="Python项目管理工具", alias="APP_NAME")
    app_version: str = Field(default="1.1.0", alias="APP_VERSION")
    debug_mode: bool = Field(default=False, alias="DEBUG_MODE")
    
    # 子配置
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    api: APISettings = Field(default_factory=APISettings)
    log: LogSettings = Field(default_factory=LogSettings)
    
    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.debug_mode
    
    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return not self.debug_mode
    
    def get(self, key: str, default=None):
        """
        兼容旧版Config的get方法
        
        Args:
            key: 配置键，支持点号分隔（如 "database.url"）
            default: 默认值
        
        Returns:
            配置值或默认值
        """
        keys = key.split(".")
        value = self
        
        for k in keys:
            if hasattr(value, k):
                value = getattr(value, k)
            elif hasattr(value, "model_dump"):
                # Pydantic模型
                data = value.model_dump()
                if k in data:
                    value = data[k]
                else:
                    return default
            else:
                return default
        
        return value


@lru_cache()
def get_settings() -> Settings:
    """
    获取配置实例（单例模式）
    
    使用lru_cache确保配置只加载一次
    
    Returns:
        Settings实例
    
    Example:
        >>> from src.core.settings import get_settings
        >>> settings = get_settings()
        >>> print(settings.app_name)
        Python项目管理工具
    """
    return Settings()


# 全局配置实例（向后兼容）
settings = get_settings()
