# PM_SESSION_SW-2026-008

## 0. Meta

- project_id: SW-2026-008
- project_name: auto-pm（自动化项目管理工具）
- project_root: 01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具
- runtime_root: 00_Infrastructure/auto_pm
- runtime_status: 双轨运行中，基础设施位为默认运行入口，旧项目母体保留为历史记录与回退来源
- target_source_of_truth: SW-2026-008 为唯一研发母体；00_Infrastructure/auto_pm 只作稳定部署容器
- architecture_transition_status: 目标架构已批准，物理迁移、入口切换和发布尚未授权
- version: V1.2.3
- last_updated: 2026-09-05
- owners: fubai

## 1. Positioning（项目定位）

- one_liner: 面向电气自动化工程师的本地项目作业系统，用于统一管理 PLC 项目结构、工程文档、变更闭环、调试记录、质量门禁和交付证据
- users: 自动化工程师（兼PLC+Python开发）、AI技能（pm-workflow/plc-electrical-engineer）
- non_goals: 不做在线协作、不做PLC代码生成、不做CI/CD管理
- owners: fubai

## 2. Current Focus（当前焦点）

- current_focus: **NG-WP-10 母体全量 Gate 1 已整改复跑全绿（10 项门禁 Exit 0，pytest 1900 passed）；当前执行 NG-WP-11 冻结候选提交与制品构建（User 已于 2026-09-05 批准）；NG-WP-12 起未授权**。
- risks_dependencies:
  - Ruff 静态代码检查已实现 100% Clean Exit (0 告警)
  - IndustrialErrorMapper 统一异常转译上线并补充 10 项单测
  - 新增 SHC-017 契约对账器，覆盖 C1~C4 四条契约（阈值/状态机/编号格式/门禁口径）
  - spec 检查器总量增至 SHC-001~017，tests/spec 回归 174 passed
- spec_compliance:
  - last_check: 2026-08-23
  - result: 代码基线 V1.2.3（CHG-SCPT-2026-164 落地完成，P2 质量收敛与友好排障全部闭环，全量单测全绿）。

## 3. Status Summary

