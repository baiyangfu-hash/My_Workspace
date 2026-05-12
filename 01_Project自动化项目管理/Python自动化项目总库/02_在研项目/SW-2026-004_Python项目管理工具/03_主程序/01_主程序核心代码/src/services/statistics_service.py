# -*- coding: utf-8 -*-
"""
数据统计服务
"""
from typing import Dict, Any, List

from src.services.project_service import ProjectService
from src.services.change_service import ChangeService
from src.services.progress_service import ProgressService
from src.services.plugin_service import PluginService
from src.dao.project_dao import ProjectDAO
from src.dao.change_dao import ChangeDAO
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class StatisticsService:
    """数据统计服务"""
    
    @staticmethod
    def get_overview() -> Dict[str, Any]:
        """获取系统概览统计"""
        projects, _ = ProjectService.list_projects(size=1000)
        
        total_projects = len(projects)
        active_projects = sum(1 for p in projects if p.status.value == "active")
        completed_projects = sum(1 for p in projects if p.status.value == "completed")
        archived_projects = sum(1 for p in projects if p.status.value == "archived")
        
        business_line_stats = {}
        for p in projects:
            bl = p.business_line.value if hasattr(p.business_line, 'value') else str(p.business_line)
            business_line_stats[bl] = business_line_stats.get(bl, 0) + 1
        
        plugins = PluginService.list_plugins()
        enabled_plugins = sum(1 for p in plugins if p.status.value == "enabled")
        
        return {
            "projects": {
                "total": total_projects,
                "active": active_projects,
                "completed": completed_projects,
                "archived": archived_projects
            },
            "business_lines": business_line_stats,
            "plugins": {
                "total": len(plugins),
                "enabled": enabled_plugins
            }
        }
    
    @staticmethod
    def get_project_statistics(project_id: str) -> Dict[str, Any]:
        """获取项目统计"""
        project = ProjectService.get_project(project_id)
        if not project:
            return {}
        
        change_stats = ChangeService.get_statistics(project_id)
        progress_stats = ProgressService.get_statistics(project_id)
        
        from dao.milestone_dao import MilestoneDAO
        from dao.task_dao import TaskDAO
        
        milestone_count = MilestoneDAO.count_by_project(project_id)
        task_count = TaskDAO.count_by_project(project_id)
        
        return {
            "project": {
                "code": project.code,
                "name": project.name,
                "status": project.status.value if hasattr(project.status, 'value') else str(project.status),
                "business_line": project.business_line.value if hasattr(project.business_line, 'value') else str(project.business_line),
                "manager": project.manager,
                "created_at": project.created_at.isoformat() if project.created_at else None
            },
            "changes": change_stats,
            "progress": progress_stats,
            "milestones": milestone_count,
            "tasks": task_count
        }
    
    @staticmethod
    def get_monthly_project_trend() -> List[Dict[str, Any]]:
        """获取项目月度趋势"""
        from datetime import datetime, timedelta
        from collections import defaultdict
        
        projects, _ = ProjectService.list_projects(size=1000)
        
        monthly_stats = defaultdict(lambda: {"created": 0, "completed": 0})
        
        for p in projects:
            if p.created_at:
                month_key = p.created_at.strftime("%Y-%m")
                monthly_stats[month_key]["created"] += 1
            
            if p.status.value == "completed" and p.updated_at:
                month_key = p.updated_at.strftime("%Y-%m")
                monthly_stats[month_key]["completed"] += 1
        
        result = []
        for month in sorted(monthly_stats.keys()):
            result.append({
                "month": month,
                "created": monthly_stats[month]["created"],
                "completed": monthly_stats[month]["completed"]
            })
        
        return result[-12:] if len(result) > 12 else result
    
    @staticmethod
    def get_change_statistics() -> Dict[str, Any]:
        """获取变更统计"""
        projects, _ = ProjectService.list_projects(size=1000)
        
        total_changes = 0
        status_distribution = {}
        type_distribution = {}
        
        for project in projects:
            stats = ChangeService.get_statistics(project.project_id)
            total_changes += stats.get("total", 0)
            
            for status, count in stats.items():
                if status != "total" and count > 0:
                    status_distribution[status] = status_distribution.get(status, 0) + count
        
        return {
            "total": total_changes,
            "by_status": status_distribution,
            "by_type": type_distribution
        }
    
    @staticmethod
    def export_statistics_report(format: str = "markdown") -> str:
        """导出统计报告"""
        overview = StatisticsService.get_overview()
        change_stats = StatisticsService.get_change_statistics()
        monthly_trend = StatisticsService.get_monthly_project_trend()
        
        if format == "markdown":
            return StatisticsService._generate_markdown_report(overview, change_stats, monthly_trend)
        elif format == "html":
            return StatisticsService._generate_html_report(overview, change_stats, monthly_trend)
        else:
            return StatisticsService._generate_text_report(overview, change_stats, monthly_trend)
    
    @staticmethod
    def _generate_markdown_report(overview: dict, change_stats: dict, monthly_trend: list) -> str:
        """生成Markdown格式报告"""
        from datetime import datetime
        
        report = f"""# 项目管理统计报告

**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## 一、项目概览

| 指标 | 数量 |
|------|------|
| 项目总数 | {overview['projects']['total']} |
| 进行中 | {overview['projects']['active']} |
| 已完成 | {overview['projects']['completed']} |
| 已归档 | {overview['projects']['archived']} |

### 业务线分布

| 业务线 | 项目数 |
|--------|--------|
"""
        for bl, count in overview['business_lines'].items():
            report += f"| {bl} | {count} |\n"
        
        report += f"""
---

## 二、变更统计

| 指标 | 数量 |
|------|------|
| 变更单总数 | {change_stats['total']} |

### 状态分布

| 状态 | 数量 |
|------|------|
"""
        for status, count in change_stats['by_status'].items():
            report += f"| {status} | {count} |\n"
        
        report += """
---

## 三、月度趋势

| 月份 | 新建项目 | 完成项目 |
|------|---------|---------|
"""
        for item in monthly_trend:
            report += f"| {item['month']} | {item['created']} | {item['completed']} |\n"
        
        report += """
---

## 四、插件统计

"""
        report += f"- 已安装插件: {overview['plugins']['total']}个\n"
        report += f"- 已启用插件: {overview['plugins']['enabled']}个\n"
        
        return report
    
    @staticmethod
    def _generate_html_report(overview: dict, change_stats: dict, monthly_trend: list) -> str:
        """生成HTML格式报告"""
        from datetime import datetime
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>项目管理统计报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>项目管理统计报告</h1>
    <p><strong>生成时间</strong>: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    
    <h2>一、项目概览</h2>
    <table>
        <tr><th>指标</th><th>数量</th></tr>
        <tr><td>项目总数</td><td>{overview['projects']['total']}</td></tr>
        <tr><td>进行中</td><td>{overview['projects']['active']}</td></tr>
        <tr><td>已完成</td><td>{overview['projects']['completed']}</td></tr>
        <tr><td>已归档</td><td>{overview['projects']['archived']}</td></tr>
    </table>
    
    <h2>二、变更统计</h2>
    <table>
        <tr><th>指标</th><th>数量</th></tr>
        <tr><td>变更单总数</td><td>{change_stats['total']}</td></tr>
    </table>
    
    <h2>三、月度趋势</h2>
    <table>
        <tr><th>月份</th><th>新建项目</th><th>完成项目</th></tr>
"""
        for item in monthly_trend:
            html += f"        <tr><td>{item['month']}</td><td>{item['created']}</td><td>{item['completed']}</td></tr>\n"
        
        html += """    </table>
</body>
</html>"""
        
        return html
    
    @staticmethod
    def _generate_text_report(overview: dict, change_stats: dict, monthly_trend: list) -> str:
        """生成纯文本格式报告"""
        from datetime import datetime
        
        report = f"""项目管理统计报告
{'='*50}
生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

一、项目概览
{'-'*30}
项目总数: {overview['projects']['total']}
进行中: {overview['projects']['active']}
已完成: {overview['projects']['completed']}
已归档: {overview['projects']['archived']}

二、变更统计
{'-'*30}
变更单总数: {change_stats['total']}

三、月度趋势
{'-'*30}
"""
        for item in monthly_trend:
            report += f"{item['month']}: 新建 {item['created']} | 完成 {item['completed']}\n"
        
        return report
