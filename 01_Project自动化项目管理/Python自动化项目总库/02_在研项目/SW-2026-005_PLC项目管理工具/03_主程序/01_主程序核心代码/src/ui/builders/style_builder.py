# -*- coding: utf-8 -*-
import sys
from pathlib import Path

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QFont, QFontDatabase

from src.ui.ui_scale import build_runtime_stylesheet, current_ui_profile
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

_font_preloaded = False


def _preload_system_fonts():
    global _font_preloaded
    if _font_preloaded:
        return

    db = QFontDatabase()
    font_paths = [
        Path(r"C:\Windows\Fonts\msyh.ttc"),
        Path(r"C:\Windows\Fonts\msyhl.ttc"),
        Path(r"C:\Windows\Fonts\simsun.ttc"),
        Path(r"C:\Windows\Fonts\simhei.ttf"),
    ]

    for font_path in font_paths:
        if font_path.exists():
            try:
                font_id = db.addApplicationFont(str(font_path))
                if font_id >= 0:
                    families = db.applicationFontFamilies(font_id)
                    logger.debug(f"预加载字体: {font_path.name} -> {families}")
                else:
                    logger.warning(f"字体加载失败: {font_path}")
            except Exception as e:
                logger.debug(f"字体加载异常: {font_path} - {e}")

    _font_preloaded = True


def _find_resources_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent

    base_path = Path(__file__).resolve()
    for _ in range(8):
        base_path = base_path.parent
        if (base_path / "resources").exists():
            return base_path

    return Path(__file__).resolve().parent.parent.parent.parent


class StyleBuilder:

    @staticmethod
    def apply(widget: QWidget, theme: str):
        _preload_system_fonts()
        profile = current_ui_profile(widget)

        base_path = _find_resources_root()
        _theme_alias = {"ide_dark": "dark", "ide_light": "light", "dark": "dark", "light": "light"}
        resolved = _theme_alias.get(theme, theme)
        theme_filenames = [f"{resolved}.qss", f"material_{resolved}.qss", f"{theme}.qss", f"material_{theme}.qss"]
        qss_path = None
        for fname in theme_filenames:
            candidate = base_path / "resources" / "styles" / fname
            if candidate.exists():
                qss_path = candidate
                break
        if qss_path is None:
            qss_path = base_path / "resources" / "styles" / f"{theme}.qss"
        logger.debug(f"尝试加载 QSS 文件: {qss_path}")

        qss_content = ""
        if qss_path.exists():
            try:
                with open(qss_path, 'r', encoding='utf-8') as f:
                    qss_content = f.read()
                logger.info(f"已加载主题样式: {qss_path} (长度: {len(qss_content)} 字符)")
            except IOError as e:
                logger.error(f"主题文件读取失败: {e}")
                qss_content = StyleBuilder.get_default_stylesheet()
        else:
            logger.warning(f"QSS 文件不存在: {qss_path}, 使用 fallback 样式")
            qss_content = StyleBuilder.get_default_stylesheet()

        widget.setStyleSheet(
            qss_content + "\n" + build_runtime_stylesheet(profile)
        )
        font = StyleBuilder._resolve_chinese_font(profile.base_font_pt)
        font.setStyleStrategy(font.PreferAntialias | font.PreferMatch)
        widget.setFont(font)

    @staticmethod
    def get_default_stylesheet() -> str:
        return """
QMainWindow { background-color: #F5F5F5; }
QToolBox { background-color: #2D2D30; color: #D4D4D4; }
QToolBox::tab {
    font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
    color: #D4D4D4; padding: 10px 12px;
}
QPushButton[SidebarBtn="true"] {
    text-align: left; padding: 8px 12px;
    border: none; border-radius: 0px;
    background-color: transparent; color: #D4D4D4;
    font-size: 9pt; font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
}
QPushButton[SidebarBtn="true"]:hover {
    background-color: #3E3E42; color: #FF8C00;
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
