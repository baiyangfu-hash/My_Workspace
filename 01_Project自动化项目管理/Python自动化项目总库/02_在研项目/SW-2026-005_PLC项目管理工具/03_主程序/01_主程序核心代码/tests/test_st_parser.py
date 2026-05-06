# -*- coding: utf-8 -*-
"""
ST解析器单元测试

测试STParser类的核心功能：
- POU提取
- 变量声明解析
- 全局变量识别
- 边界条件处理
"""
import pytest
from src.parsers.st_parser import (
    STParser,
    POUType,
    VarCategory,
    VariableInfo,
    POUInfo,
)


@pytest.fixture
def sample_st_code() -> str:
    """示例ST代码测试数据"""
    return """
(* ============================================ *)
(* Test Program                                   *)
(* ============================================ *)

PROGRAM PLC_PRG
VAR
    bStart      : BOOL := FALSE;
    nCounter    : INT := 0;
END_VAR

(* 主逻辑 *)
IF bStart THEN
    nCounter := nCounter + 1;
END_IF;

END_PROGRAM


(* ============================================ *)
(* Function Block Example                         *)
(* ============================================ *)

FUNCTION_BLOCK FB_Motor
VAR_INPUT
    bEnable     : BOOL;
    rSpeedRef   : REAL;
END_VAR

VAR_OUTPUT
    bRunning    : BOOL;
    rActualSpeed : REAL;
END_VAR

VAR
    fbState     : INT := 0;
END_VAR

CASE fbState OF
    0:
        bRunning := FALSE;
        IF bEnable THEN
            fbState := 1;
        END_IF;
    1:
        bRunning := TRUE;
        rActualSpeed := rSpeedRef;
        IF NOT bEnable THEN
            fbState := 0;
        END_IF;
END_CASE;

END_FUNCTION_BLOCK


(* ============================================ *)
(* Global Variables                               *)
(* ============================================ *)

VAR_GLOBAL
    g_bSystemReady : BOOL;       (* 系统就绪标志 *)
    g_rTemperature : REAL;       (* 全局温度值 *)
    g_nErrorCode   : INT := 0;   (* 错误代码 *)
END_VAR
"""


class TestSTParserInitialization:
    """STParser初始化测试"""

    def test_parser_creation(self):
        """测试解析器正常创建"""
        parser = STParser()
        assert parser is not None
        assert parser.pous == []
        assert parser.global_variables == []


class TestPOUExtraction:
    """POU提取功能测试"""

    def test_extract_program(self, sample_st_code):
        """测试PROGRAM提取"""
        parser = STParser()
        pous, _ = parser.parse(sample_st_code)

        program_pou = [p for p in pous if p.pou_type == POUType.PROGRAM]
        assert len(program_pou) >= 1
        assert program_pou[0].name == "PLC_PRG"

    def test_extract_function_block(self, sample_st_code):
        """测试FUNCTION_BLOCK提取"""
        parser = STParser()
        pous, _ = parser.parse(sample_st_code)

        fb_pou = [p for p in pous if p.pou_type == POUType.FUNCTION_BLOCK]
        assert len(fb_pou) >= 1
        assert fb_pou[0].name == "FB_Motor"

    def test_pou_count(self, sample_st_code):
        """测试POU总数正确性"""
        parser = STParser()
        pous, _ = parser.parse(sample_st_code)

        assert len(pous) == 2  # 1 PROGRAM + 1 FUNCTION_BLOCK


class TestVariableParsing:
    """变量声明解析测试"""

    def test_parse_local_variables(self, sample_st_code):
        """测试局部变量解析"""
        parser = STParser()
        pous, _ = parser.parse(sample_st_code)

        program = parser.get_pou_by_name("PLC_PRG")
        assert program is not None
        assert len(program.variables) >= 2

        var_names = [v.name for v in program.variables]
        assert "bStart" in var_names
        assert "nCounter" in var_names

    def test_parse_input_variables(self, sample_st_code):
        """测试输入变量(VAR_INPUT)解析"""
        parser = STParser()
        pous, _ = parser.parse(sample_st_code)

        motor_fb = parser.get_pou_by_name("FB_Motor")
        assert motor_fb is not None

        input_vars = [
            v for v in motor_fb.variables
            if v.category == VarCategory.VAR_INPUT
        ]
        assert len(input_vars) >= 2

        input_names = [v.name for v in input_vars]
        assert "bEnable" in input_names
        assert "rSpeedRef" in input_names

    def test_parse_output_variables(self, sample_st_code):
        """测试输出变量(VAR_OUTPUT)解析"""
        parser = STParser()
        pous, _ = parser.parse(sample_st_code)

        motor_fb = parser.get_pou_by_name("FB_Motor")
        output_vars = [
            v for v in motor_fb.variables
            if v.category == VarCategory.VAR_OUTPUT
        ]
        assert len(output_vars) >= 2

    def test_parse_global_variables(self, sample_st_code):
        """测试全局变量(VAR_GLOBAL)解析"""
        parser = STParser()
        _, global_vars = parser.parse(sample_st_code)

        assert len(global_vars) >= 3
        global_names = [v.name for v in global_vars]
        assert "g_bSystemReady" in global_names
        assert "g_rTemperature" in global_names
        assert "g_nErrorCode" in global_names


class TestVariableDataTypes:
    """变量数据类型验证测试"""

    def test_bool_variable_type(self, sample_st_code):
        """测试BOOL类型变量"""
        parser = STParser()
        pous, _ = parser.parse(sample_st_code)

        program = parser.get_pou_by_name("PLC_PRG")
        start_var = next(
            (v for v in program.variables if v.name == "bStart"), None
        )
        assert start_var is not None
        assert start_var.data_type == "BOOL"

    def test_int_variable_type(self, sample_st_code):
        """测试INT类型变量"""
        parser = STParser()
        pous, _ = parser.parse(sample_st_code)

        program = parser.get_pou_by_name("PLC_PRG")
        counter_var = next(
            (v for v in program.variables if v.name == "nCounter"), None
        )
        assert counter_var is not None
        assert counter_var.data_type == "INT"

    def test_real_variable_type(self, sample_st_code):
        """测试REAL类型变量"""
        parser = STParser()
        pous, _ = parser.parse(sample_st_code)

        motor_fb = parser.get_pou_by_name("FB_Motor")
        speed_var = next(
            (v for v in motor_fb.variables if v.name == "rSpeedRef"), None
        )
        assert speed_var is not None
        assert speed_var.data_type == "REAL"


class TestEdgeCases:
    """边界条件和异常输入测试"""

    def test_empty_source(self):
        """测试空源码输入"""
        parser = STParser()
        pous, globals_ = parser.parse("")
        assert pous == []
        assert globals_ == []

    def test_no_pou_source(self):
        """测试无POU声明的源码"""
        code = "(* Just comments *)\nVAR\n    x : INT;\nEND_VAR"
        parser = STParser()
        pous, globals_ = parser.parse(code)
        assert pous == []

    def test_get_nonexistent_pou(self, sample_st_code):
        """测试查找不存在的POU"""
        parser = STParser()
        parser.parse(sample_st_code)
        result = parser.get_pou_by_name("NonExistentPOU")
        assert result is None

    def test_get_nonexistent_variable(self, sample_st_code):
        """测试查找不存在的变量"""
        parser = STParser()
        parser.parse(sample_st_code)
        result = parser.get_variable_by_name("NonExistentVar")
        assert result is None
