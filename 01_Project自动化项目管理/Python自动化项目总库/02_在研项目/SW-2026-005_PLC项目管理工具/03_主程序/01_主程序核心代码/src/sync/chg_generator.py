# -*- coding: utf-8 -*-
"""
CHG 变更记录文档半自动生成器

从 PM_SESSION change_log 或 .scl changelog 提取变更历史，
生成标准 Markdown 变更记录文档。
半自动模式：生成 → 人工审核(版本号/类型/详细说明) → 替换正式文档。
"""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from src.sync.session_parser import SessionParser, ChangeLogEntry
from src.sync.version_extractor import VersionExtractor
from src.sync.fb_registry import resolve_title_en, resolve_file_prefix
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

RE_SCL_CHANGELOG_ENTRY = re.compile(
    r'^\s*(?://|\(\*)\s*V(\d+\.\d+\.\d+)\s*[\(（]\s*(\d{4}-\d{2}-\d{2})\s*[\)）]\s*[：:]?\s*(.+?)\s*\*?\)?\s*$'
)

TYPE_KEYWORDS = {
    "feat": "功能",
    "fix": "Bug修复",
    "bug": "Bug修复",
    "refactor": "重构",
    "重构": "重构",
    "docs": "文档",
    "文档": "文档",
    "chore": "维护",
    "test": "测试",
}


class ChgGenerator:
    """CHG 变更记录文档半自动生成器"""

    @classmethod
    def generate_from_session(cls, session_path: str, fb_name: str,
                               output_dir: str = None) -> str:
        entries = SessionParser.parse_change_logs(session_path)
        if not entries:
            logger.warning(f"PM_SESSION 中无 change_log 条目")
            return ""

        fb_lower = fb_name.lower()
        filtered = [e for e in entries if cls._is_relevant(e, fb_lower)]

        if not filtered:
            logger.warning(f"未找到与 {fb_name} 相关的变更记录")
            return ""

        title = cls._resolve_title(fb_name)
        prefix = cls._resolve_prefix(fb_name)
        latest_version = cls._infer_version(filtered) or "V?.?.?"

        doc = cls._render_from_entries(title, filtered, latest_version, source="PM_SESSION")

        return cls._write_output(doc, prefix, latest_version, output_dir or Path(session_path).parent)

    @classmethod
    def generate_from_scl(cls, scl_path: str, fb_name: str,
                           output_dir: str = None) -> str:
        try:
            path = Path(scl_path)
            if not path.exists():
                logger.error(f".scl 文件不存在: {scl_path}")
                return ""

            content = path.read_text(encoding="utf-8", errors="ignore")
            entries = []
            for line in content.splitlines():
                m = RE_SCL_CHANGELOG_ENTRY.match(line.strip())
                if m:
                    entries.append({
                        "version": f"V{m.group(1)}",
                        "date": m.group(2),
                        "type": cls._infer_type(m.group(3)),
                        "content": m.group(3).strip(),
                        "author": "—",
                    })

            if not entries:
                logger.warning(f".scl 中无 changelog 条目: {scl_path}")
                return ""

            title = cls._resolve_title(fb_name)
            prefix = cls._resolve_prefix(fb_name)
            latest_version = entries[0]["version"]

            doc = cls._render_from_scl_entries(title, entries, latest_version)

            return cls._write_output(doc, prefix, latest_version,
                                     output_dir or path.parent / "PRD")

        except Exception as e:
            logger.error(f"CHG 生成失败: {e}")
            return ""

    @classmethod
    def _is_relevant(cls, entry: ChangeLogEntry, fb_lower: str) -> bool:
        combined = f"{entry.summary} {entry.scope}".lower()
        return fb_lower in combined

    @classmethod
    def _infer_type(cls, text: str) -> str:
        t = text.lower()
        for k, v in TYPE_KEYWORDS.items():
            if k in t:
                return v
        return "功能"

    @classmethod
    def _infer_version(cls, entries: List[ChangeLogEntry]) -> str:
        for e in entries:
            m = re.search(r'[MV](\d+\.\d+\.\d+)', e.summary)
            if m:
                return f"V{m.group(1)}"
        return "V?.?.?"

    @classmethod
    def _resolve_title(cls, fb_name: str) -> str:
        return resolve_title_en(fb_name)

    @classmethod
    def _resolve_prefix(cls, fb_name: str) -> str:
        return resolve_file_prefix(fb_name)

    @classmethod
    def _render_from_entries(cls, title: str, entries: List[ChangeLogEntry],
                              version: str, source: str) -> str:
        lines = []
        lines.append(f"# 变更记录 {title}")
        lines.append("")
        lines.append("| 版本号 | 变更日期 | 变更类型 | 变更内容 | 变更人 |")
        lines.append("|--------|----------|----------|----------|--------|")

        for e in entries:
            ctype = cls._infer_type(e.summary)
            ver = cls._infer_version([e]) or version
            lines.append(f"| {ver} | {e.date} | {ctype} | {e.summary} | [待补充] |")

        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(f"> **数据来源**: PM_SESSION change_log → chg_generator.py 自动生成")
        lines.append(f"> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"> **[!] 本文件由 CHG 生成器自动生成，请人工审核后替换正式文档**")
        lines.append("")
        lines.append("**人工审核清单**:")
        lines.append("- [ ] 补全版本号映射")
        lines.append("- [ ] 确认变更类型分类正确")
        lines.append("- [ ] 补充变更人信息")
        lines.append("- [ ] 添加详细变更说明（接口清单/逻辑要点）")
        lines.append("- [ ] 与 .scl 文件 changelog 交叉核对")

        return "\n".join(lines)

    @classmethod
    def _render_from_scl_entries(cls, title: str, entries: List[Dict],
                                  version: str) -> str:
        lines = []
        lines.append(f"# 变更记录 {title}")
        lines.append("")
        lines.append("| 版本号 | 变更日期 | 变更类型 | 变更内容 | 变更人 |")
        lines.append("|--------|----------|----------|----------|--------|")

        for e in entries:
            lines.append(
                f"| {e['version']} | {e['date']} | {e['type']} | {e['content']} | {e['author']} |"
            )

        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(f"> **数据来源**: .scl changelog → chg_generator.py 自动生成")
        lines.append(f"> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"> **[!] 本文件由 CHG 生成器自动生成，请人工审核后替换正式文档**")
        lines.append("")
        lines.append("**人工审核清单**:")
        lines.append("- [ ] 核对版本号与 .scl 源码一致")
        lines.append("- [ ] 补充详细变更说明（接口清单/逻辑要点）")
        lines.append("- [ ] 确认变更内容描述准确")

        return "\n".join(lines)

    @classmethod
    def _write_output(cls, doc: str, prefix: str, version: str,
                       output_dir: str) -> str:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        filename = f"变更记录_CHG-{prefix}-{version}-GENERATED.md"
        filepath = out / filename
        filepath.write_text(doc, encoding="utf-8")
        logger.info(f"CHG 文档已生成: {filepath}")
        return str(filepath)