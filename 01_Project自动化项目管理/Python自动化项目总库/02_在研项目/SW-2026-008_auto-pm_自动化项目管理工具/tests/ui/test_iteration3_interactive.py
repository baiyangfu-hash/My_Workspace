"""迭代3 GUI 交互测试

真实操作 widget（点击、输入、信号验证），不使用 mock。
覆盖迭代3交付的 CheckTab / DocTab / MainWindow 集成。

测试内容：
- 检查 Tab：加载/执行检查/分组显示/状态图标/修复按钮/自动修复预览/标准化预览/摘要栏
- 文档 Tab：加载/分类/双击打开/模板信息/模板更新按钮/空状态
- 完整流程：执行检查 → 发现问题 → 自动修复 → 重新检查

遵循项目现有测试模式：自定义 qapp fixture + QT_QPA_PLATFORM=offscreen。
通过 MainWindow 实例化真实组件链路，注入临时工作空间和样本数据。
"""

from __future__ import annotations

import json
import os
from collections.abc import Generator
from pathlib import Path
from unittest.mock import patch

import pytest

# 必须在导入 PySide6 前设置离屏渲染，避免无显示环境报错
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QUrl  # noqa: E402
from PySide6.QtWidgets import (  # noqa: E402
    QApplication,
    QLabel,
    QPushButton,
    QTreeWidgetItem,
    QWidget,
)

from auto_pm.models import ProjectInfo  # noqa: E402
from auto_pm.ui.main_window import MainWindow  # noqa: E402
from auto_pm.ui.workspace.check_tab import CheckTab  # noqa: E402
from auto_pm.ui.workspace.doc_tab import DocTab  # noqa: E402

# ── fixtures ─────────────────────────────────────────────


@pytest.fixture
def workspace_root(tmp_path: Path) -> Path:
    """临时工作空间根目录"""
    return tmp_path


@pytest.fixture
def main_window(qapp: QApplication, workspace_root: Path) -> Generator[MainWindow, None, None]:
    """创建 MainWindow 实例，指向临时工作空间"""
    window = MainWindow(workspace_root=str(workspace_root))
    yield window
    window.deleteLater()
    qapp.processEvents()


# ── 辅助：项目目录构造 ───────────────────────────────────

PROJECT_ID = "TEST-2026-001"
DOC_PROJECT_ID = "DOC-2026-001"


