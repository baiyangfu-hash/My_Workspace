import pytest
from unittest import mock
from ui.main_window import MainWindow

class TestGUIIntegration:
    """测试GUI集成功能"""

    def test_full_workflow(self, root, mock_filedialog, mock_messagebox):
        """测试完整的文件打开-编辑-导出流程"""
        window = MainWindow(root)
        
        # 1. 测试打开文件
        mock_filedialog['askopenfilename'].return_value = 'test.csv'
        
        # 模拟PLC格式选择对话框
        with mock.patch('tkinter.Toplevel') as mock_toplevel:
            mock_window = mock.MagicMock()
            mock_toplevel.return_value = mock_window
            mock_window.transient = mock.MagicMock()
            mock_window.grab_set = mock.MagicMock()
            mock_window.destroy = mock.MagicMock()
            
            mock_var = mock.MagicMock()
            mock_var.get.return_value = 'autoshop'
            with mock.patch('tkinter.StringVar', return_value=mock_var):
                root.wait_window = mock.MagicMock()
                
                with mock.patch('builtins.open', mock.mock_open(read_data='类别,名称,数据类型,注释\nGLOBAL,VAR1,BOOL,测试变量1')):
                    with mock.patch('utils.encoding_detector.EncodingDetector.detect_encoding', return_value='utf-8'):
                        with mock.patch('parser.parser_factory.ParserFactory.create_parser') as mock_create_parser:
                            mock_parser = mock.MagicMock()
                            mock_parser.parse.return_value = [{'name': 'VAR1', 'type': 'BOOL', 'scope': 'GLOBAL', 'description': '测试变量1'}]
                            mock_create_parser.return_value = mock_parser
                            
                            window.open_file()
                            assert len(window.variables) == 1
        
        # 2. 测试添加变量
        with mock.patch('ui.variable_dialog.VariableDialog') as mock_dialog:
            mock_instance = mock.MagicMock()
            mock_instance.show.return_value = {'name': 'VAR2', 'type': 'INT', 'scope': 'LOCAL', 'description': '测试变量2'}
            mock_dialog.return_value = mock_instance
            
            window.add_variable()
            assert len(window.variables) == 2
        
        # 3. 测试编辑变量
        with mock.patch.object(window.variable_table, 'get_selected_index', return_value=0):
            with mock.patch('ui.variable_dialog.VariableDialog') as mock_dialog:
                mock_instance = mock.MagicMock()
                mock_instance.show.return_value = {'name': 'EDITED_VAR', 'type': 'BOOL', 'scope': 'GLOBAL', 'description': '编辑后的变量'}
                mock_dialog.return_value = mock_instance
                
                window.edit_variable()
                assert window.variables[0]['name'] == 'EDITED_VAR'
        
        # 4. 测试导出文件
        mock_filedialog['asksaveasfilename'].return_value = 'output.csv'
        
        # 模拟导出格式选择对话框
        with mock.patch('tkinter.Toplevel') as mock_toplevel:
            mock_window = mock.MagicMock()
            mock_toplevel.return_value = mock_window
            mock_window.transient = mock.MagicMock()
            mock_window.grab_set = mock.MagicMock()
            mock_window.destroy = mock.MagicMock()
            
            mock_var = mock.MagicMock()
            mock_var.get.return_value = 'csv'
            with mock.patch('tkinter.StringVar', return_value=mock_var):
                root.wait_window = mock.MagicMock()
                
                with mock.patch('exporter.exporter.Exporter.export_to_format', return_value=True):
                    window.export_file()
                    mock_messagebox['showinfo'].assert_called()

    def test_batch_edit_workflow(self, root, mock_messagebox):
        """测试批量编辑功能的完整流程"""
        window = MainWindow(root)
        window.variables = [
            {'name': 'VAR1', 'type': 'BOOL', 'scope': 'GLOBAL', 'description': '测试变量1'},
            {'name': 'VAR2', 'type': 'INT', 'scope': 'LOCAL', 'description': '测试变量2'}
        ]
        
        # 模拟变量表格的选择
        with mock.patch.object(window.variable_table, 'get_selected_indices', return_value=[0, 1]):
            # 模拟批量编辑对话框
            with mock.patch('ui.batch_edit_dialog.BatchEditDialog') as mock_dialog:
                mock_instance = mock.MagicMock()
                mock_instance.show.return_value = {'type': 'BOOL'}
                mock_dialog.return_value = mock_instance
                
                # 执行批量编辑操作
                window.batch_edit_variables()
                
                # 验证结果
                assert window.variables[0]['type'] == 'BOOL'
                assert window.variables[1]['type'] == 'BOOL'
                mock_messagebox['showinfo'].assert_called_once()

    def test_error_handling(self, root, mock_filedialog, mock_messagebox):
        """测试异常情况的处理"""
        window = MainWindow(root)
        
        # 测试打开不存在的文件
        mock_filedialog['askopenfilename'].return_value = 'nonexistent.csv'
        
        # 模拟PLC格式选择对话框
        with mock.patch('tkinter.Toplevel') as mock_toplevel:
            mock_window = mock.MagicMock()
            mock_toplevel.return_value = mock_window
            mock_window.transient = mock.MagicMock()
            mock_window.grab_set = mock.MagicMock()
            mock_window.destroy = mock.MagicMock()
            
            mock_var = mock.MagicMock()
            mock_var.get.return_value = 'autoshop'
            with mock.patch('tkinter.StringVar', return_value=mock_var):
                root.wait_window = mock.MagicMock()
                
                # 模拟文件读取失败
                with mock.patch('builtins.open', side_effect=FileNotFoundError):
                    with mock.patch('utils.encoding_detector.EncodingDetector.detect_encoding', return_value='utf-8'):
                        with mock.patch('parser.parser_factory.ParserFactory.create_parser') as mock_create_parser:
                            mock_parser = mock.MagicMock()
                            mock_parser.parse.side_effect = Exception('文件读取失败')
                            mock_create_parser.return_value = mock_parser
                            
                            window.open_file()
                            mock_messagebox['showerror'].assert_called()
