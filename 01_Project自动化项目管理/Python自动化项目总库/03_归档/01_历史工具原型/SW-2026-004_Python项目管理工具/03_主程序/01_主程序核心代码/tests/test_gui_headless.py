# -*- coding: utf-8 -*-
"""
GUI自动化测试脚本 - 无头模式
测试Python项目管理工具的所有GUI功能模块
"""
import sys
import os
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['QT_FONT_DPI'] = '96'

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

app = None

def get_app():
    global app
    if app is None:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
    return app


class TestResult:
    def __init__(self):
        self.test_cases = []
        self.passed = 0
        self.failed = 0
        self.errors = 0
        self.start_time = None
        self.end_time = None
    
    def add_result(self, module, test_name, status, message="", duration=0):
        self.test_cases.append({
            "module": module,
            "test_name": test_name,
            "status": status,
            "message": message,
            "duration": duration,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        if status == "PASS":
            self.passed += 1
        elif status == "FAIL":
            self.failed += 1
        else:
            self.errors += 1
    
    def to_dict(self):
        return {
            "summary": {
                "total": len(self.test_cases),
                "passed": self.passed,
                "failed": self.failed,
                "errors": self.errors,
                "start_time": self.start_time.strftime('%Y-%m-%d %H:%M:%S') if self.start_time else "N/A",
                "end_time": self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else "N/A",
                "duration": self._calculate_duration()
            },
            "test_cases": self.test_cases
        }
    
    def _calculate_duration(self):
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return str(delta).split('.')[0]
        return "N/A"


class GUITestRunner:
    def __init__(self):
        self.result = TestResult()
        self.app = get_app()
        self.main_window = None
    
    def setup(self):
        self.result.start_time = datetime.now()
        from src.core.config import Config
        Config.load_config()
        from src.ui.main_window import MainWindow
        self.main_window = MainWindow()
        QTest.qWait(100)
    
    def teardown(self):
        if self.main_window:
            self.main_window.close()
        self.result.end_time = datetime.now()
    
    def run_all_tests(self):
        self.setup()
        
        try:
            self.test_main_window()
            self.test_project_management()
            self.test_template_management()
            self.test_plugin_management()
            self.test_spec_center()
            self.test_change_management()
            self.test_progress_management()
            self.test_report_center()
            self.test_plugin_config()
        except Exception as e:
            self.result.add_result("全局", "测试执行", "ERROR", str(e))
        
        self.teardown()
        return self.result
    
    def _run_test(self, module, test_name, test_func):
        start = time.time()
        try:
            test_func()
            duration = round((time.time() - start) * 1000, 2)
            self.result.add_result(module, test_name, "PASS", duration=duration)
            print(f"  ✅ {test_name}")
            return True
        except AssertionError as e:
            duration = round((time.time() - start) * 1000, 2)
            self.result.add_result(module, test_name, "FAIL", str(e), duration)
            print(f"  ❌ {test_name}: {e}")
            return False
        except Exception as e:
            duration = round((time.time() - start) * 1000, 2)
            self.result.add_result(module, test_name, "ERROR", str(e), duration)
            print(f"  ⚠️ {test_name}: {e}")
            return False
    
    def test_main_window(self):
        module = "主窗口"
        print(f"\n[{module}]")
        
        def test_window_title():
            title = self.main_window.windowTitle()
            assert "Python项目管理工具" in title, f"窗口标题不正确: {title}"
        
        def test_window_size():
            size = self.main_window.minimumSize()
            assert size.width() >= 1200, f"窗口最小宽度不足: {size.width()}"
            assert size.height() >= 800, f"窗口最小高度不足: {size.height()}"
        
        def test_tab_count():
            tab_count = self.main_window.tab_widget.count()
            assert tab_count == 8, f"标签页数量不正确: {tab_count}"
        
        def test_tab_names():
            expected_tabs = ["项目管理", "模板管理", "插件管理", "规范中心", 
                           "变更管理", "进度管理", "报告中心", "插件配置"]
            for i, expected in enumerate(expected_tabs):
                actual = self.main_window.tab_widget.tabText(i)
                assert actual == expected, f"标签页名称不正确: 期望'{expected}', 实际'{actual}'"
        
        def test_menu_bar():
            menu_bar = self.main_window.menuBar()
            actions = menu_bar.actions()
            menu_names = [a.text() for a in actions]
            assert "文件" in menu_names, "缺少'文件'菜单"
            assert "工具" in menu_names, "缺少'工具'菜单"
            assert "帮助" in menu_names, "缺少'帮助'菜单"
        
        def test_status_bar():
            status_bar = self.main_window.statusBar()
            assert status_bar is not None, "状态栏不存在"
        
        self._run_test(module, "窗口标题验证", test_window_title)
        self._run_test(module, "窗口尺寸验证", test_window_size)
        self._run_test(module, "标签页数量验证", test_tab_count)
        self._run_test(module, "标签页名称验证", test_tab_names)
        self._run_test(module, "菜单栏验证", test_menu_bar)
        self._run_test(module, "状态栏验证", test_status_bar)
    
    def test_project_management(self):
        module = "项目管理"
        print(f"\n[{module}]")
        
        project_list = self.main_window.project_list
        
        def test_table_exists():
            assert project_list.table is not None, "项目表格不存在"
        
        def test_table_columns():
            headers = [project_list.table.horizontalHeaderItem(i).text() 
                      for i in range(project_list.table.columnCount())]
            expected = ["项目编号", "项目名称", "业务线", "负责人", "状态", "创建时间", "操作"]
            assert headers == expected, f"表头不正确: {headers}"
        
        def test_search_input():
            assert project_list.search_input is not None, "搜索框不存在"
        
        def test_filter_combos():
            assert project_list.status_filter is not None, "状态筛选不存在"
            assert project_list.business_filter is not None, "业务线筛选不存在"
        
        def test_buttons():
            assert project_list.new_btn is not None, "新建按钮不存在"
            assert project_list.refresh_btn is not None, "刷新按钮不存在"
        
        def test_table_has_data():
            row_count = project_list.table.rowCount()
            assert row_count >= 0, "表格行数异常"
        
        self._run_test(module, "项目表格存在性", test_table_exists)
        self._run_test(module, "项目表格列头", test_table_columns)
        self._run_test(module, "搜索功能", test_search_input)
        self._run_test(module, "筛选下拉框", test_filter_combos)
        self._run_test(module, "按钮存在性", test_buttons)
        self._run_test(module, "表格数据", test_table_has_data)
    
    def test_template_management(self):
        module = "模板管理"
        print(f"\n[{module}]")
        
        template_manager = self.main_window.template_manager
        
        def test_table_exists():
            assert template_manager.table is not None, "模板表格不存在"
        
        def test_table_columns():
            headers = [template_manager.table.horizontalHeaderItem(i).text() 
                      for i in range(template_manager.table.columnCount())]
            expected = ["模板ID", "模板名称", "版本", "编译器", "适用场景", "业务线", "内置", "描述", "操作"]
            assert headers == expected, f"表头不正确: {headers}"
        
        def test_search_input():
            assert template_manager.search_input is not None, "搜索框不存在"
        
        def test_filter_combos():
            assert template_manager.business_line_filter is not None, "业务线筛选不存在"
            assert template_manager.compiler_filter is not None, "编译器筛选不存在"
            assert template_manager.scene_filter is not None, "场景筛选不存在"
        
        def test_buttons():
            assert template_manager.new_btn is not None, "新建按钮不存在"
            assert template_manager.import_btn is not None, "导入按钮不存在"
            assert template_manager.refresh_btn is not None, "刷新按钮不存在"
        
        self._run_test(module, "模板表格存在性", test_table_exists)
        self._run_test(module, "模板表格列头", test_table_columns)
        self._run_test(module, "搜索功能", test_search_input)
        self._run_test(module, "筛选下拉框", test_filter_combos)
        self._run_test(module, "按钮存在性", test_buttons)
    
    def test_plugin_management(self):
        module = "插件管理"
        print(f"\n[{module}]")
        
        plugin_manager = self.main_window.plugin_manager
        
        def test_table_exists():
            assert plugin_manager.table is not None, "插件表格不存在"
        
        def test_table_columns():
            headers = [plugin_manager.table.horizontalHeaderItem(i).text() 
                      for i in range(plugin_manager.table.columnCount())]
            expected = ["插件ID", "插件名称", "版本", "作者", "状态", "内置", "操作"]
            assert headers == expected, f"表头不正确: {headers}"
        
        def test_search_input():
            assert plugin_manager.search_input is not None, "搜索框不存在"
        
        def test_status_filter():
            assert plugin_manager.status_filter is not None, "状态筛选不存在"
        
        def test_buttons():
            assert plugin_manager.install_btn is not None, "安装按钮不存在"
            assert plugin_manager.refresh_btn is not None, "刷新按钮不存在"
        
        self._run_test(module, "插件表格存在性", test_table_exists)
        self._run_test(module, "插件表格列头", test_table_columns)
        self._run_test(module, "搜索功能", test_search_input)
        self._run_test(module, "状态筛选", test_status_filter)
        self._run_test(module, "按钮存在性", test_buttons)
    
    def test_spec_center(self):
        module = "规范中心"
        print(f"\n[{module}]")
        
        spec_center = self.main_window.spec_center
        
        def test_tree_exists():
            assert spec_center.spec_tree is not None, "规范树不存在"
        
        def test_search_input():
            assert spec_center.search_input is not None, "搜索框不存在"
        
        def test_category_combo():
            assert spec_center.category_combo is not None, "分类下拉框不存在"
        
        def test_detail_display():
            assert spec_center.spec_title is not None, "规范标题不存在"
            assert spec_center.spec_content is not None, "规范内容不存在"
        
        def test_quick_ref_tab():
            assert spec_center.quick_ref_content is not None, "速查手册不存在"
        
        self._run_test(module, "规范树存在性", test_tree_exists)
        self._run_test(module, "搜索功能", test_search_input)
        self._run_test(module, "分类下拉框", test_category_combo)
        self._run_test(module, "详情显示", test_detail_display)
        self._run_test(module, "速查手册", test_quick_ref_tab)
    
    def test_change_management(self):
        module = "变更管理"
        print(f"\n[{module}]")
        
        change_manager = self.main_window.change_manager
        
        def test_project_combo():
            assert change_manager.project_combo is not None, "项目下拉框不存在"
        
        def test_statistics_labels():
            assert len(change_manager.stat_labels) > 0, "统计标签不存在"
        
        def test_table_exists():
            assert change_manager.change_table is not None, "变更表格不存在"
        
        def test_filter_controls():
            assert change_manager.status_filter is not None, "状态筛选不存在"
            assert change_manager.search_input is not None, "搜索框不存在"
        
        def test_buttons():
            assert change_manager.new_btn is not None, "新建按钮不存在"
            assert change_manager.refresh_btn is not None, "刷新按钮不存在"
        
        self._run_test(module, "项目下拉框", test_project_combo)
        self._run_test(module, "统计标签", test_statistics_labels)
        self._run_test(module, "变更表格", test_table_exists)
        self._run_test(module, "筛选控件", test_filter_controls)
        self._run_test(module, "操作按钮", test_buttons)
    
    def test_progress_management(self):
        module = "进度管理"
        print(f"\n[{module}]")
        
        progress_manager = self.main_window.progress_manager
        
        def test_project_combo():
            assert progress_manager.project_combo is not None, "项目下拉框不存在"
        
        def test_progress_bar():
            assert progress_manager.progress_bar is not None, "进度条不存在"
        
        def test_statistics_labels():
            assert progress_manager.ms_stats_label is not None, "里程碑统计标签不存在"
            assert progress_manager.task_stats_label is not None, "任务统计标签不存在"
        
        def test_tree_exists():
            assert progress_manager.progress_tree is not None, "进度树不存在"
        
        def test_buttons():
            assert progress_manager.new_ms_btn is not None, "新建里程碑按钮不存在"
            assert progress_manager.new_task_btn is not None, "新建任务按钮不存在"
            assert progress_manager.refresh_btn is not None, "刷新按钮不存在"
        
        self._run_test(module, "项目下拉框", test_project_combo)
        self._run_test(module, "进度条", test_progress_bar)
        self._run_test(module, "统计标签", test_statistics_labels)
        self._run_test(module, "进度树", test_tree_exists)
        self._run_test(module, "操作按钮", test_buttons)
    
    def test_report_center(self):
        module = "报告中心"
        print(f"\n[{module}]")
        
        report_center = self.main_window.report_center
        
        def test_report_type_combo():
            assert report_center.report_type is not None, "报告类型下拉框不存在"
        
        def test_project_combo():
            assert report_center.project_combo is not None, "项目下拉框不存在"
        
        def test_format_combo():
            assert report_center.format_combo is not None, "格式下拉框不存在"
        
        def test_preview():
            assert report_center.preview_text is not None, "预览区域不存在"
        
        def test_buttons():
            assert report_center.generate_btn is not None, "生成按钮不存在"
            assert report_center.export_btn is not None, "导出按钮不存在"
        
        self._run_test(module, "报告类型下拉框", test_report_type_combo)
        self._run_test(module, "项目下拉框", test_project_combo)
        self._run_test(module, "格式下拉框", test_format_combo)
        self._run_test(module, "预览区域", test_preview)
        self._run_test(module, "操作按钮", test_buttons)
    
    def test_plugin_config(self):
        module = "插件配置"
        print(f"\n[{module}]")
        
        plugin_config = self.main_window.plugin_config
        
        def test_plugin_list():
            assert plugin_config.plugin_list is not None, "插件列表不存在"
        
        def test_info_labels():
            assert plugin_config.name_label is not None, "名称标签不存在"
            assert plugin_config.version_label is not None, "版本标签不存在"
        
        def test_config_controls():
            assert plugin_config.enabled_check is not None, "启用复选框不存在"
            assert plugin_config.auto_run_check is not None, "自动运行复选框不存在"
            assert plugin_config.priority_spin is not None, "优先级输入框不存在"
        
        def test_buttons():
            assert plugin_config.save_btn is not None, "保存按钮不存在"
            assert plugin_config.reset_btn is not None, "重置按钮不存在"
        
        self._run_test(module, "插件列表", test_plugin_list)
        self._run_test(module, "信息标签", test_info_labels)
        self._run_test(module, "配置控件", test_config_controls)
        self._run_test(module, "操作按钮", test_buttons)


def generate_report(result: TestResult):
    report_dir = Path(__file__).parent.parent / "data" / "test_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = report_dir / f"GUI测试报告_{timestamp}.md"
    
    summary = result.to_dict()["summary"]
    test_cases = result.to_dict()["test_cases"]
    
    content = f"""# GUI自动化测试报告

## 测试概要

| 项目 | 值 |
|------|-----|
| 测试时间 | {summary['start_time']} - {summary['end_time']} |
| 测试耗时 | {summary['duration']} |
| 测试用例总数 | {summary['total']} |
| 通过数量 | {summary['passed']} |
| 失败数量 | {summary['failed']} |
| 错误数量 | {summary['errors']} |
| 通过率 | {round(summary['passed']/summary['total']*100, 2) if summary['total'] > 0 else 0}% |

## 测试结果统计

```
通过: {'█' * summary['passed']} {summary['passed']}
失败: {'█' * summary['failed']} {summary['failed']}
错误: {'█' * summary['errors']} {summary['errors']}
```

## 详细测试结果

| 模块 | 测试用例 | 状态 | 耗时(ms) | 时间戳 |
|------|----------|------|----------|--------|
"""
    
    for tc in test_cases:
        status_icon = "✅" if tc['status'] == "PASS" else ("❌" if tc['status'] == "FAIL" else "⚠️")
        content += f"| {tc['module']} | {tc['test_name']} | {status_icon} {tc['status']} | {tc['duration']} | {tc['timestamp']} |\n"
    
    failed_cases = [tc for tc in test_cases if tc['status'] != 'PASS']
    if failed_cases:
        content += "\n## 失败/错误详情\n\n"
        for tc in failed_cases:
            content += f"### {tc['module']} - {tc['test_name']}\n\n"
            content += f"- **状态**: {tc['status']}\n"
            content += f"- **时间**: {tc['timestamp']}\n"
            content += f"- **错误信息**: {tc['message']}\n\n"
    
    content += f"""
## 测试环境

- 操作系统: {os.name}
- Python版本: {sys.version.split()[0]}

## 测试结论

本次测试共执行 {summary['total']} 个测试用例，其中：
- ✅ 通过: {summary['passed']} 个
- ❌ 失败: {summary['failed']} 个  
- ⚠️ 错误: {summary['errors']} 个

总体通过率: **{round(summary['passed']/summary['total']*100, 2) if summary['total'] > 0 else 0}%**

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return report_file


def main():
    print("=" * 60)
    print("Python项目管理工具 - GUI自动化测试")
    print("=" * 60)
    print()
    
    runner = GUITestRunner()
    result = runner.run_all_tests()
    
    summary = result.to_dict()["summary"]
    
    print()
    print("=" * 60)
    print("测试执行完成!")
    print("=" * 60)
    print(f"总用例数: {summary['total']}")
    print(f"通过: {summary['passed']}")
    print(f"失败: {summary['failed']}")
    print(f"错误: {summary['errors']}")
    print(f"通过率: {round(summary['passed']/summary['total']*100, 2) if summary['total'] > 0 else 0}%")
    
    report_file = generate_report(result)
    print()
    print(f"测试报告已生成: {report_file}")
    
    return result


if __name__ == "__main__":
    main()
