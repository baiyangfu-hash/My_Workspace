# -*- coding: utf-8 -*-
"""
工作空间治理测试 - TC-G01 ~ TC-G09

覆盖 WorkspaceService 跨项目检查、聚合报告、汇总统计、命名冲突等核心场景。
"""
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from src.core.constants import ProjectType
from src.services.artifact_registry_service import ArtifactRegistryService
from src.services.workspace_service import WorkspaceService


class _TempDirMixin:
    """临时目录管理混入"""

    def setUp(self):
        self._temp_root = tempfile.mkdtemp(prefix="wsgov_test_")

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


class TestWorkspaceStatistics(_TempDirMixin, unittest.TestCase):
    """TC-G01 ~ TC-G03: 工作空间汇总统计测试"""

    def _build_workspace(self):
        ws_dir = self._make_dir("ws_stats")
        self._make_file("ws_stats", "workspace.json", content='{}')

        dj_dir = self._make_dir("ws_stats", "DJ-001")
        for marker in ArtifactRegistryService.DJ_ROOT_MARKERS:
            self._make_dir("ws_stats", "DJ-001", marker)
        self._make_file("ws_stats", "DJ-001", "02_PLC程序", "FB_Main.scl", content="FUNCTION_BLOCK FB_Main\nEND_FUNCTION_BLOCK")

        lib_dir = self._make_dir("ws_stats", "SysLib")
        self._make_file("ws_stats", "SysLib", ".plc.json", content='{}')
        self._make_dir("ws_stats", "SysLib", "timer")
        self._make_file("ws_stats", "SysLib", "timer", "FB_TON.scl", content="FUNCTION_BLOCK FB_TON\nEND_FUNCTION_BLOCK")

        return ws_dir

    def test_tc_g01_workspace_statistics(self):
        """TC-G01: 工作空间统计包含完整信息"""
        ws_dir = self._build_workspace()
        from src.services.project_service import ProjectService
        projects, _ = ProjectService.load_workspace_from_path(ws_dir)
        self.assertIsNotNone(projects)

        stats = WorkspaceService.get_workspace_statistics(ws_dir, projects)
        self.assertEqual(stats["total_projects"], 2)
        self.assertIn("total_st_files", stats)
        self.assertIn("total_spec_files", stats)
        self.assertIn("project_type_distribution", stats)

    def test_tc_g02_project_type_distribution(self):
        """TC-G02: 项目类型分布统计正确"""
        ws_dir = self._build_workspace()
        from src.services.project_service import ProjectService
        projects, _ = ProjectService.load_workspace_from_path(ws_dir)

        stats = WorkspaceService.get_workspace_statistics(ws_dir, projects)
        dist = stats["project_type_distribution"]
        self.assertIn("dj_single_machine", dist)
        self.assertIn("plc_library", dist)

    def test_tc_g03_naming_conflicts_count(self):
        """TC-G03: 命名冲突计数正确(无冲突时为0)"""
        ws_dir = self._build_workspace()
        from src.services.project_service import ProjectService
        projects, _ = ProjectService.load_workspace_from_path(ws_dir)

        stats = WorkspaceService.get_workspace_statistics(ws_dir, projects)
        self.assertEqual(stats["naming_conflicts"], 0)
        self.assertFalse(stats["has_issues"])


class TestNamingConflictDetection(_TempDirMixin, unittest.TestCase):
    """TC-G04 ~ TC-G05: 命名冲突检测测试"""

    def test_tc_g04_detect_fb_conflict(self):
        """TC-G04: 检测跨项目FB命名冲突"""
        ws_dir = self._make_dir("ws_conflict")
        self._make_file("ws_conflict", "workspace.json", content='{}')

        dj1_dir = self._make_dir("ws_conflict", "DJ-001")
        for marker in ArtifactRegistryService.DJ_ROOT_MARKERS:
            self._make_dir("ws_conflict", "DJ-001", marker)
        self._make_file("ws_conflict", "DJ-001", "02_PLC程序", "FB_Valve.scl", content="")

        dj2_dir = self._make_dir("ws_conflict", "DJ-002")
        for marker in ArtifactRegistryService.DJ_ROOT_MARKERS:
            self._make_dir("ws_conflict", "DJ-002", marker)
        self._make_file("ws_conflict", "DJ-002", "02_PLC程序", "FB_Valve.scl", content="")

        from src.services.project_service import ProjectService
        projects, _ = ProjectService.load_workspace_from_path(ws_dir)

        conflicts = WorkspaceService.detect_naming_conflicts(projects)
        conflict_names = [c.name for c in conflicts]
        self.assertIn("FB_Valve", conflict_names)

    def test_tc_g05_no_conflict_different_names(self):
        """TC-G05: 不同名称的FB不产生冲突"""
        ws_dir = self._make_dir("ws_no_conflict")
        self._make_file("ws_no_conflict", "workspace.json", content='{}')

        dj1_dir = self._make_dir("ws_no_conflict", "DJ-001")
        for marker in ArtifactRegistryService.DJ_ROOT_MARKERS:
            self._make_dir("ws_no_conflict", "DJ-001", marker)
        self._make_file("ws_no_conflict", "DJ-001", "02_PLC程序", "FB_Valve.scl", content="")

        dj2_dir = self._make_dir("ws_no_conflict", "DJ-002")
        for marker in ArtifactRegistryService.DJ_ROOT_MARKERS:
            self._make_dir("ws_no_conflict", "DJ-002", marker)
        self._make_file("ws_no_conflict", "DJ-002", "02_PLC程序", "FB_Motor.scl", content="")

        from src.services.project_service import ProjectService
        projects, _ = ProjectService.load_workspace_from_path(ws_dir)

        conflicts = WorkspaceService.detect_naming_conflicts(projects)
        self.assertEqual(len(conflicts), 0)


