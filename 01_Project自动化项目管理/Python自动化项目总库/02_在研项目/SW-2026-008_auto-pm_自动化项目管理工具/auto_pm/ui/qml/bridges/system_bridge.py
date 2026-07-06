"""System Bridge (QML)"""
from typing import Any

from PySide6.QtCore import Property, QObject, Slot

from auto_pm.application.system_facade import SystemFacade


class SystemBridge(QObject):

    def __init__(self, facade: SystemFacade | None = None, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._facade = facade

    @Property(bool, constant=True)
    def hasService(self) -> bool:
        return self._facade is not None

    @Slot(result=list)
    def listTemplates(self) -> list[str]:
        if self._facade:
            res = self._facade.list_templates()
            if res.success and res.payload is not None:
                return res.payload
        return []

    @Slot(str, result=str)
    def getTemplatePath(self, template_name: str) -> str:
        if self._facade:
            res = self._facade.get_template_path(template_name)
            if res.success and res.payload is not None:
                return res.payload
        return ""

    @Slot(str, result="QVariant")
    def getTemplateDetail(self, template_name: str) -> dict[str, Any]:
        if self._facade:
            res = self._facade.get_template_detail(template_name)
            if res.success and res.payload is not None:
                return res.payload
        return {}

    @Slot(result="QVariant")
    def getPmSessionView(self) -> dict[str, Any]:
        if self._facade:
            res = self._facade.get_pm_session_view()
            if res.success and res.payload is not None:
                return res.payload
        return {}

    @Slot(result="QVariant")
    def runPmSessionCheck(self) -> dict[str, Any]:
        if self._facade:
            res = self._facade.run_pm_session_check()
            if res.success and res.payload is not None:
                return res.payload
            return {"success": False, "message": res.message}
        return {"success": False, "message": "未初始化"}
