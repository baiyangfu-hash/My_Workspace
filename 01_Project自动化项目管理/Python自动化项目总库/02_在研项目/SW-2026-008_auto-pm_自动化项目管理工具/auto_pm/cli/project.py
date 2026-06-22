"""project 子命令组 - 项目 CRUD

Commands:
    list                          列出工作空间内所有项目
    create --stack --id --name    创建新项目（调用 Copier 模板）
    show <ID> [--json]            查看项目详情
    edit <ID> [--phase] [--desc]  编辑项目元数据
    delete <ID> --confirm         删除项目
    retrofit <ID>                 补全 .copier-answers.yml 元数据文件
    import <PATH> [--move]        导入外部项目目录到工作空间
"""

from __future__ import annotations

import json
import os
import shutil

import click
from rich.console import Console
from rich.table import Table
from yaml import dump as yaml_dump

from auto_pm.app_context import AppContext
from auto_pm.core.constants import get_template_name
from auto_pm.core.paths import WORKSPACE_PROJECTS_SUBDIR
from auto_pm.core.project_service import ProjectService
from auto_pm.core.template_service import TemplateService

console = Console()


@click.group(name="project")
@click.pass_context
def project_group(ctx: click.Context) -> None:
    """项目管理 - 列表/创建/查看/编辑/删除"""


@project_group.command(name="list")
@click.option(
    "--business-line",
    "-bl",
    type=click.Choice(["SW", "DJ", "ZD", "XT", "WX"]),
    default=None,
    help="按业务线筛选（从项目编号前缀提取）",
)
@click.option(
    "--stack",
    type=click.Choice(["plc", "python", "unknown"]),
    default=None,
    help="按技术栈筛选",
)
@click.option(
    "--phase",
    type=click.Choice(["developing", "commissioning", "production", "archived", ""]),
    default=None,
    help="按项目阶段筛选",
)
@click.option(
    "--search",
    default=None,
    help="关键字搜索（匹配项目编号/名称/描述）",
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="以JSON格式输出结果",
)
@click.pass_context
def cmd_list(
    ctx: click.Context,
    business_line: str | None,
    stack: str | None,
    phase: str | None,
    search: str | None,
    output_json: bool,
) -> None:
    """列出工作空间内所有项目"""
    app_ctx: AppContext = ctx.obj
    svc = ProjectService(app_ctx.workspace_root)
    projects = svc.list_projects()

    if business_line is not None:
        projects = [
            p for p in projects
            if p.project_id.split("-", 1)[0] == business_line
        ]
    if stack is not None:
        projects = [p for p in projects if p.stack == stack]
    if phase is not None:
        projects = [p for p in projects if p.phase == phase]
    if search is not None:
        search_lower = search.lower()
        projects = [
            p for p in projects
            if search_lower in p.project_id.lower()
            or search_lower in p.name.lower()
            or search_lower in p.description.lower()
        ]

    if not projects:
        if output_json:
            click.echo("[]")
        else:
            console.print("[yellow]未发现项目[/yellow]")
        return

    if output_json:
        click.echo(json.dumps([p.model_dump() for p in projects], ensure_ascii=False, indent=2))
        return

    table = Table(title=f"项目列表 ({len(projects)} 个)")
    table.add_column("项目ID", style="cyan")
    table.add_column("名称", style="white")
    table.add_column("技术栈", style="green")
    table.add_column("版本", style="yellow")
    table.add_column("阶段", style="magenta")
    table.add_column("业务线", style="blue")
    table.add_column("来源", style="dim")
    table.add_column("路径", style="dim")

    for p in projects:
        table.add_row(
            p.project_id,
            p.name,
            p.stack,
            p.version,
            p.phase or "-",
            p.business_line or "-",
            p.source,
            os.path.relpath(p.path, app_ctx.workspace_root),
        )

    console.print(table)


