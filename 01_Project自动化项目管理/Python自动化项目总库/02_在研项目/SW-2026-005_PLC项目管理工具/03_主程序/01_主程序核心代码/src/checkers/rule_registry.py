# -*- coding: utf-8 -*-
"""
规则注册表模块

实现检查器规则的单例注册中心。
负责管理所有可用的检查器实例，提供注册、查询和过滤功能。
支持按类别、ID等维度进行规则检索。
"""
from typing import Dict, List, Optional, Type

from src.utils.logger import setup_logger

from .base_checker import BaseChecker, RuleInfo, Severity

logger = setup_logger(__name__)


class RuleRegistry:
    """
    规则注册表（单例模式）

    采用单例模式确保全局只有一个注册表实例，
    所有检查器通过此类进行统一管理。

    主要功能:
    - 注册新的检查器
    - 按ID或类别查询检查器
    - 批量启用/禁用规则
    - 提供规则统计信息

    Usage:
        registry = RuleRegistry.get_instance()

        # 注册检查器
        registry.register(MyNamingChecker())

        # 查询检查器
        checker = registry.get_checker_by_id("NAMING_001")
        naming_checkers = registry.get_checkers_by_category("naming")

        # 获取所有启用的检查器
        all_enabled = registry.get_all_checkers(enabled_only=True)
    """

    _instance: Optional["RuleRegistry"] = None
    _initialized: bool = False

    def __new__(cls) -> "RuleRegistry":
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化注册表（单例保护）"""
        if RuleRegistry._initialized:
            return

        self._checkers: Dict[str, BaseChecker] = {}
        self._categories: Dict[str, List[str]] = {}
        RuleRegistry._initialized = True
        logger.info("规则注册表初始化完成")

    @classmethod
    def get_instance(cls) -> "RuleRegistry":
        """
        获取注册表单例实例

        Returns:
            RuleRegistry: 注册表实例
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """
        重置单例实例（主要用于测试）

        Warning:
            此方法会清除所有已注册的检查器，请谨慎使用
        """
        cls._instance = None
        cls._initialized = False
        logger.warning("规则注册表已重置")

    def register(self, checker: BaseChecker) -> bool:
        """
        注册一个检查器

        Args:
            checker: 要注册的检查器实例

        Returns:
            bool: 注册成功返回True，如果ID已存在返回False

        Raises:
            TypeError: 如果checker不是BaseChecker的子类实例
        """
        if not isinstance(checker, BaseChecker):
            raise TypeError(
                f"检查器必须是BaseChecker的子类实例，"
                f"当前类型: {type(checker).__name__}"
            )

        rule_id = checker.rule_info.rule_id

        if rule_id in self._checkers:
            logger.warning(f"规则ID已存在，将被覆盖: {rule_id}")

        self._checkers[rule_id] = checker

        # 更新类别索引
        category = checker.rule_info.category
        if category not in self._categories:
            self._categories[category] = []
        if rule_id not in self._categories[category]:
            self._categories[category].append(rule_id)

        logger.info(
            f"注册检查器成功: {rule_id} "
            f"(类别: {category}, 名称: {checker.rule_info.name})"
        )
        return True

    def unregister(self, rule_id: str) -> bool:
        """
        注销指定规则

        Args:
            rule_id: 要注销的规则ID

        Returns:
            bool: 注销成功返回True，不存在返回False
        """
        if rule_id not in self._checkers:
            logger.warning(f"尝试注销不存在的规则: {rule_id}")
            return False

        checker = self._checkers.pop(rule_id)
        category = checker.rule_info.category

        # 从类别索引中移除
        if category in self._categories and rule_id in self._categories[category]:
            self._categories[category].remove(rule_id)
            if not self._categories[category]:
                del self._categories[category]

        logger.info(f"注销规则成功: {rule_id}")
        return True

    def get_checker_by_id(self, rule_id: str) -> Optional[BaseChecker]:
        """
        根据规则ID获取检查器

        Args:
            rule_id: 规则唯一标识符

        Returns:
            Optional[BaseChecker]: 检查器实例，不存在时返回None
        """
        return self._checkers.get(rule_id)

    def get_checkers_by_category(
        self, category: str
    ) -> List[BaseChecker]:
        """
        根据类别获取所有检查器

        Args:
            category: 规则类别名称

        Returns:
            List[BaseChecker]: 该类别下的所有检查器列表
        """
        rule_ids = self._categories.get(category, [])
        return [
            self._checkers[rid]
            for rid in rule_ids
            if rid in self._checkers
        ]

    def get_all_checkers(
        self, enabled_only: bool = False
    ) -> List[BaseChecker]:
        """
        获取所有检查器

        Args:
            enabled_only: 是否只返回启用的检查器

        Returns:
            List[BaseChecker]: 检查器列表
        """
        if enabled_only:
            return [
                c for c in self._checkers.values() if c.is_enabled()
            ]
        return list(self._checkers.values())

    def get_all_categories(self) -> List[str]:
        """
        获取所有规则类别

        Returns:
            List[str]: 类别名称列表
        """
        return list(self._categories.keys())

    def enable_rule(self, rule_id: str) -> bool:
        """
        启用指定规则

        Args:
            rule_id: 规则ID

        Returns:
            bool: 操作成功返回True，规则不存在返回False
        """
        checker = self.get_checker_by_id(rule_id)
        if checker is None:
            logger.error(f"无法启用不存在的规则: {rule_id}")
            return False

        checker.enable()
        return True

    def disable_rule(self, rule_id: str) -> bool:
        """
        禁用指定规则

        Args:
            rule_id: 规则ID

        Returns:
            bool: 操作成功返回True，规则不存在返回False
        """
        checker = self.get_checker_by_id(rule_id)
        if checker is None:
            logger.error(f"无法禁用不存在的规则: {rule_id}")
            return False

        checker.disable()
        return True

    def enable_category(self, category: str) -> int:
        """
        启用某个类别的所有规则

        Args:
            category: 类别名称

        Returns:
            int: 成功启用的规则数量
        """
        count = 0
        for checker in self.get_checkers_by_category(category):
            if not checker.is_enabled():
                checker.enable()
                count += 1
        logger.info(f"类别 '{category}' 已启用 {count} 个规则")
        return count

    def disable_category(self, category: str) -> int:
        """
        禁用某个类别的所有规则

        Args:
            category: 类别名称

        Returns:
            int: 成功禁用的规则数量
        """
        count = 0
        for checker in self.get_checkers_by_category(category):
            if checker.is_enabled():
                checker.disable()
                count += 1
        logger.info(f"类别 '{category}' 已禁用 {count} 个规则")
        return count

    def get_statistics(self) -> Dict[str, any]:
        """
        获取注册表统计信息

        Returns:
            Dict: 包含以下键的字典:
                - total_rules: 总规则数
                - enabled_rules: 启用的规则数
                - disabled_rules: 禁用的规则数
                - categories: 类别列表及各类别规则数
        """
        all_checkers = self.get_all_checkers()
        enabled_count = sum(1 for c in all_checkers if c.is_enabled())
        disabled_count = len(all_checkers) - enabled_count

        category_stats = {
            cat: len(ids)
            for cat, ids in self._categories.items()
        }

        return {
            "total_rules": len(all_checkers),
            "enabled_rules": enabled_count,
            "disabled_rules": disabled_count,
            "categories": category_stats,
        }

    def clear(self) -> None:
        """
        清空所有已注册的检查器

        Warning:
            此操作不可逆，主要用于测试场景
        """
        self._checkers.clear()
        self._categories.clear()
        logger.warning("规则注册表已清空")

    def __len__(self) -> int:
        """返回已注册的检查器总数"""
        return len(self._checkers)

    def __contains__(self, rule_id: str) -> bool:
        """检查规则ID是否已注册"""
        return rule_id in self._checkers

    def __iter__(self):
        """迭代所有检查器"""
        return iter(self._checkers.values())
