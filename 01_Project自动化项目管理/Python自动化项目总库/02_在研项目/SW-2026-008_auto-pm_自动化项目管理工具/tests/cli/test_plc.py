"""plc CLI 命令测试"""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from auto_pm.cli.__main__ import cli


def test_plc_check_all(cli_runner: CliRunner, tmp_workspace: Path) -> None:
    """测试 plc check --all"""
    result = cli_runner.invoke(
        cli,
        ["-w", str(tmp_workspace), "plc", "check", "--all"],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "DJ-2026-TEST" in result.output


def test_plc_check_project(cli_runner: CliRunner, tmp_workspace: Path) -> None:
    """测试 plc check <ID>"""
    result = cli_runner.invoke(
        cli,
        ["-w", str(tmp_workspace), "plc", "check", "DJ-2026-TEST"],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "检查结果" in result.output


def test_plc_check_not_found(cli_runner: CliRunner, tmp_workspace: Path) -> None:
    """测试 check 不存在的项目"""
    result = cli_runner.invoke(
        cli,
        ["-w", str(tmp_workspace), "plc", "check", "NOT-EXIST"],
    )
    assert result.exit_code == 1


def test_template_list(cli_runner: CliRunner, tmp_workspace: Path) -> None:
    """测试 template list"""
    result = cli_runner.invoke(
        cli,
        ["template", "list"],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
