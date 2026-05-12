#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python项目管理工具全面功能测试
测试范围:
1. GUI启动测试
2. API服务测试
3. 项目创建功能测试
4. 规范检查功能测试
5. 所有核心功能模块测试
"""
import sys
import os
import time
import subprocess
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(project_root))

class FullFunctionalTestRunner:
    """全面功能测试运行器"""
    
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.test_start_time = datetime.now()
    
    def add_result(self, name: str, success: bool, message: str = ""):
        """添加测试结果"""
        status = "✓ 通过" if success else "✗ 失败"
        self.results.append({
            "name": name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        if success:
            self.passed += 1
        else:
            self.failed += 1
        print(f"  {status}: {name} - {message}")
    
    def print_summary(self):
        """打印测试摘要"""
        test_end_time = datetime.now()
        duration = (test_end_time - self.test_start_time).total_seconds()
        
        print("\n" + "="*80)
        print("Python项目管理工具全面功能测试报告")
        print("="*80)
        print(f"测试时间: {self.test_start_time.strftime('%Y-%m-%d %H:%M:%S')} 至 {test_end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"测试时长: {duration:.2f} 秒")
        print(f"总计: {self.passed + self.failed} 项")
        print(f"通过: {self.passed} 项")
        print(f"失败: {self.failed} 项")
        print(f"成功率: {self.passed / (self.passed + self.failed) * 100:.2f}%")
        
        if self.failed > 0:
            print("\n失败项:")
            for r in self.results:
                if not r["success"]:
                    print(f"  - {r['name']}: {r['message']} ({r['timestamp']})")
        
        # 生成测试报告文件
        self.generate_test_report()
    
    def generate_test_report(self):
        """生成测试报告文件"""
        report_path = project_root / "data" / "test_reports"
        report_path.mkdir(exist_ok=True)
        report_file = report_path / f"功能测试报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Python项目管理工具全面功能测试报告\n\n")
            f.write(f"**测试时间:** {self.test_start_time.strftime('%Y-%m-%d %H:%M:%S')} 至 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**测试结果:**\n")
            f.write(f"- 总计: {self.passed + self.failed} 项\n")
            f.write(f"- 通过: {self.passed} 项\n")
            f.write(f"- 失败: {self.failed} 项\n")
            f.write(f"- 成功率: {self.passed / (self.passed + self.failed) * 100:.2f}%\n\n")
            
            f.write("## 测试详情\n\n")
            for r in self.results:
                status = "✅ 通过" if r["success"] else "❌ 失败"
                f.write(f"### {status} {r['name']}\n")
                f.write(f"- 时间: {r['timestamp']}\n")
                f.write(f"- 消息: {r['message']}\n\n")
        
        print(f"\n测试报告已生成: {report_file}")
    
    def run_all(self):
        """运行所有测试"""
        print("="*80)
        print("Python项目管理工具全面功能测试")
        print("="*80)
        
        self.test_gui_launch()
        self.test_api_service()
        self.test_database()
        self.test_project_creation()
        self.test_spec_check()
        self.test_core_services()
        self.test_plugins()
        
        self.print_summary()
    
    def test_gui_launch(self):
        """测试GUI启动功能"""
        print("\n[1] GUI启动测试")
        
        try:
            # 检查GUI模块导入
            from src.ui.main_window import MainWindow
            self.add_result("GUI模块导入", True, "成功导入MainWindow类")
            
            # 检查主窗口初始化
            try:
                from PyQt5.QtWidgets import QApplication
                app = QApplication([])
                window = MainWindow()
                self.add_result("主窗口初始化", True, "成功创建MainWindow实例")
                window.close()
                app.quit()
            except Exception as e:
                self.add_result("主窗口初始化", False, f"初始化失败: {str(e)}")
                
        except Exception as e:
            self.add_result("GUI启动测试", False, str(e))
    
    def test_api_service(self):
        """测试API服务功能"""
        print("\n[2] API服务测试")
        
        try:
            from src.api.app import app
            self.add_result("API模块导入", True, "成功导入API应用")
            
            # 测试API路由
            routes = list(app.url_map.iter_rules())
            route_count = len([r for r in routes if not r.rule.startswith('/static')])
            self.add_result("API路由检查", route_count > 0, f"发现{route_count}个API路由")
            
        except Exception as e:
            self.add_result("API服务测试", False, str(e))
    
    def test_database(self):
        """测试数据库连接"""
        print("\n[3] 数据库测试")
        
        try:
            from src.dao.database import Database
            from src.models.base import Base
            
            db = Database()
            engine = db.get_engine()
            
            self.add_result("数据库连接", engine is not None, "连接成功")
            
            # 测试数据库表结构
            inspector = db.get_inspector()
            tables = inspector.get_table_names()
            self.add_result("数据库表结构", len(tables) > 0, f"发现{len(tables)}个表")
            
        except Exception as e:
            self.add_result("数据库测试", False, str(e))
    
    def test_project_creation(self):
        """测试项目创建功能"""
        print("\n[4] 项目创建测试")
        
        try:
            from src.services.project_service import ProjectService
            from src.services.template_service import TemplateService
            
            # 测试项目列表
            projects, total = ProjectService.list_projects(size=10)
            self.add_result("项目列表查询", True, f"共{total}个项目")
            
            # 测试模板列表
            templates = TemplateService.list_templates()
            self.add_result("模板列表查询", len(templates) > 0, f"共{len(templates)}个模板")
            
            # 测试创建测试项目
            test_project_data = {
                "project_name": "测试项目_Test",
                "project_code": "TEST-" + datetime.now().strftime("%Y%m%d"),
                "description": "功能测试项目",
                "template_id": templates[0].template_id if templates else None
            }
            
            if test_project_data["template_id"]:
                project_id = ProjectService.create_project(test_project_data)
                self.add_result("项目创建", project_id is not None, f"成功创建项目ID: {project_id}")
                
                # 测试项目详情
                project = ProjectService.get_project(project_id)
                self.add_result("项目详情查询", project is not None, f"成功获取项目: {project.project_name}")
                
                # 测试项目更新
                update_data = {"description": "更新后的测试项目描述"}
                updated = ProjectService.update_project(project_id, update_data)
                self.add_result("项目更新", updated, "成功更新项目信息")
                
                # 测试项目删除（清理测试数据）
                deleted = ProjectService.delete_project(project_id)
                self.add_result("项目删除", deleted, "成功删除测试项目")
            else:
                self.add_result("项目创建", False, "没有可用模板")
            
        except Exception as e:
            self.add_result("项目创建测试", False, str(e))
    
    def test_spec_check(self):
        """测试规范检查功能"""
        print("\n[5] 规范检查测试")
        
        try:
            from src.services.check_service import CheckService
            
            # 测试规范检查服务
            check_service = CheckService()
            self.add_result("规范检查服务初始化", True, "成功初始化CheckService")
            
            # 测试规范检查功能
            test_code = """def test_function():
    print("test")
