"""全局功能页 - 规范中心

展示 PLC 和 Python 技术栈的规范目录列表，点击"打开"按钮调用系统默认程序打开规范文件。

布局：
┌─────────────────────────────────────────────────────────┐
│ 规范中心                                                  │
├─────────────────────────────────────────────────────────┤
│ [搜索框]                                  [刷新] [对比]  │
├─────────────────────────────────────────────────────────┤
│ ┌─ PLC 技术栈规范 ──────────────────────────────────┐  │
│ │ 905  SCL 编程规范                          [打开] │  │
│ │ 904  SCL 注释规范                          [打开] │  │
│ │ 903  定时器使用规范                        [打开] │  │
│ │ 906  错误预防规则                          [打开] │  │
│ └────────────────────────────────────────────────────┘  │
│ ┌─ Python 技术栈规范 ────────────────────────────────┐  │
│ │ 210  Python 编程规范                       [打开] │  │
│ │ 211  Python 代码审查规范                   [打开] │  │
│ │ 220  Python 项目打包规范                   [打开] │  │
│ └────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘

M4-Iter3：增加搜索框（实时过滤）、刷新按钮（重建索引）、对比按钮（对比两个规范）。
"""

from __future__ import annotations

import glob
import os

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from auto_pm.core.spec_index_service import SpecDiffResult, SpecIndexService
from auto_pm.logging.logging import setup_logger

log = setup_logger(log_level="INFO", app_name="auto_pm")

__all__ = ["SpecCenterView"]

# ── 规范数据（硬编码，规范目录结构固定） ──────────────

# PLC 技术栈规范：(编号, 名称)
_PLC_SPECS: list[tuple[str, str]] = [
    ("905", "SCL 编程规范"),
    ("904", "SCL 注释规范"),
    ("903", "定时器使用规范"),
    ("906", "错误预防规则"),
]

# Python 技术栈规范：(编号, 名称)
_PYTHON_SPECS: list[tuple[str, str]] = [
    ("210", "Python 编程规范"),
    ("211", "Python 代码审查规范"),
    ("220", "Python 项目打包规范"),
]

# 技术栈 → (分区标题, 规范目录相对路径, 规范列表)
_STACK_SPECS: dict[str, tuple[str, str, list[tuple[str, str]]]] = {
    "plc": (
        "PLC 技术栈规范",
        os.path.join("0100_PLC自动化", "00_通用规范", "PLC编程"),
        _PLC_SPECS,
    ),
    "python": (
        "Python 技术栈规范",
        os.path.join("01_Project自动化项目管理", "00_通用规范", "Python开发"),
        _PYTHON_SPECS,
    ),
}

# ── 样式 ─────────────────────────────────────────────────

_PAGE_STYLE = """
QWidget#specCenterPage { background: #fafafa; }
QLabel#specTitle { font-size: 18px; font-weight: bold; color: #222; }
QLabel#specSubtitle { font-size: 12px; color: #999; }
QGroupBox#specGroup {
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    margin-top: 14px;
    font-size: 13px;
    font-weight: bold;
    color: #333;
}
QGroupBox#specGroup::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 8px;
    color: #4a90d9;
}
QLabel#specCode { font-size: 13px; font-weight: bold; color: #4a90d9; }
QLabel#specName { font-size: 13px; color: #333; }
QPushButton#openBtn {
    background: #4a90d9;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 4px 12px;
    font-size: 12px;
}
QPushButton#openBtn:hover { background: #3a7bc8; }
QPushButton#openBtn:disabled { background: #cccccc; color: #888; }
QPushButton#toolBtn {
    background: #f5f5f5;
    color: #333;
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    padding: 4px 12px;
    font-size: 12px;
}
QPushButton#toolBtn:hover { background: #e8e8e8; }
QPushButton#toolBtn:disabled { background: #f5f5f5; color: #aaa; }
QLineEdit#searchBox {
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
}
"""


