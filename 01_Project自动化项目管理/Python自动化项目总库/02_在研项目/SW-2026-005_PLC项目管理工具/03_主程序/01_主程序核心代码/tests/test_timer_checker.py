# -*- coding: utf-8 -*-
"""
定时器检查器单元测试模块

对TimerChecker类的所有功能进行全面的单元测试，
覆盖TIMER_001到TIMER_005共5条规则的各种场景。

测试用例包括:
    - 正常代码的通过测试
    - 违规代码的检测测试
    - 边界条件测试
    - 规则启用/禁用测试
    - 配置参数修改测试

Author: PLC Code Quality Test Team
Version: 1.0.0
"""

import pytest
from src.checkers.timer_checker import TimerChecker
from src.checkers.base_checker import Severity
from src.models.check_result import Violation


@pytest.fixture
def timer_checker() -> TimerChecker:
    """
    创建TimerChecker实例的fixture

    Returns:
        TimerChecker: 新创建的检查器实例
    """
    return TimerChecker()


class TestTimerCheckerInit:
    """TimerChecker初始化和基本属性测试"""

    def test_creation(self, timer_checker):
        """测试检查器正常创建"""
        assert timer_checker is not None
        assert timer_checker.rule_info.rule_id == "TIMER_CHECKER"
        assert timer_checker.rule_info.category == "timer"

    def test_rule_infos_count(self, timer_checker):
        """测试规则信息数量正确"""
        rule_infos = timer_checker.get_rule_infos()
        assert len(rule_infos) == 5  # TIMER_001到TIMER_005

    def test_all_rule_ids_exist(self, timer_checker):
        """测试所有预期的规则ID都存在"""
        expected_ids = ["TIMER_001", "TIMER_002", "TIMER_003", "TIMER_004", "TIMER_005"]
        rule_infos = timer_checker.get_rule_infos()

        for rule_id in expected_ids:
            assert rule_id in rule_infos
            assert rule_infos[rule_id].rule_id == rule_id

    def test_default_nesting_depth(self, timer_checker):
        """测试默认嵌套深度为3"""
        # 通过私有属性访问（仅用于测试）
        assert timer_checker._max_nesting_depth == 3

    def test_repr(self, timer_checker):
        """测试字符串表示"""
        repr_str = repr(timer_checker)
        assert "TimerChecker" in repr_str
        assert "TIMER_CHECKER" in repr_str


class TestTimer001NamingConvention:
    """规则TIMER_001: 定时器变量命名规范测试"""

    def test_ton_with_correct_prefix(self, timer_checker):
        """测试TON定时器使用正确的前缀ton_"""
        code = """
VAR
    ton_StartDelay : TON;
END_VAR
"""
        violations = timer_checker.check(code)
        timer_001_violations = [v for v in violations if v.rule_id == "TIMER_001"]
        assert len(timer_001_violations) == 0

    def test_tof_with_correct_prefix(self, timer_checker):
        """测试TOF定时器使用正确的前缀tof_"""
        code = """
VAR
    tof_StopDelay : TOF;
END_VAR
"""
        violations = timer_checker.check(code)
        timer_001_violations = [v for v in violations if v.rule_id == "TIMER_001"]
        assert len(timer_001_violations) == 0

    def test_tp_with_correct_prefix(self, timer_checker):
        """测试TP定时器使用正确的前缀tp_"""
        code = """
VAR
    tp_PulseGen : TP;
END_VAR
"""
        violations = timer_checker.check(code)
        timer_001_violations = [v for v in violations if v.rule_id == "TIMER_001"]
        assert len(timer_001_violations) == 0

    def test_ton_without_prefix(self, timer_checker):
        """测试TON定时器缺少ton_前缀"""
        code = """
VAR
    myTimer : TON;
END_VAR
"""
        violations = timer_checker.check(code)
        timer_001_violations = [v for v in violations if v.rule_id == "TIMER_001"]
        assert len(timer_001_violations) == 1
        assert "myTimer" in timer_001_violations[0].message
        assert "ton_" in timer_001_violations[0].message

    def test_tof_without_prefix(self, timer_checker):
        """测试TOF定时器缺少tof_前缀"""
        code = """
VAR
    delayTimer : TOF;
END_VAR
"""
        violations = timer_checker.check(code)
        timer_001_violations = [v for v in violations if v.rule_id == "TIMER_001"]
        assert len(timer_001_violations) == 1
        assert "tof_" in timer_001_violations[0].suggestion

    def test_multiple_naming_violations(self, timer_checker):
        """测试多个命名违规同时存在"""
        code = """
VAR
    timer1 : TON;
    timer2 : TOF;
    tp_ok : TP;  (* 这个是正确的 *)
    badName : TON;
END_VAR
"""
        violations = timer_checker.check(code)
        timer_001_violations = [v for v in violations if v.rule_id == "TIMER_001"]
        # 应该检测到3个违规 (timer1, timer2, badName)
        assert len(timer_001_violations) == 3

    def test_case_insensitive_matching(self, timer_checker):
        """测试大小写不敏感的匹配"""
        code = """
VAR
    MY_TIMER : ton;  (* 小写类型 *)
END_VAR
"""
        violations = timer_checker.check(code)
        timer_001_violations = [v for v in violations if v.rule_id == "TIMER_001"]
        assert len(timer_001_violations) == 1


