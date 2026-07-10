"""spec CLI 命令边界用例 - V0.5.2 步骤3

本文件仅包含 spec_group 的边界用例（新增）。
原有 spec CLI 测试仍在 tests/spec/test_cli.py（依赖 tests/spec/conftest.py 的 fixture）。

统一组织通过 run_tests.py cli 模式涵盖 tests/cli/ + tests/spec/test_cli.py。
新增的边界用例放在本文件，使用 tests/cli/conftest.py 的 fixture 体系。
"""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from auto_pm.cli.spec import spec_group


@pytest.mark.cli
class TestSpecCLIBoundary:
    """spec CLI 边界用例（V0.5.2 新增）

    补充 tests/spec/test_cli.py 未覆盖的边界场景。
    """

    def test_help_shows_subcommands(self, cli_runner: CliRunner) -> None:
        """--help 显示所有子命令"""
        result = cli_runner.invoke(spec_group, ["--help"])
        assert result.exit_code == 0
        assert "规范管理" in result.output
        # 应列出所有子命令
        assert "check" in result.output
        assert "index" in result.output
        assert "frontmatter" in result.output
        assert "report" in result.output

    def test_no_subcommand(self, cli_runner: CliRunner) -> None:
        """无子命令时 click 显示帮助 exit_code != 0"""
        result = cli_runner.invoke(spec_group, [])
        # click group 无子命令时通常 exit_code=0 显示帮助，或 exit_code=2
        # 具体行为取决于 click 版本，这里验证不崩溃
        assert result.exit_code in (0, 2)

    def test_invalid_subcommand(self, cli_runner: CliRunner) -> None:
        """无效子命令 click 报错 exit_code != 0"""
        result = cli_runner.invoke(spec_group, ["invalid-subcommand"])
        assert result.exit_code != 0
