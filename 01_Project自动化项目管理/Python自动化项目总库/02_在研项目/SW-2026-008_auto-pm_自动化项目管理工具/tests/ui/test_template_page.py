"""TemplatePage 模板管理页单元测试

测试内容：
- TemplatePage 加载模板列表
- 模板卡片信息正确（图标/名称/版本/技术栈/使用项目数/描述）
- "更新项目"按钮存在
- 模板使用项目数统计正确（按 _src_path 匹配）
- 无模板时显示空状态提示

使用真实 TemplateService + ProjectService + 临时工作空间（不 mock），
遵循项目现有 qapp fixture 模式。
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

# 必须在导入 PySide6 前设置离屏渲染，避免无显示环境报错
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QPushButton  # noqa: E402

from auto_pm.core.project_service import ProjectService  # noqa: E402
from auto_pm.core.template_service import TemplateService  # noqa: E402
from auto_pm.db.connection import DatabaseManager  # noqa: E402
from auto_pm.ui.global_pages.template_page import (  # noqa: E402
    TemplateCard,
    TemplatePage,
    _infer_stack,
    _read_template_description,
)

# ── fixtures ─────────────────────────────────────────────


def _make_template_dir(templates_root: Path, name: str, comment: str) -> Path:
    """创建一个模板目录（含 copier.yml）"""
    tpl_dir = templates_root / name
    tpl_dir.mkdir(parents=True)
    (tpl_dir / "copier.yml").write_text(
        f"# Copier 模板配置 - {comment}\n"
        f"# 用于生成测试模板\n\n"
        "project_id:\n"
        "  type: str\n"
        "  help: 项目编号\n\n"
        "project_name:\n"
        "  type: str\n"
        "  help: 项目名称\n",
        encoding="utf-8",
    )
    return tpl_dir


def _make_project(
    workspace: Path,
    project_id: str,
    name: str,
    src_path: str,
) -> Path:
    """创建一个使用指定模板的项目（含 .copier-answers.yml）"""
    proj_dir = workspace / f"{project_id}_{name}"
    proj_dir.mkdir(parents=True)
    (proj_dir / ".copier-answers.yml").write_text(
        f"project_id: {project_id}\n"
        f"project_name: {name}\n"
        "version: V1.0.0\n"
        f"_src_path: {src_path}\n"
        "_commit: HEAD\n",
        encoding="utf-8",
    )
    return proj_dir


@pytest.fixture
def template_workspace(tmp_path: Path) -> Path:
    """临时工作空间，含模板目录和若干使用模板的项目

    结构：
        tmp_path/
            templates/
                plc-standard/        (PLC 模板)
                    copier.yml
                python-tool/         (Python 模板)
                    copier.yml
            SW-2026-001_项目A/       (使用 plc-standard)
                .copier-answers.yml
            SW-2026-002_项目B/       (使用 plc-standard)
                .copier-answers.yml
            SW-2026-003_项目C/       (使用 python-tool)
                .copier-answers.yml
    """
    templates_root = tmp_path / "templates"
    _make_template_dir(templates_root, "plc-standard", "PLC 标准项目（LSP-907）")
    _make_template_dir(templates_root, "python-tool", "Python 工具项目（210 规范）")

    _make_project(tmp_path, "SW-2026-001", "项目A", "templates/plc-standard")
    _make_project(tmp_path, "SW-2026-002", "项目B", "templates/plc-standard")
    _make_project(tmp_path, "SW-2026-003", "项目C", "templates/python-tool")

    return tmp_path


@pytest.fixture
def template_service(template_workspace: Path) -> TemplateService:
    """真实 TemplateService（指向临时工作空间的 templates 目录）"""
    return TemplateService(str(template_workspace / "templates"))


@pytest.fixture
def project_service(template_workspace: Path) -> ProjectService:
    """真实 ProjectService（含 DB 缓存，已同步项目）"""
    db = DatabaseManager(str(template_workspace))
    db.init_schema()
    svc = ProjectService(str(template_workspace), db=db)
    svc.sync_to_cache(force_full=True)
    return svc


# ── 辅助函数测试 ─────────────────────────────────────────


class TestHelpers:
    """辅助函数测试"""

    def test_infer_stack_plc(self) -> None:
        """plc-standard 应推断为 plc 技术栈"""
        assert _infer_stack("plc-standard") == "plc"

    def test_infer_stack_python(self) -> None:
        """python-tool 应推断为 python 技术栈"""
        assert _infer_stack("python-tool") == "python"

    def test_infer_stack_unknown(self) -> None:
        """未知模板名应推断为 unknown"""
        assert _infer_stack("custom-template") == "unknown"

    def test_read_template_description(
        self, template_workspace: Path
    ) -> None:
        """应从 copier.yml 首行注释提取描述"""
        tpl_path = str(template_workspace / "templates" / "plc-standard")
        desc = _read_template_description(tpl_path)
        assert "PLC 标准项目" in desc


# ── TemplatePage 加载测试 ───────────────────────────────


class TestTemplatePageLoading:
    """TemplatePage 加载测试"""

    def test_page_instantiation(
        self,
        qapp: QApplication,
        template_service: TemplateService,
        project_service: ProjectService,
    ) -> None:
        """TemplatePage 应能正常实例化"""
        page = TemplatePage(template_service, project_service)
        assert page is not None
        page.deleteLater()
        qapp.processEvents()

    def test_loads_template_list(
        self,
        qapp: QApplication,
        template_service: TemplateService,
        project_service: ProjectService,
    ) -> None:
        """应加载所有模板并渲染卡片"""
        page = TemplatePage(template_service, project_service)
        qapp.processEvents()

        # 应有 2 个模板卡片
        assert len(page._cards) == 2
        assert "plc-standard" in page._cards
        assert "python-tool" in page._cards
        page.deleteLater()
        qapp.processEvents()

    def test_empty_templates_shows_hint(
        self,
        qapp: QApplication,
        tmp_path: Path,
        project_service: ProjectService,
    ) -> None:
        """无模板时应显示空状态提示"""
        # 指向空目录的 TemplateService
        empty_templates = tmp_path / "empty_templates"
        empty_templates.mkdir()
        svc = TemplateService(str(empty_templates))

        page = TemplatePage(svc, project_service)
        qapp.processEvents()

        assert len(page._cards) == 0
        assert page._empty_hint.isVisibleTo(page) is True
        page.deleteLater()
        qapp.processEvents()

    def test_refresh_reloads_cards(
        self,
        qapp: QApplication,
        template_service: TemplateService,
        project_service: ProjectService,
    ) -> None:
        """refresh() 应重新加载模板列表"""
        page = TemplatePage(template_service, project_service)
        qapp.processEvents()
        assert len(page._cards) == 2

        # refresh 后仍应有 2 个卡片
        page.refresh()
        qapp.processEvents()
        assert len(page._cards) == 2
        page.deleteLater()
        qapp.processEvents()


# ── 模板卡片信息测试 ───────────────────────────────────


class TestTemplateCardInfo:
    """模板卡片信息正确性测试"""

    def test_plc_card_info(
        self,
        qapp: QApplication,
        template_service: TemplateService,
        project_service: ProjectService,
    ) -> None:
        """PLC 模板卡片应显示正确的图标/名称/技术栈/使用项目数"""
        page = TemplatePage(template_service, project_service)
        qapp.processEvents()

        card = page._cards["plc-standard"]
        assert card.template_name == "plc-standard"
        # 图标应为 PLC 工厂图标
        assert card._icon_label.text() == "🏭"
        # 标题为模板名
        assert card._title_label.text() == "plc-standard"
        # 元信息应包含技术栈 PLC 和使用项目数 2
        meta_text = card._meta_label.text()
        assert "PLC" in meta_text
        assert "使用项目: 2" in meta_text
        # 描述应包含 PLC
        assert "PLC" in card._desc_label.text()
        page.deleteLater()
        qapp.processEvents()

    def test_python_card_info(
        self,
        qapp: QApplication,
        template_service: TemplateService,
        project_service: ProjectService,
    ) -> None:
        """Python 模板卡片应显示正确的图标/名称/技术栈/使用项目数"""
        page = TemplatePage(template_service, project_service)
        qapp.processEvents()

        card = page._cards["python-tool"]
        assert card.template_name == "python-tool"
        # 图标应为 Python 蛇图标
        assert card._icon_label.text() == "🐍"
        # 标题为模板名
        assert card._title_label.text() == "python-tool"
        # 元信息应包含技术栈 Python 和使用项目数 1
        meta_text = card._meta_label.text()
        assert "Python" in meta_text
        assert "使用项目: 1" in meta_text
        # 描述应包含 Python
        assert "Python" in card._desc_label.text()
        page.deleteLater()
        qapp.processEvents()

    def test_card_version_displayed(
        self,
        qapp: QApplication,
        template_service: TemplateService,
        project_service: ProjectService,
    ) -> None:
        """卡片应显示版本号"""
        page = TemplatePage(template_service, project_service)
        qapp.processEvents()

        card = page._cards["plc-standard"]
        # copier.yml 无 _version 字段，应回退为默认 v1.0
        assert "v1.0" in card._meta_label.text()
        page.deleteLater()
        qapp.processEvents()


# ── 更新项目按钮测试 ───────────────────────────────────


class TestUpdateButton:
    """更新项目按钮测试"""

    def test_update_button_exists(
        self,
        qapp: QApplication,
        template_service: TemplateService,
        project_service: ProjectService,
    ) -> None:
        """每个模板卡片应包含"更新项目"按钮"""
        page = TemplatePage(template_service, project_service)
        qapp.processEvents()

        for name, card in page._cards.items():
            btn = card.update_button
            assert btn is not None
            assert btn.text() == "更新项目"
        page.deleteLater()
        qapp.processEvents()

    def test_update_button_is_pushbutton(
        self,
        qapp: QApplication,
        template_service: TemplateService,
        project_service: ProjectService,
    ) -> None:
        """更新项目按钮应为 QPushButton 实例"""
        page = TemplatePage(template_service, project_service)
        qapp.processEvents()

        card = page._cards["plc-standard"]
        assert isinstance(card.update_button, QPushButton)
        page.deleteLater()
        qapp.processEvents()

    def test_update_requested_signal(
        self,
        qapp: QApplication,
    ) -> None:
        """点击更新按钮应发射 updateRequested(template_name) 信号

        使用独立 TemplateCard（未连接到 TemplatePage）测试信号，
        避免触发页面的 QMessageBox 弹窗导致测试阻塞。
        """
        card = TemplateCard(
            template_name="plc-standard",
            stack="plc",
            version="v1.0",
            usage_count=0,
            description="测试模板",
        )
        qapp.processEvents()

        received: list[str] = []
        card.updateRequested.connect(received.append)
        card.updateRequested.emit("plc-standard")

        assert received == ["plc-standard"]
        card.deleteLater()
        qapp.processEvents()


# ── 模板使用项目数统计测试 ─────────────────────────────


class TestTemplateUsageCount:
    """模板使用项目数统计测试"""

    def test_usage_count_correct(
        self,
        qapp: QApplication,
        template_service: TemplateService,
        project_service: ProjectService,
    ) -> None:
        """使用项目数应按 _src_path 正确统计"""
        page = TemplatePage(template_service, project_service)
        qapp.processEvents()

        # plc-standard 被 2 个项目使用
        plc_card = page._cards["plc-standard"]
        assert "使用项目: 2" in plc_card._meta_label.text()

        # python-tool 被 1 个项目使用
        py_card = page._cards["python-tool"]
        assert "使用项目: 1" in py_card._meta_label.text()
        page.deleteLater()
        qapp.processEvents()

    def test_usage_count_zero_when_no_projects(
        self,
        qapp: QApplication,
        template_service: TemplateService,
        tmp_path: Path,
    ) -> None:
        """无项目使用模板时使用项目数应为 0"""
        # 创建一个不含项目的 DB
        empty_workspace = tmp_path / "empty_ws"
        empty_workspace.mkdir()
        db = DatabaseManager(str(empty_workspace))
        db.init_schema()
        svc = ProjectService(str(empty_workspace), db=db)

        page = TemplatePage(template_service, svc)
        qapp.processEvents()

        plc_card = page._cards["plc-standard"]
        assert "使用项目: 0" in plc_card._meta_label.text()
        page.deleteLater()
        qapp.processEvents()
