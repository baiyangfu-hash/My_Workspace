"""路径解析（工作空间约定）"""

from __future__ import annotations

import os
import re


def find_proj_file(project_path: str) -> str | None:
    """在项目目录下查找立项表文件

    查找路径: 00_项目管理/01_立项与需求/*_PROJ-*.md
    """
    search_dir = os.path.join(project_path, "00_项目管理", "01_立项与需求")
    if not os.path.isdir(search_dir):
        return None
    for name in os.listdir(search_dir):
        if re.search(r"_PROJ-.*\.md$", name, re.IGNORECASE):
            return os.path.join(search_dir, name)
    return None


def scan_change_files(project_path: str) -> list[str]:
    """扫描变更单文件

    查找路径: 00_项目管理/04_变更管理/01_变更单/CHG-*/CHG-*.md
    """
    base_dir = os.path.join(project_path, "00_项目管理", "04_变更管理", "01_变更单")
    if not os.path.isdir(base_dir):
        return []
    results: list[str] = []
    for domain_dir in sorted(os.listdir(base_dir)):
        domain_path = os.path.join(base_dir, domain_dir)
        if not os.path.isdir(domain_path):
            continue
        for name in sorted(os.listdir(domain_path)):
            if name.startswith("CHG-") and name.endswith(".md"):
                results.append(os.path.join(domain_path, name))
    return results


def find_ledger_file(project_path: str) -> str | None:
    """查找版本变更台帐文件

    查找路径: 00_项目管理/04_变更管理/04_变更记录/01_版本变更台帐.md
    """
    ledger_path = os.path.join(
        project_path, "00_项目管理", "04_变更管理", "04_变更记录", "01_版本变更台帐.md"
    )
    if os.path.isfile(ledger_path):
        return ledger_path
    return None


def get_project_id_from_path(project_path: str) -> str:
    """从项目目录路径提取项目编号

    例: C:\\...\\0100_PLC自动化\\DJ-2026-005\\ → DJ-2026-005
    """
    return os.path.basename(project_path)


def extract_domain_from_change_number(change_number: str) -> str:
    """从变更编号提取领域

    例: CHG-DOCU-2026-001 → DOCU
    """
    parts = change_number.split("-")
    if len(parts) >= 2:
        return parts[1]
    return ""
