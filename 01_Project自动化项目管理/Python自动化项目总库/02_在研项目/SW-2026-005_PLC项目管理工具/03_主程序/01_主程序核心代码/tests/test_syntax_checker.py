# -*- coding: utf-8 -*-
"""
语法检查器单元测试

测试覆盖范围（13+个测试用例）：
1. SyntaxChecker初始化和基本功能
2. SYNTAX_001: VAR_TEMP位置验证
3. SYNTAX_002: 控制结构配对检测（IF/END_IF, FOR/END_FOR等）
4. SYNTAX_003: FB/函数块结构完整性
5. SYNTAX_004: 语句分号检测
6. SYNTAX_005: 类型合法性验证
7. 边界条件和异常处理
8. 单独规则检查器类测试

运行方式:
    python -m pytest tests/test_syntax_checker.py -v
"""
import pytest
from pathlib import Path
import sys

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.checkers.syntax_checker import (
    SyntaxChecker,
    VarTempPositionChecker,
    ControlStructureChecker,
    FBStructureChecker,
    StatementTerminatorChecker,
    TypeValidityChecker,
)
from src.checkers.base_checker import BaseChecker, Severity, RuleInfo
from src.models.check_result import Violation


# ============================================================================
# 测试辅助函数和fixture
# ============================================================================

@pytest.fixture
def syntax_checker():
    """创建SyntaxChecker实例的fixture"""
    return SyntaxChecker()


@pytest.fixture
def valid_st_code():
    """符合规范的ST代码示例"""
    return """
FUNCTION_BLOCK FB_MotorControl
VAR_INPUT
    bStart       : BOOL;      (* 启动信号 *)
    bStop        : BOOL;      (* 停止信号 *)
END_VAR
VAR_OUTPUT
    bMotorRunning : BOOL;     (* 电机运行状态 *)
END_VAR
VAR
    nState       : INT := 0;  (* 状态机状态 *)
END_VAR

(* 主控制逻辑 *)
IF bStart AND NOT bMotorRunning THEN
    bMotorRunning := TRUE;
    nState := 1;
ELSIF bStop THEN
    bMotorRunning := FALSE;
    nState := 0;
END_IF;

(* 循环计数示例 *)
FOR i := 1 TO 10 DO
    nCounter := nCounter + 1;
END_FOR;
END_FUNCTION_BLOCK
"""


@pytest.fixture
def invalid_st_code_var_temp():
    """包含VAR_TEMP位置错误的代码"""
    return """
PROGRAM MainProgram
VAR_TEMP
    xLocalVar : INT;
END_VAR
VAR
    xGlobalVar : BOOL;
END_VAR
END_PROGRAM
"""


@pytest.fixture
def invalid_st_code_unmatched_if():
    """包含未闭合IF的代码"""
    return """
FUNCTION TestFunc
VAR_INPUT
    xInput : BOOL;
END_VAR

IF xInput THEN
    (* 做一些操作，但忘记END_IF *)
    nResult := 1;

(* 缺少 END_IF *)
END_FUNCTION
"""


@pytest.fixture
def invalid_st_code_missing_semicolon():
    """缺少分号的代码"""
    return """
FUNCTION TestFunc
VAR
    nValue : INT;
END_VAR

nValue := 100
nResult := nValue + 1;

END_FUNCTION
"""


# ============================================================================
# 1. SyntaxChecker 初始化测试
# ============================================================================

class TestSyntaxCheckerInit:
    """语法检查器初始化测试"""

    def test_creation(self, syntax_checker):
        """测试检查器正常创建"""
        assert syntax_checker is not None
        assert isinstance(syntax_checker, BaseChecker)

    def test_rule_info(self, syntax_checker):
        """测试规则信息正确设置"""
        info = syntax_checker.get_rule_info()
        assert info.rule_id == "SYNTAX_CHECKER"
        assert "语法" in info.name
        assert info.category == "syntax"

    def test_enabled_by_default(self, syntax_checker):
        """测试默认启用状态"""
        assert syntax_checker.is_enabled() is True

    def test_enable_disable(self, syntax_checker):
        """测试启用/禁用切换"""
        syntax_checker.disable()
        assert syntax_checker.is_enabled() is False
        syntax_checker.enable()
        assert syntax_checker.is_enabled() is True


