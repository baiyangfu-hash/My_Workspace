# -*- coding: utf-8 -*-
"""
共享库治理测试 - TC-L01 ~ TC-L09

覆盖 LibraryService 扫描、分类、统计、规范目录识别等核心场景。
"""
import os
import shutil
import tempfile
import unittest

from src.core.constants import (
    LibraryArtifactType,
    PLC_LIBRARY_CATEGORY_DIRS,
    SPEC_DIR_MARKERS,
)
from src.services.library_service import LibraryService
from src.services.artifact_registry_service import ArtifactRegistryService


class _TempDirMixin:
    """临时目录管理混入"""

    def setUp(self):
        self._temp_root = tempfile.mkdtemp(prefix="lib_test_")

    def tearDown(self):
        if os.path.exists(self._temp_root):
            shutil.rmtree(self._temp_root, ignore_errors=True)

    def _make_dir(self, *parts):
        d = os.path.join(self._temp_root, *parts)
        os.makedirs(d, exist_ok=True)
        return d

    def _make_file(self, *parts, content=""):
        fpath = os.path.join(self._temp_root, *parts)
        os.makedirs(os.path.dirname(fpath), exist_ok=True)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
        return fpath


class TestLibraryScan(_TempDirMixin, unittest.TestCase):
    """TC-L01 ~ TC-L05: 共享库扫描测试"""

    def test_tc_l01_scan_standard_library(self):
        """TC-L01: 标准共享库扫描 - 识别分类目录和规范目录"""
        lib_dir = self._make_dir("SysLib")
        self._make_file("SysLib", ".plc.json", content='{}')
        self._make_file("SysLib", "actuator", "FB_Valve.scl", content="FUNCTION_BLOCK FB_Valve\nEND_FUNCTION_BLOCK")
        self._make_file("SysLib", "timer", "FB_TON.scl", content="FUNCTION_BLOCK FB_TON\nEND_FUNCTION_BLOCK")
        self._make_file("SysLib", "00_通用规范", "LSP-905.md", content="# SCL编程规范")

        result = LibraryService.scan_library(lib_dir)
        self.assertIsNotNone(result)
        self.assertEqual(result.library_name, "SysLib")
        self.assertGreaterEqual(len(result.categories), 2)
        self.assertGreaterEqual(len(result.spec_dirs), 1)
        self.assertGreater(result.total_st_files, 0)
        self.assertGreater(result.total_spec_files, 0)

    def test_tc_l02_category_file_count(self):
        """TC-L02: 分类目录文件计数正确"""
        lib_dir = self._make_dir("TestLib")
        self._make_file("TestLib", ".plc.json", content='{}')
        self._make_file("TestLib", "actuator", "FB_Valve.scl", content="")
        self._make_file("TestLib", "actuator", "FB_Cylinder.scl", content="")
        self._make_file("TestLib", "actuator", "README.md", content="")

        result = LibraryService.scan_library(lib_dir)
        self.assertIsNotNone(result)

        actuator = next(
            (c for c in result.categories if c.name == "actuator"), None
        )
        self.assertIsNotNone(actuator)
        self.assertEqual(actuator.file_count, 2)
        self.assertEqual(actuator.spec_count, 1)

    def test_tc_l03_spec_dir_identification(self):
        """TC-L03: 规范目录识别"""
        lib_dir = self._make_dir("LibWithSpecs")
        self._make_file("LibWithSpecs", ".plc.json", content='{}')
        self._make_file("LibWithSpecs", "00_通用规范", "spec1.md", content="")
        self._make_file("LibWithSpecs", "00_通用规范", "spec2.yaml", content="")
        self._make_file("LibWithSpecs", "specs", "spec3.md", content="")

        result = LibraryService.scan_library(lib_dir)
        self.assertIsNotNone(result)
        self.assertGreaterEqual(len(result.spec_dirs), 2)

        spec_dir_names = [d["name"] for d in result.spec_dirs]
        self.assertIn("00_通用规范", spec_dir_names)
        self.assertIn("specs", spec_dir_names)

    def test_tc_l04_orphan_files(self):
        """TC-L04: 根目录孤立文件检测"""
        lib_dir = self._make_dir("OrphanLib")
        self._make_file("OrphanLib", ".plc.json", content='{}')
        self._make_file("OrphanLib", "orphan_block.scl", content="")
        self._make_file("OrphanLib", "orphan_spec.md", content="")

        result = LibraryService.scan_library(lib_dir)
        self.assertIsNotNone(result)
        self.assertGreater(len(result.orphan_files), 0)

        orphan_names = [f["name"] for f in result.orphan_files]
        self.assertIn("orphan_block.scl", orphan_names)
        self.assertIn("orphan_spec.md", orphan_names)

    def test_tc_l05_empty_library(self):
        """TC-L05: 空共享库返回零ST计数"""
        lib_dir = self._make_dir("EmptyLib")
        self._make_file("EmptyLib", ".plc.json", content='{}')

        result = LibraryService.scan_library(lib_dir)
        self.assertIsNotNone(result)
        self.assertEqual(result.total_st_files, 0)
        self.assertEqual(len(result.categories), 0)

    def test_nonexistent_library(self):
        """不存在的目录返回None"""
        result = LibraryService.scan_library(
            os.path.join(self._temp_root, "no_such_lib")
        )
        self.assertIsNone(result)


