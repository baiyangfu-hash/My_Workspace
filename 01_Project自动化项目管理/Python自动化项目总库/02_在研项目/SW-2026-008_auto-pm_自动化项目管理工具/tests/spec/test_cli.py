"""CLI 测试 - 适配 auto_pm.spec 命令组。

auto_pm 的 spec 命令组入口为 auto_pm.cli.spec:spec_group，每个子命令独立
接收 --workspace/-w 参数（非顶层 -w），且无 --version 选项。
"""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from auto_pm.cli.spec import spec_group


class TestCLIGroup:
    def test_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(spec_group, ["--help"])
        assert result.exit_code == 0
        assert "规范管理" in result.output

    @pytest.mark.skip(reason="auto_pm spec_group 无 --version 选项")
    def test_version(self) -> None:
        runner = CliRunner()
        result = runner.invoke(spec_group, ["--version"])
        assert result.exit_code == 0


class TestCheckCommand:
    def test_check_missing_workspace(self) -> None:
        runner = CliRunner()
        result = runner.invoke(spec_group, ["check"])
        assert result.exit_code != 0

    def test_check_with_workspace(self, populated_workspace: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(spec_group, ["check", "-w", str(populated_workspace)])
        assert result.exit_code in (0, 1, 2)

    def test_check_json_format(self, populated_workspace: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(
            spec_group,
            ["check", "-w", str(populated_workspace), "--format", "json"],
        )
        assert result.exit_code in (0, 1, 2)

    def test_check_severity_filter(self, populated_workspace: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(
            spec_group,
            ["check", "-w", str(populated_workspace), "--severity", "error"],
        )
        assert result.exit_code in (0, 1)

    def test_check_nonexistent_workspace(self) -> None:
        runner = CliRunner()
        result = runner.invoke(spec_group, ["check", "-w", "/nonexistent/path"])
        assert result.exit_code != 0

    def test_check_project_scope_requires_project_root(self, populated_workspace: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(
            spec_group,
            ["check", "-w", str(populated_workspace), "--scope", "project"],
        )
        assert result.exit_code != 0
        assert "--project-root" in result.output

    def test_check_project_scope_with_project_root(self, populated_workspace: Path) -> None:
        project_root = populated_workspace / "DJ-2026-000"
        project_root.mkdir(parents=True, exist_ok=True)
        (project_root / "PM_SESSION_DJ-2026-000.md").write_text(
            "# PM_SESSION_DJ-2026-000\n\n## 4. Artifacts Index\n- req:\n  - [missing](missing.md)\n",
            encoding="utf-8",
        )
        runner = CliRunner()
        result = runner.invoke(
            spec_group,
            [
                "check",
                "-w",
                str(populated_workspace),
                "--scope",
                "project",
                "--project-root",
                str(project_root),
            ],
        )
        assert result.exit_code == 2


class TestIndexCommand:
    def test_index_with_workspace(self, populated_workspace: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(spec_group, ["index", "-w", str(populated_workspace)])
        assert result.exit_code == 0

    def test_index_single_domain(self, populated_workspace: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(
            spec_group,
            ["index", "-w", str(populated_workspace), "--domain", "plc"],
        )
        assert result.exit_code == 0


class TestFrontmatterCommand:
    def test_frontmatter_dry_run(self, populated_workspace: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(spec_group, ["frontmatter", "-w", str(populated_workspace)])
        assert result.exit_code == 0

    def test_frontmatter_missing_workspace(self) -> None:
        runner = CliRunner()
        result = runner.invoke(spec_group, ["frontmatter"])
        assert result.exit_code != 0


class TestReportCommand:
    def test_report_with_workspace(self, populated_workspace: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(spec_group, ["report", "-w", str(populated_workspace)])
        assert result.exit_code == 0

    def test_report_json_format(self, populated_workspace: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(
            spec_group,
            ["report", "-w", str(populated_workspace), "--format", "json"],
        )
        assert result.exit_code == 0
