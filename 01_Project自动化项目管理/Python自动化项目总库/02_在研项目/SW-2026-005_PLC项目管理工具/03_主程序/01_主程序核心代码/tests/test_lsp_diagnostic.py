# -*- coding: utf-8 -*-
"""
LSP兼容性检查器单元测试

覆盖以下测试场景:
1. 诊断报告模型的基本功能（to_dict, to_markdown, 统计计算）
2. LSPCompatibilityChecker的初始化和扫描
3. DIAG_001: Builtin stub误用检测
4. DIAG_002: 缺失FB实现检测
5. DIAG_003: 可疑内存访问检测
6. DIAG_004: 不安全类型转换检测
7. OB→FB调用链分析
8. 空项目/无效路径处理
9. 单文件扫描功能
10. 报告序列化（JSON/Markdown）
11. 边界情况和异常处理
12. 集成测试（完整扫描流程）
"""

import os
import sys
import tempfile
import json
from pathlib import Path
from datetime import datetime
from unittest import TestCase

# 添加项目根目录到系统路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from src.models.diagnostic_report import (
    DiagnosticIssue,
    DiagnosticReport,
    DiagnosticSeverity,
)
from src.diagnostics.lsp_compatibility_checker import (
    LSPCompatibilityChecker,
    DiagnosticRules,
    FBCallInfo,
    check_project_lsp_compatibility,
)


class TestDiagnosticIssueModel(TestCase):
    """诊断问题数据模型测试"""

    def test_issue_creation_with_required_fields(self):
        """测试1: 使用必填字段创建问题记录"""
        issue = DiagnosticIssue(
            rule_id="DIAG_001",
            severity=DiagnosticSeverity.ERROR,
            message="测试问题"
        )

        self.assertEqual(issue.rule_id, "DIAG_001")
        self.assertEqual(issue.severity, DiagnosticSeverity.ERROR)
        self.assertEqual(issue.message, "测试问题")
        self.assertEqual(issue.file_path, "")
        self.assertEqual(issue.line_number, 0)

    def test_issue_to_dict_serialization(self):
        """测试2: 问题记录的字典序列化"""
        issue = DiagnosticIssue(
            rule_id="DIAG_002",
            severity=DiagnosticSeverity.WARNING,
            message="FB缺失",
            file_path="runtime/blocks_ob_autogen.go",
            line_number=15,
            column=5,
            category="missing_implementation",
            suggestion="请创建FB",
            code_snippet="FB_Test(mem, &mem.db)",
            source_line="d:/path/OB1.scl:20",
            related_symbols=["FB_Test", "OB1"]
        )

        result = issue.to_dict()

        self.assertIsInstance(result, dict)
        self.assertEqual(result["rule_id"], "DIAG_002")
        self.assertEqual(result["severity"], "warning")
        self.assertEqual(result["file_path"], "runtime/blocks_ob_autogen.go")
        self.assertEqual(result["line_number"], 15)
        self.assertEqual(len(result["related_symbols"]), 2)

    def test_issue_location_str_formatting(self):
        """测试3: 位置字符串格式化"""
        # 完整位置信息
        issue1 = DiagnosticIssue(
            rule_id="TEST",
            severity=DiagnosticSeverity.ERROR,
            message="test",
            file_path="path/to/file.go",
            line_number=10,
            column=5
        )
        self.assertIn("file.go:10:5", issue1.location_str)

        # 无列号
        issue2 = DiagnosticIssue(
            rule_id="TEST",
            severity=DiagnosticSeverity.ERROR,
            message="test",
            file_path="path/to/file.go",
            line_number=10
        )
        self.assertEqual(issue2.location_str, "file.go:10")

        # 无文件路径
        issue3 = DiagnosticIssue(
            rule_id="TEST",
            severity=DiagnosticSeverity.ERROR,
            message="test"
        )
        self.assertEqual(issue3.location_str, "未知位置")

    def test_issue_string_representation(self):
        """测试4: 问题的字符串表示"""
        issue = DiagnosticIssue(
            rule_id="DIAG_001",
            severity=DiagnosticSeverity.ERROR,
            message="Stub误用",
            file_path="test.go",
            line_number=5
        )

        str_repr = str(issue)
        self.assertIn("ERROR", str_repr)
        self.assertIn("DIAG_001", str_repr)
        self.assertIn("Stub误用", str_repr)


