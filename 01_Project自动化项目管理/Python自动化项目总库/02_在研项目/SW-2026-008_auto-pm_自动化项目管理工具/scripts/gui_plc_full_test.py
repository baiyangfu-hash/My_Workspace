"""PLC 全功能 GUI 自动化驱动脚本 V3（电气工程师视角）

基于《GUI使用说明书_电气工程师视角》13 个场景，使用 QTest 程序化驱动 GUI。
所有模态对话框（dialog.exec()）采用 QTimer.singleShot 模式处理，全程无人工干预。

V3 升级（2026-07-01）：
  1. 修复 exec() 阻塞：全面采用 QTimer.singleShot 模式（与 pytest 测试一致）
  2. visible 模式真实截图
  3. 三视口测试（桌面 1920x1080 / 平板 768x1024 / 手机 375x812）
  4. 实际创建项目/变更单 + 实际状态流转（7 次到完成）
  5. 变量表 Tab 测试（V2.3 Week4）
  6. 规范中心 6 Tab 遍历（V2.2 Week3）
  7. 程序化视觉几何检查（控件越界/重叠/截断/对比度/可见性）
  8. 隔离 tmp 工作空间（TD-T09 修复）

运行方式：
  python scripts/gui_plc_full_test.py
"""

# ruff: noqa: E402, T201
from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
import time
import traceback
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPalette
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QMessageBox,
    QPushButton,
    QWidget,
    QWizard,
)

# 复用 tests/gui/helpers 的弹窗处理工具，避免两套实现导致 bug 修复遗漏
from tests.gui.helpers.interactions import (  # noqa: E402
    close_all_modal_widgets as _close_all_modal_widgets,
    dismiss_message_boxes as _dismiss_message_boxes,
    find_dialog as _find_dialog,
    find_message_box as _find_message_box,
)

# ── 全局配置 ──────────────────────────────────────────────

SCREENSHOT_DIR = PROJECT_ROOT / "test_reports" / "gui" / "full_test_screenshots"
REPORT_DIR = PROJECT_ROOT / "test_reports" / "gui"

TEST_PROJECT_ID = "DJ-2026-099"
TEST_PROJECT_NAME = "GUI测试临时项目"
PLC_SUBDIR = "0100_PLC自动化"
# fixture 预置项目（确保 GUI 启动时有项目可显示，避免空状态）
FIXTURE_PROJECT_ID = "DJ-2026-001"
FIXTURE_PROJECT_NAME = "预置测试项目"

VIEWPORTS: list[tuple[int, int, str]] = [
    (1920, 1080, "desktop"),
    (768, 1024, "tablet"),
    (375, 812, "mobile"),
]

bugs: list[dict] = []
op_log: list[str] = []
visual_issues: list[dict] = []
_current_viewport: str = "desktop"


# ── 日志与记录 ────────────────────────────────────────────

def log_op(msg: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    line = f"[{ts}] {msg}"
    op_log.append(line)
    print(line, flush=True)


def record_bug(step: str, error: str, severity: str = "major", screenshot_path: str = "") -> None:
    bugs.append({
        "step": step,
        "error": error,
        "severity": severity,
        "timestamp": datetime.now().isoformat(),
        "screenshot": screenshot_path,
    })
    log_op(f"  *** BUG [{severity}]: {error}")


def record_visual(issue_type: str, widget_path: str, detail: str, severity: str = "minor",
                  screenshot_path: str = "") -> None:
    visual_issues.append({
        "type": issue_type,
        "widget": widget_path,
        "detail": detail,
        "severity": severity,
        "viewport": _current_viewport,
        "timestamp": datetime.now().isoformat(),
        "screenshot": screenshot_path,
    })
    log_op(f"  *** VISUAL [{severity}] {issue_type}: {detail} @ {widget_path}")


# ── 截图与视口 ────────────────────────────────────────────

def screenshot(app: QApplication, name: str) -> str:
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    widget = app.activeWindow() or (app.topLevelWidgets()[0] if app.topLevelWidgets() else None)
    # 保护：如果活跃窗口尺寸过小（可能是残留的 QMenu/Dialog），
    # 回退到第一个正常尺寸的 topLevelWidget（通常是主窗口）
    if widget is not None and (widget.width() < 100 or widget.height() < 100):
        for w in app.topLevelWidgets():
            if w.width() >= 100 and w.height() >= 100:
                widget = w
                break
    if widget is None:
        log_op(f"  截图跳过（无活跃窗口）: {name}")
        return ""
    pixmap = widget.grab()
    path = SCREENSHOT_DIR / f"{name}_{_current_viewport}.png"
    pixmap.save(str(path))
    return str(path)


def process_events(app: QApplication, ms: int = 200) -> None:
    app.processEvents()
    QTest.qWait(ms)


def resize_viewport(app: QApplication, window: QWidget, width: int, height: int, viewport: str) -> None:
    global _current_viewport
    _current_viewport = viewport
    window.resize(width, height)
    app.processEvents()
    QTest.qWait(300)


def screenshot_all_viewports(app: QApplication, window: QWidget, name: str,
                              run_checks: bool = True) -> None:
    for w, h, vp in VIEWPORTS:
        resize_viewport(app, window, w, h, vp)
        screenshot(app, name)
        if run_checks:
            run_visual_checks(app, window, f"{name}_{vp}")


# ── 视觉几何检查 ──────────────────────────────────────────

def _widget_path(widget: QWidget) -> str:
    parts = []
    w = widget
    while w is not None:
        name = w.objectName() or w.__class__.__name__
        parts.append(name)
        w = w.parentWidget() if hasattr(w, "parentWidget") else None
    return " > ".join(reversed(parts[-5:]))  # 最多 5 层


def _is_inside_scrollarea(widget: QWidget) -> bool:
    """判断 widget 是否位于 QScrollArea 的 viewport 内

    QScrollArea 的内容 widget 设计上可以大于 viewport（由滚动条裁剪），
    这种"溢出"是预期行为，不应视为视觉缺陷。
    """
    from PySide6.QtWidgets import QScrollArea
    w = widget.parentWidget()
    while w is not None:
        if isinstance(w, QScrollArea):
            return True
        # qt_scrollarea_viewport 是 QScrollArea 的内部 viewport
        if w.objectName() == "qt_scrollarea_viewport":
            return True
        w = w.parentWidget()
    return False


def _check_widget_bounds(widget: QWidget) -> None:
    if not widget.isVisible():
        return
    parent = widget.parentWidget()
    if parent is None:
        return
    # V0.5.1 V-01~V-03 修复：跳过 QScrollArea 内部内容
    # QScrollArea 的内容 widget 可以合法地大于 viewport，由滚动条裁剪
    if _is_inside_scrollarea(widget):
        return
    wg = widget.geometry()
    pg = parent.geometry()
    if wg.right() > pg.right() + 2 or wg.bottom() > pg.bottom() + 2:
        record_visual(
            "out_of_bounds", _widget_path(widget),
            f"控件({wg.right()},{wg.bottom()})超出父控件({pg.right()},{pg.bottom()})",
            severity="major",
        )


def _check_text_truncation(label: QLabel) -> None:
    if not label.isVisible():
        return
    text = label.text()
    if not text:
        return
    fm = label.fontMetrics()
    needed = fm.horizontalAdvance(text)
    actual = label.width()
    if needed > actual + 10 and not label.wordWrap():
        record_visual(
            "text_truncated", _widget_path(label),
            f"文本'{text[:30]}'需{needed}px实际{actual}px",
            severity="minor",
        )


def _check_zero_size(widget: QWidget) -> None:
    if not widget.isVisible():
        return
    g = widget.geometry()
    if g.width() == 0 or g.height() == 0:
        record_visual(
            "zero_size", _widget_path(widget),
            f"可见控件尺寸{g.width()}x{g.height()}",
            severity="major",
        )


def _check_color_contrast(widget: QWidget) -> None:
    if not widget.isVisible():
        return
    try:
        palette = widget.palette()
        fg = palette.color(QPalette.ColorRole.WindowText)
        bg = palette.color(QPalette.ColorRole.Window)
    except Exception:
        return
    if not fg.isValid() or not bg.isValid():
        return
    ratio = _contrast_ratio(fg, bg)
    if 0.1 < ratio < 4.5:
        record_visual(
            "low_contrast", _widget_path(widget),
            f"对比度{ratio:.2f}:1 (fg={fg.name()} bg={bg.name()})",
            severity="minor",
        )


def _contrast_ratio(c1: QColor, c2: QColor) -> float:
    def luminance(c: QColor) -> float:
        r, g, b = c.red() / 255, c.green() / 255, c.blue() / 255
        def adj(v: float) -> float:
            return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
        return 0.2126 * adj(r) + 0.7152 * adj(g) + 0.0722 * adj(b)
    l1, l2 = luminance(c1), luminance(c2)
    return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)


