"""Delivery Bridge (QML)"""
from typing import Any

from PySide6.QtCore import Property, QObject, Slot

from auto_pm.application.delivery_facade import DeliveryFacade


class DeliveryBridge(QObject):

    def __init__(self, facade: DeliveryFacade | None = None, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._facade = facade

    @Property(bool, constant=True)
    def hasService(self) -> bool:
        return self._facade is not None

    @Slot(result="QVariant")
    def getProjectReport(self) -> dict[str, Any]:
        if self._facade:
            res = self._facade.get_project_report()
            if res.success and res.payload is not None:
                return res.payload
        return {}

    @Slot(result="QVariant")
    def getChangeReport(self) -> dict[str, Any]:
        if self._facade:
            res = self._facade.get_change_report()
            if res.success and res.payload is not None:
                return res.payload
        return {}

    @Slot(result="QVariant")
    def getSpecReport(self) -> dict[str, Any]:
        if self._facade:
            res = self._facade.get_spec_report()
            if res.success and res.payload is not None:
                return res.payload
        return {}

    @Slot(result="QVariant")
    def getScanReport(self) -> dict[str, Any]:
        if self._facade:
            res = self._facade.get_scan_report()
            if res.success and res.payload is not None:
                return res.payload
        return {}

    @Slot(str, bool, result="QVariant")
    def refreshProjectDocs(self, project_id: str, dry_run: bool = False) -> dict[str, Any]:
        if self._facade:
            res = self._facade.refresh_project_docs(project_id, dry_run)
            if res.payload:
                return res.payload
            return {"success": res.success, "message": res.message}
        return {"success": False, "message": "未初始化"}
