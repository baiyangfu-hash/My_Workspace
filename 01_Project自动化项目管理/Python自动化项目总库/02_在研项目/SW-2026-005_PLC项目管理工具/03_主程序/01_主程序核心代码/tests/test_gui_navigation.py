# -*- coding: utf-8 -*-
"""
GUI导航映射回归测试

验证方案B结构重构后的导航一致性：
- 左侧ToolBox页面与顶部TabWidget一一对应
- 变更管理Tab正确映射到独立的变更管理ToolBox页面
- HMI工具页面已移除，不再造成冲突
"""
import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PyQt5.QtWidgets import QToolBox, QTabWidget, QApplication
from src.ui.builders.left_panel_builder import LeftPanelBuilder
from src.ui.controllers.navigation_controller import NavigationController


class TestGUINavigationMapping(unittest.TestCase):
    """GUI导航映射完整性测试"""

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)

    def test_001_toolbox_page_count(self):
        """TC-GUI-007: 验证ToolBox页面数量为6"""
        mock_handler = Mock()
        tool_box = LeftPanelBuilder.build(None, mock_handler)
        
        self.assertEqual(
            tool_box.count(), 6,
            f"ToolBox应该有6个页面，实际有{tool_box.count()}个"
        )
        
        expected_pages = [
            "项目管理",
            "文档管理", 
            "PLC工具",
            "变更管理",
            "规范中心",
            "系统设置",
        ]
        
        for i, expected_name in enumerate(expected_pages):
            actual_name = tool_box.itemText(i)
            self.assertIn(
                expected_name, actual_name,
                f"页面{i}名称应该包含'{expected_name}'，实际是'{actual_name}'"
            )

    def test_002_change_mgmt_tab_maps_to_correct_toolbox(self):
        """TC-GUI-001: 验证变更管理Tab(3)映射到变更管理ToolBox页面(2)"""
        tab_idx = NavigationController.TAB_CHANGE_MGMT
        expected_toolbox_idx = NavigationController.TOOL_CHANGE_MGMT
        
        actual_toolbox_idx = NavigationController.TAB_TO_TOOLBOX.get(tab_idx)
        
        self.assertEqual(
            actual_toolbox_idx, expected_toolbox_idx,
            f"TAB_CHANGE_MGMT({tab_idx})应该映射到TOOL_CHANGE_MGMT({expected_toolbox_idx})，"
            f"实际映射到{actual_toolbox_idx}"
        )
        
        self.assertNotEqual(
            actual_toolbox_idx, NavigationController.TOOL_SPEC,
            "变更管理Tab不应该映射到规范中心(TOOL_SPEC)"
        )

    def test_003_change_mgmt_toolbox_maps_to_correct_tab(self):
        """验证变更管理ToolBox页面(2)映射到变更管理Tab(3)"""
        toolbox_idx = NavigationController.TOOL_CHANGE_MGMT
        expected_tab_idx = NavigationController.TAB_CHANGE_MGMT
        
        actual_tab_idx = NavigationController.TOOLBOX_TO_TAB.get(toolbox_idx)
        
        self.assertEqual(
            actual_tab_idx, expected_tab_idx,
            f"TOOL_CHANGE_MGMT({toolbox_idx})应该映射到TAB_CHANGE_MGMT({expected_tab_idx})，"
            f"实际映射到{actual_tab_idx}"
        )

    def test_004_no_hmi_tool_mapping_conflict(self):
        """TC-GUI-002: 验证HMI工具不再造成映射冲突"""
        self.assertFalse(
            hasattr(NavigationController, 'TOOL_HMI'),
            "NavigationController不应该再有TOOL_HMI常量"
        )
        
        for toolbox_idx, tab_idx in NavigationController.TOOLBOX_TO_TAB.items():
            if tab_idx == NavigationController.TAB_SPEC_CHECK:
                self.assertEqual(
                    toolbox_idx, NavigationController.TOOL_SPEC,
                    f"只有TOOL_SPEC应该映射到TAB_SPEC_CHECK，"
                    f"但TOOL_{toolbox_idx}也映射到了TAB_SPEC_CHECK"
                )

    def test_005_bidirectional_mapping_consistency(self):
        """TC-GUI-003: 验证正向映射可被反向映射覆盖（允许多对一共享）"""
        for tab_idx, toolbox_idx in NavigationController.TAB_TO_TOOLBOX.items():
            if toolbox_idx is None:
                continue
            
            reverse_tab_idx = NavigationController.TOOLBOX_TO_TAB.get(toolbox_idx)
            
            self.assertIsNotNone(
                reverse_tab_idx,
                f"TOOL_{toolbox_idx}应该有反向映射到某个Tab"
            )
            
            forward_check = NavigationController.TAB_TO_TOOLBOX.get(reverse_tab_idx)
            
            self.assertEqual(
                forward_check, toolbox_idx,
                f"反向链不一致: TAB_{tab_idx}→TOOL_{toolbox_idx}→TAB_{reverse_tab_idx}→TOOL_{forward_check}"
            )

    def test_006_all_tabs_have_valid_mapping(self):
        """TC-GUI-004: 验证所有Tab都有有效的ToolBox映射"""
        expected_mappings = {
            NavigationController.TAB_DASHBOARD: NavigationController.TOOL_PROJECT,
            NavigationController.TAB_PROJECT: NavigationController.TOOL_PROJECT,
            NavigationController.TAB_DOCUMENT: NavigationController.TOOL_DOCUMENT,
            NavigationController.TAB_CHANGE_MGMT: NavigationController.TOOL_CHANGE_MGMT,
            NavigationController.TAB_PLC_TOOLS: NavigationController.TOOL_PLC,
            NavigationController.TAB_SPEC_CHECK: NavigationController.TOOL_SPEC,
        }
        
        for tab_idx, expected_toolbox in expected_mappings.items():
            actual_toolbox = NavigationController.TAB_TO_TOOLBOX.get(tab_idx)
            
            self.assertEqual(
                actual_toolbox, expected_toolbox,
                f"Tab {tab_idx} 映射错误: 期望TOOL_{expected_toolbox}，实际TOOL_{actual_toolbox}"
            )

    def test_007_change_mgmt_page_exists_in_toolbox(self):
        """TC-GUI-005: 验证ToolBox中存在独立的变更管理页面"""
        mock_handler = Mock()
        tool_box = LeftPanelBuilder.build(None, mock_handler)
        
        change_mgmt_found = False
        for i in range(tool_box.count()):
            if "变更管理" in tool_box.itemText(i):
                change_mgmt_found = True
                
                page_widget = tool_box.widget(i)
                self.assertIsNotNone(
                    page_widget,
                    f"变更管理页面({i})的widget不应为None"
                )
                
                children = page_widget.findChildren(type(page_widget).__subclasses__()[0]) if page_widget.children() else []
                
                break
        
        self.assertTrue(
            change_mgmt_found,
            "ToolBox中应该存在'变更管理'页面"
        )

    def test_008_spec_center_page_without_change_mgmt_button(self):
        """验证规范中心页面不再包含变更管理按钮"""
        mock_handler = Mock()
        tool_box = LeftPanelBuilder.build(None, mock_handler)
        
        spec_center_idx = None
        for i in range(tool_box.count()):
            if "规范中心" in tool_box.itemText(i):
                spec_center_idx = i
                break
        
        self.assertIsNotNone(
            spec_center_idx,
            "应该找到规范中心页面"
        )
        
        spec_page = tool_box.widget(spec_center_idx)
        layout = spec_page.layout()
        
        if layout:
            for i in range(layout.count()):
                item = layout.itemAt(i)
                widget = item.widget()
                if widget and hasattr(widget, 'text'):
                    button_text = widget.text()
                    self.assertNotIn(
                        "变更管理", button_text,
                        f"规范中心页面不应包含'变更管理'按钮，发现: '{button_text}'"
                    )

    def test_009_left_panel_builder_constants_match_controller(self):
        """验证LeftPanelBuilder和NavigationController的常量一致"""
        self.assertEqual(
            LeftPanelBuilder.TOOL_PROJECT, NavigationController.TOOL_PROJECT,
            "TOOL_PROJECT常量不一致"
        )
        self.assertEqual(
            LeftPanelBuilder.TOOL_DOCUMENT, NavigationController.TOOL_DOCUMENT,
            "TOOL_DOCUMENT常量不一致"
        )
        self.assertEqual(
            LeftPanelBuilder.TOOL_CHANGE_MGMT, NavigationController.TOOL_CHANGE_MGMT,
            "TOOL_CHANGE_MGMT常量不一致"
        )
        self.assertEqual(
            LeftPanelBuilder.TOOL_PLC, NavigationController.TOOL_PLC,
            "TOOL_PLC常量不一致"
        )
        self.assertEqual(
            LeftPanelBuilder.TOOL_SPEC, NavigationController.TOOL_SPEC,
            "TOOL_SPEC常量不一致"
        )
        self.assertEqual(
            LeftPanelBuilder.TOOL_SETTINGS, NavigationController.TOOL_SETTINGS,
            "TOOL_SETTINGS常量不一致"
        )


