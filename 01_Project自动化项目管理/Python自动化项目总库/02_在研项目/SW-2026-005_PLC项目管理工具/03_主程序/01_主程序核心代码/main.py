#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SW-2026-005 PLC项目管理工具 - 应用入口

基于SW-2026-004模式构建的PLC项目管理GUI应用程序。
支持项目创建、文档管理、PLC代码编辑、变量检查、HMI映射等功能。
"""
import sys
import os
from pathlib import Path


def get_base_path() -> Path:
    """获取基础路径（兼容PyInstaller打包）"""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent


def setup_paths():
    """设置Python路径，确保src模块可被正确导入"""
    base_path = get_base_path()
    src_path = base_path / "src"
    sys.path.insert(0, str(src_path))
    sys.path.insert(0, str(base_path))


setup_paths()

from src.core.config import ConfigLoader

ConfigLoader.load()
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def run_gui():
    """启动GUI界面"""
    from PyQt5.QtWidgets import QApplication
    from src.ui.main_window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName(ConfigLoader.get("app_name", "PLC项目管理工具"))
    app.setApplicationVersion(ConfigLoader.get("version", "1.0.0"))

    window = MainWindow()
    window.show()

    logger.info("GUI应用启动成功")
    sys.exit(app.exec_())


def main():
    """主函数 - 应用程序入口点"""
    if getattr(sys, "frozen", False):
        # 打包后的可执行文件直接运行GUI
        run_gui()
        return 0

    # 开发环境默认启动GUI模式
    run_gui()
    return 0


if __name__ == "__main__":
    sys.exit(main())
