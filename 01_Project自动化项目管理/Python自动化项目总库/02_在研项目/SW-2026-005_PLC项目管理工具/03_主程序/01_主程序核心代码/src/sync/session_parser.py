# -*- coding: utf-8 -*-
"""
PM_SESSION.md 解析器

从项目 PM_SESSION 文件中提取变更日志、迭代日志等结构化数据。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class ChangeLogEntry:
    date: str = ""
    summary: str = ""
    scope: str = ""
    status: str = ""


@dataclass
class SessionData:
    project_id: str = ""
    project_name: str = ""
    current_focus: str = ""
    milestone: str = ""
    change_logs: List[ChangeLogEntry] = field(default_factory=list)
    iteration_logs: List[Dict] = field(default_factory=list)
    artifacts_index: Dict[str, List[str]] = field(default_factory=dict)


class SessionParser:
    """PM_SESSION.md 解析器"""

    RE_LOG_LINE = re.compile(
        r'^[\s-]*[-*]\s+(\d{4}-\d{2}-\d{2})\s+(.+)$'
    )
    RE_FIELD = re.compile(r'(?:影响|Scope|状态|Status)\s*[：:]\s*(.+?)(?:\s*[|]\s*|$)')

    @classmethod
    def parse_file(cls, file_path: str) -> SessionData:
        try:
            path = Path(file_path)
            if not path.exists():
                logger.warning(f"PM_SESSION 不存在: {file_path}")
                return SessionData()

            content = path.read_text(encoding="utf-8", errors="ignore")

            data = SessionData()
            data.project_id = cls._extract_field(content, r'project_id\s*[：:]\s*(\S+)')
            data.project_name = cls._extract_field(content, r'project_name\s*[：:]\s*(.+)')
            data.current_focus = cls._extract_field(content, r'current_focus\s*[：:]\s*(.+)')
            data.milestone = cls._extract_field(content, r'milestone\s*[：:]\s*(.+)')
            data.change_logs = cls.parse_change_logs(file_path)
            return data

        except Exception as e:
            logger.error(f"解析失败 {file_path}: {e}")
            return SessionData()

    @classmethod
    def parse_change_logs(cls, file_path: str) -> List[ChangeLogEntry]:
        try:
            path = Path(file_path)
            if not path.exists():
                return []

            content = path.read_text(encoding="utf-8", errors="ignore")

            in_section = False
            entries = []

            for line in content.splitlines():
                stripped = line.strip()

                if "change_log" in stripped and stripped.startswith("- "):
                    in_section = True
                    continue
                if in_section and stripped.startswith("- ") and (
                        "iteration_log" in stripped or "bug_log" in stripped
                        or "refactor_log" in stripped or "release_log" in stripped):
                    in_section = False
                    continue
                if in_section and stripped.startswith("## "):
                    in_section = False
                    continue

                if not in_section:
                    continue

                m = cls.RE_LOG_LINE.match(stripped)
                if not m:
                    continue

                date = m.group(1)
                rest = m.group(2)

                scope = ""
                status = ""

                parts = rest.split("|")
                if len(parts) >= 2:
                    summary_part = parts[0].strip()
                    for p in parts[1:]:
                        p = p.strip()
                        if p.startswith(("影响", "Scope")):
                            scope = p.split(":", 1)[-1].split("：", 1)[-1].strip()
                        elif p.startswith(("状态", "Status")):
                            status = p.split(":", 1)[-1].split("：", 1)[-1].strip()
                else:
                    summary_part = rest

                summary = summary_part.strip()
                if summary.endswith(":"):
                    summary = summary[:-1]

                entries.append(ChangeLogEntry(
                    date=date, summary=summary, scope=scope, status=status
                ))

            logger.info(f"解析 change_log: {len(entries)} 条")
            return entries

        except Exception as e:
            logger.error(f"change_log 解析失败: {e}")
            return []

    @classmethod
    def _extract_field(cls, text: str, pattern: str) -> str:
        m = re.search(pattern, text, re.MULTILINE)
        if m:
            return m.group(1).strip()
        return ""