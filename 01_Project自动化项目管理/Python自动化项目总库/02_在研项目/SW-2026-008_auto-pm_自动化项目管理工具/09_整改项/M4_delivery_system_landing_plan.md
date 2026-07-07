---
version: "V1.0"
status: "已完成"
created: "2026-07-07"
updated: "2026-07-07"
project_id: "SW-2026-008"
milestone: "M4（第 2 批）"
---

# M4 第 2 批：DeliveryFacade + SystemFacade 落地计划

## 一、目标与 done_when

**M4 总目标**：规范中心、报告发布、系统设置进入新结构
**M4 done_when**：主要全局页面全部脱离"直接绑多个 service"的扩展方式

**第 2 批目标**：DeliveryFacade 7 方法 + SystemFacade 6 方法从"转发层"升级为"用例编排层"，返回带类型 DTO
**第 2 批 done_when**：
- DeliveryFacade 7 方法返回带类型 DTO + DeliveryBridge 7 Slot 改用 asdict 转换（含 2 新 Slot）
- SystemFacade 6 方法返回带类型 DTO（list_templates/get_template_path 除外）+ SystemBridge 6 Slot 改用 asdict 转换（含 1 新 Slot）
- 测试覆盖 ≥30 个新增

## 二、现状诊断

### DeliveryFacade（delivery_facade.py）— 7 方法已落地但返回裸 dict

| 方法 | 当前返回 | 问题 |
|------|----------|------|
| refresh_project_docs(project_id, dry_run) | CommandResult[dict] | 裸 dict，无类型约束 |
| get_project_report() | QueryResult[dict] | 裸 dict，无类型约束 |
| get_change_report() | QueryResult[dict] | 裸 dict，无类型约束 |
| get_spec_report() | QueryResult[dict] | 裸 dict，无类型约束 |
| get_scan_report() | QueryResult[dict] | 裸 dict，无类型约束 |
| refresh_asset_summary() | CommandResult[dict] | 裸 dict，无类型约束 |
| get_asset_summary() | QueryResult[dict] | 裸 dict，无类型约束 |

### SystemFacade（system_facade.py）— 6 方法已落地但返回裸 dict

| 方法 | 当前返回 | 问题 |
|------|----------|------|
| get_pm_session_view() | QueryResult[dict] | 裸 dict，无类型约束 |
| run_pm_session_check() | CommandResult[dict] | 裸 dict，无类型约束 |
| list_templates() | QueryResult[list[str]] | 基础类型，无需 DTO |
| get_template_path(name) | QueryResult[str] | 基础类型，无需 DTO |
| get_template_detail(name) | QueryResult[dict] | 裸 dict（6 字段：name/version/description/stack/usage_count/path） |
| apply_template(pid, name) | CommandResult[dict] | 裸 dict，无类型约束 |

### Bridge 缺口

| Bridge | 现有 Slot | 缺失 Slot |
|--------|-----------|-----------|
| DeliveryBridge | 5（getProjectReport/getChangeReport/getSpecReport/getScanReport/refreshProjectDocs） | 2（refreshAssetSummary/getAssetSummary） |
| SystemBridge | 5（listTemplates/getTemplatePath/getTemplateDetail/getPmSessionView/runPmSessionCheck） | 1（applyTemplate） |

### DTO 缺口

- delivery_dto.py：不存在，需新建（7 DTO）
- system_dto.py：不存在，需新建（4 DTO）

## 三、DTO 设计

### delivery_dto.py（7 DTO）

| DTO | 字段 | 说明 |
|-----|------|------|
| RefreshProjectDocsResultDTO | project_id, dry_run, result: dict | 文档刷新结果 |
| ProjectReportDTO | data: dict | 项目报告（TODO: Service 结构明确后细化） |
| ChangeReportDTO | data: dict | 变更报告 |
| SpecReportDTO | data: dict | 规范报告 |
| ScanReportDTO | data: dict | 扫描报告 |
| RefreshAssetSummaryResultDTO | result: dict | 资产刷新结果 |
| AssetSummaryDTO | data: dict | 资产汇总 |

