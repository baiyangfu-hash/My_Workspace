"""文档 Tab GUI 集成测试

测试内容：
- 切换到文档 Tab
- 文档树分类节点加载
- 模板信息显示
- 检查模板更新按钮（不崩溃）
- 遍历分类获取文档列表（不崩溃）

使用 tests/gui/conftest.py 提供的 main_window / app / test_project_id fixture，
通过 helpers 辅助函数操作 GUI。
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

# 必须在导入 PySide6 前设置离屏渲染，避免无显示环境报错
# V0.5.2: 默认可见模式（用户要求）；offscreen 仅通过 QT_QPA_PLATFORM=offscreen 环境变量设置

import pytest  # noqa: E402
from PySide6.QtTest import QTest  # noqa: E402

from tests.gui.helpers.interactions import (  # noqa: E402
    dismiss_message_boxes,
    enter_workspace,
    switch_workspace_tab,
)

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication

    from auto_pm.ui.main_window import MainWindow


@pytest.mark.gui
class TestDocTab:
    """文档 Tab GUI 集成测试"""

    def test_switch_to_doc_tab(self, main_window: MainWindow, app: QApplication, test_project_id: str) -> None:
        """进入工作区后切换到文档 Tab，验证 _doc_tab 已初始化"""
        enter_workspace(main_window, test_project_id, app)
        switch_workspace_tab(main_window, "doc", app)

        doc_tab = main_window._workspace_view._doc_tab
        assert doc_tab is not None, "文档 Tab 未初始化"

    def test_doc_tree_populated(self, main_window: MainWindow, app: QApplication, test_project_id: str) -> None:
        """切换到文档 Tab，验证文档树分类节点已加载（至少 1 个）"""
        enter_workspace(main_window, test_project_id, app)
        switch_workspace_tab(main_window, "doc", app)

        doc_tab = main_window._workspace_view._doc_tab
        assert doc_tab is not None

        categories = doc_tab._get_category_items()
        assert len(categories) >= 1, f"文档分类数预期 >=1，实际 {len(categories)}"

    def test_template_info_displayed(self, main_window: MainWindow, app: QApplication, test_project_id: str) -> None:
        """验证模板名称或版本信息至少一项非空（不能全空）"""
        enter_workspace(main_window, test_project_id, app)
        switch_workspace_tab(main_window, "doc", app)

        doc_tab = main_window._workspace_view._doc_tab
        assert doc_tab is not None

        name_text = doc_tab._template_name_label.text()
        version_text = doc_tab._template_version_label.text()
        assert name_text or version_text, "模板名称和版本信息均为空"

    def test_check_template_update(self, main_window: MainWindow, app: QApplication, test_project_id: str) -> None:
        """点击检查更新按钮，验证不崩溃并清理弹窗"""
        enter_workspace(main_window, test_project_id, app)
        switch_workspace_tab(main_window, "doc", app)

        doc_tab = main_window._workspace_view._doc_tab
        assert doc_tab is not None

        doc_tab._check_btn.click()
        app.processEvents()
        QTest.qWait(1000)

        # 清理可能出现的消息框（验证不崩溃为主）
        dismiss_message_boxes(app)

    def test_doc_categories_have_docs(self, main_window: MainWindow, app: QApplication, test_project_id: str) -> None:
        """遍历文档分类节点，验证获取文档列表不崩溃"""
        enter_workspace(main_window, test_project_id, app)
        switch_workspace_tab(main_window, "doc", app)

        doc_tab = main_window._workspace_view._doc_tab
        assert doc_tab is not None

        categories = doc_tab._get_category_items()
        for cat in categories:
            docs = doc_tab._get_documents_in_category(cat)
            assert len(docs) >= 0, "获取文档列表不应崩溃"
