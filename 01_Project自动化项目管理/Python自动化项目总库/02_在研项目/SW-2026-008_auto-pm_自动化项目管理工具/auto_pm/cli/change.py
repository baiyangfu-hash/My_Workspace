"""change 子命令组 - 变更单 CRUD + 状态流转

Commands:
    list <PID>                          列出项目变更单
    show <CHG-NUM>                      查看变更单详情
    create --pid --domain ...           创建变更单
    transition <CHG-NUM> --to <STATUS>  状态流转
"""

from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

from auto_pm.app_context import AppContext
from auto_pm.change.change_service import ChangeService
from auto_pm.change.models import (
    ALL_STATUSES,
    BUSINESS_NATURES,
    DOMAINS,
    IMPACT_SCOPES,
    STATUS_LABELS,
    URGENCY_LEVELS,
)

console = Console()

# click.Choice 选项（从规范常量动态生成）
_DOMAIN_CHOICES = list(DOMAINS.keys())
_NATURE_CHOICES = list(BUSINESS_NATURES.keys())
_SCOPE_CHOICES = list(IMPACT_SCOPES.keys())
_URGENCY_CHOICES = list(URGENCY_LEVELS.keys())
_STATUS_CHOICES = sorted(ALL_STATUSES)


@click.group(name="change")
@click.pass_context
def change_group(ctx: click.Context) -> None:
    """变更管理 - 变更单创建/查询/状态流转"""


@change_group.command(name="list")
@click.argument("project_id")
@click.option("--status", type=click.Choice(_STATUS_CHOICES), default=None, help="按状态筛选")
@click.option("--domain", type=click.Choice(_DOMAIN_CHOICES), default=None, help="按领域筛选")
@click.pass_context
def cmd_list(
    ctx: click.Context,
    project_id: str,
    status: str | None,
    domain: str | None,
) -> None:
    """列出项目变更单"""
    app_ctx: AppContext = ctx.obj
    svc = ChangeService(app_ctx.workspace_root)
    summaries = svc.list_change_requests(project_id, status=status, domain=domain)

    if not summaries:
        console.print("[yellow]未发现变更单[/yellow]")
        return

    table = Table(title=f"变更单列表 ({len(summaries)} 条) - 项目 {project_id}")
    table.add_column("变更编号", style="cyan")
    table.add_column("领域", style="green")
    table.add_column("性质", style="blue")
    table.add_column("影响范围", style="magenta")
    table.add_column("状态", style="yellow")
    table.add_column("申请人", style="white")
    table.add_column("申请日期", style="dim")
    table.add_column("标题", style="white")

    for s in summaries:
        table.add_row(
            s.change_number,
            s.domain,
            s.business_nature,
            ",".join(s.impact_scope),
            STATUS_LABELS.get(s.status, s.status),
            s.applicant,
            s.apply_date,
            s.title,
        )

    console.print(table)


@change_group.command(name="show")
@click.argument("change_number")
@click.pass_context
def cmd_show(ctx: click.Context, change_number: str) -> None:
    """查看变更单详情"""
    app_ctx: AppContext = ctx.obj
    svc = ChangeService(app_ctx.workspace_root)
    cr = svc.get_change_request(change_number)

    if cr is None:
        console.print(f"[red]错误: 变更单不存在: {change_number}[/red]")
        ctx.exit(1)

    console.print(f"[cyan]变更编号:[/cyan] {cr.change_number}")
    console.print(f"[cyan]项目编号:[/cyan] {cr.project_id}")
    console.print(f"[cyan]项目名称:[/cyan] {cr.project_name}")
    console.print(f"[cyan]技术领域:[/cyan] {cr.domain} ({DOMAINS.get(cr.domain, '?')})")
    console.print(f"[cyan]业务性质:[/cyan] {cr.business_nature} ({BUSINESS_NATURES.get(cr.business_nature, '?')})")
    console.print(f"[cyan]影响范围:[/cyan] {','.join(cr.impact_scope)}")
    console.print(f"[cyan]紧急程度:[/cyan] {cr.urgency} ({URGENCY_LEVELS.get(cr.urgency, '?')})")
    console.print(f"[cyan]当前状态:[/cyan] {STATUS_LABELS.get(cr.status, cr.status)}")
    console.print(f"[cyan]申请人:[/cyan]   {cr.applicant}")
    console.print(f"[cyan]申请日期:[/cyan] {cr.apply_date}")
    console.print(f"[cyan]预计实施:[/cyan] {cr.planned_date}")
    console.print()
    console.print("[cyan]变更背景:[/cyan]")
    console.print(cr.background)
    console.print()
    console.print("[cyan]变更必要性:[/cyan]")
    console.print(cr.necessity)
    if cr.references and cr.references != "待补充":
        console.print()
        console.print("[cyan]参考依据:[/cyan]")
        console.print(cr.references)
    if cr.file_path:
        console.print()
        console.print(f"[dim]文件路径: {cr.file_path}[/dim]")


