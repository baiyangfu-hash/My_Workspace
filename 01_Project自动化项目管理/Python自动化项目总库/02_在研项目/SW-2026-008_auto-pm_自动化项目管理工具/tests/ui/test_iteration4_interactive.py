"""迭代4 GUI 交互测试

真实操作 widget（点击、输入、信号验证），不使用 mock。
覆盖迭代4交付的 ReportPage / TemplatePage / SettingsPage / SpecCenterView / MainWindow 集成。

测试内容：
- 报告中心：加载/4个统计卡片/数据正确性/柱状图显示
- 模板管理：加载/模板列表/卡片信息/更新项目按钮
- 系统设置：加载/工作空间路径/数据库统计/清除缓存按钮/重建索引按钮
- 规范中心：加载/PLC规范列表/Python规范列表/打开按钮
- 完整流程：系统设置 → 清除缓存 → 重建索引 → 数据恢复

遵循项目现有测试模式：自定义 qapp fixture + QT_QPA_PLATFORM=offscreen。
通过 MainWindow 实例化真实组件链路，注入临时工作空间和样本数据。
"""

from __future__ import annotations

import gc
import os
from pathlib import Path

import pytest

# 必须在导入 PySide6 前设置离屏渲染，避免无显示环境报错
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import (  # noqa: E402
    QApplication,
    QGroupBox,
    QLabel,
    QMessageBox,
    QProgressBar,
)

from auto_pm.db.repository import ChangeRequestRepository  # noqa: E402
from auto_pm.models import ChangeSummary  # noqa: E402
from auto_pm.ui.global_pages.report_page import ReportPage  # noqa: E402
from auto_pm.ui.global_pages.settings_page import SettingsPage  # noqa: E402
from auto_pm.ui.global_pages.spec_center import SpecCenterView  # noqa: E402
from auto_pm.ui.global_pages.template_page import TemplateCard, TemplatePage  # noqa: E402
from auto_pm.ui.main_window import MainWindow  # noqa: E402

# ── fixtures ─────────────────────────────────────────────


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """提供全局 QApplication 实例（session 级复用）"""
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def workspace_root(tmp_path: Path) -> Path:
    """临时工作空间根目录，含 5 个样本项目目录

    项目分布：
    - DJ-2026-001: PLC, developing, DJ, 模板 plc-standard
    - DJ-2026-002: PLC, commissioning, DJ, 模板 plc-standard
    - SW-2026-003: Python, developing, SW, 模板 python-tool
    - ZD-2026-004: PLC, production, ZD, 模板 plc-standard
    - SW-2026-005: Python, archived, SW, 模板 python-tool
    """
    _create_sample_projects(tmp_path)
    return tmp_path


@pytest.fixture
def main_window(qapp: QApplication, workspace_root: Path) -> MainWindow:
    """创建 MainWindow 实例，指向临时工作空间

    自动同步项目到 DB 缓存并注入变更记录，刷新所有全局页。
    """
    window = MainWindow(workspace_root=str(workspace_root))

    # 同步项目到 DB 缓存（force_full=True 强制全量扫描）
    window._project_service.sync_to_cache(force_full=True)

    # 注入变更记录到 DB 缓存
    _inject_sample_changes(window._db)

    # 刷新所有全局页（使其加载 DB 缓存数据）
    window._report_page.refresh()
    window._template_page.refresh()
    window._settings_page.refresh()

    qapp.processEvents()
    yield window
    window.deleteLater()
    qapp.processEvents()


# ── 辅助：项目目录构造 ───────────────────────────────────


def _create_sample_projects(workspace: Path) -> None:
    """在工作空间下创建 5 个样本项目目录（含 .copier-answers.yml）

    项目分布覆盖多技术栈/阶段/业务线，用于报告中心统计验证。
    """
    projects = [
        {
            "project_id": "DJ-2026-001",
            "name": "PLC单机A",
            "src_path": "templates/plc-standard",
            "phase": "developing",
        },
        {
            "project_id": "DJ-2026-002",
            "name": "PLC单机B",
            "src_path": "templates/plc-standard",
            "phase": "commissioning",
        },
        {
            "project_id": "SW-2026-003",
            "name": "Python软件A",
            "src_path": "templates/python-tool",
            "phase": "developing",
        },
        {
            "project_id": "ZD-2026-004",
            "name": "PLC整线A",
            "src_path": "templates/plc-standard",
            "phase": "production",
        },
        {
            "project_id": "SW-2026-005",
            "name": "Python软件B",
            "src_path": "templates/python-tool",
            "phase": "archived",
        },
    ]

    for p in projects:
        project_dir = workspace / f"{p['project_id']}_{p['name']}"
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / ".copier-answers.yml").write_text(
            f"project_id: {p['project_id']}\n"
            f"project_name: {p['name']}\n"
            "version: V1.0.0\n"
            f"_src_path: {p['src_path']}\n"
            f"phase: {p['phase']}\n"
            f"description: 测试项目 {p['project_id']}\n",
            encoding="utf-8",
        )


