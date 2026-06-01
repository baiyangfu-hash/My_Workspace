# -*- coding: utf-8 -*-
"""
变量命名建议修复器

基于NamingChecker的检测规则，生成变量重命名建议列表。
出于安全考虑（重命名可能导致引用链断裂），
本修复器不直接修改代码，而是输出修复脚本供用户确认后执行。

支持的重命名建议类型：
- NAMING_001: 移除METHOD定义中的CALL_前缀
- NAMING_002: 移除METHOD调用中的CALL_前缀
- NAMING_003: 添加正确的变量前缀
- NAMING_004: 中文变量名→英文翻译建议
- NAMING_005: 移除多余下划线，改用小驼峰
- NAMING_006: 修正小驼峰命名格式

安全级别：仅建议（is_safe=False），需用户确认后手动执行。
"""

import re
from typing import List, Dict, Tuple, Optional

from src.fixers.base_fixer import (
    BaseFixer,
    FixIssue,
    FixResult,
    FixPreview,
    FixerInfo,
    Severity,
)
from src.checkers.naming_checker import NamingChecker
from src.models.check_result import Violation
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class NamingFixer(BaseFixer):
    """
    变量命名建议修复器

    基于NamingChecker的检测结果生成重命名建议，
    输出可执行的重命名脚本供用户确认。

    与CommentPunctuationFixer不同：
    - is_safe=False: 变量重命名有风险，不直接修改源文件
    - fix()方法返回的是建议脚本而非修改后代码
    - preview_fix()生成结构化建议列表而非diff

    Usage:
        fixer = NamingFixer()
        issues = fixer.detect(source_code, file_path="main.st")
        previews = fixer.preview_fix(source_code, issues)
        script = fixer.generate_rename_script(source_code, issues)
    """

    def __init__(self):
        super().__init__(
            fixer_info=FixerInfo(
                fixer_id="NAMING_FIXER",
                name="变量命名建议修复器",
                description=(
                    "基于905规范生成变量/METHOD重命名建议。"
                    "输出重命名脚本供用户确认后执行，不直接修改源文件。"
                ),
                category="naming",
                is_safe=False,
                tags=["naming", "rename", "suggestion", "manual-confirm"],
            )
        )

        self._checker = NamingChecker()

    def detect(
        self,
        source_code: str,
        file_path: str = "",
    ) -> List[FixIssue]:
        """
        检测命名规范违规并转换为可修复问题

        复用NamingChecker的检查结果，将Violation转换为FixIssue格式。

        Args:
            source_code: 待检测的ST源代码
            file_path: 源文件路径

        Returns:
            List[FixIssue]: 可修复问题列表
        """
        issues: List[FixIssue] = []

        if not source_code or not isinstance(source_code, str):
            return issues

        violations: List[Violation] = self._checker.check(
            source_code, file_path=file_path
        )

        for v in violations:
            suggested = self._extract_suggested_name(v.suggestion)
            original_text = self._extract_original_name(v.message, v.code_snippet)

            severity = Severity.WARNING
            if v.severity.name == "ERROR":
                severity = Severity.ERROR

            issues.append(FixIssue(
                rule_id=v.rule_id,
                file_path=v.file_path or file_path,
                line_number=v.line_number,
                column=v.column,
                original_text=original_text,
                suggested_text=suggested,
                severity=severity,
            ))

        logger.debug(
            f"命名检测完成: 文件={file_path}, 发现{len(issues)}个命名问题"
        )
        return issues

    def fix(
        self,
        source_code: str,
        issues: List[FixIssue],
    ) -> Tuple[str, List[FixResult]]:
        """
        生成重命名建议（不直接修改源代码）

        由于变量重命名存在风险（可能破坏引用链），
        本方法仅生成建议报告，不实际修改代码。

        Args:
            source_code: 原始源代码
            issues: 待处理的问题列表

        Returns:
            Tuple[str, List[FixResult]]: (原始代码不变, 建议结果列表)
        """
        results: List[FixResult] = []

        if not issues:
            results.append(FixResult(
                success=True,
                original_line="",
                fixed_line="",
                applied_fixes=["无需修复"],
            ))
            return source_code, results

        issue_by_line: Dict[int, List[FixIssue]] = {}
        for issue in issues:
            issue_by_line.setdefault(issue.line_number, []).append(issue)

        lines = source_code.splitlines() if source_code else []

        for line_num, line_issues in sorted(issue_by_line.items()):
            line_idx = line_num - 1
            original_line = ""
            if 0 <= line_idx < len(lines):
                original_line = lines[line_idx]

            applied: List[str] = []
            for issue in line_issues:
                if issue.original_text and issue.suggested_text:
                    applied.append(
                        f"建议将 '{issue.original_text}' "
                        f"重命名为 '{issue.suggested_text}' "
                        f"(规则: {issue.rule_id})"
                    )
                elif issue.suggested_text:
                    applied.append(
                        f"建议修改 (规则: {issue.rule_id}): "
                        f"{issue.suggested_text}"
                    )

            results.append(FixResult(
                success=True,
                original_line=original_line,
                fixed_line=original_line,
                line_number=line_num,
                applied_fixes=applied,
            ))

        logger.info(
            f"命名建议生成完成: 共{len(issue_by_line)}行, "
            f"{len(issues)}个建议"
        )

        return source_code, results

    def preview_fix(
        self,
        source_code: str,
        issues: List[FixIssue],
    ) -> List[FixPreview]:
        """
        生成结构化的命名修复预览

        以表格形式展示每个问题的原始名称和建议名称，
        并附带风险提示信息。

        Args:
            source_code: 原始源代码
            issues: 问题列表

        Returns:
            List[FixPreview]: 预览列表
        """
        if not issues:
            return [FixPreview(
                diff_view="未发现需要修复的命名规范问题",
                issue_count=0,
                fixer_id=self.fixer_id,
            )]

        preview_lines: List[str] = []
        preview_lines.append("=" * 70)
        preview_lines.append("变量命名修复预览（需手动确认后执行）")
        preview_lines.append("=" * 70)
        preview_lines.append("")
        preview_lines.append(f"{'规则ID':<14} {'行号':<6} {'原始名称':<20} {'建议名称':<20}")
        preview_lines.append("-" * 70)

        affected_lines: List[int] = []
        rule_stats: Dict[str, int] = {}

        for issue in issues:
            preview_lines.append(
                f"{issue.rule_id:<14} {issue.line_number:<6} "
                f"{issue.original_text:<20} {issue.suggested_text:<20}"
            )
            affected_lines.append(issue.line_number)
            rule_stats[issue.rule_id] = rule_stats.get(issue.rule_id, 0) + 1

        preview_lines.append("-" * 70)
        preview_lines.append("")
        preview_lines.append("统计摘要:")
        for rule_id, count in sorted(rule_stats.items()):
            preview_lines.append(f"  - {rule_id}: {count} 个问题")
        preview_lines.append(f"  - 合计: {len(issues)} 个问题, 影响 {len(set(affected_lines))} 行")
        preview_lines.append("")
        preview_lines.append("⚠️  风险提示:")
        preview_lines.append("  变量重命名可能影响所有引用该变量的位置。")
        preview_lines.append("  请确认无误后再执行重命名操作。")
        preview_lines.append("=" * 70)

        diff_view = "\n".join(preview_lines)

        preview = FixPreview(
            diff_view=diff_view,
            issue_count=len(issues),
            affected_lines=sorted(set(affected_lines)),
            fixer_id=self.fixer_id,
        )

        return [preview]

    def generate_rename_script(
        self,
        source_code: str,
        issues: Optional[List[FixIssue]] = None,
    ) -> str:
        """
        生成可执行的重命名脚本

        输出结构化的重命名操作清单，
        用户确认后可用于批量执行重命名。

        脚本格式：
        ```
        # 自动生成的重命名脚本
        # 文件: xxx.st
        # 生成时间: YYYY-MM-DD HH:MM:SS
        #
        # 使用说明: 确认每项修改后，使用文本编辑器的
        #           "全部替换"功能执行重命名

        ## 重命名操作列表
        1. 行NNN: '旧名称' → '新名称'  [规则ID]
        ...
        ```

        Args:
            source_code: 原始源代码
            issues: 问题列表（为None时自动调用detect）

        Returns:
            str: 格式化的重命名脚本文本
        """
        from datetime import datetime

        if issues is None:
            issues = self.detect(source_code)

        if not issues:
            return "# 未发现需要重命名的变量\n"

        script_lines: List[str] = []
        script_lines.append("# 自动生成的重命名脚本")
        script_lines.append(f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        script_lines.append("#")
        script_lines.append("# 使用说明:")
        script_lines.append("#   1. 逐条审查以下重命名建议")
        script_lines.append("#   2. 确认无误后，使用编辑器'全部替换'功能执行")
        script_lines.append("#   3. 替换范围: 当前文件全局搜索替换")
        script_lines.append("#   4. 注意: 替换前请先备份原文件")
        script_lines.append("")

        rename_items: List[Tuple[str, str, str, int]] = []
        seen_pairs: set = set()

        for issue in issues:
            pair_key = (issue.original_text, issue.suggested_text)
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)

            if issue.original_text and issue.suggested_text:
                rename_items.append((
                    issue.original_text,
                    issue.suggested_text,
                    issue.rule_id,
                    issue.line_number,
                ))

        script_lines.append("## 重命名操作列表")
        script_lines.append("")

        for idx, (old_name, new_name, rule_id, line_num) in enumerate(rename_items, start=1):
            script_lines.append(
                f"{idx}. 行{line_num}: "
                f"'{old_name}' → '{new_name}'  [{rule_id}]"
            )

        script_lines.append("")
        script_lines.append(f"## 统计: 共{len(rename_items)}个独立重命名操作")

        logger.debug(f"生成重命名脚本: {len(rename_items)}个操作")
        return "\n".join(script_lines)

    def get_rules_summary(self) -> Dict[str, Dict[str, str]]:
        """
        获取所有支持的命名规则摘要

        Returns:
            Dict: 规则ID到规则描述的映射
        """
        all_rules = self._checker.get_all_rules()
        summary = {}
        for rule_id, info in all_rules.items():
            summary[rule_id] = {
                "name": info.name,
                "description": info.description,
                "severity": info.severity.name,
            }
        return summary

    @staticmethod
    def _extract_suggested_name(suggestion: Optional[str]) -> str:
        """从建议文本中提取目标名称"""
        if not suggestion:
            return ""

        patterns = [
            r"(?:改为|重命名为|建议改为|改为|更名)\s*[:：]?\s*['\"]?(\w+)['\"]?",
            r"(?:移除.*?改为|改为)\s*[:：]?\s*['\"]?(\w+)['\"]?",
            r"['\"]([\w_]+)['\"]",
        ]

        for pattern in patterns:
            match = re.search(pattern, suggestion)
            if match:
                return match.group(1)

        return suggestion.strip()

    @staticmethod
    def _extract_original_name(message: str, code_snippet: Optional[str]) -> str:
        """从消息或代码片段中提取原始名称"""
        if code_snippet:
            name_match = re.match(r"^(\w+)", code_snippet.strip())
            if name_match:
                return name_match.group(1)

        name_match = re.search(r"['\"]([^'\"]+)['\"]|(?:变量名|名称)\s*[\"']?(\w+)", message)
        if name_match:
            return name_match.group(1) or name_match.group(2) or ""

        return ""
