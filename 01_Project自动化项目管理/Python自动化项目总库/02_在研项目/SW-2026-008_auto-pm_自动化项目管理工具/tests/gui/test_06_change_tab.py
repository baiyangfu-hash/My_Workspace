"""变更 Tab GUI 测试

覆盖变更 Tab 切换、创建变更单对话框、创建变更单完整流程、状态/领域筛选等交互。
涉及模态对话框（dialog.exec()）的用例通过 QTimer.singleShot 调度对话框操作。
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QComboBox

from tests.gui.helpers.interactions import (
    dismiss_message_boxes,
    enter_workspace,
    find_dialog,
    reject_dialog,
    switch_workspace_tab,
)

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication

    from auto_pm.ui.main_window import MainWindow


def set_combo_by_data(combo: QComboBox, data_value: str) -> None:
    """通过 data 值设置 ComboBox 选中项"""
    for i in range(combo.count()):
        if combo.itemData(i) == data_value:
            combo.setCurrentIndex(i)
            return
    raise ValueError(f"未找到 data={data_value}")


@pytest.mark.gui
def test_switch_to_change_tab(main_window: MainWindow, app: QApplication, test_project_id: str) -> None:
    """测试进入工作区后能切换到变更 Tab 且 ChangeTab 实例已初始化"""
    enter_workspace(main_window, test_project_id, app)
    switch_workspace_tab(main_window, "change", app)
    assert main_window._workspace_view._change_tab is not None


@pytest.mark.gui
def test_create_change_dialog_open(main_window: MainWindow, app: QApplication, test_project_id: str) -> None:
    """测试点击创建变更单按钮能弹出创建变更单对话框"""
    enter_workspace(main_window, test_project_id, app)
    switch_workspace_tab(main_window, "change", app)
    change_tab = main_window._workspace_view._change_tab
    assert change_tab is not None

    found: list[object] = []

    def _verify_and_close() -> None:
        dlg = find_dialog(app, "创建变更单")
        assert dlg is not None, "创建变更单对话框未弹出"
        found.append(dlg)
        reject_dialog(dlg, app)

    QTimer.singleShot(100, _verify_and_close)
    change_tab._on_create_change()

    assert len(found) == 1, "创建变更单对话框未弹出"


@pytest.mark.gui
def test_create_change_full_flow(main_window: MainWindow, app: QApplication, test_project_id: str) -> None:
    """测试创建变更单对话框填写流程：填写表单不崩溃（不实际提交，避免模态弹窗阻塞）"""
    enter_workspace(main_window, test_project_id, app)
    switch_workspace_tab(main_window, "change", app)
    change_tab = main_window._workspace_view._change_tab
    assert change_tab is not None

    created: list[object] = []

    def _fill_and_close() -> None:
        dlg = find_dialog(app, "创建变更单")
        if dlg is None:
            return
        created.append(dlg)
        # 填写表单（不提交，避免 QMessageBox.critical 模态阻塞）
        try:
            set_combo_by_data(dlg._project_combo, test_project_id)  # type: ignore[attr-defined]
            set_combo_by_data(dlg._domain_combo, "PLC")  # type: ignore[attr-defined]
            set_combo_by_data(dlg._nature_combo, "DEF")  # type: ignore[attr-defined]
            set_combo_by_data(dlg._scope_combo, "LOCAL")  # type: ignore[attr-defined]
            dlg._applicant_edit.setText("auto_test")  # type: ignore[attr-defined]
            dlg._background_edit.setPlainText("GUI自动化测试创建变更单")  # type: ignore[attr-defined]
            app.processEvents()
            QTest.qWait(100)
        finally:
            reject_dialog(dlg, app)
        dismiss_message_boxes(app)

    QTimer.singleShot(100, _fill_and_close)
    change_tab._on_create_change()

    assert len(created) == 1, "创建变更单对话框未弹出"


@pytest.mark.gui
def test_change_status_filter(main_window: MainWindow, app: QApplication, test_project_id: str) -> None:
    """测试变更 Tab 状态筛选下拉切换不崩溃"""
    enter_workspace(main_window, test_project_id, app)
    switch_workspace_tab(main_window, "change", app)
    change_tab = main_window._workspace_view._change_tab
    assert change_tab is not None

    for i in range(change_tab._status_combo.count()):
        change_tab._status_combo.setCurrentIndex(i)
        app.processEvents()
        QTest.qWait(200)

    # 恢复全部状态
    change_tab._status_combo.setCurrentIndex(0)
    app.processEvents()
    QTest.qWait(200)


@pytest.mark.gui
def test_change_domain_filter(main_window: MainWindow, app: QApplication, test_project_id: str) -> None:
    """测试变更 Tab 领域筛选下拉切换不崩溃"""
    enter_workspace(main_window, test_project_id, app)
    switch_workspace_tab(main_window, "change", app)
    change_tab = main_window._workspace_view._change_tab
    assert change_tab is not None

    for i in range(change_tab._domain_combo.count()):
        change_tab._domain_combo.setCurrentIndex(i)
        app.processEvents()
        QTest.qWait(200)

    # 恢复全部领域
    change_tab._domain_combo.setCurrentIndex(0)
    app.processEvents()
    QTest.qWait(200)
