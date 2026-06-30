"""GUI 视觉检查专项测试（优化版）

复用 tests/gui/conftest.py 的测试基础设施，避免重复创建项目。
全面遍历所有页面、对话框、交互状态，并在关键点截图用于视觉分析。

截图保存到 test_reports/gui/visual_screenshots/ 目录。
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

if not os.environ.get("GUI_VISIBLE"):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QToolButton,
    QMessageBox,
)
from PySide6.QtTest import QTest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SCREENSHOT_DIR = PROJECT_ROOT / "test_reports" / "gui" / "visual_screenshots"

VIEWPORTS = {
    "desktop": QSize(1280, 800),
    "tablet": QSize(768, 1024),
    "mobile": QSize(375, 812),
}


@pytest.fixture(scope="session")
def screenshot_dir() -> Path:
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    return SCREENSHOT_DIR


def take_screenshot(widget, screenshot_dir: Path, name: str) -> str:
    path = screenshot_dir / f"{name}.png"
    widget.grab().save(str(path))
    return str(path)


def resize_window(window, size: QSize) -> None:
    window.resize(size)
    QApplication.processEvents()
    QTest.qWait(300)


def find_dialog(app: QApplication, title_contains: str, timeout_ms: int = 2000) -> QDialog | None:
    import time

    deadline = time.time() + timeout_ms / 1000
    while time.time() < deadline:
        for w in app.topLevelWidgets():
            if isinstance(w, QDialog) and w.isVisible() and title_contains in w.windowTitle():
                return w
        app.processEvents()
        QTest.qWait(50)
    return None


def close_all_dialogs(app: QApplication) -> None:
    for w in app.topLevelWidgets():
        if isinstance(w, QDialog) and w.isVisible():
            w.reject()
    app.processEvents()
    QTest.qWait(200)


def close_all_message_boxes(app: QApplication) -> None:
    for w in app.topLevelWidgets():
        if isinstance(w, QMessageBox) and w.isVisible():
            w.accept()
    app.processEvents()
    QTest.qWait(200)


# ══════════════════════════════════════════════════════════
# 1. 首屏与项目列表页
# ══════════════════════════════════════════════════════════

class TestSplashAndProjectList:
    """首屏加载与项目列表页视觉检查"""

    def test_01_first_load_desktop(self, qapp, main_window, screenshot_dir):
        """首屏加载完成 - 桌面尺寸"""
        resize_window(main_window, VIEWPORTS["desktop"])
        take_screenshot(main_window, screenshot_dir, "01_01_first_load_desktop")

    def test_02_first_load_tablet(self, qapp, main_window, screenshot_dir):
        """首屏加载完成 - 平板尺寸"""
        resize_window(main_window, VIEWPORTS["tablet"])
        take_screenshot(main_window, screenshot_dir, "01_02_first_load_tablet")

    def test_03_first_load_mobile(self, qapp, main_window, screenshot_dir):
        """首屏加载完成 - 手机尺寸"""
        resize_window(main_window, VIEWPORTS["mobile"])
        take_screenshot(main_window, screenshot_dir, "01_03_first_load_mobile")
        resize_window(main_window, VIEWPORTS["desktop"])

    def test_04_card_view(self, qapp, main_window, screenshot_dir):
        """项目列表 - 卡片视图"""
        vc = main_window._project_list_view._view_controls
        vc._card_btn.click()
        qapp.processEvents()
        QTest.qWait(200)
        take_screenshot(main_window, screenshot_dir, "02_01_project_list_card_view")

    def test_05_list_view(self, qapp, main_window, screenshot_dir):
        """项目列表 - 表格视图"""
        vc = main_window._project_list_view._view_controls
        vc._list_btn.click()
        qapp.processEvents()
        QTest.qWait(200)
        take_screenshot(main_window, screenshot_dir, "02_02_project_list_table_view")

    def test_06_search_with_text(self, qapp, main_window, screenshot_dir):
        """搜索框输入文字"""
        main_window._search_edit.setText("DJ-2026")
        qapp.processEvents()
        QTest.qWait(300)
        take_screenshot(main_window, screenshot_dir, "02_03_search_with_text")
        main_window._search_edit.clear()
        qapp.processEvents()

    def test_07_empty_search(self, qapp, main_window, screenshot_dir):
        """搜索无结果 - 空状态"""
        main_window._search_edit.setText("ZZZZZ不存在的项目")
        qapp.processEvents()
        QTest.qWait(300)
        take_screenshot(main_window, screenshot_dir, "02_04_empty_search")
        main_window._search_edit.clear()
        qapp.processEvents()

    def test_08_loading_state(self, qapp, main_window, screenshot_dir):
        """加载状态"""
        main_window._project_list_view.set_loading()
        qapp.processEvents()
        QTest.qWait(100)
        take_screenshot(main_window, screenshot_dir, "02_05_loading_state")
        main_window._on_refresh()
        qapp.processEvents()
        QTest.qWait(500)

    def test_09_error_state(self, qapp, main_window, screenshot_dir):
        """错误状态"""
        main_window._project_list_view.set_error("模拟错误：无法连接到项目数据库，请检查工作空间配置。")
        qapp.processEvents()
        QTest.qWait(100)
        take_screenshot(main_window, screenshot_dir, "02_06_error_state")
        main_window._on_refresh()
        qapp.processEvents()
        QTest.qWait(500)

    def test_10_navigation_expanded(self, qapp, main_window, screenshot_dir):
        """左侧导航树展开状态"""
        nav = main_window._nav_tree
        for i in range(nav.topLevelItemCount()):
            item = nav.topLevelItem(i)
            nav.expandItem(item)
        qapp.processEvents()
        QTest.qWait(200)
        take_screenshot(main_window, screenshot_dir, "02_07_navigation_expanded")

    def test_11_nav_collapsed(self, qapp, main_window, screenshot_dir):
        """导航栏收起"""
        main_window._splitter.setSizes([50, 1000])
        qapp.processEvents()
        QTest.qWait(200)
        take_screenshot(main_window, screenshot_dir, "02_08_nav_collapsed")
        main_window._splitter.setSizes([200, 1000])
        qapp.processEvents()


# ══════════════════════════════════════════════════════════
# 2. 项目工作区 - 5 个 Tab
# ══════════════════════════════════════════════════════════

class TestWorkspaceTabs:
    """项目工作区各 Tab 视觉检查"""

    TEST_PROJECT_ID = "DJ-2026-998"

    @pytest.fixture(autouse=True)
    def setup(self, qapp, main_window):
        main_window._on_project_selected(self.TEST_PROJECT_ID)
        qapp.processEvents()
        QTest.qWait(500)
        yield
        try:
            main_window._on_back_to_list()
            qapp.processEvents()
            QTest.qWait(300)
        except Exception:
            pass

    def test_01_overview_tab(self, qapp, main_window, screenshot_dir):
        """工作区 - 概览 Tab"""
        wv = main_window._workspace_view
        idx = wv._tab_indices.get("overview", 0)
        wv._tab_widget.setCurrentIndex(idx)
        qapp.processEvents()
        QTest.qWait(300)
        take_screenshot(main_window, screenshot_dir, "03_01_workspace_overview")

    def test_02_change_tab(self, qapp, main_window, screenshot_dir):
        """工作区 - 变更 Tab"""
        wv = main_window._workspace_view
        idx = wv._tab_indices.get("change", 1)
        wv._tab_widget.setCurrentIndex(idx)
        qapp.processEvents()
        QTest.qWait(300)
        take_screenshot(main_window, screenshot_dir, "03_02_workspace_change")

    def test_03_check_tab(self, qapp, main_window, screenshot_dir):
        """工作区 - 检查 Tab"""
        wv = main_window._workspace_view
        idx = wv._tab_indices.get("check", 2)
        wv._tab_widget.setCurrentIndex(idx)
        qapp.processEvents()
        QTest.qWait(800)
        take_screenshot(main_window, screenshot_dir, "03_03_workspace_check")

    def test_04_doc_tab(self, qapp, main_window, screenshot_dir):
        """工作区 - 文档 Tab"""
        wv = main_window._workspace_view
        idx = wv._tab_indices.get("doc", 3)
        wv._tab_widget.setCurrentIndex(idx)
        qapp.processEvents()
        QTest.qWait(300)
        take_screenshot(main_window, screenshot_dir, "03_04_workspace_doc")

    def test_05_vartable_tab(self, qapp, main_window, screenshot_dir):
        """工作区 - 变量表 Tab"""
        wv = main_window._workspace_view
        idx = wv._tab_indices.get("vartable", 4)
        if idx >= 0:
            wv._tab_widget.setCurrentIndex(idx)
            qapp.processEvents()
            QTest.qWait(500)
            take_screenshot(main_window, screenshot_dir, "03_05_workspace_vartable")

    def test_06_responsive_tablet(self, qapp, main_window, screenshot_dir):
        """工作区响应式 - 平板"""
        resize_window(main_window, VIEWPORTS["tablet"])
        take_screenshot(main_window, screenshot_dir, "03_06_workspace_tablet")
        resize_window(main_window, VIEWPORTS["desktop"])

    def test_07_responsive_mobile(self, qapp, main_window, screenshot_dir):
        """工作区响应式 - 手机"""
        resize_window(main_window, VIEWPORTS["mobile"])
        take_screenshot(main_window, screenshot_dir, "03_07_workspace_mobile")
        resize_window(main_window, VIEWPORTS["desktop"])


# ══════════════════════════════════════════════════════════
# 3. 全局页面
# ══════════════════════════════════════════════════════════

class TestGlobalPages:
    """全局功能页面视觉检查"""

    def test_01_change_center(self, qapp, main_window, screenshot_dir):
        """变更中心页"""
        main_window._on_page_switch("change_center")
        qapp.processEvents()
        QTest.qWait(500)
        take_screenshot(main_window, screenshot_dir, "04_01_global_change_center")

    def test_02_spec_center(self, qapp, main_window, screenshot_dir):
        """规范中心页"""
        main_window._on_page_switch("spec_center")
        qapp.processEvents()
        QTest.qWait(500)
        take_screenshot(main_window, screenshot_dir, "04_02_global_spec_center")

    def test_03_report_page(self, qapp, main_window, screenshot_dir):
        """报告中心页"""
        main_window._on_page_switch("report")
        qapp.processEvents()
        QTest.qWait(300)
        take_screenshot(main_window, screenshot_dir, "04_03_global_report")

    def test_04_template_page(self, qapp, main_window, screenshot_dir):
        """模板管理页"""
        main_window._on_page_switch("template")
        qapp.processEvents()
        QTest.qWait(300)
        take_screenshot(main_window, screenshot_dir, "04_04_global_template")

    def test_05_settings_page(self, qapp, main_window, screenshot_dir):
        """系统设置页"""
        main_window._on_page_switch("settings")
        qapp.processEvents()
        QTest.qWait(300)
        take_screenshot(main_window, screenshot_dir, "04_05_global_settings")

    def test_06_back_to_list(self, qapp, main_window, screenshot_dir):
        """返回项目列表"""
        main_window._on_page_switch("all_projects")
        qapp.processEvents()
        QTest.qWait(300)
        take_screenshot(main_window, screenshot_dir, "04_06_back_to_list")


# ══════════════════════════════════════════════════════════
# 4. 规范中心各 Tab
# ══════════════════════════════════════════════════════════

class TestSpecCenterTabs:
    """规范中心各 Tab 视觉检查"""

    @pytest.fixture(autouse=True)
    def setup(self, qapp, main_window):
        main_window._on_page_switch("spec_center")
        qapp.processEvents()
        QTest.qWait(300)
        yield
        main_window._on_page_switch("all_projects")
        qapp.processEvents()

    def test_01_overview_tab(self, qapp, main_window, screenshot_dir):
        """规范中心 - 概览 Tab"""
        sc = main_window._spec_center_view
        if hasattr(sc, "_tab_widget") and sc._tab_widget.count() > 0:
            sc._tab_widget.setCurrentIndex(0)
            qapp.processEvents()
            QTest.qWait(300)
            take_screenshot(main_window, screenshot_dir, "05_01_spec_overview")

    def test_02_check_tab(self, qapp, main_window, screenshot_dir):
        """规范中心 - 检查 Tab"""
        sc = main_window._spec_center_view
        if hasattr(sc, "_tab_widget") and sc._tab_widget.count() > 1:
            sc._tab_widget.setCurrentIndex(1)
            qapp.processEvents()
            QTest.qWait(300)
            take_screenshot(main_window, screenshot_dir, "05_02_spec_check")

    def test_03_index_tab(self, qapp, main_window, screenshot_dir):
        """规范中心 - 索引 Tab"""
        sc = main_window._spec_center_view
        if hasattr(sc, "_tab_widget") and sc._tab_widget.count() > 2:
            sc._tab_widget.setCurrentIndex(2)
            qapp.processEvents()
            QTest.qWait(300)
            take_screenshot(main_window, screenshot_dir, "05_03_spec_index")

    def test_04_frontmatter_tab(self, qapp, main_window, screenshot_dir):
        """规范中心 - Frontmatter Tab"""
        sc = main_window._spec_center_view
        if hasattr(sc, "_tab_widget") and sc._tab_widget.count() > 3:
            sc._tab_widget.setCurrentIndex(3)
            qapp.processEvents()
            QTest.qWait(300)
            take_screenshot(main_window, screenshot_dir, "05_04_spec_frontmatter")

    def test_05_compare_tab(self, qapp, main_window, screenshot_dir):
        """规范中心 - 对比 Tab"""
        sc = main_window._spec_center_view
        if hasattr(sc, "_tab_widget") and sc._tab_widget.count() > 4:
            sc._tab_widget.setCurrentIndex(4)
            qapp.processEvents()
            QTest.qWait(300)
            take_screenshot(main_window, screenshot_dir, "05_05_spec_compare")

    def test_06_report_tab(self, qapp, main_window, screenshot_dir):
        """规范中心 - 报告 Tab"""
        sc = main_window._spec_center_view
        if hasattr(sc, "_tab_widget") and sc._tab_widget.count() > 5:
            sc._tab_widget.setCurrentIndex(5)
            qapp.processEvents()
            QTest.qWait(300)
            take_screenshot(main_window, screenshot_dir, "05_06_spec_report")


# ══════════════════════════════════════════════════════════
# 5. 对话框视觉检查
# ══════════════════════════════════════════════════════════

class TestDialogs:
    """各对话框视觉检查（使用 QTimer.singleShot 处理模态对话框）"""

    TEST_PROJECT_ID = "DJ-2026-998"

    def test_01_new_project_dialog(self, qapp, main_window, screenshot_dir):
        """新建项目对话框"""
        found: list[bool] = []

        def _screenshot_and_close() -> None:
            dlg = find_dialog(qapp, "新建项目")
            if dlg:
                take_screenshot(dlg, screenshot_dir, "06_01_dialog_new_project")
                found.append(True)
                dlg.reject()
                qapp.processEvents()

        QTimer.singleShot(500, _screenshot_and_close)
        main_window._on_new_project("plc")
        close_all_dialogs(qapp)

    def test_02_edit_project_dialog(self, qapp, main_window, screenshot_dir):
        """编辑项目对话框"""
        found: list[bool] = []

        def _screenshot_and_close() -> None:
            dlg = find_dialog(qapp, "编辑项目")
            if dlg:
                take_screenshot(dlg, screenshot_dir, "06_02_dialog_edit_project")
                found.append(True)
                dlg.reject()
                qapp.processEvents()

        QTimer.singleShot(500, _screenshot_and_close)
        main_window._on_edit_project(self.TEST_PROJECT_ID)
        close_all_dialogs(qapp)

    def test_03_create_change_wizard_page1(self, qapp, main_window, screenshot_dir):
        """创建变更单向导 - 第1页"""
        found: list[bool] = []

        def _screenshot_and_close() -> None:
            dlg = find_dialog(qapp, "新建变更单")
            if dlg:
                take_screenshot(dlg, screenshot_dir, "06_03_dialog_create_change_p1")
                found.append(True)
                dlg.reject()
                qapp.processEvents()

        QTimer.singleShot(500, _screenshot_and_close)
        main_window._on_new_change()
        close_all_dialogs(qapp)

    def test_04_sync_warning_message(self, qapp, main_window, screenshot_dir):
        """同步缓存提示（DB 未连接时）"""
        found: list[bool] = []

        def _screenshot_and_close() -> None:
            for w in qapp.topLevelWidgets():
                if isinstance(w, QMessageBox) and w.isVisible():
                    take_screenshot(w, screenshot_dir, "06_04_msg_sync_warning")
                    found.append(True)
                    w.accept()
                    qapp.processEvents()
                    break

        QTimer.singleShot(300, _screenshot_and_close)
        main_window._on_sync()
        close_all_message_boxes(qapp)

    @pytest.mark.skip(reason="删除确认对话框交互复杂，offscreen 模式容易超时")
    def test_05_delete_project_dialog(self, qapp, main_window, screenshot_dir):
        """删除项目确认对话框"""
        pass

    @pytest.mark.skip(reason="导入项目会打开原生文件选择器，offscreen 模式超时")
    def test_06_import_project_dialog(self, qapp, main_window, screenshot_dir):
        """导入项目对话框"""
        pass


# ══════════════════════════════════════════════════════════
# 6. 状态栏与工具栏
# ══════════════════════════════════════════════════════════

class TestToolbarAndStatusbar:
    """工具栏与状态栏视觉检查"""

    def test_01_status_bar_info(self, qapp, main_window, screenshot_dir):
        """状态栏信息"""
        take_screenshot(main_window, screenshot_dir, "07_01_status_bar")

    def test_02_toolbar_new_menu(self, qapp, main_window, screenshot_dir):
        """工具栏新建下拉菜单"""
        new_btn = None
        for child in main_window.children():
            if isinstance(child, QToolButton) and child.text() == "新建":
                new_btn = child
                break
        if new_btn:
            new_btn.showMenu()
            qapp.processEvents()
            QTest.qWait(200)
            take_screenshot(main_window, screenshot_dir, "07_02_toolbar_new_menu")
            new_btn.menu().close()
            qapp.processEvents()

    def test_03_business_line_combo(self, qapp, main_window, screenshot_dir):
        """业务线筛选下拉"""
        main_window._business_combo.showPopup()
        qapp.processEvents()
        QTest.qWait(200)
        take_screenshot(main_window, screenshot_dir, "07_03_business_line_combo")
        main_window._business_combo.hidePopup()
        qapp.processEvents()
