# -*- coding: utf-8 -*-
"""
Excel导出面板组件 - FB接口变量表导出为Excel格式

基于PyQt5实现的Excel导出面板UI。
提供单个FB/批量FB/检查报告的Excel导出功能，
集成目录选择、选项配置、FB列表和实时日志。

主要功能:
- 目录选择: QPushButton + QFileDialog 选择输出目录
- 单个导出: 调用 ExcelExporter.export_fb_from_file()
- 批量导出: 调用 ExcelExporter.export_all_fbs()
- 检查报告导出: 调用 ExcelExporter.export_check_report()
- FB列表: 自动扫描项目中所有.scl文件，列出FB供勾选
- 导出日志: QTextBrowser 实时显示进度和结果
"""
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QGroupBox,
    QTextBrowser,
    QCheckBox,
    QComboBox,
    QHeaderView,
    QFileDialog,
    QApplication,
    QFrame,
    QSizePolicy,
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QMutex
from PyQt5.QtGui import QColor, QFont

from src.utils.logger import setup_logger
from src.exporters.excel_exporter import ExcelExporter

logger = setup_logger(__name__)


class ExportWorker(QThread):
    """后台导出工作线程"""

    progress_updated = pyqtSignal(str)
    fb_exported = pyqtSignal(str, str)
    batch_completed = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(
        self,
        mode: str,
        project_path: str = "",
        scl_file_path: str = "",
        output_dir: str = "",
        include_syslib: bool = False,
        selected_fbs: Optional[List[str]] = None,
        check_results: Optional[List] = None,
        parent=None,
    ):
        super().__init__(parent)
        self._mode = mode
        self._project_path = project_path
        self._scl_file_path = scl_file_path
        self._output_dir = output_dir
        self._include_syslib = include_syslib
        self._selected_fbs = selected_fbs or []
        self._check_results = check_results or []
        self._mutex = QMutex()
        self._is_cancelled = False

    def run(self):
        try:
            if self._mode == "single":
                self._do_single_export()
            elif self._mode == "batch":
                self._do_batch_export()
            elif self._mode == "report":
                self._do_report_export()
        except Exception as e:
            logger.error(f"导出异常: {e}", exc_info=True)
            self.error_occurred.emit(f"导出过程发生异常: {str(e)}")

    def _do_single_export(self):
        self.progress_updated.emit(f"正在导出: {Path(self._scl_file_path).name}")
        try:
            result_path = ExcelExporter.export_fb_from_file(
                self._scl_file_path,
                self._output_dir,
            )
            fb_name = Path(self._scl_file_path).stem
            self.fb_exported.emit(fb_name, result_path)
            self.batch_completed.emit([result_path])
            self.progress_updated.emit(f"✅ {fb_name}.xlsx 已导出")
        except Exception as e:
            self.error_occurred.emit(f"单FB导出失败: {str(e)}")

    def _do_batch_export(self):
        project = Path(self._project_path)
        pattern = "**/*.scl"
        scl_files = sorted(project.glob(pattern), key=lambda p: p.name.lower())
        exported_paths = []
        total = len(scl_files)

        self.progress_updated.emit(f"📦 开始批量导出, 共找到 {total} 个SCL文件")

        for idx, scl_file in enumerate(scl_files):
            self._mutex.lock()
            if self._is_cancelled:
                self._mutex.unlock()
                self.progress_updated.emit("⚠ 批量导出已取消")
                break
            self._mutex.unlock()

            if not self._include_syslib and "syslib" in scl_file.parts:
                continue

            try:
                source_text = scl_file.read_text(encoding="utf-8")
                exports = ExcelExporter._parse_scl_source(source_text)
                for exp in exports:
                    if self._selected_fbs and exp.fb_name not in self._selected_fbs:
                        continue
                    out_file = Path(self._output_dir) / f"{exp.fb_name}_接口变量表.xlsx"
                    from openpyxl import Workbook
                    wb = Workbook()
                    ws = wb.active
                    ws.title = exp.fb_name
                    ExcelExporter._write_sheet(ws, exp)
                    wb.save(str(out_file))
                    exported_paths.append(str(out_file))
                    self.fb_exported.emit(exp.fb_name, str(out_file))
                    self.progress_updated.emit(
                        f"[{idx + 1}/{total}] ✅ {exp.fb_name}.xlsx 已导出"
                    )
            except Exception as e:
                self.progress_updated.emit(
                    f"[{idx + 1}/{total}] ⚠ 跳过 {scl_file.name}: {e}"
                )

        self.progress_updated.emit(f"🎉 批量导出完成, 共 {len(exported_paths)} 个文件")
        self.batch_completed.emit(exported_paths)

    def _do_report_export(self):
        self.progress_updated.emit("📋 正在生成检查报告...")
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"规范检查报告_{timestamp}.xlsx"
            output_path = os.path.join(self._output_dir, default_name)
            result_path = ExcelExporter.export_check_report(
                self._check_results, output_path
            )
            self.batch_completed.emit([result_path])
            self.progress_updated.emit(f"✅ 检查报告已导出: {Path(result_path).name}")
        except Exception as e:
            self.error_occurred.emit(f"检查报告导出失败: {str(e)}")

    def cancel(self):
        self._mutex.lock()
        self._is_cancelled = True
        self._mutex.unlock()


