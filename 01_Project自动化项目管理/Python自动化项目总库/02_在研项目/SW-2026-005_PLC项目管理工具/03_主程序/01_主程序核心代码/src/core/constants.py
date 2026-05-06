# -*- coding: utf-8 -*-
"""
常量和枚举定义

定义项目中使用的所有枚举类型、常量映射表和业务规则常量。
参考SW-2026-004的constants.py结构，针对PLC项目管理场景进行定制。
"""
from enum import Enum


# ============================================================
# 应用基础信息
# ============================================================
APP_NAME = "SW-2026-005 PLC项目管理工具"
VERSION = "1.0.0-alpha"
AUTHOR = "Trae AI Assistant"
DESCRIPTION = "专注于PLC+HMI单机设备项目的标准化管理工具"


# ============================================================
# 业务线类型 (BusinessLine)
# ============================================================
class BusinessLine(Enum):
    """业务线类型 - 项目所属的业务领域"""
    SOFTWARE = "SW"       # 软件开发
    DEVICE = "DJ"         # 单机设备
    AUTOMATION = "ZD"     # 自动化整线
    UPGRADE = "XT"        # 系统升级
    MAINTENANCE = "WX"    # 维保项目


BUSINESS_LINE_DESC = {
    BusinessLine.SOFTWARE: "软件开发项目",
    BusinessLine.DEVICE: "单机设备项目",
    BusinessLine.AUTOMATION: "自动化整线项目",
    BusinessLine.UPGRADE: "系统升级项目",
    BusinessLine.MAINTENANCE: "维保项目",
}


# ============================================================
# 项目状态 (ProjectStatus)
# ============================================================
class ProjectStatus(Enum):
    """项目生命周期状态"""
    PLANNING = "planning"       # 规划中
    ACTIVE = "active"           # 进行中
    TESTING = "testing"         # 测试中
    COMPLETED = "completed"     # 已完成
    ARCHIVED = "archived"       # 已归档
    PAUSED = "paused"           # 已暂停
    CANCELLED = "cancelled"     # 已取消


PROJECT_STATUS_COLOR = {
    ProjectStatus.PLANNING: "#9E9E9E",
    ProjectStatus.ACTIVE: "#4CAF50",
    ProjectStatus.TESTING: "#2196F3",
    ProjectStatus.COMPLETED: "#3F51B5",
    ProjectStatus.ARCHIVED: "#607D8B",
    ProjectStatus.PAUSED: "#FF9800",
    ProjectStatus.CANCELLED: "#F44336",
}

PROJECT_STATUS_DESC = {
    ProjectStatus.PLANNING: "规划中",
    ProjectStatus.ACTIVE: "进行中",
    ProjectStatus.TESTING: "测试中",
    ProjectStatus.COMPLETED: "已完成",
    ProjectStatus.ARCHIVED: "已归档",
    ProjectStatus.PAUSED: "已暂停",
    ProjectStatus.CANCELLED: "已取消",
}


# ============================================================
# 文档类型 (DocumentType)
# ============================================================
class DocumentType(Enum):
    """文档类型枚举 - PLC项目全生命周期文档体系"""
    REQ = "REQ"      # 需求规格说明书
    DSN = "DSN"      # 详细设计文档
    IFC = "IFC"      # 接口文档
    UM = "UM"        # 用户操作手册
    CHG = "CHG"      # 变更记录
    ALM = "ALM"      # 报警码定义
    VAR = "VAR"      # 变量清单
    IO = "IO"        # IO分配表
    ARC = "ARC"      # 架构设计文档
    TEST = "TEST"    # 测试报告
    SUM = "SUM"      # 项目总结


DOCUMENT_TYPE_NAMES = {
    DocumentType.REQ: "需求规格说明书",
    DocumentType.DSN: "详细设计文档",
    DocumentType.IFC: "接口文档",
    DocumentType.UM: "用户操作手册",
    DocumentType.CHG: "变更记录",
    DocumentType.ALM: "报警码定义",
    DocumentType.VAR: "变量清单",
    DocumentType.IO: "IO分配表",
    DocumentType.ARC: "架构设计文档",
    DocumentType.TEST: "测试报告",
    DocumentType.SUM: "项目总结",
}


