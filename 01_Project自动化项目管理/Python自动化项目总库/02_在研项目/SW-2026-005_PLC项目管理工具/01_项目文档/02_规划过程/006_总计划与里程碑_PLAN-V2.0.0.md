# 总计划与里程碑 PLAN-V2.0.0

> **项目**: SW-2026-005 PLC项目管理工具  
> **版本**: V2.0.0 | **日期**: 2026-05-22  
> **变更**: V2.0深度审查完成 — 13项修复+6项降级+cleanup架构统一  
> **说明**: 本文档作为"里程碑/版本/Sprint"唯一权威总表，执行进度每日更新记录在 `01_项目文档/03_执行过程/README.md`

---

## 1. 总体目标

- 交付一个可运行的桌面 GUI 工具，覆盖 PLC 项目从创建到交付的核心闭环。
- 以 **V1.2.0-MVP** 为第一阶段可交付门槛：可安装运行、关键流程可用、具备基本用户手册与测试证据。

---

## 2. 版本与里程碑

### 2.1 里程碑定义

| 里程碑 | 版本目标 | 定义（验收口径） |
|---|---|---|
| M1 | V1.0.0-M1 | 应用骨架可启动；核心基础设施（Application/EventBus/Settings）可用 |
| M2 | V1.0.0-M2 | 项目创建/打开闭环可用；模板可应用 |
| M3 | V1.0.0-M3 | Checker 框架闭环可用；核心规则可运行并产出报告 |
| M4 | V1.1.0-M4 | 文档生成闭环可用（模板可渲染/输出）；UI 可触达 |
| M5 | V1.1.0-M5 | 诊断分析闭环可用（健康度/问题列表/建议）；测试统计可产出 |
| M6 | V1.2.0-M6 | STEditor 增强与片段库可用；编辑体验与缺依赖降级路径稳定 |
| MVP | V1.2.0-MVP | 集成测试+打包exe+用户手册；"创建项目→编辑/检查→诊断→生成交付文档"可演示 |
| M7 | V1.3.0-M7 | **同步自动化 Phase A**：CLI `check`/`full-report` 可运行；版本差距矩阵自动生成 |
| M8 | V1.3.0-M8 ✅ | **同步自动化 Phase B**：IFC 接口文档从 GlobalVars.db 半自动生成 |
| M9 | V1.3.0-M9 ✅ | **同步自动化 Phase C**：CHG 变更记录从 .scl changelog / PM_SESSION 半自动生成 |
| M10 | V1.4.0-M10 ✅ | **同步自动化 Phase D**：全量同步报告（DSN/UM/台帐对齐清单） |
| M11 | V2.0-R1 | 深度审查: 范围重定义+死代码清理+FB映射统一+sync GUI集成 |
| M12 | V2.0-R2 | QSS修复+导航映射+样式迁移+侧边栏重构+Controller接口化+cleanup架构 |
| RC | V2.0.0-RC | 验证测试通过+文档同步+发布准备 |

### 2.2 Sprint 计划表

> Sprint 的"完成/进行中/待开始"状态以执行过程索引为准：[`../03_执行过程/README.md`](../03_执行过程/README.md)

| Sprint | 时间范围 | 目标版本 | 主要交付物 |
|---|---|---|---|
| Sprint 1 | 04-15 ~ 04-19 | V1.0.0-M1 | Application/EventBus/SettingsManager |
| Sprint 2 | 04-22 ~ 04-26 | V1.0.0-M2 | ProjectService/TemplateService/NewProjectDialog |
| Sprint 3 | 04-29 ~ 05-03 | V1.0.0-M3 | BaseChecker/RuleRegistry/6种Checker |
| Sprint 4 | 05-06 ~ 05-10 | V1.1.0-M4 | DocumentService/10种模板 |
| Sprint 5 | 05-13 ~ 05-17 | V1.1.0-M5 | DiagnosticService/HealthAnalyzer |
| Sprint 6 | 05-20 ~ 05-24 | V1.2.0-M6 | STEditor增强 + 代码片段库 |
| Sprint 7 | 05-27 ~ 05-30 | V1.2.0-MVP | 集成测试 + 打包exe + 用户手册 |
| Sprint 8 | 05-21 ~ 05-22 | **V1.3.0-M7** ✅ | **sync/ Phase A**: version_extractor + version_checker + sync_engine + sync_cli + ARCH/DES文档更新 |
| Sprint 9 | 05-21 | **V1.3.0-M8** ✅ | **sync/ Phase B**: db_parser(解析GlobalVars.db 5 STRUCT/203变量) + ifc_generator(半自动生成IFC文档) + CLI集成 |
| Sprint 10 | 05-21 | **V1.3.0-M9** ✅ | **sync/ Phase C**: session_parser(解析PM_SESSION change_log) + chg_generator(.scl changelog→CHG文档+PM_SESSION→CHG) + CLI集成 |
| Sprint 11 | 05-21 | **V1.4.0-M10** ✅ | **sync/ Phase D**: sync_report 全量报告生成 (5段式Markdown: 版本矩阵+DSN+UM+台帐+行动建议) |
| Sprint 12 | 05-22 | V2.0-R1 | 深度审查+范围重定义+Phase0-3修复(死代码清理/FB映射统一/sync GUI集成/HMI降级) |
| Sprint 13 | 05-22 | V2.0-R2 | QSS语法修复+导航映射+内联样式迁移+侧边栏重构+Controller模式+cleanup架构+SpecCheck Dock+QLayout修复+退出异常消除 |

