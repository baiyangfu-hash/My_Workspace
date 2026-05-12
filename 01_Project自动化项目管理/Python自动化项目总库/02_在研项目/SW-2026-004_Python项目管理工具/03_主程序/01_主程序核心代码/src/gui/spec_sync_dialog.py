# -*- coding: utf-8 -*-
"""
规范同步对话框模块
提供规范检查、同步的可视化界面
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QTextEdit, QProgressBar,
    QSplitter, QMessageBox, QCheckBox, QComboBox, QLineEdit
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

from src.core.spec_manager import SpecManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class SyncWorker(QThread):
    """同步工作线程"""
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, spec_manager, spec_name=None, backup=True):
        super().__init__()
        self.spec_manager = spec_manager
        self.spec_name = spec_name
        self.backup = backup
    
    def run(self):
        try:
            if self.spec_name:
                result = self.spec_manager.sync_spec(self.spec_name, self.backup)
            else:
                result = self.spec_manager.sync_all_specs()
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class SpecSyncDialog(QDialog):
    """规范同步对话框"""
    
    def __init__(self, parent=None):
        """
        初始化规范同步对话框
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self.spec_manager = SpecManager()
        self.check_results = None
        self.sync_worker = None
        
        # 设置窗口属性
        self.setWindowTitle("规范同步中心")
        self.setMinimumSize(900, 700)
        
        # 创建UI组件
        self._create_ui()
        
        # 加载初始数据
        self._load_initial_data()
    
    def _create_ui(self):
        """创建UI组件"""
        main_layout = QVBoxLayout(self)
        
        # 顶部工具栏
        toolbar = QHBoxLayout()
        
        self.check_btn = QPushButton("检查更新")
        self.check_btn.clicked.connect(self._check_updates)
        toolbar.addWidget(self.check_btn)
        
        self.sync_all_btn = QPushButton("同步所有")
        self.sync_all_btn.clicked.connect(self._sync_all_specs)
        self.sync_all_btn.setEnabled(False)
        toolbar.addWidget(self.sync_all_btn)
        
        self.backup_checkbox = QCheckBox("备份旧版本")
        self.backup_checkbox.setChecked(True)
        toolbar.addWidget(self.backup_checkbox)
        
        toolbar.addStretch()
        
        main_layout.addLayout(toolbar)
        
        # 分割器
        splitter = QSplitter(Qt.Vertical)
        
        # 规范列表
        specs_group = QGroupBox("规范状态")
        specs_layout = QVBoxLayout(specs_group)
        
        self.specs_table = QTableWidget()
        self.specs_table.setColumnCount(5)
        self.specs_table.setHorizontalHeaderLabels(["规范名称", "当前版本", "最新版本", "状态", "操作"])
        self.specs_table.setColumnWidth(0, 200)
        self.specs_table.setColumnWidth(1, 100)
        self.specs_table.setColumnWidth(2, 100)
        self.specs_table.setColumnWidth(3, 100)
        self.specs_table.setColumnWidth(4, 100)
        specs_layout.addWidget(self.specs_table)
        
        splitter.addWidget(specs_group)
        
        # 日志区域
        log_group = QGroupBox("同步日志")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 10))
        log_layout.addWidget(self.log_text)
        
        splitter.addWidget(log_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        main_layout.addWidget(splitter)
        
        # 底部按钮
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.close)
        bottom_layout.addWidget(self.close_btn)
        
        main_layout.addLayout(bottom_layout)
    
    def _load_initial_data(self):
        """加载初始数据"""
        try:
            # 加载规范列表
            self._load_specs()
        except Exception as e:
            logger.exception(f"加载初始数据失败: {e}")
            QMessageBox.warning(self, "错误", f"加载初始数据失败: {str(e)}")
    
    def _load_specs(self):
        """加载规范列表"""
        self.specs_table.setRowCount(0)
        
        try:
            specs = self.spec_manager.get_specs_list()
            
            for spec in specs:
                row = self.specs_table.rowCount()
                self.specs_table.insertRow(row)
                
                # 规范名称
                name_item = QTableWidgetItem(spec.get('name', ''))
                name_item.setData(Qt.UserRole, spec.get('id'))
                self.specs_table.setItem(row, 0, name_item)
                
                # 当前版本
                current_ver = QTableWidgetItem(spec.get('current_version', 'N/A'))
                self.specs_table.setItem(row, 1, current_ver)
                
                # 最新版本
                latest_ver = QTableWidgetItem(spec.get('latest_version', 'N/A'))
                self.specs_table.setItem(row, 2, latest_ver)
                
                # 状态
                status = spec.get('status', 'unknown')
                status_item = QTableWidgetItem(status)
                if status == '可更新':
                    status_item.setForeground(Qt.red)
                self.specs_table.setItem(row, 3, status_item)
                
                # 操作按钮
                sync_btn = QPushButton("同步")
                sync_btn.clicked.connect(lambda checked, s=spec: self._sync_spec(s))
                if status != '可更新':
                    sync_btn.setEnabled(False)
                self.specs_table.setCellWidget(row, 4, sync_btn)
                
        except Exception as e:
            logger.exception(f"加载规范列表失败: {e}")
            QMessageBox.warning(self, "错误", f"加载规范列表失败: {str(e)}")
    
    def _check_updates(self):
        """检查更新"""
        try:
            self.check_btn.setEnabled(False)
            self.log_text.append("正在检查规范更新...")
            
            self.check_results = self.spec_manager.check_updates()
            
            # 更新表格
            self._load_specs()
            
            # 启用同步按钮
            self.sync_all_btn.setEnabled(True)
            
            # 显示结果
            summary = self.spec_manager.get_update_summary()
            self.log_text.append(f"\n{summary}")
            
            QMessageBox.information(self, "检查完成", "规范更新检查完成！")
            
        except Exception as e:
            logger.exception(f"检查更新失败: {e}")
            QMessageBox.warning(self, "错误", f"检查更新失败: {str(e)}")
        finally:
            self.check_btn.setEnabled(True)
    
    def _sync_spec(self, spec):
        """同步单个规范"""
        spec_name = spec.get('name')
        if not spec_name:
            return
        
        try:
            self._start_sync(spec_name)
        except Exception as e:
            logger.exception(f"同步规范失败: {e}")
            QMessageBox.warning(self, "错误", f"同步规范失败: {str(e)}")
    
    def _sync_all_specs(self):
        """同步所有规范"""
        try:
            self._start_sync()
        except Exception as e:
            logger.exception(f"同步所有规范失败: {e}")
            QMessageBox.warning(self, "错误", f"同步所有规范失败: {str(e)}")
    
    def _start_sync(self, spec_name=None):
        """开始同步"""
        # 禁用按钮
        self.check_btn.setEnabled(False)
        self.sync_all_btn.setEnabled(False)
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # 清空日志
        self.log_text.append("\n开始同步...")
        
        # 创建并启动同步线程
        backup = self.backup_checkbox.isChecked()
        self.sync_worker = SyncWorker(self.spec_manager, spec_name, backup)
        self.sync_worker.progress.connect(self._on_progress)
        self.sync_worker.status.connect(self._on_status)
        self.sync_worker.finished.connect(self._on_sync_finished)
        self.sync_worker.error.connect(self._on_sync_error)
        self.sync_worker.start()
    
    def _on_progress(self, value):
        """处理进度更新"""
        self.progress_bar.setValue(value)
    
    def _on_status(self, message):
        """处理状态更新"""
        self.log_text.append(message)
    
    def _on_sync_finished(self, result):
        """处理同步完成"""
        try:
            self.log_text.append("\n同步完成！")
            
            # 更新规范列表
            self._load_specs()
            
            # 显示结果
            QMessageBox.information(self, "同步完成", "规范同步操作已完成！")
            
        finally:
            # 恢复按钮状态
            self.check_btn.setEnabled(True)
            self.sync_all_btn.setEnabled(True)
            self.progress_bar.setVisible(False)
    
    def _on_sync_error(self, error_message):
        """处理同步错误"""
        self.log_text.append(f"\n错误: {error_message}")
        QMessageBox.warning(self, "同步失败", f"同步过程中出现错误: {error_message}")
        
        # 恢复按钮状态
        self.check_btn.setEnabled(True)
        self.sync_all_btn.setEnabled(True)
        self.progress_bar.setVisible(False)


def show_spec_sync_dialog(parent=None):
    """
    显示规范同步对话框
    
    Args:
        parent: 父窗口
    """
    dialog = SpecSyncDialog(parent)
    dialog.exec_()
