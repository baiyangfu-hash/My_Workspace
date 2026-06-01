# -*- coding: utf-8 -*-
"""
项目健康度分析器单元测试

测试覆盖范围:
1. 完美项目（无问题）的健康度评估
2. 有少量warning的项目的健康度
3. 有error级别的项目的健康度
4. 库引用正常/失败的情况
5. 权重计算准确性验证
6. 增量更新功能测试
7. 边界条件处理（空报告、缺失路径等）
8. 改进建议生成逻辑
9. UI卡片数据生成
10. JSON序列化和文本输出

运行方式:
    python -m pytest tests/test_health_analyzer.py -v
"""
import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

# 导入被测模块
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.checkers.base_checker import Severity
from src.models.check_result import Violation, CheckResult, CheckReport
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
from src.diagnostics.project_health_analyzer import ProjectHealthAnalyzer


# ============================================================================
# 测试辅助函数
# ============================================================================

def create_violation(
    rule_id: str = "TEST_001",
    severity: Severity = Severity.WARNING,
    message: str = "测试违规",
    file_path: str = "test.st"
) -> Violation:
    """创建违规记录的辅助函数"""
    return Violation(
        rule_id=rule_id,
        severity=severity,
        message=message,
        file_path=file_path,
        line_number=1
    )


def create_check_result(
    file_path: str = "test.st",
    violations: list = None
) -> CheckResult:
    """创建检查结果的辅助函数"""
    result = CheckResult(source_file=file_path)
    if violations:
        for v in violations:
            result.add_violation(v)
    return result


def create_check_report(
    project_name: str = "测试项目",
    results: list = None
) -> CheckReport:
    """创建检查报告的辅助函数"""
    report = CheckReport(project_name=project_name)
    if results:
        for r in results:
            report.add_result(r)
    return report


# ============================================================================
# 1. 完美项目测试（应接近100%）
# ============================================================================

class TestPerfectProjectHealth:
    """
    测试完美项目的健康度

    场景：无任何违规、结构完整、库配置正确
    预期：总分接近100分，等级为A（优秀）
    """

    def test_perfect_project_high_score(self):
        """测试完美项目应该获得接近100分的评分"""
        # 创建空报告（无违规）
        report = create_check_report("完美项目")

        analyzer = ProjectHealthAnalyzer()

        # 使用临时目录作为项目路径
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建标准目录结构
            for dir_name in STANDARD_DIRECTORIES["required"]:
                (Path(tmpdir) / dir_name).mkdir()

            # 创建有效的.plc.json
            plc_json = Path(tmpdir) / ".plc.json"
            plc_json.write_text(json.dumps({
                "libraries": [
                    {
                        "name": "StandardLibrary",
                        "path": "./libs/standard"
                    }
                ]
            }, ensure_ascii=False))

            # 创建库目录
            (Path(tmpdir) / "libs" / "standard").mkdir(parents=True)

            metrics = analyzer.analyze(report, tmpdir)

            # 验证高分
            assert metrics.overall_score >= 90.0, \
                f"完美项目得分应为>=90，实际: {metrics.overall_score}"

            # 验证等级
            assert metrics.health_grade == HealthGrade.EXCELLENT, \
                f"等级应为A(优秀)，实际: {metrics.health_grade.value}"

    def test_perfect_project_no_issues(self):
        """测试完美项目不应有问题分布"""
        report = create_check_report()
        analyzer = ProjectHealthAnalyzer()

        with tempfile.TemporaryDirectory() as tmpdir:
            for dir_name in STANDARD_DIRECTORIES["required"]:
                (Path(tmpdir) / dir_name).mkdir()

            plc_json = Path(tmpdir) / ".plc.json"
            plc_json.write_text(json.dumps({
                "libraries": [
                    {"name": "StandardLibrary", "path": "./libs/standard"}
                ]
            }, ensure_ascii=False))
            (Path(tmpdir) / "libs" / "standard").mkdir(parents=True)

            metrics = analyzer.analyze(report, tmpdir)

            # 问题总数应为0
            assert metrics.issue_distribution.total_issues == 0

            # 不应有改进建议（或仅有建议性建议）
            high_priority = [s for s in metrics.suggestions if s.priority == "高"]
            assert len(high_priority) == 0, \
                "完美项目不应有高优先级建议"