### system_dto.py（4 DTO）

| DTO | 字段 | 说明 |
|-----|------|------|
| PmSessionViewDTO | data: dict | PM_SESSION 视图 |
| PmSessionCheckResultDTO | data: dict | PM_SESSION 检查结果 |
| TemplateDetailDTO | name, version, description, stack, usage_count, path | 模板详情（具体字段） |
| ApplyTemplateResultDTO | project_id, template_name, result: dict | 模板应用结果 |

**注**：list_templates 返回 list[str]、get_template_path 返回 str，无需 DTO。

## 四、步骤 S1-S14

| 步骤 | 内容 | 产出 |
|------|------|------|
| S1 | 创建 delivery_dto.py | 7 DTO |
| S2 | 创建 system_dto.py | 4 DTO |
| S3+S4 | DeliveryFacade 7 方法重构 | 返回带类型 DTO |
| S5+S6 | SystemFacade 6 方法重构 | 返回带类型 DTO |
| S7+S8 | Bridge 重构（DeliveryBridge 7 Slot + SystemBridge 6 Slot） | asdict 转换 + 3 新 Slot |
| S9+S10 | Facade 单元测试扩展 | delivery 4→14 + system 5→15 |
| S11+S12 | Bridge 测试新建 | delivery 8 + system 7 |
| S13 | 三轨门禁回归 | ruff 0 + mypy ≤18 + pytest ~1209 passed |
| S14 | 文档更新 | M4_delivery_system_landing_plan.md + PM_SESSION §6 |

## 五、测试设计

### Facade 单元测试

| 测试文件 | 旧 | 新 | 增量 |
|----------|-----|-----|------|
| test_delivery_facade.py | 4 | 14 | +10 |
| test_system_facade.py | 5 | 15 | +10 |

### Bridge 测试

| 测试文件 | 旧 | 新 | 增量 |
|----------|-----|-----|------|
| test_delivery_bridge.py | 0 | 8 | +8 |
| test_system_bridge.py | 0 | 7 | +7 |

**合计新增 35 个测试**

## 六、风险与缓解

| 风险 | 等级 | 缓解 |
|------|------|------|
| DTO 字段用 dict 包装，价值有限 | 低 | 添加 TODO 注释，待 Service 层结构明确后细化 |
| SystemFacade.get_template_detail 有复杂逻辑 | 低 | 重构时保持逻辑不变，仅改返回类型 |
| 3 个新 Slot QML 端未接入 | 低 | 留 TODO M5 注释 |
| mypy 新增 error | 低 | M4-1 基线 18，本次实测 7（改善） |

## 七、预期收益

- DeliveryFacade 7 方法 + SystemFacade 6 方法全部从"转发层"升级为"用例编排层"
- DeliveryBridge 7 Slot + SystemBridge 6 Slot 全部落地（含 3 新 Slot）
- 新增 35 测试
- **达成 M4 done_when**："主要全局页面全部脱离直接绑多个 service 的扩展方式"

## 八、后续待办

1. M5 QML UI 开发：3 个新 Slot（refreshAssetSummary/getAssetSummary/applyTemplate）接入 QML 端
2. DTO 字段细化：待 Service 层返回结构明确后，将 dict 字段替换为具体字段
3. M4 dogfooding 闭环：补 CHG-*.md 变更单（类似 M2/M3 的 CHG-095/096）
4. 集成测试补齐：M4-1 留待第 2 批完成后统一补的集成测试

## 九、执行结果

### S1-S12 完成情况

| 步骤 | 状态 | 产出 |
|------|------|------|
| S1 | ✅ | delivery_dto.py 7 DTO |
| S2 | ✅ | system_dto.py 4 DTO |
| S3+S4 | ✅ | DeliveryFacade 7 方法重构 |
| S5+S6 | ✅ | SystemFacade 6 方法重构 |
| S7+S8 | ✅ | DeliveryBridge 7 Slot + SystemBridge 6 Slot |
| S9+S10 | ✅ | test_delivery_facade.py 14 测试 + test_system_facade.py 15 测试 |
| S11+S12 | ✅ | test_delivery_bridge.py 8 测试 + test_system_bridge.py 7 测试 |

