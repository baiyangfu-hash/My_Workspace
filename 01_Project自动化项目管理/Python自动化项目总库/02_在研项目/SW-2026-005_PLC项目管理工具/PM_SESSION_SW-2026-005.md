# PM_SESSION_SW-2026-005

## 0. Meta
- project_id: SW-2026-005
- project_name: PLC项目管理工具
- project_root: c:\Users\fubai\Desktop\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\02_在研项目\SW-2026-005_PLC项目管理工具
- last_updated: 2026-05-27 (V2.4 EventBus信号治理+Application死代码清理)
- owners: Trae

## 1. Positioning（项目定位）
- one_liner: PLC项目全生命周期管理桌面工具 — 聚焦项目管理、文档生成、变更管理三大核心
- users: PLC 工程师、项目管理者
- non_goals: 不替代西门子 TIA Portal；不做实时 PLC 通信；不做HMI映射/IO分配表（V2.1+规划）

### 1.1 MVP V2.0 范围重定义（2026-05-22）

**核心功能（必须可用）**:
- ✅ 项目管理: 新建/打开/关闭项目、项目树浏览、项目元数据管理
- ✅ 文档生成: 10种模板一键生成、变量替换、文档CRUD、另存为
- ✅ 变更管理: 版本检查(sync)、CHG/IFC文档生成、同步报告（已集成GUI）
- ✅ 变更管理UI: 变更单列表/创建/审核/状态流转面板（V2.2新增）
- ✅ 规范检查: 6种检查器(命名/语法/注释/配置/定时器/变量)
- ✅ 诊断分析: 七维度健康度评估、LSP兼容性检查

**降级为占位符（V2.0不实现）**:
- ⏸ HMI变量映射: 保留Tab占位，显示"开发中"提示
- ⏸ IO分配表: 保留Tab占位，显示"开发中"提示
- ⏸ 测试运行器: 不创建Dock，V2.1+规划
- ⏸ ST编辑器增强: 保留基础编辑，不实现代码片段/高级高亮

**明确排除**:
- ❌ Git版本控制集成
- ❌ 多人协作/云端同步
- ❌ PLC在线连接/下载程序

## 2. Current Focus（当前焦点）
- current_focus: V2.4 EventBus信号治理完成 — 2个断路信号已连接+6个死信号已清理+Application死代码已删除
- milestone: V2.4.0 ✅信号治理完成 → V2.5.0 📋下一步(SyncEngine属性修复+SpecDocParser) → V3.0.0-RC(发布候选)
- acceptance: A1:main.py可启动✅ | A2:ANALYZING状态不再死胡同✅ | A3:变更管理面板可用✅ | A4:CHG/IFC异步生成✅ | A5:33个sync测试全PASS✅ | A6:接口文档与代码100%对齐✅ | A7:0个断路信号✅ | A8:0个死代码✅ | A9:性能基线达标⏳

## 3. Status Summary（当前状态摘要）
- in_progress:
  - V2.4 EventBus信号治理完成 (2个断路信号已连接+6个死信号已清理+Application死代码已删除)
- next_up:
  - V2.5: 修复SyncEngine.format_version_report_html属性引用(is_consistent vs is_synced)
  - V2.5: 修复test_checker_framework 3个预存失败用例(SpecDocParser)
  - V3.0-RC: SpecDocParser修复+ST词法增强+诊断Markdown代码块+打包exe
- open_questions:
  - test_checker_framework.py 3个预存失败用例(SpecDocParser解析逻辑)
  - SyncEngine.format_version_report_html 引用不匹配属性(is_consistent vs is_synced)
- risks_dependencies:
  - 新增ChangeManagementPanel需UI自动化测试覆盖

## 4. Artifacts Index（文档索引）
- prd:
  - 00_项目基础信息/001_产品需求文档_PRD-V2.1.0.md
- plan:
  - 01_项目文档/02_规划过程/006_总计划与里程碑_PLAN-V2.0.0.md
- arch:
  - 01_项目文档/02_规划过程/007_架构设计文档_ARCH-V3.0.0.md (V3.0.0 深度对齐版)
- des:
  - 01_项目文档/02_规划过程/008_详细设计文档_DES-V2.0.0.md
- dev:
  - 01_项目文档/02_规划过程/010_代码结构说明_DEV-V2.0.0.md
- api:
  - 01_项目文档/02_规划过程/009_API接口文档_INT-V3.0.0.md (V3.0.0 深度审查对齐版)
