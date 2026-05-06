# -*- coding: utf-8 -*-
"""
基础检查器模块

定义检查器框架的核心抽象类和数据结构。
所有具体的规则检查器都必须继承BaseChecker类。
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import IntEnum
from typing import List, Optional, Any, Dict

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class Severity(IntEnum):
    """
    违规严重级别枚举

    数值越大表示越严重的违规：
    - ERROR (3): 必须修复的严重错误
    - WARNING (2): 建议修复的警告
    - INFO (1): 信息性提示
    """
    ERROR = 3
    WARNING = 2
    INFO = 1


@dataclass
class RuleInfo:
    """
    规则元信息数据类

    存储规则的描述性信息，用于文档生成和用户界面展示。

    Attributes:
        rule_id: 规则唯一标识符 (格式: 类别_编号, 如 NAMING_001)
        name: 规则名称
        description: 规则详细描述
        category: 规则所属类别 (如 naming, structure, safety)
        severity: 默认严重级别
        enabled: 是否启用该规则
        version: 规则版本号
        author: 规则作者
        tags: 标签列表，便于分类检索
    """
    rule_id: str
    name: str
    description: str
    category: str
    severity: Severity = Severity.WARNING
    enabled: bool = True
    version: str = "1.0.0"
    author: str = ""
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """将规则信息转换为字典格式"""
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "severity": self.severity.name,
            "enabled": self.enabled,
            "version": self.version,
            "author": self.author,
            "tags": self.tags,
        }


class BaseChecker(ABC):
    """
    检查器抽象基类

    所有PLC代码规范检查器的基类，定义了统一的接口规范。
    子类必须实现check()方法来执行具体的检查逻辑。

    设计原则:
    - 单一职责: 每个检查器只负责一类规则的检查
    - 开闭原则: 通过继承扩展新规则，无需修改现有代码
    - 依赖倒置: 依赖于抽象接口而非具体实现

    Usage:
        class NamingConventionChecker(BaseChecker):
            def __init__(self):
                super().__init__(
                    rule_info=RuleInfo(
                        rule_id="NAMING_001",
                        name="变量命名规范",
                        description="检查变量名是否符合匈牙利命名法",
                        category="naming",
                    )
                )

            def check(self, source_code: str, context: dict = None) -> List[Violation]:
                # 实现检查逻辑
                violations = []
                # ... 检查代码 ...
                return violations
    """

    def __init__(self, rule_info: RuleInfo):
        """
        初始化检查器

        Args:
            rule_info: 规则元信息对象
        """
        self._rule_info = rule_info
        self._enabled = rule_info.enabled
        logger.debug(f"初始化检查器: {rule_info.rule_id} - {rule_info.name}")

    @property
    def rule_info(self) -> RuleInfo:
        """获取规则元信息"""
        return self._rule_info

    @abstractmethod
    def check(
        self,
        source_code: str,
        file_path: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Any]:
        """
        执行检查逻辑（抽象方法）

        Args:
            source_code: 待检查的源代码文本
            file_path: 源文件路径（可选）
            context: 上下文信息字典（可选），可包含：
                - project_config: 项目配置
                - variables: 已解析的变量列表
                - pous: 已解析的POU列表

        Returns:
            List[Violation]: 发现的违规列表

        Raises:
            NotImplementedError: 子类必须实现此方法
        """
        pass

    def get_rule_info(self) -> RuleInfo:
        """
        获取规则详细信息

        Returns:
            RuleInfo: 规则元信息对象
        """
        return self._rule_info

    def get_severity(self) -> Severity:
        """
        获取规则默认严重级别

        Returns:
            Severity: 严重级别枚举值
        """
        return self._rule_info.severity

    def is_enabled(self) -> bool:
        """
        检查规则是否启用

        Returns:
            bool: True表示已启用，False表示已禁用
        """
        return self._enabled

    def enable(self) -> None:
        """启用该规则"""
        self._enabled = True
        self._rule_info.enabled = True
        logger.info(f"启用规则: {self._rule_info.rule_id}")

    def disable(self) -> None:
        """禁用该规则"""
        self._enabled = False
        self._rule_info.enabled = False
        logger.info(f"禁用规则: {self._rule_info.rule_id}")

    def __repr__(self) -> str:
        """返回检查器的字符串表示"""
        status = "启用" if self._enabled else "禁用"
        return (
            f"<{self.__class__.__name__} "
            f"(id={self._rule_info.rule_id}, "
            f"name={self._rule_info.name}, "
            f"status={status})>"
        )
