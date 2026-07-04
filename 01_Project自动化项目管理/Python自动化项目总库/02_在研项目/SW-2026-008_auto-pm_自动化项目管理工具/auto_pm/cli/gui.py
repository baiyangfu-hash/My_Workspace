"""GUI CLI 命令

启动 PySide6 桌面 GUI 应用（V0.8.0 起 QML 为默认入口）。

Usage:
    auto-pm gui                       # 默认启动 QML GUI（V0.8.0）
    auto-pm gui --debug
    auto-pm gui -w <workspace_root>
    auto-pm gui --qwidget             # 启动旧版 QWidget GUI（deprecated，V0.9 移除）
    auto-pm gui --qml                 # (deprecated) QML 现为默认入口，本标志将被移除
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
@click.option(
    "--qwidget",
    is_flag=True,
    help="启动旧版 QWidget GUI（deprecated，V0.9 移除）",
)
@click.option(
    "--qml",
    is_flag=True,
    help="(deprecated) QML 现为默认入口，本标志将被移除",
)
@click.pass_context
def gui_command(ctx: click.Context, debug: bool, qwidget: bool, qml: bool) -> None:
    """启动 GUI 桌面应用（V0.8.0 起 QML 为默认入口）"""
    app_ctx: AppContext = ctx.obj
    workspace = app_ctx.workspace_root

    # 安装 GUI 崩溃捕获（电气部门试用期间问题追溯）
    _install_crash_handler()

    if qml:
        # V0.8.0 起 QML 为默认入口，--qml 标志已无实际作用，仅提示弃用
        console.print(
            "[yellow]--qml 已弃用：QML 现为默认入口，本标志将在 V0.9 移除[/yellow]"
        )

    if qwidget:
        # 旧版 QWidget 入口（保留至 V0.9，向后兼容）
        console.print(f"[cyan]启动 QWidget GUI (legacy): {workspace}[/cyan]")
        _run_pyside_gui(workspace, debug)
    else:
        # 默认入口：QML（V0.8.0 翻转）
        console.print(f"[cyan]启动 QML GUI (V0.8.0): {workspace}[/cyan]")
        _run_qml_gui(workspace, debug)


def _run_qml_gui(workspace: str, debug: bool) -> None:
    """启动 QML GUI（V0.8.0 起为默认入口）

    用 QQmlApplicationEngine 加载 main.qml，由 QmlBridge 桥接后端 Service。
    V0.6.0~V0.7.x 期间曾作为 PoC 入口，V0.8.0 翻转为默认入口。
    """
    try:
        from auto_pm.ui.qml_main_window import run_qml_gui
    except ImportError as e:
        console.print(f"[red]QML 模块加载失败: {e}[/red]")
        console.print("[yellow]请确认 PySide6 ≥ 6.5 已安装[/yellow]")
        raise click.ClickException("QML 模块加载失败") from e

    exit_code = run_qml_gui(workspace_root=workspace, debug=debug)
    if exit_code != 0:
        raise click.ClickException(f"QML GUI 异常退出: exit_code={exit_code}")


def _run_pyside_gui(workspace: str, debug: bool) -> None:
    """启动旧版 QWidget 主窗口（deprecated，V0.9 移除）

    V0.8.0 起 QML 为默认入口，本函数仅作向后兼容入口。
    """
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
