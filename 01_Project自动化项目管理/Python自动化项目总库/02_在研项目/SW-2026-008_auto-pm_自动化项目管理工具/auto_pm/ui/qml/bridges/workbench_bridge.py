"""Workbench Bridge (QML)"""
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
