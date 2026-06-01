# -*- coding: utf-8 -*-
"""
伴生工作流测试 - TC-C01 ~ TC-C09

覆盖 CompanionService 能力边界、跳转逻辑、产品定位等核心场景。
"""
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.core.constants import (
    COMPANION_CAPABILITIES,
    COMPANION_NON_CAPABILITIES,
    COMPANION_PRIMARY_IDE,
    COMPANION_ROLE,
    DESCRIPTION,
    TRAJUMP_SUPPORTED_EXTENSIONS,
)
from src.services.companion_service import CompanionService


class TestCompanionRole(unittest.TestCase):
    """TC-C01 ~ TC-C03: 伴生角色与能力边界测试"""

    def test_tc_c01_product_description_is_companion(self):
        """TC-C01: 产品描述体现伴生定位"""
        self.assertIn("伴生", DESCRIPTION)
        self.assertIn("治理", DESCRIPTION)

    def test_tc_c02_capability_boundary(self):
        """TC-C02: 能力边界正确 - 治理能力可用, 编辑能力不可用"""
        for cap in COMPANION_CAPABILITIES:
            self.assertTrue(
                CompanionService.can_handle(cap),
                f"应具备能力: {cap}",
            )
        for non_cap in COMPANION_NON_CAPABILITIES:
            self.assertFalse(
                CompanionService.can_handle(non_cap),
                f"不应具备能力: {non_cap}",
            )

    def test_tc_c03_unknown_capability_returns_false(self):
        """TC-C03: 未知能力返回False"""
        self.assertFalse(CompanionService.can_handle("unknown_capability"))
        self.assertFalse(CompanionService.can_handle(""))

    def test_role_description_contains_key_info(self):
        """角色描述包含关键信息"""
        desc = CompanionService.get_role_description()
        self.assertIn(COMPANION_PRIMARY_IDE, desc)
        self.assertIn(COMPANION_ROLE, desc)

    def test_jump_summary_structure(self):
        """跳转摘要结构完整"""
        summary = CompanionService.get_jump_summary()
        self.assertIn("role", summary)
        self.assertIn("primary_ide", summary)
        self.assertIn("capabilities", summary)
        self.assertIn("non_capabilities", summary)
        self.assertIn("supported_extensions", summary)
        self.assertEqual(summary["primary_ide"], COMPANION_PRIMARY_IDE)


class TestShouldJumpToIDE(unittest.TestCase):
    """TC-C04 ~ TC-C05: 跳转判定测试"""

    def test_tc_c04_source_files_should_jump(self):
        """TC-C04: 源码文件应跳转到IDE"""
        for ext in [".scl", ".st", ".plc"]:
            self.assertTrue(
                CompanionService.should_jump_to_ide(f"test{ext}"),
                f"扩展名 {ext} 应跳转",
            )

    def test_tc_c05_binary_files_should_not_jump(self):
        """TC-C05: 二进制文件不应跳转到IDE"""
        for ext in [".exe", ".dll", ".bin", ".zip", ".pdf"]:
            self.assertFalse(
                CompanionService.should_jump_to_ide(f"test{ext}"),
                f"扩展名 {ext} 不应跳转",
            )

    def test_config_files_should_jump(self):
        """配置文件应跳转"""
        for ext in [".json", ".xml", ".yaml", ".yml"]:
            self.assertTrue(
                CompanionService.should_jump_to_ide(f"config{ext}"),
            )

    def test_document_files_should_jump(self):
        """文档文件应跳转"""
        for ext in [".md", ".txt", ".csv"]:
            self.assertTrue(
                CompanionService.should_jump_to_ide(f"doc{ext}"),
            )

    def test_excel_files_should_jump(self):
        """Excel文件应跳转(系统默认打开)"""
        for ext in [".xlsx", ".xls"]:
            self.assertTrue(
                CompanionService.should_jump_to_ide(f"report{ext}"),
            )


class _TempDirMixin:
    """临时目录管理混入"""

    def setUp(self):
        self._temp_root = tempfile.mkdtemp(prefix="companion_test_")

    def tearDown(self):
        if os.path.exists(self._temp_root):
            shutil.rmtree(self._temp_root, ignore_errors=True)

    def _make_file(self, *parts, content=""):
        fpath = os.path.join(self._temp_root, *parts)
        os.makedirs(os.path.dirname(fpath), exist_ok=True)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
        return fpath