@change_group.command(name="create")
@click.option("--pid", "project_id", required=True, help="项目编号")
@click.option("--domain", type=click.Choice(_DOMAIN_CHOICES), required=True, help="技术领域")
@click.option("--nature", "business_nature", type=click.Choice(_NATURE_CHOICES), required=True, help="业务性质")
@click.option("--scope", "impact_scope", multiple=True, type=click.Choice(_SCOPE_CHOICES), required=True, help="影响范围（可多次指定）")
@click.option("--applicant", required=True, help="变更申请人")
@click.option("--background", required=True, help="变更背景")
@click.option("--necessity", required=True, help="变更必要性")
@click.option("--references", "references", default="", help="参考依据")
@click.option("--planned-date", default=None, help="预计实施日期（YYYY-MM-DD，默认今天）")
@click.option("--urgency", type=click.Choice(_URGENCY_CHOICES), default="normal", help="紧急程度")
@click.pass_context
def cmd_create(
    ctx: click.Context,
    project_id: str,
    domain: str,
    business_nature: str,
    impact_scope: tuple[str, ...],
    applicant: str,
    background: str,
    necessity: str,
    references: str,
    planned_date: str | None,
    urgency: str,
) -> None:
    """创建变更单（生成 CHG-*.md 文件并更新台帐）"""
    app_ctx: AppContext = ctx.obj
    svc = ChangeService(app_ctx.workspace_root)

    try:
        cr = svc.create_change_request(
            project_id=project_id,
            domain=domain,
            business_nature=business_nature,
            impact_scope=list(impact_scope),
            applicant=applicant,
            background=background,
            necessity=necessity,
            references=references,
            planned_date=planned_date,
            urgency=urgency,
        )
        console.print(f"[green]变更单创建成功: {cr.change_number}[/green]")
        console.print(f"  领域: {domain} ({DOMAINS[domain]})")
        console.print(f"  性质: {business_nature} ({BUSINESS_NATURES[business_nature]})")
        console.print(f"  范围: {','.join(impact_scope)}")
        console.print(f"  状态: {STATUS_LABELS.get(cr.status, cr.status)}")
        if cr.file_path:
            console.print(f"  文件: {cr.file_path}")
    except ValueError as e:
        console.print(f"[red]创建失败: {e}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]创建异常: {e}[/red]")
        ctx.exit(1)


@change_group.command(name="transition")
@click.argument("change_number")
@click.option("--to", "new_status", type=click.Choice(_STATUS_CHOICES), required=True, help="目标状态")
@click.option("--approver", default="", help="审批人/实施人")
@click.option("--comment", default="", help="审批意见/返工原因")
@click.option("--verification-conclusion", default="全部通过", help="验证结论（completed 状态必填）")
@click.pass_context
def cmd_transition(
    ctx: click.Context,
    change_number: str,
    new_status: str,
    approver: str,
    comment: str,
    verification_conclusion: str,
) -> None:
    """状态流转（更新变更单章节并持久化状态）"""
    app_ctx: AppContext = ctx.obj
    svc = ChangeService(app_ctx.workspace_root)

    try:
        cr = svc.transition_status(
            change_number=change_number,
            new_status=new_status,
            approver=approver,
            comment=comment,
            verification_conclusion=verification_conclusion,
        )
        if cr is None:
            console.print(f"[red]错误: 变更单不存在: {change_number}[/red]")
            ctx.exit(1)
        console.print(f"[green]状态流转成功: {change_number}[/green]")
        console.print(f"  新状态: {STATUS_LABELS.get(cr.status, cr.status)}")
        if cr.file_path:
            console.print(f"  文件: {cr.file_path}")
    except ValueError as e:
        console.print(f"[red]流转失败: {e}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]流转异常: {e}[/red]")
        ctx.exit(1)
