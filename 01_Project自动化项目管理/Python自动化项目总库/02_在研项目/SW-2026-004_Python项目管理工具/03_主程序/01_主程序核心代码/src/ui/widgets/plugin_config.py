# -*- coding: utf-8 -*-
"""
插件配置中心控件
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QListWidget, QListWidgetItem, QGroupBox, QFormLayout,
    QLineEdit, QTextEdit, QComboBox, QPushButton, QLabel,
    QMessageBox, QCheckBox, QSpinBox, QTabWidget
)
from PyQt5.QtCore import Qt, pyqtSignal

from src.services.plugin_service import PluginService
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class PluginConfigWidget(QWidget):
    """插件配置中心控件"""
    
    config_changed = pyqtSignal(str, dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_plugin = None
        self._init_ui()
        self._load_plugins()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        splitter = QSplitter(Qt.Horizontal)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        left_layout.addWidget(QLabel("已安装插件"))
        
        self.plugin_list = QListWidget()
        self.plugin_list.currentItemChanged.connect(self._on_plugin_selected)
        left_layout.addWidget(self.plugin_list)
        
        btn_layout = QHBoxLayout()
        
        self.install_btn = QPushButton("安装插件")
        self.install_btn.clicked.connect(self._on_install_plugin)
        btn_layout.addWidget(self.install_btn)
        
        self.uninstall_btn = QPushButton("卸载插件")
        self.uninstall_btn.clicked.connect(self._on_uninstall_plugin)
        btn_layout.addWidget(self.uninstall_btn)
        
        left_layout.addLayout(btn_layout)
        
        splitter.addWidget(left_widget)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        self.info_group = QGroupBox("插件信息")
        info_layout = QFormLayout(self.info_group)
        
        self.name_label = QLabel("-")
        info_layout.addRow("名称:", self.name_label)
        
        self.version_label = QLabel("-")
        info_layout.addRow("版本:", self.version_label)
        
        self.author_label = QLabel("-")
        info_layout.addRow("作者:", self.author_label)
        
        self.status_label = QLabel("-")
        info_layout.addRow("状态:", self.status_label)
        
        self.desc_text = QTextEdit()
        self.desc_text.setReadOnly(True)
        self.desc_text.setMaximumHeight(80)
        info_layout.addRow("描述:", self.desc_text)
        
        right_layout.addWidget(self.info_group)
        
        self.config_group = QGroupBox("插件配置")
        config_layout = QVBoxLayout(self.config_group)
        
        self.config_tabs = QTabWidget()
        config_layout.addWidget(self.config_tabs)
        
        self.general_tab = QWidget()
        general_layout = QFormLayout(self.general_tab)
        
        self.enabled_check = QCheckBox("启用插件")
        self.enabled_check.stateChanged.connect(self._on_enabled_changed)
        general_layout.addRow(self.enabled_check)
        
        self.auto_run_check = QCheckBox("自动运行")
        general_layout.addRow(self.auto_run_check)
        
        self.priority_spin = QSpinBox()
        self.priority_spin.setRange(1, 100)
        self.priority_spin.setValue(50)
        general_layout.addRow("优先级:", self.priority_spin)
        
        self.config_tabs.addTab(self.general_tab, "常规")
        
        self.params_tab = QWidget()
        self.params_layout = QVBoxLayout(self.params_tab)
        self.params_layout.addWidget(QLabel("此插件无自定义配置参数"))
        self.config_tabs.addTab(self.params_tab, "参数")
        
        right_layout.addWidget(self.config_group)
        
        btn_layout2 = QHBoxLayout()
        
        self.save_btn = QPushButton("保存配置")
        self.save_btn.clicked.connect(self._on_save_config)
        btn_layout2.addWidget(self.save_btn)
        
        self.reset_btn = QPushButton("重置")
        self.reset_btn.clicked.connect(self._on_reset_config)
        btn_layout2.addWidget(self.reset_btn)
        
        btn_layout2.addStretch()
        
        right_layout.addLayout(btn_layout2)
        
        splitter.addWidget(right_widget)
        
        splitter.setSizes([200, 500])
        
        layout.addWidget(splitter)
    
    def _load_plugins(self):
        """加载插件列表"""
        self.plugin_list.clear()
        
        plugins = PluginService.list_plugins()
        for plugin in plugins:
            item = QListWidgetItem(f"{plugin.name} (v{plugin.version})")
            item.setData(Qt.UserRole, plugin.plugin_id)

            status_value = getattr(plugin.status, 'value', None) if plugin.status else None
            if status_value == "enabled":
                item.setForeground(Qt.darkGreen)
            else:
                item.setForeground(Qt.gray)
            
            self.plugin_list.addItem(item)
        
        if self.plugin_list.count() > 0:
            self.plugin_list.setCurrentRow(0)
    
    def _on_plugin_selected(self, current: QListWidgetItem, previous: QListWidgetItem):
        """选择插件"""
        if not current:
            self.current_plugin = None
            return
        
        plugin_id = current.data(Qt.UserRole)
        plugin_dict = PluginService.get_plugin(plugin_id)
        
        # 如果返回的是字典，提取model对象
        if plugin_dict and isinstance(plugin_dict, dict) and "model" in plugin_dict:
            self.current_plugin = plugin_dict["model"]
        else:
            self.current_plugin = plugin_dict
        
        if self.current_plugin:
            self._display_plugin_info()
            self._load_plugin_config()
    
    def _display_plugin_info(self):
        """显示插件信息"""
        if not self.current_plugin:
            return
        
        self.name_label.setText(self.current_plugin.name)
        self.version_label.setText(self.current_plugin.version)
        self.author_label.setText(self.current_plugin.author or "-")

        status_value = getattr(self.current_plugin.status, 'value', None) if self.current_plugin.status else None
        status_text = "已启用" if status_value == "enabled" else "已禁用"
        self.status_label.setText(status_text)
        self.desc_text.setText(self.current_plugin.description or "暂无描述")
    
    def _load_plugin_config(self):
        """加载插件配置"""
        if not self.current_plugin:
            return
        
        config = self.current_plugin.config or {}
        
        self.enabled_check.setChecked(self.current_plugin.status.value == "enabled")
        self.auto_run_check.setChecked(config.get("auto_run", False))
        self.priority_spin.setValue(config.get("priority", 50))
        
        self._load_custom_params(config.get("params", {}))
    
    def _load_custom_params(self, params: dict):
        """加载自定义参数"""
        for i in reversed(range(self.params_layout.count())):
            self.params_layout.itemAt(i).widget().setParent(None)
        
        if not params:
            self.params_layout.addWidget(QLabel("此插件无自定义配置参数"))
            return
        
        for key, value in params.items():
            label = QLabel(f"{key}:")
            value_label = QLabel(str(value))
            self.params_layout.addRow(label, value_label)
    
    def _on_enabled_changed(self, state: int):
        """启用状态变更"""
        if not self.current_plugin:
            return
        
        if state == Qt.Checked:
            PluginService.enable_plugin(self.current_plugin.plugin_id)
        else:
            PluginService.disable_plugin(self.current_plugin.plugin_id)
    
    def _on_save_config(self):
        """保存配置"""
        if not self.current_plugin:
            return
        
        config = {
            "auto_run": self.auto_run_check.isChecked(),
            "priority": self.priority_spin.value()
        }
        
        self.config_changed.emit(self.current_plugin.plugin_id, config)
        QMessageBox.information(self, "成功", "配置已保存")
    
    def _on_reset_config(self):
        """重置配置"""
        if not self.current_plugin:
            return
        
        self.auto_run_check.setChecked(False)
        self.priority_spin.setValue(50)
    
    def _on_install_plugin(self):
        """安装插件"""
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择插件包",
            "",
            "Python Package (*.zip *.whl);;All Files (*)"
        )
        
        if file_path:
            plugin, error = PluginService.install_plugin(file_path)
            if plugin:
                QMessageBox.information(self, "成功", f"插件 {plugin.name} 安装成功")
                self._load_plugins()
            else:
                QMessageBox.warning(self, "失败", f"安装失败: {error}")
    
    def _on_uninstall_plugin(self):
        """卸载插件"""
        if not self.current_plugin:
            QMessageBox.warning(self, "提示", "请先选择要卸载的插件")
            return
        
        reply = QMessageBox.question(
            self,
            "确认卸载",
            f"确定要卸载插件 {self.current_plugin.name} 吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, error = PluginService.uninstall_plugin(self.current_plugin.plugin_id)
            if success:
                QMessageBox.information(self, "成功", "插件已卸载")
                self._load_plugins()
            else:
                QMessageBox.warning(self, "失败", f"卸载失败: {error}")
