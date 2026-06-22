"""auto-pm CLI 主入口

统一管理 PLC/Python 多技术栈项目。

Usage:
    auto-pm project list
    auto-pm project create --stack plc --id DJ-2026-010 --name 边框缓存机
    auto-pm plc init DJ-2026-010
    auto-pm plc check DJ-2026-010
    auto-pm plc check --all
    auto-pm plc repair DJ-2026-010 --rename
"""

from __future__ import annotations

import io
import os
import sys


def _fix_windows_encoding() -> None:
    """Windows GBK 终端编码修复

    仅在直接执行（非被 import）时调用。
    避免与 pytest capture 机制冲突。
    """
    if sys.platform != "win32" or sys.stdout is None:
        return
    _actual_encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    # PYTHONUTF8=1 时 stdout.encoding 报告 utf-8，但终端可能是 GBK
    # 通过 Windows API 获取真实控制台代码页
    try:
        import ctypes

        _kernel32 = ctypes.windll.kernel32
        _console_cp = _kernel32.GetConsoleOutputCP()
        if _console_cp and _console_cp != 65001:  # 65001 = UTF-8
            _actual_encoding = f"cp{_console_cp}"
    except (OSError, AttributeError):
        pass
    if _actual_encoding.lower() != "utf-8":
        _raw = sys.stdout.buffer if hasattr(sys.stdout, "buffer") else None
        if _raw is not None:
            sys.stdout = io.TextIOWrapper(
                _raw, encoding=_actual_encoding, errors="replace", line_buffering=True
            )


import click
from rich.console import Console

from auto_pm.app_context import AppContext
from auto_pm.cli.change import change_group
from auto_pm.cli.gui import gui_command
from auto_pm.cli.plc import plc_group
from auto_pm.cli.project import project_group
from auto_pm.cli.python import python_group
from auto_pm.cli.template import template_group

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

console = Console()


@click.version_option(None, "--version", "-v")
@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--workspace",
    "-w",
    envvar="AUTO_PM_WORKSPACE",
    default=None,
    help="工作空间根目录（默认: 当前目录）",
)
@click.pass_context
def cli(ctx: click.Context, workspace: str | None) -> None:
    """auto-pm - 自动化项目管理工具

    统一 CLI 管理 PLC/Python 多技术栈项目。
    """
    ctx.ensure_object(AppContext)
    app_ctx: AppContext = ctx.obj
    if workspace:
        app_ctx.workspace_root = os.path.abspath(workspace)


# 挂载子命令组
cli.add_command(project_group)
cli.add_command(change_group)
cli.add_command(plc_group)
cli.add_command(python_group)
cli.add_command(template_group)
cli.add_command(gui_command)


if __name__ == "__main__":
    _fix_windows_encoding()
    cli()
