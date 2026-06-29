"""VartableTab 单元测试（M4-Iter1）

验证变量表 Tab 的扫描和加载功能。
"""

from __future__ import annotations

from pathlib import Path

import pytest

# 跳过 GUI 测试如果 PySide6 不可用
pytest.importorskip("PySide6")

from auto_pm.ui.workspace.vartable_tab import VartableTab


class TestVartableTab:
    """VartableTab 测试"""

    def test_vartable_tab_creation(self, qapp) -> None:
        """创建 VartableTab"""
        tab = VartableTab()
        assert tab is not None

    def test_set_project_path_empty(self, qapp, tmp_path: Path) -> None:
        """设置空项目路径"""
        tab = VartableTab()
        tab.set_project_path("")
        # 不应崩溃，状态应为未加载
        assert "未加载" in tab._status_label.text() or "无效" in tab._status_label.text()

    def test_set_project_path_no_vartable(self, qapp, tmp_path: Path) -> None:
        """设置无变量表的项目路径"""
        project_dir = tmp_path / "DJ-2026-001_项目"
        project_dir.mkdir()

        tab = VartableTab()
        tab.set_project_path(str(project_dir))
        assert "未找到" in tab._status_label.text()

    def test_set_project_path_with_vartable(self, qapp, tmp_path: Path) -> None:
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

    def test_vartable_tab_refresh(self, qapp, tmp_path: Path) -> None:
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

    def test_vartable_tab_invalid_csv(self, qapp, tmp_path: Path) -> None:
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
