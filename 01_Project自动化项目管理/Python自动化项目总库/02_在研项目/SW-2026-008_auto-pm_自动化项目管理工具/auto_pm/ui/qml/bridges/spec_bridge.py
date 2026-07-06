"""Spec Bridge (QML)"""
from typing import Any

from PySide6.QtCore import Property, QObject, Signal, Slot

from auto_pm.application.spec_facade import SpecFacade


class SpecBridge(QObject):
    specCheckCompleted = Signal(int, int, int)  # error_count, warning_count, info_count

    def __init__(self, facade: SpecFacade | None = None, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._facade = facade

    @Property(bool, constant=True)
    def hasService(self) -> bool:
        return self._facade is not None

    @Slot(result="QVariant")
    def runSpecCheck(self) -> dict[str, Any]:
        if self._facade:
            res = self._facade.run_spec_check()
            if res.success and res.payload:
                payload = res.payload
                self.specCheckCompleted.emit(
                    payload.get("error_count", 0),
                    payload.get("warning_count", 0),
                    payload.get("info_count", 0),
                )
                return payload
            return {"error_count": -1, "message": res.message}
        return {"error_count": -1, "message": "未初始化"}

    @Slot(result="QVariant")
    def getSpecOverview(self) -> dict[str, Any]:
        if self._facade:
            res = self._facade.get_spec_center_overview()
            if res.success and res.payload:
                return res.payload
        return {}

    @Slot(str, result=list)
    def listSpecEntries(self, filter_domain: str = "") -> list[Any]:
        if self._facade:
            domain = filter_domain if filter_domain else None
            res = self._facade.list_spec_center_entries(domain)
            if res.success and res.payload:
                return res.payload
        return []
