#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LIB_DIR = BASE_DIR / "lib"
if LIB_DIR.is_dir() and str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
sys.path.insert(0, str(BASE_DIR))

USE_WEBVIEW = os.environ.get("PLC_GUI_MODE", "webview") == "webview"


def run_webview():
    import webview
    from src.core.config import ConfigLoader
    ConfigLoader.load()
    from src.utils.logger import setup_logger
    logger = setup_logger(__name__)
    app_name = ConfigLoader.get("app_name", "PLC项目管理工具")
    version = ConfigLoader.get("version", "1.0.0")
    title = f"{app_name} V{version}"
    html_path = str(BASE_DIR / "ui_prototype" / "index.html")
    logger.info("PyWebView模式启动: %s | HTML: %s", title, html_path)
    from src.ui.webview_window import create_window
    window = create_window(html_path=html_path, title=title)
    webview.start(debug=True)
    logger.info("PyWebView已退出")


def run_pyqt():
    from PyQt5.QtCore import QCoreApplication, Qt
    from PyQt5.QtGui import QGuiApplication
    from PyQt5.QtWidgets import QApplication
    from src.core.config import ConfigLoader
    ConfigLoader.load()
    from src.utils.logger import setup_logger
    logger = setup_logger(__name__)
    from src.ui.main_window import MainWindow
    from src.ui.builders.style_builder import StyleBuilder
    from src.ui.ui_scale import (
        collect_screen_metrics,
        current_ui_profile,
        format_screen_metrics,
    )
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    try:
        QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
    except Exception:
        pass
    app = QApplication(sys.argv)
    app.setApplicationName(ConfigLoader.get("app_name", "PLC项目管理工具"))
    app.setApplicationVersion(ConfigLoader.get("version", "1.0.0"))
    from src.ui.builders.style_builder import _preload_system_fonts
    _preload_system_fonts()
    screen_metrics = collect_screen_metrics(QGuiApplication.primaryScreen())
    ui_profile = current_ui_profile(QGuiApplication.primaryScreen())
    chinese_font = StyleBuilder._resolve_chinese_font(ui_profile.base_font_pt)
    chinese_font.setStyleStrategy(chinese_font.PreferAntialias | chinese_font.PreferMatch)
    app.setFont(chinese_font)
    window = MainWindow()
    window.show()
    logger.info("PyQt5模式启动 (字体: %s %dpt)", chinese_font.family(), chinese_font.pointSize())
    exit_code = app.exec_()
    app.processEvents()
    app.closeAllWindows()
    import gc
    gc.collect()
    sys.exit(exit_code)


def main():
    if USE_WEBVIEW:
        try:
            run_webview()
        except ImportError:
            print("[WARN] pywebview不可用, 回退到PyQt5模式")
            run_pyqt()
    else:
        run_pyqt()
    return 0


if __name__ == "__main__":
    sys.exit(main())
