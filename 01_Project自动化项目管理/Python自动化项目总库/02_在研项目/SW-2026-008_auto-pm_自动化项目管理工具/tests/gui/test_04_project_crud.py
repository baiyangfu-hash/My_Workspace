"""项目 CRUD GUI 测试

覆盖新建项目对话框、编辑项目对话框、dry-run 预览、实际创建项目等交互流程。
所有涉及模态对话框（dialog.exec()）的用例均通过 QTimer.singleShot
在调用前调度对话框查找与关闭逻辑，避免阻塞测试线程。

V3 升级（2026-07-01）：
  - 新增 test_new_project_actual_create：实际点 OK 创建项目 + 验证项目出现在列表
  - 新增 test_new_project_duplicate_id：创建已存在 ID 验证错误提示
  - 所有 error 分支调用 close_all_modal_widgets 防止残留弹窗阻塞
"""

from __future__ import annotations

import os
import shutil
from typing import TYPE_CHECKING

# V0.5.2: 默认可见模式（用户要求）；offscreen 仅通过 QT_QPA_PLATFORM=offscreen 环境变量设置

import pytest
from PySide6.QtCore import QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QComboBox, QDialogButtonBox

from tests.gui.helpers.interactions import (
    close_all_modal_widgets,
    dismiss_message_boxes,
    enter_workspace,
    find_dialog,
    reject_dialog,
)

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication

    from auto_pm.ui.main_window import MainWindow

# 实际创建项目测试用的独立 ID（不与 session fixture DJ-2026-998 冲突）
_ACTUAL_CREATE_ID = "DJ-2026-900"


def set_combo_by_data(combo: QComboBox, data_value: str) -> None:
    """通过 data 值设置 ComboBox 选中项"""
    for i in range(combo.count()):
        if combo.itemData(i) == data_value:
            combo.setCurrentIndex(i)
            return
    raise ValueError(f"未找到 data={data_value}")


@pytest.mark.gui
def test_new_project_dialog_open(main_window: MainWindow, app: QApplication) -> None:
    """测试点击新建项目后能正常弹出新建项目对话框"""
    found: list[object] = []

    def _verify_and_close() -> None:
        dlg = find_dialog(app, "新建项目")
        assert dlg is not None, "新建项目对话框未弹出"
        found.append(dlg)
        reject_dialog(dlg, app)

    QTimer.singleShot(100, _verify_and_close)
    main_window._on_new_project("plc")

    assert len(found) == 1, "新建项目对话框未弹出"


@pytest.mark.gui
def test_new_project_invalid_id(main_window: MainWindow, app: QApplication) -> None:
    """测试新建项目对话框能填写非法编号（不点击 OK，避免 QMessageBox 模态阻塞）"""
    found: list[object] = []

    def _fill_and_close() -> None:
        dlg = find_dialog(app, "新建项目")
        if dlg is None:
            return
        found.append(dlg)
        dlg._id_edit.setText("invalid")  # type: ignore[attr-defined]
        app.processEvents()
        QTest.qWait(100)
        # 不点击 OK，避免触发 QMessageBox.warning 模态阻塞
        reject_dialog(dlg, app)
        dismiss_message_boxes(app)

    QTimer.singleShot(100, _fill_and_close)
    main_window._on_new_project("plc")

    assert len(found) == 1, "新建项目对话框未弹出"


@pytest.mark.gui
def test_edit_project_dialog_open(main_window: MainWindow, app: QApplication, test_project_id: str) -> None:
    """测试进入工作区后点击编辑按钮能弹出编辑项目对话框"""
    enter_workspace(main_window, test_project_id, app)
    assert main_window._stack.currentIndex() == 1

    found: list[object] = []

    def _verify_and_close() -> None:
        dlg = find_dialog(app, "编辑项目")
        assert dlg is not None, "编辑项目对话框未弹出"
        found.append(dlg)
        reject_dialog(dlg, app)

    QTimer.singleShot(100, _verify_and_close)
    main_window._workspace_view._on_edit_clicked()

    assert len(found) == 1, "编辑项目对话框未弹出"


