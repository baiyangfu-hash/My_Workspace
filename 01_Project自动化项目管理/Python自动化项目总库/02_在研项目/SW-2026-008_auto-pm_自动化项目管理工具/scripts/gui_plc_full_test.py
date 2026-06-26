"""PLC 全功能 GUI 自动化驱动脚本

使用 QTest 程序化驱动 GUI，模拟用户操作所有 PLC 相关功能。
每一步操作自动截图，遇到异常记录为 Bug。

测试流程：
  1. 启动 GUI → 截图
  2. 导航树：点击 PLC 总库 / 阶段节点 / 功能节点
  3. 项目列表：搜索 / 业务线筛选 / 分组切换 / 视图切换
  4. 新建 PLC 项目（DJ-2026-099 测试项目）
  5. 进入项目工作区 → 概览 Tab
  6. 变更 Tab：创建变更单 → 状态全流程流转（draft→completed）
  7. 检查 Tab：执行检查 / 自动修复 / 标准化命名
  8. 文档 Tab：文档列表 / 模板信息
  9. 变更中心全局页
  10. 报告中心
  11. 系统设置
  12. 清理测试项目

运行方式：
  python scripts/gui_plc_full_test.py
"""

# ruff: noqa: E402, T201
from __future__ import annotations

import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

# 确保项目根目录在 sys.path 中
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QMessageBox,
    QPushButton,
    QWidget,
)

# ── 全局配置 ──────────────────────────────────────────────

WORKSPACE_ROOT = r"c:\Users\fubai\Desktop\My_Workspace"
SCREENSHOT_DIR = PROJECT_ROOT / "test_screenshots"
TEST_PROJECT_ID = "DJ-2026-099"
TEST_PROJECT_NAME = "GUI测试临时项目"

# Bug 记录
bugs: list[dict] = []
# 操作日志
op_log: list[str] = []


def log_op(msg: str) -> None:
    """记录操作日志"""
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    line = f"[{ts}] {msg}"
    op_log.append(line)
    print(line)


def record_bug(step: str, error: str, severity: str = "major") -> None:
    """记录 Bug"""
    bug = {
        "step": step,
        "error": error,
        "severity": severity,
        "timestamp": datetime.now().isoformat(),
    }
    bugs.append(bug)
    log_op(f"  *** BUG [{severity}]: {error}")


def screenshot(app: QApplication, name: str) -> None:
    """截取当前活跃窗口的截图"""
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    widget = app.activeWindow() or app.topLevelWidgets()[0] if app.topLevelWidgets() else None
    if widget is None:
        log_op(f"  截图跳过（无活跃窗口）: {name}")
        return
    pixmap = widget.grab()
    path = SCREENSHOT_DIR / f"{name}.png"
    pixmap.save(str(path))
    log_op(f"  截图已保存: {path}")


def find_child(widget: QWidget, object_name: str) -> QWidget | None:
    """按 objectName 查找子控件"""
    return widget.findChild(QWidget, object_name)


def find_children(widget: QWidget, class_type: type) -> list:
    """按类型查找所有子控件"""
    return widget.findChildren(class_type)


def click_button(btn: QPushButton, label: str = "") -> None:
    """安全点击按钮"""
    if btn is None:
        raise RuntimeError(f"按钮未找到: {label}")
    if not btn.isEnabled():
        log_op(f"  按钮已禁用，跳过点击: {label}")
        return
    btn.click()


def set_combo_by_data(combo: QComboBox, data_value: str, label: str = "") -> None:
    """通过 data 值设置 ComboBox 选中项"""
    if combo is None:
        raise RuntimeError(f"下拉框未找到: {label}")
    for i in range(combo.count()):
        if combo.itemData(i) == data_value:
            combo.setCurrentIndex(i)
            return
    raise RuntimeError(f"下拉框未找到选项 {data_value}: {label}")


def set_combo_by_text(combo: QComboBox, text: str, label: str = "") -> None:
    """通过显示文本设置 ComboBox 选中项"""
    if combo is None:
        raise RuntimeError(f"下拉框未找到: {label}")
    index = combo.findText(text)
    if index >= 0:
        combo.setCurrentIndex(index)
        return
    raise RuntimeError(f"下拉框未找到文本 '{text}': {label}")