class TestArtifactTypeInference(_TempDirMixin, unittest.TestCase):
    """TC-L06: 资产类型推断测试"""

    def test_tc_l06_category_to_artifact_type(self):
        """TC-L06: 分类目录名正确推断资产类型"""
        type_mapping = {
            "actuator": LibraryArtifactType.FB,
            "timer": LibraryArtifactType.FB,
            "counter": LibraryArtifactType.FB,
            "edge": LibraryArtifactType.FB,
            "convert": LibraryArtifactType.FC,
            "analog": LibraryArtifactType.FB,
            "motion": LibraryArtifactType.FB,
            "communication": LibraryArtifactType.FC,
            "safety": LibraryArtifactType.FB,
        }
        for category_name, expected_type in type_mapping.items():
            result = LibraryService._infer_artifact_type(category_name)
            self.assertEqual(
                result, expected_type,
                f"分类 {category_name} 应推断为 {expected_type.value}",
            )

    def test_unknown_category_defaults_to_doc(self):
        """未知分类默认为DOC类型"""
        result = LibraryService._infer_artifact_type("custom_stuff")
        self.assertEqual(result, LibraryArtifactType.DOC)


class TestSpecDirIdentification(_TempDirMixin, unittest.TestCase):
    """TC-L07: 规范目录识别测试"""

    def test_tc_l07_identify_spec_dirs(self):
        """TC-L07: identify_spec_dirs 正确识别规范目录"""
        lib_dir = self._make_dir("SpecLib")
        self._make_file("SpecLib", ".plc.json", content='{}')
        self._make_dir("SpecLib", "00_通用规范")
        self._make_dir("SpecLib", "01_编程规范")
        self._make_dir("SpecLib", "actuator")

        spec_dirs = LibraryService.identify_spec_dirs(lib_dir)
        self.assertGreaterEqual(len(spec_dirs), 2)

        spec_names = [d["name"] for d in spec_dirs]
        self.assertIn("00_通用规范", spec_names)
        self.assertIn("01_编程规范", spec_names)
        self.assertNotIn("actuator", spec_names)


