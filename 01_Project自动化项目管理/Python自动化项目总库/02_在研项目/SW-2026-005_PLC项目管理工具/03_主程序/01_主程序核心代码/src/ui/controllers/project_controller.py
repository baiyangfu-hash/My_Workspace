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

            from src.services.artifact_registry_service import ArtifactRegistryService
            from src.core.constants import ProjectType

            detected_type = ArtifactRegistryService.detect_project_type(str(project_root))

            if not has_root_config and detected_type == ProjectType.PLC_WORKSPACE:
                self._open_as_workspace(str(project_root))
                return

            is_likely_dj_project = (detected_type == ProjectType.DJ_SINGLE_MACHINE)

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

    def _open_as_workspace(self, workspace_path: str):
        """以工作空间模式打开目录

        Args:
            workspace_path: 工作空间根目录路径
        """
        try:
            from src.services.project_service import ProjectService

            projects, error = ProjectService.load_workspace_from_path(workspace_path)
            if not projects:
                QMessageBox.warning(
                    self._main_window,
                    "打开工作空间失败",
                    error or "未在工作空间中发现任何可管理的子项目",
                )
                return

            self._project_tree_widget.load_workspace(workspace_path, projects)
            self._main_window.statusBar().showMessage(
                f"已加载工作空间: {_Path(workspace_path).name} | 子项目: {len(projects)} 个"
            )
            logger.info(
                f"工作空间打开成功: {workspace_path}, 子项目数: {len(projects)}"
            )
        except Exception as e:
            logger.exception(f"打开工作空间失败: {e}")
            QMessageBox.critical(
                self._main_window, "错误", f"打开工作空间失败:\n{e}"
            )

    def check_workspace(self, workspace_path: str):
        """对工作空间执行跨项目检查"""
        try:
            from src.services.workspace_service import WorkspaceService
            from src.services.project_service import ProjectService

            projects, error = ProjectService.load_workspace_from_path(workspace_path)
            if not projects:
                QMessageBox.warning(
                    self._main_window, "工作空间检查",
                    error or "无法加载工作空间",
                )
                return

            check_items = WorkspaceService.check_workspace(workspace_path, projects)

            error_count = sum(1 for i in check_items if i.severity == "error")
            warning_count = sum(1 for i in check_items if i.severity == "warning")

            if error_count == 0 and warning_count == 0:
                QMessageBox.information(
                    self._main_window, "工作空间检查",
                    f"工作空间检查完成: 全部通过\n"
                    f"共检查 {len(projects)} 个子项目, {len(check_items)} 个检查项",
                )
            else:
                details = "\n".join(
                    f"[{i.severity.upper()}] {i.project_name}: {i.message}"
                    for i in check_items
                    if i.severity in ("error", "warning")
                )
                QMessageBox.warning(
                    self._main_window, "工作空间检查",
                    f"工作空间检查完成:\n"
                    f"  错误: {error_count}, 警告: {warning_count}\n\n"
                    f"{details}",
                )

            self._main_window.statusBar().showMessage(
                f"工作空间检查完成: {error_count}个错误, {warning_count}个警告", 5000
            )
        except Exception as e:
            logger.exception(f"工作空间检查失败: {e}")
            QMessageBox.critical(
                self._main_window, "错误", f"工作空间检查失败:\n{e}"
            )

    def generate_workspace_report(self, workspace_path: str):
        """生成工作空间聚合报告"""
        try:
            from src.services.project_service import ProjectService

            report, error = ProjectService.generate_workspace_report(workspace_path)
            if not report:
                QMessageBox.warning(
                    self._main_window, "聚合报告",
                    error or "报告生成失败",
                )
                return

            report_dict = report.to_dict()
            summary_text = (
                f"工作空间聚合报告: {report.workspace_name}\n"
                f"  子项目数: {report.total_projects}\n"
                f"  ST文件总数: {report.total_st_files}\n"
                f"  规范文件总数: {report.total_spec_files}\n"
                f"  命名冲突: {len(report.naming_conflicts)}\n"
                f"  检查项: {len(report.check_items)}\n"
                f"  生成时间: {report.generated_at}"
            )

            QMessageBox.information(
                self._main_window, "工作空间聚合报告", summary_text
            )
            self._main_window.statusBar().showMessage(
                f"聚合报告已生成: {report.total_projects}个项目, "
                f"{report.total_st_files}个ST文件", 5000
            )
        except Exception as e:
            logger.exception(f"聚合报告生成失败: {e}")
            QMessageBox.critical(
                self._main_window, "错误", f"聚合报告生成失败:\n{e}"
            )

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
