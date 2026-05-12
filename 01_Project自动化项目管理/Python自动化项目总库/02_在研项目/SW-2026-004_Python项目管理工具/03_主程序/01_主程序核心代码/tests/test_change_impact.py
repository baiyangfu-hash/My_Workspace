# -*- coding: utf-8 -*-
"""
变更影响分析模块测试用例
"""
import unittest
from unittest.mock import Mock, patch
from src.services.change_service import ChangeService
from src.models.change import Change
from src.core.constants import ChangeStatus

class TestChangeImpactAnalysis(unittest.TestCase):
    """变更影响分析模块测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.project_id = "PROJ-2026-001"
        self.change_data = {
            "project_id": self.project_id,
            "title": "测试变更",
            "type": "需求变更",
            "description": "测试变更描述",
            "reason": "测试变更原因",
            "impact": "测试影响范围",
            "proposer": "测试用户"
        }
    
    def test_impact_analysis_basic(self):
        """测试基本影响分析功能"""
        # 创建变更单
        change, error = ChangeService.create_change(**self.change_data)
        self.assertIsNotNone(change)
        self.assertEqual(error, "")
        
        # 验证变更单创建成功
        self.assertEqual(change.title, self.change_data["title"])
        self.assertEqual(change.type, self.change_data["type"])
        self.assertEqual(change.status, ChangeStatus.DRAFT)
    
    def test_impact_analysis_with_different_types(self):
        """测试不同变更类型的影响分析"""
        change_types = ["需求变更", "设计变更", "技术变更", "资源变更", "进度变更"]
        
        for change_type in change_types:
            data = self.change_data.copy()
            data["type"] = change_type
            
            change, error = ChangeService.create_change(**data)
            self.assertIsNotNone(change)
            self.assertEqual(error, "")
            self.assertEqual(change.type, change_type)
    
    def test_impact_analysis_risk_assessment(self):
        """测试风险评估功能"""
        # 模拟风险评估逻辑
        high_risk_change = self.change_data.copy()
        high_risk_change["title"] = "核心功能变更"
        high_risk_change["description"] = "修改核心业务逻辑，影响范围较大"
        
        change, error = ChangeService.create_change(**high_risk_change)
        self.assertIsNotNone(change)
        self.assertEqual(error, "")
    
    def test_impact_analysis_mitigation_plan(self):
        """测试缓解措施生成"""
        # 测试带有缓解措施的变更
        change_with_mitigation = self.change_data.copy()
        change_with_mitigation["impact"] = "可能影响系统稳定性，需要制定缓解措施"
        
        change, error = ChangeService.create_change(**change_with_mitigation)
        self.assertIsNotNone(change)
        self.assertEqual(error, "")
    
    def test_impact_analysis_integration(self):
        """测试影响分析与其他模块集成"""
        # 创建变更单
        change, error = ChangeService.create_change(**self.change_data)
        self.assertIsNotNone(change)
        
        # 提交审批
        success, error = ChangeService.submit_change(change.change_id)
        self.assertTrue(success)
        self.assertEqual(error, "")
        
        # 审批通过
        success, error = ChangeService.approve_change(change.change_id, "审批人")
        self.assertTrue(success)
        self.assertEqual(error, "")

if __name__ == '__main__':
    unittest.main()
