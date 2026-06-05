"""全局日志配置

用法:
    from src.utils.logger import get_logger
    log = get_logger(__name__)

    log.debug("详细信息")
    log.info("关键流程节点")
    log.warning("异常分支")
    log.error("错误")

日志级别由环境变量 PLC_MGR_LOG_LEVEL 控制:
    DEBUG / INFO / WARNING / ERROR
默认 INFO，CLI 模式下输出到 stderr，UI 模式下输出到 logs/ 目录。
"""

from __future__ import annotations

import logging
import os
import sys

_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_DATE_FORMAT = "%H:%M:%S"

_initialized = False


def _ensure_initialized() -> None:
    """首次调用时配置根 logger"""
    global _initialized
    if _initialized:
        return
    _initialized = True

    level_name = os.environ.get("PLC_MGR_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    root = logging.getLogger("src")
    root.setLevel(level)

    # 避免重复添加 handler
    if not root.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(level)
        handler.setFormatter(logging.Formatter(_LOG_FORMAT, _DATE_FORMAT))
        root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """获取 logger 实例

    Args:
        name: 通常传 __name__，如 src.services.project_overview_service
    """
    _ensure_initialized()
    # 确保 logger 名以 src. 开头，受根 logger 管理
    if not name.startswith("src"):
        name = f"src.{name}"
    return logging.getLogger(name)
