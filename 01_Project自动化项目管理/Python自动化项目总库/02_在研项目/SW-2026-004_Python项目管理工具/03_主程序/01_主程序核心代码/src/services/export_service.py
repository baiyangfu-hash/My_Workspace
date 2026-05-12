# -*- coding: utf-8 -*-
"""
文档导出服务
"""
import os
from datetime import datetime
from typing import Optional, List

from src.services.project_service import ProjectService
from src.services.statistics_service import StatisticsService
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ExportService:
    """文档导出服务"""
    
    @staticmethod
    def export_project_report(project_id: str, format: str = "markdown", 
                               output_path: str = None) -> tuple[Optional[str], str]:
        """导出项目报告"""
        try:
            project = ProjectService.get_project(project_id)
            if not project:
                return None, "项目不存在"
            
            stats = StatisticsService.get_project_statistics(project_id)
            
            if format == "markdown":
                content = ExportService._generate_project_md(project, stats)
                ext = ".md"
            elif format == "html":
                content = ExportService._generate_project_html(project, stats)
                ext = ".html"
            else:
                content = ExportService._generate_project_text(project, stats)
                ext = ".txt"
            
            if not output_path:
                output_path = os.path.join(
                    project.path,
                    "01_项目文档",
                    f"项目报告_{project.code}{ext}"
                )
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"项目报告导出成功: {output_path}")
            return output_path, ""
            
        except Exception as e:
            logger.exception(f"导出项目报告失败: {e}")
            return None, f"导出失败: {str(e)}"
    
    @staticmethod
    def export_statistics_report(format: str = "markdown",
                                  output_path: str = None) -> tuple[Optional[str], str]:
        """导出统计报告"""
        try:
            content = StatisticsService.export_statistics_report(format)
            
            if format == "markdown":
                ext = ".md"
            elif format == "html":
                ext = ".html"
            else:
                ext = ".txt"
            
            if not output_path:
                from pathlib import Path
                output_dir = Path("data/reports")
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = str(output_dir / f"统计报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}")
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"统计报告导出成功: {output_path}")
            return output_path, ""
            
        except Exception as e:
            logger.exception(f"导出统计报告失败: {e}")
            return None, f"导出失败: {str(e)}"
    
    @staticmethod
    def _generate_project_md(project, stats: dict) -> str:
        """生成Markdown格式项目报告"""
        return f"""# {project.name} 项目报告

**项目编号**: {project.code}  
**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## 一、项目基本信息

| 项目 | 内容 |
|------|------|
| 项目编号 | {project.code} |
| 项目名称 | {project.name} |
| 业务线 | {project.business_line.value if hasattr(project.business_line, 'value') else project.business_line} |
| 项目状态 | {project.status.value if hasattr(project.status, 'value') else project.status} |
| 项目负责人 | {project.manager or '-'} |
| 创建时间 | {project.created_at.strftime('%Y-%m-%d %H:%M') if project.created_at else '-'} |
| 项目路径 | {project.path} |

---

## 二、进度概况

| 指标 | 数值 |
|------|------|
| 总体进度 | {stats.get('progress', {}).get('overall_progress', 0)}% |
| 里程碑数 | {stats.get('milestones', 0)} |
| 任务数 | {stats.get('tasks', 0)} |

### 里程碑统计

| 状态 | 数量 |
|------|------|
| 待开始 | {stats.get('progress', {}).get('milestones', {}).get('pending', 0)} |
| 进行中 | {stats.get('progress', {}).get('milestones', {}).get('in_progress', 0)} |
| 已完成 | {stats.get('progress', {}).get('milestones', {}).get('completed', 0)} |

### 任务统计

| 状态 | 数量 |
|------|------|
| 待开始 | {stats.get('progress', {}).get('tasks', {}).get('pending', 0)} |
| 进行中 | {stats.get('progress', {}).get('tasks', {}).get('in_progress', 0)} |
| 已完成 | {stats.get('progress', {}).get('tasks', {}).get('completed', 0)} |

---

## 三、变更管理

| 状态 | 数量 |
|------|------|
| 变更单总数 | {stats.get('changes', {}).get('total', 0)} |
| 草稿 | {stats.get('changes', {}).get('draft', 0)} |
| 待审批 | {stats.get('changes', {}).get('pending', 0)} |
| 已批准 | {stats.get('changes', {}).get('approved', 0)} |
| 实施中 | {stats.get('changes', {}).get('implementing', 0)} |
| 已完成 | {stats.get('changes', {}).get('completed', 0)} |

---

## 四、项目描述

{project.description or '暂无描述'}

---

*报告由Python项目管理工具自动生成*
"""
    
    @staticmethod
    def _generate_project_html(project, stats: dict) -> str:
        """生成HTML格式项目报告"""
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{project.name} 项目报告</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 20px; max-width: 900px; margin: 0 auto; }}
        h1 {{ color: #2196F3; border-bottom: 2px solid #2196F3; padding-bottom: 10px; }}
        h2 {{ color: #333; margin-top: 30px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        th {{ background-color: #2196F3; color: white; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .info {{ color: #666; font-size: 14px; margin-bottom: 20px; }}
        .footer {{ margin-top: 30px; padding-top: 10px; border-top: 1px solid #ddd; color: #999; font-size: 12px; }}
    </style>
</head>
<body>
    <h1>{project.name} 项目报告</h1>
    <p class="info">项目编号: {project.code} | 生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    
    <h2>一、项目基本信息</h2>
    <table>
        <tr><th>项目</th><th>内容</th></tr>
        <tr><td>项目编号</td><td>{project.code}</td></tr>
        <tr><td>项目名称</td><td>{project.name}</td></tr>
        <tr><td>业务线</td><td>{project.business_line.value if hasattr(project.business_line, 'value') else project.business_line}</td></tr>
        <tr><td>项目状态</td><td>{project.status.value if hasattr(project.status, 'value') else project.status}</td></tr>
        <tr><td>项目负责人</td><td>{project.manager or '-'}</td></tr>
        <tr><td>创建时间</td><td>{project.created_at.strftime('%Y-%m-%d %H:%M') if project.created_at else '-'}</td></tr>
    </table>
    
    <h2>二、进度概况</h2>
    <table>
        <tr><th>指标</th><th>数值</th></tr>
        <tr><td>总体进度</td><td>{stats.get('progress', {}).get('overall_progress', 0)}%</td></tr>
        <tr><td>里程碑数</td><td>{stats.get('milestones', 0)}</td></tr>
        <tr><td>任务数</td><td>{stats.get('tasks', 0)}</td></tr>
    </table>
    
    <h2>三、变更管理</h2>
    <table>
        <tr><th>状态</th><th>数量</th></tr>
        <tr><td>变更单总数</td><td>{stats.get('changes', {}).get('total', 0)}</td></tr>
        <tr><td>草稿</td><td>{stats.get('changes', {}).get('draft', 0)}</td></tr>
        <tr><td>待审批</td><td>{stats.get('changes', {}).get('pending', 0)}</td></tr>
        <tr><td>已完成</td><td>{stats.get('changes', {}).get('completed', 0)}</td></tr>
    </table>
    
    <p class="footer">报告由Python项目管理工具自动生成</p>
</body>
</html>"""
    
    @staticmethod
    def _generate_project_text(project, stats: dict) -> str:
        """生成纯文本格式项目报告"""
        return f"""{project.name} 项目报告
{'='*50}
项目编号: {project.code}
生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

一、项目基本信息
{'-'*30}
项目编号: {project.code}
项目名称: {project.name}
业务线: {project.business_line.value if hasattr(project.business_line, 'value') else project.business_line}
项目状态: {project.status.value if hasattr(project.status, 'value') else project.status}
项目负责人: {project.manager or '-'}
创建时间: {project.created_at.strftime('%Y-%m-%d %H:%M') if project.created_at else '-'}

二、进度概况
{'-'*30}
总体进度: {stats.get('progress', {}).get('overall_progress', 0)}%
里程碑数: {stats.get('milestones', 0)}
任务数: {stats.get('tasks', 0)}

三、变更管理
{'-'*30}
变更单总数: {stats.get('changes', {}).get('total', 0)}

报告由Python项目管理工具自动生成
"""
