"""OverviewTab 工程资产摘要区块测试（V0.4.1 Step 1）

覆盖场景：
- PLC 项目 + healthy 资产摘要：渲染健康徽标 + 三类数量 + 问题摘要
- PLC 项目 + missing 资产目录：渲染缺失徽标 + 缺失提示
- PLC 项目 + warning 资产摘要：渲染警告徽标 + 问题列表
- 非 PLC 项目（Python）+ not_applicable：渲染不适用徽标 + 原因
- 项目 extra 缺失 asset_summary：降级为"暂无资产摘要"
- 项目 extra 为 None：降级为"暂无资产摘要"
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

# 必须在导入 PySide6 前设置离屏渲染，避免无显示环境报错
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QLabel, QWidget  # noqa: E402

from auto_pm.models import ProjectInfo  # noqa: E402
from auto_pm.ui.workspace.overview_tab import OverviewTab  # noqa: E402


def _make_plc_project(asset_summary: dict[str, Any] | None) -> ProjectInfo:
    """构造带 asset_summary 的 PLC ProjectInfo

    注意：使用三元表达式而非条件语句块，避免触发
    test_no_conditional_assertion_skips 元测试正则误判。
    """
    extra: dict[str, Any] = (
        {"asset_summary": asset_summary} if asset_summary is not None else {}
    )
    return ProjectInfo(
        project_id="DJ-2026-555",
        name="PLC 单机样例",
        path="/tmp/DJ-2026-555",
        stack="plc",
        version="V1.0.0",
        description="V0.4.1 Step 1 验证样例",
        source="copier",
        phase="developing",
        project_type="single_machine",
        equipment_type="conveyor",
        plc_vendor="Siemens",
        plc_model="S7-1200",
        extra=extra,
    )


def _make_python_project(asset_summary: dict[str, Any] | None) -> ProjectInfo:
    """构造带 asset_summary 的 Python ProjectInfo

    注意：使用三元表达式而非条件语句块，避免触发
    test_no_conditional_assertion_skips 元测试正则误判。
    """
    extra: dict[str, Any] = (
        {"asset_summary": asset_summary} if asset_summary is not None else {}
    )
    return ProjectInfo(
        project_id="SW-2026-008",
        name="auto-pm",
        path="/tmp/SW-2026-008",
        stack="python",
        version="V0.3.8",
        description="Python 项目样例",
        source="copier",
        phase="developing",
        extra=extra,
    )


def _find_label_by_text(parent: QWidget, text: str) -> QLabel | None:
    """在父组件下查找文本匹配的 QLabel"""
    labels = parent.findChildren(QLabel)
    for lbl in labels:
        if text in lbl.text():
            return lbl
    return None


# ── 工程资产摘要区块渲染测试 ───────────────────────────────


class TestOverviewTabAssetSummary:
    """OverviewTab 工程资产摘要区块渲染测试"""

    def test_plc_healthy_renders_badge_and_counts(
        self, qapp: QApplication
    ) -> None:
        """PLC 项目 + healthy 摘要：渲染健康徽标 + 三类数量 + 无问题提示"""
        asset_summary = {
            "status": "healthy",
            "asset_dir": "/tmp/DJ-2026-555/02_PLC程序/工程资产",
            "asset_dir_exists": True,
            "total_issues": 0,
            "issue_messages": [],
            "io_points": {"exists": True, "valid": True, "count": 4, "issues": []},
            "program_blocks": {"exists": True, "valid": True, "count": 3, "issues": []},
            "communications": {"exists": True, "valid": True, "count": 3, "issues": []},
        }
        proj = _make_plc_project(asset_summary)
        tab = OverviewTab()
        tab.load_project(proj)

        # 健康徽标存在
        badge = _find_label_by_text(tab._asset_summary_card, "健康")
        assert badge is not None, "应渲染健康徽标"
        # 三类数量展示
        assert _find_label_by_text(tab._asset_summary_card, "4") is not None, "IO 点数=4"
        assert _find_label_by_text(tab._asset_summary_card, "3") is not None, "程序块=3"
        # 无问题提示
        assert _find_label_by_text(tab._asset_summary_card, "无问题") is not None

        tab.deleteLater()
        qapp.processEvents()

    def test_plc_missing_renders_missing_badge(
        self, qapp: QApplication
    ) -> None:
        """PLC 项目 + missing 资产目录：渲染缺失徽标 + 缺失提示"""
        asset_summary = {
            "status": "missing",
            "asset_dir": "/tmp/DJ-2026-555/02_PLC程序/工程资产",
            "asset_dir_exists": False,
            "total_issues": 1,
            "issue_messages": ["缺少工程资产目录: 02_PLC程序/工程资产"],
            "io_points": {"exists": False, "valid": False, "count": 0, "issues": []},
            "program_blocks": {"exists": False, "valid": False, "count": 0, "issues": []},
            "communications": {"exists": False, "valid": False, "count": 0, "issues": []},
        }
        proj = _make_plc_project(asset_summary)
        tab = OverviewTab()
        tab.load_project(proj)

        # 缺失徽标
        badge = _find_label_by_text(tab._asset_summary_card, "缺失")
        assert badge is not None, "应渲染缺失徽标"
        # 缺失提示
        assert _find_label_by_text(tab._asset_summary_card, "缺少工程资产目录") is not None

        tab.deleteLater()
        qapp.processEvents()

    def test_plc_warning_renders_warning_badge_and_issues(
        self, qapp: QApplication
    ) -> None:
        """PLC 项目 + warning 摘要：渲染警告徽标 + 问题列表"""
        asset_summary = {
            "status": "warning",
            "asset_dir": "/tmp/DJ-2026-555/02_PLC程序/工程资产",
            "asset_dir_exists": True,
            "total_issues": 2,
            "issue_messages": [
                "io_points.csv 缺少列: station",
                "program_blocks.yml 第 1 项缺少字段: name",
            ],
            "io_points": {"exists": True, "valid": False, "count": 4, "issues": ["io_points.csv 缺少列: station"]},
            "program_blocks": {"exists": True, "valid": False, "count": 3, "issues": ["program_blocks.yml 第 1 项缺少字段: name"]},
            "communications": {"exists": True, "valid": True, "count": 3, "issues": []},
        }
        proj = _make_plc_project(asset_summary)
        tab = OverviewTab()
        tab.load_project(proj)

        # 警告徽标
        badge = _find_label_by_text(tab._asset_summary_card, "警告")
        assert badge is not None, "应渲染警告徽标"
        # 问题摘要
        assert _find_label_by_text(tab._asset_summary_card, "问题摘要") is not None
        assert _find_label_by_text(tab._asset_summary_card, "io_points.csv 缺少列") is not None
        assert _find_label_by_text(tab._asset_summary_card, "program_blocks.yml 第 1 项") is not None

        tab.deleteLater()
        qapp.processEvents()

    def test_python_not_applicable_renders_hint(
        self, qapp: QApplication
    ) -> None:
        """非 PLC 项目 + not_applicable：渲染不适用徽标 + 原因"""
        asset_summary = {
            "status": "not_applicable",
            "asset_dir": "",
            "asset_dir_exists": False,
            "total_issues": 0,
            "issue_messages": ["仅 PLC 项目支持工程资产摘要"],
            "io_points": {"exists": False, "valid": False, "count": 0, "issues": []},
            "program_blocks": {"exists": False, "valid": False, "count": 0, "issues": []},
            "communications": {"exists": False, "valid": False, "count": 0, "issues": []},
        }
        proj = _make_python_project(asset_summary)
        tab = OverviewTab()
        tab.load_project(proj)

        # 不适用徽标
        badge = _find_label_by_text(tab._asset_summary_card, "不适用")
        assert badge is not None, "应渲染不适用徽标"
        # 原因提示
        assert _find_label_by_text(tab._asset_summary_card, "仅 PLC 项目支持") is not None
        # 不应有"无问题"提示（not_applicable 分支提前返回）
        assert _find_label_by_text(tab._asset_summary_card, "无问题") is None

        tab.deleteLater()
        qapp.processEvents()

    def test_missing_asset_summary_shows_hint(
        self, qapp: QApplication
    ) -> None:
        """项目 extra 缺失 asset_summary：降级为"暂无资产摘要" """
        proj = _make_plc_project(asset_summary=None)
        tab = OverviewTab()
        tab.load_project(proj)

        # 应显示"暂无资产摘要"
        assert _find_label_by_text(tab._asset_summary_card, "暂无资产摘要") is not None
        # 不应显示健康徽标
        assert _find_label_by_text(tab._asset_summary_card, "健康") is None

        tab.deleteLater()
        qapp.processEvents()

    def test_issue_messages_truncated_with_more_label(
        self, qapp: QApplication
    ) -> None:
        """问题摘要超过 3 条时显示"+N 更多"提示"""
        issues = [f"问题 {i+1}" for i in range(5)]
        asset_summary = {
            "status": "warning",
            "asset_dir": "/tmp/DJ-2026-555/02_PLC程序/工程资产",
            "asset_dir_exists": True,
            "total_issues": 5,
            "issue_messages": issues,
            "io_points": {"exists": True, "valid": False, "count": 0, "issues": issues[:2]},
            "program_blocks": {"exists": True, "valid": False, "count": 0, "issues": issues[2:4]},
            "communications": {"exists": True, "valid": False, "count": 0, "issues": [issues[4]]},
        }
        proj = _make_plc_project(asset_summary)
        tab = OverviewTab()
        tab.load_project(proj)

        # 前 3 条显示
        assert _find_label_by_text(tab._asset_summary_card, "问题 1") is not None
        assert _find_label_by_text(tab._asset_summary_card, "问题 3") is not None
        # 第 4 条不应直接显示
        issue4 = _find_label_by_text(tab._asset_summary_card, "• 问题 4")
        assert issue4 is None, "第 4 条不应直接显示"
        # "+2 更多"提示
        assert _find_label_by_text(tab._asset_summary_card, "+2 更多") is not None

        tab.deleteLater()
        qapp.processEvents()


# ── 既有 UI 测试无回归验证 ─────────────────────────────────


class TestOverviewTabNoRegression:
    """OverviewTab 既有功能无回归验证"""

    def test_load_project_python_without_extra(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """Python 项目（无 extra）加载不抛异常，资产摘要降级为"暂无" """
        proj = ProjectInfo(
            project_id="SW-2026-008",
            name="测试项目",
            path=str(tmp_path),
            stack="python",
            version="V1.0.0",
            description="无回归测试",
            source="copier",
            phase="developing",
        )
        tab = OverviewTab()
        tab.load_project(proj)

        # 既有功能仍工作
        assert tab._project is not None
        # 资产摘要降级提示
        assert _find_label_by_text(tab._asset_summary_card, "暂无资产摘要") is not None

        tab.deleteLater()
        qapp.processEvents()

    def test_asset_summary_card_exists_after_build_ui(
        self, qapp: QApplication
    ) -> None:
        """_build_ui 后工程资产摘要卡片应已实例化"""
        tab = OverviewTab()
        assert tab._asset_summary_card is not None
        assert tab._asset_summary_layout is not None
        tab.deleteLater()
        qapp.processEvents()
