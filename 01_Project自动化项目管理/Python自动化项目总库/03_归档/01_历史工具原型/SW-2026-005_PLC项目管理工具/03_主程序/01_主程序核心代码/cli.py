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
from src.services.plc_project_service import PlcProjectService
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
        verification_conclusion=getattr(args, "verification_conclusion", "全部通过"),
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


def cmd_plc_init(args: argparse.Namespace) -> None:
    """创建标准 PLC 项目骨架"""
    log.info("CLI: plc-init project=%s name=%s", args.project_id, args.name)
    svc = PlcProjectService(WORKSPACE_ROOT)
    result = svc.init_project(
        project_id=args.project_id,
        project_name=args.name,
        description=getattr(args, "description", "") or "",
        dry_run=args.dry_run,
    )
    if args.dry_run:
        print(f"[DRY-RUN] 将创建项目: {result['project_path']}")
        print("将创建以下文件/目录:")
        for f in result["created_files"]:
            print(f"  {f}")
    else:
        print(f"项目已创建: {result['project_path']}")
        print(f"共创建 {len(result['created_files'])} 个文件/目录")
        print(f"PM_SESSION: {result['project_path']}/PM_SESSION_{args.project_id}.md")


def cmd_plc_check(args: argparse.Namespace) -> None:
    """检查项目结构是否符合 LSP-907 规范"""
    svc = PlcProjectService(WORKSPACE_ROOT)

    if args.all:
        log.info("CLI: plc-check --all")
        results = svc.check_workspace(scan_depth=args.depth)
        if not results:
            print("未发现任何项目")
            return
        for r in results:
            _print_check_result(r)
    else:
        project_path = args.project_path
        if not os.path.isabs(project_path):
            project_path = os.path.join(WORKSPACE_ROOT, project_path)
        log.info("CLI: plc-check %s", project_path)
        result = svc.check_project(project_path)
        _print_check_result(result)


def _print_check_result(result) -> None:
    """格式化输出检查结果"""
    project_name = os.path.basename(result.project_path)
    status_icon = "PASS" if result.all_pass else "FAIL"
    print(f"\n{'='*60}")
    print(f"  {project_name} [{result.project_type}]  {status_icon}")
    print(f"  pass={result.pass_count}  warn={result.warn_count}  fail={result.fail_count}")
    print(f"{'='*60}")
    for item in result.items:
        icon = {"pass": "  OK", "warn": " WARN", "fail": "FAIL"}.get(item.status, "  ??")
        print(f"  [{icon}] {item.item}: {item.message}")


def cmd_plc_repair(args: argparse.Namespace) -> None:
    """自动修复项目结构问题"""
    from src.services.plc_project_service import RepairResult

    svc = PlcProjectService(WORKSPACE_ROOT)

    if args.all:
        log.info("CLI: plc-repair --all (dry_run=%s, rename_confirm=%s)",
                 args.dry_run, args.rename_confirm)
        results = svc.repair_workspace(
            dry_run=args.dry_run, rename_confirm=args.rename_confirm
        )
        if not results:
            print("所有项目均已通过检查，无需修复")
            return
        for r in results:
            _print_repair_result(r)
    else:
        project_path = args.project_path
        if not os.path.isabs(project_path):
            project_path = os.path.join(WORKSPACE_ROOT, project_path)
        log.info("CLI: plc-repair %s (dry_run=%s, rename_confirm=%s)",
                 project_path, args.dry_run, args.rename_confirm)
        result = svc.repair_project(
            project_path, dry_run=args.dry_run, rename_confirm=args.rename_confirm
        )
        _print_repair_result(result)


def _print_repair_result(result) -> None:
    """格式化输出修复结果"""
    project_name = os.path.basename(result.project_path)
    print(f"\n{'='*60}")
    print(f"  修复报告: {project_name}")
    print(f"  fixed={result.fixed_count}  skipped={result.skipped_count}  failed={result.failed_count}")
    print(f"{'='*60}")

    for action in result.actions:
        icon = {"fixed": "FIXED", "skipped": "SKIP ", "failed": "FAIL "}.get(action.status, "??   ")
        destructive = " [破坏性]" if action.destructive else ""
        print(f"  [{icon}] {action.item}{destructive}")
        print(f"         动作: {action.action}")
        print(f"         详情: {action.detail}")

    # 修复前后对比
    if result.before_check and result.after_check:
        print(f"\n  修复前: pass={result.before_check.pass_count} "
              f"warn={result.before_check.warn_count} "
              f"fail={result.before_check.fail_count}")
        print(f"  修复后: pass={result.after_check.pass_count} "
              f"warn={result.after_check.warn_count} "
              f"fail={result.after_check.fail_count}")
        if result.after_check.all_pass:
            print("  [OK] 项目已全部通过检查")
        else:
            print(f"  [FAIL] 仍有 {result.after_check.fail_count} 项未通过")


