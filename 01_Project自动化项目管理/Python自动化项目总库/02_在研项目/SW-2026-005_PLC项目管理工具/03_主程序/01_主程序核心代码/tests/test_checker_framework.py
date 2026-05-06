# -*- coding: utf-8 -*-
"""
检查器框架单元测试

测试覆盖范围:
1. BaseChecker抽象基类的接口和行为
2. RuleRegistry单例模式的注册和查询功能
3. 数据模型（Violation, CheckResult, CheckReport）的完整性
4. SpecDocParser的Markdown解析功能

运行方式:
    python -m pytest tests/test_checker_framework.py -v
"""
import pytest
import tempfile
import os
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

# 导入被测模块
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.checkers.base_checker import BaseChecker, Severity, RuleInfo
from src.checkers.rule_registry import RuleRegistry
from src.models.check_result import Violation, CheckResult, CheckReport
from src.parsers.spec_doc_parser import SpecDocParser, SpecRule


# ============================================================================
# 测试辅助类
# ============================================================================

class MockChecker(BaseChecker):
    """用于测试的模拟检查器"""

    def __init__(
        self,
        rule_id: str = "TEST_001",
        name: str = "测试规则",
        severity: Severity = Severity.WARNING,
        category: str = "test",
    ):
        rule_info = RuleInfo(
            rule_id=rule_id,
            name=name,
            description=f"这是一个测试规则: {name}",
            category=category,
            severity=severity,
        )
        super().__init__(rule_info=rule_info)
        self._mock_violations = []

    def set_mock_violations(self, violations: list):
        """设置模拟返回的违规列表"""
        self._mock_violations = violations

    def check(
        self,
        source_code: str,
        file_path: str = "",
        context: dict = None,
    ) -> list:
        """返回预设的模拟违规"""
        return self._mock_violations


# ============================================================================
# 1. BaseChecker 测试
# ============================================================================

class TestBaseChecker:
    """BaseChecker抽象基类测试套件"""

    def test_cannot_instantiate_abstract_class(self):
        """测试不能直接实例化抽象基类"""
        with pytest.raises(TypeError):
            BaseChecker(rule_info=RuleInfo(
                rule_id="ABS_001",
                name="抽象类",
                description="测试",
                category="test",
            ))

    def test_subclass_can_be_instantiated(self):
        """测试子类可以正常实例化"""
        checker = MockChecker()
        assert checker is not None
        assert isinstance(checker, BaseChecker)

    def test_rule_info_property(self):
        """测试规则信息属性"""
        checker = MockChecker(
            rule_id="NAMING_001",
            name="变量命名",
            category="naming",
        )
        info = checker.get_rule_info()
        assert info.rule_id == "NAMING_001"
        assert info.name == "变量命名"
        assert info.category == "naming"

    def test_severity_property(self):
        """测试严重级别属性"""
        checker_error = MockChecker(severity=Severity.ERROR)
        checker_warning = MockChecker(severity=Severity.WARNING)
        checker_info = MockChecker(severity=Severity.INFO)

        assert checker_error.get_severity() == Severity.ERROR
        assert checker_warning.get_severity() == Severity.WARNING
        assert checker_info.get_severity() == Severity.INFO

    def test_enable_disable_toggle(self):
        """测试启用/禁用切换功能"""
        checker = MockChecker()

        # 初始状态应该是启用
        assert checker.is_enabled() is True

        # 禁用
        checker.disable()
        assert checker.is_enabled() is False

        # 重新启用
        checker.enable()
        assert checker.is_enabled() is True

    def test_repr_output(self):
        """测试字符串表示"""
        checker = MockChecker(rule_id="SAFETY_001", name="安全检查")
        repr_str = repr(checker)

        assert "MockChecker" in repr_str
        assert "SAFETY_001" in repr_str
        assert "安全检查" in repr_str
        assert "启用" in repr_str  # 默认启用状态

    def test_disabled_repr(self):
        """测试禁用状态的字符串表示"""
        checker = MockChecker()
        checker.disable()
        repr_str = repr(checker)
        assert "禁用" in repr_str

    def test_check_method_returns_list(self):
        """测试check方法返回列表"""
        checker = MockChecker()
        result = checker.check("test code")
        assert isinstance(result, list)


