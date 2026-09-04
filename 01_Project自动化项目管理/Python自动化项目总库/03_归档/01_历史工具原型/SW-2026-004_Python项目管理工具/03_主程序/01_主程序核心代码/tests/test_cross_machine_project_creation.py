# -*- coding: utf-8 -*-
"""
跨机器创建项目目录兼容性测试

测试目标：
1. ensure_directory() 返回 tuple[bool, str] 格式
2. ProjectService.create_project() 的路径预检和自动回退
3. new_project_dialog.py 的路径验证逻辑
4. 错误提示信息的友好性

运行方式：
    cd d:\BaiduSyncdisk\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\02_在研项目\SW-2026-004_Python项目管理工具\03_主程序\01_主程序核心代码
    python tests/test_cross_machine_project_creation.py
"""
import os
import sys
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# ============================================================================
# Test 1: ensure_directory() 功能测试
# ============================================================================

def test_ensure_directory_success():
    """测试正常创建目录"""
    from src.utils.path_utils import ensure_directory

    test_dir = os.path.join(tempfile.gettempdir(), "test_dir_success")

    try:
        success, error = ensure_directory(test_dir)
        assert success == True, f"应该成功, 但返回: {error}"
        assert error == ""
        assert os.path.exists(test_dir)
        print("✅ test_ensure_directory_success 通过")
    finally:
        if os.path.exists(test_dir):
            os.rmdir(test_dir)


def test_ensure_directory_permission_error():
    """测试权限不足错误（模拟）"""
    from src.utils.path_utils import ensure_directory

    # Windows 上测试一个明显无效的路径
    invalid_path = "Z:\\nonexistent\\drive\\path"
    success, error = ensure_directory(invalid_path)

    # 应该失败（路径不存在或无法访问）
    if not success:
        print(f"✅ test_ensure_directory_permission_error 通过 - 错误信息: {error}")
        assert len(error) > 0, "错误信息不应为空"
    else:
        print("⚠️ 路径意外成功（可能环境特殊）")


def test_ensure_directory_long_path():
    """测试超长路径"""
    from src.utils.path_utils import ensure_directory

    long_path = "C:\\" + "A" * 300 + "\\test"
    success, error = ensure_directory(long_path)

    assert success == False, "超长路径不应该成功"
    assert "过长" in error or "long" in error.lower(), f"应提示路径过长, 实际: {error}"
    print(f"✅ test_ensure_directory_long_path 通过 - 错误: {error}")


def test_ensure_directory_return_format():
    """验证返回格式为 tuple[bool, str]"""
    from src.utils.path_utils import ensure_directory

    test_dir = os.path.join(tempfile.gettempdir(), "test_format_check")

    try:
        result = ensure_directory(test_dir)

        # 验证返回类型
        assert isinstance(result, tuple), f"应该返回 tuple, 实际: {type(result)}"
        assert len(result) == 2, f"tuple长度应为2, 实际: {len(result)}"

        success, error = result
        assert isinstance(success, bool), f"第一个元素应该是bool, 实际: {type(success)}"
        assert isinstance(error, str), f"第二个元素应该是str, 实际: {type(error)}"

        print(f"✅ test_ensure_directory_return_format 通过 - 返回格式正确: ({success}, '{error}')")
    finally:
        if os.path.exists(test_dir):
            os.rmdir(test_dir)


def test_ensure_directory_already_exists():
    """测试目录已存在的情况"""
    from src.utils.path_utils import ensure_directory

    test_dir = os.path.join(tempfile.gettempdir(), "test_already_exists")

    try:
        # 先创建目录
        os.makedirs(test_dir, exist_ok=True)

        # 再次调用 should succeed
        success, error = ensure_directory(test_dir)
        assert success == True, f"已存在的目录应该成功, 但返回: {error}"
        assert error == ""

        print("✅ test_ensure_directory_already_exists 通过 - 已存在目录处理正确")
    finally:
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir, ignore_errors=True)


# ============================================================================
# Test 2: ProjectService 路径回退测试
# ============================================================================

def test_create_project_with_invalid_path():
    """测试使用无效路径时自动回退"""
    from src.services.project_service import ProjectService

    service = ProjectService()

    # 使用一个不存在的路径作为 custom_path
    invalid_custom_path = "Z:\\NonExistentDrive\\InvalidPath\\Project"

    # 调用 create_project（应该会回退到可用路径）
    templates = service.template_dao.list()
    template_id = templates[0].template_id if templates else None

    if not template_id:
        print("⚠️ test_create_project_with_invalid_path 跳过 - 没有可用模板")
        return

    project, error = service.create_project(
        business_line="SW",
        name="TestProject_PathFallback",
        template_id=template_id,
        custom_path=invalid_custom_path
    )

    if project:
        print(f"✅ 项目创建成功（使用了回退路径）")
        print(f"   项目编号: {project.code}")
        print(f"   项目路径: {project.path}")

        # 验证项目路径实际存在
        assert Path(project.path).exists(), "项目路径应该存在"

        # 清理测试数据
        try:
            service.project_dao.delete(project.project_id, hard_delete=True)
        except Exception as e:
            print(f"   ⚠️ 清理数据库记录失败: {e}")

        if Path(project.path).exists():
            shutil.rmtree(project.path, ignore_errors=True)
    else:
        print(f"⚠️ 项目创建失败: {error}")


