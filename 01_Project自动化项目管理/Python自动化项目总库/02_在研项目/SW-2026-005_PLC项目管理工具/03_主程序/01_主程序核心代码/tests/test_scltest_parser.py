"""
SCLTest解析器单元测试模块

本模块包含SCLTestParser类的全面单元测试，覆盖：
- 正常解析流程（5个测试用例）
- 各种语句类型的识别和提取
- 边界情况和错误处理
- 数据模型的正确性验证

测试策略：
- 使用真实的valve_test.scltest文件进行集成式测试
- 同时使用构造的测试字符串进行边界条件测试
- 验证解析结果的完整性和准确性

运行方式：
    pytest tests/test_scltest_parser.py -v

作者：双栖资深开发
版本：1.0.0
"""

import pytest
from pathlib import Path
from datetime import datetime

# 导入被测模块
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.test_case import TestStep, StepType, TestCase, TestSuite
from parsers.scltest_parser import SCLTestParser, parse_scltest_file, parse_scltest_string


# ============================================================================
# 测试固定装置
# ============================================================================

@pytest.fixture
def parser():
    """创建解析器实例"""
    return SCLTestParser()


@pytest.fixture
def valve_test_file():
    """获取valve_test.scltest文件路径"""
    base_path = Path(__file__).parent.parent.parent.parent
    test_file = base_path / "0100_项目" / "DJ-2026-000" / "Test" / "valve_test.scltest"

    if not test_file.exists():
        pytest.skip(f"测试文件不存在: {test_file}")

    return test_file


@pytest.fixture
def valve_test_suite(valve_test_file, parser):
    """解析valve_test.scltest得到完整的测试套件"""
    return parser.parse_file(valve_test_file)


# ============================================================================
# 测试组1: 文件级解析测试（使用真实文件）
# ============================================================================

class TestFileLevelParsing:
    """文件级别解析测试"""

    def test_parse_valve_test_file_exists(self, valve_test_file):
        """测试1: 验证测试文件存在且可读"""
        assert valve_test_file.exists()
        assert valve_test_file.suffix.lower() == '.scltest'

    def test_parse_valve_test_suite_basic(self, valve_test_suite):
        """测试2: 验证基本解析结果 - 应包含5个测试用例"""
        assert isinstance(valve_test_suite, TestSuite)
        assert valve_test_suite.test_case_count == 5
        assert valve_test_suite.total_steps > 0
        assert not valve_test_suite.has_errors  # 不应有致命错误

    def test_parse_test_case_names(self, valve_test_suite):
        """测试3: 验证5个测试用例名称正确"""
        names = [tc.name for tc in valve_test_suite.test_cases]
        assert "test1" in names
        assert "test2" in names
        assert "test3" in names
        assert "test4" in names
        assert "test5" in names
        assert len(names) == 5

    def test_parse_total_step_count(self, valve_test_suite):
        """测试4: 验证总步骤数合理"""
        # test1: 2 SET + 1 WAIT + 1 ASSERT = 4
        # test2: 3 SET + 1 WAIT + 1 ASSERT = 5
        # test3: 1 SET + 1 WAIT + 1 ASSERT = 3
        # test4: 1 SET + 1 WAIT + 1 ASSERT = 3
        # test5: 1 SET + 1 WAIT + 1 ASSERT = 3
        # 总计: 18个步骤
        assert valve_test_suite.total_steps == 18


# ============================================================================
# 测试组2: 各测试用例详细验证
# ============================================================================

