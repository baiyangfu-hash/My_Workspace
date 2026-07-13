"""PLC-HMI 概念映射：SFB 库函数（路径解析器（变更单路径计算/变量替换））

像 PLC 的 SFB/SFC 系统函数，被 FB 功能块（application/*_facade.py）调用，
不直接暴露给 HMI 画面。

--- 原始注释 ---

路径解析（工作空间约定）

支持两套目录约定：
  - PLC 项目：00_项目管理/01_立项与需求/*_PROJ.md
  - 通用项目：00_项目基础信息/*立项表*.md 或 00_项目基础信息/*_PM.md
"""

from __future__ import annotations

import os
import re

# ── 安全校验 ──────────────────────────────────────────────

# project_id 允许的字符：字母、数字、连字符、下划线
_PROJECT_ID_PATTERN = re.compile(r"^[A-Za-z0-9_\-]+$")

# change_number 允许的格式：CHG-{DOMAIN}-{YYYY}-{XXX}
_CHANGE_NUMBER_PATTERN = re.compile(r"^CHG-[A-Z]+-\d{4}-\d{3}$")


class PathTraversalError(ValueError):
    """路径遍历攻击检测异常"""
    pass


def validate_project_id(project_id: str) -> str:
    """校验 project_id 防止路径遍历

    规则:
      - 非空
      - 仅允许字母、数字、连字符、下划线
      - 不允许包含路径分隔符或 .. 等遍历字符

    Args:
        project_id: 项目编号，如 DJ-2026-005

    Returns:
        校验通过的 project_id

    Raises:
        PathTraversalError: 检测到路径遍历攻击
    """
    if not project_id:
        raise PathTraversalError("项目编号不能为空")
    if not _PROJECT_ID_PATTERN.match(project_id):
        raise PathTraversalError(
            f"项目编号包含非法字符: '{project_id}'，"
            "仅允许字母、数字、连字符、下划线"
        )
    if ".." in project_id or "/" in project_id or "\\" in project_id:
        raise PathTraversalError(
            f"项目编号包含路径遍历字符: '{project_id}'"
        )
    return project_id


def validate_change_number(change_number: str) -> str:
    """校验 change_number 防止路径遍历

    规则:
      - 必须匹配 CHG-{DOMAIN}-{YYYY}-{XXX} 格式
      - DOMAIN 仅允许大写字母

    Args:
        change_number: 变更编号，如 CHG-DOCU-2026-001

    Returns:
        校验通过的 change_number

    Raises:
        PathTraversalError: 检测到路径遍历攻击或格式不合法
    """
    if not change_number:
        raise PathTraversalError("变更编号不能为空")
    if not _CHANGE_NUMBER_PATTERN.match(change_number):
        raise PathTraversalError(
            f"变更编号格式不合法: '{change_number}'，"
            "应为 CHG-{{DOMAIN}}-{{YYYY}}-{{XXX}} 格式"
        )
    return change_number


def validate_path_within_workspace(path: str, workspace_root: str) -> str:
    """校验路径在工作空间范围内，防止路径遍历

    Args:
        path: 待校验的绝对路径
        workspace_root: 工作空间根目录绝对路径

    Returns:
        校验通过的规范化路径

    Raises:
        PathTraversalError: 路径超出工作空间范围
    """
    real_workspace = os.path.realpath(workspace_root)
    real_path = os.path.realpath(path)
    if not real_path.startswith(real_workspace + os.sep) and real_path != real_workspace:
        raise PathTraversalError(
            f"路径超出工作空间范围: '{path}' 不在 '{workspace_root}' 内"
        )
    return real_path


# ── 目录约定 ──────────────────────────────────────────────

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
    re.compile(r"_PROJ\.md$", re.IGNORECASE),
    re.compile(r"立项表.*\.md$", re.IGNORECASE),
    re.compile(r"_PM\.md$", re.IGNORECASE),
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


def _scan_change_dir(base_dir: str, results: list[str], depth: int = 0, max_depth: int = 3) -> None:
    """递归扫描变更单目录，查找 CHG-*.md 文件"""
    try:
        entries = sorted(os.listdir(base_dir))
    except PermissionError:
        return
    for name in entries:
        full_path = os.path.join(base_dir, name)
        if os.path.isdir(full_path):
            # 递归进入子目录（如 CHG-DOCU/、CHG-PLC/ 等）
            if depth < max_depth:
                _scan_change_dir(full_path, results, depth + 1, max_depth)
        elif name.startswith("CHG-") and name.endswith(".md"):
            results.append(full_path)


# 台帐搜索路径（按优先级排列）
_LEDGER_SEARCH_PATHS = [
    # PLC 项目约定
    os.path.join("00_项目管理", "04_变更管理", "04_变更记录"),
    # Python/通用项目约定
    os.path.join("01_项目文档", "03_执行过程", "02_变更管理", "04_变更记录"),
]

