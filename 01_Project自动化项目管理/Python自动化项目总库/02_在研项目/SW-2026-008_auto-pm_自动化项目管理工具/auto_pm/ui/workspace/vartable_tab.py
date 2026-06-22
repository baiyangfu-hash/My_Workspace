"""项目工作区 - 变量表 Tab（M4-Iter1）

展示 PLC 项目的变量表（CSV 格式），支持：
- 扫描项目下的变量表文件（02_PLC程序/通用ST程序及变量表/*.csv）
- 表格展示变量定义（名称/类型/地址/注释）
- 刷新变量表

布局：
    ┌─────────────────────────────────────────────────────────┐
    │ [🔄 刷新]  文件: 变量表_全局.csv                          │
    ├─────────────────────────────────────────────────────────┤
    │ 名称      │ 类型    │ 地址      │ 注释                   │
    │──────────┼─────────┼───────────┼────────────────────────│
    │ Motor1   │ Bool    │ %Q0.0    │ 1号电机启动             │
    │ Speed1   │ Int     │ %MW10    │ 1号电机速度             │
    ├─────────────────────────────────────────────────────────┤
    │ 变量数: 25  文件: 2 个                                   │
    └─────────────────────────────────────────────────────────┘

信号：
    vartable_loaded() - 变量表加载完成
"""

from __future__ import annotations

import csv
import os
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from auto_pm.core.paths import PLC_STD_DIRS
from auto_pm.logging.logging import setup_logger

log = setup_logger(log_level="INFO", app_name="auto_pm")

__all__ = ["VartableTab"]

# 变量表文件搜索路径（相对项目根目录）
_VARTABLE_SEARCH_PATHS = [
    os.path.join("02_PLC程序", "通用ST程序及变量表"),
    os.path.join("02_PLC程序"),
]

# 支持的变量表文件扩展名
_VARTABLE_EXTENSIONS = (".csv",)

# 变量表列定义
_VARTABLE_COLUMNS = ["名称", "类型", "地址", "注释"]


class VartableTab(QWidget):
    """变量表 Tab

    扫描并展示 PLC 项目下的变量表文件（CSV 格式）。
    """

    vartable_loaded = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._project_path = ""
        self._vartable_files: list[str] = []
        self._current_file = ""
        self._build_ui()

    def _build_ui(self) -> None:
        """构建 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # 工具栏
        toolbar = self._build_toolbar()
        layout.addWidget(toolbar)

        # 表格
        self._table = QTableWidget(0, len(_VARTABLE_COLUMNS))
        self._table.setHorizontalHeaderLabels(_VARTABLE_COLUMNS)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.setAlternatingRowColors(True)
        layout.addWidget(self._table, 1)

        # 状态栏
        self._status_label = QLabel("未加载")
        self._status_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(self._status_label)

    def _build_toolbar(self) -> QFrame:
        """构建工具栏"""
        frame = QFrame()
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.clicked.connect(self._on_refresh)
        layout.addWidget(refresh_btn)

        layout.addWidget(QLabel("文件:"))
        self._file_combo = QComboBox()
        self._file_combo.setMinimumWidth(300)
        self._file_combo.currentTextChanged.connect(self._on_file_changed)
        layout.addWidget(self._file_combo, 1)

        layout.addStretch()
        return frame

    def set_project_path(self, project_path: str) -> None:
        """设置项目路径并加载变量表"""
        self._project_path = project_path
        self._refresh_files()

    def _refresh_files(self) -> None:
        """刷新变量表文件列表"""
        self._vartable_files = []
        self._file_combo.clear()

        if not self._project_path or not os.path.isdir(self._project_path):
            self._status_label.setText("未加载（项目路径无效）")
            return

        # 扫描变量表文件
        for search_path in _VARTABLE_SEARCH_PATHS:
            full_path = os.path.join(self._project_path, search_path)
            if not os.path.isdir(full_path):
                continue
            try:
                for entry in os.listdir(full_path):
                    if entry.lower().endswith(_VARTABLE_EXTENSIONS):
                        file_path = os.path.join(full_path, entry)
                        if file_path not in self._vartable_files:
                            self._vartable_files.append(file_path)
                            self._file_combo.addItem(entry, file_path)
            except OSError as e:
                log.warning("扫描变量表目录失败: %s: %s", full_path, e)

        if self._vartable_files:
            self._status_label.setText(f"找到 {len(self._vartable_files)} 个变量表文件")
            # 加载第一个文件
            self._load_file(self._vartable_files[0])
        else:
            self._status_label.setText("未找到变量表文件")
            self._table.setRowCount(0)

    def _load_file(self, file_path: str) -> None:
        """加载变量表文件"""
        self._current_file = file_path
        self._table.setRowCount(0)

        try:
            with open(file_path, encoding="utf-8-sig", newline="") as f:
                reader = csv.reader(f)
                rows = list(reader)
        except (OSError, csv.Error) as e:
            log.warning("读取变量表失败: %s: %s", file_path, e)
            self._status_label.setText(f"读取失败: {e}")
            return

        if not rows:
            self._status_label.setText("变量表为空")
            return

        # 第一行作为表头（跳过），其余作为数据
        # 兼容不同列数的变量表
        data_rows = rows[1:] if len(rows) > 1 else []
        self._table.setRowCount(len(data_rows))

        for row_idx, row in enumerate(data_rows):
            for col_idx, value in enumerate(row[:len(_VARTABLE_COLUMNS)]):
                item = QTableWidgetItem(value.strip())
                self._table.setItem(row_idx, col_idx, item)

        self._status_label.setText(
            f"已加载: {os.path.basename(file_path)} ({len(data_rows)} 个变量)"
        )
        self.vartable_loaded.emit()
        log.info("变量表已加载: %s (%d 个变量)", file_path, len(data_rows))

    def _on_refresh(self) -> None:
        """刷新按钮点击"""
        self._refresh_files()

    def _on_file_changed(self, _text: str) -> None:
        """文件选择变化"""
        idx = self._file_combo.currentIndex()
        if idx < 0 or idx >= len(self._vartable_files):
            return
        file_path = self._vartable_files[idx]
        if file_path != self._current_file:
            self._load_file(file_path)