# ============================================================================
# 2. 有少量warning的项目测试
# ============================================================================

class TestProjectWithWarnings:
    """
    测试包含少量警告的项目

    场景：有5-10个WARNING级别的问题，无ERROR
    预期：分数在70-90之间，等级B或A
    """

    def test_warnings_reduce_score_moderately(self):
        """测试警告应适度降低分数"""
        violations = [
            create_violation(
                rule_id="NAMING_001",
                severity=Severity.WARNING,
                message="命名不规范"
            )
            for _ in range(8)  # 8个警告
        ]

        results = [create_check_result(f"file_{i}.st", violations[:2])
                   for i in range(4)]  # 分布在4个文件中
        report = create_check_report(results=results)

        analyzer = ProjectHealthAnalyzer()

        with tempfile.TemporaryDirectory() as tmpdir:
            for dir_name in STANDARD_DIRECTORIES["required"]:
                (Path(tmpdir) / dir_name).mkdir()

            plc_json = Path(tmpdir) / ".plc.json"
            plc_json.write_text(json.dumps({
                "libraries": [
                    {"name": "StandardLibrary", "path": "./libs/standard"}
                ]
            }, ensure_ascii=False))
            (Path(tmpdir) / "libs" / "standard").mkdir(parents=True)

            metrics = analyzer.analyze(report, tmpdir)

            # 分数应在合理范围
            assert 60.0 <= metrics.overall_score <= 95.0, \
                f"有警告的项目分数异常: {metrics.overall_score}"

            # 应包含警告统计
            assert metrics.issue_distribution.by_severity.get("WARNING", 0) == 8

    def test_warnings_generate_suggestions(self):
        """测试警告应产生改进建议"""
        violations = [
            create_violation(severity=Severity.WARNING)
            for _ in range(5)
        ]

        report = create_check_report(results=[
            create_check_result(violations=violations)
        ])

        analyzer = ProjectHealthAnalyzer()

        with tempfile.TemporaryDirectory() as tmpdir:
            metrics = analyzer.analyze(report, tmpdir)

            # 应该有关于警告的建议
            warning_sugs = [
                s for s in metrics.suggestions
                if "警告" in s.title or "warning" in s.title.lower()
            ]
            assert len(warning_sugs) > 0, \
                "有警告时应该生成相关建议"


# ============================================================================
# 3. 有ERROR的项目测试
# ============================================================================

class TestProjectWithErrors:
    """
    测试包含错误的项目

    场景：有3-5个ERROR级别的问题
    预期：分数显著降低，可能低于70分
    """

    def test_errors_significantly_reduce_score(self):
        """测试错误应大幅降低分数"""
        error_violations = [
            create_violation(
                rule_id="SYNTAX_001",
                severity=Severity.ERROR,
                message="语法错误"
            )
            for _ in range(5)  # 5个错误
        ]

        warning_violations = [
            create_violation(severity=Severity.WARNING)
            for _ in range(3)  # 3个警告
        ]

        all_violations = error_violations + warning_violations

        report = create_check_report(results=[
            create_check_result(violations=all_violations)
        ])

        analyzer = ProjectHealthAnalyzer()

        with tempfile.TemporaryDirectory() as tmpdir:
            metrics = analyzer.analyze(report, tmpdir)

            # 错误应导致分数显著下降
            # 问题维度: 5错误*10 + 3警告*3 = 59扣分 → 41分
            # 综合考虑四维加权，分数应明显低于60
            assert metrics.overall_score <= 60.0, \
                f"错误扣分不足: {metrics.overall_score}"

    def test_errors_generate_high_priority_suggestions(self):
        """测试错误应生成高优先级建议"""
        errors = [
            create_violation(severity=Severity.ERROR)
            for _ in range(3)
        ]

        report = create_check_report(results=[
            create_check_result(violations=errors)
        ])

        analyzer = ProjectHealthAnalyzer()

        with tempfile.TemporaryDirectory() as tmpdir:
            metrics = analyzer.analyze(report, tmpdir)

            # 应该有高优先级的修复建议
            high_priority = [s for s in metrics.suggestions if s.priority == "高"]
            assert len(high_priority) > 0, \
                "有错误时应生成高优先级建议"

            # 建议内容应提及错误数量
            error_sug = [s for s in high_priority if "错误" in s.title]
            assert len(error_sug) > 0, \
                "高优先级建议应提及错误修复"


