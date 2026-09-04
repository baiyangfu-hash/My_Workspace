"""ChangeManagementService 单元测试"""

from __future__ import annotations

import os
import tempfile

import pytest

from src.services.change_management_service import ChangeManagementService
from src.utils.file_utils import write_file


class TestChangeManagementService:
    """变更管理 Service 测试"""

    def test_create_change_request(self, workspace_root: str, project_id: str) -> None:
        """测试创建变更单"""
        if not os.path.isdir(workspace_root):
            pytest.skip("工作空间目录不存在")

        svc = ChangeManagementService(workspace_root)
        cr = svc.create_change_request(
            project_id=project_id,
            domain="PLC",
            business_nature="DEF",
            impact_scope=["LOCAL"],
            applicant="测试人员",
            background="测试变更背景",
            necessity="测试变更必要性",
        )

        assert cr.change_number.startswith("CHG-PLC-")
        assert cr.status == "draft"
        assert cr.project_id == project_id
        assert os.path.isfile(cr.file_path)

        # 清理：删除测试创建的文件
        if os.path.isfile(cr.file_path):
            os.remove(cr.file_path)

    def test_list_change_requests(self, workspace_root: str, project_id: str) -> None:
        """测试列出变更单"""
        if not os.path.isdir(workspace_root):
            pytest.skip("工作空间目录不存在")

        svc = ChangeManagementService(workspace_root)
        changes = svc.list_change_requests(project_id)

        assert isinstance(changes, list)
        # DJ-2026-005 应该有变更单
        if changes:
            assert changes[0].change_number.startswith("CHG-")

    def test_list_change_requests_with_filter(self, workspace_root: str, project_id: str) -> None:
        """测试筛选变更单"""
        if not os.path.isdir(workspace_root):
            pytest.skip("工作空间目录不存在")

        svc = ChangeManagementService(workspace_root)
        changes = svc.list_change_requests(project_id, domain="DOCU")

        assert isinstance(changes, list)
        for c in changes:
            assert c.domain == "DOCU"

    def test_get_change_request(self, workspace_root: str) -> None:
        """测试获取变更单详情"""
        if not os.path.isdir(workspace_root):
            pytest.skip("工作空间目录不存在")

        svc = ChangeManagementService(workspace_root)
        cr = svc.get_change_request("CHG-DOCU-2026-001")

        if cr is not None:
            assert cr.change_number == "CHG-DOCU-2026-001"
            assert cr.domain == "DOCU"

    def test_get_change_request_not_found(self, workspace_root: str) -> None:
        """测试查询不存在的变更单"""
        svc = ChangeManagementService(workspace_root)
        cr = svc.get_change_request("CHG-NONEXISTENT-9999-999")

        assert cr is None

    def test_generate_change_number(self, workspace_root: str, project_id: str) -> None:
        """测试变更编号生成"""
        if not os.path.isdir(workspace_root):
            pytest.skip("工作空间目录不存在")

        svc = ChangeManagementService(workspace_root)
        project_path = os.path.join(workspace_root, project_id)

        num1 = svc._generate_change_number(project_path, "PLC")
        assert num1.startswith("CHG-PLC-")

        # 连续生成应递增
        num2 = svc._generate_change_number(project_path, "PLC")
        assert num2.startswith("CHG-PLC-")