"""
            
            check_result = check_service.check_code规范(test_code)
            self.add_result("代码规范检查", isinstance(check_result, dict), "成功执行代码规范检查")
            
        except Exception as e:
            self.add_result("规范检查测试", False, str(e))
    
    def test_core_services(self):
        """测试核心服务功能"""
        print("\n[6] 核心服务测试")
        
        # 测试统计服务
        try:
            from src.services.statistics_service import StatisticsService
            overview = StatisticsService.get_overview()
            self.add_result("统计服务", True, f"成功获取系统概览: {overview['projects']['total']}个项目")
        except Exception as e:
            self.add_result("统计服务", False, str(e))
        
        # 测试变更管理服务
        try:
            from src.services.change_service import ChangeService
            self.add_result("变更管理服务", True, "成功导入ChangeService")
        except Exception as e:
            self.add_result("变更管理服务", False, str(e))
        
        # 测试模板服务
        try:
            from src.services.template_service import TemplateService
            templates = TemplateService.list_templates()
            self.add_result("模板服务", True, f"成功获取{len(templates)}个模板")
        except Exception as e:
            self.add_result("模板服务", False, str(e))
        
        # 测试插件服务
        try:
            from src.services.plugin_service import PluginService
            plugins = PluginService.list_plugins()
            self.add_result("插件服务", True, f"成功获取{len(plugins)}个插件")
        except Exception as e:
            self.add_result("插件服务", False, str(e))
    
    def test_plugins(self):
        """测试插件功能"""
        print("\n[7] 插件功能测试")
        
        try:
            from src.services.plugin_service import PluginService
            
            # 测试插件列表
            plugins = PluginService.list_plugins()
            self.add_result("插件列表", len(plugins) > 0, f"发现{len(plugins)}个插件")
            
            # 测试插件加载
            for plugin in plugins:
                try:
                    loaded = PluginService.load_plugin(plugin.name)
                    self.add_result(f"插件加载: {plugin.name}", loaded, "成功加载插件")
                except Exception as e:
                    self.add_result(f"插件加载: {plugin.name}", False, str(e))
            
        except Exception as e:
            self.add_result("插件功能测试", False, str(e))


def main():
    """主函数"""
    runner = FullFunctionalTestRunner()
    runner.run_all()
    
    return 0 if runner.failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
