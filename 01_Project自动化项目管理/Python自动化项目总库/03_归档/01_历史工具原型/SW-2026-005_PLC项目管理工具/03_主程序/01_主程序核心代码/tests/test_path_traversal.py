"""SEC-02 路径遍历漏洞修复验证

验证 path_resolver.py 中的校验函数和 webview_bridge.py 中的拦截逻辑，
确保 project_id / change_number 参数无法被用于路径遍历攻击。

运行: python -m pytest tests/test_path_traversal.py -v
"""

from __future__ import annotations

import os
import tempfile

import pytest

from src.utils.path_resolver import (
    PathTraversalError,
    validate_change_number,
    validate_path_within_workspace,
    validate_project_id,
)


# ============================================================
#  validate_project_id 测试
# ============================================================

class TestValidateProjectId:
    """project_id 校验：仅允许字母、数字、连字符、下划线"""

    @pytest.mark.parametrize("valid_id", [
        "DJ-2026-005",
        "SW-2026-001",
        "test_project",
        "ABC123",
        "a-b-c",
    ])
    def test_valid_project_ids(self, valid_id):
        """合法 project_id 应通过校验"""
        assert validate_project_id(valid_id) == valid_id

    @pytest.mark.parametrize("malicious_id,desc", [
        ("../../etc/passwd", "Unix路径遍历"),
        ("..\\..\\windows\\system32", "Windows路径遍历"),
        ("DJ-2026-005/../../etc", "混合遍历"),
        ("DJ-2026-005\x00.exe", "空字节注入"),
        ("DJ-2026-005;rm -rf /", "命令注入"),
        ("DJ-2026-005|cat /etc/passwd", "管道注入"),
        ("DJ-2026-005$(whoami)", "命令替换"),
        ("../DJ-2026-005", "前缀遍历"),
        ("DJ-2026-005/../../../", "后缀遍历"),
        ("", "空字符串"),
    ])
    def test_malicious_project_ids_blocked(self, malicious_id, desc):
        """恶意 project_id 应被拦截"""
        with pytest.raises(PathTraversalError):
            validate_project_id(malicious_id)

    def test_project_id_with_spaces_blocked(self):
        """含空格的 project_id 应被拦截"""
        with pytest.raises(PathTraversalError):
            validate_project_id("DJ 2026 005")

    def test_project_id_with_dot_blocked(self):
        """含点号的 project_id 应被拦截"""
        with pytest.raises(PathTraversalError):
            validate_project_id("DJ.2026.005")


# ============================================================
#  validate_change_number 测试
# ============================================================

class TestValidateChangeNumber:
    """change_number 校验：必须匹配 CHG-{DOMAIN}-{YYYY}-{XXX} 格式"""

    @pytest.mark.parametrize("valid_num", [
        "CHG-DOCU-2026-001",
        "CHG-PLC-2026-099",
        "CHG-ELEC-2025-001",
        "CHG-SAFE-2026-999",
    ])
    def test_valid_change_numbers(self, valid_num):
        """合法 change_number 应通过校验"""
        assert validate_change_number(valid_num) == valid_num

    @pytest.mark.parametrize("malicious_num,desc", [
        ("CHG-PLC-2026-001/../../etc/passwd", "路径遍历后缀"),
        ("CHG-../../2026-001", "DOMAIN遍历"),
        ("CHG-PLC-2026-001\x00.md", "空字节注入"),
        ("CHG-PLC-2026-001;cat /etc/passwd", "命令注入"),
        ("../../CHG-PLC-2026-001", "前缀遍历"),
        ("CHG-PLC-2026-001/../../../etc", "深层遍历"),
        ("", "空字符串"),
        ("CHG--2026-001", "空DOMAIN"),
        ("CHG-plc-2026-001", "小写DOMAIN"),
        ("CHG-PLC-26-001", "短年份"),
        ("CHG-PLC-2026-01", "短序号"),
    ])
    def test_malicious_change_numbers_blocked(self, malicious_num, desc):
        """恶意 change_number 应被拦截"""
        with pytest.raises(PathTraversalError):
            validate_change_number(malicious_num)


# ============================================================
#  validate_path_within_workspace 测试
# ============================================================

