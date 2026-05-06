# -*- coding: utf-8 -*-
"""
LSP兼容性诊断报告数据模型

定义诊断问题的完整数据结构和报告生成功能，
支持序列化为字典和Markdown格式输出。
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Any
from pathlib import Path


class DiagnosticSeverity(Enum):
    """诊断问题严重级别枚举"""
    ERROR = "error"           # 错误：必须修复的严重问题
    WARNING = "warning"       # 警告：建议修复的问题
    INFO = "info"             # 信息：提示性信息
    HINT = "hint"             # 提示：改进建议


@dataclass
class DiagnosticIssue:
    """
    单个诊断问题记录

    记录LSP兼容性检查中发现的问题，包括位置、类型、描述和修复建议。

    Attributes:
        rule_id: 触发的诊断规则ID（如 DIAG_001）
        severity: 问题严重级别
        message: 问题描述
        file_path: 问题所在文件路径（相对于.plc-out目录）
        line_number: 所在行号（从1开始）
        column: 所在列号（从1开始，可选）
        category: 问题分类（如 'stub_misuse', 'missing_implementation'）
        suggestion: 修复建议（可选）
        code_snippet: 问题代码片段（可选，用于快速定位）
        source_line: 源文件中的原始行（用于定位SCL源码位置）
        related_symbols: 相关符号列表（如调用的FB名称等）
    """
    rule_id: str
    severity: DiagnosticSeverity
    message: str
    file_path: str = ""
    line_number: int = 0
    column: int = 0
    category: str = ""
    suggestion: Optional[str] = None
    code_snippet: Optional[str] = None
    source_line: Optional[str] = None
    related_symbols: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        将诊断问题转换为字典

        Returns:
            Dict: 包含所有字段的可序列化字典
        """
        return {
            "rule_id": self.rule_id,
            "severity": self.severity.value,
            "message": self.message,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "column": self.column,
            "category": self.category,
            "suggestion": self.suggestion,
            "code_snippet": self.code_snippet,
            "source_line": self.source_line,
            "related_symbols": self.related_symbols,
        }

    @property
    def location_str(self) -> str:
        """
        格式化的位置字符串

        Returns:
            str: 格式为 "文件名:行号:列号"
        """
        if self.file_path and self.line_number > 0:
            # 只显示文件名，不显示完整路径
            filename = Path(self.file_path).name
            loc = f"{filename}:{self.line_number}"
            if self.column > 0:
                loc += f":{self.column}"
            return loc
        return self.file_path or "未知位置"

    @property
    def severity_icon(self) -> str:
        """获取严重级别对应的图标"""
        icons = {
            DiagnosticSeverity.ERROR: "❌",
            DiagnosticSeverity.WARNING: "⚠️",
            DiagnosticSeverity.INFO: "ℹ️",
            DiagnosticSeverity.HINT: "💡",
        }
        return icons.get(self.severity, "?")

    def __str__(self) -> str:
        """人类可读的问题描述"""
        return (
            f"[{self.severity.value.upper()}] {self.location_str}: "
            f"{self.message} (规则: {self.rule_id})"
        )


