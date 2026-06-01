# -*- coding: utf-8 -*-
"""
工作空间支持测试 - TC-W01 ~ TC-W09

覆盖工作空间识别、加载、UI分支等核心场景。
"""
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from src.core.constants import (
    BusinessLine,
    PLC_LIBRARY_CATEGORY_DIRS,
    ProjectType,
    WORKSPACE_IGNORED_DIRS,
)
from src.services.artifact_registry_service import ArtifactRegistryService
from src.services.project_service import ProjectService


class _TempDirMixin:
    """临时目录管理混入"""

    def setUp(self):
        self._temp_root = tempfile.mkdtemp(prefix="ws_test_")

    def tearDown(self):
        if os.path.exists(self._temp_root):
            shutil.rmtree(self._temp_root, ignore_errors=True)

    def _make_dir(self, *parts):
        d = os.path.join(self._temp_root, *parts)
        os.makedirs(d, exist_ok=True)
        return d

    def _make_file(self, *parts, content=""):
        d = os.path.dirname(os.path.join(self._temp_root, *parts))
        os.makedirs(d, exist_ok=True)
        fpath = os.path.join(self._temp_root, *parts)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
        return fpath


class TestDetectProjectType(_TempDirMixin, unittest.TestCase):
    """TC-W01 ~ TC-W06: 项目类型识别测试"""

    def test_tc_w01_explicit_workspace_json(self):
        """TC-W01: 显式 workspace.json -> PLC_WORKSPACE"""
        ws_dir = self._make_dir("workspace01")
        self._make_file("workspace01", "workspace.json", content='{"name": "test"}')
        result = ArtifactRegistryService.detect_project_type(ws_dir)
        self.assertEqual(result, ProjectType.PLC_WORKSPACE)

    def test_tc_w02_multi_dj_subdirs(self):
        """TC-W02: 多 DJ 子目录 -> PLC_WORKSPACE"""
        ws_dir = self._make_dir("workspace02")
        for name in ("DJ-001", "DJ-002"):
            dj_dir = self._make_dir("workspace02", name)
            for marker in ArtifactRegistryService.DJ_ROOT_MARKERS:
                self._make_dir("workspace02", name, marker)
        result = ArtifactRegistryService.detect_project_type(ws_dir)
        self.assertEqual(result, ProjectType.PLC_WORKSPACE)

    def test_tc_w03_dj_plus_syslib(self):
        """TC-W03: DJ + SysLib 混合目录 -> PLC_WORKSPACE"""
        ws_dir = self._make_dir("workspace03")
        dj_dir = self._make_dir("workspace03", "DJ-001")
        for marker in ArtifactRegistryService.DJ_ROOT_MARKERS:
            self._make_dir("workspace03", "DJ-001", marker)
        lib_dir = self._make_dir("workspace03", "SysLib")
        self._make_file("workspace03", "SysLib", ".plc.json", content='{}')
        self._make_dir("workspace03", "SysLib", "timer")
        self._make_dir("workspace03", "SysLib", "counter")
        result = ArtifactRegistryService.detect_project_type(ws_dir)
        self.assertEqual(result, ProjectType.PLC_WORKSPACE)

    def test_tc_w04_single_dj_project(self):
        """TC-W04: 单一 DJ 项目 -> DJ_SINGLE_MACHINE (不误判工作空间)"""
        dj_dir = self._make_dir("single_dj")
        for marker in ArtifactRegistryService.DJ_ROOT_MARKERS:
            self._make_dir("single_dj", marker)
        result = ArtifactRegistryService.detect_project_type(dj_dir)
        self.assertEqual(result, ProjectType.DJ_SINGLE_MACHINE)

    def test_tc_w05_plc_library(self):
        """TC-W05: .plc.json + 共享库分类目录 -> PLC_LIBRARY"""
        lib_dir = self._make_dir("my_library")
        self._make_file("my_library", ".plc.json", content='{}')
        self._make_dir("my_library", "actuator")
        self._make_dir("my_library", "timer")
        result = ArtifactRegistryService.detect_project_type(lib_dir)
        self.assertEqual(result, ProjectType.PLC_LIBRARY)

    def test_tc_w06_empty_directory(self):
        """TC-W06: 空目录 -> GENERIC"""
        empty_dir = self._make_dir("empty_dir")
        result = ArtifactRegistryService.detect_project_type(empty_dir)
        self.assertEqual(result, ProjectType.GENERIC)

    def test_nonexistent_directory(self):
        """不存在的目录 -> GENERIC"""
        result = ArtifactRegistryService.detect_project_type(
            os.path.join(self._temp_root, "no_such_dir")
        )
        self.assertEqual(result, ProjectType.GENERIC)

    def test_single_generic_subproject_not_workspace(self):
        """只有1个普通子项目 -> 不隐式判定为工作空间"""
        ws_dir = self._make_dir("one_sub")
        self._make_file("one_sub", "sub1", "project.json", content='{}')
        result = ArtifactRegistryService.detect_project_type(ws_dir)
        self.assertEqual(result, ProjectType.GENERIC)

    def test_two_generic_subprojects_is_workspace(self):
        """2个普通子项目 -> PLC_WORKSPACE"""
        ws_dir = self._make_dir("two_subs")
        self._make_file("two_subs", "sub1", "project.json", content='{}')
        self._make_file("two_subs", "sub2", "project.json", content='{}')
        result = ArtifactRegistryService.detect_project_type(ws_dir)
        self.assertEqual(result, ProjectType.PLC_WORKSPACE)


