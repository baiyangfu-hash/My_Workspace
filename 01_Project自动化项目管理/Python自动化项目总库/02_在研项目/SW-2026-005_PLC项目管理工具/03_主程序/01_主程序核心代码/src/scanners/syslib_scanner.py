# -*- coding: utf-8 -*-
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from src.utils.logger import setup_logger
from src.parsers.st_parser import STParser, POUType, VarCategory

logger = setup_logger(__name__)

_SYSLIB_RELATIVE_PATH = "0100_PLC自动化/01_SharedLibraries/SysLib"
_RE_VERSION = re.compile(r"V(\d+\.\d+\.\d+)")
_RE_HEADER_META = re.compile(
    r"(?:功能块名称|FUNCTION_BLOCK|FUNCTION)\s*:\s*(\w+)",
    re.IGNORECASE,
)
_RE_AUTHOR = re.compile(r"作者\s*[:：]\s*(.+)", re.IGNORECASE)
_RE_DESCRIPTION = re.compile(r"描述\s*[:：]\s*(.+)", re.IGNORECASE)
_RE_RETAIN_VAR = re.compile(
    r"VAR(?:_\w+)?\s+(RETAIN|PERSISTENT)",
    re.IGNORECASE,
)


@dataclass
class SCLFileInfo:
    file_path: str
    fb_name: str
    pou_type: str
    directory: str
    last_modified: str
    version: Optional[str] = None
    variable_count: int = 0


@dataclass
class GlobalFBIndex:
    syslib_root: str
    scan_time: datetime
    total_files: int
    fbs: Dict[str, SCLFileInfo] = field(default_factory=dict)
    fcs: Dict[str, SCLFileInfo] = field(default_factory=dict)

    def get_pou(self, name: str) -> Optional[SCLFileInfo]:
        key = name.lower()
        return self.fbs.get(key) or self.fcs.get(key)

    def all_pous(self) -> Dict[str, SCLFileInfo]:
        result = dict(self.fbs)
        result.update(self.fcs)
        return result


@dataclass
class LibraryRefIssue:
    project_file: str
    referenced_fb: str
    expected_version: Optional[str]
    actual_version: Optional[str]
    issue_type: str


