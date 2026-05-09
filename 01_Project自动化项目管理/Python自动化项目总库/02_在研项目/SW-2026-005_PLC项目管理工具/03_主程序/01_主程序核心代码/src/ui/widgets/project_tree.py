# -*- coding: utf-8 -*-
"""
项目浏览器树形视图组件

以树形结构展示PLC项目的目录和文档组织，
支持项目导航、文档快速访问和右键操作菜单。
"""
from PyQt5.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
    QVBoxLayout,
    QLabel,
    QMenu,
    QMessageBox,
    QAction,
)
from PyQt5.QtCore import Qt

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ProjectTreeWidget(QWidget):
    """
    项目浏览器树形视图

    功能:
    - 展示当前打开项目的目录结构
    - 以图标区分不同类型的节点 (文件夹/文档/代码)
    - 支持双击打开文档
    - 右键菜单支持新建/删除/重命名等操作
    - 与主窗口TabWidget联动切换内容区
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_project = None
        self._init_ui()

    def _init_ui(self):
        """初始化树形视图UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # 标题
        header_label = QLabel("\uD83D\uDCC1 项目浏览器")
        header_label.setStyleSheet(
            "font-size: 10pt; font-weight: bold; color: #1976D2;"
        )
        layout.addWidget(header_label)

        # 树形控件
        self._tree = QTreeWidget()
        self._tree.setHeaderLabel("项目结构")
        self._tree.setAlternatingRowColors(True)
        self._tree.setAnimated(True)
        self._tree.setColumnCount(1)

        # 绑定事件
        self._tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        self._tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._on_context_menu)

        layout.addWidget(self._tree)

        # 状态提示
        self._status_label = QLabel(
            "\U0001F5C1 未选择项目"
        )
        self._status_label.setStyleSheet(
            "font-size: 9pt; color: #9E9E9E; padding: 4px;"
        )
        layout.addWidget(self._status_label)

        # 显示默认空状态
        self._show_empty_state()

    def _show_empty_state(self):
        """显示空状态提示"""
        self._tree.clear()
        root_item = QTreeWidgetItem(self._tree)
        root_item.setText(0, "\U0001F4C1 暂无项目")
        root_item.setFlags(root_item.flags() & ~Qt.ItemIsSelectable)
        root_item.setForeground(0, Qt.gray)

    def load_project(self, project):
        """加载并显示项目目录结构"""
        self._current_project = project
        self._tree.clear()

        if not project:
            self._show_empty_state()
            return

        # 创建根节点
        root_item = QTreeWidgetItem(self._tree)
        root_item.setText(0, f"\uD83D\uDCC1 {project.name or '未命名项目'}")
        root_item.setData(0, Qt.UserRole, {"type": "project", "path": getattr(project, 'path', '')})
        root_item.setExpanded(True)

        project_type = getattr(project, "project_type", "generic")
        project_type_value = getattr(project_type, "value", project_type)
        if project_type_value == "dj_single_machine":
            self._build_dj_project_nodes(root_item, project)
        else:
            self._build_generic_nodes(root_item)

        self._status_label.setText(
            f"\U0001F4C1 已加载: {project.name or '未命名'}"
        )
        logger.info(f"项目树已加载: {project.name}")

    def _build_generic_nodes(self, root_item: QTreeWidgetItem):
        """构建通用项目节点"""
        standard_nodes = [
            ("\U0001F4C2 项目基础信息", "folder"),
            ("\U0001F4CB 文档管理", "folder"),
            ("\u26A1 PLC程序", "folder"),
            ("\uD83D\uDDA5 HMI配置", "folder"),
            ("\U0001F9EA 变量清单", "document"),
            ("\U0001F4CF IO分配表", "document"),
            ("\U0001F6D7 报警定义", "document"),
        ]

        for node_name, node_type in standard_nodes:
            child = QTreeWidgetItem(root_item)
            child.setText(0, node_name)
            child.setData(0, Qt.UserRole, {
                "type": node_type,
                "name": node_name.strip(),
            })
            if node_type == "folder":
                placeholder = QTreeWidgetItem(child)
                placeholder.setText(0, "(空)")

    def _build_dj_project_nodes(self, root_item: QTreeWidgetItem, project):
        """构建DJ单机项目节点"""
        workflow_stage = getattr(project, "workflow_stage", "")
        workflow_value = getattr(workflow_stage, "value", workflow_stage)
        stage_node = QTreeWidgetItem(root_item)
        stage_node.setText(0, f"\U0001F4DD 当前阶段: {workflow_value or 'unknown'}")
        stage_node.setData(0, Qt.UserRole, {"type": "workflow"})

        roots_node = QTreeWidgetItem(root_item)
        roots_node.setText(0, "\U0001F4C2 核心资产")
        roots_node.setExpanded(True)

        for artifact in getattr(project, "artifact_roots", []):
            child = QTreeWidgetItem(roots_node)
            child.setText(
                0,
                f"{artifact.get('artifact_type', 'asset')}: {artifact.get('relative_path', artifact.get('name', ''))}",
            )
            child.setData(0, Qt.UserRole, artifact)

        changes_node = QTreeWidgetItem(root_item)
        changes_node.setText(0, "\U0001F4CB 变更摘要")
        changes_node.setExpanded(True)
        change_summary = getattr(project, "change_status_summary", {}) or {}
        for key, value in change_summary.items():
            child = QTreeWidgetItem(changes_node)
            child.setText(0, f"{key}: {value}")

        docs_node = QTreeWidgetItem(root_item)
        docs_node.setText(0, "\U0001F4DD 文档资产")
        docs_node.setExpanded(True)
        for document in getattr(project, "documents", [])[:20]:
            child = QTreeWidgetItem(docs_node)
            child.setText(0, document.get("relative_path", document.get("name", "document")))
            child.setData(0, Qt.UserRole, document)

    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """处理双击事件"""
        data = item.data(0, Qt.UserRole) or {}
        item_type = data.get("type", "")

        if item_type in ("document", "code"):
            name = data.get("name", item.text(0))
            logger.info(f"双击打开: {name}")
            # TODO: 联动TabWidget切换到对应编辑器页面

    def _on_context_menu(self, position):
        """显示右键上下文菜单"""
        item = self._tree.itemAt(position)
        if not item:
            return

        menu = QMenu(self)

        action_new_doc = QAction("\U0001F4DD 新建文档...", menu)
        action_new_doc.triggered.connect(lambda: self._on_new_document(item))
        menu.addAction(action_new_doc)

        action_refresh = QAction("\U0001F504 刷新", menu)
        action_refresh.triggered.connect(lambda: self._refresh_tree(item))
        menu.addAction(action_refresh)

        menu.addSeparator()

        action_expand = QAction("\u25B6 展开全部", menu)
        action_expand.triggered.connect(lambda: self._expand_all(item))
        menu.addAction(action_expand)

        action_collapse = QAction("\u25BC 折叠全部", menu)
        action_collapse.triggered.connect(lambda: self._collapse_all(item))
        menu.addAction(action_collapse)

        menu.exec_(self._tree.viewport().mapToGlobal(position))

    def _on_new_document(self, item: QTreeWidgetItem):
        """新建文档"""
        try:
            from ..dialogs.new_document_dialog import NewDocumentDialog
            dialog = NewDocumentDialog(self)
            if dialog.exec_() == dialog.Accepted:
                doc_data = dialog.get_document_data()
                new_child = QTreeWidgetItem(item)
                new_child.setText(0, f"\U0001F4DD {doc_data['doc_name']}")
                new_child.setData(0, Qt.UserRole, {
                    "type": "document",
                    **doc_data,
                })
                logger.info(f"新增文档节点: {doc_data['doc_name']}")
        except Exception as e:
            logger.exception(f"新建文档失败: {e}")

    def _refresh_tree(self, item: QTreeWidgetItem):
        """刷新指定节点的子项"""
        if self._current_project:
            self.load_project(self._current_project)

    def _expand_all(self, item: QTreeWidgetItem):
        """展开所有子节点"""
        self._expand_item_recursive(item)

    def _collapse_all(self, item: QTreeWidgetItem):
        """折叠所有子节点"""
        self._collapse_item_recursive(item)

    def _expand_item_recursive(self, item: QTreeWidgetItem):
        """递归展开"""
        item.setExpanded(True)
        for i in range(item.childCount()):
            self._expand_item_recursive(item.child(i))

    def _collapse_item_recursive(self, item: QTreeWidgetItem):
        """递归折叠"""
        for i in range(item.childCount()):
            self._collapse_item_recursive(item.child(i))
        item.setExpanded(False)

    @property
    def current_project(self):
        """获取当前加载的项目对象"""
        return self._current_project
