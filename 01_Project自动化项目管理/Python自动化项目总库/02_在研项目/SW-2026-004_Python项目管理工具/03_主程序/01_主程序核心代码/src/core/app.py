# -*- coding: utf-8 -*-
"""
应用主入口类
"""
import sys
from typing import Optional
from pathlib import Path

from .config import Config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class Application:
    """应用主类"""
    def __init__(self, mode: str = "gui", debug: bool = False):
        self.mode = mode
        self.debug = debug
        self.running = False
        
        # 初始化日志
        if debug:
            import logging
            logging.getLogger().setLevel(logging.DEBUG)
        
        logger.info(f"应用初始化，运行模式: {mode}, 调试模式: {debug}")
    
    def run(self) -> int:
        """运行应用"""
        self.running = True
        
        try:
            if self.mode == "gui":
                return self._run_gui()
            elif self.mode == "cli":
                return self._run_cli()
            elif self.mode == "api":
                return self._run_api()
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
        """运行GUI模式"""
        try:
            from PyQt5.QtWidgets import QApplication
            from src.ui.main_window import MainWindow
            
            app = QApplication(sys.argv)
            window = MainWindow()
            window.show()
            
            return app.exec_()
        except ImportError as e:
            logger.error(f"GUI依赖未安装: {e}")
            logger.info("请安装PyQt5: pip install PyQt5")
            return 1
    
    def _run_cli(self) -> int:
        """运行CLI模式"""
        try:
            from src.cli.commands import cli
            return cli()
        except ImportError as e:
            logger.error(f"CLI依赖未安装: {e}")
            return 1
    
    def _run_api(self) -> int:
        """运行API服务模式"""
        try:
            from src.api.app import create_app
            
            app = create_app()
            host = Config.get("api.host", "127.0.0.1")
            port = Config.get("api.port", 5000)
            debug = self.debug or Config.get("debug_mode", False)
            
            logger.info(f"API服务启动，监听地址: http://{host}:{port}")
            app.run(host=host, port=port, debug=debug)
            return 0
        except ImportError as e:
            logger.error(f"API依赖未安装: {e}")
            logger.info("请安装Flask: pip install Flask")
            return 1
    
    def stop(self):
        """停止应用"""
        self.running = False
        logger.info("应用正在停止...")
