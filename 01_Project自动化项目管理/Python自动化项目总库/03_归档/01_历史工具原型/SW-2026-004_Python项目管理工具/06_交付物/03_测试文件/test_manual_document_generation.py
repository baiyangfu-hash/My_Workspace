# -*- coding: utf-8 -*-
"""
手动测试变更文档生成功能
"""
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from src.services.change_service import ChangeService
from src.services.project_service import ProjectService

def test_manual_document_generation():
    """手动测试变更文档生成功能"""
    print("\n=== 手动测试变更文档生成功能 ===")
    
    try:
        # 步骤1: 查看现有项目
        print("\n1. 查看现有项目")
        projects, total = ProjectService.list_projects(page=1, size=10)
        print(f"现有项目数量: {total}")
        for project in projects:
            print(f"  - {project.code}: {project.name} (ID: {project.project_id})")
        
        # 步骤2: 选择一个项目进行测试
        if not projects:
            print("❌ 没有现有项目，请先创建项目")
            return
        
        project = projects[0]
        print(f"\n选择测试项目: {project.code} - {project.name}")
        
        # 步骤3: 创建测试变更单
        print("\n3. 创建测试变更单")
        change, error = ChangeService.create_change(
            project_id=project.project_id,
            title="测试变更文档生成",
            type="功能变更",
            description="测试自动生成变更文档功能",
            reason="验证变更管理功能完整性",
            impact="变更管理模块",
            proposer="系统测试"
        )
        
        if not change:
            print(f"❌ 创建变更单失败: {error}")
            return
        print(f"✅ 创建变更单成功: {change.change_id}")
        
        # 步骤4: 检查变更单文件是否生成
        print("\n4. 检查变更单文件")
        change_file_path = os.path.join(
            project.path,
            "05_变更管理",
            "01_变更单",
            f"{change.change_id}.md"
        )
        
        if os.path.exists(change_file_path):
            print(f"✅ 变更单文件生成成功: {change_file_path}")
            # 显示文件内容预览
            with open(change_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print("\n变更单文件内容预览:")
            print(content[:500] + "..." if len(content) > 500 else content)
        else:
            print(f"❌ 变更单文件未生成: {change_file_path}")
            return
        
        # 步骤5: 生成变更台帐
        print("\n5. 生成变更台帐")
        ledger_path, error = ChangeService.generate_ledger(project.project_id)
        
        if not ledger_path:
            print(f"❌ 生成变更台帐失败: {error}")
            return
        print(f"✅ 生成变更台帐成功: {ledger_path}")
        
        # 步骤6: 检查变更台帐文件
        if os.path.exists(ledger_path):
            print("✅ 变更台帐文件生成成功")
            # 显示文件内容预览
            with open(ledger_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print("\n变更台帐文件内容预览:")
            print(content[:500] + "..." if len(content) > 500 else content)
        else:
            print(f"❌ 变更台帐文件未生成: {ledger_path}")
            return
        
        print("\n🎉 手动测试完成！变更文档生成功能正常工作")
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n=== 测试完成 ===")

if __name__ == '__main__':
    test_manual_document_generation()