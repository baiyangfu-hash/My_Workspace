# -*- coding: utf-8 -*-
"""
自动批量修复面板组件

基于PyQt5实现的自动批量修复功能GUI面板。
集成AutoFixService和多个修复器，提供扫描、预览、执行、回滚的完整流程。

主要功能:
- 工具栏控制: 扫描项目、预览修复、执行修复、回滚操作
- 修复器选择: 复选框控制启用哪些修复器
- 实时统计: 可修复/需确认/已跳过数量展示
- 预览列表: 表格显示所有检测到的问题详情
- 后台任务: 使用QThread避免阻塞UI线程
"""
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QProgressBar,
    QCheckBox,
    QApplication,
    QMessageBox,
    QHeaderView,
    QFrame,
    QSizePolicy,
)
from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    QThread,
    QMutex,
)
from PyQt5.QtGui import QColor, QFont

from src.utils.logger import setup_logger
from src.services.auto_fix_service import (
    AutoFixService,
    FixReport,
    ProjectFixReport,
    FileFixReport,
)

logger = setup_logger(__name__)


class FixWorker(QThread):
    """
    修复工作线程

    在后台线程中执行扫描或修复任务，
    避免长时间操作阻塞UI线程。
    通过信号机制与主界面通信进度和结果。

    Attributes:
        _task_type: 任务类型 (scan/preview/execute/rollback)
        _project_path: 项目根目录路径
        _fixer_ids: 启用的修复器ID列表
        _dry_run: 是否为dry_run模式
        _mutex: 线程安全互斥锁
        _is_cancelled: 取消标志
    """

    progress_updated = pyqtSignal(int, str)
    task_completed = pyqtSignal(str, object)
    error_occurred = pyqtSignal(str)

    def __init__(
        self,
        task_type: str,
        project_path: str,
        fixer_ids: Optional[List[str]] = None,
        dry_run: bool = True,
        rollback_file: str = "",
        rollback_backup: str = "",
        parent=None,
    ):
        super().__init__(parent)
        self._task_type = task_type
        self._project_path = project_path
        self._fixer_ids = fixer_ids or []
        self._dry_run = dry_run
        self._rollback_file = rollback_file
        self._rollback_backup = rollback_backup
        self._mutex = QMutex()
        self._is_cancelled = False
        logger.info(f"修复工作线程初始化完成 - 任务类型: {task_type}")

    def run(self):
        """执行任务的主体方法"""
        try:
            if self._task_type == "scan":
                self._execute_scan()
            elif self._task_type == "preview":
                self._execute_preview()
            elif self._task_type == "execute":
                self._execute_fix()
            elif self._task_type == "rollback":
                self._execute_rollback()
            else:
                self.error_occurred.emit(f"未知任务类型: {self._task_type}")

        except Exception as e:
            error_msg = f"修复任务发生异常: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)

    def _execute_scan(self):
        """执行项目扫描任务"""
        try:
            self.progress_updated.emit(10, "正在初始化修复器...")

            self._mutex.lock()
            if self._is_cancelled:
                self._mutex.unlock()
                return
            self._mutex.unlock()

            self.progress_updated.emit(30, "正在扫描项目文件...")

            report = AutoFixService.scan_project(
                self._project_path,
                fixer_ids=self._fixer_ids if self._fixer_ids else None,
            )

            self.progress_updated.emit(100, "扫描完成")
            self.task_completed.emit("scan", report)

            logger.info(
                f"扫描完成 - 文件数: {report.total_files_scanned}, "
                f"问题数: {report.total_issues_found}"
            )

        except Exception as e:
            logger.exception(f"扫描任务异常: {e}")
            self.error_occurred.emit(str(e))

    def _execute_preview(self):
        """执行预览修复任务（dry_run模式）"""
        try:
            self.progress_updated.emit(10, "正在生成修复预览...")

            self._mutex.lock()
            if self._is_cancelled:
                self._mutex.unlock()
                return
            self._mutex.unlock()

            self.progress_updated.emit(30, "正在分析可修复问题...")

            result = AutoFixService.fix_project(
                self._project_path,
                fixer_ids=self._fixer_ids,
                dry_run=True,
            )

            self.progress_updated.emit(100, "预览生成完成")
            self.task_completed.emit("preview", result)

            logger.info(
                f"预览完成 - 处理文件: {result.total_files_processed}, "
                f"问题数: {result.total_issues_fixed}"
            )

        except Exception as e:
            logger.exception(f"预览任务异常: {e}")
            self.error_occurred.emit(str(e))

    def _execute_fix(self):
        """执行实际修复任务"""
        try:
            self.progress_updated.emit(10, "正在准备修复...")

            self._mutex.lock()
            if self._is_cancelled:
                self._mutex.unlock()
                return
            self._mutex.unlock()

            self.progress_updated.emit(30, "正在执行批量修复...")

            result = AutoFixService.fix_project(
                self._project_path,
                fixer_ids=self._fixer_ids,
                dry_run=False,
            )

            self.progress_updated.emit(100, "修复执行完成")
            self.task_completed.emit("execute", result)

            logger.info(
                f"修复完成 - 处理文件: {result.total_files_processed}, "
                f"修复问题: {result.total_issues_fixed}, "
                f"修改文件: {result.total_files_modified}"
            )

        except Exception as e:
            logger.exception(f"修复任务异常: {e}")
            self.error_occurred.emit(str(e))

    def _execute_rollback(self):
        """执行回滚任务"""
        try:
            self.progress_updated.emit(10, "正在准备回滚...")

            self._mutex.lock()
            if self._is_cancelled:
                self._mutex.unlock()
                return
            self._mutex.unlock()

            self.progress_updated.emit(50, f"正在恢复文件: {Path(self._rollback_file).name}")

            success = AutoFixService.rollback_file(
                self._rollback_file,
                self._rollback_backup,
            )

            self.progress_updated.emit(100, "回滚完成")
            self.task_completed.emit(
                "rollback",
                {
                    "success": success,
                    "file_path": self._rollback_file,
                },
            )

            logger.info(f"回滚完成 - 文件: {self._rollback_file}, 成功: {success}")

        except Exception as e:
            logger.exception(f"回滚任务异常: {e}")
            self.error_occurred.emit(str(e))

    def cancel(self):
        """请求取消当前任务"""
        self._mutex.lock()
        self._is_cancelled = True
        self._mutex.unlock()
        logger.info("收到取消修复任务请求")


