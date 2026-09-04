# -*- coding: utf-8 -*-
"""
模板管理控件
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QLineEdit, QComboBox, QLabel, QMessageBox, QMenu,
    QDialog, QFormLayout, QTextEdit, QCheckBox, QInputDialog,
    QFileDialog, QStyle
)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QColor, QBrush

from src.services.template_service import TemplateService
from src.ui.widgets.template_editor import TemplateEditorDialog
from src.utils.logger import setup_logger
from src.utils.file_utils import write_file
from src.core.constants import BusinessLine

logger = setup_logger(__name__)

class TemplateManagerWidget(QWidget):
    """模板管理控件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.templates = []
        self._init_ui()
        self._load_templates()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 顶部工具栏
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(10, 10, 10, 10)
        
        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索模板名称...")
        self.search_input.textChanged.connect(self._filter_templates)
        self.search_input.setMinimumWidth(200)
        toolbar_layout.addWidget(self.search_input)
        
        # 业务线筛选
        toolbar_layout.addWidget(QLabel("业务线:"))
        self.business_line_filter = QComboBox()
        self.business_line_filter.addItem("全部", "")
        for bl in BusinessLine:
            self.business_line_filter.addItem(f"{bl.value} - {bl.name}", bl.value)
        self.business_line_filter.currentIndexChanged.connect(self._filter_templates)
        toolbar_layout.addWidget(self.business_line_filter)
        
        # 编译器筛选
        toolbar_layout.addWidget(QLabel("编译器:"))
        self.compiler_filter = QComboBox()
        self.compiler_filter.addItem("全部", "")
        self.compiler_filter.currentIndexChanged.connect(self._filter_templates)
        toolbar_layout.addWidget(self.compiler_filter)
        
        # 场景筛选
        toolbar_layout.addWidget(QLabel("场景:"))
        self.scene_filter = QComboBox()
        self.scene_filter.addItem("全部", "")
        self.scene_filter.currentIndexChanged.connect(self._filter_templates)
        toolbar_layout.addWidget(self.scene_filter)
        
        toolbar_layout.addStretch()
        
        # 按钮
        self.new_btn = QPushButton("新建模板")
        self.new_btn.setDefault(True)
        self.new_btn.clicked.connect(self._on_new_template)
        toolbar_layout.addWidget(self.new_btn)
        
        self.import_btn = QPushButton("导入模板")
        self.import_btn.clicked.connect(self._on_import_template)
        toolbar_layout.addWidget(self.import_btn)
        
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self._load_templates)
        toolbar_layout.addWidget(self.refresh_btn)
        
        # 重置内置模板按钮
        self.reset_btn = QPushButton("重置内置模板")
        self.reset_btn.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.reset_btn.clicked.connect(self._reset_builtin_templates)
        toolbar_layout.addWidget(self.reset_btn)
        
        layout.addLayout(toolbar_layout)
        
        # 模板表格
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "模板ID", "模板名称", "版本", "编译器", "适用场景", "业务线", "内置", "描述", "操作"
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.Stretch)
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)
        
        # 右键菜单
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        
        self.table.setContentsMargins(10, 0, 10, 10)
        layout.addWidget(self.table)
        
        # 底部统计栏
        self.stats_label = QLabel("")
        self.stats_label.setAlignment(Qt.AlignCenter)
        self.stats_label.setStyleSheet("padding: 5px; color: #666; font-size: 12px;")
        layout.addWidget(self.stats_label)
    
    def _load_templates(self):
        """加载模板列表"""
        self.templates = TemplateService.list_templates()
        self._update_filter_options()
        self._display_templates(self.templates)
    
    def _update_filter_options(self):
        """更新筛选选项"""
        compilers = set()
        scenes = set()
        
        for template in self.templates:
            if template.compiler:
                compilers.add(template.compiler)
            if template.scene:
                scenes.add(template.scene)
        
        self.compiler_filter.blockSignals(True)
        self.scene_filter.blockSignals(True)
        
        self.compiler_filter.clear()
        self.compiler_filter.addItem("全部", "")
        for compiler in sorted(compilers):
            self.compiler_filter.addItem(compiler, compiler)
        
        self.scene_filter.clear()
        self.scene_filter.addItem("全部", "")
        for scene in sorted(scenes):
            self.scene_filter.addItem(scene, scene)
        
        self.compiler_filter.blockSignals(False)
        self.scene_filter.blockSignals(False)
    
    def _display_templates(self, templates):
        """显示模板列表"""
        self.table.setRowCount(len(templates))
        
        # 清除旧的cell widgets
        for row in range(self.table.rowCount()):
            self.table.removeCellWidget(row, 8)
        
        op_col = 8  # 操作列
        
        for row, tmpl in enumerate(templates):
            self.table.setItem(row, 0, QTableWidgetItem(tmpl.template_id))
            self.table.setItem(row, 1, QTableWidgetItem(tmpl.name))
            self.table.setItem(row, 2, QTableWidgetItem(tmpl.version))
            self.table.setItem(row, 3, QTableWidgetItem(tmpl.compiler or "-"))
            self.table.setItem(row, 4, QTableWidgetItem(tmpl.scene or "-"))
            
            business_lines = tmpl.business_lines or []
            bl_text = ", ".join(business_lines) if business_lines else "-"
            self.table.setItem(row, 5, QTableWidgetItem(bl_text))
            
            self.table.setItem(row, 6, QTableWidgetItem("是" if tmpl.is_builtin else "否"))
            self.table.setItem(row, 7, QTableWidgetItem(tmpl.description or "-"))
            
            # 操作按钮
            btn_edit = QPushButton("编辑")
            btn_export = QPushButton("导出")
            btn_copy = QPushButton("复制")
            btn_delete = QPushButton("删除")
            
            # 连接信号
            btn_edit.clicked.connect(lambda checked, t=tmpl: self._edit_template(t))
            btn_export.clicked.connect(lambda checked, t=tmpl: self._export_template(t))
            btn_copy.clicked.connect(lambda checked, t=tmpl: self._duplicate_template(t))
            btn_delete.clicked.connect(lambda checked, t=tmpl: self._delete_template(t))
            
            # 内置模板：允许编辑非标识字段，禁止删除
            is_builtin = getattr(tmpl, 'is_builtin', False)
            if is_builtin:
                btn_edit.setEnabled(True)
                btn_edit.setToolTip("编辑内置模板（仅可修改名称、描述等非标识字段）")
                btn_delete.setEnabled(False)
                btn_delete.setToolTip("内置模板不能删除(可使用重置功能)")
            
            # 创建水平布局容器widget来容纳4个按钮
            btn_container = QWidget()
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(2, 0, 2, 0)
            btn_layout.setSpacing(3)
            btn_layout.addWidget(btn_edit)
            btn_layout.addWidget(btn_export)
            btn_layout.addWidget(btn_copy)
            btn_layout.addWidget(btn_delete)
            btn_layout.addStretch()
            self.table.setCellWidget(row, op_col, btn_container)
            
            self.table.item(row, 0).setData(Qt.UserRole, tmpl.template_id)
            
            # 内置模板行视觉区分（修改2）
            if is_builtin:
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item:
                        item.setBackground(QBrush(QColor("#E8F4FD")))
                        # 第一列名称前加★
                        if col == 1:
                            text = item.text()
                            if not text.startswith("★"):
                                item.setText("★ " + text)
        
        self.table.resizeRowsToContents()
        
        # 更新统计信息（修改4）
        total = len(templates)
        builtin_count = sum(1 for t in templates if getattr(t, 'is_builtin', False))
        custom_count = total - builtin_count
        self.stats_label.setText(f"共 {total} 个模板 ({builtin_count} 个内置 / {custom_count} 个自定义)")
    
    def _filter_templates(self):
        """筛选模板"""
        keyword = self.search_input.text().lower()
        business_line = self.business_line_filter.currentData()
        compiler = self.compiler_filter.currentData()
        scene = self.scene_filter.currentData()
        
        filtered = []
        for template in self.templates:
            if keyword:
                if keyword not in template.name.lower():
                    continue
            
            if business_line:
                template_bl = template.business_lines or []
                if business_line not in template_bl:
                    continue
            
            if compiler and template.compiler != compiler:
                continue
            
            if scene and template.scene != scene:
                continue
            
            filtered.append(template)
        
        self._display_templates(filtered)
    
    def _show_context_menu(self, pos: QPoint):
        """显示右键菜单"""
        item = self.table.itemAt(pos)
        if not item:
            return
        
        row = self.table.row(item)
        template_id = self.table.item(row, 0).data(Qt.UserRole)
        template = next((t for t in self.templates if t.template_id == template_id), None)
        if not template:
            return
        
        menu = QMenu(self)
        
        edit_action = menu.addAction("编辑模板")
        export_action = menu.addAction("导出模板")
        duplicate_action = menu.addAction("复制模板")
        delete_action = menu.addAction("删除模板")
        
        # 内置模板：允许编辑非标识字段，禁止删除
        if template.is_builtin:
            edit_action.setEnabled(True)
            delete_action.setEnabled(False)
        
        action = menu.exec_(self.table.mapToGlobal(pos))
        
        if action == edit_action:
            self._edit_template(template)
        elif action == export_action:
            self._export_template(template)
        elif action == duplicate_action:
            self._duplicate_template(template)
        elif action == delete_action:
            self._delete_template(template)
    
    def _on_new_template(self):
        """新建模板"""
        dialog = TemplateEditorDialog(template_id=None, parent=self)
        dialog.template_saved.connect(self._load_templates)
        dialog.exec_()
    
    def _on_import_template(self):
        """导入模板"""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "导入模板",
            "",
            "JSON文件 (*.json)"
        )
        
        if path:
            from src.utils.file_utils import read_file
            json_data = read_file(path)
            if json_data:
                success, error = TemplateService.import_template(json_data)
                if error:
                    QMessageBox.critical(self, "错误", f"导入失败: {error}")
                    return
                
                self._load_templates()
                QMessageBox.information(self, "成功", "模板已导入")
                logger.info(f"模板导入成功: {path}")
    
    def _edit_template(self, template):
        """编辑模板"""
        readonly = template.is_builtin
        dialog = TemplateEditorDialog(
            template_id=template.template_id,
            parent=self,
            readonly=readonly
        )
        dialog.template_saved.connect(self._load_templates)
        dialog.exec_()
    
    def _export_template(self, template):
        """导出模板"""
        json_data, error = TemplateService.export_template(template.template_id)
        if error:
            QMessageBox.critical(self, "错误", f"导出失败: {error}")
            return
        
        path, _ = QFileDialog.getSaveFileName(
            self,
            "导出模板",
            f"{template.name}_{template.version}.json",
            "JSON文件 (*.json)"
        )
        
        if path:
            write_file(path, json_data)
            QMessageBox.information(self, "成功", f"模板已导出到: {path}")
            logger.info(f"模板导出成功: {path}")
    
    def _duplicate_template(self, template):
        """复制模板"""
        new_id, ok = QInputDialog.getText(
            self,
            "复制模板",
            "新模板ID:",
            text=f"{template.template_id}_copy"
        )
        
        if ok and new_id:
            json_data, error = TemplateService.export_template(template.template_id)
            if error:
                QMessageBox.critical(self, "错误", f"复制失败: {error}")
                return
            
            import json
            data = json.loads(json_data)
            
            base_id = new_id
            counter = 1
            while TemplateService.get_template(new_id):
                new_id = f"{base_id}_{counter}"
                counter += 1
            
            data["id"] = new_id
            data["name"] = f"{template.name} (副本)"
            data["is_builtin"] = False
            
            success, error = TemplateService.import_template(json.dumps(data, ensure_ascii=False))
            if error:
                QMessageBox.critical(self, "错误", f"复制失败: {error}")
                return
            
            self._load_templates()
            QMessageBox.information(self, "成功", f"模板已复制为: {new_id}")
            logger.info(f"模板复制成功: {new_id}")
    
    def _delete_template(self, template):
        """删除模板"""
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除模板 {template.template_id} {template.name} 吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, error = TemplateService.delete_template(template.template_id)
            if error:
                QMessageBox.critical(self, "错误", f"删除失败: {error}")
                return
            
            self._load_templates()
            QMessageBox.information(self, "成功", "模板已删除")
            logger.info(f"模板已删除: {template.template_id}")
    
    def _reset_builtin_templates(self):
        """重置所有内置模板为默认值"""
        reply = QMessageBox.question(
            self, '确认重置',
            '确定要重置所有内置模板为默认值吗？\n\n'
            '这将删除所有内置模板并重新创建。\n'
            '自定义模板不受影响。',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            result, error = TemplateService.reset_builtin_templates()
            if error:
                QMessageBox.critical(self, '错误', f'重置失败: {error}')
            else:
                QMessageBox.information(self, '成功', f'已重置 {result} 个内置模板')
                self._load_templates()