# ============================================================================
# 2. SYNTAX_001: VAR_TEMP位置验证测试
# ============================================================================

class TestVarTempPositionRule:
    """SYNTAX_001规则测试"""

    def test_var_temp_in_program_error(self, syntax_checker):
        """测试PROGRAM中使用VAR_TEMP报错"""
        code = """
PROGRAM MainProg
VAR_TEMP
    xTemp : INT;
END_VAR
END_PROGRAM
"""
        violations = syntax_checker.check(code, file_path="test.st")

        var_temp_violations = [
            v for v in violations if v.rule_id == "SYNTAX_001"
        ]
        assert len(var_temp_violations) > 0
        assert any("PROGRAM" in v.message for v in var_temp_violations)
        assert any(v.severity == Severity.ERROR for v in var_temp_violations)

    def test_var_temp_after_other_var_warning(self, syntax_checker):
        """测试VAR_TEMP在VAR之后警告"""
        code = """
FUNCTION_BLOCK MyFB
VAR_INPUT
    xIn : BOOL;
END_VAR
VAR
    xLocal : INT;
END_VAR
VAR_TEMP
    xTemp : REAL;
END_VAR
VAR_OUTPUT
    xOut : BOOL;
END_VAR
END_FUNCTION_BLOCK
"""
        violations = syntax_checker.check(code, file_path="test.st")

        var_temp_violations = [
            v for v in violations if v.rule_id == "SYNTAX_001"
        ]
        # 应该有关于VAR_OUTPUT在VAR_TEMP之后的警告
        assert len(var_temp_violations) >= 1

    def test_valid_var_temp_position(self, syntax_checker):
        """测试正确的VAR_TEMP位置不报错"""
        code = """
FUNCTION_BLOCK MyFB
VAR_INPUT
    xIn : BOOL;
END_VAR
VAR_OUTPUT
    xOut : BOOL;
END_VAR
VAR
    xLocal : INT;
END_VAR
VAR_TEMP
    xTemp : REAL;
END_VAR
END_FUNCTION_BLOCK
"""
        violations = syntax_checker.check(code, file_path="test.st")

        var_temp_violations = [
            v for v in violations if v.rule_id == "SYNTAX_001"
        ]
        # 正确位置不应有错误（可能有顺序建议）
        errors = [v for v in var_temp_violations
                  if v.severity == Severity.ERROR]
        assert len(errors) == 0

    def test_no_var_temp_no_violation(self, syntax_checker):
        """测试没有VAR_TEMP时不触发此规则"""
        code = """
FUNCTION MyFunc
VAR
    xVar : INT;
END_VAR
END_FUNCTION
"""
        violations = syntax_checker.check(code, file_path="test.st")

        var_temp_violations = [
            v for v in violations if v.rule_id == "SYNTAX_001"
        ]
        assert len(var_temp_violations) == 0


# ============================================================================
# 3. SYNTAX_002: 控制结构配对检测测试
# ============================================================================

