# SW-2026-004 变更管理模块 V2.1.0 升级计划

## 一、背景与目标

### 1.1 背景

我们刚刚在 DJ-2026-014 项目中实践验证了**变更管理规范V2.1.0精简工程版**，并通过反向同步将最佳实践写入规范仓库（043 V2.1.0 + 041 V2.1.0 + 042 V2.0.0）。现在需要将这些经过验证的最佳实践**集成到 Python项目管理工具（SW-2026-004）** 中，使工具能够自动生成符合V2.1.0规范的变更单、台帐和目录结构。

### 1.2 目标

将SW-2026-004的变更管理模块从当前的**V1.x软件视角**升级为**V2.1.0工程视角**，使其：
- 支持二维分类（领域×性质×范围）
- 自动生成符合043 V2.1.0的目录结构
- 导出符合040 V2.0.0的变更单模板
- 生成符合041 V2.1.0引用模式的台帐
- 支持传播链追踪和关联变更单管理

---

## 二、现状分析（工具 vs 规范差距）

### 2.1 数据模型差距

| 字段 | 当前工具 (models/change.py) | V2.1.0规范要求 | 差距 |
|------|---------------------------|---------------|:----:|
| type | `String(50)` 自由文本 | `Domain` 枚举(7值) + `Nature` 枚举(5值) | 🔴 需重构 |
| impact_level | `ImpactLevel`(LOW/MED/HIGH 3级) | `Scope`(LOCAL/MODULE/SYSTEM/CROSS/SAFE 5级) | 🔴 需替换 |
| related_changes | ❌ 不存在 | `List[str]` 关联变更单编号列表 | 🔴 需新增 |
| propagation_chain | ❌ 不存在 | `str` 传播链描述(ASCII图+关联编号) | 🔴 需新增 |
| approval_level | ❌ 不存在 | `str` 审批层级(项目经理/负责人/总监/高层/安全) | 🟡 需新增 |
| change_id生成 | `CHG-{YYYYMMDD}-{UUID8}` | `CHG-[DOMAIN]-[YYYY]-[XXX]` | 🟡 需修改 |

### 2.2 常量定义差距

| 常量 | 当前值 | V2.1.0规范值 | 差距 |
|------|--------|-------------|:----:|
| ChangeType | CODE/CONFIG/DEPENDENCY/DOCUMENT/STRUCTURE/TEMPLATE/PLUGIN (软件7类) | ELEC/MECH/PLC/HMI/SCPT/DOCU/SAFE (工程7域) | 🔴 完全不同 |
| Nature | ❌ 不存在 | REQ/DEF/OPT/CFG/EMRG | 🔴 缺失 |
| Scope(ImpactLevel) | LOW/MEDIUM/HIGH | LOCAL/MODULE/SYSTEM/CROSS/SAFE | 🔴 不匹配 |
| UI CHANGE_TYPES | ["需求变更","设计变更","技术变更","资源变更","进度变更","其他"] | 应使用Domain+Nature组合 | 🔴 与常量层不一致 |

### 2.3 服务层差距

| 功能 | 当前实现 | V2.1.0要求 | 差距 |
|------|---------|-----------|:----:|
| export_change() | 导出V1.0格式markdown | 导出040 V2.0.0完整模板(§1~§10) | 🔴 模板需重写 |
| generate_ledger() | 生成内嵌详情表格(CHG-V1.0.0) | 生成引用模式表格(CHG-V2.1.0, 含超链接) | 🔴 格式需重写 |
| get_statistics() | 2维(status+type) | 4维(domain+nature+scope+status) | 🟡 需扩展 |
| 目录结构生成 | `05_变更管理/{01~06}` 6子目录 | `04_变更管理/01_变更单/{7领域子目录}` | 🔴 结构需改 |
| 传播链检测 | ❌ 无 | SYSTEM/CROSS级自动提示填写 | 🔴 缺失 |

### 2.4 UI层差距

| 组件 | 当前 | V2.1.0要求 | 差距 |
|------|------|-----------|:----:|
| 表格列 | 编号/标题/**类型*/状态/提出人/时间 (6列) | 编号/链接/领域/性质/范围/标题/优先级/状态 (8列) | 🟡 列需调整 |
| 筛选器 | 状态筛选 + 文本搜索 | +领域筛选 + 性质筛选 + 范围筛选 | 🟡 需新增 |
| 详情Tab | 变更详情/流程操作/影响分析 (3个) | +传播链Tab + 关联变更Tab | 🟡 需新增 |
| 新建表单 | 标题/类型(下拉)/原因/影响/附件 | +领域(7选1)+性质(5选1)+范围(5多选)+关联变更 | 🔴 表单需重构 |

