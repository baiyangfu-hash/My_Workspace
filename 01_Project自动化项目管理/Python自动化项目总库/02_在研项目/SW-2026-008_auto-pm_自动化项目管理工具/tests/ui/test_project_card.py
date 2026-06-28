"""ProjectCard 项目卡片单元测试

测试内容：
- 构造函数填充数据正确（向后兼容 ProjectInfo + change_count）
- set_project(ProjectCardDTO) 填充数据正确
- set_project_info(ProjectInfo, change_count) 填充数据正确
- 变更数显示（0 → "变更: 0"，N>0 → "变更: N 活跃"）
- 修改时间格式化（正常时间戳 / file_mtime=0 → "—"）
- 描述摘要截断（长文本加省略号 / 短文本不变 / 空描述隐藏）
- 点击信号 clicked(project_id) 发射
- 不同 stack/phase 的徽标颜色
- 右键菜单信号 editRequested / deleteRequested

遵循项目现有测试模式：自定义 qapp fixture + QT_QPA_PLATFORM=offscreen。
"""

from __future__ import annotations

import os
from datetime import datetime

import pytest

# 必须在导入 PySide6 前设置离屏渲染，避免无显示环境报错
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from auto_pm.models import ProjectCardDTO, ProjectInfo  # noqa: E402
from auto_pm.ui.project_list import ProjectCard  # noqa: E402
from auto_pm.ui.project_list.project_card import (  # noqa: E402
    _format_change_count,
    _format_mtime,
    _truncate_description,
)


def _make_project(
    project_id: str = "SW-2026-008",
    name: str = "测试项目",
    stack: str = "python",
    phase: str = "developing",
    description: str = "卡片测试项目",
    file_mtime: float = 0.0,
    version: str = "V1.0.0",
) -> ProjectInfo:
    """构造测试用 ProjectInfo"""
    return ProjectInfo(
        project_id=project_id,
        name=name,
        path=f"/tmp/{project_id}",
        stack=stack,
        version=version,
        description=description,
        source="copier",
        phase=phase,
        file_mtime=file_mtime,
    )


def _make_dto(
    project_id: str = "DJ-2026-005",
    name: str = "输送线自动化项目",
    stack: str = "plc",
    phase: str = "commissioning",
    description: str = "输送线自动化项目描述",
    file_mtime: float = 0.0,
    change_count: int = 5,
    version: str = "v2.1",
) -> ProjectCardDTO:
    """构造测试用 ProjectCardDTO"""
    return ProjectCardDTO(
        project_id=project_id,
        name=name,
        stack=stack,
        phase=phase,
        version=version,
        business_line="",
        change_count=change_count,
        path=f"/tmp/{project_id}",
        file_mtime=file_mtime,
        description=description,
    )


# ── 纯函数测试 ───────────────────────────────────────────


class TestFormatHelpers:
    """格式化辅助函数测试"""

    def test_format_mtime_zero(self) -> None:
        """file_mtime=0 应返回占位符 '—'"""
        assert _format_mtime(0.0) == "—"

    def test_format_mtime_negative(self) -> None:
        """file_mtime 为负应返回占位符 '—'"""
        assert _format_mtime(-1.0) == "—"

    def test_format_mtime_normal(self) -> None:
        """正常时间戳应格式化为 YYYY-MM-DD"""
        ts = datetime(2026, 6, 15, 12, 0, 0).timestamp()
        assert _format_mtime(ts) == "2026-06-15"

    def test_format_change_count_zero(self) -> None:
        """变更数为 0 应显示 '变更: 0'"""
        assert _format_change_count(0) == "变更: 0"

    def test_format_change_count_active(self) -> None:
        """变更数 >0 应追加 '活跃' 标记"""
        assert _format_change_count(5) == "变更: 5 活跃"
        assert _format_change_count(1) == "变更: 1 活跃"

    def test_truncate_description_short(self) -> None:
        """短描述应原样返回（折叠空白后）"""
        assert _truncate_description("短描述") == "短描述"

    def test_truncate_description_empty(self) -> None:
        """空描述应返回空字符串"""
        assert _truncate_description("") == ""
        assert _truncate_description("   ") == ""

    def test_truncate_description_long(self) -> None:
        """超长描述应截断并追加省略号"""
        long_desc = "甲" * 200
        result = _truncate_description(long_desc)
        assert result.endswith("…")
        assert len(result) == 81  # 80 + 省略号

    def test_truncate_description_collapses_whitespace(self) -> None:
        """描述中的换行/多余空白应折叠为单空格"""
        desc = "第一行\n第二行\n\n第三行"
        assert _truncate_description(desc) == "第一行 第二行 第三行"


