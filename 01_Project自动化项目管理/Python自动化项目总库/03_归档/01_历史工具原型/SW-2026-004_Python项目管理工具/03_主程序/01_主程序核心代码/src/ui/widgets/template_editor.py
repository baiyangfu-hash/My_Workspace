# -*- coding: utf-8 -*-
"""
模板编辑器对话框
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QTextEdit, QTreeWidget, QTreeWidgetItem,
    QTabWidget, QWidget, QFormLayout, QCheckBox, QComboBox,
    QMessageBox, QSplitter, QGroupBox, QListWidget, QListWidgetItem,
    QFileDialog, QMenu
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from src.services.template_service import TemplateService
from src.core.constants import BusinessLine
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class TemplateEditorDialog(QDialog):
    """模板编辑器对话框"""
    
    template_saved = pyqtSignal(str)
    
    SUPPORTED_VARIABLES = [
        ("project_name", "项目名称"),
        ("project_code", "项目编号"),
        ("business_line", "业务线"),
        ("manager", "项目负责人"),
        ("create_date", "创建日期"),
        ("description", "项目描述"),
    ]
    
    def __init__(self, template_id=None, parent=None, readonly=False):
        super().__init__(parent)
        self.template_id = template_id
        self.template_data = None
        self.readonly = readonly
        self.is_new = template_id is None
        self.is_builtin = False
        
        self._init_ui()
        self._load_template()
    
    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("模板编辑器" if not self.readonly else "模板查看")
        self.setMinimumSize(1000, 700)
        
        layout = QVBoxLayout(self)
        
        # 顶部信息栏
        self._create_info_bar(layout)
        
        # 主内容区域
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：目录结构树
        left_panel = self._create_structure_panel()
        splitter.addWidget(left_panel)
        
        # 右侧：文件模板编辑
        right_panel = self._create_template_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([400, 600])
        layout.addWidget(splitter)
        
        # 底部按钮栏
        self._create_button_bar(layout)
        
        # 应用只读模式
        if self.readonly:
            self._apply_readonly_mode()
    
    def _create_info_bar(self, parent_layout):
        """创建顶部信息栏"""
        info_group = QGroupBox("基本信息")
        info_layout = QFormLayout(info_group)
        
        # 模板ID
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("例如: TPL-CUSTOM-001")
        info_layout.addRow("模板ID:", self.id_input)
        
        # 模板名称
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("例如: 自定义模板")
        info_layout.addRow("模板名称:", self.name_input)
        
        # 版本
        self.version_input = QLineEdit()
        self.version_input.setText("V1.0.0")
        info_layout.addRow("版本:", self.version_input)
        
        # 编译器
        self.compiler_input = QComboBox()
        self.compiler_input.setEditable(True)
        self.compiler_input.addItems([
            "", "Python", "PyQt5", "Flask", "Django", 
            "Step7/TIA Portal", "Multi",
            "机器人", "全系统"
        ])
        info_layout.addRow("编译器:", self.compiler_input)
        
        # 适用场景
        self.scene_input = QLineEdit()
        self.scene_input.setPlaceholderText("例如: 自定义项目")
        info_layout.addRow("适用场景:", self.scene_input)
        
        # 描述
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("模板描述...")
        self.desc_input.setMaximumHeight(60)
        info_layout.addRow("描述:", self.desc_input)
        
        # 业务线 - 动态从 BusinessLine 枚举生成
        business_layout = QHBoxLayout()
        self.business_line_checkboxes = {}
        for bl in BusinessLine:
            cb = QCheckBox(f"{bl.value}-{bl.name}")
            self.business_line_checkboxes[bl.value] = cb
            business_layout.addWidget(cb)
        business_layout.addStretch()
        info_layout.addRow("适用业务线:", business_layout)
        
        parent_layout.addWidget(info_group)
    
    def _create_structure_panel(self):
        """创建目录结构面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 标题和工具栏
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("目录结构"))
        
        self.add_dir_btn = QPushButton("添加目录")
        self.add_dir_btn.clicked.connect(self._add_directory)
        header_layout.addWidget(self.add_dir_btn)
        
        self.add_file_btn = QPushButton("添加文件")
        self.add_file_btn.clicked.connect(self._add_file_template)
        header_layout.addWidget(self.add_file_btn)
        
        self.delete_item_btn = QPushButton("删除")
        self.delete_item_btn.clicked.connect(self._delete_selected_item)
        header_layout.addWidget(self.delete_item_btn)
        
        layout.addLayout(header_layout)
        
        # 目录树
        self.structure_tree = QTreeWidget()
        self.structure_tree.setHeaderLabels(["目录/文件", "类型", "必填"])
        self.structure_tree.setColumnWidth(0, 250)
        self.structure_tree.setColumnWidth(1, 80)
        self.structure_tree.setColumnWidth(2, 50)
        self.structure_tree.itemClicked.connect(self._on_structure_item_clicked)
        
        self.structure_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.structure_tree.customContextMenuRequested.connect(self._show_structure_context_menu)
        
        layout.addWidget(self.structure_tree)
        
        return panel
    
    def _create_template_panel(self):
        """创建文件模板编辑面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 标签页
        self.tab_widget = QTabWidget()
        
        # 文件内容标签页
        content_tab = QWidget()
        content_layout = QVBoxLayout(content_tab)
        
        # 文件路径
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("文件路径:"))
        self.file_path_input = QLineEdit()
        self.file_path_input.setReadOnly(True)
        path_layout.addWidget(self.file_path_input)
        content_layout.addLayout(path_layout)
        
        # 文件类型
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("文件类型:"))
        self.file_type_combo = QComboBox()
        self.file_type_combo.addItems(["document", "code", "config", "data", "notebook"])
        type_layout.addWidget(self.file_type_combo)
        type_layout.addStretch()
        content_layout.addLayout(type_layout)
        
        # 文件内容
        content_layout.addWidget(QLabel("文件内容:"))
        self.file_content_edit = QTextEdit()
        self.file_content_edit.setFontFamily("Consolas")
        self.file_content_edit.setPlaceholderText("文件模板内容，支持变量占位符如 {project_name}")
        content_layout.addWidget(self.file_content_edit)
        
        self.tab_widget.addTab(content_tab, "文件内容")
        
        # 变量说明标签页
        var_tab = QWidget()
        var_layout = QVBoxLayout(var_tab)
        
        var_layout.addWidget(QLabel("支持的变量占位符:"))
        self.var_list = QListWidget()
        for var_name, var_desc in self.SUPPORTED_VARIABLES:
            item = QListWidgetItem(f"{{{var_name}}} - {var_desc}")
            item.setData(Qt.UserRole, var_name)
            self.var_list.addItem(item)
        var_layout.addWidget(self.var_list)
        
        insert_btn = QPushButton("插入变量到内容")
        insert_btn.clicked.connect(self._insert_variable)
        var_layout.addWidget(insert_btn)
        
        self.tab_widget.addTab(var_tab, "变量说明")
        
        layout.addWidget(self.tab_widget)
        
        return panel
    
    def _create_button_bar(self, parent_layout):
        """创建底部按钮栏"""
        button_layout = QHBoxLayout()
        
        button_layout.addStretch()
        
        if not self.readonly:
            self.save_btn = QPushButton("保存")
            self.save_btn.clicked.connect(self._save_template)
            button_layout.addWidget(self.save_btn)
            
            self.save_as_btn = QPushButton("另存为")
            self.save_as_btn.clicked.connect(self._save_as_template)
            button_layout.addWidget(self.save_as_btn)
        
        self.cancel_btn = QPushButton("关闭")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        parent_layout.addLayout(button_layout)
    
    def _load_template(self):
        """加载模板数据"""
        if self.template_id:
            template = TemplateService.get_template(self.template_id)
            if template:
                self.template_data = template
                self.is_builtin = template.is_builtin
                
                self.id_input.setText(template.template_id)
                self.name_input.setText(template.name)
                self.version_input.setText(template.version)
                self.compiler_input.setCurrentText(template.compiler or "")
                self.scene_input.setText(template.scene or "")
                self.desc_input.setPlainText(template.description or "")
                
                if template.business_lines:
                    for bl in template.business_lines:
                        if bl in self.business_line_checkboxes:
                            self.business_line_checkboxes[bl].setChecked(True)
                
                self._load_structure(template.structure, template.templates)

                # 内置模板：仅锁定 template_id 字段和禁用保存按钮
                if self.is_builtin:
                    if hasattr(self, 'id_input'):
                        self.id_input.setReadOnly(True)
                    if hasattr(self, 'save_btn'):
                        self.save_btn.setEnabled(False)
    
    def _load_structure(self, structure, templates):
        """加载目录结构"""
        self.structure_tree.clear()
        
        root = QTreeWidgetItem(self.structure_tree, ["根目录", "", ""])
        root.setExpanded(True)
        
        for item in structure:
            path = item.get("path", "")
            required = item.get("required", False)
            description = item.get("description", "")
            
            parts = path.split("/")
            current = root
            
            for i, part in enumerate(parts):
                found = None
                for j in range(current.childCount()):
                    child = current.child(j)
                    if child.text(0) == part:
                        found = child
                        break
                
                if not found:
                    is_file = i == len(parts) - 1 and "." in part
                    item_type = "文件" if is_file else "目录"
                    found = QTreeWidgetItem(current, [part, item_type, "是" if required else "否"])
                    found.setData(0, Qt.UserRole, path)
                    found.setData(1, Qt.UserRole, "directory")
                
                current = found
                current.setExpanded(True)
        
        for tmpl in templates or []:
            path = tmpl.get("path", "")
            file_type = tmpl.get("type", "document")
            
            parts = path.split("/")
            current = root
            
            for i, part in enumerate(parts):
                found = None
                for j in range(current.childCount()):
                    child = current.child(j)
                    if child.text(0) == part:
                        found = child
                        break
                
                if not found:
                    is_file = i == len(parts) - 1
                    item_type = "文件模板" if is_file else "目录"
                    found = QTreeWidgetItem(current, [part, item_type, ""])
                    found.setData(0, Qt.UserRole, path)
                    found.setData(1, Qt.UserRole, "file" if is_file else "directory")
                    if is_file:
                        found.setData(2, Qt.UserRole, tmpl)
                
                current = found
                current.setExpanded(True)
        
        self.structure_tree.expandAll()
    
    def _on_structure_item_clicked(self, item, column):
        """点击结构项"""
        item_type = item.data(1, Qt.UserRole)
        
        if item_type == "file":
            path = item.data(0, Qt.UserRole)
            tmpl_data = item.data(2, Qt.UserRole)
            
            self.file_path_input.setText(path)
            if tmpl_data:
                self.file_type_combo.setCurrentText(tmpl_data.get("type", "document"))
                self.file_content_edit.setPlainText(tmpl_data.get("content", ""))
        else:
            self.file_path_input.setText("")
            self.file_content_edit.setPlainText("")
    
    def _show_structure_context_menu(self, pos):
        """显示结构树右键菜单"""
        item = self.structure_tree.itemAt(pos)
        if not item:
            return
        
        menu = QMenu(self)
        
        add_dir_action = menu.addAction("添加子目录")
        add_file_action = menu.addAction("添加文件模板")
        menu.addSeparator()
        rename_action = menu.addAction("重命名")
        delete_action = menu.addAction("删除")
        
        if self.readonly:
            add_dir_action.setEnabled(False)
            add_file_action.setEnabled(False)
            rename_action.setEnabled(False)
            delete_action.setEnabled(False)
        
        action = menu.exec_(self.structure_tree.mapToGlobal(pos))
        
        if action == add_dir_action:
            self._add_directory_under(item)
        elif action == add_file_action:
            self._add_file_template_under(item)
        elif action == rename_action:
            self._rename_item(item)
        elif action == delete_action:
            self._delete_item(item)
    
    def _add_directory(self):
        """添加目录"""
        from PyQt5.QtWidgets import QInputDialog, QDialog, QVBoxLayout, QLabel, QCheckBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("添加目录")
        layout = QVBoxLayout(dialog)
        
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("目录名称:")
        layout.addWidget(QLabel("目录名称:"))
        layout.addWidget(name_edit)
        
        required_cb = QCheckBox("必填目录")
        layout.addWidget(required_cb)
        
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        if dialog.exec_() == QDialog.Accepted:
            name = name_edit.text().strip()
            if name:
                required_text = "是" if required_cb.isChecked() else "否"
                item = QTreeWidgetItem(self.structure_tree.topLevelItem(0), [name, "目录", required_text])
                item.setData(1, Qt.UserRole, "directory")
    
    def _add_directory_under(self, parent_item):
        """在指定项下添加目录"""
        from PyQt5.QtWidgets import QInputDialog, QDialog, QVBoxLayout, QLabel, QCheckBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("添加子目录")
        layout = QVBoxLayout(dialog)
        
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("目录名称:")
        layout.addWidget(QLabel("目录名称:"))
        layout.addWidget(name_edit)
        
        required_cb = QCheckBox("必填目录")
        layout.addWidget(required_cb)
        
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        if dialog.exec_() == QDialog.Accepted:
            name = name_edit.text().strip()
            if name:
                required_text = "是" if required_cb.isChecked() else "否"
                item = QTreeWidgetItem(parent_item, [name, "目录", required_text])
                item.setData(1, Qt.UserRole, "directory")
                parent_item.setExpanded(True)
    
    def _add_file_template(self):
        """添加文件模板"""
        from PyQt5.QtWidgets import QInputDialog
        
        name, ok = QInputDialog.getText(self, "添加文件", "文件名称:")
        if ok and name:
            item = QTreeWidgetItem(self.structure_tree.topLevelItem(0), [name, "文件模板", ""])
            item.setData(1, Qt.UserRole, "file")
            item.setData(2, Qt.UserRole, {"type": "document", "content": ""})
    
    def _add_file_template_under(self, parent_item):
        """在指定项下添加文件模板"""
        from PyQt5.QtWidgets import QInputDialog
        
        name, ok = QInputDialog.getText(self, "添加文件", "文件名称:")
        if ok and name:
            item = QTreeWidgetItem(parent_item, [name, "文件模板", ""])
            item.setData(1, Qt.UserRole, "file")
            item.setData(2, Qt.UserRole, {"type": "document", "content": ""})
            parent_item.setExpanded(True)
    
    def _delete_selected_item(self):
        """删除选中项"""
        item = self.structure_tree.currentItem()
        if item and item != self.structure_tree.topLevelItem(0):
            self._delete_item(item)
    
    def _delete_item(self, item):
        """删除项"""
        parent = item.parent()
        if parent:
            parent.removeChild(item)
    
    def _rename_item(self, item):
        """重命名项"""
        from PyQt5.QtWidgets import QInputDialog
        
        new_name, ok = QInputDialog.getText(self, "重命名", "新名称:", text=item.text(0))
        if ok and new_name:
            item.setText(0, new_name)
    
    def _insert_variable(self):
        """插入变量"""
        current_item = self.var_list.currentItem()
        if current_item:
            var_name = current_item.data(Qt.UserRole)
            self.file_content_edit.insertPlainText(f"{{{var_name}}}")
    
    def _collect_structure(self):
        """收集目录结构数据"""
        structure = []
        templates = []
        
        def collect_items(item, parent_path=""):
            for i in range(item.childCount()):
                child = item.child(i)
                name = child.text(0)
                item_type = child.data(1, Qt.UserRole)
                current_path = f"{parent_path}/{name}" if parent_path else name
                
                if item_type == "directory":
                    required = child.text(2) == "是"
                    structure.append({
                        "path": current_path,
                        "required": required,
                        "description": ""
                    })
                    collect_items(child, current_path)
                elif item_type == "file":
                    tmpl_data = child.data(2, Qt.UserRole) or {}
                    templates.append({
                        "path": current_path,
                        "type": tmpl_data.get("type", "document"),
                        "content": tmpl_data.get("content", "")
                    })
        
        root = self.structure_tree.topLevelItem(0)
        if root:
            collect_items(root)
        
        return structure, templates
    
    def _collect_business_lines(self):
        """收集业务线 - 动态从枚举生成的 CheckBox 收集"""
        lines = []
        for bl_value, cb in self.business_line_checkboxes.items():
            if cb.isChecked():
                lines.append(bl_value)
        return lines
    
    def _save_template(self):
        """保存模板"""
        template_id = self.id_input.text().strip()
        name = self.name_input.text().strip()
        
        if not template_id:
            QMessageBox.warning(self, "警告", "请输入模板ID")
            return
        
        if not name:
            QMessageBox.warning(self, "警告", "请输入模板名称")
            return
        
        structure, templates = self._collect_structure()
        
        template_data = {
            "id": template_id,
            "name": name,
            "version": self.version_input.text().strip(),
            "compiler": self.compiler_input.currentText() or None,
            "scene": self.scene_input.text().strip() or None,
            "description": self.desc_input.toPlainText().strip() or None,
            "is_builtin": False,
            "business_lines": self._collect_business_lines(),
            "structure": structure,
            "templates": templates
        }
        
        if self.is_new:
            success, error = TemplateService.create_template(template_data)
        else:
            success, error = TemplateService.update_template(template_id, template_data)
        
        if error:
            QMessageBox.critical(self, "错误", f"保存失败: {error}")
            return
        
        self.template_saved.emit(template_id)
        QMessageBox.information(self, "成功", "模板已保存")
        self.accept()
    
    def _save_as_template(self):
        """另存为新模板"""
        from PyQt5.QtWidgets import QInputDialog
        
        new_id, ok = QInputDialog.getText(self, "另存为", "新模板ID:", text=f"{self.id_input.text()}_copy")
        if ok and new_id:
            self.id_input.setText(new_id)
            self.is_new = True
            self.is_builtin = False
            self.id_input.setReadOnly(False)
            self._save_template()
    
    def _apply_readonly_mode(self):
        """应用只读模式"""
        self.id_input.setReadOnly(True)
        self.name_input.setReadOnly(True)
        self.version_input.setReadOnly(True)
        self.compiler_input.setEnabled(False)
        self.scene_input.setReadOnly(True)
        self.desc_input.setReadOnly(True)

        # 动态禁用所有业务线 CheckBox
        if hasattr(self, 'business_line_checkboxes'):
            for cb in self.business_line_checkboxes.values():
                cb.setEnabled(False)

        self.add_dir_btn.setEnabled(False)
        self.add_file_btn.setEnabled(False)
        self.delete_item_btn.setEnabled(False)

        self.file_content_edit.setReadOnly(True)
        self.file_type_combo.setEnabled(False)
