"""PLC-HMI 概念映射：HMI 变量表（Spec 域）

像 HMI 触摸屏的变量表，定义了 QML 画面能访问的所有规范检查相关变量和方法：
- @Slot 方法 = HMI 按钮触发的脚本（规范检查/索引/Frontmatter/报告）
- Signal = HMI 变量变化事件（检查结果变了自动刷新画面）

--- 原始注释 ---
Spec Bridge (QML)

M4 第 1 批重构：3 个 Slot 改用 dataclasses.asdict() 转换 DTO 为 dict 给 QML。
"""
from dataclasses import asdict
from typing import Any

from PySide6.QtCore import Property, QObject, Signal, Slot

from auto_pm.application.spec_facade import SpecFacade


class SpecBridge(QObject):
    specCheckCompleted = Signal(int, int, int)  # error_count, warning_count, info_count

    def __init__(self, facade: SpecFacade | None = None, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._facade = facade

    def set_facade(self, facade: SpecFacade | None) -> None:
        self._facade = facade

    @Property(bool, constant=True)
    def hasService(self) -> bool:
        return self._facade is not None

    @Slot(str, result="QVariant")
    @Slot(result="QVariant")
    def runSpecCheck(self, project_id: str = "") -> dict[str, Any]:
        if self._facade:
            res = self._facade.run_spec_check(project_id)
            if res.success and res.payload:
                payload = asdict(res.payload)
                self.specCheckCompleted.emit(
                    payload.get("error_count", 0),
                    payload.get("warning_count", 0),
                    payload.get("info_count", 0),
                )
                return payload
            return {"error_count": -1, "message": res.message}
        return {"error_count": -1, "message": "未初始化"}

    @Slot(str, result="QVariant")
    def repairSpec(self, project_id: str) -> dict[str, Any]:
        if self._facade:
            res = self._facade.run_spec_repair(project_id)
            if res.success and res.payload is not None:
                return {"success": True, "message": res.message, "payload": res.payload}
            return {"success": False, "message": res.message}
        return {"success": False, "message": "未初始化"}

    @Slot(result="QVariant")
    def getSpecOverview(self) -> dict[str, Any]:
        if self._facade:
            res = self._facade.get_spec_center_overview()
            if res.success and res.payload:
                return asdict(res.payload)
        return {}

    @Slot(str, result=list)
    def listSpecEntries(self, filter_domain: str = "") -> list[Any]:
        if self._facade:
            domain = filter_domain if filter_domain else None
            res = self._facade.list_spec_center_entries(domain)
            if res.success and res.payload:
                return [asdict(e) for e in res.payload]
        return []

    @Slot(str, result="QVariant")
    def generateSpecIndex(self, domain: str = "all") -> dict[str, Any]:
        """生成规范索引（M5 CHG-119 新增）

        Args:
            domain: "all" 生成全部（pm/plc/python），或 "pm"/"plc"/"python" 指定单域

        Returns:
            索引生成结果 dict（含 domain/generated_files/errors）或
            {"success": False, "message": ...}
        """
        if self._facade:
            res = self._facade.generate_spec_index(domain)
            if res.success and res.payload is not None:
                return asdict(res.payload)
            return {"success": res.success, "message": res.message}
        return {"success": False, "message": "未初始化"}

    @Slot(str, result="QVariant")
    def generateSpecReport(self, fmt: str = "markdown") -> dict[str, Any]:
        """生成规范报告（M5 CHG-120 新增）

        Args:
            fmt: 报告格式，"markdown" 或 "json"

        Returns:
            报告生成结果 dict（含 fmt/output_path/content/file_size）或
            {"success": False, "message": ...}
        """
        if self._facade:
            res = self._facade.generate_spec_report(fmt)
            if res.success and res.payload is not None:
                return asdict(res.payload)
            return {"success": res.success, "message": res.message}
        return {"success": False, "message": "未初始化"}

    @Slot(bool, result="QVariant")
    def checkSpecFrontmatter(self, autoFix: bool = False) -> dict[str, Any]:
        """检查/修复规范 Frontmatter（M5 CHG-121 新增）

        Args:
            autoFix: True 时自动添加缺失的 frontmatter

        Returns:
            检查结果 dict（含 items/total_count/pending_count/skipped_count/
            error_count/modified_count/auto_fixed）或
            {"success": False, "message": ...}
        """
        if self._facade:
            res = self._facade.check_spec_frontmatter(auto_fix=autoFix)
            if res.success and res.payload is not None:
                return asdict(res.payload)
            return {"success": res.success, "message": res.message}
        return {"success": False, "message": "未初始化"}