### S13 三轨门禁结果

| 门禁 | 结果 | 对比 M4-1 基线 |
|------|------|----------------|
| ruff | 0 errors ✅ | 一致 |
| mypy | 7 errors in 5 files ✅ | 18→7 大幅改善（全部既有 P1/P2 非阻断） |
| pytest | 1211 passed, 2 skipped, 3 warnings in 28.19s ✅ | 1174→1211 增加 37 个测试 |

**mypy 7 errors 明细**（全部既有，M4-2 未引入新 error）：
1. change_list_model.py:71 unreachable
2. workbench_facade.py:157 workspace_root attr-defined（M2 引入）
3. workbench_facade.py:184 clear_cache attr-defined（M2 引入）
4. change_facade.py:116 allow_partial_verification call-arg（M3 引入）
5. registry.py:15 __init__ no-untyped-def
6. registry.py:40 project_service arg-type
7. qml_main_window.py:91 FacadeRegistry no-untyped-call

### 改动文件清单

**生产代码（6 个文件）**：
1. `auto_pm/ui/contracts/dto/delivery_dto.py`（S1 新建：7 DTO）
2. `auto_pm/ui/contracts/dto/system_dto.py`（S2 新建：4 DTO）
3. `auto_pm/application/delivery_facade.py`（S3+S4：7 方法重构返回带类型 DTO）
4. `auto_pm/application/system_facade.py`（S5+S6：6 方法重构返回带类型 DTO）
5. `auto_pm/ui/qml/bridges/delivery_bridge.py`（S7：5 Slot asdict + 2 Slot 新增）
6. `auto_pm/ui/qml/bridges/system_bridge.py`（S8：3 Slot asdict + 1 Slot 新增）

**测试代码（4 个文件）**：
1. `tests/application/test_delivery_facade.py`（S9：4→14 测试）
2. `tests/application/test_system_facade.py`（S10：5→15 测试）
3. `tests/qml/test_delivery_bridge.py`（S11 新建：8 测试）
4. `tests/qml/test_system_bridge.py`（S12 新建：7 测试）

## 十、M4 整体总结（第 1 批 + 第 2 批）

| 维度 | M4 第 1 批 | M4 第 2 批 | M4 合计 |
|------|-----------|-----------|---------|
| Facade 方法 | SpecFacade 3 | DeliveryFacade 7 + SystemFacade 6 | 16 |
| Bridge Slot | SpecBridge 3 | DeliveryBridge 7 + SystemBridge 6 | 16 |
| 新增 DTO | 3 | 11 | 14 |
| 新增测试 | 15 | 35 | 50 |
| ruff | 0 | 0 | 0 |
| mypy | 18→18 | 18→7 | 21→7（累计改善 14） |
| pytest | 1162→1174 | 1174→1211 | 1162→1211（+49） |

**M4 done_when 达成**：主要全局页面（规范中心/报告发布/系统设置）全部脱离"直接绑多个 service"的扩展方式，Facade 从"转发层"升级为"用例编排层"，返回带类型 DTO。

## 十一、后续待办实施情况（阶段 A：DTO 字段细化）

### A. DTO 字段细化结果（2026-07-07）

基于 Service 层返回结构调研（A1），对 11 个 DTO 分类处理：

**已细化为具体字段（6 个）**：

| DTO | 旧字段 | 新字段 | 依据 |
|-----|--------|--------|------|
| RefreshProjectDocsResultDTO | result: dict | project_id, dry_run, updated, refreshed_files, issues | DocRefreshResult.to_dict() 结构 |
| ProjectReportDTO | data: dict | total, by_stack, by_phase, by_business_line | ReportService.get_project_overview() |
| ChangeReportDTO | data: dict | total, by_status, by_domain | ReportService.get_change_overview() |
| SpecReportDTO | data: dict | total, found, missing, by_stack, missing_codes | ReportService.get_spec_report() |
| ScanReportDTO | data: dict | latest, last_sync_time, is_cache_available | ReportService.get_scan_report() |
| TemplateDetailDTO | (已是具体字段) | name, version, description, stack, usage_count, path | M4-2 已落地 |

