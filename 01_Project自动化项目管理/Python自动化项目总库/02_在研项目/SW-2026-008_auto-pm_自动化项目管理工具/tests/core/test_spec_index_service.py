"""SpecIndexService 单元测试（M4-Iter3）

测试内容：
- build_index() 构建规范索引
- search() 按关键词检索
- get_entry() 按编号获取
- get_spec_content() 读取规范内容
- compare() 对比两个规范
- get_stats() 统计信息
- 异常情况（未注入 workspace_root、文件不存在等）
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from auto_pm.core.spec_index_service import (
    SpecDiffResult,
    SpecIndexService,
)

# ── fixtures ─────────────────────────────────────────────


def _create_spec_file(
    workspace: Path, stack: str, code: str, name: str, content: str = ""
) -> Path:
    """在工作空间下创建规范文件"""
    if stack == "plc":
        rel_dir = os.path.join("0100_PLC自动化", "00_通用规范", "PLC编程")
    else:
        rel_dir = os.path.join("01_Project自动化项目管理", "00_通用规范", "Python开发")
    spec_dir = workspace / rel_dir
    spec_dir.mkdir(parents=True, exist_ok=True)
    file_path = spec_dir / f"{code}_{name}.md"
    file_path.write_text(content or f"# {code} {name}\n\n规范内容\n", encoding="utf-8")
    return file_path


@pytest.fixture
def spec_workspace(tmp_path: Path) -> Path:
    """临时工作空间，含所有规范文件"""
    _create_spec_file(tmp_path, "plc", "905", "SCL编程规范_LSP", "# 905 SCL\n\nPLC 编程规范\n")
    _create_spec_file(tmp_path, "plc", "904", "SCL注释规范_LSP", "# 904 SCL 注释\n\nPLC 注释规范\n")
    _create_spec_file(tmp_path, "plc", "903", "定时器使用规范_LSP", "# 903 定时器\n\nPLC 定时器规范\n")
    _create_spec_file(tmp_path, "plc", "906", "错误预防规则_LSP", "# 906 错误预防\n\nPLC 错误预防规范\n")
    _create_spec_file(tmp_path, "python", "210", "Python编程规范_DEV", "# 210 Python\n\nPython 编程规范\n")
    _create_spec_file(tmp_path, "python", "211", "Python代码审查规范_DEV", "# 211 审查\n\nPython 审查规范\n")
    _create_spec_file(tmp_path, "python", "220", "Python项目打包规范_DEV", "# 220 打包\n\nPython 打包规范\n")
    return tmp_path


@pytest.fixture
def partial_workspace(tmp_path: Path) -> Path:
    """部分规范文件存在的工作空间（仅 905 和 210）"""
    _create_spec_file(tmp_path, "plc", "905", "SCL编程规范_LSP")
    _create_spec_file(tmp_path, "python", "210", "Python编程规范_DEV")
    return tmp_path


# ── build_index 测试 ────────────────────────────────────


class TestBuildIndex:
    """build_index() 测试"""

    def test_raises_without_workspace_root(self) -> None:
        """未注入 workspace_root 时抛 RuntimeError"""
        svc = SpecIndexService()
        with pytest.raises(RuntimeError, match="未注入 workspace_root"):
            svc.build_index()

    def test_all_specs_found(self, spec_workspace: Path) -> None:
        """所有规范文件都存在"""
        svc = SpecIndexService(str(spec_workspace))
        index = svc.build_index()
        assert len(index) == 7  # 4 PLC + 3 Python
        for entry in index:
            assert entry.exists is True
            assert entry.file_path != ""
            assert entry.file_size > 0
            assert entry.line_count > 0

    def test_partial_specs_found(self, partial_workspace: Path) -> None:
        """部分规范文件存在"""
        svc = SpecIndexService(str(partial_workspace))
        index = svc.build_index()
        assert len(index) == 7
        found = [e for e in index if e.exists]
        missing = [e for e in index if not e.exists]
        assert len(found) == 2
        assert len(missing) == 5

    def test_index_sorted_by_stack_and_code(self, spec_workspace: Path) -> None:
        """索引按 (stack, code) 排序"""
        svc = SpecIndexService(str(spec_workspace))
        index = svc.build_index()
        # plc 在前，python 在后
        assert index[0].stack == "plc"
        assert index[0].code == "903"  # 903 < 904 < 905 < 906
        assert index[3].stack == "plc"
        assert index[3].code == "906"
        assert index[4].stack == "python"
        assert index[4].code == "210"

    def test_entry_fields(self, spec_workspace: Path) -> None:
        """索引条目字段完整"""
        svc = SpecIndexService(str(spec_workspace))
        index = svc.build_index()
        entry = next(e for e in index if e.code == "905")
        assert entry.name == "SCL 编程规范"
        assert entry.stack == "plc"
        assert entry.exists is True
        assert entry.file_path.endswith(".md")
        assert "905_" in os.path.basename(entry.file_path)


# ── search 测试 ─────────────────────────────────────────


class TestSearch:
    """search() 测试"""

    def test_empty_keyword_returns_all(self, spec_workspace: Path) -> None:
        """空关键词返回所有规范"""
        svc = SpecIndexService(str(spec_workspace))
        results = svc.search("")
        assert len(results) == 7

    def test_search_by_code(self, spec_workspace: Path) -> None:
        """按编号检索"""
        svc = SpecIndexService(str(spec_workspace))
        results = svc.search("905")
        assert len(results) == 1
        assert results[0].code == "905"

    def test_search_by_name(self, spec_workspace: Path) -> None:
        """按名称检索"""
        svc = SpecIndexService(str(spec_workspace))
        results = svc.search("SCL")
        # 905 SCL 编程规范、904 SCL 注释规范
        assert len(results) == 2
        codes = {r.code for r in results}
        assert codes == {"905", "904"}

    def test_search_by_stack(self, spec_workspace: Path) -> None:
        """按技术栈检索"""
        svc = SpecIndexService(str(spec_workspace))
        results = svc.search("plc")
        assert len(results) == 4
        for r in results:
            assert r.stack == "plc"

    def test_search_case_insensitive(self, spec_workspace: Path) -> None:
        """检索不区分大小写"""
        svc = SpecIndexService(str(spec_workspace))
        results_lower = svc.search("scl")
        results_upper = svc.search("SCL")
        assert len(results_lower) == len(results_upper) == 2

    def test_search_no_match(self, spec_workspace: Path) -> None:
        """无匹配时返回空列表"""
        svc = SpecIndexService(str(spec_workspace))
        results = svc.search("不存在的关键词")
        assert results == []


# ── get_entry 测试 ──────────────────────────────────────


class TestGetEntry:
    """get_entry() 测试"""

    def test_get_existing_entry(self, spec_workspace: Path) -> None:
        """获取存在的规范条目"""
        svc = SpecIndexService(str(spec_workspace))
        entry = svc.get_entry("905")
        assert entry is not None
        assert entry.code == "905"
        assert entry.stack == "plc"
        assert entry.exists is True

    def test_get_nonexistent_code(self, spec_workspace: Path) -> None:
        """获取不存在的编号返回 None"""
        svc = SpecIndexService(str(spec_workspace))
        entry = svc.get_entry("999")
        assert entry is None

    def test_get_entry_for_missing_file(self, partial_workspace: Path) -> None:
        """文件缺失的规范条目 exists=False"""
        svc = SpecIndexService(str(partial_workspace))
        entry = svc.get_entry("904")  # 904 文件不存在
        assert entry is not None
        assert entry.exists is False
        assert entry.file_path == ""


# ── get_spec_content 测试 ───────────────────────────────


class TestGetSpecContent:
    """get_spec_content() 测试"""

    def test_read_content(self, spec_workspace: Path) -> None:
        """读取规范文件内容"""
        svc = SpecIndexService(str(spec_workspace))
        content = svc.get_spec_content("905")
        assert "905" in content
        assert "SCL" in content

    def test_read_nonexistent_code(self, spec_workspace: Path) -> None:
        """读取不存在的规范编号抛 FileNotFoundError"""
        svc = SpecIndexService(str(spec_workspace))
        with pytest.raises(FileNotFoundError, match="未找到规范编号"):
            svc.get_spec_content("999")

    def test_read_missing_file(self, partial_workspace: Path) -> None:
        """读取缺失文件抛 FileNotFoundError"""
        svc = SpecIndexService(str(partial_workspace))
        with pytest.raises(FileNotFoundError, match="规范文件不存在"):
            svc.get_spec_content("904")  # 904 文件不存在


# ── compare 测试 ────────────────────────────────────────


class TestCompare:
    """compare() 测试"""

    def test_compare_different_specs(self, spec_workspace: Path) -> None:
        """对比两个不同的规范"""
        svc = SpecIndexService(str(spec_workspace))
        diff = svc.compare("905", "210")
        assert isinstance(diff, SpecDiffResult)
        assert diff.code1 == "905"
        assert diff.code2 == "210"
        assert diff.file1 != ""
        assert diff.file2 != ""
        assert diff.same is False
        assert len(diff.lines1) > 0
        assert len(diff.lines2) > 0
        # 应有差异行
        assert len(diff.added) > 0 or len(diff.removed) > 0

    def test_compare_same_spec(self, spec_workspace: Path) -> None:
        """对比相同规范返回 same=True"""
        svc = SpecIndexService(str(spec_workspace))
        diff = svc.compare("905", "905")
        assert diff.same is True
        assert diff.added == []
        assert diff.removed == []

    def test_compare_nonexistent_code(self, spec_workspace: Path) -> None:
        """对比不存在的规范编号抛 FileNotFoundError"""
        svc = SpecIndexService(str(spec_workspace))
        with pytest.raises(FileNotFoundError):
            svc.compare("999", "905")

    def test_compare_missing_file(self, partial_workspace: Path) -> None:
        """对比缺失文件抛 FileNotFoundError"""
        svc = SpecIndexService(str(partial_workspace))
        with pytest.raises(FileNotFoundError):
            svc.compare("904", "905")  # 904 文件不存在


# ── get_stats 测试 ──────────────────────────────────────


class TestGetStats:
    """get_stats() 测试"""

    def test_stats_all_found(self, spec_workspace: Path) -> None:
        """所有规范都存在时的统计"""
        svc = SpecIndexService(str(spec_workspace))
        stats = svc.get_stats()
        assert stats["total"] == 7
        assert stats["found"] == 7
        assert stats["missing"] == 0
        assert stats["missing_codes"] == []
        assert stats["by_stack"]["plc"]["found"] == 4
        assert stats["by_stack"]["python"]["found"] == 3

    def test_stats_partial_found(self, partial_workspace: Path) -> None:
        """部分规范存在时的统计"""
        svc = SpecIndexService(str(partial_workspace))
        stats = svc.get_stats()
        assert stats["total"] == 7
        assert stats["found"] == 2
        assert stats["missing"] == 5
        assert len(stats["missing_codes"]) == 5
        assert "904" in stats["missing_codes"]
        assert "211" in stats["missing_codes"]

    def test_stats_structure(self, spec_workspace: Path) -> None:
        """统计结构完整"""
        svc = SpecIndexService(str(spec_workspace))
        stats = svc.get_stats()
        assert set(stats.keys()) == {"total", "found", "missing", "by_stack", "missing_codes"}
        for stack_data in stats["by_stack"].values():
            assert set(stack_data.keys()) == {"total", "found", "missing"}


# ── set_workspace_root 测试 ─────────────────────────────


class TestSetWorkspaceRoot:
    """set_workspace_root() 测试"""

    def test_set_workspace_root(self, tmp_path: Path) -> None:
        """设置工作空间根目录"""
        svc = SpecIndexService()
        assert svc.workspace_root == ""
        svc.set_workspace_root(str(tmp_path))
        assert svc.workspace_root == os.path.abspath(str(tmp_path))

    def test_set_empty_workspace_root(self) -> None:
        """设置空工作空间根目录"""
        svc = SpecIndexService("/some/path")
        svc.set_workspace_root("")
        assert svc.workspace_root == ""
