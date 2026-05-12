# -*- coding: utf-8 -*-
"""
模板编辑器对话框
"""
import re
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QTextEdit, QTreeWidget, QTreeWidgetItem,
    QTabWidget, QWidget, QFormLayout, QCheckBox, QComboBox,
    QMessageBox, QSplitter, QGroupBox, QListWidget, QListWidgetItem,
    QFileDialog, QMenu, QDialogButtonBox, QInputDialog,
    QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import (
    QIcon, QFont, QColor, QPalette, QTextCharFormat,
    QSyntaxHighlighter, QTextCursor, QKeySequence, QTextDocument
)

from src.services.template_service import TemplateService
from src.core.constants import BusinessLine
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class PlaceholderHighlighter(QSyntaxHighlighter):
    """占位符语法高亮器 - 高亮 {xxx} 格式的变量"""

    PLACEHOLDER_PATTERN = re.compile(r'\{[a-zA-Z_][a-zA-Z0-9_]*\}')

    def __init__(self, parent=None):
        super().__init__(parent)
        self.placeholder_format = QTextCharFormat()
        self.placeholder_format.setBackground(QColor("#E3F2FD"))
        self.placeholder_format.setForeground(QColor("#1565C0"))
        self.placeholder_format.setFontWeight(QFont.Bold)

        self.brace_format = QTextCharFormat()
        self.brace_format.setForeground(QColor("#1976D2"))

    def highlightBlock(self, text):
        for match in self.PLACEHOLDER_PATTERN.finditer(text):
            start = match.start()
            length = match.end() - start
            self.setFormat(start, length, self.placeholder_format)


