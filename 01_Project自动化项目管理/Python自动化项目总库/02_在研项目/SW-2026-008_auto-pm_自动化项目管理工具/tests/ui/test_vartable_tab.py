"""VartableTab 单元测试

M4-Iter1：验证旧 VartableTab（auto_pm.ui.workspace.vartable_tab）的扫描和加载功能。
V2.3 Week4 T16：验证新 VartableTab（auto_pm.ui.vartable.vartable_tab）基于
VariableTableEditor + vartable 模块 Parser/Converter 的功能。
"""

from __future__ import annotations

import csv
import os
from pathlib import Path

import pytest

# 必须在导入 PySide6 前设置离屏渲染
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# 跳过 GUI 测试如果 PySide6 不可用
pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication  # noqa: E402

from auto_pm.ui.vartable.vartable_tab import (  # noqa: E402
    EDITABLE_ROLES,
)
from auto_pm.ui.vartable.vartable_tab import (
    VartableTab as VartableTabV2,
)
from auto_pm.ui.workspace.vartable_tab import VartableTab  # noqa: E402


class TestVartableTab:
    """VartableTab 测试"""

    def test_vartable_tab_creation(self, qapp: QApplication) -> None:
        """创建 VartableTab"""
        tab = VartableTab()
        assert tab is not None

    def test_set_project_path_empty(self, qapp: QApplication, tmp_path: Path) -> None:
        """设置空项目路径"""
        tab = VartableTab()
        tab.set_project_path("")
        # 不应崩溃，状态应为未加载
        assert "未加载" in tab._status_label.text() or "无效" in tab._status_label.text()

    def test_set_project_path_no_vartable(self, qapp: QApplication, tmp_path: Path) -> None:
        """设置无变量表的项目路径"""
        project_dir = tmp_path / "DJ-2026-001_项目"
        project_dir.mkdir()

        tab = VartableTab()
        tab.set_project_path(str(project_dir))
        assert "未找到" in tab._status_label.text()

    def test_set_project_path_with_vartable(self, qapp: QApplication, tmp_path: Path) -> None:
        """设置含变量表的项目路径"""
        project_dir = tmp_path / "DJ-2026-002_项目"
        project_dir.mkdir()
        vartable_dir = project_dir / "02_PLC程序" / "通用ST程序及变量表"
        vartable_dir.mkdir(parents=True)

        # 创建变量表 CSV 文件
        vartable_file = vartable_dir / "变量表_全局.csv"
        vartable_file.write_text(
            "名称,类型,地址,注释\n"
            "Motor1,Bool,%Q0.0,1号电机启动\n"
            "Speed1,Int,%MW10,1号电机速度\n"
            "Temp1,Real,%MD20,温度传感器1\n",
            encoding="utf-8",
        )

        tab = VartableTab()
        tab.set_project_path(str(project_dir))

        # 应找到 1 个变量表文件
        assert tab._file_combo.count() == 1
        # 应加载 3 个变量
        assert tab._table.rowCount() == 3
        # 状态应显示已加载
        assert "已加载" in tab._status_label.text()
        assert "3 个变量" in tab._status_label.text()

    def test_vartable_tab_refresh(self, qapp: QApplication, tmp_path: Path) -> None:
        """刷新变量表"""
        project_dir = tmp_path / "DJ-2026-003_项目"
        project_dir.mkdir()
        vartable_dir = project_dir / "02_PLC程序" / "通用ST程序及变量表"
        vartable_dir.mkdir(parents=True)
        (vartable_dir / "vartable1.csv").write_text(
            "名称,类型,地址,注释\nM1,Bool,%Q0.0,电机1\n",
            encoding="utf-8",
        )

        tab = VartableTab()
        tab.set_project_path(str(project_dir))
        assert tab._file_combo.count() == 1

        # 添加第二个文件后刷新
        (vartable_dir / "vartable2.csv").write_text(
            "名称,类型,地址,注释\nM2,Bool,%Q0.1,电机2\n",
            encoding="utf-8",
        )
        tab._on_refresh()
        assert tab._file_combo.count() == 2

    def test_vartable_tab_invalid_csv(self, qapp: QApplication, tmp_path: Path) -> None:
        """读取无效 CSV 文件"""
        project_dir = tmp_path / "DJ-2026-004_项目"
        project_dir.mkdir()
        vartable_dir = project_dir / "02_PLC程序" / "通用ST程序及变量表"
        vartable_dir.mkdir(parents=True)
        # 创建一个无效的 CSV 文件（实际是文本）
        (vartable_dir / "bad.csv").write_text("这不是有效的CSV", encoding="utf-8")

        tab = VartableTab()
        tab.set_project_path(str(project_dir))
        # 不应崩溃，应能处理（单行无表头）
        assert tab._table.rowCount() == 0  # 只有 1 行，作为表头跳过


