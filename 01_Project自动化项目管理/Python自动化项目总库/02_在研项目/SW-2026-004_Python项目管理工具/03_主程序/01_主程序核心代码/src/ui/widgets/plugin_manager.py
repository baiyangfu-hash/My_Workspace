# -*- coding: utf-8 -*-
"""
插件管理控件
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QLineEdit, QComboBox, QLabel, QMessageBox, QMenu, QProgressDialog
)
from PyQt5.QtCore import Qt, QPoint
import json

from src.services.plugin_service import PluginService
from src.core.constants import PluginStatus
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class PluginManagerWidget(QWidget):
    """插件管理控件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.plugins = []
        self._init_ui()
        self._load_plugins()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 顶部工具栏
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(10, 10, 10, 10)
        
        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索插件名称...")
        self.search_input.textChanged.connect(self._filter_plugins)
        self.search_input.setMinimumWidth(200)
        toolbar_layout.addWidget(self.search_input)
        
        # 状态筛选
        toolbar_layout.addWidget(QLabel("状态:"))
        self.status_filter = QComboBox()
        self.status_filter.addItem("全部", "")
        for status in PluginStatus:
            self.status_filter.addItem(status.value, status.value)
        self.status_filter.currentTextChanged.connect(self._filter_plugins)
        toolbar_layout.addWidget(self.status_filter)
        
        toolbar_layout.addStretch()
        
        # 按钮
        self.install_btn = QPushButton("安装插件")
        self.install_btn.setDefault(True)
        self.install_btn.clicked.connect(self._on_install_plugin)
        toolbar_layout.addWidget(self.install_btn)
        
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self._load_plugins)
        toolbar_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(toolbar_layout)
        
        # 插件表格
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "插件ID", "插件名称", "版本", "作者", "状态", "内置", "操作"
        ])
        
        # 设置表头
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        
        # 右键菜单
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        
        self.table.setContentsMargins(10, 0, 10, 10)
        layout.addWidget(self.table)
    
    def _load_plugins(self):
        """加载插件列表"""
        self.plugins = PluginService.list_plugins()
        self._display_plugins(self.plugins)
    
    def _display_plugins(self, plugins):
        """显示插件列表"""
        self.table.setRowCount(len(plugins))
        
        for row, plugin in enumerate(plugins):
            self.table.setItem(row, 0, QTableWidgetItem(plugin.plugin_id))
            self.table.setItem(row, 1, QTableWidgetItem(plugin.name))
            self.table.setItem(row, 2, QTableWidgetItem(plugin.version))
            self.table.setItem(row, 3, QTableWidgetItem(plugin.author or "-"))
            self.table.setItem(row, 4, QTableWidgetItem(plugin.status.value))
            self.table.setItem(row, 5, QTableWidgetItem("是" if plugin.is_builtin else "否"))
            
            # 操作按钮
            if plugin.status == PluginStatus.ENABLED:
                action_text = "禁用"
            elif plugin.status == PluginStatus.DISABLED:
                action_text = "启用"
            else:
                action_text = "操作"
            
            self.table.setItem(row, 6, QTableWidgetItem(action_text))
            
            # 存储插件ID
            self.table.item(row, 0).setData(Qt.UserRole, plugin.plugin_id)
        
        self.table.resizeRowsToContents()
    
    def _filter_plugins(self):
        """筛选插件"""
        keyword = self.search_input.text().lower()
        status = self.status_filter.currentData()
        
        filtered = []
        for plugin in self.plugins:
            # 关键词筛选
            if keyword:
                if keyword not in plugin.name.lower():
                    continue
            
            # 状态筛选
            if status and plugin.status.value != status:
                continue
            
            filtered.append(plugin)
        
        self._display_plugins(filtered)
    
    def _show_context_menu(self, pos: QPoint):
        """显示右键菜单"""
        item = self.table.itemAt(pos)
        if not item:
            return
        
        row = self.table.row(item)
        plugin_id = self.table.item(row, 0).data(Qt.UserRole)
        plugin = next((p for p in self.plugins if p.plugin_id == plugin_id), None)
        if not plugin:
            return
        
        menu = QMenu(self)
        
        if plugin.status == PluginStatus.ENABLED:
            toggle_action = menu.addAction("禁用插件")
            # 检查插件是否提供UI组件
            plugin_instance = PluginService.get_plugin(plugin.plugin_id)
            if plugin_instance and "instance" in plugin_instance:
                instance = plugin_instance["instance"]
                if hasattr(instance, "get_widget"):
                    use_action = menu.addAction("使用插件")
        elif plugin.status == PluginStatus.DISABLED:
            toggle_action = menu.addAction("启用插件")
        else:
            toggle_action = menu.addAction("修复插件")
        
        config_action = menu.addAction("配置插件")
        export_action = menu.addAction("查看详情")
        uninstall_action = menu.addAction("卸载插件")
        
        # 内置插件不能卸载
        if plugin.is_builtin:
            uninstall_action.setEnabled(False)
        
        action = menu.exec_(self.table.mapToGlobal(pos))
        
        if action == toggle_action:
            self._toggle_plugin(plugin)
        elif action == config_action:
            self._config_plugin(plugin)
        elif action == export_action:
            self._view_plugin_detail(plugin)
        elif action == uninstall_action:
            self._uninstall_plugin(plugin)
        elif 'use_action' in locals() and action == use_action:
            self._use_plugin(plugin)
    
    def _on_install_plugin(self):
        """安装插件"""
        from PyQt5.QtWidgets import QFileDialog
        path = QFileDialog.getExistingDirectory(self, "选择插件目录")
        if not path:
            return
        
        progress = QProgressDialog("正在安装插件...", "取消", 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        
        try:
            plugin, error = PluginService.install_plugin(path)
            progress.close()
            
            if error:
                QMessageBox.critical(self, "错误", f"安装失败: {error}")
                return
            
            self._load_plugins()
            QMessageBox.information(self, "成功", f"插件 {plugin.name} 安装成功")
            logger.info(f"插件安装成功: {plugin.plugin_id}")
            
        except Exception as e:
            progress.close()
            QMessageBox.critical(self, "错误", f"安装失败: {str(e)}")
    
    def _toggle_plugin(self, plugin):
        """启用/禁用插件"""
        if plugin.status == PluginStatus.ENABLED:
            # 禁用
            reply = QMessageBox.question(
                self,
                "确认禁用",
                f"确定要禁用插件 {plugin.name} 吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success, error = PluginService.disable_plugin(plugin.plugin_id)
                if error:
                    QMessageBox.critical(self, "错误", f"禁用失败: {error}")
                    return
                
                self._load_plugins()
                logger.info(f"插件已禁用: {plugin.plugin_id}")
        
        elif plugin.status == PluginStatus.DISABLED:
            # 启用
            progress = QProgressDialog("正在启用插件...", "取消", 0, 0, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            
            try:
                success, error = PluginService.enable_plugin(plugin.plugin_id)
                progress.close()
                
                if error:
                    QMessageBox.critical(self, "错误", f"启用失败: {error}")
                    return
                
                self._load_plugins()
                QMessageBox.information(self, "成功", f"插件 {plugin.name} 已启用")
                logger.info(f"插件已启用: {plugin.plugin_id}")
                
            except Exception as e:
                progress.close()
                QMessageBox.critical(self, "错误", f"启用失败: {str(e)}")
    
    def _config_plugin(self, plugin):
        """配置插件"""
        from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                     QLineEdit, QTextEdit, QFormLayout, QPushButton,
                                     QComboBox, QSpinBox, QCheckBox, QTabWidget,
                                     QWidget)
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"配置插件 - {plugin.name}")
        dialog.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        tab_basic = QWidget()
        form = QFormLayout(tab_basic)
        
        self.cfg_name = QLineEdit(plugin.name or "")
        self.cfg_version = QLineEdit(plugin.version or "")
        self.cfg_author = QLineEdit(plugin.author or "")
        self.cfg_description = QTextEdit()
        self.cfg_description.setPlainText(plugin.description or "")
        self.cfg_status = QComboBox()
        self.cfg_status.addItems([s.value for s in PluginStatus])
        if plugin.status:
            self.cfg_status.setCurrentText(plugin.status.value)
        
        form.addRow("名称:", self.cfg_name)
        form.addRow("版本:", self.cfg_version)
        form.addRow("作者:", self.cfg_author)
        form.addRow("状态:", self.cfg_status)
        form.addRow("描述:", self.cfg_description)
        
        tabs.addTab(tab_basic, "基本信息")
        
        tab_params = QWidget()
        params_layout = QVBoxLayout(tab_params)
        self.cfg_params_text = QTextEdit()
        try:
            config_data = json.loads(plugin.config) if plugin.config else {}
            self.cfg_params_text.setPlainText(json.dumps(config_data, indent=2, ensure_ascii=False))
        except Exception as e:
            self.cfg_params_text.setPlainText(str(plugin.config or "{}"))
        self.cfg_params_text.setPlaceholderText('JSON格式配置参数，例如:\n{"timeout": 30, "retry": 3}')
        params_layout.addWidget(QLabel("配置参数 (JSON):"))
        params_layout.addWidget(self.cfg_params_text)
        tabs.addTab(tab_params, "配置参数")
        
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("保存")
        cancel_btn = QPushButton("取消")
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        if dialog.exec_() == QDialog.Accepted:
            try:
                from src.dao.plugin_dao import PluginDAO
                
                update_data = {
                    "name": self.cfg_name.text().strip(),
                    "version": self.cfg_version.text().strip(),
                    "author": self.cfg_author.text().strip(),
                    "description": self.cfg_description.toPlainText().strip(),
                    "status": self.cfg_status.currentText(),
                    "config": self.cfg_params_text.toPlainText().strip()
                }
                
                updated_plugin = PluginDAO.update(plugin.plugin_id, update_data)
                if not updated_plugin:
                    QMessageBox.critical(self, "错误", "保存失败：插件不存在或更新出错")
                    return
                
                self._load_plugins()
                QMessageBox.information(self, "成功", "插件配置已保存")
                logger.info(f"插件配置已保存: {plugin.plugin_id}")
                
            except Exception as e:
                logger.exception(f"配置插件时发生异常: {e}")
                QMessageBox.critical(self, "错误", f"配置插件时出错:\n{str(e)}")
    
    def _view_plugin_detail(self, plugin):
        """查看插件详情"""
        from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                     QTextEdit, QFormLayout, QPushButton,
                                     QTabWidget, QWidget)
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"插件详情 - {plugin.name}")
        dialog.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(dialog)
        
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        tab_basic = QWidget()
        form = QFormLayout(tab_basic)
        
        form.addRow("ID:", QLabel(plugin.plugin_id or "-"))
        form.addRow("名称:", QLabel(plugin.name or "-"))
        form.addRow("版本:", QLabel(plugin.version or "-"))
        form.addRow("作者:", QLabel(plugin.author or "-"))
        form.addRow("状态:", QLabel(plugin.status.value if plugin.status and hasattr(plugin.status, 'value') else "-"))
        form.addRow("描述:", QLabel(plugin.description or "-"))
        form.addRow("安装路径:", QLabel(plugin.install_path or "-"))
        form.addRow("创建时间:", QLabel(str(plugin.created_at) if plugin.created_at else "-"))
        form.addRow("更新时间:", QLabel(str(plugin.updated_at) if plugin.updated_at else "-"))
        
        tabs.addTab(tab_basic, "基本信息")
        
        tab_config = QWidget()
        config_layout = QVBoxLayout(tab_config)
        config_text = QTextEdit()
        config_text.setReadOnly(True)
        try:
            config_data = json.loads(plugin.config) if plugin.config else {}
            config_text.setPlainText(json.dumps(config_data, indent=2, ensure_ascii=False))
        except Exception:
            config_text.setPlainText(str(plugin.config or "{}"))
        config_layout.addWidget(QLabel("当前配置:"))
        config_layout.addWidget(config_text)
        tabs.addTab(tab_config, "配置信息")
        
        tab_deps = QWidget()
        deps_layout = QVBoxLayout(tab_deps)
        deps_text = QTextEdit()
        deps_text.setReadOnly(True)
        deps_data = plugin.dependencies or []
        deps_text.setPlainText("\n".join(deps_data) if deps_data else "无依赖")
        deps_layout.addWidget(QLabel("依赖列表:"))
        deps_layout.addWidget(deps_text)
        tabs.addTab(tab_deps, "依赖信息")
        
        btn = QPushButton("关闭")
        btn.clicked.connect(dialog.accept)
        layout.addWidget(btn)
        
        dialog.exec_()
    
    def _uninstall_plugin(self, plugin):
        """卸载插件"""
        reply = QMessageBox.warning(
            self,
            "确认卸载",
            f"确定要卸载插件 {plugin.name} 吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, error = PluginService.uninstall_plugin(plugin.plugin_id)
            if error:
                QMessageBox.critical(self, "错误", f"卸载失败: {error}")
                return
            
            self._load_plugins()
            QMessageBox.information(self, "成功", "插件已卸载")
            logger.info(f"插件已卸载: {plugin.plugin_id}")
    
    def _use_plugin(self, plugin):
        """使用插件"""
        try:
            plugin_instance = PluginService.get_plugin(plugin.plugin_id)
            if not plugin_instance or "instance" not in plugin_instance:
                QMessageBox.warning(self, "错误", "插件实例未找到")
                return
            
            instance = plugin_instance["instance"]
            if not hasattr(instance, "get_widget"):
                QMessageBox.warning(self, "错误", "插件不提供用户界面")
                return
            
            # 获取插件的UI组件
            widget = instance.get_widget(self)
            if not widget:
                QMessageBox.warning(self, "错误", "插件UI组件加载失败")
                return
            
            # 创建对话框显示插件界面
            from PyQt5.QtWidgets import QDialog, QVBoxLayout
            dialog = QDialog(self)
            dialog.setWindowTitle(f"{plugin.name}")
            dialog.setMinimumSize(800, 600)
            
            layout = QVBoxLayout(dialog)
            layout.addWidget(widget)
            
            dialog.exec_()
            
            logger.info(f"使用插件: {plugin.plugin_id}")
            
        except Exception as e:
            logger.error(f"使用插件失败: {plugin.plugin_id}, 错误: {e}")
            QMessageBox.critical(self, "错误", f"使用插件失败: {str(e)}")
