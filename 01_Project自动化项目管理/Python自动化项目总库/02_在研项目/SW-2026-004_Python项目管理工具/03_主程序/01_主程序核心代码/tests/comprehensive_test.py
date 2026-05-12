# -*- coding: utf-8 -*-
"""
全面测试脚本
测试范围:
1. 总库管理功能
2. 监控与统计功能
3. 变更管理功能
4. 统一管理功能
"""
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(project_root))

from datetime import date

class ComprehensiveTestRunner:
    """全面测试运行器"""
    
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
    
    def add_result(self, name: str, success: bool, message: str = ""):
        """添加测试结果"""
        status = "✓ 通过" if success else "✗ 失败"
        self.results.append({
            "name": name,
            "success": success,
            "message": message
        })
        if success:
            self.passed += 1
        else:
            self.failed += 1
        print(f"  {status}: {name} - {message}")
    
    def print_summary(self):
        """打印测试摘要"""
        print("\n" + "="*60)
        print("测试摘要")
        print("="*60)
        print(f"总计: {self.passed + self.failed} 项")
        print(f"通过: {self.passed} 项")
        print(f"失败: {self.failed} 项")
        
        if self.failed > 0:
            print("\n失败项:")
            for r in self.results:
                if not r["success"]:
                    print(f"  - {r['name']}: {r['message']}")
    
    def run_all(self):
        """运行所有测试"""
        print("="*60)
        print("SW-2026-004 Python项目管理工具全面测试")
        print("="*60)
        
        self.test_database()
        self.test_project_management()
        self.test_statistics()
        self.test_change_management()
        self.test_library_management()
        
        self.print_summary()
    
    def test_database(self):
        """测试数据库连接"""
        print("\n[1] 数据库测试")
        
        try:
            from src.dao.database import Database
            from src.models.base import Base
            
            db = Database()
            engine = db.get_engine()
            
            self.add_result("数据库连接", engine is not None, "连接成功")
            
        except Exception as e:
            self.add_result("数据库测试", False, str(e))
    
    def test_project_management(self):
        """测试项目管理功能"""
        print("\n[2] 项目管理测试")
        
        try:
            from src.services.project_service import ProjectService
            from src.services.template_service import TemplateService
            
            # 测试项目列表
            projects, total = ProjectService.list_projects(size=10)
            self.add_result("项目列表查询", True, f"共{total}个项目")
            
            # 测试项目统计
            stats = ProjectService.get_statistics()
            self.add_result("项目统计", True, f"总计{stats.get('total', 0)}个项目")
            
            # 测试模板列表
            templates = TemplateService.list_templates()
            self.add_result("模板列表", len(templates) > 0, f"共{len(templates)}个模板")
            
        except Exception as e:
            self.add_result("项目管理测试", False, str(e))
    
    def test_statistics(self):
        """测试统计功能"""
        print("\n[3] 统计功能测试")
        
        try:
            from src.services.statistics_service import StatisticsService
            
            # 测试系统概览
            overview = StatisticsService.get_overview()
            self.add_result("系统概览统计", True, 
                           f"{overview['projects']['total']}个项目")
            
            # 测试变更统计
            change_stats = StatisticsService.get_change_statistics()
            self.add_result("变更统计", True, f"共{change_stats['total']}条变更")
            
            # 测试月度趋势
            monthly_trend = StatisticsService.get_monthly_project_trend()
            self.add_result("月度趋势", True, f"{len(monthly_trend)}个月份")
            
            # 测试报告生成
            report = StatisticsService.export_statistics_report("markdown")
            self.add_result("生成Markdown报告", len(report) > 0, f"{len(report)}字符")
            
        except Exception as e:
            self.add_result("统计功能测试", False, str(e))
    
    def test_change_management(self):
        """测试变更管理功能"""
        print("\n[4] 变更管理测试")
        
        try:
            from src.services.change_service import ChangeService
            from src.services.project_service import ProjectService
            
            # 获取测试项目
            projects, total = ProjectService.list_projects(size=10)
            if projects and len(projects) > 0:
                project_id = projects[0].project_id
                
                # 测试变更统计
                stats = ChangeService.get_statistics(project_id)
                self.add_result("变更统计", True, f"总计{stats.get('total', 0)}条变更")
            else:
                self.add_result("变更管理", False, "没有测试项目")
            
        except Exception as e:
            self.add_result("变更管理测试", False, str(e))
    
    def test_library_management(self):
        """测试总库管理功能"""
        print("\n[5] 总库管理测试")
        
        try:
            from src.services.library_service import LibraryService
            from src.services.library_dashboard_service import LibraryDashboardService
            
            # 测试总库列表
            libraries = LibraryService.list_libraries()
            self.add_result("总库列表", True, f"共{len(libraries)}个总库")
            
            # 测试总库统计
            dashboard = LibraryDashboardService.get_dashboard_data()
            self.add_result("总库统计", True, f"共{dashboard.get('total_libraries', 0)}个总库")
            
        except Exception as e:
            self.add_result("总库管理测试", False, str(e))


def main():
    """主函数"""
    runner = ComprehensiveTestRunner()
    runner.run_all()
    
    return 0 if runner.failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
