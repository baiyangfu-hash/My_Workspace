from __future__ import annotations

import json
import sys
from pathlib import Path

import click
from specmgr.commands import resolve_workspace
from specmgr.core.checker_base import CheckResult, Severity
from specmgr.services.check_svc import CheckService

_SEVERITY_ICONS = {Severity.ERROR: "🔴", Severity.WARNING: "🟡", Severity.INFO: "🟢"}
_SEVERITY_COLORS = {Severity.ERROR: "red", Severity.WARNING: "yellow", Severity.INFO: "green"}
_SEVERITY_LABELS = {Severity.ERROR: "错误", Severity.WARNING: "警告", Severity.INFO: "提示"}


@click.command()
@click.option("--format", "fmt", type=click.Choice(["table", "json"]), default="table", help="输出格式")
@click.option("--check-id", "-c", multiple=True, help="只运行指定检查项")
@click.option("--severity", type=click.Choice(["error", "warning", "info"]), default="info", help="最低严重级别")
@click.pass_context
def check(ctx: click.Context, fmt: str, check_id: tuple[str, ...], severity: str) -> None:
    """运行规范健康检查"""
    workspace = resolve_workspace(ctx)
    svc = CheckService(workspace)
    output = svc.run(
        check_ids=list(check_id) or None,
        min_severity=Severity[severity.upper()],
    )

    if fmt == "json":
        _output_json(output.results)
    else:
        _output_table(output.results)

    sys.exit(output.exit_code)


def _output_json(results: list[CheckResult]) -> None:
    data = [
        {
            "check_id": r.check_id,
            "severity": r.severity.name,
            "message": r.message,
            "details": r.details,
            "fix_suggestion": r.fix_suggestion,
        }
        for r in results
    ]
    click.echo(json.dumps(data, ensure_ascii=False, indent=2))


def _output_table(results: list[CheckResult]) -> None:
    if not results:
        click.echo(click.style("✅ 所有检查通过！", fg="green"))
        return

    for r in results:
        icon = _SEVERITY_ICONS[r.severity]
        label = _SEVERITY_LABELS[r.severity]
        color = _SEVERITY_COLORS[r.severity]
        click.echo(click.style(f"  {icon} {label}: {r.message}", fg=color))
        if r.details:
            click.echo(click.style(f"    详情: {r.details}", fg="bright_black"))
        if r.fix_suggestion:
            click.echo(click.style(f"    建议: {r.fix_suggestion}", fg="cyan"))

    click.echo("")
    click.echo("-" * 60)

    error_count = sum(1 for r in results if r.severity == Severity.ERROR)
    warning_count = sum(1 for r in results if r.severity == Severity.WARNING)
    info_count = sum(1 for r in results if r.severity == Severity.INFO)

    click.echo(
        f"  汇总: 🔴 错误 {error_count} | 🟡 警告 {warning_count} | "
        f"🟢 提示 {info_count} | 共 {len(results)} 项"
    )