# ============================================================================
# 2. RuleRegistry 测试
# ============================================================================

class TestRuleRegistry:
    """RuleRegistry单例注册表测试套件"""

    def setup_method(self):
        """每个测试方法前的初始化"""
        # 重置单例以确保测试隔离
        RuleRegistry.reset_instance()
        self.registry = RuleRegistry.get_instance()

    def teardown_method(self):
        """每个测试方法后的清理"""
        RuleRegistry.reset_instance()

    def test_singleton_pattern(self):
        """测试单例模式"""
        registry1 = RuleRegistry.get_instance()
        registry2 = RuleRegistry.get_instance()
        assert registry1 is registry2

    def test_register_checker(self):
        """测试注册检查器"""
        checker = MockChecker(rule_id="REG_001", name="注册测试")
        success = self.registry.register(checker)

        assert success is True
        assert "REG_001" in self.registry
        assert len(self.registry) == 1

    def test_register_duplicate_overwrites(self):
        """测试重复注册会覆盖"""
        checker1 = MockChecker(rule_id="DUP_001", name="第一个")
        checker2 = MockChecker(rule_id="DUP_001", name="第二个")

        self.registry.register(checker1)
        self.registry.register(checker2)  # 应该覆盖

        retrieved = self.registry.get_checker_by_id("DUP_001")
        assert retrieved is checker2  # 应该是第二个

    def test_get_checker_by_id_exists(self):
        """测试按ID查询存在的检查器"""
        checker = MockChecker(rule_id="GET_001", name="查询测试")
        self.registry.register(checker)

        result = self.registry.get_checker_by_id("GET_001")
        assert result is checker

    def test_get_checker_by_id_not_exists(self):
        """测试查询不存在的检查器返回None"""
        result = self.registry.get_checker_by_id("NONEXISTENT")
        assert result is None

    def test_register_invalid_type_raises_error(self):
        """测试注册非检查器类型抛出异常"""
        with pytest.raises(TypeError):
            self.registry.register("not a checker")

    def test_unregister_checker(self):
        """测试注销检查器"""
        checker = MockChecker(rule_id="UNREG_001")
        self.registry.register(checker)

        success = self.registry.unregister("UNREG_001")
        assert success is True
        assert "UNREG_001" not in self.registry
        assert len(self.registry) == 0

    def test_unregister_nonexistent_returns_false(self):
        """测试注销不存在的规则返回False"""
        success = self.registry.unregister("GHOST_001")
        assert success is False

    def test_get_checkers_by_category(self):
        """测试按类别查询检查器"""
        checker1 = MockChecker(rule_id="CAT_A_001", category="naming")
        checker2 = MockChecker(rule_id="CAT_A_002", category="naming")
        checker3 = MockChecker(rule_id="CAT_B_001", category="structure")

        self.registry.register(checker1)
        self.registry.register(checker2)
        self.registry.register(checker3)

        naming_checkers = self.registry.get_checkers_by_category("naming")
        assert len(naming_checkers) == 2
        assert checker1 in naming_checkers
        assert checker2 in naming_checkers

        structure_checkers = self.registry.get_checkers_by_category("structure")
        assert len(structure_checkers) == 1
        assert checker3 in structure_checkers

    def test_get_all_checkers(self):
        """测试获取所有检查器"""
        for i in range(5):
            checker = MockChecker(rule_id=f"ALL_{i:03d}")
            self.registry.register(checker)

        all_checkers = self.registry.get_all_checkers()
        assert len(all_checkers) == 5

    def test_get_all_checkers_enabled_only(self):
        """测试只获取启用的检查器"""
        checker1 = MockChecker(rule_id="EN_001")
        checker2 = MockChecker(rule_id="EN_002")
        checker2.disable()

        self.registry.register(checker1)
        self.registry.register(checker2)

        enabled = self.registry.get_all_checkers(enabled_only=True)
        assert len(enabled) == 1
        assert checker1 in enabled

    def test_enable_rule(self):
        """测试启用规则"""
        checker = MockChecker(rule_id="ENABLE_001")
        checker.disable()
        self.registry.register(checker)

        success = self.registry.enable_rule("ENABLE_001")
        assert success is True
        assert checker.is_enabled() is True

    def test_enable_nonexistent_rule(self):
        """测试启用不存在的规则"""
        success = self.registry.enable_rule("PHANTOM_001")
        assert success is False

    def test_disable_rule(self):
        """测试禁用规则"""
        checker = MockChecker(rule_id="DISABLE_001")
        self.registry.register(checker)

        success = self.registry.disable_rule("DISABLE_001")
        assert success is True
        assert checker.is_enabled() is False

    def test_enable_disable_category(self):
        """测试批量启用/禁用类别"""
        for i in range(3):
            checker = MockChecker(
                rule_id=f"BATCH_{i:03d}",
                category="batch_test",
            )
            checker.disable()
            self.registry.register(checker)

        # 批量启用
        enabled_count = self.registry.enable_category("batch_test")
        assert enabled_count == 3

        # 批量禁用
        disabled_count = self.registry.disable_category("batch_test")
        assert disabled_count == 3

    def test_get_statistics(self):
        """测试获取统计信息"""
        checker1 = MockChecker(rule_id="STAT_001")  # 启用
        checker2 = MockChecker(rule_id="STAT_002")
        checker2.disable()  # 禁用
        checker3 = MockChecker(rule_id="STAT_003", category="cat_a")
        checker4 = MockChecker(rule_id="STAT_004", category="cat_a")

        self.registry.register(checker1)
        self.registry.register(checker2)
        self.registry.register(checker3)
        self.registry.register(checker4)

        stats = self.registry.get_statistics()
        assert stats["total_rules"] == 4
        assert stats["enabled_rules"] == 3
        assert stats["disabled_rules"] == 1
        assert "cat_a" in stats["categories"]
        assert stats["categories"]["cat_a"] == 2

    def test_clear_registry(self):
        """测试清空注册表"""
        for i in range(3):
            self.registry.register(MockChecker(rule_id=f"CLEAR_{i:03d}"))

        assert len(self.registry) == 3
        self.registry.clear()
        assert len(self.registry) == 0

    def test_iteration(self):
        """测试迭代协议"""
        checkers = [
            MockChecker(rule_id=f"ITER_{i:03d}")
            for i in range(3)
        ]
        for c in checkers:
            self.registry.register(c)

        iterated = list(self.registry)
        assert len(iterated) == 3

    def test_get_all_categories(self):
        """测试获取所有类别"""
        self.registry.register(MockChecker(category="cat1"))
        self.registry.register(MockChecker(category="cat2"))
        self.registry.register(MockChecker(category="cat1"))

        categories = self.registry.get_all_categories()
        assert "cat1" in categories
        assert "cat2" in categories
        assert len(categories) == 2


