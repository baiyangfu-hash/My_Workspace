"""项目驾驶舱 Service - 首页聚合统计

聚合 ProjectService / ChangeService / PlcService 的最小首页数据：
- 项目总数
- 阶段分布
- 未关闭变更数
- PLC 检查失败项目数（fail_count > 0）
- PLC 检查不适用项目数（Python 项目，V0.4.1 Step 3 新增）

Week 1 只做数据聚合，不引入新表，不持久化检查结果。
V0.4.1 Step 3: 增加 not_applicable 口径，避免 Python 项目误报为 PLC 检查失败。
"""

from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime
from typing import Any

from auto_pm.models import DashboardSummaryDTO

log = logging.getLogger(__name__)


class DashboardService:
    """项目驾驶舱数据聚合服务"""

    _PHASE_KEYS: tuple[str, ...] = (
        "developing",
        "commissioning",
        "production",
        "archived",
    )

    def __init__(
        self,
        project_service: Any,
        change_service: Any,
        plc_service: Any | None = None,
        workspace_root: str | None = None,
    ) -> None:
        self._project_service = project_service
        self._change_service = change_service
        self._plc_service = plc_service
        # CHG-106 新增：用于定位 006 报告和 .pytest_cache
        self._workspace_root = workspace_root

    def get_summary(self) -> DashboardSummaryDTO:
        """返回首页驾驶舱摘要数据"""
        projects = self._project_service.list_projects_cached()
        changes = self._change_service.list_all_changes()

        phase_counts = {key: 0 for key in self._PHASE_KEYS}
        for project in projects:
            phase_key = project.phase or ""
            phase_counts[phase_key] = phase_counts.get(phase_key, 0) + 1

        open_changes = [change for change in changes if change.status != "closed"]
        # V0.4.1 Step 3: 一次遍历收集 failed + not_applicable，避免重复跑 PlcChecker.check
        failed_project_ids, not_applicable_ids = self._collect_plc_check_stats(projects)
        recent_activities = self._collect_recent_activities(projects, changes)
        risk_hints = self._collect_risk_hints(
            open_changes, failed_project_ids, not_applicable_ids
        )
        # CHG-106 新增：技术债计数 + 测试通过率
        tech_debt_remaining, tech_debt_total = self._collect_tech_debt_summary()
        test_pass_rate, test_total = self._collect_test_summary()

        summary = DashboardSummaryDTO(
            total_projects=len(projects),
            phase_counts=phase_counts,
            open_change_count=len(open_changes),
            failed_check_project_count=len(failed_project_ids),
            failed_check_project_ids=failed_project_ids,
            not_applicable_project_count=len(not_applicable_ids),
            not_applicable_project_ids=not_applicable_ids,
            recent_activities=recent_activities,
            risk_hints=risk_hints,
            tech_debt_count=tech_debt_remaining,
            tech_debt_total=tech_debt_total,
            test_pass_rate=test_pass_rate,
            test_total=test_total,
        )
        log.info(
            "驾驶舱摘要统计: total=%d open_changes=%d failed_checks=%d "
            "not_applicable=%d phases=%s tech_debt=%d/%d test_rate=%.1f%%(%d)",
            summary.total_projects,
            summary.open_change_count,
            summary.failed_check_project_count,
            summary.not_applicable_project_count,
            summary.phase_counts,
            summary.tech_debt_count,
            summary.tech_debt_total,
            summary.test_pass_rate,
            summary.test_total,
        )
        return summary

    def get_active_change_for_project(self, project_id: str) -> Any | None:
        """获取项目最近一条活跃变更单（CHG-106 新增）

        活跃定义：status 不在 (completed, closed) 中。
        用于平台驾驶舱状态机视图的主线变更展示。

        Args:
            project_id: 项目编号

        Returns:
            最近活跃变更单 ChangeSummary，若无则返回 None
        """
        try:
            changes = self._change_service.list_all_changes(project_id=project_id)
        except Exception as exc:  # pragma: no cover - 防御性日志
            log.warning("查询项目活跃变更失败 %s: %s", project_id, exc)
            return None

        active_changes = [
            c for c in changes if c.status not in ("completed", "closed")
        ]
        if not active_changes:
            return None

        # 按 apply_date 降序取最近一条（apply_date 格式 YYYY-MM-DD）
        active_changes.sort(
            key=lambda c: self._parse_date_to_timestamp(c.apply_date),
            reverse=True,
        )
        return active_changes[0]

    def _collect_plc_check_stats(
        self, projects: list[Any]
    ) -> tuple[list[str], list[str]]:
        """一次遍历收集 PLC 检查统计

        V0.4.1 Step 3: 合并 failed + not_applicable 收集，避免重复跑 PlcChecker.check。
        not_applicable 短路返回不跑 5 项检查，性能开销可忽略。

        Returns:
            (failed_project_ids, not_applicable_project_ids) 元组
            - failed_project_ids: PLC 检查 fail_count > 0 的项目编号（真失败）
            - not_applicable_project_ids: Python 项目（not_applicable=True）编号
        """
        if self._plc_service is None:
            return [], []

        failed_project_ids: list[str] = []
        not_applicable_project_ids: list[str] = []
        for project in projects:
            try:
                result = self._plc_service.check(project.path)
            except Exception as exc:  # pragma: no cover - 防御性日志
                log.warning("驾驶舱检查项目失败，已跳过: %s: %s", project.project_id, exc)
                continue
            # V0.4.1 Step 3: not_applicable 项目（Python 项目）不计入 failed
            if result.not_applicable:
                not_applicable_project_ids.append(project.project_id)
                continue
            if result.fail_count > 0:
                failed_project_ids.append(project.project_id)
        return failed_project_ids, not_applicable_project_ids

    def _collect_recent_activities(
        self,
        projects: list[Any],
        changes: list[Any],
        limit: int = 4,
    ) -> list[dict[str, Any]]:
        """汇总最近活动（最近修改项目 + 最近变更单）

        CHG-106: 返回格式从 list[str] 改为 list[dict]，匹配 V7 时间线 {type, title, desc, time}。
        """
        activities: list[tuple[float, dict[str, Any]]] = []

        for project in projects:
            if not project.file_mtime:
                continue
            formatted_time = self._format_timestamp(project.file_mtime)
            activities.append(
                (
                    float(project.file_mtime),
                    {
                        "type": "default",
                        "title": f"项目更新 {project.project_id}",
                        "desc": project.name or project.project_id,
                        "time": formatted_time,
                    },
                )
            )

        for change in changes:
            sort_key = self._parse_date_to_timestamp(change.apply_date)
            if sort_key <= 0:
                continue
            # 开放变更用 success（绿色），已关闭用 default（灰色）
            activity_type = "success" if change.status != "closed" else "default"
            activities.append(
                (
                    sort_key,
                    {
                        "type": activity_type,
                        "title": f"变更单 {change.change_number}",
                        "desc": f"状态: {change.status} | 申请日期: {change.apply_date}",
                        "time": change.apply_date,
                    },
                )
            )

        activities.sort(key=lambda item: item[0], reverse=True)
        return [item[1] for item in activities[:limit]]

    def _collect_tech_debt_summary(self) -> tuple[int, int]:
        """收集技术债摘要（CHG-106 新增）

        解析 006 技术债评估报告 §0.1 总览表合计行，返回 (remaining, total)。
        解析失败或文件不存在时返回 (0, 0)。

        Returns:
            (remaining, total) 元组
            - remaining: 遗留技术债数（剩余未治理）
            - total: 技术债总数（历史累计）
        """
        report_path = self._find_tech_debt_report()
        if not report_path or not os.path.isfile(report_path):
            log.debug("技术债报告未找到: workspace_root=%s", self._workspace_root)
            return 0, 0

        try:
            with open(report_path, encoding="utf-8") as f:
                content = f.read()
        except OSError as exc:
            log.warning("读取技术债报告失败: %s: %s", report_path, exc)
            return 0, 0

        # 匹配合计行: | **合计** | **35 项** | **35 项** | **0 项** | ✅ 全部偿还 |
        # 或: | **合计** | **35 项** | **34 项** | **1 项** | 🟡 中（TD-A04 待治理） |
        match = re.search(
            r"\|\s*\*\*合计\*\*\s*\|\s*\*\*(\d+)\s*项\*\*\s*\|\s*\*\*(\d+)\s*项\*\*\s*\|\s*\*\*(\d+)\s*项\*\*\s*\|",
            content,
        )
        if not match:
            log.debug("技术债合计行未匹配: %s", report_path)
            return 0, 0

        total = int(match.group(1))
        # remaining 是第 3 个数字（剩余未治理）
        remaining = int(match.group(3))
        log.debug("技术债解析: total=%d remaining=%d", total, remaining)
        return remaining, total

    def _find_tech_debt_report(self) -> str | None:
        """定位 006 技术债评估报告文件路径

        查找顺序：
        1. workspace_root/00_项目基础信息/006_技术债评估报告.md
        2. 项目列表中 stack='python' 项目的 00_项目基础信息/006_技术债评估报告.md
        """
        if self._workspace_root:
            candidate = os.path.join(
                self._workspace_root, "00_项目基础信息", "006_技术债评估报告.md"
            )
            if os.path.isfile(candidate):
                return candidate

        # 从项目列表中查找 Python 项目（auto-pm 自身）
        try:
            projects = self._project_service.list_projects_cached()
            for project in projects:
                if getattr(project, "stack", "") == "python":
                    candidate = os.path.join(
                        project.path, "00_项目基础信息", "006_技术债评估报告.md"
                    )
                    if os.path.isfile(candidate):
                        return candidate
        except Exception as exc:  # pragma: no cover - 防御性日志
            log.warning("查找技术债报告时列举项目失败: %s", exc)

        return None

    def _collect_test_summary(self) -> tuple[float, int]:
        """收集测试通过率摘要（CHG-106 新增）

        读取 .pytest_cache 统计测试总数和失败数，返回 (pass_rate, total)。
        .pytest_cache 不存在时返回 (0.0, 0)。

        Returns:
            (pass_rate, total) 元组
            - pass_rate: 通过率（0-100）
            - total: 测试总数
        """
        cache_dir = self._find_pytest_cache()
        if not cache_dir:
            return 0.0, 0

        nodeids_file = os.path.join(cache_dir, "v", "cache", "nodeids")
        lastfailed_file = os.path.join(cache_dir, "v", "cache", "lastfailed")

        try:
            with open(nodeids_file, encoding="utf-8") as f:
                nodeids_data = json.load(f)
            # nodeids 格式: {"tests/test_foo.py::test_bar": true, ...}
            total = len(nodeids_data) if isinstance(nodeids_data, dict) else 0
        except (OSError, json.JSONDecodeError):
            log.debug("pytest nodeids 读取失败: %s", nodeids_file)
            return 0.0, 0

        if total == 0:
            return 0.0, 0

        try:
            with open(lastfailed_file, encoding="utf-8") as f:
                lastfailed_data = json.load(f)
            failed = len(lastfailed_data) if isinstance(lastfailed_data, dict) else 0
        except (OSError, json.JSONDecodeError):
            # lastfailed 不存在表示没有失败
            failed = 0

        passed = total - failed
        pass_rate = round((passed / total) * 100, 1) if total > 0 else 0.0
        log.debug("测试统计: total=%d failed=%d pass_rate=%.1f%%", total, failed, pass_rate)
        return pass_rate, total

    def _find_pytest_cache(self) -> str | None:
        """定位 .pytest_cache 目录

        查找顺序：
        1. workspace_root/.pytest_cache
        2. 项目列表中 stack='python' 项目的 .pytest_cache
        """
        if self._workspace_root:
            candidate = os.path.join(self._workspace_root, ".pytest_cache")
            if os.path.isdir(candidate):
                return candidate

        try:
            projects = self._project_service.list_projects_cached()
            for project in projects:
                if getattr(project, "stack", "") == "python":
                    candidate = os.path.join(project.path, ".pytest_cache")
                    if os.path.isdir(candidate):
                        return candidate
        except Exception as exc:  # pragma: no cover - 防御性日志
            log.warning("查找 .pytest_cache 时列举项目失败: %s", exc)

        return None

    @staticmethod
    def _collect_risk_hints(
        open_changes: list[Any],
        failed_project_ids: list[str],
        not_applicable_project_ids: list[str] | None = None,
    ) -> list[str]:
        """生成首页风险提示文案

        V0.4.1 Step 3: 区分「PLC 检查失败项目」（真失败，需处理）与
        「PLC 检查不适用项目」（Python 项目，正常口径，不计入风险提示）。
        not_applicable 仅在信息提示中说明，不计入风险项。
        """
        hints: list[str] = []
        if open_changes:
            hints.append(f"存在 {len(open_changes)} 条未关闭变更，建议优先清理实施中和待验收项")
        if failed_project_ids:
            joined_ids = ", ".join(failed_project_ids[:3])
            suffix = " 等" if len(failed_project_ids) > 3 else ""
            hints.append(f"PLC 检查失败项目: {joined_ids}{suffix}")
        # V0.4.1 收口批次阶段 4: not_applicable 始终展示口径说明（Python 项目，与 failed 独立）
        if not_applicable_project_ids:
            count = len(not_applicable_project_ids)
            hints.append(
                f"PLC 检查不适用项目: {count} 个（Python 项目，已跳过 PLC 检查）"
            )
        if not hints:
            hints.append("当前未发现高优先级风险")
        return hints

    @staticmethod
    def _format_timestamp(timestamp: float) -> str:
        """格式化时间戳为 YYYY-MM-DD HH:MM"""
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")

    @staticmethod
    def _parse_date_to_timestamp(value: str) -> float:
        """解析 YYYY-MM-DD / YYYY-MM-DD HH:MM[:SS] 日期字符串"""
        if not value or value == "待补充":
            return 0.0
        normalized = value.strip().replace("T", " ")
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
            try:
                return datetime.strptime(normalized, fmt).timestamp()
            except ValueError:
                continue
        return 0.0
