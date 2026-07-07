---
version: "V1.0"
status: "已完成"
created: "2026-07-07"
updated: "2026-07-07"
project_id: "SW-2026-008"
milestone: "M3"
---

# M3 Change 域真正落地执行计划

## 一、目标与 done_when

### 1.1 目标
把 ChangeFacade 从"4 方法已落地但功能不全"补齐到"6 方法 + 时间线/验证摘要 DTO 完整"，把 ChangeBridge 从"4 Slot 列表/详情"补齐到"8 Slot 含创建/流转/时间线/验证摘要"，达成 005 里程碑 M3 的 done_when：**变更中心链路能以 Command/Result 表达完整动作**。

### 1.2 Done When（验收标准）
- ✅ ChangeFacade 6 个方法全部返回带类型 DTO（非裸 dict）
- ✅ ChangeBridge 8 个 Slot 全部用 `dataclasses.asdict()` 转换 DTO
- ✅ CreateChangeCommand 支持 impact_scope 字段
- ✅ 时间线 DTO（ChangeTimelineItemDTO）+ 验证摘要 DTO（ChangeValidationSummaryDTO）已建并接入
- ✅ ChangeService 新增 get_impact_analysis() 方法
- ✅ ChangeServiceProtocol 契约同步扩展
- ✅ 三轨门禁全绿：ruff 0 / mypy ≤21（非阻断）/ pytest 全通过
- ✅ 测试覆盖：ChangeFacade 单元测试 3→12+，集成测试 0→2+，Bridge 测试 0→4+

### 1.3 用户决策边界
- ✅ 先做 ChangeFacade/Bridge 自身（不立即回填 WorkbenchFacade 的 7 处 TODO M3）
- ✅ 时间线/验证摘要 DTO 纳入 M3
- ✅ M3 新增 Slot 需注释说明（QML 端不调整，留 TODO 注释）

---

## 二、现状诊断

### 2.1 ChangeFacade 4 方法现状（[change_facade.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/application/change_facade.py)）

| 方法 | 行号 | 状态 | 问题 |
|------|------|------|------|
| list_change_requests(project_id) | L63-74 | ✅ 已落地 | 走 list_all_changes / list_change_requests，返回 ChangeSummaryDTO |
| get_change_detail(change_id) | L76-85 | ✅ 已落地 | 走 get_change_request，返回 ChangeRequestDTO |
| create_change_request(command) | L87-105 | ⚠️ 半落地 | **impact_scope=[] 硬编码**（L98 TODO），未透传 command 字段 |
| transition_change(command) | L107-124 | ✅ 已落地 | 走 transition_status + 重新 get_change_request |

**结论**：4 方法整体比 M2 WorkbenchFacade 状态好（M2 是 5/6 空壳，M3 是 1/4 半空壳），主要缺口是 impact_scope 透传 + 2 个新方法（时间线/验证摘要）。

### 2.2 ChangeBridge 4 Slot 现状（[change_bridge.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/ui/qml/bridges/change_bridge.py)）

| Slot | 行号 | 状态 |
|------|------|------|
| listAllChanges() | L23-33 | ✅ 已落地（含缓存） |
| listChanges(project_id) | L35-41 | ✅ 已落地 |
| getChangeRequest(change_number) | L43-53 | ✅ 已落地（含缓存） |
| refreshChanges() | L55-58 | ✅ 已落地 |

**缺 4 个 Slot**：createChange / transitionChange / getChangeTimeline / getChangeValidationSummary

### 2.3 后端能力现状

| 组件 | 状态 | 说明 |
|------|------|------|
| ChangeService | ✅ 完整 | 800+ 行，CRUD + 状态流转 + 影响分析写入 |
| ChangeService.list_approval_history(change_number) | ✅ 已有 | L584-595，委托 _repo.list_approval_history |
| ChangeService.transition_status 内部 save_approval_record | ✅ 已有 | L552，流转时自动写 approval_history 表 |
| ChangeService.get_impact_analysis(change_number) | ❌ 缺 | 需新增（Repository 已有 get_impact_analysis L303） |
| ChangeRequestRepository | ✅ 完整 | save_impact_analysis / get_impact_analysis / save_approval_record / list_approval_history 全套 |
| ChangeServiceProtocol | ⚠️ 待扩展 | 需新增 get_impact_analysis 契约 |
| CreateChangeCommand | ⚠️ 待扩展 | 缺 impact_scope 字段 |
| TransitionChangeCommand | ✅ 完整 | 5 字段全 |
| ChangeSummaryDTO / ChangeRequestDTO | ✅ 完整 | 11/18 字段 |
| ChangeTimelineItemDTO | ❌ 缺 | 需新建（从 ApprovalRecord 映射） |
| ChangeValidationSummaryDTO | ❌ 缺 | 需新建（聚合 ImpactAnalysis + approval count） |

