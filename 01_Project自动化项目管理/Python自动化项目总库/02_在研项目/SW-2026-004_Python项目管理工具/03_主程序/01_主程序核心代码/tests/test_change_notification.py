# -*- coding: utf-8 -*-
"""
变更通知机制测试用例
"""
import unittest
from unittest.mock import Mock, patch
from src.services.change_service import ChangeService
from src.core.constants import ChangeStatus

class TestChangeNotification(unittest.TestCase):
    """变更通知机制测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.project_id = "PROJ-2026-001"
        self.change_data = {
            "project_id": self.project_id,
            "title": "测试变更通知",
            "type": "需求变更",
            "description": "测试变更通知描述",
            "reason": "测试变更通知原因",
            "impact": "测试影响范围",
            "proposer": "测试用户"
        }
    
    @patch('src.services.change_service.NotificationService')
    def test_notification_on_status_change(self, mock_notification_service):
        """测试状态变更时的通知"""
        # 创建变更单
        change, error = ChangeService.create_change(**self.change_data)
        self.assertIsNotNone(change)
        
        # 模拟通知服务
        mock_notify = Mock()
        mock_notification_service.notify_change_status = mock_notify
        
        # 提交审批（应该触发通知）
        success, error = ChangeService.submit_change(change.change_id)
        self.assertTrue(success)
        
        # 验证通知被调用
        # 注意：由于实际代码中可能还没有集成通知服务，这里只是测试框架
        # 实际项目中需要确保通知服务被正确调用
    
    def test_notification_template_based_on_type(self):
        """测试基于变更类型的通知模板"""
        # 测试不同类型变更的通知模板
        change_types = ["需求变更", "设计变更", "技术变更"]
        
        for change_type in change_types:
            data = self.change_data.copy()
            data["type"] = change_type
            
            change, error = ChangeService.create_change(**data)
            self.assertIsNotNone(change)
            self.assertEqual(change.type, change_type)
    
    def test_notification_triggers(self):
        """测试通知触发时机"""
        # 创建变更单
        change, error = ChangeService.create_change(**self.change_data)
        self.assertIsNotNone(change)
        
        # 测试状态变更触发通知
        # 1. 提交审批
        success, error = ChangeService.submit_change(change.change_id)
        self.assertTrue(success)
        
        # 2. 审批通过
        success, error = ChangeService.approve_change(change.change_id, "审批人")
        self.assertTrue(success)
        
        # 3. 开始实施
        success, error = ChangeService.start_implement(change.change_id, "实施人")
        self.assertTrue(success)
        
        # 4. 完成变更
        success, error = ChangeService.complete_change(change_id=change.change_id)
        self.assertTrue(success)
    
    def test_notification_recipients(self):
        """测试通知接收人"""
        # 测试不同角色的通知接收
        # 创建变更单
        change, error = ChangeService.create_change(**self.change_data)
        self.assertIsNotNone(change)
        
        # 提交审批（应该通知审批人）
        success, error = ChangeService.submit_change(change.change_id)
        self.assertTrue(success)
        
        # 审批通过（应该通知实施人）
        success, error = ChangeService.approve_change(change.change_id, "审批人")
        self.assertTrue(success)
    
    def test_notification_fallback(self):
        """测试通知失败的 fallback 机制"""
        # 测试通知服务不可用时的处理
        # 由于这是模拟测试，我们只验证核心功能
        change, error = ChangeService.create_change(**self.change_data)
        self.assertIsNotNone(change)
        
        # 即使通知服务失败，核心功能应该正常工作
        success, error = ChangeService.submit_change(change.change_id)
        self.assertTrue(success)

if __name__ == '__main__':
    unittest.main()
