# SW-2026-004 变更管理模块 V2.1.0 升级 - 继续执行计划

> **计划日期**: 2026-04-12
> **状态**: 🔄 执行中（Phase 1已完成，Phase 2进行中）
> **原始计划**: `.trae/documents/sw004-change-mgmt-v21-upgrade-plan.md`

---

## 一、当前进度确认

### ✅ 已完成部分

| 阶段 | 文件 | 状态 | 完成内容 |
|:----:|------|:----:|---------|
| **P1-1** | [constants.py](03_主程序/01_主程序核心代码/src/core/constants.py) | ✅ 100% | Domain/Nature/Scope/ApprovalLevel枚举 + 迁移映射 |
| **P1-2+1.3** | [change.py](03_主程序/01_主程序核心代码/src/models/change.py) | ✅ 100% | V2.1.0完整模型 + helper方法 |
| **P2-a** | [change_service.py](03_主程序/01_主程序核心代码/src/services/change_service.py#L12-L16) | ✅ | import语句已更新 |
| **P2-b** | [change_service.py#L356-L523](03_主程序/01_主程序核心代码/src/services/change_service.py#L356-L523) | ✅ | `_generate_change_content()` 完全重写为040 V2.0.0模板(§1~§10) |
| **P2-c** | [change_service.py#L329-L339](03_主程序/01_主程序核心代码/src/services/change_service.py#L329-L339) | ✅ | `export_change()` 输出路径修正为`04_变更管理/01_变更单/CHG-{DOMAIN}/` |

### ❌ 待完成部分

| 阶段 | 文件/方法 | 当前行号 | 问题 | 优先级 |
|:----:|----------|:-------:|:-----|:------:|
| **P2-d** | `change_service.py:_generate_ledger_content()` | L564-L692 | 仍生成V1.0.0内嵌详情格式，需改为041 V2.1.0引用模式 | 🔴 P0 |
| **P2-e** | `change_service.py:generate_ledger()` | L542-L547 | 输出路径仍为`05_变更管理/03_变更记录/`，需改为`04_变更管理/{项目}_版本变更台帐.md` | 🔴 P0 |
| **P2-f** | `change_service.py` | L304-L310 | `get_statistics()`仅返回2D(status+type)，需扩展为4D(+domain+nature+scope) | 🟡 P1 |
| **P2-g** | `change_service.py` | 缺失 | 需新增`check_propagation_required()`和`suggest_related_domains()`辅助方法 | 🟡 P1 |
| **P3-a** | [change_dao.py](03_主程序/01_主程序核心代码/src/dao/change_dao.py) | 全文 | 缺少`list_by_domain/nature/scope()`、`find_propagation_chain()`方法 | 🟡 P1 |
| **P3-b** | `change_dao.py:get_statistics()` | L112-L133 | 需扩展支持4D统计(domain+nature+scope维度) | 🟡 P1 |
| **P4-a** | [change_manager.py](03_主程序/01_主程序核心代码/src/ui/widgets/change_manager.py) | L45-L52 | `CHANGE_TYPES`硬编码(6项≠常量层)，需改用Domain+Nature组合 | 🔴 P1 |
| **P4-b** | `change_manager.py:_init_ui()` | L121-L122 | 表格仅6列(编号/标题/**类型*/状态/提出人/时间)，需改为8列(编号/链接/领域/性质/范围/标题/优先级/状态) | 🔴 P1 |
| **P4-c** | `change_manager.py:_init_ui()` | L95-L101 | 仅状态筛选器，需新增领域/性质/范围筛选器 | 🟡 P1 |
| **P4-d** | `NewChangeDialog._init_ui()` | L686-L731 | 表单仅有标题+类型下拉(V1.x)，需重构为领域(7选1)+性质(5选1)+范围(5多选)+关联变更 | 🔴 P1 |
| **P4-e** | `change_manager.py` | L132-L235 | 详情Tab仅3个(变更详情/流程操作/影响分析)，需新增传播链Tab+关联变更Tab | 🟡 P2 |
| **P4-f** | `change_manager.py:_show_change_detail()` | L327-L357 | 详情显示仍用V1.x字段(type/impact)，需改为V2.1.0字段(domain/nature/scope) | 🟡 P1 |
| **P4-g** | `change_manager.py:_on_view_ledger()` / `_load_ledger_content()` | L455-L509 | 台帐路径仍为V1.0.0路径，需同步更新 | 🟡 P2 |
| **P5-a** | [constants.py#L184-L858](03_主程序/01_主程序核心代码/src/core/constants.py#L184-L858) | DEFAULT_TEMPLATES | 所有模板的`05_变更管理`需改为`04_变更管理`且子目录结构需调整 | 🟡 P1 |

---

## 二、详细执行步骤

### Step 1: 完成 Phase 2 剩余工作 (🔴 最高优先级)

#### 1.1 重写 `_generate_ledger_content()` 方法

**目标**: 将当前的V1.0.0内嵌详情表格完全替换为041 V2.1.0引用模式

**当前实现问题** ([change_service.py#L564-L692](03_主程序/01_主程序核心代码/src/services/change_service.py#L564-L692)):
```python
# 当前: 生成内嵌详情表格 (每行包含完整信息)
def _generate_ledger_content(project, changes):
    # §4: 每行 = 编号/标题/类型/状态/提出人/日期 (全部内嵌)
    # §5: 按type统计 (V1.x)
```

**目标实现**:
```python
# 目标: 引用模式 (每行=摘要+超链接)
def _generate_ledger_content(project, changes):
    # §3: 4D统计表格 (domain × nature × scope × status)
    # §4: 每行 = 序号/链接(CHG-xxx→)/领域/性质/范围/标题/优先级/状态/日期
    #     其中链接列使用markdown超链接: `[→ CHG-xxx](./01_变更单/CHG-{DOMAIN}/CHG-{DOMAIN}-{YYYY}-{XXX}.md)`
    # §5: 新增传播链矩阵 (如有跨域变更)
    # §6: 跨引用验证 (检查所有链接有效性)
```

**具体改动点**:
1. **§3 统计区域**:
   - 删除: 按`type`(V1.x)统计表格
   - 新增: 4维统计表格
     ```
     | 维度 | ELEC | MECH | PLC | HMI | SCPT | DOCU | SAFE | 合计 |
     |:----:|:----:|:----:|:---:|:---:|:----:|:----:|:----:|:----:|
     | REQ  |  0   |  0   |  2  |  0  |  1   |  0   |  0   |  3   |
     | DEF  | ...                                                            |
     | OPT  | ...                                                            |
     | CFG  | ...                                                            |
     | EMRG | ...                                                            |
     | 合计 |                                                              | N   |
     
     + 按scope统计行
     + 按status统计行
     ```

2. **§4 变更记录表格**:
   - 列定义: `序号 | → 变更单 | 领域 | 性质 | 范围 | 标题 | 优先级 | 状态 | 提出人 | 日期`
   - "→ 变更单"列内容: `[→ {change_id}](./01_变更单/{domain_dir}/{change_id}.md)`
   - 领域/性质/范围列: 使用中文名称 (DOMAIN_NAMES/NATURE_NAMES/SCOPE_NAMES)
   - 状态列: 带颜色标记 (✅已完成/⚠️待审批/🚫已取消)

3. **§5 传播链矩阵** (新增):
   ```markdown
   ## 5. 变更传播链矩阵
   
   > 仅当存在SYSTEM/CROSS/SAFE级别变更时显示此节
   
   | 原始变更 | 影响方向 | 受影响变更 | 影响说明 |
   |:--------:|:-------:|:----------:|:---------|
   | CHG-PLC-2026-001 | → | CHG-HMI-2026-003 | 画面变量映射需同步 |
   ```
   
4. **删除冗余章节**:
   - 删除 §6 (版本详细变更说明 - 内嵌式，与引用模式矛盾)
   - 删除 §7 (附录 - 过于冗长)
   - 删除 §8 (流程执行统计 - 不属于台帐职责)
   - 简化 §9 (相关文档 - 改为仅保留链接列表)

#### 1.2 更新 `generate_ledger()` 输出路径

**当前** ([L542-L547](03_主程序/01_主程序核心代码/src/services/change_service.py#L542-L547)):
```python
output_path = os.path.join(
    project.path,
    "05_变更管理",        # ❌ 旧目录名
    "03_变更记录",         # ❌ 旧子目录
    "版本变更台帐_CHG-V1.0.0.md"  # ❌ 旧版本号
)
```

**目标**:
```python
output_path = os.path.join(
    project.path,
    "00_项目管理",
    "04_变更管理",                    # ✅ 新目录名
    f"{project.name}_版本变更台帐.md"  # ✅ 项目名+无版本号(动态更新)
)
```

#### 1.3 扩展 `get_statistics()` 为4D统计

**当前** ([L304-L310](03_主程序/01_主程序核心代码/src/services/change_service.py#L304-L310)):
```python
def get_statistics(project_id: str) -> dict:
    return ChangeDAO.get_statistics(project_id)  # 返回 {total, status_xxx, type_xxx}
```

**目标**:
```python
def get_statistics(project_id: str) -> dict:
    dao_stats = ChangeDAO.get_statistics(project_id)
    
    return {
        "total": dao_stats["total"],
        
        # 按状态 (原有)
        **{s.value: dao_stats.get(s.value, 0) for s in ChangeStatus},
        
        # V2.1.0: 按领域 (新增)
        **{f"domain_{d.value}": dao_stats.get(f"domain_{d.value}", 0) for d in Domain},
        
        # V2.1.0: 按性质 (新增)
        **{f"nature_{n.value}": dao_stats.get(f"nature_{n.value}", 0) for n in Nature},
        
        # V2.1.0: 按范围 (新增)
        **{f"scope_{s.value}": dao_stats.get(f"scope_{s.value}", 0) for s in Scope},
    }
```

#### 1.4 新增辅助方法

在 `ChangeService` 类中新增两个静态方法:

```python
@staticmethod
def check_propagation_required(change: Change) -> bool:
    """检查是否需要填写传播链(SYSTEM/CROSS/SAFE级必须)"""
    return change.scope in [Scope.SYSTEM, Scope.CROSS, Scope.SAFE]

@staticmethod
def suggest_related_domains(change: Change) -> List[Domain]:
    """根据当前domain和scope建议可能受影响的关联领域
    
    规则示例:
    - PLC + SYSTEM → 可能影响 [HMI, DOCU, SAFE]
    - ELEC + MODULE → 可能影响 [PLC, DOCU]
    - HMI + CROSS → 可能影响 [PLC, SCPT, DOCU]
    """
    PROPAGATION_RULES = {
        (Domain.PLC, Scope.SYSTEM): [Domain.HMI, Domain.DOCU, Domain.SAFE],
        (Domain.PLC, Scope.CROSS): [Domain.ELEC, Domain.MECH, Domain.HMI, Domain.SCPT, Domain.DOCU],
        (Domain.ELEC, Scope.MODULE): [Domain.PLC, Domain.DOCU],
        (Domain.ELEC, Scope.SYSTEM): [Domain.PLC, Domain.SAFE, Domain.DOCU],
        (Domain.MECH, Scope.MODULE): [Domain.ELEC, Domain.DOCU],
        (Domain.HMI, Scope.SYSTEM): [Domain.PLC, Domain.SCPT, Domain.DOCU],
        (Domain.HMI, Scope.CROSS): [Domain.PLC, Domain.SCPT, Domain.DOCU],
        (Domain.SCPT, Scope.SYSTEM): [Domain.DOCU, Domain.HMI],
        (Domain.SCPT, Scope.CROSS): [Domain.PLC, Domain.HMI, Domain.DOCU],
        (Domain.SAFE, Scope.LOCAL): [Domain.PLC, Domain.ELEC],  # 安全变更通常影响控制层
        (Domain.SAFE, Scope.MODULE): [Domain.PLC, Domain.ELEC, Domain.DOCU],
    }
    return PROPAGATION_RULES.get((change.domain, change.scope), [])
```

---

### Step 2: 升级 DAO 层 (🟡 高优先级)

#### 2.1 在 `change_dao.py` 中新增查询方法

在现有方法后追加:

```python
@staticmethod
def list_by_domain(project_id: str, domain: Domain) -> List[Change]:
    """按技术领域查询"""
    with db.get_session() as session:
        return session.query(Change).filter(
            Change.project_id == project_id,
            Change.domain == domain
        ).order_by(Change.created_at.desc()).all()

@staticmethod
def list_by_nature(project_id: str, nature: Nature) -> List[Change]:
    """按业务性质查询"""
    with db.get_session() as session:
        return session.query(Change).filter(
            Change.project_id == project_id,
            Change.nature == nature
        ).order_by(Change.created_at.desc()).all()

@staticmethod
def list_by_scope(project_id: str, scope: Scope) -> List[Change]:
    """按影响范围查询"""
    with db.get_session() as session:
        return session.query(Change).filter(
            Change.project_id == project_id,
            Change.scope == scope
        ).order_by(Change.created_at.desc()).all()

@staticmethod
def find_propagation_chain(change_id: str) -> List[Change]:
    """查找某变更的所有关联变更(通过related_changes字段)"""
    with db.get_session() as session:
        change = session.query(Change).filter(Change.change_id == change_id).first()
        if not change or not change.related_changes:
            return []
        
        related_ids = change.related_changes
        return session.query(Change).filter(
            Change.change_id.in_(related_ids)
        ).all()
```

#### 2.2 修改 `get_statistics()` 支持4D统计

**当前实现** ([L112-L133](03_主程序/01_主程序核心代码/src/dao/change_dao.py#L112-L133)):
```python
def get_statistics(project_id: str) -> dict:
    # ...
    # 按type统计 (V1.x)
    type_counts = {}
    types = session.query(Change.type).distinct().all()
    for (change_type,) in types:
        type_counts[change_type] = query.filter(Change.type == change_type).count()
    
    return {"total": total, **status_counts, **{f"type_{k}": v for k, v in type_counts.items()}}
```

**目标实现**:
```python
def get_statistics(project_id: str) -> dict:
    from src.core.constants import Domain, Nature, Scope, ChangeStatus
    
    with db.get_session() as session:
        query = session.query(Change).filter(Change.project_id == project_id)
        total = query.count()
        
        result = {"total": total}
        
        # 按状态统计 (原有)
        for status in ChangeStatus:
            result[status.value] = query.filter(Change.status == status).count()
        
        # V2.1.0: 按领域统计 (新增)
        for domain in Domain:
            result[f"domain_{domain.value}"] = query.filter(Change.domain == domain).count()
        
        # V2.1.0: 按性质统计 (新增)
        for nature in Nature:
            result[f"nature_{nature.value}"] = query.filter(Change.nature == nature).count()
        
        # V2.1.0: 按范围统计 (新增)
        for scope in Scope:
            result[f"scope_{scope.value}"] = query.filter(Change.scope == scope).count()
        
        return result
```

同时修改或标记废弃以下两个旧方法:
- `count_by_type()` (L136-L144) - 标记为 `@deprecated`，建议使用新的`get_statistics()`中的domain/nature维度
- `count_by_status()` (L147-L153) - 同上

---

### Step 3: 升级 UI 层 (🔴 高优先级)

#### 3.1 修改导入和常量

**当前** ([L20](03_主程序/01_主程序核心代码/src/ui/widgets/change_manager.py#L20)):
```python
from src.core.constants import ChangeStatus
```

**目标**:
```python
from src.core.constants import (
    ChangeStatus, Domain, Nature, Scope,
    DOMAIN_NAMES, NATURE_NAMES, SCOPE_NAMES,
    SCOPE_APPROVAL_MAP,
)
```

**删除硬编码** ([L45-L52](03_主程序/01_主程序核心代码/src/ui/widgets/change_manager.py#L45-L52)):
```python
# 删除此块:
CHANGE_TYPES = [
    "需求变更",
    "设计变更",
    "技术变更",
    "资源变更",
    "进度变更",
    "其他变更"
]
```

新增常量字典:
```python
# V2.1.0: 领域/性质/范围选择项
DOMAIN_OPTIONS = [(d.value, DOMAIN_NAMES[d]) for d in Domain]  # [("ELEC", "电气设计"), ...]
NATURE_OPTIONS = [(n.value, NATURE_NAMES[n]) for n in Nature]   # [("REQ", "需求变更"), ...]
SCOPE_OPTIONS = [(s.value, SCOPE_NAMES[s]) for s in Scope]      # [("LOCAL", "局部"), ...]

# 范围颜色 (用于表格高亮)
SCOPE_COLORS = {
    Scope.LOCAL: "#4CAF50",    # 绿色 - 低风险
    Scope.MODULE: "#FF9800",   # 橙色 - 中等
    Scope.SYSTEM: "#F44336",   # 红色 - 高风险 ⚠️
    Scope.CROSS: "#9C27B0",    # 紫色 - 跨系统
    Scope.SAFE: "#000000",     # 黑色 - 安全相关
}
```

#### 3.2 重构主表格

**当前** ([L121-L122](03_主程序/01_主程序核心代码/src/ui/widgets/change_manager.py#L121-L122)):
```python
self.change_table.setColumnCount(6)
self.change_table.setHorizontalHeaderLabels(["变更编号", "标题", "类型", "状态", "提出人", "创建时间"])
```

**目标**:
```python
self.change_table.setColumnCount(9)
self.change_table.setHorizontalHeaderLabels([
    "序号", "→ 变更单", "领域", "性质", "范围", "标题", "优先级", "状态", "日期"
])
```

**修改 `_load_changes()` 中的填充逻辑** ([L284-L298](03_主程序/01_主程序核心代码/src/ui/widgets/change_manager.py#L284-L298)):

```python
for row, change in enumerate(changes):
    self.change_table.insertRow(row)
    
    # 序号
    self.change_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
    
    # → 变更单 (带超链接样式的文本)
    link_item = QTableWidgetItem(f"→ {change.change_id}")
    link_item.setForeground(QColor("#2196F3"))  # 蓝色链接样式
    link_item.setToolTip(f"点击查看: {change.change_id}")
    self.change_table.setItem(row, 1, link_item)
    
    # 领域 (中文名)
    domain_name = DOMAIN_NAMES.get(change.domain, change.domain.value)
    self.change_table.setItem(row, 2, QTableWidgetItem(domain_name))
    
    # 性质 (中文名)
    nature_name = NATURE_NAMES.get(change.nature, change.nature.value)
    self.change_table.setItem(row, 3, QTableWidgetItem(nature_name))
    
    # 范围 (带警告标记)
    scope_display = change.get_scope_display() if hasattr(change, 'get_scope_display') else SCOPE_NAMES.get(change.scope, "")
    scope_item = QTableWidgetItem(scope_display)
    if change.needs_reviewer() if hasattr(change, 'needs_reviewer') else False:
        scope_item.setBackground(QColor("#FFF3E0"))  # 浅橙色背景提醒
    self.change_table.setItem(row, 4, scope_item)
    
    # 标题
    self.change_table.setItem(row, 5, QTableWidgetItem(change.title))
    
    # 优先级
    prio_item = QTableWidgetItem(change.priority or "P2")
    if change.priority == "P0":
        prio_item.setForeground(QColor("#F44336"))
    elif change.priority == "P1":
        prio_item.setForeground(QColor("#FF9800"))
    self.change_table.setItem(row, 6, prio_item)
    
    # 状态 (带颜色)
    status_item = QTableWidgetItem(CHANGE_STATUS_NAMES.get(change.status, str(change.status)))
    status_item.setForeground(QColor(CHANGE_STATUS_COLORS.get(change.status, "#000000")))
    self.change_table.setItem(row, 7, status_item)
    
    # 日期
    self.change_table.setItem(row, 8, QTableWidgetItem(
        change.created_at.strftime("%Y-%m-%d") if change.created_at else ""
    ))
```

#### 3.3 新增筛选器行

**当前** ([L93-L106](03_主程序/01_主程序核心代码/src/ui/widgets/change_manager.py#L93-L106)):
```python
toolbar = QHBoxLayout()
# 仅: 状态筛选 + 搜索框 + 按钮
```

**目标**: 在toolbar中新增3个QComboBox:

```python
# 领域筛选 (新增)
self.domain_filter = QComboBox()
self.domain_filter.addItem("全部领域", None)
for domain in Domain:
    self.domain_filter.addItem(DOMAIN_NAMES[domain], domain)
self.domain_filter.currentIndexChanged.connect(self._load_changes)
toolbar.addWidget(QLabel("领域:"))
toolbar.addWidget(self.domain_filter)

# 性质筛选 (新增)
self.nature_filter = QComboBox()
self.nature_filter.addItem("全部性质", None)
for nature in Nature:
    self.nature_filter.addItem(NATURE_NAMES[nature], nature)
self.nature_filter.currentIndexChanged.connect(self._load_changes)
toolbar.addWidget(QLabel("性质:"))
toolbar.addWidget(self.nature_filter)

# 范围筛选 (新增)
self.scope_filter = QComboBox()
self.scope_filter.addItem("全部范围", None)
for scope in Scope:
    self.scope_filter.addItem(SCOPE_NAMES[scope], scope)
self.scope_filter.currentIndexChanged.connect(self._load_changes)
toolbar.addWidget(QLabel("范围:"))
toolbar.addWidget(self.scope_filter)

# 原有: 状态筛选 + 搜索框 (保持不变)
```

**修改 `_load_changes()` 以支持新筛选器**:

在现有逻辑后增加客户端过滤:
```python
# 应用领域筛选
domain_filter = self.domain_filter.currentData()
if domain_filter:
    changes = [c for c in changes if c.domain == domain_filter]

# 应用性质筛选
nature_filter = self.nature_filter.currentData()
if nature_filter:
    changes = [c for c in changes if c.nature == nature_filter]

# 应用范围筛选
scope_filter = self.scope_filter.currentData()
if scope_filter:
    changes = [c for c in changes if c.scope == scope_filter]
```

#### 3.4 重构 `NewChangeDialog`

**当前** ([L676-L756](03_主程序/01_主程序核心代码/src/ui/widgets/change_manager.py#L676-L756)):
- 字段: 标题* + 类型*(下拉6选项) + 提出人 + 描述 + 原因 + 影响

**目标**:
- 字段: 标题* + 领域*(7选1radio/group) + 性质*(5选1radio/group) + 范围*(5checkbox,默认LOCAL) + 原因(textarea) + 变更前(textarea) + 变更后(textarea) + 关联变更(可选autocomplete) + 提出人

**UI布局草图**:
```
┌─────────────────────────────────────┐
│  新建变更单 (V2.1.0)                │
├─────────────────────────────────────┤
│  标题*: [____________________]     │
│                                      │
│  技术领域 (WHO)*:                   │
│  ○ ELEC电气设计 ○ MECH机械结构      │
│  ● PLC程序(默认) ○ HMI程序          │
│  ○ Python脚本 ○ 工程文档           │
│  ○ 安全功能                         │
│                                      │
│  业务性质 (WHY)*:                   │
│  ○ 需求变更 ● 优化改进(默认)        │
│  ○ 缺陷修复 ○ 配置调整             │
│  ○ 紧急变更                         │
│                                      │
│  影响范围 (WHERE)*:                 │
│  ☑ 局部(默认) ☐ 模块级              │
│  ☐ 系统级⚠️ ☐ 跨系统 ☐ 安全相关    │
│  [当选择系统级/跨系统/安全时显示:]  │
│  ⚠️ 此变更需要[Tech Director]复审   │
│  ─────────────────────────          │
│  传播链编辑区 (可选):               │
│  [...textarea...]                  │
│                                      │
│  变更原因:                          │
│  [...textarea...]                  │
│                                      │
│  变更前 (Before):                   │
│  [...textarea...]                  │
│                                      │
│  变更后 (After):                    │
│  [...textarea...]                  │
│                                      │
│  关联变更单 (可选):                 │
│  [搜索已有变更...      ] [添加]    │
│  [CHG-PLC-2026-001] [×]            │
│                                      │
│  提出人: [________]  附件: [...]   │
│                                      │
│       [确定]          [取消]        │
└─────────────────────────────────────┘
```

**关键交互逻辑**:
1. 当用户选择 **SYSTEM/CROSS/SAFE** 范围时:
   - 自动弹出提示框: `"此变更为{范围名}级，按V2.1.0规范必须由{审批层级}复审后方可实施。是否继续？"`
   - 显示传播链编辑区域(默认隐藏)
   - 自动调用 `suggest_related_domains()` 并显示建议列表

2. 当用户点击"确定"时:
   - 收集所有字段值
   - 如果选择了多个范围，取最高级别(优先级: SAFE > CROSS > SYSTEM > MODULE > LOCAL)
   - 调用 `ChangeService.create_change_v21()` (新的V2.1.0专用创建方法)

#### 3.5 新增/修改详情Tab页

**当前Tab列表** ([L145-L235](03_主程序/01_主程序核心代码/src/ui/widgets/change_manager.py#L145-L235)):
1. 变更详情 (detail_tab)
2. 流程操作 (flow_tab)
3. 影响分析 (impact_tab)
4. 审批历史 (approval_tab)
5. 变更台帐 (ledger_tab)

**目标Tab列表** (调整为):
1. **变更详情** (保持，但内容需更新为V2.1.0字段)
2. **流程操作** (保持不变)
3. **影响分析** (重构: 从纯文本改为结构化显示)
   - 显示 §6.2 技术领域影响checklist (7行表格)
   - 显示 §6.3 传播链可视化 (ASCII图渲染)
4. **审批历史** (保持不变)
5. **关联变更** (**新增Tab** - 替代原"变更台帐"位置或插入新位置)
   - 显示 `related_changes` 列表
   - 每行可点击跳转到对应变更单详情
   - 显示传播方向箭头 (→ 受影响 ← 被影响)
6. **变更台帐** (保持不变，但路径需同步更新)

#### 3.6 修改详情显示逻辑

**当前** (`_show_change_detail()` [L327-L357](03_主程序/01_主程序核心代码/src/ui/widgets/change_manager.py#L327-L357)):
```python
info = f"""
<h3>{change.title}</h3>
<p><b>变更编号:</b> {change.change_id}</p>
<p><b>变更类型:</b> {change.type}</p>  # ❌ V1.x字段
<p><b>当前状态:</b> ...</p>
...
<p><b>影响范围:</b> {change.impact}</p>  # ❌ V1.x字段
"""
```

**目标**:
```python
# 使用V2.1.0字段
d = change.to_v2_dict() if hasattr(change, 'to_v2_dict') else {
    'domain': change.domain.value,
    'nature': change.nature.value,
    'scope': change.scope.value,
    # ... fallback
}

info = f"""
<h3>{change.title}</h3>
<p><b>变更编号:</b> {change.change_id}</p>
<p><b>技术领域:</b> {d['domain_name']} ({d['domain']})</p>
<p><b>业务性质:</b> {d['nature_name']} ({d['nature']})</p>
<p><b>影响范围:</b> {d['scope_display']}</p>
<p><b>优先级:</b> {change.priority}</p>
<p><b>审批层级:</b> {d['approval_level']}</p>
{'<p><b>⚠️ 复审人:</b> ' + d['reviewer'] + ' (必需)</p>' if change.needs_reviewer() else ''}
<p><b>当前状态:</b> <span style="color: ...">...</span></p>
<p><b>提出人:</b> {change.proposer or '-'}</p>
...
<hr>
<h4>变更前后对比</h4>
<b>变更前:</b><pre>{change.content_before or '(无)'}</pre>
<b>变更后:</b><pre>{change.content_after or '(无)'}</pre>
"""
```

#### 3.7 更新台帐相关路径

**涉及位置**:
1. `_on_view_ledger()` ([L468-L473](03_主程序/01_主程序核心代码/src/ui/widgets/change_manager.py#L468-L473))
2. `_load_ledger_content()` ([L494-L499](03_主程序/01_主程序核心代码/src/ui/widgets/change_manager.py#L494-L499))

两处均将:
```python
ledger_path = os.path.join(
    project.path,
    "05_变更管理",
    "03_变更记录",
    "版本变更台帐_CHG-V1.0.0.md"
)
```

改为:
```python
ledger_path = os.path.join(
    project.path,
    "00_项目管理",
    "04_变更管理",
    f"{project.name}_版本变更台帐.md"
)
```

---

### Step 4: 更新目录模板 (🟡 高优先级)

#### 4.1 修改 DEFAULT_TEMPLATES 中的变更管理部分

**需要修改的模板ID**:
- TPL-PLC-STD-001 (第391-396行): PLC标准版
- TPL-PLC-AUTO-001 (第511行): 自动化整线版
- TPL-PLC-HMI-001 (第568行): PLC+上位机版
- TPL-DJ-STD-001 (第624行): 单机设备标准版
- TPL-XT-STD-001 (第660-662行): 系统升级版
- TPL-WX-STD-001 (第713行): 维保项目版
- TPL-PY-WEB-001 (第778行): Python Web版
- TPL-PY-DATA-001 (第828行): Python数据分析版
- TPL-001/TPL-002/TPL-003 (第198/250/315行): Python通用版

**通用替换规则**:
```
旧: {"path": "05_变更管理", ...}
新: {"path": "04_变更管理", ...}

旧: {"path": "05_变更管理/01_变更单", ...}
新: {"path": "04_变更管理/01_变更单", ...}

旧: {"path": "05_变更管理/02_变更需求", ...}  (删除此行及后续05_变更管理/02~06子目录)
...

新增:
{"path": "04_变更管理/01_变更单/CHG-ELEC", "required": False, "description": "电气设计类变更单"},
{"path": "04_变更管理/01_变更单/CHG-MECH", "required": False, "description": "机械结构类变更单"},
{"path": "04_变更管理/01_变更单/CHG-PLC", "required": False, "description": "PLC程序类变更单"},
{"path": "04_变更管理/01_变更单/CHG-HMI", "required": False, "description": "HMI程序类变更单"},
{"path": "04_变更管理/01_变更单/CHG-SCPT", "required": False, "description": "Python脚本类变更单"},
{"path": "04_变更管理/01_变更单/CHG-DOCU", "required": False, "description": "工程文档类变更单"},
{"path": "04_变更管理/01_变更单/CHG-SAFE", "required": False, "description": "安全功能类变更单"},
```

**特殊处理 - TPL-PLC-STD-004 的模板文件**:

当前有一个模板文件:
```json
{
    "path": "05_变更管理/00_变更管理目录结构说明.md",
    "type": "document",
    "content": "# 变更管理目录结构说明\n\n## 目录说明\n### 01_变更单\n..."
}
```

需要:
1. 路径改为: `04_变更管理/00_变更管理README.md`
2. 内容完全重写为符合043 V2.1.0规范的精简版README (参考DJ-2026-014项目的README.md)

---

## 三、执行顺序与依赖关系

```
Step 1 (P2-d/e/f/g) ──→ Step 2 (P3-a/b) ──┬──→ Step 3 (P4-a~g)
                                           │
                                           └──→ Step 4 (P5-a)
```

**推荐执行顺序**:
1. ✅ **Step 1.1** - 重写`_generate_ledger_content()` (最核心，阻塞后续)
2. ✅ **Step 1.2** - 更新`generate_ledger()`路径 (与1.1紧密耦合)
3. ✅ **Step 1.3** - 扩展`get_statistics()` (独立，可并行)
4. ✅ **Step 1.4** - 新增辅助方法 (独立，可并行)
5. ⏳ **Step 2.1+2.2** - DAO层升级 (依赖Step 1.3的接口定义)
6. ⏳ **Step 3.1~3.7** - UI层升级 (依赖Step 1+2全部完成)
7. ⏳ **Step 4.1** - 目录模板更新 (完全独立，可随时进行)

**预计工作量**:
- Step 1: ~200行代码修改 (主要是`_generate_ledger_content()`重写)
- Step 2: ~100行新增代码
- Step 3: ~400行代码修改 (UI改动最大)
- Step 4: ~50行×9模板 = ~450行修改

---

## 四、验证标准

### 4.1 单元验证 (每个Step完成后立即验证)

**Step 1 验证**:
```bash
# 测试1: 创建一个V2.1.0变更单并导出
python -c "
from src.services.change_service import ChangeService
# 创建含domain/nature/scope字段的变更
change, err = ChangeService.create_change_v21(...)
assert err == '', f'创建失败: {err}'
# 导出并检查输出路径
path, err = ChangeService.export_change(change.change_id)
assert '04_变更管理/01_变更单/CHG-PLC/' in path, f'路径错误: {path}'
print('✅ export_change测试通过')
"

# 测试2: 生成台帐并检查格式
python -c "
from src.services.change_service import ChangeService
path, err = ChangeService.generate_ledger(project_id)
assert '04_变更管理' in path and '_版本变更台帐.md' in path
with open(path) as f:
    content = f.read()
    assert '[→ CHG-' in content, '缺少超链接格式'
    assert '## 3. 多维统计' in content or '## 3.' in content, '缺少4D统计'
print('✅ generate_ledger测试通过')
"

# 测试3: 统计接口返回4D数据
stats = ChangeService.get_statistics(project_id)
assert 'domain_PLC' in stats, '缺少domain维度'
assert 'nature_OPT' in stats, '缺少nature维度'
assert 'scope_LOCAL' in stats, '缺少scope维度'
print('✅ get_statistics 4D测试通过')
```

**Step 2 验证**:
```bash
# 测试DAO新方法
from src.dao.change_dao import ChangeDAO
from src.core.constants import Domain, Nature, Scope

changes = ChangeDAO.list_by_domain(project_id, Domain.PLC)
assert all(c.domain == Domain.PLC for c in changes)

changes = ChangeDAO.list_by_nature(project_id, Nature.DEF)
assert all(c.nature == Nature.DEF for c in changes)

chain = ChangeDAO.find_propagation_chain('CHG-PLC-2026-001')
print('✅ DAO新方法测试通过')
```

**Step 3 验证** (需GUI环境):
- 启动工具 → 进入变更管理模块
- 验证表格显示9列 (序号/链接/领域/性质/范围/标题/优先级/状态/日期)
- 验证3个新筛选器 (领域/性质/范围) 可正常过滤
- 点击"新建变更" → 验证新表单包含领域/性质/范围选择器
- 选择SYSTEM范围 → 验证弹出⚠️提示并显示传播链编辑区
- 选择某变更单 → 验证详情显示V2.1.0字段 (domain/nature/scope)
- 验证新增"关联变更"Tab页可正常显示

**Step 4 验证**:
```bash
# 用工具创建新项目 → 检查目录结构
project = ProjectService.create_project(..., template_id='TPL-PLC-STD-001')
import os
assert os.path.exists(os.path.join(project.path, '00_项目管理', '04_变更管理'))
assert os.path.exists(os.path.join(project.path, '00_项目管理', '04_变更管理', '01_变更单', 'CHG-PLC'))
assert not os.path.exists(os.path.join(project.path, '05_变更管理'))  # 旧目录不应存在
print('✅ 目录模板测试通过')
```

### 4.2 集成验证 (全部完成后)

**端到端场景**:
1. 创建项目 (使用TPL-PLC-STD-001模板) → 验证04_变更管理目录结构正确
2. 新建变更单 (选择PLC/DEF/SYSTEM) → 验证自动提示需要Tech Director复审
3. 填写传播链 → 建议关联[HMI, DOCU, SAFE]
4. 导出变更单 → 验证文件位于`04_变更管理/01_变更单/CHG-PLC/`且格式符合040 V2.0.0
5. 再创建2个变更 (ELEC/CFG/MODULE, HMI/OPT/LOCAL)
6. 生成台帐 → 验证:
   - 文件位于`04_变更管理/{项目}_版本变更台帐.md`
   - §3包含4D统计表格 (3个变更分布在ELEC/PLC/HMI领域)
   - §4包含3行记录，每行有`[→ CHG-xxx](./01_变更单/...)`超链接
   - §5显示传播链矩阵 (PLC SYSTEM变更 → 影响HMI变更)
7. 在UI中查看台帐 → 验证超链接可点击跳转

---

## 五、向后兼容性保障

### 5.1 数据库兼容
- 旧字段 `type`, `impact` 保留为nullable，不强制迁移历史数据
- 新字段 `domain`, `nature`, `scope` 有default值，旧记录导入时自动填充默认值(PLC/OPT/LOCAL)
- 提供 `Change.migrate_from_v1()` 静态方法供手动迁移脚本调用

### 5.2 API兼容
- `ChangeService.create_change()` 保持原签名不变 (内部自动将type映射为domain+nature)
- 新增 `create_change_v21()` 方法接受V2.1.0参数
- `export_change()` 和 `generate_ledger()` 无version参数，始终输出V2.1.0格式 (如需V1.0格式可后续添加参数)

### 5.3 UI兼容
- 表格列数从6→9，但前3列(序号/编号/标题)概念保留
- 旧变更单(仅有type字段)在表格中显示:
  - 领域列: 尝试从type映射，失败则显示"-"
  - 性质列: 显示"-"
  - 范围列: 显示"-(未分类)"

---

## 六、风险评估与应对

| 风险 | 概率 | 影响 | 应对措施 |
|:----:|:----:|:----:|---------|
| 数据库迁移失败 (旧数据库无domain列) | 低 | 🔴 高 | Alembic auto-migration; 启动时检测并自动ALTER TABLE ADD COLUMN |
| UI重构导致回归缺陷 | 中 | 🟡 中 | 保留旧`NewChangeDialog`为`NewChangeDialogV1`备份; A/B测试 |
| 台帐格式变化导致用户困惑 | 低 | 🟡 低 | 在台帐头部添加"V2.1.0格式说明"; 保留V1.0格式导出选项(预留) |
| 性能下降 (4D统计查询次数增多) | 低 | 🟡 低 | 使用SQL GROUP BY一次性计算4D; 结果缓存5分钟 |

---

## 七、下一步行动

**立即可执行** (本计划批准后):
1. 开始 **Step 1.1** - 重写`_generate_ledger_content()`方法 (~1.5小时)
2. 同时启动 **Step 1.3+1.4** (独立任务，可并行) (~30分钟)
3. 完成后立即 **Step 1.2** (与1.1联动) (~10分钟)
4. 进入 **Step 2** DAO层升级 (~1小时)
5. 进入 **Step 3** UI层升级 (最大任务，~3-4小时)
6. 最后 **Step 4** 目录模板更新 (~1小时)

**总预计时间**: 7-9小时 (不含测试调试)

---

**文档版本**: V1.0.0
**编制人**: AI Assistant
**编制日期**: 2026-04-12
**状态**: 待用户确认后执行
