# -*- coding: utf-8 -*-
"""
规范中心控件
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTreeWidget, QTreeWidgetItem, QTextEdit, QLineEdit,
    QPushButton, QLabel, QComboBox, QTabWidget,
    QScrollArea, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from src.services.spec_service import SpecService
from src.utils.logger import setup_logger
from src.gui.spec_sync_dialog import show_spec_sync_dialog

logger = setup_logger(__name__)

class SpecCenterWidget(QWidget):
    """规范中心控件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._load_data()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        toolbar = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索规范...")
        self.search_input.textChanged.connect(self._on_search)
        toolbar.addWidget(self.search_input)
        
        self.category_combo = QComboBox()
        self.category_combo.addItem("全部分类", None)
        self.category_combo.currentIndexChanged.connect(self._on_category_changed)
        toolbar.addWidget(self.category_combo)
        
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self._load_data)
        toolbar.addWidget(self.refresh_btn)
        
        self.sync_btn = QPushButton("规范同步")
        self.sync_btn.clicked.connect(self._on_sync_specs)
        toolbar.addWidget(self.sync_btn)
        
        layout.addLayout(toolbar)
        
        splitter = QSplitter(Qt.Horizontal)
        
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.spec_tree = QTreeWidget()
        self.spec_tree.setHeaderLabels(["规范名称", "版本"])
        self.spec_tree.setColumnWidth(0, 200)
        self.spec_tree.itemClicked.connect(self._on_spec_selected)
        left_layout.addWidget(self.spec_tree)
        
        splitter.addWidget(left_panel)
        
        right_panel = QTabWidget()
        
        self.detail_tab = QWidget()
        detail_layout = QVBoxLayout(self.detail_tab)
        
        self.spec_title = QLabel()
        self.spec_title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        self.spec_title.setWordWrap(True)
        detail_layout.addWidget(self.spec_title)
        
        self.spec_info = QLabel()
        self.spec_info.setStyleSheet("color: #666;")
        detail_layout.addWidget(self.spec_info)
        
        self.spec_content = QTextEdit()
        self.spec_content.setReadOnly(True)
        self.spec_content.setFont(QFont("Consolas", 10))
        detail_layout.addWidget(self.spec_content)
        
        right_panel.addTab(self.detail_tab, "规范详情")
        
        self.quick_ref_tab = QWidget()
        quick_ref_layout = QVBoxLayout(self.quick_ref_tab)
        
        self.quick_ref_content = QTextEdit()
        self.quick_ref_content.setReadOnly(True)
        self.quick_ref_content.setFont(QFont("Microsoft YaHei", 10))
        quick_ref_layout.addWidget(self.quick_ref_content)
        
        right_panel.addTab(self.quick_ref_tab, "速查手册")
        
        splitter.addWidget(right_panel)
        
        splitter.setSizes([250, 750])
        
        layout.addWidget(splitter)
    
    def _load_data(self):
        """加载数据"""
        try:
            SpecService.initialize_builtin_specs()
            
            self._load_categories()
            self._load_specs()
            self._load_quick_reference()
            
            logger.info("规范中心数据加载完成")
            
        except Exception as e:
            logger.exception(f"加载规范数据失败: {e}")
            QMessageBox.warning(self, "错误", f"加载规范数据失败: {str(e)}")
    
    def _load_categories(self):
        """加载分类"""
        self.category_combo.clear()
        self.category_combo.addItem("全部分类", None)
        
        categories = SpecService.list_categories()
        for category in categories:
            self.category_combo.addItem(category, category)
    
    def _load_specs(self, category: str = None, keyword: str = None):
        """加载规范列表"""
        self.spec_tree.clear()
        
        specs = SpecService.list_specs(category=category, keyword=keyword, is_active=True)
        
        category_items = {}
        
        for spec in specs:
            if spec.category not in category_items:
                category_item = QTreeWidgetItem([spec.category, ""])
                category_item.setFont(0, QFont("Microsoft YaHei", 10, QFont.Bold))
                category_item.setData(0, Qt.UserRole, "category")
                self.spec_tree.addTopLevelItem(category_item)
                category_items[spec.category] = category_item
                category_item.setExpanded(True)
            
            spec_item = QTreeWidgetItem([spec.name, spec.version])
            spec_item.setData(0, Qt.UserRole, spec.spec_id)
            category_items[spec.category].addChild(spec_item)
        
        self.spec_tree.expandAll()
    
    def _on_sync_specs(self):
        """规范同步"""
        try:
            show_spec_sync_dialog(self)
        except Exception as e:
            logger.exception(f"打开规范同步对话框失败: {e}")
            QMessageBox.warning(self, "错误", f"打开规范同步对话框失败: {str(e)}")
    
    def _load_quick_reference(self):
        """加载速查手册"""
        quick_refs = SpecService.get_quick_reference()
        
        content = "# 规范速查手册\n\n"
        
        current_category = None
        for ref in quick_refs:
            if ref["category"] != current_category:
                current_category = ref["category"]
                content += f"## {current_category}\n\n"
            
            content += f"### {ref['name']}\n\n"
            
            if ref["key_points"]:
                content += "**核心要点：**\n\n"
                for point in ref["key_points"]:
                    content += f"- {point}\n"
                content += "\n"
            
            content += "---\n\n"
        
        self.quick_ref_content.setMarkdown(content)
    
    def _on_spec_selected(self, item: QTreeWidgetItem, column: int):
        """选择规范"""
        spec_id = item.data(0, Qt.UserRole)
        
        if spec_id and spec_id != "category":
            spec = SpecService.get_spec(spec_id)
            if spec:
                self._show_spec_detail(spec)
    
    def _show_spec_detail(self, spec):
        """显示规范详情"""
        self.spec_title.setText(spec.name)
        self.spec_info.setText(f"分类: {spec.category} | 版本: {spec.version} | ID: {spec.spec_id}")
        self.spec_content.setMarkdown(spec.content)
    
    def _on_search(self, keyword: str):
        """搜索规范"""
        category = self.category_combo.currentData()
        self._load_specs(category=category, keyword=keyword if keyword else None)
    
    def _on_category_changed(self, index: int):
        """分类变更"""
        category = self.category_combo.currentData()
        keyword = self.search_input.text()
        self._load_specs(category=category, keyword=keyword if keyword else None)
        
        if category:
            quick_refs = SpecService.get_quick_reference(category=category)
            content = f"# {category}规范速查\n\n"
            for ref in quick_refs:
                content += f"## {ref['name']}\n\n"
                if ref["key_points"]:
                    for point in ref["key_points"]:
                        content += f"- {point}\n"
                    content += "\n"
            self.quick_ref_content.setMarkdown(content)
        else:
            self._load_quick_reference()
