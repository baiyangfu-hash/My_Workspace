# -*- coding: utf-8 -*-
"""
注释检查器模块

实现PLC代码注释规范检查，包含4条核心规则：
- COMMENT_001: 嵌套注释括号匹配
- COMMENT_002: 中文标点符号检测
- COMMENT_003: 注释密度分析
- COMMENT_004: 注释格式一致性

核心算法：
1. 状态机 + 计数器检测嵌套注释括号匹配
2. Unicode范围检测中文标点符号
3. 行级统计计算注释密度百分比
4. 正则模式匹配验证注释格式一致性
"""

import re
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from collections import Counter

from src.checkers.base_checker import BaseChecker, RuleInfo, Severity
from src.models.check_result import Violation
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


# ============================================================================
# 常量定义
# ============================================================================

# 中文标点符号Unicode范围（常用集合）
CHINESE_PUNCTUATION_PATTERN = re.compile(
    r'[\u3000-\u303f'   # CJK符号和标点
    r'\uff00-\uffef]'    # 全角ASCII、全角标点
)

# 具体中文标点字符集（用于详细报告）
CHINESE_PUNCTUATION_CHARS = {
    '\u3001',  # 、（顿号）
    '\u3002',  # 。（句号）
    '\uff0c',  # ，（逗号）
    '\uff1a',  # ：（冒号）
    '\uff1b',  # ；（分号）
    '\uff01',  # ！（感叹号）
    '\uff1f',  # ？（问号）
    '\u2018',  # '（左单引号）
    '\u2019',  # '（右单引号）
    '\u201c',  # "（左双引号）
    '\u201d',  # "（右双引号）
    '\u300a',  # 《（左书名号）
    '\u300b',  # 》（右书名号）
    '\u3008',  # <（左单书名号）
    '\u3009',  # >（右单书名号）
    '\uff08',  # （（左括号）
    '\uff09',  # ）（右括号）
    '\u3010',  # 【（左方括号）
    '\u3011',  # 】（右方括号）
}

# 标准注释格式模式
# 分组说明：
#   (group 1): 可选的标签前缀 [TAG]
#   (group 2): 注释内容文本
STANDARD_COMMENT_FORMAT = re.compile(
    r'^\s*\(\*\s*'
    r'(?:\[\w+\]\s*)?'     # 可选标签: [INPUT], [OUTPUT]等
    r'(.+?)'               # 注释内容
    r'\s*\*\)\s*$',
    re.DOTALL
)

# 简单行注释格式（用于检测一致性）
# 正则表达式：匹配以破折号开头的分隔线
LINE_COMMENT_FORMAT = re.compile(
    r'^\s*\(\*\s*-+\s*'    # 以破折号开头的分隔线
)


@dataclass
class _CommentBlockInfo:
    """注释块信息数据类"""
    start_line: int         # 起始行号
    end_line: int           # 结束行号
    content: str            # 完整内容
    open_count: int         # 开括号数量
    close_count: int        # 关闭括号数量


# ============================================================================
# CommentChecker 主类
# ============================================================================