# ── 构造函数与数据填充测试 ───────────────────────────────


class TestProjectCardConstruction:
    """ProjectCard 构造与数据填充测试"""

    def test_instantiation(self, qapp: QApplication) -> None:
        """ProjectCard 应能正常实例化（向后兼容 ProjectInfo + change_count）"""
        proj = _make_project("SW-2026-008", "测试项目", "python")
        card = ProjectCard(proj, change_count=3)
        assert card is not None
        assert card.project.project_id == "SW-2026-008"
        assert card.change_count == 3
        card.deleteLater()
        qapp.processEvents()

    def test_constructor_fills_fields(self, qapp: QApplication) -> None:
        """构造函数应正确填充各显示字段"""
        ts = datetime(2026, 6, 15, 12, 0, 0).timestamp()
        proj = _make_project(
            "DJ-2026-005",
            "输送线自动化项目",
            "plc",
            "commissioning",
            description="输送线项目",
            file_mtime=ts,
            version="v2.1",
        )
        card = ProjectCard(proj, change_count=5)

        assert card._title_label.text() == "输送线自动化项目"
        assert card._id_label.text() == "DJ-2026-005"
        assert card._stack_badge.text() == "PLC"
        assert card._bl_label.text() == "单机"  # DJ → 单机
        assert card._version_label.text() == "v2.1"  # 无前缀补 v
        assert card._phase_badge.text() == "调试中"
        assert card._change_label.text() == "变更: 5 活跃"
        assert card._mtime_label.text() == "修改: 2026-06-15"
        assert card._desc_label.text() == "输送线项目"
        assert card._desc_label.isVisibleTo(card) is True
        card.deleteLater()
        qapp.processEvents()

    def test_set_project_info_updates_fields(self, qapp: QApplication) -> None:
        """set_project_info 应更新卡片字段"""
        proj1 = _make_project("SW-2026-001", "项目A", "python", "developing")
        card = ProjectCard(proj1, change_count=0)
        assert card._title_label.text() == "项目A"
        assert card._change_label.text() == "变更: 0"

        ts = datetime(2026, 1, 10, 0, 0, 0).timestamp()
        proj2 = _make_project(
            "ZD-2026-002",
            "项目B",
            "plc",
            "production",
            description="更新后描述",
            file_mtime=ts,
        )
        card.set_project_info(proj2, change_count=7)

        assert card.project.project_id == "ZD-2026-002"
        assert card.change_count == 7
        assert card._title_label.text() == "项目B"
        assert card._id_label.text() == "ZD-2026-002"
        assert card._stack_badge.text() == "PLC"
        assert card._phase_badge.text() == "生产中"
        assert card._change_label.text() == "变更: 7 活跃"
        assert card._mtime_label.text() == "修改: 2026-01-10"
        card.deleteLater()
        qapp.processEvents()

    def test_set_project_dto_fills_fields(self, qapp: QApplication) -> None:
        """set_project(ProjectCardDTO) 应正确填充字段"""
        ts = datetime(2026, 6, 15, 12, 0, 0).timestamp()
        dto = _make_dto(
            "DJ-2026-005",
            "输送线自动化项目",
            "plc",
            "commissioning",
            description="DTO 描述",
            file_mtime=ts,
            change_count=5,
            version="v2.1",
        )
        card = ProjectCard(_make_project(), change_count=0)
        card.set_project(dto)

        assert card._title_label.text() == "输送线自动化项目"
        assert card._id_label.text() == "DJ-2026-005"
        assert card._stack_badge.text() == "PLC"
        assert card._phase_badge.text() == "调试中"
        assert card._change_label.text() == "变更: 5 活跃"
        assert card._mtime_label.text() == "修改: 2026-06-15"
        assert card._desc_label.text() == "DTO 描述"
        assert card.change_count == 5
        card.deleteLater()
        qapp.processEvents()


