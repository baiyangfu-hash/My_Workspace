"""元测试：检查所有测试 fixture 是否创建了项目标志文件。

背景：ChangeFileLocator._is_project_dir 依赖项目标志文件
（PM_SESSION_*.md / .plc.json / .copier-answers.yml）识别项目目录。
若 fixture 创建了项目目录但缺标志文件，locator 无法找到变更单，
导致测试假通过（if cr is not None: 跳过断言）或假失败（assert None is not None）。

本测试扫描 tests/ 下所有 .py 文件，查找创建项目目录的 fixture，
验证同一 fixture 是否创建了项目标志文件。
"""

from __future__ import annotations

import ast
import os
import re
from pathlib import Path

import pytest

# 项目标志文件模式
MARKER_PATTERNS = [
    r"PM_SESSION_",
    r"\.plc\.json",
    r"\.copier-answers",
]

# 创建项目目录的模式（表示 fixture 在构建临时项目结构）
PROJECT_DIR_PATTERNS = [
    r'00_项目管理',
    r'04_变更管理',
    r'01_变更单',
    r'CHG-',
]


def _find_test_files(tests_dir: Path) -> list[Path]:
    """递归查找 tests/ 下所有 .py 文件（排除 __pycache__ 和 helpers/）。"""
    return [
        p
        for p in tests_dir.rglob("*.py")
        if "__pycache__" not in str(p)
        and p.name != "__init__.py"
        and p.name != "test_fixture_health.py"  # 排除自身
        and "helpers" not in p.parts  # 排除辅助目录
    ]


# 需要 ChangeService 的文件才需要项目标志文件
SERVICE_PATTERNS = [
    r"ChangeService",
    r"change_service",
    r"find_change_file",
    r"transition_status",
    r"get_change_request",
]


def _fixture_creates_project_dir(source: str) -> bool:
    """检查源码是否包含创建项目目录的代码模式。"""
    return any(re.search(p, source) for p in PROJECT_DIR_PATTERNS)


def _fixture_has_marker(source: str) -> bool:
    """检查源码是否包含创建项目标志文件的代码模式。"""
    return any(re.search(p, source) for p in MARKER_PATTERNS)


def _extract_fixtures(source: str) -> list[tuple[str, str]]:
    """提取源码中所有 fixture 函数，返回 (函数名, 函数源码) 列表。"""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    lines = source.splitlines()
    fixtures: list[tuple[str, str]] = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        # 检查是否是 fixture（有 @pytest.fixture 装饰器）
        is_fixture = any(
            isinstance(d, ast.Attribute) and d.attr == "fixture"
            or isinstance(d, ast.Name) and d.id == "fixture"
            for d in node.decorator_list
        )

        # 也检查辅助函数（非 fixture 但创建项目目录的 helper）
        if not is_fixture:
            # 检查函数名是否暗示创建工作空间/项目
            name_hints = ("workspace", "create_chg", "build_chg", "_create")
            if not any(hint in node.name.lower() for hint in name_hints):
                continue

        # 提取函数源码
        start = node.lineno - 1
        end = node.end_lineno if node.end_lineno else len(lines)
        func_source = "\n".join(lines[start:end])
        fixtures.append((node.name, func_source))

    return fixtures


class TestFixtureHealth:
    """元测试：验证所有测试 fixture 的项目标志文件完整性。"""

    @pytest.fixture(autouse=True)
    def _setup(self, tests_dir: Path) -> None:
        self.tests_dir = tests_dir

    def test_all_fixtures_have_project_markers(self, tests_dir: Path) -> None:
        """扫描使用 ChangeService 的测试文件，确保创建项目目录的 fixture 同时创建了项目标志文件。
        
        本测试为 WARN 级别：发现问题时输出警告但不阻断测试套件，
        因为这些是技术债需要逐步修复。
        """
        test_files = _find_test_files(tests_dir)
        assert len(test_files) > 0, "未找到测试文件"

        violations: list[str] = []

        for file_path in test_files:
            rel_path = file_path.relative_to(tests_dir)
            source = file_path.read_text(encoding="utf-8")

            if not any(re.search(p, source) for p in SERVICE_PATTERNS):
                continue

            if not _fixture_creates_project_dir(source):
                continue

            if _fixture_has_marker(source):
                fixtures = _extract_fixtures(source)
                for func_name, func_source in fixtures:
                    if _fixture_creates_project_dir(func_source) and not _fixture_has_marker(func_source):
                        violations.append(
                            f"  - {rel_path}::{func_name}"
                        )
            else:
                violations.append(
                    f"  - {rel_path}"
                )

        if violations:
            import warnings
            msg = "\n".join(violations)
            warnings.warn(
                f"\n[FIXTURE HEALTH WARN] 发现 {len(violations)} 个 fixture 缺项目标志文件：\n{msg}\n"
                f"这些 fixture 可能导致 ChangeFileLocator 无法定位项目目录，"
                f"建议逐步修复以避免假通过/假失败。"
            )

    def test_no_conditional_assertion_skips(self, tests_dir: Path) -> None:
        """检查是否存在 `if cr is not None:` 类条件断言跳过（假通过模式）。
        
        本测试为 WARN 级别：发现问题时输出警告但不阻断测试套件，
        因为这些是技术债需要逐步修复。
        """
        test_files = _find_test_files(tests_dir)
        violations: list[str] = []

        pattern = re.compile(r"if\s+\w+\s+is\s+not\s+None\s*:", re.MULTILINE)

        for file_path in test_files:
            rel_path = file_path.relative_to(tests_dir)
            source = file_path.read_text(encoding="utf-8")
            matches = pattern.findall(source)
            if matches:
                violations.append(
                    f"  - {rel_path}（{len(matches)}处）"
                )

        if violations:
            import warnings
            msg = "\n".join(violations)
            warnings.warn(
                f"\n[FIXTURE HEALTH WARN] 发现 {len(violations)} 个文件存在条件断言跳过模式：\n{msg}\n"
                f"建议改为 `assert x is not None` 暴露 fixture 缺陷，避免假通过。"
            )
