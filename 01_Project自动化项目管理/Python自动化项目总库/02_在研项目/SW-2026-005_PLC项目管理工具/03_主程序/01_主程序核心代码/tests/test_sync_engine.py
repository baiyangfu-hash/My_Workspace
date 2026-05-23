# -*- coding: utf-8 -*-
"""SyncEngine 单元测试"""
from pathlib import Path

import pytest

from types import SimpleNamespace

from src.sync.sync_engine import SyncEngine
from src.sync.version_checker import VersionGapReport, FbVersionGap


def _make_project_with_scl(project_path: Path, fb_name: str = "FB_1002_Conveyor",
                            version: str = "V1.0.0") -> Path:
    """创建含 .scl 文件的项目目录"""
    scl_dir = project_path / "src"
    scl_dir.mkdir(parents=True, exist_ok=True)
    scl_file = scl_dir / f"{fb_name}.scl"
    scl_file.write_text(
        f"(* {fb_name} (V1.0.0) *)\n"
        f"// 版本号：{version}\n"
        f"FUNCTION_BLOCK {fb_name}\n"
        f"END_FUNCTION_BLOCK\n",
        encoding="utf-8",
    )
    return scl_file


def _make_project_with_db(project_path: Path, db_name: str = "GlobalVars") -> Path:
    """创建含 .db 文件的项目目录"""
    db_dir = project_path / "src"
    db_dir.mkdir(parents=True, exist_ok=True)
    db_file = db_dir / f"{db_name}.db"
    db_file.write_text(
        f"DATA_BLOCK {db_name}\n"
        f"VAR\n"
        f"  stConveyor : STRUCT\n"
        f"    i_Start : BOOL; // 启动信号\n"
        f"    o_Running : BOOL; // 运行状态\n"
        f"  END_STRUCT;\n"
        f"END_VAR\n"
        f"END_DATA_BLOCK\n",
        encoding="utf-8",
    )
    return db_file


def test_run_check_nonexistent_path(tmp_path: Path):
    """项目路径不存在时返回空报告"""
    report = SyncEngine.run_check(str(tmp_path / "nonexistent"))

    assert isinstance(report, VersionGapReport)
    assert report.total_fbs == 0


def test_run_check_with_scl_files(tmp_path: Path):
    """包含 .scl 文件时能正常检查"""
    project = tmp_path / "CheckProject"
    project.mkdir()
    _make_project_with_scl(project, "FB_1002_Conveyor", "V1.0.0")

    report = SyncEngine.run_check(str(project))

    assert isinstance(report, VersionGapReport)
    assert report.total_fbs >= 1


def test_run_generate_chg_no_scl(tmp_path: Path):
    """无 .scl 文件时 CHG 生成返回输出目录路径"""
    project = tmp_path / "NoSclProject"
    project.mkdir()

    result = SyncEngine.run_generate_chg(str(project))

    assert result is not None


def test_run_generate_chg_with_scl(tmp_path: Path):
    """有 .scl 文件时 CHG 生成正常执行"""
    project = tmp_path / "ChgProject"
    project.mkdir()
    _make_project_with_scl(project, "FB_1002_Conveyor", "V1.0.0")

    out_dir = tmp_path / "chg_output"
    result = SyncEngine.run_generate_chg(str(project), str(out_dir))

    assert result is not None
    assert out_dir.exists()


def test_run_generate_ifc_no_db(tmp_path: Path):
    """无 .db 文件时 IFC 生成返回输出目录路径"""
    project = tmp_path / "NoDbProject"
    project.mkdir()

    result = SyncEngine.run_generate_ifc(str(project))

    assert result is not None


def test_run_generate_ifc_with_db(tmp_path: Path):
    """有 .db 文件时 IFC 生成正常执行"""
    project = tmp_path / "IfcProject"
    project.mkdir()
    _make_project_with_db(project, "GlobalVars")

    out_dir = tmp_path / "ifc_output"
    result = SyncEngine.run_generate_ifc(str(project), str(out_dir))

    assert result is not None
    assert out_dir.exists()