- 2026-09-05 [已验证] NG-WP-14 Gate 2：非活动槽 release `1.2.3-d41eb38` 部署与净化验证全过；根入口 API 缺陷修复（run_qml_gui）；发布申请要素齐备（source commit/version/manifest 哈希/目标槽/回退目标 null）。
- 2026-09-05 [已验证] NG-WP-13 根入口与环境解耦：main.py/bootstrap/launch/钩子 v3 全部双槽化且去 editable；全量回归 1946 passed/18 skip；隔离矩阵六场景全过、provenance 无母体泄漏；candidate `d41eb38`。
- 2026-09-05 [已验证] NG-WP-12 稳定部署双槽骨架：`00_Infrastructure/auto_pm` 新增 launcher/releases/双指针/manifest（未部署 active、未切入口）；母体 `auto_pm/application/core/deployment_service.py` fail-closed 双槽服务提交 `92e2c94`；稳定侧 `git_hook.py` 模板遗留修复完成。
- 2026-09-05 [已验证] NG-WP-11 冻结候选提交与制品构建：candidate `87183fb`（262 文件）+ wheel `auto_pm-1.2.3` SHA-256 `ca47b787…`，886 文件 manifest、依赖锁副本、空目录安装验证与 provenance 探针全通过。
- 2026-09-05 [已验证] NG-WP-03 至 NG-WP-10：在 detached candidate 完成契约、事务、决策、编排器与归档的逐包回收加固，Gate 1 整改复跑 10 项门禁全绿（pytest 1900 passed/16 skipped），candidate 变更 100% 位于批准白名单。
- current_status: [架构迁移冻结] 目标真源已裁决为 SW-2026-008 母体；detached candidate 已通过全量 Gate 1（NG-WP-03 至 NG-WP-10 逐包收口）；稳定部署 `00_Infrastructure/auto_pm` 保持只读，在 Gate 2 与首个稳定发布完成前不得切换或清理。
- in_progress: NG-WP-14 已完成：release `1.2.3-d41eb38`（450 文件）持锁构建登记，Gate 2 十用例净化验证全过，并修复真实入口 API 缺陷（run_qml_app→run_qml_gui）；指针仍为 null，NG-WP-15 原子切流。
- completed_milestones:
  - 2026-09-04 [已验证] CHG-SCPT-2026-177 Cockpit OS Phase 3 WBS 3.1 项目全生命周期归档与恢复引擎：实现 ProjectArchiveService 核心引擎、领域就近路由、三道硬门禁、归档台账自动化（ARC-YYYYMMDD-XXX流水号）与逆向恢复，扩展 ProjectScanner.scan_archived 与 CLI archive/restore/list/delete 命令，单测 45 passed 全绿。
  - 2026-09-04 [已验证] CHG-SCPT-2026-176 Cockpit OS Phase 2 WBS 2.2 工作流执行内核流水线 WorkflowOrchestrator.execute：实现执行流水线、项目/单据/白名单强门禁、事务沙箱原子回滚、verify_only预检与auto_commit提交，单测 21 passed 全绿。
  - 2026-09-04 [已验证] CHG-SCPT-2026-175 Cockpit OS Phase 2 WBS 2.1 工作流编排内核流水线 WorkflowOrchestrator.plan：实现方案规划流水线、项目校验、草稿复用/生成、规范动态绑定与决策包锁死，单测 15 passed 全绿。
  - 2026-09-04 [已验证] CHG-SCPT-2026-174 Cockpit OS Phase 1 WBS 1.1 事务沙箱 ChangeTransactionManager 与 WBS 1.2 自动化测试：实现 ChangeTransaction 与 ChangeTransactionManager，快照备份、新建追踪、原子提交与回滚上下文管理器，单测 19 passed 100% 覆盖率全绿。
  - 2026-09-04 [已验证] CHG-SCPT-2026-173 Cockpit OS Phase 0 WBS 0.1 契约层强类型 DTO 纯净定义：实现 TransactionStatus 枚举及 5 个工作流核心 DTO，单测 17 passed 全绿。
  - 2026-09-04 [已验证] CHG-SCPT-2026-172 W2批次可恢复 PM Saga 事务日志：实现 8 步 WAL 顺序日志、Checkpoint 故障恢复、补偿回滚与 CLI 扩展。
  - 2026-09-04 [已验证] CHG-SCPT-2026-171 证据门禁扩展：Scope Gating 决策包白名单越界拦截、跨资产变更单存在性与真实证据物理硬门禁闭环。
  - 2026-09-03 [已验证] CHG-SCPT-2026-170 驾驶舱防空壳实质化体系、结构化决策包契约（W0）与跨领域穿透门禁（W1-1）落地闭环。
  - 2026-08-27 [已验证] CHG-SCPT-2026-167 契约对账器：新增 SHC-017 SkillContractDriftChecker，以代码为唯一真源校验技能文档（C1~C4）。
  - 2026-08-27 [已验证] CHG-SCPT-2026-166 落账门禁下沉：StageGateEngine G3 新增落账完整性 BLOCKER，PmSessionCheckService 新增落账新鲜度 WARN。
  - 2026-08-22 [已验证] CHG-SCPT-2026-163 驾驶舱 P1 级架构加固与测试深化（V1.2.2 发布）。
  - 2026-08-22 [已验证] CHG-SCPT-2026-162 驾驶舱严苛审计缺陷修复与安全加固（V1.2.1 发布）。
  - 2026-08-22 [已验证] 完成基于 ISO/IEC 25010 与 IEC 62443 的 100% 真实数据全维度严苛技术审计。
  - 2026-08-21 [已验证] CHG-SCPT-2026-161 驾驶舱工业逆向摄取 (PlcIngest) 与 HMI 拓扑自适应标准 (STD-909) 落地。
  - 2026-08-17 [已验证] 20 维全景 GUI 交互与弹窗深度矩阵测试通过，20 张真机快照存档。
  - 2026-08-16 [已验证] CHG-SCPT-2026-159 Clean Architecture 5 层整洁架构物理重构完成，消除平铺目录。
- open_questions:
  - [技术债已消除] 驾驶舱项目管理硬删除技术债已于 2026-09-04 通过 CHG-SCPT-2026-177 彻底消除，已全面建立领域就近路由、三道硬门禁、台账自动化与逆向恢复引擎。

## 4. Artifacts Index

