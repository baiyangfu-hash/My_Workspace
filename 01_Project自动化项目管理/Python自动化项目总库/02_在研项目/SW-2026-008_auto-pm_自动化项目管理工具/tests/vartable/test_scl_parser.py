"""SclParser 深化测试 - V2.3 Week3 T12

验证 SclParser 的 detect_format 方法 + VAR 块状态机解析 + 边界场景。
"""

from __future__ import annotations

from pathlib import Path

from auto_pm.vartable.parsers.scl_parser import SclParser


class TestSclParserDetectFormat:
    def test_scl_detect_format_scl_extension(self, tmp_path: Path) -> None:
        """detect_format 对 .scl 文件返回 True"""
        f = tmp_path / "fb.scl"
        f.write_text(
            "FUNCTION_BLOCK FB_Test\n"
            "VAR_INPUT\n"
            "  i_bStart : BOOL;\n"
            "END_VAR\n",
            encoding="utf-8",
        )
        assert SclParser().detect_format(f) is True

    def test_scl_detect_format_non_scl(self, tmp_path: Path) -> None:
        """detect_format 对非 scl 文件返回 False（如纯 CSV）"""
        f = tmp_path / "var.csv"
        f.write_text(
            "station,signal_type,address,tag,signal_name,device,comment\n"
            "cpu,DI,X0,Tag,name,dev,comment\n",
            encoding="utf-8",
        )
        assert SclParser().detect_format(f) is False


class TestSclParserVarBlockExtraction:
    def test_scl_parse_var_blocks_with_fb_name_metadata(
        self, tmp_path: Path
    ) -> None:
        """解析 SCL 文件，验证 VAR_INPUT/VAR_OUTPUT/VAR 块变量提取 + FB 名称元数据"""
        f = tmp_path / "fb.scl"
        f.write_text(
            "FUNCTION_BLOCK FB_Conveyor\n"
            "VAR_INPUT\n"
            "  i_bStart : BOOL; // 启动按钮\n"
            "  i_bStop : BOOL; // 停止按钮\n"
            "  i_wSpeed : INT;\n"
            "END_VAR\n"
            "VAR_OUTPUT\n"
            "  q_bRunning : BOOL;\n"
            "  q_iAlarmCode : INT; // 报警码\n"
            "END_VAR\n"
            "VAR\n"
            "  stInternal : ST_Conveyor;\n"
            "END_VAR\n"
            "BEGIN\n"
            "  // 实现逻辑\n"
            "END_FUNCTION_BLOCK\n",
            encoding="utf-8",
        )
        result = SclParser().parse(f)
        assert result.success
        assert result.var_table is not None
        # 3 input + 2 output + 1 var = 6 个变量
        assert result.var_table.total_count == 6

        # 验证 FB 名称元数据
        assert result.var_table.metadata["fb_name"] == "FB_Conveyor"
        assert result.var_table.metadata["var_block_count"] == 3

        # 验证 VAR_INPUT 块变量
        input_entries = [
            e for e in result.var_table.entries if e.station == "VAR_INPUT"
        ]
        assert len(input_entries) == 3
        assert input_entries[0].tag == "i_bStart"
        assert input_entries[0].signal_type == "BOOL"
        assert input_entries[0].comment == "启动按钮"
        assert input_entries[0].device == "FB_Conveyor"

        # 验证 VAR_OUTPUT 块变量
        output_entries = [
            e for e in result.var_table.entries if e.station == "VAR_OUTPUT"
        ]
        assert len(output_entries) == 2
        assert output_entries[1].tag == "q_iAlarmCode"
        assert output_entries[1].signal_type == "INT"
        assert output_entries[1].comment == "报警码"

        # 验证 VAR 块变量（复杂类型 ST_ 顶层声明）
        var_entries = [e for e in result.var_table.entries if e.station == "VAR"]
        assert len(var_entries) == 1
        assert var_entries[0].tag == "stInternal"
        assert var_entries[0].signal_type == "ST_Conveyor"


class TestSclParserEdgeCases:
    def test_scl_parse_no_var_block_emits_warning(self, tmp_path: Path) -> None:
        """无 VAR 块的 SCL 文件：success=True + warnings 提示"""
        f = tmp_path / "ob1.scl"
        f.write_text(
            "ORGANIZATION_BLOCK OB1\n"
            "BEGIN\n"
            "  // 仅调用 FB，无 VAR 块\n"
            "  fbConveyor();\n"
            "END_ORGANIZATION_BLOCK\n",
            encoding="utf-8",
        )
        result = SclParser().parse(f)
        # SCL 解析默认 success=True（即使无 VAR 块也视为格式识别成功）
        assert result.success
        assert result.var_table is not None
        assert result.var_table.total_count == 0
        assert result.warning_count >= 1
        # 元数据：var_block_count=0
        assert result.var_table.metadata["var_block_count"] == 0
