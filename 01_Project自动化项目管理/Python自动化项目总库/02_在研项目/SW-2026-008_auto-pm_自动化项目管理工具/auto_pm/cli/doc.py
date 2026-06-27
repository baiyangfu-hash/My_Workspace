"""文档相关 CLI 命令"""

from __future__ import annotations

import json

import click
from rich.console import Console

from auto_pm.app_context import AppContext
from auto_pm.core.doc_refresh_service import DocRefreshService
from auto_pm.core.project_service import ProjectService

console = Console()


@click.group(name="doc")
@click.pass_context
def doc_group(ctx: click.Context) -> None:
    """项目文档相关命令"""


@doc_group.command(name="refresh")
@click.argument("project_id")
@click.option("--dry-run", is_flag=True, help="仅预览将更新的自动区，不实际写入文档")
@click.option("--json", "output_json", is_flag=True, help="以 JSON 格式输出刷新结果")
@click.pass_context
def cmd_refresh(
    ctx: click.Context,
    project_id: str,
    dry_run: bool,
    output_json: bool,
) -> None:
    """刷新 PLC 文档中的自动区"""
    app_ctx: AppContext = ctx.obj
    svc = ProjectService(app_ctx.workspace_root)
    proj = svc.get_project(project_id)
    if proj is None:
        console.print(f"[red]错误: 项目不存在: {project_id}[/red]")
        ctx.exit(1)

    refresh_service = DocRefreshService(app_ctx.workspace_root)
    result = refresh_service.refresh_project_documents(proj, dry_run=dry_run)

    if output_json:
        click.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return

    if result.issues:
        for issue in result.issues:
            console.print(f"[yellow]{issue}[/yellow]")

    if not result.refreshed_files:
        console.print("[yellow]没有可刷新的文档自动区[/yellow]")
        return

    mode_text = "[DRY-RUN] " if dry_run else ""
    console.print(
        f"[green]{mode_text}文档自动区处理完成: {len(result.refreshed_files)} 个文档[/green]"
    )
    for item in result.refreshed_files:
        action = "将刷新" if dry_run else "已刷新"
        status = "有变更" if item.changed else "无变更"
        console.print(f"  {action}: {item.file_path} ({status})")
        for block_key in item.block_keys:
            console.print(f"    - 自动区: {block_key}")
