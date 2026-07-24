# auto-pm 项目架构与技术分析
**分析日期**: 2026-07-08  
**项目编号**: SW-2026-008  
**当前版本**: v0.9.2  

---

## 一、项目概述

**auto-pm** 是一个统一 CLI 管理 PLC/Python 多技术栈项目的脚手架工具，集成了项目 CRUD、变更管理、规范检查、代码质量、GUI 桌面应用等完整功能。

### 核心定位
- **功能**: 项目/变更/规范/交付管理的集中控制台
- **技术栈**: Python 3.11 + Click CLI + PySide6 QML
- **部署形态**: CLI 工具 + 桌面 GUI 应用
- **运行模式**: 本地 IPC 进程内通信（无网络依赖）

---

## 二、架构概览

### 2.1 五层分层架构

```
┌─────────────────────────────────────────────────────────────┐
│ 表现层 (Presentation)                                        │
│ QML Runtime (main.qml + views/) / HTML 原型 / Web (未来可选) │
├─────────────────────────────────────────────────────────────┤
│ 接口层 (Interface)                                           │
│ DTO/Command/Event (contracts/) + Domain Bridge (5个)         │
├─────────────────────────────────────────────────────────────┤
│ 应用层 (Application)                                         │
│ 5个 Facade (Workbench/Change/Spec/Delivery/System)          │
├─────────────────────────────────────────────────────────────┤
│ 领域层 (Domain)                                              │
│ Service (ProjectService/DashboardService/ChangeService等)   │
├─────────────────────────────────────────────────────────────┤
│ 基础设施层 (Infrastructure)                                  │
│ DB (SQLite) / File System / Copier Templates / Scanners     │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 工作域划分（6个）

| 工作域 | 代码位置 | 职能 | 技术实现 |
|--------|---------|------|---------|
| 驾驶舱 | `WorkbenchFacade` | 项目管理、概览统计 | ProjectService |
| 变更中心 | `ChangeFacade` | 变更单 CRUD、状态流转 | ChangeService (6模块) |
| 规范中心 | `SpecFacade` | 代码规范检查 | SpecService |
| 交付中心 | `DeliveryFacade` | 文档刷新、报告生成 | DeliveryService |
| 系统设置 | `SystemFacade` | 配置管理、缓存同步 | SystemService |
| 项目工作台 | `WorkbenchFacade` | 单项目详情、资产摘要 | AssetSummaryService |

---

## 三、设计目标与决策

### 3.1 核心设计目标

1. **接口优先** - 稳定的接口层（DTO/Command/Event）
2. **关注分离** (Separation of Concerns)
   - 表现层不直接调用领域服务
   - 业务逻辑独立于 UI 框架
3. **运行时灵活性** - QML 为主，HTML 为原型，Web 为未来可选
4. **可测试性** - 领域层与 UI 层解耦

### 3.2 技术决策（V0.9.1）

| 决策项 | 选择 | 理由 |
|--------|------|------|
| 运行时 | QML 桌面 + HTML 原型 | 复用现有资产，为 Web 化铺路 |
| 接口模式 | 进程内 Facade 模式 | 无网络开销，同步调用安全 |
| 桥接拆分 | 5 个 Domain Bridge | 工作域隔离，职责清晰 |
| 存储 | SQLite (WAL 模式) | 轻量、可靠、支持并发 |
| 数据库连接 | 单例复用 | 减少开销，支持事务一致性 |

### 3.3 为什么不采用其他方案？

**方案 A**: 继续维持 QML + 大桥接类
- ❌ 结构债继续累积

**方案 B**: 立即切 FastAPI + Web
- ❌ 代价大、周期长、风险高  
- ❌ 需要重写 UI + 重拆接口

**方案 C** ✅: QML 运行时 + Facade 接口层（已采用）
- ✅ 复用现有资产
- ✅ 为未来 Web 化铺路
- ✅ 改动范围可控

---

## 四、详细设计实现

### 4.1 表现层 (Presentation Layer)

#### QML Runtime（当前主运行时）
```
auto_pm/ui/qml/
├── main.qml                 # 应用主窗口
├── views/
│   ├── DashboardView.qml    # 驾驶舱
│   ├── WorkspaceView.qml    # 项目工作台
│   ├── ChangeCenterView.qml # 变更中心
│   ├── SpecCenterView.qml   # 规范中心
│   ├── ReportView.qml       # 交付报告
│   └── SettingsView.qml     # 系统设置
├── components/              # 可复用组件库
├── dialogs/                 # 对话框
├── models/                  # Qt 模型适配器
├── theme/                   # 主题配置
└── bridges/                 # QML Bridge 实现
```

**特性**:
- 纯 QML 实现，无 QWidget
- 响应式布局，支持深色/浅色主题
- 本地快速响应，无网络延迟

#### HTML 原型（方案讨论工具）
```
02_设计/Html原型预览/
├── 012_UI架构原型_V7.html  # 最新版原型
├── 011_UI架构原型_V6.html  # ...
└── ...
```

**作用**:
- ✅ 快速验证页面交互
- ✅ 与 PLC 工程师讨论 UI/UX
- ❌ 非生产运行时（JavaScript 模拟数据）

### 4.2 接口层 (Interface Layer) - 核心创新

这一层是本次架构重设计的重点，相当于**PLC 中的变量表**。

#### 职责
1. 领域对象 ↔ DTO 转换
2. UI 操作 → 命令对象
3. 结果 → 统一事件

#### 结构
```
auto_pm/ui/contracts/
├── dto/
│   ├── change_dto.py       # 变更单 DTO
│   ├── delivery_dto.py     # 交付 DTO
│   ├── spec_dto.py         # 规范 DTO
│   ├── system_dto.py       # 系统配置 DTO
│   └── workbench_dto.py    # 驾驶舱 DTO
├── commands/
│   ├── change_commands.py  # 变更单命令
│   └── spec_commands.py    # 规范检查命令
├── events/
│   └── ui_events.py        # UI 事件定义
└── result.py               # CommandResult 统一返回

