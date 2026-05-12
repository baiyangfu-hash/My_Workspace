# 变更管理功能技术方案

## 1. 概述

本技术方案描述SW-2026-004 Python项目管理工具的**变更管理模块V2.1.0升级**。本次升级基于在DJ-2026-014项目中实践验证的**变更管理规范V2.1.0精简工程版**（043 + 041 + 040），将变更管理从**V1.x软件视角**全面升级为**V2.1.0工程视角**。

### 1.1 升级背景

| 维度 | V1.x (旧) | V2.1.0 (新) |
|:----:|-----------|-------------|
| **分类体系** | 单维度 (type: 6种软件类型) | 二维分类 (Domain×Nature×Scope) |
| **命名规则** | `CHG-{YYYYMMDD}-{UUID8}` | `CHG-[DOMAIN]-[YYYY]-[XXX]` |
| **台帐格式** | 内嵌详情表格 (冗余) | 引用模式 (超链接+摘要) |
| **审批机制** | 单一审批流 | 分级审批 (按scope自动匹配) |
| **目录结构** | `05_变更管理/{01~06}` 6子目录 | `04_变更管理/01_变更单/{7领域}` |
| **传播追踪** | ❌ 无 | ✅ 传播链矩阵+关联变更 |

### 1.2 规范依据

| 规范文件 | 版本 | 用途 |
|----------|:----:|:-----|
| [043_通用变更管理目录结构说明](../../../00_Obsidian_Base全局规范文件仓库/04_监控和控制/01_变更管理/03_变更管理规范/043_通用变更管理目录结构说明_PM-V2.1.0.md) | V2.1.0 | 目录结构与职责定义 |
| [040_通用变更单模板](../../../00_Obsidian_Base全局规范文件仓库/04_监控和控制/01_变更管理/02_变更单模板/040_通用变更单模板_CHG-V2.0.0.md) | V2.0.0 | 变更单模板格式(§1~§10) |
| [041_通用版本变更台帐模板](../../../00_Obsidian_Base全局规范文件仓库/04_监控和控制/01_变更管理/04_变更记录/041_通用版本变更台帐模板_CHG-V2.1.0.md) | V2.1.0 | 台帐引用模式格式 |
| [042_通用变更管理流程规范](../../../00_Obsidian_Base全局规范文件仓库/04_监控和控制/01_变更管理/03_变更管理规范/042_通用变更管理流程规范_PM-V2.0.0.md) | V2.0.0 | 流程与审批规范 |

---

## 2. 架构设计 (V2.1.0)

### 2.1 二维分类体系

```
┌─────────────────────────────────────────────────────────────┐
│                    V2.1.0 二维分类矩阵                        │
├───────────┬───────────────────────────────────────────────┤
│           │              业务性质 (WHY - 为什么变?)          │
│           ├───────┬───────┬───────┬───────┬───────┤        │
│ 技术领域   │ REQ   │ DEF   │ OPT   │ CFG   │ EMRG  │        │
│ (WHO      │ 需求  │ 缺陷  │ 优化  │ 配置  │ 紧急  │        │
│ 哪个专业?) │ 变更  │ 修复  │ 改进  │ 调整  │ 变更  │        │
├───────────┼───────┼───────┼───────┼───────┼───────┤        │
│ ELEC电气  │       │       │       │       │       │        │
│ MECH机械  │       │       │       │       │       │        │
│ PLC程序   │ ← 核心域(默认)                                   │
│ HMI程序   │       │       │       │       │       │        │
│ SCPT脚本  │       │       │       │       │       │        │
│ DOCU文档  │       │       │       │       │       │        │
│ SAFE安全  │       │       │       │       │       │        │
└───────────┴───────┴───────┴───────┴───────┴───────┘        │
                                                              │
┌─────────────────────────────────────────────────────────────┤
│            影响范围 (WHERE - 影响到什么程度?)                │
│  LOCAL局部 → MODULE模块级 → SYSTEM系统级 → CROSS跨系统 → SAFE安全 │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 分级审批机制

| 范围(Scope) | 审批层级(ApprovalLevel) | 是否需要复审人 | 适用场景 |
|:------------:|:----------------------:|:-------------:|:---------|
| LOCAL | 项目经理 | 否 | 单个POU/画面/IO点修改 |
| MODULE | 项目负责人 | 否 | 单设备/单线/子系统 |
| SYSTEM | **技术总监** | ✅ **是** | 多模块联动/联锁/通讯 |
| CROSS | **高层管理** | ✅ **是** | 跨子系统(PLC+HMI+电气...) |
| SAFE | **安全负责人** | ✅ **是** | 急停/SIL/安全功能 |

### 2.3 Single Source of Truth 原则

```
V1.x (错误模式):                    V2.1.0 (正确模式):
┌─────────────┐                   ┌─────────────────────────────┐
│  变更台帐     │  ← 内嵌详情    │  变更台帐 (索引)             │
│  (完整副本)   │               │  §4: [→ CHG-xxx](链接)     │
├─────────────┤               ├─────────────────────────────┤
│  变更报告     │  ← 又一份    │  01_变更单/                  │
│  (再次复制)   │               │  ├── CHG-PLC/               │
├─────────────┤               │  │   ├── CHG-PLC-2026-001.md │ ← ★唯一权威记录
│  变更单       │  ← 原始数据   │  │   ├── CHG-PLC-2026-002.md │
│  (可能过时)   │               │  ├── CHG-ELEC/              │
└─────────────┘               │  └── CHG-SAFE/              │
                               └─────────────────────────────┘
