# -*- coding: utf-8 -*-
"""
路径解析模块

提供可扩展的路径规范化与解析能力。
采用策略模式支持多种路径处理方式：
- RelativePathStrategy: 基于基准路径的相对路径转换
- 预留: EnvVarPathStrategy, HomePathStrategy 等

设计原则:
- 高内聚: 所有路径处理逻辑集中在此模块
- 低耦合: 通过策略接口与外部解耦
- 可扩展: 新增策略只需实现基类
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class PathStrategy(ABC):
    """路径处理策略基类（抽象接口）"""

    @abstractmethod
    def normalize(self, raw_path: str, base_path: Optional[Path] = None) -> str:
        """
        规范化路径用于存储

        Args:
            raw_path: 原始路径
            base_path: 基准参考路径

        Returns:
            规范化后的存储路径
        """
        pass

    @abstractmethod
    def resolve(self, stored_path: str, base_path: Optional[Path] = None) -> str:
        """
        解析存储路径为可用路径

        Args:
            stored_path: 存储的路径
            base_path: 基准参考路径

        Returns:
            解析后的绝对/可用路径
        """
        pass


class RelativePathStrategy(PathStrategy):
    """
    相对路径策略

    将绝对路径转换为相对于基准路径的相对路径进行存储，
    读取时自动还原为绝对路径。

    适用场景:
    - 项目整体迁移后保持路径有效
    - 配置文件需要跨环境共享
    """

    def normalize(self, raw_path: str, base_path: Optional[Path] = None) -> str:
        if not base_path or not raw_path:
            return raw_path

        path_obj = Path(raw_path)

        if path_obj.is_absolute():
            try:
                relative = path_obj.relative_to(base_path)
                logger.debug(f"路径规范化: {raw_path} -> {relative}")
                return str(relative)
            except ValueError:
                logger.warning(f"无法计算相对路径，保持原值: {raw_path}")

        return raw_path

    def resolve(self, stored_path: str, base_path: Optional[Path] = None) -> str:
        if not base_path or not stored_path:
            return stored_path

        path_obj = Path(stored_path)

        if not path_obj.is_absolute():
            resolved = (base_path / path_obj).resolve()

            if resolved.exists():
                logger.debug(f"路径解析: {stored_path} -> {resolved}")
                return str(resolved)

            logger.warning(f"解析路径不存在，返回原始值: {stored_path}")

        return stored_path


class PathResolver:
    """
    路径解析器（门面类）

    统一入口，封装策略选择和调用逻辑。
    对外提供简洁的API，内部委托给具体策略。

    Usage:
        resolver = PathResolver(RelativePathStrategy())
        normalized = resolver.normalize("/abs/path", base_path=Path("."))
        resolved = resolver.resolve("../rel/path", base_path=Path("."))
    """

    def __init__(self, strategy: PathStrategy = None):
        self._strategy = strategy or RelativePathStrategy()

    @property
    def strategy(self) -> PathStrategy:
        return self._strategy

    @strategy.setter
    def strategy(self, value: PathStrategy):
        if not isinstance(value, PathStrategy):
            raise TypeError("策略必须是 PathStrategy 的子类实例")
        self._strategy = value

    def normalize(self, raw_path: str, base_path: Optional[Path] = None) -> str:
        """规范化路径（委托给当前策略）"""
        return self._strategy.normalize(raw_path, base_path)

    def resolve(self, stored_path: str, base_path: Optional[Path] = None) -> str:
        """解析路径（委托给当前策略）"""
        return self._strategy.resolve(stored_path, base_path)


_default_resolver: Optional[PathResolver] = None


def get_default_resolver() -> PathResolver:
    """获取默认路径解析器（懒加载单例）"""
    global _default_resolver
    if _default_resolver is None:
        _default_resolver = PathResolver(RelativePathStrategy())
    return _default_resolver


def reset_default_resolver():
    """重置默认解析器（主要用于测试）"""
    global _default_resolver
    _default_resolver = None
