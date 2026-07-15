"""PLC-HMI 概念映射：HMI 变量表（Delivery 域）

像 HMI 触摸屏的变量表，定义了 QML 画面能访问的所有交付管理相关变量和方法：
- @Slot 方法 = HMI 按钮触发的脚本（文档刷新/报告生成/资产汇总）
- Signal = HMI 变量变化事件（数据变了自动刷新画面）

--- 原始注释 ---
Delivery Bridge (QML)

M4 第 2 批重构：5 个 Slot 改用 dataclasses.asdict() 转换 DTO 为 dict 给 QML。
M5 CHG-116：refreshAssetSummary / getAssetSummary Slot 已接入 WorkspaceView.qml 资产汇总 Card。
"""
from dataclasses import asdict
from typing import Any

from PySide6.QtCore import Property, QObject, Slot

from auto_pm.application.delivery_facade import DeliveryFacade


class DeliveryBridge(QObject):

    def __init__(self, facade: DeliveryFacade | None = None, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._facade = facade

    def set_facade(self, facade: DeliveryFacade | None) -> None:
        self._facade = facade

    @Property(bool, constant=True)
    def hasService(self) -> bool:
        return self._facade is not None

    @Slot(result="QVariant")
    def getProjectReport(self) -> dict[str, Any]:
        if self._facade:
            res = self._facade.get_project_report()
            if res.success and res.payload:
                return asdict(res.payload)
        return {}

    @Slot(result="QVariant")
    def getChangeReport(self) -> dict[str, Any]:
        if self._facade:
            res = self._facade.get_change_report()
            if res.success and res.payload:
                return asdict(res.payload)
        return {}

    @Slot(result="QVariant")
    def getSpecReport(self) -> dict[str, Any]:
        if self._facade:
            res = self._facade.get_spec_report()
            if res.success and res.payload:
                return asdict(res.payload)
        return {}

    @Slot(result="QVariant")
    def getScanReport(self) -> dict[str, Any]:
        if self._facade:
            res = self._facade.get_scan_report()
            if res.success and res.payload:
                return asdict(res.payload)
        return {}

    @Slot(str, bool, result="QVariant")
    def refreshProjectDocs(self, project_id: str, dry_run: bool = False) -> dict[str, Any]:
        if self._facade:
            res = self._facade.refresh_project_docs(project_id, dry_run)
            if res.success and res.payload:
                return asdict(res.payload)
            return {"success": res.success, "message": res.message}
        return {"success": False, "message": "未初始化"}

    @Slot(str, result="QVariant")
    def refreshAssetSummary(self, project_id: str) -> dict[str, Any]:
        # M5 CHG-116: 已接入 WorkspaceView.qml 资产汇总 Card 刷新按钮
        if self._facade:
            res = self._facade.refresh_asset_summary(project_id)
            if res.success and res.payload:
                return asdict(res.payload)
            return {"success": res.success, "message": res.message}
        return {"success": False, "message": "未初始化"}

    @Slot(str, result="QVariant")
    def getAssetSummary(self, project_id: str) -> dict[str, Any]:
        # M5 CHG-116: 已接入 WorkspaceView.qml 资产汇总 Card 展示
        if self._facade:
            res = self._facade.get_asset_summary(project_id)
            if res.success and res.payload:
                return asdict(res.payload)
        return {}

    @Slot(str, QObject, result=bool)
    def loadVarTable(self, project_id: str, var_model: Any) -> bool:
        if not self._facade or not self._facade.has_project_service or self._facade._project_service is None:
            return False
        proj = self._facade._project_service.get_project(project_id)
        if proj is None:
            return False

        import os

        from auto_pm.vartable.parsers.io_points_parser import IoPointsParser

        file_path = os.path.join(proj.path, "02_PLC程序", "工程资产", "io_points.csv")
        if not os.path.isfile(file_path):
            var_model.clear()
            return False

        parser = IoPointsParser()
        result = parser.parse(file_path)
        if result.success and result.var_table:
            entries = []
            for entry in result.var_table.entries:
                entries.append({
                    "station": entry.station,
                    "signal_type": entry.signal_type,
                    "address": entry.address,
                    "tag": entry.tag,
                    "signal_name": entry.signal_name,
                    "device": entry.device,
                    "comment": entry.comment,
                })
            var_model.setEntries(entries)
            return True
        return False

    @Slot(str, QObject, result=bool)
    def saveVarTable(self, project_id: str, var_model: Any) -> bool:
        if not self._facade or not self._facade.has_project_service or self._facade._project_service is None:
            return False
        proj = self._facade._project_service.get_project(project_id)
        if proj is None:
            return False

        import csv
        import os

        file_path = os.path.join(proj.path, "02_PLC程序", "工程资产", "io_points.csv")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        entries = var_model.getEntries()
        fieldnames = ["station", "signal_type", "address", "tag", "signal_name", "device", "comment"]

        try:
            with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for entry in entries:
                    writer.writerow(entry)
            return True
        except OSError:
            return False

    @Slot(str, result=list)
    def listProjectDocs(self, project_id: str) -> list[dict[str, Any]]:
        if not self._facade or not self._facade.has_project_service or self._facade._project_service is None:
            return []
        proj = self._facade._project_service.get_project(project_id)
        if proj is None:
            return []

        import os
        from datetime import datetime

        docs = []
        # Walk project directory for markdown files
        for root_dir, _, files in os.walk(proj.path):
            for file in files:
                if file.endswith(".md"):
                    abs_path = os.path.join(root_dir, file)
                    rel_path = os.path.relpath(abs_path, proj.path).replace("\\", "/")
                    try:
                        stat = os.stat(abs_path)
                        size_kb = round(stat.st_size / 1024, 1)
                        mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                    except OSError:
                        size_kb = 0.0
                        mtime = "—"
                    
                    docs.append({
                        "name": rel_path,
                        "path": abs_path.replace("\\", "/"),
                        "size_kb": size_kb,
                        "last_modified": mtime
                    })
        # Sort documents by name
        docs.sort(key=lambda d: str(d["name"]))
        return docs

    @Slot(str, result=str)
    def renderMarkdown(self, file_path: str) -> str:
        import os

        import markdown

        if not os.path.isfile(file_path):
            return "<p style='color: red;'>文件不存在</p>"

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            # Convert markdown to html
            html = markdown.markdown(content, extensions=['extra', 'codehilite', 'toc'])
            # Wrap with basic CSS to look nice in QML Text (rich text)
            styled_html = f"""
            <html>
            <head>
            <style>
                body {{ font-family: sans-serif; color: #E0E0E0; line-height: 1.6; font-size: 14px; }}
                h1 {{ color: #ffffff; font-size: 20px; border-bottom: 1px solid #444; padding-bottom: 8px; }}
                h2 {{ color: #ffffff; font-size: 18px; border-bottom: 1px solid #333; padding-bottom: 4px; }}
                h3 {{ color: #ffffff; font-size: 16px; }}
                code {{ background-color: #2D2D2D; padding: 2px 4px; border-radius: 4px; font-family: monospace; color: #FF8A80; }}
                pre {{ background-color: #2D2D2D; padding: 12px; border-radius: 6px; overflow-x: auto; }}
                pre code {{ background-color: transparent; padding: 0; color: #E0E0E0; }}
                a {{ color: #40C4FF; text-decoration: none; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 16px; }}
                th, td {{ border: 1px solid #444; padding: 8px; text-align: left; }}
                th {{ background-color: #333; color: #fff; }}
                blockquote {{ border-left: 4px solid #00E5FF; padding-left: 12px; color: #B0BEC5; margin-left: 0; }}
            </style>
            </head>
            <body>
            {html}
            </body>
            </html>
            """
            return styled_html
        except Exception as e:
            return f"<p style='color: red;'>解析 Markdown 失败: {str(e)}</p>"

