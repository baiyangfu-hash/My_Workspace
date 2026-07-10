---
title: auto-pm GUI 测试计划
version: V0.9.2
date: 2026-07-10
scope: QML 页面全量测试矩阵
baseline: pyproject=0.9.1 / 1115 passed / QML 143 passed（V0.9.2 新增 4 个 detectProject 测试）
---

# auto-pm GUI 测试计划

> 适用范围：`auto_pm/ui/qml/` 全量 QML 页面 + 5 个 Domain Bridge + 3 个 QAbstractListModel + 10 个可复用组件 + 8 个对话框。
> 基线说明：V0.9.0 完成 QWidget→QML 迁移并删除 84 个旧文件，QML 为唯一 UI 入口；当前 `pyproject.toml` 版本 0.9.1，全量回归 1115 passed。

---

## 1. 测试目标与范围

### 1.1 测试目标

| 目标编号 | 目标 | 验收标准 |
|---------|------|---------|
| G1 | QML 页面可加载性 | 8 个 view + 8 个 dialog + 10 个 component 在 QQmlEngine 下无错误加载 |
| G2 | Bridge Slot 契约一致性 | 5 个 Bridge 的全部 Slot 在 facade 可用时返回正确 dict/list，在 facade=None 时降级不抛异常 |
| G3 | DTO→dict 转换正确性 | `dataclasses.asdict()` 转换的 dict 字段与 QML 端 `model.xxx` 访问路径一致 |
| G4 | 状态覆盖完整性 | 每个页面覆盖 idle/loading/success/empty/warning/error 6 状态（详见 §5） |
| G5 | 关键交互链路可用 | §6 列出的 6 条关键链路端到端可走通，含参数透传与信号 emit |
| G6 | 模型数据流正确 | ProjectListModel / ChangeListModel / VarTableModel 的 setXxx/data/roleNames 正确 |
| G7 | 三重守卫生效 | `typeof xxxBridge === "undefined" \|\| xxxBridge === null \|\| !xxxBridge.hasService` 在所有页面降级为空数据/错误提示 |

### 1.2 测试范围

**纳入范围：**
- `auto_pm/ui/qml/` 下全部 QML 文件（main.qml + 8 views + 10 components + 8 dialogs + theme/Theme.qml）
- `auto_pm/ui/qml/bridges/` 下 5 个 Bridge（WorkbenchBridge/ChangeBridge/SpecBridge/DeliveryBridge/SystemBridge）
- `auto_pm/ui/qml/models/` 下 3 个 QAbstractListModel（ProjectListModel/ChangeListModel/VarTableModel）
- `auto_pm/ui/contracts/dto/` 下 5 个 DTO 模块（workbench_dto/change_dto/spec_dto/delivery_dto/system_dto）
- `auto_pm/ui/qml_main_window.py` 的 Bridge 装配与 context property 注入
- `tests/qml/` 下现有 11 个测试文件

**不纳入范围：**
- 后端 Service/Facade 层内部逻辑（由 `tests/unit/`、`tests/integration/` 覆盖）
- CLI 命令测试（由 `tests/cli/` 覆盖，标记 `@pytest.mark.cli`）
- 真实文件系统/DB 扫描（GUI 测试统一用 Mock Facade，无文件系统依赖）

### 1.3 测试分层

| 层级 | 测试对象 | 测试方式 | 现有资产 |
|------|---------|---------|---------|
| L1 Bridge 单元 | 5 个 Bridge 的 Slot | Mock Facade + 直接调用 Slot + QSignalSpy | `test_*_bridge.py`（5 文件） |
| L2 Model 单元 | 3 个 QAbstractListModel | 直接调用方法，不走 QML 渲染 | `test_*_model.py`（3 文件） |
| L3 组件加载 | 10 个 component + 8 个 dialog | QQmlEngine + QQmlComponent 加载 + 属性断言 | `test_qml_components*.py`、`test_qml_dialogs_w3.py`（3 文件） |
| L4 端到端页面 | 8 个 view QML | 可见窗口模式加载页面 + Bridge 注入 + 交互（**待补充**） | 暂无 |

---

## 2. 测试模式约束（强制章节）

### 2.1 默认可见模式（强制）

> 本规则为强制约束，违反即视为测试无效。

**正常 GUI 测试禁止使用 offscreen 模式，必须使用可见窗口模式。**

| 模式 | 触发方式 | 适用场景 |
|------|---------|---------|
| **可见模式（默认）** | `GUI_VISIBLE=1` 或不设置 `QT_QPA_PLATFORM` | 正常开发/验收/回归测试 |
| offscreen 模式（受限） | `QT_QPA_PLATFORM=offscreen` | **仅限** CI 无显示器环境、批量回归、用户特别要求时 |

### 2.2 理由

offscreen 模式存在以下缺陷，会掩盖真实问题：
1. **无法验证真实字体渲染**：中文字体回退、emoji 渲染（项目列表/导航大量使用 📂📋🔄📐📊📑⚙️ 等 emoji）在 offscreen 下表现不一致
2. **无法验证 DPI 缩放**：高 DPI 显示器下的字体模糊、布局错位无法暴露
3. **无法验证多显示器场景**：跨屏窗口拖拽、不同 DPI 显示器混用场景缺失
4. **掩盖交互问题**：鼠标 hover、焦点切换、键盘事件在 offscreen 下行为异常

### 2.3 执行约束

- 所有 `tests/qml/` 下的测试默认按可见模式执行
- `conftest.py` 的 `qapp` fixture（session 级 QApplication）不得设置 `QT_QPA_PLATFORM=offscreen`
- 仅当用户明确要求 CI 批量回归时，方可在命令行临时设置 `QT_QPA_PLATFORM=offscreen`，并在测试报告中标注"offscreen 模式，未覆盖字体/DPI/交互"

---

## 3. QML 页面矩阵

> 基于 `main.qml` 侧边栏导航 7 入口 + 独立变量表编辑器，共 8 个 view 页面。

### 3.1 页面总览

