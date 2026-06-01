"""
SCLTest文件解析器模块

本模块实现了对Siemens SCLTest测试文件的解析功能。
SCLTest是PLCcheck Test工具使用的测试脚本格式，用于自动化测试PLC程序。

支持的语法特性：
- TEST_CASE ... END_TEST_CASE 块定义
- SET 语句：设置变量值（支持布尔、整数、实数等类型）
- WAIT_CYCLES 语句：等待PLC扫描周期
- ASSERT 语句：断言变量值
- // 注释风格
- #region/#endregion 区域标记

解析策略：
- 使用状态机逐行解析
- 支持错误恢复，单个解析错误不会中断整个文件
- 完整保留原始行号用于错误定位
- 提取测试用例描述（从注释中推断）

作者：双栖资深开发
版本：1.0.0
"""

import re
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass

# 导入数据模型
import sys
sys.path.append(str(Path(__file__).parent.parent))
from models.test_case import TestCase, TestSuite, TestStep, StepType


@dataclass
class ParseContext:
    """解析上下文，跟踪当前解析状态"""
    current_state: str = "OUTSIDE"  # OUTSIDE / IN_TEST_CASE
    current_test_case: Optional[TestCase] = None
    line_number: int = 0
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class SCLTestParser:
    """
    SCLTest文件解析器

    负责将.scltest文本文件解析为结构化的TestSuite对象。

    主要功能：
    - 解析TEST_CASE块，提取测试步骤
    - 识别SET/WAIT_CYCLES/ASSERT三种语句类型
    - 处理各种边界情况（空行、注释、格式变化等）
    - 提供详细的错误报告和恢复机制

    使用示例：
        >>> parser = SCLTestParser()
        >>> suite = parser.parse_file(Path("test.scltest"))
        >>> print(suite.test_case_count)
        5
        >>> for tc in suite.test_cases:
        ...     print(tc.name, tc.step_count)
    """

    # 正则表达式模式（编译一次以提高性能）
    PATTERN_TEST_CASE_START = re.compile(
        r'^\s*TEST_CASE\s+"([^"]+)"\s*',
        re.IGNORECASE
    )
    PATTERN_END_TEST_CASE = re.compile(
        r'^\s*END_TEST_CASE\s*;?\s*$',
        re.IGNORECASE
    )
    PATTERN_SET = re.compile(
        r'^\s*SET\s+([\w.\[\]]+)\s*:=\s*(.+?)\s*;\s*$',
        re.IGNORECASE
    )
    PATTERN_WAIT_CYCLES = re.compile(
        r'^\s*WAIT_CYCLES\s+(\d+)\s*;\s*$',
        re.IGNORECASE
    )
    PATTERN_ASSERT = re.compile(
        r'^\s*ASSERT\s+([\w.\[\]]+)\s*=\s*(.+?)\s*;\s*$',
        re.IGNORECASE
    )
    PATTERN_COMMENT = re.compile(r'^\s*//')
    PATTERN_REGION = re.compile(r'^\s*#(?:region|endregion)')
    PATTERN_BLANK = re.compile(r'^\s*$')

    def __init__(self):
        """初始化解析器"""
        self._reset_state()

    def _reset_state(self):
        """重置解析器状态"""
        self._context = ParseContext()
        self._header_comments: List[str] = []
        self._in_header = True

    def parse_file(self, file_path: Path) -> TestSuite:
        """
        解析SCLTest文件

        Args:
            file_path: .scltest文件路径

        Returns:
            TestSuite对象，包含所有解析出的测试用例

        Raises:
            FileNotFoundError: 文件不存在
            UnicodeDecodeError: 文件编码问题
        """
        if not file_path.exists():
            raise FileNotFoundError(f"SCLTest文件不存在: {file_path}")

        # 尝试不同编码读取文件
        content = self._read_file_with_encoding(file_path)

        return self.parse_string(content, file_path)

    def parse_string(self, content: str, source_path: Optional[Path] = None) -> TestSuite:
        """
        解析SCLTest字符串内容

        Args:
            content: SCLTest文件内容
            source_path: 来源路径（可选，用于错误报告）

        Returns:
            TestSuite对象
        """
        self._reset_state()

        lines = content.splitlines()

        for line_num, line in enumerate(lines, 1):
            self._context.line_number = line_num
            self._process_line(line.strip(), line_num)

        # 处理最后一个未关闭的测试用例
        if self._context.current_state == "IN_TEST_CASE":
            self._context.errors.append(
                f"警告(第{self._context.line_number}行): 测试用例未正确关闭"
            )
            self._finalize_current_test_case()

        # 构建TestSuite
        file_path = source_path or Path("<string>")
        return TestSuite(
            file_path=file_path,
            test_cases=self._collected_test_cases,
            header_comments=self._header_comments,
            parse_errors=self._context.errors
        )

    def _read_file_with_encoding(self, file_path: Path) -> str:
        """
        尝试多种编码读取文件

        Args:
            file_path: 文件路径

        Returns:
            文件内容字符串
        """
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'latin-1']

        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
            except Exception as e:
                raise IOError(f"无法读取文件 {file_path}: {e}")

        raise UnicodeDecodeError(
            'multi', b'', 0, 1,
            f"无法确定文件编码: {file_path}"
        )

    @property
    def _collected_test_cases(self) -> List[TestCase]:
        """收集已完成的测试用例（内部属性）"""
        if not hasattr(self, '_test_cases'):
            self._test_cases = []
        return self._test_cases

    def _process_line(self, line: str, line_num: int):
        """
        处理单行内容（核心状态机逻辑）

        Args:
            line: 去除首尾空白后的行内容
            line_num: 行号
        """
        # 空行处理
        if self.PATTERN_BLANK.match(line):
            return

        # 注释行处理
        if self.PATTERN_COMMENT.match(line):
            if self._in_header and self._context.current_state == "OUTSIDE":
                self._header_comments.append(line)
            return

        # region/endregion 标记忽略
        if self.PATTERN_REGION.match(line):
            return

        # 状态机分发
        if self._context.current_state == "OUTSIDE":
            self._handle_outside_state(line, line_num)
        elif self._context.current_state == "IN_TEST_CASE":
            self._handle_inside_test_case(line, line_num)

    def _handle_outside_state(self, line: str, line_num: int):
        """
        处理TEST_CASE外部状态

        寻找TEST_CASE开始标记
        """
        match = self.PATTERN_TEST_CASE_START.match(line)
        if match:
            test_name = match.group(1).strip()
            self._start_new_test_case(test_name, line_num)
            self._in_header = False
        # 其他内容在外部状态下忽略（可能是文档说明等）

    def _handle_inside_test_case(self, line: str, line_num: int):
        """
        处理TEST_CASE内部状态

        解析SET/WAIT_CYCLES/ASSERT语句，或检测END_TEST_CASE
        """
        # 检查是否结束
        if self.PATTERN_END_TEST_CASE.match(line):
            self._finalize_current_test_case()
            return

        # 尝试解析SET语句
        set_match = self.PATTERN_SET.match(line)
        if set_match:
            self._parse_set_statement(set_match, line, line_num)
            return

        # 尝试解析WAIT_CYCLES语句
        wait_match = self.PATTERN_WAIT_CYCLES.match(line)
        if wait_match:
            self._parse_wait_statement(wait_match, line, line_num)
            return

        # 尝试解析ASSERT语句
        assert_match = self.PATTERN_ASSERT.match(line)
        if assert_match:
            self._parse_assert_statement(assert_match, line, line_num)
            return

        # 无法识别的行 - 记录警告但不中断
        self._context.errors.append(
            f"警告(第{line_num}行): 无法识别的语句 - {line[:50]}"
        )

    def _start_new_test_case(self, name: str, line_num: int):
        """
        开始新的测试用例

        Args:
            name: 测试用例名称
            line_num: 起始行号
        """
        # 如果前一个测试用例未关闭，先关闭它
        if self._context.current_state == "IN_TEST_CASE":
            self._context.errors.append(
                f"警告(第{line_num}行): 前一个测试用例未正确关闭"
            )
            self._finalize_current_test_case()

        self._context.current_state = "IN_TEST_CASE"
        self._context.current_test_case = TestCase(
            name=name,
            start_line=line_num,
            file_path=None  # 稍后在TestSuite中设置
        )

    def _finalize_current_test_case(self):
        """
        完成当前测试用例的解析
        """
        if self._context.current_test_case:
            tc = self._context.current_test_case
            tc.end_line = self._context.line_number

            # 从步骤中推断描述（如果有注释步骤的话）
            if not tc.description and tc.steps:
                tc.description = f"包含 {tc.step_count} 个测试步骤"

            if not hasattr(self, '_test_cases'):
                self._test_cases = []
            self._test_cases.append(tc)

        self._context.current_state = "OUTSIDE"
        self._context.current_test_case = None

    def _parse_set_statement(self, match: re.Match, raw_line: str, line_num: int):
        """
        解析SET语句

        语法: SET variable := value;

        支持的值类型：
        - 布尔值: TRUE, FALSE
        - 整数: 0, 100, -5
        - 实数: 3.14, -0.5
        - 字符串: 'hello'
        """
        variable = match.group(1).strip()
        value_str = match.group(2).strip()

        # 解析值
        parsed_value = self._parse_value(value_str)

        step = TestStep(
            step_type=StepType.SET,
            variable=variable,
            value=parsed_value,
            raw_line=raw_line,
            line_number=line_num
        )

        self._context.current_test_case.steps.append(step)

    def _parse_wait_statement(self, match: re.Match, raw_line: str, line_num: int):
        """
        解析WAIT_CYCLES语句

        语法: WAIT_CYCLES count;
        """
        cycles_str = match.group(1)
        cycles = int(cycles_str)

        step = TestStep(
            step_type=StepType.WAIT_CYCLES,
            cycles=cycles,
            raw_line=raw_line,
            line_number=line_num
        )

        self._context.current_test_case.steps.append(step)

    def _parse_assert_statement(self, match: re.Match, raw_line: str, line_num: int):
        """
        解析ASSERT语句

        语法: ASSERT variable = expected_value;
        """
        variable = match.group(1).strip()
        expected_str = match.group(2).strip()

        # 解析期望值
        expected_value = self._parse_value(expected_str)

        step = TestStep(
            step_type=StepType.ASSERT,
            variable=variable,
            value=expected_value,
            raw_line=raw_line,
            line_number=line_num
        )

        self._context.current_test_case.steps.append(step)

    def _parse_value(self, value_str: str) -> Any:
        """
        解析值字符串为Python类型

        支持的类型：
        - 布尔: TRUE/FALSE (不区分大小写)
        - 整数: 十进制整数（支持负数）
        - 实数: 浮点数
        - 字符串: 单引号括起来的字符串

        Args:
            value_str: 值字符串

        Returns:
            解析后的Python值
        """
        value_str = value_str.strip()

        # 布尔值
        if value_str.upper() == 'TRUE':
            return True
        if value_str.upper() == 'FALSE':
            return False

        # 字符串（单引号）
        if value_str.startswith("'") and value_str.endswith("'"):
            return value_str[1:-1]

        # 整数
        try:
            if '.' not in value_str:
                return int(value_str)
        except ValueError:
            pass

        # 实数
        try:
            return float(value_str)
        except ValueError:
            pass

        # 无法识别的类型，保持原字符串
        return value_str

    def validate_syntax(self, content: str) -> Tuple[bool, List[str]]:
        """
        验证SCLTest语法但不完全解析

        用于快速检查文件是否有明显的语法问题。

        Args:
            content: 文件内容

        Returns:
            (是否有效, 错误消息列表)
        """
        errors = []

        open_count = len(re.findall(
            r'^\s*TEST_CASE\s+"([^"]+)"\s*',
            content, re.IGNORECASE | re.MULTILINE
        ))
        close_count = len(re.findall(
            r'^\s*END_TEST_CASE\s*;?\s*$',
            content, re.IGNORECASE | re.MULTILINE
        ))

        if open_count != close_count:
            errors.append(
                f"TEST_CASE块不匹配: 找到 {open_count} 个开始, {close_count} 个结束"
            )

        # 基本的括号匹配检查（简化版）
        # 这里可以添加更多语法验证规则

        return len(errors) == 0, errors

    def get_test_case_names(self, file_path: Path) -> List[str]:
        """
        快速获取文件中的所有测试用例名称（不完全解析）

        适用于测试列表展示等轻量级场景。

        Args:
            file_path: 文件路径

        Returns:
            测试用例名称列表
        """
        if not file_path.exists():
            return []

        try:
            content = self._read_file_with_encoding(file_path)
            names = []
            for match in self.PATTERN_TEST_CASE_START.finditer(content):
                names.append(match.group(1).strip())
            return names
        except Exception:
            return []