# ── 变更数显示测试 ───────────────────────────────────────


class TestChangeCountDisplay:
    """变更数显示测试"""

    def test_zero_change_count(self, qapp: QApplication) -> None:
        """change_count=0 应显示 '变更: 0'"""
        card = ProjectCard(_make_project(), change_count=0)
        assert card._change_label.text() == "变更: 0"
        card.deleteLater()
        qapp.processEvents()

    def test_positive_change_count(self, qapp: QApplication) -> None:
        """change_count>0 应显示 '变更: N 活跃'"""
        card = ProjectCard(_make_project(), change_count=12)
        assert card._change_label.text() == "变更: 12 活跃"
        card.deleteLater()
        qapp.processEvents()


# ── 修改时间格式化测试 ───────────────────────────────────


class TestMtimeDisplay:
    """修改时间格式化测试"""

    def test_mtime_zero_shows_placeholder(self, qapp: QApplication) -> None:
        """file_mtime=0 应显示 '修改: —'"""
        proj = _make_project(file_mtime=0.0)
        card = ProjectCard(proj)
        assert card._mtime_label.text() == "修改: —"
        card.deleteLater()
        qapp.processEvents()

    def test_mtime_normal_format(self, qapp: QApplication) -> None:
        """正常 file_mtime 应格式化为 '修改: YYYY-MM-DD'"""
        ts = datetime(2026, 6, 15, 8, 30, 0).timestamp()
        proj = _make_project(file_mtime=ts)
        card = ProjectCard(proj)
        assert card._mtime_label.text() == "修改: 2026-06-15"
        card.deleteLater()
        qapp.processEvents()

    def test_mtime_default_zero(self, qapp: QApplication) -> None:
        """未设置 file_mtime（默认 0）应显示占位符"""
        proj = ProjectInfo(
            project_id="SW-2026-008",
            name="无时间项目",
            path="/tmp",
            stack="python",
        )
        card = ProjectCard(proj)
        assert card._mtime_label.text() == "修改: —"
        card.deleteLater()
        qapp.processEvents()


# ── 描述摘要截断测试 ─────────────────────────────────────


class TestDescriptionDisplay:
    """描述摘要显示与截断测试"""

    def test_short_description_shown(self, qapp: QApplication) -> None:
        """短描述应完整显示且可见"""
        proj = _make_project(description="这是一个短描述")
        card = ProjectCard(proj)
        assert card._desc_label.text() == "这是一个短描述"
        assert card._desc_label.isVisibleTo(card) is True
        card.deleteLater()
        qapp.processEvents()

    def test_empty_description_hidden(self, qapp: QApplication) -> None:
        """空描述应隐藏描述标签"""
        proj = _make_project(description="")
        card = ProjectCard(proj)
        assert card._desc_label.text() == ""
        assert card._desc_label.isVisibleTo(card) is False
        card.deleteLater()
        qapp.processEvents()

    def test_long_description_truncated(self, qapp: QApplication) -> None:
        """超长描述应被截断并追加省略号"""
        long_desc = "自动化输送线项目的详细描述内容" * 20
        proj = _make_project(description=long_desc)
        card = ProjectCard(proj)
        text = card._desc_label.text()
        assert text.endswith("…")
        assert len(text) <= 81  # 80 字符 + 省略号
        assert card._desc_label.isVisibleTo(card) is True
        card.deleteLater()
        qapp.processEvents()

    def test_multiline_description_collapsed(self, qapp: QApplication) -> None:
        """多行描述应折叠为单行（换行变空格）"""
        proj = _make_project(description="第一行\n第二行\n第三行")
        card = ProjectCard(proj)
        assert card._desc_label.text() == "第一行 第二行 第三行"
        card.deleteLater()
        qapp.processEvents()


# ── 信号测试 ─────────────────────────────────────────────


