# -*- coding: utf-8 -*-
"""
语法检查器模块

实现PLC结构化文本(ST)代码的语法规范检查，包含5条核心规则：
- SYNTAX_001: VAR_TEMP位置验证
- SYNTAX_002: 控制结构配对检测（IF/END_IF, FOR/END_FOR等）
- SYNTAX_003: FB/函数块结构完整性
- SYNTAX_004: 语句分号检测
- SYNTAX_005: 类型合法性验证

核心算法：
1. 使用栈数据结构处理嵌套控制结构的配对验证
2. 状态机模式处理多行注释和字符串字面量
3. 正则表达式模式匹配进行语法元素识别
"""

import re
from typing import List, Dict, Optional, Any, Tuple, Set
from dataclasses import dataclass

from src.checkers.base_checker import BaseChecker, RuleInfo, Severity
from src.models.check_result import Violation
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


# ============================================================================
# 常量定义
# ============================================================================

# IEC 61131-3 标准数据类型集合
IEC_STANDARD_TYPES: Set[str] = {
    # 布尔类型
    "BOOL",
    # 整数类型
    "SINT", "USINT", "INT", "UINT", "DINT", "UDINT", "LINT", "ULINT",
    # 浮点类型
    "REAL", "LREAL",
    # 时间类型
    "TIME", "DATE", "TIME_OF_DAY", "TOD", "DATE_AND_TIME", "DT",
    # 字符串类型
    "STRING", "WSTRING",
    # 位串类型
    "BYTE", "WORD", "DWORD", "LWORD",
}

# 控制结构关键字配对映射
CONTROL_STRUCTURE_PAIRS: Dict[str, str] = {
    "IF": "END_IF",
    "CASE": "END_CASE",
    "FOR": "END_FOR",
    "WHILE": "END_WHILE",
    "REPEAT": "END_REPEAT",
    "WITH": "END_WITH",
}

# VAR声明块类型
VAR_BLOCK_TYPES: Set[str] = {
    "VAR", "VAR_INPUT", "VAR_OUTPUT", "VAR_IN_OUT",
    "VAR_TEMP", "VAR_GLOBAL", "VAR_EXTERNAL", "VAR_ACCESS",
    "VAR_STATIC",
}


@dataclass
class _ControlStructureInfo:
    """控制结构信息数据类，用于栈中存储"""
    keyword: str           # 开始关键字（如 IF, FOR）
    line_number: int       # 所在行号
    expected_end: str      # 期望的结束关键字
    nesting_level: int     # 嵌套层级


# ============================================================================
# SyntaxChecker 主类
# ============================================================================

