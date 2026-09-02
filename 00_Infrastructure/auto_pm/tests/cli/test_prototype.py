import os
import tempfile

from auto_pm.cli.__main__ import cli
from click.testing import CliRunner


def test_cli_prototype_flow():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Test prototype init CLI
        res = runner.invoke(cli, ["-w", tmp_dir, "prototype", "init", "--pid", "TEST-001"])
        assert res.exit_code == 0
        assert "原型脚手架初始化成功" in res.output

        # Test prototype check CLI
        res_check = runner.invoke(cli, ["-w", tmp_dir, "prototype", "check", "--pid", "TEST-001"])
        assert res_check.exit_code == 0
        assert "原型检查" in res_check.output

        # Test prototype bundle CLI
        res_bundle = runner.invoke(cli, ["-w", tmp_dir, "prototype", "bundle", "--pid", "TEST-001", "--version", "V1.0.0"])
        assert res_bundle.exit_code == 0
        assert "原型打包成功" in res_bundle.output


def test_cli_prototype_check_fails_on_undefined_handler():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmp_dir:
        res = runner.invoke(cli, ["-w", tmp_dir, "prototype", "init", "--pid", "TEST-002"])
        assert res.exit_code == 0

        html_path = os.path.join(
            tmp_dir, "03_HMI设计", "原型", "files", "HMI原型设计.html"
        )
        with open(html_path, "a", encoding="utf-8") as f:
            f.write('<button onclick="undefinedCustomFunc()">broken</button>')

        result = runner.invoke(
            cli, ["-w", tmp_dir, "prototype", "check", "--pid", "TEST-002"]
        )
        assert result.exit_code == 1
        assert "undefinedCustomFunc" in result.output
