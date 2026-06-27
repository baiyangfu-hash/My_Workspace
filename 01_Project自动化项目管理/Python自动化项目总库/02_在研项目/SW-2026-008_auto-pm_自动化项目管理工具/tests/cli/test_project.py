"""project CLI 命令测试"""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from auto_pm.cli.__main__ import cli


def test_project_list_via_main(cli_runner: CliRunner, tmp_workspace: Path) -> None:
    """通过主入口测试 project list"""
    result = cli_runner.invoke(
        cli,
        ["-w", str(tmp_workspace), "project", "list"],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "DJ-2026-TEST" in result.output or "DJ-2026" in result.output


def test_project_show_via_main(cli_runner: CliRunner, tmp_workspace: Path) -> None:
    """通过主入口测试 project show"""
    result = cli_runner.invoke(
        cli,
        ["-w", str(tmp_workspace), "project", "show", "DJ-2026-TEST"],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "DJ-2026-TEST" in result.output or "DJ-2026" in result.output


def test_project_show_not_found(cli_runner: CliRunner, tmp_workspace: Path) -> None:
    """测试 show 不存在的项目"""
    result = cli_runner.invoke(
        cli,
        ["-w", str(tmp_workspace), "project", "show", "NOT-EXIST"],
    )
    assert result.exit_code == 1


def test_project_show_displays_v040_metadata(cli_runner: CliRunner, tmp_path: Path) -> None:
    """project show 展示 Week 2 项目元数据"""
    project_dir = tmp_path / "DJ-2026-020_单机项目"
    project_dir.mkdir()
    (project_dir / ".copier-answers.yml").write_text(
        "\n".join(
            [
                "project_id: DJ-2026-020",
                "project_name: 单机项目",
                "stack: plc",
                "project_type: single_machine",
                "equipment_type: conveyor",
                "plc_vendor: Siemens",
                "plc_model: S7-1200",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = cli_runner.invoke(
        cli,
        ["-w", str(tmp_path), "project", "show", "DJ-2026-020"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "项目类型" in result.output
    assert "单机设备" in result.output
    assert "设备类型" in result.output
    assert "输送设备" in result.output
    assert "PLC品牌" in result.output
    assert "Siemens" in result.output
    assert "PLC型号" in result.output
    assert "S7-1200" in result.output


def test_project_create_dry_run_displays_v040_metadata(
    cli_runner: CliRunner, tmp_path: Path
) -> None:
    """project create --dry-run 输出 Week 2 元数据"""
    result = cli_runner.invoke(
        cli,
        [
            "-w",
            str(tmp_path),
            "project",
            "create",
            "--stack",
            "plc",
            "--id",
            "DJ-2026-021",
            "--name",
            "测试单机",
            "--project-type",
            "single_machine",
            "--equipment-type",
            "conveyor",
            "--plc-vendor",
            "Siemens",
            "--plc-model",
            "S7-1200",
            "--dry-run",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "项目类型: single_machine" in result.output
    assert "设备类型: conveyor" in result.output
    assert "PLC 品牌: Siemens" in result.output
    assert "PLC 型号: S7-1200" in result.output


# ── project snapshot 命令测试（V0.3.2 独立 Spec Snapshot 刷新） ──

# PM_SESSION 内容（含 Spec Snapshot 表格，版本号故意设旧）
_PM_SESSION_WITH_DRIFT = """# PM_SESSION_SW-2026-TEST

## 0. Meta
- project_id: SW-2026-TEST
- project_name: 测试项目

## Spec Snapshot（初始化时锁定，供后续版本漂移检测）

> 以下版本号在项目初始化时从 spec_registry.json 读取并填入。

| 规范编号 | 版本号 | 记录日期 | 说明 |
|---------|--------|---------|------|
| LSP-906 | V1.0.0 | 2026-06-06 | PLC编程错误预防规则 |
| LSP-907 | V1.0.0 | 2026-06-06 | PLC项目配置规范 |

## 其他章节

一些内容。
"""

# PM_SESSION 内容（无漂移，版本号与注册表一致）
_PM_SESSION_NO_DRIFT = """# PM_SESSION_SW-2026-TEST

## 0. Meta
- project_id: SW-2026-TEST
- project_name: 测试项目

## Spec Snapshot（初始化时锁定，供后续版本漂移检测）

| 规范编号 | 版本号 | 记录日期 | 说明 |
|---------|--------|---------|------|
| LSP-906 | V2.0.0 | 2026-06-06 | PLC编程错误预防规则 |
| LSP-907 | V1.2.1 | 2026-06-06 | PLC项目配置规范 |
"""

# PM_SESSION 内容（无 Spec Snapshot 表格）
_PM_SESSION_NO_TABLE = """# PM_SESSION_SW-2026-TEST

## 0. Meta
- project_id: SW-2026-TEST
- project_name: 测试项目

## 其他章节

无 Spec Snapshot 表格。
"""

# spec_registry.json（版本号设新）
_REGISTRY_JSON = {
    "version": "1.0.0",
    "specs": [
        {"spec_id": "LSP-906", "version": "V2.0.0", "title": "PLC编程错误预防规则"},
        {"spec_id": "LSP-907", "version": "V1.2.1", "title": "PLC项目配置规范"},
    ],
}


def _setup_snapshot_workspace(
    tmp_path: Path, pm_session_content: str, with_registry: bool = True
) -> Path:
    """创建临时工作空间和项目目录（含 spec_registry.json）

    Args:
        tmp_path: pytest 临时目录
        pm_session_content: PM_SESSION 文件内容
        with_registry: 是否创建 spec_registry.json

    Returns:
        工作空间根目录路径（tmp_path）
    """
    # 创建项目目录（使用 .copier-answers.yml 标志文件以便 ProjectService 识别）
    project_dir = tmp_path / "SW-2026-TEST_测试项目"
    project_dir.mkdir()
    (project_dir / ".copier-answers.yml").write_text(
        "project_id: SW-2026-TEST\nproject_name: 测试项目\n",
        encoding="utf-8",
    )

    # 写入 PM_SESSION
    (project_dir / "PM_SESSION_SW-2026-TEST.md").write_text(pm_session_content, encoding="utf-8")

    # 写入 spec_registry.json
    if with_registry:
        registry_dir = tmp_path / "00_Obsidian_Base全局规范文件仓库"
        registry_dir.mkdir(parents=True, exist_ok=True)
        (registry_dir / "spec_registry.json").write_text(
            json.dumps(_REGISTRY_JSON, ensure_ascii=False), encoding="utf-8"
        )

    return tmp_path


class TestProjectSnapshot:
    """project snapshot 命令测试"""

    def test_snapshot_with_drift_updates_versions(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """有漂移时更新版本号"""
        workspace = _setup_snapshot_workspace(tmp_path, _PM_SESSION_WITH_DRIFT)
        result = cli_runner.invoke(
            cli,
            ["-w", str(workspace), "project", "snapshot", "SW-2026-TEST"],
            catch_exceptions=False,
        )
        assert result.exit_code == 0
        assert "Spec Snapshot 已更新" in result.output
        assert "LSP-906" in result.output
        assert "V1.0.0 → V2.0.0" in result.output
        assert "LSP-907" in result.output
        assert "V1.0.0 → V1.2.1" in result.output

        # 验证文件已更新
        pm_session = tmp_path / "SW-2026-TEST_测试项目" / "PM_SESSION_SW-2026-TEST.md"
        content = pm_session.read_text(encoding="utf-8")
        assert "| LSP-906 | V2.0.0 |" in content
        assert "| LSP-907 | V1.2.1 |" in content
        assert "| LSP-906 | V1.0.0 |" not in content

    def test_snapshot_dry_run_does_not_modify(self, cli_runner: CliRunner, tmp_path: Path) -> None:
        """dry-run 模式不修改文件"""
        workspace = _setup_snapshot_workspace(tmp_path, _PM_SESSION_WITH_DRIFT)
        result = cli_runner.invoke(
            cli,
            ["-w", str(workspace), "project", "snapshot", "SW-2026-TEST", "--dry-run"],
            catch_exceptions=False,
        )
        assert result.exit_code == 0
        assert "[DRY-RUN]" in result.output
        assert "LSP-906" in result.output

        # 验证文件未被修改
        pm_session = tmp_path / "SW-2026-TEST_测试项目" / "PM_SESSION_SW-2026-TEST.md"
        content = pm_session.read_text(encoding="utf-8")
        assert "| LSP-906 | V1.0.0 |" in content
        assert "| LSP-906 | V2.0.0 |" not in content

    def test_snapshot_no_drift(self, cli_runner: CliRunner, tmp_path: Path) -> None:
        """无漂移时输出已是最新"""
        workspace = _setup_snapshot_workspace(tmp_path, _PM_SESSION_NO_DRIFT)
        result = cli_runner.invoke(
            cli,
            ["-w", str(workspace), "project", "snapshot", "SW-2026-TEST"],
            catch_exceptions=False,
        )
        assert result.exit_code == 0
        assert "已是最新" in result.output

    def test_snapshot_not_found(self, cli_runner: CliRunner, tmp_path: Path) -> None:
        """项目不存在时报错"""
        workspace = _setup_snapshot_workspace(tmp_path, _PM_SESSION_WITH_DRIFT)
        result = cli_runner.invoke(
            cli,
            ["-w", str(workspace), "project", "snapshot", "NOT-EXIST"],
        )
        assert result.exit_code == 1
        assert "项目不存在" in result.output

    def test_snapshot_no_table(self, cli_runner: CliRunner, tmp_path: Path) -> None:
        """PM_SESSION 缺少 Spec Snapshot 表格时报错"""
        workspace = _setup_snapshot_workspace(tmp_path, _PM_SESSION_NO_TABLE)
        result = cli_runner.invoke(
            cli,
            ["-w", str(workspace), "project", "snapshot", "SW-2026-TEST"],
        )
        assert result.exit_code == 1
        assert "缺少 Spec Snapshot 表格" in result.output

    def test_snapshot_no_registry(self, cli_runner: CliRunner, tmp_path: Path) -> None:
        """spec_registry.json 不存在时报错"""
        workspace = _setup_snapshot_workspace(tmp_path, _PM_SESSION_WITH_DRIFT, with_registry=False)
        result = cli_runner.invoke(
            cli,
            ["-w", str(workspace), "project", "snapshot", "SW-2026-TEST"],
        )
        assert result.exit_code == 1
        assert "spec_registry.json" in result.output

    def test_snapshot_json_output(self, cli_runner: CliRunner, tmp_path: Path) -> None:
        """JSON 输出格式（dry-run）"""
        workspace = _setup_snapshot_workspace(tmp_path, _PM_SESSION_WITH_DRIFT)
        result = cli_runner.invoke(
            cli,
            [
                "-w",
                str(workspace),
                "project",
                "snapshot",
                "SW-2026-TEST",
                "--dry-run",
                "--json",
            ],
            catch_exceptions=False,
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["dry_run"] is True
        assert data["updated"] is False
        assert len(data["drifts"]) == 2
        spec_ids = {d["spec_id"] for d in data["drifts"]}
        assert spec_ids == {"LSP-906", "LSP-907"}

    def test_snapshot_json_output_no_drift(self, cli_runner: CliRunner, tmp_path: Path) -> None:
        """JSON 输出格式（无漂移）"""
        workspace = _setup_snapshot_workspace(tmp_path, _PM_SESSION_NO_DRIFT)
        result = cli_runner.invoke(
            cli,
            [
                "-w",
                str(workspace),
                "project",
                "snapshot",
                "SW-2026-TEST",
                "--json",
            ],
            catch_exceptions=False,
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["drifts"] == []
        assert data["updated"] is False
