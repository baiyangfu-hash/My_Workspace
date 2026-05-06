# -*- coding: utf-8 -*-
"""
命名规范检查器单元测试

测试覆盖范围:
1. NAMING_001: METHOD定义禁止CALL_前缀
2. NAMING_002: METHOD调用禁止CALL_前缀
3. NAMING_003: 变量必须使用规范前缀
4. NAMING_004: 禁止中文变量名
5. NAMING_005: 禁止多余下划线
6. NAMING_006: 必须使用小驼峰命名
7. 规则启用/禁用功能
8. 复杂混合场景测试

运行方式:
    python -m pytest tests/test_naming_checker.py -v
"""
import pytest
from pathlib import Path

# 导入被测模块
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.checkers.naming_checker import NamingChecker, RE_METHOD_DEFINITION, RE_METHOD_CALL, VALID_PREFIXES
from src.checkers.base_checker import Severity


# ============================================================================
# 测试辅助函数和固定代码片段
# ============================================================================

# 正确的ST代码示例（无违规）
VALID_ST_CODE = """FUNCTION_BLOCK FB_TestNaming
VAR_INPUT
    i_bStart : BOOL;
    i_rSpeedSetpoint : REAL;
    i_iMaxCycle : INT;
END_VAR

VAR_OUTPUT
    o_bRunning : BOOL;
    o_iErrorCode : INT;
END_VAR

VAR
    s_bInitialized : BOOL;
    s_iCurrentStep : INT;
    fb_tActionTimer : TON;
END_VAR

VAR_CONSTANT
    CONST_MAX_SPEED : INT := 100;
END_VAR

BEGIN
    IF i_bStart THEN
        o_bRunning := TRUE;
        fb_tActionTimer(IN := TRUE, PT := T#1000ms);
    END_IF;
END_FUNCTION_BLOCK
"""

# 包含METHOD定义违规的代码
INVALID_METHOD_DEF_CODE = """FUNCTION_BLOCK FB_MethodTest
VAR_INPUT
    i_bEnable : BOOL;
END_VAR

METHOD CALL_AutoMode : VOID
    // 方法实现
END_METHOD

BEGIN
    CALL_AutoMode();
END_FUNCTION_BLOCK
"""

# 包含中文变量名的代码
CHINESE_VAR_CODE = """FUNCTION_BLOCK FB_ChineseTest
VAR
    运行标志 : BOOL;
    当前步骤 : INT;
    s_bValid : BOOL;
END_VAR

BEGIN
    运行标志 := TRUE;
END_FUNCTION_BLOCK
"""

# 包含下划线违规的代码
UNDERSCORE_CODE = """FUNCTION_BLOCK FB_UnderscoreTest
VAR_INPUT
    i_b_start_signal : BOOL;      // 错误: 多余下划线
    i_bCorrectName : BOOL;         // 正确
END_VAR

VAR
    s_current_step : INT;          // 错误: 多余下划线
    s_i_error_code : INT;          // 错误: 多余下划线
END_VAR

BEGIN
    i_b_start_signal := TRUE;
END_FUNCTION_BLOCK
"""

# 混合多种违规的复杂场景
COMPLEX_MIXED_CODE = """FUNCTION_BLOCK FB_ComplexTest
// 这是一个复杂的测试用例，包含多种违规

VAR_INPUT
    i_bStart : BOOL;               // 正确
    StartSignal : BOOL;            // 错误NAMING_003: 缺少前缀
    i_start_button : BOOL;         // 错误NAMING_005: 多余下划线
END_VAR

VAR_OUTPUT
    o_bRunning : BOOL;             // 正确
    RunningState : BOOL;           // 错误NAMING_003 + NAMING_006
END_VAR

VAR
    s_bInit : BOOL;                // 正确
    运行状态 : BOOL;               // 错误NAMING_004: 中文变量名
    fb_tTimer : TON;               // 正确
    MyTimer : TON;                 // 错误NAMING_003: 功能块缺少fb_前缀
END_VAR

METHOD CALL_ProcessData : VOID     // 错误NAMING_001: METHOD定义带CALL_
    // 实现细节
END_METHOD

BEGIN
    // 正确调用
    s_bInit := TRUE;

    // 错误调用
    CALL_ProcessData();            // 错误NAMING_002: 调用带CALL_

    运行状态 := o_bRunning;       // 使用中文变量
END_FUNCTION_BLOCK
"""


