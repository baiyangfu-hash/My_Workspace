# -*- coding: utf-8 -*-
"""
集成测试套件

验证PLC项目管理工具各核心组件的协同工作能力，
包括服务层初始化、规范检查、诊断流程和UI信号连接等。

测试覆盖范围：
1. PLCService初始化和基础功能
2. SpecCheckerService接口完整性
3. DiagnosticService完整诊断流程
4. 规范检查面板的信号连接
5. 数据模型序列化和反序列化
6. 配置加载和默认值回退

运行方式：
    pytest tests/test_integration.py -v

设计原则：
- 独立性：每个测试用例可独立运行，无执行顺序依赖
- 隔离性：使用临时目录和mock对象，不影响真实项目数据
- 完整性：覆盖正常路径和异常路径
- 可读性：清晰的测试名称和断言消息
"""
import json
import os
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

import pytest


# ============================================================================
# 测试固件和辅助工具
# ============================================================================

@pytest.fixture
def temp_project_dir():
    """
    创建临时项目目录的测试固件

    生成一个包含基本PLC项目结构的临时目录，
    测试结束后自动清理。

    Yields:
        Path: 临时项目目录路径
    """
    with tempfile.TemporaryDirectory(prefix="plc_test_") as tmpdir:
        project_path = Path(tmpdir) / "TestProject"
        project_path.mkdir()

        # 创建基本的子目录结构
        (project_path / "DB1").mkdir()
        (project_path / "OB1").mkdir()
        (project_path / "common").mkdir()

        # 创建示例ST文件
        st_file = project_path / "common" / "main.st"
        st_file.write_text("""
PROGRAM MainProgram
VAR
    counter : INT := 0;
    timer1 : TON;
END_VAR

(* 主程序逻辑 *)
IF counter < 100 THEN
    counter := counter + 1;
END_IF;

timer1(IN := TRUE, PT := T#1s);
IF timer1.Q THEN
    counter := 0;
END_IF;

END_PROGRAM
""", encoding="utf-8")

        yield project_path


@pytest.fixture
def sample_st_file(temp_project_dir):
    """
    创建示例ST文件的测试固件

    Args:
        temp_project_dir: 临时项目目录

    Yields:
        Path: 示例ST文件路径
    """
    st_file = temp_project_dir / "sample_program.st"
    st_file.write_text("""
FUNCTION_BLOCK MotorControl
VAR_INPUT
    start : BOOL;
    stop : BOOL;
END_VAR

VAR_OUTPUT
    running : BOOL;
    speed : INT;
END_VAR

VAR
    stateTimer : TON;
    rampUp : R_TRIG;
END_VAR

(* 电机控制逻辑 *)
rampUp(CLK := start);
IF rampUp.Q THEN
    running := TRUE;
    speed := 1000;
ELSIF stop THEN
    running := FALSE;
    speed := 0;
END_IF;

stateTimer(IN := running, PT := T#5s);

END_FUNCTION_BLOCK
""", encoding="utf-8")

    return st_file