- prd: 02_规划/001_产品需求文档_PRD.md
- int: 02_规划/002_接口文档_INT.md
- dsn: 02_规划/003_详细设计说明书_DSN.md
- tec: 02_规划/004_技术方案文档_TEC.md
- charter: 01_启动/001_项目立项章程_CHARTER.md
- matrix: 03_执行/001_系统模块版本演进矩阵_MATRIX.md
- test_plan: 05_收尾/003_测试策略与验收规程_TEST_PLAN.md
- user_guide: 06_交付物/001_用户操作指南与排障手册_USER_GUIDE.md

## 5. Logs（按事件沉淀）

- change_log:
  - 2026-09-04 CHG-SCPT-2026-177 Cockpit OS Phase 3 WBS 3.1 项目全生命周期归档与恢复引擎：落地 ProjectArchiveService、领域就近路由、三道硬门禁、归档台账自动化（ARC-YYYYMMDD-XXX流水号）与逆向恢复，单测 45 passed。
  - 2026-09-04 CHG-SCPT-2026-176 Cockpit OS Phase 2 WBS 2.2 工作流执行内核流水线 WorkflowOrchestrator.execute：落地执行流水线与 ChangeTransactionManager 事务沙箱集成与自动回滚，单测 21 passed。
  - 2026-09-04 CHG-SCPT-2026-175 Cockpit OS Phase 2 WBS 2.1 工作流编排内核流水线 WorkflowOrchestrator.plan：打通方案规划流水线，组合领域服务，单测 15 passed。
  - 2026-09-04 CHG-SCPT-2026-174 Cockpit OS Phase 1 WBS 1.1 事务沙箱 ChangeTransactionManager：落地快照备份隔离、新建追踪、原子回滚与提交、异常上下文管理器，单测 19 passed 100% 覆盖率。
  - 2026-09-04 CHG-SCPT-2026-173 Cockpit OS Phase 0 WBS 0.1 契约层强类型 DTO 纯净定义：落地 TransactionStatus 枚举与 5 个工作流核心 DTO，单测 17 passed。
  - 2026-09-04 CHG-SCPT-2026-172 W2批次 PM Saga 事务日志：落地 PmClosureSagaCoordinator，建立事务日志，支持失败注入与 checkpoint 恢复，单测 17 passed。
  - 2026-09-04 CHG-SCPT-2026-171 证据门禁扩展：在 AiHandoffService._validate_closure 中下沉 Scope Gating 白名单越界拦截、跨资产单据物理存在性校验与交付物真实性硬门禁，补充 5 组全量单测用例。
  - 2026-09-01 文档资产评估与归档治理：已将闭环 CHG-SCPT、历史 HTML 原型、V1.1.0 历史交付包、旧迭代计划和过期诊断报告移入对应 archive；活区仅保留当前可用入口和未闭环草稿单。

## 6. Execution Log Summary

- 2026-09-04：[已验证] 实施并闭环 CHG-SCPT-2026-177，落地 Cockpit OS Phase 3 WBS 3.1 项目全生命周期归档与恢复引擎，单测 45 passed + Ruff / Mypy 0 errors。
- 2026-09-04：[已验证] 实施并闭环 CHG-SCPT-2026-176，落地 Cockpit OS Phase 2 WorkflowOrchestrator.execute，单测 21 passed + Ruff / Mypy 0 errors。
- 2026-09-04：[已验证] 实施并闭环 CHG-SCPT-2026-175，落地 Cockpit OS Phase 2 WorkflowOrchestrator.plan，单测 15 passed + Ruff / Mypy 0 errors。
- 2026-09-04：[已验证] 实施并闭环 CHG-SCPT-2026-174，落地 Cockpit OS Phase 1 事务沙箱 ChangeTransactionManager，单测 19 passed 100% 覆盖率 + Ruff / Mypy 0 errors。
- 2026-09-04：[已验证] 实施并闭环 CHG-SCPT-2026-173，落地 Cockpit OS Phase 0 契约层 DTO，单测 17 passed + Ruff / Mypy 0 errors。
- 2026-09-04：[已验证] 实施并闭环 CHG-SCPT-2026-172，落地 C6 可恢复 PM Saga 事务日志与补偿机制，单元测试 17 passed 全绿。
- 2026-09-04：[已验证] 实施并闭环 CHG-SCPT-2026-171，落地 Scope Gating 与真实证据门禁，单元测试 9 passed + 全量门禁全绿。
- 2026-08-27：[已验证] 实施并闭环 CHG-SCPT-2026-167，新增 SHC-017 SkillContractDriftChecker 契约对账器，tests/spec 回归 174 passed + mypy 全绿 + spec check -c SHC-017 通过。