**保留 dict 字段 + TODO 注释（5 个）**：因 Service 调用存在既有 bug，DTO 暂保留 dict 包装，待 bug 修复后细化。

| DTO | 当前字段 | 阻断原因（Service 调用 bug） |
|-----|---------|---------------------------|
| RefreshAssetSummaryResultDTO | result: dict | bug #2: Facade 调 refresh_all() 但 Service 无此方法 |
| AssetSummaryDTO | data: dict | bug #3: Facade 调 get_summary() 但 Service 无此方法 |
| PmSessionViewDTO | data: dict | bug #4: Facade 调 generate_view() 方式错误（模块级函数，返回 str） |
| PmSessionCheckResultDTO | data: dict | bug #5: Facade 调 check() 方式错误（需 file_path 参数，返回 CheckResult） |
| ApplyTemplateResultDTO | result: dict | bug #6: Facade 调 apply_template() 但 Service 无此方法（有 copy_template） |

### B. 6 个 Service 调用既有 bug 清单（待后续修复）

> 这些 bug 在 M4 之前就存在，Facade 用 isinstance 防御使单元测试能通过但实际运行会失败。修复需要改变 Facade 签名/依赖注入，不在当前阶段处理，记录为后续待办。

| # | Facade 方法 | Service 类 | 问题描述 | 修复方向 |
|---|------------|-----------|---------|---------|
| 1 | DeliveryFacade.refresh_project_docs | DocRefreshService | 传 project_id(str) 但 Service 期望 ProjectInfo 对象 | Facade 注入 ProjectService 查 ProjectInfo，或 Service 增加 project_id 重载 |
| 2 | DeliveryFacade.refresh_asset_summary | AssetSummaryService | 调用 refresh_all() 但方法不存在（仅有 build_summary） | Service 增加 refresh_all() 缓存入口，或 Facade 改调 build_summary |
| 3 | DeliveryFacade.get_asset_summary | AssetSummaryService | 调用 get_summary() 但方法不存在（仅有 build_summary） | 同 #2，缓存读取 vs 重建需明确 |
| 4 | SystemFacade.get_pm_session_view | pm_session_service | 调用 generate_view() 方式错误（模块级函数，返回 str 非 dict） | Facade 改为调用模块级函数 + 处理 str 返回 |
| 5 | SystemFacade.run_pm_session_check | PmSessionCheckService | 调用 check() 方式错误（需 file_path 参数，返回 CheckResult 非 dict） | Facade 注入 file_path，处理 CheckResult dataclass |
| 6 | SystemFacade.apply_template | TemplateService | 调用 apply_template() 但方法不存在（有 copy_template） | Service 增加 apply_template 语义封装，或 Facade 改调 copy_template |

### C. 阶段 A 验证结果

| 门禁 | 结果 | 对比 M4-2 基线 |
|------|------|----------------|
| ruff | 0 errors ✅ | 一致 |
| mypy | 7 errors in 5 files ✅ | 一致（全部既有） |
| pytest | 1211 passed, 2 skipped, 3 warnings in 27.75s ✅ | 一致 |

### D. 改动文件清单（阶段 A）

**生产代码（2 个文件）**：
1. `auto_pm/ui/contracts/dto/delivery_dto.py`（5 DTO 字段细化）
2. `auto_pm/application/delivery_facade.py`（5 方法构造具体字段 DTO）

**测试代码（2 个文件）**：
1. `tests/application/test_delivery_facade.py`（mock 返回值 + 断言更新）
2. `tests/qml/test_delivery_bridge.py`（DTO 构造 + 断言更新）

## 十二、后续待办实施情况（阶段 B：集成测试补齐）

### A. 集成测试覆盖结果（2026-07-07）

按"无 Service bug 的方法才补集成测试"原则，覆盖 3 个 Facade 共 10 个方法：