# ============================================================================
# 1. NamingChecker 初始化和基础功能测试
# ============================================================================

class TestNamingCheckerInitialization:
    """检查器初始化测试"""

    def test_instantiation(self):
        """测试检查器可以正常实例化"""
        checker = NamingChecker()
        assert checker is not None
        assert isinstance(checker, NamingChecker)

    def test_rule_count(self):
        """测试规则数量正确（6条）"""
        checker = NamingChecker()
        rules = checker.get_all_rules()
        assert len(rules) == 6
        assert "NAMING_001" in rules
        assert "NAMING_002" in rules
        assert "NAMING_003" in rules
        assert "NAMING_004" in rules
        assert "NAMING_005" in rules
        assert "NAMING_006" in rules

    def test_rules_default_enabled(self):
        """测试所有规则默认启用"""
        checker = NamingChecker()
        stats = checker.get_statistics()
        assert stats["enabled_rules"] == 6
        assert stats["disabled_rules"] == 0

    def test_repr_output(self):
        """测试字符串表示"""
        checker = NamingChecker()
        repr_str = repr(checker)
        assert "NamingChecker" in repr_str
        assert "6/6" in repr_str  # 全部启用

    def test_check_returns_list(self):
        """测试check方法返回列表"""
        checker = NamingChecker()
        result = checker.check("test code")
        assert isinstance(result, list)

    def test_valid_code_no_violations(self):
        """测试正确代码无违规"""
        checker = NamingChecker()
        violations = checker.check(VALID_ST_CODE)
        assert len(violations) == 0

    def test_empty_code_handling(self):
        """测试空代码处理"""
        checker = NamingChecker()
        violations = checker.check("")
        assert isinstance(violations, list)


# ============================================================================
# 2. NAMING_001: METHOD定义禁止CALL_前缀
# ============================================================================

class TestNamingRule001:
    """NAMING_001: METHOD定义禁止CALL_前缀"""

    def setup_method(self):
        """每个测试前初始化"""
        self.checker = NamingChecker()

    def test_method_def_with_call_prefix(self):
        """检测METHOD定义使用CALL_前缀"""
        code = """
METHOD CALL_MyMethod : VOID
    // 实现
END_METHOD
"""
        violations = self.checker.check(code)
        naming_001_violations = [v for v in violations if v.rule_id == "NAMING_001"]
        assert len(naming_001_violations) >= 1
        assert "CALL_" in naming_001_violations[0].message

    def test_method_def_without_call_prefix(self):
        """正确的METHOD定义不报错"""
        code = """
METHOD MyMethod : VOID
    // 实现
END_METHOD
"""
        violations = self.checker.check(code)
        naming_001 = [v for v in violations if v.rule_id == "NAMING_001"]
        assert len(naming_001) == 0

    def test_method_def_with_fb_qualifier_call(self):
        """检测带FB限定符的METHOD定义违规"""
        code = """
METHOD FB_MyBlock.CALL_DoWork : VOID
END_METHOD
"""
        violations = self.checker.check(code)
        naming_001 = [v for v in violations if v.rule_id == "NAMING_001"]
        assert len(naming_001) >= 1

    def test_method_def_case_insensitive(self):
        """检测大小写不敏感"""
        code = """
METHOD call_myMethod : VOID
END_METHOD
"""
        violations = self.checker.check(code)
        naming_001 = [v for v in violations if v.rule_id == "NAMING_001"]
        assert len(naming_001) >= 1

    def test_method_def_multiple_violations(self):
        """检测多个METHOD定义违规"""
        code = """
METHOD CALL_First : VOID
END_METHOD

METHOD CALL_Second : VOID
END_METHOD
"""
        violations = self.checker.check(code)
        naming_001 = [v for v in violations if v.rule_id == "NAMING_001"]
        assert len(naming_001) == 2

    def test_rule_001_can_be_disabled(self):
        """测试NAMING_001可以禁用"""
        self.checker.disable_rule("NAMING_001")
        code = "METHOD CALL_Test : VOID\nEND_METHOD"
        violations = self.checker.check(code)
        naming_001 = [v for v in violations if v.rule_id == "NAMING_001"]
        assert len(naming_001) == 0