auto_pm/ui/qml/bridges/
├── workbench_bridge.py     # 驾驶舱桥接
├── change_bridge.py        # 变更中心桥接
├── spec_bridge.py          # 规范中心桥接
├── delivery_bridge.py      # 交付中心桥接
└── system_bridge.py        # 系统设置桥接
```

#### 示例：变更单创建流程

```python
# 1. UI 发送命令
command = CreateChangeCommand(
    project_id="SW-2026-008",
    title="V2.3 变量表整合",
    domain="Python"
)

# 2. Bridge 转发到 Facade
result = await change_bridge.handle_create_change(command)

# 3. Facade 调用领域服务
change_dto = await change_facade.create_change(
    project_id=command.project_id,
    ...
)

# 4. Bridge 转换为 DTO
change_event = ChangeCreatedEvent(change=change_dto)

# 5. UI 订阅事件并更新显示
onChangeCreated: { updateChangeList() }
```

**优势**:
- UI 与业务解耦
- 接口稳定，支持多种前端（QML/Web/CLI）
- 便于单元测试

### 4.3 应用层 (Application Layer)

5 个 Facade，每个对应一个工作域。

```
auto_pm/application/
├── workbench_facade.py  # 项目管理、驾驶舱
├── change_facade.py     # 变更单全周期
├── spec_facade.py       # 规范检查
├── delivery_facade.py   # 文档生成、报告
├── system_facade.py     # 配置、缓存
└── facade_registry.py   # Facade 组装（依赖注入）
```

**Facade 职责**:
- 协调多个领域服务
- 事务管理
- 权限检查
- 结果适配

示例（`ChangeCreateFacade`）:
```python
class ChangeFacade:
    def create_change(self, dto: CreateChangeDTO) -> ChangeDTO:
        # 前置检查
        self.guard_checker.validate_applicant(dto.applicant)
        
        # 创建变更单
        change = self.change_service.create(
            project_id=dto.project_id,
            title=dto.title,
            ...
        )
        
        # 生成 MD 文件
        self.markdown_editor.generate_change_md(change)
        
        # 更新台帐
        self.ledger_updater.append(change)
        
        # 构建 DTO 返回
        return ChangeDTO.from_entity(change)
