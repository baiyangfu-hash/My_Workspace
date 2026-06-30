"""EditChangeDialog 单元测试（M3-1 T64）

测试内容：
- 表单字段存在性（Tab1 基本信息 + Tab2 影响分析）
- 数据加载（_fill_form 从 ChangeRequest 填充表单）
- 数据收集（get_edit_data 返回正确结构）
- 保存调用（_on_save 调用 ChangeService.update_change_request）
- change_updated 信号发射
- §6 字段更新（risk_level/mitigation/propagation_chain/constraint_impacts/domain_impacts）

使用真实 ChangeService + 临时工作空间（不 mock），遵循项目现有 qapp fixture 模式。
"""

from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

import pytest

# 必须在导入 PySide6 前设置离屏渲染，避免无显示环境报错
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import (  # noqa: E402
    QApplication,
    QComboBox,
    QDialogButtonBox,
    QMessageBox,
    QTableWidget,
    QTabWidget,
    QTextEdit,
)

from auto_pm.change.change_service import ChangeService  # noqa: E402
from auto_pm.ui.dialogs.edit_change_dialog import EditChangeDialog  # noqa: E402

# ── fixtures ─────────────────────────────────────────────


@pytest.fixture
def change_workspace(tmp_path: Path) -> Path:
    """临时工作空间，含一个可被 ProjectService/ChangeService 识别的项目"""
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
def _patch_message_boxes() -> Generator[None, None, None]:
    """自动 patch QMessageBox 静态方法，避免模态对话框阻塞测试"""
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


@pytest.fixture
def created_change(change_workspace: Path) -> tuple[ChangeService, str]:
    """创建一个变更单供编辑测试使用，返回 (ChangeService, change_number)"""
    svc = ChangeService(str(change_workspace))
    cr = svc.create_change_request(
        project_id="TEST-2026-001",
        domain="SCPT",
        business_nature="REQ",
        impact_scope=["LOCAL"],
        applicant="测试人",
        background="原始变更背景",
        necessity="原始变更必要性",
        references="原始参考依据",
        planned_date="2026-06-25",
        urgency="normal",
    )
    return svc, cr.change_number


# ── 表单字段存在性测试 ────────────────────────────────────


class TestEditChangeDialogFields:
    """EditChangeDialog 表单字段存在性测试"""

    def test_tab_widget_exists(
        self, qapp: QApplication, created_change: tuple[ChangeService, str]
    ) -> None:
        """对话框应包含 QTabWidget 双 Tab"""
        svc, change_number = created_change
        dialog = EditChangeDialog(change_number, svc)
        assert isinstance(dialog._tab_widget, QTabWidget)
        assert dialog._tab_widget.count() == 2
        assert dialog._tab_widget.tabText(0) == "基本信息"
        assert dialog._tab_widget.tabText(1) == "影响分析"

    def test_basic_tab_fields(
        self, qapp: QApplication, created_change: tuple[ChangeService, str]
    ) -> None:
        """Tab1 基本信息应包含所有基本字段控件"""
        svc, change_number = created_change
        dialog = EditChangeDialog(change_number, svc)
        assert isinstance(dialog._background_edit, QTextEdit)
        assert isinstance(dialog._necessity_edit, QTextEdit)
        assert isinstance(dialog._references_edit, QTextEdit)
        assert isinstance(dialog._urgency_combo, QComboBox)
        assert dialog._urgency_combo.count() == 3  # normal/urgent/critical

    def test_impact_tab_fields(
        self, qapp: QApplication, created_change: tuple[ChangeService, str]
    ) -> None:
        """Tab2 影响分析应包含所有 §6 字段控件"""
        svc, change_number = created_change
        dialog = EditChangeDialog(change_number, svc)
        assert isinstance(dialog._risk_level_combo, QComboBox)
        assert dialog._risk_level_combo.count() == 4  # none/low/medium/high
        assert isinstance(dialog._mitigation_edit, QTextEdit)
        assert isinstance(dialog._propagation_chain_edit, type(dialog._propagation_chain_edit))

        # 约束影响表格 5 行 × 2 列
        assert isinstance(dialog._constraint_table, QTableWidget)
        assert dialog._constraint_table.rowCount() == 5
        assert dialog._constraint_table.columnCount() == 2

        # 领域影响表格 7 行 × 3 列
        assert isinstance(dialog._domain_table, QTableWidget)
        assert dialog._domain_table.rowCount() == 7
        assert dialog._domain_table.columnCount() == 3

    def test_button_box_exists(
        self, qapp: QApplication, created_change: tuple[ChangeService, str]
    ) -> None:
        """对话框应包含保存和取消按钮"""
        svc, change_number = created_change
        dialog = EditChangeDialog(change_number, svc)
        assert isinstance(dialog._button_box, QDialogButtonBox)
        ok_btn = dialog._button_box.button(QDialogButtonBox.StandardButton.Ok)
        cancel_btn = dialog._button_box.button(QDialogButtonBox.StandardButton.Cancel)
        assert ok_btn is not None
        assert cancel_btn is not None
        assert ok_btn.text() == "保存"
        assert cancel_btn.text() == "取消"


