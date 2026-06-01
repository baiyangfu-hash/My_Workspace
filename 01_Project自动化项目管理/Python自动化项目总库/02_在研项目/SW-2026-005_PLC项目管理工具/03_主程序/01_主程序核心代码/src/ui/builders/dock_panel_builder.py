# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDockWidget, QMainWindow
from PyQt5.QtCore import Qt

from src.ui.ui_scale import current_ui_profile
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class DockPanelBuilder:

    @staticmethod
    def build(main_window: QMainWindow, ui_profile=None) -> dict:
        profile = ui_profile or current_ui_profile(main_window)
        result = {
            "diagnostic_panel": None,
            "diagnostic_dock": None,
            "spec_check_panel": None,
            "spec_check_dock": None,
        }

        try:
            from ..widgets.diagnostic_panel import DiagnosticPanel

            diagnostic_panel = DiagnosticPanel()
            diagnostic_dock = QDockWidget(
                "\U0001F52C 深度诊断", main_window
            )
            diagnostic_dock.setWidget(diagnostic_panel)
            diagnostic_dock.setMinimumHeight(profile.dock_min_height)
            diagnostic_dock.setMaximumHeight(profile.dock_max_height)
            diagnostic_dock.setAllowedAreas(
                Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea
            )
            main_window.addDockWidget(Qt.BottomDockWidgetArea, diagnostic_dock)

            diagnostic_panel.source_jump_requested.connect(
                main_window._jump_to_source
            )
            logger.info("深度诊断面板已创建")

            result["diagnostic_panel"] = diagnostic_panel
            result["diagnostic_dock"] = diagnostic_dock

        except ImportError as e:
            logger.error(f"无法导入面板组件: {e}")
        except Exception as e:
            logger.exception(f"创建DockWidget面板失败: {e}")

        try:
            from ..widgets.spec_check_panel import SpecCheckPanel

            spec_check_panel = SpecCheckPanel()
            spec_check_dock = QDockWidget(
                "\u2705 规范检查", main_window
            )
            spec_check_dock.setWidget(spec_check_panel)
            spec_check_dock.setMinimumHeight(profile.dock_min_height)
            spec_check_dock.setMaximumHeight(profile.dock_max_height)
            spec_check_dock.setAllowedAreas(
                Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea
            )
            main_window.addDockWidget(Qt.BottomDockWidgetArea, spec_check_dock)

            spec_check_panel.source_jump_requested.connect(
                main_window._jump_to_source
            )
            logger.info("规范检查Dock面板已创建")

            result["spec_check_panel"] = spec_check_panel
            result["spec_check_dock"] = spec_check_dock

        except ImportError as e:
            logger.error(f"无法导入规范检查面板组件: {e}")
        except Exception as e:
            logger.exception(f"创建规范检查DockWidget面板失败: {e}")

        return result