def cmd_plc_standardize(args: argparse.Namespace) -> None:
    """检测并修正PRD文档命名"""
    svc = PlcProjectService(WORKSPACE_ROOT)

    if args.all:
        log.info("CLI: plc-standardize --all (apply=%s)", args.apply)
        results = svc.standardize_workspace(apply=args.apply)
        if not results:
            print("未发现任何项目")
            return
        for r in results:
            _print_standardize_result(r)
    else:
        project_path = args.project_path
        if not os.path.isabs(project_path):
            project_path = os.path.join(WORKSPACE_ROOT, project_path)
        log.info("CLI: plc-standardize %s (apply=%s)", project_path, args.apply)
        result = svc.standardize_docs(project_path, apply=args.apply)
        _print_standardize_result(result)


def _print_standardize_result(result) -> None:
    """格式化输出标准化结果"""
    project_name = os.path.basename(result.project_path)
    print(f"\n{'='*60}")
    print(f"  文档标准化: {project_name}")
    print(f"  applied={result.applied_count}  skipped={result.skipped_count}")
    print(f"{'='*60}")

    if not result.plans:
        print("  无需标准化（所有文档命名已符合规范）")
        return

    for plan in result.plans:
        old_name = os.path.basename(plan.old_path)
        new_name = os.path.basename(plan.new_path)
        status = "已执行" if plan.applied else "未执行"
        print(f"  [{plan.doc_type}] {old_name} → {new_name}  ({status})")
        if plan.backup_path:
            print(f"         备份: {plan.backup_path}")

    if result.reference_updates:
        print(f"\n  关联引用更新 ({len(result.reference_updates)} 处):")
        for update in result.reference_updates:
            print(f"    - {update}")


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
    sub.add_argument("--verification-conclusion", default="全部通过",
                     choices=["全部通过", "部分不通过", "需补充验证"],
                     help="验证结论（仅 completed 状态有效）")
    sub.set_defaults(func=cmd_transition)

    # refresh
    sub = subparsers.add_parser("refresh", help="刷新缓存")
    sub.add_argument("project_id", nargs="?", default=None, help="项目编号（可选）")
    sub.set_defaults(func=cmd_refresh)

    # plc-init
    sub = subparsers.add_parser("plc-init", help="创建标准 PLC 项目骨架")
    sub.add_argument("project_id", help="项目编号，如 DJ-2026-010")
    sub.add_argument("name", help="项目名称，如 边框缓存机")
    sub.add_argument("--description", default="", help="项目描述（可选，默认使用项目名称）")
    sub.add_argument("--dry-run", action="store_true", help="仅预览，不实际创建文件")
    sub.set_defaults(func=cmd_plc_init)

    # plc-check
    sub = subparsers.add_parser("plc-check", help="检查项目结构是否符合 LSP-907 规范")
    sub.add_argument("project_path", nargs="?", default=".", help="项目路径（绝对路径或相对于工作空间的路径）")
    sub.add_argument("--all", action="store_true", help="扫描工作空间下所有项目")
    sub.add_argument("--depth", type=int, default=4, help="扫描深度（默认4，覆盖SysLib/actuator/FB_xxx三级嵌套）")
    sub.set_defaults(func=cmd_plc_check)

    # plc-repair
    sub = subparsers.add_parser("plc-repair", help="自动修复项目结构问题")
    sub.add_argument("project_path", nargs="?", default=".", help="项目路径（绝对路径或相对于工作空间的路径）")
    sub.add_argument("--all", action="store_true", help="批量修复工作空间所有项目")
    sub.add_argument("--dry-run", action="store_true", help="仅预览修复动作，不实际执行")
    sub.add_argument("--rename-confirm", action="store_true", help="确认执行文件重命名（破坏性操作）")
    sub.set_defaults(func=cmd_plc_repair)

    # plc-standardize
    sub = subparsers.add_parser("plc-standardize", help="检测并修正PRD文档命名")
    sub.add_argument("project_path", nargs="?", default=".", help="项目路径（绝对路径或相对于工作空间的路径）")
    sub.add_argument("--all", action="store_true", help="批量检测工作空间所有项目")
    sub.add_argument("--apply", action="store_true", help="执行重命名（默认仅检测预览）")
    sub.set_defaults(func=cmd_plc_standardize)

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
