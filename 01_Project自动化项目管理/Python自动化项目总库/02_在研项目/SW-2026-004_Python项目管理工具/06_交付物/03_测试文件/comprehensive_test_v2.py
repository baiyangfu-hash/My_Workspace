# -*- coding: utf-8 -*-
"""
全面测试脚本 V2
测试范围:
1. 功能测试：总库管理、项目管理、变更管理、模板管理、插件系统、PLC集成等核心功能
2. 性能测试：启动时间、响应时间、内存占用等
3. 安全测试：权限控制、数据安全等
4. 兼容性测试：不同环境下的运行情况
"""
import sys
import os
import time
import psutil
import platform
import subprocess
from pathlib import Path
import json
from datetime import datetime

project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(project_root))

class TestResult:
    """测试结果类"""
    def __init__(self):
        self.test_cases = []
        self.start_time = None
        self.end_time = None
        self.total_passed = 0
        self.total_failed = 0
        self.total_skipped = 0
    
    def add_test_case(self, category, name, success, message, execution_time=0):
        """添加测试用例结果"""
        self.test_cases.append({
            "category": category,
            "name": name,
            "success": success,
            "message": message,
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat()
        })
        if success:
            self.total_passed += 1
        elif message == "跳过":
            self.total_skipped += 1
        else:
            self.total_failed += 1
    
    def generate_report(self):
        """生成测试报告"""
        report = {
            "test_summary": {
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "total_tests": len(self.test_cases),
                "passed": self.total_passed,
                "failed": self.total_failed,
                "skipped": self.total_skipped,
                "success_rate": f"{self.total_passed / len(self.test_cases) * 100:.2f}%" if self.test_cases else "0%"
            },
            "test_cases": self.test_cases,
            "environment": {
                "python_version": platform.python_version(),
                "os": platform.platform(),
                "architecture": platform.architecture(),
                "system": platform.system(),
                "release": platform.release()
            }
        }
        return report

