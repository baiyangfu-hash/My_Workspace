from __future__ import annotations

from pathlib import Path

import click


def resolve_workspace(ctx: click.Context) -> Path:
    """从 click 上下文中解析工作空间路径。

    兼容两种上下文对象：
    - specmgr 风格：ctx.obj 为 dict，包含 "workspace" 键
    - auto_pm 风格：ctx.obj 为 AppContext，包含 workspace_root 属性
    """
    obj = ctx.obj
    ws: str | None = None
    if isinstance(obj, dict):
        ws = obj.get("workspace")
    else:
        ws = getattr(obj, "workspace_root", None)
    if not ws:
        raise click.UsageError("缺少工作空间路径，请使用 -w 或 --workspace 指定")
    p = Path(ws)
    if not p.exists():
        raise click.UsageError(f"工作空间路径不存在: {ws}")
    return p.resolve()