# ============================================================================
# 4. 库引用状态测试
# ============================================================================

class TestLibraryStatusAnalysis:
    """
    测试共享库引用状态分析功能

    场景包括：
    - 库引用正常
    - 库路径无效
    - .plc.json缺失
    - libraries字段格式错误
    """

    def test_valid_library_reference(self):
        """测试有效的库引用应得高分"""
        analyzer = ProjectHealthAnalyzer()
        report = create_check_report()

        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建有效的.plc.json和库目录
            plc_json = Path(tmpdir) / ".plc.json"
            plc_json.write_text(json.dumps({
                "libraries": [
                    {"name": "TestLib", "path": "./lib/test"}
                ]
            }, ensure_ascii=False))

            lib_dir = Path(tmpdir) / "lib" / "test"
            lib_dir.mkdir(parents=True)

            score, lib_info = analyzer.analyze_library_status(tmpdir)

            # 应获得接近满分的评分
            assert score >= 90.0, \
                f"有效库引用得分过低: {score}"

            # 状态应为OK
            assert len(lib_info) > 0
            assert lib_info[0].status == LibraryStatus.OK

    def test_invalid_library_path(self):
        """测试无效路径的库引用应降低分数"""
        analyzer = ProjectHealthAnalyzer()
        report = create_check_report()

        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建指向不存在路径的库配置
            plc_json = Path(tmpdir) / ".plc.json"
            plc_json.write_text(json.dumps({
                "libraries": [
                    {"name": "MissingLib", "path": "./nonexistent/lib"}
                ]
            }, ensure_ascii=False))

            score, lib_info = analyzer.analyze_library_status(tmpdir)

            # 分数应显著降低
            assert score < 80.0, \
                f"无效路径库引用得分过高: {score}"

            # 状态应为INVALID_PATH
            assert any(lib.status == LibraryStatus.INVALID_PATH
                       for lib in lib_info)

    def test_missing_plc_json(self):
        """测试缺少.plc.json的情况"""
        analyzer = ProjectHealthAnalyzer()
        report = create_check_report()

        with tempfile.TemporaryDirectory() as tmpdir:
            # 不创建.plc.json
            score, lib_info = analyzer.analyze_library_status(tmpdir)

            # 分数应为0或很低
            assert score < 50.0, \
                f"缺失配置文件得分过高: {score}"

            # 应标记为MISSING
            assert any(lib.status == LibraryStatus.MISSING
                       for lib in lib_info)

    def test_empty_libraries_config(self):
        """测试libraries字段为空的情况"""
        analyzer = ProjectHealthAnalyzer()
        report = create_check_report()

        with tempfile.TemporaryDirectory() as tmpdir:
            plc_json = Path(tmpdir) / ".plc.json"
            plc_json.write_text(json.dumps({
                "libraries": []
            }, ensure_ascii=False))

            score, lib_info = analyzer.analyze_library_status(tmpdir)

            # 空配置应给中等分数（不是0）
            assert 30.0 <= score <= 50.0, \
                f"空配置分数异常: {score}"


# ============================================================================
# 5. 权重计算准确性测试
# ============================================================================

