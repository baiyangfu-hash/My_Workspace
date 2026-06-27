"""项目驾驶舱 Service - 首页聚合统计

聚合 ProjectService / ChangeService / PlcService 的最小首页数据：
- 项目总数
- 阶段分布
- 未关闭变更数
- PLC 检查失败项目数

Week 1 只做数据聚合，不引入新表，不持久化检查结果。
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
        failed_project_ids = self._collect_failed_plc_projects(projects)
        recent_activities = self._collect_recent_activities(projects, changes)
        risk_hints = self._collect_risk_hints(open_changes, failed_project_ids)

        summary = DashboardSummaryDTO(
            total_projects=len(projects),
            phase_counts=phase_counts,
            open_change_count=len(open_changes),
            failed_check_project_count=len(failed_project_ids),
            failed_check_project_ids=failed_project_ids,
            recent_activities=recent_activities,
            risk_hints=risk_hints,
        )
        log.info(
            "驾驶舱摘要统计: total=%d open_changes=%d failed_checks=%d phases=%s",
            summary.total_projects,
            summary.open_change_count,
            summary.failed_check_project_count,
            summary.phase_counts,
        )
        return summary

    def _collect_failed_plc_projects(self, projects: list[Any]) -> list[str]:
        """检查所有 PLC 项目，收集 fail_count > 0 的项目编号"""
        if self._plc_service is None:
            return []

        failed_project_ids: list[str] = []
        for project in projects:
            if project.stack != "plc":
                continue
            try:
                result = self._plc_service.check(project.path)
            except Exception as exc:  # pragma: no cover - 防御性日志
                log.warning("驾驶舱检查 PLC 项目失败，已跳过: %s: %s", project.project_id, exc)
                continue
            if result.fail_count > 0:
                failed_project_ids.append(project.project_id)
        return failed_project_ids

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
    ) -> list[str]:
        """生成首页风险提示文案"""
        hints: list[str] = []
        if open_changes:
            hints.append(f"存在 {len(open_changes)} 条未关闭变更，建议优先清理实施中和待验收项")
        if failed_project_ids:
            joined_ids = ", ".join(failed_project_ids[:3])
            suffix = " 等" if len(failed_project_ids) > 3 else ""
            hints.append(f"PLC 检查失败项目: {joined_ids}{suffix}")
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