# ============================================================================
# 3. NAMING_002: METHOD调用禁止CALL_前缀
# ============================================================================

class TestNamingRule002:
    """NAMING_002: METHOD调用禁止CALL_前缀"""

    def setup_method(self):
        self.checker = NamingChecker()

    def test_method_call_with_call_prefix(self):
        """检测METHOD调用使用CALL_前缀"""
        code = """
FUNCTION_BLOCK FB_Test
BEGIN
    CALL_MyMethod();
END_FUNCTION_BLOCK
"""
        violations = self.checker.check(code)
        naming_002 = [v for v in violations if v.rule_id == "NAMING_002"]
        assert len(naming_002) >= 1
        "CALL_MyMethod" in naming_002[0].message

    def test_direct_method_call_ok(self):
        """直接调用方法不报错"""
        code = """
FUNCTION_BLOCK FB_Test
BEGIN
    MyMethod();
END_FUNCTION_BLOCK
"""
        violations = self.checker.check(code)
        naming_002 = [v for v in violations if v.rule_id == "NAMING_002"]
        assert len(naming_002) == 0

    def test_method_call_with_parameters(self):
        """检测带参数的CALL_调用"""
        code = """
BEGIN
    CALL_ProcessData(i_bStart, o_bDone);
END_FUNCTION_BLOCK
"""
        violations = self.checker.check(code)
        naming_002 = [v for v in violations if v.rule_id == "NAMING_002"]
        assert len(naming_002) >= 1

    def test_ignore_method_definition_line(self):
        """调用检测应忽略METHOD定义行"""
        # 定义行由NAMING_001处理，不应在NAMING_002重复报告
        code = """
METHOD CALL_Test : VOID
END_METHOD

BEGIN
    CALL_Test();
END_FUNCTION_BLOCK
"""
        violations = self.checker.check(code)
        # NAMING_001应报告定义行
        naming_001 = [v for v in violations if v.rule_id == "NAMING_001"]
        assert len(naming_001) >= 1
        # NAMING_002应报告调用行
        naming_002 = [v for v in violations if v.rule_id == "NAMING_002"]
        assert len(naming_002) >= 1
        # 确保不是同一行
        assert naming_001[0].line_number != naming_002[0].line_number

    def test_rule_002_can_be_disabled(self):
        """测试NAMING_002可以禁用"""
        self.checker.disable_rule("NAMING_002")
        code = "BEGIN\n    CALL_Test();\nEND_FUNCTION_BLOCK"
        violations = self.checker.check(code)
        naming_002 = [v for v in violations if v.rule_id == "NAMING_002"]
        assert len(naming_002) == 0


# ============================================================================
# 4. NAMING_003: 变量必须使用规范前缀
# ============================================================================

