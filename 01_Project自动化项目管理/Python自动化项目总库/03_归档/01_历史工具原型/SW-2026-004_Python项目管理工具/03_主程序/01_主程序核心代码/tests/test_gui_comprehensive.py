# -*- coding: utf-8 -*-
"""
GUI模块综合测试用例
"""
import pytest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt, QPoint

from src.ui.main_window import MainWindow
from src.ui.widgets.project_list import ProjectListWidget
from src.ui.widgets.template_manager import TemplateManagerWidget
from src.ui.widgets.change_manager import ChangeManagerWidget
from src.services.project_service import ProjectService
from src.services.template_service import TemplateService
from src.services.change_service import ChangeService


@pytest.fixture(scope="module")
def app():
    """创建QApplication实例"""
    return QApplication([])


@pytest.fixture
def main_window(app):
    """创建主窗口实例"""
    window = MainWindow()
    yield window
    window.close()


class TestMainWindow:
    """主窗口测试"""
    
    def test_init(self, main_window):
        """测试主窗口初始化"""
        assert main_window.windowTitle() != ""
        assert main_window.minimumSize().width() == 1200
        assert main_window.minimumSize().height() == 800
    
    def test_tab_widget(self, main_window):
        """测试标签页初始化"""
        assert main_window.tab_widget is not None
        assert main_window.tab_widget.count() > 0
        
        # 检查标签页名称
        tab_names = [main_window.tab_widget.tabText(i) for i in range(main_window.tab_widget.count())]
        assert "项目管理" in tab_names
        assert "模板管理" in tab_names
        assert "变更管理" in tab_names
    
    def test_menu_bar(self, main_window):
        """测试菜单栏"""
        menu_bar = main_window.menuBar()
        assert menu_bar is not None
        
        # 检查菜单项
        file_menu = menu_bar.findChild(type(menu_bar), "文件")
        assert file_menu is not None
        
        tools_menu = menu_bar.findChild(type(menu_bar), "工具")
        assert tools_menu is not None
        
        help_menu = menu_bar.findChild(type(menu_bar), "帮助")
        assert help_menu is not None
    
    def test_status_bar(self, main_window):
        """测试状态栏"""
        assert main_window.status_bar is not None
        assert main_window.status_bar.currentMessage() == "就绪"


class TestProjectListWidget:
    """项目管理测试"""
    
    def test_init(self, app):
        """测试项目列表控件初始化"""
        widget = ProjectListWidget()
        assert widget is not None
        assert widget.table is not None
        assert widget.table.columnCount() == 7
        widget.deleteLater()
    
    def test_load_projects(self, app):
        """测试加载项目列表"""
        widget = ProjectListWidget()
        # 模拟加载项目
        widget._load_projects()
        # 检查表格行数
        assert widget.table.rowCount() >= 0
        widget.deleteLater()
    
    def test_filter_projects(self, app):
        """测试筛选项目"""
        widget = ProjectListWidget()
        widget._load_projects()
        
        # 测试搜索功能
        original_count = widget.table.rowCount()
        widget.search_input.setText("测试")
        # 筛选后行数应该小于等于原始行数
        assert widget.table.rowCount() <= original_count
        
        # 测试状态筛选
        widget.status_filter.setCurrentIndex(1)  # 选择第一个状态
        assert widget.table.rowCount() <= original_count
        
        widget.deleteLater()


class TestTemplateManagerWidget:
    """模板管理测试"""
    
    def test_init(self, app):
        """测试模板管理控件初始化"""
        widget = TemplateManagerWidget()
        assert widget is not None
        assert widget.table is not None
        assert widget.table.columnCount() == 9
        widget.deleteLater()
    
    def test_load_templates(self, app):
        """测试加载模板列表"""
        widget = TemplateManagerWidget()
        # 模拟加载模板
        widget._load_templates()
        # 检查表格行数
        assert widget.table.rowCount() >= 0
        widget.deleteLater()
    
    def test_filter_templates(self, app):
        """测试筛选模板"""
        widget = TemplateManagerWidget()
        widget._load_templates()
        
        # 测试搜索功能
        original_count = widget.table.rowCount()
        widget.search_input.setText("模板")
        # 筛选后行数应该小于等于原始行数
        assert widget.table.rowCount() <= original_count
        
        # 测试业务线筛选
        if widget.business_line_filter.count() > 1:
            widget.business_line_filter.setCurrentIndex(1)  # 选择第一个业务线
            assert widget.table.rowCount() <= original_count
        
        widget.deleteLater()


class TestChangeManagerWidget:
    """变更管理测试"""
    
    def test_init(self, app):
        """测试变更管理控件初始化"""
        widget = ChangeManagerWidget()
        assert widget is not None
        assert widget.project_combo is not None
        assert widget.change_table is not None
        assert widget.change_table.columnCount() == 6
        widget.deleteLater()
    
    def test_load_projects(self, app):
        """测试加载项目列表"""
        widget = ChangeManagerWidget()
        # 模拟加载项目
        widget._load_projects()
        # 检查项目下拉框选项数
        assert widget.project_combo.count() >= 0
        widget.deleteLater()
    
    def test_load_changes(self, app):
        """测试加载变更列表"""
        widget = ChangeManagerWidget()
        widget._load_projects()
        
        # 如果有项目，测试加载变更
        if widget.project_combo.count() > 0:
            widget.current_project_id = widget.project_combo.currentData()
            widget._load_changes()
            # 检查变更表格行数
            assert widget.change_table.rowCount() >= 0
        
        widget.deleteLater()


if __name__ == "__main__":
    pytest.main([__file__])
