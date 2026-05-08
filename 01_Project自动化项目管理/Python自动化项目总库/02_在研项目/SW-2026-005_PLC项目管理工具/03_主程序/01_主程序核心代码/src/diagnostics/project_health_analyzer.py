# -*- coding: utf-8 -*-
"""
项目健康度分析器

实现PLC项目的综合健康度评估功能，包括：
1. 规范符合度计算（按类别分级）
2. 代码质量问题分布统计
3. 共享库引用状态分析
4. 项目结构合规性评分
5. 综合健康度加权评分
6. 健康度卡片数据生成

该分析器集成CheckReport模型，支持增量更新，
提供清晰的改进建议，可直接集成到UI面板中。
"""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
from collections import defaultdict

from src.models.check_result import CheckReport, CheckResult, Violation
from src.checkers.base_checker import Severity
from src.models.health_metrics import (
    HealthMetrics,
    HealthGrade,
    DimensionScore,
    ComplianceDetail,
    ComplianceLevel,
    IssueDistribution,
    LibraryInfo,
    LibraryStatus,
    StructureCompliance,
    ImprovementSuggestion,
    WEIGHT_CONFIG,
    STANDARD_DIRECTORIES
)
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ProjectHealthAnalyzer:
    """
    项目健康度分析器

    对PLC项目进行全面的质量评估，从多个维度计算健康度指标。
    支持基于检查报告的增量更新，提供可操作的建议。

    使用示例:
        >>> analyzer = ProjectHealthAnalyzer()
        >>> metrics = analyzer.analyze(check_report, project_path)
        >>> print(metrics.overall_score)  # 综合得分
        >>> print(metrics.to_json_string())  # JSON输出
    """

    def __init__(self):
        """初始化分析器实例"""
        self._weight_config = WEIGHT_CONFIG.copy()
        self._standard_dirs = STANDARD_DIRECTORIES.copy()
        self._previous_metrics: Optional[HealthMetrics] = None

    @property
    def weight_config(self) -> Dict[str, float]:
        """获取当前权重配置"""
        return self._weight_config.copy()

    def set_weight_config(self, config: Dict[str, float]) -> None:
        """
        自定义权重配置

        Args:
            config: 权重字典，键为维度名(compliance/issues/library/structure)
                   值为权重(0-1)，所有权重之和应为1.0
        """
        total = sum(config.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"权重总和必须为1.0，当前为{total:.3f}")

        for key in config:
            if key not in self._weight_config:
                raise ValueError(f"未知的权重维度: {key}")

        self._weight_config.update(config)
        logger.info("权重配置已更新")

    def analyze(
        self,
        check_report: CheckReport,
        project_path: str = "",
        previous_metrics: Optional[HealthMetrics] = None
    ) -> HealthMetrics:
        """
        执行完整的健康度分析

        这是主要入口方法，依次执行各维度的分析并汇总结果。

        Args:
            check_report: 规范检查器的完整报告
            project_path: 项目根目录路径（用于结构分析和库检测）
            previous_metrics: 上一次的分析结果（用于增量比较）

        Returns:
            HealthMetrics: 完整的健康度指标对象
        """
        logger.info(f"开始健康度分析 - 项目: {check_report.project_name}")

        # 保存历史数据用于增量比较
        if previous_metrics:
            self._previous_metrics = previous_metrics

        # 1. 计算规范符合度
        compliance_score, compliance_details = \
            self.calculate_compliance_score(check_report)

        # 2. 分析问题分布
        issue_score, issue_distribution = \
            self.analyze_issue_distribution(check_report)

        # 3. 分析库引用状态
        library_score, library_info_list = \
            self.analyze_library_status(project_path)

        # 4. 分析结构合规性
        structure_score, structure_compliance = \
            self.analyze_structure_compliance(project_path)

        # 5. 计算综合评分
        overall_score, dimensions = self.calculate_overall_score(
            compliance_score=compliance_score,
            issue_score=issue_score,
            library_score=library_score,
            structure_score=structure_score
        )

        # 6. 生成改进建议
        suggestions = self.generate_suggestions(
            check_report=check_report,
            compliance_details=compliance_details,
            issue_distribution=issue_distribution,
            library_info_list=library_info_list,
            structure_compliance=structure_compliance
        )

        # 构建最终结果
        metrics = HealthMetrics(
            overall_score=overall_score,
            health_grade=HealthGrade.from_score(overall_score),
            dimensions=dimensions,
            compliance_details=compliance_details,
            issue_distribution=issue_distribution,
            library_info_list=library_info_list,
            structure_compliance=structure_compliance,
            suggestions=suggestions,
            analysis_time=datetime.now(),
            project_name=check_report.project_name,
            project_path=project_path
        )

        logger.info(
            f"健康度分析完成 - 总分: {overall_score:.1f}, "
            f"等级: {metrics.health_grade.value}"
        )
        return metrics

    def calculate_compliance_score(
        self,
        report: CheckReport
    ) -> Tuple[float, List[ComplianceDetail]]:
        """
        计算规范符合度分数和详细数据

        按检查类别分别计算通过率，然后加权平均得到综合得分。

        算法说明：
        - 通过率 = 通过的检查项 / 总检查项 * 100%
        - 分级：优秀(>90%) / 良好(70-90%) / 及格(50-70%) / 不及格(<50%)
        - 类别包括：定时器、命名、语法、配置等

        Args:
            report: 规范检查报告

        Returns:
            Tuple[float, List[ComplianceDetail]]: (综合得分, 各类别详情列表)
        """
        logger.debug("计算规范符合度...")

        # 按类别分组统计违规
        category_stats: Dict[str, Dict] = defaultdict(lambda: {
            "total": 0,
            "passed": 0,
            "violations": []
        })

        # 遍历所有检查结果，按规则ID前缀分类
        for result in report.results:
            for violation in result.violations:
                # 从rule_id提取类别 (如 TIMER_001 -> timer)
                category = self._extract_category(violation.rule_id)
                category_stats[category]["total"] += 1
                category_stats[category]["violations"].append(violation)

        # 如果没有检查数据，返回满分
        if not category_stats:
            detail = ComplianceDetail(
                category="总体",
                total_checks=0,
                passed_checks=0,
                pass_rate=100.0,
                level="优秀"
            )
            return 100.0, [detail]

        # 计算每个类别的通过率和等级
        details: List[ComplianceDetail] = []
        category_scores: List[float] = []

        for category, stats in category_stats.items():
            # 通过数 = 总数 - 违规数（简化处理）
            passed = max(0, stats["total"] - len(stats["violations"]))
            total = stats["total"]

            pass_rate = (passed / total * 100) if total > 0 else 100.0
            level = ComplianceLevel.from_rate(pass_rate).value

            detail = ComplianceDetail(
                category=category,
                total_checks=total,
                passed_checks=passed,
                pass_rate=pass_rate,
                level=level
            )
            details.append(detail)
            category_scores.append(pass_rate)

        # 综合得分：各类别通过率的平均值
        overall = sum(category_scores) / len(category_scores) \
            if category_scores else 100.0

        logger.debug(f"规范符合度: {overall:.1f}%")
        return overall, details

    def _extract_category(self, rule_id: str) -> str:
        """
        从规则ID提取类别名称

        Args:
            rule_id: 规则ID (如 "TIMER_001", "NAMING_002")

        Returns:
            str: 类别名称 (小写)
        """
        if "_" in rule_id:
            prefix = rule_id.split("_")[0].lower()
            # 映射常见前缀到中文类别名
            mapping = {
                "timer": "定时器",
                "naming": "命名",
                "syntax": "语法",
                "config": "配置",
                "comment": "注释"
            }
            return mapping.get(prefix, prefix)
        return rule_id

    def analyze_issue_distribution(
        self,
        report: CheckReport
    ) -> Tuple[float, IssueDistribution]:
        """
        分析代码质量问题分布

        从多个角度统计问题分布：
        1. 按严重级别分类 (Error/Warning/Info)
        2. 按检查类别分类
        3. 按文件分类（找出最差的Top 10）

        评分算法：
        - 基础分100分
        - Error每条扣10分，Warning扣3分，Info扣1分
        - 最低0分

        Args:
            report: 规范检查报告

        Returns:
            Tuple[float, IssueDistribution]: (问题严重程度得分, 分布统计)
        """
        logger.debug("分析问题分布...")

        # 1. 按严重级别统计
        by_severity = {
            "ERROR": report.total_errors,
            "WARNING": report.total_warnings,
            "INFO": report.total_infos
        }

        # 2. 按检查类别统计
        by_category: Dict[str, int] = defaultdict(int)
        for result in report.results:
            for violation in result.violations:
                category = self._extract_category(violation.rule_id)
                by_category[category] += 1

        # 3. 最差的Top 10文件
        worst_files = [
            (r.source_file, r.total_violations)
            for r in report.get_worst_files(top_n=10)
            if r.total_violations > 0
        ]

        # 4. 计算得分（基于严重程度加权扣分）
        base_score = 100.0
        error_penalty = by_severity["ERROR"] * 10
        warning_penalty = by_severity["WARNING"] * 3
        info_penalty = by_severity["INFO"] * 1

        total_penalty = error_penalty + warning_penalty + info_penalty
        score = max(0.0, base_score - total_penalty)

        distribution = IssueDistribution(
            by_severity=by_severity,
            by_category=dict(by_category),
            worst_files=worst_files,
            total_issues=report.total_violations
        )

        logger.debug(
            f"问题分布 - 得分:{score:.1f}, "
            f"Error:{by_severity['ERROR']}, "
            f"Warning:{by_severity['WARNING']}, "
            f"Info:{by_severity['INFO']}"
        )
        return score, distribution

    def analyze_library_status(
        self,
        project_path: str = ""
    ) -> Tuple[float, List[LibraryInfo]]:
        """
        分析共享库引用状态

        检测.plc.json配置文件中的libraries字段：
        1. 验证字段存在性和格式正确性
        2. 检查引用路径的有效性
        3. 尝试获取版本信息（如果可用）

        评分算法：
        - 所有库正常：100分
        - 有路径无效的库：60分
        - 完全缺失或配置错误：0分

        Args:
            project_path: 项目根目录路径

        Returns:
            Tuple[float, List[LibraryInfo]]: (库状态得分, 库信息列表)
        """
        logger.debug("分析库引用状态...")

        library_info_list: List[LibraryInfo] = []

        if not project_path:
            # 无法检测时返回默认值
            info = LibraryInfo(
                name="未知",
                path="",
                status=LibraryStatus.MISSING,
                error_message="未提供项目路径"
            )
            return 0.0, [info]

        plc_json_path = Path(project_path) / ".plc.json"

        if not plc_json_path.exists():
            info = LibraryInfo(
                name=".plc.json",
                path=str(plc_json_path),
                status=LibraryStatus.MISSING,
                error_message="配置文件不存在"
            )
            return 0.0, [info]

        try:
            with open(plc_json_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            info = LibraryInfo(
                name=".plc.json",
                path=str(plc_json_path),
                status=LibraryStatus.MISSING,
                error_message=f"配置文件读取失败: {str(e)}"
            )
            return 0.0, [info]

        # 提取libraries字段（注意：必须是libraries不是libraryDirectories）
        libraries = config.get("libraries", [])

        if not libraries:
            info = LibraryInfo(
                name="共享库",
                path="",
                status=LibraryStatus.MISSING,
                error_message="未配置共享库引用(libraries字段为空)"
            )
            return 40.0, [info]

        # 验证每个库的路径
        valid_count = 0
        invalid_count = 0

        for lib_entry in libraries:
            if isinstance(lib_entry, dict):
                lib_name = lib_entry.get("name", "未知库")
                lib_path = lib_entry.get("path", "")
            elif isinstance(lib_entry, str):
                lib_name = lib_entry
                lib_path = lib_entry
            else:
                continue

            # 解析路径（支持相对路径）
            if lib_path:
                full_path = Path(project_path) / lib_path
            else:
                full_path = None

            # 检查路径有效性
            if full_path and full_path.exists():
                lib_info = LibraryInfo(
                    name=lib_name,
                    path=lib_path,
                    status=LibraryStatus.OK,
                    version=self._try_get_version(full_path)
                )
                valid_count += 1
            else:
                lib_info = LibraryInfo(
                    name=lib_name,
                    path=lib_path,
                    status=LibraryStatus.INVALID_PATH,
                    error_message=(
                        f"库路径不存在: {lib_path}"
                        if lib_path else "未指定路径"
                    )
                )
                invalid_count += 1

            library_info_list.append(lib_info)

        # 计算得分
        total_libs = valid_count + invalid_count
        if total_libs == 0:
            score = 100.0
        elif invalid_count == 0:
            score = 100.0
        elif valid_count == 0:
            score = 20.0
        else:
            # 部分有效：按比例计分
            score = (valid_count / total_libs) * 80 + 20

        logger.debug(
            f"库引用状态 - 得分:{score:.1f}, "
            f"有效:{valid_count}, 无效:{invalid_count}"
        )
        return score, library_info_list

    def _try_get_version(self, lib_path: Path) -> Optional[str]:
        """
        尝试获取库版本号

        通过查找常见的版本标识文件或配置来获取版本。

        Args:
            lib_path: 库根目录路径

        Returns:
            Optional[str]: 版本号字符串，无法获取时返回None
        """
        # 尝试多种方式获取版本
        version_files = ["version.txt", "VERSION", ".version"]
        for vf in version_files:
            vfile = lib_path / vf
            if vfile.exists():
                try:
                    return vfile.read_text(encoding='utf-8').strip()
                except Exception:
                    continue

        # 尝试从package.json或其他配置文件获取
        package_json = lib_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json, 'r', encoding='utf-8') as f:
                    pkg = json.load(f)
                    return pkg.get("version")
            except Exception:
                pass

        return None

    def analyze_structure_compliance(
        self,
        project_path: str = ""
    ) -> Tuple[float, StructureCompliance]:
        """
        分析项目结构合规性

        对照标准模板检查目录结构的完整性：
        - 必需目录：DB1/, OB1/, common/, Test/
        - 可选目录：feeder/, pickplace/, external/

        评分算法（100分制）：
        - 基础分100分
        - 每缺少一个必需目录扣25分
        - 存在可选目录不加分也不扣分

        Args:
            project_path: 项目根目录路径

        Returns:
            Tuple[float, StructureCompliance]: (结构合规得分, 合规详情)
        """
        logger.debug("分析项目结构合规性...")

        required_dirs = self._standard_dirs["required"]
        optional_dirs = self._standard_dirs["optional"]

        if not project_path:
            # 无法检查时返回默认低分
            compliance = StructureCompliance(
                required_dirs=required_dirs,
                optional_dirs=optional_dirs,
                existing_required=[],
                missing_required=required_dirs,
                existing_optional=[],
                score=0.0
            )
            return 0.0, compliance

        project_dir = Path(project_path)

        # 检查必需目录
        existing_required = []
        missing_required = []

        for dir_name in required_dirs:
            dir_path = project_dir / dir_name
            if dir_path.exists() and dir_path.is_dir():
                existing_required.append(dir_name)
            else:
                missing_required.append(dir_name)

        # 检查可选目录
        existing_optional = []

        for dir_name in optional_dirs:
            dir_path = project_dir / dir_name
            if dir_path.exists() and dir_path.is_dir():
                existing_optional.append(dir_name)

        # 计算得分
        penalty_per_missing = 25.0  # 每个必需目录扣25分
        total_penalty = len(missing_required) * penalty_per_missing
        score = max(0.0, 100.0 - total_penalty)

        compliance = StructureCompliance(
            required_dirs=required_dirs,
            optional_dirs=optional_dirs,
            existing_required=existing_required,
            missing_required=missing_required,
            existing_optional=existing_optional,
            score=score
        )

        logger.debug(
            f"结构合规性 - 得分:{score:.1f}, "
            f"已存在:{len(existing_required)}, "
            f"缺失:{len(missing_required)}"
        )
        return score, compliance

    def calculate_overall_score(
        self,
        compliance_score: float,
        issue_score: float,
        library_score: float,
        structure_score: float
    ) -> Tuple[float, List[DimensionScore]]:
        """
        计算综合健康度评分

        使用预定义的权重配置对各维度进行加权平均：
        - 规范符合度：40%
        - 问题严重程度：30%
        - 库引用状态：15%
        - 结构合规性：15%

        同时确定各维度的评级标签。

        Args:
            compliance_score: 规范符合度得分
            issue_score: 问题严重程度得分
            library_score: 库引用状态得分
            structure_score: 结构合规性得分

        Returns:
            Tuple[float, List[DimensionScore]]: (总分, 各维度得分列表)
        """
        logger.debug("计算综合健康度评分...")

        weights = self._weight_config

        # 构建各维度得分对象
        dimensions = [
            DimensionScore(
                name="规范符合度",
                score=compliance_score,
                weight=weights["compliance"],
                grade=ComplianceLevel.from_rate(compliance_score).value,
                details={"description": "基于检查项通过率的评估"}
            ),
            DimensionScore(
                name="问题严重程度",
                score=issue_score,
                weight=weights["issues"],
                grade=self._score_to_grade_label(issue_score),
                details={"description": "基于错误/警告密度的评估"}
            ),
            DimensionScore(
                name="库引用状态",
                score=library_score,
                weight=weights["library"],
                grade=self._score_to_grade_label(library_score),
                details={"description": "共享库配置有效性评估"}
            ),
            DimensionScore(
                name="结构合规性",
                score=structure_score,
                weight=weights["structure"],
                grade=self._score_to_grade_label(structure_score),
                details={"description": "对照标准模板的结构完整性"}
            ),
        ]

        # 加权平均计算总分
        overall = sum(
            d.score * d.weight for d in dimensions
        )

        logger.debug(
            f"综合评分 - 总分:{overall:.1f}, "
            f"维度:[{', '.join(f'{d.name}:{d.score:.1f}' for d in dimensions)}]"
        )
        return round(overall, 2), dimensions

    def _score_to_grade_label(self, score: float) -> str:
        """
        将分数转换为中文评级标签

        Args:
            score: 分数值 (0-100)

        Returns:
            str: 中文评级标签
        """
        if score >= 90:
            return "优秀"
        elif score >= 70:
            return "良好"
        elif score >= 55:
            return "一般"
        else:
            return "较差"

    def generate_suggestions(
        self,
        check_report: CheckReport,
        compliance_details: List[ComplianceDetail],
        issue_distribution: IssueDistribution,
        library_info_list: List[LibraryInfo],
        structure_compliance: StructureCompliance
    ) -> List[ImprovementSuggestion]:
        """
        生成改进建议列表

        根据各维度的分析结果，自动生成优先级排序的改进建议。
        建议内容针对具体问题，提供可操作的指导。

        Args:
            check_report: 检查报告
            compliance_details: 符合度详情
            issue_distribution: 问题分布
            library_info_list: 库信息列表
            structure_compliance: 结构合规性

        Returns:
            List[ImprovementSuggestion]: 改进建议列表（按优先级排序）
        """
        suggestions: List[ImprovementSuggestion] = []

        # 1. 错误级别问题建议（最高优先级）
        errors = issue_distribution.by_severity.get("ERROR", 0)
        if errors > 0:
            sug = ImprovementSuggestion(
                priority="高",
                category="问题严重程度",
                title=f"修复{errors}个错误级别的问题",
                description=(
                    f"项目中存在{errors}个必须立即修复的错误。"
                    f"这些错误可能导致编译失败或运行时异常。"
                    f"请优先处理Error级别的违规项。"
                ),
                affected_items=[
                    f"{cat}({count}个)"
                    for cat, count in issue_distribution.by_category.items()
                    if count > 0
                ][:3]
            )
            suggestions.append(sug)

        # 2. 警告级别问题建议
        warnings = issue_distribution.by_severity.get("WARNING", 0)
        if warnings > 0:
            sug = ImprovementSuggestion(
                priority="中",
                category="问题严重程度",
                title=f"优化{warnings}个警告级别的问题",
                description=(
                    f"项目中有{warnings}个警告项需要关注。"
                    f"虽然不会阻止编译，但可能影响代码质量和可维护性。"
                    f"建议在修复错误后逐步处理这些警告。"
                ),
                affected_items=[]
            )
            suggestions.append(sug)

        # 3. 低符合度类别建议
        low_compliance_cats = [
            cd for cd in compliance_details
            if cd.pass_rate < 70 and cd.category != "总体"
        ]

        for cat_detail in low_compliance_cats[:2]:
            sug = ImprovementSuggestion(
                priority="高" if cat_detail.pass_rate < 50 else "中",
                category="规范符合度",
                title=f"提升{cat_detail.category}类别的规范符合度",
                description=(
                    f"{cat_detail.category}类别的通过率为"
                    f"{cat_detail.pass_rate:.1f}%，低于推荐阈值70%。"
                    f"请重点检查该类别相关的编码规范。"
                ),
                affected_items=[cat_detail.category]
            )
            suggestions.append(sug)

        # 4. 库引用问题建议
        problematic_libs = [
            lib for lib in library_info_list
            if lib.status != LibraryStatus.OK
        ]

        if problematic_libs:
            lib_names = ", ".join([lib.name for lib in problematic_libs])
            sug = ImprovementSuggestion(
                priority="高",
                category="库引用状态",
                title=f"修复共享库引用问题 ({len(problematic_libs)}个)",
                description=(
                    f"以下共享库存在问题: {lib_names}。"
                    f"请检查.plc.json中的libraries配置，"
                    f"确保路径正确且库文件已部署到位。"
                ),
                affected_items=[lib.name for lib in problematic_libs]
            )
            suggestions.append(sug)

        # 5. 目录结构缺失建议
        if structure_compliance.missing_required:
            missing = ", ".join(structure_compliance.missing_required)
            sug = ImprovementSuggestion(
                priority="中",
                category="结构合规性",
                title=f"补充缺失的必需目录 ({len(structure_compliance.missing_required)}个)",
                description=(
                    f"以下标准目录缺失: {missing}。"
                    f"请创建这些目录以符合项目结构规范。"
                    f"这将有助于提升项目的组织性和可维护性。"
                ),
                affected_items=structure_compliance.missing_required
            )
            suggestions.append(sug)

        # 6. 最差文件建议
        if issue_distribution.worst_files:
            worst_file = issue_distribution.worst_files[0]
            if worst_file[1] >= 5:  # 问题数>=5才提示
                sug = ImprovementSuggestion(
                    priority="低",
                    category="问题严重程度",
                    title=f"重点关注文件: {Path(worst_file[0]).name}",
                    description=(
                        f"该文件包含{worst_file[1]}个问题，是项目中问题最多的文件。"
                        f"建议安排专项重构或详细审查。"
                    ),
                    affected_items=[worst_file[0]]
                )
                suggestions.append(sug)

        # 按优先级排序（高>中>低）
        priority_order = {"高": 0, "中": 1, "低": 2}
        suggestions.sort(key=lambda x: priority_order.get(x.priority, 99))

        return suggestions

    def generate_health_card_data(
        self,
        metrics: HealthMetrics
    ) -> Dict[str, Any]:
        """
        生成适合UI展示的健康度卡片数据

        将完整的HealthMetrics转换为UI面板友好的数据结构，
        包含可视化所需的全部信息。

        输出格式特点：
        - 扁平化的字典结构，便于JSON绑定
        - 包含颜色、图标等展示属性
        - 预格式化文本摘要
        - 分组的数据便于渲染不同类型的组件

        Args:
            metrics: 健康度指标对象

        Returns:
            Dict[str, Any]: UI卡片数据字典
        """
        card_data = {
            # === 头部信息 ===
            "header": {
                "title": "项目健康度概览",
                "project_name": metrics.project_name or "未命名项目",
                "analysis_time": metrics.analysis_time.strftime(
                    "%Y-%m-%d %H:%M"
                ),
                "refresh_hint": "点击刷新重新分析"
            },

            # === 核心评分卡片 ===
            "score_card": {
                "overall_score": metrics.overall_score,
                "grade": metrics.health_grade.value,
                "grade_label": metrics.health_grade.label,
                "grade_color": metrics.health_grade.color,
                "score_arc_params": self._calculate_score_arc_params(
                    metrics.overall_score
                ),
                "trend_indicator": self._calculate_trend(metrics),
                "summary_text": self._generate_brief_summary(metrics)
            },

            # === 维度雷达图数据 ===
            "radar_chart": {
                "dimensions": [
                    {
                        "name": dim.name,
                        "value": dim.score,
                        "max_value": 100,
                        "weight_percent": dim.weight * 100,
                        "grade": dim.grade
                    }
                    for dim in metrics.dimensions
                ]
            },

            # === 问题分布面板 ===
            "issue_panel": {
                "total_issues": metrics.issue_distribution.total_issues,
                "severity_breakdown": [
                    {
                        "level": level,
                        "count": count,
                        "color": self._get_severity_color(level),
                        "icon": self._get_severity_icon(level)
                    }
                    for level, count in
                    metrics.issue_distribution.by_severity.items()
                    if count > 0
                ],
                "category_breakdown": [
                    {
                        "category": cat,
                        "count": count
                    }
                    for cat, count in
                    metrics.issue_distribution.by_category.items()
                ],
                "worst_files_table": [
                    {
                        "rank": i + 1,
                        "file_name": Path(file).name,
                        "full_path": file,
                        "violation_count": violations,
                        "status_color": self._get_violation_status_color(
                            violations
                        )
                    }
                    for i, (file, violations) in enumerate(
                        metrics.issue_distribution.worst_files[:10]
                    )
                ]
            },

            # === 库引用状态面板 ===
            "library_panel": {
                "total_libraries": len(metrics.library_info_list),
                "healthy_count": sum(
                    1 for lib in metrics.library_info_list
                    if lib.status == LibraryStatus.OK
                ),
                "problematic_count": sum(
                    1 for lib in metrics.library_info_list
                    if lib.status != LibraryStatus.OK
                ),
                "library_list": [
                    {
                        "name": lib.name,
                        "path": lib.path,
                        "status": lib.status.value,
                        "icon": lib.status.icon,
                        "version": lib.version or "未知",
                        "error": lib.error_message
                    }
                    for lib in metrics.library_info_list
                ]
            },

            # === 结构合规性面板 ===
            "structure_panel": (
                {
                    "score": metrics.structure_compliance.score,
                    "required_dirs": {
                        "total": len(
                            metrics.structure_compliance.required_dirs
                        ),
                        "existing": len(
                            metrics.structure_compliance.existing_required
                        ),
                        "missing": len(
                            metrics.structure_compliance.missing_required
                        ),
                        "list": [
                            {
                                "name": d,
                                "exists": d in
                                metrics.structure_compliance.existing_required
                            }
                            for d in
                            metrics.structure_compliance.required_dirs
                        ]
                    },
                    "optional_dirs": {
                        "existing": list(
                            metrics.structure_compliance.existing_optional
                        )
                    }
                }
                if metrics.structure_compliance else None
            ),

            # === 改进建议面板 ===
            "suggestions_panel": {
                "total_suggestions": len(metrics.suggestions),
                "high_priority_count": sum(
                    1 for s in metrics.suggestions
                    if s.priority == "高"
                ),
                "suggestion_cards": [
                    {
                        "priority": sug.priority,
                        "priority_color": self._get_priority_color(
                            sug.priority
                        ),
                        "category": sug.category,
                        "title": sug.title,
                        "description": sug.description,
                        "affected_items": sug.affected_items
                    }
                    for sug in metrics.suggestions[:8]
                ]
            },

            # === 导出选项 ===
            "export_options": {
                "json_available": True,
                "text_report_available": True,
                "data": metrics.to_dict()
            }
        }

        return card_data

    def _calculate_score_arc_params(
        self,
        score: float
    ) -> Dict[str, Any]:
        """
        计算圆弧进度条的参数

        用于UI中的环形进度图绘制。

        Args:
            score: 分数 (0-100)

        Returns:
            Dict: 包含百分比、角度等参数
        """
        percentage = score / 100.0
        angle = percentage * 360  # 总角度360度

        return {
            "percentage": round(percentage * 100, 1),
            "angle": round(angle, 1),
            "stroke_dashoffset": round((1 - percentage) * 283, 2),  # 圆周长约283
            "color": HealthGrade.from_score(score).color
        }

    def _calculate_trend(
        self,
        metrics: HealthMetrics
    ) -> Dict[str, Any]:
        """
        计算趋势指示器参数

        与上一次分析结果对比，判断健康度变化趋势。

        Args:
            metrics: 当前健康度指标

        Returns:
            Dict: 趋势信息（方向、变化量、描述）
        """
        if not self._previous_metrics:
            return {
                "direction": "none",
                "change": 0,
                "description": "首次分析，无历史数据"
            }

        current = metrics.overall_score
        previous = self._previous_metrics.overall_score
        change = round(current - previous, 2)

        if change > 2:
            direction = "up"
            icon = "\u2191"  # ↑
            desc = f"较上次提升{abs(change):.1f}分"
        elif change < -2:
            direction = "down"
            icon = "\u2193"  # ↓
            desc = f"较上次下降{abs(change):.1f}分"
        else:
            direction = "stable"
            icon = "\u2192"  # →
            desc = "与上次基本持平"

        return {
            "direction": direction,
            "change": change,
            "icon": icon,
            "description": desc
        }

    def _generate_brief_summary(
        self,
        metrics: HealthMetrics
    ) -> str:
        """
        生成简短摘要文本

        一句话概括当前项目健康状态。

        Args:
            metrics: 健康度指标

        Returns:
            str: 摘要文本
        """
        grade = metrics.health_grade.label
        issues = metrics.issue_distribution.total_issues

        if issues == 0:
            return f"项目状态{grade}，未发现问题"
        elif issues <= 10:
            return f"项目状态{grade}，发现{issues}个小问题"
        else:
            return f"项目状态{grade}，需关注{issues}个问题"

    def _get_severity_color(self, severity: str) -> str:
        """获取严重级别对应的颜色"""
        colors = {
            "ERROR": "#ff4d4f",
            "WARNING": "#faad14",
            "INFO": "#1890ff"
        }
        return colors.get(severity, "#999999")

    def _get_severity_icon(self, severity: str) -> str:
        """获取严重级别对应的图标"""
        icons = {
            "ERROR": "\u274c",
            "WARNING": "\u26a0\ufe0f",
            "INFO": "\u2139\ufe0f"
        }
        return icons.get(severity, "\u2022")

    def _get_violation_status_color(
        self,
        violation_count: int
    ) -> str:
        """根据违规数量返回状态颜色"""
        if violation_count >= 10:
            return "#ff4d4f"
        elif violation_count >= 5:
            return "#faad14"
        else:
            return "#52c41a"

    def _get_priority_color(self, priority: str) -> str:
        """获取优先级对应的颜色"""
        colors = {
            "高": "#ff4d4f",
            "中": "#faad14",
            "低": "#1890ff"
        }
        return colors.get(priority, "#999999")

    def update_with_new_results(
        self,
        current_metrics: HealthMetrics,
        new_report: CheckReport,
        project_path: str = ""
    ) -> HealthMetrics:
        """
        增量更新健康度指标

        基于新的检查结果更新现有指标，保留历史对比数据。
        适用于持续集成的场景。

        Args:
            current_metrics: 当前的健康度指标
            new_report: 新的检查报告
            project_path: 项目路径

        Returns:
            HealthMetrics: 更新后的健康度指标
        """
        logger.info("执行增量更新...")

        # 使用当前指标作为历史参考
        updated = self.analyze(
            check_report=new_report,
            project_path=project_path,
            previous_metrics=current_metrics
        )

        logger.info("增量更新完成")
        return updated