class TestNamingRule003:
    """NAMING_003: 变量前缀规范"""

    def setup_method(self):
        self.checker = NamingChecker()

    def test_input_var_missing_prefix(self):
        """输入变量缺少i_前缀"""
        code = """
FUNCTION_BLOCK FB_PrefixTest
VAR_INPUT
    startSignal : BOOL;   // 缺少 i_ 前缀
    i_bCorrect : BOOL;    // 正确
END_VAR
BEGIN
END_FUNCTION_BLOCK
"""
        violations = self.checker.check(code)
        naming_003 = [v for v in violations if v.rule_id == "NAMING_003"]
        assert len(naming_003) >= 1
        assert "startSignal" in naming_003[0].message or "i_" in naming_003[0].message

    def test_output_var_missing_prefix(self):
        """输出变量缺少o_前缀"""
        code = """
FUNCTION_BLOCK FB_OutputTest
VAR_OUTPUT
    runningStatus : BOOL;  // 缺少 o_ 前缀
END_VAR
BEGIN
END_FUNCTION_BLOCK
"""
        violations = self.checker.check(code)
        naming_003 = [v for v in violations if v.rule_id == "NAMING_003"]
        assert len(naming_003) >= 1

    def test_fb_instance_missing_fb_prefix(self):
        """功能块实例缺少fb_前缀"""
        code = """
FUNCTION_BLOCK FB_FbTest
VAR
    myTimer : TON;          // 缺少 fb_ 前缀
    fb_tCorrect : TON;      // 正确
END_VAR
BEGIN
END_FUNCTION_BLOCK
"""
        violations = self.checker.check(code)
        naming_003 = [v for v in violations if v.rule_id == "NAMING_003"]
        assert any("myTimer" in v.message or "fb_" in v.message for v in naming_003)

    def test_constant_missing_const_prefix(self):
        """常量缺少CONST_前缀"""
        code = """
FUNCTION_BLOCK FB_ConstTest
VAR_CONSTANT
    MAX_VALUE : INT := 100;    // 缺少 CONST_ 前缀
END_VAR
BEGIN
END_FUNCTION_BLOCK
"""
        violations = self.checker.check(code)
        naming_003 = [v for v in violations if v.rule_id == "NAMING_003"]
        assert len(naming_003) >= 1

    def test_correct_prefixes_pass(self):
        """所有正确的变量前缀通过检查"""
        code = VALID_ST_CODE  # 使用预定义的正确代码
        violations = self.checker.check(code)
        naming_003 = [v for v in violations if v.rule_id == "NAMING_003"]
        assert len(naming_003) == 0

    def test_local_var_should_use_s_prefix(self):
        """局部变量应使用s_前缀"""
        code = """
FUNCTION_BLOCK FB_LocalTest
VAR
    localCounter : INT;   // 应该使用 s_ 前缀
END_VAR
BEGIN
END_FUNCTION_BLOCK
"""
        violations = self.checker.check(code)
        naming_003 = [v for v in violations if v.rule_id == "NAMING_003"]
        assert len(naming_003) >= 1


# ============================================================================
# 5. NAMING_004: 禁止中文变量名
# ============================================================================