- src:
  - 03_主程序/01_主程序核心代码/src/
- test:
  - 03_主程序/01_主程序核心代码/tests/
- um:
  - 01_项目文档/03_执行过程/05_用户手册/012_用户操作手册_UM-V2.1.0.md
- release:
  - 01_项目文档/03_执行过程/04_发布说明/RELEASE_NOTES.md
- change_mgmt:
  - 01_项目文档/03_执行过程/02_变更管理/变更列表.md
  - 01_项目文档/03_执行过程/02_变更管理/版本变更台帐.md
- defect:
  - 01_项目文档/03_执行过程/01_测试报告/缺陷跟踪表.md
- test_plan:
  - 01_项目文档/03_执行过程/01_测试报告/测试计划.md

## 5. Logs（按事件沉淀）
- change_log:
  - 2026-05-27 V2.4 EventBus信号治理: 修复2个断路信号(spec_check_request→_show_spec_check_dock, variable_check_request→导航PLC工具Tab+状态栏提示); 清理6个死信号(project_selected/document_saved/document_created/st_file_open_request/fb_doc_generate_request+规范事件分类); 删除Application死代码(app.py); menu_manager移除冗余QMessageBox | 影响: event_bus.py+main_window.py+menu_manager.py+删除app.py | ✅已完成
  - 2026-05-23 全方位PM审查: 输出开发进度+方案目标差距+问题点风险+V2.3→V3.0路线图 | 影响: 项目管理 | ✅已完成
  - 2026-05-23 V2.2变更: P0缺陷修复(main.py启动+ANALYZING死胡同)+变更管理UI面板+CHG/IFC异步生成+sync测试覆盖+技术债清理 | 影响: 8文件修改+4文件新增 | ✅已完成
  - 2026-05-22 范围重定义: 聚焦项目管理+文档生成+变更管理，HMI/IO/测试运行器降级为占位符 | 影响: 全局 | 已完成
  - 2026-05-22 Phase 3完成: HMI/IO/测试运行器降级为占位符UI + sync GUI集成(规范中心3按钮) + PLCService废弃重定向DiagnosticService + 文档编辑器另存为 | 影响: main_window.py + plc_service.py + document_editor.py + sync_engine.py | 已完成
- iteration_log:
  - 2026-05-23 V2.3迭代完成: 文档同步+接口对齐 — 创建ARCH-V3.0.0(修正模块计数/接口描述/EventBus信号)+确认INT-V3.0.0已对齐 | 33个sync测试全PASS | ✅已完成
  - 2026-05-23 V2.2迭代执行: Epic1(P0修复:main.py+ANALYZING+approve校验)→Epic2(变更管理UI:ChangeManagementPanel+审核+CHG/IFC异步)→Epic3(sync测试:33个用例全PASS)→Epic4(技术债:StyleBuilder路径+ChangeRequest枚举+print→logger) | ✅代码完成
  - 2026-05-22 V2.1迭代完成: Epic2(变更管理闭环:SyncResultDialog+回写+审核状态)→Epic1(瘦身823→292行:5Builder+NavigationController)→Epic3(SpecCheck单实例引导页)→Epic4(诊断异步化+右键菜单+设置验证) | 62项UI测试全PASS | ✅已完成
  - 2026-05-22 V2.1迭代启动: Epic2优先(变更管理闭环) → Epic1(瘦身823→<400) → Epic3(SpecCheck单实例/引导页) → Epic4(遗留项) | 基准: main_window 823行, 62项UI测试全PASS | ✅已完成
  - 2026-05-22 文档同步迭代: 11份文档修订/版本更新/缺失补充 | ✅已完成
  - 2026-05-22 Sprint 0 M0: 全面审查 + 范围重定义 + Phase 1-3修复 | 已完成
  - 2026-05-21 Sprint 8-12: Phase A-D + GUI布局重构 | 已完成
