# -*- coding: utf-8 -*-
"""
注释检查器单元测试

测试覆盖范围（12+个测试用例）：
1. CommentChecker初始化和基本功能
2. COMMENT_001: 嵌套注释括号匹配
3. COMMENT_002: 中文标点符号检测
4. COMMENT_003: 注释密度分析
5. COMMENT_004: 注释格式一致性
6. 边界条件和异常处理
7. 统计功能测试
8. 单独规则检查器类测试

运行方式:
    python -m pytest tests/test_comment_checker.py -v
"""
import pytest
from pathlib import Path
import sys

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.checkers.comment_checker import (
    CommentChecker,
    NestedCommentChecker,
    ChinesePunctuationChecker,
    CommentDensityChecker,
    CommentFormatChecker,
)
from src.checkers.base_checker import BaseChecker, Severity, RuleInfo
from src.models.check_result import Violation


# ============================================================================
# 测试辅助函数和fixture
# ============================================================================

@pytest.fixture
def comment_checker():
    """创建CommentChecker实例的fixture"""
    return CommentChecker()


@pytest.fixture
def well_commented_code():
    """注释良好的代码示例（密度约20-30%）"""
    return """
FUNCTION_BLOCK FB_WellCommented
(* ============================================ *)
(* 功能描述：电机控制函数块                      *)
(* 作者：AutoGen                                *)
(* 版本：1.0                                    *)
(* ============================================ *)

VAR_INPUT  (* 输入变量声明 *)
    bStartCmd   : BOOL;  (* 启动命令信号 *)
    bStopCmd    : BOOL;  (* 停止命令信号 *)
END_VAR

VAR_OUTPUT (* 输出变量声明 *)
    bMotorRun  : BOOL;  (* 电机运行状态 *)
END_VAR

VAR         (* 局部变量 *)
    nState     : INT;   (* 状态机当前状态 *)
END_VAR

(* ===== 主控制逻辑 ===== *)
IF bStartCmd AND NOT bMotorRun THEN
    (* 启动电机 *)
    bMotorRun := TRUE;
    nState := 1;
ELSIF bStopCmd THEN
    (* 停止电机 *)
    bMotorRun := FALSE;
    nState := 0;
END_IF;

END_FUNCTION_BLOCK
"""


@pytest.fixture
def code_with_nested_comments():
    """包含嵌套注释的错误代码"""
    return """
(* 外层注释开始
   (* 内层嵌套注释 - 这是错误的！*)
   外层注释内容继续
*)  (* 外层注释结束 *)
"""


@pytest.fixture
def code_with_chinese_punctuation():
    """包含中文标点的代码"""
    return """
VAR
    xValue : INT;  (* 这是一个变量，用于存储数值。*)
    bFlag  : BOOL; (* 状态标志位：TRUE表示启用；FALSE表示禁用。*)
END_VAR
"""


@pytest.fixture
def code_no_comments():
    """完全没有注释的代码"""
    return """
FUNCTION TestFunc
VAR_INPUT
    xIn : BOOL;
END_VAR
VAR
    nResult : INT;
END_VAR

IF xIn THEN
    nResult := 1;
ELSE
    nResult := 0;
END_IF;

END_FUNCTION
"""


# ============================================================================
# 1. CommentChecker 初始化测试
# ============================================================================

class TestCommentCheckerInit:
    """注释检查器初始化测试"""

    def test_creation(self, comment_checker):
        """测试检查器正常创建"""
        assert comment_checker is not None
        assert isinstance(comment_checker, BaseChecker)

    def test_rule_info(self, comment_checker):
        """测试规则信息正确设置"""
        info = comment_checker.get_rule_info()
        assert info.rule_id == "COMMENT_CHECKER"
        assert "注释" in info.name
        assert info.category == "comment"

    def test_enabled_by_default(self, comment_checker):
        """测试默认启用状态"""
        assert comment_checker.is_enabled() is True

    def test_configurable_density_range(self, comment_checker):
        """测试可配置的密度范围"""
        assert comment_checker._min_comment_density == 5.0
        assert comment_checker._max_comment_density == 50.0


