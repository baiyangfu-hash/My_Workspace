# -*- coding: utf-8 -*-
"""
解析器主界面组件
"""
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QToolBar, QAction,
    QSplitter, QLabel, QComboBox, QMessageBox, QFileDialog,
    QStatusBar, QProgressBar, QGroupBox, QLineEdit, QPushButton
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QKeySequence
from typing import List, Dict, Optional
from src.utils.logger import setup_logger

from .variable_table import VariableTable
from .variable_dialog import VariableDialog
from .batch_edit_dialog import BatchEditDialog

logger = setup_logger(__name__)


class ParserWidget(QWidget):
    """解析器主界面组件"""
    
    file_opened = pyqtSignal(str)
    file_saved = pyqtSignal(str)
    
    def __init__(self, parent=None, config: dict = None):
        super().__init__(parent)
        self._config = config or {}
        self._current_file: Optional[str] = None
        self._current_format: Optional[str] = None
        self._current_encoding: Optional[str] = None
        self._original_variables: List[Dict] = []
        
        self._init_ui()
        self._init_connections()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        toolbar = QToolBar()
        toolbar.setMovable(False)
        
        open_action = QAction("打开", self)
        open_action.setToolTip("打开变量表文件 (Ctrl+O)")
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        open_action.triggered.connect(self._on_open_file)
        toolbar.addAction(open_action)
        
        save_action = QAction("保存", self)
        save_action.setToolTip("保存文件 (Ctrl+S)")
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(self._on_save_file)
        toolbar.addAction(save_action)
        
        save_as_action = QAction("另存为", self)
        save_as_action.setToolTip("另存为...")
        save_as_action.triggered.connect(self._on_save_as)
        toolbar.addAction(save_as_action)
        
        toolbar.addSeparator()
        
        add_action = QAction("添加", self)
        add_action.setToolTip("添加变量 (Ins)")
        add_action.setShortcut(QKeySequence("Ins"))
        add_action.triggered.connect(self._on_add_variable)
        toolbar.addAction(add_action)
        
        edit_action = QAction("编辑", self)
        edit_action.setToolTip("编辑选中变量 (Enter)")
        edit_action.setShortcut(QKeySequence("Enter"))
        edit_action.triggered.connect(self._on_edit_variable)
        toolbar.addAction(edit_action)
        
        delete_action = QAction("删除", self)
        delete_action.setToolTip("删除选中变量 (Del)")
        delete_action.setShortcut(QKeySequence("Del"))
        delete_action.triggered.connect(self._on_delete_variable)
        toolbar.addAction(delete_action)
        
        toolbar.addSeparator()
        
        batch_action = QAction("批量编辑", self)
        batch_action.setToolTip("批量编辑选中的变量")
        batch_action.triggered.connect(self._on_batch_edit)
        toolbar.addAction(batch_action)
        
        toolbar.addSeparator()
        
        export_csv_action = QAction("导出CSV", self)
        export_csv_action.setToolTip("导出为CSV格式")
        export_csv_action.triggered.connect(self._on_export_csv)
        toolbar.addAction(export_csv_action)
        
        export_json_action = QAction("导出JSON", self)
        export_json_action.setToolTip("导出为JSON格式")
        export_json_action.triggered.connect(self._on_export_json)
        toolbar.addAction(export_json_action)
        
        toolbar.addSeparator()
        
        create_empty_action = QAction("创建空文件", self)
        create_empty_action.setToolTip("基于当前文件创建空模板")
        create_empty_action.triggered.connect(self._on_create_empty)
        toolbar.addAction(create_empty_action)
        
        layout.addWidget(toolbar)
        
        info_group = QGroupBox("文件信息")
        info_layout = QHBoxLayout(info_group)
        
        info_layout.addWidget(QLabel("格式:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(['自动检测', 'Autoshop', 'Work3', 'Codesys'])
        self.format_combo.setToolTip("选择PLC格式")
        info_layout.addWidget(self.format_combo)
        
        info_layout.addWidget(QLabel("编码:"))
        self.encoding_combo = QComboBox()
        self.encoding_combo.addItem("自动检测", None)
        self.encoding_combo.addItems(['utf-8', 'gbk', 'gb2312', 'utf-16', 'utf-16-le', 'utf-16-be'])
        info_layout.addWidget(self.encoding_combo)
        
        info_layout.addWidget(QLabel("搜索:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入变量名搜索...")
        self.search_edit.setMaximumWidth(200)
        info_layout.addWidget(self.search_edit)
        
        search_btn = QPushButton("搜索")
        search_btn.clicked.connect(self._on_search)
        info_layout.addWidget(search_btn)
        
        info_layout.addStretch()
        
        self.file_label = QLabel("未打开文件")
        self.file_label.setStyleSheet("color: #666;")
        info_layout.addWidget(self.file_label)
        
        layout.addWidget(info_group)
        
        self.variable_table = VariableTable()
        layout.addWidget(self.variable_table)
        
        self.status_bar = QStatusBar()
        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label)
        self.count_label = QLabel("变量数: 0")
        self.status_bar.addPermanentWidget(self.count_label)
        layout.addWidget(self.status_bar)
    
    def _init_connections(self):
        """初始化信号连接"""
        self.variable_table.variable_changed.connect(self._on_variable_changed)
        self.variable_table.itemDoubleClicked.connect(self._on_table_double_click)
        self.search_edit.textChanged.connect(self._on_search_text_changed)
    
    def _on_open_file(self):
        """打开文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "打开变量表文件",
            "",
            "变量表文件 (*.csv *.txt *.var);;所有文件 (*.*)"
        )
        
        if file_path:
            self._load_file(file_path)
    
    def _load_file(self, file_path: str):
        """加载文件"""
        from ..parsers.parser_factory import ParserFactory
        
        try:
            format_type = self.format_combo.currentText().lower()
            if format_type == '自动检测':
                format_type = 'auto'
            
            encoding = self.encoding_combo.currentData()
            if encoding is None:
                encoding = self.encoding_combo.currentText()
                if encoding == '自动检测':
                    encoding = None
            
            parser = ParserFactory.create_parser(format_type, file_path, encoding)
            if not parser:
                QMessageBox.warning(self, "错误", "无法识别文件格式")
                return
            
            variables = parser.parse()
            
            self._current_file = file_path
            self._current_format = parser.get_format_name()
            self._current_encoding = parser.get_encoding()
            self._original_variables = variables.copy()
            
            self.variable_table.set_variables(variables)
            
            self.file_label.setText(f"{os.path.basename(file_path)} ({self._current_format}, {self._current_encoding})")
            self._update_status()
            
            self.file_opened.emit(file_path)
            
            logger.info(f"成功加载文件: {file_path}, 共 {len(variables)} 个变量")
            
        except Exception as e:
            logger.error(f"加载文件失败: {e}")
            QMessageBox.critical(self, "错误", f"加载文件失败:\n{str(e)}")
    
    def _on_save_file(self):
        """保存文件"""
        if not self._current_file:
            self._on_save_as()
            return
        
        self._save_to_file(self._current_file)
    
    def _on_save_as(self):
        """另存为"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存变量表文件",
            "",
            "CSV文件 (*.csv);;所有文件 (*.*)"
        )
        
        if file_path:
            self._save_to_file(file_path)
    
    def _save_to_file(self, file_path: str):
        """保存到文件"""
        from ..exporters.exporter import Exporter
        
        try:
            exporter = Exporter()
            variables = self.variable_table.get_variables()
            
            encoding = self._current_encoding or 'utf-8'
            
            success = exporter.export_to_csv(variables, file_path, encoding)
            
            if success:
                self._current_file = file_path
                self._original_variables = variables.copy()
                self.variable_table.set_modified(False)
                
                self.file_label.setText(f"{os.path.basename(file_path)} ({self._current_format}, {encoding})")
                self.status_label.setText("保存成功")
                
                self.file_saved.emit(file_path)
                
                logger.info(f"成功保存文件: {file_path}")
            else:
                QMessageBox.warning(self, "错误", "保存文件失败")
                
        except Exception as e:
            logger.error(f"保存文件失败: {e}")
            QMessageBox.critical(self, "错误", f"保存文件失败:\n{str(e)}")
    
    def _on_add_variable(self):
        """添加变量"""
        dialog = VariableDialog(self, title="添加变量")
        if dialog.exec_() == dialog.Accepted:
            result = dialog.get_result()
            if result:
                self.variable_table.add_variable(result)
    
    def _on_edit_variable(self):
        """编辑变量"""
        selected = self.variable_table.get_selected_variables()
        if not selected:
            QMessageBox.information(self, "提示", "请先选择要编辑的变量")
            return
        
        dialog = VariableDialog(self, selected[0], "编辑变量")
        if dialog.exec_() == dialog.Accepted:
            result = dialog.get_result()
            if result:
                variables = self.variable_table.get_variables()
                for i, var in enumerate(variables):
                    if var['name'] == selected[0]['name']:
                        variables[i] = result
                        break
                
                self.variable_table.set_variables(variables)
    
    def _on_delete_variable(self):
        """删除变量"""
        self.variable_table.delete_selected()
    
    def _on_batch_edit(self):
        """批量编辑"""
        selected = self.variable_table.get_selected_variables()
        if not selected:
            QMessageBox.information(self, "提示", "请先选择要批量编辑的变量")
            return
        
        dialog = BatchEditDialog(self, len(selected))
        if dialog.exec_() == dialog.Accepted:
            result = dialog.get_result()
            if result:
                edited = BatchEditDialog.apply_batch_edit(selected, result)
                
                variables = self.variable_table.get_variables()
                for i, var in enumerate(variables):
                    for j, sel in enumerate(selected):
                        if var['name'] == sel['name']:
                            variables[i] = edited[j]
                            break
                
                self.variable_table.set_variables(variables)
    
    def _on_export_csv(self):
        """导出CSV"""
        variables = self.variable_table.get_variables()
        if not variables:
            QMessageBox.information(self, "提示", "没有数据可导出")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出CSV",
            "",
            "CSV文件 (*.csv)"
        )
        
        if file_path:
            from ..exporters.exporter import Exporter
            exporter = Exporter()
            
            if exporter.export_to_csv(variables, file_path):
                QMessageBox.information(self, "成功", f"已导出到:\n{file_path}")
            else:
                QMessageBox.warning(self, "错误", "导出失败")
    
    def _on_export_json(self):
        """导出JSON"""
        variables = self.variable_table.get_variables()
        if not variables:
            QMessageBox.information(self, "提示", "没有数据可导出")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出JSON",
            "",
            "JSON文件 (*.json)"
        )
        
        if file_path:
            from ..exporters.exporter import Exporter
            exporter = Exporter()
            
            if exporter.export_to_json(variables, file_path):
                QMessageBox.information(self, "成功", f"已导出到:\n{file_path}")
            else:
                QMessageBox.warning(self, "错误", "导出失败")
    
    def _on_create_empty(self):
        """创建空文件"""
        if not self._current_file:
            QMessageBox.information(self, "提示", "请先打开一个文件作为模板")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "创建空文件",
            "",
            "变量表文件 (*.csv *.txt)"
        )
        
        if file_path:
            from ..exporters.exporter import Exporter
            exporter = Exporter()
            
            if exporter.create_empty_file(self._current_file, file_path):
                QMessageBox.information(self, "成功", f"已创建空文件:\n{file_path}")
            else:
                QMessageBox.warning(self, "错误", "创建失败")
    
    def _on_search(self):
        """搜索"""
        text = self.search_edit.text().strip()
        if text:
            rows = self.variable_table.find_by_name(text)
            if rows:
                self.variable_table.highlight_rows(rows)
                self.status_label.setText(f"找到 {len(rows)} 个匹配项")
            else:
                self.status_label.setText("未找到匹配项")
    
    def _on_search_text_changed(self, text: str):
        """搜索文本改变"""
        if not text:
            self.variable_table.highlight_rows([])
    
    def _on_variable_changed(self):
        """变量改变"""
        self._update_status()
    
    def _on_table_double_click(self, item):
        """表格双击"""
        self._on_edit_variable()
    
    def _update_status(self):
        """更新状态"""
        count = len(self.variable_table.get_variables())
        self.count_label.setText(f"变量数: {count}")
        
        if self.variable_table.is_modified():
            self.status_label.setText("已修改")
            self.status_label.setStyleSheet("color: #D32F2F;")
        else:
            self.status_label.setText("就绪")
            self.status_label.setStyleSheet("")
    
    def load_file(self, file_path: str):
        """公共方法：加载文件"""
        self._load_file(file_path)
    
    def get_current_file(self) -> Optional[str]:
        """获取当前文件路径"""
        return self._current_file
    
    def is_modified(self) -> bool:
        """是否已修改"""
        return self.variable_table.is_modified()