class TestWeightCalculation:
    """
    测试权重计算的准确性

    验证：
    - 默认权重总和为1.0
    - 自定义权重生效
    - 加权平均结果正确
    """

    def test_default_weights_sum_to_one(self):
        """测试默认权重总和应为1.0"""
        weights = WEIGHT_CONFIG
        total = sum(weights.values())

        assert abs(total - 1.0) < 0.001, \
            f"权重总和不为1.0: {total}"

    def test_custom_weights_validation(self):
        """测试自定义权重的有效性验证"""
        analyzer = ProjectHealthAnalyzer()

        # 无效权重（总和不为1）
        with pytest.raises(ValueError, match="权重总和"):
            analyzer.set_weight_config({
                "compliance": 0.5,
                "issues": 0.5,
                "library": 0.1,  # 总和1.1
                "structure": 0.1
            })

        # 未知的维度名
        with pytest.raises(ValueError, match="未知的权重维度"):
            analyzer.set_weight_config({
                "compliance": 0.4,
                "issues": 0.3,
                "library": 0.15,
                "unknown_dim": 0.15  # 无效维度
            })

    def test_custom_weights_affect_score(self):
        """测试自定义权重会影响最终得分"""
        analyzer1 = ProjectHealthAnalyzer()
        analyzer2 = ProjectHealthAnalyzer()

        # analyzer2使用不同权重：提高问题严重程度的权重
        analyzer2.set_weight_config({
            "compliance": 0.20,  # 降低
            "issues": 0.50,      # 提高
            "library": 0.15,
            "structure": 0.15
        })

        # 创建有较多问题的报告
        errors = [create_violation(severity=Severity.ERROR) for _ in range(3)]
        warnings = [create_violation(severity=Severity.WARNING) for _ in range(5)]
        report = create_check_report(results=[
            create_check_result(violations=errors + warnings)
        ])

        with tempfile.TemporaryDirectory() as tmpdir:
            for dir_name in STANDARD_DIRECTORIES["required"]:
                (Path(tmpdir) / dir_name).mkdir()

            plc_json = Path(tmpdir) / ".plc.json"
            plc_json.write_text(json.dumps({
                "libraries": [
                    {"name": "StandardLibrary", "path": "./libs/standard"}
                ]
            }, ensure_ascii=False))
            (Path(tmpdir) / "libs" / "standard").mkdir(parents=True)

            metrics1 = analyzer1.analyze(report, tmpdir)
            metrics2 = analyzer2.analyze(report, tmpdir)

            # 提高问题权重后，有问题的项目得分应该更低
            assert metrics2.overall_score < metrics1.overall_score, \
                "提高问题权重后得分应更低"


# ============================================================================
# 6. 结构合规性测试
# ============================================================================

class TestStructureCompliance:
    """
    测试项目结构合规性分析

    场景：
    - 所有必需目录存在
    - 缺少部分必需目录
    - 可选目录存在与否不影响必需评分
    """

    def test_all_required_dirs_present(self):
        """测试所有必需目录都存在时应满分"""
        analyzer = ProjectHealthAnalyzer()

        with tempfile.TemporaryDirectory() as tmpdir:
            for dir_name in STANDARD_DIRECTORIES["required"]:
                (Path(tmpdir) / dir_name).mkdir()

            score, compliance = analyzer.analyze_structure_compliance(tmpdir)

            assert score == 100.0, \
                f"完整结构应得100分: {score}"
            assert len(compliance.missing_required) == 0

    def test_missing_required_dirs_penalty(self):
        """测试缺少必需目录应扣分"""
        analyzer = ProjectHealthAnalyzer()

        with tempfile.TemporaryDirectory() as tmpdir:
            # 只创建2个必需目录（共4个）
            for dir_name in STANDARD_DIRECTORIES["required"][:2]:
                (Path(tmpdir) / dir_name).mkdir()

            score, compliance = analyzer.analyze_structure_compliance(tmpdir)

            # 缺少2个目录，每个扣25分，应得50分
            assert score == 50.0, \
                f"缺少2个目录应得50分: {score}"
            assert len(compliance.missing_required) == 2

    def test_optional_dirs_no_penalty(self):
        """测试可选目录不影响评分"""
        analyzer = ProjectHealthAnalyzer()

        with tempfile.TemporaryDirectory() as tmpdir:
            # 只创建必需目录
            for dir_name in STANDARD_DIRECTORIES["required"]:
                (Path(tmpdir) / dir_name).mkdir()

            score_without, _ = analyzer.analyze_structure_compliance(tmpdir)

            # 添加可选目录
            for dir_name in STANDARD_DIRECTORIES["optional"]:
                (Path(tmpdir) / dir_name).mkdir()

            score_with, _ = analyzer.analyze_structure_compliance(tmpdir)

            # 分数应相同
            assert score_without == score_with, \
                "可选目录不应影响评分"


# ============================================================================
# 7. 增量更新测试
# ============================================================================

