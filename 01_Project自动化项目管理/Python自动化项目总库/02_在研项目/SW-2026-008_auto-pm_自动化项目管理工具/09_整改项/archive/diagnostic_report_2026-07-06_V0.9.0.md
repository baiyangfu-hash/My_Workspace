# auto-pm 项目全面诊断报告

> **项目**: SW-2026-008 auto-pm 自动化项目管理工具
> **诊断日期**: 2026-07-06
> **当前版本**: V0.9.0
> **代码规模**: 源码 117 文件 / ~877KB，测试 111 文件 / ~900KB
> **诊断角度**: 架构师 × 资深程序员 × 主要使用者（电气工程师/兼任 PM）

---

## 一、诊断总评

| 维度 | 评分 | 判断依据 |
|------|------|----------|
| 架构设计 | ★★★★☆ | V3.0 五层架构方向正确，Facade 已落地，但新旧并存过渡期有冗余 |
| 代码质量 | ★★★★☆ | ruff 0 errors、mypy strict、Pydantic v2 模型层清晰，少量设计味道问题 |
| 测试体系 | ★★★★☆ | 1714+ 测试全绿，coverage 有体系，但 Facade 层测试过度依赖 MagicMock |
| 文档体系 | ★★★☆☆ | 文档量大且认真，但存在**显著的双源/过时/矛盾问题** |
| 用户体验 | ★★★☆☆ | CLI 功能完整，GUI 已可跑，但使用者上手路径不清晰 |
| 可维护性 | ★★★★☆ | Protocol 接口、类型标注、分层清晰，但模块间依赖仍有暗耦合 |

---

## 二、架构师视角

### 2.1 ✅ 做得好的

#### 五层架构方向清晰

[DSN](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/02_设计/003_详细设计说明书_DSN.md) 定义的 `表现层 → 接口层 → 应用层 → 领域层 → 基础设施层` 在代码中已初步落地：

- 5 个 Facade（[workbench_facade.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/application/workbench_facade.py)、[change_facade.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/application/change_facade.py)、[spec_facade.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/application/spec_facade.py)、[delivery_facade.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/application/delivery_facade.py)、[system_facade.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/application/system_facade.py)）已创建并接入
- [FacadeRegistry](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/ui/registry.py) 做了手工 DI 装配
- [contracts/](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/ui/contracts) 目录有 DTO、Command、Result 分离

#### Protocol 接口定义规范

[protocols.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/core/protocols.py) 使用 `@runtime_checkable Protocol` 定义了 `ProjectServiceProtocol`、`ChangeServiceProtocol`、`PlcServiceProtocol`，实现了依赖倒置。

#### DB 层设计合理

