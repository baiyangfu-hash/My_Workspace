# -*- coding: utf-8 -*-
"""
日志工具
"""
import logging
import sys
from pathlib import Path
from typing import Optional

from src.core.config import Config

def setup_logger(name: Optional[str] = None, log_level: Optional[int] = None) -> logging.Logger:
    """设置日志记录器"""
    logger = logging.getLogger(name or __name__)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 设置日志级别
    if log_level is None:
        debug_mode = Config.get("debug_mode", False)
        log_level = logging.DEBUG if debug_mode else logging.INFO
    
    logger.setLevel(log_level)
    
    # 格式化器
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    logger.addHandler(console_handler)
    
    # 文件处理器
    try:
        log_dir = Path(__file__).parent.parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / "app.log"
        
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"无法创建日志文件: {e}")
    
    return logger
