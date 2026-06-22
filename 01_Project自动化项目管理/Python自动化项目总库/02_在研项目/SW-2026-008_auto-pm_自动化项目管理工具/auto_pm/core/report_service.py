"""报告 Service - 统计聚合

聚合 ProjectService / ChangeService / 规范目录 / 扫描日志的数据，
提供 4 种报告类型：
- 项目报告（get_project_overview）
- 变更报告（get_change_overview）
- 规范报告（get_spec_report）
- 扫描报告（get_scan_report）

用于报告中心全局页展示。不直接访问文件系统/DB 进行写入，
数据来源完全依赖注入的 Service 和 Repository。
"""

from __future__ import annotations

import glob
import os
from typing import Any, Optional

from auto_pm.logging.logging import setup_logger

log = setup_logger(log_level="INFO", app_name="auto_pm")


# ── 规范元数据（与 ui/global_pages/spec_center.py 保持一致） ────
# M4-Iter3 将统一提取到 core/constants.py

_PLC_SPECS: list[tuple[str, str]] = [
    ("905", "SCL 编程规范"),
    ("904", "SCL 注释规范"),
    ("903", "定时器使用规范"),
    ("906", "错误预防规则"),
]

_PYTHON_SPECS: list[tuple[str, str]] = [
    ("210", "Python 编程规范"),
    ("211", "Python 代码审查规范"),
    ("220", "Python 项目打包规范"),
]

# 技术栈 → (分区标题, 规范目录相对路径, 规范列表)
_STACK_SPECS: dict[str, tuple[str, str, list[tuple[str, str]]]] = {
    "plc": (
        "PLC 技术栈规范",
        os.path.join("0100_PLC自动化", "00_通用规范", "PLC编程"),
        _PLC_SPECS,
    ),
    "python": (
        "Python 技术栈规范",
        os.path.join("01_Project自动化项目管理", "00_通用规范", "Python开发"),
        _PYTHON_SPECS,
    ),
}