- WAL 模式、外键开启、幂等 schema 初始化
- [migrate_schema](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/db/schema.py#L151-L163) 处理了版本迁移
- PEP 562 延迟导入解决了 [SyncService 循环依赖](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/db/__init__.py#L24-L34)

### 2.2 ⚠️ 需要关注的架构问题

#### 问题 A1：QmlBridge 仍是 933 行的"上帝类"

**证据**: [qml_bridge.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/ui/qml/qml_bridge.py) = 933 行 / 38KB

DSN §5.1 明确指出 QmlBridge 承担过多职责需要拆分，已定义了 5 个 Domain Bridge 的目标结构，但**代码中 QmlBridge 仍然完整存在且仍是 QML 的实际入口**。虽然它的构造函数已经改为接收 Facade，但本质上只是把"直接持有 Service"换成了"直接持有 Facade"，QmlBridge 自身并没有被拆分成 WorkbenchBridge/ChangeBridge/SpecBridge/DeliveryBridge/SystemBridge。

**风险**: 新旧架构**语义重叠**——Facade 做了一层聚合，QmlBridge 又在做一层几乎相同的聚合（加上 Qt Signal/Slot 包装），造成数据流链路变成 `QML → QmlBridge → Facade → Service`，Facade 和 Bridge 的边界模糊。

**建议**: 按 DSN §5.2 的目标，将 QmlBridge 拆成 5 个 Domain Bridge，每个 Bridge 只暴露本域的 Slot/Property/Signal。QmlBridge 保留为轻量装配入口或完全移除。

#### 问题 A2：DTO 体系双源并存

项目中存在**两套 DTO 体系**：

1. [auto_pm/models/dto.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/models/dto.py)（Pydantic BaseModel，220 行）：`ProjectCardDTO`、`DashboardSummaryDTO`、`ProjectDetailDTO` 等
2. [auto_pm/ui/contracts/dto/](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/ui/contracts/dto)（dataclass，3 个文件）：`ProjectCardDTO`、`DashboardSnapshotDTO`、`ProjectWorkspaceDTO` 等

**两个 ProjectCardDTO 同名但字段不同**：
- `models/dto.py` 的 `ProjectCardDTO` 有 `file_mtime`、`description`、`change_count`，用 Pydantic
- `contracts/dto/workbench_dto.py` 的 `ProjectCardDTO` 有 `health_status`、`open_change_count`、`last_activity_at`，用 dataclass

**同样 DashboardSummaryDTO vs DashboardSnapshotDTO**——名字不同但概念重叠。

**建议**: 统一到 `contracts/dto/` 一个位置。如果需要领域层和 UI 层不同粒度的 DTO，用清晰的命名区分（如 `DomainXxxDTO` vs `ViewXxxDTO`），避免同名冲突。

#### 问题 A3：Facade 构造函数缺乏类型约束

所有 5 个 Facade 的构造函数参数都是无类型注解的：

```python
# system_facade.py L8
def __init__(self, pm_session_service, template_service=None, project_service=None):

# workbench_facade.py L13
def __init__(self, dashboard_service, project_service, asset_summary_service):
```

这与项目 `mypy strict=true` 的配置矛盾。这些参数应当引用 [protocols.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/core/protocols.py) 中已定义的 Protocol 类型。

**建议**: 为 Facade 构造函数添加 Protocol 类型注解，或至少用 `Any` 显式标注，让 mypy 能够覆盖。

#### 问题 A4：`gui/` 目录为空，`flet_app/` 遗留

- [auto_pm/gui/](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/gui) 是空目录
- [auto_pm/flet_app/](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/flet_app) 只有 `views/` 子目录，看起来是废弃的技术探索

这些是历史遗留，应清理以避免混淆。

#### 问题 A5：CLI 和 GUI 共用 Service 但装配路径不同

CLI 通过 [AppContext](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/app_context.py) 装配，GUI 通过 [FacadeRegistry](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/ui/registry.py) 装配。两条路径创建的 Service 实例不共享，如果将来 CLI 也想用 Facade，需要第三套装配逻辑。

**建议**: 统一装配器，或让 CLI 的命令也可选地走 Facade 路径。

---

## 三、资深程序员视角

### 3.1 ✅ 做得好的

- **Pydantic v2 模型层**：类型安全、序列化便捷、ConfigDict 配置规范
- **Literal 类型取代 Enum**：[enums.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/models/enums.py) 用 `Literal` 而非 `Enum`，与 Pydantic v2 和 JSON 序列化集成更好
- **Windows 编码兼容**：[__main__.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/__main__.py#L14) 的 `PYTHONUTF8=1` 和 [cli/__main__.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/cli/__main__.py#L21-L46) 的 `_fix_windows_encoding` 非常务实
- **常量集中管理**：[constants.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/core/constants.py) + [paths.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/core/paths.py) 消除了硬编码
- **测试固件设计**：session 级 `qapp`、固定 seed 随机化、`tmp_workspace` fixture 都很规范
- **Dogfooding**：项目自身使用 CHG 流程，已完成 17 次闭环，这个实践非常有价值

### 3.2 ⚠️ 代码级问题

#### 问题 C1：Facade 层 `getattr` 防御性编程过重

[workbench_facade.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/application/workbench_facade.py) 中大量出现：

```python
stack=str(getattr(p.stack, "value", p.stack)),  # L54
phase=str(getattr(p.phase, "value", p.phase)),  # L55
```

这暗示 Facade 不确定收到的 `p.stack` 是 Literal 字符串还是 Enum。既然 [models/project.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/models/project.py#L51) 已经定义 `stack: Stack = Field("unknown")`（Stack 是 Literal），那 `getattr(p.stack, "value", p.stack)` 是不必要的。这说明**新旧模型混用**的问题还没有完全清理。

#### 问题 C2：ChangeFacade.create_change_request 遗留注释

[change_facade.py L96-97](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/application/change_facade.py#L96-L97)：

```python
impact_scope=[], # UI creation currently doesn't specify impact_scope from GUI, but let's pass a default or map it if command had it. Wait, CreateChangeCommand does not have impact_scope. 
# Let me check if impact_scope is required.
```

这是开发过程中的思考过程注释，不应该残留在交付代码中。并且 `impact_scope` 硬编码为空列表是一个功能缺口——GUI 创建变更单时无法指定影响范围。

#### 问题 C3：SystemFacade 中存在内联 `import`

[system_facade.py L66-67](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/application/system_facade.py#L66-L67)：

```python
from pathlib import Path
import yaml
```

在方法内部导入标准库和第三方库，虽然不是错误，但违反了项目其他地方的约定（文件顶部导入）。

#### 问题 C4：WorkbenchFacade.get_settings_summary 直接访问 Service 内部

[workbench_facade.py L107-116](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/application/workbench_facade.py#L107-L116)：

```python
db = getattr(self._project_service, "db", None)
repo = getattr(self._project_service, "_repo", None)
```

Facade 直接用 `getattr` 探查 Service 的私有属性 `_repo`，这违反了 Facade "只调用 Service 公开方法" 的设计原则（DSN §3.3）。

#### 问题 C5：`CommandResult` 和 `QueryResult` 几乎完全相同

[result.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/ui/contracts/result.py) 中两个类的字段一模一样（`success, message, payload, errors`）。CQRS 分离的初衷是好的，但如果两者的结构完全相同，维护者会困惑"为什么有两个一样的类"。建议至少在 docstring 中更明确各自的使用场景，或者考虑合并为一个 `Result[T]`。

### 3.3 测试体系分析

#### 优点
- 测试/源码比接近 1:1（111 文件 vs 117 文件）
- 分层测试标记（`gui`、`cli`、`smoke`、`unit`、`integration`、`slow`）
- 覆盖率有体系化配置

#### 问题 T1：Facade 测试全部使用 MagicMock

[test_spec_facade.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/tests/application/test_spec_facade.py)、[test_system_facade.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/tests/application/test_system_facade.py)、[test_delivery_facade.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/tests/application/test_delivery_facade.py) 全部使用 `MagicMock`，测试只验证了"Facade 调用了 Service 方法"，但没有验证：

- DTO 转换的正确性（mock 跳过了真实对象的结构）
- 异常路径的完整性（只测了通用 Exception，没有测领域异常）
- 跨 Facade 的集成路径

**建议**: 至少补一层 Fake Service 或 In-Memory Service 的集成测试，验证真实数据流通。

---

## 四、主要使用者视角（电气工程师 + 兼任 PM）

### 4.1 ✅ 做得好的

- **CLI 功能完善**：项目 CRUD、变更管理、PLC 检查、模板管理、文档管理一应俱全
- **中文友好**：所有 CLI 帮助信息、错误消息、文档都是中文
- **Dogfooding 真实**：项目自身使用 CHG 流程管理迭代，证据可查
- **技术债零剩余**：34/34 项全部偿还，这个纪律性非常好

### 4.2 ⚠️ 使用者会遇到的问题

#### 问题 U1：README 与 02_设计文档叙述矛盾

[README.md](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/README.md) 第 242 行描述的项目结构仍然是旧架构：

```
│   ├── ui/                         # PySide6 GUI 层（8 子模块：workspace/global_pages/widgets/dialogs/models/navigation/project_list/change_center）
```

但实际代码中 `ui/` 目录已重组为 `contracts/`、`global_pages/`、`models/`、`qml/`、`registry.py` 的新结构。README 列出的 `workspace/widgets/dialogs/navigation/project_list/change_center` 等子目录**在当前代码中已不存在**。

#### 问题 U2：docs/归档索引.md 严重过时

[归档索引.md](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/docs/归档索引.md)（更新日期 2026-06-22）：

- §1.1 指向 `00_项目基础信息/001~004`，但 V3.0 设计文档已在 `02_设计/001~007`
- §1.2 指向 `02_设计/GUI原型设计-V2.0.md` 和 `GUI原型-V2.0.html`，这些文件**已不存在**，被 V3.0 版替代
- §1.4 指向 `.trae/specs/rebuild-auto-pm-v2-unified/spec.md`，这是 V2 时代的 spec，V3.0 PRD 已说明 V2.1 spec 也已废弃

这是使用者最直接的困惑源：不知道该看哪份文档。

#### 问题 U3：文档存放位置有三套体系

| 位置 | 内容 | 版本 |
|------|------|------|
| `00_项目基础信息/` | 技术债、发布门禁、试运行报告 | V0.9.0 生效 |
| `02_设计/` | PRD/INT/DSN/TEC/里程碑/原型 | V3.0.0-draft |
| README | 项目概览 + CLI 用法 + 项目结构 | 混合（部分 V0.9.0，部分已过时） |

- `00_项目基础信息/` 里原有的 PRD/INT/DSN/TEC（V2.1）还在不在？README L279-282 仍然指向它们
- `02_设计/` 里的 V3.0-draft 文档是否已经取代了 `00_项目基础信息/` 里的同名文档？

使用者无法判断哪份是"当前生效真源"。

#### 问题 U4：README 版本号与 pyproject.toml 一致但功能描述停留在旧版

README 描述了大量 GUI 功能（变更创建 QWizard、StatusMachineView、ApprovalTimeline、PropagationView），但这些描述中的组件名来自 PySide6 QWidget 时代（"QWizard"、"QDialog"、"QGraphicsView"），而当前 UI 已迁移到 QML。

#### 问题 U5：pyproject.toml 版本为 0.9.0，设计文档标 V3.0.0-draft

软件版本和设计文档版本使用不同的版本号体系（0.x.x vs Vx.x.x），两者之间的对应关系不明确。

---

## 五、文档矛盾汇总（需优先修复）

> [!CAUTION]
> 以下矛盾会导致新加入者（甚至 AI 助手）无法判断真源，是最需要优先解决的问题。

| # | 矛盾描述 | 涉及文件 |
|---|----------|----------|
| D1 | README 项目结构与实际代码不符 | README.md L225-255 |
| D2 | 归档索引指向已不存在的文件 | docs/归档索引.md |
| D3 | README 文档导航表指向 `00_项目基础信息/001~004`（V2.1），但设计文档已迁移到 `02_设计/` | README.md L277-290 |
| D4 | `00_项目基础信息/` 是否仍有 PRD/INT/DSN/TEC？如果有，与 `02_设计/` 里的哪个是真源？ | 两个目录 |
| D5 | README GUI 功能描述使用 QWidget 术语（QWizard/QDialog），但代码已迁 QML | README.md L177-193 |
| D6 | `ui/__init__.py` 文档提到 `qml_bridge.py`（旧路径），实际文件在 `qml/qml_bridge.py` | auto_pm/ui/__init__.py L7 |

---

## 六、综合建议

### 6.1 立即修复（0-1 周）

1. **更新 README.md**：项目结构、GUI 功能描述、文档导航对齐实际代码
2. **更新 docs/归档索引.md**：反映 V3.0 文档体系
3. **明确声明 `00_项目基础信息/` 与 `02_设计/` 的关系**：治理类文档留 `00_`，设计类文档统一在 `02_设计/`
4. **清理 change_facade.py L96-97 的遗留注释**
5. **清理空目录** `auto_pm/gui/`，评估 `auto_pm/flet_app/` 是否保留

### 6.2 短期优化（2-4 周）

1. **统一 DTO 体系**：消除 `models/dto.py` 与 `contracts/dto/` 的双源
2. **为 Facade 构造函数添加类型注解**
3. **修复 WorkbenchFacade 的 `getattr(service, "_repo")` 反模式**：让 Service 暴露公开方法
4. **补充 Facade 集成测试**：用真实 Service（或轻量 Fake）替代纯 MagicMock
5. **清理 Facade 层的 `getattr(x, "value", x)` 模式**：既然模型已统一用 Literal，不需要兼容 Enum

### 6.3 中期推进（M5 里程碑方向）

1. **按 DSN §5.2 拆分 QmlBridge**：创建 5 个 Domain Bridge，QmlBridge 退化为装配入口
2. **统一 CLI 和 GUI 的 Service 装配路径**：AppContext + FacadeRegistry 合并或桥接
3. **完善事件体系**：DSN §8 定义了 7 种状态，contracts/events/ 目录已创建但为空

---

## 七、项目亮点总结

尽管上面列了不少问题，这个项目有几个值得特别肯定的特质：

1. **Dogfooding 纪律**：17 次 CHG 闭环，项目自己吃自己的狗粮，问题发现和流程验证都通过实践驱动
2. **技术债零剩余**：34/34 全部偿还的记录比绝大多数项目都好
3. **架构演进有据可查**：从 QWidget → QML → 五层 Facade，每一步都有 CHG 变更单、PM_SESSION 记录、技术债追踪
4. **领域建模精确**：12 状态机 + 门禁校验 + 章节渲染，变更管理的领域规则建模得很细
5. **Windows 工程实践扎实**：UTF-8 处理、控制台编码修复、跨平台路径，这些是很多项目忽略的

> [!IMPORTANT]
> 当前项目的主要短板不在代码质量，而在**文档真源不一致**和**新旧架构过渡期的冗余**。建议将文档同步作为下一个迭代的第一优先级——只有文档准确了，后续的迭代决策才有可靠的输入。