# ============================================================================
# 3. 数据模型测试
# ============================================================================

class TestViolation:
    """Violation数据类测试"""

    def test_creation_with_required_fields(self):
        """测试使用必填字段创建"""
        violation = Violation(
            rule_id="VIO_001",
            severity=Severity.ERROR,
            message="测试违规",
        )
        assert violation.rule_id == "VIO_001"
        assert violation.severity == Severity.ERROR
        assert violation.message == "测试违规"

    def test_creation_with_all_fields(self):
        """测试使用所有字段创建"""
        violation = Violation(
            rule_id="VIO_002",
            severity=Severity.WARNING,
            message="变量名不规范",
            file_path="/path/to/file.st",
            line_number=42,
            column=15,
            suggestion="建议使用匈牙利命名法",
            code_snippet="VAR x : INT; END_VAR",
        )
        assert violation.file_path == "/path/to/file.st"
        assert violation.line_number == 42
        assert violation.column == 15
        assert "匈牙利" in violation.suggestion

    def test_to_dict_serialization(self):
        """测试字典序列化"""
        violation = Violation(
            rule_id="SER_001",
            severity=Severity.INFO,
            message="序列化测试",
        )
        d = violation.to_dict()

        assert isinstance(d, dict)
        assert d["rule_id"] == "SER_001"
        assert d["severity"] == "INFO"
        assert d["severity_value"] == 1
        assert "message" in d

    def test_location_str_formatting(self):
        """测试位置字符串格式化"""
        # 有完整位置信息
        v1 = Violation(
            rule_id="LOC_001",
            severity=Severity.ERROR,
            message="测试",
            file_path="/project/main.st",
            line_number=100,
            column=20,
        )
        assert "main.st:100:20" in v1.location_str

        # 只有文件和行号
        v2 = Violation(
            rule_id="LOC_002",
            severity=Severity.ERROR,
            message="测试",
            file_path="/project/main.st",
            line_number=50,
        )
        assert "main.st:50" in v2.location_str

        # 无位置信息
        v3 = Violation(
            rule_id="LOC_003",
            severity=Severity.ERROR,
            message="测试",
        )
        assert v3.location_str == "未知位置"

    def test_str_representation(self):
        """测试字符串表示"""
        violation = Violation(
            rule_id="STR_001",
            severity=Severity.ERROR,
            message="重要错误",
            file_path="test.st",
            line_number=10,
        )
        str_repr = str(violation)
        assert "[ERROR]" in str_repr
        assert "STR_001" in str_repr
        assert "重要错误" in str_repr