class ReportService:
    """报告 Service

    通过注入的 ProjectService / ChangeService 聚合统计数据。
    规范报告和扫描报告依赖 workspace_root 和 db（可选）。

    构造参数向后兼容：仅传入 project_service/change_service 时仍可使用
    项目报告和变更报告；规范报告和扫描报告需要额外传入 workspace_root/db。
    """

    # 固定统计维度（确保返回结构稳定，未知值额外追加 key）
    _STACK_KEYS: list[str] = ["plc", "python", "unknown"]
    _PHASE_KEYS: list[str] = ["developing", "commissioning", "production", "archived"]
    _BL_KEYS: list[str] = ["SW", "DJ", "ZD", "XT", "WX"]

    # 报告类型枚举
    REPORT_PROJECT: str = "project"
    REPORT_CHANGE: str = "change"
    REPORT_SPEC: str = "spec"
    REPORT_SCAN: str = "scan"
    _REPORT_TYPES: tuple[str, ...] = (
        REPORT_PROJECT, REPORT_CHANGE, REPORT_SPEC, REPORT_SCAN,
    )

    def __init__(
        self,
        project_service: object,
        change_service: object,
        workspace_root: str = "",
        db: Optional[object] = None,
    ) -> None:
        self._project_service = project_service
        self._change_service = change_service
        self._workspace_root = os.path.abspath(workspace_root) if workspace_root else ""
        self._db = db

    # ── 项目报告 ──────────────────────────────────────────

    def get_project_overview(self) -> dict:
        """项目概览统计

        Returns:
            {
                'total': int,
                'by_stack': {'plc': int, 'python': int, 'unknown': int},
                'by_phase': {'developing': int, 'commissioning': int,
                             'production': int, 'archived': int},
                'by_business_line': {'SW': int, 'DJ': int, 'ZD': int,
                                     'XT': int, 'WX': int},
            }

        Raises:
            RuntimeError: ProjectService 未注入 DatabaseManager
        """
        projects = self._project_service.list_projects_cached()

        by_stack: dict[str, int] = {k: 0 for k in self._STACK_KEYS}
        by_phase: dict[str, int] = {k: 0 for k in self._PHASE_KEYS}
        by_business_line: dict[str, int] = {k: 0 for k in self._BL_KEYS}

        for p in projects:
            # 技术栈（Stack Literal 仅 plc/python/unknown）
            by_stack[p.stack] = by_stack.get(p.stack, 0) + 1

            # 阶段（ProjectPhase 含 ""，未设置时计入 "" key）
            phase_key = p.phase if p.phase else ""
            by_phase[phase_key] = by_phase.get(phase_key, 0) + 1

            # 业务线（BusinessLine 含 ""，未设置时计入 "" key）
            bl_key = p.business_line if p.business_line else ""
            by_business_line[bl_key] = by_business_line.get(bl_key, 0) + 1

        log.info(
            "项目概览统计: total=%d, stack=%s, phase=%s, bl=%s",
            len(projects), by_stack, by_phase, by_business_line,
        )
        return {
            "total": len(projects),
            "by_stack": by_stack,
            "by_phase": by_phase,
            "by_business_line": by_business_line,
        }

    # ── 变更报告 ──────────────────────────────────────────

    def get_change_overview(self) -> dict:
        """变更统计

        Returns:
            {
                'total': int,
                'by_status': {'draft': int, 'submitted': int, ...},
                'by_domain': {'ELEC': int, 'MECH': int, ...},
            }
        """
        changes = self._change_service.list_all_changes()

        by_status: dict[str, int] = {}
        by_domain: dict[str, int] = {}

        for c in changes:
            status_key = c.status if c.status else ""
            by_status[status_key] = by_status.get(status_key, 0) + 1

            domain_key = c.domain if c.domain else ""
            by_domain[domain_key] = by_domain.get(domain_key, 0) + 1

        log.info(
            "变更统计: total=%d, status=%s, domain=%s",
            len(changes), by_status, by_domain,
        )
        return {
            "total": len(changes),
            "by_status": by_status,
            "by_domain": by_domain,
        }

    # ── 规范报告 ──────────────────────────────────────────

    def get_spec_report(self) -> dict:
        """规范覆盖报告

        扫描 workspace_root 下的规范目录，统计每个技术栈的规范总数、
        已存在数、缺失列表。

        Returns:
            {
                'total': int,                    # 规范总数
                'found': int,                    # 已找到文件数
                'missing': int,                  # 缺失文件数
                'by_stack': {
                    'plc': {'total': int, 'found': int, 'missing': list[str]},
                    'python': {'total': int, 'found': int, 'missing': list[str]},
                },
                'missing_codes': list[str],      # 所有缺失的规范编号
            }

        Raises:
            RuntimeError: 未注入 workspace_root
        """
        if not self._workspace_root:
            raise RuntimeError("未注入 workspace_root，无法生成规范报告")

        by_stack: dict[str, dict[str, Any]] = {}
        total = 0
        found = 0
        missing = 0
        all_missing_codes: list[str] = []

        for stack_key, (_, rel_dir, specs) in _STACK_SPECS.items():
            spec_dir = os.path.join(self._workspace_root, rel_dir)
            stack_total = len(specs)
            stack_found = 0
            stack_missing: list[str] = []

            for code, _name in specs:
                pattern = os.path.join(spec_dir, f"{code}_*.md")
                matches = glob.glob(pattern)
                if matches:
                    stack_found += 1
                else:
                    stack_missing.append(code)
                    all_missing_codes.append(code)

            stack_missing_count = stack_total - stack_found
            total += stack_total
            found += stack_found
            missing += stack_missing_count

            by_stack[stack_key] = {
                "total": stack_total,
                "found": stack_found,
                "missing": stack_missing,
            }

        log.info(
            "规范覆盖统计: total=%d, found=%d, missing=%d, missing_codes=%s",
            total, found, missing, all_missing_codes,
        )
        return {
            "total": total,
            "found": found,
            "missing": missing,
            "by_stack": by_stack,
            "missing_codes": all_missing_codes,
        }

    # ── 扫描报告 ──────────────────────────────────────────

    def get_scan_report(self) -> dict:
        """扫描日志报告

        从 ScanLogRepository 获取扫描日志统计。

        Returns:
            {
                'latest': dict | None,          # 最近一次扫描日志
                'last_sync_time': str,          # 上次同步时间（YYYY-MM-DD HH:MM）或 '—'
                'is_cache_available': bool,     # DB 缓存是否可用
            }

        Raises:
            RuntimeError: 未注入 DatabaseManager
        """
        if self._db is None:
            raise RuntimeError("未注入 DatabaseManager，无法生成扫描报告")

        # 延迟导入避免循环依赖
        from auto_pm.db.repository import ScanLogRepository

        repo = ScanLogRepository(self._db)
        latest = repo.get_latest()

        last_sync_time = "—"
        if latest:
            timestamp = latest.get("timestamp", "")
            if timestamp:
                last_sync_time = timestamp[:16].replace("T", " ")

        log.info(
            "扫描日志报告: latest=%s, last_sync_time=%s",
            latest, last_sync_time,
        )
        return {
            "latest": latest,
            "last_sync_time": last_sync_time,
            "is_cache_available": True,
        }

    # ── 统一入口 ──────────────────────────────────────────

    def get_report(self, report_type: str) -> dict:
        """统一报告入口

        Args:
            report_type: 报告类型
                - 'project': 项目报告
                - 'change': 变更报告
                - 'spec': 规范报告
                - 'scan': 扫描报告

        Returns:
            报告数据字典

        Raises:
            ValueError: 未知报告类型
            RuntimeError: 缺少必要依赖（如未注入 workspace_root/db）
        """
        if report_type == self.REPORT_PROJECT:
            return self.get_project_overview()
        if report_type == self.REPORT_CHANGE:
            return self.get_change_overview()
        if report_type == self.REPORT_SPEC:
            return self.get_spec_report()
        if report_type == self.REPORT_SCAN:
            return self.get_scan_report()
        raise ValueError(
            f"未知报告类型: {report_type}，支持: {self._REPORT_TYPES}"
        )

    def list_report_types(self) -> tuple[str, ...]:
        """列出支持的报告类型"""
        return self._REPORT_TYPES