class TestControlStructureRule:
    """SYNTAX_002规则测试 - 核心栈算法"""

    def test_matched_if_end_if(self, syntax_checker):
        """测试正确配对的IF...END_IF"""
        code = """
IF xCondition THEN
    nResult := 1;
END_IF;
"""
        violations = syntax_checker.check(code, file_path="test.st")

        control_violations = [
            v for v in violations if v.rule_id == "SYNTAX_002"
        ]
        assert len(control_violations) == 0

    def test_unmatched_if(self, syntax_checker):
        """测试未闭合的IF"""
        code = """
IF xCondition THEN
    nResult := 1;
(* 缺少 END_IF *)
"""
        violations = syntax_checker.check(code, file_path="test.st")

        control_violations = [
            v for v in violations if v.rule_id == "SYNTAX_002"
        ]
        assert len(control_violations) > 0
        assert any("未闭合" in v.message or "IF" in v.message
                   for v in control_violations)

    def test_nested_control_structures(self, syntax_checker):
        """测试嵌套控制结构正确处理"""
        code = """
IF xOuter THEN
    IF xInner THEN
        nResult := 1;
    END_IF;
    
    FOR i := 1 TO 10 DO
        nCount := nCount + 1;
    END_FOR;
END_IF;
"""
        violations = syntax_checker.check(code, file_path="test.st")

        control_violations = [
            v for v in violations if v.rule_id == "SYNTAX_002"
        ]
        assert len(control_violations) == 0

    def test_mismatched_structure(self, syntax_checker):
        """测试不匹配的控制结构"""
        code = """
IF xCond THEN
    nResult := 1;
END_FOR;  (* 错误：应该是END_IF *)
"""
        violations = syntax_checker.check(code, file_path="test.st")

        control_violations = [
            v for v in violations if v.rule_id == "SYNTAX_002"
        ]
        assert len(control_violations) > 0
        assert any("不匹配" in v.message for v in control_violations)

    def test_extra_end_keyword(self, syntax_checker):
        """测试多余的结束关键字"""
        code = """
IF xCond THEN
    nResult := 1;
END_IF;
END_IF;  (* 多余的END_IF *)
"""
        violations = syntax_checker.check(code, file_path="test.st")

        control_violations = [
            v for v in violations if v.rule_id == "SYNTAX_002"
        ]
        assert len(control_violations) > 0
        assert any("多余" in v.message for v in control_violations)

    def test_while_loop_matching(self, syntax_checker):
        """测试WHILE循环配对"""
        code = """
WHILE bRunning DO
    nCounter := nCounter + 1;
    IF nCounter > 100 THEN
        EXIT;
    END_IF;
END_WHILE;
"""
        violations = syntax_checker.check(code, file_path="test.st")

        control_violations = [
            v for v in violations if v.rule_id == "SYNTAX_002"
        ]
        assert len(control_violations) == 0

    def test_case_statement_matching(self, syntax_checker):
        """测试CASE语句配对"""
        code = """
CASE nMode OF
    1:
        nResult := 10;
    2:
        nResult := 20;
    ELSE
        nResult := 0;
END_CASE;
"""
        violations = syntax_checker.check(code, file_path="test.st")

        control_violations = [
            v for v in violations if v.rule_id == "SYNTAX_002"
        ]
        assert len(control_violations) == 0

    def test_repeat_until_matching(self, syntax_checker):
        """测试REPEAT循环配对"""
        code = """
REPEAT
    nCounter := nCounter + 1;
UNTIL nCounter >= 100
END_REPEAT;
"""
        violations = syntax_checker.check(code, file_path="test.st")

        control_violations = [
            v for v in violations if v.rule_id == "SYNTAX_002"
        ]
        assert len(control_violations) == 0

    def test_complex_nesting_all_types(self, syntax_checker):
        """测试所有类型的复杂嵌套"""
        code = """
IF xInit THEN
    CASE nState OF
        1:
            FOR i := 1 TO 10 DO
                WHILE bCondition DO
                    (* 嵌套逻辑 *)
                    nVal := nVal + 1;
                END_WHILE;
            END_FOR;
        2:
            REPEAT
                nCnt := nCnt + 1;
            UNTIL nCnt > 50
            END_REPEAT;
    END_CASE;
END_IF;
"""
        violations = syntax_checker.check(code, file_path="test.st")

        control_violations = [
            v for v in violations if v.rule_id == "SYNTAX_002"
        ]
        assert len(control_violations) == 0

    def test_ignore_comments_and_strings(self, syntax_checker):
        """测试忽略注释和字符串中的关键字"""
        code = """
(* 这是一个包含 IF 和 END_IF 的注释文字 *)
sMessage := 'This has IF and END_IF inside string';
IF xReal THEN
    nResult := 1;
END_IF;
"""
        violations = syntax_checker.check(code, file_path="test.st")

        control_violations = [
            v for v in violations if v.rule_id == "SYNTAX_002"
        ]
        assert len(control_violations) == 0


# ============================================================================
# 4. SYNTAX_003: FB结构完整性测试
# ============================================================================

