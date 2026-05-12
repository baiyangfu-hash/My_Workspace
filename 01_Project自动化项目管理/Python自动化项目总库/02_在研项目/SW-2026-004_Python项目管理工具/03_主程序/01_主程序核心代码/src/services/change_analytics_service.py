# -*- coding: utf-8 -*-
"""
变更分析服务
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from src.dao.change_dao import ChangeDAO
from src.core.constants import ChangeStatus, ChangeType
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ChangeAnalyticsService:
    """变更分析服务"""
    
    @staticmethod
    def get_change_trends(project_id: str, period: str = "month") -> Dict:
        """获取变更趋势"""
        try:
            # 获取时间范围
            end_date = datetime.now()
            if period == "week":
                start_date = end_date - timedelta(days=7)
            elif period == "month":
                start_date = end_date - timedelta(days=30)
            elif period == "quarter":
                start_date = end_date - timedelta(days=90)
            elif period == "year":
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=30)
            
            # 获取变更数据
            changes = ChangeDAO.get_by_date_range(project_id, start_date, end_date)
            
            # 按时间周期聚合
            trend_data = ChangeAnalyticsService._aggregate_by_period(changes, period)
            
            return {
                "period": period,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "trend_data": trend_data
            }
            
        except Exception as e:
            logger.exception(f"获取变更趋势失败: {e}")
            return {"error": f"获取变更趋势失败: {str(e)}"}
    
    @staticmethod
    def generate_statistics_report(project_id: str, format: str = "pdf") -> str:
        """生成统计报告"""
        try:
            # 收集统计数据
            stats = ChangeDAO.get_statistics(project_id)
            
            # 生成报告内容
            report_content = ChangeAnalyticsService._generate_report_content(project_id, stats)
            
            # 这里可以根据format参数生成不同格式的报告
            # 暂时返回文本内容
            return report_content
            
        except Exception as e:
            logger.exception(f"生成统计报告失败: {e}")
            return f"生成统计报告失败: {str(e)}"
    
    @staticmethod
    def get_change_distribution(project_id: str) -> Dict:
        """获取变更分布"""
        try:
            # 按类型统计
            type_distribution = ChangeDAO.count_by_type(project_id)
            
            # 按状态统计
            status_distribution = ChangeDAO.count_by_status(project_id)
            
            return {
                "type_distribution": type_distribution,
                "status_distribution": status_distribution
            }
            
        except Exception as e:
            logger.exception(f"获取变更分布失败: {e}")
            return {"error": f"获取变更分布失败: {str(e)}"}
    
    @staticmethod
    def _aggregate_by_period(changes: List, period: str) -> List[Dict]:
        """按时间周期聚合数据"""
        aggregated = []
        time_format = "%Y-%m-%d" if period in ["week", "month"] else "%Y-%m"
        
        # 按日期分组
        grouped = {}
        for change in changes:
            date_key = change.created_at.strftime(time_format)
            if date_key not in grouped:
                grouped[date_key] = 0
            grouped[date_key] += 1
        
        # 转换为列表格式
        for date_key, count in sorted(grouped.items()):
            aggregated.append({
                "date": date_key,
                "count": count
            })
        
        return aggregated
    
    @staticmethod
    def _generate_report_content(project_id: str, stats: Dict) -> str:
        """生成报告内容"""
        report = []
        report.append(f"# 变更统计报告")
        report.append(f"项目ID: {project_id}")
        report.append(f"生成日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        report.append("## 统计概览")
        report.append(f"- 总变更数: {stats.get('total', 0)}")
        report.append(f"- 草稿: {stats.get('draft', 0)}")
        report.append(f"- 待审批: {stats.get('pending', 0)}")
        report.append(f"- 已批准: {stats.get('approved', 0)}")
        report.append(f"- 实施中: {stats.get('implementing', 0)}")
        report.append(f"- 已完成: {stats.get('completed', 0)}")
        report.append(f"- 已拒绝: {stats.get('rejected', 0)}")
        report.append(f"- 已取消: {stats.get('cancelled', 0)}")
        report.append("")
        report.append("## 变更类型分布")
        for change_type in ChangeType:
            count = stats.get(f"type_{change_type.value}", 0)
            report.append(f"- {change_type.value}: {count}")
        report.append("")
        report.append("## 变更趋势")
        report.append("(趋势图表将在此处显示)")
        report.append("")
        report.append("## 结论与建议")
        report.append("1. 分析变更频率和类型分布")
        report.append("2. 识别变更热点和潜在风险")
        report.append("3. 优化变更管理流程")
        
        return "\n".join(report)
