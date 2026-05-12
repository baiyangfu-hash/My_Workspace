# -*- coding: utf-8 -*-
"""
主窗口
"""
import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QStatusBar, QMenuBar, QAction, QMessageBox, QToolBar
)
from PyQt5.QtGui import QIcon, QPalette, QColor, QFont
from PyQt5.QtCore import Qt, QSize

from src.core.config import Config
from src.utils.logger import setup_logger
from .widgets.project_list import ProjectListWidget
from .widgets.template_manager import TemplateManagerWidget
from .widgets.plugin_manager import PluginManagerWidget
from .widgets.spec_center import SpecCenterWidget
from .widgets.change_manager import ChangeManagerWidget
from .widgets.progress_manager import ProgressManagerWidget
from .widgets.report_center import ReportCenterWidget
from .widgets.plugin_config import PluginConfigWidget
from .widgets.library_manager import LibraryManagerWidget

logger = setup_logger(__name__)

class MainWindow(QMainWindow):
    """应用主窗口"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        app_name = Config.get('app_name', 'Python项目管理工具')
        version = Config.get('version', '1.0.6')
        self.setWindowTitle(f"{app_name} v{version}")
        self.setMinimumSize(1200, 800)
        
        # 设置窗口样式
        self._setup_styles()
        
        # 初始化UI
        self._init_ui()
        self._init_menu()
        self._init_status_bar()
        
        # 加载数据（增强错误处理：即使部分初始化失败也不影响窗口显示）
        init_errors = []

        # 1. 初始化模板
        try:
            from src.services.template_service import TemplateService
            TemplateService.initialize_builtin_templates()
        except Exception as e:
            logger.exception(f"初始化模板失败: {e}")
            init_errors.append(f"模板初始化失败: {str(e)}")

        # 2. 初始化插件
        try:
            from src.services.plugin_service import PluginService
            PluginService.initialize_builtin_plugins()
            PluginService.load_plugins()
        except Exception as e:
            logger.exception(f"初始化插件失败: {e}")
            init_errors.append(f"插件初始化失败: {str(e)}")

        # 3. 初始化规范
        try:
            from src.services.spec_service import SpecService
            SpecService.initialize_builtin_specs()
        except Exception as e:
            logger.exception(f"初始化规范失败: {e}")
            init_errors.append(f"规范初始化失败: {str(e)}")

        # 4. 初始化默认总库（关键步骤）
        try:
            from src.services.library_service import LibraryService
            default_lib, lib_msg = LibraryService.initialize_default_library()
            if default_lib:
                logger.info(f"默认总库就绪: {default_lib.name} ({default_lib.library_id})")
            else:
                logger.warning(f"默认总库初始化失败: {lib_msg}")
                init_errors.append(f"总库初始化失败: {lib_msg}")
        except Exception as e:
            logger.exception(f"初始化默认总库异常: {e}")
            init_errors.append(f"总库初始化异常: {str(e)}")

        # 如果有任何初始化失败，显示警告但继续运行
        if init_errors:
            error_summary = "\n".join([f"• {err}" for err in init_errors])
            QMessageBox.warning(
                self,
                "警告",
                f"部分数据加载失败:\n{error_summary}\n\n程序将继续运行，部分功能可能不可用"
            )
        
        logger.info("主窗口初始化完成")
    
    def _setup_styles(self):
        """设置窗口样式"""
        # 设置字体
        font = QFont("Microsoft YaHei", 10)
        self.setFont(font)
        
        # 设置调色板
        palette = QPalette()
        # 背景色
        palette.setColor(QPalette.Window, QColor(248, 250, 252))
        # 文本色
        palette.setColor(QPalette.WindowText, QColor(30, 41, 59))
        # 按钮色
        palette.setColor(QPalette.Button, QColor(255, 255, 255))
        # 按钮文本色
        palette.setColor(QPalette.ButtonText, QColor(30, 41, 59))
        # 高亮色
        palette.setColor(QPalette.Highlight, QColor(59, 130, 246))
        # 高亮文本色
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        self.setPalette(palette)
        
        # 设置样式表 - 简约风格
        self.setStyleSheet("""
            /* 主窗口 */
            QMainWindow {
                background-color: #f8fafc;
            }
            
            /* 标签页 */
            QTabWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                margin: 10px;
            }
            
            QTabBar {
                background-color: white;
                padding: 6px 10px 0 10px;
            }
            
            QTabBar::tab {
                background-color: #f8fafc;
                color: #64748b;
                padding: 10px 24px;
                margin-right: 4px;
                border-radius: 6px 6px 0 0;
                font-size: 10pt;
                min-width: 80px;
            }
            
            QTabBar::tab:hover {
                background-color: #e2e8f0;
                color: #334155;
            }
            
            QTabBar::tab:selected {
                background-color: white;
                color: #3b82f6;
                border-bottom: 2px solid #3b82f6;
            }
            
            /* 菜单栏 */
            QMenuBar {
                background-color: white;
                border-bottom: 1px solid #e2e8f0;
                padding: 2px 0;
            }
            
            QMenuBar::item {
                padding: 8px 16px;
                color: #475569;
            }
            
            QMenuBar::item:selected {
                background-color: #f1f5f9;
                color: #3b82f6;
            }
            
            QMenu {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 4px 0;
            }
            
            QMenu::item {
                padding: 8px 24px;
                color: #475569;
                font-size: 9pt;
            }
            
            QMenu::item:selected {
                background-color: #dbeafe;
                color: #1d4ed8;
            }
            
            /* 状态栏 */
            QStatusBar {
                background-color: white;
                border-top: 1px solid #e2e8f0;
                padding: 4px 16px;
                font-size: 9pt;
                color: #64748b;
            }
            
            /* 按钮 */
            QPushButton {
                background-color: #ffffff;
                color: #475569;
                border: 1px solid #e2e8f0;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 9pt;
            }
            
            QPushButton:hover {
                background-color: #f1f5f9;
                border-color: #cbd5e1;
            }
            
            QPushButton:pressed {
                background-color: #e2e8f0;
            }
            
            QPushButton:default {
                background-color: #3b82f6;
                color: white;
                border-color: #3b82f6;
            }
            
            QPushButton:default:hover {
                background-color: #2563eb;
                border-color: #2563eb;
            }
            
            /* 输入框 */
            QLineEdit {
                border: 1px solid #e2e8f0;
                border-radius: 4px;
                padding: 6px 10px;
                background-color: white;
            }
            
            QLineEdit:focus {
                border-color: #3b82f6;
                outline: none;
            }
            
            /* 下拉框 */
            QComboBox {
                border: 1px solid #e2e8f0;
                border-radius: 4px;
                padding: 6px 8px;
                background-color: white;
            }
            
            QComboBox:focus {
                border-color: #3b82f6;
                outline: none;
            }
            
            /* 表格 */
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                background-color: white;
            }
            
            QTableWidget::item {
                padding: 8px;
            }
            
            QTableWidget::item:selected {
                background-color: #dbeafe;
                color: #1d4ed8;
            }
            
            QHeaderView::section {
                background-color: #f8fafc;
                color: #64748b;
                padding: 8px;
                border: 1px solid #e2e8f0;
            }
        """)
    
    def _init_ui(self):
        """初始化UI结构"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setTabShape(QTabWidget.Rounded)
        self.tab_widget.setElideMode(Qt.ElideRight)
        
        # 项目管理标签
        self.project_list = ProjectListWidget()
        self.tab_widget.addTab(self.project_list, "项目管理")
        
        # 模板管理标签
        self.template_manager = TemplateManagerWidget()
        self.tab_widget.addTab(self.template_manager, "模板管理")
        
        # 插件管理标签
        self.plugin_manager = PluginManagerWidget()
        self.tab_widget.addTab(self.plugin_manager, "插件管理")
        
        self.spec_center = SpecCenterWidget()
        self.tab_widget.addTab(self.spec_center, "规范中心")
        
        self.change_manager = ChangeManagerWidget()
        self.tab_widget.addTab(self.change_manager, "变更管理")
        
        self.progress_manager = ProgressManagerWidget()
        self.tab_widget.addTab(self.progress_manager, "进度管理")
        
        self.report_center = ReportCenterWidget()
        self.tab_widget.addTab(self.report_center, "报告中心")
        
        self.plugin_config = PluginConfigWidget()
        self.tab_widget.addTab(self.plugin_config, "插件配置")
        
        # 总库管理标签
        self.library_manager = LibraryManagerWidget()
        self.tab_widget.addTab(self.library_manager, "总库管理")
        
        layout.addWidget(self.tab_widget)
    
    def _init_menu(self):
        """初始化菜单栏"""
        menu_bar = self.menuBar()
        
        # 文件菜单
        file_menu = menu_bar.addMenu("文件")
        
        new_project_action = QAction("新建项目", self)
        new_project_action.setShortcut("Ctrl+N")
        new_project_action.triggered.connect(self._on_new_project)
        file_menu.addAction(new_project_action)
        
        import_project_action = QAction("导入项目", self)
        import_project_action.triggered.connect(self._on_import_project)
        file_menu.addAction(import_project_action)
        
        file_menu.addSeparator()
        
        settings_action = QAction("设置", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self._on_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 工具菜单
        tools_menu = menu_bar.addMenu("工具")
        
        check_action = QAction("规范检查", self)
        check_action.setShortcut("F5")
        check_action.triggered.connect(self._on_run_check)
        tools_menu.addAction(check_action)
        
        generate_report_action = QAction("生成报告", self)
        generate_report_action.triggered.connect(self._on_generate_report)
        tools_menu.addAction(generate_report_action)
        
        # 帮助菜单
        help_menu = menu_bar.addMenu("帮助")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)
    
    def _init_status_bar(self):
        """初始化状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
    
    def _load_data(self):
        """加载初始数据"""
        from src.services.template_service import TemplateService
        TemplateService.initialize_builtin_templates()

        from src.services.plugin_service import PluginService
        PluginService.initialize_builtin_plugins()
        PluginService.load_plugins()

        from src.services.spec_service import SpecService
        SpecService.initialize_builtin_specs()

        from src.services.library_service import LibraryService
        default_lib, lib_msg = LibraryService.initialize_default_library()
        if default_lib:
            logger.info(f"默认总库就绪: {default_lib.name} ({default_lib.library_id})")
        else:
            logger.warning(f"默认总库初始化失败: {lib_msg}")
    
    def _on_new_project(self):
        """新建项目"""
        # 委托给项目列表页面处理
        self.project_list._on_new_project()
    
    def _on_import_project(self):
        """导入项目"""
        from .dialogs.import_project_dialog import ImportProjectDialog
        
        dialog = ImportProjectDialog(self)
        if dialog.exec_() == dialog.Accepted:
            # 导入成功后刷新项目列表
            self.project_list._load_projects()
            self.status_bar.showMessage("项目导入成功")
        else:
            self.status_bar.showMessage("导入项目取消")
    
    def _on_settings(self):
        """打开设置"""
        from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                     QLineEdit, QFormLayout, QPushButton,
                                     QComboBox, QSpinBox, QCheckBox, QTabWidget,
                                     QWidget)
        
        dialog = QDialog(self)
        dialog.setWindowTitle("系统设置")
        dialog.setMinimumSize(550, 450)
        
        layout = QVBoxLayout(dialog)
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        tab_general = QWidget()
        form = QFormLayout(tab_general)
        
        self.setting_default_path = QLineEdit(
            Config.get("default_project_path", "C:\\Projects") or ""
        )
        self.setting_auto_save = QCheckBox("自动保存")
        self.setting_auto_save.setChecked(Config.get("auto_save", True))
        self.setting_log_level = QComboBox()
        self.setting_log_level.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        current_level = Config.get("log_level", "INFO")
        idx = self.setting_log_level.findText(current_level)
        if idx >= 0:
            self.setting_log_level.setCurrentIndex(idx)
        
        form.addRow("默认项目路径:", self.setting_default_path)
        form.addRow("", self.setting_auto_save)
        form.addRow("日志级别:", self.setting_log_level)
        
        tabs.addTab(tab_general, "常规设置")
        
        tab_template = QWidget()
        tpl_layout = QVBoxLayout(tab_template)
        self.setting_tpl_overwrite = QCheckBox("覆盖已存在模板")
        self.setting_tpl_overwrite.setChecked(Config.get("template_overwrite", False))
        tpl_layout.addWidget(self.setting_tpl_overwrite)
        tabs.addTab(tab_template, "模板设置")
        
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
            Config.set("default_project_path", self.setting_default_path.text().strip())
            Config.set("auto_save", self.setting_auto_save.isChecked())
            Config.set("log_level", self.setting_log_level.currentText())
            Config.set("template_overwrite", self.setting_tpl_overwrite.isChecked())
            Config.save()
            QMessageBox.information(self, "成功", "设置已保存")
            logger.info("系统设置已更新")
    
    def _on_run_check(self):
        """运行规范检查"""
        from src.services.check_service import CheckService
        current = self.tab_widget.currentIndex()
        widget = self.tab_widget.widget(current)
        
        project = getattr(widget, 'current_project', None) or \
                  getattr(widget, '_current_project', None)
        
        if not project:
            items = self.project_list.get_selected_items()
            if items:
                project = items[0]
        
        if not project:
            QMessageBox.warning(self, "提示", "请先选择一个项目进行规范检查")
            return
        
        try:
            result, error = CheckService.check_project(project)
            if error:
                QMessageBox.critical(self, "检查失败", f"规范检查失败: {error}")
                return
            
            passed = sum(1 for r in result.get('results', []) if r.get('passed', False))
            total = len(result.get('results', []))
            
            msg = f"检查完成！\n通过: {passed}/{total} 项"
            if passed == total:
                QMessageBox.information(self, "检查结果", msg + "\n✓ 所有检查项均通过")
            else:
                details = "\n".join([
                    f"  {'✗' if not r.get('passed') else '✓'} {r.get('name', '')}: {r.get('message', '')}"
                    for r in result.get('results', [])
                    if not r.get('passed', False)
                ])
                QMessageBox.warning(self, "检查结果", msg + "\n\n未通过项:\n" + details)
                
            self.status_bar.showMessage(f"规范检查完成: {passed}/{total} 通过")
            logger.info(f"规范检查完成: {project.code}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"运行检查时出错: {str(e)}")
    
    def _on_generate_report(self):
        """生成报告"""
        from src.services.report_service import ReportService
        
        current = self.tab_widget.currentIndex()
        widget = self.tab_widget.widget(current)
        
        project = getattr(widget, 'current_project', None) or \
                  getattr(widget, '_current_project', None)
        
        if not project:
            items = self.project_list.get_selected_items()
            if items:
                project = items[0]
        
        if not project:
            QMessageBox.warning(self, "提示", "请先选择一个项目以生成报告")
            return
        
        report_types = [
            ("项目概览报告 (Markdown)", "overview_md"),
            ("项目详细报告 (Markdown)", "detail_md"),
            ("项目统计报告 (JSON)", "statistics_json"),
            ("进度报告 (Markdown)", "progress_md")
        ]
        
        from PyQt5.QtWidgets import QInputDialog, QFileDialog
        report_type, ok = QInputDialog.getItem(
            self,
            "选择报告类型",
            "请选择要生成的报告类型:",
            [r[0] for r in report_types],
            0,
            False
        )
        
        if not ok:
            return
        
        type_key = [r[1] for r in report_types if r[0] == report_type][0]
        
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存报告",
            f"{project.name}_{type_key}",
            "Markdown (*.md);;JSON (*.json);;All Files (*)"
        )
        
        if not save_path:
            return
        
        success, error = ReportService.generate_report(project, type_key, save_path)
        if error:
            QMessageBox.critical(self, "错误", f"生成报告失败: {error}")
            return
        
        QMessageBox.information(self, "成功", f"报告已生成并保存到:\n{save_path}")
        self.status_bar.showMessage(f"报告已生成: {report_type}")
        logger.info(f"报告已生成: {save_path}")
    
    def _on_about(self):
        """关于对话框"""
        QMessageBox.about(
            self,
            f"关于 {Config.get('app_name')}",
            f"""
            <h1>{Config.get('app_name')}</h1>
            <p>版本: {Config.get('version')}</p>
            <p>轻量级Python项目管理工具</p>
            <p>© 2026 Trae AI</p>
            """
        )
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        reply = QMessageBox.question(
            self,
            "确认退出",
            "确定要退出吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            logger.info("用户确认退出")
            event.accept()
        else:
            event.ignore()
