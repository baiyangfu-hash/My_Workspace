# -*- coding: utf-8 -*-
"""
全量同步报告生成器

L2 按需层：在项目交付/验收前，生成覆盖 L0+L1+L2 的完整同步状态报告。
包含：版本差距矩阵、DSN/UM 文档覆盖度、变更台帐聚合、优先级行动建议。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from src.sync.version_checker import VersionChecker, VersionGapReport, FbVersionGap
from src.sync.version_extractor import VersionExtractor
from src.sync.session_parser import SessionParser, ChangeLogEntry
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class DocStatus:
    fb_name: str = ""
    code_version: str = ""
    doc_path: str = ""
    doc_version: str = ""
    doc_type: str = ""
    status: str = "-"


@dataclass
class FullSyncReport:
    project_path: str = ""
    project_name: str = ""
    generated_at: str = ""
    version_gap: Optional[VersionGapReport] = None
    dsn_status: List[DocStatus] = field(default_factory=list)
    um_status: List[DocStatus] = field(default_factory=list)
    change_ledger: List[ChangeLogEntry] = field(default_factory=list)
    action_items: List[str] = field(default_factory=list)


class SyncReport:
    """全量同步报告生成器"""

    RE_FB_ID = re.compile(r'(FB_\d+|OB1|FB_External|GlobalVars)', re.IGNORECASE)

    FB_ALIAS_MAP = {
        "fb_external": ["fb3001", "external"],
        "globalvars": ["globalvars", "db1"],
    }

    @classmethod
    def _extract_fb_id(cls, name: str) -> str:
        m = cls.RE_FB_ID.search(name)
        if m:
            return m.group(1).lower()
        return name.lower()

    @classmethod
    def generate_full_report(cls, project_path: str) -> FullSyncReport:
        p = Path(project_path)
        report = FullSyncReport(
            project_path=str(p.resolve()),
            project_name=p.name,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
        )

        report.version_gap = VersionChecker.check_project(project_path)

        report.dsn_status = cls._check_documents(p, "DSN", report.version_gap.fb_gaps)
        report.um_status = cls._check_documents(p, "UM", report.version_gap.fb_gaps)

        session_path = cls._find_session(p)
        if session_path:
            report.change_ledger = SessionParser.parse_change_logs(str(session_path))

        report.action_items = cls._generate_action_items(report)

        logger.info(f"全量报告生成: {len(report.version_gap.fb_gaps)} FB, "
                     f"{len(report.dsn_status)} DSN, {len(report.um_status)} UM, "
                     f"{len(report.action_items)} 行动项")
        return report

    @classmethod
    def render_markdown(cls, report: FullSyncReport) -> str:
        lines = []
        lines.append(f"# 文档-代码全量同步报告")
        lines.append("")
        lines.append(f"> **项目**: {report.project_name}")
        lines.append(f"> **生成时间**: {report.generated_at}")
        lines.append(f"> **路径**: {report.project_path}")
        lines.append("")

        lines.append("## 1. 版本差距矩阵 (L0)")
        lines.append("")
        if report.version_gap and report.version_gap.fb_gaps:
            lines.append(VersionChecker.format_report(report.version_gap))
        else:
            lines.append("> 无版本数据")
        lines.append("")

        lines.append("## 2. DSN 详细设计文档覆盖度 (L2)")
        lines.append("")
        if report.dsn_status:
            lines.append("| FB模块 | 代码版本 | DSN版本 | DSN文件 | 状态 |")
            lines.append("|--------|:------:|:------:|---------|:--:|")
            for d in report.dsn_status:
                lines.append(
                    f"| {d.fb_name} | {d.code_version} | {d.doc_version} | "
                    f"{Path(d.doc_path).name if d.doc_path else '-'} | {d.status} |"
                )
        else:
            lines.append("> 项目内无 DSN 文档")
        lines.append("")

        lines.append("## 3. UM 使用手册覆盖度 (L2)")
        lines.append("")
        if report.um_status:
            lines.append("| FB模块 | 代码版本 | UM版本 | UM文件 | 状态 |")
            lines.append("|--------|:------:|:------:|--------|:--:|")
            for d in report.um_status:
                lines.append(
                    f"| {d.fb_name} | {d.code_version} | {d.doc_version} | "
                    f"{Path(d.doc_path).name if d.doc_path else '-'} | {d.status} |"
                )
        else:
            lines.append("> 项目内无 UM 文档")
        lines.append("")

        lines.append("## 4. 变更台帐聚合 (L2)")
        lines.append("")
        if report.change_ledger:
            lines.append("| 日期 | 变更摘要 | 影响范围 | 状态 |")
            lines.append("|------|----------|----------|------|")
            for e in report.change_ledger:
                lines.append(f"| {e.date} | {e.summary[:60]} | {e.scope or '-'} | {e.status or '-'} |")
            lines.append("")
            lines.append(f"> 共 {len(report.change_ledger)} 条变更记录 (来源: PM_SESSION)")
        else:
            lines.append("> 未找到 PM_SESSION 或 change_log 为空")
        lines.append("")

        lines.append("## 5. 同步行动建议")
        lines.append("")
        if report.action_items:
            for i, item in enumerate(report.action_items, 1):
                lines.append(f"{i}. {item}")
        else:
            lines.append("> 所有文档已同步，无需行动 [OK]")
        lines.append("")
        lines.append("---")
        lines.append(f"> 报告由 SW-2026-005 sync_report.py 自动生成")

        return "\n".join(lines)

    @classmethod
    def _check_documents(cls, project_root: Path, doc_type: str,
                          fb_gaps: List[FbVersionGap]) -> List[DocStatus]:
        results = []

        all_docs = []
        for f in project_root.rglob("*.md"):
            if "archive" in str(f).lower() or ".trae" in f.parts:
                continue
            name_upper = f.name.upper()
            if doc_type.upper() in name_upper:
                all_docs.append(f)

        matched_fbs = set()
        for gap in fb_gaps:
            matched = False
            fb_id = cls._extract_fb_id(gap.fb_name)

            for doc_path in all_docs:
                doc_name = doc_path.name.lower()
                if cls._match_fb_to_doc(fb_id, doc_name):
                    ver = VersionExtractor.extract_prd_version(str(doc_path)) or ""
                    code_v = gap.code_version
                    status = cls._status_for_doc(code_v, ver)
                    results.append(DocStatus(
                        fb_name=gap.fb_name,
                        code_version=code_v,
                        doc_path=str(doc_path),
                        doc_version=ver,
                        doc_type=doc_type,
                        status=status,
                    ))
                    matched_fbs.add(doc_path.name.lower())
                    matched = True
                    break

            if not matched:
                results.append(DocStatus(
                    fb_name=gap.fb_name,
                    code_version=gap.code_version,
                    doc_type=doc_type,
                    status="[MISSING]",
                ))

        for doc_path in all_docs:
            if doc_path.name.lower() not in matched_fbs:
                ver = VersionExtractor.extract_prd_version(str(doc_path)) or ""
                fb = cls._extract_fb_from_docname(doc_path.name)
                results.append(DocStatus(
                    fb_name=fb,
                    code_version="-",
                    doc_path=str(doc_path),
                    doc_version=ver,
                    doc_type=doc_type,
                    status="[?]",
                ))

        return results

    @classmethod
    def _match_fb_to_doc(cls, fb_id_lower: str, doc_name_lower: str) -> bool:
        if fb_id_lower in doc_name_lower:
            return True
        fb_id_no_sep = fb_id_lower.replace("_", "").replace("-", "")
        doc_name_no_sep = doc_name_lower.replace("_", "").replace("-", "")
        if fb_id_no_sep in doc_name_no_sep:
            return True
        if "globalvars" in fb_id_lower and "globalvars" in doc_name_lower:
            return True
        aliases = cls.FB_ALIAS_MAP.get(fb_id_lower, [])
        for alias in aliases:
            if alias in doc_name_lower or alias in doc_name_no_sep:
                return True
        return False

    @classmethod
    def _extract_fb_from_docname(cls, doc_name: str) -> str:
        m = re.search(r'(FB[\s_\-]*\d+|FB[\s_\-]*External|OB1)', doc_name, re.IGNORECASE)
        if m:
            return m.group(1).replace(" ", "_").replace("-", "_")
        m = re.search(r'DSN-(DJ-\d+-\d+)', doc_name, re.IGNORECASE)
        if m:
            return m.group(1)
        return doc_name.rsplit(".", 1)[0][:40]

    @classmethod
    def _status_for_doc(cls, code_version: str, doc_version: str) -> str:
        if not doc_version:
            return "[X]"
        if not code_version:
            return "[?]"
        cmp = VersionExtractor.compare_versions(doc_version, code_version)
        if cmp >= 0:
            return "[OK]"
        return "[X]"

    @classmethod
    def _generate_action_items(cls, report: FullSyncReport) -> List[str]:
        items = []

        dsn_missing = [d for d in report.dsn_status if d.status == "[MISSING]"]
        um_missing = [u for u in report.um_status if u.status == "[MISSING]"]

        for d in dsn_missing:
            items.append(f"[P0] {d.fb_name} 缺少 DSN 详细设计文档 — 需新建")

        for u in um_missing:
            items.append(f"[P1] {u.fb_name} 缺少 UM 使用手册 — 需新建")

        dsn_lag = [d for d in report.dsn_status if d.status == "[X]"]
        um_lag = [u for u in report.um_status if u.status == "[X]"]

        for d in dsn_lag:
            diff = cls._gap_desc(d.doc_version, d.code_version)
            items.append(f"[P1] {d.fb_name} DSN 版本滞后 ({diff}): {d.doc_version} -> {d.code_version}")

        for u in um_lag:
            diff = cls._gap_desc(u.doc_version, u.code_version)
            items.append(f"[P2] {u.fb_name} UM 版本滞后 ({diff}): {u.doc_version} -> {u.code_version}")

        if report.version_gap:
            for gap in report.version_gap.fb_gaps:
                if gap.status == "[X]":
                    items.append(f"[P1] {gap.fb_name} IFC/DSN/CHG 版本不一致 — 运行 generate-ifc / generate-chg")

        no_version_docs = [d for d in report.dsn_status if not d.doc_version and d.doc_path]
        for d in no_version_docs[:5]:
            items.append(f"[P2] {Path(d.doc_path).name} 文件名/内容无版本号标记 — 需规范化命名")

        if not items:
            items.append("[OK] 所有文档与代码版本一致，无需行动")

        items.sort(key=lambda x: (
            0 if "[P0]" in x else 1 if "[P1]" in x else 2
        ))
        return items

    @classmethod
    def _gap_desc(cls, doc_v: str, code_v: str) -> str:
        dt = VersionExtractor.parse_version_tuple(doc_v)
        ct = VersionExtractor.parse_version_tuple(code_v)
        if ct[0] - dt[0] > 0:
            return f"~{ct[0] - dt[0]}个大版本"
        if ct[1] - dt[1] > 0:
            return f"{ct[1] - dt[1]}个版本"
        return "未知"

    @classmethod
    def _find_session(cls, project_root: Path) -> Optional[Path]:
        candidates = list(project_root.rglob("PM_SESSION*.md"))
        for c in candidates:
            if ".trae" not in c.parts:
                return c
        return None