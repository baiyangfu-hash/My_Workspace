# -*- coding: utf-8 -*-
"""
测试变更文档生成功能
"""
import os
import sys
import unittest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from src.services.change_service import ChangeService
from src.services.project_service import ProjectService

class TestChangeDocumentGeneration(unittest.TestCase):
    """测试变更文档生成功能"""
    
    def setUp(self):
        """设置测试环境"""
        print("\n=== 开始测试变更文档生成功能 ===")
        # 创建测试项目
        self.project_id = "test-project-001"
        project_data = {
            "code": "TEST-2026-001",
            "name": "测试项目",
            "description": "用于测试变更文档生成功能的项目",
            "path": os.path.join(os.path.dirname(__file__), "test_project"),
            "status": "active",
            "created_by": "test"
        }
        
        # 确保测试目录存在
        os.makedirs(project_data["path"], exist_ok=True)
        
        # 创建项目
        self.project = ProjectService.create_project(project_data)
        print(f"创建测试项目: {self.project.code} - {self.project.name}")
    
    def tearDown(self):
        """清理测试环境"""
        print("\n=== 测试完成 ===")
    
    def test_create_change_with_auto_export(self):
        """测试创建变更单时自动导出文档"""
        print("\n1. 测试创建变更单时自动导出文档")
        
        # 创建变更单
        change, error = ChangeService.create_change(
            project_id=self.project.project_id,
            title="测试变更单",
            type="功能变更",
            description="这是一个测试变更单",
            reason="测试需要",
            impact="测试模块",
            proposer="测试用户"
        )
        
        self.assertIsNotNone(change, f"创建变更单失败: {error}")
        print(f"创建变更单成功: {change.change_id}")
        
        # 检查变更单文件是否生成
        change_file_path = os.path.join(
            self.project.path,
            "05_变更管理",
            "01_变更单",
            f"{change.change_id}.md"
        )
        
        print(f"检查变更单文件: {change_file_path}")
        self.assertTrue(os.path.exists(change_file_path), "变更单文件未生成")
        print("变更单文件生成成功")
        
        # 检查文件内容
        with open(change_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn(change.title, content, "变更单标题未包含在文件中")
        self.assertIn(change.change_id, content, "变更单ID未包含在文件中")
        print("变更单文件内容验证成功")
    
    def test_generate_ledger(self):
        """测试生成变更台帐"""
        print("\n2. 测试生成变更台帐")
        
        # 先创建一个变更单
        change, error = ChangeService.create_change(
            project_id=self.project.project_id,
            title="测试变更单2",
            type="Bug修复",
            description="这是第二个测试变更单",
            reason="测试需要",
            impact="测试模块2",
            proposer="测试用户"
        )
        
        self.assertIsNotNone(change, f"创建变更单失败: {error}")
        print(f"创建变更单成功: {change.change_id}")
        
        # 生成变更台帐
        ledger_path, error = ChangeService.generate_ledger(self.project.project_id)
        
        self.assertIsNotNone(ledger_path, f"生成变更台帐失败: {error}")
        print(f"生成变更台帐成功: {ledger_path}")
        
        # 检查变更台帐文件是否生成
        self.assertTrue(os.path.exists(ledger_path), "变更台帐文件未生成")
        print("变更台帐文件生成成功")
        
        # 检查文件内容
        with open(ledger_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn(self.project.name, content, "项目名称未包含在台帐中")
        self.assertIn(change.change_id, content, "变更单ID未包含在台帐中")
        print("变更台帐文件内容验证成功")
    
    def test_update_ledger(self):
        """测试更新变更台帐"""
        print("\n3. 测试更新变更台帐")
        
        # 生成初始台帐
        ledger_path, error = ChangeService.generate_ledger(self.project.project_id)
        self.assertIsNotNone(ledger_path, f"生成变更台帐失败: {error}")
        print(f"生成初始变更台帐成功: {ledger_path}")
        
        # 创建新的变更单
        change, error = ChangeService.create_change(
            project_id=self.project.project_id,
            title="测试变更单3",
            type="性能优化",
            description="这是第三个测试变更单",
            reason="测试需要",
            impact="测试模块3",
            proposer="测试用户"
        )
        
        self.assertIsNotNone(change, f"创建变更单失败: {error}")
        print(f"创建新变更单成功: {change.change_id}")
        
        # 更新变更台帐
        updated_ledger_path, error = ChangeService.update_ledger(self.project.project_id)
        self.assertIsNotNone(updated_ledger_path, f"更新变更台帐失败: {error}")
        print(f"更新变更台帐成功: {updated_ledger_path}")
        
        # 检查更新后的台帐内容
        with open(updated_ledger_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn(change.change_id, content, "新变更单ID未包含在更新后的台帐中")
        print("变更台帐更新验证成功")

if __name__ == '__main__':
    unittest.main()