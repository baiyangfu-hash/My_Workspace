"""PySide6 主窗口

项目中心式导航：左侧侧边栏 + 顶部工具栏 + 中央 QStackedWidget + 底部状态栏。

UI 层通过 Service 层访问数据，不直接访问文件系统/DB。
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QShowEvent
from PySide6.QtWidgets import (
    QComboBox,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QToolBar,
    QToolButton,
    QWidget,
)

from auto_pm.core.constants import BUSINESS_LINE_OPTIONS
from auto_pm.logging.logging import setup_logger
from auto_pm.models import ProjectInfo
from auto_pm.ui.change_center.center_view import ChangeCenterView
from auto_pm.ui.dialogs import (
    CreateChangeDialog,
    DeleteProjectDialog,
    EditProjectDialog,
    ImportProjectDialog,
    NewProjectDialog,
)
from auto_pm.ui.global_pages.global_view import GlobalView
from auto_pm.ui.global_pages.report_page import ReportPage
from auto_pm.ui.global_pages.settings_page import SettingsPage
from auto_pm.ui.global_pages.spec_center import SpecCenterView
from auto_pm.ui.global_pages.template_page import TemplatePage
from auto_pm.ui.navigation.nav_tree import NavigationTree
from auto_pm.ui.project_list.list_view import ProjectListView
from auto_pm.ui.workspace.workspace_view import ProjectWorkspaceView

if TYPE_CHECKING:
    from auto_pm.db.connection import DatabaseManager

log = setup_logger(log_level="INFO", app_name="auto_pm")

# 业务线选项：(value, label)
# M3-Iter7: 基于 core.constants.BUSINESS_LINE_OPTIONS 构建，附加 "全部" 选项
# 标签格式从 "SW 软件开发" 转换为 "软件开发 (SW)" 以适配 UI 显示
_BUSINESS_LINE_OPTIONS: list[tuple[str, str]] = [
    ("all", "全部业务线"),
    *[
        (code, f"{label.split(' ', 1)[1] if ' ' in label else label} ({code})")
        for code, label in BUSINESS_LINE_OPTIONS
    ],
]


class MainWindow(QMainWindow):
    """auto-pm 主窗口

    项目中心式布局：
    - 左侧侧边栏：项目列表/规范中心/模板管理/报告中心/系统设置
    - 顶部工具栏：搜索框 + 业务线筛选 + 新建 + 同步 + 刷新
    - 中央 QStackedWidget：项目列表页 / 项目工作区 / 全局功能页
    - 底部状态栏：项目数/变更数/DB状态/上次扫描时间
    """

    WINDOW_TITLE = "auto-pm 项目管理工具"
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 800

    def __init__(self, workspace_root: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._workspace_root = workspace_root or os.getcwd()
        self._auto_loaded = False
        self._db = self._init_db()
        self._build_ui()

    def _init_db(self) -> DatabaseManager | None:
        """初始化 DB 缓存管理器（失败时返回 None，回退到文件系统扫描）"""
        try:
            from auto_pm.db.connection import DatabaseManager

            db = DatabaseManager(self._workspace_root)
            db.init_schema()
            log.info("DB 缓存已就绪: %s", db.db_path)
            return db
        except Exception as e:
            log.warning("DB 初始化失败，回退到文件系统扫描: %s", e)
            return None

    @staticmethod
    def _resolve_templates_dir() -> str:
        """推断模板目录（auto_pm 包的上级目录下的 templates/）"""
        import auto_pm

        package_dir = os.path.dirname(os.path.abspath(auto_pm.__file__))
        project_root = os.path.dirname(package_dir)
        return os.path.join(project_root, "templates")

    # ── UI 构建 ────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.setWindowTitle(self.WINDOW_TITLE)
        self.resize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

        self._build_sidebar()
        self._build_central()
        self._build_toolbar()
        self._build_statusbar()
        self._apply_stylesheet()

    def _build_sidebar(self) -> None:
        self._nav_tree = NavigationTree()

        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._splitter.addWidget(self._nav_tree)

    def _build_central(self) -> None:
        self._stack = QStackedWidget()
        self._project_list_view = ProjectListView()
        self._workspace_view = ProjectWorkspaceView(self._workspace_root)
        self._global_view = GlobalView()

        # 变更中心所需 Service（复用 DB 缓存）
        from auto_pm.change.change_service import ChangeService
        from auto_pm.core.project_service import ProjectService
        from auto_pm.core.report_service import ReportService
        from auto_pm.core.template_service import TemplateService

        self._change_service = ChangeService(self._workspace_root, db=self._db)
        self._project_service = ProjectService(self._workspace_root, db=self._db)
        self._change_center_view = ChangeCenterView(
            change_service=self._change_service,
            project_service=self._project_service,
        )

        # 全局功能页 Service
        self._report_service = ReportService(
            self._project_service, self._change_service,
            workspace_root=self._workspace_root, db=self._db,
        )
        self._template_service = TemplateService(self._resolve_templates_dir())

        # 全局功能页
        self._report_page = ReportPage(self._report_service)
        self._template_page = TemplatePage(
            self._template_service, self._project_service
        )
        self._settings_page = SettingsPage(
            self._project_service, self._change_service
        )
        self._spec_center_view = SpecCenterView(self._workspace_root)

        self._stack.addWidget(self._project_list_view)  # index 0
        self._stack.addWidget(self._workspace_view)  # index 1
        self._stack.addWidget(self._global_view)  # index 2（保留，不再使用）
        self._stack.addWidget(self._change_center_view)  # index 3
        self._stack.addWidget(self._report_page)  # index 4
        self._stack.addWidget(self._template_page)  # index 5
        self._stack.addWidget(self._settings_page)  # index 6
        self._stack.addWidget(self._spec_center_view)  # index 7

        self._project_list_view.projectSelected.connect(self._on_project_selected)
        self._project_list_view.projectEditRequested.connect(self._on_edit_project)
        self._project_list_view.projectDeleteRequested.connect(self._on_delete_project)
        self._workspace_view.backRequested.connect(self._on_back_to_list)
        self._workspace_view.editRequested.connect(self._on_edit_project)
        self._workspace_view.deleteRequested.connect(self._on_delete_project)

        # 变更中心变更（创建/流转）→ 刷新项目计数
        self._change_center_view.change_updated.connect(self._on_refresh)

        # NavigationTree 信号 → 项目列表筛选 / 页面切换
        self._nav_tree.project_filter_requested.connect(
            self._project_list_view.set_filter
        )
        self._nav_tree.page_switch_requested.connect(self._on_page_switch)

        self._splitter.addWidget(self._stack)
        self._splitter.setStretchFactor(0, 0)
        self._splitter.setStretchFactor(1, 1)
        self.setCentralWidget(self._splitter)

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("主工具栏")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        toolbar.addWidget(QLabel("  搜索: "))
        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText("按编号/名称/描述搜索...")
        self._search_edit.setClearButtonEnabled(True)
        self._search_edit.setMinimumWidth(220)
        self._search_edit.textChanged.connect(self._on_search_changed)
        toolbar.addWidget(self._search_edit)

        toolbar.addWidget(QLabel("  业务线: "))
        self._business_combo = QComboBox()
        for value, label in _BUSINESS_LINE_OPTIONS:
            self._business_combo.addItem(label, value)
        self._business_combo.currentIndexChanged.connect(self._on_business_line_changed)
        toolbar.addWidget(self._business_combo)

        toolbar.addSeparator()
        new_btn = QToolButton()
        new_btn.setText("新建")
        new_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        new_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        new_menu = QMenu(new_btn)
        act_plc = new_menu.addAction("PLC 项目")
        act_py = new_menu.addAction("Python 项目")
        new_menu.addSeparator()
        act_change = new_menu.addAction("变更单")
        act_plc.triggered.connect(lambda: self._on_new_project("plc"))
        act_py.triggered.connect(lambda: self._on_new_project("python"))
        act_change.triggered.connect(self._on_new_change)
        new_btn.setMenu(new_menu)
        toolbar.addWidget(new_btn)

        import_btn = QAction("导入项目", self)
        import_btn.triggered.connect(self._on_import_project)
        toolbar.addAction(import_btn)

        sync_btn = QAction("同步缓存", self)
        sync_btn.triggered.connect(self._on_sync)
        toolbar.addAction(sync_btn)

        refresh_btn = QAction("刷新列表", self)
        refresh_btn.triggered.connect(self._on_refresh)
        toolbar.addAction(refresh_btn)

    def _build_statusbar(self) -> None:
        self._statusbar = QStatusBar()
        self.setStatusBar(self._statusbar)
        self._status_workspace = QLabel("工作空间: —")
        self._status_workspace.setToolTip(self._workspace_root)
        self._status_project = QLabel("项目: 0")
        self._status_change = QLabel("变更: 0")
        self._status_db = QLabel("DB: 未连接")
        self._status_scan = QLabel("上次扫描: —")
        for widget in (
            self._status_workspace,
            self._status_project,
            self._status_change,
            self._status_db,
            self._status_scan,
        ):
            self._statusbar.addPermanentWidget(widget)

    def _apply_stylesheet(self) -> None:
        self.setStyleSheet(
            """