class TestIncrementalUpdate:
    """
    测试增量更新功能

    验证：
    - 能够基于历史数据计算趋势
    - 新结果能正确替换旧指标
    - 趋势方向判断准确
    """

    def test_update_preserves_trend_data(self):
        """测试更新后保留趋势对比数据"""
        analyzer = ProjectHealthAnalyzer()

        # 第一次分析：有一些问题
        warnings1 = [create_violation(severity=Severity.WARNING) for _ in range(5)]
        report1 = create_check_report(results=[
            create_check_result(violations=warnings1)
        ])

        with tempfile.TemporaryDirectory() as tmpdir:
            for dir_name in STANDARD_DIRECTORIES["required"]:
                (Path(tmpdir) / dir_name).mkdir()

            metrics1 = analyzer.analyze(report1, tmpdir)

            # 第二次分析：问题减少（改善）
            warnings2 = [create_violation(severity=Severity.WARNING) for _ in range(2)]
            report2 = create_check_report(results=[
                create_check_result(violations=warnings2)
            ])

            metrics2 = analyzer.update_with_new_results(
                current_metrics=metrics1,
                new_report=report2,
                project_path=tmpdir
            )

            # 生成卡片数据以触发趋势计算
            card = analyzer.generate_health_card_data(metrics2)

            # 趋势应该是上升（改善）
            trend = card["score_card"]["trend_indicator"]
            assert trend["direction"] == "up", \
                f"问题减少后趋势应向上: {trend['description']}"

    def test_update_with_worse_results(self):
        """测试结果变差时的趋势"""
        analyzer = ProjectHealthAnalyzer()

        # 初始状态良好
        report1 = create_check_report()
        with tempfile.TemporaryDirectory() as tmpdir:
            for dir_name in STANDARD_DIRECTORIES["required"]:
                (Path(tmpdir) / dir_name).mkdir()

            metrics1 = analyzer.analyze(report1, tmpdir)

            # 变差：添加错误
            errors = [create_violation(severity=Severity.ERROR) for _ in range(3)]
            report2 = create_check_report(results=[
                create_check_result(violations=errors)
            ])

            metrics2 = analyzer.update_with_new_results(
                current_metrics=metrics1,
                new_report=report2,
                project_path=tmpdir
            )

            card = analyzer.generate_health_card_data(metrics2)
            trend = card["score_card"]["trend_indicator"]

            # 趋势应该向下
            assert trend["direction"] == "down", \
                f"新增错误后趋势应向下: {trend['description']}"


# ============================================================================
# 8. 边界条件和异常处理测试
# ============================================================================

class TestEdgeCases:
    """
    测试边界条件和异常情况

    包括：
    - 空检查报告
    - 缺失项目路径
    - 所有检查项失败
    - 超大规模项目
    """

    def test_empty_report_handling(self):
        """测试空报告的处理"""
        analyzer = ProjectHealthAnalyzer()
        report = CheckReport(project_name="空项目")

        with tempfile.TemporaryDirectory() as tmpdir:
            for dir_name in STANDARD_DIRECTORIES["required"]:
                (Path(tmpdir) / dir_name).mkdir()

            plc_json = Path(tmpdir) / ".plc.json"
            plc_json.write_text(json.dumps({
                "libraries": [
                    {"name": "StandardLibrary", "path": "./libs/standard"}
                ]
            }, ensure_ascii=False))
            (Path(tmpdir) / "libs" / "standard").mkdir(parents=True)

            metrics = analyzer.analyze(report, tmpdir)

            # 空报告应获得合理的高分
            assert metrics.overall_score >= 80.0, \
                f"空报告得分异常: {metrics.overall_score}"

            # 不应抛出异常
            assert isinstance(metrics, HealthMetrics)

    def test_missing_project_path(self):
        """测试缺失项目路径的处理"""
        analyzer = ProjectHealthAnalyzer()
        report = create_check_report()

        # 不提供项目路径
        metrics = analyzer.analyze(report, "")

        # 应正常完成分析（无法检测的维度给默认满分）
        assert isinstance(metrics, HealthMetrics)
        assert metrics.overall_score >= 0

        # 无法检测时不生成库信息条目
        assert isinstance(metrics.library_info_list, list)

    def test_all_checks_failed(self):
        """测试所有检查项都失败的场景"""
        analyzer = ProjectHealthAnalyzer()

        # 大量各种类型的违规
        violations = []
        for i in range(20):
            if i < 10:
                violations.append(create_violation(
                    rule_id=f"TEST_{i:03d}",
                    severity=Severity.ERROR
                ))
            elif i < 17:
                violations.append(create_violation(
                    rule_id=f"TEST_{i:03d}",
                    severity=Severity.WARNING
                ))
            else:
                violations.append(create_violation(
                    rule_id=f"TEST_{i:03d}",
                    severity=Severity.INFO
                ))

        report = create_check_report(results=[
            create_check_result(violations=violations)
        ])

        with tempfile.TemporaryDirectory() as tmpdir:
            metrics = analyzer.analyze(report, tmpdir)

            # 得分应该很低
            assert metrics.overall_score < 50.0, \
                f"大量违规应导致低分: {metrics.overall_score}"

            # 等级应为D
            assert metrics.health_grade == HealthGrade.POOR, \
                f"低分等级应为D: {metrics.health_grade.value}"

    def test_single_file_analysis(self):
        """测试单文件项目的分析"""
        analyzer = ProjectHealthAnalyzer()

        single_violation = create_violation(
            rule_id="NAMING_001",
            severity=Severity.INFO
        )

        report = create_check_report(results=[
            create_check_result(
                file_path="main_program.st",
                violations=[single_violation]
            )
        ])

        with tempfile.TemporaryDirectory() as tmpdir:
            metrics = analyzer.analyze(report, tmpdir)

            # 单文件也应正常分析
            assert isinstance(metrics, HealthMetrics)
            assert metrics.issue_distribution.total_issues == 1


