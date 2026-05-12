"""
新模板可用性测试脚本
测试 S001 和 M001 模板的项目创建功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.template_service import TemplateService
from src.services.project_service import ProjectService
import tempfile
import shutil

def test_template_availability(template_id, template_name, project_name):
    """测试指定模板的可用性和项目创建功能"""
    print(f"\n{'='*70}")
    print(f"测试模板: {template_id} ({template_name})")
    print(f"{'='*70}\n")

    # 1. 验证模板存在且可获取
    print(f"1. 验证模板存在性...")
    template = TemplateService.get_template(template_id)
    if not template:
        print(f"   ❌ 失败：模板 {template_id} 不存在")
        return False

    print(f"   ✅ 模板存在:")
    print(f"      - ID: {template.template_id}")
    print(f"      - 名称: {template.name}")
    print(f"      - 版本: {template.version}")
    print(f"      - 内置: {'是' if template.is_builtin else '否'}")

    # 2. 获取模板结构定义
    print(f"\n2. 获取模板结构...")
    try:
        structure = template.structure
        if not structure:
            print(f"   ❌ 失败：模板结构为空")
            return False

        # structure 是一个 list，每个元素是 dict（包含 path, required, description）
        if isinstance(structure, list):
            dir_count = len(structure)
            print(f"   ✅ 模板结构已加载 (包含 {dir_count} 个目录定义)")

            # 检查是否包含变更管理目录
            dirs = [d.get('path', '') for d in structure if isinstance(d, dict)]
            has_change_mgmt = any('04_变更管理' in d for d in dirs)

            if has_change_mgmt:
                print(f"   ✅ 包含 04_变更管理 目录")
                # 列出变更管理相关的目录
                change_dirs = [d for d in dirs if '04_变更管理' in d]
                for cd in change_dirs:
                    print(f"      - {cd}")
            else:
                print(f"   ⚠️ 未找到 04_变更管理 目录")
        else:
            print(f"   ⚠️ 结构格式异常: {type(structure)}")

    except Exception as e:
        print(f"   ❌ 获取模板结构失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 3. 测试项目创建（在临时目录）
    print(f"\n3. 测试项目创建...")

    # 创建临时目录作为项目根目录
    temp_base = tempfile.mkdtemp(prefix=f'test_{template_id}_')
    project_path = os.path.join(temp_base, project_name)

    try:
        # 使用 ProjectService 创建项目（注意：需要 business_line 参数）
        project, error_msg = ProjectService.create_project(
            business_line='DJ',  # 设备业务线
            name=project_name,
            template_id=template_id,
            description=f'验证测试项目 - {template_name}',
            custom_path=project_path  # 使用 custom_path 而不是 base_path
        )

        if not project:
            print(f"   ❌ 项目创建失败: {error_msg}")
            shutil.rmtree(temp_base, ignore_errors=True)
            return False

        print(f"   ✅ 项目创建成功:")
        print(f"      - 项目ID: {project.project_id}")
        print(f"      - 项目名称: {project.name}")
        print(f"      - 项目路径: {project_path}")

        # 4. 验证生成的目录结构
        print(f"\n4. 验证生成的目录结构...")

        if not os.path.exists(project_path):
            print(f"   ❌ 项目目录不存在: {project_path}")
            shutil.rmtree(temp_base, ignore_errors=True)
            return False

        # 列出顶层目录
        top_level = os.listdir(project_path)
        print(f"   顶层目录: {top_level}")

        # 检查关键目录是否存在
        pm_dir = os.path.join(project_path, '00_项目管理')
        if os.path.exists(pm_dir):
            print(f"   ✅ 00_项目管理/ 目录存在")

            change_mgmt_dir = os.path.join(pm_dir, '04_变更管理')
            if os.path.exists(change_mgmt_dir):
                print(f"   ✅ 04_变更管理/ 目录存在")

                # 列出变更管理子目录
                change_subdirs = os.listdir(change_mgmt_dir)
                print(f"      子目录: {change_subdirs}")
            else:
                print(f"   ⚠️ 04_变更管理/ 目录不存在")
        else:
            print(f"   ⚠️ 00_项目管理/ 目录不存在")

        # 统计总文件和目录数
        total_items = sum(len(dirpath[2]) for dirpath in os.walk(project_path))
        print(f"\n   📊 项目统计:")
        print(f"      - 总文件/目录数: {total_items}")
        print(f"      - 项目路径: {project_path}")

        print(f"\n   🎉 模板 {template_id} 测试完全通过！")
        return True

    except Exception as e:
        print(f"   ❌ 项目创建过程出错: {e}")
        import traceback
        traceback.print_exc()
        shutil.rmtree(temp_base, ignore_errors=True)
        return False

def main():
    """主测试函数"""
    print("=" * 70)
    print("新模板可用性测试 - S001 & M001")
    print("=" * 70)

    results = {}

    # 测试 S001 模板
    results['S001'] = test_template_availability(
        template_id='TPL-SINGLE-PLC-S001',
        template_name='小型单机设备(PLC+HMI)',
        project_name='验证测试-小型PLC项目'
    )

    # 测试 M001 模板
    results['M001'] = test_template_availability(
        template_id='TPL-SINGLE-PLC-M001',
        template_name='中大型单机设备(PLC+HMI)',
        project_name='验证测试-中大型PLC项目'
    )

    # 输出最终结果
    print("\n" + "=" * 70)
    print("最终测试结果汇总")
    print("=" * 70)

    for template_key, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{template_key} 模板: {status}")

    all_passed = all(results.values())
    print()

    if all_passed:
        print("🎉 所有新模板测试通过！S001 和 M001 均可正常使用。")
        return 0
    else:
        print("⚠️ 部分测试失败，需要排查问题。")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
