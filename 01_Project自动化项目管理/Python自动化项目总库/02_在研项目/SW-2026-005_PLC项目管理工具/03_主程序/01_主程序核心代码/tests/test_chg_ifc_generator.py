# -*- coding: utf-8 -*-
"""CHG/IFC 生成器单元测试"""
from pathlib import Path

import pytest

from src.sync.chg_generator import ChgGenerator
from src.sync.ifc_generator import IfcGenerator
from src.sync.db_parser import DbParser, StructGroup, VarRecord


def _make_scl_with_changelog(path: Path, fb_name: str = "FB_1002_Conveyor") -> Path:
    """创建含 changelog 的 .scl 文件"""
    scl_file = path / f"{fb_name}.scl"
    scl_file.write_text(
        f"(* {fb_name} (V1.0.0) *)\n"
        f"// V1.0.0 (2026-01-15): feat: 初始版本\n"
        f"// V1.1.0 (2026-03-20): fix: 修复启动逻辑\n"
        f"FUNCTION_BLOCK {fb_name}\n"
        f"END_FUNCTION_BLOCK\n",
        encoding="utf-8",
    )
    return scl_file


def _make_scl_without_changelog(path: Path, fb_name: str = "FB_9999_Unknown") -> Path:
    """创建不含 changelog 的 .scl 文件"""
    scl_file = path / f"{fb_name}.scl"
    scl_file.write_text(
        f"FUNCTION_BLOCK {fb_name}\n"
        f"END_FUNCTION_BLOCK\n",
        encoding="utf-8",
    )
    return scl_file


def _make_db_file(path: Path, db_name: str = "GlobalVars") -> Path:
    """创建含 STRUCT 和版本号的 .db 文件

    添加版本号行，避免 VersionExtractor 返回 None 导致文件名含非法字符。
    """
    db_file = path / f"{db_name}.db"
    db_file.write_text(
        f"DATA_BLOCK {db_name}\n"
        f"// 版本号：V1.0.0\n"
        f"VAR\n"
        f"// === 输送机接口 ===\n"
        f"// 接口统计: 2输入 / 1输出\n"
        f"  stConveyor : STRUCT\n"
        f"    i_Start : BOOL; // 启动信号\n"
        f"    i_Stop : BOOL; // 停止信号\n"
        f"    o_Running : BOOL; // 运行状态\n"
        f"  END_STRUCT;\n"
        f"END_VAR\n"
        f"END_DATA_BLOCK\n",
        encoding="utf-8",
    )
    return db_file


def test_chg_generate_from_scl(tmp_path: Path):
    """从含 changelog 的 .scl 文件生成 CHG 文档"""
    scl_dir = tmp_path / "scl"
    scl_dir.mkdir()
    _make_scl_with_changelog(scl_dir, "FB_1002_Conveyor")

    out_dir = tmp_path / "chg_output"
    result = ChgGenerator.generate_from_scl(
        str(scl_dir / "FB_1002_Conveyor.scl"),
        "FB_1002_Conveyor",
        str(out_dir),
    )

    assert result != ""
    output_file = Path(result)
    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "变更记录" in content
    assert "V1.0.0" in content
    assert "V1.1.0" in content


def test_chg_generate_from_scl_no_changelog(tmp_path: Path):
    """无 changelog 的 .scl 文件返回空字符串"""
    scl_dir = tmp_path / "scl"
    scl_dir.mkdir()
    _make_scl_without_changelog(scl_dir)

    result = ChgGenerator.generate_from_scl(
        str(scl_dir / "FB_9999_Unknown.scl"),
        "FB_9999_Unknown",
        str(tmp_path / "out"),
    )

    assert result == ""


def test_chg_generate_from_scl_nonexistent_file(tmp_path: Path):
    """不存在的 .scl 文件返回空字符串"""
    result = ChgGenerator.generate_from_scl(
        str(tmp_path / "nonexistent.scl"),
        "FB_1002_Conveyor",
        str(tmp_path / "out"),
    )

    assert result == ""


def test_chg_infer_type():
    """类型推断逻辑验证"""
    assert ChgGenerator._infer_type("feat: 新增功能") == "功能"
    assert ChgGenerator._infer_type("fix: 修复bug") == "Bug修复"
    assert ChgGenerator._infer_type("refactor: 重构代码") == "重构"
    assert ChgGenerator._infer_type("docs: 更新文档") == "文档"
    assert ChgGenerator._infer_type("其他变更") == "功能"


def test_chg_render_from_scl_entries():
    """从 scl 条目渲染 CHG 文档内容"""
    entries = [
        {"version": "V1.0.0", "date": "2026-01-15", "type": "功能", "content": "初始版本", "author": "—"},
        {"version": "V1.1.0", "date": "2026-03-20", "type": "Bug修复", "content": "修复启动逻辑", "author": "—"},
    ]

    doc = ChgGenerator._render_from_scl_entries("FB_1002_Conveyor", entries, "V1.1.0")

    assert "# 变更记录" in doc
    assert "V1.0.0" in doc
    assert "V1.1.0" in doc
    assert "初始版本" in doc
    assert "人工审核清单" in doc


def test_ifc_generate(tmp_path: Path):
    """从含 STRUCT 的 .db 文件生成 IFC 文档"""
    db_dir = tmp_path / "db"
    db_dir.mkdir()
    _make_db_file(db_dir, "GlobalVars")

    out_dir = tmp_path / "ifc_output"
    result = IfcGenerator.generate(
        str(db_dir / "GlobalVars.db"),
        "FB_1002_Conveyor",
        str(out_dir),
    )

    assert result != ""
    output_file = Path(result)
    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "接口文档" in content
    assert "stConveyor" in content


def test_ifc_generate_no_match(tmp_path: Path):
    """FB 名称无匹配结构体时返回空字符串"""
    db_dir = tmp_path / "db"
    db_dir.mkdir()
    _make_db_file(db_dir, "GlobalVars")

    result = IfcGenerator.generate(
        str(db_dir / "GlobalVars.db"),
        "FB_9999_NoMatch",
        str(tmp_path / "out"),
    )

    assert result == ""


def test_ifc_generate_nonexistent_file(tmp_path: Path):
    """不存在的 .db 文件返回空字符串"""
    result = IfcGenerator.generate(
        str(tmp_path / "nonexistent.db"),
        "FB_1002_Conveyor",
        str(tmp_path / "out"),
    )

    assert result == ""


def test_ifc_render_document():
    """渲染 IFC 文档内容验证"""
    groups = [
        StructGroup(
            name="stConveyor",
            description="输送机接口",
            variables=[
                VarRecord(name="i_Start", type_="BOOL", default="", comment="启动信号"),
                VarRecord(name="o_Running", type_="BOOL", default="", comment="运行状态"),
            ],
            input_count=1,
            output_count=1,
        ),
    ]

    doc = IfcGenerator._render_document(
        "FB_1002 四层输送机系统", "V1.0.0", groups, "FB1002-SingleLayerConveyor"
    )

    assert "# 接口文档" in doc
    assert "stConveyor" in doc
    assert "i_Start" in doc
    assert "o_Running" in doc
    assert "1输入 / 1输出" in doc
    assert "人工审核清单" in doc


def test_ifc_match_groups_ob1():
    """OB1 匹配所有结构体"""
    groups = [
        StructGroup(name="stConveyor", variables=[], input_count=0, output_count=0),
        StructGroup(name="stPickPlace", variables=[], input_count=0, output_count=0),
    ]

    matched = IfcGenerator._match_groups(groups, "OB1")

    assert len(matched) == 2
