# -*- coding: utf-8 -*-
"""
变量检查器单元测试

测试VariableParser类的核心功能：
- GVL文件解析
- 变量重复检测
- 命名规范校验
- IEC地址解析
"""
import pytest
from src.parsers.variable_parser import (
    VariableParser,
    VariableRecord,
)


@pytest.fixture
def sample_gvl_content() -> str:
    """示例GVL内容"""
    return """
VAR_GLOBAL
    (* ===== 系统状态变量 ===== *)
    g_bSystemReady     : BOOL;          (* 系统就绪 *)
    g_bEmergencyStop   : BOOL := TRUE;  (* 急停状态 *)
    g_nOperationMode   : INT := 0;      (* 运行模式 *)

    (* ===== 过程变量 ===== *)
    g_rTemperature     : REAL;          (* 温度值 [°C] *)
    g_rPressure        : REAL;          (* 压力值 [bar] *)
    g_sBatchID         : STRING := '';  (* 批次号 *)

    (* ===== IO映射变量 ===== *)
    g_diStartBtn       AT %IX0.1 : BOOL;    (* 启动按钮 *)
    g_diStopBtn        AT %IX0.2 : BOOL;    (* 停止按钮 *)
    g_doMotorRun       AT %QX0.0 : BOOL;   (* 电机运行 *)
    g_aiTempSensor      AT %IW64  : INT;    (* 温度传感器 *)
END_VAR
"""


class TestVariableParserInit:
    """VariableParser初始化测试"""

    def test_creation(self):
        """测试解析器创建"""
        parser = VariableParser()
        assert parser is not None
        assert parser.variable_count == 0


class TestGVLParsing:
    """GVL文件解析测试"""

    def test_parse_basic_gvl(self, sample_gvl_content, tmp_path):
        """测试基本GVL解析"""
        gvl_file = tmp_path / "GVL_Global.gvl"
        gvl_file.write_text(sample_gvl_content, encoding="utf-8")

        parser = VariableParser()
        success, error = parser.parse_gvl_file(str(gvl_file))

        assert success > 0
        assert error == 0
        assert parser.variable_count >= 7

    def test_variable_names_extracted(self, sample_gvl_content, tmp_path):
        """测试变量名正确提取"""
        gvl_file = tmp_path / "GVL_Test.gvl"
        gvl_file.write_text(sample_gvl_content, encoding="utf-8")

        parser = VariableParser()
        parser.parse_gvl_file(str(gvl_file))

        names = [v.name for v in parser.variables]
        assert "g_bSystemReady" in names
        assert "g_rTemperature" in names
        assert "g_aiTempSensor" in names

    def test_variable_categories(self, sample_gvl_content, tmp_path):
        """测试变量类别标记"""
        gvl_file = tmp_path / "GVL_Category.gvl"
        gvl_file.write_text(sample_gvl_content, encoding="utf-8")

        parser = VariableParser()
        parser.parse_gvl_file(str(gvl_file))

        for var in parser.variables:
            assert var.category == "GLOBAL"


class TestDuplicateDetection:
    """重复变量检测测试"""

    def test_find_duplicates_with_dups(self, tmp_path):
        """测试存在重复时的检测"""
        gvl_content = """
VAR_GLOBAL
    xTestVar   : INT;
    xTestVar   : BOOL;   (* 重复! *)
    yUniqueVar : REAL;
END_VAR
"""
        gvl_file = tmp_path / "GVL_Dup.gvl"
        gvl_file.write_text(gvl_content, encoding="utf-8")

        parser = VariableParser()
        parser.parse_gvl_file(str(gvl_file))
        duplicates = parser.find_duplicates()

        assert len(duplicates) >= 1
        dup_name = duplicates[0][0]
        assert "xtestvar" == dup_name.lower()

    def test_no_duplicates(self, sample_gvl_content, tmp_path):
        """测试无重复时返回空列表"""
        gvl_file = tmp_path / "GVL_NoDup.gvl"
        gvl_file.write_text(sample_gvl_content, encoding="utf-8")

        parser = VariableParser()
        parser.parse_gvl_file(str(gvl_file))
        duplicates = parser.find_duplicates()

        assert len(duplicates) == 0


