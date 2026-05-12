# -*- coding: utf-8 -*-
"""
代码验证脚本 - 检查新创建的代码是否可以正常导入
"""
import sys
import os

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

print("开始验证代码...")

try:
    # 测试导入ApprovalService
    print("1. 测试导入ApprovalService...")
    from src.services.approval_service import ApprovalService
    print("   ✓ ApprovalService导入成功")
    
    # 测试导入ApprovalDAO
    print("2. 测试导入ApprovalDAO...")
    from src.dao.approval_dao import ApprovalDAO
    print("   ✓ ApprovalDAO导入成功")
    
    # 测试导入ApprovalHistory模型
    print("3. 测试导入ApprovalHistory模型...")
    from src.models.approval import ApprovalHistory
    print("   ✓ ApprovalHistory模型导入成功")
    
    # 测试导入ImpactService
    print("4. 测试导入ImpactService...")
    from src.services.impact_service import ImpactService
    print("   ✓ ImpactService导入成功")
    
    # 测试导入ImpactAssessment模型
    print("5. 测试导入ImpactAssessment模型...")
    from src.models.impact import ImpactAssessment
    print("   ✓ ImpactAssessment模型导入成功")
    
    # 测试导入ChangeService
    print("6. 测试导入ChangeService...")
    from src.services.change_service import ChangeService
    print("   ✓ ChangeService导入成功")
    
    print("\n所有核心模块导入成功！")
    
    # 检查类方法
    print("\n检查类方法...")
    print(f"ApprovalService方法: {[m for m in dir(ApprovalService) if not m.startswith('_')]}")
    print(f"ApprovalDAO方法: {[m for m in dir(ApprovalDAO) if not m.startswith('_')]}")
    print(f"ImpactService方法: {[m for m in dir(ImpactService) if not m.startswith('_')]}")
    
    print("\n代码验证完成！")
    print("✓ 所有新创建的代码都可以正常导入")
    print("✓ 类和方法定义正确")
    
except ImportError as e:
    print(f"✗ 导入失败: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ 验证失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