class CommentChecker(BaseChecker):
    """
    PLC代码注释规范检查器

    检查范围：
    1. 注释括号 (* *) 必须正确配对（不支持嵌套）
    2. 注释中不应使用中文标点符号（应使用英文半角标点）
    3. 注释密度应在合理范围内（建议10%-30%）
    4. 注释格式应保持一致（统一风格）

    Usage:
        checker = CommentChecker()
        violations = checker.check(source_code, file_path="main.st")
    """

    def __init__(self):
        """初始化注释检查器"""
        super().__init__(
            rule_info=RuleInfo(
                rule_id="COMMENT_CHECKER",
                name="ST注释规范检查器",
                description="检查PLC代码注释的规范性",
                category="comment",
                severity=Severity.WARNING,
                tags=["comment", "documentation", "style"],
            )
        )

        # 可配置参数
        self._min_comment_density: float = 5.0    # 最小注释密度(%)
        self._max_comment_density: float = 50.0   # 最大注释密度(%)
        self._ideal_density_range: Tuple[float, float] = (10.0, 30.0)

        logger.info("注释检查器初始化完成")

    def check(
        self,
        source_code: str,
        file_path: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Violation]:
        """
        执行所有注释规则检查

        Args:
            source_code: 待检查的ST源代码
            file_path: 源文件路径
            context: 上下文信息（可选），可包含：
                - min_comment_density: 自定义最小注释密度
                - max_comment_density: 自定义最大注释密度

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

            # 应用上下文配置
            if context:
                if "min_comment_density" in context:
                    self._min_comment_density = context["min_comment_density"]
                if "max_comment_density" in context:
                    self._max_comment_density = context["max_comment_density"]

            # 执行各项检查
            violations.extend(
                self._check_nested_comments(lines, file_path)
            )
            violations.extend(
                self._check_chinese_punctuation(lines, file_path)
            )
            violations.extend(
                self._check_comment_density(lines, file_path)
            )
            violations.extend(
                self._check_comment_format_consistency(lines, file_path)
            )

            logger.debug(
                f"注释检查完成: 文件={file_path}, "
                f"发现{len(violations)}个违规"
            )

        except Exception as e:
            logger.error(f"注释检查过程发生异常: {e}", exc_info=True)

        return violations

    # =====================================================================
    # 规则 COMMENT_001: 嵌套注释括号匹配
    # =====================================================================

    def _check_nested_comments(
        self,
        lines: List[str],
        file_path: str,
    ) -> List[Violation]:
        """
        使用状态机和计数器检测注释括号配对

        核心算法说明：
        IEC 61131-3标准规定ST语言的注释使用 (* 和 *) 括号，
        且**不支持嵌套注释**。本方法通过以下步骤检测：

        1. 遍历每一行，统计 (* 和 *) 的出现次数
        2. 维护一个计数器：遇到 (* 加1，遇到 *) 减1
        3. 如果计数器小于0，说明有多余的关闭括号
        4. 如果遍历结束后计数器不为0，说明有未闭合的注释
        5. 如果在已打开的注释内再次遇到 (*，报告嵌套警告

        Args:
            lines: 代码行列表
            file_path: 文件路径

        Returns:
            List[Violation]: 违规记录列表
        """
        violations: List[Violation] = []
        comment_stack: int = 0          # 注释深度计数器
        in_string: bool = False         # 是否在字符串中
        string_char: str = ""           # 字符串引号字符
        comment_start_line: int = 0     # 当前注释块的起始行
        nested_detected: bool = False   # 是否检测到嵌套

        for line_num, line in enumerate(lines, start=1):
            i = 0
            while i < len(line):
                # 处理字符串状态
                if in_string:
                    if line[i] == string_char:
                        in_string = False
                        string_char = ""
                    i += 1
                    continue

                # 检测字符串开始
                if line[i] in ("'", '"'):
                    in_string = True
                    string_char = line[i]
                    i += 1
                    continue

                # 检测注释开始 (*
                if i + 1 < len(line) and line[i:i+2] == '(*':
                    if comment_stack > 0:
                        # 已经在注释中，这是嵌套！
                        if not nested_detected:
                            violations.append(Violation(
                                rule_id="COMMENT_001",
                                severity=Severity.ERROR,
                                message=(
                                    "检测到嵌套注释。IEC 61131-3标准"
                                    "不支持嵌套注释。"
                                ),
                                file_path=file_path,
                                line_number=line_num,
                                column=i + 1,
                                suggestion=(
                                    "将内部注释改为其他形式，或使用多个"
                                    "独立注释块代替嵌套"
                                ),
                                code_snippet=line.strip(),
                            ))
                            nested_detected = True

                    comment_stack += 1
                    if comment_stack == 1:
                        comment_start_line = line_num
                    i += 2
                    continue

                # 检测注释结束 *)
                if i + 1 < len(line) and line[i:i+2] == '*)':
                    comment_stack -= 1
                    if comment_stack < 0:
                        # 多余的关闭括号
                        violations.append(Violation(
                            rule_id="COMMENT_001",
                            severity=Severity.ERROR,
                            message="多余的注释关闭括号 '*)'。",
                            file_path=file_path,
                            line_number=line_num,
                            column=i + 1,
                            suggestion="删除多余的 '*)' 或检查配对",
                            code_snippet=line.strip(),
                        ))
                        comment_stack = 0  # 重置以继续检查
                    i += 2
                    continue

                i += 1

        # 检查未闭合的注释
        if comment_stack > 0:
            violations.append(Violation(
                rule_id="COMMENT_001",
                severity=Severity.ERROR,
                message=(
                    f"未闭合的注释块，从第{comment_start_line}行开始。"
                    f"缺少 {comment_stack} 个关闭括号 '*)'。"
                ),
                file_path=file_path,
                line_number=comment_start_line,
                suggestion=f"在第{comment_start_line}行后的适当位置添加 '*)'",
                code_snippet=self._get_safe_line(lines, comment_start_line - 1),
            ))

        return violations

    # =====================================================================
    # 规则 COMMENT_002: 中文标点符号检测
    # =====================================================================

    def _check_chinese_punctuation(
        self,
        lines: List[str],
        file_path: str,
    ) -> List[Violation]:
        """
        检测注释中的中文标点符号

        规则说明：
        - PLC代码注释应使用英文半角标点符号
        - 中文全角标点可能导致编码问题或显示异常
        - 特别是在跨平台/国际化项目中更应注意

        检测的中文字符包括：
        - ，。！？：；""''《》【】（）等

        Args:
            lines: 代码行列表
            file_path: 文件路径

        Returns:
            List[Violation]: 违规记录列表
        """
        violations: List[Violation] = []
        in_comment: bool = False

        for line_num, line in enumerate(lines, start=1):
            # 简单状态跟踪：检测是否在注释中
            i = 0
            while i < len(line):
                # 检测注释边界
                if i + 1 < len(line) and line[i:i+2] == '(*':
                    in_comment = True
                    i += 2
                    continue

                if i + 1 < len(line) and line[i:i+2] == '*)':
                    in_comment = False
                    i += 2
                    continue

                # 在注释内检测中文标点
                if in_comment:
                    char = line[i]
                    if char in CHINESE_PUNCTUATION_CHARS:
                        # 获取该字符的描述名称
                        char_name = self._get_punctuation_name(char)

                        violations.append(Violation(
                            rule_id="COMMENT_002",
                            severity=Severity.WARNING,
                            message=(
                                f"注释中使用了中文标点 '{char}' "
                                f"({char_name})。建议使用英文半角标点。"
                            ),
                            file_path=file_path,
                            line_number=line_num,
                            column=i + 1,
                            suggestion=f"将 '{char}' 替换为对应的英文标点",
                            code_snippet=line.strip(),
                        ))
                        # 同一行只报告一次，避免重复
                        break

                i += 1

        return violations

    @staticmethod
    def _get_punctuation_name(char: str) -> str:
        """获取中文标点字符的中文名称"""
        names = {
            '\u3001': '顿号',
            '\u3002': '句号',
            '\uff0c': '逗号',
            '\uff1a': '冒号',
            '\uff1b': '分号',
            '\uff01': '感叹号',
            '\uff1f': '问号',
            '\u2018': '左单引号',
            '\u2019': '右单引号',
            '\u201c': '左双引号',
            '\u201d': '右双引号',
            '\u300a': '左书名号',
            '\u300b': '右书名号',
            '\uff08': '左圆括号',
            '\uff09': '右圆括号',
            '\u3010': '左方括号',
            '\u3011': '右方括号',
        }
        return names.get(char, '未知标点')

    # =====================================================================
    # 规则 COMMENT_003: 注释密度分析
    # =====================================================================

    def _check_comment_density(
        self,
        lines: List[str],
        file_path: str,
    ) -> List[Violation]:
        """
        分析并检查注释密度

        计算方式：
        - 统计总有效代码行数（排除空行）
        - 统计纯注释行和包含注释的混合行的数量
        - 注释密度 = (注释相关行数 / 总有效行数) * 100%

        判断标准：
        - 密度 < 5%: 注释不足（WARNING）
        - 密度 > 50%: 过度注释（INFO）
        - 10%-30%: 理想范围

        Args:
            lines: 代码行列表
            file_path: 文件路径

        Returns:
            List[Violation]: 违规记录列表
        """
        violations: List[Violation] = []

        total_lines = len(lines)
        if total_lines == 0:
            return violations

        empty_lines = 0
        pure_comment_lines = 0
        mixed_comment_lines = 0
        code_lines = 0

        for line in lines:
            stripped = line.strip()

            # 空行
            if not stripped:
                empty_lines += 1
                continue

            # 纯注释行：整行都是注释
            if stripped.startswith('(*') and stripped.endswith('*)'):
                pure_comment_lines += 1
                continue

            # 包含注释的混合行
            if '(*' in stripped or '*)' in stripped:
                mixed_comment_lines += 1
            else:
                code_lines += 1

        effective_lines = total_lines - empty_lines
        if effective_lines == 0:
            return violations

        # 计算注释密度（纯注释行权重更高）
        comment_weighted = pure_comment_lines * 1.0 + mixed_comment_lines * 0.5
        density = (comment_weighted / effective_lines) * 100

        # 判断是否违规
        if density < self._min_comment_density:
            violations.append(Violation(
                rule_id="COMMENT_003",
                severity=Severity.WARNING,
                message=(
                    f"注释密度过低: {density:.1f}% "
                    f"(最低要求: {self._min_comment_density}%)。"
                    f"建议增加代码注释以提高可读性。"
                ),
                file_path=file_path,
                line_number=1,
                suggestion=(
                    f"增加注释使密度达到至少 {self._min_comment_density}%，"
                    f"理想范围为 {self._ideal_density_range[0]}%-"
                    f"{self._ideal_density_range[1]}%"
                ),
            ))

        elif density > self._max_comment_density:
            violations.append(Violation(
                rule_id="COMMENT_003",
                severity=Severity.INFO,
                message=(
                    f"注释密度过高: {density:.1f}% "
                    f"(上限: {self._max_comment_density}%)。"
                    f"可能存在过度注释的情况。"
                ),
                file_path=file_path,
                line_number=1,
                suggestion=(
                    f"精简注释，移除冗余描述，"
                    f"保持密度在 {self._ideal_density_range[0]}%-"
                    f"{self._ideal_density_range[1]}% 范围内"
                ),
            ))

        logger.debug(
            f"注释密度统计: 总行={total_lines}, "
            f"空行={empty_lines}, 纯注释={pure_comment_lines}, "
            f"混合注释={mixed_comment_lines}, 代码={code_lines}, "
            f"密度={density:.1f}%"
        )

        return violations

    # =====================================================================
    # 规则 COMMENT_004: 注释格式一致性
    # =====================================================================

    def _check_comment_format_consistency(
        self,
        lines: List[str],
        file_path: str,
    ) -> List[Violation]:
        """
        检查注释格式的一致性

        检查项：
        1. 注释标签使用一致性（如 [INPUT], [OUTPUT] 等）
        2. 分隔线风格一致性（如 (* ---- *) vs (* ==== *)）
        3. 对齐方式一致性
        4. 大小写使用一致性

        Args:
            lines: 代码行列表
            file_path: 文件路径

        Returns:
            List[Violation]: 违规记录列表
        """
        violations: List[Violation] = []

        # 收集所有注释格式样本
        comment_formats: List[str] = []
        tag_patterns: Counter = Counter()
        separator_styles: Counter = Counter()

        for line_num, line in enumerate(lines, start=1):
            stripped = line.strip()

            # 匹配带标签的注释
            # 正则表达式：提取注释标签
            # 分组说明：
            #   (group 1): 标签内容（方括号内的文字）
            tag_match = re.search(r'\(\*\s*\[(\w+)\]', stripped)
            if tag_match:
                tag = tag_match.group(1).upper()
                tag_patterns[tag] += 1
                comment_formats.append(f"[{tag}]")

            # 匹配分隔线样式
            sep_match = LINE_COMMENT_FORMAT.match(stripped)
            if sep_match:
                # 提取分隔线字符
                sep_chars = re.sub(r'[()\*\s]', '', stripped)
                if sep_chars:
                    main_char = sep_chars[0]
                    separator_styles[main_char] += 1
                    comment_formats.append(f"sep-{main_char}")

        # 检查标签大小写一致性
        if len(tag_patterns) > 1:
            # 检查是否有大小写混用
            case_variations = set()
            for tag in tag_patterns.keys():
                case_variations.add(tag.lower())

            if len(case_variations) < len(tag_patterns):
                violations.append(Violation(
                    rule_id="COMMENT_004",
                    severity=Severity.WARNING,
                    message=(
                        "注释标签存在大小写不一致。"
                        f"发现的标签: {list(tag_patterns.keys())}"
                    ),
                    file_path=file_path,
                    line_number=1,
                    suggestion="统一使用大写或小写的注释标签",
                ))

        # 检查分隔线风格一致性
        if len(separator_styles) > 1:
            style_list = [f"'{char}' ({count}次)"
                         for char, count in separator_styles.items()]
            violations.append(Violation(
                rule_id="COMMENT_004",
                severity=Severity.INFO,
                message=(
                    f"注释分隔线风格不一致。使用了多种分隔符: "
                    f"{', '.join(style_list)}"
                ),
                file_path=file_path,
                line_number=1,
                suggestion="统一使用一种分隔线风格（推荐使用 '-'）",
            ))

        # 检查注释块长度一致性（可选的高级检查）
        self._check_comment_block_length(lines, file_path, violations)

        return violations

    def _check_comment_block_length(
        self,
        lines: List[str],
        file_path: str,
        violations: List[Violation],
    ) -> None:
        """
        检查注释块长度的合理性

        过长的单行注释可能影响可读性，
        过短的多行注释块可能缺乏足够说明。

        Args:
            lines: 代码行列表
            file_path: 文件路径
            violations: 违规列表（就地修改）
        """
        max_single_line_length = 120  # 单行注释最大长度

        for line_num, line in enumerate(lines, start=1):
            stripped = line.strip()

            # 只检查纯注释行
            if not (stripped.startswith('(*') and stripped.endswith('*)')):
                continue

            # 移除注释标记后检查内容长度
            content = stripped[2:-2].strip()

            if len(content) > max_single_line_length:
                violations.append(Violation(
                    rule_id="COMMENT_004",
                    severity=Severity.INFO,
                    message=(
                        f"单行注释过长({len(content)}字符)，"
                        f"建议不超过{max_single_line_length}字符。"
                    ),
                    file_path=file_path,
                    line_number=line_num,
                    suggestion="将长注释拆分为多行或精简内容",
                    code_snippet=stripped[:80] + "...",
                ))

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

    def get_statistics(self, source_code: str) -> Dict[str, Any]:
        """
        获取注释统计数据（供外部调用）

        Args:
            source_code: 源代码

        Returns:
            Dict: 包含各项统计数据的字典
        """
        if not source_code:
            return {
                "total_lines": 0,
                "comment_lines": 0,
                "density": 0.0,
                "chinese_punct_count": 0,
            }

        lines = source_code.splitlines()
        stats = {
            "total_lines": len(lines),
            "pure_comment_lines": 0,
            "mixed_comment_lines": 0,
            "empty_lines": 0,
            "chinese_punct_count": 0,
        }

        for line in lines:
            stripped = line.strip()
            if not stripped:
                stats["empty_lines"] += 1
            elif stripped.startswith('(*') and stripped.endswith('*)'):
                stats["pure_comment_lines"] += 1
            elif '(*' in stripped:
                stats["mixed_comment_lines"] += 1

            # 统计中文标点
            for char in stripped:
                if char in CHINESE_PUNCTUATION_CHARS:
                    stats["chinese_punct_count"] += 1

        effective = stats["total_lines"] - stats["empty_lines"]
        if effective > 0:
            weighted = (
                stats["pure_comment_lines"] * 1.0 +
                stats["mixed_comment_lines"] * 0.5
            )
            stats["density"] = round((weighted / effective) * 100, 2)

        return stats


# ============================================================================
# 单独规则检查器类（可选使用）
# ============================================================================

class NestedCommentChecker(BaseChecker):
    """COMMENT_001: 嵌套注释括号匹配"""

    def __init__(self):
        super().__init__(rule_info=RuleInfo(
            rule_id="COMMENT_001",
            name="嵌套注释检测",
            description="检查注释括号是否正确配对，禁止嵌套",
            category="comment",
            severity=Severity.ERROR,
        ))
        self._checker = CommentChecker()

    def check(
        self,
        source_code: str,
        file_path: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Violation]:
        lines = source_code.splitlines() if source_code else []
        return self._checker._check_nested_comments(lines, file_path)


class ChinesePunctuationChecker(BaseChecker):
    """COMMENT_002: 中文标点符号检测"""

    def __init__(self):
        super().__init__(rule_info=RuleInfo(
            rule_id="COMMENT_002",
            name="中文标点检测",
            description="检查注释中是否使用了中文标点符号",
            category="comment",
            severity=Severity.WARNING,
        ))
        self._checker = CommentChecker()

    def check(
        self,
        source_code: str,
        file_path: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Violation]:
        lines = source_code.splitlines() if source_code else []
        return self._checker._check_chinese_punctuation(lines, file_path)


class CommentDensityChecker(BaseChecker):
    """COMMENT_003: 注释密度分析"""

    def __init__(self):
        super().__init__(rule_info=RuleInfo(
            rule_id="COMMENT_003",
            name="注释密度分析",
            description="检查代码注释密度是否在合理范围内",
            category="comment",
            severity=Severity.WARNING,
        ))
        self._checker = CommentChecker()

    def check(
        self,
        source_code: str,
        file_path: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Violation]:
        lines = source_code.splitlines() if source_code else []
        return self._checker._check_comment_density(lines, file_path)


class CommentFormatChecker(BaseChecker):
    """COMMENT_004: 注释格式一致性"""

    def __init__(self):
        super().__init__(rule_info=RuleInfo(
            rule_id="COMMENT_004",
            name="注释格式一致性",
            description="检查注释格式、标签、分隔线是否一致",
            category="comment",
            severity=Severity.INFO,
        ))
        self._checker = CommentChecker()

    def check(
        self,
        source_code: str,
        file_path: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Violation]:
        lines = source_code.splitlines() if source_code else []
        return self._checker._check_comment_format_consistency(lines, file_path)
