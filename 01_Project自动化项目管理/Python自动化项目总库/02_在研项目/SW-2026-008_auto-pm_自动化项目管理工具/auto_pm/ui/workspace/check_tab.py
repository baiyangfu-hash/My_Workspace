"""项目工作区 - 检查 Tab

展示 PLC 项目结构检查结果，支持执行检查/自动修复预览/标准化命名预览。

布局：
    ┌─────────────────────────────────────────────────────────┐
    │ [▶ 执行检查]  [🔧 自动修复]  [📝 标准化命名]              │
    ├─────────────────────────────────────────────────────────┤
    │ ✅ 目录结构                                              │
    │   ✅ 02_PLC程序/ 存在                                     │
    │   ❌ 04_现场调试/ 缺失 — [修复]                           │
    │ ⚠️ 标志文件                                              │
    │   ✅ .plc.json 存在                                       │
    │   ⚠️ PM_SESSION_*.md 缺失 — [修复]                      │
    ├─────────────────────────────────────────────────────────┤
    │ 检查结果: 8 通过 / 2 警告 / 1 失败                       │
    └─────────────────────────────────────────────────────────┘

信号：
    check_completed() - 检查完成
    repair_completed() - 修复完成
"""

from __future__ import annotations

import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from auto_pm.logging.logging import setup_logger
from auto_pm.models.plc import (
    CheckItem,
    CheckResult,
    RepairResult,
    StandardizeResult,
)

log = setup_logger(log_level="INFO", app_name="auto_pm")

__all__ = ["CheckTab"]

# 检查项状态 → 图标
_STATUS_ICON: dict[str, str] = {
    "pass": "✅",
    "warn": "⚠️",
    "fail": "❌",
}

# 修复动作状态 → 图标
_REPAIR_ICON: dict[str, str] = {
    "fixed": "✅",
    "skipped": "⏭️",
    "failed": "❌",
}

_TAB_STYLE = """
QFrame#checkTab { background: #fafafa; }
QPushButton#primaryBtn {
    font-size: 13px; color: #ffffff;
    background: #4a90d9; border: none;
    border-radius: 4px; padding: 6px 16px;
}
QPushButton#primaryBtn:hover { background: #357abd; }
QPushButton#secondaryBtn {
    font-size: 13px; color: #4a90d9;
    background: #ffffff; border: 1px solid #4a90d9;
    border-radius: 4px; padding: 6px 16px;
}
QPushButton#secondaryBtn:hover { background: #f0f5ff; }
QFrame#groupCard {
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
}
QFrame#groupCard:hover { border-color: #4a90d9; }
QLabel#groupTitle { font-size: 13px; font-weight: bold; color: #333; }
QLabel#itemText { font-size: 12px; color: #444; }
QLabel#summaryText { font-size: 12px; color: #555; }
QLabel#emptyHint { color: #999; font-size: 14px; padding: 60px; }
QPushButton#itemBtn {
    font-size: 11px; color: #e67e22;
    background: #ffffff; border: 1px solid #e67e22;
    border-radius: 3px; padding: 2px 10px;
}
QPushButton#itemBtn:hover { background: #fef5e7; }
QFrame#summaryBar {
    background: #ffffff;
    border-top: 1px solid #e0e0e0;
}
"""


def _categorize(item_name: str) -> str:
    """将检查项名称映射到分组类别"""
    if item_name.startswith("目录 "):
        return "目录结构"
    if item_name == ".plc.json" or item_name.startswith(".plc.json"):
        return "标志文件"
    if item_name == "PM_SESSION":
        return "标志文件"
    if item_name == "PRD 目录" or item_name.startswith("PRD/"):
        return "PRD 文档"
    return "其他"


def _group_status(items: list[CheckItem]) -> str:
    """计算分组的聚合状态：有 fail→fail，有 warn→warn，否则 pass"""
    statuses = {it.status for it in items}
    if "fail" in statuses:
        return "fail"
    if "warn" in statuses:
        return "warn"
    return "pass"


