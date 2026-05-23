# -*- coding: utf-8 -*-
from pathlib import Path

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QFont, QFontDatabase

from src.core.settings import SettingsManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class StyleBuilder:

    @staticmethod
    def apply(widget: QWidget, theme: str):
        font = StyleBuilder._resolve_chinese_font(10)
        widget.setFont(font)

        base_path = Path(__file__).resolve()
        for _ in range(5):
            base_path = base_path.parent
            if (base_path / "resources").exists():
                break

        qss_path = base_path / "resources" / "styles" / f"material_{theme}.qss"

        if qss_path.exists():
            try:
                with open(qss_path, 'r', encoding='utf-8') as f:
                    qss_content = f.read()
                    widget.setStyleSheet(qss_content)
                logger.debug(f"已加载主题样式: {qss_path}")
                return
            except IOError as e:
                logger.warning(f"主题文件读取失败: {e}")

        widget.setStyleSheet(StyleBuilder.get_default_stylesheet())

    @staticmethod
    def get_default_stylesheet() -> str:
        return """
            QMainWindow { background-color: #FAFAFA; }
            QToolBox::tab {
                font-family: "Microsoft YaHei UI", "Microsoft YaHei", "SimHei", sans-serif;
            }
            QPushButton[SidebarBtn="true"] {
                text-align: left;
                padding: 8px 12px;
                border: none;
                border-radius: 4px;
                background-color: transparent;
                color: #424242;
                font-size: 9pt;
                font-family: "Microsoft YaHei UI", "Microsoft YaHei", "SimHei", sans-serif;
            }
            QPushButton[SidebarBtn="true"]:hover {
                background-color: #E3F2FD;
                color: #1976D2;
            }
        """

    @staticmethod
    def _resolve_chinese_font(size: int = 10) -> QFont:
        chinese_fonts = [
            "Microsoft YaHei UI", "Microsoft YaHei", "SimHei",
            "PingFang SC", "Noto Sans CJK SC", "WenQuanYi Micro Hei",
            "STHeiti", "Arial Unicode MS", "SimSun",
        ]
        db = QFontDatabase()
        families = db.families()
        for name in chinese_fonts:
            if name in families:
                return QFont(name, size)
        font = QFont("", size)
        font.setStyleHint(QFont.SansSerif)
        return font