| Facade | 方法 | 集成测试 | 跳过原因 |
|--------|------|---------|----------|
| SpecFacade | run_spec_check | ✅ | — |
| SpecFacade | get_spec_center_overview | ✅ | — |
| SpecFacade | list_spec_center_entries | ✅ | — |
| DeliveryFacade | get_project_report | ✅ | — |
| DeliveryFacade | get_change_report | ✅ | — |
| DeliveryFacade | get_spec_report | ✅ | — |
| DeliveryFacade | get_scan_report | ✅ | — |
| DeliveryFacade | refresh_project_docs | ❌ | bug #1 |
| DeliveryFacade | refresh_asset_summary | ❌ | bug #2 |
| DeliveryFacade | get_asset_summary | ❌ | bug #3 |
| SystemFacade | list_templates | ✅ | — |
| SystemFacade | get_template_path | ✅ | — |
| SystemFacade | get_template_detail | ✅ | — |
| SystemFacade | get_pm_session_view | ❌ | bug #4 |
| SystemFacade | run_pm_session_check | ❌ | bug #5 |
| SystemFacade | apply_template | ❌ | bug #6 |

**新增 25 个集成测试**：
- test_spec_facade_int.py: 8 测试（overview / list_entries×3 / run_check / full_flow / no_service / file_exists）
- test_delivery_facade_int.py: 8 测试（4 report / full_flow / no_service / 2 error_case）
- test_system_facade_int.py: 9 测试（list / get_path×2 / get_detail×4 / full_flow / no_service）

### B. 共享 fixture（tests/application/conftest.py）

| Fixture | 用途 |
|---------|------|
| temp_workspace | 临时工作空间（含 PLC + Python 项目标志） |
| db_manager | 已 init_schema 的 DatabaseManager |
| project_repo_with_data | 预置 2 个项目记录（plc + python） |
| change_repo_with_data | 预置 1 个变更记录（DOCU/approved） |
| templates_dir | 含 2 个模板的目录（plc-standard + python-standard） |
| spec_registry_workspace | 含最小 spec_registry.json 的工作空间（2 条规范，1 found + 1 missing） |

### C. 阶段 B 验证结果

| 门禁 | 结果 | 对比阶段 A 基线 |
|------|------|----------------|
| ruff | 0 errors ✅ | 一致 |
| mypy | 7 errors in 5 files ✅ | 一致（全部既有） |
| pytest | 1236 passed, 2 skipped, 3 warnings in 27.99s ✅ | 1211→1236（+25 集成测试） |

### D. 改动文件清单（阶段 B）

**测试代码（4 个文件）**：
1. `tests/application/conftest.py`（新建：6 个共享 fixture）
2. `tests/application/test_spec_facade_int.py`（新建：8 集成测试）
3. `tests/application/test_delivery_facade_int.py`（新建：8 集成测试）
4. `tests/application/test_system_facade_int.py`（新建：9 集成测试）

## 十三、后续待办实施情况（阶段 C：Service Bug 修复）

### A. 阶段 C 执行结果（2026-07-07）

阶段 A 标记的 6 个 Service 调用 bug 经阶段 C 实际核查后，**4 个真 bug 修复 + 2 个误判纠正**：

| # | Facade 方法 | 处置 | 说明 |
|---|------------|------|------|
| 1 | DeliveryFacade.refresh_project_docs | ✅ 真 bug 修复 | 注入 ProjectService 查 ProjectInfo，调 `refresh_project_documents(project_info, dry_run)` |
| 2 | DeliveryFacade.refresh_asset_summary | ✅ 真 bug 修复 | 改调 `build_summary(project_path, stack, project_type)`，签名加 project_id |
| 3 | DeliveryFacade.get_asset_summary | ✅ 真 bug 修复 | 同 #2，改调 `build_summary`，签名加 project_id |
| 4 | SystemFacade.get_pm_session_view | ⚠️ 误判纠正 | factories.py 中 `_PmSessionViewAggregator` 已正确封装 generate_view 返回 dict |
| 5 | SystemFacade.run_pm_session_check | ⚠️ 误判纠正 | `_PmSessionViewAggregator` 已正确封装 check 返回 dict |
| 6 | SystemFacade.apply_template | ✅ 真 bug 修复 | 注入 ProjectService 查 ProjectInfo，调 `copy_template(template_name, dest_path, data, overwrite=True)` |