### 2.4 测试现状

| 文件 | 当前测试数 | 缺口 |
|------|-----------|------|
| tests/application/test_change_facade.py | 3（list/get/create） | 缺 transition / timeline / validation_summary / impact_scope / 错误路径 |
| tests/application/test_change_facade_int.py | 0（不存在） | 需新建集成测试 |
| tests/qml/test_change_bridge.py | 0（不存在） | 需新建 Bridge 测试 |

---

## 三、6 个方法迁移方案

### 3.1 已落地 4 方法的补全

#### 3.1.1 list_change_requests（无需改动）
当前已走 `list_all_changes()` / `list_change_requests(project_id)` 并返回 `list[ChangeSummaryDTO]`，符合 M3 要求。

#### 3.1.2 get_change_detail（无需改动）
当前已走 `get_change_request()` 并返回 `ChangeRequestDTO`，符合 M3 要求。

#### 3.1.3 create_change_request（S5 修复 impact_scope 透传）
**当前问题**：L98 `impact_scope=[]  # TODO: CreateChangeCommand 暂未携带 impact_scope`
**修复**：
- S2: CreateChangeCommand 新增 `impact_scope: list[str]` 字段（默认空列表）
- S5: ChangeFacade.create_change_request 改为 `impact_scope=command.impact_scope`

#### 3.1.4 transition_change（无需改动）
当前已走 `transition_status()` + 重新 `get_change_request()` 返回 `ChangeRequestDTO`，符合 M3 要求。

### 3.2 新增 2 方法

#### 3.2.1 get_change_timeline(change_id) → QueryResult[list[ChangeTimelineItemDTO]]
**数据流**：ChangeFacade → ChangeService.list_approval_history(change_number) → list[ApprovalRecord] → 映射为 list[ChangeTimelineItemDTO]

**DTO 字段**（从 ApprovalRecord 映射）：
```python
@dataclass(frozen=True)
class ChangeTimelineItemDTO:
    """变更审批时间线条目"""
    from_status: str
    to_status: str
    approver: str
    comment: str
    transition_date: str
```

#### 3.2.2 get_change_validation_summary(change_id) → QueryResult[ChangeValidationSummaryDTO]
**数据流**：ChangeFacade → 并行调用 ① ChangeService.list_approval_history(change_number) ② ChangeService.get_impact_analysis(change_number) → 聚合为 ChangeValidationSummaryDTO

**DTO 字段**：
```python
@dataclass(frozen=True)
class ChangeValidationSummaryDTO:
    """变更验证摘要（聚合影响分析 + 审批历史）"""
    change_number: str
    current_status: str
    risk_level: str
    mitigation: str
    propagation_chain: str
    approval_count: int
    last_approval_date: str | None
    domain_impacts: dict[str, Any]
    related_changes: list[str]
```

---

## 四、DTO 决策

延续 M2 的双源体系：
- **dataclass DTO**（auto_pm/ui/contracts/dto/change_dto.py）：Facade 边界，Bridge 用 `dataclasses.asdict()` 转 dict 给 QML
- **Pydantic 模型**（auto_pm/models/）：Service 层内部，含业务校验

M3 新增 2 个 DTO 全部用 dataclass，放在 `auto_pm/ui/contracts/dto/change_dto.py` 末尾。

---

## 五、测试用例清单（共 16+ 个）

### 5.1 ChangeFacade 单元测试（test_change_facade.py，3 → 12）