class TestFBStructureRule:
    """SYNTAX_003规则测试"""

    def test_fb_with_complete_vars(self, syntax_checker):
        """测试完整的FB结构不报错"""
        code = """
FUNCTION_BLOCK CompleteFB
VAR_INPUT
    xStart : BOOL;
END_VAR
VAR_OUTPUT
    bRunning : BOOL;
END_VAR
VAR
    nState : INT;
END_VAR
END_FUNCTION_BLOCK
"""
        violations = syntax_checker.check(
            code, file_path="test.st",
            context={"is_function_block": True}
        )

        fb_violations = [
            v for v in violations if v.rule_id == "SYNTAX_003"
        ]
        errors = [v for v in fb_violations if v.severity == Severity.ERROR]
        assert len(errors) == 0

    def test_fb_missing_interface(self, syntax_checker):
        """测试FB缺少接口声明"""
        code = """
FUNCTION_BLOCK IncompleteFB
VAR
    nLocal : INT;
END_VAR
END_FUNCTION_BLOCK
"""
        violations = syntax_checker.check(code, file_path="test.st")

        fb_violations = [
            v for v in violations if v.rule_id == "SYNTAX_003"
        ]
        assert len(fb_violations) > 0
        assert any("接口" in v.message for v in fb_violations)

    def test_non_fb_not_checked(self, syntax_checker):
        """测试非FB类型不执行此检查"""
        code = """
FUNCTION SimpleFunc
VAR
    nResult : INT;
END_VAR
END_FUNCTION
"""
        violations = syntax_checker.check(
            code, file_path="test.st",
            context={"is_function_block": False}
        )

        fb_violations = [
            v for v in violations if v.rule_id == "SYNTAX_003"
        ]
        assert len(fb_violations) == 0


# ============================================================================
# 5. SYNTAX_004: 语句分号检测测试
# ============================================================================

class TestStatementTerminatorRule:
    """SYNTAX_004规则测试"""

    def test_assignment_with_semicolon(self, syntax_checker):
        """测试带分号的赋值语句不报错"""
        code = """
nValue := 100;
nResult := nValue + 1;
bFlag := TRUE;
"""
        violations = syntax_checker.check(code, file_path="test.st")

        semi_violations = [
            v for v in violations if v.rule_id == "SYNTAX_004"
        ]
        assert len(semi_violations) == 0

    def test_assignment_without_semicolon(self, syntax_checker):
        """测试缺少分号的赋值语句"""
        code = """
nValue := 100
nResult := nValue + 1;
"""
        violations = syntax_checker.check(code, file_path="test.st")

        semi_violations = [
            v for v in violations if v.rule_id == "SYNTAX_004"
        ]
        assert len(semi_violations) > 0
        assert any("分号" in v.message for v in semi_violations)

    def test_ignore_control_lines(self, syntax_checker):
        """测试忽略不需要分号的控制行"""
        code = """
IF xCondition THEN
ELSIF xOther THEN
ELSE
END_IF;
FOR i := 1 TO 10 DO
END_FOR;
"""
        violations = syntax_checker.check(code, file_path="test.st")

        semi_violations = [
            v for v in violations if v.rule_id == "SYNTAX_004"
        ]
        assert len(semi_violations) == 0

    def test_ignore_var_declarations(self, syntax_checker):
        """测试忽略变量声明行（使用冒号而非:=）"""
        code = """
VAR
    nValue   : INT;
    bFlag    : BOOL := TRUE;
    rRate    : REAL;
END_VAR
"""
        violations = syntax_checker.check(code, file_path="test.st")

        semi_violations = [
            v for v in violations if v.rule_id == "SYNTAX_004"
        ]
        assert len(semi_violations) == 0


# ============================================================================
# 6. SYNTAX_005: 类型合法性验证测试
# ============================================================================