# ── 数据加载测试 ──────────────────────────────────────────


class TestEditChangeDialogLoad:
    """EditChangeDialog 数据加载测试"""

    def test_form_filled_on_load(
        self, qapp: QApplication, created_change: tuple[ChangeService, str]
    ) -> None:
        """打开对话框时表单应填充变更单数据"""
        svc, change_number = created_change
        dialog = EditChangeDialog(change_number, svc)

        assert dialog._background_edit.toPlainText() == "原始变更背景"
        assert dialog._necessity_edit.toPlainText() == "原始变更必要性"
        assert dialog._references_edit.toPlainText() == "原始参考依据"
        assert dialog._urgency_combo.currentData() == "normal"
        assert dialog._planned_date_edit.date().toString("yyyy-MM-dd") == "2026-06-25"

    def test_risk_level_default_none(
        self, qapp: QApplication, created_change: tuple[ChangeService, str]
    ) -> None:
        """新建变更单风险等级默认为 none"""
        svc, change_number = created_change
        dialog = EditChangeDialog(change_number, svc)
        assert dialog._risk_level_combo.currentData() == "none"

    def test_constraint_table_default_values(
        self, qapp: QApplication, created_change: tuple[ChangeService, str]
    ) -> None:
        """约束影响表格默认影响程度为'无'"""
        svc, change_number = created_change
        dialog = EditChangeDialog(change_number, svc)
        for row in range(dialog._constraint_table.rowCount()):
            combo = dialog._constraint_table.cellWidget(row, 1)
            assert isinstance(combo, QComboBox)
            assert combo.currentText() == "无"

    def test_domain_table_default_not_affected(
        self, qapp: QApplication, created_change: tuple[ChangeService, str]
    ) -> None:
        """领域影响表格默认'是否受影响'为'否'"""
        svc, change_number = created_change
        dialog = EditChangeDialog(change_number, svc)
        for row in range(dialog._domain_table.rowCount()):
            combo = dialog._domain_table.cellWidget(row, 1)
            assert isinstance(combo, QComboBox)
            assert combo.currentData() is False


# ── 数据收集测试 ──────────────────────────────────────────