class SpecCenterView(QWidget):
    """规范中心全局页

    展示 PLC 和 Python 技术栈的规范目录列表，点击"打开"按钮调用系统默认程序打开规范文件。

    规范文件路径查找：
        - PLC: {workspace_root}/0100_PLC自动化/00_通用规范/PLC编程/{code}_*.md
        - Python: {workspace_root}/01_Project自动化项目管理/00_通用规范/Python开发/{code}_*.md
    若找不到规范文件，对应"打开"按钮禁用。

    M4-Iter3 扩展：
        - 搜索框：实时过滤规范列表（按编号/名称/技术栈匹配，不区分大小写）
        - 刷新按钮：重建规范索引
        - 对比按钮：对比两个已选规范的文件内容
    """

    def __init__(
        self,
        workspace_root: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._workspace_root = workspace_root
        self._open_buttons: dict[tuple[str, str], QPushButton] = {}
        # M4-Iter3：规范行容器，用于搜索过滤
        self._spec_rows: dict[tuple[str, str], QWidget] = {}
        # M4-Iter3：规范选择状态（用于对比）
        self._selected_for_compare: set[tuple[str, str]] = set()
        # M4-Iter3：规范索引服务
        self._index_service = SpecIndexService(workspace_root)
        self._build_ui()

    # ── UI 构建 ────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.setObjectName("specCenterPage")
        self.setStyleSheet(_PAGE_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        # 标题
        title = QLabel("规范中心")
        title.setObjectName("specTitle")
        layout.addWidget(title)

        subtitle = QLabel("PLC 与 Python 技术栈规范目录")
        subtitle.setObjectName("specSubtitle")
        layout.addWidget(subtitle)

        # M4-Iter3：工具栏（搜索框 + 刷新 + 对比）
        toolbar = self._build_toolbar()
        layout.addWidget(toolbar)

        # 两个技术栈分区
        for stack_key, (group_title, _, specs) in _STACK_SPECS.items():
            group = self._build_spec_group(stack_key, group_title, specs)
            layout.addWidget(group)

        layout.addStretch(1)

    def _build_toolbar(self) -> QWidget:
        """构建工具栏：搜索框 + 刷新按钮 + 对比按钮"""
        toolbar = QWidget()
        h = QHBoxLayout(toolbar)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(8)

        # 搜索框
        self._search_box = QLineEdit()
        self._search_box.setObjectName("searchBox")
        self._search_box.setPlaceholderText("搜索规范（编号/名称/技术栈）...")
        self._search_box.textChanged.connect(self._on_search_changed)
        h.addWidget(self._search_box, 1)

        # 刷新按钮
        self._refresh_btn = QPushButton("刷新")
        self._refresh_btn.setObjectName("toolBtn")
        self._refresh_btn.clicked.connect(self._on_refresh)
        h.addWidget(self._refresh_btn)

        # 对比按钮
        self._compare_btn = QPushButton("对比")
        self._compare_btn.setObjectName("toolBtn")
        self._compare_btn.clicked.connect(self._on_compare)
        self._compare_btn.setEnabled(False)  # 需选择 2 个规范后启用
        h.addWidget(self._compare_btn)

        return toolbar

    def _build_spec_group(
        self,
        stack: str,
        group_title: str,
        specs: list[tuple[str, str]],
    ) -> QGroupBox:
        """构建单个技术栈规范分区"""
        group = QGroupBox(group_title)
        group.setObjectName("specGroup")
        v = QVBoxLayout(group)
        v.setContentsMargins(12, 16, 12, 12)
        v.setSpacing(8)

        for code, name in specs:
            row = self._build_spec_row(stack, code, name)
            v.addWidget(row)

        return group

    def _build_spec_row(self, stack: str, code: str, name: str) -> QWidget:
        """构建单个规范行：[选择] [编号] [名称] ... [打开]"""
        row = QWidget()
        h = QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(12)

        # M4-Iter3：选择按钮（用于对比）
        select_btn = QPushButton("选择")
        select_btn.setObjectName("toolBtn")
        select_btn.setCheckable(True)
        select_btn.clicked.connect(
            lambda checked=False, s=stack, c=code: self._on_select_for_compare(s, c)
        )
        h.addWidget(select_btn)

        code_label = QLabel(code)
        code_label.setObjectName("specCode")
        code_label.setMinimumWidth(40)
        h.addWidget(code_label)

        name_label = QLabel(name)
        name_label.setObjectName("specName")
        h.addWidget(name_label, 1)

        open_btn = QPushButton("打开")
        open_btn.setObjectName("openBtn")
        open_btn.clicked.connect(
            lambda checked=False, s=stack, c=code: self._on_open_spec(s, c)
        )
        h.addWidget(open_btn)

        # 查找规范文件，若不存在则禁用按钮
        spec_path = self._find_spec_file(stack, code)
        if not spec_path:
            open_btn.setEnabled(False)
            open_btn.setToolTip("未找到规范文件")

        self._open_buttons[(stack, code)] = open_btn
        self._spec_rows[(stack, code)] = row
        return row

    # ── 文件查找 ──────────────────────────────────────────

    def _find_spec_file(self, stack: str, code: str) -> str:
        """查找规范文件路径

        Args:
            stack: 技术栈（plc/python）
            code: 规范编号（如 905、210）

        Returns:
            规范文件绝对路径，未找到返回空字符串
        """
        if stack not in _STACK_SPECS:
            return ""
        _, rel_dir, _ = _STACK_SPECS[stack]
        if not self._workspace_root:
            return ""
        spec_dir = os.path.join(self._workspace_root, rel_dir)
        pattern = os.path.join(spec_dir, f"{code}_*.md")
        matches = glob.glob(pattern)
        if matches:
            return matches[0]
        return ""

    # ── 交互 ─────────────────────────────────────────────

    def _on_open_spec(self, stack: str, code: str) -> None:
        """打开规范文件（调用系统默认程序）"""
        path = self._find_spec_file(stack, code)
        if not path:
            log.warning("规范文件未找到: stack=%s, code=%s", stack, code)
            return
        url = QUrl.fromLocalFile(path)
        if not QDesktopServices.openUrl(url):
            log.error("打开规范文件失败: %s", path)

    def _on_search_changed(self, text: str) -> None:
        """搜索框文本变化时过滤规范行"""
        keyword = text.strip().lower()
        for (stack, code), row in self._spec_rows.items():
            if not keyword:
                row.setHidden(False)
                continue
            # 按编号/名称/技术栈匹配
            name = dict(_STACK_SPECS[stack][2]).get(code, "")
            match = (
                keyword in code.lower()
                or keyword in name.lower()
                or keyword in stack.lower()
            )
            row.setHidden(not match)

    def _on_refresh(self) -> None:
        """刷新规范索引"""
        try:
            if self._workspace_root:
                index = self._index_service.build_index()
                log.info("规范索引刷新完成: %d 条", len(index))
                # 重新检查按钮启用状态
                for entry in index:
                    btn = self._open_buttons.get((entry.stack, entry.code))
                    if btn is not None:
                        btn.setEnabled(entry.exists)
                        if not entry.exists:
                            btn.setToolTip("未找到规范文件")
                        else:
                            btn.setToolTip("")
            else:
                log.warning("workspace_root 为空，无法刷新索引")
        except Exception as e:
            log.error("刷新规范索引失败: %s", e)

    def _on_select_for_compare(self, stack: str, code: str) -> None:
        """选择规范用于对比

        通过查找对应的选择按钮状态判断选中与否，不依赖 sender()。
        """
        key = (stack, code)
        select_btn = self.get_select_button(stack, code)
        if select_btn is None:
            return

        if select_btn.isChecked():
            if len(self._selected_for_compare) >= 2:
                # 已选 2 个，取消新选择
                select_btn.setChecked(False)
                return
            self._selected_for_compare.add(key)
        else:
            self._selected_for_compare.discard(key)

        # 对比按钮仅在选择 2 个时启用
        self._compare_btn.setEnabled(len(self._selected_for_compare) == 2)

    def _on_compare(self) -> None:
        """对比两个已选规范"""
        if len(self._selected_for_compare) != 2:
            return

        keys = list(self._selected_for_compare)
        (_stack1, code1), (_stack2, code2) = keys[0], keys[1]

        try:
            diff = self._index_service.compare(code1, code2)
            self._show_diff_dialog(diff)
        except FileNotFoundError as e:
            QMessageBox.warning(self, "对比失败", f"规范文件不存在：\n{e}")
        except Exception as e:
            QMessageBox.critical(self, "对比失败", f"对比过程出错：\n{e}")

    def _show_diff_dialog(self, diff: SpecDiffResult) -> None:
        """展示对比结果对话框"""
        msg = QMessageBox(self)
        msg.setWindowTitle(f"规范对比: {diff.code1} vs {diff.code2}")
        msg.setIcon(QMessageBox.Icon.Information)

        if diff.same:
            msg.setText(f"规范 {diff.code1} 与 {diff.code2} 内容完全相同。")
        else:
            text_parts = [
                f"规范 {diff.code1} ({len(diff.lines1)} 行) vs {diff.code2} ({len(diff.lines2)} 行)",
                "",
                f"新增行（{diff.code2} 有而 {diff.code1} 无）：{len(diff.added)}",
                f"删除行（{diff.code1} 有而 {diff.code2} 无）：{len(diff.removed)}",
                "",
                "— 新增行预览（前 10 行）—",
                "\n".join(diff.added[:10]) if diff.added else "（无）",
                "",
                "— 删除行预览（前 10 行）—",
                "\n".join(diff.removed[:10]) if diff.removed else "（无）",
            ]
            msg.setText("\n".join(text_parts))

        msg.exec()

    # ── 属性（便于测试访问） ─────────────────────────────

    @property
    def workspace_root(self) -> str:
        return self._workspace_root

    @property
    def open_buttons(self) -> dict[tuple[str, str], QPushButton]:
        """所有"打开"按钮：{(stack, code): QPushButton}"""
        return self._open_buttons

    def get_open_button(self, stack: str, code: str) -> QPushButton | None:
        """获取指定规范项的"打开"按钮"""
        return self._open_buttons.get((stack, code))

    # M4-Iter3：新增属性
    @property
    def search_box(self) -> QLineEdit:
        """搜索框"""
        return self._search_box

    @property
    def refresh_button(self) -> QPushButton:
        """刷新按钮"""
        return self._refresh_btn

    @property
    def compare_button(self) -> QPushButton:
        """对比按钮"""
        return self._compare_btn

    @property
    def spec_rows(self) -> dict[tuple[str, str], QWidget]:
        """所有规范行：{(stack, code): QWidget}"""
        return self._spec_rows

    @property
    def index_service(self) -> SpecIndexService:
        """规范索引服务"""
        return self._index_service

    def get_spec_row(self, stack: str, code: str) -> QWidget | None:
        """获取指定规范项的行控件"""
        return self._spec_rows.get((stack, code))

    def get_select_button(self, stack: str, code: str) -> QPushButton | None:
        """获取指定规范项的"选择"按钮"""
        row = self._spec_rows.get((stack, code))
        if row is None:
            return None
        # 使用 findChildren 查找所有 QPushButton，返回文本为"选择"的第一个
        for btn in row.findChildren(QPushButton):
            if btn.text() == "选择":
                return btn
        return None

    def set_workspace_root(self, workspace_root: str) -> None:
        """设置工作空间根目录并刷新索引"""
        self._workspace_root = workspace_root
        self._index_service.set_workspace_root(workspace_root)
        self._on_refresh()
