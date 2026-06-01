# -*- coding: utf-8 -*-
"""
自动修复服务层

提供PLC代码规范问题的自动批量修复能力，
与SpecCheckerService的检测能力形成完整闭环。

核心功能：
- 项目级扫描：扫描所有源码文件并检测可修复问题
- 单文件修复：对指定文件执行自动修复（支持dry_run预览）
- 项目级修复：批量修复整个项目（支持dry_run预览）
- 修复器管理：获取可用修复器列表及其元信息
- 回滚机制：基于.bak备份文件的回滚能力

设计原则：
- 安全优先：修复前强制备份，dry_run模式只预览不修改
- 可追溯：记录每次修复操作的详细日志
- 低耦合：与UI层解耦，仅返回标准化的报告对象

Usage:
    report = AutoFixService.scan_project("/path/to/project")
    result = AutoFixService.fix_file("/path/to/file.st", ["COMMENT_PUNCTUATION_FIXER"], dry_run=True)
    project_report = AutoFixService.fix_project("/path/to/project", ["COMMENT_PUNCTUATION_FIXER"], dry_run=False)
"""
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

_FIXER_REGISTRY: Dict[str, Any] = {}


class FixReport:
    """
    扫描报告数据类

    记录一次项目扫描的结果摘要。

    Attributes:
        project_path: 项目路径
        scan_time: 扫描时间
        total_files_scanned: 扫描文件总数
        total_issues_found: 发现的问题总数
        file_reports: 各文件的扫描结果列表
    """

    def __init__(
        self,
        project_path: str = "",
        total_files_scanned: int = 0,
        total_issues_found: int = 0,
    ):
        self.project_path = project_path
        self.scan_time = datetime.now()
        self.total_files_scanned = total_files_scanned
        self.total_issues_found = total_issues_found
        self.file_reports: List[FileFixReport] = []

    def add_file_report(self, report: "FileFixReport") -> None:
        self.file_reports.append(report)
        self.total_files_scanned += 1
        self.total_issues_found += report.total_issues

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_path": self.project_path,
            "scan_time": self.scan_time.isoformat(),
            "total_files_scanned": self.total_files_scanned,
            "total_issues_found": self.total_issues_found,
            "file_reports": [r.to_dict() for r in self.file_reports],
        }


class FileFixReport:
    """
    单文件修复报告数据类

    记录单个文件的一次修复操作结果。

    Attributes:
        file_path: 文件路径
        issues: 检测到的问题列表
        results: 修复结果列表
        total_issues: 问题总数
        success_count: 成功修复数
        is_dry_run: 是否为dry_run模式
        backup_path: 备份文件路径
        error_message: 错误信息（如有）
    """

    def __init__(
        self,
        file_path: str = "",
        issues: Optional[List[Any]] = None,
        results: Optional[List[Any]] = None,
        is_dry_run: bool = False,
        backup_path: str = "",
        error_message: str = "",
    ):
        from src.fixers.base_fixer import FixResult

        self.file_path = file_path
        self.issues = issues or []
        self.results = results or []
        self.total_issues = len(self.issues)
        self.success_count = sum(
            1 for r in self.results if isinstance(r, FixResult) and r.success
        )
        self.is_dry_run = is_dry_run
        self.backup_path = backup_path
        self.error_message = error_message
        self.fix_time = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        from src.fixers.base_fixer import FixIssue, FixResult

        return {
            "file_path": self.file_path,
            "total_issues": self.total_issues,
            "success_count": self.success_count,
            "is_dry_run": self.is_dry_run,
            "backup_path": self.backup_path,
            "error_message": self.error_message,
            "fix_time": self.fix_time.isoformat(),
            "issues": [
                i.to_dict() if isinstance(i, FixIssue) else str(i)
                for i in self.issues
            ],
            "results": [
                r.to_dict() if isinstance(r, FixResult) else str(r)
                for r in self.results
            ],
        }