# 台帐文件名匹配模式
_LEDGER_FILE_PATTERNS = [
    re.compile(r"版本变更台帐.*\.md$", re.IGNORECASE),
    re.compile(r"变更台帐.*\.md$", re.IGNORECASE),
]


def find_ledger_file(project_path: str) -> str | None:
    """查找版本变更台帐文件

    按优先级搜索多套目录约定（PLC / Python），命中即返回。
    PLC 项目: 00_项目管理/04_变更管理/04_变更记录/01_版本变更台帐.md
    Python 项目: 01_项目文档/03_执行过程/02_变更管理/04_变更记录/01_版本变更台帐.md
    """
    for rel_path in _LEDGER_SEARCH_PATHS:
        search_dir = os.path.join(project_path, rel_path)
        if not os.path.isdir(search_dir):
            continue
        for name in sorted(os.listdir(search_dir)):
            if not name.endswith(".md"):
                continue
            for pattern in _LEDGER_FILE_PATTERNS:
                if pattern.search(name):
                    return os.path.join(search_dir, name)
    return None


def get_or_create_ledger_file(project_path: str) -> str | None:
    """查找或创建版本变更台帐文件

    V0.2.1-P2-8: 若台帐文件不存在，按 PLC 约定路径自动创建
    （00_项目管理/04_变更管理/04_变更记录/01_版本变更台帐.md），
    含「变更单索引」表格骨架，供 LedgerUpdater 追加记录。

    V0.3.0-M0.5-Phase1: 修复跨栈路径策略。不再固定走 PLC 路径，
    而是按项目类型标记自动选择：
    - PLC 项目（有 .plc.json 或 00_项目管理/ 目录）→ PLC 约定路径
    - Python 项目（有 pyproject.toml 或 01_项目文档/ 目录）→ Python 约定路径
    - 默认回退 → PLC 约定路径（向后兼容）

    Args:
        project_path: 项目根目录

    Returns:
        台帐文件路径，失败返回 None
    """
    # 1. 先查找已有台帐
    existing = find_ledger_file(project_path)
    if existing:
        return existing

    # 2. 未找到 → 按项目类型选择创建路径
    ledger_rel_path = _detect_ledger_path_for_project(project_path)
    ledger_dir = os.path.join(project_path, ledger_rel_path)
    ledger_path = os.path.join(ledger_dir, "01_版本变更台帐.md")

    try:
        os.makedirs(ledger_dir, exist_ok=True)
        # 写入台帐骨架（含变更单索引表格，与 LedgerUpdater 期望的结构对齐）
        skeleton = (
            "# 版本变更台帐\n\n"
            "> 记录项目所有变更单的索引与状态\n\n"
            "## 变更单索引\n\n"
            "| 序号 | 变更编号 | 领域 | 申请人 | 申请日期 | 变更描述 | 完成日期 | 状态 |\n"
            "|------|----------|------|--------|----------|----------|----------|------|\n"
        )
        from auto_pm.utils.file_utils import write_file
        write_file(ledger_path, skeleton)
        return ledger_path
    except OSError:
        return None


def _detect_ledger_path_for_project(project_path: str) -> str:
    """按项目类型标记检测应使用的台帐路径（V0.3.0-M0.5-Phase1）

    判据优先级：
    1. 已有目录结构（00_项目管理/ → PLC；01_项目文档/ → Python）
    2. 标记文件（.plc.json → PLC；pyproject.toml → Python）
    3. 默认回退 → PLC 约定路径（向后兼容）

    Returns:
        台帐目录的相对路径（os.path.join 拼接的字符串）
    """
    # 判据 1: 已有目录结构
    plc_dir = os.path.join(project_path, "00_项目管理")
    python_dir = os.path.join(project_path, "01_项目文档")
    if os.path.isdir(plc_dir):
        return _LEDGER_SEARCH_PATHS[0]  # PLC 约定
    if os.path.isdir(python_dir):
        return _LEDGER_SEARCH_PATHS[1]  # Python 约定

    # 判据 2: 标记文件
    has_plc_json = os.path.isfile(os.path.join(project_path, ".plc.json"))
    has_pyproject = os.path.isfile(os.path.join(project_path, "pyproject.toml"))
    if has_plc_json and not has_pyproject:
        return _LEDGER_SEARCH_PATHS[0]  # PLC 约定
    if has_pyproject and not has_plc_json:
        return _LEDGER_SEARCH_PATHS[1]  # Python 约定

    # 判据 3: 默认回退（向后兼容）
    return _LEDGER_SEARCH_PATHS[0]  # PLC 约定


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
