"""PLC 项目数据模型与常量（LSP-907 907_项目配置规范_LSP）

迁移自 SW-2026-005 的 plc_project_service.py 数据结构。

数据模型已迁移至 auto_pm/models/plc.py（Pydantic v2）。
本文件保留规范常量，并重新导出模型以保持向后兼容。
"""

from __future__ import annotations

from typing import Any

from auto_pm.models.plc import (  # noqa: F401
    CheckItem,
    CheckResult,
    RenamePlan,
    RepairAction,
    RepairResult,
    StandardizeResult,
)

# 显式导出（mypy strict 模式要求）
__all__ = [
    "CheckItem",
    "CheckResult",
    "RenamePlan",
    "RepairAction",
    "RepairResult",
    "StandardizeResult",
]

# ── 常量 ──────────────────────────────────────────────────

# 标准 PLC 项目目录结构（LSP-907 §3.1）
STD_DIRS: list[str] = [
    "00_项目管理",
    "01_需求与设计",
    "02_PLC程序",
    "03_HMI设计",
    "04_现场调试",
    "04_驱动器与设备",
    "05_测试与验证",
    "06_文档与交付",
    "07_技术支持",
    "08_备件管理",
    "09_项目总结",
    "10_知识库",
]

# PRD 文档模板集（LSP-907 + SysLib FB 标准）
STD_PRDS: list[str] = [
    "需求分析文档_REQ.md",
    "接口文档_INT.md",
    "详细设计说明书_DSN.md",
    "技术方案文档_TEC.md",
]

# .plc.json 必填字段（LSP-907 §1.1）
REQUIRED_PLC_JSON_FIELDS: list[str] = ["name", "description", "version"]

# 允许缺失 .plc.json 的库类型（SysLib FB 项目无 .plc.json）
SKIP_PLC_JSON_TYPES: list[str] = ["syslib_fb"]

# PRD 文档命名规范映射（标准名 → 非标准匹配模式）
NAMING_RULES: dict[str, dict[str, Any]] = {
    "需求分析文档_REQ.md": {
        "doc_type": "REQ",
        "prefix": "需求",
        "patterns": [r"^需求文档_PRD-.*\.md$", r"^.*_REQ\.md$"],
    },
    "接口文档_INT.md": {
        "doc_type": "INT",
        "prefix": "接口",
        "patterns": [r"^接口文档_IFC-.*\.md$", r"^.*_INT\.md$"],
    },
    "详细设计说明书_DSN.md": {
        "doc_type": "DSN",
        "prefix": "详细设计",
        "patterns": [r"^详细设计说明书_DSN-.*\.md$", r"^.*_DSN\.md$"],
    },
    "技术方案文档_TEC.md": {
        "doc_type": "TEC",
        "prefix": "技术方案",
        "patterns": [r"^技术方案文档_TEC-.*\.md$", r"^.*_TEC\.md$"],
    },
}


# 数据模型已迁移至 auto_pm/models/plc.py（Pydantic v2）
# 此处通过顶部 import 重新导出，保持向后兼容：
#   from auto_pm.plc.models import CheckResult, RepairResult, ...
