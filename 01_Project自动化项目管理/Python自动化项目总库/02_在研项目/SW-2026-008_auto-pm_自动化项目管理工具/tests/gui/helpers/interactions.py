"""GUI 交互库

封装常见的 GUI 操作，减少测试代码重复。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QMessageBox,
    QWidget,
)

if TYPE_CHECKING:
    pass


def click_nav_page(window: QWidget, page_id: str, app: QApplication) -> None:
    """通过导航树切换页面"""
    window._on_page_switch(page_id)
    app.processEvents()
    QTest.qWait(200)


def click_nav_filter(window: QWidget, stack: str, phase: str, app: QApplication) -> None:
    """通过导航树筛选项目"""
    window._nav_tree.project_filter_requested.emit(stack, phase)
    app.processEvents()
    QTest.qWait(200)


def search_projects(window: QWidget, text: str, app: QApplication) -> None:
    """搜索项目"""
    window._search_edit.setText(text)
    app.processEvents()
    QTest.qWait(300)


def clear_search(window: QWidget, app: QApplication) -> None:
    """清空搜索"""
    window._search_edit.clear()
    app.processEvents()
    QTest.qWait(200)


def switch_view_mode(window: QWidget, mode: str, app: QApplication) -> None:
    """切换视图模式（card / list）"""
    vc = window._project_list_view._view_controls
    if mode == "card":
        vc._card_btn.click()
    else:
        vc._list_btn.click()
    app.processEvents()
    QTest.qWait(200)


def switch_group_mode(window: QWidget, mode_text: str, app: QApplication) -> None:
    """切换分组模式"""
    vc = window._project_list_view._view_controls
    combo = vc._group_combo
    idx = combo.findText(mode_text)
    if idx >= 0:
        combo.setCurrentIndex(idx)
    app.processEvents()
    QTest.qWait(200)


def enter_workspace(window: QWidget, project_id: str, app: QApplication) -> None:
    """进入项目工作区"""
    window._on_project_selected(project_id)
    app.processEvents()
    QTest.qWait(500)


def back_to_list(window: QWidget, app: QApplication) -> None:
    """返回项目列表"""
    window._on_back_to_list()
    app.processEvents()
    QTest.qWait(300)


def switch_workspace_tab(window: QWidget, tab_id: str, app: QApplication) -> None:
    """切换工作区 Tab"""
    wv = window._workspace_view
    idx = wv._tab_indices.get(tab_id, -1)
    assert idx >= 0, f"Tab '{tab_id}' 不存在"
    wv._tab_widget.setCurrentIndex(idx)
    app.processEvents()
    QTest.qWait(300)


def find_dialog(app: QApplication, title_contains: str, timeout_ms: int = 2000) -> QDialog | None:
    """查找已弹出的对话框"""
    import time

    deadline = time.time() + timeout_ms / 1000
    while time.time() < deadline:
        for w in app.topLevelWidgets():
            if isinstance(w, QDialog) and w.isVisible() and title_contains in w.windowTitle():
                return w
        app.processEvents()
        QTest.qWait(50)
    return None


def accept_dialog(dialog: QDialog, app: QApplication) -> None:
    """点击对话框的 OK/确定按钮"""
    ok_btn = dialog._button_box.button(QDialogButtonBox.StandardButton.Ok)
    ok_btn.click()
    app.processEvents()
    QTest.qWait(500)


def reject_dialog(dialog: QDialog, app: QApplication) -> None:
    """点击对话框的 Cancel/取消按钮"""
    cancel_btn = dialog._button_box.button(QDialogButtonBox.StandardButton.Cancel)
    cancel_btn.click()
    app.processEvents()
    QTest.qWait(300)


def dismiss_message_boxes(app: QApplication) -> list[str]:
    """关闭所有 QMessageBox，返回弹窗文本列表"""
    texts: list[str] = []
    for w in app.topLevelWidgets():
        if isinstance(w, QMessageBox) and w.isVisible():
            texts.append(w.text())
            w.accept()
    app.processEvents()
    QTest.qWait(200)
    return texts


def refresh_list(window: QWidget, app: QApplication) -> None:
    """刷新项目列表"""
    window._on_refresh()
    app.processEvents()
    QTest.qWait(800)


def sync_cache(window: QWidget, app: QApplication) -> None:
    """同步缓存"""
    window._on_sync()
    app.processEvents()
    QTest.qWait(800)


from PySide6.QtTest import QTest  # noqa: E402