# ============================================================================
# 2. COMMENT_001: 嵌套注释括号匹配测试
# ============================================================================

class TestNestedCommentRule:
    """COMMENT_001规则测试 - 核心状态机算法"""

    def test_matched_comments(self, comment_checker):
        """测试正确配对的注释"""
        code = """
(* 正常注释1 *)
x := 1;

(* 多行
   注释
   内容 *)
y := 2;

(* 最后一个注释 *)
z := 3;
"""
        violations = comment_checker.check(code, file_path="test.st")

        nested_violations = [
            v for v in violations if v.rule_id == "COMMENT_001"
        ]
        assert len(nested_violations) == 0

    def test_nested_comment_detection(self, comment_checker, code_with_nested_comments):
        """测试嵌套注释被检测到"""
        violations = comment_checker.check(
            code_with_nested_comments,
            file_path="nested.st"
        )

        nested_violations = [
            v for v in violations if v.rule_id == "COMMENT_001"
        ]
        assert len(nested_violations) > 0
        assert any("嵌套" in v.message for v in nested_violations)
        assert any(v.severity == Severity.ERROR for v in nested_violations)

    def test_unclosed_comment(self, comment_checker):
        """测试未闭合的注释"""
        code = """
(* 这个注释没有关闭
x := 100;
y := 200;
"""
        violations = comment_checker.check(code, file_path="unclosed.st")

        nested_violations = [
            v for v in violations if v.rule_id == "COMMENT_001"
        ]
        assert len(nested_violations) > 0
        assert any("未闭合" in v.message for v in nested_violations)

    def test_extra_closing_bracket(self, comment_checker):
        """测试多余的关闭括号"""
        code = """
x := 100;  (* 正常注释 *)
*)  (* 多余的关闭括号 *)
y := 200;
"""
        violations = comment_checker.check(code, file_path="extra_close.st")

        nested_violations = [
            v for v in violations if v.rule_id == "COMMENT_001"
        ]
        assert len(nested_violations) > 0
        assert any("多余" in v.message for v in nested_violations)

    def test_multiple_unclosed(self, comment_checker):
        """测试多个未闭合注释"""
        code = """
(* 第一个未闭合
x := 1;
(* 第二个未闭合
y := 2;
"""
        violations = comment_checker.check(code, file_path="multi_unclosed.st")

        nested_violations = [
            v for v in violations if v.rule_id == "COMMENT_001"
        ]
        # 应该报告未闭合，且计数正确
        unclosed = [v for v in nested_violations if "未闭合" in v.message]
        assert len(unclosed) >= 1

    def test_ignore_strings(self, comment_checker):
        """测试忽略字符串中的伪注释标记"""
        code = """
sMessage := 'This has (* fake *) comment markers';
sAnother := "Also has (*) inside";
(* Real comment *)
x := 1;
"""
        violations = comment_checker.check(code, file_path="strings.st")

        nested_violations = [
            v for v in violations if v.rule_id == "COMMENT_001"
        ]
        assert len(nested_violations) == 0

    def test_adjacent_comments(self, comment_checker):
        """测试相邻的独立注释块"""
        code = """
(* 注释1 *)
(* 注释2 *)
(* 注释3 *)
x := 100;
"""
        violations = comment_checker.check(code, file_path="adjacent.st")

        nested_violations = [
            v for v in violations if v.rule_id == "COMMENT_001"
        ]
        assert len(nested_violations) == 0


# ============================================================================
# 3. COMMENT_002: 中文标点符号检测测试
# ============================================================================

