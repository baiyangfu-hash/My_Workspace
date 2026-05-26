from __future__ import annotations

import click
from specmgr import __version__
from specmgr.commands.check import check
from specmgr.commands.frontmatter import frontmatter
from specmgr.commands.index import index
from specmgr.commands.report import report


@click.group()
@click.version_option(version=__version__)
@click.option("--workspace", "-w", envvar="SPECMGR_WORKSPACE", help="工作空间根目录")
@click.option("--verbose", "-v", is_flag=True, help="详细输出")
@click.pass_context
def cli(ctx: click.Context, workspace: str | None, verbose: bool) -> None:
    """SpecMgr - 规范管理体系一站式CLI工具"""
    ctx.ensure_object(dict)
    ctx.obj["workspace"] = workspace
    ctx.obj["verbose"] = verbose


cli.add_command(check)
cli.add_command(index)
cli.add_command(frontmatter)
cli.add_command(report)