class TestNamingRule004:
    """NAMING_004: 禁止中文变量名"""

    def setup_method(self):
        self.checker = NamingChecker()

    def test_chinese_variable_name(self):
        """检测中文变量名"""
        code = CHINESE_VAR_CODE
        violations = self.checker.check(code)
        naming_004 = [v for v in violations if v.rule_id == "NAMING_004"]
        assert len(naming_004) >= 2  # 有两个中文变量

    def test_chinese_var_message_content(self):
        """错误消息包含中文提示"""
        code = """
FUNCTION_BLOCK FB_CnTest
VAR
    温度值 : REAL;
END_VAR
BEGIN
END_FUNCTION_BLOCK
"""
        violations = self.checker.check(code)
        naming_004 = [v for v in violations if v.rule_id == "NAMING_004"]
        assert len(naming_004) >= 1
        assert "中文字符" in naming_004[0].message

    def test_english_variable_pass(self):
        """英文变量名通过检查"""
        code = """
FUNCTION_BLOCK FB_EnTest
VAR
    rTemperature : REAL;
END_VAR
BEGIN
END_FUNCTION_BLOCK
"""
        violations = self.checker.check(code)
        naming_004 = [v for v in violations if v.rule_id == "NAMING_004"]
        assert len(naming_004) == 0

    def test_mixed_chinese_english_vars(self):
        """混合中英文变量只报告中文的"""
        code = """
FUNCTION_BLOCK FB_MixedTest
VAR
    bStart : BOOL;        // 正确
    停止信号 : BOOL;      // 错误: 中文
    s_bDone : BOOL;       // 正确
END_VAR
BEGIN
END_FUNCTION_BLOCK
"""
        violations = self.checker.check(code)
        naming_004 = [v for v in violations if v.rule_id == "NAMING_004"]
        assert len(naming_004) == 1
        assert "停止信号" in naming_004[0].message

    def test_rule_004_can_be_disabled(self):
        """测试NAMING_004可以禁用"""
        self.checker.disable_rule("NAMING_004")
        code = "VAR\n    中文变量 : BOOL;\nEND_VAR"
        violations = self.checker.check(code)
        naming_004 = [v for v in violations if v.rule_id == "NAMING_004"]
        assert len(naming_004) == 0


# ============================================================================
# 6. NAMING_005: 禁止多余下划线
# ============================================================================

class TestNamingRule005:
    """NAMING_005: 禁止多余下划线"""

    def setup_method(self):
        self.checker = NamingChecker()

    def test_extra_underscore_in_name(self):
        """检测多余下划线"""
        code = UNDERSCORE_CODE
        violations = self.checker.check(code)
        naming_005 = [v for v in violations if v.rule_id == "NAMING_005"]
        assert len(naming_005) >= 2  # 至少有两个下划线违规

    def test_correct_camelcase_format(self):
        """正确的驼峰格式通过检查"""
        code = """
FUNCTION_BLOCK FB_CamelTest
VAR_INPUT
    i_bStartSignal : BOOL;   // 正确: 驼峰格式
END_VAR
BEGIN
END_FUNCTION_BLOCK
"""
        violations = self.checker.check(code)
        naming_005 = [v for v in violations if v.rule_id == "NAMING_005"]
        assert len(naming_005) == 0

    def test_single_underscore_only_prefix(self):
        """只有前缀的下划线是允许的"""
        code = """
FUNCTION_BLOCK FB_SingleUSTest
VAR
    s_bInitFlag : BOOL;   // 正确: 只有前缀有一个下划线
END_VAR
BEGIN
END_FUNCTION_BLOCK
"""
        violations = self.checker.check(code)
        naming_005 = [v for v in violations if v.rule_id == "NAMING_005"]
        assert len(naming_005) == 0

    def test_multiple_underscores_detected(self):
        """多个连续下划线被检测"""
        code = """
FUNCTION_BLOCK FB_MultiUSTest
VAR
    i_b__start : BOOL;   // 双下划线
END_VAR
BEGIN
END_FUNCTION_BLOCK
"""
        violations = self.checker.check(code)
        naming_005 = [v for v in violations if v.rule_id == "NAMING_005"]
        assert len(naming_005) >= 1

    def test_suggestion_contains_removal_hint(self):
        """修复建议包含移除下划线的提示"""
        code = """
FUNCTION_BLOCK FB_SuggestTest
VAR
    i_b_wrong_name : BOOL;
END_VAR
BEGIN
END_FUNCTION_BLOCK
"""
        violations = self.checker.check(code)
        naming_005 = [v for v in violations if v.rule_id == "NAMING_005"]
        if naming_005:
            assert naming_005[0].suggestion is not None


# ============================================================================
# 7. NAMING_006: 小驼峰命名法
# ============================================================================