### 2.5 目录模板差距

| 项目 | 当前 (DEFAULT_TEMPLATES) | V2.1.0规范 |
|------|-------------------------|-----------|
| 根目录名 | `05_变更管理` | `04_变更管理` |
| 子目录数 | 6个 (01_变更单 ~ 06_变更归档) | 1个核心 (01_变更单) + 7个领域子目录 |
| 台帐位置 | `03_变更记录/` 子目录 | 根目录下独立文件 |
| README | 无 | 推荐 |

---

## 三、升级方案（分阶段实施）

### Phase 1: 数据模型与常量层重构 (P0 - 基础)

#### 1.1 新增/修改常量 (`src/core/constants.py`)

```python
# ===== V2.1.0 新增: 技术领域 (WHO) =====
class Domain(Enum):
    """技术领域 - 变更所属专业"""
    ELEC = "ELEC"    # 电气设计
    MECH = "MECH"    # 机械结构
    PLC = "PLC"      # PLC程序
    HMI = "HMI"      # HMI程序
    SCPT = "SCPT"    # Python脚本
    DOCU = "DOCU"    # 工程文档
    SAFE = "SAFE"    # 安全功能

DOMAIN_NAMES = {
    Domain.ELEC: "电气设计",
    Domain.MECH: "机械结构",
    Domain.PLC: "PLC程序",
    Domain.HMI: "HMI程序",
    Domain.SCPT: "Python脚本",
    Domain.DOCU: "工程文档",
    Domain.SAFE: "安全功能"
}

# ===== V2.1.0 新增: 业务性质 (WHY) =====
class Nature(Enum):
    """业务性质 - 变更驱动因素"""
    REQ = "REQ"      # 需求变更
    DEF = "DEF"      # 缺陷修复
    OPT = "OPT"      # 优化改进
    CFG = "CFG"      # 配置调整
    EMRG = "EMRG"    # 紧急变更

NATURE_NAMES = {
    Nature.REQ: "需求变更",
    Nature.DEF: "缺陷修复",
    Nature.OPT: "优化改进",
    Nature.CFG: "配置调整",
    Nature.EMRG: "紧急变更"
}

# ===== V2.1.0 替换: 影响范围 (WHERE) =====
class Scope(Enum):
    """影响范围"""
    LOCAL = "LOCAL"        # 局部
    MODULE = "MODULE"      # 模块级
    SYSTEM = "SYSTEM"      # 系统级
    CROSS = "CROSS"        # 跨系统
    SAFE = "SAFE"          # 安全相关

SCOPE_NAMES = {
    Scope.LOCAL: "局部",
    Scope.MODULE: "模块级",
    Scope.SYSTEM: "系统级 ⚠️",
    Scope.CROSS: "跨系统",
    Scope.SAFE: "安全相关"
}

# ===== V2.1.0 替换: 审批层级 =====
class ApprovalLevel(Enum):
    """审批层级(按范围自动匹配)"""
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
```

#### 1.2 重构数据模型 (`src/models/change.py`)

```python
class Change(Base):
    __tablename__ = 'changes'

    # === 基础信息 ===
    change_id = Column(String(30), primary_key=True)  # CHG-[DOMAIN]-[YYYY]-[XXX]
    project_id = Column(String(20), ForeignKey('projects.project_id'), nullable=False)
    title = Column(String(200), nullable=False)

    # === V2.1.0 二维分类 (替代原type字段) ===
    domain = Column(Enum(Domain), nullable=False, default=Domain.PLC)     # 技术领域
    nature = Column(Enum(Nature), nullable=False, default=Nature.OPT)     # 业务性质
    scope = Column(Enum(Scope), nullable=False, default=Scope.LOCAL)     # 影响范围
    priority = Column(String(10), default="P2")                          # P0/P1/P2/P3

    # === 变更内容 ===
    reason = Column(Text)           # 变更原因(§4)
    content_before = Column(Text)   # 变更前(§5.1)
    content_after = Column(Text)    # 变更后(§5.2)

    # === V2.1.0 新增: 传播链与关联 ===
    related_changes = Column(JSON, default=list)       # 关联变更单ID列表 [str]
    propagation_chain = Column(Text)                   # 传播链描述(ASCII图)

    # === V2.1.0 新增: 分级审批 ===
    approval_level = Column(String(30))               # 审批层级(自动按scope匹配)
    reviewer = Column(String(50))                     # 复审人(SYS/CROSS/SAFE时)

    # === 原有字段保留(兼容) ===
    description = Column(Text)       # 详细描述
    impact_analysis = Column(Text)   # 影响分析(§6, 可保留为补充说明)
    status = Column(Enum(ChangeStatus), default=ChangeStatus.DRAFT)
    proposer = Column(String(50))
    approver = Column(String(50))
    implementer = Column(String(50))
    attachment = Column(JSON, default=dict)

    # === 时间戳 ===
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)
    approved_at = Column(DateTime)
    implemented_at = Column(DateTime)
    completed_at = Column(DateTime)

    project = relationship("Project", back_populates="changes")

    def update_from_dict(self, data: dict):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
```