@project_group.command(name="create")
@click.option("--stack", type=click.Choice(["plc", "python"]), required=True, help="技术栈")
@click.option("--id", "project_id", required=True, help="项目编号（如 DJ-2026-010）")
@click.option("--name", "project_name", required=True, help="项目名称")
@click.option("--desc", "description", default="", help="项目描述")
@click.option(
    "--business-line",
    "-bl",
    type=click.Choice(["SW", "DJ", "ZD", "XT", "WX"]),
    default=None,
    help="指定业务线（默认从项目编号前缀推断，不一致时警告）",
)
@click.option(
    "--mode",
    type=click.Choice(["shared-library", "test-suite", "standard-project"]),
    default="standard-project",
    help="PLC 项目模式（仅 --stack=plc 时有效）",
)
@click.option("--dry-run", is_flag=True, help="仅预览，不实际创建")
@click.pass_context
def cmd_create(
    ctx: click.Context,
    stack: str,
    project_id: str,
    project_name: str,
    description: str,
    business_line: str | None,
    mode: str,
    dry_run: bool,
) -> None:
    """创建新项目（调用 Copier 模板生成骨架）"""
    app_ctx: AppContext = ctx.obj

    # 业务线校验：若指定 --business-line，检查与项目编号前缀是否一致
    if business_line is not None:
        inferred = project_id.split("-", 1)[0] if "-" in project_id else ""
        if inferred != business_line:
            console.print(
                f"[yellow]提示: 指定业务线 {business_line} 与项目编号前缀 {inferred} 不一致[/yellow]"
            )

    # 根据技术栈选择模板（M3-Iter7: 统一从 core.constants 读取；H-2: 支持 mode 参数）
    template_name = get_template_name(stack, mode if stack == "plc" else "")

    # 目标路径
    project_dir = f"{project_id}_{project_name}"
    dest_path = os.path.join(app_ctx.workspace_root, project_dir)

    if os.path.exists(dest_path):
        console.print(f"[red]错误: 目标路径已存在: {dest_path}[/red]")
        ctx.exit(1)

    if dry_run:
        console.print(f"[yellow][DRY-RUN] 将创建项目: {dest_path}[/yellow]")
        console.print(f"  模板: {template_name}")
        console.print(f"  编号: {project_id}")
        console.print(f"  名称: {project_name}")
        return

    # 调用 Copier 模板
    tpl_svc = TemplateService(app_ctx.templates_dir)
    data = {
        "project_id": project_id,
        "project_name": project_name,
        "description": description or project_name,
        "version": "V1.0.0",
    }

    try:
        tpl_svc.copy_template(template_name, dest_path, data)
        console.print(f"[green]项目创建成功: {dest_path}[/green]")
        console.print(f"  项目编号: {project_id}")
        console.print(f"  项目名称: {project_name}")
        console.print(f"  技术栈: {stack}")
    except FileNotFoundError as e:
        console.print(f"[red]错误: 模板不存在 - {e}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]创建失败: {e}[/red]")
        ctx.exit(1)


@project_group.command(name="show")
@click.argument("project_id")
@click.option("--json", "output_json", is_flag=True, help="以JSON格式输出结果")
@click.pass_context
def cmd_show(ctx: click.Context, project_id: str, output_json: bool) -> None:
    """查看项目详情"""
    app_ctx: AppContext = ctx.obj
    svc = ProjectService(app_ctx.workspace_root)
    proj = svc.get_project(project_id)

    if proj is None:
        console.print(f"[red]错误: 项目不存在: {project_id}[/red]")
        ctx.exit(1)

    if output_json:
        click.echo(json.dumps(proj.model_dump(), ensure_ascii=False, indent=2))
    else:
        console.print(f"[cyan]项目ID:[/cyan] {proj.project_id}")
        console.print(f"[cyan]名称:[/cyan]   {proj.name}")
        console.print(f"[cyan]技术栈:[/cyan] {proj.stack}")
        console.print(f"[cyan]版本:[/cyan]   {proj.version}")
        console.print(f"[cyan]描述:[/cyan]   {proj.description}")
        console.print(f"[cyan]来源:[/cyan]   {proj.source}")
        console.print(f"[cyan]路径:[/cyan]   {proj.path}")


