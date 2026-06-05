"""WebViewBridge — JS → Python IPC 桥接层

按 API V1.0.0 §5 定义，将 Service 层方法暴露为 JS 可调用的 API。
所有方法通过 PyWebView 的 expose 机制自动注册到 window.pywebview.api。
"""

from __future__ import annotations

import dataclasses
import logging
from typing import Any

import webview

from src.models.spec_constants import (
    SpecViolationError,
    TransitionGuardError,
    DOMAINS,
    BUSINESS_NATURES,
    IMPACT_SCOPES,
    URGENCY_LEVELS,
    STATUS_LABELS,
    PHASE_LABELS,
)
from src.services.change_management_service import ChangeManagementService
from src.services.project_overview_service import ProjectOverviewService

log = logging.getLogger(__name__)


class WebViewBridge:
    """JS → Python IPC 桥接层

    使用方式:
        bridge = WebViewBridge(workspace_root)
        window = webview.create_window("PLC项目管理", "ui/bridge_test.html", js_api=bridge)
        webview.start()
    """

    def __init__(self, workspace_root: str) -> None:
        self._overview_svc = ProjectOverviewService(workspace_root)
        self._change_svc = ChangeManagementService(workspace_root)
        self._window: webview.Window | None = None
        self._workspace_root = workspace_root
        log.info("WebViewBridge 初始化完成, workspace_root=%s", workspace_root or "(待选择)")

    def set_window(self, window: webview.Window) -> None:
        """设置 PyWebView 窗口引用（用于回调）"""
        self._window = window

    # ── 工作空间管理 API ──────────────────────────────────────

    def get_workspace_info(self) -> dict:
        """获取当前工作空间信息

        Returns:
            dict: {"workspace_root": str, "is_set": bool}
        """
        return {
            "workspace_root": self._workspace_root,
            "is_set": bool(self._workspace_root),
        }

    def set_workspace(self, path: str) -> dict:
        """设置工作空间根目录并刷新服务

        Args:
            path: 工作空间根目录绝对路径

        Returns:
            dict: {"status": "ok", "workspace_root": str}
        """
        import os
        if not os.path.isdir(path):
            return {"error": "ValueError", "message": f"目录不存在: {path}"}
        self._workspace_root = os.path.abspath(path)
        self._overview_svc = ProjectOverviewService(self._workspace_root)
        self._change_svc = ChangeManagementService(self._workspace_root)
        self._overview_svc.refresh()  # 清空旧缓存
        log.info("工作空间已切换: %s", self._workspace_root)
        return {"status": "ok", "workspace_root": self._workspace_root}

    def select_workspace(self) -> dict:
        """弹出文件夹选择对话框，让用户选择工作空间

        Returns:
            dict: {"status": "ok", "workspace_root": str} 或 {"status": "cancelled"}
        """
        if self._window is None:
            return {"error": "InternalError", "message": "窗口未初始化"}
        result = self._window.create_file_dialog(
            webview.FOLDER_DIALOG,
            directory="",
        )
        if result and len(result) > 0:
            return self.set_workspace(result[0])
        return {"status": "cancelled"}

    # ── 项目总览 API ──────────────────────────────────────────

    def get_workspace_projects(self) -> list[dict]:
        """获取工作空间下所有项目概览

        Returns:
            list[dict]: 项目信息列表，每个元素为 ProjectInfo 的 dict 序列化
        """
        log.info("API: get_workspace_projects")
        try:
            projects = self._overview_svc.get_workspace_projects()
            return [dataclasses.asdict(p) for p in projects]
        except Exception as e:
            log.exception("get_workspace_projects 失败")
            return self._error_result(e)

    def get_project_detail(self, project_id: str) -> dict | None:
        """获取项目详情

        Args:
            project_id: 项目编号

        Returns:
            dict | None: 项目完整信息，不存在时返回 None
        """
        log.info("API: get_project_detail(%s)", project_id)
        try:
            info = self._overview_svc.get_project_detail(project_id)
            if info is None:
                return None
            return dataclasses.asdict(info)
        except Exception as e:
            log.exception("get_project_detail 失败")
            return self._error_result(e)

    def get_project_changes(self, project_id: str) -> list[dict]:
        """获取项目变更单摘要列表

        Args:
            project_id: 项目编号

        Returns:
            list[dict]: 变更单摘要列表
        """
        log.info("API: get_project_changes(%s)", project_id)
        try:
            changes = self._overview_svc.get_project_changes(project_id)
            return [dataclasses.asdict(c) for c in changes]
        except Exception as e:
            log.exception("get_project_changes 失败")
            return [self._error_result(e)]

    def refresh_cache(self, project_id: str | None = None) -> dict:
        """刷新缓存

        Args:
            project_id: 指定项目编号，None 则刷新全部

        Returns:
            dict: {"status": "ok"}
        """
        log.info("API: refresh_cache(%s)", project_id)
        try:
            self._overview_svc.refresh(project_id)
            return {"status": "ok"}
        except Exception as e:
            log.exception("refresh_cache 失败")
            return self._error_result(e)

    def get_spec_constants(self) -> dict:
        """返回规范常量（供前端渲染使用，消除前后端枚举重复维护）

        Returns:
            dict: {
                "domains": {code: label},
                "business_natures": {code: label},
                "impact_scopes": {code: label},
                "urgency_levels": {code: label},
                "status_labels": {code: label},
                "phase_labels": {code: label},
            }
        """
        return {
            "domains": DOMAINS,
            "business_natures": BUSINESS_NATURES,
            "impact_scopes": IMPACT_SCOPES,
            "urgency_levels": URGENCY_LEVELS,
            "status_labels": STATUS_LABELS,
            "phase_labels": PHASE_LABELS,
        }

    # ── 变更管理 API ──────────────────────────────────────────

    def create_change_request(self, project_id: str, fields: dict) -> dict:
        """创建变更单

        Args:
            project_id: 项目编号
            fields: 变更单字段 dict，包含:
                - domain (str): 技术领域
                - business_nature (str): 业务性质
                - impact_scope (list[str]): 影响范围
                - applicant (str): 申请人
                - background (str): 变更背景
                - necessity (str): 变更必要性
                - references (str, 可选): 参考依据
                - planned_date (str | None, 可选): 预计实施日期
                - urgency (str, 可选): 紧急程度

        Returns:
            dict: 创建成功的 ChangeRequest 序列化
        """
        log.info("API: create_change_request(%s, ...)", project_id)
        try:
            cr = self._change_svc.create_change_request(
                project_id=project_id,
                domain=fields.get("domain", ""),
                business_nature=fields.get("business_nature", ""),
                impact_scope=fields.get("impact_scope", []),
                applicant=fields.get("applicant", ""),
                background=fields.get("background", ""),
                necessity=fields.get("necessity", ""),
                references=fields.get("references", ""),
                planned_date=fields.get("planned_date"),
                urgency=fields.get("urgency", "normal"),
            )
            return dataclasses.asdict(cr)
        except Exception as e:
            log.exception("create_change_request 失败")
            return self._error_result(e)

    def list_change_requests(self, project_id: str, filters: dict | None = None) -> list[dict]:
        """列出变更单

        Args:
            project_id: 项目编号
            filters: 筛选条件 dict，包含:
                - status (str | None): 按状态筛选
                - domain (str | None): 按领域筛选

        Returns:
            list[dict]: 变更单摘要列表
        """
        log.info("API: list_change_requests(%s, %s)", project_id, filters)
        try:
            filters = filters or {}
            changes = self._change_svc.list_change_requests(
                project_id=project_id,
                status=filters.get("status"),
                domain=filters.get("domain"),
            )
            return [dataclasses.asdict(c) for c in changes]
        except Exception as e:
            log.exception("list_change_requests 失败")
            return [self._error_result(e)]

    def get_change_request(self, change_number: str) -> dict | None:
        """获取变更单详情

        Args:
            change_number: 变更编号

        Returns:
            dict | None: 变更单完整内容，不存在时返回 None
        """
        log.info("API: get_change_request(%s)", change_number)
        try:
            cr = self._change_svc.get_change_request(change_number)
            if cr is None:
                return None
            return dataclasses.asdict(cr)
        except Exception as e:
            log.exception("get_change_request 失败")
            return self._error_result(e)

    def transition_status(
        self,
        change_number: str,
        new_status: str,
        kwargs: dict | None = None,
    ) -> dict:
        """状态流转

        Args:
            change_number: 变更编号
            new_status: 目标状态
            kwargs: 可选参数 dict，包含:
                - approver (str): 审批人
                - comment (str): 审批意见

        Returns:
            dict: 流转后的 ChangeRequest 序列化
        """
        log.info("API: transition_status(%s, %s)", change_number, new_status)
        try:
            kwargs = kwargs or {}
            cr = self._change_svc.transition_status(
                change_number=change_number,
                new_status=new_status,
                approver=kwargs.get("approver", ""),
                comment=kwargs.get("comment", ""),
                verification_conclusion=kwargs.get("verification_conclusion", "全部通过"),
            )
            if cr is None:
                return {"error": "NotFoundError", "message": f"变更单 {change_number} 不存在"}
            return dataclasses.asdict(cr)
        except Exception as e:
            log.exception("transition_status 失败")
            return self._error_result(e)

    # ── 错误序列化 ────────────────────────────────────────────

    @staticmethod
    def _error_result(exc: Exception) -> dict:
        """将 Python 异常序列化为 JSON 格式（API V1.0.0 §5.4）

        格式: {"error": "<异常类型名>", "message": "<异常消息>"}
        """
        if isinstance(exc, SpecViolationError):
            return {"error": "SpecViolationError", "message": str(exc)}
        elif isinstance(exc, TransitionGuardError):
            return {"error": "TransitionGuardError", "message": str(exc)}
        elif isinstance(exc, ValueError):
            return {"error": "ValueError", "message": str(exc)}
        else:
            log.error("未预期的异常: %s: %s", type(exc).__name__, exc)
            return {"error": "InternalError", "message": "内部错误，请查看日志"}
