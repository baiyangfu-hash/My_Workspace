"""CheckTab 单元测试

测试内容：
- load_project 后初始状态
- 点击"执行检查" → 结果展示
- 结果分组显示正确
- 状态图标（pass/warn/fail）
- "修复"按钮仅对 warn/fail 显示
- 点击"自动修复" → 预览显示
- 点击"标准化命名" → 预览显示
- 摘要栏计数
- check_completed / repair_completed 信号

使用真实 PlcChecker/PlcRepairer + 临时项目目录（不 mock），遵循项目现有 qapp fixture 模式。
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

# 必须在导入 PySide6 前设置离屏渲染，避免无显示环境报错
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QLabel, QPushButton  # noqa: E402

from auto_pm.ui.workspace.check_tab import CheckTab  # noqa: E402

# ── fixtures ─────────────────────────────────────────────


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """提供全局 QApplication 实例（session 级复用）"""
    app = QApplication.instance() or QApplication([])
    yield app


PROJECT_ID = "TEST-2026-001"


@pytest.fixture
def mixed_project_dir(tmp_path: Path) -> Path:
    """临时项目目录，含 pass/warn/fail 混合检查项

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
    """
    project_dir = tmp_path / f"{PROJECT_ID}_检查测试项目"
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
    (project_dir / f"PM_SESSION_{PROJECT_ID}.md").write_text("# PM_SESSION", encoding="utf-8")

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


@pytest.fixture
def standardize_project_dir(tmp_path: Path) -> Path:
    """临时项目目录，含可被标准化的非标准 PRD 文件名

    结构：
      TEST-2026-001_标准化测试项目/
        PRD/
          需求文档_PRD-001.md  → 匹配 NAMING_RULES 模式，可标准化为 需求分析文档_REQ.md
    """
    project_dir = tmp_path / f"{PROJECT_ID}_标准化测试项目"
    project_dir.mkdir()
    prd_dir = project_dir / "PRD"
    prd_dir.mkdir()
    # 非标准命名，匹配 r"^需求文档_PRD-.*\.md$" 模式
    (prd_dir / "需求文档_PRD-001.md").write_text("# REQ", encoding="utf-8")
    return project_dir


@pytest.fixture
def empty_project_dir(tmp_path: Path) -> Path:
    """空项目目录（全部检查项 fail）"""
    project_dir = tmp_path / f"{PROJECT_ID}_空项目"
    project_dir.mkdir()
    return project_dir


@pytest.fixture
def check_tab(qapp: QApplication, mixed_project_dir: Path) -> CheckTab:
    """已加载 mixed 项目的 CheckTab"""
    tab = CheckTab()
    tab.load_project(PROJECT_ID, str(mixed_project_dir))
    qapp.processEvents()
    yield tab
    tab.deleteLater()
    qapp.processEvents()


# ── 辅助函数 ─────────────────────────────────────────────


def _get_item_buttons(tab: CheckTab) -> list[QPushButton]:
    """获取所有"修复"按钮（objectName == itemBtn）"""
    return [b for b in tab.findChildren(QPushButton) if b.objectName() == "itemBtn"]


def _get_item_labels(tab: CheckTab) -> list[QLabel]:
    """获取所有检查项文本标签（objectName == itemText）"""
    return [lbl for lbl in tab.findChildren(QLabel) if lbl.objectName() == "itemText"]


def _get_group_titles(tab: CheckTab) -> list[str]:
    """获取所有分组标题文本"""
    titles = [lbl for lbl in tab.findChildren(QLabel) if lbl.objectName() == "groupTitle"]
    return [lbl.text() for lbl in titles]


def _run_check(tab: CheckTab, qapp: QApplication) -> None:
    """执行检查并处理事件"""
    tab._on_run_check()
    qapp.processEvents()


# ── 初始状态测试 ─────────────────────────────────────────


class TestCheckTabInitial:
    """CheckTab 初始状态测试"""

    def test_initial_state_shows_hint(self, qapp: QApplication, mixed_project_dir: Path) -> None:
        """load_project 后应显示空状态提示，滚动区隐藏"""
        tab = CheckTab()
        tab.load_project(PROJECT_ID, str(mixed_project_dir))
        qapp.processEvents()

        assert tab._empty_hint.isVisibleTo(tab) is True
        assert tab._scroll.isVisibleTo(tab) is False
        assert tab._summary_label.text() == "检查结果: —"
        tab.deleteLater()
        qapp.processEvents()

    def test_buttons_exist(self, qapp: QApplication) -> None:
        """CheckTab 应包含三个操作按钮"""
        tab = CheckTab()
        qapp.processEvents()

        assert tab._check_btn.text() == "▶ 执行检查"
        assert tab._repair_btn.text() == "🔧 自动修复"
        assert tab._standardize_btn.text() == "📝 标准化命名"
        tab.deleteLater()
        qapp.processEvents()

    def test_load_project_initializes_checker(
        self, qapp: QApplication, mixed_project_dir: Path
    ) -> None:
        """load_project 应初始化 checker 和 repairer"""
        tab = CheckTab()
        tab.load_project(PROJECT_ID, str(mixed_project_dir))
        qapp.processEvents()

        assert tab._checker is not None
        assert tab._repairer is not None
        assert tab._project_id == PROJECT_ID
        assert tab._project_path == str(mixed_project_dir)
        tab.deleteLater()
        qapp.processEvents()

    def test_run_check_without_load_is_safe(self, qapp: QApplication) -> None:
        """未 load_project 时点击执行检查应安全返回（不抛异常）"""
        tab = CheckTab()
        qapp.processEvents()

        # 不应抛异常
        tab._on_run_check()
        qapp.processEvents()
        tab.deleteLater()
        qapp.processEvents()


# ── 执行检查测试 ─────────────────────────────────────────


class TestCheckTabRunCheck:
    """CheckTab 执行检查测试"""

    def test_run_check_displays_results(self, check_tab: CheckTab, qapp: QApplication) -> None:
        """点击执行检查后应展示结果，隐藏空状态"""
        _run_check(check_tab, qapp)

        assert check_tab._empty_hint.isVisibleTo(check_tab) is False
        assert check_tab._scroll.isVisibleTo(check_tab) is True
        # 应有分组卡片
        cards = check_tab._get_group_cards()
        assert len(cards) > 0

    def test_run_check_summary_counts(self, check_tab: CheckTab, qapp: QApplication) -> None:
        """摘要栏应显示正确的通过/警告/失败计数"""
        _run_check(check_tab, qapp)

        # mixed 项目: 8 pass / 1 warn / 4 fail
        summary = check_tab._summary_label.text()
        assert "8 通过" in summary
        assert "1 警告" in summary
        assert "4 失败" in summary

    def test_run_check_groups_correct(self, check_tab: CheckTab, qapp: QApplication) -> None:
        """结果应按类别分组：标志文件 / PRD 文档 / 目录结构"""
        _run_check(check_tab, qapp)

        titles = _get_group_titles(check_tab)
        # 分组标题含状态图标前缀（如 "✅  标志文件"），用包含匹配
        assert any("标志文件" in t for t in titles)
        assert any("PRD 文档" in t for t in titles)
        assert any("目录结构" in t for t in titles)
        assert len(titles) == 3

    def test_run_check_group_card_count(self, check_tab: CheckTab, qapp: QApplication) -> None:
        """分组卡片数量应与分组数一致"""
        _run_check(check_tab, qapp)

        cards = check_tab._get_group_cards()
        assert len(cards) == 3

    def test_run_check_emits_signal(self, check_tab: CheckTab, qapp: QApplication) -> None:
        """执行检查后应发射 check_completed 信号"""
        received: list[bool] = []
        check_tab.check_completed.connect(lambda: received.append(True))

        _run_check(check_tab, qapp)
        assert received == [True]

    def test_last_check_result_stored(self, check_tab: CheckTab, qapp: QApplication) -> None:
        """执行检查后 _last_check_result 应被保存"""
        assert check_tab._last_check_result is None
        _run_check(check_tab, qapp)
        assert check_tab._last_check_result is not None
        assert check_tab._last_check_result.pass_count == 8
        assert check_tab._last_check_result.warn_count == 1
        assert check_tab._last_check_result.fail_count == 4


# ── 状态图标测试 ─────────────────────────────────────────


class TestCheckTabStatusIcon:
    """CheckTab 状态图标测试"""

    def test_pass_items_have_pass_icon(self, check_tab: CheckTab, qapp: QApplication) -> None:
        """pass 项的文本应包含 ✅ 图标"""
        _run_check(check_tab, qapp)

        item_labels = _get_item_labels(check_tab)
        pass_labels = [lbl for lbl in item_labels if lbl.text().startswith("✅")]
        assert len(pass_labels) == 8  # 8 个 pass 项

    def test_warn_items_have_warn_icon(self, check_tab: CheckTab, qapp: QApplication) -> None:
        """warn 项的文本应包含 ⚠️ 图标"""
        _run_check(check_tab, qapp)

        item_labels = _get_item_labels(check_tab)
        warn_labels = [lbl for lbl in item_labels if lbl.text().startswith("⚠️")]
        assert len(warn_labels) == 1  # 1 个 warn 项

    def test_fail_items_have_fail_icon(self, check_tab: CheckTab, qapp: QApplication) -> None:
        """fail 项的文本应包含 ❌ 图标"""
        _run_check(check_tab, qapp)

        item_labels = _get_item_labels(check_tab)
        fail_labels = [lbl for lbl in item_labels if lbl.text().startswith("❌")]
        assert len(fail_labels) == 4  # 4 个 fail 项

    def test_group_title_icons(self, check_tab: CheckTab, qapp: QApplication) -> None:
        """分组标题应显示聚合状态图标"""
        _run_check(check_tab, qapp)

        titles = _get_group_titles(check_tab)
        # 标志文件组：全 pass → ✅
        assert any(t.startswith("✅") and "标志文件" in t for t in titles)
        # PRD 文档组：有 fail → ❌
        assert any(t.startswith("❌") and "PRD 文档" in t for t in titles)
        # 目录结构组：有 fail → ❌
        assert any(t.startswith("❌") and "目录结构" in t for t in titles)


# ── 修复按钮测试 ─────────────────────────────────────────


class TestCheckTabRepairButton:
    """CheckTab 修复按钮测试"""

    def test_repair_buttons_only_for_warn_fail(
        self, check_tab: CheckTab, qapp: QApplication
    ) -> None:
        """修复按钮仅对 warn/fail 项显示（共 5 个：1 warn + 4 fail）"""
        _run_check(check_tab, qapp)

        item_btns = _get_item_buttons(check_tab)
        assert len(item_btns) == 5

    def test_pass_items_have_no_repair_button(
        self, check_tab: CheckTab, qapp: QApplication
    ) -> None:
        """pass 项不应有修复按钮"""
        _run_check(check_tab, qapp)

        item_btns = _get_item_buttons(check_tab)
        # 所有修复按钮的文本都是"修复"
        assert all(b.text() == "修复" for b in item_btns)
        # 修复按钮数量 = warn + fail = 1 + 4 = 5
        assert len(item_btns) == 5

    def test_repair_button_click_fixes_issues(
        self, check_tab: CheckTab, qapp: QApplication
    ) -> None:
        """点击修复按钮应实际执行修复，fail 项变为 pass"""
        _run_check(check_tab, qapp)
        assert check_tab._last_check_result is not None
        assert check_tab._last_check_result.fail_count == 4

        # 点击第一个修复按钮
        item_btns = _get_item_buttons(check_tab)
        assert len(item_btns) > 0
        item_btns[0].click()
        qapp.processEvents()

        # 修复后重新检查，fail 应减少（4 个 fail 全部被修复）
        assert check_tab._last_check_result is not None
        assert check_tab._last_check_result.fail_count == 0
        # warn 项（命名不匹配）未被修复（rename_confirm=False）
        assert check_tab._last_check_result.warn_count == 1

    def test_repair_button_emits_signal(self, check_tab: CheckTab, qapp: QApplication) -> None:
        """点击修复按钮后应发射 repair_completed 信号"""
        _run_check(check_tab, qapp)

        received: list[bool] = []
        check_tab.repair_completed.connect(lambda: received.append(True))

        item_btns = _get_item_buttons(check_tab)
        item_btns[0].click()
        qapp.processEvents()

        assert received == [True]


# ── 自动修复预览测试 ─────────────────────────────────────


class TestCheckTabAutoRepair:
    """CheckTab 自动修复预览测试"""

    def test_auto_repair_displays_preview(self, check_tab: CheckTab, qapp: QApplication) -> None:
        """点击自动修复应显示修复预览"""
        check_tab._on_auto_repair()
        qapp.processEvents()

        assert check_tab._empty_hint.isVisibleTo(check_tab) is False
        assert check_tab._scroll.isVisibleTo(check_tab) is True
        # 应有分组卡片（修复预览卡片）
        cards = check_tab._get_group_cards()
        assert len(cards) == 1

    def test_auto_repair_summary(self, check_tab: CheckTab, qapp: QApplication) -> None:
        """自动修复预览摘要应显示可修复/跳过/失败计数"""
        check_tab._on_auto_repair()
        qapp.processEvents()

        # mixed 项目: 4 fixed (创建缺失的 PRD 文档和目录) + 1 skipped (命名不匹配需确认)
        summary = check_tab._summary_label.text()
        assert "4 可修复" in summary
        assert "1 跳过" in summary
        assert "0 失败" in summary

    def test_auto_repair_preview_title(self, check_tab: CheckTab, qapp: QApplication) -> None:
        """修复预览应显示 dry-run 标题"""
        check_tab._on_auto_repair()
        qapp.processEvents()

        titles = _get_group_titles(check_tab)
        assert any("修复预览" in t for t in titles)

    def test_auto_repair_shows_actions(self, check_tab: CheckTab, qapp: QApplication) -> None:
        """修复预览应列出修复动作"""
        check_tab._on_auto_repair()
        qapp.processEvents()

        item_labels = _get_item_labels(check_tab)
        # 应有修复动作文本（非"无需修复"提示）
        assert len(item_labels) > 0
        # 不应显示"无需修复"（因为有 fail 项需要修复）
        assert not any("无需修复" in lbl.text() for lbl in item_labels)

    def test_auto_repair_dry_run_no_filesystem_change(
        self, check_tab: CheckTab, qapp: QApplication, mixed_project_dir: Path
    ) -> None:
        """dry_run 模式不应实际创建文件"""
        # 记录修复前的文件列表
        prd_files_before = set(os.listdir(mixed_project_dir / "PRD"))

        check_tab._on_auto_repair()
        qapp.processEvents()

        # dry_run 不应改变文件系统
        prd_files_after = set(os.listdir(mixed_project_dir / "PRD"))
        assert prd_files_before == prd_files_after


# ── 标准化命名预览测试 ───────────────────────────────────


class TestCheckTabStandardize:
    """CheckTab 标准化命名预览测试"""

    def test_standardize_displays_preview(
        self,
        qapp: QApplication,
        standardize_project_dir: Path,
    ) -> None:
        """点击标准化命名应显示标准化预览"""
        tab = CheckTab()
        tab.load_project(PROJECT_ID, str(standardize_project_dir))
        qapp.processEvents()

        tab._on_standardize()
        qapp.processEvents()

        assert tab._empty_hint.isVisibleTo(tab) is False
        assert tab._scroll.isVisibleTo(tab) is True
        cards = tab._get_group_cards()
        assert len(cards) == 1
        tab.deleteLater()
        qapp.processEvents()

    def test_standardize_shows_rename_plan(
        self,
        qapp: QApplication,
        standardize_project_dir: Path,
    ) -> None:
        """标准化预览应显示重命名计划"""
        tab = CheckTab()
        tab.load_project(PROJECT_ID, str(standardize_project_dir))
        qapp.processEvents()

        tab._on_standardize()
        qapp.processEvents()

        item_labels = _get_item_labels(tab)
        # 应包含重命名计划文本（→ 符号）
        rename_labels = [lbl for lbl in item_labels if "→" in lbl.text()]
        assert len(rename_labels) > 0
        # 应包含目标标准名
        assert any("需求分析文档_REQ.md" in lbl.text() for lbl in rename_labels)
        tab.deleteLater()
        qapp.processEvents()

    def test_standardize_preview_title(
        self,
        qapp: QApplication,
        standardize_project_dir: Path,
    ) -> None:
        """标准化预览应显示预览标题"""
        tab = CheckTab()
        tab.load_project(PROJECT_ID, str(standardize_project_dir))
        qapp.processEvents()

        tab._on_standardize()
        qapp.processEvents()

        titles = _get_group_titles(tab)
        assert any("标准化命名预览" in t for t in titles)
        tab.deleteLater()
        qapp.processEvents()

    def test_standardize_no_plans_shows_hint(self, check_tab: CheckTab, qapp: QApplication) -> None:
        """无标准化计划时应显示提示"""
        # mixed 项目的 需求分析文档_v2.md 不匹配 NAMING_RULES 模式
        check_tab._on_standardize()
        qapp.processEvents()

        item_labels = _get_item_labels(check_tab)
        assert any("无需标准化" in lbl.text() for lbl in item_labels)

    def test_standardize_no_filesystem_change(
        self,
        qapp: QApplication,
        standardize_project_dir: Path,
    ) -> None:
        """apply=False 不应实际重命名文件"""
        tab = CheckTab()
        tab.load_project(PROJECT_ID, str(standardize_project_dir))
        qapp.processEvents()

        files_before = set(os.listdir(standardize_project_dir / "PRD"))

        tab._on_standardize()
        qapp.processEvents()

        files_after = set(os.listdir(standardize_project_dir / "PRD"))
        assert files_before == files_after
        tab.deleteLater()
        qapp.processEvents()


# ── 空项目测试 ───────────────────────────────────────────


class TestCheckTabEmptyProject:
    """CheckTab 空项目测试"""

    def test_empty_project_all_fail(self, qapp: QApplication, empty_project_dir: Path) -> None:
        """空项目应全部 fail"""
        tab = CheckTab()
        tab.load_project(PROJECT_ID, str(empty_project_dir))
        qapp.processEvents()

        _run_check(tab, qapp)

        assert tab._last_check_result is not None
        assert tab._last_check_result.fail_count > 0
        assert tab._last_check_result.pass_count == 0
        tab.deleteLater()
        qapp.processEvents()

    def test_empty_project_repair_buttons(
        self, qapp: QApplication, empty_project_dir: Path
    ) -> None:
        """空项目所有检查项都应有修复按钮（全 fail）"""
        tab = CheckTab()
        tab.load_project(PROJECT_ID, str(empty_project_dir))
        qapp.processEvents()

        _run_check(tab, qapp)

        item_btns = _get_item_buttons(tab)
        assert len(item_btns) > 0
        tab.deleteLater()
        qapp.processEvents()
