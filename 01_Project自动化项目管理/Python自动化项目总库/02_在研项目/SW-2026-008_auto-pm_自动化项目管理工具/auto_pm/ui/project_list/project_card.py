"""项目卡片组件

展示单个项目的摘要信息：编号、名称、技术栈徽标、版本、阶段、变更数、业务线、
描述摘要、最近修改时间。
点击发射 clicked(project_id)，右键菜单提供编辑/删除/打开目录/复制路径。
"""

from __future__ import annotations

import os
from datetime import datetime

from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import QAction, QContextMenuEvent, QDesktopServices, QMouseEvent
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
    QVBoxLayout,
    QWidget,
)

from auto_pm.models import ProjectCardDTO, ProjectInfo
from auto_pm.models.project import extract_business_line

__all__ = ["ProjectCard", "extract_business_line"]

# 技术栈 → (标签文案, 背景色, 前景色)
_STACK_BADGE: dict[str, tuple[str, str, str]] = {
    "plc": ("PLC", "#4a90d9", "#ffffff"),  # 蓝色
    "python": ("Python", "#27ae60", "#ffffff"),  # 绿色
    "unknown": ("未分类", "#95a5a6", "#ffffff"),  # 灰色
}

# 项目阶段 → (标签文案, 背景色, 前景色)
_PHASE_BADGE: dict[str, tuple[str, str, str]] = {
    "developing": ("开发中", "#4a90d9", "#ffffff"),  # 蓝色
    "commissioning": ("调试中", "#f39c12", "#ffffff"),  # 黄/橙色
    "production": ("生产中", "#27ae60", "#ffffff"),  # 绿色
    "archived": ("已归档", "#95a5a6", "#ffffff"),  # 灰色
}

# 项目阶段 → 标签文案（用于无徽标的回退显示）
_PHASE_LABEL: dict[str, str] = {
    "developing": "开发中",
    "commissioning": "调试中",
    "production": "生产中",
    "archived": "已归档",
    "": "未设置",
}

# 业务线 → 标签文案
_BUSINESS_LINE_LABEL: dict[str, str] = {
    "SW": "软件",
    "DJ": "单机",
    "ZD": "整线",
    "XT": "升级",
    "WX": "维保",
}

# 描述摘要最大字符数（约 2 行，超出截断加省略号）
_DESC_MAX_CHARS = 80

_CARD_STYLE = """
QFrame#ProjectCard {
    border: 1px solid #d0d0d0;
    border-radius: 8px;
    background: #ffffff;
}
QFrame#ProjectCard:hover {
    border: 1px solid #4a90d9;
    background: #f5f9ff;
}
QLabel#cardTitle { font-size: 14px; font-weight: bold; color: #222; }
QLabel#cardId { font-size: 12px; color: #666; }
QLabel#cardMeta { font-size: 11px; color: #888; }
QLabel#cardDesc { font-size: 11px; color: #555; }
QLabel#cardTag {
    font-size: 10px;
    color: #555;
    padding: 1px 5px;
    border: 1px solid #ccc;
    border-radius: 3px;
    background: #f5f5f5;
}
"""


def _format_mtime(mtime: float) -> str:
    """格式化修改时间戳为 YYYY-MM-DD；mtime<=0 或异常时返回占位符 '—'。"""
    if not mtime or mtime <= 0:
        return "—"
    try:
        return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
    except (OSError, ValueError, OverflowError):
        return "—"


def _format_change_count(count: int) -> str:
    """格式化变更数：有变更时追加 '活跃' 标记。"""
    if count > 0:
        return f"变更: {count} 活跃"
    return "变更: 0"


def _truncate_description(desc: str, max_chars: int = _DESC_MAX_CHARS) -> str:
    """截断描述摘要，超出 max_chars 时截断并追加省略号。"""
    if not desc:
        return ""
    text = desc.strip()
    # 折叠换行/多余空白为单空格，避免多行破坏卡片布局
    text = " ".join(text.split())
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "…"