```

---

## 3. 现有代码结构 (已升级)

### 3.1 文件清单

```
src/
├── core/
│   └── constants.py          ← [MODIFIED V2.1.0] 新增Domain/Nature/Scope/ApprovalLevel枚举
├── models/
│   └── change.py             ← [REWRITTEN V2.1.0] 新模型: domain/nature/scope/related_changes/...
├── services/
│   └── change_service.py     ← [UPGRADED V2.1.0] 导出模板重写(040 V2.0.0)+台帐重写(041 V2.1.0)
├── dao/
│   └── change_dao.py          ← [EXTENDED V2.1.0] +4新查询方法(list_by_domain/nature/scope/...)
└── ui/widgets/
    └── change_manager.py      ← [UPGRADED V2.1.0] 9列表格+3筛选器+V2.1.0详情显示
```

### 3.2 核心常量定义 (constants.py)

```python
# ===== V2.1.0 技术领域 (WHO) =====
class Domain(Enum):
    ELEC = "ELEC"    # 电气设计
    MECH = "MECH"    # 机械结构
    PLC = "PLC"      # PLC程序 (默认)
    HMI = "HMI"      # HMI程序
    SCPT = "SCPT"    # Python脚本
    DOCU = "DOCU"    # 工程文档
    SAFE = "SAFE"    # 安全功能

# ===== V2.1.0 业务性质 (WHY) =====
class Nature(Enum):
    REQ = "REQ"      # 需求变更
    DEF = "DEF"      # 缺陷修复
    OPT = "OPT"      # 优化改进 (默认)
    CFG = "CFG"      # 配置调整
    EMRG = "EMRG"    # 紧急变更

# ===== V2.1.0 影响范围 (WHERE) =====
class Scope(Enum):
    LOCAL = "LOCAL"        # 局部 (默认)
    MODULE = "MODULE"      # 模块级
    SYSTEM = "SYSTEM"      # 系统级 ⚠️
    CROSS = "CROSS"        # 跨系统
    SAFE = "SAFE"          # 安全相关