---

## 3. 当前阶段（Sprint 13 / V2.0-R2 已交付 → RC发布准备）

### 3.1 优先级

| 优先级 | 说明 |
|---|---|
| P0 | 影响可运行性/可理解性的缺陷（崩溃、缺依赖无提示、关键流程断链） |
| P1 | 影响可用性的交互闭环（项目树联动、跳转、主要入口可达） |
| P2 | 体验增强与扩展能力（片段库、编辑增强、性能优化、sync自动化扩展） |

### 3.2 Done 标准（Sprint 6）

- STEditor 在缺少 QScintilla 时必须可用且提示明确；存在回归用例覆盖。
- 核心 UI 流程无崩溃：启动→打开项目→查看项目树→进入主要面板。

### 3.3 Sprint 8 交付物 ✅ (V1.3.0-M7 已交付)

| 交付物 | 路径 | 状态 |
|--------|------|------|
| ARCH 架构文档 V1.1.0 | `01_项目文档/02_规划过程/007_架构设计文档_ARCH-V1.1.0.md` | ✅ |
| DES 详细设计 V1.1.0 | `01_项目文档/02_规划过程/008_详细设计文档_DES-V1.1.0.md` | ✅ |
| PLAN 总计划 V1.1.0 | `01_项目文档/02_规划过程/006_总计划与里程碑_PLAN-V1.1.0.md` | ✅ |
| `src/sync/version_extractor.py` | 版本号提取（.scl/.md/.db） | ✅ |
| `src/sync/version_checker.py` | 版本差距矩阵自动生成 | ✅ |
| `src/sync/sync_engine.py` | 同步编排引擎 | ✅ |
| `src/sync/sync_cli.py` | CLI 入口（`check` / `full-report`） | ✅ |
| 集成测试 | 对 DJ-2026-005 项目运行验证通过 | ✅ |

**验收口径**：
- `python -m src.sync.sync_cli check <project_path>` 在 1 秒内输出版本差距矩阵
- 退出码 0 = 全部一致，1 = 存在滞后
- 对实际项目 DJ-2026-005 验证：7 个模块中检测出 3 个滞后

### 3.4 Sprint 9 交付物 ✅ (V1.3.0-M8 已交付)

| 交付物 | 路径 | 状态 |
|--------|------|------|
| DES 详细设计 V1.2.0 | `01_项目文档/02_规划过程/008_详细设计文档_DES-V1.2.0.md` | ✅ |
| `src/sync/db_parser.py` | GlobalVars.db 解析 (5 STRUCT, 203 变量) | ✅ |
| `src/sync/ifc_generator.py` | IFC 文档半自动生成 + 审核清单 | ✅ |
| CLI `generate-ifc` 集成 | `sync_cli.py` 新增子命令 | ✅ |
| 集成测试 | DJ-2026-005: pickplace(57in/26out), feeder(16in/13out), conveyor(21in/14out) 全部生成 | ✅ |

**验收口径**：
- `python -m src.sync.sync_cli generate-ifc pickplace <project>` 从 DB 自动生成完整接口表格
- 输出包含 审核清单（来源列/状态机/地址映射 提示待人工补充）
- 文件名带 `-GENERATED` 后缀，防止覆盖正式文档

### 3.5 Sprint 10 交付物 ✅ (V1.3.0-M9 已交付)