@project_group.command(name="edit")
@click.argument("project_id")
@click.option("--phase", default=None, help="更新项目阶段")
@click.option("--desc", "description", default=None, help="更新项目描述")
@click.option("--version", default=None, help="更新项目版本")
@click.option(
    "--business-line",
    "-bl",
    type=click.Choice(["SW", "DJ", "ZD", "XT", "WX"]),
    default=None,
    help="更新业务线（写入 .copier-answers.yml 覆盖从编号前缀提取的值）",
)
@click.pass_context
def cmd_edit(
    ctx: click.Context,
    project_id: str,
    phase: str | None,
    description: str | None,
    version: str | None,
    business_line: str | None,
) -> None:
    """编辑项目元数据（写入 .copier-answers.yml）"""
    app_ctx: AppContext = ctx.obj
    svc = ProjectService(app_ctx.workspace_root)

    kwargs: dict[str, str] = {}
    if phase is not None:
        kwargs["phase"] = phase
    if description is not None:
        kwargs["description"] = description
    if version is not None:
        kwargs["version"] = version
    if business_line is not None:
        kwargs["business_line"] = business_line

    if not kwargs:
        console.print("[yellow]未指定更新字段（使用 --phase/--desc/--version/--business-line）[/yellow]")
        return

    try:
        svc.update_project_meta(project_id, **kwargs)
        console.print(f"[green]项目元数据已更新: {project_id}[/green]")
        console.print(f"  更新字段: {', '.join(kwargs.keys())}")
    except FileNotFoundError as e:
        console.print(f"[red]错误: {e}[/red]")
        ctx.exit(1)


@project_group.command(name="delete")
@click.argument("project_id")
@click.option("--confirm", is_flag=True, help="确认删除（破坏性操作）")
@click.pass_context
def cmd_delete(ctx: click.Context, project_id: str, confirm: bool) -> None:
    """删除项目（破坏性操作，需 --confirm）"""
    app_ctx: AppContext = ctx.obj
    svc = ProjectService(app_ctx.workspace_root)
    proj = svc.get_project(project_id)

    if proj is None:
        console.print(f"[red]错误: 项目不存在: {project_id}[/red]")
        ctx.exit(1)

    if not confirm:
        console.print(f"[yellow]警告: 即将删除项目: {proj.path}[/yellow]")
        console.print("[yellow]请使用 --confirm 确认删除[/yellow]")
        ctx.exit(1)

    try:
        shutil.rmtree(proj.path)
        console.print(f"[green]项目已删除: {proj.path}[/green]")
    except OSError as e:
        console.print(f"[red]删除失败: {e}[/red]")
        ctx.exit(1)


@project_group.command(name="retrofit")
@click.argument("project_id")
@click.pass_context
def cmd_retrofit(ctx: click.Context, project_id: str) -> None:
    """为已有项目补全元数据文件（.copier-answers.yml 及 PLC 标志文件）"""
    app_ctx: AppContext = ctx.obj
    svc = ProjectService(app_ctx.workspace_root)
    proj = svc.get_project(project_id)

    if proj is None:
        console.print(f"[red]错误: 项目不存在: {project_id}[/red]")
        ctx.exit(1)

    # 1. 补全 .copier-answers.yml
    copier_answers_path = os.path.join(proj.path, ".copier-answers.yml")
    if os.path.isfile(copier_answers_path):
        console.print("[yellow]项目已有 .copier-answers.yml，跳过[/yellow]")
    else:
        # Generate .copier-answers.yml content
        # M3-Iter7: 统一从 core.constants 读取模板名映射
        template_name = get_template_name(proj.stack)
        content = {
            "_commit": "HEAD",
            "_src_path": f"templates/{template_name}",
            "project_id": proj.project_id,
            "project_name": proj.name,
            "description": proj.description,
            "version": proj.version,
        }
        try:
            with open(copier_answers_path, "w", encoding="utf-8") as f:
                yaml_dump(content, f, default_flow_style=False, allow_unicode=True)
            console.print(f"[green].copier-answers.yml 已创建: {copier_answers_path}[/green]")
        except Exception as e:
            console.print(f"[red]创建 .copier-answers.yml 失败: {e}[/red]")
            ctx.exit(1)

    # 2. 对 PLC 项目，补全标志文件（.plc.json/PM_SESSION/PRD）
    # H-8: 使用 PlcService 层而非直接调用 PlcRepairer（遵循 Phase 1 的 C-3 修复原则）
    if proj.stack == "plc":
        try:
            from auto_pm.plc.service import PlcService

            plc_svc = PlcService(app_ctx.workspace_root)
            repair_result = plc_svc.repair(proj.path, dry_run=False)
            console.print(
                f"[green]PLC 标志文件补全完成: "
                f"fixed={repair_result.fixed_count}, "
                f"skipped={repair_result.skipped_count}[/green]"
            )
        except Exception as e:
            console.print(f"[red]PLC 标志文件补全失败: {e}[/red]")