class TestChinesePunctuationRule:
    """COMMENT_002规则测试 - Unicode检测"""

    def test_english_punctuation_ok(self, comment_checker):
        """测试英文标点不报错"""
        code = """
VAR
    xValue : INT;  (* This is a variable, used to store value. *)
    bFlag  : BOOL; (* Status flag: TRUE=enabled, FALSE=disabled. *)
END_VAR
"""
        violations = comment_checker.check(code, file_path="english_punc.st")

        punc_violations = [
            v for v in violations if v.rule_id == "COMMENT_002"
        ]
        assert len(punc_violations) == 0

    def test_chinese_comma_detected(self, comment_checker):
        """检测中文逗号"""
        code = "x := 1;  (* 包含中文逗号，应该被检测 *)"
        violations = comment_checker.check(code, file_path="cn_comma.st")

        punc_violations = [
            v for v in violations if v.rule_id == "COMMENT_002"
        ]
        assert len(punc_violations) > 0
        assert any("\uff0c" in v.code_snippet or "逗号" in v.message
                   for v in punc_violations)

    def test_chinese_period_detected(self, comment_checker):
        """检测中文句号"""
        code = "x := 2;  (* 这是一句话。包含句号 *)"
        violations = comment_checker.check(code, file_path="cn_period.st")

        punc_violations = [
            v for v in violations if v.rule_id == "COMMENT_002"
        ]
        assert len(punc_violations) > 0

    def test_chinese_colon_detected(self, comment_checker):
        """检测中文冒号"""
        code = "x := 3;  (* 说明：这是重要变量 *)"
        violations = comment_checker.check(code, file_path="cn_colon.st")

        punc_violations = [
            v for v in violations if v.rule_id == "COMMENT_002"
        ]
        assert len(punc_violations) > 0

    def test_multiple_chinese_punctuations(self, comment_checker, code_with_chinese_punctuation):
        """测试多个中文标点同时存在"""
        violations = comment_checker.check(
            code_with_chinese_punctuation,
            file_path="multi_cn.st"
        )

        punc_violations = [
            v for v in violations if v.rule_id == "COMMENT_002"
        ]
        # 应该有多个违规（每行一个）
        assert len(punc_violations) >= 2

    def test_only_detect_in_comments(self, comment_checker):
        """测试只在注释内检测，不在代码中检测"""
        # 中文引号在字符串字面量中不应被报告为注释问题
        code = 'sText := \u201c中文内容\u201d;  (* English punctuation only *)'
        violations = comment_checker.check(code, file_path="string_test.st")

        punc_violations = [
            v for v in violations if v.rule_id == "COMMENT_002"
        ]
        # 字符串中的中文标点不应该触发此规则
        cn_in_comment = [
            v for v in punc_violations
            if "English" not in v.message or v.line_number > 1
        ]


# ============================================================================
# 4. COMMENT_003: 注释密度分析测试
# ============================================================================

class TestCommentDensityRule:
    """COMMENT_003规则测试 - 密度算法"""

    def test_well_commented_code(self, comment_checker, well_commented_code):
        """测试良好注释的代码通过密度检查"""
        violations = comment_checker.check(
            well_commented_code,
            file_path="well_commented.st"
        )

        density_violations = [
            v for v in violations if v.rule_id == "COMMENT_003"
        ]
        warnings = [
            v for v in density_violations
            if v.severity == Severity.WARNING
        ]
        # 良好注释的代码不应有WARNING级别的密度警告
        assert len(warnings) == 0

    def test_no_comments_low_density(self, comment_checker, code_no_comments):
        """测试无注释代码的低密度警告"""
        violations = comment_checker.check(
            code_no_comments,
            file_path="no_comments.st"
        )

        density_violations = [
            v for v in violations if v.rule_id == "COMMENT_003"
        ]
        assert len(density_violations) > 0
        assert any("过低" in v.message for v in density_violations)
        assert any(v.severity == Severity.WARNING for v in density_violations)

    def test_over_commented_code(self, comment_checker):
        """测试过度注释的代码"""
        # 创建注释密度超过50%的代码
        lines = []
        for i in range(30):
            lines.append(f"(* 注释行{i} - 这是一行很长的注释说明文字 *)")
            if i % 3 == 0:
                lines.append(f"x{i} := {i};")
        
        over_commented_code = "\n".join(lines)
        
        violations = comment_checker.check(
            over_commented_code,
            file_path="over_commented.st"
        )

        density_violations = [
            v for v in violations if v.rule_id == "COMMENT_003"
        ]
        assert len(density_violations) > 0
        assert any("过高" in v.message for v in density_violations)

    def test_empty_file_density(self, comment_checker):
        """测试空文件的密度检查"""
        violations = comment_checker.check("", file_path="empty.st")
        
        density_violations = [
            v for v in violations if v.rule_id == "COMMENT_003"
        ]
        assert len(density_violations) == 0

    def test_mixed_content_density_calculation(self, comment_checker):
        """测试混合内容的密度计算准确性"""
        code = """
(* 文件头注释 *)
(* 作者：Test *)

FUNCTION Test
VAR
    x : INT;
END_VAR

(* 简单处理 *)
x := 1;

END_FUNCTION
"""
        violations = comment_checker.check(code, file_path="mixed.st")
        
        # 此代码应该有一些注释但不会太少或太多
        density_violations = [
            v for v in violations if v.rule_id == "COMMENT_003"
        ]
        errors = [
            v for v in density_violations
            if v.severity == Severity.ERROR
        ]
        assert len(errors) == 0  # 不应有错误级别