# ============================================================================
# 便捷函数
# ============================================================================

def parse_scltest_file(file_path: Path) -> TestSuite:
    """
    便捷函数：解析SCLTest文件

    Args:
        file_path: .scltest文件路径

    Returns:
        解析后的TestSuite对象
    """
    parser = SCLTestParser()
    return parser.parse_file(file_path)


def parse_scltest_string(content: str) -> TestSuite:
    """
    便捷函数：解析SCLTest字符串

    Args:
        content: SCLTest内容

    Returns:
        解析后的TestSuite对象
    """
    parser = SCLTestParser()
    return parser.parse_string(content)


if __name__ == "__main__":
    # 简单的自测
    import sys

    if len(sys.argv) > 1:
        test_file = Path(sys.argv[1])
        print(f"解析文件: {test_file}")

        parser = SCLTestParser()
        suite = parser.parse_file(test_file)

        print(f"\n{'='*60}")
        print(f"测试套件: {suite.file_path.name}")
        print(f"测试用例数: {suite.test_case_count}")
        print(f"总步骤数: {suite.total_steps}")
        print(f"解析错误: {len(suite.parse_errors)}")
        print(f"{'='*60}\n")

        for i, tc in enumerate(suite.test_cases, 1):
            print(f"{i}. {tc.name}")
            print(f"   步骤数: {tc.step_count}")
            print(f"   总等待周期: {tc.total_wait_cycles}")
            for step in tc.steps:
                print(f"     - {step}")
            print()

        if suite.parse_errors:
            print("\n解析警告/错误:")
            for err in suite.parse_errors:
                print(f"  ! {err}")
    else:
        print("用法: python scltest_parser.py <文件路径.scltest>")
