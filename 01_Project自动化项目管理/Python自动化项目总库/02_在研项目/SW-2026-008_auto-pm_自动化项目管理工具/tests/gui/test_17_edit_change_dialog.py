"""EditChangeDialog GUI 集成测试

测试内容：
- 从 MainWindow 导航到变更中心，触发 EditChangeDialog 弹窗
- 验证弹窗标题、Tab 结构、表单字段加载
- 测试 Tab 切换（基本信息 ↔ 影响分析）
- 测试表单字段交互（输入、选择、表格）
- 测试保存按钮和信号发射
- 测试取消按钮关闭弹窗

使用 tests/gui/conftest.py 提供的 main_window / app / bug_recorder fixture，
通过 helpers 辅助函数操作 GUI，发现 bug 自动记录到 bug_recorder。
"""

from __future__ import annotations

import logging
import os

# 必须在导入 PySide6 前设置离屏渲染（GUI_VISIBLE=1 时切换为可见窗口演示模式）
if not os.environ.get("GUI_VISIBLE"):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402
from PySide6.QtCore import Qt, QTimer  # noqa: E402
from PySide6.QtTest import QTest  # noqa: E402
from PySide6.QtWidgets import (  # noqa: E402
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QTabWidget,
)

from auto_pm.change.change_service import ChangeService  # noqa: E402
from auto_pm.change.path_resolver import find_ledger_file  # noqa: E402
from auto_pm.ui.dialogs.edit_change_dialog import EditChangeDialog  # noqa: E402
from tests.gui.helpers.assertions import assert_stack_index  # noqa: E402
from tests.gui.helpers.interactions import click_nav_page  # noqa: E402

logger = logging.getLogger(__name__)

# ── 测试隔离：记录本模块创建的变更单，autouse fixture 在每个测试后清理 ──
_created_change_numbers: list[str] = []


@pytest.fixture(autouse=True)
def _cleanup_test_changes(workspace_root: str):
    """每个测试后清理本测试创建的变更单文件和台帐条目，避免污染生产数据（TD-T10 修复）

    V0.4.1 收口批次修复：原 `except Exception: pass` 静默吞掉所有清理异常，
    导致 CHG-SCPT-2026-076 残留生产数据（TD-T09 复发）。改为 logging.warning
    暴露清理失败，便于诊断 fixture 缺陷。
    """
    yield
    cs = ChangeService(workspace_root)
    ledger_updater = cs._get_ledger_updater()
    for change_number in _created_change_numbers:
        try:
            file_path = cs._locator.find_change_file(change_number)
            if file_path and os.path.exists(file_path):
                # TD-T10 修复：同时清理台帐条目
                project_path = cs._find_project_root_from_path(file_path)
                if project_path:
                    ledger_path = find_ledger_file(project_path)
                    if ledger_path:
                        ledger_updater.remove(ledger_path, change_number)
                os.remove(file_path)
            else:
                logger.warning(
                    "清理变更单失败：找不到文件 %s（可能 fixture 定位逻辑有缺陷）",
                    change_number,
                )
        except Exception as e:  # noqa: BLE001
            logger.warning(
                "清理变更单 %s 时抛异常: %s: %s",
                change_number,
                type(e).__name__,
                e,
            )
    _created_change_numbers.clear()


# ── 辅助函数 ──────────────────────────────────────────────


def _create_test_change(change_service: ChangeService, project_id: str) -> str:
    """创建一个测试变更单，返回 change_number

    记录到模块级列表，由 _cleanup_test_changes fixture 在测试后自动清理。
    """
    cr = change_service.create_change_request(
        project_id=project_id,
        domain="SCPT",
        business_nature="OPT",
        impact_scope=["SYSTEM"],
        applicant="gui_test",
        background="GUI 集成测试变更背景",
        necessity="验证 EditChangeDialog 弹窗和 Tab 切换",
    )
    _created_change_numbers.append(cr.change_number)
    return cr.change_number


