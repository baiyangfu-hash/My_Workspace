# -*- coding: utf-8 -*-
"""
ConfigChecker单元测试模块

测试覆盖范围:
1. CONFIG_001: 必填字段完整性检查（name, description, version）
2. CONFIG_002: 项目名称格式验证
3. CONFIG_003: 版本号格式验证
4. CONFIG_004: libraries字段名正确性检查（重点：libraryDirectories错误用法）
5. CONFIG_005: 库路径类型检查（相对路径 vs 绝对路径）
6. CONFIG_006: 库路径有效性验证
7. CONFIG_007: 路径分隔符规范化检查
8. JSON解析错误处理
9. 边界条件和异常场景

运行方式:
    python -m pytest tests/test_config_checker.py -v

重点测试:
    - libraryDirectories错误字段名的检测
    - Windows环境下路径计算的正确性
    - 各种配置组合的完整覆盖
"""
import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch

# 导入被测模块
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.checkers.config_checker import ConfigChecker
from src.checkers.base_checker import Severity
from src.models.check_result import Violation


# ============================================================================
# 测试辅助函数和固定装置
# ============================================================================

def create_valid_config(
    name: str = "DJ-2026-005",
    description: str = "测试项目描述",
    version: str = "V1.0.0",
    libraries: list = None,
) -> str:
    """
    创建有效的.plc.json配置字符串

    Args:
        name: 项目名称
        description: 项目描述
        version: 版本号
        libraries: 库路径列表

    Returns:
        str: 格式化的JSON字符串
    """
    config = {
        "name": name,
        "description": description,
        "version": version,
    }
    if libraries is not None:
        config["libraries"] = libraries
    return json.dumps(config, ensure_ascii=False, indent=2)


@pytest.fixture
def checker():
    """创建ConfigChecker实例的fixture"""
    return ConfigChecker()


