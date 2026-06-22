"""WebViewBridge — JS → Python IPC 桥接层

按 API V1.0.0 §5 定义，将 Service 层方法暴露为 JS 可调用的 API。
所有方法通过 PyWebView 的 expose 机制自动注册到 window.pywebview.api。
"""

from __future__ import annotations

import dataclasses
import logging
import os
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
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
from src.services.plc_project_service import PlcProjectService
from src.utils.path_resolver import (
    PathTraversalError,
    validate_change_number,
    validate_path_within_workspace,
    validate_project_id,
)

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
        self._plc_svc = PlcProjectService(workspace_root)
        self._window: webview.Window | None = None
        self._workspace_root = workspace_root
        self._executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="bridge_bg")
        log.info("WebViewBridge 初始化完成, workspace_root=%s", workspace_root or "(待选择)")

    def _run_in_thread(self, fn, *args, timeout=30):
        """在后台线程执行耗时操作，带超时保护"""
        try:
            future = self._executor.submit(fn, *args)
            return future.result(timeout=timeout)
        except FuturesTimeoutError:
            log.error("后台线程操作超时(%ds): %s", timeout, fn.__name__)
            return {"error": "TimeoutError", "message": f"操作超时({timeout}s)"}
        except Exception as e:
            log.exception("后台线程操作失败: %s", fn.__name__)
            return self._error_result(e)

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
        abs_path = os.path.abspath(path)
        # 安全校验：不允许将工作空间设为系统关键目录
        try:
            validate_path_within_workspace(abs_path, abs_path)  # 自身校验通过
        except PathTraversalError:
            return {"error": "ValueError", "message": f"路径不合法: {path}"}
        self._workspace_root = abs_path
        self._overview_svc = ProjectOverviewService(self._workspace_root)
        self._change_svc = ChangeManagementService(self._workspace_root)
        self._overview_svc.refresh()  # 清空旧缓存
        # 切换工作空间后立即预热新缓存
        self._overview_svc.get_workspace_projects(use_cache=False)
        log.info("工作空间已切换: %s", self._workspace_root)
        # 推送 Dashboard 数据到前端（解决无环境变量启动时选择工作空间后页面空白）
        self.push_dashboard_data()
        return {"status": "ok", "workspace_root": self._workspace_root}

    def select_workspace(self) -> dict:
        """弹出文件夹选择对话框，让用户选择工作空间

        Returns:
            dict: {"status": "ok", "workspace_root": str} 或 {"status": "cancelled"}
        """
        if self._window is None:
            return {"error": "InternalError", "message": "窗口未初始化"}
        result = self._window.create_file_dialog(
            webview.FileDialog.FOLDER,
            directory="",
        )
        if result and len(result) > 0:
            return self.set_workspace(result[0])
        return {"status": "cancelled"}

    def preload_cache(self) -> None:
        """预热项目列表缓存（在 webview.start() 前调用）"""
        log.info("开始预热项目列表缓存...")
        self._overview_svc.get_workspace_projects(use_cache=False)  # 强制扫描+写入缓存
        log.info("项目列表缓存预热完成")

    # ── Python → JS 数据推送 API ──────────────────────────────

    def push_dashboard_data(self) -> None:
        """通过 evaluate_js 将项目列表数据主动推送到前端 Dashboard

        解决 PyWebView Windows WebView2 expose 同步 IPC 死锁问题：
        前端不再 await api.get_workspace_projects()，
        改由 Python 端通过 window.evaluate_js() 将数据注入到前端。
        """
        if self._window is None:
            log.warning("push_dashboard_data: 窗口未初始化，跳过推送")
            return

        try:
            projects = self._overview_svc.get_workspace_projects(use_cache=True)
            data = [dataclasses.asdict(p) for p in projects] if projects else []
            import json
            json_str = json.dumps(data, ensure_ascii=False)
            # 优先调用回调（如果 DashboardModule 已注册），同时写入全局变量兜底
            js_code = (
                f"window.__dashboardData = {json_str}; "
                f"if (typeof window.__onDashboardData === 'function') {{"
                f"  window.__onDashboardData(window.__dashboardData);"
                f"}}"
            )
            self._window.evaluate_js(js_code)
            log.info("push_dashboard_data: 已推送 %d 个项目到前端", len(data))
        except Exception as e:
            log.exception("push_dashboard_data 推送失败")

    # ── 项目总览 API ──────────────────────────────────────────

    def get_workspace_projects(self) -> list[dict]:
        """获取工作空间下所有项目概览（读缓存，瞬时返回）

        主要数据流为 push 模式（push_to_dashboard → evaluate_js），
        本方法作为降级路径保留，供前端主动拉取或其他场景使用。
        """
        log.debug("API: get_workspace_projects (读缓存)")
        try:
            # use_cache=True → 直接读缓存，瞬时返回
            projects = self._overview_svc.get_workspace_projects(use_cache=True)
            return [dataclasses.asdict(p) for p in projects] if projects else []
        except Exception as e:
            log.exception("get_workspace_projects 异常")
            return [self._error_result(e)]

    def get_project_detail(self, project_id: str) -> dict | None:
        """获取项目详情

        Args:
            project_id: 项目编号

        Returns:
            dict | None: 项目完整信息，不存在时返回 None
        """
        log.info("API: get_project_detail(%s)", project_id)
        try:
            validate_project_id(project_id)
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
            validate_project_id(project_id)
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
            if project_id is not None:
                validate_project_id(project_id)
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
            validate_project_id(project_id)
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
            validate_project_id(project_id)
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
            validate_change_number(change_number)
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
            validate_change_number(change_number)
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

    # ── V9 标准化管理 API ─────────────────────────────────────

    def plc_check_all(self) -> dict:
        """批量检查工作空间所有项目的结构合规性

        Returns:
            dict: {
                "total": int,
                "pass_count": int,
                "warn_count": int,
                "fail_count": int,
                "compliance_rate": float,
                "projects": [CheckResult dict, ...]
            }
        """
        try:
            results = self._plc_svc.check_workspace()
            projects = [self._check_result_to_dict(r) for r in results]
            total = len(results)
            pass_n = sum(1 for r in results if r.all_pass)
            warn_n = sum(1 for r in results if r.warn_count > 0 and r.fail_count == 0)
            fail_n = sum(1 for r in results if r.fail_count > 0)
            rate = (pass_n / total * 100) if total > 0 else 0
            return {
                "total": total,
                "pass_count": pass_n,
                "warn_count": warn_n,
                "fail_count": fail_n,
                "compliance_rate": round(rate, 1),
                "projects": projects,
            }
        except Exception as e:
            log.exception("plc_check_all 失败")
            return self._error_result(e)

    def plc_check_project(self, project_path: str) -> dict:
        """检查单个项目的结构合规性

        Args:
            project_path: 项目路径（绝对路径或相对于工作空间）

        Returns:
            dict: CheckResult 字典
        """
        try:
            abs_path = self._resolve_project_path(project_path)
            result = self._plc_svc.check_project(abs_path)
            return self._check_result_to_dict(result)
        except Exception as e:
            log.exception("plc_check_project 失败")
            return self._error_result(e)

    def plc_init_project(
        self,
        project_id: str,
        project_name: str,
        project_type: str = "standard",
        description: str = "",
    ) -> dict:
        """初始化新项目

        Args:
            project_id: 项目编号，如 DJ-2026-010
            project_name: 项目名称
            project_type: 项目类型 standard / syslib_fb
            description: 项目描述

        Returns:
            dict: {"project_id", "project_path", "created_files", "dry_run"}
        """
        try:
            result = self._plc_svc.init_project(
                project_id=project_id,
                project_name=project_name,
                description=description,
                dry_run=False,
            )
            return result
        except Exception as e:
            log.exception("plc_init_project 失败")
            return self._error_result(e)

    def plc_repair_project(
        self, project_path: str, rename_confirm: bool = False
    ) -> dict:
        """修复项目结构问题

        Args:
            project_path: 项目路径
            rename_confirm: 是否确认文件重命名（破坏性操作）

        Returns:
            dict: RepairResult 字典
        """
        try:
            abs_path = self._resolve_project_path(project_path)
            result = self._plc_svc.repair_project(
                abs_path, dry_run=False, rename_confirm=rename_confirm
            )
            return self._repair_result_to_dict(result)
        except Exception as e:
            log.exception("plc_repair_project 失败")
            return self._error_result(e)

    def plc_standardize_project(
        self, project_path: str, apply: bool = False
    ) -> dict:
        """标准化项目文档命名

        Args:
            project_path: 项目路径
            apply: False=仅检测预览, True=执行重命名

        Returns:
            dict: StandardizeResult 字典
        """
        try:
            abs_path = self._resolve_project_path(project_path)
            result = self._plc_svc.standardize_docs(abs_path, apply=apply)
            return self._standardize_result_to_dict(result)
        except Exception as e:
            log.exception("plc_standardize_project 失败")
            return self._error_result(e)

    # ── V9 辅助方法 ───────────────────────────────────────────

    def _resolve_project_path(self, project_path: str) -> str:
        """解析项目路径为绝对路径"""
        if os.path.isabs(project_path):
            return project_path
        return os.path.join(self._workspace_root, project_path)

    @staticmethod
    def _check_result_to_dict(result) -> dict:
        """将 CheckResult 转换为 dict"""
        return {
            "project_path": result.project_path,
            "project_name": os.path.basename(result.project_path),
            "project_type": result.project_type,
            "pass_count": result.pass_count,
            "warn_count": result.warn_count,
            "fail_count": result.fail_count,
            "all_pass": result.all_pass,
            "items": [
                {"item": i.item, "status": i.status, "message": i.message}
                for i in result.items
            ],
        }

    @staticmethod
    def _repair_result_to_dict(result) -> dict:
        """将 RepairResult 转换为 dict"""
        return {
            "project_path": result.project_path,
            "project_name": os.path.basename(result.project_path),
            "fixed_count": result.fixed_count,
            "skipped_count": result.skipped_count,
            "failed_count": result.failed_count,
            "actions": [
                {
                    "item": a.item,
                    "action": a.action,
                    "destructive": a.destructive,
                    "status": a.status,
                    "detail": a.detail,
                }
                for a in result.actions
            ],
            "before_check": (
                WebViewBridge._check_result_to_dict(result.before_check)
                if result.before_check else None
            ),
            "after_check": (
                WebViewBridge._check_result_to_dict(result.after_check)
                if result.after_check else None
            ),
        }

    @staticmethod
    def _standardize_result_to_dict(result) -> dict:
        """将 StandardizeResult 转换为 dict"""
        return {
            "project_path": result.project_path,
            "project_name": os.path.basename(result.project_path),
            "applied_count": result.applied_count,
            "skipped_count": result.skipped_count,
            "plans": [
                {
                    "old_path": p.old_path,
                    "new_path": p.new_path,
                    "old_name": os.path.basename(p.old_path),
                    "new_name": os.path.basename(p.new_path),
                    "doc_type": p.doc_type,
                    "applied": p.applied,
                    "backup_path": p.backup_path,
                }
                for p in result.plans
            ],
            "reference_updates": result.reference_updates,
        }

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
        elif isinstance(exc, PathTraversalError):
            return {"error": "PathTraversalError", "message": str(exc)}
        elif isinstance(exc, ValueError):
            return {"error": "ValueError", "message": str(exc)}
        else:
            log.error("未预期的异常: %s: %s", type(exc).__name__, exc)
            return {"error": "InternalError", "message": "内部错误，请查看日志"}