class TestDiagnosticReportModel(TestCase):
    """诊断报告数据模型测试"""

    def setUp(self):
        """每个测试前的初始化"""
        self.report = DiagnosticReport(
            project_name="TestProject",
            project_path="/tmp/test",
            plc_output_path="/tmp/test/.plc-out/golang"
        )

    def test_report_initial_stats(self):
        """测试5: 报告初始统计值"""
        self.assertEqual(self.report.total_issues, 0)
        self.assertEqual(self.report.error_count, 0)
        self.assertFalse(self.report.has_errors)
        self.assertTrue(self.report.is_passed)

    def test_add_single_issue(self):
        """测试6: 添加单个问题"""
        issue = DiagnosticIssue(
            rule_id="DIAG_001",
            severity=DiagnosticSeverity.ERROR,
            message="错误1"
        )
        self.report.add_issue(issue)

        self.assertEqual(self.report.total_issues, 1)
        self.assertEqual(self.report.error_count, 1)
        self.assertTrue(self.report.has_errors)
        self.assertFalse(self.report.is_passed)

    def test_batch_add_issues(self):
        """测试7: 批量添加问题"""
        issues = [
            DiagnosticIssue(
                rule_id="DIAG_001",
                severity=DiagnosticSeverity.ERROR,
                message="错误"
            ),
            DiagnosticIssue(
                rule_id="DIAG_002",
                severity=DiagnosticSeverity.WARNING,
                message="警告"
            ),
            DiagnosticIssue(
                rule_id="DIAG_003",
                severity=DiagnosticSeverity.INFO,
                message="信息"
            ),
        ]
        self.report.add_issues(issues)

        self.assertEqual(self.report.total_issues, 3)
        self.assertEqual(self.report.error_count, 1)
        self.assertEqual(self.report.warning_count, 1)
        self.assertEqual(self.report.info_count, 1)

    def test_filter_issues_by_severity(self):
        """测试8: 按严重级别筛选问题"""
        issues = [
            DiagnosticIssue(rule_id="T1", severity=DiagnosticSeverity.ERROR, message="E"),
            DiagnosticIssue(rule_id="T2", severity=DiagnosticSeverity.WARNING, message="W"),
            DiagnosticIssue(rule_id="T3", severity=DiagnosticSeverity.ERROR, message="E2"),
        ]
        self.report.add_issues(issues)

        errors = self.report.get_issues_by_severity(DiagnosticSeverity.ERROR)
        self.assertEqual(len(errors), 2)

        warnings = self.report.get_issues_by_severity(DiagnosticSeverity.WARNING)
        self.assertEqual(len(warnings), 1)

    def test_report_to_dict_serialization(self):
        """测试9: 报告的字典序列化"""
        self.report.add_issue(DiagnosticIssue(
            rule_id="TEST",
            severity=DiagnosticSeverity.ERROR,
            message="测试"
        ))
        self.report.scanned_files = ["file1.go", "file2.go"]

        result = self.report.to_dict()

        self.assertIn("project_name", result)
        self.assertIn("summary", result)
        self.assertIn("issues", result)
        self.assertEqual(result["summary"]["total_issues"], 1)
        self.assertEqual(len(result["scanned_files"]), 2)

    def test_report_to_json_string(self):
        """测试10: 报告的JSON字符串输出"""
        json_str = self.report.to_json_string()

        # 验证是有效的JSON
        parsed = json.loads(json_str)
        self.assertIsInstance(parsed, dict)
        self.assertEqual(parsed["project_name"], "TestProject")

    def test_report_quality_score_calculation(self):
        """测试11: 质量评分计算"""
        # 无问题时满分
        self.assertEqual(self.report.quality_score, 100.0)

        # 添加不同级别的问题
        self.report.add_issue(DiagnosticIssue(
            rule_id="D1", severity=DiagnosticSeverity.ERROR, message="E"
        ))
        score_after_error = self.report.quality_score
        self.assertLess(score_after_error, 100.0)

        self.report.add_issue(DiagnosticIssue(
            rule_id="D2", severity=DiagnosticSeverity.WARNING, message="W"
        ))
        score_after_warning = self.report.quality_score
        self.assertLess(score_after_warning, score_after_error)

    def test_report_worst_files_ranking(self):
        """测试12: 问题最多的文件排名"""
        # 添加多个文件的问题
        for i in range(5):
            self.report.add_issue(DiagnosticIssue(
                rule_id=f"T{i}",
                severity=DiagnosticSeverity.ERROR,
                message=f"Issue {i}",
                file_path=f"file_a.go"
            ))
        for i in range(3):
            self.report.add_issue(DiagnosticIssue(
                rule_id=f"W{i}",
                severity=DiagnosticSeverity.WARNING,
                message=f"Warning {i}",
                file_path="file_b.go"
            ))

        worst = self.report.get_worst_files(top_n=2)

        self.assertEqual(len(worst), 2)
        # file_a.go 应该排在第一位
        self.assertEqual(worst[0][0], "file_a.go")
        self.assertEqual(worst[0][1], 5)


