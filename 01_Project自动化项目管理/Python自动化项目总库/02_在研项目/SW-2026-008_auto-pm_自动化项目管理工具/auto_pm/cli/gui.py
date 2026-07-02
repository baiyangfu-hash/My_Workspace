"""GUI CLI 命令

启动 PySide6 桌面 GUI 应用。

Usage:
    auto-pm gui
    auto-pm gui --debug
    auto-pm gui -w <workspace_root>
"""

from __future__ import annotations

import sys
import traceback
from datetime import datetime
from pathlib import Path
from types import TracebackType
from typing import Optional

import click
from rich.console import Console

from auto_pm.app_context import AppContext

console = Console()


def _install_crash_handler() -> None:
    """安装 GUI 崩溃捕获（sys.excepthook + crash.log）

    电气部门试用期间如遇 GUI 崩溃，未捕获的异常会写入
    ``~/.auto-pm/logs/crash.log``，含时间戳 + 完整 traceback，便于问题追溯。
    """
    crash_log_path = Path.home() / ".auto-pm" / "logs" / "crash.log"
    try:
        crash_log_path.parent.mkdir(parents=True, exist_ok=True)
    except (OSError, PermissionError):
        return  # 目录创建失败时静默跳过，不阻断 GUI 启动

    def _crash_excepthook(
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_tb: Optional[TracebackType],
    ) -> None:
        # 先写 crash.log
        try:
            ts = datetime.now().isoformat()
            tb_lines = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
            with open(crash_log_path, "a", encoding="utf-8") as f:
                f.write(f"\n{'=' * 80}\n")
                f.write(f"[{ts}] GUI 未捕获异常\n")
                f.write(f"{'=' * 80}\n")
                f.write(tb_lines)
        except (OSError, PermissionError):
            pass
        # 再调用默认 excepthook 输出到 stderr
        sys.__excepthook__(exc_type, exc_value, exc_tb)

    sys.excepthook = _crash_excepthook


@click.command()
@click.option("--debug", is_flag=True, help="调试模式（开启 DevTools / 控制台输出）")
@click.pass_context
def gui_command(ctx: click.Context, debug: bool) -> None:
    """启动 GUI 桌面应用"""
    app_ctx: AppContext = ctx.obj
    workspace = app_ctx.workspace_root

    # 安装 GUI 崩溃捕获（电气部门试用期间问题追溯）
    _install_crash_handler()
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
