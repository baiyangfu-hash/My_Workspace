# -*- coding: utf-8 -*-
"""
变更审批流程测试用例
"""
import unittest
from src.services.change_service import ChangeService
from src.core.constants import ChangeStatus

class TestChangeApprovalProcess(unittest.TestCase):
    """变更审批流程测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.project_id = "PROJ-2026-001"
        self.change_data = {
            "project_id": self.project_id,
            "title": "测试变更审批流程",
            "type": "需求变更",
            "description": "测试变更审批流程描述",
            "reason": "测试变更审批流程原因",
            "impact": "测试影响范围",
            "proposer": "测试用户"
        }
    
    def test_approval_process_complete(self):
        """测试完整审批流程"""
        # 1. 创建变更单（草稿状态）
        change, error = ChangeService.create_change(**self.change_data)
        self.assertIsNotNone(change)
        self.assertEqual(error, "")
        self.assertEqual(change.status, ChangeStatus.DRAFT)
        
        change_id = change.change_id
        
        # 2. 提交审批（草稿 → 待审批）
        success, error = ChangeService.submit_change(change_id)
        self.assertTrue(success)
        self.assertEqual(error, "")
        
        # 验证状态变更
        change = ChangeService.get_change(change_id)
        self.assertEqual(change.status, ChangeStatus.PENDING)
        
        # 3. 审批通过（待审批 → 已批准）
        success, error = ChangeService.approve_change(change_id, "审批人")
        self.assertTrue(success)
        self.assertEqual(error, "")
        
        # 验证状态变更
        change = ChangeService.get_change(change_id)
        self.assertEqual(change.status, ChangeStatus.APPROVED)
        self.assertEqual(change.approver, "审批人")
        
        # 4. 开始实施（已批准 → 实施中）
        success, error = ChangeService.start_implement(change_id, "实施人")
        self.assertTrue(success)
        self.assertEqual(error, "")
        
        # 验证状态变更
        change = ChangeService.get_change(change_id)
        self.assertEqual(change.status, ChangeStatus.IMPLEMENTING)
        self.assertEqual(change.implementer, "实施人")
        
        # 5. 完成变更（实施中 → 已完成）
        success, error = ChangeService.complete_change(change_id)
        self.assertTrue(success)
        self.assertEqual(error, "")
        
        # 验证状态变更
        change = ChangeService.get_change(change_id)
        self.assertEqual(change.status, ChangeStatus.COMPLETED)
    
    def test_approval_process_reject(self):
        """测试审批流程-驳回"""
        # 1. 创建变更单
        change, error = ChangeService.create_change(**self.change_data)
        self.assertIsNotNone(change)
        
        change_id = change.change_id
        
        # 2. 提交审批
        success, error = ChangeService.submit_change(change_id)
        self.assertTrue(success)
        
        # 3. 驳回变更
        reject_reason = "变更理由不充分"
        success, error = ChangeService.reject_change(change_id, "审批人", reject_reason)
        self.assertTrue(success)
        self.assertEqual(error, "")
        
        # 验证状态变更
        change = ChangeService.get_change(change_id)
        self.assertEqual(change.status, ChangeStatus.REJECTED)
        self.assertEqual(change.approver, "审批人")
    
    def test_approval_process_cancel(self):
        """测试审批流程-取消"""
        # 1. 创建变更单
        change, error = ChangeService.create_change(**self.change_data)
        self.assertIsNotNone(change)
        
        change_id = change.change_id
        
        # 2. 提交审批
        success, error = ChangeService.submit_change(change_id)
        self.assertTrue(success)
        
        # 3. 取消变更
        success, error = ChangeService.cancel_change(change_id)
        self.assertTrue(success)
        self.assertEqual(error, "")
        
        # 验证状态变更
        change = ChangeService.get_change(change_id)
        self.assertEqual(change.status, ChangeStatus.CANCELLED)
    
    def test_approval_process_invalid_transitions(self):
        """测试无效的状态转换"""
        # 1. 创建变更单
        change, error = ChangeService.create_change(**self.change_data)
        self.assertIsNotNone(change)
        
        change_id = change.change_id
        
        # 测试：直接审批未提交的变更
        success, error = ChangeService.approve_change(change_id, "审批人")
        self.assertFalse(success)
        self.assertIn("仅待审批状态可以审批", error)
        
        # 测试：直接开始实施未批准的变更
        success, error = ChangeService.start_implement(change_id, "实施人")
        self.assertFalse(success)
        self.assertIn("仅已批准状态可以开始实施", error)
        
        # 测试：直接完成未实施的变更
        success, error = ChangeService.complete_change(change_id)
        self.assertFalse(success)
        self.assertIn("仅实施中状态可以标记完成", error)
    
    def test_approval_process_permissions(self):
        """测试审批流程权限控制"""
        # 1. 创建变更单
        change, error = ChangeService.create_change(**self.change_data)
        self.assertIsNotNone(change)
        
        change_id = change.change_id
        
        # 2. 提交审批
        success, error = ChangeService.submit_change(change_id)
        self.assertTrue(success)
        
        # 3. 测试审批操作
        success, error = ChangeService.approve_change(change_id, "审批人")
        self.assertTrue(success)
        
        # 4. 测试实施操作
        success, error = ChangeService.start_implement(change_id, "实施人")
        self.assertTrue(success)

if __name__ == '__main__':
    unittest.main()
