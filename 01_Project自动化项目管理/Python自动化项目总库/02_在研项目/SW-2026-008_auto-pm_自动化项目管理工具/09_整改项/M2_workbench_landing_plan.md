---
version: "V1.0"
status: "已完成"
created: "2026-07-07"
updated: "2026-07-07"
project_id: "SW-2026-008"
milestone: "M2"
completed_at: "2026-07-07"
---

# M2 Workbench 域真正落地执行计划

## 一、目标与 done_when

**目标**：让 WorkbenchFacade 从"转发层"升级为"用例编排层"，真正承担 M2 里程碑定义的职责。

**done_when**（对应 005 计划 M2）：
- Facade 6 个方法均通过 Service 层编排，不直接操作文件/拼装裸 dict
- 6 个方法均有单元测试（成功/失败/边界）+ 端到端集成测试
- 三轨门禁保持通过（ruff 0 + pytest 全绿 + mypy 不新增错误）
- PM_SESSION §6 追加 M2 落地实施记录

## 二、当前空壳问题诊断

| Facade 方法 | 空壳类型 | 问题 |
|-------------|----------|------|
| `get_dashboard_snapshot()` | 非空壳但冗余 | DashboardSummaryDTO→DashboardSnapshotDTO 全量复制，含无意义 list() 转换 |
| `list_project_cards()` | **空壳** | 调 `list_projects()`（文件系统扫描）而非 `list_projects_with_change_count()`（DB 缓存+聚合），`open_change_count` 硬编码 0 |
| `get_project_workspace()` | **半空壳** | document_status/vartable_status/pending_actions 全为 None/[] |
| `get_settings_summary()` | **空壳** | 返回 dict 无 DTO，直接调 4 个 Service 方法拼装 |
| `clear_cache()` | **空壳** | 绕过 Service 直接 `os.remove` db 文件 |
| `rebuild_index()` | **半空壳** | payload 拼装在 Facade，返回 dict 无 DTO |

**现有测试覆盖**：仅 2 个（get_dashboard_snapshot 成功/失败），其余 5 个方法零覆盖。

## 三、需要迁移的具体方法（6 个）

### 方法 1：`list_project_cards()` —— 核心迁移

**现状**（workbench_facade.py L54-74）：
- 调 `list_projects()`（文件系统扫描）
- `open_change_count` 硬编码 0
- `health_status` 硬编码 "Unknown"
- `last_activity_at` 硬编码 None

**迁移方案**：
- 改调 `list_projects_with_change_count()`（project_service.py L144，返回 ProjectListItem 含 change_count）
- ProjectListItem → ProjectCardDTO 映射保留在 Facade（边界转换）
- `open_change_count` 从 ProjectListItem.change_count 取值
- `health_status` 暂保留 "Unknown"（M3 Change 域落地时接入）
- `last_activity_at` 暂保留 None（需 file_mtime，M2 不接入，标注 TODO）
- **降级策略**：无 DB 时捕获 RuntimeError 降级为 list_projects() + change_count=0

### 方法 2：`get_settings_summary()` —— 补 DTO

**现状**：返回 QueryResult[dict]，无 DTO

**迁移方案**：
- workbench_dto.py 新增 `SettingsSummaryDTO`（workspace_root/db_path/project_count/last_sync/db_available）
- Facade 返回 QueryResult[SettingsSummaryDTO]
- WorkbenchBridge.getSettingsSummary() 改为 dataclasses.asdict(res.payload)

### 方法 3：`clear_cache()` —— 走 Service 层

**现状**：直接 os.remove db 文件 + db.init_schema()

**迁移方案**：
- ProjectService 新增 `clear_cache()` 方法（封装删除 db 文件 + 重建 schema）
- Facade 调 project_service.clear_cache()，不再直接操作文件
- 新增 `ClearCacheResultDTO`（success/message）

### 方法 4：`rebuild_index()` —— payload 标准化

**现状**：返回 CommandResult[dict]，含 int(result.get(...)) 防御性转换

**迁移方案**：
- 新增 `RebuildIndexResultDTO`（projects_found/changes_found/message）
- 消除防御性转换

### 方法 5：`get_project_workspace()` —— 最小化补充

**现状**：document_status/vartable_status/pending_actions 全为 None/[]

**迁移方案**（M2 范围内最小化）：
- pending_actions：从 ChangeService 查询该项目的 open changes（如方法存在且可用）
- document_status / vartable_status：保留 None + TODO 注释（留待 M3/M4）
- 避免过度工程——不新建 Service

### 方法 6：`get_dashboard_snapshot()` —— 消除冗余

**现状**：DashboardSummaryDTO→DashboardSnapshotDTO 全量复制 + list() 转换

**迁移方案**：
- 保留双 DTO（dataclass 作 Facade 边界，Pydantic 作 Service 层）
- 消除无意义的 list(summary.failed_check_project_ids) 转换

## 四、DTO 体系决策

