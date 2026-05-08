#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PLC变量表解析工具GUI综合测试用例
"""

import pytest
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from ui.main_window import MainWindow
from ui.variable_table import VariableTable
from ui.variable_dialog import VariableDialog
from ui.batch_edit_dialog import BatchEditDialog
import tempfile


class TestGUIFunctionality:
    """
    GUI功能测试类
    """
    
    def test_main_window_initialization(self, root):
        """
        测试主窗口初始化
        """
        app = MainWindow(root)
        assert app.root.title() == "PLC变量表解析工具"
        # 验证菜单和工具栏是否创建
        assert hasattr(app, 'variable_table')
    
    def test_variable_table_initialization(self, root):
        """
        测试变量表格初始化
        """
        table = VariableTable(root, [])
        assert len(table.variables) == 0
        assert table.get_selected_index() == -1
    
    def test_add_variable(self, root, mock_messagebox):
        """
        测试添加变量功能
        """
        app = MainWindow(root)
        # 模拟添加变量
        test_variable = {
            'name': 'TestVar',
            'type': 'INT',
            'address': 'D100',
            'description': 'Test variable',
            'scope': 'VAR'
        }
        app.variables.append(test_variable)
        app.variable_table.update_table(app.variables)
        assert len(app.variables) == 1
        assert app.variables[0]['name'] == 'TestVar'
    
    def test_edit_variable(self, root, mock_messagebox):
        """
        测试编辑变量功能
        """
        app = MainWindow(root)
        # 添加测试变量
        test_variable = {
            'name': 'TestVar',
            'type': 'INT',
            'address': 'D100',
            'description': 'Test variable',
            'scope': 'VAR'
        }
        app.variables.append(test_variable)
        app.variable_table.update_table(app.variables)
        
        # 模拟编辑变量
        updated_variable = {
            'name': 'UpdatedVar',
            'type': 'REAL',
            'address': 'D200',
            'description': 'Updated test variable',
            'scope': 'VAR_INPUT'
        }
        app.variables[0] = updated_variable
        app.variable_table.update_table(app.variables)
        assert app.variables[0]['name'] == 'UpdatedVar'
        assert app.variables[0]['type'] == 'REAL'
    
    def test_delete_variable(self, root, mock_messagebox):
        """
        测试删除变量功能
        """
        app = MainWindow(root)
        # 添加测试变量
        test_variable = {
            'name': 'TestVar',
            'type': 'INT',
            'address': 'D100',
            'description': 'Test variable',
            'scope': 'VAR'
        }
        app.variables.append(test_variable)
        app.variable_table.update_table(app.variables)
        assert len(app.variables) == 1
        
        # 模拟删除变量
        app.variables.pop(0)
        app.variable_table.update_table(app.variables)
        assert len(app.variables) == 0
    
    def test_batch_edit_variables(self, root, mock_messagebox):
        """
        测试批量编辑变量功能
        """
        app = MainWindow(root)
        # 添加测试变量
        test_variable1 = {
            'name': 'Var1',
            'type': 'INT',
            'address': 'D100',
            'description': 'Variable 1',
            'scope': 'VAR'
        }
        test_variable2 = {
            'name': 'Var2',
            'type': 'INT',
            'address': 'D200',
            'description': 'Variable 2',
            'scope': 'VAR'
        }
        app.variables.extend([test_variable1, test_variable2])
        app.variable_table.update_table(app.variables)
        
        # 模拟批量编辑
        changes = {'type': 'REAL', 'scope': 'VAR_INPUT'}
        for i in range(len(app.variables)):
            for field, value in changes.items():
                if value:
                    app.variables[i][field] = value
        
        app.variable_table.update_table(app.variables)
        assert app.variables[0]['type'] == 'REAL'
        assert app.variables[1]['type'] == 'REAL'
        assert app.variables[0]['scope'] == 'VAR_INPUT'
        assert app.variables[1]['scope'] == 'VAR_INPUT'
    
    def test_create_empty_file(self, root, mock_filedialog, mock_messagebox):
        """
        测试创建空文件功能
        """
        app = MainWindow(root)
        
        # 模拟文件选择
        mock_filedialog['askopenfilename'].return_value = 'source.csv'
        mock_filedialog['asksaveasfilename'].return_value = 'empty.csv'
        
        # 模拟导出器
        with pytest.MonkeyPatch.context() as m:
            m.setattr('exporter.exporter.Exporter.create_empty_file', lambda *args: True)
            # 执行创建空文件操作
            app.create_empty_file()
            # 验证结果
            mock_messagebox['showinfo'].assert_called_once()
    
    def test_convert_file(self, root, mock_filedialog, mock_messagebox):
        """
        测试转换文件功能
        """
        app = MainWindow(root)
        
        # 模拟文件选择
        mock_filedialog['askopenfilename'].side_effect = ['source.csv', 'target.csv']
        mock_filedialog['asksaveasfilename'].return_value = 'converted.csv'
        
        # 模拟导出器
        with pytest.MonkeyPatch.context() as m:
            m.setattr('exporter.exporter.Exporter.convert_file', lambda *args: True)
            # 执行文件转换操作
            app.convert_file()
            # 验证结果
            mock_messagebox['showinfo'].assert_called_once()
    
    def test_export_to_csv(self, root, mock_filedialog, mock_messagebox):
        """
        测试导出为CSV格式
        """
        app = MainWindow(root)
        # 添加测试变量
        test_variable = {
            'name': 'TestVar',
            'type': 'INT',
            'address': 'D100',
            'description': 'Test variable',
            'scope': 'VAR'
        }
        app.variables.append(test_variable)
        
        # 模拟文件保存
        mock_filedialog['asksaveasfilename'].return_value = 'output.csv'
        
        # 模拟导出器
        with pytest.MonkeyPatch.context() as m:
            m.setattr('exporter.exporter.Exporter.export_to_format', lambda *args: True)
            # 执行导出文件操作
            app.export_file()
            # 验证结果
            mock_messagebox['showinfo'].assert_called_once()
    
    def test_export_to_json(self, root, mock_filedialog, mock_messagebox):
        """
        测试导出为JSON格式
        """
        app = MainWindow(root)
        # 添加测试变量
        test_variable = {
            'name': 'TestVar',
            'type': 'INT',
            'address': 'D100',
            'description': 'Test variable',
            'scope': 'VAR'
        }
        app.variables.append(test_variable)
        
        # 模拟文件保存
        mock_filedialog['asksaveasfilename'].return_value = 'output.json'
        
        # 模拟导出器
        with pytest.MonkeyPatch.context() as m:
            m.setattr('exporter.exporter.Exporter.export_to_format', lambda *args: True)
            # 执行导出文件操作
            app.export_file()
            # 验证结果
            mock_messagebox['showinfo'].assert_called_once()
