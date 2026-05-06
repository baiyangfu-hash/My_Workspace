import pytest
from ui.variable_table import VariableTable

class TestVariableTable:
    """测试变量表格类"""

    def test_init(self, root):
        """测试变量表格初始化"""
        variables = [{'name': 'VAR1', 'type': 'BOOL', 'scope': 'GLOBAL', 'description': '测试变量1'}]
        table = VariableTable(root, variables)
        assert table.root == root
        assert table.variables == variables

    def test_update_table(self, root, test_variables):
        """测试表格数据更新"""
        table = VariableTable(root, [])
        assert len(table.variables) == 0
        
        # 更新表格数据
        table.update_table(test_variables)
        assert table.variables == test_variables

    def test_get_selected_index(self, root, test_variables):
        """测试获取选中行索引"""
        table = VariableTable(root, test_variables)
        
        # 模拟选择第一行
        # 注意：实际测试中可能需要模拟事件
        # 这里我们假设默认情况下没有选中行
        assert table.get_selected_index() == -1

    def test_get_selected_indices(self, root, test_variables):
        """测试获取选中行索引列表"""
        table = VariableTable(root, test_variables)
        
        # 模拟选择多行
        # 注意：实际测试中可能需要模拟事件
        # 这里我们假设默认情况下没有选中行
        selected_indices = table.get_selected_indices()
        assert isinstance(selected_indices, list)
        assert len(selected_indices) == 0
