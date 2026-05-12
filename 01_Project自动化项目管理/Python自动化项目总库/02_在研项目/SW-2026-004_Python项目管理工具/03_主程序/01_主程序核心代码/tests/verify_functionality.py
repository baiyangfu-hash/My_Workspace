# -*- coding: utf-8 -*-
"""
验证审批历史和影响分析功能
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.services.change_service import ChangeService
    from src.services.approval_service import ApprovalService
    from src.services.impact_service import ImpactService
    from src.core.constants import ChangeStatus
    print("✅ 模块导入成功")
except Exception as e:
    print(f"❌ 模块导入失败: {e}")
    sys.exit(1)

def test_approval_history():
    """测试审批历史功能"""
    print("\n=== 测试审批历史功能 ===")
    
    # 1. 创建变更单
    change_data = {
        "project_id": "PROJ-2026-001",
        "title": "测试审批历史",
        "type": "需求变更",
        "description": "测试审批历史功能",
        "reason": "测试审批历史功能",
        "impact": "测试影响范围",
        "proposer": "测试用户"
    }
    
    print("1. 创建变更单...")
    change, error = ChangeService.create_change(**change_data)
    if change:
        print(f"✅ 变更单创建成功: {change.change_id}")
    else:
        print(f"❌ 变更单创建失败: {error}")
        return False
    
    change_id = change.change_id
    
    # 2. 提交审批
    print("2. 提交审批...")
    success, error = ChangeService.submit_change(change_id)
    if success:
        print("✅ 提交审批成功")
    else:
        print(f"❌ 提交审批失败: {error}")
        return False
    
    # 3. 审批通过
    print("3. 审批通过...")
    success, error = ChangeService.approve_change(change_id, "测试审批人")
    if success:
        print("✅ 审批通过成功")
    else:
        print(f"❌ 审批通过失败: {error}")
        return False
    
    # 4. 获取审批历史
    print("4. 获取审批历史...")
    histories = ApprovalService.get_approval_history(change_id)
    if histories:
        print(f"✅ 审批历史获取成功，共 {len(histories)} 条记录")
        for i, history in enumerate(histories, 1):
            print(f"   {i}. 审批人: {history.approver}, 动作: {history.action}, 时间: {history.approved_at}")
    else:
        print("❌ 审批历史获取失败")
        return False
    
    return True

def test_impact_analysis():
    """测试影响分析功能"""
    print("\n=== 测试影响分析功能 ===")
    
    # 1. 创建变更单
    change_data = {
        "project_id": "PROJ-2026-001",
        "title": "测试影响分析",
        "type": "技术变更",
        "description": "测试影响分析功能",
        "reason": "测试影响分析功能",
        "impact": "测试影响范围",
        "proposer": "测试用户"
    }
    
    print("1. 创建变更单...")
    change, error = ChangeService.create_change(**change_data)
    if change:
        print(f"✅ 变更单创建成功: {change.change_id}")
    else:
        print(f"❌ 变更单创建失败: {error}")
        return False
    
    change_id = change.change_id
    
    # 2. 执行影响分析
    print("2. 执行影响分析...")
    impact_result = ImpactService.analyze_impact(change_id)
    if "error" in impact_result:
        print(f"❌ 影响分析失败: {impact_result['error']}")
        return False
    else:
        print("✅ 影响分析成功")
        print(f"   风险等级: {impact_result['risk_level']}")
        print(f"   受影响组件数: {len(impact_result['affected_components'])}")
        print(f"   分析时间: {impact_result['analysis_time']}")
    
    return True

def test_integration():
    """测试集成功能"""
    print("\n=== 测试集成功能 ===")
    
    # 1. 创建变更单
    change_data = {
        "project_id": "PROJ-2026-001",
        "title": "测试集成功能",
        "type": "设计变更",
        "description": "测试集成功能",
        "reason": "测试集成功能",
        "impact": "测试影响范围",
        "proposer": "测试用户"
    }
    
    print("1. 创建变更单...")
    change, error = ChangeService.create_change(**change_data)
    if change:
        print(f"✅ 变更单创建成功: {change.change_id}")
    else:
        print(f"❌ 变更单创建失败: {error}")
        return False
    
    change_id = change.change_id
    
    # 2. 执行影响分析
    print("2. 执行影响分析...")
    impact_result = ImpactService.analyze_impact(change_id)
    if "error" in impact_result:
        print(f"❌ 影响分析失败: {impact_result['error']}")
        return False
    else:
        print("✅ 影响分析成功")
    
    # 3. 提交审批
    print("3. 提交审批...")
    success, error = ChangeService.submit_change(change_id)
    if success:
        print("✅ 提交审批成功")
    else:
        print(f"❌ 提交审批失败: {error}")
        return False
    
    # 4. 审批通过
    print("4. 审批通过...")
    success, error = ChangeService.approve_change(change_id, "测试审批人")
    if success:
        print("✅ 审批通过成功")
    else:
        print(f"❌ 审批通过失败: {error}")
        return False
    
    # 5. 验证审批历史
    print("5. 验证审批历史...")
    histories = ApprovalService.get_approval_history(change_id)
    if histories:
        print(f"✅ 审批历史获取成功，共 {len(histories)} 条记录")
    else:
        print("❌ 审批历史获取失败")
        return False
    
    # 6. 再次执行影响分析
    print("6. 再次执行影响分析...")
    impact_result2 = ImpactService.analyze_impact(change_id)
    if "error" in impact_result2:
        print(f"❌ 影响分析失败: {impact_result2['error']}")
        return False
    else:
        print("✅ 影响分析成功")
    
    return True

if __name__ == "__main__":
    print("开始验证审批历史和影响分析功能...")
    
    # 测试审批历史
    approval_result = test_approval_history()
    
    # 测试影响分析
    impact_result = test_impact_analysis()
    
    # 测试集成功能
    integration_result = test_integration()
    
    print("\n=== 验证结果 ===")
    print(f"审批历史功能: {'✅ 通过' if approval_result else '❌ 失败'}")
    print(f"影响分析功能: {'✅ 通过' if impact_result else '❌ 失败'}")
    print(f"集成功能: {'✅ 通过' if integration_result else '❌ 失败'}")
    
    if approval_result and impact_result and integration_result:
        print("\n🎉 所有功能验证通过！")
    else:
        print("\n⚠️ 部分功能验证失败，请检查错误信息。")
