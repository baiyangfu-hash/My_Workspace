"""SettingsPage 系统设置页单元测试

测试内容：
- SettingsPage 加载
- 工作空间路径显示
- 数据库统计显示（项目记录数/变更记录数/缓存路径/上次同步时间）
- "清除缓存"按钮存在
- "重建索引"按钮存在
- 无 DB 时回退显示

使用真实 ProjectService + ChangeService + 临时工作空间（不 mock），
遵循项目现有 qapp fixture 模式。
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

# 必须在导入 PySide6 前设置离屏渲染，避免无显示环境报错
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QPushButton  # noqa: E402

from auto_pm.change.change_service import ChangeService  # noqa: E402
from auto_pm.core.project_service import ProjectService  # noqa: E402
from auto_pm.db.connection import DatabaseManager  # noqa: E402
from auto_pm.ui.global_pages.settings_page import SettingsPage  # noqa: E402

# ── fixtures ─────────────────────────────────────────────


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """提供全局 QApplication 实例（session 级复用）"""
    app = QApplication.instance() or QApplication([])
    yield app


def _make_project(workspace: Path, project_id: str, name: str) -> Path:
    """创建一个使用 copier 模板的项目"""
    proj_dir = workspace / f"{project_id}_{name}"
    proj_dir.mkdir(parents=True)
    (proj_dir / ".copier-answers.yml").write_text(
        f"project_id: {project_id}\n"
        f"project_name: {name}\n"
        "version: V1.0.0\n"
        "_src_path: templates/python-tool\n"
        "_commit: HEAD\n",
        encoding="utf-8",
    )
    return proj_dir


@pytest.fixture
def settings_workspace(tmp_path: Path) -> Path:
    """临时工作空间，含若干项目"""
    _make_project(tmp_path, "SW-2026-001", "项目A")
    _make_project(tmp_path, "SW-2026-002", "项目B")
    return tmp_path


@pytest.fixture
def db(settings_workspace: Path) -> DatabaseManager:
    """创建并初始化 DB，同步项目缓存"""
    db = DatabaseManager(str(settings_workspace))
    db.init_schema()
    return db


@pytest.fixture
def project_service(settings_workspace: Path, db: DatabaseManager) -> ProjectService:
    """真实 ProjectService（含 DB 缓存，已同步项目）"""
    svc = ProjectService(str(settings_workspace), db=db)
    svc.sync_to_cache(force_full=True)
    return svc


@pytest.fixture
def change_service(settings_workspace: Path, db: DatabaseManager) -> ChangeService:
    """真实 ChangeService（含 DB 缓存）"""
    return ChangeService(str(settings_workspace), db=db)


# ── SettingsPage 加载测试 ───────────────────────────────


class TestSettingsPageLoading:
    """SettingsPage 加载测试"""

    def test_page_instantiation(
        self,
        qapp: QApplication,
        project_service: ProjectService,
        change_service: ChangeService,
    ) -> None:
        """SettingsPage 应能正常实例化"""
        page = SettingsPage(project_service, change_service)
        assert page is not None
        page.deleteLater()
        qapp.processEvents()

    def test_workspace_path_displayed(
        self,
        qapp: QApplication,
        project_service: ProjectService,
        change_service: ChangeService,
        settings_workspace: Path,
    ) -> None:
        """应显示工作空间路径"""
        page = SettingsPage(project_service, change_service)
        qapp.processEvents()

        assert page.workspace_edit.text() == str(settings_workspace)
        page.deleteLater()
        qapp.processEvents()

    def test_scan_depth_default(
        self,
        qapp: QApplication,
        project_service: ProjectService,
        change_service: ChangeService,
    ) -> None:
        """扫描深度默认应为 4"""
        page = SettingsPage(project_service, change_service)
        qapp.processEvents()

        assert page.depth_spin.value() == 4
        page.deleteLater()
        qapp.processEvents()

    def test_refresh_reloads_stats(
        self,
        qapp: QApplication,
        project_service: ProjectService,
        change_service: ChangeService,
    ) -> None:
        """refresh() 应重新加载统计"""
        page = SettingsPage(project_service, change_service)
        qapp.processEvents()

        before = page.project_count_label.text()
        page.refresh()
        qapp.processEvents()
        after = page.project_count_label.text()
        assert before == after  # 项目数应保持一致
        page.deleteLater()
        qapp.processEvents()


# ── 数据库统计显示测试 ─────────────────────────────────


class TestDbStatsDisplay:
    """数据库统计显示测试"""

    def test_db_path_displayed(
        self,
        qapp: QApplication,
        project_service: ProjectService,
        change_service: ChangeService,
        settings_workspace: Path,
    ) -> None:
        """应显示缓存路径"""
        page = SettingsPage(project_service, change_service)
        qapp.processEvents()

        expected_path = str(settings_workspace / ".auto-pm" / "index.db")
        assert expected_path in page.db_path_label.text()
        page.deleteLater()
        qapp.processEvents()

    def test_project_count_displayed(
        self,
        qapp: QApplication,
        project_service: ProjectService,
        change_service: ChangeService,
    ) -> None:
        """应显示项目记录数（2 个项目）"""
        page = SettingsPage(project_service, change_service)
        qapp.processEvents()

        text = page.project_count_label.text()
        assert "项目记录" in text
        assert "2 条" in text
        page.deleteLater()
        qapp.processEvents()

    def test_change_count_displayed(
        self,
        qapp: QApplication,
        project_service: ProjectService,
        change_service: ChangeService,
    ) -> None:
        """应显示变更记录数（0 条）"""
        page = SettingsPage(project_service, change_service)
        qapp.processEvents()

        text = page.change_count_label.text()
        assert "变更记录" in text
        assert "0 条" in text
        page.deleteLater()
        qapp.processEvents()

    def test_last_sync_displayed(
        self,
        qapp: QApplication,
        project_service: ProjectService,
        change_service: ChangeService,
    ) -> None:
        """应显示上次同步时间（同步后应有值）"""
        page = SettingsPage(project_service, change_service)
        qapp.processEvents()

        text = page.last_sync_label.text()
        assert "上次同步" in text
        # 同步过应有时间值（非 '—'）
        assert "—" not in text
        page.deleteLater()
        qapp.processEvents()


# ── 按钮存在性测试 ─────────────────────────────────────


class TestButtons:
    """按钮存在性测试"""

    def test_clear_cache_button_exists(
        self,
        qapp: QApplication,
        project_service: ProjectService,
        change_service: ChangeService,
    ) -> None:
        """应存在"清除缓存"按钮"""
        page = SettingsPage(project_service, change_service)
        qapp.processEvents()

        btn = page.clear_cache_button
        assert btn is not None
        assert btn.text() == "清除缓存"
        assert isinstance(btn, QPushButton)
        page.deleteLater()
        qapp.processEvents()

    def test_rebuild_button_exists(
        self,
        qapp: QApplication,
        project_service: ProjectService,
        change_service: ChangeService,
    ) -> None:
        """应存在"重建索引"按钮"""
        page = SettingsPage(project_service, change_service)
        qapp.processEvents()

        btn = page.rebuild_button
        assert btn is not None
        assert btn.text() == "重建索引"
        assert isinstance(btn, QPushButton)
        page.deleteLater()
        qapp.processEvents()


# ── 无 DB 回退测试 ─────────────────────────────────────


class TestNoDbFallback:
    """无 DB 时回退显示测试"""

    def test_stats_show_unavailable_without_db(
        self,
        qapp: QApplication,
        settings_workspace: Path,
    ) -> None:
        """无 DB 时统计应显示未连接/—"""
        # 不注入 DB 的 ProjectService
        proj_svc = ProjectService(str(settings_workspace))
        chg_svc = ChangeService(str(settings_workspace))

        page = SettingsPage(proj_svc, chg_svc)
        qapp.processEvents()

        assert "未连接" in page.db_path_label.text()
        assert "—" in page.project_count_label.text()
        assert "—" in page.change_count_label.text()
        assert "—" in page.last_sync_label.text()
        page.deleteLater()
        qapp.processEvents()