class TestIndividualTestCases:
    """各个测试用例的详细解析验证"""

    def test_test1_normal_mode_no_fault(self, valve_test_suite):
        """
        测试5: 验证test1解析 - 正常模式下无故障

        预期步骤：
        1. SET GlobalVars.Hmibutton[0] := TRUE
        2. SET GlobalVars.Hmibutton[1] := FALSE
        3. WAIT_CYCLES 1
        4. ASSERT GlobalVars.FaultStatus = FALSE
        """
        test1 = valve_test_suite.get_test_case_by_name("test1")
        assert test1 is not None
        assert test1.step_count == 4

        # 验证步骤顺序和类型
        steps = test1.steps
        assert steps[0].step_type == StepType.SET
        assert steps[0].variable == "GlobalVars.Hmibutton[0]"
        assert steps[0].value is True

        assert steps[1].step_type == StepType.SET
        assert steps[1].variable == "GlobalVars.Hmibutton[1]"
        assert steps[1].value is False

        assert steps[2].step_type == StepType.WAIT_CYCLES
        assert steps[2].cycles == 1

        assert steps[3].step_type == StepType.ASSERT
        assert steps[3].variable == "GlobalVars.FaultStatus"
        assert steps[3].value is False

    def test_test2_open_valve_command(self, valve_test_suite):
        """
        测试6: 验证test2解析 - 开阀命令测试

        预期步骤：
        1. SET Hmibutton[0] := TRUE
        2. SET Hmibutton[1] := TRUE
        3. SET Hmibutton[4] := FALSE
        4. WAIT_CYCLES 2
        5. ASSERT ValveOpen = TRUE
        """
        test2 = valve_test_suite.get_test_case_by_name("test2")
        assert test2 is not None
        assert test2.step_count == 5

        steps = test2.steps

        # 验证3个SET语句
        set_steps = test2.get_steps_by_type(StepType.SET)
        assert len(set_steps) == 3
        assert set_steps[0].variable == "GlobalVars.Hmibutton[0]"
        assert set_steps[1].variable == "GlobalVars.Hmibutton[1]"
        assert set_steps[2].variable == "GlobalVars.Hmibutton[4]"

        # 验证WAIT_CYCLES
        wait_steps = test2.get_steps_by_type(StepType.WAIT_CYCLES)
        assert len(wait_steps) == 1
        assert wait_steps[0].cycles == 2

        # 验证ASSERT
        assert_steps = test2.get_steps_by_type(StepType.ASSERT)
        assert len(assert_steps) == 1
        assert assert_steps[0].variable == "GlobalVars.ValveOpen"
        assert assert_steps[0].value is True

    def test_test3_overcurrent_fault(self, valve_test_suite):
        """
        测试7: 验证test3解析 - 过流故障触发

        预期步骤：
        1. SET Hmibutton[3] := TRUE
        2. WAIT_CYCLES 1
        3. ASSERT FaultStatus = TRUE
        """
        test3 = valve_test_suite.get_test_case_by_name("test3")
        assert test3 is not None
        assert test3.step_count == 3

        steps = test3.steps
        assert steps[0].step_type == StepType.SET
        assert steps[0].variable == "GlobalVars.Hmibutton[3]"
        assert steps[0].value is True

        assert steps[1].step_type == StepType.WAIT_CYCLES
        assert steps[1].cycles == 1

        assert steps[2].step_type == StepType.ASSERT
        assert steps[2].variable == "GlobalVars.FaultStatus"
        assert steps[2].value is True

    def test_test4_timer_a(self, valve_test_suite):
        """
        测试8: 验证test4解析 - 方案A定时器测试

        预期步骤：
        1. SET Hmibutton[7] := TRUE (bStart_A)
        2. WAIT_CYCLES 1000
        3. ASSERT bOut_A = TRUE
        """
        test4 = valve_test_suite.get_test_case_by_name("test4")
        assert test4 is not None
        assert test4.step_count == 3

        assert test4.total_wait_cycles == 1000

        steps = test4.steps
        assert steps[0].variable == "GlobalVars.Hmibutton[7]"
        assert steps[2].variable == "GlobalVars.bOut_A"

    def test_test5_timer_b(self, valve_test_suite):
        """
        测试9: 验证test5解析 - 方案B定时器测试

        预期步骤：
        1. SET Hmibutton[8] := TRUE (bStart_B)
        2. WAIT_CYCLES 1000
        3. ASSERT bOut_B = TRUE
        """
        test5 = valve_test_suite.get_test_case_by_name("test5")
        assert test5 is not None
        assert test5.step_count == 3

        steps = test5.steps
        assert steps[0].variable == "GlobalVars.Hmibutton[8]"
        assert steps[2].variable == "GlobalVars.bOut_B"


# ============================================================================
# 测试组3: 数据模型验证
# ============================================================================

