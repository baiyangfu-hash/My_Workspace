"""变量表编辑器（V2.3 Week4 T15）

QTableView + VariableTableModel 实现 VarEntry 列表的增删改查。

功能：
- QTableView 展示 VarEntry 列表（8 列：station/signal_type/address/tag/
  signal_name/device/comment/source_format）
- 双击单元格编辑（受 editable 标志控制）
- 右键菜单：添加行/删除行/复制行
- 工具栏：导入文件（调用 Parser）/导出文件（调用 Converter）/刷新
- 信号：data_changed（通知外部数据已修改）

设计原则：
- VariableTableModel 持有可变的 list[list[str]] 内部数据（VarEntry 是 frozen
  dataclass，无法原地修改）
- 导入时 VarEntry → 行列表转换；导出时行列表 → VarEntry/VarTable/ParseResult
  转换，再经 VariableConverter 输出
- 角色权限由外部通过 editable 参数控制，编辑器本身不判断角色
- line_number 为解析元数据，不作为可编辑列；导出时统一写 0（编辑后的行号
  无意义）
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QPersistentModelIndex,
    Qt,
    Signal,
)
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMenu,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from auto_pm.logging.logging import setup_logger
from auto_pm.vartable.converter import SUPPORTED_OUTPUT_FORMATS, VariableConverter
from auto_pm.vartable.models import ParseResult, VarEntry, VarTable
from auto_pm.vartable.parsers.format_detector import (
    detect_format,
    get_parser_for_format,
)

log = setup_logger(log_level="INFO", app_name="auto_pm")

__all__ = ["VariableTableEditor", "VariableTableModel"]

# VarEntry 可编辑列定义（顺序即表格列顺序）
# line_number 为解析元数据，不作为可编辑列
COLUMNS: tuple[str, ...] = (
    "station",
    "signal_type",
    "address",
    "tag",
    "signal_name",
    "device",
    "comment",
    "source_format",
)


def _entry_to_row(entry: VarEntry) -> list[str]:
    """VarEntry → 可编辑行列表（8 列）"""
    return [
        entry.station,
        entry.signal_type,
        entry.address,
        entry.tag,
        entry.signal_name,
        entry.device,
        entry.comment,
        entry.source_format,
    ]


def _row_to_entry(row: Sequence[str]) -> VarEntry:
    """可编辑行列表 → VarEntry（line_number 统一为 0）"""
    # 保证 8 列，不足补空串
    padded = list(row) + [""] * (len(COLUMNS) - len(row))
    return VarEntry(
        station=padded[0],
        signal_type=padded[1],
        address=padded[2],
        tag=padded[3],
        signal_name=padded[4],
        device=padded[5],
        comment=padded[6],
        source_format=padded[7],
        line_number=0,
    )


class VariableTableModel(QAbstractTableModel):
    """变量表数据模型

    持有可变的 list[list[str]]，通过标准 Qt 模型接口暴露给 QTableView。
    支持批量加载、添加行、删除行、复制行。

    Args:
        editable: 是否允许编辑单元格（角色权限由外部决定后传入）
        parent: 父 QObject
    """

    def __init__(
        self,
        editable: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._headers: list[str] = list(COLUMNS)
        self._rows: list[list[str]] = []
        self._editable = editable

    # ── Qt 模型接口 ────────────────────────────────────────

    def rowCount(
        self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()
    ) -> int:
        if parent.isValid():
            return 0
        return len(self._rows)

    def columnCount(
        self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()
    ) -> int:
        if parent.isValid():
            return 0
        return len(self._headers)

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if not index.isValid() or not (
            0 <= index.row() < len(self._rows)
        ):
            return None
        if role in (
            Qt.ItemDataRole.DisplayRole,
            Qt.ItemDataRole.EditRole,
        ):
            return self._rows[index.row()][index.column()]
        return None

    def setData(
        self,
        index: QModelIndex | QPersistentModelIndex,
        value: Any,
        role: int = Qt.ItemDataRole.EditRole,
    ) -> bool:
        if not self._editable or not index.isValid():
            return False
        if role != Qt.ItemDataRole.EditRole:
            return False
        if not (0 <= index.row() < len(self._rows)):
            return False
        self._rows[index.row()][index.column()] = str(value)
        self.dataChanged.emit(index, index, [role])
        return True

    def flags(
        self, index: QModelIndex | QPersistentModelIndex
    ) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        if self._editable:
            flags |= Qt.ItemFlag.ItemIsEditable
        return flags

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            if 0 <= section < len(self._headers):
                return self._headers[section]
            return None
        return str(section + 1)

    # ── 数据操作 ──────────────────────────────────────────

    def set_entries(self, entries: Sequence[VarEntry]) -> None:
        """批量加载 VarEntry 列表"""
        self.beginResetModel()
        self._rows = [_entry_to_row(e) for e in entries]
        self.endResetModel()

    def get_entries(self) -> list[VarEntry]:
        """导出当前数据为 VarEntry 列表"""
        return [_row_to_entry(row) for row in self._rows]

    def set_rows(self, rows: Sequence[Sequence[str]]) -> None:
        """批量加载通用行数据（列数需与 COLUMNS 一致）"""
        self.beginResetModel()
        self._rows = [list(row) for row in rows]
        self.endResetModel()

    def get_rows(self) -> list[list[str]]:
        """导出当前行数据（副本）"""
        return [list(row) for row in self._rows]

    def add_row(self) -> int:
        """追加一个空行，返回新行索引"""
        row = len(self._rows)
        self.beginInsertRows(QModelIndex(), row, row)
        self._rows.append([""] * len(COLUMNS))
        self.endInsertRows()
        return row

    def remove_row(self, row: int) -> bool:
        """删除指定行，返回是否成功"""
        if not (0 <= row < len(self._rows)):
            return False
        self.beginRemoveRows(QModelIndex(), row, row)
        self._rows.pop(row)
        self.endRemoveRows()
        return True

    def copy_row(self, row: int) -> int:
        """复制指定行并追加到末尾，返回新行索引；失败返回 -1"""
        if not (0 <= row < len(self._rows)):
            return -1
        new_row = len(self._rows)
        self.beginInsertRows(QModelIndex(), new_row, new_row)
        self._rows.append(list(self._rows[row]))
        self.endInsertRows()
        return new_row

    def set_editable(self, editable: bool) -> None:
        """切换可编辑状态"""
        self._editable = editable
        # 通知整个模型刷新（flags 会重新查询）
        if self.rowCount() > 0:
            top = self.index(0, 0)
            bottom = self.index(self.rowCount() - 1, self.columnCount() - 1)
            self.dataChanged.emit(top, bottom, [Qt.ItemDataRole.EditRole])

    @property
    def editable(self) -> bool:
        return self._editable

    @property
    def row_count(self) -> int:
        """当前行数（便于测试访问）"""
        return len(self._rows)

    @property
    def headers(self) -> list[str]:
        return list(self._headers)


class VariableTableEditor(QWidget):
    """变量表编辑器

    QTableView + 工具栏 + 右键菜单，支持 VarEntry 的增删改查、导入导出。

    Args:
        editable: 是否允许编辑（由角色权限决定）
        parent: 父 QWidget

    信号：
        data_changed: 数据被修改（编辑/添加/删除/导入）时发射
    """

    data_changed = Signal()

    def __init__(
        self,
        editable: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._model = VariableTableModel(editable=editable)
        self._converter = VariableConverter()
        self._build_ui()
        # 同步按钮状态与 editable 标志（_build_ui 创建按钮时默认 enabled=True）
        self._add_btn.setEnabled(editable)
        self._delete_btn.setEnabled(editable)
        # 同步初始状态栏文本
        self._update_status()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        # 工具栏
        layout.addWidget(self._build_toolbar())

        # 表格
        self._table = QTableView()
        self._table.setModel(self._model)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self._table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        # V0.5.1 V-04~V-12 修复：隐藏行号列与左上角按钮
        # 行号（line_number）是解析元数据不作为可编辑列展示；默认显示的
        # verticalHeader 在 Stretch 模式下宽度被压缩为 0 但仍 visible，
        # 会触发 zero_size 视觉检查告警。cornerButton 同理。
        self._table.verticalHeader().setVisible(False)
        self._table.setCornerButtonEnabled(False)
        self._table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._on_context_menu)
        layout.addWidget(self._table, 1)

        # 状态栏
        self._status_label = QLabel("未加载")
        self._status_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(self._status_label)

    def _build_toolbar(self) -> QFrame:
        frame = QFrame()
        h = QHBoxLayout(frame)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(6)

        self._import_btn = QPushButton("导入文件")
        self._import_btn.clicked.connect(self._on_import_clicked)
        h.addWidget(self._import_btn)

        self._export_btn = QPushButton("导出文件")
        self._export_btn.clicked.connect(self._on_export_clicked)
        h.addWidget(self._export_btn)

        self._refresh_btn = QPushButton("刷新")
        self._refresh_btn.clicked.connect(self._on_refresh_clicked)
        h.addWidget(self._refresh_btn)

        self._add_btn = QPushButton("添加行")
        self._add_btn.clicked.connect(self._on_add_clicked)
        h.addWidget(self._add_btn)

        self._delete_btn = QPushButton("删除行")
        self._delete_btn.clicked.connect(self._on_delete_clicked)
        h.addWidget(self._delete_btn)

        h.addStretch()
        return frame

    # ── 公开 API ─────────────────────────────────────────

    def set_entries(self, entries: Sequence[VarEntry]) -> None:
        """加载 VarEntry 列表到编辑器"""
        self._model.set_entries(entries)
        self._update_status()
        self.data_changed.emit()

    def get_entries(self) -> list[VarEntry]:
        """获取当前编辑器中的 VarEntry 列表"""
        return self._model.get_entries()

    def set_editable(self, editable: bool) -> None:
        """切换可编辑状态"""
        self._model.set_editable(editable)
        self._add_btn.setEnabled(editable)
        self._delete_btn.setEnabled(editable)

    @property
    def model(self) -> VariableTableModel:
        return self._model

    @property
    def table(self) -> QTableView:
        return self._table

    @property
    def status_label(self) -> QLabel:
        return self._status_label

    @property
    def row_count(self) -> int:
        """当前行数"""
        return self._model.row_count

    def import_file(self, file_path: str | Path) -> bool:
        """导入文件：自动识别格式 → 解析 → 加载到编辑器

        Args:
            file_path: 文件路径

        Returns:
            是否导入成功
        """
        path = Path(file_path)
        if not path.exists():
            self._status_label.setText(f"文件不存在: {path.name}")
            return False

        fmt = detect_format(path)
        parser_cls = get_parser_for_format(fmt)
        if parser_cls is None:
            self._status_label.setText(f"不支持的格式: {fmt.value}")
            return False

        parser = parser_cls()
        result: ParseResult = parser.parse(path)
        if not result.success or result.var_table is None:
            errors = result.errors
            msg = errors[0].message if errors else "解析失败"
            self._status_label.setText(f"解析失败: {msg}")
            return False

        self._model.set_entries(result.var_table.entries)
        self._update_status()
        self.data_changed.emit()
        log.info(
            "导入变量表: %s (%d 条)",
            path.name,
            result.var_table.total_count,
        )
        return True

    def export_file(self, file_path: str | Path, output_format: str) -> bool:
        """导出当前编辑器数据到文件

        Args:
            file_path: 输出文件路径
            output_format: 输出格式（csv/yaml/json）

        Returns:
            是否导出成功
        """
        if output_format not in SUPPORTED_OUTPUT_FORMATS:
            self._status_label.setText(
                f"不支持的格式: {output_format}"
            )
            return False

        entries = self._model.get_entries()
        if not entries:
            self._status_label.setText("无数据可导出")
            return False

        var_table = VarTable(
            entries=tuple(entries),
            source_path=str(file_path),
            source_format="variable_table_editor",
            parsed_at=datetime.now(timezone.utc).isoformat(),
        )
        parse_result = ParseResult(success=True, var_table=var_table)

        try:
            content = self._converter.convert(parse_result, output_format)
        except ValueError as e:
            self._status_label.setText(f"导出失败: {e}")
            return False

        path = Path(file_path)
        try:
            path.write_text(content, encoding="utf-8")
        except OSError as e:
            self._status_label.setText(f"写入失败: {e}")
            return False

        self._status_label.setText(
            f"已导出: {path.name} ({len(entries)} 条, {output_format.upper()})"
        )
        log.info("导出变量表: %s (%s, %d 条)", path.name, output_format, len(entries))
        return True

    # ── 私有槽 ───────────────────────────────────────────

    def _on_import_clicked(self) -> None:
        """导入文件按钮：弹出文件选择对话框"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择变量表文件",
            "",
            "变量表文件 (*.csv *.yml *.yaml *.scl *.awl *.asc *.asn *.wr3);;所有文件 (*)",
        )
        if file_path:
            self.import_file(file_path)

    def _on_export_clicked(self) -> None:
        """导出文件按钮：弹出文件保存对话框"""
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "导出变量表",
            "vartable_export.csv",
            "CSV (*.csv);;YAML (*.yml *.yaml);;JSON (*.json)",
        )
        if not file_path:
            return
        # 根据选择的过滤器推断格式
        fmt = "csv"
        if "YAML" in selected_filter.upper():
            fmt = "yaml"
        elif "JSON" in selected_filter.upper():
            fmt = "json"
        self.export_file(file_path, fmt)

    def _on_refresh_clicked(self) -> None:
        """刷新按钮：触发 data_changed 信号"""
        self._update_status()
        self.data_changed.emit()

    def _on_add_clicked(self) -> None:
        """添加行按钮"""
        row = self._model.add_row()
        self._update_status()
        self.data_changed.emit()
        # 选中新增行
        idx = self._model.index(row, 0)
        self._table.selectRow(row)
        self._table.scrollTo(idx)

    def _on_delete_clicked(self) -> None:
        """删除行按钮：删除当前选中行"""
        row = self._table.currentIndex().row()
        if row >= 0 and self._model.remove_row(row):
            self._update_status()
            self.data_changed.emit()

    def _on_context_menu(self, pos: Any) -> None:
        """右键菜单：添加行/删除行/复制行"""
        menu = QMenu(self)
        menu.addAction("添加行", self._on_add_clicked)
        menu.addAction("删除行", self._on_delete_clicked)
        menu.addAction("复制行", self._on_copy_clicked)
        menu.exec(self._table.viewport().mapToGlobal(pos))

    def _on_copy_clicked(self) -> None:
        """复制行：复制当前选中行并追加到末尾"""
        row = self._table.currentIndex().row()
        if row >= 0:
            self._model.copy_row(row)
            self._update_status()
            self.data_changed.emit()

    # ── 辅助 ─────────────────────────────────────────────

    def _update_status(self) -> None:
        """更新状态栏"""
        count = self._model.row_count
        if count == 0:
            self._status_label.setText("未加载（0 条变量）")
        else:
            self._status_label.setText(f"已加载 {count} 条变量")