# ============================================================
# PLC品牌 (PLCBrand)
# ============================================================
class PLCBrand(Enum):
    """支持的PLC品牌"""
    SIEMENS = "Siemens"       # 西门子 (TIA Portal)
    BECKHOFF = "Beckhoff"     # 倍福 (TwinCAT)
    OMRON = "Omron"           # 欧姆龙 (Sysmac Studio)
    MITSUBISHI = "Mitsubishi" # 三菱GX Works
    CODESYS = "Codesys"       # CODESYS (通用IEC平台)


PLC_BRAND_DESCRIPTIONS = {
    PLCBrand.SIEMENS: "西门子 TIA Portal",
    PLCBrand.BECKHOFF: "倍福 TwinCAT3",
    PLCBrand.OMRON: "欧姆龙 Sysmac Studio",
    PLCBrand.MITSUBISHI: "三菱 GX Works3",
    PLCBrand.CODESYS: "CODESYS V3.5",
}


# ============================================================
# HMI品牌 (HMIBrand)
# ============================================================
class HMIBrand(Enum):
    """支持的HMI/触摸屏品牌"""
    SIEMENS = "Siemens"       # 西门子 WinCC
    BECKHOFF = "Beckhoff"     # 倍福 TwinCAT HMI
    PROFACE = "Proface"       # 普洛菲斯
    WEINVIEW = "Weinview"     # 威纶通
    MITSUBISHI = "Mitsubishi" # 三菱 GT Works


HMI_BRAND_DESCRIPTIONS = {
    HMIBrand.SIEMENS: "西门子 WinCC Unified",
    HMIBrand.BECKHOFF: "倍福 TwinCAT HMI",
    HMIBrand.PROFACE: "普洛菲斯 GP-ProEX",
    HMIBrand.WEINVIEW: "威纶通 EBPro",
    HMIBrand.MITSUBISHI: "三菱 GT Works3",
}


# ============================================================
# ST语言关键字 (ST Keywords) - 用于语法高亮
# ============================================================
ST_KEYWORDS = [
    "VAR", "VAR_INPUT", "VAR_OUTPUT", "VAR_IN_OUT", "VAR_GLOBAL",
    "VAR_TEMP", "VAR_STATIC", "VAR_CONSTANT", "VAR_EXTERNAL",
    "VAR_ACCESS", "RETAIN", "NON_RETAIN", "CONSTANT", "END_VAR",
    "PROGRAM", "FUNCTION", "FUNCTION_BLOCK", "METHOD", "PROPERTY",
    "ACTION", "STEP", "INITIAL_STEP", "TRANSITION",
    "TYPE", "END_TYPE", "STRUCT", "END_STRUCT", "ENUM", "END_ENUM",
    "ARRAY", "OF", "IF", "THEN", "ELSIF", "ELSE", "END_IF",
    "CASE", "OF", "ELSE", "END_CASE",
    "FOR", "TO", "BY", "DO", "END_FOR",
    "WHILE", "DO", "END_WHILE",
    "REPEAT", "UNTIL", "END_REPEAT",
    "LOOP", "END_LOOP",
    "EXIT", "RETURN", "CONTINUE",
    "WITH", "DO", "END_WITH",
]

ST_DATA_TYPES = [
    "BOOL", "BYTE", "WORD", "DWORD", "LWORD",
    "SINT", "USINT", "INT", "UINT", "DINT", "UDINT", "LINT", "ULINT",
    "REAL", "LREAL",
    "TIME", "DATE", "TIME_OF_DAY", "DATE_AND_TIME",
    "STRING", "WSTRING",
]


# ============================================================
# 模板定义
# ============================================================
TEMPLATE_METADATA = [
    {
        "id": "TPL-SINGLE-PLC-M001",
        "name": "标准单机PLC项目(完整版)",
        "version": "V1.0.0",
        "business_lines": ["DJ", "ZD"],
        "is_builtin": True,
        "description": (
            "包含完整文档体系的单机PLC项目模板，"
            "含需求/设计/接口/IO分配/报警/变量等全套文档结构"
        ),
    },
    {
        "id": "TPL-SINGLE-PLC-S001",
        "name": "标准单机PLC项目(精简版)",
        "version": "V1.0.0",
        "business_lines": ["DJ"],
        "is_builtin": True,
        "description": (
            "精简版单机PLC项目模板，适用于小型快速交付项目"
        ),
    },
]

TEMPLATE_FILES = {
    "TPL-SINGLE-PLC-M001": "src/templates/project_structures/M001_full.json",
    "TPL-SINGLE-PLC-S001": "src/templates/project_structures/S001_lite.json",
}