class TestTimer002InstantiationCompleteness:
    """规则TIMER_002: 定时器实例化完整性测试"""

    def test_complete_instantiation(self, timer_checker):
        """测试完整的定时器实例化（包含PT和ET）"""
        code = """
VAR
    ton_Delay : TON := (PT := T#5s, ET := tElapsed);
END_VAR
"""
        violations = timer_checker.check(code)
        timer_002_violations = [v for v in violations if v.rule_id == "TIMER_002"]
        assert len(timer_002_violations) == 0

    def test_missing_pt_parameter(self, timer_checker):
        """测试缺少PT参数的实例化"""
        code = """
VAR
    ton_Delay : TON := (ET := tElapsed);
END_VAR
"""
        violations = timer_checker.check(code)
        timer_002_violations = [v for v in violations if v.rule_id == "TIMER_002"]
        assert len(timer_002_violations) == 1
        assert "PT" in timer_002_violations[0].message

    def test_missing_et_parameter(self, timer_checker):
        """测试缺少ET参数的实例化"""
        code = """
VAR
    tof_OffDelay : TOF := (PT := T#10s);
END_VAR
"""
        violations = timer_checker.check(code)
        timer_002_violations = [v for v in violations if v.rule_id == "TIMER_002"]
        assert len(timer_002_violations) == 1
        assert "ET" in timer_002_violations[0].message

    def test_missing_both_parameters(self, timer_checker):
        """测试同时缺少PT和ET参数"""
        code = """
VAR
    tp_Pulse : TP := ();
END_VAR
"""
        violations = timer_checker.check(code)
        timer_002_violations = [v for v in violations if v.rule_id == "TIMER_002"]
        assert len(timer_002_violations) == 1
        assert "PT" in timer_002_violations[0].message
        assert "ET" in timer_002_violations[0].message

    def test_simple_declaration_no_error(self, timer_checker):
        """测试简单声明（无初始值）不应触发此规则"""
        code = """
VAR
    ton_Delay : TON;
END_VAR
"""
        violations = timer_checker.check(code)
        timer_002_violations = [v for v in violations if v.rule_id == "TIMER_002"]
        assert len(timer_002_violations) == 0

    def test_severity_is_error(self, timer_checker):
        """测试此规则的严重级别为ERROR"""
        code = """
VAR
    ton_Bad : TON := (PT := T#5s);  (* 缺少ET *)
END_VAR
"""
        violations = timer_checker.check(code)
        timer_002_violations = [v for v in violations if v.rule_id == "TIMER_002"]
        assert len(timer_002_violations) > 0
        assert timer_002_violations[0].severity == Severity.ERROR


