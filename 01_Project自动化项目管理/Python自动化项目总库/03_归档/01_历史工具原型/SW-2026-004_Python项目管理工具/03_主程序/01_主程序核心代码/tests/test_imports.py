# -*- coding: utf-8 -*-
"""
测试导入变更管理模块
"""
import sys
import os

# 设置路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("开始测试导入变更管理模块...")

try:
    from src.core.constants import ChangeStatus, ImpactLevel
    print("✓ 导入常量模块成功")
except Exception as e:
    print(f"✗ 导入常量模块失败: {e}")

try:
    from src.models.change import Change
    print("✓ 导入变更模型成功")
except Exception as e:
    print(f"✗ 导入变更模型失败: {e}")

try:
    from src.models.impact import ImpactAssessment
    print("✓ 导入影响评估模型成功")
except Exception as e:
    print(f"✗ 导入影响评估模型失败: {e}")

try:
    from src.models.approval import ApprovalHistory
    print("✓ 导入审批历史模型成功")
except Exception as e:
    print(f"✗ 导入审批历史模型失败: {e}")

try:
    from src.services.change_service import ChangeService
    print("✓ 导入变更服务成功")
except Exception as e:
    print(f"✗ 导入变更服务失败: {e}")

try:
    from src.services.impact_service import ImpactService
    print("✓ 导入影响分析服务成功")
except Exception as e:
    print(f"✗ 导入影响分析服务失败: {e}")

try:
    from src.services.change_analytics_service import ChangeAnalyticsService
    print("✓ 导入变更分析服务成功")
except Exception as e:
    print(f"✗ 导入变更分析服务失败: {e}")

try:
    from src.services.notification_service import NotificationService
    print("✓ 导入通知服务成功")
except Exception as e:
    print(f"✗ 导入通知服务失败: {e}")

try:
    from src.dao.change_dao import ChangeDAO
    print("✓ 导入变更DAO成功")
except Exception as e:
    print(f"✗ 导入变更DAO失败: {e}")

print("导入测试完成")
