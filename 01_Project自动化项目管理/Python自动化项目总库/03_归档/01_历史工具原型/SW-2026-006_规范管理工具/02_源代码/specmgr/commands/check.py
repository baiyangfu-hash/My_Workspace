from __future__ import annotations

import json
import sys
from pathlib import Path

import click
from specmgr.commands import resolve_workspace
from specmgr.core.checker_base import CheckResult, Severity
from specmgr.core.config import CHECK_SCOPES
from specmgr.services.check_svc import CheckService
from specmgr.services.fix_svc import can_auto_fix

_SEVERITY_ICONS = {Severity.ERROR: "🔴", Severity.WARNING: "🟡", Severity.INFO: "🟢"}
_SEVERITY_COLORS = {Severity.ERROR: "red", Severity.WARNING: "yellow", Severity.INFO: "green"}
_SEVERITY_LABELS = {Severity.ERROR: "错误", Severity.WARNING: "警告", Severity.INFO: "提示"}
_ASCII_SEVERITY_ICONS = {Severity.ERROR: "[ERR]", Severity.WARNING: "[WARN]", Severity.INFO: "[INFO]"}


def _supports_unicode_output() -> bool:
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        "🟡✅⏭️🔧".encode(encoding)
    except (LookupError, UnicodeEncodeError):
        return False
    return True


@click.command()
@click.option("--format", "fmt", type=click.Choice(["table", "json"]), default="table", help="输出格式")
@click.option("--check-id", "-c", multiple=True, help="只运行指定检查项")
@click.option("--severity", type=click.Choice(["error", "warning", "info"]), default="info", help="最低严重级别")
@click.option("--auto-fix", is_flag=True, default=False, help="自动修复可修复的问题")
@click.option("--dry-run", is_flag=True, default=False, help="仅预览修复操作，不实际修改文件")
@click.option("--scope", type=click.Choice(CHECK_SCOPES), default="workspace", help="检查范围")
@click.option("--project-root", type=click.Path(path_type=Path), help="项目根目录，scope=project 时必填")
@click.pass_context
def check(
    ctx: click.Context,
    fmt: str,
    check_id: tuple[str, ...],
    severity: str,
    auto_fix: bool,
    dry_run: bool,
    scope: str,
    project_root: Path | None,
) -> None:
    """运行规范健康检查"""
    workspace = resolve_workspace(ctx)
    resolved_project_root: Path | None = None
    if scope == "project":
        if project_root is None:
            raise click.UsageError("scope=project 时必须通过 --project-root 指定项目根目录")
        resolved_project_root = project_root.resolve()
        if not resolved_project_root.exists():
            raise click.UsageError(f"项目根目录不存在: {project_root}")
        try:
            resolved_project_root.relative_to(workspace)
        except ValueError as exc:
            raise click.UsageError("项目根目录必须位于工作空间内部") from exc

    svc = CheckService(workspace)
    output = svc.run(
        check_ids=list(check_id) or None,
        min_severity=Severity[severity.upper()],
        auto_fix=auto_fix,
        dry_run=dry_run,
        scope=scope,
        project_root=resolved_project_root,
    )

    if fmt == "json":
        _output_json(output.results, output.fix_results)
    else:
        _output_table(output.results, output.fix_results, auto_fix)

    sys.exit(output.exit_code)


def _output_json(results: list[CheckResult], fix_results=None) -> None:
    data = [
        {
            "check_id": r.check_id,
            "severity": r.severity.name,
            "message": r.message,
            "details": r.details,
            "fix_suggestion": r.fix_suggestion,
            "auto_fixable": can_auto_fix(r),
        }
        for r in results
    ]
    output = {"check_results": data}
    if fix_results is not None:
        output["fix_results"] = [
            {
                "check_id": fr.check_id,
                "applied": fr.applied,
                "message": fr.message,
            }
            for fr in fix_results
        ]
    click.echo(json.dumps(output, ensure_ascii=False, indent=2))


def _output_table(results: list[CheckResult], fix_results=None, show_fix: bool = False) -> None:
    unicode_output = _supports_unicode_output()
    severity_icons = _SEVERITY_ICONS if unicode_output else _ASCII_SEVERITY_ICONS
    summary_icons = ("🔴", "🟡", "🟢") if unicode_output else ("E", "W", "I")
    status_icons = ("✅", "⏭️") if unicode_output else ("OK", "SKIP")
    fix_title = "  🔧 修复结果:" if unicode_output else "  修复结果:"
    pass_prefix = "✅" if unicode_output else "OK"

    if not results:
        click.echo(click.style(f"{pass_prefix} 所有检查通过！", fg="green"))
        return

    for r in results:
        icon = severity_icons[r.severity]
        label = _SEVERITY_LABELS[r.severity]
        color = _SEVERITY_COLORS[r.severity]
        fixable_tag = " [可自动修复]" if show_fix and can_auto_fix(r) else ""
        click.echo(click.style(f"  {icon} {label}: {r.message}{fixable_tag}", fg=color))
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
        f"  汇总: {summary_icons[0]} 错误 {error_count} | {summary_icons[1]} 警告 {warning_count} | "
        f"{summary_icons[2]} 提示 {info_count} | 共 {len(results)} 项"
    )

    if fix_results is not None:
        click.echo("")
        click.echo(click.style(fix_title, fg="bright_cyan"))
        applied_count = 0
        for fr in fix_results:
            status_icon = status_icons[0] if fr.applied else status_icons[1]
            click.echo(f"    {status_icon} [{fr.check_id}] {fr.message}")
            if fr.applied:
                applied_count += 1
        click.echo(
            f"  修复汇总: {status_icons[0]} 已修复 {applied_count} | "
            f"{status_icons[1]} 跳过 {len(fix_results) - applied_count}"
        )
