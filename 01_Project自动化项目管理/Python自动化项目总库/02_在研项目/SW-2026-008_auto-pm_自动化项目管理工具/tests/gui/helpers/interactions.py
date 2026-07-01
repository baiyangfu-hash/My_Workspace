"""GUI 交互库

封装常见的 GUI 操作，减少测试代码重复。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QMenu,
    QMessageBox,
)

if TYPE_CHECKING:
    from auto_pm.ui.main_window import MainWindow


def click_nav_page(window: MainWindow, page_id: str, app: QApplication) -> None:
    """通过导航树切换页面"""
    window._on_page_switch(page_id)
    app.processEvents()
    QTest.qWait(200)


def click_nav_filter(window: MainWindow, stack: str, phase: str, app: QApplication) -> None:
    """通过导航树筛选项目"""
    window._nav_tree.project_filter_requested.emit(stack, phase)
    app.processEvents()
    QTest.qWait(200)


def search_projects(window: MainWindow, text: str, app: QApplication) -> None:
    """搜索项目"""
    window._search_edit.setText(text)
    app.processEvents()
    QTest.qWait(300)


def clear_search(window: MainWindow, app: QApplication) -> None:
    """清空搜索"""
    window._search_edit.clear()
    app.processEvents()
    QTest.qWait(200)


def switch_view_mode(window: MainWindow, mode: str, app: QApplication) -> None:
    """切换视图模式（card / list）"""
    vc = window._project_list_view._view_controls
    if mode == "card":
        vc._card_btn.click()
    else:
        vc._list_btn.click()
    app.processEvents()
    QTest.qWait(200)


def switch_group_mode(window: MainWindow, mode_text: str, app: QApplication) -> None:
    """切换分组模式"""
    vc = window._project_list_view._view_controls
    combo = vc._group_combo
    idx = combo.findText(mode_text)
    if idx >= 0:
        combo.setCurrentIndex(idx)
    app.processEvents()
    QTest.qWait(200)


def enter_workspace(window: MainWindow, project_id: str, app: QApplication) -> None:
    """进入项目工作区"""
    window._on_project_selected(project_id)
    app.processEvents()
    QTest.qWait(500)


def back_to_list(window: MainWindow, app: QApplication) -> None:
    """返回项目列表"""
    window._on_back_to_list()
    app.processEvents()
    QTest.qWait(300)


def switch_workspace_tab(window: MainWindow, tab_id: str, app: QApplication) -> None:
    """切换工作区 Tab"""
    wv = window._workspace_view
    idx = wv._tab_indices.get(tab_id, -1)
    assert idx >= 0, f"Tab '{tab_id}' 不存在"
    wv._tab_widget.setCurrentIndex(idx)
    app.processEvents()
    QTest.qWait(300)


def find_dialog(app: QApplication, title_contains: str, timeout_ms: int = 2000) -> QDialog | None:
    """查找已弹出的对话框（包括有 parent 的嵌套对话框）

    TransitionDialog/NewProjectDialog/CreateChangeDialog 都有 parent（非 top-level），
    app.topLevelWidgets() 找不到它们，必须用 findChildren 递归查找。

    Args:
        timeout_ms: 超时毫秒数。0 表示只检查一次立即返回（用于 singleShot 回调中
                    对话框已弹出的场景，避免阻塞）。
    """
    import time

    deadline = time.time() + timeout_ms / 1000
    while True:
        for top in app.topLevelWidgets():
            if isinstance(top, QDialog) and top.isVisible() and title_contains in top.windowTitle():
                return top
            for dlg in top.findChildren(QDialog):
                if dlg.isVisible() and title_contains in dlg.windowTitle():
                    return dlg
        if time.time() >= deadline:
            return None
        app.processEvents()
        QTest.qWait(50)


def find_message_box(app: QApplication) -> QMessageBox | None:
    """查找可见的 QMessageBox（包括有 parent 的）"""
    for top in app.topLevelWidgets():
        if isinstance(top, QMessageBox) and top.isVisible():
            return top
        for mb in top.findChildren(QMessageBox):
            if mb.isVisible():
                return mb
    return None


def accept_dialog(dialog: QDialog, app: QApplication) -> None:
    """点击对话框的 OK/确定按钮"""
    ok_btn = dialog._button_box.button(QDialogButtonBox.StandardButton.Ok)  # type: ignore[attr-defined]
    ok_btn.click()
    app.processEvents()
    QTest.qWait(500)


def reject_dialog(dialog: QDialog, app: QApplication) -> None:
    """点击对话框的 Cancel/取消按钮"""
    cancel_btn = dialog._button_box.button(QDialogButtonBox.StandardButton.Cancel)  # type: ignore[attr-defined]
    cancel_btn.click()
    app.processEvents()
    QTest.qWait(300)


def dismiss_message_boxes(app: QApplication) -> list[str]:
    """关闭所有 QMessageBox，返回弹窗文本列表

    循环关闭嵌套 QMessageBox（最多 5 个），每个关闭后 processEvents 让后续弹出。
    """
    texts: list[str] = []
    for _ in range(5):
        mb = find_message_box(app)
        if mb is None:
            break
        texts.append(mb.text())
        mb.accept()
        app.processEvents()
        QTest.qWait(200)
    return texts


def close_all_modal_widgets(app: QApplication) -> None:
    """关闭所有可见的 QMenu/QMessageBox/QDialog，防止残留弹窗阻塞测试

    在 singleShot 回调找不到目标对话框、或流转/创建失败时调用，
    确保不会有遗留的模态对话框阻塞后续测试步骤。
    """
    # 1. 关闭所有 QMessageBox
    dismiss_message_boxes(app)
    # 2. 关闭所有可见的 QMenu（多目标流转时弹出）
    for top in app.topLevelWidgets():
        for menu in top.findChildren(QMenu):
            if menu.isVisible():
                menu.close()
                app.processEvents()
                QTest.qWait(100)
    # 3. reject 所有可见的 QDialog（先关子对话框再关父对话框）
    for _ in range(3):
        closed_any = False
        for top in app.topLevelWidgets():
            if isinstance(top, QDialog) and top.isVisible():
                top.reject()
                closed_any = True
                app.processEvents()
                QTest.qWait(100)
            for dlg in top.findChildren(QDialog):
                if dlg.isVisible():
                    dlg.reject()
                    closed_any = True
                    app.processEvents()
                    QTest.qWait(100)
        if not closed_any:
            break
        dismiss_message_boxes(app)  # reject 可能触发新的 QMessageBox


def refresh_list(window: MainWindow, app: QApplication) -> None:
    """刷新项目列表"""
    window._on_refresh()
    app.processEvents()
    QTest.qWait(800)


def sync_cache(window: MainWindow, app: QApplication) -> None:
    """同步缓存"""
    window._on_sync()
    app.processEvents()
    QTest.qWait(800)


from PySide6.QtTest import QTest  # noqa: E402
