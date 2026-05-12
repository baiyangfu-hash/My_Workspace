# -*- coding: utf-8 -*-
"""
常量定义
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
    "安全变更": Domain.SAFE, "配置变更": Domain.PLC,  # 配置变更通常属于PLC参数调整
    "文档变更": Domain.DOCU, "Bug修复": Domain.SCPT,  # Bug修复默认归为脚本/代码领域
}

IMPACT_LEVEL_TO_SCOPE_MAP = {
    "low": Scope.LOCAL, "LOW": Scope.LOCAL,
    "medium": Scope.MODULE, "MEDIUM": Scope.MODULE,
    "high": Scope.SYSTEM, "HIGH": Scope.SYSTEM,
}

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

# 默认项目结构模板 - V2.2.0 重组后5类模板
DEFAULT_TEMPLATES = [
    {
        "id": "TPL-FULLLINE-AUTO-001",
        "name": "自动化整线项目",
        "version": "V1.0.0",
        "compiler": "Step7/TIA Portal + Python",
        "scene": "多PLC协同自动化整线项目",
        "description": "包含PLC、HMI、机器人、上位机、Eplan电气、机械设计、通讯协议的完整整线结构",
        "is_builtin": True,
        "business_lines": ["ZD", "DJ"],
        "structure": [
            {"path": "00_项目管理/01_立项与需求", "required": True, "description": "立项表、需求分析"},
            {"path": "00_项目管理/02_进度与风险", "required": True, "description": "进度计划、风险管理"},
            {"path": "00_项目管理/04_变更管理/01_变更单/CHG-PLC", "required": True, "description": "PLC类变更单"},
            {"path": "00_项目管理/04_变更管理/01_变更单/CHG-ELEC", "required": False, "description": "电气类变更单"},
            {"path": "00_项目管理/04_变更管理/01_变更单/CHG-MECH", "required": False, "description": "机械类变更单"},
            {"path": "00_项目管理/05_资源管理", "required": True, "description": "资源分配、成本预算"},
            {"path": "10_技术设计/11_Eplan电气/Export_PDF", "required": True, "description": "电气原理图(PDF)"},
            {"path": "10_技术设计/11_Eplan电气/Source", "required": True, "description": "Eplan源文件"},
            {"path": "10_技术设计/12_机械结构/3D_Models", "required": True, "description": "3D模型和BOM"},
            {"path": "10_技术设计/12_机械结构/2D_Drawings", "required": False, "description": "2D工程图"},
            {"path": "10_技术设计/13_通讯与协议", "required": True, "description": "通讯配置和协议文档"},
            {"path": "20_软件程序/21_PLC_Autoshop/Source", "required": True, "description": "PLC源代码(Autoshop)"},
            {"path": "20_软件程序/21_PLC_Autoshop/ST结构文本", "required": True, "description": "SCL结构文本(可编译)"},
            {"path": "20_软件程序/21_PLC_Autoshop/Docs", "required": True, "description": "PLC设计文档(IO分配/架构/联锁)"},
            {"path": "20_软件程序/22_HMI_ProFace/Source", "required": False, "description": "HMI源文件"},
            {"path": "20_软件程序/22_HMI_ProFace/Docs", "required": False, "description": "HMI设计文档"},
            {"path": "20_软件程序/23_机器人程序", "required": False, "description": "机器人控制程序"},
            {"path": "20_软件程序/24_上位机与脚本/Python_Scripts", "required": False, "description": "上位机Python脚本"},
            {"path": "30_设备配置/驱动器参数", "required": True, "description": "变频器/伺服驱动参数表"},
            {"path": "30_设备配置/智能模块配置", "required": True, "description": "远程IO/安全模块配置"},
            {"path": "40_交付与文档/41_操作手册", "required": True, "description": "设备操作手册"},
            {"path": "40_交付与文档/43_验收清单", "required": True, "description": "验收检查表(FAT/SAT)"},
            {"path": "40_交付与文档/44_培训资料", "required": True, "description": "培训记录和教材"},
            {"path": "40_交付与文档/45_故障排查指南", "required": True, "description": "故障排除手册"},
            {"path": "40_交付与文档/46_维护计划", "required": True, "description": "维护手册和备件清单"},
            {"path": "07_交付文档/04_项目总结报告", "required": True, "description": "项目总结和经验教训"},
            {"path": "90_知识库_本项目", "required": False, "description": "项目知识库(选型/最佳实践/避坑指南)"},
        ],
        "templates": [
            {
                "path": ".gitignore",
                "type": "config",
                "content": "# PLC Project\n*.zap\n*.zap16\n*.ap16\n*.ap19\n\n# Eplan\n*.elk\n*.zkp\n\n# Backup\n*.bak\n*~\n\n# Logs\n*.log\nlogs/\n\n# OS\n.DS_Store\nThumbs.db\n"
            },
            {
                "path": "README.md",
                "type": "document",
                "spec_id": "SPEC-DOC-README-001",
                "content": "# {project_name}\n\n## 项目信息\n- **编号**: {project_code}\n- **名称**: {project_name}\n- **业务线**: {business_line}\n- **负责人**: {manager}\n- **创建日期**: {create_date}\n- **模板**: TPL-FULLLINE-AUTO-001 (自动化整线)\n\n## 项目概述\n{description}\n\n## 目录结构\n详见各目录README.md\n"
            },
            {
                "path": "00_项目管理/01_立项与需求/{project_code}_项目立项表.md",
                "type": "document",
                "spec_id": "SPEC-DOC-INIT-001",
                "content": "# {project_name} 项目立项表\n\n| 项目 | 内容 |\n|------|------|\n| 编号 | {project_code} |\n| 名称 | {project_name} |\n| 业务线 | {business_line} |\n| 负责人 | {manager} |\n| 日期 | {create_date} |\n| 版本 | V1.0.0 |\n| 使用模板 | {template_id} ({template_name}) |\n\n## 概述\n{description}\n\n## 整线范围\n- PLC站数: \n- HMI数量: \n- 机器人/轴数: \n- 上位机接口: \n\n## 里程碑\n| 阶段 | 计划完成 | 负责人 |\n|------|----------|--------|\n| 电气设计 | | |\n| 机械安装 | | |\n| PLC编程 | | |\n| 调试验收 | | |\n"
            },
            {
                "path": "00_项目管理/01_立项与需求/{project_code}_需求分析文档.md",
                "type": "document",
                "spec_id": "SPEC-DOC-REQ-001",
                "content": "# {project_name} 需求分析文档\n\n## 功能需求\n### 自动化功能\n### 安全功能\n### 通讯需求\n\n## IO统计\n| 类型 | 数量 |\n|------|------|\n| DI | |\n| DO | |\n| AI | |\n| AO | |\n\n## 性能指标\n- 生产节拍:\n- 设备OEE目标:\n"
            },
            {
                "path": "00_项目管理/02_进度与风险/{project_code}_进度计划.md",
                "type": "document",
                "content": "# {project_name} 进度计划\n\n## 阶段划分\n1. 方案设计 (W1-W2)\n2. 电气设计 (W3-W6)\n3. 机械加工 (W4-W8)\n4. 程序开发 (W6-W10)\n5. 现场调试 (W10-W14)\n6. 验收交付 (W14-W16)\n\n## 关键路径\n\n## 风险登记\n| ID | 风险 | 概率 | 影响 | 应对措施 |\n|----|------|:----:|:----:|----------|\n"
            },
            {
                "path": "20_软件程序/21_PLC_Autoshop/Docs/{project_code}_IO分配表.md",
                "type": "document",
                "spec_id": "SPEC-DOC-IO-001",
                "content": "# {project_name} IO分配表\n\n## DI 输入信号\n| 地址 | 符号名 | 描述 | 模块位置 |\n|------|--------|------|----------|\n\n## DO 输出信号\n| 地址 | 符号名 | 描述 | 模块位置 |\n|------|--------|------|----------|\n\n## AI/AO 模拟量\n| 地址 | 范围 | 描述 |\n|------|------|------|\n"
            },
            {
                "path": "20_软件程序/21_PLC_Autoshop/Docs/{project_code}_系统架构设计说明书.md",
                "type": "document",
                "spec_id": "SPEC-DOC-ARCH-001",
                "content": "# {project_name} 系统架构设计\n\n## 1. 系统总览\n\n## 2. 硬件架构\n- CPU型号及数量:\n- 通信网络拓扑:\n\n## 3. 软件架构\n- 程序组织(OB/FC/FB/DB):\n- 数据流设计:\n\n## 4. 接口定义\n- PLC间通讯:\n- 与HMI接口:\n- 与上位机接口:\n"
            },
            {
                "path": "40_交付与文档/41_操作手册/{project_code}_操作手册.md",
                "type": "document",
                "spec_id": "SPEC-DOC-OPMAN-001",
                "content": "# {project_name} 操作手册\n\n## 1. 开机前检查 (7项)\n## 2. 标准开机流程\n## 3. 正常运行监控\n## 4. 正常停机流程\n## 5. 完整关机流程\n## 6. 急停操作SOP\n## 7. 常见报警处理\n\n**版本**: V1.0.0 | **编制日期**: {create_date}\n"
            },
            {
                "path": "40_交付与文档/45_故障排查指南/{project_code}_故障排除手册.md",
                "type": "document",
                "spec_id": "SPEC-DOC-FAULT-001",
                "content": "# {project_name} 故障排除手册\n\n## 诊断方法论 (5步法)\n1. 现象确认 → 2. 信息收集 → 3. 原因定位 → 4. 故障排除 → 5. 验证恢复\n\n## 常见故障案例\n| 编号 | 现象 | 可能原因 | 解决方法 |\n|:----:|------|----------|----------|\n\n## 维修记录模板\n"
            },
            {
                "path": "40_交付与文档/46_维护计划/{project_code}_维护手册.md",
                "type": "document",
                "content": "# {project_name} 维护手册\n\n## 一级维护 (每日/每周)\n## 二级维护 (每月)\n## 三级维护 (每季/半年)\n\n## 备件库存清单\n| 序号 | 物料名称 | 规格 | 最低库存 | 供应商 |\n|:----:|----------|------|:--------:|--------|\n"
            }
        ]
    },
    {
        "id": "TPL-SINGLE-ROBOT-001",
        "name": "单机设备(机器人)",
        "version": "V1.0.0",
        "compiler": "Multi",
        "scene": "单机机器人工作站项目",
        "description": "包含Eplan电气、机械设计、通讯设计和机器人程序设计的单机机器人工作站",
        "is_builtin": True,
        "business_lines": ["DJ"],
        "structure": [
            {"path": "00_项目管理/01_立项与需求", "required": True},
            {"path": "00_项目管理/02_进度与风险", "required": True},
            {"path": "00_项目管理/04_变更管理", "required": True},
            {"path": "00_项目管理/05_资源管理", "required": True},
            {"path": "10_技术设计/11_Eplan电气/Export_PDF", "required": True},
            {"path": "10_技术设计/11_Eplan电气/Source", "required": True},
            {"path": "10_技术设计/12_机械结构/3D_Models", "required": True},
            {"path": "10_技术设计/12_机械结构/2D_Drawings", "required": False},
            {"path": "10_技术设计/13_通讯与协议", "required": True},
            {"path": "20_软件程序/21_PLC_Autoshop/ST结构文本", "required": True},
            {"path": "20_软件程序/21_PLC_Autoshop/Docs", "required": True},
            {"path": "20_软件程序/23_机器人程序", "required": True},
            {"path": "30_设备配置/驱动器参数", "required": True},
            {"path": "40_交付与文档/41_操作手册", "required": True},
            {"path": "40_交付与文档/43_验收清单", "required": True},
            {"path": "40_交付与文档/45_故障排查指南", "required": True},
            {"path": "07_交付文档/04_项目总结报告", "required": True},
        ],
        "templates": [
            {
                "path": ".gitignore",
                "type": "config",
                "content": "# Robot Station Project\n*.zap\n*.bak\n*~\n*.log\nlogs/\n.DS_Store\n"
            },
            {
                "path": "README.md",
                "type": "document",
                "spec_id": "SPEC-DOC-README-001",
                "content": "# {project_name}\n\n- **编号**: {project_code}\n- **模板**: TPL-SINGLE-ROBOT-001 (单机机器人)\n- **负责人**: {manager}\n- **日期**: {create_date}\n\n{description}\n"
            },
            {
                "path": "00_项目管理/01_立项与需求/{project_code}_项目立项表.md",
                "type": "document",
                "spec_id": "SPEC-DOC-INIT-001",
                "content": "# {project_name} 项目立项表\n\n| 项目 | 内容 |\n|------|------|\n| 编号 | {project_code} |\n| 名称 | {project_name} |\n| 业务线 | 单机设备(DJ) |\n| 模板 | 单机设备(机器人) |\n| 负责人 | {manager} |\n| 日期 | {create_date} |\n| 使用模板 | {template_id} ({template_name}) |\n\n## 机器人工作站规格\n- 机器人品牌/型号: \n- 轴数/负载: \n- 控制方式: \n- 安全等级: \n"
            },
            {
                "path": "00_项目管理/01_立项与需求/{project_code}_需求分析文档.md",
                "type": "document",
                "spec_id": "SPEC-DOC-REQ-001",
                "content": "# {project_name} 需求分析\n\n## 工艺需求\n## 机器人运动需求\n## 安全需求 (ISO 10218)\n## IO需求\n## 通讯需求\n"
            },
            {
                "path": "20_软件程序/21_PLC_Autoshop/Docs/{project_code}_IO分配表.md",
                "type": "document",
                "spec_id": "SPEC-DOC-IO-001",
                "content": "# {project_name} IO分配表\n\n## 机器人IO\n| 地址 | 信号 | 描述 |\n|------|------|------|\n\n## 外部设备IO\n| 地址 | 信号 | 描述 |\n|------|------|------|\n"
            },
            {
                "path": "40_交付与文档/41_操作手册/{project_code}_操作手册.md",
                "type": "document",
                "spec_id": "SPEC-DOC-OPMAN-001",
                "content": "# {project_name} 操作手册\n\n## 机器人操作\n## PLC操作\n## 急停处理\n## 日常点检\n"
            },
            {
                "path": "40_交付与文档/45_故障排查指南/{project_code}_故障排除手册.md",
                "type": "document",
                "spec_id": "SPEC-DOC-FAULT-001",
                "content": "# {project_name} 故障排除手册\n\n## 机器人故障\n## PLC故障\n## 通讯故障\n## 机械故障\n"
            }
        ]
    },
    {
        "id": "TPL-SINGLE-PLC-001",
        "name": "单机设备(PLC+HMI)",
        "version": "V1.0.0",
        "compiler": "Step7/TIA Portal + ProFace",
        "scene": "PLC自动化单机设备",
        "description": "包含Eplan电气、机械设计、通讯设计、PLC程序设计和HMI界面设计的标准单机设备模板",
        "is_builtin": True,
        "business_lines": ["DJ", "ZD"],
        "structure": [
            {"path": "00_项目管理/01_立项与需求", "required": True, "description": "立项表、需求分析"},
            {"path": "00_项目管理/02_进度与风险", "required": True, "description": "进度计划、风险管理"},
            {"path": "00_项目管理/04_变更管理/01_变更单/CHG-PLC", "required": True, "description": "PLC类变更单"},
            {"path": "00_项目管理/04_变更管理/01_变更单/CHG-SCPT", "required": False, "description": "脚本类变更单"},
            {"path": "00_项目管理/04_变更管理/01_变更单/CHG-DOCU", "required": False, "description": "文档类变更单"},
            {"path": "00_项目管理/05_资源管理", "required": True, "description": "资源分配、成本预算"},
            {"path": "10_技术设计/11_Eplan电气/Export_PDF", "required": True, "description": "电气图纸(PDF)"},
            {"path": "10_技术设计/11_Eplan电气/Source", "required": True, "description": "Eplan源文件"},
            {"path": "10_技术设计/12_机械结构/3D_Models", "required": True, "description": "3D模型/BOM"},
            {"path": "10_技术设计/13_通讯与协议", "required": True, "description": "通讯配置"},
            {"path": "20_软件程序/21_PLC_Autoshop/Source", "required": True, "description": "PLC源代码"},
            {"path": "20_软件程序/21_PLC_Autoshop/ST结构文本", "required": True, "description": "SCL结构文本"},
            {"path": "20_软件程序/21_PLC_Autoshop/Docs", "required": True, "description": "PLC文档(IO/架构/联锁/变量表)"},
            {"path": "20_软件程序/22_HMI_ProFace/Docs", "required": False, "description": "HMI文档"},
            {"path": "30_设备配置/驱动器参数", "required": True, "description": "变频器/伺服参数"},
            {"path": "30_设备配置/智能模块配置", "required": True, "description": "IO模块配置"},
            {"path": "40_交付与文档/41_操作手册", "required": True, "description": "操作手册"},
            {"path": "40_交付与文档/42_仪表手册", "required": False, "description": "仪表说明书"},
            {"path": "40_交付与文档/43_验收清单", "required": True, "description": "验收检查表"},
            {"path": "40_交付与文档/44_培训资料", "required": True, "description": "培训记录"},
            {"path": "40_交付与文档/45_故障排查指南", "required": True, "description": "故障排除手册"},
            {"path": "40_交付与文档/46_维护计划", "required": True, "description": "维护手册/备件"},
            {"path": "07_交付文档/04_项目总结报告", "required": True, "description": "项目总结"},
            {"path": "90_知识库_本项目", "required": False, "description": "知识库"},
        ],
        "templates": [
            {
                "path": ".gitignore",
                "type": "config",
                "content": "# PLC Single Station\n*.zap\n*.zap16\n*.ap16\n*.ap19\n*.al18\n*.s7p\n*.s7s\n*.bak\n*~\n*.log\nlogs/\n.DS_Store\nThumbs.db\n"
            },
            {
                "path": "README.md",
                "type": "document",
                "spec_id": "SPEC-DOC-README-001",
                "content": "# {project_name}\n\n- **编号**: {project_code}\n- **模板**: TPL-SINGLE-PLC-001 (单机设备PLC+HMI)\n- **负责人**: {manager}\n- **日期**: {create_date}\n\n{description}\n"
            },
            {
                "path": "00_项目管理/01_立项与需求/{project_code}_项目立项表.md",
                "type": "document",
                "spec_id": "SPEC-DOC-INIT-001",
                "content": "# {project_name} 项目立项表\n\n| 项目 | 内容 |\n|------|------|\n| 编号 | {project_code} |\n| 名称 | {project_name} |\n| 业务线 | {business_line} |\n| 负责人 | {manager} |\n| 日期 | {create_date} |\n| 版本 | V1.0.0 |\n| 使用模板 | {template_id} ({template_name}) |\n\n## 设备概况\n- 设备类型:\n- 控制方式: PLC+HMI\n- 主要工艺:\n\n## IO概览\n| DI | DO | AI | AO |\n|:--:|:--:|:--:|:--:|\n|   |   |   |   |\n"
            },
            {
                "path": "00_项目管理/01_立项与需求/{project_code}_需求分析文档.md",
                "type": "document",
                "spec_id": "SPEC-DOC-REQ-001",
                "content": "# {project_name} 需求分析文档\n\n## 1. 功能需求\n### 1.1 主工艺功能\n### 1.2 安全保护功能\n### 1.3 操作模式(自动/手动/维护)\n\n## 2. IO需求\n### 2.1 输入信号(DI/AI)\n### 2.2 输出信号(DO/AO)\n\n## 3. 通讯需求\n### 3.1 HMI通讯\n### 3.2 上位机(预留)\n\n## 4. 性能要求\n- PLC扫描周期:\n- 急停响应时间:\n- 定位精度:\n"
            },
            {
                "path": "20_软件程序/21_PLC_Autoshop/Docs/{project_code}_IO分配表.md",
                "type": "document",
                "spec_id": "SPEC-DOC-IO-001",
                "content": "# {project_name} IO分配表\n\n## DI - 数字输入\n| 地址 | 符号名 | 描述 | 模块 | 备注 |\n|------|--------|------|------|------|\n\n## DO - 数字输出\n| 地址 | 符号名 | 描述 | 模块 | 备注 |\n|------|--------|------|------|------|\n\n## AI - 模拟输入\n| 地址 | 范围 | 描述 | 模块 |\n|------|------|------|------|\n\n## AO - 模拟输出\n| 地址 | 范围 | 描述 | 模块 |\n|------|------|------|------|\n"
            },
            {
                "path": "20_软件程序/21_PLC_Autoshop/Docs/{project_code}_PLC程序设计总文档.md",
                "type": "document",
                "spec_id": "SPEC-DOC-PLCDESIGN-001",
                "content": "# {project_name} PLC程序设计总文档\n\n## 1. 程序架构\n### OB组织块列表\n### FB/FC功能块清单\n### DB数据块清单\n\n## 2. 主要功能块说明\n\n## 3. 变量命名规范\n\n## 4. 联锁逻辑说明\n"
            },
            {
                "path": "20_软件程序/21_PLC_Autoshop/Docs/{project_code}_系统架构设计说明书.md",
                "type": "document",
                "spec_id": "SPEC-DOC-ARCH-001",
                "content": "# {project_name} 系统架构设计\n\n## 1. 硬件配置\n### 1.1 CPU选型\n### 1.2 IO模块清单\n### 1.3 网络拓扑\n\n## 2. 软件架构\n### 2.1 程序组织\n### 2.2 数据流\n### 2.3 接口定义\n\n## 3. HMI接口规划\n"
            },
            {
                "path": "20_软件程序/21_PLC_Autoshop/Docs/{project_code}_联锁逻辑设计说明书.md",
                "type": "document",
                "spec_id": "SPEC-DOC-INTERLOCK-001",
                "content": "# {project_name} 联锁逻辑设计\n\n## 1. 正向联锁(防堆积)\n## 2. 反向联锁(故障传播)\n## 3. 安全联锁\n## 4. 启停顺序逻辑\n"
            },
            {
                "path": "10_技术设计/11_Eplan电气/Export_PDF/{project_code}_电气图纸清单.md",
                "type": "document",
                "spec_id": "SPEC-DOC-EPLAN-001",
                "content": "# {project_name} 电气图纸清单\n\n## 图纸目录\n| 序号 | 图纸名称 | 图纸编号 | 版本 | 状态 |\n|:----:|----------|----------|:----:|:----:|\n\n## 绘制规范\n"
            },
            {
                "path": "10_技术设计/11_Eplan电气/Source/{project_code}_PLC硬件配置表.md",
                "type": "document",
                "spec_id": "SPEC-DOC-HWCONFIG-001",
                "content": "# {project_name} PLC硬件配置表\n\n## CPU\n## IO模块\n## 通讯模块\n## 电源计算\n"
            },
            {
                "path": "10_技术设计/12_机械结构/3D_Models/{project_code}_机械BOM清单.md",
                "type": "document",
                "spec_id": "SPEC-DOC-MECHBOM-001",
                "content": "# {project_name} 机械BOM清单\n\n## 标准件\n## 加工件\n## 外购件\n## 总重估算\n"
            },
            {
                "path": "40_交付与文档/41_操作手册/{project_code}_操作手册.md",
                "type": "document",
                "spec_id": "SPEC-DOC-OPMAN-001",
                "content": "# {project_name} 操作手册\n\n## 1. 开机前检查 (7项)\n## 2. 标准开机流程\n## 3. 运行状态监控\n## 4. 正常停机流程\n## 5. 完整关机流程\n## 6. 急停操作SOP\n## 7. 报警代码速查\n\n**版本**: V1.0.0 | **编制**: {create_date}\n"
            },
            {
                "path": "40_交付与文档/45_故障排查指南/{project_code}_故障排除手册.md",
                "type": "document",
                "spec_id": "SPEC-DOC-FAULT-001",
                "content": "# {project_name} 故障排除手册\n\n## 诊断5步法\n## PLC系统故障\n## 变频器/驱动器故障\n## 机械系统故障\n## 传感器故障\n## 维修记录\n"
            },
            {
                "path": "40_交付与文档/46_维护计划/{project_code}_维护手册.md",
                "type": "document",
                "content": "# {project_name} 维护手册\n\n## 一级维护(每日/每周)\n## 二级维护(每月)\n## 三级维护(季/半年)\n## 备件库存\n## 维护记录\n"
            },
            {
                "path": "40_交付与文档/43_验收清单/{project_code}_验收检查表.md",
                "type": "document",
                "spec_id": "SPEC-DOC-ACCEPT-001",
                "content": "# {project_name} 验收检查表\n\n## 文档验收 (15%)\n## 安装质量 (10%)\n## 安全功能 (25%, 一票否决)\n## 功能性能 (35%)\n## 培训效果 (15%)\n"
            },
            {
                "path": "40_交付与文档/44_培训资料/{project_code}_培训记录.md",
                "type": "document",
                "spec_id": "SPEC-DOC-TRAIN-001",
                "content": "# {project_name} 培训记录\n\n## 培训日程\n## 参训人员\n## 考核成绩\n## 证书发放\n"
            },
            {
                "path": "07_交付文档/04_项目总结报告.md",
                "type": "document",
                "spec_id": "SPEC-DOC-SUMMARY-001",
                "content": "# {project_name} 项目总结报告\n\n## 执行概况\n## 技术成果\n## 成本分析\n## 经验教训\n## 后续建议\n"
            }
        ]
    },
    {
        "id": "TPL-UPGRADE-STD-001",
        "name": "系统升级改造",
        "version": "V1.0.0",
        "compiler": "Multi",
        "scene": "现有系统升级改造项目",
        "description": "包含现状评估、升级方案、回滚方案的标准改造升级模板",
        "is_builtin": True,
        "business_lines": ["XT"],
        "structure": [
            {"path": "00_项目管理/01_现状评估", "required": True, "description": "现有系统评估报告"},
            {"path": "00_项目管理/02_升级方案", "required": True, "description": "升级方案设计书"},
            {"path": "00_项目管理/03_回滚方案", "required": True, "description": "回滚预案"},
            {"path": "00_项目管理/04_实施记录", "required": True, "description": "升级实施过程记录"},
            {"path": "00_项目管理/05_变更管理", "required": True, "description": "改造期间变更管理"},
            {"path": "10_技术设计/差异分析", "required": True, "description": "新旧系统差异对比"},
            {"path": "20_软件程序/新旧程序对照", "required": True, "description": "程序迁移对照表"},
            {"path": "40_交付与文档/验收确认", "required": True, "description": "升级后验收确认"},
            {"path": "90_知识库/遗留问题", "required": False, "description": "已知遗留问题追踪"},
        ],
        "templates": [
            {
                "path": ".gitignore",
                "type": "config",
                "content": "# Upgrade Project\n*.bak\n*~\n*.log\nold_version/\nbackup/\n"
            },
            {
                "path": "README.md",
                "type": "document",
                "spec_id": "SPEC-DOC-README-001",
                "content": "# {project_name}\n\n- **编号**: {project_code}\n- **模板**: TPL-UPGRADE-STD-001 (系统升级改造)\n- **负责人**: {manager}\n- **日期**: {create_date}\n\n{description}\n"
            },
            {
                "path": "00_项目管理/01_现状评估/{project_code}_现状评估报告.md",
                "type": "document",
                "content": "# {project_name} 现状评估报告\n\n## 1. 现有系统概况\n## 2. 存在问题清单\n## 3. 性能瓶颈分析\n## 4. 改造必要性评估\n## 5. 风险评估\n"
            },
            {
                "path": "00_项目管理/02_升级方案/{project_code}_升级方案设计书.md",
                "type": "document",
                "content": "# {project_name} 升级方案设计书\n\n## 1. 升级目标\n## 2. 技术方案\n## 3. 实施步骤\n## 4. 时间计划\n## 5. 资源需求\n## 6. 预算估算\n## 7. 回滚预案\n"
            },
            {
                "path": "00_项目管理/03_回滚方案/{project_code}_回滚预案.md",
                "type": "document",
                "content": "# {project_name} 回滚预案\n\n## 触发条件\n## 回滚步骤\n## 回滚时间窗口\n## 数据备份策略\n## 验证方法\n"
            },
            {
                "path": "00_项目管理/04_实施记录/{project_code}_实施日志.md",
                "type": "document",
                "content": "# {project_name} 升级实施日志\n\n| 日期 | 步骤 | 执行人 | 结果 | 问题 |\n|------|------|:------:|:----:|------|\n"
            },
            {
                "path": "40_交付与文档/验收确认/{project_code}_升级验收确认.md",
                "type": "document",
                "content": "# {project_name} 升级验收确认\n\n## 功能验证\n## 性能对比(升级前vs升级后)\n## 用户签字确认\n## 移交清单\n"
            }
        ]
    },
    {
        "id": "TPL-UPPER-STD-001",
        "name": "上位机/数据系统",
        "version": "V1.0.0",
        "compiler": "Flask/Django / Python",
        "scene": "上位机/MES/数据采集/可视化系统",
        "description": "纯软件Python项目，含API接口、数据库、前端展示，适用于数据采集/MES/Web应用",
        "is_builtin": True,
        "business_lines": ["SW"],
        "structure": [
            {"path": "00_项目基础信息", "required": True, "description": "立项表、需求"},
            {"path": "01_项目文档", "required": True, "description": "设计文档、API文档"},
            {"path": "02_需求设计", "required": True, "description": "需求、架构、DB设计"},
            {"path": "03_主程序/01_主程序核心代码/src", "required": True, "description": "源代码"},
            {"path": "03_主程序/01_主程序核心代码/tests", "required": True, "description": "测试代码"},
            {"path": "03_主程序/01_主程序核心_code/config", "required": False, "description": "配置文件"},
            {"path": "04_变更管理", "required": True, "description": "变更管理(V2.1.0)"},
            {"path": "06_测试相关/01_测试用例", "required": True, "description": "测试用例"},
            {"path": "06_测试相关/02_测试报告", "required": True, "description": "测试报告"},
            {"path": "07_部署文档", "required": True, "description": "部署指南、运维手册"},
            {"path": "19_交付物", "required": True, "description": "可交付成果"},
        ],
        "templates": [
            {
                "path": ".gitignore",
                "type": "config",
                "content": "# Python\n__pycache__/\n*.py[cod]\n*$py.class\n*.so\nbuild/\ndist/\n*.egg-info/\n\n# IDE\n.vscode/\n.idea/\n\n# Env\n.env\n.venv/\n\n# Data\n*.csv\n*.db\n\n# Logs\n*.log\nlogs/\n"
            },
            {
                "path": "README.md",
                "type": "document",
                "spec_id": "SPEC-DOC-README-001",
                "content": "# {project_name}\n\n- **编号**: {project_code}\n- **模板**: TPL-UPPER-STD-001 (上位机/数据系统)\n- **负责人**: {manager}\n- **日期**: {create_date}\n\n{description}\n\n## 快速开始\n```bash\npip install -r requirements.txt\npython main.py\n```\n"
            },
            {
                "path": "00_项目基础信息/0-项目立项表_PROJ-V1.0.0.md",
                "type": "document",
                "spec_id": "SPEC-DOC-INIT-001",
                "content": "# {project_name} 项目立项表\n\n| 项目 | 内容 |\n|------|------|\n| 编号 | {project_code} |\n| 名称 | {project_name} |\n| 业务线 | 软件开发(SW) |\n| 负责人 | {manager} |\n| 日期 | {create_date} |\n| 使用模板 | {template_id} ({template_name}) |\n\n## 技术栈\n- 语言: Python 3.x\n- 框架: \n- 数据库: \n- 部署: \n\n## 核心目标\n{description}\n"
            },
            {
                "path": "01_项目文档/1-需求分析文档_REQ-V1.0.0.md",
                "type": "document",
                "spec_id": "SPEC-DOC-REQ-001",
                "content": "# {project_name} 需求分析\n\n## 功能需求\n### API接口\n### 数据处理\n### 可视化\n\n## 非功能需求\n### 性能\n### 安全\n### 兼容性\n"
            },
            {
                "path": "03_主程序/01_主程序核心代码/main.py",
                "type": "code",
                "content": "#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\n\"\"\"\n{project_name}\nVersion: V1.0.0\nDate: {create_date}\n\"\"\"\n\ndef main():\n    print(\"{project_name} starting...\")\n\nif __name__ == \"__main__\":\n    main()\n"
            },
            {
                "path": "03_主程序/01_主程序核心_code/requirements.txt",
                "type": "config",
                "content": "# {project_name} Dependencies\n# Core\nflask>=3.0\nsqlalchemy>=2.0\n\n# Dev\npytest>=7.4\nblack>=24.0\n"
            },
            {
                "path": "03_主程序/01_主程序核心_code/src/__init__.py",
                "type": "code",
                "content": "# -*- coding: utf-8 -*-\n\"\"\"{project_name} src package\"\"\"\n__version__ = \"1.0.0\"\n"
            },
            {
                "path": "07_部署文档/部署指南.md",
                "type": "document",
                "content": "# {project_name} 部署指南\n\n## 环境准备\n## 安装步骤\n## 配置说明\n## 启动/停止\n## 监控\n"
            }
        ]
    },
]