| # | 测试名 | 覆盖方法 | 场景 |
|---|--------|---------|------|
| 1 | test_list_change_requests | list_change_requests | 已有，正常列表 |
| 2 | test_get_change_detail | get_change_detail | 已有，正常详情 |
| 3 | test_create_change_request | create_change_request | 已有，但需更新断言 impact_scope |
| 4 | test_create_change_request_with_impact_scope | create_change_request | 新增，impact_scope 透传 |
| 5 | test_transition_change | transition_change | 新增，正常流转 |
| 6 | test_transition_change_service_exception | transition_change | 新增，Service 异常 |
| 7 | test_get_change_timeline_empty | get_change_timeline | 新增，无审批历史 |
| 8 | test_get_change_timeline_normal | get_change_timeline | 新增，多条审批记录 |
| 9 | test_get_change_timeline_not_found | get_change_timeline | 新增，change_id 不存在 |
| 10 | test_get_change_validation_summary_no_impact | get_change_validation_summary | 新增，无影响分析 |
| 11 | test_get_change_validation_summary_normal | get_change_validation_summary | 新增，含影响分析 + 审批历史 |
| 12 | test_get_change_validation_summary_service_exception | get_change_validation_summary | 新增，Service 异常 |
| 13 | test_list_change_requests_no_service | list_change_requests | 新增，service=None 降级 |
| 14 | test_create_change_request_no_service | create_change_request | 新增，service=None 降级 |

### 5.2 ChangeFacade 集成测试（test_change_facade_int.py，新建 2+）

| # | 测试名 | 场景 |
|---|--------|------|
| 1 | test_change_facade_full_flow | create → transition → get_timeline → get_validation_summary 端到端 |
| 2 | test_change_facade_list_and_filter | list_all + project_id 过滤 + status 过滤 |

### 5.3 ChangeBridge 单元测试（test_change_bridge.py，新建 4+）

| # | 测试名 | 场景 |
|---|--------|------|
| 1 | test_change_bridge_list_all_changes | listAllChanges() 返回 list[dict] |
| 2 | test_change_bridge_get_change_request | getChangeRequest() 返回 dict |
| 3 | test_change_bridge_create_change | createChange() 委托 Facade 并返回 dict |
| 4 | test_change_bridge_transition_change | transitionChange() 委托 Facade 并返回 dict |
| 5 | test_change_bridge_get_timeline | getChangeTimeline() 返回 list[dict] |
| 6 | test_change_bridge_no_facade | facade=None 时所有 Slot 降级返回空值 |

---

## 六、14 步执行顺序（S1-S14）

| 步骤 | 内容 | 文件 |
|------|------|------|
| S1 | 新增 2 个 DTO（ChangeTimelineItemDTO + ChangeValidationSummaryDTO） | change_dto.py |
| S2 | CreateChangeCommand 新增 impact_scope 字段 | change_commands.py |
| S3 | ChangeService 新增 get_impact_analysis() 方法 | change_service.py |
| S4 | ChangeServiceProtocol 新增 get_impact_analysis 契约 | protocols.py |
| S5 | ChangeFacade.create_change_request 修复 impact_scope 透传 | change_facade.py |
| S6 | ChangeFacade 新增 get_change_timeline() 方法 | change_facade.py |
| S7 | ChangeFacade 新增 get_change_validation_summary() 方法 | change_facade.py |
| S8 | ChangeBridge 新增 createChange Slot（含注释说明） | change_bridge.py |
| S9 | ChangeBridge 新增 transitionChange Slot（含注释说明） | change_bridge.py |
| S10 | ChangeBridge 新增 getChangeTimeline Slot | change_bridge.py |
| S11 | ChangeBridge 新增 getChangeValidationSummary Slot | change_bridge.py |
| S12 | test_change_facade.py 单元测试扩展 3 → 14 | test_change_facade.py |
| S13 | 新建 test_change_facade_int.py + test_change_bridge.py | 2 个新文件 |
| S14 | 三轨门禁回归 + 更新 PM_SESSION + M3 计划文档状态 | 文档 |

---

## 七、风险评估

### 7.1 技术风险
- **低**：M3 全部工作在 M2 已验证的"用例编排 + DTO + Bridge asdict"模式内，无新技术
- **低**：ChangeService 后端能力完整，仅缺 get_impact_analysis 1 个方法（Repository 已有）
- **中**：transition_status 写 approval_history 的时机需确认——若 transition 失败时是否回滚 approval_history 记录（影响时间线数据一致性）

### 7.2 范围风险
- **低**：用户已明确"先做 ChangeFacade/Bridge 自身"，WorkbenchFacade 的 7 处 TODO M3 暂不回填
- **低**：QML 端不调整，新增 Slot 用注释说明（避免 UI 改动连锁）

