"""QML 主窗口入口（V0.6.0 Week 1 PoC / V0.8.0 Phase 1+2 扩展）

独立的 QML UI 入口，用 QQmlApplicationEngine 加载 main.qml。
- 不修改现有 main_window.py（保证现有 QWidget UI 零回归）
- 通过 rootContext() 注入 QmlBridge 和 ProjectListModel
- Week 4 收尾时再统一替换 main_window.py

V0.8.0 Phase 1（CHG-090）：扩展注入 6 个新 Service（Report/Template/PmSession/
Dashboard/AssetSummary/DocRefresh），为 4 个新 QML 页面做前置准备。
V0.8.0 Phase 2（CHG-091）：扩展注入 SpecCenterAdapter，为 SpecCenterView 提供
get_overview/list_entries 等 Slot 后端。

启动方式：
    python -m auto_pm gui --qml
    或
    auto-pm gui --qml

设计参考：02_设计/GUI原型设计.md §15.4 QML 架构设计
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from PySide6.QtCore import QObject, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from auto_pm.change.change_service import ChangeService
from auto_pm.core.project_service import ProjectService
from auto_pm.ui.qml.models.project_list_model import ProjectListModel
from auto_pm.ui.qml.qml_bridge import (
    QmlBridge,
    make_asset_summary_service,
    make_dashboard_service,
    make_doc_refresh_service,
    make_pm_session_service,
    make_report_service,
    make_spec_center_service,
    make_spec_check_service,
    make_template_service,
)


def run_qml_gui(workspace_root: str, debug: bool = False) -> int:
    """启动 QML GUI

    V0.6.0 W2：注入 ProjectService + ChangeService + SpecCheckService
    V0.8.0 Phase 1（CHG-090）：扩展注入 6 个新 Service
    V0.8.0 Phase 2（CHG-091）：扩展注入 SpecCenterAdapter

    Args:
        workspace_root: 工作空间根路径
        debug: 是否开启调试日志

    Returns:
        应用退出码
    """
    # 1. 创建 QGuiApplication（QML 应用用 QGuiApplication 而非 QApplication）
    app = QGuiApplication.instance() or QGuiApplication(sys.argv)

    # 2. 初始化后端 Service（后端零改动约束：直接复用现有 Service）
    project_service = ProjectService(workspace_root=workspace_root)
    change_service = ChangeService(workspace_root=workspace_root)
    spec_check_service = make_spec_check_service(workspace_root)
    # V0.8.0 Phase 1 新增 6 个 Service（CHG-090）
    report_service = make_report_service(
        project_service=project_service,
        change_service=change_service,
        workspace_root=workspace_root,
    )
    template_service = make_template_service(workspace_root)
    pm_session_service = make_pm_session_service(workspace_root)
    dashboard_service = make_dashboard_service(
        project_service=project_service,
        change_service=change_service,
    )
    asset_summary_service = make_asset_summary_service()
    doc_refresh_service = make_doc_refresh_service(workspace_root)
    # V0.8.0 Phase 2 新增 SpecCenterAdapter（CHG-091）
    spec_center_service = make_spec_center_service(workspace_root)

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
            f"  spec_center={'✓' if spec_center_service else '✗（无 spec_registry.json）'}\n"
        )

    # 3. 创建 QML 桥接对象（V0.8.0 Phase 1+2 扩展注入 9 个新 Service）
    bridge = QmlBridge(
        project_service=project_service,
        change_service=change_service,
        spec_check_service=spec_check_service,
        report_service=report_service,
        template_service=template_service,
        pm_session_service=pm_session_service,
        dashboard_service=dashboard_service,
        asset_summary_service=asset_summary_service,
        doc_refresh_service=doc_refresh_service,
        spec_center_service=spec_center_service,
    )
    project_model = ProjectListModel()

    # 4. 加载 main.qml
    qml_dir = Path(__file__).parent / "qml"
    main_qml_path = qml_dir / "main.qml"

    if not main_qml_path.exists():
        sys.stderr.write(f"[ERROR] main.qml 不存在: {main_qml_path}\n")
        return 1

    engine = QQmlApplicationEngine()

    # 5. 注入 context property（QML 端通过 bridge / projectModel 访问）
    engine.rootContext().setContextProperty("bridge", bridge)
    engine.rootContext().setContextProperty("projectModel", project_model)

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