# ===== V2.1.0 分级审批映射 =====
SCOPE_APPROVAL_MAP = {
    Scope.LOCAL: ApprovalLevel.PROJECT_MANAGER,
    Scope.MODULE: ApprovalLevel.LEAD,
    Scope.SYSTEM: ApprovalLevel.TECH_DIRECTOR,
    Scope.CROSS: ApprovalLevel.EXECUTIVE,
    Scope.SAFE: ApprovalLevel.SAFETY_OFFICER,
}
```

### 3.3 数据模型 (change.py)

```python
class Change(BaseModel):
    __tablename__ = "changes"

    # === 基础信息 ===
    change_id = Column(String(32))       # CHG-[DOMAIN]-[YYYY]-[XXX]
    project_id = Column(String(32))
    title = Column(String(200))

    # === V2.1.0 二维分类 (替代原type字段) ===
    domain = Column(Enum(Domain), default=Domain.PLC)     # WHO
    nature = Column(Enum(Nature), default=Nature.OPT)     # WHY
    scope = Column(Enum(Scope), default=Scope.LOCAL)      # WHERE
    priority = Column(String(10), default="P2")             # P0/P1/P2/P3

    # === V1.x 兼容 (保留) ===
    type = Column(String(50), nullable=True)               # 旧类型
    impact = Column(Text, nullable=True)                    # 旧影响范围

    # === 变更内容 ===
    content_before = Column(Text)    # §5.1 变更前
    content_after = Column(Text)     # §5.2 变更后

    # === V2.1.0 传播链与关联 ===
    related_changes = Column(JSON, default=list)            # 关联变更ID列表
    propagation_chain = Column(Text)                       # ASCII传播图

    # === V2.1.0 分级审批 ===
    approval_level = Column(String(30))                    # 自动按scope匹配
    reviewer = Column(String(50))                          # 复审人(SYS/CROSS/SAFE时需要)

    # === Helper方法 ===
    @staticmethod
    def generate_change_id(domain, year, sequence) -> str:
        return f"CHG-{domain.value}-{year}-{sequence:03d}"

    def needs_reviewer(self) -> bool:
        return self.scope in [Scope.SYSTEM, Scope.CROSS, Scope.SAFE]

    def to_v2_dict(self) -> dict:
        """导出为V2.1.0字典(用于模板渲染)"""
```

---

## 4. 服务层设计 (V2.1.0)

### 4.1 导出服务 - 符合040 V2.0.0模板

**输出路径**: `{项目}/00_项目管理/04_变更管理/01_变更单/CHG-{DOMAIN}/{change_id}.md`

**输出内容** (完整的§1~§10章节):

```markdown
# 变更单

## 1. 文档基础信息
## 3. 二维分类
### 3.1 技术领域 (WHO) - 7选1 radio
### 3.2 业务性质 (WHY) - 5选1 radio  
### 3.3 影响范围 (WHERE) - 5多选 checkbox
## 4. 变更原因
## 5. 变更内容 (Before/After对比)
## 6. 三维影响评估
### 6.1 项目约束影响
### 6.2 技术领域影响 (7行checklist)
### 6.3 变更传播链 (ASCII图)
## 7. 实施计划
## 8. 分级审批 (自动显示⚠️复审提示)
## 9. 实施记录
## 10. 验证结论
```

### 4.2 台帐生成 - 符合041 V2.1.0引用模式

**输出路径**: `{项目}/00_项目管理/04_变更管理/{项目名}_版本变更台帐.md`

**核心特性**:

| 章节 | 内容 | 与V1.x区别 |
|:----:|:-----|:----------|
| §2 | 台帐说明 (引用模式原则) | **新增** |
| §3 | **4D统计矩阵** (domain×nature + scope/status) | 替代旧的按type统计 |
| §4 | **超链接表格** `[→ CHG-xxx](./01_变更单/...)` | 替代内嵌详情 |
| §5 | **传播链矩阵** (仅SYSTEM/CROSS/SAFE时显示) | **新增** |
| §6 | 相关规范引用 (043/040/042) | 替代旧的附录 |

### 4.3 辅助方法

```python
@staticmethod
def check_propagation_required(change: Change) -> bool:
    """检查是否需要填写传播链"""
    return change.scope in [Scope.SYSTEM, Scope.CROSS, Scope.SAFE]

@staticmethod
def suggest_related_domains(change: Change) -> List[Domain]:
    """建议关联领域 (基于PROPAGATION_RULES)"""
    # 例: PLC+SYSTEM → [HMI, DOCU, SAFE]
    # 例: ELEC+MODULE → [PLC, DOCU]

@staticmethod
def get_statistics(project_id: str) -> dict:
    """4D统计: status + domain + nature + scope"""