class TestCheckResult:
    """CheckResult数据类测试"""

    def test_empty_result(self):
        """测试空结果"""
        result = CheckResult(source_file="empty.st")
        assert result.total_violations == 0
        assert result.is_passed is True
        assert result.has_violations is False

    def test_add_single_violation(self):
        """测试添加单个违规"""
        result = CheckResult()
        violation = Violation(
            rule_id="ADD_001",
            severity=Severity.ERROR,
            message="添加测试",
        )
        result.add_violation(violation)

        assert result.total_violations == 1
        assert result.error_count == 1
        assert result.has_errors is True
        assert result.is_passed is False

    def test_add_multiple_violations(self):
        """测试批量添加违规"""
        result = CheckResult()
        violations = [
            Violation(rule_id="MUL_001", severity=Severity.ERROR, message="E1"),
            Violation(rule_id="MUL_002", severity=Severity.WARNING, message="W1"),
            Violation(rule_id="MUL_003", severity=Severity.INFO, message="I1"),
            Violation(rule_id="MUL_004", severity=Severity.ERROR, message="E2"),
        ]
        result.add_violations(violations)

        assert result.total_violations == 4
        assert result.error_count == 2
        assert result.warning_count == 1
        assert result.info_count == 1

    def test_filter_by_severity(self):
        """测试按严重级别筛选"""
        result = CheckResult()
        result.add_violations([
            Violation(rule_id="FIL_001", severity=Severity.ERROR, message="E"),
            Violation(rule_id="FIL_002", severity=Severity.WARNING, message="W"),
            Violation(rule_id="FIL_003", severity=Severity.ERROR, message="E2"),
        ])

        errors = result.get_violations_by_severity(Severity.ERROR)
        warnings = result.get_violations_by_severity(Severity.WARNING)

        assert len(errors) == 2
        assert len(warnings) == 1

    def test_filter_by_rule_id(self):
        """测试按规则ID筛选"""
        result = CheckResult()
        result.add_violations([
            Violation(rule_id="RUL_A", severity=Severity.ERROR, message="M1"),
            Violation(rule_id="RUL_B", severity=Severity.WARNING, message="M2"),
            Violation(rule_id="RUL_A", severity=Severity.ERROR, message="M3"),
        ])

        rule_a_violations = result.get_violations_by_rule("RUL_A")
        assert len(rule_a_violations) == 2

    def test_to_dict_serialization(self):
        """测试字典序列化"""
        result = CheckResult(source_file="test.st")
        result.add_violation(Violation(
            rule_id="DICT_001",
            severity=Severity.ERROR,
            message="序列化",
        ))

        d = result.to_dict()
        assert d["source_file"] == "test.st"
        assert d["total_violations"] == 1
        assert d["is_passed"] is False
        assert len(d["violations"]) == 1