# ============================================================================
# 9. 改进建议生成测试
# ============================================================================

class TestSuggestionGeneration:
    """
    测试改进建议生成逻辑

    验证：
    - 建议按优先级排序
    - 建议内容与实际问题相关
    - 不同场景产生不同的建议组合
    """

    def test_suggestions_sorted_by_priority(self):
        """测试建议按优先级排序"""
        analyzer = ProjectHealthAnalyzer()

        # 创建混合问题场景
        errors = [create_violation(severity=Severity.ERROR) for _ in range(2)]
        warnings = [create_violation(severity=Severity.WARNING) for _ in range(3)]

        report = create_check_report(results=[
            create_check_result(violations=errors + warnings)
        ])

        with tempfile.TemporaryDirectory() as tmpdir:
            metrics = analyzer.analyze(report, tmpdir)

            # 如果有多条建议，高优先级应在前面
            if len(metrics.suggestions) > 1:
                priorities = [s.priority for s in metrics.suggestions]
                priority_order = {"高": 0, "中": 1, "低": 2}

                for i in range(len(priorities) - 1):
                    assert priority_order[priorities[i]] <= \
                           priority_order[priorities[i + 1]], \
                        "建议未按优先级排序"

    def test_suggestions_content_relevance(self):
        """测试建议内容与问题相关"""
        analyzer = ProjectHealthAnalyzer()

        # 只有语法类错误
        syntax_errors = [
            create_violation(
                rule_id="SYNTAX_001",
                severity=Severity.ERROR,
                message="语法错误"
            ) for _ in range(3)
        ]

        report = create_check_report(results=[
            create_check_result(violations=syntax_errors)
        ])

        with tempfile.TemporaryDirectory() as tmpdir:
            metrics = analyzer.analyze(report, tmpdir)

            # 应该有提到错误或修复的建议
            has_error_related = any(
                "错误" in s.title or "修复" in s.description
                for s in metrics.suggestions
            )
            assert has_error_related, \
                "有错误时应生成相关的修复建议"

    def test_no_false_positives_in_suggestions(self):
        """测试不应产生误导性建议"""
        analyzer = ProjectHealthAnalyzer()

        # 完美项目（无问题）
        report = create_check_report()

        with tempfile.TemporaryDirectory() as tmpdir:
            for dir_name in STANDARD_DIRECTORIES["required"]:
                (Path(tmpdir) / dir_name).mkdir()

            plc_json = Path(tmpdir) / ".plc.json"
            plc_json.write_text(json.dumps({
                "libraries": [
                    {"name": "StandardLibrary", "path": "./libs/standard"}
                ]
            }, ensure_ascii=False))
            (Path(tmpdir) / "libs" / "standard").mkdir(parents=True)

            metrics = analyzer.analyze(report, tmpdir)

            # 不应有高优先级建议
            high_priority = [s for s in metrics.suggestions if s.priority == "高"]
            assert len(high_priority) == 0, \
                "完美项目不应有高优先级建议"


# ============================================================================
# 10. 数据输出和序列化测试
# ============================================================================