@pytest.fixture
def temp_project_dir():
    """创建临时项目目录结构的fixture"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir) / "test_project"
        project_path.mkdir()

        # 创建共享库目录结构
        shared_lib = Path(tmpdir) / "01_SharedLibraries" / "SysLib"
        shared_lib.mkdir(parents=True)

        # 在SysLib中创建一个标记文件
        (shared_lib / ".plc.json").write_text("{}")

        yield {
            "project_path": str(project_path),
            "shared_lib_path": str(shared_lib),
            "tmpdir": tmpdir,
        }


# ============================================================================
# 1. CONFIG_001 测试 - 必填字段完整性
# ============================================================================

class TestCONFIG001RequiredFields:
    """CONFIG_001: 必填字段完整性检查测试"""

    def test_all_required_fields_present(self, checker):
        """测试所有必填字段都存在时无违规"""
        config = create_valid_config()
        violations = checker.check(config)

        config_violations = [v for v in violations if v.rule_id == "CONFIG_001"]
        assert len(config_violations) == 0

    def test_missing_name_field(self, checker):
        """测试缺少name字段"""
        config = json.dumps({
            "description": "测试",
            "version": "V1.0.0",
        })
        violations = checker.check(config)

        config_violations = [v for v in violations if v.rule_id == "CONFIG_001"]
        assert len(config_violations) == 1
        assert "name" in config_violations[0].message

    def test_missing_description_field(self, checker):
        """测试缺少description字段"""
        config = json.dumps({
            "name": "DJ-2026-005",
            "version": "V1.0.0",
        })
        violations = checker.check(config)

        config_violations = [v for v in violations if v.rule_id == "CONFIG_001"]
        assert len(config_violations) == 1
        assert "description" in config_violations[0].message

    def test_missing_version_field(self, checker):
        """测试缺少version字段"""
        config = json.dumps({
            "name": "DJ-2026-005",
            "description": "测试",
        })
        violations = checker.check(config)

        config_violations = [v for v in violations if v.rule_id == "CONFIG_001"]
        assert len(config_violations) == 1
        assert "version" in config_violations[0].message

    def test_missing_all_required_fields(self, checker):
        """测试所有必填字段都缺失"""
        config = json.dumps({})
        violations = checker.check(config)

        config_violations = [v for v in violations if v.rule_id == "CONFIG_001"]
        assert len(config_violations) == 3  # name, description, version

    def test_empty_name_value(self, checker):
        """测试name字段值为空字符串"""
        config = json.dumps({
            "name": "",
            "description": "测试",
            "version": "V1.0.0",
        })
        violations = checker.check(config)

        config_violations = [v for v in violations if v.rule_id == "CONFIG_001"]
        assert len(config_violations) >= 1
        assert any("name" in v.message and "空" in v.message for v in config_violations)


# ============================================================================
# 2. CONFIG_002 测试 - 项目名称格式
# ============================================================================

class TestCONFIG002NameFormat:
    """CONFIG_002: 项目名称格式验证测试"""

    def test_valid_name_format(self, checker):
        """测试标准的项目名称格式"""
        config = create_valid_config(name="DJ-2026-005")
        violations = checker.check(config)

        name_violations = [v for v in violations if v.rule_id == "CONFIG_002"]
        assert len(name_violations) == 0

    def test_invalid_name_too_short(self, checker):
        """测试过短的项目编号"""
        config = create_valid_config(name="DJ-2026-05")  # 只有2位数字
        violations = checker.check(config)

        name_violations = [v for v in violations if v.rule_id == "CONFIG_002"]
        assert len(name_violations) == 1

    def test_invalid_name_lowercase(self, checker):
        """测试小写字母的项目名称"""
        config = create_valid_config(name="dj-2026-005")
        violations = checker.check(config)

        name_violations = [v for v in violations if v.rule_id == "CONFIG_002"]
        assert len(name_violations) == 1

    def test_invalid_name_no_hyphens(self, checker):
        """测试没有连字符的项目名称"""
        config = create_valid_config(name="DJ2026005")
        violations = checker.check(config)

        name_violations = [v for v in violations if v.rule_id == "CONFIG_002"]
        assert len(name_violations) == 1


# ============================================================================
# 3. CONFIG_003 测试 - 版本号格式
# ============================================================================

class TestCONFIG003VersionFormat:
    """CONFIG_003: 版本号格式验证测试"""

    def test_valid_version_format(self, checker):
        """测试标准的版本号格式"""
        config = create_valid_config(version="V1.0.0")
        violations = checker.check(config)

        ver_violations = [v for v in violations if v.rule_id == "CONFIG_003"]
        assert len(ver_violations) == 0

    def test_valid_version_with_large_numbers(self, checker):
        """测试大版本号"""
        config = create_valid_config(version="V10.20.30")
        violations = checker.check(config)

        ver_violations = [v for v in violations if v.rule_id == "CONFIG_003"]
        assert len(ver_violations) == 0

    def test_invalid_version_no_prefix(self, checker):
        """测试没有V前缀的版本号"""
        config = create_valid_config(version="1.0.0")
        violations = checker.check(config)

        ver_violations = [v for v in violations if v.rule_id == "CONFIG_003"]
        assert len(ver_violations) == 1

    def test_invalid_version_semver_style(self, checker):
        """测试语义化版本号风格（没有V）"""
        config = create_valid_config(version="1.2.3-beta")
        violations = checker.check(config)

        ver_violations = [v for v in violations if v.rule_id == "CONFIG_003"]
        assert len(ver_violations) == 1


# ============================================================================
# 4. CONFIG_004 测试 - libraries字段名正确性（重点测试！）
# ============================================================================

class TestCONFIG004LibrariesFieldName:
    """
    CONFIG_004: libraries字段名正确性检查

    这是关键测试！Siemens LSP只识别 'libraries' 字段，
    使用 'libraryDirectories' 会导致LSP静默忽略库配置。
    """

    def test_correct_libraries_field(self, checker):
        """测试使用正确的libraries字段名"""
        config = create_valid_config(libraries=["../01_SharedLibraries/SysLib"])
        violations = checker.check(config)

        field_violations = [v for v in violations if v.rule_id == "CONFIG_004"]
        assert len(field_violations) == 0

    def test_wrong_library_directories_field(self, checker):
        """
        【重点测试】使用错误的libraryDirectories字段名

        这是最常见的配置错误，会导致LSP无法加载库文件。
        必须确保此规则能准确捕获该问题。
        """
        config_dict = {
            "name": "DJ-2026-005",
            "description": "测试项目",
            "version": "V1.0.0",
            "libraryDirectories": ["../01_SharedLibraries/SysLib"],  # 错误的字段名！
        }
        config = json.dumps(config_dict)
        violations = checker.check(config)

        field_violations = [v for v in violations if v.rule_id == "CONFIG_004"]
        assert len(field_violations) == 1
        assert field_violations[0].severity == Severity.ERROR
        assert "libraryDirectories" in field_violations[0].message
        assert "libraries" in field_violations[0].suggestion

    def test_both_correct_and_wrong_field(self, checker):
        """测试同时存在正确和错误的字段名"""
        config_dict = {
            "name": "DJ-2026-005",
            "description": "测试项目",
            "version": "V1.0.0",
            "libraries": ["../correct/lib"],           # 正确的字段
            "libraryDirectories": ["../wrong/lib"],     # 错误的字段
        }
        config = json.dumps(config_dict)
        violations = checker.check(config)

        # 应该报告libraryDirectories的错误
        field_violations = [v for v in violations if v.rule_id == "CONFIG_004"]
        assert len(field_violations) == 1
        assert "libraryDirectories" in field_violations[0].message

    def test_empty_library_directories_array(self, checker):
        """测试空的libraryDirectories数组"""
        config_dict = {
            "name": "DJ-2026-005",
            "description": "测试项目",
            "version": "V1.0.0",
            "libraryDirectories": [],
        }
        config = json.dumps(config_dict)
        violations = checker.check(config)

        field_violations = [v for v in violations if v.rule_id == "CONFIG_004"]
        assert len(field_violations) == 1

    def test_code_snippet_in_violation(self, checker):
        """测试违规记录包含代码片段"""
        config_dict = {
            "name": "DJ-2026-005",
            "description": "测试",
            "version": "V1.0.0",
            "libraryDirectories": ["lib"],
        }
        config = json.dumps(config_dict)
        violations = checker.check(config)

        field_violations = [v for v in violations if v.rule_id == "CONFIG_004"]
        assert len(field_violations) == 1
        assert field_violations[0].code_snippet is not None
        assert "libraryDirectories" in field_violations[0].code_snippet


# ============================================================================
# 5. CONFIG_005 测试 - 库路径类型检查
# ============================================================================

class TestCONFIG005PathType:
    """CONFIG_005: 库路径类型检查测试"""

    def test_relative_path_accepted(self, checker):
        """测试相对路径被接受"""
        config = create_valid_config(libraries=["../../../01_SharedLibraries/SysLib"])
        violations = checker.check(config)

        path_type_violations = [v for v in violations if v.rule_id == "CONFIG_005"]
        assert len(path_type_violations) == 0

    def test_windows_absolute_path_rejected(self, checker):
        """测试Windows绝对路径被拒绝"""
        config = create_valid_config(libraries=["D:/SharedLibraries/SysLib"])
        violations = checker.check(config)

        path_type_violations = [v for v in violations if v.rule_id == "CONFIG_005"]
        assert len(path_type_violations) == 1
        assert "Windows绝对路径" in path_type_violations[0].message or "绝对路径" in path_type_violations[0].message

    def test_unix_absolute_path_rejected(self, checker):
        """测试Unix/Linux绝对路径被拒绝"""
        config = create_valid_config(libraries=["/usr/local/lib/syslib"])
        violations = checker.check(config)

        path_type_violations = [v for v in violations if v.rule_id == "CONFIG_005"]
        assert len(path_type_violations) == 1
        assert "Unix绝对路径" in path_type_violations[0].message or "绝对路径" in path_type_violations[0].message

    def test_multiple_paths_mixed_types(self, checker):
        """测试多个路径混合类型"""
        config = create_valid_config(libraries=[
            "../relative/lib",          # 正确
            "D:/absolute/lib",         # 错误
            "/unix/absolute",          # 错误
        ])
        violations = checker.check(config)

        path_type_violations = [v for v in violations if v.rule_id == "CONFIG_005"]
        assert len(path_type_violations) == 2  # 应该报告2个绝对路径

    def test_empty_libraries_list(self, checker):
        """测试空库列表不产生违规"""
        config = create_valid_config(libraries=[])
        violations = checker.check(config)

        path_type_violations = [v for v in violations if v.rule_id == "CONFIG_005"]
        assert len(path_type_violations) == 0


# ============================================================================
# 6. CONFIG_006 测试 - 库路径有效性验证
# ============================================================================

class TestCONFIG006PathValidity:
    """CONFIG_006: 库路径有效性验证测试"""

    def test_existing_relative_path(self, checker, temp_project_dir):
        """测试存在的相对路径"""
        project_path = temp_project_dir["project_path"]
        tmpdir = temp_project_dir["tmpdir"]

        # 创建.plc.json在项目目录中
        plc_json_dir = Path(project_path) / "02_PLC程序" / "通用ST程序及变量表"
        plc_json_dir.mkdir(parents=True)

        # 配置指向已存在的共享库
        relative_path = "../../../01_SharedLibraries/SysLib"
        config = create_valid_config(libraries=[relative_path])

        context = {"project_path": str(plc_json_dir)}
        violations = checker.check(config, file_path=str(plc_json_dir / ".plc.json"), context=context)

        validity_violations = [v for v in violations if v.rule_id == "CONFIG_006"]
        assert len(validity_violations) == 0

    def test_nonexistent_path(self, checker, temp_project_dir):
        """测试不存在的路径"""
        project_path = temp_project_dir["project_path"]

        config = create_valid_config(libraries=["../../nonexistent/library"])
        context = {"project_path": project_path}
        violations = checker.check(config, context=context)

        validity_violations = [v for v in violations if v.rule_id == "CONFIG_006"]
        assert len(validity_violations) == 1
        assert "不存在" in validity_violations[0].message

    def test_no_project_path_skips_check(self, checker):
        """测试未提供project_path时跳过此检查"""
        config = create_valid_config(libraries=["../../any/path"])
        violations = checker.check(config)  # 不提供context

        validity_violations = [v for v in violations if v.rule_id == "CONFIG_006"]
        assert len(validity_violations) == 0  # 应该跳过检查

    def test_windows_path_calculation(self, checker, temp_project_dir):
        """
        【重点测试】Windows环境下的路径计算

        验证在Windows系统中，正斜杠路径能被正确解析为实际路径。
        """
        project_path = temp_project_dir["project_path"]

        # 使用正斜杠的相对路径
        config = create_valid_config(libraries=["../../../01_SharedLibraries/SysLib"])
        context = {"project_path": project_path}

        violations = checker.check(config, context=context)

        validity_violations = [v for v in violations if v.rule_id == "CONFIG_006"]
        # 路径应该存在，所以不应该有违规
        assert len(validity_violations) == 0


# ============================================================================
# 7. CONFIG_007 测试 - 路径分隔符规范化
# ============================================================================

class TestCONFIG007PathSeparator:
    """CONFIG_007: 路径分隔符规范化检查测试"""

    def test_forward_slash_accepted(self, checker):
        """测试正斜杠被接受"""
        config = create_valid_config(libraries=["../relative/path/to/lib"])
        violations = checker.check(config)

        sep_violations = [v for v in violations if v.rule_id == "CONFIG_007"]
        assert len(sep_violations) == 0

    def test_backslash_warning(self, checker):
        """测试反斜杠产生警告"""
        config = create_valid_config(libraries=["..\\relative\\path\\to\\lib"])
        violations = checker.check(config)

        sep_violations = [v for v in violations if v.rule_id == "CONFIG_007"]
        assert len(sep_violations) == 1
        assert "反斜杠" in sep_violations[0].message
        assert sep_violations[0].severity == Severity.INFO  # 只是信息提示

    def test_unc_path_not_flagged(self, checker):
        """测试UNC路径不被标记（\\\\server\\share）"""
        config = create_valid_config(libraries=["\\\\server\\share\\lib"])
        violations = checker.check(config)

        sep_violations = [v for v in violations if v.rule_id == "CONFIG_007"]
        assert len(sep_violations) == 0  # UNC路径不应被标记

    def test_mixed_separators(self, checker):
        """测试混合分隔符"""
        config = create_valid_config(libraries=["path/to\\mixed/lib"])
        violations = checker.check(config)

        sep_violations = [v for v in violations if v.rule_id == "CONFIG_007"]
        assert len(sep_violations) == 1


# ============================================================================
# 8. JSON解析错误处理测试
# ============================================================================

class TestJSONParsingErrors:
    """JSON解析错误处理测试"""

    def test_invalid_json_syntax(self, checker):
        """测试无效的JSON语法"""
        invalid_json = "{name: 'DJ-2026-005'}"  # 缺少引号
        violations = checker.check(invalid_json)

        assert len(violations) >= 1
        assert violations[0].rule_id == "CONFIG_001"
        assert "JSON" in violations[0].message

    def test_trailing_comma(self, checker):
        """测试尾随逗号导致的JSON错误"""
        invalid_json = '{"name": "DJ-2026-005",}'  # 尾随逗号
        violations = checker.check(invalid_json)

        assert len(violations) >= 1
        assert "JSON" in violations[0].message

    def test_non_object_json(self, checker):
        """测试非对象类型的JSON"""
        invalid_json = '["array", "not", "object"]'
        violations = checker.check(invalid_json)

        obj_violations = [v for v in violations if v.rule_id == "CONFIG_001"]
        assert len(obj_violations) >= 1
        assert "对象" in obj_violations[0].message

    def test_empty_string_input(self, checker):
        """测试空字符串输入"""
        violations = checker.check("")

        assert len(violations) >= 1
        assert "JSON" in violations[0].message


# ============================================================================
# 9. 完整集成测试
# ============================================================================

class TestCompleteIntegration:
    """完整集成测试 - 验证真实场景"""

    def test_perfect_configuration(self, checker, temp_project_dir):
        """测试完美的配置文件（无任何违规）"""
        project_path = temp_project_dir["project_path"]

        config = create_valid_config(
            name="DJ-2026-005",
            description="边框缓存机 PLC 控制系统",
            version="V6.0.0",
            libraries=["../../../01_SharedLibraries/SysLib"],
        )

        context = {"project_path": project_path}
        violations = checker.check(config, file_path=str(Path(project_path) / ".plc.json"), context=context)

        assert len(violations) == 0, f"完美配置不应有违规，但发现: {[str(v) for v in violations]}"

    def test_real_world_bad_config(self, checker):
        """
        【重要】测试现实世界中的错误配置

        模拟新手常犯的所有典型错误：
        1. 使用 libraryDirectories（最常见错误）
        2. 使用绝对路径
        3. 使用反斜杠
        """
        bad_config = {
            "name": "dj-2026-005",              # 小写（CONFIG_002违规）
            "description": "",                   # 空描述（CONFIG_001违规）
            "version": "1.0.0",                 # 无V前缀（CONFIG_003违规）
            "libraryDirectories": [              # 错误字段名！（CONFIG_004违规）
                "D:\\SharedLib\\SysLib",        # 绝对路径+反斜杠（CONFIG_005, CONFIG_007违规）
            ],
        }

        violations = checker.check(json.dumps(bad_config))

        # 验证捕获到多种类型的违规
        rule_ids = {v.rule_id for v in violations}

        assert "CONFIG_001" in rule_ids  # 空描述
        assert "CONFIG_002" in rule_ids  # 小写名称
        assert "CONFIG_003" in rule_ids  # 版本格式
        assert "CONFIG_004" in rule_ids  # 错误字段名（最重要！）
        assert "CONFIG_005" in rule_ids  # 绝对路径
        assert "CONFIG_007" in rule_ids  # 反斜杠

        print(f"\n发现 {len(violations)} 个违规:")
        for v in sorted(violations, key=lambda x: x.rule_id):
            print(f"  [{v.severity.name}] {v.rule_id}: {v.message}")

    def test_dj_2026_000_reference_example(self, checker):
        """测试参考示例 DJ-2026-000 的配置文件"""
        # 基于实际读取到的 .plc.json 内容
        reference_config = json.dumps({
            "name": "DJ-2026-000",
            "description": "测试项目",
            "version": "1.0.0",
            "libraries": [],
        }, ensure_ascii=False)

        violations = checker.check(reference_config)

        # 这个配置应该是基本合规的（除了版本号可能不符合V前缀规范）
        critical_errors = [v for v in violations if v.severity == Severity.ERROR and v.rule_id != "CONFIG_003"]
        # 不应有ERROR级别的严重错误（CONFIG_003是WARNING）
        assert len(critical_errors) == 0, f"参考示例不应有严重错误: {[str(e) for e in critical_errors]}"

    def test_multi_library_configuration(self, checker, temp_project_dir):
        """测试多库配置场景"""
        project_path = temp_project_dir["project_path"]
        tmpdir = temp_project_dir["tmpdir"]

        # 创建第二个库目录
        app_lib = Path(tmpdir) / "01_SharedLibraries" / "AppLib"
        app_lib.mkdir(parents=True)
        (app_lib / ".plc.json").write_text("{}")

        config = create_valid_config(
            libraries=[
                "../../../01_SharedLibraries/SysLib",
                "../../../01_SharedLibraries/AppLib",
            ]
        )

        context = {"project_path": project_path}
        violations = checker.check(config, context=context)

        # 所有路径都应该有效
        validity_violations = [v for v in violations if v.rule_id == "CONFIG_006"]
        assert len(validity_violations) == 0


# ============================================================================
# 10. 边界条件测试
# ============================================================================

class TestEdgeCases:
    """边界条件和异常场景测试"""

    def test_none_context_handling(self, checker):
        """测试None值的context参数"""
        config = create_valid_config(libraries=["../some/path"])
        violations = checker.check(config, context=None)

        # 不应抛出异常
        assert isinstance(violations, list)

    def test_unicode_in_description(self, checker):
        """测试描述中的Unicode字符"""
        config = create_valid_config(description="边框缓存机 PLC 控制系统 - 中文测试")
        violations = checker.check(config)

        desc_violations = [v for v in violations if v.rule_id == "CONFIG_001"]
        assert len(desc_violations) == 0

    def test_very_long_library_path(self, checker):
        """测试超长的库路径"""
        long_path = "../" + "very/long/path/" * 20 + "final"
        config = create_valid_config(libraries=[long_path])
        violations = checker.check(config)

        # 不应崩溃
        assert isinstance(violations, list)

    def test_special_characters_in_path(self, checker):
        """测试路径中的特殊字符"""
        config = create_valid_config(libraries=["../path-with-dashes_and_underscores/SysLib"])
        violations = checker.check(config)

        # 特殊字符路径本身不是错误
        special_violations = [v for v in violations if v.rule_id in ["CONFIG_005", "CONFIG_007"]]
        assert len(special_violations) == 0

    def test_get_all_rule_ids(self, checker):
        """测试获取所有规则ID的方法"""
        rule_ids = checker.get_all_rule_ids()

        assert len(rule_ids) == 7
        assert "CONFIG_001" in rule_ids
        assert "CONFIG_007" in rule_ids

    def test_get_rule_descriptions(self, checker):
        """测试获取规则描述的方法"""
        desc = checker.get_rule_description("CONFIG_004")
        assert desc is not None
        assert "libraries" in desc.lower() or "字段" in desc

        invalid_desc = checker.get_rule_description("NONEXISTENT")
        assert invalid_desc is None


# ============================================================================
# 11. 违规记录完整性测试
# ============================================================================

class TestViolationRecordIntegrity:
    """验证Violation记录的完整性和准确性"""

    def test_violation_contains_suggestion(self, checker):
        """测试违规记录包含修复建议"""
        config_dict = {
            "name": "DJ-2026-005",
            "description": "测试",
            "version": "V1.0.0",
            "libraryDirectories": ["lib"],
        }
        violations = checker.check(json.dumps(config_dict))

        config_004 = [v for v in violations if v.rule_id == "CONFIG_004"][0]
        assert config_004.suggestion is not None
        assert len(config_004.suggestion) > 0

    def test_violation_file_path_preserved(self, checker):
        """测试文件路径信息被保留"""
        test_file = "/project/.plc.json"
        config = create_valid_config()
        violations = checker.check(config, file_path=test_file)

        for v in violations:
            assert v.file_path == test_file

    def test_violation_severity_levels(self, checker):
        """测试不同规则的严重级别设置正确"""
        # CONFIG_004 应该是 ERROR
        config_err = {"name": "T", "description": "T", "version": "V1.0.0", "libraryDirectories": []}
        v_err = checker.check(json.dumps(config_err))
        assert any(v.rule_id == "CONFIG_004" and v.severity == Severity.ERROR for v in v_err)

        # CONFIG_007 应该是 INFO
        config_info = create_valid_config(libraries=["path\\with\\backslash"])
        v_info = checker.check(config_info)
        assert any(v.rule_id == "CONFIG_007" and v.severity == Severity.INFO for v in v_info)


# ============================================================================
# 主入口
# ============================================================================

if __name__ == "__main__":
    # 直接运行测试
    pytest.main([__file__, "-v", "--tb=short", "-x"])
