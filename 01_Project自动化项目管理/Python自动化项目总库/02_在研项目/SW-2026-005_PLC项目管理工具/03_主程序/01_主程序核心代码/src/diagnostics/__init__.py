# -*- coding: utf-8 -*-
"""
诊断分析模块

提供项目健康度分析和LSP兼容性检查功能。

主要组件:
- LSPCompatibilityChecker: LSP兼容性检查器，检测Go代码中的问题
- DiagnosticReport: 诊断报告数据模型
- project_health_analyzer: 项目健康度分析器
"""

from src.diagnostics.lsp_compatibility_checker import (
    LSPCompatibilityChecker,
    DiagnosticRules,
    FBCallInfo,
    check_project_lsp_compatibility,
)

from src.diagnostics.project_health_analyzer import (
    ProjectHealthAnalyzer,
)

__all__ = [
    # LSP兼容性检查
    "LSPCompatibilityChecker",
    "DiagnosticRules",
    "FBCallInfo",
    "check_project_lsp_compatibility",
    # 项目健康度分析
    "ProjectHealthAnalyzer",
]