| # | 页面名 | QML 文件路径 | 对应 Domain Bridge | 关键 Slot / Property | 现有测试定位 |
|---|--------|-------------|-------------------|---------------------|-------------|
| 1 | 项目列表（默认首页/驾驶舱入口） | `auto_pm/ui/qml/views/ProjectListView.qml` | WorkbenchBridge | `listProjects()` / `refreshProjects()` / `selectProject(id,name)` / `projectModel` / `searchText` / `stackFilter` / `phaseFilter` / `sortField` / `pageSize` / `viewMode(card\|table)` | `test_workbench_bridge.py`（listProjects/refreshProjects 间接覆盖）+ `test_project_list_model.py`（model 层） |
| 2 | 项目工作台（5 Tab） | `auto_pm/ui/qml/views/WorkspaceView.qml` | WorkbenchBridge + ChangeBridge + SpecBridge + DeliveryBridge | `getProjectById(id)` / `listChanges(id)` / `runSpecCheck()` / `getAssetSummary(id)` / `refreshAssetSummary(id)` / `setProject(id,name)` / `currentProjectDetail` / `changesList` / `specCheckResult` / `assetSummary` | `test_workbench_bridge.py`（getProjectById 间接）+ `test_change_bridge.py`（listChanges）+ `test_spec_bridge.py`（runSpecCheck）+ `test_delivery_bridge.py`（getAssetSummary/refreshAssetSummary） |
| 3 | 变更中心 | `auto_pm/ui/qml/views/ChangeCenterView.qml` | ChangeBridge | `listAllChanges()` / `getChangeRequest(num)` / `refreshChanges()` / `selectedChangeNumber` / `selectedChangeDetail` / `statusFilter` / `domainFilter` / `searchText` | `test_change_bridge.py`（listAllChanges/getChangeRequest/refreshChanges 间接） |
| 4 | 规范中心（3 Tab） | `auto_pm/ui/qml/views/SpecCenterView.qml` | SpecBridge | `getSpecOverview()` / `listSpecEntries(domain)` / `runSpecCheck()` / `overviewData` / `currentTab(0\|1\|2)` / `errorMessage` / `specCheckCompleted` 信号 | `test_spec_bridge.py`（3 Slot + 信号全覆盖） |
| 5 | 报告中心（2×2 网格） | `auto_pm/ui/qml/views/ReportView.qml` | DeliveryBridge | `getProjectReport()` / `getChangeReport()` / `projectSummary` / `changeSummary` / `projectOverviewModel` / `phaseModel` / `blModel` / `changeModel` | `test_delivery_bridge.py`（getProjectReport/getChangeReport） |
| 6 | 模板管理 | `auto_pm/ui/qml/views/TemplateView.qml` | SystemBridge | `listTemplates()` / `getTemplateDetail(name)` / `applyTemplate(pid,name)` / `templatesModel` / `selectedTemplate` / `applyResultMessage` / `currentProjectId` | `test_system_bridge.py`（3 Slot 全覆盖） |
| 7 | 系统设置（4 卡片） | `auto_pm/ui/qml/views/SettingsView.qml` | WorkbenchBridge + SystemBridge | `getSettingsSummary()` / `clearCache()` / `rebuildIndex()` / `runPmSessionCheck()` / `settingsData` / `pmSessionData` / `resultMessage` | `test_workbench_bridge.py`（getSettingsSummary/clearCache/rebuildIndex）+ `test_system_bridge.py`（runPmSessionCheck） |
| 8 | 变量表编辑器 | `auto_pm/ui/qml/views/VarTableEditorView.qml` | （无 Bridge，直接用 `varTableModel` context property） | `selectedRows` / `lastValidationError` / 单元格编辑 / 批量操作 / 撤销重做 | `test_var_table_model.py`（model 层全覆盖） |

### 3.2 辅助资源矩阵

| 资源类型 | 文件数 | 路径 | 现有测试 |
|---------|-------|------|---------|
| 主题单例 | 1 | `auto_pm/ui/qml/theme/Theme.qml` | `test_qml_components.py::test_theme_singleton_loadable`（间接） |
| 基础组件 | 5 | `components/Card.qml` / `Badge.qml` / `TabBar.qml` / `PrimaryButton.qml` / `Dialog.qml` | `test_qml_components.py`（11 用例） |
| W3 复杂组件 | 4 | `components/ApprovalTimeline.qml` / `PropagationView.qml` / `StatusMachineView.qml` / `PhaseProgress.qml` | `test_qml_components_w3.py`（14 用例） |
| W3 对话框 | 8 | `dialogs/NewProjectWizard.qml` / `NewChangeDialog.qml`（V0.9.2 已对齐后端 BUSINESS_NATURES）/ `ProjectSettingsDialog.qml` / `SyncCacheDialog.qml` / `ImportProjectDialog.qml` / `AboutDialog.qml` / `ReportDialog.qml` / `GlobalSettingsDialog.qml` | `test_qml_dialogs_w3.py`（17 用例） |
| 主入口 | 1 | `auto_pm/ui/qml/main.qml` | 暂无（待 L4 端到端覆盖） |

### 3.3 Bridge → Facade → Service 装配链

装配入口：`auto_pm/ui/qml_main_window.py::run_qml_gui()` → `FacadeRegistry.initialize()` → 5 个 Bridge 构造 → `engine.rootContext().setContextProperty()` 注入。

| Bridge | context property 名 | Facade | 装配位置 |
|--------|---------------------|--------|---------|
| WorkbenchBridge | `workbenchBridge` | WorkbenchFacade（dashboard_service + project_service + asset_summary_service） | `registry.py:44` |
| ChangeBridge | `changeBridge` | ChangeFacade（change_service） | `registry.py:50` |
| SpecBridge | `specBridge` | SpecFacade（spec_check_service + spec_center_service） | `registry.py:54` |
| DeliveryBridge | `deliveryBridge` | DeliveryFacade（doc_refresh_service + report_service + asset_summary_service + project_service） | `registry.py:59` |
| SystemBridge | `systemBridge` | SystemFacade（pm_session_service + template_service + project_service） | `registry.py:66` |
| ProjectListModel | `projectModel` | —（QAbstractListModel） | `qml_main_window.py:125` |
| VarTableModel | `varTableModel` | —（QAbstractListModel） | 注：main.qml 未注入，VarTableEditorView 独立使用 |

---

## 4. 状态覆盖矩阵

> 对每个页面标注 6 状态覆盖情况。状态定义：
> - **idle**：页面加载前初始状态（Component.onCompleted 触发前）
> - **loading**：数据加载中（注：QML 同步调用 Bridge Slot，无显式 loading 态，为同步阻塞）
> - **success**：数据正常返回且有数据，正常渲染
> - **empty**：数据返回成功但为空（filteredModel.count===0 / 暂无数据提示）
> - **warning**：部分失败或告警（error_count>0 / warning_count>0 / is_healthy=false）
> - **error**：失败（errorMessage!=="" / 三重守卫失败 / error_count===-1）

### 4.1 页面状态覆盖矩阵