class TestDataModelValidation:
    """数据模型的完整性和方法验证"""

    def test_testcase_properties(self, valve_test_suite):
        """测试10: 验证TestCase的计算属性"""
        test2 = valve_test_suite.get_test_case_by_name("test2")

        assert test2.has_set_steps is True
        assert test2.has_assert_steps is True
        assert test2.step_count == 5
        assert test2.total_wait_cycles == 2

    def test_testsuite_statistics(self, valve_test_suite):
        """测试11: 验证TestSuite的统计功能"""
        assert valve_test_suite.test_case_count == 5
        assert valve_test_suite.total_steps == 18

        # 所有涉及的变量
        variables = valve_test_suite.get_all_variable_names()
        assert len(variables) > 0
        assert "GlobalVars.FaultStatus" in variables
        assert "GlobalVars.ValveOpen" in variables

    def test_serialization_roundtrip(self, valve_test_suite):
        """测试12: 验证序列化/反序列化往返一致性"""
        # 序列化
        data = valve_test_suite.to_dict()
        assert isinstance(data, dict)
        assert 'test_cases' in data

        # 反序列化
        restored = TestSuite.from_dict(data)

        # 验证一致性
        assert restored.test_case_count == valve_test_suite.test_case_count
        assert restored.total_steps == valve_test_suite.total_steps

        for original, restored_tc in zip(
            valve_test_suite.test_cases, restored.test_cases
        ):
            assert original.name == restored_tc.name
            assert original.step_count == restored_tc.step_count

    def test_step_string_representation(self, valve_test_suite):
        """测试13: 验证TestStep的字符串表示"""
        test1 = valve_test_suite.get_test_case_by_name("test1")
        set_step = test1.steps[0]

        str_repr = str(set_step)
        assert "SET" in str_repr
        assert "Hmibutton[0]" in str_repr
        assert "True" in str_repr

    def test_testcase_string_representation(self, valve_test_suite):
        """测试14: 验证TestCase的字符串表示"""
        test1 = valve_test_suite.get_test_case_by_name("test1")
        str_repr = str(test1)

        assert "test1" in str_repr
        assert "4" in str_repr  # 步骤数


# ============================================================================
# 测试组4: 边界情况和错误处理
# ============================================================================

class TestEdgeCasesAndErrorHandling:
    """边界条件和错误处理测试"""

    def test_empty_content(self, parser):
        """测试15: 解析空内容"""
        suite = parser.parse_string("")
        assert suite.test_case_count == 0
        assert suite.total_steps == 0

    def test_only_comments(self, parser):
        """测试16: 只有注释的内容"""
        content = "// This is a comment\n// Another comment\n"
        suite = parser.parse_string(content)
        assert suite.test_case_count == 0

    def test_unclosed_test_case(self, parser):
        """测试17: 未关闭的TEST_CASE（应能恢复）"""
        content = '''
        TEST_CASE "unclosed"
            SET x := TRUE;
            // Missing END_TEST_CASE
        '''
        suite = parser.parse_string(content)
        # 应该能够解析出一个测试用例（即使没有显式关闭）
        assert suite.test_case_count >= 1
        # 应该有警告
        assert len(suite.parse_errors) > 0

    def test_malformed_set_statement(self, parser):
        """测试18: 格式错误的SET语句"""
        content = '''
        TEST_CASE "bad_set"
            SET ;  // 缺少变量和值
            ASSERT x = TRUE;
        END_TEST_CASE
        '''
        suite = parser.parse_string(content)
        # 应该有错误但不会崩溃
        assert suite.test_case_count == 1
        # 可能会有解析错误记录

    def test_special_characters_in_values(self, parser):
        """测试19: 特殊字符值的处理"""
        content = '''
        TEST_CASE "special_chars"
            SET myVar := 'Hello World';
            SET number := -42;
            SET pi := 3.14159;
            ASSERT myVar = 'Hello World';
        END_TEST_CASE
        '''
        suite = parser.parse_string(content)
        assert suite.test_case_count == 1
        tc = suite.test_cases[0]
        assert tc.step_count == 4

        # 验证特殊值被正确解析
        assert tc.steps[0].value == "Hello World"
        assert tc.steps[1].value == -42
        assert abs(tc.steps[2].value - 3.14159) < 0.0001

    def test_multiple_test_cases(self, parser):
        """测试20: 多个连续的测试用例"""
        content = '''
        TEST_CASE "first"
            SET a := TRUE;
            ASSERT a = TRUE;
        END_TEST_CASE

        TEST_CASE "second"
            SET b := FALSE;
            ASSERT b = FALSE;
        END_TEST_CASE

        TEST_CASE "third"
            WAIT_CYCLES 10;
            ASSERT c = 100;
        END_TEST_CASE
        '''
        suite = parser.parse_string(content)
        assert suite.test_case_count == 3
        assert suite.total_steps == 6  # 每个2个步骤

    def test_region_markers_ignored(self, parser):
        """测试21: #region/#endregion标记应被忽略"""
        content = '''
        //#region Test Region
        TEST_CASE "with_regions"
            SET x := 1;
        END_TEST_CASE
        //#endregion
        '''
        suite = parser.parse_string(content)
        assert suite.test_case_count == 1

    def test_blank_lines_and_formatting(self, parser):
        """测试22: 空行和多余空白不影响解析"""
        content = '''

        TEST_CASE "formatted"


            SET   x   :=   TRUE;



            WAIT_CYCLES   5   ;


            ASSERT   x   =   TRUE   ;


        END_TEST_CASE


        '''
        suite = parser.parse_string(content)
        assert suite.test_case_count == 1
        assert suite.test_cases[0].step_count == 3

    def test_get_test_case_names_quick_scan(self, parser, valve_test_file):
        """测试23: 快速扫描测试用例名称（不完全解析）"""
        names = parser.get_test_case_names(valve_test_file)
        assert len(names) == 5
        assert "test1" in names
        assert "test5" in names

    def test_validate_syntax_method(self, parser):
        """测试24: 语法验证方法"""
        valid_content = '''
        TEST_CASE "valid"
            SET x := TRUE;
            ASSERT x = TRUE;
        END_TEST_CASE
        '''
        is_valid, errors = parser.validate_syntax(valid_content)
        assert is_valid is True
        assert len(errors) == 0

        invalid_content = '''
        TEST_CASE "unclosed"
            SET x := TRUE;
        // Missing END_TEST_CASE
        '''
        is_valid, errors = parser.validate_syntax(invalid_content)
        assert is_valid is False  # 不匹配
        assert len(errors) > 0


