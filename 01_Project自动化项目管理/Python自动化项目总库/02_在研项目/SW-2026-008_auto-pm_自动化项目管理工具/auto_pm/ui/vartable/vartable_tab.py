"""项目工作区 - 变量表 Tab（V2.3 Week4 T16）

基于 VariableTableEditor + vartable 模块 Parser/Converter/BatchParser 实现。

功能：
- 扫描项目下的变量表文件（io_points.csv/program_blocks.yml/communications.yml
  + PLC_ST/*.scl + 通用ST程序及变量表/*.csv）
- 点击文件 → 调用 Parser 解析 → 在 VariableTableEditor 中展示
- 支持批量解析（BatchParser）展示合并结果
- 角色权限：仅 PLCEngineer / SpecEditor 角色可编辑

布局：
    ┌─────────────────────────────────────────────────────────┐
    │ [🔄 刷新] [📊 批量解析]  角色: PLCEngineer               │
    ├──────────┬──────────────────────────────────────────────┤
    │ 文件列表  │  变量表编辑器                                  │
    │ io_points│  [导入][导出][刷新][添加][删除]                │
    │ blocks   │  station | signal_type | address | ...       │
    │ comm     │  cpu     | DI          | X0      | ...       │
    │ FB_Motor │  cpu     | DO          | Y0      | ...       │
    ├──────────┴──────────────────────────────────────────────┤
    │ 状态: 已加载 3 条变量                                     │
    └─────────────────────────────────────────────────────────┘

信号：
    vartable_loaded() - 变量表加载完成
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from auto_pm.logging.logging import setup_logger
from auto_pm.ui.vartable.variable_table_editor import VariableTableEditor
from auto_pm.vartable.batch_parser import (
    BATCH_SCAN_EXTENSIONS,
    BATCH_SCAN_FILENAMES,
    BatchParser,
)
from auto_pm.vartable.models import VarEntry
from auto_pm.vartable.parsers.format_detector import (
    detect_format,
    get_parser_for_format,
)

if TYPE_CHECKING:
    pass

log = setup_logger(log_level="INFO", app_name="auto_pm")

__all__ = ["VartableTab"]

# 可编辑角色（仅这些角色可编辑变量表）
EDITABLE_ROLES: frozenset[str] = frozenset({"PLCEngineer", "SpecEditor"})

# 项目下变量表文件搜索根目录（相对项目根）
_VARTABLE_SEARCH_DIRS: tuple[str, ...] = (
    os.path.join("02_PLC程序"),
)


def _is_supported_vartable(file_path: Path) -> bool:
    """判断文件是否为支持的变量表文件

    复用 BatchParser 的扩展名 + 文件名逻辑。
    """
    ext = file_path.suffix.lower()
    if ext in BATCH_SCAN_EXTENSIONS:
        return True
    if file_path.name in BATCH_SCAN_FILENAMES:
        return True
    return False


def _scan_vartable_files(project_path: str) -> list[Path]:
    """扫描项目下的变量表文件

    在 02_PLC程序/ 下递归搜索支持的变量表文件。

    Args:
        project_path: 项目根目录路径

    Returns:
        找到的文件路径列表（按路径名排序）
    """
    if not project_path or not os.path.isdir(project_path):
        return []

    found: list[Path] = []
    seen: set[str] = set()
    for search_dir in _VARTABLE_SEARCH_DIRS:
        root = Path(project_path) / search_dir
        if not root.is_dir():
            continue
        try:
            for candidate in sorted(root.rglob("*")):
                if not candidate.is_file():
                    continue
                if _is_supported_vartable(candidate):
                    key = str(candidate.resolve())
                    if key not in seen:
                        seen.add(key)
                        found.append(candidate)
        except OSError as e:
            log.warning("扫描变量表目录失败: %s: %s", root, e)

    return found


def _parse_file_to_entries(file_path: Path) -> tuple[list[VarEntry], str]:
    """解析单个文件为 VarEntry 列表

    对于 VarTable 直接返回 entries。
    对于 BlockTable/ChannelTable 返回空列表 + 提示信息（编辑器仅支持 VarEntry）。

    Args:
        file_path: 文件路径

    Returns:
        (entries, status_message)
    """
    fmt = detect_format(file_path)
    parser_cls = get_parser_for_format(fmt)
    if parser_cls is None:
        return [], f"不支持的格式: {fmt.value}"

    parser = parser_cls()
    result = parser.parse(file_path)
    if not result.success:
        errors = result.errors
        msg = errors[0].message if errors else "解析失败"
        return [], f"解析失败: {msg}"

    if result.var_table is not None:
        count = result.var_table.total_count
        return list(result.var_table.entries), f"已加载 {count} 条变量"

    # BlockTable / ChannelTable 无法在 VariableTableEditor 中编辑
    if result.block_table is not None:
        return [], f"程序块表（{result.block_table.total_count} 块），不支持编辑"
    if result.channel_table is not None:
        return [], f"通信通道表（{result.channel_table.total_count} 通道），不支持编辑"

    return [], "无数据"


class VartableTab(QWidget):
    """项目工作区变量表 Tab

    扫描项目下的变量表文件，选择文件后解析并加载到 VariableTableEditor。
    支持批量解析合并结果。角色权限控制编辑能力。

    Args:
        parent: 父 QWidget
        role: 当前用户角色（PLCEngineer/SpecEditor 可编辑，其他只读）

    信号：
        vartable_loaded: 变量表加载完成时发射
    """

    vartable_loaded = Signal()

    def __init__(
        self,
        parent: QWidget | None = None,
        role: str = "",
    ) -> None:
        super().__init__(parent)
        self._project_path = ""
        self._role = role
        self._files: list[Path] = []
        self._batch_parser = BatchParser()
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # 工具栏
        layout.addWidget(self._build_toolbar())

        # 主区域：文件列表 + 编辑器
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧：文件列表
        left = QFrame()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(4)
        left_layout.addWidget(QLabel("变量表文件"))
        self._file_list = QListWidget()
        self._file_list.setMinimumWidth(200)
        self._file_list.currentRowChanged.connect(self._on_file_selected)
        left_layout.addWidget(self._file_list, 1)
        splitter.addWidget(left)

        # 右侧：编辑器
        self._editor = VariableTableEditor(
            editable=self._is_editable(), parent=self
        )
        splitter.addWidget(self._editor)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        layout.addWidget(splitter, 1)

        # 状态栏
        self._status_label = QLabel("未加载")
        self._status_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(self._status_label)

    def _build_toolbar(self) -> QFrame:
        frame = QFrame()
        h = QHBoxLayout(frame)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(6)

        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.clicked.connect(self._on_refresh)
        h.addWidget(refresh_btn)

        batch_btn = QPushButton("📊 批量解析")
        batch_btn.clicked.connect(self._on_batch_parse)
        h.addWidget(batch_btn)

        h.addStretch()

        role_label_text = f"角色: {self._role}" if self._role else "角色: 未设置"
        self._role_label = QLabel(role_label_text)
        self._role_label.setStyleSheet(
            "font-size: 12px; color: #555; padding: 2px 6px;"
        )
        h.addWidget(self._role_label)

        return frame

    # ── 公开 API ─────────────────────────────────────────

    def set_project_path(self, project_path: str) -> None:
        """设置项目路径并扫描变量表文件"""
        self._project_path = project_path
        self._refresh_files()

    def set_role(self, role: str) -> None:
        """设置当前用户角色"""
        self._role = role
        self._role_label.setText(
            f"角色: {role}" if role else "角色: 未设置"
        )
        self._editor.set_editable(self._is_editable())

    def _is_editable(self) -> bool:
        """当前角色是否可编辑"""
        return self._role in EDITABLE_ROLES

    # ── 文件扫描与加载 ───────────────────────────────────

    def _refresh_files(self) -> None:
        """刷新变量表文件列表"""
        self._files = []
        self._file_list.clear()

        if not self._project_path or not os.path.isdir(self._project_path):
            self._status_label.setText("未加载（项目路径无效）")
            return

        self._files = _scan_vartable_files(self._project_path)

        for file_path in self._files:
            # 显示相对项目根的路径
            try:
                rel = file_path.relative_to(self._project_path)
                display = str(rel)
            except ValueError:
                display = file_path.name
            item = QListWidgetItem(display)
            item.setToolTip(str(file_path))
            self._file_list.addItem(item)

        if self._files:
            self._status_label.setText(
                f"找到 {len(self._files)} 个变量表文件"
            )
            self._file_list.setCurrentRow(0)
        else:
            self._status_label.setText("未找到变量表文件")

    def _load_file(self, file_path: Path) -> None:
        """加载单个文件到编辑器"""
        entries, msg = _parse_file_to_entries(file_path)
        self._editor.set_entries(entries)
        self._status_label.setText(
            f"{file_path.name}: {msg}"
        )
        self.vartable_loaded.emit()
        log.info("变量表已加载: %s (%s)", file_path.name, msg)

    # ── 槽 ───────────────────────────────────────────────

    def _on_refresh(self) -> None:
        """刷新按钮"""
        self._refresh_files()

    def _on_file_selected(self, row: int) -> None:
        """文件列表选择变化"""
        if row < 0 or row >= len(self._files):
            return
        self._load_file(self._files[row])

    def _on_batch_parse(self) -> None:
        """批量解析：合并所有文件的 VarEntry"""
        if not self._files:
            self._status_label.setText("无文件可批量解析")
            return

        all_entries: list[VarEntry] = []
        total_files = 0
        skipped = 0
        for file_path in self._files:
            results = self._batch_parser.parse_files([file_path])
            for result in results:
                if result.success and result.var_table is not None:
                    all_entries.extend(result.var_table.entries)
                    total_files += 1
                else:
                    skipped += 1

        self._editor.set_entries(all_entries)
        self._status_label.setText(
            f"批量解析: {total_files} 文件, {len(all_entries)} 条变量"
            + (f", 跳过 {skipped}" if skipped else "")
        )
        self.vartable_loaded.emit()
        log.info(
            "批量解析完成: %d 文件, %d 条变量",
            total_files,
            len(all_entries),
        )

    # ── 属性（便于测试访问） ─────────────────────────────

    @property
    def file_list(self) -> QListWidget:
        return self._file_list

    @property
    def editor(self) -> VariableTableEditor:
        return self._editor

    @property
    def status_label(self) -> QLabel:
        return self._status_label

    @property
    def role(self) -> str:
        return self._role

    @property
    def files(self) -> list[Path]:
        """当前扫描到的文件列表"""
        return list(self._files)

    @property
    def project_path(self) -> str:
        return self._project_path