class TestLibrarySummary(_TempDirMixin, unittest.TestCase):
    """TC-L08: 共享库摘要测试"""

    def test_tc_l08_get_library_summary(self):
        """TC-L08: get_library_summary 返回完整摘要"""
        lib_dir = self._make_dir("SummaryLib")
        self._make_file("SummaryLib", ".plc.json", content='{}')
        self._make_file("SummaryLib", "timer", "FB_TON.scl", content="")
        self._make_file("SummaryLib", "timer", "FB_TONR.scl", content="")
        self._make_file("SummaryLib", "00_通用规范", "spec.md", content="")

        summary = LibraryService.get_library_summary(lib_dir)
        self.assertIsNotNone(summary)
        self.assertEqual(summary["library_name"], "SummaryLib")
        self.assertIn("timer", summary["category_names"])
        self.assertIn("00_通用规范", summary["spec_dir_names"])
        self.assertEqual(summary["total_st_files"], 2)
        self.assertGreaterEqual(summary["total_spec_files"], 1)


class TestArtifactRegistryLibraryScan(_TempDirMixin, unittest.TestCase):
    """TC-L09: ArtifactRegistryService 共享库资产扫描测试"""

    def test_tc_l09_scan_library_artifacts(self):
        """TC-L09: scan_library_artifacts 正确分类资产目录"""
        lib_dir = self._make_dir("RegLib")
        self._make_file("RegLib", ".plc.json", content='{}')
        self._make_dir("RegLib", "actuator")
        self._make_dir("RegLib", "timer")
        self._make_dir("RegLib", "00_通用规范")
        self._make_dir("RegLib", "custom_folder")

        artifacts = ArtifactRegistryService.scan_library_artifacts(lib_dir)
        self.assertGreaterEqual(len(artifacts), 4)

        type_map = {a["name"]: a for a in artifacts}
        self.assertEqual(type_map["actuator"]["type"], "actuator")
        self.assertEqual(type_map["timer"]["type"], "timer")
        self.assertTrue(type_map["00_通用规范"]["is_spec_dir"])
        self.assertEqual(type_map["custom_folder"]["type"], "other")

    def test_identify_spec_dirs_in_library(self):
        """ArtifactRegistryService 规范目录识别"""
        lib_dir = self._make_dir("RegLib2")
        self._make_file("RegLib2", ".plc.json", content='{}')
        self._make_dir("RegLib2", "00_通用规范")
        self._make_dir("RegLib2", "standards")
        self._make_dir("RegLib2", "actuator")

        spec_dirs = ArtifactRegistryService.identify_spec_dirs_in_library(lib_dir)
        spec_names = [d["name"] for d in spec_dirs]
        self.assertIn("00_通用规范", spec_names)
        self.assertIn("standards", spec_names)
        self.assertNotIn("actuator", spec_names)


class TestLibraryScanResultSerialization(_TempDirMixin, unittest.TestCase):
    """扫描结果序列化测试"""

    def test_scan_result_to_dict(self):
        """LibraryScanResult.to_dict() 结构完整"""
        lib_dir = self._make_dir("DictLib")
        self._make_file("DictLib", ".plc.json", content='{}')
        self._make_file("DictLib", "timer", "FB_TON.scl", content="")

        result = LibraryService.scan_library(lib_dir)
        self.assertIsNotNone(result)

        d = result.to_dict()
        self.assertIn("library_path", d)
        self.assertIn("library_name", d)
        self.assertIn("total_artifacts", d)
        self.assertIn("total_st_files", d)
        self.assertIn("total_spec_files", d)
        self.assertIn("categories", d)
        self.assertIn("spec_dirs", d)
        self.assertIn("orphan_files", d)

    def test_library_artifact_to_dict(self):
        """LibraryArtifact.to_dict() 结构完整"""
        from src.services.library_service import LibraryArtifact
        artifact = LibraryArtifact(
            name="timer",
            artifact_type=LibraryArtifactType.FB,
            relative_path="timer",
            absolute_path="/tmp/timer",
            category="timer",
            file_count=3,
            spec_count=1,
        )
        d = artifact.to_dict()
        self.assertEqual(d["name"], "timer")
        self.assertEqual(d["artifact_type"], "fb")
        self.assertEqual(d["file_count"], 3)


if __name__ == "__main__":
    unittest.main()
