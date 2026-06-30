"""变量表管理命令组 - V2.3 吸收 SW-2026-001 变量表解析能力

提供变量表解析、编码检测能力。

子命令：
- parse: 解析 io_points.csv 文件，输出条目详情
- detect-encoding: 检测文件编码
"""

from __future__ import annotations

import json
import sys

import click
from rich.console import Console
from rich.table import Table

from auto_pm.vartable.parsers.io_points_parser import IoPointsParser
from auto_pm.vartable.utils.encoding import SUPPORTED_ENCODINGS, detect_encoding

console = Console()


def _supports_unicode_output() -> bool:
    """检查当前终端是否支持 Unicode 输出（避免 GBK 终端 emoji 崩溃）"""
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        "✅❌📊".encode(encoding)
    except (LookupError, UnicodeEncodeError):
        return False
    return True


@click.group(name="vartable")
def vartable_group() -> None:
    """变量表管理 - 解析/编码检测（V2.3 吸收 SW-2026-001）"""


@vartable_group.command(name="parse")
@click.option("--format", "fmt", type=click.Choice(["table", "json"]), default="table", help="输出格式")
@click.argument("file_path", type=click.Path(exists=True, dir_okay=False, resolve_path=True))
def parse_command(file_path: str, fmt: str) -> None:
    """解析 io_points.csv 文件，输出变量条目详情。

    FILE_PATH: io_points.csv 文件路径

    示例：
    auto-pm vartable parse path/to/io_points.csv
    auto-pm vartable parse path/to/io_points.csv --format json
    """
    parser = IoPointsParser()
    result = parser.parse(file_path)

    if fmt == "json":
        # JSON 输出禁止任何非 JSON 文本污染 stdout（日志走 stderr）
        click.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return

    # 表格输出
    if not result.success:
        console.print("[red]解析失败[/red]")
        for err in result.errors:
            console.print(
                f"  [red]L{err.line_number}[/red] {err.field}: {err.message}"
            )
        raise SystemExit(1)

    assert result.var_table is not None
    table = result.var_table

    # 概要
    icon_ok = "✅" if _supports_unicode_output() else "[OK]"
    console.print(f"{icon_ok} 解析完成: {table.total_count} 条变量")
    console.print(f"   源文件: {table.source_path}")
    console.print(f"   编码: {table.encoding}")
    console.print(f"   站点: {', '.join(table.stations)}")
    console.print(f"   信号类型: {', '.join(table.signal_types)}")
    if result.warnings:
        for w in result.warnings:
            console.print(f"   [yellow]警告: {w}[/yellow]")
    if result.errors:
        console.print(f"   [yellow]跳过错误行: {result.error_count} 个[/yellow]")

    # 详细表格 - 使用宽 console 避免 Tag 被截断
    detail_table = Table(title="变量条目详情", expand=True)
    detail_table.add_column("行号", style="cyan", justify="right", no_wrap=True)
    detail_table.add_column("站点", style="magenta", no_wrap=True)
    detail_table.add_column("类型", style="yellow", no_wrap=True)
    detail_table.add_column("地址", style="green", no_wrap=True)
    detail_table.add_column("Tag", style="white", overflow="fold")
    detail_table.add_column("信号名", style="white", overflow="fold")
    detail_table.add_column("设备", style="dim", overflow="fold")
    detail_table.add_column("注释", style="dim", overflow="fold")

    for entry in table.entries:
        detail_table.add_row(
            str(entry.line_number),
            entry.station,
            entry.signal_type,
            entry.address,
            entry.tag,
            entry.signal_name,
            entry.device,
            entry.comment,
        )

    # 用宽 console 打印表格,避免 Rich 在窄终端下截断 Tag/信号名
    wide_console = Console(width=max(console.width, 200))
    wide_console.print(detail_table)


@vartable_group.command(name="detect-encoding")
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text", help="输出格式")
@click.argument("file_path", type=click.Path(exists=True, dir_okay=False, resolve_path=True))
def detect_encoding_command(file_path: str, fmt: str) -> None:
    """检测文件编码。

    FILE_PATH: 待检测文件路径

    示例：
    auto-pm vartable detect-encoding path/to/io_points.csv
    auto-pm vartable detect-encoding path/to/file --format json
    """
    try:
        encoding = detect_encoding(file_path)
    except FileNotFoundError as exc:
        if fmt == "json":
            click.echo(json.dumps({"error": str(exc)}, ensure_ascii=False))
        else:
            console.print(f"[red]错误: {exc}[/red]")
        raise SystemExit(1) from exc

    if fmt == "json":
        click.echo(
            json.dumps(
                {"file": file_path, "encoding": encoding},
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    icon = "✅" if _supports_unicode_output() else "[OK]"
    console.print(f"{icon} 文件编码检测结果")
    console.print(f"   文件: {file_path}")
    console.print(f"   编码: [green]{encoding}[/green]")


@vartable_group.command(name="list-encodings")
def list_encodings_command() -> None:
    """列出支持的编码列表"""
    console.print("[bold]支持的编码列表[/bold]")
    for enc in SUPPORTED_ENCODINGS:
        console.print(f"  - {enc}")
