import pytest
from unittest import mock
from ui.main_window import MainWindow

class TestMainWindow:
    """测试主窗口类"""

    def test_init(self, root):
        """测试主窗口初始化"""
        window = MainWindow(root)
        assert window.root == root
        assert window.title == "PLC变量表解析工具"
        assert window.variables == []
        assert window.parser_factory is not None
        assert window.exporter is not None

    def test_create_menu(self, root):
        """测试菜单创建"""
        window = MainWindow(root)
        # 验证菜单是否创建成功
        assert root.cget('menu') is not None

    def test_create_toolbar(self, root):
        """测试工具栏创建"""
        window = MainWindow(root)
        # 验证工具栏是否创建成功
        # 这里可以通过检查窗口的子组件来验证

    def test_create_variable_table(self, root):
        """测试变量表格创建"""
        window = MainWindow(root)
        assert window.variable_table is not None

    def test_open_file(self, root, mock_filedialog, mock_messagebox):
        """测试文件打开功能"""
        window = MainWindow(root)
        
        # 模拟文件选择
        mock_filedialog['askopenfilename'].return_value = 'test.csv'
        
        # 模拟PLC格式选择对话框
        with mock.patch('tkinter.Toplevel') as mock_toplevel:
            # 模拟对话框的行为
            mock_window = mock.MagicMock()
            mock_toplevel.return_value = mock_window
            
            # 模拟变量和方法
            mock_window.transient = mock.MagicMock()
            mock_window.grab_set = mock.MagicMock()
            mock_window.destroy = mock.MagicMock()
            
            # 模拟StringVar
            mock_var = mock.MagicMock()
            mock_var.get.return_value = 'autoshop'
            with mock.patch('tkinter.StringVar', return_value=mock_var):
                # 模拟wait_window
                root.wait_window = mock.MagicMock()
                
                # 模拟文件读取
                with mock.patch('builtins.open', mock.mock_open(read_data='类别,名称,数据类型,注释\nGLOBAL,VAR1,BOOL,测试变量1')):
                    # 模拟编码检测
                    with mock.patch('utils.encoding_detector.EncodingDetector.detect_encoding', return_value='utf-8'):
                        # 模拟解析器
                        with mock.patch('parser.parser_factory.ParserFactory.create_parser') as mock_create_parser:
                            mock_parser = mock.MagicMock()
                            mock_parser.parse.return_value = [{'name': 'VAR1', 'type': 'BOOL', 'scope': 'GLOBAL', 'description': '测试变量1'}]
                            mock_create_parser.return_value = mock_parser
                            
                            # 执行打开文件操作
                            window.open_file()
                            
                            # 验证结果
                            assert len(window.variables) == 1
                            assert window.variables[0]['name'] == 'VAR1'
                            mock_messagebox['showinfo'].assert_called_once()

    def test_export_file(self, root, mock_filedialog, mock_messagebox, test_variables):
        """测试文件导出功能"""
        window = MainWindow(root)
        window.variables = test_variables
        
        # 模拟文件保存
        mock_filedialog['asksaveasfilename'].return_value = 'output.csv'
        
        # 模拟导出格式选择对话框
        with mock.patch('tkinter.Toplevel') as mock_toplevel:
            # 模拟对话框的行为
            mock_window = mock.MagicMock()
            mock_toplevel.return_value = mock_window
            
            # 模拟变量和方法
            mock_window.transient = mock.MagicMock()
            mock_window.grab_set = mock.MagicMock()
            mock_window.destroy = mock.MagicMock()
            
            # 模拟StringVar
            mock_var = mock.MagicMock()
            mock_var.get.return_value = 'csv'
            with mock.patch('tkinter.StringVar', return_value=mock_var):
                # 模拟wait_window
                root.wait_window = mock.MagicMock()
                
                # 模拟导出器
                with mock.patch('exporter.exporter.Exporter.export_to_format', return_value=True):
                    # 执行导出文件操作
                    window.export_file()
                    
                    # 验证结果
                    mock_messagebox['showinfo'].assert_called_once()

    def test_add_variable(self, root, mock_messagebox):
        """测试添加变量功能"""
        window = MainWindow(root)
        
        # 模拟变量对话框
        with mock.patch('ui.variable_dialog.VariableDialog') as mock_dialog:
            mock_instance = mock.MagicMock()
            mock_instance.show.return_value = {'name': 'NEW_VAR', 'type': 'BOOL', 'scope': 'GLOBAL', 'description': '新变量'}
            mock_dialog.return_value = mock_instance
            
            # 执行添加变量操作
            window.add_variable()
            
            # 验证结果
            assert len(window.variables) == 1
            assert window.variables[0]['name'] == 'NEW_VAR'

    def test_edit_variable(self, root, mock_messagebox, test_variables):
        """测试编辑变量功能"""
        window = MainWindow(root)
        window.variables = test_variables
        
        # 模拟变量表格的选择
        with mock.patch.object(window.variable_table, 'get_selected_index', return_value=0):
            # 模拟变量对话框
            with mock.patch('ui.variable_dialog.VariableDialog') as mock_dialog:
                mock_instance = mock.MagicMock()
                mock_instance.show.return_value = {'name': 'EDITED_VAR', 'type': 'INT', 'scope': 'LOCAL', 'description': '编辑后的变量'}
                mock_dialog.return_value = mock_instance
                
                # 执行编辑变量操作
                window.edit_variable()
                
                # 验证结果
                assert window.variables[0]['name'] == 'EDITED_VAR'

    def test_delete_variable(self, root, mock_messagebox, test_variables):
        """测试删除变量功能"""
        window = MainWindow(root)
        window.variables = test_variables
        
        # 模拟变量表格的选择
        with mock.patch.object(window.variable_table, 'get_selected_index', return_value=0):
            # 模拟确认对话框
            mock_messagebox['askyesno'].return_value = True
            
            # 执行删除变量操作
            window.delete_variable()
            
            # 验证结果
            assert len(window.variables) == 1
            assert window.variables[0]['name'] == 'VAR2'

    def test_batch_edit_variables(self, root, mock_messagebox, test_variables):
        """测试批量编辑变量功能"""
        window = MainWindow(root)
        window.variables = test_variables
        
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

    def test_show_about(self, root, mock_messagebox):
        """测试关于对话框功能"""
        window = MainWindow(root)
        
        # 执行显示关于对话框操作
        window.show_about()
        
        # 验证结果
        mock_messagebox['showinfo'].assert_called_once()

    def test_create_empty_file(self, root, mock_filedialog, mock_messagebox):
        """测试创建空文件功能"""
        window = MainWindow(root)
        
        # 模拟文件选择
        mock_filedialog['askopenfilename'].return_value = 'source.csv'
        mock_filedialog['asksaveasfilename'].return_value = 'empty.csv'
        
        # 模拟导出器
        with mock.patch('exporter.exporter.Exporter.create_empty_file', return_value=True):
            # 执行创建空文件操作
            window.create_empty_file()
            
            # 验证结果
            mock_messagebox['showinfo'].assert_called_once()

    def test_convert_file(self, root, mock_filedialog, mock_messagebox):
        """测试文件转换功能"""
        window = MainWindow(root)
        
        # 模拟文件选择
        mock_filedialog['askopenfilename'].side_effect = ['source.csv', 'target.csv']
        mock_filedialog['asksaveasfilename'].return_value = 'converted.csv'
        
        # 模拟导出器
        with mock.patch('exporter.exporter.Exporter.convert_file', return_value=True):
            # 执行文件转换操作
            window.convert_file()
            
            # 验证结果
            mock_messagebox['showinfo'].assert_called_once()
