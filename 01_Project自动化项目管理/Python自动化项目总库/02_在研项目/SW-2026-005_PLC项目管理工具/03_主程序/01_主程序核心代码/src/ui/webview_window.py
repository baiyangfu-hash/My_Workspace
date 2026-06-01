# -*- coding: utf-8 -*-
import json
import os
import sys
import traceback
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
LIB_DIR = BASE_DIR / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

import webview


class IPCBridge:

    MOCK_PROJECTS = [
        {"project_id": "SW-2026-005", "name": "PLC项目管理工具", "path": "C:\\Workspace\\SW-2026-005", "business_line": "软件工具", "status": "进行中"},
        {"project_id": "DJ-2026-005", "name": "边框缓存机", "path": "C:\\Workspace\\DJ-2026-005", "business_line": "DJ产线", "status": "已归档"},
        {"project_id": "DJ-2026-008", "name": "自动涂胶机", "path": "C:\\Workspace\\DJ-2026-008", "business_line": "DJ产线", "status": "进行中"},
    ]

    MOCK_CHECKERS = [
        {"id": "naming", "name": "命名规范检查", "engine": "Python", "enabled": True},
        {"id": "syntax", "name": "语法结构检查", "engine": "Trae", "enabled": True},
        {"id": "comment", "name": "注释规范检查", "engine": "Trae", "enabled": True},
        {"id": "config", "name": "配置完整性检查", "engine": "Python", "enabled": True},
        {"id": "timer", "name": "定时器使用检查", "engine": "Python", "enabled": False},
        {"id": "variable", "name": "变量声明检查", "engine": "Hybrid", "enabled": True},
        {"id": "fb_interface", "name": "FB接口一致性检查", "engine": "Hybrid", "enabled": True},
    ]

    MOCK_SPEC_RESULT = {
        "total_issues": 12,
        "summary": {"error": 3, "warning": 5, "info": 4},
        "results": [
            {"file": "OB1_Main.scl", "line": 45, "severity": "error", "rule": "NAM-001", "message": "变量名'iCounter'不符合PascalCase命名规范"},
            {"file": "FB_ValveControl.scl", "line": 12, "severity": "warning", "rule": "CMT-002", "message": "方法缺少功能注释"},
            {"file": "DB1_Global.scl", "line": 8, "severity": "info", "rule": "CFG-001", "message": "建议添加版本号注释"},
        ],
    }

    MOCK_DIAGNOSTIC = {
        "health_score": 78,
        "dimensions": {
            "naming": {"score": 85, "issues": 3},
            "syntax": {"score": 92, "issues": 1},
            "comment": {"score": 60, "issues": 8},
            "config": {"score": 75, "issues": 4},
            "timer": {"score": 90, "issues": 1},
            "variable": {"score": 70, "issues": 5},
            "fb_interface": {"score": 80, "issues": 2},
        },
    }

    def __init__(self):
        self._window = None
        self._use_mock = os.environ.get("PLC_MOCK_DATA", "0") == "1"
        from src.core.config import ConfigLoader
        try:
            ConfigLoader.load()
        except Exception:
            pass
        from src.utils.logger import setup_logger
        self._logger = setup_logger(__name__)
        self._logger.info("[IPC] IPCBridge初始化完成, mock模式=%s", self._use_mock)

    def set_window(self, window):
        self._window = window
        self._logger.info("[IPC] window已绑定")

    def _emit(self, event: str, data=None):
        payload = json.dumps({"event": event, "data": data}, ensure_ascii=False)
        self._logger.info("[IPC] emit -> %s", event)
        if self._window:
            self._window.evaluate_js(f"window.__ipc_recv({payload})")

    def _safe_call(self, name: str, fn, *args, **kwargs):
        self._logger.info("[IPC] >>> %s 开始, args=%s", name, list(args)[:2])
        try:
            result = fn(*args, **kwargs)
            self._logger.info("[IPC] <<< %s 成功, result_type=%s", name, type(result).__name__)
            return result
        except Exception as e:
            self._logger.error("[IPC] !!! %s 失败: %s\n%s", name, e, traceback.format_exc())
            return {"success": False, "error": str(e)}

    def get_app_info(self):
        return self._safe_call("get_app_info", self._get_app_info)

    def _get_app_info(self):
        from src.core.constants import APP_NAME, VERSION
        return {"name": APP_NAME, "version": VERSION}

    def get_settings(self):
        return self._safe_call("get_settings", self._get_settings)

    def _get_settings(self):
        from src.core.settings import SettingsManager
        return SettingsManager.get_all()

    def update_setting(self, key: str, value):
        return self._safe_call("update_setting", self._update_setting, key, value)

    def _update_setting(self, key, value):
        from src.core.settings import SettingsManager
        SettingsManager.set(key, value)
        SettingsManager.save()
        self._emit("setting_changed", {"key": key, "value": value})
        return True

    def reset_settings(self):
        return self._safe_call("reset_settings", self._do_reset_settings)

    def _do_reset_settings(self):
        from src.core.settings import SettingsManager
        SettingsManager.reset_to_defaults()
        self._emit("settings_reset")
        return True

    def get_templates(self):
        return self._safe_call("get_templates", self._get_templates)

    def _get_templates(self):
        from src.services.template_service import TemplateService
        templates = TemplateService.get_all_templates()
        return [{"id": t.get("id", ""), "name": t.get("name", "")} for t in templates]

    def create_project(self, project_info: str):
        return self._safe_call("create_project", self._create_project, project_info)

    def _create_project(self, project_info):
        info = json.loads(project_info)
        self._logger.info("[IPC] 创建项目: name=%s", info.get("name"))
        from src.services.project_service import ProjectService
        project, error = ProjectService.create_new_project(info)
        if error:
            return {"success": False, "error": error}
        self._emit("project_created", {"path": str(project.project_root) if project else None})
        return {"success": True, "path": str(project.project_root) if project else None}

    def open_project(self, path: str):
        return self._safe_call("open_project", self._open_project, path)

    def _open_project(self, path):
        self._logger.info("[IPC] 打开项目: path=%s", path)
        from src.services.project_service import ProjectService
        project, error = ProjectService.load_project_from_path(path)
        if error:
            return {"success": False, "error": error}
        info = {
            "project_id": project.project_id,
            "name": project.name,
            "path": str(project.project_root),
            "business_line": getattr(project, "business_line", ""),
        }
        self._emit("project_opened", info)
        return {"success": True, "project": info}

    def get_recent_projects(self):
        return self._safe_call("get_recent_projects", self._do_get_recent_projects)

    def _do_get_recent_projects(self):
        if self._use_mock:
            self._logger.info("[IPC] 返回模拟最近项目列表(%d项)", len(self.MOCK_PROJECTS))
            return self.MOCK_PROJECTS
        from src.core.settings import SettingsManager
        return SettingsManager.get_recent_projects()

    def create_document(self, params: str):
        return self._safe_call("create_document", self._create_document, params)

    def _create_document(self, params):
        p = json.loads(params)
        from src.services.document_service import DocumentService
        doc_path, error = DocumentService.create_document(
            p["project_path"], p["doc_type"], p["doc_name"],
            p.get("version", "1.0"), p.get("author", ""), p.get("content", "")
        )
        if error:
            return {"success": False, "error": error}
        self._emit("document_created", {"path": doc_path})
        return {"success": True, "path": doc_path}

    def list_documents(self, project_path: str):
        return self._safe_call("list_documents", self._list_documents, project_path)

    def _list_documents(self, project_path):
        from src.services.document_service import DocumentService
        return DocumentService.list_documents(project_path)

    def run_version_check(self, project_path: str):
        return self._safe_call("run_version_check", self._run_version_check, project_path)

    def _run_version_check(self, project_path):
        if self._use_mock:
            self._logger.info("[IPC] 返回模拟版本检查结果")
            return {"is_consistent": False, "gaps": [{"file": "OB1_Main.scl", "local": "V1.2", "server": "V1.3"}], "summary": {"total": 1}}
        from src.sync.sync_engine import SyncEngine
        report = SyncEngine.run_check(project_path)
        return {
            "is_consistent": getattr(report, "is_consistent", True),
            "gaps": getattr(report, "gaps", []),
            "summary": getattr(report, "summary", {}),
        }

    def generate_chg(self, project_path: str, output_dir: str = ""):
        return self._safe_call("generate_chg", self._generate_chg, project_path, output_dir)

    def _generate_chg(self, project_path, output_dir):
        from src.sync.sync_engine import SyncEngine
        path = SyncEngine.run_generate_chg(project_path, output_dir or None)
        return {"success": bool(path), "path": path}

    def generate_ifc(self, project_path: str, output_dir: str = ""):
        return self._safe_call("generate_ifc", self._generate_ifc, project_path, output_dir)

    def _generate_ifc(self, project_path, output_dir):
        from src.sync.sync_engine import SyncEngine
        path = SyncEngine.run_generate_ifc(project_path, output_dir or None)
        return {"success": bool(path), "path": path}

    def run_spec_check(self, project_path: str, checker_ids: str = ""):
        return self._safe_call("run_spec_check", self._run_spec_check, project_path, checker_ids)

    def _run_spec_check(self, project_path, checker_ids):
        if self._use_mock:
            ids = json.loads(checker_ids) if checker_ids else []
            self._logger.info("[IPC] 返回模拟规范检查结果(checkers=%s)", ids)
            return self.MOCK_SPEC_RESULT
        from src.services.spec_checker_service import SpecCheckerService
        service = SpecCheckerService()
        result = service.check_project(project_path)
        return {
            "total_issues": getattr(result, "total_issues", 0),
            "results": getattr(result, "results", []),
            "summary": getattr(result, "summary", {}),
        }

    def get_checkers(self):
        return self._safe_call("get_checkers", self._do_get_checkers)

    def _do_get_checkers(self):
        if self._use_mock:
            self._logger.info("[IPC] 返回模拟检查器列表(%d项)", len(self.MOCK_CHECKERS))
            return self.MOCK_CHECKERS
        from src.services.spec_checker_service import SpecCheckerService
        service = SpecCheckerService()
        checkers = service.get_enabled_checkers()
        return [
            {"id": getattr(c, "id", str(i)), "name": getattr(c, "name", f"Checker {i}")}
            for i, c in enumerate(checkers)
        ]

    def run_diagnosis(self, project_path: str):
        return self._safe_call("run_diagnosis", self._run_diagnosis, project_path)

    def _run_diagnosis(self, project_path):
        if self._use_mock:
            self._logger.info("[IPC] 返回模拟诊断结果")
            return self.MOCK_DIAGNOSTIC
        from src.services.diagnostic_service import DiagnosticService
        service = DiagnosticService()
        report, metrics = service.run_full_diagnostic(project_path)
        return {"report": report, "metrics": metrics}

    def browse_directory(self, title: str = "选择目录"):
        self._logger.info("[IPC] browse_directory: %s", title)
        result = self._window.create_file_dialog(webview.FOLDER_DIALOG, directory=BASE_DIR, allow_multi=False)
        path = result[0] if result else ""
        self._logger.info("[IPC] browse_directory结果: %s", path)
        return path

    def browse_file(self, title: str = "选择文件", file_filter: str = "All files (*.*)"):
        self._logger.info("[IPC] browse_file: %s filter=%s", title, file_filter)
        result = self._window.create_file_dialog(webview.OPEN_DIALOG, directory=BASE_DIR, allow_multi=False, file_filter=file_filter)
        path = result[0] if result else ""
        self._logger.info("[IPC] browse_file结果: %s", path)
        return path

    def save_file_dialog(self, title: str = "保存文件", file_filter: str = "All files (*.*)"):
        self._logger.info("[IPC] save_file_dialog: %s", title)
        result = self._window.create_file_dialog(webview.SAVE_DIALOG, directory=BASE_DIR, save_filename=True, file_filter=file_filter)
        path = result[0] if result else ""
        self._logger.info("[IPC] save_file_dialog结果: %s", path)
        return path

    def open_in_explorer(self, path: str):
        self._logger.info("[IPC] open_in_explorer: %s", path)
        os.startfile(f'explorer.exe /select,"{path}"')
        return True

    def open_url(self, url: str):
        self._logger.info("[IPC] open_url: %s", url)
        import webbrowser
        webbrowser.open(url)
        return True

    def ipc_ping(self):
        self._logger.info("[IPC] <<< ping >>> 收到, 响应pong")
        return {"status": "ok", "message": "pong", "mock_mode": self._use_mock}

    def get_mock_data(self, data_type: str):
        self._logger.info("[IPC] get_mock_data: type=%s", data_type)
        mapping = {
            "projects": self.MOCK_PROJECTS,
            "checkers": self.MOCK_CHECKERS,
            "spec_result": self.MOCK_SPEC_RESULT,
            "diagnostic": self.MOCK_DIAGNOSTIC,
        }
        return mapping.get(data_type, {"error": f"unknown type: {data_type}"})

    def close_project(self):
        return self._safe_call("close_project", self._close_project)

    def _close_project(self):
        self._emit("project_closed")
        return {"success": True}

    def get_project_detail(self, path: str):
        return self._safe_call("get_project_detail", self._get_project_detail, path)

    def _get_project_detail(self, path):
        from src.services.project_service import ProjectService
        project, error = ProjectService.load_project_from_path(path)
        if error:
            return {"success": False, "error": error}
        info = {}
        for attr in ["project_id", "name", "code", "description", "business_line",
                      "status", "plc_brand", "hmi_brand", "manager", "path",
                      "template_id", "project_type", "workflow_stage"]:
            info[attr] = getattr(project, attr, "")
        info["created_at"] = getattr(project, "created_at", "")
        info["updated_at"] = getattr(project, "updated_at", "")
        info["document_count"] = getattr(project, "document_count", 0)
        return {"success": True, "project": info}

    def save_project_info(self, info_json: str):
        return self._safe_call("save_project_info", self._save_project_info, info_json)

    def _save_project_info(self, info_json):
        info = json.loads(info_json)
        self._logger.info("[IPC] 保存项目信息: %s", info.get("project_id", ""))
        return {"success": True}

    def list_change_requests(self, project_path: str):
        return self._safe_call("list_change_requests", self._list_change_requests, project_path)

    def _list_change_requests(self, project_path):
        from src.services.change_service import ChangeService
        changes = ChangeService.list_change_requests(project_path)
        result = []
        for c in changes:
            item = {}
            for attr in ["change_id", "category", "title", "project_path", "status",
                          "description", "created_at", "updated_at"]:
                item[attr] = getattr(c, attr, "")
            if hasattr(c, "affected_paths"):
                item["affected_paths"] = c.affected_paths
            result.append(item)
        return result

    def create_change_request(self, params: str):
        return self._safe_call("create_change_request", self._create_change_request, params)

    def _create_change_request(self, params):
        p = json.loads(params)
        from src.services.change_service import ChangeService
        cr, error = ChangeService.create_change_request(
            p["project_path"], p["category"], p["title"], p.get("description", "")
        )
        if error:
            return {"success": False, "error": error}
        return {"success": True, "change_id": cr.change_id if cr else ""}

    def update_change_status(self, params: str):
        return self._safe_call("update_change_status", self._update_change_status, params)

    def _update_change_status(self, params):
        p = json.loads(params)
        from src.services.change_service import ChangeService
        ok = ChangeService.update_status(p["project_path"], p["change_id"], p["new_status"])
        return {"success": ok}

    def approve_change_request(self, params: str):
        return self._safe_call("approve_change_request", self._approve_change_request, params)

    def _approve_change_request(self, params):
        p = json.loads(params)
        from src.services.change_service import ChangeService
        ok = ChangeService.approve_change_request(
            p["project_path"], p["change_id"], p.get("approver", "")
        )
        return {"success": ok}

    def read_document(self, file_path: str):
        return self._safe_call("read_document", self._read_document, file_path)

    def _read_document(self, file_path):
        from src.services.document_service import DocumentService
        content, error = DocumentService.read_document(file_path)
        if error:
            return {"success": False, "error": error}
        return {"success": True, "content": content}

    def save_document(self, params: str):
        return self._safe_call("save_document", self._save_document, params)

    def _save_document(self, params):
        p = json.loads(params)
        from src.services.document_service import DocumentService
        ok, error = DocumentService.save_document(p["file_path"], p["content"])
        if error:
            return {"success": False, "error": error}
        return {"success": ok}

    def get_available_fixers(self):
        return self._safe_call("get_available_fixers", self._get_available_fixers)

    def _get_available_fixers(self):
        from src.services.auto_fix_service import AutoFixService
        fixers = AutoFixService.get_available_fixers()
        return fixers

    def scan_fixes(self, params: str):
        return self._safe_call("scan_fixes", self._scan_fixes, params)

    def _scan_fixes(self, params):
        p = json.loads(params)
        from src.services.auto_fix_service import AutoFixService
        report = AutoFixService.scan_project(p["project_path"], p.get("fixer_ids"))
        return {
            "total_issues": getattr(report, "total_issues", 0),
            "files_scanned": getattr(report, "files_scanned", 0),
            "fixable_issues": getattr(report, "fixable_issues", 0),
        }

    def fix_project(self, params: str):
        return self._safe_call("fix_project", self._fix_project, params)

    def _fix_project(self, params):
        p = json.loads(params)
        from src.services.auto_fix_service import AutoFixService
        report = AutoFixService.fix_project(
            p["project_path"], p.get("fixer_ids", []), p.get("dry_run", True)
        )
        return {
            "success": True,
            "total_fixed": getattr(report, "total_fixed", 0),
            "total_rolled_back": getattr(report, "total_rolled_back", 0),
        }

    def export_excel_single(self, params: str):
        return self._safe_call("export_excel_single", self._export_excel_single, params)

    def _export_excel_single(self, params):
        p = json.loads(params)
        from src.exporters.excel_exporter import ExcelExporter
        path = ExcelExporter.export_fb_from_file(p["file_path"])
        return {"success": bool(path), "path": str(path) if path else ""}

    def export_excel_batch(self, project_path: str):
        return self._safe_call("export_excel_batch", self._export_excel_batch, project_path)

    def _export_excel_batch(self, project_path):
        from src.exporters.excel_exporter import ExcelExporter
        path = ExcelExporter.export_all_fbs(project_path)
        return {"success": bool(path), "path": str(path) if path else ""}

    def get_dashboard_stats(self):
        return self._safe_call("get_dashboard_stats", self._get_dashboard_stats)

    def _get_dashboard_stats(self):
        from src.core.settings import SettingsManager
        recent = SettingsManager.get_recent_projects()
        from src.services.template_service import TemplateService
        templates = TemplateService.get_all_templates()
        return {
            "project_count": len(recent),
            "template_count": len(templates),
            "recent_projects": recent,
        }

    def window_minimize(self):
        if self._window:
            self._window.minimize()
        return True

    def window_maximize(self):
        if self._window:
            self._window.toggle_fullscreen()
        return True

    def window_close(self):
        if self._window:
            self._window.destroy()
        return True


def create_window(html_path: str = None, title: str = "", width: int = 1280, height: int = 800):
    if html_path is None:
        html_path = str(BASE_DIR / "ui_prototype" / "index.html")
    bridge = IPCBridge()
    url = f"file:///{html_path.replace(os.sep, '/')}"
    window = webview.create_window(
        title=title,
        url=url,
        js_api=bridge,
        width=width,
        height=height,
        min_size=(960, 600),
        text_select=True,
    )
    bridge.set_window(window)
    return window