class TestLSPCompatibilityCheckerBasic(TestCase):
    """LSP兼容性检查器基础功能测试"""

    def test_checker_initialization(self):
        """测试13: 检查器正确初始化"""
        checker = LSPCompatibilityChecker("/fake/path")

        self.assertEqual(checker.project_path, Path("/fake/path").resolve())
        self.assertIsNotNone(checker.report)
        self.assertEqual(checker.report.project_name, "path")

    def test_scan_nonexistent_directory(self):
        """测试14: 扫描不存在的目录"""
        checker = LSPCompatibilityChecker("/nonexistent/project/path")
        report = checker.scan()

        self.assertIsNotNone(report)
        self.assertTrue(report.has_issues)  # 应该有警告：未找到Go文件


class TestLSPCompatibilityCheckerWithMockData(TestCase):
    """使用模拟数据的LSP兼容性检查器测试"""

    def setUp(self):
        """创建临时测试目录结构"""
        self.temp_dir = tempfile.mkdtemp(prefix="lsp_test_")

        # 创建 .plc-out/golang 目录结构
        self.golang_dir = Path(self.temp_dir) / ".plc-out" / "golang"
        self.golang_dir.mkdir(parents=True)

    def tearDown(self):
        """清理临时目录"""
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def _create_go_file(self, filename: str, content: str) -> Path:
        """辅助方法：创建Go测试文件"""
        file_path = self.golang_dir / filename
        file_path.write_text(content, encoding="utf-8")
        return file_path

    def test_detect_builtin_stub_misuse_DIAG_001(self):
        """测试15: DIAG_001 - 检测builtin stub误用模式"""
        # 创建包含stub误用的Go代码
        go_content = """\
package plcruntime

func OB_OB1(mem *Memory) {
	//line d:/test/OB1.scl:10:1
	mem.v_Var1 = true
	_ = builtins.B_TON(mem, &mem.v_Timer1)
	_ = builtins.B_CTU(mem, &mem.v_Counter1)
	FB_FB_ValveControl(mem, &mem.v_GlobalVars.v_ValveCtrl)
}
"""
        self._create_go_file("runtime/blocks_ob_autogen.go", go_content)

        # 创建对应的FB实现文件
        fb_content = """\
package plcruntime

func FB_FB_ValveControl(mem *Memory, db *DB_FB_ValveControl) {
	db.v_Output = db.v_Input
}
"""
        self._create_go_file("runtime/blocks_fb_autogen.go", fb_content)

        # 执行扫描
        checker = LSPCompatibilityChecker(self.temp_dir)
        report = checker.scan()

        # 验证检测结果
        stub_issues = report.get_issues_by_rule(DiagnosticRules.DIAG_001)
        self.assertGreaterEqual(len(stub_issues), 2)  # 应该检测到至少2个stub误用

        # 验证stub名称被正确提取
        stub_names = [sym for issue in stub_issues for sym in issue.related_symbols]
        self.assertIn("B_TON", stub_names)
        self.assertIn("B_CTU", stub_names)

    def test_detect_missing_fb_implementation_DIAG_002(self):
        """测试16: DIAG_002 - 检测缺失的FB实现"""
        # 创建OB文件，调用一个不存在的FB
        ob_content = """\
package plcruntime

func OB_OB1(mem *Memory) {
	//line d:/test/OB1.scl:15:1
	FB_FB_MissingFunc(mem, &mem.v_Data)
	FB_FB_ExistingFunc(mem, &mem.v_Data2)
}
"""
        self._create_go_file("runtime/blocks_ob_autogen.go", ob_content)

        # 只创建其中一个FB的实现
        fb_content = """\
package plcruntime

func FB_FB_ExistingFunc(mem *Memory, db *DB_FB_ExistingFunc) {
	db.v_Result = true
}
"""
        self._create_go_file("runtime/blocks_fb_autogen.go", fb_content)

        # 执行扫描
        checker = LSPCompatibilityChecker(self.temp_dir)
        report = checker.scan()

        # 验证缺失实现检测
        missing_issues = report.get_issues_by_rule(DiagnosticRules.DIAG_002)
        self.assertEqual(len(missing_issues), 1)  # 应该检测到1个缺失的FB
        self.assertIn("FB_MissingFunc", missing_issues[0].related_symbols)

    def test_ob_fb_call_chain_analysis(self):
        """测试17: OB→FB调用链分析"""
        ob_content = """\
package plcruntime

func OB_OB1(mem *Memory) {
	//line d:/test/OB1.scl:20:1
	FB_FB_Motor(mem, &mem.v_MotorData)
	FB_FB_Valve(mem, &mem.v_ValveData)
}

func OB_OB35(mem *Memory) {
	//line d:/test/OB35.scl:10:1
	FB_FB_PID(mem, &mem.v_PIDData)
}
"""
        self._create_go_file("runtime/blocks_ob_autogen.go", ob_content)

        # 创建所有FB实现
        fb_content = """\
package plcruntime

func FB_FB_Motor(mem *Memory, db *DB_FB_Motor) {}
func FB_FB_Valve(mem *Memory, db *DB_FB_Valve) {}
func FB_FB_PID(mem *Memory, db *DB_FB_PID) {}
"""
        self._create_go_file("runtime/blocks_fb_autogen.go", fb_content)

        checker = LSPCompatibilityChecker(self.temp_dir)
        report = checker.scan()

        # 验证调用链
        self.assertIn("OB_OB1", report.ob_fb_call_chain)
        self.assertIn("OB_OB35", report.ob_fb_call_chain)

        # OB1应该调用2个FB
        self.assertEqual(len(report.ob_fb_call_chain["OB_OB1"]), 2)
        # OB35应该调用1个FB
        self.assertEqual(len(report.obfb_call_chain["OB_OB35"]), 1)

    def test_detect_risky_memory_access_DIAG_003(self):
        """测试18: DIAG_003 - 可疑内存访问检测"""
        go_content = """\
package plcruntime

func OB_OB1(mem *Memory) {
	//line d:/test/OB1.scl:25:1
	var value int16
	value = mem.v_Array[mem.v_Index + 1]
	value = mem.v_Buffer[mem.v_Ptr - 5]
}
"""
        self._create_go_file("runtime/blocks_ob_autogen.go", go_content)

        checker = LSPCompatibilityChecker(self.temp_dir)
        report = checker.scan()

        memory_issues = report.get_issues_by_rule(DiagnosticRules.DIAG_003)
        self.assertGreater(len(memory_issues), 0)  # 应该检测到可疑访问

    def test_detect_unsafe_type_cast_DIAG_004(self):
        """测试19: DIAG_004 - 不安全类型转换检测"""
        go_content = """\
package plcruntime

func OB_OB1(mem *Memory) {
	//line d:/test/OB1.scl:30:1
	mem.v_SmallVar = int16(mem.v_LargeVar)
	mem.v_Converted = int32(mem.v_OtherVar)
}
"""
        self._create_go_file("runtime/blocks_ob_autogen.go", go_content)

        checker = LSPCompatibilityChecker(self.temp_dir)
        report = checker.scan()

        cast_issues = report.get_issues_by_rule(DiagnosticRules.DIAG_004)
        self.assertGreater(len(cast_issues), 0)  # 应该检测到类型转换

        # 验证窄化转换被标记为WARNING
        narrowing_casts = [
            i for i in cast_issues
            if i.severity == DiagnosticSeverity.WARNING and "窄化" in i.message
        ]
        self.assertGreater(len(narrowing_casts), 0)


