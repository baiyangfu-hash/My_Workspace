"""Change Bridge (QML)"""
import dataclasses
from typing import Any

from PySide6.QtCore import Property, QObject, Signal, Slot

from auto_pm.application.change_facade import ChangeFacade


class ChangeBridge(QObject):
    changesChanged = Signal()

    def __init__(self, facade: ChangeFacade | None = None, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._facade = facade
        self._changes_cache: list[Any] = []
        self._change_detail_cache: dict[str, Any] = {}

    @Property(bool, notify=changesChanged)
    def hasService(self) -> bool:
        return self._facade is not None

    @Slot(result=list)
    def listAllChanges(self) -> list[Any]:
        if self._changes_cache:
            return self._changes_cache
        if self._facade:
            res = self._facade.list_change_requests()
            if res.success and res.payload is not None:
                self._changes_cache = [dataclasses.asdict(c) for c in res.payload]
                self.changesChanged.emit()
                return self._changes_cache
        return []

    @Slot(str, result=list)
    def listChanges(self, project_id: str) -> list[Any]:
        if self._facade:
            res = self._facade.list_change_requests(project_id)
            if res.success and res.payload is not None:
                return [dataclasses.asdict(c) for c in res.payload]
        return []

    @Slot(str, result="QVariant")
    def getChangeRequest(self, change_number: str) -> Any:
        if change_number in self._change_detail_cache:
            return self._change_detail_cache[change_number]
        if self._facade:
            res = self._facade.get_change_detail(change_number)
            if res.success and res.payload is not None:
                detail = dataclasses.asdict(res.payload)
                self._change_detail_cache[change_number] = detail
                return detail
        return {}

    @Slot()
    def refreshChanges(self) -> None:
        self._changes_cache = []
        self._change_detail_cache.clear()
        self.changesChanged.emit()
