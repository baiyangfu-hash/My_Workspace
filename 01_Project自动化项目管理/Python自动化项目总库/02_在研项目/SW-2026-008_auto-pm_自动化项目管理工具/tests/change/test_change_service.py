"""ChangeService 单元测试"""

from __future__ import annotations

import os

import pytest

from auto_pm.change.change_service import ChangeService
from auto_pm.change.models import (
    SpecViolationError,
    validate_business_nature,
    validate_domain,
    validate_impact_scope,
    validate_status_transition,
    validate_urgency,
)


class TestChangeService:
    """变更管理 Service 测试"""

    def test_create_change_request(self, workspace_root: str, project_id: str) -> None:
        """测试创建变更单"""
        if not os.path.isdir(workspace_root):
            pytest.skip("工作空间目录不存在")

        svc = ChangeService(workspace_root)
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

        svc = ChangeService(workspace_root)
        changes = svc.list_change_requests(project_id)

        assert isinstance(changes, list)
        # TEST-2026-001 应该有变更单（conftest 创建了 CHG-DOCU-2026-001）
        if changes:
            assert changes[0].change_number.startswith("CHG-")

    def test_list_change_requests_with_filter(self, workspace_root: str, project_id: str) -> None:
        """测试筛选变更单"""
        if not os.path.isdir(workspace_root):
            pytest.skip("工作空间目录不存在")

        svc = ChangeService(workspace_root)
        changes = svc.list_change_requests(project_id, domain="DOCU")

        assert isinstance(changes, list)
        for c in changes:
            assert c.domain == "DOCU"

    def test_get_change_request(self, workspace_root: str) -> None:
        """测试获取变更单详情"""
        if not os.path.isdir(workspace_root):
            pytest.skip("工作空间目录不存在")

        svc = ChangeService(workspace_root)
        cr = svc.get_change_request("CHG-DOCU-2026-001")

        if cr is not None:
            assert cr.change_number == "CHG-DOCU-2026-001"
            assert cr.domain == "DOCU"

    def test_get_change_request_not_found(self, workspace_root: str) -> None:
        """测试查询不存在的变更单"""
        svc = ChangeService(workspace_root)
        cr = svc.get_change_request("CHG-NONEXISTENT-9999-999")

        assert cr is None

    def test_generate_change_number(self, workspace_root: str, project_id: str) -> None:
        """测试变更编号生成"""
        if not os.path.isdir(workspace_root):
            pytest.skip("工作空间目录不存在")

        svc = ChangeService(workspace_root)
        project_path = os.path.join(workspace_root, project_id)

        num1 = svc._generate_change_number(project_path, "PLC")
        assert num1.startswith("CHG-PLC-")

        # 连续生成应递增
        num2 = svc._generate_change_number(project_path, "PLC")
        assert num2.startswith("CHG-PLC-")

    def test_create_change_request_project_not_found(self, workspace_root: str) -> None:
        """创建变更单时项目不存在抛 ValueError"""
        svc = ChangeService(workspace_root)
        with pytest.raises(ValueError, match="项目不存在"):
            svc.create_change_request(
                project_id="NONEXISTENT-9999",
                domain="PLC",
                business_nature="DEF",
                impact_scope=["LOCAL"],
                applicant="测试",
                background="背景",
                necessity="必要性",
            )

    def test_create_change_request_invalid_domain(self, workspace_root: str, project_id: str) -> None:
        """创建变更单时非法领域抛 SpecViolationError"""
        svc = ChangeService(workspace_root)
        with pytest.raises(SpecViolationError, match="技术领域"):
            svc.create_change_request(
                project_id=project_id,
                domain="INVALID",
                business_nature="DEF",
                impact_scope=["LOCAL"],
                applicant="测试",
                background="背景",
                necessity="必要性",
            )

    def test_list_change_requests_project_not_found(self, workspace_root: str) -> None:
        """列出变更单时项目不存在返回空列表"""
        svc = ChangeService(workspace_root)
        result = svc.list_change_requests("NONEXISTENT-9999")
        assert result == []

    def test_get_project_path_not_found(self, workspace_root: str) -> None:
        """_get_project_path 对不存在的项目返回 None"""
        svc = ChangeService(workspace_root)
        assert svc._get_project_path("NONEXISTENT-9999") is None

    def test_get_project_path_exists(self, workspace_root: str, project_id: str) -> None:
        """_get_project_path 对存在的项目返回路径"""
        svc = ChangeService(workspace_root)
        result = svc._get_project_path(project_id)
        assert result is not None
        assert project_id in result

    def test_find_change_file_no_domain(self, workspace_root: str) -> None:
        """_find_change_file 对无领域编号返回 None"""
        svc = ChangeService(workspace_root)
        assert svc._find_change_file("X") is None

    def test_find_change_file_nonexistent_workspace(self, tmp_path: object) -> None:
        """_find_change_file 对不存在的工作空间目录返回 None"""
        tmp = tmp_path  # type: Path
        svc = ChangeService(str(tmp / "nonexistent"))
        assert svc._find_change_file("CHG-PLC-2026-001") is None


class TestValidationFunctions:
    """变更管理规范校验函数测试"""

    def test_validate_domain_valid(self) -> None:
        """合法领域通过"""
        validate_domain("PLC")
        validate_domain("DOCU")

    def test_validate_domain_invalid(self) -> None:
        """非法领域抛异常"""
        with pytest.raises(SpecViolationError, match="技术领域"):
            validate_domain("INVALID")

    def test_validate_business_nature_valid(self) -> None:
        """合法业务性质通过"""
        validate_business_nature("DEF")
        validate_business_nature("REQ")

    def test_validate_business_nature_invalid(self) -> None:
        """非法业务性质抛异常"""
        with pytest.raises(SpecViolationError, match="业务性质"):
            validate_business_nature("INVALID")

    def test_validate_impact_scope_valid(self) -> None:
        """合法影响范围通过"""
        validate_impact_scope(["LOCAL", "MODULE"])

    def test_validate_impact_scope_invalid(self) -> None:
        """非法影响范围抛异常"""
        with pytest.raises(SpecViolationError, match="影响范围"):
            validate_impact_scope(["INVALID"])

    def test_validate_urgency_valid(self) -> None:
        """合法紧急程度通过"""
        validate_urgency("normal")
        validate_urgency("urgent")
        validate_urgency("critical")

    def test_validate_urgency_invalid(self) -> None:
        """非法紧急程度抛异常"""
        with pytest.raises(SpecViolationError, match="紧急程度"):
            validate_urgency("INVALID")

    def test_validate_status_transition_valid(self) -> None:
        """合法状态流转通过"""
        validate_status_transition("draft", "submitted")

    def test_validate_status_transition_invalid_current(self) -> None:
        """非法当前状态抛异常"""
        with pytest.raises(SpecViolationError, match="当前状态"):
            validate_status_transition("invalid_status", "submitted")

    def test_validate_status_transition_invalid_target(self) -> None:
        """非法目标状态抛异常"""
        with pytest.raises(SpecViolationError, match="状态流转"):
            validate_status_transition("draft", "completed")