#### 1.3 修改ChangeID生成逻辑

```python
@staticmethod
def generate_change_id(domain: Domain, year: int, sequence: int) -> str:
    """V2.1.0命名规则: CHG-[DOMAIN]-[YYYY]-[XXX]"""
    return f"CHG-{domain.value}-{year}-{sequence:03d}"
```

### Phase 2: 服务层升级 (P0 - 核心)

#### 2.1 重写导出模板 (`src/services/change_service.py` → `export_change()`)

将现有的V1.0格式导出完全重写为符合 **040_通用变更单模板_CHG-V2.0.0** 的完整格式：

输出文件路径: `{项目根}/00_项目管理/04_变更管理/01_变更单/CHG-{DOMAIN}/CHG-{DOMAIN}-{YYYY}-{XXX}.md`

输出内容包含完整的§1~§10章节，特别是：
- §3: 二维分类（自动从model填充）
- §5: 变更前后对比（content_before / content_after）
- §6: 三维影响评估（含§6.2跨领域检查 + §6.3传播链）
- §8: 分级审批（根据scope自动匹配approval_level）
- §10: 验证结论

#### 2.2 重写台帐生成 (`generate_ledger()`)

将现有内嵌详情表格改为**引用模式**：
- §4每行只含摘要 + 超链接 `[→ CHG-xxx](./01_变更单/CHG-{DOMAIN}/...)`
- §3统计扩展为4维（domain/nature/scope/status）
- §5新增传播链矩阵
- 输出路径: `{项目根}/00_项目管理/04_变更管理/{项目}_版本变更台帐.md`

#### 2.3 扩展统计方法 (`get_statistics()`)

```python
def get_statistics(project_id: str) -> dict:
    return {
        "total": total,
        # 按状态
        **{s.value: count for s in ChangeStatus},
        # V2.1.0: 按领域
        **{f"domain_{d.value}": count for d in Domain},
        # V2.1.0: 按性质
        **{f"nature_{n.value}": count for n in Nature},
        # V2.1.0: 按范围
        **{f"scope_{s.value}": count for s in Scope},
    }
```

#### 2.4 新增传播链辅助方法

```python
def check_propagation_required(change: Change) -> bool:
    """检查是否需要填写传播链(SYSTEM/CROSS/SAFE级必须)"""
    return change.scope in [Scope.SYSTEM, Scope.CROSS, Scope.SAFE]

def suggest_related_domains(change: Change) -> List[Domain]:
    """根据当前domain和scope建议可能受影响的关联领域"""
    # 例: PLC+SYSTEM → 可能影响[HMI, DOCU, SAFE]
    # 例: ELEC+MODULE → 可能影响[PLC, DOCU]
    PROPAGATION_RULES = {
        (Domain.PLC, Scope.SYSTEM): [Domain.HMI, Domain.DOCU, Domain.SAFE],
        (Domain.ELEC, Scope.MODULE): [Domain.PLC, Domain.DOCU],
        # ... 更多规则
    }
    return PROPAGATION_RULES.get((change.domain, change.scope), [])
```

### Phase 3: DAO层适配 (P1)

#### 3.1 新增查询方法

```python
@staticmethod
def list_by_domain(project_id: str, domain: Domain) -> List[Change]:
    """按技术领域查询"""

@staticmethod
def list_by_nature(project_id: str, nature: Nature) -> List[Change]:
    """按业务性质查询"""

@staticmethod
def list_by_scope(project_id: str, scope: Scope) -> List[Change]:
    """按影响范围查询"""

@staticmethod
def find_propagation_chain(change_id: str) -> List[Change]:
    """查找某变更的所有关联变更(通过related_changes字段)"""
```

#### 3.2 修改get_statistics()支持4D统计

### Phase 4: UI层升级 (P1)

#### 4.1 修改新建变更对话框