class FindReplaceWidget(QWidget):
    """搜索替换工具栏"""

    find_next = pyqtSignal()
    find_prev = pyqtSignal()
    replace_current = pyqtSignal()
    replace_all = pyqtSignal()
    close_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)

        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("查找...")
        self.find_input.setMinimumWidth(200)
        self.find_input.returnPressed.connect(self.find_next.emit)
        layout.addWidget(self.find_input)

        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("替换为...")
        self.replace_input.setMinimumWidth(150)
        layout.addWidget(self.replace_input)

        self.find_next_btn = QPushButton("↓")
        self.find_next_btn.setToolTip("查找下一个 (F3)")
        self.find_next_btn.setFixedWidth(28)
        self.find_next_btn.clicked.connect(self.find_next.emit)
        layout.addWidget(self.find_next_btn)

        self.replace_btn = QPushButton("替换")
        self.replace_btn.clicked.connect(self.replace_current.emit)
        layout.addWidget(self.replace_btn)

        self.replace_all_btn = QPushButton("全部")
        self.replace_all_btn.setToolTip("全部替换")
        self.replace_all_btn.clicked.connect(self.replace_all.emit)
        layout.addWidget(self.replace_all_btn)

        self.close_btn = QPushButton("×")
        self.close_btn.setFixedWidth(24)
        self.close_btn.clicked.connect(self.close_requested.emit)
        layout.addWidget(self.close_btn)


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

    def __init__(self, template_id=None, parent=None, readonly=False, is_clone_mode=False):
        super().__init__(parent)
        self.template_id = template_id
        self.template_data = None
        self.readonly = readonly
        self.is_new = template_id is None
        self.is_builtin = False
        self.is_clone_mode = is_clone_mode
        self.current_file_path = ""
        self.highlighter = None
        self.find_widget = None

        self._init_ui()
        self._load_template()

    def _init_ui(self):
        """初始化UI"""
        if self.is_clone_mode:
            self.setWindowTitle("模板编辑器 [副本模式 - 将保存为新模板]")
        elif not self.readonly:
            self.setWindowTitle("模板编辑器")
        else:
            self.setWindowTitle("模板查看")

        self.setMinimumSize(1100, 750)

        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        # 副本模式提示条（T02）
        if self.is_clone_mode:
            self._create_clone_banner(layout)

        # 顶部信息栏
        self._create_info_bar(layout)

        # 主内容区域
        splitter = QSplitter(Qt.Horizontal)

        left_panel = self._create_structure_panel()
        splitter.addWidget(left_panel)

        right_panel = self._create_template_panel()
        splitter.addWidget(right_panel)

        splitter.setSizes([380, 720])
        layout.addWidget(splitter)

        # 底部按钮栏
        self._create_button_bar(layout)

        if self.readonly and not self.is_clone_mode:
            self._apply_readonly_mode()

    def _create_clone_banner(self, parent_layout):
        """创建副本模式提示横幅"""
        banner = QFrame()
        banner.setStyleSheet("""
            QFrame {
                background-color: #FFF8E1;
                border: 1px solid #FFB300;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        banner_layout = QHBoxLayout(banner)
        banner_layout.setContentsMargins(12, 8, 12, 8)

        icon_label = QLabel("⚠️")
        icon_label.setStyleSheet("font-size: 18px;")
        banner_layout.addWidget(icon_label)

        msg_text = QLabel(
            "<b>您正在编辑内置模板的副本</b> &nbsp;|&nbsp; "
            "保存后将创建为新的自定义模板，原内置模板不受影响"
        )
        msg_text.setStyleSheet("color: #F57F17; font-size: 13px;")
        msg_text.setWordWrap(True)
        banner_layout.addWidget(msg_text, 1)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(22, 22)
        close_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                color: #F57F17;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { color: #E65100; }
        """)
        close_btn.clicked.connect(banner.hide)
        banner_layout.addWidget(close_btn)

        parent_layout.addWidget(banner)
        self.clone_banner = banner

    def _create_info_bar(self, parent_layout):
        """创建顶部信息栏"""
        info_group = QGroupBox("基本信息")
        info_layout = QFormLayout(info_group)
        info_layout.setSpacing(6)

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("例如: TPL-CUSTOM-001")
        info_layout.addRow("模板ID:", self.id_input)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("例如: 自定义模板")
        info_layout.addRow("模板名称:", self.name_input)

        self.version_input = QLineEdit()
        self.version_input.setText("V1.0.0")
        info_layout.addRow("版本:", self.version_input)

        self.compiler_input = QComboBox()
        self.compiler_input.setEditable(True)
        self.compiler_input.addItems([
            "", "Python", "PyQt5", "Flask", "Django",
            "Step7/TIA Portal + ProFace",
            "Multi",
            "机器人", "全系统"
        ])
        info_layout.addRow("编译器:", self.compiler_input)

        self.scene_input = QLineEdit()
        self.scene_input.setPlaceholderText("例如: 自定义项目")
        info_layout.addRow("适用场景:", self.scene_input)

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("模板描述...")
        self.desc_input.setMaximumHeight(60)
        info_layout.addRow("描述:", self.desc_input)

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
        layout.setContentsMargins(0, 0, 0, 0)

        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("<b>目录结构</b>"))

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
        layout.setContentsMargins(0, 0, 0, 0)

        self.tab_widget = QTabWidget()

        content_tab = QWidget()
        content_layout = QVBoxLayout(content_tab)

        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("文件路径:"))
        self.file_path_input = QLineEdit()
        self.file_path_input.textChanged.connect(self._on_file_path_changed)
        path_layout.addWidget(self.file_path_input)
        content_layout.addLayout(path_layout)

        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("文件类型:"))
        self.file_type_combo = QComboBox()
        self.file_type_combo.addItems(["document", "code", "config", "data", "notebook"])
        type_layout.addWidget(self.file_type_combo)
        type_layout.addStretch()
        content_layout.addLayout(type_layout)

        content_layout.addWidget(QLabel("<b>文件内容:</b>"))
        self.file_content_edit = QTextEdit()
        self.file_content_edit.setFontFamily("Consolas")
        self.file_content_edit.setFontPointSize(10)
        self.file_content_edit.setPlaceholderText(
            "文件模板内容，支持变量占位符如 {project_name}、{project_code} 等"
        )
        content_layout.addWidget(self.file_content_edit)

        # 占位符高亮器 (T03)
        self.highlighter = PlaceholderHighlighter(self.file_content_edit.document())

        # 搜索替换工具栏 (T07)
        self.find_widget = FindReplaceWidget()
        self.find_widget.setVisible(False)
        self.find_widget.find_next.connect(self._find_next)
        self.find_widget.find_prev.connect(self._find_prev)
        self.find_widget.replace_current.connect(self._replace_current)
        self.find_widget.replace_all.connect(self._replace_all)
        self.find_widget.close_requested.connect(lambda: self.find_widget.hide())
        content_layout.addWidget(self.find_widget)

        self.tab_widget.addTab(content_tab, "文件内容")

        var_tab = QWidget()
        var_layout = QVBoxLayout(var_tab)

        var_layout.addWidget(QLabel("<b>支持的变量占位符:</b>"))
        self.var_list = QListWidget()
        for var_name, var_desc in self.SUPPORTED_VARIABLES:
            item = QListWidgetItem(f"{{{var_name}}} - {var_desc}")
            item.setData(Qt.UserRole, var_name)
            self.var_list.addItem(item)
        var_layout.addWidget(self.var_list)

        insert_btn = QPushButton("插入变量到光标位置")
        insert_btn.clicked.connect(self._insert_variable)
        var_layout.addWidget(insert_btn)

        self.tab_widget.addTab(var_tab, "变量说明")

        # 占位符管理标签页 (T04)
        placeholder_tab = self._create_placeholder_tab()
        self.tab_widget.addTab(placeholder_tab, "占位符管理")

        layout.addWidget(self.tab_widget)
        return panel

    def _create_placeholder_tab(self):
        """创建占位符管理标签页 (T04)"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        header = QHBoxLayout()
        header.addWidget(QLabel("<b>当前文件中的占位符</b>"))
        header.addStretch()
        refresh_btn = QPushButton("🔄 刷新扫描")
        refresh_btn.clicked.connect(self._scan_placeholders)
        header.addWidget(refresh_btn)
        layout.addLayout(header)

        self.placeholder_table = QTreeWidget()
        self.placeholder_table.setHeaderLabels(["占位符", "说明", "预览值"])
        self.placeholder_table.setColumnWidth(0, 180)
        self.placeholder_table.setColumnWidth(1, 120)
        self.placeholder_table.setHeaderHidden(False)
        self.placeholder_table.itemChanged.connect(self._on_placeholder_value_changed)
        layout.addWidget(self.placeholder_table)

        preview_layout = QHBoxLayout()
        preview_layout.addWidget(QLabel("<b>替换预览:</b>"))
        self.preview_label = QLabel("")
        self.preview_label.setWordWrap(True)
        self.preview_label.setStyleSheet("padding: 8px; background: #F5F5F5; border-radius: 4px;")
        preview_layout.addWidget(self.preview_label, 1)
        layout.addLayout(preview_layout)

        return tab

    def _scan_placeholders(self):
        """扫描当前文件内容中的占位符并显示在表格中"""
        self.placeholder_table.clear()
        content = self.file_content_edit.toPlainText()
        found = set(re.findall(r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}', content))

        var_dict = dict(self.SUPPORTED_VARIABLES)
        for ph in sorted(found):
            desc = var_dict.get(ph, "自定义变量")
            item = QTreeWidgetItem([f"{{{ph}}}", desc, ""])
            item.setData(0, Qt.UserRole, ph)
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.placeholder_table.addTopLevelItem(item)

        self._update_preview()

    def _on_placeholder_value_changed(self, item, column):
        """占位符值变化时更新预览"""
        if column == 2:
            self._update_preview()

    def _update_preview(self):
        """更新替换预览"""
        content = self.file_content_edit.toPlainText()
        result = content

        for i in range(self.placeholder_table.topLevelItemCount()):
            item = self.placeholder_table.topLevelItem(i)
            ph_name = item.data(0, Qt.UserRole)
            value = item.text(2)
            result = result.replace(f"{{{ph_name}}}", value or f"{{{ph_name}}}")

        self.preview_label.setText(result if result != content else "(未设置预览值)")

    def _on_file_path_changed(self, new_path):
        """文件路径变化时记录 (T05)"""
        self.current_file_path = new_path

    def _create_button_bar(self, parent_layout):
        """创建底部按钮栏"""
        button_layout = QHBoxLayout()

        button_layout.addStretch()

        if not self.readonly or self.is_clone_mode:
            self.save_btn = QPushButton("💾 保存")
            self.save_btn.setDefault(True)
            self.save_btn.clicked.connect(self._save_template)
            button_layout.addWidget(self.save_btn)

            self.save_as_btn = QPushButton("另存为...")
            self.save_as_btn.clicked.connect(self._save_as_template)
            button_layout.addWidget(self.save_as_btn)

        self.cancel_btn = QPushButton("关闭")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        parent_layout.addLayout(button_layout)

    def keyPressEvent(self, event):
        """键盘快捷键处理 (T07)"""
        if event.modifiers() == Qt.ControlModifier:
            if event.key() == Qt.Key_F:
                self._toggle_find_replace()
                return
            elif event.key() == Qt.Key_H:
                self._toggle_find_replace()
                return
        super().keyPressEvent(event)

    def _toggle_find_replace(self):
        """切换搜索替换面板可见性"""
        if self.find_widget.isVisible():
            self.find_widget.hide()
        else:
            self.find_widget.show()
            self.find_widget.find_input.setFocus()

    def _find_next(self):
        """查找下一个"""
        keyword = self.find_widget.find_input.text()
        if keyword:
            cursor = self.file_content_edit.textCursor()
            found = self.file_content_edit.find(keyword)
            if not found:
                cursor.movePosition(QTextCursor.Start)
                self.file_content_edit.setTextCursor(cursor)
                self.file_content_edit.find(keyword)

    def _find_prev(self):
        """查找上一个"""
        keyword = self.find_widget.find_input.text()
        if keyword:
            flags = QTextDocument.FindBackward
            self.file_content_edit.find(keyword, flags)

    def _replace_current(self):
        """替换当前选中"""
        keyword = self.find_widget.find_input.text()
        replacement = self.find_widget.replace_input.text()
        cursor = self.file_content_edit.textCursor()
        if cursor.hasSelection() and cursor.selectedText() == keyword:
            cursor.insertText(replacement)

    def _replace_all(self):
        """全部替换"""
        keyword = self.find_widget.find_input.text()
        replacement = self.find_widget.replace_input.text()
        if keyword:
            content = self.file_content_edit.toPlainText()
            new_content = content.replace(keyword, replacement)
            self.file_content_edit.setPlainText(new_content)

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

                if self.is_clone_mode:
                    self.id_input.setText(f"{template.template_id}_CUSTOM")
                    self.name_input.setText(f"{template.name} (自定义)")
                    self.id_input.setReadOnly(False)

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

            self.current_file_path = path
            self.file_path_input.setText(path)
            self.file_path_input.setReadOnly(False)
            if tmpl_data:
                self.file_type_combo.setCurrentText(tmpl_data.get("type", "document"))
                self.file_content_edit.setPlainText(tmpl_data.get("content", ""))
            else:
                self.file_content_edit.setPlainText("")

            self._scan_placeholders()
        else:
            self.file_path_input.setText("")
            self.file_content_edit.setPlainText("")
            self.placeholder_table.clear()
            self.preview_label.setText("")

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

        if self.readonly and not self.is_clone_mode:
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
            self._delete_item_with_confirm(item)

    def _add_directory(self):
        """添加目录"""
        dialog = QDialog(self)
        dialog.setWindowTitle("添加目录")
        dialog.setFixedWidth(360)
        layout = QVBoxLayout(dialog)

        name_edit = QLineEdit()
        name_edit.setPlaceholderText("目录名称:")
        layout.addWidget(QLabel("目录名称:"))
        layout.addWidget(name_edit)

        required_cb = QCheckBox("必填目录")
        required_cb.setToolTip("必填目录在创建项目时会自动生成，不可跳过")
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
        dialog = QDialog(self)
        dialog.setWindowTitle("添加子目录")
        dialog.setFixedWidth(360)
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
        name, ok = QInputDialog.getText(self, "添加文件", "文件名称(建议使用中文纯名称，如：需求分析文档.md):")
        if ok and name:
            item = QTreeWidgetItem(self.structure_tree.topLevelItem(0), [name, "文件模板", ""])
            item.setData(1, Qt.UserRole, "file")
            item.setData(2, Qt.UserRole, {"type": "document", "content": ""})

    def _add_file_template_under(self, parent_item):
        """在指定项下添加文件模板"""
        name, ok = QInputDialog.getText(self, "添加文件", "文件名称(建议使用中文纯名称):")
        if ok and name:
            item = QTreeWidgetItem(parent_item, [name, "文件模板", ""])
            item.setData(1, Qt.UserRole, "file")
            item.setData(2, Qt.UserRole, {"type": "document", "content": ""})
            parent_item.setExpanded(True)

    def _delete_selected_item(self):
        """删除选中项"""
        item = self.structure_tree.currentItem()
        if item and item != self.structure_tree.topLevelItem(0):
            self._delete_item_with_confirm(item)

    def _delete_item_with_confirm(self, item):
        """删除项（带确认和级联警告）(T06)"""
        name = item.text(0)
        has_children = item.childCount() > 0

        msg = f"确定要删除「{name}」吗？"
        if has_children:
            msg += f"\n\n⚠️ 该项下有 {item.childCount()} 个子项，将一并删除！"

        reply = QMessageBox.question(
            self, "确认删除", msg,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            parent = item.parent()
            if parent:
                parent.removeChild(item)

    def _delete_item(self, item):
        """删除项（无确认）"""
        parent = item.parent()
        if parent:
            parent.removeChild(item)

    def _rename_item(self, item):
        """重命名项"""
        new_name, ok = QInputDialog.getText(self, "重命名", "新名称:", text=item.text(0))
        if ok and new_name:
            item.setText(0, new_name)

    def _insert_variable(self):
        """插入变量到光标位置"""
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
        """收集业务线"""
        lines = []
        for bl_value, cb in self.business_line_checkboxes.items():
            if cb.isChecked():
                lines.append(bl_value)
        return lines

    def _validate_before_save(self):
        """保存前校验 (T08)"""
        errors = []
        warnings = []

        template_id = self.id_input.text().strip()
        name = self.name_input.text().strip()

        if not template_id:
            errors.append("模板ID不能为空")
        if not name:
            errors.append("模板名称不能为空")

        if "/" in template_id or "\\" in template_id:
            errors.append("模板ID不能包含路径分隔符 / 或 \\")

        structure, templates = self._collect_structure()

        if not structure and not templates:
            warnings.append("模板没有任何目录或文件定义")

        supported_vars = set(v[0] for v in self.SUPPORTED_VARIABLES)
        for tmpl in templates:
            path = tmpl.get("path", "")
            content = tmpl.get("content", "")

            path_ph = set(re.findall(r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}', path))
            content_ph = set(re.findall(r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}', content))

            unknown_ph = (path_ph | content_ph) - supported_vars
            if unknown_ph:
                warnings.append(
                    f"文件「{path}」使用了未定义的占位符: "
                    + ", ".join(f"{{{p}}}" for p in unknown_ph)
                )

        return errors, warnings

    def _save_template(self):
        """保存模板"""
        errors, warnings = self._validate_before_save()

        if errors:
            QMessageBox.critical(self, "校验失败", "\n".join(f"❌ {e}" for e in errors))
            return

        if warnings:
            warn_msg = "\n".join(f"⚠️ {w}" for w in warnings)
            reply = QMessageBox.warning(
                self, "存在警告",
                f"{warn_msg}\n\n是否继续保存？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        template_id = self.id_input.text().strip()
        name = self.name_input.text().strip()

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

        if self.is_clone_mode or self.is_new:
            success, error = TemplateService.create_template(template_data)
        else:
            success, error = TemplateService.update_template(template_id, template_data)

        if error:
            QMessageBox.critical(self, "错误", f"保存失败: {error}")
            return

        self.template_saved.emit(template_id)
        mode_msg = " (已保存为新自定义模板)" if self.is_clone_mode else ""
        QMessageBox.information(self, "成功", f"模板已保存{mode_msg}")
        self.accept()

    def _save_as_template(self):
        """另存为新模板"""
        new_id, ok = QInputDialog.getText(
            self, "另存为", "新模板ID:",
            text=f"{self.id_input.text()}_copy"
        )
        if ok and new_id:
            self.id_input.setText(new_id)
            self.is_new = True
            self.is_builtin = False
            self.is_clone_mode = False
            self.id_input.setReadOnly(False)
            if hasattr(self, 'clone_banner'):
                self.clone_banner.hide()
            self._save_template()

    def _apply_readonly_mode(self):
        """应用只读模式"""
        self.id_input.setReadOnly(True)
        self.name_input.setReadOnly(True)
        self.version_input.setReadOnly(True)
        self.compiler_input.setEnabled(False)
        self.scene_input.setReadOnly(True)
        self.desc_input.setReadOnly(True)

        if hasattr(self, 'business_line_checkboxes'):
            for cb in self.business_line_checkboxes.values():
                cb.setEnabled(False)

        self.add_dir_btn.setEnabled(False)
        self.add_file_btn.setEnabled(False)
        self.delete_item_btn.setEnabled(False)

        self.file_content_edit.setReadOnly(True)
        self.file_type_combo.setEnabled(False)
        self.file_path_input.setReadOnly(True)