class SyntaxChecker(BaseChecker):
    """
    PLC ST语法规范检查器

    检查范围：
    1. VAR_TEMP声明必须在正确位置
    2. 控制结构必须正确配对和嵌套
    3. FB/函数块必须包含完整的VAR_INPUT/VAR_OUTPUT/VAR结构
    4. 赋值语句必须以分号结尾
    5. 变量类型必须是合法的IEC标准类型或用户自定义类型

    Usage:
        checker = SyntaxChecker()
        violations = checker.check(source_code, file_path="main.st")
    """

    def __init__(self):
        """初始化语法检查器，注册所有规则"""
        super().__init__(
            rule_info=RuleInfo(
                rule_id="SYNTAX_CHECKER",
                name="ST语法规范检查器",
                description="检查PLC结构化文本代码的语法规范性",
                category="syntax",
                severity=Severity.WARNING,
                tags=["syntax", "structure", "st", "iec61131"],
            )
        )
        logger.info("语法检查器初始化完成")

    def check(
        self,
        source_code: str,
        file_path: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Violation]:
        """
        执行所有语法规则检查

        Args:
            source_code: 待检查的ST源代码
            file_path: 源文件路径
            context: 上下文信息（可选），可包含：
                - user_types: 用户自定义类型列表
                - is_function_block: 是否为FB程序组织单元

        Returns:
            List[Violation]: 发现的所有违规记录列表
        """
        violations: List[Violation] = []

        # 输入验证
        if not source_code or not isinstance(source_code, str):
            logger.warning("输入源代码为空或类型错误")
            return violations

        try:
            lines = source_code.splitlines()

            # 提取上下文信息
            user_types: Set[str] = set()
            is_fb: bool = False
            if context:
                user_types = set(context.get("user_types", []))
                is_fb = context.get("is_function_block", False)

            # 执行各项检查
            violations.extend(
                self._check_var_temp_position(lines, file_path)
            )
            violations.extend(
                self._check_control_structures(lines, file_path)
            )
            violations.extend(
                self._check_fb_structure(lines, file_path, is_fb)
            )
            violations.extend(
                self._check_statement_terminators(lines, file_path)
            )
            violations.extend(
                self._check_type_validity(lines, file_path, user_types)
            )

            logger.debug(
                f"语法检查完成: 文件={file_path}, "
                f"发现{len(violations)}个违规"
            )

        except Exception as e:
            logger.error(f"语法检查过程发生异常: {e}", exc_info=True)
            # 返回已发现的违规，不中断整个检查流程

        return violations

    # =====================================================================
    # 规则 SYNTAX_001: VAR_TEMP位置验证
    # =====================================================================

    def _check_var_temp_position(
        self,
        lines: List[str],
        file_path: str,
    ) -> List[Violation]:
        """
        检查VAR_TEMP声明的位置是否正确

        规则说明：
        - VAR_TEMP只能在FUNCTION或FUNCTION_BLOCK内部使用
        - VAR_TEMP必须位于其他VAR声明之后
        - 不能出现在PROGRAM POU中（PROGRAM应使用VAR）

        Args:
            lines: 代码行列表
            file_path: 文件路径

        Returns:
            List[Violation]: 违规记录列表
        """
        violations: List[Violation] = []
        pou_type: Optional[str] = None
        var_temp_found: bool = False
        var_temp_line: int = 0
        other_var_after_temp: bool = False

        # 正则表达式：匹配POU声明
        # 分组说明：
        #   (group 1): POU类型关键词 (FUNCTION|FUNCTION_BLOCK|PROGRAM)
        #   (group 2): POU名称标识符
        pou_pattern = re.compile(
            r'^\s*(FUNCTION|FUNCTION_BLOCK|PROGRAM)\s+'
            r'(\w+)\s*',
            re.IGNORECASE
        )

        # 正则表达式：匹配VAR声明块开始
        # 分组说明：
        #   (group 1): 完整的VAR声明类型 (如 VAR_INPUT, VAR_TEMP)
        var_decl_pattern = re.compile(
            r'^\s*(VAR(?:_\w+)?)\s*$',
            re.IGNORECASE
        )

        for line_num, line in enumerate(lines, start=1):
            stripped = line.strip()

            # 检测POU类型
            pou_match = pou_pattern.match(line)
            if pou_match:
                pou_type = pou_match.group(1).upper()

            # 检测VAR_TEMP声明
            var_match = var_decl_pattern.match(line)
            if var_match:
                var_type = var_match.group(1).upper()

                if var_type == "VAR_TEMP":
                    var_temp_found = True
                    var_temp_line = line_num

                    # 检查POU类型兼容性
                    if pou_type == "PROGRAM":
                        violations.append(Violation(
                            rule_id="SYNTAX_001",
                            severity=Severity.ERROR,
                            message=(
                                "VAR_TEMP不能用于PROGRAM类型的POU。"
                                "PROGRAM应使用普通VAR声明。"
                            ),
                            file_path=file_path,
                            line_number=line_num,
                            column=len(line) - len(stripped) + 1,
                            suggestion=(
                                "将VAR_TEMP改为VAR，或将POU类型改为"
                                "FUNCTION/FUNCTION_BLOCK"
                            ),
                            code_snippet=stripped,
                        ))
                elif var_temp_found and var_type != "END_VAR":
                    # VAR_TEMP之后出现了其他VAR声明
                    other_var_after_temp = True
                    violations.append(Violation(
                        rule_id="SYNTAX_001",
                        severity=Severity.WARNING,
                        message=(
                            f"VAR_TEMP声明(第{var_temp_line}行)之后"
                            f"出现了{var_type}声明。"
                            f"VAR_TEMP应放在所有VAR声明的最后。"
                        ),
                        file_path=file_path,
                        line_number=line_num,
                        column=len(line) - len(stripped) + 1,
                        suggestion=(
                            "调整VAR声明顺序，确保VAR_TEMP位于最后"
                        ),
                        code_snippet=stripped,
                    ))

        return violations

    # =====================================================================
    # 规则 SYNTAX_002: 控制结构配对检测
    # =====================================================================

    def _check_control_structures(
        self,
        lines: List[str],
        file_path: str,
    ) -> List[Violation]:
        """
        使用栈算法检查控制结构的配对和嵌套

        核心算法说明：
        1. 遍历每一行代码
        2. 识别控制结构开始关键字（IF, CASE, FOR等）并压入栈
        3. 识别结束关键字（END_IF等）并与栈顶元素匹配
        4. 如果不匹配则报告违规
        5. 遍历结束后如果栈非空则报告未闭合的结构

        支持的控制结构：
        - IF ... END_IF
        - CASE ... END_CASE
        - FOR ... END_FOR
        - WHILE ... END_WHILE
        - REPEAT ... END_REPEAT
        - WITH ... END_WITH

        Args:
            lines: 代码行列表
            file_path: 文件路径

        Returns:
            List[Violation]: 违规记录列表
        """
        violations: List[Violation] = []
        stack: List[_ControlStructureInfo] = []
        in_comment: bool = False          # 是否在多行注释中
        in_string: bool = False           # 是否在字符串字面量中
        string_char: str = ""             # 字符串引号字符

        # 正则表达式：匹配控制结构开始关键字
        # 分组说明：
        #   (group 1): 控制结构关键字 (IF, CASE, FOR, WHILE, REPEAT, WITH)
        # 使用单词边界确保精确匹配
        control_start_pattern = re.compile(
            r'\b(IF|CASE|FOR|WHILE|REPEAT|WITH)\b',
            re.IGNORECASE
        )

        # 正则表达式：匹配控制结构结束关键字
        # 分组说明：
        #   (group 1): 结束关键字 (END_IF, END_CASE等)
        control_end_pattern = re.compile(
            r'\b(END_(?:IF|CASE|FOR|WHILE|REPEAT|WITH))\b',
            re.IGNORECASE
        )

        for line_num, line in enumerate(lines, start=1):
            # 状态机：处理注释和字符串状态
            line, in_comment, in_string, string_char = (
                self._process_line_state(
                    line, in_comment, in_string, string_char
                )
            )

            # 跳过注释行和纯注释内容
            if in_comment or line.strip().startswith("(*"):
                continue

            pos = 0
            line_length = len(line)

            while pos < line_length:
                # 查找下一个控制结构开始
                start_match = control_start_pattern.search(line, pos)

                # 查找下一个控制结构结束
                end_match = control_end_pattern.search(line, pos)

                # 确定先出现的是哪个
                if start_match and end_match:
                    if start_match.start() < end_match.start():
                        # 先出现开始关键字
                        keyword = start_match.group(1).upper()
                        expected_end = CONTROL_STRUCTURE_PAIRS.get(keyword)

                        if expected_end:
                            stack.append(_ControlStructureInfo(
                                keyword=keyword,
                                line_number=line_num,
                                expected_end=expected_end,
                                nesting_level=len(stack),
                            ))

                        pos = start_match.end()
                    else:
                        # 先出现结束关键字
                        violation = self._handle_end_keyword(
                            end_match, stack, line, line_num,
                            file_path, violations
                        )
                        if violation:
                            violations.append(violation)
                        pos = end_match.end()

                elif start_match and not end_match:
                    # 只有开始关键字
                    keyword = start_match.group(1).upper()
                    expected_end = CONTROL_STRUCTURE_PAIRS.get(keyword)

                    if expected_end:
                        stack.append(_ControlStructureInfo(
                            keyword=keyword,
                            line_number=line_num,
                            expected_end=expected_end,
                            nesting_level=len(stack),
                        ))

                    pos = start_match.end()

                elif end_match and not start_match:
                    # 只有结束关键字
                    violation = self._handle_end_keyword(
                        end_match, stack, line, line_num,
                        file_path, violations
                    )
                    if violation:
                        violations.append(violation)
                    pos = end_match.end()

                else:
                    # 都没有找到，跳出循环
                    break

        # 检查未闭合的控制结构
        for unclosed in stack:
            violations.append(Violation(
                rule_id="SYNTAX_002",
                severity=Severity.ERROR,
                message=(
                    f"控制结构 '{unclosed.keyword}' "
                    f"(第{unclosed.line_number}行) 未闭合。"
                    f"期望找到 '{unclosed.expected_end}'。"
                ),
                file_path=file_path,
                line_number=unclosed.line_number,
                suggestion=f"添加 '{unclosed.expected_end}' 来闭合此结构",
                code_snippet=self._get_safe_line(lines, unclosed.line_number - 1),
            ))

        return violations

    def _handle_end_keyword(
        self,
        end_match: re.Match,
        stack: List[_ControlStructureInfo],
        line: str,
        line_num: int,
        file_path: str,
        violations: List[Violation],
    ) -> Optional[Violation]:
        """
        处理控制结构结束关键字的辅助方法

        Args:
            end_match: 结束关键字的正则匹配对象
            stack: 控制结构栈
            line: 当前行内容
            line_num: 行号
            file_path: 文件路径
            violations: 违规列表（用于追加）

        Returns:
            Optional[Violation]: 如果发现违规则返回Violation对象
        """
        end_keyword = end_match.group(1).upper()

        if not stack:
            # 栈为空，有多余的结束关键字
            return Violation(
                rule_id="SYNTAX_002",
                severity=Severity.ERROR,
                message=(
                    f"多余的 '{end_keyword}' 关键字，"
                    f"没有对应的开始结构。"
                ),
                file_path=file_path,
                line_number=line_num,
                column=end_match.start() + 1,
                suggestion="删除此多余的结束关键字或检查嵌套结构",
                code_snippet=line.strip(),
            )

        top = stack[-1]
        if end_keyword != top.expected_end:
            # 不匹配：期望的不是这个结束关键字
            return Violation(
                rule_id="SYNTAX_002",
                severity=Severity.ERROR,
                message=(
                    f"控制结构不匹配: 第{top.line_number}行的 "
                    f"'{top.keyword}' 期望以 '{top.expected_end}' 结束，"
                    f"但找到了 '{end_keyword}'。"
                ),
                file_path=file_path,
                line_number=line_num,
                column=end_match.start() + 1,
                suggestion=(
                    f"将 '{end_keyword}' 改为 '{top.expected_end}'，"
                    f"或检查 '{top.keyword}' 的嵌套结构"
                ),
                code_snippet=line.strip(),
            )

        # 匹配成功，弹出栈顶
        stack.pop()
        return None

    def _process_line_state(
        self,
        line: str,
        in_comment: bool,
        in_string: bool,
        string_char: str,
    ) -> Tuple[str, bool, bool, str]:
        """
        处理行的注释和字符串状态

        使用有限状态机跟踪当前是否在：
        - 多行注释 (* ... *) 中
        - 字符串字面量 '...' 或 "..."

        Args:
            line: 输入行
            in_comment: 当前是否在注释中
            in_string: 当前是否在字符串中
            string_char: 字符串引号字符

        Returns:
            Tuple[str, bool, bool, str]: 处理后的行和新状态
        """
        result_chars = []
        i = 0

        while i < len(line):
            if in_comment:
                # 在注释中，查找注释结束标记
                if i + 1 < len(line) and line[i:i+2] == '*)':
                    in_comment = False
                    i += 2
                else:
                    i += 1
            elif in_string:
                # 在字符串中，查找字符串结束
                if line[i] == string_char:
                    in_string = False
                    string_char = ""
                result_chars.append(line[i])
                i += 1
            else:
                # 正常状态
                if line[i] in ("'", '"'):
                    # 进入字符串状态
                    in_string = True
                    string_char = line[i]
                    result_chars.append(line[i])
                    i += 1
                elif i + 1 < len(line) and line[i:i+2] == '(*':
                    # 进入注释状态
                    in_comment = True
                    i += 2
                else:
                    result_chars.append(line[i])
                    i += 1

        return ''.join(result_chars), in_comment, in_string, string_char

    # =====================================================================
    # 规则 SYNTAX_003: FB/函数块结构完整性
    # =====================================================================

    def _check_fb_structure(
        self,
        lines: List[str],
        file_path: str,
        is_fb: bool = False,
    ) -> List[Violation]:
        """
        检查函数块(FUNCTION_BLOCK)的结构完整性

        规则说明：
        - FUNCTION_BLOCK必须至少包含一个VAR_INPUT或VAR_OUTPUT
        - 必须有VAR声明区域（用于局部变量）
        - 结构顺序应为：VAR_INPUT -> VAR_OUTPUT -> [VAR]

        Args:
            lines: 代码行列表
            file_path: 文件路径
            is_fb: 从上下文获取的FB标志

        Returns:
            List[Violation]: 违规记录列表
        """
        violations: List[Violation] = []

        # 检测是否为FUNCTION_BLOCK
        fb_pattern = re.compile(
            r'^\s*FUNCTION_BLOCK\s+(\w+)',
            re.IGNORECASE
        )

        # 查找FUNCTION_BLOCK声明
        fb_start_line = 0
        fb_name = ""
        for line_num, line in enumerate(lines, start=1):
            match = fb_pattern.match(line)
            if match:
                is_fb = True
                fb_start_line = line_num
                fb_name = match.group(1)
                break

        if not is_fb:
            return violations

        # 收集VAR声明信息
        var_blocks: List[Tuple[int, str]] = []
        has_var_input = False
        has_var_output = False
        has_var = False

        # 正则表达式：匹配VAR声明块
        # 分组说明：
        #   (group 1): VAR声明类型
        var_pattern = re.compile(
            r'^\s*(VAR(?:_(?:INPUT|OUTPUT|IN_OUT|TEMP|GLOBAL|EXTERNAL|ACCESS|STATIC))?)'
            r'\s*(?:\(\*.*?\*\))?'  # 可选的行尾注释
            r'\s*$',
            re.IGNORECASE
        )

        for line_num, line in enumerate(lines, start=1):
            match = var_pattern.match(line)
            if match:
                var_type = match.group(1).upper()
                var_blocks.append((line_num, var_type))

                if var_type == "VAR_INPUT":
                    has_var_input = True
                elif var_type == "VAR_OUTPUT":
                    has_var_output = True
                elif var_type == "VAR":
                    has_var = True

        # 验证完整性
        if not has_var_input and not has_var_output:
            violations.append(Violation(
                rule_id="SYNTAX_003",
                severity=Severity.ERROR,
                message=(
                    f"函数块 '{fb_name}' 缺少必要的接口声明。"
                    f"FUNCTION_BLOCK必须包含至少一个"
                    f"VAR_INPUT或VAR_OUTPUT声明。"
                ),
                file_path=file_path,
                line_number=fb_start_line,
                suggestion=(
                    "添加VAR_INPUT（输入参数）或VAR_OUTPUT（输出参数）声明"
                ),
                code_snippet=self._get_safe_line(lines, fb_start_line - 1),
            ))

        # 检查VAR声明顺序
        input_pos = -1
        output_pos = -1
        var_pos = -1

        for idx, (line_num, var_type) in enumerate(var_blocks):
            if var_type == "VAR_INPUT" and input_pos == -1:
                input_pos = idx
            elif var_type == "VAR_OUTPUT" and output_pos == -1:
                output_pos = idx
            elif var_type == "VAR" and var_pos == -1:
                var_pos = idx

        # 验证顺序：VAR_INPUT应在VAR_OUTPUT之前
        if input_pos > 0 and output_pos > 0 and input_pos > output_pos:
            violations.append(Violation(
                rule_id="SYNTAX_003",
                severity=Severity.WARNING,
                message=(
                    "VAR_INPUT声明位置不正确。"
                    "建议将VAR_INPUT放在VAR_OUTPUT之前。"
                ),
                file_path=file_path,
                line_number=var_blocks[input_pos][0],
                suggestion=(
                    "调整VAR声明顺序，推荐顺序："
                    "VAR_INPUT -> VAR_OUTPUT -> VAR"
                ),
            ))

        return violations

    # =====================================================================
    # 规则 SYNTAX_004: 语句分号检测
    # =====================================================================

    def _check_statement_terminators(
        self,
        lines: List[str],
        file_path: str,
    ) -> List[Violation]:
        """
        检查赋值语句是否以分号结尾

        规则说明：
        - 所有赋值语句（variable := expression）必须以分号结尾
        - 函数调用语句应以分号结尾
        - 例外：控制结构行、VAR声明行、注释行不需要分号

        Args:
            lines: 代码行列表
            file_path: 文件路径

        Returns:
            List[Violation]: 违规记录列表
        """
        violations: List[Violation] = []
        in_comment: bool = False
        in_string: bool = False
        string_char: str = ""

        # 正则表达式：匹配赋值语句
        # 分组说明：
        #   (group 1): 左侧变量名
        #   (group 2): 赋值运算符 :=
        assignment_pattern = re.compile(
            r'^\s*(\w+(?:\.\w+)*)\s*(:=)\s*.+',
            re.MULTILINE
        )

        # 需要忽略的关键字行（这些行不需要分号）
        ignore_keywords = {
            "VAR", "END_VAR", "IF", "ELSE", "ELSIF", "END_IF",
            "CASE", "OF", "ELSE", "END_CASE",
            "FOR", "DO", "END_FOR",
            "WHILE", "DO", "END_WHILE",
            "REPEAT", "UNTIL", "END_REPEAT",
            "WITH", "DO", "END_WITH",
            "RETURN", "EXIT", "CONTINUE",
            "FUNCTION", "FUNCTION_BLOCK", "PROGRAM",
            "END_FUNCTION", "END_FUNCTION_BLOCK", "END_PROGRAM",
        }

        for line_num, raw_line in enumerate(lines, start=1):
            # 处理注释和字符串状态
            processed_line, in_comment, in_string, string_char = (
                self._process_line_state(
                    raw_line, in_comment, in_string, string_char
                )
            )

            stripped = processed_line.strip()

            # 跳过空行和注释行
            if not stripped or stripped.startswith("(*"):
                continue

            # 跳过已知不需要分号的行
            first_word = stripped.split()[0].split('(')[0].upper() if stripped.split() else ""
            if first_word in ignore_keywords or stripped.endswith(":"):
                continue

            # 检查是否是赋值语句且缺少分号
            if assignment_pattern.match(stripped):
                # 移除尾部注释后再检查分号
                code_part = re.sub(r'\(\*.*?\*\)', '', stripped).strip()

                if not code_part.endswith(';'):
                    # 进一步验证这确实是一个需要分号的语句
                    # 排除一些特殊情况（如数组索引、条件表达式等）
                    if self._requires_semicolon(code_part):
                        violations.append(Violation(
                            rule_id="SYNTAX_004",
                            severity=Severity.WARNING,
                            message="赋值语句缺少分号结尾。",
                            file_path=file_path,
                            line_number=line_num,
                            column=len(code_part) + 1,
                            suggestion="在语句末尾添加分号 (;)",
                            code_snippet=raw_line.strip(),
                        ))

        return violations

    def _requires_semicolon(self, statement: str) -> bool:
        """
        判断语句是否需要分号

        排除一些看起来像赋值但实际上不需要分号的情况

        Args:
            statement: 待判断的语句

        Returns:
            bool: True表示需要分号
        """
        # 包含 := 且不是以下情况
        if ":=" not in statement:
            return False

        # 排除纯变量声明（带冒号的）
        if re.match(r'^\s*\w+\s*:\s*\w+', statement):
            return False

        # 排除FOR循环中的赋值（通常包含 TO 或 DOWNTO）
        if re.search(r'\bTO\b|\bDOWNTO\b', statement, re.IGNORECASE):
            return False

        return True

    # =====================================================================
    # 规则 SYNTAX_005: 类型合法性验证
    # =====================================================================

    def _check_type_validity(
        self,
        lines: List[str],
        file_path: str,
        user_types: Set[str] = None,
    ) -> List[Violation]:
        """
        检查变量类型是否合法

        规则说明：
        - 类型必须是IEC 61131-3标准类型之一
        - 或者是已知的用户自定义类型（从上下文获取）
        - 数组类型声明格式应为 ARRAY [x..y] OF type

        Args:
            lines: 代码行列表
            file_path: 文件路径
            user_types: 用户自定义类型集合

        Returns:
            List[Violation]: 违规记录列表
        """
        violations: List[Violation] = []
        if user_types is None:
            user_types = set()

        # 合法类型集合（标准 + 用户自定义），统一转大写以便比较
        valid_types = IEC_STANDARD_TYPES | {t.upper() for t in user_types}

        # 正则表达式：匹配变量声明中的类型
        # 分组说明：
        #   (group 1): 变量名
        #   (group 2): 数组声明部分 (可选)
        #   (group 3): 数据类型名称
        var_type_pattern = re.compile(
            r'^\s*(\w+)\s*:\s*'
            r'(ARRAY\s*\[[^\]]*\]\s*OF\s+)?'  # 数组部分 (group 2)
            r'(\w+)'                           # 类型名 (group 3)
            r'(?:\s*\([^)]*\))?'               # 可选的类型参数
            r'\s*(?:;)?',                       # 可选的分号结尾
            re.IGNORECASE
        )

        in_var_block = False
        var_indent_level: Optional[int] = None

        for line_num, line in enumerate(lines, start=1):
            stripped = line.strip().upper()

            # 检测VAR块开始
            if re.match(r'^VAR(?:_\w+)?\s*$', stripped, re.IGNORECASE):
                in_var_block = True
                var_indent_level = len(line) - len(line.lstrip())
                continue

            # 检测VAR块结束
            if stripped == "END_VAR":
                in_var_block = False
                var_indent_level = None
                continue

            # 只在VAR块内检查
            if not in_var_block:
                continue

            # 跳过空行和注释行
            if not stripped or stripped.startswith("(*"):
                continue

            # 尝试匹配变量声明
            match = var_type_pattern.match(line)
            if match:
                var_name = match.group(1)
                array_part = match.group(2)  # 数组部分（可选）
                type_name = match.group(3).upper() if match.group(3) else ""

                # 如果有数组部分，提取基础类型
                if array_part:
                    # 正则：从 ARRAY [...] OF xxx 中提取xxx
                    array_type_match = re.search(
                        r'OF\s+(\w+)',
                        array_part,
                        re.IGNORECASE
                    )
                    if array_type_match:
                        type_name = array_type_match.group(1).upper()

                # 验证类型合法性
                if type_name and type_name not in valid_types:
                    violations.append(Violation(
                        rule_id="SYNTAX_005",
                        severity=Severity.ERROR,
                        message=(
                            f"变量 '{var_name}' 使用了未知的数据类型 "
                            f"'{type_name}'。"
                        ),
                        file_path=file_path,
                        line_number=line_num,
                        suggestion=(
                            f"使用标准IEC类型({', '.join(sorted(list(IEC_STANDARD_TYPES))[:5])}...) "
                            f"或有效的用户自定义类型"
                        ),
                        code_snippet=line.strip(),
                    ))

        return violations

    # =====================================================================
    # 辅助方法
    # =====================================================================

    @staticmethod
    def _get_safe_line(lines: List[str], index: int) -> str:
        """
        安全地获取指定索引的行内容

        Args:
            lines: 行列表
            index: 行索引（0-based）

        Returns:
            str: 行内容，越界时返回空字符串
        """
        if 0 <= index < len(lines):
            return lines[index].strip()
        return ""


