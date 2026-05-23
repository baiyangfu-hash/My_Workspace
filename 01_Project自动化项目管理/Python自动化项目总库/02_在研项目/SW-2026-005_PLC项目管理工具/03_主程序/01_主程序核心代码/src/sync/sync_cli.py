# -*- coding: utf-8 -*-
"""
同步CLI命令行入口

用法:
    python -m src.sync.sync_cli check <project_path>
    python -m src.sync.sync_cli full-report <project_path> [--output <dir>]
    python -m src.sync.sync_cli generate-ifc <fb_name> <project_path> [--db <db_path>]
    python -m src.sync.sync_cli generate-chg <fb_name> <project_path> [--source scl|session]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.sync.sync_engine import SyncEngine
from src.sync.ifc_generator import IfcGenerator
from src.sync.chg_generator import ChgGenerator
from src.utils.logger import setup_logger

logger = setup_logger("sync_cli")


def cmd_check(args):
    """L0 版本一致性检查"""
    project_path = str(Path(args.project_path).resolve())
    report = SyncEngine.run_check(project_path)
    if report.lagging_count > 0:
        return 1
    return 0


def cmd_full_report(args):
    """全量同步报告"""
    project_path = str(Path(args.project_path).resolve())
    output = args.output
    report_path = SyncEngine.run_full_report(project_path, output)
    print(f"报告已生成: {report_path}")
    return 0


def cmd_generate_ifc(args):
    """L1 半自动: 从 GlobalVars.db 生成 IFC 接口文档"""
    project_path = Path(args.project_path).resolve()
    db_path = args.db if args.db else _find_db(project_path)
    if not db_path or not Path(db_path).exists():
        print(f"[ERROR] 未找到 GlobalVars.db，请用 --db 指定路径")
        return 2

    fb_name = args.fb_name
    output_dir = args.output
    path = IfcGenerator.generate(str(db_path), fb_name, output_dir)
    if path:
        print(f"IFC 文档已生成: {path}")
        print(f"请人工审核后替换正式文档")
        return 0
    return 1


def _find_db(project_path: Path) -> str:
    """在项目路径中查找 GlobalVars.db"""
    candidates = list(project_path.rglob("GlobalVars.db"))
    if not candidates:
        candidates = list(project_path.rglob("*.db"))
    for c in candidates:
        if "archive" not in str(c).lower():
            return str(c)
    return ""


def cmd_generate_chg(args):
    """L1 半自动: 生成 CHG 变更记录文档"""
    project_path = Path(args.project_path).resolve()
    fb_name = args.fb_name
    source = args.source or "scl"

    if source == "session":
        session_path = project_path / "PM_SESSION_SW-2026-005.md"
        if not session_path.exists():
            candidates = list(project_path.rglob("PM_SESSION*.md"))
            if candidates:
                session_path = candidates[0]
            else:
                print("[ERROR] 未找到 PM_SESSION 文件")
                return 2
        path = ChgGenerator.generate_from_session(str(session_path), fb_name)
    else:
        scl_matches = list(project_path.rglob(f"*{fb_name}*.scl"))
        scl_matches = [s for s in scl_matches if "archive" not in str(s).lower()]
        if not scl_matches:
            if fb_name.lower() == "ob1":
                scl_matches = list(project_path.rglob("OB1.scl"))
            else:
                print(f"[ERROR] 未找到 {fb_name} 的 .scl 文件，请用 --source session")
                return 2
        scl_path = str(scl_matches[0])
        path = ChgGenerator.generate_from_scl(scl_path, fb_name)

    if path:
        print(f"CHG 文档已生成: {path}")
        print(f"请人工审核后替换正式文档")
        return 0
    return 1


def main():
    parser = argparse.ArgumentParser(
        prog="sync_cli",
        description="PLC项目文档-代码同步自动化工具 (SW-2026-005)"
    )
    sub = parser.add_subparsers(dest="command", help="子命令")

    p_check = sub.add_parser("check", help="L0 版本一致性检查 (全自动)")
    p_check.add_argument("project_path", help="项目根目录路径")
    p_check.set_defaults(func=cmd_check)

    p_report = sub.add_parser("full-report", help="生成全量同步报告")
    p_report.add_argument("project_path", help="项目根目录路径")
    p_report.add_argument("--output", "-o", help="报告输出目录 (默认项目根目录)")
    p_report.set_defaults(func=cmd_full_report)

    p_ifc = sub.add_parser("generate-ifc", help="L1 半自动: 从GlobalVars.db生成IFC文档")
    p_ifc.add_argument("fb_name", help="FB名称 (如 pickplace, feeder, conveyor, alarm, external, ob1)")
    p_ifc.add_argument("project_path", help="项目根目录路径")
    p_ifc.add_argument("--db", help="GlobalVars.db 路径 (默认自动查找)")
    p_ifc.add_argument("--output", "-o", help="输出目录 (默认 DB 同目录 PRD)")
    p_ifc.set_defaults(func=cmd_generate_ifc)

    p_chg = sub.add_parser("generate-chg", help="L1 半自动: 从.scl changelog或PM_SESSION生成CHG文档")
    p_chg.add_argument("fb_name", help="FB名称 (如 pickplace, feeder, conveyor, alarm, external, ob1)")
    p_chg.add_argument("project_path", help="项目根目录路径")
    p_chg.add_argument("--source", choices=["scl", "session"], default="scl",
                       help="数据来源: scl(从.scl changelog提取) / session(从PM_SESSION提取)")
    p_chg.set_defaults(func=cmd_generate_chg)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 0

    try:
        return args.func(args)
    except Exception as e:
        logger.exception(f"执行失败: {e}")
        print(f"[ERROR] {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())