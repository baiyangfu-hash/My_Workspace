"""项目工作区 - 文档 Tab

展示当前项目的文档列表（按类别分组），支持双击打开文档、模板更新与预览。

布局：
    ┌─────────────────────────────────────────────────────────┐
    │ [🔄 模板更新]                                            │
    ├─────────────────────────────────────────────────────────┤
    │ 📄 项目文档                                              │
    │ ├─ 📋 PM_SESSION_XXX.md                                │
    │ ├─ 📋 立项表_XXX.md                                     │
    │ ├─ 📋 变更单_CHG-XXX.md                                │
    │ └─ 📁 09_整改项/                                        │
    │                                                         │
    │ 模板信息                                                 │
    │ 模板: plc-project-template v1.0                         │
    │ 上次更新: 2026-05-01                                     │
    │ [检查更新]                                               │
    └─────────────────────────────────────────────────────────┘

信号：
    template_updated() - 模板更新完成时发射
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any

from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

import yaml

from auto_pm.core.template_service import TemplateService
from auto_pm.logging.logging import setup_logger

log = setup_logger(log_level="INFO", app_name="auto_pm")

__all__ = ["DocTab"]

# 文档分类：(类别键, 类别显示名, 图标)
_CATEGORIES: list[tuple[str, str, str]] = [
    ("pm_session", "PM_SESSION", "📋"),
    ("initiation", "立项表", "📋"),
    ("change", "变更单", "📋"),
    ("rectification", "整改项", "📁"),
    ("other", "其他文档", "📋"),
]

# 整改项目录名
_RECT_DIR_NAME = "09_整改项"

# 文档树节点存储完整路径的 Qt role
_PATH_ROLE = Qt.ItemDataRole.UserRole + 1

_TAB_STYLE = """
QFrame#docTab { background: #fafafa; }
QPushButton#updateBtn {
    font-size: 13px; color: #ffffff;
    background: #4a90d9; border: none;
    border-radius: 4px; padding: 6px 16px;
}
QPushButton#updateBtn:hover { background: #357abd; }
QPushButton#checkBtn {
    font-size: 12px; color: #4a90d9;
    background: #ffffff; border: 1px solid #4a90d9;
    border-radius: 4px; padding: 4px 12px;
}
QPushButton#checkBtn:hover { background: #f0f5ff; }
QTreeWidget#docTree {
    background: #ffffff; border: 1px solid #e0e0e0;
    border-radius: 6px; font-size: 13px;
}
QTreeWidget#docTree::item { padding: 4px 2px; }
QLabel#sectionTitle {
    font-size: 13px; font-weight: bold; color: #333;
    padding: 4px 0;
}
QLabel#templateInfo {
    font-size: 12px; color: #555; padding: 2px 0;
}
QLabel#emptyHint {
    color: #999; font-size: 14px;
    padding: 60px;
}
QFrame#infoFrame {
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
}
"""


class DocTab(QWidget):
    """项目工作区 - 文档 Tab

    展示项目文档列表（分类分组），支持双击打开、模板更新与预览。
    模板更新完成时发射 template_updated() 信号。
    """

    template_updated = Signal()

    def __init__(
        self,
        template_service: TemplateService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._template_service = template_service
        self._project_id: str | None = None
        self._project_path: str = ""
        self._build_ui()

    # ── UI 构建 ────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.setObjectName("docTab")
        self.setStyleSheet(_TAB_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        # 顶部按钮栏
        toolbar = self._build_toolbar()
        layout.addWidget(toolbar)

        # 文档列表区
        layout.addWidget(self._build_section_label("📄 项目文档"))
        self._doc_tree = QTreeWidget()
        self._doc_tree.setObjectName("docTree")
        self._doc_tree.setHeaderHidden(True)
        self._doc_tree.setRootIsDecorated(True)
        self._doc_tree.itemDoubleClicked.connect(self._on_document_double_clicked)
        layout.addWidget(self._doc_tree, 1)

        # 空状态提示
        self._empty_hint = QLabel("暂无文档")
        self._empty_hint.setObjectName("emptyHint")
        self._empty_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_hint.setVisible(False)
        layout.addWidget(self._empty_hint)

        # 模板信息区
        layout.addWidget(self._build_template_info())

    def _build_toolbar(self) -> QWidget:
        """构建顶部按钮栏：模板更新按钮"""
        toolbar = QWidget()
        h = QHBoxLayout(toolbar)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(8)

        self._update_btn = QPushButton("🔄 模板更新")
        self._update_btn.setObjectName("updateBtn")
        self._update_btn.clicked.connect(self._on_update_template)
        h.addWidget(self._update_btn)

        h.addStretch(1)
        return toolbar

    def _build_section_label(self, text: str) -> QLabel:
        """构建分区标题"""
        label = QLabel(text)
        label.setObjectName("sectionTitle")
        return label

    def _build_template_info(self) -> QFrame:
        """构建模板信息区"""
        frame = QFrame()
        frame.setObjectName("infoFrame")
        v = QVBoxLayout(frame)
        v.setContentsMargins(14, 10, 14, 10)
        v.setSpacing(4)

        title = QLabel("模板信息")
        title.setObjectName("sectionTitle")
        v.addWidget(title)

        self._template_name_label = QLabel("模板: —")
        self._template_name_label.setObjectName("templateInfo")
        v.addWidget(self._template_name_label)

        self._template_version_label = QLabel("版本: —")
        self._template_version_label.setObjectName("templateInfo")
        v.addWidget(self._template_version_label)

        self._template_updated_label = QLabel("上次更新: —")
        self._template_updated_label.setObjectName("templateInfo")
        v.addWidget(self._template_updated_label)

        self._check_btn = QPushButton("检查更新")
        self._check_btn.setObjectName("checkBtn")
        self._check_btn.clicked.connect(self._on_check_update)
        v.addWidget(self._check_btn)

        return frame

    # ── 数据加载 ──────────────────────────────────────────

    def load_project(self, project_id: str, project_path: str) -> None:
        """加载项目文档

        Args:
            project_id: 项目编号
            project_path: 项目绝对路径
        """
        self._project_id = project_id
        self._project_path = project_path
        log.info("文档Tab加载项目: %s (path=%s)", project_id, project_path)
        self._scan_documents(project_path)
        self._load_template_info(project_path)

    def _scan_documents(self, project_path: str) -> None:
        """扫描项目目录下的文档并分类展示"""
        self._doc_tree.clear()

        if not project_path or not os.path.isdir(project_path):
            self._doc_tree.setVisible(False)
            self._empty_hint.setVisible(True)
            return

        # 按类别收集文档
        classified: dict[str, list[tuple[str, str]]] = {key: [] for key, _, _ in _CATEGORIES}

        try:
            self._collect_documents(project_path, classified)
        except OSError as e:
            log.warning("扫描文档失败 %s: %s", project_path, e)

        # 检查是否有任何文档
        total = sum(len(docs) for docs in classified.values())
        if total == 0:
            self._doc_tree.setVisible(False)
            self._empty_hint.setVisible(True)
            return

        self._doc_tree.setVisible(True)
        self._empty_hint.setVisible(False)

        # 按类别顺序构建树
        for cat_key, cat_label, cat_icon in _CATEGORIES:
            docs = classified.get(cat_key, [])
            if not docs:
                continue
            cat_item = QTreeWidgetItem(self._doc_tree, [f"{cat_icon} {cat_label} ({len(docs)})"])
            cat_item.setExpanded(True)
            for doc_name, doc_path in docs:
                child = QTreeWidgetItem(cat_item, [f"📄 {doc_name}"])
                child.setData(0, _PATH_ROLE, doc_path)

    def _collect_documents(
        self, project_path: str, classified: dict[str, list[tuple[str, str]]]
    ) -> None:
        """遍历项目目录收集文档并分类

        扫描项目根目录及一级子目录（09_整改项/ 单独归类），
        跳过隐藏目录和常见非文档目录（.git, __pycache__, node_modules 等）。
        """
        skip_dirs = {".git", "__pycache__", "node_modules", ".venv", "venv", ".idea", ".vscode"}

        # 先处理项目根目录下的 .md 文件
        try:
            entries = sorted(os.listdir(project_path))
        except OSError:
            return

        for entry in entries:
            full_path = os.path.join(project_path, entry)
            if os.path.isfile(full_path) and entry.endswith(".md"):
                cat = self._classify_document(entry)
                classified[cat].append((entry, full_path))
            elif os.path.isdir(full_path):
                if entry.startswith(".") or entry in skip_dirs:
                    continue
                # 09_整改项/ 目录单独归类
                if entry == _RECT_DIR_NAME:
                    self._collect_rectification(full_path, classified)
                else:
                    # 其他子目录：扫描其中的 .md 文件归入"其他"
                    self._collect_from_subdir(full_path, classified)

    def _collect_rectification(
        self, rect_dir: str, classified: dict[str, list[tuple[str, str]]]
    ) -> None:
        """收集 09_整改项/ 目录下的 .md 文件"""
        try:
            for entry in sorted(os.listdir(rect_dir)):
                full_path = os.path.join(rect_dir, entry)
                if os.path.isfile(full_path) and entry.endswith(".md"):
                    classified["rectification"].append((entry, full_path))
        except OSError as e:
            log.warning("扫描整改项目录失败 %s: %s", rect_dir, e)

    def _collect_from_subdir(
        self, subdir: str, classified: dict[str, list[tuple[str, str]]]
    ) -> None:
        """收集普通子目录下的 .md 文件（归入"其他"类）"""
        try:
            for entry in sorted(os.listdir(subdir)):
                full_path = os.path.join(subdir, entry)
                if os.path.isfile(full_path) and entry.endswith(".md"):
                    # 子目录中的文档，若匹配特殊类别仍归入对应类
                    cat = self._classify_document(entry)
                    if cat == "other":
                        # 用相对路径展示，便于区分
                        rel = os.path.relpath(full_path, self._project_path)
                        classified["other"].append((rel, full_path))
                    else:
                        classified[cat].append((entry, full_path))
        except OSError:
            pass

    @staticmethod
    def _classify_document(filename: str) -> str:
        """根据文件名分类文档

        分类规则：
        - PM_SESSION_*.md → pm_session
        - 立项表_*.md → initiation
        - 变更单_*.md 或 CHG-*.md → change
        - 其他 .md → other
        """
        name = filename.lower()
        if filename.startswith("PM_SESSION_") and filename.endswith(".md"):
            return "pm_session"
        if filename.startswith("立项表_") and filename.endswith(".md"):
            return "initiation"
        if (filename.startswith("变更单_") or filename.startswith("CHG-")) and filename.endswith(".md"):
            return "change"
        return "other"

    # ── 模板信息 ──────────────────────────────────────────

    def _load_template_info(self, project_path: str) -> None:
        """加载并显示模板信息（从 .copier-answers.yml 读取）"""
        info = self._read_template_info(project_path)
        template_name = info.get("template", "") or "—"
        commit = info.get("commit", "") or "—"
        last_updated = info.get("last_updated", "") or "—"
        self._template_name_label.setText(f"模板: {template_name}")
        self._template_version_label.setText(f"版本: {commit}")
        self._template_updated_label.setText(f"上次更新: {last_updated}")

    @staticmethod
    def _read_template_info(project_path: str) -> dict[str, Any]:
        """从 .copier-answers.yml 读取模板信息"""
        info: dict[str, Any] = {"template": "", "commit": "", "last_updated": ""}
        answers_path = os.path.join(project_path, ".copier-answers.yml")
        if not os.path.isfile(answers_path):
            return info
        try:
            with open(answers_path, encoding="utf-8") as f:
                answers = yaml.safe_load(f) or {}
        except (OSError, yaml.YAMLError) as e:
            log.warning("读取 .copier-answers.yml 失败: %s", e)
            return info

        src_path = answers.get("_src_path", "")
        info["template"] = os.path.basename(src_path) if src_path else ""
        info["commit"] = str(answers.get("_commit", ""))
        try:
            mtime = os.path.getmtime(answers_path)
            info["last_updated"] = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
        except OSError:
            info["last_updated"] = ""
        return info

    # ── 事件处理 ──────────────────────────────────────────

    def _on_update_template(self) -> None:
        """模板更新按钮 → 调用 TemplateService.update_template()"""
        if not self._project_path:
            log.warning("未加载项目，无法更新模板")
            return
        log.info("文档Tab: 执行模板更新 %s", self._project_path)
        try:
            self._template_service.update_template(self._project_path, overwrite=False)
            self._load_template_info(self._project_path)
            self.template_updated.emit()
        except FileNotFoundError as e:
            log.warning("模板更新失败（缺少 .copier-answers.yml）: %s", e)
        except Exception as e:
            log.error("模板更新失败: %s", e, exc_info=True)

    def _on_check_update(self) -> None:
        """检查更新按钮 → 调用 update_template(dry_run=True) 预览"""
        if not self._project_path:
            log.warning("未加载项目，无法检查更新")
            return
        log.info("文档Tab: 检查模板更新（预览）%s", self._project_path)
        try:
            result = self._template_service.update_template(
                self._project_path, dry_run=True
            )
            info = result.get("info", {})
            log.info("模板预览结果: %s", info)
        except FileNotFoundError as e:
            log.warning("检查更新失败（缺少 .copier-answers.yml）: %s", e)
        except Exception as e:
            log.error("检查更新失败: %s", e, exc_info=True)

    def _on_document_double_clicked(self, item: QTreeWidgetItem) -> None:
        """双击文档 → 用系统默认程序打开"""
        path = item.data(0, _PATH_ROLE)
        if not path:
            # 双击的是分类节点，不处理
            return
        log.info("文档Tab: 打开文档 %s", path)
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    # ── 辅助方法（供测试使用）──────────────────────────────

    def _get_category_items(self) -> list[QTreeWidgetItem]:
        """获取文档树的所有分类节点（顶层节点）"""
        items: list[QTreeWidgetItem] = []
        for i in range(self._doc_tree.topLevelItemCount()):
            items.append(self._doc_tree.topLevelItem(i))
        return items

    def _get_documents_in_category(self, cat_item: QTreeWidgetItem) -> list[QTreeWidgetItem]:
        """获取某分类下的所有文档节点"""
        return [cat_item.child(i) for i in range(cat_item.childCount())]
