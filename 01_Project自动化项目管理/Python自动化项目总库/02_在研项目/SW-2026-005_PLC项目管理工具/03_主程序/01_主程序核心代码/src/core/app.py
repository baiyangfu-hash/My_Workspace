# -*- coding: utf-8 -*-
"""
应用主入口类

基于SW-2026-004的Application类模式构建。
支持GUI模式运行，提供统一的异常处理和错误报告机制。
"""
import sys
from typing import Optional

from .config import ConfigLoader
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class Application:
    """应用主类 - 管理应用生命周期"""

    def __init__(self, mode: str = "gui", debug: bool = False):
        """
        初始化应用实例

        Args:
            mode: 运行模式，目前仅支持 "gui"
            debug: 是否启用调试模式
        """
        self.mode = mode
        self.debug = debug
        self.running = False

        # 初始化日志级别
        if debug:
            import logging
            logging.getLogger().setLevel(logging.DEBUG)

        logger.info(f"应用初始化 - 运行模式: {mode}, 调试模式: {debug}")

    def run(self) -> int:
        """
        运行应用主循环

        Returns:
            int: 退出码，0表示正常退出，非0表示异常退出
        """
        self.running = True

        try:
            if self.mode == "gui":
                return self._run_gui()
            else:
                logger.error(f"不支持的运行模式: {self.mode}")
                return 1
        except Exception as e:
            logger.exception(f"应用运行出错: {e}")
            return 1
        finally:
            self.running = False
            logger.info("应用已退出")

    def _run_gui(self) -> int:
        """运行GUI模式 - 创建QApplication并显示MainWindow"""
        try:
            from PyQt5.QtWidgets import QApplication
            from src.ui.main_window import MainWindow

            qt_app = QApplication(sys.argv)
            qt_app.setApplicationName(
                ConfigLoader.get("app_name", "PLC项目管理工具")
            )
            qt_app.setApplicationVersion(
                ConfigLoader.get("version", "1.0.0")
            )

            window = MainWindow()
            window.show()

            return qt_app.exec_()
        except ImportError as e:
            logger.error(f"GUI依赖未安装: {e}")
            logger.info("请安装依赖: pip install PyQt5 QScintilla")
            return 1

    def stop(self):
        """停止应用运行"""
        self.running = False
        logger.info("应用正在停止...")