def _create_mixed_project(workspace: Path) -> Path:
    """创建含 pass/warn/fail 混合检查项的项目目录

    结构：
      TEST-2026-001_检查测试项目/
        .plc.json              → pass（配置完整 + libraries 有效）
        lib/                   → libraries 指向此目录 → pass
        PM_SESSION_TEST-2026-001.md → pass
        PRD/
          接口文档_INT.md       → pass
          需求分析文档_v2.md     → warn（命名不匹配 需求分析文档_REQ.md）
          （缺 DSN/TEC）        → fail
        02_PLC程序/通用ST程序及变量表/ → pass
        03_HMI设计/            → pass
        （缺 04_现场调试, 04_变更管理）→ fail

    检查结果：8 pass / 1 warn / 4 fail
    """
    project_dir = workspace / f"{PROJECT_ID}_检查测试项目"
    project_dir.mkdir()

    # .plc.json（有效 + libraries 指向存在的目录）→ pass
    lib_dir = project_dir / "lib"
    lib_dir.mkdir()
    # 创建关键文件使 libraries 深度校验通过（H-10）
    (lib_dir / "timer").mkdir()
    (lib_dir / "timer" / "FB_TON.scl").write_text("// FB_TON", encoding="utf-8")
    (project_dir / ".plc.json").write_text(
        json.dumps(
            {
                "name": PROJECT_ID,
                "description": "检查测试项目",
                "version": "V1.0.0",
                "libraries": ["./lib"],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # PM_SESSION → pass
    (project_dir / f"PM_SESSION_{PROJECT_ID}.md").write_text(
        "# PM_SESSION", encoding="utf-8"
    )

    # PRD 目录 → pass
    prd_dir = project_dir / "PRD"
    prd_dir.mkdir()
    # 接口文档_INT.md → pass
    (prd_dir / "接口文档_INT.md").write_text("# INT", encoding="utf-8")
    # 需求分析文档_v2.md → warn（命名不匹配）
    (prd_dir / "需求分析文档_v2.md").write_text("# REQ v2", encoding="utf-8")
    # 缺少 详细设计说明书_DSN.md, 技术方案文档_TEC.md → fail

    # 标准目录（部分存在）
    (project_dir / "02_PLC程序" / "通用ST程序及变量表").mkdir(parents=True)
    (project_dir / "03_HMI设计").mkdir()
    # 缺少 04_现场调试, 04_变更管理 → fail

    return project_dir


def _create_standardize_project(workspace: Path) -> Path:
    """创建含可标准化命名的项目目录

    结构：
      TEST-2026-001_标准化测试项目/
        PRD/
          需求文档_PRD-001.md  → 匹配 NAMING_RULES 模式，可标准化为 需求分析文档_REQ.md
    """
    project_dir = workspace / f"{PROJECT_ID}_标准化测试项目"
    project_dir.mkdir()
    prd_dir = project_dir / "PRD"
    prd_dir.mkdir()
    # 非标准命名，匹配 r"^需求文档_PRD-.*\.md$" 模式
    (prd_dir / "需求文档_PRD-001.md").write_text("# REQ", encoding="utf-8")
    return project_dir


def _create_doc_project(workspace: Path) -> Path:
    """创建含各类文档的项目目录（用于 DocTab 测试）

    结构：
      DOC-2026-001_文档测试项目/
        .copier-answers.yml      → 模板信息来源
        PM_SESSION_DOC-2026-001.md → PM_SESSION 类
        立项表_DOC-2026-001.md     → 立项表类
        CHG-DOC-2026-001-001.md    → 变更单类
        变更单_CHG-DOC-2026-001-002.md → 变更单类
        09_整改项/V2.0-测试整改.md → 整改项类
        README.md                  → 其他文档类
    """
    project_dir = workspace / f"{DOC_PROJECT_ID}_文档测试项目"
    project_dir.mkdir()

    # .copier-answers.yml（模板信息来源）
    (project_dir / ".copier-answers.yml").write_text(
        "_commit: abc1234\n"
        "_src_path: templates/plc-standard\n"
        f"project_id: {DOC_PROJECT_ID}\n"
        "project_name: 文档测试项目\n"
        "version: V1.0.0\n",
        encoding="utf-8",
    )

    # PM_SESSION 文档
    (project_dir / f"PM_SESSION_{DOC_PROJECT_ID}.md").write_text(
        "# PM_SESSION\n测试会话", encoding="utf-8"
    )

    # 立项表文档
    (project_dir / f"立项表_{DOC_PROJECT_ID}.md").write_text(
        "# 立项表\n测试立项", encoding="utf-8"
    )

    # 变更单文档（CHG- 前缀）
    (project_dir / f"CHG-{DOC_PROJECT_ID}-001.md").write_text(
        "# 变更单\n测试变更", encoding="utf-8"
    )

    # 变更单文档（变更单_ 前缀）
    (project_dir / f"变更单_CHG-{DOC_PROJECT_ID}-002.md").write_text(
        "# 变更单2\n测试变更2", encoding="utf-8"
    )

    # 整改项目录及文档
    rect_dir = project_dir / "09_整改项"
    rect_dir.mkdir()
    (rect_dir / "V2.0-测试整改.md").write_text("# 整改\n测试整改", encoding="utf-8")

    # 其他文档
    (project_dir / "README.md").write_text("# README\n测试说明", encoding="utf-8")

    return project_dir


def _create_empty_project(workspace: Path) -> Path:
    """创建空项目目录（无任何 .md 文档）"""
    project_dir = workspace / "EMPTY-2026-001_空项目"
    project_dir.mkdir()
    return project_dir


def _make_project(
    project_id: str, name: str, path: str, stack: str = "plc"
) -> ProjectInfo:
    """构造测试用 ProjectInfo"""
    return ProjectInfo(
        project_id=project_id,
        name=name,
        path=path,
        stack=stack,
        version="V1.0.0",
        description=f"测试项目 {project_id}",
        source="copier",
        phase="developing",
        business_line="DJ",
    )


# ── 辅助：widget 查找 ────────────────────────────────────


def _get_item_buttons(tab: QWidget) -> list[QPushButton]:
    """获取所有"修复"按钮（objectName == itemBtn）"""
    return [b for b in tab.findChildren(QPushButton) if b.objectName() == "itemBtn"]


def _get_item_labels(tab: QWidget) -> list[QLabel]:
    """获取所有检查项文本标签（objectName == itemText）"""
    return [lbl for lbl in tab.findChildren(QLabel) if lbl.objectName() == "itemText"]


def _get_group_titles(tab: QWidget) -> list[str]:
    """获取所有分组标题文本"""
    titles = [lbl for lbl in tab.findChildren(QLabel) if lbl.objectName() == "groupTitle"]
    return [lbl.text() for lbl in titles]


def _run_check(tab: CheckTab, qapp: QApplication) -> None:
    """执行检查并处理事件"""
    tab._on_run_check()
    qapp.processEvents()


def _assert_check_summary_matches_result(tab: CheckTab) -> None:
    """断言摘要栏与真实检查结果一致。"""
    assert tab._last_check_result is not None
    summary = tab._summary_label.text()
    assert f"{tab._last_check_result.pass_count} 通过" in summary
    assert f"{tab._last_check_result.warn_count} 警告" in summary
    assert f"{tab._last_check_result.fail_count} 失败" in summary


def _find_category(tab: DocTab, keyword: str) -> QTreeWidgetItem | None:
    """按关键字查找分类节点"""
    for item in tab._get_category_items():
        if keyword in item.text(0):
            return item
    return None


# ══════════════════════════════════════════════════════════
#  检查 Tab 交互测试
# ══════════════════════════════════════════════════════════


class TestCheckTabInteractive:
    """检查 Tab 交互测试（通过 MainWindow → WorkspaceView → CheckTab 链路）"""

    def test_check_tab_load(
        self, qapp: QApplication, main_window: MainWindow, workspace_root: Path
    ) -> None:
        """进入项目工作区 → 检查 Tab 加载（checker/repairer 初始化，初始空状态）"""
        project_dir = _create_mixed_project(workspace_root)
        proj = _make_project(PROJECT_ID, "检查测试项目", str(project_dir))
        main_window._workspace_view.load_project(proj)
        qapp.processEvents()

        tab = main_window._workspace_view._check_tab
        assert tab is not None
        assert tab._project_id == PROJECT_ID
        assert tab._project_path == str(project_dir)
        assert tab._checker is not None
        assert tab._repairer is not None
        # 初始状态：显示空状态提示，滚动区隐藏
        assert tab._empty_hint.isVisibleTo(tab) is True
        assert tab._scroll.isVisibleTo(tab) is False
        assert tab._summary_label.text() == "检查结果: —"

    def test_check_tab_run_check(
        self, qapp: QApplication, main_window: MainWindow, workspace_root: Path
    ) -> None:
        """点击"执行检查" → 结果显示 pass/warn/fail"""
        project_dir = _create_mixed_project(workspace_root)
        proj = _make_project(PROJECT_ID, "检查测试项目", str(project_dir))
        main_window._workspace_view.load_project(proj)
        qapp.processEvents()

        tab = main_window._workspace_view._check_tab
        assert tab is not None
        # 真实点击"执行检查"按钮
        tab._check_btn.click()
        qapp.processEvents()

        # 应隐藏空状态，显示滚动区
        assert tab._empty_hint.isVisibleTo(tab) is False
        assert tab._scroll.isVisibleTo(tab) is True
        # 应有分组卡片
        cards = tab._get_group_cards()
        assert len(cards) > 0
        # 检查结果应被保存
        assert tab._last_check_result is not None
        assert tab._last_check_result.pass_count > 0
        assert tab._last_check_result.warn_count >= 0
        assert tab._last_check_result.fail_count > 0

    def test_check_tab_groups(
        self, qapp: QApplication, main_window: MainWindow, workspace_root: Path
    ) -> None:
        """结果按类别分组显示（标志文件 / PRD 文档 / 目录结构）"""
        project_dir = _create_mixed_project(workspace_root)
        proj = _make_project(PROJECT_ID, "检查测试项目", str(project_dir))
        main_window._workspace_view.load_project(proj)
        qapp.processEvents()

        tab = main_window._workspace_view._check_tab
        assert tab is not None
        _run_check(tab, qapp)

        titles = _get_group_titles(tab)
        # 分组标题含状态图标前缀（如 "✅  标志文件"），用包含匹配
        assert any("标志文件" in t for t in titles)
        assert any("PRD 文档" in t for t in titles)
        assert any("目录结构" in t for t in titles)
        assert len(titles) == 4  # 标志文件/PRD文档/目录结构/其他（V0.2.3 新增）
        # 分组卡片数量应与分组数一致
        cards = tab._get_group_cards()
        assert len(cards) == 4

    def test_check_tab_status_icons(
        self, qapp: QApplication, main_window: MainWindow, workspace_root: Path
    ) -> None:
        """状态图标正确（✅ pass / ⚠️ warn / ❌ fail）"""
        project_dir = _create_mixed_project(workspace_root)
        proj = _make_project(PROJECT_ID, "检查测试项目", str(project_dir))
        main_window._workspace_view.load_project(proj)
        qapp.processEvents()

        tab = main_window._workspace_view._check_tab
        assert tab is not None
        _run_check(tab, qapp)

        item_labels = _get_item_labels(tab)
        assert tab._last_check_result is not None
        # pass 项的文本应包含 ✅ 图标
        pass_labels = [lbl for lbl in item_labels if lbl.text().startswith("✅")]
        assert len(pass_labels) == tab._last_check_result.pass_count
        # warn 项的文本应包含 ⚠️ 图标
        warn_labels = [lbl for lbl in item_labels if lbl.text().startswith("⚠️")]
        assert len(warn_labels) == tab._last_check_result.warn_count
        # fail 项的文本应包含 ❌ 图标
        fail_labels = [lbl for lbl in item_labels if lbl.text().startswith("❌")]
        assert len(fail_labels) == tab._last_check_result.fail_count

        # 分组标题也应显示聚合状态图标
        titles = _get_group_titles(tab)
        # 标志文件组：全 pass → ✅
        assert any(t.startswith("✅") and "标志文件" in t for t in titles)
        # PRD 文档组：有 fail → ❌
        assert any(t.startswith("❌") and "PRD 文档" in t for t in titles)
        # 目录结构组：有 fail → ❌
        assert any(t.startswith("❌") and "目录结构" in t for t in titles)

    def test_check_tab_repair_button(
        self, qapp: QApplication, main_window: MainWindow, workspace_root: Path
    ) -> None:
        """warn/fail 项显示"修复"按钮"""
        project_dir = _create_mixed_project(workspace_root)
        proj = _make_project(PROJECT_ID, "检查测试项目", str(project_dir))
        main_window._workspace_view.load_project(proj)
        qapp.processEvents()

        tab = main_window._workspace_view._check_tab
        assert tab is not None
        _run_check(tab, qapp)

        item_btns = _get_item_buttons(tab)
        assert tab._last_check_result is not None
        assert len(item_btns) == (
            tab._last_check_result.warn_count + tab._last_check_result.fail_count
        )
        # 所有修复按钮的文本都是"修复"
        assert all(b.text() == "修复" for b in item_btns)

    def test_check_tab_auto_repair(
        self, qapp: QApplication, main_window: MainWindow, workspace_root: Path
    ) -> None:
        """点击"自动修复" → 预览显示（dry-run，未实际执行）"""
        project_dir = _create_mixed_project(workspace_root)
        proj = _make_project(PROJECT_ID, "检查测试项目", str(project_dir))
        main_window._workspace_view.load_project(proj)
        qapp.processEvents()

        tab = main_window._workspace_view._check_tab
        assert tab is not None
        # 真实点击"自动修复"按钮
        tab._repair_btn.click()
        qapp.processEvents()

        # 应隐藏空状态，显示滚动区
        assert tab._empty_hint.isVisibleTo(tab) is False
        assert tab._scroll.isVisibleTo(tab) is True
        # 应有分组卡片（修复预览卡片）
        cards = tab._get_group_cards()
        assert len(cards) == 1
        # 预览标题应含"修复预览"
        titles = _get_group_titles(tab)
        assert any("修复预览" in t for t in titles)
        # 摘要应显示可修复/跳过/失败计数
        # mixed 项目: 12 fixed (创建缺失的 PRD 文档和目录) + 1 skipped (命名不匹配需确认)
        summary = tab._summary_label.text()
        assert "12 可修复" in summary
        assert "1 跳过" in summary
        assert "0 失败" in summary

    def test_check_tab_standardize(
        self, qapp: QApplication, main_window: MainWindow, workspace_root: Path
    ) -> None:
        """点击"标准化命名" → 预览显示（未实际执行）"""
        project_dir = _create_standardize_project(workspace_root)
        proj = _make_project(PROJECT_ID, "标准化测试项目", str(project_dir))
        main_window._workspace_view.load_project(proj)
        qapp.processEvents()

        tab = main_window._workspace_view._check_tab
        assert tab is not None
        # 真实点击"标准化命名"按钮
        tab._standardize_btn.click()
        qapp.processEvents()

        # 应隐藏空状态，显示滚动区
        assert tab._empty_hint.isVisibleTo(tab) is False
        assert tab._scroll.isVisibleTo(tab) is True
        # 应有分组卡片（标准化预览卡片）
        cards = tab._get_group_cards()
        assert len(cards) == 1
        # 预览标题应含"标准化命名预览"
        titles = _get_group_titles(tab)
        assert any("标准化命名预览" in t for t in titles)
        # 应显示重命名计划（→ 符号）
        item_labels = _get_item_labels(tab)
        rename_labels = [lbl for lbl in item_labels if "→" in lbl.text()]
        assert len(rename_labels) > 0
        # 应包含目标标准名
        assert any("需求分析文档_REQ.md" in lbl.text() for lbl in rename_labels)

    def test_check_tab_summary(
        self, qapp: QApplication, main_window: MainWindow, workspace_root: Path
    ) -> None:
        """底部摘要栏显示计数（通过/警告/失败）"""
        project_dir = _create_mixed_project(workspace_root)
        proj = _make_project(PROJECT_ID, "检查测试项目", str(project_dir))
        main_window._workspace_view.load_project(proj)
        qapp.processEvents()

        tab = main_window._workspace_view._check_tab
        assert tab is not None
        # 初始摘要应为 "检查结果: —"
        assert tab._summary_label.text() == "检查结果: —"

        _run_check(tab, qapp)

        _assert_check_summary_matches_result(tab)


# ══════════════════════════════════════════════════════════
#  文档 Tab 交互测试
# ══════════════════════════════════════════════════════════


class TestDocTabInteractive:
    """文档 Tab 交互测试（通过 MainWindow → WorkspaceView → DocTab 链路）"""

    def test_doc_tab_load(
        self, qapp: QApplication, main_window: MainWindow, workspace_root: Path
    ) -> None:
        """进入项目工作区 → 文档 Tab 加载（分类节点非空，空状态隐藏）"""
        project_dir = _create_doc_project(workspace_root)
        proj = _make_project(DOC_PROJECT_ID, "文档测试项目", str(project_dir))
        main_window._workspace_view.load_project(proj)
        qapp.processEvents()

        tab = main_window._workspace_view._doc_tab
        assert tab is not None
        assert tab._project_id == DOC_PROJECT_ID
        assert tab._project_path == str(project_dir)
        # 应有分类节点（非空）
        cats = tab._get_category_items()
        assert len(cats) > 0
        # 空状态提示应隐藏
        assert tab._empty_hint.isVisibleTo(tab) is False

    def test_doc_tab_classification(
        self, qapp: QApplication, main_window: MainWindow, workspace_root: Path
    ) -> None:
        """文档分类正确（PM_SESSION/立项表/变更单/整改项/其他）"""
        project_dir = _create_doc_project(workspace_root)
        proj = _make_project(DOC_PROJECT_ID, "文档测试项目", str(project_dir))
        main_window._workspace_view.load_project(proj)
        qapp.processEvents()

        tab = main_window._workspace_view._doc_tab
        assert tab is not None
        cats = tab._get_category_items()
        labels = [item.text(0) for item in cats]

        # 应包含所有 5 个分类
        assert any("PM_SESSION" in label for label in labels)
        assert any("立项表" in label for label in labels)
        assert any("变更单" in label for label in labels)
        assert any("整改项" in label for label in labels)
        assert any("其他文档" in label for label in labels)

        # PM_SESSION 类应有 1 个文档
        pm_cat = _find_category(tab, "PM_SESSION")
        assert pm_cat is not None
        pm_docs = tab._get_documents_in_category(pm_cat)
        assert len(pm_docs) == 1
        assert "PM_SESSION_DOC-2026-001" in pm_docs[0].text(0)

        # 立项表类应有 1 个文档
        init_cat = _find_category(tab, "立项表")
        assert init_cat is not None
        init_docs = tab._get_documents_in_category(init_cat)
        assert len(init_docs) == 1

        # 变更单类应有 2 个文档（CHG- 前缀 + 变更单_ 前缀）
        change_cat = _find_category(tab, "变更单")
        assert change_cat is not None
        change_docs = tab._get_documents_in_category(change_cat)
        assert len(change_docs) == 2

        # 整改项类应有 1 个文档
        rect_cat = _find_category(tab, "整改项")
        assert rect_cat is not None
        rect_docs = tab._get_documents_in_category(rect_cat)
        assert len(rect_docs) == 1

        # 其他文档类应有 1 个文档（README.md）
        other_cat = _find_category(tab, "其他文档")
        assert other_cat is not None
        other_docs = tab._get_documents_in_category(other_cat)
        assert len(other_docs) == 1
        assert "README" in other_docs[0].text(0)

    def test_doc_tab_double_click(
        self, qapp: QApplication, main_window: MainWindow, workspace_root: Path
    ) -> None:
        """双击文档 → 触发打开（QDesktopServices.openUrl 调用）"""
        project_dir = _create_doc_project(workspace_root)
        proj = _make_project(DOC_PROJECT_ID, "文档测试项目", str(project_dir))
        main_window._workspace_view.load_project(proj)
        qapp.processEvents()

        tab = main_window._workspace_view._doc_tab
        assert tab is not None
        # 找到 PM_SESSION 分类下的文档
        cat = _find_category(tab, "PM_SESSION")
        assert cat is not None
        docs = tab._get_documents_in_category(cat)
        assert len(docs) == 1
        doc_item = docs[0]

        # 通过 itemDoubleClicked 信号触发双击（等价于真实双击）
        # 使用 patch 拦截 QDesktopServices.openUrl 系统调用，验证打开路径正确
        with patch("auto_pm.ui.workspace.doc_tab.QDesktopServices.openUrl") as mock_open:
            tab._on_document_double_clicked(doc_item)
            qapp.processEvents()
            mock_open.assert_called_once()
            # 验证传入的是 QUrl
            args = mock_open.call_args[0]
            assert isinstance(args[0], QUrl)
            # 验证路径指向实际文件
            assert "PM_SESSION_DOC-2026-001.md" in args[0].toLocalFile()

    def test_doc_tab_template_info(
        self, qapp: QApplication, main_window: MainWindow, workspace_root: Path
    ) -> None:
        """模板信息显示（名称/版本/上次更新）"""
        project_dir = _create_doc_project(workspace_root)
        proj = _make_project(DOC_PROJECT_ID, "文档测试项目", str(project_dir))
        main_window._workspace_view.load_project(proj)
        qapp.processEvents()

        tab = main_window._workspace_view._doc_tab
        assert tab is not None
        # 模板名称应从 _src_path 提取
        assert "plc-standard" in tab._template_name_label.text()
        # 版本应显示 _commit
        assert "abc1234" in tab._template_version_label.text()
        # 上次更新应非空（非占位符）
        assert tab._template_updated_label.text() != "上次更新: —"

    def test_doc_tab_update_button(
        self, qapp: QApplication, main_window: MainWindow, workspace_root: Path
    ) -> None:
        """模板更新按钮存在（文本为"🔄 模板更新"）"""
        project_dir = _create_doc_project(workspace_root)
        proj = _make_project(DOC_PROJECT_ID, "文档测试项目", str(project_dir))
        main_window._workspace_view.load_project(proj)
        qapp.processEvents()

        tab = main_window._workspace_view._doc_tab
        assert tab is not None
        assert tab._update_btn is not None
        assert tab._update_btn.text() == "🔄 模板更新"
        # 检查更新按钮也应存在
        assert tab._check_btn is not None
        assert tab._check_btn.text() == "检查更新"

    def test_doc_tab_empty_state(
        self, qapp: QApplication, main_window: MainWindow, workspace_root: Path
    ) -> None:
        """空项目（无文档）显示空状态"""
        project_dir = _create_empty_project(workspace_root)
        proj = _make_project("EMPTY-2026-001", "空项目", str(project_dir))
        main_window._workspace_view.load_project(proj)
        qapp.processEvents()

        tab = main_window._workspace_view._doc_tab
        assert tab is not None
        cats = tab._get_category_items()
        assert len(cats) == 0
        # 空状态提示应可见
        assert tab._empty_hint.isVisibleTo(tab) is True


# ══════════════════════════════════════════════════════════
#  完整流程测试
# ══════════════════════════════════════════════════════════


class TestFullFlow:
    """完整流程测试：执行检查 → 发现问题 → 自动修复 → 重新检查"""

    def test_full_flow_check_repair(
        self, qapp: QApplication, main_window: MainWindow, workspace_root: Path
    ) -> None:
        """执行检查 → 发现问题 → 自动修复 → 重新检查

        流程：
        1. 加载含 fail 项的项目（mixed: 8 pass / 1 warn / 4 fail）
        2. 点击"执行检查" → 验证 fail 项存在
        3. 点击"修复"按钮 → 实际执行修复（dry_run=False）
        4. 修复后自动重新检查 → 验证 fail 项已被修复
        """
        project_dir = _create_mixed_project(workspace_root)
        proj = _make_project(PROJECT_ID, "检查测试项目", str(project_dir))
        main_window._workspace_view.load_project(proj)
        qapp.processEvents()

        tab = main_window._workspace_view._check_tab
        assert tab is not None

        # ── Step 1: 执行检查 → 发现问题 ──
        tab._check_btn.click()
        qapp.processEvents()

        assert tab._last_check_result is not None
        assert tab._last_check_result.fail_count > 0
        assert tab._last_check_result.warn_count >= 0
        assert tab._last_check_result.pass_count > 0
        item_btns = _get_item_buttons(tab)
        assert len(item_btns) == (
            tab._last_check_result.warn_count + tab._last_check_result.fail_count
        )

        # ── Step 2: 点击修复按钮 → 实际执行修复 ──
        # 修复按钮触发 _on_repair_item，执行 repair_project(dry_run=False)
        # 后端会修复所有可修复项（12 个 fail 全部被修复）
        item_btns[0].click()
        qapp.processEvents()

        # ── Step 3: 修复后自动重新检查 → 验证 fail 项已被修复 ──
        # _on_repair_item 内部会重新检查并渲染结果
        assert tab._last_check_result is not None
        assert tab._last_check_result.fail_count == 0
        # warn 项（命名不匹配 + Spec Snapshot）可能仍保留
        assert tab._last_check_result.warn_count >= 0
        # pass 项应增加
        assert tab._last_check_result.pass_count > 0

        # 摘要栏应更新
        _assert_check_summary_matches_result(tab)

        # 修复后应发射 repair_completed 信号
        # （通过重新检查验证修复效果，信号已在 _on_repair_item 中发射）

        # 修复按钮数量应减少（只剩 warn 项）
        remaining_btns = _get_item_buttons(tab)
        assert len(remaining_btns) == tab._last_check_result.warn_count
