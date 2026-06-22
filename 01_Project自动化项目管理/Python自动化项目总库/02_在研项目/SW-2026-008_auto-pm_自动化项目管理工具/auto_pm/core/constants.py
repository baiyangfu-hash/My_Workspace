"""统一常量定义（M3-Iter7）

集中定义技术栈模板映射、业务线选项等常量，消除散落在各模块的重复定义。

来源：
- LSP-907：PLC 技术栈规范
- 210/211/220：Python 技术栈规范
- 项目管理规范：业务线编码定义
"""

from __future__ import annotations

from typing import Final

# ── 技术栈 → 模板名映射 ───────────────────────────────────

#: 技术栈到 Copier 模板名的映射（默认模板）
STACK_TEMPLATE_MAP: Final[dict[str, str]] = {
    "plc": "plc-standard-project",
    "python": "python-tool",
}

#: PLC 项目模式到模板名的映射
PLC_MODE_TEMPLATE_MAP: Final[dict[str, str]] = {
    "shared-library": "plc-shared-library",
    "test-suite": "plc-test-suite",
    "standard-project": "plc-standard-project",
}

#: PLC 项目模式选项列表（用于 CLI 和 UI）
PLC_MODE_OPTIONS: Final[list[tuple[str, str]]] = [
    ("shared-library", "公共库"),
    ("test-suite", "公共库验证"),
    ("standard-project", "标准单机项目"),
]

#: 默认 PLC 项目模式
DEFAULT_PLC_MODE: Final[str] = "standard-project"

#: 默认模板名（技术栈未知时使用）
DEFAULT_TEMPLATE_NAME: Final[str] = "unknown"


def get_plc_template_name(mode: str = DEFAULT_PLC_MODE) -> str:
    """根据 PLC 项目模式获取模板名

    Args:
        mode: PLC 项目模式 (shared-library/test-suite/standard-project)

    Returns:
        模板名，未知模式返回标准项目模板
    """
    return PLC_MODE_TEMPLATE_MAP.get(mode, PLC_MODE_TEMPLATE_MAP[DEFAULT_PLC_MODE])


def get_template_name(stack: str, mode: str = "") -> str:
    """根据技术栈获取模板名

    Args:
        stack: 技术栈标识 (plc/python/unknown)
        mode: PLC 项目模式（仅 stack=="plc" 时有效）

    Returns:
        模板名，未知技术栈返回 DEFAULT_TEMPLATE_NAME
    """
    if stack == "plc" and mode:
        return get_plc_template_name(mode)
    return STACK_TEMPLATE_MAP.get(stack, DEFAULT_TEMPLATE_NAME)


# ── 业务线选项 ─────────────────────────────────────────────

#: 业务线选项列表：(value, label) 格式，用于 UI 下拉框和 CLI 选项
BUSINESS_LINE_OPTIONS: Final[list[tuple[str, str]]] = [
    ("SW", "SW 软件开发"),
    ("DJ", "DJ 单机设备"),
    ("ZD", "ZD 自动化整线"),
    ("XT", "XT 系统升级"),
    ("WX", "WX 维保项目"),
]

#: 业务线编码列表（仅 value）
BUSINESS_LINE_CODES: Final[list[str]] = [opt[0] for opt in BUSINESS_LINE_OPTIONS]

#: 业务线编码到标签的映射
BUSINESS_LINE_LABELS: Final[dict[str, str]] = dict(BUSINESS_LINE_OPTIONS)


def get_business_line_label(code: str) -> str:
    """根据业务线编码获取标签

    Args:
        code: 业务线编码 (SW/DJ/ZD/XT/WX)

    Returns:
        业务线标签，未知编码返回编码本身
    """
    return BUSINESS_LINE_LABELS.get(code, code)


def is_valid_business_line(code: str) -> bool:
    """检查业务线编码是否合法"""
    return code in BUSINESS_LINE_CODES


# ── 技术栈选项 ─────────────────────────────────────────────

#: 技术栈选项列表：(value, label) 格式
STACK_OPTIONS: Final[list[tuple[str, str]]] = [
    ("plc", "PLC 自动化"),
    ("python", "Python 工具"),
]

#: 技术栈编码列表
STACK_CODES: Final[list[str]] = [opt[0] for opt in STACK_OPTIONS]


# ── 项目阶段选项 ───────────────────────────────────────────

#: 项目阶段选项列表：(value, label) 格式
PHASE_OPTIONS: Final[list[tuple[str, str]]] = [
    ("developing", "开发中"),
    ("commissioning", "调试中"),
    ("production", "已投产"),
    ("archived", "已归档"),
]

#: 项目阶段编码列表
PHASE_CODES: Final[list[str]] = [opt[0] for opt in PHASE_OPTIONS]

#: 项目阶段编码到标签的映射
PHASE_LABELS: Final[dict[str, str]] = dict(PHASE_OPTIONS)


def get_phase_label(code: str) -> str:
    """根据阶段编码获取标签"""
    return PHASE_LABELS.get(code, code)