## 8. Handoff Notes

- 2026-09-04 | from=pm-workflow | mode=CHG-SCPT-2026-177 Phase 3 WBS 3.1 闭环
  - current_state: [已验证] Cockpit OS Phase 3 WBS 3.1 项目全生命周期归档与恢复引擎完成消费并落账闭环。
  - actions: 落地 ProjectArchiveService 核心引擎、三道硬门禁、台账自动化、逆向恢复与 CLI/GUI 双视图。
- 2026-09-04 | from=pm-workflow | mode=CHG-SCPT-2026-176 Phase 2 WBS 2.2 闭环
  - current_state: [已验证] Cockpit OS Phase 2 WBS 2.2 方案执行流水线 WorkflowOrchestrator.execute 完成消费并落账闭环。
- 2026-09-04 | from=pm-workflow | mode=CHG-SCPT-2026-175 Phase 2 WBS 2.1 闭环
  - current_state: [已验证] Cockpit OS Phase 2 WBS 2.1 方案规划流水线 WorkflowOrchestrator.plan 完成消费并落账闭环。
- 2026-09-04 | from=pm-workflow | mode=CHG-SCPT-2026-174 Phase 1 闭环
  - current_state: [已验证] Cockpit OS Phase 1 WBS 1.1 事务沙箱 ChangeTransactionManager 与 WBS 1.2 自动化测试完成消费并落账闭环。
- 2026-09-04 | from=pm-workflow | mode=CHG-SCPT-2026-173 Phase 0 闭环
  - current_state: [已验证] Cockpit OS Phase 0 WBS 0.1 契约层强类型 DTO 纯净定义完成消费并落账闭环。
- 2026-09-04 | from=pm-workflow | mode=CHG-SCPT-2026-172 W2 闭环
  - current_state: [已验证] W2 批次 C6 可恢复 PM Saga 事务日志完成消费并落账闭环。
- 2026-09-04 | from=pm-workflow | mode=CHG-SCPT-2026-171 W1-2 闭环
  - current_state: [已验证] W1-2 证据门禁扩展（Scope Gating、变更单存在性、交付物真实性）完成消费并落账闭环。
  - actions: AiHandoffService._validate_closure 下沉白名单越界拦截与跨资产物理真实性门禁。
- 2026-09-01 | from=Codex | mode=SW-2026-008 文档资产评估与归档治理

## 9. Next Actions

- [已完成] 单向发布架构规划基线 | result=ADR-SW008-001、差异回收方案、发布/回退 WBS 与验收标准已编制；治理在 SYS-2026-001 落账
- [待报批] WBS-1 全量只读差异事实包 + 决策链纠偏记录 | gate=未批准前不修复、移动、覆盖、删除、提交、发布或切流

- [x] 任务 13: [高优先技术债 / 必做] 实施 Cockpit OS Phase 3 WBS 3.1 项目全生命周期归档与恢复引擎（ProjectService.archive/restore、三道硬门禁、台账自动化、CLI/GUI双视图）
- [x] 任务 12: 实施并闭环 CHG-SCPT-2026-176（Cockpit OS Phase 2 WBS 2.2 工作流执行内核流水线 WorkflowOrchestrator.execute）
- [x] 任务 11: 实施并闭环 CHG-SCPT-2026-175（Cockpit OS Phase 2 WBS 2.1 工作流编排内核流水线 WorkflowOrchestrator.plan）
- [x] 任务 10: 实施并闭环 CHG-SCPT-2026-174（Cockpit OS Phase 1 WBS 1.1 事务沙箱 ChangeTransactionManager）
- [x] 任务 9: 实施并闭环 CHG-SCPT-2026-173（Cockpit OS Phase 0 WBS 0.1 契约层强类型 DTO 纯净定义）
- [x] 任务 8: 实施并闭环 CHG-SCPT-2026-172（W2 C6 可恢复 PM Saga 事务日志与补偿编排）
- [x] 任务 7: 实施并闭环 CHG-SCPT-2026-171（W1-2 证据门禁扩展与 Scope Gating）
- [x] 任务 5: 文档资产第一轮评估与归档治理（不删除变更管理资产）
- [ ] 任务 6: DJ-2026-009 业务验证（plc check + pm-session check + ledger reconcile）
