# -*- coding: utf-8 -*-
"""
业务常量定义 — 项目/业务线/模板/插件相关枚举与映射
"""
from enum import Enum


class BusinessLine(Enum):
    """业务线类型"""
    SOFTWARE = "SW"       # 软件开发
    DEVICE = "DJ"         # 单机设备
    AUTOMATION = "ZD"     # 自动化整线
    UPGRADE = "XT"        # 系统升级
    MAINTENANCE = "WX"    # 维保项目


class ProjectStatus(Enum):
    """项目状态"""
    ACTIVE = "active"        # 进行中
    COMPLETED = "completed"  # 已完成
    ARCHIVED = "archived"    # 已归档
    PAUSED = "paused"        # 已暂停


class TemplateType(Enum):
    """模板类型"""
    BUILTIN = "builtin"    # 内置模板
    CUSTOM = "custom"      # 自定义模板


class PluginStatus(Enum):
    """插件状态"""
    INSTALLED = "installed"  # 已安装
    ENABLED = "enabled"      # 已启用
    DISABLED = "disabled"    # 已禁用
    ERROR = "error"          # 错误状态


class CheckResult(Enum):
    """检查结果"""
    PASS = "pass"      # 通过
    WARNING = "warning"  # 警告
    FAIL = "fail"      # 失败


# 业务线描述
BUSINESS_LINE_DESC = {
    BusinessLine.SOFTWARE: "软件开发项目",
    BusinessLine.DEVICE: "单机设备项目",
    BusinessLine.AUTOMATION: "自动化整线项目",
    BusinessLine.UPGRADE: "系统升级项目",
    BusinessLine.MAINTENANCE: "维保项目",
}

# 业务线模板关联（按推荐优先级排序）- V2.2.0 重组后5类模板
BUSINESS_LINE_TEMPLATES = {
    BusinessLine.DEVICE.value: ["TPL-SINGLE-PLC-001", "TPL-SINGLE-ROBOT-001"],
    BusinessLine.AUTOMATION.value: ["TPL-FULLLINE-AUTO-001"],
    BusinessLine.UPGRADE.value: ["TPL-UPGRADE-STD-001"],
    BusinessLine.SOFTWARE.value: ["TPL-UPPER-STD-001"],
    BusinessLine.MAINTENANCE.value: ["TPL-UPPER-STD-001"],
}

# 项目状态颜色
PROJECT_STATUS_COLOR = {
    ProjectStatus.ACTIVE: "#4CAF50",
    ProjectStatus.COMPLETED: "#2196F3",
    ProjectStatus.ARCHIVED: "#9E9E9E",
    ProjectStatus.PAUSED: "#FF9800",
}