def process_events(app: QApplication, ms: int = 200) -> None:
    """处理事件队列并等待"""
    app.processEvents()
    QTest.qWait(ms)


def find_and_click_dialog_button(app: QApplication, button_text: str, timeout_ms: int = 3000) -> QDialog | None:
    """查找当前弹出的对话框并点击指定按钮"""
    deadline = time.time() + timeout_ms / 1000
    while time.time() < deadline:
        for widget in app.topLevelWidgets():
            if isinstance(widget, QDialog) and widget.isVisible():
                # 查找按钮
                for btn in widget.findChildren(QPushButton):
                    if button_text in btn.text():
                        btn.click()
                        process_events(app, 300)
                        return widget
        process_events(app, 100)
    return None


# ── 测试步骤 ──────────────────────────────────────────────

def step_01_launch_gui(app: QApplication) -> object:
    """步骤1: 启动 GUI 主窗口"""
    log_op("步骤1: 启动 GUI 主窗口")
    try:
        from auto_pm.ui.main_window import MainWindow
        window = MainWindow(workspace_root=WORKSPACE_ROOT)
        window.show()
        process_events(app, 1000)
        screenshot(app, "01_main_window")
        log_op("  GUI 启动成功")
        return window
    except Exception as e:
        record_bug("启动GUI", str(e), "critical")
        raise


def step_02_navigation_tree(app: QApplication, window) -> None:
    """步骤2: 导航树操作"""
    log_op("步骤2: 导航树操作")
    nav_tree = find_child(window, "navTree")
    if nav_tree is None:
        record_bug("导航树", "navTree 控件未找到", "critical")
        return

    # 2.1 点击 PLC 总库节点
    log_op("  2.1 点击 PLC 总库节点")
    try:
        for i in range(nav_tree.topLevelItemCount()):
            item = nav_tree.topLevelItem(i)
            if "PLC" in item.text(0):
                nav_tree.setCurrentItem(item)
                nav_tree.itemClicked.emit(item, 0)
                process_events(app, 500)
                break
        screenshot(app, "02_nav_plc_stack")
    except Exception as e:
        record_bug("导航树-PLC总库", str(e), "minor")

    # 2.2 点击 PLC 在研项目阶段节点
    log_op("  2.2 点击 PLC 在研项目阶段节点")
    try:
        for i in range(nav_tree.topLevelItemCount()):
            item = nav_tree.topLevelItem(i)
            if "PLC" in item.text(0):
                for j in range(item.childCount()):
                    child = item.child(j)
                    if "在研" in child.text(0):
                        nav_tree.setCurrentItem(child)
                        nav_tree.itemClicked.emit(child, 0)
                        process_events(app, 500)
                        break
        screenshot(app, "02_nav_plc_developing")
    except Exception as e:
        record_bug("导航树-PLC在研", str(e), "minor")

    # 2.3 点击功能节点
    for page_name, label in [
        ("all_projects", "全部项目"),
        ("change_center", "变更中心"),
        ("report", "报告中心"),
        ("settings", "系统设置"),
    ]:
        log_op(f"  2.3 点击功能节点: {label}")
        try:
            for i in range(nav_tree.topLevelItemCount()):
                item = nav_tree.topLevelItem(i)
                node_data = item.data(0, Qt.UserRole)
                if node_data and getattr(node_data, "page_id", None) == page_name:
                    nav_tree.setCurrentItem(item)
                    nav_tree.itemClicked.emit(item, 0)
                    process_events(app, 500)
                    break
                # 检查子节点
                for j in range(item.childCount()):
                    child = item.child(j)
                    child_data = child.data(0, Qt.UserRole)
                    if child_data and getattr(child_data, "page_id", None) == page_name:
                        nav_tree.setCurrentItem(child)
                        nav_tree.itemClicked.emit(child, 0)
                        process_events(app, 500)
                        break
            screenshot(app, f"02_nav_{page_name}")
        except Exception as e:
            record_bug(f"导航树-{label}", str(e), "minor")

    # 最后切回项目列表
    try:
        for i in range(nav_tree.topLevelItemCount()):
            item = nav_tree.topLevelItem(i)
            node_data = item.data(0, Qt.UserRole)
            if node_data and getattr(node_data, "page_id", None) == "all_projects":
                nav_tree.setCurrentItem(item)
                nav_tree.itemClicked.emit(item, 0)
                process_events(app, 500)
                break
    except Exception:
        pass


