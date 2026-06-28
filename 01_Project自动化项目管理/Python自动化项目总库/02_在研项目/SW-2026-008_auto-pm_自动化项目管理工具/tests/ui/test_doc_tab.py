"""DocTab 单元测试

测试内容：
- load_project 后文档列表加载
- 文档分类正确（PM_SESSION/立项表/变更单/整改项/其他）
- 双击文档 → 打开信号
- 模板信息显示
- "模板更新"按钮存在
- 空项目（无文档）显示空状态

使用真实文件系统 + 临时项目目录（不 mock），遵循项目现有 qapp fixture 模式。
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

# 必须在导入 PySide6 前设置离屏渲染，避免无显示环境报错
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QUrl  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from auto_pm.core.template_service import TemplateService  # noqa: E402
from auto_pm.ui.workspace.doc_tab import DocTab  # noqa: E402

# ── fixtures ─────────────────────────────────────────────


@pytest.fixture
def template_service(tmp_path: Path) -> TemplateService:
    """真实 TemplateService（指向临时模板目录）"""
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    return TemplateService(str(templates_dir))


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    """临时项目目录，含 .copier-answers.yml 和各类文档"""
    project_id = "TEST-2026-001"
    project_path = tmp_path / f"{project_id}_测试项目"
    project_path.mkdir()

    # .copier-answers.yml（模板信息来源）
    (project_path / ".copier-answers.yml").write_text(
        "_commit: abc1234\n"
        "_src_path: templates/plc-standard\n"
        "project_id: TEST-2026-001\n"
        "project_name: 测试项目\n"
        "version: V1.0.0\n",
        encoding="utf-8",
    )

    # PM_SESSION 文档
    (project_path / f"PM_SESSION_{project_id}.md").write_text(
        "# PM_SESSION\n测试会话", encoding="utf-8"
    )

    # 立项表文档
    (project_path / f"立项表_{project_id}.md").write_text(
        "# 立项表\n测试立项", encoding="utf-8"
    )

    # 变更单文档（CHG- 前缀）
    (project_path / "CHG-TEST-2026-001-001.md").write_text(
        "# 变更单\n测试变更", encoding="utf-8"
    )

    # 变更单文档（变更单_ 前缀）
    (project_path / "变更单_CHG-TEST-2026-001-002.md").write_text(
        "# 变更单2\n测试变更2", encoding="utf-8"
    )

    # 整改项目录及文档
    rect_dir = project_path / "09_整改项"
    rect_dir.mkdir()
    (rect_dir / "V2.0-测试整改.md").write_text("# 整改\n测试整改", encoding="utf-8")

    # 其他文档
    (project_path / "README.md").write_text("# README\n测试说明", encoding="utf-8")

    return project_path


@pytest.fixture
def empty_project_dir(tmp_path: Path) -> Path:
    """空项目目录（无任何 .md 文档）"""
    project_path = tmp_path / "EMPTY-2026-001_空项目"
    project_path.mkdir()
    return project_path


# ── 辅助函数 ─────────────────────────────────────────────


def _get_category_labels(tab: DocTab) -> list[str]:
    """获取文档树所有分类节点的文本"""
    return [item.text(0) for item in tab._get_category_items()]


def _find_category(tab: DocTab, keyword: str):
    """按关键字查找分类节点"""
    for item in tab._get_category_items():
        if keyword in item.text(0):
            return item
    return None


# ── DocTab 加载测试 ──────────────────────────────────────


class TestDocTabLoad:
    """DocTab 加载测试"""

    def test_load_project_loads_documents(
        self,
        qapp: QApplication,
        template_service: TemplateService,
        project_dir: Path,
    ) -> None:
        """load_project 后应加载文档列表"""
        tab = DocTab(template_service)
        tab.load_project("TEST-2026-001", str(project_dir))
        qapp.processEvents()

        # 应有分类节点（非空）
        cats = tab._get_category_items()
        assert len(cats) > 0
        # 空状态提示应隐藏
        assert tab._empty_hint.isVisibleTo(tab) is False
        tab.deleteLater()
        qapp.processEvents()

    def test_load_empty_project_shows_hint(
        self,
        qapp: QApplication,
        template_service: TemplateService,
        empty_project_dir: Path,
    ) -> None:
        """空项目（无文档）应显示空状态提示"""
        tab = DocTab(template_service)
        tab.load_project("EMPTY-2026-001", str(empty_project_dir))
        qapp.processEvents()

        cats = tab._get_category_items()
        assert len(cats) == 0
        assert tab._empty_hint.isVisibleTo(tab) is True
        tab.deleteLater()
        qapp.processEvents()

    def test_load_project_without_path(
        self,
        qapp: QApplication,
        template_service: TemplateService,
    ) -> None:
        """未加载项目时文档树应为空"""
        tab = DocTab(template_service)
        qapp.processEvents()

        # 直接检查初始状态
        assert tab._doc_tree.topLevelItemCount() == 0
        tab.deleteLater()
        qapp.processEvents()


# ── 文档分类测试 ────────────────────────────────────────


class TestDocTabClassification:
    """DocTab 文档分类测试"""

    def test_pm_session_classification(
        self,
        qapp: QApplication,
        template_service: TemplateService,
        project_dir: Path,
    ) -> None:
        """PM_SESSION_*.md 应归入 PM_SESSION 类"""
        tab = DocTab(template_service)
        tab.load_project("TEST-2026-001", str(project_dir))
        qapp.processEvents()

        cat = _find_category(tab, "PM_SESSION")
        assert cat is not None
        docs = tab._get_documents_in_category(cat)
        assert len(docs) == 1
        assert "PM_SESSION_TEST-2026-001" in docs[0].text(0)
        tab.deleteLater()
        qapp.processEvents()

    def test_initiation_classification(
        self,
        qapp: QApplication,
        template_service: TemplateService,
        project_dir: Path,
    ) -> None:
        """立项表_*.md 应归入立项表类"""
        tab = DocTab(template_service)
        tab.load_project("TEST-2026-001", str(project_dir))
        qapp.processEvents()

        cat = _find_category(tab, "立项表")
        assert cat is not None
        docs = tab._get_documents_in_category(cat)
        assert len(docs) == 1
        assert "立项表_TEST-2026-001" in docs[0].text(0)
        tab.deleteLater()
        qapp.processEvents()

    def test_change_classification(
        self,
        qapp: QApplication,
        template_service: TemplateService,
        project_dir: Path,
    ) -> None:
        """变更单_*.md 和 CHG-*.md 应归入变更单类"""
        tab = DocTab(template_service)
        tab.load_project("TEST-2026-001", str(project_dir))
        qapp.processEvents()

        cat = _find_category(tab, "变更单")
        assert cat is not None
        docs = tab._get_documents_in_category(cat)
        assert len(docs) == 2
        tab.deleteLater()
        qapp.processEvents()

    def test_rectification_classification(
        self,
        qapp: QApplication,
        template_service: TemplateService,
        project_dir: Path,
    ) -> None:
        """09_整改项/ 目录下的 .md 应归入整改项类"""
        tab = DocTab(template_service)
        tab.load_project("TEST-2026-001", str(project_dir))
        qapp.processEvents()

        cat = _find_category(tab, "整改项")
        assert cat is not None
        docs = tab._get_documents_in_category(cat)
        assert len(docs) == 1
        assert "V2.0-测试整改" in docs[0].text(0)
        tab.deleteLater()
        qapp.processEvents()

    def test_other_classification(
        self,
        qapp: QApplication,
        template_service: TemplateService,
        project_dir: Path,
    ) -> None:
        """其他 .md 应归入其他文档类"""
        tab = DocTab(template_service)
        tab.load_project("TEST-2026-001", str(project_dir))
        qapp.processEvents()

        cat = _find_category(tab, "其他文档")
        assert cat is not None
        docs = tab._get_documents_in_category(cat)
        assert len(docs) == 1
        assert "README" in docs[0].text(0)
        tab.deleteLater()
        qapp.processEvents()

    def test_all_categories_present(
        self,
        qapp: QApplication,
        template_service: TemplateService,
        project_dir: Path,
    ) -> None:
        """应包含所有 5 个分类（PM_SESSION/立项表/变更单/整改项/其他）"""
        tab = DocTab(template_service)
        tab.load_project("TEST-2026-001", str(project_dir))
        qapp.processEvents()

        labels = _get_category_labels(tab)
        assert any("PM_SESSION" in label for label in labels)
        assert any("立项表" in label for label in labels)
        assert any("变更单" in label for label in labels)
        assert any("整改项" in label for label in labels)
        assert any("其他文档" in label for label in labels)
        tab.deleteLater()
        qapp.processEvents()


# ── 双击打开测试 ────────────────────────────────────────


class TestDocTabDoubleClick:
    """DocTab 双击打开文档测试"""

    def test_double_click_opens_document(
        self,
        qapp: QApplication,
        template_service: TemplateService,
        project_dir: Path,
    ) -> None:
        """双击文档节点应调用 QDesktopServices.openUrl"""
        tab = DocTab(template_service)
        tab.load_project("TEST-2026-001", str(project_dir))
        qapp.processEvents()

        # 找到 PM_SESSION 分类下的文档
        cat = _find_category(tab, "PM_SESSION")
        assert cat is not None
        docs = tab._get_documents_in_category(cat)
        assert len(docs) == 1
        doc_item = docs[0]

        # mock QDesktopServices.openUrl 避免真正打开文件
        with patch("auto_pm.ui.workspace.doc_tab.QDesktopServices.openUrl") as mock_open:
            tab._on_document_double_clicked(doc_item)
            qapp.processEvents()
            mock_open.assert_called_once()
            # 验证传入的是 QUrl
            args = mock_open.call_args[0]
            assert isinstance(args[0], QUrl)
            # 验证路径指向实际文件
            assert "PM_SESSION_TEST-2026-001.md" in args[0].toLocalFile()
        tab.deleteLater()
        qapp.processEvents()

    def test_double_click_category_node_no_op(
        self,
        qapp: QApplication,
        template_service: TemplateService,
        project_dir: Path,
    ) -> None:
        """双击分类节点（非文档节点）不应触发打开"""
        tab = DocTab(template_service)
        tab.load_project("TEST-2026-001", str(project_dir))
        qapp.processEvents()

        cat = _find_category(tab, "PM_SESSION")
        assert cat is not None

        with patch("auto_pm.ui.workspace.doc_tab.QDesktopServices.openUrl") as mock_open:
            tab._on_document_double_clicked(cat)
            qapp.processEvents()
            mock_open.assert_not_called()
        tab.deleteLater()
        qapp.processEvents()


# ── 模板信息测试 ────────────────────────────────────────


class TestDocTabTemplateInfo:
    """DocTab 模板信息显示测试"""

    def test_template_info_displayed(
        self,
        qapp: QApplication,
        template_service: TemplateService,
        project_dir: Path,
    ) -> None:
        """加载项目后应显示模板信息（名称/版本/上次更新）"""
        tab = DocTab(template_service)
        tab.load_project("TEST-2026-001", str(project_dir))
        qapp.processEvents()

        # 模板名称应从 _src_path 提取
        assert "plc-standard" in tab._template_name_label.text()
        # 版本应显示 _commit
        assert "abc1234" in tab._template_version_label.text()
        # 上次更新应非空
        assert tab._template_updated_label.text() != "上次更新: —"
        tab.deleteLater()
        qapp.processEvents()

    def test_template_info_empty_without_copier(
        self,
        qapp: QApplication,
        template_service: TemplateService,
        empty_project_dir: Path,
    ) -> None:
        """无 .copier-answers.yml 时模板信息应显示占位符"""
        tab = DocTab(template_service)
        tab.load_project("EMPTY-2026-001", str(empty_project_dir))
        qapp.processEvents()

        assert tab._template_name_label.text() == "模板: —"
        assert tab._template_version_label.text() == "版本: —"
        assert tab._template_updated_label.text() == "上次更新: —"
        tab.deleteLater()
        qapp.processEvents()


# ── 按钮测试 ────────────────────────────────────────────


class TestDocTabButtons:
    """DocTab 按钮测试"""

    def test_update_btn_exists(
        self,
        qapp: QApplication,
        template_service: TemplateService,
    ) -> None:
        """DocTab 应包含"模板更新"按钮"""
        tab = DocTab(template_service)
        qapp.processEvents()

        assert tab._update_btn.text() == "🔄 模板更新"
        tab.deleteLater()
        qapp.processEvents()

    def test_check_btn_exists(
        self,
        qapp: QApplication,
        template_service: TemplateService,
    ) -> None:
        """DocTab 应包含"检查更新"按钮"""
        tab = DocTab(template_service)
        qapp.processEvents()

        assert tab._check_btn.text() == "检查更新"
        tab.deleteLater()
        qapp.processEvents()

    def test_update_btn_calls_template_service(
        self,
        qapp: QApplication,
        template_service: TemplateService,
        project_dir: Path,
    ) -> None:
        """点击"模板更新"应调用 TemplateService.update_template"""
        tab = DocTab(template_service)
        tab.load_project("TEST-2026-001", str(project_dir))
        qapp.processEvents()

        with patch.object(template_service, "update_template") as mock_update:
            tab._on_update_template()
            qapp.processEvents()
            mock_update.assert_called_once_with(str(project_dir), overwrite=False)
        tab.deleteLater()
        qapp.processEvents()

    def test_check_btn_calls_dry_run(
        self,
        qapp: QApplication,
        template_service: TemplateService,
        project_dir: Path,
    ) -> None:
        """点击"检查更新"应调用 update_template(dry_run=True)"""
        tab = DocTab(template_service)
        tab.load_project("TEST-2026-001", str(project_dir))
        qapp.processEvents()

        with patch.object(template_service, "update_template") as mock_update:
            mock_update.return_value = {"dry_run": True, "info": {}}
            tab._on_check_update()
            qapp.processEvents()
            mock_update.assert_called_once_with(str(project_dir), dry_run=True)
        tab.deleteLater()
        qapp.processEvents()


# ── 信号测试 ────────────────────────────────────────────


class TestDocTabSignal:
    """DocTab 信号测试"""

    def test_template_updated_signal(
        self,
        qapp: QApplication,
        template_service: TemplateService,
        project_dir: Path,
    ) -> None:
        """模板更新成功后应发射 template_updated 信号"""
        tab = DocTab(template_service)
        tab.load_project("TEST-2026-001", str(project_dir))
        qapp.processEvents()

        received: list[bool] = []
        tab.template_updated.connect(lambda: received.append(True))

        with patch.object(template_service, "update_template"):
            tab._on_update_template()
            qapp.processEvents()

        assert received == [True]
        tab.deleteLater()
        qapp.processEvents()

    def test_template_updated_not_emitted_on_error(
        self,
        qapp: QApplication,
        template_service: TemplateService,
        project_dir: Path,
    ) -> None:
        """模板更新失败时不应发射 template_updated 信号"""
        tab = DocTab(template_service)
        tab.load_project("TEST-2026-001", str(project_dir))
        qapp.processEvents()

        received: list[bool] = []
        tab.template_updated.connect(lambda: received.append(True))

        with patch.object(
            template_service,
            "update_template",
            side_effect=FileNotFoundError("缺少 .copier-answers.yml"),
        ):
            tab._on_update_template()
            qapp.processEvents()

        assert received == []
        tab.deleteLater()
        qapp.processEvents()


# ── 组件初始化测试 ──────────────────────────────────────


class TestDocTabComponents:
    """DocTab 组件初始化测试"""

    def test_components_initialized(
        self,
        qapp: QApplication,
        template_service: TemplateService,
    ) -> None:
        """DocTab 应正确初始化所有子组件"""
        tab = DocTab(template_service)
        qapp.processEvents()

        assert tab._update_btn is not None
        assert tab._check_btn is not None
        assert tab._doc_tree is not None
        assert tab._empty_hint is not None
        assert tab._template_name_label is not None
        assert tab._template_version_label is not None
        assert tab._template_updated_label is not None
        tab.deleteLater()
        qapp.processEvents()

    def test_doc_tree_header_hidden(
        self,
        qapp: QApplication,
        template_service: TemplateService,
    ) -> None:
        """文档树应隐藏表头"""
        tab = DocTab(template_service)
        qapp.processEvents()

        assert tab._doc_tree.isHeaderHidden() is True
        tab.deleteLater()
        qapp.processEvents()
