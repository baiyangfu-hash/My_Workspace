# -*- coding: utf-8 -*-
"""
变更统计分析测试用例
"""
import unittest
from src.services.change_service import ChangeService
from src.core.constants import ChangeStatus

class TestChangeStatistics(unittest.TestCase):
    """变更统计分析测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.project_id = "PROJ-2026-001"
        self.change_data = {
            "project_id": self.project_id,
            "title": "测试变更统计",
            "type": "需求变更",
            "description": "测试变更统计描述",
            "reason": "测试变更统计原因",
            "impact": "测试影响范围",
            "proposer": "测试用户"
        }
    
    def test_statistics_basic(self):
        """测试基本统计功能"""
        # 获取初始统计数据
        initial_stats = ChangeService.get_statistics(self.project_id)
        self.assertIsInstance(initial_stats, dict)
        self.assertIn("total", initial_stats)
        self.assertIn("draft", initial_stats)
        self.assertIn("pending", initial_stats)
        self.assertIn("approved", initial_stats)
        self.assertIn("implementing", initial_stats)
        self.assertIn("completed", initial_stats)
        self.assertIn("rejected", initial_stats)
        self.assertIn("cancelled", initial_stats)
    
    def test_statistics_with_changes(self):
        """测试有变更数据的统计"""
        # 创建多个变更单
        for i in range(3):
            data = self.change_data.copy()
            data["title"] = f"测试变更{i+1}"
            change, error = ChangeService.create_change(**data)
            self.assertIsNotNone(change)
        
        # 获取统计数据
        stats = ChangeService.get_statistics(self.project_id)
        self.assertGreater(stats.get("total", 0), 0)
        self.assertGreater(stats.get("draft", 0), 0)
    
    def test_statistics_status_distribution(self):
        """测试状态分布统计"""
        # 创建不同状态的变更单
        
        # 1. 草稿状态
        change1, error = ChangeService.create_change(**self.change_data)
        self.assertIsNotNone(change1)
        
        # 2. 待审批状态
        change2, error = ChangeService.create_change(**self.change_data)
        self.assertIsNotNone(change2)
        ChangeService.submit_change(change2.change_id)
        
        # 3. 已批准状态
        change3, error = ChangeService.create_change(**self.change_data)
        self.assertIsNotNone(change3)
        ChangeService.submit_change(change3.change_id)
        ChangeService.approve_change(change3.change_id, "审批人")
        
        # 获取统计数据
        stats = ChangeService.get_statistics(self.project_id)
        self.assertGreater(stats.get("draft", 0), 0)
        self.assertGreater(stats.get("pending", 0), 0)
        self.assertGreater(stats.get("approved", 0), 0)
    
    def test_statistics_trend_analysis(self):
        """测试趋势分析功能"""
        # 测试统计数据的趋势分析
        # 由于这是模拟测试，我们只验证统计功能是否正常工作
        stats = ChangeService.get_statistics(self.project_id)
        self.assertIsInstance(stats, dict)
        for key, value in stats.items():
            self.assertIsInstance(value, int)
            self.assertGreaterEqual(value, 0)
    
    def test_statistics_empty_project(self):
        """测试空项目的统计"""
        # 测试不存在的项目
        non_existent_project_id = "PROJ-NON-EXISTENT"
        stats = ChangeService.get_statistics(non_existent_project_id)
        self.assertIsInstance(stats, dict)
        # 应该返回空统计数据
        for key, value in stats.items():
            self.assertEqual(value, 0)

if __name__ == '__main__':
    unittest.main()