def step_03_project_list(app: QApplication, window) -> None:
    """步骤3: 项目列表操作"""
    log_op("步骤3: 项目列表操作")

    # 3.1 搜索框
    log_op("  3.1 搜索框输入 'DJ'")
    try:
        search_edit = window._search_edit
        search_edit.setText("DJ")
        process_events(app, 500)
        screenshot(app, "03_search_dj")
        search_edit.clear()
        process_events(app, 300)
    except Exception as e:
        record_bug("项目列表-搜索", str(e), "minor")

    # 3.2 业务线筛选
    log_op("  3.2 业务线筛选切换")
    try:
        combo = window._business_combo
        for target_text in ["单机设备 (DJ)", "软件开发 (SW)", "全部业务线"]:
            idx = combo.findText(target_text)
            if idx >= 0:
                combo.setCurrentIndex(idx)
                process_events(app, 500)
        screenshot(app, "03_business_line_filter")
    except Exception as e:
        record_bug("项目列表-业务线筛选", str(e), "minor")

    # 3.3 视图切换（卡片/列表）
    log_op("  3.3 视图切换")
    try:
        list_view = window._project_list_view
        view_controls = list_view._view_controls
        # 切换到列表视图
        view_controls._list_btn.click()
        process_events(app, 500)
        screenshot(app, "03_list_view")
        # 切换回卡片视图
        view_controls._card_btn.click()
        process_events(app, 500)
        screenshot(app, "03_card_view")
    except Exception as e:
        record_bug("项目列表-视图切换", str(e), "minor")

    # 3.4 分组模式切换
    log_op("  3.4 分组模式切换")
    try:
        list_view = window._project_list_view
        view_controls = list_view._view_controls
        for mode_text in ["总库+业务线", "总库+阶段", "业务线", "阶段"]:
            combo = view_controls._group_combo
            idx = combo.findText(mode_text)
            if idx >= 0:
                combo.setCurrentIndex(idx)
                process_events(app, 500)
        screenshot(app, "03_group_mode")
        # 恢复默认
        combo = view_controls._group_combo
        idx = combo.findText("总库+业务线")
        if idx >= 0:
            combo.setCurrentIndex(idx)
        process_events(app, 300)
    except Exception as e:
        record_bug("项目列表-分组切换", str(e), "minor")


