# PM_SESSION_SYS-2026-001

## 0. Meta
- project_id: SYS-2026-001
- project_name: WorkspaceGovernance
- project_root: c:\Users\fubai\Documents\My_Workspace\SYS-2026-001_WorkspaceGovernance
- last_updated: 2026-09-01
- owners: fubai

## 1. Positioning（项目定位）
- one_liner: 面向整个工作空间的系统级治理项目，统一入口、职责边界、风险台账和长期整改节奏。
- users: 工作空间维护者、AI助手、未来的自己
- non_goals: 不重排现有 PLC/软件主目录，不把治理项目做成新的开发工具，不在首轮直接迁移大量历史文件
- key_principle: 先建立单一真源，再做渐进收编；先做映射和边界，后做清理和自动化

## 2. Current Focus（当前焦点）
- current_focus: SW-2026-008 驾驶舱 Dogfooding WBS 2 准备（WBS 0/1 已完成，2026-09-01）
- milestone: 工作树治理第一轮 ✅ 已完成；驾驶舱迁移第一/二批 ✅ 已验证；文档资产第一轮归档 ✅ 已验证；Dogfooding WBS 0 ✅ 已完成；WBS 1 ✅ 已完成；WBS 2 ⏸ 待审批
- code_baseline: SW-2026-008 当前代码基线 V1.2.3，默认运行位为 `00_Infrastructure/auto_pm`
- acceptance: 路径修正 ✅ + 工具链口径统一 ✅ + 风险台账对齐 ✅ + PM_SESSION精简 ✅ + 基础设施双轨运行 ✅ + 活文档/历史档案分层 ✅ + WBS 0 基线清洁与可回退 ✅ + WBS 1 真源与版本指纹锁定 ✅

## 3. Status Summary（当前状态摘要）
- in_progress:
  - 维持 WBS 1 后的干净稳定基线；准备 WBS 2 handoff v1 契约设计，不启动驾驶舱代码实现
- next_up:
  - 待用户单独批准后执行 WBS 2：定义 handoff v1 的 request/schema、create/list/show/close 影响面和兼容边界
  - WBS 2 完成后再具体报批 Saga 原子收口及稳定/候选双环境隔离
- open_questions:
  - 项目简称保持 `WorkspaceGovernance`（已确认）
  - `handoff` 目前只有待办读取与 GUI 收口上下文，CLI 创建/消费/Saga 收口尚未实现；PM 技能命令需与驾驶舱能力重新对齐
- risks_dependencies:
  - 依赖现有规范仓库路径稳定
  - 依赖 `auto-pm` 作为统一工具链入口
  - 双轨期需防止旧 `SW-2026-008` 母体代码与基础设施位代码长期分叉
  - 活跃规划/交付文档暂留旧母体，后续迁移前需先确定唯一真源，避免文档双份维护
  - `CHG-SCPT-2026-161` 至 `164` 保留历史结构告警，后续单独治理，不在本批改写审计证据
  - 驾驶舱迭代自身存在循环自证风险，必须采用稳定控制面复核候选开发面的双钥匙门禁
  - WBS 0 中发现的 22 个未验证 PLC 研发现场文件已停放于 `.auto-pm/reports/archive/wbs0-backup-20260901/parked-current/`，仅作为可回退备份，不纳入治理提交
  - WBS 1 后代码真源已锁定，但活跃产品文档仍在 SW 母体；文档单轨迁移必须等待同步策略和门禁先行
- spec_compliance:
  - last_check: 2026-08-26
  - result: 项目编号 `SYS-2026-001` 符合 `DEV-001` 语义约束；已校正为 `auto-pm` 口径

## 4. Artifacts Index（文档索引）
- charter: 00_项目基础信息/01_项目章程_PM.md
- req: 01_项目文档/01_需求分析_REQ.md
- dsn: 01_项目文档/02_工作区治理方案_DES.md
- tec: 01_项目文档/03_分阶段整改路线图_PM.md
- int: 01_项目文档/05_变更准入规则_DEV.md
- risk: 01_项目文档/04_风险登记册_REP.md
- governance_rule: 01_项目文档/05_变更准入规则_DEV.md
- sw_doc_audit: 01_项目文档/06_SW-2026-008_文档资产评估_REP.md
- cockpit_dogfood_plan: 01_项目文档/07_SW-2026-008_驾驶舱Dogfooding迭代方案与WBS_PM.md
- source_of_truth_matrix: 01_项目文档/08_SW-2026-008_唯一真源矩阵与版本指纹_REP.md

