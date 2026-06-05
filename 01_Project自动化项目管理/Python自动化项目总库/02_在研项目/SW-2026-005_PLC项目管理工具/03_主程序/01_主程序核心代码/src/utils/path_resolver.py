"""路径解析（工作空间约定）

支持两套目录约定：
  - PLC 项目：00_项目管理/01_立项与需求/*_PROJ-*.md
  - 通用项目：00_项目基础信息/*立项表*.md 或 00_项目基础信息/*_PM-*.md
"""

from __future__ import annotations

import os
import re

# 立项表搜索路径（按优先级排列，命中即停）
_PROJ_SEARCH_PATHS = [
    # PLC 项目约定
    ("00_项目管理", "01_立项与需求"),
    # Python/通用项目约定
    ("00_项目基础信息",),
    # 兼容：直接在项目根目录下
    (),
]

# 立项表文件名匹配模式（按优先级排列）
_PROJ_FILE_PATTERNS = [
    re.compile(r"_PROJ-.*\.md$", re.IGNORECASE),
    re.compile(r"立项表.*\.md$", re.IGNORECASE),
    re.compile(r"_PM-.*\.md$", re.IGNORECASE),
]

# 变更单搜索路径（按优先级排列）
_CHANGE_SEARCH_PATHS = [
    # PLC 项目约定
    os.path.join("00_项目管理", "04_变更管理", "01_变更单"),
    # Python/通用项目约定
    os.path.join("01_项目文档", "03_执行过程", "02_变更管理"),
]


def find_proj_file(project_path: str) -> str | None:
    """在项目目录下查找立项表文件

    按优先级搜索多套目录约定，命中即返回。
    """
    for search_parts in _PROJ_SEARCH_PATHS:
        search_dir = os.path.join(project_path, *search_parts) if search_parts else project_path
        if not os.path.isdir(search_dir):
            continue
        for name in sorted(os.listdir(search_dir)):
            if not name.endswith(".md"):
                continue
            for pattern in _PROJ_FILE_PATTERNS:
                if pattern.search(name):
                    return os.path.join(search_dir, name)
    return None


def scan_change_files(project_path: str) -> list[str]:
    """扫描变更单文件

    按优先级搜索多套目录约定，合并结果。
    PLC 项目: 00_项目管理/04_变更管理/01_变更单/CHG-*/CHG-*.md
    通用项目: 01_项目文档/03_执行过程/02_变更管理/ 下的 CHG-*.md
    """
    results: list[str] = []
    for rel_path in _CHANGE_SEARCH_PATHS:
        base_dir = os.path.join(project_path, rel_path)
        if not os.path.isdir(base_dir):
            continue
        _scan_change_dir(base_dir, results)
    return results


def _scan_change_dir(base_dir: str, results: list[str]) -> None:
    """递归扫描变更单目录，查找 CHG-*.md 文件"""
    try:
        entries = sorted(os.listdir(base_dir))
    except PermissionError:
        return
    for name in entries:
        full_path = os.path.join(base_dir, name)
        if os.path.isdir(full_path):
            # 递归进入子目录（如 CHG-DOCU/、CHG-PLC/ 等）
            _scan_change_dir(full_path, results)
        elif name.startswith("CHG-") and name.endswith(".md"):
            results.append(full_path)


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