- bug_log:
  - 2026-05-23 BUG-OPEN-001: 无法打开现有DJ项目(DJ-2026-005)→Controller只认project.json/.plc_project.json,不支持.plc_json且未识别DJ目录结构 | 优先级: Critical | ✅已修复(扩展白名单+DJ智能检测+Service多格式加载)
  - 2026-05-23 P0-1: main.py调用MainWindow._resolve_chinese_font→应用无法启动 | 优先级: Critical | ✅已修复(改为StyleBuilder._resolve_chinese_font)
  - 2026-05-23 P0-2: ChangeStatus.ANALYZING在valid_transitions中无定义→死胡同状态 | 优先级: Critical | ✅已修复(APPROVED→ANALYZING+ANALYZING→IN_PROGRESS)
  - 2026-05-23 P1-3: approve_change_request绕过valid_transitions校验 | 优先级: High | ✅已修复(改用valid_transitions校验)
  - 2026-05-23 GUI-001: TAB_CHANGE_MGMT(3)错误映射到TOOL_SPEC(4)→点击变更管理Tab显示规范中心 | 优先级: Critical | ✅已修复(方案B结构重构:新增独立变更管理ToolBox页面+重写映射表)
  - 2026-05-23 GUI-002~004: HMI工具映射冲突/规范中心与变更管理共享页面/架构不对称 | 优先级: High/Medium | ✅已修复(移除HMI页面+建立一一对应映射)
  - 2026-05-22 C-05: QSS文件QSplitter::handle:hover缺闭合括号→半数样式失效 | 优先级: Critical | ✅已修复
  - 2026-05-22 C-06: ToolBox(6页)↔TabWidget(5Tab)索引不匹配→导航越界 | 优先级: Critical | ✅已修复(映射表+blockSignals)
  - 2026-05-22 H-09: 内联样式与QSS文件严重冲突→主题切换无效 | 优先级: High | ✅已修复(迁移到QSS属性选择器)
  - 2026-05-22 H-10: Dashboard StatCard用findChild(QLabel)查找数值→找到图标标签 | 优先级: High | ✅已修复(直接引用_value_label)
  - 2026-05-22 H-11: 侧边栏ToolBox页面全是文字按钮列表→视觉"1大坨" | 优先级: High | ✅已修复(添加图标+分隔线+QSS属性)
  - 2026-05-22 M-13: 字体检测逻辑在main.py和main_window.py重复 | 优先级: Medium | ✅已修复
  - 2026-05-22 M-14~M-17: Controller接口化/枚举映射/菜单修复/EventBus | 优先级: Medium | ✅已修复
  - 2026-05-22 S-05: main_window._project_data从未赋值→变更管理3按钮完全不可用 | 优先级: Critical | ✅已修复
  - 2026-05-22 C-01~C-04: 诊断/测试/词法分析器Critical问题 | 优先级: Critical | ✅已修复
  - 2026-05-22 H-01/H-04/H-08: 硬编码路径/主线程sleep/跨组件私有属性 | 优先级: High | ✅已修复
  - 2026-05-22 H-02/H-06/H-07: 测试运行器/HMI/IO占位问题 | 优先级: High | 降级占位
  - 2026-05-22 M-01/M-02/M-09/M-10/M-12: 规范检查/文档编辑/配置路径/职责 | 优先级: Medium | ✅已修复
  - 2026-05-22 F-01: 左侧ToolBox侧边栏中文乱码 | 优先级: Critical | ✅已修复
- refactor_log:
  - 2026-05-23 V2.2重构: 新增ChangeManagementPanel(变更单列表+审核+状态流转) + CHG/IFC生成异步化(_GenerateDocWorker) + StyleBuilder路径遍历改用循环查找 + ChangeRequest.status改用ChangeStatus.DRAFT.value + SyncEngine print→logger | 影响: 8文件修改+1文件新增 | ✅已完成
  - 2026-05-22 V2.1重构: MainWindow 823→292行(-66%) — 5Builder+NavigationController+SyncResultDialog+回写+审核+SpecCheck单实例+诊断异步化+右键菜单+设置验证 | ✅已完成
  - 2026-05-22 Event B完成: UI Controller模式重构 — 3Controller + main_window 1205→982行 | ✅已完成
  - 2026-05-22 Event D完成: S-01 FB映射表统一fb_registry.py | ✅已完成
  - 2026-05-22 Phase 0死代码清理: 删除7个模块(~1500行) | ✅已完成
- release_log:
  - 2026-05-23 V2.2.1 发布: BUG-OPEN-001修复(无法打开现有DJ项目) — Controller白名单扩展+.plc.json支持+DJ智能检测+Service多格式加载 | 19/19专项测试通过+0新增回归 | ✅已发布
  - 2026-05-23 V2.2.0 开发中: P0修复+变更管理UI+sync测试+技术债

## 6. 审查问题清单（2026-05-23 V2.2更新）