class TestEditChangeDialogGetData:
    """EditChangeDialog get_edit_data 测试"""

    def test_get_edit_data_structure(
        self, qapp: QApplication, created_change: tuple[ChangeService, str]
    ) -> None:
        """get_edit_data 应返回包含所有字段的字典"""
        svc, change_number = created_change
        dialog = EditChangeDialog(change_number, svc)
        data = dialog.get_edit_data()

        # §4/§3.4 基本字段
        assert "background" in data
        assert "necessity" in data
        assert "references" in data
        assert "urgency" in data
        assert "planned_date" in data
        # §6 影响分析字段
        assert "risk_level" in data
        assert "mitigation" in data
        assert "propagation_chain" in data
        assert "constraint_impacts" in data
        assert "domain_impacts" in data

    def test_get_edit_data_types(
        self, qapp: QApplication, created_change: tuple[ChangeService, str]
    ) -> None:
        """get_edit_data 返回值类型应正确"""
        svc, change_number = created_change
        dialog = EditChangeDialog(change_number, svc)
        data = dialog.get_edit_data()

        assert isinstance(data["background"], str)
        assert isinstance(data["urgency"], str)
        assert isinstance(data["risk_level"], str)
        assert isinstance(data["constraint_impacts"], dict)
        assert isinstance(data["domain_impacts"], dict)

    def test_get_edit_data_modified_values(
        self, qapp: QApplication, created_change: tuple[ChangeService, str]
    ) -> None:
        """修改表单后 get_edit_data 应返回修改后的值"""
        svc, change_number = created_change
        dialog = EditChangeDialog(change_number, svc)

        # 修改基本字段
        dialog._background_edit.setPlainText("修改后的背景")
        dialog._necessity_edit.setPlainText("修改后的必要性")

        # 修改风险等级
        for i in range(dialog._risk_level_combo.count()):
            if dialog._risk_level_combo.itemData(i) == "high":
                dialog._risk_level_combo.setCurrentIndex(i)
                break

        # 修改缓解措施
        dialog._mitigation_edit.setPlainText("增加单元测试覆盖率")

        # 修改传播链
        dialog._propagation_chain_edit.setText("SCPT -> PLC -> HMI")

        # 修改约束影响（第一行设为'高'）
        combo = dialog._constraint_table.cellWidget(0, 1)
        assert isinstance(combo, QComboBox)
        combo.setCurrentText("高")

        # 修改领域影响（第二行 PLC 设为受影响）
        domain_combo = dialog._domain_table.cellWidget(2, 1)
        assert isinstance(domain_combo, QComboBox)
        domain_combo.setCurrentIndex(1)  # 是
        content_item = dialog._domain_table.item(2, 2)
        assert content_item is not None
        content_item.setText("PLC 程序需同步修改")

        data = dialog.get_edit_data()
        assert data["background"] == "修改后的背景"
        assert data["necessity"] == "修改后的必要性"
        assert data["risk_level"] == "high"
        assert data["mitigation"] == "增加单元测试覆盖率"
        assert data["propagation_chain"] == "SCPT -> PLC -> HMI"

        # 约束影响
        assert data["constraint_impacts"]["范围"] == "高"

        # 领域影响
        assert data["domain_impacts"]["PLC"]["affected"] is True
        assert data["domain_impacts"]["PLC"]["content"] == "PLC 程序需同步修改"


# ── 保存和信号测试 ────────────────────────────────────────