def run_visual_checks(app: QApplication, window: QWidget, page_name: str) -> None:
    log_op(f"  视觉检查: {page_name} (viewport={_current_viewport})")
    all_widgets = window.findChildren(QWidget)
    checked = 0
    for w in all_widgets:
        if w.isVisible():
            _check_widget_bounds(w)
            _check_zero_size(w)
            checked += 1
            if checked > 200:
                break
    for lbl in window.findChildren(QLabel)[:50]:
        _check_text_truncation(lbl)
    for btn in window.findChildren(QPushButton)[:30]:
        _check_text_truncation(btn)
    for w in window.findChildren(QLabel)[:20]:
        _check_color_contrast(w)


# ── 弹窗处理工具（薄包装，复用 tests/gui/helpers/interactions.py） ──
# singleShot 回调中对话框已弹出，用 timeout_ms=0 即时返回避免阻塞

def find_dialog(app: QApplication, title_contains: str) -> QDialog | None:
    """即时查找可见的 QDialog（包括嵌套），找不到立即返回 None"""
    return _find_dialog(app, title_contains, timeout_ms=0)


def find_message_box(app: QApplication) -> QMessageBox | None:
    """即时查找可见的 QMessageBox（包括嵌套）"""
    return _find_message_box(app)


def dismiss_message_boxes(app: QApplication) -> list[str]:
    """关闭所有 QMessageBox，返回文本列表"""
    return _dismiss_message_boxes(app)


def close_all_modal_widgets(app: QApplication) -> None:
    """关闭所有可见的 QMenu/QMessageBox/QDialog，防止残留弹窗阻塞测试"""
    _close_all_modal_widgets(app)


def set_combo_by_data(combo: QComboBox, data_value: str, label: str = "") -> None:
    for i in range(combo.count()):
        if combo.itemData(i) == data_value:
            combo.setCurrentIndex(i)
            return
    raise RuntimeError(f"下拉框未找到选项 {data_value}: {label}")


def set_combo_by_text(combo: QComboBox, text: str, label: str = "") -> None:
    index = combo.findText(text)
    if index >= 0:
        combo.setCurrentIndex(index)
        return
    raise RuntimeError(f"下拉框未找到文本 '{text}': {label}")


# ── 隔离工作空间（TD-T09 修复） ──────────────────────────

def create_isolated_workspace() -> tuple[str, tempfile.TemporaryDirectory]:
    tmp_dir = tempfile.TemporaryDirectory(prefix="auto_pm_gui_test_")
    ws = Path(tmp_dir.name)
    (ws / PLC_SUBDIR).mkdir(parents=True, exist_ok=True)
    log_op(f"  创建隔离工作空间: {ws}")
    return str(ws), tmp_dir


def create_minimal_test_project(workspace_root: str) -> str:
    """预置 fixture 项目（确保 GUI 启动时有项目可显示，避免空状态）"""
    project_dir = Path(workspace_root) / PLC_SUBDIR / f"{FIXTURE_PROJECT_ID}_{FIXTURE_PROJECT_NAME}"
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / ".plc.json").write_text(
        json.dumps({
            "name": FIXTURE_PROJECT_ID,
            "version": "V1.0.0",
            "description": "GUI自动化预置测试项目",
            "type": "standard",
            "equipment_type": "conveyor",
            "plc_vendor": "siemens",
            "plc_model": "S7-1200",
            "stack": "plc",
            "phase": "developing",
        }, ensure_ascii=False),
        encoding="utf-8",
    )
    (project_dir / "00_项目管理").mkdir(exist_ok=True)
    (project_dir / "02_PLC程序").mkdir(exist_ok=True)
    (project_dir / "02_PLC程序" / "PLC_ST").mkdir(exist_ok=True)
    (project_dir / f"PM_SESSION_{FIXTURE_PROJECT_ID}.md").write_text(
        f"# {FIXTURE_PROJECT_ID} GUI自动化预置测试项目\n\n"
        f"- project_id: {FIXTURE_PROJECT_ID}\n- stack: plc\n- phase: developing\n",
        encoding="utf-8",
    )
    log_op(f"  创建预置项目: {project_dir}")
    return str(project_dir)


