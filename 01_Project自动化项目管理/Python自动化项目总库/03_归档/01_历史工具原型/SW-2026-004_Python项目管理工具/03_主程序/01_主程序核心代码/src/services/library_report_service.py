# -*- coding: utf-8 -*-
"""
总库报告服务
"""
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import markdown

from src.services.library_dashboard_service import LibraryDashboardService
from src.services.library_version_service import LibraryVersionService
from src.services.library_dependency_service import LibraryDependencyService
from src.utils.file_utils import write_file
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class LibraryReportService:
    """总库报告服务类"""
    
    @staticmethod
    def generate_health_report(library_id: str, output_path: Optional[str] = None) -> tuple[str, str]:
        """
        生成总库健康报告
        
        Args:
            library_id: 总库ID
            output_path: 输出路径，默认为当前目录
        
        Returns:
            (报告路径, 错误信息)，生成成功时错误信息为空
        """
        try:
            # 获取总库仪表盘数据
            dashboard_data = LibraryDashboardService.get_library_dashboard(library_id)
            if not dashboard_data:
                return "", "总库不存在或获取数据失败"
            
            # 生成报告内容
            report_content = LibraryReportService._generate_health_report_content(dashboard_data)
            
            # 生成报告文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"总库健康报告_{dashboard_data['basic_info']['name']}_{timestamp}.md"
            
            # 确定输出路径
            if output_path:
                report_path = Path(output_path) / report_filename
            else:
                report_path = Path.cwd() / report_filename
            
            # 写入报告文件
            write_file(str(report_path), report_content)
            
            logger.info(f"总库健康报告生成成功: {report_path}")
            return str(report_path), ""
            
        except Exception as e:
            logger.exception(f"生成总库健康报告失败: {e}")
            return "", f"生成报告失败: {str(e)}"
    
    @staticmethod
    def _generate_health_report_content(dashboard_data: Dict) -> str:
        """
        生成健康报告内容
        
        Args:
            dashboard_data: 总库仪表盘数据
        
        Returns:
            报告内容（Markdown格式）
        """
        basic_info = dashboard_data.get("basic_info", {})
        overall_health = dashboard_data.get("overall_health", {})
        project_stats = dashboard_data.get("project_stats", {})
        version_stats = dashboard_data.get("version_stats",