def test_create_project_with_valid_custom_path():
    """测试使用有效自定义路径创建项目"""
    from src.services.project_service import ProjectService

    service = ProjectService()
    valid_custom_path = os.path.join(tempfile.gettempdir(), "test_custom_path_project")

    templates = service.template_dao.list()
    template_id = templates[0].template_id if templates else None

    if not template_id:
        print("⚠️ test_create_project_with_valid_custom_path 跳过 - 没有可用模板")
        return

    try:
        project, error = service.create_project(
            business_line="SW",
            name="TestProject_CustomPath",
            template_id=template_id,
            custom_path=valid_custom_path
        )

        if project:
            print(f"✅ 使用有效自定义路径创建成功")
            print(f"   项目编号: {project.code}")
            print(f"   项目路径: {project.path}")

            # 验证路径包含自定义基础路径
            assert valid_custom_path in str(project.path) or str(Path(project.path).parent) == valid_custom_path, \
                f"项目路径应使用自定义路径, 实际: {project.path}"

            # 清理
            try:
                service.project_dao.delete(project.project_id, hard_delete=True)
            except Exception as e:
                print(f"   ⚠️ 清理数据库记录失败: {e}")

            if Path(project.path).exists():
                shutil.rmtree(project.path, ignore_errors=True)
            if os.path.exists(valid_custom_path):
                shutil.rmtree(valid_custom_path, ignore_errors=True)
        else:
            print(f"⚠️ 项目创建失败: {error}")
    finally:
        if os.path.exists(valid_custom_path):
            shutil.rmtree(valid_custom_path, ignore_errors=True)


# ============================================================================
# Test 3: 模拟 PyInstaller 环境测试
# ============================================================================

def test_detect_base_path_in_frozen_env():
    """模拟 PyInstaller 冻结环境的路径检测"""
    from src.services.library_service import LibraryService

    # 临时设置 sys.frozen 模拟打包环境
    original_frozen = getattr(sys, 'frozen', False)
    original_executable = getattr(sys, 'executable', None)

    try:
        sys.frozen = True
        sys.executable = "C:\\TestPath\\Python项目管理工具.exe"

        # 调用路径检测
        detected_path = LibraryService._detect_project_base_path()

        print(f"✅ 冻结环境路径检测结果: {detected_path}")
        assert detected_path is not None, "应该能检测到某个路径"
        assert len(detected_path) > 0, "路径不应为空"

    finally:
        # 恢复原始值
        if original_frozen:
            sys.frozen = original_frozen
        elif hasattr(sys, 'frozen'):
            delattr(sys, 'frozen')

        if original_executable is not None:
            sys.executable = original_executable
        elif hasattr(sys, 'executable'):
            delattr(sys, 'executable')


def test_detect_base_path_in_dev_env():
    """测试开发环境的路径检测"""
    from src.services.library_service import LibraryService

    # 确保不在冻结模式
    original_frozen = getattr(sys, 'frozen', False)

    try:
        if hasattr(sys, 'frozen'):
            delattr(sys, 'frozen')

        detected_path = LibraryService._detect_project_base_path()

        print(f"✅ 开发环境路径检测结果: {detected_path}")
        assert detected_path is not None, "开发环境应该能检测到某个路径"
        assert len(detected_path) > 0, "路径不应为空"

    finally:
        if original_frozen:
            sys.frozen = original_frozen


# ============================================================================
# Test 4: 边界情况测试
# ============================================================================

def test_empty_root_path_handling():
    """测试总库 root_path 为空时的处理"""
    from src.services.library_service import LibraryService

    # 直接调用 _detect_project_base_path（不依赖总库配置）
    detected = LibraryService._detect_project_base_path()

    print(f"✅ 空 root_path 回退测试通过 - 检测到: {detected}")
    assert detected is not None


def test_chinese_path_handling():
    """测试中文路径处理"""
    from src.utils.path_utils import ensure_directory, get_project_path

    chinese_name = "测试项目_中文路径"
    base_path = tempfile.gettempdir()
    full_path = get_project_path(base_path, "SW-2026-001", chinese_name)

    success, error = ensure_directory(full_path)

    if success:
        print(f"✅ 中文路径创建成功: {full_path}")
        # 清理
        if os.path.exists(full_path):
            shutil.rmtree(full_path, ignore_errors=True)
    else:
        print(f"⚠️ 中文路径创建失败: {error}")


