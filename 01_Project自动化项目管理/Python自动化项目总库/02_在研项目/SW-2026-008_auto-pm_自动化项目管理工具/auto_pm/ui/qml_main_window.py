"""QML 主窗口入口（V0.9.0 QML 单入口）

用 QQmlApplicationEngine 加载 main.qml，通过 rootContext() 注入 5 个域 Bridge
（Workbench/Change/Spec/Delivery/System）+ ProjectListModel。

版本演进：
- V0.6.0 Week 1 PoC：QmlBridge + ProjectListModel 基础入口
- V0.8.0 Phase 1+2：扩展注入 6 个新 Service + SpecCenterAdapter
- V0.9.0：旧 QWidget main_window.py 完整移除，QML 成为唯一 GUI 入口；
  CLI 标志 --qml/--qwidget 退役，gui_command 简化为 (ctx, debug)；
  QmlBridge 拆分为 5 个域 Bridge（change/workbench/delivery/system/spec）

启动方式：
    auto-pm gui
    auto-pm gui --debug

设计参考：02_设计/GUI原型设计.md §15.4 QML 架构设计
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from PySide6.QtCore import QObject, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from auto_pm.change.change_service import ChangeService
from auto_pm.core.project_service import ProjectService
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
from auto_pm.ui.qml.models.var_table_model import VarTableModel
from auto_pm.ui.registry import FacadeRegistry


def run_qml_gui(workspace_root: str, debug: bool = False) -> int:
    """启动 QML GUI（V0.9.0 QML 单入口）

    初始化 10 个后端 Service + FacadeRegistry + 5 个域 Bridge，加载 main.qml。

    Args:
        workspace_root: 工作空间根路径
        debug: 是否开启调试日志

    Returns:
        应用退出码
    """
    # 1. 创建 QGuiApplication（QML 应用用 QGuiApplication 而非 QApplication）
    app = QGuiApplication.instance() or QGuiApplication(sys.argv)

    # 1.5 设置 Basic 样式（支持控件 background 自定义，消除原生样式警告）
    QQuickStyle.setStyle("Basic")

    # 1.8 初始化 DatabaseManager 并注入
    from auto_pm.db.connection import DatabaseManager
    db = DatabaseManager(workspace_root)

    # 2. 初始化后端 Service（后端零改动约束：直接复用现有 Service）
    project_service = ProjectService(workspace_root=workspace_root, db=db)
    change_service = ChangeService(workspace_root=workspace_root, db=db)
    spec_check_service = make_spec_check_service(workspace_root)
    # V0.8.0 Phase 1 新增 6 个 Service（CHG-090）
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
        workspace_root=workspace_root,
    )
    asset_summary_service = make_asset_summary_service()
    doc_refresh_service = make_doc_refresh_service(workspace_root)
    # V0.8.0 Phase 2 新增 SpecCenterAdapter（CHG-091）
    spec_center_service = make_spec_center_service(workspace_root)
    # M5 CHG-119 新增 IndexService（规范索引生成）
    spec_index_service = make_spec_index_service(workspace_root)
    # M5 CHG-120 新增 Spec 域 ReportService（规范报告生成）
    spec_report_service = make_spec_report_service(workspace_root)
    # M5 CHG-121 新增 FrontmatterService（规范 Frontmatter 检查/修复）
    frontmatter_service = make_spec_frontmatter_service(workspace_root)

    # M1 阶段：初始化 FacadeRegistry
    registry = FacadeRegistry()
    registry.initialize({
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

    if debug:
        sys.stderr.write(
            f"[DEBUG] Service 初始化:\n"
            f"  project=✓ change=✓ spec="
            f"{'✓' if spec_check_service else '✗（无 spec_registry.json）'}\n"
            f"  report={'✓' if report_service else '✗'} "
            f"template={'✓' if template_service else '✗'} "
            f"pm_session={'✓' if pm_session_service else '✗'}\n"
            f"  dashboard={'✓' if dashboard_service else '✗'} "
            f"asset_summary={'✓' if asset_summary_service else '✗'} "
            f"doc_refresh={'✓' if doc_refresh_service else '✗'}\n"
            f"  spec_center={'✓' if spec_center_service else '✗（无 spec_registry.json）'} "
            f"spec_index={'✓' if spec_index_service else '✗（无 spec_registry.json）'} "
            f"spec_report={'✓' if spec_report_service else '✗（无 spec_registry.json）'} "
            f"frontmatter={'✓' if frontmatter_service else '✗（无 spec_registry.json）'}\n"
        )

    # 3. 创建 QML 桥接对象
    workbench_bridge = WorkbenchBridge(facade=registry.workbench_facade)
    change_bridge = ChangeBridge(facade=registry.change_facade)
    spec_bridge = SpecBridge(facade=registry.spec_facade)
    delivery_bridge = DeliveryBridge(facade=registry.delivery_facade)
    system_bridge = SystemBridge(facade=registry.system_facade)
    project_model = ProjectListModel()
    var_table_model = VarTableModel()

    # 4. 加载 main.qml
    qml_dir = Path(__file__).parent / "qml"
    main_qml_path = qml_dir / "main.qml"

    if not main_qml_path.exists():
        sys.stderr.write(f"[ERROR] main.qml 不存在: {main_qml_path}\n")
        return 1

    engine = QQmlApplicationEngine()

    # 5. 注入 context property（QML 端通过 xxxBridge / projectModel 访问）
    engine.rootContext().setContextProperty("workbenchBridge", workbench_bridge)
    engine.rootContext().setContextProperty("changeBridge", change_bridge)
    engine.rootContext().setContextProperty("specBridge", spec_bridge)
    engine.rootContext().setContextProperty("deliveryBridge", delivery_bridge)
    engine.rootContext().setContextProperty("systemBridge", system_bridge)
    engine.rootContext().setContextProperty("projectModel", project_model)
    engine.rootContext().setContextProperty("varTableModel", var_table_model)

    # 6. 加载 QML 文件
    qml_url = QUrl.fromLocalFile(str(main_qml_path))
    engine.load(qml_url)

    # 7. 检查加载结果
    if not engine.rootObjects():
        sys.stderr.write("[ERROR] QML 加载失败，rootObjects() 为空\n")
        return 1

    root_obj: QObject = engine.rootObjects()[0]
    if debug:
        sys.stderr.write(f"[DEBUG] QML root object: {type(root_obj).__name__}\n")
        sys.stderr.write(f"[DEBUG] workspace_root: {workspace_root}\n")

    # 8. 启动事件循环
    return app.exec()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write("用法: python -m auto_pm.ui.qml_main_window <workspace_root>\n")
        sys.exit(1)
    workspace = os.path.abspath(sys.argv[1])
    sys.exit(run_qml_gui(workspace_root=workspace, debug="--debug" in sys.argv))