| 页面 | idle | loading | success | empty | warning | error | 现有覆盖缺口 |
|------|------|---------|---------|-------|---------|-------|-------------|
| 项目列表 | △（短暂） | ✗（同步阻塞，无显式态） | ✅（listProjects 返回数据） | ✅（filteredModel.count===0 提示"暂无项目"） | N/A | △（bridge 未注入时 applyFilters 空跑） | 缺 loading/error 显式态；缺 bridge=None 时 ProjectListView 行为 |
| 项目工作台 | △ | ✗ | ✅（getProjectById 返回详情） | △（changesList 为空时提示"暂无变更"） | ✅（specCheckResult.warning_count>0） | ✅（specCheckResult.error_count===-1） | 缺 loading/empty 全 Tab 覆盖；缺 assetSummary 空态 |
| 变更中心 | △ | ✗ | ✅（listAllChanges 返回） | ✅（filteredModel.count===0 提示"暂无变更"） | N/A | △（ChangeService 未启用时 loadChanges 空跑） | 缺 loading/error 显式态 |
| 规范中心 | △ | ✗ | ✅（getSpecOverview 返回） | ✅（entriesModel.count===0） | ✅（health_summary.error_count>0 / warning_count>0） | ✅（errorMessage!=="" 三重守卫） | 缺 loading 显式态 |
| 报告中心 | △ | ✗ | ✅（getProjectReport 返回） | △（total=0 时柱状图全 0） | N/A | ✅（errorMessage="ReportService 未启用"） | 缺 empty 显式断言；缺 loading |
| 模板管理 | △ | ✗ | ✅（listTemplates 返回） | ✅（templatesModel.count===0 提示"暂无可用模板"） | N/A | ✅（errorMessage="TemplateService 未启用"） | 缺 loading |
| 系统设置 | △ | ✗ | ✅（getSettingsSummary 返回） | △（project_count=0） | ✅（pmSessionData.is_healthy=false） | ✅（errorMessage="QmlBridge 未注入"） | 缺 loading；缺 clearCache/rebuildIndex 失败态 |
| 变量表编辑器 | △ | ✗ | ✅（setEntries 后 rowCount>0） | ✅（rowCount===0） | △（lastValidationError 提示） | N/A | 缺 loading；缺万行虚拟化压力测试 |

**图例：** ✅=已覆盖 / △=部分覆盖 / ✗=未覆盖 / N/A=不适用

### 4.2 状态覆盖缺口分析

**主要缺口（按优先级）：**
1. **loading 态全缺**：QML 同步调用 Bridge Slot，无异步 loading 指示器。建议 L4 端到端测试中验证"同步阻塞期间 UI 不卡死"（processEvents 可推进）
2. **error 态显式断言不足**：现有 Bridge 测试覆盖了 `facade=None` 降级，但 QML 页面层的"三重守卫"分支（`typeof xxxBridge === "undefined" || xxxBridge === null || !xxxBridge.hasService`）无端到端验证
3. **empty 态渲染未断言**：filteredModel.count===0 时的"暂无数据"提示文本未在测试中断言
4. **warning 态仅规范中心覆盖**：SpecCenterView 的 health_summary.error_count>0 有间接覆盖，但 WorkspaceView 检查 Tab 的 warning_count>0 渲染未验证

---

## 5. 关键交互链路测试

> 基于 Bridge 实际 Slot 列出的 6 条关键端到端链路。每条链路标注：触发 Slot、预期 DTO、现有测试用例定位。

### 5.1 链路清单

#### 链路 1：驾驶舱加载（getDashboardSummary / getDashboardSnapshot）

| 项目 | 内容 |
|------|------|
| 触发 Slot | `WorkbenchBridge.getDashboardSummary()` |
| 后端方法 | `WorkbenchFacade.get_dashboard_snapshot()` → DashboardService |
| 预期 DTO | `DashboardSnapshotDTO`（total_projects / phase_counts / open_change_count / failed_check_project_count / not_applicable_project_count / recent_activities / risk_hints / failed_check_project_ids / not_applicable_project_ids） |
| QML 消费方 | 注：main.qml 未直接调用 getDashboardSummary，但 WorkbenchBridge 已暴露该 Slot，供驾驶舱/状态栏扩展使用 |
| 现有测试 | `test_workbench_bridge.py::test_workbench_bridge_dashboard_summary`（验证返回 dict 字段）<br>`test_workbench_bridge.py::test_workbench_bridge_no_facade`（验证降级返回 {}） |
| 缺口 | 无端到端页面渲染验证；驾驶舱数据未接入 main.qml 状态栏（仅 projectModel.rowCount() 显示项目数） |

#### 链路 2：打开项目工作台（openProject → getProjectWorkspace）

| 项目 | 内容 |
|------|------|
| 触发 Slot | `WorkbenchBridge.selectProject(project_id, project_name)` → emit `projectSelected` 信号 → main.qml Connections 接收 → `workspaceView.setProject(id, name)` → `getProjectById(id)` |
| 后端方法 | `WorkbenchFacade.get_project_workspace(project_id)` → ProjectWorkspaceDTO |
| 预期 DTO | `ProjectWorkspaceDTO`（project_id / summary / asset_summary / document_status / vartable_status / pending_actions），Bridge 返回 `summary` dict |
| QML 消费方 | WorkspaceView.setProject → currentProjectDetail / changesList / specCheckResult / assetSummary |
| 现有测试 | `test_workbench_bridge.py::test_workbench_bridge_list_projects`（listProjects 链路）<br>`test_workbench_bridge.py::test_workbench_bridge_no_facade`（getProjectById 降级） |
| 缺口 | selectProject 信号 emit 未测试；setProject → 多 Tab 联动加载未端到端验证 |

#### 链路 3：创建变更单（createChange）

| 项目 | 内容 |
|------|------|
| 触发 Slot | `ChangeBridge.createChange(command_dict)` |
| 后端方法 | `ChangeFacade.create_change_request(CreateChangeCommand)` → ChangeService |
| 预期 DTO | `ChangeRequestDTO`（change_number / project_id / status="draft" / background / necessity / impact_scope / risk_level / mitigation / propagation_chain / sections 等） |
| QML 消费方 | 注：createChange Slot 已暴露，但 QML 端 NewChangeDialog 尚未接入（TODO M5） |
| 现有测试 | `test_change_bridge.py::test_change_bridge_create_change`（验证 CreateChangeCommand 透传 + impact_scope 透传）<br>`test_change_bridge.py::test_change_bridge_create_change_failure`（Facade 失败返回 {success:False}）<br>`test_change_bridge.py::test_change_bridge_no_facade`（降级返回 {success:False, message:"未初始化"}） |
| 缺口 | NewChangeDialog → createChange 端到端未联通（QML 端 TODO M5） |

#### 链路 4：规范检查（runSpecCheck）

