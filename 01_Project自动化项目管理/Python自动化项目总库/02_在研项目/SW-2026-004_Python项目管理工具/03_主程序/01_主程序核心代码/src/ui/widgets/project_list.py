# -*- coding: utf-8 -*-
"""
项目列表控件
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QLineEdit, QComboBox, QLabel, QMessageBox, QMenu, QDialog
)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QBrush, QColor, QFont

from src.services.project_service import ProjectService
from src.core.constants import ProjectStatus, BUSINESS_LINE_DESC, PROJECT_STATUS_COLOR
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ProjectListWidget(QWidget):
    """项目列表控件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.projects = []
        self._init_ui()
        self._load_projects()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 使用全局样式，不设置局部样式
        
        # 顶部工具栏
        toolbar_layout = QHBoxLayout()
        
        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索项目名称/编号...")
        self.search_input.textChanged.connect(self._filter_projects)
        self.search_input.setMinimumWidth(200)
        toolbar_layout.addWidget(self.search_input)
        
        # 状态筛选
        toolbar_layout.addWidget(QLabel("状态:"))
        self.status_filter = QComboBox()
        self.status_filter.addItem("全部", "")
        for status in ProjectStatus:
            self.status_filter.addItem(status.value, status.value)
        self.status_filter.currentTextChanged.connect(self._filter_projects)
        toolbar_layout.addWidget(self.status_filter)
        
        # 业务线筛选
        toolbar_layout.addWidget(QLabel("业务线:"))
        self.business_filter = QComboBox()
        self.business_filter.addItem("全部", "")
        for bl in BUSINESS_LINE_DESC:
            self.business_filter.addItem(BUSINESS_LINE_DESC[bl], bl.value)
        self.business_filter.currentTextChanged.connect(self._filter_projects)
        toolbar_layout.addWidget(self.business_filter)
        
        toolbar_layout.addStretch()
        
        # 按钮
        self.new_btn = QPushButton("新建项目")
        self.new_btn.setDefault(True)
        self.new_btn.clicked.connect(self._on_new_project)
        toolbar_layout.addWidget(self.new_btn)
        
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self._load_projects)
        toolbar_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(toolbar_layout)
        
        # 项目表格
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "项目编号", "项目名称", "业务线", "负责人", "状态", "创建时间", "操作"
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
        
        # 设置表格属性
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("QTableWidget { alternate-background-color: #f8f9fa; }")
        self.table.setShowGrid(False)
        
        # 右键菜单
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        
        # 双击事件
        self.table.doubleClicked.connect(self._on_project_double_click)
        
        layout.addWidget(self.table)
    
    def _load_projects(self):
        """加载项目列表"""
        try:
            logger.info("正在加载项目列表...")
            self.projects, total = ProjectService.list_projects(page=1, size=1000)
            logger.info(f"加载完成，共 {total} 个项目")
            self._display_projects(self.projects)
        except Exception as e:
            logger.exception(f"加载项目列表失败: {e}")
            QMessageBox.critical(self, "错误", f"加载项目列表失败: {str(e)}")
    
    def _display_projects(self, projects):
        """显示项目列表"""
        try:
            self.table.setRowCount(len(projects))
            
            for row, project in enumerate(projects):
                # 项目编号
                code_item = QTableWidgetItem(project.code)
                code_item.setData(Qt.UserRole, project.project_id)
                self.table.setItem(row, 0, code_item)
                
                # 项目名称
                self.table.setItem(row, 1, QTableWidgetItem(project.name))
                
                # 业务线
                bl_desc = BUSINESS_LINE_DESC.get(project.business_line, str(project.business_line))
                self.table.setItem(row, 2, QTableWidgetItem(bl_desc))
                
                # 负责人
                self.table.setItem(row, 3, QTableWidgetItem(project.manager or "-"))
                
                # 状态
                status_item = QTableWidgetItem(project.status.value)
                color = QColor(PROJECT_STATUS_COLOR.get(project.status, "#9E9E9E"))
                status_item.setForeground(QBrush(color))
                self.table.setItem(row, 4, status_item)
                
                # 创建时间
                create_time = project.created_at.strftime("%Y-%m-%d")
                self.table.setItem(row, 5, QTableWidgetItem(create_time))
                
                # 操作
                self.table.setItem(row, 6, QTableWidgetItem("查看详情"))
            
            self.table.resizeRowsToContents()
            logger.info(f"项目列表已显示 {len(projects)} 个项目")
        except Exception as e:
            logger.exception(f"显示项目列表失败: {e}")
            QMessageBox.critical(self, "错误", f"显示项目列表失败: {str(e)}")
    
    def _filter_projects(self):
        """筛选项目"""
        keyword = self.search_input.text().lower()
        status = self.status_filter.currentData()
        business_line = self.business_filter.currentData()
        
        filtered = []
        for project in self.projects:
            # 关键词筛选
            if keyword:
                if keyword not in project.name.lower() and keyword not in project.code.lower():
                    continue
            
            # 状态筛选
            if status and project.status.value != status:
                continue
            
            # 业务线筛选
            if business_line and project.business_line.value != business_line:
                continue
            
            filtered.append(project)
        
        self._display_projects(filtered)
    
    def _show_context_menu(self, pos: QPoint):
        """显示右键菜单"""
        item = self.table.itemAt(pos)
        if not item:
            return
        
        row = self.table.row(item)
        project_id = self.table.item(row, 0).data(Qt.UserRole)
        project = next((p for p in self.projects if p.project_id == project_id), None)
        if not project:
            return
        
        menu = QMenu(self)
        
        open_action = menu.addAction("打开项目目录")
        edit_action = menu.addAction("编辑项目信息")
        change_template_action = menu.addAction("变更模板")
        check_action = menu.addAction("规范检查")
        report_action = menu.addAction("生成报告")
        archive_action = menu.addAction("归档项目")
        delete_action = menu.addAction("删除项目")
        
        action = menu.exec_(self.table.mapToGlobal(pos))
        
        if action == open_action:
            self._open_project_dir(project)
        elif action == edit_action:
            self._edit_project(project)
        elif action == change_template_action:
            self._change_template(project)
        elif action == check_action:
            self._run_check(project)
        elif action == report_action:
            self._generate_report(project)
        elif action == archive_action:
            self._archive_project(project)
        elif action == delete_action:
            self._delete_project(project)
    
    def get_selected_items(self):
        """获取当前选中的项目对象列表（供主窗口菜单调用）"""
        selected_rows = set(item.row() for item in self.table.selectedItems())
        result = []
        for row in selected_rows:
            project_id = self.table.item(row, 0).data(Qt.UserRole)
            project = next((p for p in self.projects if p.project_id == project_id), None)
            if project:
                result.append(project)
        return result

    def _on_project_double_click(self, index):
        """双击项目行"""
        row = index.row()
        project_id = self.table.item(row, 0).data(Qt.UserRole)
        project = next((p for p in self.projects if p.project_id == project_id), None)
        if project:
            self._open_project_dir(project)
    
    def _on_new_project(self):
        """新建项目"""
        try:
            from src.ui.dialogs.new_project_dialog import NewProjectDialog

            dialog = NewProjectDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                self._load_projects()
                if hasattr(self.parent(), 'status_bar'):
                    self.parent().status_bar.showMessage("项目创建成功")
                logger.info("新建项目成功")
        except Exception as e:
            logger.exception(f"打开新建项目对话框失败: {e}")
            QMessageBox.critical(self, "错误", f"无法打开新建项目对话框: {str(e)}")
    
    def _open_project_dir(self, project):
        """打开项目目录"""
        import os
        import platform
        path = project.path
        if not os.path.exists(path):
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "错误", f"项目目录不存在: {path}")
            logger.error(f"项目目录不存在: {path}")
            return
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            os.system(f"open '{path}'")
        else:
            os.system(f"xdg-open '{path}'")
        logger.info(f"打开项目目录: {path}")
    
    def _edit_project(self, project):
        """编辑项目信息"""
        from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                     QLineEdit, QTextEdit, QFormLayout, QPushButton,
                                     QComboBox, QDateTimeEdit)
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"编辑项目 - {project.name}")
        dialog.setMinimumSize(500, 450)
        
        layout = QVBoxLayout(dialog)
        
        form = QFormLayout()
        
        self.edit_name = QLineEdit(project.name or "")
        self.edit_code = QLineEdit(project.code or "")
        self.edit_code.setReadOnly(True)
        self.edit_description = QTextEdit()
        self.edit_description.setPlainText(project.description or "")
        self.edit_manager = QLineEdit(project.manager or "")
        self.edit_status = QComboBox()
        self.edit_status.addItems([s.value for s in ProjectStatus])
        if project.status:
            self.edit_status.setCurrentText(project.status.value)
        
        form.addRow("项目编号:", self.edit_code)
        form.addRow("项目名称:", self.edit_name)
        form.addRow("负责人:", self.edit_manager)
        form.addRow("状态:", self.edit_status)
        form.addRow("项目描述:", self.edit_description)
        
        layout.addLayout(form)
        
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
            success, error = ProjectService.update_project(
                project.project_id,
                {
                    "name": self.edit_name.text().strip(),
                    "description": self.edit_description.toPlainText().strip(),
                    "manager": self.edit_manager.text().strip(),
                    "status": self.edit_status.currentText()
                }
            )
            if error:
                QMessageBox.critical(self, "错误", f"更新失败: {error}")
                return
            
            self._load_projects()
            QMessageBox.information(self, "成功", "项目信息已更新")
            logger.info(f"项目已更新: {project.code}")
    
    def _run_check(self, project):
        """运行规范检查"""
        from src.services.check_service import CheckService
        from src.services.report_service import ReportService
        
        result, error = CheckService.check_project(project)
        if error:
            QMessageBox.critical(self, "错误", f"检查失败: {error}")
            return
        
        report_path, report_error = ReportService.generate_check_report(project, result)
        if report_error:
            QMessageBox.warning(self, "警告", f"检查完成，但生成报告失败: {report_error}")
        else:
            QMessageBox.information(self, "成功", f"检查完成，报告已生成到: {report_path}")
        
        logger.info(f"项目检查完成: {project.code}")
    
    def _generate_report(self, project):
        """生成项目报告"""
        from src.services.report_service import ReportService
        
        report_path, error = ReportService.generate_project_report(project)
        if error:
            QMessageBox.critical(self, "错误", f"生成报告失败: {error}")
            return
        
        QMessageBox.information(self, "成功", f"报告已生成到: {report_path}")
        logger.info(f"生成项目报告: {project.code}")
    
    def _archive_project(self, project):
        """归档项目"""
        reply = QMessageBox.question(
            self,
            "确认归档",
            f"确定要归档项目 {project.code} {project.name} 吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, error = ProjectService.update_project(project.project_id, {
                "status": ProjectStatus.ARCHIVED.value
            })
            if error:
                QMessageBox.critical(self, "错误", f"归档失败: {error}")
                return
            
            self._load_projects()
            QMessageBox.information(self, "成功", "项目已归档")
            logger.info(f"项目已归档: {project.code}")
    
    def _delete_project(self, project):
        """删除项目"""
        # 询问删除类型
        reply = QMessageBox.question(
            self,
            "删除选项",
            f"请选择删除方式：\n\n项目：{project.code} {project.name}\n\n• 是(Y)：仅删除数据库记录（保留本地文件）\n• 否(N)：删除数据库记录 + 删除本地文件\n• 取消：取消操作",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            QMessageBox.Cancel
        )
        
        if reply == QMessageBox.Cancel:
            return
        
        hard_delete = True
        delete_local_files = (reply == QMessageBox.No)
        
        # 二次确认
        if delete_local_files:
            confirm = QMessageBox.warning(
                self,
                "危险操作确认",
                f"即将彻底删除项目和本地文件！\n\n项目路径：{project.path}\n\n此操作不可恢复，确定继续吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if confirm != QMessageBox.Yes:
                return
        
        # 执行删除
        success, error = ProjectService.delete_project(
            project.project_id, 
            hard_delete=hard_delete,
            delete_local_files=delete_local_files
        )
        
        if error:
            QMessageBox.critical(self, "错误", f"删除失败: {error}")
            return
        
        self._load_projects()
        
        if delete_local_files:
            QMessageBox.information(self, "成功", "项目已彻底删除（含本地文件）")
            logger.info(f"项目已彻底删除（含本地文件）: {project.code}")
        else:
            QMessageBox.information(self, "成功", "项目已从数据库删除（本地文件保留）")
            logger.info(f"项目已从数据库删除（本地文件保留）: {project.code}")
    
    def _change_template(self, project):
        """变更项目模板"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox
        from src.dao.template_dao import TemplateDAO
        
        # 获取可用模板
        try:
            templates = TemplateDAO.list()
            if not templates:
                QMessageBox.warning(self, "提示", "暂无可用模板")
                return
        except Exception as e:
            logger.exception(f"获取模板列表失败: {e}")
            QMessageBox.critical(self, "错误", f"获取模板列表失败: {str(e)}")
            return
        
        # 创建模板选择对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("变更模板")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel(f"项目: {project.code} {project.name}"))
        layout.addWidget(QLabel("当前模板: {}".format(project.template_id)))
        
        layout.addWidget(QLabel("请选择新模板:"))
        
        template_combo = QComboBox()
        for template in templates:
            template_combo.addItem(f"{template.name} ({template.template_id})", template.template_id)
        layout.addWidget(template_combo)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
        
        if dialog.exec_() == QDialog.Accepted:
            new_template_id = template_combo.currentData()
            
            # 执行模板变更
            try:
                logger.info(f"开始变更项目模板: {project.code} -> {new_template_id}")
                result, error = ProjectService.change_template(project.project_id, new_template_id)
                
                if error:
                    QMessageBox.critical(self, "错误", f"变更模板失败: {error}")
                    logger.error(f"变更模板失败: {error}")
                else:
                    QMessageBox.information(self, "成功", "模板变更成功")
                    self._load_projects()  # 刷新项目列表
                    logger.info(f"模板变更成功: {project.code} -> {new_template_id}")
            except Exception as e:
                logger.exception(f"变更模板异常: {e}")
                QMessageBox.critical(self, "错误", f"变更模板异常: {str(e)}")