class TestWorkspaceLoading(_TempDirMixin, unittest.TestCase):
    """TC-W07 ~ TC-W08: 工作空间加载测试"""

    def test_tc_w07_workspace_aggregate_loading(self):
        """TC-W07: 工作空间聚合加载 -> 返回所有可管理子项目"""
        ws_dir = self._make_dir("workspace07")
        self._make_file("workspace07", "workspace.json", content='{"name": "ws07"}')

        dj_dir = self._make_dir("workspace07", "DJ-001")
        for marker in ArtifactRegistryService.DJ_ROOT_MARKERS:
            self._make_dir("workspace07", "DJ-001", marker)

        lib_dir = self._make_dir("workspace07", "SysLib")
        self._make_file("workspace07", "SysLib", ".plc.json", content='{}')
        self._make_dir("workspace07", "SysLib", "timer")

        gen_dir = self._make_dir("workspace07", "GenProject")
        self._make_file(
            "workspace07", "GenProject", "project.json",
            content=json.dumps({
                "name": "GenProject",
                "project_id": "gen-001",
                "business_line": "SW",
                "status": "planning",
                "project_type": "generic",
                "workflow_stage": "initiation",
                "plc_brand": "Codesys",
                "hmi_brand": "Weinview",
            }),
        )

        projects, error = ProjectService.load_workspace_from_path(ws_dir)
        self.assertIsNone(error, f"加载不应失败: {error}")
        self.assertIsNotNone(projects)
        self.assertGreaterEqual(len(projects), 2)

        project_names = [p.name for p in projects]
        self.assertIn("DJ-001", project_names)
        self.assertIn("SysLib", project_names)

    def test_tc_w08_ignored_dirs(self):
        """TC-W08: .trae 等忽略目录不影响结果"""
        ws_dir = self._make_dir("workspace08")
        self._make_file("workspace08", "workspace.json", content='{}')

        dj_dir = self._make_dir("workspace08", "DJ-001")
        for marker in ArtifactRegistryService.DJ_ROOT_MARKERS:
            self._make_dir("workspace08", "DJ-001", marker)

        for ignored in (".trae", ".git", "__pycache__", "_archive", "node_modules", ".venvs"):
            self._make_dir("workspace08", ignored)

        subprojects = ArtifactRegistryService.scan_workspace_subprojects(ws_dir)
        sub_names = [s["name"] for s in subprojects]
        for ignored in (".trae", ".git", "__pycache__", "_archive", "node_modules", ".venvs"):
            self.assertNotIn(ignored, sub_names)

        self.assertIn("DJ-001", sub_names)

    def test_workspace_no_manageable_subprojects(self):
        """工作空间下无可管理子项目 -> 返回错误"""
        ws_dir = self._make_dir("workspace_empty")
        self._make_file("workspace_empty", "workspace.json", content='{}')
        self._make_dir("workspace_empty", "random_stuff")

        projects, error = ProjectService.load_workspace_from_path(ws_dir)
        self.assertIsNotNone(error)
        self.assertIsNone(projects)

    def test_non_workspace_path_rejected(self):
        """非工作空间路径被拒绝"""
        ws_dir = self._make_dir("not_a_workspace")
        projects, error = ProjectService.load_workspace_from_path(ws_dir)
        self.assertIsNotNone(error)
        self.assertIsNone(projects)

    def test_nonexistent_path_rejected(self):
        """不存在的路径被拒绝"""
        projects, error = ProjectService.load_workspace_from_path(
            os.path.join(self._temp_root, "no_such_dir")
        )
        self.assertIsNotNone(error)
        self.assertIsNone(projects)


