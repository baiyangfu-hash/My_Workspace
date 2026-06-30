"""Work3Parser 深化测试 - V2.3 Week3 T12

验证 Work3Parser 的 detect_format 方法 + tab 分隔字段提取 + 错误处理。
"""

from __future__ import annotations

from pathlib import Path

from auto_pm.vartable.parsers.work3_parser import Work3Parser


class TestWork3ParserDetectFormat:
    def test_work3_detect_format_wr3_extension(self, tmp_path: Path) -> None:
        """detect_format 对 .wr3 文件返回 True"""
        f = tmp_path / "var.wr3"
        # 前 2 行表头 + 1 行数据（8 字段 tab 分隔）
        f.write_text(
            "Header1\tHeader2\tHeader3\tHeader4\tHeader5\tHeader6\tHeader7\tHeader8\n"
            "Name\tType\tExtra\tExtra\tExtra\tExtra\tAddress\tDescription\n"
            "VAR_INPUT\ti_bStart\tBOOL\t\t\t\tX0\t启动\n",
            encoding="utf-8",
        )
        assert Work3Parser().detect_format(f) is True

    def test_work3_detect_format_non_work3(self, tmp_path: Path) -> None:
        """detect_format 对非 work3 文件返回 False"""
        f = tmp_path / "var.scl"
        f.write_text(
            "FUNCTION_BLOCK FB_Test\nVAR_INPUT\n  i_bStart : BOOL;\nEND_VAR\n",
            encoding="utf-8",
        )
        assert Work3Parser().detect_format(f) is False


class TestWork3ParserFieldExtraction:
    def test_work3_parse_address_and_description_extraction(
        self, tmp_path: Path
    ) -> None:
        """解析 Work3 文件，验证 scope/name/type/address/description 字段提取"""
        f = tmp_path / "var.wr3"
        f.write_text(
            "Header1\tHeader2\tHeader3\tHeader4\tHeader5\tHeader6\tHeader7\tHeader8\n"
            "Name\tType\tExtra\tExtra\tExtra\tExtra\tAddress\tDescription\n"
            "VAR_INPUT\ti_bStart\tBOOL\t\t\t\tX0\t启动按钮\n"
            "VAR_OUTPUT\tq_bRun\tBOOL\t\t\t\tY0\t运行中\n"
            "VAR_INPUT\ti_wCount\tINT\t\t\t\tD100\t计数器\n",
            encoding="utf-8",
        )
        result = Work3Parser().parse(f)
        assert result.success
        assert result.var_table is not None
        assert result.var_table.total_count == 3

        # 验证字段提取（索引：scope=0/name=1/type=2/address=6/desc=7）
        entry0 = result.var_table.entries[0]
        assert entry0.tag == "i_bStart"
        assert entry0.signal_type == "BOOL"
        assert entry0.address == "X0"
        assert entry0.comment == "启动按钮"
        assert entry0.station == "VAR_INPUT"
        assert entry0.source_format == "work3"
        assert entry0.line_number == 3  # 前 2 行表头，数据从第 3 行开始

        # 验证第 3 个条目（INT 类型）
        entry2 = result.var_table.entries[2]
        assert entry2.tag == "i_wCount"
        assert entry2.signal_type == "INT"
        assert entry2.address == "D100"

        # 派生属性
        assert set(result.var_table.stations) == {"VAR_INPUT", "VAR_OUTPUT"}
        assert set(result.var_table.signal_types) == {"BOOL", "INT"}


class TestWork3ParserErrorHandling:
    def test_work3_parse_insufficient_fields_records_error(
        self, tmp_path: Path
    ) -> None:
        """字段数不足 8 列的行计入 errors，不中断整体解析"""
        f = tmp_path / "var.wr3"
        f.write_text(
            "Header1\tHeader2\tHeader3\tHeader4\tHeader5\tHeader6\tHeader7\tHeader8\n"
            "Name\tType\tExtra\tExtra\tExtra\tExtra\tAddress\tDescription\n"
            "VAR_INPUT\ti_bStart\tBOOL\t\t\t\tX0\t启动\n"
            "BAD_ROW\tOnlyThreeFields\t\n"  # 仅 3 字段
            "VAR_OUTPUT\tq_bRun\tBOOL\t\t\t\tY0\t运行\n",
            encoding="utf-8",
        )
        result = Work3Parser().parse(f)
        # 部分成功：2 个有效条目 + 1 个错误
        assert result.success
        assert result.var_table is not None
        assert result.var_table.total_count == 2
        assert result.error_count == 1
        assert result.errors[0].field == "columns"
        assert result.errors[0].line_number == 4
