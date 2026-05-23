#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SW-2026-005 UI自动化测试脚本

逐个触发所有UI按钮/菜单/工具栏操作，记录崩溃/异常/无响应问题。
"""
import sys
import os
import traceback
import faulthandler
from pathlib import Path

faulthandler.enable()

# Fix encoding for Windows console/file redirect
if sys.stdout.encoding != 'utf-8':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', errors='replace', closefd=False)
if sys.stderr.encoding != 'utf-8':
    sys.stderr = open(sys.stderr.fileno(), mode='w', encoding='utf-8', errors='replace', closefd=False)

BASE_PATH = Path(__file__).parent
sys.path.insert(0, str(BASE_PATH / "src"))
sys.path.insert(0, str(BASE_PATH))

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication


results = []


def record(test_name, status, detail=""):
    results.append({"test": test_name, "status": status, "detail": detail})
    icons = {"PASS": "[PASS]", "CRASH": "[CRASH]", "ERROR": "[ERROR]", "WARN": "[WARN]", "NOOP": "[NOOP]"}
    icon = icons.get(status, "[?]")
    line = f"  {icon} {test_name}"
    if detail:
        line += f" -- {detail}"
    print(line, flush=True)


def safe_run(test_name, func):
    try:
        # Auto-close any modal dialogs after 200ms
        def close_dialogs():
            from PyQt5.QtWidgets import QApplication
            for widget in QApplication.topLevelWidgets():
                if widget.isModal() and widget.isVisible():
                    widget.reject()
                    widget.close()
        QTimer.singleShot(200, close_dialogs)

        func()
        record(test_name, "PASS")
    except Exception as e:
        tb_lines = traceback.format_exc().split('\n')
        last_3 = '\n'.join(tb_lines[-3:])
        record(test_name, "CRASH", f"{type(e).__name__}: {e}")
        print(f"    TB: {last_3[:200]}", flush=True)


def test_toolbox_navigation(window):
    print("\n--- 1. ToolBox 页面切换 ---", flush=True)
    tb = window._tool_box
    if not tb:
        record("ToolBox", "ERROR", "ToolBox not created")
        return
    for i in range(tb.count()):
        name = tb.itemText(i)
        safe_run(f"ToolBox [{name}]", lambda idx=i: tb.setCurrentIndex(idx))


def test_tab_navigation(window):
    print("\n--- 2. TabWidget 页面切换 ---", flush=True)
    tw = window._tab_widget
    if not tw:
        record("TabWidget", "ERROR", "TabWidget not created")
        return
    for i in range(tw.count()):
        name = tw.tabText(i)
        safe_run(f"Tab [{name}]", lambda idx=i: tw.setCurrentIndex(idx))


def test_sidebar_buttons(window):
    print("\n--- 3. 侧边栏按钮点击 ---", flush=True)
    tb = window._tool_box
    if not tb:
        record("侧边栏", "ERROR", "ToolBox not created")
        return
    for page_idx in range(tb.count()):
        page_name = tb.itemText(page_idx)
        page_widget = tb.widget(page_idx)
        btn_list = page_widget.findChildren(object)
        btn_list = [b for b in btn_list if b.metaObject().className() == "QPushButton"]
        for btn in btn_list:
            btn_text = btn.text().strip()
            test_name = f"Sidebar [{page_name}] btn [{btn_text}]"
            if not btn.isEnabled():
                record(test_name, "NOOP", "disabled")
                continue
            safe_run(test_name, lambda b=btn: b.click())


def test_menu_actions(window):
    print("\n--- 4. 菜单栏操作 ---", flush=True)
    menu_bar = window.menuBar()
    if not menu_bar:
        record("菜单栏", "ERROR", "MenuBar not created")
        return
    for menu in menu_bar.findChildren(object):
        if menu.metaObject().className() != "QMenu":
            continue
        menu_title = menu.title()
        if not menu_title:
            continue
        for action in menu.actions():
            action_text = action.text()
            if not action_text or action.isSeparator():
                continue
            test_name = f"Menu [{menu_title}] -> [{action_text}]"
            if not action.isEnabled():
                record(test_name, "NOOP", "disabled")
                continue
            if action.menu():
                record(test_name, "NOOP", "submenu")
                continue
            safe_run(test_name, lambda a=action: a.trigger())


def test_toolbar_actions(window):
    print("\n--- 5. 工具栏按钮点击 ---", flush=True)
    toolbar_list = [t for t in window.findChildren(object) if t.metaObject().className() == "QToolBar"]
    for toolbar in toolbar_list:
        tb_name = toolbar.windowTitle()
        for action in toolbar.actions():
            action_text = action.text()
            if not action_text or action.isSeparator():
                continue
            test_name = f"Toolbar [{tb_name}] -> [{action_text}]"
            if not action.isEnabled():
                record(test_name, "NOOP", "disabled")
                continue
            safe_run(test_name, lambda a=action: a.trigger())


def test_dashboard_buttons(window):
    print("\n--- 6. Dashboard 按钮 ---", flush=True)
    dashboard = window._dashboard_page
    if not dashboard:
        record("Dashboard", "ERROR", "DashboardPage not created")
        return
    btn_list = [b for b in dashboard.findChildren(object) if b.metaObject().className() == "QPushButton"]
    for btn in btn_list:
        btn_text = btn.text().strip()
        if not btn_text:
            continue
        test_name = f"Dashboard [{btn_text}]"
        if not btn.isEnabled():
            record(test_name, "NOOP", "disabled")
            continue
        safe_run(test_name, lambda b=btn: b.click())


def test_dock_panels(window):
    print("\n--- 7. DockWidget面板 ---", flush=True)
    if window._diagnostic_dock:
        safe_run("Show diagnostic dock", lambda: window._diagnostic_dock.show())
        safe_run("Hide diagnostic dock", lambda: window._diagnostic_dock.hide())
    else:
        record("Diagnostic dock", "WARN", "not created")

    if window._spec_check_dock:
        safe_run("Show spec_check dock", lambda: window._spec_check_dock.show())
        safe_run("Hide spec_check dock", lambda: window._spec_check_dock.hide())
    else:
        record("SpecCheck dock", "WARN", "not created")


def print_summary():
    print("\n" + "=" * 70, flush=True)
    print("  测试结果汇总", flush=True)
    print("=" * 70, flush=True)

    crash_list = [r for r in results if r["status"] == "CRASH"]
    error_list = [r for r in results if r["status"] == "ERROR"]
    warn_list = [r for r in results if r["status"] == "WARN"]
    noop_list = [r for r in results if r["status"] == "NOOP"]
    pass_list = [r for r in results if r["status"] == "PASS"]

    print(f"\n  Total: {len(results)} tests", flush=True)
    print(f"  PASS:  {len(pass_list)}", flush=True)
    print(f"  CRASH: {len(crash_list)}", flush=True)
    print(f"  ERROR: {len(error_list)}", flush=True)
    print(f"  WARN:  {len(warn_list)}", flush=True)
    print(f"  NOOP:  {len(noop_list)}", flush=True)

    if crash_list:
        print("\n  CRASH details:", flush=True)
        for r in crash_list:
            print(f"    * {r['test']}", flush=True)
            print(f"      {r['detail']}", flush=True)

    if error_list:
        print("\n  ERROR details:", flush=True)
        for r in error_list:
            print(f"    * {r['test']}", flush=True)
            print(f"      {r['detail']}", flush=True)

    if warn_list:
        print("\n  WARN details:", flush=True)
        for r in warn_list:
            print(f"    * {r['test']}", flush=True)
            print(f"      {r['detail']}", flush=True)

    print("\n" + "=" * 70, flush=True)


def run_tests(window):
    test_toolbox_navigation(window)
    test_tab_navigation(window)
    test_sidebar_buttons(window)
    test_menu_actions(window)
    test_toolbar_actions(window)
    test_dashboard_buttons(window)
    test_dock_panels(window)
    print_summary()
    QApplication.quit()


def main():
    app = QApplication(sys.argv)

    try:
        from src.ui.widgets.st_lexer import QsciLexerST
        if not hasattr(QsciLexerST, 'previousLineStyle'):
            QsciLexerST.previousLineStyle = lambda self, start: -1
    except ImportError:
        pass

    from src.ui.main_window import MainWindow
    window = MainWindow()
    window.show()

    print("", flush=True)
    print("=" * 70, flush=True)
    print("  SW-2026-005 UI Auto Test", flush=True)
    print("=" * 70, flush=True)

    QTimer.singleShot(1000, lambda: run_tests(window))

    app.exec_()

    if hasattr(window, '_cleanup_resources'):
        window._cleanup_resources()
    import sip
    sip.delete(window)
    app.processEvents()
    del app


if __name__ == "__main__":
    main()
