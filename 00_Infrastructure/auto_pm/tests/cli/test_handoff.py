"""handoff.v1 CLI 的请求、回执和 PM 消费测试。"""

from __future__ import annotations

import json
from pathlib import Path

from auto_pm.cli.__main__ import cli
from click.testing import CliRunner


def test_handoff_cli_create_list_show(tmp_path: Path) -> None:
    runner = CliRunner()
    create = runner.invoke(
        cli,
        [
            "-w",
            str(tmp_path),
            "handoff",
            "create",
            "--pid",
            "SW-2026-008",
            "--to",
            "fullstack-engineer",
            "--summary",
            "执行 cockpit CLI 适配",
            "--mode",
            "grooming",
            "--request-id",
            "AI-20260901-CLI",
            "--json-output",
        ],
    )
    assert create.exit_code == 0, create.output
    payload = json.loads(create.output)
    assert payload["schema_version"] == "handoff.v1"

    listed = runner.invoke(
        cli,
        [
            "-w",
            str(tmp_path),
            "handoff",
            "list",
            "--pid",
            "SW-2026-008",
            "--json-output",
        ],
    )
    assert listed.exit_code == 0, listed.output
    assert json.loads(listed.output)[0]["request_id"] == "AI-20260901-CLI"

    shown = runner.invoke(
        cli,
        [
            "-w",
            str(tmp_path),
            "handoff",
            "show",
            "AI-20260901-CLI",
            "--json-output",
        ],
    )
    assert shown.exit_code == 0, shown.output
    assert json.loads(shown.output)["status"] == "pending"


def test_handoff_cli_close_result_file_and_legacy_pid_resolution(tmp_path: Path) -> None:
    runner = CliRunner()
    created = runner.invoke(
        cli,
        [
            "-w",
            str(tmp_path),
            "handoff",
            "create",
            "--pid",
            "SW-2026-008",
            "--to",
            "plc-electrical-engineer",
            "--summary",
            "执行 PLC 静态检查",
            "--request-id",
            "AI-20260901-CLI-CLOSE",
        ],
    )
    assert created.exit_code == 0, created.output

    result_file = tmp_path / "handoff_result.json"
    result_file.write_text(
        json.dumps(
            {
                "summary": "PLC 静态检查通过",
                "verification": {
                    "lint_result": "auto-pm plc check PASS",
                    "test_result": "pytest PASS",
                },
                "changed_files": ["DJ-2026-005/TEC.md"],
                "chg_updates": ["CHG-PLC-2026-001: verified"],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    closed = runner.invoke(
        cli,
        [
            "-w",
            str(tmp_path),
            "handoff",
            "close",
            "--pid",
            "SW-2026-008",
            "--result-file",
            str(result_file),
            "--json-output",
        ],
    )
    assert closed.exit_code == 0, closed.output
    assert json.loads(closed.output)["status"] == "consumed"

    retry = runner.invoke(
        cli,
        [
            "-w",
            str(tmp_path),
            "handoff",
            "close",
            "AI-20260901-CLI-CLOSE",
            "--result-file",
            str(result_file),
            "--json-output",
        ],
    )
    assert retry.exit_code == 0, retry.output


def test_handoff_cli_close_rejects_missing_evidence(tmp_path: Path) -> None:
    runner = CliRunner()
    created = runner.invoke(
        cli,
        [
            "-w",
            str(tmp_path),
            "handoff",
            "create",
            "--pid",
            "SW-2026-008",
            "--to",
            "fullstack-engineer",
            "--summary",
            "必须有验证证据",
            "--request-id",
            "AI-20260901-CLI-FAIL",
        ],
    )
    assert created.exit_code == 0, created.output

    closed = runner.invoke(
        cli,
        [
            "-w",
            str(tmp_path),
            "handoff",
            "close",
            "AI-20260901-CLI-FAIL",
        ],
    )
    assert closed.exit_code == 1
    assert "验证证据" in closed.output


def test_handoff_cli_preflight_does_not_consume(tmp_path: Path) -> None:
    runner = CliRunner()
    created = runner.invoke(
        cli,
        [
            "-w",
            str(tmp_path),
            "handoff",
            "create",
            "--pid",
            "SW-2026-008",
            "--to",
            "fullstack-engineer",
            "--summary",
            "预检不应改变状态",
            "--request-id",
            "AI-20260901-CLI-PREFLIGHT",
        ],
    )
    assert created.exit_code == 0, created.output

    result_file = tmp_path / "preflight.json"
    result_file.write_text(
        json.dumps({"verification": {"other_checks": ["preflight PASS"]}}),
        encoding="utf-8",
    )
    preflight = runner.invoke(
        cli,
        [
            "-w",
            str(tmp_path),
            "handoff",
            "preflight",
            "AI-20260901-CLI-PREFLIGHT",
            "--result-file",
            str(result_file),
            "--pid",
            "SW-2026-008",
            "--json-output",
        ],
    )
    assert preflight.exit_code == 0, preflight.output
    assert json.loads(preflight.output)["already_consumed"] is False

    shown = runner.invoke(
        cli,
        [
            "-w",
            str(tmp_path),
            "handoff",
            "show",
            "AI-20260901-CLI-PREFLIGHT",
            "--json-output",
        ],
    )
    assert json.loads(shown.output)["status"] == "pending"
