"""SpecCenterView 规范中心全局页单元测试

测试内容：
- SpecCenterView 加载
- PLC 规范列表显示（4 项）
- Python 规范列表显示（3 项）
- "打开"按钮存在
- 点击"打开" → 调用 QDesktopServices.openUrl
- 规范文件不存在时按钮禁用

使用临时目录模拟规范文件，遵循项目现有 qapp fixture 模式。
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

# 必须在导入 PySide6 前设置离屏渲染，避免无显示环境报错
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QUrl  # noqa: E402
from PySide6.QtWidgets import QApplication, QGroupBox, QLabel, QPushButton  # noqa: E402

from auto_pm.ui.global_pages.spec_center import SpecCenterView  # noqa: E402

# ── fixtures ─────────────────────────────────────────────


def _create_spec_file(spec_dir: Path, code: str, name_suffix: str) -> Path:
    """在指定目录创建模拟规范文件

    Args:
        spec_dir: 规范目录
        code: 规范编号（如 905）
        name_suffix: 文件名后缀（如 SCL编程规范_LSP）

    Returns:
        创建的文件路径
    """
    spec_dir.mkdir(parents=True, exist_ok=True)
    file_path = spec_dir / f"{code}_{name_suffix}.md"
    file_path.write_text(f"# {code} 规范\n\n测试规范内容\n", encoding="utf-8")
    return file_path


@pytest.fixture
def spec_workspace(tmp_path: Path) -> Path:
    """临时工作空间，含 PLC 和 Python 规范文件

    目录结构：
        tmp_path/
        ├── 0100_PLC自动化/00_通用规范/PLC编程/
        │   ├── 905_SCL编程规范_LSP.md
        │   ├── 904_SCL注释规范_LSP.md
        │   ├── 903_定时器使用规范_LSP.md
        │   └── 906_错误预防规则_LSP.md
        └── 01_Project自动化项目管理/00_通用规范/Python开发/
            ├── 210_Python编程规范_DEV.md
            ├── 211_Python代码审查规范_DEV.md
            └── 220_Python项目打包规范_DEV.md
    """
    plc_dir = tmp_path / "0100_PLC自动化" / "00_通用规范" / "PLC编程"
    py_dir = tmp_path / "01_Project自动化项目管理" / "00_通用规范" / "Python开发"

    _create_spec_file(plc_dir, "905", "SCL编程规范_LSP")
    _create_spec_file(plc_dir, "904", "SCL注释规范_LSP")
    _create_spec_file(plc_dir, "903", "定时器使用规范_LSP")
    _create_spec_file(plc_dir, "906", "错误预防规则_LSP")

    _create_spec_file(py_dir, "210", "Python编程规范_DEV")
    _create_spec_file(py_dir, "211", "Python代码审查规范_DEV")
    _create_spec_file(py_dir, "220", "Python项目打包规范_DEV")

    return tmp_path


# ── SpecCenterView 加载测试 ─────────────────────────────


class TestSpecCenterViewLoad:
    """SpecCenterView 实例化与基础结构测试"""

    def test_instantiation(self, qapp: QApplication) -> None:
        """SpecCenterView 应能正常实例化"""
        view = SpecCenterView()
        assert view is not None
        assert view.objectName() == "specCenterPage"
        view.deleteLater()
        qapp.processEvents()

    def test_has_two_group_boxes(self, qapp: QApplication) -> None:
        """应包含 2 个分区（PLC 和 Python）"""
        view = SpecCenterView()
        groups = view.findChildren(QGroupBox)
        assert len(groups) == 2
        titles = [g.title() for g in groups]
        assert "PLC 技术栈规范" in titles
        assert "Python 技术栈规范" in titles
        view.deleteLater()
        qapp.processEvents()

    def test_title_label(self, qapp: QApplication) -> None:
        """应显示"规范中心"标题"""
        view = SpecCenterView()
        labels = view.findChildren(QLabel)
        texts = [label.text() for label in labels]
        assert "规范中心" in texts
        view.deleteLater()
        qapp.processEvents()


# ── PLC 规范列表测试 ────────────────────────────────────


class TestPlcSpecList:
    """PLC 技术栈规范列表显示测试"""

    def test_plc_has_four_specs(self, qapp: QApplication) -> None:
        """PLC 规范列表应显示 4 项"""
        view = SpecCenterView()
        plc_codes = ["905", "904", "903", "906"]
        for code in plc_codes:
            btn = view.get_open_button("plc", code)
            assert btn is not None, f"PLC 规范 {code} 的按钮不存在"
        view.deleteLater()
        qapp.processEvents()

    def test_plc_spec_codes_displayed(self, qapp: QApplication) -> None:
        """PLC 规范编号应正确显示"""
        view = SpecCenterView()
        labels = view.findChildren(QLabel)
        texts = [label.text() for label in labels]
        for code in ["905", "904", "903", "906"]:
            assert code in texts, f"PLC 规范编号 {code} 未显示"
        view.deleteLater()
        qapp.processEvents()

    def test_plc_spec_names_displayed(self, qapp: QApplication) -> None:
        """PLC 规范名称应正确显示"""
        view = SpecCenterView()
        labels = view.findChildren(QLabel)
        texts = [label.text() for label in labels]
        expected_names = [
            "SCL 编程规范",
            "SCL 注释规范",
            "定时器使用规范",
            "错误预防规则",
        ]
        for name in expected_names:
            assert name in texts, f"PLC 规范名称 '{name}' 未显示"
        view.deleteLater()
        qapp.processEvents()


# ── Python 规范列表测试 ─────────────────────────────────


class TestPythonSpecList:
    """Python 技术栈规范列表显示测试"""

    def test_python_has_three_specs(self, qapp: QApplication) -> None:
        """Python 规范列表应显示 3 项"""
        view = SpecCenterView()
        py_codes = ["210", "211", "220"]
        for code in py_codes:
            btn = view.get_open_button("python", code)
            assert btn is not None, f"Python 规范 {code} 的按钮不存在"
        view.deleteLater()
        qapp.processEvents()

    def test_python_spec_codes_displayed(self, qapp: QApplication) -> None:
        """Python 规范编号应正确显示"""
        view = SpecCenterView()
        labels = view.findChildren(QLabel)
        texts = [label.text() for label in labels]
        for code in ["210", "211", "220"]:
            assert code in texts, f"Python 规范编号 {code} 未显示"
        view.deleteLater()
        qapp.processEvents()

    def test_python_spec_names_displayed(self, qapp: QApplication) -> None:
        """Python 规范名称应正确显示"""
        view = SpecCenterView()
        labels = view.findChildren(QLabel)
        texts = [label.text() for label in labels]
        expected_names = [
            "Python 编程规范",
            "Python 代码审查规范",
            "Python 项目打包规范",
        ]
        for name in expected_names:
            assert name in texts, f"Python 规范名称 '{name}' 未显示"
        view.deleteLater()
        qapp.processEvents()


# ── "打开"按钮存在性测试 ───────────────────────────────


class TestOpenButtons:
    """"打开"按钮存在性测试"""

    def test_all_open_buttons_exist(self, qapp: QApplication) -> None:
        """所有规范项都应有"打开"按钮"""
        view = SpecCenterView()
        expected_buttons = [
            ("plc", "905"),
            ("plc", "904"),
            ("plc", "903"),
            ("plc", "906"),
            ("python", "210"),
            ("python", "211"),
            ("python", "220"),
        ]
        for stack, code in expected_buttons:
            btn = view.get_open_button(stack, code)
            assert btn is not None, f"{stack}/{code} 的按钮不存在"
            assert isinstance(btn, QPushButton)
            assert btn.text() == "打开"
        view.deleteLater()
        qapp.processEvents()

    def test_open_buttons_count(self, qapp: QApplication) -> None:
        """应有 7 个"打开"按钮（PLC 4 + Python 3）"""
        view = SpecCenterView()
        assert len(view.open_buttons) == 7
        view.deleteLater()
        qapp.processEvents()


# ── 规范文件查找测试 ───────────────────────────────────


class TestFindSpecFile:
    """规范文件查找逻辑测试"""

    def test_find_plc_spec_file(
        self, qapp: QApplication, spec_workspace: Path
    ) -> None:
        """应能找到 PLC 规范文件"""
        view = SpecCenterView(str(spec_workspace))
        path = view._find_spec_file("plc", "905")
        assert path != ""
        assert "905_" in os.path.basename(path)
        assert path.endswith(".md")
        view.deleteLater()
        qapp.processEvents()

    def test_find_python_spec_file(
        self, qapp: QApplication, spec_workspace: Path
    ) -> None:
        """应能找到 Python 规范文件"""
        view = SpecCenterView(str(spec_workspace))
        path = view._find_spec_file("python", "210")
        assert path != ""
        assert "210_" in os.path.basename(path)
        assert path.endswith(".md")
        view.deleteLater()
        qapp.processEvents()

    def test_find_spec_file_not_found(self, qapp: QApplication) -> None:
        """workspace_root 为空时应返回空字符串"""
        view = SpecCenterView("")
        path = view._find_spec_file("plc", "905")
        assert path == ""
        view.deleteLater()
        qapp.processEvents()

    def test_find_spec_file_invalid_stack(
        self, qapp: QApplication, spec_workspace: Path
    ) -> None:
        """无效技术栈应返回空字符串"""
        view = SpecCenterView(str(spec_workspace))
        path = view._find_spec_file("invalid", "905")
        assert path == ""
        view.deleteLater()
        qapp.processEvents()


# ── 按钮启用/禁用状态测试 ──────────────────────────────


class TestButtonState:
    """按钮启用/禁用状态测试"""

    def test_buttons_enabled_when_spec_exists(
        self, qapp: QApplication, spec_workspace: Path
    ) -> None:
        """规范文件存在时按钮应启用"""
        view = SpecCenterView(str(spec_workspace))
        for stack, code in [
            ("plc", "905"),
            ("plc", "904"),
            ("plc", "903"),
            ("plc", "906"),
            ("python", "210"),
            ("python", "211"),
            ("python", "220"),
        ]:
            btn = view.get_open_button(stack, code)
            assert btn is not None
            assert btn.isEnabled(), f"{stack}/{code} 按钮应启用"
        view.deleteLater()
        qapp.processEvents()

    def test_buttons_disabled_when_spec_missing(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """规范文件不存在时按钮应禁用"""
        # tmp_path 下没有规范文件
        view = SpecCenterView(str(tmp_path))
        for stack, code in [
            ("plc", "905"),
            ("python", "210"),
        ]:
            btn = view.get_open_button(stack, code)
            assert btn is not None
            assert not btn.isEnabled(), f"{stack}/{code} 按钮应禁用"
        view.deleteLater()
        qapp.processEvents()

    def test_buttons_disabled_when_workspace_empty(
        self, qapp: QApplication
    ) -> None:
        """workspace_root 为空时按钮应禁用"""
        view = SpecCenterView("")
        btn = view.get_open_button("plc", "905")
        assert btn is not None
        assert not btn.isEnabled()
        view.deleteLater()
        qapp.processEvents()


# ── 点击"打开"按钮测试 ─────────────────────────────────


class TestOpenSpecAction:
    """点击"打开"按钮调用 QDesktopServices.openUrl 测试"""

    def test_open_plc_spec_calls_open_url(
        self, qapp: QApplication, spec_workspace: Path
    ) -> None:
        """点击 PLC 规范"打开"按钮应调用 QDesktopServices.openUrl"""
        view = SpecCenterView(str(spec_workspace))
        expected_path = view._find_spec_file("plc", "905")
        assert expected_path != ""

        with patch(
            "auto_pm.ui.global_pages.spec_center.QDesktopServices.openUrl"
        ) as mock_open:
            view._on_open_spec("plc", "905")
            assert mock_open.called
            call_args = mock_open.call_args[0][0]
            assert isinstance(call_args, QUrl)
            # QUrl.toLocalFile() 在 Windows 上返回正斜杠路径，需规范化比较
            assert os.path.normpath(call_args.toLocalFile()) == os.path.normpath(
                expected_path
            )

        view.deleteLater()
        qapp.processEvents()

    def test_open_python_spec_calls_open_url(
        self, qapp: QApplication, spec_workspace: Path
    ) -> None:
        """点击 Python 规范"打开"按钮应调用 QDesktopServices.openUrl"""
        view = SpecCenterView(str(spec_workspace))
        expected_path = view._find_spec_file("python", "210")
        assert expected_path != ""

        with patch(
            "auto_pm.ui.global_pages.spec_center.QDesktopServices.openUrl"
        ) as mock_open:
            view._on_open_spec("python", "210")
            assert mock_open.called
            call_args = mock_open.call_args[0][0]
            assert isinstance(call_args, QUrl)
            # QUrl.toLocalFile() 在 Windows 上返回正斜杠路径，需规范化比较
            assert os.path.normpath(call_args.toLocalFile()) == os.path.normpath(
                expected_path
            )

        view.deleteLater()
        qapp.processEvents()

    def test_open_spec_not_called_when_file_missing(
        self, qapp: QApplication, tmp_path: Path
    ) -> None:
        """规范文件不存在时不应调用 openUrl"""
        view = SpecCenterView(str(tmp_path))

        with patch(
            "auto_pm.ui.global_pages.spec_center.QDesktopServices.openUrl"
        ) as mock_open:
            view._on_open_spec("plc", "905")
            assert not mock_open.called

        view.deleteLater()
        qapp.processEvents()

    def test_open_all_plc_specs(
        self, qapp: QApplication, spec_workspace: Path
    ) -> None:
        """点击所有 PLC 规范"打开"按钮都应调用 openUrl"""
        view = SpecCenterView(str(spec_workspace))

        with patch(
            "auto_pm.ui.global_pages.spec_center.QDesktopServices.openUrl"
        ) as mock_open:
            for code in ["905", "904", "903", "906"]:
                view._on_open_spec("plc", code)
            assert mock_open.call_count == 4

        view.deleteLater()
        qapp.processEvents()

    def test_open_all_python_specs(
        self, qapp: QApplication, spec_workspace: Path
    ) -> None:
        """点击所有 Python 规范"打开"按钮都应调用 openUrl"""
        view = SpecCenterView(str(spec_workspace))

        with patch(
            "auto_pm.ui.global_pages.spec_center.QDesktopServices.openUrl"
        ) as mock_open:
            for code in ["210", "211", "220"]:
                view._on_open_spec("python", code)
            assert mock_open.call_count == 3

        view.deleteLater()
        qapp.processEvents()

    def test_open_url_uses_local_file_url(
        self, qapp: QApplication, spec_workspace: Path
    ) -> None:
        """openUrl 应使用 QUrl.fromLocalFile 构造本地文件 URL"""
        view = SpecCenterView(str(spec_workspace))

        with patch(
            "auto_pm.ui.global_pages.spec_center.QDesktopServices.openUrl"
        ) as mock_open:
            view._on_open_spec("plc", "905")
            assert mock_open.called
            url = mock_open.call_args[0][0]
            # QUrl.fromLocalFile 构造的 URL 应为 file:// 协议
            assert url.toString().startswith("file:")

        view.deleteLater()
        qapp.processEvents()


# ── M4-Iter3：搜索/刷新/对比功能测试 ────────────────────


class TestSearchFunctionality:
    """搜索框功能测试（M4-Iter3）"""

    def test_search_box_exists(self, qapp: QApplication) -> None:
        """应包含搜索框"""
        view = SpecCenterView()
        assert view.search_box is not None
        assert view.search_box.placeholderText() == "搜索规范（编号/名称/技术栈）..."
        view.deleteLater()
        qapp.processEvents()

    def test_all_rows_visible_by_default(self, qapp: QApplication) -> None:
        """默认所有规范行可见"""
        view = SpecCenterView()
        for (stack, code), row in view.spec_rows.items():
            assert row.isHidden() is False, f"{stack}/{code} 应可见"
        view.deleteLater()
        qapp.processEvents()

    def test_search_filters_by_code(self, qapp: QApplication) -> None:
        """按编号搜索应过滤规范行"""
        view = SpecCenterView()
        view.search_box.setText("905")
        qapp.processEvents()

        # 仅 905 可见
        for (stack, code), row in view.spec_rows.items():
            if code == "905":
                assert row.isHidden() is False, f"{stack}/{code} 应可见"
            else:
                assert row.isHidden() is True, f"{stack}/{code} 应隐藏"

        view.deleteLater()
        qapp.processEvents()

    def test_search_filters_by_name(self, qapp: QApplication) -> None:
        """按名称搜索应过滤规范行（不区分大小写）"""
        view = SpecCenterView()
        view.search_box.setText("scl")
        qapp.processEvents()

        # 905 SCL 编程规范、904 SCL 注释规范 应可见
        visible_codes = {
            code for (stack, code), row in view.spec_rows.items()
            if not row.isHidden()
        }
        assert "905" in visible_codes
        assert "904" in visible_codes
        assert "903" not in visible_codes

        view.deleteLater()
        qapp.processEvents()

    def test_search_filters_by_stack(self, qapp: QApplication) -> None:
        """按技术栈搜索应过滤规范行"""
        view = SpecCenterView()
        view.search_box.setText("plc")
        qapp.processEvents()

        # PLC 4 项可见，Python 3 项隐藏
        for (stack, code), row in view.spec_rows.items():
            if stack == "plc":
                assert row.isHidden() is False
            else:
                assert row.isHidden() is True

        view.deleteLater()
        qapp.processEvents()

    def test_search_clear_restores_all(self, qapp: QApplication) -> None:
        """清空搜索框应恢复所有规范行"""
        view = SpecCenterView()
        view.search_box.setText("905")
        qapp.processEvents()
        view.search_box.setText("")
        qapp.processEvents()

        for (stack, code), row in view.spec_rows.items():
            assert row.isHidden() is False

        view.deleteLater()
        qapp.processEvents()

    def test_search_no_match_hides_all(self, qapp: QApplication) -> None:
        """无匹配时应隐藏所有规范行"""
        view = SpecCenterView()
        view.search_box.setText("不存在的关键词")
        qapp.processEvents()

        for (stack, code), row in view.spec_rows.items():
            assert row.isHidden() is True

        view.deleteLater()
        qapp.processEvents()


class TestRefreshFunctionality:
    """刷新按钮功能测试（M4-Iter3）"""

    def test_refresh_button_exists(self, qapp: QApplication) -> None:
        """应包含刷新按钮"""
        view = SpecCenterView()
        assert view.refresh_button is not None
        assert view.refresh_button.text() == "刷新"
        view.deleteLater()
        qapp.processEvents()

    def test_refresh_updates_button_state(
        self, qapp: QApplication, spec_workspace: Path
    ) -> None:
        """刷新应更新按钮启用状态"""
        view = SpecCenterView(str(spec_workspace))
        # 初始所有按钮应启用（规范文件存在）
        for (stack, code), btn in view.open_buttons.items():
            assert btn.isEnabled() is True

        # 删除一个规范文件
        plc_dir = spec_workspace / "0100_PLC自动化" / "00_通用规范" / "PLC编程"
        for f in plc_dir.glob("905_*.md"):
            f.unlink()

        # 刷新后 905 按钮应禁用
        view._on_refresh()
        qapp.processEvents()
        assert view.get_open_button("plc", "905").isEnabled() is False

        view.deleteLater()
        qapp.processEvents()

    def test_refresh_without_workspace_logs_warning(
        self, qapp: QApplication
    ) -> None:
        """无 workspace_root 时刷新应记录警告"""
        view = SpecCenterView()
        # 不应抛异常
        view._on_refresh()
        view.deleteLater()
        qapp.processEvents()


class TestCompareFunctionality:
    """对比按钮功能测试（M4-Iter3）"""

    def test_compare_button_exists(self, qapp: QApplication) -> None:
        """应包含对比按钮"""
        view = SpecCenterView()
        assert view.compare_button is not None
        assert view.compare_button.text() == "对比"
        # 默认禁用
        assert view.compare_button.isEnabled() is False
        view.deleteLater()
        qapp.processEvents()

    def test_select_button_exists(self, qapp: QApplication) -> None:
        """每个规范行应包含选择按钮"""
        view = SpecCenterView()
        for (stack, code) in view.spec_rows.keys():
            btn = view.get_select_button(stack, code)
            assert btn is not None, f"{stack}/{code} 的选择按钮不存在"
            assert btn.text() == "选择"
            assert btn.isCheckable() is True
        view.deleteLater()
        qapp.processEvents()

    def test_select_one_does_not_enable_compare(
        self, qapp: QApplication
    ) -> None:
        """选择 1 个规范不启用对比按钮"""
        view = SpecCenterView()
        btn = view.get_select_button("plc", "905")
        btn.setChecked(True)
        view._on_select_for_compare("plc", "905")
        assert view.compare_button.isEnabled() is False
        view.deleteLater()
        qapp.processEvents()

    def test_select_two_enables_compare(
        self, qapp: QApplication
    ) -> None:
        """选择 2 个规范启用对比按钮"""
        view = SpecCenterView()
        view.get_select_button("plc", "905").setChecked(True)
        view._on_select_for_compare("plc", "905")
        view.get_select_button("python", "210").setChecked(True)
        view._on_select_for_compare("python", "210")
        assert view.compare_button.isEnabled() is True
        view.deleteLater()
        qapp.processEvents()

    def test_select_three_keeps_only_two(
        self, qapp: QApplication
    ) -> None:
        """选择第 3 个规范时取消新选择"""
        view = SpecCenterView()
        view.get_select_button("plc", "905").setChecked(True)
        view._on_select_for_compare("plc", "905")
        view.get_select_button("python", "210").setChecked(True)
        view._on_select_for_compare("python", "210")
        # 尝试选择第 3 个
        view.get_select_button("python", "211").setChecked(True)
        view._on_select_for_compare("python", "211")
        # 第 3 个应被取消
        assert view.get_select_button("python", "211").isChecked() is False
        assert view.compare_button.isEnabled() is True
        view.deleteLater()
        qapp.processEvents()

    def test_deselect_disables_compare(
        self, qapp: QApplication
    ) -> None:
        """取消选择后对比按钮禁用"""
        view = SpecCenterView()
        view.get_select_button("plc", "905").setChecked(True)
        view._on_select_for_compare("plc", "905")
        view.get_select_button("python", "210").setChecked(True)
        view._on_select_for_compare("python", "210")
        assert view.compare_button.isEnabled() is True

        # 取消一个
        view.get_select_button("python", "210").setChecked(False)
        view._on_select_for_compare("python", "210")
        assert view.compare_button.isEnabled() is False

        view.deleteLater()
        qapp.processEvents()


class TestIndexServiceIntegration:
    """SpecIndexService 集成测试（M4-Iter3）"""

    def test_index_service_exists(self, qapp: QApplication) -> None:
        """应包含 SpecIndexService 实例"""
        view = SpecCenterView()
        assert view.index_service is not None
        view.deleteLater()
        qapp.processEvents()

    def test_set_workspace_root_updates_service(
        self, qapp: QApplication, spec_workspace: Path
    ) -> None:
        """set_workspace_root 应更新索引服务"""
        view = SpecCenterView()
        assert view.index_service.workspace_root == ""

        view.set_workspace_root(str(spec_workspace))
        assert view.index_service.workspace_root == os.path.abspath(str(spec_workspace))

        view.deleteLater()
        qapp.processEvents()

    def test_spec_rows_property(self, qapp: QApplication) -> None:
        """spec_rows 属性应包含所有规范行"""
        view = SpecCenterView()
        assert len(view.spec_rows) == 7  # 4 PLC + 3 Python
        for (stack, code) in [("plc", "905"), ("python", "210")]:
            assert (stack, code) in view.spec_rows
        view.deleteLater()
        qapp.processEvents()

    def test_get_spec_row(self, qapp: QApplication) -> None:
        """get_spec_row 应返回指定规范行"""
        view = SpecCenterView()
        row = view.get_spec_row("plc", "905")
        assert row is not None
        assert row.isHidden() is False
        view.deleteLater()
        qapp.processEvents()
