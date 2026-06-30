"""项目工作区

进入项目后的 Tab 导航页：概览/变更/变量表/文档/检查。
"""

from __future__ import annotations

import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from auto_pm.logging.logging import setup_logger
from auto_pm.models import ProjectInfo
from auto_pm.ui.vartable.vartable_tab import VartableTab
from auto_pm.ui.workspace.change_tab import ChangeTab
from auto_pm.ui.workspace.check_tab import CheckTab
from auto_pm.ui.workspace.doc_tab import DocTab
from auto_pm.ui.workspace.overview_tab import OverviewTab

# 项目工作区 Tab 标识 → 中文标签
WORKSPACE_TAB_LABELS: dict[str, str] = {
    "overview": "概览",
    "change": "变更",
    "vartable": "变量表",
    "doc": "文档",
    "check": "检查",
}

# 项目工作区 Tab 默认顺序
WORKSPACE_TAB_ORDER: list[str] = [
    "overview",
    "change",
    "vartable",
    "doc",
    "check",
]

# 项目工作区 Tab → 计划交付版本（占位提示）
WORKSPACE_TAB_VERSION: dict[str, str] = {
    "overview": "V2.0",
    "change": "V2.1",
    "vartable": "V2.3",  # V2.3 Week4: 变量编辑器 + 项目工作区变量表 Tab
    "doc": "V2.0",
    "check": "V2.0",
}

log = setup_logger(log_level="INFO", app_name="auto_pm")

# 技术栈 → (标签文案, 背景色, 前景色)
_STACK_BADGE: dict[str, tuple[str, str, str]] = {
    "plc": ("PLC", "#4a90d9", "#ffffff"),  # 蓝色
    "python": ("Python", "#27ae60", "#ffffff"),  # 绿色
    "unknown": ("未分类", "#95a5a6", "#ffffff"),  # 灰色
}

# 项目阶段 → 标签文案
_PHASE_LABEL: dict[str, str] = {
    "developing": "开发中",
    "commissioning": "调试中",
    "production": "生产中",
    "archived": "已归档",
    "": "未设置",
}

_HEADER_STYLE = """
QFrame#workspaceHeader {
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
}
QLabel#headerTitle { font-size: 16px; font-weight: bold; color: #222; }
QLabel#headerId { font-size: 12px; color: #888; }
QPushButton#headerBtn {
    padding: 4px 12px;
    border: 1px solid #ccc;
    border-radius: 4px;
    background: #f5f5f5;
    font-size: 12px;
}
QPushButton#headerBtn:hover { background: #e8e8e8; }
QPushButton#deleteBtn {
    padding: 4px 12px;
    border: 1px solid #e74c3c;
    border-radius: 4px;
    background: #fff5f5;
    color: #e74c3c;
    font-size: 12px;
}
QPushButton#deleteBtn:hover { background: #ffe0e0; }
"""


