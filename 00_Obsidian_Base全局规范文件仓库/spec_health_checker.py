# -*- coding: utf-8 -*-
# ⚠️ 此脚本已废弃，请使用 specmgr CLI工具
# 安装: pip install -e "c:\Users\fubai\Desktop\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\02_在研项目\SW-2026-006_规范管理工具\02_源代码"
# 用法: specmgr check --workspace <path>
"""
规范健康检查工具 (Spec Health Checker) [已废弃 - 请使用 specmgr check]

检查规范管理体系的健康状况，包括：
- SHC-001: 同一规范ID在多个位置存在活跃副本（版本漂移检测）
- SHC-002: 规范文件版本与注册表记录不一致
- SHC-003: deprecated规范仍被其他文件引用
- SHC-004: INDEX中列出的文件实际不存在
- SHC-005: 实际存在的规范未在INDEX中列出
- SHC-006: Obsidian [[链接]]指向不存在的文件
- SHC-007: 规范文件缺少必要frontmatter
- SHC-008: .trae/rules中引用的规范路径无效

用法:
    python spec_health_checker.py --workspace "c:\\Users\\fubai\\Desktop\\My_Workspace"
    python spec_health_checker.py --workspace "c:\\Users\\fubai\\Desktop\\My_Workspace" --fix
"""
import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class Severity(IntEnum):
    ERROR = 3
    WARNING = 2
    INFO = 1


@dataclass
class CheckResult:
    check_id: str
    severity: Severity
    message: str
    details: str = ""
    fix_suggestion: str = ""


