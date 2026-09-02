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
- current_focus: SW-2026-008 驾驶舱 Dogfooding 可行性评估与迭代规划（第四批，规划态，2026-09-01）
- milestone: 工作树治理第一轮 ✅ 已完成；驾驶舱迁移第一/二批 ✅ 已验证；文档资产第一轮归档 ✅ 已验证；Dogfooding 架构与 WBS ✅ 待审批
- code_baseline: SW-2026-008 当前代码基线 V1.2.3，默认运行位为 `00_Infrastructure/auto_pm`
- acceptance: 路径修正 ✅ + 工具链口径统一 ✅ + 风险台账对齐 ✅ + PM_SESSION精简 ✅ + 基础设施双轨运行 ✅ + 活文档/历史档案分层 ✅

## 3. Status Summary（当前状态摘要）
- in_progress:
  - 审核驾驶舱、PM 技能、全栈技能和 PLC 技能组成受控 Dogfooding 闭环的可行性，不启动代码实现
- next_up:
  - 用户批准后先执行 WBS 0，以规划前 243 条变更快照及本规划新增 SYS 资产为范围，分组收口并恢复干净基线
  - 基线干净后另行报批 PM handoff 契约修复和稳定/候选双环境隔离
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

## 5. Logs（按事件沉淀）
- change_log:
  - 2026-09-01 驾驶舱 Dogfooding 评估：结论为有条件可行；采用 PM 总控、全栈实现、PLC 域验收、稳定版驾驶舱外部复核的受控自托管模型
  - 2026-09-01 SW-2026-008 文档资产评估：闭环变更单、V8-V14原型、V1.1.0历史交付物、旧迭代计划和过期诊断报告移入归档；不删除变更管理资产
  - 2026-09-01 迁移前工作树治理：已提交忽略规则、规范治理、DJ-2026-009、DJ-2026-005；高风险删除项暂缓处理
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
    - 01_项目文档/03_分阶段整改路线图_PM.md
    - 01_项目文档/04_风险登记册_REP.md
    - 01_项目文档/05_变更准入规则_DEV.md
    - ..\README.md
    - ..\.trae\documents\README.md
  - artifacts:
    - `SYS-2026-001_WorkspaceGovernance/`
  - impact: 工作区级变更具备统一入口、文档骨架和治理边界
  - risks: 历史计划尚未全部收编，后续仍需持续清理

## 8. Handoff Notes
- archive: 2026-09-01 历史交接记录已完整保存至 `05_收尾/PM_SESSION归档/PM_SESSION_SYS-2026-001_handoff_notes_20260901.md`
- current_state: 当前工作空间级控制面为 `00_Infrastructure/auto_pm`，旧 SW 母体保留产品文档、变更历史和回退参考。
- current_focus: 以受控 Dogfooding 迭代驾驶舱，先完成 WBS 0 基线分流，再修复 handoff CLI/Saga 和稳定/候选双环境。
- handoff_gap: PM 技能描述的 handoff CLI 尚未实现，现有代码仅覆盖待办读取和 GUI PM 收口上下文。
- gate: 候选版本必须通过自身测试和稳定版外部复核，PM_SESSION、CHG、台账和反馈完成对账后才可收口。
- watchouts: PLC 技能只做域验收；不得将 `DJ-2026-005` 未全绿研发现场混入驾驶舱治理提交。

## 9. Next Actions
- [完成] 工作树剩余高风险项裁决 | result=已恢复 `.dockerignore`/`docs/docker`/历史设备样例删除、通用 README 与 SW-2026-009 db 漂移；PM_SESSION 漂移经门禁证明后转为最小合规补丁
- [完成] SW-2026-008 驾驶舱迁移第一批 | result=基础设施运行位建立，根入口与 editable install 已切换，旧项目母体保留回退
- [完成] SW-2026-008 驾驶舱迁移第二批 | result=Doc-as-Code 代码源优先基础设施位，旧母体降级标注完成，版本解析防回归测试通过
- [已验证] SW-2026-008 文档资产第一轮治理 | precondition=旧母体文档资产完成分类 | done_when=完成验证、台账对账和治理提交；变更管理资产保持 archive-only
- [后续] SW-2026-008 活跃文档迁移评估 | precondition=本批验证通过且唯一真源/同步策略明确 | done_when=决定是否迁移活跃规划/交付文档，不自动迁移历史变更档案
- [待审批] SW-2026-008 驾驶舱 Dogfooding WBS 0 | precondition=用户批准本方案 | done_when=规划前 243 条跨项目变更及本规划新增 SYS 资产完成分组裁决，形成干净且可回退的稳定基线

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

