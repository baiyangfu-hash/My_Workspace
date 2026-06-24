"""项目列表表格视图

QTableWidget 表格展示项目，支持列头排序和行点击信号。
列：编号 / 业务线 / 项目名称 / 技术栈 / 阶段 / 版本 / 变更数 / 修改时间。
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)

from auto_pm.models import ProjectInfo
from auto_pm.models.project import extract_business_line

__all__ = ["ProjectTableView"]

# 列定义：(列标题, 列索引)
_COL_INDEX = 0
_COL_BL = 1
_COL_NAME = 2
_COL_STACK = 3
_COL_PHASE = 4
_COL_VERSION = 5
_COL_CHANGES = 6
_COL_MTIME = 7

_HEADERS = [
    "编号",
    "业务线",
    "项目名称",
    "技术栈",
    "阶段",
    "版本",
    "变更数",
    "修改时间",
]

_STACK_LABEL: dict[str, str] = {
    "plc": "PLC",
    "python": "Python",
    "unknown": "未分类",
}

_PHASE_LABEL: dict[str, str] = {
    "developing": "开发中",
    "commissioning": "调试中",
    "production": "生产中",
    "archived": "已归档",
    "": "未设置",
}

_BL_LABEL: dict[str, str] = {
    "SW": "SW 软件",
    "DJ": "DJ 单机",
    "ZD": "ZD 整线",
    "XT": "XT 升级",
    "WX": "WX 维保",
    "": "—",
}


class ProjectTableView(QTableWidget):
    """项目列表表格

    表格展示项目，点击列头排序，点击行发射 project_clicked(project_id)。

    Signals:
        project_clicked(str): 行点击时发射，参数为 project_id
    """

    project_clicked = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._project_ids: list[str] = []
        self._build_ui()

    def _build_ui(self) -> None:
        self.setColumnCount(len(_HEADERS))
        self.setHorizontalHeaderLabels(_HEADERS)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        self.setSortingEnabled(True)

        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(False)
        header.setSectionsClickable(True)

        self.cellClicked.connect(self._on_cell_clicked)

    def _on_cell_clicked(self, row: int, _col: int) -> None:
        if 0 <= row < len(self._project_ids):
            self.project_clicked.emit(self._project_ids[row])

    # ── 数据加载 ──────────────────────────────────────────

    def set_projects(
        self,
        projects: list[ProjectInfo],
        change_counts: dict[str, int] | None = None,
    ) -> None:
        """加载项目列表到表格

        Args:
            projects: 项目列表
            change_counts: project_id → 变更数 映射（可选）
        """
        change_counts = change_counts or {}
        self.setSortingEnabled(False)
        self.setRowCount(len(projects))
        self._project_ids = [p.project_id for p in projects]

        for row, proj in enumerate(projects):
            bl = proj.business_line or extract_business_line(proj.project_id)
            self._set_item(row, _COL_INDEX, proj.project_id)
            self._set_item(row, _COL_BL, _BL_LABEL.get(bl, bl or "—"))
            self._set_item(row, _COL_NAME, proj.name or proj.project_id)
            self._set_item(row, _COL_STACK, _STACK_LABEL.get(proj.stack, proj.stack))
            self._set_item(row, _COL_PHASE, _PHASE_LABEL.get(proj.phase, proj.phase or "未设置"))
            self._set_item(row, _COL_VERSION, proj.version or "—")
            self._set_item(row, _COL_CHANGES, str(change_counts.get(proj.project_id, 0)))
            self._set_item(row, _COL_MTIME, _format_mtime(proj.file_mtime))

            # 存储 project_id 到行（UserRole），便于排序后定位
            for col in range(len(_HEADERS)):
                item = self.item(row, col)
                if item is not None:
                    item.setData(Qt.ItemDataRole.UserRole, proj.project_id)

        self.setSortingEnabled(True)
        self.resizeColumnsToContents()

    def _set_item(self, row: int, col: int, text: str) -> None:
        item = QTableWidgetItem(text)
        # 变更数列右对齐并作为数字排序
        if col == _COL_CHANGES:
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            try:
                item.setData(Qt.ItemDataRole.EditRole, int(text))
            except ValueError:
                pass
        self.setItem(row, col, item)

    def clear_projects(self) -> None:
        """清空表格"""
        self.setRowCount(0)
        self._project_ids = []


def _format_mtime(mtime: float) -> str:
    """格式化修改时间戳为可读字符串"""
    if not mtime or mtime <= 0:
        return "—"
    try:
        from datetime import datetime

        return datetime.fromtimestamp(float(mtime)).strftime("%Y-%m-%d %H:%M")
    except (OSError, ValueError, OverflowError):
        return "—"