### 7.3 测试风险
- **中**：集成测试需构造真实 ChangeService + DB + 临时项目目录，fixture 比 M2 复杂（需创建 CHG-*.md 变更单文件）
- **低**：Bridge 测试可全用 Mock，无文件系统依赖

---

## 八、不在 M3 范围内

- WorkbenchFacade 的 7 处 TODO M3 回填（health_status / last_activity_at / pending_actions / document_status / vartable_status）—— 留待 M3 完成后单独迭代
- QML 端新增 createChange/transitionChange 对应 UI（对话框/表单）—— 留待 M5 Bridge 收口
- ChangeService 业务逻辑增强（如 transition_status 失败回滚 approval_history）—— 留待 M6 性能/稳定性优化
- 变更单导出 PDF / 邮件通知 —— 不在 M0-M9 路线图内

---

## 九、执行结果与验证记录

### 9.1 S1-S14 步骤完成情况

| 步骤 | 内容 | 状态 | 备注 |
|------|------|------|------|
| S1 | 新增 ChangeTimelineItemDTO + ChangeValidationSummaryDTO | ✅ 已完成 | change_dto.py 末尾追加 2 个 frozen dataclass |
| S2 | CreateChangeCommand 新增 impact_scope 字段 | ✅ 已完成 | 默认 `field(default_factory=list)`，消除 Facade 硬编码 |
| S3 | ChangeService 新增 get_impact_analysis() 方法 | ✅ 已完成 | 委托 _repo.get_impact_analysis，无 DB 时返回 None |
| S4 | ChangeServiceProtocol 契约同步扩展 | ✅ 已完成 | 追加 list_approval_history + get_impact_analysis 签名 |
| S5 | ChangeFacade.create_change_request 修复 impact_scope 透传 | ✅ 已完成 | 硬编码 `impact_scope=[]` 改为 `impact_scope=list(command.impact_scope)` |
| S6 | ChangeFacade 新增 get_change_timeline() | ✅ 已完成 | ApprovalRecord → ChangeTimelineItemDTO 映射 + try/except 降级 |
| S7 | ChangeFacade 新增 get_change_validation_summary() | ✅ 已完成 | 聚合 ImpactAnalysis + ApprovalHistory + ChangeRequest |
| S8 | ChangeBridge 新增 createChange Slot | ✅ 已完成 | 含 M3 注释说明 + 失效列表缓存 + emit changesChanged |
| S9 | ChangeBridge 新增 transitionChange Slot | ✅ 已完成 | 含 M3 注释说明 + 失效详情/列表缓存 + emit changesChanged |
| S10 | ChangeBridge 新增 getChangeTimeline Slot | ✅ 已完成 | 含 M3 注释说明 + asdict 转 dict |
| S11 | ChangeBridge 新增 getChangeValidationSummary Slot | ✅ 已完成 | 含 M3 注释说明 + asdict 转 dict |
| S12 | test_change_facade.py 单元测试扩展 | ✅ 已完成 | 3 → 17 个测试，新增 4 个 mock helper |
| S13 | 新建 test_change_facade_int.py + test_change_bridge.py | ✅ 已完成 | 6 集成测试 + 8 Bridge 测试 |
| S14 | 三轨门禁回归 + 文档更新 | ✅ 已完成 | 见 9.2 |

### 9.2 三轨门禁最终结果

| 门禁 | 结果 | 备注 |
|------|------|------|
| ruff check . | ✅ All checks passed | 0 errors |
| mypy auto_pm | ⚠️ 21 errors in 8 files | 与 M2 基线一致，非阻断；未引入新增 error |
| pytest --no-cov -q | ✅ 1162 passed, 2 skipped, 3 warnings in 27.87s | M2 基线 1134 + M3 新增 28 = 1162 |

**结论**：三轨门禁全绿，M3 落地达成 done_when 全部验收标准。

### 9.3 修复的关键 Bug

#### Bug 1: ruff F401 unused import pytest
- **文件**：tests/qml/test_change_bridge.py
- **现象**：Bridge 测试用 qapp fixture 但不直接用 pytest，ruff 报 unused import
- **修复**：删除 `import pytest`

#### Bug 2: ImpactScope 枚举校验失败
- **现象**：`ValidationError: Input should be 'LOCAL', 'MODULE', 'SYSTEM', 'CROSS', 'SAFE' or ''`
- **根因**：集成测试 fixture 用 `impact_scope=["约束A"]`，但 ChangeSummary.impact_scope 是 `list[ImpactScope]` 枚举
- **修复**：改为 `impact_scope=["LOCAL"]`，同步修改断言