# ============================================================================
# 测试组5: 便捷函数测试
# ============================================================================

class TestConvenienceFunctions:
    """便捷函数测试"""

    def test_parse_scltest_file_function(self, valve_test_file):
        """测试25: 便捷函数parse_scltest_file"""
        suite = parse_scltest_file(valve_test_file)
        assert isinstance(suite, TestSuite)
        assert suite.test_case_count == 5

    def test_parse_scltest_string_function(self):
        """测试26: 便捷函数parse_scltest_string"""
        content = '''
        TEST_CASE "quick_test"
            SET x := 42;
            ASSERT x = 42;
        END_TEST_CASE
        '''
        suite = parse_scltest_string(content)
        assert suite.test_case_count == 1
        assert suite.test_cases[0].name == "quick_test"


# ============================================================================
# 测试组6: 性能和压力测试
# ============================================================================

class TestPerformanceAndStress:
    """性能和压力测试"""

    def test_large_file_parsing(self, parser):
        """测试27: 大文件解析性能"""
        # 生成包含大量测试用例的内容
        lines = []
        for i in range(100):  # 100个测试用例
            lines.append(f'TEST_CASE "perf_test_{i}"')
            lines.append(f'    SET var{i} := {i % 2 == 0};')
            lines.append(f'    WAIT_CYCLES {(i % 10) + 1};')
            lines.append(f'    ASSERT var{i} = {i % 2 == 0};')
            lines.append('END_TEST_CASE')
            lines.append('')

        content = '\n'.join(lines)

        import time
        start = time.time()
        suite = parser.parse_string(content)
        elapsed = time.time() - start

        # 验证正确性
        assert suite.test_case_count == 100
        assert suite.total_steps == 300  # 每个测试3个步骤

        # 性能要求：100个测试用例应在1秒内解析完成
        assert elapsed < 1.0, f"解析耗时过长: {elapsed:.2f}s"

    def test_deeply_nested_arrays(self, parser):
        """测试28: 深层数组索引解析"""
        content = '''
        TEST_CASE "deep_array"
            SET arr[0][1][2] := TRUE;
            SET matrix[5][3] := 100;
            ASSERT arr[0][1][2] = TRUE;
        END_TEST_CASE
        '''
        suite = parser.parse_string(content)
        assert suite.test_case_count == 1
        tc = suite.test_cases[0]

        # 验证复杂变量名被正确提取
        assert tc.steps[0].variable == "arr[0][1][2]"
        assert tc.steps[1].variable == "matrix[5][3]"


# ============================================================================
# 主入口
# ============================================================================

if __name__ == "__main__":
    # 运行所有测试
    pytest.main([__file__, "-v", "--tb=short"])