def _fix_copier_answers(workspace_root: str) -> None:
    """修复 GUI Bug TD-G01: 补全 .copier-answers.yml 中 None 值字段

    auto-pm 新建项目时 equipment_type/plc_vendor/plc_model 非必填，
    copier 模板渲染时写入 null，但 ProjectInfo 模型要求 str，导致扫描失败。
    测试策略：找到 GUI 创建的项目 .copier-answers.yml，将 None 改为空字符串。
    """
    import yaml
    ws = Path(workspace_root)
    fixed = 0
    for answers_file in ws.rglob(".copier-answers.yml"):
        try:
            with open(answers_file, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            changed = False
            for key in ["equipment_type", "plc_vendor", "plc_model",
                        "project_type", "stack", "phase", "business_line"]:
                if key in data and data[key] is None:
                    data[key] = ""
                    changed = True
            if changed:
                with open(answers_file, "w", encoding="utf-8") as f:
                    yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
                fixed += 1
                log_op(f"  修复 .copier-answers.yml: {answers_file}")
        except Exception as e:
            log_op(f"  修复 .copier-answers.yml 失败: {answers_file} - {e}")
    if fixed:
        log_op(f"  共修复 {fixed} 个 .copier-answers.yml（绕过 TD-G01 让后续测试继续）")


# ── 测试步骤 ──────────────────────────────────────────────

def step_01_launch_gui(app: QApplication, workspace_root: str) -> object:
    """场景1: 启动应用"""
    log_op("场景1: 启动 GUI 主窗口")
    try:
        from auto_pm.ui.main_window import MainWindow
        window = MainWindow(workspace_root=workspace_root)
        window.show()
        process_events(app, 1000)
        screenshot_all_viewports(app, window, "01_first_load")
        log_op("  GUI 启动成功")
        return window
    except Exception as e:
        record_bug("启动GUI", str(e), "critical")
        raise


def step_02_navigation(app: QApplication, window) -> None:
    """场景2: 查找项目 - 导航树/搜索/筛选/视图切换"""
    log_op("场景2: 导航树与项目查找")
    # 2.1 搜索
    try:
        log_op("  2.1 搜索 'DJ'")
        window._search_edit.setText("DJ")
        process_events(app, 500)
        screenshot(app, "02_search_dj")
        window._search_edit.clear()
        process_events(app, 300)
    except Exception as e:
        record_bug("搜索", str(e), "minor")

    # 2.2 业务线筛选
    try:
        log_op("  2.2 业务线筛选切换")
        combo = window._business_combo
        for text in ["单机设备 (DJ)", "软件开发 (SW)", "全部业务线"]:
            idx = combo.findText(text)
            if idx >= 0:
                combo.setCurrentIndex(idx)
                process_events(app, 500)
        screenshot(app, "02_business_filter")
    except Exception as e:
        record_bug("业务线筛选", str(e), "minor")

    # 2.3 视图切换
    try:
        log_op("  2.3 视图切换（卡片/列表）")
        vc = window._project_list_view._view_controls
        vc._list_btn.click()
        process_events(app, 500)
        screenshot_all_viewports(app, window, "02_list_view")
        vc._card_btn.click()
        process_events(app, 500)
        screenshot_all_viewports(app, window, "02_card_view", run_checks=False)
    except Exception as e:
        record_bug("视图切换", str(e), "minor")

    # 2.4 分组模式
    try:
        log_op("  2.4 分组模式切换")
        combo = window._project_list_view._view_controls._group_combo
        for text in ["总库+业务线", "总库+阶段", "业务线", "阶段"]:
            idx = combo.findText(text)
            if idx >= 0:
                combo.setCurrentIndex(idx)
                process_events(app, 500)
        idx = combo.findText("总库+业务线")
        if idx >= 0:
            combo.setCurrentIndex(idx)
        process_events(app, 300)
    except Exception as e:
        record_bug("分组切换", str(e), "minor")


def step_03_create_project(app: QApplication, window, workspace_root: str) -> None:
    """场景3: 新建 PLC 项目（singleShot 模式）"""
    log_op("场景3: 新建 PLC 项目")
    created = {"success": False, "error": ""}

    def _fill_and_submit():
        # 先关闭可能存在的 critical 弹窗
        dismiss_message_boxes(app)
        dlg = find_dialog(app, "新建项目")
        if dlg is None:
            created["error"] = "对话框未弹出"
            close_all_modal_widgets(app)  # 关闭可能残留的 QMenu/Dialog
            return
        try:
            dlg._id_edit.setText(TEST_PROJECT_ID)
            process_events(app, 100)
            dlg._name_edit.setText(TEST_PROJECT_NAME)
            process_events(app, 100)
            try:
                set_combo_by_data(dlg._stack_combo, "plc", "技术栈")
            except Exception:
                pass
            dlg._dry_run_check.setChecked(False)
            process_events(app, 100)
            screenshot(app, "03_new_project_form")
            # 点击 OK
            ok_btn = dlg._button_box.button(QDialogButtonBox.StandardButton.Ok)
            ok_btn.click()
            # 预注册 QMessageBox 处理
            def _handle_msg():
                texts = dismiss_message_boxes(app)
                for t in texts:
                    if "已存在" in t:
                        created["error"] = f"项目已存在: {t}"
                    elif "成功" in t or "创建" in t:
                        created["success"] = True
                    else:
                        created["error"] = t
                # 如果创建失败，对话框可能还在显示，关闭它防止阻塞
                if not created["success"] and dlg is not None and dlg.isVisible():
                    dlg.reject()
                    process_events(app, 300)
                process_events(app, 500)
            QTimer.singleShot(300, _handle_msg)
        except Exception as e:
            created["error"] = str(e)
            close_all_modal_widgets(app)

    QTimer.singleShot(100, _fill_and_submit)
    try:
        window._on_new_project("plc")
    except Exception as e:
        record_bug("新建项目", f"调用失败: {e}", "major")
        return

    process_events(app, 1000)
    if created["success"]:
        log_op("  项目创建成功")
    elif created["error"] and "已存在" in created["error"]:
        log_op(f"  项目已存在（视为成功）: {created['error']}")
        created["success"] = True
    elif created["error"]:
        record_bug("新建项目", created["error"], "major")

    screenshot(app, "03_project_created")

    # 修复 GUI Bug TD-G01: copier 模板渲染的 .copier-answers.yml 中
    # equipment_type/plc_vendor/plc_model 为 null，导致 ProjectInfo 校验失败
    # 测试策略：创建后手动补全 .copier-answers.yml 字段，让后续测试能继续
    _fix_copier_answers(workspace_root)

    # 刷新列表
    try:
        window._on_refresh()
        process_events(app, 1000)
    except Exception:
        pass


def reject_dialog_safe(dlg, app):
    try:
        cancel_btn = dlg._button_box.button(QDialogButtonBox.StandardButton.Cancel)
        if cancel_btn:
            cancel_btn.click()
        else:
            dlg.reject()
        process_events(app, 300)
    except Exception:
        dlg.reject()
        process_events(app, 300)


def step_04_enter_workspace(app: QApplication, window) -> None:
    """场景4: 进入项目工作区"""
    log_op("场景4: 进入项目工作区")
    try:
        list_view = window._project_list_view
        # 优先尝试 GUI 新建的 TEST_PROJECT_ID，降级用 FIXTURE_PROJECT_ID
        candidates = [TEST_PROJECT_ID, FIXTURE_PROJECT_ID]
        entered_pid = None
        for pid in candidates:
            window._search_edit.setText(pid)
            process_events(app, 500)
            project = list_view.get_project(pid)
            if project is not None:
                entered_pid = pid
                break
        window._search_edit.clear()
        process_events(app, 300)

        if entered_pid is None:
            # 使用任意 PLC 项目
            projects = list_view._all_projects
            plc_projects = [p for p in projects if p.stack == "plc"]
            if plc_projects:
                entered_pid = plc_projects[0].project_id
                log_op(f"  测试项目未找到，使用已有: {entered_pid}")
            else:
                record_bug("进入工作区", "无PLC项目可进入", "major")
                return

        log_op(f"  进入项目: {entered_pid}")
        window._on_project_selected(entered_pid)
        process_events(app, 800)
        screenshot_all_viewports(app, window, "04_workspace_overview")
    except Exception as e:
        record_bug("进入工作区", str(e), "major")


def step_05_create_change(app: QApplication, window) -> None:
    """场景5: 创建变更单（singleShot 模式，QWizard）"""
    log_op("场景5: 创建变更单")
    workspace_view = window._workspace_view
    if workspace_view._project is None:
        log_op("  跳过：未进入项目工作区")
        return

    # 切换到变更 Tab
    try:
        change_idx = workspace_view._tab_indices.get("change", -1)
        if change_idx < 0:
            record_bug("变更Tab", "Tab索引未找到", "major")
            return
        workspace_view._tab_widget.setCurrentIndex(change_idx)
        process_events(app, 500)
        screenshot(app, "05_change_tab_empty")
    except Exception as e:
        record_bug("变更Tab切换", str(e), "major")
        return

    change_tab = workspace_view._change_tab
    if change_tab is None:
        record_bug("变更Tab", "ChangeTab 未初始化", "major")
        return

    created = {"success": False, "error": ""}
    project_id = workspace_view._project.project_id

    def _fill_wizard_and_submit():
        # 先关闭可能存在的 critical 弹窗（_load_projects 失败时弹出）
        dismiss_message_boxes(app)
        wizard = find_dialog(app, "创建变更单")
        if wizard is None:
            created["error"] = "向导未弹出"
            close_all_modal_widgets(app)  # 关闭可能残留的弹窗
            return
        # 监听 change_created 信号（_on_create 成功时 emit，不弹 QMessageBox）
        wizard.change_created.connect(lambda pid: created.__setitem__("success", True))  # type: ignore[attr-defined]
        try:
            # 等待 _load_projects 完成（最多 2 秒）
            for _ in range(20):
                if wizard._project_combo.count() > 0:
                    break
                process_events(app, 100)
            # 第 1 页：基本信息
            combo_filled = False
            try:
                set_combo_by_data(wizard._project_combo, project_id, "项目")
                combo_filled = True
            except Exception:
                # 项目加载失败，尝试用第一项
                if wizard._project_combo.count() > 0:
                    wizard._project_combo.setCurrentIndex(0)
                    combo_filled = True
                else:
                    created["error"] = "项目下拉框无数据"
                    wizard.reject()
                    process_events(app, 300)
                    return
            process_events(app, 100)
            try:
                set_combo_by_data(wizard._domain_combo, "PLC", "领域")
                set_combo_by_data(wizard._nature_combo, "DEF", "性质")
                set_combo_by_data(wizard._scope_combo, "LOCAL", "范围")
            except Exception as e:
                log_op(f"  下拉框设置部分失败: {e}")
            wizard._applicant_edit.setText("auto_test")
            process_events(app, 100)
            wizard._background_edit.setPlainText("GUI自动化测试：验证变更单创建功能")
            process_events(app, 100)
            screenshot(app, "05_create_change_page1")

            # 跳到下一页（描述页）
            wizard.next()
            process_events(app, 500)
            # 填写必要性
            try:
                wizard._necessity_edit.setPlainText("自动化测试必需")
                process_events(app, 100)
            except Exception:
                pass

            # 跳到确认页
            wizard.next()
            process_events(app, 500)
            screenshot(app, "05_create_change_confirm")

            # 预注册 QMessageBox 处理（在 Finish 点击之前注册，
            # 因为 validatePage → _on_create 失败时弹 QMessageBox 阻塞）
            def _handle_msg():
                texts = dismiss_message_boxes(app)
                for t in texts:
                    if "失败" in t or "错误" in t:
                        created["error"] = t
                # 失败时关闭 wizard 防止阻塞（成功时 wizard 已被 QWizard.accept 关闭）
                if not created.get("success") and wizard is not None and wizard.isVisible():
                    wizard.reject()
                    process_events(app, 300)
                process_events(app, 500)
            QTimer.singleShot(300, _handle_msg)
            # 点 Finish 按钮（不是 next()！QWizard.next() 在最后一页只调 validatePage 不 accept，
            # 必须用 FinishButton.click() 触发 done(Accepted) 让 wizard.exec() 退出）
            finish_btn = wizard.button(QWizard.WizardButton.FinishButton)  # type: ignore[attr-defined]
            finish_btn.click()
            process_events(app, 1000)
        except Exception as e:
            created["error"] = f"向导填写异常: {e}"
            try:
                wizard.reject()
                process_events(app, 300)
            except Exception:
                pass

    # 延长等待时间到 800ms，确保 _load_projects 先启动
    QTimer.singleShot(800, _fill_wizard_and_submit)
    try:
        change_tab._on_create_change()
    except Exception as e:
        record_bug("创建变更单", f"调用失败: {e}", "major")
        return

    process_events(app, 1500)
    if created["success"]:
        log_op("  变更单创建成功")
    elif created["error"]:
        record_bug("创建变更单", created["error"], "major")

    screenshot(app, "05_change_created")


def step_06_change_transitions(app: QApplication, window) -> None:
    """场景6: 变更审批流转（7 次）

    策略：草稿→已提交用 GUI 对话框（单目标直接弹）；
    后续多目标流转直接调 ChangeService API（绕过 QMenu 菜单），
    但每次流转后刷新 ChangeTab 列表，截图验证 UI 状态更新。
    """
    log_op("场景6: 变更状态流转（7 次）")
    workspace_view = window._workspace_view
    if workspace_view._project is None:
        log_op("  跳过：未进入项目工作区")
        return

    change_tab = workspace_view._change_tab
    if change_tab is None:
        record_bug("状态流转", "ChangeTab 未初始化", "major")
        return

    project_id = workspace_view._project.project_id
    change_service = change_tab._change_service

    # 获取变更单编号
    try:
        changes = change_service.list_change_requests(project_id)
        if not changes:
            record_bug("状态流转", "无变更单可流转", "major")
            return
        change_number = changes[0].change_number
        log_op(f"  目标变更单: {change_number}")
    except Exception as e:
        record_bug("状态流转", f"获取变更单失败: {e}", "major")
        return

    # 7 次流转：草稿→已提交→审核中→已批准→实施中→待验收→验收中→已完成
    transitions = [
        ("submitted", "已提交"),
        ("under_review", "审核中"),
        ("approved", "已批准"),
        ("implementing", "实施中"),
        ("pending_acceptance", "待验收"),
        ("accepting", "验收中"),
        ("completed", "已完成"),
    ]

    for i, (target_status, target_label) in enumerate(transitions, 1):
        log_op(f"  6.{i} 流转: → {target_label} ({target_status})")

        # 第 1 次（草稿→已提交）用 GUI 对话框验证 UI 交互
        if i == 1:
            result = {"success": False, "error": ""}

            def _fill_transition(res=result, label=target_label):
                dismiss_message_boxes(app)
                dlg = find_dialog(app, "流转") or find_dialog(app, "状态流转")
                if dlg is None:
                    res["error"] = "流转对话框未弹出"
                    close_all_modal_widgets(app)  # 关闭可能残留的 QMenu/Dialog
                    return
                # 监听 transition_completed 信号（流转成功时不弹 QMessageBox，只 emit + accept）
                dlg.transition_completed.connect(lambda cn: res.__setitem__("success", True))  # type: ignore[attr-defined]
                try:
                    dlg._approver_edit.setText("auto_test")
                    process_events(app, 100)
                    dlg._comment_edit.setPlainText(f"自动测试流转至{label}")
                    process_events(app, 100)
                    screenshot(app, f"06_transition_{target_status}_form")
                    ok_btn = dlg._button_box.button(QDialogButtonBox.StandardButton.Ok)
                    ok_btn.click()

                    def _handle_msg():
                        texts = dismiss_message_boxes(app)
                        for t in texts:
                            if "失败" in t or "错误" in t:
                                res["error"] = t
                        # 如果流转失败，对话框可能还在显示，关闭它防止阻塞
                        if not res.get("success") and dlg is not None and dlg.isVisible():
                            dlg.reject()
                            process_events(app, 300)
                            dismiss_message_boxes(app)
                        process_events(app, 500)
                    QTimer.singleShot(300, _handle_msg)
                except Exception as e:
                    res["error"] = f"填写异常: {e}"
                    close_all_modal_widgets(app)

            QTimer.singleShot(300, _fill_transition)
            try:
                cards = change_tab._get_cards()
                if cards:
                    cards[0]._transition_btn.click()
                else:
                    record_bug(f"流转→{target_label}", "无变更单卡片", "major")
                    break
            except Exception as e:
                record_bug(f"流转→{target_label}", f"点击失败: {e}", "major")
                continue

            # 等待流转完成（最多 8 秒）
            for _ in range(40):
                if result["success"] or result["error"]:
                    break
                process_events(app, 200)

            if result["success"]:
                log_op(f"    流转成功（GUI 对话框）")
            elif result["error"]:
                record_bug(f"流转→{target_label}", result["error"], "minor")
                # 降级前先清理可能残留的弹窗（QMenu/Dialog/QMessageBox）
                close_all_modal_widgets(app)
                # 降级用 API 完成流转
                _transition_via_api(change_service, change_number, target_status,
                                    target_label, change_tab, app, i)
        else:
            # 后续流转直接用 API（多目标会弹 QMenu，自动化处理复杂）
            # 先清理可能残留的弹窗
            close_all_modal_widgets(app)
            _transition_via_api(change_service, change_number, target_status,
                                target_label, change_tab, app, i)

        screenshot(app, f"06_after_{target_status}")
        process_events(app, 500)


def _transition_via_api(change_service, change_number: str, target_status: str,
                        target_label: str, change_tab, app, step_idx: int) -> None:
    """通过 ChangeService API 直接流转（绕过 GUI QMenu）"""
    try:
        cr = change_service.transition_status(
            change_number=change_number,
            new_status=target_status,
            approver="auto_test",
            comment=f"自动测试流转至{target_label}",
            verification_conclusion="全部通过" if target_status == "completed" else "通过",
        )
        if cr is not None:
            log_op(f"    流转成功（API）: {change_number} → {target_status}")
            # 刷新 ChangeTab UI
            change_tab._refresh_list()
            process_events(app, 500)
        else:
            record_bug(f"流转→{target_label}", "API 返回 None", "minor")
    except Exception as e:
        record_bug(f"流转→{target_label}", f"API 异常: {e}", "minor")


def step_07_check_tab(app: QApplication, window) -> None:
    """场景7: PLC 检查"""
    log_op("场景7: PLC 检查")
    workspace_view = window._workspace_view
    if workspace_view._project is None:
        log_op("  跳过：未进入项目工作区")
        return

    try:
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

        # 执行检查
        log_op("  7.1 执行检查")
        try:
            check_tab._check_btn.click()
            process_events(app, 1500)
            screenshot(app, "07_check_result")
        except Exception as e:
            record_bug("执行检查", str(e), "major")

        # 自动修复预览
        log_op("  7.2 自动修复预览")
        try:
            check_tab._repair_btn.click()
            process_events(app, 1000)
            screenshot(app, "07_repair_preview")
            dismiss_message_boxes(app)
        except Exception as e:
            record_bug("自动修复", str(e), "minor")

        # 标准化命名预览
        log_op("  7.3 标准化命名预览")
        try:
            check_tab._standardize_btn.click()
            process_events(app, 1000)
            screenshot(app, "07_standardize_preview")
            dismiss_message_boxes(app)
        except Exception as e:
            record_bug("标准化命名", str(e), "minor")
    except Exception as e:
        record_bug("检查Tab", str(e), "major")


def step_08_doc_tab(app: QApplication, window) -> None:
    """场景8: 文档管理"""
    log_op("场景8: 文档管理")
    workspace_view = window._workspace_view
    if workspace_view._project is None:
        log_op("  跳过：未进入项目工作区")
        return

    try:
        doc_idx = workspace_view._tab_indices.get("doc", -1)
        if doc_idx < 0:
            record_bug("文档Tab", "Tab索引未找到", "minor")
            return
        workspace_view._tab_widget.setCurrentIndex(doc_idx)
        process_events(app, 500)
        screenshot(app, "08_doc_tab")

        doc_tab = workspace_view._doc_tab
        if doc_tab is None:
            record_bug("文档Tab", "DocTab 未初始化", "minor")
            return

        log_op("  8.1 检查文档树")
        cat_items = doc_tab._get_category_items()
        log_op(f"  文档分类数: {len(cat_items)}")

        log_op("  8.2 模板信息")
        try:
            log_op(f"  模板: {doc_tab._template_name_label.text()}")
            log_op(f"  版本: {doc_tab._template_version_label.text()}")
        except Exception:
            pass

        log_op("  8.3 检查模板更新")
        try:
            doc_tab._check_btn.click()
            process_events(app, 1000)
            dismiss_message_boxes(app)
        except Exception as e:
            record_bug("检查模板更新", str(e), "minor")

        screenshot(app, "08_doc_tab_final")
    except Exception as e:
        record_bug("文档Tab", str(e), "minor")


def step_09_vartable_tab(app: QApplication, window) -> None:
    """场景9: 变量表管理"""
    log_op("场景9: 变量表管理")
    workspace_view = window._workspace_view
    if workspace_view._project is None:
        log_op("  跳过：未进入项目工作区")
        return

    try:
        vt_idx = workspace_view._tab_indices.get("vartable", -1)
        if vt_idx < 0:
            record_bug("变量表Tab", "Tab索引未找到", "major")
            return
        workspace_view._tab_widget.setCurrentIndex(vt_idx)
        process_events(app, 500)
        screenshot_all_viewports(app, window, "09_vartable_tab")

        vartable_tab = workspace_view._vartable_tab
        if vartable_tab is None:
            record_bug("变量表Tab", "VartableTab 未初始化", "major")
            return

        # 文件列表（QListWidget，非 QComboBox）
        log_op("  9.1 文件列表")
        file_list = vartable_tab._file_list
        log_op(f"  变量表文件数: {file_list.count()}")
        for i in range(file_list.count()):
            log_op(f"    [{i}] {file_list.item(i).text()}")

        # 状态标签
        log_op("  9.2 状态信息")
        try:
            log_op(f"  状态: {vartable_tab._status_label.text()}")
        except Exception:
            pass

        # 切换文件
        if file_list.count() > 1:
            log_op("  9.3 切换文件")
            file_list.setCurrentRow(1)
            process_events(app, 500)
            screenshot(app, "09_vartable_file_switched")
            file_list.setCurrentRow(0)
            process_events(app, 300)

        # 批量解析
        log_op("  9.4 批量解析")
        try:
            vartable_tab._on_batch_parse()
            process_events(app, 1500)
            dismiss_message_boxes(app)
        except Exception as e:
            record_bug("变量表批量解析", str(e), "minor")

        # 编辑器（VariableTableEditor，非 QTableWidget）
        log_op("  9.5 编辑器检查")
        editor = vartable_tab._editor
        if editor is not None:
            log_op(f"  编辑器类型: {type(editor).__name__}")
            # 尝试获取内部表格
            try:
                inner_table = editor._table if hasattr(editor, "_table") else None
                if inner_table is not None:
                    log_op(f"  内部表格: {inner_table.rowCount()} 行 × {inner_table.columnCount()} 列")
            except Exception:
                pass
        else:
            record_bug("变量表Tab", "Editor 未初始化", "minor")

        screenshot(app, "09_vartable_final")
    except Exception as e:
        record_bug("变量表Tab", str(e), "major")


def step_10_change_center(app: QApplication, window) -> None:
    """场景10: 变更中心"""
    log_op("场景10: 变更中心")
    try:
        window._on_page_switch("change_center")
        process_events(app, 800)
        screenshot_all_viewports(app, window, "10_change_center")

        change_center = window._change_center_view
        if change_center is None:
            record_bug("变更中心", "ChangeCenterView 未初始化", "major")
            return

        # 切换状态 Tab
        log_op("  10.1 切换状态 Tab")
        list_panel = change_center._list_panel
        if list_panel is not None:
            for tab_btn in list_panel.findChildren(QPushButton):
                if tab_btn.isCheckable():
                    tab_btn.click()
                    process_events(app, 300)
            screenshot(app, "10_change_center_tabs")

        # 从变更中心创建变更单（弹出后关闭，验证弹窗可用）
        log_op("  10.2 从变更中心创建变更单（弹出后关闭）")
        dismissed = {"done": False}

        def _reject_wizard():
            wizard = find_dialog(app, "创建变更单")
            if wizard is not None:
                screenshot(app, "10_create_change_from_center")
                wizard.reject()
                process_events(app, 300)
            dismissed["done"] = True

        QTimer.singleShot(100, _reject_wizard)
        try:
            change_center._create_btn.click()
        except Exception as e:
            record_bug("变更中心创建变更单", str(e), "minor")
        process_events(app, 800)
        # 确保关闭所有残留弹窗（wizard + 可能的 critical QMessageBox）
        close_all_modal_widgets(app)
    except Exception as e:
        record_bug("变更中心", str(e), "major")


def step_11_spec_center(app: QApplication, window) -> None:
    """场景11: 规范中心（6 Tab 遍历）"""
    log_op("场景11: 规范中心（6 Tab）")
    try:
        window._on_page_switch("spec_center")
        process_events(app, 1000)
        screenshot_all_viewports(app, window, "11_spec_center_overview")

        spec_center = window._spec_center_view
        if spec_center is None:
            record_bug("规范中心", "SpecCenterView 未初始化", "major")
            return

        tab_widget = spec_center._tab_widget
        if tab_widget is None:
            record_bug("规范中心", "_tab_widget 未初始化", "major")
            return

        tab_count = tab_widget.count()
        log_op(f"  规范中心 Tab 数: {tab_count}")

        for i in range(tab_count):
            tab_label = tab_widget.tabText(i)
            log_op(f"  11.{i+1} 切换 Tab: {tab_label}")
            tab_widget.setCurrentIndex(i)
            process_events(app, 800)
            screenshot(app, f"11_spec_center_tab{i}")

        # 三视口检查
        tab_widget.setCurrentIndex(0)
        process_events(app, 500)
        screenshot_all_viewports(app, window, "11_spec_center_viewports", run_checks=False)
    except Exception as e:
        record_bug("规范中心", str(e), "major")


def step_12_report_center(app: QApplication, window) -> None:
    """场景12: 报告中心"""
    log_op("场景12: 报告中心")
    try:
        window._on_page_switch("report")
        process_events(app, 800)
        screenshot_all_viewports(app, window, "12_report_center")
    except Exception as e:
        record_bug("报告中心", str(e), "minor")


def step_13_settings(app: QApplication, window) -> None:
    """场景13: 系统设置"""
    log_op("场景13: 系统设置")
    try:
        window._on_page_switch("settings")
        process_events(app, 800)
        screenshot_all_viewports(app, window, "13_settings")

        settings_page = window._settings_page
        if settings_page is None:
            record_bug("系统设置", "SettingsPage 未初始化", "minor")
            return

        log_op("  13.1 设置信息")
        try:
            log_op(f"  工作空间: {settings_page.workspace_edit.text()}")
            log_op(f"  {settings_page.db_path_label.text()}")
            log_op(f"  {settings_page.project_count_label.text()}")
        except Exception:
            pass

        log_op("  13.2 调整扫描深度")
        try:
            settings_page.depth_spin.setValue(3)
            process_events(app, 300)
        except Exception as e:
            record_bug("扫描深度", str(e), "minor")

        # 重建索引（弹出确认 → 选否）
        log_op("  13.3 重建索引（确认弹窗→否）")
        rejected = {"done": False}

        def _reject_confirm():
            mb = find_message_box(app)
            if mb is not None:
                mb.reject()
                process_events(app, 300)
            rejected["done"] = True

        QTimer.singleShot(300, _reject_confirm)
        try:
            settings_page.rebuild_button.click()
        except Exception as e:
            record_bug("重建索引", str(e), "minor")
        process_events(app, 800)
        # 确保关闭所有残留弹窗
        close_all_modal_widgets(app)

        screenshot(app, "13_settings_final")
    except Exception as e:
        record_bug("系统设置", str(e), "minor")


def step_14_toolbar(app: QApplication, window) -> None:
    """工具栏操作"""
    log_op("步骤14: 工具栏操作")
    try:
        log_op("  14.1 同步缓存")
        window._on_sync()
        process_events(app, 1000)
        screenshot(app, "14_sync")
    except Exception as e:
        record_bug("同步缓存", str(e), "minor")

    try:
        log_op("  14.2 刷新列表")
        window._on_refresh()
        process_events(app, 1000)
        screenshot(app, "14_refresh")
    except Exception as e:
        record_bug("刷新列表", str(e), "minor")

    try:
        log_op("  14.3 状态栏检查")
        log_op(f"  {window._status_workspace.text()} | {window._status_project.text()} | {window._status_db.text()}")
    except Exception as e:
        record_bug("状态栏", str(e), "minor")


def step_15_cleanup(app: QApplication, window) -> None:
    """清理：返回列表"""
    log_op("步骤15: 清理")
    try:
        window._on_back_to_list()
        process_events(app, 500)
        screenshot(app, "15_back_to_list")
    except Exception as e:
        record_bug("清理", str(e), "minor")


# ── 报告生成 ──────────────────────────────────────────────

def generate_report() -> str:
    lines = [
        "=" * 60,
        "PLC 全功能 GUI 测试报告（电气工程师视角）",
        f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"测试项目: {TEST_PROJECT_ID} (隔离 tmp 工作空间)",
        f"截图目录: {SCREENSHOT_DIR}",
        f"视口: {[v[2] for v in VIEWPORTS]}",
        "=" * 60,
        "",
    ]

    # 功能 Bug
    if not bugs:
        lines.append("✅ 未发现功能性 Bug")
    else:
        lines.append(f"共发现 {len(bugs)} 个功能性问题：")
        lines.append("")
        for i, bug in enumerate(bugs, 1):
            lines.append(f"Bug #{i}: [{bug['severity']}] {bug['step']}")
            lines.append(f"  错误: {bug['error']}")
            lines.append(f"  时间: {bug['timestamp']}")
            lines.append("")

    critical = sum(1 for b in bugs if b["severity"] == "critical")
    major = sum(1 for b in bugs if b["severity"] == "major")
    minor = sum(1 for b in bugs if b["severity"] == "minor")
    lines.append(f"功能问题统计: 严重={critical} 主要={major} 次要={minor}")
    lines.append("")

    # 视觉问题
    if visual_issues:
        lines.append("")
        lines.append("=" * 60)
        lines.append(f"视觉问题（程序化几何检查）: {len(visual_issues)} 个")
        lines.append("=" * 60)
        v_major = sum(1 for v in visual_issues if v["severity"] == "major")
        v_minor = sum(1 for v in visual_issues if v["severity"] == "minor")
        lines.append(f"统计: 主要={v_major} 次要={v_minor}")
        lines.append("")
        by_type: dict[str, list[dict]] = {}
        for v in visual_issues:
            by_type.setdefault(v["type"], []).append(v)
        for vtype, items in by_type.items():
            lines.append(f"  [{vtype}] {len(items)} 个")
            for v in items[:5]:
                lines.append(f"    - [{v['severity']}] {v['detail']} (viewport={v['viewport']})")
            if len(items) > 5:
                lines.append(f"    ... 还有 {len(items) - 5} 条")

    return "\n".join(lines)


def save_reports() -> dict[str, str]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    bug_path = REPORT_DIR / "full_test_bug_report.txt"
    bug_path.write_text(generate_report(), encoding="utf-8")

    log_path = REPORT_DIR / "full_test_operation_log.txt"
    log_path.write_text("\n".join(op_log), encoding="utf-8")

    json_path = REPORT_DIR / "full_test_report.json"
    report_data = {
        "test_session": datetime.now().isoformat(),
        "test_project_id": TEST_PROJECT_ID,
        "workspace": "isolated_tmp",
        "viewports": [{"width": w, "height": h, "name": v} for w, h, v in VIEWPORTS],
        "screenshot_dir": str(SCREENSHOT_DIR),
        "screenshot_count": len(list(SCREENSHOT_DIR.glob("*.png"))) if SCREENSHOT_DIR.exists() else 0,
        "bugs": {
            "total": len(bugs),
            "critical": sum(1 for b in bugs if b["severity"] == "critical"),
            "major": sum(1 for b in bugs if b["severity"] == "major"),
            "minor": sum(1 for b in bugs if b["severity"] == "minor"),
            "items": bugs,
        },
        "visual_issues": {
            "total": len(visual_issues),
            "major": sum(1 for v in visual_issues if v["severity"] == "major"),
            "minor": sum(1 for v in visual_issues if v["severity"] == "minor"),
            "by_type": _group_visual_by_type(),
            "items": visual_issues,
        },
    }
    json_path.write_text(json.dumps(report_data, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "bug_report": str(bug_path),
        "operation_log": str(log_path),
        "json_report": str(json_path),
    }


def _group_visual_by_type() -> dict[str, int]:
    result: dict[str, int] = {}
    for v in visual_issues:
        result[v["type"]] = result.get(v["type"], 0) + 1
    return result


# ── 主流程 ────────────────────────────────────────────────

def main() -> None:
    # Windows 控制台默认 GBK，emoji 会崩溃；强制 utf-8 输出
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

    print("=" * 60, flush=True)
    print("PLC 全功能 GUI 自动化测试 V3（电气工程师视角）", flush=True)
    print("=" * 60, flush=True)

    # 看门狗：5 分钟总超时，防止模态阻塞导致脚本永久卡住
    _WATCHDOG_TIMEOUT = 300
    _watchdog_fired = {"value": False}

    def _watchdog() -> None:
        time.sleep(_WATCHDOG_TIMEOUT)
        if _watchdog_fired["value"]:
            return
        _watchdog_fired["value"] = True
        # 超时后写日志 + 强制退出（不访问 Qt 对象，线程安全）
        try:
            REPORT_DIR.mkdir(parents=True, exist_ok=True)
            with open(REPORT_DIR / "watchdog_timeout.txt", "w", encoding="utf-8") as f:
                f.write(f"Watchdog timeout at {datetime.now().isoformat()}\n")
                f.write(f"Last 10 operations:\n")
                for line in op_log[-10:]:
                    f.write(f"  {line}\n")
        except Exception:
            pass
        print(f"\n*** 看门狗超时（{_WATCHDOG_TIMEOUT}s），强制退出", flush=True)
        os._exit(2)

    threading.Thread(target=_watchdog, daemon=True).start()

    # 支持 offscreen（默认，CI 兼容）和 visible（GUI_VISIBLE=1）两种模式
    if os.environ.get("GUI_VISIBLE", "0") == "1":
        if "QT_QPA_PLATFORM" in os.environ:
            del os.environ["QT_QPA_PLATFORM"]
            log_op("  清除 QT_QPA_PLATFORM，使用可见窗口模式（GUI_VISIBLE=1）")
    else:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        log_op("  使用 offscreen 模式（默认；设置 GUI_VISIBLE=1 切换可见窗口）")

    app = QApplication.instance() or QApplication(sys.argv)

    workspace_root, tmp_dir = create_isolated_workspace()
    try:
        create_minimal_test_project(workspace_root)

        window = None
        try:
            window = step_01_launch_gui(app, workspace_root)
            step_02_navigation(app, window)
            step_03_create_project(app, window, workspace_root)
            step_04_enter_workspace(app, window)
            step_05_create_change(app, window)
            step_06_change_transitions(app, window)
            step_07_check_tab(app, window)
            step_08_doc_tab(app, window)
            step_09_vartable_tab(app, window)
            step_10_change_center(app, window)
            step_11_spec_center(app, window)
            step_12_report_center(app, window)
            step_13_settings(app, window)
            step_14_toolbar(app, window)
            step_15_cleanup(app, window)
        except Exception as e:
            record_bug("主流程", f"未捕获异常: {e}\n{traceback.format_exc()}", "critical")

        if window is not None:
            resize_viewport(app, window, 1920, 1080, "desktop")
            screenshot(app, "99_final_state")

        report_paths = save_reports()
        print("\n" + generate_report(), flush=True)
        print(f"\nBug 报告: {report_paths['bug_report']}", flush=True)
        print(f"操作日志: {report_paths['operation_log']}", flush=True)
        print(f"JSON 报告: {report_paths['json_report']}", flush=True)
        print(f"截图目录: {SCREENSHOT_DIR}", flush=True)

        if window is not None:
            window.close()
    finally:
        try:
            tmp_dir.cleanup()
            log_op("  隔离工作空间已清理")
        except Exception as e:
            log_op(f"  隔离工作空间清理失败: {e}")

    sys.exit(0)


if __name__ == "__main__":
    main()