class ProjectCard(QFrame):
    """项目卡片

    可点击的卡片组件，展示项目摘要。点击发射 clicked(project_id)。
    右键菜单：编辑/删除（占位，发射信号）/打开目录/复制路径。

    支持两种数据填充方式：
    - 构造函数 / set_project_info(project: ProjectInfo, change_count=0)
    - set_project(project: ProjectCardDTO)
    """

    clicked = Signal(str)
    editRequested = Signal(str)
    deleteRequested = Signal(str)

    def __init__(
        self,
        project: ProjectInfo,
        change_count: int = 0,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._project = project
        self._change_count = change_count
        self.setObjectName("ProjectCard")
        self.setStyleSheet(_CARD_STYLE)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._build_ui()
        self._apply_project_info(project, change_count)

    # ── UI 构建 ──────────────────────────────────────────

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # 第一行：技术栈徽标 + 业务线标签 + 版本（右对齐）
        top_row = QHBoxLayout()
        top_row.setSpacing(6)
        self._stack_badge = QLabel()
        top_row.addWidget(self._stack_badge)

        self._bl_label = QLabel()
        self._bl_label.setObjectName("cardTag")
        top_row.addWidget(self._bl_label)

        top_row.addStretch(1)

        self._version_label = QLabel()
        self._version_label.setObjectName("cardMeta")
        top_row.addWidget(self._version_label)
        layout.addLayout(top_row)

        # 第二行：项目名称（加粗）
        self._title_label = QLabel()
        self._title_label.setObjectName("cardTitle")
        self._title_label.setWordWrap(True)
        layout.addWidget(self._title_label)

        # 第三行：项目编号（灰色）
        self._id_label = QLabel()
        self._id_label.setObjectName("cardId")
        layout.addWidget(self._id_label)

        # 第四行：描述摘要（最多 2 行，无描述时隐藏）
        self._desc_label = QLabel()
        self._desc_label.setObjectName("cardDesc")
        self._desc_label.setWordWrap(True)
        self._desc_label.setVisible(False)
        layout.addWidget(self._desc_label)

        # 第五行：阶段徽标 + 变更数
        meta_row = QHBoxLayout()
        meta_row.setSpacing(8)
        self._phase_badge = QLabel()
        meta_row.addWidget(self._phase_badge)
        meta_row.addStretch(1)
        self._change_label = QLabel()
        self._change_label.setObjectName("cardMeta")
        meta_row.addWidget(self._change_label)
        layout.addLayout(meta_row)

        # 第六行：最近修改时间
        self._mtime_label = QLabel()
        self._mtime_label.setObjectName("cardMeta")
        layout.addWidget(self._mtime_label)

    def _make_stack_badge(self, stack: str) -> None:
        """填充技术栈徽标（彩色标签）"""
        text, bg, fg = _STACK_BADGE.get(stack, _STACK_BADGE["unknown"])
        self._stack_badge.setText(text)
        self._stack_badge.setStyleSheet(
            f"background: {bg}; color: {fg}; "
            "font-size: 10px; font-weight: bold; "
            "padding: 2px 6px; border-radius: 3px;"
        )

    def _make_phase_badge(self, phase: str) -> None:
        """填充阶段徽标（彩色标签）；未知阶段回退为普通文本。"""
        if phase in _PHASE_BADGE:
            text, bg, fg = _PHASE_BADGE[phase]
            self._phase_badge.setText(text)
            self._phase_badge.setStyleSheet(
                f"background: {bg}; color: {fg}; "
                "font-size: 10px; font-weight: bold; "
                "padding: 2px 6px; border-radius: 3px;"
            )
        else:
            # 未知/未设置阶段：回退为灰色边框标签
            text = _PHASE_LABEL.get(phase, phase or "未设置")
            self._phase_badge.setText(text)
            self._phase_badge.setStyleSheet(
                "color: #555; font-size: 10px; "
                "padding: 2px 6px; border: 1px solid #ccc; "
                "border-radius: 3px; background: #f5f5f5;"
            )

    # ── 数据填充 ──────────────────────────────────────────

    def _apply_project_info(self, project: ProjectInfo, change_count: int) -> None:
        """根据 ProjectInfo 填充卡片各字段。"""
        self._project = project
        self._change_count = change_count

        # 技术栈徽标
        self._make_stack_badge(project.stack)

        # 业务线标签（从项目编号提取）
        bl = project.business_line or extract_business_line(project.project_id)
        if bl:
            self._bl_label.setText(_BUSINESS_LINE_LABEL.get(bl, bl))
            self._bl_label.setVisible(True)
        else:
            self._bl_label.setText("")
            self._bl_label.setVisible(False)

        # 版本（右对齐）：已有 v/V 前缀原样显示，否则补 v 前缀；空则占位
        version_text = project.version or ""
        if not version_text:
            self._version_label.setText("—")
        elif version_text[:1] in ("v", "V"):
            self._version_label.setText(version_text)
        else:
            self._version_label.setText(f"v{version_text}")

        # 项目名称
        self._title_label.setText(project.name or project.project_id)

        # 项目编号
        self._id_label.setText(project.project_id)

        # 描述摘要（截断 2 行）
        desc = _truncate_description(project.description)
        if desc:
            self._desc_label.setText(desc)
            self._desc_label.setVisible(True)
        else:
            self._desc_label.setText("")
            self._desc_label.setVisible(False)

        # 阶段徽标
        self._make_phase_badge(project.phase)

        # 变更数
        self._change_label.setText(_format_change_count(change_count))

        # 修改时间
        self._mtime_label.setText(f"修改: {_format_mtime(project.file_mtime)}")

    def set_project(self, project: ProjectCardDTO) -> None:
        """接收 ProjectCardDTO 填充数据。"""
        # 复用 ProjectInfo 适配逻辑：构造临时 ProjectInfo 并填充
        info = ProjectInfo(
            project_id=project.project_id,
            name=project.name,
            path=project.path,
            stack=project.stack,
            version=project.version,
            description=project.description,
            phase=project.phase,
            business_line=project.business_line,
            file_mtime=project.file_mtime,
        )
        self._apply_project_info(info, project.change_count)

    def set_project_info(self, project: ProjectInfo, change_count: int = 0) -> None:
        """接收 ProjectInfo 填充数据。"""
        self._apply_project_info(project, change_count)

    # ── 交互 ─────────────────────────────────────────────

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._project.project_id)
        super().mousePressEvent(event)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        """右键菜单：编辑/删除（占位）/打开目录/复制路径"""
        menu = QMenu(self)

        edit_action = QAction("编辑项目...", menu)
        edit_action.triggered.connect(lambda: self.editRequested.emit(self._project.project_id))
        menu.addAction(edit_action)

        delete_action = QAction("删除项目...", menu)
        delete_action.triggered.connect(lambda: self.deleteRequested.emit(self._project.project_id))
        menu.addAction(delete_action)

        menu.addSeparator()

        open_dir_action = QAction("打开目录", menu)
        open_dir_action.triggered.connect(self._open_dir)
        menu.addAction(open_dir_action)

        copy_path_action = QAction("复制路径", menu)
        copy_path_action.triggered.connect(self._copy_path)
        menu.addAction(copy_path_action)

        menu.exec(event.globalPos())

    def _open_dir(self) -> None:
        """在系统文件管理器中打开项目目录"""
        path = self._project.path
        if path and os.path.isdir(path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def _copy_path(self) -> None:
        """复制项目路径到剪贴板"""
        clipboard = QApplication.clipboard()
        if clipboard is not None:
            clipboard.setText(self._project.path)

    @property
    def project(self) -> ProjectInfo:
        """卡片对应的项目信息"""
        return self._project

    @property
    def change_count(self) -> int:
        """卡片对应的变更数"""
        return self._change_count
