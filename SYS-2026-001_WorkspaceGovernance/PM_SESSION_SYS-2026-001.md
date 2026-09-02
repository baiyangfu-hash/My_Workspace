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
- current_focus: SW-2026-008 驾驶舱 Dogfooding WBS 7 执行（WBS 0/1/2/3/4/5/6 已完成，2026-09-01）
- milestone: 工作树治理第一轮 ✅ 已完成；驾驶舱迁移第一/二批 ✅ 已验证；文档资产第一轮归档 ✅ 已验证；Dogfooding WBS 0 ✅ 已完成；WBS 1 ✅ 已完成；WBS 2 ✅ 已完成；WBS 3 ✅ 已完成；WBS 4 ✅ 已完成；WBS 5 ✅ 已完成；WBS 6 ✅ 已完成；WBS 7 ▶ 执行中
- code_baseline: SW-2026-008 当前代码基线 V1.2.3，默认运行位为 `00_Infrastructure/auto_pm`
- acceptance: 路径修正 ✅ + 工具链口径统一 ✅ + 风险台账对齐 ✅ + PM_SESSION精简 ✅ + 基础设施双轨运行 ✅ + 活文档/历史档案分层 ✅ + WBS 0 基线清洁与可回退 ✅ + WBS 1 真源与版本指纹锁定 ✅

## 3. Status Summary（当前状态摘要）
- in_progress:
  - 以 DJ-2026-005 为 PLC 域标杆，完成驾驶舱 checker、模板、变量表和 HTML 原型的静态消费验收
- next_up:
  - 完成 WBS 7：形成 PLC 域验收矩阵，区分已验证、待验证和真实硬件外部验证
  - WBS 7 完成后进入 WBS 8：选择第二个中风险 Dogfood 功能
- open_questions:
  - 项目简称保持 `WorkspaceGovernance`（已确认）
  - `handoff` 已完成 v1 CLI 与基础原子消费；PM_SESSION、变更单和反馈的统一落账仍属于后续 Saga 工作包
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
- 2026-09-01 | skill=pm-workflow | mode=SW-2026-008 Dogfooding WBS 2 handoff.v1 契约修复
  - goal: 让 PM 技能声明的 handoff create/list/show/close 命令与驾驶舱实现一致，并锁定执行技能回执边界
  - artifact: `00_Infrastructure/auto_pm/auto_pm/application/core/ai_handoff_service.py`、`00_Infrastructure/auto_pm/auto_pm/ui/cli/handoff.py`、`.trae/skills/pm-workflow/refs/handoff_schema.md`
  - evidence: 11 个 handoff 核心/CLI 测试通过；CLI help、create、list、show、close 实机冒烟通过；ruff 通过；运行态 handoff 目录已加入忽略规则
  - decision: 使用 `handoff.v1`；执行技能只写结果回执，PM 负责消费和业务台账落账；保留旧文件名扫描兼容；WBS 3 继续强化 Saga 故障恢复
  - result: ✅ WBS 2 完成；未迁移历史变更档案，未修改 Obsidian 规范内容
- 2026-09-01 | skill=pm-workflow | mode=SW-2026-008 Dogfooding WBS 3 Saga 原子收口
  - goal: 为 handoff 消费增加预检、失败证据、幂等重试和跨项目身份保护，确保失败不留下半成品
  - artifact: `00_Infrastructure/auto_pm/auto_pm/application/core/ai_handoff_service.py`、`00_Infrastructure/auto_pm/auto_pm/ui/cli/handoff.py`
  - evidence: 16 个 handoff 核心/CLI 测试通过；覆盖预检不消费、跨项目拒绝、原子写入故障注入、失败事件记录、锁释放和 retry_close；ruff 通过
  - decision: 失败只保留 `pending` 并记录至被忽略的 `.auto-pm/reports/dogfood/handoff-saga/`；成功后才原子切换 `consumed`；重试复用相同幂等协议
  - result: ✅ WBS 3 完成；跨 PM_SESSION/CHG/ledger/feedback 的业务落账仍由 PM 负责，WBS 4 开始隔离基建
- 2026-09-01 | skill=pm-workflow | mode=SW-2026-008 Dogfooding WBS 4 稳定/候选隔离基建
  - goal: 让稳定控制面能够从外部读取候选 worktree 的状态、指纹、路径白名单和运行态污染，不执行候选代码
  - artifact: `00_Infrastructure/auto_pm/auto_pm/application/core/dogfood_runner.py`、`00_Infrastructure/auto_pm/auto_pm/ui/cli/dogfood.py`
  - evidence: 6 个隔离核心/CLI 测试通过；覆盖候选路径限制、稳定侧指纹、白名单违规、运行态变化、干净树创建候选和报告临时文件清理；ruff 通过
  - decision: 候选 worktree 只能创建在 `.auto-pm/worktrees/`；`prepare` 拒绝脏稳定树，`review` 只由 stable-control-plane 生成 verdict；证据写入忽略的 `.auto-pm/reports/dogfood/`
  - result: ✅ WBS 4 完成；尚未对当前工作树执行真实候选创建，原因是 WBS2/3 变更尚未取得 Git 提交权限