class TestProjectCardSignals:
    """ProjectCard 信号测试"""

    def test_clicked_signal_emission(self, qapp: QApplication) -> None:
        """clicked 信号应能正确发射 project_id"""
        proj = _make_project("SW-2026-008", "测试项目")
        card = ProjectCard(proj)

        received: list[str] = []
        card.clicked.connect(received.append)
        card.clicked.emit("SW-2026-008")

        assert received == ["SW-2026-008"]
        card.deleteLater()
        qapp.processEvents()

    def test_edit_signal_emission(self, qapp: QApplication) -> None:
        """editRequested 信号应能正确发射"""
        proj = _make_project("DJ-2026-001", "编辑测试")
        card = ProjectCard(proj)

        received: list[str] = []
        card.editRequested.connect(received.append)
        card.editRequested.emit("DJ-2026-001")

        assert received == ["DJ-2026-001"]
        card.deleteLater()
        qapp.processEvents()

    def test_delete_signal_emission(self, qapp: QApplication) -> None:
        """deleteRequested 信号应能正确发射"""
        proj = _make_project("DJ-2026-002", "删除测试")
        card = ProjectCard(proj)

        received: list[str] = []
        card.deleteRequested.connect(received.append)
        card.deleteRequested.emit("DJ-2026-002")

        assert received == ["DJ-2026-002"]
        card.deleteLater()
        qapp.processEvents()

    def test_clicked_emits_current_project_id(self, qapp: QApplication) -> None:
        """set_project_info 后 clicked 应发射最新 project_id"""
        card = ProjectCard(_make_project("SW-2026-001", "A"))
        received: list[str] = []
        card.clicked.connect(received.append)

        card.set_project_info(_make_project("ZD-2026-999", "B"))
        card.clicked.emit(card.project.project_id)

        assert received == ["ZD-2026-999"]
        card.deleteLater()
        qapp.processEvents()


# ── 徽标颜色测试 ─────────────────────────────────────────


class TestBadgeColors:
    """技术栈/阶段徽标颜色测试"""

    def test_stack_badge_plc_blue(self, qapp: QApplication) -> None:
        """PLC 技术栈徽标应为蓝色背景"""
        card = ProjectCard(_make_project(stack="plc"))
        assert card._stack_badge.text() == "PLC"
        assert "#4a90d9" in card._stack_badge.styleSheet()
        card.deleteLater()
        qapp.processEvents()

    def test_stack_badge_python_green(self, qapp: QApplication) -> None:
        """Python 技术栈徽标应为绿色背景"""
        card = ProjectCard(_make_project(stack="python"))
        assert card._stack_badge.text() == "Python"
        assert "#27ae60" in card._stack_badge.styleSheet()
        card.deleteLater()
        qapp.processEvents()

    def test_stack_badge_unknown_gray(self, qapp: QApplication) -> None:
        """unknown 技术栈徽标应为灰色背景"""
        card = ProjectCard(_make_project(stack="unknown"))
        assert card._stack_badge.text() == "未分类"
        assert "#95a5a6" in card._stack_badge.styleSheet()
        card.deleteLater()
        qapp.processEvents()

    def test_phase_badge_developing_blue(self, qapp: QApplication) -> None:
        """开发中阶段徽标应为蓝色"""
        card = ProjectCard(_make_project(phase="developing"))
        assert card._phase_badge.text() == "开发中"
        assert "#4a90d9" in card._phase_badge.styleSheet()
        card.deleteLater()
        qapp.processEvents()

    def test_phase_badge_commissioning_yellow(self, qapp: QApplication) -> None:
        """调试中阶段徽标应为黄/橙色"""
        card = ProjectCard(_make_project(phase="commissioning"))
        assert card._phase_badge.text() == "调试中"
        assert "#f39c12" in card._phase_badge.styleSheet()
        card.deleteLater()
        qapp.processEvents()

    def test_phase_badge_production_green(self, qapp: QApplication) -> None:
        """生产中阶段徽标应为绿色"""
        card = ProjectCard(_make_project(phase="production"))
        assert card._phase_badge.text() == "生产中"
        assert "#27ae60" in card._phase_badge.styleSheet()
        card.deleteLater()
        qapp.processEvents()

    def test_phase_badge_archived_gray(self, qapp: QApplication) -> None:
        """已归档阶段徽标应为灰色"""
        card = ProjectCard(_make_project(phase="archived"))
        assert card._phase_badge.text() == "已归档"
        assert "#95a5a6" in card._phase_badge.styleSheet()
        card.deleteLater()
        qapp.processEvents()

    def test_phase_badge_empty_fallback(self, qapp: QApplication) -> None:
        """未设置阶段应回退为 '未设置' 文本（无彩色背景）"""
        card = ProjectCard(_make_project(phase=""))
        assert card._phase_badge.text() == "未设置"
        # 回退样式不应包含彩色背景
        assert "#4a90d9" not in card._phase_badge.styleSheet()
        assert "#27ae60" not in card._phase_badge.styleSheet()
        card.deleteLater()
        qapp.processEvents()

    def test_all_phases_have_correct_label_and_color(self, qapp: QApplication) -> None:
        """所有合法阶段应有正确文案与颜色（全覆盖）"""
        expected = {
            "developing": ("开发中", "#4a90d9"),
            "commissioning": ("调试中", "#f39c12"),
            "production": ("生产中", "#27ae60"),
            "archived": ("已归档", "#95a5a6"),
        }
        for phase, (label, color) in expected.items():
            card = ProjectCard(_make_project(phase=phase))
            assert card._phase_badge.text() == label
            assert color in card._phase_badge.styleSheet()
            card.deleteLater()
            qapp.processEvents()