| 项目 | 内容 |
|------|------|
| 触发 Slot | `SpecBridge.runSpecCheck()` |
| 后端方法 | `SpecFacade.run_spec_check()` → CheckService |
| 预期 DTO | `SpecCheckResultDTO`（error_count / warning_count / info_count / exit_code / results） |
| 信号 | `specCheckCompleted(int error_count, int warning_count, int info_count)` |
| QML 消费方 | SpecCenterView.runChecks() / WorkspaceView.loadCheckTab() |
| 现有测试 | `test_spec_bridge.py::test_spec_bridge_run_check`（验证 dict 字段 + QSignalSpy 验证信号 emit 1 次 + 参数 (2,3,1)）<br>`test_spec_bridge.py::test_spec_bridge_run_check_failure`（失败时不 emit 信号，返回 {error_count:-1}）<br>`test_spec_bridge.py::test_spec_bridge_no_facade`（降级） |
| 缺口 | SpecCenterView 检查 Tab 的 results 列表渲染未端到端验证 |

#### 链路 5：文档刷新（refreshProjectDocs）

| 项目 | 内容 |
|------|------|
| 触发 Slot | `DeliveryBridge.refreshProjectDocs(project_id, dry_run)` |
| 后端方法 | `DeliveryFacade.refresh_project_docs(project_id, dry_run)` → DocRefreshService |
| 预期 DTO | `RefreshProjectDocsResultDTO`（project_id / dry_run / updated / refreshed_files / issues） |
| QML 消费方 | 注：refreshProjectDocs Slot 已暴露，QML 端 WorkspaceView 文档 Tab 为占位（W3 未实现），TODO 接入 |
| 现有测试 | `test_delivery_bridge.py::test_delivery_bridge_refresh_project_docs`（验证 project_id/dry_run 透传 + refreshed_files 字段）<br>`test_delivery_bridge.py::test_delivery_bridge_no_facade`（降级返回 {success:False, message:"未初始化"}） |
| 缺口 | QML 端文档 Tab 未实现，端到端不可走通 |

#### 链路 6：资产摘要（listAssetSummaries / getAssetSummary）

| 项目 | 内容 |
|------|------|
| 触发 Slot | `DeliveryBridge.getAssetSummary(project_id)` / `DeliveryBridge.refreshAssetSummary(project_id)` |
| 后端方法 | `DeliveryFacade.get_asset_summary(project_id)` / `refresh_asset_summary(project_id)` → AssetSummaryService |
| 预期 DTO | `AssetSummaryDTO`（data: {status / total_issues / io_points / program_blocks / communications / issue_messages}）<br>`RefreshAssetSummaryResultDTO`（result: dict） |
| QML 消费方 | WorkspaceView.loadAssetSummary()（仅 PLC 项目，stack==="plc" 时调用）+ 概览 Tab 资产汇总卡片刷新按钮 |
| 现有测试 | `test_delivery_bridge.py::test_delivery_bridge_get_asset_summary`（验证 project_id 透传 + data 字段）<br>`test_delivery_bridge.py::test_delivery_bridge_refresh_asset_summary`（验证 project_id 透传 + result 字段）<br>`test_delivery_bridge.py::test_delivery_bridge_no_facade`（降级） |
| 缺口 | WorkspaceView.loadAssetSummary 的"仅 PLC 项目"分支未端到端验证；assetSummary 空态/错误态渲染未验证 |

### 5.2 链路覆盖汇总

| 链路 | Bridge 层覆盖 | QML 端到端覆盖 | 整体状态 |
|------|-------------|---------------|---------|
| 1 驾驶舱加载 | ✅ | ✗（main.qml 未消费） | Bridge 就绪，QML 待接入 |
| 2 打开项目工作台 | ✅ | △（selectProject 信号未测） | Bridge 就绪，QML 部分 |
| 3 创建变更单 | ✅ | ✗（NewChangeDialog 未接入） | Bridge 就绪，QML TODO M5 |
| 4 规范检查 | ✅ | △（检查 Tab 渲染未测） | Bridge 就绪，QML 部分 |
| 5 文档刷新 | ✅ | ✗（文档 Tab 占位） | Bridge 就绪，QML 待实现 |
| 6 资产摘要 | ✅ | △（仅 PLC 分支未测） | Bridge 就绪，QML 部分 |

---

## 6. 测试执行方式

### 6.1 执行命令

#### 6.1.1 可见模式（默认，推荐）

```bash
# 激活 venv（强制，见 project-rule.md）
& "c:\Users\fubai\Desktop\My_Workspace\.venv\Scripts\Activate.ps1"

# 全量 QML 测试（默认可见模式）
pytest tests/qml/ -m gui --no-cov -q

# 指定单个 Bridge 测试
pytest tests/qml/test_workbench_bridge.py -m gui --no-cov -q

# 指定单个用例
pytest tests/qml/test_spec_bridge.py::test_spec_bridge_run_check -m gui --no-cov -q
```

#### 6.1.2 offscreen 模式（仅 CI / 批量回归，需用户特别要求）

```bash
# 仅 CI 无显示器环境或用户特别要求时使用
$env:QT_QPA_PLATFORM="offscreen"; pytest tests/qml/ -m gui --no-cov -q

# Linux/macOS 等效
QT_QPA_PLATFORM=offscreen pytest tests/qml/ -m gui --no-cov -q
```

> ⚠️ offscreen 模式必须在测试报告中标注"未覆盖字体渲染/DPI/交互"，不得作为唯一回归手段。

### 6.2 marker 使用

`pyproject.toml` 已注册 6 个 marker：

| marker | 用途 | GUI 测试适用 |
|--------|------|-------------|
| `gui` | GUI 全功能自动化测试 | ✅ QML 测试主标记 |
| `cli` | CLI 命令测试 | ✗ 不适用 |
| `smoke` | 冒烟测试（核心功能快速验证） | △ 可用于 8 个页面加载冒烟 |
| `unit` | 单元测试 | ✅ Bridge/Model 层标记 |
| `integration` | 集成测试 | △ L4 端到端页面标记 |
| `slow` | 慢速测试（>5s） | △ 万行变量表/全量回归标记 |

**建议标记策略：**
- L1/L2/L3 层测试标记 `@pytest.mark.gui` + `@pytest.mark.unit`
- L4 端到端页面测试标记 `@pytest.mark.gui` + `@pytest.mark.integration`
- 全量回归中耗时>5s 的用例追加 `@pytest.mark.slow`

### 6.3 执行耗时预估

