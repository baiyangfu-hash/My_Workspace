from __future__ import annotations

from pathlib import Path

import click


def resolve_workspace(ctx: click.Context) -> Path:
    ws = ctx.obj.get("workspace")
    if not ws:
        raise click.UsageError("缺少工作空间路径，请使用 -w 或 --workspace 指定")
    p = Path(ws)
    if not p.exists():
        raise click.UsageError(f"工作空间路径不存在: {ws}")
    return p.resolve()
