"""GUI 冒烟测试 - 全页面截图 + 控制台警告收集

用途：对 auto-pm QML GUI 进行端到端冒烟测试，覆盖所有 8 个主要页面和关键对话框，
每次操作后截图，收集 QML 警告/错误，输出测试结果。

运行方式：
    python scripts/gui_smoke_test.py --workspace <工作空间路径> --output <输出目录>

注意：
- GUI 测试默认可见模式（用户硬约束）
- 截图保存到 output/screenshots/ 目录
- 测试结果以 JSON 格式输出到 output/test_result.json
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QObject, QTimer, QtMsgType, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow
from PySide6.QtQuickControls2 import QQuickStyle


class GuiTestRunner(QObject):
    """GUI 冒烟测试运行器

    按顺序执行测试步骤，每步截图，收集警告。
    """

    def __init__(
        self,
        engine: QQmlApplicationEngine,
        output_dir: Path,
        workspace_root: str,
    ) -> None:
        super().__init__()
        self.engine = engine
        self.output_dir = output_dir
        self.screenshots_dir = output_dir / "screenshots"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.workspace_root = workspace_root

        self.warnings: list[dict] = []
        self.screenshots: list[dict] = []
        self.test_steps: list[dict] = []
        self.current_step = 0
        self.step_index = 0

        self._install_message_handler()

    def _install_message_handler(self) -> None:
        """安装 Qt 消息处理器，捕获 QML 警告和错误"""
        def handler(mode, context, message):
            if mode in (QtMsgType.QtWarningMsg, QtMsgType.QtCriticalMsg, QtMsgType.QtFatalMsg):
                type_name = {
                    QtMsgType.QtWarningMsg: "Warning",
                    QtMsgType.QtCriticalMsg: "Critical",
                    QtMsgType.QtFatalMsg: "Fatal",
                }.get(mode, "Unknown")
                self.warnings.append({
                    "type": type_name,
                    "message": message,
                    "file": context.file if context else "",
                    "line": context.line if context else 0,
                    "function": context.function if context else "",
                    "timestamp": datetime.now().isoformat(),
                })

        from PySide6.QtCore import qInstallMessageHandler
        qInstallMessageHandler(handler)

    def _take_screenshot(self, name: str, description: str) -> str:
        """对当前窗口截图，保存到 screenshots 目录

        Returns:
            截图文件相对路径
        """
        # 刷新渲染与事件队列，确保界面与后台数据对齐后再截图
        from PySide6.QtCore import QCoreApplication
        QCoreApplication.processEvents()

        root_objects = self.engine.rootObjects()
        if not root_objects:
            return ""

        window = root_objects[0]
        if not isinstance(window, QQuickWindow):
            return ""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.step_index:02d}_{name}_{timestamp}.png"
        filepath = self.screenshots_dir / filename

        image = window.grabWindow()
        image.save(str(filepath), "PNG")

        rel_path = f"screenshots/{filename}"
        self.screenshots.append({
            "step": self.step_index,
            "name": name,
            "description": description,
            "path": rel_path,
            "timestamp": datetime.now().isoformat(),
        })
        return rel_path

    def _get_root_window(self) -> QQuickWindow | None:
        """获取根窗口对象"""
        root_objects = self.engine.rootObjects()
        if not root_objects:
            return None
        window = root_objects[0]
        if isinstance(window, QQuickWindow):
            return window
        return None

    def _navigate_to_page(self, page_name: str, page_key: str) -> bool:
        """导航到指定页面

        通过设置 mainWindow.currentPage 属性切换页面。
        """
        window = self._get_root_window()
        if not window:
            return False

        window.setProperty("currentPage", page_key)
        return True

    def run(self) -> dict:
        """执行所有测试步骤

        Returns:
            测试结果字典
        """
        start_time = datetime.now()

        steps = self._build_test_steps()

        def execute_next_step():
            if self.step_index >= len(steps):
                self._finish_test(start_time)
                return

            step = steps[self.step_index]
            try:
                result = step["action"]()
                self.test_steps.append({
                    "index": self.step_index,
                    "name": step["name"],
                    "description": step["description"],
                    "status": "passed" if result else "failed",
                    "timestamp": datetime.now().isoformat(),
                })
            except Exception as e:
                self.test_steps.append({
                    "index": self.step_index,
                    "name": step["name"],
                    "description": step["description"],
                    "status": "error",
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "timestamp": datetime.now().isoformat(),
                })

            self.step_index += 1
            QTimer.singleShot(500, execute_next_step)

        QTimer.singleShot(1000, execute_next_step)

        return {}

    def _build_test_steps(self) -> list[dict]:
        """构建测试步骤列表"""
        return [
            {
                "name": "应用启动",
                "description": "验证应用启动成功，主窗口可见",
                "action": self._step_app_launch,
            },
            {
                "name": "项目列表页",
                "description": "导航到项目列表页，验证页面加载",
                "action": self._step_project_list,
            },
            {
                "name": "变更中心页",
                "description": "导航到变更中心页，验证页面加载",
                "action": self._step_change_center,
            },
            {
                "name": "规范中心页",
                "description": "导航到规范中心页，验证页面加载",
                "action": self._step_spec_center,
            },
            {
                "name": "报告中心页",
                "description": "导航到报告中心页，验证页面加载",
                "action": self._step_report_center,
            },
            {
                "name": "模板管理页",
                "description": "导航到模板管理页，验证页面加载",
                "action": self._step_template_manage,
            },
            {
                "name": "设置页",
                "description": "导航到设置页，验证页面加载",
                "action": self._step_settings,
            },
            {
                "name": "工作台页",
                "description": "导航到工作台页（通过选中第一个项目），验证页面加载",
                "action": self._step_workspace,
            },
            {
                "name": "返回项目列表",
                "description": "从工作台返回项目列表页",
                "action": self._step_back_to_project_list,
            },
        ]

    def _step_app_launch(self) -> bool:
        """步骤：应用启动"""
        window = self._get_root_window()
        if not window:
            return False
        # 冒烟测试启动时强制重建索引，确保缓存数据完整
        workbench_bridge = self.engine.rootContext().contextProperty("workbenchBridge")
        change_bridge = self.engine.rootContext().contextProperty("changeBridge")
        if workbench_bridge:
            print("正在冒烟测试中重建数据库缓存...")
            workbench_bridge.rebuildIndex()
            workbench_bridge.refreshProjects()
            if change_bridge:
                change_bridge.refreshChanges()
        self._take_screenshot("app_launch", "应用启动后主窗口初始状态")
        return window.isVisible()

    def _step_project_list(self) -> bool:
        """步骤：项目列表页"""
        result = self._navigate_to_page("项目列表", "projectList")
        if result:
            self._take_screenshot("project_list", "项目列表页 - 显示所有项目")
        return result

    def _step_change_center(self) -> bool:
        """步骤：变更中心页"""
        result = self._navigate_to_page("变更中心", "changeCenter")
        if result:
            self._take_screenshot("change_center", "变更中心页 - 显示所有变更单")
        return result

    def _step_spec_center(self) -> bool:
        """步骤：规范中心页"""
        result = self._navigate_to_page("规范中心", "specCenter")
        if result:
            self._take_screenshot("spec_center", "规范中心页 - 显示规范概览/索引/检查")
        return result

    def _step_report_center(self) -> bool:
        """步骤：报告中心页"""
        result = self._navigate_to_page("报告中心", "reportCenter")
        if result:
            self._take_screenshot("report_center", "报告中心页 - 显示报告模板和生成入口")
        return result

    def _step_template_manage(self) -> bool:
        """步骤：模板管理页"""
        result = self._navigate_to_page("模板管理", "templateManage")
        if result:
            self._take_screenshot("template_manage", "模板管理页 - 显示项目模板列表")
        return result

    def _step_settings(self) -> bool:
        """步骤：设置页"""
        result = self._navigate_to_page("设置", "settings")
        if result:
            self._take_screenshot("settings", "设置页 - 显示应用设置选项")
        return result

    def _step_workspace(self) -> bool:
        """步骤：工作台页"""
        # 通过选中第一个项目来加载工作台详情
        workbench_bridge = self.engine.rootContext().contextProperty("workbenchBridge")
        if workbench_bridge:
            projects = workbench_bridge.listProjects()
            if projects:
                first_proj = projects[0]
                print(f"正在选中第一个项目进行工作台冒烟测试: {first_proj.get('project_id')}")
                workbench_bridge.selectProject(first_proj.get("project_id"), first_proj.get("name"))
                
                # 刷新事件队列使 projectSelected 信号和 UI 绑定生效
                from PySide6.QtCore import QCoreApplication
                QCoreApplication.processEvents()

        result = self._navigate_to_page("工作台", "workspace")
        if result:
            from PySide6.QtCore import QCoreApplication
            QCoreApplication.processEvents()
            self._take_screenshot("workspace", "工作台页 - 项目概览和详情")
        return result

    def _step_back_to_project_list(self) -> bool:
        """步骤：返回项目列表"""
        result = self._navigate_to_page("项目列表", "projectList")
        if result:
            self._take_screenshot("back_to_project_list", "返回项目列表页 - 验证导航往返正常")
        return result

    def _finish_test(self, start_time: datetime) -> None:
        """完成测试，输出结果"""
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        passed = sum(1 for s in self.test_steps if s["status"] == "passed")
        failed = sum(1 for s in self.test_steps if s["status"] == "failed")
        errors = sum(1 for s in self.test_steps if s["status"] == "error")

        result = {
            "test_name": "auto-pm QML GUI 冒烟测试",
            "version": "V1.0.0",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "workspace_root": self.workspace_root,
            "summary": {
                "total_steps": len(self.test_steps),
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "total_screenshots": len(self.screenshots),
                "total_warnings": len(self.warnings),
            },
            "test_steps": self.test_steps,
            "screenshots": self.screenshots,
            "warnings": self.warnings,
        }

        result_path = self.output_dir / "test_result.json"
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"\n{'='*60}")
        print("GUI 冒烟测试完成")
        print(f"{'='*60}")
        print(f"总步骤: {len(self.test_steps)}")
        print(f"通过: {passed}")
        print(f"失败: {failed}")
        print(f"错误: {errors}")
        print(f"截图数: {len(self.screenshots)}")
        print(f"警告数: {len(self.warnings)}")
        print(f"耗时: {duration:.1f}s")
        print(f"结果文件: {result_path}")
        print(f"{'='*60}\n")

        QGuiApplication.quit()


def main() -> int:
    parser = argparse.ArgumentParser(description="auto-pm QML GUI 冒烟测试")
    parser.add_argument(
        "--workspace",
        "-w",
        required=True,
        help="工作空间根路径",
    )
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="测试结果输出目录",
    )
    args = parser.parse_args()

    workspace_root = str(Path(args.workspace).resolve())
    output_dir = Path(args.output).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    app = QGuiApplication.instance() or QGuiApplication(sys.argv)

    # 设置 Basic 样式（支持控件 background 自定义，消除原生样式警告）
    QQuickStyle.setStyle("Basic")

    from auto_pm.change.change_service import ChangeService
    from auto_pm.core.project_service import ProjectService
    from auto_pm.db.connection import DatabaseManager
    from auto_pm.ui.factories import (
    make_asset_summary_service,
    make_dashboard_service,
    make_doc_refresh_service,
    make_pm_session_service,
    make_report_service,
    make_spec_center_service,
    make_spec_check_service,
    make_spec_frontmatter_service,
    make_spec_index_service,
    make_spec_report_service,
    make_template_service,
)
    from auto_pm.ui.qml.bridges.change_bridge import ChangeBridge
    from auto_pm.ui.qml.bridges.delivery_bridge import DeliveryBridge
    from auto_pm.ui.qml.bridges.spec_bridge import SpecBridge
    from auto_pm.ui.qml.bridges.system_bridge import SystemBridge
    from auto_pm.ui.qml.bridges.workbench_bridge import WorkbenchBridge
    from auto_pm.ui.qml.models.project_list_model import ProjectListModel
    from auto_pm.ui.registry import FacadeRegistry
    db = DatabaseManager(workspace_root)

    project_service = ProjectService(workspace_root=workspace_root, db=db)
    change_service = ChangeService(workspace_root=workspace_root, db=db)
    spec_check_service = make_spec_check_service(workspace_root)
    report_service = make_report_service(
        project_service=project_service,
        change_service=change_service,
        workspace_root=workspace_root,
        db=db,
    )
    template_service = make_template_service(workspace_root)
    pm_session_service = make_pm_session_service(workspace_root)
    dashboard_service = make_dashboard_service(
        project_service=project_service,
        change_service=change_service,
    )
    asset_summary_service = make_asset_summary_service()
    doc_refresh_service = make_doc_refresh_service(workspace_root)
    spec_center_service = make_spec_center_service(workspace_root)
    spec_index_service = make_spec_index_service(workspace_root)
    spec_report_service = make_spec_report_service(workspace_root)
    frontmatter_service = make_spec_frontmatter_service(workspace_root)

    facade_registry = FacadeRegistry()
    facade_registry.initialize({
        "project_service": project_service,
        "change_service": change_service,
        "spec_check_service": spec_check_service,
        "report_service": report_service,
        "template_service": template_service,
        "pm_session_service": pm_session_service,
        "dashboard_service": dashboard_service,
        "asset_summary_service": asset_summary_service,
        "doc_refresh_service": doc_refresh_service,
        "spec_center_service": spec_center_service,
        "index_service": spec_index_service,
        "spec_report_service": spec_report_service,
        "frontmatter_service": frontmatter_service,
    })

    project_model = ProjectListModel()
    workbench_bridge = WorkbenchBridge(facade=facade_registry.workbench_facade)
    change_bridge = ChangeBridge(facade=facade_registry.change_facade)
    spec_bridge = SpecBridge(facade=facade_registry.spec_facade)
    delivery_bridge = DeliveryBridge(facade=facade_registry.delivery_facade)
    system_bridge = SystemBridge(facade=facade_registry.system_facade)

    engine = QQmlApplicationEngine()
    qml_dir = Path(__file__).parent.parent / "auto_pm" / "ui" / "qml"
    engine.addImportPath(str(qml_dir))

    context = engine.rootContext()
    context.setContextProperty("workspace_root", workspace_root)
    context.setContextProperty("workbenchBridge", workbench_bridge)
    context.setContextProperty("changeBridge", change_bridge)
    context.setContextProperty("specBridge", spec_bridge)
    context.setContextProperty("deliveryBridge", delivery_bridge)
    context.setContextProperty("systemBridge", system_bridge)
    context.setContextProperty("projectModel", project_model)

    runner = GuiTestRunner(engine, output_dir, workspace_root)

    main_qml = qml_dir / "main.qml"
    engine.load(QUrl.fromLocalFile(str(main_qml.resolve())))

    if not engine.rootObjects():
        print("错误：QML 引擎加载失败，根对象为空")
        return -1

    runner.run()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
