# -*- coding: utf-8 -*-
"""
SyncController - 变更管理功能控制器

负责版本检查/CHG生成/IFC生成的 UI 交互逻辑，
以及生成后的审核→回写工作流闭环。
"""
from __future__ import annotations

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QDialog, QDialogButtonBox, QMessageBox,
    QProgressDialog, QTextBrowser, QVBoxLayout,
)

from src.sync.sync_engine import SyncEngine
from src.ui.dialogs.sync_result_dialog import SyncResultDialog
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class _VersionCheckWorker(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, project_path: str, parent=None):
        super().__init__(parent)
        self._project_path = project_path

    def run(self):
        try:
            report = SyncEngine.run_check(self._project_path)
            self.finished.emit(report)
        except Exception as e:
            self.error.emit(str(e))


class _GenerateDocWorker(QThread):
    finished = pyqtSignal(str, str)
    error = pyqtSignal(str, str)

    def __init__(self, project_path: str, doc_type: str, parent=None):
        super().__init__(parent)
        self._project_path = project_path
        self._doc_type = doc_type

    def run(self):
        try:
            if self._doc_type == "chg":
                output_path = SyncEngine.run_generate_chg(self._project_path)
            else:
                output_path = SyncEngine.run_generate_ifc(self._project_path)
            self.finished.emit(output_path, self._doc_type)
        except Exception as e:
            self.error.emit(str(e), self._doc_type)


class SyncController:
    """变更管理功能控制器"""

    def __init__(self, main_window):
        self._main_window = main_window

    def _get_current_project_path(self) -> str:
        if hasattr(self._main_window, '_project_tree_widget') and self._main_window._project_tree_widget:
            current = self._main_window._project_tree_widget.current_project
            if current and current.path:
                return current.path
        return ''

    def _notify_project_tree_refresh(self):
        try:
            tree = getattr(self._main_window, '_project_tree_widget', None)
            if tree and hasattr(tree, 'refresh_tree'):
                tree.refresh_tree()
        except Exception as e:
            logger.warning(f"项目树刷新失败: {e}")

    def on_sync_version_check(self):
        project_path = self._get_current_project_path()
        if not project_path:
            QMessageBox.information(
                self._main_window, "版本检查",
                "请先打开一个项目再执行版本检查。"
            )
            return

        progress = QProgressDialog("正在执行版本检查...", None, 0, 0, self._main_window)
        progress.setWindowTitle("版本一致性检查")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setCancelButton(None)
        progress.show()

        self._check_worker = _VersionCheckWorker(project_path, self._main_window)
        self._check_worker.finished.connect(
            lambda report: self._on_version_check_done(report, progress)
        )
        self._check_worker.error.connect(
            lambda err: self._on_version_check_error(err, progress)
        )
        self._check_worker.start()

    def _on_version_check_done(self, report, progress: QProgressDialog):
        progress.close()
        dialog = QDialog(self._main_window)
        dialog.setWindowTitle("版本一致性检查报告")
        dialog.resize(700, 500)

        layout = QVBoxLayout(dialog)
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(SyncEngine.format_version_report_html(report))
        layout.addWidget(browser)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)

        dialog.exec_()

    def _on_version_check_error(self, err: str, progress: QProgressDialog):
        progress.close()
        logger.error(f"版本检查失败: {err}")
        QMessageBox.critical(self._main_window, "版本检查失败", err)

    def on_sync_generate_chg(self):
        project_path = self._get_current_project_path()
        if not project_path:
            QMessageBox.information(
                self._main_window, "生成CHG文档",
                "请先打开一个项目再生成CHG文档。"
            )
            return

        progress = QProgressDialog("正在生成CHG文档...", None, 0, 0, self._main_window)
        progress.setWindowTitle("CHG文档生成")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setCancelButton(None)
        progress.show()

        self._gen_worker = _GenerateDocWorker(project_path, "chg", self._main_window)
        self._gen_worker.finished.connect(
            lambda output_path, doc_type: self._on_generate_done(
                output_path, doc_type, progress
            )
        )
        self._gen_worker.error.connect(
            lambda err, doc_type: self._on_generate_error(err, doc_type, progress)
        )
        self._gen_worker.start()

    def on_sync_generate_ifc(self):
        project_path = self._get_current_project_path()
        if not project_path:
            QMessageBox.information(
                self._main_window, "生成IFC文档",
                "请先打开一个项目再生成IFC文档。"
            )
            return

        progress = QProgressDialog("正在生成IFC文档...", None, 0, 0, self._main_window)
        progress.setWindowTitle("IFC文档生成")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setCancelButton(None)
        progress.show()

        self._gen_worker = _GenerateDocWorker(project_path, "ifc", self._main_window)
        self._gen_worker.finished.connect(
            lambda output_path, doc_type: self._on_generate_done(
                output_path, doc_type, progress
            )
        )
        self._gen_worker.error.connect(
            lambda err, doc_type: self._on_generate_error(err, doc_type, progress)
        )
        self._gen_worker.start()

    def _on_generate_done(self, output_path: str, doc_type: str, progress: QProgressDialog):
        progress.close()
        title = "CHG文档生成结果" if doc_type == "chg" else "IFC文档生成结果"
        self._show_sync_result(output_path, doc_type, title)

    def _on_generate_error(self, err: str, doc_type: str, progress: QProgressDialog):
        progress.close()
        doc_name = "CHG" if doc_type == "chg" else "IFC"
        logger.error(f"生成{doc_name}文档失败: {err}")
        QMessageBox.critical(self._main_window, f"生成{doc_name}失败", err)

    def _show_sync_result(self, output_path: str, doc_type: str, title: str):
        dialog = SyncResultDialog(
            self._main_window, output_path, title, doc_type=doc_type
        )
        dialog.exec_()

        action = dialog.get_action()
        if action == SyncResultDialog.ACTION_WRITEBACK:
            self._do_writeback(output_path, doc_type)

    def _do_writeback(self, output_path: str, doc_type: str):
        project_path = self._get_current_project_path()
        if not project_path:
            QMessageBox.warning(
                self._main_window, "回写失败",
                "无法获取当前项目路径，回写操作已取消。"
            )
            return

        try:
            written = SyncEngine.writeback_to_project(
                output_path, project_path, doc_type
            )
            if written:
                file_list = "\n".join(written)
                QMessageBox.information(
                    self._main_window, "回写成功",
                    f"已回写 {len(written)} 个文件到项目目录:\n{file_list}"
                )
                self._notify_project_tree_refresh()
                logger.info(f"回写完成: {len(written)} 个文件")
            else:
                QMessageBox.information(
                    self._main_window, "回写结果",
                    "源目录无文件可回写。"
                )
        except Exception as e:
            logger.error(f"回写失败: {e}", exc_info=True)
            QMessageBox.critical(self._main_window, "回写失败", str(e))