class TestCheckReport:
    """CheckReport项目报告测试"""

    def test_empty_report(self):
        """测试空报告"""
        report = CheckReport(project_name="空项目")
        assert report.total_files_checked == 0
        assert report.quality_score == 100.0
        assert report.pass_rate == 0.0

    def test_add_results_and_aggregate(self):
        """测试添加结果和聚合统计"""
        report = CheckReport(project_name="测试项目")

        # 结果1: 通过（无错误）
        result1 = CheckResult(source_file="good.st")
        result1.add_violation(Violation(
            rule_id="REP_001",
            severity=Severity.WARNING,
            message="仅警告",
        ))
        report.add_result(result1)

        # 结果2: 未通过（有错误）
        result2 = CheckResult(source_file="bad.st")
        result2.add_violation(Violation(
            rule_id="REP_002",
            severity=Severity.ERROR,
            message="有错误",
        ))
        report.add_result(result2)

        assert report.total_files_checked == 2
        assert report.passed_files == 1
        assert report.failed_files == 1
        assert report.pass_rate == 50.0
        assert report.total_errors == 1
        assert report.total_warnings == 1

    def test_quality_score_calculation(self):
        """测试质量评分计算"""
        report = CheckReport()

        # 添加一些违规
        result = CheckResult()
        result.add_violations([
            Violation(rule_id="Q_001", severity=Severity.ERROR, message="E"),
            Violation(rule_id="Q_002", severity=Severity.ERROR, message="E"),
            Violation(rule_id="Q_003", severity=Severity.WARNING, message="W"),
        ])
        report.add_result(result)

        # 2个错误(-20) + 1个警告(-3) = 77分
        assert report.quality_score < 100
        assert report.quality_score >= 70

    def test_worst_files_ranking(self):
        """测试最差文件排名"""
        report = CheckReport()

        # 创建不同违规数量的结果
        for i, count in enumerate([5, 2, 8, 1, 3]):
            result = CheckResult(source_file=f"file{i}.st")
            for j in range(count):
                result.add_violation(Violation(
                    rule_id=f"WORST_{j}",
                    severity=Severity.INFO,
                    message=f"违规{j}",
                ))
            report.add_result(result)

        worst = report.get_worst_files(top_n=3)
        assert worst[0].total_violations == 8  # file2.st
        assert worst[1].total_violations == 5  # file0.st
        assert worst[2].total_violations == 3  # file4.st

    def test_to_dict_complete_structure(self):
        """测试完整的字典序列化结构"""
        report = CheckReport(
            project_name="序列化测试",
            project_path="/test/project",
        )
        result = CheckResult(source_file="test.st")
        report.add_result(result)

        d = report.to_dict()

        assert "project_name" in d
        assert "report_time" in d
        assert "summary" in d
        assert "file_results" in d

        summary = d["summary"]
        assert "total_files_checked" in summary
        assert "quality_score" in summary
        assert "pass_rate" in summary

    def test_generate_summary_text(self):
        """测试生成摘要文本"""
        report = CheckReport(project_name="摘要测试")
        result = CheckResult(source_file="demo.st")
        result.add_violation(Violation(
            rule_id="SUM_001",
            severity=Severity.ERROR,
            message="演示错误",
        ))
        report.add_result(result)

        text = report.generate_summary_text()
        assert "摘要测试" in text
        assert "1" in text  # 文件数
        assert "ERROR" in text or "错误" in text


