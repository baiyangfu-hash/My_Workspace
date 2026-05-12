# -*- coding: utf-8 -*-
"""
全量自动化测试执行脚本
实现完整的自动化测试流程，无需人工干预

使用方法:
    py run_full_test_suite.py
    py run_full_test_suite.py --mode=ci
    py run_full_test_suite.py --mode=quick
    py run_full_test_suite.py --notify=email
"""
import sys
import os
import time
import json
import argparse
import datetime
import subprocess
import traceback
from pathlib import Path
from collections import defaultdict

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class TestSuiteRunner:
    """测试套件执行器"""
    
    def __init__(self, mode='full', notify=False):
        self.mode = mode  # full, ci, quick
        self.notify = notify
        self.start_time = None
        self.end_time = None
        self.test_results = []
        self.test_categories = {
            'core': {'name': '核心模块测试', 'priority': 'P0', 'enabled': True},
            'service': {'name': '服务模块测试', 'priority': 'P0', 'enabled': True},
            'functional': {'name': '功能流程测试', 'priority': 'P0', 'enabled': True},
            'performance': {'name': '性能测试', 'priority': 'P1', 'enabled': mode == 'full'},
        }
        self.category_results = defaultdict(list)
        self.report_dir = os.path.join('data', 'test_reports')
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保必要目录存在"""
        os.makedirs(self.report_dir, exist_ok=True)
        os.makedirs(os.path.join(self.report_dir, 'realtime'), exist_ok=True)
        os.makedirs(os.path.join(self.report_dir, 'detailed'), exist_ok=True)
        os.makedirs(os.path.join(self.report_dir, 'trends'), exist_ok=True)
    
    def start(self):
        """开始测试套件执行"""
        self.start_time = time.time()
        print("=" * 80)
        print("=" * 80)
        print("    Python项目管理工具 - 全量自动化测试套件")
        print("=" * 80)
        print(f"开始时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"执行模式: {self.mode.upper()}")
        print(f"通知方式: {'启用' if self.notify else '禁用'}")
        print("=" * 80)
        print()
        
        # 记录测试开始日志
        self._log_event('INFO', '测试套件开始执行', {'mode': self.mode})
    
    def end(self):
        """结束测试套件执行"""
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        
        print()
        print("=" * 80)
        print("=" * 80)
        print("    测试执行完成")
        print("=" * 80)
        print(f"结束时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"执行时间: {duration:.2f} 秒 ({duration/60:.2f} 分钟)")
        print("=" * 80)
        
        # 生成报告
        self._generate_reports()
        
        # 发送通知
        if self.notify:
            self._send_notifications()
        
        # 记录测试结束日志
        self._log_event('INFO', '测试套件执行完成', {
            'duration': duration,
            'total_tests': len(self.test_results),
            'passed': sum(1 for r in self.test_results if r['status'] == 'PASS'),
            'failed': sum(1 for r in self.test_results if r['status'] == 'FAIL')
        })
    
    def run_all_tests(self):
        """运行所有测试"""
        self.start_time = time.time()
        print("【阶段1】执行核心模块测试...")
        self._run_core_tests()
        
        print("\n【阶段2】执行服务模块测试...")
        self._run_service_tests()
        
        print("\n【阶段3】执行功能流程测试...")
        self._run_functional_tests()
        
        if self.mode == 'full':
            print("\n【阶段4】执行性能测试...")
            self._run_performance_tests()
        
        self.end_time = time.time()
        print("\n【阶段5】生成测试报告...")
        self._generate_reports()
    
    def _run_core_tests(self):
        """运行核心模块测试"""
        tests = [
            ('CORE-001', '配置加载测试', self._test_config_loading),
            ('CORE-002', '数据库连接测试', self._test_database_connection),
            ('CORE-003', '常量定义测试', self._test_constants),
            ('CORE-004', '版本信息测试', self._test_version),
        ]
        
        for test_id, test_name, test_func in tests:
            self._run_single_test('core', test_id, test_name, test_func)
    
    def _run_service_tests(self):
        """运行服务模块测试"""
        tests = [
            ('SRV-001', '项目管理服务测试', self._test_project_service),
            ('SRV-002', '变更管理服务测试', self._test_change_service),
            ('SRV-003', '统计服务测试', self._test_statistics_service),
            ('SRV-004', '库服务测试', self._test_library_service),
            ('SRV-005', '插件服务测试', self._test_plugin_service),
            ('SRV-006', '模板服务测试', self._test_template_service),
        ]
        
        for test_id, test_name, test_func in tests:
            self._run_single_test('service', test_id, test_name, test_func)
    
    def _run_functional_tests(self):
        """运行功能流程测试"""
        tests = [
            ('FLOW-001', '完整项目创建流程', self._test_project_creation_flow),
            ('FLOW-002', '变更单审批流程', self._test_change_approval_flow),
            ('FLOW-003', '文档生成流程', self._test_document_generation_flow),
            ('FLOW-004', '统计分析流程', self._test_statistics_flow),
            ('FLOW-005', '插件安装流程', self._test_plugin_install_flow),
        ]
        
        for test_id, test_name, test_func in tests:
            self._run_single_test('functional', test_id, test_name, test_func)
    
    def _run_performance_tests(self):
        """运行性能测试"""
        tests = [
            ('PERF-001', '数据库查询性能', self._test_db_query_performance),
            ('PERF-002', '文档生成性能', self._test_doc_generation_performance),
            ('PERF-003', '并发处理性能', self._test_concurrency_performance),
            ('PERF-004', '内存使用测试', self._test_memory_usage),
        ]
        
        for test_id, test_name, test_func in tests:
            self._run_single_test('performance', test_id, test_name, test_func)
    
    def _run_single_test(self, category, test_id, test_name, test_func):
        """运行单个测试"""
        print(f"  执行测试 {test_id}: {test_name}...", end=' ')
        
        test_start = time.time()
        try:
            result = test_func()
            test_end = time.time()
            duration = test_end - test_start
            
            if result:
                print(f"✅ 通过 ({duration:.2f}s)")
                status = 'PASS'
                message = '测试通过'
            else:
                print(f"❌ 失败 ({duration:.2f}s)")
                status = 'FAIL'
                message = '测试失败'
        except Exception as e:
            test_end = time.time()
            duration = test_end - test_start
            print(f"❌ 异常 ({duration:.2f}s): {str(e)[:50]}")
            status = 'FAIL'
            message = str(e)
            traceback.print_exc()
        
        test_result = {
            'category': category,
            'test_id': test_id,
            'test_name': test_name,
            'status': status,
            'message': message,
            'duration': duration,
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.test_results.append(test_result)
        self.category_results[category].append(test_result)
        
        # 实时保存结果
        self._save_realtime_result(test_result)
    
    # ==================== 核心模块测试实现 ====================
    
    def _test_config_loading(self):
        """测试配置加载"""
        try:
            from src.core.config import Config
            Config.load_config()
            return Config.get('app_name') is not None
        except Exception as e:
            print(f"\n    错误: {e}")
            return False
    
    def _test_database_connection(self):
        """测试数据库连接"""
        try:
            from src.dao.database import Database
            db = Database()
            engine = db.get_engine()
            return engine is not None
        except Exception as e:
            print(f"\n    错误: {e}")
            return False
    
    def _test_constants(self):
        """测试常量定义"""
        try:
            from src.core.constants import ChangeStatus
            return hasattr(ChangeStatus, 'DRAFT')
        except Exception as e:
            print(f"\n    错误: {e}")
            return False
    
    def _test_version(self):
        """测试版本信息"""
        try:
            from src.core.version import __version__
            return __version__ is not None and len(__version__) > 0
        except Exception as e:
            print(f"\n    错误: {e}")
            return False
    
    # ==================== 服务模块测试实现 ====================
    
    def _test_project_service(self):
        """测试项目管理服务"""
        try:
            from src.services.project_service import ProjectService
            projects, total = ProjectService.list_projects(size=10)
            return True
        except Exception as e:
            print(f"\n    错误: {e}")
            return False
    
    def _test_change_service(self):
        """测试变更管理服务"""
        try:
            from src.services.change_service import ChangeService
            changes = ChangeService.get_changes()
            return True
        except Exception as e:
            print(f"\n    错误: {e}")
            return False
    
    def _test_statistics_service(self):
        """测试统计服务"""
        try:
            from src.services.statistics_service import StatisticsService
            overview = StatisticsService.get_overview()
            return True
        except Exception as e:
            print(f"\n    错误: {e}")
            return False
    
    def _test_library_service(self):
        """测试库服务"""
        try:
            from src.services.library_service import LibraryService
            libraries = LibraryService.list_libraries()
            return True
        except Exception as e:
            print(f"\n    错误: {e}")
            return False
    
    def _test_plugin_service(self):
        """测试插件服务"""
        try:
            from src.services.plugin_service import PluginService
            plugins = PluginService.get_plugins()
            return True
        except Exception as e:
            print(f"\n    错误: {e}")
            return False
    
    def _test_template_service(self):
        """测试模板服务"""
        try:
            from src.services.template_service import TemplateService
            templates = TemplateService.list_templates()
            return True
        except Exception as e:
            print(f"\n    错误: {e}")
            return False
    
    # ==================== 功能流程测试实现 ====================
    
    def _test_project_creation_flow(self):
        """测试项目创建流程"""
        try:
            from src.services.project_service import ProjectService
            from src.services.template_service import TemplateService
            
            # 初始化内置模板
            TemplateService.initialize_builtin_templates()
            
            # 获取默认模板
            templates = TemplateService.list_templates()
            if not templates:
                # 如果没有模板，创建一个默认模板
                default_template = {
                    "name": "默认模板",
                    "version": "1.0.0",
                    "structure": [
                        {"path": "01_项目文档", "required": true},
                        {"path": "02_代码", "required": true},
                        {"path": "03_测试", "required": true}
                    ],
                    "templates": []
                }
                template, error = TemplateService.create_template(default_template)
                template_id = template.template_id if template else 'TEMPLATE-DEFAULT'
            else:
                template_id = templates[0].template_id
            
            # 创建测试项目
            project, error = ProjectService.create_project(
                business_line='DJ',
                name='测试项目',
                template_id=template_id,
                manager='自动化测试',
                description='自动化测试项目'
            )
            if not project:
                print(f"\n    错误: 项目创建失败 - {error}")
            return project is not None
        except Exception as e:
            print(f"\n    错误: {e}")
            return False
    
    def _test_change_approval_flow(self):
        """测试变更审批流程"""
        try:
            from src.services.change_service import ChangeService
            
            # 创建变更单
            change_data = {
                'project_id': 'TEST-2026-001',
                'title': '测试变更审批流程',
                'type': '测试',
                'description': '测试变更审批流程',
                'reason': '功能验证',
                'impact': '测试影响',
                'proposer': '自动化测试'
            }
            change, error = ChangeService.create_change(**change_data)
            if not change:
                return False
            
            # 提交审批
            success, error = ChangeService.submit_change(change.change_id)
            if not success:
                return False
            
            # 审批通过
            success, error = ChangeService.approve_change(change.change_id, '自动化审批人')
            return success
        except Exception as e:
            print(f"\n    错误: {e}")
            return False
    
    def _test_document_generation_flow(self):
        """测试文档生成流程"""
        try:
            from src.services.change_service import ChangeService
            from src.services.project_service import ProjectService
            from src.services.template_service import TemplateService
            
            # 初始化内置模板
            TemplateService.initialize_builtin_templates()
            
            # 获取默认模板
            templates = TemplateService.list_templates()
            template_id = templates[0].template_id if templates else 'TEMPLATE-DEFAULT'
            
            # 创建测试项目
            project, error = ProjectService.create_project(
                business_line='DJ',
                name='测试项目',
                template_id=template_id,
                manager='自动化测试',
                description='自动化测试项目'
            )
            if not project:
                print(f"\n    错误: 项目创建失败 - {error}")
                return False
            
            # 创建变更单
            change_data = {
                'project_id': project.project_id,
                'title': '测试文档生成',
                'type': '测试',
                'description': '测试文档生成功能',
                'reason': '功能验证',
                'impact': '测试影响',
                'proposer': '自动化测试'
            }
            change, error = ChangeService.create_change(**change_data)
            if not change:
                return False
            
            # 生成文档
            result, error = ChangeService.export_change(change.change_id)
            if not result:
                print(f"\n    错误: 文档生成失败 - {error}")
            return result is not None
        except Exception as e:
            print(f"\n    错误: {e}")
            return False
    
    def _test_statistics_flow(self):
        """测试统计分析流程"""
        try:
            from src.services.statistics_service import StatisticsService
            
            # 获取系统概览
            overview = StatisticsService.get_overview()
            
            # 获取变更统计
            change_stats = StatisticsService.get_change_statistics()
            
            # 生成报告
            report = StatisticsService.export_statistics_report('markdown')
            
            return overview is not None and change_stats is not None and report is not None
        except Exception as e:
            print(f"\n    错误: {e}")
            return False
    
    def _test_plugin_install_flow(self):
        """测试插件安装流程"""
        try:
            from src.services.plugin_service import PluginService
            
            # 获取插件列表
            plugins = PluginService.get_plugins()
            
            # 获取已安装插件
            installed_plugins = PluginService.get_installed_plugins()
            
            return plugins is not None and installed_plugins is not None
        except Exception as e:
            print(f"\n    错误: {e}")
            return False
    
    # ==================== 性能测试实现 ====================
    
    def _test_db_query_performance(self):
        """测试数据库查询性能"""
        try:
            from src.services.project_service import ProjectService
            
            start = time.time()
            projects, total = ProjectService.list_projects(size=100)
            duration = time.time() - start
            
            # 查询时间应小于2秒
            return duration < 2.0
        except Exception as e:
            print(f"\n    错误: {e}")
            return False
    
    def _test_doc_generation_performance(self):
        """测试文档生成性能"""
        try:
            from src.services.change_service import ChangeService
            
            # 创建变更单
            change_data = {
                'project_id': 'TEST-2026-001',
                'title': '性能测试文档生成',
                'type': '测试',
                'description': '测试文档生成性能',
                'reason': '性能验证',
                'impact': '性能测试',
                'proposer': '自动化测试'
            }
            change, error = ChangeService.create_change(**change_data)
            if not change:
                return False
            
            start = time.time()
            result, error = ChangeService.export_change(change.change_id)
            duration = time.time() - start
            
            # 文档生成时间应小于5秒
            return duration < 5.0
        except Exception as e:
            print(f"\n    错误: {e}")
            return False
    
    def _test_concurrency_performance(self):
        """测试并发处理性能"""
        try:
            import threading
            from src.services.project_service import ProjectService
            
            results = []
            
            def query_projects():
                try:
                    projects, total = ProjectService.list_projects(size=10)
                    results.append(True)
                except:
                    results.append(False)
            
            # 启动10个并发线程
            threads = []
            for i in range(10):
                t = threading.Thread(target=query_projects)
                threads.append(t)
                t.start()
            
            # 等待所有线程完成
            for t in threads:
                t.join()
            
            # 所有查询都应成功
            return all(results)
        except Exception as e:
            print(f"\n    错误: {e}")
            return False
    
    def _test_memory_usage(self):
        """测试内存使用"""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # 执行一些操作
            from src.services.project_service import ProjectService
            for i in range(10):
                projects, total = ProjectService.list_projects(size=100)
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # 内存增长应小于100MB
            return memory_increase < 100
        except Exception as e:
            print(f"\n    错误: {e}")
            return False
    
    # ==================== 报告生成 ====================
    
    def _generate_reports(self):
        """生成测试报告"""
        print("\n  生成详细测试报告...")
        self._generate_detailed_report()
        
        print("  生成汇总测试报告...")
        self._generate_summary_report()
        
        print("  生成趋势分析报告...")
        self._generate_trend_report()
    
    def _generate_detailed_report(self):
        """生成详细测试报告"""
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = os.path.join(self.report_dir, 'detailed', f'详细测试报告_{timestamp}.md')
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# Python项目管理工具 - 详细测试报告\n\n")
            f.write(f"**报告生成时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**执行模式**: {self.mode.upper()}\n")
            f.write(f"**执行时间**: {self.end_time - self.start_time:.2f} 秒\n\n")
            
            # 总体结果
            total_tests = len(self.test_results)
            passed_tests = sum(1 for r in self.test_results if r['status'] == 'PASS')
            failed_tests = total_tests - passed_tests
            pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
            
            f.write(f"## 总体结果\n")
            f.write(f"- 总测试数: {total_tests}\n")
            f.write(f"- 通过: {passed_tests} ({pass_rate:.1f}%)\n")
            f.write(f"- 失败: {failed_tests}\n\n")
            
            # 分类结果
            for category, results in self.category_results.items():
                category_name = self.test_categories.get(category, {}).get('name', category)
                f.write(f"## {category_name}\n\n")
                
                for result in results:
                    status_icon = "✅" if result['status'] == 'PASS' else "❌"
                    f.write(f"### {result['test_id']}: {result['test_name']}\n")
                    f.write(f"- 状态: {status_icon} {result['status']}\n")
                    f.write(f"- 耗时: {result['duration']:.2f} 秒\n")
                    f.write(f"- 时间: {result['timestamp']}\n")
                    if result['message'] and result['message'] != '测试通过':
                        f.write(f"- 消息: {result['message']}\n")
                    f.write("\n")
        
        print(f"    详细报告已生成: {report_file}")
    
    def _generate_summary_report(self):
        """生成汇总测试报告"""
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = os.path.join(self.report_dir, f'测试报告_{timestamp}.md')
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# Python项目管理工具 - 测试报告\n\n")
            f.write(f"**测试时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**执行时间**: {self.end_time - self.start_time:.2f} 秒\n\n")
            
            # 总体结果
            total_tests = len(self.test_results)
            passed_tests = sum(1 for r in self.test_results if r['status'] == 'PASS')
            failed_tests = total_tests - passed_tests
            pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
            
            f.write(f"## 测试结果\n")
            f.write(f"- 总测试数: {total_tests}\n")
            f.write(f"- 通过: {passed_tests}\n")
            f.write(f"- 失败: {failed_tests}\n")
            f.write(f"- 通过率: {pass_rate:.1f}%\n\n")
            
            # 分类汇总
            f.write(f"## 分类结果\n\n")
            for category, results in self.category_results.items():
                category_name = self.test_categories.get(category, {}).get('name', category)
                passed = sum(1 for r in results if r['status'] == 'PASS')
                total = len(results)
                rate = (passed / total * 100) if total > 0 else 0
                
                f.write(f"### {category_name}\n")
                f.write(f"- 测试数: {total}\n")
                f.write(f"- 通过: {passed}\n")
                f.write(f"- 失败: {total - passed}\n")
                f.write(f"- 通过率: {rate:.1f}%\n\n")
        
        print(f"    汇总报告已生成: {report_file}")
    
    def _generate_trend_report(self):
        """生成趋势分析报告"""
        # 读取历史数据
        trend_data = self._load_trend_data()
        
        # 添加当前数据
        current_data = {
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total': len(self.test_results),
            'passed': sum(1 for r in self.test_results if r['status'] == 'PASS'),
            'failed': sum(1 for r in self.test_results if r['status'] == 'FAIL'),
            'duration': self.end_time - self.start_time
        }
        trend_data.append(current_data)
        
        # 保存趋势数据
        self._save_trend_data(trend_data)
        
        # 生成趋势报告
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = os.path.join(self.report_dir, 'trends', f'趋势报告_{timestamp}.md')
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# Python项目管理工具 - 测试趋势报告\n\n")
            f.write(f"**报告生成时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write(f"## 历史趋势\n\n")
            f.write(f"| 时间 | 总测试数 | 通过 | 失败 | 通过率 | 执行时间(秒) |\n")
            f.write(f"|------|---------|------|------|--------|-------------|\n")
            
            for data in trend_data[-10:]:  # 显示最近10次
                pass_rate = (data['passed'] / data['total'] * 100) if data['total'] > 0 else 0
                f.write(f"| {data['timestamp']} | {data['total']} | {data['passed']} | {data['failed']} | {pass_rate:.1f}% | {data['duration']:.2f} |\n")
        
        print(f"    趋势报告已生成: {report_file}")
    
    def _save_realtime_result(self, result):
        """保存实时结果"""
        realtime_file = os.path.join(self.report_dir, 'realtime', 'current_test.json')
        
        data = {
            'last_update': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'current_test': result,
            'progress': {
                'total': len(self.test_results),
                'completed': len(self.test_results),
                'passed': sum(1 for r in self.test_results if r['status'] == 'PASS'),
                'failed': sum(1 for r in self.test_results if r['status'] == 'FAIL')
            }
        }
        
        with open(realtime_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _load_trend_data(self):
        """加载趋势数据"""
        trend_file = os.path.join(self.report_dir, 'trends', 'trend_data.json')
        
        if os.path.exists(trend_file):
            with open(trend_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_trend_data(self, data):
        """保存趋势数据"""
        trend_file = os.path.join(self.report_dir, 'trends', 'trend_data.json')
        
        # 只保留最近30条记录
        if len(data) > 30:
            data = data[-30:]
        
        with open(trend_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _send_notifications(self):
        """发送测试通知"""
        print("\n  发送测试通知...")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed_tests = total_tests - passed_tests
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # 生成通知内容
        if failed_tests == 0:
            title = "✅ [测试通过] Python项目管理工具 - 所有测试通过"
            content = f"""