class TestSingleProjectRegression(_TempDirMixin, unittest.TestCase):
    """单项目打开逻辑无回归验证"""

    def test_dj_project_load_still_works(self):
        """DJ 单机项目仍能正常加载"""
        dj_dir = self._make_dir("DJ-REG-001")
        for marker in ArtifactRegistryService.DJ_ROOT_MARKERS:
            self._make_dir("DJ-REG-001", marker)

        project, error = ProjectService.load_project_from_path(dj_dir)
        self.assertIsNone(error, f"DJ项目加载不应失败: {error}")
        self.assertIsNotNone(project)
        self.assertEqual(project.project_type, ProjectType.DJ_SINGLE_MACHINE)

    def test_generic_project_with_config_still_works(self):
        """含 project.json 的通用项目仍能正常加载"""
        gen_dir = self._make_dir("GenProject")
        self._make_file(
            "GenProject", "project.json",
            content=json.dumps({
                "name": "GenProject",
                "project_id": "gen-reg-001",
                "business_line": "SW",
                "status": "planning",
                "project_type": "generic",
                "workflow_stage": "initiation",
                "plc_brand": "Codesys",
                "hmi_brand": "Weinview",
            }),
        )

        project, error = ProjectService.load_project_from_path(gen_dir)
        self.assertIsNone(error, f"通用项目加载不应失败: {error}")
        self.assertIsNotNone(project)
        self.assertEqual(project.name, "GenProject")

    def test_library_project_type_preserved(self):
        """共享库降级 Project 的 project_type 正确保留"""
        lib_dir = self._make_dir("TestLib")
        self._make_file("TestLib", ".plc.json", content='{}')
        self._make_dir("TestLib", "actuator")

        project = ProjectService._create_library_project(lib_dir)
        self.assertEqual(project.project_type, ProjectType.PLC_LIBRARY)
        self.assertEqual(project.business_line, BusinessLine.LIBRARY)
        self.assertTrue(project.extra.get("_workspace_child"))

    def test_workspace_child_marker(self):
        """工作空间子项目标记 _workspace_child 正确设置"""
        ws_dir = self._make_dir("ws_marker")
        self._make_file("ws_marker", "workspace.json", content='{}')

        dj_dir = self._make_dir("ws_marker", "DJ-001")
        for marker in ArtifactRegistryService.DJ_ROOT_MARKERS:
            self._make_dir("ws_marker", "DJ-001", marker)

        projects, error = ProjectService.load_workspace_from_path(ws_dir)
        self.assertIsNone(error)
        self.assertIsNotNone(projects)
        for p in projects:
            self.assertTrue(
                p.extra.get("_workspace_child"),
                f"子项目 {p.name} 应标记 _workspace_child",
            )


class TestScanWorkspaceSubprojects(_TempDirMixin, unittest.TestCase):
    """scan_workspace_subprojects 详细测试"""

    def test_mixed_subprojects(self):
        """混合子项目正确分类"""
        ws_dir = self._make_dir("ws_mixed")
        self._make_file("ws_mixed", "workspace.json", content='{}')

        dj_dir = self._make_dir("ws_mixed", "DJ-001")
        for marker in ArtifactRegistryService.DJ_ROOT_MARKERS:
            self._make_dir("ws_mixed", "DJ-001", marker)

        lib_dir = self._make_dir("ws_mixed", "SysLib")
        self._make_file("ws_mixed", "SysLib", ".plc.json", content='{}')
        self._make_dir("ws_mixed", "SysLib", "timer")

        gen_dir = self._make_dir("ws_mixed", "GenProj")
        self._make_file("ws_mixed", "GenProj", "project.json", content='{}')

        subs = ArtifactRegistryService.scan_workspace_subprojects(ws_dir)
        self.assertEqual(len(subs), 3)

        type_map = {s["name"]: s["type"] for s in subs}
        self.assertEqual(type_map["DJ-001"], ProjectType.DJ_SINGLE_MACHINE.value)
        self.assertEqual(type_map["SysLib"], ProjectType.PLC_LIBRARY.value)
        self.assertEqual(type_map["GenProj"], ProjectType.GENERIC.value)

    def test_no_subprojects_in_empty_workspace(self):
        """空工作空间无子项目"""
        ws_dir = self._make_dir("ws_empty")
        self._make_file("ws_empty", "workspace.json", content='{}')
        self._make_dir("ws_empty", "random_folder")

        subs = ArtifactRegistryService.scan_workspace_subprojects(ws_dir)
        self.assertEqual(len(subs), 0)


if __name__ == "__main__":
    unittest.main()
