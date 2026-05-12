# -*- coding: utf-8 -*-
"""
插件市场控件
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QLabel, QScrollArea, QFrame, QGridLayout,
    QMessageBox, QProgressDialog, QTabWidget, QSpacerItem,
    QSizePolicy, QDialog, QTextEdit, QDialogButtonBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QPixmap

from src.services.plugin_market_service import PluginMarketService, RemotePlugin
from src.services.plugin_service import PluginService
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class PluginCardWidget(QFrame):
    """插件卡片控件"""
    
    install_clicked = pyqtSignal(str)
    update_clicked = pyqtSignal(str)
    uninstall_clicked = pyqtSignal(str)
    detail_clicked = pyqtSignal(str)
    
    def __init__(self, plugin: RemotePlugin, parent=None):
        super().__init__(parent)
        self.plugin = plugin
        self._init_ui()
        self._set_style()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        header_layout = QHBoxLayout()
        
        name_label = QLabel(self.plugin.name)
        name_label.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        header_layout.addWidget(name_label)
        
        header_layout.addStretch()
        
        if self.plugin.installed:
            if self.plugin.has_update:
                update_btn = QPushButton("更新")
                update_btn.setProperty("class", "update-btn")
                update_btn.clicked.connect(lambda: self.update_clicked.emit(self.plugin.plugin_id))
                header_layout.addWidget(update_btn)
            else:
                installed_label = QLabel("已安装")
                installed_label.setStyleSheet("color: #52c41a;")
                header_layout.addWidget(installed_label)
        else:
            install_btn = QPushButton("安装")
            install_btn.setProperty("class", "install-btn")
            install_btn.clicked.connect(lambda: self.install_clicked.emit(self.plugin.plugin_id))
            header_layout.addWidget(install_btn)
        
        layout.addLayout(header_layout)
        
        author_label = QLabel(f"作者: {self.plugin.author}")
        author_label.setStyleSheet("color: #666;")
        layout.addWidget(author_label)
        
        desc_label = QLabel(self.plugin.description)
        desc_label.setWordWrap(True)
        desc_label.setMaximumHeight(60)
        layout.addWidget(desc_label)
        
        info_layout = QHBoxLayout()
        
        version_label = QLabel(f"v{self.plugin.version}")
        version_label.setStyleSheet("color: #1890ff;")
        info_layout.addWidget(version_label)
        
        info_layout.addStretch()
        
        rating_label = QLabel(f"⭐ {self.plugin.rating:.1f}")
        info_layout.addWidget(rating_label)
        
        download_label = QLabel(f"📥 {self._format_count(self.plugin.download_count)}")
        info_layout.addWidget(download_label)
        
        layout.addLayout(info_layout)
        
        if self.plugin.tags:
            tags_layout = QHBoxLayout()
            tags_layout.setSpacing(4)
            for tag in self.plugin.tags[:3]:
                tag_label = QLabel(tag)
                tag_label.setStyleSheet("""
                    QLabel {
                        background-color: #f0f0f0;
                        padding: 2px 6px;
                        border-radius: 3px;
                        font-size: 11px;
                    }
                """)
                tags_layout.addWidget(tag_label)
            tags_layout.addStretch()
            layout.addLayout(tags_layout)
        
        detail_btn = QPushButton("查看详情")
        detail_btn.setFlat(True)
        detail_btn.setStyleSheet("color: #1890ff; border: none;")
        detail_btn.clicked.connect(lambda: self.detail_clicked.emit(self.plugin.plugin_id))
        layout.addWidget(detail_btn)
    
    def _format_count(self, count: int) -> str:
        """格式化下载次数"""
        if count >= 10000:
            return f"{count/10000:.1f}万"
        elif count >= 1000:
            return f"{count/1000:.1f}k"
        return str(count)
    
    def _set_style(self):
        """设置样式"""
        self.setStyleSheet("""
            PluginCardWidget {
                background-color: white;
                border: 1px solid #e8e8e8;
                border-radius: 6px;
                padding: 12px;
            }
            PluginCardWidget:hover {
                border-color: #1890ff;
            }
            QPushButton[class="install-btn"] {
                background-color: #1890ff;
                color: white;
                border: none;
                padding: 4px 12px;
                border-radius: 4px;
            }
            QPushButton[class="install-btn"]:hover {
                background-color: #40a9ff;
            }
            QPushButton[class="update-btn"] {
                background-color: #52c41a;
                color: white;
                border: none;
                padding: 4px 12px;
                border-radius: 4px;
            }
            QPushButton[class="update-btn"]:hover {
                background-color: #73d13d;
            }
        """)


class PluginDetailDialog(QDialog):
    """插件详情对话框"""
    
    def __init__(self, plugin: RemotePlugin, parent=None):
        super().__init__(parent)
        self.plugin = plugin
        self.setWindowTitle(f"插件详情 - {plugin.name}")
        self.setMinimumSize(500, 400)
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        header_layout = QHBoxLayout()
        
        name_label = QLabel(self.plugin.name)
        name_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        header_layout.addWidget(name_label)
        
        version_label = QLabel(f"v{self.plugin.version}")
        version_label.setStyleSheet("color: #1890ff; font-size: 12px;")
        header_layout.addWidget(version_label)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        info_grid = QGridLayout()
        info_grid.setColumnStretch(1, 1)
        
        info_grid.addWidget(QLabel("作者:"), 0, 0)
        info_grid.addWidget(QLabel(self.plugin.author), 0, 1)
        
        info_grid.addWidget(QLabel("评分:"), 1, 0)
        info_grid.addWidget(QLabel(f"⭐ {self.plugin.rating:.1f}"), 1, 1)
        
        info_grid.addWidget(QLabel("下载:"), 2, 0)
        info_grid.addWidget(QLabel(str(self.plugin.download_count)), 2, 1)
        
        if self.plugin.repository:
            info_grid.addWidget(QLabel("仓库:"), 3, 0)
            repo_label = QLabel(f'<a href="{self.plugin.repository}">{self.plugin.repository}</a>')
            repo_label.setOpenExternalLinks(True)
            info_grid.addWidget(repo_label, 3, 1)
        
        if self.plugin.homepage:
            info_grid.addWidget(QLabel("主页:"), 4, 0)
            home_label = QLabel(f'<a href="{self.plugin.homepage}">{self.plugin.homepage}</a>')
            home_label.setOpenExternalLinks(True)
            info_grid.addWidget(home_label, 4, 1)
        
        layout.addLayout(info_grid)
        
        layout.addWidget(QLabel("描述:"))
        desc_text = QTextEdit()
        desc_text.setPlainText(self.plugin.description)
        desc_text.setReadOnly(True)
        desc_text.setMaximumHeight(80)
        layout.addWidget(desc_text)
        
        if self.plugin.changelog:
            layout.addWidget(QLabel("更新日志:"))
            changelog_text = QTextEdit()
            changelog_text.setPlainText(self.plugin.changelog)
            changelog_text.setReadOnly(True)
            changelog_text.setMaximumHeight(120)
            layout.addWidget(changelog_text)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.close)
        layout.addWidget(button_box)


class FetchPluginsThread(QThread):
    """获取插件列表线程"""
    
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, market_service: PluginMarketService, force: bool = False):
        super().__init__()
        self.market_service = market_service
        self.force = force
    
    def run(self):
        try:
            plugins = self.market_service.fetch_remote_plugins(self.force)
            self.finished.emit(plugins)
        except Exception as e:
            self.error.emit(str(e))


class PluginMarketWidget(QWidget):
    """插件市场控件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.market_service = PluginMarketService()
        self.plugins = []
        self._fetch_thread = None
        self._init_ui()
        self._load_plugins()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        header_layout = QHBoxLayout()
        
        title_label = QLabel("插件市场")
        title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self.update_check_btn = QPushButton("检查更新")
        self.update_check_btn.clicked.connect(self._check_updates)
        header_layout.addWidget(self.update_check_btn)
        
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self._refresh_plugins)
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索插件名称、描述、标签...")
        self.search_input.setMinimumHeight(36)
        self.search_input.textChanged.connect(self._search_plugins)
        search_layout.addWidget(self.search_input)
        
        layout.addLayout(search_layout)
        
        self.tab_widget = QTabWidget()
        
        self.all_tab = QWidget()
        self.all_scroll = QScrollArea()
        self.all_scroll.setWidgetResizable(True)
        self.all_scroll.setFrameShape(QFrame.NoFrame)
        self.all_content = QWidget()
        self.all_layout = QGridLayout(self.all_content)
        self.all_layout.setSpacing(12)
        self.all_scroll.setWidget(self.all_content)
        all_tab_layout = QVBoxLayout(self.all_tab)
        all_tab_layout.setContentsMargins(0, 0, 0, 0)
        all_tab_layout.addWidget(self.all_scroll)
        self.tab_widget.addTab(self.all_tab, "全部")
        
        self.installed_tab = QWidget()
        self.installed_scroll = QScrollArea()
        self.installed_scroll.setWidgetResizable(True)
        self.installed_scroll.setFrameShape(QFrame.NoFrame)
        self.installed_content = QWidget()
        self.installed_layout = QGridLayout(self.installed_content)
        self.installed_layout.setSpacing(12)
        self.installed_scroll.setWidget(self.installed_content)
        installed_tab_layout = QVBoxLayout(self.installed_tab)
        installed_tab_layout.setContentsMargins(0, 0, 0, 0)
        installed_tab_layout.addWidget(self.installed_scroll)
        self.tab_widget.addTab(self.installed_tab, "已安装")
        
        self.updates_tab = QWidget()
        self.updates_scroll = QScrollArea()
        self.updates_scroll.setWidgetResizable(True)
        self.updates_scroll.setFrameShape(QFrame.NoFrame)
        self.updates_content = QWidget()
        self.updates_layout = QGridLayout(self.updates_content)
        self.updates_layout.setSpacing(12)
        self.updates_scroll.setWidget(self.updates_content)
        updates_tab_layout = QVBoxLayout(self.updates_tab)
        updates_tab_layout.setContentsMargins(0, 0, 0, 0)
        updates_tab_layout.addWidget(self.updates_scroll)
        self.tab_widget.addTab(self.updates_tab, "可更新")
        
        layout.addWidget(self.tab_widget)
        
        self.loading_label = QLabel("正在加载插件列表...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.hide()
        layout.addWidget(self.loading_label)
    
    def _load_plugins(self):
        """加载插件列表"""
        self.loading_label.show()
        self.tab_widget.hide()
        
        self._fetch_thread = FetchPluginsThread(self.market_service)
        self._fetch_thread.finished.connect(self._on_plugins_loaded)
        self._fetch_thread.error.connect(self._on_load_error)
        self._fetch_thread.start()
    
    def _refresh_plugins(self):
        """刷新插件列表"""
        self.loading_label.show()
        self.tab_widget.hide()
        
        self._fetch_thread = FetchPluginsThread(self.market_service, force=True)
        self._fetch_thread.finished.connect(self._on_plugins_loaded)
        self._fetch_thread.error.connect(self._on_load_error)
        self._fetch_thread.start()
    
    def _on_plugins_loaded(self, plugins: list):
        """插件列表加载完成"""
        self.plugins = plugins
        self.loading_label.hide()
        self.tab_widget.show()
        self._display_plugins()
    
    def _on_load_error(self, error: str):
        """加载失败"""
        self.loading_label.setText(f"加载失败: {error}")
        logger.error(f"加载插件列表失败: {error}")
    
    def _display_plugins(self):
        """显示插件列表"""
        self._clear_layout(self.all_layout)
        self._clear_layout(self.installed_layout)
        self._clear_layout(self.updates_layout)
        
        col = 0
        row = 0
        max_cols = 3
        
        for plugin in self.plugins:
            card = PluginCardWidget(plugin)
            card.install_clicked.connect(self._install_plugin)
            card.update_clicked.connect(self._update_plugin)
            card.detail_clicked.connect(self._show_detail)
            
            self.all_layout.addWidget(card, row, col)
            
            if plugin.installed:
                self.installed_layout.addWidget(PluginCardWidget(plugin), row, col)
            
            if plugin.has_update:
                self.updates_layout.addWidget(PluginCardWidget(plugin), row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        self.all_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding), row + 1, 0)
        self.installed_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding), row + 1, 0)
        self.updates_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding), row + 1, 0)
    
    def _clear_layout(self, layout):
        """清空布局"""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def _search_plugins(self, keyword: str):
        """搜索插件"""
        if not keyword:
            self._display_plugins()
            return
        
        self._clear_layout(self.all_layout)
        
        results = self.market_service.search_plugins(keyword)
        
        col = 0
        row = 0
        max_cols = 3
        
        for plugin in results:
            card = PluginCardWidget(plugin)
            card.install_clicked.connect(self._install_plugin)
            card.update_clicked.connect(self._update_plugin)
            card.detail_clicked.connect(self._show_detail)
            self.all_layout.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def _install_plugin(self, plugin_id: str):
        """安装插件"""
        plugin = self.market_service.get_plugin_detail(plugin_id)
        if not plugin:
            return
        
        reply = QMessageBox.question(
            self,
            "确认安装",
            f"确定要安装插件 {plugin.name} 吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply != QMessageBox.Yes:
            return
        
        progress = QProgressDialog("正在下载插件...", "取消", 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        
        try:
            zip_path, error = self.market_service.download_plugin(plugin_id)
            if error:
                progress.close()
                QMessageBox.critical(self, "错误", f"下载失败: {error}")
                return
            
            progress.setLabelText("正在安装插件...")
            
            plugin_obj, error = self.market_service.install_from_zip(zip_path)
            progress.close()
            
            if error:
                QMessageBox.critical(self, "错误", f"安装失败: {error}")
                return
            
            QMessageBox.information(self, "成功", f"插件 {plugin_obj.name} 安装成功")
            self._refresh_plugins()
            
        except Exception as e:
            progress.close()
            QMessageBox.critical(self, "错误", f"安装失败: {str(e)}")
    
    def _update_plugin(self, plugin_id: str):
        """更新插件"""
        plugin = self.market_service.get_plugin_detail(plugin_id)
        if not plugin:
            return
        
        reply = QMessageBox.question(
            self,
            "确认更新",
            f"确定要将插件 {plugin.name} 更新到 v{plugin.version} 吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply != QMessageBox.Yes:
            return
        
        progress = QProgressDialog("正在更新插件...", "取消", 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        
        try:
            zip_path, error = self.market_service.download_plugin(plugin_id)
            if error:
                progress.close()
                QMessageBox.critical(self, "错误", f"下载失败: {error}")
                return
            
            success, error = PluginService.update_plugin(plugin_id, plugin.version)
            progress.close()
            
            if error:
                QMessageBox.critical(self, "错误", f"更新失败: {error}")
                return
            
            QMessageBox.information(self, "成功", f"插件已更新到 v{plugin.version}")
            self._refresh_plugins()
            
        except Exception as e:
            progress.close()
            QMessageBox.critical(self, "错误", f"更新失败: {str(e)}")
    
    def _show_detail(self, plugin_id: str):
        """显示插件详情"""
        plugin = self.market_service.get_plugin_detail(plugin_id)
        if plugin:
            dialog = PluginDetailDialog(plugin, self)
            dialog.exec_()
    
    def _check_updates(self):
        """检查更新"""
        updates = self.market_service.check_updates()
        
        if not updates:
            QMessageBox.information(self, "检查更新", "所有插件都是最新版本")
            return
        
        update_list = "\n".join([
            f"- {u['name']}: {u['current_version']} → {u['latest_version']}"
            for u in updates
        ])
        
        reply = QMessageBox.information(
            self,
            "发现更新",
            f"以下插件有可用更新:\n\n{update_list}\n\n是否前往更新?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.tab_widget.setCurrentIndex(2)