当前: 标题 + 类型下拉(6选项) + 原因 + 影响 + 附件
改为:
- 标题 (必填)
- **领域** (7选1 radio/group, 默认=PLC)
- **性质** (5选1 radio/group, 默认=OPT)
- **范围** (5个checkbox, 默认=LOCAL, 多选时取最高级)
- 变更原因 (textarea)
- 变更前/后对比 (两个textarea或diff editor)
- 关联变更 (可选, autocomplete搜索已有变更单)
- 附件 (不变)

当用户选择SYSTEM/CROSS/SAFE范围时:
- 自动弹出提示: "此变更需要[Tech Director]复审"
- 显示传播链编辑区域(可选填)

#### 4.2 修改主表格

当前列: 编号 | 标题 | **类型** | 状态 | 提出人 | 时间
改为: 编号 | **→链接** | **领域** | **性质** | **范围** | 标题 | **优先级** | 状态

新增筛选器行:
- [领域 ▼] [性质 ▼] [范围 ▼] | 状态 ▼ | [搜索框]

#### 4.3 新增/修改Tab页

- **影响分析Tab**: 从纯文本改为结构化显示(领域影响checklist + 传播链可视化)
- **关联变更Tab**: 新增, 显示related_changes中的所有关联变更单(可点击跳转)

#### 4.4 删除旧的UI CHANGE_TYPES硬编码

移除 `change_manager.py` 顶部的 `CHANGE_TYPES = [...]`, 改用 `constants.py` 的 `Domain` + `Nature` 组合。

### Phase 5: 目录模板更新 (P1)

#### 5.1 修改 `DEFAULT_TEMPLATES` 中变更管理部分

```python
# 旧: "05_变更管理": [...6个子目录...]
# 新:
"04_变更管理": [
    ("01_变更单", "变更单档案(按领域分子目录)", True),
    ("01_变更单/CHG-ELEC", "电气设计类变更单", False),
    ("01_变更单/CHG-MECH", "机械结构类变更单", False),
    ("01_变更单/CHG-PLC", "PLC程序类变更单", False),
    ("01_变更单/CHG-HMI", "HMI程序类变更单", False),
    ("01_变更单/CHG-SCPT", "Python脚本类变更单", False),
    ("01_变更单/CHG-DOCU", "工程文档类变更单", False),
    ("01_变更单/CHG-SAFE", "安全功能类变更单", False),
],
```

同时删除 `05_变更管理` 条目（如存在）。

#### 5.2 新增README生成

工具在创建项目的`04_变更管理/`目录时, 自动生成一个README.md(基于043 V2.1.0模板).

---

## 四、向后兼容策略

### 4.1 数据库迁移

- 旧字段 `type`(String) → 迁移到新字段 `domain` + `nature`
  - 映射规则: "功能变更"→(SCPT,REQ), "Bug修复"→(SCPT,DEF), ... (需定义映射表)
  - 旧 `impact_level` → 迁移到 `scope` (LOW→LOCAL, MEDIUM→MODULE, HIGH→SYSTEM)
- 旧 `change_id` 格式保持可读(不强制重命名历史数据)
- 使用 Alembic 或应用启动时的 auto-migration 脚本

### 4.2 API兼容

- `ChangeService.create()` 签名扩展(新增参数均有默认值), 不破坏旧调用
- `export_change()` 和 `generate_ledger()` 增加 `version` 参数:
  - `version="v1"` → 旧格式(兼容模式)
  - `version="v2"` → V2.1.0新格式(默认)

---

## 五、实施顺序与依赖关系

```
Phase 1 (常量+模型) ──→ Phase 2 (服务层) ──┬──→ Phase 3 (DAO)
                                          │
                                          ├──→ Phase 4 (UI)
                                          │
                                          └──→ Phase 5 (目录模板)
```

- Phase 1 必须最先完成 (后续全部依赖新常量和模型)
- Phase 2 完成后, Phase 3/4/5 可并行执行
- 建议先完成 Phase 1+2 (确保核心逻辑正确), 再做UI

---

## 六、验证标准

1. **单元测试**: 新增Domain/Nature/Scope枚举的正确性; ID生成规则; 传播链建议逻辑
2. **集成测试**: 创建一个完整变更单 → 导出到markdown → 验证格式符合040 V2.0.0
3. **台帐测试**: 创建多个变更单(含关联) → 生成台帐 → 验证引用模式+4D统计
4. **目录测试**: 用工具创建新项目 → 检查04_变更管理目录结构是否符合043 V2.1.0
5. **回归测试**: 旧格式的变更单仍能正常读取和显示(兼容模式)
