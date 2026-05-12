# -*- coding: utf-8 -*-
"""
批量编辑对话框
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QCheckBox, QPushButton,
    QDialogButtonBox, QGroupBox, QLabel, QMessageBox
)
from PyQt5.QtCore import Qt
from typing import List, Dict, Optional
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class BatchEditDialog(QDialog):
    """批量编辑对话框"""
    
    DATA_TYPES = ['(不修改)', 'BOOL', 'INT', 'DINT', 'REAL', 'LREAL', 'STRING', 'TIME', 'WORD', 'DWORD', 'BYTE']
    SCOPES = ['(不修改)', 'VAR_GLOBAL', 'VAR_INPUT', 'VAR_OUTPUT', 'VAR_IN_OUT', 'VAR_LOCAL', 'VAR_TEMP']
    
    def __init__(self, parent=None, selected_count: int = 0):
        super().__init__(parent)
        self._selected_count = selected_count
        self._result: Optional[Dict] = None
        
        self.setWindowTitle("批量编辑")
        self.setMinimumWidth(400)
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        info_label = QLabel(f"将对选中的 {self._selected_count} 个变量进行批量修改")
        info_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(info_label)
        
        group_box = QGroupBox("批量修改选项")
        form_layout = QFormLayout(group_box)
        
        self.type_check = QCheckBox("修改数据类型")
        self.type_combo = QComboBox()
        self.type_combo.addItems(self.DATA_TYPES)
        self.type_combo.setEnabled(False)
        self.type_check.toggled.connect(self.type_combo.setEnabled)
        
        type_layout = QHBoxLayout()
        type_layout.addWidget(self.type_check)
        type_layout.addWidget(self.type_combo)
        form_layout.addRow("数据类型:", type_layout)
        
        self.scope_check = QCheckBox("修改作用域")
        self.scope_combo = QComboBox()
        self.scope_combo.addItems(self.SCOPES)
        self.scope_combo.setEnabled(False)
        self.scope_check.toggled.connect(self.scope_combo.setEnabled)
        
        scope_layout = QHBoxLayout()
        scope_layout.addWidget(self.scope_check)
        scope_layout.addWidget(self.scope_combo)
        form_layout.addRow("作用域:", scope_layout)
        
        self.prefix_check = QCheckBox("添加前缀")
        self.prefix_edit = QLineEdit()
        self.prefix_edit.setEnabled(False)
        self.prefix_check.toggled.connect(self.prefix_edit.setEnabled)
        
        prefix_layout = QHBoxLayout()
        prefix_layout.addWidget(self.prefix_check)
        prefix_layout.addWidget(self.prefix_edit)
        form_layout.addRow("名称前缀:", prefix_layout)
        
        self.suffix_check = QCheckBox("添加后缀")
        self.suffix_edit = QLineEdit()
        self.suffix_edit.setEnabled(False)
        self.suffix_check.toggled.connect(self.suffix_edit.setEnabled)
        
        suffix_layout = QHBoxLayout()
        suffix_layout.addWidget(self.suffix_check)
        suffix_layout.addWidget(self.suffix_edit)
        form_layout.addRow("名称后缀:", suffix_layout)
        
        self.desc_append_check = QCheckBox("追加注释")
        self.desc_append_edit = QLineEdit()
        self.desc_append_edit.setEnabled(False)
        self.desc_append_check.toggled.connect(self.desc_append_edit.setEnabled)
        
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(self.desc_append_check)
        desc_layout.addWidget(self.desc_append_edit)
        form_layout.addRow("追加注释:", desc_layout)
        
        layout.addWidget(group_box)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _on_accept(self):
        """确认"""
        if not any([
            self.type_check.isChecked(),
            self.scope_check.isChecked(),
            self.prefix_check.isChecked(),
            self.suffix_check.isChecked(),
            self.desc_append_check.isChecked()
        ]):
            QMessageBox.warning(self, "提示", "请至少选择一项修改内容")
            return
        
        self._result = {
            'modify_type': self.type_check.isChecked(),
            'type_value': self.type_combo.currentText() if self.type_check.isChecked() else None,
            'modify_scope': self.scope_check.isChecked(),
            'scope_value': self.scope_combo.currentText() if self.scope_check.isChecked() else None,
            'add_prefix': self.prefix_check.isChecked(),
            'prefix_value': self.prefix_edit.text() if self.prefix_check.isChecked() else None,
            'add_suffix': self.suffix_check.isChecked(),
            'suffix_value': self.suffix_edit.text() if self.suffix_check.isChecked() else None,
            'append_desc': self.desc_append_check.isChecked(),
            'desc_value': self.desc_append_edit.text() if self.desc_append_check.isChecked() else None,
        }
        
        self.accept()
    
    def get_result(self) -> Optional[Dict]:
        """获取结果"""
        return self._result
    
    @staticmethod
    def apply_batch_edit(variables: List[Dict], edit_config: Dict) -> List[Dict]:
        """应用批量编辑"""
        result = []
        
        for var in variables:
            new_var = var.copy()
            
            if edit_config.get('modify_type') and edit_config.get('type_value') != '(不修改)':
                new_var['type'] = edit_config['type_value']
            
            if edit_config.get('modify_scope') and edit_config.get('scope_value') != '(不修改)':
                new_var['scope'] = edit_config['scope_value']
            
            if edit_config.get('add_prefix') and edit_config.get('prefix_value'):
                new_var['name'] = edit_config['prefix_value'] + new_var['name']
            
            if edit_config.get('add_suffix') and edit_config.get('suffix_value'):
                new_var['name'] = new_var['name'] + edit_config['suffix_value']
            
            if edit_config.get('append_desc') and edit_config.get('desc_value'):
                original_desc = new_var.get('description', '')
                if original_desc:
                    new_var['description'] = f"{original_desc}; {edit_config['desc_value']}"
                else:
                    new_var['description'] = edit_config['desc_value']
            
            result.append(new_var)
        
        return result