| 范围 | 预估耗时 | 说明 |
|------|---------|------|
| 单个 Bridge 测试文件 | <2s | Mock Facade，无 IO |
| 单个 Model 测试文件 | <3s | 内存数据，processEvents |
| 单个组件/对话框测试文件 | <5s | QQmlEngine 加载 + 属性断言 |
| `tests/qml/` 全量（现有 11 文件） | 15-30s | 约 110 用例 |
| L4 端到端页面（待补充） | 60-120s | 8 页面 × 6 状态 × 交互 |
| **全量 GUI 回归（含 L4）** | **90-150s** | 可见模式 + processEvents |

### 6.4 venv 激活约束

按 `project-rule.md` 强制规则，执行任何 Python/pytest 命令前必须先激活工作空间虚拟环境：

```powershell
& "c:\Users\fubai\Desktop\My_Workspace\.venv\Scripts\Activate.ps1"
python --version  # 验证指向 .venv
pip --version     # 验证指向 .venv
```

未激活 venv 时禁止运行 `pytest`、`auto-pm gui` 等命令。

---

## 7. 现有测试资产映射

> `tests/qml/` 下现有 11 个测试文件，约 110 个用例。

### 7.1 测试文件清单

| # | 测试文件 | 用例数 | 覆盖范围 | 测试层 |
|---|---------|-------|---------|-------|
| 1 | `conftest.py` | —（fixture） | `qapp`（session 级 QApplication）/ `sample_projects`（3 个 ProjectInfo）/ `mock_project_service`（MagicMock） | 共享 |
| 2 | `test_workbench_bridge.py` | 3 | listProjects / getDashboardSummary / no_facade 降级（listProjects→[] / getDashboardSummary→{} / getSettingsSummary→{} / clearCache→{success:False} / rebuildIndex→{success:False}） | L1 Bridge |
| 3 | `test_change_bridge.py` | 8 | listAllChanges / getChangeRequest / createChange（CreateChangeCommand 透传 + impact_scope）/ transitionChange（TransitionChangeCommand 透传）/ getChangeTimeline / getChangeValidationSummary / no_facade 降级 / create_change_failure | L1 Bridge |
| 4 | `test_spec_bridge.py` | 5 | runSpecCheck（dict + specCheckCompleted 信号 QSignalSpy）/ getSpecOverview / listSpecEntries（filter_domain 透传）/ no_facade 降级 / run_check_failure（失败不 emit 信号） | L1 Bridge |
| 5 | `test_delivery_bridge.py` | 8 | getProjectReport / getChangeReport / getSpecReport / getScanReport / refreshProjectDocs（project_id+dry_run 透传）/ refreshAssetSummary / getAssetSummary / no_facade 降级 | L1 Bridge |
| 6 | `test_system_bridge.py` | 7 | listTemplates / getTemplatePath / getTemplateDetail / getPmSessionView / runPmSessionCheck / applyTemplate（project_id+template_name 透传）/ no_facade 降级 | L1 Bridge |
| 7 | `test_project_list_model.py` | 10 | 初始空态 / setProjects 填充 / setProjects([]) 清空 / roleNames 7 映射 / role-field 对齐 / data 各 role / PLC 项目 stack / 无效 index / 越界 / clear / getProjectAt 越界 | L2 Model |
| 8 | `test_change_list_model.py` | 10 | 初始空态 / setChanges 填充 / setChanges([]) 清空 / roleNames 10 映射 / role-field 对齐 / data 各 role / PLC 变更 domain / 无效 index / 越界 / clear / getChangeAt 越界 | L2 Model |
| 9 | `test_var_table_model.py` | 30+ | COLUMNS 8 列 / UndoStack 基本 + redo 清空 + max_size 100 + clear / 字段校验（address/station/tag/comment）/ setEntries dict+list / clear / data 索引列 / setCell 基本 + 只读列 + 校验 + 无变化 + undo 入栈 / batchUpdate 多行 + 跳过同值 + 校验 + 只读列 + 每行 undo / undo+redo 基本 + canUndo/canRedo + 25 步 + 空栈 + setEntries 清栈 / getCell 越界 + 索引列 / QML Slot rowCountQml+columnCountQml+headerText | L2 Model |
| 10 | `test_qml_components.py` | 11 | Card（默认+设置）/ Badge（默认+设置）/ TabBar（默认+设置 tabs+设置 currentTabIndex）/ PrimaryButton（默认+设置）/ Dialog（默认+open/close+设置 title）/ Theme 单例加载 | L3 组件 |
| 11 | `test_qml_components_w3.py` | 14 | ApprovalTimeline（默认+设置 approvals+结论映射）/ PropagationView（默认+设置 nodes+尺寸）/ StatusMachineView（默认状态+7 状态序+9 状态标签+设置+尺寸）/ PhaseProgress（默认阶段+4 阶段+标签+设置+尺寸） | L3 组件 |
| 12 | `test_qml_dialogs_w3.py` | 17 | NewProjectWizard（默认+设置 step+设置 projectId）/ NewChangeDialog（默认+设置）/ ProjectSettingsDialog（默认+设置 version）/ SyncCacheDialog（默认+设置 progress）/ ImportProjectDialog（默认+设置 path）/ AboutDialog（默认+设置 version）/ ReportDialog（默认+设置 outputPath）/ GlobalSettingsDialog（默认+设置 workspace+设置 refreshInterval）/ 8 对话框全加载验证 | L3 对话框 |

### 7.2 资产覆盖热力图

| 测试层 | Bridge | Model | 组件 | 对话框 | 页面端到端 |
|-------|--------|-------|------|--------|-----------|
| L1 Bridge 单元 | ✅ 5/5（31 用例） | — | — | — | — |
| L2 Model 单元 | — | ✅ 3/3（50+ 用例） | — | — | — |
| L3 组件加载 | — | — | ✅ 9/10（25 用例，缺 BarRow） | ✅ 8/8（17 用例） | — |
| L4 端到端页面 | — | — | — | — | ✗ 0/8（**待补充**） |

**BarRow.qml 缺口：** `test_qml_components.py` 未覆盖 `components/BarRow.qml`（ReportView 使用的柱状图行组件），建议补充。

---

## 8. 测试用例清单

> 按页面/链路列出具体测试用例。优先级：P0=阻塞性 / P1=关键 / P2=重要 / P3=补充。

### 8.1 项目列表页（ProjectListView）