class TestValidatePathWithinWorkspace:
    """路径范围校验：路径必须在工作空间内"""

    def test_path_within_workspace_passes(self):
        """工作空间内的路径应通过"""
        with tempfile.TemporaryDirectory() as tmp:
            sub = os.path.join(tmp, "DJ-2026-005")
            os.makedirs(sub)
            result = validate_path_within_workspace(sub, tmp)
            assert result.startswith(tmp)

    def test_path_outside_workspace_blocked(self):
        """工作空间外的路径应被拦截"""
        with tempfile.TemporaryDirectory() as tmp:
            with pytest.raises(PathTraversalError):
                validate_path_within_workspace("/etc/passwd", tmp)

    def test_workspace_root_itself_passes(self):
        """工作空间根目录自身应通过"""
        with tempfile.TemporaryDirectory() as tmp:
            result = validate_path_within_workspace(tmp, tmp)
            assert result == os.path.realpath(tmp)

    def test_symlink_escape_blocked(self):
        """符号链接逃逸应被拦截"""
        with tempfile.TemporaryDirectory() as tmp:
            with tempfile.TemporaryDirectory() as outside:
                # 在工作空间内创建指向外部的符号链接
                link_path = os.path.join(tmp, "escape_link")
                try:
                    os.symlink(outside, link_path)
                except OSError:
                    pytest.skip("当前环境不支持符号链接")
                # 通过符号链接访问外部路径
                target = os.path.join(link_path, "secret.txt")
                with pytest.raises(PathTraversalError):
                    validate_path_within_workspace(target, tmp)


# ============================================================
#  Bridge 层拦截验证
# ============================================================

class TestBridgePathTraversalProtection:
    """Bridge API 层路径遍历拦截验证"""

    @pytest.fixture
    def bridge(self):
        from src.bridge.webview_bridge import WebViewBridge
        with tempfile.TemporaryDirectory() as tmp:
            b = WebViewBridge(tmp)
            yield b

    def test_get_project_detail_traversal_blocked(self, bridge):
        """get_project_detail 拦截路径遍历"""
        result = bridge.get_project_detail("../../etc/passwd")
        assert isinstance(result, dict)
        assert result.get("error") == "PathTraversalError"

    def test_get_project_changes_traversal_blocked(self, bridge):
        """get_project_changes 拦截路径遍历"""
        result = bridge.get_project_changes("..\\..\\windows\\system32")
        assert isinstance(result, list)
        # 错误被包在 list 中
        if result and isinstance(result[0], dict):
            assert result[0].get("error") == "PathTraversalError"

    def test_get_change_request_traversal_blocked(self, bridge):
        """get_change_request 拦截非法 change_number"""
        result = bridge.get_change_request("CHG-PLC-2026-001/../../etc")
        assert isinstance(result, dict)
        assert result.get("error") == "PathTraversalError"

    def test_transition_status_traversal_blocked(self, bridge):
        """transition_status 拦截非法 change_number"""
        result = bridge.transition_status("../../../etc/passwd", "submitted")
        assert isinstance(result, dict)
        assert result.get("error") == "PathTraversalError"

    def test_create_change_request_traversal_blocked(self, bridge):
        """create_change_request 拦截路径遍历 project_id"""
        result = bridge.create_change_request("../../etc", {
            "domain": "PLC", "business_nature": "DEF",
            "impact_scope": ["LOCAL"], "applicant": "test",
            "background": "test", "necessity": "test",
        })
        assert isinstance(result, dict)
        assert result.get("error") == "PathTraversalError"

    def test_list_change_requests_traversal_blocked(self, bridge):
        """list_change_requests 拦截路径遍历"""
        result = bridge.list_change_requests("..\\..\\windows")
        assert isinstance(result, list)
        if result and isinstance(result[0], dict):
            assert result[0].get("error") == "PathTraversalError"

    def test_refresh_cache_traversal_blocked(self, bridge):
        """refresh_cache 拦截路径遍历"""
        result = bridge.refresh_cache("../../etc")
        assert isinstance(result, dict)
        assert result.get("error") == "PathTraversalError"

    def test_normal_project_id_passes(self, bridge):
        """正常 project_id 不被误拦"""
        result = bridge.get_project_detail("DJ-2026-005")
        # 不应返回 PathTraversalError
        if isinstance(result, dict):
            assert result.get("error") != "PathTraversalError"

    def test_normal_change_number_passes(self, bridge):
        """正常 change_number 不被误拦"""
        result = bridge.get_change_request("CHG-DOCU-2026-001")
        # 不应返回 PathTraversalError
        if isinstance(result, dict):
            assert result.get("error") != "PathTraversalError"
