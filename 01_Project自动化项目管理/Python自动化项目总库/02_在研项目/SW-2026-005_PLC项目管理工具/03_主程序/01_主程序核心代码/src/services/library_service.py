# -*- coding: utf-8 -*-
"""
共享库治理服务

负责共享库(PLC_LIBRARY)的资产扫描、分类、统计和规范目录识别。
共享库是工作空间中的可复用PLC组件集合, 典型结构:

  SysLib/
  ├── .plc.json
  ├── actuator/
  │   ├── FB_ValveControl.scl
  │   └── FB_CylinderControl.scl
  ├── timer/
  │   ├── FB_TON.scl
  │   └── FB_TONR.scl
  └── 00_通用规范/
      ├── LSP-905_SCL编程规范.md
      └── LSP-904_注释规范.md
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.core.constants import (
    IGNORED_PROJECT_DIRS,
    LIBRARY_SPEC_EXTENSIONS,
    LIBRARY_ST_EXTENSIONS,
    LibraryArtifactType,
    PLC_LIBRARY_CATEGORY_DIRS,
    SPEC_DIR_MARKERS,
)
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class LibraryArtifact:
    """共享库资产条目"""
    name: str
    artifact_type: LibraryArtifactType
    relative_path: str
    absolute_path: str
    category: str = ""
    file_count: int = 0
    spec_count: int = 0

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "artifact_type": self.artifact_type.value,
            "relative_path": self.relative_path,
            "absolute_path": self.absolute_path,
            "category": self.category,
            "file_count": self.file_count,
            "spec_count": self.spec_count,
        }


@dataclass
class LibraryScanResult:
    """共享库扫描结果"""
    library_path: str
    library_name: str
    total_artifacts: int = 0
    total_st_files: int = 0
    total_spec_files: int = 0
    categories: List[LibraryArtifact] = field(default_factory=list)
    spec_dirs: List[Dict] = field(default_factory=list)
    orphan_files: List[Dict] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "library_path": self.library_path,
            "library_name": self.library_name,
            "total_artifacts": self.total_artifacts,
            "total_st_files": self.total_st_files,
            "total_spec_files": self.total_spec_files,
            "categories": [a.to_dict() for a in self.categories],
            "spec_dirs": self.spec_dirs,
            "orphan_files": self.orphan_files,
        }


class LibraryService:
    """共享库治理服务

    职责:
    1. 扫描共享库目录, 识别分类子目录和规范目录
    2. 统计各分类下的ST源码文件和规范文件
    3. 识别孤立文件(不在分类目录中的源码/规范)
    4. 提供库资产汇总信息
    """

    @classmethod
    def scan_library(cls, library_path: str) -> Optional[LibraryScanResult]:
        """扫描共享库目录

        Args:
            library_path: 共享库根目录路径

        Returns:
            LibraryScanResult | None
        """
        root = Path(library_path)
        if not root.exists() or not root.is_dir():
            logger.warning(f"共享库目录不存在: {library_path}")
            return None

        result = LibraryScanResult(
            library_path=str(root),
            library_name=root.name,
        )

        for child in root.iterdir():
            if not child.is_dir():
                continue
            if child.name in IGNORED_PROJECT_DIRS:
                continue

            dir_name_lower = child.name.lower()

            if dir_name_lower in SPEC_DIR_MARKERS or child.name in SPEC_DIR_MARKERS:
                spec_info = cls._scan_spec_dir(child, root)
                result.spec_dirs.append(spec_info)
                result.total_spec_files += spec_info.get("file_count", 0)
                continue

            if dir_name_lower in PLC_LIBRARY_CATEGORY_DIRS:
                artifact = cls._scan_category_dir(child, root)
                result.categories.append(artifact)
                result.total_st_files += artifact.file_count
                result.total_spec_files += artifact.spec_count
                continue

            artifact = cls._scan_unknown_dir(child, root)
            if artifact.file_count > 0 or artifact.spec_count > 0:
                result.categories.append(artifact)
                result.total_st_files += artifact.file_count
                result.total_spec_files += artifact.spec_count

        orphan_files = cls._scan_orphan_files(root)
        result.orphan_files = orphan_files
        result.total_st_files += sum(
            1 for f in orphan_files
            if Path(f["path"]).suffix.lower() in LIBRARY_ST_EXTENSIONS
        )
        result.total_spec_files += sum(
            1 for f in orphan_files
            if Path(f["path"]).suffix.lower() in LIBRARY_SPEC_EXTENSIONS
        )
        result.total_artifacts = len(result.categories) + len(result.spec_dirs)

        logger.info(
            f"共享库扫描完成: {root.name}, "
            f"{result.total_artifacts}个分类, "
            f"{result.total_st_files}个ST文件, "
            f"{result.total_spec_files}个规范文件"
        )
        return result

    @classmethod
    def _scan_category_dir(
        cls, category_path: Path, library_root: Path
    ) -> LibraryArtifact:
        """扫描分类子目录"""
        st_count = 0
        spec_count = 0

        for f in category_path.rglob("*"):
            if not f.is_file():
                continue
            if f.suffix.lower() in LIBRARY_ST_EXTENSIONS:
                st_count += 1
            elif f.suffix.lower() in LIBRARY_SPEC_EXTENSIONS:
                spec_count += 1

        return LibraryArtifact(
            name=category_path.name,
            artifact_type=cls._infer_artifact_type(category_path.name),
            relative_path=str(category_path.relative_to(library_root)),
            absolute_path=str(category_path),
            category=category_path.name.lower(),
            file_count=st_count,
            spec_count=spec_count,
        )

    @classmethod
    def _scan_spec_dir(
        cls, spec_path: Path, library_root: Path
    ) -> Dict:
        """扫描规范目录"""
        files = []
        for f in spec_path.rglob("*"):
            if f.is_file() and f.suffix.lower() in LIBRARY_SPEC_EXTENSIONS:
                files.append({
                    "name": f.name,
                    "relative_path": str(f.relative_to(library_root)),
                })

        return {
            "name": spec_path.name,
            "relative_path": str(spec_path.relative_to(library_root)),
            "absolute_path": str(spec_path),
            "file_count": len(files),
            "files": files,
        }

    @classmethod
    def _scan_unknown_dir(
        cls, dir_path: Path, library_root: Path
    ) -> LibraryArtifact:
        """扫描非标准分类目录"""
        st_count = 0
        spec_count = 0

        for f in dir_path.rglob("*"):
            if not f.is_file():
                continue
            if f.suffix.lower() in LIBRARY_ST_EXTENSIONS:
                st_count += 1
            elif f.suffix.lower() in LIBRARY_SPEC_EXTENSIONS:
                spec_count += 1

        return LibraryArtifact(
            name=dir_path.name,
            artifact_type=LibraryArtifactType.DOC,
            relative_path=str(dir_path.relative_to(library_root)),
            absolute_path=str(dir_path),
            category=dir_path.name.lower(),
            file_count=st_count,
            spec_count=spec_count,
        )

    @classmethod
    def _scan_orphan_files(cls, library_root: Path) -> List[Dict]:
        """扫描根目录下的孤立文件"""
        orphans = []
        for f in library_root.iterdir():
            if f.is_file():
                ext = f.suffix.lower()
                if ext in LIBRARY_ST_EXTENSIONS or ext in LIBRARY_SPEC_EXTENSIONS:
                    orphans.append({
                        "name": f.name,
                        "path": str(f),
                        "type": "st" if ext in LIBRARY_ST_EXTENSIONS else "spec",
                    })
        return orphans

    @classmethod
    def _infer_artifact_type(cls, category_name: str) -> LibraryArtifactType:
        """根据分类目录名推断资产类型"""
        name_lower = category_name.lower()
        type_mapping = {
            "actuator": LibraryArtifactType.FB,
            "timer": LibraryArtifactType.FB,
            "counter": LibraryArtifactType.FB,
            "edge": LibraryArtifactType.FB,
            "convert": LibraryArtifactType.FC,
            "analog": LibraryArtifactType.FB,
            "motion": LibraryArtifactType.FB,
            "communication": LibraryArtifactType.FC,
            "safety": LibraryArtifactType.FB,
        }
        return type_mapping.get(name_lower, LibraryArtifactType.DOC)

    @classmethod
    def identify_spec_dirs(cls, library_path: str) -> List[Dict]:
        """识别共享库中的规范目录

        Args:
            library_path: 共享库根目录路径

        Returns:
            List[Dict]: 规范目录列表
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
    def get_library_summary(cls, library_path: str) -> Optional[Dict]:
        """获取共享库摘要信息

        Args:
            library_path: 共享库根目录路径

        Returns:
            Dict | None
        """
        result = cls.scan_library(library_path)
        if result is None:
            return None

        return {
            "library_name": result.library_name,
            "total_categories": result.total_artifacts,
            "total_st_files": result.total_st_files,
            "total_spec_files": result.total_spec_files,
            "category_names": [a.name for a in result.categories],
            "spec_dir_names": [d["name"] for d in result.spec_dirs],
            "has_orphan_files": len(result.orphan_files) > 0,
        }
