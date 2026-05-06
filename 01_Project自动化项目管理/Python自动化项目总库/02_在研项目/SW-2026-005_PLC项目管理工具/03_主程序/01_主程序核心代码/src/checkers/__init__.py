# -*- coding: utf-8 -*-
"""
检查器框架模块

提供PLC代码规范检查的核心框架，包括：
- BaseChecker: 检查器抽象基类
- RuleRegistry: 规则注册表（单例模式）
- Severity: 违规严重级别枚举
- RuleInfo: 规则元信息数据类
"""

from .base_checker import BaseChecker, Severity, RuleInfo
from .rule_registry import RuleRegistry

__all__ = [
    "BaseChecker",
    "RuleRegistry",
    "Severity",
    "RuleInfo",
]
