"""GUI 断言库

提供针对 auto-pm GUI 控件的断言函数，断言失败时抛出 AssertionError 并附带可读信息。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QDialog, QPushButton, QWidget

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication


def assert_window_title(window: QWidget, expected: str) -> None:
    """验证窗口标题"""
    actual = window.windowTitle()
    assert actual == expected, f"窗口标题预期 '{expected}'，实际 '{actual}'"


def assert_stack_index(window: QWidget, expected: int) -> None:
    """验证中央页面栈索引"""
    actual = window._stack.currentIndex()
    assert actual == expected, f"页面栈索引预期 {expected}，实际 {actual}"


def assert_project_count(window: QWidget, expected: int) -> None:
    """验证项目列表项目数"""
    actual = len(window._project_list_view._filtered_projects)
    assert actual == expected, f"项目数预期 {expected}，实际 {actual}"


def assert_project_in_list(window: QWidget, project_id: str) -> None:
    """验证项目在列表中"""
    proj = window._project_list_view.get_project(project_id)
    assert proj is not None, f"项目 {project_id} 不在列表中"


def assert_project_not_in_list(window: QWidget, project_id: str) -> None:
    """验证项目不在列表中"""
    proj = window._project_list_view.get_project(project_id)
    assert proj is None, f"项目 {project_id} 仍在列表中（应已删除）"


def assert_statusbar_contains(window: QWidget, key: str, expected: str) -> None:
    """验证状态栏文本包含指定内容"""
    status_map = {
        "workspace": window._status_workspace,
        "project": window._status_project,
        "change": window._status_change,
        "db": window._status_db,
        "scan": window._status_scan,
    }
    label = status_map.get(key)
    assert label is not None, f"状态栏 key '{key}' 不存在"
    actual = label.text()
    assert expected in actual, f"状态栏 {key} 预期含 '{expected}'，实际 '{actual}'"


def assert_dialog_open(app: "QApplication", title_contains: str) -> QDialog:
    """验证对话框已弹出并返回，未找到则断言失败"""
    for _ in range(20):  # 最多等待 1 秒
        for w in app.topLevelWidgets():
            if isinstance(w, QDialog) and w.isVisible() and title_contains in w.windowTitle():
                return w
        app.processEvents()
        QTest.qWait(50)
    assert False, f"对话框 '{title_contains}' 未弹出"


def assert_no_error_dialog(app: "QApplication") -> None:
    """验证当前无错误弹窗（QMessageBox）"""
    from PySide6.QtWidgets import QMessageBox

    for w in app.topLevelWidgets():
        if isinstance(w, QMessageBox) and w.isVisible():
            text = w.text()
            w.accept()
            assert False, f"出现错误弹窗: {text}"


def assert_change_card_count(change_tab: QWidget, expected: int) -> None:
    """验证变更 Tab 卡片数量"""
    cards = change_tab._get_cards()
    actual = len(cards)
    assert actual == expected, f"变更卡片数预期 {expected}，实际 {actual}"


def assert_check_summary_contains(check_tab: QWidget, *keywords: str) -> None:
    """验证检查 Tab 摘要栏包含关键词"""
    summary = check_tab._summary_label.text()
    for kw in keywords:
        assert kw in summary, f"检查摘要预期含 '{kw}'，实际 '{summary}'"


def assert_doc_categories_count(doc_tab: QWidget, expected: int) -> None:
    """验证文档 Tab 分类节点数"""
    cats = doc_tab._get_category_items()
    actual = len(cats)
    assert actual == expected, f"文档分类数预期 {expected}，实际 {actual}"


def assert_report_cards_visible(report_page: QWidget) -> None:
    """验证报告中心 4 个卡片可见"""
    assert report_page._project_card is not None
    assert report_page._phase_card is not None
    assert report_page._bl_card is not None
    assert report_page._change_card is not None


def assert_settings_loaded(settings_page: QWidget) -> None:
    """验证系统设置页已加载信息"""
    assert settings_page.workspace_edit.text(), "工作空间路径为空"
    assert settings_page.db_path_label.text(), "DB 路径为空"


# 延迟导入 QTest
from PySide6.QtTest import QTest  # noqa: E402
