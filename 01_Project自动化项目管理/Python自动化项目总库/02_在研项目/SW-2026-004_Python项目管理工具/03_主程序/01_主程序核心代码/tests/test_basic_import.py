# -*- coding: utf-8 -*-
"""
测试基本导入
"""
import sys
import os

# 设置路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    print("测试基本导入...")
    
    # 测试1: 导入常量模块
    from src.core.constants import ChangeStatus
    print("✓ 导入常量模块成功")
    
    # 测试2: 导入模型基类
    from src.models.base import Base
    print("✓ 导入模型基类成功")
    
    # 测试3: 导入变更模型
    from src.models.change import Change
    print("✓ 导入变更模型成功")
    
    # 测试4: 导入影响评估模型
    from src.models.impact import ImpactAssessment
    print("✓ 导入影响评估模型成功")
    
    # 测试5: 导入审批历史模型
    from src.models.approval import ApprovalHistory
    print("✓ 导入审批历史模型成功")
    
    # 测试6: 导入数据库模块
    from src.dao.database import db
    print("✓ 导入数据库模块成功")
    
    # 测试7: 导入变更DAO
    from src.dao.change_dao import ChangeDAO
    print("✓ 导入变更DAO成功")
    
    # 测试8: 导入影响分析服务
    from src.services.impact_service import ImpactService
    print("✓ 导入影响分析服务成功")
    
    # 测试9: 导入通知服务
    from src.services.notification_service import NotificationService
    print("✓ 导入通知服务成功")
    
    # 测试10: 导入变更分析服务
    from src.services.change_analytics_service import ChangeAnalyticsService
    print("✓ 导入变更分析服务成功")
    
    # 测试11: 导入变更服务
    from src.services.change_service import ChangeService
    print("✓ 导入变更服务成功")
    
    print("\n所有模块导入成功！")
    
except Exception as e:
    print(f"\n导入失败: {e}")
    import traceback
    traceback.print_exc()
