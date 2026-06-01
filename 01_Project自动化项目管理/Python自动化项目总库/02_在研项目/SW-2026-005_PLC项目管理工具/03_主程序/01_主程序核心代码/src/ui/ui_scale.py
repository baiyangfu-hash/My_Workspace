# -*- coding: utf-8 -*-
"""
GUI 尺寸策略层

统一根据屏幕参数推导窗口、字号、间距和关键控件尺寸，
避免各个页面散落硬编码像素值。
"""
from dataclasses import dataclass
from math import sqrt
from typing import Any, Dict, Optional

from PyQt5.QtGui import QGuiApplication, QScreen

from src.core.settings import SettingsManager

BASE_LOGICAL_DPI = 96.0
TARGET_BASE_WIDTH = 2560.0
TARGET_BASE_HEIGHT = 1600.0


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def _get_screen(window_or_screen=None) -> Optional[QScreen]:
    if isinstance(window_or_screen, QScreen):
        return window_or_screen
    if window_or_screen is not None and hasattr(window_or_screen, "screen"):
        try:
            screen = window_or_screen.screen()
            if screen:
                return screen
        except Exception:
            pass
    return QGuiApplication.primaryScreen()


def collect_screen_metrics(window_or_screen=None) -> Dict[str, float]:
    """采集屏幕指标，用于日志与 UI profile 计算。"""
    screen = _get_screen(window_or_screen)
    if not screen:
        return {
            "screen_name": "unknown",
            "geometry_width": 1920,
            "geometry_height": 1080,
            "available_width": 1920,
            "available_height": 1040,
            "device_pixel_ratio": 1.0,
            "logical_dpi": BASE_LOGICAL_DPI,
            "physical_width": 1920,
            "physical_height": 1080,
            "available_physical_width": 1920,
            "available_physical_height": 1040,
        }

    geometry = screen.geometry()
    available = screen.availableGeometry()
    dpr = float(screen.devicePixelRatio() or 1.0)
    logical_dpi = float(screen.logicalDotsPerInch() or BASE_LOGICAL_DPI)

    return {
        "screen_name": screen.name() or "primary",
        "geometry_width": geometry.width(),
        "geometry_height": geometry.height(),
        "available_width": available.width(),
        "available_height": available.height(),
        "device_pixel_ratio": dpr,
        "logical_dpi": logical_dpi,
        "physical_width": int(round(geometry.width() * dpr)),
        "physical_height": int(round(geometry.height() * dpr)),
        "available_physical_width": int(round(available.width() * dpr)),
        "available_physical_height": int(round(available.height() * dpr)),
    }


@dataclass(frozen=True)
class UIProfile:
    scale_factor: float
    density: str
    target_machine_mode: bool
    base_font_pt: int
    small_font_pt: int
    section_font_pt: int
    title_font_pt: int
    value_font_pt: int
    hero_icon_pt: int
    spacing_xs: int
    spacing_sm: int
    spacing_md: int
    spacing_lg: int
    spacing_xl: int
    spacing_xxl: int
    window_min_width: int
    window_min_height: int
    sidebar_min_width: int
    sidebar_default_width: int
    sidebar_max_width: int
    right_panel_min_width: int
    dock_min_height: int
    dock_max_height: int
    button_min_height: int
    compact_button_height: int
    guide_button_height: int
    dialog_width: int
    dialog_height: int
    dialog_min_width: int
    dialog_min_height: int
    description_max_height: int
    stat_card_min_height: int
    stat_card_max_height: int
    quick_action_min_height: int
    recent_scroll_height: int
    guide_padding: int

    def scale_px(self, value: int) -> int:
        return max(1, int(round(value * self.scale_factor)))

    def font_pt(self, value: int) -> int:
        return max(8, int(round(value * self.scale_factor)))


def build_ui_scale_profile(
    metrics: Dict[str, float],
    density: Optional[str] = None,
    target_machine_mode: Optional[bool] = None,
) -> UIProfile:
    """根据屏幕指标生成统一 UI 尺寸配置。"""
    density = density or SettingsManager.get("ui_density", "target_machine")
    if target_machine_mode is None:
        target_machine_mode = bool(
            SettingsManager.get("ui_target_machine_mode", True)
        )

    density_multipliers = {
        "compact": 0.98,
        "standard": 1.04,
        "comfortable": 1.10,
        "target_machine": 1.15,
    }
    density_multiplier = density_multipliers.get(density, 1.04)

    physical_width = float(metrics.get("physical_width", 1920))
    physical_height = float(metrics.get("physical_height", 1080))
    logical_dpi = float(metrics.get("logical_dpi", BASE_LOGICAL_DPI))

    area_factor = sqrt(
        max(physical_width * physical_height, 1.0)
        / (TARGET_BASE_WIDTH * TARGET_BASE_HEIGHT)
    )
    dpi_factor = _clamp(logical_dpi / BASE_LOGICAL_DPI, 1.0, 2.0)
    blended_factor = (area_factor * 0.70) + (dpi_factor * 0.30)

    if target_machine_mode and physical_width >= 2500:
        blended_factor = max(blended_factor, 1.15)

    scale_factor = _clamp(blended_factor * density_multiplier, 1.0, 1.65)

    def px(value: int) -> int:
        return max(1, int(round(value * scale_factor)))

    def pt(value: int) -> int:
        return max(8, int(round(value * scale_factor)))

    return UIProfile(
        scale_factor=scale_factor,
        density=density,
        target_machine_mode=target_machine_mode,
        base_font_pt=pt(11),
        small_font_pt=pt(10),
        section_font_pt=pt(13),
        title_font_pt=pt(20),
        value_font_pt=pt(24),
        hero_icon_pt=pt(52),
        spacing_xs=px(5),
        spacing_sm=px(8),
        spacing_md=px(10),
        spacing_lg=px(14),
        spacing_xl=px(18),
        spacing_xxl=px(28),
        window_min_width=px(1320),
        window_min_height=px(900),
        sidebar_min_width=px(210),
        sidebar_default_width=px(280),
        sidebar_max_width=px(400),
        right_panel_min_width=px(940),
        dock_min_height=px(260),
        dock_max_height=px(540),
        button_min_height=px(36),
        compact_button_height=px(40),
        guide_button_height=px(48),
        dialog_width=px(720),
        dialog_height=px(540),
        dialog_min_width=px(660),
        dialog_min_height=px(500),
        description_max_height=px(260),
        stat_card_min_height=px(96),
        stat_card_max_height=px(128),
        quick_action_min_height=px(58),
        recent_scroll_height=px(200),
        guide_padding=px(52),
    )