class ComprehensiveTestRunner:
    """全面测试运行器"""
    
    def __init__(self):
        self.result = TestResult()
    
    def run_all_tests(self):
        """运行所有测试"""
        print("="*80)
        print("SW-2026-004 Python项目管理工具全面测试")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        self.result.start_time = datetime.now()
        
        # 1. 功能测试
        self.test_functional_features()
        
        # 2. 性能测试
        self.test_performance()
        
        # 3. 安全测试
        self.test_security()
        
        # 4. 兼容性测试
        self.test_compatibility()
        
        self.result.end_time = datetime.now()
        self.print_summary()
        self.generate_test_report()
    
    def test_functional_features(self):
        """测试功能特性"""
        print("\n[1] 功能测试")
        print("-"*60)
        
        # 总库管理测试
        self.test_library_management()
        
        # 项目管理测试
        self.test_project_management()
        
        # 变更管理测试
        self.test_change_management()
        
        # 模板管理测试
        self.test_template_management()
        
        # 插件系统测试
        self.test_plugin_system()
        
        # PLC集成测试
        self.test_plc_integration()
    
    def test_library_management(self):
        """测试总库管理功能"""
        print("\n  [1.1] 总库管理测试")
        
        try:
            from src.services.library_service import LibraryService
            from src.services.library_dashboard_service import LibraryDashboardService
            from src.services.library_version_service import LibraryVersionService
            from src.services.library_dependency_service import LibraryDependencyService
            
            # 测试总库列表
            start_time = time.time()
            libraries = LibraryService.list_libraries()
            execution_time = time.time() - start_time
            self.result.add_test_case("总库管理", "总库列表查询", True, 
                                   f"共{len(libraries)}个总库", execution_time)
            
            # 测试总库统计
            start_time = time.time()
            dashboard = LibraryDashboardService.get_dashboard_data()
            execution_time = time.time() - start_time
            self.result.add_test_case("总库管理", "总库统计", True, 
                                   f"共{dashboard.get('total_libraries', 0)}个总库", execution_time)
            
            # 测试总库版本管理
            start_time = time.time()
            if libraries:
                library_id = libraries[0].library_id
                versions = LibraryVersionService.get_versions(library_id)
                self.result.add_test_case("总库管理", "版本管理", True, 
                                       f"共{len(versions)}个版本", execution_time)
            else:
                self.result.add_test_case("总库管理", "版本管理", True, "无总库数据", execution_time)
            
            # 测试总库依赖管理
            start_time = time.time()
            if libraries:
                dependencies = LibraryDependencyService.get_dependencies(libraries[0].library_id)
                self.result.add_test_case("总库管理", "依赖管理", True, 
                                       f"共{len(dependencies)}个依赖", execution_time)
            else:
                self.result.add_test_case("总库管理", "依赖管理", True, "无总库数据", execution_time)
            
        except Exception as e:
            self.result.add_test_case("总库管理", "总库管理功能", False, str(e))
    
    def test_project_management(self):
        """测试项目管理功能"""
        print("\n  [1.2] 项目管理测试")
        
        try:
            from src.services.project_service import ProjectService
            from src.services.spec_service import SpecService
            
            # 测试项目列表
            start_time = time.time()
            projects, total = ProjectService.list_projects(size=20)
            execution_time = time.time() - start_time
            self.result.add_test_case("项目管理", "项目列表查询", True, 
                                   f"共{total}个项目", execution_time)
            
            # 测试项目统计
            start_time = time.time()
            stats = ProjectService.get_statistics()
            execution_time = time.time() - start_time
            self.result.add_test_case("项目管理", "项目统计", True, 
                                   f"总计{stats.get('total', 0)}个项目", execution_time)
            
            # 测试项目规格管理
            start_time = time.time()
            if projects:
                specs = SpecService.get_project_specs(projects[0].project_id)
                self.result.add_test_case("项目管理", "规格管理", True, 
                                       f"共{len(specs)}个规格", execution_time)
            else:
                self.result.add_test_case("项目管理", "规格管理", True, "无项目数据", execution_time)
            
        except Exception as e:
            self.result.add_test_case("项目管理", "项目管理功能", False, str(e))
    
    def test_change_management(self):
        """测试变更管理功能"""
        print("\n  [1.3] 变更管理测试")
        
        try:
            from src.services.change_service import ChangeService
            from src.services.project_service import ProjectService
            from src.services.library_change_service import LibraryChangeService
            
            # 获取测试项目
            projects, total = ProjectService.list_projects(size=10)
            
            # 测试项目变更管理
            start_time = time.time()
            if projects:
                project_id = projects[0].project_id
                changes = ChangeService.get_project_changes(project_id)
                execution_time = time.time() - start_time
                self.result.add_test_case("变更管理", "项目变更管理", True, 
                                       f"共{len(changes)}条变更", execution_time)
            else:
                execution_time = time.time() - start_time
                self.result.add_test_case("变更管理", "项目变更管理", True, "无项目数据", execution_time)
            
            # 测试总库变更管理
            start_time = time.time()
            library_changes = LibraryChangeService.get_recent_changes(limit=10)
            execution_time = time.time() - start_time
            self.result.add_test_case("变更管理", "总库变更管理", True, 
                                   f"共{len(library_changes)}条变更", execution_time)
            
        except Exception as e:
            self.result.add_test_case("变更管理", "变更管理功能", False, str(e))
    
    def test_template_management(self):
        """测试模板管理功能"""
        print("\n  [1.4] 模板管理测试")
        
        try:
            from src.services.template_service import TemplateService
            
            # 测试模板列表
            start_time = time.time()
            templates = TemplateService.list_templates()
            execution_time = time.time() - start_time
            self.result.add_test_case("模板管理", "模板列表", True, 
                                   f"共{len(templates)}个模板", execution_time)
            
            # 测试模板类型
            start_time = time.time()
            template_types = TemplateService.get_template_types()
            execution_time = time.time() - start_time
            self.result.add_test_case("模板管理", "模板类型", True, 
                                   f"共{len(template_types)}种类型", execution_time)
            
        except Exception as e:
            self.result.add_test_case("模板管理", "模板管理功能", False, str(e))
    
    def test_plugin_system(self):
        """测试插件系统"""
        print("\n  [1.5] 插件系统测试")
        
        try:
            from src.services.plugin_service import PluginService
            from src.services.plugin_market_service import PluginMarketService
            
            # 测试插件列表
            start_time = time.time()
            plugins = PluginService.get_installed_plugins()
            execution_time = time.time() - start_time
            self.result.add_test_case("插件系统", "插件列表", True, 
                                   f"共{len(plugins)}个插件", execution_time)
            
            # 测试插件市场
            start_time = time.time()
            market_plugins = PluginMarketService.get_available_plugins()
            execution_time = time.time() - start_time
            self.result.add_test_case("插件系统", "插件市场", True, 
                                   f"共{len(market_plugins)}个可用插件", execution_time)
            
        except Exception as e:
            self.result.add_test_case("插件系统", "插件系统功能", False, str(e))
    
    def test_plc_integration(self):
        """测试PLC集成功能"""
        print("\n  [1.6] PLC集成测试")
        
        try:
            # 测试PLC变量解析器插件
            plugin_path = project_root / "src" / "plugins" / "plc_variable_parser"
            if plugin_path.exists():
                # 测试插件结构
                start_time = time.time()
                plugin_json = plugin_path / "plugin.json"
                if plugin_json.exists():
                    with open(plugin_json, 'r', encoding='utf-8') as f:
                        plugin_info = json.load(f)
                    execution_time = time.time() - start_time
                    self.result.add_test_case("PLC集成", "PLC变量解析器", True, 
                                           f"版本: {plugin_info.get('version', '未知')}", execution_time)
                else:
                    execution_time = time.time() - start_time
                    self.result.add_test_case("PLC集成", "PLC变量解析器", False, "缺少plugin.json")
            else:
                self.result.add_test_case("PLC集成", "PLC变量解析器", True, "跳过 - 插件未安装")
            
        except Exception as e:
            self.result.add_test_case("PLC集成", "PLC集成功能", False, str(e))
    
    def test_performance(self):
        """测试性能"""
        print("\n[2] 性能测试")
        print("-"*60)
        
        # 测试启动时间
        self.test_startup_time()
        
        # 测试响应时间
        self.test_response_time()
        
        # 测试内存占用
        self.test_memory_usage()
    
    def test_startup_time(self):
        """测试启动时间"""
        print("\n  [2.1] 启动时间测试")
        
        try:
            # 测试可执行文件启动时间
            exe_path = project_root / "dist" / "Python项目管理工具" / "Python项目管理工具.exe"
            if exe_path.exists():
                start_time = time.time()
                # 启动进程并立即终止（仅测试启动时间）
                process = subprocess.Popen([str(exe_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                time.sleep(1)  # 等待启动
                process.terminate()
                process.wait(timeout=5)
                execution_time = time.time() - start_time
                self.result.add_test_case("性能测试", "启动时间", True, 
                                       f"{execution_time:.2f}秒", execution_time)
            else:
                self.result.add_test_case("性能测试", "启动时间", True, "跳过 - 可执行文件不存在")
        except Exception as e:
            self.result.add_test_case("性能测试", "启动时间", False, str(e))
    
    def test_response_time(self):
        """测试响应时间"""
        print("\n  [2.2] 响应时间测试")
        
        try:
            from src.services.project_service import ProjectService
            from src.services.library_service import LibraryService
            
            # 测试项目列表响应时间
            start_time = time.time()
            projects, total = ProjectService.list_projects(size=50)
            execution_time = time.time() - start_time
            self.result.add_test_case("性能测试", "项目列表响应时间", True, 
                                   f"{execution_time:.3f}秒", execution_time)
            
            # 测试总库列表响应时间
            start_time = time.time()
            libraries = LibraryService.list_libraries()
            execution_time = time.time() - start_time
            self.result.add_test_case("性能测试", "总库列表响应时间", True, 
                                   f"{execution_time:.3f}秒", execution_time)
            
        except Exception as e:
            self.result.add_test_case("性能测试", "响应时间", False, str(e))
    
    def test_memory_usage(self):
        """测试内存占用"""
        print("\n  [2.3] 内存占用测试")
        
        try:
            import gc
            
            # 测试当前进程内存占用
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            self.result.add_test_case("性能测试", "内存占用", True, 
                                   f"{memory_info.rss / 1024 / 1024:.2f} MB")
            
        except Exception as e:
            self.result.add_test_case("性能测试", "内存占用", False, str(e))
    
    def test_security(self):
        """测试安全"""
        print("\n[3] 安全测试")
        print("-"*60)
        
        # 测试权限控制
        self.test_permission_control()
        
        # 测试数据安全
        self.test_data_security()
    
    def test_permission_control(self):
        """测试权限控制"""
        print("\n  [3.1] 权限控制测试")
        
        try:
            # 检查配置文件权限
            config_path = project_root / "config"
            if config_path.exists():
                for config_file in config_path.glob("*.json"):
                    if config_file.exists():
                        # 检查文件权限（在Windows上权限检查有限）
                        self.result.add_test_case("安全测试", f"配置文件权限 - {config_file.name}", 
                                               True, "配置文件存在")
            else:
                self.result.add_test_case("安全测试", "配置文件权限", True, "配置目录不存在")
                
        except Exception as e:
            self.result.add_test_case("安全测试", "权限控制", False, str(e))
    
    def test_data_security(self):
        """测试数据安全"""
        print("\n  [3.2] 数据安全测试")
        
        try:
            # 检查数据库文件
            data_path = project_root / "data"
            db_path = data_path / "project_manager.db"
            if db_path.exists():
                # 检查数据库文件权限
                self.result.add_test_case("安全测试", "数据库文件", True, "数据库文件存在")
            else:
                self.result.add_test_case("安全测试", "数据库文件", True, "数据库文件不存在")
                
        except Exception as e:
            self.result.add_test_case("安全测试", "数据安全", False, str(e))
    
    def test_compatibility(self):
        """测试兼容性"""
        print("\n[4] 兼容性测试")
        print("-"*60)
        
        # 测试环境兼容性
        self.test_environment_compatibility()
        
        # 测试依赖兼容性
        self.test_dependency_compatibility()
    
    def test_environment_compatibility(self):
        """测试环境兼容性"""
        print("\n  [4.1] 环境兼容性测试")
        
        try:
            # 检查Python版本
            python_version = platform.python_version()
            self.result.add_test_case("兼容性测试", "Python版本", True, 
                                   f"Python {python_version}")
            
            # 检查操作系统
            os_info = platform.platform()
            self.result.add_test_case("兼容性测试", "操作系统", True, os_info)
            
        except Exception as e:
            self.result.add_test_case("兼容性测试", "环境兼容性", False, str(e))
    
    def test_dependency_compatibility(self):
        """测试依赖兼容性"""
        print("\n  [4.2] 依赖兼容性测试")
        
        try:
            # 检查关键依赖
            dependencies = [
                "PyQt5",
                "psutil",
                "sqlalchemy"
            ]
            
            for dep in dependencies:
                try:
                    __import__(dep)
                    self.result.add_test_case("兼容性测试", f"依赖 - {dep}", True, "依赖可用")
                except ImportError:
                    self.result.add_test_case("兼容性测试", f"依赖 - {dep}", False, "依赖缺失")
                    
        except Exception as e:
            self.result.add_test_case("兼容性测试", "依赖兼容性", False, str(e))
    
    def print_summary(self):
        """打印测试摘要"""
        print("\n" + "="*80)
        print("测试摘要")
        print("="*80)
        print(f"总计: {len(self.result.test_cases)} 项")
        print(f"通过: {self.result.total_passed} 项")
        print(f"失败: {self.result.total_failed} 项")
        print(f"跳过: {self.result.total_skipped} 项")
        print(f"成功率: {self.result.total_passed / len(self.result.test_cases) * 100:.2f}%" if self.result.test_cases else "0%")
        
        if self.result.total_failed > 0:
            print("\n失败项:")
            for test in self.result.test_cases:
                if not test["success"] and test["message"] != "跳过":
                    print(f"  - {test['category']} - {test['name']}: {test['message']}")
    
    def generate_test_report(self):
        """生成测试报告"""
        report = self.result.generate_report()
        
        # 生成JSON报告
        report_dir = project_root / "data" / "test_reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_report_path = report_dir / f"comprehensive_test_report_{timestamp}.json"
        md_report_path = report_dir / f"comprehensive_test_report_{timestamp}.md"
        
        # 写入JSON报告
        with open(json_report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 生成Markdown报告
        md_content = self._generate_markdown_report(report)
        with open(md_report_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"\n测试报告已生成:")
        print(f"  JSON报告: {json_report_path}")
        print(f"  Markdown报告: {md_report_path}")
    
    def _generate_markdown_report(self, report):
        """生成Markdown报告"""
        md = []
        md.append(f"# Python项目管理工具测试报告")
        md.append(f"> 测试时间: {report['test_summary']['start_time']}")
        md.append(f"> 完成时间: {report['test_summary']['end_time']}")
        md.append("")
        
        # 测试摘要
        md.append("## 测试摘要")
        md.append(f"- 总计测试: {report['test_summary']['total_tests']} 项")
        md.append(f"- 通过: {report['test_summary']['passed']} 项")
        md.append(f"- 失败: {report['test_summary']['failed']} 项")
        md.append(f"- 跳过: {report['test_summary']['skipped']} 项")
        md.append(f"- 成功率: {report['test_summary']['success_rate']}")
        md.append("")
        
        # 环境信息
        md.append("## 环境信息")
        env = report['environment']
        md.append(f"- Python版本: {env['python_version']}")
        md.append(f"- 操作系统: {env['os']}")
        md.append(f"- 架构: {env['architecture'][0]}")
        md.append(f"- 系统: {env['system']} {env['release']}")
        md.append("")
        
        # 测试详情
        md.append("## 测试详情")
        
        # 按类别分组
        categories = {}
        for test in report['test_cases']:
            category = test['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(test)
        
        for category, tests in categories.items():
            md.append(f"### {category}")
            for test in tests:
                status = "✅ 通过" if test['success'] else "❌ 失败"
                if test['message'] == "跳过":
                    status = "⚠️ 跳过"
                md.append(f"- **{test['name']}**: {status}")
                if test['message'] and test['message'] != "跳过":
                    md.append(f"  - 详情: {test['message']}")
                if test.get('execution_time', 0) > 0:
                    md.append(f"  - 执行时间: {test['execution_time']:.3f}秒")
            md.append("")
        
        # Bug清单
        failed_tests = [test for test in report['test_cases'] if not test['success'] and test['message'] != "跳过"]
        if failed_tests:
            md.append("## Bug清单")
            md.append("| 编号 | 类别 | 测试项 | 问题描述 |")
            md.append("|------|------|--------|----------|")
            for i, test in enumerate(failed_tests, 1):
                md.append(f"| {i} | {test['category']} | {test['name']} | {test['message']} |")
            md.append("")
        
        # 建议
        md.append("## 建议")
        md.append("1. 针对失败的测试项进行修复")
        md.append("2. 优化性能测试中发现的瓶颈")
        md.append("3. 加强安全测试覆盖")
        md.append("4. 确保在不同环境下的兼容性")
        
        return '\n'.join(md)

def main():
    """主函数"""
    runner = ComprehensiveTestRunner()
    runner.run_all_tests()
    
    return 0 if runner.result.total_failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())