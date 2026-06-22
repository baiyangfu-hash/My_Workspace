"""project CLI 命令测试"""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from auto_pm.cli.__main__ import cli


def test_project_list_via_main(
    cli_runner: CliRunner, tmp_workspace: Path
) -> None:
    """通过主入口测试 project list"""
    result = cli_runner.invoke(
        cli,
        ["-w", str(tmp_workspace), "project", "list"],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "DJ-2026-TEST" in result.output or "DJ-2026" in result.output


def test_project_show_via_main(
    cli_runner: CliRunner, tmp_workspace: Path
) -> None:
    """通过主入口测试 project show"""
    result = cli_runner.invoke(
        cli,
        ["-w", str(tmp_workspace), "project", "show", "DJ-2026-TEST"],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "DJ-2026-TEST" in result.output or "DJ-2026" in result.output


def test_project_show_not_found(
    cli_runner: CliRunner, tmp_workspace: Path
) -> None:
    """测试 show 不存在的项目"""
    result = cli_runner.invoke(
        cli,
        ["-w", str(tmp_workspace), "project", "show", "NOT-EXIST"],
    )
    assert result.exit_code == 1