def _find_edit_dialog(app, timeout_ms: int = 2000) -> QDialog | None:
    """查找已弹出的 EditChangeDialog"""
    import time

    deadline = time.time() + timeout_ms / 1000
    while time.time() < deadline:
        for w in app.topLevelWidgets():
            if (
                isinstance(w, QDialog)
                and w.isVisible()
                and "编辑变更单" in w.windowTitle()
            ):
                return w
        app.processEvents()
        QTest.qWait(50)
    return None


# ── 测试类 ────────────────────────────────────────────────


@pytest.mark.gui
class TestEditChangeDialogGUI:
    """EditChangeDialog GUI 集成测试"""

    def test_edit_dialog_popup_from_detail_panel(
        self, main_window, app, bug_recorder, workspace_root
    ):
        """测试从详情面板点击编辑按钮弹出 EditChangeDialog

        步骤：
        1. 导航到变更中心
        2. 创建测试变更单
        3. 选中变更单加载到详情面板
        4. 点击编辑按钮
        5. 验证 EditChangeDialog 弹窗打开
        """
        try:
            # 1. 导航到变更中心
            click_nav_page(main_window, "change_center", app)
            assert_stack_index(main_window, 3)

            view = main_window._change_center_view
            assert view is not None, "变更中心视图未初始化"

            # 2. 创建测试变更单
            cs = ChangeService(workspace_root)
            # 使用 SW-2026-008 项目（auto-pm 自身）作为测试项目
            change_number = _create_test_change(cs, "SW-2026-008")
            assert change_number.startswith("CHG-SCPT-"), f"变更单号异常: {change_number}"

            # 3. 加载变更单到详情面板
            view._detail_panel.load_change(change_number)
            app.processEvents()
            QTest.qWait(500)

            assert view._detail_panel._current_change is not None, "详情面板未加载变更单"

            # 4. 点击编辑按钮 → dialog.exec() 模态阻塞
            #    在 exec() 进入嵌套事件循环前注册 QTimer：
            #    - capture_and_verify: 在 exec() 事件循环中捕获弹窗、验证属性、reject() 让 exec() 返回
            #    - hard_timeout: 3s 兜底，若弹窗未弹出则强制 reject 任何阻塞对话框，避免卡死
            result: dict[str, object] = {"dialog": None, "verified": False, "error": None}

            def capture_and_verify(retries: int = 60) -> None:
                """在 exec() 嵌套事件循环中捕获并验证弹窗，然后 reject 让 exec() 返回"""
                if result["error"] is not None:
                    return
                for w in app.topLevelWidgets():
                    if (
                        isinstance(w, QDialog)
                        and w.isVisible()
                        and "编辑变更单" in w.windowTitle()
                    ):
                        result["dialog"] = w
                        try:
                            assert "编辑变更单" in w.windowTitle(), (
                                f"弹窗标题异常: {w.windowTitle()}"
                            )
                            assert isinstance(w, EditChangeDialog), "弹窗类型不是 EditChangeDialog"
                            result["verified"] = True
                        except AssertionError as e:
                            result["error"] = e
                        finally:
                            w.reject()  # 关键：让 dialog.exec() 返回，避免卡死
                        return
                if retries > 0:
                    QTimer.singleShot(50, lambda: capture_and_verify(retries - 1))

            def hard_timeout() -> None:
                """3s 兜底超时：截图保存现场 → 记录 bug → 强制 reject 避免卡死"""
                if result["dialog"] is None and result["error"] is None:
                    # 先截图保存现场（所有可见顶层窗口）
                    bug_recorder.capture_all_windows(
                        app=app,
                        test_name="test_edit_dialog_popup_from_detail_panel",
                        step="点击编辑按钮后 3s 超时兜底",
                        expected="3s 内弹出 EditChangeDialog 弹窗",
                        actual="3s 内未弹出 EditChangeDialog（可能卡死或未触发）",
                        severity="critical",
                    )
                    result["error"] = TimeoutError(
                        "点击编辑按钮后 3s 内未弹出 EditChangeDialog（可能卡死或未触发）"
                    )
                    for w in app.topLevelWidgets():
                        if isinstance(w, QDialog) and w.isVisible():
                            w.reject()

            QTimer.singleShot(0, capture_and_verify)
            QTimer.singleShot(3000, hard_timeout)
            view._detail_panel._on_edit_clicked()  # dialog.exec() 在此阻塞，直到 reject

            # exec() 已返回
            app.processEvents()
            QTest.qWait(200)

            # 5. 验证结果
            if result["error"] is not None:
                bug_recorder.record(
                    test_name="test_edit_dialog_popup_from_detail_panel",
                    step="点击编辑按钮后验证 EditChangeDialog 弹窗",
                    expected="EditChangeDialog 弹窗应打开，标题包含'编辑变更单'，类型为 EditChangeDialog",
                    actual=f"异常: {result['error']}",
                    severity="critical",
                )
                pytest.fail(f"EditChangeDialog 弹窗验证失败: {result['error']}")

            if result["dialog"] is None:
                bug_recorder.record(
                    test_name="test_edit_dialog_popup_from_detail_panel",
                    step="点击编辑按钮后查找 EditChangeDialog 弹窗",
                    expected="EditChangeDialog 弹窗应打开",
                    actual="未找到弹窗（可能未弹出或被立即关闭）",
                    severity="critical",
                )
                pytest.fail("EditChangeDialog 弹窗未弹出")

            assert result["verified"], "弹窗属性验证未通过"

        except Exception as e:
            bug_recorder.record(
                test_name="test_edit_dialog_popup_from_detail_panel",
                step="GUI 集成测试执行",
                expected="测试正常完成",
                actual=f"异常: {e}",
                severity="major",
                exc=e,
            )
            raise

    def test_edit_dialog_tab_structure(
        self, main_window, app, bug_recorder, workspace_root
    ):
        """测试 EditChangeDialog 的 Tab 结构（基本信息 + 影响分析）"""
        try:
            click_nav_page(main_window, "change_center", app)
            _view = main_window._change_center_view

            # 创建测试变更单
            cs = ChangeService(workspace_root)
            change_number = _create_test_change(cs, "SW-2026-008")

            # 直接构造 EditChangeDialog（绕过详情面板点击）
            dlg = EditChangeDialog(
                change_number=change_number,
                change_service=cs,
                parent=main_window,
            )
            dlg.show()
            app.processEvents()
            QTest.qWait(500)

            # 验证 Tab 结构
            tab_widget = dlg.findChild(QTabWidget)
            assert tab_widget is not None, "未找到 QTabWidget"

            tab_count = tab_widget.count()
            if tab_count != 2:
                bug_recorder.record(
                    test_name="test_edit_dialog_tab_structure",
                    step="验证 Tab 数量",
                    expected="Tab 数量为 2（基本信息 + 影响分析）",
                    actual=f"Tab 数量为 {tab_count}",
                    severity="major",
                    widget=dlg,
                )

            assert tab_count == 2, f"Tab 数量异常: {tab_count}"

            # 验证 Tab 标签
            tab0_text = tab_widget.tabText(0)
            tab1_text = tab_widget.tabText(1)
            assert tab0_text == "基本信息", f"Tab0 标签异常: {tab0_text}"
            assert tab1_text == "影响分析", f"Tab1 标签异常: {tab1_text}"

            dlg.reject()
            app.processEvents()
            QTest.qWait(200)

        except Exception as e:
            bug_recorder.record(
                test_name="test_edit_dialog_tab_structure",
                step="验证 Tab 结构",
                expected="Tab 结构正确（2 个 Tab：基本信息 + 影响分析）",
                actual=f"异常: {e}",
                severity="major",
                exc=e,
            )
            raise

    def test_tab_switching(
        self, main_window, app, bug_recorder, workspace_root
    ):
        """测试 Tab 切换功能（基本信息 ↔ 影响分析）"""
        try:
            click_nav_page(main_window, "change_center", app)
            _view = main_window._change_center_view

            cs = ChangeService(workspace_root)
            change_number = _create_test_change(cs, "SW-2026-008")

            dlg = EditChangeDialog(
                change_number=change_number,
                change_service=cs,
                parent=main_window,
            )
            dlg.show()
            app.processEvents()
            QTest.qWait(500)

            tab_widget = dlg._tab_widget
            assert tab_widget is not None

            # 初始应在 Tab0（基本信息）
            assert tab_widget.currentIndex() == 0, "初始 Tab 不是基本信息"

            # 切换到 Tab1（影响分析）
            tab_widget.setCurrentIndex(1)
            app.processEvents()
            QTest.qWait(300)
            assert tab_widget.currentIndex() == 1, "切换到影响分析 Tab 失败"

            # 验证影响分析 Tab 的控件存在
            assert dlg._risk_level_combo is not None, "风险等级下拉框不存在"
            assert dlg._mitigation_edit is not None, "缓解措施输入框不存在"
            assert dlg._propagation_chain_edit is not None, "传播链输入框不存在"
            assert dlg._constraint_table is not None, "约束影响表格不存在"
            assert dlg._domain_table is not None, "领域影响表格不存在"

            # 切换回 Tab0（基本信息）
            tab_widget.setCurrentIndex(0)
            app.processEvents()
            QTest.qWait(300)
            assert tab_widget.currentIndex() == 0, "切换回基本信息 Tab 失败"

            # 验证基本信息 Tab 的控件存在
            assert dlg._background_edit is not None, "变更背景输入框不存在"
            assert dlg._necessity_edit is not None, "变更必要性输入框不存在"
            assert dlg._references_edit is not None, "参考依据输入框不存在"
            assert dlg._urgency_combo is not None, "紧急程度下拉框不存在"
            assert dlg._planned_date_edit is not None, "计划日期选择器不存在"

            dlg.reject()
            app.processEvents()
            QTest.qWait(200)

        except Exception as e:
            bug_recorder.record(
                test_name="test_tab_switching",
                step="Tab 切换功能测试",
                expected="Tab 切换正常，控件存在",
                actual=f"异常: {e}",
                severity="major",
                exc=e,
            )
            raise

    def test_form_fields_loaded(
        self, main_window, app, bug_recorder, workspace_root
    ):
        """测试表单字段正确加载变更单数据"""
        try:
            click_nav_page(main_window, "change_center", app)

            cs = ChangeService(workspace_root)
            change_number = _create_test_change(cs, "SW-2026-008")

            dlg = EditChangeDialog(
                change_number=change_number,
                change_service=cs,
                parent=main_window,
            )
            dlg.show()
            app.processEvents()
            QTest.qWait(500)

            # 验证基本信息 Tab 字段已加载
            background = dlg._background_edit.toPlainText()
            necessity = dlg._necessity_edit.toPlainText()

            if not background:
                bug_recorder.record(
                    test_name="test_form_fields_loaded",
                    step="验证变更背景字段加载",
                    expected="变更背景应加载为'GUI 集成测试变更背景'",
                    actual="变更背景为空",
                    severity="major",
                    widget=dlg,
                )

            assert background == "GUI 集成测试变更背景", f"变更背景加载异常: '{background}'"
            assert necessity == "验证 EditChangeDialog 弹窗和 Tab 切换", f"变更必要性加载异常: '{necessity}'"

            # 验证影响分析 Tab 字段（默认值）
            assert dlg._risk_level_combo.currentData() == "none", "风险等级默认值异常"
            assert dlg._mitigation_edit.toPlainText() == "", "缓解措施默认值异常"
            # propagation_chain: 新建变更单经 parser 解析后为模板占位符（generator 模板含 [___________]）
            prop_chain = dlg._propagation_chain_edit.text()
            assert "[___________]" in prop_chain or prop_chain == "", (
                f"传播链默认值异常（应含占位符或为空）: {prop_chain!r}"
            )

            # 验证约束影响表格（5 行）
            assert dlg._constraint_table.rowCount() == 5, f"约束影响表格行数异常: {dlg._constraint_table.rowCount()}"

            # 验证领域影响表格（7 行，对应 DOMAINS）
            assert dlg._domain_table.rowCount() == 7, f"领域影响表格行数异常: {dlg._domain_table.rowCount()}"

            dlg.reject()
            app.processEvents()
            QTest.qWait(200)

        except Exception as e:
            bug_recorder.record(
                test_name="test_form_fields_loaded",
                step="验证表单字段加载",
                expected="所有字段正确加载",
                actual=f"异常: {e}",
                severity="major",
                exc=e,
            )
            raise

    def test_form_interaction(
        self, main_window, app, bug_recorder, workspace_root
    ):
        """测试表单交互（输入文本、切换下拉框、编辑表格）"""
        try:
            click_nav_page(main_window, "change_center", app)

            cs = ChangeService(workspace_root)
            change_number = _create_test_change(cs, "SW-2026-008")

            dlg = EditChangeDialog(
                change_number=change_number,
                change_service=cs,
                parent=main_window,
            )
            dlg.show()
            app.processEvents()
            QTest.qWait(500)

            # 1. 编辑基本信息 Tab 字段
            dlg._background_edit.setPlainText("修改后的变更背景")
            dlg._necessity_edit.setPlainText("修改后的必要性")
            dlg._references_edit.setPlainText("修改后的参考依据")
            app.processEvents()
            QTest.qWait(200)

            # 2. 切换紧急程度（URGENCY_LEVELS: normal=0, urgent=1, critical=2）
            urgency_idx = dlg._urgency_combo.findData("urgent")
            assert urgency_idx >= 0, "urgency_combo 未找到 'urgent' 选项"
            dlg._urgency_combo.setCurrentIndex(urgency_idx)  # urgent
            app.processEvents()
            QTest.qWait(200)

            # 3. 切换到影响分析 Tab
            dlg._tab_widget.setCurrentIndex(1)
            app.processEvents()
            QTest.qWait(300)

            # 4. 编辑影响分析字段
            dlg._risk_level_combo.setCurrentIndex(2)  # medium
            dlg._mitigation_edit.setPlainText("测试缓解措施")
            dlg._propagation_chain_edit.setText("SCPT -> PLC -> HMI")
            app.processEvents()
            QTest.qWait(200)

            # 5. 编辑约束影响表格（第 0 行设为"中"）
            combo = dlg._constraint_table.cellWidget(0, 1)
            assert isinstance(combo, QComboBox), "约束影响表格 cellWidget 不是 QComboBox"
            combo.setCurrentIndex(2)  # 中
            app.processEvents()
            QTest.qWait(200)

            # 6. 编辑领域影响表格（找到 SCPT 行设为"是"）
            #    DOMAINS 顺序为 ELEC/MECH/PLC/HMI/SCPT/DOCU/SAFE，SCPT 在第 4 行
            scpt_row = -1
            for row in range(dlg._domain_table.rowCount()):
                item = dlg._domain_table.item(row, 0)
                if item is not None and item.data(Qt.ItemDataRole.UserRole) == "SCPT":
                    scpt_row = row
                    break
            assert scpt_row >= 0, "领域影响表格未找到 SCPT 行"
            domain_combo = dlg._domain_table.cellWidget(scpt_row, 1)
            assert isinstance(domain_combo, QComboBox), "领域影响表格 cellWidget 不是 QComboBox"
            domain_combo.setCurrentIndex(1)  # 是
            app.processEvents()
            QTest.qWait(200)

            # 7. 验证 get_edit_data 返回修改后的值
            data = dlg.get_edit_data()
            assert data["background"] == "修改后的变更背景", f"background 异常: {data['background']}"
            assert data["necessity"] == "修改后的必要性", f"necessity 异常: {data['necessity']}"
            assert data["references"] == "修改后的参考依据", f"references 异常: {data['references']}"
            assert data["urgency"] == "urgent", f"urgency 异常: {data['urgency']}"
            assert data["risk_level"] == "medium", f"risk_level 异常: {data['risk_level']}"
            assert data["mitigation"] == "测试缓解措施", f"mitigation 异常: {data['mitigation']}"
            assert data["propagation_chain"] == "SCPT -> PLC -> HMI", f"propagation_chain 异常: {data['propagation_chain']}"
            assert data["constraint_impacts"]["范围"] == "中", f"constraint_impacts 异常: {data['constraint_impacts']}"
            assert data["domain_impacts"]["SCPT"]["affected"] is True, f"domain_impacts 异常: {data['domain_impacts']}"

            dlg.reject()
            app.processEvents()
            QTest.qWait(200)

        except Exception as e:
            bug_recorder.record(
                test_name="test_form_interaction",
                step="表单交互测试",
                expected="表单交互正常，get_edit_data 返回正确值",
                actual=f"异常: {e}",
                severity="major",
                exc=e,
            )
            raise

    def test_save_button_emits_signal(
        self, main_window, app, bug_recorder, workspace_root
    ):
        """测试保存按钮发射 change_updated 信号"""
        try:
            click_nav_page(main_window, "change_center", app)

            cs = ChangeService(workspace_root)
            change_number = _create_test_change(cs, "SW-2026-008")

            dlg = EditChangeDialog(
                change_number=change_number,
                change_service=cs,
                parent=main_window,
            )
            dlg.show()
            app.processEvents()
            QTest.qWait(500)

            # 修改背景字段
            dlg._background_edit.setPlainText("保存信号测试背景")
            app.processEvents()
            QTest.qWait(200)

            # 监听信号
            received: list[str] = []
            dlg.change_updated.connect(received.append)

            # 点击保存按钮
            ok_btn = dlg._button_box.button(QDialogButtonBox.StandardButton.Ok)
            ok_btn.click()
            app.processEvents()
            QTest.qWait(500)

            # 验证信号发射
            if not received:
                bug_recorder.record(
                    test_name="test_save_button_emits_signal",
                    step="点击保存按钮后验证信号",
                    expected="change_updated 信号应发射，received 包含 change_number",
                    actual=f"received 为空: {received}",
                    severity="critical",
                    widget=dlg,
                )

            assert received == [change_number], f"信号发射异常: {received}"

        except Exception as e:
            bug_recorder.record(
                test_name="test_save_button_emits_signal",
                step="保存按钮信号测试",
                expected="保存按钮点击后发射 change_updated 信号",
                actual=f"异常: {e}",
                severity="major",
                exc=e,
            )
            raise

    def test_cancel_button_closes_dialog(
        self, main_window, app, bug_recorder, workspace_root
    ):
        """测试取消按钮关闭弹窗"""
        try:
            click_nav_page(main_window, "change_center", app)

            cs = ChangeService(workspace_root)
            change_number = _create_test_change(cs, "SW-2026-008")

            dlg = EditChangeDialog(
                change_number=change_number,
                change_service=cs,
                parent=main_window,
            )
            dlg.show()
            app.processEvents()
            QTest.qWait(500)

            assert dlg.isVisible(), "弹窗未显示"

            # 点击取消按钮
            cancel_btn = dlg._button_box.button(QDialogButtonBox.StandardButton.Cancel)
            cancel_btn.click()
            app.processEvents()
            QTest.qWait(300)

            # 验证弹窗已关闭
            if dlg.isVisible():
                bug_recorder.record(
                    test_name="test_cancel_button_closes_dialog",
                    step="点击取消按钮后验证弹窗关闭",
                    expected="弹窗应关闭，isVisible() 返回 False",
                    actual="弹窗仍然可见",
                    severity="major",
                    widget=dlg,
                )

            assert not dlg.isVisible(), "取消按钮未关闭弹窗"

        except Exception as e:
            bug_recorder.record(
                test_name="test_cancel_button_closes_dialog",
                step="取消按钮测试",
                expected="取消按钮关闭弹窗",
                actual=f"异常: {e}",
                severity="major",
                exc=e,
            )
            raise

    @pytest.mark.skipif(
        not os.environ.get("GUI_VISIBLE"),
        reason="可见 GUI 演示模式，需设置 GUI_VISIBLE=1 环境变量启用",
    )
    def test_visible_demo(self, main_window, app, bug_recorder, workspace_root):
        """可见 GUI 演示：弹出 EditChangeDialog 并自动切换 Tab，让用户看到真实界面

        运行方式（PowerShell）：
            $env:GUI_VISIBLE=1; python -m pytest tests/gui/test_17_edit_change_dialog.py::TestEditChangeDialogGUI::test_visible_demo -v -s
        """
        try:
            # 1. 导航到变更中心并显示主窗口
            click_nav_page(main_window, "change_center", app)
            main_window.show()
            main_window.raise_()
            main_window.activateWindow()
            app.processEvents()
            QTest.qWait(800)

            view = main_window._change_center_view
            assert view is not None, "变更中心视图未初始化"

            # 2. 创建测试变更单并加载到详情面板
            cs = ChangeService(workspace_root)
            change_number = _create_test_change(cs, "SW-2026-008")
            view._detail_panel.load_change(change_number)
            app.processEvents()
            QTest.qWait(500)

            # 3. 演示流程：QTimer 驱动 Tab 切换，最后 reject 让 exec() 返回
            demo_steps: list[str] = []

            def run_demo_step(step: int) -> None:
                """按步骤演示：弹窗已弹出 → 切换影响分析 Tab → 切换回基本信息 → 关闭"""
                if step == 0:
                    # 弹窗刚弹出，停留在基本信息 Tab
                    demo_steps.append("基本信息 Tab 展示")
                elif step == 1:
                    # 切换到影响分析 Tab
                    dlg = _find_visible_edit_dialog(app)
                    assert dlg is not None, "演示步骤1: 未找到弹窗"
                    dlg._tab_widget.setCurrentIndex(1)
                    demo_steps.append("切换到影响分析 Tab")
                elif step == 2:
                    # 切换回基本信息 Tab
                    dlg = _find_visible_edit_dialog(app)
                    assert dlg is not None, "演示步骤2: 未找到弹窗"
                    dlg._tab_widget.setCurrentIndex(0)
                    demo_steps.append("切换回基本信息 Tab")
                elif step == 3:
                    # 关闭弹窗
                    dlg = _find_visible_edit_dialog(app)
                    assert dlg is not None, "演示步骤3: 未找到弹窗"
                    dlg.reject()
                    demo_steps.append("关闭弹窗")

                # 安排下一步（每步间隔 1.5 秒，让用户看清）
                if step < 3:
                    QTimer.singleShot(1500, lambda: run_demo_step(step + 1))

            def capture_and_demo(retries: int = 60) -> None:
                """捕获弹窗后启动演示流程"""
                dlg = _find_visible_edit_dialog(app)
                if dlg is None:
                    if retries > 0:
                        QTimer.singleShot(50, lambda: capture_and_demo(retries - 1))
                    return
                demo_steps.append(f"捕获弹窗: {dlg.windowTitle()}")
                QTimer.singleShot(1500, lambda: run_demo_step(0))

            def hard_timeout() -> None:
                """10s 兜底超时：截图保存现场 → 记录 bug → 强制 reject 避免卡死"""
                dlg = _find_visible_edit_dialog(app)
                if dlg is not None and dlg.isVisible():
                    # 先截图保存现场（所有可见顶层窗口）
                    bug_recorder.capture_all_windows(
                        app=app,
                        test_name="test_visible_demo",
                        step="可见 GUI 演示 10s 超时兜底",
                        expected="演示流程在 10s 内完成（弹窗弹出+Tab 切换+关闭）",
                        actual="10s 内演示未完成，弹窗仍可见（可能卡死或演示步骤异常）",
                        severity="critical",
                    )
                    dlg.reject()

            QTimer.singleShot(0, capture_and_demo)
            QTimer.singleShot(10000, hard_timeout)
            view._detail_panel._on_edit_clicked()  # dialog.exec() 阻塞，直到 reject

            app.processEvents()
            QTest.qWait(300)

            assert len(demo_steps) >= 4, (
                f"演示步骤不完整: {demo_steps}"
            )

        except Exception as e:
            bug_recorder.record(
                test_name="test_visible_demo",
                step="可见 GUI 演示",
                expected="弹窗弹出 + Tab 切换演示 + 关闭",
                actual=f"异常: {e}",
                severity="major",
                exc=e,
            )
            raise


def _find_visible_edit_dialog(app, timeout_ms: int = 100) -> QDialog | None:
    """查找已弹出的可见 EditChangeDialog"""
    for w in app.topLevelWidgets():
        if (
            isinstance(w, QDialog)
            and w.isVisible()
            and "编辑变更单" in w.windowTitle()
        ):
            return w
    return None