QMainWindow { background: #fafafa; }
QTreeWidget#navTree {
    background: #2c3e50;
    color: #ecf0f1;
    border: none;
    font-size: 13px;
    outline: none;
}
QTreeWidget#navTree::item {
    padding: 6px 8px;
    border: none;
}
QTreeWidget#navTree::item:selected {
    background: #34495e;
    color: #ffffff;
    border-left: 3px solid #4a90d9;
}
QTreeWidget#navTree::item:hover {
    background: #34495e;
}
QToolBar {
    background: #ffffff;
    border-bottom: 1px solid #e0e0e0;
    spacing: 4px;
    padding: 4px;
}
QStatusBar {
    background: #f0f0f0;
    border-top: 1px solid #e0e0e0;
    font-size: 12px;
}
QStatusBar QLabel { padding: 0 8px; color: #555; }
"""
        )

    # ── 导航 ──────────────────────────────────────────────

    def _on_page_switch(self, page_id: str) -> None:
        """响应 NavigationTree 功能节点点击，切换中央页面

        - 'all_projects' → 项目列表页，重置筛选为全部
        - 'change_center' → 变更中心页（ChangeCenterView）
        - 'report' → 报告中心页（ReportPage）
        - 'template' → 模板管理页（TemplatePage）
        - 'settings' → 系统设置页（SettingsPage）
        - 'spec_center' → 规范中心页（SpecCenterView）
        """
        if page_id == "all_projects":
            self._stack.setCurrentIndex(0)
            self._project_list_view.set_filter("all", "")
        elif page_id == "change_center":
            self._stack.setCurrentIndex(3)
        elif page_id == "report":
            self._stack.setCurrentIndex(4)
        elif page_id == "template":
            self._stack.setCurrentIndex(5)
        elif page_id == "settings":
            self._stack.setCurrentIndex(6)
        elif page_id == "spec_center":
            self._stack.setCurrentIndex(7)

    def _on_project_selected(self, project_id: str) -> None:
        proj = self._project_list_view.get_project(project_id)
        if proj is None:
            log.warning("未找到项目: %s", project_id)
            return
        self._workspace_view.load_project(proj)
        self._stack.setCurrentIndex(1)

    def _on_back_to_list(self) -> None:
        self._stack.setCurrentIndex(0)

    def _on_search_changed(self, text: str) -> None:
        self._project_list_view.set_search_text(text)

    def _on_business_line_changed(self) -> None:
        line = self._business_combo.currentData() or "all"
        self._project_list_view.set_business_line(line)

    # ── 业务动作 ──────────────────────────────────────────

    def _on_new_project(self, stack: str = "plc") -> None:
        dialog = NewProjectDialog(self._workspace_root, self, stack=stack)
        dialog.projectCreated.connect(self._on_project_created)
        dialog.exec()

    def _on_new_change(self) -> None:
        """工具栏"新建变更单" → 弹出 CreateChangeDialog"""
        dialog = CreateChangeDialog(
            project_service=self._project_service,
            change_service=self._change_service,
            parent=self,
        )
        dialog.change_created.connect(self._on_change_created)
        dialog.exec()

    def _on_change_created(self, project_id: str) -> None:
        """变更单创建成功 → 刷新变更中心列表 + 刷新项目计数"""
        log.info("变更单已创建（项目 %s）", project_id)
        self._change_center_view.refresh()
        self._on_refresh()

    def _on_project_created(self, project_id: str) -> None:
        log.info("项目已创建: %s", project_id)
        self._on_refresh()

    def _on_edit_project(self, project_id: str) -> None:
        dialog = EditProjectDialog(project_id, self._workspace_root, self)
        dialog.projectUpdated.connect(self._on_project_updated)
        dialog.exec()

    def _on_project_updated(self, project_id: str) -> None:
        log.info("项目已更新: %s", project_id)
        self._on_refresh()

    def _on_delete_project(self, project_id: str) -> None:
        dialog = DeleteProjectDialog(project_id, self._workspace_root, self)
        dialog.projectDeleted.connect(self._on_project_deleted)
        dialog.exec()

    def _on_project_deleted(self, project_id: str) -> None:
        log.info("项目已删除: %s", project_id)
        self._on_refresh()

    def _on_import_project(self) -> None:
        dialog = ImportProjectDialog(self._workspace_root, self)
        dialog.projectImported.connect(self._on_project_imported)
        dialog.exec()

    def _on_project_imported(self, project_id: str) -> None:
        log.info("项目已导入: %s", project_id)
        self._on_refresh()

    def _on_sync(self) -> None:
        """同步 DB 缓存（通过 SyncService 增量扫描文件系统）"""
        if self._db is None:
            QMessageBox.warning(self, "同步缓存", "DB 未初始化，无法同步缓存。")
            return
        try:
            from auto_pm.core.project_service import ProjectService

            svc = ProjectService(self._workspace_root, db=self._db)
            result = svc.sync_to_cache(force_full=False)
            log.info(
                "同步完成: %d 项目, %d 变更单, %dms",
                result.get("projects_found", 0),
                result.get("changes_found", 0),
                result.get("duration_ms", 0),
            )
            self._on_refresh()
        except Exception as e:
            log.error("同步缓存失败: %s", e)
            QMessageBox.warning(self, "同步失败", str(e))

    def _on_refresh(self) -> None:
        """刷新项目列表（通过 Service 层加载）"""
        self._project_list_view.set_loading()
        # 延迟实际扫描，让加载状态先渲染
        QTimer.singleShot(0, self._do_refresh)

    def _do_refresh(self) -> None:
        """实际执行刷新（延迟调用以让加载状态先显示）"""
        try:
            projects = self._load_projects()
            self._project_list_view.set_projects(projects)
            self._nav_tree.update_counts(projects)
            self._update_statusbar(projects)
            self._change_center_view.refresh()
            # 全局功能页刷新（各页面内部已捕获异常，不会中断整体刷新）
            self._report_page.refresh()
            self._template_page.refresh()
            self._settings_page.refresh()
        except Exception as e:
            log.error("刷新项目列表失败: %s", e)
            self._project_list_view.set_error(str(e))
            QMessageBox.warning(self, "刷新失败", str(e))

    def _load_projects(self) -> list[ProjectInfo]:
        """加载项目列表（优先 DB 缓存，失败时回退文件系统扫描）"""
        projects = self._load_projects_cached()
        if projects:
            return projects
        return self._load_projects_from_fs()

    def _load_projects_cached(self) -> list[ProjectInfo]:
        """从 DB 缓存读取项目列表（缓存为空或异常时返回空列表）"""
        if self._db is None:
            return []
        try:
            from auto_pm.core.project_service import ProjectService

            svc = ProjectService(self._workspace_root, db=self._db)
            return svc.list_projects_cached()
        except Exception as e:
            log.warning("DB 缓存读取失败，回退文件系统扫描: %s", e)
            return []

    def _load_projects_from_fs(self) -> list[ProjectInfo]:
        """从文件系统扫描项目列表（回退路径）"""
        from auto_pm.core.project_service import ProjectService

        svc = ProjectService(self._workspace_root)
        return svc.list_projects()

    def _update_statusbar(self, projects: list[ProjectInfo]) -> None:
        total = len(projects)
        self._status_workspace.setText(f"工作空间: {self._workspace_root}")
        self._status_workspace.setToolTip(self._workspace_root)
        self._status_project.setText(f"项目: {total}")
        self._status_change.setText("变更: 0")
        if self._db is not None:
            self._status_db.setText("DB: 已连接")
        else:
            self._status_db.setText("DB: 未连接")
        self._status_scan.setText(f"上次扫描: {self._get_latest_scan_time()}")

    def _get_latest_scan_time(self) -> str:
        """获取最近一次扫描时间，格式 YYYY-MM-DD HH:MM

        M3-Iter5：通过 ProjectService.get_last_sync_time() 访问，
        不再直接使用 ScanLogRepository（保持分层架构）。
        """
        try:
            from auto_pm.core.project_service import ProjectService

            svc = ProjectService(self._workspace_root, db=self._db)
            return svc.get_last_sync_time()
        except Exception as e:
            log.warning("获取扫描时间失败: %s", e)
            return "—"

    # ── 启动后自动加载 ────────────────────────────────────

    def showEvent(self, event: QShowEvent) -> None:
        """窗口首次显示时自动加载项目列表"""
        super().showEvent(event)
        if not self._auto_loaded:
            self._auto_loaded = True
            QTimer.singleShot(0, self._on_refresh)
