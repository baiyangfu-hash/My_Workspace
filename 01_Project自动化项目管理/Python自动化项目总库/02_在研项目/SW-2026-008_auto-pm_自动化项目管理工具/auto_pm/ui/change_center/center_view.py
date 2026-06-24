"""变更中心全局页

左右分栏布局（QSplitter）：
    左侧：ChangeListPanel（宽度 350px）- 变更单列表 + 状态 Tab 筛选
    右侧：ChangeDetailPanel - 变更单详情 + 状态流转按钮

顶部：标题"变更中心" + "创建变更单"按钮（弹出 CreateChangeDialog）。

信号流向：
    ChangeListPanel.change_selected → ChangeCenterView._on_change_selected
        → ChangeDetailPanel.load_change
    ChangeDetailPanel.transition_completed → ChangeCenterView._on_transition_completed
        → ChangeListPanel.refresh + 发射 change_updated()
    CreateChangeDialog.change_created → ChangeCenterView._on_change_created
        → ChangeListPanel.refresh + 发射 change_updated()
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from auto_pm.change.change_service import ChangeService
from auto_pm.core.project_service import ProjectService
from auto_pm.logging.logging import setup_logger
from auto_pm.ui.change_center.change_detail_panel import ChangeDetailPanel
from auto_pm.ui.change_center.change_list_panel import ChangeListPanel
from auto_pm.ui.dialogs.create_change_dialog import CreateChangeDialog

log = setup_logger(log_level="INFO", app_name="auto_pm")

__all__ = ["ChangeCenterView"]

_VIEW_STYLE = """
QWidget#changeCenterView { background: #fafafa; }
QLabel#centerTitle { font-size: 18px; font-weight: bold; color: #222; }
QPushButton#createChangeBtn {
    font-size: 13px; color: #ffffff;
    background: #4a90d9; border: none;
    border-radius: 4px; padding: 6px 16px;
}
QPushButton#createChangeBtn:hover { background: #357abd; }
QPushButton#createChangeBtn:disabled { background: #b0c4de; }
"""

# 左侧列表面板默认宽度
_LIST_PANEL_WIDTH = 350


class ChangeCenterView(QWidget):
    """变更中心全局页

    左右分栏：左侧变更单列表，右侧变更单详情。
    顶部标题栏含"创建变更单"按钮。变更有变动时发射 change_updated() 信号。
    """

    change_updated = Signal()

    def __init__(
        self,
        change_service: ChangeService,
        project_service: ProjectService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._change_service = change_service
        self._project_service = project_service
        self._build_ui()
        self._connect_signals()

    # ── UI 构建 ────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.setObjectName("changeCenterView")
        self.setStyleSheet(_VIEW_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 顶部标题栏
        header = self._build_header()
        layout.addWidget(header)

        # 左右分栏
        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._list_panel = ChangeListPanel(self._change_service, self._splitter)
        self._detail_panel = ChangeDetailPanel(self._change_service, self._splitter)
        self._splitter.addWidget(self._list_panel)
        self._splitter.addWidget(self._detail_panel)
        self._splitter.setStretchFactor(0, 0)
        self._splitter.setStretchFactor(1, 1)
        self._splitter.setSizes([_LIST_PANEL_WIDTH, self.width() - _LIST_PANEL_WIDTH])
        layout.addWidget(self._splitter, 1)

    def _build_header(self) -> QWidget:
        """构建顶部标题栏（标题 + 创建按钮）"""
        header = QWidget()
        header.setStyleSheet(
            "QWidget { background: #ffffff; border-bottom: 1px solid #e0e0e0; }"
        )
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(16, 10, 16, 10)
        h_layout.setSpacing(8)

        title = QLabel("变更中心")
        title.setObjectName("centerTitle")
        h_layout.addWidget(title)
        h_layout.addStretch(1)

        self._create_btn = QPushButton("创建变更单")
        self._create_btn.setObjectName("createChangeBtn")
        self._create_btn.clicked.connect(self._on_create_change_clicked)
        h_layout.addWidget(self._create_btn)
        return header

    def _connect_signals(self) -> None:
        """连接子面板信号"""
        self._list_panel.change_selected.connect(self._on_change_selected)
        self._detail_panel.transition_completed.connect(self._on_transition_completed)
        self._detail_panel.change_updated.connect(self._on_change_updated)

    # ── 公共方法 ─────────────────────────────────────────

    def refresh(self) -> None:
        """刷新变更单列表"""
        log.info("变更中心刷新列表")
        self._list_panel.refresh()

    # ── 信号处理 ─────────────────────────────────────────

    def _on_change_selected(self, change_number: str) -> None:
        """左侧选中变更单 → 右侧加载详情"""
        log.debug("变更中心: 选中 %s，加载详情", change_number)
        self._detail_panel.load_change(change_number)

    def _on_transition_completed(self, change_number: str) -> None:
        """状态流转完成 → 刷新列表 + 发射 change_updated()"""
        log.info("变更中心: 流转完成 %s，刷新列表", change_number)
        self._list_panel.refresh()
        # 流转后重新选中该变更单（若仍在列表中）
        self._list_panel.select_change(change_number)
        self.change_updated.emit()

    def _on_change_updated(self, change_number: str) -> None:
        """变更单编辑完成 → 刷新列表 + 发射 change_updated()"""
        log.info("变更中心: 变更单已修改 %s，刷新列表", change_number)
        self._list_panel.refresh()
        self._list_panel.select_change(change_number)
        self.change_updated.emit()

    def _on_create_change_clicked(self) -> None:
        """创建变更单按钮 → 弹出 CreateChangeDialog"""
        log.info("变更中心: 打开创建变更单对话框")
        dialog = CreateChangeDialog(
            project_service=self._project_service,
            change_service=self._change_service,
            parent=self,
        )
        dialog.change_created.connect(self._on_change_created)
        dialog.exec()

    def _on_change_created(self, project_id: str) -> None:
        """变更单创建成功 → 刷新列表 + 发射 change_updated()"""
        log.info("变更中心: 变更单已创建（项目 %s），刷新列表", project_id)
        self._list_panel.refresh()
        self.change_updated.emit()
