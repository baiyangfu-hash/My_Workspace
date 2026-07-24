"""chg141-e2e-test CLI 主入口

Usage:
    chg141-e2e-test --help
    chg141-e2e-test hello
"""

from __future__ import annotations

import click
from rich.console import Console

from chg141_e2e_test.app_context import AppContext

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}

console = Console()


@click.version_option(None, "--version", "-v")
@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--workspace",
    "-w",
    envvar="CHG141_E2E_TEST_WORKSPACE",
    default=None,
    help="工作空间根目录（默认: 当前目录）",
)
@click.pass_context
def cli(ctx: click.Context, workspace: str | None) -> None:
    """chg141_e2e_test - CHG-SCPT-2026-141 FileWatcherBridge end-to-end verification test project"""
    ctx.ensure_object(AppContext)
    app_ctx: AppContext = ctx.obj
    if workspace:
        app_ctx.workspace_root = workspace


@cli.command()
@click.pass_context
def hello(ctx: click.Context) -> None:
    """示例命令：打印欢迎信息"""
    app_ctx: AppContext = ctx.obj
    console.print("[green]Hello from chg141_e2e_test![/green]")
    console.print(f"workspace: {app_ctx.workspace_root}")


if __name__ == "__main__":
    cli()
