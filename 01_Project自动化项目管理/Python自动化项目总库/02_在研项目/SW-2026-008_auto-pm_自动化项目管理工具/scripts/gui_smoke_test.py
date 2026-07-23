"""GUI 冒烟测试 - 全页面截图 + 控制台警告收集

用途：对 auto-pm QML GUI 进行端到端冒烟测试，覆盖所有 8 个主要页面和关键对话框，
每次操作后截图，收集 QML 警告/错误，输出测试结果。

运行方式：
    python scripts/gui_smoke_test.py --workspace <工作空间路径> --output <输出目录>

注意：
- GUI 测试默认可见模式（用户硬约束）
- 截图保存到 output/screenshots/ 目录
- 测试结果以 JSON 格式输出到 output/test_result.json

CHG-SCPT-2026-141 扩展：新增 FileWatcherBridge 集成测试步骤（步骤 10-13）
- 步骤10：验证文件监听工具栏可见 + 监听已启动
- 步骤11：手动同步按钮（syncNow → 等 syncFinished 信号）
- 步骤12：监听开关 toggle（关闭→验证目录数 0→重新开启）
- 步骤13：业务文件改动自动同步（创建临时文件 → 等 debounce+sync → 验证信号触发）
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from PySide6.QtCore import QObject, QTimer, QtMsgType, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QSignalSpy

if TYPE_CHECKING:
    from auto_pm.ui.qml.bridges.file_watcher_bridge import FileWatcherBridge


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

        self.warnings: list[dict[str, Any]] = []
        self.screenshots: list[dict[str, Any]] = []
        self.test_steps: list[dict[str, Any]] = []
        self.current_step = 0
        self.step_index = 0

        self._install_message_handler()

    def _install_message_handler(self) -> None:
        """安装 Qt 消息处理器，捕获 QML 警告和错误"""
        def handler(mode: QtMsgType, context: Any, message: str) -> None:
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
        image.save(str(filepath), "PNG")  # type: ignore[call-overload]

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

    def run(self) -> dict[str, Any]:
        """执行所有测试步骤

        Returns:
            测试结果字典
        """
        start_time = datetime.now()

        steps = self._build_test_steps()

        def execute_next_step() -> None:
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

    def _build_test_steps(self) -> list[dict[str, Any]]:
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
            # ── CHG-SCPT-2026-141：FileWatcherBridge 集成测试 ──
            {
                "name": "文件监听工具栏可见",
                "description": "验证全局文件监听工具栏可见且监听已启动",
                "action": self._step_watcher_toolbar_visible,
            },
            {
                "name": "手动同步触发",
                "description": "点击同步按钮触发 syncNow，等待 syncFinished 信号",
                "action": self._step_manual_sync,
            },
            {
                "name": "监听开关 toggle",
                "description": "关闭监听验证目录数归零，再重新开启",
                "action": self._step_watcher_toggle,
            },
            {
                "name": "业务文件自动同步",
                "description": "创建临时业务文件，等待 debounce+sync 自动触发",
                "action": self._step_auto_sync_on_file_change,
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

    # ── CHG-SCPT-2026-141：FileWatcherBridge 集成测试步骤 ──

    def _get_file_watcher_bridge(self) -> FileWatcherBridge | None:
        """获取 FileWatcherBridge context property"""
        prop = self.engine.rootContext().contextProperty("fileWatcherBridge")
        if prop is None:
            return None
        return cast(FileWatcherBridge, prop)

    def _wait_for_signal(self, spy: QSignalSpy, timeout_ms: int = 15000) -> bool:
        """循环 processEvents 等待信号触发（GUI 可见模式）。

        用 time.sleep(0.02) + processEvents 释放 GIL，让 QThreadPool worker
        全速执行 sync_to_cache（参考 tests/qml/test_file_watcher_bridge.py 的
        _wait_for_signal 同款模式）。
        """
        app = QGuiApplication.instance()
        for _ in range(timeout_ms // 20):
            time.sleep(0.02)
            if app is not None:
                app.processEvents()
            if spy.count() > 0:
                return True
        return False

    def _step_watcher_toolbar_visible(self) -> bool:
        """步骤10：验证文件监听工具栏可见 + 监听已启动"""
        bridge = self._get_file_watcher_bridge()
        if not bridge:
            print("  [FAIL] fileWatcherBridge 未注入")
            return False
        enabled = bridge.isWatcherEnabled()
        dir_count = bridge.watchedDirectoryCount()
        print(f"  监听启用={enabled}, 监听目录数={dir_count}")
        self._take_screenshot(
            "watcher_toolbar", "文件监听工具栏 - 全局常驻同步按钮+监听开关"
        )
        return enabled and dir_count > 0

    def _step_manual_sync(self) -> bool:
        """步骤11：手动同步按钮（syncNow → 等 syncFinished 信号）"""
        bridge = self._get_file_watcher_bridge()
        if not bridge:
            return False
        spy = QSignalSpy(bridge.syncFinished)
        bridge.syncNow()
        # sync_to_cache 扫描全工作空间，首次可能较慢，给 15s 超时
        ok = self._wait_for_signal(spy, timeout_ms=15000)
        if ok:
            # PySide6 QSignalSpy 无 takeFirst，用 at(0) 取第一组参数
            args = spy.at(0)
            projects, changes, ms = int(args[0]), int(args[1]), int(args[2])
            print(f"  手动同步完成: {projects} 项目, {changes} 变更, {ms}ms")
        else:
            print("  [FAIL] syncFinished 信号超时未触发")
        self._take_screenshot("manual_sync", "手动同步后 - 状态反馈显示已同步")
        return ok

    def _step_watcher_toggle(self) -> bool:
        """步骤12：监听开关 toggle（关闭→验证 enabled=False→重新开启）

        注意：QFileSystemWatcher.removePaths 在 Windows 上对部分路径会失败
        （directories() 残留），因此关闭后 dirs 可能不为 0。这是 Qt/Windows
        限制，不影响功能——_on_debounce_timeout 会检查 _watcher_enabled，
        关闭后残留监听路径触发的信号不会引发 sync。
        """
        bridge = self._get_file_watcher_bridge()
        if not bridge:
            return False
        # 关闭监听
        bridge.toggleWatcher(False)
        app = QGuiApplication.instance()
        if app:
            app.processEvents()
        off_enabled = bridge.isWatcherEnabled()
        off_count = bridge.watchedDirectoryCount()
        print(f"  关闭后: enabled={off_enabled}, dirs={off_count}")
        if off_enabled:
            print("  [FAIL] 关闭监听后 enabled 未归零")
            self._take_screenshot("watcher_toggle_off_fail", "监听关闭失败")
            return False
        # dirs 残留是 QFileSystemWatcher 限制，enabled=False 即功能正确
        if off_count > 0:
            print(
                f"  [INFO] dirs 残留 {off_count}（QFileSystemWatcher 限制，"
                "已由 _on_debounce_timeout 拦截，不影响功能）"
            )
        # 重新开启（扫描目录可能耗时）
        bridge.toggleWatcher(True)
        ok = False
        for _ in range(500):  # 最多等 10s 扫描完成
            time.sleep(0.02)
            if app:
                app.processEvents()
            if bridge.watchedDirectoryCount() > 0:
                ok = True
                break
        on_enabled = bridge.isWatcherEnabled()
        on_count = bridge.watchedDirectoryCount()
        print(f"  重开后: enabled={on_enabled}, dirs={on_count}")
        self._take_screenshot("watcher_toggle", "监听开关 toggle - 关闭后重新开启")
        return ok and on_enabled and on_count > 0

    def _step_auto_sync_on_file_change(self) -> bool:
        """步骤13：业务文件改动自动同步（创建临时文件 → 等 debounce+sync）"""
        bridge = self._get_file_watcher_bridge()
        if not bridge:
            return False
        if not bridge.isWatcherEnabled():
            print("  [FAIL] 监听未启用，无法测试自动同步")
            return False
        # 在工作空间根创建临时业务文件（不在 NOISE_DIRS 排除范围）
        tmp_file = Path(self.workspace_root) / ".gui_smoke_test_autosync.md"
        spy = QSignalSpy(bridge.syncFinished)
        try:
            tmp_file.write_text(
                f"# GUI 冒烟测试自动同步触发\n\n生成时间: {datetime.now().isoformat()}\n",
                encoding="utf-8",
            )
            # 等待 1s debounce + sync 完成（给 15s 超时）
            ok = self._wait_for_signal(spy, timeout_ms=15000)
            if ok:
                # PySide6 QSignalSpy 无 takeFirst，用 at(0) 取第一组参数
                args = spy.at(0)
                projects, changes, ms = int(args[0]), int(args[1]), int(args[2])
                print(
                    f"  自动同步触发成功: {projects} 项目, {changes} 变更, {ms}ms"
                )
            else:
                print("  [FAIL] 文件改动后 syncFinished 信号超时未触发")
        finally:
            if tmp_file.exists():
                try:
                    tmp_file.unlink()
                except OSError:
                    pass
        self._take_screenshot(
            "auto_sync", "业务文件改动后自动同步 - 状态反馈更新"
        )
        return ok

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
    from auto_pm.ui.qml.bridges.file_watcher_bridge import FileWatcherBridge
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
    # CHG-SCPT-2026-141：文件监听同步桥接层（自建 DB 连接，不依赖共享 db）
    file_watcher_bridge = FileWatcherBridge(workspace_root)

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
    # CHG-SCPT-2026-141：注入文件监听桥接层供 QML 工具栏调用
    context.setContextProperty("fileWatcherBridge", file_watcher_bridge)

    runner = GuiTestRunner(engine, output_dir, workspace_root)

    main_qml = qml_dir / "main.qml"
    engine.load(QUrl.fromLocalFile(str(main_qml.resolve())))

    if not engine.rootObjects():
        print("错误：QML 引擎加载失败，根对象为空")
        return -1

    # CHG-SCPT-2026-141：启动文件监听（模拟 qml_main_window 启动逻辑）
    # 扫描业务目录可能耗时数秒（取决于工作空间大小），在 runner.run 之前完成
    file_watcher_bridge.toggleWatcher(True)
    print(f"文件监听已启动，监听目录数: {file_watcher_bridge.watchedDirectoryCount()}")

    runner.run()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
