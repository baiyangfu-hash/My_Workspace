"""ReportPage 单元测试

测试内容：
- ReportPage 加载
- 4 个统计卡片显示
- 数据正确性
- refresh() 方法

使用真实 Service + 临时工作空间（DB 缓存模式），遵循项目现有 qapp fixture 模式。
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

# 必须在导入 PySide6 前设置离屏渲染，避免无显示环境报错
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import (  # noqa: E402
    QApplication,
    QGroupBox,
    QLabel,
    QProgressBar,
)

from auto_pm.change.change_service import ChangeService  # noqa: E402
from auto_pm.core.project_service import ProjectService  # noqa: E402
from auto_pm.core.report_service import ReportService  # noqa: E402
from auto_pm.db.connection import DatabaseManager  # noqa: E402
from auto_pm.db.repository import ChangeRequestRepository  # noqa: E402
from auto_pm.models import ChangeSummary, ProjectRecord  # noqa: E402
from auto_pm.ui.global_pages.report_page import ReportPage  # noqa: E402

# ── fixtures ─────────────────────────────────────────────


@pytest.fixture
def db(tmp_path: Path) -> DatabaseManager:
    """临时 DB（已建表）"""
    d = DatabaseManager(str(tmp_path))
    d.init_schema()
    return d


@pytest.fixture
def report_service(tmp_path: Path, db: DatabaseManager) -> ReportService:
    """真实 ReportService（注入带 DB 的 Service）"""
    ps = ProjectService(str(tmp_path), db=db)
    cs = ChangeService(str(tmp_path), db=db)
    return ReportService(ps, cs)


def _make_project_record(
    project_id: str,
    name: str = "",
    stack: str = "plc",
    phase: str = "developing",
    business_line: str = "",
) -> ProjectRecord:
    """构造测试用 ProjectRecord"""
    return ProjectRecord(
        project_id=project_id,
        name=name or project_id,
        path=f"/tmp/{project_id}",
        stack=stack,
        version="V1.0.0",
        description="",
        source="copier",
        phase=phase,
        business_line=business_line,
        extra={},
        file_mtime=1000.0,
        last_scanned="2026-01-01",
    )


def _make_change_summary(
    change_number: str,
    project_id: str = "SW-2026-001",
    domain: str = "PLC",
    status: str = "draft",
) -> ChangeSummary:
    """构造测试用 ChangeSummary"""
    return ChangeSummary(
        change_number=change_number,
        project_id=project_id,
        project_name=project_id,
        domain=domain,
        business_nature="REQ",
        impact_scope=["LOCAL"],
        status=status,
        applicant="张三",
        apply_date="2026-01-01",
        title="测试变更",
    )


def _seed_data(
    project_service: ProjectService,
    db: DatabaseManager,
    projects: list[ProjectRecord],
    changes: list[ChangeSummary] | None = None,
) -> None:
    """预置项目和变更数据到 DB"""
    assert project_service._repo is not None
    for r in projects:
        project_service._repo.upsert(r)
    if changes:
        repo = ChangeRequestRepository(db)
        for c in changes:
            repo.upsert(c)


# ── ReportPage 加载测试 ──────────────────────────────────


class TestReportPageLoad:
    """ReportPage 实例化与基础结构测试"""

    def test_instantiation(
        self, qapp: QApplication, report_service: ReportService
    ) -> None:
        """ReportPage 应能正常实例化"""
        page = ReportPage(report_service)
        assert page is not None
        assert page.objectName() == "reportPage"
        page.deleteLater()
        qapp.processEvents()

    def test_has_four_cards(
        self, qapp: QApplication, report_service: ReportService
    ) -> None:
        """应包含 4 个统计卡片（QGroupBox）"""
        page = ReportPage(report_service)
        cards = page.findChildren(QGroupBox)
        assert len(cards) == 4
        titles = [c.title() for c in cards]
        assert "项目概览" in titles
        assert "阶段分布" in titles
        assert "业务线分布" in titles
        assert "变更统计" in titles
        page.deleteLater()
        qapp.processEvents()

    def test_card_references(
        self, qapp: QApplication, report_service: ReportService
    ) -> None:
        """4 个卡片引用应正确"""
        page = ReportPage(report_service)
        assert isinstance(page._project_card, QGroupBox)
        assert isinstance(page._phase_card, QGroupBox)
        assert isinstance(page._bl_card, QGroupBox)
        assert isinstance(page._change_card, QGroupBox)
        assert page._project_card.title() == "项目概览"
        assert page._phase_card.title() == "阶段分布"
        assert page._bl_card.title() == "业务线分布"
        assert page._change_card.title() == "变更统计"
        page.deleteLater()
        qapp.processEvents()


# ── refresh() 与数据正确性测试 ───────────────────────────


class TestReportPageRefresh:
    """refresh() 方法与数据渲染测试"""

    def test_refresh_empty_data(
        self, qapp: QApplication, report_service: ReportService
    ) -> None:
        """空数据 refresh 应渲染摘要为 0"""
        page = ReportPage(report_service)
        page.refresh()
        qapp.processEvents()

        # 项目概览卡片应含"总项目数: 0"
        summary_labels = page._project_card.findChildren(QLabel)
        texts = [label.text() for label in summary_labels]
        assert any("总项目数: 0" in t for t in texts)

        # 变更统计卡片应含"总变更: 0"
        change_labels = page._change_card.findChildren(QLabel)
        texts = [label.text() for label in change_labels]
        assert any("总变更: 0" in t for t in texts)
        page.deleteLater()
        qapp.processEvents()

    def test_refresh_with_data(
        self,
        qapp: QApplication,
        tmp_path: Path,
        db: DatabaseManager,
    ) -> None:
        """有数据 refresh 应渲染正确数值"""
        ps = ProjectService(str(tmp_path), db=db)
        cs = ChangeService(str(tmp_path), db=db)
        svc = ReportService(ps, cs)

        _seed_data(
            ps,
            db,
            projects=[
                _make_project_record("SW-2026-001", "项目A", "python", "developing", "SW"),
                _make_project_record("SW-2026-002", "项目B", "plc", "developing", "SW"),
                _make_project_record("DJ-2026-001", "项目C", "plc", "production", "DJ"),
            ],
            changes=[
                _make_change_summary("CHG-PLC-2026-001", status="draft"),
                _make_change_summary("CHG-PLC-2026-002", status="implementing"),
                _make_change_summary("CHG-PLC-2026-003", status="completed"),
            ],
        )

        page = ReportPage(svc)
        page.refresh()
        qapp.processEvents()

        # 项目概览：总项目数 3
        proj_labels = page._project_card.findChildren(QLabel)
        proj_texts = [label.text() for label in proj_labels]
        assert any("总项目数: 3" in t for t in proj_texts)

        # 变更统计：总变更 3
        chg_labels = page._change_card.findChildren(QLabel)
        chg_texts = [label.text() for label in chg_labels]
        assert any("总变更: 3" in t for t in chg_texts)
        page.deleteLater()
        qapp.processEvents()

    def test_refresh_renders_progress_bars(
        self,
        qapp: QApplication,
        tmp_path: Path,
        db: DatabaseManager,
    ) -> None:
        """refresh 后卡片应包含 QProgressBar 柱状图"""
        ps = ProjectService(str(tmp_path), db=db)
        cs = ChangeService(str(tmp_path), db=db)
        svc = ReportService(ps, cs)

        _seed_data(
            ps,
            db,
            projects=[
                _make_project_record("SW-2026-001", "项目A", "plc", "developing", "SW"),
            ],
        )

        page = ReportPage(svc)
        page.refresh()
        qapp.processEvents()

        # 项目概览卡片应含进度条
        bars = page._project_card.findChildren(QProgressBar)
        assert len(bars) > 0
        # 阶段分布卡片应含进度条
        phase_bars = page._phase_card.findChildren(QProgressBar)
        assert len(phase_bars) > 0
        page.deleteLater()
        qapp.processEvents()

    def test_refresh_idempotent(
        self,
        qapp: QApplication,
        tmp_path: Path,
        db: DatabaseManager,
    ) -> None:
        """多次 refresh 不应累积组件"""
        ps = ProjectService(str(tmp_path), db=db)
        cs = ChangeService(str(tmp_path), db=db)
        svc = ReportService(ps, cs)

        _seed_data(
            ps,
            db,
            projects=[
                _make_project_record("SW-2026-001", "项目A", "plc", "developing", "SW"),
            ],
        )

        page = ReportPage(svc)
        page.refresh()
        qapp.processEvents()
        bars_after_first = len(page._project_card.findChildren(QProgressBar))

        page.refresh()
        qapp.processEvents()
        bars_after_second = len(page._project_card.findChildren(QProgressBar))

        assert bars_after_first == bars_after_second
        page.deleteLater()
        qapp.processEvents()

    def test_refresh_updates_after_data_change(
        self,
        qapp: QApplication,
        tmp_path: Path,
        db: DatabaseManager,
    ) -> None:
        """数据变化后 refresh 应更新显示"""
        ps = ProjectService(str(tmp_path), db=db)
        cs = ChangeService(str(tmp_path), db=db)
        svc = ReportService(ps, cs)

        # 初始无数据
        page = ReportPage(svc)
        page.refresh()
        qapp.processEvents()
        labels = page._project_card.findChildren(QLabel)
        texts = [label.text() for label in labels]
        assert any("总项目数: 0" in t for t in texts)

        # 新增数据后 refresh
        _seed_data(
            ps,
            db,
            projects=[
                _make_project_record("SW-2026-001", "项目A", "plc", "developing", "SW"),
                _make_project_record("DJ-2026-001", "项目B", "plc", "production", "DJ"),
            ],
        )
        page.refresh()
        qapp.processEvents()

        labels = page._project_card.findChildren(QLabel)
        texts = [label.text() for label in labels]
        assert any("总项目数: 2" in t for t in texts)
        page.deleteLater()
        qapp.processEvents()


# ── 卡片数据正确性测试 ───────────────────────────────────


class TestReportPageCardData:
    """各卡片数据渲染正确性测试"""

    def test_project_overview_card(
        self,
        qapp: QApplication,
        tmp_path: Path,
        db: DatabaseManager,
    ) -> None:
        """项目概览卡片应正确显示总数和技术栈分布"""
        ps = ProjectService(str(tmp_path), db=db)
        cs = ChangeService(str(tmp_path), db=db)
        svc = ReportService(ps, cs)

        _seed_data(
            ps,
            db,
            projects=[
                _make_project_record("SW-2026-001", "A", "python", "developing", "SW"),
                _make_project_record("SW-2026-002", "B", "python", "developing", "SW"),
                _make_project_record("DJ-2026-001", "C", "plc", "production", "DJ"),
            ],
        )

        page = ReportPage(svc)
        page.refresh()
        qapp.processEvents()

        labels = page._project_card.findChildren(QLabel)
        texts = [label.text() for label in labels]
        # 总数
        assert any("总项目数: 3" in t for t in texts)
        # Python 计数 2
        assert "2" in texts
        page.deleteLater()
        qapp.processEvents()

    def test_phase_distribution_card(
        self,
        qapp: QApplication,
        tmp_path: Path,
        db: DatabaseManager,
    ) -> None:
        """阶段分布卡片应显示 4 个阶段"""
        ps = ProjectService(str(tmp_path), db=db)
        cs = ChangeService(str(tmp_path), db=db)
        svc = ReportService(ps, cs)

        _seed_data(
            ps,
            db,
            projects=[
                _make_project_record("SW-2026-001", "A", "plc", "developing", "SW"),
                _make_project_record("DJ-2026-001", "B", "plc", "production", "DJ"),
            ],
        )

        page = ReportPage(svc)
        page.refresh()
        qapp.processEvents()

        labels = page._phase_card.findChildren(QLabel)
        texts = [label.text() for label in labels]
        # 应包含 4 个阶段标签
        assert any("开发中" in t for t in texts)
        assert any("调试中" in t for t in texts)
        assert any("生产中" in t for t in texts)
        assert any("已归档" in t for t in texts)
        page.deleteLater()
        qapp.processEvents()

    def test_bl_distribution_card(
        self,
        qapp: QApplication,
        tmp_path: Path,
        db: DatabaseManager,
    ) -> None:
        """业务线分布卡片应显示 5 个业务线"""
        ps = ProjectService(str(tmp_path), db=db)
        cs = ChangeService(str(tmp_path), db=db)
        svc = ReportService(ps, cs)

        _seed_data(
            ps,
            db,
            projects=[
                _make_project_record("SW-2026-001", "A", "plc", "developing", "SW"),
                _make_project_record("DJ-2026-001", "B", "plc", "production", "DJ"),
            ],
        )

        page = ReportPage(svc)
        page.refresh()
        qapp.processEvents()

        labels = page._bl_card.findChildren(QLabel)
        texts = [label.text() for label in labels]
        # 应包含 5 个业务线标签
        assert any(t == "SW" for t in texts)
        assert any(t == "DJ" for t in texts)
        assert any(t == "ZD" for t in texts)
        assert any(t == "XT" for t in texts)
        assert any(t == "WX" for t in texts)
        page.deleteLater()
        qapp.processEvents()

    def test_change_overview_card(
        self,
        qapp: QApplication,
        tmp_path: Path,
        db: DatabaseManager,
    ) -> None:
        """变更统计卡片应正确显示总数和状态分布"""
        ps = ProjectService(str(tmp_path), db=db)
        cs = ChangeService(str(tmp_path), db=db)
        svc = ReportService(ps, cs)

        _seed_data(
            ps,
            db,
            projects=[
                _make_project_record("SW-2026-001", "项目A", "plc", "developing", "SW"),
            ],
            changes=[
                _make_change_summary("CHG-PLC-2026-001", status="draft"),
                _make_change_summary("CHG-PLC-2026-002", status="draft"),
                _make_change_summary("CHG-PLC-2026-003", status="implementing"),
            ],
        )

        page = ReportPage(svc)
        page.refresh()
        qapp.processEvents()

        labels = page._change_card.findChildren(QLabel)
        texts = [label.text() for label in labels]
        # 总数
        assert any("总变更: 3" in t for t in texts)
        # 状态标签
        assert any("草稿" in t for t in texts)
        assert any("实施中" in t for t in texts)
        page.deleteLater()
        qapp.processEvents()