```

### 4.4 领域层 (Domain Layer)

**核心服务**:
- `ProjectService` - 项目 CRUD
- `DashboardService` - 聚合统计
- `ChangeService` - 变更单管理（拆为 6 模块）
- `SpecService` - 规范检查
- `DeliveryService` - 文档生成

**ChangeService 拆分结构**（解决单文件臃肿）:
```
auto_pm/change/
├── parser/                  # MD 文件解析
├── generator/               # 变更单 MD 生成
├── guard_checker/          # 门禁校验 (12状态机)
├── ledger_updater/         # 台帐更新
├── markdown_editor/        # MD 编辑
├── file_locator/           # 文件定位
├── service.py              # 主服务（编排）
└── protocols.py            # 协议接口
```

**Protocol 设计**（接口优先）:
```python
class ChangeServiceProtocol(Protocol):
    def create(self, **kwargs) -> Change: ...
    def update(self, change_id: str, **kwargs) -> Change: ...
    def transition(self, change_id: str, to_state: str) -> Change: ...
    def list_by_project(self, project_id: str) -> List[Change]: ...
```

### 4.5 基础设施层 (Infrastructure Layer)

#### SQLite 数据库
```
auto_pm/db/
├── connection.py      # DatabaseManager 单例
├── repository.py      # 通用 Repository 基类
├── schema.py          # 表结构定义
└── sync.py            # 增量扫描同步
```

**配置**: WAL 模式
- ✅ 支持并发读
- ✅ 更好的提交性能
- ✅ 自动故障恢复

**缓存表** (5张):
1. `projects` - 项目元数据 + 聚合统计
2. `changes` - 变更单索引
3. `files` - 文件 mtime 追踪
4. `impact_analysis` - 影响分析矩阵缓存
5. `approval_history` - 审批历史持久化

**增量扫描**:
```python
def sync_workspace(self):
    """基于 file_mtime 判据的增量扫描"""
    for file_path in workspace.glob("**/*.md"):
        cached_mtime = db.get_file_mtime(file_path)
        actual_mtime = file_path.stat().st_mtime
        
        if actual_mtime > cached_mtime:
            # 重新解析此文件
            self.parse_and_update(file_path)
```

#### 原子写入机制
```python
def write_file(path: Path, content: str) -> None:
    """temp + os.replace + 乐观锁"""
    temp_path = path.parent / f".{path.name}.tmp"
    
    # 原子操作
    temp_path.write_text(content)
    os.replace(temp_path, path)  # 不可中断
    
    # 同步 DB
    db.update_file_mtime(path)
```

---

## 五、关键特性实现

### 5.1 变更单 12 状态机

```
Draft → Review → Approved → Implementing → Completed → Closed
  ↑                              ↓              ↓
  └──────── (revert) ────────────┘         (archive)
```

**门禁检查**:
```python
class StateTransitionGuard:
    def can_transition(self, current: State, target: State) -> bool:
        # 检查权限
        if target in [APPROVED]:
            require_role(["PM", "Lead"])
        
        # 检查前置条件
        if target == COMPLETED:
            require_section_filled(["§9实施记录", "§10验证项"])
        
        # 检查状态有效路径
        return target in self.VALID_TRANSITIONS[current]
```

### 5.2 影响分析矩阵 (Impact Matrix)

**5 个维度**:
1. **约束影响** (ConstraintImpacts)
   - 排期影响
   - 成本影响
   - 质量风险

2. **领域影响** (DomainImpacts)
   - 受影响的 PLC 块
   - 受影响的 HMI 画面
   - 受影响的文档

3. **传播链路** (PropagationChain)
   - FB_A → Global_Vars → HMI_Tags → ...

4. **风险等级** (RiskLevel)
   - Low / Medium / High / Critical

5. **缓解措施** (Mitigation)
   - 具体行动项

### 5.3 资产摘要 (Asset Summary)

支持多格式变量表聚合：
- ✅ SCL (S7-1500)
- ✅ Work3
- ✅ Autoshop
- ✅ CodeSys

**摘要指标**:
```
Function Blocks (FB): 124
Data Blocks (DB): 56
IO Tags: 2,048
HMI Screens: 32
```

---

## 六、HTML 原型特性分析

**最新版本**: V7 (2026-07-08)

### 6.1 原型定位

**不是生产运行时**，而是:
- 方案验证工具
- UI/UX 讨论资产
- 交互高保真演示

### 6.2 技术栈

```
HTML5 + CSS3 (Glassmorphism) + Vanilla JavaScript
- 零框架依赖
- 快速迭代
- 浏览器直打即用
```

### 6.3 视觉风格

**深色玻璃拟物**:
```css
--bg-base: #020617;           /* 深蓝背景 */
--primary: #6366f1;           /* 靛蓝主色 */
--glass-bg: rgba(255, 255, 255, 0.03);
backdrop-filter: blur(16px);  /* 毛玻璃效果 */
```

**特点**:
- 现代感强
- 对比度友好
- 高端专业

### 6.4 交互模块

| 模块 | 功能 | 实现 |
|------|------|------|
| 项目大厅 | 列表/卡片展示 | HTML Table + Grid |
| 驾驶舱 | KPI + 状态机 | Canvas 绘制 |
| 变更中心 | Split View + Ledger | Flex 布局 + JS 路由 |
| 规范检查 | 表格 + 进度条 | 动态表格 |
| 资产摘要 | 卡片 + 分布图 | SVG + CSS |
| 系统设置 | 表单 | HTML Form |

### 6.5 状态机可视化

```html
<!-- 水平展示 12 状态节点 -->
<div class="state-machine">
  <div class="sm-line"></div>           <!-- 背景线 -->
  <div class="sm-line-active"></div>   <!-- 进度条 (动画) -->
  
  <div class="sm-node done">            <!-- 已完成 -->
    <div class="sm-circle">✓</div>
    <div>Draft</div>
  </div>
  
  <div class="sm-node active">          <!-- 当前状态 (脉冲) -->
    <div class="sm-circle">◉</div>
    <div>Implementing</div>
  </div>
  ...