```

---

## 5. DAO层扩展 (V2.1.0)

### 5.1 新增查询方法

| 方法 | 签名 | 用途 |
|:----:|:-----|:-----|
| `list_by_domain()` | `(project_id, domain) → List[Change]` | 按技术领域筛选 |
| `list_by_nature()` | `(project_id, nature) → List[Change]` | 按业务性质筛选 |
| `list_by_scope()` | `(project_id, scope) → List[Change]` | 按影响范围筛选 |
| `find_propagation_chain()` | `(change_id) → List[Change]` | 查找关联变更 |

### 5.2 统计接口升级

```python
# V1.x 返回值:
{"total": 10, "draft": 2, "approved": 5, ..., "type_需求变更": 3}

# V2.1.0 返回值:
{
    "total": 10,
    # 按状态 (保留)
    "draft": 2, "approved": 5, ...,
    # V2.1.0: 按领域 (新增)
    "domain_PLC": 5, "domain_ELEC": 2, "domain_HMI": 1, ...,
    # V2.1.0: 按性质 (新增)
    "nature_OPT": 4, "nature_DEF": 3, ...,
    # V2.1.0: 按范围 (新增)
    "scope_LOCAL": 6, "scope_MODULE": 2, "scope_SYSTEM": 2, ...
}
```

---

## 6. UI层设计 (V2.1.0)

### 6.1 主表格升级

| 维度 | V1.x | V2.1.0 |
|:----:|:-----|:-------|
| 列数 | 6列 | **9列** |
| 列定义 | 编号/标题/**类型*/状态/提出人/时间 | 序号/**→链接**/**领域**/**性质**/**范围**/标题/**优先级**/状态/日期 |
| 筛选器 | 仅状态 | **状态 + 领域(7选1) + 性质(5选1) + 范围(5选1)** |

### 6.2 详情显示升级

**V1.x字段**: type, impact, description (软件视角)
**V2.1.0字段**: 
- domain_name (领域中文名)
- nature_name (性质中文名)  
- scope_display (范围+⚠️警告标记)
- priority (P0~P3, 带颜色)
- approval_level (自动匹配的审批层级)
- reviewer (复审人, SYSTEM/CROSS/SAFE时必需)
- content_before / content_after (变更前后对比)

### 6.3 向后兼容处理

对于旧版变更单(仅有type字段):
- 领域列: 尝试从type映射 → 失败显示"-"
- 性质列: 显示"-"
- 范围列: 显示"-(未分类)"

---

## 7. 目录模板更新

### 7.1 结构变化

```
旧 (V1.x):                        新 (V2.1.0):
05_变更管理/                       04_变更管理/
├── 01_变更单/                     ├── 00_变更管理README.md  (新增, 符合043)
├── 02_变更需求/          (删除)     ├── {项目}_版本变更台帐.md (动态生成)
├── 03_变更记录/          (删除)     └── 01_变更单/
├── 04_变更实施/          (删除)         ├── CHG-ELEC/  (新增)
├── 05_变更验收/          (删除)         ├── CHG-MECH/  (新增)
└── 06_变更归档/          (删除)         ├── CHG-PLC/   (新增)
                                     ├── CHG-HMI/   (新增)
                                     ├── CHG-SCPT/  (新增)
                                     ├── CHG-DOCU/  (新增)
                                     └── CHG-SAFE/  (新增)
