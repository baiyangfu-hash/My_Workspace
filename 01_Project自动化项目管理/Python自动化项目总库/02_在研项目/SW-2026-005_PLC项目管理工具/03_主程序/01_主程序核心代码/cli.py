"""CLI 入口：Service 层命令行验证

环境变量:
    PLC_WORKSPACE_ROOT  工作空间根目录（默认 0100_PLC自动化）
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from dataclasses import asdict

from src.services.change_management_service import ChangeManagementService
from src.services.project_overview_service import ProjectOverviewService
from src.utils.logger import get_logger

log = get_logger("cli")

_WORKSPACE_DEFAULT = r"C:\Users\fubai\Desktop\My_Workspace\0100_PLC自动化"
WORKSPACE_ROOT = os.environ.get("PLC_WORKSPACE_ROOT", _WORKSPACE_DEFAULT)


def cmd_projects(args: argparse.Namespace) -> None:
    """列出所有项目"""
    log.info("CLI: projects")
    svc = ProjectOverviewService(WORKSPACE_ROOT)
    projects = svc.get_workspace_projects()
    for p in projects:
        phase_display = p.phase if p.phase != "待补充" else "?"
        change_info = f"变更{p.change_count}件/待处理{p.pending_change_count}件"
        print(f"  {p.project_id}  {p.name}  [{phase_display}]  {change_info}")


def cmd_project(args: argparse.Namespace) -> None:
    """查看项目详情"""
    log.info("CLI: project %s", args.project_id)
    svc = ProjectOverviewService(WORKSPACE_ROOT)
    info = svc.get_project_detail(args.project_id)
    if info is None:
        print(f"项目不存在: {args.project_id}")
        return
    data = asdict(info)
    # 格式化输出
    print(f"项目编号: {data['project_id']}")
    print(f"项目名称: {data['name']}")
    print(f"当前阶段: {data['phase']}")
    print(f"业务描述: {data['business_desc']}")
    print(f"工艺范围: {data['process_scope']}")
    print(f"编程平台: {data['platform']}")
    print(f"PLC型号: {data['plc_model']}")
    print(f"开始日期: {data['start_date']}")
    print(f"预计完成: {data['end_date']}")
    print(f"变更总数: {data['change_count']}")
    print(f"待处理变更: {data['pending_change_count']}")
    if data["risks"]:
        print("风险评估:")
        for r in data["risks"]:
            print(f"  - {r['risk_item']} [{r['level']}] → {r['measure']}")


def cmd_changes(args: argparse.Namespace) -> None:
    """查看项目变更单"""
    log.info("CLI: changes %s", args.project_id)
    svc = ProjectOverviewService(WORKSPACE_ROOT)
    changes = svc.get_project_changes(args.project_id)
    if not changes:
        print("无变更单")
        return
    for c in changes:
        print(f"  {c.change_number}  [{c.domain}]  [{c.business_nature}]  [{c.status}]  {c.title}")


def cmd_create_change(args: argparse.Namespace) -> None:
    """创建变更单"""
    log.info("CLI: create-change project=%s domain=%s nature=%s",
             args.project_id, args.domain, args.nature)
    svc = ChangeManagementService(WORKSPACE_ROOT)
    cr = svc.create_change_request(
        project_id=args.project_id,
        domain=args.domain,
        business_nature=args.nature,
        impact_scope=args.scope,
        applicant=args.applicant,
        background=args.background,
        necessity=args.necessity,
        references=getattr(args, "references", ""),
        planned_date=getattr(args, "planned_date", None),
        urgency=getattr(args, "urgency", "normal"),
    )
    print(f"变更单已创建: {cr.change_number}")
    print(f"文件路径: {cr.file_path}")


def cmd_list_changes(args: argparse.Namespace) -> None:
    """列出变更单"""
    log.info("CLI: list-changes project=%s status=%s domain=%s",
             args.project_id, args.status, args.domain)
    svc = ChangeManagementService(WORKSPACE_ROOT)
    filters = {}
    if args.status:
        filters["status"] = args.status
    if args.domain:
        filters["domain"] = args.domain
    changes = svc.list_change_requests(args.project_id, **filters)
    if not changes:
        print("无匹配变更单")
        return
    for c in changes:
        print(f"  {c.change_number}  [{c.domain}]  [{c.business_nature}]  [{c.status}]  {c.title}")


def cmd_show_change(args: argparse.Namespace) -> None:
    """查看变更单详情"""
    log.info("CLI: show-change %s", args.change_number)
    svc = ChangeManagementService(WORKSPACE_ROOT)
    cr = svc.get_change_request(args.change_number)
    if cr is None:
        print(f"变更单不存在: {args.change_number}")
        return
    print(f"变更编号: {cr.change_number}")
    print(f"项目编号: {cr.project_id}")
    print(f"领域: {cr.domain}")
    print(f"性质: {cr.business_nature}")
    print(f"影响范围: {', '.join(cr.impact_scope)}")
    print(f"状态: {cr.status}")
    print(f"申请人: {cr.applicant}")
    print(f"申请日期: {cr.apply_date}")
    print(f"变更背景: {cr.background}")


def cmd_transition(args: argparse.Namespace) -> None:
    """状态流转"""
    log.info("CLI: transition %s → %s", args.change_number, args.status)
    svc = ChangeManagementService(WORKSPACE_ROOT)
    cr = svc.transition_status(
        change_number=args.change_number,
        new_status=args.status,
        approver=getattr(args, "approver", ""),
        comment=getattr(args, "comment", ""),
    )
    if cr is None:
        print(f"变更单不存在: {args.change_number}")
        return
    print(f"状态已更新: {cr.change_number} → {cr.status}")


def cmd_refresh(args: argparse.Namespace) -> None:
    """刷新缓存"""
    log.info("CLI: refresh project=%s", getattr(args, "project_id", None))
    svc = ProjectOverviewService(WORKSPACE_ROOT)
    project_id = getattr(args, "project_id", None)
    svc.refresh(project_id)
    if project_id:
        print(f"已刷新项目 {project_id} 的缓存")
    else:
        print("已刷新全部缓存")


def main() -> None:
    parser = argparse.ArgumentParser(description="PLC项目管理工具 CLI")
    parser.add_argument(
        "-w", "--workspace",
        default=WORKSPACE_ROOT,
        help="工作空间根目录",
    )
    subparsers = parser.add_subparsers(dest="command")

    # projects
    sub = subparsers.add_parser("projects", help="列出所有项目")
    sub.set_defaults(func=cmd_projects)

    # project <id>
    sub = subparsers.add_parser("project", help="查看项目详情")
    sub.add_argument("project_id", help="项目编号")
    sub.set_defaults(func=cmd_project)

    # changes <project_id>
    sub = subparsers.add_parser("changes", help="查看项目变更单")
    sub.add_argument("project_id", help="项目编号")
    sub.set_defaults(func=cmd_changes)

    # create-change
    sub = subparsers.add_parser("create-change", help="创建变更单")
    sub.add_argument("project_id", help="项目编号")
    sub.add_argument("--domain", required=True, help="技术领域 (ELEC/MECH/PLC/HMI/SCPT/DOCU/SAFE)")
    sub.add_argument("--nature", required=True, help="业务性质 (REQ/DEF/OPT/CFG/EMRG)")
    sub.add_argument("--scope", nargs="+", required=True, help="影响范围 (LOCAL/MODULE/SYSTEM/CROSS/SAFE)")
    sub.add_argument("--applicant", required=True, help="变更申请人")
    sub.add_argument("--background", required=True, help="变更背景")
    sub.add_argument("--necessity", required=True, help="变更必要性")
    sub.add_argument("--references", default="", help="参考依据")
    sub.add_argument("--planned-date", default=None, help="预计实施日期")
    sub.add_argument("--urgency", default="normal", choices=["normal", "urgent", "critical"], help="紧急程度")
    sub.set_defaults(func=cmd_create_change)

    # list-changes
    sub = subparsers.add_parser("list-changes", help="列出变更单")
    sub.add_argument("project_id", help="项目编号")
    sub.add_argument("--status", default=None, help="筛选状态")
    sub.add_argument("--domain", default=None, help="筛选领域")
    sub.set_defaults(func=cmd_list_changes)

    # show-change
    sub = subparsers.add_parser("show-change", help="查看变更单详情")
    sub.add_argument("change_number", help="变更编号")
    sub.set_defaults(func=cmd_show_change)

    # transition
    sub = subparsers.add_parser("transition", help="状态流转")
    sub.add_argument("change_number", help="变更编号")
    sub.add_argument("--status", required=True, help="新状态")
    sub.add_argument("--approver", default="", help="审批人")
    sub.add_argument("--comment", default="", help="审批意见")
    sub.set_defaults(func=cmd_transition)

    # refresh
    sub = subparsers.add_parser("refresh", help="刷新缓存")
    sub.add_argument("project_id", nargs="?", default=None, help="项目编号（可选）")
    sub.set_defaults(func=cmd_refresh)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    # 更新工作空间根目录
    import cli as cli_module
    cli_module.WORKSPACE_ROOT = args.workspace

    args.func(args)


if __name__ == "__main__":
    main()