class TestTypeValidityRule:
    """SYNTAX_005规则测试"""

    def test_standard_iec_types(self, syntax_checker):
        """测试标准IEC类型通过验证"""
        code = """
VAR
    bFlag    : BOOL;
    nCount   : INT;
    rValue   : REAL;
    sMessage : STRING;
    dwData   : DWORD;
END_VAR
"""
        violations = syntax_checker.check(code, file_path="test.st")

        type_violations = [
            v for v in violations if v.rule_id == "SYNTAX_005"
        ]
        assert len(type_violations) == 0

    def test_unknown_type_detection(self, syntax_checker):
        """测试未知类型被检测"""
        code = """
VAR
    myCustomType : UnknownType;
    anotherBad   : InvalidType;
END_VAR
"""
        violations = syntax_checker.check(code, file_path="test.st")

        type_violations = [
            v for v in violations if v.rule_id == "SYNTAX_005"
        ]
        assert len(type_violations) >= 2
        # 使用大小写不敏感的匹配
        assert any("unknowntype" in v.message.lower() for v in type_violations)

    def test_user_defined_types_accepted(self, syntax_checker):
        """测试用户自定义类型被接受"""
        code = """
VAR
    myMotor : MotorType_t;
    sensor  : SensorStruct;
END_VAR
"""
        context = {
            "user_types": ["MotorType_t", "SensorStruct"]
        }
        violations = syntax_checker.check(
            code, file_path="test.st", context=context
        )

        type_violations = [
            v for v in violations if v.rule_id == "SYNTAX_005"
        ]
        assert len(type_violations) == 0

    def test_array_type_validation(self, syntax_checker):
        """测试数组类型的基础类型验证"""
        code = """
VAR
    aValues : ARRAY[1..10] OF INT;
    aBadType : ARRAY[1..5] OF FakeType;
END_VAR
"""
        violations = syntax_checker.check(code, file_path="test.st")

        type_violations = [
            v for v in violations if v.rule_id == "SYNTAX_005"
        ]
        # 应该只有FakeType报错（INT是标准类型）
        assert len(type_violations) == 1
        # 使用大小写不敏感的匹配
        assert "faketype" in type_violations[0].message.lower()


# ============================================================================
# 7. 边界条件和异常处理测试
# ============================================================================

class TestEdgeCasesAndErrorHandling:
    """边界条件和异常处理测试"""

    def test_empty_input(self, syntax_checker):
        """测试空输入不崩溃"""
        violations = syntax_checker.check("", file_path="empty.st")
        assert isinstance(violations, list)
        assert len(violations) == 0

    def test_none_input_handling(self, syntax_checker):
        """测试None输入处理"""
        violations = syntax_checker.check(None, file_path="none.st")
        assert isinstance(violations, list)
        assert len(violations) == 0

    def test_only_whitespace(self, syntax_checker):
        """测试仅空白字符输入"""
        code = "   \n\n\t\n   \n"
        violations = syntax_checker.check(code, file_path="whitespace.st")
        assert isinstance(violations, list)

    def test_single_line_input(self, syntax_checker):
        """测试单行输入"""
        code = "nValue := 100;"
        violations = syntax_checker.check(code, file_path="single.st")
        assert isinstance(violations, list)

    def test_very_long_line(self, syntax_checker):
        """测试超长行处理"""
        long_assignment = "nResult := " + " + ".join(["i"] * 1000) + ";"
        violations = syntax_checker.check(long_assignment, file_path="long.st")
        assert isinstance(violations, list)

    def test_unicode_content(self, syntax_checker):
        """测试Unicode内容处理"""
        code = "(* 中文注释 *)\nnValue := 100;"
        violations = syntax_checker.check(code, file_path="unicode.st")
        assert isinstance(violations, list)


# ============================================================================
# 8. 综合测试 - 完整ST程序
# ============================================================================

