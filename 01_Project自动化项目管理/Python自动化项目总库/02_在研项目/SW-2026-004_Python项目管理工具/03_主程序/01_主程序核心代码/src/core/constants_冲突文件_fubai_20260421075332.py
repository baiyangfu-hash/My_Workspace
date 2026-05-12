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

# 业务线模板关联（按推荐优先级排序）- V2.3.0 重组后6类模板
BUSINESS_LINE_TEMPLATES = {
    BusinessLine.DEVICE.value: ["TPL-SINGLE-PLC-S001", "TPL-SINGLE-PLC-M001", "TPL-SINGLE-ROBOT-001"],
    BusinessLine.AUTOMATION.value: ["TPL-FULLLINE-AUTO-001", "TPL-SINGLE-PLC-M001"],
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

# 默认项目结构模板 - V2.3.0 重组后6类模板（对齐参考规范06_项目模板规范）
DEFAULT_TEMPLATES = [
    {
        "id": "TPL-FULLLINE-AUTO-001",
        "name": "自动化整线项目",
        "version": "V2.0.0",
        "compiler": "Step7/TIA Portal + Python",
        "scene": "多PLC协同自动化整线项目",
        "description": "V2.0.0 整线项目模板: 包含项目管理(00)、技术设计(10)、软件程序(20)、设备配置(30)、交付文档(40)、项目收尾(50)、知识库(90)七大连续编号模块，覆盖PLC/HMI/机器人/上位机/Eplan/机械/通讯全专业",
        "is_builtin": True,
        "business_lines": ["ZD", "DJ"],
        "structure": [
            {"path": "00_项目管理/01_立项与需求", "required": True, "description": "立项表、需求分析"},
            {"path": "00_项目管理/02_进度与风险", "required": True, "description": "进度计划、风险管理"},
            {"path": "00_项目管理/04_变更管理/01_变更单", "required": True, "description": "变更单(扁平结构)"},
            {"path": "00_项目管理/04_变更管理/03_变更管理规范", "required": False, "description": "变更管理流程规范"},
            {"path": "00_项目管理/04_变更管理/04_变更记录", "required": True, "description": "版本变更台帐"},
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
            {"path": "50_项目收尾/04_项目总结报告", "required": True, "description": "项目总结和经验教训"},
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
                "path": "00_项目管理/01_立项与需求/项目立项表.md",
                "type": "document",
                "spec_id": "SPEC-DOC-INIT-001",
                "content": "# {project_name} 项目立项表\n\n| 项目 | 内容 |\n|------|------|\n| 编号 | {project_code} |\n| 名称 | {project_name} |\n| 业务线 | {business_line} |\n| 负责人 | {manager} |\n| 日期 | {create_date} |\n| 版本 | V1.0.0 |\n| 使用模板 | {template_id} ({template_name}) |\n\n## 概述\n{description}\n\n## 整线范围\n- PLC站数: \n- HMI数量: \n- 机器人/轴数: \n- 上位机接口: \n\n## 里程碑\n| 阶段 | 计划完成 | 负责人 |\n|------|----------|--------|\n| 电气设计 | | |\n| 机械安装 | | |\n| PLC编程 | | |\n| 调试验收 | | |\n"
            },
            {
                "path": "00_项目管理/01_立项与需求/需求分析文档.md",
                "type": "document",
                "spec_id": "SPEC-DOC-REQ-001",
                "content": "# {project_name} 需求分析文档\n\n## 功能需求\n### 自动化功能\n### 安全功能\n### 通讯需求\n\n## IO统计\n| 类型 | 数量 |\n|------|------|\n| DI | |\n| DO | |\n| AI | |\n| AO | |\n\n## 性能指标\n- 生产节拍:\n- 设备OEE目标:\n"
            },
            {
                "path": "00_项目管理/02_进度与风险/进度计划.md",
                "type": "document",
                "content": "# {project_name} 进度计划\n\n## 阶段划分\n1. 方案设计 (W1-W2)\n2. 电气设计 (W3-W6)\n3. 机械加工 (W4-W8)\n4. 程序开发 (W6-W10)\n5. 现场调试 (W10-W14)\n6. 验收交付 (W14-W16)\n\n## 关键路径\n\n## 风险登记\n| ID | 风险 | 概率 | 影响 | 应对措施 |\n|----|------|:----:|:----:|----------|\n"
            },
            {
                "path": "20_软件程序/21_PLC_Autoshop/Docs/IO分配表.md",
                "type": "document",
                "spec_id": "SPEC-DOC-IO-001",
                "content": "# {project_name} IO分配表\n\n## DI 输入信号\n| 地址 | 符号名 | 描述 | 模块位置 |\n|------|--------|------|----------|\n\n## DO 输出信号\n| 地址 | 符号名 | 描述 | 模块位置 |\n|------|--------|------|----------|\n\n## AI/AO 模拟量\n| 地址 | 范围 | 描述 |\n|------|------|------|\n"
            },
            {
                "path": "20_软件程序/21_PLC_Autoshop/Docs/系统架构设计说明书.md",
                "type": "document",
                "spec_id": "SPEC-DOC-ARCH-001",
                "content": "# {project_name} 系统架构设计\n\n## 1. 系统总览\n\n## 2. 硬件架构\n- CPU型号及数量:\n- 通信网络拓扑:\n\n## 3. 软件架构\n- 程序组织(OB/FC/FB/DB):\n- 数据流设计:\n\n## 4. 接口定义\n- PLC间通讯:\n- 与HMI接口:\n- 与上位机接口:\n"
            },
            {
                "path": "40_交付与文档/41_操作手册/操作手册.md",
                "type": "document",
                "spec_id": "SPEC-DOC-OPMAN-001",
                "content": "# {project_name} 操作手册\n\n## 1. 开机前检查 (7项)\n## 2. 标准开机流程\n## 3. 正常运行监控\n## 4. 正常停机流程\n## 5. 完整关机流程\n## 6. 急停操作SOP\n## 7. 常见报警处理\n\n**版本**: V1.0.0 | **编制日期**: {create_date}\n"
            },
            {
                "path": "40_交付与文档/45_故障排查指南/故障排除手册.md",
                "type": "document",
                "spec_id": "SPEC-DOC-FAULT-001",
                "content": "# {project_name} 故障排除手册\n\n## 诊断方法论 (5步法)\n1. 现象确认 → 2. 信息收集 → 3. 原因定位 → 4. 故障排除 → 5. 验证恢复\n\n## 常见故障案例\n| 编号 | 现象 | 可能原因 | 解决方法 |\n|:----:|------|----------|----------|\n\n## 维修记录模板\n"
            },
            {
                "path": "40_交付与文档/46_维护计划/维护手册.md",
                "type": "document",
                "content": "# {project_name} 维护手册\n\n## 一级维护 (每日/每周)\n## 二级维护 (每月)\n## 三级维护 (每季/半年)\n\n## 备件库存清单\n| 序号 | 物料名称 | 规格 | 最低库存 | 供应商 |\n|:----:|----------|------|:--------:|--------|\n"
            },
            {
                "path": "00_项目管理/04_变更管理/01_变更单/.gitkeep",
                "content": "",
                "required": True
            },
            {
                "path": "00_项目管理/04_变更管理/03_变更管理规范/042_{project_code}_变更管理流程规范_PM-V2.0.0.md",
                "type": "document",
                "content": "# {project_code} 变更管理流程规范\n\n## 1. 变更管理概述\n本文档定义{project_name}项目的变更管理流程，确保所有变更可控、可追溯、可审计。\n\n## 2. 变更分类\n| 类别 | 编码 | 说明 |\n|------|:----:|------|\n| 电气设计 | ELEC | Eplan原理图/接线图/IO分配表/BOM |\n| 机械结构 | MECH | SolidWorks 3D/装配图/加工图 |\n| PLC程序 | PLC | IEC 61131-3 SCL/ST/LD/GVL |\n| HMI程序 | HMI | 触摸屏画面/变量映射/报警配置 |\n| Python脚本 | SCPT | 数据采集/MES接口/上位机应用 |\n| 工程文档 | DOCU | 设计说明书/操作手册/验收报告 |\n| 安全功能 | SAFE | 急停回路/安全矩阵/SIL评估 |\n\n## 3. 变更流程\n1. **提交** → 填写变更单 → 选择变更类型和影响范围\n2. **评审** → 技术负责人审核 → 根据Scope自动匹配审批层级\n3. **审批** → 按审批层级逐级审批\n4. **实施** → 执行变更 → 更新相关文档\n5. **验证** → 测试验证 → 更新台帐\n6. **关闭** → 归档变更单\n\n## 4. 文件命名规范\n- 变更单：`040_{project_code}_变更单{序号}_CHG-V2.0.0.md`\n- 台帐：`041_{project_code}_版本变更台帐_CHG-V2.1.0.md`\n\n---\n**文档版本**: PM-V2.0.0\n**编制日期**: {current_date}",
                "required": False
            },
            {
                "path": "00_项目管理/04_变更管理/04_变更记录/041_{project_code}_版本变更台帐_CHG-V2.1.0.md",
                "content": "# {project_code} 版本变更台帐\n\n## 1. 项目信息\n- **项目代码**: {project_code}\n- **项目名称**: {project_name}\n- **项目版本**: V1.0.0\n\n## 2. 变更记录\n| 变更单号 | 变更类型 | 变更标题 | 申请日期 | 申请人 | 审批状态 | 实施日期 | 影响文件数 |\n|---------|---------|---------|---------|--------|---------|---------|-----------|\n| (暂无变更记录) | | | | | | | |\n\n## 3. 版本统计\n| 版本 | 变更单数 | 变更日期范围 | 主要变更内容 |\n|------|---------|-------------|-------------|\n| V1.0.0 | 0 | - | 初始版本 |\n\n---\n**文档版本**: CHG-V2.1.0\n**编制日期**: {current_date}\n**编制人**: 系统",
                "required": False
            },
            {
                "path": "00_项目管理/04_变更管理/README.md",
                "content": "# 变更管理目录\n\n## 目录结构\n\n本目录按照 Obsidian 规范 06_项目模板规范/变更管理与模板文件映射文档 组织。\n\n### 01_变更单/\n存放所有变更单文件，采用扁平结构（按序号排列）。\n- 命名格式：`040_{project_code}_变更单{序号}_CHG-V2.0.0.md`\n- 示例：`040_SW-2026-001_变更单 001_CHG-V2.0.0.md`\n\n### 03_变更管理规范/ （可选）\n存放变更管理流程规范说明文件。\n\n### 04_变更记录/\n存放版本变更台帐文件。\n- 文件名：`041_{project_code}_版本变更台帐_CHG-V2.1.0.md`\n- 记录所有变更历史和版本统计\n\n## 使用方式\n1. 创建变更单 → 工具自动生成到 `01_变更单/`\n2. 更新台帐 → 工具自动刷新 `04_变更记录/` 下的台帐文件\n\n---\n**最后更新**: {current_date}",
                "required": False
            }
        ]
    },
    {
        "id": "TPL-SINGLE-ROBOT-001",
        "name": "单机设备(机器人)",
        "version": "V2.0.0",
        "compiler": "Multi",
        "scene": "单机机器人工作站项目",
        "description": "V2.0.0 单机机器人模板: 包含项目管理(00)、技术设计(10)、软件程序(20含机器人子目录)、设备配置(30)、交付文档(40)、项目收尾(50)六大连续编号模块，覆盖Eplan/机械/PLC/机器人全专业",
        "is_builtin": True,
        "business_lines": ["DJ"],
        "structure": [
            {"path": "00_项目管理/01_立项与需求", "required": True},
            {"path": "00_项目管理/02_进度与风险", "required": True},
            {"path": "00_项目管理/04_变更管理/01_变更单", "required": True, "description": "变更单(扁平结构)"},
            {"path": "00_项目管理/04_变更管理/03_变更管理规范", "required": False, "description": "变更管理流程规范"},
            {"path": "00_项目管理/04_变更管理/04_变更记录", "required": True, "description": "版本变更台帐"},
            {"path": "00_项目管理/05_资源管理", "required": True},
            {"path": "10_技术设计/11_Eplan电气/Export_PDF", "required": True},
            {"path": "10_技术设计/11_Eplan电气/Source", "required": True},
            {"path": "10_技术设计/12_机械结构/3D_Models", "required": True},
            {"path": "10_技术设计/12_机械结构/2D_Drawings", "required": False},
            {"path": "10_技术设计/13_通讯与协议", "required": True},
            {"path": "20_软件程序/21_PLC_Autoshop/Source", "required": False, "description": "PLC源代码(Autoshop)"},
            {"path": "20_软件程序/21_PLC_Autoshop/ST结构文本", "required": True, "description": "SCL结构文本(可编译)"},
            {"path": "20_软件程序/21_PLC_Autoshop/Docs", "required": True, "description": "PLC设计文档(IO分配/架构/联锁)"},
            {"path": "20_软件程序/23_机器人程序/Source", "required": True, "description": "机器人源程序(示教/离线编程)"},
            {"path": "20_软件程序/23_机器人程序/Docs", "required": True, "description": "机器人设计文档(IO分配/运动参数/安全配置)"},
            {"path": "20_软件程序/23_机器人程序/仿真", "required": False, "description": "机器人仿真文件"},
            {"path": "30_设备配置/驱动器参数", "required": True},
            {"path": "40_交付与文档/41_操作手册", "required": True},
            {"path": "40_交付与文档/43_验收清单", "required": True},
            {"path": "40_交付与文档/45_故障排查指南", "required": True},
            {"path": "50_项目收尾/04_项目总结报告", "required": True},
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
                "path": "00_项目管理/01_立项与需求/项目立项表.md",
                "type": "document",
                "spec_id": "SPEC-DOC-INIT-001",
                "content": "# {project_name} 项目立项表\n\n| 项目 | 内容 |\n|------|------|\n| 编号 | {project_code} |\n| 名称 | {project_name} |\n| 业务线 | 单机设备(DJ) |\n| 模板 | 单机设备(机器人) |\n| 负责人 | {manager} |\n| 日期 | {create_date} |\n| 使用模板 | {template_id} ({template_name}) |\n\n## 机器人工作站规格\n- 机器人品牌/型号: \n- 轴数/负载: \n- 控制方式: \n- 安全等级: \n"
            },
            {
                "path": "00_项目管理/01_立项与需求/需求分析文档.md",
                "type": "document",
                "spec_id": "SPEC-DOC-REQ-001",
                "content": "# {project_name} 需求分析\n\n## 工艺需求\n## 机器人运动需求\n## 安全需求 (ISO 10218)\n## IO需求\n## 通讯需求\n"
            },
            {
                "path": "20_软件程序/21_PLC_Autoshop/Docs/IO分配表.md",
                "type": "document",
                "spec_id": "SPEC-DOC-IO-001",
                "content": "# {project_name} IO分配表\n\n## 机器人IO\n| 地址 | 信号 | 描述 |\n|------|------|------|\n\n## 外部设备IO\n| 地址 | 信号 | 描述 |\n|------|------|------|\n"
            },
            {
                "path": "40_交付与文档/41_操作手册/操作手册.md",
                "type": "document",
                "spec_id": "SPEC-DOC-OPMAN-001",
                "content": "# {project_name} 操作手册\n\n## 机器人操作\n## PLC操作\n## 急停处理\n## 日常点检\n"
            },
            {
                "path": "40_交付与文档/45_故障排查指南/故障排除手册.md",
                "type": "document",
                "spec_id": "SPEC-DOC-FAULT-001",
                "content": "# {project_name} 故障排除手册\n\n## 机器人故障\n## PLC故障\n## 通讯故障\n## 机械故障\n"
            },
            {
                "path": "00_项目管理/04_变更管理/01_变更单/.gitkeep",
                "content": "",
                "required": True
            },
            {
                "path": "00_项目管理/04_变更管理/03_变更管理规范/042_{project_code}_变更管理流程规范_PM-V2.0.0.md",
                "type": "document",
                "content": "# {project_code} 变更管理流程规范\n\n## 1. 变更管理概述\n本文档定义{project_name}项目的变更管理流程，确保所有变更可控、可追溯、可审计。\n\n## 2. 变更分类\n| 类别 | 编码 | 说明 |\n|------|:----:|------|\n| 电气设计 | ELEC | Eplan原理图/接线图/IO分配表/BOM |\n| 机械结构 | MECH | SolidWorks 3D/装配图/加工图 |\n| PLC程序 | PLC | IEC 61131-3 SCL/ST/LD/GVL |\n| HMI程序 | HMI | 触摸屏画面/变量映射/报警配置 |\n| Python脚本 | SCPT | 数据采集/MES接口/上位机应用 |\n| 工程文档 | DOCU | 设计说明书/操作手册/验收报告 |\n| 安全功能 | SAFE | 急停回路/安全矩阵/SIL评估 |\n\n## 3. 变更流程\n1. **提交** → 填写变更单 → 选择变更类型和影响范围\n2. **评审** → 技术负责人审核 → 根据Scope自动匹配审批层级\n3. **审批** → 按审批层级逐级审批\n4. **实施** → 执行变更 → 更新相关文档\n5. **验证** → 测试验证 → 更新台帐\n6. **关闭** → 归档变更单\n\n## 4. 文件命名规范\n- 变更单：`040_{project_code}_变更单{序号}_CHG-V2.0.0.md`\n- 台帐：`041_{project_code}_版本变更台帐_CHG-V2.1.0.md`\n\n---\n**文档版本**: PM-V2.0.0\n**编制日期**: {current_date}",
                "required": False
            },
            {
                "path": "00_项目管理/04_变更管理/04_变更记录/041_{project_code}_版本变更台帐_CHG-V2.1.0.md",
                "content": "# {project_code} 版本变更台帐\n\n## 1. 项目信息\n- **项目代码**: {project_code}\n- **项目名称**: {project_name}\n- **项目版本**: V1.0.0\n\n## 2. 变更记录\n| 变更单号 | 变更类型 | 变更标题 | 申请日期 | 申请人 | 审批状态 | 实施日期 | 影响文件数 |\n|---------|---------|---------|---------|--------|---------|---------|-----------|\n| (暂无变更记录) | | | | | | | |\n\n## 3. 版本统计\n| 版本 | 变更单数 | 变更日期范围 | 主要变更内容 |\n|------|---------|-------------|-------------|\n| V1.0.0 | 0 | - | 初始版本 |\n\n---\n**文档版本**: CHG-V2.1.0\n**编制日期**: {current_date}\n**编制人**: 系统",
                "required": False
            },
            {
                "path": "00_项目管理/04_变更管理/README.md",
                "content": "# 变更管理目录\n\n## 目录结构\n\n本目录按照 Obsidian 规范 06_项目模板规范/变更管理与模板文件映射文档 组织。\n\n### 01_变更单/\n存放所有变更单文件，采用扁平结构（按序号排列）。\n- 命名格式：`040_{project_code}_变更单{序号}_CHG-V2.0.0.md`\n- 示例：`040_SW-2026-001_变更单 001_CHG-V2.0.0.md`\n\n### 03_变更管理规范/ （可选）\n存放变更管理流程规范说明文件。\n\n### 04_变更记录/\n存放版本变更台帐文件。\n- 文件名：`041_{project_code}_版本变更台帐_CHG-V2.1.0.md`\n- 记录所有变更历史和版本统计\n\n## 使用方式\n1. 创建变更单 → 工具自动生成到 `01_变更单/`\n2. 更新台帐 → 工具自动刷新 `04_变更记录/` 下的台帐文件\n\n---\n**最后更新**: {current_date}",
                "required": False
            }
        ]
    },
    {
        "id": "TPL-SINGLE-PLC-M001",
        "name": "中大型单机设备(PLC+HMI)",
        "version": "V3.0.0",
        "compiler": "Step7/TIA Portal + ProFace + Eplan",
        "scene": "中大型PLC自动化单机设备（IO点数>=100，复杂运动控制）",
        "description": "V3.0.0 中大型单机设备模板: 完整的项目管理流程，包含项目基本信息(00_00)、立项与需求(00_01)、进度与风险(00_02)、沟通管理(00_03)、变更管理(00_04)、资源管理(00_05)、Eplan电气设计(11)、机械结构(12)、软件方案(13)、PLC程序(02)、HMI设计(03)、驱动器配置(04)、测试验证(05)、文档交付(06)、工具配置(07)、技术知识库(08)十四大模块，完全适配项目管理工具的变更管理功能",
        "is_builtin": True,
        "business_lines": ["DJ", "ZD"],
        "structure": [
            {"path": "00_项目管理/00_项目基本信息", "required": True, "description": "项目章程、范围说明书、干系人登记册"},
            {"path": "00_项目管理/01_立项与需求", "required": True, "description": "立项表、PRD、需求分析"},
            {"path": "00_项目管理/02_进度与风险", "required": True, "description": "进度计划、风险管理"},
            {"path": "00_项目管理/03_沟通管理", "required": False, "description": "沟通管理计划"},
            {"path": "00_项目管理/04_变更管理/01_变更单", "required": True, "description": "变更单(扁平结构)"},
            {"path": "00_项目管理/04_变更管理/03_变更管理规范", "required": False, "description": "变更管理流程规范"},
            {"path": "00_项目管理/04_变更管理/04_变更记录", "required": True, "description": "版本变更台帐"},
            {"path": "00_项目管理/05_资源管理", "required": True, "description": "资源分配、成本预算"},
            {"path": "01_需求与设计/11_Eplan电气/Export_PDF", "required": True, "description": "Eplan导出的PDF电气原理图"},
            {"path": "01_需求与设计/11_Eplan电气/Source", "required": True, "description": "Eplan源文件(.edz/.edb)"},
            {"path": "01_需求与设计/11_Eplan电气", "required": False, "description": "Eplan检查清单"},
            {"path": "01_需求与设计/12_机械结构/3D_Models", "required": True, "description": "机械3D模型及BOM"},
            {"path": "01_需求与设计/12_机械结构/2D_Drawings", "required": False, "description": "2D工程图(PDF/DWG)"},
            {"path": "01_需求与设计/13_软件方案", "required": True, "description": "需求规格、系统架构、详细设计"},
            {"path": "02_PLC程序/主程序", "required": True, "description": "PLC主程序源码"},
            {"path": "02_PLC程序/功能块", "required": False, "description": "FB功能块库"},
            {"path": "02_PLC程序/变量表", "required": True, "description": "全局变量表和IO映射"},
            {"path": "02_PLC程序/模块配置", "required": False, "description": "硬件模块配置"},
            {"path": "02_PLC程序/程序文档", "required": True, "description": "IO分配表、程序设计文档、联锁逻辑"},
            {"path": "03_HMI设计/HMI设计规范", "required": False, "description": "HMI视觉和交互规范"},
            {"path": "03_HMI设计/变量绑定", "required": True, "description": "PLC-HMI变量映射"},
            {"path": "03_HMI设计/操作手册", "required": True, "description": "HMI操作手册SOP"},
            {"path": "03_HMI设计/画面文件", "required": False, "description": "ProFace工程文件"},
            {"path": "04_驱动器与设备/驱动器参数", "required": True, "description": "变频器/伺服驱动参数表"},
            {"path": "04_驱动器与设备/设备手册", "required": False, "description": "设备技术手册"},
            {"path": "04_驱动器与设备/传感器使用说明", "required": False, "description": "传感器接线与调试说明"},
            {"path": "05_测试与验证/测试计划", "required": False, "description": "测试策略和进度安排"},
            {"path": "05_测试与验证/测试用例", "required": False, "description": "详细测试用例"},
            {"path": "05_测试与验证/测试报告", "required": True, "description": "测试执行报告"},
            {"path": "05_测试与验证/验证记录", "required": True, "description": "FAT/SAT验收记录"},
            {"path": "06_文档与交付/项目总方案", "required": False, "description": "项目总体方案"},
            {"path": "06_文档与交付/技术文档", "required": True, "description": "技术文档集合"},
            {"path": "06_文档与交付/版本变更记录", "required": True, "description": "版本发布记录"},
            {"path": "06_文档与交付/培训资料", "required": False, "description": "培训教材和考核记录"},
            {"path": "06_文档与交付/验收交付清单", "required": True, "description": "验收检查表和交付物清单"},
            {"path": "07_工具与配置/开发环境配置", "required": True, "description": "开发环境规范和配置"},
            {"path": "07_工具与配置/工具清单", "required": False, "description": "软硬件工具清单"},
            {"path": "07_工具与配置/脚本", "required": False, "description": "自动化辅助脚本"},
            {"path": "08_技术知识库", "required": False, "description": "最佳实践、问题解决方案、技术分享"}
        ],
        "templates": [
            {
                "path": "00_项目管理/任务分配/任务模板.md",
                "type": "document",
                "content": "# 任务模板\n\n## PLC功能迭代模板\n- **任务名称**：[V{版本号}] {功能名称}\n- **关联文档**：{文档链接}\n- **修改内容**：\n- **影响范围**：\n- **文档已更新**：是/否\n- **程序文件**：\n- **状态**：待排期 → 文档更新中 → 开发中 → 仿真调试 → 现场调试 → 已完成\n\n## HMI画面制作模板\n- **任务名称**：[HMI] {画面名称}\n- **关联文档**：HMI设计手册\n- **画面内容**：\n- **绑定变量**：\n- **文档已更新**：是/否\n- **状态**：待制作 → 文档更新中 → 制作中 → 变量绑定 → 测试 → 已完成\n\n## 文档更新模板\n- **任务名称**：[文档] {文档名称} 更新\n- **更新原因**：\n- **更新内容**：\n- **对应程序修改**：\n- **版本号**：\n- **状态**：待更新 → 更新中 → 审核定稿 → 已归档\n\n## Bug修复模板\n- **任务名称**：[Bug] {问题描述}\n- **关联文档**：{文档链接}\n- **问题原因**：\n- **修复方案**：\n- **验证结果**：\n- **状态**：待确认 → 修复中 → 验证中 → 已关闭"
            },
            {
                "path": "00_项目管理/资源管理/资源管理.md",
                "type": "document",
                "content": "# {project_name} 资源管理\n\n## 人员分配\n| 角色 | 姓名 | 职责 | 投入比例 |\n|------|------|------|:--------:|\n| 项目经理 | | | |\n| PLC工程师 | | | |\n| HMI工程师 | | | |\n| 电气工程师 | | | |\n\n## 设备资源\n- 编程电脑:\n- 仿真设备:\n- 调试工具:\n\n## 成本预算\n| 类别 | 预算 | 实际 | 差异 |\n|------|:----:|:----:|:----:|\n"
            },
            {
                "path": "00_项目管理/项目计划/项目计划.md",
                "type": "document",
                "content": "# {project_name} 项目计划\n\n## 项目信息\n- **编号**: {project_code}\n- **创建日期**: {create_date}\n\n## 时间线\n| 阶段 | 计划开始 | 计划完成 | 负责人 | 状态 |\n|------|----------|----------|--------|:----:|\n| 需求分析 | | | | |\n| 方案设计 | | | | |\n| PLC编程 | | | | |\n| HMI制作 | | | | |\n| 仿真调试 | | | | |\n| 现场调试 | | | | |\n| 验收交付 | | | | |\n\n## 里程碑\n| 里程碑 | 计划日期 | 实际日期 | 状态 |\n|--------|----------|----------|:----:|\n| 需求冻结 | | | |\n| FAT验收 | | | |\n| SAT验收 | | | |"
            },
            {
                "path": "00_项目管理/风险评估/风险评估.md",
                "type": "document",
                "content": "# {project_name} 风险评估\n\n## 风险登记表\n| ID | 风险描述 | 概率 | 影响 | 风险等级 | 应对策略 | 负责人 | 状态 |\n|:--:|----------|:----:|:----:|:--------:|----------|--------|:----:|\n\n## 高风险项跟踪\n\n## 风险应对措施\n### 规避\n### 转移\n### 减轻\n### 接受\n"
            },
            {
                "path": "01_需求与设计/11_Eplan电气/Eplan检查清单.md",
                "type": "document",
                "content": "# {project_name} Eplan图纸检查清单\n\n## 图纸完整性检查\n| 序号 | 检查项 | 标准 | 检查结果 | 备注 |\n|:----:|--------|------|:--------:|------|\n| 1 | 主电路原理图 | 含电源、断路器、接触器、热继电器 | □合格 □不合格 | |\n| 2 | 控制回路原理图 | 含PLC IO端子标注 | □合格 □不合格 | |\n| 3 | 安全回路图 | 急停、安全门、光幕联锁 | □合格 □不合格 | |\n| 4 | IO分配图 | DI/DO/AI/AO全部标注 | □合格 □不合格 | |\n| 5 | 端子排接线图 | 端子号与PLC地址对应 | □合格 □不合格 | |\n| 6 | 柜体布局图 | 元器件位置标注 | □合格 □不合格 | |\n| 7 | BOM材料表 | 型号/数量/品牌完整 | □合格 □不合格 | |\n\n## Eplan项目信息\n| 属性 | 值 |\n|------|-----|\n| 项目名称 | |\n| Eplan版本 | |\n| 页框模板 | |\n| 最后修改人 | |\n| 最后修改日期 | |\n\n## 与PLC程序的IO对照\n> 详细IO对照请参考 `13_软件方案/IO分配表.md`\n"
            },
            {
                "path": "01_需求与设计/12_机械结构/BOM模板.md",
                "type": "document",
                "content": "# {project_name} 机械BOM清单\n\n## 标准件BOM\n| 序号 | 物料名称 | 规格/型号 | 品牌 | 数量 | 单位 | 供应商 | 备注 |\n|:----:|----------|----------|------|:----:|------|--------|------|\n\n## 加工件BOM\n| 序号 | 零件名称 | 材料 | 数量 | 加工工艺 | 重量(kg) | 备注 |\n|:----:|----------|------|:----:|----------|:-------:|------|\n\n## 外购件BOM\n| 序号 | 物料名称 | 规格型号 | 品牌 | 数量 | 交货周期 | 单价 | 备注 |\n|:----:|----------|----------|------|:----:|----------|:----:|------|\n\n## 3D模型文件清单\n| 文件名 | 格式 | 版本 | 描述 | 存放位置 |\n|--------|------|:----:|------|----------|\n"
            },
            {
                "path": "01_需求与设计/13_软件方案/需求规格说明书/需求规格说明书.md",
                "type": "document",
                "content": "# {project_name} 需求规格说明书\n\n## 1. 功能需求\n### 1.1 主工艺功能\n### 1.2 安全保护功能\n### 1.3 操作模式（自动/手动/维护）\n\n## 2. IO需求\n### 2.1 输入信号（DI/AI）\n### 2.2 输出信号（DO/AO）\n\n## 3. 通讯需求\n### 3.1 PLC-HMI通讯\n### 3.2 上位机接口（预留）\n\n## 4. 性能指标\n- PLC扫描周期目标:\n- 急停响应时间要求:\n- 定位精度要求:\n- 生产节拍要求:"
            },
            {
                "path": "01_需求与设计/13_软件方案/系统架构设计/系统架构设计.md",
                "type": "document",
                "content": "# {project_name} 系统架构设计\n\n## 1. 硬件架构\n### 1.1 CPU选型及配置\n### 1.2 IO模块清单\n### 1.3 网络拓扑结构\n\n## 2. 软件架构\n### 2.1 程序组织块(OB)\n### 2.2 功能块/函数(FB/FC)层级\n### 2.3 数据块(DB)规划\n### 2.4 主程序调用逻辑\n\n## 3. 接口定义\n### 3.1 PLC-HMI接口变量\n### 3.2 驱动器通讯接口\n### 3.3 外部设备接口\n\n## 4. 数据流设计\n"
            },
            {
                "path": "01_需求与设计/13_软件方案/详细设计说明书/详细设计说明书.md",
                "type": "document",
                "content": "# {project_name} 详细设计说明书\n\n## 1. FB/FC功能块清单\n| 序号 | 名称 | 类型 | 功能描述 | 调用关系 |\n|:----:|------|:----:|----------|----------|\n\n## 2. 数据流图\n\n## 3. 联锁逻辑设计\n### 3.1 正向联锁（防堆积）\n### 3.2 反向联锁（故障传播）\n### 3.3 安全联锁\n### 3.4 启停顺序逻辑\n\n## 4. 关键算法说明\n"
            },
            {
                "path": "02_PLC程序/主程序/主程序说明.md",
                "type": "document",
                "content": "# {project_name} 主程序说明\n\n## OB组织块列表\n| OB类型 | OB号 | 名称 | 功能描述 | 执行周期 |\n|--------|:----:|------|----------|----------|\n\n## 主调用逻辑\n```\nOB1 Main ->\n  |-- FB_SystemInit    // 系统初始化\n  |-- FB_AutoMode      // 自动模式\n  |-- FB_ManualMode    // 手动模式\n  |-- FB_Safety        // 安全联锁\n  |-- FB_Diagnostics   // 诊断\n  |-- FB_Comms         // 通讯处理\n```\n\n## 注意事项\n"
            },
            {
                "path": "02_PLC程序/功能块/功能块说明.md",
                "type": "document",
                "content": "# {project_name} 功能块说明\n\n## FB列表\n| 序号 | FB名称 | 版本 | 功能描述 | 输入参数 | 输出参数 | 状态 |\n|:----:|--------|:----:|----------|----------|----------|:----:|\n\n## 调用关系图\n\n## 版本信息\n> **变更管理通过工具的变更管理模块统一处理，此处仅保留当前有效版本摘要。**\n\n| FB名称 | 当前版本 | 最后更新人 | 更新日期 | 变更摘要 |\n|--------|:--------:|-----------|----------|----------|\n"
            },
            {
                "path": "02_PLC程序/变量表/变量表说明.md",
                "type": "document",
                "content": "# {project_name} 变量表说明\n\n## 全局变量(DB)\n| 变量名 | 数据类型 | 地址 | 初始值 | 描述 |\n|--------|----------|------|:------:|------|\n\n## IO变量映射\n| 符号名 | 绝对地址 | 数据类型 | 描述 | 模块位置 |\n|--------|----------|----------|------|----------|\n\n## 命名规范\n> 参考 `07_工具与配置/开发环境配置/PLC项目规范.md` 中的变量命名规范章节。\n\n### 前缀规则\n| 前缀 | 含义 | 示例 |\n|------|------|------|\n| b_ | 布尔量 | b_Start |\n| n_ | 整数 | n_Speed |\n| r_ | 实数 | r_Temp |\n| st_ | 结构体 | st_DeviceStatus |\n\n## 常量定义\n"
            },
            {
                "path": "02_PLC程序/模块配置/模块配置说明.md",
                "type": "document",
                "content": "# {project_name} 模块配置说明\n\n## 硬件模块配置\n### CPU配置\n| 属性 | 值 |\n|------|-----|\n| 型号 | |\n| 固件版本 | |\n| 内存大小 | |\n\n### IO模块清单\n| 槽位 | 型号 | 类型 | 通道数 | 地址范围 |\n|:----:|------|------|:------:|----------|\n\n### 通讯模块\n| 槽位 | 型号 | 接口类型 | 协议 | 从站地址 |\n|:----:|------|----------|------|:--------:|\n\n## 网络配置\n### PROFINET配置\n### Modbus/串口配置（如有）\n"
            },
            {
                "path": "02_PLC程序/程序文档/IO分配表.md",
                "type": "document",
                "content": "# {project_name} IO分配表\n\n## DI - 数字输入\n| 地址 | 符号名 | 描述 | 模块位置 | 信号类型 |\n|------|--------|------|----------|----------|\n\n## DO - 数字输出\n| 地址 | 符号名 | 描述 | 模块位置 | 负载类型 |\n|------|--------|------|----------|----------|\n\n## AI - 模拟输入\n| 地址 | 符号名 | 描述 | 范围 | 量程 | 单位 |\n|------|--------|------|------|------|------|\n\n## AO - 模拟输出\n| 地址 | 符号名 | 描述 | 范围 | 量程 | 单位 |\n|------|--------|------|------|------|------|\n\n## IO统计汇总\n| 类型 | 已用 | 总计 | 利用率 |\n|------|:----:|:----:|:------:|\n| DI | | | |\n| DO | | | |\n| AI | | | |\n| AO | | | |"
            },
            {
                "path": "02_PLC程序/程序文档/PLC程序设计总文档.md",
                "type": "document",
                "content": "# {project_name} PLC程序设计总文档\n\n## 1. 设计概述\n本节概述{project_name}的PLC整体设计方案，包括程序架构、主要功能模块划分和设计原则。\n\n## 2. 程序架构\n### 2.1 组织块(OB)规划\n### 2.2 功能块(FB/FC)层级结构\n### 2.3 数据块(DB)规划\n\n## 3. 主要功能模块说明\n\n## 4. 变量命名与数据结构\n> 详细命名规范请参考 `07_工具与配置/开发环境配置/PLC项目规范.md`。\n\n## 5. 联锁逻辑总述\n\n## 6. 通讯接口总述\n\n## 7. 安全机制总述\n"
            },
            {
                "path": "02_PLC程序/程序文档/系统架构设计说明书.md",
                "type": "document",
                "content": "# {project_name} 系统架构设计说明书\n\n## 1. 硬件架构\n### 1.1 CPU选型依据\n### 1.2 IO模块配置详情\n### 1.3 网络拓扑结构\n### 1.4 电源系统设计\n\n## 2. 软件架构\n### 2.1 程序组织结构\n#### OB主循环调用链\n#### 中断组织块分配\n### 2.2 功能模块分层\n- 应用层(App): 业务逻辑\n- 功能层(Func): 通用功能\n- 驱动层(Drv): 硬件驱动\n### 2.3 数据流架构\n### 2.4 状态机设计\n\n## 3. 接口定义\n### 3.1 内部接口（FB/FC间）\n### 3.2 外部接口（PLC-HMI/驱动器）\n\n## 4. 性能设计\n### 4.1 扫描周期估算\n### 4.2 内存使用规划\n"
            },
            {
                "path": "02_PLC程序/程序文档/联锁逻辑设计说明书.md",
                "type": "document",
                "content": "# {project_name} 联锁逻辑设计说明书\n\n## 1. 正向联锁（防堆积）\n### 1.1 联锁条件\n### 1.2 时序要求\n### 1.3 实现方式\n\n## 2. 反向联锁（故障传播）\n### 2.1 故障分类\n### 2.2 传播路径\n### 2.3 保护策略\n\n## 3. 安全联锁\n### 3.1 急停回路设计\n### 3.2 安全门/光幕联锁\n### 3.3 使能条件\n\n## 4. 启停顺序逻辑\n### 4.1 启动序列\n### 4.2 正常停止序列\n### 4.3 急停停止序列\n### 4.4 复位恢复序列\n\n## 5. 联锁真值表\n\n## 6. 测试验证要点\n"
            },
            {
                "path": "03_HMI设计/HMI设计规范/HMI设计规范.md",
                "type": "document",
                "content": "# {project_name} HMI设计规范\n\n## 1. 画面总体布局\n### 1.1 分辨率标准\n### 1.2 区域划分（标题栏/操作区/状态区/导航区）\n\n## 2. 颜色规范\n| 用途 | 颜色 | RGB值 | 含义 |\n|------|------|-------|------|\n| 运行 | 绿色 | #00FF00 | 设备正常运行 |\n| 停止 | 灰色 | #808080 | 设备停止 |\n| 报警 | 红色 | #FF0000 | 故障报警 |\n| 警告 | 黄色 | #FFFF00 | 预警提示 |\n| 手动 | 蓝色 | #0000FF | 手动模式 |\n\n## 3. 字体规范\n| 元素 | 字体 | 大小 | 样式 |\n|------|------|:----:|------|\n| 标题 | | 16pt | 加粗 |\n| 正文 | | 12pt | 常规 |\n| 数值显示 | | 14pt | 常规 |\n| 按钮 | | 11pt | 常规 |\n\n## 4. 按钮与控件规范\n\n## 5. 动画效果规范\n\n## 6. 多语言支持（如需）\n"
            },
            {
                "path": "03_HMI设计/变量绑定/变量绑定说明.md",
                "type": "document",
                "content": "# {project_name} PLC-HMI变量绑定说明\n\n## 变量映射表\n| HMI元素 | PLC地址 | 数据类型 | 读写属性 | 描述 | 刷新周期 |\n|----------|----------|----------|:--------:|------|:--------:|\n\n## 按钮类变量\n| 按钮名称 | PLC地址 | 触发方式 | 确认机制 |\n|----------|----------|----------|----------|\n\n## 显示类变量\n| 显示内容 | PLC地址 | 格式化 | 小数位数 |\n|----------|----------|--------|:--------:|\n\n## 报警类变量\n| 报警ID | 触发条件 | PLC地址 | 优先级 | 确认方式 |\n|:-------:|----------|----------|:------:|--------|\n\n## 通讯配置\n- 协议:\n- 端口号:\n- 刷新时间:\n"
            },
            {
                "path": "03_HMI设计/操作手册/操作手册.md",
                "type": "document",
                "content": "# {project_name} HMI操作手册\n\n## 1. 画面索引\n| 画面编号 | 画面名称 | 功能说明 | 访问权限 |\n|:--------:|----------|----------|:--------:|\n\n## 2. 各画面操作说明\n### 2.1 监控主画面\n### 2.2 参数设置画面\n### 2.3 手动操作画面\n### 2.4 报警历史画面\n### 2.5 维护诊断画面\n\n## 3. 权限等级说明\n| 等级 | 名称 | 可操作内容 |\n|:----:|------|----------|\n| 0 | 操作员 | 基本监控、启停 |\n| 1 | 技术员 | 参数修改、手动操作 |\n| 2 | 工程师 | 高级参数、配方管理 |\n| 3 | 管理员 | 用户管理、系统配置 |\n\n## 4. 常见操作流程\n### 4.1 标准开机流程\n### 4.2 标准停机流程\n### 4.3 异常处理流程\n\n## 5. 报警代码速查\n"
            },
            {
                "path": "03_HMI设计/画面文件/画面文件说明.md",
                "type": "document",
                "content": "# {project_name} ProFace工程文件说明\n\n## 工程信息\n| 属性 | 值 |\n|------|-----|\n| 工程名称 | |\n| ProFace版本 | |\n| 目标机型 | |\n| 分辨率 | |\n| 颜色深度 | |\n\n## 画面清单\n| 画面ID | 画面名称 | 文件名 | 尺寸 | 说明 |\n|:------:|----------|--------|------|------|\n\n## 公共资源\n### 公共窗口\n### 公共D脚本\n### 数据库文件\n### 配方数据\n\n## 下载配置\n- 通信端口:\n- 下载线型号:\n- 目标IP/站号:\n\n## 版本记录\n> **变更管理通过工具的变更管理模块统一处理。**\n"
            },
            {
                "path": "03_HMI设计/HMI设计规范.md",
                "type": "document",
                "content": "# {project_name} HMI设计综合规范\n\n## 文档说明\n本文档为{project_name} HMI设计的综合规范文档，汇总了设计规范、变量绑定、操作手册等核心内容。\n\n## 1. 设计总则\n\n## 2. 画面体系\n\n## 3. 变量体系\n\n## 4. 安全与权限\n\n## 5. 相关文档引用\n- [HMI设计规范](./HMI设计规范/HMI设计规范.md) — 详细的视觉和交互规范\n- [变量绑定说明](./变量绑定/变量绑定说明.md) — PLC-HMI变量映射\n- [操作手册](./操作手册/操作手册.md) — 完整操作SOP\n- [画面文件说明](./画面文件/画面文件说明.md) — ProFace工程说明\n"
            },
            {
                "path": "04_驱动器与设备/驱动器参数/驱动器参数说明.md",
                "type": "document",
                "content": "# {project_name} 驱动器参数说明\n\n## 变频器参数\n| 参数号 | 参数名称 | 设定值 | 默认值 | 说明 |\n|:------:|----------|:------:|:------:|------|\n\n## 伺服驱动器参数\n| 参数号 | 参数名称 | 设定值 | 默认值 | 说明 |\n|:------:|----------|:------:|:------:|------|\n\n## 电机铭牌参数\n| 项目 | 值 |\n|------|-----|\n| 型号 | |\n| 功率 | |\n| 额定电流 | |\n| 额定转速 | |\n| 编码器类型 | |\n\n## 通讯参数设置\n"
            },
            {
                "path": "04_驱动器与设备/设备手册/设备手册.md",
                "type": "document",
                "content": "# {project_name} 设备手册\n\n## 设备清单\n| 序号 | 设备名称 | 品牌 | 型号 | 数量 | 安装位置 |\n|:----:|----------|------|------|:----:|----------|\n\n## 各设备技术参数\n\n## 安装要求\n\n## 维护保养要求\n\n## 易损件清单\n| 序号 | 物料名称 | 规格 | 寿命周期 | 最低库存 |\n|:----:|----------|------|----------|:--------:|\n"
            },
            {
                "path": "04_驱动器与设备/传感器使用说明/传感器使用说明.md",
                "type": "document",
                "content": "# {project_name} 传感器使用说明\n\n## 传感器清单\n| 序号 | 传感器类型 | 品牌 | 型号 | 安装位置 | 用途 | 信号类型 |\n|:----:|------------|------|------|----------|------|----------|\n\n## 光电传感器\n### 接线方式\n### 调整方法\n### 常见故障\n\n## 接近开关\n### 接线方式\n### 感应距离调整\n### 常见故障\n\n## 温度/压力等模拟量传感器\n### 量程设定\n### 线性校准\n### 常见故障\n\n## 安全传感器（光幕/安全门开关）\n### 安全等级要求\n### 接线规范\n### 测试方法\n"
            },
            {
                "path": "05_测试与验证/测试计划/测试计划.md",
                "type": "document",
                "content": "# {project_name} 测试计划\n\n## 1. 测试策略\n### 1.1 单元测试\n### 1.2 集成测试\n### 1.3 系统测试\n### 1.4 验收测试(FAT/SAT)\n\n## 2. 测试环境\n| 环境 | 配置 | 状态 |\n|------|------|:----:|\n| 仿真环境 | | |\n| 现场环境 | | |\n\n## 3. 测试进度\n| 阶段 | 计划时间 | 负责人 | 状态 |\n|------|----------|--------|:----:|\n\n## 4. 测试准入/准出标准\n\n## 5. 风险与应对\n"
            },
            {
                "path": "05_测试与验证/测试用例/测试用例.md",
                "type": "document",
                "content": "# {project_name} 测试用例\n\n## PLC功能测试\n| 用例ID | 测试项 | 前置条件 | 操作步骤 | 预期结果 | 实际结果 | 状态 |\n|:------:|--------|----------|----------|----------|----------|:----:|\n\n## HMI功能测试\n| 用例ID | 测试项 | 前置条件 | 操作步骤 | 预期结果 | 实际结果 | 状态 |\n|:------:|--------|----------|----------|----------|----------|:----:|\n\n## 通讯测试\n| 用例ID | 测试项 | 协议 | 测试内容 | 结果 |\n|:------:|--------|------|----------|:----:|\n\n## 安全功能测试\n| 用例ID | 测试项 | 安全等级要求 | 测试方法 | 结果 |\n|:------:|--------|--------------|----------|:----:|\n\n## 性能测试\n| 测试项 | 指标 | 要求值 | 实测值 | 结论 |\n|--------|------|:------:|:------:|:----:|\n"
            },
            {
                "path": "05_测试与验证/测试报告/测试报告.md",
                "type": "document",
                "content": "# {project_name} 测试报告\n\n## 报告信息\n| 属性 | 值 |\n|------|-----|\n| 项目名称 | {project_name} |\n| 测试阶段 | |\n| 测试日期 | |\n| 测试人员 | |\n| 版本 | V1.0.0 |\n\n## 测试总结\n| 类别 | 计划数 | 通过数 | 失败数 | 通过率 |\n|------|:------:|:------:|:------:|:------:|\n\n## 缺陷统计\n| 严重程度 | 数量 | 状态 |\n|----------|:----:|:----:|\n| 致命 | | |\n| 严重 | | |\n| 一般 | | |\n| 建议 | | |\n\n## 测试结论\n\n## 遗留问题清单\n| ID | 问题描述 | 严重程度 | 建议修复期限 |\n|:--:|----------|:--------:|--------------|\n"
            },
            {
                "path": "05_测试与验证/验证记录/验证记录.md",
                "type": "document",
                "content": "# {project_name} 验收记录\n\n## FAT（工厂验收测试）\n### FAT基本信息\n| 属性 | 值 |\n|------|-----|\n| 测试地点 | |\n| 测试日期 | |\n| 客户代表 | |\n| 我方代表 | |\n\n### FAT检查项\n| 序号 | 检查项目 | 标准 | 检查结果 | 备注 |\n|:----:|----------|------|:--------:|------|\n\n### FAT结论\n\n---\n\n## SAT（现场验收测试）\n### SAT基本信息\n| 属性 | 值 |\n|------|-----|\n| 测试地点 | |\n| 测试日期 | |\n| 客户代表 | |\n| 我方代表 | |\n\n### SAT检查项\n| 序号 | 检查项目 | 标准 | 检查结果 | 备注 |\n|:----:|----------|------|:--------:|------|\n\n### SAT结论\n\n---\n\n## 遗留问题及整改跟踪\n"
            },
            {
                "path": "06_文档与交付/项目总方案/项目总方案.md",
                "type": "document",
                "content": "# {project_name} 项目总方案\n\n## 1. 项目背景\n\n## 2. 项目目标\n\n## 3. 项目范围\n\n## 4. 技术方案\n### 4.1 总体方案\n### 4.2 硬件方案\n### 4.3 软件方案\n### 4.4 通讯方案\n\n## 5. 项目计划\n\n## 6. 组织架构\n\n## 7. 质量保证\n\n## 8. 风险管理\n\n## 9. 交付物清单\n\n## 10. 验收标准\n"
            },
            {
                "path": "06_文档与交付/技术文档/IO点表与变量清单.md",
                "type": "document",
                "content": "# {project_name} IO点表与变量清单\n\n## 1. IO点表总览\n### DI点表\n### DO点表\n### AI点表\n### AO点表\n\n## 2. PLC变量清单\n### 全局DB变量\n### M区中间变量\n### 定时器/计数器\n\n## 3. HMI变量清单\n### 位变量\n### 字变量\n### 字符串变量\n\n## 4. 通讯变量映射\n"
            },
            {
                "path": "06_文档与交付/技术文档/PLC程序说明.md",
                "type": "document",
                "content": "# {project_name} PLC程序说明\n\n## 1. 程序概述\n\n## 2. 程序结构\n### OB组织块\n### FB/FC功能块\n### DB数据块\n\n## 3. 主要功能说明\n\n## 4. 关键算法\n\n## 5. 联锁逻辑\n\n## 6. 通讯协议\n\n## 7. 调试要点\n"
            },
            {
                "path": "06_文档与交付/技术文档/HMI设计规范与操作手册.md",
                "type": "document",
                "content": "# {project_name} HMI设计规范与操作手册\n\n## 第一部分：设计规范\n### 画面布局规范\n### 颜色与字体规范\n### 控件使用规范\n\n## 第二部分：操作手册\n### 画面索引\n### 操作流程\n### 权限说明\n### 报警处理\n\n## 第三部分：维护指南\n### 常见问题\n### 备份恢复\n"
            },
            {
                "path": "06_文档与交付/版本变更记录/版本变更记录.md",
                "type": "document",
                "content": "# {project_name} 版本变更记录\n\n> **全局版本摘要台帐，详细变更通过变更管理模块管理。**\n\n## 文档基础信息\n| 属性 | 值 |\n|------|-----|\n| 项目编号 | {project_code} |\n| 项目名称 | {project_name} |\n| 创建日期 | {create_date} |\n| 最后更新 | |\n\n---\n\n## 版本发布记录\n| 版本号 | 发布日期 | 发布类型 | 主要变更内容 | 发布人 | 状态 |\n|:------:|:--------:|:--------:|-------------|:------:|:----:|\n| V1.0.0 | {create_date} | 初始版本 | 项目初始化 | 系统 | 已发布 |\n\n## 各子系统版本对照\n| 子系统 | 当前版本 | 最后更新 | 备注 |\n|--------|:--------:|----------|------|\n| PLC程序 | | |\n| HMI程序 | | |\n| 驱动器参数 | | |\n| 技术文档 | | |"
            },
            {
                "path": "06_文档与交付/培训资料/培训资料.md",
                "type": "document",
                "content": "# {project_name} 培训资料\n\n## 1. 培训计划\n| 场次 | 培训对象 | 培训内容 | 时长 | 培训师 | 日期 | 地点 |\n|:----:|----------|----------|:----:|--------|------|------|\n\n## 2. 培训大纲\n### 2.1 系统概述培训\n### 2.2 PLC操作培训\n### 2.3 HMI操作培训\n### 2.4 日常维护培训\n### 2.5 故障排查培训\n\n## 3. 培训签到表\n| 序号 | 姓名 | 职务 | 所属部门 | 签到时间 |\n|:----:|------|------|----------|----------|\n\n## 4. 考核记录\n| 序号 | 姓名 | 理论成绩 | 操作成绩 | 是否合格 |\n|:----:|------|:--------:|:--------:|:--------:|\n\n## 5. 培训反馈\n"
            },
            {
                "path": "06_文档与交付/验收交付清单/验收交付清单.md",
                "type": "document",
                "content": "# {project_name} 验收交付清单\n\n## 一、文档验收\n| 序号 | 交付文档 | 版本 | 份数 | 验收情况 | 备注 |\n|:----:|----------|:----:|:----:|:--------:|------|\n\n## 二、程序验收\n| 序号 | 程序文件 | 版本 | 格式 | 验收情况 | 备注 |\n|:----:|----------|:----:|------|:--------:|------|\n\n## 三、硬件验收\n| 序号 | 设备/材料 | 型号规格 | 数量 | 验收情况 | 备注 |\n|:----:|------------|----------|:----:|:--------:|------|\n\n## 四、功能验收\n| 序号 | 验收项目 | 验收标准 | 测试方法 | 结果 | 签字 |\n|:----:|----------|----------|----------|:----:|------|\n\n## 五、培训验收\n| 序号 | 培训内容 | 参训人数 | 考核通过率 | 签字 |\n|:----:|----------|:--------:|:--------:|------|\n\n## 六、遗留问题清单\n| 序号 | 问题描述 | 解决方案 | 责任人 | 计划完成日期 |\n|:----:|----------|----------|--------|----------|\n\n## 七、最终验收结论\n- **验收结论**: □通过 □有条件通过 □不通过\n- **客户签字**:\n- **日期**:\n- **我方签字**:\n- **日期**:"
            },
            {
                "path": "07_工具与配置/开发环境配置/PLC项目规范.md",
                "type": "document",
                "content": "# PLC项目开发规范\n\n## 1. 项目命名规范\n### 1.1 项目编码规则\n- 格式: `{业务线代码}-{年份}-{序号}`\n- 示例: `DJ-2026-001`\n- 业务线代码: DJ(单机设备), ZD(自动化整线), XT(系统升级), SW(软件开发), WX(维保项目)\n\n### 1.2 文件命名规则\n- 程序文件: `{项目代码}_{功能名}.scl`\n- 文档文件: `{项目代码}_{文档名}.md`\n- 配置文件: `{项目代码}_{用途}.cfg`\n\n## 2. 变量命名规范\n### 2.1 基本前缀规则\n| 前缀 | 数据类型 | 含义 | 示例 |\n|------|----------|------|------|\n| b_ | BOOL | 布尔量 | b_Start, b_Emergency |\n| n_ | INT/DINT/WORD/DWORD | 整数/字 | n_Speed, n_Mode, w_Status |\n| r_ | REAL/LREAL | 实数 | r_Temp, r_Position |\n| c_ | CHAR/WCHAR | 字符 | c_Unit |\n| s_ | STRING/WSTRING | 字符串 | s_Message |\n| st_ | UDT/STRUCT | 结构体 | st_MotorInfo |\n| ary_ | ARRAY | 数组 | ary_InputData |\n| e_ | ENUM | 枚举 | e_AutoMode |\n\n### 2.2 功能域前缀\n| 前缀 | 功能域 | 示例 |\n|------|--------|------|\n| sys_ | 系统全局 | sys_b_Run |\n| dev_ | 设备相关 | dev_Motor_b_On |\n| hmi_ | HMI接口 | hmi_n_SetSpeed |\n| diag_ | 诊断相关 | diag_n_ErrorCode |\n| safe_ | 安全相关 | safe_b_EStop |\n| cfg_ | 配置参数 | cfg_r_MaxSpeed |\n\n### 2.3 命名格式\n- 基本格式: `{前缀}{功能域}_{功能描述}{类型后缀}`\n- 示例: `dev_Conveyor_b_Run`, `hmi_n_SetSpeed`, `safe_b_DoorOpen`\n- 布尔量后缀: `_b_` 或 `_b` 表示布尔\n- 长度限制: 不超过32个字符(TIA Portal兼容)\n\n## 3. PLC程序结构规范\n### 3.1 组织块(OB)分配\n| OB类型 | OB号 | 用途 | 执行周期 |\n|--------|:----:|------|----------|\n| 主循环 | OB1 | 主程序循环 | 默认 |\n| 循环中断 | OB30~OB38 | 周期性任务 | 自定义 |\n| 时间触发 | OB10~OB17 | 日历任务 | 日/周/月 |\n| 延时中断 | OB20~OB23 | 精确延时 | 单次触发 |\n| 硬件中断 | OB40~OB47 | IO事件响应 | 即时 |\n| 诊断中断 | OB82~OB87 | 模块诊断 | 即时 |\n| 启动 | OB100 | 启动初始化 | Warm Restart |\n\n### 3.2 FB/FC层级结构\n```\nMain (OB1)\n├── FB_System_Init       // 系统初始化\n├── FB_Auto_Control      // 自动控制主控\n│   ├── FB_Sequence      // 步进控制\n│   ├── FB_Interlock     // 联锁逻辑\n│   └── FB_Alarm         // 报警处理\n├── FB_Manual_Control    // 手动控制\n│   ├── FB_Jog           // 点动控制\n│   └── FB_Setup         // 参数设置\n├── FB_Safety            // 安全功能\n│   ├── FB_EStop         // 急停处理\n│   └── FB_SafeDoor      // 安全门\n├── FB_Driver            // 驱动控制\n│   ├── FB_Inverter      // 变频器\n│   └── FB_Servo         // 伺服\n├── FB_Diagnostics       // 诊断功能\n└── FB_Communication     // 通讯处理\n    ├── FB_HMI           // HMI通讯\n    └── FB_Modbus        // Modbus通讯\n```\n\n### 3.3 DB数据块规划\n| DB名称 | 用途 | 类型 |\n|--------|------|------|\n| DB_Global | 全局共享变量 | 全局DB |\n| DB_HMI | HMI接口变量 | 全局DB |\n| DB_Config | 系统配置参数 | 全局DB |\n| DB_Diag | 诊断数据 | 全局DB |\n| DB_Instance_FBxx | FB实例数据块 | 实例DB |\n\n### 3.4 程序注释规范\n#### FB/FC头注释模板\n```scl\n(* ============================================================================ *)\n(* Function Block: FB_xxx                                                *)\n(* Description: [功能描述]                                               *)\n(* Version: V1.0.0                                                        *)\n(* Author: [作者]                                                         *)\n(* Date: [日期]                                                           *)\n(* Inputs:                                                               *)\n(*   - xxx: [说明]                                                        *)\n(* Outputs:                                                              *)\n(*   - xxx: [说明]                                                        *)\n(* InOuts:                                                               *)\n(*   - xxx: [说明]                                                        *)\n(* Change History:                                                       *)\n(*   V1.0.0 [日期] [作者] Initial version                                *)\n(* ========================================================================= *)\n```\n\n#### 行内注释规范\n- 关键逻辑必须有注释\n- 注释语言统一使用中文或英文（按项目约定）\n- 复杂算法需添加段落注释\n- TODO/FIXME/HACK 必须标注责任人\n\n## 4. 版本管理规范\n### 4.1 版本号规则\n- 格式: `V{主版本}.{次版本}.{修订号}`\n- 主版本: 架构变更或不兼容修改\n- 次版本: 新增功能或重大改进\n- 修订号: Bug修复或小幅优化\n\n### 4.2 变更记录要求\n每次修改必须记录: 版本号、日期、修改人、修改原因、影响范围\n> 详细变更通过工具的变更管理模块统一处理。\n\n## 5. 代码风格规范\n### 5.1 缩进与对齐\n- 使用4个空格缩进，禁止Tab\n- 同层级的赋值语句对齐\n- CASE分支对齐\n\n### 5.2 命名一致性\n- 同一功能的变量在FB/FC/HMI中使用相同名称\n- 全局变量使用唯一前缀避免冲突\n\n### 5.3 代码长度限制\n- 单个POU不超过500行\n- 单行不超过120字符\n- 单个函数/方法不超过50行\n\n### 5.4 禁止事项\n- 禁止使用魔法数字（必须使用符号常量）\n- 禁止使用GOTO跳转\n- 禁止在OB1中编写大量业务逻辑\n- 禁止直接操作绝对地址（使用符号寻址）\n\n## 6. 安全规范\n### 6.1 急停回路\n- 急停信号必须使用硬件回路+软件双重检测\n- 急停响应时间 ≤ 50ms\n- 急停复位必须满足安全条件\n\n### 6.2 安全联锁\n- 安全门/光幕信号必须接入安全输入模块\n- 安全功能必须独立于普通控制逻辑\n- 安全相关代码必须经过安全认证人员审核\n\n### 6.3 使能链\n- 所有运动使能必须串联急停和安全门信号\n- 使能条件必须在程序中显式表达\n\n### 6.4 速度/位置限制\n- 必须设置软件限位\n- 速度限制值必须可配置\n- 超限必须触发报警并执行保护动作\n\n## 7. 测试规范\n### 7.1 单元测试\n- 每个FB/FC必须编写单元测试用例\n- 覆盖正常路径、边界条件和异常路径\n\n### 7.2 集成测试\n- 模块间接口测试\n- 通讯功能测试\n- HMI联动测试\n\n### 7.3 安全测试\n- 急停功能测试（各种工况下）\n- 安全联锁测试\n- 使能链完整性测试\n\n### 7.4 性能测试\n- 扫描周期测量\n- 响应时间测试\n- 长时间运行稳定性测试\n\n## 8. 文档规范\n### 8.1 必须编写的文档\n- 需求规格说明书\n- 系统架构设计说明书\n- 详细设计说明书\n- IO分配表\n- 联锁逻辑设计说明书\n- 操作手册\n- 测试报告\n\n### 8.2 文档更新原则\n- 代码变更必须同步更新文档\n- 文档版本与程序版本保持一致\n- 废弃文档必须标记归档\n\n## 9. 最佳实践\n### 9.1 模块化设计\n- 单一职责原则: 每个FB/FC只做一件事\n- 低耦合高内聚: 减少模块间的依赖\n- 接口清晰: 明确定义输入输出\n\n### 9.2 状态机应用\n- 复杂控制逻辑优先使用状态机实现\n- 状态转换条件必须明确\n- 避免非法状态转换\n\n### 9.3 错误处理\n- 所有可能失败的操作都要有错误处理\n- 错误码统一规划和定义\n- 错误信息要便于定位问题\n\n### 9.4 诊断友好\n- 关键状态点设置诊断变量\n- 报警信息包含足够的上下文\n- 支持远程诊断的数据采集\n\n### 9.5 可维护性\n- 避免硬编码，参数化配置\n- 使用UDT统一数据结构\n- 保持代码简洁易读\n\n## 10. 附则\n- 本规范自发布之日起生效\n- 规范的解释权归技术部门所有\n- 如有疑问请联系项目负责人\n- 本规范将根据项目实践持续优化完善\n\n---\n**版本**: V2.0.0  \n**最后更新**: {create_date}"
            },
            {
                "path": "07_工具与配置/开发环境配置/开发环境配置.md",
                "type": "document",
                "content": "# {project_name} 开发环境配置\n\n## 编程软件\n| 软件 | 版本 | 用途 | 许可信息 |\n|------|:----:|------|----------|\n| TIA Portal | | PLC编程 | |\n| ProFace GP-ProEX | | HMI编程 | |\n| Eplan | | 电气设计 | |\n\n## 通讯配置\n| 接口 | 协议 | 参数 | 用途 |\n|------|------|------|------|\n| PN/IE | PROFINET | | PLC编程/下载 |\n| MPI/PPI | | | 兼容老设备 |\n| USB | | | 现场调试 |\n\n## 仿真环境\n| 软件 | 版本 | 用途 |\n|------|:----:|------|\n| PLCSIM | | PLC仿真 |\n| ProFace Simulator | | HMI仿真 |\n\n## 版本控制\n- Git仓库地址:\n- 分支策略:\n\n## 常用工具\n| 工具 | 用途 |\n|------|------|\n| Wireshark | 抓包分析 |\n| PuTTY | 串口调试 |\n| AdvancedPort | 串口助手 |"
            },
            {
                "path": "07_工具与配置/工具清单/工具清单.md",
                "type": "document",
                "content": "# {project_name} 工具清单\n\n## 硬件工具\n| 序号 | 工具名称 | 型号规格 | 数量 | 用途 | 存放位置 |\n|:----:|----------|----------|:----:|------|----------|\n| 1 | 编程电缆 | | | PLC下载/调试 | |\n| 2 | 万用表 | | | 电气测量 | |\n| 3 | 示波器 | | | 信号分析 | |\n\n## 软件工具\n| 序号 | 软件名称 | 版本 | 用途 | 授权方式 |\n|:----:|----------|:----:|------|----------|\n| 1 | TIA Portal | | PLC开发 | 正版授权 |\n| 2 | GP-ProEX | | HMI开发 | 正版授权 |\n| 3 | Eplan Electric P8 | | 电气设计 | 正版授权 |\n| 4 | VS Code | | 代码编辑 | 免费 |\n| 5 | Git | | 版本控制 | 免费 |\n\n## 专用工具\n| 序号 | 工具名称 | 用途 | 备注 |\n|:----:|----------|------|------|\n"
            },
            {
                "path": "07_工具与配置/脚本/脚本说明.md",
                "type": "document",
                "content": "# {project_name} 脚本说明\n\n## 脚本清单\n| 脚本名称 | 语言 | 功能 | 用法 | 最后更新 |\n|----------|:----:|------|------|----------|\n\n## Python辅助脚本\n### IO导出脚本\n### 批量变量生成脚本\n### 文档生成脚本\n\n## 使用说明\n\n## 依赖环境\n- Python 3.x\n- 依赖包列表:\n\n## 注意事项\n"
            },
            {
                "path": "07_工具与配置/.gitignore",
                "type": "config",
                "content": "# PLC Project\n*.zap\n*.zap16\n*.ap16\n*.ap19\n*.al18\n*.s7p\n*.s7s\n\n# Eplan\n*.elk\n*.zkp\n\n# ProFace\n*.prx\n*.prj\n\n# Backup\n*.bak\n*~\n\n# Logs\n*.log\nlogs/\n\n# OS\n.DS_Store\nThumbs.db\n\n# IDE\n.vscode/\n.idea/\n\n# Python\n__pycache__/\n*.pyc\n\n# Temp\ntemp/\ntmp/"
            },
            {
                "path": "07_工具与配置/README.md",
                "type": "document",
                "content": "# {project_name}\n\n## 项目概述\n- **编号**: {project_code}\n- **名称**: {project_name}\n- **模板**: TPL-SINGLE-PLC-M001 (中大型单机设备 PLC+HMI)\n- **版本**: V3.0.0\n- **创建日期**: {create_date}\n\n## 适用场景\n- IO点数 >= 100 点\n- 复杂运动控制（伺服、步进）\n- 多驱动器系统（>=3台）\n- 项目周期 >= 3 个月\n- 团队规模 >= 5 人\n\n## 快速开始\n1. 查看 `00_项目管理/00_项目基本信息/` 了解项目启动文档\n2. 参考 `00_项目管理/01_立项与需求/` 阅读立项和需求文档\n3. 从 `07_工具与配置/开发环境配置/` 了解开发规范\n\n## 目录索引\n| 目录 | 内容 | 关键文档 |\n|------|------|----------|\n| 00_项目管理 | 十四大管理模块(00-05) | 项目章程、立项表、变更管理 |\n| 01_需求与设计 | 技术设计(11-13) | Eplan电气、机械结构、软件方案 |\n| 02_PLC程序 | PLC源码和文档 | 主程序、IO分配表、联锁逻辑 |\n| 03_HMI设计 | HMI全流程 | 设计规范、变量绑定、操作手册 |\n| 04_驱动器与设备 | 设备配置 | 驱动器参数、设备手册 |\n| 05_测试与验证 | 测试验收 | 测试报告、FAT/SAT记录 |\n| 06_文档与交付 | 文档交付 | 技术文档、培训资料、验收清单 |\n| 07_工具与配置 | 开发工具 | 开发环境配置、工具清单 |\n| 08_技术知识库 | 知识沉淀 | 最佳实践、问题解决方案 |\n\n## 重要提醒\n- 变更管理通过工具的变更管理模块统一处理，不在目录中单独维护变更文档\n- 版本变更记录见 `06_文档与交付/版本变更记录/`\n- PLC开发规范详见 `07_工具与配置/开发环境配置/PLC项目规范.md`"
            },
            {
                "path": "00_项目管理/04_变更管理/01_变更单/.gitkeep",
                "content": "",
                "required": True
            },
            {
                "path": "00_项目管理/04_变更管理/03_变更管理规范/042_{project_code}_变更管理流程规范_PM-V2.0.0.md",
                "type": "document",
                "content": "# {project_code} 变更管理流程规范\n\n## 1. 变更管理概述\n本文档定义{project_name}项目的变更管理流程，确保所有变更可控、可追溯、可审计。\n\n## 2. 变更分类\n| 类别 | 编码 | 说明 |\n|------|:----:|------|\n| 电气设计 | ELEC | Eplan原理图/接线图/IO分配表/BOM |\n| 机械结构 | MECH | SolidWorks 3D/装配图/加工图 |\n| PLC程序 | PLC | IEC 61131-3 SCL/ST/LD/GVL |\n| HMI程序 | HMI | 触摸屏画面/变量映射/报警配置 |\n| Python脚本 | SCPT | 数据采集/MES接口/上位机应用 |\n| 工程文档 | DOCU | 设计说明书/操作手册/验收报告 |\n| 安全功能 | SAFE | 急停回路/安全矩阵/SIL评估 |\n\n## 3. 变更流程\n1. **提交** → 填写变更单 → 选择变更类型和影响范围\n2. **评审** → 技术负责人审核 → 根据Scope自动匹配审批层级\n3. **审批** → 按审批层级逐级审批\n4. **实施** → 执行变更 → 更新相关文档\n5. **验证** → 测试验证 → 更新台帐\n6. **关闭** → 归档变更单\n\n## 4. 文件命名规范\n- 变更单：`040_{project_code}_变更单{序号}_CHG-V2.0.0.md`\n- 台帐：`041_{project_code}_版本变更台帐_CHG-V2.1.0.md`\n\n---\n**文档版本**: PM-V2.0.0\n**编制日期**: {current_date}",
                "required": False
            },
            {
                "path": "00_项目管理/04_变更管理/04_变更记录/041_{project_code}_版本变更台帐_CHG-V2.1.0.md",
                "content": "# {project_code} 版本变更台帐\n\n## 1. 项目信息\n- **项目代码**: {project_code}\n- **项目名称**: {project_name}\n- **项目版本**: V1.0.0\n\n## 2. 变更记录\n| 变更单号 | 变更类型 | 变更标题 | 申请日期 | 申请人 | 审批状态 | 实施日期 | 影响文件数 |\n|---------|---------|---------|---------|--------|---------|---------|-----------|\n| (暂无变更记录) | | | | | | | |\n\n## 3. 版本统计\n| 版本 | 变更单数 | 变更日期范围 | 主要变更内容 |\n|------|---------|-------------|-------------|\n| V1.0.0 | 0 | - | 初始版本 |\n\n---\n**文档版本**: CHG-V2.1.0\n**编制日期**: {current_date}\n**编制人**: 系统",
                "required": False
            },
            {
                "path": "00_项目管理/04_变更管理/README.md",
                "content": "# 变更管理目录\n\n## 目录结构\n\n本目录按照 Obsidian 规范 06_项目模板规范/变更管理与模板文件映射文档 组织。\n\n### 01_变更单/\n存放所有变更单文件，采用扁平结构（按序号排列）。\n- 命名格式：`040_{project_code}_变更单{序号}_CHG-V2.0.0.md`\n- 示例：`040_SW-2026-001_变更单 001_CHG-V2.0.0.md`\n\n### 04_变更记录/\n存放版本变更台帐文件。\n- 文件名：`041_{project_code}_版本变更台帐_CHG-V2.1.0.md`\n- 记录所有变更历史和版本统计\n\n## 使用方式\n1. 创建变更单 → 工具自动生成到 `01_变更单/`\n2. 更新台帐 → 工具自动刷新 `04_变更记录/` 下的台帐文件\n\n---\n**最后更新**: {current_date}",
                "required": False
            }
        ]
    },
    {
        "id": "TPL-SINGLE-PLC-S001",
        "name": "小型单机设备(PLC+HMI)",
        "version": "V1.0.0",
        "compiler": "Step7/TIA Portal + ProFace",
        "scene": "小型PLC自动化单机设备（IO点数<100，无复杂运动控制）",
        "description": "V1.0.0 小型单机设备精简版: 适用于简单单机设备，保留了完整的项目管理和变更管理功能，精简了技术设计文档和测试文档。适用场景：IO点数少于100点、无复杂运动控制、无机器人集成、项目周期<3个月、团队<5人",
        "is_builtin": True,
        "business_lines": ["DJ"],
        "structure": [
            {"path": "00_项目管理/01_立项与需求", "required": True, "description": "立项表、需求分析"},
            {"path": "00_项目管理/02_进度与风险", "required": True, "description": "进度计划、风险管理"},
            {"path": "00_项目管理/04_变更管理/01_变更单", "required": True, "description": "变更单(扁平结构)"},
            {"path": "00_项目管理/04_变更管理/03_变更管理规范", "required": False, "description": "变更管理流程规范"},
            {"path": "00_项目管理/04_变更管理/04_变更记录", "required": True, "description": "版本变更台帐"},
            {"path": "01_需求与设计/11_Eplan电气/Export_PDF", "required": True, "description": "Eplan导出的PDF电气原理图"},
            {"path": "01_需求与设计/11_Eplan电气/Source", "required": True, "description": "Eplan源文件(.edz/.edb)"},
            {"path": "01_需求与设计/13_软件方案", "required": True, "description": "需求规格说明书(精简版)"},
            {"path": "02_PLC程序/主程序", "required": True, "description": "PLC主程序源码"},
            {"path": "02_PLC程序/变量表", "required": True, "description": "全局变量表和IO映射"},
            {"path": "02_PLC程序/程序文档", "required": True, "description": "IO分配表、程序设计总文档"},
            {"path": "03_HMI设计/变量绑定", "required": True, "description": "PLC-HMI变量映射"},
            {"path": "03_HMI设计/操作手册", "required": True, "description": "HMI操作手册SOP"},
            {"path": "04_驱动器与设备/驱动器参数", "required": True, "description": "变频器/伺服驱动参数表"},
            {"path": "05_测试与验证/测试报告", "required": True, "description": "测试执行报告"},
            {"path": "05_测试与验证/验证记录", "required": True, "description": "FAT/SAT验收记录"},
            {"path": "06_文档与交付/操作手册", "required": True, "description": "设备操作手册"},
            {"path": "06_文档与交付/验收交付清单", "required": True, "description": "验收检查表和交付物清单"},
            {"path": "07_工具与配置", "required": True, "description": "开发环境规范、Git配置"}
        ],
        "templates": [
            {
                "path": ".gitignore",
                "type": "config",
                "content": "# PLC Project (Small)\n*.zap\n*.zap16\n*.ap16\n*.ap19\n\n# Eplan\n*.elk\n*.zkp\n\n# Backup\n*.bak\n*~\n\n# Logs\n*.log\nlogs/\n\n# OS\n.DS_Store\nThumbs.db\n"
            },
            {
                "path": "README.md",
                "type": "document",
                "spec_id": "SPEC-DOC-README-001",
                "content": "# {project_name}\n\n## 项目概述\n- **编号**: {project_code}\n- **名称**: {project_name}\n- **模板**: TPL-SINGLE-PLC-S001 (小型单机设备 PLC+HMI)\n- **版本**: V1.0.0\n- **创建日期**: {create_date}\n\n## 适用场景\n- IO点数 < 100 点\n- 单 PLC 控制\n- 简单 HMI 操作界面\n- 无复杂运动控制\n- 项目周期 < 3 个月\n- 团队规模 < 5 人\n\n## 快速开始\n1. 查看 `00_项目管理/01_立项与需求/` 阅读立项和需求文档\n2. 参考 `07_工具与配置/` 了解开发规范\n3. 从 `02_PLC程序/` 开始 PLC 开发工作\n\n## 目录索引\n| 目录 | 内容 | 关键文档 |\n|------|------|----------|\n| 00_项目管理 | 精简项目管理(01/02/04) | 立项表、进度计划、变更管理 |\n| 01_需求与设计 | 精简技术设计(11/13) | Eplan电气、需求规格说明书 |\n| 02_PLC程序 | PLC核心程序 | 主程序、IO分配表、设计总文档 |\n| 03_HMI设计 | 精简HMI设计 | 变量绑定、操作手册 |\n| 04_驱动器与设备 | 设备配置 | 驱动器参数 |\n| 05_测试与验证 | 精简测试验证 | 测试报告、FAT/SAT记录 |\n| 06_文档与交付 | 精简文档交付 | 操作手册、验收清单 |\n| 07_工具与配置 | 基础工具配置 | 开发环境规范、Git配置 |\n\n## 与中大型版本(M001)的区别\n| 模块 | 小型版(S001) | 中大型版(M001) |\n|------|:-----------:|:------------:|\n| 项目基本信息 | ❌ 精简 | ✅ 完整 |\n| 产品需求文档(PRD) | ❌ 精简 | ✅ 独立 |\n| 沟通管理计划 | ❌ 精简 | ✅ 完整 |\n| 资源管理计划 | ❌ 精简 | ✅ 完整 |\n| 机械结构设计 | ❌ 通常不需要 | ✅ 完整 |\n| 系统架构设计 | ❌ 精简 | ✅ 完整 |\n| 详细设计说明书 | ❌ 精简 | ✅ 完整 |\n| 联锁逻辑文档 | ❌ 精简 | ✅ 完整 |\n| HMI设计规范 | ❌ 精简 | ✅ 完整 |\n| 测试计划和用例 | ❌ 精简 | ✅ 完整 |\n| 技术知识库 | ❌ 精简 | ✅ 完整 |\n\n## 重要提醒\n- 变更管理通过工具的变更管理模块统一处理\n- 版本变更记录见 `00_项目管理/04_变更管理/04_变更记录/`\n- 如项目规模扩大，可升级到 TPL-SINGLE-PLC-M001"
            },
            {
                "path": "00_项目管理/01_立项与需求/003_{project_code}_项目立项表_PROJ-V1.1.0.md",
                "type": "document",
                "spec_id": "SPEC-DOC-INIT-001",
                "content": "# {project_name} 项目立项表\n\n## 基本信息\n| 项目 | 内容 |\n|------|------|\n| 编号 | {project_code} |\n| 名称 | {project_name} |\n| 业务线 | 单机设备(DJ) |\n| 模板 | 小型单机设备(S001) |\n| 负责人 | {manager} |\n| 日期 | {create_date} |\n| 版本 | V1.0.0 |\n\n## 项目概述\n{description}\n\n## 设备规格\n- PLC型号:\n- HMI型号:\n- IO点数预估(DI/DO/AI/AO):\n- 驱动器数量:\n- 控制方式:\n\n## 适用场景确认\n- [x] IO点数 < 100 点\n- [x] 单 PLC 控制\n- [x] 无复杂运动控制\n- [x] 项目周期 < 3 个月\n- [x] 团队 < 5 人\n\n## 里程碑\n| 阶段 | 计划完成 | 负责人 |\n|------|----------|--------|\n| 电气设计 | | |\n| PLC编程 | | |\n| HMI制作 | | |\n| 调试验收 | | |"
            },
            {
                "path": "00_项目管理/01_立项与需求/005_{project_code}_需求分析文档_REQ-V1.1.0.md",
                "type": "document",
                "spec_id": "SPEC-DOC-REQ-001",
                "content": "# {project_name} 需求分析文档\n\n## 功能需求\n### 主工艺功能\n### 安全保护功能\n### 操作模式（自动/手动/维护）\n\n## IO统计\n| 类型 | 数量 | 说明 |\n|------|:----:|------|\n| DI | | 数字输入 |\n| DO | | 数字输出 |\n| AI | | 模拟输入 |\n| AO | | 模拟输出 |\n\n## 性能指标\n- PLC扫描周期目标:\n- 生产节拍要求:\n- 急停响应时间要求:"
            },
            {
                "path": "00_项目管理/02_进度与风险/006_{project_code}_项目进度计划_PM-V1.0.0.md",
                "type": "document",
                "content": "# {project_name} 项目进度计划\n\n## 时间线\n| 阶段 | 计划开始 | 计划完成 | 负责人 | 状态 |\n|------|----------|----------|--------|:----:|\n| 需求分析 | | | | |\n| 方案设计 | | | | |\n| 电气设计 | | | | |\n| PLC编程 | | | | |\n| HMI制作 | | | | |\n| 调试验收 | | | | |\n\n## 关键路径\n\n## 风险登记\n| ID | 风险 | 应对措施 | 负责人 |\n|:--:|------|----------|--------|"
            },
            {
                "path": "01_需求与设计/13_软件方案/012_{project_code}_需求规格说明书_REQ-V1.0.0.md",
                "type": "document",
                "content": "# {project_name} 需求规格说明书\n\n## 1. 功能需求\n### 1.1 主工艺功能\n### 1.2 安全保护功能\n### 1.3 操作模式\n\n## 2. IO需求\n### 2.1 输入信号（DI/AI）\n### 2.2 输出信号（DO/AO）\n\n## 3. 通讯需求\n### 3.1 PLC-HMI通讯\n\n## 4. 性能指标\n- 扫描周期目标:\n- 定位精度要求:\n- 生产节拍要求:"
            },
            {
                "path": "02_PLC程序/程序文档/015_{project_code}_IO分配表_IO-V1.0.0.md",
                "type": "document",
                "spec_id": "SPEC-DOC-IO-001",
                "content": "# {project_name} IO分配表\n\n## DI - 数字输入\n| 地址 | 符号名 | 描述 | 模块位置 |\n|------|--------|------|----------|\n\n## DO - 数字输出\n| 地址 | 符号名 | 描述 | 模块位置 |\n|------|--------|------|----------|\n\n## AI/AO - 模拟量\n| 地址 | 范围 | 描述 |\n|------|------|------|\n\n## IO统计汇总\n| 类型 | 已用 | 总计 | 利用率 |\n|------|:----:|:----:|:------:|\n| DI | | | |\n| DO | | | |\n| AI | | | |\n| AO | | | |"
            },
            {
                "path": "02_PLC程序/程序文档/016_{project_code}_PLC程序设计总文档_PLC-V1.0.0.md",
                "type": "document",
                "content": "# {project_name} PLC程序设计总文档\n\n## 1. 设计概述\n本节概述{project_name}的PLC整体设计方案。\n\n## 2. 程序架构\n### OB组织块规划\n### FB/FC功能块层级\n### DB数据块规划\n\n## 3. 主要功能说明\n\n## 4. 变量命名规范\n> 详细命名规范请参考 `07_工具与配置/开发环境配置/PLC项目规范.md`\n\n## 5. 联锁逻辑总述\n\n## 6. 通讯接口总述\n\n## 7. 安全机制总述"
            },
            {
                "path": "03_HMI设计/操作手册/HMI操作手册.md",
                "type": "document",
                "content": "# {project_name} HMI操作手册\n\n## 1. 画面索引\n| 画面编号 | 画面名称 | 功能说明 |\n|:--------:|----------|----------|\n\n## 2. 各画面操作说明\n### 2.1 监控主画面\n### 2.2 参数设置画面\n### 2.3 手动操作画面\n\n## 3. 权限等级\n| 等级 | 名称 | 可操作内容 |\n|:----:|------|----------|\n| 0 | 操作员 | 基本监控、启停 |\n| 1 | 技术员 | 参数修改、手动操作 |\n\n## 4. 常见报警处理\n\n## 5. 标准操作流程\n### 5.1 开机流程\n### 5.2 停机流程\n### 5.3 急停处理"
            },
            {
                "path": "06_文档与交付/操作手册/设备操作手册.md",
                "type": "document",
                "spec_id": "SPEC-DOC-OPMAN-001",
                "content": "# {project_name} 设备操作手册\n\n## 1. 开机前检查\n\n## 2. 标准开机流程\n\n## 3. 正常运行监控\n\n## 4. 标准停机流程\n\n## 5. 完整关机流程\n\n## 6. 急停操作SOP\n\n## 7. 常见报警处理\n\n**版本**: V1.0.0 | **编制日期**: {create_date}"
            },
            {
                "path": "06_文档与交付/验收交付清单/验收交付清单.md",
                "type": "document",
                "content": "# {project_name} 验收交付清单\n\n## 一、文档验收\n| 序号 | 交付文档 | 版本 | 验收情况 |\n|:----:|----------|:----:|:--------:|\n\n## 二、程序验收\n| 序号 | 程序文件 | 版本 | 验收情况 |\n|:----:|----------|:----:|:--------:|\n\n## 三、功能验收\n| 序号 | 验收项目 | 验收标准 | 结果 |\n|:----:|----------|----------|:----:|\n\n## 四、最终验收结论\n- **验收结论**: □通过 □有条件通过 □不通过\n- **客户签字**:\n- **日期**:"
            },
            {
                "path": "07_工具与配置/开发环境配置/PLC项目规范.md",
                "type": "document",
                "content": "# PLC项目开发规范（小型版）\n\n## 1. 项目命名规范\n- 格式: `{业务线代码}-{年份}-{序号}`\n- 示例: `DJ-2026-001`\n\n## 2. 变量命名规范\n### 前缀规则\n| 前缀 | 数据类型 | 含义 | 示例 |\n|------|----------|------|------|\n| b_ | BOOL | 布尔量 | b_Start |\n| n_ | INT/DINT | 整数 | n_Speed |\n| r_ | REAL | 实数 | r_Temp |\n| st_ | STRUCT | 结构体 | st_Status |\n\n### 功能域前缀\n| 前缀 | 功能域 | 示例 |\n|------|--------|------|\n| sys_ | 系统全局 | sys_b_Run |\n| dev_ | 设备相关 | dev_Motor_b_On |\n| hmi_ | HMI接口 | hmi_n_SetSpeed |\n| safe_ | 安全相关 | safe_b_EStop |\n\n## 3. 程序结构规范\n### OB组织块分配\n| OB类型 | OB号 | 用途 |\n|--------|:----:|------|\n| 主循环 | OB1 | 主程序 |\n| 启动 | OB100 | 初始化 |\n\n### FB/FC层级结构\n```\nMain (OB1)\n├── FB_System_Init    // 系统初始化\n├── FB_AutoMode       // 自动模式\n├── FB_ManualMode     // 手动模式\n├── FB_Safety         // 安全联锁\n└── FB_Diagnostics    // 诊断\n```\n\n## 4. 文件命名规则\n- 程序文件: `{项目代码}_{功能名}.scl`\n- 文档文件: `{项目代码}_{文档名}.md`"
            },
            {
                "path": "07_工具与配置/.gitignore",
                "type": "config",
                "content": "# PLC Project (Small)\n*.zap\n*.zap16\n*.ap16\n*.ap19\n*.al18\n*.s7p\n*.s7s\n\n# Eplan\n*.elk\n*.zkp\n\n# ProFace\n*.prx\n*.prj\n\n# Backup\n*.bak\n*~\n\n# Logs\n*.log\nlogs/\n\n# OS\n.DS_Store\nThumbs.db\n\n# IDE\n.vscode/\n.idea/"
            },
            {
                "path": "00_项目管理/04_变更管理/01_变更单/.gitkeep",
                "content": "",
                "required": True
            },
            {
                "path": "00_项目管理/04_变更管理/03_变更管理规范/042_{project_code}_变更管理流程规范_PM-V2.0.0.md",
                "type": "document",
                "content": "# {project_code} 变更管理流程规范\n\n## 1. 变更管理概述\n本文档定义{project_name}项目的变更管理流程，确保所有变更可控、可追溯、可审计。\n\n## 2. 变更分类（小型单机）\n| 类别 | 编码 | 说明 |\n|------|:----:|------|\n| PLC程序 | PLC | IEC 61131-3 SCL/ST/LD/GVL |\n| 电气设计 | ELEC | Eplan原理图/接线图/IO分配表 |\n| HMI程序 | HMI | 触摸屏画面/变量映射/报警配置 |\n| 工程文档 | DOCU | 设计说明书/操作手册/验收报告 |\n\n## 3. 变更流程\n1. **提交** → 填写变更单 → 选择变更类型和影响范围\n2. **评审** → 技术负责人审核 → 根据Scope自动匹配审批层级\n3. **审批** → 按审批层级逐级审批\n4. **实施** → 执行变更 → 更新相关文档\n5. **验证** → 测试验证 → 更新台帐\n6. **关闭** → 归档变更单\n\n## 4. 文件命名规范\n- 变更单：`040_{project_code}_变更单{序号}_CHG-V2.0.0.md`\n- 台帐：`041_{project_code}_版本变更台帐_CHG-V2.1.0.md`\n\n---\n**文档版本**: PM-V2.0.0\n**编制日期**: {current_date}",
                "required": False
            },
            {
                "path": "00_项目管理/04_变更管理/04_变更记录/041_{project_code}_版本变更台帐_CHG-V2.1.0.md",
                "content": "# {project_code} 版本变更台帐\n\n## 1. 项目信息\n- **项目代码**: {project_code}\n- **项目名称**: {project_name}\n- **项目版本**: V1.0.0\n\n## 2. 变更记录\n| 变更单号 | 变更类型 | 变更标题 | 申请日期 | 申请人 | 审批状态 | 实施日期 | 影响文件数 |\n|---------|---------|---------|---------|--------|---------|---------|-----------|\n| (暂无变更记录) | | | | | | | |\n\n## 3. 版本统计\n| 版本 | 变更单数 | 变更日期范围 | 主要变更内容 |\n|------|---------|-------------|-------------|\n| V1.0.0 | 0 | - | 初始版本 |\n\n---\n**文档版本**: CHG-V2.1.0\n**编制日期**: {current_date}\n**编制人**: 系统",
                "required": False
            },
            {
                "path": "00_项目管理/04_变更管理/README.md",
                "content": "# 变更管理目录\n\n## 目录结构\n\n本目录按照 Obsidian 规范 06_项目模板规范/变更管理与模板文件映射文档 组织。\n\n### 01_变更单/\n存放所有变更单文件，采用扁平结构（按序号排列）。\n- 命名格式：`040_{project_code}_变更单{序号}_CHG-V2.0.0.md`\n\n### 04_变更记录/\n存放版本变更台帐文件。\n- 文件名：`041_{project_code}_版本变更台帐_CHG-V2.1.0.md`\n\n## 使用方式\n1. 创建变更单 → 工具自动生成到 `01_变更单/`\n2. 更新台帐 → 工具自动刷新 `04_变更记录/` 下的台帐文件\n\n## 小型项目特点\n- 变更类型仅包含：PLC/ELEC/HMI/DOCU 四类\n- 审批层级相对简化\n- 适合快速迭代的小型项目\n\n---\n**最后更新**: {current_date}",
                "required": False
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
            {"path": "00_项目管理/04_变更管理/01_变更单", "required": True, "description": "变更单(扁平结构)"},
            {"path": "00_项目管理/04_变更管理/03_变更管理规范", "required": False, "description": "变更管理流程规范"},
            {"path": "00_项目管理/04_变更管理/04_变更记录", "required": True, "description": "版本变更台帐"},
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
                "path": "00_项目管理/01_现状评估/现状评估报告.md",
                "type": "document",
                "content": "# {project_name} 现状评估报告\n\n## 1. 现有系统概况\n## 2. 存在问题清单\n## 3. 性能瓶颈分析\n## 4. 改造必要性评估\n## 5. 风险评估\n"
            },
            {
                "path": "00_项目管理/02_升级方案/升级方案设计书.md",
                "type": "document",
                "content": "# {project_name} 升级方案设计书\n\n## 1. 升级目标\n## 2. 技术方案\n## 3. 实施步骤\n## 4. 时间计划\n## 5. 资源需求\n## 6. 预算估算\n## 7. 回滚预案\n"
            },
            {
                "path": "00_项目管理/03_回滚方案/回滚预案.md",
                "type": "document",
                "content": "# {project_name} 回滚预案\n\n## 触发条件\n## 回滚步骤\n## 回滚时间窗口\n## 数据备份策略\n## 验证方法\n"
            },
            {
                "path": "00_项目管理/04_实施记录/实施日志.md",
                "type": "document",
                "content": "# {project_name} 升级实施日志\n\n| 日期 | 步骤 | 执行人 | 结果 | 问题 |\n|------|------|:------:|:----:|------|\n"
            },
            {
                "path": "40_交付与文档/验收确认/升级验收确认.md",
                "type": "document",
                "content": "# {project_name} 升级验收确认\n\n## 功能验证\n## 性能对比(升级前vs升级后)\n## 用户签字确认\n## 移交清单\n"
            },
            {
                "path": "00_项目管理/04_变更管理/01_变更单/.gitkeep",
                "content": "",
                "required": True
            },
            {
                "path": "00_项目管理/04_变更管理/03_变更管理规范/042_{project_code}_变更管理流程规范_PM-V2.0.0.md",
                "type": "document",
                "content": "# {project_code} 变更管理流程规范\n\n## 1. 变更管理概述\n本文档定义{project_name}系统升级项目的变更管理流程，确保所有变更可控、可追溯、可审计。\n\n## 2. 变更分类\n| 类别 | 编码 | 说明 |\n|------|:----:|------|\n| 需求变更 | REQ | 客户/市场/工艺驱动的新增或修改 |\n| 缺陷修复 | DEF | Bug修复、故障排除、设计纠错 |\n| 配置变更 | CFG | 参数修改、IO地址调整、通信配置变更 |\n| 紧急变更 | EMRG | 安全相关、生产中断等需立即处理 |\n\n## 3. 升级项目特殊流程\n1. **基线冻结** → 升级前冻结当前版本作为回滚基线\n2. **变更评估** → 评估变更对升级方案的影响\n3. **审批** → 项目经理 + 技术总监双签审批\n4. **实施** → 在测试环境验证后再到生产环境\n5. **回滚准备** → 每次变更前准备好回滚方案\n6. **台帐更新** → 记录变更对版本的影响\n\n## 4. 文件命名规范\n- 变更单：`040_{project_code}_变更单{序号}_CHG-V2.0.0.md`\n- 台帐：`041_{project_code}_版本变更台帐_CHG-V2.1.0.md`\n\n---\n**文档版本**: PM-V2.0.0\n**编制日期**: {current_date}",
                "required": False
            },
            {
                "path": "00_项目管理/04_变更管理/04_变更记录/041_{project_code}_版本变更台帐_CHG-V2.1.0.md",
                "content": "# {project_code} 版本变更台帐\n\n## 1. 项目信息\n- **项目代码**: {project_code}\n- **项目名称**: {project_name}\n- **项目版本**: V1.0.0\n\n## 2. 变更记录\n| 变更单号 | 变更类型 | 变更标题 | 申请日期 | 申请人 | 审批状态 | 实施日期 | 影响文件数 |\n|---------|---------|---------|---------|--------|---------|---------|-----------|\n| (暂无变更记录) | | | | | | | |\n\n## 3. 版本统计\n| 版本 | 变更单数 | 变更日期范围 | 主要变更内容 |\n|------|---------|-------------|-------------|\n| V1.0.0 | 0 | - | 初始版本 |\n\n---\n**文档版本**: CHG-V2.1.0\n**编制日期**: {current_date}\n**编制人**: 系统",
                "required": False
            },
            {
                "path": "00_项目管理/04_变更管理/README.md",
                "content": "# 变更管理目录\n\n## 目录结构\n\n本目录按照 Obsidian 规范 06_项目模板规范/变更管理与模板文件映射文档 组织。\n\n### 01_变更单/\n存放所有变更单文件，采用扁平结构（按序号排列）。\n- 命名格式：`040_{project_code}_变更单{序号}_CHG-V2.0.0.md`\n- 示例：`040_SW-2026-001_变更单 001_CHG-V2.0.0.md`\n\n### 03_变更管理规范/ （可选）\n存放变更管理流程规范说明文件（含升级项目特殊要求）。\n\n### 04_变更记录/\n存放版本变更台帐文件。\n- 文件名：`041_{project_code}_版本变更台帐_CHG-V2.1.0.md`\n- 记录所有变更历史和版本统计\n\n## 使用方式\n1. 创建变更单 → 工具自动生成到 `01_变更单/`\n2. 更新台帐 → 工具自动刷新 `04_变更记录/` 下的台帐文件\n\n## 升级项目注意事项\n- 所有变更必须评估对升级方案的影响\n- 每次变更实施前需准备回滚方案\n- 变更审批需要项目经理 + 技术总监双签\n\n---\n**最后更新**: {current_date}",
                "required": False
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
            {"path": "00_项目管理/04_变更管理/01_变更单", "required": True, "description": "标准变更单(扁平结构)"},
            {"path": "00_项目管理/04_变更管理/03_变更管理规范", "required": False, "description": "标准变更管理流程规范"},
            {"path": "00_项目管理/04_变更管理/04_变更记录", "required": True, "description": "标准版本变更台帐"},
            {"path": "04_变更管理", "required": True, "description": "软件专用变更管理(Git记录+版本发布)"},
            {"path": "04_变更管理/01_变更单", "required": True, "description": "软件变更单(扁平结构)"},
            {"path": "04_变更管理/04_变更记录", "required": True, "description": "软件版本变更台帐"},
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
            },
            {
                "path": "00_项目管理/04_变更管理/01_变更单/.gitkeep",
                "content": "",
                "required": True
            },
            {
                "path": "00_项目管理/04_变更管理/03_变更管理规范/042_{project_code}_变更管理流程规范_PM-V2.0.0.md",
                "type": "document",
                "content": "# {project_code} 变更管理流程规范（标准）\n\n## 1. 变更管理概述\n本文档定义{project_name}项目的标准变更管理流程，适用于项目管理层面的变更控制。\n\n## 2. 变更分类\n| 类别 | 编码 | 说明 |\n|------|:----:|------|\n| 代码变更 | code | Python源码修改 |\n| 配置变更 | config | 配置文件/环境变量调整 |\n| 依赖变更 | dependency | 第三方库版本升级 |\n| 文档变更 | document | 设计文档/API文档更新 |\n| 结构变更 | structure | 目录结构/架构调整 |\n\n## 3. 变更流程\n1. **提交** → 填写变更单 → 选择变更类型和影响范围\n2. **评审** → 技术负责人审核代码/设计\n3. **审批** → 按Scope匹配审批层级\n4. **实施** → Git分支开发 → Code Review → 合并\n5. **验证** → 自动化测试 + 手工验证\n6. **发布** → 更新版本号 → 发布说明\n7. **关闭** → 归档变更单 + 更新台帐\n\n## 4. 文件命名规范\n- 变更单：`040_{project_code}_变更单{序号}_CHG-V2.0.0.md`\n- 台帐：`041_{project_code}_版本变更台帐_CHG-V2.1.0.md`\n\n---\n**文档版本**: PM-V2.0.0\n**编制日期**: {current_date}",
                "required": False
            },
            {
                "path": "00_项目管理/04_变更管理/04_变更记录/041_{project_code}_版本变更台帐_CHG-V2.1.0.md",
                "content": "# {project_code} 版本变更台帐（标准）\n\n## 1. 项目信息\n- **项目代码**: {project_code}\n- **项目名称**: {project_name}\n- **项目版本**: V1.0.0\n\n## 2. 变更记录\n| 变更单号 | 变更类型 | 变更标题 | 申请日期 | 申请人 | 审批状态 | 实施日期 | 影响文件数 |\n|---------|---------|---------|---------|--------|---------|---------|-----------|\n| (暂无变更记录) | | | | | | | |\n\n## 3. 版本统计\n| 版本 | 变更单数 | 变更日期范围 | 主要变更内容 |\n|------|---------|-------------|-------------|\n| V1.0.0 | 0 | - | 初始版本 |\n\n---\n**文档版本**: CHG-V2.1.0\n**编制日期**: {current_date}\n**编制人**: 系统",
                "required": False
            },
            {
                "path": "00_项目管理/04_变更管理/README.md",
                "content": "# 标准变更管理目录\n\n## 目录结构\n\n本目录按照 Obsidian 规范 06_项目模板规范/变更管理与模板文件映射文档 组织。\n\n### 01_变更单/\n存放所有标准变更单文件，采用扁平结构（按序号排列）。\n- 命名格式：`040_{project_code}_变更单{序号}_CHG-V2.0.0.md`\n\n### 03_变更管理规范/ （可选）\n存放标准变更管理流程规范说明文件。\n\n### 04_变更记录/\n存放标准版本变更台帐文件。\n- 文件名：`041_{project_code}_版本变更台帐_CHG-V2.1.0.md`\n\n## 与软件专用变更管理的区别\n- 本目录：项目管理层面的变更（需求、设计、文档等）\n- `04_变更管理/`：软件专用变更（Git提交、代码Review、版本发布等）\n\n---\n**最后更新**: {current_date}",
                "required": False
            },
            {
                "path": "04_变更管理/01_变更单/.gitkeep",
                "content": "",
                "required": True
            },
            {
                "path": "04_变更管理/04_变更记录/041_{project_code}_软件版本变更台帐_CHG-V2.1.0.md",
                "content": "# {project_code} 软件版本变更台帐\n\n## 1. 项目信息\n- **项目代码**: {project_code}\n- **项目名称**: {project_name}\n- **软件版本**: V1.0.0\n\n## 2. Git提交记录\n| Commit Hash | 提交日期 | 提交者 | 变更类型 | 变更摘要 | 关联变更单 |\n|------------|---------|--------|---------|----------|----------|\n| (暂无提交记录) | | | | | |\n\n## 3. 版本发布记录\n| 版本号 | 发布日期 | 发布类型 | 主要变更内容 | Git Tag | 发布人 |\n|:------:|:--------:|:--------:|-------------|---------|:------:|\n| V1.0.0 | {current_date} | 初始版本 | 项目初始化 | v1.0.0 | 系统 |\n\n## 4. 分支策略\n- main: 生产环境稳定版\n- develop: 开发集成分支\n- feature/*: 功能开发分支\n- hotfix/*: 紧急修复分支\n\n---\n**文档版本**: CHG-V2.1.0\n**编制日期**: {current_date}\n**编制人**: 系统",
                "required": False
            },
            {
                "path": "04_变更管理/README.md",
                "content": "# 软件专用变更管理目录\n\n## 目录结构\n\n本目录用于软件项目的Git版本控制和发布管理。\n\n### 01_变更单/\n存放软件变更单文件（与Git提交关联）。\n- 命名格式：`040_{project_code}_软件变更单{序号}_CHG-V2.0.0.md`\n\n### 04_变更记录/\n存放软件版本变更台帐和Git提交记录。\n- 台帐文件：`041_{project_code}_软件版本变更台帐_CHG-V2.1.0.md`\n\n## 软件变更流程\n1. 创建分支 → 从develop创建feature/hotfix分支\n2. 开发编码 → 遵循编码规范\n3. 代码审查 → Code Review通过\n4. 合并分支 → 合并到develop/main\n5. 打Tag → 语义化版本号(vMajor.Minor.Patch)\n6. 发布部署 → 更新台帐\n\n## 与标准变更管理的区别\n- 本目录：软件技术变更（代码、配置、依赖、发布等）\n- `00_项目管理/04_变更管理/`：项目管理层面变更（需求、计划、文档等）\n\n---\n**最后更新**: {current_date}",
                "required": False
            }
        ]
    },
]