```

### 7.2 README模板内容

每个新创建项目的 `04_变更管理/00_变更管理README.md` 自动包含:
- 目录结构树 (符合043 V2.1.0)
- 二维分类说明表 (Domain/Nature/Scope)
- 命名规则 (`CHG-[DOMAIN]-[YYYY]-[XXX]`)
- Single Source of Truth 原则说明
- 分级审批对照表

---

## 8. 向后兼容策略

### 8.1 数据库兼容

| 策略 | 说明 |
|:----:|:-----|
| 旧字段保留 | `type`(String), `impact`(Text) 保留为nullable |
| 新字段有默认值 | domain=PLC, nature=OPT, scope=LOCAL |
| 自动迁移 | 启动时检测旧数据库 → ALTER TABLE ADD COLUMN |
| 映射工具 | `Change.migrate_from_v1(old_type)` 静态方法 |

### 8.2 API兼容

| 方法 | 兼容性 |
|:----:|:-----:|
| `create_change()` | 签名不变, 内部自动将type映射为domain+nature |
| `export_change()` | 始终输出V2.1.0格式 |
| `generate_ledger()` | 始终输出V2.1.0格式 |

### 8.3 UI兼容

- 表格使用 `hasattr()` fallback
- 旧变更单显示 "-" 占位符 (不崩溃)

---

## 9. 实施记录

### 9.1 已完成工作 (2026-04-12)

| 阶段 | 任务 | 状态 | 改动量 |
|:----:|:-----|:----:|:-----:|
| P1-1 | constants.py - Domain/Nature/Scope枚举 | ✅ | +80行 |
| P1-2 | change.py - V2.1.0完整模型 | ✅ | 重写145行 |
| P2-a | import语句更新 | ✅ | +4行 |
| P2-b | `_generate_change_content()` 重写为040 V2.0.0 | ✅ | +168行 |
| P2-c | `export_change()` 输出路径修正 | ✅ | 3行 |
| **P2-d** | **`_generate_ledger_content()` 重写为041 V2.1.0** | ✅ | **+164行** |
| **P2-e** | **`generate_ledger()` 路径更新** | ✅ | **3行** |
| P2-f | `get_statistics()` 扩展为4D | ✅ | +16行 |
| P2-g | 新增辅助方法 (2个) | ✅ | +30行 |
| P3 | DAO层 - 4新方法 + 4D统计 | ✅ | +68行 |
| P4 | UI层 - 导入/常量/9列/3筛选器/详情/路径 | ✅ | ~200行 |
| P5 | 目录模板 - 9个模板05→04 + TPL-PLC重构 | ✅ | ~50行 |

**总计**: **~1200行代码修改**, 5个源文件, 0个新文件

### 9.2 修改文件清单

```
SW-2026-004_Python项目管理工具/
└── 03_主程序/01_主程序核心代码/src/
    ├── core/constants.py              ← [MODIFIED] DEFAULT_TEMPLATES (10处)
    ├── dao/change_dao.py             ← [MODIFIED] +4新方法
    ├── services/change_service.py     ← [MODIFIED] 台帐重写+统计+辅助方法
    └── ui/widgets/change_manager.py  ← [MODIFIED] 9列+筛选器+详情
```

---

## 10. 验证标准

### 10.1 功能验证

- [ ] 创建新项目(TPL-PLC-STD-001) → 检查 `04_变更管理/01_变更单/{7领域}/` 结构正确
- [ ] 新建变更单(选择PLC/DEF/SYSTEM) → 自动提示需Tech Director复审
- [ ] 导出变更单 → 文件位于 `04_变更管理/01_变更单/CHG-PLC/`, 格式符合040 V2.0.0
- [ ] 生成台帐 → 文件位于 `04_变更管理/{项目}_版本变更台帐.md`, 格式符合041 V2.1.0
- [ ] UI表格显示9列 + 3个筛选器正常工作
- [ ] 旧数据库导入 → 不崩溃, 旧变更单显示fallback值

### 10.2 回归测试

- [ ] V1.x格式的变更单仍能正常读取和显示
- [ ] 原有的审批流程不受影响
- [ ] 原有的影响分析功能正常工作

---

## 11. 后续可选增强 (未纳入本次升级)

| 优先级 | 功能 | 说明 |
|:------:|:-----|:-----|
| P2 | NewChangeDialog完全重构 | 当前保持基本兼容, 未来改为Domain/Nature/Scope选择器 |
| P2 | "关联变更"Tab页 | UI预留位置, 显示related_changes列表 |
| P3 | 单元测试覆盖 | 新增DAO/service方法的单元测试 |
| P3 | 数据库迁移脚本 | Alembic auto-migration for V1.x → V2.1.0 |
| P3 | Excel导出 | 4D统计数据导出Excel格式 |

---

**文档版本**: DEV-V2.1.0
**编制日期**: 2026-04-12
**编制人**: AI Assistant (基于实际代码升级)
**状态**: ✅ 代码实施完成, 待集成测试
**关联计划**: [.trae/documents/sw004-change-mgmt-v21-upgrade-plan.md](../../.trae/documents/sw004-change-mgmt-v21-upgrade-plan.md)
