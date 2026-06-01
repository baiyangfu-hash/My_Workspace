# -*- coding: utf-8 -*-
"""
自动修复器模块

提供PLC代码规范问题的自动修复能力，
与checkers模块的检测能力形成 检测-修复 闭环。

可用修复器：
- CommentPunctuationFixer: 中文标点→英文半角自动替换
- NamingFixer: 变量命名建议（生成重命名脚本，不直接修改）
"""

from src.fixers.base_fixer import (
    BaseFixer,
    FixIssue,
    FixResult,
    FixPreview,
    FixerInfo,
    Severity,
)
from src.fixers.comment_punctuation_fixer import CommentPunctuationFixer
from src.fixers.naming_fixer import NamingFixer

__all__ = [
    "BaseFixer",
    "FixIssue",
    "FixResult",
    "FixPreview",
    "FixerInfo",
    "Severity",
    "CommentPunctuationFixer",
    "NamingFixer",
]