def step_04_create_plc_project(app: QApplication, window) -> None:
    """步骤4: 新建 PLC 测试项目"""
    log_op("步骤4: 新建 PLC 测试项目")
    try:
        # 点击工具栏"新建"按钮的 PLC 项目菜单项
        window._on_new_project("plc")
        process_events(app, 500)

        # 查找 NewProjectDialog
        dialog = None
        for w in app.topLevelWidgets():
            if isinstance(w, QDialog) and w.isVisible() and "新建项目" in w.windowTitle():
                dialog = w
                break

        if dialog is None:
            record_bug("新建项目", "对话框未弹出", "major")
            return

        # 填写表单
        dialog._id_edit.setText(TEST_PROJECT_ID)
        process_events(app, 100)
        dialog._name_edit.setText(TEST_PROJECT_NAME)
        process_events(app, 100)

        # 确认技术栈为 PLC
        set_combo_by_data(dialog._stack_combo, "plc", "技术栈")
        process_events(app, 100)

        # 勾选 dry-run 先预览
        dialog._dry_run_check.setChecked(True)
        process_events(app, 100)

        # 点击确定（预览）
        ok_btn = dialog._button_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_btn.click()
        process_events(app, 500)

        # 处理预览弹窗
        for w in app.topLevelWidgets():
            if isinstance(w, QMessageBox) and w.isVisible():
                w.accept()
                process_events(app, 300)

        # 取消对话框，重新创建（实际创建）
        dialog.reject()
        process_events(app, 300)

        # 重新打开对话框
        window._on_new_project("plc")
        process_events(app, 500)

        dialog = None
        for w in app.topLevelWidgets():
            if isinstance(w, QDialog) and w.isVisible() and "新建项目" in w.windowTitle():
                dialog = w
                break

        if dialog is None:
            record_bug("新建项目(第二次)", "对话框未弹出", "major")
            return

        # 填写表单
        dialog._id_edit.setText(TEST_PROJECT_ID)
        process_events(app, 100)
        dialog._name_edit.setText(TEST_PROJECT_NAME)
        process_events(app, 100)
        set_combo_by_data(dialog._stack_combo, "plc", "技术栈")
        process_events(app, 100)
        # 不勾选 dry-run
        dialog._dry_run_check.setChecked(False)
        process_events(app, 100)

        # 点击确定
        ok_btn = dialog._button_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_btn.click()
        process_events(app, 1000)

        # 处理可能的错误弹窗
        for w in app.topLevelWidgets():
            if isinstance(w, QMessageBox) and w.isVisible():
                msg_text = w.text()
                if "已存在" in msg_text:
                    log_op(f"  项目已存在，跳过创建: {msg_text}")
                    w.accept()
                    record_bug("新建项目", f"项目已存在: {msg_text}", "minor")
                else:
                    w.accept()
                process_events(app, 300)

        screenshot(app, "04_project_created")

        # 刷新列表
        window._on_refresh()
        process_events(app, 1000)

    except Exception as e:
        record_bug("新建PLC项目", str(e), "major")


def step_05_enter_workspace(app: QApplication, window) -> None:
    """步骤5: 进入项目工作区"""
    log_op("步骤5: 进入项目工作区")
    try:
        # 在项目列表中查找并点击测试项目
        list_view = window._project_list_view
        project = list_view.get_project(TEST_PROJECT_ID)

        if project is None:
            # 尝试搜索
            window._search_edit.setText(TEST_PROJECT_ID)
            process_events(app, 500)
            project = list_view.get_project(TEST_PROJECT_ID)

        if project is not None:
            window._on_project_selected(TEST_PROJECT_ID)
            process_events(app, 800)
            screenshot(app, "05_workspace_overview")
        else:
            # 尝试使用已有项目
            projects = list_view._all_projects
            plc_projects = [p for p in projects if p.stack == "plc"]
            if plc_projects:
                proj = plc_projects[0]
                log_op(f"  测试项目未找到，使用已有PLC项目: {proj.project_id}")
                window._on_project_selected(proj.project_id)
                process_events(app, 800)
                screenshot(app, "05_workspace_existing")
            else:
                record_bug("进入工作区", "无PLC项目可进入", "major")
                return

    except Exception as e:
        record_bug("进入工作区", str(e), "major")