class ProjectFixReport:
    """
    项目级修复报告数据类

    汇总整个项目的批量修复结果。

    Attributes:
        project_path: 项目路径
        fix_time: 修复时间
        total_files_processed: 处理的文件总数
        total_issues_fixed: 修复的问题总数
        total_files_modified: 实际修改的文件数
        is_dry_run: 是否为dry_run模式
        file_reports: 各文件的修复报告列表
    """

    def __init__(
        self,
        project_path: str = "",
        is_dry_run: bool = True,
    ):
        self.project_path = project_path
        self.fix_time = datetime.now()
        self.total_files_processed = 0
        self.total_issues_fixed = 0
        self.total_files_modified = 0
        self.is_dry_run = is_dry_run
        self.file_reports: List[FileFixReport] = []

    def add_file_report(self, report: FileFixReport) -> None:
        self.file_reports.append(report)
        self.total_files_processed += 1
        self.total_issues_fixed += report.success_count
        if not report.is_dry_run and report.success_count > 0:
            self.total_files_modified += 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_path": self.project_path,
            "fix_time": self.fix_time.isoformat(),
            "total_files_processed": self.total_files_processed,
            "total_issues_fixed": self.total_issues_fixed,
            "total_files_modified": self.total_files_modified,
            "is_dry_run": self.is_dry_run,
            "file_reports": [r.to_dict() for r in self.file_reports],
        }

    def generate_summary_text(self) -> str:
        lines = [
            "=" * 60,
            "PLC代码自动修复报告",
            "=" * 60,
            f"项目路径: {self.project_path}",
            f"修复时间: {self.fix_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"运行模式: {'预览(dry_run)' if self.is_dry_run else '实际修复'}",
            "-" * 60,
            "统计摘要:",
            f"  • 处理文件数: {self.total_files_processed}",
            f"  • 修复问题数: {self.total_issues_fixed}",
            f"  • 修改文件数: {self.total_files_modified}" if not self.is_dry_run else "",
            "-" * 60,
        ]
        if self.file_reports:
            lines.append("\n各文件修复详情:")
            for idx, fr in enumerate(self.file_reports, start=1):
                status = "✓" if fr.success_count > 0 else "-"
                mode = "[预览]" if fr.is_dry_run else "[已修复]"
                err = f" (错误: {fr.error_message})" if fr.error_message else ""
                lines.append(
                    f"  {idx}. {status} {Path(fr.file_path).name}{mode}"
                    f" - {fr.success_count}/{fr.total_issues} 个问题{err}"
                )
        lines.append("=" * 60)
        return "\n".join(lines)