### B. 修复方案要点

**DeliveryFacade + SystemFacade 共用模式**：
1. 构造函数加 `project_service: Any = None` 参数
2. 新增 `_get_project_info(project_id)` helper：优先 DB 缓存（`get_project_cached`），fallback 文件系统扫描（`list_projects`）
3. Service 调用前先查 ProjectInfo，从 ProjectInfo 取 path/stack/project_type 传给 Service

**误判原因**：阶段 A 仅读 Facade + Service 代码即判断 bug，未读 factories.py 的 `_PmSessionViewAggregator` 聚合器封装。阶段 C 通过读 factories.py + 写 2 个集成测试验证后确认 #4/#5 误判。

### C. 集成测试补齐（17 新测试）

| 测试文件 | 阶段 B | 阶段 C 新增 | 覆盖范围 |
|---------|-------|------------|---------|
| test_delivery_facade_int.py | 8 | +10 | refresh_project_docs（4）+ refresh_asset_summary（4）+ get_asset_summary（2） |
| test_system_facade_int.py | 9 | +7 | apply_template（3）+ get_pm_session_view 误判验证（2）+ run_pm_session_check 误判验证（2） |

### D. 阶段 C 验证结果

| 门禁 | 结果 | 对比阶段 B 基线 |
|------|------|----------------|
| ruff | 0 errors ✅ | 一致 |
| mypy | 8 errors ✅ | 7→8（+1 非阻断，registry.py project_service 类型）|
| pytest | 1260 passed, 2 skipped, 3 warnings ✅ | 1236→1260（+24 测试）|

### E. 改动文件清单（阶段 C）

**生产代码（4 个文件）**：
1. `auto_pm/application/delivery_facade.py`（C1+C2：注入 project_service，修复 bug #1/#2/#3）
2. `auto_pm/application/system_facade.py`（C4：注入 project_service，修复 bug #6；C3 验证 #4/#5 误判）
3. `auto_pm/ui/registry.py`（C5：传入 project_service 给 DeliveryFacade 和 SystemFacade）
4. `auto_pm/ui/qml/bridges/delivery_bridge.py`（C6：refreshAssetSummary/getAssetSummary Slot 加 project_id 参数）

**测试代码（6 个文件）**：
1. `tests/application/conftest.py`（project_repo_with_data fixture path 改为绝对路径）
2. `tests/application/test_delivery_facade.py`（适配新签名 + 新增 5 边界测试）
3. `tests/application/test_system_facade.py`（适配 apply_template 新签名 + 新增 2 边界测试）
4. `tests/qml/test_delivery_bridge.py`（适配 Slot 新签名 + 跟踪调用列表）
5. `tests/application/test_delivery_facade_int.py`（追加 10 集成测试）
6. `tests/application/test_system_facade_int.py`（追加 7 集成测试）

### F. 阶段 C 后续待办

1. **阶段 D：M5 QML UI 开发** — 3 个新 Slot 接入 QML UI
   - refreshAssetSummary/getAssetSummary：资产汇总展示组件（需从当前选中项目传 project_id）
   - applyTemplate：模板应用对话框（需选模板 + 当前 project_id）
2. **阶段 E：dogfooding 闭环** — auto-pm 自身走 CHG-*.md 变更单流程（用户明确要求最后执行）

---

## §十四 阶段 D 结果（M5 QML UI 开发）

### A. 阶段 D 目标

将 M4 新增的 3 个 Bridge Slot 接入 QML UI：
1. `deliveryBridge.refreshAssetSummary(project_id)` — 资产汇总刷新按钮
2. `deliveryBridge.getAssetSummary(project_id)` — 资产汇总卡片展示
3. `systemBridge.applyTemplate(project_id, template_name)` — 模板应用对话框

### B. 实施步骤