def step_06_change_tab(app: QApplication, window) -> None:
    """步骤6: 变更 Tab - 创建变更单并全流程流转"""
    log_op("步骤6: 变更 Tab - 创建变更单并全流程流转")
    try:
        workspace_view = window._workspace_view
        if workspace_view._project is None:
            log_op("  跳过：未进入项目工作区")
            return

        # 切换到变更 Tab
        change_idx = workspace_view._tab_indices.get("change", -1)
        if change_idx < 0:
            record_bug("变更Tab", "Tab索引未找到", "major")
            return
        workspace_view._tab_widget.setCurrentIndex(change_idx)
        process_events(app, 500)
        screenshot(app, "06_change_tab")

        change_tab = workspace_view._change_tab
        if change_tab is None:
            record_bug("变更Tab", "ChangeTab 未初始化", "major")
            return

        # 6.1 创建变更单
        log_op("  6.1 创建变更单")
        change_tab._on_create_change()
        process_events(app, 500)

        # 查找 CreateChangeDialog
        dialog = None
        for w in app.topLevelWidgets():
            if isinstance(w, QDialog) and w.isVisible() and "创建变更单" in w.windowTitle():
                dialog = w
                break

        if dialog is None:
            record_bug("创建变更单", "对话框未弹出", "major")
            return

        # 填写表单
        project_id = workspace_view._project.project_id
        set_combo_by_data(dialog._project_combo, project_id, "项目")
        process_events(app, 100)
        set_combo_by_data(dialog._domain_combo, "PLC", "领域")
        process_events(app, 100)
        set_combo_by_data(dialog._nature_combo, "DEF", "性质")
        process_events(app, 100)
        set_combo_by_data(dialog._scope_combo, "LOCAL", "范围")
        process_events(app, 100)
        dialog._applicant_edit.setText("auto_test")
        process_events(app, 100)
        dialog._background_edit.setPlainText("GUI自动化测试：验证变更单创建功能")
        process_events(app, 100)

        screenshot(app, "06_create_change_form")

        # 点击创建
        ok_btn = dialog._button_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_btn.click()
        process_events(app, 1000)

        # 处理可能的错误弹窗
        for w in app.topLevelWidgets():
            if isinstance(w, QMessageBox) and w.isVisible():
                record_bug("创建变更单", f"创建失败: {w.text()}", "major")
                w.accept()
                process_events(app, 300)

        screenshot(app, "06_change_created")

        # 6.2 状态全流程流转
        log_op("  6.2 状态全流程流转")
        transitions = [
            ("submitted", "已提交"),
            ("under_review", "审核中"),
            ("approved", "已批准"),
            ("implementing", "实施中"),
            ("pending_acceptance", "待验收"),
            ("accepting", "验收中"),
            ("completed", "已完成"),
        ]

        for target_status, target_label in transitions:
            log_op(f"    流转: → {target_label} ({target_status})")
            try:
                # 获取当前变更单卡片
                cards = change_tab._get_cards()
                if not cards:
                    log_op("      无变更单卡片，跳过流转")
                    break

                card = cards[0]  # 取第一个（最新创建的）
                card._transition_btn.click()
                process_events(app, 500)

                # 如果有菜单弹出（多个目标状态可选），选择目标
                # 如果只有一个目标状态，直接弹出 TransitionDialog
                dialog = None
                for w in app.topLevelWidgets():
                    if isinstance(w, QDialog) and w.isVisible() and "流转" in w.windowTitle():
                        dialog = w
                        break

                if dialog is not None:
                    # 填写流转对话框
                    dialog._approver_edit.setText("auto_test")
                    process_events(app, 100)
                    dialog._comment_edit.setPlainText(f"自动测试流转至{target_label}")
                    process_events(app, 100)

                    # completed 状态需要验证结论
                    if target_status == "completed":
                        dialog._verification_edit.setPlainText("全部通过")
                        process_events(app, 100)

                    screenshot(app, f"06_transition_{target_status}")

                    # 点击确认流转
                    ok_btn = dialog._button_box.button(QDialogButtonBox.StandardButton.Ok)
                    ok_btn.click()
                    process_events(app, 1000)

                    # 检查是否有错误弹窗
                    for w in app.topLevelWidgets():
                        if isinstance(w, QMessageBox) and w.isVisible():
                            error_text = w.text()
                            record_bug(
                                f"状态流转→{target_label}",
                                f"流转失败: {error_text}",
                                "major" if target_status == "completed" else "minor",
                            )
                            w.accept()
                            process_events(app, 300)
                else:
                    # 可能弹出了右键菜单，等待一下
                    process_events(app, 500)

                screenshot(app, f"06_after_{target_status}")

            except Exception as e:
                record_bug(f"状态流转→{target_label}", str(e), "major")

    except Exception as e:
        record_bug("变更Tab", str(e), "major")