### V2.2新增修复 (3项)
| ID | 问题 | 优先级 | 状态 |
|----|------|--------|------|
| P0-1 | main.py调用MainWindow._resolve_chinese_font→应用无法启动 | Critical | ✅已修复 |
| P0-2 | ChangeStatus.ANALYZING在valid_transitions中无定义→死胡同 | Critical | ✅已修复 |
| P1-3 | approve_change_request绕过valid_transitions校验 | High | ✅已修复 |

### 累计修复统计
- ✅ 已修复: 19项 (6 Critical + 7 High + 6 Medium) — V2.2新增3项
- ⏸ 降级占位: 6项 (H-02, H-06, H-07, M-03, M-05, M-11)
- 🔄 后续迭代: 4项 (M-07, M-08, L-01~08)
- 📊 总计: 35项 → 19修复 + 6降级 + 4+8后续

## 7. V2.2 文件变更清单

### 新增文件
| 文件 | 用途 | 行数 |
|------|------|------|
| src/ui/widgets/change_management_panel.py | 变更管理面板(列表+审核+状态流转) | ~280 |
| tests/test_change_service.py | ChangeService单元测试(10用例) | ~150 |
| tests/test_sync_engine.py | SyncEngine单元测试(13用例) | ~200 |
| tests/test_chg_ifc_generator.py | CHG/IFC生成器单元测试(10用例) | ~180 |

### 修改文件
| 文件 | 变更 |
|------|------|
| main.py | 修复StyleBuilder._resolve_chinese_font引用 |
| src/core/constants.py | ANALYZING状态转换规则补全 |
| src/services/change_service.py | approve_change_request改用valid_transitions校验 |
| src/ui/builders/right_panel_builder.py | 新增变更管理Tab |
| src/ui/builders/left_panel_builder.py | 侧边栏新增变更管理入口+Tab索引更新 |
| src/ui/controllers/navigation_controller.py | 新增TAB_CHANGE_MGMT映射 |
| src/ui/controllers/sync_controller.py | CHG/IFC生成异步化(_GenerateDocWorker) |
| src/ui/main_window.py | 集成变更管理面板+Tab索引更新 |
| src/ui/builders/style_builder.py | QSS路径遍历改用循环查找 |
| src/models/change_request.py | status默认值改用ChangeStatus.DRAFT.value |
| src/sync/sync_engine.py | print→logger |

## 8. 功能完成度（V2.2更新）

| # | 功能域 | V2.1完成度 | V2.2完成度 |
|---|--------|-----------|-----------|
| F01 | 项目管理(向导/模板/树/CRUD) | 90% | 90% |
| F02 | 文档生成(10模板/变量替换/另存为) | 95% | 95% |
| F03 | 变更管理-Sync(版本检查/CHG/IFC/报告/回写/审核) | 95% | 98% (+异步生成) |
| F04 | 规范检查(6检查器/规则注册表/单实例) | 95% | 95% |
| F05 | 诊断分析(七维度/LSP兼容性/Dock面板) | 85% | 85% |
| F06 | ST编辑器基础版(语法高亮) | 70% | 70% |
| F07 | 仪表盘(统计卡片/最近项目) | 85% | 85% |
| F08 | 变更管理-变更单(列表/创建/审核/状态流转UI) | 80% | 95% (+ChangeManagementPanel) |

## 9. 深度审查报告（2026-05-23）

### 9.1 审查范围
- 主程序核心代码逻辑（main.py + app.py）
- 功能模块设计与模块间接口（11个Service + 4个Controller + 4个Builder + 2个Manager）
- GUI接口与功能模块对应关系（7个Widget + 5个Dialog + DashboardPage）
- 接口文档与实际代码对齐度（INT-V2.0.0 + ARCH-V2.0.0）

### 9.2 API接口文档与代码差异（INT-V2.0.0 → 实际代码）

#### 9.2.1 严重不匹配（方法名/签名完全不同）

