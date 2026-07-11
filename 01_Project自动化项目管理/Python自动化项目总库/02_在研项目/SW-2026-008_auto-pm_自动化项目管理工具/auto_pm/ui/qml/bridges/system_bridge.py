"""System Bridge (QML)

M4 第 2 批重构：3 个 Slot 改用 dataclasses.asdict() 转换 DTO 为 dict 给 QML。
listTemplates 返回 list[str]、getTemplatePath 返回 str，保持基础类型。
新增 1 个 Slot：applyTemplate（QML 端尚未接入，TODO M5）。
M5 CHG-117 新增 1 个 Slot：archivePmSession（PM_SESSION 归档对话框接入）。
"""
from dataclasses import asdict
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
            if res.success and res.payload:
                return asdict(res.payload)
        return {}

    @Slot(result="QVariant")
    def getPmSessionView(self) -> dict[str, Any]:
        if self._facade:
            res = self._facade.get_pm_session_view()
            if res.success and res.payload:
                return asdict(res.payload)
        return {}

    @Slot(result="QVariant")
    def runPmSessionCheck(self) -> dict[str, Any]:
        if self._facade:
            res = self._facade.run_pm_session_check()
            if res.success and res.payload:
                return asdict(res.payload)
            return {"success": False, "message": res.message}
        return {"success": False, "message": "未初始化"}

    @Slot(str, str, result="QVariant")
    def applyTemplate(self, project_id: str, template_name: str) -> dict[str, Any]:
        # TODO M5: QML 端接入模板应用对话框
        if self._facade:
            res = self._facade.apply_template(project_id, template_name)
            if res.success and res.payload:
                return asdict(res.payload)
            return {"success": res.success, "message": res.message}
        return {"success": False, "message": "未初始化"}

    @Slot(str, int, bool, result="QVariant")
    def archivePmSession(self, section: str, keepRecent: int, dryRun: bool) -> dict[str, Any]:
        # M5 CHG-117: QML 端接入 PM_SESSION 归档对话框
        if self._facade:
            res = self._facade.archive_pm_session(section, keepRecent, dryRun)
            if res.success and res.payload:
                return asdict(res.payload)
            return {"success": res.success, "message": res.message}
        return {"success": False, "message": "未初始化"}