# ============================================================================
# 4. SpecDocParser 测试
# ============================================================================

class TestSpecDocParser:
    """SpecDocParser解析器测试套件"""

    def setup_method(self):
        """每个测试方法前的初始化"""
        self.parser = SpecDocParser()

    def create_temp_spec_file(self, content: str) -> str:
        """创建临时规范文件"""
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".md",
            encoding="utf-8",
            delete=False,
        ) as f:
            f.write(content)
            return f.name

    def test_parse_standard_rule_format(self):
        """测试解析标准规则格式"""
        spec_content = """# PLC编程规范

## 命名规范

### [REQ-NAMING-001] 变量命名规则
**优先级**: high
**严重级别**: error
**标签**: naming, convention

变量名必须采用匈牙利命名法，包含类型前缀。

### [REQ-NAMING-002] POU命名规则
**优先级**: medium
**严重级别**: warning

POU名称应使用PascalCase格式。
"""
        temp_file = self.create_temp_spec_file(spec_content)

        try:
            rules = self.parser.parse_file(temp_file)

            assert len(rules) == 2
            assert rules[0].rule_id == "REQ-NAMING-001"
            assert rules[0].title == "变量命名规则"
            assert rules[0].priority == "high"
            assert rules[0].severity == "error"
            assert "naming" in rules[0].tags
            assert "匈牙利" in rules[0].content

            assert rules[1].rule_id == "REQ-NAMING-002"
            assert rules[1].title == "POU命名规则"
            assert rules[1].priority == "medium"
        finally:
            os.unlink(temp_file)

    def test_parse_colon_format(self):
        """测试解析冒号分隔格式"""
        spec_content = """# 规范文档

## 结构要求

#### RULE-STRUCT-001: 函数长度限制
- 优先级: high
- 严重级别: error

单个函数体不应超过200行代码。

#### RULE-STRUCT-002: 嵌套深度限制
- 优先级: medium
- 严重级别: warning

IF嵌套深度不应超过4层。
"""
        temp_file = self.create_temp_spec_file(spec_content)

        try:
            rules = self.parser.parse_file(temp_file)

            assert len(rules) == 2
            assert rules[0].rule_id == "RULE-STRUCT-001"
            assert rules[0].title == "函数长度限制"
            assert "200" in rules[0].content

            assert rules[1].rule_id == "RULE-STRUCT-002"
            assert "4层" in rules[1].content
        finally:
            os.unlink(temp_file)

    def test_parse_directory(self):
        """测试批量解析目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建多个规范文件
            for i, content in enumerate([
                "### [DIR-001] 规则一\n\n内容一",
                "### [DIR-002] 规则二\n\n内容二",
                "### [DIR-003] 规则三\n\n内容三",
            ]):
                filepath = Path(tmpdir) / f"spec_{i}.md"
                filepath.write_text(content, encoding="utf-8")

            rules = self.parser.parse_directory(tmpdir)
            assert len(rules) == 3
            assert self.parser.parsed_files_count == 3

    def test_get_spec_summary(self):
        """测试获取规范概要"""
        spec_content = """# 规范

### [SUM-001] 高优先级规则
**优先级**: high
**严重级别**: error
**类别**: safety

安全相关内容。

### [SUM-002] 中优先级规则
**优先级**: medium
**严重级别**: warning
**类别**: naming

命名相关内容。

### [SUM-003] 低优先级规则
**优先级**: low
**严重级别**: info
**类别**: safety

提示性内容。
"""
        temp_file = self.create_temp_spec_file(spec_content)

        try:
            self.parser.parse_file(temp_file)
            summary = self.parser.get_spec_summary()

            assert summary["total_rules"] == 3
            assert summary["categories"]["safety"] == 2
            assert summary["categories"]["naming"] == 1
            assert summary["priorities"]["high"] == 1
            assert summary["severities"]["error"] == 1
        finally:
            os.unlink(temp_file)

    def test_search_rules_by_keyword(self):
        """测试关键词搜索"""
        spec_content = """# 搜索测试