class TestTimer003InvocationParameters:
    """规则TIMER_003: 定时器调用参数完整性测试"""

    def test_complete_invocation(self, timer_checker):
        """测试完整的定时器调用（包含IN和PT）"""
        code = """
ton_Delay(IN := bStart, PT := T#5s);
"""
        violations = timer_checker.check(code)
        timer_003_violations = [v for v in violations if v.rule_id == "TIMER_003"]
        assert len(timer_003_violations) == 0

    def test_missing_in_parameter(self, timer_checker):
        """测试调用时缺少IN参数"""
        code = """
ton_Delay(PT := T#5s);
"""
        violations = timer_checker.check(code)
        timer_003_violations = [v for v in violations if v.rule_id == "TIMER_003"]
        assert len(timer_003_violations) == 1
        assert "IN" in timer_003_violations[0].message

    def test_missing_pt_parameter(self, timer_checker):
        """测试调用时缺少PT参数"""
        code = """
ton_Delay(IN := bCondition);
"""
        violations = timer_checker.check(code)
        timer_003_violations = [v for v in violations if v.rule_id == "TIMER_003"]
        assert len(timer_003_violations) == 1
        assert "PT" in timer_003_violations[0].message

    def test_missing_both_parameters(self, timer_checker):
        """测试调用时同时缺少IN和PT"""
        code = """
tof_OffDelay();
"""
        violations = timer_checker.check(code)
        timer_003_violations = [v for v in violations if v.rule_id == "TIMER_003"]
        assert len(timer_003_violations) == 1
        assert "IN" in timer_003_violations[0].message
        assert "PT" in timer_003_violations[0].message

    def test_invocation_not_confused_with_instantiation(self, timer_checker):
        """确保不会将实例化语句误判为调用"""
        code = """
VAR
    ton_Delay : TON := (PT := T#5s, ET := tElapsed);
END_VAR

(* 调用部分 *)
ton_Delay(IN := bStart, PT := T#5s);
"""
        violations = timer_checker.check(code)
        timer_003_violations = [v for v in violations if v.rule_id == "TIMER_003"]
        # 实例化中的参数不应该被当作调用来检查
        assert len(timer_003_violations) == 0


class TestTimer004ResetLogic:
    """规则TIMER_004: 定时器复位逻辑测试"""

    def test_timer_with_reset(self, timer_checker):
        """测试有复位逻辑的定时器"""
        code = """
VAR
    ton_Delay : TON;
END_VAR

IF bStart THEN
    ton_Delay(IN := TRUE, PT := T#5s);
ELSE
    ton_Delay(IN := FALSE);  (* 复位 *)
END_IF;
"""
        violations = timer_checker.check(code)
        timer_004_violations = [v for v in violations if v.rule_id == "TIMER_004"]
        assert len(timer_004_violations) == 0

    def test_timer_without_reset(self, timer_checker):
        """测试没有复位逻辑的定时器"""
        code = """
VAR
    ton_Delay : TON;
END_VAR

IF bStart THEN
    ton_Delay(IN := TRUE, PT := T#5s);
END_IF;

(* 没有复位操作 *)
"""
        violations = timer_checker.check(code)
        timer_004_violations = [v for v in violations if v.rule_id == "TIMER_004"]
        assert len(timer_004_violations) == 1
        assert "复位" in timer_004_violations[0].message

    def test_multiple_timers_partial_reset(self, timer_checker):
        """测试多个定时器中只有部分复位"""
        code = """
VAR
    ton_First : TON;
    ton_Second : TON;
END_VAR

ton_First(IN := TRUE, PT := T#2s);
ton_Second(IN := TRUE, PT := T#3s);

ton_Second(IN := FALSE);  (* 只有第二个复位 *)
"""
        violations = timer_checker.check(code)
        timer_004_violations = [v for v in violations if v.rule_id == "TIMER_004"]
        # 应该只报告第一个定时器没有复位
        assert len(timer_004_violations) == 1
        assert "ton_First" in timer_004_violations[0].message

    def test_timer_never_activated(self, timer_checker):
        """测试从未被激活的定时器不报复位错误"""
        code = """
VAR
    ton_Standby : TON;
END_VAR

(* 定时器声明但从未使用 *)
"""
        violations = timer_checker.check(code)
        timer_004_violations = [v for v in violations if v.rule_id == "TIMER_004"]
        assert len(timer_004_violations) == 0

    def test_suggestion_contains_reset_code(self, timer_checker):
        """测试建议包含复位代码示例"""
        code = """
VAR
    ton_NoReset : TON;
END_VAR

ton_NoReset(IN := TRUE, PT := T#5s);
"""
        violations = timer_checker.check(code)
        timer_004_violations = [v for v in violations if v.rule_id == "TIMER_004"]
        assert len(timer_004_violations) > 0
        assert "IN := FALSE" in timer_004_violations[0].suggestion