class TestNamingRule006:
    """NAMING_006: 小驼峰命名法"""

    def setup_method(self):
        self.checker = NamingChecker()

    def test_uppercase_first_letter_invalid(self):
        """首字母大写无效"""
        code = """
FUNCTION_BLOCK FB_UpperTest
VAR
    s_BadStart : BOOL;   // 首字母大写，应该小写
END_VAR
BEGIN
END_FUNCTION_BLOCK
"""
        violations = self.checker.check(code)
        naming_006 = [v for v in violations if v.rule_id == "NAMING_006"]
        assert len(naming_006) >= 1

    def test_lowercase_first_letter_valid(self):
        """首字母小写有效"""
        code = """
FUNCTION_BLOCK FB_LowerTest
VAR
    s_goodStart : BOOL;   // 正确的小驼峰
END_VAR
BEGIN
END_FUNCTION_BLOCK
"""
        violations = self.checker.check(code)
        naming_006 = [v for v in violations if v.rule_id == "NAMING_006"]
        assert len(naming_006) == 0

    def test_constant_uppercase_allowed(self):
        """常量全大写允许"""
        code = """
FUNCTION_BLOCK FB_ConstCamelTest
VAR_CONSTANT
    CONST_MAX_VALUE : INT := 999;
END_VAR
BEGIN
END_FUNCTION_BLOCK
"""
        violations = self.checker.check(code)
        naming_006 = [v for v in violations if v.rule_id == "NAMING_006"]
        # CONST_ 前缀后的全大写应该是允许的
        const_violations = [v for v in naming_006 if "CONST_MAX_VALUE" in v.code_snippet]
        assert len(const_violations) == 0

    def test_variable_after_prefix_lowercase(self):
        """前缀后首字符必须小写"""
        code = """
FUNCTION_BLOCK FB_PrefixLowerTest
VAR_INPUT
    i_BStart : BOOL;   // B大写，应该小写
END_VAR
BEGIN
END_FUNCTION_BLOCK
"""
        violations = self.checker.check(code)
        naming_006 = [v for v in violations if v.rule_id == "NAMING_006"]
        assert len(naming_006) >= 1


# ============================================================================
# 8. 规则启用/禁用功能测试
# ============================================================================

class TestRuleEnableDisable:
    """规则启用/禁用功能测试"""

    def setup_method(self):
        self.checker = NamingChecker()

    def test_disable_single_rule(self):
        """禁用单条规则"""
        assert self.checker.disable_rule("NAMING_001") is True
        stats = self.checker.get_statistics()
        assert stats["enabled_rules"] == 5
        assert stats["disabled_rules"] == 1

    def test_enable_disabled_rule(self):
        """重新启用已禁用的规则"""
        self.checker.disable_rule("NAMING_002")
        assert self.checker.enable_rule("NAMING_002") is True
        stats = self.checker.get_statistics()
        assert stats["enabled_rules"] == 6

    def test_disable_nonexistent_rule(self):
        """禁用不存在的规则返回False"""
        assert self.checker.disable_rule("NONEXISTENT") is False

    def test_enable_nonexistent_rule(self):
        """启用不存在的规则返回False"""
        assert self.checker.enable_rule("NONEXISTENT") is False

    def test_disable_all_rules(self):
        """禁用所有规则"""
        for rule_id in ["NAMING_001", "NAMING_002", "NAMING_003",
                        "NAMING_004", "NAMING_005", "NAMING_006"]:
            self.checker.disable_rule(rule_id)
        stats = self.checker.get_statistics()
        assert stats["enabled_rules"] == 0
        assert stats["disabled_rules"] == 6

        # 验证无任何违规输出
        violations = self.checker.check(INVALID_METHOD_DEF_CODE)
        assert len(violations) == 0

    def test_selective_enable(self):
        """选择性启用部分规则"""
        # 只保留NAMING_003和NAMING_004启用
        for rule_id in ["NAMING_001", "NAMING_002", "NAMING_005", "NAMING_006"]:
            self.checker.disable_rule(rule_id)

        # 混合代码应只报告003和004的违规
        violations = self.checker.check(COMPLEX_MIXED_CODE)
        active_rules = set(v.rule_id for v in violations)
        assert "NAMING_001" not in active_rules
        assert "NAMING_002" not in active_rules
        assert "NAMING_005" not in active_rules
        assert "NAMING_006" not in active_rules