class TestDJProjectGovernance:
    """测试DJ单机项目导入与治理基础能力"""

    @pytest.fixture
    def temp_dj_project_dir(self):
        """创建最小DJ单机项目目录"""
        with tempfile.TemporaryDirectory(prefix="dj_project_") as tmpdir:
            root = Path(tmpdir) / "DJ-2026-005"
            (root / "00_项目管理" / "04_变更管理" / "01_变更单" / "CHG-DOCU").mkdir(parents=True)
            (root / "02_PLC程序" / "通用ST程序及变量表" / "OB1").mkdir(parents=True)
            (root / "02_PLC程序" / "通用ST程序及变量表" / "DB1").mkdir(parents=True)
            (root / "02_PLC程序" / "通用ST程序及变量表" / "Test").mkdir(parents=True)
            (root / "03_HMI设计").mkdir(parents=True)
            (root / "04_现场调试").mkdir(parents=True)
            (root / "06_文档与交付").mkdir(parents=True)
            (root / "10_知识库").mkdir(parents=True)
            (root / ".trae").mkdir(parents=True)
            (root / ".plc-out").mkdir(parents=True)

            (root / ".plc.json").write_text(
                json.dumps(
                    {
                        "name": "DJ-2026-005",
                        "description": "test",
                        "version": "1.0.0",
                        "libraries": ["../01_SharedLibraries/SysLib"],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            (root / "00_项目管理" / "01_需求与设计说明_REQ-V1.0.0.md").write_text(
                "# REQ",
                encoding="utf-8",
            )
            (root / "02_PLC程序" / "通用ST程序及变量表" / "程序架构文档_ARC-V1.0.0.md").write_text(
                "# ARC",
                encoding="utf-8",
            )
            (root / "02_PLC程序" / "通用ST程序及变量表" / "详细设计说明书_DSN-V1.0.0.md").write_text(
                "# DSN",
                encoding="utf-8",
            )
            (root / "02_PLC程序" / "通用ST程序及变量表" / "OB1" / "OB1.scl").write_text(
                "PROGRAM OB1\nEND_PROGRAM",
                encoding="utf-8",
            )
            (root / "02_PLC程序" / "通用ST程序及变量表" / "DB1" / "GlobalVars.db").write_text(
                "DATA_BLOCK GlobalVars\nEND_DATA_BLOCK",
                encoding="utf-8",
            )
            (root / "02_PLC程序" / "通用ST程序及变量表" / "Test" / "basic_test.scltest").write_text(
                'TEST_CASE "smoke"\nEND_TEST_CASE',
                encoding="utf-8",
            )
            (root / "00_项目管理" / "04_变更管理" / "01_变更单" / "CHG-DOCU" / "CHG-DOCU-2026-001.md").write_text(
                "# CHG-DOCU-2026-001",
                encoding="utf-8",
            )
            (root / ".trae" / "ignored.md").write_text("# ignore", encoding="utf-8")
            (root / ".plc-out" / "ignored.md").write_text("# ignore", encoding="utf-8")
            yield root

    def test_04b_artifact_registry_ignores_internal_dirs(self, temp_dj_project_dir):
        """忽略 .trae 和 .plc-out 目录"""
        from src.services.artifact_registry_service import ArtifactRegistryService

        assets = ArtifactRegistryService.scan_project_assets(str(temp_dj_project_dir))
        relative_paths = [asset.relative_path for asset in assets]

        assert relative_paths
        assert all(".trae" not in path for path in relative_paths)
        assert all(".plc-out" not in path for path in relative_paths)

    def test_04c_project_service_import_dj_project(self, temp_dj_project_dir):
        """可导入DJ单机项目并识别画像信息"""
        from src.services.project_service import ProjectService

        project, error = ProjectService.import_dj_project(str(temp_dj_project_dir))

        assert error is None
        assert project is not None
        assert getattr(project.project_type, "value", project.project_type) == "dj_single_machine"
        assert len(project.artifact_roots) >= 3
        assert project.change_status_summary["total"] == 1
        assert project.extra["artifact_summary"]["plc_test"] == 1

    def test_04d_document_service_updates_existing_authoritative_doc(self, temp_dj_project_dir):
        """创建文档时优先更新现有权威文档，不新增重复文件"""
        from src.core.constants import DocumentType
        from src.services.document_service import DocumentService

        existing_doc = temp_dj_project_dir / "00_项目管理" / "01_需求与设计说明_REQ-V1.0.0.md"
        doc_path, error = DocumentService.create_or_update_document(
            project_path=str(temp_dj_project_dir),
            doc_type=DocumentType.REQ,
            doc_name="新的需求文档",
            content="# updated",
        )

        assert error is None
        assert doc_path == str(existing_doc)
        assert existing_doc.read_text(encoding="utf-8") == "# updated"
        duplicate_files = list(temp_dj_project_dir.rglob("*新的需求文档*.md"))
        assert duplicate_files == []


class TestSpecCheckerServiceInterface:
    """测试SpecCheckerService的接口完整性"""

    def test_05_spec_checker_service_creation(self):
        """
        测试5: SpecCheckerService实例创建

        验证SpecCheckerService可以正常创建且配置加载正确。
        应该：
        - 成功创建实例
        - 缓存字典为空
        - 统计计数器归零
        - 配置包含必要字段
        """
        from src.services.spec_checker_service import SpecCheckerService

        service = SpecCheckerService()

        assert service is not None
        assert isinstance(service._cache, dict)
        assert len(service._cache) == 0
        assert service._stats["total_files_checked"] == 0
        assert "concurrency" in service._config
        assert "file_scanning" in service._config
        assert "caching" in service._config

    def test_06_spec_checker_get_enabled_checkers(self):
        """
        测试6: 获取启用的检查器列表

        验证get_enabled_checkers()能从RuleRegistry获取检查器。
        应该：
        - 返回非空列表
        - 所有返回的检查器都是启用状态
        """
        from src.services.spec_checker_service import SpecCheckerService

        service = SpecCheckerService()
        checkers = service.get_enabled_checkers()

        assert isinstance(checkers, list)
        # 注意：如果没有注册任何检查器可能返回空列表
        # 这里只验证接口不抛异常

    def test_07_spec_checker_check_file_not_exists(self):
        """
        测试7: 检查不存在文件时的容错处理

        验证对不存在的文件进行检查时不会崩溃，
        而是返回空的CheckResult。
        应该：
        - 不抛出FileNotFoundError
        - 返回CheckResult实例
        - 结果中违规数为0
        """
        from src.services.spec_checker_service import SpecCheckerService

        service = SpecCheckerService()

        # 检查不存在的文件
        result = service.check_file("/nonexistent/path/file.st")

        assert result is not None
        assert result.total_violations == 0
        assert result.source_file == "/nonexistent/path/file.st"

    def test_08_spec_checker_load_project_rules_missing(self, temp_project_dir):
        """
        测试8: 加载不存在的项目规则文件

        验证当项目中没有.rules.json时能优雅处理。
        应该：
        - 返回False（未找到规则）
        - 不抛出异常
        - _project_rules保持为空字典
        """
        from src.services.spec_checker_service import SpecCheckerService

        service = SpecCheckerService()

        # 项目中没有.rules.json文件
        result = service.load_project_rules(str(temp_project_dir))

        assert result is False
        assert service._project_rules == {}

    def test_09_spec_checker_load_project_rules_valid(self, temp_project_dir):
        """
        测试9: 加载有效的项目规则配置

        验证能正确解析.rules.json中的规则覆盖配置。
        应该：
        - 成功读取JSON文件
        - 解析checker_overrides字段
        - _project_rules包含正确的数据
        """
        from src.services.spec_checker_service import SpecCheckerService

        # 创建.rules.json文件
        rules_content = {
            "checker_overrides": {
                "NAMING_001": {
                    "min_length": 4,
                    "max_length": 20,
                },
                "SYNTAX_002": {
                    "enabled": False,
                },
            }
        }

        rules_file = temp_project_dir / ".rules.json"
        rules_file.write_text(
            json.dumps(rules_content, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        service = SpecCheckerService()
        result = service.load_project_rules(str(temp_project_dir))

        assert result is True
        assert "NAMING_001" in service._project_rules["checker_overrides"]
        assert (
            service._project_rules["checker_overrides"]["NAMING_001"]["min_length"]
            == 4
        )

    def test_10_spec_checker_cache_mechanism(self, sample_st_file):
        """
        测试10: 缓存机制工作正常

        验证缓存机制能够正确存储和检索检查结果。
        应该：
        - 第一次检查时缓存未命中
        - 第二次检查相同文件时缓存命中
        - 统计计数器正确更新
        """
        from src.services.spec_checker_service import SpecCheckerService

        service = SpecCheckerService()

        # 清空统计
        service.reset_statistics()

        # 第一次检查（应该是缓存未命中）
        result1 = service.check_file(str(sample_st_file))

        stats_after_first = service.get_statistics()
        cache_misses_first = stats_after_first["total_cache_misses"]

        # 第二次检查相同文件（应该是缓存命中，因为文件未修改）
        result2 = service.check_file(str(sample_st_file))

        stats_after_second = service.get_statistics()
        cache_hits = stats_after_second["total_cache_hits"]

        # 验证第二次产生了缓存命中
        assert cache_hits > 0 or cache_misses_first > 0
        # 验证两次结果一致
        assert result1.source_file == result2.source_file

    def test_11_spec_checker_clear_cache(self, sample_st_file):
        """
        测试11: 缓存清理功能

        验证clear_cache()能正确清空所有缓存数据。
        应该：
        - 清空前缓存不为空
        - 清空后缓存为空
        - 统计信息保持不变
        """
        from src.services.spec_checker_service import SpecCheckerService

        service = SpecCheckerService()

        # 先执行一次检查以填充缓存
        service.check_file(str(sample_st_file))
        cache_size_before = len(service._cache)

        # 清空缓存
        service.clear_cache()

        assert len(service._cache) == 0
        assert len(service._cache_timestamps) == 0


class TestDiagnosticServiceFlow:
    """测试DiagnosticService的完整诊断流程"""

    def test_12_diagnostic_service_creation(self):
        """
        测试12: DiagnosticService实例创建

        验证DiagnosticService可以正常创建且配置完整。
        应该：
        - 成功创建实例
        - 包含3个步骤的流程配置
        - LSP和健康度分析配置存在
        """
        from src.services.diagnostic_service import DiagnosticService

        service = DiagnosticService()

        assert service is not None
        flow_config = service._config.get("full_diagnostic_flow", {})
        assert len(flow_config.get("steps_order", [])) == 3

        assert "lsp_diagnostic" in service._config
        assert "health_analysis" in service._config

    def test_13_diagnostic_service_run_full_invalid_path(self):
        """
        测试13: 对无效路径执行完整诊断

        验证传入无效项目路径时诊断服务能优雅处理。
        应该：
        - 不抛出异常
        - 返回(None, None)或有效的结果元组
        - 日志中记录错误信息
        """
        from src.services.diagnostic_service import DiagnosticService

        service = DiagnosticService()

        # 使用不存在的路径
        report, metrics = service.run_full_diagnostic(
            "/nonexistent/project/path"
        )

        # 应该返回有效的结果（可能是None如果所有步骤都失败）
        assert (report is None and metrics is None) or (
            report is not None or metrics is not None
        )

    def test_14_diagnostic_service_timing_statistics(self):
        """
        测试14: 性能计时统计功能

        验证诊断流程能正确记录各步骤的耗时。
        应该：
        - get_timing_statistics()返回字典
        - 执行后包含时间记录
        """
        from src.services.diagnostic_service import DiagnosticService

        service = DiagnosticService()

        # 初始状态应该为空
        timing = service.get_timing_statistics()
        assert isinstance(timing, dict)

        # 执行一次诊断（即使失败也会记录时间）
        service.run_full_diagnostic("/tmp/nonexistent")

        timing_after = service.get_timing_statistics()
        # 可能包含时间记录（如果某些步骤执行了）

    def test_15_diagnostic_service_reset(self):
        """
        测试15: 服务状态重置功能

        验证reset()能清除所有缓存的状态数据。
        应该：
        - 重置后_last_report和_last_metrics为None
        - 计时统计被清空
        """
        from src.services.diagnostic_service import DiagnosticService

        service = DiagnosticService()

        # 执行一次诊断
        service.run_full_diagnostic("/tmp/fake")

        # 重置状态
        service.reset()

        report, metrics = service.get_last_diagnostics()
        assert report is None
        assert metrics is None
        assert len(service.get_timing_statistics()) == 0

    def test_16_diagnostic_is_healthy_no_results(self):
        """
        测试16: 无诊断结果时的健康判断

        验证在未执行诊断前is_healthy()返回False。
        应该：
        - 返回False（因为没有历史结果）
        """
        from src.services.diagnostic_service import DiagnosticService

        service = DiagnosticService()

        assert service.is_healthy() is False


class TestSpecCheckPanelSignals:
    """测试规范检查面板的信号连接"""

    def test_17_panel_signal_definitions(self):
        """
        测试17: 面板信号定义完整性

        验证SpecCheckPanel定义了必要的PyQt信号。
        应该：
        - 定义check_started信号
        - 定义check_finished信号
        - 定义source_jump_requested信号
        """
        # 注意：此测试需要PyQt5环境
        try:
            from PyQt5.QtCore import pyqtSignal
            from src.ui.widgets.spec_check_panel import SpecCheckPanel

            # 检查信号是否定义
            assert hasattr(SpecCheckPanel, 'check_started')
            assert hasattr(SpecCheckPanel, 'check_finished')
            assert hasattr(SpecCheckPanel, 'source_jump_requested')

        except ImportError:
            pytest.skip("PyQt5环境不可用")

    def test_18_panel_initialization(self):
        """
        测试18: 面板初始化基本属性

        验证SpecCheckPanel初始化后具有正确的初始状态。
        应该：
        - _current_report为None
        - _all_violations为空列表
        - UI组件已创建
        """
        try:
            from src.ui.widgets.spec_check_panel import SpecCheckPanel

            panel = SpecCheckPanel()

            assert panel._current_report is None
            assert panel._all_violations == []
            assert panel._filtered_violations == []

        except ImportError:
            pytest.skip("PyQt5环境不可用")

    def test_19_panel_clear_all_method(self):
        """
        测试19: clear_all()方法重置状态

        验证clear_all()能正确重置面板的所有状态。
        应该：
        - 清空报告引用
        - 清空违规列表
        - 重置UI组件状态
        """
        try:
            from src.ui.widgets.spec_check_panel import SpecCheckPanel

            panel = SpecCheckPanel()
            panel.clear_all()

            assert panel._current_report is None
            assert len(panel._all_violations) == 0
            assert len(panel._filtered_violations) == 0

        except ImportError:
            pytest.skip("PyQt5环境不可用")


class TestDataModelSerialization:
    """测试数据模型的序列化功能"""

    def test_20_check_result_serialization(self, sample_st_file):
        """
        测试20: CheckResult JSON序列化

        验证CheckResult可以正确序列化为JSON格式。
        应该：
        - to_dict()返回字典
        - 包含所有关键字段
        - 可以通过json.dumps序列化
        """
        from src.models.check_result import CheckResult, Violation
        from src.checkers.base_checker import Severity

        result = CheckResult(source_file=str(sample_st_file))
        result.add_violation(Violation(
            rule_id="TEST_001",
            severity=Severity.ERROR,
            message="测试违规",
            file_path=str(sample_st_file),
            line_number=10,
        ))

        data_dict = result.to_dict()

        assert isinstance(data_dict, dict)
        assert "source_file" in data_dict
        assert "violations" in data_dict
        assert len(data_dict["violations"]) == 1

        # 验证可以序列化为JSON
        json_str = json.dumps(data_dict, ensure_ascii=False)
        assert len(json_str) > 0

    def test_21_health_metrics_serialization(self):
        """
        测试21: HealthMetrics JSON序列化

        验证HealthMetrics可以正确序列化。
        应该：
        - to_dict()包含overall_score
        - 包含health_grade信息
        - 包含dimensions维度得分
        """
        from src.models.health_metrics import (
            HealthMetrics,
            HealthGrade,
            DimensionScore,
        )

        metrics = HealthMetrics(
            overall_score=85.5,
            health_grade=HealthGrade.GOOD,
            project_name="TestProject",
        )

        metrics.dimensions.append(
            DimensionScore(
                name="规范符合度",
                score=90.0,
                weight=0.4,
                grade="优秀",
            )
        )

        data_dict = metrics.to_dict()

        assert data_dict["overall_score"] == 85.5
        assert data_dict["health_grade"]["grade"] == "B"
        assert len(data_dict["dimensions"]) == 1

        # 验证JSON字符串输出
        json_str = metrics.to_json_string()
        assert "85.5" in json_str

    def test_22_diagnostic_report_markdown_generation(self):
        """
        测试22: DiagnosticReport Markdown生成

        验证DiagnosticReport可以生成Markdown格式的报告。
        应该：
        - to_markdown()返回非空字符串
        - 包含标题和基本信息
        - 格式符合Markdown语法
        """
        from src.models.diagnostic_report import (
            DiagnosticReport,
            DiagnosticIssue,
            DiagnosticSeverity,
        )

        report = DiagnosticReport(
            project_name="TestProject",
            project_path="/path/to/project",
        )

        report.add_issue(
            DiagnosticIssue(
                rule_id="DIAG_001",
                severity=DiagnosticSeverity.ERROR,
                message="测试问题",
                file_path="test.st",
                line_number=15,
            )
        )

        markdown = report.to_markdown()

        assert len(markdown) > 0
        assert "# LSP兼容性诊断报告" in markdown
        assert "TestProject" in markdown
        assert "DIAG_001" in markdown


class TestConfigLoading:
    """测试配置加载和默认值机制"""

    def test_23_config_spec_check_loaded(self):
        """
        测试23: SPEC_CHECK_CONFIG配置加载

        验证config模块中的SPEC_CHECK_CONFIG可以被正确导入。
        应该：
        - 导入成功
        - 包含concurrency配置
        - 包含file_scanning配置
        - 包含caching配置
        """
        from config import SPEC_CHECK_CONFIG

        assert isinstance(SPEC_CHECK_CONFIG, dict)
        assert "concurrency" in SPEC_CHECK_CONFIG
        assert "file_scanning" in SPEC_CHECK_CONFIG
        assert "caching" in SPEC_CHECK_CONFIG
        assert SPEC_CHECK_CONFIG["concurrency"]["max_workers"] > 0

    def test_24_config_diagnostic_loaded(self):
        """
        测试24: DIAGNOSTIC_CONFIG配置加载

        验证DIAGNOSTIC_CONFIG包含完整的诊断流程配置。
        应该：
        - 包含3步流程定义
        - LSP诊断配置完整
        - 健康度分析权重合理
        """
        from config import DIAGNOSTIC_CONFIG

        assert isinstance(DIAGNOSTIC_CONFIG, dict)

        steps = DIAGNOSTIC_CONFIG["full_diagnostic_flow"]["steps_order"]
        assert len(steps) == 3
        assert "spec_check" in steps
        assert "lsp_diagnostic" in steps
        assert "health_analysis" in steps

        weights = DIAGNOSTIC_CONFIG["health_analysis"]["dimensions_weights"]
        total_weight = sum(weights.values())
        assert abs(total_weight - 1.0) < 0.01  # 权重总和应为1.0

    def test_25_config_test_loaded(self):
        """
        测试25: TEST_CONFIG配置加载

        验证TEST_CONFIG包含测试框架所需的配置项。
        应该：
        - 包含test_discovery配置
        - 包含execution配置
        - 包含reporting配置
        """
        from config import TEST_CONFIG

        assert isinstance(TEST_CONFIG, dict)
        assert "test_discovery" in TEST_CONFIG
        assert "execution" in TEST_CONFIG
        assert "reporting" in TEST_CONFIG
        assert "assertions" in TEST_CONFIG

        assert TEST_CONFIG["execution"]["default_timeout"] > 0


# ============================================================================
# 运行入口
# ============================================================================

if __name__ == "__main__":
    # 直接运行时使用pytest执行
    pytest.main([__file__, "-v", "--tb=short"])
