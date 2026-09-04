# -*- coding: utf-8 -*-
"""
测试变更管理模块
"""
import sys
import os

# 设置路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    # 导入变更管理相关模块
    from src.core.constants import ChangeStatus, ImpactLevel
    from src.models.change import Change
    from src.models.impact import ImpactAssessment
    from src.models.approval import ApprovalHistory
    from src.services.change_service import ChangeService
    from src.services.impact_service import ImpactService
    from src.services.notification_service import NotificationService
    from src.services.change_analytics_service import ChangeAnalyticsService
    from src.dao.change_dao import ChangeDAO
    
    print("所有变更管理模块导入成功！")
    print(f"ChangeStatus 枚举: {[s.value for s in ChangeStatus]}")
    print(f"ImpactLevel 枚举: {[s.value for s in ImpactLevel]}")
    print(f"Change 模型字段: {[c.name for c in Change.__table__.columns]}")
    print(f"ImpactAssessment 模型字段: {[c.name for c in ImpactAssessment.__table__.columns]}")
    print(f"ApprovalHistory 模型字段: {[c.name for c in ApprovalHistory.__table__.columns]}")
    
except Exception as e:
    print(f"导入失败: {e}")
    import traceback
    traceback.print_exc()