class ExcelExportPanel(QWidget):
    """
    Excel导出面板主组件

    提供完整的FB接口变量表Excel导出UI界面，
    包括目录选择、导出选项、FB列表、操作按钮和日志输出。

    Signals:
        export_completed: 单个FB导出完成时发出，携带文件路径
        export_all_completed: 批量导出完成时发出，携带文件路径列表
        export_error: 导出错误时发出，携带错误信息
        file_open_requested: 用户请求打开导出文件时发出
    """

    export_completed = pyqtSignal(str)
    export_all_completed = pyqtSignal(list)
    export_error = pyqtSignal(str)
    file_open_requested = pyqtSignal(str)

    COL_CHECK = 0
    COL_NAME = 1
    COL_CATEGORY = 2
    COL_VAR_COUNT = 3
    COL_FILE_PATH = 4

    FORMAT_OPTIONS = ["9列标准格式", "扩展格式(含调用关系)", "精简格式"]
    STYLE_OPTIONS = ["带样式(推荐)", "纯数据(无样式)"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._output_dir: str = ""
        self._project_path: str = ""
        self._export_worker: Optional[ExportWorker] = None
        self._fb_data_list: List[dict] = []
        self._init_ui()
        self._connect_signals()
        logger.info("Excel导出面板初始化完成")

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        title_label = QLabel("\U0001F4CA FB接口Excel导出")
        title_label.setProperty("panelTitle", True)
        main_layout.addWidget(title_label)

        dir_group = self._create_directory_area()
        main_layout.addWidget(dir_group)

        options_group = self._create_options_area()
        main_layout.addWidget(options_group)

        btn_bar = self._create_button_bar()
        main_layout.addLayout(btn_bar)

        list_group = self._create_fb_list_area()
        main_layout.addWidget(list_group, stretch=1)

        log_group = self._create_log_area()
        main_layout.addWidget(log_group)

    def _create_directory_area(self) -> QGroupBox:
        group = QGroupBox("\U0001F4C1 导出目标")
        group.setProperty("IndustrialGroup", True)

        layout = QHBoxLayout(group)
        layout.setContentsMargins(10, 18, 10, 10)

        dir_label = QLabel("📁 输出目录:")
        layout.addWidget(dir_label)

        self._btn_select_dir = QPushButton("选择目录...")
        self._btn_select_dir.setMinimumHeight(28)
        self._btn_select_dir.setProperty("ToolBtn", True)
        layout.addWidget(self._btn_select_dir)

        self._dir_path_label = QLabel("未选择")
        self._dir_path_label.setProperty("treeStatus", True)
        self._dir_path_label.setMinimumWidth(200)
        layout.addWidget(self._dir_path_label)

        layout.addStretch()

        return group

    def _create_options_area(self) -> QGroupBox:
        group = QGroupBox("⚙ 导出选项")
        group.setProperty("IndustrialGroup", True)

        layout = QHBoxLayout(group)
        layout.setContentsMargins(10, 18, 10, 10)

        self._chk_include_syslib = QCheckBox("包含SysLib公共库")
        self._chk_include_syslib.setChecked(True)
        layout.addWidget(self._chk_include_syslib)

        self._chk_call_matrix = QCheckBox("导出调用关系矩阵")
        self._chk_call_matrix.setChecked(True)
        layout.addWidget(self._chk_call_matrix)

        layout.addSpacing(20)

        fmt_label = QLabel("格式:")
        layout.addWidget(fmt_label)

        self._combo_format = QComboBox()
        self._combo_format.addItems(self.FORMAT_OPTIONS)
        self._combo_format.setCurrentIndex(0)
        self._combo_format.setMinimumWidth(130)
        layout.addWidget(self._combo_format)

        style_label = QLabel("样式:")
        layout.addWidget(style_label)

        self._combo_style = QComboBox()
        self._combo_style.addItems(self.STYLE_OPTIONS)
        self._combo_style.setCurrentIndex(0)
        self._combo_style.setMinimumWidth(110)
        layout.addWidget(self._combo_style)

        layout.addStretch()

        return group

    def _create_button_bar(self) -> QHBoxLayout:
        bar = QHBoxLayout()
        bar.setSpacing(8)

        self._btn_export_single = QPushButton("\U0001F4E5 导出当前选中FB")
        self._btn_export_single.setMinimumHeight(32)
        self._btn_export_single.setMinimumWidth(150)
        self._btn_export_single.setProperty("PrimaryBtn", True)
        bar.addWidget(self._btn_export_single)

        self._btn_export_all = QPushButton("\U0001F4E6 批量导出全部FB")
        self._btn_export_all.setMinimumHeight(32)
        self._btn_export_all.setMinimumWidth(150)
        self._btn_export_all.setProperty("SuccessBtn", True)
        bar.addWidget(self._btn_export_all)

        self._btn_export_report = QPushButton("\U0001F4CB 导出检查报告")
        self._btn_export_report.setMinimumHeight(32)
        self._btn_export_report.setMinimumWidth(150)
        self._btn_export_report.setProperty("WarningBtn", True)
        bar.addWidget(self._btn_export_report)

        bar.addStretch()

        self._progress_label = QLabel("")
        self._progress_label.setProperty("treeStatus", True)
        self._progress_label.setMinimumWidth(180)
        bar.addWidget(self._progress_label)

        return bar

    def _create_fb_list_area(self) -> QGroupBox:
        group = QGroupBox("\U0001F4CB 待导出的FB列表")
        group.setProperty("IndustrialGroup", True)

        layout = QVBoxLayout(group)
        layout.setContentsMargins(8, 18, 8, 8)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(6)

        self._chk_select_all = QCheckBox("全选/取消")
        self._chk_select_all.setChecked(True)
        toolbar.addWidget(self._chk_select_all)

        toolbar.addStretch()

        self._lbl_fb_count = QLabel("共 0 个FB")
        self._lbl_fb_count.setProperty("treeStatus", True)
        toolbar.addWidget(self._lbl_fb_count)

        layout.addLayout(toolbar)

        self._fb_table = QTableWidget()
        self._fb_table.setColumnCount(5)
        self._fb_table.setHorizontalHeaderLabels([
            "", "FB名称", "分类", "变量数", "源文件路径",
        ])

        header = self._fb_table.horizontalHeader()
        header.setSectionResizeMode(self.COL_CHECK, QHeaderView.Fixed)
        header.setSectionResizeMode(self.COL_NAME, QHeaderView.Interactive)
        header.setSectionResizeMode(self.COL_CATEGORY, QHeaderView.Fixed)
        header.setSectionResizeMode(self.COL_VAR_COUNT, QHeaderView.Fixed)
        header.setSectionResizeMode(self.COL_FILE_PATH, QHeaderView.Stretch)

        self._fb_table.setColumnWidth(self.COL_CHECK, 34)
        self._fb_table.setColumnWidth(self.COL_NAME, 220)
        self._fb_table.setColumnWidth(self.COL_CATEGORY, 90)
        self._fb_table.setColumnWidth(self.COL_VAR_COUNT, 60)

        self._fb_table.setAlternatingRowColors(True)
        self._fb_table.setSelectionBehavior(QTableWidget.SelectRows)
        self._fb_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._fb_table.verticalHeader().setVisible(False)
        layout.addWidget(self._fb_table)

        return group

    def _create_log_area(self) -> QGroupBox:
        group = QGroupBox("\U0001F4CB 导出日志")
        group.setProperty("IndustrialGroup", True)

        layout = QVBoxLayout(group)
        layout.setContentsMargins(8, 18, 8, 8)

        log_toolbar = QHBoxLayout()
        self._btn_clear_log = QPushButton("清空日志")
        self._btn_clear_log.setMaximumHeight(24)
        self._btn_clear_log.setProperty("ToolBtn", True)
        log_toolbar.addWidget(self._btn_clear_log)
        log_toolbar.addStretch()
        layout.addLayout(log_toolbar)

        self._log_browser = QTextBrowser()
        self._log_browser.setMinimumHeight(120)
        self._log_browser.setOpenExternalLinks(False)
        layout.addWidget(self._log_browser)

        return group

    def _connect_signals(self):
        self._btn_select_dir.clicked.connect(self._on_select_directory)
        self._btn_export_single.clicked.connect(self._on_export_selected)
        self._btn_export_all.clicked.connect(self._on_export_all)
        self._btn_export_report.clicked.connect(self._on_export_report)
        self._btn_clear_log.clicked.connect(lambda: self._log_browser.clear())
        self._chk_select_all.toggled.connect(self._on_toggle_select_all)
        self._fb_table.cellClicked.connect(self._on_table_cell_clicked)

    def set_project_path(self, project_path: str):
        self._project_path = project_path
        self._scan_fb_files(project_path)
        logger.info(f"已设置项目路径: {project_path}")

    def set_output_dir(self, output_dir: str):
        self._output_dir = output_dir
        self._dir_path_label.setText(output_dir)
        logger.info(f"已设置输出目录: {output_dir}")

    def _scan_fb_files(self, project_path: str):
        self._fb_data_list.clear()
        self._fb_table.setRowCount(0)

        project = Path(project_path)
        if not project.exists():
            self._append_log(f"⚠ 项目目录不存在: {project_path}")
            return

        pattern = "**/*.scl"
        scl_files = sorted(project.glob(pattern), key=lambda p: p.name.lower())

        include_syslib = self._chk_include_syslib.isChecked()

        for scl_file in scl_files:
            if not include_syslib and "syslib" in scl_file.parts:
                continue

            try:
                source_text = scl_file.read_text(encoding="utf-8")
                exports = ExcelExporter._parse_scl_source(source_text)
                for exp in exports:
                    category = self._classify_fb(exp.fb_name)
                    fb_entry = {
                        "name": exp.fb_name,
                        "category": category,
                        "var_count": len(exp.variables),
                        "file_path": str(scl_file.resolve()),
                        "checked": True,
                    }
                    self._fb_data_list.append(fb_entry)
            except Exception as e:
                logger.debug(f"扫描跳过 {scl_file.name}: {e}")
                continue

        self._refresh_fb_table()
        self._append_log(
            f"\U0001F50D 扫描完成: 找到 {len(self._fb_data_list)} 个FB/FC"
        )

    @staticmethod
    def _classify_fb(fb_name: str) -> str:
        name_upper = fb_name.upper()
        if name_upper.startswith("FB_TON") or name_upper.startswith("FB_TOF") or name_upper.startswith("FB_TP"):
            return "timer"
        if name_upper.startswith("FB_CTU") or name_upper.startswith("FB_CTD") or name_upper.startswith("FB_CTUD"):
            return "counter"
        if any(kw in name_upper for kw in ("CYLINDER", "VALVE", "MOTOR", "CONVEYOR", "ACTUATOR")):
            return "actuator"
        if any(kw in name_upper for kw in ("SENSOR", "PROBE", "DETECT")):
            return "sensor"
        if "STATION" in name_upper:
            return "station"
        if name_upper.startswith("FC_"):
            return "function"
        return "custom"

    def _refresh_fb_table(self):
        self._fb_table.blockSignals(True)
        self._fb_table.setRowCount(len(self._fb_data_list))

        for row_idx, fb_entry in enumerate(self._fb_data_list):
            chk_item = QTableWidgetItem()
            chk_item.setCheckState(
                Qt.Checked if fb_entry["checked"] else Qt.Unchecked
            )
            chk_item.setTextAlignment(Qt.AlignCenter)
            self._fb_table.setItem(row_idx, self.COL_CHECK, chk_item)

            name_item = QTableWidgetItem(fb_entry["name"])
            name_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            name_item.setToolTip(fb_entry["file_path"])
            self._fb_table.setItem(row_idx, self.COL_NAME, name_item)

            cat_item = QTableWidgetItem(fb_entry["category"])
            cat_item.setTextAlignment(Qt.AlignCenter)
            self._fb_table.setItem(row_idx, self.COL_CATEGORY, cat_item)

            var_item = QTableWidgetItem(str(fb_entry["var_count"]))
            var_item.setTextAlignment(Qt.AlignCenter)
            var_item.setData(Qt.UserRole, fb_entry["var_count"])
            self._fb_table.setItem(row_idx, self.COL_VAR_COUNT, var_item)

            path_item = QTableWidgetItem(fb_entry["file_path"])
            path_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self._fb_table.setItem(row_idx, self.COL_FILE_PATH, path_item)

        self._lbl_fb_count.setText(f"共 {len(self._fb_data_list)} 个FB")
        self._fb_table.blockSignals(False)

    def _get_checked_fbs(self) -> List[Tuple[str, str]]:
        checked = []
        for row_idx in range(self._fb_table.rowCount()):
            chk_item = self._fb_table.item(row_idx, self.COL_CHECK)
            if chk_item and chk_item.checkState() == Qt.Checked:
                name_item = self._fb_table.item(row_idx, self.COL_NAME)
                path_item = self._fb_table.item(row_idx, self.COL_FILE_PATH)
                if name_item and path_item:
                    checked.append((name_item.text(), path_item.text()))
        return checked

    def _get_selected_fb(self) -> Optional[Tuple[str, str]]:
        selected_rows = self._fb_table.selectionModel().selectedRows()
        if not selected_rows:
            return None
        row = selected_rows[0].row()
        name_item = self._fb_table.item(row, self.COL_NAME)
        path_item = self._fb_table.item(row, self.COL_FILE_PATH)
        if name_item and path_item:
            return (name_item.text(), path_item.text())
        return None

    def _on_select_directory(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择Excel导出输出目录",
            self._output_dir or str(Path.home()),
            QFileDialog.ShowDirsOnly,
        )
        if directory:
            self.set_output_dir(directory)
            self._append_log(f"📁 输出目录已设置: {directory}")

    def _on_export_selected(self):
        if not self._output_dir:
            self._append_log("⚠ 请先选择输出目录")
            return

        selected = self._get_selected_fb()
        if not selected:
            self._append_log("⚠ 请先在列表中选中一个FB")
            return

        fb_name, scl_file = selected
        self._start_worker("single", scl_file_path=scl_file)
        self._append_log(f"📥 开始导出选中FB: {fb_name}")

    def _on_export_all(self):
        if not self._output_dir:
            self._append_log("⚠ 请先选择输出目录")
            return

        if not self._project_path:
            self._append_log("⚠ 请先加载项目（调用 set_project_path）")
            return

        checked_fbs = [name for name, _ in self._get_checked_fbs()]
        self._start_worker(
            "batch",
            project_path=self._project_path,
            selected_fbs=checked_fbs,
        )
        total = len(checked_fbs) if checked_fbs else len(self._fb_data_list)
        self._append_log(f"📦 开始批量导出, 目标 {total} 个FB...")

    def _on_export_report(self):
        if not self._output_dir:
            self._append_log("⚠ 请先选择输出目录")
            return

        self._append_log("📋 检查报告导出需要传入检查结果数据")
        self.export_error.emit("未提供检查结果数据，无法导出报告")

    def _on_toggle_select_all(self, checked: bool):
        self._fb_table.blockSignals(True)
        for row_idx in range(self._fb_table.rowCount()):
            chk_item = self._fb_table.item(row_idx, self.COL_CHECK)
            if chk_item:
                chk_item.setCheckState(
                    Qt.Checked if checked else Qt.Unchecked
                )
                if row_idx < len(self._fb_data_list):
                    self._fb_data_list[row_idx]["checked"] = checked
        self._fb_table.blockSignals(False)

    def _on_table_cell_clicked(self, row: int, column: int):
        if column == self.COL_CHECK:
            chk_item = self._fb_table.item(row, self.COL_CHECK)
            if chk_item and row < len(self._fb_data_list):
                self._fb_data_list[row]["checked"] = (
                    chk_item.checkState() == Qt.Checked
                )

    def _start_worker(
        self,
        mode: str,
        project_path: str = "",
        scl_file_path: str = "",
        selected_fbs: Optional[List[str]] = None,
        check_results: Optional[List] = None,
    ):
        if self._export_worker and self._export_worker.isRunning():
            self._export_worker.cancel()
            self._export_worker.finished.connect(
                lambda: self._start_worker(
                    mode, project_path, scl_file_path,
                    selected_fbs, check_results,
                )
            )
            return

        self._set_exporting_state(True)

        self._export_worker = ExportWorker(
            mode=mode,
            project_path=project_path or self._project_path,
            scl_file_path=scl_file_path,
            output_dir=self._output_dir,
            include_syslib=self._chk_include_syslib.isChecked(),
            selected_fbs=selected_fbs,
            check_results=check_results,
        )

        self._export_worker.progress_updated.connect(self._append_log)
        self._export_worker.fb_exported.connect(self._on_fb_exported)
        self._export_worker.batch_completed.connect(self._on_batch_completed)
        self._export_worker.error_occurred.connect(self._on_export_error)
        self._export_worker.start()

    def _on_fb_exported(self, fb_name: str, file_path: str):
        self.export_completed.emit(file_path)
        logger.info(f"FB导出完成: {fb_name} -> {file_path}")

    def _on_batch_completed(self, paths: List[str]):
        self._set_exporting_state(False)
        self.export_all_completed.emit(paths)
        self._progress_label.setText(f"✅ 完成 {len(paths)} 个文件")
        logger.info(f"批量导出完成: {len(paths)} 个文件")

    def _on_export_error(self, error_msg: str):
        self._set_exporting_state(False)
        self._append_log(f"❌ {error_msg}")
        self.export_error.emit(error_msg)
        self._progress_label.setText("❌ 导出失败")
        logger.error(f"导出错误: {error_msg}")

    def _set_exporting_state(self, is_exporting: bool):
        self._btn_export_single.setEnabled(not is_exporting)
        self._btn_export_all.setEnabled(not is_exporting)
        self._btn_export_report.setEnabled(not is_exporting)
        if is_exporting:
            self._progress_label.setText("⏳ 正在导出...")
        else:
            self._progress_label.setText("")

    def _append_log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {message}"
        self._log_browser.append(formatted)

    def load_check_results(self, check_results: List):
        self._check_results_cache = check_results
        self._append_log(
            f"📋 已加载 {len(check_results)} 条检查结果，可导出报告"
        )

    def export_report_with_results(self, check_results: List):
        if not self._output_dir:
            self._append_log("⚠ 请先选择输出目录")
            return
        self._start_worker("report", check_results=check_results)
        self._append_log("📋 开始导出检查报告...")

    def clear_all(self):
        self._fb_data_list.clear()
        self._fb_table.setRowCount(0)
        self._log_browser.clear()
        self._dir_path_label.setText("未选择")
        self._output_dir = ""
        self._project_path = ""
        self._progress_label.setText("")

    def cleanup(self):
        if self._export_worker and self._export_worker.isRunning():
            self._export_worker.cancel()
            self._export_worker.finished.disconnect()
            self._export_worker.wait(3000)
            self._export_worker = None