class TestReportGeneration(TestCase):
    """报告生成功能测试"""

    def setUp(self):
        """准备测试报告"""
        self.report = DiagnosticReport(
            project_name="TestProj",
            project_path="/test",
            plc_output_path="/test/.plc-out"
        )

        # 添加一些示例问题
        self.report.add_issue(DiagnosticIssue(
            rule_id="DIAG_001",
            severity=DiagnosticSeverity.ERROR,
            message="Stub误用: B_TON",
            file_path="blocks_ob_autogen.go",
            line_number=10,
            category="stub_misuse",
            suggestion="检查SCL代码",
            code_snippet="_ = builtins.B_TON(...)",
            related_symbols=["B_TON"]
        ))

        self.report.add_issue(DiagnosticIssue(
            rule_id="DIAG_002",
            severity=DiagnosticSeverity.WARNING,
            message="FB缺失",
            file_path="blocks_ob_autogen.go",
            line_number=15,
            category="missing_implementation"
        ))

        self.report.scanned_files = [
            "runtime/blocks_ob_autogen.go",
            "runtime/blocks_fb_autogen.go"
        ]

    def test_markdown_report_generation(self):
        """测试20: Markdown报告生成"""
        markdown = self.report.to_markdown()

        # 验证基本内容
        self.assertIn("# LSP兼容性诊断报告", markdown)
        self.assertIn("TestProj", markdown)
        self.assertIn("## 📊 统计摘要", markdown)
        self.assertIn("DIAG_001", markdown)
        self.assertIn("DIAG_002", markdown)
        self.assertIn("Stub误用: B_TON", markdown)
        self.assertIn("💡 修复建议汇总", markdown)

    def test_markdown_report_contains_table(self):
        """测试21: Markdown报告包含表格"""
        markdown = self.report.to_markdown()

        # 验证包含Markdown表格语法
        self("| 指标 | 数值 |" in markdown)
        self("|------|------|" in markdown)

    def test_summary_text_generation(self):
        """测试22: 摘要文本生成"""
        summary = self.report.generate_summary_text()

        self.assertIn("LSP兼容性诊断报告摘要", summary)
        self.assertIn("TestProj", summary)
        self.assertIn("问题总数: 2", summary)
        self.assertIn("错误: 1", summary)
        self.assertIn("警告: 1", summary)


