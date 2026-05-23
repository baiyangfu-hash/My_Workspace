# -*- coding: utf-8 -*-
"""
BUG-OPEN-001 自动化测试套件

测试计划:
  T1  Controller白名单完整性
  T2  Controller白名单包含.plc.json
  T3  Controller检测-根目录有project.json放行
  T4  Controller检测-根目录有.plc_project.json放行
  T5  Controller检测-根目录有.plc.json放行
  T6  Controller检测-DJ目录结构(无配置文件)放行
  T7  Controller检测-空目录拦截
  T8  Controller检测-非DJ无配置目录拦截
  T9  Service-import_dj_project从.plc_project.json加载
  T10 Service-import_dj_project从.plc.json加载
  T11 Service-import_dj_project从project.json加载
  T12 Service-import_dj_project无配置文件时创建虚拟Project
  T13 Service-load_project_from_path识别DJ项目
  T14 Service-load_project_from_path识别通用项目
  T15 ArtifactRegistry-detect_project_type识别DJ
  T16 ArtifactRegistry-detect_project_type识别GENERIC
  T17 集成-DJ-2026-005真实项目端到端加载
  T18 集成-配置文件损坏时降级处理
"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent / "src"))


class TestControllerWhitelist(unittest.TestCase):
    """T1-T2: Controller白名单完整性"""

    def test_t01_whitelist_contains_all_formats(self):
        from src.ui.controllers.project_controller import ProjectController
        controller = ProjectController(main_window=None)
        expected = ["project.json", ".plc_project.json", ".plc.json"]
        for fmt in expected:
            self.assertIn(fmt, controller.SUPPORTED_PROJECT_FILES,
                         f"白名单缺少: {fmt}")

    def test_t02_whitelist_has_plc_json(self):
        from src.ui.controllers.project_controller import ProjectController
        controller = ProjectController(main_window=None)
        self.assertIn(".plc.json", controller.SUPPORTED_PROJECT_FILES)


class TestControllerDetection(unittest.TestCase):
    """T3-T8: Controller项目检测逻辑"""

    def _make_controller(self):
        from src.ui.controllers.project_controller import ProjectController
        mw = MagicMock()
        mw.get_project_tree_widget.return_value = MagicMock()
        return ProjectController(main_window=mw)

    def test_t03_root_project_json_passes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "project.json").write_text("{}", encoding="utf-8")
            controller = self._make_controller()
            has_root = any(
                (Path(tmpdir) / f).exists()
                for f in controller.SUPPORTED_PROJECT_FILES
            )
            self.assertTrue(has_root, "有project.json时应放行")

    def test_t04_root_plc_project_json_passes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".plc_project.json").write_text("{}", encoding="utf-8")
            controller = self._make_controller()
            has_root = any(
                (Path(tmpdir) / f).exists()
                for f in controller.SUPPORTED_PROJECT_FILES
            )
            self.assertTrue(has_root, "有.plc_project.json时应放行")

    def test_t05_root_plc_json_passes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".plc.json").write_text("{}", encoding="utf-8")
            controller = self._make_controller()
            has_root = any(
                (Path(tmpdir) / f).exists()
                for f in controller.SUPPORTED_PROJECT_FILES
            )
            self.assertTrue(has_root, "有.plc.json时应放行")

    def test_t06_dj_structure_no_config_passes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "00_项目管理").mkdir()
            (root / "02_PLC程序").mkdir()
            (root / "03_HMI设计").mkdir()

            from src.services.artifact_registry_service import ArtifactRegistryService
            from src.core.constants import ProjectType
            detected = ArtifactRegistryService.detect_project_type(str(root))
            self.assertEqual(detected, ProjectType.DJ_SINGLE_MACHINE,
                             "DJ标记目录完整时应识别为DJ项目")

    def test_t07_empty_dir_blocked(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            controller = self._make_controller()
            has_root = any(
                (Path(tmpdir) / f).exists()
                for f in controller.SUPPORTED_PROJECT_FILES
            )
            from src.services.artifact_registry_service import ArtifactRegistryService
            from src.core.constants import ProjectType
            detected = ArtifactRegistryService.detect_project_type(str(tmpdir))
            is_dj = (detected == ProjectType.DJ_SINGLE_MACHINE)

            should_block = not has_root and not is_dj
            self.assertTrue(should_block, "空目录应被拦截")

    def test_t08_non_dj_no_config_blocked(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "some_folder").mkdir()
            (root / "readme.txt").write_text("hello", encoding="utf-8")

            controller = self._make_controller()
            has_root = any(
                (Path(tmpdir) / f).exists()
                for f in controller.SUPPORTED_PROJECT_FILES
            )
            from src.services.artifact_registry_service import ArtifactRegistryService
            from src.core.constants import ProjectType
            detected = ArtifactRegistryService.detect_project_type(str(tmpdir))
            is_dj = (detected == ProjectType.DJ_SINGLE_MACHINE)

            should_block = not has_root and not is_dj
            self.assertTrue(should_block, "非DJ无配置目录应被拦截")


class TestServiceImportDjProject(unittest.TestCase):
    """T9-T12: Service层import_dj_project多格式支持"""

    def _create_dj_structure(self, root: Path):
        (root / "00_项目管理").mkdir()
        (root / "02_PLC程序").mkdir()
        (root / "03_HMI设计").mkdir()

    def test_t09_load_from_plc_project_json(self):
        from src.services.project_service import ProjectService
        ProjectService._projects.clear()

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._create_dj_structure(root)

            meta = {
                "name": "TestProject",
                "code": "DJ-TEST-001",
                "description": "test",
                "business_line": "DJ",
                "status": "active",
                "plc_brand": "Codesys",
                "hmi_brand": "Weinview",
                "manager": "tester",
                "project_type": "dj_single_machine",
                "workflow_stage": "design",
            }
            (root / ".plc_project.json").write_text(
                json.dumps(meta, ensure_ascii=False), encoding="utf-8"
            )

            project, error = ProjectService.import_dj_project(str(root))
            self.assertIsNotNone(project, f"应成功加载, 错误: {error}")
            self.assertEqual(project.name, "TestProject")

    def test_t10_load_from_plc_json(self):
        from src.services.project_service import ProjectService
        ProjectService._projects.clear()

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._create_dj_structure(root)

            meta = {
                "name": "PLCJsonProject",
                "code": "DJ-PLC-001",
                "description": "from .plc.json",
                "business_line": "DJ",
                "status": "active",
                "plc_brand": "Codesys",
                "hmi_brand": "Weinview",
                "manager": "tester",
                "project_type": "dj_single_machine",
                "workflow_stage": "development",
            }
            (root / ".plc.json").write_text(
                json.dumps(meta, ensure_ascii=False), encoding="utf-8"
            )

            project, error = ProjectService.import_dj_project(str(root))
            self.assertIsNotNone(project, f"应从.plc.json加载, 错误: {error}")
            self.assertEqual(project.name, "PLCJsonProject")

    def test_t11_load_from_project_json(self):
        from src.services.project_service import ProjectService
        ProjectService._projects.clear()

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._create_dj_structure(root)

            meta = {
                "name": "OldProject",
                "code": "DJ-OLD-001",
                "description": "from project.json",
                "business_line": "DJ",
                "status": "planning",
                "plc_brand": "Codesys",
                "hmi_brand": "Weinview",
                "manager": "tester",
                "project_type": "dj_single_machine",
                "workflow_stage": "initiation",
            }
            (root / "project.json").write_text(
                json.dumps(meta, ensure_ascii=False), encoding="utf-8"
            )

            project, error = ProjectService.import_dj_project(str(root))
            self.assertIsNotNone(project, f"应从project.json加载, 错误: {error}")
            self.assertEqual(project.name, "OldProject")

    def test_t12_no_config_creates_virtual_project(self):
        from src.services.project_service import ProjectService
        ProjectService._projects.clear()

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._create_dj_structure(root)

            project, error = ProjectService.import_dj_project(str(root))
            self.assertIsNotNone(project, "无配置文件时应创建虚拟Project")
            self.assertEqual(project.project_type.value, "dj_single_machine")
            self.assertIn(root.name, project.name)


class TestServiceLoadFromPath(unittest.TestCase):
    """T13-T14: Service层load_project_from_path"""

    def test_t13_dj_project_auto_detected(self):
        from src.services.project_service import ProjectService
        ProjectService._projects.clear()

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "00_项目管理").mkdir()
            (root / "02_PLC程序").mkdir()
            (root / "03_HMI设计").mkdir()

            project, error = ProjectService.load_project_from_path(str(root))
            self.assertIsNotNone(project, f"DJ项目应自动识别, 错误: {error}")
            self.assertEqual(project.project_type.value, "dj_single_machine")

    def test_t14_generic_project_needs_project_json(self):
        from src.services.project_service import ProjectService
        ProjectService._projects.clear()

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "some_dir").mkdir()

            project, error = ProjectService.load_project_from_path(str(root))
            self.assertIsNone(project, "通用项目无project.json应返回None")
            self.assertIsNotNone(error, "应有错误信息")


class TestArtifactRegistryDetection(unittest.TestCase):
    """T15-T16: ArtifactRegistry项目类型检测"""

    def test_t15_detect_dj_single_machine(self):
        from src.services.artifact_registry_service import ArtifactRegistryService
        from src.core.constants import ProjectType

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "00_项目管理").mkdir()
            (root / "02_PLC程序").mkdir()
            (root / "03_HMI设计").mkdir()

            result = ArtifactRegistryService.detect_project_type(str(root))
            self.assertEqual(result, ProjectType.DJ_SINGLE_MACHINE)

    def test_t16_detect_generic(self):
        from src.services.artifact_registry_service import ArtifactRegistryService
        from src.core.constants import ProjectType

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "random_dir").mkdir()

            result = ArtifactRegistryService.detect_project_type(str(root))
            self.assertEqual(result, ProjectType.GENERIC)

    def test_t16b_partial_dj_markers_is_generic(self):
        from src.services.artifact_registry_service import ArtifactRegistryService
        from src.core.constants import ProjectType

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "00_项目管理").mkdir()
            (root / "02_PLC程序").mkdir()

            result = ArtifactRegistryService.detect_project_type(str(root))
            self.assertEqual(result, ProjectType.GENERIC,
                             "缺少03_HMI设计应为GENERIC")


class TestIntegrationRealProject(unittest.TestCase):
    """T17: 真实DJ-2026-005端到端集成测试"""

    DJ_PROJECT_PATH = r"C:\Users\fubai\Desktop\My_Workspace\0100_PLC自动化\DJ-2026-005"

    def setUp(self):
        if not Path(self.DJ_PROJECT_PATH).exists():
            self.skipTest(f"真实项目路径不存在: {self.DJ_PROJECT_PATH}")

    def test_t17_load_dj_2026_005(self):
        from src.services.project_service import ProjectService
        ProjectService._projects.clear()

        project, error = ProjectService.load_project_from_path(self.DJ_PROJECT_PATH)

        self.assertIsNone(error, f"加载不应有错误: {error}")
        self.assertIsNotNone(project, "应返回有效的Project对象")
        self.assertEqual(project.project_type.value, "dj_single_machine")
        self.assertIn("DJ-2026-005", project.name)
        self.assertTrue(len(project.path) > 0)


class TestCorruptedConfigFallback(unittest.TestCase):
    """T18: 配置文件损坏时降级处理"""

    def _create_dj_structure(self, root: Path):
        (root / "00_项目管理").mkdir()
        (root / "02_PLC程序").mkdir()
        (root / "03_HMI设计").mkdir()

    def test_t18_corrupted_plc_json_fallback(self):
        from src.services.project_service import ProjectService
        ProjectService._projects.clear()

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._create_dj_structure(root)

            (root / ".plc_project.json").write_text(
                "{invalid json content!!!", encoding="utf-8"
            )

            project, error = ProjectService.import_dj_project(str(root))
            self.assertIsNotNone(project,
                                 "配置文件损坏时应降级创建虚拟Project")
            self.assertEqual(project.project_type.value, "dj_single_machine")


if __name__ == "__main__":
    unittest.main(verbosity=2)