| 用例ID | 操作 | 预期结果 | 优先级 | 现有/待补 |
|--------|------|---------|-------|----------|
| TC-PL-001 | bridge 可用时 listProjects() 返回 N 个项目 | projectModel.rowCount()===N，displayModel 渲染 N 条 | P0 | 现有（model 层） |
| TC-PL-002 | bridge=None 时 ProjectListView.onCompleted | applyFilters 空跑，displayModel.count===0，显示"暂无项目匹配筛选条件" | P1 | 待补 |
| TC-PL-003 | 搜索框输入"SW"，stackFilter="all" | filteredItems 仅含 name/project_id 含"SW"的项目 | P1 | 待补 |
| TC-PL-004 | stackFilter="plc" | filteredItems 仅含 stack==="plc" 项目 | P1 | 待补 |
| TC-PL-005 | phaseFilter="production" | filteredItems 仅含 phase==="production" 项目 | P1 | 待补 |
| TC-PL-006 | sortField="version" + sortDir="desc" | filteredItems 按版本号降序排列 | P2 | 待补 |
| TC-PL-007 | pageSize=10，currentPage 翻页 | 第 2 页显示第 11-20 条 | P2 | 待补 |
| TC-PL-008 | viewMode="table" 切换 | tableView 可见，cardListView 不可见 | P2 | 待补 |
| TC-PL-009 | 点击项目卡片 | emit projectClicked(id,name) + workbenchBridge.selectProject(id,name) | P0 | 待补 |
| TC-PL-010 | 点击"刷新"按钮 | workbenchBridge.refreshProjects() + listProjects() 重新加载 | P1 | 待补 |
| TC-PL-011 | 空状态：filteredModel.count===0 | 显示"暂无项目匹配筛选条件"文本 | P2 | 待补 |

### 8.2 项目工作台页（WorkspaceView）

| 用例ID | 操作 | 预期结果 | 优先级 | 现有/待补 |
|--------|------|---------|-------|----------|
| TC-WS-001 | setProject(id,name) 加载项目 | currentProjectDetail 含 project_id/name/stack/phase/version | P0 | 待补（Bridge 层间接） |
| TC-WS-002 | 概览 Tab：currentProjectDetail 渲染 | 基本信息/PLC 信息/项目分类/描述/路径卡片正确显示 | P1 | 待补 |
| TC-WS-003 | 变更 Tab：changeBridge.listChanges(id) | changesList 渲染变更单列表，空时显示"该项目暂无变更单" | P1 | 待补（Bridge 层间接） |
| TC-WS-004 | 检查 Tab：specBridge.runSpecCheck() | specCheckResult 含 error_count/warning_count，results 列表渲染 | P0 | 待补（Bridge 层间接） |
| TC-WS-005 | 检查 Tab：specBridge=None | specCheckResult={error_count:-1,message:"未启用规范检查服务"} | P1 | 待补 |
| TC-WS-006 | 文档 Tab | 显示"W3 实现"占位文本 | P3 | 待补 |
| TC-WS-007 | 变量表 Tab | 显示"W3 实现"占位文本 | P3 | 待补 |
| TC-WS-008 | PLC 项目资产汇总：loadAssetSummary() | assetSummary 含 status/io_points/program_blocks，仅 stack==="plc" 时加载 | P1 | 待补（Bridge 层间接） |
| TC-WS-009 | 非 PLC 项目资产汇总 | assetSummary={}，资产汇总卡片不显示 | P1 | 待补 |
| TC-WS-010 | 点击"刷新"资产汇总按钮 | deliveryBridge.refreshAssetSummary(id)，assetSummary 更新 | P1 | 待补 |
| TC-WS-011 | 点击"重新运行检查"按钮 | loadCheckTab() 重新调用 runSpecCheck | P2 | 待补 |

### 8.3 变更中心页（ChangeCenterView）

| 用例ID | 操作 | 预期结果 | 优先级 | 现有/待补 |
|--------|------|---------|-------|----------|
| TC-CC-001 | loadChanges() 加载变更列表 | filteredModel 渲染变更单，显示编号/标题/状态/领域 | P0 | 待补（Bridge 层间接） |
| TC-CC-002 | changeBridge=None 时 loadChanges | filteredModel.clear()，显示"暂无变更" | P1 | 待补 |
| TC-CC-003 | statusFilter="approved" | filteredModel 仅含 status==="approved" | P1 | 待补 |
| TC-CC-004 | domainFilter="PLC" | filteredModel 仅含 domain==="PLC" | P1 | 待补 |
| TC-CC-005 | 搜索"CHG-2026" | filteredModel 仅含 change_number/title/project_id 含关键词 | P2 | 待补 |
| TC-CC-006 | 点击变更单 | selectedChangeNumber 更新，loadChangeDetail 加载详情面板 | P0 | 待补 |
| TC-CC-007 | 详情面板渲染 | 显示编号/状态/领域/紧急度/基本信息/背景/必要性/风险评估/参考依据/文件路径卡片 | P1 | 待补 |
| TC-CC-008 | 点击"刷新"按钮 | changeBridge.refreshChanges() + loadChanges() | P1 | 待补 |
| TC-CC-009 | 空状态：filteredModel.count===0 | 显示"暂无变更" | P2 | 待补 |

### 8.4 规范中心页（SpecCenterView）

| 用例ID | 操作 | 预期结果 | 优先级 | 现有/待补 |
|--------|------|---------|-------|----------|
| TC-SC-001 | 概览 Tab：getSpecOverview() | overviewData 含 spec_count/domain_counts/lifecycle_counts/health_summary | P0 | 待补（Bridge 层✅） |
| TC-SC-002 | 索引 Tab：listSpecEntries(domain) | entriesModel 渲染规范条目列表 | P1 | 待补（Bridge 层✅） |
| TC-SC-003 | 索引 Tab：搜索 spec_id | QML 端过滤，仅显示匹配条目 | P2 | 待补 |
| TC-SC-004 | 索引 Tab：domainCombo 切换 | loadEntries 重新加载指定域 | P2 | 待补 |
| TC-SC-005 | 检查 Tab：点击"运行检查" | runSpecCheck()，checkResultsModel 渲染 results | P0 | 待补（Bridge 层✅） |
| TC-SC-006 | specBridge=None | errorMessage="SpecCenterAdapter 未启用"，Tab 内容不可见 | P1 | 待补 |
| TC-SC-007 | 健康摘要：error_count>0 | 错误数显示红色（Theme.error） | P2 | 待补 |
| TC-SC-008 | 空状态：entriesModel.count===0 | 显示"暂无规范条目" | P2 | 待补 |
| TC-SC-009 | 点击"刷新"按钮 | loadOverview() + loadEntries() | P1 | 待补 |

### 8.5 报告中心页（ReportView）