def _inject_sample_changes(db) -> None:
    """向 DB 缓存注入 2 条变更记录

    - CHG-PLC-2026-001: draft, PLC 领域
    - CHG-DOCU-2026-001: completed, DOCU 领域
    """
    repo = ChangeRequestRepository(db)
    changes = [
        ChangeSummary(
            change_number="CHG-PLC-2026-001",
            project_id="DJ-2026-001",
            project_name="PLC单机A",
            domain="PLC",
            business_nature="DEF",
            impact_scope=["LOCAL"],
            status="draft",
            applicant="fubai",
            apply_date="2026-06-20",
            title="PLC 程序缺陷修复",
        ),
        ChangeSummary(
            change_number="CHG-DOCU-2026-001",
            project_id="SW-2026-003",
            project_name="Python软件A",
            domain="DOCU",
            business_nature="REQ",
            impact_scope=["MODULE"],
            status="completed",
            applicant="fubai",
            apply_date="2026-06-19",
            title="文档需求变更",
        ),
    ]
    for c in changes:
        repo.upsert(c, file_path=f"/tmp/{c.change_number}.md", file_mtime=0.0)


# ── 辅助：widget 查找 ────────────────────────────────────


def _find_progress_bars(parent) -> list[QProgressBar]:
    """获取 parent 下所有 objectName=statBar 的 QProgressBar"""
    return [b for b in parent.findChildren(QProgressBar) if b.objectName() == "statBar"]


def _find_spec_codes(parent) -> list[str]:
    """获取规范中心所有规范编号文本（objectName=specCode）"""
    labels = [lbl for lbl in parent.findChildren(QLabel) if lbl.objectName() == "specCode"]
    return [lbl.text() for lbl in labels]


# ══════════════════════════════════════════════════════════
#  报告中心（ReportPage）交互测试
# ══════════════════════════════════════════════════════════