## 5. Logs（按事件沉淀）
- change_log:
  - 2026-09-01 驾驶舱 Dogfooding 评估：结论为有条件可行；采用 PM 总控、全栈实现、PLC 域验收、稳定版驾驶舱外部复核的受控自托管模型
  - 2026-09-01 SW-2026-008 文档资产评估：闭环变更单、V8-V14原型、V1.1.0历史交付物、旧迭代计划和过期诊断报告移入归档；不删除变更管理资产
  - 2026-09-01 迁移前工作树治理：已提交忽略规则、规范治理、DJ-2026-009、DJ-2026-005；高风险删除项暂缓处理
  - 2026-09-01 Dogfooding WBS 1：唯一真源矩阵、版本/Git 指纹、旧母体代码冻结规则和双轨退出条件已完成；未改代码、未迁移文档
  - 2026-06-15 P1计划收编：4份历史长期计划映射完成，执行状态评估完成，遗留事项已登记
  - 2026-06-16 P1移交完成：6项遗留事项移交至SW-2026-006，2项移交至SW-2026-004，2项归属SYS-2026-001自身
  - 2026-06-16 P2节奏固化启动：路线图更新，P2执行事项登记
  - 2026-06-15 创建 `SYS-2026-001` 治理项目，建立工作区级 PM_SESSION
- iteration_log:
  - P0 启动: 统一工作区治理入口和职责边界
  - P1 计划收编: 4份历史计划映射+执行状态评估+遗留事项登记+跨项目移交 ✅
  - P2 节奏固化: 进行中
- 2026-06-16 P2节奏固化完成：P2.1-P2.4全部完成（2026-08-26重基线：P2.4已吸收进工具链统一口径）
- bug_log:
  - 2026-06-15 识别到错误使用 `SW-` 立项的语义风险，已改为 `SYS-`
- refactor_log:
  - 2026-06-15 将“根目录散装计划驱动”升级为“项目化治理驱动”
- release_log:
  - (待补充)
- spec_change_log:
  - 2026-06-15 按 `DEV-001` 与 `PM-004` 校正治理项目类型和会话载体

## 6. Implementation Log
- 2026-09-01 | skill=pm-workflow | mode=SW-2026-008 Dogfooding WBS 0 基线治理
  - goal: 在不启动驾驶舱代码迭代的前提下，将规划前工作树变更按风险分流并恢复可回退的干净基线
  - scope: 规划前 243 条变更快照、Dogfooding 规划资产及其关联运行态；未验证 PLC 现场文件不纳入提交
  - actions: 保留文件级备份；恢复未验证的删除/漂移；清理根目录 `.coverage`；恢复旧 PLC 工作树漂移；将 22 个未验证 PLC 文件可逆停放到备份目录
  - evidence: `git status --short --untracked-files=all` 为空；PM_SESSION 门禁通过；规范检查通过；未修改驾驶舱运行代码
  - backup: `.auto-pm/reports/archive/wbs0-backup-20260901/`（含状态、差异补丁和现场文件清单）
  - result: ✅ WBS 0 完成；基线可进入 WBS 1 评估，尚未启动 handoff CLI/Saga 或稳定/候选隔离实现
- 2026-09-01 | skill=pm-workflow | mode=SW-2026-008 Dogfooding WBS 1 唯一真源锁定
  - goal: 明确驾驶舱代码、产品账、治理账、规范库、技能库、PLC 标杆和运行态的唯一活跃 owner，记录可复核版本指纹
  - artifact: `01_项目文档/08_SW-2026-008_唯一真源矩阵与版本指纹_REP.md`
  - evidence: 根入口解析到 `00_Infrastructure/auto_pm`；包/CLI/pyproject/CHANGELOG/产品与治理 PM_SESSION 均为 `V1.2.3`；Git tree 与入口 SHA 已记录
  - decision: 旧母体代码冻结为只读回退参考；活跃产品文档和历史变更资产暂留 SW 母体；WBS 2 起需单独报批
  - result: ✅ WBS 1 完成；未修改驾驶舱代码、未迁移活跃文档、未删除变更管理资产