| 用例ID | 操作 | 预期结果 | 优先级 | 现有/待补 |
|--------|------|---------|-------|----------|
| TC-RC-001 | loadData() 加载报告 | projectSummary="总项目数: N"，changeSummary="总变更: M" | P0 | 待补（Bridge 层间接） |
| TC-RC-002 | 项目概览卡片 | by_stack 柱状图渲染 plc/python/unknown | P1 | 待补 |
| TC-RC-003 | 阶段分布卡片 | by_phase 柱状图渲染 developing/commissioning/production/archived | P1 | 待补 |
| TC-RC-004 | 业务线分布卡片 | by_business_line 柱状图渲染 SW/DJ/ZD/XT/WX | P1 | 待补 |
| TC-RC-005 | 变更统计卡片 | by_status 柱状图渲染各状态 | P1 | 待补 |
| TC-RC-006 | deliveryBridge=None | errorMessage="ReportService 未启用"，卡片网格不可见 | P1 | 待补 |
| TC-RC-007 | 空数据：total=0 | 柱状图全 0，projectSummary="总项目数: 0" | P2 | 待补 |
| TC-RC-008 | 点击"刷新"按钮 | loadData() 重新加载 | P1 | 待补 |

### 8.6 模板管理页（TemplateView）

| 用例ID | 操作 | 预期结果 | 优先级 | 现有/待补 |
|--------|------|---------|-------|----------|
| TC-TM-001 | loadData() 加载模板 | templatesModel 渲染模板卡片，显示 name/version/stack/usage_count/description | P0 | 待补（Bridge 层间接） |
| TC-TM-002 | systemBridge=None | errorMessage="TemplateService 未启用" | P1 | 待补 |
| TC-TM-003 | 空状态：templatesModel.count===0 | 显示"暂无可用模板" | P2 | 待补 |
| TC-TM-004 | 点击"应用模板到项目" | updateDialog 打开，显示模板名 + 目标项目 | P1 | 待补 |
| TC-TM-005 | 未选项目时应用模板 | 显示"⚠️ 未选择项目"提示 | P1 | 待补 |
| TC-TM-006 | 确认应用：systemBridge.applyTemplate(pid,name) | applyResultMessage="✅ 模板应用成功" | P1 | 待补（Bridge 层✅） |
| TC-TM-007 | 应用失败：res.message | applyResultMessage="❌ 失败: ..." | P2 | 待补 |
| TC-TM-008 | 点击"刷新"按钮 | loadData() | P2 | 待补 |

### 8.7 系统设置页（SettingsView）

| 用例ID | 操作 | 预期结果 | 优先级 | 现有/待补 |
|--------|------|---------|-------|----------|
| TC-ST-001 | loadData() 加载设置 | settingsData 含 workspace_root/db_path/project_count/last_sync/db_available | P0 | 待补（Bridge 层间接） |
| TC-ST-002 | PM_SESSION 健康：runPmSessionCheck() | pmSessionData 含 file_path/file_size_kb/total_lines/is_healthy | P1 | 待补（Bridge 层✅） |
| TC-ST-003 | systemBridge=None | pmSessionData={error:"未启用 PM_SESSION 服务"} | P1 | 待补 |
| TC-ST-004 | 点击"清除缓存" → 确认 | workbenchBridge.clearCache()，resultMessage 显示 message | P1 | 待补（Bridge 层✅） |
| TC-ST-005 | 点击"重建索引" → 确认 | workbenchBridge.rebuildIndex()，resultMessage 显示 message+项目数+变更数 | P1 | 待补（Bridge 层✅） |
| TC-ST-006 | db_available=false | "清除缓存"/"重建索引"按钮 enabled=false | P2 | 待补 |
| TC-ST-007 | 点击"刷新检查"按钮 | loadData() 重新加载 | P2 | 待补 |
| TC-ST-008 | bridge=None | errorMessage="QmlBridge 未注入" | P1 | 待补 |

### 8.8 变量表编辑器页（VarTableEditorView）

| 用例ID | 操作 | 预期结果 | 优先级 | 现有/待补 |
|--------|------|---------|-------|----------|
| TC-VT-001 | varTableModel.setEntries(dict) | rowCount 正确，8 列渲染 | P0 | 现有（model 层✅） |
| TC-VT-002 | 双击单元格编辑 | 进入编辑态，校验通过则更新 | P1 | 待补 |
| TC-VT-003 | 地址列空值校验 | lastValidationError 提示，setCell 返回 False | P1 | 现有（model 层✅） |
| TC-VT-004 | 批量改类型 | batchUpdate 多行同列 | P1 | 现有（model 层✅） |
| TC-VT-005 | Ctrl+Z 撤销 | undo() 还原上一动作 | P0 | 现有（model 层✅） |
| TC-VT-006 | Ctrl+Y 重做 | redo() 重做 | P0 | 现有（model 层✅） |
| TC-VT-007 | 25 步撤销链 | 完整回退到初始值 | P1 | 现有（model 层✅） |
| TC-VT-008 | 万行数据虚拟化 | 10000 行 TableView 流畅滚动 | P2 | 待补（性能） |

### 8.9 关键链路用例（跨页面）

| 用例ID | 链路 | 操作 | 预期结果 | 优先级 | 现有/待补 |
|--------|------|------|---------|-------|----------|
| TC-FLOW-001 | 驾驶舱加载 | WorkbenchBridge.getDashboardSummary() | 返回 DashboardSnapshotDTO dict，含 total_projects/phase_counts 等 9 字段 | P0 | 现有（Bridge✅） |
| TC-FLOW-002 | 打开项目工作台 | selectProject(id,name) → emit projectSelected → setProject | currentProjectId/currentProjectName 更新，currentPage="workspace" | P0 | 待补（信号未测） |
| TC-FLOW-003 | 创建变更单 | createChange(cmd_dict) | 返回 ChangeRequestDTO dict，status="draft"，changesChanged 信号 emit | P0 | 现有（Bridge✅） |
| TC-FLOW-004 | 规范检查 | runSpecCheck() | 返回 SpecCheckResultDTO dict，specCheckCompleted 信号 emit (error,warning,info) | P0 | 现有（Bridge✅） |
| TC-FLOW-005 | 文档刷新 | refreshProjectDocs(id,dry_run) | 返回 RefreshProjectDocsResultDTO dict，含 refreshed_files/issues | P1 | 现有（Bridge✅） |
| TC-FLOW-006 | 资产摘要 | getAssetSummary(id) | 返回 AssetSummaryDTO dict，含 data.status/io_points 等 | P1 | 现有（Bridge✅） |
| TC-FLOW-007 | 变更单流转 | transitionChange(cmd_dict) | 返回 ChangeRequestDTO dict，status 更新，详情缓存失效 | P1 | 现有（Bridge✅） |
| TC-FLOW-008 | 模板应用 | applyTemplate(pid,name) | 返回 ApplyTemplateResultDTO dict，含 project_id/template_name/result | P1 | 现有（Bridge✅） |
| TC-FLOW-009 | PM_SESSION 检查 | runPmSessionCheck() | 返回 PmSessionCheckResultDTO dict，含 data.is_healthy/warnings | P1 | 现有（Bridge✅） |
| TC-FLOW-010 | 重建索引 | rebuildIndex() | 返回 RebuildIndexResultDTO dict，含 projects_found/changes_found/message | P1 | 现有（Bridge✅） |

