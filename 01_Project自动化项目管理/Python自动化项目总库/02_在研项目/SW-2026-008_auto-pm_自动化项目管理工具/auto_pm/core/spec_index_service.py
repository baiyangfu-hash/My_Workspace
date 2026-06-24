"""规范索引 Service - 规范索引/检索/对比

扫描工作空间下的规范目录，建立规范索引，支持按关键词检索和内容对比。

规范目录约定（与 ui/global_pages/spec_center.py 一致）：
    - PLC: {workspace_root}/0100_PLC自动化/00_通用规范/PLC编程/{code}_*.md
    - Python: {workspace_root}/01_Project自动化项目管理/00_通用规范/Python开发/{code}_*.md

M4-Iter3：提取自 ui/global_pages/spec_center.py，实现职责分离。
"""

from __future__ import annotations

import glob
import os
from dataclasses import dataclass, field
from typing import Any, Optional

from auto_pm.logging.logging import setup_logger

log = setup_logger(log_level="INFO", app_name="auto_pm")


# ── 规范元数据（与 ui/global_pages/spec_center.py 保持一致） ────
# M4-Iter3 后续可统一提取到 core/constants.py

_PLC_SPECS: list[tuple[str, str]] = [
    ("905", "SCL 编程规范"),
    ("904", "SCL 注释规范"),
    ("903", "定时器使用规范"),
    ("906", "错误预防规则"),
]

_PYTHON_SPECS: list[tuple[str, str]] = [
    ("210", "Python 编程规范"),
    ("211", "Python 代码审查规范"),
    ("220", "Python 项目打包规范"),
]

# 技术栈 → (分区标题, 规范目录相对路径, 规范列表)
_STACK_SPECS: dict[str, tuple[str, str, list[tuple[str, str]]]] = {
    "plc": (
        "PLC 技术栈规范",
        os.path.join("0100_PLC自动化", "00_通用规范", "PLC编程"),
        _PLC_SPECS,
    ),
    "python": (
        "Python 技术栈规范",
        os.path.join("01_Project自动化项目管理", "00_通用规范", "Python开发"),
        _PYTHON_SPECS,
    ),
}


@dataclass
class SpecIndexEntry:
    """规范索引条目"""

    code: str                       # 规范编号（如 905、210）
    name: str                       # 规范名称
    stack: str                      # 技术栈（plc/python）
    file_path: str                  # 规范文件绝对路径（空字符串表示未找到）
    exists: bool = False            # 文件是否存在
    file_size: int = 0              # 文件大小（字节）
    mtime: float = 0.0              # 文件修改时间戳
    line_count: int = 0             # 文件行数


@dataclass
class SpecDiffResult:
    """规范对比结果"""

    code1: str
    code2: str
    file1: str
    file2: str
    lines1: list[str] = field(default_factory=list)
    lines2: list[str] = field(default_factory=list)
    added: list[str] = field(default_factory=list)       # file2 有而 file1 无的行
    removed: list[str] = field(default_factory=list)     # file1 有而 file2 无的行
    same: bool = False                                   # 内容是否完全相同


