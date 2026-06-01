# -*- coding: utf-8 -*-
"""
中文标点自动替换修复器

实现PLC代码注释中中文全角标点→英文半角标点的自动替换。
仅在注释区域（(* *)块注释和//行注释）内执行替换，不触碰任何代码。

映射表（复用comment_checker.CHINESE_PUNCTUATION_CHARS的字符集）：
- ，(U+FF0C) → ,(comma)
- 。(U+3002) → .(period)
- ：(U+FF1A) → :(colon)
- ；(U+FF1B) → ;(semicolon)
- （(U+FF08) → ((left parenthesis)
- ）(U+FF09) → )(right parenthesis)
- 【(U+3010) → [(left square bracket)
- 】(U+3011) → ](right square bracket)
- "(U+201C) → "(left double quote)
- "(U+201D) → "(right double quote)
- '(U+2018) → '(left single quote)
- '(U+2019) → '(right single quote)
"""

import difflib
from typing import List, Dict, Tuple

from src.fixers.base_fixer import (
    BaseFixer,
    FixIssue,
    FixResult,
    FixPreview,
    FixerInfo,
    Severity,
)
from src.checkers.comment_checker import CHINESE_PUNCTUATION_CHARS
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


PUNCTUATION_MAP: Dict[str, str] = {
    "\uff0c": ",",
    "\u3002": ".",
    "\uff1a": ":",
    "\uff1b": ";",
    "\uff08": "(",
    "\uff09": ")",
    "\u3010": "[",
    "\u3011": "]",
    "\u201c": '"',
    "\u201d": '"',
    "\u2018": "'",
    "\u2019": "'",
}