- 2026-09-01 | skill=pm-workflow | mode=SW-2026-008 Dogfooding WBS 5 只读 Grooming Pilot
  - goal: 用驾驶舱管理自身的只读预研请求，验证 create/list/show/preflight/close 和 PM 消费链
  - artifact: `.auto-pm/handoffs/AI-20260901-WBS5.json`（运行态）及 `.auto-pm/handoffs/AI-20260901-WBS5.result.json`（运行态回执）
  - evidence: 驾驶舱实际创建请求；preflight 返回 `ok=true, already_consumed=false`；PM close 返回 `status=consumed`；`changed_files=[]`；请求和回执均未进入 Git
  - decision: 只读 Pilot 不修改产品代码，不伪造 CHG；候选 worktree 真实复核留待稳定提交权限恢复后补跑
  - result: ✅ WBS 5 完成（只读闭环通过）；候选发布仍未批准
- 2026-09-01 | skill=pm-workflow | mode=SW-2026-008 Dogfooding WBS 6 doctor 版本真源修复
  - goal: 消除 doctor 在工作空间根目录缺少 pyproject.toml 时回退到旧版本常量的问题
  - artifact: `00_Infrastructure/auto_pm/auto_pm/ui/cli/doctor.py`、`00_Infrastructure/auto_pm/tests/cli/test_doctor.py`
  - evidence: doctor 实机输出 `1.2.3` 并显示基础设施包 pyproject source；7 个 doctor/dogfood 相关测试通过；ruff 通过
  - decision: 版本优先来自当前加载的 `auto_pm.__version__`，不再使用 `1.1.0` 硬编码；版本源路径显式展示
  - result: ✅ WBS 6 完成；仍未触碰真实 PLC/HMI 硬件

## 8. Handoff Notes
- archive: 2026-09-01 历史交接记录已完整保存至 `05_收尾/PM_SESSION归档/Handoff_Notes_SYS-2026-001_20260901.md`
- current_state: 当前工作空间级控制面为 `00_Infrastructure/auto_pm`，旧 SW 母体保留产品文档、变更历史和回退参考。
- current_focus: 以受控 Dogfooding 迭代驾驶舱，WBS 0/1/2/3/4/5/6 已完成；当前进入 DJ-2026-005 PLC 域消费验收。
- handoff_gap: handoff.v1 已具备预检、原子消费、失败证据和重试；PM_SESSION、CHG、台账和反馈的业务落账仍保持 PM 单一 owner。
- gate: 候选版本必须通过自身测试和稳定版外部复核，PM_SESSION、CHG、台账和反馈完成对账后才可收口。
- watchouts: PLC 技能只做域验收；不得将 `DJ-2026-005` 未全绿研发现场混入驾驶舱治理提交。
- 代码基线 V1.2.3
- status: [已验证] WBS 0/1/2/3/4/5/6 完成；WBS 7 执行中；工作树在每个提交门前保持可解释

## 9. Next Actions
- [完成] 工作树剩余高风险项裁决 | result=已恢复 `.dockerignore`/`docs/docker`/历史设备样例删除、通用 README 与 SW-2026-009 db 漂移；PM_SESSION 漂移经门禁证明后转为最小合规补丁
- [完成] SW-2026-008 驾驶舱迁移第一批 | result=基础设施运行位建立，根入口与 editable install 已切换，旧项目母体保留回退
- [完成] SW-2026-008 驾驶舱迁移第二批 | result=Doc-as-Code 代码源优先基础设施位，旧母体降级标注完成，版本解析防回归测试通过
- [已验证] SW-2026-008 文档资产第一轮治理 | precondition=旧母体文档资产完成分类 | done_when=完成验证、台账对账和治理提交；变更管理资产保持 archive-only
- [后续] SW-2026-008 活跃文档迁移评估 | precondition=本批验证通过且唯一真源/同步策略明确 | done_when=决定是否迁移活跃规划/交付文档，不自动迁移历史变更档案
- [完成] SW-2026-008 驾驶舱 Dogfooding WBS 0 | result=规划前变更已分组裁决；未验证漂移恢复；未验证 PLC 现场文件可逆停放；备份与证据已保留；工作树干净
- [完成] SW-2026-008 驾驶舱 Dogfooding WBS 1 | result=形成 infra/SW/SYS 唯一真源矩阵、入口版本指纹和双轨退出条件；旧母体代码冻结
- [完成] SW-2026-008 驾驶舱 Dogfooding WBS 2 | result=实现 handoff.v1 create/list/show/close、request_id 幂等定位、证据和 CHG 前置校验；技能命令已对齐；运行态已忽略
- [完成] SW-2026-008 驾驶舱 Dogfooding WBS 3 | result=预检、文件锁、原子替换、幂等指纹、失败事件和 retry_close 已完成；故障注入后 pending 可恢复，重复关闭无重复状态
- [完成] SW-2026-008 驾驶舱 Dogfooding WBS 4 | result=prepare/inspect/review 隔离 runner 已完成；候选只能位于 `.auto-pm/worktrees/`；稳定脏树拒绝创建候选；外部复核报告可留存
- [完成] SW-2026-008 驾驶舱 Dogfooding WBS 5 | result=实际创建 `AI-20260901-WBS5` 只读请求；preflight 与 PM close 均成功；changed_files 为空；未产生产品变更
- [完成] SW-2026-008 驾驶舱 Dogfooding WBS 6 | result=doctor 版本来自当前基础设施包 `__version__`，实机显示 1.2.3；回归测试与 ruff 通过
- [进行中] SW-2026-008 驾驶舱 Dogfooding WBS 7 | precondition=WBS 6 低风险代码闭环完成 | done_when=DJ-2026-005 的 PLC checker、文档、变量表、HTML 原型静态验收矩阵完成；真实硬件项明确为外部验证

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