# ── 业务线标签测试 ───────────────────────────────────────


class TestBusinessLineLabel:
    """业务线标签测试"""

    def test_business_line_from_project_id(self, qapp: QApplication) -> None:
        """业务线应从项目编号提取并显示中文标签"""
        cases = [
            ("SW-2026-001", "软件"),
            ("DJ-2026-002", "单机"),
            ("ZD-2026-003", "整线"),
            ("XT-2026-004", "升级"),
            ("WX-2026-005", "维保"),
        ]
        for project_id, expected_label in cases:
            card = ProjectCard(_make_project(project_id=project_id))
            assert card._bl_label.text() == expected_label
            assert card._bl_label.isVisibleTo(card) is True
            card.deleteLater()
            qapp.processEvents()

    def test_business_line_hidden_when_unrecognized(self, qapp: QApplication) -> None:
        """无法识别业务线时标签应隐藏"""
        # 项目编号不符合 XX-YYYY-NNN 格式
        proj = ProjectInfo(
            project_id="UNKNOWN",
            name="无业务线",
            path="/tmp",
            stack="python",
        )
        card = ProjectCard(proj)
        assert card._bl_label.isVisibleTo(card) is False
        card.deleteLater()
        qapp.processEvents()


# ── 版本显示测试 ─────────────────────────────────────────


class TestVersionDisplay:
    """版本号显示测试"""

    def test_version_without_prefix_gets_v(self, qapp: QApplication) -> None:
        """无前缀版本号应补 'v' 前缀"""
        proj = _make_project(version="2.1")
        card = ProjectCard(proj)
        assert card._version_label.text() == "v2.1"
        card.deleteLater()
        qapp.processEvents()

    def test_version_with_uppercase_v_kept(self, qapp: QApplication) -> None:
        """已有 'V' 前缀的版本号应原样显示"""
        proj = _make_project(version="V1.0.0")
        card = ProjectCard(proj)
        assert card._version_label.text() == "V1.0.0"
        card.deleteLater()
        qapp.processEvents()

    def test_version_with_lowercase_v_kept(self, qapp: QApplication) -> None:
        """已有 'v' 前缀的版本号应原样显示"""
        proj = _make_project(version="v2.1")
        card = ProjectCard(proj)
        assert card._version_label.text() == "v2.1"
        card.deleteLater()
        qapp.processEvents()

    def test_version_empty_shows_placeholder(self, qapp: QApplication) -> None:
        """空版本号应显示占位符 '—'"""
        proj = _make_project(version="")
        card = ProjectCard(proj)
        assert card._version_label.text() == "—"
        card.deleteLater()
        qapp.processEvents()