class TestDataOutputAndSerialization:
    """
    测试数据输出和序列化功能

    验证：
    - to_dict()输出完整
    - to_json_string()格式正确
    - get_summary_text()可读性好
    - generate_health_card_data()UI友好
    """

    def test_to_dict_completeness(self):
        """测试to_dict()输出完整性"""
        analyzer = ProjectHealthAnalyzer()
        report = create_check_report(project_name="序列化测试")

        with tempfile.TemporaryDirectory() as tmpdir:
            metrics = analyzer.analyze(report, tmpdir)
            data = metrics.to_dict()

            # 验证关键字段存在
            required_keys = [
                "overall_score",
                "health_grade",
                "dimensions",
                "issue_distribution",
                "analysis_time"
            ]

            for key in required_keys:
                assert key in data, f"to_dict()缺少字段: {key}"

            # 验证health_grade子结构
            grade_data = data["health_grade"]
            assert "grade" in grade_data
            assert "label" in grade_data
            assert "color" in grade_data

    def test_json_serialization_valid(self):
        """测试JSON序列化的有效性"""
        analyzer = ProjectHealthAnalyzer()
        report = create_check_report()

        with tempfile.TemporaryDirectory() as tmpdir:
            metrics = analyzer.analyze(report, tmpdir)
            json_str = metrics.to_json_string()

            # 应能够反序列化
            parsed = json.loads(json_str)
            assert isinstance(parsed, dict)
            assert "overall_score" in parsed

            # 应包含中文（不转义）
            assert "\u4e2d\u6587" not in json_str or "项目" in json_str

    def test_summary_text_format(self):
        """测试摘要文本格式"""
        analyzer = ProjectHealthAnalyzer()
        report = create_check_report(project_name="摘要测试")

        with tempfile.TemporaryDirectory() as tmpdir:
            metrics = analyzer.analyze(report, tmpdir)
            summary = metrics.get_summary_text()

            # 应包含关键信息
            assert "项目名称" in summary or "摘要测试" in summary
            assert "综合评分" in summary or "评分" in summary
            assert "=" in summary  # 有分隔线

            # 应为多行文本
            lines = summary.strip().split("\n")
            assert len(lines) >= 5, "摘要文本过短"

    def test_health_card_data_ui_friendly(self):
        """测试健康度卡片数据的UI友好性"""
        analyzer = ProjectHealthAnalyzer()
        report = create_check_report(project_name="卡片测试")

        with tempfile.TemporaryDirectory() as tmpdir:
            for dir_name in STANDARD_DIRECTORIES["required"]:
                (Path(tmpdir) / dir_name).mkdir()

            metrics = analyzer.analyze(report, tmpdir)
            card_data = analyzer.generate_health_card_data(metrics)

            # 验证主要面板存在
            required_panels = [
                "header",
                "score_card",
                "radar_chart",
                "issue_panel",
                "library_panel",
                "structure_panel",
                "suggestions_panel",
                "export_options"
            ]

            for panel in required_panels:
                assert panel in card_data, f"卡片数据缺少面板: {panel}"

            # 验证评分卡片的关键属性
            score_card = card_data["score_card"]
            assert "overall_score" in score_card
            assert "grade" in score_card
            assert "grade_color" in score_card
            assert "summary_text" in score_card

            # 验证颜色格式（十六进制）
            color = score_card["grade_color"]
            assert color.startswith("#"), \
                f"颜色格式错误: {color}"
            assert len(color) == 7, \
                f"颜色长度错误: {color}"

    def test_health_card_contains_visualization_params(self):
        """测试卡片数据包含可视化参数"""
        analyzer = ProjectHealthAnalyzer()
        report = create_check_report()

        with tempfile.TemporaryDirectory() as tmpdir:
            metrics = analyzer.analyze(report, tmpdir)
            card = analyzer.generate_health_card_data(metrics)

            # 圆弧进度条参数
            arc = card["score_card"]["score_arc_params"]
            assert "percentage" in arc
            assert "angle" in arc
            assert "stroke_dashoffset" in arc
            assert "color" in arc

            # 参数值合理
            assert 0 <= arc["percentage"] <= 100
            assert 0 <= arc["angle"] <= 360


# ============================================================================
# 11. 规范符合度详细测试
# ============================================================================

