"""规范中心 6 个 Tab 子模块

- overview_tab: Tab1 概览（规范统计 + 健康摘要）
- index_tab: Tab2 索引（三域规范列表 + 打开文件 + 搜索框）
- check_tab: Tab3 健康检查（10 项 SHC 检查结果 + 自动修复按钮）
- frontmatter_tab: Tab4 Frontmatter（批量预览/应用）
- report_tab: Tab5 报告（markdown/json 格式 + 生成 + 保存）
- compare_tab: Tab6 对比（保留旧对比功能，迁移到新 IndexService）
"""

from auto_pm.ui.global_pages.spec_center_tabs.check_tab import CheckTab
from auto_pm.ui.global_pages.spec_center_tabs.compare_tab import CompareTab
from auto_pm.ui.global_pages.spec_center_tabs.frontmatter_tab import FrontmatterTab
from auto_pm.ui.global_pages.spec_center_tabs.index_tab import IndexTab
from auto_pm.ui.global_pages.spec_center_tabs.overview_tab import OverviewTab
from auto_pm.ui.global_pages.spec_center_tabs.report_tab import ReportTab

__all__ = [
    "OverviewTab",
    "IndexTab",
    "CheckTab",
    "FrontmatterTab",
    "ReportTab",
    "CompareTab",
]