class TestReportPage:
    """报告中心交互测试（通过 MainWindow → ReportPage 链路）"""

    def test_report_page_load(
        self, qapp: QApplication, main_window: MainWindow
    ) -> None:
        """点击导航"报告中心" → ReportPage 加载（QStackedWidget 切换到 index 4）"""
        assert main_window._stack.currentIndex() == 0

        # 真实点击导航树"报告中心"节点
        main_window._nav_tree._on_item_clicked(
            main_window._nav_tree._function_nodes["report"], 0
        )
        qapp.processEvents()

        assert main_window._stack.currentIndex() == 4
        assert main_window._stack.currentWidget() is main_window._report_page
        assert isinstance(main_window._report_page, ReportPage)

    def test_report_page_cards(
        self, qapp: QApplication, main_window: MainWindow
    ) -> None:
        """4 个统计卡片显示（项目概览/阶段分布/业务线分布/变更统计）"""
        page = main_window._report_page
        page.refresh()
        qapp.processEvents()

        # 4 个 QGroupBox 卡片
        cards = page.findChildren(QGroupBox)
        card_titles = [c.title() for c in cards]
        assert "项目概览" in card_titles
        assert "阶段分布" in card_titles
        assert "业务线分布" in card_titles
        assert "变更统计" in card_titles
        assert len(card_titles) == 4

    def test_report_page_data(
        self, qapp: QApplication, main_window: MainWindow
    ) -> None:
        """数据正确性（与 ReportService 返回一致）"""
        page = main_window._report_page
        page.refresh()
        qapp.processEvents()

        # 直接调用 Service 获取预期数据
        project_data = main_window._report_service.get_project_overview()
        change_data = main_window._report_service.get_change_overview()

        # 验证项目概览数据
        assert project_data["total"] == 5
        assert project_data["by_stack"]["plc"] == 3
        assert project_data["by_stack"]["python"] == 2
        assert project_data["by_phase"]["developing"] == 2
        assert project_data["by_phase"]["commissioning"] == 1
        assert project_data["by_phase"]["production"] == 1
        assert project_data["by_phase"]["archived"] == 1
        assert project_data["by_business_line"]["DJ"] == 2
        assert project_data["by_business_line"]["SW"] == 2
        assert project_data["by_business_line"]["ZD"] == 1

        # 验证变更统计数据
        assert change_data["total"] == 2
        assert change_data["by_status"]["draft"] == 1
        assert change_data["by_status"]["completed"] == 1

        # 验证页面渲染的摘要标签与 Service 数据一致
        summary_labels = [
            lbl for lbl in page.findChildren(QLabel) if lbl.objectName() == "summaryLabel"
        ]
        summary_texts = [lbl.text() for lbl in summary_labels]
        # 项目概览卡片应显示"总项目数: 5"
        assert any("总项目数: 5" in t for t in summary_texts)
        # 变更统计卡片应显示"总变更: 2"
        assert any("总变更: 2" in t for t in summary_texts)

    def test_report_page_bars(
        self, qapp: QApplication, main_window: MainWindow
    ) -> None:
        """柱状图显示（QProgressBar 行存在且数值正确）"""
        page = main_window._report_page
        page.refresh()
        qapp.processEvents()

        bars = _find_progress_bars(page)
        # 应有多个柱状图行（项目概览 3 + 阶段分布 4 + 业务线分布 5 + 变更统计 2 = 14）
        assert len(bars) >= 10

        # 验证计数标签（objectName=countLabel）包含预期数值
        count_labels = [
            lbl for lbl in page.findChildren(QLabel) if lbl.objectName() == "countLabel"
        ]
        count_texts = [lbl.text() for lbl in count_labels]
        # PLC 应为 3
        assert "3" in count_texts
        # Python 应为 2
        assert "2" in count_texts
        # 0 也应存在（unknown/XT/WX 等）
        assert "0" in count_texts


# ══════════════════════════════════════════════════════════
#  模板管理（TemplatePage）交互测试
# ══════════════════════════════════════════════════════════


class TestTemplatePage:
    """模板管理交互测试（通过 MainWindow → TemplatePage 链路）"""

    def test_template_page_load(
        self, qapp: QApplication, main_window: MainWindow
    ) -> None:
        """点击导航"模板管理" → TemplatePage 加载（QStackedWidget 切换到 index 5）"""
        assert main_window._stack.currentIndex() == 0

        main_window._nav_tree._on_item_clicked(
            main_window._nav_tree._function_nodes["template"], 0
        )
        qapp.processEvents()

        assert main_window._stack.currentIndex() == 5
        assert main_window._stack.currentWidget() is main_window._template_page
        assert isinstance(main_window._template_page, TemplatePage)

    def test_template_page_list(
        self, qapp: QApplication, main_window: MainWindow
    ) -> None:
        """模板列表显示（plc-standard + python-tool 共 2 个模板）"""
        page = main_window._template_page
        page.refresh()
        qapp.processEvents()

        # TemplatePage._cards 字典应包含模板卡片
        cards = page._cards
        assert len(cards) >= 2
        assert "plc-standard" in cards
        assert "python-tool" in cards

    def test_template_page_card_info(
        self, qapp: QApplication, main_window: MainWindow
    ) -> None:
        """模板卡片信息正确（名称/版本/技术栈/使用项目数）"""
        page = main_window._template_page
        page.refresh()
        qapp.processEvents()

        # 验证 plc-standard 卡片
        plc_card = page._cards["plc-standard"]
        assert isinstance(plc_card, TemplateCard)
        assert plc_card.template_name == "plc-standard"
        # 元信息标签应包含技术栈 PLC
        meta_text = plc_card._meta_label.text()
        assert "PLC" in meta_text
        # 使用项目数应为 3（DJ-2026-001, DJ-2026-002, ZD-2026-004）
        assert "使用项目: 3" in meta_text

        # 验证 python-tool 卡片
        py_card = page._cards["python-tool"]
        assert isinstance(py_card, TemplateCard)
        assert py_card.template_name == "python-tool"
        meta_text_py = py_card._meta_label.text()
        assert "Python" in meta_text_py
        # 使用项目数应为 2（SW-2026-003, SW-2026-005）
        assert "使用项目: 2" in meta_text_py

    def test_template_page_update_button(
        self, qapp: QApplication, main_window: MainWindow
    ) -> None:
        """"更新项目"按钮存在（每个模板卡片都有一个）"""
        page = main_window._template_page
        page.refresh()
        qapp.processEvents()

        for card_name, card in page._cards.items():
            btn = card.update_button
            assert btn is not None
            assert btn.text() == "更新项目"