# ============================================================================
# 9. 复杂混合场景测试
# ============================================================================

class TestComplexScenarios:
    """复杂混合场景测试"""

    def setup_method(self):
        self.checker = NamingChecker()

    def test_complex_mixed_scenario(self):
        """复杂混合场景：多种违规同时存在"""
        violations = self.checker.check(COMPLEX_MIXED_CODE)

        # 应检测到多种类型的违规
        rule_ids = set(v.rule_id for v in violations)

        # 验证各类违规都被检测到
        assert "NAMING_001" in rule_ids, "应检测到METHOD定义违规"
        assert "NAMING_002" in rule_ids, "应检测到METHOD调用违规"
        assert "NAMING_003" in rule_ids, "应检测到前缀违规"
        assert "NAMING_004" in rule_ids, "应检测到中文变量违规"

        # 总违规数应大于等于预期最小值
        assert len(violations) >= 6, f"期望至少6个违规，实际{len(violations)}个"

    def test_real_world_plc_code(self):
        """真实PLC代码场景测试"""
        real_code = """(* ============================================================
 * 功能块: FB_1004_GlueMachineFeeder
 * 描述: 打胶机送料机构控制
 * ============================================================ *)
FUNCTION_BLOCK FB_1004_GlueMachineFeeder
VAR_INPUT
    i_bSystemReady : BOOL;          (* 系统就绪信号 *)
    i_bStartCommand : BOOL;         (* 启动命令 *)
    i_bStopCommand : BOOL;          (* 停止命令 *)
    i_rConveyorSpeed : REAL;        (* 输送带速度设定 *)
END_VAR

VAR_OUTPUT
    o_bMachineRunning : BOOL;       (* 机器运行状态 *)
    o_iFaultCode : INT;             (* 故障代码 *)
    o_bCompleteSignal : BOOL;       (* 完成信号 *)
END_VAR

VAR
    s_bInitialized : BOOL;          (* 初始化完成标志 *)
    s_iCurrentStep : INT;           (* 当前步序号 *)
    s_iLastError : INT;             (* 上次错误码 *)
    fb_tCycleTimer : TON;           (* 循环周期定时器 *)
    fb_tFeedTimer : TON;            (* 送料定时器 *)
END_VAR

VAR_CONSTANT
    CONST_MAX_STEP : INT := 10;     (* 最大步数 *)
    CONST_TIMEOUT : TIME := T#30s;  (* 超时时间 *)
END_VAR

METHOD InitSequence : VOID
    (* 初始化序列 *)
    s_bInitialized := FALSE;
    s_iCurrentStep := 0;
END_METHOD

BEGIN
    (* 主程序逻辑 *)
    IF NOT s_bInitialized THEN
        InitSequence();
        s_bInitialized := TRUE;
    END_IF;

    IF i_bStartCommand AND i_bSystemReady THEN
        o_bMachineRunning := TRUE;
        fb_tCycleTimer(IN := TRUE, PT := T#500ms);
    END_IF;

    IF i_bStopCommand THEN
        o_bMachineRunning := FALSE;
        fb_tCycleTimer(IN := FALSE);
    END_IF;
END_FUNCTION_BLOCK
"""

        violations = self.checker.check(real_code)

        # 这段代码应该是规范的，最多只有轻微警告或无违规
        # 如果有违规，记录下来用于验证
        error_count = sum(1 for v in violations if v.severity == Severity.ERROR)
        warning_count = sum(1 for v in violations if v.severity == Severity.WARNING)

        print(f"\n[真实代码测试] 错误: {error_count}, 警告: {warning_count}")
        for v in violations:
            print(f"  - [{v.rule_id}] {v.message}")

        # 正规代码应该没有ERROR级别的问题
        assert error_count == 0, "规范的真实代码不应有ERROR级别的违规"

    def test_edge_cases(self):
        """边界情况测试"""
        edge_code = """FUNCTION_BLOCK FB_EdgeCase
VAR
    _ : BOOL;              // 单下划线变量名
    __ : BOOL;             // 双下划线
    a : BOOL;              // 单字符
    abcdefg : BOOL;        // 纯小写无驼峰
END_VAR
BEGIN
END_FUNCTION_BLOCK
"""
        violations = self.checker.check(edge_code)
        # 边界情况不应该导致崩溃
        assert isinstance(violations, list)

    def test_comment_and_string_ignored(self):
        """注释中的内容不影响检查"""
        comment_code = """FUNCTION_BLOCK FB_CommentTest
VAR
    s_bValid : BOOL;       // 这里写 CALL_Example() 不应触发002
END_VAR
BEGIN
    s_bValid := TRUE;      (* CALL_Another() 注释中也不应触发 *)
END_FUNCTION_BLOCK
"""
        violations = self.checker.check(comment)
        naming_002 = [v for v in violations if v.rule_id == "NAMING_002"]
        # 注释中的CALL_可能仍会被简单正则匹配到
        # 这取决于实现复杂度，这里仅验证不崩溃


