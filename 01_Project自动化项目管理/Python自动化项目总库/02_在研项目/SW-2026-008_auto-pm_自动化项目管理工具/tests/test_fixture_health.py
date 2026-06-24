"""元测试：检查所有测试 fixture 是否创建了项目标志文件。

背景：ChangeFileLocator._is_project_dir 依赖项目标志文件
（PM_SESSION_*.md / .plc.json / .copier-answers.yml）识别项目目录。
若 fixture 创建了项目目录但缺标志文件，locator 无法找到变更单，
导致测试假通过（if cr is not None: 跳过断言）或假失败（assert None is not None）。

本测试扫描 tests/ 下所有 .py 文件，查找创建项目目录的 fixture，
验证同一 fixture（或其调用的辅助函数）是否创建了项目标志文件。

检测逻辑（V2 改进）：
- 用 AST 分析 mkdir/makedirs 调用检测"创建目录"，替代字符串模式匹配
- 用 AST 分析 write_text/open 调用检测"创建标志文件"
- 递归检查辅助函数调用（最多 2 层深度），避免误报
- SERVICE_PATTERNS 使用单词边界，避免 get_change_request 误匹配 get_change_requests_paths
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

# 项目标志文件模式（用于检测 write_text/open 调用中的文件名）
MARKER_PATTERNS = [
    r"PM_SESSION_",
    r"\.plc\.json",
    r"\.copier-answers",
]

# 需要 ChangeService 的文件才需要项目标志文件（使用单词边界避免误匹配）
SERVICE_PATTERNS = [
    r"\bChangeService\b",
    r"\bchange_service\b",
    r"\bfind_change_file\b",
    r"\btransition_status\b",
    r"\bget_change_request\b",
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


# ── AST 分析工具 ──────────────────────────────────────────


def _extract_functions(source: str) -> dict[str, ast.FunctionDef]:
    """提取源码中所有函数定义，返回 {函数名: AST 节点}。"""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {}
    return {
        node.name: node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def _extract_fixtures(source: str) -> list[tuple[str, ast.FunctionDef]]:
    """提取源码中所有 fixture 函数和辅助函数，返回 (函数名, AST 节点) 列表。"""
    funcs = _extract_functions(source)
    fixtures: list[tuple[str, ast.FunctionDef]] = []
    # 排除创建规范文件/报告等非项目目录的辅助函数
    exclude_hints = ("spec_file", "spec_dir", "create_spec", "report", "scan_log")
    for name, node in funcs.items():
        # 检查是否是 fixture（有 @pytest.fixture 装饰器）
        is_fixture = any(
            isinstance(d, ast.Attribute) and d.attr == "fixture"
            or isinstance(d, ast.Name) and d.id == "fixture"
            for d in node.decorator_list
        )
        # 也检查辅助函数（非 fixture 但创建工作空间/项目）
        if not is_fixture:
            name_lower = name.lower()
            name_hints = ("workspace", "create_chg", "build_chg", "_create")
            if not any(hint in name_lower for hint in name_hints):
                continue
            # 排除创建规范文件/报告等非项目目录的辅助函数
            if any(hint in name_lower for hint in exclude_hints):
                continue
        fixtures.append((name, node))
    return fixtures


def _calls_mkdir(node: ast.FunctionDef) -> bool:
    """检查函数 AST 是否包含 mkdir/makedirs 调用（创建目录）。"""
    for child in ast.walk(node):
        if isinstance(child, ast.Attribute) and child.attr in ("mkdir", "makedirs"):
            return True
    return False


def _extract_strings_from_node(node: ast.AST) -> list[str]:
    """从 AST 节点中提取所有字符串值（包括 f-string 的字面量部分）。"""
    strings: list[str] = []
    for sub in ast.walk(node):
        if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
            strings.append(sub.value)
        elif isinstance(sub, ast.JoinedStr):
            # f-string：提取每个 FormattedValue 之间的字面量部分
            for value in sub.values:
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    strings.append(value.value)
    return strings


def _creates_marker_file(node: ast.FunctionDef) -> bool:
    """检查函数 AST 是否创建项目标志文件。

    检测 write_text/open 调用中是否包含标志文件名模式（包括 f-string）。
    """
    for child in ast.walk(node):
        # 检测 write_text 调用（Path 对象方法）
        if isinstance(child, ast.Attribute) and child.attr == "write_text":
            # 检查调用链中的所有字符串（包括 f-string 字面量部分）
            for s in _extract_strings_from_node(child):
                if any(re.search(p, s) for p in MARKER_PATTERNS):
                    return True
        # 检测 open 调用中的标志文件名
        if isinstance(child, ast.Call):
            func = child.func
            # open(...) 调用
            if isinstance(func, ast.Name) and func.id == "open":
                for s in _extract_strings_from_node(child):
                    if any(re.search(p, s) for p in MARKER_PATTERNS):
                        return True
            # os.path.join(...) 中包含标志文件名
            if isinstance(func, ast.Attribute) and func.attr == "join":
                for s in _extract_strings_from_node(child):
                    if any(re.search(p, s) for p in MARKER_PATTERNS):
                        return True
    return False


def _get_called_functions(node: ast.FunctionDef) -> list[str]:
    """提取函数 AST 中调用的所有函数名（用于递归检查辅助函数）。"""
    called: list[str] = []
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            func = child.func
            if isinstance(func, ast.Name):
                called.append(func.id)
            elif isinstance(func, ast.Attribute):
                called.append(func.attr)
    return called


def _fixture_creates_dir_with_marker(
    node: ast.FunctionDef,
    all_funcs: dict[str, ast.FunctionDef],
    depth: int = 0,
    max_depth: int = 2,
) -> tuple[bool, bool]:
    """递归检查函数是否创建目录且创建标志文件。

    返回 (creates_dir, has_marker)。
    递归检查调用的辅助函数（最多 max_depth 层）。
    """
    creates_dir = _calls_mkdir(node)
    has_marker = _creates_marker_file(node)

    # 如果当前函数已创建目录且有标志文件，直接返回
    if creates_dir and has_marker:
        return (True, True)

    # 递归检查调用的辅助函数
    if depth < max_depth:
        for called_name in _get_called_functions(node):
            if called_name in all_funcs and called_name != node.name:
                sub_dir, sub_marker = _fixture_creates_dir_with_marker(
                    all_funcs[called_name], all_funcs, depth + 1, max_depth
                )
                creates_dir = creates_dir or sub_dir
                has_marker = has_marker or sub_marker

    return (creates_dir, has_marker)


# ── 兼容旧接口（保留但不再使用字符串模式匹配）──────────────


def _fixture_creates_project_dir(source: str) -> bool:
    """[已废弃] 检查源码是否包含创建项目目录的代码模式。"""
    return False  # 不再使用字符串模式匹配


def _fixture_has_marker(source: str) -> bool:
    """[已废弃] 检查源码是否包含创建项目标志文件的代码模式。"""
    return False  # 不再使用字符串模式匹配


class TestFixtureHealth:
    """元测试：验证所有测试 fixture 的项目标志文件完整性。"""

    @pytest.fixture
    def tests_dir(self) -> Path:
        """测试目录"""
        return Path(__file__).parent

    @pytest.fixture(autouse=True)
    def _setup(self, tests_dir: Path) -> None:
        self.tests_dir = tests_dir

    def test_all_fixtures_have_project_markers(self, tests_dir: Path) -> None:
        """扫描使用 ChangeService 的测试文件，确保创建项目目录的 fixture 同时创建了项目标志文件。

        V2 改进：用 AST 分析 mkdir/makedirs 调用检测"创建目录"，
        递归检查辅助函数调用，避免字符串模式匹配的误报。

        本测试为 WARN 级别：发现问题时输出警告但不阻断测试套件，
        因为这些是技术债需要逐步修复。
        """
        test_files = _find_test_files(tests_dir)
        assert len(test_files) > 0, "未找到测试文件"

        violations: list[str] = []

        for file_path in test_files:
            rel_path = file_path.relative_to(tests_dir)
            source = file_path.read_text(encoding="utf-8")

            # 筛选：文件必须使用 ChangeService 相关 API
            if not any(re.search(p, source) for p in SERVICE_PATTERNS):
                continue

            # 提取所有函数（fixture + 辅助函数）
            all_funcs = _extract_functions(source)
            if not all_funcs:
                continue

            # 提取 fixture 和辅助函数
            fixtures = _extract_fixtures(source)

            for func_name, func_node in fixtures:
                # 递归检查：是否创建目录且创建标志文件
                creates_dir, has_marker = _fixture_creates_dir_with_marker(
                    func_node, all_funcs
                )

                # 只报告"创建目录但缺标志文件"的 fixture
                if creates_dir and not has_marker:
                    violations.append(
                        f"  - {rel_path}::{func_name}"
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