class TestComplianceDetails:
    """
    测试规范符合度的详细计算

    验证：
    - 按类别分组统计
    - 通过率计算准确性
    - 等级划分正确性
    """

    def test_category_grouping(self):
        """测试按类别分组统计"""
        analyzer = ProjectHealthAnalyzer()

        # 创建多个类别的违规
        violations = [
            create_violation(rule_id="TIMER_001"),
            create_violation(rule_id="TIMER_002"),
            create_violation(rule_id="NAMING_001"),
            create_violation(rule_id="SYNTAX_001"),
        ]

        report = create_check_report(results=[
            create_check_result(violations=violations)
        ])

        score, details = analyzer.calculate_compliance_score(report)

        # 应有多个类别的详情
        assert len(details) >= 2, \
            f"应有至少2个类别详情，实际: {len(details)}"

        # 类别名称应已翻译
        category_names = [d.category for d in details]
        assert any("定时器" in c or "timer" in c.lower()
                   for c in category_names), \
            "应包含定时器类别"

    def test_compliance_level_classification(self):
        """测试符合度等级分类"""
        # 测试各阈值点
        test_cases = [
            (95, ComplianceLevel.EXCELLENT),
            (85, ComplianceLevel.GOOD),
            (60, ComplianceLevel.PASS),
            (40, ComplianceLevel.FAIL),
        ]

        for rate, expected_level in test_cases:
            level = ComplianceLevel.from_rate(rate)
            assert level == expected_level, \
                f"通过率{rate}%应为{expected_level.value}，实际:{level.value}"


# ============================================================================
# 12. 综合集成测试
# ============================================================================

class TestIntegrationScenarios:
    """
    综合集成测试场景

    模拟真实使用场景，验证端到端流程
    """

    def test_realistic_project_scenario(self):
        """测试真实项目场景的综合分析"""
        analyzer = ProjectHealthAnalyzer()

        # 模拟一个中等规模的项目
        files_and_issues = [
            ("main.ob", [
                create_violation(rule_id="SYNTAX_001", severity=Severity.ERROR),
                create_violation(rule_id="NAMING_001", severity=Severity.WARNING),
            ]),
            ("motor_control.fb", [
                create_violation(rule_id="TIMER_001", severity=Severity.WARNING),
                create_violation(rule_id="COMMENT_001", severity=Severity.INFO),
            ]),
            ("io_handler.fb", []),
            ("safety_monitor.fb", [
                create_violation(rule_id="CONFIG_001", severity=Severity.ERROR),
            ]),
            ("hmi_interface.fb", [
                create_violation(rule_id="NAMING_002", severity=Severity.WARNING),
                create_violation(rule_id="NAMING_003", severity=Severity.WARNING),
            ]),
        ]

        results = [
            create_check_result(file_path=f, violations=v)
            for f, v in files_and_issues
        ]

        report = create_check_report(
            project_name="生产线控制系统",
            results=results
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建部分标准目录
            for dir_name in ["DB1", "OB1", "common"]:  # 缺少Test
                (Path(tmpdir) / dir_name).mkdir()

            # 创建有效的库配置
            plc_json = Path(tmpdir) / ".plc.json"
            plc_json.write_text(json.dumps({
                "libraries": [
                    {"name": "MotionLib", "path": "./libs/motion"}
                ]
            }, ensure_ascii=False))
            (Path(tmpdir) / "libs" / "motion").mkdir(parents=True)

            # 执行分析
            metrics = analyzer.analyze(report, tmpdir)

            # 验证基本输出
            assert 0 <= metrics.overall_score <= 100
            assert isinstance(metrics.health_grade, HealthGrade)
            assert len(metrics.dimensions) == 4  # 4个维度

            # 验证问题统计
            assert metrics.issue_distribution.total_issues == 7

            # 验证结构合规性（缺少Test目录）
            assert metrics.structure_compliance is not None
            assert "Test" in metrics.structure_compliance.missing_required

            # 验证可以生成完整输出
            json_output = metrics.to_json_string()
            assert len(json_output) > 0

            summary = metrics.get_summary_text()
            assert len(summary) > 0

            card_data = analyzer.generate_health_card_data(metrics)
            assert len(card_data) > 0

            print(f"\n=== 项目健康度分析结果 ===")
            print(summary)
            print(f"\n总分: {metrics.overall_score:.1f}/100 "
                  f"[{metrics.health_grade.value}级]")


# ============================================================================
# 运行入口
# ============================================================================

if __name__ == "__main__":
    # 运行所有测试
    pytest.main([__file__, "-v", "--tb=short"])