class TestEdgeCasesAndErrorHandling(TestCase):
    """边界情况和异常处理测试"""

    def test_empty_project_scan(self):
        """测试23: 空项目目录扫描"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建空的.plc-out/golang目录
            golang_dir = Path(temp_dir) / ".plc-out" / "golang"
            golang_dir.mkdir(parents=True)

            checker = LSPCompatibilityChecker(temp_dir)
            report = checker.scan()

            # 应该没有严重错误，但可能有提示
            self.assertFalse(report.has_errors)

    def test_single_file_scan_method(self):
        """测试24: 单文件扫描方法"""
        with tempfile.TemporaryDirectory() as temp_dir:
            golang_dir = Path(temp_dir) / ".plc-out" / "golang"
            golang_dir.mkdir(parents=True)

            # 创建单个测试文件
            test_file = golang_dir / "test.go"
            test_file.write_text("""\
package plcruntime
_ = builtins.B_TEST()
""", encoding="utf-8")

            checker = LSPCompatibilityChecker(temp_dir)
            issues = checker.scan_single_file(str(test_file))

            # 应该检测到stub误用
            self.assertGreater(len(issues), 0)
            self.assertTrue(any(i.rule_id == DiagnosticRules.DIAG_001 for i in issues))

    def test_invalid_file_path_handling(self):
        """测试25: 无效文件路径处理"""
        checker = LSPCompatibilityChecker("/fake/path")

        # 扫描不存在的文件不应抛出异常
        issues = checker.scan_single_file("/nonexistent/file.go")
        self.assertEqual(len(issues), 0)

    def test_convenience_function(self):
        """测试26: 便捷函数接口"""
        with tempfile.TemporaryDirectory() as temp_dir:
            golang_dir = Path(temp_dir) / ".plc-out" / "golang"
            golang_dir.mkdir(parents=True)

            # 创建测试文件
            (golang_dir / "test.go").write_text(
                "package plcruntime\nfunc OB_OB1(mem *Memory) {}\n",
                encoding="utf-8"
            )

            # 测试不同的输出格式
            report_obj = check_project_lsp_compatibility(temp_dir, output_format="report")
            self.assertIsInstance(report_obj, DiagnosticReport)

            dict_result = check_project_lsp_compatibility(temp_dir, output_format="dict")
            self.assertIsInstance(dict_result, dict)

            json_result = check_project_lsp_compatibility(temp_dir, output_format="json")
            parsed = json.loads(json_result)
            self.assertIsInstance(parsed, dict)

            md_result = check_project_lsp_compatibility(temp_dir, output_format="markdown")
            self.assertIsInstance(md_result, str)
            self.assertIn("LSP兼容性诊断报告", md_result)


class TestIntegrationScenarios(TestCase):
    """集成测试场景"""

    def test_complete_realistic_scenario(self):
        """测试27: 完整的真实场景模拟"""
        with tempfile.TemporaryDirectory() as temp_dir:
            golang_dir = Path(temp_dir) / ".plc-out" / "golang"
            runtime_dir = golang_dir / "runtime"
            runtime_dir.mkdir(parents=True)

            # 模拟真实的OB文件（包含多种问题）
            ob_content = '''\
package plcruntime

//line d:/project/OB1/OB1.scl:19:1
func OB_OB1(mem *Memory) {
//line d:/project/OB1/OB1.scl:26:1
	mem.v_GlobalVars.v_ValveCtrl.v_AutoManual = mem.v_GlobalVars.v_Hmibutton[0]
//line d:/project/OB1/OB1.scl:35:1
	_ = builtins.B_TON(mem, &mem.v_Timer1)
//line d:/project/OB1/OB1.scl:40:1
	FB_FB_ValveControl(mem, &mem.v_GlobalVars.v_ValveCtrl)
//line d:/project/OB1/OB1.scl:45:1
	mem.v_GlobalVars.v_Counter = int16(mem.v_GlobalVars.v_LargeValue)
//line d:/project/OB1/OB1.scl:50:1
	FB_FB_MissingMotor(mem, &mem.v_MotorData)
}
'''
            (runtime_dir / "blocks_ob_autogen.go").write_text(
                ob_content, encoding="utf-8"
            )

            # 模拟FB实现文件（只实现部分FB）
            fb_content = '''\
package plcruntime

//line d:/project/FB100/FB_ValveControl.scl:23:1
func FB_FB_ValveControl(mem *Memory, db *DB_FB_ValveControl) {
	if db.v_AutoManual {
		db.v_Open = true
	}
}
'''
            (runtime_dir / "blocks_fb_autogen.go").write_text(
                fb_content, encoding="utf-8"
            )

            # 执行完整扫描
            checker = LSPCompatibilityChecker(temp_dir)
            report = checker.scan()

            # 验证完整结果
            self.assertTrue(report.has_issues)  # 应该有问题

            # 验证各类问题的检测
            stub_issues = report.get_issues_by_rule(DiagnosticRules.DIAG_001)
            self.assertGreater(len(stub_issues), 0)  # B_TON stub误用

            missing_issues = report.get_issues_by_rule(DiagnosticRules.DIAG_002)
            self.assertGreater(len(missing_issues), 0)  # FB_MissingMotor缺失

            cast_issues = report.get_issues_by_rule(DiagnosticRules.DIAG_004)
            self.assertGreater(len(cast_issues), 0)  # 类型转换

            # 验证调用链分析
            self.assertIn("OB_OB1", report.ob_fb_call_chain)
            self.assertIn("FB_ValveControl", report.ob_fb_call_chain["OB_OB1"])
            self.assertIn("FB_MissingMotor", report.ob_fb_call_chain["OB_OB1"])

            # 验证报告可以正确序列化
            md_report = report.to_markdown()
            self.assertIn("ValveControl", md_report)
            self.assertIn("MissingMotor", md_report)
            self.assertIn("B_TON", md_report)

            # 验证JSON输出
            json_output = report.to_json_string()
            parsed = json.loads(json_output)
            self.assertEqual(parsed["summary"]["total_issues"], report.total_issues)


# ============================================================
# pytest主入口
# ============================================================

if __name__ == "__main__":
    # 运行所有测试
    pytest.main([__file__, "-v", "--tb=short"])