class ProjectWorkspaceView(QWidget):
    """项目工作区

    顶部显示当前项目信息与返回按钮，下方为 Tab 导航。
    """

    backRequested = Signal()
    editRequested = Signal(str)
    deleteRequested = Signal(str)
    change_updated = Signal()

    def __init__(
        self,
        workspace_root: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._project: ProjectInfo | None = None
        self._tab_indices: dict[str, int] = {}
        self._workspace_root = workspace_root
        self._change_tab: ChangeTab | None = None
        self._check_tab: CheckTab | None = None
        self._doc_tab: DocTab | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        layout.addWidget(self._build_header())

        # Tab 区
        self._tab_widget = QTabWidget()
        self._overview_tab = OverviewTab()
        self._change_tab = self._build_change_tab()
        self._check_tab = CheckTab()
        self._doc_tab = self._build_doc_tab()
        self._vartable_tab = self._build_vartable_tab()
        for tab_id in WORKSPACE_TAB_ORDER:
            if tab_id == "overview":
                page: QWidget = self._overview_tab
            elif tab_id == "change":
                page = (
                    self._change_tab
                    if self._change_tab is not None
                    else self._make_placeholder(tab_id)
                )
            elif tab_id == "check":
                page = self._check_tab
            elif tab_id == "doc":
                page = (
                    self._doc_tab if self._doc_tab is not None else self._make_placeholder(tab_id)
                )
            elif tab_id == "vartable":
                page = (
                    self._vartable_tab
                    if self._vartable_tab is not None
                    else self._make_placeholder(tab_id)
                )
            else:
                page = self._make_placeholder(tab_id)
            idx = self._tab_widget.addTab(page, WORKSPACE_TAB_LABELS[tab_id])
            self._tab_indices[tab_id] = idx
        layout.addWidget(self._tab_widget, 1)

    def _build_change_tab(self) -> ChangeTab | None:
        """构建变更 Tab（需要 workspace_root 才能创建 Service）"""
        if not self._workspace_root:
            log.debug("workspace_root 未设置，变更 Tab 暂用占位")
            return None
        try:
            from auto_pm.change.change_service import ChangeService
            from auto_pm.core.project_service import ProjectService

            change_service = ChangeService(self._workspace_root)
            project_service = ProjectService(self._workspace_root)
            tab = ChangeTab(change_service, project_service, self)
            tab.change_updated.connect(self.change_updated.emit)
            return tab
        except Exception as e:
            log.warning("变更 Tab 初始化失败，使用占位: %s", e)
            return None

    def _build_doc_tab(self) -> DocTab | None:
        """构建文档 Tab（需要 workspace_root 才能创建 TemplateService）"""
        if not self._workspace_root:
            log.debug("workspace_root 未设置，文档 Tab 暂用占位")
            return None
        try:
            from auto_pm.core.template_service import TemplateService

            templates_dir = self._resolve_templates_dir()
            template_service = TemplateService(templates_dir)
            tab = DocTab(template_service, self)
            return tab
        except Exception as e:
            log.warning("文档 Tab 初始化失败，使用占位: %s", e)
            return None

    def _build_vartable_tab(self) -> VartableTab | None:
        """构建变量表 Tab（V2.3 Week4）

        VartableTab 不依赖 workspace_root，但需要项目路径才能加载变量表。
        项目路径在 set_project() 时通过 set_project_path() 传入。
        """
        try:
            tab = VartableTab(parent=self)
            # 如果已有项目路径，立即加载
            if self._project and self._project.path:
                tab.set_project_path(self._project.path)
            return tab
        except Exception as e:
            log.warning("变量表 Tab 初始化失败，使用占位: %s", e)
            return None

    @staticmethod
    def _resolve_templates_dir() -> str:
        """推断模板目录（auto_pm 包的上级目录下的 templates/）"""
        import auto_pm

        package_dir = os.path.dirname(os.path.abspath(auto_pm.__file__))
        project_root = os.path.dirname(package_dir)
        return os.path.join(project_root, "templates")

    def _build_header(self) -> QFrame:
        """构建工作区头部：返回按钮 + 项目名称/编号 + 徽标 + 编辑/删除按钮"""
        header = QFrame()
        header.setObjectName("workspaceHeader")
        header.setStyleSheet(_HEADER_STYLE)
        h = QHBoxLayout(header)
        h.setContentsMargins(14, 10, 14, 10)
        h.setSpacing(10)

        self._back_btn = QPushButton("← 返回列表")
        self._back_btn.setObjectName("headerBtn")
        self._back_btn.clicked.connect(self.backRequested.emit)
        h.addWidget(self._back_btn)

        # 中间：项目名称 + 编号
        center = QVBoxLayout()
        center.setSpacing(2)
        self._title_label = QLabel("未选择项目")
        self._title_label.setObjectName("headerTitle")
        center.addWidget(self._title_label)
        self._id_label = QLabel("")
        self._id_label.setObjectName("headerId")
        center.addWidget(self._id_label)
        h.addLayout(center, 1)

        # 右侧：技术栈徽标 + 阶段徽标 + 编辑/删除按钮
        self._stack_badge = QLabel("")
        h.addWidget(self._stack_badge)

        self._phase_badge = QLabel("")
        h.addWidget(self._phase_badge)

        self._edit_btn = QPushButton("编辑")
        self._edit_btn.setObjectName("headerBtn")
        self._edit_btn.clicked.connect(self._on_edit_clicked)
        h.addWidget(self._edit_btn)

        self._delete_btn = QPushButton("删除")
        self._delete_btn.setObjectName("deleteBtn")
        self._delete_btn.clicked.connect(self._on_delete_clicked)
        h.addWidget(self._delete_btn)

        return header

    def _make_stack_badge(self, stack: str) -> None:
        """设置技术栈徽标"""
        text, bg, fg = _STACK_BADGE.get(stack, _STACK_BADGE["unknown"])
        self._stack_badge.setText(text)
        self._stack_badge.setStyleSheet(
            f"background: {bg}; color: {fg}; "
            "font-size: 10px; font-weight: bold; "
            "padding: 2px 6px; border-radius: 3px;"
        )

    def _make_phase_badge(self, phase: str) -> None:
        """设置阶段徽标"""
        text = _PHASE_LABEL.get(phase, phase or "未设置")
        self._phase_badge.setText(text)
        self._phase_badge.setStyleSheet(
            "font-size: 10px; color: #555; "
            "padding: 2px 6px; border: 1px solid #ccc; "
            "border-radius: 3px; background: #f5f5f5;"
        )

    def _make_placeholder(self, tab_id: str) -> QWidget:
        page = QWidget()
        v = QVBoxLayout(page)
        v.setContentsMargins(20, 20, 20, 20)
        version = WORKSPACE_TAB_VERSION.get(tab_id, "后续版本")
        label = QLabel(f"{WORKSPACE_TAB_LABELS[tab_id]} 功能将在 {version} 交付")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #999; font-size: 14px;")
        v.addWidget(label)
        v.addStretch(1)
        return page

    def _on_edit_clicked(self) -> None:
        if self._project is not None:
            self.editRequested.emit(self._project.project_id)

    def _on_delete_clicked(self) -> None:
        if self._project is not None:
            self.deleteRequested.emit(self._project.project_id)

    def load_project(self, project: ProjectInfo) -> None:
        """加载项目到工作区"""
        self._project = project
        self._title_label.setText(project.name or project.project_id)
        self._id_label.setText(project.project_id)
        self._make_stack_badge(project.stack)
        self._make_phase_badge(project.phase)
        self._overview_tab.load_project(project)
        if self._change_tab is not None:
            self._change_tab.load_project(project.project_id)
        if self._check_tab is not None:
            self._check_tab.load_project(project.project_id, project.path)
        if self._doc_tab is not None:
            self._doc_tab.load_project(project.project_id, project.path)
        # V2.3 Week4: 变量表 Tab 加载项目路径
        if self._vartable_tab is not None:
            self._vartable_tab.set_project_path(project.path)
        log.info("工作区加载项目: %s", project.project_id)