def step_07_check_tab(app: QApplication, window) -> None:
    """步骤7: 检查 Tab - PLC 项目结构检查"""
    log_op("步骤7: 检查 Tab - PLC 项目结构检查")
    try:
        workspace_view = window._workspace_view
        if workspace_view._project is None:
            log_op("  跳过：未进入项目工作区")
            return

        # 切换到检查 Tab
        check_idx = workspace_view._tab_indices.get("check", -1)
        if check_idx < 0:
            record_bug("检查Tab", "Tab索引未找到", "major")
            return
        workspace_view._tab_widget.setCurrentIndex(check_idx)
        process_events(app, 500)
        screenshot(app, "07_check_tab_empty")

        check_tab = workspace_view._check_tab
        if check_tab is None:
            record_bug("检查Tab", "CheckTab 未初始化", "major")
            return

        # 7.1 执行检查
        log_op("  7.1 执行检查")
        try:
            check_tab._check_btn.click()
            process_events(app, 1000)
            screenshot(app, "07_check_result")
        except Exception as e:
            record_bug("执行检查", str(e), "major")

        # 7.2 自动修复（预览）
        log_op("  7.2 自动修复预览")
        try:
            check_tab._repair_btn.click()
            process_events(app, 1000)
            screenshot(app, "07_repair_preview")
        except Exception as e:
            record_bug("自动修复预览", str(e), "minor")

        # 7.3 标准化命名（预览）
        log_op("  7.3 标准化命名预览")
        try:
            check_tab._standardize_btn.click()
            process_events(app, 1000)
            screenshot(app, "07_standardize_preview")
        except Exception as e:
            record_bug("标准化命名预览", str(e), "minor")

    except Exception as e:
        record_bug("检查Tab", str(e), "major")


def step_08_doc_tab(app: QApplication, window) -> None:
    """步骤8: 文档 Tab"""
    log_op("步骤8: 文档 Tab")
    try:
        workspace_view = window._workspace_view
        if workspace_view._project is None:
            log_op("  跳过：未进入项目工作区")
            return

        # 切换到文档 Tab
        doc_idx = workspace_view._tab_indices.get("doc", -1)
        if doc_idx < 0:
            record_bug("文档Tab", "Tab索引未找到", "major")
            return
        workspace_view._tab_widget.setCurrentIndex(doc_idx)
        process_events(app, 500)
        screenshot(app, "08_doc_tab")

        doc_tab = workspace_view._doc_tab
        if doc_tab is None:
            record_bug("文档Tab", "DocTab 未初始化", "minor")
            return

        # 8.1 检查文档树
        log_op("  8.1 检查文档树")
        cat_items = doc_tab._get_category_items()
        log_op(f"  文档分类数: {len(cat_items)}")
        for cat in cat_items:
            docs = doc_tab._get_documents_in_category(cat)
            log_op(f"    {cat.text(0)}: {len(docs)} 个文档")

        # 8.2 模板信息
        log_op("  8.2 模板信息")
        template_name = doc_tab._template_name_label.text()
        template_version = doc_tab._template_version_label.text()
        log_op(f"  模板: {template_name}, 版本: {template_version}")

        # 8.3 检查更新（预览）
        log_op("  8.3 检查模板更新")
        try:
            doc_tab._check_btn.click()
            process_events(app, 1000)
        except Exception as e:
            record_bug("检查模板更新", str(e), "minor")

        screenshot(app, "08_doc_tab_final")

    except Exception as e:
        record_bug("文档Tab", str(e), "minor")


def step_09_change_center(app: QApplication, window) -> None:
    """步骤9: 变更中心全局页"""
    log_op("步骤9: 变更中心全局页")
    try:
        # 通过导航树切换到变更中心
        window._on_page_switch("change_center")
        process_events(app, 800)
        screenshot(app, "09_change_center")

        change_center = window._change_center_view
        if change_center is None:
            record_bug("变更中心", "ChangeCenterView 未初始化", "major")
            return

        # 9.1 查看变更单列表
        log_op("  9.1 查看变更单列表")
        list_panel = change_center._list_panel
        if list_panel is not None:
            # 尝试切换状态 Tab
            for tab_btn in find_children(list_panel, QPushButton):
                if tab_btn.isCheckable():
                    tab_btn.click()
                    process_events(app, 300)
            screenshot(app, "09_change_center_tabs")

        # 9.2 创建变更单（从变更中心）
        log_op("  9.2 从变更中心创建变更单")
        try:
            change_center._create_btn.click()
            process_events(app, 500)

            # 关闭对话框（不实际创建）
            for w in app.topLevelWidgets():
                if isinstance(w, QDialog) and w.isVisible() and "创建变更单" in w.windowTitle():
                    w.reject()
                    process_events(app, 300)
                    break
        except Exception as e:
            record_bug("变更中心-创建变更单", str(e), "minor")

    except Exception as e:
        record_bug("变更中心", str(e), "major")