@dataclass
class DiagnosticReport:
    """
    LSP兼容性诊断报告

    汇总整个项目的LSP兼容性检查结果，
    提供详细的统计分析、问题列表和修复建议。

    Attributes:
        project_name: 项目名称
        project_path: 项目根目录路径
        plc_output_path: .plc-out目录路径
        issues: 发现的所有诊断问题列表
        scan_time: 扫描完成时间戳
        scanned_files: 扫描的文件列表
        total_issues: 问题总数
        error_count: 错误级别问题数
        warning_count: 警告级别问题数
        info_count: 信息级别问题数
        hint_count: 提示级别问题数
        ob_fb_call_chain: OB到FB的调用链分析结果
        missing_implementations: 缺失实现的FB/FC列表
        stub_misuses: 检测到的stub误用列表
    """
    project_name: str = ""
    project_path: str = ""
    plc_output_path: str = ""
    issues: List[DiagnosticIssue] = field(default_factory=list)
    scan_time: datetime = field(default_factory=datetime.now)
    scanned_files: List[str] = field(default_factory=list)
    total_issues: int = 0
    error_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    hint_count: int = 0
    ob_fb_call_chain: Dict[str, List[str]] = field(default_factory=dict)
    missing_implementations: List[Dict[str, Any]] = field(default_factory=list)
    stub_misuses: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        """初始化后自动计算统计数据"""
        self._recalculate_stats()

    def add_issue(self, issue: DiagnosticIssue) -> None:
        """
        添加一条诊断问题

        Args:
            issue: 诊断问题对象
        """
        self.issues.append(issue)
        self._update_stats_for_issue(issue)

    def add_issues(self, issues: List[DiagnosticIssue]) -> None:
        """
        批量添加诊断问题

        Args:
            issues: 诊断问题列表
        """
        self.issues.extend(issues)
        for issue in issues:
            self._update_stats_for_issue(issue)

    def _update_stats_for_issue(self, issue: DiagnosticIssue) -> None:
        """根据问题更新统计计数"""
        if issue.severity == DiagnosticSeverity.ERROR:
            self.error_count += 1
        elif issue.severity == DiagnosticSeverity.WARNING:
            self.warning_count += 1
        elif issue.severity == DiagnosticSeverity.INFO:
            self.info_count += 1
        elif issue.severity == DiagnosticSeverity.HINT:
            self.hint_count += 1

    def _recalculate_stats(self) -> None:
        """重新计算所有统计数据"""
        self.total_issues = len(self.issues)
        self.error_count = sum(
            1 for i in self.issues if i.severity == DiagnosticSeverity.ERROR
        )
        self.warning_count = sum(
            1 for i in self.issues if i.severity == DiagnosticSeverity.WARNING
        )
        self.info_count = sum(
            1 for i in self.issues if i.severity == DiagnosticSeverity.INFO
        )
        self.hint_count = sum(
            1 for i in self.issues if i.severity == DiagnosticSeverity.HINT
        )

    @property
    def has_errors(self) -> bool:
        """是否包含错误级别的问题"""
        return self.error_count > 0

    @property
    def has_issues(self) -> bool:
        """是否包含任何问题"""
        return len(self.issues) > 0

    @property
    def is_passed(self) -> bool:
        """检查是否通过（无错误）"""
        return not self.has_errors

    @property
    def pass_rate(self) -> float:
        """通过率（基于扫描文件数）"""
        if not self.scanned_files:
            return 100.0
        files_with_errors = len(set(i.file_path for i in self.issues
                                   if i.severity == DiagnosticSeverity.ERROR))
        passed_files = len(self.scanned_files) - files_with_errors
        return (passed_files / len(self.scanned_files)) * 100

    @property
    def quality_score(self) -> float:
        """
        质量评分（0-100分）

        基于问题密度和严重程度计算的加权分数
        """
        if not self.scanned_files:
            return 100.0

        # 加权扣分机制
        error_penalty = self.error_count * 10
        warning_penalty = self.warning_count * 3
        info_penalty = self.info_count * 1
        hint_penalty = self.hint_count * 0.5

        total_penalty = error_penalty + warning_penalty + info_penalty + hint_penalty
        score = max(0, 100 - total_penalty)

        return round(score, 2)

    def get_issues_by_severity(
        self, severity: DiagnosticSeverity
    ) -> List[DiagnosticIssue]:
        """
        按严重级别筛选问题

        Args:
            severity: 要筛选的严重级别

        Returns:
            List[DiagnosticIssue]: 匹配的问题列表
        """
        return [i for i in self.issues if i.severity == severity]

    def get_issues_by_rule(self, rule_id: str) -> List[DiagnosticIssue]:
        """
        按规则ID筛选问题

        Args:
            rule_id: 规则ID

        Returns:
            List[DiagnosticIssue]: 匹配的问题列表
        """
        return [i for i in self.issues if i.rule_id == rule_id]

    def get_issues_by_category(self, category: str) -> List[DiagnosticIssue]:
        """
        按分类筛选问题

        Args:
            category: 问题分类

        Returns:
            List[DiagnosticIssue]: 匹配的问题列表
        """
        return [i for i in self.issues if i.category == category]

    def get_issues_by_file(self, file_path: str) -> List[DiagnosticIssue]:
        """
        根据文件路径获取问题列表

        Args:
            file_path: 文件路径

        Returns:
            List[DiagnosticIssue]: 该文件的问题列表
        """
        return [i for i in self.issues if i.file_path == file_path]

    def get_worst_files(self, top_n: int = 10) -> List[tuple]:
        """
        获取问题最多的前N个文件

        Args:
            top_n: 返回的数量

        Returns:
            List[tuple]: (文件路径, 问题数) 的元组列表，按问题数降序排列
        """
        file_issue_count: Dict[str, int] = {}
        for issue in self.issues:
            file_issue_count[issue.file_path] = (
                file_issue_count.get(issue.file_path, 0) + 1
            )

        sorted_files = sorted(
            file_issue_count.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        return sorted_files[:top_n]

    def to_dict(self) -> Dict[str, Any]:
        """
        序列化为字典格式

        用于JSON序列化和API响应。

        Returns:
            Dict: 完整的报告数据字典
        """
        return {
            "project_name": self.project_name,
            "project_path": str(self.project_path),
            "plc_output_path": str(self.plc_output_path),
            "scan_time": self.scan_time.isoformat(),
            "summary": {
                "total_scanned_files": len(self.scanned_files),
                "total_issues": self.total_issues,
                "error_count": self.error_count,
                "warning_count": self.warning_count,
                "info_count": self.info_count,
                "hint_count": self.hint_count,
                "is_passed": self.is_passed,
                "pass_rate": round(self.pass_rate, 2),
                "quality_score": self.quality_score,
            },
            "scanned_files": self.scanned_files,
            "issues": [issue.to_dict() for issue in self.issues],
            "analysis": {
                "ob_fb_call_chain": self.ob_fb_call_chain,
                "missing_implementations": self.missing_implementations,
                "stub_misuses": self.stub_misuses,
            },
        }

    def to_json_string(self, indent: int = 2) -> str:
        """
        转换为JSON字符串

        Args:
            indent: 缩进空格数

        Returns:
            str: 格式化的JSON字符串
        """
        import json
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    def to_markdown(self) -> str:
        """
        生成Markdown格式的诊断报告

        生成包含统计摘要、详细问题列表、调用链分析和修复建议的完整报告。

        Returns:
            str: 格式化的Markdown报告文本
        """
        lines = []

        # 报告标题
        lines.append("# LSP兼容性诊断报告")
        lines.append("")
        lines.append(f"**项目名称**: {self.project_name}")
        lines.append(f"**扫描时间**: {self.scan_time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(
            f"**PLC输出目录**: `{self.plc_output_path or '未指定'}`"
        )
        lines.append("")

        # 统计摘要
        lines.append("---")
        lines.append("## 📊 统计摘要")
        lines.append("")

        # 状态指示器
        status_icon = "✅ 通过" if self.is_passed else "❌ 未通过"
        status_color = "green" if self.is_passed else "red"

        lines.append(f"| 指标 | 数值 |")
        lines.append("|------|------|")
        lines.append(f"| 扫描文件数 | {len(self.scanned_files)} |")
        lines.append(f"| **问题总数** | **{self.total_issues}** |")
        lines.append(f"| 🔴 错误 | {self.error_count} |")
        lines.append(f"| 🟡 警告 | {self.warning_count} |")
        lines.append(f"| 🔵 信息 | {self.info_count} |")
        lines.append(f"| 🟢 提示 | {self.hint_count} |")
        lines.append(f"| <span style='color:{status_color}'>检查状态</span> | {status_icon} |")
        lines.append(f"| 通过率 | {self.pass_rate:.1f}% |")
        lines.append(f"| 质量评分 | **{self.quality_score}/100** |")
        lines.append("")

        # 问题最多的文件
        if self.issues:
            worst_files = self.get_worst_files(5)
            if worst_files:
                lines.append("### ⚠️ 问题最集中的文件")
                lines.append("")
                lines.append("| 排名 | 文件 | 问题数 |")
                lines.append("|------|------|--------|")
                for i, (file_path, count) in enumerate(worst_files, 1):
                    filename = Path(file_path).name
                    lines.append(f"| {i} | `{filename}` | {count} |")
                lines.append("")

        # 详细问题列表
        if self.issues:
            lines.append("---")
            lines.append("## 🔍 详细问题列表")
            lines.append("")

            # 按严重级别分组
            severity_order = [
                (DiagnosticSeverity.ERROR, "🔴 错误"),
                (DiagnosticSeverity.WARNING, "🟡 警告"),
                (DiagnosticSeverity.INFO, "🔵 信息"),
                (DiagnosticSeverity.HINT, "🟢 提示"),
            ]

            for severity, title in severity_order:
                issues_by_severity = self.get_issues_by_severity(severity)
                if issues_by_severity:
                    lines.append(f"### {title} ({len(issues_by_severity)} 个)")
                    lines.append("")

                    for idx, issue in enumerate(issues_by_severity, 1):
                        lines.append(f"#### {idx}. [{issue.rule_id}] {issue.message}")
                        lines.append("")
                        lines.append(f"- **位置**: `{issue.location_str}`")
                        if issue.source_line:
                            lines.append(f"- **源码位置**: `{issue.source_line}`")
                        if issue.category:
                            lines.append(f"- **分类**: `{issue.category}`")
                        if issue.related_symbols:
                            symbols = ", ".join(issue.related_symbols)
                            lines.append(f"- **相关符号**: {symbols}")
                        if issue.code_snippet:
                            lines.append("- **代码片段**:")
                            lines.append("```go")
                            lines.append(issue.code_snippet)
                            lines.append("```")
                        if issue.suggestion:
                            lines.append(f"- **修复建议**: {issue.suggestion}")
                        lines.append("")

        # OB→FB调用链分析
        if self.ob_fb_call_chain:
            lines.append("---")
            lines.append("## 🔗 OB→FB调用链分析")
            lines.append("")
            lines.append("以下是从OB块检测到的FB调用关系：")
            lines.append("")

            for ob_name, fb_list in self.ob_fb_call_chain.items():
                lines.append(f"### {ob_name}")
                lines.append("")
                if fb_list:
                    lines.append("调用的FB/FC:")
                    for fb_name in fb_list:
                        lines.append(f"  - `{fb_name}`")
                else:
                    lines.append("* 未检测到FB调用*")
                lines.append("")

        # 缺失实现
        if self.missing_implementations:
            lines.append("---")
            lines.append("## ❌ 缺失实现")
            lines.append("")
            lines.append("以下FB/FC在OB中被调用但缺少实现：")
            lines.append("")
            for item in self.missing_implementations:
                caller = item.get("caller", "未知")
                missing = item.get("missing_fb", "未知")
                location = item.get("location", "")
                lines.append(f"- **{missing}** (被 `{caller}` 调用)")
                if location:
                    lines.append(f"  - 位置: {location}")
            lines.append("")

        # Stub误用检测
        if self.stub_misuses:
            lines.append("---")
            lines.append("## ⚠️ Builtin Stub误用检测")
            lines.append("")
            lines.append("检测到以下可能的builtin stub误用模式：")
            lines.append("")
            for item in self.stub_misuses:
                stub_name = item.get("stub_name", "未知")
                file_path = item.get("file_path", "")
                line_num = item.get("line_number", 0)
                usage = item.get("usage_pattern", "")

                lines.append(f"### Stub: `{stub_name}`")
                lines.append("")
                lines.append(f"- **文件**: `{Path(file_path).name}`")
                lines.append(f"- **行号**: {line_num}")
                if usage:
                    lines.append(f"- **使用模式**: `{usage}`")
                lines.append("")

        # 修复建议汇总
        if self.has_errors or self.has_issues:
            lines.append("---")
            lines.append("## 💡 修复建议汇总")
            lines.append("")

            # 按规则分组统计
            rule_stats: Dict[str, tuple] = {}
            for issue in self.issues:
                if issue.rule_id not in rule_stats:
                    rule_stats[issue.rule_id] = (issue.message, 0)
                msg, count = rule_stats[issue.rule_id]
                rule_stats[issue.rule_id] = (msg, count + 1)

            lines.append("| 规则ID | 描述 | 出现次数 | 优先级 |")
            lines.append("|--------|------|----------|--------|")
            for rule_id, (msg, count) in sorted(rule_stats.items()):
                priority = "高" if "ERROR" in rule_id else ("中" if "WARNING" in rule_id else "低")
                lines.append(f"| {rule_id} | {msg} | {count} | {priority} |")
            lines.append("")

        # 报告尾部
        lines.append("---")
        lines.append("")
        lines.append(
            f"*报告生成时间: {self.scan_time.strftime('%Y-%m-%d %H:%M:%S')}*"
        )
        lines.append(
            "*由 PLC项目管理工具 LSP兼容性检查器 自动生成*"
        )

        return "\n".join(lines)

    def generate_summary_text(self) -> str:
        """
        生成简短的摘要文本

        适用于命令行输出或通知消息。

        Returns:
            str: 格式化的摘要文本
        """
        lines = [
            "=" * 70,
            "LSP兼容性诊断报告摘要",
            "=" * 70,
            f"项目名称: {self.project_name}",
            f"扫描时间: {self.scan_time.strftime('%Y-%m-%d %H:%M:%S')}",
            "-" * 70,
            "统计摘要:",
            f"  • 扫描文件数: {len(self.scanned_files)}",
            f"  • 问题总数: {self.total_issues}",
            f"    - 错误: {self.error_count}",
            f"    - 警告: {self.warning_count}",
            f"    - 信息: {self.info_count}",
            f"    - 提示: {self.hint_count}",
            f"  • 检查状态: {'✅ 通过' if self.is_passed else '❌ 未通过'}",
            f"  • 质量评分: {self.quality_score}/100",
            "-" * 70,
        ]

        if self.total_issues > 0:
            lines.append("\n问题最集中的文件:")
            for i, (file_path, count) in enumerate(self.get_worst_files(5), 1):
                filename = Path(file_path).name
                lines.append(f"  {i}. {filename}: {count} 个问题")

        lines.append("=" * 70)
        return "\n".join(lines)

    def save_to_file(self, output_path: str, format: str = "markdown") -> None:
        """
        将报告保存到文件

        Args:
            output_path: 输出文件路径
            format: 输出格式 ('markdown', 'json')
        """
        output_file = Path(output_path)

        if format.lower() == "json":
            content = self.to_json_string()
        else:
            content = self.to_markdown()

        output_file.write_text(content, encoding="utf-8")