# ============================================================================
# 单独规则检查器类（可选使用）
# ============================================================================

class VarTempPositionChecker(BaseChecker):
    """SYNTAX_001: VAR_TEMP位置验证"""

    def __init__(self):
        super().__init__(rule_info=RuleInfo(
            rule_id="SYNTAX_001",
            name="VAR_TEMP位置验证",
            description="检查VAR_TEMP声明是否位于正确位置",
            category="syntax",
            severity=Severity.ERROR,
        ))
        self._checker = SyntaxChecker()

    def check(
        self,
        source_code: str,
        file_path: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Violation]:
        lines = source_code.splitlines() if source_code else []
        return self._checker._check_var_temp_position(lines, file_path)


class ControlStructureChecker(BaseChecker):
    """SYNTAX_002: 控制结构配对检测"""

    def __init__(self):
        super().__init__(rule_info=RuleInfo(
            rule_id="SYNTAX_002",
            name="控制结构配对检测",
            description="检查IF/FOR/WHILE等控制结构是否正确配对",
            category="syntax",
            severity=Severity.ERROR,
        ))
        self._checker = SyntaxChecker()

    def check(
        self,
        source_code: str,
        file_path: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Violation]:
        lines = source_code.splitlines() if source_code else []
        return self._checker._check_control_structures(lines, file_path)