### [SRCH-001] 变量命名规范
**类别**: naming

变量应该使用有意义的名称。

### [SRCH-002] 函数注释要求
**类别**: documentation

每个函数必须有详细的注释说明。
"""
        temp_file = self.create_temp_spec_file(spec_content)

        try:
            self.parser.parse_file(temp_file)

            # 搜索"变量"
            results = self.parser.search_rules("变量")
            assert len(results) == 1
            assert results[0].rule_id == "SRCH-001"

            # 搜索"注释"
            results = self.parser.search_rules("注释")
            assert len(results) == 1
            assert results[0].rule_id == "SRCH-002"
        finally:
            os.unlink(temp_file)

    def test_get_rules_by_category(self):
        """测试按类别获取规则"""
        spec_content = """# 分类测试

### [CAT-A-001] A类规则1
**类别**: category_a

内容1。

### [CAT-B-001] B类规则1
**类别**: category_b

内容2。

### [CAT-A-002] A类规则2
**类别**: category_a

内容3。
"""
        temp_file = self.create_temp_spec_file(spec_content)

        try:
            self.parser.parse_file(temp_file)

            cat_a_rules = self.parser.get_rules_by_category("category_a")
            assert len(cat_a_rules) == 2

            cat_b_rules = self.parser.get_rules_by_category("category_b")
            assert len(cat_b_rules) == 1
        finally:
            os.unlink(temp_file)

    def test_handle_nonexistent_file(self):
        """测试处理不存在的文件"""
        with pytest.raises(FileNotFoundError):
            self.parser.parse_file("/nonexistent/path/spec.md")

    def test_handle_unsupported_format(self):
        """测试处理不支持的文件格式"""
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".pdf",
            delete=False,
        ) as f:
            f.write("not markdown")
            temp_file = f.name

        try:
            with pytest.raises(ValueError):
                self.parser.parse_file(temp_file)
        finally:
            os.unlink(temp_file)

    def test_clear_parser_state(self):
        """测试清空解析器状态"""
        spec_content = "### [CLR-001] 测试规则\n\n内容"
        temp_file = self.create_temp_spec_file(spec_content)

        try:
            self.parser.parse_file(temp_file)
            assert len(self.parser) == 1

            self.parser.clear()
            assert len(self.parser) == 0
            assert self.parser.parsed_files_count == 0
        finally:
            os.unlink(temp_file)

    def test_rule_to_dict_conversion(self):
        """测试规则对象字典转换"""
        rule = SpecRule(
            rule_id="DICT_TEST_001",
            title="字典转换测试",
            content="测试内容",
            category="test",
            priority="high",
            severity="error",
            tags=["tag1", "tag2"],
        )

        d = rule.to_dict()
        assert d["rule_id"] == "DICT_TEST_001"
        assert d["title"] == "字典转换测试"
        assert len(d["tags"]) == 2
        assert "tag1" in d["tags"]

    def test_multiline_content_extraction(self):
        """测试多行内容提取"""
        spec_content = """# 多行测试

### [ML-001] 复杂规则
**优先级**: high

这是第一段内容。

这是第二段内容，可能包含：
- 列表项1
- 列表项2

这是第三段总结。
"""
        temp_file = self.create_temp_spec_file(spec_content)

        try:
            rules = self.parser.parse_file(temp_file)
            assert len(rules) == 1
            content = rules[0].content

            assert "第一段" in content
            assert "第二段" in content
            assert "列表项1" in content
            assert "第三段" in content
        finally:
            os.unlink(temp_file)


# ============================================================================
# 主入口
# ============================================================================

if __name__ == "__main__":
    # 直接运行测试
    pytest.main([__file__, "-v", "--tb=short"])