| 交付物 | 路径 | 状态 |
|--------|------|------|
| ARCH 架构设计 V1.3.0 | `01_项目文档/02_规划过程/007_架构设计文档_ARCH-V1.3.0.md` | ✅ |
| DES 详细设计 V1.3.0 | `01_项目文档/02_规划过程/008_详细设计文档_DES-V1.3.0.md` | ✅ |
| `src/sync/session_parser.py` | PM_SESSION.md 解析 (change_log 3条目) | ✅ |
| `src/sync/chg_generator.py` | .scl changelog → CHG / PM_SESSION → CHG | ✅ |
| CLI `generate-chg` 集成 | `sync_cli.py` 新增子命令, --source scl/session | ✅ |
| 集成测试 | DJ-2026-005: OB1(5条目), PickPlace(2条目) 生成验证 | ✅ |

**验收口径**：
- `python -m src.sync.sync_cli generate-chg ob1 <project>` 从 .scl changelog 提取5条版本变更
- 支持 `--source session` 从 PM_SESSION change_log 聚合
- 类型推断 (修复→Bug修复, 重构→重构, 集成→功能)

### 3.6 Sprint 11 交付物 ✅ (V1.4.0-M10 已交付)

| 交付物 | 路径 | 状态 |
|--------|------|------|
| ARCH 架构设计 V1.4.0 | `01_项目文档/02_规划过程/007_架构设计文档_ARCH-V1.4.0.md` | ✅ |
| DES 详细设计 V1.4.0 | `01_项目文档/02_规划过程/008_详细设计文档_DES-V1.4.0.md` | ✅ |
| `src/sync/sync_report.py` | 全量同步报告生成器 (FullSyncReport/SyncReport) | ✅ |
| CLI `full-report` 增强集成 | `sync_engine.py` run_full_report 改用 SyncReport | ✅ |
| 集成测试 | DJ-2026-005: 7FB × (DSN+UM) 覆盖矩阵 + 11条行动建议 生成验证 | ✅ |

**验收口径**：
- `python -m src.sync.sync_cli full-report <project>` 生成五段式 Markdown 报告
- §1 版本差距矩阵 (复用L0 check) / §2 DSN覆盖度 / §3 UM覆盖度 / §4 变更台帐 / §5 行动建议
- DSN/UM 匹配支持 FB标识符提取 (含 alias 映射: fb_external→fb3001)
- 孤本文档标记为 [?]，无对应文档标记为 [MISSING]

### 3.7 Sprint 12 交付物 (V2.0-R1 已交付)

| 交付物 | 说明 | 状态 |
|--------|------|------|
| 删除7个死代码模块(~1500行) | hmi_service/plc_service/test_management_service/hmi_mapper/io_table/test_runner_panel/variable_checker等 | ✅ |
| fb_registry.py统一映射 | sync/ 新增 FB标识符→文档类型映射注册表 | ✅ |
| sync GUI集成(3按钮) | MainWindow 同步面板: 版本检查/CHG生成/IFC生成 | ✅ |
| HMI/IO/测试运行器降级占位 | 降级为占位符，移除死代码依赖 | ✅ |

### 3.8 Sprint 13 交付物 (V2.0-R2 已交付)

| 交付物 | 说明 | 状态 |
|--------|------|------|
| QSS语法修复(C-05) | 修复QSS解析错误导致的样式失效 | ✅ |
| 导航映射修复(C-06) | 修复导航跳转映射错误 | ✅ |
| 内联样式迁移(H-09) | 内联样式迁移到QSS主题系统 | ✅ |
| StatCard修复(H-10) | 修复统计卡片显示异常 | ✅ |
| 侧边栏重构(H-11) | 侧边栏布局与交互重构 | ✅ |
| Controller模式(3个) | ProjectController/SyncController/DashboardController | ✅ |
| cleanup架构(4组件) | DiagnosticPanel/ScoreRingWidget/BarChartWidget/SpecCheckPanel资源清理 | ✅ |
| SpecCheck Dock创建 | 规范检查面板迁移为Dock组件 | ✅ |
| QLayout修复 | 修复布局约束警告 | ✅ |
| 退出异常消除(sip.delete) | 使用sip.delete替代del消除退出时COM异常 | ✅ |

---

## 4. 文档与索引关系

| 文档 | 用途 |
|---|---|
| `00_项目基础信息/000_通用项目立项表_PM-*.md` | 立项范围、资源、约束 |
| `00_项目基础信息/001_产品需求文档_PRD-*.md` | 需求与验收标准 |
| `01_项目文档/02_规划过程/007~009` | 架构/详细设计/API 契约 |
| `01_项目文档/03_执行过程/README.md` | Sprint 进度、已知问题、测试统计（每日更新） |

---

*文档版本: PLAN-V2.0.0 | 最后更新: 2026-05-22*
*变更记录: V2.0 深度审查完成 — 13项修复+6项降级+cleanup架构统一*
