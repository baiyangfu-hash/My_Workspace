# -*- coding: utf-8 -*-
"""
版本差异检查器

对比 PLC 代码(.scl) 与 PRD 文档(IFC/DSN/CHG) 的版本号，
生成版本差距矩阵。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from src.sync.version_extractor import VersionExtractor
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class FbVersionGap:
    """单个FB/模块的版本差距"""
    fb_name: str = ""
    code_path: str = ""
    code_version: str = ""
    ifc_path: str = ""
    ifc_version: str = ""
    dsn_path: str = ""
    dsn_version: str = ""
    chg_path: str = ""
    chg_version: str = ""
    status: str = "-"

    @property
    def is_synced(self) -> bool:
        return self.status == "[OK]"

    @property
    def gap_desc(self) -> str:
        gaps = []
        if self.ifc_version and self.code_version:
            cmp = VersionExtractor.compare_versions(self.ifc_version, self.code_version)
            if cmp < 0:
                gaps.append(f"IFC滞后{self._version_diff(self.ifc_version, self.code_version)}")
        if self.dsn_version and self.code_version:
            cmp = VersionExtractor.compare_versions(self.dsn_version, self.code_version)
            if cmp < 0:
                gaps.append(f"DSN滞后{self._version_diff(self.dsn_version, self.code_version)}")
        if self.chg_version and self.code_version:
            cmp = VersionExtractor.compare_versions(self.chg_version, self.code_version)
            if cmp < 0:
                gaps.append(f"CHG滞后{self._version_diff(self.chg_version, self.code_version)}")
        return ", ".join(gaps) if gaps else ""

    @staticmethod
    def _version_diff(doc_v: str, code_v: str) -> str:
        dt = VersionExtractor.parse_version_tuple(doc_v)
        ct = VersionExtractor.parse_version_tuple(code_v)
        major_diff = ct[0] - dt[0]
        if major_diff > 0:
            return f"~{major_diff}个大版本"
        minor_diff = ct[1] - dt[1]
        if minor_diff > 0:
            return f"{minor_diff}个版本"
        return ""

    def _compute_status(self):
        if not self.code_version:
            self.status = "-"
            return
        checks = []
        if self.ifc_version:
            checks.append(VersionExtractor.compare_versions(self.ifc_version, self.code_version) >= 0)
        if self.dsn_version:
            checks.append(VersionExtractor.compare_versions(self.dsn_version, self.code_version) >= 0)
        if self.chg_version:
            checks.append(VersionExtractor.compare_versions(self.chg_version, self.code_version) >= 0)
        if not checks:
            self.status = "[?]"
        elif False in checks:
            self.status = "[X]"
        else:
            self.status = "[OK]"


@dataclass
class VersionGapReport:
    project_path: str = ""
    total_fbs: int = 0
    synced_count: int = 0
    lagging_count: int = 0
    unknown_count: int = 0
    fb_gaps: List[FbVersionGap] = field(default_factory=list)
    generated_at: str = ""


class VersionChecker:
    """版本差异检查器"""

    RE_FB_ID = re.compile(r'(FB_\d+|OB1|FB_External|GlobalVars)', re.IGNORECASE)

    @classmethod
    def check_project(cls, project_path: str) -> VersionGapReport:
        p = Path(project_path)
        if not p.exists():
            logger.error(f"项目路径不存在: {project_path}")
            return VersionGapReport(project_path=project_path, generated_at=cls._now())

        scl_files = cls._find_scl_files(p)
        prd_files = cls._find_prd_files(p)

        if not scl_files:
            logger.warning(f"未找到 .scl 文件: {project_path}")
            return VersionGapReport(project_path=project_path, generated_at=cls._now())

        fb_gaps = []
        for scl_path in scl_files:
            gap = cls._build_gap(scl_path, prd_files)
            gap._compute_status()
            fb_gaps.append(gap)

        fb_gaps.sort(key=lambda g: g.fb_name)

        synced = sum(1 for g in fb_gaps if g.is_synced)
        lagging = sum(1 for g in fb_gaps if g.status == "[X]")
        unknown = sum(1 for g in fb_gaps if g.status in ("[?]", "-"))

        return VersionGapReport(
            project_path=project_path,
            total_fbs=len(fb_gaps),
            synced_count=synced,
            lagging_count=lagging,
            unknown_count=unknown,
            fb_gaps=fb_gaps,
            generated_at=cls._now(),
        )

    @classmethod
    def check_fb(cls, project_path: str, fb_name: str) -> FbVersionGap:
        p = Path(project_path)
        scl_files = [f for f in cls._find_scl_files(p) if fb_name.lower() in f.name.lower()]
        prd_files = cls._find_prd_files(p)

        if not scl_files:
            return FbVersionGap(fb_name=fb_name, status="-")

        gap = cls._build_gap(scl_files[0], prd_files)
        gap._compute_status()
        return gap

    @classmethod
    def _build_gap(cls, scl_path: Path, prd_files: List[Path]) -> FbVersionGap:
        fb_id = cls._extract_fb_id(scl_path.name)
        fb_name = scl_path.stem

        code_version = VersionExtractor.extract_scl_version(str(scl_path)) or ""

        ifc_path, ifc_version = cls._match_prd(prd_files, fb_id, "IFC", scl_path.parent)
        dsn_path, dsn_version = cls._match_prd(prd_files, fb_id, "DSN", scl_path.parent)
        chg_path, chg_version = cls._match_prd(prd_files, fb_id, "CHG", scl_path.parent)

        return FbVersionGap(
            fb_name=fb_name,
            code_path=str(scl_path),
            code_version=code_version,
            ifc_path=str(ifc_path) if ifc_path else "",
            ifc_version=ifc_version,
            dsn_path=str(dsn_path) if dsn_path else "",
            dsn_version=dsn_version,
            chg_path=str(chg_path) if chg_path else "",
            chg_version=chg_version,
        )

    @classmethod
    def _match_prd(cls, prd_files: List[Path], fb_id: str, doc_type: str,
                   scl_parent: Path) -> tuple:
        """
        为指定 FB 匹配对应文档类型的 PRD 文件
        fb_id: "FB_1003", "OB1", "FB_External", "GlobalVars"
        doc_type: "IFC", "DSN", "CHG"

        匹配优先级:
        1. 与 .scl 同目录的 PRD 子目录中有匹配文档
        2. 全局其他 PRD 目录中有匹配文档
        返回值: (Path|None, version_str|"")
        """
        candidates = []
        for f in prd_files:
            name_upper = f.name.upper()
            if doc_type not in name_upper:
                continue
            if cls._is_prd_match(name_upper, fb_id):
                candidates.append(f)

        if not candidates:
            return None, ""

        # 优先同父目录
        if scl_parent:
            local = [c for c in candidates if scl_parent in c.parents]
            if local:
                candidates = local

        # 排除 archive 目录
        active = [c for c in candidates if "archive" not in str(c).lower()]
        if active:
            candidates = active

        best = candidates[0]
        version = VersionExtractor.extract_prd_version(str(best)) or ""
        return best, version

    @classmethod
    def _is_prd_match(cls, name_upper: str, fb_id: str) -> bool:
        """判断 PRD 文件名是否匹配指定 FB"""
        fb_id_lower = fb_id.lower()
        name_lower = name_upper.lower()

        if fb_id_lower in name_lower:
            return True

        fb_id_no_underscore = fb_id_lower.replace("_", "")
        if fb_id_no_underscore in name_lower:
            return True

        special_map = {
            "FB_EXTERNAL": ["FB3001", "EXTERNAL"],
            "GLOBALVARS": ["GLOBALVARS", "DB1"],
        }

        fb_key = fb_id.upper().replace("_", "")
        for key, aliases in special_map.items():
            if fb_id.upper() == key or fb_key == key:
                for alias in aliases:
                    if alias.lower() in name_lower:
                        return True
        return False

    @classmethod
    def _extract_fb_id(cls, filename: str) -> str:
        """
        从文件名提取 FB 标识符
        "FB_1003_PickPlace_BufferFraming.scl" → "FB_1003"
        "OB1.scl" → "OB1"
        "FB_ExternalDeviceInteraction.scl" → "FB_External"
        "GlobalVars.db" → "GlobalVars"
        """
        m = cls.RE_FB_ID.search(filename)
        if m:
            return m.group(1)
        return filename.rsplit(".", 1)[0]

    @classmethod
    def _find_scl_files(cls, project_root: Path) -> List[Path]:
        """查找所有 .scl 和 .db 源文件（排除 archive）"""
        files = []
        for ext in ("*.scl", "*.db"):
            for f in project_root.rglob(ext):
                if "archive" not in str(f).lower() and ".trae" not in f.parts:
                    files.append(f)
        return sorted(files)

    @classmethod
    def _find_prd_files(cls, project_root: Path) -> List[Path]:
        """查找所有 PRD 文档（IFC/DSN/CHG .md 文件，排除 archive）"""
        files = []
        for f in project_root.rglob("*.md"):
            if any(p in f.parts for p in (".trae", "archive")):
                continue
            name_upper = f.name.upper()
            if any(tag in name_upper for tag in ("IFC", "DSN", "CHG")):
                files.append(f)
        return files

    @classmethod
    def format_report(cls, report: VersionGapReport) -> str:
        lines = []
        lines.append("")
        lines.append("| 模块                     | 代码(.scl)版本 | IFC接口文档 | DSN详细设计 | CHG变更记录 | 状态 |")
        lines.append("| ------------------------ | :----------: | :-------: | :------: | :-------: | :--: |")

        for gap in report.fb_gaps:
            cv = gap.code_version or "-"
            iv = gap.ifc_version or "-"
            dv = gap.dsn_version or "-"
            cv_ = gap.chg_version or "-"
            lines.append(
                f"| **{gap.fb_name}** | **{cv}** | {iv} | {dv} | {cv_} | {gap.status} |"
            )

        lines.append("")
        lines.append(f"> 总计: {report.total_fbs} 个模块 | [OK]已同步: {report.synced_count} | "
                      f"[X]滞后: {report.lagging_count} | [?]无法判断: {report.unknown_count}")
        lines.append(f"> 生成时间: {report.generated_at}")
        return "\n".join(lines)

    @staticmethod
    def _now() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M")