class CommentPunctuationFixer(BaseFixer):
    """
    中文标点自动替换修复器

    检测并修复注释中的中文全角标点符号，
    将其替换为对应的英文半角标点。

    安全级别：安全（is_safe=True），可直接修改源文件。

    Usage:
        fixer = CommentPunctuationFixer()
        issues = fixer.detect(source_code, file_path="main.st")
        previews = fixer.preview_fix(source_code, issues)
        fixed_code, results = fixer.fix(source_code, issues)
    """

    def __init__(self):
        super().__init__(
            fixer_info=FixerInfo(
                fixer_id="COMMENT_PUNCTUATION_FIXER",
                name="中文标点自动替换",
                description=(
                    "将注释中的中文全角标点符号自动替换为英文半角标点。"
                    "仅修改注释区域，不影响代码逻辑。"
                ),
                category="punctuation",
                is_safe=True,
                tags=["comment", "punctuation", "auto-fix", "safe"],
            )
        )

    def detect(
        self,
        source_code: str,
        file_path: str = "",
    ) -> List[FixIssue]:
        """
        检测注释中的中文标点符号

        使用状态机逐字符遍历，仅标记注释区域内的中文标点，
        代码区域中的中文标点不会被检测到（避免误报）。

        Args:
            source_code: 待检测的ST源代码
            file_path: 源文件路径

        Returns:
            List[FixIssue]: 发现的可修复问题列表
        """
        issues: List[FixIssue] = []

        if not source_code or not isinstance(source_code, str):
            return issues

        lines = source_code.splitlines()

        for line_num, line in enumerate(lines, start=1):
            in_comment = False
            in_string = False
            string_char = ""

            i = 0
            while i < len(line):
                if in_string:
                    if i < len(line) and line[i] == string_char:
                        in_string = False
                        string_char = ""
                    i += 1
                    continue

                if line[i] in ("'", '"'):
                    in_string = True
                    string_char = line[i]
                    i += 1
                    continue

                if i + 1 < len(line) and line[i:i + 2] == "(*":
                    in_comment = True
                    i += 2
                    continue

                if i + 1 < len(line) and line[i:i + 2] == "*)":
                    in_comment = False
                    i += 2
                    continue

                if in_comment:
                    char = line[i]
                    if char in PUNCTUATION_MAP:
                        replacement = PUNCTUATION_MAP[char]
                        issues.append(FixIssue(
                            rule_id="COMMENT_002",
                            file_path=file_path,
                            line_number=line_num,
                            column=i + 1,
                            original_text=char,
                            suggested_text=replacement,
                            severity=Severity.WARNING,
                        ))
                    i += 1
                    continue

                i += 1

        logger.debug(
            f"标点检测完成: 文件={file_path}, 发现{len(issues)}个可修复问题"
        )
        return issues

    def fix(
        self,
        source_code: str,
        issues: List[FixIssue],
    ) -> Tuple[str, List[FixResult]]:
        """
        执行中文标点替换修复

        基于detect返回的问题列表，在注释区域内执行字符替换。
        仅替换issues中记录的位置，确保精确控制。

        Args:
            source_code: 原始源代码
            issues: 待修复的问题列表

        Returns:
            Tuple[str, List[FixResult]]: (修复后代码, 修复结果列表)
        """
        if not source_code or not issues:
            return source_code, []

        lines = source_code.splitlines()
        results: List[FixResult] = []
        replacement_count = 0

        issue_by_line: Dict[int, List[FixIssue]] = {}
        for issue in issues:
            issue_by_line.setdefault(issue.line_number, []).append(issue)

        for line_num, line_issues in issue_by_line.items():
            line_idx = line_num - 1
            if line_idx < 0 or line_idx >= len(lines):
                continue

            original_line = lines[line_idx]
            fixed_line = list(original_line)
            applied: List[str] = []
            success = True

            sorted_issues = sorted(line_issues, key=lambda x: x.column, reverse=True)

            for issue in sorted_issues:
                col_idx = issue.column - 1
                if col_idx < 0 or col_idx >= len(fixed_line):
                    success = False
                    continue

                current_char = fixed_line[col_idx]
                if current_char != issue.original_text:
                    success = False
                    continue

                fixed_line[col_idx] = issue.suggested_text
                applied.append(
                    f"将 '{issue.original_text}' 替换为 '{issue.suggested_text}'"
                )
                replacement_count += 1

            final_fixed = "".join(fixed_line)
            lines[line_idx] = final_fixed

            results.append(FixResult(
                success=success and len(applied) > 0,
                original_line=original_line,
                fixed_line=final_fixed,
                line_number=line_num,
                applied_fixes=applied,
            ))

        fixed_code = "\n".join(lines)

        logger.info(
            f"标点修复完成: 共处理{len(issue_by_line)}行, "
            f"执行{replacement_count}次替换"
        )

        return fixed_code, results

    def preview_fix(
        self,
        source_code: str,
        issues: List[FixIssue],
    ) -> List[FixPreview]:
        """
        生成修复预览（unified diff格式）

        不修改原始源代码，生成差异对比视图供用户确认。

        Args:
            source_code: 原始源代码
            issues: 待修复的问题列表

        Returns:
            List[FixPreview]: 包含diff视图的预览列表
        """
        if not issues:
            return [FixPreview(
                diff_view="未发现需要修复的中文标点问题",
                issue_count=0,
                fixer_id=self.fixer_id,
            )]

        fixed_code, _ = self.fix(source_code, issues)

        original_lines = source_code.splitlines()
        fixed_lines = fixed_code.splitlines()

        diff = difflib.unified_diff(
            original_lines,
            fixed_lines,
            fromfile="原始文件",
            tofile="修复后",
            lineterm="",
        )

        diff_text = "\n".join(diff)

        affected_lines = sorted(set(issue.line_number for issue in issues))

        preview = FixPreview(
            diff_view=diff_text or "无差异（可能替换前后内容相同）",
            issue_count=len(issues),
            affected_lines=affected_lines,
            fixer_id=self.fixer_id,
        )

        logger.debug(f"生成修复预览: {len(issues)}个问题, 影响{len(affected_lines)}行")
        return [preview]

    def get_replacement_statistics(
        self,
        source_code: str,
    ) -> Dict[str, int]:
        """
        获取各类标点的替换统计信息

        用于UI展示和报告生成。

        Args:
            source_code: 源代码文本

        Returns:
            Dict[str, int]: 各中文标点及其出现次数
        """
        issues = self.detect(source_code)
        stats: Dict[str, int] = {}

        for issue in issues:
            char = issue.original_text
            char_name = self._get_punctuation_display_name(char)
            key = f"{char_name}({char})"
            stats[key] = stats.get(key, 0) + 1

        return stats

    @staticmethod
    def _get_punctuation_display_name(char: str) -> str:
        names = {
            "\uff0c": "逗号",
            "\u3002": "句号",
            "\uff1a": "冒号",
            "\uff1b": "分号",
            "\uff08": "左圆括号",
            "\uff09": "右圆括号",
            "\u3010": "左方括号",
            "\u3011": "右方括号",
            "\u201c": "左双引号",
            "\u201d": "右双引号",
            "\u2018": "左单引号",
            "\u2019": "右单引号",
        }
        return names.get(char, "未知")