class CheckTab(QWidget):
    """项目工作区 - 检查 Tab

    展示 PLC 项目结构检查结果，支持执行检查/自动修复预览/标准化命名预览。
    检查完成发射 check_completed()，修复完成发射 repair_completed()。
    """

    check_completed = Signal()
    repair_completed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._project_id: str | None = None
        self._project_path: str = ""
        self._workspace_root: str = ""
        self._checker: object | None = None
        self._repairer: object | None = None
        self._last_check_result: CheckResult | None = None
        self._build_ui()

    # ── UI 构建 ────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.setObjectName("checkTab")
        self.setStyleSheet(_TAB_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        layout.addWidget(self._build_toolbar())

        # 结果展示区（滚动）
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)

        self._list_container = QWidget()
        self._list_layout = QVBoxLayout(self._list_container)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(8)
        self._list_layout.addStretch(1)
        self._scroll.setWidget(self._list_container)
        self._scroll.setVisible(False)
        layout.addWidget(self._scroll, 1)

        # 空状态提示
        self._empty_hint = QLabel("点击「执行检查」开始检查项目结构")
        self._empty_hint.setObjectName("emptyHint")
        self._empty_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._empty_hint)

        # 底部摘要栏
        self._summary_bar = QFrame()
        self._summary_bar.setObjectName("summaryBar")
        sh = QHBoxLayout(self._summary_bar)
        sh.setContentsMargins(14, 8, 14, 8)
        self._summary_label = QLabel("检查结果: —")
        self._summary_label.setObjectName("summaryText")
        sh.addWidget(self._summary_label)
        sh.addStretch(1)
        layout.addWidget(self._summary_bar)

    def _build_toolbar(self) -> QWidget:
        """构建顶部按钮栏"""
        toolbar = QWidget()
        h = QHBoxLayout(toolbar)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(10)

        self._check_btn = QPushButton("▶ 执行检查")
        self._check_btn.setObjectName("primaryBtn")
        self._check_btn.clicked.connect(self._on_run_check)
        h.addWidget(self._check_btn)

        self._repair_btn = QPushButton("🔧 自动修复")
        self._repair_btn.setObjectName("secondaryBtn")
        self._repair_btn.clicked.connect(self._on_auto_repair)
        h.addWidget(self._repair_btn)

        self._standardize_btn = QPushButton("📝 标准化命名")
        self._standardize_btn.setObjectName("secondaryBtn")
        self._standardize_btn.clicked.connect(self._on_standardize)
        h.addWidget(self._standardize_btn)

        h.addStretch(1)
        return toolbar

    # ── 数据加载 ──────────────────────────────────────────

    def load_project(self, project_id: str, project_path: str) -> None:
        """加载项目，初始化 checker/repairer

        Args:
            project_id: 项目编号
            project_path: 项目根目录绝对路径
        """
        self._project_id = project_id
        self._project_path = project_path
        # 推算 workspace_root（单项目检查/修复不依赖此值，但构造器需要）
        self._workspace_root = os.path.dirname(project_path) or project_path
        try:
            from auto_pm.plc.checker import PlcChecker
            from auto_pm.plc.repairer import PlcRepairer

            self._checker = PlcChecker(self._workspace_root)
            self._repairer = PlcRepairer(self._workspace_root)
        except Exception as e:
            log.error("检查Tab初始化 checker/repairer 失败: %s", e, exc_info=True)
            self._checker = None
            self._repairer = None
        log.info("检查Tab加载项目: %s (%s)", project_id, project_path)

    # ── 执行检查 ──────────────────────────────────────────

    def _on_run_check(self) -> None:
        """执行检查"""
        if self._checker is None or not self._project_path:
            log.warning("检查Tab: checker 未初始化或项目路径为空")
            return
        try:
            result = self._checker.check_project(self._project_path)  # type: ignore[attr-defined]
        except Exception as e:
            log.error("检查Tab: 执行检查失败: %s", e, exc_info=True)
            return
        self._last_check_result = result
        self._render_check_result(result)
        self.check_completed.emit()

    def _render_check_result(self, result: CheckResult) -> None:
        """渲染检查结果（按 category 分组）"""
        self._clear_list()
        self._empty_hint.setVisible(False)
        self._scroll.setVisible(True)

        # 按 category 分组（保留首次出现顺序）
        groups: dict[str, list[CheckItem]] = {}
        order: list[str] = []
        for it in result.items:
            cat = _categorize(it.item)
            if cat not in groups:
                groups[cat] = []
                order.append(cat)
            groups[cat].append(it)

        for cat in order:
            group_widget = self._build_group(cat, groups[cat])
            self._list_layout.insertWidget(self._list_layout.count() - 1, group_widget)

        # 更新摘要
        self._summary_label.setText(
            f"检查结果: {result.pass_count} 通过 / "
            f"{result.warn_count} 警告 / {result.fail_count} 失败"
        )

    def _build_group(self, category: str, items: list[CheckItem]) -> QFrame:
        """构建一个分组卡片"""
        card = QFrame()
        card.setObjectName("groupCard")
        v = QVBoxLayout(card)
        v.setContentsMargins(14, 10, 14, 10)
        v.setSpacing(6)

        # 分组标题（聚合状态图标 + 类别名）
        gstatus = _group_status(items)
        icon = _STATUS_ICON.get(gstatus, "•")
        title = QLabel(f"{icon}  {category}")
        title.setObjectName("groupTitle")
        v.addWidget(title)

        # 各检查项
        for it in items:
            row = self._build_item_row(it)
            v.addLayout(row)

        return card

    def _build_item_row(self, item: CheckItem) -> QHBoxLayout:
        """构建单条检查项行：状态图标 + 描述 + 可选修复按钮"""
        row = QHBoxLayout()
        row.setSpacing(8)

        icon = _STATUS_ICON.get(item.status, "•")
        text = f"{icon}  {item.message}" if item.message else f"{icon}  {item.item}"
        label = QLabel(text)
        label.setObjectName("itemText")
        label.setWordWrap(True)
        row.addWidget(label, 1)

        # warn/fail 项显示"修复"按钮
        if item.status in ("warn", "fail"):
            repair_btn = QPushButton("修复")
            repair_btn.setObjectName("itemBtn")
            repair_btn.clicked.connect(
                lambda checked=False, iid=item.item: self._on_repair_item(iid)
            )
            row.addWidget(repair_btn)

        return row

    # ── 自动修复 ──────────────────────────────────────────

    def _on_auto_repair(self) -> None:
        """自动修复预览（dry_run=True，不实际执行）"""
        if self._repairer is None or not self._project_path:
            log.warning("检查Tab: repairer 未初始化或项目路径为空")
            return
        try:
            result = self._repairer.repair_project(  # type: ignore[attr-defined]
                self._project_path, dry_run=True, rename_confirm=False
            )
        except Exception as e:
            log.error("检查Tab: 自动修复预览失败: %s", e, exc_info=True)
            return
        self._render_repair_result(result)

    def _render_repair_result(self, result: RepairResult) -> None:
        """渲染修复预览结果"""
        self._clear_list()
        self._empty_hint.setVisible(False)
        self._scroll.setVisible(True)

        card = QFrame()
        card.setObjectName("groupCard")
        v = QVBoxLayout(card)
        v.setContentsMargins(14, 10, 14, 10)
        v.setSpacing(6)

        title = QLabel("🔧 修复预览（dry-run，未实际执行）")
        title.setObjectName("groupTitle")
        v.addWidget(title)

        if not result.actions:
            hint = QLabel("无需修复，所有检查项已通过")
            hint.setObjectName("itemText")
            v.addWidget(hint)
        else:
            for act in result.actions:
                icon = _REPAIR_ICON.get(act.status, "•")
                destructive = " [破坏性]" if act.destructive else ""
                text = f"{icon}  {act.action}{destructive} — {act.detail}"
                label = QLabel(text)
                label.setObjectName("itemText")
                label.setWordWrap(True)
                v.addWidget(label)

        self._list_layout.insertWidget(self._list_layout.count() - 1, card)

        self._summary_label.setText(
            f"修复预览: {result.fixed_count} 可修复 / "
            f"{result.skipped_count} 跳过 / {result.failed_count} 失败"
        )

    # ── 标准化命名 ────────────────────────────────────────

    def _on_standardize(self) -> None:
        """标准化命名预览（apply=False，不实际执行）"""
        if self._repairer is None or not self._project_path:
            log.warning("检查Tab: repairer 未初始化或项目路径为空")
            return
        try:
            result = self._repairer.standardize_docs(  # type: ignore[attr-defined]
                self._project_path, apply=False
            )
        except Exception as e:
            log.error("检查Tab: 标准化预览失败: %s", e, exc_info=True)
            return
        self._render_standardize_result(result)

    def _render_standardize_result(self, result: StandardizeResult) -> None:
        """渲染标准化预览结果"""
        self._clear_list()
        self._empty_hint.setVisible(False)
        self._scroll.setVisible(True)

        card = QFrame()
        card.setObjectName("groupCard")
        v = QVBoxLayout(card)
        v.setContentsMargins(14, 10, 14, 10)
        v.setSpacing(6)

        title = QLabel("📝 标准化命名预览（未实际执行）")
        title.setObjectName("groupTitle")
        v.addWidget(title)

        if not result.plans:
            hint = QLabel("无需标准化，所有 PRD 文档命名已符合规范")
            hint.setObjectName("itemText")
            v.addWidget(hint)
        else:
            for plan in result.plans:
                old_name = os.path.basename(plan.old_path)
                new_name = os.path.basename(plan.new_path)
                text = f"🔄  {old_name} → {new_name}（{plan.doc_type}）"
                label = QLabel(text)
                label.setObjectName("itemText")
                label.setWordWrap(True)
                v.addWidget(label)

        self._list_layout.insertWidget(self._list_layout.count() - 1, card)

        self._summary_label.setText(
            f"标准化预览: {result.applied_count} 已应用 / {result.skipped_count} 待确认"
        )

    # ── 单项修复 ──────────────────────────────────────────

    def _on_repair_item(self, item_id: str) -> None:
        """单项修复（实际执行 repair_project，后端会修复所有可修复项）

        Args:
            item_id: 触发修复的检查项名称（用于日志记录）
        """
        log.info("检查Tab: 触发单项修复 item=%s", item_id)
        if self._repairer is None or not self._project_path:
            log.warning("检查Tab: repairer 未初始化或项目路径为空")
            return
        try:
            self._repairer.repair_project(  # type: ignore[attr-defined]
                self._project_path, dry_run=False, rename_confirm=False
            )
        except Exception as e:
            log.error("检查Tab: 单项修复失败: %s", e, exc_info=True)
            return
        # 修复后重新检查并渲染
        if self._checker is not None:
            try:
                result = self._checker.check_project(self._project_path)  # type: ignore[attr-defined]
            except Exception as e:
                log.error("检查Tab: 修复后重新检查失败: %s", e, exc_info=True)
                return
            self._last_check_result = result
            self._render_check_result(result)
        self.repair_completed.emit()

    # ── 辅助 ─────────────────────────────────────────────

    def _clear_list(self) -> None:
        """清空列表（保留底部弹簧）"""
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def _get_group_cards(self) -> list[QFrame]:
        """获取当前列表中的所有分组卡片（用于测试/外部检查）"""
        cards: list[QFrame] = []
        for i in range(self._list_layout.count()):
            item = self._list_layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if isinstance(widget, QFrame) and widget.objectName() == "groupCard":
                    cards.append(widget)
        return cards