| 文档API | 实际代码 | 差异类型 |
|---------|---------|---------|
| `ProjectService.open_project(path)` | `ProjectService.load_project_from_path(path)` → `(Project, error)` | 方法名+返回值不同 |
| `ProjectService.close_project()` | 不存在 | 文档虚构 |
| `DiagnosticService.run_diagnosis(path)` → report | `DiagnosticService().run_full_diagnostic(path)` → `(report, metrics)` | 方法名+返回值不同 |
| `DiagnosticService.run_lsp_check(path)` → lsp_result | 不存在独立方法，内嵌于run_full_diagnostic | 文档虚构 |
| `DocumentService.get_template_types()` | 不存在 | 文档虚构 |
| `DocumentService.generate_document(...)` | `DocumentService.create_document(...)` / `create_or_update_document(...)` | 方法名+参数不同 |
| `SpecCheckerService.get_available_rules()` | `SpecCheckerService().get_enabled_checkers()` | 方法名+返回类型不同 |
| `SpecCheckerService.run_checks(path, rule_ids)` | `SpecCheckerService().check_project(path)` / `check_file(path)` | 方法名+参数不同 |
| `SyncEngine.run_version_check(path)` | `SyncEngine.run_check(path)` | 方法名不同 |
| `ProjectController.create_project(parent)` | 不存在 | 文档虚构 |
| `ProjectController.open_project(parent)` | 不存在 | 文档虚构 |
| `ProjectController.save_project()` | 不存在 | 文档虚构 |
| `ProjectController.load_project_to_tree(path)` | 不存在 | 文档虚构 |
| `SyncController.run_version_check(path)` | `SyncController.on_sync_version_check()` | 方法名+参数不同 |
| `SyncController.run_generate_chg(path)` | `SyncController.on_sync_generate_chg()` | 方法名+参数不同 |
| `SyncController.run_generate_ifc(path)` | `SyncController.on_sync_generate_ifc()` | 方法名+参数不同 |
| `DashboardController.update_stats()` | `DashboardController.refresh_dashboard_data()` | 方法名不同 |
| `DashboardController.refresh_recent_projects()` | 不存在独立方法 | 文档虚构 |
| `SettingsManager.load(path)` | `SettingsManager.initialize(settings_dir)` | 方法名+参数不同 |

#### 9.2.2 文档缺失（实际存在但未记录）

| 模块 | 缺失的API |
|------|----------|
| ChangeService | `list_change_requests()`, `create_change_request()`, `update_status()`, `approve_change_request()` — 整个服务未记录 |
| NavigationController | `connect()`, `navigate_to_tab()`, `on_sidebar_action()`, `on_project_tree_navigate()` — 整个控制器未记录 |
| ArtifactRegistryService | `detect_project_type()`, `scan_project_assets()`, `summarize_assets()`, `get_artifact_roots()` — 整个服务未记录 |
| WorkflowService | `build_checkpoints()` — 整个服务未记录 |
| TemplateService | `initialize_builtin_templates()`, `get_template()`, `get_all_templates()`, `apply_template()` — 仅提及未详细记录 |
| SyncEngine | `run_full_report()`, `run_generate_chg()`, `run_generate_ifc()`, `writeback_to_project()`, `format_version_report_html()` |
| SettingsManager | `initialize()`, `reset_to_defaults()`, `get_all()` |
| ChangeManagementPanel | `set_project_path()`, `refresh()`, `cleanup()` — 整个Widget未记录 |
| SyncResultDialog | `get_action()`, `get_file_path()`, `get_doc_type()` — 整个Dialog未记录 |

#### 9.2.3 EventBus信号差异

| 文档记录的信号 | 实际代码 | 状态 |
|--------------|---------|------|
| `project_selected(str)` | ✅ 存在但从未连接 | ⚠️ 死信号 |
| `project_created(str)` | ✅ 存在且已连接 | ✅ |
| `project_opened(str)` | ✅ 存在且已连接 | ✅ |
| `project_closed()` | ❌ 不存在 | 文档虚构 |
| `document_open_request(str)` | ✅ 存在但处理为空 | ⚠️ 空处理 |
| `document_saved(str)` | ✅ 存在但从未发射 | ⚠️ 死信号 |
| `document_created(str)` | ✅ 存在但从未发射 | ⚠️ 死信号 |
| `check_started()` | ❌ 不存在 | 文档虚构 |
| `check_completed(object)` | ❌ 不存在 | 文档虚构 |
| `diagnostic_started()` | ❌ 不存在 | 文档虚构 |
| `diagnostic_completed(object)` | ❌ 不存在 | 文档虚构 |
| `st_file_open_request(str)` | ✅ 存在但从未连接 | ⚠️ 死信号 |
| `variable_check_request()` | ✅ 存在，MenuManager发射但无处理 | ⚠️ 断路信号 |
| `fb_doc_generate_request(str)` | ✅ 存在但从未发射/连接 | ⚠️ 死信号 |
| `spec_check_request(dict)` | ✅ 存在，ToolBarManager发射但无处理 | ⚠️ 断路信号 |
| `theme_changed(str)` | ✅ 存在且已连接 | ✅ |
| `settings_changed()` | ✅ 存在且已连接 | ✅ |
| `sync_*_requested` (文档V2.0-R2) | ❌ 不存在 | 文档虚构 |

