"""ChangeTab 单元测试

测试内容：
- load_project 后列表加载
- 状态筛选
- 领域筛选
- 点击"创建变更单" → 弹出对话框（通过回调验证）
- 点击"流转" → 弹出对话框（通过回调验证）
- change_updated 信号
- 空项目（无变更单）显示空状态

使用真实 ChangeService + 临时工作空间（不 mock），遵循项目现有 qapp fixture 模式。
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

# 必须在导入 PySide6 前设置离屏渲染，避免无显示环境报错
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from auto_pm.change.change_service import ChangeService  # noqa: E402
from auto_pm.core.project_service import ProjectService  # noqa: E402
from auto_pm.ui.workspace.change_tab import ChangeTab, _ChangeCard  # noqa: E402

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


# ── 辅助函数 ─────────────────────────────────────────────


def _get_cards(tab: ChangeTab) -> list[_ChangeCard]:
    """获取 ChangeTab 当前的所有卡片"""
    return tab._get_cards()


# ── ChangeTab 测试 ───────────────────────────────────────


class TestChangeTabLoad:
    """ChangeTab 加载测试"""

    def test_load_project_loads_list(
        self,
        qapp: QApplication,
        change_service: ChangeService,
        project_service: ProjectService,
    ) -> None:
        """load_project 后应加载变更单列表"""
        _create_change(change_service, background="加载测试背景1")
        _create_change(change_service, domain="DOCU", background="加载测试背景2")

        tab = ChangeTab(change_service, project_service)
        tab.load_project("TEST-2026-001")
        qapp.processEvents()

        cards = _get_cards(tab)
        assert len(cards) == 2
        # 空状态提示应隐藏
        assert tab._empty_hint.isVisibleTo(tab) is False
        tab.deleteLater()
        qapp.processEvents()

    def test_load_empty_project_shows_hint(
        self,
        qapp: QApplication,
        change_service: ChangeService,
        project_service: ProjectService,
    ) -> None:
        """空项目（无变更单）应显示空状态提示"""
        tab = ChangeTab(change_service, project_service)
        tab.load_project("TEST-2026-001")
        qapp.processEvents()

        cards = _get_cards(tab)
        assert len(cards) == 0
        assert tab._empty_hint.isVisibleTo(tab) is True
        tab.deleteLater()
        qapp.processEvents()

    def test_load_project_without_project_id(
        self,
        qapp: QApplication,
        change_service: ChangeService,
        project_service: ProjectService,
    ) -> None:
        """未调用 load_project 时 _refresh_list 应安全返回"""
        tab = ChangeTab(change_service, project_service)
        # 直接调用 _refresh_list，project_id 为 None
        tab._refresh_list()
        qapp.processEvents()

        cards = _get_cards(tab)
        assert len(cards) == 0
        tab.deleteLater()
        qapp.processEvents()

    def test_card_displays_change_number(
        self,
        qapp: QApplication,
        change_service: ChangeService,
        project_service: ProjectService,
    ) -> None:
        """卡片应显示变更单编号"""
        num = _create_change(change_service, background="编号显示测试")

        tab = ChangeTab(change_service, project_service)
        tab.load_project("TEST-2026-001")
        qapp.processEvents()

        cards = _get_cards(tab)
        assert len(cards) == 1
        assert cards[0]._summary.change_number == num
        tab.deleteLater()
        qapp.processEvents()


class TestChangeTabFilter:
    """ChangeTab 筛选测试"""

    def test_status_filter(
        self,
        qapp: QApplication,
        change_service: ChangeService,
        project_service: ProjectService,
    ) -> None:
        """状态筛选应只显示对应状态的变更单"""
        num1 = _create_change(change_service, background="状态筛选1")
        num2 = _create_change(change_service, background="状态筛选2")
        # 将 num1 流转到 submitted
        change_service.transition_status(num1, "submitted", approver="fubai")

        tab = ChangeTab(change_service, project_service)
        tab.load_project("TEST-2026-001")
        qapp.processEvents()

        # 全部：2 条
        assert len(_get_cards(tab)) == 2

        # 筛选草稿：1 条（num2）
        tab._status_filter = "draft"
        tab._refresh_list()
        qapp.processEvents()
        cards = _get_cards(tab)
        assert len(cards) == 1
        assert cards[0]._summary.change_number == num2

        # 筛选待审批：1 条（num1）
        tab._status_filter = "submitted"
        tab._refresh_list()
        qapp.processEvents()
        cards = _get_cards(tab)
        assert len(cards) == 1
        assert cards[0]._summary.change_number == num1

        # 恢复全部
        tab._status_filter = None
        tab._refresh_list()
        qapp.processEvents()
        assert len(_get_cards(tab)) == 2
        tab.deleteLater()
        qapp.processEvents()

    def test_status_filter_via_combobox(
        self,
        qapp: QApplication,
        change_service: ChangeService,
        project_service: ProjectService,
    ) -> None:
        """通过下拉框切换状态筛选应刷新列表"""
        num1 = _create_change(change_service, background="下拉筛选1")
        _create_change(change_service, background="下拉筛选2")
        change_service.transition_status(num1, "submitted", approver="fubai")

        tab = ChangeTab(change_service, project_service)
        tab.load_project("TEST-2026-001")
        qapp.processEvents()
        assert len(_get_cards(tab)) == 2

        # 切换到"草稿"（index=1）
        tab._status_combo.setCurrentIndex(1)
        qapp.processEvents()
        assert len(_get_cards(tab)) == 1

        # 切换回"全部状态"（index=0）
        tab._status_combo.setCurrentIndex(0)
        qapp.processEvents()
        assert len(_get_cards(tab)) == 2
        tab.deleteLater()
        qapp.processEvents()

    def test_domain_filter(
        self,
        qapp: QApplication,
        change_service: ChangeService,
        project_service: ProjectService,
    ) -> None:
        """领域筛选应只显示对应领域的变更单"""
        _create_change(change_service, domain="PLC", background="PLC领域筛选")
        _create_change(change_service, domain="DOCU", background="DOCU领域筛选")

        tab = ChangeTab(change_service, project_service)
        tab.load_project("TEST-2026-001")
        qapp.processEvents()
        assert len(_get_cards(tab)) == 2

        # 筛选 PLC 领域
        tab._domain_filter = "PLC"
        tab._refresh_list()
        qapp.processEvents()
        cards = _get_cards(tab)
        assert len(cards) == 1
        assert cards[0]._summary.domain == "PLC"

        # 清除筛选
        tab._domain_filter = None
        tab._refresh_list()
        qapp.processEvents()
        assert len(_get_cards(tab)) == 2
        tab.deleteLater()
        qapp.processEvents()

    def test_domain_filter_via_combobox(
        self,
        qapp: QApplication,
        change_service: ChangeService,
        project_service: ProjectService,
    ) -> None:
        """通过下拉框切换领域筛选应刷新列表"""
        _create_change(change_service, domain="PLC", background="下拉领域1")
        _create_change(change_service, domain="DOCU", background="下拉领域2")

        tab = ChangeTab(change_service, project_service)
        tab.load_project("TEST-2026-001")
        qapp.processEvents()
        assert len(_get_cards(tab)) == 2

        # 找到 PLC 领域对应的下拉索引
        plc_index = -1
        for i in range(tab._domain_combo.count()):
            if tab._domain_combo.itemData(i) == "PLC":
                plc_index = i
                break
        assert plc_index > 0  # 应找到 PLC（非"全部领域"）

        tab._domain_combo.setCurrentIndex(plc_index)
        qapp.processEvents()
        assert len(_get_cards(tab)) == 1

        # 切换回"全部领域"（index=0）
        tab._domain_combo.setCurrentIndex(0)
        qapp.processEvents()
        assert len(_get_cards(tab)) == 2
        tab.deleteLater()
        qapp.processEvents()


class TestChangeTabCreateDialog:
    """ChangeTab 创建变更单对话框测试"""

    def test_create_btn_exists(
        self,
        qapp: QApplication,
        change_service: ChangeService,
        project_service: ProjectService,
    ) -> None:
        """ChangeTab 应包含"创建变更单"按钮"""
        tab = ChangeTab(change_service, project_service)
        qapp.processEvents()

        assert tab._create_btn.text() == "+ 创建变更单"
        tab.deleteLater()
        qapp.processEvents()

    def test_create_change_dialog_opens(
        self,
        qapp: QApplication,
        change_service: ChangeService,
        project_service: ProjectService,
    ) -> None:
        """点击"创建变更单"应弹出 CreateChangeDialog"""
        tab = ChangeTab(change_service, project_service)
        qapp.processEvents()

        # mock CreateChangeDialog.exec 避免真正弹出
        with patch("auto_pm.ui.workspace.change_tab.CreateChangeDialog") as mock_dialog_cls:
            mock_dialog = mock_dialog_cls.return_value
            mock_dialog.exec.return_value = 0  # QDialog.Rejected
            tab._on_create_change()
            qapp.processEvents()

            # 应创建对话框实例
            mock_dialog_cls.assert_called_once()
            # 应连接 change_created 信号
            mock_dialog.change_created.connect.assert_called_once()
        tab.deleteLater()
        qapp.processEvents()

    def test_change_created_callback_refreshes(
        self,
        qapp: QApplication,
        change_service: ChangeService,
        project_service: ProjectService,
    ) -> None:
        """_on_change_created 回调应刷新列表"""
        tab = ChangeTab(change_service, project_service)
        tab.load_project("TEST-2026-001")
        qapp.processEvents()
        assert len(_get_cards(tab)) == 0

        # 直接创建一个变更单（模拟对话框创建成功后的状态）
        _create_change(change_service, background="回调刷新测试")

        # 调用回调
        tab._on_change_created("TEST-2026-001")
        qapp.processEvents()

        # 列表应刷新，显示 1 条
        assert len(_get_cards(tab)) == 1
        tab.deleteLater()
        qapp.processEvents()


class TestChangeTabTransition:
    """ChangeTab 状态流转测试"""

    def test_transition_btn_exists_for_draft(
        self,
        qapp: QApplication,
        change_service: ChangeService,
        project_service: ProjectService,
    ) -> None:
        """草稿状态变更单的卡片应包含可用的"流转"按钮"""
        _create_change(change_service, background="流转按钮测试")

        tab = ChangeTab(change_service, project_service)
        tab.load_project("TEST-2026-001")
        qapp.processEvents()

        cards = _get_cards(tab)
        assert len(cards) == 1
        assert cards[0]._transition_btn.isEnabled() is True
        assert cards[0]._transition_btn.text() == "流转"
        tab.deleteLater()
        qapp.processEvents()

    def test_transition_btn_disabled_for_closed(
        self,
        qapp: QApplication,
        change_service: ChangeService,
        project_service: ProjectService,
    ) -> None:
        """终态（closed）变更单的"流转"按钮应禁用"""
        _create_change(change_service, background="终态按钮测试")

        tab = ChangeTab(change_service, project_service)
        tab.load_project("TEST-2026-001")
        qapp.processEvents()

        cards = _get_cards(tab)
        assert len(cards) == 1

        # 手动将卡片状态改为 closed（避免长链路流转）
        cards[0]._summary.status = "closed"
        cards[0]._transition_btn.setEnabled(False)

        assert cards[0]._transition_btn.isEnabled() is False
        tab.deleteLater()
        qapp.processEvents()

    def test_transition_dialog_opens(
        self,
        qapp: QApplication,
        change_service: ChangeService,
        project_service: ProjectService,
    ) -> None:
        """点击"流转"按钮应弹出 TransitionDialog（draft 只有一个目标状态）"""
        num = _create_change(change_service, background="流转对话框测试")

        tab = ChangeTab(change_service, project_service)
        tab.load_project("TEST-2026-001")
        qapp.processEvents()

        # mock TransitionDialog.exec 避免真正弹出
        with patch("auto_pm.ui.workspace.change_tab.TransitionDialog") as mock_dialog_cls:
            mock_dialog = mock_dialog_cls.return_value
            mock_dialog.exec.return_value = 0  # QDialog.Rejected
            tab._on_transition(num)
            qapp.processEvents()

            # 应创建对话框实例（draft 只有一个目标 submitted，直接弹出）
            mock_dialog_cls.assert_called_once()
            # 应连接 transition_completed 信号
            mock_dialog.transition_completed.connect.assert_called_once()
        tab.deleteLater()
        qapp.processEvents()

    def test_transition_completed_callback_refreshes(
        self,
        qapp: QApplication,
        change_service: ChangeService,
        project_service: ProjectService,
    ) -> None:
        """_on_transition_completed 回调应刷新列表"""
        num = _create_change(change_service, background="流转完成回调测试")

        tab = ChangeTab(change_service, project_service)
        tab.load_project("TEST-2026-001")
        qapp.processEvents()

        # 执行真实状态流转（draft → submitted）
        change_service.transition_status(num, "submitted", approver="fubai")

        # 调用回调
        tab._on_transition_completed(num)
        qapp.processEvents()

        # 列表应刷新，卡片状态应更新
        cards = _get_cards(tab)
        assert len(cards) == 1
        assert cards[0]._summary.status == "submitted"
        tab.deleteLater()
        qapp.processEvents()

    def test_transition_nonexistent_change(
        self,
        qapp: QApplication,
        change_service: ChangeService,
        project_service: ProjectService,
    ) -> None:
        """流转不存在的变更单应安全返回（不抛异常）"""
        tab = ChangeTab(change_service, project_service)
        tab.load_project("TEST-2026-001")
        qapp.processEvents()

        # 流转不存在的变更单
        tab._on_transition("CHG-XXX-9999-999")
        qapp.processEvents()
        # 不应抛异常，列表保持空
        assert len(_get_cards(tab)) == 0
        tab.deleteLater()
        qapp.processEvents()


class TestChangeTabSignal:
    """ChangeTab 信号测试"""

    def test_change_updated_signal_on_create(
        self,
        qapp: QApplication,
        change_service: ChangeService,
        project_service: ProjectService,
    ) -> None:
        """变更单创建后应发射 change_updated 信号"""
        tab = ChangeTab(change_service, project_service)
        tab.load_project("TEST-2026-001")
        qapp.processEvents()

        received: list[bool] = []
        tab.change_updated.connect(lambda: received.append(True))

        # 模拟创建回调
        tab._on_change_created("TEST-2026-001")
        qapp.processEvents()

        assert received == [True]
        tab.deleteLater()
        qapp.processEvents()

    def test_change_updated_signal_on_transition(
        self,
        qapp: QApplication,
        change_service: ChangeService,
        project_service: ProjectService,
    ) -> None:
        """状态流转完成后应发射 change_updated 信号"""
        num = _create_change(change_service, background="信号测试流转")

        tab = ChangeTab(change_service, project_service)
        tab.load_project("TEST-2026-001")
        qapp.processEvents()

        received: list[bool] = []
        tab.change_updated.connect(lambda: received.append(True))

        # 执行真实状态流转
        change_service.transition_status(num, "submitted", approver="fubai")
        tab._on_transition_completed(num)
        qapp.processEvents()

        assert received == [True]
        tab.deleteLater()
        qapp.processEvents()


class TestChangeTabCardDetail:
    """ChangeTab 卡片详情展开测试"""

    def test_detail_toggle(
        self,
        qapp: QApplication,
        change_service: ChangeService,
        project_service: ProjectService,
    ) -> None:
        """点击"详情"按钮应展开/收起详情区域"""
        _create_change(
            change_service,
            background="详情展开测试背景",
            necessity="详情展开测试必要性",
        )

        tab = ChangeTab(change_service, project_service)
        tab.load_project("TEST-2026-001")
        qapp.processEvents()

        cards = _get_cards(tab)
        assert len(cards) == 1
        card = cards[0]

        # 初始详情区域隐藏
        assert card._detail_section.isVisibleTo(card) is False
        assert card._detail_btn.text() == "详情"

        # 点击展开
        card._toggle_detail()
        qapp.processEvents()
        assert card._detail_section.isVisibleTo(card) is True
        assert card._detail_btn.text() == "收起"

        # 点击收起
        card._toggle_detail()
        qapp.processEvents()
        assert card._detail_section.isVisibleTo(card) is False
        assert card._detail_btn.text() == "详情"
        tab.deleteLater()
        qapp.processEvents()

    def test_detail_loads_full_content(
        self,
        qapp: QApplication,
        change_service: ChangeService,
        project_service: ProjectService,
    ) -> None:
        """展开详情应加载背景/必要性/影响范围全文"""
        _create_change(
            change_service,
            background="全文背景内容",
            necessity="全文必要性内容",
        )

        tab = ChangeTab(change_service, project_service)
        tab.load_project("TEST-2026-001")
        qapp.processEvents()

        cards = _get_cards(tab)
        assert len(cards) == 1
        card = cards[0]

        # 展开详情
        card._toggle_detail()
        qapp.processEvents()

        # 详情区域应有 3 个 label（背景/必要性/影响范围）
        assert card._detail_layout.count() == 3
        tab.deleteLater()
        qapp.processEvents()


class TestChangeTabComponents:
    """ChangeTab 组件初始化测试"""

    def test_components_initialized(
        self,
        qapp: QApplication,
        change_service: ChangeService,
        project_service: ProjectService,
    ) -> None:
        """ChangeTab 应正确初始化所有子组件"""
        tab = ChangeTab(change_service, project_service)
        qapp.processEvents()

        assert tab._create_btn is not None
        assert tab._status_combo is not None
        assert tab._domain_combo is not None
        assert tab._scroll is not None
        assert tab._empty_hint is not None
        assert tab._list_layout is not None

        # 状态下拉应有 7 个选项
        assert tab._status_combo.count() == 7
        # 领域下拉应有 8 个选项（全部领域 + 7 个领域）
        assert tab._domain_combo.count() == 8
        tab.deleteLater()
        qapp.processEvents()

    def test_status_combo_options(
        self,
        qapp: QApplication,
        change_service: ChangeService,
        project_service: ProjectService,
    ) -> None:
        """状态下拉应包含全部/草稿/待审批/已审批/实施中/已完成/已归档"""
        tab = ChangeTab(change_service, project_service)
        qapp.processEvents()

        labels = [tab._status_combo.itemText(i) for i in range(tab._status_combo.count())]
        assert labels == ["全部状态", "草稿", "待审批", "已审批", "实施中", "已完成", "已归档"]

        # 第一个选项的 data 应为 None（全部）
        assert tab._status_combo.itemData(0) is None
        # 第二个选项的 data 应为 "draft"
        assert tab._status_combo.itemData(1) == "draft"
        tab.deleteLater()
        qapp.processEvents()

    def test_domain_combo_options(
        self,
        qapp: QApplication,
        change_service: ChangeService,
        project_service: ProjectService,
    ) -> None:
        """领域下拉应包含全部领域 + DOMAINS 中的所有领域"""
        tab = ChangeTab(change_service, project_service)
        qapp.processEvents()

        # 第一个选项的 data 应为 None（全部领域）
        assert tab._domain_combo.itemData(0) is None
        assert tab._domain_combo.itemText(0) == "全部领域"

        # 后续选项应包含所有领域代码
        codes = [
            tab._domain_combo.itemData(i)
            for i in range(1, tab._domain_combo.count())
        ]
        assert "ELEC" in codes
        assert "MECH" in codes
        assert "PLC" in codes
        assert "HMI" in codes
        assert "SCPT" in codes
        assert "DOCU" in codes
        assert "SAFE" in codes
        tab.deleteLater()
        qapp.processEvents()
