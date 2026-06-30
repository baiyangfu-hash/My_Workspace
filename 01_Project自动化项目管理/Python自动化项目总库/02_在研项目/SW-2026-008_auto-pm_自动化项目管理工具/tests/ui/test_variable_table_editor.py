"""VariableTableEditor 单元测试（V2.3 Week4 T15）

验证变量表编辑器的创建/空数据/加载/编辑/增删/导入/导出/只读模式。

设计原则：
- 遵循项目 qapp fixture（session 级，tests/conftest.py 单一定位）
- 用 tmp_path 隔离，不污染生产数据
- PySide6 枚举完整路径（Qt.ItemDataRole.DisplayRole 而非 Qt.DisplayRole）
- 禁止 if x is not None: assert 模式（元测试 AST 拦截）
"""

from __future__ import annotations

import csv
import os
from pathlib import Path

# 必须在导入 PySide6 前设置离屏渲染
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QModelIndex, Qt  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from auto_pm.ui.vartable.variable_table_editor import (  # noqa: E402
    COLUMNS,
    VariableTableEditor,
    VariableTableModel,
)
from auto_pm.vartable.models import VarEntry  # noqa: E402

# ── 测试用样本数据 ───────────────────────────────────────


def _make_entry(
    tag: str = "Motor1",
    address: str = "%Q0.0",
    signal_type: str = "DO",
    station: str = "cpu",
) -> VarEntry:
    """构造测试用 VarEntry"""
    return VarEntry(
        station=station,
        signal_type=signal_type,
        address=address,
        tag=tag,
        signal_name=f"{tag} 信号名",
        device="测试设备",
        comment=f"{tag} 注释",
        source_format="io_points_csv",
        line_number=2,
    )


_SAMPLE_ENTRIES: list[VarEntry] = [
    _make_entry("Motor1", "%Q0.0", "DO", "cpu"),
    _make_entry("Motor2", "%Q0.1", "DO", "cpu"),
    _make_entry("Sensor1", "%I0.0", "DI", "cpu"),
]


# ── 测试用 io_points.csv 文件 ────────────────────────────

_IO_POINTS_CSV_CONTENT = (
    "station,signal_type,address,tag,signal_name,device,comment\n"
    "cpu,DI,X0,Z_Home_Sensor,Z轴原点传感器,Z轴开关,P35\n"
    "cpu,DO,Y0,Motor1_Start,电机1启动,KM1,P40\n"
    "remote_io_1,DI,RIO1:X1,Door_Lock,门锁信号,SL2,P41\n"
)


