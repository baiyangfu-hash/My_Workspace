# -*- coding: utf-8 -*-
"""
项目健康度指标数据模型

定义健康度分析器的完整数据结构，
包括各维度得分、等级评定和综合指标。
支持序列化为JSON格式以便UI展示和持久化。
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any
from datetime import datetime


class HealthGrade(Enum):
    """
    健康等级枚举

    定义项目的整体健康状态等级：
    - A: 优秀 (>85分)
    - B: 良好 (70-85分)
    - C: 一般 (55-70分)
    - D: 较差 (<55分)
    """
    EXCELLENT = "A"
    GOOD = "B"
    FAIR = "C"
    POOR = "D"

    @classmethod
    def from_score(cls, score: float) -> 'HealthGrade':
        """
        根据分数确定健康等级

        Args:
            score: 健康度分数 (0-100)

        Returns:
            HealthGrade: 对应的健康等级
        """
        if score > 85:
            return cls.EXCELLENT
        elif score >= 70:
            return cls.GOOD
        elif score >= 55:
            return cls.FAIR
        else:
            return cls.POOR

    @property
    def label(self) -> str:
        """中文标签"""
        labels = {
            self.EXCELLENT: "优秀",
            self.GOOD: "良好",
            self.FAIR: "一般",
            self.POOR: "较差"
        }
        return labels[self]

    @property
    def color(self) -> str:
        """UI展示颜色（十六进制）"""
        colors = {
            self.EXCELLENT: "#52c41a",  # 绿色
            self.GOOD: "#1890ff",       # 蓝色
            self.FAIR: "#faad14",       # 橙色
            self.POOR: "#ff4d4f"        # 红色
        }
        return colors[self]


class ComplianceLevel(Enum):
    """
    规范符合度等级

    定义规范检查的通过率等级：
    - 优秀 (>90%)
    - 良好 (70-90%)
    - 及格 (50-70%)
    - 不及格 (<50%)
    """
    EXCELLENT = "优秀"
    GOOD = "良好"
    PASS = "及格"
    FAIL = "不及格"

    @classmethod
    def from_rate(cls, rate: float) -> 'ComplianceLevel':
        """
        根据通过率确定符合度等级

        Args:
            rate: 通过率百分比 (0-100)

        Returns:
            ComplianceLevel: 对应的等级
        """
        if rate > 90:
            return cls.EXCELLENT
        elif rate >= 70:
            return cls.GOOD
        elif rate >= 50:
            return cls.PASS
        else:
            return cls.FAIL


class LibraryStatus(Enum):
    """
    共享库引用状态枚举

    定义库引用的验证状态：
    - OK: 正常（路径有效，库存在）
    - INVALID_PATH: 路径无效（路径不存在）
    - MISSING: 缺失（.plc.json中未配置或配置错误）
    """
    OK = "正常"
    INVALID_PATH = "路径无效"
    MISSING = "缺失"

    @property
    def icon(self) -> str:
        """状态图标"""
        icons = {
            self.OK: "\u2705",           # ✅
            self.INVALID_PATH: "\u26a0\ufe0f",  # ⚠️
            self.MISSING: "\u274c"      # ❌
        }
        return icons[self]


@dataclass
class DimensionScore:
    """
    单维度得分数据类

    记录单个评估维度的得分详情。

    Attributes:
        name: 维度名称（如"规范符合度"、"问题严重程度"）
        score: 得分 (0-100)
        weight: 权重占比 (0-1)
        grade: 等级标签
        details: 详细说明或子项得分
    """
    name: str
    score: float
    weight: float
    grade: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "name": self.name,
            "score": round(self.score, 2),
            "weight": round(self.weight, 3),
            "grade": self.grade,
            "details": self.details
        }


@dataclass
class ComplianceDetail:
    """
    规范符合度详细数据

    Attributes:
        category: 检查类别（定时器/命名/语法/配置等）
        total_checks: 总检查项数
        passed_checks: 通过的检查项数
        pass_rate: 通过率百分比
        level: 符合度等级
    """
    category: str
    total_checks: int
    passed_checks: int
    pass_rate: float
    level: str

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "category": self.category,
            "total_checks": self.total_checks,
            "passed_checks": self.passed_checks,
            "pass_rate": round(self.pass_rate, 2),
            "level": self.level
        }


@dataclass
class IssueDistribution:
    """
    问题分布统计数据

    Attributes:
        by_severity: 按严重级别统计 {ERROR: n, WARNING: n, INFO: n}
        by_category: 按检查类别统计 {类别名: n}
        worst_files: 最差的Top N文件列表 [(文件路径, 违规数), ...]
        total_issues: 问题总数
    """
    by_severity: Dict[str, int] = field(default_factory=dict)
    by_category: Dict[str, int] = field(default_factory=dict)
    worst_files: List[tuple] = field(default_factory=list)
    total_issues: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "by_severity": self.by_severity,
            "by_category": self.by_category,
            "worst_files": [
                {"file": f[0], "violations": f[1]}
                for f in self.worst_files
            ],
            "total_issues": self.total_issues
        }


@dataclass
class LibraryInfo:
    """
    共享库引用信息

    Attributes:
        name: 库名称
        path: 库路径（相对或绝对）
        status: 引用状态
        version: 版本号（如果可获取）
        error_message: 错误信息（如果有问题）
    """
    name: str
    path: str
    status: LibraryStatus
    version: Optional[str] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "name": self.name,
            "path": self.path,
            "status": self.status.value,
            "icon": self.status.icon,
            "version": self.version,
            "error_message": self.error_message
        }


@dataclass
class StructureCompliance:
    """
    项目结构合规性信息

    Attributes:
        required_dirs: 必需目录列表
        optional_dirs: 可选目录列表
        existing_required: 已存在的必需目录
        missing_required: 缺失的必需目录
        existing_optional: 已存在的可选目录
        score: 结构评分 (0-100)
        max_score: 最高分 (通常为100)
    """
    required_dirs: List[str]
    optional_dirs: List[str]
    existing_required: List[str]
    missing_required: List[str]
    existing_optional: List[str]
    score: float
    max_score: float = 100.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "required_dirs": self.required_dirs,
            "optional_dirs": self.optional_dirs,
            "existing_required": self.existing_required,
            "missing_required": self.missing_required,
            "existing_optional": self.existing_optional,
            "score": round(self.score, 2),
            "max_score": self.max_score
        }


@dataclass
class ImprovementSuggestion:
    """
    改进建议条目

    Attributes:
        priority: 优先级 (高/中/低)
        category: 所属维度
        title: 建议标题
        description: 详细描述
        affected_items: 受影响的项目（文件、规则等）
    """
    priority: str
    category: str
    title: str
    description: str
    affected_items: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "priority": self.priority,
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "affected_items": self.affected_items
        }


@dataclass
class HealthMetrics:
    """
    项目健康度综合指标数据类

    容纳所有维度的评估结果，提供完整的健康度快照。
    支持序列化为JSON格式以便UI面板展示和持久化存储。

    Attributes:
        overall_score: 综合健康度总分 (0-100)
        health_grade: 健康等级 (A/B/C/D)
        dimensions: 各维度得分列表
        compliance_details: 规范符合度详细数据
        issue_distribution: 问题分布统计
        library_info_list: 共享库引用信息列表
        structure_compliance: 项目结构合规性
        suggestions: 改进建议列表
        analysis_time: 分析时间戳
        project_name: 项目名称
        project_path: 项目路径
    """
    overall_score: float = 0.0
    health_grade: HealthGrade = HealthGrade.POOR
    dimensions: List[DimensionScore] = field(default_factory=list)
    compliance_details: List[ComplianceDetail] = field(default_factory=list)
    issue_distribution: IssueDistribution = field(
        default_factory=IssueDistribution
    )
    library_info_list: List[LibraryInfo] = field(default_factory=list)
    structure_compliance: Optional[StructureCompliance] = None
    suggestions: List[ImprovementSuggestion] = field(default_factory=list)
    analysis_time: datetime = field(default_factory=datetime.now)
    project_name: str = ""
    project_path: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """
        序列化为字典格式

        用于JSON序列化和UI数据绑定。

        Returns:
            Dict: 完整的健康度指标字典
        """
        return {
            "overall_score": round(self.overall_score, 2),
            "health_grade": {
                "grade": self.health_grade.value,
                "label": self.health_grade.label,
                "color": self.health_grade.color
            },
            "dimensions": [d.to_dict() for d in self.dimensions],
            "compliance_details": [
                c.to_dict() for c in self.compliance_details
            ],
            "issue_distribution": self.issue_distribution.to_dict(),
            "library_info": [
                lib.to_dict() for lib in self.library_info_list
            ],
            "structure_compliance": (
                self.structure_compliance.to_dict()
                if self.structure_compliance else None
            ),
            "suggestions": [
                s.to_dict() for s in self.suggestions
            ],
            "analysis_time": self.analysis_time.isoformat(),
            "project_name": self.project_name,
            "project_path": self.project_path
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
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            indent=indent
        )

    def get_summary_text(self) -> str:
        """
        生成人类可读的摘要文本

        Returns:
            str: 格式化的健康度摘要
        """
        lines = [
            "=" * 60,
            f"\U0001f9ea 项目健康度分析报告",
            "=" * 60,
            f"项目名称: {self.project_name or '未知'}",
            f"分析时间: {self.analysis_time.strftime('%Y-%m-%d %H:%M:%S')}",
            "-" * 60,
            f"\U0001f4ca 综合评分: {self.overall_score:.1f}/100 "
            f"[{self.health_grade.value}级 - {self.health_grade.label}]",
            "-" * 60,
            "\U0001f4cb 各维度得分:"
        ]

        for dim in self.dimensions:
            lines.append(
                f"  \u2022 {dim.name}: {dim.score:.1f}分 "
                f"(权重{dim.weight*100:.0f}%) [{dim.grade}]"
            )

        lines.extend([
            "-" * 60,
            "\U0001f4a1 主要问题与建议:"
        ])

        if self.suggestions:
            for i, sug in enumerate(self.suggestions[:5], 1):
                lines.append(
                    f"  {i}. [{sug.priority}] {sug.title}"
                )
        else:
            lines.append("  \u2714\ufe0f 未发现明显问题，继续保持！")

        lines.append("=" * 60)
        return "\n".join(lines)


# 预定义的权重配置
WEIGHT_CONFIG = {
    "compliance": 0.40,      # 规范符合度权重
    "issues": 0.30,          # 问题严重程度权重
    "library": 0.15,         # 库引用状态权重
    "structure": 0.15        # 结构合规性权重
}

# 预定义的标准目录结构模板
STANDARD_DIRECTORIES = {
    "required": ["DB1", "OB1", "common", "Test"],
    "optional": ["feeder", "pickplace", "external"]
}