class AutoFixService:
    """
    自动修复服务类

    提供PLC代码规范问题的自动检测和修复能力，
    采用@classmethod静态接口模式，无需实例化即可调用。

    Attributes:
        _FIXER_REGISTRY: 内部修复器注册表 {fixer_id: fixer_instance}
        _supported_extensions: 支持的文件扩展名列表
        _exclude_patterns: 排除的文件名模式列表
    """

    _supported_extensions: List[str] = [".st", ".TcPOU", ".st7"]
    _exclude_patterns: List[str] = ["_test", "test_", "example"]

    @classmethod
    def _get_registry(cls) -> Dict[str, Any]:
        """获取或初始化修复器注册表"""
        global _FIXER_REGISTRY

        if not _FIXER_REGISTRY:
            try:
                from src.fixers.comment_punctuation_fixer import CommentPunctuationFixer
                from src.fixers.naming_fixer import NamingFixer

                _FIXER_REGISTRY["COMMENT_PUNCTUATION_FIXER"] = CommentPunctuationFixer()
                _FIXER_REGISTRY["NAMING_FIXER"] = NamingFixer()

                logger.info(
                    f"修复器注册表初始化完成, "
                    f"共{len(_FIXER_REGISTRY)}个修复器"
                )

            except Exception as e:
                logger.error(f"初始化修复器注册表失败: {e}", exc_info=True)

        return _FIXER_REGISTRY

    @classmethod
    def scan_project(
        cls,
        project_path: str,
        fixer_ids: Optional[List[str]] = None,
    ) -> FixReport:
        """
        扫描项目中所有可修复的问题

        遍历项目目录中的ST源码文件，
        使用指定的修复器检测可自动修复的问题。

        Args:
            project_path: PLC项目根目录路径
            fixer_ids: 要使用的修复器ID列表，为None时使用全部修复器

        Returns:
            FixReport: 包含所有文件扫描结果的报告对象
        """
        start_time = datetime.now()
        report = FixReport(project_path=project_path)

        try:
            project_dir = Path(project_path).resolve()
            if not project_dir.exists():
                logger.error(f"项目目录不存在: {project_path}")
                return report

            registry = cls._get_registry()
            active_fixers = cls._resolve_fixers(registry, fixer_ids)

            if not active_fixers:
                logger.warning("没有可用的修复器")
                return report

            st_files = cls._collect_st_files(project_path)

            if not st_files:
                logger.warning("未找到可扫描的ST源码文件")
                return report

            logger.info(
                f"开始项目扫描: {project_dir.name}, "
                f"{len(st_files)} 个文件, "
                f"{len(active_fixers)} 个修复器"
            )

            for file_path in st_files:
                file_report = cls._scan_single_file(
                    file_path, active_fixers
                )
                report.add_file_report(file_report)

            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(
                f"项目扫描完成: {report.total_files_scanned} 文件, "
                f"{report.total_issues_found} 问题, 耗时 {elapsed:.2f}s"
            )

        except Exception as e:
            logger.exception(f"项目扫描过程发生异常: {e}")

        return report

    @classmethod
    def fix_file(
        cls,
        file_path: str,
        fixer_ids: List[str],
        dry_run: bool = False,
    ) -> FileFixReport:
        """
        对指定文件执行自动修复

        流程：
        1. 读取源文件内容
        2. 使用指定修复器检测问题
        3. 若非dry_run则创建.bak备份
        4. 执行修复操作
        5. 若非dry_run则写回文件
        6. 返回修复报告

        Args:
            file_path: 待修复的源码文件路径
            fixer_ids: 要使用的修复器ID列表
            dry_run: True=仅预览不修改文件, False=实际执行修复

        Returns:
            FileFixReport: 单文件修复报告
        """
        from src.fixers.base_fixer import FixIssue, FixResult

        try:
            file_obj = Path(file_path).resolve()
            if not file_obj.exists():
                return FileFixReport(
                    file_path=file_path,
                    error_message=f"文件不存在: {file_path}",
                )

            with open(file_obj, "r", encoding="utf-8") as f:
                source_code = f.read()

            registry = cls._get_registry()
            active_fixers = cls._resolve_fixers(registry, fixer_ids)

            all_issues: List[FixIssue] = []
            all_results: List[FixResult] = []

            for fixer in active_fixers:
                try:
                    issues = fixer.detect(source_code, file_path=str(file_obj))
                    if issues:
                        all_issues.extend(issues)

                        if dry_run:
                            _, results = fixer.fix(source_code, issues)
                            all_results.extend(results)
                        else:
                            fixed_code, results = fixer.fix(source_code, issues)
                            all_results.extend(results)
                            source_code = fixed_code

                except Exception as e:
                    logger.error(
                        f"修复器 {fixer.fixer_id} 执行异常: {e}"
                    )

            backup_path = ""
            if not dry_run and all_results:
                backup_path = cls._create_backup(str(file_obj))

            if not dry_run and any(r.success for r in all_results):
                with open(file_obj, "w", encoding="utf-8") as f:
                    f.write(source_code)
                logger.info(f"文件已修复并保存: {file_obj.name}")

            file_report = FileFixReport(
                file_path=str(file_obj),
                issues=all_issues,
                results=all_results,
                is_dry_run=dry_run,
                backup_path=backup_path,
            )

            logger.debug(
                f"单文件修复完成: {file_obj.name} - "
                f"{file_report.success_count}/{file_report.total_issues}"
            )

            return file_report

        except Exception as e:
            logger.exception(f"文件修复失败: {file_path} - {e}")
            return FileFixReport(
                file_path=file_path,
                error_message=str(e),
            )

    @classmethod
    def fix_project(
        cls,
        project_path: str,
        fixer_ids: List[str],
        dry_run: bool = True,
    ) -> ProjectFixReport:
        """
        对整个项目执行批量自动修复

        扫描项目中所有ST文件并逐一执行修复。
        默认使用dry_run=True确保安全。

        Args:
            project_path: PLC项目根目录路径
            fixer_ids: 要使用的修复器ID列表
            dry_run: True=仅预览, False=实际修复（默认True）

        Returns:
            ProjectFixReport: 项目级修复报告
        """
        start_time = datetime.now()
        report = ProjectFixReport(
            project_path=project_path,
            is_dry_run=dry_run,
        )

        try:
            project_dir = Path(project_path).resolve()
            if not project_dir.exists():
                logger.error(f"项目目录不存在: {project_path}")
                return report

            st_files = cls._collect_st_files(project_path)

            if not st_files:
                logger.warning("未找到可修复的ST源码文件")
                return report

            mode_str = "预览(dry_run)" if dry_run else "实际修复"
            logger.info(
                f"开始项目级{'预览' if dry_run else '修复'}: "
                f"{project_dir.name}, {len(st_files)} 个文件"
            )

            for idx, file_path in enumerate(st_files, start=1):
                logger.debug(
                    f"正在处理 ({idx}/{len(st_files)}): "
                    f"{Path(file_path).name}"
                )

                file_report = cls.fix_file(file_path, fixer_ids, dry_run=dry_run)
                report.add_file_report(file_report)

            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(
                f"项目{mode_str}完成: "
                f"{report.total_files_processed} 文件, "
                f"{report.total_issues_fixed} 问题, "
                f"耗时 {elapsed:.2f}s"
            )

        except Exception as e:
            logger.exception(f"项目级修复过程发生异常: {e}")

        return report

    @classmethod
    def get_available_fixers(cls) -> List[Dict[str, Any]]:
        """
        获取所有可用修复器的信息列表

        Returns:
            List[Dict]: 修复器信息字典列表，每个包含fixer_id/name/description/category/is_safe等字段
        """
        registry = cls._get_registry()
        fixer_info_list = []

        for fixer_id, fixer in sorted(registry.items()):
            info = fixer.get_fixer_info()
            fixer_info_list.append(info.to_dict())

        return fixer_info_list

    @classmethod
    def rollback_file(cls, file_path: str, backup_path: str = "") -> bool:
        """
        从备份文件回滚指定文件

        将.bak备份文件恢复为原始文件。

        Args:
            file_path: 要回滚的原始文件路径
            backup_path: 备份文件路径，为空时自动查找 .bak 文件

        Returns:
            bool: 回滚成功返回True，失败返回False
        """
        try:
            file_obj = Path(file_path).resolve()

            if not backup_path:
                backup_path = str(file_obj) + ".bak"

            backup_obj = Path(backup_path).resolve()

            if not backup_obj.exists():
                logger.error(f"备份文件不存在: {backup_path}")
                return False

            shutil.copy2(str(backup_obj), str(file_obj))

            logger.info(f"文件已从备份回滚: {file_obj.name} <- {backup_obj.name}")
            return True

        except Exception as e:
            logger.exception(f"文件回滚失败: {file_path} - {e}")
            return False

    @classmethod
    def preview_file(
        cls,
        file_path: str,
        fixer_ids: List[str],
    ) -> List[Dict[str, Any]]:
        """
        对指定文件生成修复预览

        不修改任何文件，返回结构化的预览信息。

        Args:
            file_path: 源文件路径
            fixer_ids: 修复器ID列表

        Returns:
            List[Dict]: 预览信息列表（每个修复器一个预览）
        """
        from src.fixers.base_fixer import FixPreview

        previews: List[Dict[str, Any]] = []

        try:
            file_obj = Path(file_path).resolve()
            if not file_obj.exists():
                return [{"error": f"文件不存在: {file_path}"}]

            with open(file_obj, "r", encoding="utf-8") as f:
                source_code = f.read()

            registry = cls._get_registry()
            active_fixers = cls._resolve_fixers(registry, fixer_ids)

            for fixer in active_fixers:
                try:
                    issues = fixer.detect(source_code, file_path=str(file_obj))
                    if issues:
                        fix_previews = fixer.preview_fix(source_code, issues)
                        for fp in fix_previews:
                            if isinstance(fp, FixPreview):
                                previews.append(fp.to_dict())
                    else:
                        previews.append({
                            "fixer_id": fixer.fixer_id,
                            "diff_view": "未发现需要修复的问题",
                            "issue_count": 0,
                            "affected_lines": [],
                        })

                except Exception as e:
                    previews.append({
                        "fixer_id": fixer.fixer_id,
                        "error": str(e),
                    })

        except Exception as e:
            previews.append({"error": str(e)})

        return previews

    # ==================================================================
    # 内部辅助方法
    # ==================================================================

    @classmethod
    def _resolve_fixers(
        cls,
        registry: Dict[str, Any],
        fixer_ids: Optional[List[str]],
    ) -> List[Any]:
        """根据ID列表解析出修复器实例"""
        if fixer_ids is None:
            return list(registry.values())

        resolved = []
        for fid in fixer_ids:
            if fid in registry:
                resolved.append(registry[fid])
            else:
                logger.warning(f"未知的修复器ID: {fid}")

        return resolved

    @classmethod
    def _collect_st_files(cls, project_path: str) -> List[str]:
        """收集项目中所有的ST源码文件"""
        project_dir = Path(project_path)
        st_files = []

        for ext in cls._supported_extensions:
            for file_path in project_dir.rglob(f"*{ext}"):
                if not file_path.is_file():
                    continue

                file_str = str(file_path)
                should_exclude = any(
                    pattern in file_str.lower()
                    for pattern in cls._exclude_patterns
                )

                if not should_exclude:
                    st_files.append(str(file_path))

        st_files.sort()
        return st_files

    @classmethod
    def _scan_single_file(
        cls,
        file_path: str,
        active_fixers: List[Any],
    ) -> FileFixReport:
        """扫描单个文件的可修复问题"""
        from src.fixers.base_fixer import FixIssue

        all_issues: List[FixIssue] = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source_code = f.read()

            for fixer in active_fixers:
                try:
                    issues = fixer.detect(source_code, file_path=file_path)
                    all_issues.extend(issues)
                except Exception as e:
                    logger.error(
                        f"修复器 {fixer.fixer_id} 检测异常 ({Path(file_path).name}): {e}"
                    )

        except Exception as e:
            logger.error(f"读取文件失败: {file_path} - {e}")
            return FileFixReport(
                file_path=file_path,
                error_message=str(e),
            )

        return FileFixReport(
            file_path=file_path,
            issues=all_issues,
            is_dry_run=True,
        )

    @staticmethod
    def _create_backup(file_path: str) -> str:
        """
        创建文件备份(.bak)

        Args:
            file_path: 原始文件路径

        Returns:
            str: 备份文件路径
        """
        backup_path = file_path + ".bak"
        shutil.copy2(file_path, backup_path)
        logger.debug(f"已创建备份: {backup_path}")
        return backup_path
