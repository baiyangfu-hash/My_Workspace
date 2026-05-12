# -*- coding: utf-8 -*-
"""
变更管理目录创建功能验证脚本

验证目标：
1. 通过 ProjectService.create_project() 创建项目时，变更管理目录是否正确生成
2. _initialize_change_management() 方法的增强日志是否正常工作
3. diagnose_and_fix_change_management() 诊断修复功能是否正常

运行方式：
    cd d:\BaiduSyncdisk\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\02_在研项目\SW-2026-004_Python项目管理工具\03_主程序\01_主程序核心代码
    python verify_change_management_fix.py
"""
import os
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_create_project_with_change_management():
    """测试1: 创建项目并验证变更管理目录"""
    print("\n" + "=" * 70)
    print("Test 1: 创建项目并验证变更管理目录")
    print("=" * 70)

    from src.services.project_service import ProjectService
    from src.services.template_service import TemplateService

    # 初始化内置模板（确保数据库中有最新模板）
    print("\n📋 步骤1: 初始化内置模板...")
    TemplateService.initialize_builtin_templates()
    print("✅ 内置模板初始化完成")

    # 获取 TPL-SINGLE-PLC-001 模板
    print("\n📋 步骤2: 获取测试模板...")
    template = TemplateService.get_template("TPL-SINGLE-PLC-001")
    if not template:
        print("❌ 测试模板 TPL-SINGLE-PLC-001 不存在")
        return False
    print(f"✅ 获取到模板: {template.name} V{template.version}")

    # 创建临时目录用于测试
    test_base_path = os.path.join(tempfile.gettempdir(), f"test_chg_mgmt_{datetime.now().strftime('%Y%m%d%H%M%S')}")

    try:
        service = ProjectService()

        # 创建项目
        print(f"\n📋 步骤3: 创建测试项目...")
        print(f"   基础路径: {test_base_path}")

        project, error = service.create_project(
            business_line="DJ",
            name="变更管理测试项目",
            template_id="TPL-SINGLE-PLC-001",
            manager="测试人员",
            description="用于验证变更管理目录创建功能的测试项目",
            custom_path=test_base_path
        )

        if not project:
            print(f"❌ 项目创建失败: {error}")
            return False

        print(f"✅ 项目创建成功")
        print(f"   项目编号: {project.code}")
        print(f"   项目路径: {project.path}")

        # 验证变更管理目录结构
        print(f"\n📋 步骤4: 验证变更管理目录结构...")

        project_path = Path(project.path)
        chg_mgmt_path = project_path / "00_项目管理" / "04_变更管理"

        expected_structure = {
            "00_项目管理/04_变更管理": "directory",
            "00_项目管理/04_变更管理/01_变更单": "directory",
            "00_项目管理/04_变更管理/01_变更单/.gitkeep": "file",
            "00_项目管理/04_变更管理/04_变更记录": "directory",
            f"00_项目管理/04_变更管理/04_变更记录/041_{project.code}_版本变更台帐_CHG-V2.1.0.md": "file",
            "00_项目管理/04_变更管理/README.md": "file",
        }

        all_passed = True
        for rel_path, item_type in expected_structure.items():
            full_path = project_path / rel_path
            exists = full_path.is_dir() if item_type == "directory" else full_path.is_file()

            status = "✅" if exists else "❌"
            print(f"   {status} {rel_path} ({item_type})")

            if not exists:
                all_passed = False

        if all_passed:
            print(f"\n🎉 Test 1 通过! 所有变更管理目录和文件均已正确创建")
        else:
            print(f"\n⚠️ Test 1 部分失败: 存在缺失的目录或文件")

        return all_passed

    except Exception as e:
        print(f"\n❌ Test 1 异常: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # 清理测试数据
        if 'project' in locals() and project:
            try:
                service = ProjectService()
                service.delete_project(project.project_id, hard_delete=True, delete_local_files=False)
                print(f"\n🧹 已清理数据库记录: {project.code}")
            except Exception as cleanup_err:
                print(f"\n⚠️ 清理数据库记录失败: {cleanup_err}")

        if os.path.exists(test_base_path):
            try:
                shutil.rmtree(test_base_path, ignore_errors=True)
                print(f"🧹 已清理临时目录: {test_base_path}")
            except Exception as cleanup_err:
                print(f"⚠️ 清理临时目录失败: {cleanup_err}")


def test_diagnose_and_fix():
    """测试2: 诊断和修复功能"""
    print("\n" + "=" * 70)
    print("Test 2: 诊断和修复功能测试")
    print("=" * 70)

    from src.services.project_service import ProjectService
    from src.services.template_service import TemplateService

    # 初始化模板
    TemplateService.initialize_builtin_templates()

    # 创建一个故意缺少变更管理目录的项目
    test_base_path = os.path.join(tempfile.gettempdir(), f"test_fix_{datetime.now().strftime('%Y%m%d%H%M%S')}")

    try:
        service = ProjectService()

        # 先创建项目
        print(f"\n📋 步骤1: 创建测试项目...")
        project, error = service.create_project(
            business_line="DJ",
            name="诊断修复测试",
            template_id="TPL-SINGLE-PLC-001",
            custom_path=test_base_path
        )

        if not project:
            print(f"❌ 项目创建失败: {error}")
            return False

        print(f"✅ 项目创建成功: {project.code}")

        # 故意删除变更管理目录来模拟问题
        print(f"\n📋 步骤2: 模拟变更管理目录缺失...")
        chg_path = Path(project.path) / "00_项目管理" / "04_变更管理"
        if chg_path.exists():
            shutil.rmtree(chg_path)
            print(f"✅ 已删除变更管理目录: {chg_path}")

        # 运行诊断和修复
        print(f"\n📋 步骤3: 运行诊断和修复...")
        success, message, operations = service.diagnose_and_fix_change_management(project.project_id)

        print(f"\n诊断结果:")
        print(f"  状态: {'成功' if success else '部分成功/失败'}")
        print(f"  消息: {message}")
        print(f"\n执行的操作:")
        for op in operations:
            print(f"  - {op}")

        # 验证修复结果
        print(f"\n📋 步骤4: 验证修复结果...")
        if chg_path.exists():
            print(f"✅ 变更管理目录已恢复: {chg_path}")

            # 检查关键文件
            key_files = [
                "01_变更单/.gitkeep",
                f"04_变更记录/041_{project.code}_版本变更台帐_CHG-V2.1.0.md",
                "README.md"
            ]

            all_restored = True
            for file_rel in key_files:
                file_path = chg_path / file_rel
                if file_path.exists():
                    print(f"  ✅ {file_rel}")
                else:
                    print(f"  ❌ {file_rel} (仍缺失)")
                    all_restored = False

            if all_restored:
                print(f"\n🎉 Test 2 通过! 诊断和修复功能正常工作")
                return True
            else:
                print(f"\n⚠️ Test 2 部分通过: 部分文件未恢复")
                return False
        else:
            print(f"❌ 变更管理目录仍未存在")
            return False

    except Exception as e:
        print(f"\n❌ Test 2 异常: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # 清理
        if 'project' in locals() and project:
            try:
                service = ProjectService()
                service.delete_project(project.project_id, hard_delete=True, delete_local_files=False)
            except:
                pass

        if os.path.exists(test_base_path):
            try:
                shutil.rmtree(test_base_path, ignore_errors=True)
            except:
                pass


def main():
    """主测试入口"""
    print("=" * 70)
    print("变更管理目录创建功能验证")
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    results = []

    # 执行测试
    try:
        result1 = test_create_project_with_change_management()
        results.append(("Test 1: 创建项目并验证变更管理目录", result1))
    except Exception as e:
        print(f"\n❌ Test 1 执行异常: {e}")
        results.append(("Test 1: 创建项目并验证变更管理目录", False))

    try:
        result2 = test_diagnose_and_fix()
        results.append(("Test 2: 诊断和修复功能", result2))
    except Exception as e:
        print(f"\n❌ Test 2 执行异常: {e}")
        results.append(("Test 2: 诊断和修复功能", False))

    # 输出总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}: {test_name}")

    print(f"\n总计: {passed}/{total} 个测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！变更管理目录功能已修复。")
        return 0
    else:
        print(f"\n⚠️ 有 {total - passed} 个测试失败，请检查上方详细信息。")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