_PROJECTS_SUBDIR = WORKSPACE_PROJECTS_SUBDIR  # M3-Iter6: 从 core.paths 读取


@project_group.command(name="import")
@click.argument("path", type=click.Path(exists=True, file_okay=False))
@click.option("--move", is_flag=True, help="移动而非复制（默认复制）")
@click.option("--force", is_flag=True, help="强制覆盖已存在的目标目录")
@click.option(
    "--business-line",
    "-bl",
    type=click.Choice(["SW", "DJ", "ZD", "XT", "WX"]),
    default=None,
    help="指定业务线（默认从项目编号前缀推断）",
)
@click.pass_context
def cmd_import(
    ctx: click.Context,
    path: str,
    move: bool,
    force: bool,
    business_line: str | None,
) -> None:
    """导入外部项目目录到工作空间的 02_在研项目/ 下"""
    app_ctx: AppContext = ctx.obj
    source_path = os.path.abspath(path)
    dirname = os.path.basename(source_path)
    dest_path = os.path.join(app_ctx.workspace_root, _PROJECTS_SUBDIR, dirname)

    if os.path.exists(dest_path):
        if not force:
            console.print(f"[red]错误: 目标路径已存在: {dest_path}（使用 --force 覆盖）[/red]")
            ctx.exit(1)
        console.print(f"[yellow]强制覆盖: {dest_path}[/yellow]")
        shutil.rmtree(dest_path, ignore_errors=True)

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    try:
        if move:
            shutil.move(source_path, dest_path)
            console.print(f"[green]项目已移动: {dest_path}[/green]")
        else:
            shutil.copytree(source_path, dest_path)
            console.print(f"[green]项目已复制: {dest_path}[/green]")
    except OSError as e:
        console.print(f"[red]导入失败: {e}[/red]")
        ctx.exit(1)

    # 导入后补全 .copier-answers.yml（如果仍缺少）
    svc = ProjectService(app_ctx.workspace_root)
    try:
        svc.retrofit_project_by_path(dest_path)
        console.print("[green].copier-answers.yml 已补全[/green]")
    except FileExistsError:
        pass  # 已有 .copier-answers.yml，正常
    except Exception as e:
        console.print(f"[yellow]补全元数据失败: {e}[/yellow]")

    project_id = ProjectService._extract_id_from_dirname(dest_path)
    if business_line is not None:
        inferred = project_id.split("-", 1)[0] if "-" in project_id else ""
        if inferred != business_line:
            console.print(
                f"[yellow]提示: 指定业务线 {business_line} 与项目编号前缀 {inferred} 不一致[/yellow]"
            )

    console.print(f"  项目编号: {project_id}")
    console.print(f"  导入路径: {dest_path}")

    # 同步到 DB 缓存（如果 DB 已存在）
    db_path = os.path.join(app_ctx.workspace_root, ".auto-pm", "index.db")
    if os.path.isfile(db_path):
        try:
            from auto_pm.db.connection import DatabaseManager

            db = DatabaseManager(db_path)
            db.init_schema()
            svc_with_db = ProjectService(app_ctx.workspace_root, db=db)
            svc_with_db.sync_to_cache(force_full=True)
            console.print("[green]DB 缓存已同步[/green]")
        except Exception as e:
            console.print(f"[yellow]DB 缓存同步失败（不影响导入）: {e}[/yellow]")