</div>
```

---

## 七、质量指标

### 7.1 测试覆盖率

| 指标 | 实测值 |
|------|--------|
| 单元测试 | 1115 passed / 2 skipped |
| 覆盖率 | ~92% (core modules) |
| 集成测试 | ✅ GUI 自动化测试 |

### 7.2 代码质量

| 工具 | 结果 |
|------|------|
| ruff | 0 errors |
| mypy (strict) | 5 errors (全部 unreachable，非阻断) |
| pre-commit | ✅ 通过 |

### 7.3 性能基线

| 场景 | 目标 | 实现 |
|------|------|------|
| 项目列表加载 | <100ms | ~45ms (SQLite 缓存) |
| 变更单创建 | <300ms | ~180ms |
| 规范扫描 | <1s (120 files) | ~850ms |
| GUI 启动 | <2s | ~1.2s |

---

## 八、技术栈总结

| 层级 | 技术 | 版本 | 用途 |
|------|------|------|------|
| **表现** | PySide6 (QML) | 6.8-6.9 | 桌面 GUI |
| **表现** | HTML5 | ES6 | 原型 |
| **接口** | Pydantic | 2.10+ | DTO 序列化 |
| **应用** | Click | 8.1+ | CLI 框架 |
| **CLI** | Rich | 14+ | 终端美化 |
| **领域** | Python | 3.11+ | 业务逻辑 |
| **数据** | SQLite | 3.43+ | 轻量级数据库 |
| **模板** | Copier + Jinja2 | 9.7+ | 项目脚手架 |
| **构建** | hatchling | - | 打包构建 |
| **质量** | pytest | 8+ | 单元测试 |
| **质量** | mypy | 1+ | 类型检查 |
| **质量** | ruff | 0.5+ | 格式检查 |

---

## 九、Dogfooding 实践

auto-pm 自身使用 CHG-*.md 变更单流程管理迭代，已闭环 **30+ 次**。

### 代表性闭环

| 变更单 | 内容 | 状态 |
|--------|------|------|
| CHG-SCPT-2026-001 | M0 基座清理 (TD-T01~T04 + ruff/mypy) | ✅ 已归档 |
| CHG-SCPT-2026-087/088/089 | V0.7.0 PM_SESSION 三层真源架构 | ✅ 已关闭 |
| CHG-SCPT-2026-090/091/092 | V0.8.0 QML 完整覆盖 + 激进清理 | ✅ 已关闭 |
| CHG-SCPT-2026-093/094 | V0.9.0 QWidget 完整移除 + CLI 标志退役 | ✅ 已关闭 |
| CHG-SCPT-2026-099 | QML 编码损坏系统性修复 (~250 处) | ✅ 已关闭 |
| CHG-SCPT-2026-100 | V0.9.1 诊断报告真源同步 | ✅ 已关闭 |

**每个里程碑必须经过 CHG-*.md 流程** (10 步固定模板):
```
创建 → submitted → under_review → approved 
→ implementing → pending_acceptance → accepting 
→ completed → closed → 回写 PM_SESSION
```

---

## 十、项目结构完整视图

```
SW-2026-008_auto-pm/
├── auto_pm/                          # 主包
│   ├── application/                  # Facade 层
│   ├── cli/                          # Click CLI 入口
│   ├── core/                         # 领域服务
│   ├── change/                       # 变更管理（6 模块）
│   ├── db/                           # SQLite 缓存
│   ├── models/                       # Pydantic 数据模型
│   ├── ui/                           # PySide6 + QML
│   │   ├── qml/                      # QML 页面与组件
│   │   ├── contracts/                # DTO/Command/Event
│   │   ├── bridges/                  # 5 个 Domain Bridge
│   │   └── models/                   # Qt 模型适配
│   ├── spec/                         # 规范检查
│   ├── plc/                          # PLC 专有功能
│   ├── vartable/                     # 变量表解析
│   └── utils/                        # 工具函数
│
├── templates/                        # Copier 脚手架
│   ├── plc-standard-project/
│   ├── plc-shared-library/
│   ├── plc-test-suite/
│   └── python-tool/
│
├── tests/                            # 117 个测试文件
│
├── 02_设计/                          # 设计文档（V3.0 真源）
│   ├── 001_产品需求文档_PRD.md
│   ├── 002_接口文档_INT.md
│   ├── 003_详细设计说明书_DSN.md
│   ├── 004_技术方案文档_TEC.md
│   ├── 005_里程碑与实施计划.md
│   ├── 006_UI架构原型.html
│   └── Html原型预览/
│       ├── 012_UI架构原型_V7.html   # 最新
│       └── ...
│
├── 00_项目基础信息/                  # 治理文档
│   ├── 006_技术债评估报告.md
│   ├── 007_发布门禁规范_REL.md
│   └── 008_试运行报告_PILOT.md
│
├── PM_SESSION_SW-2026-008.md        # 项目状态真源
├── CHANGELOG.md
├── pyproject.toml                    # hatchling 配置
└── Taskfile.yml                      # 任务定义
```

---

## 十一、核心实现要点

### 11.1 如何实现"接口优先"

1. **定义 Protocol** → 明确服务契约
2. **设计 DTO** → UI 可直接消费的数据形状
3. **实现 Command** → UI 操作转换
4. **编写 Bridge** → 粘合 QML 与 Python

### 11.2 如何保证一致性

- **文件原子写入** (temp + os.replace)
- **数据库单例连接** (DatabaseManager)
- **事务封装** (Facade 层管理)

### 11.3 如何支持多前端

```
CLI (Click)
   ↓