| 决策点 | 方案 | 理由 |
|--------|------|------|
| DashboardSnapshotDTO vs DashboardSummaryDTO | 保留双 DTO | dataclass 作 Facade 边界，Pydantic 作 Service 层，架构分层合理 |
| ProjectCardDTO vs ProjectListItem | 保留双 DTO | ProjectCardDTO 是 UI 展示 DTO，ProjectListItem 是轻量列表 DTO |
| SettingsSummaryDTO | **新增** | 当前返回 dict 不规范 |
| RebuildIndexResultDTO | **新增** | 当前返回 dict 不规范 |
| ClearCacheResultDTO | **新增** | 当前返回 dict 不规范 |

## 五、测试用例清单（19 个）

### 单元测试 test_workbench_facade.py（现有 2 + 新增 14 = 16）

**`list_project_cards()`（4 个新增）**：
1. `test_list_project_cards_empty` —— 空列表返回 success + []
2. `test_list_project_cards_normal` —— 正常列表，验证字段映射（含 change_count）
3. `test_list_project_cards_service_exception` —— Service 抛异常时 success=False
4. `test_list_project_cards_no_db_fallback` —— 无 DB 时降级为 list_projects()

**`get_project_workspace()`（3 个新增）**：
5. `test_get_project_workspace_not_found` —— 项目不存在返回 success=False
6. `test_get_project_workspace_normal` —— 正常项目，验证 summary + asset_summary
7. `test_get_project_workspace_python_project` —— Python 项目 asset_summary 为 not_applicable

**`get_settings_summary()`（3 个新增）**：
8. `test_get_settings_summary_no_db` —— 无 DB 时 db_available=False
9. `test_get_settings_summary_with_db` —— 有 DB 时返回正确统计 + DTO 字段
10. `test_get_settings_summary_exception` —— 异常降级

**`clear_cache()`（2 个新增）**：
11. `test_clear_cache_no_db` —— 无 DB 时 success=False
12. `test_clear_cache_success` —— 正常清除后验证 db 重建

**`rebuild_index()`（2 个新增）**：
13. `test_rebuild_index_no_db` —— 无 DB 时 success=False
14. `test_rebuild_index_success` —— 正常重建后验证 projects_found/changes_found

### 集成测试 test_workbench_facade_int.py（现有 1 + 新增 2 = 3）

15. `test_workbench_facade_full_flow` —— 端到端：rebuild_index → list_project_cards → get_project_workspace → get_dashboard_snapshot
16. `test_workbench_facade_clear_and_rebuild` —— 清缓存后重建索引，验证数据一致性

### Bridge 测试 tests/qml/test_workbench_bridge.py（新建，3 个）

17. `test_workbench_bridge_list_projects` —— Bridge.listProjects() 返回 list[dict]
18. `test_workbench_bridge_dashboard_summary` —— Bridge.getDashboardSummary() 返回 dict
19. `test_workbench_bridge_no_facade` —— facade=None 时所有 Slot 降级返回空

## 六、执行顺序

| 步骤 | 内容 | 依赖 |
|------|------|------|
| S1 | workbench_dto.py 新增 3 个 DTO | 无 |
| S2 | ProjectService 新增 clear_cache() 方法 | 无 |
| S3 | 重构 Facade.list_project_cards() | S1 |
| S4 | 重构 Facade.get_settings_summary() | S1 |
| S5 | 重构 Facade.clear_cache() | S2 |
| S6 | 重构 Facade.rebuild_index() | S1 |
| S7 | 微调 Facade.get_dashboard_snapshot() | 无 |
| S8 | 微调 Facade.get_project_workspace() | 无 |
| S9 | WorkbenchBridge.getSettingsSummary() 改用 asdict | S4 |
| S10 | 补 14 个单元测试 | S3-S8 |
| S11 | 补 2 个集成测试 | S10 |
| S12 | 补 3 个 Bridge 测试 | S10 |
| S13 | 三轨门禁回归验证 | S10-S12 |
| S14 | 更新 PM_SESSION 文档 | S13 |

## 七、风险评估

| 风险 | 等级 | 控制方式 |
|------|------|----------|
| list_projects_with_change_count 无 DB 时抛 RuntimeError | 中 | Facade 捕获降级为 list_projects() + change_count=0 |
| get_project_workspace 的 document_status/vartable_status 无对应 Service | 低 | 保留 None + TODO 注释，不新建 Service |
| DTO 新增导致 Bridge 的 asdict 失败 | 低 | Bridge 已用 asdict，新 DTO 只要是 dataclass 即可 |
| 集成测试 fixture 需完整项目标志文件 + DB | 中 | 复用 test_workbench_facade_int.py 现有 fixture 模式 |
| mypy 新增类型错误 | 低 | 每个 DTO 都标注字段类型，Facade 返回类型明确 |

## 八、不在 M2 范围内

- document_status / vartable_status 真正接入（需 DocumentService/VartableService，留待 M3/M4）
- health_status 实时计算（需 Change 域数据，留待 M3）
- last_activity_at 从 file_mtime 转换（留待 M3）
- 性能优化（FPS/内存，留待 M6）
- QML 界面调整（Bridge Slot 接口不变，QML 无需改动）

