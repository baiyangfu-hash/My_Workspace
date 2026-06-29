from __future__ import annotations

import click

from auto_pm.spec.commands import resolve_workspace
from auto_pm.spec.services.frontmatter_svc import FrontmatterService


@click.command()
@click.option("--dry-run", is_flag=True, help="仅预览不修改")
@click.option("--spec-id", default=None, help="只处理指定规范")
@click.pass_context
def frontmatter(ctx: click.Context, dry_run: bool, spec_id: str | None) -> None:
    """批量添加/更新规范frontmatter"""
    workspace = resolve_workspace(ctx)
    svc = FrontmatterService(workspace)
    items = svc.preview(spec_id=spec_id)

    if not items:
        click.echo("没有需要处理的规范文件")
        return

    mode = "DRY-RUN（仅预览）" if dry_run else "实际修改"
    pending_count = sum(1 for i in items if i.status == "pending")
    click.echo(f"扫描到 {len(items)} 个规范，其中 {pending_count} 个需要添加frontmatter")
    click.echo(f"模式: {mode}")
    click.echo("-" * 50)

    for item in items:
        if item.status == "skipped":
            if item.is_deprecated:
                continue
            if item.has_frontmatter:
                continue
            if not item.file_exists:
                click.secho(f"  ⚠️ 文件不存在: {item.file_path}", fg="yellow")
            continue

        if item.status == "error":
            click.secho(f"  ❌ 处理失败: {item.spec_id}", fg="red")
            continue

        if item.status == "pending":
            if dry_run:
                click.secho(f"  [DRY-RUN] 将添加frontmatter到: {item.spec_id}", fg="cyan")
                click.echo(f"    {item.new_frontmatter[:80]}...")
            else:
                click.secho(f"  📝 添加frontmatter到: {item.spec_id}", fg="green")

    if not dry_run and pending_count > 0:
        pending_items = [i for i in items if i.status == "pending"]
        result = svc.apply(pending_items)
        click.echo("-" * 50)
        click.echo(
            f"完成！修改: {result.modified_count}, "
            f"跳过: {result.skipped_count}, "
            f"错误: {result.error_count}"
        )
    else:
        skipped = sum(1 for i in items if i.status == "skipped")
        errors = sum(1 for i in items if i.status == "error")
        click.echo("-" * 50)
        click.echo(
            f"预览完成！待修改: {pending_count}, "
            f"跳过: {skipped}, "
            f"错误: {errors}"
        )