class SysLibScanner:
    DEFAULT_SYSLIB_PATH: Optional[str] = None
    _index_cache: Optional[GlobalFBIndex] = None
    _cache_syslib_root: Optional[str] = None

    @classmethod
    def discover_syslib_root(cls, workspace_root: str) -> Optional[Path]:
        candidate = Path(workspace_root) / _SYSLIB_RELATIVE_PATH
        if candidate.is_dir():
            logger.info(f"自动发现SysLib根目录: {candidate}")
            return candidate
        logger.warning(f"SysLib目录不存在: {candidate}")
        return None

    @classmethod
    def scan_all_scl_files(cls, syslib_root: str) -> List[SCLFileInfo]:
        root = Path(syslib_root).resolve()
        if not root.is_dir():
            logger.error(f"SysLib根目录不存在: {root}")
            return []

        results: List[SCLFileInfo] = []
        scl_files = sorted(root.rglob("*.scl"))

        for scl_file in scl_files:
            try:
                info = cls._parse_scl_file(scl_file, root)
                if info:
                    results.append(info)
            except Exception as e:
                logger.warning(f"解析SCL文件失败 {scl_file.name}: {e}")

        logger.info(
            f"SysLib扫描完成: {root.name} - "
            f"共{len(results)}个SCL文件 "
            f"(FB:{sum(1 for r in results if r.pou_type == 'FUNCTION_BLOCK')}, "
            f"FC:{sum(1 for r in results if r.pou_type == 'FUNCTION')})"
        )
        return results

    @classmethod
    def _parse_scl_file(
        cls, scl_file: Path, syslib_root: Path
    ) -> Optional[SCLFileInfo]:
        try:
            source = scl_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            source = scl_file.read_text(encoding="gbk", errors="replace")

        version = cls.get_library_version(source)

        parser = STParser()
        pous, _globals = parser.parse(source)

        if not pous:
            return None

        pou = pous[0]
        relative_dir = scl_file.parent.relative_to(syslib_root)
        mtime = datetime.fromtimestamp(scl_file.stat().st_mtime)

        var_count = sum(len(p.variables) for p in pous) + len(_globals)

        return SCLFileInfo(
            file_path=str(scl_file),
            fb_name=pou.name,
            pou_type=pou.pou_type.value,
            directory=str(relative_dir),
            last_modified=mtime.isoformat(),
            version=version,
            variable_count=var_count,
        )

    @classmethod
    def build_global_fb_index(cls, syslib_root: str) -> GlobalFBIndex:
        if (
            cls._index_cache is not None
            and cls._cache_syslib_root == syslib_root
        ):
            logger.debug("使用缓存的GlobalFBIndex")
            return cls._index_cache

        start = datetime.now()
        all_files = cls.scan_all_scl_files(syslib_root)

        index = GlobalFBIndex(
            syslib_root=syslib_root,
            scan_time=start,
            total_files=len(all_files),
        )

        for finfo in all_files:
            key = finfo.fb_name.lower()
            if finfo.pou_type == "FUNCTION_BLOCK":
                index.fbs[key] = finfo
            elif finfo.pou_type == "FUNCTION":
                index.fcs[key] = finfo

        cls._index_cache = index
        cls._cache_syslib_root = syslib_root

        elapsed = (datetime.now() - start).total_seconds()
        logger.info(
            f"GlobalFBIndex构建完成: "
            f"{len(index.fbs)} FBs + {len(index.fcs)} FCs, "
            f"耗时 {elapsed:.2f}s"
        )
        return index

    @classmethod
    def invalidate_cache(cls) -> None:
        cls._index_cache = None
        cls._cache_syslib_root = None
        logger.debug("GlobalFBIndex缓存已清除")

    @classmethod
    def get_library_version(cls, source_code: str) -> Optional[str]:
        lines = source_code.splitlines()
        header_lines = []
        in_header = False

        for line in lines:
            stripped = line.strip()
            if stripped.startswith(("(*", "//", "{-")):
                in_header = True
            elif in_header:
                if stripped.endswith(("*)", "-}", "//")) or stripped.startswith(
                    ("FUNCTION", "PROGRAM", "TYPE", "VAR")
                ):
                    break
            if in_header:
                header_lines.append(stripped)

        header_text = "\n".join(header_lines)
        match = _RE_VERSION.search(header_text)
        if match:
            return f"V{match.group(1)}"

        first_block = source_code[:2000]
        match = _RE_VERSION.search(first_block)
        if match:
            return f"V{match.group(1)}"

        return None

    @classmethod
    def find_outdated_references(
        cls, project_path: str, syslib_index: GlobalFBIndex
    ) -> List[LibraryRefIssue]:
        issues: List[LibraryRefIssue] = []
        project_dir = Path(project_path)

        project_scl_files = list(project_dir.rglob("*.scl"))
        known_names = set(syslib_index.all_pous().keys())

        for scl_file in project_scl_files:
            try:
                source = scl_file.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                source = scl_file.read_text(encoding="gbk", errors="continue")

            parser = STParser()
            pous, _globals = parser.parse(source)

            for pou in pous:
                for var in pou.variables:
                    fb_ref = var.data_type.strip()
                    if fb_ref.lower() in known_names:
                        lib_info = syslib_index.get_pou(fb_ref)
                        if lib_info is None:
                            continue
                        file_version = cls.get_library_version(source)
                        if (
                            file_version
                            and lib_info.version
                            and file_version != lib_info.version
                        ):
                            issues.append(LibraryRefIssue(
                                project_file=str(scl_file),
                                referenced_fb=fb_ref,
                                expected_version=lib_info.version,
                                actual_version=file_version,
                                issue_type="version_mismatch",
                            ))

            ref_pattern = re.compile(r"\b(FB_\w+|FC_\w+)\b")
            for match in ref_pattern.finditer(source):
                ref_name = match.group(1)
                if ref_name.lower() in known_names:
                    lib_info = syslib_index.get_pou(ref_name)
                    if lib_info is None:
                        issues.append(LibraryRefIssue(
                            project_file=str(scl_file),
                            referenced_fb=ref_name,
                            expected_version=None,
                            actual_version=None,
                            issue_type="not_found",
                        ))

        unique_issues = []
        seen = set()
        for issue in issues:
            key = (issue.project_file, issue.referenced_fb, issue.issue_type)
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)

        logger.info(
            f"库引用检查完成: 发现{len(unique_issues)}个问题 "
            f"(项目路径: {project_path})"
        )
        return unique_issues

    @classmethod
    def extract_retain_vars(cls, source_code: str) -> List[Dict[str, str]]:
        results = []
        for match in _RE_RETAIN_VAR.finditer(source_code):
            retain_type = match.group(1).upper()
            pos = match.start()
            block_start = source_code.rfind("VAR", 0, pos)
            block_end = source_code.find("END_VAR", pos)
            if block_start == -1 or block_end == -1:
                continue
            var_block = source_code[block_start:block_end]
            var_decl_pattern = re.compile(
                r"([\w]+)\s*:\s*(\w+)",
                re.IGNORECASE,
            )
            for vm in var_decl_pattern.finditer(var_block):
                var_name = vm.group(1).strip()
                var_type = vm.group(2).strip()
                if var_name.upper() not in ("VAR", "END_VAR", "RETAIN",
                                            "PERSISTENT", "NON_RETAIN"):
                    results.append({
                        "name": var_name,
                        "data_type": var_type,
                        "retain_type": retain_type,
                    })
        return results