#### Bug 3: save_approval_record 签名不匹配
- **现象**：`TypeError: missing 2 required positional arguments: 'to_status' and 'approver'`
- **根因**：ChangeRequestRepository.save_approval_record 签名是位置参数 `(change_number, to_status, approver, comment, from_status)`，不接受 ApprovalRecord 对象
- **修复**：改用 `ApprovalHistoryRepository.insert(ApprovalRecord(...))` 直接写入完整记录含 transition_date

#### Bug 4: get_change_request 走文件系统不从 DB 读取
- **现象**：`Change CHG-2026-001 not found`，日志显示"获取变更单: 文件未找到"
- **根因**：ChangeService.get_change_request 通过 `self._locator.find_change_file()` 扫描文件系统，不从 DB 缓存读取
- **修复**：集成测试 fixture 中 mock 该方法 `change_service.get_change_request = lambda cn: mock_cr if cn == "CHG-2026-001" else None`，其他方法保持真实走 DB

### 9.4 改动文件清单

#### 生产代码（7 个文件）
| 文件 | 改动类型 | 内容 |
|------|---------|------|
| auto_pm/ui/contracts/dto/change_dto.py | 修改 | 新增 2 个 DTO（ChangeTimelineItemDTO + ChangeValidationSummaryDTO） |
| auto_pm/ui/contracts/commands/change_commands.py | 修改 | CreateChangeCommand 新增 impact_scope 字段 |
| auto_pm/change/change_service.py | 修改 | 新增 get_impact_analysis() 方法 + 导入 ImpactAnalysis |
| auto_pm/core/protocols.py | 修改 | ChangeServiceProtocol 追加 list_approval_history + get_impact_analysis 契约 |
| auto_pm/application/change_facade.py | 修改 | S5 修复 impact_scope 透传 + S6/S7 新增 2 个方法 |
| auto_pm/ui/qml/bridges/change_bridge.py | 修改 | 新增 4 个 Slot（含 M3 注释说明） |

#### 测试代码（3 个文件）
| 文件 | 改动类型 | 内容 |
|------|---------|------|
| tests/application/test_change_facade.py | 修改 | 3 → 17 个测试，新增 4 个 mock helper |
| tests/application/test_change_facade_int.py | 新建 | 6 个集成测试，fixture 预置 DB 记录 + mock get_change_request |
| tests/qml/test_change_bridge.py | 新建 | 8 个 Bridge 测试 + 4 个 DTO 构造 helper |

#### 文档（2 个文件）
| 文件 | 改动类型 | 内容 |
|------|---------|------|
| 09_整改项/M3_change_landing_plan.md | 修改 | status 待执行 → 已完成 + 填写 §九 执行结果 |
| PM_SESSION_SW-2026-008.md | 修改 | §6 追加 M3 落地实施记录 |

### 9.5 后续待办（移交 M4/M5）

#### M5 Bridge 收口（QML 端 UI 接入）
- 新增 createChange 对应 UI（创建变更单对话框，含 impact_scope 多选）
- 新增 transitionChange 对应 UI（流转操作按钮 + 审批意见输入）
- 新增 getChangeTimeline 对应 UI（时间线视图，按 transition_date 排序）
- 新增 getChangeValidationSummary 对应 UI（验证摘要面板，展示风险等级/缓解措施/审批计数）
- 当前 4 个 Slot 已暴露接口，QML 端按 TODO M5 注释指引接入即可

#### WorkbenchFacade 7 处 TODO M3 回填（独立迭代）
- get_dashboard_snapshot 的 health_status / last_activity_at / pending_actions
- get_settings_summary 的 document_status / vartable_status
- 用户已明确"先做 ChangeFacade/Bridge 自身"，7 处 TODO 留待 M3 完成后单独迭代

#### ChangeService 业务逻辑增强（M6 性能/稳定性）
- transition_status 失败时是否回滚 approval_history 记录（影响时间线数据一致性）
- 变更单导出 PDF / 邮件通知（不在 M0-M9 路线图内，长期待办）

#### Dogfooding 闭环（auto-pm 自身变更管理）
- auto-pm 项目自身需补 CHG-*.md 变更单，走自己的变更管理流程
- 当前 M3 落地未生成 CHG-DOCU-2026-xxx 变更单，留待 dogfooding 专项整改