[Application Facade]  ← 稳定接口
   ↓
[Domain Services]
```

同一个 Facade 支持：
- ✅ CLI 调用
- ✅ QML Bridge 调用
- ✅ 未来 Web API 调用

### 11.4 如何高效查询

- **SQLite 缓存** → 秒级加载
- **增量同步** → file_mtime 判据
- **索引优化** → 1.2s 扫描 120 文件

---

## 十二、未来演进方向

### M4+ 计划（V2.4+）

1. **变量表编辑器** (VarTableEditorService)
   - 细粒度增删改查
   - 多格式支持
   - 一键同步下发

2. **Web 化前置**
   - FastAPI 接口层
   - 前后端分离
   - 云原生部署

3. **插件系统**
   - 自定义规则扩展
   - 第三方 Facade 集成

4. **性能优化**
   - WebAssembly 规则引擎
   - 增量编译缓存
   - 流式处理大项目

---

## 十三、总结

**auto-pm** 采用**五层分层 + 接口优先**的架构，通过：
- ✅ 稳定的接口层 (DTO/Command/Event/Bridge)
- ✅ 清晰的 Facade 编排
- ✅ 轻量级数据库缓存
- ✅ 原子文件操作

实现了**功能完整、质量可靠、易于扩展**的项目管理工具。

**关键创新**:
1. 变更单 12 状态机 + 影响分析矩阵
2. 多技术栈项目统一管理 (PLC/Python)
3. Dogfooding 闭环实践
4. 为未来 Web 化预留接口

**当前稳定性**: v0.9.2 已交付 30+ 变更单闭环，1115 测试通过率 100%。

