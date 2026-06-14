# -*- coding: utf-8 -*-
"""
变更管理常量定义 — 变更状态/类型/领域/性质/范围/审批层级
"""
from enum import Enum


class ChangeStatus(Enum):
    """变更状态"""
    DRAFT = "draft"          # 草稿
    PENDING = "pending"      # 待审批
    APPROVED = "approved"    # 已批准
    REJECTED = "rejected"    # 已拒绝
    IMPLEMENTING = "implementing"  # 实施中
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消


class ChangeType(Enum):
    """变更类型"""
    CODE = "code"            # 代码变更
    CONFIG = "config"        # 配置变更
    DEPENDENCY = "dependency"  # 依赖变更
    DOCUMENT = "document"    # 文档变更
    STRUCTURE = "structure"  # 结构变更
    TEMPLATE = "template"    # 模板变更
    PLUGIN = "plugin"       # 插件变更


class ImpactLevel(Enum):
    """影响等级 (V1.x遗留, 建议使用Scope替代)"""
    LOW = "low"        # 低影响
    MEDIUM = "medium"  # 中等影响
    HIGH = "high"      # 高影响


# ===== V2.1.0 新增: 技术领域 (WHO - 哪个专业?) =====
class Domain(Enum):
    """技术领域 - 变更所属专业领域"""
    ELEC = "ELEC"    # 电气设计: Eplan原理图/接线图/IO分配表/BOM
    MECH = "MECH"    # 机械结构: SolidWorks 3D/装配图/加工图
    PLC = "PLC"      # PLC程序: IEC 61131-3 SCL/ST/LD/GVL
    HMI = "HMI"      # HMI程序: 触摸屏画面/变量映射/报警配置
    SCPT = "SCPT"    # Python脚本: 数据采集/MES接口/上位机应用
    DOCU = "DOCU"    # 工程文档: 设计说明书/操作手册/验收报告
    SAFE = "SAFE"    # 安全功能: 急停回路/安全矩阵/SIL评估


DOMAIN_NAMES = {
    Domain.ELEC: "电气设计",
    Domain.MECH: "机械结构",
    Domain.PLC: "PLC程序",
    Domain.HMI: "HMI程序",
    Domain.SCPT: "Python脚本",
    Domain.DOCU: "工程文档",
    Domain.SAFE: "安全功能"
}

# ===== V2.1.0 新增: 业务性质 (WHY - 为什么变?) =====
class Nature(Enum):
    """业务性质 - 变更驱动因素"""
    REQ = "REQ"      # 需求变更: 客户/市场/工艺驱动的新增或修改
    DEF = "DEF"      # 缺陷修复: Bug修复、故障排除、设计纠错
    OPT = "OPT"      # 优化改进: 性能提升、可维护性改善、用户体验优化
    CFG = "CFG"      # 配置调整: 参数修改、IO地址调整、通信配置变更
    EMRG = "EMRG"    # 紧急变更: 安全相关、生产中断等需立即处理


NATURE_NAMES = {
    Nature.REQ: "需求变更",
    Nature.DEF: "缺陷修复",
    Nature.OPT: "优化改进",
    Nature.CFG: "配置调整",
    Nature.EMRG: "紧急变更"
}

# ===== V2.1.0 替代: 影响范围 (WHERE - 影响到什么程度?) =====
class Scope(Enum):
    """影响范围 - 变更对系统的影响程度"""
    LOCAL = "LOCAL"        # 局部: 仅影响单个POU/单个画面/单个IO点
    MODULE = "MODULE"      # 模块级: 影响单个设备/单条线/单个子系统
    SYSTEM = "SYSTEM"      # 系统级: 影响多模块联动/联锁逻辑/通讯接口
    CROSS = "CROSS"        # 跨系统: 影响PLC+HMI+电气+机械多个子系统
    SAFE = "SAFE"          # 安全相关: 影响急停回路/SIL等级/安全功能


SCOPE_NAMES = {
    Scope.LOCAL: "局部",
    Scope.MODULE: "模块级",
    Scope.SYSTEM: "系统级 ⚠️",
    Scope.CROSS: "跨系统",
    Scope.SAFE: "安全相关"
}

# ===== V2.1.0 新增: 审批层级 (按范围自动匹配) =====
class ApprovalLevel(Enum):
    """审批层级"""
    PROJECT_MANAGER = "项目经理"
    LEAD = "项目负责人"
    TECH_DIRECTOR = "技术总监"
    EXECUTIVE = "高层管理"
    SAFETY_OFFICER = "安全负责人"


SCOPE_APPROVAL_MAP = {
    Scope.LOCAL: ApprovalLevel.PROJECT_MANAGER,
    Scope.MODULE: ApprovalLevel.LEAD,
    Scope.SYSTEM: ApprovalLevel.TECH_DIRECTOR,
    Scope.CROSS: ApprovalLevel.EXECUTIVE,
    Scope.SAFE: ApprovalLevel.SAFETY_OFFICER,
}

# V2.1.0 旧版到新版映射 (用于迁移)
CHANGE_TYPE_TO_DOMAIN_MAP = {
    "code": Domain.SCPT, "config": Domain.SCPT,
    "dependency": Domain.SCPT, "document": Domain.DOCU,
    "structure": Domain.SCPT, "template": Domain.SCPT,
    "plugin": Domain.SCPT, "功能变更": Domain.SCPT,
    "设计变更": Domain.SCPT, "技术变更": Domain.SCPT,
    "资源变更": Domain.SCPT, "进度变更": Domain.SCPT,
    "其他变更": Domain.SCPT, "性能变更": Domain.SCPT,
    "安全变更": Domain.SAFE, "配置变更": Domain.PLC,
    "文档变更": Domain.DOCU, "Bug修复": Domain.SCPT,
}

IMPACT_LEVEL_TO_SCOPE_MAP = {
    "low": Scope.LOCAL, "LOW": Scope.LOCAL,
    "medium": Scope.MODULE, "MEDIUM": Scope.MODULE,
    "high": Scope.SYSTEM, "HIGH": Scope.SYSTEM,
}
