# -*- coding: utf-8 -*-
"""
自动化测试所有功能模块
无需手动操作GUI，自动执行测试
"""
import sys
import os
import time
import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class AutoTestRunner:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_start_time = None
    
    def start(self):
        """开始测试"""
        print("=" * 80)
        print("=== Python项目管理工具 - 自动化测试 ===")
        print(f"测试开始时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        self.test_start_time = time.time()
    
    def test(self, test_name, test_func):
        """执行单个测试"""
        self.total_tests += 1
        print(f"\n测试 {self.total_tests}: {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            if result:
                print(f"✅ 测试通过: {test_name}")
                self.passed_tests += 1
                status = "通过"
            else:
                print(f"❌ 测试失败: {test_name}")
                self.failed_tests += 1
                status = "失败"
        except Exception as e:
            print(f"❌ 测试异常: {test_name} - {str(e)}")
            self.failed_tests += 1
            status = f"异常: {str(e)}"
        
        self.test_results.append({
            "name": test_name,
            "status": status,
            "time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    def finish(self):
        """结束测试"""
        test_duration = time.time() - self.test_start_time
        
        print("\n" + "=" * 80)
        print("=== 测试结果汇总 ===")
        print(f"测试结束时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"测试持续时间: {test_duration:.2f} 秒")
        print(f"总测试数: {self.total_tests}")
        print(f"通过: {self.passed_tests}")
        print(f"失败: {self.failed_tests}")
        print(f"通过率: {(self.passed_tests / self.total_tests * 100):.1f}%")
        
        if self.failed_tests == 0:
            print("\n🎉 所有测试通过！系统功能正常")
        else:
            print("\n⚠️ 部分测试失败，需要检查和修复")
            print("\n失败的测试:")
            for result in self.test_results:
                if not result["status"] == "通过":
                    print(f"- {result['name']}: {result['status']}")
        
        # 生成测试报告
        self.generate_report(test_duration)
    
    def generate_report(self, duration):
        """生成测试报告"""
        report_dir = os.path.join("data", "test_reports")
        os.makedirs(report_dir, exist_ok=True)
        
        report_file = os.path.join(report_dir, f"自动化测试报告_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("# Python项目管理工具 - 自动化测试报告\n\n")
            f.write(f"**测试时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**测试持续时间**: {duration:.2f} 秒\n\n")
            f.write("## 测试结果\n")
            f.write(f"- 总测试数: {self.total_tests}\n")
            f.write(f"- 通过: {self.passed_tests}\n")
            f.write(f"- 失败: {self.failed_tests}\n")
            f.write(f"- 通过率: {(self.passed_tests / self.total_tests * 100):.1f}%\n\n")
            f.write("## 测试详情\n")
            for i, result in enumerate(self.test_results, 1):
                f.write(f"### 测试 {i}: {result['name']}\n")
                f.write(f"- 状态: {result['status']}\n")
                f.write(f"- 时间: {result['time']}\n\n")
        
        print(f"\n测试报告已生成: {report_file}")

def test_core_imports():
    """测试核心模块导入"""
    try:
        from src.core.config import Config
        from src.core.constants import ChangeStatus
        from src.core.version import __version__
        return True
    except Exception as e:
        print(f"核心模块导入失败: {e}")
        return False

def test_database():
    """测试数据库连接"""
    try:
        from src.dao.database import Database
        db = Database()
        engine = db.get_engine()
        return engine is not None
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return False

def test_project_service():
    """测试项目服务"""
    try:
        from src.services.project_service import ProjectService
        projects, total = ProjectService.list_projects(size=10)
        return True
    except Exception as e:
        print(f"项目服务测试失败: {e}")
        return False

def test_change_service():
    """测试变更服务"""
    try:
        from src.services.change_service import ChangeService
        changes = ChangeService.get_changes()
        return True
    except Exception as e:
        print(f"变更服务测试失败: {e}")
        return False

def test_statistics_service():
    """测试统计服务"""
    try:
        from src.services.statistics_service import StatisticsService
        overview = StatisticsService.get_overview()
        return True
    except Exception as e:
        print(f"统计服务测试失败: {e}")
        return False

def test_library_service():
    """测试库服务"""
    try:
        from src.services.library_service import LibraryService
        libraries = LibraryService.list_libraries()
        return True
    except Exception as e:
        print(f"库服务测试失败: {e}")
        return False

def test_plugin_service():
    """测试插件服务"""
    try:
        from src.services.plugin_service import PluginService
        plugins = PluginService.get_plugins()
        return True
    except Exception as e:
        print(f"插件服务测试失败: {e}")
        return False

def test_template_service():
    """测试模板服务"""
    try:
        from src.services.template_service import TemplateService
        templates = TemplateService.list_templates()
        return True
    except Exception as e:
        print(f"模板服务测试失败: {e}")
        return False

def test_change_document_generation():
    """测试变更文档生成"""
    try:
        from src.services.change_service import ChangeService
        # 创建测试变更单
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
            return result is not None
        return False
    except Exception as e:
        print(f"变更文档生成测试失败: {e}")
        return False

def test_change_approval():
    """测试变更审批"""
    try:
        from src.services.change_service import ChangeService
        # 创建测试变更单
        change_data = {
            "project_id": "TEST-2026-002",
            "title": "测试变更审批",
            "type": "测试",
            "description": "测试变更审批功能",
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
                return success
        return False
    except Exception as e:
        print(f"变更审批测试失败: {e}")
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
            "description": "测试变更影响分析功能",
            "reason": "功能验证",
            "impact": "测试影响",
            "proposer": "自动化测试"
        }
        change, error = ChangeService.create_change(**change_data)
        if change:
            # 测试影响分析
            result = ImpactService.analyze_impact(change.change_id)
            return "risk_level" in result
        return False
    except Exception as e:
        print(f"变更影响分析测试失败: {e}")
        return False

def test_change_ledger():
    """测试变更台帐生成"""
    try:
        from src.services.change_service import ChangeService
        # 测试台帐生成
        result, error = ChangeService.generate_ledger("TEST-2026-001")
        return result is not None
    except Exception as e:
        print(f"变更台帐生成测试失败: {e}")
        return False

def main():
    """主测试函数"""
    runner = AutoTestRunner()
    runner.start()
    
    # 测试核心模块
    runner.test("核心模块导入", test_core_imports)
    runner.test("数据库连接", test_database)
    
    # 测试服务模块
    runner.test("项目服务", test_project_service)
    runner.test("变更服务", test_change_service)
    runner.test("统计服务", test_statistics_service)
    runner.test("库服务", test_library_service)
    runner.test("插件服务", test_plugin_service)
    runner.test("模板服务", test_template_service)
    
    # 测试变更管理功能
    runner.test("变更文档生成", test_change_document_generation)
    runner.test("变更审批流程", test_change_approval)
    runner.test("变更影响分析", test_change_impact_analysis)
    runner.test("变更台帐生成", test_change_ledger)
    
    runner.finish()

if __name__ == "__main__":
    main()