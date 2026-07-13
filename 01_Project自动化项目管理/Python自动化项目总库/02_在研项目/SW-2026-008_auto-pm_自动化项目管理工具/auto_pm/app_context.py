"""PLC-HMI 概念映射：SFB 库函数（应用上下文（全局状态管理/工作空间信息））

像 PLC 的 SFB/SFC 系统函数，被 FB 功能块（application/*_facade.py）调用，
不直接暴露给 HMI 画面。

--- 原始注释 ---

应用上下文 - 持有 CLI 命令所需的全局对象"""

from __future__ import annotations

import os

from auto_pm import __app_name__
from auto_pm.config.app_config import AutoPmConfig
from auto_pm.logging.logging import setup_logger


class AppContext:
    """Holds all the objects needed by commands"""

    def __init__(self, workspace_root: str = "") -> None:
        self.app_config = AutoPmConfig(app_name=__app_name__)
        self.logger = setup_logger(
            log_level=self.app_config.log_level, app_name=__app_name__
        )
        # 工作空间根目录（项目库所在目录）
        self.workspace_root: str = workspace_root or os.getcwd()

    @property
    def templates_dir(self) -> str:
        """模板目录：项目根目录下的 templates/"""
        # auto_pm/app_context.py -> auto_pm/ -> 项目根/templates/
        package_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(package_dir)
        return os.path.join(project_root, "templates")