class SpecHealthChecker:
    def __init__(self, workspace_root: str):
        self.workspace = Path(workspace_root)
        self.registry_path = self.workspace / "00_Obsidian_Base全局规范文件仓库" / "spec_registry.json"
        self.registry: Dict = {}
        self.results: List[CheckResult] = []
        self.spec_dirs = [
            self.workspace / "00_Obsidian_Base全局规范文件仓库" / "01_项目管理域",
            self.workspace / "0100_PLC自动化" / "00_通用规范",
            self.workspace / "01_Project自动化项目管理" / "00_通用规范",
        ]
        self.archive_dir = self.workspace / "00_Obsidian_Base全局规范文件仓库" / "_archive"

    def load_registry(self) -> bool:
        if not self.registry_path.exists():
            self.results.append(CheckResult(
                check_id="SHC-000",
                severity=Severity.ERROR,
                message="规范注册表不存在",
                details=f"预期路径: {self.registry_path}",
                fix_suggestion="运行Phase 1创建spec_registry.json"
            ))
            return False
        try:
            with open(self.registry_path, "r", encoding="utf-8") as f:
                self.registry = json.load(f)
            return True
        except json.JSONDecodeError as e:
            self.results.append(CheckResult(
                check_id="SHC-000",
                severity=Severity.ERROR,
                message="规范注册表JSON格式错误",
                details=str(e),
                fix_suggestion="修复spec_registry.json的JSON格式"
            ))
            return False

    def scan_spec_files(self) -> Dict[str, List[Path]]:
        file_map: Dict[str, List[Path]] = {}
        scan_dirs = self.spec_dirs + [self.archive_dir]
        for scan_dir in scan_dirs:
            if not scan_dir.exists():
                continue
            for md_file in scan_dir.rglob("*.md"):
                if md_file.name == "README.md":
                    continue
                rel_path = md_file.relative_to(self.workspace)
                name = md_file.name
                num_match = re.match(r"^(\d+)_", name)
                if num_match:
                    number = num_match.group(1)
                    if number not in file_map:
                        file_map[number] = []
                    file_map[number].append(md_file)
        return file_map

    def check_shc001_duplicate_active_copies(self, file_map: Dict[str, List[Path]]):
        for number, paths in file_map.items():
            active_paths = []
            for p in paths:
                rel = str(p.relative_to(self.workspace))
                if "_archive" not in rel and "_deprecated" not in rel:
                    active_paths.append(p)
            if len(active_paths) > 1:
                filenames = [p.name for p in active_paths]
                if len(set(filenames)) == len(filenames):
                    continue
                locations = []
                for p in active_paths:
                    rel = str(p.relative_to(self.workspace))
                    version = self._extract_version_from_file(p)
                    locations.append(f"  - {rel} ({version})")
                self.results.append(CheckResult(
                    check_id="SHC-001",
                    severity=Severity.ERROR,
                    message=f"编号{number}的规范在{len(active_paths)}个位置存在活跃副本",
                    details="\n".join(locations),
                    fix_suggestion="保留canonical_path处的副本，其他位置移入_archive或添加重定向"
                ))

    def check_shc002_version_mismatch(self):
        if not self.registry.get("specs"):
            return
        for spec_id, spec_info in self.registry["specs"].items():
            canonical = self.workspace / spec_info["canonical_path"]
            if not canonical.exists():
                continue
            file_version = self._extract_version_from_file(canonical)
            if file_version and file_version != spec_info["version"]:
                self.results.append(CheckResult(
                    check_id="SHC-002",
                    severity=Severity.ERROR,
                    message=f"规范{spec_id}版本不一致",
                    details=f"注册表: {spec_info['version']}, 文件实际: {file_version}",
                    fix_suggestion=f"更新spec_registry.json中{spec_id}的version为{file_version}"
                ))

    def check_shc003_deprecated_still_referenced(self):
        if not self.registry.get("specs"):
            return
        deprecated_ids = set()
        for spec_id, spec_info in self.registry["specs"].items():
            if spec_info.get("lifecycle") == "deprecated":
                deprecated_ids.add(spec_id)
        if not deprecated_ids:
            return
        for scan_dir in self.spec_dirs:
            if not scan_dir.exists():
                continue
            for md_file in scan_dir.rglob("*.md"):
                if md_file.name == "README.md":
                    continue
                try:
                    content = md_file.read_text(encoding="utf-8")
                except Exception:
                    continue
                for dep_id in deprecated_ids:
                    dep_info = self.registry["specs"].get(dep_id, {})
                    dep_number = dep_info.get("number", "")
                    if not dep_number:
                        continue
                    active_ref_pattern = re.compile(
                        r"(?:遵循|参照|引用|参考|按照|依据|根据|基于|见|参见|详见)"
                        r".*?"
                        rf"(?:{dep_number}|{dep_id})"
                        r"|"
                        rf"\[\[.*?{dep_number}.*?\]\]"
                        r"|"
                        rf"\[.*?{dep_number}.*?\]\(.*?\.md\)"
                    )
                    matches = list(active_ref_pattern.finditer(content))
                    if not matches:
                        continue
                    filtered = []
                    for m in matches:
                        ctx = content[max(0, m.start()-30):m.end()+30]
                        if any(kw in ctx for kw in ["已废弃", "替代", "deprecated", "replaced_by", "历史", "归档", "archive"]):
                            continue
                        filtered.append(m)
                    if filtered:
                        rel = str(md_file.relative_to(self.workspace))
                        replaced_by = dep_info.get("replaced_by", [])
                        self.results.append(CheckResult(
                            check_id="SHC-003",
                            severity=Severity.WARNING,
                            message=f"已废弃规范{dep_id}仍被引用",
                            details=f"引用文件: {rel}",
                            fix_suggestion=f"替换为替代规范: {', '.join(replaced_by)}"
                        ))

    def check_shc004_index_file_existence(self):
        index_path = self.workspace / "00_Obsidian_Base全局规范文件仓库" / "00_INDEX_全局规范索引_V2.0.0.md"
        if not index_path.exists():
            self.results.append(CheckResult(
                check_id="SHC-004",
                severity=Severity.ERROR,
                message="全局规范索引文件不存在",
                details=f"预期路径: {index_path}",
            ))
            return
        try:
            content = index_path.read_text(encoding="utf-8")
        except Exception:
            return
        link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+\.md)\)")
        for match in link_pattern.finditer(content):
            link_text = match.group(1)
            link_path = match.group(2)
            if link_path.startswith("http"):
                continue
            full_path = index_path.parent / link_path
            if not full_path.exists():
                self.results.append(CheckResult(
                    check_id="SHC-004",
                    severity=Severity.ERROR,
                    message=f"索引中链接指向不存在的文件",
                    details=f"链接: [{link_text}]({link_path})",
                    fix_suggestion="检查文件是否已被移动或重命名"
                ))

    def check_shc005_unlisted_specs(self, file_map: Dict[str, List[Path]]):
        if not self.registry.get("specs"):
            return
        registered_paths = set()
        for spec_info in self.registry["specs"].values():
            registered_paths.add(spec_info["canonical_path"])
        for scan_dir in self.spec_dirs:
            if not scan_dir.exists():
                continue
            for md_file in scan_dir.rglob("*.md"):
                if md_file.name == "README.md":
                    continue
                rel_path = str(md_file.relative_to(self.workspace)).replace("\\", "/")
                if rel_path not in registered_paths:
                    self.results.append(CheckResult(
                        check_id="SHC-005",
                        severity=Severity.WARNING,
                        message=f"规范文件未在注册表中登记",
                        details=rel_path,
                        fix_suggestion=f"在spec_registry.json中添加此文件的条目"
                    ))

    def check_shc006_obsidian_links(self):
        obsidian_dir = self.workspace / "00_Obsidian_Base全局规范文件仓库"
        if not obsidian_dir.exists():
            return
        wiki_link_pattern = re.compile(r"\[\[([^\]]+)\]\]")
        for md_file in obsidian_dir.rglob("*.md"):
            if "_archive" in str(md_file):
                continue
            try:
                content = md_file.read_text(encoding="utf-8")
            except Exception:
                continue
            in_code_block = False
            in_frontmatter = False
            fm_line_count = 0
            for line_no, line in enumerate(content.split("\n"), 1):
                if line_no == 1 and line.strip() == "---":
                    in_frontmatter = True
                    fm_line_count = 1
                    continue
                if in_frontmatter:
                    if line.strip() == "---" and fm_line_count > 1:
                        in_frontmatter = False
                    fm_line_count += 1
                    continue
                if line.strip().startswith("```"):
                    in_code_block = not in_code_block
                    continue
                if in_code_block:
                    continue
                if line.strip().startswith("|") or line.strip().startswith(">"):
                    for ch in ["`[[wikilink]]`", "`[[", "]]`"]:
                        if ch in line:
                            line = line.replace(ch, "")
                for match in wiki_link_pattern.finditer(line):
                    link_target = match.group(1).split("|")[0].strip()
                    if link_target in ("wikilink",):
                        continue
                    target_path = md_file.parent / (link_target + ".md" if not link_target.endswith(".md") else link_target)
                    if not target_path.exists():
                        rel = str(md_file.relative_to(self.workspace))
                        self.results.append(CheckResult(
                            check_id="SHC-006",
                            severity=Severity.WARNING,
                            message=f"Obsidian链接指向不存在的文件",
                            details=f"文件: {rel}:{line_no}, 链接: [[{link_target}]]",
                            fix_suggestion="更新链接或确认目标文件存在"
                        ))

    def check_shc007_missing_frontmatter(self):
        if not self.registry.get("specs"):
            return
        for spec_id, spec_info in self.registry["specs"].items():
            if spec_info.get("lifecycle") in ("deprecated", "archived"):
                continue
            canonical = self.workspace / spec_info["canonical_path"]
            if not canonical.exists():
                continue
            try:
                content = canonical.read_text(encoding="utf-8")
            except Exception:
                continue
            if not content.startswith("---"):
                self.results.append(CheckResult(
                    check_id="SHC-007",
                    severity=Severity.INFO,
                    message=f"规范{spec_id}缺少frontmatter",
                    details=spec_info["canonical_path"],
                    fix_suggestion="添加YAML frontmatter（spec_id, version, domain, lifecycle）"
                ))

    def check_shc008_rules_path_validity(self):
        rules_files = [
            self.workspace / ".trae" / "rules" / "project-rule.md",
            self.workspace / "0100_PLC自动化" / ".trae" / "rules" / "plc-rules.md",
            self.workspace / "01_Project自动化项目管理" / ".trae" / "rules" / "python-rules.md",
        ]
        for rules_file in rules_files:
            if not rules_file.exists():
                continue
            try:
                content = rules_file.read_text(encoding="utf-8")
            except Exception:
                continue
            spec_file_pattern = re.compile(r"(\d{3}_[\w\u4e00-\u9fff]+\.md)")
            for match in spec_file_pattern.finditer(content):
                referenced = match.group(1)
                found = False
                for search_dir in self.spec_dirs:
                    if not search_dir.exists():
                        continue
                    candidates = list(search_dir.rglob(referenced))
                    if candidates:
                        found = True
                        break
                if not found:
                    rel = str(rules_file.relative_to(self.workspace))
                    self.results.append(CheckResult(
                        check_id="SHC-008",
                        severity=Severity.ERROR,
                        message=f".trae/rules中引用的规范文件不存在",
                        details=f"规则文件: {rel}, 引用: {referenced}",
                        fix_suggestion="确认规范文件路径是否正确"
                    ))

    def _extract_version_from_file(self, file_path: Path) -> Optional[str]:
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            return None
        version_patterns = [
            r"版本[：:]\s*V?(\d+\.\d+\.\d+)",
            r"version:\s*V?(\d+\.\d+\.\d+)",
            r"_V(\d+\.\d+\.\d+)",
            r"V(\d+\.\d+\.\d+)",
        ]
        for pattern in version_patterns:
            match = re.search(pattern, content[:500])
            if match:
                return "V" + match.group(1) if not match.group(0).startswith("V") else "V" + match.group(1)
        return None

    def run_all_checks(self) -> List[CheckResult]:
        self.results = []
        if not self.load_registry():
            return self.results
        file_map = self.scan_spec_files()
        self.check_shc001_duplicate_active_copies(file_map)
        self.check_shc002_version_mismatch()
        self.check_shc003_deprecated_still_referenced()
        self.check_shc004_index_file_existence()
        self.check_shc005_unlisted_specs(file_map)
        self.check_shc006_obsidian_links()
        self.check_shc007_missing_frontmatter()
        self.check_shc008_rules_path_validity()
        return self.results

    def print_report(self):
        if not self.results:
            print("\n✅ 所有检查通过！规范管理体系健康状况良好。")
            return
        error_count = sum(1 for r in self.results if r.severity == Severity.ERROR)
        warning_count = sum(1 for r in self.results if r.severity == Severity.WARNING)
        info_count = sum(1 for r in self.results if r.severity == Severity.INFO)
        print(f"\n{'='*60}")
        print(f"规范健康检查报告")
        print(f"{'='*60}")
        print(f"总计: {len(self.results)} 个问题")
        print(f"  🔴 错误: {error_count}")
        print(f"  🟡 警告: {warning_count}")
        print(f"  🟢 提示: {info_count}")
        print(f"{'='*60}\n")
        for result in sorted(self.results, key=lambda r: r.severity, reverse=True):
            severity_icon = {Severity.ERROR: "🔴", Severity.WARNING: "🟡", Severity.INFO: "🟢"}
            icon = severity_icon.get(result.severity, "⚪")
            print(f"{icon} {result.check_id} [{result.severity.name}]")
            print(f"   {result.message}")
            if result.details:
                for line in result.details.split("\n"):
                    print(f"   {line}")
            if result.fix_suggestion:
                print(f"   💡 建议: {result.fix_suggestion}")
            print()


def main():
    parser = argparse.ArgumentParser(description="规范健康检查工具")
    parser.add_argument(
        "--workspace",
        default=r"c:\Users\fubai\Desktop\My_Workspace",
        help="工作空间根目录路径"
    )
    args = parser.parse_args()
    checker = SpecHealthChecker(args.workspace)
    checker.run_all_checks()
    checker.print_report()


if __name__ == "__main__":
    main()
