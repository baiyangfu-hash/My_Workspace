# -*- coding: utf-8 -*-
"""
菜单管理器 - 负责构建和管理所有菜单项

从main_window.py的_init_menu_bar()方法提取，
实现菜单创建逻辑的独立封装，降低MainWindow复杂度。

职责:
- 构建完整菜单栏 (文件/编辑/工具/视图/帮助)
- 管理菜单项的状态和可见性
- 通过EventBus发射菜单事件
- 处理最近项目列表动态更新
"""
from pathlib import Path
from typing import Optional, Callable

from PyQt5.QtWidgets import (
    QMainWindow,
    QMenuBar,
    QMenu,
    QAction,
    QMessageBox,
)
from PyQt5.QtGui import QIcon

from src.core.event_bus import EventBus
from src.core.constants import APP_NAME, VERSION
from src.core.config import ConfigLoader
from src.core.settings import SettingsManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class MenuManager:
    """
    菜单管理器

    使用方式:
        menu_manager = MenuManager(main_window, event_bus)
        menu_bar = menu_manager.build()

    设计原则:
        - 单一职责: 只负责菜单的创建和管理
        - 事件驱动: 通过EventBus发射信号，不直接调用业务逻辑
        - 可扩展: 支持动态添加菜单项和子菜单
    """

    def __init__(self, parent: QMainWindow, event_bus: EventBus):
        """
        初始化菜单管理器

        Args:
            parent: 主窗口实例 (QMainWindow)
            event_bus: 全局事件总线实例
        """
        self._parent = parent
        self._event_bus = event_bus
        self._menu_bar: Optional[QMenuBar] = None
        self._recent_menu: Optional[QMenu] = None

    def build(self) -> QMenuBar:
        """
        构建完整菜单栏并返回

        Returns:
            QMenuBar: 构建完成的菜单栏对象
        """
        self._menu_bar = self._parent.menuBar()

        # 按顺序创建各菜单
        file_menu = self._create_file_menu()
        edit_menu = self._create_edit_menu()
        tools_menu = self._create_tools_menu()
        view_menu = self._create_view_menu()
        help_menu = self._create_help_menu()

        logger.debug("菜单栏构建完成")
        return self._menu_bar

    def _create_file_menu(self) -> QMenu:
        """
        创建文件菜单

        菜单项:
        - 新建项目 (Ctrl+N)
        - 打开项目 (Ctrl+O)
        - 最近打开 (子菜单)
        - 保存 (Ctrl+S)
        - 设置 (Ctrl+,)
        - 退出 (Ctrl+Q)

        Returns:
            QMenu: 文件菜单对象
        """
        menu = self._menu_bar.addMenu("\U0001F4C4 文件(&F)")

        # 新建项目
        new_action = QAction("\u002B 新建项目", self._parent)
        new_action.setShortcut("Ctrl+N")
        new_action.setStatusTip("创建新的PLC项目")
        new_action.triggered.connect(self._on_new_project)
        menu.addAction(new_action)

        # 打开项目
        open_action = QAction("\U0001F4C2 打开项目...", self._parent)
        open_action.setShortcut("Ctrl+O")
        open_action.setStatusTip("打开已有项目")
        open_action.triggered.connect(self._on_open_project)
        menu.addAction(open_action)

        # 最近打开的项目 (子菜单)
        self._recent_menu = menu.addMenu("\U0001F552 最近打开")
        self._refresh_recent_projects()

        menu.addSeparator()

        # 保存
        save_action = QAction("\U0001F4BE 保存", self._parent)
        save_action.setShortcut("Ctrl+S")
        save_action.setStatusTip("保存当前工作")
        save_action.triggered.connect(self._on_save)
        menu.addAction(save_action)

        menu.addSeparator()

        # 设置
        settings_action = QAction("\u2699\uFE0F 设置", self._parent)
        settings_action.setShortcut("Ctrl+,")
        settings_action.setStatusTip("系统设置")
        settings_action.triggered.connect(self._on_settings)
        menu.addAction(settings_action)

        menu.addSeparator()

        # 退出
        exit_action = QAction("\U0001F6D1 退出", self._parent)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("退出应用程序")
        exit_action.triggered.connect(self._parent.close)
        menu.addAction(exit_action)

        return menu

    def _create_edit_menu(self) -> QMenu:
        """
        创建编辑菜单

        菜单项:
        - 撤销 (Ctrl+Z)
        - 重做 (Ctrl+Y)
        - 查找 (Ctrl+F)
        - 替换 (Ctrl+H)

        Returns:
            QMenu: 编辑菜单对象
        """
        menu = self._menu_bar.addMenu("\u270F\uFE0F 编辑(&E)")

        undo_action = QAction("\u21A6 撤销", self._parent)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.setEnabled(False)
        menu.addAction(undo_action)

        redo_action = QAction("\u21A9 重做", self._parent)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.setEnabled(False)
        menu.addAction(redo_action)

        menu.addSeparator()

        find_action = QAction("\U0001F50D 查找", self._parent)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self._on_find)
        menu.addAction(find_action)

        replace_action = QAction("\U0001F502 替换", self._parent)
        replace_action.setShortcut("Ctrl+H")
        replace_action.triggered.connect(self._on_replace)
        menu.addAction(replace_action)

        return menu

    def _create_tools_menu(self) -> QMenu:
        """
        创建工具菜单

        菜单项:
        - 规范检查 (F5) - 改进为真实功能
        - 深度诊断 (F6) - 新增
        - 运行测试 (F7) - 新增
        - 变量检查
        - 生成报告

        Returns:
            QMenu: 工具菜单对象
        """
        menu = self._menu_bar.addMenu("\U0001F527 \u5DE5\u5177(&T)")

        # 规范检查（改进为真实功能）
        check_spec_action = QAction("\u2705 \u89C4\u8303\u68C0\u67E5", self._parent)
        check_spec_action.setShortcut("F5")
        check_spec_action.setStatusTip("\u8FD0\u884C\u89C4\u8303\u68C0\u67E5")
        check_spec_action.triggered.connect(self._on_run_check)
        menu.addAction(check_spec_action)

        # 深度诊断（新增）
        diagnostic_action = QAction(
            "\U0001F52C \u6DF1\u5EA6\u8BCA\u65AD(&D)", self._parent
        )
        diagnostic_action.setShortcut("F6")
        diagnostic_action.setStatusTip(
            "\u8FD0\u884CLSP\u517C\u5BB9\u6027\u8BCA\u65AD\u548C\u9879\u76EE\u5065\u5EB7\u5EA6\u5206\u6790"
        )
        diagnostic_action.triggered.connect(self._on_run_diagnostic)
        menu.addAction(diagnostic_action)

        # 运行测试（新增）
        test_action = QAction(
            "\u25B6 \u8FD0\u884C\u6D4B\u8BD5(&T)", self._parent
        )
        test_action.setShortcut("F7")
        test_action.setStatusTip(
            "\u6267\u884CPLC\u6D4B\u8BD5\u7528\u4F8B"
        )
        test_action.triggered.connect(self._on_run_tests)
        menu.addAction(test_action)

        menu.addSeparator()

        # 变量检查
        var_check_action = QAction(
            "\U0001F9EA \u53D8\u91CF\u68C0\u67E5", self._parent
        )
        var_check_action.setStatusTip("\u8FD0\u884C\u53D8\u91CF\u68C0\u67E5")
        var_check_action.triggered.connect(self._on_variable_check)
        menu.addAction(var_check_action)

        menu.addSeparator()

        # 生成报告
        gen_report_action = QAction(
            "\U0001F4CB \u751F\u6210\u62A5\u544A", self._parent
        )
        gen_report_action.setStatusTip("\u751F\u6210\u9879\u76EE\u62A5\u544A")
        gen_report_action.triggered.connect(self._on_generate_report)
        menu.addAction(gen_report_action)

        return menu

    def _create_view_menu(self) -> QMenu:
        """
        创建视图菜单

        菜单项:
        - 底部面板 (子菜单: 诊断面板/测试运行器)
        - 主题 (子菜单: 浅色/深色)

        Returns:
            QMenu: 视图菜单对象
        """
        menu = self._menu_bar.addMenu("\U0001F441 视图(&V)")

        # 底部面板子菜单
        panels_menu = menu.addMenu("\U0001F4CA 底部面板")

        # 诊断面板
        diagnostic_action = QAction("\U0001F52C 深度诊断面板", self._parent)
        diagnostic_action.setCheckable(True)
        diagnostic_action.setShortcut("Ctrl+D")
        diagnostic_action.setStatusTip("显示/隐藏深度诊断面板")
        diagnostic_action.triggered.connect(self._toggle_diagnostic_panel)
        panels_menu.addAction(diagnostic_action)
        self._diagnostic_action = diagnostic_action

        menu.addSeparator()

        # 主题子菜单
        theme_menu = menu.addMenu("\U0001F3A8 主题")

        # 浅色主题
        light_theme_action = QAction("\u2600\uFE0F 浅色主题", self._parent)
        light_theme_action.setStatusTip("切换到浅色主题")
        light_theme_action.triggered.connect(lambda: self._switch_theme("light"))
        theme_menu.addAction(light_theme_action)

        # 深色主题
        dark_theme_action = QAction("\u263E\uFE0F 深色主题", self._parent)
        dark_theme_action.setStatusTip("切换到深色主题")
        dark_theme_action.triggered.connect(lambda: self._switch_theme("dark"))
        theme_menu.addAction(dark_theme_action)

        return menu

    def _toggle_diagnostic_panel(self):
        """切换诊断面板的显示/隐藏状态"""
        main_window = self._parent
        if hasattr(main_window, '_diagnostic_dock') and main_window._diagnostic_dock:
            is_visible = main_window._diagnostic_dock.isVisible()
            if is_visible:
                main_window._diagnostic_dock.hide()
                self._diagnostic_action.setChecked(False)
            else:
                main_window._diagnostic_dock.show()
                main_window._diagnostic_dock.raise_()
                self._diagnostic_action.setChecked(True)

    def _create_help_menu(self) -> QMenu:
        """
        创建帮助菜单

        菜单项:
        - 关于

        Returns:
            QMenu: 帮助菜单对象
        """
        menu = self._menu_bar.addMenu("\u2753 帮助(&H)")

        # 关于
        about_action = QAction("\u2139\uFE0F 关于", self._parent)
        about_action.setStatusTip(f"关于 {APP_NAME}")
        about_action.triggered.connect(self._on_about)
        menu.addAction(about_action)

        return menu

    # ===== 事件处理方法 =====

    def _on_new_project(self):
        """新建项目 - 打开新建项目向导对话框"""
        try:
            from ..dialogs.new_project_dialog import NewProjectDialog

            dialog = NewProjectDialog(self._parent)
            if dialog.exec_() == dialog.Accepted:
                project_path = dialog.get_created_project_path()
                project_data = dialog.get_project_data()

                if project_path and project_data:
                    self._event_bus.project_created.emit(str(project_path))

                    project_id = project_data.get("project_id", "")
                    project_name = project_data.get("project_name", "")
                    self._parent.statusBar().showMessage(
                        f"\u002B 项目已创建: {project_id}_{project_name}"
                    )
                    logger.info(f"新建项目成功: {project_id}_{project_name} @ {project_path}")

                    QMessageBox.information(
                        self._parent,
                        "\u2705 项目创建成功",
                        (
                            f"项目已成功创建!\n\n"
                            f"  编号: {project_id}\n"
                            f"  名称: {project_name}\n"
                            f"  路径: {project_path}\n\n"
                            f"项目树已自动刷新。"
                        ),
                        QMessageBox.Ok,
                    )
                else:
                    logger.warning("向导返回 Accepted 但无有效项目路径")

        except ImportError as e:
            logger.error(f"无法导入新建项目对话框: {e}")
            QMessageBox.information(
                self._parent, "提示", "新建项目功能正在开发中..."
            )
        except Exception as e:
            logger.exception(f"新建项目操作失败: {e}")
            QMessageBox.critical(
                self._parent,
                "\u274C 错误",
                f"新建项目失败:\n\n{str(e)}",
                QMessageBox.Ok,
            )

    def _on_open_project(self):
        """打开已有项目"""
        from PyQt5.QtWidgets import QFileDialog

        project_dir = QFileDialog.getExistingDirectory(
            self._parent, "选择项目目录", "./Projects"
        )
        if project_dir:
            self._parent.statusBar().showMessage(
                f"\U0001F4C2 已打开项目: {Path(project_dir).name}"
            )
            SettingsManager.add_recent_project(
                project_dir, Path(project_dir).name
            )
            self._refresh_recent_projects()
            self._event_bus.project_opened.emit(project_dir)
            logger.info(f"打开项目目录: {project_dir}")

    def _on_save(self):
        self._parent.statusBar().showMessage("\U0001F4BE 已保存")
        logger.debug("执行保存操作")

    def _on_find(self):
        self._parent.statusBar().showMessage("\U0001F50D 查找功能开发中...")

    def _on_replace(self):
        self._parent.statusBar().showMessage("\U0001F502 替换功能开发中...")

    def _on_settings(self):
        """打开系统设置对话框"""
        try:
            from ..dialogs.settings_dialog import SettingsDialog

            dialog = SettingsDialog(self._parent)
            result = dialog.exec_()
            if result == dialog.Accepted:
                self._event_bus.settings_changed.emit()
                logger.info("系统设置已更新")

        except ImportError as e:
            logger.error(f"无法导入设置对话框: {e}")
            self._fallback_settings()
        except Exception as e:
            logger.exception(f"打开设置对话框失败: {e}")
            QMessageBox.critical(
                self._parent, "错误", f"打开设置失败: {str(e)}"
            )

    def _fallback_settings(self):
        """回退的内联设置对话框 (兼容性保障)"""
        from PyQt5.QtWidgets import (
            QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
            QLineEdit, QComboBox, QCheckBox,
            QSpinBox, QWidget, QPushButton,
        )

        dialog = QDialog(self._parent)
        dialog.setWindowTitle("\u2699\uFE0F 系统设置")
        dialog.setMinimumSize(550, 420)

        layout = QVBoxLayout(dialog)

        form_widget = QWidget()
        form = QFormLayout(form_widget)

        setting_default_path = QLineEdit(
            SettingsManager.get("default_project_root", "./Projects") or ""
        )
        setting_auto_save = QCheckBox("自动保存")
        setting_auto_save.setChecked(SettingsManager.get("auto_backup", True))

        form.addRow("默认项目路径:", setting_default_path)
        form.addRow("", setting_auto_save)
        layout.addWidget(form_widget)

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("保存")
        cancel_btn = QPushButton("取消")
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        if dialog.exec_() == QDialog.Accepted:
            SettingsManager.set(
                "default_project_root",
                setting_default_path.text().strip(),
            )
            SettingsManager.set("auto_backup", setting_auto_save.isChecked())
            SettingsManager.save()
            QMessageBox.information(self._parent, "成功", "设置已保存")

    def _on_run_check(self):
        """
        运行规范检查

        打开规范检查面板并开始检查当前项目。
        优先使用Tab导航（规范检查面板在TabWidget中），
        如果存在DockWidget则使用DockWidget。
        """
        try:
            main_window = self._parent
            project_path = self._get_current_project_path()

            if getattr(main_window, '_spec_check_dock', None):
                main_window._spec_check_dock.show()
                main_window._spec_check_dock.raise_()
            elif hasattr(main_window, '_navigate_to_tab'):
                main_window._navigate_to_tab(main_window.TAB_SPEC_CHECK)

            if project_path and getattr(main_window, '_spec_check_tab_panel', None):
                if hasattr(main_window._spec_check_tab_panel, 'start_check'):
                    main_window._spec_check_tab_panel.start_check(project_path)
                self._parent.statusBar().showMessage(
                    f"\u2705 \u5F00\u59CB\u89C4\u8303\u68C0\u67E5: {project_path}"
                )
                logger.info(f"F5 \u89C4\u8303\u68C0\u67E5\u5DF2\u89E6\u53D1: {project_path}")
            else:
                QMessageBox.information(
                    self._parent,
                    "\u2705 \u89C4\u8303\u68C0\u67E5",
                    "\u89C4\u8303\u68C0\u67E5\u9762\u677F\u5DF2\u6253\u5F00\n\n"
                    "\u8BF7\u5148\u5728\u9879\u76EE\u6811\u4E2D\u9009\u62E9\u4E00\u4E2A\u9879\u76EE\uFF0C\n"
                    "\u7136\u540E\u70B9\u51FB\"\u5F00\u59CB\u68C0\u67E5\"\u6309\u94AE\u3002",
                    QMessageBox.Ok,
                )

        except Exception as e:
            logger.exception(f"\u8FD0\u884C\u89C4\u8303\u68C0\u67E5\u5931\u8D25: {e}")
            QMessageBox.critical(
                self._parent,
                "\u274C \u9519\u8BEF",
                f"\u89C4\u8303\u68C0\u67E5\u5931\u8D25:\n{str(e)}",
                QMessageBox.Ok,
            )

    def _on_run_diagnostic(self):
        """
        运行深度诊断（新增功能 - F6快捷键）

        打开诊断面板并执行LSP兼容性诊断和健康度分析
        """
        try:
            main_window = self._parent

            if hasattr(main_window, '_diagnostic_dock') and \
               main_window._diagnostic_dock:
                main_window._diagnostic_dock.show()
                main_window._diagnostic_dock.raise_()

                project_path = self._get_current_project_path()

                if project_path and main_window._diagnostic_panel:
                    main_window._diagnostic_panel.set_project_path(project_path)
                    main_window._diagnostic_panel.run_diagnostic('full')

                    self._parent.statusBar().showMessage(
                        f"\U0001F52C \u5F00\u59CB\u6DF1\u5EA6\u8BCA\u65AD: {project_path}"
                    )
                    logger.info(f"F6 深度诊断已触发: {project_path}")
                else:
                    QMessageBox.information(
                        self._parent,
                        "\U0001F52C \u6DF1\u5EA6\u8BCA\u65AD",
                        "\u8BCA\u65AD\u9762\u677F\u5DF2\u6253\u5F00\n\n"
                        "\u8BF7\u5148\u9009\u62E9\u4E00\u4E2aPLC\u9879\u76EE\uFF0C\n"
                        "\u7136\u540E\u70B9\u51FB\"\u5F00\u59CB\u8BCA\u65AD\"\u6309\u94AE\u3002",
                        QMessageBox.Ok,
                    )

        except Exception as e:
            logger.exception(f"运行深度诊断失败: {e}")
            QMessageBox.critical(
                self._parent,
                "\u274C \u9519\u8BEF",
                f"\u6DF1\u5EA6\u8BCA\u65AD\u5931\u8D25:\n{str(e)}",
                QMessageBox.Ok,
            )

    def _on_run_tests(self):
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(
            self._parent,
            "\u25B6 运行测试",
            "测试运行器功能正在开发中\n\n将在 V2.1+ 版本提供。",
            QMessageBox.Ok,
        )

    def _get_current_project_path(self) -> Optional[str]:
        """
        获取当前选中项目的路径（辅助方法）

        Returns:
            str或None: 项目路径字符串
        """
        try:
            main_window = self._parent

            if hasattr(main_window, '_project_tree_widget'):
                project_tree = main_window._project_tree_widget

                for attr_name in [
                    'current_project',
                    'selected_project',
                    'active_project',
                ]:
                    if hasattr(project_tree, attr_name):
                        project = getattr(project_tree, attr_name)
                        if project and hasattr(project, 'path'):
                            return project.path

            from src.core.settings import SettingsManager
            recent_projects = SettingsManager.get_recent_projects()
            if recent_projects:
                return recent_projects[0].get('path', '')

            return None

        except Exception as e:
            logger.warning(f"获取当前项目路径失败: {e}")
            return None

    def _on_variable_check(self):
        """运行变量检查 - 通过EventBus路由到MainWindow处理"""
        self._event_bus.variable_check_request.emit()

    def _on_generate_report(self):
        """生成报告"""
        QMessageBox.information(
            self._parent,
            "\U0001F4CB 生成报告",
            "报告生成功能正在开发中...",
        )

    def _switch_theme(self, theme_name: str):
        """切换界面主题"""
        SettingsManager.set("theme", theme_name)
        SettingsManager.save()
        self._event_bus.theme_changed.emit(theme_name)
        self._parent.statusBar().showMessage(
            f"\U0001F3A8 主题已切换为: "
            f"{'浅色' if theme_name == 'light' else '深色'}"
        )
        logger.info(f"主题切换为: {theme_name}")

    def _on_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self._parent,
            f"\u2139\uFE0F 关于 {APP_NAME}",
            f"<h2>{APP_NAME}</h2>"
            f"<p><b>版本:</b> {VERSION}</p>"
            f"<p>{ConfigLoader.get('description', '')}</p>"
            f"<hr>"
            f"<p>技术栈: Python 3.8+ / PyQt5 / SQLite</p>"
            f"<p>支持PLC: Siemens / Beckhoff / Omron / Codesys</p>"
            f"<p>&copy; 2026 Trae AI</p>",
        )

    def _refresh_recent_projects(self):
        """刷新最近项目列表"""
        if not self._recent_menu:
            return

        self._recent_menu.clear()

        recent_projects = SettingsManager.get_recent_projects()

        if not recent_projects:
            no_recent_action = QAction("暂无最近项目", self._parent)
            no_recent_action.setEnabled(False)
            self._recent_menu.addAction(no_recent_action)
            return

        for proj in recent_projects[:10]:
            path = proj.get("path", "")
            name = proj.get("name", Path(path).name)

            action = QAction(f"{name}", self._parent)
            action.setStatusTip(path)
            action.triggered.connect(lambda checked, p=path: self._open_recent_project(p))
            self._recent_menu.addAction(action)

        self._recent_menu.addSeparator()

        clear_action = QAction("清除历史记录", self._parent)
        clear_action.triggered.connect(self._clear_recent_projects)
        self._recent_menu.addAction(clear_action)

    def _open_recent_project(self, project_path: str):
        """打开最近项目"""
        self._event_bus.project_opened.emit(project_path)
        self._parent.statusBar().showMessage(
            f"\U0001F4C2 已打开项目: {Path(project_path).name}"
        )
        logger.info(f"从最近列表打开项目: {project_path}")

    def _clear_recent_projects(self):
        """清除最近项目记录"""
        reply = QMessageBox.question(
            self._parent,
            "确认清除",
            "确定要清除所有最近项目记录吗?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            SettingsManager.set("recent_projects", [])
            SettingsManager.save()
            self._refresh_recent_projects()
            logger.info("已清除最近项目记录")