class TestNamingConvention:
    """命名规范校验测试"""

    def test_valid_hungarian_names(self, tmp_path):
        """测试符合匈牙利命名法的变量"""
        gvl_content = """
VAR_GLOBAL
    bEnabled    : BOOL;
    nCount      : INT;
    rValue      : REAL;
    sMessage    : STRING;
END_VAR
"""
        gvl_file = tmp_path / "GVL_Valid.gvl"
        gvl_file.write_text(gvl_content, encoding="utf-8")

        parser = VariableParser()
        parser.parse_gvl_file(str(gvl_file))
        violations = parser.validate_naming_convention()

        assert len(violations) == 0

    def test_invalid_prefix_names(self, tmp_path):
        """测试不符合前缀规范的变量"""
        gvl_content = """
VAR_GLOBAL
    tempValue  : REAL;    (* 缺少 'r' 前缀 *)
    flag       : BOOL;    (* 缺少 'b' 前缀 *)
    counter    : INT;     (* 缺少 'n' 前缀 *)
END_VAR
"""
        gvl_file = tmp_path / "GVL_Invalid.gvl"
        gvl_file.write_text(gvl_content, encoding="utf-8")

        parser = VariableParser()
        parser.parse_gvl_file(str(gvl_file))
        violations = parser.validate_naming_convention()

        assert len(violations) >= 2


class TestIECAddressParsing:
    """IEC地址解析测试"""

    def test_parse_digital_input(self):
        """测试DI地址解析 %IX0.1"""
        parser = VariableParser()
        result = parser.parse_io_address("%IX0.1")

        assert result is not None
        assert result["direction"] == "INPUT"
        assert result["data_type"] == "BOOL"
        assert result["byte_offset"] == 0
        assert result["bit_offset"] == 1

    def test_parse_digital_output(self):
        """测试DO地址解析 %QX0.0"""
        parser = VariableParser()
        result = parser.parse_io_address("%QX0.0")

        assert result is not None
        assert result["direction"] == "OUTPUT"
        assert result["data_type"] == "BOOL"

    def test_parse_analog_input_word(self):
        """测试AI地址解析 %IW64"""
        parser = VariableParser()
        result = parser.parse_io_address("%IW64")

        assert result is not None
        assert result["direction"] == "INPUT"
        assert result["data_type"] == "WORD"
        assert result["byte_offset"] == 64

    def test_parse_invalid_address(self):
        """测试无效地址返回None"""
        parser = VariableParser()
        result = parser.parse_io_address("INVALID_ADDR")
        assert result is None

    def test_parse_memory_variable(self):
        """测试内存变量地址 %M0.0"""
        parser = VariableParser()
        result = parser.parse_io_address("%M0.0")

        assert result is not None
        assert result["direction"] == "MEMORY"


class TestEdgeCases:
    """边界条件测试"""

    def test_empty_gvl(self, tmp_path):
        """测试空GVL文件"""
        gvl_file = tmp_path / "GVL_Empty.gvl"
        gvl_file.write_text("", encoding="utf-8")

        parser = VariableParser()
        success, error = parser.parse_gvl_file(str(gvl_file))

        assert success == 0
        assert parser.variable_count == 0

    def test_clear_method(self, sample_gvl_content, tmp_path):
        """测试clear方法"""
        gvl_file = tmp_path / "GVL_Clear.gvl"
        gvl_file.write_text(sample_gvl_content, encoding="utf-8")

        parser = VariableParser()
        parser.parse_gvl_file(str(gvl_file))
        assert parser.variable_count > 0

        parser.clear()
        assert parser.variable_count == 0
        assert parser.variables == []
