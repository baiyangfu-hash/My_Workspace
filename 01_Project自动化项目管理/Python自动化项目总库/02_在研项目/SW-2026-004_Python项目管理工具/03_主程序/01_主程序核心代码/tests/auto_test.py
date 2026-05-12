# -*- coding: utf-8 -*-
"""
自动测试变更管理新功能
"""
import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=== 变更管理新功能自动测试 ===")
print(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 50)

# 测试结果记录
test_results = []

def test_imports():
    """测试模块导入"""
    print("\n1. 测试模块导入...")
    try:
        from src.services.change_service import ChangeService
        from src.services.approval_service import ApprovalService
        from src.services.impact_service import ImpactService
        from src.core.constants import ChangeStatus
        print("✅ 模块导入成功")
        test_results.append("模块导入: 通过")
        return True
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        test_results.append(f"模块导入: 失败 - {e}")
        return False

def test_change_creation():
    """测试变更单创建"""
    print("\n2. 测试变更单创建...")
    try:
        from src.services.change_service import ChangeService
        
        change_data = {
            "project_id": "PROJ-2026-001",
            "title": "自动测试变更",
            "type": "测试变更",
            "description": "自动测试审批历史和影响分析功能",
            "reason": "功能验证",
            "impact": "测试影响范围",
            "proposer": "自动测试"
        }
        
        change, error = ChangeService.create_change(**change_data)
        if change:
            print(f"✅ 变更单创建成功: {change.change_id}")
            test_results.append(f"变更单创建: 通过 - {change.change_id}")
            return change
        else:
            print(f"❌ 变更单创建失败: {error}")
            test_results.append(f"变更单创建: 失败 - {error}")
            return None
    except Exception as e:
        print(f"❌ 变更单创建异常: {e}")
        test_results.append(f"变更单创建: 异常 - {e}")
        return None

def test_impact_analysis(change):
    """测试影响分析"""
    print("\n3. 测试影响分析...")
    try:
        from src.services.impact_service import ImpactService
        
        impact_result = ImpactService.analyze_impact(change.change_id)
        if "error" in impact_result:
            print(f"❌ 影响分析失败: {impact_result['error']}")
            test_results.append(f"影响分析: 失败 - {impact_result['error']}")
            return False
        else:
            print("✅ 影响分析成功")
            print(f"   风险等级: {impact_result['risk_level']}")
            print(f"   受影响组件数: {len(impact_result['affected_components'])}")
            test_results.append("影响分析: 通过")
            return True
    except Exception as e:
        print(f"❌ 影响分析异常: {e}")
        test_results.append(f"影响分析: 异常 - {e}")
        return False

def test_approval_process(change):
    """测试审批流程"""
    print("\n4. 测试审批流程...")
    try:
        from src.services.change_service import ChangeService
        from src.services.approval_service import ApprovalService
        
        # 提交审批
        success, error = ChangeService.submit_change(change.change_id)
        if not success:
            print(f"❌ 提交审批失败: {error}")
            test_results.append(f"提交审批: 失败 - {error}")
            return False
        print("✅ 提交审批成功")
        
        # 审批通过
        success, error = ChangeService.approve_change(change.change_id, "自动测试审批人")
        if not success:
            print(f"❌ 审批通过失败: {error}")
            test_results.append(f"审批通过: 失败 - {error}")
            return False
        print("✅ 审批通过成功")
        
        # 验证审批历史
        histories = ApprovalService.get_approval_history(change.change_id)
        if not histories:
            print("❌ 审批历史获取失败")
            test_results.append("审批历史: 失败")
            return False
        print(f"✅ 审批历史获取成功，共 {len(histories)} 条记录")
        for i, history in enumerate(histories, 1):
            print(f"   {i}. 审批人: {history.approver}, 动作: {history.action}")
        test_results.append("审批流程: 通过")
        return True
    except Exception as e:
        print(f"❌ 审批流程异常: {e}")
        test_results.append(f"审批流程: 异常 - {e}")
        return False

def test_integration():
    """测试集成功能"""
    print("\n5. 测试集成功能...")
    try:
        from src.services.change_service import ChangeService
        from src.services.impact_service import ImpactService
        from src.services.approval_service import ApprovalService
        
        # 创建变更单
        change_data = {
            "project_id": "PROJ-2026-001",
            "title": "集成测试变更",
            "type": "集成测试",
            "description": "集成测试审批历史和影响分析",
            "reason": "集成验证",
            "impact": "测试影响范围",
            "proposer": "集成测试"
        }
        
        change, error = ChangeService.create_change(**change_data)
        if not change:
            print(f"❌ 集成测试变更单创建失败: {error}")
            test_results.append(f"集成测试: 失败 - {error}")
            return False
        
        # 执行影响分析
        impact_result = ImpactService.analyze_impact(change.change_id)
        if "error" in impact_result:
            print(f"❌ 集成测试影响分析失败: {impact_result['error']}")
            test_results.append(f"集成测试: 失败 - {impact_result['error']}")
            return False
        
        # 提交审批
        success, error = ChangeService.submit_change(change.change_id)
        if not success:
            print(f"❌ 集成测试提交审批失败: {error}")
            test_results.append(f"集成测试: 失败 - {error}")
            return False
        
        # 审批通过
        success, error = ChangeService.approve_change(change.change_id, "集成测试审批人")
        if not success:
            print(f"❌ 集成测试审批通过失败: {error}")
            test_results.append(f"集成测试: 失败 - {error}")
            return False
        
        # 验证审批历史
        histories = ApprovalService.get_approval_history(change.change_id)
        if not histories:
            print("❌ 集成测试审批历史获取失败")
            test_results.append("集成测试: 失败")
            return False
        
        print("✅ 集成测试成功")
        test_results.append("集成测试: 通过")
        return True
    except Exception as e:
        print(f"❌ 集成测试异常: {e}")
        test_results.append(f"集成测试: 异常 - {e}")
        return False

def main():
    """主测试函数"""
    print("开始自动测试变更管理新功能...")
    
    # 测试模块导入
    if not test_imports():
        print("\n❌ 模块导入失败，测试终止")
        return
    
    # 测试变更单创建
    change = test_change_creation()
    if not change:
        print("\n❌ 变更单创建失败，测试终止")
        return
    
    # 测试影响分析
    impact_ok = test_impact_analysis(change)
    
    # 测试审批流程
    approval_ok = test_approval_process(change)
    
    # 测试集成功能
    integration_ok = test_integration()
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print("=== 测试结果汇总 ===")
    for result in test_results:
        print(f"- {result}")
    
    # 统计通过率
    passed = sum(1 for r in test_results if "通过" in r)
    total = len(test_results)
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"\n测试通过率: {passed}/{total} ({pass_rate:.1f}%)")
    
    if passed == total:
        print("\n🎉 所有测试通过！变更管理新功能工作正常")
    else:
        print("\n⚠️ 部分测试失败，需要检查和修复")
    
    print("\n测试完成。")

if __name__ == "__main__":
    main()
