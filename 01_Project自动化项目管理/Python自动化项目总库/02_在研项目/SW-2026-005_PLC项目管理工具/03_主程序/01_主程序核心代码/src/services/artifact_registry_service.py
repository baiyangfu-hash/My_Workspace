# -*- coding: utf-8 -*-
"""
项目资产注册服务

扫描项目目录，识别关键资产并忽略不参与治理的目录。
支持工作空间、共享库、DJ单机项目等多种项目类型的识别。
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from src.core.constants import (
    IGNORED_PROJECT_DIRS,
    PLC_LIBRARY_CATEGORY_DIRS,
    SPEC_DIR_MARKERS,
    WORKSPACE_IGNORED_DIRS,
    ProjectArtifactType,
    ProjectType,
)
from src.models.project_artifact import ProjectArtifact
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ArtifactRegistryService:
    """项目资产扫描与分类服务"""

    DJ_ROOT_MARKERS = [
        "00_项目管理",
        "02_PLC程序",
        "03_HMI设计",
    ]

    @classmethod
    def detect_project_type(cls, project_path: str) -> ProjectType:
        """根据目录结构判断项目类型

        识别优先级:
        1. workspace.json 显式标记 -> PLC_WORKSPACE
        2. DJ 三标记 -> DJ_SINGLE_MACHINE
        3. .plc.json + 共享库分类子目录 -> PLC_LIBRARY
        4. >=2 个可识别子项目 -> PLC_WORKSPACE
        5. 其他 -> GENERIC
        """
        root = Path(project_path)
        if not root.exists() or not root.is_dir():
            return ProjectType.GENERIC

        if (root / "workspace.json").exists():
            logger.debug(f"识别为 PLC_WORKSPACE (workspace.json): {project_path}")
            return ProjectType.PLC_WORKSPACE

        markers = [root / marker for marker in cls.DJ_ROOT_MARKERS]
        if all(path.exists() for path in markers):
            logger.debug(f"识别为 DJ_SINGLE_MACHINE (三标记): {project_path}")
            return ProjectType.DJ_SINGLE_MACHINE

        if cls._is_plc_library(root):
            logger.debug(f"识别为 PLC_LIBRARY (.plc.json+分类目录): {project_path}")
            return ProjectType.PLC_LIBRARY

        identifiable_count = cls._count_identifiable_subprojects(root)
        if identifiable_count >= 2:
            logger.debug(
                f"识别为 PLC_WORKSPACE ({identifiable_count}个子项目): {project_path}"
            )
            return ProjectType.PLC_WORKSPACE

        return ProjectType.GENERIC

    @classmethod
    def _is_plc_library(cls, root: Path) -> bool:
        """判定是否为PLC共享库目录

        条件: 存在 .plc.json 且包含共享库典型分类子目录
        """
        if not (root / ".plc.json").exists():
            return False

        child_names = set()
        for child in root.iterdir():
            if child.is_dir() and child.name.lower() not in WORKSPACE_IGNORED_DIRS:
                child_names.add(child.name.lower())

        category_overlap = child_names & PLC_LIBRARY_CATEGORY_DIRS
        return len(category_overlap) > 0

    @classmethod
    def _count_identifiable_subprojects(cls, root: Path) -> int:
        """统计工作空间根目录下可识别的子项目数量

        可识别子项目:
        - DJ 单机项目 (三标记)
        - 共享库 (.plc.json + 分类目录)
        - 含 project.json/.plc_project.json/.plc.json 的普通项目
        """
        count = 0
        for child in root.iterdir():
            if not child.is_dir():
                continue
            if child.name in WORKSPACE_IGNORED_DIRS:
                continue

            if cls._is_dj_project(child):
                count += 1
            elif cls._is_plc_library(child):
                count += 1
            elif cls._has_project_config(child):
                count += 1

        return count

    @classmethod
    def _is_dj_project(cls, path: Path) -> bool:
        """判定目录是否为DJ单机项目"""
        markers = [path / marker for marker in cls.DJ_ROOT_MARKERS]
        return all(m.exists() for m in markers)

    @classmethod
    def _has_project_config(cls, path: Path) -> bool:
        """判定目录是否包含项目配置文件"""
        config_files = {"project.json", ".plc_project.json", ".plc.json"}
        return any((path / f).exists() for f in config_files)

    @classmethod
    def scan_workspace_subprojects(cls, workspace_path: str) -> List[Dict[str, str]]:
        """扫描工作空间根目录下的可识别子项目

        Returns:
            List[Dict]: 每项包含 path, name, type 三个字段
        """
        root = Path(workspace_path)
        if not root.exists() or not root.is_dir():
            return []

        subprojects: List[Dict[str, str]] = []
        for child in root.iterdir():
            if not child.is_dir():
                continue
            if child.name in WORKSPACE_IGNORED_DIRS:
                continue

            sub_type = cls._classify_subproject(child)
            if sub_type is not None:
                subprojects.append({
                    "path": str(child),
                    "name": child.name,
                    "type": sub_type,
                })

        logger.info(
            f"工作空间子项目扫描完成: {root.name}, 识别 {len(subprojects)} 个子项目"
        )
        return subprojects

    @classmethod
    def _classify_subproject(cls, path: Path) -> Optional[str]:
        """对单个子目录进行分类

        Returns:
            "dj_single_machine" | "plc_library" | "generic" | None
        """
        if cls._is_dj_project(path):
            return ProjectType.DJ_SINGLE_MACHINE.value
        if cls._is_plc_library(path):
            return ProjectType.PLC_LIBRARY.value
        if cls._has_project_config(path):
            return ProjectType.GENERIC.value
        return None

    @classmethod
    def scan_library_artifacts(cls, library_path: str) -> List[Dict]:
        """扫描共享库的资产目录结构

        Args:
            library_path: 共享库根目录路径

        Returns:
            List[Dict]: 每项包含 name, path, type, is_spec_dir 字段
        """
        root = Path(library_path)
        if not root.exists() or not root.is_dir():
            return []

        artifacts: List[Dict] = []
        for child in root.iterdir():
            if not child.is_dir():
                continue
            if child.name in IGNORED_PROJECT_DIRS:
                continue

            dir_name_lower = child.name.lower()
            is_spec_dir = (
                dir_name_lower in SPEC_DIR_MARKERS
                or child.name in SPEC_DIR_MARKERS
            )

            if is_spec_dir:
                artifacts.append({
                    "name": child.name,
                    "path": str(child),
                    "type": "spec_dir",
                    "is_spec_dir": True,
                })
            elif dir_name_lower in PLC_LIBRARY_CATEGORY_DIRS:
                artifacts.append({
                    "name": child.name,
                    "path": str(child),
                    "type": dir_name_lower,
                    "is_spec_dir": False,
                })
            else:
                artifacts.append({
                    "name": child.name,
                    "path": str(child),
                    "type": "other",
                    "is_spec_dir": False,
                })

        return artifacts

    @classmethod
    def identify_spec_dirs_in_library(cls, library_path: str) -> List[Dict]:
        """识别共享库中的规范目录

        Args:
            library_path: 共享库根目录路径

        Returns:
            List[Dict]: 规范目录列表, 每项含 name, path, relative_path
        """
        root = Path(library_path)
        if not root.exists() or not root.is_dir():
            return []

        spec_dirs = []
        for child in root.iterdir():
            if not child.is_dir():
                continue
            if child.name in IGNORED_PROJECT_DIRS:
                continue

            dir_name_lower = child.name.lower()
            if dir_name_lower in SPEC_DIR_MARKERS or child.name in SPEC_DIR_MARKERS:
                spec_dirs.append({
                    "name": child.name,
                    "path": str(child),
                    "relative_path": str(child.relative_to(root)),
                })

        return spec_dirs

    @classmethod
    def scan_project_assets(cls, project_path: str) -> List[ProjectArtifact]:
        """扫描项目资产"""
        root = Path(project_path).resolve()
        if not root.exists():
            return []

        assets: List[ProjectArtifact] = [
            cls._build_artifact(
                root,
                root,
                ProjectArtifactType.ROOT,
                category="project",
                is_dir=True,
            )
        ]

        for current in root.rglob("*"):
            if cls._should_ignore(current):
                continue
            asset = cls._classify_path(root, current)
            if asset is not None:
                assets.append(asset)

        logger.info(f"项目资产扫描完成: {root.name}, 共识别 {len(assets)} 项")
        return assets

    @classmethod
    def summarize_assets(cls, assets: List[ProjectArtifact]) -> Dict[str, int]:
        """汇总资产数量"""
        summary: Dict[str, int] = {}
        for asset in assets:
            summary[asset.artifact_type] = summary.get(asset.artifact_type, 0) + 1
        return summary

    @classmethod
    def get_artifact_roots(cls, assets: List[ProjectArtifact]) -> List[Dict[str, str]]:
        """提取核心根目录资产"""
        root_types = {
            ProjectArtifactType.ROOT.value,
            ProjectArtifactType.CHANGE_ROOT.value,
            ProjectArtifactType.PLC_ROOT.value,
            ProjectArtifactType.HMI_SOURCE.value,
            ProjectArtifactType.DEBUG_DOC.value,
            ProjectArtifactType.DELIVERY.value,
            ProjectArtifactType.KNOWLEDGE.value,
        }
        return [
            {
                "artifact_type": asset.artifact_type,
                "name": asset.name,
                "relative_path": asset.relative_path,
            }
            for asset in assets
            if asset.is_dir and asset.artifact_type in root_types
        ]

    @classmethod
    def _should_ignore(cls, path: Path) -> bool:
        """判断是否应忽略路径"""
        return any(part in IGNORED_PROJECT_DIRS for part in path.parts)

    @classmethod
    def _classify_path(
        cls, root: Path, current: Path
    ) -> Optional[ProjectArtifact]:
        """识别路径类型"""
        if current.is_dir():
            dir_name = current.name
            if current == root / "00_项目管理" / "04_变更管理":
                return cls._build_artifact(
                    root,
                    current,
                    ProjectArtifactType.CHANGE_ROOT,
                    category="change",
                    is_dir=True,
                )
            if current == root / "02_PLC程序" / "通用ST程序及变量表":
                return cls._build_artifact(
                    root,
                    current,
                    ProjectArtifactType.PLC_ROOT,
                    category="plc",
                    is_dir=True,
                )
            if current == root / "03_HMI设计":
                return cls._build_artifact(
                    root,
                    current,
                    ProjectArtifactType.HMI_SOURCE,
                    category="hmi",
                    is_dir=True,
                )
            if current == root / "04_现场调试":
                return cls._build_artifact(
                    root,
                    current,
                    ProjectArtifactType.DEBUG_DOC,
                    category="debug",
                    is_dir=True,
                )
            if current == root / "06_文档与交付":
                return cls._build_artifact(
                    root,
                    current,
                    ProjectArtifactType.DELIVERY,
                    category="delivery",
                    is_dir=True,
                )
            if current == root / "10_知识库":
                return cls._build_artifact(
                    root,
                    current,
                    ProjectArtifactType.KNOWLEDGE,
                    category="knowledge",
                    is_dir=True,
                )
            return None

        suffix = current.suffix.lower()
        name = current.name
        relative_str = cls._relative_path(root, current)

        if name == ".plc.json":
            return cls._build_artifact(
                root,
                current,
                ProjectArtifactType.PLC_CONFIG,
                category="plc",
                metadata={"scope": "root" if current.parent == root else "subproject"},
            )
        if suffix in {".scl", ".st"}:
            artifact_type = (
                ProjectArtifactType.PLC_DB
                if current.suffix.lower() == ".db"
                else ProjectArtifactType.PLC_SOURCE
            )
            return cls._build_artifact(
                root, current, artifact_type, category="plc"
            )
        if suffix == ".db":
            return cls._build_artifact(
                root, current, ProjectArtifactType.PLC_DB, category="plc"
            )
        if suffix == ".scltest":
            return cls._build_artifact(
                root, current, ProjectArtifactType.PLC_TEST, category="test"
            )
        if suffix == ".md":
            artifact_type = cls._classify_markdown(relative_str, name)
            return cls._build_artifact(
                root, current, artifact_type, category="document"
            )

        return None

    @classmethod
    def _classify_markdown(
        cls, relative_path: str, file_name: str
    ) -> ProjectArtifactType:
        """识别Markdown文档类型"""
        upper_name = file_name.upper()
        if "CHG-" in upper_name or "变更" in file_name:
            if "CHG-" in upper_name:
                return ProjectArtifactType.CHANGE_ORDER
            return ProjectArtifactType.DOC_CHG
        if "REQ" in upper_name or "需求" in file_name:
            return ProjectArtifactType.DOC_REQ
        if "DSN" in upper_name or "设计" in file_name:
            return ProjectArtifactType.DOC_DSN
        if "IFC" in upper_name or "接口" in file_name:
            return ProjectArtifactType.DOC_IFC
        if "UM" in upper_name or "手册" in file_name:
            return ProjectArtifactType.DOC_UM
        if "ALM" in upper_name or "报警" in file_name:
            return ProjectArtifactType.DOC_ALM
        if "IO" in upper_name or "IO分配" in file_name:
            return ProjectArtifactType.DOC_IO
        if "VAR" in upper_name or "变量" in file_name:
            return ProjectArtifactType.DOC_VAR
        if "ARC" in upper_name or "架构" in file_name:
            return ProjectArtifactType.DOC_ARC
        if "HMI" in upper_name:
            return ProjectArtifactType.DOC_HMI
        if relative_path.startswith("06_文档与交付"):
            return ProjectArtifactType.DOC_DELIVERY
        return ProjectArtifactType.DOC_MISC

    @classmethod
    def _build_artifact(
        cls,
        root: Path,
        current: Path,
        artifact_type: ProjectArtifactType,
        category: str = "",
        is_dir: bool = False,
        metadata: Optional[Dict[str, object]] = None,
    ) -> ProjectArtifact:
        """构造资产对象"""
        relative_path = cls._relative_path(root, current)
        artifact_id = relative_path.replace("\\", "/") or current.name
        return ProjectArtifact(
            artifact_id=artifact_id,
            artifact_type=artifact_type.value,
            name=current.name,
            relative_path=relative_path,
            absolute_path=str(current),
            category=category,
            exists=current.exists(),
            is_dir=is_dir,
            metadata=metadata or {},
        )

    @staticmethod
    def _relative_path(root: Path, current: Path) -> str:
        """获取相对路径字符串"""
        try:
            return str(current.relative_to(root))
        except ValueError:
            return str(current)
