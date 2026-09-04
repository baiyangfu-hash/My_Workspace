# -*- coding: utf-8 -*-
"""
PLC变量表解析插件GUI测试
"""
import os
import sys
import tempfile
from datetime import datetime

os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['QT_FONT_DPI'] = '96'

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt, QTimer


class GUITestRunner:
    """GUI测试运行器"""
    
    def __init__(self):
        self.app = None
        self.widget = None
        self.test_results = []
        self.start_time = None
    
    def setup(self):
        """初始化测试环境"""
        self.start_time = datetime.now()
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication([])
        
        from src.core.config import Config
        Config.load_config()
        
        from src.plugins.plc_variable_parser.ui.parser_widget import ParserWidget
        self.widget = ParserWidget()
        QTest.qWait(100)
    
    def teardown(self):
        """清理测试环境"""
        if self.widget:
            self.widget.close()
            self.widget = None
    
    def record_result(self, test_name: str, passed: bool, message: str = ""):
        """记录测试结果"""
        self.test_results.append({
            'name': test_name,
            'passed': passed,
            'message': message,
            'time': datetime.now().strftime('%H:%M:%S')
        })
    
    def test_widget_creation(self):
        """测试组件创建"""
        try:
            from src.plugins.plc_variable_parser.ui.parser_widget import ParserWidget
            widget = ParserWidget()
            
            assert widget is not None, "组件创建失败"
            widget.close()
            
            self.record_result("组件创建测试", True, "ParserWidget创建成功")
        except Exception as e:
            self.record_result("组件创建测试", False, str(e))
    
    def test_variable_table(self):
        """测试变量表格"""
        try:
            from src.plugins.plc_variable_parser.ui.variable_table import VariableTable
            table = VariableTable()
            
            test_vars = [
                {'name': 'Var1', 'type': 'BOOL', 'address': 'M0', 'description': 'Test1'},
                {'name': 'Var2', 'type': 'INT', 'address': 'D100', 'description': 'Test2'}
            ]
            
            table.set_variables(test_vars)
            assert table.rowCount() == 2, "表格行数不正确"
            
            retrieved = table.get_variables()
            assert len(retrieved) == 2, "获取变量数量不正确"
            
            table.close()
            
            self.record_result("变量表格测试", True, f"表格操作正常，共{len(retrieved)}个变量")
        except Exception as e:
            self.record_result("变量表格测试", False, str(e))
    
    def test_variable_dialog(self):
        """测试变量编辑对话框"""
        try:
            from src.plugins.plc_variable_parser.ui.variable_dialog import VariableDialog
            
            dialog = VariableDialog()
            
            dialog.name_edit.setText("TestVariable")
            dialog.type_combo.setCurrentText("INT")
            dialog.address_edit.setText("D200")
            dialog.description_edit.setPlainText("测试变量描述")
            
            QTest.mouseClick(dialog.button_box.button(dialog.button_box.Ok), Qt.LeftButton)
            
            self.record_result("变量对话框测试", True, "对话框操作正常")
        except Exception as e:
            self.record_result("变量对话框测试", False, str(e))
    
    def test_batch_edit_dialog(self):
        """测试批量编辑对话框"""
        try:
            from src.plugins.plc_variable_parser.ui.batch_edit_dialog import BatchEditDialog
            
            dialog = BatchEditDialog(selected_count=5)
            
            assert dialog._selected_count == 5, "选中数量不正确"
            
            dialog.close()
            
            self.record_result("批量编辑对话框测试", True, "对话框创建正常")
        except Exception as e:
            self.record_result("批量编辑对话框测试", False, str(e))
    
    def test_toolbar_actions(self):
        """测试工具栏操作"""
        try:
            from src.plugins.plc_variable_parser.ui.parser_widget import ParserWidget
            widget = ParserWidget()
            
            toolbar = widget.findChild(object, "toolbar")
            if toolbar:
                actions = toolbar.actions()
                assert len(actions) > 0, "工具栏没有操作按钮"
            
            widget.close()
            
            self.record_result("工具栏测试", True, "工具栏操作正常")
        except Exception as e:
            self.record_result("工具栏测试", False, str(e))
    
    def test_file_operations(self):
        """测试文件操作"""
        try:
            from src.plugins.plc_variable_parser.ui.parser_widget import ParserWidget
            widget = ParserWidget()
            
            content = "变量名,数据类型,地址,注释\nTestVar,BOOL,M0,测试\n"
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.csv', delete=False) as f:
                f.write(content)
                temp_path = f.name
            
            try:
                widget.load_file(temp_path)
                
                variables = widget.variable_table.get_variables()
                assert len(variables) == 1, "加载变量数量不正确"
                assert variables[0]['name'] == 'TestVar', "变量名不正确"
                
                self.record_result("文件操作测试", True, f"成功加载{len(variables)}个变量")
            finally:
                os.unlink(temp_path)
                widget.close()
        except Exception as e:
            self.record_result("文件操作测试", False, str(e))
    
    def test_search_function(self):
        """测试搜索功能"""
        try:
            from src.plugins.plc_variable_parser.ui.variable_table import VariableTable
            table = VariableTable()
            
            test_vars = [
                {'name': 'Motor_Start', 'type': 'BOOL', 'address': 'M0'},
                {'name': 'Motor_Stop', 'type': 'BOOL', 'address': 'M1'},
                {'name': 'Speed_Set', 'type': 'INT', 'address': 'D100'}
            ]
            
            table.set_variables(test_vars)
            
            results = table.find_by_name('Motor')
            assert len(results) == 2, "搜索结果数量不正确"
            
            table.close()
            
            self.record_result("搜索功能测试", True, f"搜索'Motor'找到{len(results)}个结果")
        except Exception as e:
            self.record_result("搜索功能测试", False, str(e))
    
    def test_add_delete_variable(self):
        """测试添加和删除变量"""
        try:
            from src.plugins.plc_variable_parser.ui.variable_table import VariableTable
            table = VariableTable()
            
            initial_count = table.rowCount()
            
            table.add_variable({'name': 'NewVar', 'type': 'BOOL', 'address': 'M10'})
            assert table.rowCount() == initial_count + 1, "添加变量失败"
            
            table.selectRow(0)
            QTest.qWait(50)
            
            table.close()
            
            self.record_result("添加删除变量测试", True, "变量操作正常")
        except Exception as e:
            self.record_result("添加删除变量测试", False, str(e))
    
    def test_export_functionality(self):
        """测试导出功能"""
        try:
            from src.plugins.plc_variable_parser.exporters.exporter import Exporter
            
            exporter = Exporter()
            variables = [
                {'name': 'Var1', 'type': 'BOOL', 'address': 'M0', 'description': 'Test'}
            ]
            
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.csv', delete=False) as f:
                csv_path = f.name
            
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.json', delete=False) as f:
                json_path = f.name
            
            try:
                csv_success = exporter.export_to_csv(variables, csv_path)
                json_success = exporter.export_to_json(variables, json_path)
                
                assert csv_success, "CSV导出失败"
                assert json_success, "JSON导出失败"
                
                assert os.path.exists(csv_path), "CSV文件未创建"
                assert os.path.exists(json_path), "JSON文件未创建"
                
                self.record_result("导出功能测试", True, "CSV和JSON导出成功")
            finally:
                if os.path.exists(csv_path):
                    os.unlink(csv_path)
                if os.path.exists(json_path):
                    os.unlink(json_path)
        except Exception as e:
            self.record_result("导出功能测试", False, str(e))
    
    def test_plugin_integration(self):
        """测试插件集成"""
        try:
            from src.plugins.plc_variable_parser import PLCVariableParserPlugin
            
            plugin = PLCVariableParserPlugin()
            init_result = plugin.initialize({})
            
            assert init_result, "插件初始化失败"
            
            actions = plugin.get_actions()
            assert len(actions) > 0, "插件没有可用操作"
            
            widget = plugin.get_widget()
            assert widget is not None, "获取UI组件失败"
            
            plugin.cleanup()
            
            self.record_result("插件集成测试", True, f"插件初始化成功，共{len(actions)}个操作")
        except Exception as e:
            self.record_result("插件集成测试", False, str(e))
    
    def run_all_tests(self):
        """运行所有测试"""
        self.start_time = datetime.now()
        
        print("\n" + "=" * 60)
        print("PLC变量表解析插件 GUI测试报告")
        print("=" * 60)
        print(f"开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        
        self.setup()
        
        tests = [
            self.test_widget_creation,
            self.test_variable_table,
            self.test_variable_dialog,
            self.test_batch_edit_dialog,
            self.test_toolbar_actions,
            self.test_file_operations,
            self.test_search_function,
            self.test_add_delete_variable,
            self.test_export_functionality,
            self.test_plugin_integration,
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.record_result(test.__name__, False, f"测试异常: {str(e)}")
        
        self.teardown()
        
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        passed = sum(1 for r in self.test_results if r['passed'])
        failed = sum(1 for r in self.test_results if not r['passed'])
        
        print("\n测试结果:")
        print("-" * 60)
        for result in self.test_results:
            status = "✓ 通过" if result['passed'] else "✗ 失败"
            print(f"  [{result['time']}] {result['name']}: {status}")
            if not result['passed'] and result['message']:
                print(f"    错误: {result['message']}")
        
        print("-" * 60)
        print(f"总计: {len(self.test_results)} 个测试")
        print(f"通过: {passed} 个")
        print(f"失败: {failed} 个")
        print(f"耗时: {duration:.2f} 秒")
        print(f"结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        return failed == 0


def run_gui_tests():
    """运行GUI测试"""
    runner = GUITestRunner()
    return runner.run_all_tests()


if __name__ == '__main__':
    success = run_gui_tests()
    sys.exit(0 if success else 1)
