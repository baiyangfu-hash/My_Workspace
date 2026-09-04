# -*- coding: utf-8 -*-
"""
总库管理组件
"""
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QLineEdit, QLabel, QSplitter, QTabWidget, QFormLayout,
    QTextEdit, QComboBox, QDialog, QMessageBox, QInputDialog, QFileDialog
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QFont

from src.services.library_service import LibraryService
from src.services.project_service import ProjectService
from src.services.template_service import TemplateService
from src.core.constants import BusinessLine, BUSINESS_LINE_DESC
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class LibraryManagerWidget(QWidget):
    """总库管理组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_library_id = None
        self._init_ui()
        self._load_libraries()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 顶部操作栏
        top_layout = QHBoxLayout()
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("搜索总库...")
        self.search_edit.textChanged.connect(self._on_search)
        top_layout.addWidget(self.search_edit)
        
        self.add_library_btn = QPushButton("新建总库")
        self.add_library_btn.clicked.connect(self._on_add_library)
        top_layout.addWidget(self.add_library_btn)
        
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self._load_libraries)
        top_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(top_layout)
        
        # 主分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 总库列表
        self.library_tree = QTreeWidget()
        self.library_tree.setHeaderLabels(["总库名称", "状态", "项目数"])
        self.library_tree.itemClicked.connect(self._on_library_select)
        splitter.addWidget(self.library_tree)
        
        # 右侧内容区
        self.right_widget = QWidget()
        right_layout = QVBoxLayout(self.right_widget)
        
        # 标签页
        self.tab_widget = QTabWidget()
        
        # 总库详情标签
        self.detail_tab = QWidget()
        detail_layout = QVBoxLayout(self.detail_tab)
        
        self.detail_form = QFormLayout()
        self.name_label = QLabel("名称:")
        self.name_value = QLabel("")
        self.detail_form.addRow(self.name_label, self.name_value)
        
        self.description_label = QLabel("描述:")
        self.description_value = QTextEdit()
        self.description_value.setReadOnly(True)
        self.detail_form.addRow(self.description_label, self.description_value)
        
        self.path_label = QLabel("根路径:")
        self.path_value = QLabel("")
        self.path_value.setWordWrap(True)
        self.detail_form.addRow(self.path_label, self.path_value)
        
        self.status_label = QLabel("状态:")
        self.status_value = QLabel("")
        self.detail_form.addRow(self.status_label, self.status_value)

        self.created_at_label = QLabel("创建时间:")
        self.created_at_value = QLabel("")
        self.detail_form.addRow(self.created_at_label, self.created_at_value)

        self.project_count_label = QLabel("项目数量:")
        self.project_count_value = QLabel("")
        self.detail_form.addRow(self.project_count_label, self.project_count_value)

        detail_layout.addLayout(self.detail_form)
        
        self.update_btn = QPushButton("更新总库")
        self.update_btn.clicked.connect(self._on_update_library)
        detail_layout.addWidget(self.update_btn)
        
        self.delete_btn = QPushButton("删除总库")
        self.delete_btn.clicked.connect(self._on_delete_library)
        detail_layout.addWidget(self.delete_btn)
        
        self.tab_widget.addTab(self.detail_tab, "总库详情")
        
        # 项目管理标签
        self.projects_tab = QWidget()
        projects_layout = QVBoxLayout(self.projects_tab)
        
        projects_top_layout = QHBoxLayout()
        self.add_project_btn = QPushButton("添加项目")
        self.add_project_btn.clicked.connect(self._on_add_project)
        projects_top_layout.addWidget(self.add_project_btn)

        self.remove_project_btn = QPushButton("移出总库")
        self.remove_project_btn.clicked.connect(self._on_remove_project)
        projects_top_layout.addWidget(self.remove_project_btn)

        self.scan_projects_btn = QPushButton("扫描项目")
        self.scan_projects_btn.clicked.connect(self._on_scan_projects)
        projects_top_layout.addWidget(self.scan_projects_btn)

        projects_layout.addLayout(projects_top_layout)

        self.project_tree = QTreeWidget()
        self.project_tree.setHeaderLabels(["编号", "名称", "业务线", "状态", "模板", "创建日期"])
        self.project_tree.itemDoubleClicked.connect(self._on_project_double_clicked)
        projects_layout.addWidget(self.project_tree)
        
        self.tab_widget.addTab(self.projects_tab, "项目管理")
        
        # 分类管理标签
        self.categories_tab = QWidget()
        categories_layout = QVBoxLayout(self.categories_tab)
        
        categories_top_layout = QHBoxLayout()
        self.add_category_btn = QPushButton("新建分类")
        self.add_category_btn.clicked.connect(self._on_add_category)
        categories_top_layout.addWidget(self.add_category_btn)
        categories_layout.addLayout(categories_top_layout)
        
        self.category_tree = QTreeWidget()
        self.category_tree.setHeaderLabels(["分类名称", "项目数", "描述"])
        self.category_tree.itemClicked.connect(self._on_category_clicked)
        categories_layout.addWidget(self.category_tree)
        
        self.tab_widget.addTab(self.categories_tab, "分类管理")
        
        # 统计标签
        self.stats_tab = QWidget()
        stats_layout = QVBoxLayout(self.stats_tab)
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        stats_layout.addWidget(self.stats_text)
        
        self.tab_widget.addTab(self.stats_tab, "统计信息")
        
        right_layout.addWidget(self.tab_widget)
        splitter.addWidget(self.right_widget)
        
        splitter.setSizes([300, 700])
        layout.addWidget(splitter)
    
    def _load_libraries(self):
        """加载总库列表"""
        self.library_tree.clear()

        try:
            libraries, _ = LibraryService.list_libraries()

            for library in libraries:
                item = QTreeWidgetItem()
                item.setText(0, library.name)
                item.setText(1, library.status)

                # 获取项目数量
                stats = LibraryService.get_library_statistics(library.library_id)
                project_count = stats.get("project_count", 0)
                item.setText(2, str(project_count))
                item.setData(0, Qt.UserRole, library.library_id)

                self.library_tree.addTopLevelItem(item)

            # 如果列表为空，尝试重新初始化默认总库（修复打包exe在新机器运行时无默认总库的问题）
            if self.library_tree.topLevelItemCount() == 0:
                logger.warning("总库列表为空，尝试自动初始化默认总库...")
                lib, msg = LibraryService.initialize_default_library()
                if lib:
                    logger.info(f"自动恢复默认总库成功: {lib.name} (ID={lib.library_id})")
                    # 递归调用自身重新加载
                    self._load_libraries()
                    return
                else:
                    logger.error(f"自动恢复默认总库失败: {msg}")

        except Exception as e:
            logger.exception(f"加载总库列表失败: {e}")
            QMessageBox.warning(self, "警告", f"加载总库列表失败: {str(e)}")
    
    def _on_library_select(self, item, column):
        """选择总库"""
        library_id = item.data(0, Qt.UserRole)
        if library_id:
            self.current_library_id = library_id
            self._load_library_detail(library_id)
            self._load_library_projects(library_id)
            self._load_library_categories(library_id)
            self._load_library_statistics(library_id)
    
    def _load_library_detail(self, library_id):
        """加载总库详情"""
        try:
            library = LibraryService.get_library(library_id)
            if library:
                self.name_value.setText(library.name)
                self.description_value.setPlainText(library.description or "")

                # 显示根路径（增加防御性检查）
                root_path = getattr(library, 'root_path', None) or ""
                if not root_path:
                    logger.warning(f"总库 {library.library_id} 的根路径为空，尝试修复...")
                    # 尝试使用当前工作目录作为默认值
                    root_path = os.getcwd()
                    logger.info(f"已设置默认根路径: {root_path}")
                self.path_value.setText(root_path)
                self.path_value.setToolTip(root_path)  # 添加tooltip显示完整路径

                self.status_value.setText(library.status)

                # 设置状态颜色
                status_colors = {
                    "活跃": "#28a745",  # 绿色
                    "归档": "#6c757d",  # 灰色
                    "禁用": "#dc3545",  # 红色
                }
                color = status_colors.get(library.status, "#000000")
                self.status_value.setStyleSheet(f"color: {color}; font-weight: bold;")

                # 设置创建时间
                if hasattr(library, 'created_at') and library.created_at:
                    if isinstance(library.created_at, str):
                        self.created_at_value.setText(library.created_at)
                    else:
                        self.created_at_value.setText(library.created_at.strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    self.created_at_value.setText("未知")

                # 设置项目数量
                stats = LibraryService.get_library_statistics(library_id)
                project_count = stats.get("project_count", 0)
                self.project_count_value.setText(str(project_count))

                logger.debug(f"总库详情加载完成: name={library.name}, root_path={root_path}")

        except Exception as e:
            logger.exception(f"加载总库详情失败: {e}")
    
    def _load_library_projects(self, library_id, category_id=None):
        """加载总库中的项目"""
        self.project_tree.clear()

        try:
            projects, _ = LibraryService.list_library_projects(
                library_id=library_id,
                category_id=category_id
            )

            for project in projects:
                item = QTreeWidgetItem()
                item.setText(0, project.code)
                item.setText(1, project.name)

                # 业务线
                business_line = getattr(project, 'business_line', None)
                if business_line:
                    from src.core.constants import BUSINESS_LINE_DESC
                    item.setText(2, BUSINESS_LINE_DESC.get(business_line, str(business_line)))
                else:
                    item.setText(2, "")

                # 状态
                item.setText(3, project.status.value if hasattr(project.status, 'value') else str(project.status))

                # 模板
                template_id = getattr(project, 'template_id', None)
                item.setText(4, template_id or "")

                # 创建日期
                created_at = getattr(project, 'created_at', None)
                if created_at:
                    if isinstance(created_at, str):
                        item.setText(5, created_at[:10])  # 只显示日期部分
                    else:
                        item.setText(5, created_at.strftime("%Y-%m-%d"))
                else:
                    item.setText(5, "")

                item.setData(0, Qt.UserRole, project.project_id)

                self.project_tree.addTopLevelItem(item)

        except Exception as e:
            logger.exception(f"加载项目列表失败: {e}")
    
    def _load_library_categories(self, library_id):
        """加载总库分类"""
        self.category_tree.clear()

        try:
            categories = LibraryService.list_categories(library_id)

            # 获取每个分类的项目数量
            category_project_counts = {}
            for category in categories:
                projects, _ = LibraryService.list_library_projects(
                    library_id=library_id,
                    category_id=category.category_id
                )
                category_project_counts[category.category_id] = len(projects)

            # 构建分类树
            category_map = {}
            root_items = []

            for category in categories:
                item = QTreeWidgetItem()
                item.setText(0, category.name)

                # 显示项目数量
                count = category_project_counts.get(category.category_id, 0)
                item.setText(1, str(count))

                item.setText(2, category.description or "")
                item.setData(0, Qt.UserRole, category.category_id)
                category_map[category.category_id] = item

                if not category.parent_id:
                    root_items.append(item)
                else:
                    parent_item = category_map.get(category.parent_id)
                    if parent_item:
                        parent_item.addChild(item)

            for item in root_items:
                self.category_tree.addTopLevelItem(item)

            # 展开所有节点
            self.category_tree.expandAll()

        except Exception as e:
            logger.exception(f"加载分类列表失败: {e}")
    
    def _load_library_statistics(self, library_id):
        """加载总库统计信息"""
        try:
            stats = LibraryService.get_library_statistics(library_id)

            # 构建美化的统计文本
            stats_text = "📊 总库统计\n"
            stats_text += "━━━━━━━━━━━━━━━\n\n"
            stats_text += f"总项目数: {stats.get('project_count', 0)}\n"
            stats_text += f"分类数: {stats.get('category_count', 0)}\n\n"

            # 状态分布
            status_dist = stats.get('status_distribution', {})
            if status_dist:
                stats_text += "按状态分布:\n"
                for status, count in status_dist.items():
                    # 添加状态图标
                    status_icons = {
                        "规划中": "📋",
                        "进行中": "🔄",
                        "已完成": "✅",
                        "已暂停": "⏸️",
                        "已取消": "❌"
                    }
                    icon = status_icons.get(status, "📌")
                    stats_text += f"  {icon} {status}: {count}\n"

            stats_text += "\n"

            # 业务线分布
            bl_dist = stats.get('business_line_distribution', {})
            if bl_dist:
                stats_text += "按业务线分布:\n"
                for bl, count in bl_dist.items():
                    # 添加业务线图标
                    bl_icons = {
                        "自动化项目": "🤖",
                        "设备项目": "🔧",
                        "软件项目": "💻",
                        "升级项目": "⬆️"
                    }
                    icon = bl_icons.get(bl, "📁")
                    stats_text += f"  {icon} {bl}: {count}\n"

            self.stats_text.setPlainText(stats_text)

        except Exception as e:
            logger.exception(f"加载统计信息失败: {e}")
    
    def _on_add_library(self):
        """新建总库"""
        dialog = LibraryDialog(self)
        if dialog.exec_() == dialog.Accepted:
            name = dialog.name_edit.text()
            root_path = dialog.path_edit.text()
            description = dialog.description_edit.toPlainText()
            
            library, error = LibraryService.create_library(
                name=name,
                root_path=root_path,
                description=description
            )
            
            if error:
                QMessageBox.warning(self, "警告", f"创建总库失败: {error}")
            else:
                QMessageBox.information(self, "成功", "总库创建成功")
                self._load_libraries()
    
    def _on_update_library(self):
        """更新总库"""
        if not self.current_library_id:
            QMessageBox.warning(self, "警告", "请先选择一个总库")
            return
        
        dialog = LibraryDialog(self, self.current_library_id)
        if dialog.exec_() == dialog.Accepted:
            data = {}
            if dialog.name_edit.text():
                data['name'] = dialog.name_edit.text()
            if dialog.path_edit.text():
                data['root_path'] = dialog.path_edit.text()
            if dialog.description_edit.toPlainText():
                data['description'] = dialog.description_edit.toPlainText()
            
            library, error = LibraryService.update_library(self.current_library_id, data)
            
            if error:
                QMessageBox.warning(self, "警告", f"更新总库失败: {error}")
            else:
                QMessageBox.information(self, "成功", "总库更新成功")
                self._load_libraries()
                self._load_library_detail(self.current_library_id)
    
    def _on_delete_library(self):
        """删除总库"""
        if not self.current_library_id:
            QMessageBox.warning(self, "警告", "请先选择一个总库")
            return
        
        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除这个总库吗？删除前请确保总库中没有项目。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, error = LibraryService.delete_library(self.current_library_id)
            
            if error:
                QMessageBox.warning(self, "警告", f"删除总库失败: {error}")
            else:
                QMessageBox.information(self, "成功", "总库删除成功")
                self.current_library_id = None
                self._load_libraries()
                # 清空详情
                self.name_value.setText("")
                self.description_value.setPlainText("")
                self.path_value.setText("")
                self.status_value.setText("")
                self.project_tree.clear()
                self.category_tree.clear()
                self.stats_text.setPlainText("")
    
    def _on_add_project(self):
        """添加项目到总库"""
        if not self.current_library_id:
            QMessageBox.warning(self, "警告", "请先选择一个总库")
            return
        
        # 选择项目
        projects, _ = ProjectService.list_projects()
        project_names = [f"{p.code} - {p.name}" for p in projects]
        
        if not project_names:
            QMessageBox.warning(self, "警告", "没有可添加的项目")
            return
        
        project_name, ok = QInputDialog.getItem(
            self,
            "选择项目",
            "请选择要添加的项目:",
            project_names,
            0,
            False
        )
        
        if ok and project_name:
            project_code = project_name.split(" - ")[0]
            project = ProjectService.get_project_by_code(project_code)
            
            if project:
                success, error = LibraryService.add_project_to_library(
                    library_id=self.current_library_id,
                    project_id=project.project_id
                )
                
                if error:
                    QMessageBox.warning(self, "警告", f"添加项目失败: {error}")
                else:
                    QMessageBox.information(self, "成功", "项目添加成功")
                    self._load_library_projects(self.current_library_id)

    def _on_remove_project(self):
        """从总库中移除项目"""
        if not self.current_library_id:
            QMessageBox.warning(self, "警告", "请先选择一个总库")
            return

        # 获取选中的项目
        current_item = self.project_tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择要移出的项目")
            return

        project_id = current_item.data(0, Qt.UserRole)
        project_name = current_item.text(1)

        reply = QMessageBox.question(
            self,
            "确认移出",
            f"确定要将项目 [{project_name}] 从总库中移出吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            success, error = LibraryService.remove_project_from_library(
                library_id=self.current_library_id,
                project_id=project_id
            )

            if error:
                QMessageBox.warning(self, "警告", f"移出项目失败: {error}")
            else:
                QMessageBox.information(self, "成功", "项目已从总库中移出")
                self._load_library_projects(self.current_library_id)
                self._load_library_statistics(self.current_library_id)

    def _on_project_double_clicked(self, item, column):
        """双击项目打开详情"""
        project_id = item.data(0, Qt.UserRole)
        if project_id:
            # 发射信号或调用主窗口的方法来打开项目详情
            logger.info(f"双击打开项目: {project_id}")
            # 这里可以通过信号通知主窗口打开项目详情页
            # 如果需要，可以定义一个自定义信号
    
    def _on_scan_projects(self):
        """扫描项目"""
        if not self.current_library_id:
            QMessageBox.warning(self, "警告", "请先选择一个总库")
            return
        
        # 选择扫描路径
        scan_path = QFileDialog.getExistingDirectory(
            self,
            "选择扫描目录",
            "C:/"
        )
        
        if scan_path:
            # 选择业务线（使用枚举值和描述）
            business_lines = [f"{bl.value} - {BUSINESS_LINE_DESC.get(bl, bl.value)}" for bl in BusinessLine]
            business_line, ok = QInputDialog.getItem(
                self,
                "选择业务线",
                "请选择业务线:",
                business_lines,
                0,
                False
            )
            
            if ok and business_line:
                # 提取纯枚举值（去除描述部分）
                business_line = business_line.split(" - ")[0].strip()

                # 选择模板（从TemplateService获取可用模板）
                templates = TemplateService.list_templates()
                template_id = templates[0].template_id if templates else ""
                if not template_id:
                    QMessageBox.warning(self, "警告", "没有可用的模板，请先创建模板")
                    return
                
                # 扫描并导入
                success_projects, failed_projects = LibraryService.scan_and_import_projects(
                    library_id=self.current_library_id,
                    scan_path=scan_path,
                    business_line=business_line,
                    template_id=template_id
                )
                
                message = f"扫描完成\n成功: {len(success_projects)} 个项目\n失败: {len(failed_projects)} 个项目"
                if failed_projects:
                    message += "\n\n失败项目:\n" + "\n".join(failed_projects)
                
                QMessageBox.information(self, "扫描完成", message)
                self._load_library_projects(self.current_library_id)
    
    def _on_add_category(self):
        """新建分类"""
        if not self.current_library_id:
            QMessageBox.warning(self, "警告", "请先选择一个总库")
            return
        
        name, ok = QInputDialog.getText(
            self,
            "新建分类",
            "请输入分类名称:"
        )
        
        if ok and name:
            description, ok = QInputDialog.getText(
                self,
                "新建分类",
                "请输入分类描述:"
            )
            
            category, error = LibraryService.create_category(
                library_id=self.current_library_id,
                name=name,
                description=description if ok else ""
            )
            
            if error:
                QMessageBox.warning(self, "警告", f"创建分类失败: {error}")
            else:
                QMessageBox.information(self, "成功", "分类创建成功")
                self._load_library_categories(self.current_library_id)

    def _on_category_clicked(self, item, column):
        """点击分类节点，过滤项目列表"""
        if not self.current_library_id:
            return

        category_id = item.data(0, Qt.UserRole)
        if category_id:
            # 切换到项目管理标签页
            self.tab_widget.setCurrentIndex(1)  # 项目管理是第2个标签页（索引为1）

            # 按分类过滤项目
            self._load_library_projects(self.current_library_id, category_id=category_id)
            logger.info(f"按分类过滤项目: {category_id}")
    
    def _on_search(self, text):
        """搜索总库"""
        # 简单的客户端搜索
        for i in range(self.library_tree.topLevelItemCount()):
            item = self.library_tree.topLevelItem(i)
            library_name = item.text(0)
            if text.lower() in library_name.lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

class LibraryDialog(QDialog):
    """总库编辑对话框"""
    
    def __init__(self, parent=None, library_id=None):
        super().__init__(parent)
        self.library_id = library_id
        self.setWindowTitle("编辑总库" if library_id else "新建总库")
        self.setMinimumWidth(500)
        self._init_ui()
        
        if library_id:
            self._load_library_data()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self.name_label = QLabel("总库名称:")
        self.name_edit = QLineEdit()
        form_layout.addRow(self.name_label, self.name_edit)
        
        self.path_label = QLabel("根路径:")
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.browse_btn = QPushButton("浏览...")
        self.browse_btn.clicked.connect(self._on_browse)
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.browse_btn)
        form_layout.addRow(self.path_label, path_layout)
        
        self.description_label = QLabel("描述:")
        self.description_edit = QTextEdit()
        form_layout.addRow(self.description_label, self.description_edit)
        
        layout.addLayout(form_layout)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.ok_btn = QPushButton("确定")
        self.ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_btn)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
    
    def _load_library_data(self):
        """加载总库数据"""
        try:
            library = LibraryService.get_library(self.library_id)
            if library:
                self.name_edit.setText(library.name)
                self.path_edit.setText(library.root_path)
                self.description_edit.setPlainText(library.description or "")
        except Exception as e:
            logger.exception(f"加载总库数据失败: {e}")
    
    def _on_browse(self):
        """浏览路径"""
        path = QFileDialog.getExistingDirectory(
            self,
            "选择根路径",
            "C:/"
        )
        if path:
            self.path_edit.setText(path)
