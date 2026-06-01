# -*- coding: utf-8 -*-
"""
工作空间治理服务

提供跨项目检查、聚合报告和汇总统计功能。
工作空间是多个子项目的容器, 本服务负责:
1. 跨项目规范检查: 对工作空间内所有子项目执行统一检查
2. 聚合报告: 汇总各子项目的检查结果, 生成工作空间级报告
3. 汇总统计: 统计工作空间内子项目/资产/规范的总体情况
4. 命名冲突检测: 检测跨项目的FB/FC命名冲突
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.core.constants import (
    LIBRARY_ST_EXTENSIONS,
    ProjectType,
)
from src.services.artifact_registry_service import ArtifactRegistryService
from src.services.library_service import LibraryService
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class WorkspaceCheckItem:
    """工作空间检查条目"""
    project_name: str
    project_path: str
    project_type: str
    status: str
    message: str
    severity: str = "info"

    def to_dict(self) -> Dict:
        return {
            "project_name": self.project_name,
            "project_path": self.project_path,
            "project_type": self.project_type,
            "status": self.status,
            "message": self.message,
            "severity": self.severity,
        }


@dataclass
class NamingConflict:
    """命名冲突条目"""
    name: str
    locations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "locations": self.locations,
        }


@dataclass
class WorkspaceReport:
    """工作空间聚合报告"""
    workspace_path: str
    workspace_name: str
    generated_at: str = ""
    total_projects: int = 0
    total_st_files: int = 0
    total_spec_files: int = 0
    project_summaries: List[Dict] = field(default_factory=list)
    check_items: List[WorkspaceCheckItem] = field(default_factory=list)
    naming_conflicts: List[NamingConflict] = field(default_factory=list)
    library_summaries: List[Dict] = field(default_factory=list)

    def __post_init__(self):
        if not self.generated_at:
            self.generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> Dict:
        return {
            "workspace_path": self.workspace_path,
            "workspace_name": self.workspace_name,
            "generated_at": self.generated_at,
            "total_projects": self.total_projects,
            "total_st_files": self.total_st_files,
            "total_spec_files": self.total_spec_files,
            "project_summaries": self.project_summaries,
            "check_items": [i.to_dict() for i in self.check_items],
            "naming_conflicts": [c.to_dict() for c in self.naming_conflicts],
            "library_summaries": self.library_summaries,
        }


class WorkspaceService:
    """工作空间治理服务

    职责:
    1. 跨项目规范检查
    2. 聚合报告生成
    3. 汇总统计
    4. 命名冲突检测
    """

    @classmethod
    def generate_report(
        cls, workspace_path: str, projects: List[Any]
    ) -> Optional[WorkspaceReport]:
        """生成工作空间聚合报告

        Args:
            workspace_path: 工作空间根目录路径
            projects: 子项目 Project 对象列表

        Returns:
            WorkspaceReport | None
        """
        root = Path(workspace_path)
        if not root.exists():
            return None

        report = WorkspaceReport(
            workspace_path=str(root),
            workspace_name=root.name,
            total_projects=len(projects),
        )

        total_st = 0
        total_spec = 0

        for project in projects:
            proj_type = getattr(project, "project_type", ProjectType.GENERIC)
            proj_type_value = getattr(proj_type, "value", str(proj_type))
            proj_path = getattr(project, "path", "")
            proj_name = getattr(project, "name", "")

            summary: Dict = {
                "name": proj_name,
                "path": proj_path,
                "type": proj_type_value,
            }

            if proj_type_value == ProjectType.PLC_LIBRARY.value:
                lib_summary = LibraryService.get_library_summary(proj_path)
                if lib_summary:
                    summary["library"] = lib_summary
                    total_st += lib_summary.get("total_st_files", 0)
                    total_spec += lib_summary.get("total_spec_files", 0)
                    report.library_summaries.append(lib_summary)

                    if lib_summary.get("has_orphan_files"):
                        report.check_items.append(WorkspaceCheckItem(
                            project_name=proj_name,
                            project_path=proj_path,
                            project_type=proj_type_value,
                            status="warning",
                            message=f"共享库存在 {len(LibraryService.scan_library(proj_path).orphan_files if LibraryService.scan_library(proj_path) else [])} 个孤立文件",
                            severity="warning",
                        ))
            else:
                st_count, spec_count = cls._count_project_files(proj_path)
                summary["st_files"] = st_count
                summary["spec_files"] = spec_count
                total_st += st_count
                total_spec += spec_count

            report.project_summaries.append(summary)

        report.total_st_files = total_st
        report.total_spec_files = total_spec

        naming_conflicts = cls.detect_naming_conflicts(projects)
        report.naming_conflicts = naming_conflicts

        for conflict in naming_conflicts:
            report.check_items.append(WorkspaceCheckItem(
                project_name="*",
                project_path="",
                project_type="workspace",
                status="warning",
                message=f"命名冲突: {conflict.name} 存在于 {len(conflict.locations)} 个位置",
                severity="warning",
            ))

        logger.info(
            f"工作空间报告生成完成: {root.name}, "
            f"{report.total_projects}个项目, "
            f"{report.total_st_files}个ST文件, "
            f"{len(report.naming_conflicts)}个命名冲突"
        )
        return report

    @classmethod
    def detect_naming_conflicts(
        cls, projects: List[Any]
    ) -> List[NamingConflict]:
        """检测跨项目的FB/FC命名冲突

        扫描所有子项目的ST源码文件, 检测同名文件在不同子项目中重复出现。

        Args:
            projects: 子项目 Project 对象列表

        Returns:
            List[NamingConflict]
        """
        name_to_locations: Dict[str, List[str]] = {}

        for project in projects:
            proj_path = getattr(project, "path", "")
            proj_name = getattr(project, "name", "")
            if not proj_path or not os.path.exists(proj_path):
                continue

            for f in Path(proj_path).rglob("*"):
                if not f.is_file():
                    continue
                if f.suffix.lower() in LIBRARY_ST_EXTENSIONS:
                    stem = f.stem
                    if stem.startswith("FB_") or stem.startswith("FC_"):
                        key = stem
                        if key not in name_to_locations:
                            name_to_locations[key] = []
                        name_to_locations[key].append(f"{proj_name}/{f.relative_to(proj_path)}")

        conflicts = []
        for name, locations in name_to_locations.items():
            if len(locations) > 1:
                conflicts.append(NamingConflict(
                    name=name,
                    locations=locations,
                ))

        if conflicts:
            logger.info(f"检测到 {len(conflicts)} 个命名冲突")

        return conflicts

    @classmethod
    def check_workspace(
        cls, workspace_path: str, projects: List[Any]
    ) -> List[WorkspaceCheckItem]:
        """对工作空间内所有子项目执行统一检查

        检查项:
        1. 子项目目录是否存在
        2. 共享库孤立文件
        3. 跨项目命名冲突
        4. 项目配置完整性

        Args:
            workspace_path: 工作空间根目录路径
            projects: 子项目 Project 对象列表

        Returns:
            List[WorkspaceCheckItem]
        """
        items: List[WorkspaceCheckItem] = []

        for project in projects:
            proj_type = getattr(project, "project_type", ProjectType.GENERIC)
            proj_type_value = getattr(proj_type, "value", str(proj_type))
            proj_path = getattr(project, "path", "")
            proj_name = getattr(project, "name", "")

            if not proj_path or not os.path.exists(proj_path):
                items.append(WorkspaceCheckItem(
                    project_name=proj_name,
                    project_path=proj_path,
                    project_type=proj_type_value,
                    status="error",
                    message="项目目录不存在",
                    severity="error",
                ))
                continue

            items.append(WorkspaceCheckItem(
                project_name=proj_name,
                project_path=proj_path,
                project_type=proj_type_value,
                status="ok",
                message="项目目录存在",
                severity="info",
            ))

            if proj_type_value == ProjectType.PLC_LIBRARY.value:
                scan_result = LibraryService.scan_library(proj_path)
                if scan_result and scan_result.orphan_files:
                    items.append(WorkspaceCheckItem(
                        project_name=proj_name,
                        project_path=proj_path,
                        project_type=proj_type_value,
                        status="warning",
                        message=f"共享库存在 {len(scan_result.orphan_files)} 个孤立文件",
                        severity="warning",
                    ))

        conflicts = cls.detect_naming_conflicts(projects)
        for conflict in conflicts:
            items.append(WorkspaceCheckItem(
                project_name="*",
                project_path="",
                project_type="workspace",
                status="warning",
                message=f"命名冲突: {conflict.name} ({len(conflict.locations)}处)",
                severity="warning",
            ))

        logger.info(
            f"工作空间检查完成: {len(items)} 个检查项, "
            f"{sum(1 for i in items if i.severity == 'error')} 个错误, "
            f"{sum(1 for i in items if i.severity == 'warning')} 个警告"
        )
        return items

    @classmethod
    def get_workspace_statistics(
        cls, workspace_path: str, projects: List[Any]
    ) -> Dict:
        """获取工作空间汇总统计

        Args:
            workspace_path: 工作空间根目录路径
            projects: 子项目 Project 对象列表

        Returns:
            Dict: 统计信息
        """
        type_counts: Dict[str, int] = {}
        total_st = 0
        total_spec = 0

        for project in projects:
            proj_type = getattr(project, "project_type", ProjectType.GENERIC)
            proj_type_value = getattr(proj_type, "value", str(proj_type))
            proj_path = getattr(project, "path", "")

            type_counts[proj_type_value] = type_counts.get(proj_type_value, 0) + 1

            if proj_type_value == ProjectType.PLC_LIBRARY.value:
                lib_summary = LibraryService.get_library_summary(proj_path)
                if lib_summary:
                    total_st += lib_summary.get("total_st_files", 0)
                    total_spec += lib_summary.get("total_spec_files", 0)
            else:
                st_count, spec_count = cls._count_project_files(proj_path)
                total_st += st_count
                total_spec += spec_count

        conflicts = cls.detect_naming_conflicts(projects)

        return {
            "workspace_name": Path(workspace_path).name,
            "total_projects": len(projects),
            "project_type_distribution": type_counts,
            "total_st_files": total_st,
            "total_spec_files": total_spec,
            "naming_conflicts": len(conflicts),
            "has_issues": len(conflicts) > 0,
        }

    @classmethod
    def _count_project_files(cls, project_path: str) -> Tuple[int, int]:
        """统计项目目录下的ST文件和规范文件数量

        Args:
            project_path: 项目路径

        Returns:
            Tuple[int, int]: (ST文件数, 规范文件数)
        """
        st_count = 0
        spec_count = 0

        if not project_path or not os.path.exists(project_path):
            return 0, 0

        for f in Path(project_path).rglob("*"):
            if not f.is_file():
                continue
            ext = f.suffix.lower()
            if ext in LIBRARY_ST_EXTENSIONS:
                st_count += 1
            elif ext in {".md", ".yaml", ".yml", ".json"}:
                if f.name != ".plc.json" and f.name != "project.json":
                    spec_count += 1

        return st_count, spec_count