def test_writeback_to_project_chg(tmp_path: Path):
    """CHG 文档回写到项目标准目录"""
    project = tmp_path / "WritebackProject"
    project.mkdir()

    source_dir = tmp_path / "chg_source"
    source_dir.mkdir()
    chg_file = source_dir / "变更记录_CHG-FB1002-V1.0.0.md"
    chg_file.write_text("# CHG 测试", encoding="utf-8")

    written = SyncEngine.writeback_to_project(
        str(source_dir), str(project), "chg"
    )

    assert len(written) == 1
    target = Path(written[0])
    assert target.exists()
    assert target.name == chg_file.name


def test_writeback_to_project_ifc(tmp_path: Path):
    """IFC 文档回写到项目标准目录"""
    project = tmp_path / "WritebackIfcProject"
    project.mkdir()

    source_dir = tmp_path / "ifc_source"
    source_dir.mkdir()
    ifc_file = source_dir / "接口文档_IFC-FB1002-V1.0.0.md"
    ifc_file.write_text("# IFC 测试", encoding="utf-8")

    written = SyncEngine.writeback_to_project(
        str(source_dir), str(project), "ifc"
    )

    assert len(written) == 1
    target = Path(written[0])
    assert target.exists()


def test_writeback_to_project_invalid_type(tmp_path: Path):
    """不支持的文档类型抛出 ValueError"""
    project = tmp_path / "InvalidTypeProject"
    project.mkdir()

    with pytest.raises(ValueError, match="不支持的文档类型"):
        SyncEngine.writeback_to_project(
            str(tmp_path), str(project), "unknown"
        )


def test_writeback_to_project_nonexistent_project(tmp_path: Path):
    """项目路径不存在时抛出 FileNotFoundError"""
    with pytest.raises(FileNotFoundError):
        SyncEngine.writeback_to_project(
            str(tmp_path), str(tmp_path / "nonexistent"), "chg"
        )


def test_writeback_backup_existing_file(tmp_path: Path):
    """回写时已存在同名文件则创建 .bak 备份"""
    project = tmp_path / "BackupProject"
    project.mkdir()

    target_dir = project / SyncEngine.WRITEBACK_DIRS["chg"]
    target_dir.mkdir(parents=True)
    existing = target_dir / "test.md"
    existing.write_text("旧内容", encoding="utf-8")

    source_dir = tmp_path / "source"
    source_dir.mkdir()
    new_file = source_dir / "test.md"
    new_file.write_text("新内容", encoding="utf-8")

    SyncEngine.writeback_to_project(str(source_dir), str(project), "chg")

    bak = target_dir / "test.md.bak"
    assert bak.exists()
    assert bak.read_text(encoding="utf-8") == "旧内容"
    assert existing.read_text(encoding="utf-8") == "新内容"


def test_format_version_report_html_all_synced(tmp_path: Path):
    """全部同步时 HTML 报告显示绿色提示"""
    report = VersionGapReport(
        project_path="/test/project",
        total_fbs=1,
        synced_count=1,
        lagging_count=0,
    )
    entry = SimpleNamespace(
        is_consistent=True,
        module_name="FB_1002_Conveyor",
        code_version="V1.0.0",
        doc_version="V1.0.0",
    )
    report.module_entries = [entry]

    html = SyncEngine.format_version_report_html(report)

    assert "版本一致性检查报告" in html
    assert "全部模块文档版本一致" in html
    assert "green" in html
    assert "FB_1002_Conveyor" in html


def test_format_version_report_html_lagging(tmp_path: Path):
    """存在滞后时 HTML 报告显示红色警告"""
    report = VersionGapReport(
        project_path="/test/project",
        total_fbs=1,
        synced_count=0,
        lagging_count=1,
    )
    entry = SimpleNamespace(
        is_consistent=False,
        module_name="FB_1002_Conveyor",
        code_version="V2.0.0",
        doc_version="V1.0.0",
    )
    report.module_entries = [entry]

    html = SyncEngine.format_version_report_html(report)

    assert "1 个模块文档滞后" in html
    assert "red" in html
    assert "FB_1002_Conveyor" in html
