# -*- coding: utf-8 -*-
"""
导入项目对话框
"""
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QTextEdit, QPushButton,
    QFileDialog, QLabel, QMessageBox
)
from PyQt5.QtCore import Qt

from src.services.project_service import ProjectService
from src.services.template_service import TemplateService
from src.core.constants import BusinessLine, BUSINESS_LINE_DESC, BUSINESS_LINE_TEMPLATES
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ImportProjectDialog(QDialog):
    """导入项目对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("导入项目")
        self.setMinimumSize(500, 400)
        self.setWindowModality(Qt.WindowModal)
        
        self.templates = []
        self._init_ui()
        self._load_data()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # 业务线
        self.business_line_combo = QComboBox()
        for bl in BusinessLine:
            self.business_line_combo.addItem(BUSINESS_LINE_DESC[bl], bl.value)
        self.business_line_combo.currentIndexChanged.connect(self._on_business_line_changed)
        form_layout.addRow("业务线:", self.business_line_combo)
        
        # 项目编号
        self.code_input = QLineEdit()
        self.code_input.setReadOnly(True)
        form_layout.addRow("项目编号:", self.code_input)
        
        # 项目名称
        self.name_input = QLineEdit()
        self.name_input.textChanged.connect(self._generate_project_code)
        form_layout.addRow("项目名称:", self.name_input)
        
        # 项目模板
        self.template_combo = QComboBox()
        form_layout.addRow("项目模板:", self.template_combo)
        
        # 负责人
        self.manager_input = QLineEdit()
        form_layout.addRow("负责人:", self.manager_input)
        
        # 项目描述
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        form_layout.addRow("项目描述:", self.description_input)
        
        # 项目路径
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        path_layout.addWidget(self.path_input)
        
        browse_btn = QPushButton("浏览")
        browse_btn.clicked.connect(self._browse_path)
        path_layout.addWidget(browse_btn)
        form_layout.addRow("项目路径:", path_layout)
        
        layout.addLayout(form_layout)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        self.import_btn = QPushButton("导入")
        self.import_btn.clicked.connect(self._on_import)
        self.import_btn.setDefault(True)
        btn_layout.addWidget(self.import_btn)
        
        layout.addLayout(btn_layout)
    
    def _load_data(self):
        """加载模板数据"""
        self.templates = TemplateService.list_templates()
        self._update_template_combo()
        self._generate_project_code()
    
    def _on_business_line_changed(self):
        """业务线变更时更新模板列表"""
        self._generate_project_code()
        self._update_template_combo()
    
    def _update_template_combo(self):
        """根据业务线更新模板下拉框"""
        business_line = self.business_line_combo.currentData()
        self.template_combo.clear()
        
        recommended_ids = BUSINESS_LINE_TEMPLATES.get(business_line, [])
        
        recommended_templates = []
        other_templates = []
        
        for template in self.templates:
            if template.template_id in recommended_ids:
                recommended_templates.append(template)
            else:
                other_templates.append(template)
        
        for template in recommended_templates:
            self.template_combo.addItem(f"★ {template.name} ({template.version}) [推荐]", template.template_id)
        
        if recommended_templates and other_templates:
            self.template_combo.insertSeparator(len(recommended_templates))
        
        for template in other_templates:
            self.template_combo.addItem(f"{template.name} ({template.version})", template.template_id)
    
    def _generate_project_code(self):
        """生成项目编号"""
        business_line = self.business_line_combo.currentData()
        if business_line:
            code, _ = ProjectService.generate_project_code(business_line)
            self.code_input.setText(code)
    
    def _browse_path(self):
        """浏览项目路径"""
        path = QFileDialog.getExistingDirectory(self, "选择项目目录")
        if path:
            self.path_input.setText(path)
            # 自动填充项目名称
            project_name = os.path.basename(path)
            self.name_input.setText(project_name)
    
    def _on_import(self):
        """导入项目"""
        business_line = self.business_line_combo.currentData()
        name = self.name_input.text().strip()
        template_id = self.template_combo.currentData()
        path = self.path_input.text().strip()
        manager = self.manager_input.text().strip()
        description = self.description_input.toPlainText().strip()
        
        # 验证输入
        if not name:
            QMessageBox.warning(self, "警告", "项目名称不能为空")
            self.name_input.setFocus()
            return
        
        if not template_id:
            QMessageBox.warning(self, "警告", "请选择项目模板")
            self.template_combo.setFocus()
            return
        
        if not path:
            QMessageBox.warning(self, "警告", "项目路径不能为空")
            self.path_input.setFocus()
            return
        
        # 导入项目
        project, error = ProjectService.import_project(
            business_line=business_line,
            name=name,
            template_id=template_id,
            path=path,
            manager=manager,
            description=description
        )
        
        if error:
            QMessageBox.critical(self, "错误", f"导入项目失败: {error}")
            return
        
        QMessageBox.information(self, "成功", f"项目导入成功!\n项目编号: {project.code}\n项目路径: {project.path}")
        self.accept()
    
    def get_project(self):
        """获取导入的项目（在accept后调用）"""
        # 这里可以返回最新导入的项目
        projects, _ = ProjectService.list_projects(page=1, size=1)
        return projects[0] if projects else None