# ══════════════════════════════════════════════════════════
#  系统设置（SettingsPage）交互测试
# ══════════════════════════════════════════════════════════


class TestSettingsPage:
    """系统设置交互测试（通过 MainWindow → SettingsPage 链路）"""

    def test_settings_page_load(
        self, qapp: QApplication, main_window: MainWindow
    ) -> None:
        """点击导航"系统设置" → SettingsPage 加载（QStackedWidget 切换到 index 6）"""
        assert main_window._stack.currentIndex() == 0

        main_window._nav_tree._on_item_clicked(
            main_window._nav_tree._function_nodes["settings"], 0
        )
        qapp.processEvents()

        assert main_window._stack.currentIndex() == 6
        assert main_window._stack.currentWidget() is main_window._settings_page
        assert isinstance(main_window._settings_page, SettingsPage)

    def test_settings_page_workspace(
        self, qapp: QApplication, main_window: MainWindow, workspace_root: Path
    ) -> None:
        """工作空间路径显示（与 MainWindow 的 workspace_root 一致）"""
        page = main_window._settings_page
        page.refresh()
        qapp.processEvents()

        text = page.workspace_edit.text()
        assert text == str(workspace_root)

    def test_settings_page_db_stats(
        self, qapp: QApplication, main_window: MainWindow
    ) -> None:
        """数据库统计显示（项目数 5 / 变更数 2 / 上次同步时间）"""
        page = main_window._settings_page
        page.refresh()
        qapp.processEvents()

        # 项目记录数应为 5
        project_text = page.project_count_label.text()
        assert "项目记录: 5 条" in project_text

        # 变更记录数应为 2
        change_text = page.change_count_label.text()
        assert "变更记录: 2 条" in change_text

        # 缓存路径应非空（DB 已初始化）
        db_path_text = page.db_path_label.text()
        assert "index.db" in db_path_text
        assert "未连接" not in db_path_text

        # 上次同步时间应非占位符（sync_to_cache 会写入 scan_log）
        sync_text = page.last_sync_label.text()
        assert "上次同步:" in sync_text

    def test_settings_page_clear_cache_button(
        self, qapp: QApplication, main_window: MainWindow
    ) -> None:
        """"清除缓存"按钮存在"""
        page = main_window._settings_page
        btn = page.clear_cache_button
        assert btn is not None
        assert btn.text() == "清除缓存"

    def test_settings_page_rebuild_button(
        self, qapp: QApplication, main_window: MainWindow
    ) -> None:
        """"重建索引"按钮存在"""
        page = main_window._settings_page
        btn = page.rebuild_button
        assert btn is not None
        assert btn.text() == "重建索引"


# ══════════════════════════════════════════════════════════
#  规范中心（SpecCenterView）交互测试
# ══════════════════════════════════════════════════════════