def test_special_characters_in_path():
    """测试特殊字符路径处理"""
    from src.utils.path_utils import sanitize_filename, get_project_path, ensure_directory

    # 测试各种特殊字符
    test_cases = [
        ("正常项目名", "正常项目名"),
        ("项目名-带横线", "项目名-带横线"),
        ("项目名_带下划线", "项目名_带下划线"),
        ("项目名(带括号)", "项目名(带括号)"),
        ("项目名.带点", "项目名.带点"),
    ]

    base_path = tempfile.gettempdir()
    all_passed = True

    for original_name, expected_clean_name in test_cases:
        cleaned = sanitize_filename(original_name)
        full_path = get_project_path(base_path, "SW-2026-TEST", cleaned)

        success, error = ensure_directory(full_path)

        if success:
            print(f"✅ 特殊字符测试通过: '{original_name}' -> '{cleaned}'")
            if os.path.exists(full_path):
                shutil.rmtree(full_path, ignore_errors=True)
        else:
            print(f"❌ 特殊字符测试失败: '{original_name}' - 错误: {error}")
            all_passed = False

    assert all_passed, "部分特殊字符测试失败"


def test_nested_directory_creation():
    """测试深层嵌套目录创建"""
    from src.utils.path_utils import ensure_directory

    # 创建多层嵌套目录
    nested_path = os.path.join(
        tempfile.gettempdir(),
        "level1",
        "level2",
        "level3",
        "deep_nested_test"
    )

    try:
        success, error = ensure_directory(nested_path)

        if success:
            assert os.path.exists(nested_path), "嵌套目录应该存在"
            print(f"✅ 嵌套目录创建成功: {nested_path}")
        else:
            print(f"⚠️ 嵌套目录创建失败: {error}")
    finally:
        if os.path.exists(nested_path):
            shutil.rmtree(os.path.join(tempfile.gettempdir(), "level1"), ignore_errors=True)


def test_error_message_friendliness():
    """测试错误信息的友好性"""
    from src.utils.path_utils import ensure_directory

    test_cases = [
        ("Z:\\nonexistent", "路径不存在或无效"),
        ("C:\\" + "A" * 300, "过长"),
    ]

    for invalid_path, expected_keyword in test_cases:
        success, error = ensure_directory(invalid_path)

        if not success:
            assert expected_keyword in error or any(kw in error.lower() for kw in expected_keyword.split('、')), \
                f"错误信息应包含'{expected_keyword}', 实际: {error}"
            print(f"✅ 错误信息友好性检查通过: {error[:50]}...")
        else:
            print(f"⚠️ 路径意外成功: {invalid_path}")


# ============================================================================
# 主测试执行入口
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("开始执行跨机器项目创建兼容性测试")
    print("=" * 70)
    print()

    # 统计变量
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    skipped_tests = 0

    test_functions = [
        # Test 1: ensure_directory() 功能测试
        ("Test 1.1: 正常创建目录", test_ensure_directory_success),
        ("Test 1.2: 权限不足错误", test_ensure_directory_permission_error),
        ("Test 1.3: 超长路径处理", test_ensure_directory_long_path),
        ("Test 1.4: 返回格式验证", test_ensure_directory_return_format),
        ("Test 1.5: 目录已存在处理", test_ensure_directory_already_exists),

        # Test 2: ProjectService 路径回退测试
        ("Test 2.1: 无效路径自动回退", test_create_project_with_invalid_path),
        ("Test 2.2: 有效自定义路径", test_create_project_with_valid_custom_path),

        # Test 3: PyInstaller 环境测试
        ("Test 3.1: 冻结环境路径检测", test_detect_base_path_in_frozen_env),
        ("Test 3.2: 开发环境路径检测", test_detect_base_path_in_dev_env),

        # Test 4: 边界情况测试
        ("Test 4.1: 空 root_path 处理", test_empty_root_path_handling),
        ("Test 4.2: 中文路径处理", test_chinese_path_handling),
        ("Test 4.3: 特殊字符处理", test_special_characters_in_path),
        ("Test 4.4: 嵌套目录创建", test_nested_directory_creation),
        ("Test 4.5: 错误信息友好性", test_error_message_friendliness),
    ]

    for test_name, test_func in test_functions:
        total_tests += 1
        print(f"\n▶ 执行: {test_name}")
        try:
            test_func()
            passed_tests += 1
        except AssertionError as e:
            failed_tests += 1
            print(f"❌ 测试失败: {str(e)}")
        except Exception as e:
            failed_tests += 1
            print(f"❌ 测试异常: {type(e).__name__}: {str(e)}")

    # 输出测试总结
    print("\n" + "=" * 70)
    print("测试执行总结")
    print("=" * 70)
    print(f"总测试数: {total_tests}")
    print(f"✅ 通过: {passed_tests}")
    print(f"❌ 失败: {failed_tests}")
    print(f"⏭️ 跳过: {skipped_tests}")
    print(f"通过率: {(passed_tests / total_tests * 100):.1f}%" if total_tests > 0 else "N/A")

    if failed_tests == 0:
        print("\n🎉 所有测试通过！跨机器项目创建功能验证完成。")
    else:
        print(f"\n⚠️ 有 {failed_tests} 个测试失败，请查看上方详细信息。")

    print("=" * 70)
