# -*- coding: utf-8 -*-
"""
UI 尺寸策略测试

验证固定目标机适配相关的尺寸计算和关键页面尺寸落点。
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PyQt5.QtWidgets import QApplication

from src.ui.dashboard import DashboardPage
from src.ui.ui_scale import (
    UIProfile,
    build_runtime_stylesheet,
    build_ui_scale_profile,
    collect_screen_metrics,
)


class TestUIScaleProfile(unittest.TestCase):
    """验证 UI 尺寸策略计算。"""

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)

    def test_build_ui_scale_profile_for_target_machine(self):
        """固定目标机配置应得到放大后的 profile。"""
        metrics = {
            "physical_width": 2880,
            "physical_height": 1800,
            "logical_dpi": 96.0,
        }

        profile = build_ui_scale_profile(
            metrics,
            density="target_machine",
            target_machine_mode=True,
        )

        self.assertGreaterEqual(profile.scale_factor, 1.10)
        self.assertGreaterEqual(profile.sidebar_default_width, 260)
        self.assertGreaterEqual(profile.dock_max_height, 480)
        self.assertGreaterEqual(profile.dialog_width, 680)

    def test_collect_screen_metrics_contains_expected_keys(self):
        """运行时采样结果应包含诊断所需字段。"""
        metrics = collect_screen_metrics()

        for key in [
            "screen_name",
            "geometry_width",
            "geometry_height",
            "available_width",
            "available_height",
            "device_pixel_ratio",
            "logical_dpi",
            "physical_width",
            "physical_height",
        ]:
            self.assertIn(key, metrics)

    def test_build_runtime_stylesheet_contains_scaled_rules(self):
        """运行时样式表应包含关键控件的缩放覆盖。"""
        metrics = {
            "physical_width": 2880,
            "physical_height": 1800,
            "logical_dpi": 96.0,
        }
        profile = build_ui_scale_profile(
            metrics,
            density="target_machine",
            target_machine_mode=True,
        )

        stylesheet = build_runtime_stylesheet(profile)

        self.assertIn("QTabBar::tab", stylesheet)
        self.assertIn("QPushButton[QuickAction=\"true\"]", stylesheet)
        self.assertIn(f"font-size: {profile.title_font_pt}pt;", stylesheet)


class TestDashboardPageScaling(unittest.TestCase):
    """验证仪表盘是否使用统一 profile。"""

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)

    def _build_profile(self) -> UIProfile:
        return build_ui_scale_profile(
            {
                "physical_width": 2880,
                "physical_height": 1800,
                "logical_dpi": 96.0,
            },
            density="target_machine",
            target_machine_mode=True,
        )

    def test_dashboard_uses_profile_dimensions(self):
        """关键控件尺寸应来自 UIProfile。"""
        profile = self._build_profile()
        page = DashboardPage(ui_profile=profile)

        self.assertEqual(page.card_total.minimumHeight(), profile.stat_card_min_height)
        self.assertEqual(page.card_total.maximumHeight(), profile.stat_card_max_height)
        self.assertEqual(page._recent_scroll.maximumHeight(), profile.recent_scroll_height)

    def test_health_cards_are_created(self):
        """健康度区域应创建 5 张卡片。"""
        profile = self._build_profile()
        page = DashboardPage(ui_profile=profile)

        cards = [
            page._health_compliance,
            page._health_issues,
            page._health_libraries,
            page._health_structure,
            page._health_overall,
        ]
        self.assertEqual(len(cards), 5)
        self.assertTrue(all(card is not None for card in cards))


if __name__ == "__main__":
    unittest.main(verbosity=2)