### 9.3 架构文档与代码差异（ARCH-V2.0.0 → 实际代码）

| 维度 | 文档描述 | 实际代码 | 差异 |
|------|---------|---------|------|
| Widget数量 | 5个 | 7个(+ChangeManagementPanel, SpecCheckTabPanel引导页) | ❌ |
| Dialog数量 | 4个 | 5个(+SyncResultDialog) | ❌ |
| Controller数量 | 3个 | 4个(+NavigationController) | ❌ |
| Service数量 | 9个 | 11个(+WorkflowService, ChangeService) | ❌ |
| Model数量 | 8个 | 13个(+ChangeRequest, CheckResult, ProjectArtifact, WorkflowCheckpoint等) | ❌ |
| Application类 | 有_run_cli()+shutdown() | 无CLI模式，无shutdown() | ❌ |
| Dashboard统计 | FB数/变量数/文档数/测试数 | 项目总数/进行中/已完成/已归档 | ❌ |
| MainWindow方法 | _build_menu_bar/_build_toolbar等 | 委托给MenuManager/ToolBarManager | ❌ |
| EventBus信号 | project_closed/check_started/completed等 | 不存在这些信号 | ❌ |
| SettingsManager | load(path) | initialize(settings_dir) | ❌ |

### 9.4 GUI与功能模块对应关系审查

#### 9.4.1 左侧ToolBox → 右侧Tab映射（✅ 正确）

| ToolBox页面 | 索引 | Tab页面 | 索引 | 状态 |
|------------|------|---------|------|------|
| 项目管理 | 0 | 仪表盘 | 0 | ✅ |
| 文档管理 | 1 | 项目 | 1 | ✅ |
| PLC工具 | 2 | 文档 | 2 | ✅ |
| HMI工具 | 3 | 变更管理 | 3 | ⚠️ 映射到TAB_SPEC_CHECK(5) |
| 规范中心 | 4 | PLC工具 | 4 | ✅ |
| 系统设置 | 5 | 规范检查 | 5 | ✅ |

#### 9.4.2 GUI功能入口 → 服务层调用链（✅ 基本完整）

| GUI入口 | 触发方式 | Controller | Service | 状态 |
|---------|---------|-----------|---------|------|
| 新建项目 | 菜单/工具栏/仪表盘 | MenuManager→EventBus | ProjectService.create_new_project() | ✅ |
| 打开项目 | 菜单/工具栏/仪表盘 | MenuManager→EventBus | ProjectService.load_project_from_path() | ✅ |
| 项目树浏览 | 左侧面板 | ProjectController | ProjectService | ✅ |
| 项目信息更新 | 项目树双击 | ProjectController.update_project_info() | — | ✅ |
| 新建文档 | 侧边栏/项目树右键 | ProjectTreeWidget | DocumentService.create_document() | ✅ |
| 文档编辑 | 文档Tab | DocumentEditor | — (直接文件I/O) | ✅ |
| 另存为 | 文档编辑器工具栏 | DocumentEditor.save_file_as() | — | ✅ |
| 规范检查 | 菜单F5/侧边栏/Dock | SpecCheckPanel.start_check() | SpecCheckerService.check_project() | ✅ |
| 深度诊断 | 菜单F6/Dock | DiagnosticPanel.run_diagnostic() | DiagnosticService.run_full_diagnostic() | ✅ |
| 版本检查 | 侧边栏规范中心 | SyncController.on_sync_version_check() | SyncEngine.run_check() | ✅ |
| 生成CHG | 侧边栏规范中心 | SyncController.on_sync_generate_chg() | SyncEngine.run_generate_chg() | ✅ |
| 生成IFC | 侧边栏规范中心 | SyncController.on_sync_generate_ifc() | SyncEngine.run_generate_ifc() | ✅ |
| 变更单列表 | 变更管理Tab | ChangeManagementPanel.refresh() | ChangeService.list_change_requests() | ✅ |
| 创建变更单 | 变更管理Tab按钮 | ChangeManagementPanel._on_create() | ChangeService.create_change_request() | ✅ |
| 审核变更单 | 变更管理Tab按钮 | ChangeManagementPanel._on_approve() | ChangeService.approve_change_request() | ✅ |
| 推进状态 | 变更管理Tab按钮 | ChangeManagementPanel._on_advance() | ChangeService.update_status() | ✅ |
| 主题切换 | 菜单/侧边栏 | MenuManager→EventBus | StyleBuilder.apply() | ✅ |
| 设置 | 菜单/侧边栏 | MenuManager→SettingsDialog | SettingsManager | ✅ |
| ST编辑器 | PLC工具Tab | STEditor.open_file() | — (直接文件I/O) | ✅ |
| 源码跳转 | 诊断/规范检查面板 | MainWindow._jump_to_source() | STEditor.open_file() | ✅ |

