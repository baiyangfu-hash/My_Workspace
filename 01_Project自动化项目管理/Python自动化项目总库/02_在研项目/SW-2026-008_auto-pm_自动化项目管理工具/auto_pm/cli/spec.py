"""规范管理命令组 - 整合自 specmgr 工具（SW-2026-006）

提供规范检查、索引生成、frontmatter 同步、健康报告能力。

每个子命令独立接收 --workspace 参数，不依赖顶层 -w。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click
from rich.console import Console

from auto_pm.spec.core.checker_base import CheckResult, Severity
from auto_pm.spec.core.config import CHECK_SCOPES
from auto_pm.spec.services.check_svc import CheckService
from auto_pm.spec.services.fix_svc import FixResult, can_auto_fix
from auto_pm.spec.services.frontmatter_svc import FrontmatterService
from auto_pm.spec.services.index_svc import IndexService
from auto_pm.spec.services.report_svc import ReportService

console = Console()

_SEVERITY_ICONS = {Severity.ERROR: "🔴", Severity.WARNING: "🟡", Severity.INFO: "🟢"}
_SEVERITY_COLORS = {Severity.ERROR: "red", Severity.WARNING: "yellow", Severity.INFO: "green"}
_SEVERITY_LABELS = {Severity.ERROR: "错误", Severity.WARNING: "警告", Severity.INFO: "提示"}
_ASCII_SEVERITY_ICONS = {
    Severity.ERROR: "[ERR]",
    Severity.WARNING: "[WARN]",
    Severity.INFO: "[INFO]",
}


def _supports_unicode_output() -> bool:
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        "🟡✅⏭️🔧".encode(encoding)
    except (LookupError, UnicodeEncodeError):
        return False
    return True


def _resolve_workspace(workspace: str) -> Path:
    """解析工作空间路径并校验存在性。"""
    ws = Path(workspace).resolve()
    if not ws.exists():
        console.print(f"[red]错误: 工作空间路径不存在: {workspace}[/red]")
        raise SystemExit(1)
    return ws


@click.group(name="spec")
def spec_group() -> None:
    """规范管理 - 检查/索引/frontmatter/报告（整合自 specmgr）"""


@spec_group.command(name="check")
@click.option("--workspace", "-w", required=True, help="工作空间根目录")
@click.option("--fix", "auto_fix", is_flag=True, help="自动修复可修复的问题（SHC-002/007）")
@click.option("--dry-run", is_flag=True, help="仅预览修复操作，不实际修改文件")
@click.option("--format", "fmt", type=click.Choice(["table", "json"]), default="table", help="输出格式")
@click.option("--check-id", "-c", multiple=True, help="只运行指定检查项（如 -c SHC-001）")
@click.option(
    "--severity",
    type=click.Choice(["error", "warning", "info"]),
    default="info",
    help="最低严重级别",
)
@click.option("--scope", type=click.Choice(CHECK_SCOPES), default="workspace", help="检查范围")
@click.option(
    "--project-root",
    type=click.Path(path_type=Path),
    help="项目根目录，scope=project 时必填",
)
def cmd_check(
    workspace: str,
    auto_fix: bool,
    dry_run: bool,
    fmt: str,
    check_id: tuple[str, ...],
    severity: str,
    scope: str,
    project_root: Path | None,
) -> None:
    """运行规范健康检查（SHC-001~010）"""
    ws = _resolve_workspace(workspace)

    resolved_project_root: Path | None = None
    if scope == "project":
        if project_root is None:
            console.print("[red]错误: scope=project 时必须通过 --project-root 指定项目根目录[/red]")
            raise SystemExit(1)
        resolved_project_root = project_root.resolve()
        if not resolved_project_root.exists():
            console.print(f"[red]错误: 项目根目录不存在: {project_root}[/red]")
            raise SystemExit(1)
        try:
            resolved_project_root.relative_to(ws)
        except ValueError:
            console.print("[red]错误: 项目根目录必须位于工作空间内部[/red]")
            raise SystemExit(1)

    svc = CheckService(ws)
    output = svc.run(
        check_ids=list(check_id) or None,
        min_severity=Severity[severity.upper()],
        auto_fix=auto_fix,
        dry_run=dry_run,
        scope=scope,
        project_root=resolved_project_root,
    )

    if fmt == "json":
        _output_check_json(output.results, output.fix_results)
    else:
        _output_check_table(output.results, output.fix_results, auto_fix)

    raise SystemExit(output.exit_code)


def _output_check_json(
    results: list[CheckResult],
    fix_results: list[FixResult] | None = None,
) -> None:
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
    out = {"check_results": data}
    if fix_results is not None:
        out["fix_results"] = [
            {"check_id": fr.check_id, "applied": fr.applied, "message": fr.message}
            for fr in fix_results
        ]
    click.echo(json.dumps(out, ensure_ascii=False, indent=2))


def _output_check_table(
    results: list[CheckResult],
    fix_results: list[FixResult] | None = None,
    show_fix: bool = False,
) -> None:
    unicode_output = _supports_unicode_output()
    severity_icons = (
        _SEVERITY_ICONS if unicode_output else _ASCII_SEVERITY_ICONS
    )
    summary_icons = ("🔴", "🟡", "🟢") if unicode_output else ("E", "W", "I")
    status_icons = ("✅", "⏭️") if unicode_output else ("OK", "SKIP")

    if not results:
        console.print("[green]✅ 所有检查通过！[/green]" if unicode_output else "[green]所有检查通过[/green]")
        return

    for r in results:
        icon = severity_icons[r.severity]
        label = _SEVERITY_LABELS[r.severity]
        color = _SEVERITY_COLORS[r.severity]
        fixable_tag = " [可自动修复]" if show_fix and can_auto_fix(r) else ""
        console.print(f"[{color}]  {icon} {label}: {r.message}{fixable_tag}[/{color}]")
        if r.details:
            console.print(f"[dim]    详情: {r.details}[/dim]")
        if r.fix_suggestion:
            console.print(f"[cyan]    建议: {r.fix_suggestion}[/cyan]")

    console.print("")
    console.print("-" * 60)

    error_count = sum(1 for r in results if r.severity == Severity.ERROR)
    warning_count = sum(1 for r in results if r.severity == Severity.WARNING)
    info_count = sum(1 for r in results if r.severity == Severity.INFO)

    console.print(
        f"  汇总: {summary_icons[0]} 错误 {error_count} | {summary_icons[1]} 警告 {warning_count} | "
        f"{summary_icons[2]} 提示 {info_count} | 共 {len(results)} 项"
    )

    if fix_results is not None:
        console.print("")
        fix_title = "  🔧 修复结果:" if unicode_output else "  修复结果:"
        console.print(f"[bright_cyan]{fix_title}[/bright_cyan]")
        applied_count = 0
        for fr in fix_results:
            status_icon = status_icons[0] if fr.applied else status_icons[1]
            console.print(f"    {status_icon} [{fr.check_id}] {fr.message}")
            if fr.applied:
                applied_count += 1
        console.print(
            f"  修复汇总: {status_icons[0]} 已修复 {applied_count} | "
            f"{status_icons[1]} 跳过 {len(fix_results) - applied_count}"
        )


@spec_group.command(name="index")
@click.option("--workspace", "-w", required=True, help="工作空间根目录")
@click.option(
    "--domain",
    type=click.Choice(["pm", "plc", "python", "all"]),
    default="all",
    help="只生成指定域（默认 all）",
)
def cmd_index(workspace: str, domain: str) -> None:
    """生成规范索引文件"""
    ws = _resolve_workspace(workspace)
    svc = IndexService(ws)
    domains = None if domain == "all" else [domain]
    output = svc.run(domains=domains)

    for f in output.generated_files:
        console.print(f"[green]✅ 已生成: {f}[/green]")

    for err in output.errors:
        console.print(f"[red]❌ 生成失败: {err}[/red]")


@spec_group.command(name="frontmatter")
@click.option("--workspace", "-w", required=True, help="工作空间根目录")
@click.option("--fix", is_flag=True, help="实际执行写入（默认仅预览）")
@click.option("--spec-id", default=None, help="只处理指定规范")
def cmd_frontmatter(workspace: str, fix: bool, spec_id: str | None) -> None:
    """检查/同步规范 frontmatter

    默认仅预览将添加的 frontmatter；使用 --fix 实际写入。
    """
    ws = _resolve_workspace(workspace)
    svc = FrontmatterService(ws)
    items = svc.preview(spec_id=spec_id)

    if not items:
        console.print("[yellow]没有需要处理的规范文件[/yellow]")
        return

    mode = "实际修改" if fix else "DRY-RUN（仅预览）"
    pending_count = sum(1 for i in items if i.status == "pending")
    console.print(f"扫描到 {len(items)} 个规范，其中 {pending_count} 个需要添加frontmatter")
    console.print(f"模式: {mode}")
    console.print("-" * 50)

    for item in items:
        if item.status == "skipped":
            if item.is_deprecated:
                continue
            if item.has_frontmatter:
                continue
            if not item.file_exists:
                console.print(f"[yellow]  ⚠️ 文件不存在: {item.file_path}[/yellow]")
            continue

        if item.status == "error":
            console.print(f"[red]  ❌ 处理失败: {item.spec_id}[/red]")
            continue

        if item.status == "pending":
            if not fix:
                console.print(f"[cyan]  [DRY-RUN] 将添加frontmatter到: {item.spec_id}[/cyan]")
                preview = item.new_frontmatter[:80]
                console.print(f"    {preview}...")
            else:
                console.print(f"[green]  📝 添加frontmatter到: {item.spec_id}[/green]")

    if fix and pending_count > 0:
        pending_items = [i for i in items if i.status == "pending"]
        result = svc.apply(pending_items)
        console.print("-" * 50)
        console.print(
            f"[green]完成！修改: {result.modified_count}, "
            f"跳过: {result.skipped_count}, "
            f"错误: {result.error_count}[/green]"
        )
    else:
        skipped = sum(1 for i in items if i.status == "skipped")
        errors = sum(1 for i in items if i.status == "error")
        console.print("-" * 50)
        console.print(
            f"[cyan]预览完成！待修改: {pending_count}, "
            f"跳过: {skipped}, "
            f"错误: {errors}[/cyan]"
        )


@spec_group.command(name="report")
@click.option("--workspace", "-w", required=True, help="工作空间根目录")
@click.option("--output", "-o", default=None, help="输出文件路径")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["markdown", "json"]),
    default="markdown",
    help="输出格式",
)
def cmd_report(workspace: str, output: str | None, fmt: str) -> None:
    """生成规范元数据汇总报告"""
    ws = _resolve_workspace(workspace)
    svc = ReportService(ws)
    output_path = Path(output) if output else None
    result = svc.generate(fmt=fmt, output_path=output_path)
    console.print(f"[green]✅ 报告已生成: {result.output_path}[/green]")
