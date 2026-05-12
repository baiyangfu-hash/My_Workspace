# -*- coding: utf-8 -*-
"""
变更管理功能性能测试用例
"""
import unittest
import time
import gc
from src.services.change_service import ChangeService
from src.core.constants import ChangeStatus

class TestChangePerformance(unittest.TestCase):
    """变更管理功能性能测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.project_id = "PROJ-2026-001"
        self.change_data = {
            "project_id": self.project_id,
            "title": "测试变更性能",
            "type": "需求变更",
            "description": "测试变更性能描述",
            "reason": "测试变更性能原因",
            "impact": "测试影响范围",
            "proposer": "测试用户"
        }
    
    def test_batch_create_changes(self):
        """测试批量创建变更单的性能"""
        # 测试创建100个变更单的性能
        start_time = time.time()
        change_ids = []
        
        for i in range(100):
            data = self.change_data.copy()
            data["title"] = f"性能测试变更{i+1}"
            change, error = ChangeService.create_change(**data)
            self.assertIsNotNone(change)
            change_ids.append(change.change_id)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 验证性能指标
        print(f"批量创建100个变更单耗时: {total_time:.2f}秒")
        # 性能要求：100个变更单创建时间应小于10秒
        self.assertLess(total_time, 10)
        
        # 清理测试数据
        for change_id in change_ids:
            ChangeService.delete_change(change_id)
    
    def test_status_update_performance(self):
        """测试变更状态更新的性能"""
        # 创建测试变更单
        change, error = ChangeService.create_change(**self.change_data)
        self.assertIsNotNone(change)
        
        # 测试状态更新性能
        start_time = time.time()
        
        # 提交审批
        success, error = ChangeService.submit_change(change.change_id)
        self.assertTrue(success)
        
        # 审批通过
        success, error = ChangeService.approve_change(change.change_id, "审批人")
        self.assertTrue(success)
        
        # 开始实施
        success, error = ChangeService.start_implement(change.change_id, "实施人")
        self.assertTrue(success)
        
        # 完成变更
        success, error = ChangeService.complete_change(change.change_id)
        self.assertTrue(success)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 验证性能指标
        print(f"变更状态全流程更新耗时: {total_time:.2f}秒")
        # 性能要求：完整状态流程更新应小于2秒
        self.assertLess(total_time, 2)
    
    def test_statistics_performance(self):
        """测试变更统计的性能"""
        # 创建多个变更单
        for i in range(50):
            data = self.change_data.copy()
            data["title"] = f"统计测试变更{i+1}"
            change, error = ChangeService.create_change(**data)
            self.assertIsNotNone(change)
        
        # 测试统计性能
        start_time = time.time()
        stats = ChangeService.get_statistics(self.project_id)
        end_time = time.time()
        total_time = end_time - start_time
        
        # 验证性能指标
        print(f"获取变更统计耗时: {total_time:.2f}秒")
        # 性能要求：统计查询应小于0.5秒
        self.assertLess(total_time, 0.5)
    
    def test_change_list_performance(self):
        """测试变更列表查询的性能"""
        # 创建多个变更单
        for i in range(100):
            data = self.change_data.copy()
            data["title"] = f"列表测试变更{i+1}"
            change, error = ChangeService.create_change(**data)
            self.assertIsNotNone(change)
        
        # 测试列表查询性能
        start_time = time.time()
        changes, total = ChangeService.list_changes(self.project_id, page=1, size=50)
        end_time = time.time()
        total_time = end_time - start_time
        
        # 验证性能指标
        print(f"查询变更列表耗时: {total_time:.2f}秒")
        # 性能要求：列表查询应小于1秒
        self.assertLess(total_time, 1)
    
    def test_memory_usage(self):
        """测试内存使用情况"""
        # 测试内存使用
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 创建多个变更单
        change_ids = []
        for i in range(200):
            data = self.change_data.copy()
            data["title"] = f"内存测试变更{i+1}"
            change, error = ChangeService.create_change(**data)
            self.assertIsNotNone(change)
            change_ids.append(change.change_id)
        
        # 强制垃圾回收
        gc.collect()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"内存使用增加: {memory_increase:.2f} MB")
        # 性能要求：200个变更单内存增加应小于50MB
        self.assertLess(memory_increase, 50)
        
        # 清理测试数据
        for change_id in change_ids:
            ChangeService.delete_change(change_id)

if __name__ == '__main__':
    unittest.main()