class TestComprehensiveScenarios:
    """综合场景测试"""

    def test_complete_function_block(self, syntax_checker):
        """测试完整且正确的FB程序"""
        code = """
FUNCTION_BLOCK FB_ConveyorControl
VAR_INPUT  (* 输入参数 *)
    bStartCmd      : BOOL;   (* 启动命令 *)
    bStopCmd       : BOOL;   (* 停止命令 *)
    bEmergency     : BOOL;   (* 急停信号 *)
    nSpeedSetpoint : INT;    (* 速度设定值 [0-100%] *)
END_VAR

VAR_OUTPUT  (* 输出参数 *)
    bMotorRun      : BOOL;   (* 电机运行输出 *)
    bFault         : BOOL;   (* 故障指示 *)
    nActualSpeed   : INT;    (* 实际速度反馈 *)
END_VAR

VAR  (* 局部变量 *)
    nStateMachine  : INT := 0;  (* 状态机当前状态 *)
    nTimerCounter  : INT := 0;  (* 计时器计数 *)
    bFaultLatched  : BOOL;      (* 故障锁存标志 *)
END_VAR

(* ===== 状态机主逻辑 ===== *)
CASE nStateMachine OF
    0:  (* 停止状态 *)
        IF bStartCmd AND NOT bEmergency THEN
            nStateMachine := 1;
            bMotorRun := TRUE;
        ELSIF bEmergency THEN
            bFaultLatched := TRUE;
            bFault := TRUE;
        END_IF;

    1:  (* 运行状态 *)
        IF bStopCmd OR bEmergency THEN
            nStateMachine := 2;
        ELSE
            (* 速度控制逻辑 *)
            IF nActualSpeed < nSpeedSetpoint THEN
                nActualSpeed := nActualSpeed + 1;
            ELSIF nActualSpeed > nSpeedSetpoint THEN
                nActualSpeed := nActualSpeed - 1;
            END_IF;
        END_IF;

    2:  (* 减速停止状态 *)
        FOR i := 1 TO 20 DO
            IF nActualSpeed > 0 THEN
                nActualSpeed := nActualSpeed - 5;
            END_IF;
        END_FOR;
        
        bMotorRun := FALSE;
        nStateMachine := 0;

    ELSE  (* 未知状态 *)
        nStateMachine := 0;
        bFault := TRUE;
END_CASE;

(* 急停优先处理 *)
IF bEmergency THEN
    bMotorRun := FALSE;
    nStateMachine := 0;
    bFault := TRUE;
END_IF;

END_FUNCTION_BLOCK
"""
        violations = syntax_checker.check(
            code,
            file_path="ConveyorControl.st",
            context={
                "is_function_block": True,
                "user_types": [],
            }
        )

        # 这个完整的程序应该没有ERROR级别的违规
        errors = [v for v in violations if v.severity == Severity.ERROR]
        assert len(errors) == 0, f"发现错误: {[str(e) for e in errors]}"

    def test_multiple_errors_combined(self, syntax_checker):
        """测试同时存在多种错误的代码"""
        code = """
PROGRAM BadProgram
VAR_TEMP
    xTemp : INT;
END_VAR
VAR
    xUnknown : FakeType;
END_VAR

IF bCondition THEN
    xResult := 100
    FOR i := 1 TO 10 DO
        (* 未闭合的FOR *)
END_PROGRAM
"""
        violations = syntax_checker.check(code, file_path="bad.st")

        # 应该有多种类型的违规
        rule_ids = set(v.rule_id for v in violations)
        assert "SYNTAX_001" in rule_ids  # VAR_TEMP in PROGRAM
        assert "SYNTAX_002" in rule_ids  # Unmatched structures
        assert "SYNTAX_004" in rule_ids  # Missing semicolon
        assert "SYNTAX_005" in rule_ids  # Unknown type


# ============================================================================
# 9. 单独规则检查器类测试
# ============================================================================

class TestIndividualCheckerClasses:
    """单独规则检查器类测试"""

    def test_var_temp_position_checker(self):
        """测试单独的VAR_TEMP检查器"""
        checker = VarTempPositionChecker()
        code = """
PROGRAM P
VAR_TEMP
    x : INT;
END_VAR
END_PROGRAM
"""
        violations = checker.check(code, file_path="test.st")
        assert len(violations) > 0
        assert all(v.rule_id == "SYNTAX_001" for v in violations)

    def test_control_structure_checker(self):
        """测试单独的控制结构检查器"""
        checker = ControlStructureChecker()
        code = "IF x THEN\n    y := 1;\n"
        violations = checker.check(code, file_path="test.st")
        assert len(violations) > 0
        assert all(v.rule_id == "SYNTAX_002" for v in violations)

    def test_fb_structure_checker(self):
        """测试单独的FB结构检查器"""
        checker = FBStructureChecker()
        code = """
FUNCTION_BLOCK F
VAR
    x : INT;
END_VAR
END_FUNCTION_BLOCK
"""
        violations = checker.check(code, file_path="test.st")
        assert len(violations) > 0
        assert all(v.rule_id == "SYNTAX_003" for v in violations)

    def test_statement_terminator_checker(self):
        """测试单独的分号检查器"""
        checker = StatementTerminatorChecker()
        code = "x := 100\ny := 200;"
        violations = checker.check(code, file_path="test.st")
        assert len(violations) > 0
        assert all(v.rule_id == "SYNTAX_004" for v in violations)

    def test_type_validity_checker(self):
        """测试单独的类型有效性检查器"""
        checker = TypeValidityChecker()
        code = "VAR\n    x : FakeType;\nEND_VAR"
        violations = checker.check(code, file_path="test.st")
        assert len(violations) > 0
        assert all(v.rule_id == "SYNTAX_005" for v in violations)


# ============================================================================
# 主入口
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