class TestVariableTableModel:
    """VariableTableModel 单元测试"""

    def test_model_creation_default_editable(
        self, qapp: QApplication
    ) -> None:
        """创建模型，默认可编辑"""
        model = VariableTableModel()
        assert model.rowCount() == 0
        assert model.columnCount() == len(COLUMNS)
        assert model.editable is True

    def test_model_load_entries(self, qapp: QApplication) -> None:
        """加载 VarEntry 列表后行数正确"""
        model = VariableTableModel()
        model.set_entries(_SAMPLE_ENTRIES)
        assert model.rowCount() == 3
        # 验证第一行第一列数据
        idx = model.index(0, 0)
        assert idx.data(Qt.ItemDataRole.DisplayRole) == "cpu"
        # 验证 tag 列（第 4 列，索引 3）
        idx_tag = model.index(0, 3)
        assert idx_tag.data(Qt.ItemDataRole.DisplayRole) == "Motor1"

    def test_model_get_entries_roundtrip(self, qapp: QApplication) -> None:
        """加载后导出 VarEntry 列表，字段值一致（line_number 除外）"""
        model = VariableTableModel()
        model.set_entries(_SAMPLE_ENTRIES)
        entries = model.get_entries()
        assert len(entries) == 3
        assert entries[0].tag == "Motor1"
        assert entries[0].address == "%Q0.0"
        assert entries[0].station == "cpu"
        # line_number 在导出时统一为 0（编辑后行号无意义）
        assert entries[0].line_number == 0

    def test_model_add_row(self, qapp: QApplication) -> None:
        """添加空行"""
        model = VariableTableModel()
        model.set_entries(_SAMPLE_ENTRIES)
        assert model.rowCount() == 3
        new_row = model.add_row()
        assert new_row == 3
        assert model.rowCount() == 4
        # 新行所有列为空串
        for col in range(model.columnCount()):
            idx = model.index(3, col)
            assert idx.data(Qt.ItemDataRole.DisplayRole) == ""

    def test_model_remove_row(self, qapp: QApplication) -> None:
        """删除指定行"""
        model = VariableTableModel()
        model.set_entries(_SAMPLE_ENTRIES)
        assert model.rowCount() == 3
        assert model.remove_row(0) is True
        assert model.rowCount() == 2
        # 删除后第一行应为原第二行
        idx = model.index(0, 3)
        assert idx.data(Qt.ItemDataRole.DisplayRole) == "Motor2"
        # 越界删除返回 False
        assert model.remove_row(99) is False

    def test_model_copy_row(self, qapp: QApplication) -> None:
        """复制行到末尾"""
        model = VariableTableModel()
        model.set_entries(_SAMPLE_ENTRIES)
        assert model.rowCount() == 3
        new_idx = model.copy_row(0)
        assert new_idx == 3
        assert model.rowCount() == 4
        # 复制行与原行数据一致
        orig_idx = model.index(0, 3)
        copy_idx = model.index(3, 3)
        assert (
            orig_idx.data(Qt.ItemDataRole.DisplayRole)
            == copy_idx.data(Qt.ItemDataRole.DisplayRole)
            == "Motor1"
        )

    def test_model_set_data_editable(self, qapp: QApplication) -> None:
        """可编辑模式下 setData 修改单元格"""
        model = VariableTableModel(editable=True)
        model.set_entries(_SAMPLE_ENTRIES)
        idx = model.index(0, 3)  # tag 列
        assert model.setData(idx, "Modified_Tag", Qt.ItemDataRole.EditRole) is True
        assert idx.data(Qt.ItemDataRole.DisplayRole) == "Modified_Tag"

    def test_model_set_data_readonly(self, qapp: QApplication) -> None:
        """只读模式下 setData 失败"""
        model = VariableTableModel(editable=False)
        model.set_entries(_SAMPLE_ENTRIES)
        idx = model.index(0, 3)
        assert model.setData(idx, "Modified", Qt.ItemDataRole.EditRole) is False
        # 原值不变
        assert idx.data(Qt.ItemDataRole.DisplayRole) == "Motor1"
        # flags 不含 ItemIsEditable
        flags = model.flags(idx)
        assert not (flags & Qt.ItemFlag.ItemIsEditable)

    def test_model_flags_empty_index(self, qapp: QApplication) -> None:
        """空索引 flags 返回 NoItemFlags"""
        model = VariableTableModel()
        assert model.flags(QModelIndex()) == Qt.ItemFlag.NoItemFlags

    def test_model_header_data(self, qapp: QApplication) -> None:
        """表头数据正确"""
        model = VariableTableModel()
        # 水平表头
        for i, expected in enumerate(COLUMNS):
            assert (
                model.headerData(i, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
                == expected
            )
        # 垂直表头（行号从 1 开始）
        assert (
            model.headerData(0, Qt.Orientation.Vertical, Qt.ItemDataRole.DisplayRole)
            == "1"
        )


class TestVariableTableEditor:
    """VariableTableEditor 单元测试"""

    def test_editor_creation(self, qapp: QApplication) -> None:
        """创建编辑器，默认空数据"""
        editor = VariableTableEditor()
        assert editor.row_count == 0
        assert "0 条变量" in editor.status_label.text()

    def test_editor_load_entries(self, qapp: QApplication) -> None:
        """加载 VarEntry 列表后状态更新"""
        editor = VariableTableEditor()
        editor.set_entries(_SAMPLE_ENTRIES)
        assert editor.row_count == 3
        assert "3 条变量" in editor.status_label.text()

    def test_editor_add_row(self, qapp: QApplication) -> None:
        """添加行按钮触发数据变更"""
        editor = VariableTableEditor()
        editor.set_entries(_SAMPLE_ENTRIES)
        assert editor.row_count == 3
        editor._on_add_clicked()
        assert editor.row_count == 4
        assert "4 条变量" in editor.status_label.text()

    def test_editor_delete_row(self, qapp: QApplication) -> None:
        """删除行按钮触发数据变更"""
        editor = VariableTableEditor()
        editor.set_entries(_SAMPLE_ENTRIES)
        assert editor.row_count == 3
        # 选中第一行
        editor.table.selectRow(0)
        editor.table.setCurrentIndex(editor.model.index(0, 0))
        editor._on_delete_clicked()
        assert editor.row_count == 2

    def test_editor_import_file(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """导入 io_points.csv 文件"""
        csv_file = tmp_path / "io_points.csv"
        csv_file.write_text(_IO_POINTS_CSV_CONTENT, encoding="utf-8")

        editor = VariableTableEditor()
        assert editor.row_count == 0
        result = editor.import_file(csv_file)
        assert result is True
        assert editor.row_count == 3
        # 验证第一行 tag
        entries = editor.get_entries()
        assert entries[0].tag == "Z_Home_Sensor"

    def test_editor_export_file_csv(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """导出为 CSV 文件"""
        editor = VariableTableEditor()
        editor.set_entries(_SAMPLE_ENTRIES)
        export_path = tmp_path / "export.csv"
        result = editor.export_file(export_path, "csv")
        assert result is True
        assert export_path.exists()
        # 验证 CSV 内容
        with open(export_path, encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
        # 表头 + 3 行数据
        assert len(rows) == 4
        assert rows[0][0] == "station"
        assert rows[1][3] == "Motor1"  # tag 列

    def test_editor_export_file_json(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """导出为 JSON 文件"""
        editor = VariableTableEditor()
        editor.set_entries(_SAMPLE_ENTRIES)
        export_path = tmp_path / "export.json"
        result = editor.export_file(export_path, "json")
        assert result is True
        assert export_path.exists()
        content = export_path.read_text(encoding="utf-8")
        assert '"total_count": 3' in content

    def test_editor_export_empty_data(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """空数据导出失败"""
        editor = VariableTableEditor()
        result = editor.export_file(tmp_path / "empty.csv", "csv")
        assert result is False
        assert "无数据" in editor.status_label.text()

    def test_editor_readonly_mode(self, qapp: QApplication) -> None:
        """只读模式：添加/删除按钮禁用"""
        editor = VariableTableEditor(editable=False)
        editor.set_entries(_SAMPLE_ENTRIES)
        assert editor.model.editable is False
        # 添加/删除按钮应禁用
        assert editor._add_btn.isEnabled() is False
        assert editor._delete_btn.isEnabled() is False

    def test_editor_set_editable_toggle(self, qapp: QApplication) -> None:
        """切换可编辑状态

        注意：使用 _add_btn.isEnabled()（方法调用）而非 model.editable（属性）做初始
        状态断言，避免 mypy 将 model.editable 窄化为 Literal[False] 后，set_editable
        的副作用无法被 mypy 追踪，导致后续断言被判定为 unreachable。
        """
        editor = VariableTableEditor(editable=False)
        assert editor._add_btn.isEnabled() is False
        editor.set_editable(True)
        assert editor.model.editable is True
        assert editor._add_btn.isEnabled() is True

    def test_editor_import_nonexistent_file(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """导入不存在的文件失败"""
        editor = VariableTableEditor()
        result = editor.import_file(tmp_path / "nonexistent.csv")
        assert result is False
        assert "文件不存在" in editor.status_label.text()

    def test_editor_data_changed_signal(
        self, qapp: QApplication
    ) -> None:
        """data_changed 信号在加载时发射"""
        editor = VariableTableEditor()
        signals: list[int] = []
        editor.data_changed.connect(lambda: signals.append(1))
        editor.set_entries(_SAMPLE_ENTRIES)
        assert len(signals) >= 1
        editor._on_add_clicked()
        assert len(signals) >= 2