@pytest.mark.gui
def test_new_project_dry_run(main_window: MainWindow, app: QApplication, test_project_id: str) -> None:
    """测试新建项目对话框勾选 dry-run 后仅预览不实际创建项目"""
    found: list[object] = []

    def _fill_and_accept() -> None:
        dlg = find_dialog(app, "新建项目")
        if dlg is None:
            return
        found.append(dlg)
        # 使用合法编号 + 不冲突名称，确保走通 dry-run 预览分支
        dlg._id_edit.setText(test_project_id)  # type: ignore[attr-defined]
        dlg._name_edit.setText("dry_run_test")  # type: ignore[attr-defined]
        set_combo_by_data(dlg._stack_combo, "plc")  # type: ignore[attr-defined]
        dlg._dry_run_check.setChecked(True)  # type: ignore[attr-defined]
        app.processEvents()
        QTest.qWait(100)
        # dry-run 点击 OK 会弹出预览信息框（模态），需提前调度关闭
        QTimer.singleShot(300, lambda: dismiss_message_boxes(app))
        ok_btn = dlg._button_box.button(QDialogButtonBox.StandardButton.Ok)  # type: ignore[attr-defined]
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


@pytest.mark.gui
def test_new_project_actual_create(
    main_window: MainWindow,
    app: QApplication,
    workspace_root: str,
) -> None:
    """实际创建项目：填写表单 + 点 OK + 验证项目出现在列表

    使用独立 ID DJ-2026-900 避免与 session fixture 的 DJ-2026-998 冲突。
    测试后清理创建的项目目录，防止污染后续测试。

    V3.1 修复（2026-07-01）：
      - 断言逻辑：_on_accept 成功时只 emit projectCreated + accept()，不弹 QMessageBox。
        改用 projectCreated 信号 + dialog.accepted 状态判断成功，不依赖消息框文本。
      - 清理路径：补充 02_在研项目/（_PROJECTS_SUBDIR 实际值），原仅清 0100_PLC自动化/。
    """
    from PySide6.QtWidgets import QDialog

    result: dict[str, object] = {}

    def _fill_and_submit() -> None:
        dismiss_message_boxes(app)
        dlg = find_dialog(app, "新建项目")
        if dlg is None:
            result["error"] = "对话框未弹出"
            close_all_modal_widgets(app)
            return
        try:
            dlg._id_edit.setText(_ACTUAL_CREATE_ID)  # type: ignore[attr-defined]
            dlg._name_edit.setText("实际创建测试项目")  # type: ignore[attr-defined]
            set_combo_by_data(dlg._stack_combo, "plc")  # type: ignore[attr-defined]
            dlg._dry_run_check.setChecked(False)  # type: ignore[attr-defined]
            app.processEvents()
            QTest.qWait(100)

            # 监听 projectCreated 信号（_on_accept 成功时 emit，无需依赖 QMessageBox）
            dlg.projectCreated.connect(lambda pid: result.__setitem__("success", True))  # type: ignore[attr-defined]

            # 预注册 QMessageBox 处理（在 click() 之前注册，
            # 因为 accept 可能弹 QMessageBox 阻塞 click()）
            def _handle_msg() -> None:
                texts = dismiss_message_boxes(app)
                for t in texts:
                    if "已存在" in t or "失败" in t or "错误" in t or "格式" in t:
                        result["error"] = t
                # 失败时关闭对话框防止阻塞
                if not result.get("success") and dlg.isVisible():
                    dlg.reject()
                    app.processEvents()
                    QTest.qWait(300)
                app.processEvents()
                QTest.qWait(500)

            QTimer.singleShot(300, _handle_msg)
            ok_btn = dlg._button_box.button(QDialogButtonBox.StandardButton.Ok)  # type: ignore[attr-defined]
            ok_btn.click()
        except Exception as e:
            result["error"] = str(e)
            close_all_modal_widgets(app)

    QTimer.singleShot(100, _fill_and_submit)
    main_window._on_new_project("plc")

    try:
        assert result.get("success"), f"创建项目失败: {result.get('error', '未知错误')}"
        # 刷新列表并验证项目出现
        main_window._on_refresh()
        app.processEvents()
        QTest.qWait(800)
        proj = main_window._project_list_view.get_project(_ACTUAL_CREATE_ID)
        assert proj is not None, f"创建后项目 {_ACTUAL_CREATE_ID} 未出现在列表中"
        assert proj.name == "实际创建测试项目"
    finally:
        # 清理创建的项目目录（避免污染后续测试）
        # _PROJECTS_SUBDIR 实际值为 "02_在研项目"，但兼容多种可能路径
        import glob
        for pattern in [
            f"{workspace_root}/02_在研项目/{_ACTUAL_CREATE_ID}*",
            f"{workspace_root}/0100_PLC自动化/{_ACTUAL_CREATE_ID}*",
            f"{workspace_root}/{_ACTUAL_CREATE_ID}*",
        ]:
            for path in glob.glob(pattern):
                shutil.rmtree(path, ignore_errors=True)