class TestJumpToFile(_TempDirMixin, unittest.TestCase):
    """TC-C06 ~ TC-C08: 跳转执行测试"""

    def test_tc_c06_nonexistent_file_returns_error(self):
        """TC-C06: 不存在的文件返回错误"""
        success, error = CompanionService.jump_to_file(
            os.path.join(self._temp_root, "no_such_file.scl")
        )
        self.assertFalse(success)
        self.assertIsNotNone(error)
        self.assertIn("不存在", error)

    @patch.object(CompanionService, '_open_in_trae')
    def test_tc_c07_scl_file_tries_trae_first(self, mock_trae):
        """TC-C07: SCL文件优先尝试Trae跳转"""
        mock_trae.return_value = (True, None)
        scl_file = self._make_file("test.scl", content="PROGRAM Main\nEND_PROGRAM")

        success, error = CompanionService.jump_to_file(scl_file)
        self.assertTrue(success)
        mock_trae.assert_called_once()

    @patch.object(CompanionService, '_open_in_trae')
    def test_tc_c08_trae_failure_falls_back_to_system(self, mock_trae):
        """TC-C08: Trae跳转失败时降级到系统默认"""
        mock_trae.return_value = (False, "Trae CLI未安装")
        scl_file = self._make_file("test.scl", content="PROGRAM Main\nEND_PROGRAM")

        with patch.object(CompanionService, '_open_with_system') as mock_sys:
            mock_sys.return_value = (True, None)
            success, error = CompanionService.jump_to_file(scl_file)
            self.assertTrue(success)
            mock_sys.assert_called_once()

    @patch.object(CompanionService, '_open_with_system')
    def test_excel_file_uses_system_open(self, mock_sys):
        """Excel文件直接用系统默认打开"""
        mock_sys.return_value = (True, None)
        xlsx_file = self._make_file("report.xlsx", content="")

        success, error = CompanionService.jump_to_file(xlsx_file)
        self.assertTrue(success)
        mock_sys.assert_called_once()


class TestTraeCLIJump(unittest.TestCase):
    """TC-C09: Trae CLI 跳转测试"""

    @patch('subprocess.run')
    def test_tc_c09_trae_cli_with_line_number(self, mock_run):
        """TC-C09: Trae CLI 跳转带行号参数"""
        mock_run.return_value = MagicMock(returncode=0)

        success, error = CompanionService._open_in_trae("/test/file.scl", 42)
        self.assertTrue(success)
        self.assertIsNone(error)

        call_args = mock_run.call_args
        cmd = call_args[0][0]
        self.assertIn("trae", cmd)
        self.assertIn("--goto", cmd)
        self.assertIn("42", cmd)

    @patch('subprocess.run')
    def test_trae_cli_without_line_number(self, mock_run):
        """Trae CLI 跳转不带行号"""
        mock_run.return_value = MagicMock(returncode=0)

        success, error = CompanionService._open_in_trae("/test/file.scl", 0)
        self.assertTrue(success)

        call_args = mock_run.call_args
        cmd = call_args[0][0]
        self.assertNotIn("--goto", cmd)

    @patch('subprocess.run', side_effect=FileNotFoundError("trae not found"))
    def test_trae_cli_not_found(self, mock_run):
        """Trae CLI 未安装"""
        success, error = CompanionService._open_in_trae("/test/file.scl")
        self.assertFalse(success)
        self.assertIn("未安装", error)


class TestCompanionConstants(unittest.TestCase):
    """伴生常量完整性测试"""

    def test_supported_extensions_not_empty(self):
        """支持的扩展名列表不为空"""
        self.assertGreater(len(TRAJUMP_SUPPORTED_EXTENSIONS), 0)

    def test_capabilities_include_required(self):
        """能力列表包含必要项"""
        required = ["mount", "index", "check", "summarize"]
        for cap in required:
            self.assertIn(cap, COMPANION_CAPABILITIES)

    def test_non_capabilities_include_edit_source(self):
        """非能力列表包含源码编辑"""
        self.assertIn("edit_source", COMPANION_NON_CAPABILITIES)

    def test_primary_ide_is_trae(self):
        """主IDE是Trae"""
        self.assertEqual(COMPANION_PRIMARY_IDE, "Trae")


if __name__ == "__main__":
    unittest.main()
