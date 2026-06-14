"""WebViewBridge 单元测试

不依赖 PyWebView 窗口，直接测试 Bridge 方法的：
1. 参数映射（JS dict → Python 参数）
2. 返回值序列化（dataclass → dict）
3. 错误序列化（Exception → JSON error dict）
"""

from __future__ import annotations

import dataclasses
import os
import sys
import unittest

# 确保项目根目录在 sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.bridge.webview_bridge import WebViewBridge
from src.models.change_request import ChangeRequest, ChangeSummary
from src.models.project_info import ProjectInfo
from src.models.spec_constants import SpecViolationError, TransitionGuardError

WORKSPACE_ROOT = r"C:\Users\fubai\Desktop\My_Workspace\0100_PLC自动化"


class TestWebViewBridgeProjects(unittest.TestCase):
    """项目总览 API 测试"""

    @classmethod
    def setUpClass(cls):
        cls.bridge = WebViewBridge(WORKSPACE_ROOT)

    def test_get_workspace_projects_returns_list(self):
        result = self.bridge.get_workspace_projects()
        self.assertIsInstance(result, list)
        if result:
            self.assertIsInstance(result[0], dict)
            self.assertIn("project_id", result[0])

    def test_get_project_detail_existing(self):
        result = self.bridge.get_project_detail("DJ-2026-005")
        self.assertIsInstance(result, dict)
        self.assertEqual(result["project_id"], "DJ-2026-005")

    def test_get_project_detail_not_found(self):
        result = self.bridge.get_project_detail("DJ-9999-999")
        self.assertIsNone(result)

    def test_get_project_changes(self):
        result = self.bridge.get_project_changes("DJ-2026-005")
        self.assertIsInstance(result, list)

    def test_refresh_cache(self):
        result = self.bridge.refresh_cache(None)
        self.assertEqual(result, {"status": "ok"})

    def test_refresh_cache_specific_project(self):
        result = self.bridge.refresh_cache("DJ-2026-005")
        self.assertEqual(result, {"status": "ok"})


class TestWebViewBridgeChangeQuery(unittest.TestCase):
    """变更查询 API 测试"""

    @classmethod
    def setUpClass(cls):
        cls.bridge = WebViewBridge(WORKSPACE_ROOT)

    def test_list_change_requests(self):
        result = self.bridge.list_change_requests("DJ-2026-005")
        self.assertIsInstance(result, list)

    def test_list_change_requests_with_filters(self):
        result = self.bridge.list_change_requests(
            "DJ-2026-005", {"status": "completed", "domain": "DOCU"}
        )
        self.assertIsInstance(result, list)

    def test_list_change_requests_empty_filters(self):
        result = self.bridge.list_change_requests("DJ-2026-005", {})
        self.assertIsInstance(result, list)

    def test_list_change_requests_none_filters(self):
        result = self.bridge.list_change_requests("DJ-2026-005", None)
        self.assertIsInstance(result, list)

    def test_get_change_request_existing(self):
        result = self.bridge.get_change_request("CHG-DOCU-2026-001")
        self.assertIsInstance(result, dict)
        self.assertEqual(result["change_number"], "CHG-DOCU-2026-001")

    def test_get_change_request_not_found(self):
        result = self.bridge.get_change_request("CHG-XXX-9999-000")
        self.assertIsNone(result)


