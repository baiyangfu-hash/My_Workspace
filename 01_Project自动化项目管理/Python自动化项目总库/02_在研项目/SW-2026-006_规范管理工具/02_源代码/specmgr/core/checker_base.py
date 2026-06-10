from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import Optional

from .config import WorkspaceConfig
from .registry import SpecRegistry
from .scanner import SpecScanner


class Severity(IntEnum):
    INFO = 1
    WARNING = 2
    ERROR = 3


@dataclass
class CheckResult:
    check_id: str
    severity: Severity
    message: str
    details: str = ""
    fix_suggestion: str = ""


class BaseChecker(ABC):
    @abstractmethod
    def check(
        self,
        registry: SpecRegistry,
        scanner: SpecScanner,
    ) -> list[CheckResult]:
        ...


class DuplicateChecker(BaseChecker):
    def check(
        self,
        registry: SpecRegistry,
        scanner: SpecScanner,
    ) -> list[CheckResult]:
        results: list[CheckResult] = []
        duplicates = scanner.find_duplicates()
        for spec_num, paths in duplicates.items():
            path_list = ", ".join(str(p) for p in paths)
            results.append(
                CheckResult(
                    check_id="SHC-001",
                    severity=Severity.ERROR,
                    message=f"规范 {spec_num} 存在重复文件",
                    details=f"文件列表: {path_list}",
                    fix_suggestion="保留一个主文件，将其余文件移至归档目录并更新注册表",
                )
            )
        return results


class VersionMismatchChecker(BaseChecker):
    @staticmethod
    def _normalize_version(v: str) -> str:
        return v.lstrip("Vv")

    def check(
        self,
        registry: SpecRegistry,
        scanner: SpecScanner,
    ) -> list[CheckResult]:
        results: list[CheckResult] = []
        all_specs = scanner.scan_all()
        for spec_num, paths in all_specs.items():
            spec_info = registry.get_spec(spec_num)
            if not spec_info:
                continue
            for path in paths:
                fm = scanner.extract_frontmatter(path)
                if fm and isinstance(fm, dict):
                    file_version = fm.get("version")
                else:
                    file_version = scanner.extract_version(path)
                if file_version and spec_info.version:
                    norm_file = self._normalize_version(file_version)
                    norm_reg = self._normalize_version(spec_info.version)
                    if norm_file != norm_reg:
                        results.append(
                            CheckResult(
                                check_id="SHC-002",
                                severity=Severity.WARNING,
                                message=f"规范 {spec_num} 版本不一致",
                                details=f"注册表版本: {spec_info.version}, 文件版本: {file_version}, 文件: {path}",
                                fix_suggestion="更新注册表中的版本号或更新文件frontmatter中的version字段使其一致",
                            )
                        )
        return results


class DeprecatedRefChecker(BaseChecker):
    _ACTIVE_REF_PATTERNS = re.compile(
        r"(遵循|参照|引用|参考|依据|按照|遵守)\s*[:：]?\s*.*?"
    )
    _DEPRECATED_CONTEXT_PATTERNS = re.compile(
        r"(已废弃|替代|deprecated|取代|替换为|替代为)"
    )
    _SPEC_ID_RE = re.compile(r"(?:SW|PM|PLC|PY|CODE|LSP|INT)-\d{3,4}(?:-\d{3})?")

    def check(
        self,
        registry: SpecRegistry,
        scanner: SpecScanner,
    ) -> list[CheckResult]:
        results: list[CheckResult] = []
        deprecated_ids = {s.spec_id for s in registry.get_deprecated()}
        if not deprecated_ids:
            return results

        all_specs = scanner.scan_all()
        for spec_num, paths in all_specs.items():
            for path in paths:
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                except (OSError, UnicodeDecodeError):
                    continue

                for line_no, line in enumerate(content.splitlines(), 1):
                    refs = self._SPEC_ID_RE.findall(line)
                    if not refs:
                        continue
                    if not self._ACTIVE_REF_PATTERNS.search(line):
                        continue
                    if self._DEPRECATED_CONTEXT_PATTERNS.search(line):
                        continue
                    for ref_id in refs:
                        if ref_id in deprecated_ids:
                            results.append(
                                CheckResult(
                                    check_id="SHC-003",
                                    severity=Severity.WARNING,
                                    message=f"规范 {spec_num} 主动引用了已废弃规范 {ref_id}",
                                    details=f"文件: {path}, 第{line_no}行: {line.strip()}",
                                    fix_suggestion=f"将引用更新为 {ref_id} 的替代规范",
                                )
                            )
        return results