class SpecIndexService:
    """规范索引 Service

    提供规范索引、检索、对比能力。

    用法：
        svc = SpecIndexService(workspace_root)
        index = svc.build_index()
        results = svc.search("SCL")
        diff = svc.compare("905", "210")
    """

    def __init__(self, workspace_root: str = "") -> None:
        self._workspace_root = os.path.abspath(workspace_root) if workspace_root else ""

    @property
    def workspace_root(self) -> str:
        return self._workspace_root

    def set_workspace_root(self, workspace_root: str) -> None:
        """设置工作空间根目录"""
        self._workspace_root = os.path.abspath(workspace_root) if workspace_root else ""

    # ── 索引 ──────────────────────────────────────────────

    def build_index(self) -> list[SpecIndexEntry]:
        """构建规范索引

        扫描所有技术栈的规范目录，返回索引条目列表。

        Returns:
            规范索引条目列表，按 (stack, code) 排序

        Raises:
            RuntimeError: 未注入 workspace_root
        """
        if not self._workspace_root:
            raise RuntimeError("未注入 workspace_root，无法构建规范索引")

        entries: list[SpecIndexEntry] = []
        for stack_key, (_, rel_dir, specs) in _STACK_SPECS.items():
            spec_dir = os.path.join(self._workspace_root, rel_dir)
            for code, name in specs:
                entry = self._build_entry(stack_key, code, name, spec_dir)
                entries.append(entry)

        entries.sort(key=lambda e: (e.stack, e.code))
        log.info("规范索引构建完成: %d 条", len(entries))
        return entries

    def _build_entry(
        self, stack: str, code: str, name: str, spec_dir: str
    ) -> SpecIndexEntry:
        """构建单个规范索引条目"""
        pattern = os.path.join(spec_dir, f"{code}_*.md")
        matches = glob.glob(pattern)

        if not matches:
            return SpecIndexEntry(
                code=code, name=name, stack=stack, file_path="", exists=False
            )

        file_path = matches[0]
        try:
            stat = os.stat(file_path)
            file_size = stat.st_size
            mtime = stat.st_mtime
            with open(file_path, encoding="utf-8") as f:
                line_count = sum(1 for _ in f)
        except OSError as e:
            log.warning("读取规范文件失败 %s: %s", file_path, e)
            return SpecIndexEntry(
                code=code, name=name, stack=stack, file_path=file_path, exists=False
            )

        return SpecIndexEntry(
            code=code,
            name=name,
            stack=stack,
            file_path=file_path,
            exists=True,
            file_size=file_size,
            mtime=mtime,
            line_count=line_count,
        )

    # ── 检索 ──────────────────────────────────────────────

    def search(self, keyword: str) -> list[SpecIndexEntry]:
        """按关键词检索规范

        支持按编号、名称、技术栈匹配（不区分大小写）。

        Args:
            keyword: 检索关键词（空字符串返回所有规范）

        Returns:
            匹配的规范索引条目列表

        Raises:
            RuntimeError: 未注入 workspace_root
        """
        index = self.build_index()
        if not keyword:
            return index

        kw = keyword.lower()
        results = [
            e for e in index
            if kw in e.code.lower() or kw in e.name.lower() or kw in e.stack.lower()
        ]
        log.info("规范检索 '%s': 命中 %d 条", keyword, len(results))
        return results

    def get_entry(self, code: str) -> Optional[SpecIndexEntry]:
        """按编号获取规范索引条目

        Args:
            code: 规范编号（如 905、210）

        Returns:
            规范索引条目，未找到返回 None
        """
        index = self.build_index()
        for entry in index:
            if entry.code == code:
                return entry
        return None

    # ── 内容读取 ──────────────────────────────────────────

    def get_spec_content(self, code: str) -> str:
        """读取规范文件内容

        Args:
            code: 规范编号

        Returns:
            规范文件文本内容

        Raises:
            RuntimeError: 未注入 workspace_root
            FileNotFoundError: 规范文件不存在
        """
        entry = self.get_entry(code)
        if entry is None:
            raise FileNotFoundError(f"未找到规范编号: {code}")
        if not entry.exists or not entry.file_path:
            raise FileNotFoundError(f"规范文件不存在: {code}")

        with open(entry.file_path, encoding="utf-8") as f:
            return f.read()

    # ── 对比 ──────────────────────────────────────────────

    def compare(self, code1: str, code2: str) -> SpecDiffResult:
        """对比两个规范文件内容

        Args:
            code1: 第一个规范编号
            code2: 第二个规范编号

        Returns:
            对比结果

        Raises:
            RuntimeError: 未注入 workspace_root
            FileNotFoundError: 规范文件不存在
        """
        entry1 = self.get_entry(code1)
        entry2 = self.get_entry(code2)

        if entry1 is None:
            raise FileNotFoundError(f"未找到规范编号: {code1}")
        if entry2 is None:
            raise FileNotFoundError(f"未找到规范编号: {code2}")
        if not entry1.exists or not entry1.file_path:
            raise FileNotFoundError(f"规范文件不存在: {code1}")
        if not entry2.exists or not entry2.file_path:
            raise FileNotFoundError(f"规范文件不存在: {code2}")

        content1 = self.get_spec_content(code1)
        content2 = self.get_spec_content(code2)

        lines1 = content1.splitlines()
        lines2 = content2.splitlines()

        # 简单的行级对比（不使用 difflib 以保持依赖最小）
        set1 = set(lines1)
        set2 = set(lines2)
        added = [line for line in lines2 if line not in set1]
        removed = [line for line in lines1 if line not in set2]

        return SpecDiffResult(
            code1=code1,
            code2=code2,
            file1=entry1.file_path,
            file2=entry2.file_path,
            lines1=lines1,
            lines2=lines2,
            added=added,
            removed=removed,
            same=content1 == content2,
        )

    # ── 统计 ──────────────────────────────────────────────

    def get_stats(self) -> dict[str, Any]:
        """获取规范索引统计信息

        Returns:
            {
                'total': int,
                'found': int,
                'missing': int,
                'by_stack': {'plc': {...}, 'python': {...}},
                'missing_codes': list[str],
            }

        Raises:
            RuntimeError: 未注入 workspace_root
        """
        index = self.build_index()
        total = len(index)
        found = sum(1 for e in index if e.exists)
        missing = total - found

        by_stack: dict[str, dict[str, int]] = {}
        missing_codes: list[str] = []
        for entry in index:
            stack = entry.stack
            if stack not in by_stack:
                by_stack[stack] = {"total": 0, "found": 0, "missing": 0}
            by_stack[stack]["total"] += 1
            if entry.exists:
                by_stack[stack]["found"] += 1
            else:
                by_stack[stack]["missing"] += 1
                missing_codes.append(entry.code)

        return {
            "total": total,
            "found": found,
            "missing": missing,
            "by_stack": by_stack,
            "missing_codes": missing_codes,
        }
