# -*- coding: utf-8 -*-
"""
运行测试脚本
"""
import unittest
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tests.test_change_impact import TestChangeImpactAnalysis
from tests.test_change_approval import TestChangeApprovalProcess
from tests.test_change_document import TestChangeDocumentManagement
from tests.test_change_statistics import TestChangeStatistics
from tests.test_change_notification import TestChangeNotification
from tests.test_change_performance import TestChangePerformance

# 运行所有测试
if __name__ == '__main__':
    print("开始运行变更管理功能测试...")
    
    # 运行变更影响分析测试
    print("\n=== 运行变更影响分析测试 ===")
    suite1 = unittest.TestLoader().loadTestsFromTestCase(TestChangeImpactAnalysis)
    result1 = unittest.TextTestRunner(verbosity=2).run(suite1)
    
    # 运行变更审批流程测试
    print("\n=== 运行变更审批流程测试 ===")
    suite2 = unittest.TestLoader().loadTestsFromTestCase(TestChangeApprovalProcess)
    result2 = unittest.TextTestRunner(verbosity=2).run(suite2)
    
    # 运行变更文档管理测试
    print("\n=== 运行变更文档管理测试 ===")
    suite3 = unittest.TestLoader().loadTestsFromTestCase(TestChangeDocumentManagement)
    result3 = unittest.TextTestRunner(verbosity=2).run(suite3)
    
    # 运行变更统计分析测试
    print("\n=== 运行变更统计分析测试 ===")
    suite4 = unittest.TestLoader().loadTestsFromTestCase(TestChangeStatistics)
    result4 = unittest.TextTestRunner(verbosity=2).run(suite4)
    
    # 运行变更通知机制测试
    print("\n=== 运行变更通知机制测试 ===")
    suite5 = unittest.TestLoader().loadTestsFromTestCase(TestChangeNotification)
    result5 = unittest.TextTestRunner(verbosity=2).run(suite5)
    
    # 运行变更管理功能性能测试
    print("\n=== 运行变更管理功能性能测试 ===")
    suite6 = unittest.TestLoader().loadTestsFromTestCase(TestChangePerformance)
    result6 = unittest.TextTestRunner(verbosity=2).run(suite6)
    
    # 汇总测试结果
    print("\n=== 测试结果汇总 ===")
    print(f"变更影响分析测试: {'通过' if result1.wasSuccessful() else '失败'}")
    print(f"变更审批流程测试: {'通过' if result2.wasSuccessful() else '失败'}")
    print(f"变更文档管理测试: {'通过' if result3.wasSuccessful() else '失败'}")
    print(f"变更统计分析测试: {'通过' if result4.wasSuccessful() else '失败'}")
    print(f"变更通知机制测试: {'通过' if result5.wasSuccessful() else '失败'}")
    print(f"变更管理功能性能测试: {'通过' if result6.wasSuccessful() else '失败'}")
    
    # 检查是否所有测试都通过
    all_passed = all([
        result1.wasSuccessful(),
        result2.wasSuccessful(),
        result3.wasSuccessful(),
        result4.wasSuccessful(),
        result5.wasSuccessful(),
        result6.wasSuccessful()
    ])
    
    print(f"\n总体测试结果: {'全部通过' if all_passed else '存在失败'}")