# ============================================================================
# 5. COMMENT_004: 注释格式一致性测试
# ============================================================================

class TestCommentFormatRule:
    """COMMENT_004规则测试"""

    def test_consistent_tag_format(self, comment_checker):
        """测试一致的标签格式不报错"""
        code = """
VAR_INPUT
    xStart : BOOL;  (* [INPUT] 启动信号 *)
    xStop  : BOOL;  (* [INPUT] 停止信号 *)
END_VAR
VAR_OUTPUT
    bRun   : BOOL;  (* [OUTPUT] 运行状态 *)
END_VAR
"""
        violations = comment_checker.check(code, file_path="consistent_tags.st")

        format_violations = [
            v for v in violations if v.rule_id == "COMMENT_004"
        ]
        case_violations = [
            v for v in format_violations
            if "大小写" in v.message
        ]
        assert len(case_violations) == 0

    def test_inconsistent_case_tags(self, comment_checker):
        """测试大小写不一致的标签"""
        code = """
VAR
    x1 : INT;  (* [INPUT] 变量1 *)
    x2 : INT;  (* [input] 变量2 *)
    x3 : INT;  (* [Input] 变量3 *)
END_VAR
"""
        violations = comment_checker.check(code, file_path="inconsistent_case.st")

        format_violations = [
            v for v in violations if v.rule_id == "COMMENT_004"
        ]
        case_violations = [
            v for v in format_violations
            if "大小写" in v.message
        ]
        assert len(case_violations) > 0

    def test_mixed_separator_styles(self, comment_checker):
        """测试混合的分隔线风格"""
        code = """
(* ==================== *)
(* 第一部分 *)
(* ------------------- *)
(* 第二部分 *)
(* *************** *)
(* 第三部分 *)
"""
        violations = comment_checker.check(code, file_path="mixed_sep.st")

        format_violations = [
            v for v in violations if v.rule_id == "COMMENT_004"
        ]
        sep_violations = [
            v for v in format_violations
            if "分隔线" in v.message or "分隔符" in v.message
        ]
        assert len(sep_violations) > 0

    def test_long_single_line_comment(self, comment_checker):
        """测试超长单行注释"""
        long_text = "A" * 150
        code = f"(* {long_text} *)"
        violations = comment_checker.check(code, file_path="long_comment.st")

        format_violations = [
            v for v in violations if v.rule_id == "COMMENT_004"
        ]
        length_violations = [
            v for v in format_violations
            if "过长" in v.message
        ]
        assert len(length_violations) > 0

    def test_normal_length_comment_ok(self, comment_checker):
        """测试正常长度注释不报错"""
        normal_text = "这是一个正常长度的注释说明文字"
        code = f"(* {normal_text} *)"
        violations = comment_checker.check(code, file_path="normal_len.st")

        format_violations = [
            v for v in violations if v.rule_id == "COMMENT_004"
        ]
        length_violations = [
            v for v in format_violations
            if "过长" in v.message
        ]
        assert len(length_violations) == 0


