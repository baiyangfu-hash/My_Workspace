# -*- coding: utf-8 -*-
"""
变量表格组件
"""
from PyQt5.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, QMenu, QAction,
    QAbstractItemView, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont
from typing import List, Dict, Optional
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class VariableTable(QTableWidget):
    """变量表格组件"""
    
    variable_changed = pyqtSignal()
    selection_changed = pyqtSignal(list)
    
    COLUMN_HEADERS = ['变量名', '数据类型', '地址', '注释', '作用域', '初始值', '变量组']
    COLUMN_KEYS = ['name', 'type', 'address', 'description', 'scope', 'default_value', 'group']
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._variables: List[Dict] = []
        self._modified = False
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        self.setColumnCount(len(self.COLUMN_HEADERS))
        self.setHorizontalHeaderLabels(self.COLUMN_HEADERS)
        
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Interactive)
        header.setSectionResizeMode(5, QHeaderView.Interactive)
        header.setSectionResizeMode(6, QHeaderView.Interactive)
        
        self.setColumnWidth(0, 150)
        self.setColumnWidth(1, 100)
        self.setColumnWidth(2, 100)
        self.setColumnWidth(4, 100)
        self.setColumnWidth(5, 100)
        self.setColumnWidth(6, 100)
        
        self.itemChanged.connect(self._on_item_changed)
        self.itemSelectionChanged.connect(self._on_selection_changed)
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
    
    def set_variables(self, variables: List[Dict]):
        """设置变量数据"""
        self._variables = variables.copy() if variables else []
        self._refresh_table()
        self._modified = False
    
    def get_variables(self) -> List[Dict]:
        """获取变量数据"""
        return self._variables.copy()
    
    def get_selected_variables(self) -> List[Dict]:
        """获取选中的变量"""
        selected_rows = set()
        for item in self.selectedItems():
            selected_rows.add(item.row())
        
        return [self._variables[row] for row in sorted(selected_rows) if row < len(self._variables)]
    
    def add_variable(self, variable: Dict = None):
        """添加变量"""
        if variable is None:
            variable = {
                'name': '',
                'type': 'BOOL',
                'address': '',
                'description': '',
                'scope': 'VAR_GLOBAL',
                'default_value': '',
                'group': ''
            }
        
        self._variables.append(variable)
        self._add_row(len(self._variables) - 1, variable)
        self._modified = True
        self.variable_changed.emit()
    
    def delete_selected(self):
        """删除选中的变量"""
        selected_rows = sorted(set(item.row() for item in self.selectedItems()), reverse=True)
        
        if not selected_rows:
            return
        
        reply = QMessageBox.question(
            self, '确认删除',
            f'确定要删除选中的 {len(selected_rows)} 个变量吗？',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            for row in selected_rows:
                if row < len(self._variables):
                    del self._variables[row]
            
            self._refresh_table()
            self._modified = True
            self.variable_changed.emit()
    
    def is_modified(self) -> bool:
        """是否已修改"""
        return self._modified
    
    def set_modified(self, modified: bool):
        """设置修改状态"""
        self._modified = modified
    
    def _refresh_table(self):
        """刷新表格"""
        self.blockSignals(True)
        self.setRowCount(0)
        
        for i, var in enumerate(self._variables):
            self._add_row(i, var)
        
        self.blockSignals(False)
    
    def _add_row(self, row: int, variable: Dict):
        """添加一行"""
        self.insertRow(row)
        
        for col, key in enumerate(self.COLUMN_KEYS):
            value = variable.get(key, '')
            item = QTableWidgetItem(str(value) if value else '')
            item.setData(Qt.UserRole, key)
            
            if key == 'name':
                item.setFont(QFont('Microsoft YaHei', 9, QFont.Bold))
            
            self.setItem(row, col, item)
    
    def _on_item_changed(self, item: QTableWidgetItem):
        """单元格内容改变"""
        row = item.row()
        col = item.column()
        
        if row >= len(self._variables):
            return
        
        key = self.COLUMN_KEYS[col]
        value = item.text().strip()
        
        if self._variables[row].get(key) != value:
            self._variables[row][key] = value
            self._modified = True
            self.variable_changed.emit()
    
    def _on_selection_changed(self):
        """选择改变"""
        selected = self.get_selected_variables()
        self.selection_changed.emit(selected)
    
    def _show_context_menu(self, pos):
        """显示右键菜单"""
        menu = QMenu(self)
        
        add_action = QAction("添加变量", self)
        add_action.triggered.connect(lambda: self.add_variable())
        menu.addAction(add_action)
        
        if self.selectedItems():
            delete_action = QAction("删除选中", self)
            delete_action.triggered.connect(self.delete_selected)
            menu.addAction(delete_action)
            
            menu.addSeparator()
            
            copy_action = QAction("复制选中", self)
            copy_action.triggered.connect(self._copy_selected)
            menu.addAction(copy_action)
        
        menu.exec_(self.mapToGlobal(pos))
    
    def _copy_selected(self):
        """复制选中的变量"""
        import pyperclip
        selected = self.get_selected_variables()
        if selected:
            text = '\n'.join([f"{v['name']}\t{v['type']}\t{v['address']}\t{v['description']}" for v in selected])
            pyperclip.copy(text)
    
    def find_by_name(self, name: str) -> List[int]:
        """按名称查找变量"""
        results = []
        for i, var in enumerate(self._variables):
            if name.lower() in var.get('name', '').lower():
                results.append(i)
        return results
    
    def highlight_rows(self, rows: List[int], color: QColor = None):
        """高亮显示行"""
        if color is None:
            color = QColor(255, 255, 0, 100)
        
        for row in rows:
            for col in range(self.columnCount()):
                item = self.item(row, col)
                if item:
                    item.setBackground(color)
