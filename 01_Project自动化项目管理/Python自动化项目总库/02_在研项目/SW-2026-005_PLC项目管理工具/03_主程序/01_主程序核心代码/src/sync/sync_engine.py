# -*- coding: utf-8 -*-
"""
同步编排引擎

总控调度器，编排版本检查、IFC生成、CHG生成、回写等同步操作。
"""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import List

from src.sync.version_checker import VersionChecker, VersionGapReport
from src.sync.sync_report import SyncReport
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class SyncEngine:
    """同步编排引擎"""

    WRITEBACK_DIRS = {
        "chg": Path("00_项目管理") / "04_变更管理" / "01_变更单",
        "ifc": Path("00_项目管理") / "03_接口文档",
    }

    @classmethod
    def run_check(cls, project_path: str) -> VersionGapReport:
        """
        L0 版本一致性检查 (全自动)

        执行全量扫描并生成版本差距矩阵。
        """
        logger.info(f"开始版本检查: {project_path}")

        p = Path(project_path)
        if not p.exists():
            logger.error(f"项目路径不存在: {project_path}")
            return VersionGapReport(project_path=project_path)

        report = VersionChecker.check_project(project_path)

        cls._print_terminal_report(report)

        if report.lagging_count > 0:
            logger.warning(f"版本检查完成: {report.lagging_count} 个模块文档滞后")
        else:
            logger.info(f"版本检查完成: 全部一致 [OK]")

        return report

    @classmethod
    def run_full_report(cls, project_path: str, output_dir: str = None) -> str:
        """
        L0+L1+L2 全量同步报告

        基于 SyncReport 生成六段式完整报告:
        §1 版本差距矩阵 / §2 DSN覆盖度 / §3 UM覆盖度
        §4 变更台帐聚合 / §5 同步行动建议
        """
        logger.info(f"全量同步报告: {project_path}")

        report = SyncReport.generate_full_report(project_path)
        md_content = SyncReport.render_markdown(report)

        out = Path(output_dir) if output_dir else Path(project_path)
        out.mkdir(parents=True, exist_ok=True)
        report_path = out / "sync_full_report.md"
        report_path.write_text(md_content, encoding="utf-8")

        cls._print_terminal_summary(report)

        logger.info(f"全量报告已生成: {report_path} ({len(report.action_items)} 行动项)")
        return str(report_path)

    @classmethod
    def run_generate_chg(cls, project_path: str, output_dir: str = None) -> str:
        """
        生成变更记录文档(CHG)

        扫描项目中的 .scl 文件，为每个FB生成CHG文档。
        """
        from src.sync.chg_generator import ChgGenerator

        p = Path(project_path)
        if not p.exists():
            raise FileNotFoundError(f"项目路径不存在: {project_path}")

        out = Path(output_dir) if output_dir else p / "07_CHG"
        out.mkdir(parents=True, exist_ok=True)

        scl_files = list(p.rglob("*.scl"))
        if not scl_files:
            logger.warning("未找到 .scl 文件，跳过CHG生成")
            return str(out)

        generated = []
        for scl_file in scl_files:
            fb_name = scl_file.stem
            try:
                result = ChgGenerator.generate_from_scl(
                    str(scl_file), fb_name, str(out)
                )
                if result:
                    generated.append(result)
                    logger.info(f"CHG已生成: {fb_name}")
            except Exception as e:
                logger.warning(f"CHG生成失败 {fb_name}: {e}")

        if generated:
            logger.info(f"CHG文档生成完成: {len(generated)} 个文件")
        return str(out)

    @classmethod
    def run_generate_ifc(cls, project_path: str, output_dir: str = None) -> str:
        """
        生成接口文档(IFC)

        扫描项目中的 .db 文件，为每个DB生成IFC文档。
        """
        from src.sync.ifc_generator import IfcGenerator

        p = Path(project_path)
        if not p.exists():
            raise FileNotFoundError(f"项目路径不存在: {project_path}")

        out = Path(output_dir) if output_dir else p / "08_IFC"
        out.mkdir(parents=True, exist_ok=True)

        db_files = list(p.rglob("*.db"))
        if not db_files:
            logger.warning("未找到 .db 文件，跳过IFC生成")
            return str(out)

        generated = []
        for db_file in db_files:
            fb_name = db_file.stem
            try:
                result = IfcGenerator.generate(
                    str(db_file), fb_name, str(out)
                )
                if result:
                    generated.append(result)
                    logger.info(f"IFC已生成: {fb_name}")
            except Exception as e:
                logger.warning(f"IFC生成失败 {fb_name}: {e}")

        if generated:
            logger.info(f"IFC文档生成完成: {len(generated)} 个文件")
        return str(out)

    @classmethod
    def writeback_to_project(
        cls, source_path: str, project_path: str, doc_type: str
    ) -> List[str]:
        """
        将生成的文档回写到项目标准目录

        Args:
            source_path: 生成文件所在目录路径
            project_path: 项目根目录路径
            doc_type: 文档类型 "chg" | "ifc"

        Returns:
            回写后的文件路径列表

        Raises:
            FileNotFoundError: 项目路径不存在
            ValueError: doc_type 不合法
        """
        p = Path(project_path)
        if not p.exists():
            raise FileNotFoundError(f"项目路径不存在: {project_path}")

        if doc_type not in cls.WRITEBACK_DIRS:
            raise ValueError(f"不支持的文档类型: {doc_type}，可选: {list(cls.WRITEBACK_DIRS.keys())}")

        target_dir = p / cls.WRITEBACK_DIRS[doc_type]
        target_dir.mkdir(parents=True, exist_ok=True)

        source = Path(source_path)
        if not source.exists():
            raise FileNotFoundError(f"源路径不存在: {source_path}")

        source_files = [source] if source.is_file() else list(source.glob("*"))
        source_files = [f for f in source_files if f.is_file()]

        if not source_files:
            logger.warning(f"源目录无文件可回写: {source_path}")
            return []

        written = []
        for src_file in source_files:
            dest = target_dir / src_file.name
            if dest.exists():
                bak = dest.with_suffix(dest.suffix + ".bak")
                shutil.copy2(str(dest), str(bak))
                logger.info(f"已备份: {dest.name} -> {bak.name}")
            shutil.copy2(str(src_file), str(dest))
            written.append(str(dest))
            logger.info(f"已回写: {src_file.name} -> {dest}")

        logger.info(f"回写完成: {len(written)} 个文件 -> {target_dir}")
        return written

    @classmethod
    def _print_terminal_summary(cls, report) -> None:
        logger.info("=" * 60)
        logger.info(f"  全量同步报告 - {report.project_name}")
        logger.info("=" * 60)
        if report.version_gap:
            logger.info(f"  模块总数:     {report.version_gap.total_fbs}")
            logger.info(f"  [OK]已同步:   {report.version_gap.synced_count}")
            logger.info(f"  [X]滞后:     {report.version_gap.lagging_count}")
        dsn_ok = sum(1 for d in report.dsn_status if d.status == "[OK]")
        dsn_x = sum(1 for d in report.dsn_status if d.status in ("[X]", "[MISSING]"))
        um_ok = sum(1 for u in report.um_status if u.status == "[OK]")
        um_x = sum(1 for u in report.um_status if u.status in ("[X]", "[MISSING]"))
        logger.info(f"  DSN覆盖:      {dsn_ok}[OK] / {dsn_x}[X/MISSING]")
        logger.info(f"  UM覆盖:       {um_ok}[OK] / {um_x}[X/MISSING]")
        logger.info(f"  变更台帐:      {len(report.change_ledger)} 条")
        logger.info(f"  行动项:       {len(report.action_items)}")
        logger.info("=" * 60)

    @classmethod
    def format_version_report_html(cls, report: VersionGapReport) -> str:
        html_parts = [
            "<h2>版本一致性检查报告</h2>",
            f"<p><b>项目路径:</b> {report.project_path}</p>",
        ]

        if report.lagging_count == 0:
            html_parts.append(
                '<p style="color: green; font-size: 12pt;">'
                '✅ 全部模块文档版本一致</p>'
            )
        else:
            html_parts.append(
                f'<p style="color: red; font-size: 12pt;">'
                f'⚠️ {report.lagging_count} 个模块文档滞后</p>'
            )

        if hasattr(report, 'module_entries') and report.module_entries:
            html_parts.append("<table border='1' cellpadding='6' cellspacing='0'>")
            html_parts.append(
                "<tr><th>模块</th><th>代码版本</th><th>文档版本</th>"
                "<th>状态</th></tr>"
            )
            for entry in report.module_entries:
                status = "✅ 一致" if entry.is_consistent else "⚠️ 滞后"
                color = "green" if entry.is_consistent else "red"
                html_parts.append(
                    f"<tr><td>{entry.module_name}</td>"
                    f"<td>{entry.code_version}</td>"
                    f"<td>{entry.doc_version}</td>"
                    f"<td style='color:{color}'>{status}</td></tr>"
                )
            html_parts.append("</table>")

        return "\n".join(html_parts)

    @classmethod
    def _print_terminal_report(cls, report: VersionGapReport) -> None:
        logger.info(VersionChecker.format_report(report))

        if report.lagging_count > 0:
            logger.info("")
            logger.info("[详细差距]")
            for gap in report.fb_gaps:
                if gap.status == "[X]":
                    desc = gap.gap_desc or "文档版本滞后"
                    logger.info(f"  [X] {gap.fb_name}: {desc}")
            logger.info("")
            logger.info(f"[!] 建议: 运行 'generate-ifc' 或 'generate-chg' 子命令同步文档")