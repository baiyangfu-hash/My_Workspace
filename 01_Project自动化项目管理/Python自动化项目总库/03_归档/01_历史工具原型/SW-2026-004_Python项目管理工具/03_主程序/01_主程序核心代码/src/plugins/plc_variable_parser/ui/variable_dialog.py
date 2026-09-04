# -*- coding: utf-8 -*-
"""
变量编辑对话框
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QTextEdit, QPushButton,
    QDialogButtonBox, QLabel, QWidget
)
from PyQt5.QtCore import Qt
from typing import Dict, Optional
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class VariableDialog(QDialog):
    """变量编辑对话框"""
    
    DATA_TYPES = ['BOOL', 'INT', 'DINT', 'REAL', 'LREAL', 'STRING', 'TIME', 'WORD', 'DWORD', 'BYTE']
    SCOPES = ['VAR_GLOBAL', 'VAR_INPUT', 'VAR_OUTPUT', 'VAR_IN_OUT', 'VAR_LOCAL', 'VAR_TEMP']
    
    def __init__(self, parent=None, variable: Dict = None, title: str = "编辑变量"):
        super().__init__(parent)
        self._variable = variable or {}
        self._result: Optional[Dict] = None
        
        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        self._init_ui()
        self._load_data()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("请输入变量名称")
        form_layout.addRow("变量名*:", self.name_edit)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(self.DATA_TYPES)
        self.type_combo.setEditable(True)
        form_layout.addRow("数据类型*:", self.type_combo)
        
        self.address_edit = QLineEdit()
        self.address_edit.setPlaceholderText("如: M0, D100, %IX0.0")
        form_layout.addRow("地址:", self.address_edit)
        
        self.scope_combo = QComboBox()
        self.scope_combo.addItems(self.SCOPES)
        form_layout.addRow("作用域:", self.scope_combo)
        
        self.default_edit = QLineEdit()
        self.default_edit.setPlaceholderText("初始值")
        form_layout.addRow("初始值:", self.default_edit)
        
        self.group_edit = QLineEdit()
        self.group_edit.setPlaceholderText("变量组名称")
        form_layout.addRow("变量组:", self.group_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("变量注释说明")
        self.description_edit.setMaximumHeight(80)
        form_layout.addRow("注释:", self.description_edit)
        
        layout.addLayout(form_layout)
        
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self._on_accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
    
    def _load_data(self):
        """加载数据"""
        self.name_edit.setText(self._variable.get('name', ''))
        
        data_type = self._variable.get('type', 'BOOL')
        index = self.type_combo.findText(data_type)
        if index >= 0:
            self.type_combo.setCurrentIndex(index)
        else:
            self.type_combo.setEditText(data_type)
        
        self.address_edit.setText(self._variable.get('address', ''))
        
        scope = self._variable.get('scope', 'VAR_GLOBAL')
        index = self.scope_combo.findText(scope)
        if index >= 0:
            self.scope_combo.setCurrentIndex(index)
        
        self.default_edit.setText(self._variable.get('default_value', ''))
        self.group_edit.setText(self._variable.get('group', ''))
        self.description_edit.setPlainText(self._variable.get('description', ''))
    
    def _on_accept(self):
        """确认"""
        name = self.name_edit.text().strip()
        if not name:
            self.name_edit.setFocus()
            return
        
        self._result = {
            'name': name,
            'type': self.type_combo.currentText().strip(),
            'address': self.address_edit.text().strip(),
            'scope': self.scope_combo.currentText(),
            'default_value': self.default_edit.text().strip(),
            'group': self.group_edit.text().strip(),
            'description': self.description_edit.toPlainText().strip()
        }
        
        self.accept()
    
    def get_result(self) -> Optional[Dict]:
        """获取结果"""
        return self._result