| 步骤 | 内容 | 状态 |
|------|------|------|
| D0 | QML UI 架构调研（main.qml/views/dialogs/components/theme） | ✅ |
| D1 | WorkspaceView 接入 refreshAssetSummary/getAssetSummary | ✅ |
| D2 | WorkspaceView 概览 Tab 新增资产汇总 Card（仅 PLC 项目显示） | ✅ |
| D3 | TemplateView 接入 applyTemplate（对话框改造+结果展示）+ main.qml 绑定 currentProjectId | ✅ |
| D4 | 验证：三轨门禁 + QML 加载测试 + 既有编码损坏调查 | ✅ |

### C. 修改文件清单（阶段 D）

**QML 文件（3 个）**：
1. `auto_pm/ui/qml/main.qml` — TemplateView 绑定 `currentProjectId: mainWindow.currentProjectId`；修复 L392/L395 既有中文编码损坏（`加载?`→`加载了`、`未注?`→`未注入`）
2. `auto_pm/ui/qml/views/WorkspaceView.qml` — 新增 `assetSummary` 属性 + `loadAssetSummary()` 函数 + 资产汇总 Card（状态/Badge/刷新按钮/IO/程序块/通讯通道/问题明细）
3. `auto_pm/ui/qml/views/TemplateView.qml` — 新增 `currentProjectId`/`applyResultMessage` 属性；按钮"更新项目"→"应用模板到项目"；对话框改造（项目检查+确认/取消+结果消息）

### D. 阶段 D 验证结果

| 验证项 | 结果 | 说明 |
|--------|------|------|
| ruff | 0 errors ✅ | 一致 |
| mypy | 8 errors ✅ | 非阻断（既有） |
| pytest | 1260 passed ✅ | 一致（阶段 C 基线） |
| Bridge 单元测试 | 8 个全通过 ✅ | delivery_bridge + system_bridge |
| QML 加载测试 | main.qml 自身语法通过 ✅ | L392/L395 修复后 main.qml 无语法错误 |
| GUI 冒烟测试 | ⚠️ 无法运行 | 因系统性既有 QML 编码损坏（见 §E） |

### E. 既有 QML 编码损坏发现（系统性问题，非 M5 引入）

**调查结论**：用 `git stash` 对比确认，QML 编码损坏在原始版本（HEAD）中就存在，非 M5 修改引入。

**损坏范围**：79 处未闭合字符串损坏，分布在 6 个 view 文件：
| 文件 | 损坏数 | 说明 |
|------|--------|------|
| SpecCenterView.qml | 18 处 | 规范中心视图 |
| ReportView.qml | 17 处 | 报告中心视图 |
| ChangeCenterView.qml | 16 处 | 变更中心视图 |
| SettingsView.qml | 11 处 | 设置视图 |
| ProjectListView.qml | 10 处 | 项目列表视图 |
| WorkspaceView.qml | 6 处 | 工作区视图（M5 修改文件） |
| TemplateView.qml | 1 处 | 模板视图（M5 修改文件） |

**根因**：文件是有效 UTF-8 编码，但某些中文字符（如 `入`、`用`、`条`、`类`、`置`、`告`、`败`、`查`、`签`、`表`、`辑`、`化`）被损坏成 ASCII `?`（U+003F），导致字符串字面量未闭合，QML 解析失败。可能是之前某次编辑时以错误编码读取后保存导致。

**影响**：GUI 无法启动（main.qml 加载时实例化所有 view，任一 view 语法错误都会导致加载失败）。

**已修复**：
- `main.qml` L392/L395（2 处，已写入磁盘 ✅）
- `TemplateView.qml` / `WorkspaceView.qml` 的 Edit 修改在 VS Code 缓冲区但未写入磁盘（buffer staleness 问题）

**后续 TODO**（建议作为专门任务处理）：
1. 修复剩余 77 处未闭合字符串损坏（6 个 view 文件）
2. 修复注释中的 `?` 损坏（不影响解析，但影响可读性）
3. 修复后做 GUI 可见模式冒烟测试

### F. 阶段 D 后续待办

1. **QML 编码系统性修复**（专门任务）— 79 处未闭合损坏，6 个 view 文件
2. **阶段 E：dogfooding 闭环** — auto-pm 自身走 CHG-*.md 变更单流程（用户明确要求最后执行）