class TestNavigationControllerIntegration(unittest.TestCase):
    """NavigationController集成测试"""

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)

    def setUp(self):
        self.tool_box = QToolBox()
        self.tab_widget = QTabWidget()
        
        from PyQt5.QtWidgets import QWidget
        for i in range(6):
            self.tab_widget.addTab(QWidget(), f"Tab-{i}")
        
        self.nav_ctrl = NavigationController(
            self.tool_box, 
            self.tab_widget,
            sync_handler=Mock(),
            project_info_handler=Mock()
        )
        self.nav_ctrl.connect()

    def tearDown(self):
        self.tool_box.deleteLater()
        self.tab_widget.deleteLater()

    def test_tab_change_updates_toolbox(self):
        """测试Tab切换时ToolBox同步更新"""
        from PyQt5.QtWidgets import QWidget
        for i in range(6):
            self.tool_box.addItem(QWidget(), f"Page-{i}")
        
        self.tab_widget.setCurrentIndex(NavigationController.TAB_CHANGE_MGMT)
        
        expected_toolbox_idx = NavigationController.TOOL_CHANGE_MGMT
        actual_toolbox_idx = self.tool_box.currentIndex()
        
        self.assertEqual(
            actual_toolbox_idx, expected_toolbox_idx,
            f"切换到变更管理Tab后，ToolBox应该切换到页面{expected_toolbox_idx}，"
            f"实际在页面{actual_toolbox_idx}"
        )

    def test_toolbox_change_updates_tab(self):
        """测试ToolBox切换时Tab同步更新"""
        from PyQt5.QtWidgets import QWidget
        for i in range(6):
            self.tool_box.addItem(QWidget(), f"Page-{i}")
        
        self.tool_box.setCurrentIndex(NavigationController.TOOL_CHANGE_MGMT)
        
        expected_tab_idx = NavigationController.TAB_CHANGE_MGMT
        actual_tab_idx = self.tab_widget.currentIndex()
        
        self.assertEqual(
            actual_tab_idx, expected_tab_idx,
            f"切换到变更管理ToolBox页面后，Tab应该切换到{expected_tab_idx}，"
            f"实际在{actual_tab_idx}"
        )

    def test_navigate_to_change_mgmt(self):
        """测试navigate_to_tab方法对变更管理的处理"""
        from PyQt5.QtWidgets import QWidget
        for i in range(6):
            self.tool_box.addItem(QWidget(), f"Page-{i}")
        
        self.nav_ctrl.navigate_to_tab(NavigationController.TAB_CHANGE_MGMT)
        
        self.assertEqual(
            self.tab_widget.currentIndex(), NavigationController.TAB_CHANGE_MGMT,
            "navigate_to_tab应该切换Tab到变更管理"
        )
        self.assertEqual(
            self.tool_box.currentIndex(), NavigationController.TOOL_CHANGE_MGMT,
            "navigate_to_tab应该切换ToolBox到变更管理页面"
        )


if __name__ == '__main__':
    unittest.main(verbosity=2)
