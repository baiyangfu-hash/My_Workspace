# -*- coding: utf-8 -*-
"""
ProjectController - 项目管理功能控制器

负责项目创建/打开/关闭事件处理、项目信息面板更新。
从 main_window.py 抽取，实现 UI 层按功能域拆分。
"""
from __future__ import annotations

from PyQt5.QtWidgets import QMessageBox

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ProjectController:
    """项目管理功能控制器"""

    def __init__(self, main_window):
        self._main_window = main_window

    @property
    def _project_tree_widget(self):
        return self._main_window.get_project_tree_widget()

    @property
    def _labels(self):
        return self._main_window.get_project_info_labels()

    def on_project_created(self, path: str):
        try:
            from src.services.project_service import ProjectService

            created_project = None
            for proj in ProjectService.get_all_projects():
                if getattr(proj, 'path', '') == path:
                    created_project = proj
                    break

            if created_project:
                self._project_tree_widget.load_project(created_project)
                logger.info(f"项目树已刷新: {created_project.name}")
            else:
                project, error = ProjectService.load_project_from_path(path)
                if project:
                    self._project_tree_widget.load_project(project)
                    logger.info(f"从路径加载并刷新项目树: {project.name}")
                else:
                    logger.warning(f"无法加载项目到树: {error}")

        except Exception as e:
            logger.warning(f"刷新项目树时出错 (非致命): {e}")

    SUPPORTED_PROJECT_FILES = [
        "project.json",
        ".plc_project.json",
        ".plc.json",
    ]

    def on_project_opened(self, path: str):
        try:
            from pathlib import Path as _Path
            project_root = _Path(path)

            if not project_root.exists() or not project_root.is_dir():
                QMessageBox.warning(
                    self._main_window,
                    "打开项目失败",
                    f"所选路径不是有效的目录:\n\n{path}\n\n"
                    f"请选择一个包含项目配置文件的目录。\n"
                    f"支持的配置文件: {', '.join(self.SUPPORTED_PROJECT_FILES)}",
                )
                return

            has_root_config = any(
                (project_root / fname).exists()
                for fname in self.SUPPORTED_PROJECT_FILES
            )

            is_likely_dj_project = False
            if not has_root_config:
                try:
                    from src.services.artifact_registry_service import ArtifactRegistryService
                    from src.core.constants import ProjectType

                    detected_type = ArtifactRegistryService.detect_project_type(str(project_root))
                    is_likely_dj_project = (detected_type == ProjectType.DJ_SINGLE_MACHINE)
                except Exception:
                    pass

            if not has_root_config and not is_likely_dj_project:
                QMessageBox.warning(
                    self._main_window,
                    "打开项目失败",
                    f"所选目录中未找到项目配置文件:\n\n{path}\n\n"
                    f"支持以下配置文件: {', '.join(self.SUPPORTED_PROJECT_FILES)}\n\n"
                    "提示: 可通过「新建项目」功能创建新项目。",
                )
                return

            from src.services.project_service import ProjectService

            project, error = ProjectService.load_project_from_path(path)
            if project:
                self._project_tree_widget.load_project(project)
                self._main_window.statusBar().showMessage(
                    f"已加载项目: {project.name} | 类型: {project.project_type.value}"
                )
                logger.info(f"项目打开并加载成功: {project.name}")
            else:
                logger.warning(f"项目打开失败: {error}")
                QMessageBox.warning(self._main_window, "打开项目失败", error or "未知错误")
        except Exception as e:
            logger.exception(f"处理项目打开事件失败: {e}")
            QMessageBox.critical(self._main_window, "错误", f"打开项目失败:\n{e}")

    def update_project_info(self, context: dict):
        self._main_window._navigate_to_tab(self._main_window.TAB_PROJECT)
        project = context.get("project")
        if not project:
            return

        try:
            name = getattr(project, "name", "-") or "-"
            project_id = getattr(project, "project_id", "-") or "-"
            project_type = getattr(project, "project_type", "-")
            project_type_str = getattr(project_type, "value", str(project_type)) if project_type else "-"
            project_path = getattr(project, "path", "-") or "-"
            stage = getattr(project, "workflow_stage", "-")
            stage_str = getattr(stage, "value", str(stage)) if stage else "-"

            labels = self._labels
            labels["name"].setText(str(name))
            labels["id"].setText(str(project_id))
            labels["type"].setText(str(project_type_str))
            labels["stage"].setText(str(stage_str))
            labels["path"].setText(str(project_path))

            description = getattr(project, "description", "")
            labels["desc"].setPlainText(
                str(description) if description else ""
            )

            self._main_window.statusBar().showMessage(
                f"\U0001F4C1 项目详情: {name}",
                3000,
            )
        except Exception as e:
            logger.warning(f"更新项目信息面板失败: {e}")