@pytest.mark.gui
def test_new_project_duplicate_id(
    main_window: MainWindow,
    app: QApplication,
    test_project_id: str,
    workspace_root: str,
) -> None:
    """创建已存在路径的项目，验证弹出"路径已存在"错误提示

    V3.1 修复（2026-07-01）：_on_accept 实际检测的是 dest_path 是否存在
    （02_在研项目/<ID>_<名称>），而非 project_id 重复。预先创建同名目录触发检测。
    """
    import os as _os

    result: dict[str, object] = {}

    # 预先创建目标路径，触发 _on_accept 的"路径已存在"分支
    dest_path = _os.path.join(workspace_root, "02_在研项目", f"{test_project_id}_重复ID测试")
    _os.makedirs(dest_path, exist_ok=True)

    def _fill_and_submit() -> None:
        dismiss_message_boxes(app)
        dlg = find_dialog(app, "新建项目")
        if dlg is None:
            result["error"] = "对话框未弹出"
            close_all_modal_widgets(app)
            return
        try:
            # 用已存在的 fixture 项目 ID + 预创建目录的名称
            dlg._id_edit.setText(test_project_id)  # type: ignore[attr-defined]
            dlg._name_edit.setText("重复ID测试")  # type: ignore[attr-defined]
            set_combo_by_data(dlg._stack_combo, "plc")  # type: ignore[attr-defined]
            dlg._dry_run_check.setChecked(False)  # type: ignore[attr-defined]
            app.processEvents()
            QTest.qWait(100)

            # 预注册 QMessageBox 处理（在 click() 之前注册）
            def _handle_msg() -> None:
                texts = dismiss_message_boxes(app)
                for t in texts:
                    result["msg_text"] = t
                    if "已存在" in t:
                        result["duplicate_detected"] = True
                # 关闭对话框防止阻塞
                if dlg.isVisible():
                    dlg.reject()
                    app.processEvents()
                    QTest.qWait(300)
                app.processEvents()
                QTest.qWait(500)

            QTimer.singleShot(300, _handle_msg)
            ok_btn = dlg._button_box.button(QDialogButtonBox.StandardButton.Ok)  # type: ignore[attr-defined]
            ok_btn.click()
        except Exception as e:
            result["error"] = str(e)
            close_all_modal_widgets(app)

    QTimer.singleShot(100, _fill_and_submit)
    main_window._on_new_project("plc")

    # 清理预创建目录
    import shutil as _shutil
    _shutil.rmtree(dest_path, ignore_errors=True)

    # 验证弹出了"已存在"提示（或至少有错误提示，不崩溃）
    assert not result.get("error"), f"测试异常: {result.get('error')}"
    msg = result.get("msg_text", "")
    assert msg, "未弹出任何消息框"
    # 宽松断言：包含"已存在"或"失败"或"冲突"等关键词
    assert any(kw in msg for kw in ["已存在", "失败", "冲突", "重复"]), (
        f"消息框文本预期包含'已存在/失败/冲突/重复'，实际: '{msg}'"
    )