## 8. Handoff Notes
- archive: 2026-09-01 历史交接记录已完整保存至 `05_收尾/PM_SESSION归档/Handoff_Notes_SYS-2026-001_20260901.md`
- current_state: 当前工作空间级控制面为 `00_Infrastructure/auto_pm`，旧 SW 母体保留产品文档、变更历史和回退参考。
- current_focus: 以受控 Dogfooding 迭代驾驶舱，WBS 0 基线分流和 WBS 1 唯一真源锁定已完成；下一步先定义 handoff v1，再修复 Saga 和稳定/候选双环境。
- handoff_gap: PM 技能描述的 handoff CLI 尚未实现，现有代码仅覆盖待办读取和 GUI PM 收口上下文。
- gate: 候选版本必须通过自身测试和稳定版外部复核，PM_SESSION、CHG、台账和反馈完成对账后才可收口。
- watchouts: PLC 技能只做域验收；不得将 `DJ-2026-005` 未全绿研发现场混入驾驶舱治理提交。
- 代码基线 V1.2.3
- status: [已验证] WBS 0/1 完成；工作树干净，WBS 2 尚未启动

## 9. Next Actions
- [完成] 工作树剩余高风险项裁决 | result=已恢复 `.dockerignore`/`docs/docker`/历史设备样例删除、通用 README 与 SW-2026-009 db 漂移；PM_SESSION 漂移经门禁证明后转为最小合规补丁
- [完成] SW-2026-008 驾驶舱迁移第一批 | result=基础设施运行位建立，根入口与 editable install 已切换，旧项目母体保留回退
- [完成] SW-2026-008 驾驶舱迁移第二批 | result=Doc-as-Code 代码源优先基础设施位，旧母体降级标注完成，版本解析防回归测试通过
- [已验证] SW-2026-008 文档资产第一轮治理 | precondition=旧母体文档资产完成分类 | done_when=完成验证、台账对账和治理提交；变更管理资产保持 archive-only
- [后续] SW-2026-008 活跃文档迁移评估 | precondition=本批验证通过且唯一真源/同步策略明确 | done_when=决定是否迁移活跃规划/交付文档，不自动迁移历史变更档案
- [完成] SW-2026-008 驾驶舱 Dogfooding WBS 0 | result=规划前变更已分组裁决；未验证漂移恢复；未验证 PLC 现场文件可逆停放；备份与证据已保留；工作树干净
- [完成] SW-2026-008 驾驶舱 Dogfooding WBS 1 | result=形成 infra/SW/SYS 唯一真源矩阵、入口版本指纹和双轨退出条件；旧母体代码冻结；本阶段不实现 handoff CLI
- [待审批] SW-2026-008 驾驶舱 Dogfooding WBS 2 | precondition=WBS 1 已完成且工作树干净 | done_when=定义 handoff v1 request/schema、create/list/show/close 影响面、兼容边界和验收矩阵；不实现 Saga

## Spec Snapshot（更新至2026-08-26）

> 本项目是系统级治理项目，不绑定单一技术栈实现，但仍引用 PM 规范作为工作基线。
> 2026-08-26重基线：已统一工具链口径为 `auto-pm`，校正路径引用。

| spec_id | 版本 | 记录日期 | 说明 |
|---------|------|---------|------|
| DEV-001 | V1.0.2 | 2026-06-16 | 通用项目名称命名规范 |
| DEV-002 | V1.0.1 | 2026-06-16 | 通用项目工作流命名规范 |
| DEV-003 | V1.1.0 | 2026-06-16 | 跨资源库命名统一规范 |
| PM-004 | V1.2.0 | 2026-06-16 | PM_WORKFLOW总控Skill使用说明 |
| PM-042 | V1.0.0 | 2026-08 | PM_SESSION管理规程（按pm-workflow当前规程） |
| PROJ-016 | V1.0.0 | 2026-06-16 | 通用项目结构模板 |

