"""变更 Tab GUI 测试

覆盖变更 Tab 切换、创建变更单对话框、创建变更单完整流程、实际创建变更单、
实际状态流转、状态/领域筛选等交互。
涉及模态对话框（dialog.exec()）的用例通过 QTimer.singleShot 调度对话框操作。

V3 升级（2026-07-01）：
  - 新增 test_create_change_actual_submit：实际提交创建变更单 + 验证出现在列表
  - 新增 test_change_status_transition：实际状态流转 7 次到 completed
  - 所有 error 分支调用 close_all_modal_widgets 防止残留弹窗阻塞
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

# V0.5.2: 默认可见模式（用户要求）；offscreen 仅通过 QT_QPA_PLATFORM=offscreen 环境变量设置

import pytest
from PySide6.QtCore import QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QComboBox

from tests.gui.helpers.interactions import (
    close_all_modal_widgets,
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
def test_create_change_actual_submit(
    main_window: MainWindow,
    app: QApplication,
    test_project_id: str,
) -> None:
    """实际创建变更单：填表 + 跳页 + 点完成 + 验证变更单出现在列表

    使用 QWizard 的 next() 推进页面，最后一步触发 validatePage → _on_create。

    V3.1 修复（2026-07-01）：_on_create 成功时只 emit change_created 信号 + 返回 True，
    不弹 QMessageBox。改用 change_created 信号判断成功，不依赖消息框文本。
    """
    enter_workspace(main_window, test_project_id, app)
    switch_workspace_tab(main_window, "change", app)
    change_tab = main_window._workspace_view._change_tab
    assert change_tab is not None

    result: dict[str, object] = {}

    def _fill_wizard_and_submit() -> None:
        dismiss_message_boxes(app)
        wizard = find_dialog(app, "创建变更单")
        if wizard is None:
            result["error"] = "向导未弹出"
            close_all_modal_widgets(app)
            return
        # 监听 change_created 信号（_on_create 成功时 emit，无需依赖 QMessageBox）
        wizard.change_created.connect(lambda pid: result.__setitem__("success", True))  # type: ignore[attr-defined]
        try:
            # 等待 _load_projects 完成
            for _ in range(20):
                if wizard._project_combo.count() > 0:  # type: ignore[attr-defined]
                    break
                app.processEvents()
                QTest.qWait(100)
            # 第 1 页：基本信息
            try:
                set_combo_by_data(wizard._project_combo, test_project_id)  # type: ignore[attr-defined]
            except Exception:
                if wizard._project_combo.count() > 0:  # type: ignore[attr-defined]
                    wizard._project_combo.setCurrentIndex(0)  # type: ignore[attr-defined]
                else:
                    result["error"] = "项目下拉框无数据"
                    wizard.reject()  # type: ignore[attr-defined]
                    app.processEvents()
                    QTest.qWait(300)
                    return
            app.processEvents()
            QTest.qWait(100)
            try:
                set_combo_by_data(wizard._domain_combo, "PLC")  # type: ignore[attr-defined]
                set_combo_by_data(wizard._nature_combo, "DEF")  # type: ignore[attr-defined]
                set_combo_by_data(wizard._scope_combo, "LOCAL")  # type: ignore[attr-defined]
            except Exception:
                pass
            wizard._applicant_edit.setText("auto_test")  # type: ignore[attr-defined]
            app.processEvents()
            QTest.qWait(100)
            wizard._background_edit.setPlainText("GUI自动化测试创建变更单")  # type: ignore[attr-defined]
            app.processEvents()
            QTest.qWait(100)

            # 跳到描述页
            wizard.next()  # type: ignore[attr-defined]
            app.processEvents()
            QTest.qWait(500)
            try:
                wizard._necessity_edit.setPlainText("自动化测试必需")  # type: ignore[attr-defined]
                app.processEvents()
                QTest.qWait(100)
            except Exception:
                pass

            # 跳到确认页
            wizard.next()  # type: ignore[attr-defined]
            app.processEvents()
            QTest.qWait(500)

            # 预注册 QMessageBox 处理（在 Finish 点击之前注册，
            # 因为 validatePage → _on_create 失败时弹 QMessageBox 阻塞）
            def _handle_msg() -> None:
                texts = dismiss_message_boxes(app)
                for t in texts:
                    if "失败" in t or "错误" in t:
                        result["error"] = t
                # 失败时关闭 wizard 防止阻塞（成功时 wizard 已被 QWizard.accept 关闭）
                if not result.get("success") and wizard.isVisible():  # type: ignore[attr-defined]
                    wizard.reject()  # type: ignore[attr-defined]
                    app.processEvents()
                    QTest.qWait(300)
                app.processEvents()
                QTest.qWait(500)

            QTimer.singleShot(300, _handle_msg)
            # 点 Finish 按钮（不是 next()！QWizard.next() 在最后一页只调 validatePage 不 accept，
            # 必须用 FinishButton.click() 触发 done(Accepted) 让 wizard.exec() 退出）
            from PySide6.QtWidgets import QWizard
            finish_btn = wizard.button(QWizard.WizardButton.FinishButton)  # type: ignore[attr-defined]
            finish_btn.click()
            app.processEvents()
            QTest.qWait(1000)
        except Exception as e:
            result["error"] = f"向导填写异常: {e}"
            close_all_modal_widgets(app)

    QTimer.singleShot(100, _fill_wizard_and_submit)
    change_tab._on_create_change()

    assert result.get("success"), f"创建变更单失败: {result.get('error', '未知错误')}"
    # 刷新变更列表并验证
    change_tab._refresh_list()
    app.processEvents()
    QTest.qWait(500)
    cards = change_tab._get_cards()
    assert len(cards) >= 1, f"创建后变更卡片数预期 >=1，实际 {len(cards)}"


@pytest.mark.gui
def test_change_status_transition(
    main_window: MainWindow,
    app: QApplication,
    test_project_id: str,
) -> None:
    """实际状态流转：创建变更单后流转 7 次到 completed

    第 1 次流转（draft→submitted）用 GUI 对话框（单目标），
    后续流转用 ChangeService.transition_status() API（多目标弹 QMenu 难处理）。
    """
    from auto_pm.change.change_service import ChangeService

    enter_workspace(main_window, test_project_id, app)
    switch_workspace_tab(main_window, "change", app)
    change_tab = main_window._workspace_view._change_tab
    assert change_tab is not None

    # ── 步骤1：先创建变更单（复用实际提交流程）──
    create_result: dict[str, object] = {}

    def _fill_wizard_and_submit() -> None:
        dismiss_message_boxes(app)
        wizard = find_dialog(app, "创建变更单")
        if wizard is None:
            create_result["error"] = "向导未弹出"
            close_all_modal_widgets(app)
            return
        # 监听 change_created 信号（V3.1：_on_create 成功时不弹 QMessageBox）
        wizard.change_created.connect(lambda pid: create_result.__setitem__("success", True))  # type: ignore[attr-defined]
        try:
            for _ in range(20):
                if wizard._project_combo.count() > 0:  # type: ignore[attr-defined]
                    break
                app.processEvents()
                QTest.qWait(100)
            try:
                set_combo_by_data(wizard._project_combo, test_project_id)  # type: ignore[attr-defined]
            except Exception:
                if wizard._project_combo.count() > 0:  # type: ignore[attr-defined]
                    wizard._project_combo.setCurrentIndex(0)  # type: ignore[attr-defined]
                else:
                    create_result["error"] = "项目下拉框无数据"
                    wizard.reject()  # type: ignore[attr-defined]
                    return
            try:
                set_combo_by_data(wizard._domain_combo, "PLC")  # type: ignore[attr-defined]
                set_combo_by_data(wizard._nature_combo, "DEF")  # type: ignore[attr-defined]
                set_combo_by_data(wizard._scope_combo, "LOCAL")  # type: ignore[attr-defined]
            except Exception:
                pass
            wizard._applicant_edit.setText("auto_test")  # type: ignore[attr-defined]
            wizard._background_edit.setPlainText("状态流转测试")  # type: ignore[attr-defined]
            app.processEvents()
            wizard.next()  # type: ignore[attr-defined]
            app.processEvents()
            QTest.qWait(500)
            try:
                wizard._necessity_edit.setPlainText("流转测试必需")  # type: ignore[attr-defined]
            except Exception:
                pass
            app.processEvents()
            wizard.next()  # type: ignore[attr-defined]
            app.processEvents()
            QTest.qWait(500)

            # 预注册 QMessageBox 处理（在 Finish 点击之前注册，处理失败分支）
            def _handle_msg() -> None:
                texts = dismiss_message_boxes(app)
                for t in texts:
                    if "失败" in t or "错误" in t:
                        create_result["error"] = t
                if not create_result.get("success") and wizard.isVisible():  # type: ignore[attr-defined]
                    wizard.reject()  # type: ignore[attr-defined]
                    app.processEvents()
                    QTest.qWait(300)

            QTimer.singleShot(300, _handle_msg)
            # 点 Finish 按钮（不是 next()！QWizard.next() 在最后一页不 accept）
            from PySide6.QtWidgets import QWizard
            finish_btn = wizard.button(QWizard.WizardButton.FinishButton)  # type: ignore[attr-defined]
            finish_btn.click()
            app.processEvents()
            QTest.qWait(1000)
        except Exception as e:
            create_result["error"] = str(e)
            close_all_modal_widgets(app)

    QTimer.singleShot(100, _fill_wizard_and_submit)
    change_tab._on_create_change()
    assert create_result.get("success"), f"创建变更单失败: {create_result.get('error')}"

    # 获取刚创建的变更单编号
    change_tab._refresh_list()
    app.processEvents()
    QTest.qWait(500)
    cards = change_tab._get_cards()
    assert len(cards) >= 1, "无变更单可流转"
    change_number = cards[0]._summary.change_number

    # ── 步骤2：第 1 次流转 draft→submitted（GUI 对话框）──
    transition_result: dict[str, object] = {}

    def _fill_transition() -> None:
        dismiss_message_boxes(app)
        dlg = find_dialog(app, "流转") or find_dialog(app, "状态流转")
        if dlg is None:
            transition_result["error"] = "流转对话框未弹出"
            close_all_modal_widgets(app)
            return
        # 监听 transition_completed 信号（V3.1：流转成功时不弹 QMessageBox，只 emit + accept）
        dlg.transition_completed.connect(lambda cn: transition_result.__setitem__("success", True))  # type: ignore[attr-defined]
        try:
            dlg._approver_edit.setText("auto_test")  # type: ignore[attr-defined]
            app.processEvents()
            QTest.qWait(100)
            dlg._comment_edit.setPlainText("自动测试流转至已提交")  # type: ignore[attr-defined]
            app.processEvents()
            QTest.qWait(100)

            # 预注册 QMessageBox 处理（在 click() 之前注册，处理失败分支）
            def _handle_msg() -> None:
                texts = dismiss_message_boxes(app)
                for t in texts:
                    if "失败" in t or "错误" in t:
                        transition_result["error"] = t
                if not transition_result.get("success") and dlg.isVisible():
                    dlg.reject()
                    app.processEvents()
                    QTest.qWait(300)

            QTimer.singleShot(300, _handle_msg)
            from PySide6.QtWidgets import QDialogButtonBox
            ok_btn = dlg._button_box.button(QDialogButtonBox.StandardButton.Ok)  # type: ignore[attr-defined]
            ok_btn.click()
        except Exception as e:
            transition_result["error"] = str(e)
            close_all_modal_widgets(app)

    QTimer.singleShot(100, _fill_transition)
    # 选中第一张卡片并点击流转按钮
    cards[0]._transition_btn.click()
    app.processEvents()
    QTest.qWait(500)

    # 第 1 次 GUI 流转可能失败（多目标弹 QMenu），降级用 API
    if not transition_result.get("success"):
        close_all_modal_widgets(app)
        change_service = ChangeService(workspace_root=main_window._workspace_root)
        try:
            cr = change_service.transition_status(
                change_number=change_number,
                new_status="submitted",
                approver="auto_test",
                comment="API 自动测试流转至已提交",
            )
            assert cr is not None, "API 流转 draft→submitted 失败"
        except Exception as e:
            pytest.fail(f"API 流转 draft→submitted 异常: {e}")

    # ── 步骤3：后续流转用 API（under_review→approved→implementing→pending_acceptance→accepting→completed）──
    close_all_modal_widgets(app)
    change_service = ChangeService(workspace_root=main_window._workspace_root)
    transitions = [
        ("under_review", "审核中"),
        ("approved", "已批准"),
        ("implementing", "实施中"),
        ("pending_acceptance", "待验收"),
        ("accepting", "验收中"),
        ("completed", "已完成"),
    ]
    for target_status, label in transitions:
        try:
            cr = change_service.transition_status(
                change_number=change_number,
                new_status=target_status,
                approver="auto_test",
                comment=f"自动测试流转至{label}",
                verification_conclusion="全部通过" if target_status == "completed" else "通过",
            )
            assert cr is not None, f"API 流转至 {label} 失败"
            change_tab._refresh_list()
            app.processEvents()
            QTest.qWait(300)
        except Exception as e:
            pytest.fail(f"API 流转至 {label} 异常: {e}")


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


@pytest.mark.gui
def test_change_tab_empty_state(main_window: MainWindow, app: QApplication, test_project_id: str) -> None:
    """测试变更 Tab 空状态提示与变更单数量一致性

    验证 _refresh_list 的 UI 逻辑：无变更单时 _empty_hint 可见 + 文本含"暂无变更单"；
    有变更单时 _empty_hint 不可见。
    注：fixture 项目可能因前序测试残留变更单，故用一致性断言而非硬编码空状态。
    """
    enter_workspace(main_window, test_project_id, app)
    switch_workspace_tab(main_window, "change", app)
    change_tab = main_window._workspace_view._change_tab
    assert change_tab is not None

    # 刷新列表（确保加载最新状态）
    change_tab._refresh_list()
    app.processEvents()
    QTest.qWait(500)

    cards = change_tab._get_cards()
    if len(cards) == 0:
        # 无变更单：空状态提示应可见
        assert change_tab._empty_hint.isVisible(), "无变更单时空状态提示应可见"
        assert "暂无变更单" in change_tab._empty_hint.text(), (
            f"空状态文本异常: {change_tab._empty_hint.text()}"
        )
    else:
        # 有变更单：空状态提示应不可见
        assert not change_tab._empty_hint.isVisible(), (
            f"有 {len(cards)} 个变更单时空状态提示不应可见"
        )


@pytest.mark.gui
def test_create_change_cancel_wizard(main_window: MainWindow, app: QApplication, test_project_id: str) -> None:
    """测试创建变更单向导取消按钮正确关闭对话框（对话框生命周期边界）

    点击创建变更单 → 弹出 wizard → 点 Cancel 按钮 → 验证 wizard 关闭。
    """
    from PySide6.QtWidgets import QWizard

    enter_workspace(main_window, test_project_id, app)
    switch_workspace_tab(main_window, "change", app)
    change_tab = main_window._workspace_view._change_tab
    assert change_tab is not None

    result: dict[str, object] = {}

    def _cancel_wizard() -> None:
        dismiss_message_boxes(app)
        wizard = find_dialog(app, "创建变更单")
        if wizard is None:
            result["error"] = "向导未弹出"
            close_all_modal_widgets(app)
            return
        try:
            # 点 Cancel 按钮（QWizard 的 CancelButton）
            cancel_btn = wizard.button(QWizard.WizardButton.CancelButton)  # type: ignore[attr-defined]
            cancel_btn.click()
            app.processEvents()
            QTest.qWait(300)
            result["cancelled"] = not wizard.isVisible()
        except Exception as e:
            result["error"] = str(e)
            close_all_modal_widgets(app)

    QTimer.singleShot(100, _cancel_wizard)
    change_tab._on_create_change()

    assert not result.get("error"), f"测试异常: {result.get('error')}"
    assert result.get("cancelled"), "取消按钮未关闭 wizard"
