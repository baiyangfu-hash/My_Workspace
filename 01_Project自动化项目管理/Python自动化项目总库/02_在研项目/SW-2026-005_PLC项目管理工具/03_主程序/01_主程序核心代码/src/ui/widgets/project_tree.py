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
    QInputDialog,
)
from PyQt5.QtCore import Qt, pyqtSignal

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ProjectTreeWidget(QWidget):
    """
    项目浏览器树形视图

    功能:
    - 展示当前打开项目的目录结构
    - 以图标区分不同类型的节点 (文件夹/文档/代码)
    - 支持双击打开文档并导航到对应Tab
    - 右键菜单支持新建/删除/重命名等操作
    - 与主窗口TabWidget联动切换内容区

    Signals:
        navigation_requested(int, dict): 请求导航到指定Tab
            - int: Tab索引
            - dict: 上下文数据 (如项目对象)
    """

    navigation_requested = pyqtSignal(int, dict)

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
        header_label.setProperty("treeHeader", True)
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
        self._status_label.setProperty("treeStatus", True)
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

        root_item = QTreeWidgetItem(self._tree)
        root_item.setText(0, f"\uD83D\uDCC1 {project.name or '未命名项目'}")
        root_item.setData(0, Qt.UserRole, {"type": "project", "path": getattr(project, 'path', '')})
        root_item.setExpanded(True)

        project_type = getattr(project, "project_type", "generic")
        project_type_value = getattr(project_type, "value", project_type)
        if project_type_value == "dj_single_machine":
            self._build_dj_project_nodes(root_item, project)
        elif project_type_value == "plc_library":
            self._build_library_nodes(root_item, project)
        else:
            self._build_generic_nodes(root_item)

        self._status_label.setText(
            f"\U0001F4C1 已加载: {project.name or '未命名'}"
        )
        logger.info(f"项目树已加载: {project.name}")

    def load_workspace(self, workspace_path: str, projects: list):
        """加载工作空间并显示多个子项目

        Args:
            workspace_path: 工作空间根目录路径
            projects: 子项目 Project 对象列表
        """
        self._current_project = None
        self._tree.clear()

        from pathlib import Path as _Path
        workspace_name = _Path(workspace_path).name

        root_item = QTreeWidgetItem(self._tree)
        root_item.setText(0, f"\U0001F3E2 工作空间: {workspace_name}")
        root_item.setData(0, Qt.UserRole, {
            "type": "workspace",
            "path": workspace_path,
        })
        root_item.setExpanded(True)

        try:
            from src.services.workspace_service import WorkspaceService
            stats = WorkspaceService.get_workspace_statistics(workspace_path, projects)
            if stats:
                stats_node = QTreeWidgetItem(root_item)
                stats_node.setText(
                    0,
                    f"\U0001F4CA 汇总: {stats['total_projects']}个项目 | "
                    f"{stats['total_st_files']}个ST | "
                    f"{stats['total_spec_files']}个规范 | "
                    f"{stats['naming_conflicts']}个冲突",
                )
                stats_node.setData(0, Qt.UserRole, {"type": "workflow"})
        except Exception:
            pass

        for project in projects:
            child_item = QTreeWidgetItem(root_item)
            project_type = getattr(project, "project_type", "generic")
            project_type_value = getattr(project_type, "value", project_type)

            if project_type_value == "dj_single_machine":
                child_item.setText(0, f"\uD83D\uDCC1 {project.name}")
            elif project_type_value == "plc_library":
                child_item.setText(0, f"\U0001F4DA {project.name}")
            else:
                child_item.setText(0, f"\uD83D\uDCC4 {project.name}")

            child_item.setData(0, Qt.UserRole, {
                "type": "project",
                "path": getattr(project, 'path', ''),
                "project_type": project_type_value,
            })
            child_item.setExpanded(False)

            if project_type_value == "dj_single_machine":
                self._build_dj_project_nodes(child_item, project)
            elif project_type_value == "plc_library":
                self._build_library_nodes(child_item, project)
            else:
                self._build_generic_nodes(child_item)

        self._status_label.setText(
            f"\U0001F3E2 工作空间: {workspace_name} ({len(projects)} 个子项目)"
        )
        logger.info(f"工作空间树已加载: {workspace_name}, {len(projects)} 个子项目")

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

    def _build_library_nodes(self, root_item: QTreeWidgetItem, project):
        """构建共享库项目节点"""
        desc = getattr(project, "description", "")
        if desc:
            desc_node = QTreeWidgetItem(root_item)
            desc_node.setText(0, f"\U0001F4DD {desc}")
            desc_node.setData(0, Qt.UserRole, {"type": "workflow"})

        extra = getattr(project, "extra", {})
        library_scan = extra.get("library_scan", {})

        if library_scan:
            summary_node = QTreeWidgetItem(root_item)
            total_st = library_scan.get("total_st_files", 0)
            total_spec = library_scan.get("total_spec_files", 0)
            total_cat = library_scan.get("total_artifacts", 0)
            summary_node.setText(
                0,
                f"\U0001F4CA 汇总: {total_cat}个分类 | {total_st}个ST文件 | {total_spec}个规范文件",
            )
            summary_node.setData(0, Qt.UserRole, {"type": "workflow"})

        categories = library_scan.get("categories", [])
        if categories:
            roots_node = QTreeWidgetItem(root_item)
            roots_node.setText(0, "\U0001F4C2 库资产分类")
            roots_node.setExpanded(True)

            for cat in categories:
                cat_item = QTreeWidgetItem(roots_node)
                cat_name = cat.get("name", "")
                file_count = cat.get("file_count", 0)
                spec_count = cat.get("spec_count", 0)
                cat_item.setText(
                    0,
                    f"\U0001F4E6 {cat_name} ({file_count} ST | {spec_count} 规范)",
                )
                cat_item.setData(0, Qt.UserRole, {
                    "type": "folder",
                    "path": cat.get("absolute_path", ""),
                    "name": cat_name,
                })

        spec_dirs = extra.get("spec_dirs", [])
        if spec_dirs:
            spec_node = QTreeWidgetItem(root_item)
            spec_node.setText(0, "\U0001F4D6 规范目录")
            spec_node.setExpanded(True)

            for sd in spec_dirs:
                sd_item = QTreeWidgetItem(spec_node)
                sd_name = sd.get("name", "")
                sd_files = sd.get("files", [])
                sd_item.setText(
                    0,
                    f"\U0001F4C4 {sd_name} ({len(sd_files)} 文件)",
                )
                sd_item.setData(0, Qt.UserRole, {
                    "type": "folder",
                    "path": sd.get("absolute_path", sd.get("path", "")),
                    "name": sd_name,
                })

        orphan_files = library_scan.get("orphan_files", [])
        if orphan_files:
            orphan_node = QTreeWidgetItem(root_item)
            orphan_node.setText(0, f"\u26A0\uFE0F 孤立文件 ({len(orphan_files)})")
            for of in orphan_files:
                of_item = QTreeWidgetItem(orphan_node)
                of_item.setText(0, f"\U0001F4C4 {of.get('name', '')}")
                of_item.setData(0, Qt.UserRole, {
                    "type": "document",
                    "path": of.get("path", ""),
                    "name": of.get("name", ""),
                })

        if not library_scan:
            roots_node = QTreeWidgetItem(root_item)
            roots_node.setText(0, "\U0001F4C2 库资产")
            roots_node.setExpanded(True)

            for artifact in getattr(project, "artifact_roots", []):
                child = QTreeWidgetItem(roots_node)
                child.setText(
                    0,
                    f"{artifact.get('artifact_type', 'asset')}: {artifact.get('relative_path', artifact.get('name', ''))}",
                )
                child.setData(0, Qt.UserRole, artifact)

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
        """处理双击事件 — 根据节点类型导航到对应Tab或跳转到Trae"""
        data = item.data(0, Qt.UserRole) or {}
        item_type = data.get("type", "")
        name = data.get("name", item.text(0))

        context = {"project": self._current_project, "item_data": data, "name": name}

        if item_type in ("document", "code"):
            file_path = data.get("path") or data.get("relative_path", "")
            if file_path:
                from src.services.companion_service import CompanionService
                if CompanionService.should_jump_to_ide(file_path):
                    success, _ = CompanionService.jump_to_file(file_path)
                    if success:
                        logger.info(f"伴生跳转: {file_path}")
                        return
            logger.info(f"双击打开: {name}")
            self.navigation_requested.emit(2, context)
        elif item_type == "project":
            logger.info(f"双击项目节点: {name}")
            self.navigation_requested.emit(1, context)
        elif item_type == "workspace":
            logger.info(f"双击工作空间节点: {name}")
            self.navigation_requested.emit(1, context)
        elif item_type == "folder":
            self.navigation_requested.emit(1, context)
        elif item_type == "workflow":
            self.navigation_requested.emit(1, context)
        else:
            logger.debug(f"双击未识别类型节点: {item_type}")

    def _on_context_menu(self, position):
        item = self._tree.itemAt(position)
        if not item:
            return

        menu = QMenu(self)

        action_new_folder = QAction("\U0001F4C2 新建文件夹", menu)
        action_new_folder.triggered.connect(lambda: self._on_new_folder(item))
        menu.addAction(action_new_folder)

        action_new_doc = QAction("\U0001F4DD 新建文档...", menu)
        action_new_doc.triggered.connect(lambda: self._on_new_document(item))
        menu.addAction(action_new_doc)

        menu.addSeparator()

        action_rename = QAction("\u270F\uFE0F 重命名", menu)
        action_rename.triggered.connect(lambda: self._on_rename(item))
        menu.addAction(action_rename)

        action_delete = QAction("\U0001F5D1 删除", menu)
        action_delete.triggered.connect(lambda: self._on_delete(item))
        menu.addAction(action_delete)

        menu.addSeparator()

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

    def _on_new_folder(self, item: QTreeWidgetItem):
        name, ok = QInputDialog.getText(
            self, "新建文件夹", "文件夹名称:"
        )
        if ok and name.strip():
            new_child = QTreeWidgetItem(item)
            new_child.setText(0, f"\U0001F4C1 {name.strip()}")
            new_child.setData(0, Qt.UserRole, {"type": "folder", "name": name.strip()})
            item.setExpanded(True)
            logger.info(f"新建文件夹: {name.strip()}")

    def _on_rename(self, item: QTreeWidgetItem):
        data = item.data(0, Qt.UserRole) or {}
        old_name = data.get("name", item.text(0))
        new_name, ok = QInputDialog.getText(
            self, "重命名", "新名称:", text=old_name
        )
        if ok and new_name.strip() and new_name.strip() != old_name:
            data["name"] = new_name.strip()
            item.setData(0, Qt.UserRole, data)
            prefix = ""
            if data.get("type") == "folder":
                prefix = "\U0001F4C1 "
            elif data.get("type") == "document":
                prefix = "\U0001F4DD "
            item.setText(0, f"{prefix}{new_name.strip()}")
            logger.info(f"重命名: {old_name} -> {new_name.strip()}")

    def _on_delete(self, item: QTreeWidgetItem):
        data = item.data(0, Qt.UserRole) or {}
        name = data.get("name", item.text(0))
        reply = QMessageBox.question(
            self, "\u2753 确认删除",
            f"确定要删除 \"{name}\" 吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            parent = item.parent() or self._tree.invisibleRootItem()
            parent.removeChild(item)
            logger.info(f"已删除: {name}")

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
