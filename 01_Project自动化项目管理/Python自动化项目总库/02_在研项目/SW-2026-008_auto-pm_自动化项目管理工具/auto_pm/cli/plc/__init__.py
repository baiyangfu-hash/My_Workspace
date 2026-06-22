"""plc 子命令组 - PLC 项目管理（LSP-907）

Commands:
    init <ID>                    创建 PLC 项目骨架（Copier 模板）
    check <ID>                   检查项目结构（LSP-907）
    check --all                  检查工作空间所有项目
    repair <ID> [--rename]       自动修复项目结构
    standardize <ID> [--apply]   文档命名标准化
"""

from __future__ import annotations

import json
import os

import click
from rich.console import Console
from rich.table import Table

from auto_pm.app_context import AppContext
from auto_pm.core.project_service import ProjectService
from auto_pm.core.template_service import TemplateService
from auto_pm.plc.checker import PlcChecker
from auto_pm.plc.models import CheckResult
from auto_pm.plc.repairer import PlcRepairer

console = Console()


@click.group(name="plc")
@click.pass_context
def plc_group(ctx: click.Context) -> None:
    """PLC 项目管理 - 初始化/检查/修复/标准化（LSP-907）"""


@plc_group.command(name="init")
@click.argument("project_id")
@click.option("--name", "project_name", required=True, help="项目名称")
@click.option("--desc", "description", default="", help="项目描述")
@click.pass_context
def cmd_init(
    ctx: click.Context, project_id: str, project_name: str, description: str
) -> None:
    """创建 PLC 项目骨架（调用 Copier plc-standard 模板）"""
    app_ctx: AppContext = ctx.obj

    project_dir = f"{project_id}_{project_name}"
    dest_path = os.path.join(app_ctx.workspace_root, project_dir)

    if os.path.exists(dest_path):
        console.print(f"[red]错误: 目标路径已存在: {dest_path}[/red]")
        ctx.exit(1)

    tpl_svc = TemplateService(app_ctx.templates_dir)
    data = {
        "project_id": project_id,
        "project_name": project_name,
        "description": description or project_name,
        "version": "V1.0.0",
    }

    try:
        tpl_svc.copy_template("plc-standard", dest_path, data)
        console.print(f"[green]PLC 项目创建成功: {dest_path}[/green]")
    except FileNotFoundError as e:
        console.print(f"[red]错误: 模板不存在 - {e}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]创建失败: {e}[/red]")
        ctx.exit(1)


@plc_group.command(name="check")
@click.argument("project_id", required=False)
@click.option("--all", "check_all", is_flag=True, help="检查工作空间所有项目")
@click.option("--json", "output_json", is_flag=True, help="以JSON格式输出结果")
@click.pass_context
def cmd_check(
    ctx: click.Context, project_id: str | None, check_all: bool, output_json: bool
) -> None:
    """检查项目结构是否符合 LSP-907 规范"""
    app_ctx: AppContext = ctx.obj
    checker = PlcChecker(app_ctx.workspace_root)

    if check_all:
        results = checker.check_workspace()
        if not results:
            if output_json:
                print(json.dumps([], ensure_ascii=False, indent=2))
            else:
                console.print("[yellow]未发现 PLC 项目[/yellow]")
            return
        if output_json:
            print(json.dumps([r.model_dump() for r in results], ensure_ascii=False, indent=2))
        else:
            _print_check_summary(results)
        return

    if not project_id:
        console.print("[red]错误: 请指定项目ID 或使用 --all[/red]")
        ctx.exit(1)

    # 查找项目路径
    proj_svc = ProjectService(app_ctx.workspace_root)
    proj = proj_svc.get_project(project_id)
    if proj is None:
        console.print(f"[red]错误: 项目不存在: {project_id}[/red]")
        ctx.exit(1)

    result = checker.check_project(proj.path)
    if output_json:
        print(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))
    else:
        _print_check_detail(result)


@plc_group.command(name="repair")
@click.argument("project_id")
@click.option("--rename", "rename_confirm", is_flag=True, help="确认文件重命名（破坏性操作）")
@click.option("--dry-run", is_flag=True, help="仅预览不执行")
@click.pass_context
def cmd_repair(
    ctx: click.Context, project_id: str, rename_confirm: bool, dry_run: bool
) -> None:
    """自动修复项目结构问题"""
    app_ctx: AppContext = ctx.obj

    proj_svc = ProjectService(app_ctx.workspace_root)
    proj = proj_svc.get_project(project_id)
    if proj is None:
        console.print(f"[red]错误: 项目不存在: {project_id}[/red]")
        ctx.exit(1)

    repairer = PlcRepairer(app_ctx.workspace_root)
    result = repairer.repair_project(
        proj.path, dry_run=dry_run, rename_confirm=rename_confirm
    )

    _print_repair_result(result)


