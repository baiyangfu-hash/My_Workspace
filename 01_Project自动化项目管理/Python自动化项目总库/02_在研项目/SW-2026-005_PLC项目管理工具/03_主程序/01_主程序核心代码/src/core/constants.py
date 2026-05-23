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
# 项目类型 (ProjectType)
# ============================================================
class ProjectType(Enum):
    """项目类型 - 用于区分管理模型和工作流模板"""
    GENERIC = "generic"
    DJ_SINGLE_MACHINE = "dj_single_machine"


PROJECT_TYPE_DESC = {
    ProjectType.GENERIC: "通用PLC项目",
    ProjectType.DJ_SINGLE_MACHINE: "DJ单机项目",
}


# ============================================================
# 工作流阶段 (WorkflowStage)
# ============================================================
class WorkflowStage(Enum):
    """DJ单机项目标准阶段"""
    INITIATION = "initiation"
    DESIGN = "design"
    DEVELOPMENT = "development"
    COMMISSIONING = "commissioning"
    TESTING = "testing"
    DELIVERY = "delivery"
    MAINTENANCE = "maintenance"


WORKFLOW_STAGE_DESC = {
    WorkflowStage.INITIATION: "立项与需求",
    WorkflowStage.DESIGN: "方案与架构",
    WorkflowStage.DEVELOPMENT: "PLC开发",
    WorkflowStage.COMMISSIONING: "现场调试",
    WorkflowStage.TESTING: "测试验证",
    WorkflowStage.DELIVERY: "交付归档",
    WorkflowStage.MAINTENANCE: "维护支持",
}


# ============================================================
# 资产类型 (ProjectArtifactType)
# ============================================================
class ProjectArtifactType(Enum):
    """项目资产类型"""
    ROOT = "root"
    CHANGE_ROOT = "change_root"
    CHANGE_ORDER = "change_order"
    PLC_ROOT = "plc_root"
    PLC_SOURCE = "plc_source"
    PLC_DB = "plc_db"
    PLC_CONFIG = "plc_config"
    PLC_TEST = "plc_test"
    DOC_REQ = "doc_req"
    DOC_DSN = "doc_dsn"
    DOC_IFC = "doc_ifc"
    DOC_CHG = "doc_chg"
    DOC_UM = "doc_um"
    DOC_ALM = "doc_alm"
    DOC_IO = "doc_io"
    DOC_VAR = "doc_var"
    DOC_ARC = "doc_arc"
    DOC_HMI = "doc_hmi"
    DOC_DELIVERY = "doc_delivery"
    DOC_MISC = "doc_misc"
    HMI_SOURCE = "hmi_source"
    DEBUG_DOC = "debug_doc"
    DELIVERY = "delivery"
    KNOWLEDGE = "knowledge"


PROJECT_ARTIFACT_TYPE_DESC = {
    ProjectArtifactType.ROOT: "项目根目录",
    ProjectArtifactType.CHANGE_ROOT: "变更管理目录",
    ProjectArtifactType.CHANGE_ORDER: "变更单",
    ProjectArtifactType.PLC_ROOT: "PLC程序目录",
    ProjectArtifactType.PLC_SOURCE: "PLC源码",
    ProjectArtifactType.PLC_DB: "PLC数据块",
    ProjectArtifactType.PLC_CONFIG: "PLC配置",
    ProjectArtifactType.PLC_TEST: "PLC测试",
    ProjectArtifactType.DOC_REQ: "需求文档",
    ProjectArtifactType.DOC_DSN: "详细设计文档",
    ProjectArtifactType.DOC_IFC: "接口文档",
    ProjectArtifactType.DOC_CHG: "变更文档",
    ProjectArtifactType.DOC_UM: "使用说明",
    ProjectArtifactType.DOC_ALM: "报警文档",
    ProjectArtifactType.DOC_IO: "IO文档",
    ProjectArtifactType.DOC_VAR: "变量文档",
    ProjectArtifactType.DOC_ARC: "架构文档",
    ProjectArtifactType.DOC_HMI: "HMI文档",
    ProjectArtifactType.DOC_DELIVERY: "交付文档",
    ProjectArtifactType.DOC_MISC: "通用文档",
    ProjectArtifactType.HMI_SOURCE: "HMI源码",
    ProjectArtifactType.DEBUG_DOC: "调试文档",
    ProjectArtifactType.DELIVERY: "交付资产",
    ProjectArtifactType.KNOWLEDGE: "知识库",
}


# ============================================================
# 变更状态/分类
# ============================================================
class ChangeStatus(Enum):
    """变更单状态"""
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    ANALYZING = "analyzing"
    IN_PROGRESS = "in_progress"
    IMPLEMENTED = "implemented"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    @classmethod
    def valid_transitions(cls, current: "ChangeStatus") -> list:
        transitions = {
            cls.DRAFT: [cls.REVIEW, cls.CANCELLED],
            cls.REVIEW: [cls.APPROVED, cls.DRAFT, cls.CANCELLED],
            cls.APPROVED: [cls.ANALYZING, cls.IN_PROGRESS, cls.CANCELLED],
            cls.ANALYZING: [cls.IN_PROGRESS, cls.CANCELLED],
            cls.IN_PROGRESS: [cls.IMPLEMENTED, cls.CANCELLED],
            cls.IMPLEMENTED: [cls.VERIFYING],
            cls.VERIFYING: [cls.COMPLETED, cls.IN_PROGRESS],
            cls.COMPLETED: [],
            cls.CANCELLED: [],
        }
        return transitions.get(current, [])


class ChangeCategory(Enum):
    """变更单分类"""
    DOCU = "DOCU"
    PLC = "PLC"
    HMI = "HMI"
    ELEC = "ELEC"
    SAFE = "SAFE"
    MECH = "MECH"
    SCPT = "SCPT"


IGNORED_PROJECT_DIRS = {
    ".trae",
    ".plc-out",
    ".git",
    "__pycache__",
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
    "TPL-DJ-SINGLE-MACHINE": "src/templates/project_structures/DJ_single_machine.json",
}
