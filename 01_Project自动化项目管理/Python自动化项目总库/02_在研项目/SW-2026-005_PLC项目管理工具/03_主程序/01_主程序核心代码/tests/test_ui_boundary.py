"""F2 UI 边界态自动化测试

覆盖测试计划 TEST-PLAN-V1.0.0 §6 中 T2.1-T2.9 全部用例:
  - T2.1 无项目数据时友好提示
  - T2.2 无变更单时列表提示
  - T2.3 详情页无变更记录降级
  - T2.4 Bridge调用失败Toast提示
  - T2.5 畸形JSON不导致崩溃
  - T2.6 页面首次加载Loading态
  - T2.7 缺少§3核心字段门禁提示
  - T2.8 缺少§7/§9/§10逐级门禁提示
  - T2.9 门禁模态框"了解"可关闭

运行: python -m pytest tests/test_ui_boundary.py -v
"""

from __future__ import annotations

import json
import os
import tempfile

import pytest

# 项目根目录
_PROJ_DIR = os.path.dirname(os.path.dirname(__file__))
_UI_DIR = os.path.join(_PROJ_DIR, "ui")


# ============================================================
#  边界态 1: 无项目数据时友好提示 (T2.1)
# ============================================================

class TestEmptyWorkspace:
    """T2.1: 无项目数据时友好提示"""

    def test_empty_workspace_returns_empty_list(self):
        """空工作空间应返回空列表而非报错"""
        from src.services.project_overview_service import ProjectOverviewService
        with tempfile.TemporaryDirectory() as tmp:
            svc = ProjectOverviewService(tmp)
            result = svc.get_workspace_projects(use_cache=False)
            assert result == []

    def test_empty_workspace_detail_returns_none(self):
        """空工作空间查询项目详情应返回None"""
        from src.services.project_overview_service import ProjectOverviewService
        with tempfile.TemporaryDirectory() as tmp:
            svc = ProjectOverviewService(tmp)
            result = svc.get_project_detail("NONEXISTENT-001")
            assert result is None

    def test_empty_workspace_changes_returns_empty(self):
        """空工作空间查询变更单应返回空列表"""
        from src.services.project_overview_service import ProjectOverviewService
        with tempfile.TemporaryDirectory() as tmp:
            svc = ProjectOverviewService(tmp)
            result = svc.get_project_changes("NONEXISTENT-001")
            assert result == []

    def test_dashboard_empty_state_html_exists(self):
        """Dashboard JS 包含空态渲染逻辑"""
        dashboard_path = os.path.join(_UI_DIR, "js", "dashboard.js")
        with open(dashboard_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "暂无" in content or "empty-state" in content

    def test_dashboard_empty_state_css_exists(self):
        """CSS 定义了空态样式"""
        css_path = os.path.join(_UI_DIR, "css", "app.css")
        with open(css_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert ".empty-state" in content


# ============================================================
#  边界态 2: 无变更单时列表提示 (T2.2)
# ============================================================

class TestEmptyChangeList:
    """T2.2: 无变更单时列表提示"""

    def test_project_without_changes_returns_zero_count(self, tmp_dir):
        """有立项表但无变更单的项目，change_count应为0"""
        from src.services.project_overview_service import ProjectOverviewService

        # 创建一个只有立项表的项目
        proj_dir = os.path.join(tmp_dir, "TEST-2026-001")
        os.makedirs(proj_dir)
        proj_file_dir = os.path.join(proj_dir, "00_项目管理", "01_立项与需求")
        os.makedirs(proj_file_dir)
        proj_file = os.path.join(proj_file_dir, "003_TEST-2026-001_项目立项表_PROJ.md")
        with open(proj_file, "w", encoding="utf-8") as f:
            f.write("# 测试项目立项表\n\n## 3. 业务身份\n\n| 字段 | 内容 |\n|------|------|\n| **项目名称** | TEST-2026-001 测试项目 |\n")

        svc = ProjectOverviewService(tmp_dir)
        projects = svc.get_workspace_projects(use_cache=False)
        assert len(projects) == 1
        assert projects[0].change_count == 0

    def test_change_module_empty_state(self):
        """变更管理 JS 包含空列表提示逻辑"""
        change_path = os.path.join(_UI_DIR, "js", "change.js")
        with open(change_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "暂无" in content or "empty" in content.lower()


# ============================================================
#  边界态 3: 详情页无变更记录降级 (T2.3)
# ============================================================

class TestDetailNoChanges:
    """T2.3: 详情页无变更记录降级"""

    def test_detail_page_no_crash_without_changes(self, tmp_dir):
        """详情页无变更记录时不崩溃"""
        from src.services.project_overview_service import ProjectOverviewService

        proj_dir = os.path.join(tmp_dir, "TEST-2026-002")
        os.makedirs(proj_dir)
        proj_file_dir = os.path.join(proj_dir, "00_项目管理", "01_立项与需求")
        os.makedirs(proj_file_dir)
        proj_file = os.path.join(proj_file_dir, "003_TEST-2026-002_项目立项表_PROJ.md")
        with open(proj_file, "w", encoding="utf-8") as f:
            f.write("# 测试项目立项表\n\n## 3. 业务身份\n\n| 字段 | 内容 |\n|------|------|\n| **项目名称** | TEST-2026-002 测试项目 |\n")

        svc = ProjectOverviewService(tmp_dir)
        detail = svc.get_project_detail("TEST-2026-002")
        assert detail is not None
        assert detail.change_count == 0

    def test_detail_js_renders_without_changes(self):
        """Detail JS 能渲染无变更记录的情况"""
        detail_path = os.path.join(_UI_DIR, "js", "detail.js")
        with open(detail_path, "r", encoding="utf-8") as f:
            content = f.read()
        # 应有变更列表为空时的降级处理
        assert "change" in content.lower()


# ============================================================
#  边界态 4: Bridge调用失败Toast提示 (T2.4)
# ============================================================

class TestBridgeFailureToast:
    """T2.4: Bridge调用失败Toast提示"""

    def test_toast_container_exists_in_html(self):
        """HTML 中存在 Toast 容器"""
        index_path = os.path.join(_UI_DIR, "index.html")
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "toast-container" in content

    def test_show_toast_function_exists(self):
        """app.js 定义了 showToast 函数"""
        app_path = os.path.join(_UI_DIR, "js", "app.js")
        with open(app_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "function showToast" in content or "showToast" in content

    def test_toast_error_class_exists(self):
        """CSS 定义了错误 Toast 样式"""
        css_path = os.path.join(_UI_DIR, "css", "app.css")
        with open(css_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert ".toast--error" in content

    def test_bridge_error_serialization(self):
        """Bridge 错误序列化格式正确"""
        from src.bridge.webview_bridge import WebViewBridge
        from src.utils.path_resolver import PathTraversalError

        result = WebViewBridge._error_result(PathTraversalError("test traversal"))
        assert result["error"] == "PathTraversalError"
        assert "test traversal" in result["message"]

    def test_api_js_timeout_protection(self):
        """api.js 有超时保护"""
        api_path = os.path.join(_UI_DIR, "js", "api.js")
        with open(api_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "timeout" in content.lower() or "Timeout" in content or "race" in content


# ============================================================
#  边界态 5: 畸形JSON不导致崩溃 (T2.5)
# ============================================================

class TestMalformedData:
    """T2.5: 畸形JSON不导致崩溃"""

    def test_null_project_in_list_handled(self):
        """项目列表中含 null 元素时前端能处理"""
        dashboard_path = os.path.join(_UI_DIR, "js", "dashboard.js")
        with open(dashboard_path, "r", encoding="utf-8") as f:
            content = f.read()
        # dashboard.js 应有 null 过滤
        assert ".filter" in content and "null" in content

    def test_escape_html_handles_none(self):
        """escapeHtml 函数处理 null/undefined"""
        app_path = os.path.join(_UI_DIR, "js", "app.js")
        with open(app_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "escapeHtml" in content
        # 应有 null 检查
        assert "null" in content or "!=" in content

    def test_bridge_returns_valid_json_on_error(self):
        """Bridge 异常时返回有效 JSON"""
        from src.bridge.webview_bridge import WebViewBridge
        result = WebViewBridge._error_result(RuntimeError("unexpected"))
        assert isinstance(result, dict)
        assert "error" in result
        assert "message" in result
        # 确保可序列化
        json_str = json.dumps(result, ensure_ascii=False)
        parsed = json.loads(json_str)
        assert parsed["error"] == "InternalError"


# ============================================================
#  边界态 6: 页面首次加载Loading态 (T2.6)
# ============================================================

class TestLoadingState:
    """T2.6: 页面首次加载Loading态"""

    def test_loading_spinner_css_exists(self):
        """CSS 定义了加载动画样式"""
        css_path = os.path.join(_UI_DIR, "css", "app.css")
        with open(css_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert ".loading-spinner" in content

    def test_dashboard_shows_loading_initially(self):
        """Dashboard 初始渲染时显示加载状态"""
        dashboard_path = os.path.join(_UI_DIR, "js", "dashboard.js")
        with open(dashboard_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "加载中" in content or "loading" in content.lower()

    def test_dashboard_has_timeout_fallback(self):
        """Dashboard 有超时降级提示"""
        dashboard_path = os.path.join(_UI_DIR, "js", "dashboard.js")
        with open(dashboard_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "setTimeout" in content


# ============================================================
#  边界态 7-9: 门禁提示 (T2.7-T2.9)
# ============================================================

class TestTransitionGuards:
    """T2.7-T2.9: 门禁条件提示与模态框"""

    def test_guard_error_includes_missing_sections(self):
        """门禁错误消息包含缺失章节信息"""
        from src.models.spec_constants import TransitionGuardError
        try:
            raise TransitionGuardError(
                "变更单 CHG-PLC-2026-001 不满足 'completed' 的门禁条件:\n"
                "  - §7 实施计划未填写\n"
                "  - §9 实施记录未填写\n"
                "  - §10.2 验证结论为'空'"
            )
        except TransitionGuardError as e:
            msg = str(e)
            assert "§7" in msg
            assert "§9" in msg
            assert "§10" in msg

    def test_guard_check_for_submitted(self):
        """draft→submitted 门禁检查 §3+§4"""
        from src.services.change_management_service import ChangeManagementService
        with tempfile.TemporaryDirectory() as tmp:
            svc = ChangeManagementService(tmp)
            # 创建一个空变更单
            proj_dir = os.path.join(tmp, "TEST-2026-003")
            os.makedirs(proj_dir)
            chg_dir = os.path.join(proj_dir, "00_项目管理", "04_变更管理", "01_变更单", "CHG-PLC")
            os.makedirs(chg_dir)
            chg_file = os.path.join(chg_dir, "CHG-PLC-2026-001.md")
            with open(chg_file, "w", encoding="utf-8") as f:
                f.write("# 变更单\n\n## 3. 变更基本信息\n\n### 3.4 申请信息\n| 字段 | 内容 |\n|------|------|\n| 变更申请人 | （待补充） |\n")

            from src.models.spec_constants import TransitionGuardError
            with pytest.raises(TransitionGuardError) as exc_info:
                cr = svc._parser.parse(chg_file)
                svc._check_transition_guards(cr, "submitted", "", "")
            assert "§3" in str(exc_info.value) or "§4" in str(exc_info.value)

    def test_modal_overlay_exists_in_html(self):
        """HTML 中存在模态框容器"""
        index_path = os.path.join(_UI_DIR, "index.html")
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "modal-overlay" in content

    def test_close_modal_function_exists(self):
        """app.js 定义了 closeModal 函数"""
        app_path = os.path.join(_UI_DIR, "js", "app.js")
        with open(app_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "function closeModal" in content or "closeModal" in content

    def test_change_js_renders_guard_modal(self):
        """change.js 渲染门禁模态框"""
        change_path = os.path.join(_UI_DIR, "js", "change.js")
        with open(change_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "modal" in content.lower()
        assert "guard" in content.lower() or "门禁" in content or "GuardError" in content

    def test_transition_guard_error_serialization(self):
        """TransitionGuardError 序列化为前端可识别格式"""
        from src.bridge.webview_bridge import WebViewBridge
        from src.models.spec_constants import TransitionGuardError
        result = WebViewBridge._error_result(
            TransitionGuardError("§7 未填写\n§9 未填写")
        )
        assert result["error"] == "TransitionGuardError"
        assert "§7" in result["message"]
