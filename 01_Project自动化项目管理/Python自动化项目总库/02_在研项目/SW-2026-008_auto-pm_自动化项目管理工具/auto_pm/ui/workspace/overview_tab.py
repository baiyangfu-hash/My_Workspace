"""项目工作区 - 概览 Tab

展示项目元数据、立项表信息、变更概览、最近活动。
所有文件系统/Service 调用均用 try-except 包裹，失败时显示友好提示。
"""

from __future__ import annotations

import os
import re
from typing import Any

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLayout,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from auto_pm.logging.logging import setup_logger
from auto_pm.models import ProjectInfo

log = setup_logger(log_level="INFO", app_name="auto_pm")

# 技术栈 → (中文标签, 背景色, 前景色)
_STACK_BADGE: dict[str, tuple[str, str, str]] = {
    "plc": ("PLC", "#4a90d9", "#ffffff"),
    "python": ("Python", "#27ae60", "#ffffff"),
    "unknown": ("未分类", "#95a5a6", "#ffffff"),
}

# 项目阶段 → 中文标签
_PHASE_LABEL: dict[str, str] = {
    "developing": "开发中",
    "commissioning": "调试中",
    "production": "生产中",
    "archived": "已归档",
    "": "未设置",
}

# 变更状态分组：状态值 → 分组key
_CHANGE_STATUS_GROUPS: dict[str, str] = {
    "draft": "draft",
    "submitted": "draft",
    "under_review": "draft",
    "approved": "implementing",
    "conditionally_approved": "implementing",
    "implementing": "implementing",
    "pending_acceptance": "implementing",
    "accepting": "implementing",
    "completed": "completed",
    "closed": "archived",
    "rejected": "archived",
}

_CHANGE_GROUP_LABELS: dict[str, str] = {
    "draft": "草稿",
    "implementing": "实施中",
    "completed": "已完成",
    "archived": "已归档",
    "other": "其他",
}

# 立项表候选路径（相对项目根目录）
_PROPOSAL_CANDIDATES: list[str] = [
    "00_项目基础信息/0-项目立项表_PROJ.md",
    "00_项目基础信息/000_通用项目立项表_PM.md",
]

# 立项表通配查找目录
_PROPOSAL_GLOB_DIRS: list[str] = [
    "00_项目管理/01_立项与需求",
    "00_项目基础信息",
]

# 立项表背景/目标章节正则（匹配 ## 或 ### 级别，标题含"背景"或"目标"）
_SECTION_RE = re.compile(r"^(#{2,3})\s+(.+)$", re.MULTILINE)

# Markdown 表格行正则
_TABLE_ROW_RE = re.compile(r"^\|(.+)\|\s*$")

# 背景或目标关键词
_BG_KEYWORDS = ("背景",)
_GOAL_KEYWORDS = ("目标",)

_STYLE = """
QFrame#sectionCard {
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
}
QLabel#sectionTitle {
    font-size: 13px;
    font-weight: bold;
    color: #333;
    padding-bottom: 4px;
    border-bottom: 1px solid #eee;
}
QLabel#fieldLabel { font-size: 12px; color: #888; }
QLabel#fieldValue { font-size: 12px; color: #222; }
QLabel#fieldValueLink {
    font-size: 12px; color: #4a90d9;
}
QLabel#fieldValueLink:hover { text-decoration: underline; }
QLabel#hintLabel { color: #999; font-size: 12px; font-style: italic; }
QLabel#activityItem { font-size: 12px; color: #444; padding: 3px 0; }
QLabel#activitySource { font-size: 11px; color: #999; }
QLabel#changeCount { font-size: 14px; font-weight: bold; color: #4a90d9; }
"""

# 立项表背景/目标文本最大长度
_BG_TEXT_MAX_LEN = 200

# 最近活动最大展示条数
_ACTIVITY_MAX_ITEMS = 10


