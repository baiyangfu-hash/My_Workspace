# -*- coding: utf-8 -*-
"""
修复器基类模块

定义自动修复框架的核心抽象类和数据结构。
所有具体的规则修复器都必须继承BaseFixer类。

设计原则（对齐BaseChecker）：
- 单一职责: 每个修复器只负责一类问题的修复
- 安全优先: 修复前必须备份，支持dry_run预览
- 可追溯: 记录每次修复的原始内容和修复结果
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import IntEnum
from typing import List, Optional, Any, Dict

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class Severity(IntEnum):
    """违规严重级别枚举（与BaseChecker.Severity保持一致）"""

    ERROR = 3
    WARNING = 2
    INFO = 1


@dataclass
class FixIssue:
    """
    修复问题数据类

    描述一个可被自动修复的具体问题，
    包含位置信息、原始文本和建议替换文本。

    Attributes:
        rule_id: 触发的规则唯一标识符
        file_path: 问题所在文件路径
        line_number: 所在行号（从1开始）
        column: 所在列号（从1开始）
        original_text: 原始文本内容
        suggested_text: 建议替换为的文本
        severity: 严重级别
    """

    rule_id: str
    file_path: str = ""
    line_number: int = 0
    column: int = 0
    original_text: str = ""
    suggested_text: str = ""
    severity: Severity = Severity.WARNING

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "column": self.column,
            "original_text": self.original_text,
            "suggested_text": self.suggested_text,
            "severity": self.severity.name,
        }

    def __repr__(self) -> str:
        return (
            f"FixIssue(rule_id={self.rule_id!r}, "
            f"line={self.line_number}, "
            f"original={self.original_text!r}, "
            f"suggested={self.suggested_text!r})"
        )


@dataclass
class FixResult:
    """
    单次修复结果数据类

    记录对一个FixIssue执行修复后的结果。

    Attributes:
        success: 修复是否成功
        original_line: 修复前的原始行内容
        fixed_line: 修复后的行内容
        line_number: 行号
        applied_fixes: 本次应用的修复操作描述列表
    """

    success: bool = False
    original_line: str = ""
    fixed_line: str = ""
    line_number: int = 0
    applied_fixes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "original_line": self.original_line,
            "fixed_line": self.fixed_line,
            "line_number": self.line_number,
            "applied_fixes": self.applied_fixes,
        }


@dataclass
class FixPreview:
    """
    修复预览数据类

    提供修复前后的差异对比视图，
    使用unified diff格式展示变更。

    Attributes:
        diff_view: unified diff格式的差异文本
        issue_count: 预计修复的问题数量
        affected_lines: 受影响的行号列表
        fixer_id: 执行修复的修复器ID
        file_path: 文件路径
    """

    diff_view: str = ""
    issue_count: int = 0
    affected_lines: List[int] = field(default_factory=list)
    fixer_id: str = ""
    file_path: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "diff_view": self.diff_view,
            "issue_count": self.issue_count,
            "affected_lines": self.affected_lines,
            "fixer_id": self.fixer_id,
            "file_path": self.file_path,
        }


@dataclass
class FixerInfo:
    """
    修复器元信息数据类

    存储修复器的描述性信息，用于UI展示和用户选择。

    Attributes:
        fixer_id: 修复器唯一标识符
        name: 修复器名称
        description: 修复器详细描述
        category: 修复类别 (如 punctuation, naming)
        is_safe: 是否安全修复（True=可直接修改，False=仅建议）
        version: 版本号
        tags: 标签列表
    """

    fixer_id: str
    name: str
    description: str
    category: str
    is_safe: bool = True
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fixer_id": self.fixer_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "is_safe": self.is_safe,
            "version": self.version,
            "tags": self.tags,
        }


class BaseFixer(ABC):
    """
    修复器抽象基类

    所有PLC代码规范修复器的基类，定义统一的接口规范。
    子类必须实现 detect/fix/preview_fix 三个核心方法。

    设计原则（对齐BaseChecker）：
    - 单一职责: 每个修复器只负责一类问题的修复
    - 安全优先: 所有修复支持preview模式，不直接修改源文件
    - 可扩展: 通过继承扩展新修复能力

    Usage:
        class MyFixer(BaseFixer):
            def __init__(self):
                super().__init__(
                    fixer_info=FixerInfo(
                        fixer_id="MY_FIXER_001",
                        name="我的修复器",
                        description="修复XXX问题",
                        category="style",
                    )
                )

            def detect(self, source_code, file_path=""):
                issues = []
                # ... 检测逻辑 ...
                return issues

            def fix(self, source_code, issues):
                fixed_code = source_code
                results = []
                # ... 修复逻辑 ...
                return fixed_code, results

            def preview_fix(self, source_code, issues):
                previews = []
                # ... 预览逻辑 ...
                return previews
    """

    def __init__(self, fixer_info: FixerInfo):
        self._fixer_info = fixer_info
        logger.debug(f"初始化修复器: {fixer_info.fixer_id} - {fixer_info.name}")

    @property
    def fixer_info(self) -> FixerInfo:
        return self._fixer_info

    @property
    def fixer_id(self) -> str:
        return self._fixer_info.fixer_id

    @property
    def is_safe(self) -> bool:
        return self._fixer_info.is_safe

    @abstractmethod
    def detect(
        self,
        source_code: str,
        file_path: str = "",
    ) -> List[FixIssue]:
        """
        检测源代码中可修复的问题

        Args:
            source_code: 待检测的源代码文本
            file_path: 源文件路径（可选）

        Returns:
            List[FixIssue]: 发现的可修复问题列表
        """
        pass

    @abstractmethod
    def fix(
        self,
        source_code: str,
        issues: List[FixIssue],
    ) -> tuple:
        """
        执行实际修复操作

        Args:
            source_code: 原始源代码
            issues: 待修复的问题列表（来自detect方法）

        Returns:
            Tuple[str, List[FixResult]]: (修复后代码, 修复结果列表)
        """
        pass

    @abstractmethod
    def preview_fix(
        self,
        source_code: str,
        issues: List[FixIssue],
    ) -> List[FixPreview]:
        """
        生成修复预览（不修改源代码）

        Args:
            source_code: 原始源代码
            issues: 待修复的问题列表

        Returns:
            List[FixPreview]: 修复预览列表（包含diff视图）
        """
        pass

    def get_fixer_info(self) -> FixerInfo:
        return self._fixer_info

    def __repr__(self) -> str:
        safe_str = "安全" if self._fixer_info.is_safe else "仅建议"
        return (
            f"<{self.__class__.__name__} "
            f"(id={self._fixer_info.fixer_id}, "
            f"name={self._fixer_info.name}, "
            f"mode={safe_str})>"
        )
