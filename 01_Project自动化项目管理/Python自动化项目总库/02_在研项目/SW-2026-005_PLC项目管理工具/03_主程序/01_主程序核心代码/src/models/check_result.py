# -*- coding: utf-8 -*-
"""
检查结果数据模型

定义规范检查结果的完整数据结构，
包括违规记录、检查结果汇总和项目级报告。
支持序列化为JSON格式以便持久化和传输。
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path

from src.checkers.base_checker import Severity


@dataclass
class Violation:
    """
    代码违规记录数据类

    记录单个规范违规的完整信息，包括位置、问题描述和建议修复方案。

    Attributes:
        rule_id: 触发的规则ID
        severity: 违规严重级别
        message: 违规描述消息
        file_path: 违规所在文件路径
        line_number: 违规所在行号（从1开始）
        column: 违规所在列号（从1开始，可选）
        suggestion: 修复建议（可选）
        code_snippet: 违规代码片段（可选，用于快速定位）
    """
    rule_id: str
    severity: Severity
    message: str
    file_path: str = ""
    line_number: int = 0
    column: int = 0
    suggestion: Optional[str] = None
    code_snippet: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        将违规记录转换为字典

        Returns:
            Dict: 包含所有字段的可序列化字典
        """
        return {
            "rule_id": self.rule_id,
            "severity": self.severity.name,
            "severity_value": int(self.severity),
            "message": self.message,
            "file_path": str(self.file_path),
            "line_number": self.line_number,
            "column": self.column,
            "suggestion": self.suggestion,
            "code_snippet": self.code_snippet,
        }

    @property
    def location_str(self) -> str:
        """
        格式化的位置字符串

        Returns:
            str: 格式为 "文件路径:行号:列号"
        """
        if self.file_path and self.line_number > 0:
            loc = f"{Path(self.file_path).name}:{self.line_number}"
            if self.column > 0:
                loc += f":{self.column}"
            return loc
        return self.file_path or "未知位置"

    def __str__(self) -> str:
        """人类可读的违规描述"""
        return (
            f"[{self.severity.name}] {self.location_str}: "
            f"{self.message} (规则: {self.rule_id})"
        )


