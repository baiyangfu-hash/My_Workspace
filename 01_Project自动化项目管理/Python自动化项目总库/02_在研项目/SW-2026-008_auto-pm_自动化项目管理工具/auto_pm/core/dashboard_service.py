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

from datetime import datetime
from typing import Any

from auto_pm.logging.logging import setup_logger
from auto_pm.models import DashboardSummaryDTO

log = setup_logger(log_level="INFO", app_name="auto_pm")


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
    ) -> None:
        self._project_service = project_service
        self._change_service = change_service
        self._plc_service = plc_service

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
        )
        log.info(
            "驾驶舱摘要统计: total=%d open_changes=%d failed_checks=%d "
            "not_applicable=%d phases=%s",
            summary.total_projects,
            summary.open_change_count,
            summary.failed_check_project_count,
            summary.not_applicable_project_count,
            summary.phase_counts,
        )
        return summary

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
            if project.stack != "plc":
                continue
            try:
                result = self._plc_service.check(project.path)
            except Exception as exc:  # pragma: no cover - 防御性日志
                log.warning("驾驶舱检查 PLC 项目失败，已跳过: %s: %s", project.project_id, exc)
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
    ) -> list[str]:
        """汇总最近活动（最近修改项目 + 最近变更单）"""
        activities: list[tuple[float, str]] = []

        for project in projects:
            if not project.file_mtime:
                continue
            formatted_time = self._format_timestamp(project.file_mtime)
            activities.append(
                (
                    float(project.file_mtime),
                    f"[项目] {project.project_id} 于 {formatted_time} 更新",
                )
            )

        for change in changes:
            sort_key = self._parse_date_to_timestamp(change.apply_date)
            if sort_key <= 0:
                continue
            activities.append(
                (
                    sort_key,
                    f"[变更] {change.change_number} ({change.status}) 申请日期 {change.apply_date}",
                )
            )

        activities.sort(key=lambda item: item[0], reverse=True)
        return [text for _, text in activities[:limit]]

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
        # V0.4.1 Step 3: not_applicable 是信息提示，不是风险项
        # （仅当存在 not_applicable 项目但无 failed 时给出说明，避免风险提示为空时的混淆）
        if not_applicable_project_ids and not failed_project_ids:
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