class TestWebViewBridgeChangeCreate(unittest.TestCase):
    """变更创建 API 测试"""

    @classmethod
    def setUpClass(cls):
        cls.bridge = WebViewBridge(WORKSPACE_ROOT)

    def test_create_change_request_bad_domain(self):
        """非法领域应返回 SpecViolationError"""
        result = self.bridge.create_change_request("DJ-2026-005", {
            "domain": "INVALID",
            "business_nature": "DEF",
            "impact_scope": ["LOCAL"],
            "applicant": "Test",
            "background": "Test",
            "necessity": "Test",
        })
        self.assertIn("error", result)
        self.assertEqual(result["error"], "SpecViolationError")
        self.assertIn("INVALID", result["message"])

    def test_create_change_request_bad_nature(self):
        """非法业务性质应返回 SpecViolationError"""
        result = self.bridge.create_change_request("DJ-2026-005", {
            "domain": "PLC",
            "business_nature": "INVALID",
            "impact_scope": ["LOCAL"],
            "applicant": "Test",
            "background": "Test",
            "necessity": "Test",
        })
        self.assertIn("error", result)
        self.assertEqual(result["error"], "SpecViolationError")

    def test_create_change_request_bad_scope(self):
        """非法影响范围应返回 SpecViolationError"""
        result = self.bridge.create_change_request("DJ-2026-005", {
            "domain": "PLC",
            "business_nature": "DEF",
            "impact_scope": ["INVALID"],
            "applicant": "Test",
            "background": "Test",
            "necessity": "Test",
        })
        self.assertIn("error", result)
        self.assertEqual(result["error"], "SpecViolationError")

    def test_create_change_request_project_not_found(self):
        """项目不存在应返回 ValueError"""
        result = self.bridge.create_change_request("DJ-9999-999", {
            "domain": "PLC",
            "business_nature": "DEF",
            "impact_scope": ["LOCAL"],
            "applicant": "Test",
            "background": "Test",
            "necessity": "Test",
        })
        self.assertIn("error", result)
        self.assertEqual(result["error"], "ValueError")


class TestWebViewBridgeTransition(unittest.TestCase):
    """状态流转 API 测试"""

    @classmethod
    def setUpClass(cls):
        cls.bridge = WebViewBridge(WORKSPACE_ROOT)

    def test_transition_illegal_flow(self):
        """非法状态流转应返回 SpecViolationError"""
        result = self.bridge.transition_status(
            "CHG-DOCU-2026-001", "draft", {}
        )
        # 001 是 completed 状态，不能转到 draft
        self.assertIn("error", result)
        self.assertEqual(result["error"], "SpecViolationError")

    def test_transition_guard_fail(self):
        """非法状态流转应返回 SpecViolationError"""
        # draft 不能直接到 completed（合法路径: draft→submitted→approved→implementing→completed）
        result = self.bridge.transition_status(
            "CHG-PLC-2026-003", "completed", {}
        )
        # 非法流转被 SpecViolationError 拦截
        self.assertIn("error", result)
        self.assertIn(result["error"], ["SpecViolationError", "TransitionGuardError"])

    def test_transition_not_found(self):
        """变更单不存在应返回 NotFoundError"""
        result = self.bridge.transition_status(
            "CHG-XXX-9999-000", "submitted", {}
        )
        self.assertIn("error", result)
        self.assertEqual(result["error"], "NotFoundError")


class TestErrorSerialization(unittest.TestCase):
    """错误序列化测试"""

    def test_spec_violation_error(self):
        result = WebViewBridge._error_result(
            SpecViolationError("技术领域 'BAD' 不合法")
        )
        self.assertEqual(result["error"], "SpecViolationError")
        self.assertIn("BAD", result["message"])

    def test_transition_guard_error(self):
        result = WebViewBridge._error_result(
            TransitionGuardError("变更单 CHG-001 不满足门禁条件:\n  - §4 未填写")
        )
        self.assertEqual(result["error"], "TransitionGuardError")
        self.assertIn("门禁", result["message"])

    def test_value_error(self):
        result = WebViewBridge._error_result(ValueError("项目不存在"))
        self.assertEqual(result["error"], "ValueError")
        self.assertIn("项目不存在", result["message"])

    def test_unexpected_error(self):
        result = WebViewBridge._error_result(RuntimeError("意外错误"))
        self.assertEqual(result["error"], "InternalError")
        self.assertEqual(result["message"], "内部错误，请查看日志")


if __name__ == "__main__":
    unittest.main()