# ════════════════════════════════════════════════════════════
# V2.3 Week4 T16: 新 VartableTab（auto_pm.ui.vartable.vartable_tab）
# 以下测试验证基于 VariableTableEditor + vartable 模块 Parser/Converter
# 的新 VartableTab 组件。与上方旧 VartableTab 测试共存于同一文件。
# ════════════════════════════════════════════════════════════

# ── 新 VartableTab 测试用样本数据 ─────────────────────────

_V2_IO_POINTS_CSV = (
    "station,signal_type,address,tag,signal_name,device,comment\n"
    "cpu,DI,X0,Z_Home_Sensor,Z轴原点传感器,Z轴开关,P35\n"
    "cpu,DO,Y0,Motor1_Start,电机1启动,KM1,P40\n"
)

_V2_PROGRAM_BLOCKS_YML = (
    "blocks:\n"
    "  - name: FB_Motor\n"
    "    type: FUNCTION_BLOCK\n"
    "    path: PLC_ST/FB_Motor.scl\n"
    "    responsibility: 电机控制\n"
)

_V2_SCL_CONTENT = (
    "FUNCTION_BLOCK FB_Motor\n"
    "VAR_INPUT\n"
    "    Start : BOOL;\n"
    "    Stop : BOOL;\n"
    "END_VAR\n"
    "VAR_OUTPUT\n"
    "    Running : BOOL;\n"
    "END_VAR\n"
    "BEGIN\n"
    "    Running := Start AND NOT Stop;\n"
    "END_FUNCTION_BLOCK\n"
)


def _create_test_project(tmp_path: Path, project_name: str = "DJ-2026-V2") -> Path:
    """创建含变量表文件的测试项目

    结构：
        tmp_path/DJ-2026-V2/
            02_PLC程序/
                工程资产/
                    io_points.csv
                    program_blocks.yml
                PLC_ST/
                    FB_Motor.scl

    注意：sorted(rglob) 排序后 PLC_ST/FB_Motor.scl 排在 工程资产/io_points.csv
    之前（'P' < '工'），故 set_project_path 后首个加载的是 FB_Motor.scl（3 条 VAR）。
    """
    project_dir = tmp_path / project_name
    plc_dir = project_dir / "02_PLC程序"
    asset_dir = plc_dir / "工程资产"
    scl_dir = plc_dir / "PLC_ST"
    asset_dir.mkdir(parents=True)
    scl_dir.mkdir(parents=True)

    (asset_dir / "io_points.csv").write_text(_V2_IO_POINTS_CSV, encoding="utf-8")
    (asset_dir / "program_blocks.yml").write_text(
        _V2_PROGRAM_BLOCKS_YML, encoding="utf-8"
    )
    (scl_dir / "FB_Motor.scl").write_text(_V2_SCL_CONTENT, encoding="utf-8")
    return project_dir


def _select_file_in_list(tab: VartableTabV2, name_substring: str) -> int:
    """在文件列表中选中包含指定子串的文件，返回行号；未找到返回 -1"""
    for i in range(tab.file_list.count()):
        item_text = tab.file_list.item(i).text()
        if name_substring in item_text:
            tab.file_list.setCurrentRow(i)
            return i
    return -1