def current_ui_profile(window_or_screen=None) -> UIProfile:
    metrics = collect_screen_metrics(window_or_screen)
    return build_ui_scale_profile(metrics)


def format_screen_metrics(metrics: Dict[str, float]) -> str:
    return (
        f"screen={metrics.get('screen_name')} "
        f"geometry={metrics.get('geometry_width')}x{metrics.get('geometry_height')} "
        f"available={metrics.get('available_width')}x{metrics.get('available_height')} "
        f"physical={metrics.get('physical_width')}x{metrics.get('physical_height')} "
        f"dpr={metrics.get('device_pixel_ratio'):.2f} "
        f"logical_dpi={metrics.get('logical_dpi'):.2f}"
    )


def build_runtime_stylesheet(profile: UIProfile) -> str:
    """生成覆盖型样式，统一常用控件尺寸和字号。"""
    return f"""
QTabBar::tab {{
    padding: {profile.scale_px(10)}px {profile.scale_px(22)}px;
    font-size: {profile.font_pt(10)}pt;
    min-width: {profile.scale_px(96)}px;
    min-height: {profile.scale_px(36)}px;
}}
QToolBox::tab {{
    padding: {profile.scale_px(14)}px {profile.scale_px(16)}px;
    font-size: {profile.font_pt(10)}pt;
}}
QPushButton {{
    padding: {profile.scale_px(8)}px {profile.scale_px(20)}px;
    font-size: {profile.font_pt(9)}pt;
    min-height: {profile.button_min_height}px;
}}
QLineEdit,
QTextEdit,
QPlainTextEdit,
QComboBox {{
    padding: {profile.scale_px(8)}px {profile.scale_px(12)}px;
    font-size: {profile.font_pt(10)}pt;
    min-height: {profile.button_min_height}px;
}}
QTableWidget,
QTableView,
QTreeWidget,
QListWidget {{
    font-size: {profile.font_pt(9)}pt;
}}
QHeaderView::section {{
    padding: {profile.scale_px(10)}px {profile.scale_px(8)}px;
    font-size: {profile.font_pt(9)}pt;
}}
QMenuBar {{
    font-size: {profile.font_pt(10)}pt;
}}
QMenu::item,
QToolBar QToolButton,
QStatusBar,
QToolTip {{
    font-size: {profile.font_pt(9)}pt;
}}
QGroupBox {{
    margin-top: {profile.scale_px(12)}px;
    padding: {profile.scale_px(20)}px {profile.scale_px(12)}px {profile.scale_px(12)}px {profile.scale_px(12)}px;
}}
QGroupBox::title {{
    left: {profile.scale_px(12)}px;
    padding: 0 {profile.scale_px(8)}px;
    font-size: {profile.font_pt(10)}pt;
}}
QCheckBox,
QRadioButton {{
    spacing: {profile.scale_px(8)}px;
    font-size: {profile.font_pt(10)}pt;
}}
QCheckBox::indicator,
QRadioButton::indicator {{
    width: {profile.scale_px(18)}px;
    height: {profile.scale_px(18)}px;
}}
QLabel[dashboardTitle="true"] {{
    font-size: {profile.title_font_pt}pt;
}}
QLabel[sectionTitle="true"] {{
    font-size: {profile.section_font_pt}pt;
}}
QLabel[welcomeText="true"] {{
    font-size: {profile.font_pt(11)}pt;
}}
QLabel[statCardTitle="true"] {{
    font-size: {profile.font_pt(10)}pt;
}}
QFrame[StatCard="true"] QLabel[valueLabel="true"] {{
    font-size: {profile.value_font_pt}pt;
}}
QPushButton[QuickAction="true"] {{
    font-size: {profile.font_pt(10)}pt;
    padding-left: {profile.scale_px(14)}px;
    min-height: {profile.quick_action_min_height}px;
}}
QPushButton[SidebarBtn="true"] {{
    padding: {profile.scale_px(8)}px {profile.scale_px(12)}px;
    font-size: {profile.font_pt(9)}pt;
}}
QLabel[SidebarHeader="true"] {{
    font-size: {profile.font_pt(11)}pt;
    padding: {profile.scale_px(6)}px {profile.scale_px(4)}px;
}}
QFrame[IndustrialSeparator="true"] {{
    max-height: 1px;
    margin: {profile.spacing_xs}px 0;
}}
QLabel[recentProjectItem="true"] {{
    font-size: {profile.font_pt(10)}pt;
}}
QLabel[treeHeader="true"] {{
    font-size: {profile.font_pt(10)}pt;
}}
QLabel[treeStatus="true"] {{
    font-size: {profile.font_pt(9)}pt;
}}
"""
