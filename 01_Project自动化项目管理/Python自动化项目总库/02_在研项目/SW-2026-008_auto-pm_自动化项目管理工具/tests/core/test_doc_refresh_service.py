"""文档自动区刷新服务测试"""

from __future__ import annotations

from pathlib import Path

import yaml

from auto_pm.core.doc_refresh_service import DocRefreshService
from auto_pm.models import ProjectInfo


def _setup_doc_project(tmp_path: Path) -> tuple[ProjectInfo, Path, Path]:
    project_dir = tmp_path / "DJ-2026-040_文档刷新项目"
    asset_dir = project_dir / "02_PLC程序" / "工程资产"
    doc_dir = project_dir / "02_PLC程序" / "程序文档"
    asset_dir.mkdir(parents=True)
    doc_dir.mkdir(parents=True)

    (asset_dir / "io_points.csv").write_text(
        "\n".join(
            [
                "station,signal_type,address,tag,signal_name,device,comment",
                "common,DI,I0.0,ESTOP_OK,急停回路正常,操作台,TRUE=安全链路闭合",
                "conveyor,DO,Q0.0,CONVEYOR_RUN,输送带运行,变频器,TRUE=正转运行",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (asset_dir / "program_blocks.yml").write_text(
        yaml.safe_dump(
            {
                "blocks": [
                    {
                        "name": "OB1",
                        "type": "OB",
                        "path": "02_PLC程序/PLC_ST/OB1/OB1.scl",
                        "responsibility": "主循环与调用编排",
                    },
                    {
                        "name": "fbConveyor",
                        "type": "FB",
                        "path": "02_PLC程序/PLC_ST/conveyor/",
                        "responsibility": "输送设备控制",
                    },
                ]
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    (asset_dir / "communications.yml").write_text(
        yaml.safe_dump(
            {
                "channels": [
                    {
                        "name": "HMI",
                        "protocol": "ethernet",
                        "role": "人机界面",
                        "endpoint": "Siemens S7-1200",
                        "notes": "补齐 IP、端口和变量映射",
                    }
                ]
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    program_doc = doc_dir / "016_DJ-2026-040_PLC程序设计总文档_PLC.md"
    program_doc.write_text(
        "\n".join(
            [
                "# PLC程序设计总文档",
                "",
                "## 4. 软件架构",
                "",
                "### 4.1 组件清单与职责",
                "",
                "<!-- AUTO_PM:BEGIN plc-program-components -->",
                "旧内容",
                "<!-- AUTO_PM:END plc-program-components -->",
                "",
                "## 8. 关联文档索引",
                "",
                "<!-- AUTO_PM:BEGIN plc-asset-index -->",
                "旧索引",
                "<!-- AUTO_PM:END plc-asset-index -->",
                "",
            ]
        ),
        encoding="utf-8",
    )
    io_doc = doc_dir / "015_DJ-2026-040_IO分配表_IO.md"
    io_doc.write_text(
        "\n".join(
            [
                "# IO分配表",
                "",
                "## 2. IO 总览",
                "",
                "<!-- AUTO_PM:BEGIN plc-io-overview -->",
                "旧IO概览",
                "<!-- AUTO_PM:END plc-io-overview -->",
                "",
            ]
        ),
        encoding="utf-8",
    )

    project = ProjectInfo(
        project_id="DJ-2026-040",
        name="文档刷新项目",
        path=str(project_dir),
        stack="plc",
        phase="developing",
        version="0.4.0",
        description="Week 4 文档自动区刷新测试项目",
        extra={},
    )
    return project, program_doc, io_doc


def test_refresh_project_documents_dry_run_does_not_modify_files(tmp_path: Path) -> None:
    """dry-run 仅预览，不修改文档"""
    project, program_doc, io_doc = _setup_doc_project(tmp_path)
    service = DocRefreshService(str(tmp_path))

    result = service.refresh_project_documents(project, dry_run=True)

    assert result.updated is False
    assert len(result.refreshed_files) == 2
    assert "旧内容" in program_doc.read_text(encoding="utf-8")
    assert "旧IO概览" in io_doc.read_text(encoding="utf-8")


def test_refresh_project_documents_updates_auto_blocks(tmp_path: Path) -> None:
    """实际刷新时只替换自动区"""
    project, program_doc, io_doc = _setup_doc_project(tmp_path)
    service = DocRefreshService(str(tmp_path))

    result = service.refresh_project_documents(project, dry_run=False)

    assert result.updated is True
    program_content = program_doc.read_text(encoding="utf-8")
    io_content = io_doc.read_text(encoding="utf-8")
    assert "旧内容" not in program_content
    assert "OB1" in program_content
    assert "io_points.csv" in program_content
    assert "旧IO概览" not in io_content
    assert "### 2.1 自动区刷新摘要" in io_content
    assert "common" in io_content