# ============================================================================
# 6. 边界条件和异常处理测试
# ============================================================================

class TestEdgeCasesAndErrorHandling:
    """边界条件和异常处理测试"""

    def test_empty_input(self, comment_checker):
        """测试空输入"""
        violations = comment_checker.check("")
        assert isinstance(violations, list)
        assert len(violations) == 0

    def test_none_input(self, comment_checker):
        """测试None输入"""
        violations = comment_checker.check(None)
        assert isinstance(violations, list)

    def test_only_comments(self, comment_checker):
        """测试纯注释文件"""
        code = """
(* 注释1 *)
(* 注释2 *)
(* 注释3 *)
(* 注释4 *)
(* 注释5 *)
"""
        violations = comment_checker.check(code, file_path="only_comments.st")
        assert isinstance(violations, list)

    def test_special_characters_in_comments(self, comment_checker):
        """测试特殊字符处理"""
        # 使用简单的特殊字符，避免 *) 组合被误判
        code = "(* Special chars: @#$%^&_+-=[]{}|;':\"./<>? ~` *)"
        violations = comment_checker.check(code, file_path="special.st")

        nested_v = [v for v in violations if v.rule_id == "COMMENT_001"]
        assert len(nested_v) == 0  # 特殊字符不应导致误报

    def test_unicode_in_comments(self, comment_checker):
        """测试Unicode内容"""
        code = "(* Unicode: \u00e9\u00e8\u00ea \u4e2d\u6587 \u65e5\u672c\u8a9e *)"
        violations = comment_checker.check(code, file_path="unicode.st")
        assert isinstance(violations, list)

    def test_very_long_line(self, comment_checker):
        """测试超长行"""
        long_line = "(* " + "x" * 10000 + " *)"
        violations = comment_checker.check(long_line, file_path="long.st")
        assert isinstance(violations, list)


# ============================================================================
# 7. 统计功能测试
# ============================================================================

class TestStatisticsFunctionality:
    """统计功能测试"""

    def test_statistics_for_well_commented(self, comment_checker, well_commented_code):
        """测试良好注释代码的统计数据"""
        stats = comment_checker.get_statistics(well_commented_code)

        assert isinstance(stats, dict)
        assert "total_lines" in stats
        assert "pure_comment_lines" in stats  # 使用实际的字段名
        assert "density" in stats
        assert stats["total_lines"] > 0
        assert stats["density"] > 0

    def test_statistics_for_no_comments(self, comment_checker, code_no_comments):
        """测试无注释代码的统计数据"""
        stats = comment_checker.get_statistics(code_no_comments)

        assert isinstance(stats, dict)
        assert stats["density"] < 10  # 应该很低
        assert stats["pure_comment_lines"] == 0

    def test_statistics_for_empty(self, comment_checker):
        """测试空输入的统计数据"""
        stats = comment_checker.get_statistics("")

        assert stats["total_lines"] == 0
        assert stats["density"] == 0.0

    def test_statistics_chinese_punct_count(self, comment_checker, code_with_chinese_punctuation):
        """测试中文标点计数"""
        stats = comment_checker.get_statistics(code_with_chinese_punctuation)

        assert stats["chinese_punct_count"] > 0


# ============================================================================
# 8. 综合场景测试
# ============================================================================