class IndexLinkChecker(BaseChecker):
    _MDLINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
    _SPEC_ID_RE = re.compile(r"(?:SW|PM|PLC|PY|CODE|LSP|INT)-\d{3,4}(?:-\d{3})?")

    def check(
        self,
        registry: SpecRegistry,
        scanner: SpecScanner,
    ) -> list[CheckResult]:
        results: list[CheckResult] = []
        for output_key, output_path in scanner.config.full_output_paths.items():
            if not output_path.exists():
                continue
            try:
                with open(output_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except (OSError, UnicodeDecodeError):
                continue

            for line_no, line in enumerate(content.splitlines(), 1):
                for match in self._MDLINK_RE.finditer(line):
                    link_text = match.group(1)
                    link_target = match.group(2)
                    spec_match = self._SPEC_ID_RE.search(link_text)
                    if not spec_match:
                        continue
                    spec_id = spec_match.group(0)
                    target_path = output_path.parent / link_target
                    if not target_path.exists():
                        results.append(
                            CheckResult(
                                check_id="SHC-004",
                                severity=Severity.ERROR,
                                message=f"索引文件中列出的规范文件不存在: {spec_id}",
                                details=f"索引文件: {output_path}, 第{line_no}行, 链接目标: {link_target}",
                                fix_suggestion=f"检查文件 {link_target} 是否存在，或更新索引中的链接",
                            )
                        )
        return results


class UnlistedSpecChecker(BaseChecker):
    def check(
        self,
        registry: SpecRegistry,
        scanner: SpecScanner,
    ) -> list[CheckResult]:
        results: list[CheckResult] = []
        all_specs = scanner.scan_all()
        for spec_num, paths in all_specs.items():
            spec_info = registry.get_spec(spec_num)
            if not spec_info:
                results.append(
                    CheckResult(
                        check_id="SHC-005",
                        severity=Severity.WARNING,
                        message=f"规范 {spec_num} 未在注册表中登记",
                        details=f"文件: {paths[0]}",
                        fix_suggestion=f"将规范 {spec_num} 添加到注册表",
                    )
                )
        return results


class ObsidianLinkChecker(BaseChecker):
    _WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")
    _MDLINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
    _SPEC_ID_RE = re.compile(r"(?:SW|PM|PLC|PY|CODE|LSP|INT)-\d{3,4}(?:-\d{3})?")

    def check(
        self,
        registry: SpecRegistry,
        scanner: SpecScanner,
    ) -> list[CheckResult]:
        results: list[CheckResult] = []
        all_specs = scanner.scan_all()
        for spec_num, paths in all_specs.items():
            for path in paths:
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                except (OSError, UnicodeDecodeError):
                    continue

                in_code_block = False
                in_frontmatter = False
                fm_line_count = 0

                for line_no, line in enumerate(lines, 1):
                    stripped = line.strip()

                    if line_no == 1 and stripped == "---":
                        in_frontmatter = True
                        fm_line_count = 1
                        continue
                    if in_frontmatter:
                        if stripped == "---" and fm_line_count > 0:
                            in_frontmatter = False
                        fm_line_count += 1
                        continue

                    if stripped.startswith("```"):
                        in_code_block = not in_code_block
                        continue
                    if in_code_block:
                        continue

                    for match in self._WIKILINK_RE.finditer(line):
                        target = match.group(1)
                        spec_match = self._SPEC_ID_RE.search(target)
                        if spec_match:
                            ref_id = spec_match.group(0)
                            target_path = self._resolve_wikilink(path, target, scanner)
                            if target_path and not target_path.exists():
                                results.append(
                                    CheckResult(
                                        check_id="SHC-006",
                                        severity=Severity.WARNING,
                                        message=f"规范 {spec_num} 的Obsidian链接指向不存在的文件: {ref_id}",
                                        details=f"文件: {path}, 第{line_no}行, 链接: [[{target}]]",
                                        fix_suggestion=f"检查链接目标文件是否存在，或更新链接",
                                    )
                                )
                            else:
                                spec_info = registry.get_spec(ref_id)
                                if spec_info and spec_info.lifecycle == "deprecated":
                                    results.append(
                                        CheckResult(
                                            check_id="SHC-006",
                                            severity=Severity.WARNING,
                                            message=f"规范 {spec_num} 链接了已废弃规范 {ref_id}",
                                            details=f"文件: {path}, 第{line_no}行, 链接: [[{target}]]",
                                            fix_suggestion=f"更新链接指向 {ref_id} 的替代规范",
                                        )
                                    )

                    for match in self._MDLINK_RE.finditer(line):
                        link_text = match.group(1)
                        link_target = match.group(2)
                        spec_match = self._SPEC_ID_RE.search(link_text) or self._SPEC_ID_RE.search(
                            link_target
                        )
                        if spec_match:
                            ref_id = spec_match.group(0)
                            target_path = path.parent / link_target
                            if not target_path.exists():
                                results.append(
                                    CheckResult(
                                        check_id="SHC-006",
                                        severity=Severity.WARNING,
                                        message=f"规范 {spec_num} 的Markdown链接指向不存在的文件: {ref_id}",
                                        details=f"文件: {path}, 第{line_no}行, 链接: [{link_text}]({link_target})",
                                        fix_suggestion=f"检查链接目标文件是否存在，或更新链接",
                                    )
                                )
                            else:
                                spec_info = registry.get_spec(ref_id)
                                if spec_info and spec_info.lifecycle == "deprecated":
                                    results.append(
                                        CheckResult(
                                            check_id="SHC-006",
                                            severity=Severity.WARNING,
                                            message=f"规范 {spec_num} 链接了已废弃规范 {ref_id}",
                                            details=f"文件: {path}, 第{line_no}行, 链接: [{link_text}]({link_target})",
                                            fix_suggestion=f"更新链接指向 {ref_id} 的替代规范",
                                        )
                                    )
        return results

    def _resolve_wikilink(
        self,
        source_file: Path,
        target: str,
        scanner: SpecScanner,
    ) -> Path | None:
        for spec_dir in scanner.config.full_spec_dirs:
            candidate = spec_dir / f"{target}.md"
            if candidate.exists():
                return candidate
        candidate = source_file.parent / f"{target}.md"
        return candidate


class FrontmatterChecker(BaseChecker):
    _REQUIRED_FIELDS = ["spec_id", "title", "version", "lifecycle"]

    def check(
        self,
        registry: SpecRegistry,
        scanner: SpecScanner,
    ) -> list[CheckResult]:
        results: list[CheckResult] = []
        all_specs = scanner.scan_all()
        for spec_num, paths in all_specs.items():
            for path in paths:
                fm = scanner.extract_frontmatter(path)
                if fm is None:
                    results.append(
                        CheckResult(
                            check_id="SHC-007",
                            severity=Severity.INFO,
                            message=f"规范 {spec_num} 缺少frontmatter",
                            details=f"文件: {path}",
                            fix_suggestion="添加包含spec_id、title、version、lifecycle的YAML frontmatter",
                        )
                    )
                    continue
                if not isinstance(fm, dict):
                    continue
                missing = [f for f in self._REQUIRED_FIELDS if f not in fm or not fm[f]]
                if missing:
                    results.append(
                        CheckResult(
                            check_id="SHC-007",
                            severity=Severity.INFO,
                            message=f"规范 {spec_num} frontmatter缺少必填字段",
                            details=f"文件: {path}, 缺少字段: {', '.join(missing)}",
                            fix_suggestion=f"补充缺失字段: {', '.join(missing)}",
                        )
                    )
        return results


class RulesPathChecker(BaseChecker):
    _RULES_DIR = ".trae/rules"

    def check(
        self,
        registry: SpecRegistry,
        scanner: SpecScanner,
    ) -> list[CheckResult]:
        results: list[CheckResult] = []
        workspace = scanner.workspace
        rules_dir = workspace / self._RULES_DIR
        if not rules_dir.exists():
            return results

        rule_files: list[Path] = []
        for ext in ("*.md", "*.yaml", "*.yml"):
            rule_files.extend(rules_dir.glob(ext))

        for rule_file in rule_files:
            try:
                with open(rule_file, "r", encoding="utf-8") as f:
                    content = f.read()
            except (OSError, UnicodeDecodeError):
                continue

            spec_refs = re.findall(r"(?:SW|PM|PLC|PY|CODE|LSP|INT)-\d{3,4}(?:-\d{3})?", content)
            for ref_id in set(spec_refs):
                spec_info = registry.get_spec(ref_id)
                if not spec_info:
                    ref_path = self._find_ref_path(workspace, ref_id, content)
                    if ref_path and not ref_path.exists():
                        results.append(
                            CheckResult(
                                check_id="SHC-008",
                                severity=Severity.ERROR,
                                message=f"规则文件引用的规范路径无效: {ref_id}",
                                details=f"文件: {rule_file}, 引用路径: {ref_path}",
                                fix_suggestion=f"更新规则文件中 {ref_id} 的引用路径",
                            )
                        )
                    else:
                        results.append(
                            CheckResult(
                                check_id="SHC-008",
                                severity=Severity.INFO,
                                message=f"规则文件引用了未注册规范 {ref_id}",
                                details=f"文件: {rule_file}",
                                fix_suggestion=f"注册规范 {ref_id} 或更新规则文件中的引用",
                            )
                        )
                elif spec_info.lifecycle == "deprecated":
                    results.append(
                        CheckResult(
                            check_id="SHC-008",
                            severity=Severity.WARNING,
                            message=f"规则文件引用了已废弃规范 {ref_id}",
                            details=f"文件: {rule_file}",
                            fix_suggestion=f"更新引用为 {ref_id} 的替代规范",
                        )
                    )
        return results

    def _find_ref_path(self, workspace: Path, ref_id: str, content: str) -> Path | None:
        path_pattern = re.compile(
            rf"{re.escape(ref_id)}[^\s]*?[:\s]+([^\s]+\.(?:md|yaml|yml))"
        )
        match = path_pattern.search(content)
        if match:
            return workspace / match.group(1)
        if spec_info := getattr(self, "_last_spec_info", None):
            if spec_info.canonical_path:
                return workspace / spec_info.canonical_path
        return None


class PMSessionRefChecker(BaseChecker):
    _PATH_REF_RE = re.compile(r"(?:^|\s)(\S+/\S+\.\w{2,6})(?:\s|$)")
    _MDLINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
    _ARTIFACTS_SECTION_RE = re.compile(
        r"^##\s*4\.?\s*Artifacts?\s*Index",
        re.MULTILINE,
    )
    _NEXT_SECTION_RE = re.compile(r"^##\s*\d", re.MULTILINE)

    def _extract_artifacts_section(self, content: str) -> str:
        m = self._ARTIFACTS_SECTION_RE.search(content)
        if not m:
            return content
        start = m.start()
        rest = content[start + len(m.group(0)):]
        nm = self._NEXT_SECTION_RE.search(rest)
        if nm:
            return content[start : start + len(m.group(0)) + nm.start()]
        return content[start:]

    def _clean_path_ref(self, ref_path_str: str) -> str:
        cleaned = ref_path_str.rstrip(".,;:)]}>")
        paren_idx = cleaned.find("(")
        if paren_idx > 0:
            cleaned = cleaned[:paren_idx].rstrip()
        return cleaned

    def check(
        self,
        registry: SpecRegistry,
        scanner: SpecScanner,
    ) -> list[CheckResult]:
        results: list[CheckResult] = []
        workspace = scanner.workspace

        pm_files = scanner.iter_pm_session_files()
        if not pm_files:
            return results

        for pm_file in pm_files:
            try:
                content = pm_file.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            base_dir = pm_file.parent

            artifacts_content = self._extract_artifacts_section(content)

            refs_seen: set[str] = set()
            for match in self._PATH_REF_RE.finditer(artifacts_content):
                ref_path_str = self._clean_path_ref(match.group(1))
                if not ref_path_str or ref_path_str.startswith(("http:", "https:")):
                    continue
                if ref_path_str in refs_seen:
                    continue
                refs_seen.add(ref_path_str)

                target = base_dir / ref_path_str
                if not target.exists():
                    results.append(
                        CheckResult(
                            check_id="SHC-009",
                            severity=Severity.WARNING,
                            message=f"PM_SESSION 引用的路径不存在: {ref_path_str}",
                            details=f"PM文件: {pm_file.relative_to(workspace)}",
                            fix_suggestion=f"确认 {ref_path_str} 文件是否存在，或更新 PM_SESSION 中的引用",
                        )
                    )

            for line_no, line in enumerate(artifacts_content.splitlines(), 1):
                for match in self._MDLINK_RE.finditer(line):
                    link_target = match.group(2)
                    if link_target.startswith(("http:", "https:", "#")):
                        continue
                    target = base_dir / link_target
                    if not target.exists() and link_target.endswith(".md"):
                        results.append(
                            CheckResult(
                                check_id="SHC-009",
                                severity=Severity.WARNING,
                                message=f"PM_SESSION markdown链接目标不存在: {link_target}",
                                details=f"PM文件: {pm_file.relative_to(workspace)}, 第{line_no}行",
                                fix_suggestion=f"确认 {link_target} 文件是否存在，或更新链接",
                            )
                        )

        return results


class SpecCrossRefChecker(BaseChecker):
    _MDLINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
    _SPEC_ID_RE = re.compile(r"(?:SW|PM|PLC|PY|CODE|LSP|INT)-\d{3,4}(?:-\d{3})?")

    def check(
        self,
        registry: SpecRegistry,
        scanner: SpecScanner,
    ) -> list[CheckResult]:
        results: list[CheckResult] = []
        all_specs = scanner.scan_all()

        for spec_num, paths in all_specs.items():
            for path in paths:
                try:
                    content = path.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    continue
                base_dir = path.parent

                for line_no, line in enumerate(content.splitlines(), 1):
                    for match in self._MDLINK_RE.finditer(line):
                        link_text = match.group(1)
                        link_target = match.group(2)
                        if link_target.startswith(("http:", "https:", "#", "./")):
                            continue

                        if not self._SPEC_ID_RE.search(link_text) and not self._SPEC_ID_RE.search(link_target):
                            continue

                        target_path = base_dir / link_target
                        if not target_path.exists():
                            results.append(
                                CheckResult(
                                    check_id="SHC-010",
                                    severity=Severity.WARNING,
                                    message=f"规范 {spec_num} 交叉引用目标不存在: {link_target}",
                                    details=f"文件: {path.relative_to(scanner.workspace)}, 第{line_no}行",
                                    fix_suggestion=f"确认 {link_target} 文件是否存在，或更新引用为正确的文件名",
                                )
                            )

        return results


_CHECKER_MAP: dict[str, type[BaseChecker]] = {
    "SHC-001": DuplicateChecker,
    "SHC-002": VersionMismatchChecker,
    "SHC-003": DeprecatedRefChecker,
    "SHC-004": IndexLinkChecker,
    "SHC-005": UnlistedSpecChecker,
    "SHC-006": ObsidianLinkChecker,
    "SHC-007": FrontmatterChecker,
    "SHC-008": RulesPathChecker,
    "SHC-009": PMSessionRefChecker,
    "SHC-010": SpecCrossRefChecker,
}


class HealthChecker:
    def __init__(self) -> None:
        self._checkers: list[BaseChecker] = [
            cls() for cls in _CHECKER_MAP.values()
        ]

    def run_all(
        self,
        registry: SpecRegistry,
        scanner: SpecScanner,
    ) -> list[CheckResult]:
        results: list[CheckResult] = []
        for checker in self._checkers:
            results.extend(checker.check(registry, scanner))
        return results

    def run_by_id(
        self,
        check_id: str,
        registry: SpecRegistry,
        scanner: SpecScanner,
    ) -> list[CheckResult]:
        checker_cls = _CHECKER_MAP.get(check_id)
        if checker_cls is None:
            return []
        checker = checker_cls()
        return checker.check(registry, scanner)
