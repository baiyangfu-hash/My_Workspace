"""CreateChangeDialog / TransitionDialog 单元测试

测试内容：
- CreateChangeDialog: 表单字段存在、必填校验、get_change_data、change_created 信号
- TransitionDialog: 显示信息、验证结论字段显隐、get_transition_data、transition_completed 信号

使用真实 ChangeService + 临时工作空间（不 mock），遵循项目现有 qapp fixture 模式。
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import pytest

# 必须在导入 PySide6 前设置离屏渲染，避免无显示环境报错
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QDialogButtonBox, QMessageBox  # noqa: E402

from auto_pm.change.change_service import ChangeService  # noqa: E402
from auto_pm.change.models import (  # noqa: E402
    BUSINESS_NATURES,
    DOMAINS,
    IMPACT_SCOPES,
    STATUS_LABELS,
    URGENCY_LEVELS,
)
from auto_pm.core.project_service import ProjectService  # noqa: E402
from auto_pm.ui.dialogs.create_change_dialog import (  # noqa: E402
    CreateChangeDialog,
    CreateChangeWizard,
)
from auto_pm.ui.dialogs.transition_dialog import TransitionDialog  # noqa: E402

# ── fixtures ─────────────────────────────────────────────


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


@pytest.fixture(autouse=True)
def _patch_message_boxes() -> Iterator[None]:
    """自动 patch QMessageBox 静态方法，避免模态对话框阻塞测试

    CreateChangeDialog._load_projects 在加载失败时会调用 QMessageBox.critical，
    TransitionDialog 也可能触发 warning/information，这些模态对话框在 offscreen
    模式下会阻塞事件循环导致测试超时。
    使用直接赋值（monkeypatch.setattr 对 PySide6 C++ 静态方法无效）。
    """
    orig_critical = QMessageBox.critical
    orig_warning = QMessageBox.warning
    orig_information = QMessageBox.information
    orig_question = QMessageBox.question
    QMessageBox.critical = staticmethod(lambda *a, **kw: None)  # type: ignore[assignment]
    QMessageBox.warning = staticmethod(lambda *a, **kw: None)  # type: ignore[assignment]
    QMessageBox.information = staticmethod(lambda *a, **kw: None)  # type: ignore[assignment]
    QMessageBox.question = staticmethod(  # type: ignore[method-assign]
        lambda *a, **kw: QMessageBox.StandardButton.Yes
    )
    yield
    QMessageBox.critical = orig_critical  # type: ignore[method-assign]
    QMessageBox.warning = orig_warning  # type: ignore[method-assign]
    QMessageBox.information = orig_information  # type: ignore[method-assign]
    QMessageBox.question = orig_question  # type: ignore[method-assign]


# ── CreateChangeDialog 测试 ──────────────────────────────


class TestCreateChangeDialog:
    """CreateChangeDialog 测试"""

    def test_form_fields_exist(self, qapp: QApplication, change_workspace: Path) -> None:
        """所有表单字段控件应存在，选项数对齐规范常量"""
        ps = ProjectService(str(change_workspace))
        cs = ChangeService(str(change_workspace))
        dlg = CreateChangeDialog(ps, cs)

        assert dlg._project_combo is not None
        assert dlg._domain_combo is not None
        assert dlg._nature_combo is not None
        assert dlg._scope_combo is not None
        assert dlg._applicant_edit is not None
        assert dlg._background_edit is not None
        assert dlg._necessity_edit is not None
        assert dlg._urgency_combo is not None
        assert dlg._planned_date_edit is not None

        # 选项数量对齐 CHG-040 规范常量
        assert dlg._domain_combo.count() == len(DOMAINS)
        assert dlg._nature_combo.count() == len(BUSINESS_NATURES)
        assert dlg._scope_combo.count() == len(IMPACT_SCOPES)
        assert dlg._urgency_combo.count() == len(URGENCY_LEVELS)

        # 申请人默认值
        assert dlg._applicant_edit.text() == "fubai"
        dlg.deleteLater()
        qapp.processEvents()

    def test_project_combo_loaded(self, qapp: QApplication, change_workspace: Path) -> None:
        """项目下拉应加载工作空间内的项目"""
        ps = ProjectService(str(change_workspace))
        cs = ChangeService(str(change_workspace))
        dlg = CreateChangeDialog(ps, cs)

        assert dlg._project_combo.count() >= 1
        assert dlg._project_combo.currentData() == "TEST-2026-001"
        dlg.deleteLater()
        qapp.processEvents()

    def test_required_validation_disables_create_button(
        self, qapp: QApplication, change_workspace: Path
    ) -> None:
        """必填字段（项目/申请人/背景）为空时创建按钮应禁用"""
        ps = ProjectService(str(change_workspace))
        cs = ChangeService(str(change_workspace))
        dlg = CreateChangeDialog(ps, cs)
        create_btn = dlg._button_box.button(QDialogButtonBox.StandardButton.Ok)

        # 默认：项目已选、申请人=fubai、背景为空 → 禁用
        assert create_btn.isEnabled() is False

        # 清空申请人 → 仍禁用
        dlg._applicant_edit.setText("")
        assert create_btn.isEnabled() is False

        # 填入申请人 + 背景 → 启用
        dlg._applicant_edit.setText("fubai")
        dlg._background_edit.setPlainText("测试背景")
        assert create_btn.isEnabled() is True

        # 再次清空背景 → 禁用
        dlg._background_edit.setPlainText("")
        assert create_btn.isEnabled() is False
        dlg.deleteLater()
        qapp.processEvents()

    def test_get_change_data(self, qapp: QApplication, change_workspace: Path) -> None:
        """get_change_data 应返回表单中各字段的当前值"""
        ps = ProjectService(str(change_workspace))
        cs = ChangeService(str(change_workspace))
        dlg = CreateChangeDialog(ps, cs)

        dlg._applicant_edit.setText("张三")
        dlg._background_edit.setPlainText("背景描述")
        dlg._necessity_edit.setPlainText("必要性描述")
        dlg._domain_combo.setCurrentIndex(dlg._domain_combo.findData("PLC"))
        dlg._nature_combo.setCurrentIndex(dlg._nature_combo.findData("DEF"))
        dlg._scope_combo.setCurrentIndex(dlg._scope_combo.findData("LOCAL"))
        dlg._urgency_combo.setCurrentIndex(dlg._urgency_combo.findData("urgent"))

        data = dlg.get_change_data()
        assert data["project_id"] == "TEST-2026-001"
        assert data["domain"] == "PLC"
        assert data["business_nature"] == "DEF"
        assert data["impact_scope"] == ["LOCAL"]
        assert data["applicant"] == "张三"
        assert data["background"] == "背景描述"
        assert data["necessity"] == "必要性描述"
        assert data["urgency"] == "urgent"
        assert data["planned_date"]  # 非空（默认今天）
        dlg.deleteLater()
        qapp.processEvents()

    def test_change_created_signal(
        self, qapp: QApplication, change_workspace: Path
    ) -> None:
        """创建成功后应发射 change_created(project_id) 信号（真实 ChangeService）"""
        ps = ProjectService(str(change_workspace))
        cs = ChangeService(str(change_workspace))
        dlg = CreateChangeDialog(ps, cs)
        dlg._background_edit.setPlainText("信号测试背景")

        received: list[str] = []
        dlg.change_created.connect(received.append)
        dlg._on_create()

        assert received == ["TEST-2026-001"]
        # 确认真实变更单已生成（列表非空）
        changes = cs.list_change_requests("TEST-2026-001")
        assert len(changes) >= 1
        assert changes[0].change_number.startswith("CHG-")
        dlg.deleteLater()
        qapp.processEvents()


# ── CreateChangeWizard 专项测试（M3-4 QWizard） ──────────


class TestCreateChangeWizard:
    """CreateChangeWizard QWizard 分步向导专项测试（M3-4）

    覆盖 QWizard 特有行为：3 页面结构、各页 isComplete 联动、
    ConfirmPage 汇总展示、validatePage 触发创建。
    兼容性测试由 TestCreateChangeDialog 覆盖（CreateChangeDialog 为别名）。
    """

    def test_wizard_has_three_pages(
        self, qapp: QApplication, change_workspace: Path
    ) -> None:
        """向导应包含 3 个页面，标题对齐设计"""
        ps = ProjectService(str(change_workspace))
        cs = ChangeService(str(change_workspace))
        wizard = CreateChangeWizard(ps, cs)

        page_ids = wizard.pageIds()
        assert len(page_ids) == 3
        titles = [wizard.page(pid).title() for pid in page_ids]
        assert titles == ["基本信息", "变更描述", "提交确认"]
        wizard.deleteLater()
        qapp.processEvents()

    def test_basic_page_complete_validation(
        self, qapp: QApplication, change_workspace: Path
    ) -> None:
        """Step 1 isComplete: 项目+申请人同时满足才为 True"""
        ps = ProjectService(str(change_workspace))
        cs = ChangeService(str(change_workspace))
        wizard = CreateChangeWizard(ps, cs)

        # 默认: 项目已选 + 申请人=fubai → True
        assert wizard._basic_page.isComplete() is True

        # 清空申请人 → False
        wizard._applicant_edit.setText("")
        assert wizard._basic_page.isComplete() is False

        # 填回申请人 → True
        wizard._applicant_edit.setText("fubai")
        assert wizard._basic_page.isComplete() is True
        wizard.deleteLater()
        qapp.processEvents()

    def test_desc_page_complete_validation(
        self, qapp: QApplication, change_workspace: Path
    ) -> None:
        """Step 2 isComplete: 背景非空才为 True"""
        ps = ProjectService(str(change_workspace))
        cs = ChangeService(str(change_workspace))
        wizard = CreateChangeWizard(ps, cs)

        # 背景为空 → False
        assert wizard._desc_page.isComplete() is False

        # 填入背景 → True
        wizard._background_edit.setPlainText("测试背景")
        assert wizard._desc_page.isComplete() is True
        wizard.deleteLater()
        qapp.processEvents()

    def test_confirm_page_shows_summary(
        self, qapp: QApplication, change_workspace: Path
    ) -> None:
        """Step 3 initializePage 后应显示含项目编号和背景的汇总信息"""
        ps = ProjectService(str(change_workspace))
        cs = ChangeService(str(change_workspace))
        wizard = CreateChangeWizard(ps, cs)
        wizard._background_edit.setPlainText("汇总测试背景")

        # 手动触发 initializePage（模拟导航到 Step 3）
        wizard._confirm_page.initializePage()

        summary_text = wizard._confirm_page._summary_label.text()
        assert "TEST-2026-001" in summary_text
        assert "汇总测试背景" in summary_text
        wizard.deleteLater()
        qapp.processEvents()

    def test_validate_page_creates_change(
        self, qapp: QApplication, change_workspace: Path
    ) -> None:
        """validatePage 应触发创建并发射 change_created 信号"""
        ps = ProjectService(str(change_workspace))
        cs = ChangeService(str(change_workspace))
        wizard = CreateChangeWizard(ps, cs)
        wizard._background_edit.setPlainText("验证测试背景")

        received: list[str] = []
        wizard.change_created.connect(received.append)

        # 直接调用 validatePage（模拟 Finish 点击）
        result = wizard._confirm_page.validatePage()
        assert result is True
        assert received == ["TEST-2026-001"]

        # 确认真实变更单已生成
        changes = cs.list_change_requests("TEST-2026-001")
        assert len(changes) >= 1
        assert changes[0].change_number.startswith("CHG-")
        wizard.deleteLater()
        qapp.processEvents()


# ── TransitionDialog 测试 ────────────────────────────────


class TestTransitionDialog:
    """TransitionDialog 测试"""

    def test_display_info(self, qapp: QApplication, change_workspace: Path) -> None:
        """应正确显示变更单编号/当前状态/目标状态/审批人默认值"""
        cs = ChangeService(str(change_workspace))
        dlg = TransitionDialog("CHG-PLC-2026-001", "draft", "submitted", cs)

        assert dlg._number_label.text() == "CHG-PLC-2026-001"
        assert dlg._current_label.text() == STATUS_LABELS["draft"]
        assert dlg._target_label.text() == STATUS_LABELS["submitted"]
        assert dlg._approver_edit.text() == "fubai"
        dlg.deleteLater()
        qapp.processEvents()

    def test_verification_field_shown_when_completed(
        self, qapp: QApplication, change_workspace: Path
    ) -> None:
        """目标状态为 completed 时验证结论字段应显示且默认'全部通过'"""
        cs = ChangeService(str(change_workspace))
        dlg = TransitionDialog("CHG-PLC-2026-001", "accepting", "completed", cs)

        assert dlg._requires_verification is True
        assert dlg._verification_edit.isVisibleTo(dlg) is True
        assert dlg._verification_edit.toPlainText() == "全部通过"
        dlg.deleteLater()
        qapp.processEvents()

    def test_verification_field_hidden_when_not_completed(
        self, qapp: QApplication, change_workspace: Path
    ) -> None:
        """目标状态非 completed 时验证结论字段应隐藏"""
        cs = ChangeService(str(change_workspace))
        dlg = TransitionDialog("CHG-PLC-2026-001", "draft", "submitted", cs)

        assert dlg._requires_verification is False
        assert dlg._verification_edit.isVisibleTo(dlg) is False
        dlg.deleteLater()
        qapp.processEvents()

    def test_get_transition_data(self, qapp: QApplication, change_workspace: Path) -> None:
        """get_transition_data 应返回审批人/备注/验证结论"""
        cs = ChangeService(str(change_workspace))
        dlg = TransitionDialog("CHG-PLC-2026-001", "draft", "submitted", cs)
        dlg._approver_edit.setText("李四")
        dlg._comment_edit.setPlainText("同意提交")

        data = dlg.get_transition_data()
        assert data["approver"] == "李四"
        assert data["comment"] == "同意提交"
        assert data["verification_conclusion"] == "全部通过"
        dlg.deleteLater()
        qapp.processEvents()

    def test_get_transition_data_completed(
        self, qapp: QApplication, change_workspace: Path
    ) -> None:
        """目标状态为 completed 时验证结论应取自验证结论输入框"""
        cs = ChangeService(str(change_workspace))
        dlg = TransitionDialog("CHG-PLC-2026-001", "accepting", "completed", cs)
        dlg._verification_edit.setPlainText("全部通过")

        data = dlg.get_transition_data()
        assert data["verification_conclusion"] == "全部通过"
        dlg.deleteLater()
        qapp.processEvents()

    def test_transition_completed_signal(
        self, qapp: QApplication, change_workspace: Path
    ) -> None:
        """draft → submitted 流转成功后应发射 transition_completed(change_number) 信号"""
        cs = ChangeService(str(change_workspace))
        # 先用真实 ChangeService 创建一个 draft 变更单
        cr = cs.create_change_request(
            project_id="TEST-2026-001",
            domain="PLC",
            business_nature="DEF",
            impact_scope=["LOCAL"],
            applicant="fubai",
            background="流转测试背景",
            necessity="流转测试必要性",
        )
        assert cr.change_number.startswith("CHG-PLC-")

        dlg = TransitionDialog(cr.change_number, "draft", "submitted", cs)
        received: list[str] = []
        dlg.transition_completed.connect(received.append)
        dlg._on_confirm()

        assert received == [cr.change_number]
        # 确认状态已真实流转
        updated = cs.get_change_request(cr.change_number)
        assert updated is not None
        assert updated.status == "submitted"
        dlg.deleteLater()
        qapp.processEvents()


class TestTransitionDialogStateMachine:
    """TransitionDialog 状态机集成测试（M3-4 T77/T79）"""

    def test_status_machine_integrated(
        self, qapp: QApplication, change_workspace: Path
    ) -> None:
        """TransitionDialog 应包含 StatusMachineView"""
        cs = ChangeService(str(change_workspace))
        dlg = TransitionDialog("CHG-PLC-2026-001", "draft", "submitted", cs)
        assert dlg._status_machine is not None
        assert dlg._status_machine._current == "draft"
        assert dlg._status_machine._target == "submitted"
        dlg.deleteLater()
        qapp.processEvents()

    def test_status_machine_current_highlighted(
        self, qapp: QApplication, change_workspace: Path
    ) -> None:
        """状态机当前状态节点应为蓝色边框样式"""
        cs = ChangeService(str(change_workspace))
        dlg = TransitionDialog("CHG-PLC-2026-001", "draft", "submitted", cs)
        current_btn = dlg._status_machine._buttons["draft"]
        assert not current_btn.isEnabled()  # 当前状态禁用
        style = current_btn.styleSheet()
        assert "#4a90d9" in style  # 蓝色边框
        dlg.deleteLater()
        qapp.processEvents()

    def test_status_machine_target_highlighted(
        self, qapp: QApplication, change_workspace: Path
    ) -> None:
        """状态机目标状态节点应为绿色填充样式"""
        cs = ChangeService(str(change_workspace))
        dlg = TransitionDialog("CHG-PLC-2026-001", "draft", "submitted", cs)
        target_btn = dlg._status_machine._buttons["submitted"]
        assert target_btn.isEnabled()  # 目标状态启用
        style = target_btn.styleSheet()
        assert "#27ae60" in style  # 绿色填充
        dlg.deleteLater()
        qapp.processEvents()

    def test_target_selected_updates_dialog(
        self, qapp: QApplication, change_workspace: Path
    ) -> None:
        """状态机节点点击联动更新 TransitionDialog 目标状态字段"""
        cs = ChangeService(str(change_workspace))
        # submitted 可达 {under_review, draft}
        dlg = TransitionDialog("CHG-PLC-2026-001", "submitted", "under_review", cs)
        assert dlg._target_status == "under_review"
        assert dlg._target_label.text() == STATUS_LABELS["under_review"]

        # 模拟点击 draft 节点（回退）
        dlg._on_target_selected("draft")
        assert dlg._target_status == "draft"
        assert dlg._target_label.text() == STATUS_LABELS["draft"]
        assert dlg._status_machine._target == "draft"
        dlg.deleteLater()
        qapp.processEvents()

    def test_target_selected_completed_shows_verification(
        self, qapp: QApplication, change_workspace: Path
    ) -> None:
        """状态机点击 completed 节点联动显示验证结论字段"""
        cs = ChangeService(str(change_workspace))
        # accepting 可达 {completed, implementing}
        dlg = TransitionDialog("CHG-PLC-2026-001", "accepting", "implementing", cs)
        assert dlg._requires_verification is False
        assert not dlg._verification_edit.isVisibleTo(dlg)

        # 模拟点击 completed 节点
        dlg._on_target_selected("completed")
        assert dlg._target_status == "completed"
        assert dlg._requires_verification is True
        assert dlg._verification_edit.isVisibleTo(dlg) is True
        dlg.deleteLater()
        qapp.processEvents()

    def test_target_selected_non_completed_hides_verification(
        self, qapp: QApplication, change_workspace: Path
    ) -> None:
        """状态机点击非 completed 节点联动隐藏验证结论字段"""
        cs = ChangeService(str(change_workspace))
        # accepting → completed 初始显示验证结论
        dlg = TransitionDialog("CHG-PLC-2026-001", "accepting", "completed", cs)
        assert dlg._requires_verification is True
        assert dlg._verification_edit.isVisibleTo(dlg) is True

        # 模拟点击 implementing 节点（返工）
        dlg._on_target_selected("implementing")
        assert dlg._target_status == "implementing"
        assert dlg._requires_verification is False
        assert not dlg._verification_edit.isVisibleTo(dlg)
        dlg.deleteLater()
        qapp.processEvents()

    def test_status_machine_reachable_matches_flow(
        self, qapp: QApplication, change_workspace: Path
    ) -> None:
        """状态机可达状态集合与 STATUS_FLOW 一致"""
        from auto_pm.change.models import STATUS_FLOW

        cs = ChangeService(str(change_workspace))
        for current in ["draft", "submitted", "under_review", "approved",
                        "implementing", "pending_acceptance", "accepting"]:
            dlg = TransitionDialog("CHG-X", current, "", cs)
            expected = STATUS_FLOW[current]
            assert dlg._status_machine.get_reachable_targets() == expected, (
                f"current={current}: expected {expected}, "
                f"got {dlg._status_machine.get_reachable_targets()}"
            )
            dlg.deleteLater()
        qapp.processEvents()
