# -*- coding: utf-8 -*-
"""
变更文档管理测试用例
"""
import unittest
import os
from unittest.mock import Mock, patch
from src.services.change_service import ChangeService
from src.core.constants import ChangeStatus

class TestChangeDocumentManagement(unittest.TestCase):
    """变更文档管理测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.project_id = "PROJ-2026-001"
        self.change_data = {
            "project_id": self.project_id,
            "title": "测试变更文档管理",
            "type": "需求变更",
            "description": "测试变更文档管理描述",
            "reason": "测试变更文档管理原因",
            "impact": "测试影响范围",
            "proposer": "测试用户"
        }
    
    def test_document_creation(self):
        """测试变更文档创建"""
        # 创建变更单
        change, error = ChangeService.create_change(**self.change_data)
        self.assertIsNotNone(change)
        self.assertEqual(error, "")
        
        # 验证变更单创建成功
        self.assertEqual(change.title, self.change_data["title"])
        self.assertEqual(change.type, self.change_data["type"])
    
    def test_document_attachment(self):
        """测试变更文档附件管理"""
        # 测试带有附件的变更
        change_data_with_attachment = self.change_data.copy()
        attachments = [
            {"name": "变更说明文档.pdf", "path": "/path/to/doc.pdf"},
            {"name": "影响分析报告.docx", "path": "/path/to/report.docx"}
        ]
        
        change, error = ChangeService.create_change(
            **change_data_with_attachment,
            attachment=attachments
        )
        self.assertIsNotNone(change)
        self.assertEqual(error, "")
        self.assertEqual(len(change.attachment), 2)
    
    def test_document_versioning(self):
        """测试变更文档版本管理"""
        # 创建变更单
        change, error = ChangeService.create_change(**self.change_data)
        self.assertIsNotNone(change)
        
        # 更新变更单（模拟版本更新）
        update_data = {
            "description": "更新后的变更描述",
            "reason": "更新后的变更原因"
        }
        updated_change, error = ChangeService.update_change(change.change_id, update_data)
        self.assertIsNotNone(updated_change)
        self.assertEqual(error, "")
        self.assertEqual(updated_change.description, "更新后的变更描述")
    
    def test_document_template_generation(self):
        """测试变更文档模板生成"""
        # 测试不同类型变更的文档模板
        change_types = ["需求变更", "设计变更", "技术变更"]
        
        for change_type in change_types:
            data = self.change_data.copy()
            data["type"] = change_type
            
            change, error = ChangeService.create_change(**data)
            self.assertIsNotNone(change)
            self.assertEqual(error, "")
            self.assertEqual(change.type, change_type)
    
    def test_document_integration_with_project(self):
        """测试文档与项目集成"""
        # 创建变更单
        change, error = ChangeService.create_change(**self.change_data)
        self.assertIsNotNone(change)
        
        # 验证变更单与项目关联
        self.assertEqual(change.project_id, self.project_id)
        
        # 测试变更流程与文档同步
        success, error = ChangeService.submit_change(change.change_id)
        self.assertTrue(success)
        
        success, error = ChangeService.approve_change(change.change_id, "审批人")
        self.assertTrue(success)

if __name__ == '__main__':
    unittest.main()
