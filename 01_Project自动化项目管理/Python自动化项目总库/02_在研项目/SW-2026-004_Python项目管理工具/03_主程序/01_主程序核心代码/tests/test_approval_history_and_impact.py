# -*- coding: utf-8 -*-
"""
审批历史和影响分析功能测试用例
"""
import unittest
from src.services.change_service import ChangeService
from src.services.approval_service import ApprovalService
from src.services.impact_service import ImpactService
from src.core.constants import ChangeStatus

class TestApprovalHistoryAndImpact(unittest.TestCase):
    """审批历史和影响分析功能测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.project_id = "PROJ-2026-001"
        self.change_data = {
            "project_id": self.project_id,
            "title": "测试审批历史和影响分析",
            "type": "需求变更",
            "description": "测试审批历史和影响分析功能描述",
            "reason": "测试审批历史和影响分析功能原因",
            "impact": "测试影响范围",
            "proposer": "测试用户"
        }
    
    def test_approval_history_creation(self):
        """测试审批历史记录创建"""
        # 1. 创建变更单
        change, error = ChangeService.create_change(**self.change_data)
        self.assertIsNotNone(change)
        self.assertEqual(error, "")
        
        change_id = change.change_id
        
        # 2. 提交审批
        success, error = ChangeService.submit_change(change_id)
        self.assertTrue(success)
        
        # 3. 审批通过
        success, error = ChangeService.approve_change(change_id, "审批人1")
        self.assertTrue(success)
        
        # 4. 验证审批历史记录
        histories = ApprovalService.get_approval_history(change_id)
        self.assertEqual(len(histories), 1)
        
        history = histories[0]
        self.assertEqual(history.change_id, change_id)
        self.assertEqual(history.approver, "审批人1")
        self.assertEqual(history.action, "approve")
        self.assertEqual(history.comment, "审批通过")
        self.assertIsNotNone(history.approved_at)
    
    def test_approval_history_reject(self):
        """测试驳回时的审批历史记录"""
        # 1. 创建变更单
        change, error = ChangeService.create_change(**self.change_data)
        self.assertIsNotNone(change)
        
        change_id = change.change_id
        
        # 2. 提交审批
        success, error = ChangeService.submit_change(change_id)
        self.assertTrue(success)
        
        # 3. 驳回变更
        reject_reason = "变更理由不充分"
        success, error = ChangeService.reject_change(change_id, "审批人1", reject_reason)
        self.assertTrue(success)
        
        # 4. 验证审批历史记录
        histories = ApprovalService.get_approval_history(change_id)
        self.assertEqual(len(histories), 1)
        
        history = histories[0]
        self.assertEqual(history.action, "reject")
        self.assertIn(reject_reason, history.comment)
    
    def test_approval_history_multiple(self):
        """测试多次审批操作的历史记录"""
        # 1. 创建变更单
        change, error = ChangeService.create_change(**self.change_data)
        self.assertIsNotNone(change)
        
        change_id = change.change_id
        
        # 2. 提交审批
        success, error = ChangeService.submit_change(change_id)
        self.assertTrue(success)
        
        # 3. 第一次驳回
        success, error = ChangeService.reject_change(change_id, "审批人1", "需要补充信息")
        self.assertTrue(success)
        
        # 4. 重新提交
        success, error = ChangeService.submit_change(change_id)
        self.assertTrue(success)
        
        # 5. 第二次审批通过
        success, error = ChangeService.approve_change(change_id, "审批人2")
        self.assertTrue(success)
        
        # 6. 验证审批历史记录
        histories = ApprovalService.get_approval_history(change_id)
        self.assertEqual(len(histories), 2)
        
        # 验证第一次驳回记录
        self.assertEqual(histories[0].approver, "审批人1")
        self.assertEqual(histories[0].action, "reject")
        
        # 验证第二次通过记录
        self.assertEqual(histories[1].approver, "审批人2")
        self.assertEqual(histories[1].action, "approve")
    
    def test_approval_history_empty(self):
        """测试无审批历史的变更单"""
        # 1. 创建变更单（草稿状态）
        change, error = ChangeService.create_change(**self.change_data)
        self.assertIsNotNone(change)
        
        change_id = change.change_id
        
        # 2. 验证审批历史记录为空
        histories = ApprovalService.get_approval_history(change_id)
        self.assertEqual(len(histories), 0)
    
    def test_impact_analysis_creation(self):
        """测试影响分析创建"""
        # 1. 创建变更单
        change, error = ChangeService.create_change(**self.change_data)
        self.assertIsNotNone(change)
        
        change_id = change.change_id
        
        # 2. 执行影响分析
        impact_result = ImpactService.analyze_impact(change_id)
        
        # 3. 验证影响分析结果
        self.assertNotIn("error", impact_result)
        self.assertIn("assessment_id", impact_result)
        self.assertIn("change_id", impact_result)
        self.assertIn("affected_components", impact_result)
        self.assertIn("risk_level", impact_result)
        self.assertIn("mitigation_plan", impact_result)
        self.assertIn("analysis_time", impact_result)
        
        # 验证风险等级是有效的
        valid_risk_levels = ["low", "medium", "high"]
        self.assertIn(impact_result["risk_level"], valid_risk_levels)
    
    def test_impact_analysis_components(self):
        """测试影响分析组件识别"""
        # 1. 创建不同类型的变更单
        test_cases = [
            ("需求变更", "需求变更测试"),
            ("设计变更", "设计变更测试"),
            ("技术变更", "技术变更测试"),
            ("资源变更", "资源变更测试")
        ]
        
        for change_type, description in test_cases:
            change_data = self.change_data.copy()
            change_data["type"] = change_type
            change_data["description"] = description
            
            change, error = ChangeService.create_change(**change_data)
            self.assertIsNotNone(change)
            
            # 执行影响分析
            impact_result = ImpactService.analyze_impact(change.change_id)
            
            # 验证影响分析结果
            self.assertNotIn("error", impact_result)
            self.assertIsInstance(impact_result["affected_components"], list)
    
    def test_impact_analysis_risk_levels(self):
        """测试不同风险等级的评估"""
        # 1. 创建高影响变更
        high_impact_data = self.change_data.copy()
        high_impact_data["title"] = "高影响变更测试"
        high_impact_data["description"] = "这是一个高影响的变更，涉及多个核心模块"
        
        change, error = ChangeService.create_change(**high_impact_data)
        self.assertIsNotNone(change)
        
        # 执行影响分析
        impact_result = ImpactService.analyze_impact(change.change_id)
        
        # 验证影响分析结果
        self.assertNotIn("error", impact_result)
        self.assertIn(impact_result["risk_level"], ["low", "medium", "high"])
        self.assertIsNotNone(impact_result["mitigation_plan"])
    
    def test_impact_analysis_error_handling(self):
        """测试影响分析错误处理"""
        # 1. 测试不存在的变更单
        impact_result = ImpactService.analyze_impact("NON-EXISTENT-ID")
        
        # 验证错误处理
        self.assertIn("error", impact_result)
        self.assertIn("不存在", impact_result["error"])
    
    def test_integration_approval_and_impact(self):
        """测试审批历史和影响分析的集成"""
        # 1. 创建变更单
        change, error = ChangeService.create_change(**self.change_data)
        self.assertIsNotNone(change)
        
        change_id = change.change_id
        
        # 2. 执行影响分析
        impact_result = ImpactService.analyze_impact(change_id)
        self.assertNotIn("error", impact_result)
        
        # 3. 提交审批
        success, error = ChangeService.submit_change(change_id)
        self.assertTrue(success)
        
        # 4. 审批通过
        success, error = ChangeService.approve_change(change_id, "审批人")
        self.assertTrue(success)
        
        # 5. 验证审批历史
        histories = ApprovalService.get_approval_history(change_id)
        self.assertEqual(len(histories), 1)
        
        # 6. 验证影响分析仍然存在
        impact_result2 = ImpactService.analyze_impact(change_id)
        self.assertNotIn("error", impact_result2)
        self.assertEqual(impact_result["assessment_id"], impact_result2["assessment_id"])

if __name__ == '__main__':
    unittest.main()