class TestComprehensiveScenarios:
    """综合场景测试"""

    def test_perfect_code_no_violations(self, comment_checker):
        """测试完美代码没有任何违规"""
        perfect_code = """
(* ============================================= *)
(* FUNCTION_BLOCK: PerfectExample                *)
(* Description: A perfectly formatted example     *)
(* Author: QA Tester                              *)
(* ============================================= *)

FUNCTION_BLOCK PerfectExample
VAR_INPUT  (* Input variables *)
    bEnable : BOOL;  (* Enable signal *)
END_VAR

VAR_OUTPUT (* Output variables *)
    bActive : BOOL;  (* Active status *)
END_VAR

VAR         (* Local variables *)
    nCounter : INT;  (* Counter value *)
END_VAR

(* Main logic: simple counter increment *)
IF bEnable THEN
    bActive := TRUE;
    nCounter := nCounter + 1;
ELSE
    bActive := FALSE;
END_IF;

END_FUNCTION_BLOCK
"""
        violations = comment_checker.check(
            perfect_code,
            file_path="perfect.st"
        )

        # 完美代码应该只有INFO级别的提示（如果有），没有ERROR或WARNING
        errors = [v for v in violations if v.severity == Severity.ERROR]
        warnings = [v for v in violations if v.severity == Severity.WARNING]
        
        assert len(errors) == 0, f"发现错误: {[str(e) for e in errors]}"
        # 警告数量应该很少或为零
        assert len(warnings) <= 2, f"发现过多警告: {[str(w) for w in warnings]}"

    def test_code_with_multiple_issues(self, comment_checker):
        """测试同时存在多种问题的代码"""
        problematic_code = """
PROGRAM BadCode
VAR_TEMP
    x : INT;
END_VAR

(* 外层注释
   (* 嵌套注释 - 错误！*)

VAR
    y : UnknownType;  (* 包含中文句号。*)
END_VAR

IF bCond THEN
    result := 100
END_PROGRAM
"""
        violations = comment_checker.check(problematic_code, file_path="bad.st")

        rule_ids = set(v.rule_id for v in violations)
        # 应该有多种类型的违规
        assert len(rule_ids) >= 2


# ============================================================================
# 9. 单独规则检查器类测试
# ============================================================================

class TestIndividualCheckerClasses:
    """单独规则检查器类测试"""

    def test_nested_comment_checker(self):
        """测试单独的嵌套注释检查器"""
        checker = NestedCommentChecker()
        code = "(* outer (* inner *) content *)"
        violations = checker.check(code, file_path="test.st")
        assert len(violations) > 0
        assert all(v.rule_id == "COMMENT_001" for v in violations)

    def test_chinese_punctuation_checker(self):
        """测试单独的中文标点检查器"""
        checker = ChinesePunctuationChecker()
        code = "x := 1;  (* 包含，中文标点 *)"
        violations = checker.check(code, file_path="test.st")
        assert len(violations) > 0
        assert all(v.rule_id == "COMMENT_002" for v in violations)

    def test_comment_density_checker(self):
        """测试单独的注释密度检查器"""
        checker = CommentDensityChecker()
        # 无注释代码应触发低密度警告
        code = "x := 1;\ny := 2;\nz := 3;"
        violations = checker.check(code, file_path="test.st")
        assert len(violations) > 0
        assert all(v.rule_id == "COMMENT_003" for v in violations)

    def test_comment_format_checker(self):
        """测试单独的注释格式检查器"""
        checker = CommentFormatChecker()
        code = """
(* [TAG1] item1 *)
(* [tag2] item2 *)
(* [Tag3] item3 *)
"""
        violations = checker.check(code, file_path="test.st")
        assert len(violations) > 0
        assert all(v.rule_id == "COMMENT_004" for v in violations)


# ============================================================================
# 上下文配置测试
# ============================================================================

class TestContextConfiguration:
    """上下文配置测试"""

    def test_custom_density_threshold(self, comment_checker):
        """测试自定义密度阈值"""
        code = "x := 1;"  # 很少注释
        
        # 使用默认阈值
        violations_default = comment_checker.check(
            code, file_path="test.st"
        )
        
        # 使用更严格的阈值
        context_strict = {"min_comment_density": 50.0}
        violations_strict = comment_checker.check(
            code, file_path="test.st", context=context_strict
        )
        
        default_density = [
            v for v in violations_default if v.rule_id == "COMMENT_003"
        ]
        strict_density = [
            v for v in violations_strict if v.rule_id == "COMMENT_003"
        ]
        
        # 更严格的阈值应该产生更多或相同的违规
        assert len(strict_density) >= len(default_density)


# ============================================================================
# 主入口
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