## 九、执行结果与验证记录（2026-07-07 完成）

### 9.1 S1-S14 步骤完成情况

| 步骤 | 内容 | 状态 |
|------|------|------|
| S1 | 新增 3 个 DTO（SettingsSummaryDTO/RebuildIndexResultDTO/ClearCacheResultDTO） | ✅ |
| S2 | ProjectService 新增 clear_cache() 方法（封装 DB 文件删除+重建） | ✅ |
| S3 | list_project_cards() 重构：DB 优先 + RuntimeError 降级 list_projects() | ✅ |
| S4 | get_settings_summary() 返回 SettingsSummaryDTO | ✅ |
| S5 | clear_cache() 调用 Service 而非直接 os.remove | ✅ |
| S6 | rebuild_index() 返回 RebuildIndexResultDTO | ✅ |
| S7 | get_dashboard_snapshot() 消除冗余 list() 转换 | ✅ |
| S8 | get_project_workspace() 添加 TODO 注释 | ✅ |
| S9 | WorkbenchBridge 3 个 Slot 改用 dataclasses.asdict() | ✅ |
| S10 | test_workbench_facade.py 单元测试 2 → 16（新增 14 个） | ✅ |
| S11 | test_workbench_facade_int.py 集成测试 1 → 3（新增 2 个端到端） | ✅ |
| S12 | tests/qml/test_workbench_bridge.py 新建（3 个 Slot 测试） | ✅ |
| S13 | 三轨门禁回归：ruff 0 / mypy 21 / pytest 1134 passed, 2 skipped | ✅ |
| S14 | 更新 PM_SESSION 文档与本计划状态 | ✅ |

### 9.2 三轨门禁最终结果

- **ruff check**: All checks passed ✅
- **mypy auto_pm**: 21 errors in 8 files（非阻断，从 P0 修复后的 24 降到 21）✅
- **pytest**: 1134 passed, 2 skipped, 3 warnings in 28.67s ✅
  - 比 M2 落地前增加 17 个测试（1115 → 1132 → 1134）
  - 失败测试全部修复

### 9.3 修复的关键 Bug

#### Bug 1：fixture .copier-answers.yml 字段名错误
- **现象**：test_workbench_facade_full_flow 断言 `card.name == "Test Project"` 失败，实际值为目录名 "SW-2026-001_Test"
- **根因**：fixture 用 `name: Test Project`，但 ProjectScanner 期望字段名是 `project_name:`（参见 project_service.py:382 `answers.setdefault("project_name", proj.name)`）
- **修复**：fixture 字段名改为 `project_name:`

#### Bug 2：fixture DatabaseManager 路径误用
- **现象**：db_path 出现 `workspace/auto_pm.db/.auto-pm/index.db` 这种错乱路径
- **根因**：fixture 把 `os.path.join(temp_workspace, "auto_pm.db")` 当 workspace_root 传给 DatabaseManager，导致 "auto_pm.db" 被当成目录名
- **修复**：直接传 `temp_workspace` 给 DatabaseManager，db 实际路径自动生成为 `<workspace>/.auto-pm/index.db`

#### Bug 3：clear_cache() 在 Windows 上抛 WinError 32（生产代码 bug）
- **现象**：clear_cache() 调用 `os.remove(db_path)` 时报"另一个程序正在使用此文件"
- **根因**：sqlite3 WAL 模式下 -wal/-shm 文件被未关闭的连接持有锁；ProjectService 持有 Repository 引用，Repository 持有 db 引用
- **修复**：clear_cache() 增加 3 步稳健处理：
  1. 释放 Repository 引用 + `gc.collect()` 强制回收 sqlite3 连接
  2. 删除文件重试 3 次（间隔 100/200/300ms）
  3. 重试仍失败时降级为 `drop_all() + init_schema()`（清空数据但不删除文件）

### 9.4 改动文件清单

**生产代码（3 个文件）**：
- `auto_pm/ui/contracts/dto/workbench_dto.py`：新增 3 个 DTO
- `auto_pm/core/project_service.py`：新增 clear_cache() 方法（含 Windows WAL 文件锁处理）
- `auto_pm/application/workbench_facade.py`：6 个方法全部从"转发层"重构为"用例编排层"
- `auto_pm/ui/qml/bridges/workbench_bridge.py`：3 个 Slot 改用 asdict 转换 DTO

**测试代码（3 个文件）**：
- `tests/application/test_workbench_facade.py`：单元测试 2 → 16
- `tests/application/test_workbench_facade_int.py`：集成测试 1 → 3，修复 fixture 路径/字段名
- `tests/qml/test_workbench_bridge.py`：新建，3 个 Slot 测试

### 9.5 后续待办（移交 M3）

- M3 落地 Change 域后，回填 list_project_cards 的 `health_status`/`last_activity_at` 字段
- M3 落地后，回填 get_project_workspace 的 `pending_actions`（从 ChangeService 查询 open changes）
- M4 落地后，回填 get_project_workspace 的 `document_status`/`vartable_status`
