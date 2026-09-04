# -*- coding: utf-8 -*-
"""
报告中心控件
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QListWidget, QListWidgetItem, QGroupBox, QFormLayout,
    QLabel, QPushButton, QTextEdit, QComboBox, QDateEdit,
    QMessageBox, QFileDialog, QProgressBar
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal

from src.services.project_service import ProjectService
from src.services.statistics_service import StatisticsService
from src.services.export_service import ExportService
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ReportCenterWidget(QWidget):
    """报告中心控件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._load_projects()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        toolbar = QHBoxLayout()
        
        toolbar.addWidget(QLabel("报告类型:"))
        
        self.report_type = QComboBox()
        self.report_type.addItems([
            "项目报告",
            "统计报告",
            "进度报告",
            "变更报告"
        ])
        self.report_type.currentIndexChanged.connect(self._on_report_type_changed)
        toolbar.addWidget(self.report_type)
        
        toolbar.addWidget(QLabel("项目:"))
        
        self.project_combo = QComboBox()
        self.project_combo.setMinimumWidth(200)
        toolbar.addWidget(self.project_combo)
        
        toolbar.addWidget(QLabel("格式:"))
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Markdown", "HTML", "纯文本"])
        toolbar.addWidget(self.format_combo)
        
        toolbar.addStretch()
        
        self.generate_btn = QPushButton("生成报告")
        self.generate_btn.clicked.connect(self._on_generate_report)
        toolbar.addWidget(self.generate_btn)
        
        self.export_btn = QPushButton("导出报告")
        self.export_btn.clicked.connect(self._on_export_report)
        toolbar.addWidget(self.export_btn)
        
        layout.addLayout(toolbar)
        
        splitter = QSplitter(Qt.Horizontal)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        left_layout.addWidget(QLabel("报告预览"))
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setAcceptRichText(True)
        left_layout.addWidget(self.preview_text)
        
        splitter.addWidget(left_widget)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        stats_group = QGroupBox("统计概览")
        stats_layout = QFormLayout(stats_group)
        
        self.total_projects_label = QLabel("0")
        stats_layout.addRow("项目总数:", self.total_projects_label)
        
        self.active_projects_label = QLabel("0")
        stats_layout.addRow("进行中:", self.active_projects_label)
        
        self.total_changes_label = QLabel("0")
        stats_layout.addRow("变更单数:", self.total_changes_label)
        
        self.plugin_count_label = QLabel("0")
        stats_layout.addRow("插件数:", self.plugin_count_label)
        
        right_layout.addWidget(stats_group)
        
        quick_group = QGroupBox("快捷操作")
        quick_layout = QVBoxLayout(quick_group)
        
        self.quick_stats_btn = QPushButton("查看系统统计")
        self.quick_stats_btn.clicked.connect(self._on_quick_stats)
        quick_layout.addWidget(self.quick_stats_btn)
        
        self.quick_export_btn = QPushButton("导出所有统计")
        self.quick_export_btn.clicked.connect(self._on_quick_export)
        quick_layout.addWidget(self.quick_export_btn)
        
        right_layout.addWidget(quick_group)
        
        right_layout.addStretch()
        
        splitter.addWidget(right_widget)
        
        splitter.setSizes([600, 200])
        
        layout.addWidget(splitter)
        
        self._update_overview()
    
    def _load_projects(self):
        """加载项目列表"""
        self.project_combo.clear()
        self.project_combo.addItem("全部项目", None)
        
        projects, _ = ProjectService.list_projects(size=100)
        for project in projects:
            self.project_combo.addItem(f"{project.code} - {project.name}", project.project_id)
    
    def _update_overview(self):
        """更新概览统计"""
        overview = StatisticsService.get_overview()
        
        self.total_projects_label.setText(str(overview['projects']['total']))
        self.active_projects_label.setText(str(overview['projects']['active']))
        
        change_stats = StatisticsService.get_change_statistics()
        self.total_changes_label.setText(str(change_stats['total']))
        
        self.plugin_count_label.setText(str(overview['plugins']['total']))
    
    def _on_report_type_changed(self, index: int):
        """报告类型变更"""
        if index == 0:
            self.project_combo.setEnabled(True)
        elif index == 1:
            self.project_combo.setEnabled(False)
        else:
            self.project_combo.setEnabled(True)
    
    def _on_generate_report(self):
        """生成报告"""
        report_type = self.report_type.currentText()
        project_id = self.project_combo.currentData()
        format_type = self.format_combo.currentText().lower()
        
        if format_type == "markdown":
            format_key = "markdown"
        elif format_type == "html":
            format_key = "html"
        else:
            format_key = "text"
        
        try:
            if report_type == "项目报告":
                if not project_id:
                    QMessageBox.warning(self, "提示", "请选择项目")
                    return
                
                content = StatisticsService.get_project_statistics(project_id)
                content = ExportService._generate_project_md(
                    ProjectService.get_project(project_id),
                    content
                )
            
            elif report_type == "统计报告":
                content = StatisticsService.export_statistics_report(format_key)
            
            elif report_type == "进度报告":
                if not project_id:
                    QMessageBox.warning(self, "提示", "请选择项目")
                    return
                
                output_path, error = ExportService.export_progress_report(
                    project_id, format_key
                )
                if output_path:
                    with open(output_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                else:
                    content = f"生成进度报告失败: {error}"
            
            elif report_type == "变更报告":
                if not project_id:
                    QMessageBox.warning(self, "提示", "请选择项目")
                    return
                
                output_path, error = ExportService.export_change_report(
                    project_id, format_key
                )
                if output_path:
                    with open(output_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                else:
                    content = f"生成变更报告失败: {error}"
            
            else:
                content = "暂不支持该报告类型"
            
            self.preview_text.setText(content)
            QMessageBox.information(self, "成功", "报告生成成功")
            
        except Exception as e:
            logger.exception(f"生成报告失败: {e}")
            QMessageBox.warning(self, "失败", f"生成报告失败: {str(e)}")
    
    def _on_export_report(self):
        """导出报告"""
        report_type = self.report_type.currentText()
        project_id = self.project_combo.currentData()
        format_type = self.format_combo.currentText().lower()
        
        if format_type == "markdown":
            format_key = "markdown"
            ext = ".md"
        elif format_type == "html":
            format_key = "html"
            ext = ".html"
        else:
            format_key = "text"
            ext = ".txt"
        
        default_name = f"{report_type}_{QDate.currentDate().toString('yyyyMMdd')}{ext}"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存报告",
            default_name,
            f"报告文件 (*{ext});;所有文件 (*)"
        )
        
        if not file_path:
            return
        
        try:
            if report_type == "项目报告":
                if not project_id:
                    QMessageBox.warning(self, "提示", "请选择项目")
                    return
                
                output_path, error = ExportService.export_project_report(
                    project_id, format_key, file_path
                )
            
            elif report_type == "统计报告":
                output_path, error = ExportService.export_statistics_report(
                    format_key, file_path
                )
            
            elif report_type == "进度报告":
                if not project_id:
                    QMessageBox.warning(self, "提示", "请选择项目")
                    return
                
                output_path, error = ExportService.export_progress_report(
                    project_id, format_key, file_path
                )
            
            elif report_type == "变更报告":
                if not project_id:
                    QMessageBox.warning(self, "提示", "请选择项目")
                    return
                
                output_path, error = ExportService.export_change_report(
                    project_id, format_key, file_path
                )
            
            else:
                output_path, error = None, "暂不支持该报告类型"
            
            if output_path:
                QMessageBox.information(self, "成功", f"报告已导出至: {output_path}")
            else:
                QMessageBox.warning(self, "失败", error)
                
        except Exception as e:
            logger.exception(f"导出报告失败: {e}")
            QMessageBox.warning(self, "失败", f"导出失败: {str(e)}")
    
    def _on_quick_stats(self):
        """查看系统统计"""
        content = StatisticsService.export_statistics_report("markdown")
        self.preview_text.setText(content)
        self.report_type.setCurrentIndex(1)
    
    def _on_quick_export(self):
        """导出所有统计"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存统计报告",
            f"统计报告_{QDate.currentDate().toString('yyyyMMdd')}.md",
            "Markdown文件 (*.md);;HTML文件 (*.html);;所有文件 (*)"
        )
        
        if not file_path:
            return
        
        format_key = "html" if file_path.endswith('.html') else "markdown"
        
        output_path, error = ExportService.export_statistics_report(format_key, file_path)
        
        if output_path:
            QMessageBox.information(self, "成功", f"报告已导出至: {output_path}")
        else:
            QMessageBox.warning(self, "失败", error)