class OverviewTab(QWidget):
    """概览 Tab

    展示项目元数据信息网格、立项表解析信息、变更概览、最近活动列表。
    通过 load_project(project) 加载数据，所有加载失败均显示友好提示。
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._project: ProjectInfo | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 12, 16, 12)
        outer.setSpacing(12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        self._container_layout = QVBoxLayout(container)
        self._container_layout.setContentsMargins(0, 0, 0, 0)
        self._container_layout.setSpacing(12)

        # 元数据信息网格
        self._meta_card, meta_content = self._make_section_card("项目元数据")
        self._meta_grid = QGridLayout()
        self._meta_grid.setContentsMargins(14, 10, 14, 10)
        self._meta_grid.setHorizontalSpacing(16)
        self._meta_grid.setVerticalSpacing(8)
        self._meta_grid.setColumnStretch(1, 1)
        meta_content.addLayout(self._meta_grid)
        self._container_layout.addWidget(self._meta_card)

        # 立项表信息
        self._proposal_card, proposal_content = self._make_section_card("立项表信息")
        self._proposal_layout = QVBoxLayout()
        self._proposal_layout.setContentsMargins(14, 10, 14, 10)
        self._proposal_layout.setSpacing(6)
        proposal_content.addLayout(self._proposal_layout)
        self._container_layout.addWidget(self._proposal_card)

        # 变更概览 + 最近活动（横向并列）
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(12)

        self._change_card, change_content = self._make_section_card("变更概览")
        self._change_layout = QVBoxLayout()
        self._change_layout.setContentsMargins(14, 10, 14, 10)
        self._change_layout.setSpacing(6)
        change_content.addLayout(self._change_layout)
        bottom_row.addWidget(self._change_card, 1)

        self._activity_card, activity_content = self._make_section_card("最近活动")
        self._activity_layout = QVBoxLayout()
        self._activity_layout.setContentsMargins(14, 10, 14, 10)
        self._activity_layout.setSpacing(4)
        activity_content.addLayout(self._activity_layout)
        bottom_row.addWidget(self._activity_card, 1)

        self._container_layout.addLayout(bottom_row)
        self._container_layout.addStretch(1)

        scroll.setWidget(container)
        outer.addWidget(scroll)

    def _make_section_card(self, title: str) -> tuple[QFrame, QVBoxLayout]:
        """创建带标题的区块卡片，返回 (卡片, 内容布局)"""
        card = QFrame()
        card.setObjectName("sectionCard")
        card.setStyleSheet(_STYLE)
        v = QVBoxLayout(card)
        v.setContentsMargins(14, 10, 14, 10)
        v.setSpacing(6)
        title_label = QLabel(title)
        title_label.setObjectName("sectionTitle")
        v.addWidget(title_label)
        return card, v

    # ── 数据加载 ──────────────────────────────────────────

    def load_project(self, project: ProjectInfo) -> None:
        """加载项目数据到概览 Tab"""
        self._project = project
        self._load_meta(project)
        self._load_proposal(project)
        self._load_change_overview(project)
        self._load_recent_activity(project)
        log.info("概览Tab加载项目: %s", project.project_id)

    # ── D2.1 项目元数据信息网格 ───────────────────────────

    def _load_meta(self, project: ProjectInfo) -> None:
        """填充项目元数据信息网格"""
        self._clear_grid(self._meta_grid)

        stack_text = _STACK_BADGE.get(project.stack, _STACK_BADGE["unknown"])[0]
        phase_text = _PHASE_LABEL.get(project.phase, project.phase or "未设置")
        version_text = project.version or "—"
        desc_text = project.description or "—"

        rows: list[tuple[str, str, bool]] = [
            ("项目编号", project.project_id, False),
            ("项目名称", project.name or "—", False),
            ("技术栈", stack_text, False),
            ("版本", version_text, False),
            ("阶段", phase_text, False),
            ("项目路径", project.path or "—", True),
            ("描述", desc_text, False),
        ]

        for row_idx, (label_text, value_text, is_link) in enumerate(rows):
            label = QLabel(label_text)
            label.setObjectName("fieldLabel")
            self._meta_grid.addWidget(label, row_idx, 0)

            value = QLabel(value_text)
            value.setObjectName("fieldValueLink" if is_link else "fieldValue")
            value.setWordWrap(True)
            value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            if is_link and project.path and os.path.isdir(project.path):
                value.setCursor(Qt.CursorShape.PointingHandCursor)
                value.mousePressEvent = self._make_open_dir_handler(project.path)  # type: ignore[method-assign]
            self._meta_grid.addWidget(value, row_idx, 1)

    @staticmethod
    def _make_open_dir_handler(path: str) -> Any:
        """创建打开目录的鼠标事件处理器"""

        def handler(_event: Any) -> None:
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))

        return handler

    @staticmethod
    def _clear_grid(grid: QGridLayout) -> None:
        """清空 GridLayout 中的所有项"""
        while grid.count():
            item = grid.takeAt(0)
            if item is None:
                continue
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    # ── D2.2 立项表解析展示 ───────────────────────────────

    def _load_proposal(self, project: ProjectInfo) -> None:
        """解析并展示立项表信息"""
        self._clear_layout(self._proposal_layout)

        proposal_path = self._find_proposal_file(project.path)
        if proposal_path is None:
            hint = QLabel("未找到立项表文件")
            hint.setObjectName("hintLabel")
            self._proposal_layout.addWidget(hint)
            return

        try:
            with open(proposal_path, encoding="utf-8") as f:
                content = f.read()
        except OSError as e:
            log.warning("读取立项表失败: %s: %s", proposal_path, e)
            hint = QLabel(f"读取立项表失败: {e}")
            hint.setObjectName("hintLabel")
            self._proposal_layout.addWidget(hint)
            return

        table_rows = self._parse_first_table(content)
        if table_rows:
            grid = QGridLayout()
            grid.setHorizontalSpacing(16)
            grid.setVerticalSpacing(6)
            grid.setColumnStretch(1, 1)
            for row_idx, (key, value) in enumerate(table_rows):
                key_label = QLabel(key)
                key_label.setObjectName("fieldLabel")
                grid.addWidget(key_label, row_idx, 0)
                value_label = QLabel(value)
                value_label.setObjectName("fieldValue")
                value_label.setWordWrap(True)
                grid.addWidget(value_label, row_idx, 1)
            self._proposal_layout.addLayout(grid)
        else:
            hint = QLabel("（立项表未包含基本信息表格）")
            hint.setObjectName("hintLabel")
            self._proposal_layout.addWidget(hint)

        bg_text = self._parse_section_text(content, _BG_KEYWORDS)
        goal_text = self._parse_section_text(content, _GOAL_KEYWORDS)
        if bg_text:
            self._proposal_layout.addWidget(self._make_text_label("项目背景", bg_text))
        if goal_text:
            self._proposal_layout.addWidget(self._make_text_label("项目目标", goal_text))

    def _make_text_label(self, title: str, text: str) -> QWidget:
        """创建带标题的文本块"""
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 6, 0, 0)
        v.setSpacing(2)
        title_label = QLabel(title)
        title_label.setObjectName("fieldLabel")
        v.addWidget(title_label)
        body = QLabel(text)
        body.setObjectName("fieldValue")
        body.setWordWrap(True)
        v.addWidget(body)
        return w

    @staticmethod
    def _find_proposal_file(project_path: str) -> str | None:
        """按优先级查找立项表文件"""
        if not project_path or not os.path.isdir(project_path):
            return None

        # 1. 已知候选路径
        for candidate_rel in _PROPOSAL_CANDIDATES:
            candidate = os.path.join(project_path, candidate_rel)
            if os.path.isfile(candidate):
                return candidate

        # 2. 已知目录通配查找
        for glob_dir in _PROPOSAL_GLOB_DIRS:
            search_dir = os.path.join(project_path, glob_dir)
            if not os.path.isdir(search_dir):
                continue
            try:
                for name in os.listdir(search_dir):
                    if name.endswith(".md") and "立项表" in name:
                        return os.path.join(search_dir, name)
            except OSError:
                continue

        # 3. 深度2层通配查找
        try:
            for root, dirs, files in os.walk(project_path):
                # 限制深度2层
                rel_depth = os.path.relpath(root, project_path).count(os.sep)
                if rel_depth >= 2:
                    dirs[:] = []
                    continue
                for name in files:
                    if name.endswith(".md") and "立项表" in name:
                        return os.path.join(root, name)
        except OSError:
            pass

        return None

    @staticmethod
    def _parse_first_table(content: str) -> list[tuple[str, str]]:
        """解析 Markdown 第一个表格，返回键值对列表

        支持两种格式：
        - | 项目 | 内容 |（首行表头，后续行为数据）
        - | 项目名称 | 值 |（每行本身就是键值对）
        """
        lines = content.splitlines()
        table_lines: list[str] = []
        in_table = False
        for line in lines:
            if _TABLE_ROW_RE.match(line):
                if not in_table:
                    in_table = True
                table_lines.append(line)
            else:
                if in_table:
                    break

        if len(table_lines) < 2:
            return []

        # 跳过分隔行（|---|---|）
        data_lines = [
            ln for ln in table_lines
            if not re.match(r"^\|[\s\-:|]+\|\s*$", ln)
        ]
        if not data_lines:
            return []

        # 判断格式：首行是否为表头（如"项目|内容"）
        first_cells = OverviewTab._split_table_row(data_lines[0])
        rows: list[tuple[str, str]] = []

        if len(first_cells) == 2 and (
            "项目" in first_cells[0] or "内容" in first_cells[0]
        ):
            # 表头格式：跳过首行，后续为 | 键 | 值 |
            for line in data_lines[1:]:
                cells = OverviewTab._split_table_row(line)
                if len(cells) >= 2:
                    key = OverviewTab._clean_cell(cells[0])
                    value = OverviewTab._clean_cell(cells[1])
                    if key:
                        rows.append((key, value))
        else:
            # 键值对格式：每行 | 键 | 值 |
            for line in data_lines:
                cells = OverviewTab._split_table_row(line)
                if len(cells) >= 2:
                    key = OverviewTab._clean_cell(cells[0])
                    value = OverviewTab._clean_cell(cells[1])
                    if key:
                        rows.append((key, value))

        return rows

    @staticmethod
    def _split_table_row(line: str) -> list[str]:
        """拆分表格行为单元格"""
        match = _TABLE_ROW_RE.match(line)
        if not match:
            return []
        inner = match.group(1)
        return [c.strip() for c in inner.split("|")]

    @staticmethod
    def _clean_cell(text: str) -> str:
        """清理单元格文本：去除 ** 加粗标记和首尾空白"""
        cleaned = text.strip()
        cleaned = re.sub(r"\*\*(.+?)\*\*", r"\1", cleaned)
        return cleaned

    @staticmethod
    def _parse_section_text(content: str, keywords: tuple[str, ...]) -> str:
        """解析包含指定关键词的章节文本，截断前200字"""
        matches = list(_SECTION_RE.finditer(content))
        for i, match in enumerate(matches):
            title = match.group(2)
            if any(kw in title for kw in keywords):
                start = match.end()
                # 章节结束于下一个同级或更高级标题
                current_level = len(match.group(1))
                end = len(content)
                for j in range(i + 1, len(matches)):
                    next_match = matches[j]
                    if len(next_match.group(1)) <= current_level:
                        end = next_match.start()
                        break
                section_text = content[start:end].strip()
                # 去除 Markdown 列表/表格标记，保留纯文本
                lines: list[str] = []
                for ln in section_text.splitlines():
                    stripped = ln.strip()
                    if not stripped:
                        continue
                    if stripped.startswith("|"):
                        continue
                    # 去除列表标记
                    cleaned = re.sub(r"^[-*+]\s+", "", stripped)
                    lines.append(cleaned)
                text = " ".join(lines)
                if len(text) > _BG_TEXT_MAX_LEN:
                    text = text[:_BG_TEXT_MAX_LEN] + "..."
                return text
        return ""

    # ── D2.3 变更概览 ─────────────────────────────────────

    def _load_change_overview(self, project: ProjectInfo) -> None:
        """加载变更概览（按状态分组统计）"""
        self._clear_layout(self._change_layout)

        counts = self._count_changes(project)
        if counts is None:
            hint = QLabel("变更数据加载失败")
            hint.setObjectName("hintLabel")
            self._change_layout.addWidget(hint)
        else:
            for group_key in ("draft", "implementing", "completed", "archived", "other"):
                count = counts.get(group_key, 0)
                if group_key == "other" and count == 0:
                    continue
                row = QHBoxLayout()
                row.setSpacing(8)
                label = QLabel(_CHANGE_GROUP_LABELS.get(group_key, group_key))
                label.setObjectName("fieldLabel")
                row.addWidget(label)
                row.addStretch(1)
                count_label = QLabel(str(count))
                count_label.setObjectName("changeCount")
                row.addWidget(count_label)
                self._change_layout.addLayout(row)

        view_all_btn = QPushButton("查看全部变更")
        view_all_btn.clicked.connect(self._on_view_all_changes)
        self._change_layout.addWidget(view_all_btn)

    def _count_changes(self, project: ProjectInfo) -> dict[str, int] | None:
        """调用 ChangeService 统计变更，失败返回 None"""
        try:
            from auto_pm.change.change_service import ChangeService

            workspace_root = self._infer_workspace_root(project)
            if workspace_root is None:
                log.warning("无法推算 workspace_root: %s", project.path)
                return None

            svc = ChangeService(workspace_root)
            summaries = svc.list_change_requests(project.project_id)
            counts: dict[str, int] = {
                "draft": 0,
                "implementing": 0,
                "completed": 0,
                "archived": 0,
                "other": 0,
            }
            for s in summaries:
                group = _CHANGE_STATUS_GROUPS.get(s.status, "other")
                counts[group] = counts.get(group, 0) + 1
            return counts
        except Exception as e:
            log.warning("变更概览加载失败: %s: %s", project.project_id, e)
            return None

    @staticmethod
    def _infer_workspace_root(project: ProjectInfo) -> str | None:
        """从项目路径推算 ChangeService 所需的 workspace_root

        ChangeService 通过 os.listdir(workspace_root) 查找 {project_id}_* 目录，
        因此 workspace_root 应为项目路径的直接父目录。
        """
        if not project.path:
            return None
        parent = os.path.dirname(project.path)
        return parent if parent else None

    def _on_view_all_changes(self) -> None:
        """查看全部变更（V2.0 占位）"""
        QMessageBox.information(self, "变更管理", "变更管理将在 V2.1 交付。")

    # ── D2.4 最近活动列表 ─────────────────────────────────

    def _load_recent_activity(self, project: ProjectInfo) -> None:
        """加载最近活动列表（解析 PM_SESSION_*.md 章节标题）"""
        self._clear_layout(self._activity_layout)

        activities = self._parse_recent_activity(project.path)
        if not activities:
            hint = QLabel("暂无活动记录")
            hint.setObjectName("hintLabel")
            self._activity_layout.addWidget(hint)
            return

        for title, source in activities:
            item = QLabel(f"• {title}")
            item.setObjectName("activityItem")
            item.setWordWrap(True)
            self._activity_layout.addWidget(item)
            source_label = QLabel(f"  来源: {source}")
            source_label.setObjectName("activitySource")
            self._activity_layout.addWidget(source_label)

        self._activity_layout.addStretch(1)

    @staticmethod
    def _parse_recent_activity(project_path: str) -> list[tuple[str, str]]:
        """解析 PM_SESSION_*.md 文件的章节标题作为活动记录

        按文件修改时间倒序，最多返回 _ACTIVITY_MAX_ITEMS 条。
        """
        if not project_path or not os.path.isdir(project_path):
            return []

        # 收集所有 PM_SESSION_*.md 文件
        session_files: list[tuple[float, str]] = []
        try:
            for name in os.listdir(project_path):
                if name.startswith("PM_SESSION_") and name.endswith(".md"):
                    fpath = os.path.join(project_path, name)
                    if os.path.isfile(fpath):
                        mtime = os.path.getmtime(fpath)
                        session_files.append((mtime, fpath))
        except OSError:
            return []

        if not session_files:
            return []

        # 按修改时间倒序
        session_files.sort(key=lambda x: x[0], reverse=True)

        activities: list[tuple[str, str]] = []
        for _mtime, fpath in session_files:
            source_name = os.path.basename(fpath)
            try:
                with open(fpath, encoding="utf-8") as f:
                    content = f.read()
            except OSError:
                continue

            for match in _SECTION_RE.finditer(content):
                level = len(match.group(1))
                if level in (2, 3):
                    title = match.group(2).strip()
                    # 跳过纯数字编号开头的章节（如 "0. Meta"）
                    if title:
                        activities.append((title, source_name))
                        if len(activities) >= _ACTIVITY_MAX_ITEMS:
                            return activities
        return activities

    @staticmethod
    def _clear_layout(layout: QLayout) -> None:
        """清空 Layout 中的所有项"""
        while layout.count():
            item = layout.takeAt(0)
            if item is None:
                continue
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
            else:
                sub_layout = item.layout()
                if sub_layout is not None:
                    OverviewTab._clear_layout(sub_layout)
