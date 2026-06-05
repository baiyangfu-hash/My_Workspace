"""ProjectOverviewService 单元测试"""

from __future__ import annotations

import os

import pytest

from src.services.project_overview_service import ProjectOverviewService


class TestProjectOverviewService:
    """项目总览 Service 测试"""

    def test_get_workspace_projects(self, workspace_root: str) -> None:
        """测试获取工作空间下所有项目"""
        if not os.path.isdir(workspace_root):
            pytest.skip("工作空间目录不存在")

        svc = ProjectOverviewService(workspace_root)
        projects = svc.get_workspace_projects()

        assert isinstance(projects, list)
        # 至少应该有 DJ-2026-005
        project_ids = [p.project_id for p in projects]
        assert "DJ-2026-005" in project_ids

    def test_get_project_detail(self, workspace_root: str, project_id: str) -> None:
        """测试获取单个项目详情"""
        if not os.path.isdir(workspace_root):
            pytest.skip("工作空间目录不存在")

        svc = ProjectOverviewService(workspace_root)
        info = svc.get_project_detail(project_id)

        assert info is not None
        assert info.project_id == project_id
        assert info.name != "待补充"
        assert info.proj_file_path != ""

    def test_get_project_detail_not_found(self, workspace_root: str) -> None:
        """测试查询不存在的项目"""
        svc = ProjectOverviewService(workspace_root)
        info = svc.get_project_detail("NONEXISTENT-9999-999")

        assert info is None

    def test_get_project_changes(self, workspace_root: str, project_id: str) -> None:
        """测试获取项目变更单列表"""
        if not os.path.isdir(workspace_root):
            pytest.skip("工作空间目录不存在")

        svc = ProjectOverviewService(workspace_root)
        changes = svc.get_project_changes(project_id)

        assert isinstance(changes, list)
        # DJ-2026-005 应该有变更单
        if changes:
            assert changes[0].change_number.startswith("CHG-")

    def test_cache_mechanism(self, workspace_root: str, project_id: str) -> None:
        """测试缓存机制"""
        if not os.path.isdir(workspace_root):
            pytest.skip("工作空间目录不存在")

        svc = ProjectOverviewService(workspace_root)

        # 第一次查询
        info1 = svc.get_project_detail(project_id)
        assert info1 is not None

        # 第二次查询应命中缓存
        info2 = svc.get_project_detail(project_id)
        assert info2 is not None
        assert info1.proj_file_path == info2.proj_file_path

    def test_refresh_cache(self, workspace_root: str, project_id: str) -> None:
        """测试刷新缓存"""
        if not os.path.isdir(workspace_root):
            pytest.skip("工作空间目录不存在")

        svc = ProjectOverviewService(workspace_root)

        # 先查询一次填充缓存
        svc.get_project_detail(project_id)

        # 刷新指定项目
        svc.refresh(project_id)

        # 刷新后缓存应被清除
        assert len(svc._cache) == 0 or not any(
            project_id in str(k) for k in svc._cache
        )

    def test_change_stats(self, workspace_root: str, project_id: str) -> None:
        """测试变更统计"""
        if not os.path.isdir(workspace_root):
            pytest.skip("工作空间目录不存在")

        svc = ProjectOverviewService(workspace_root)
        info = svc.get_project_detail(project_id)

        assert info is not None
        assert info.change_count >= 0
        assert info.pending_change_count >= 0
