from __future__ import annotations

from pathlib import Path

import click

from auto_pm.spec.commands import resolve_workspace
from auto_pm.spec.services.report_svc import ReportService


@click.command()
@click.option("--output", "-o", default=None, help="输出文件路径")
@click.option("--format", "fmt", type=click.Choice(["markdown", "json"]), default="markdown", help="输出格式")
@click.pass_context
def report(ctx: click.Context, output: str | None, fmt: str) -> None:
    """生成规范元数据汇总报告"""
    workspace = resolve_workspace(ctx)
    svc = ReportService(workspace)
    output_path = Path(output) if output else None
    result = svc.generate(fmt=fmt, output_path=output_path)
    click.secho(f"✅ 报告已生成: {result.output_path}", fg="green")
