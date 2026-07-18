"""PLC-HMI 概念映射：HMI 变量表（Workbench 域）

像 HMI 触摸屏的变量表，定义了 QML 画面能访问的所有变量和方法：
- @Slot 方法 = HMI 按钮触发的脚本（QML 调用 → 后台执行）
- Signal = HMI 变量变化事件（数据变了自动刷新画面）
- Property = HMI 只读变量（画面直接绑定显示）

--- 原始注释 ---
Workbench Bridge (QML)"""
import dataclasses
from typing import Any

from PySide6.QtCore import Property, QObject, Signal, Slot

from auto_pm.application.workbench_facade import WorkbenchFacade


class WorkbenchBridge(QObject):
    projectsChanged = Signal()
    projectSelected = Signal(str, str)

    def __init__(self, facade: WorkbenchFacade | None = None, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._facade = facade
        self._projects_cache: list[Any] = []

    def set_facade(self, facade: WorkbenchFacade | None) -> None:
        self._facade = facade
        self.refreshProjects()

    @Property(bool, notify=projectsChanged)
    def hasService(self) -> bool:
        return self._facade is not None

    @Slot(result=list)
    def listProjects(self) -> list[Any]:
        if not self._projects_cache and self._facade:
            res = self._facade.list_project_cards()
            if res.success and res.payload is not None:
                self._projects_cache = [dataclasses.asdict(p) for p in res.payload]
        self.projectsChanged.emit()
        return self._projects_cache

    @Slot(str, result="QVariant")
    def getProjectById(self, project_id: str) -> dict[str, Any]:
        if self._facade:
            res = self._facade.get_project_workspace(project_id)
            if res.success and res.payload:
                return res.payload.summary
        return {}

    @Slot()
    def refreshProjects(self) -> None:
        self._projects_cache = []
        self.projectsChanged.emit()

    @Slot(str, str)
    def selectProject(self, project_id: str, project_name: str) -> None:
        self.projectSelected.emit(project_id, project_name)

    @Slot(result="QVariant")
    def getDashboardSummary(self) -> dict[str, Any]:
        if self._facade:
            res = self._facade.get_dashboard_snapshot()
            if res.success and res.payload:
                return dataclasses.asdict(res.payload)
        return {}

    @Slot(str, result="QVariant")
    def getActiveChangeStatus(self, project_id: str) -> dict[str, Any]:
        """获取项目主线变更单的状态机视图数据（CHG-106 新增）

        供 PlatformDashboardView 状态机组件渲染。
        """
        if self._facade:
            res = self._facade.get_active_change_status(project_id)
            if res.success and res.payload is not None:
                return res.payload
        return {
            "active": False,
            "change_number": "",
            "title": "",
            "status": "",
            "apply_date": "",
            "state_machine": {
                "current_node": 0,
                "current_node_name": "需求澄清 (Draft)",
                "progress": 0,
                "nodes": [],
            },
        }

    @Slot(str, result="QVariant")
    def getProjectChangeSummary(self, project_id: str) -> dict[str, Any]:
        """获取项目级变更聚合摘要（项目工作区变更Tab驾驶舱模式）

        返回预计算的 KPI、状态机和活动时间线数据。
        """
        if self._facade:
            res = self._facade.get_project_change_summary(project_id)
            if res.success and res.payload is not None:
                return res.payload
        return {
            "kpi": {"total": 0, "implementing": 0, "pending_review": 0, "this_week": 0},
            "state_machine": {
                "current_node": 0,
                "current_node_name": "无变更",
                "progress": 0,
                "nodes": [],
            },
            "activities": [],
        }

    @Slot(str, result="QVariant")
    def getAssetSummary(self, project_id: str) -> dict[str, Any]:
        if self._facade:
            res = self._facade.get_project_workspace(project_id)
            if res.success and res.payload:
                return res.payload.asset_summary or {}
        return {}

    @Slot(result="QVariant")
    def getSettingsSummary(self) -> dict[str, Any]:
        if self._facade:
            res = self._facade.get_settings_summary()
            if res.success and res.payload is not None:
                return dataclasses.asdict(res.payload)
        return {}

    @Slot(result="QVariant")
    def clearCache(self) -> dict[str, Any]:
        if self._facade:
            res = self._facade.clear_cache()
            if res.payload is not None:
                return dataclasses.asdict(res.payload)
            return {"success": res.success, "message": res.message}
        return {"success": False, "message": "未初始化"}

    @Slot(result="QVariant")
    def rebuildIndex(self) -> dict[str, Any]:
        if self._facade:
            res = self._facade.rebuild_index()
            if res.payload is not None:
                return dataclasses.asdict(res.payload)
            return {"success": res.success, "message": res.message}
        return {"success": False, "message": "未初始化"}

    @Slot(str, result=str)
    def generateProjectCode(self, business_line: str) -> str:
        """自动生成项目编号"""
        if self._facade and hasattr(self._facade, "generate_project_code"):
            res = self._facade.generate_project_code(business_line)
            if res.success and res.payload:
                return res.payload
        return ""

    @Slot(str, str, str, str, str, str, result="QVariant")
    def createProject(self, project_id: str, project_name: str, stack: str, mode: str, business_line: str, dest_dir: str) -> dict[str, Any]:
        if self._facade and hasattr(self._facade, "create_project"):
            res = self._facade.create_project(project_id, project_name, stack, mode, business_line, dest_dir)
            if res.success:
                self.refreshProjects()
                return {"success": True, "project_id": res.payload["project_id"] if res.payload else ""}
            return {"success": False, "message": res.message}
        return {"success": False, "message": "未初始化"}

    @Slot(str, result="QVariant")
    def importProject(self, src_path: str) -> dict[str, Any]:
        if self._facade and hasattr(self._facade, "import_project"):
            res = self._facade.import_project(src_path)
            if res.success:
                self.refreshProjects()
                return {"success": True, "project_id": res.payload["project_id"] if res.payload else ""}
            return {"success": False, "message": res.message}
        return {"success": False, "message": "未初始化"}

    @Slot(str, result="QVariant")
    def detectProject(self, path: str) -> dict[str, Any]:
        if self._facade and hasattr(self._facade, "detect_project"):
            res = self._facade.detect_project(path)
            if res.success and res.payload:
                return {
                    "success": True,
                    "project_id": res.payload["project_id"],
                    "name": res.payload["name"],
                    "stack": res.payload["stack"],
                }
            return {"success": False, "message": res.message}
        return {"success": False, "message": "服务未启用"}

    @Slot(str, "QVariant", result="QVariant")
    def editProject(self, project_id: str, fields: dict[str, Any]) -> dict[str, Any]:
        """编辑项目元数据（M4 CHG-115 新增）

        Args:
            project_id: 项目编号
            fields: 待更新字段 dict（如 {"phase": "developing", "description": "..."}）
        """
        if self._facade and hasattr(self._facade, "edit_project"):
            kwargs = {k: str(v) for k, v in fields.items() if v}
            res = self._facade.edit_project(project_id, **kwargs)
            if res.success:
                self.refreshProjects()
                return {"success": True, "message": res.message}
            return {"success": False, "message": res.message}
        return {"success": False, "message": "未初始化"}

    @Slot(str, result="QVariant")
    def deleteProject(self, project_id: str) -> dict[str, Any]:
        """删除项目（M4 CHG-115 新增，破坏性操作）

        Args:
            project_id: 项目编号
        """
        if self._facade and hasattr(self._facade, "delete_project"):
            res = self._facade.delete_project(project_id)
            if res.success:
                self.refreshProjects()
                return {"success": True, "message": res.message}
            return {"success": False, "message": res.message}
        return {"success": False, "message": "未初始化"}

    @Slot(str, result="QVariant")
    def saveWorkspaceRoot(self, workspace_root: str) -> dict[str, Any]:
        """保存全局工作空间根目录设置"""
        if self._facade and hasattr(self._facade, "save_workspace_root"):
            res = self._facade.save_workspace_root(workspace_root)
            return {"success": res.success, "message": res.message}
        return {"success": False, "message": "未初始化或功能不可用"}

    @Slot(str, result="QVariant")
    def initializeProjectPm(self, project_id: str) -> dict[str, Any]:
        """为已有项目一键初始化 PM 框架与变更管理（含创世变更单）"""
        if self._facade and hasattr(self._facade, "initialize_project_pm"):
            res = self._facade.initialize_project_pm(project_id)
            if res.success:
                self.refreshProjects()
                return {"success": True, "message": res.message}
            return {"success": False, "message": res.message}
        return {"success": False, "message": "未初始化"}

    @Slot(str, result=bool)
    def isHooksInstalled(self, project_id: str) -> bool:
        """检查项目是否已安装提交门禁钩子"""
        if self._facade and hasattr(self._facade, "is_git_hooks_installed"):
            res = self._facade.is_git_hooks_installed(project_id)
            if res.success and res.payload is not None:
                return res.payload
        return False

    @Slot(str, result="QVariant")
    def installHooks(self, project_id: str) -> dict[str, Any]:
        """安装 Git Pre-commit 钩子"""
        if self._facade and hasattr(self._facade, "install_git_hooks"):
            res = self._facade.install_git_hooks(project_id)
            if res.success and res.payload is not None:
                return res.payload
            return {"success": False, "message": res.message}
        return {"success": False, "message": "未初始化或功能未启用"}

    @Slot(str, result="QVariant")
    def uninstallHooks(self, project_id: str) -> dict[str, Any]:
        """卸载 Git Pre-commit 钩子"""
        if self._facade and hasattr(self._facade, "uninstall_git_hooks"):
            res = self._facade.uninstall_git_hooks(project_id)
            if res.success and res.payload is not None:
                return res.payload
            return {"success": False, "message": res.message}
        return {"success": False, "message": "未初始化或功能未启用"}
