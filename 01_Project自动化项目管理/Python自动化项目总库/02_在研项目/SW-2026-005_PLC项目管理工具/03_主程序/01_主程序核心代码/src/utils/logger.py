# -*- coding: utf-8 -*-
"""
日志工具模块

提供统一的日志记录器配置和管理。
支持控制台输出和文件输出双通道，
自动创建日志目录和按日期轮转。
"""
import logging
import sys
from pathlib import Path
from typing import Optional

from src.core.config import ConfigLoader


def setup_logger(
    name: Optional[str] = None,
    log_level: Optional[int] = None,
) -> logging.Logger:
    """
    配置并返回日志记录器

    Args:
        name: 日志记录器名称，为None时使用调用者模块名
        log_level: 日志级别，为None时根据配置自动确定

    Returns:
        logging.Logger: 配置好的日志记录器实例
    """
    logger = logging.getLogger(name or __name__)

    # 避免重复添加处理器
    if logger.handlers:
        return logger

    # 确定日志级别
    if log_level is None:
        debug_mode = ConfigLoader.get("debug_mode", False)
        log_level = logging.DEBUG if debug_mode else logging.INFO

    logger.setLevel(log_level)

    # 格式化器
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    logger.addHandler(console_handler)

    # 文件处理器
    try:
        log_dir = (
            Path(__file__).parent.parent.parent / "logs"
        )
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "plc_project_manager.log"

        file_handler = logging.FileHandler(
            log_file, encoding="utf-8", mode="a"
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)  # 文件始终记录DEBUG级别
        logger.addHandler(file_handler)
    except OSError as e:
        logger.warning(f"无法创建日志文件: {e}")

    return logger


def get_logger(name: str) -> logging.Logger:
    """获取指定名称的日志记录器的快捷方法"""
    return setup_logger(name)