@plc_group.command(name="standardize")
@click.argument("project_id")
@click.option("--apply", is_flag=True, help="执行重命名（默认仅预览）")
@click.pass_context
def cmd_standardize(
    ctx: click.Context, project_id: str, apply: bool
) -> None:
    """检测并修正 PRD 文档命名"""
    app_ctx: AppContext = ctx.obj

    proj_svc = ProjectService(app_ctx.workspace_root)
    proj = proj_svc.get_project(project_id)
    if proj is None:
        console.print(f"[red]错误: 项目不存在: {project_id}[/red]")
        ctx.exit(1)

    repairer = PlcRepairer(app_ctx.workspace_root)
    result = repairer.standardize_docs(proj.path, apply=apply)

    if not result.plans:
        console.print("[green]无需标准化：所有文档命名已符合规范[/green]")
        return

    table = Table(title=f"文档标准化结果 ({'已执行' if apply else '仅预览'})")
    table.add_column("原文件名", style="red")
    table.add_column("标准文件名", style="green")
    table.add_column("类型", style="cyan")
    table.add_column("状态", style="yellow")

    for plan in result.plans:
        status = "已重命名" if plan.applied else "待确认"
        table.add_row(
            os.path.basename(plan.old_path),
            os.path.basename(plan.new_path),
            plan.doc_type,
            status,
        )

    console.print(table)
    if not apply and result.plans:
        console.print("[yellow]使用 --apply 执行重命名[/yellow]")


# ── 输出辅助 ──────────────────────────────────────────────

def _print_check_summary(results: list[CheckResult]) -> None:
    """打印批量检查摘要"""
    table = Table(title=f"PLC 项目检查摘要 ({len(results)} 个)")
    table.add_column("项目", style="cyan")
    table.add_column("类型", style="dim")
    table.add_column("Pass", style="green", justify="right")
    table.add_column("Warn", style="yellow", justify="right")
    table.add_column("Fail", style="red", justify="right")
    table.add_column("状态", style="bold")

    total_pass = 0
    for r in results:
        status = "[green]PASS[/green]" if r.all_pass else "[red]FAIL[/red]"
        if r.all_pass:
            total_pass += 1
        table.add_row(
            os.path.basename(r.project_path),
            r.project_type,
            str(r.pass_count),
            str(r.warn_count),
            str(r.fail_count),
            status,
        )

    console.print(table)
    console.print(
        f"\n合计: {len(results)} 个项目, {total_pass} 个 PASS, "
        f"{len(results) - total_pass} 个 FAIL"
    )


def _print_check_detail(result: CheckResult) -> None:
    """打印单项目检查详情"""
    title = f"检查结果: {os.path.basename(result.project_path)}"
    table = Table(title=title)
    table.add_column("检查项", style="cyan")
    table.add_column("状态", style="bold")
    table.add_column("说明", style="white")

    for item in result.items:
        if item.status == "pass":
            status_str = "[green]PASS[/green]"
        elif item.status == "warn":
            status_str = "[yellow]WARN[/yellow]"
        else:
            status_str = "[red]FAIL[/red]"
        table.add_row(item.item, status_str, item.message)

    console.print(table)
    console.print(
        f"\nPass={result.pass_count} "
        f"Warn={result.warn_count} "
        f"Fail={result.fail_count} "
        f"-> {'[green]ALL PASS[/green]' if result.all_pass else '[red]HAS FAIL[/red]'}"
    )


def _print_repair_result(result) -> None:
    """打印修复结果"""
    table = Table(title=f"修复结果: {os.path.basename(result.project_path)}")
    table.add_column("修复项", style="cyan")
    table.add_column("动作", style="white")
    table.add_column("破坏性", style="dim")
    table.add_column("状态", style="bold")
    table.add_column("说明", style="dim")

    for action in result.actions:
        if action.status == "fixed":
            status_str = "[green]FIXED[/green]"
        elif action.status == "skipped":
            status_str = "[yellow]SKIPPED[/yellow]"
        else:
            status_str = "[red]FAILED[/red]"
        destructive = "是" if action.destructive else "否"
        table.add_row(
            action.item, action.action, destructive, status_str, action.detail
        )

    console.print(table)
    console.print(
        f"\nFixed={result.fixed_count} "
        f"Skipped={result.skipped_count} "
        f"Failed={result.failed_count}"
    )

    if result.after_check is not None:
        console.print(
            f"修复后检查: Pass={result.after_check.pass_count} "
            f"Warn={result.after_check.warn_count} "
            f"Fail={result.after_check.fail_count} "
            f"-> {'[green]ALL PASS[/green]' if result.after_check.all_pass else '[red]HAS FAIL[/red]'}"
        )
