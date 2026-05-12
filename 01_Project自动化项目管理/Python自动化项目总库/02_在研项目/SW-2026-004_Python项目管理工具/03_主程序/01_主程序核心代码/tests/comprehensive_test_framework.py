# -*- coding: utf-8 -*-
"""
综合自动化测试框架
用于自动测试项目的所有主要功能模块
"""
import sys
import os
import time
import json
import datetime
from collections import defaultdict

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestFramework:
    def __init__(self):
        self.test_results = []
        self.test_start_time = None
        self.test_end_time = None
        self.test_categories = {
            'core': '核心功能',
            'project': '项目管理',
            'change': '变更管理',
            'library': '库管理',
            'plugin': '插件系统',
            'api': 'API服务',
            'ui': '用户界面'
        }
        self.category_results = defaultdict(list)
    
    def start_test(self):
        """开始测试"""
        print("=" * 80)
        print("=== Python项目管理工具 - 综合自动化测试框架 ===")
        print(f"测试开始时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        self.test_start_time = time.time()
    
    def end_test(self):
        """结束测试"""
        self.test_end_time = time.time()
        test_duration = self.test_end_time - self.test_start_time
        
        print("\n" + "=" * 80)
        print("=== 测试结果汇总 ===")
        print(f"测试结束时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"测试持续时间: {test_duration:.2f} 秒")
        print("=" * 80)
        
        # 按类别输出测试结果
        total_passed = 0
        total_tests = 0
        
        for category, tests in self.category_results.items():
            passed = sum(1 for test in tests if test['status'] == 'PASS')
            total = len(tests)
            pass_rate = (passed / total * 100) if total > 0 else 0
            
            total_passed += passed
            total_tests += total
            
            print(f"\n{self.test_categories.get(category, category)}:")
            print(f"  测试用例: {total}")
            print(f"  通过: {passed}")
            print(f"  失败: {total - passed}")
            print(f"  通过率: {pass_rate:.1f}%")
            
            # 输出失败的测试用例
            failed_tests = [test for test in tests if test['status'] == 'FAIL']
            for test in failed_tests:
                print(f"  ❌ {test['name']}: {test['message']}")
        
        # 总体结果
        overall_pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        print("\n" + "=" * 80)
        print("=== 总体测试结果 ===")
        print(f"总测试用例: {total_tests}")
        print(f"总通过: {total_passed}")
        print(f"总失败: {total_tests - total_passed}")
        print(f"总体通过率: {overall_pass_rate:.1f}%")
        
        if total_passed == total_tests:
            print("\n🎉 所有测试通过！系统功能正常")
        else:
            print("\n⚠️ 部分测试失败，需要检查和修复")
        
        # 生成测试报告
        self.generate_test_report()
    
    def run_test(self, category, name, test_func):
        """运行单个测试"""
        print(f"\n{self.test_categories.get(category, category)} - {name}...")
        
        test_start = time.time()
        try:
            result = test_func()
            test_end = time.time()
            duration = test_end - test_start
            
            if result:
                print(f"✅ {name} - 通过 (耗时: {duration:.2f}s)")
                status = 'PASS'
                message = '测试通过'
            else:
                print(f"❌ {name} - 失败 (耗时: {duration:.2f}s)")
                status = 'FAIL'
                message = '测试失败'
        except Exception as e:
            test_end = time.time()
            duration = test_end - test_start
            print(f"❌ {name} - 异常: {str(e)} (耗时: {duration:.2f}s)")
            status = 'FAIL'
            message = str(e)
        
        test_result = {
            'category': category,
            'name': name,
            'status': status,
            'message': message,
            'duration': duration,
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.test_results.append(test_result)
        self.category_results[category].append(test_result)
        
        return status == 'PASS'
    
    def generate_test_report(self):
        """生成测试报告"""
        report_dir = os.path.join('..', 'data', 'test_reports')
        os.makedirs(report_dir, exist_ok=True)
        
        report_filename = f"综合测试报告_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path = os.path.join(report_dir, report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# Python项目管理工具 - 综合测试报告\n\n")
            f.write(f"**测试时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**测试持续时间**: {self.test_end_time - self.test_start_time:.2f} 秒\n\n")
            
            total_passed = sum(1 for test in self.test_results if test['status'] == 'PASS')
            total_tests = len(self.test_results)
            overall_pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
            
            f.write(f"## 总体测试结果\n")
            f.write(f"- 总测试用例: {total_tests}\n")
            f.write(f"- 总通过: {total_passed}\n")
            f.write(f"- 总失败: {total_tests - total_passed}\n")
            f.write(f"- 总体通过率: {overall_pass_rate:.1f}%\n\n")
            
            for category, tests in self.category_results.items():
                passed = sum(1 for test in tests if test['status'] == 'PASS')
                total = len(tests)
                pass_rate = (passed / total * 100) if total > 0 else 0
                
                f.write(f"## {self.test_categories.get(category, category)}\n")
                f.write(f"- 测试用例: {total}\n")
                f.write(f"- 通过: {passed}\n")
                f.write(f"- 失败: {total - passed}\n")
                f.write(f"- 通过率: {pass_rate:.1f}%\n\n")
                
                # 输出失败的测试用例
                failed_tests = [test for test in tests if test['status'] == 'FAIL']
                if failed_tests:
                    f.write("### 失败的测试用例\n")
                    for test in failed_tests:
                        f.write(f"- **{test['name']}**: {test['message']}\n")
                    f.write("\n")
        
        print(f"\n测试报告已生成: {report_path}")

def test_core_modules():
    """测试核心模块"""
    try:
        from src.core.config import Config
        from src.core.constants import ChangeStatus
        from src.core.version import __version__
        
        # 测试配置加载
        config = Config()
        if config.get('app_name'):
            return True
        return False
    except Exception as e:
        print(f"核心模块测试异常: {e}")
        return False

def test_database_connection():
    """测试数据库连接"""
    try:
        from src.dao.database import Database
        
        db = Database()
        if db.get_connection():
            return True
        return False
    except Exception as e:
        print(f"数据库连接测试异常: {e}")
        return False

def test_project_management():
    """测试项目管理功能"""
    try:
        from src.services.project_service import ProjectService
        
        # 测试项目列表获取
        projects = ProjectService.get_projects()
        if projects is not None:
            return True
        return False
    except Exception as e:
        print(f"项目管理测试异常: {e}")
        return False

def test_change_management():
    """测试变更管理功能"""
    try:
        from src.services.change_service import ChangeService
        
        # 测试变更列表获取
        changes = ChangeService.get_changes()
        if changes is not None:
            return True
        return False
    except Exception as e:
        print(f"变更管理测试异常: {e}")
        return False

def test_library_management():
    """测试库管理功能"""
    try:
        from src.services.library_service import LibraryService
        
        # 测试库列表获取
        libraries = LibraryService.get_libraries()
        if libraries is not None:
            return True
        return False
    except Exception as e:
        print(f"库管理测试异常: {e}")
        return False

def test_plugin_system():
    """测试插件系统"""
    try:
        from src.services.plugin_service import PluginService
        
        # 测试插件列表获取
        plugins = PluginService.get_plugins()
        if plugins is not None:
            return True
        return False
    except Exception as e:
        print(f"插件系统测试异常: {e}")
        return False

def test_api_service():
    """测试API服务"""
    try:
        from src.api.app import create_app
        
        # 测试API应用创建
        app = create_app()
        if app:
            return True
        return False
    except Exception as e:
        print(f"API服务测试异常: {e}")
        return False

def test_change_document_generation():
    """测试变更文档生成"""
    try:
        from src.services.change_service import ChangeService
        
        # 测试文档生成功能
        # 这里创建一个测试变更单并生成文档
        change_data = {
            "project_id": "TEST-2026-001",
            "title": "测试变更文档生成",
            "type": "测试",
            "description": "测试变更文档生成功能",
            "reason": "功能验证",
            "impact": "测试影响",
            "proposer": "自动化测试"
        }
        
        change, error = ChangeService.create_change(**change_data)
        if change:
            # 测试文档导出
            result, error = ChangeService.export_change(change.change_id)
            if result:
                return True
        return False
    except Exception as e:
        print(f"变更文档生成测试异常: {e}")
        return False

def test_change_approval_process():
    """测试变更审批流程"""
    try:
        from src.services.change_service import ChangeService
        
        # 创建测试变更单
        change_data = {
            "project_id": "TEST-2026-002",
            "title": "测试变更审批流程",
            "type": "测试",
            "description": "测试变更审批流程",
            "reason": "功能验证",
            "impact": "测试影响",
            "proposer": "自动化测试"
        }
        
        change, error = ChangeService.create_change(**change_data)
        if change:
            # 测试提交审批
            success, error = ChangeService.submit_change(change.change_id)
            if success:
                # 测试审批通过
                success, error = ChangeService.approve_change(change.change_id, "自动化审批人")
                if success:
                    return True
        return False
    except Exception as e:
        print(f"变更审批流程测试异常: {e}")
        return False

def test_change_impact_analysis():
    """测试变更影响分析"""
    try:
        from src.services.change_service import ChangeService
        from src.services.impact_service import ImpactService
        
        # 创建测试变更单
        change_data = {
            "project_id": "TEST-2026-003",
            "title": "测试变更影响分析",
            "type": "测试",
            "description": "测试变更影响分析",
            "reason": "功能验证",
            "impact": "测试影响",
            "proposer": "自动化测试"
        }
        
        change, error = ChangeService.create_change(**change_data)
        if change:
            # 测试影响分析
            result = ImpactService.analyze_impact(change.change_id)
            if "risk_level" in result:
                return True
        return False
    except Exception as e:
        print(f"变更影响分析测试异常: {e}")
        return False

def test_change_ledger_generation():
    """测试变更台帐生成"""
    try:
        from src.services.change_service import ChangeService
        
        # 测试台帐生成
        result, error = ChangeService.generate_ledger("TEST-2026-001")
        if result:
            return True
        return False
    except Exception as e:
        print(f"变更台帐生成测试异常: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    framework = TestFramework()
    framework.start_test()
    
    # 测试核心模块
    framework.run_test('core', '核心模块加载', test_core_modules)
    framework.run_test('core', '数据库连接', test_database_connection)
    
    # 测试项目管理
    framework.run_test('project', '项目管理功能', test_project_management)
    
    # 测试变更管理
    framework.run_test('change', '变更管理功能', test_change_management)
    framework.run_test('change', '变更文档生成', test_change_document_generation)
    framework.run_test('change', '变更审批流程', test_change_approval_process)
    framework.run_test('change', '变更影响分析', test_change_impact_analysis)
    framework.run_test('change', '变更台帐生成', test_change_ledger_generation)
    
    # 测试库管理
    framework.run_test('library', '库管理功能', test_library_management)
    
    # 测试插件系统
    framework.run_test('plugin', '插件系统功能', test_plugin_system)
    
    # 测试API服务
    framework.run_test('api', 'API服务功能', test_api_service)
    
    framework.end_test()

if __name__ == "__main__":
    run_all_tests()
