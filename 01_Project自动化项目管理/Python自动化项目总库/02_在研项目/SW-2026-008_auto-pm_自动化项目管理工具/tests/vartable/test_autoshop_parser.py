"""AutoshopParser 深化测试 - V2.3 Week3 T12

验证 AutoshopParser 的 detect_format 方法 + 真实字段提取 + 错误处理 + 编码兼容。
"""

from __future__ import annotations

from pathlib import Path

from auto_pm.vartable.parsers.autoshop_parser import AutoshopParser


class TestAutoshopParserDetectFormat:
    def test_autoshop_detect_format_asc_extension(self, tmp_path: Path) -> None:
        """detect_format 对 .asc 文件返回 True"""
        f = tmp_path / "var.asc"
        f.write_text(
            "变量名,数据类型,地址,注释,作用域\n"
            "i_bStart,BOOL,X0,启动,VAR_INPUT\n",
            encoding="utf-8",
        )
        assert AutoshopParser().detect_format(f) is True

    def test_autoshop_detect_format_non_autoshop(self, tmp_path: Path) -> None:
        """detect_format 对非 autoshop 文件返回 False"""
        f = tmp_path / "var.scl"
        f.write_text(
            "FUNCTION_BLOCK FB_Test\nVAR_INPUT\n  i_bStart : BOOL;\nEND_VAR\n",
            encoding="utf-8",
        )
        assert AutoshopParser().detect_format(f) is False


class TestAutoshopParserFieldExtraction:
    def test_autoshop_parse_multiline_with_chinese_columns(
        self, tmp_path: Path
    ) -> None:
        """解析多行含中文列名 CSV，验证字段提取正确性"""
        f = tmp_path / "var.asc"
        f.write_text(
            "变量名,数据类型,地址,注释,作用域\n"
            "i_bStart,BOOL,X0,启动按钮,VAR_INPUT\n"
            "i_bStop,BOOL,X1,停止按钮,VAR_INPUT\n"
            "q_bRun,BOOL,Y0,运行中,VAR_OUTPUT\n",
            encoding="utf-8",
        )
        result = AutoshopParser().parse(f)
        assert result.success
        assert result.var_table is not None
        assert result.var_table.total_count == 3

        # 验证第 1 个条目字段
        entry0 = result.var_table.entries[0]
        assert entry0.tag == "i_bStart"
        assert entry0.signal_type == "BOOL"
        assert entry0.address == "X0"
        assert entry0.comment == "启动按钮"
        assert entry0.station == "VAR_INPUT"
        assert entry0.source_format == "autoshop"
        assert entry0.line_number == 2  # 表头是第 1 行

        # 验证 station/signal_types 派生属性
        assert set(result.var_table.stations) == {"VAR_INPUT", "VAR_OUTPUT"}
        assert result.var_table.signal_types == ("BOOL",)

    def test_autoshop_parse_gbk_encoding(self, tmp_path: Path) -> None:
        """GBK 编码的 Autoshop 文件能正确解析（detect_encoding 兼容）"""
        f = tmp_path / "var_gbk.asc"
        content = (
            "变量名,数据类型,地址,注释,作用域\n"
            "i_bStart,BOOL,X0,启动按钮,VAR_INPUT\n"
        )
        f.write_bytes(content.encode("gbk"))
        result = AutoshopParser().parse(f)
        assert result.success
        assert result.var_table is not None
        assert result.var_table.total_count == 1
        assert result.var_table.entries[0].tag == "i_bStart"
        assert result.var_table.entries[0].comment == "启动按钮"
        # 编码检测应识别为 gbk 或 gb2312
        assert result.var_table.encoding in ("gbk", "gb2312", "utf-8")


class TestAutoshopParserErrorHandling:
    def test_autoshop_parse_missing_name_records_error(self, tmp_path: Path) -> None:
        """变量名为空的行计入 errors，不中断整体解析"""
        f = tmp_path / "var.asc"
        f.write_text(
            "变量名,数据类型,地址,注释,作用域\n"
            "i_bStart,BOOL,X0,启动,VAR_INPUT\n"
            ",BOOL,X1,缺变量名,VAR_INPUT\n"
            "q_bRun,BOOL,Y0,运行,VAR_OUTPUT\n",
            encoding="utf-8",
        )
        result = AutoshopParser().parse(f)
        # 部分成功：2 个有效条目 + 1 个错误
        assert result.success
        assert result.var_table is not None
        assert result.var_table.total_count == 2
        assert result.error_count == 1
        assert result.errors[0].field == "name"
        assert result.errors[0].line_number == 3
