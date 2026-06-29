"""全局功能页 - 规范中心

V2.2 Week3 T11-T14 重构：将原硬编码 7 规范 + 旧 SpecIndexService 的实现
改造为 QTabWidget 6 Tab 结构，对接新 IndexService（基于 spec_registry.json）。

6 Tab 结构：
1. 概览（OverviewTab）：规范统计（总数/各域数/生命周期分布）+ 健康摘要
2. 规范索引（IndexTab）：三域（PM/PLC/Python）规范列表 + 打开文件 + 搜索框
3. 健康检查（CheckTab）：10 项 SHC 健康检查结果展示 + 自动修复按钮
4. Frontmatter（FrontmatterTab）：批量预览/应用（dry-run/apply）
5. 报告（ReportTab）：markdown/json 格式选择 + 生成 + 保存
6. 对比（CompareTab）：保留旧对比功能（迁移到新 IndexService）

数据流：
    Service 输出 → DTO 转换（spec_center_dto.py）→ QWidget 渲染
    禁止 QWidget 直接调用 Service，必须经过 SpecCenterAdapter
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QLabel, QTabWidget, QVBoxLayout, QWidget

from auto_pm.logging.logging import setup_logger
from auto_pm.ui.global_pages.spec_center_dto import (
    CompareResultDTO,
    FrontmatterPreviewDTO,
    HealthCheckOutputDTO,
    ReportOutputDTO,
    SpecCenterAdapter,
    SpecEntryDTO,
    SpecOverviewDTO,
)
from auto_pm.ui.global_pages.spec_center_tabs import (
    CheckTab,
    CompareTab,
    FrontmatterTab,
    IndexTab,
    OverviewTab,
    ReportTab,
)

if TYPE_CHECKING:
    from auto_pm.spec.core.registry import SpecRegistry

log = setup_logger(log_level="INFO", app_name="auto_pm")

__all__ = ["SpecCenterView"]

# Tab 标识 → 中文标签
_TAB_LABELS: list[str] = [
    "概览",
    "规范索引",
    "健康检查",
    "Frontmatter",
    "报告",
    "对比",
]


class SpecCenterView(QWidget):
    """规范中心全局页（QTabWidget 主容器）

    6 Tab 子页面通过 SpecCenterAdapter 获取 DTO 数据，
    QWidget 不直接调用 Service。

    Args:
        workspace_root: 工作空间根目录路径（字符串）
        parent: 父窗口

    注意：
        - workspace_root 为空时，所有 Tab 显示空数据，不抛异常
        - 调用 set_workspace_root() 切换工作空间并刷新
    """

    def __init__(
        self,
        workspace_root: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("specCenterPage")
        self._workspace_root = workspace_root
        self._adapter: SpecCenterAdapter | None = None
        if workspace_root:
            try:
                self._adapter = SpecCenterAdapter(workspace=Path(workspace_root))
            except Exception as e:
                log.warning("初始化 SpecCenterAdapter 失败（工作空间: %s）: %s", workspace_root, e)
                self._adapter = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 标题栏
        title_bar = QWidget()
        title_bar.setStyleSheet("background: #fafafa; padding: 8px 16px;")
        tb_layout = QVBoxLayout(title_bar)
        tb_layout.setContentsMargins(0, 0, 0, 0)
        tb_layout.setSpacing(2)

        title = QLabel("规范中心")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #222;")
        tb_layout.addWidget(title)

        subtitle = QLabel("基于 spec_registry.json 的规范管理与健康检查中心")
        subtitle.setStyleSheet("font-size: 12px; color: #999;")
        tb_layout.addWidget(subtitle)

        layout.addWidget(title_bar)

        # 6 Tab
        self._tab_widget = QTabWidget()
        self._tab_widget.setStyleSheet(
            "QTabWidget::pane { border: 1px solid #e0e0e0; background: #ffffff; }"
            "QTabBar::tab { background: #f5f5f5; padding: 6px 14px; margin-right: 2px; "
            "border: 1px solid #d0d0d0; border-bottom: none; border-top-left-radius: 4px; "
            "border-top-right-radius: 4px; }"
            "QTabBar::tab:selected { background: #ffffff; color: #4a90d9; font-weight: bold; }"
            "QTabBar::tab:hover { background: #e8e8e8; }"
        )

        # 占位 adapter（workspace 为空时使用）
        placeholder = _PlaceholderAdapter()

        adapter = self._adapter if self._adapter is not None else placeholder

        self._overview_tab = OverviewTab(adapter)  # type: ignore[arg-type]
        self._index_tab = IndexTab(adapter)  # type: ignore[arg-type]
        self._check_tab = CheckTab(adapter)  # type: ignore[arg-type]
        self._frontmatter_tab = FrontmatterTab(adapter)  # type: ignore[arg-type]
        self._report_tab = ReportTab(adapter)  # type: ignore[arg-type]
        self._compare_tab = CompareTab(adapter)  # type: ignore[arg-type]

        self._tab_widget.addTab(self._overview_tab, _TAB_LABELS[0])
        self._tab_widget.addTab(self._index_tab, _TAB_LABELS[1])
        self._tab_widget.addTab(self._check_tab, _TAB_LABELS[2])
        self._tab_widget.addTab(self._frontmatter_tab, _TAB_LABELS[3])
        self._tab_widget.addTab(self._report_tab, _TAB_LABELS[4])
        self._tab_widget.addTab(self._compare_tab, _TAB_LABELS[5])

        layout.addWidget(self._tab_widget, 1)

        # 工作空间有效时，首次刷新各 Tab
        if self._adapter is not None:
            self.refresh()

    # ── 公开 API ─────────────────────────────────────────

    def refresh(self) -> None:
        """刷新所有 Tab 数据"""
        if self._adapter is None:
            log.warning("workspace_root 未注入，无法刷新")
            return
        # 概览与索引立即刷新（轻量）
        self._overview_tab.refresh()
        self._index_tab.refresh()
        self._compare_tab.refresh()
        # 健康检查/Frontmatter/报告 按需触发（用户点击对应按钮）

    def set_workspace_root(self, workspace_root: str) -> None:
        """设置工作空间根目录并刷新所有 Tab"""
        self._workspace_root = workspace_root
        if not workspace_root:
            self._adapter = None
            log.warning("workspace_root 已清空")
            return
        try:
            from auto_pm.ui.global_pages.spec_center_dto import SpecCenterAdapter as _Adapter

            self._adapter = _Adapter(workspace=Path(workspace_root))
            # 重新绑定到各 Tab
            self._overview_tab._adapter = self._adapter
            self._index_tab._adapter = self._adapter
            self._check_tab._adapter = self._adapter
            self._frontmatter_tab._adapter = self._adapter
            self._report_tab._adapter = self._adapter
            self._compare_tab._adapter = self._adapter
            self.refresh()
        except Exception as e:
            log.error("切换工作空间失败: %s", e)
            self._adapter = None

    # ── 属性（便于测试访问） ─────────────────────────────

    @property
    def workspace_root(self) -> str:
        return self._workspace_root

    @property
    def adapter(self) -> SpecCenterAdapter | None:
        return self._adapter

    @property
    def tab_widget(self) -> QTabWidget:
        return self._tab_widget

    @property
    def overview_tab(self) -> OverviewTab:
        return self._overview_tab

    @property
    def index_tab(self) -> IndexTab:
        return self._index_tab

    @property
    def check_tab(self) -> CheckTab:
        return self._check_tab

    @property
    def frontmatter_tab(self) -> FrontmatterTab:
        return self._frontmatter_tab

    @property
    def report_tab(self) -> ReportTab:
        return self._report_tab

    @property
    def compare_tab(self) -> CompareTab:
        return self._compare_tab

    def get_tab(self, index: int) -> QWidget | None:
        """获取指定索引的 Tab（便于测试）"""
        return self._tab_widget.widget(index)

    @property
    def tab_count(self) -> int:
        return self._tab_widget.count()


class _PlaceholderAdapter:
    """workspace 为空时的占位 Adapter，所有方法返回空数据

    避免在 workspace_root 未注入时初始化失败。
    """

    workspace: Path = Path()

    def get_overview(self) -> SpecOverviewDTO:
        from auto_pm.ui.global_pages.spec_center_dto import (
            HealthSummaryDTO,
            SpecOverviewDTO,
        )
        return SpecOverviewDTO(
            spec_count=0,
            domain_counts={},
            lifecycle_counts={},
            health_summary=HealthSummaryDTO(
                error_count=0, warning_count=0, info_count=0, exit_code=0
            ),
        )

    def list_entries(self, domain: str | None = None) -> list[SpecEntryDTO]:
        return []

    def preview_frontmatter(self, spec_id: str | None = None) -> list[FrontmatterPreviewDTO]:
        return []

    def run_checks(
        self,
        check_ids: list[str] | None = None,
        auto_fix: bool = False,
        dry_run: bool = False,
    ) -> HealthCheckOutputDTO:
        from auto_pm.ui.global_pages.spec_center_dto import HealthCheckOutputDTO
        return HealthCheckOutputDTO(
            results=[],
            error_count=0,
            warning_count=0,
            info_count=0,
            exit_code=0,
            fix_results=[],
        )

    def generate_report(
        self, fmt: str = "markdown", output_path: Path | None = None
    ) -> ReportOutputDTO:
        from auto_pm.ui.global_pages.spec_center_dto import ReportOutputDTO
        return ReportOutputDTO(
            fmt=fmt,
            content="",
            saved_path=Path(),
        )

    def compare_specs(
        self, left_spec_id: str, right_spec_id: str
    ) -> CompareResultDTO:
        raise FileNotFoundError("workspace 未注入")

    def read_spec_content(self, spec_id: str) -> str:
        raise FileNotFoundError("workspace 未注入")

    @property
    def registry(self) -> "SpecRegistry":
        raise FileNotFoundError("workspace 未注入")