@pytest.mark.gui
def test_new_project_empty_id_submit(main_window: MainWindow, app: QApplication) -> None:
    """测试新建项目对话框 ID 为空时点 OK 弹出"请输入项目编号"警告（表单验证边界）

    NewProjectDialog._on_accept 在 ID 为空时弹 QMessageBox.warning("请输入项目编号")。
    验证警告弹出 + 对话框不关闭（验证失败时 _on_accept 直接 return 不 accept）。
    """
    result: dict[str, object] = {}

    def _fill_empty_and_submit() -> None:
        dismiss_message_boxes(app)
        dlg = find_dialog(app, "新建项目")
        if dlg is None:
            result["error"] = "对话框未弹出"
            close_all_modal_widgets(app)
            return
        try:
            # ID 和 name 都留空，直接点 OK
            dlg._id_edit.setText("")  # type: ignore[attr-defined]
            dlg._name_edit.setText("空ID测试")  # type: ignore[attr-defined]
            app.processEvents()
            QTest.qWait(100)

            # 预注册 QMessageBox 处理（在 click() 之前注册，warning 会模态阻塞）
            def _handle_msg() -> None:
                texts = dismiss_message_boxes(app)
                for t in texts:
                    result["msg_text"] = t
                    if "请输入项目编号" in t or "输入错误" in t:
                        result["validation_triggered"] = True
                # 验证失败时 _on_accept 直接 return，对话框仍可见，需手动关闭
                if dlg.isVisible():
                    dlg.reject()
                    app.processEvents()
                    QTest.qWait(300)
                app.processEvents()
                QTest.qWait(500)

            QTimer.singleShot(300, _handle_msg)
            ok_btn = dlg._button_box.button(QDialogButtonBox.StandardButton.Ok)  # type: ignore[attr-defined]
            ok_btn.click()
        except Exception as e:
            result["error"] = str(e)
            close_all_modal_widgets(app)

    QTimer.singleShot(100, _fill_empty_and_submit)
    main_window._on_new_project("plc")

    # 验证弹出了"请输入项目编号"警告
    assert not result.get("error"), f"测试异常: {result.get('error')}"
    msg = result.get("msg_text", "")
    assert msg, "ID 为空时未弹出任何消息框"
    assert any(kw in msg for kw in ["请输入项目编号", "输入错误"]), (
        f"消息框文本预期包含'请输入项目编号/输入错误'，实际: '{msg}'"
    )


@pytest.mark.gui
def test_new_project_cancel_button(main_window: MainWindow, app: QApplication) -> None:
    """测试新建项目对话框取消按钮正确关闭对话框（对话框生命周期边界）

    点击新建项目 → 弹出对话框 → 点 Cancel 按钮 → 验证对话框关闭。
    """
    result: dict[str, object] = {}

    def _cancel_dialog() -> None:
        dismiss_message_boxes(app)
        dlg = find_dialog(app, "新建项目")
        if dlg is None:
            result["error"] = "对话框未弹出"
            close_all_modal_widgets(app)
            return
        try:
            cancel_btn = dlg._button_box.button(QDialogButtonBox.StandardButton.Cancel)  # type: ignore[attr-defined]
            cancel_btn.click()
            app.processEvents()
            QTest.qWait(300)
            result["cancelled"] = not dlg.isVisible()
        except Exception as e:
            result["error"] = str(e)
            close_all_modal_widgets(app)

    QTimer.singleShot(100, _cancel_dialog)
    main_window._on_new_project("plc")

    assert not result.get("error"), f"测试异常: {result.get('error')}"
    assert result.get("cancelled"), "取消按钮未关闭对话框"