def step_10_report_center(app: QApplication, window) -> None:
    """步骤10: 报告中心"""
    log_op("步骤10: 报告中心")
    try:
        window._on_page_switch("report")
        process_events(app, 800)
        screenshot(app, "10_report_center")

        report_page = window._report_page
        if report_page is None:
            record_bug("报告中心", "ReportPage 未初始化", "minor")
            return

        # 检查统计卡片
        log_op("  检查报告统计卡片")
        process_events(app, 300)

    except Exception as e:
        record_bug("报告中心", str(e), "minor")


def step_11_settings(app: QApplication, window) -> None:
    """步骤11: 系统设置"""
    log_op("步骤11: 系统设置")
    try:
        window._on_page_switch("settings")
        process_events(app, 800)
        screenshot(app, "11_settings")

        settings_page = window._settings_page
        if settings_page is None:
            record_bug("系统设置", "SettingsPage 未初始化", "minor")
            return

        # 11.1 检查设置信息
        log_op("  11.1 检查设置信息")
        ws_path = settings_page.workspace_edit.text()
        db_path = settings_page.db_path_label.text()
        proj_count = settings_page.project_count_label.text()
        change_count = settings_page.change_count_label.text()
        log_op(f"  工作空间: {ws_path}")
        log_op(f"  {db_path}")
        log_op(f"  {proj_count}")
        log_op(f"  {change_count}")

        # 11.2 修改扫描深度
        log_op("  11.2 修改扫描深度")
        settings_page.depth_spin.setValue(3)
        process_events(app, 300)

        # 11.3 重建索引
        log_op("  11.3 重建索引（点击按钮，弹窗选否）")
        try:
            settings_page.rebuild_button.click()
            process_events(app, 500)
            # 弹窗选否（不实际执行）
            for w in app.topLevelWidgets():
                if isinstance(w, QMessageBox) and w.isVisible():
                    w.reject()
                    process_events(app, 300)
                    break
        except Exception as e:
            record_bug("重建索引", str(e), "minor")

        screenshot(app, "11_settings_final")

    except Exception as e:
        record_bug("系统设置", str(e), "minor")


def step_12_toolbar_actions(app: QApplication, window) -> None:
    """步骤12: 工具栏操作"""
    log_op("步骤12: 工具栏操作")

    # 12.1 同步缓存
    log_op("  12.1 同步缓存")
    try:
        window._on_sync()
        process_events(app, 1000)
        screenshot(app, "12_sync_cache")
    except Exception as e:
        record_bug("同步缓存", str(e), "minor")

    # 12.2 刷新列表
    log_op("  12.2 刷新列表")
    try:
        window._on_refresh()
        process_events(app, 1000)
        screenshot(app, "12_refresh_list")
    except Exception as e:
        record_bug("刷新列表", str(e), "minor")

    # 12.3 状态栏检查
    log_op("  12.3 状态栏检查")
    try:
        ws_text = window._status_workspace.text()
        proj_text = window._status_project.text()
        db_text = window._status_db.text()
        log_op(f"  状态栏: {ws_text} | {proj_text} | {db_text}")
    except Exception as e:
        record_bug("状态栏", str(e), "minor")