class AutoFixPanel(QWidget):
    """
    自动批量修复面板主组件

    提供完整的PLC代码自动修复UI界面，
    包括工具栏控制、修复器选择、统计摘要、预览列表。

    Signals:
        fix_scan_completed: 扫描完成时发出，携带FixReport对象
        fix_executed: 修复执行完成时发出，携带ProjectFixReport对象
        fix_rollback_done: 回滚完成时发出，携带文件路径
        source_jump_requested: 用户请求跳转到源码位置时发出

    Usage:
        panel = AutoFixPanel()
        panel.set_project("/path/to/project")
    """

    fix_scan_completed = pyqtSignal(object)
    fix_executed = pyqtSignal(object)
    fix_rollback_done = pyqtSignal(str)
    source_jump_requested = pyqtSignal(str, int)

    STATUS_COLORS = {
        "pending": "#E0E0E0",
        "fixed": "#E8F5E9",
        "skipped": "#FFF3E0",
        "error": "#FFEBEE",
        "confirm_needed": "#E3F2FD",
    }

    STATUS_NAMES = {
        "pending": "待修复",
        "fixed": "已修复",
        "skipped": "已跳过",
        "error": "错误",
        "confirm_needed": "需确认",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_report: Optional[FixReport] = None
        self._current_result: Optional[ProjectFixReport] = None
        self._fix_worker: Optional[FixWorker] = None
        self._current_project_path: Optional[str] = None
        self._fixer_checkboxes: Dict[str, QCheckBox] = {}
        self._all_issues: List[Any] = []
        self._init_ui()
        self._connect_signals()
        self._load_available_fixers()
        logger.info("自动批量修复面板初始化完成")

    def _init_ui(self):
        """初始化UI布局"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        toolbar = self._create_toolbar()
        main_layout.addLayout(toolbar)

        progress_bar = self._create_progress_area()
        main_layout.addLayout(progress_bar)

        fixer_group = self._create_fixer_selection_area()
        main_layout.addWidget(fixer_group)

        stats_group = self._create_stats_area()
        main_layout.addWidget(stats_group)

        table_group = self._create_preview_table_area()
        main_layout.addWidget(table_group, stretch=1)

    def _create_toolbar(self) -> QHBoxLayout:
        """创建工具栏布局"""
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        title_label = QLabel("\U0001F527 \u81EA\u52A8\u6279\u91CF\u4FEE\u590D\u9762\u677F")
        title_label.setProperty("panelTitle", True)
        toolbar.addWidget(title_label)

        toolbar.addStretch()

        scope_label = "\u8303\u56F4:"
        scope_label_widget = QLabel(scope_label)
        toolbar.addWidget(scope_label_widget)

        self._scope_combo = QComboBox()
        self._scope_combo.addItems([
            "\u6574\u4E2A\u9879\u76EE",
            "\u5F53\u524D\u6587\u4EF6",
        ])
        self._scope_combo.setMinimumWidth(100)
        toolbar.addWidget(self._scope_combo)

        self._btn_scan = QPushButton("\U0001F50D \u626B\u63CF\u9879\u76EE")
        self._btn_scan.setMinimumHeight(32)
        self._btn_scan.setMinimumWidth(90)
        self._btn_scan.setProperty("PrimaryBtn", True)
        toolbar.addWidget(self._btn_scan)

        self._btn_preview = QPushButton("\U0001F441 \u9884\u89C8\u4FEE\u590D")
        self._btn_preview.setMinimumHeight(32)
        self._btn_preview.setMinimumWidth(90)
        self._btn_preview.setProperty("WarningBtn", True)
        toolbar.addWidget(self._btn_preview)

        self._btn_execute = QPushButton("\U0001F4E5 \u6267\u884C\u4FEE\u590D")
        self._btn_execute.setMinimumHeight(32)
        self._btn_execute.setMinimumWidth(90)
        self._btn_execute.setProperty("SuccessBtn", True)
        toolbar.addWidget(self._btn_execute)

        self._btn_rollback = QPushButton("\U0001F504 \u56DE\u6EDA")
        self._btn_rollback.setMinimumHeight(32)
        self._btn_rollback.setMinimumWidth(70)
        self._btn_rollback.setProperty("DangerBtn", True)
        toolbar.addWidget(self._btn_rollback)

        return toolbar

    def _create_progress_area(self) -> QHBoxLayout:
        """创建进度条区域"""
        progress_layout = QHBoxLayout()
        progress_layout.setSpacing(8)

        self._progress_bar = QProgressBar()
        self._progress_bar.setVisible(False)
        self._progress_bar.setMinimumHeight(20)
        self._progress_bar.setTextVisible(True)
        self._progress_bar.setFormat("%p%")
        progress_layout.addWidget(self._progress_bar)

        self._status_label = QLabel("\u51C6\u5907\u5C31\u7EEA")
        self._status_label.setProperty("treeStatus", True)
        self._status_label.setMinimumWidth(200)
        progress_layout.addWidget(self._status_label)

        progress_layout.addStretch()

        return progress_layout

    def _create_fixer_selection_area(self) -> QGroupBox:
        """创建修复器选择区域"""
        fixer_group = QGroupBox("\U0001F4CB \u53EF\u7528\u4FEE\u590D\u5668")
        fixer_group.setProperty("IndustrialGroup", True)

        fixer_layout = QHBoxLayout(fixer_group)
        fixer_layout.setContentsMargins(10, 15, 10, 10)
        fixer_layout.setSpacing(20)

        self._fixer_container_layout = fixer_layout

        return fixer_group

    def _create_stats_area(self) -> QGroupBox:
        """创建统计摘要区域"""
        stats_group = QGroupBox("\U0001F4CA \u4FEE\u590D\u7EDF\u8BA1")
        stats_group.setProperty("IndustrialGroup", True)

        stats_layout = QHBoxLayout(stats_group)
        stats_layout.setContentsMargins(10, 15, 10, 10)
        stats_layout.setSpacing(10)

        self._stat_fixable = self._create_stat_card(
            "\u53EF\u4FEE\u590D", "0", "\u274C"
        )
        stats_layout.addWidget(self._stat_fixable)

        self._stat_confirm = self._create_stat_card(
            "\u9700\u786E\u8BA4", "0", "\u26A0\uFE0F"
        )
        stats_layout.addWidget(self._stat_confirm)

        self._stat_skipped = self._create_stat_card(
            "\u5DF2\u8DF3\u8FC7", "0", "\u2705"
        )
        stats_layout.addWidget(self._stat_skipped)

        return stats_group

    @staticmethod
    def _create_stat_card(
        title: str, value: str, icon: str
    ) -> QFrame:
        """创建单个统计卡片"""
        card = QFrame()
        card.setProperty("StatCard", True)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        header = QHBoxLayout()
        icon_label = QLabel(icon)
        header.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setProperty("statCardTitle", True)
        header.addWidget(title_label)
        header.addStretch()
        layout.addLayout(header)

        value_label = QLabel(value)
        value_label.setObjectName("value_label")
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setProperty("valueLabel", True)
        layout.addWidget(value_label)

        return card

    def _update_stat_card(self, card: QFrame, new_value: str):
        """更新统计卡片的数值"""
        value_label = card.findChild(QLabel, "value_label")
        if value_label:
            value_label.setText(new_value)

    def _create_preview_table_area(self) -> QGroupBox:
        """创建修复预览表格区域"""
        table_group = QGroupBox("\U0001F4DD \u4FEE\u590D\u9884\u89C8\u5217\u8868")
        table_group.setProperty("IndustrialGroup", True)

        table_layout = QVBoxLayout(table_group)
        table_layout.setContentsMargins(8, 18, 8, 8)

        self._preview_table = QTableWidget()
        self._preview_table.setColumnCount(5)
        self._preview_table.setHorizontalHeaderLabels([
            "\u6587\u4EF6\u540D",
            "\u884C\u53F7",
            "\u539F\u59CB\u6587\u672C",
            "\u5EFA\u8BAE\u6587\u672C",
            "\u72B6\u6001",
        ])

        column_widths = [180, 60, 200, 200, 80]
        for i, width in enumerate(column_widths):
            self._preview_table.setColumnWidth(i, width)

        self._preview_table.setAlternatingRowColors(True)
        self._preview_table.setSelectionBehavior(QTableWidget.SelectRows)
        self._preview_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._preview_table.verticalHeader().setVisible(False)

        header = self._preview_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)

        table_layout.addWidget(self._preview_table)

        self._table_count_label = QLabel(
            "\u5171 0 \u6761\u4FEE\u590D\u9879"
        )
        self._table_count_label.setProperty("treeStatus", True)
        self._table_count_label.setAlignment(
            Qt.AlignRight | Qt.AlignVCenter
        )
        table_layout.addWidget(self._table_count_label)

        return table_group

    def _connect_signals(self):
        """连接所有信号槽"""
        self._btn_scan.clicked.connect(self._on_scan_clicked)
        self._btn_preview.clicked.connect(self._on_preview_clicked)
        self._btn_execute.clicked.connect(self._on_execute_clicked)
        self._btn_rollback.clicked.connect(self._on_rollback_clicked)

        self._preview_table.itemDoubleClicked.connect(
            self._on_table_item_double_clicked
        )

    def _load_available_fixers(self):
        """加载可用修复器并创建复选框"""
        try:
            fixers_info = AutoFixService.get_available_fixers()

            while self._fixer_container_layout.count():
                item = self._fixer_container_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            self._fixer_checkboxes.clear()

            for fixer_info in fixers_info:
                fixer_id = fixer_info.get("fixer_id", "")
                fixer_name = fixer_info.get("name", fixer_id)
                is_safe = fixer_info.get("is_safe", True)
                description = fixer_info.get("description", "")

                checkbox = QCheckBox(f"{fixer_name} ({fixer_id})")
                checkbox.setChecked(True)
                checkbox.setToolTip(description)

                safe_icon = "\U0001F511" if is_safe else "\u26A0\uFE0F"
                label_text = f"{safe_icon} {fixer_name}\n({fixer_id})"
                checkbox.setText(label_text)

                self._fixer_container_layout.addWidget(checkbox)
                self._fixer_checkboxes[fixer_id] = checkbox

            self._fixer_container_layout.addStretch()

            logger.info(f"加载了 {len(fixers_info)} 个修复器")

        except Exception as e:
            logger.error(f"加载修复器失败: {e}", exc_info=True)

    def _get_selected_fixer_ids(self) -> List[str]:
        """获取用户选中的修复器ID列表"""
        selected = []
        for fixer_id, checkbox in self._fixer_checkboxes.items():
            if checkbox.isChecked():
                selected.append(fixer_id)
        return selected

    def set_project(self, project_path: str):
        """设置当前项目路径"""
        self._current_project_path = project_path
        logger.info(f"设置项目路径: {project_path}")

    def _set_working_state(self, is_working: bool):
        """设置工作中的UI状态"""
        self._btn_scan.setEnabled(not is_working)
        self._btn_preview.setEnabled(not is_working)
        self._btn_execute.setEnabled(not is_working)
        self._btn_rollback.setEnabled(not is_working)

        self._progress_bar.setVisible(is_working)

        if is_working:
            self._status_label.setText("\u6B63\u5728\u5904\u7406...")
            self._progress_bar.setValue(0)

    def _start_worker(self, task_type: str, **kwargs):
        """启动后台工作线程"""
        if self._fix_worker and self._fix_worker.isRunning():
            self._fix_worker.cancel()
            self._fix_worker.finished.connect(
                lambda: self._start_worker(task_type, **kwargs)
            )
            return

        self._set_working_state(True)

        self._fix_worker = FixWorker(
            task_type=task_type,
            project_path=self._current_project_path or "",
            **kwargs,
        )

        self._fix_worker.progress_updated.connect(
            self._on_progress_updated
        )
        self._fix_worker.task_completed.connect(
            self._on_task_completed
        )
        self._fix_worker.error_occurred.connect(
            self._on_task_error
        )

        self._fix_worker.start()

    def _on_scan_clicked(self):
        """处理扫描按钮点击事件"""
        if not self._current_project_path:
            self._show_warning("\u8BF7\u5148\u6253\u5F00\u4E00\u4E2A\u9879\u76EE")
            return

        fixer_ids = self._get_selected_fixer_ids()
        if not fixer_ids:
            self._show_warning("\u8BF7\u81F3\u5C11\u9009\u62E9\u4E00\u4E2A\u4FEE\u590D\u5668")
            return

        self._clear_table()
        self._start_worker("scan", fixer_ids=fixer_ids)

    def _on_preview_clicked(self):
        """处理预览按钮点击事件"""
        if not self._current_project_path:
            self._show_warning("\u8BF7\u5148\u6253\u5F00\u4E00\u4E2A\u9879\u76EE")
            return

        fixer_ids = self._get_selected_fixer_ids()
        if not fixer_ids:
            self._show_warning("\u8BF7\u81F3\u5C11\u9009\u62E9\u4E00\u4E2A\u4FEE\u590D\u5668")
            return

        self._clear_table()
        self._start_worker("preview", fixer_ids=fixer_ids, dry_run=True)

    def _on_execute_clicked(self):
        """处理执行修复按钮点击事件"""
        if not self._current_project_path:
            self._show_warning("\u8BF7\u5148\u6253\u5F00\u4E00\u4E2A\u9879\u76EE")
            return

        fixer_ids = self._get_selected_fixer_ids()
        if not fixer_ids:
            self._show_warning("\u8BF7\u81F3\u5C11\u9009\u62E9\u4E00\u4E2A\u4FEE\u590D\u5668")
            return

        reply = QMessageBox.question(
            self,
            "\u786E\u8BA4\u4FEE\u590D",
            (
                "\u60A8\u786E\u5B9A\u8981\u6267\u884C\u6279\u91CF\u4FEE\u590D\u5417?\n\n"
                "\u4FEE\u590D\u524D\u5C06\u81EA\u52A8\u521B\u5EFA .bak \u5907\u4EFD\u6587\u4EF6\u3002\n"
                "\u53EF\u4EE5\u901A\u8FC7\u56DE\u6EDA\u6309\u94AE\u6062\u590D\u3002"
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self._start_worker("execute", fixer_ids=fixer_ids, dry_run=False)

    def _on_rollback_clicked(self):
        """处理回滚按钮点击事件"""
        if not self._current_result or not self._current_result.file_reports:
            self._show_warning("\u6CA1\u6709\u53EF\u56DE\u6EDA\u7684\u4FEE\u590D\u8BB0\u5F55")
            return

        reply = QMessageBox.question(
            self,
            "\u786E\u8BA4\u56DE\u6EDA",
            (
                "\u786E\u5B9A\u8981\u4ECE\u5907\u4EFD\u6587\u4EF6\u56DE\u6EDA\u5417?\n\n"
                "\u8FD9\u5C06\u64A4\u9500\u6700\u8FD1\u4E00\u6B21\u4FEE\u590D\u64CD\u4F5C\u7684\u6240\u6709\u53D8\u66F4\u3002"
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            latest_report = self._current_result.file_reports[-1]
            file_path = latest_report.file_path
            backup_path = latest_report.backup_path

            self._start_worker(
                "rollback",
                rollback_file=file_path,
                rollback_backup=backup_path,
            )

    def _on_progress_updated(self, progress: int, message: str):
        """处理进度更新信号"""
        self._progress_bar.setValue(progress)
        self._status_label.setText(message)

    def _on_task_completed(self, task_type: str, result: Any):
        """处理任务完成信号"""
        self._set_working_state(False)

        if task_type == "scan":
            self._handle_scan_result(result)
        elif task_type == "preview":
            self._handle_preview_result(result)
        elif task_type == "execute":
            self._handle_execute_result(result)
        elif task_type == "rollback":
            self._handle_rollback_result(result)

    def _handle_scan_result(self, report: FixReport):
        """处理扫描结果"""
        self._current_report = report
        self._all_issues = []

        for file_report in report.file_reports:
            for issue in file_report.issues:
                self._all_issues.append({
                    "file_path": file_report.file_path,
                    "issue": issue,
                    "status": "pending",
                })

        self._populate_table_from_issues()
        self._update_statistics_from_issues()
        self._status_label.setText(
            f"\u626B\u63CF\u5B8C\u6210 - "
            f"{report.total_files_scanned} \u4E2A\u6587\u4EF6, "
            f"{report.total_issues_found} \u4E2A\u95EE\u9898"
        )

        self.fix_scan_completed.emit(report)
        logger.info(f"扫描结果已更新 - 共 {len(self._all_issues)} 个问题")

    def _handle_preview_result(self, result: ProjectFixReport):
        """处理预览结果"""
        self._current_result = result
        self._all_issues = []

        for file_report in result.file_reports:
            for idx, issue in enumerate(file_report.issues):
                status = "pending"
                if idx < len(file_report.results):
                    result_item = file_report.results[idx]
                    if not result_item.success:
                        status = "skipped"

                self._all_issues.append({
                    "file_path": file_report.file_path,
                    "issue": issue,
                    "status": status,
                })

        self._populate_table_from_issues()
        self._update_statistics_from_issues()
        self._status_label.setText(
            f"\u9884\u89C8\u5B8C\u6210 - "
            f"\u9884\u8BA1\u4FEE\u590D {result.total_issues_fixed} \u4E2A\u95EE\u9898"
        )

        self.fix_executed.emit(result)
        logger.info(f"预览结果已更新 - 共 {len(self._all_issues)} 个问题")

    def _handle_execute_result(self, result: ProjectFixReport):
        """处理执行修复结果"""
        self._current_result = result
        self._all_issues = []

        for file_report in result.file_reports:
            for idx, issue in enumerate(file_report.issues):
                status = "fixed"
                if idx < len(file_report.results):
                    result_item = file_report.results[idx]
                    if result_item.success:
                        status = "fixed"
                    else:
                        status = "error"

                self._all_issues.append({
                    "file_path": file_report.file_path,
                    "issue": issue,
                    "status": status,
                })

        self._populate_table_from_issues()
        self._update_statistics_from_issues()

        mode_str = "\u5B9E\u9645\u4FEE\u590D"
        self._status_label.setText(
            f"{mode_str}\u5B8C\u6210 - "
            f"\u4FEE\u590D {result.total_issues_fixed} \u4E2A, "
            f"\u4FEE\u6539 {result.total_files_modified} \u4E2A\u6587\u4EF6"
        )

        self.fix_executed.emit(result)
        logger.info(
            f"修复结果已更新 - 修复: {result.total_issues_fixed}, "
            f"修改文件: {result.total_files_modified}"
        )

    def _handle_rollback_result(self, result: Dict[str, Any]):
        """处理回滚结果"""
        success = result.get("success", False)
        file_path = result.get("file_path", "")

        if success:
            self._status_label.setText(
                f"\u56DE\u6EDA\u6210\u529F - {Path(file_path).name}"
            )
            self.fix_rollback_done.emit(file_path)
            logger.info(f"回滚成功: {file_path}")
        else:
            self._status_label.setText("\u56DE\u6EDA\u5931\u8D25")
            self._show_error("\u56DE\u6EDA\u5931\u8D25\uFF0C\u8BF7\u68C0\u67E5\u5907\u4EFD\u6587\u4EF6\u662F\u5426\u5B58\u5728")
            logger.warning(f"回滚失败: {file_path}")

    def _populate_table_from_issues(self):
        """根据问题列表填充表格"""
        self._preview_table.setRowCount(len(self._all_issues))

        for row, item_data in enumerate(self._all_issues):
            issue = item_data["issue"]
            status = item_data["status"]

            file_name = Path(item_data["file_path"]).name
            file_name_item = QTableWidgetItem(file_name)
            file_name_item.setToolTip(item_data["file_path"])
            file_name_item.setData(Qt.UserRole, item_data["file_path"])
            self._preview_table.setItem(row, 0, file_name_item)

            line_number = str(issue.line_number) if issue.line_number > 0 else "-"
            line_item = QTableWidgetItem(line_number)
            line_item.setData(Qt.UserRole, issue.line_number)
            self._preview_table.setItem(row, 1, line_item)

            original_text = issue.original_text or "-"
            if len(original_text) > 40:
                original_text = original_text[:37] + "..."
            original_item = QTableWidgetItem(original_text)
            original_item.setToolTip(issue.original_text or "")
            self._preview_table.setItem(row, 2, original_item)

            suggested_text = issue.suggested_text or "-"
            if len(suggested_text) > 40:
                suggested_text = suggested_text[:37] + "..."
            suggested_item = QTableWidgetItem(suggested_text)
            suggested_item.setToolTip(issue.suggested_text or "")
            self._preview_table.setItem(row, 3, suggested_item)

            status_name = self.STATUS_NAMES.get(status, status)
            status_item = QTableWidgetItem(status_name)
            bg_color = self.STATUS_COLORS.get(status, "#FFFFFF")
            status_item.setBackground(QColor(bg_color))
            self._preview_table.setItem(row, 4, status_item)

        count = len(self._all_issues)
        self._table_count_label.setText(f"\u5171 {count} \u6761\u4FEE\u590D\u9879")

    def _update_statistics_from_issues(self):
        """根据问题列表更新统计数据"""
        fixable = 0
        confirm = 0
        skipped = 0

        for item_data in self._all_issues:
            status = item_data["status"]
            if status == "pending":
                fixable += 1
            elif status == "confirm_needed":
                confirm += 1
            elif status in ("skipped", "error"):
                skipped += 1

        self._update_stat_card(self._stat_fixable, str(fixable))
        self._update_stat_card(self._stat_confirm, str(confirm))
        self._update_stat_card(self._stat_skipped, str(skipped))

    def _on_table_item_double_clicked(self, item: QTableWidgetItem):
        """处理表格项双击事件，触发源码跳转"""
        row = item.row()
        if row < 0 or row >= len(self._all_issues):
            return

        item_data = self._all_issues[row]
        file_path = item_data["file_path"]
        line_number = item_data["issue"].line_number

        if file_path and line_number > 0:
            self.source_jump_requested.emit(file_path, line_number)
            logger.info(f"请求跳转到源码: {file_path}:{line_number}")

    def _on_task_error(self, error_message: str):
        """处理任务错误信号"""
        self._set_working_state(False)
        self._status_label.setText(f"\u274C \u9519\u8BEF: {error_message}")
        self._show_error(f"\u64CD\u4F5C\u51FA\u9519:\n{error_message}")
        logger.error(f"任务出错: {error_message}")

    def _clear_table(self):
        """清空表格数据"""
        self._preview_table.setRowCount(0)
        self._all_issues = []
        self._table_count_label.setText("\u5171 0 \u6761\u4FEE\u590D\u9879")

        self._update_stat_card(self._stat_fixable, "0")
        self._update_stat_card(self._stat_confirm, "0")
        self._update_stat_card(self._stat_skipped, "0")

    def _show_warning(self, message: str):
        """显示警告对话框"""
        QMessageBox.warning(self, "\u8B66\u544A", message)

    def _show_error(self, message: str):
        """显示错误对话框"""
        QMessageBox.critical(self, "\u9519\u8BEF", message)

    def get_current_report(self) -> Optional[FixReport]:
        """获取当前的扫描报告"""
        return self._current_report

    def get_current_result(self) -> Optional[ProjectFixReport]:
        """获取当前的修复结果"""
        return self._current_result

    def clear_all(self):
        """公开接口：清空所有数据和UI状态"""
        self._clear_table()
        self._current_report = None
        self._current_result = None
        self._status_label.setText("\u51C6\u5907\u5C31\u7EEA")

    def cleanup(self):
        """清理工作线程资源，窗口关闭前调用"""
        if self._fix_worker and self._fix_worker.isRunning():
            self._fix_worker.cancel()
            self._fix_worker.finished.disconnect()
            self._fix_worker.wait(2000)
            self._fix_worker = None