class TestTimer005NestingDepth:
    """规则TIMER_005: 定时器嵌套深度限制测试"""

    def test_within_depth_limit(self, timer_checker):
        """测试嵌套深度在允许范围内"""
        code = """
TON( IN := TON( IN := bCond, PT := T#1s ).Q, PT := T#2s );
"""
        violations = timer_checker.check(code)
        timer_005_violations = [v for v in violations if v.rule_id == "TIMER_005"]
        assert len(timer_005_violations) == 0  # 嵌套深度为2，在限制内

    def test_exceeding_depth_limit(self, timer_checker):
        """测试嵌套深度超过限制"""
        # 创建超过3层嵌套的代码
        code = """
TON(
    IN := TON(
        IN := TON(
            IN := TON(
                IN := bDeep,
                PT := T#1s
            ).Q,
            PT := T#2s
        ).Q,
        PT := T#3s
    ).Q,
    PT := T#4s
);
"""
        violations = timer_checker.check(code)
        timer_005_violations = [v for v in violations if v.rule_id == "TIMER_005"]
        assert len(timer_005_violations) > 0  # 应该检测到超限

    def test_custom_max_depth(self, timer_checker):
        """测试自定义最大嵌套深度"""
        # 设置更严格的限制
        timer_checker.set_max_nesting_depth(1)

        code = """
TON(
    IN := TON(
        IN := bCond,
        PT := T#1s
    ).Q,
    PT := T#2s
);
"""
        violations = timer_checker.check(code)
        timer_005_violations = [v for v in violations if v.rule_id == "TIMER_005"]
        assert len(timer_005_violations) > 0  # 深度为2，现在超过了新的限制

    def test_different_timer_types_nesting(self, timer_checker):
        """测试不同类型定时器的混合嵌套"""
        code = """
TON(
    IN := TOF(
        IN := TP(
            IN := bMixed,
            PT := T#1s
        ).Q,
        PT := T#2s
    ).Q,
    PT := T#3s
);
"""
        violations = timer_checker.check(code)
        timer_005_violations = [v for v in violations if v.rule_id == "TIMER_005"]
        assert len(timer_005_violations) == 0  # 深度为3，刚好在边界

    def test_invalid_depth_value_raises_error(self, timer_checker):
        """测试设置无效的嵌套深度值抛出异常"""
        with pytest.raises(ValueError):
            timer_checker.set_max_nesting_depth(0)

        with pytest.raises(ValueError):
            timer_checker.set_max_nesting_depth(-1)


class TestRuleEnableDisable:
    """规则的启用/禁用功能测试"""

    def test_disable_rule_001(self, timer_checker):
        """测试禁用TIMER_001规则"""
        timer_checker.disable_rule("TIMER_001")

        code = """
VAR
    badName : TON;  (* 应该违反TIMER_001 *)
END_VAR
"""
        violations = timer_checker.check(code)
        timer_001_violations = [v for v in violations if v.rule_id == "TIMER_001"]
        assert len(timer_001_violations) == 0  # 规则已禁用，不应检测到

    def test_enable_disabled_rule(self, timer_checker):
        """测试重新启用已禁用的规则"""
        timer_checker.disable_rule("TIMER_001")
        timer_checker.enable_rule("TIMER_001")

        code = """
VAR
    noPrefix : TON;
END_VAR
"""
        violations = timer_checker.check(code)
        timer_001_violations = [v for v in violations if v.rule_id == "TIMER_001"]
        assert len(timer_001_violations) > 0  # 规则已重新启用

    def test_disable_nonexistent_rule_returns_false(self, timer_checker):
        """测试禁用不存在的规则返回False"""
        result = timer_checker.disable_rule("TIMER_999")
        assert result is False

    def test_enable_nonexistent_rule_returns_false(self, timer_checker):
        """测试启用不存在的规则返回False"""
        result = timer_checker.enable_rule("TIMER_999")
        assert result is False