def step_13_cleanup(app: QApplication, window) -> None:
    """步骤13: 清理测试项目"""
    log_op("步骤13: 清理测试项目（仅记录，不自动删除）")
    try:
        # 回到项目列表
        window._on_back_to_list()
        process_events(app, 500)

        # 检查测试项目是否存在
        list_view = window._project_list_view
        project = list_view.get_project(TEST_PROJECT_ID)
        if project:
            log_op(f"  测试项目 {TEST_PROJECT_ID} 存在，路径: {project.path}")
            log_op("  注意：测试项目未自动删除，需手动清理")
        else:
            log_op(f"  测试项目 {TEST_PROJECT_ID} 未找到")
    except Exception as e:
        record_bug("清理测试项目", str(e), "minor")


# ── Bug 报告生成 ──────────────────────────────────────────

def generate_bug_report() -> str:
    """生成 Bug 报告"""
    lines = [
        "=" * 60,
        "PLC 全功能 GUI 测试 - Bug 报告",
        f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"工作空间: {WORKSPACE_ROOT}",
        f"测试项目: {TEST_PROJECT_ID}",
        "=" * 60,
        "",
    ]

    if not bugs:
        lines.append("未发现 Bug！")
    else:
        lines.append(f"共发现 {len(bugs)} 个问题：")
        lines.append("")
        for i, bug in enumerate(bugs, 1):
            lines.append(f"Bug #{i}:")
            lines.append(f"  步骤: {bug['step']}")
            lines.append(f"  严重度: {bug['severity']}")
            lines.append(f"  错误: {bug['error']}")
            lines.append(f"  时间: {bug['timestamp']}")
            lines.append("")

    # 统计
    critical = sum(1 for b in bugs if b["severity"] == "critical")
    major = sum(1 for b in bugs if b["severity"] == "major")
    minor = sum(1 for b in bugs if b["severity"] == "minor")

    lines.append("-" * 40)
    lines.append(f"严重: {critical} | 主要: {major} | 次要: {minor}")
    lines.append("")

    return "\n".join(lines)


# ── 主流程 ────────────────────────────────────────────────

def main() -> None:
    """主测试流程"""
    print("=" * 60)
    print("PLC 全功能 GUI 自动化测试")
    print("=" * 60)

    # 创建 QApplication
    app = QApplication.instance() or QApplication(sys.argv)

    window = None

    try:
        # 步骤1: 启动 GUI
        window = step_01_launch_gui(app)

        # 步骤2: 导航树
        step_02_navigation_tree(app, window)

        # 步骤3: 项目列表
        step_03_project_list(app, window)

        # 步骤4: 新建 PLC 项目
        step_04_create_plc_project(app, window)

        # 步骤5: 进入项目工作区
        step_05_enter_workspace(app, window)

        # 步骤6: 变更 Tab
        step_06_change_tab(app, window)

        # 步骤7: 检查 Tab
        step_07_check_tab(app, window)

        # 步骤8: 文档 Tab
        step_08_doc_tab(app, window)

        # 步骤9: 变更中心
        step_09_change_center(app, window)

        # 步骤10: 报告中心
        step_10_report_center(app, window)

        # 步骤11: 系统设置
        step_11_settings(app, window)

        # 步骤12: 工具栏操作
        step_12_toolbar_actions(app, window)

        # 步骤13: 清理
        step_13_cleanup(app, window)

    except Exception as e:
        record_bug("主流程", f"未捕获异常: {e}\n{traceback.format_exc()}", "critical")

    # 最终截图
    if window is not None:
        screenshot(app, "99_final_state")

    # 生成 Bug 报告
    report = generate_bug_report()
    report_path = PROJECT_ROOT / "test_screenshots" / "bug_report.txt"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")

    print("\n" + report)
    print(f"\nBug 报告已保存: {report_path}")
    print(f"截图目录: {SCREENSHOT_DIR}")

    # 写操作日志
    log_path = PROJECT_ROOT / "test_screenshots" / "operation_log.txt"
    log_path.write_text("\n".join(op_log), encoding="utf-8")
    print(f"操作日志已保存: {log_path}")

    # 关闭窗口
    if window is not None:
        window.close()

    sys.exit(0)


if __name__ == "__main__":
    main()