#### 9.4.3 GUI功能入口 → 断路/死信号（❌ 需修复）

| GUI入口 | 问题 | 严重度 |
|---------|------|--------|
| 工具栏"规范检查"按钮 | 发射spec_check_request但MainWindow未连接处理 | High |
| 菜单"变量检查" | 发射variable_check_request但MainWindow未连接处理 | Medium |
| HMI工具侧边栏页面 | 3个按钮(变量映射/报警配置/画面关联)映射到TAB_SPEC_CHECK | Medium |
| EventBus.project_selected | 定义但从未连接任何处理 | Low |
| EventBus.document_saved | 定义但从未发射 | Low |
| EventBus.document_created | 定义但从未发射 | Low |
| EventBus.st_file_open_request | 定义但从未发射/连接 | Low |
| EventBus.fb_doc_generate_request | 定义但从未发射/连接 | Low |

### 9.5 代码逻辑问题

| ID | 问题 | 严重度 | 建议 |
|----|------|--------|------|
| L-01 | Application类存在但main.py未使用，直接调用run_gui() | Medium | 删除Application类或重构main.py使用它 |
| L-02 | SpecService全部空实现(3个方法返回默认值) | Low | V2.3+实现或删除 |
| L-03 | VariableService全部空实现(2个方法返回默认值) | Low | V2.3+实现或删除 |
| L-04 | FBDocumentDialog仅占位标签+关闭按钮 | Low | V2.3+实现 |
| L-05 | _build_central_widget创建splitter但未加入layout(由_build_right_panel补上) | Low | 代码可读性优化 |
| L-06 | HMI工具页面3个按钮映射到TAB_SPEC_CHECK而非独立Tab | Medium | 改为占位提示或移除 |
| L-07 | SyncEngine.format_version_report_html引用entry.is_consistent，需确认VersionGapReport属性名 | High | 验证并修复 |

### 9.6 实际接口清单（代码真实API，用于更新INT-V3.0.0）

#### SettingsManager
```
initialize(settings_dir: Optional[Path] = None) → None
get(key: str, default: Any = None) → Any
set(key: str, value: Any) → None
save() → None
add_recent_project(project_path: str, project_name: str) → None
get_recent_projects() → List[Dict[str, str]]
reset_to_defaults() → None
get_all() → Dict[str, Any]
```

#### ProjectService (全部@classmethod)
```
create_project(name, business_line, template_id, manager, description, plc_brand, hmi_brand, custom_path) → (Optional[Project], Optional[str])
get_project(project_id) → Optional[Project]
get_all_projects() → List[Project]
load_project_from_path(project_path) → (Optional[Project], Optional[str])
delete_project(project_id) → (bool, Optional[str])
scan_projects_directory(directory) → List[Project]
create_new_project(project_info: Dict) → (Optional[Path], Optional[str])
import_dj_project(project_path) → (Optional[Project], Optional[str])
```

#### DiagnosticService (实例方法)
```
__init__(config: Optional[Dict] = None)
run_full_diagnostic(project_path) → (Any, Any)
get_last_diagnostics() → (Optional[Any], Optional[Any])
get_timing_statistics() → Dict[str, float]
is_healthy() → bool
reset() → None
```

#### DocumentService (全部@classmethod)
```
create_document(project_path, doc_type, doc_name, version, author, content) → (Optional[str], Optional[str])
create_or_update_document(project_path, doc_type, doc_name, version, author, content) → (Optional[str], Optional[str])
find_authoritative_document(project_path, doc_type) → Optional[str]
read_document(file_path) → (Optional[str], Optional[str])
save_document(file_path, content) → (bool, Optional[str])
list_documents(project_path) → List[Dict]
```