class TestWorkspaceCheck(_TempDirMixin, unittest.TestCase):
    """TC-G06 ~ TC-G07: 跨项目检查测试"""

    def test_tc_g06_check_existing_projects(self):
        """TC-G06: 存在的项目返回ok状态"""
        ws_dir = self._make_dir("ws_check_ok")
        self._make_file("ws_check_ok", "workspace.json", content='{}')

        dj_dir = self._make_dir("ws_check_ok", "DJ-001")
        for marker in ArtifactRegistryService.DJ_ROOT_MARKERS:
            self._make_dir("ws_check_ok", "DJ-001", marker)

        from src.services.project_service import ProjectService
        projects, _ = ProjectService.load_workspace_from_path(ws_dir)

        items = WorkspaceService.check_workspace(ws_dir, projects)
        ok_items = [i for i in items if i.status == "ok"]
        self.assertGreater(len(ok_items), 0)

    def test_tc_g07_check_missing_project_dir(self):
        """TC-G07: 不存在的项目目录返回error状态"""
        from src.core.project import Project
        from src.core.constants import BusinessLine, ProjectStatus, WorkflowStage, PLCBrand, HMIBrand

        fake_project = Project(
            name="GhostProject",
            code="ghost",
            path="/nonexistent/path/ghost",
            project_type=ProjectType.GENERIC,
        )

        items = WorkspaceService.check_workspace("/tmp", [fake_project])
        error_items = [i for i in items if i.severity == "error"]
        self.assertGreater(len(error_items), 0)


class TestWorkspaceReport(_TempDirMixin, unittest.TestCase):
    """TC-G08 ~ TC-G09: 聚合报告测试"""

    def test_tc_g08_generate_report(self):
        """TC-G08: 聚合报告包含完整信息"""
        ws_dir = self._make_dir("ws_report")
        self._make_file("ws_report", "workspace.json", content='{}')

        dj_dir = self._make_dir("ws_report", "DJ-001")
        for marker in ArtifactRegistryService.DJ_ROOT_MARKERS:
            self._make_dir("ws_report", "DJ-001", marker)
        self._make_file("ws_report", "DJ-001", "02_PLC程序", "FB_Main.scl", content="")

        lib_dir = self._make_dir("ws_report", "SysLib")
        self._make_file("ws_report", "SysLib", ".plc.json", content='{}')
        self._make_dir("ws_report", "SysLib", "timer")
        self._make_file("ws_report", "SysLib", "timer", "FB_TON.scl", content="")

        from src.services.project_service import ProjectService
        projects, _ = ProjectService.load_workspace_from_path(ws_dir)

        report = WorkspaceService.generate_report(ws_dir, projects)
        self.assertIsNotNone(report)
        self.assertEqual(report.workspace_name, "ws_report")
        self.assertEqual(report.total_projects, 2)
        self.assertGreater(report.total_st_files, 0)
        self.assertIn("generated_at", report.to_dict())

    def test_tc_g09_report_serialization(self):
        """TC-G09: 报告序列化结构完整"""
        ws_dir = self._make_dir("ws_serial")
        self._make_file("ws_serial", "workspace.json", content='{}')

        dj_dir = self._make_dir("ws_serial", "DJ-001")
        for marker in ArtifactRegistryService.DJ_ROOT_MARKERS:
            self._make_dir("ws_serial", "DJ-001", marker)

        from src.services.project_service import ProjectService
        projects, _ = ProjectService.load_workspace_from_path(ws_dir)

        report = WorkspaceService.generate_report(ws_dir, projects)
        d = report.to_dict()
        self.assertIn("workspace_path", d)
        self.assertIn("workspace_name", d)
        self.assertIn("generated_at", d)
        self.assertIn("total_projects", d)
        self.assertIn("total_st_files", d)
        self.assertIn("total_spec_files", d)
        self.assertIn("project_summaries", d)
        self.assertIn("check_items", d)
        self.assertIn("naming_conflicts", d)
        self.assertIn("library_summaries", d)


class TestProjectServiceWorkspaceAPI(_TempDirMixin, unittest.TestCase):
    """ProjectService 工作空间 API 测试"""

    def test_get_workspace_summary(self):
        """get_workspace_summary 返回有效统计"""
        ws_dir = self._make_dir("ws_api")
        self._make_file("ws_api", "workspace.json", content='{}')

        dj_dir = self._make_dir("ws_api", "DJ-001")
        for marker in ArtifactRegistryService.DJ_ROOT_MARKERS:
            self._make_dir("ws_api", "DJ-001", marker)

        from src.services.project_service import ProjectService
        stats, error = ProjectService.get_workspace_summary(ws_dir)
        self.assertIsNone(error)
        self.assertIsNotNone(stats)
        self.assertEqual(stats["total_projects"], 1)

    def test_generate_workspace_report(self):
        """generate_workspace_report 返回有效报告"""
        ws_dir = self._make_dir("ws_api2")
        self._make_file("ws_api2", "workspace.json", content='{}')

        dj_dir = self._make_dir("ws_api2", "DJ-001")
        for marker in ArtifactRegistryService.DJ_ROOT_MARKERS:
            self._make_dir("ws_api2", "DJ-001", marker)

        from src.services.project_service import ProjectService
        report, error = ProjectService.generate_workspace_report(ws_dir)
        self.assertIsNone(error)
        self.assertIsNotNone(report)
        self.assertEqual(report.workspace_name, "ws_api2")


if __name__ == "__main__":
    unittest.main()