class TestVartableTabV2:
    """新 VartableTab 单元测试（V2.3 Week4 T16）"""

    def test_tab_creation(self, qapp: QApplication) -> None:
        """创建 VartableTab"""
        tab = VartableTabV2()
        assert tab is not None
        assert tab.editor is not None
        assert tab.editor.row_count == 0  # 编辑器行数为 0

    def test_file_list_display(self, qapp: QApplication, tmp_path: Path) -> None:
        """设置项目路径后文件列表展示

        set_project_path 后首个文件被自动选中并加载，status_label 显示文件加载
        信息（而非"找到 N 个"，该文本被 _load_file 覆盖）。
        """
        project_dir = _create_test_project(tmp_path)
        tab = VartableTabV2()
        tab.set_project_path(str(project_dir))
        # 应找到 3 个文件（io_points.csv + program_blocks.yml + FB_Motor.scl）
        assert tab.file_list.count() == 3
        # 首个文件（FB_Motor.scl）自动加载，状态显示加载信息
        assert "已加载" in tab.status_label.text()

    def test_file_selection_parse(self, qapp: QApplication, tmp_path: Path) -> None:
        """选择 io_points.csv 后解析加载到编辑器

        文件列表按路径排序，PLC_ST/FB_Motor.scl 排在 工程资产/io_points.csv 之前，
        故需显式选中 io_points.csv。
        """
        project_dir = _create_test_project(tmp_path)
        tab = VartableTabV2()
        tab.set_project_path(str(project_dir))
        # 显式选中 io_points.csv
        row = _select_file_in_list(tab, "io_points.csv")
        assert row >= 0
        # 编辑器应加载了数据（io_points.csv 有 2 条变量）
        assert tab.editor.row_count == 2
        # 验证第一行 tag
        entries = tab.editor.get_entries()
        assert entries[0].tag == "Z_Home_Sensor"

    def test_batch_parse(self, qapp: QApplication, tmp_path: Path) -> None:
        """批量解析合并所有 VarTable 文件"""
        project_dir = _create_test_project(tmp_path)
        tab = VartableTabV2()
        tab.set_project_path(str(project_dir))
        # 初始加载了第一个文件（FB_Motor.scl，3 条 VAR 变量）
        assert tab.editor.row_count == 3
        # 批量解析
        tab._on_batch_parse()
        # io_points.csv（2 条）+ FB_Motor.scl（3 条 VAR）= 5 条
        # program_blocks.yml 是 BlockTable 不是 VarTable，不计入
        assert tab.editor.row_count >= 5
        assert "批量解析" in tab.status_label.text()

    def test_role_permission_editable(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """PLCEngineer 角色可编辑"""
        project_dir = _create_test_project(tmp_path)
        tab = VartableTabV2(role="PLCEngineer")
        tab.set_project_path(str(project_dir))
        assert tab.role == "PLCEngineer"
        assert tab.editor.model.editable is True
        # 添加/删除按钮应可用
        assert tab.editor._add_btn.isEnabled() is True

    def test_role_permission_readonly(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """非授权角色只读"""
        project_dir = _create_test_project(tmp_path)
        tab = VartableTabV2(role="Viewer")
        tab.set_project_path(str(project_dir))
        assert tab.editor.model.editable is False
        # 添加/删除按钮应禁用
        assert tab.editor._add_btn.isEnabled() is False
        assert tab.editor._delete_btn.isEnabled() is False

    def test_role_permission_spec_editor(
        self, qapp: QApplication
    ) -> None:
        """SpecEditor 角色可编辑"""
        tab = VartableTabV2(role="SpecEditor")
        assert tab.editor.model.editable is True
        # 验证 EDITABLE_ROLES 常量
        assert "PLCEngineer" in EDITABLE_ROLES
        assert "SpecEditor" in EDITABLE_ROLES

    def test_set_role_toggle(self, qapp: QApplication) -> None:
        """切换角色后编辑状态变化

        使用 _add_btn.isEnabled()（方法调用）而非 model.editable（属性）做断言，
        避免 mypy 将 model.editable 窄化为 Literal 后，set_role 的副作用无法被
        mypy 追踪，导致后续断言被判定为 unreachable。
        """
        tab = VartableTabV2(role="")
        assert tab.editor._add_btn.isEnabled() is False
        tab.set_role("PLCEngineer")
        assert tab.editor._add_btn.isEnabled() is True
        tab.set_role("Guest")
        assert tab.editor._add_btn.isEnabled() is False

    def test_editor_integration_export(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """编辑器集成：选择文件后导出"""
        project_dir = _create_test_project(tmp_path)
        tab = VartableTabV2(role="PLCEngineer")
        tab.set_project_path(str(project_dir))
        # 显式选中 io_points.csv（2 条变量）
        row = _select_file_in_list(tab, "io_points.csv")
        assert row >= 0
        assert tab.editor.row_count == 2
        # 导出为 CSV
        export_path = tmp_path / "export.csv"
        result = tab.editor.export_file(export_path, "csv")
        assert result is True
        assert export_path.exists()
        # 验证导出内容
        with open(export_path, encoding="utf-8") as f:
            rows = list(csv.reader(f))
        assert len(rows) == 3  # 表头 + 2 行

    def test_empty_project_path(self, qapp: QApplication) -> None:
        """空项目路径"""
        tab = VartableTabV2()
        tab.set_project_path("")
        assert tab.file_list.count() == 0
        assert "无效" in tab.status_label.text()

    def test_no_vartable_files(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """项目无变量表文件"""
        project_dir = tmp_path / "empty_project"
        project_dir.mkdir()
        (project_dir / "02_PLC程序").mkdir()
        tab = VartableTabV2()
        tab.set_project_path(str(project_dir))
        assert tab.file_list.count() == 0
        assert "未找到" in tab.status_label.text()