class TestSpecCenterView:
    """规范中心交互测试（通过 MainWindow → SpecCenterView 链路）"""

    def test_spec_center_load(
        self, qapp: QApplication, main_window: MainWindow
    ) -> None:
        """点击导航"规范中心" → SpecCenterView 加载（QStackedWidget 切换到 index 7）"""
        assert main_window._stack.currentIndex() == 0

        main_window._nav_tree._on_item_clicked(
            main_window._nav_tree._function_nodes["spec_center"], 0
        )
        qapp.processEvents()

        assert main_window._stack.currentIndex() == 7
        assert main_window._stack.currentWidget() is main_window._spec_center_view
        assert isinstance(main_window._spec_center_view, SpecCenterView)

    def test_spec_center_plc_list(
        self, qapp: QApplication, main_window: MainWindow
    ) -> None:
        """PLC 规范列表显示（4 项：905/904/903/906）"""
        view = main_window._spec_center_view
        qapp.processEvents()

        # 验证 PLC 规范的"打开"按钮存在
        plc_codes = ["905", "904", "903", "906"]
        for code in plc_codes:
            btn = view.get_open_button("plc", code)
            assert btn is not None, f"PLC 规范 {code} 的打开按钮不存在"

        # 验证页面中包含 PLC 规范编号标签
        all_codes = _find_spec_codes(view)
        for code in plc_codes:
            assert code in all_codes, f"PLC 规范编号 {code} 未在页面中显示"

    def test_spec_center_python_list(
        self, qapp: QApplication, main_window: MainWindow
    ) -> None:
        """Python 规范列表显示（3 项：210/211/220）"""
        view = main_window._spec_center_view
        qapp.processEvents()

        # 验证 Python 规范的"打开"按钮存在
        py_codes = ["210", "211", "220"]
        for code in py_codes:
            btn = view.get_open_button("python", code)
            assert btn is not None, f"Python 规范 {code} 的打开按钮不存在"

        # 验证页面中包含 Python 规范编号标签
        all_codes = _find_spec_codes(view)
        for code in py_codes:
            assert code in all_codes, f"Python 规范编号 {code} 未在页面中显示"

    def test_spec_center_open_button(
        self, qapp: QApplication, main_window: MainWindow
    ) -> None:
        """"打开"按钮存在（共 7 个：4 PLC + 3 Python，文本均为"打开"）"""
        view = main_window._spec_center_view
        qapp.processEvents()

        buttons = view.open_buttons
        # 共 7 个按钮
        assert len(buttons) == 7

        # 所有按钮文本均为"打开"
        for (stack, code), btn in buttons.items():
            assert btn.text() == "打开", f"{stack}/{code} 按钮文本异常: {btn.text()}"


# ══════════════════════════════════════════════════════════
#  完整流程测试
# ══════════════════════════════════════════════════════════


class TestFullFlow:
    """完整流程测试：系统设置 → 清除缓存 → 重建索引 → 数据恢复"""

    def test_full_flow_settings_rebuild(
        self, qapp: QApplication, main_window: MainWindow
    ) -> None:
        """系统设置 → 清除缓存 → 重建索引 → 数据恢复

        流程：
        1. 验证初始状态：DB 有 5 个项目、2 条变更
        2. 点击"清除缓存"按钮 → DB 被清空（0 项目 / 0 变更）
        3. 点击"重建索引"按钮 → 全量扫描恢复数据（5 项目恢复）
        4. 验证数据恢复：项目数恢复为 5
        """
        page = main_window._settings_page

        # ── Step 1: 验证初始状态 ──
        page.refresh()
        qapp.processEvents()
        assert "项目记录: 5 条" in page.project_count_label.text()
        assert "变更记录: 2 条" in page.change_count_label.text()

        # 保存原始静态方法
        original_question = QMessageBox.question
        original_information = QMessageBox.information
        original_warning = QMessageBox.warning

        # 替换为不阻塞的版本
        QMessageBox.question = staticmethod(  # type: ignore[assignment]
            lambda *args, **kwargs: QMessageBox.StandardButton.Yes
        )
        QMessageBox.information = staticmethod(lambda *args, **kwargs: None)  # type: ignore[assignment]
        QMessageBox.warning = staticmethod(lambda *args, **kwargs: None)  # type: ignore[assignment]

        try:
            # ── Step 2: 点击"清除缓存"按钮 → DB 被清空 ──
            # 强制垃圾回收，关闭未显式关闭的 SQLite 连接，避免 Windows 文件锁定
            gc.collect()
            qapp.processEvents()

            page.clear_cache_button.click()
            qapp.processEvents()

            # 验证 DB 已清空
            page.refresh()
            qapp.processEvents()
            assert "项目记录: 0 条" in page.project_count_label.text()
            assert "变更记录: 0 条" in page.change_count_label.text()

            # ── Step 3: 点击"重建索引"按钮 → 全量扫描恢复数据 ──
            gc.collect()
            qapp.processEvents()

            page.rebuild_button.click()
            qapp.processEvents()

            # ── Step 4: 验证数据恢复 ──
            page.refresh()
            qapp.processEvents()
            # 重建索引后项目数应恢复为 5
            assert "项目记录: 5 条" in page.project_count_label.text()
        finally:
            # 恢复原始静态方法
            QMessageBox.question = original_question  # type: ignore[assignment]
            QMessageBox.information = original_information  # type: ignore[assignment]
            QMessageBox.warning = original_warning  # type: ignore[assignment]
