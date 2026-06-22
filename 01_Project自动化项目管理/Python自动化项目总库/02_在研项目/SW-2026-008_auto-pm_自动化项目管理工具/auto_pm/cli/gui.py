"""GUI CLI 命令

启动 PySide6 桌面 GUI 应用。

Usage:
    auto-pm gui
    auto-pm gui --debug
    auto-pm gui -w <workspace_root>
"""

from __future__ import annotations

import click
from rich.console import Console

from auto_pm.app_context import AppContext

console = Console()


@click.command()
@click.option("--debug", is_flag=True, help="调试模式（开启 DevTools / 控制台输出）")
@click.pass_context
def gui_command(ctx: click.Context, debug: bool) -> None:
    """启动 GUI 桌面应用"""
    app_ctx: AppContext = ctx.obj
    workspace = app_ctx.workspace_root

    console.print(f"[cyan]启动 PySide6 GUI: {workspace}[/cyan]")
    _run_pyside_gui(workspace, debug)


def _run_pyside_gui(workspace: str, debug: bool) -> None:
    """启动 PySide6 主窗口"""
    try:
        from PySide6.QtWidgets import QApplication

        from auto_pm.ui.main_window import MainWindow
    except ImportError as e:
        console.print(f"[red]PySide6 依赖缺失: {e}[/red]")
        console.print("[yellow]请安装: pip install PySide6[/yellow]")
        raise click.ClickException("PySide6 依赖未安装") from e

    app = QApplication.instance() or QApplication([])
    window = MainWindow(workspace_root=workspace)
    if debug:
        console.print("[yellow]调试模式: 控制台日志已开启[/yellow]")
    window.show()
    app.exec()