#### SpecCheckerService (实例方法)
```
__init__(config: Optional[Dict] = None)
check_project(project_path) → Any (CheckReport)
check_file(file_path) → Any (CheckResult)
get_enabled_checkers() → List[Any]
load_project_rules(project_path) → bool
clear_cache() → None
get_statistics() → Dict[str, int]
reset_statistics() → None
```

#### ChangeService (全部@classmethod)
```
list_change_requests(project_path) → List[ChangeRequest]
create_change_request(project_path, category, title, description) → (Optional[ChangeRequest], Optional[str])
update_status(project_path, change_id, new_status) → bool
approve_change_request(project_path, change_id, approver) → bool
```

#### SyncEngine (全部@classmethod)
```
run_check(project_path) → VersionGapReport
run_full_report(project_path, output_dir) → str
run_generate_chg(project_path, output_dir) → str
run_generate_ifc(project_path, output_dir) → str
writeback_to_project(source_path, project_path, doc_type) → List[str]
format_version_report_html(report) → str
```

#### TemplateService (全部@classmethod)
```
initialize_builtin_templates() → None
get_template(template_id) → Optional[Dict]
get_all_templates() → List[Dict]
get_template_metadata() → List[Dict]
apply_template(template_id, target_path, variables) → tuple
```

#### ArtifactRegistryService (全部@classmethod)
```
detect_project_type(project_path) → ProjectType
scan_project_assets(project_path) → List[ProjectArtifact]
summarize_assets(assets) → Dict[str, int]
get_artifact_roots(assets) → List[Dict[str, str]]
```

#### WorkflowService (全部@classmethod)
```
build_checkpoints(artifact_summary: dict) → List[WorkflowCheckpoint]
```

#### ProjectController
```
__init__(main_window)
on_project_created(path: str) → None
on_project_opened(path: str) → None
update_project_info(context: dict) → None
```

#### SyncController
```
__init__(main_window)
on_sync_version_check() → None
on_sync_generate_chg() → None
on_sync_generate_ifc() → None
```

#### DashboardController
```
__init__(main_window)
on_dashboard_action(action_id: str) → None
refresh_dashboard_data() → None
```

#### NavigationController
```
__init__(tool_box, tab_widget, menu_manager, sync_handler, project_info_handler)
connect() → None
navigate_to_tab(tab_index: int) → None
on_sidebar_action(action_text: str) → None
on_project_tree_navigate(tab_index: int, context: dict) → None
```

#### EventBus 信号（实际定义）
```
project_selected(str)       — ⚠️ 未连接
project_created(str)        — ✅ 已连接
project_opened(str)         — ✅ 已连接
document_open_request(str)  — ✅ 已连接(空处理)
document_saved(str)         — ⚠️ 未发射
document_created(str)       — ⚠️ 未发射
st_file_open_request(str)   — ⚠️ 未连接
variable_check_request()    — ⚠️ 发射但无处理
fb_doc_generate_request(str)— ⚠️ 未连接
spec_check_request(dict)    — ⚠️ 发射但无处理
theme_changed(str)          — ✅ 已连接
settings_changed()          — ✅ 已连接
```

### 9.7 审查结论与行动建议

**结论**: 代码架构设计合理（薄壳+Controller+Builder+EventBus），功能模块与GUI基本对应完整。主要问题是**文档严重滞后于代码**，22处API不匹配+6个死信号+架构文档计数错误。

**优先行动项**:

| 优先级 | 行动 | 影响范围 |
|--------|------|---------|
| P0 | 更新API接口文档INT-V3.0.0，对齐9.6节实际接口清单 | 009_API接口文档 |
| P0 | 更新架构文档ARCH-V3.0.0，修正模块计数和接口描述 | 007_架构设计文档 |
| P1 | 连接spec_check_request信号到SpecCheckPanel.start_check() | main_window.py |
| P1 | 连接variable_check_request信号到规范检查或提示 | main_window.py |
| P1 | 修复HMI工具页面映射(改为占位提示) | left_panel_builder.py |
| P2 | 清理EventBus死信号(删除或实现) | event_bus.py |
| P2 | 删除或重构Application类(当前为死代码) | app.py + main.py |
| P2 | 验证SyncEngine.format_version_report_html属性引用 | sync_engine.py |