测试完成！所有测试用例通过。

测试摘要:
- 总测试数: {total_tests}
- 通过: {passed_tests} ({pass_rate:.1f}%)
- 执行时间: {self.end_time - self.start_time:.2f} 秒

查看详细报告: data/test_reports/
            """
        else:
            title = f"⚠️ [测试失败] Python项目管理工具 - {failed_tests}个测试失败"
            content = f"""
测试完成，发现{failed_tests}个测试失败，需要关注。

测试摘要:
- 总测试数: {total_tests}
- 通过: {passed_tests} ({pass_rate:.1f}%)
- 失败: {failed_tests}
- 执行时间: {self.end_time - self.start_time:.2f} 秒

查看详细报告: data/test_reports/
            """
        
        # 保存通知到文件
        notification_file = os.path.join(self.report_dir, 'notification.txt')
        with open(notification_file, 'w', encoding='utf-8') as f:
            f.write(f"标题: {title}\n")
            f.write(f"内容:\n{content}\n")
        
        print(f"    通知已保存: {notification_file}")
        print(f"    标题: {title}")
    
    def _log_event(self, level, message, data=None):
        """记录事件日志"""
        log_file = os.path.join(self.report_dir, 'test_execution.log')
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        log_entry = f"[{timestamp}] [{level}] {message}"
        if data:
            log_entry += f" - {json.dumps(data, ensure_ascii=False)}"
        log_entry += "\n"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Python项目管理工具 - 全量自动化测试套件')
    parser.add_argument('--mode', choices=['full', 'ci', 'quick'], default='full',
                       help='测试模式: full=全量测试, ci=CI模式, quick=快速测试')
    parser.add_argument('--notify', action='store_true',
                       help='启用测试通知')
    
    args = parser.parse_args()
    
    # 创建测试运行器
    runner = TestSuiteRunner(mode=args.mode, notify=args.notify)
    
    # 开始测试
    runner.start()
    
    # 运行所有测试
    runner.run_all_tests()
    
    # 结束测试
    runner.end()
    
    # 返回退出码
    total_tests = len(runner.test_results)
    passed_tests = sum(1 for r in runner.test_results if r['status'] == 'PASS')
    
    if passed_tests == total_tests:
        return 0  # 全部通过
    else:
        return 1  # 有失败


if __name__ == '__main__':
    sys.exit(main())