@dataclass
class CheckResult:
    """
    单次检查的结果数据类

    包含对单个文件或代码段进行检查产生的所有违规记录和统计信息。

    Attributes:
        source_file: 被检查的源文件路径
        violations: 发现的违规记录列表
        check_time: 检查完成时间戳
        error_count: 错误级别的违规数
        warning_count: 警告级别的违规数
        info_count: 信息级别的违规数
    """
    source_file: str = ""
    violations: List[Violation] = field(default_factory=list)
    check_time: datetime = field(default_factory=datetime.now)
    error_count: int = 0
    warning_count: int = 0
    info_count: int = 0

    def __post_init__(self):
        """初始化后自动计算统计数据"""
        self._recalculate_stats()

    def add_violation(self, violation: Violation) -> None:
        """
        添加一条违规记录

        Args:
            violation: 违规记录对象
        """
        self.violations.append(violation)
        self._update_stats_for_violation(violation)

    def add_violations(self, violations: List[Violation]) -> None:
        """
        批量添加违规记录

        Args:
            violations: 违规记录列表
        """
        self.violations.extend(violations)
        for v in violations:
            self._update_stats_for_violation(v)

    def _update_stats_for_violation(self, violation: Violation) -> None:
        """根据违规记录更新统计计数"""
        if violation.severity == Severity.ERROR:
            self.error_count += 1
        elif violation.severity == Severity.WARNING:
            self.warning_count += 1
        elif violation.severity == Severity.INFO:
            self.info_count += 1

    def _recalculate_stats(self) -> None:
        """重新计算所有统计数据"""
        self.error_count = sum(
            1 for v in self.violations if v.severity == Severity.ERROR
        )
        self.warning_count = sum(
            1 for v in self.violations if v.severity == Severity.WARNING
        )
        self.info_count = sum(
            1 for v in self.violations if v.severity == Severity.INFO
        )

    @property
    def total_violations(self) -> int:
        """违规总数"""
        return len(self.violations)

    @property
    def has_errors(self) -> bool:
        """是否包含错误级别的违规"""
        return self.error_count > 0

    @property
    def has_violations(self) -> bool:
        """是否包含任何违规"""
        return len(self.violations) > 0

    @property
    def is_passed(self) -> bool:
        """检查是否通过（无错误）"""
        return not self.has_errors

    def get_violations_by_severity(
        self, severity: Severity
    ) -> List[Violation]:
        """
        按严重级别筛选违规

        Args:
            severity: 要筛选的严重级别

        Returns:
            List[Violation]: 匹配的违规列表
        """
        return [v for v in self.violations if v.severity == severity]

    def get_violations_by_rule(self, rule_id: str) -> List[Violation]:
        """
        按规则ID筛选违规

        Args:
            rule_id: 规则ID

        Returns:
            List[Violation]: 匹配的违规列表
        """
        return [v for v in self.violations if v.rule_id == rule_id]

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式

        Returns:
            Dict: 可序列化的字典
        """
        return {
            "source_file": self.source_file,
            "check_time": self.check_time.isoformat(),
            "total_violations": self.total_violations,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "info_count": self.info_count,
            "is_passed": self.is_passed,
            "violations": [v.to_dict() for v in self.violations],
        }


@dataclass
class CheckReport:
    """
    项目级检查报告数据类

    汇总整个项目的检查结果，提供整体质量评估和详细分析。
    支持序列化为JSON格式以便生成报告文件。

    Attributes:
        project_name: 项目名称
        project_path: 项目根目录路径
        results: 各文件的检查结果列表
        report_time: 报告生成时间
        total_files_checked: 检查的文件总数
        total_violations: 违规总数
        total_errors: 错误总数
        total_warnings: 警告总数
        total_infos: 信息提示总数
    """
    project_name: str = ""
    project_path: str = ""
    results: List[CheckResult] = field(default_factory=list)
    report_time: datetime = field(default_factory=datetime.now)
    total_files_checked: int = 0
    total_violations: int = 0
    total_errors: int = 0
    total_warnings: int = 0
    total_infos: int = 0

    def __post_init__(self):
        """初始化后自动计算汇总统计"""
        self._recalculate_summary()

    def add_result(self, result: CheckResult) -> None:
        """
        添加单个文件的检查结果

        Args:
            result: 文件检查结果
        """
        self.results.append(result)
        self.total_files_checked += 1
        self._update_summary_with_result(result)

    def _update_summary_with_result(self, result: CheckResult) -> None:
        """根据单个结果更新汇总统计"""
        self.total_violations += result.total_violations
        self.total_errors += result.error_count
        self.total_warnings += result.warning_count
        self.total_infos += result.info_count

    def _recalculate_summary(self) -> None:
        """重新计算所有汇总统计"""
        self.total_files_checked = len(self.results)
        self.total_violations = sum(r.total_violations for r in self.results)
        self.total_errors = sum(r.error_count for r in self.results)
        self.total_warnings = sum(r.warning_count for r in self.results)
        self.total_infos = sum(r.info_count for r in self.results)

    @property
    def passed_files(self) -> int:
        """通过的文件数（无错误）"""
        return sum(1 for r in self.results if r.is_passed)

    @property
    def failed_files(self) -> int:
        """未通过的文件数（有错误）"""
        return self.total_files_checked - self.passed_files

    @property
    def pass_rate(self) -> float:
        """通过率（百分比）"""
        if self.total_files_checked == 0:
            return 0.0
        return (self.passed_files / self.total_files_checked) * 100

    @property
    def quality_score(self) -> float:
        """
        质量评分（0-100分）

        基于违规密度和严重程度计算的加权分数
        """
        if self.total_files_checked == 0:
            return 100.0

        # 加权扣分机制
        error_penalty = self.total_errors * 10
        warning_penalty = self.total_warnings * 3
        info_penalty = self.total_infos * 1

        total_penalty = error_penalty + warning_penalty + info_penalty
        score = max(0, 100 - total_penalty)

        return round(score, 2)

    def get_result_by_file(self, file_path: str) -> Optional[CheckResult]:
        """
        根据文件路径获取检查结果

        Args:
            file_path: 文件路径

        Returns:
            Optional[CheckResult]: 检查结果，不存在时返回None
        """
        for result in self.results:
            if result.source_file == file_path:
                return result
        return None

    def get_worst_files(self, top_n: int = 10) -> List[CheckResult]:
        """
        获取违规最多的前N个文件

        Args:
            top_n: 返回的数量

        Returns:
            List[CheckResult]: 按违规数降序排列的结果列表
        """
        sorted_results = sorted(
            self.results,
            key=lambda r: r.total_violations,
            reverse=True,
        )
        return sorted_results[:top_n]

    def to_dict(self) -> Dict[str, Any]:
        """
        序列化为字典格式

        用于JSON序列化和报告生成。

        Returns:
            Dict: 完整的报告数据字典
        """
        return {
            "project_name": self.project_name,
            "project_path": str(self.project_path),
            "report_time": self.report_time.isoformat(),
            "summary": {
                "total_files_checked": self.total_files_checked,
                "passed_files": self.passed_files,
                "failed_files": self.failed_files,
                "pass_rate": round(self.pass_rate, 2),
                "quality_score": self.quality_score,
                "total_violations": self.total_violations,
                "total_errors": self.total_errors,
                "total_warnings": self.total_warnings,
                "total_infos": self.total_infos,
            },
            "file_results": [r.to_dict() for r in self.results],
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

    def generate_summary_text(self) -> str:
        """
        生成人类可读的摘要文本

        Returns:
            str: 格式化的报告摘要
        """
        lines = [
            "=" * 60,
            f"PLC代码规范检查报告",
            "=" * 60,
            f"项目名称: {self.project_name}",
            f"检查时间: {self.report_time.strftime('%Y-%m-%d %H:%M:%S')}",
            "-" * 60,
            "📊 统计摘要:",
            f"  • 检查文件数: {self.total_files_checked}",
            f"  • 通过文件数: {self.passed_files} ({self.pass_rate:.1f}%)",
            f"  • 违规总数: {self.total_violations}",
            f"    - 错误: {self.total_errors}",
            f"    - 警告: {self.total_warnings}",
            f"    - 提示: {self.total_infos}",
            f"  • 质量评分: {self.quality_score}/100",
            "-" * 60,
        ]

        if self.total_violations > 0:
            lines.append("\n⚠️  问题最多的文件:")
            for i, result in enumerate(self.get_worst_files(5), 1):
                lines.append(
                    f"  {i}. {result.source_file}: "
                    f"{result.total_violations} 个问题"
                )

        lines.append("=" * 60)
        return "\n".join(lines)
