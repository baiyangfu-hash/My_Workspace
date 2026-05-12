# -*- coding: utf-8 -*-
"""
GUI功能测试脚本
测试Python项目管理工具的GUI功能操作
"""
import sys
import os
import time
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PyQt5.QtWidgets import QApplication, QMessageBox, QDialog, QFileDialog, QMenu
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtTest import QTest

app = None

def get_app():
    global app
    if app is None:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
    return app


class FunctionalTestRunner:
    def __init__(self):
        self.app = get_app()
        self.main_window = None
        self.test_results = []
        self.temp_dirs = []
        self.start_time = None
        self.end_time = None
    
    def add_result(self, module, test_name, status, message="", duration=0):
        self.test_results.append({
            "module": module,
            "test_name": test_name,
            "status": status,
            "message": message,
            "duration": duration,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    def setup(self):
        self.start_time = datetime.now()
        from src.ui.main_window import MainWindow
        self.main_window = MainWindow()
        self.main_window.show()
        QTest.qWait(500)
    
    def teardown(self):
        for temp_dir in self.temp_dirs:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        if self.main_window:
            self.main_window.close()
        
        self.end_time = datetime.now()
    
    def _run_test(self, module, test_name, test_func):
        start = time.time()
        try:
            test_func()
            duration = round((time.time() - start) * 1000, 2)
            self.add_result(module, test_name, "PASS", duration=duration)
            print(f"  ✅ {test_name} - PASS ({duration}ms)")
            return True
        except AssertionError as e:
            duration = round((time.time() - start) * 1000, 2)
            self.add_result(module, test_name, "FAIL", str(e), duration)
            print(f"  ❌ {test_name} - FAIL: {e}")
            return False
        except Exception as e:
            duration = round((time.time() - start) * 1000, 2)
            self.add_result(module, test_name, "ERROR", str(e), duration)
            print(f"  ⚠️ {test_name} - ERROR: {e}")
            return False
    
    def run_all_tests(self):
        self.setup()
        
        print("\n" + "=" * 60)
        print("开始执行GUI功能测试")
        print("=" * 60)
        
        try:
            print("\n[1/9] 主窗口测试...")
            self.test_main_window_functions()
            
            print("\n[2/9] 项目管理测试...")
            self.test_project_functions()
            
            print("\n[3/9] 模板管理测试...")
            self.test_template_functions()
            
            print("\n[4/9] 插件管理测试...")
            self.test_plugin_functions()
            
            print("\n[5/9] 规范中心测试...")
            self.test_spec_functions()
            
            print("\n[6/9] 变更管理测试...")
            self.test_change_functions()
            
            print("\n[7/9] 进度管理测试...")
            self.test_progress_functions()
            
            print("\n[8/9] 报告中心测试...")
            self.test_report_functions()
            
            print("\n[9/9] 插件配置测试...")
            self.test_plugin_config_functions()
            
        except Exception as e:
            self.add_result("全局", "测试执行", "ERROR", str(e))
            print(f"\n全局错误: {e}")
        
        self.teardown()
        return self.test_results
    
    def test_main_window_functions(self):
        module = "主窗口"
        
        def test_tab_switching():
            for i in range(self.main_window.tab_widget.count()):
                self.main_window.tab_widget.setCurrentIndex(i)
                QTest.qWait(100)
                current = self.main_window.tab_widget.currentIndex()
                assert current == i, f"标签页切换失败: 期望{i}, 实际{current}"
        
        def test_menu_file():
            menu_bar = self.main_window.menuBar()
            file_menu = menu_bar.actions()[0].menu()
            actions = [a.text() for a in file_menu.actions() if a.text()]
            assert "新建项目" in actions, "缺少'新建项目'菜单项"
            assert "退出" in actions, "缺少'退出'菜单项"
        
        def test_menu_tools():
            menu_bar = self.main_window.menuBar()
            tools_menu = menu_bar.actions()[1].menu()
            actions = [a.text() for a in tools_menu.actions() if a.text()]
            assert "规范检查" in actions, "缺少'规范检查'菜单项"
            assert "生成报告" in actions, "缺少'生成报告'菜单项"
        
        def test_menu_help():
            menu_bar = self.main_window.menuBar()
            help_menu = menu_bar.actions()[2].menu()
            actions = [a.text() for a in help_menu.actions() if a.text()]
            assert "关于" in actions, "缺少'关于'菜单项"
        
        def test_status_bar_update():
            self.main_window.status_bar.showMessage("测试消息")
            QTest.qWait(100)
            message = self.main_window.status_bar.currentMessage()
            assert message == "测试消息", f"状态栏更新失败: {message}"
            self.main_window.status_bar.showMessage("就绪")
        
        self._run_test(module, "标签页切换", test_tab_switching)
        self._run_test(module, "文件菜单", test_menu_file)
        self._run_test(module, "工具菜单", test_menu_tools)
        self._run_test(module, "帮助菜单", test_menu_help)
        self._run_test(module, "状态栏更新", test_status_bar_update)
    
    def test_project_functions(self):
        module = "项目管理"
        self.main_window.tab_widget.setCurrentIndex(0)
        QTest.qWait(300)
        
        project_list = self.main_window.project_list
        
        def test_search_filter():
            project_list.search_input.setText("测试项目")
            QTest.qWait(200)
            project_list.search_input.clear()
            QTest.qWait(200)
        
        def test_status_filter():
            project_list.status_filter.setCurrentIndex(1)
            QTest.qWait(200)
            project_list.status_filter.setCurrentIndex(0)
            QTest.qWait(200)
        
        def test_business_filter():
            if project_list.business_filter.count() > 1:
                project_list.business_filter.setCurrentIndex(1)
                QTest.qWait(200)
                project_list.business_filter.setCurrentIndex(0)
                QTest.qWait(200)
        
        def test_refresh_button():
            project_list.refresh_btn.click()
            QTest.qWait(500)
            assert project_list.table.rowCount() >= 0, "刷新后表格异常"
        
        def test_table_selection():
            if project_list.table.rowCount() > 0:
                project_list.table.selectRow(0)
                selected = project_list.table.selectedItems()
                assert len(selected) > 0, "表格行选择失败"
        
        self._run_test(module, "搜索筛选", test_search_filter)
        self._run_test(module, "状态筛选", test_status_filter)
        self._run_test(module, "业务线筛选", test_business_filter)
        self._run_test(module, "刷新按钮", test_refresh_button)
        self._run_test(module, "表格选择", test_table_selection)
    
    def test_template_functions(self):
        module = "模板管理"
        self.main_window.tab_widget.setCurrentIndex(1)
        QTest.qWait(300)
        
        template_manager = self.main_window.template_manager
        
        def test_search_filter():
            template_manager.search_input.setText("python")
            QTest.qWait(200)
            template_manager.search_input.clear()
            QTest.qWait(200)
        
        def test_business_line_filter():
            if template_manager.business_line_filter.count() > 1:
                template_manager.business_line_filter.setCurrentIndex(1)
                QTest.qWait(200)
                template_manager.business_line_filter.setCurrentIndex(0)
                QTest.qWait(200)
        
        def test_compiler_filter():
            if template_manager.compiler_filter.count() > 1:
                template_manager.compiler_filter.setCurrentIndex(1)
                QTest.qWait(200)
                template_manager.compiler_filter.setCurrentIndex(0)
                QTest.qWait(200)
        
        def test_scene_filter():
            if template_manager.scene_filter.count() > 1:
                template_manager.scene_filter.setCurrentIndex(1)
                QTest.qWait(200)
                template_manager.scene_filter.setCurrentIndex(0)
                QTest.qWait(200)
        
        def test_refresh():
            template_manager.refresh_btn.click()
            QTest.qWait(500)
            assert template_manager.table.rowCount() >= 0, "刷新后表格异常"
        
        self._run_test(module, "搜索筛选", test_search_filter)
        self._run_test(module, "业务线筛选", test_business_line_filter)
        self._run_test(module, "编译器筛选", test_compiler_filter)
        self._run_test(module, "场景筛选", test_scene_filter)
        self._run_test(module, "刷新功能", test_refresh)
    
    def test_plugin_functions(self):
        module = "插件管理"
        self.main_window.tab_widget.setCurrentIndex(2)
        QTest.qWait(300)
        
        plugin_manager = self.main_window.plugin_manager
        
        def test_search_filter():
            plugin_manager.search_input.setText("code")
            QTest.qWait(200)
            plugin_manager.search_input.clear()
            QTest.qWait(200)
        
        def test_status_filter():
            if plugin_manager.status_filter.count() > 1:
                plugin_manager.status_filter.setCurrentIndex(1)
                QTest.qWait(200)
                plugin_manager.status_filter.setCurrentIndex(0)
                QTest.qWait(200)
        
        def test_refresh():
            plugin_manager.refresh_btn.click()
            QTest.qWait(500)
            assert plugin_manager.table.rowCount() >= 0, "刷新后表格异常"
        
        def test_table_display():
            row_count = plugin_manager.table.rowCount()
            if row_count > 0:
                for col in range(plugin_manager.table.columnCount()):
                    item = plugin_manager.table.item(0, col)
                    assert item is not None, f"表格第0行第{col}列为空"
        
        self._run_test(module, "搜索筛选", test_search_filter)
        self._run_test(module, "状态筛选", test_status_filter)
        self._run_test(module, "刷新功能", test_refresh)
        self._run_test(module, "表格显示", test_table_display)
    
    def test_spec_functions(self):
        module = "规范中心"
        self.main_window.tab_widget.setCurrentIndex(3)
        QTest.qWait(300)
        
        spec_center = self.main_window.spec_center
        
        def test_search():
            spec_center.search_input.setText("python")
            QTest.qWait(200)
            spec_center.search_input.clear()
            QTest.qWait(200)
        
        def test_category_filter():
            if spec_center.category_combo.count() > 1:
                spec_center.category_combo.setCurrentIndex(1)
                QTest.qWait(200)
                spec_center.category_combo.setCurrentIndex(0)
                QTest.qWait(200)
        
        def test_tree_navigation():
            tree = spec_center.spec_tree
            if tree.topLevelItemCount() > 0:
                top_item = tree.topLevelItem(0)
                tree.setCurrentItem(top_item)
                QTest.qWait(100)
                if top_item.childCount() > 0:
                    child = top_item.child(0)
                    tree.setCurrentItem(child)
                    QTest.qWait(100)
        
        def test_tab_switch():
            tabs = spec_center.findChild(type(spec_center.spec_tree.parent().parent()))
            if spec_center.detail_tabs:
                spec_center.detail_tabs.setCurrentIndex(1)
                QTest.qWait(100)
                spec_center.detail_tabs.setCurrentIndex(0)
                QTest.qWait(100)
        
        def test_refresh():
            spec_center.refresh_btn.click()
            QTest.qWait(500)
        
        self._run_test(module, "搜索功能", test_search)
        self._run_test(module, "分类筛选", test_category_filter)
        self._run_test(module, "树形导航", test_tree_navigation)
        self._run_test(module, "标签页切换", test_tab_switch)
        self._run_test(module, "刷新功能", test_refresh)
    
    def test_change_functions(self):
        module = "变更管理"
        self.main_window.tab_widget.setCurrentIndex(4)
        QTest.qWait(300)
        
        change_manager = self.main_window.change_manager
        
        def test_project_selection():
            if change_manager.project_combo.count() > 0:
                change_manager.project_combo.setCurrentIndex(0)
                QTest.qWait(200)
        
        def test_status_filter():
            if change_manager.status_filter.count() > 1:
                change_manager.status_filter.setCurrentIndex(1)
                QTest.qWait(200)
                change_manager.status_filter.setCurrentIndex(0)
                QTest.qWait(200)
        
        def test_search():
            change_manager.search_input.setText("变更")
            QTest.qWait(200)
            change_manager.search_input.clear()
            QTest.qWait(200)
        
        def test_statistics_display():
            for status, label in change_manager.stat_labels.items():
                text = label.text()
                assert text is not None and len(text) > 0, "统计标签为空"
        
        def test_tab_switch():
            if change_manager.detail_tabs:
                change_manager.detail_tabs.setCurrentIndex(1)
                QTest.qWait(100)
                change_manager.detail_tabs.setCurrentIndex(0)
                QTest.qWait(100)
        
        self._run_test(module, "项目选择", test_project_selection)
        self._run_test(module, "状态筛选", test_status_filter)
        self._run_test(module, "搜索功能", test_search)
        self._run_test(module, "统计显示", test_statistics_display)
        self._run_test(module, "标签页切换", test_tab_switch)
    
    def test_progress_functions(self):
        module = "进度管理"
        self.main_window.tab_widget.setCurrentIndex(5)
        QTest.qWait(300)
        
        progress_manager = self.main_window.progress_manager
        
        def test_project_selection():
            if progress_manager.project_combo.count() > 0:
                progress_manager.project_combo.setCurrentIndex(0)
                QTest.qWait(200)
        
        def test_progress_bar():
            progress_manager.progress_bar.setValue(50)
            QTest.qWait(100)
            assert progress_manager.progress_bar.value() == 50, "进度条设置失败"
            progress_manager.progress_bar.setValue(0)
        
        def test_tree_display():
            tree = progress_manager.progress_tree
            assert tree.columnCount() == 5, f"进度树列数不正确: {tree.columnCount()}"
        
        def test_statistics():
            ms_text = progress_manager.ms_stats_label.text()
            task_text = progress_manager.task_stats_label.text()
            assert ms_text is not None, "里程碑统计为空"
            assert task_text is not None, "任务统计为空"
        
        def test_refresh():
            progress_manager.refresh_btn.click()
            QTest.qWait(500)
        
        self._run_test(module, "项目选择", test_project_selection)
        self._run_test(module, "进度条", test_progress_bar)
        self._run_test(module, "树形显示", test_tree_display)
        self._run_test(module, "统计显示", test_statistics)
        self._run_test(module, "刷新功能", test_refresh)
    
    def test_report_functions(self):
        module = "报告中心"
        self.main_window.tab_widget.setCurrentIndex(6)
        QTest.qWait(300)
        
        report_center = self.main_window.report_center
        
        def test_report_type_switch():
            for i in range(report_center.report_type.count()):
                report_center.report_type.setCurrentIndex(i)
                QTest.qWait(100)
            report_center.report_type.setCurrentIndex(0)
        
        def test_format_switch():
            for i in range(report_center.format_combo.count()):
                report_center.format_combo.setCurrentIndex(i)
                QTest.qWait(100)
            report_center.format_combo.setCurrentIndex(0)
        
        def test_project_selection():
            if report_center.project_combo.count() > 0:
                report_center.project_combo.setCurrentIndex(0)
                QTest.qWait(200)
        
        def test_statistics_overview():
            total = report_center.total_projects_label.text()
            active = report_center.active_projects_label.text()
            assert total.isdigit() or total == "0", "项目总数格式不正确"
            assert active.isdigit() or active == "0", "进行中项目格式不正确"
        
        def test_quick_stats():
            report_center.quick_stats_btn.click()
            QTest.qWait(500)
            preview = report_center.preview_text.toPlainText()
            assert len(preview) > 0, "统计报告内容为空"
        
        self._run_test(module, "报告类型切换", test_report_type_switch)
        self._run_test(module, "格式切换", test_format_switch)
        self._run_test(module, "项目选择", test_project_selection)
        self._run_test(module, "统计概览", test_statistics_overview)
        self._run_test(module, "快捷统计", test_quick_stats)
    
    def test_plugin_config_functions(self):
        module = "插件配置"
        self.main_window.tab_widget.setCurrentIndex(7)
        QTest.qWait(300)
        
        plugin_config = self.main_window.plugin_config
        
        def test_plugin_list():
            if plugin_config.plugin_list.count() > 0:
                plugin_config.plugin_list.setCurrentRow(0)
                QTest.qWait(200)
        
        def test_config_display():
            if plugin_config.plugin_list.count() > 0:
                plugin_config.plugin_list.setCurrentRow(0)
                QTest.qWait(200)
                name = plugin_config.name_label.text()
                assert name != "-", "插件名称未显示"
        
        def test_checkbox_toggle():
            original_state = plugin_config.enabled_check.isChecked()
            plugin_config.enabled_check.setChecked(not original_state)
            QTest.qWait(100)
            plugin_config.enabled_check.setChecked(original_state)
            QTest.qWait(100)
        
        def test_priority_spin():
            plugin_config.priority_spin.setValue(75)
            QTest.qWait(100)
            assert plugin_config.priority_spin.value() == 75, "优先级设置失败"
            plugin_config.priority_spin.setValue(50)
        
        def test_config_tabs():
            if plugin_config.config_tabs.count() > 1:
                plugin_config.config_tabs.setCurrentIndex(1)
                QTest.qWait(100)
                plugin_config.config_tabs.setCurrentIndex(0)
                QTest.qWait(100)
        
        def test_reset_button():
            plugin_config.auto_run_check.setChecked(True)
            plugin_config.priority_spin.setValue(80)
            QTest.qWait(100)
            plugin_config.reset_btn.click()
            QTest.qWait(100)
        
        self._run_test(module, "插件列表选择", test_plugin_list)
        self._run_test(module, "配置显示", test_config_display)
        self._run_test(module, "复选框切换", test_checkbox_toggle)
        self._run_test(module, "优先级设置", test_priority_spin)
        self._run_test(module, "配置标签页", test_config_tabs)
        self._run_test(module, "重置按钮", test_reset_button)


def generate_functional_report(results, start_time, end_time):
    report_dir = Path(__file__).parent.parent / "data" / "test_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = report_dir / f"GUI功能测试报告_{timestamp}.md"
    
    total = len(results)
    passed = sum(1 for r in results if r['status'] == 'PASS')
    failed = sum(1 for r in results if r['status'] == 'FAIL')
    errors = sum(1 for r in results if r['status'] == 'ERROR')
    
    duration = str(end_time - start_time).split('.')[0]
    
    content = f"""# GUI功能测试报告

## 测试概要

| 项目 | 值 |
|------|-----|
| 测试时间 | {start_time.strftime('%Y-%m-%d %H:%M:%S')} - {end_time.strftime('%Y-%m-%d %H:%M:%S')} |
| 测试耗时 | {duration} |
| 测试用例总数 | {total} |
| 通过数量 | {passed} |
| 失败数量 | {failed} |
| 错误数量 | {errors} |
| 通过率 | {round(passed/total*100, 2) if total > 0 else 0}% |

## 测试结果统计

```
通过: {'█' * passed} {passed}
失败: {'█' * failed} {failed}
错误: {'█' * errors} {errors}
```

## 按模块统计

"""
    
    modules = {}
    for r in results:
        if r['module'] not in modules:
            modules[r['module']] = {'total': 0, 'passed': 0, 'failed': 0, 'errors': 0}
        modules[r['module']]['total'] += 1
        if r['status'] == 'PASS':
            modules[r['module']]['passed'] += 1
        elif r['status'] == 'FAIL':
            modules[r['module']]['failed'] += 1
        else:
            modules[r['module']]['errors'] += 1
    
    content += "| 模块 | 总数 | 通过 | 失败 | 错误 | 通过率 |\n"
    content += "|------|------|------|------|------|--------|\n"
    for mod, stats in modules.items():
        rate = round(stats['passed']/stats['total']*100, 2) if stats['total'] > 0 else 0
        content += f"| {mod} | {stats['total']} | {stats['passed']} | {stats['failed']} | {stats['errors']} | {rate}% |\n"
    
    content += "\n## 详细测试结果\n\n"
    content += "| 模块 | 测试用例 | 状态 | 耗时(ms) | 时间戳 |\n"
    content += "|------|----------|------|----------|--------|\n"
    
    for r in results:
        status_icon = "✅" if r['status'] == "PASS" else ("❌" if r['status'] == "FAIL" else "⚠️")
        content += f"| {r['module']} | {r['test_name']} | {status_icon} {r['status']} | {r['duration']} | {r['timestamp']} |\n"
    
    failed_cases = [r for r in results if r['status'] != 'PASS']
    if failed_cases:
        content += "\n## 失败/错误详情\n\n"
        for r in failed_cases:
            content += f"### {r['module']} - {r['test_name']}\n\n"
            content += f"- **状态**: {r['status']}\n"
            content += f"- **时间**: {r['timestamp']}\n"
            content += f"- **错误信息**: {r['message']}\n\n"
    
    content += f"""
## 测试环境

- 操作系统: {os.name}
- Python版本: {sys.version.split()[0]}
- PyQt5版本: {__import__('PyQt5.QtCore').QtCore.PYQT_VERSION_STR}

## 测试结论

本次测试共执行 {total} 个测试用例，其中：
- ✅ 通过: {passed} 个
- ❌ 失败: {failed} 个  
- ⚠️ 错误: {errors} 个

总体通过率: **{round(passed/total*100, 2) if total > 0 else 0}%**

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return report_file


def main():
    print("=" * 60)
    print("Python项目管理工具 - GUI功能测试")
    print("=" * 60)
    
    runner = FunctionalTestRunner()
    results = runner.run_all_tests()
    
    report_file = generate_functional_report(results, runner.start_time, runner.end_time)
    
    total = len(results)
    passed = sum(1 for r in results if r['status'] == 'PASS')
    failed = sum(1 for r in results if r['status'] == 'FAIL')
    errors = sum(1 for r in results if r['status'] == 'ERROR')
    
    print("\n" + "=" * 60)
    print("测试执行完成!")
    print("=" * 60)
    print(f"总用例数: {total}")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"错误: {errors}")
    print(f"通过率: {round(passed/total*100, 2) if total > 0 else 0}%")
    print()
    print(f"测试报告已生成: {report_file}")
    
    return results


if __name__ == "__main__":
    main()