class TestEdgeCases:
    """边界条件和特殊情况测试"""

    def test_empty_source_code(self, timer_checker):
        """测试空源代码"""
        violations = timer_checker.check("")
        assert len(violations) == 0

    def test_whitespace_only_code(self, timer_checker):
        """测试只有空白的源代码"""
        violations = timer_checker.check("   \n\t\n   ")
        assert len(violations) == 0

    def test_comments_only(self, timer_checker):
        """测试只有注释的源代码"""
        code = """
(* 这是注释 *)
(* 另一个注释 *)
"""
        violations = timer_checker.check(code)
        assert len(violations) == 0

    def test_complex_real_world_example(self, timer_checker):
        """测试复杂真实世界示例"""
        code = """
PROGRAM PLC_PRG
VAR
    (* 定时器声明 *)
    ton_MotorStartup : TON := (PT := T#3s, ET := tMotorElapsed);
    tof_SafetyBrake : TOF := (PT := T#500ms, ET := tBrakeElapsed);
    tp_AlarmPulse : TP := (PT := T#1s, ET := tAlarmElapsed);

    (* 状态标志 *)
    bMotorRunning : BOOL;
    bEmergencyStop : BOOL;
END_VAR

(* 主控制逻辑 *)
IF NOT bEmergencyStop THEN
    IF bMotorRunning THEN
        (* 启动电机延时 *)
        ton_MotorStartup(IN := bMotorRunning, PT := T#3s);

        IF ton_MotorStartup.Q THEN
            (* 电机启动完成 *)
        END_IF;
    ELSE
        (* 复位启动定时器 *)
        ton_MotorStartup(IN := FALSE);

        (* 安全制动延时 *)
        tof_SafetyBrake(IN := TRUE, PT := T#500ms);
    END_IF;
ELSE
    (* 急停处理 *)
    tp_AlarmPulse(IN := TRUE, PT := T#1s);
    tp_AlarmPulse(IN := FALSE);  (* 复位 *)
END_IF;
END_PROGRAM
"""
        violations = timer_checker.check(code)
        # 这段代码应该符合所有规范
        timer_001 = [v for v in violations if v.rule_id == "TIMER_001"]
        timer_002 = [v for v in violations if v.rule_id == "TIMER_002"]
        timer_003 = [v for v in violations if v.rule_id == "TIMER_003"]

        assert len(timer_001) == 0  # 所有命名都正确
        assert len(timer_002) == 0  # 实例化都完整
        assert len(timer_003) == 0  # 调用参数都完整

    def test_file_path_in_violations(self, timer_checker):
        """测试违规记录包含正确的文件路径"""
        code = "badTimer : TON;"
        file_path = "/project/main.st"

        violations = timer_checker.check(code, file_path=file_path)

        assert len(violations) > 0
        for violation in violations:
            assert violation.file_path == file_path

    def test_line_number_accuracy(self, timer_checker):
        """测试行号准确性"""
        code = """
(* 第1行 *)

(* 第3行 *)
badTimer : TON;  (* 第4行 - 应该在这里报错 *)

(* 第6行 *)
"""
        violations = timer_checker.check(code)
        timer_001_violations = [v for v in violations if v.rule_id == "TIMER_001"]

        assert len(timer_001_violations) > 0
        # 行号应该是第4行（从1开始计数）
        assert timer_001_violations[0].line_number == 5

    def test_multiple_rules_triggered_simultaneously(self, timer_checker):
        """测试同一段代码同时触发多条规则"""
        code = """
VAR
    badTimer : TON := (PT := T#5s);  (* 缺少前缀 + 缺少ET *)
END_VAR

badTimer(IN := bStart);  (* 缺少PT参数 *)
badTimer(IN := TRUE, PT := T#5s);  (* 激活但未复位 *)
"""
        violations = timer_checker.check(code)

        rule_ids = set(v.rule_id for v in violations)
        # 应该同时触发多条规则
        assert "TIMER_001" in rule_ids
        assert "TIMER_002" in rule_ids
        assert "TIMER_003" in rule_ids
        assert "TIMER_004" in rule_ids


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
