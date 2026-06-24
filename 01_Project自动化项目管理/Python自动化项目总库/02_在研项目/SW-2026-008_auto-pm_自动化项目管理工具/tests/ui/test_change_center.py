"""ChangeCenterView / ChangeListPanel / ChangeDetailPanel 单元测试

测试内容：
- ChangeListPanel: 加载变更单列表、状态 Tab 筛选、点击发射 change_selected 信号
- ChangeDetailPanel: 加载详情、clear() 清空、流转按钮渲染
- ChangeCenterView: 左右联动、状态流转后刷新

使用真实 ChangeService + 临时工作空间（不 mock），遵循项目现有 qapp fixture 模式。
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

# 必须在导入 PySide6 前设置离屏渲染，避免无显示环境报错
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from auto_pm.change.change_service import ChangeService  # noqa: E402
from auto_pm.core.project_service import ProjectService  # noqa: E402
from auto_pm.ui.change_center import (  # noqa: E402
    ChangeCenterView,
    ChangeDetailPanel,
    ChangeListPanel,
)

# ── fixtures ─────────────────────────────────────────────


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """提供全局 QApplication 实例（session 级复用）"""
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def change_workspace(tmp_path: Path) -> Path:
    """临时工作空间，含一个可被 ProjectService/ChangeService 识别的项目

    项目目录命名遵循 {project_id}_{name} 约定：
    - ProjectService 通过 .copier-answers.yml 标志文件识别
    - ChangeService 通过 {project_id}_ 前缀匹配定位
    """
    project_id = "TEST-2026-001"
    project_dir = tmp_path / f"{project_id}_测试项目"
    project_dir.mkdir()
    (project_dir / ".copier-answers.yml").write_text(
        "project_id: TEST-2026-001\n"
        "project_name: 测试项目\n"
        "version: V1.0.0\n"
        "_src_path: templates/python-tool\n"
        "business_line: SW\n",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def change_service(change_workspace: Path) -> ChangeService:
    """真实 ChangeService（指向临时工作空间）"""
    return ChangeService(str(change_workspace))


@pytest.fixture
def project_service(change_workspace: Path) -> ProjectService:
    """真实 ProjectService（指向临时工作空间）"""
    return ProjectService(str(change_workspace))


def _create_change(
    cs: ChangeService,
    project_id: str = "TEST-2026-001",
    domain: str = "PLC",
    nature: str = "DEF",
    background: str = "测试变更背景",
    necessity: str = "测试变更必要性",
) -> str:
    """创建一个变更单并返回编号"""
    cr = cs.create_change_request(
        project_id=project_id,
        domain=domain,
        business_nature=nature,
        impact_scope=["LOCAL"],
        applicant="fubai",
        background=background,
        necessity=necessity,
    )
    return cr.change_number


# ── ChangeListPanel 测试 ─────────────────────────────────


class TestChangeListPanel:
    """ChangeListPanel 测试"""

    def test_load_change_list(
        self, qapp: QApplication, change_service: ChangeService
    ) -> None:
        """加载变更单列表应显示所有变更单"""
        _create_change(change_service, background="列表测试背景1")
        _create_change(change_service, domain="DOCU", background="列表测试背景2")

        panel = ChangeListPanel(change_service)
        panel.refresh()
        qapp.processEvents()

        # 列表应有 2 个变更单
        assert panel._list_widget.count() == 2
        # 空状态提示应隐藏
        assert panel._empty_hint.isVisibleTo(panel) is False
        panel.deleteLater()
        qapp.processEvents()

    def test_empty_list_shows_hint(
        self, qapp: QApplication, change_service: ChangeService
    ) -> None:
        """无变更单时应显示空状态提示"""
        panel = ChangeListPanel(change_service)
        panel.refresh()
        qapp.processEvents()

        assert panel._list_widget.count() == 0
        assert panel._empty_hint.isVisibleTo(panel) is True
        panel.deleteLater()
        qapp.processEvents()

    def test_status_tab_filter(
        self, qapp: QApplication, change_service: ChangeService
    ) -> None:
        """状态 Tab 筛选应只显示对应状态的变更单"""
        # 创建 2 个 draft 变更单
        num1 = _create_change(change_service, background="筛选测试1")
        num2 = _create_change(change_service, background="筛选测试2")
        # 将 num1 流转到 submitted
        change_service.transition_status(num1, "submitted", approver="fubai")

        panel = ChangeListPanel(change_service)
        panel.refresh()
        qapp.processEvents()

        # 全部：2 条
        assert panel._list_widget.count() == 2

        # 草稿 Tab：1 条（num2）
        panel.set_status_filter("draft")
        qapp.processEvents()
        assert panel._list_widget.count() == 1
        first_item = panel._list_widget.item(0)
        assert first_item.data(0x0100) == num2  # Qt.ItemDataRole.UserRole = 0x0100

        # 待审批 Tab：1 条（num1）
        panel.set_status_filter("submitted")
        qapp.processEvents()
        assert panel._list_widget.count() == 1
        first_item = panel._list_widget.item(0)
        assert first_item.data(0x0100) == num1

        # 全部 Tab：2 条
        panel.set_status_filter(None)
        qapp.processEvents()
        assert panel._list_widget.count() == 2
        panel.deleteLater()
        qapp.processEvents()

    def test_status_tab_checked_state(
        self, qapp: QApplication, change_service: ChangeService
    ) -> None:
        """切换状态 Tab 时对应按钮应处于选中态"""
        panel = ChangeListPanel(change_service)
        qapp.processEvents()

        # 默认"全部"选中
        assert panel._status_tabs["all"].isChecked() is True

        # 切换到"草稿"
        panel.set_status_filter("draft")
        qapp.processEvents()
        assert panel._status_tabs["draft"].isChecked() is True
        assert panel._status_tabs["all"].isChecked() is False

        # 切换回"全部"
        panel.set_status_filter(None)
        qapp.processEvents()
        assert panel._status_tabs["all"].isChecked() is True
        assert panel._status_tabs["draft"].isChecked() is False
        panel.deleteLater()
        qapp.processEvents()

    def test_change_selected_signal(
        self, qapp: QApplication, change_service: ChangeService
    ) -> None:
        """点击变更单列表项应发射 change_selected(change_number) 信号"""
        num = _create_change(change_service, background="信号测试背景")

        panel = ChangeListPanel(change_service)
        panel.refresh()
        qapp.processEvents()

        received: list[str] = []
        panel.change_selected.connect(received.append)

        # 模拟点击第一项
        first_item = panel._list_widget.item(0)
        panel._on_item_clicked(first_item)
        qapp.processEvents()

        assert received == [num]
        panel.deleteLater()
        qapp.processEvents()

    def test_domain_filter(
        self, qapp: QApplication, change_service: ChangeService
    ) -> None:
        """领域筛选应只显示对应领域的变更单"""
        _create_change(change_service, domain="PLC", background="PLC领域")
        _create_change(change_service, domain="DOCU", background="DOCU领域")

        panel = ChangeListPanel(change_service)
        panel.refresh()
        qapp.processEvents()
        assert panel._list_widget.count() == 2

        # 筛选 PLC 领域
        panel.set_domain_filter("PLC")
        qapp.processEvents()
        assert panel._list_widget.count() == 1

        # 清除筛选
        panel.set_domain_filter(None)
        qapp.processEvents()
        assert panel._list_widget.count() == 2
        panel.deleteLater()
        qapp.processEvents()


# ── ChangeDetailPanel 测试 ───────────────────────────────


class TestChangeDetailPanel:
    """ChangeDetailPanel 测试"""

    def test_load_change_detail(
        self, qapp: QApplication, change_service: ChangeService
    ) -> None:
        """加载变更单详情应显示编号、状态、基本信息、背景、必要性"""
        num = _create_change(
            change_service,
            background="详情测试背景全文",
            necessity="详情测试必要性全文",
        )

        panel = ChangeDetailPanel(change_service)
        qapp.processEvents()

        # 初始为空状态
        assert panel._current_change is None
        assert panel._empty_hint.isVisibleTo(panel) is True

        # 加载详情
        panel.load_change(num)
        qapp.processEvents()

        assert panel._current_change is not None
        assert panel._current_change.change_number == num
        # 空状态应隐藏
        assert panel._empty_hint.isVisibleTo(panel) is False
        panel.deleteLater()
        qapp.processEvents()

    def test_clear(self, qapp: QApplication, change_service: ChangeService) -> None:
        """clear() 应清空详情显示并回到空状态"""
        num = _create_change(change_service, background="清空测试背景")

        panel = ChangeDetailPanel(change_service)
        panel.load_change(num)
        qapp.processEvents()
        assert panel._current_change is not None
        assert panel._empty_hint.isVisibleTo(panel) is False

        # 清空
        panel.clear()
        qapp.processEvents()
        assert panel._current_change is None
        assert panel._empty_hint.isVisibleTo(panel) is True
        panel.deleteLater()
        qapp.processEvents()

    def test_load_nonexistent_change(
        self, qapp: QApplication, change_service: ChangeService
    ) -> None:
        """加载不存在的变更单应回到空状态"""
        panel = ChangeDetailPanel(change_service)
        qapp.processEvents()

        panel.load_change("CHG-XXX-9999-999")
        qapp.processEvents()

        assert panel._current_change is None
        assert panel._empty_hint.isVisibleTo(panel) is True
        panel.deleteLater()
        qapp.processEvents()

    def test_transition_buttons_for_draft(
        self, qapp: QApplication, change_service: ChangeService
    ) -> None:
        """draft 状态应显示"提交审批"按钮"""
        num = _create_change(change_service, background="流转按钮测试")

        panel = ChangeDetailPanel(change_service)
        panel.load_change(num)
        qapp.processEvents()

        from PySide6.QtWidgets import QPushButton
        btns = panel.findChildren(QPushButton)
        btn_texts = [b.text() for b in btns]
        assert "提交审批" in btn_texts
        panel.deleteLater()
        qapp.processEvents()

    def test_transition_buttons_for_submitted(
        self, qapp: QApplication, change_service: ChangeService
    ) -> None:
        """submitted 状态应显示"开始审核"按钮（实际 STATUS_FLOW 需先经 under_review）"""
        num = _create_change(change_service, background="submitted状态测试")
        change_service.transition_status(num, "submitted", approver="fubai")

        panel = ChangeDetailPanel(change_service)
        panel.load_change(num)
        qapp.processEvents()

        from PySide6.QtWidgets import QPushButton
        btns = panel.findChildren(QPushButton)
        btn_texts = [b.text() for b in btns]
        assert "开始审核" in btn_texts
        panel.deleteLater()
        qapp.processEvents()

    def test_transition_buttons_for_under_review(
        self, qapp: QApplication, change_service: ChangeService
    ) -> None:
        """under_review 状态应显示"审批通过"和"驳回"按钮"""
        num = _create_change(change_service, background="under_review状态测试")
        change_service.transition_status(num, "submitted", approver="fubai")
        change_service.transition_status(num, "under_review", approver="fubai")

        panel = ChangeDetailPanel(change_service)
        panel.load_change(num)
        qapp.processEvents()

        from PySide6.QtWidgets import QPushButton
        btns = panel.findChildren(QPushButton)
        btn_texts = [b.text() for b in btns]
        assert "审批通过" in btn_texts
        assert "驳回" in btn_texts
        panel.deleteLater()
        qapp.processEvents()

    def test_transition_buttons_for_closed(
        self, qapp: QApplication, change_service: ChangeService
    ) -> None:
        """closed 终态不应显示流转按钮"""
        num = _create_change(change_service, background="终态测试")

        # 手动构造 closed 状态的 ChangeRequest（避免长链路流转的门禁复杂性）
        from auto_pm.models import ChangeRequest
        panel = ChangeDetailPanel(change_service)
        panel._current_change = ChangeRequest(
            change_number=num, project_id="TEST-2026-001", status="closed"
        )
        panel._clear_content()
        panel._render_detail(panel._current_change)
        qapp.processEvents()

        from PySide6.QtWidgets import QPushButton
        # 只检查流转按钮（M3-1 新增的 editBtn 不属于流转按钮）
        transition_btns = [
            btn
            for btn in panel.findChildren(QPushButton)
            if btn.objectName() in ("transitionBtn", "rejectBtn")
        ]
        assert len(transition_btns) == 0  # closed 无流转按钮
        panel.deleteLater()
        qapp.processEvents()


# ── ChangeCenterView 测试 ────────────────────────────────


class TestChangeCenterView:
    """ChangeCenterView 测试"""

    def test_left_right_linkage(
        self,
        qapp: QApplication,
        change_service: ChangeService,
        project_service: ProjectService,
    ) -> None:
        """左侧选中变更单 → 右侧加载详情"""
        num = _create_change(change_service, background="联动测试背景")

        view = ChangeCenterView(change_service, project_service)
        view.refresh()
        qapp.processEvents()

        # 左侧列表应有 1 条
        assert view._list_panel._list_widget.count() == 1

        # 模拟点击左侧第一项
        first_item = view._list_panel._list_widget.item(0)
        view._list_panel._on_item_clicked(first_item)
        qapp.processEvents()

        # 右侧应加载该变更单详情
        assert view._detail_panel._current_change is not None
        assert view._detail_panel._current_change.change_number == num
        view.deleteLater()
        qapp.processEvents()

    def test_refresh_after_transition(
        self,
        qapp: QApplication,
        change_service: ChangeService,
        project_service: ProjectService,
    ) -> None:
        """状态流转后应刷新列表并发射 change_updated 信号"""
        num = _create_change(change_service, background="流转刷新测试")

        view = ChangeCenterView(change_service, project_service)
        view.refresh()
        qapp.processEvents()

        # 模拟点击左侧第一项，加载详情
        first_item = view._list_panel._list_widget.item(0)
        view._list_panel._on_item_clicked(first_item)
        qapp.processEvents()
        assert view._detail_panel._current_change is not None
        assert view._detail_panel._current_change.status == "draft"

        # 监听 change_updated 信号
        received: list[bool] = []
        view.change_updated.connect(lambda: received.append(True))

        # 执行真实状态流转（draft → submitted），然后模拟详情面板的流转完成回调
        change_service.transition_status(num, "submitted", approver="fubai")
        view._detail_panel._on_transition_done(num)
        qapp.processEvents()

        # 应发射 change_updated 信号
        assert received == [True]

        # 列表应刷新（全部 Tab 下应存在 1 条）
        view._list_panel.set_status_filter(None)
        qapp.processEvents()
        assert view._list_panel._list_widget.count() == 1

        # 详情应重新加载，状态变为 submitted
        assert view._detail_panel._current_change is not None
        assert view._detail_panel._current_change.status == "submitted"
        view.deleteLater()
        qapp.processEvents()

    def test_refresh_loads_list(
        self,
        qapp: QApplication,
        change_service: ChangeService,
        project_service: ProjectService,
    ) -> None:
        """refresh() 应加载变更单列表"""
        _create_change(change_service, background="刷新测试1")
        _create_change(change_service, background="刷新测试2")

        view = ChangeCenterView(change_service, project_service)
        qapp.processEvents()

        # 初始列表为空（未 refresh）
        assert view._list_panel._list_widget.count() == 0

        # refresh 后应有 2 条
        view.refresh()
        qapp.processEvents()
        assert view._list_panel._list_widget.count() == 2
        view.deleteLater()
        qapp.processEvents()

    def test_change_updated_on_create(
        self,
        qapp: QApplication,
        change_service: ChangeService,
        project_service: ProjectService,
    ) -> None:
        """创建变更单后应刷新列表并发射 change_updated 信号"""
        view = ChangeCenterView(change_service, project_service)
        view.refresh()
        qapp.processEvents()
        assert view._list_panel._list_widget.count() == 0

        received: list[bool] = []
        view.change_updated.connect(lambda: received.append(True))

        # 模拟创建变更单回调
        view._on_change_created("TEST-2026-001")
        qapp.processEvents()

        assert received == [True]
        # 列表应刷新（但工作空间无变更单文件，仍为 0）
        # 此处主要验证信号发射和 refresh 被调用
        view.deleteLater()
        qapp.processEvents()

    def test_components_initialized(
        self,
        qapp: QApplication,
        change_service: ChangeService,
        project_service: ProjectService,
    ) -> None:
        """ChangeCenterView 应正确初始化子组件"""
        view = ChangeCenterView(change_service, project_service)
        qapp.processEvents()

        assert view._list_panel is not None
        assert view._detail_panel is not None
        assert view._splitter is not None
        assert view._create_btn is not None
        assert view._create_btn.text() == "创建变更单"

        # splitter 应包含 2 个面板（左列表 + 右详情）
        assert view._splitter.count() == 2
        assert view._splitter.widget(0) is view._list_panel
        assert view._splitter.widget(1) is view._detail_panel
        view.deleteLater()
        qapp.processEvents()
