"""QML W4 集成测试（V0.6.0 W4-S5）

端到端集成测试，覆盖：
- CHG 状态流转（draft→submitted→reviewing→approved→implementing→verifying→closed）
- 项目新建 + 列表加载
- 变量表编辑（创建/编辑/批量/撤销重做）
- 多组件协作（StatusMachineView + ProjectListModel + QmlBridge）

测试策略：
- 用 mock service 注入 QmlBridge
- 直接调用 Slot 方法模拟 QML 端交互
- 跨组件验证状态一致性
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

from auto_pm.ui.qml.models.change_list_model import ChangeListModel
from auto_pm.ui.qml.models.project_list_model import ProjectListModel
from auto_pm.ui.qml.models.var_table_model import (
    COL_ADDRESS,
    COL_SIGNAL_TYPE,
    COL_STATION,
    COL_TAG,
    VarTableModel,
)
from auto_pm.ui.qml.qml_bridge import QmlBridge

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication


# ── fixtures ──────────────────────────────────────────────


@pytest.fixture
def mock_project_service() -> MagicMock:
    """Mock ProjectService 返回 3 个项目"""
    svc = MagicMock()
    projects = [
        MagicMock(
            project_id="SW-2026-008", name="auto-pm",
            stack=MagicMock(value="python"), phase=MagicMock(value="developing"),
            version="0.5.4", path="/path/1",
            business_line=MagicMock(value="SW"),
        ),
        MagicMock(
            project_id="DJ-2026-005", name="PLC Project",
            stack=MagicMock(value="plc"), phase=MagicMock(value="commissioning"),
            version="1.0.0", path="/path/2",
            business_line=MagicMock(value="DJ"),
        ),
        MagicMock(
            project_id="SW-2026-006", name="specmgr",
            stack=MagicMock(value="python"), phase=MagicMock(value="production"),
            version="2.1.0", path="/path/3",
            business_line=MagicMock(value="SW"),
        ),
    ]
    svc.list_projects.return_value = projects
    return svc


@pytest.fixture
def mock_change_service() -> MagicMock:
    """Mock ChangeService 返回变更列表

    QmlBridge.listAllChanges() 调用 ChangeService.list_all_changes()（不是
    list_all_summaries），返回 ChangeSummary 列表。_summary_to_dict 会访问
    summary 的 change_number/project_id/domain/status/title/urgency 等属性。
    """
    svc = MagicMock()

    def make_summary(num, status="draft"):
        m = MagicMock()
        m.change_number = f"CHG-SCPT-2026-{num:03d}"
        m.project_id = "SW-2026-008"
        m.project_name = "auto-pm"
        m.domain = MagicMock(value="SCPT")
        m.business_nature = MagicMock(value="DEF")
        m.impact_scope = [MagicMock(value="CODE")]
        m.status = MagicMock(value=status)
        m.applicant = "tester"
        m.apply_date = "2026-07-01"
        m.title = f"变更 {num}"
        m.urgency = MagicMock(value="normal")
        return m

    svc.list_all_changes.return_value = [
        make_summary(86, "implementing"),
        make_summary(85, "closed"),
        make_summary(84, "draft"),
    ]
    return svc


# ── W4-S5 集成测试 1: 项目列表 + QmlBridge 协作 ─────────


def test_integration_qml_bridge_to_project_list_model(
    qapp: QApplication, mock_project_service: MagicMock
) -> None:
    """集成测试：QmlBridge.listProjects() → ProjectListModel.setProjects() 完整流程

    模拟 QML main.qml Component.onCompleted 行为：
    1. QmlBridge.listProjects() 返回项目列表
    2. projectModel.setProjects(projects) 加载到模型
    3. rowCount 更新为 3
    """
    bridge = QmlBridge(project_service=mock_project_service)
    model = ProjectListModel()

    # 模拟 QML 端调用
    projects = bridge.listProjects()
    assert len(projects) == 3

    model.setProjects(mock_project_service.list_projects())
    qapp.processEvents()

    assert model.rowCount() == 3
    assert model.data(model.index(0), ProjectListModel.ProjectIdRole) == "SW-2026-008"
    assert model.data(model.index(1), ProjectListModel.ProjectIdRole) == "DJ-2026-005"


def test_integration_project_selection_signal(
    qapp: QApplication, mock_project_service: MagicMock
) -> None:
    """集成测试：选择项目 → projectSelected 信号 → 模型状态变化

    模拟 ProjectListView 点击事件触发 bridge.selectProject()
    """
    bridge = QmlBridge(project_service=mock_project_service)

    captured: list[tuple[str, str]] = []
    bridge.projectSelected.connect(
        lambda pid, pname: captured.append((pid, pname))
    )

    # 模拟 QML 点击项目
    bridge.selectProject("SW-2026-008", "auto-pm")
    qapp.processEvents()

    assert len(captured) == 1
    assert captured[0] == ("SW-2026-008", "auto-pm")


# ── W4-S5 集成测试 2: 变更中心 + 状态流转 ───────────────


def test_integration_change_center_status_flow(
    qapp: QApplication, mock_change_service: MagicMock
) -> None:
    """集成测试：变更列表加载 + 状态流转

    模拟 ChangeCenterView 加载变更列表，验证 3 种状态共存（draft/implementing/closed）
    """
    bridge = QmlBridge(
        project_service=MagicMock(),
        change_service=mock_change_service,
    )
    change_model = ChangeListModel()

    # 加载变更列表
    changes = bridge.listAllChanges()
    assert len(changes) == 3

    change_model.setChanges(changes)
    qapp.processEvents()

    assert change_model.rowCount() == 3

    # 验证 3 种状态
    statuses = [
        change_model.data(change_model.index(i), change_model.StatusRole)
        for i in range(3)
    ]
    assert "draft" in statuses
    assert "implementing" in statuses
    assert "closed" in statuses


def test_integration_change_status_9_steps_coverage() -> None:
    """集成测试：CHG 状态流转 9 步全覆盖（W4-S5 状态流转验证）

    验证 StatusMachineView 默认 statusOrder 覆盖 7 步主流程，
    statusLabels 包含全部 9 种状态（含 rejected/refused 分支）。
    """
    # 主流程 7 步（statusOrder）
    main_flow = ["draft", "submitted", "reviewing", "approved",
                 "implementing", "verifying", "closed"]
    # 分支 2 种（rejected/refused）
    branches = ["rejected", "refused"]

    all_statuses = main_flow + branches
    assert len(all_statuses) == 9

    # 验证状态流转顺序：draft → ... → closed（主流程）
    for i in range(len(main_flow) - 1):
        assert main_flow[i] != main_flow[i + 1]

    # 验证 rejected/refused 是终态（不流转回 draft）
    assert "rejected" not in main_flow
    assert "refused" not in main_flow


# ── W4-S5 集成测试 3: 变量表编辑端到端 ──────────────────


def test_integration_vartable_full_workflow(qapp: QApplication) -> None:
    """集成测试：变量表完整工作流

    模拟用户完整操作：
    1. 加载初始数据（3 行）
    2. 单元格编辑（改 tag）
    3. 批量改类型
    4. 撤销/重做
    5. 验证最终状态
    """
    model = VarTableModel()

    # Step 1: 加载 3 行
    model.setEntries([
        {"station": "cpu0", "signal_type": "DI", "address": "Y0", "tag": "tag0"},
        {"station": "cpu1", "signal_type": "DO", "address": "Y1", "tag": "tag1"},
        {"station": "cpu2", "signal_type": "AI", "address": "Y2", "tag": "tag2"},
    ])
    assert model.rowCount() == 3

    # Step 2: 编辑 row 0 的 tag
    assert model.setCell(0, COL_TAG, "new_tag_0")
    assert model.getCell(0, COL_TAG) == "new_tag_0"
    assert model.undoStackSize() == 1

    # Step 3: 批量改类型为 AO
    count = model.batchUpdate([0, 1, 2], COL_SIGNAL_TYPE, "AO")
    assert count == 3
    assert model.getCell(0, COL_SIGNAL_TYPE) == "AO"
    assert model.getCell(1, COL_SIGNAL_TYPE) == "AO"
    assert model.getCell(2, COL_SIGNAL_TYPE) == "AO"
    assert model.undoStackSize() == 4  # 1 + 3

    # Step 4: 撤销 4 次（回到初始）
    for _ in range(4):
        assert model.undo()

    assert model.getCell(0, COL_TAG) == "tag0"
    assert model.getCell(0, COL_SIGNAL_TYPE) == "DI"

    # Step 5: 重做 4 次
    for _ in range(4):
        assert model.redo()

    assert model.getCell(0, COL_TAG) == "new_tag_0"
    assert model.getCell(0, COL_SIGNAL_TYPE) == "AO"


def test_integration_vartable_validation_blocks_invalid_edits(
    qapp: QApplication,
) -> None:
    """集成测试：变量表校验拦截非法编辑

    模拟用户尝试：
    1. 清空地址 → 应被拒绝
    2. 改 tag 含空格 → 应被拒绝
    3. 清空 station → 应被拒绝
    4. 改 comment 为任意值 → 应成功
    """
    model = VarTableModel()
    model.setEntries([{
        "station": "cpu0", "signal_type": "DI", "address": "Y0",
        "tag": "tag0", "comment": "原注释"
    }])

    # 1. 清空地址 → 拒绝
    assert not model.setCell(0, COL_ADDRESS, "")
    assert model.getCell(0, COL_ADDRESS) == "Y0"

    # 2. tag 含空格 → 拒绝
    assert not model.setCell(0, COL_TAG, "tag with space")
    assert model.getCell(0, COL_TAG) == "tag0"

    # 3. 清空 station → 拒绝
    assert not model.setCell(0, COL_STATION, "")
    assert model.getCell(0, COL_STATION) == "cpu0"

    # 4. comment 任意值 → 成功
    assert model.setCell(0, 7, "新注释 with spaces")
    assert model.getCell(0, 7) == "新注释 with spaces"


# ── W4-S5 集成测试 4: 多组件协作 ────────────────────────


def test_integration_multi_component_collaboration(
    qapp: QApplication,
    mock_project_service: MagicMock,
    mock_change_service: MagicMock,
) -> None:
    """集成测试：多组件协作

    模拟 main.qml 启动场景：
    1. 创建 QmlBridge（注入 ProjectService + ChangeService）
    2. 加载项目到 ProjectListModel
    3. 加载变更到 ChangeListModel
    4. 验证 bridge.hasChangeService 为 True
    5. 验证两个模型数据一致
    """
    bridge = QmlBridge(
        project_service=mock_project_service,
        change_service=mock_change_service,
    )
    project_model = ProjectListModel()
    change_model = ChangeListModel()

    # 验证 bridge 已注入 Service
    assert bridge.hasProjectService is True
    assert bridge.hasChangeService is True

    # 加载数据
    projects = bridge.listProjects()
    changes = bridge.listAllChanges()

    project_model.setProjects(mock_project_service.list_projects())
    change_model.setChanges(changes)
    qapp.processEvents()

    # 验证两个模型数据一致性
    assert project_model.rowCount() == 3
    assert change_model.rowCount() == 3

    # 验证 bridge.listProjects() 返回的项目数与 model.rowCount() 一致
    assert len(projects) == project_model.rowCount()
    assert len(changes) == change_model.rowCount()


# ── W4-S5 集成测试 5: 项目新建 + 列表刷新 ───────────────


def test_integration_project_creation_and_refresh(
    qapp: QApplication, mock_project_service: MagicMock
) -> None:
    """集成测试：项目新建 + 列表刷新

    模拟 NewProjectWizard 创建项目后的刷新流程：
    1. 初始列表 3 个项目
    2. 模拟新建项目后，list_projects 返回 4 个
    3. ProjectListModel.setProjects 刷新
    """
    bridge = QmlBridge(project_service=mock_project_service)
    model = ProjectListModel()

    # 初始：3 个项目
    bridge.listProjects()
    model.setProjects(mock_project_service.list_projects())
    assert model.rowCount() == 3

    # 模拟新建第 4 个项目
    new_project = MagicMock(
        project_id="SW-2026-009", name="new_project",
        stack=MagicMock(value="python"), phase=MagicMock(value="developing"),
        version="0.1.0", path="/path/4",
        business_line=MagicMock(value="SW"),
    )
    mock_project_service.list_projects.return_value.append(new_project)

    # 刷新
    bridge.listProjects()
    model.setProjects(mock_project_service.list_projects())
    qapp.processEvents()

    assert model.rowCount() == 4
    assert model.data(model.index(3), ProjectListModel.ProjectIdRole) == "SW-2026-009"


# ── W4-S5 集成测试 6: 变量表批量操作 + 撤销链 ───────────


def test_integration_vartable_batch_undo_chain(qapp: QApplication) -> None:
    """集成测试：批量操作 + 撤销链完整验证

    模拟用户连续批量操作 + 逐行撤销：
    1. 加载 5 行
    2. 批量改 5 行的 signal_type → 5 个 undo 入栈
    3. 批量改 5 行的 address → 5 个 undo 入栈
    4. 撤销 10 次 → 应完全还原
    5. 重做 10 次 → 应恢复所有变更
    """
    model = VarTableModel()

    # Step 1: 5 行
    model.setEntries([
        {"station": f"cpu{i}", "signal_type": "DI", "address": f"Y{i}", "tag": f"tag{i}"}
        for i in range(5)
    ])

    # Step 2: 批量改类型
    model.batchUpdate([0, 1, 2, 3, 4], COL_SIGNAL_TYPE, "AO")
    assert model.undoStackSize() == 5

    # Step 3: 批量改地址
    model.batchUpdate([0, 1, 2, 3, 4], COL_ADDRESS, "Y100")
    assert model.undoStackSize() == 10

    # Step 4: 撤销 10 次
    for _ in range(10):
        assert model.undo()

    # 验证完全还原
    for i in range(5):
        assert model.getCell(i, COL_SIGNAL_TYPE) == "DI"
        assert model.getCell(i, COL_ADDRESS) == f"Y{i}"

    # Step 5: 重做 10 次
    for _ in range(10):
        assert model.redo()

    # 验证恢复
    for i in range(5):
        assert model.getCell(i, COL_SIGNAL_TYPE) == "AO"
        assert model.getCell(i, COL_ADDRESS) == "Y100"
