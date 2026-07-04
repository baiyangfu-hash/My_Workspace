"""项目列表页

重构版：支持 4 种分组模式 + 卡片/列表双视图。

布局：顶部 ViewControls（视图切换/排序/分组）+ 下方内容区
（卡片视图=QScrollArea 含分组；列表视图=ProjectTableView）。

支持加载中/空/错误状态，响应式卡片网格布局。
点击卡片或表格行发射 projectSelected(project_id)。
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from auto_pm.logging.logging import setup_logger
from auto_pm.models import ProjectInfo
from auto_pm.models.dto import DashboardSummaryDTO, ProjectCardDTO
from auto_pm.models.project import extract_business_line
from auto_pm.ui.project_list.group_header import GroupHeader
from auto_pm.ui.project_list.project_card import ProjectCard
from auto_pm.ui.project_list.table_view import ProjectTableView
from auto_pm.ui.project_list.view_controls import (
    GROUP_NONE,
    SORT_ID_ASC,
    VIEW_MODE_CARD,
    ViewControls,
)

log = setup_logger(log_level="INFO", app_name="auto_pm")

# 卡片网格参数
_CARD_MIN_WIDTH = 280
_CARD_SPACING = 10

# 中文映射
_STACK_CN: dict[str, str] = {
    "plc": "PLC 总库",
    "python": "Python 总库",
    "unknown": "未分类",
}
_PHASE_CN: dict[str, str] = {
    "developing": "开发中",
    "commissioning": "调试中",
    "production": "生产中",
    "archived": "已归档",
    "": "未设置",
}
_BL_CN: dict[str, str] = {
    "DJ": "单机 (DJ)",
    "SW": "软件 (SW)",
    "ZD": "整线 (ZD)",
    "XT": "升级 (XT)",
    "WX": "维保 (WX)",
    "": "未设置",
}

# 分组排序优先级
_STACK_ORDER: dict[str, int] = {"plc": 0, "python": 1, "unknown": 2}
_PHASE_ORDER: dict[str, int] = {
    "developing": 0,
    "commissioning": 1,
    "production": 2,
    "archived": 3,
    "": 4,
}
_BL_ORDER: dict[str, int] = {"DJ": 0, "SW": 1, "ZD": 2, "XT": 3, "WX": 4, "": 5}


class _DashboardBanner(QWidget):
    """首页驾驶舱摘要横幅"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()
        self.setVisible(False)

    def _build_ui(self) -> None:
        self.setObjectName("dashboardBanner")
        self.setStyleSheet(
            """
QWidget#dashboardBanner {
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
}
QLabel#dashboardTitle {
    font-size: 14px;
    font-weight: bold;
    color: #222;
}
QLabel#dashboardMetric {
    font-size: 13px;
    font-weight: bold;
    color: #1f2d3d;
}
QLabel#dashboardHint {
    font-size: 12px;
    color: #666;
}
QLabel#dashboardSection {
    font-size: 12px;
    font-weight: bold;
    color: #333;
    margin-top: 4px;
}
"""
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        title = QLabel("项目驾驶舱")
        title.setObjectName("dashboardTitle")
        title.setWordWrap(True)
        layout.addWidget(title)

        self._total_label = QLabel("项目总数: 0")
        self._total_label.setObjectName("dashboardMetric")
        self._total_label.setWordWrap(True)
        layout.addWidget(self._total_label)

        self._phase_label = QLabel("阶段分布: 开发中 0 / 调试中 0 / 生产中 0 / 已归档 0")
        self._phase_label.setObjectName("dashboardHint")
        self._phase_label.setWordWrap(True)
        layout.addWidget(self._phase_label)

        self._change_label = QLabel("未关闭变更: 0")
        self._change_label.setObjectName("dashboardMetric")
        self._change_label.setWordWrap(True)
        layout.addWidget(self._change_label)

        self._check_label = QLabel("检查失败项目: 0")
        self._check_label.setObjectName("dashboardMetric")
        self._check_label.setWordWrap(True)
        layout.addWidget(self._check_label)

        # V0.4.1 Step 3: PLC 检查不适用项目数（Python 项目）
        self._not_applicable_label = QLabel("检查不适用: 0")
        self._not_applicable_label.setObjectName("dashboardHint")
        self._not_applicable_label.setWordWrap(True)
        layout.addWidget(self._not_applicable_label)

        recent_title = QLabel("最近活动")
        recent_title.setObjectName("dashboardSection")
        layout.addWidget(recent_title)

        self._recent_label = QLabel("暂无最近活动")
        self._recent_label.setObjectName("dashboardHint")
        self._recent_label.setWordWrap(True)
        layout.addWidget(self._recent_label)

        risk_title = QLabel("风险提示")
        risk_title.setObjectName("dashboardSection")
        layout.addWidget(risk_title)

        self._risk_label = QLabel("当前未发现高优先级风险")
        self._risk_label.setObjectName("dashboardHint")
        self._risk_label.setWordWrap(True)
        layout.addWidget(self._risk_label)

    def set_summary(self, summary: DashboardSummaryDTO) -> None:
        """更新横幅内容"""
        phases = summary.phase_counts
        self._total_label.setText(f"项目总数: {summary.total_projects}")
        self._phase_label.setText(
            "阶段分布: "
            f"开发中 {phases.get('developing', 0)} / "
            f"调试中 {phases.get('commissioning', 0)} / "
            f"生产中 {phases.get('production', 0)} / "
            f"已归档 {phases.get('archived', 0)}"
        )
        self._change_label.setText(f"未关闭变更: {summary.open_change_count}")
        self._check_label.setText(f"检查失败项目: {summary.failed_check_project_count}")
        if summary.failed_check_project_ids:
            self._check_label.setToolTip("失败项目: " + ", ".join(summary.failed_check_project_ids))
        else:
            self._check_label.setToolTip("")
        # V0.4.1 Step 3: 检查不适用项目（Python 项目）
        self._not_applicable_label.setText(
            f"检查不适用: {summary.not_applicable_project_count}（Python 项目）"
        )
        if summary.not_applicable_project_ids:
            self._not_applicable_label.setToolTip(
                "不适用项目: " + ", ".join(summary.not_applicable_project_ids)
            )
        else:
            self._not_applicable_label.setToolTip("")
        self._recent_label.setText("\n".join(summary.recent_activities) or "暂无最近活动")
        self._risk_label.setText("\n".join(summary.risk_hints) or "当前未发现高优先级风险")
        self.setVisible(True)


class ProjectListView(QWidget):
    """项目列表页

    展示项目卡片网格或列表表格，支持按技术栈/阶段/业务线/关键字筛选，
    支持 4 种分组模式 + 卡片/列表双视图。

    点击项目卡片或表格行发射 projectSelected(project_id)。
    右键卡片菜单编辑/删除发射 projectEditRequested/projectDeleteRequested。

    保留原公共接口以兼容 main_window.py：
    - 信号 projectSelected / projectEditRequested / projectDeleteRequested
    - 方法 set_projects / get_project / set_search_text / set_business_line
      / set_loading / set_error
    新增方法 set_filter(stack, phase) 响应 NavigationTree 信号。
    """

    projectSelected = Signal(str)
    projectEditRequested = Signal(str)
    projectDeleteRequested = Signal(str)
    # V0.5.3 Fix 4: 空状态"新建项目"按钮触发的信号
    newProjectRequested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        # 数据
        self._all_projects: list[ProjectInfo] = []
        self._filtered_projects: list[ProjectInfo] = []
        self._change_counts: dict[str, int] = {}
        # 筛选
        self._search_text = ""
        self._filter_stack = "all"
        self._filter_phase = "all"
        self._filter_bl = "all"
        # 视图状态
        self._view_mode = VIEW_MODE_CARD
        self._sort_mode = SORT_ID_ASC
        self._group_mode = "stack_bl"
        self._state = "empty"
        # 分组折叠状态（记录被折叠的组 key）
        self._collapsed_groups: set[str] = set()
        self._build_ui()

    # ── UI 构建 ────────────────────────────────────────────

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        self._dashboard_banner = _DashboardBanner()
        layout.addWidget(self._dashboard_banner)

        # 视图控制栏
        self._view_controls = ViewControls()
        self._view_controls.view_mode_changed.connect(self._on_view_mode_changed)
        self._view_controls.sort_changed.connect(self._on_sort_changed)
        self._view_controls.group_mode_changed.connect(self._on_group_mode_changed)
        layout.addWidget(self._view_controls)

        # 状态标签（空/错误）
        self._status_label = QLabel()
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_label.setStyleSheet("color: #999; font-size: 13px; padding: 40px;")
        layout.addWidget(self._status_label)

        # V0.5.3 Fix 4: 空状态"新建项目"主操作按钮
        # 当项目列表为空时，显示醒目的 CTA 引导用户创建第一个项目
        self._empty_new_btn = QPushButton("➕ 新建项目")
        self._empty_new_btn.setToolTip("点击新建 PLC 项目 / Python 项目")
        self._empty_new_btn.setStyleSheet(
            "QPushButton { background: #4a90d9; color: white; "
            "font-size: 14px; font-weight: bold; padding: 10px 24px; "
            "border-radius: 4px; min-width: 160px; }"
            "QPushButton:hover { background: #357abd; }"
        )
        self._empty_new_btn.setVisible(False)
        self._empty_new_btn.clicked.connect(self.newProjectRequested.emit)
        empty_btn_layout = QHBoxLayout()
        empty_btn_layout.addStretch()
        empty_btn_layout.addWidget(self._empty_new_btn)
        empty_btn_layout.addStretch()
        layout.addLayout(empty_btn_layout)

        # 加载进度
        self._progress = QProgressBar()
        self._progress.setRange(0, 0)
        self._progress.setTextVisible(True)
        self._progress.setFormat("正在扫描项目...")
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        # 内容区：卡片视图（QScrollArea）与列表视图（QTableWidget）切换
        self._content_stack = QStackedWidget()

        # 页 0：卡片滚动区
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._content_container = QWidget()
        self._content_layout = QVBoxLayout(self._content_container)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(8)
        self._content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._scroll.setWidget(self._content_container)
        self._content_stack.addWidget(self._scroll)  # index 0 = 卡片

        # 页 1：列表表格
        self._table_view = ProjectTableView()
        self._table_view.project_clicked.connect(self.projectSelected.emit)
        self._content_stack.addWidget(self._table_view)  # index 1 = 列表

        self._content_stack.setCurrentIndex(0)
        layout.addWidget(self._content_stack, 1)

        self._set_state("empty", "暂无项目，点击「刷新列表」加载项目。")

    # ── 状态管理 ──────────────────────────────────────────

    def _set_state(self, state: str, message: str = "") -> None:
        self._state = state
        if state == "loading":
            self._progress.setVisible(True)
            self._status_label.setVisible(False)
            self._content_stack.setVisible(False)
            self._empty_new_btn.setVisible(False)
        elif state == "error":
            self._progress.setVisible(False)
            self._status_label.setText(message or "加载失败")
            self._status_label.setStyleSheet("color: #e74c3c; font-size: 13px; padding: 40px;")
            self._status_label.setVisible(True)
            self._content_stack.setVisible(False)
            self._empty_new_btn.setVisible(False)
        elif state == "empty":
            self._progress.setVisible(False)
            self._status_label.setText(message or "暂无项目")
            self._status_label.setStyleSheet("color: #999; font-size: 13px; padding: 40px;")
            self._status_label.setVisible(True)
            self._content_stack.setVisible(False)
            # V0.5.3 Fix 4: 空状态显示"新建项目"主操作按钮（仅当无筛选时显示）
            show_new_btn = (
                self._filter_stack == "all"
                and self._filter_phase == "all"
                and self._filter_bl == "all"
                and not self._search_text
            )
            self._empty_new_btn.setVisible(show_new_btn)
        else:  # ready
            self._progress.setVisible(False)
            self._status_label.setVisible(False)
            self._content_stack.setVisible(True)
            self._empty_new_btn.setVisible(False)

    def set_loading(self, message: str = "正在扫描项目...") -> None:
        """进入加载中状态"""
        self._progress.setFormat(message)
        self._set_state("loading")

    def set_error(self, message: str) -> None:
        """进入错误状态"""
        self._set_state("error", message)

    # ── 数据加载 ──────────────────────────────────────────

    def set_projects(self, projects: list[ProjectInfo] | list[ProjectCardDTO]) -> None:
        """设置项目列表数据并刷新

        接收 list[ProjectInfo] 或 list[ProjectCardDTO]，内部统一归一化为 ProjectInfo。
        """
        self._all_projects = []
        self._change_counts = {}
        for proj in projects:
            if isinstance(proj, ProjectCardDTO):
                self._change_counts[proj.project_id] = proj.change_count
                self._all_projects.append(self._dto_to_info(proj))
            else:
                self._all_projects.append(proj)
        self._refresh()

    def set_dashboard_summary(self, summary: DashboardSummaryDTO) -> None:
        """设置首页驾驶舱摘要"""
        self._dashboard_banner.set_summary(summary)

    def get_project(self, project_id: str) -> ProjectInfo | None:
        """按 project_id 查询项目（供主窗口进入工作区用）"""
        for proj in self._all_projects:
            if proj.project_id == project_id:
                return proj
        return None

    @staticmethod
    def _dto_to_info(dto: ProjectCardDTO) -> ProjectInfo:
        """将 ProjectCardDTO 转换为 ProjectInfo（保留展示所需字段）"""
        return ProjectInfo(
            project_id=dto.project_id,
            name=dto.name,
            path=dto.path,
            stack=dto.stack,
            version=dto.version,
            phase=dto.phase,
            business_line=dto.business_line,
            file_mtime=dto.file_mtime,
            description=dto.description,
        )

    # ── 筛选 ──────────────────────────────────────────────

    def set_search_text(self, text: str) -> None:
        """设置关键字搜索（来自顶部工具栏）"""
        self._search_text = text.strip().lower()
        self._refresh()

    def set_business_line(self, line: str) -> None:
        """联动设置业务线筛选（来自顶部工具栏）"""
        self._filter_bl = line if line and line != "all" else "all"
        self._refresh()

    def set_filter(self, stack: str, phase: str) -> None:
        """响应 NavigationTree 信号筛选

        V0.5.3 Fix 1: phase 语义
        - 'all' 或 '' → 不筛选阶段（显示所有阶段），'' 为历史兼容别名
        - 'unset' → 仅显示未设置阶段的项目（phase 字段为空）
        - 'developing'/'commissioning'/'production'/'archived' → 按对应阶段筛选

        Args:
            stack: 技术栈，'all' 或 '' 表示不筛选
            phase: 阶段，'all' 或 '' 表示不筛选，'unset' 表示仅未设置
        """
        self._filter_stack = stack if stack and stack != "all" else "all"
        # V0.5.3: '' 保留为 "不筛选阶段"（历史兼容），'unset' 表示"仅未设置阶段"
        self._filter_phase = phase if phase else "all"
        self._refresh()

    def _refresh(self) -> None:
        """重新筛选 → 排序 → 渲染，并更新状态"""
        self._filtered_projects = self._filter_projects()
        self._sort_projects()
        if not self._all_projects:
            self._set_state("empty", "暂无项目，点击「刷新列表」加载项目。")
        elif not self._filtered_projects:
            self._set_state("empty", "无匹配项目，请调整筛选条件。")
        else:
            self._set_state("ready")
            self._render()

    def _filter_projects(self) -> list[ProjectInfo]:
        result: list[ProjectInfo] = []
        for proj in self._all_projects:
            if self._filter_stack != "all" and proj.stack != self._filter_stack:
                continue
            # V0.5.3: 'unset' 表示仅显示未设置阶段（phase 为空）的项目
            if self._filter_phase == "unset":
                if proj.phase:
                    continue
            elif self._filter_phase != "all" and proj.phase != self._filter_phase:
                continue
            if self._filter_bl != "all":
                bl = proj.business_line or extract_business_line(proj.project_id)
                if bl != self._filter_bl:
                    continue
            if self._search_text:
                haystack = f"{proj.project_id} {proj.name} {proj.description}".lower()
                if self._search_text not in haystack:
                    continue
            result.append(proj)
        return result

    def _sort_projects(self) -> None:
        """按当前排序模式对 _filtered_projects 原地排序"""
        if self._sort_mode == "id_asc":
            self._filtered_projects.sort(key=lambda p: p.project_id)
        elif self._sort_mode == "id_desc":
            self._filtered_projects.sort(key=lambda p: p.project_id, reverse=True)
        elif self._sort_mode == "phase":
            self._filtered_projects.sort(key=lambda p: (_PHASE_ORDER.get(p.phase, 9), p.project_id))
        elif self._sort_mode == "mtime":
            self._filtered_projects.sort(
                key=lambda p: (p.file_mtime or 0.0, p.project_id), reverse=True
            )

    # ── 渲染 ──────────────────────────────────────────────

    def _render(self) -> None:
        if self._view_mode == "list":
            self._render_table_view()
        else:
            self._render_card_view()

    def _render_card_view(self) -> None:
        """渲染卡片网格（按分组）"""
        self._clear_content()
        groups = self._apply_grouping()
        cols = self._calc_columns()
        for group_key, group_name, group_projects in groups:
            expanded = group_key not in self._collapsed_groups
            header = GroupHeader(group_name, len(group_projects), expanded=expanded)
            header.setProperty("group_key", group_key)
            header.toggled.connect(self._make_toggle_handler(group_key))

            cards_widget = QWidget()
            grid = QGridLayout(cards_widget)
            grid.setContentsMargins(0, 0, 0, 0)
            grid.setSpacing(_CARD_SPACING)
            grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            for idx, proj in enumerate(group_projects):
                card = ProjectCard(proj, change_count=self._change_counts.get(proj.project_id, 0))
                card.clicked.connect(self.projectSelected.emit)
                card.editRequested.connect(self.projectEditRequested.emit)
                card.deleteRequested.connect(self.projectDeleteRequested.emit)
                grid.addWidget(card, idx // cols, idx % cols)
            cards_widget.setVisible(expanded)

            self._content_layout.addWidget(header)
            self._content_layout.addWidget(cards_widget)

        self._content_stack.setCurrentIndex(0)

    def _render_table_view(self) -> None:
        """渲染列表表格"""
        self._table_view.set_projects(self._filtered_projects, self._change_counts)
        self._content_stack.setCurrentIndex(1)

    def _make_toggle_handler(self, group_key: str) -> Callable[[bool], None]:
        """创建分组折叠/展开回调（避免循环闭包捕获问题）"""

        def handler(expanded: bool) -> None:
            if expanded:
                self._collapsed_groups.discard(group_key)
            else:
                self._collapsed_groups.add(group_key)
            # 找到对应的卡片容器并切换可见性
            self._toggle_group_widgets(group_key, expanded)

        return handler

    def _toggle_group_widgets(self, group_key: str, expanded: bool) -> None:
        """切换指定分组的卡片容器可见性"""
        # content_layout 交替存放 header / cards_widget
        for i in range(self._content_layout.count()):
            item = self._content_layout.itemAt(i)
            widget = item.widget() if item is not None else None
            if isinstance(widget, GroupHeader) and widget.property("group_key") == group_key:
                # 下一个 widget 即为该分组的卡片容器
                next_item = self._content_layout.itemAt(i + 1)
                cards_widget = next_item.widget() if next_item is not None else None
                if cards_widget is not None:
                    cards_widget.setVisible(expanded)
                return

    # ── 分组 ──────────────────────────────────────────────

    def _apply_grouping(self) -> list[tuple[str, str, list[ProjectInfo]]]:
        """按 group_mode 分组，返回 [(group_key, group_name, projects), ...]

        分组顺序按预定义优先级稳定排序。
        """
        if self._group_mode == GROUP_NONE:
            return [("", "全部项目", list(self._filtered_projects))]

        groups: dict[str, dict[str, Any]] = {}
        for proj in self._filtered_projects:
            key, name, priority = self._project_group(proj, self._group_mode)
            if key not in groups:
                groups[key] = {"name": name, "priority": priority, "projects": []}
            groups[key]["projects"].append(proj)

        sorted_keys = sorted(
            groups.keys(),
            key=lambda k: (groups[k]["priority"], groups[k]["name"]),
        )
        return [(k, groups[k]["name"], groups[k]["projects"]) for k in sorted_keys]

    @staticmethod
    def _project_group(proj: ProjectInfo, mode: str) -> tuple[str, str, tuple[int, ...]]:
        """返回 (group_key, group_display_name, sort_priority)"""
        stack = proj.stack
        phase = proj.phase or ""
        bl = proj.business_line or extract_business_line(proj.project_id)
        stack_cn = _STACK_CN.get(stack, "未分类")
        phase_cn = _PHASE_CN.get(phase, "未设置")
        bl_cn = _BL_CN.get(bl, bl or "未设置")

        if mode == "stack_bl":
            return (
                f"{stack}|{bl}",
                f"{stack_cn} · {bl_cn}",
                (_STACK_ORDER.get(stack, 9), _BL_ORDER.get(bl, 9)),
            )
        if mode == "stack_phase":
            return (
                f"{stack}|{phase}",
                f"{stack_cn} · {phase_cn}",
                (_STACK_ORDER.get(stack, 9), _PHASE_ORDER.get(phase, 9)),
            )
        if mode == "bl":
            return (bl or "_none", bl_cn, (_BL_ORDER.get(bl, 9),))
        if mode == "phase":
            return (phase or "_none", phase_cn, (_PHASE_ORDER.get(phase, 9),))
        return ("", "全部项目", (0,))

    # ── 控件事件 ──────────────────────────────────────────

    def _on_view_mode_changed(self, mode: str) -> None:
        self._view_mode = mode
        if self._state == "ready":
            self._render()

    def _on_sort_changed(self, mode: str) -> None:
        self._sort_mode = mode
        if self._state == "ready":
            self._sort_projects()
            self._render()

    def _on_group_mode_changed(self, mode: str) -> None:
        self._group_mode = mode
        if self._state == "ready":
            self._render()

    # ── 辅助 ──────────────────────────────────────────────

    def _calc_columns(self) -> int:
        """根据滚动区视口宽度计算网格列数（响应式）"""
        width = self._scroll.viewport().width()
        if width <= 0:
            return 3
        cols = max(1, width // (_CARD_MIN_WIDTH + _CARD_SPACING))
        return min(cols, 6)

    def _clear_content(self) -> None:
        """清空卡片内容容器"""
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            widget = item.widget() if item is not None else None
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def resizeEvent(self, event: QResizeEvent) -> None:
        """窗口大小变化时重新计算卡片网格列数"""
        super().resizeEvent(event)
        if self._state == "ready" and self._view_mode != "list" and self._filtered_projects:
            self._render_card_view()
