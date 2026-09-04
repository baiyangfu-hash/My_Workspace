# -*- coding: utf-8 -*-
"""
基础模型类
"""
from datetime import datetime
import json
from sqlalchemy import Column, DateTime, Integer, String, TypeDecorator, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class SafeJSON(TypeDecorator):
    """
    安全的 JSON 类型，兼容旧数据中的空字符串和 NULL 值

    解决问题：
    - 旧数据库中 JSON 字段可能是空字符串 '' 或 NULL
    - SQLAlchemy 默认的 JSON 类型无法解析空字符串，导致 JSONDecodeError
    - 该类型在加载数据时自动将空字符串转换为空字典 {}
    """
    impl = JSON
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """Python -> 数据库：存储时的处理"""
        if value is None:
            return None
        if isinstance(value, str):
            if not value.strip():
                return '{}'  # 空字符串转为空JSON对象
            # 尝试解析字符串确保是有效JSON
            try:
                json.loads(value)
                return value
            except json.JSONDecodeError:
                return '{}'
        return value

    def process_result_value(self, value, dialect):
        """数据库 -> Python：加载时的处理"""
        if value is None:
            return {}
        if isinstance(value, str):
            if not value.strip():
                return {}  # 空字符串返回空字典
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return {}  # 无效JSON返回空字典
        if isinstance(value, dict):
            return value
        # 其他类型尝试转换
        try:
            return dict(value)
        except (TypeError, ValueError):
            return {}

class BaseModel(Base):
    """基础模型，包含通用字段"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    def to_dict(self) -> dict:
        """转换为字典"""
        data = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            data[column.name] = value
        return data
    
    def update_from_dict(self, data: dict):
        """从字典更新字段"""
        for key, value in data.items():
            if hasattr(self, key) and key not in ["id", "created_at"]:
                setattr(self, key, value)