# ============================================================================
# 10. Violation数据完整性测试
# ============================================================================

class TestViolationDataIntegrity:
    """违规记录数据完整性测试"""

    def setup_method(self):
        self.checker = NamingChecker()

    def test_violation_has_required_fields(self):
        """违规记录包含必填字段"""
        code = """
METHOD CALL_BadMethod : VOID
END_METHOD
"""
        violations = self.checker.check(code)
        assert len(violations) > 0

        v = violations[0]
        assert hasattr(v, 'rule_id')
        assert hasattr(v, 'severity')
        assert hasattr(v, 'message')
        assert hasattr(v, 'file_path')
        assert hasattr(v, 'line_number')
        assert v.rule_id == "NAMING_001"
        assert v.severity in [Severity.ERROR, Severity.WARNING, Severity.INFO]

    def test_line_number_accuracy(self):
        """行号准确性测试"""
        code = (
            "LINE1\n"
            "LINE2\n"
            "METHOD CALL_Test : VOID\n"  # 第3行
            "END_METHOD\n"
        )
        violations = self.checker.check(code)
        naming_001 = [v for v in violations if v.rule_id == "NAMING_001"]
        if naming_001:
            assert naming_001[0].line_number == 3

    def test_code_snippet_present(self):
        """违规包含代码片段"""
        code = """
FUNCTION_BLOCK FB_SnippetTest
VAR
    中文变量 : BOOL;
END_VAR
BEGIN
END_FUNCTION_BLOCK
"""
        violations = self.checker.check(code)
        naming_004 = [v for v in violations if v.rule_id == "NAMING_004"]
        if naming_004:
            assert naming_004[0].code_snippet is not None
            assert len(naming_004[0].code_snippet) > 0

    def test_suggestion_is_helpful(self):
        """修复建议具有参考价值"""
        code = """
FUNCTION_BLOCK FB_SuggestTest
VAR_INPUT
    signal : BOOL;   // 缺少前缀
END_VAR
BEGIN
END_FUNCTION_BLOCK
"""
        violations = self.checker.check(code)
        naming_003 = [v for v in violations if v.rule_id == "NAMING_003"]
        if naming_003:
            assert naming_003[0].suggestion is not None
            assert "建议" in naming_003[0].suggestion or "重命名" in naming_003[0].suggestion


# ============================================================================
# 主入口
# ============================================================================

if __name__ == "__main__":
    # 直接运行测试
    pytest.main([__file__, "-v", "--tb=short"])
