"""pm-mgr CLI - pm-workflow project management toolchain."""

from __future__ import annotations

import click
from pm_mgr import __version__


@click.group()
@click.version_option(version=__version__)
@click.option("--workspace", "-w", envvar="PM_MGR_WORKSPACE", help="工作空间根目录")
@click.pass_context
def cli(ctx: click.Context, workspace: str | None) -> None:
    """pm-mgr - pm-workflow 项目工作流工具链 CLI

    支持项目初始化、旧项目补完、健康检查、类型检测、Spec Snapshot 管理。
    """
    ctx.ensure_object(dict)
    ctx.obj["workspace"] = workspace


@cli.command()
@click.argument("project_dir", type=click.Path())
@click.option("--type", "-t", "project_type", type=click.Choice(["software", "plc", "sys"]), required=True, help="项目类型")
@click.option("--id", "-i", "project_id", required=True, help="项目编号 (如 SW-2026-001)")
@click.option("--name", "-n", "project_name", required=True, help="项目名称")
@click.option("--owner", "-o", default="Pending", help="项目负责人")
@click.option("--oneliner", "-l", default="Pending", help="项目一句话描述")
@click.option("--force", "-f", is_flag=True, help="强制初始化（目录非空时仍执行）")
@click.pass_context
def init(
    ctx: click.Context,
    project_dir: str,
    project_type: str,
    project_id: str,
    project_name: str,
    owner: str,
    oneliner: str,
    force: bool,
) -> None:
    """初始化新项目骨架。

    从 .trae/project-bootstrap/ 模板创建完整项目结构。
    """
    workspace = _resolve_workspace(ctx)

    try:
        from .bootstrap import init_project
        created = init_project(
            project_root=project_dir,
            project_type=project_type,
            project_id=project_id,
            project_name=project_name,
            workspace_root=workspace,
            owner=owner,
            one_liner=oneliner,
            force=force,
        )
        click.echo(f"\n项目初始化完成: {project_dir}")
        click.echo(f"  类型: {project_type}")
        click.echo(f"  创建/更新 {len(created)} 个文件/目录")
    except FileExistsError as e:
        click.echo(f"错误: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"初始化失败: {e}", err=True)
        raise SystemExit(1)


@cli.command()
@click.argument("project_dir", type=click.Path(exists=True))
@click.option("--force", "-f", is_flag=True, help="强制补完（跳过生命周期检查）")
@click.pass_context
def retrofit(ctx: click.Context, project_dir: str, force: bool) -> None:
    """为已有项目注入连续性机制（仅添加 hooks + handoffs + Spec Snapshot）。

    不会修改现有目录结构和文件内容。
    """
    workspace = _resolve_workspace(ctx)

    try:
        from .retrofit import retrofit_project
        created = retrofit_project(
            project_root=project_dir,
            workspace_root=workspace,
            force=force,
        )
        if created:
            click.echo(f"\n补完成功: {project_dir}")
            click.echo(f"  注入 {len(created)} 项")
        else:
            click.echo(f"\n无需补完: {project_dir}")
    except Exception as e:
        click.echo(f"补完失败: {e}", err=True)
        raise SystemExit(1)


@cli.command()
@click.argument("project_dir", type=click.Path(exists=True))
def detect(project_dir: str) -> None:
    """检测项目类型 (software / plc / sys / unknown)。"""
    try:
        from .detect import detect_project_type
        result = detect_project_type(project_dir)
        if result:
            click.echo(result)
        else:
            click.echo("unknown")
    except Exception as e:
        click.echo(f"检测失败: {e}", err=True)
        raise SystemExit(1)


@cli.command()
@click.argument("project_dir", type=click.Path(exists=True))
@click.option("--fix", is_flag=True, help="自动修复缺失项")
@click.pass_context
def check(ctx: click.Context, project_dir: str, fix: bool) -> None:
    """检查项目连续性健康状态。"""
    try:
        from .check import check_project
        report = check_project(project_dir)
        click.echo(report.format())

        if fix and report.failed:
            click.echo("\n尝试自动修复...")
            workspace = _resolve_workspace(ctx)
            from .retrofit import retrofit_project
            created = retrofit_project(
                project_root=project_dir,
                workspace_root=workspace,
                force=True,
            )
            if created:
                click.echo(f"  修复 {len(created)} 项")
                report2 = check_project(project_dir)
                click.echo(f"\n修复后:\n{report2.format()}")

    except Exception as e:
        click.echo(f"检查失败: {e}", err=True)
        raise SystemExit(1)


@cli.command()
@click.argument("project_dir", type=click.Path(exists=True))
@click.pass_context
def snapshot(ctx: click.Context, project_dir: str) -> None:
    """刷新项目的 Spec Snapshot。"""
    try:
        from pathlib import Path
        from .detect import detect_project_type
        from .snapshot import update_pm_session_snapshot

        root = Path(project_dir).resolve()
        workspace = _resolve_workspace(ctx)
        project_type = detect_project_type(root)

        if not project_type:
            click.echo("错误: 无法检测项目类型", err=True)
            raise SystemExit(1)

        pm_sessions = list(root.glob("PM_SESSION*.md"))
        if not pm_sessions:
            click.echo("错误: 未找到 PM_SESSION 文件", err=True)
            raise SystemExit(1)

        updated = update_pm_session_snapshot(
            pm_sessions[0],
            project_type,
            workspace,
        )
        if updated:
            click.echo(f"Spec Snapshot 已刷新: {project_type}")
        else:
            click.echo("Spec Snapshot 无需更新")
    except Exception as e:
        click.echo(f"刷新失败: {e}", err=True)
        raise SystemExit(1)


def _resolve_workspace(ctx: click.Context) -> str:
    """Resolve workspace root from CLI option or auto-detect."""
    workspace = ctx.obj.get("workspace")
    if workspace:
        return workspace

    # Auto-detect from current directory upward
    import os
    cwd = os.getcwd()
    path = cwd
    while True:
        if os.path.isdir(os.path.join(path, ".trae")):
            return path
        parent = os.path.dirname(path)
        if parent == path:
            break
        path = parent

    # Fallback: use the project's known parent structure
    raise click.UsageError(
        "无法自动检测工作空间根目录。请使用 -w/--workspace 指定。\n"
        "工作空间根目录应包含 .trae/ 目录。"
    )
