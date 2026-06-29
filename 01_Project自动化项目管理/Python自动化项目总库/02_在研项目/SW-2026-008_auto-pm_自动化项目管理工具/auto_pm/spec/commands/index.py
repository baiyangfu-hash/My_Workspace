from __future__ import annotations

import click

from auto_pm.spec.commands import resolve_workspace
from auto_pm.spec.services.index_svc import IndexService


@click.command()
@click.option("--domain", type=click.Choice(["pm", "plc", "python"]), default=None, help="只生成指定域")
@click.pass_context
def index(ctx: click.Context, domain: str | None) -> None:
    """自动生成规范索引文件"""
    workspace = resolve_workspace(ctx)
    svc = IndexService(workspace)
    domains = [domain] if domain else None
    output = svc.run(domains=domains)

    for f in output.generated_files:
        click.secho(f"✅ 已生成: {f}", fg="green")

    for err in output.errors:
        click.secho(f"❌ 生成失败: {err}", fg="red")