class TestEditChangeDialogSave:
    """EditChangeDialog 保存和信号测试"""

    def test_save_emits_change_updated(
        self, qapp: QApplication, created_change: tuple[ChangeService, str]
    ) -> None:
        """保存成功后应发射 change_updated 信号"""
        svc, change_number = created_change
        dialog = EditChangeDialog(change_number, svc)

        # 修改背景
        dialog._background_edit.setPlainText("保存测试背景")

        # 捕获信号
        received: list[str] = []
        dialog.change_updated.connect(lambda cn: received.append(cn))

        # 点击保存
        dialog._on_save()

        assert len(received) == 1
        assert received[0] == change_number
        assert dialog.result() == QDialogButtonBox.StandardButton.Ok.value or dialog.isVisible() is False

    def test_save_updates_markdown_file(
        self, qapp: QApplication, created_change: tuple[ChangeService, str]
    ) -> None:
        """保存后 Markdown 文件应包含修改后的内容"""
        svc, change_number = created_change
        dialog = EditChangeDialog(change_number, svc)

        # 修改背景和风险等级
        dialog._background_edit.setPlainText("文件更新测试背景")
        for i in range(dialog._risk_level_combo.count()):
            if dialog._risk_level_combo.itemData(i) == "medium":
                dialog._risk_level_combo.setCurrentIndex(i)
                break
        dialog._mitigation_edit.setPlainText("增加代码评审")

        dialog._on_save()

        # 重新从文件加载
        updated_cr = svc.get_change_request(change_number)
        assert updated_cr is not None
        assert "文件更新测试背景" in updated_cr.background
        assert updated_cr.risk_level == "medium"
        assert "增加代码评审" in updated_cr.mitigation

    def test_save_empty_background_shows_warning(
        self, qapp: QApplication, created_change: tuple[ChangeService, str]
    ) -> None:
        """背景为空时保存应被拒绝（不发射信号）"""
        svc, change_number = created_change
        dialog = EditChangeDialog(change_number, svc)

        # 清空背景
        dialog._background_edit.setPlainText("")

        received: list[str] = []
        dialog.change_updated.connect(lambda cn: received.append(cn))

        dialog._on_save()

        # 信号不应发射
        assert len(received) == 0

    def test_save_constraint_impacts_to_file(
        self, qapp: QApplication, created_change: tuple[ChangeService, str]
    ) -> None:
        """保存约束影响后重新解析应得到相同值"""
        svc, change_number = created_change
        dialog = EditChangeDialog(change_number, svc)

        # 修改约束影响
        for row in range(dialog._constraint_table.rowCount()):
            combo = dialog._constraint_table.cellWidget(row, 1)
            assert isinstance(combo, QComboBox)
            if row == 0:
                combo.setCurrentText("高")
            elif row == 1:
                combo.setCurrentText("中")

        dialog._on_save()

        # 重新加载验证
        updated_cr = svc.get_change_request(change_number)
        assert updated_cr is not None
        assert updated_cr.constraint_impacts.get("范围") == "高"
        assert updated_cr.constraint_impacts.get("进度") == "中"

    def test_save_domain_impacts_to_file(
        self, qapp: QApplication, created_change: tuple[ChangeService, str]
    ) -> None:
        """保存领域影响后重新解析应得到相同值"""
        svc, change_number = created_change
        dialog = EditChangeDialog(change_number, svc)

        # 修改领域影响（PLC 和 HMI 设为受影响）
        for row in range(dialog._domain_table.rowCount()):
            domain_item = dialog._domain_table.item(row, 0)
            if domain_item is None:
                continue
            domain_code = domain_item.data(0x0100)  # Qt.UserRole
            if domain_code in ("PLC", "HMI"):
                combo = dialog._domain_table.cellWidget(row, 1)
                assert isinstance(combo, QComboBox)
                combo.setCurrentIndex(1)  # 是
                content_item = dialog._domain_table.item(row, 2)
                assert content_item is not None
                content_item.setText(f"{domain_code} 需同步修改")

        dialog._on_save()

        # 重新加载验证
        updated_cr = svc.get_change_request(change_number)
        assert updated_cr is not None
        assert updated_cr.domain_impacts["PLC"]["affected"] is True
        assert "PLC 需同步修改" in updated_cr.domain_impacts["PLC"]["content"]
        assert updated_cr.domain_impacts["HMI"]["affected"] is True
        assert "HMI 需同步修改" in updated_cr.domain_impacts["HMI"]["content"]

    def test_save_propagation_chain_to_file(
        self, qapp: QApplication, created_change: tuple[ChangeService, str]
    ) -> None:
        """保存传播链后重新解析应得到相同值"""
        svc, change_number = created_change
        dialog = EditChangeDialog(change_number, svc)

        dialog._propagation_chain_edit.setText("SCPT -> PLC -> HMI")
        dialog._on_save()

        updated_cr = svc.get_change_request(change_number)
        assert updated_cr is not None
        assert "SCPT" in updated_cr.propagation_chain
        assert "PLC" in updated_cr.propagation_chain