class FBStructureChecker(BaseChecker):
    """SYNTAX_003: FB/函数块结构完整性"""

    def __init__(self):
        super().__init__(rule_info=RuleInfo(
            rule_id="SYNTAX_003",
            name="FB结构完整性",
            description="检查函数块的VAR声明完整性",
            category="syntax",
            severity=Severity.ERROR,
        ))
        self._checker = SyntaxChecker()

    def check(
        self,
        source_code: str,
        file_path: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Violation]:
        lines = source_code.splitlines() if source_code else []
        is_fb = context.get("is_function_block", False) if context else False
        return self._checker._check_fb_structure(lines, file_path, is_fb)


class StatementTerminatorChecker(BaseChecker):
    """SYNTAX_004: 语句分号检测"""

    def __init__(self):
        super().__init__(rule_info=RuleInfo(
            rule_id="SYNTAX_004",
            name="语句分号检测",
            description="检查赋值语句是否以分号结尾",
            category="syntax",
            severity=Severity.WARNING,
        ))
        self._checker = SyntaxChecker()

    def check(
        self,
        source_code: str,
        file_path: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Violation]:
        lines = source_code.splitlines() if source_code else []
        return self._checker._check_statement_terminators(lines, file_path)


class TypeValidityChecker(BaseChecker):
    """SYNTAX_005: 类型合法性验证"""

    def __init__(self):
        super().__init__(rule_info=RuleInfo(
            rule_id="SYNTAX_005",
            name="类型合法性验证",
            description="检查变量类型是否为合法的IEC标准类型",
            category="syntax",
            severity=Severity.ERROR,
        ))
        self._checker = SyntaxChecker()

    def check(
        self,
        source_code: str,
        file_path: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Violation]:
        lines = source_code.splitlines() if source_code else []
        user_types = set(context.get("user_types", [])) if context else set()
        return self._checker._check_type_validity(lines, file_path, user_types)
