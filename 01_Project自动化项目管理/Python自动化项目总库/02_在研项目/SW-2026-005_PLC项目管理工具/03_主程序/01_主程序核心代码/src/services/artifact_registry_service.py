# -*- coding: utf-8 -*-
"""
DJ单机项目资产注册服务

扫描项目目录，识别关键资产并忽略不参与治理的目录。
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from src.core.constants import (
    IGNORED_PROJECT_DIRS,
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
        """根据目录结构判断项目类型"""
        root = Path(project_path)
        markers = [root / marker for marker in cls.DJ_ROOT_MARKERS]
        if all(path.exists() for path in markers):
            return ProjectType.DJ_SINGLE_MACHINE
        return ProjectType.GENERIC

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
