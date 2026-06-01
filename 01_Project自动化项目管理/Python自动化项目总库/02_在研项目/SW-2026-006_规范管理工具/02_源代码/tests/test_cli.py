from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from specmgr.cli import cli


class TestCLIGroup:
    def test_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "SpecMgr" in result.output

    def test_version(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.2.0" in result.output


class TestCheckCommand:
    def test_check_missing_workspace(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["check"])
        assert result.exit_code != 0

    def test_check_with_workspace(self, populated_workspace: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["-w", str(populated_workspace), "check"])
        assert result.exit_code in (0, 1, 2)

    def test_check_json_format(self, populated_workspace: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["-w", str(populated_workspace), "check", "--format", "json"])
        assert result.exit_code in (0, 1, 2)

    def test_check_severity_filter(self, populated_workspace: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["-w", str(populated_workspace), "check", "--severity", "error"])
        assert result.exit_code in (0, 1)

    def test_check_nonexistent_workspace(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["-w", "/nonexistent/path", "check"])
        assert result.exit_code != 0

    def test_check_project_scope_requires_project_root(self, populated_workspace: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["-w", str(populated_workspace), "check", "--scope", "project"])
        assert result.exit_code != 0
        assert "--project-root" in result.output

    def test_check_project_scope_with_project_root(self, populated_workspace: Path) -> None:
        project_root = populated_workspace / "DJ-2026-000"
        project_root.mkdir(parents=True, exist_ok=True)
        (project_root / "PM_SESSION_DJ-2026-000.md").write_text(
            "# PM_SESSION_DJ-2026-000\n\n## 4. Artifacts Index\n- req:\n  - missing.md\n",
            encoding="utf-8",
        )
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "-w",
                str(populated_workspace),
                "check",
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
        result = runner.invoke(cli, ["-w", str(populated_workspace), "index"])
        assert result.exit_code == 0

    def test_index_single_domain(self, populated_workspace: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["-w", str(populated_workspace), "index", "--domain", "plc"])
        assert result.exit_code == 0


class TestFrontmatterCommand:
    def test_frontmatter_dry_run(self, populated_workspace: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["-w", str(populated_workspace), "frontmatter", "--dry-run"])
        assert result.exit_code == 0

    def test_frontmatter_missing_workspace(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["frontmatter", "--dry-run"])
        assert result.exit_code != 0


class TestReportCommand:
    def test_report_with_workspace(self, populated_workspace: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["-w", str(populated_workspace), "report"])
        assert result.exit_code == 0

    def test_report_json_format(self, populated_workspace: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["-w", str(populated_workspace), "report", "--format", "json"])
        assert result.exit_code == 0
