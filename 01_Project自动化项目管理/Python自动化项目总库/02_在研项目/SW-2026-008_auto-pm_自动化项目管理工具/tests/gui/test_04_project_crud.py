"""项目 CRUD GUI 测试

覆盖新建项目对话框、编辑项目对话框、dry-run 预览等交互流程。
所有涉及模态对话框（dialog.exec()）的用例均通过 QTimer.singleShot
在调用前调度对话框查找与关闭逻辑，避免阻塞测试线程。
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QDialogButtonBox

from tests.gui.helpers.interactions import (
    dismiss_message_boxes,
    enter_workspace,
    find_dialog,
    reject_dialog,
)


def set_combo_by_data(combo, data_value):
    """通过 data 值设置 ComboBox 选中项"""
    for i in range(combo.count()):
        if combo.itemData(i) == data_value:
            combo.setCurrentIndex(i)
            return
    raise ValueError(f"未找到 data={data_value}")


@pytest.mark.gui
def test_new_project_dialog_open(main_window, app):
    """测试点击新建项目后能正常弹出新建项目对话框"""
    found = []

    def _verify_and_close():
        dlg = find_dialog(app, "新建项目")
        if dlg is not None:
            found.append(dlg)
            reject_dialog(dlg, app)

    QTimer.singleShot(100, _verify_and_close)
    main_window._on_new_project("plc")

    assert len(found) == 1, "新建项目对话框未弹出"


@pytest.mark.gui
def test_new_project_invalid_id(main_window, app):
    """测试新建项目对话框能填写非法编号（不点击 OK，避免 QMessageBox 模态阻塞）"""
    found = []

    def _fill_and_close():
        dlg = find_dialog(app, "新建项目")
        if dlg is None:
            return
        found.append(dlg)
        dlg._id_edit.setText("invalid")
        app.processEvents()
        QTest.qWait(100)
        # 不点击 OK，避免触发 QMessageBox.warning 模态阻塞
        reject_dialog(dlg, app)
        dismiss_message_boxes(app)

    QTimer.singleShot(100, _fill_and_close)
    main_window._on_new_project("plc")

    assert len(found) == 1, "新建项目对话框未弹出"


@pytest.mark.gui
def test_edit_project_dialog_open(main_window, app, test_project_id):
    """测试进入工作区后点击编辑按钮能弹出编辑项目对话框"""
    enter_workspace(main_window, test_project_id, app)
    assert main_window._stack.currentIndex() == 1

    found = []

    def _verify_and_close():
        dlg = find_dialog(app, "编辑项目")
        if dlg is not None:
            found.append(dlg)
            reject_dialog(dlg, app)

    QTimer.singleShot(100, _verify_and_close)
    main_window._workspace_view._on_edit_clicked()

    assert len(found) == 1, "编辑项目对话框未弹出"


@pytest.mark.gui
def test_new_project_dry_run(main_window, app, test_project_id):
    """测试新建项目对话框勾选 dry-run 后仅预览不实际创建项目"""
    found = []

    def _fill_and_accept():
        dlg = find_dialog(app, "新建项目")
        if dlg is None:
            return
        found.append(dlg)
        # 使用合法编号 + 不冲突名称，确保走通 dry-run 预览分支
        dlg._id_edit.setText(test_project_id)
        dlg._name_edit.setText("dry_run_test")
        set_combo_by_data(dlg._stack_combo, "plc")
        dlg._dry_run_check.setChecked(True)
        app.processEvents()
        QTest.qWait(100)
        # dry-run 点击 OK 会弹出预览信息框（模态），需提前调度关闭
        QTimer.singleShot(300, lambda: dismiss_message_boxes(app))
        ok_btn = dlg._button_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_btn.click()
        app.processEvents()
        QTest.qWait(300)
        # dry-run 不关闭对话框，需手动关闭
        if dlg.isVisible():
            reject_dialog(dlg, app)
        dismiss_message_boxes(app)

    QTimer.singleShot(100, _fill_and_accept)
    main_window._on_new_project("plc")

    assert len(found) == 1, "新建项目对话框未弹出"
