# -*- coding: utf-8 -*-
"""
DashboardController - 仪表盘功能控制器

负责仪表盘快捷操作分发、统计数据刷新。
从 main_window.py 抽取，实现 UI 层按功能域拆分。
"""
from __future__ import annotations

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class DashboardController:
    """仪表盘功能控制器"""

    def __init__(self, main_window):
        self._main_window = main_window

    @property
    def _dashboard_page(self):
        return self._main_window.get_dashboard_page()

    @property
    def _menu_manager(self):
        return self._main_window.get_menu_manager()

    def on_dashboard_action(self, action_id: str):
        logger.info(f"Dashboard动作: {action_id}")

        action_map = {
            "new_project": lambda: (
                self._menu_manager._on_new_project()
                if self._menu_manager else None
            ),
            "open_project": lambda: (
                self._menu_manager._on_open_project()
                if self._menu_manager else None
            ),
            "new_document": lambda: self._main_window._navigate_to_tab(self._main_window.TAB_DOCUMENT),
            "spec_check": lambda: self._main_window._navigate_to_tab(self._main_window.TAB_SPEC_CHECK),
            "variable_check": lambda: self._main_window._navigate_to_tab(self._main_window.TAB_PLC_TOOLS),
            "generate_report": lambda: (
                self._menu_manager._on_run_diagnostic()
                if self._menu_manager else None
            ),
        }

        handler = action_map.get(action_id)
        if handler:
            try:
                handler()
            except Exception as e:
                logger.exception(f"Dashboard动作执行失败 [{action_id}]: {e}")

    def refresh_dashboard_data(self):
        if not self._dashboard_page:
            return

        try:
            from src.services.project_service import ProjectService
            from src.core.settings import SettingsManager

            projects = ProjectService.get_all_projects() or []
            total = len(projects)

            active = sum(
                1 for p in projects
                if getattr(getattr(p, 'status', None), 'value', '') == 'active'
            )
            completed = sum(
                1 for p in projects
                if getattr(getattr(p, 'status', None), 'value', '') == 'completed'
            )
            archived = total - active - completed

            self._dashboard_page.refresh_statistics(
                total, active, completed, archived
            )

            recent = SettingsManager.get_recent_projects() or []
            self._dashboard_page.refresh_recent_projects(recent)

        except Exception as e:
            logger.warning(f"刷新Dashboard数据失败: {e}")