### 8.10 降级与异常用例

| 用例ID | 场景 | 预期结果 | 优先级 | 现有/待补 |
|--------|------|---------|-------|----------|
| TC-ERR-001 | WorkbenchBridge facade=None | listProjects→[] / getDashboardSummary→{} / clearCache→{success:False,message:"未初始化"} | P0 | 现有✅ |
| TC-ERR-002 | ChangeBridge facade=None | listAllChanges→[] / createChange→{success:False} / transitionChange→{success:False} | P0 | 现有✅ |
| TC-ERR-003 | SpecBridge facade=None | runSpecCheck→{error_count:-1,message:"未初始化"} / getSpecOverview→{} / listSpecEntries→[] | P0 | 现有✅ |
| TC-ERR-004 | DeliveryBridge facade=None | 4 reports→{} / refreshProjectDocs→{success:False} / refreshAssetSummary→{success:False} / getAssetSummary→{} | P0 | 现有✅ |
| TC-ERR-005 | SystemBridge facade=None | listTemplates→[] / getTemplatePath→"" / getTemplateDetail→{} / runPmSessionCheck→{success:False} / applyTemplate→{success:False} | P0 | 现有✅ |
| TC-ERR-006 | createChange Facade 失败 | 返回 {success:False,message:"Validation failed"} | P1 | 现有✅ |
| TC-ERR-007 | runSpecCheck Facade 失败 | 返回 {error_count:-1,message:"Spec check failed"}，不 emit 信号 | P1 | 现有✅ |

### 8.11 用例统计

| 分类 | 用例数 | 现有 | 待补 |
|------|-------|------|------|
| 项目列表 | 11 | 1 | 10 |
| 项目工作台 | 11 | 0 | 11 |
| 变更中心 | 9 | 0 | 9 |
| 规范中心 | 9 | 0 | 9 |
| 报告中心 | 8 | 0 | 8 |
| 模板管理 | 8 | 0 | 8 |
| 系统设置 | 8 | 0 | 8 |
| 变量表编辑器 | 8 | 6 | 2 |
| 关键链路 | 10 | 10 | 0 |
| 降级异常 | 7 | 7 | 0 |
| **合计** | **89** | **24** | **65** |

**结论：** Bridge/Model 层覆盖良好（24 用例），QML 页面端到端覆盖缺口大（65 待补），L4 层为后续补强重点。

---

## 9. 补强建议与优先级

### 9.1 P0 优先补强（阻塞性）

1. **L4 端到端页面加载冒烟测试**：8 个 view QML 在可见模式下加载无错误（参考 `test_qml_dialogs_w3.py::test_all_8_dialogs_loadable` 模式）
2. **TC-PL-009 项目卡片点击 → 工作台跳转**：验证 selectProject 信号 emit + main.qml Connections 接收 + setProject 调用
3. **BarRow.qml 组件测试**：补 `test_qml_components.py` 对 BarRow 的覆盖（ReportView 依赖）

### 9.2 P1 优先补强（关键）

4. **三重守卫页面级验证**：每个 view 的 `xxxBridge === undefined/null/!hasService` 分支端到端断言
5. **空状态渲染断言**：filteredModel.count===0 时的"暂无数据"文本断言
6. **warning 态渲染**：SpecCenterView health_summary.error_count>0 / WorkspaceView 检查 Tab warning_count>0 的红色渲染
7. **资产汇总仅 PLC 分支**：WorkspaceView.loadAssetSummary 的 stack==="plc" 条件分支

### 9.3 P2 优先补强（重要）

8. **搜索/过滤/排序/分页交互**：ProjectListView 和 ChangeCenterView 的 JS 过滤逻辑
9. **变量表万行虚拟化性能**：10000 行 setEntries + 滚动流畅性
10. **loading 态处理**：同步阻塞期间 processEvents 可推进（QML 同步调用 Bridge Slot 的特性验证）

---

## 10. 附录

### 10.1 相关文件索引

| 文件 | 路径 | 用途 |
|------|------|------|
| QML 主入口 | `auto_pm/ui/qml_main_window.py` | Bridge 装配 + context property 注入 |
| Bridge 注册表 | `auto_pm/ui/registry.py` | FacadeRegistry 装配 5 个 Facade |
| Service 工厂 | `auto_pm/ui/factories.py` | 9 个 make_xxx_service 工厂函数 |
| DTO 契约 | `auto_pm/ui/contracts/dto/` | 5 个 DTO 模块（workbench/change/spec/delivery/system） |
| 测试共享 fixture | `tests/qml/conftest.py` | qapp / sample_projects / mock_project_service |
| 全局 conftest | `tests/conftest.py` | session 级 qapp（QApplication） |
| pyproject markers | `pyproject.toml` 第 86-93 行 | gui/cli/smoke/unit/integration/slow |

### 10.2 术语表

| 术语 | 含义 |
|------|------|
| Bridge | QObject 子类，暴露 Facade 为 QML 可调用 Slot/Property |
| Facade | Application 层聚合器，封装多个 Service |
| DTO | Data Transfer Object，dataclass(frozen=True) |
| 三重守卫 | `typeof xxxBridge === "undefined" \|\| xxxBridge === null \|\| !xxxBridge.hasService` 的降级判断 |
| context property | QML 通过 `engine.rootContext().setContextProperty()` 注入的全局对象 |
| 降级 | facade=None 或 Facade 失败时，Bridge Slot 返回空值/{success:False} 而非抛异常 |
| L1-L4 | 测试分层：L1 Bridge 单元 / L2 Model 单元 / L3 组件加载 / L4 端到端页面 |

### 10.3 版本基线核查

| 项目 | 基线值 | 实际值 | 核查结果 |
|------|-------|-------|---------|
| pyproject.toml version | 0.9.1 | 0.9.1（`pyproject.toml:7`） | ✅ |
| QML 唯一 UI 入口 | 是 | QWidget 已删除，QML 唯一 | ✅ |
| markers 注册 | gui/cli/smoke/unit/integration/slow | 6 个全注册 | ✅ |
| tests/qml/ 文件数 | 11 | conftest+10 测试文件 | ✅ |

---

**文档版本：** V0.9.1  
**最后更新：** 2026-07-08  
**维护者：** auto-pm 项目组  
**下次评审：** V0.9.2 迭代时同步更新页面矩阵与用例清单
