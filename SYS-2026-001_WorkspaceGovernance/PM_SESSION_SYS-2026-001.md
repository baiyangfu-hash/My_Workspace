# PM_SESSION_SYS-2026-001

## 0. Meta
- project_id: SYS-2026-001
- project_name: WorkspaceGovernance
- project_root: c:\Users\fubai\Documents\My_Workspace\SYS-2026-001_WorkspaceGovernance
- last_updated: 2026-09-05
- owners: fubai

## 1. Positioning（项目定位）
- one_liner: 面向整个工作空间的系统级治理项目，统一入口、职责边界、风险台账和长期整改节奏。
- users: 工作空间维护者、AI助手、未来的自己
- non_goals: 不重排现有 PLC/软件主目录，不把治理项目做成新的开发工具，不在首轮直接迁移大量历史文件
- key_principle: 先建立单一真源，再做渐进收编；先做映射和边界，后做清理和自动化

## 2. Current Focus（当前焦点）
- current_focus: NG-WP-01 至 NG-WP-08 已依次完成候选提交；NG-WP-08 已实现默认无 hard-delete、可恢复且 fail-closed 的 archive/restore 核心。连续执行授权至少覆盖至 NG-WP-10；稳定部署仍未切换，工程发布门禁保持 NO-GO。
- milestone: 单向发布目标架构 ✅；WBS-2 Bootstrap R0 ✅；WBS-1 事实包 ✅；WBS-1D disposition ✅；supersession、R1/R2/R3、双槽部署、切流和回退 ⛔ 未授权
- code_baseline: 当前物理 import 仍来自 `00_Infrastructure/auto_pm`，但已批准的目标基线将 SW-2026-008 定义为唯一研发母体，基础设施位仅作稳定部署容器
- acceptance: 路径修正 ✅ + 工具链口径统一 ✅ + 风险台账对齐 ✅ + PM_SESSION精简 ✅ + 基础设施双轨运行 ✅ + 活文档/历史档案分层 ✅ + WBS 0 基线清洁与可回退 ✅ + WBS 1 真源与版本指纹锁定 ✅ + RC1 收口证据 ✅ + 双技术栈实战 ✅ + 决策包契约与跨领域穿透门禁 ✅ + Scope Gating 与真实证据硬门禁 ✅

## 3. Status Summary（当前状态摘要）
- in_progress: 主工作区仍冻结 26 个既有 staged 候选与原始 SW PM_SESSION 未暂存差异；候选链已推进至 `036685c`，未合并、未部署。
- next_up: 依 User 连续执行授权，为 NG-WP-09 建立独立精确 CHG/DEC，将 archive/restore/list CLI 接入同一安全服务并移除门禁绕过；不得提供 hard-delete。
- 2026-09-05 NG-WP-08：依据 `CHG-SCPT-2026-008` / `DEC-20260905-ACE2F65D`，候选实现工作区全局锁、锁后事实重读、NG-WP-04 事务、严格反向补偿、精确 archive_code/原 phase 恢复及显式 scanner 根。140 项回归通过、2 项因 Windows symlink 权限环境性跳过，Ruff、Mypy、provenance 和 diff/hash 全绿，候选提交 `036685c`。
- 2026-09-05 NG-WP-07：依据 `CHG-SCPT-2026-007` / `DEC-20260905-A7DE4108`，候选新增只含 archive/restore 的类型化领域契约，覆盖不可变授权、canonical 路径、状态机、故障/测试矩阵、并发/幂等和反向补偿。37 项专项 pytest、Ruff、Mypy、provenance 和 diff/hash 门禁全绿，候选提交 `ca09431`。
- 2026-09-05 NG-WP-06：依据 `CHG-SCPT-2026-006` / `DEC-20260905-5AF88A4F`，候选编排器实施 canonical 白名单、verify-only 零写、拒绝任意 callback/auto_commit、禁止 partial verification，并对未实现 resume 明确 fail-closed。22 项专项 pytest、Ruff、Mypy、`python -S` provenance 和 diff/hash 门禁全绿，候选提交 `31da305`。
- 2026-09-05 NG-WP-04：依据 `CHG-SCPT-2026-004` / `DEC-20260905-F41AC539`，候选 transaction 拒绝工作区外、`..` 与 reparse 越界；回滚/清理失败保留 backup 并进入 FAILED。19 项专项 pytest、Ruff、Mypy、`python -S` provenance 和 diff check 全绿，候选提交 `5b4b56f`。
- 2026-09-05 NG-WP-05：依据 `CHG-SCPT-2026-005` / `DEC-20260905-7D85019F`，候选决策服务对 disposition、目标 SHA-256、状态冲突和损坏 JSON fail-closed；16 项专项 pytest、Ruff、Mypy、`python -S` provenance 和 diff check 全绿，候选提交 `67697c1`。
- 2026-09-05 NG-WP-02：受控离线轮子闭包已安装到唯一 `.venv`，生成 94 项候选 `requirements.lock` 并完成 `pip check`、离线 dry-run、`python -S` candidate provenance；候选配置提交 `6241f934`。全量候选 Ruff 35 项与 Mypy 50 项为既有存量质量债，未在环境工作包修改。
- 2026-09-05 NG-WP-03：依据 `CHG-SCPT-2026-003` / `DEC-20260905-74C2F7A1`，隔离 candidate 回收 `workflow_dtos.py` 与 17 项契约测试；`python -S` provenance、pytest、Ruff、Mypy 与 staged diff 检查全绿，候选提交 `f0899ab`。稳定部署、入口、运行态和主 index 未触及。
- open_questions:
  - 项目简称保持 `WorkspaceGovernance`（已确认）
  - `handoff` 已完成 v1 CLI、基础原子消费和只读队列快照；PM_SESSION、变更单和反馈仍由 PM 单一 owner 收口
  - 双轨期需防止旧 `SW-2026-008` 母体代码与基础设施位代码长期分叉
  - 活跃规划/交付文档暂留旧母体，后续迁移前需先确定唯一真源，避免文档双份维护
  - `CHG-SCPT-2026-161` 至 `164` 保留历史结构告警，后续单独治理，不在本批改写审计证据
  - 驾驶舱迭代自身存在循环自证风险，必须采用稳定控制面复核候选开发面的双钥匙门禁
  - `DISP-20260904-3362BFFF-01` 已将 `DEC-20260904-3362BFFF` 标记为 `BLOCKED_SEMANTIC_CONFLICT`，仅限制未来消费且不改写旧证据
  - 当前 `.venv` 仍通过 editable `.pth` 挂接基础设施位，与已批准的目标架构不符；本轮未授权修改
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
- plc_domain_acceptance: 01_项目文档/09_SW-2026-008_WBS7_DJ-2026-005_PLC域验收矩阵_REP.md
- handoff_queue_acceptance: 01_项目文档/10_SW-2026-008_WBS8_handoff工作队列验收矩阵_REP.md
- migration_closure: 01_项目文档/11_SW-2026-008_迁移收口与退路决策_REP.md
- cockpit_enforced_closure_handoff: 01_项目文档/12_SW-2026-008_PM驾驶舱强制闭环_对话交接_PM.md
- sw008_architecture_pack: ../01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/02_规划/`005_ADR`、`006_MATRIX`、`007_TEC`、`GO_NOGO_CHECK_REPORT.md`

## 5. Logs（按事件沉淀）
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
- 2026-09-05 | skill=fullstack-engineer + pm-workflow | mode=NG-WP-12 | result=稳定容器骨架落地：launcher（解析校验、fail-closed，不执行 release）、releases/ 空槽、双指针 null 未初始化、空 manifest、`.lock` 运行期互斥语义；母体 `DeploymentContainer`（release-id 校验/releases containment/指针原子写/manifest SHA-256 核验/独占锁）提交 `92e2c94`；全量 1936 passed/17 skip、Ruff/Mypy/provenance/doc 全 Exit 0；隔离矩阵 8 用例通过且真实容器只读；遗留钩子模板缺陷已在稳定侧 `git_hook.py` 修复（再生成与本地修复版逐字节一致），candidate 提交验证钩子真实生效；未切入口、未部署 active、主工作区未提交 | evidence=`CHG-SCPT-2026-014`、`DEC-20260905-3DB6BE6C`、`NG-WP-12_isolation_evidence_2026-09-05.md`
- 2026-09-05 | skill=fullstack-engineer + pm-workflow | mode=NG-WP-11 | result=主工作区一次收口提交 `efee250`；candidate 冻结提交 `87183fb29d5d99730c90fe25db2ca6a020098ab3`（262 文件）；从冻结 commit `git archive` 导出 886 文件构建 `auto_pm-1.2.3-py3-none-any.whl`（SHA-256 `ca47b787f8cb55ef2ec48ac01e2747e65f138e848fc3a96b326077a5c823bde7`）；逐文件 SHA-256 manifest、requirements.lock 副本、构建环境元数据落盘 `.auto-pm/artifacts/sw-2026-008/NG-WP-11/`；空隔离目录安装 + `python -S` provenance 探针通过且无稳定部署泄漏；制品可仅由 source commit 重建 | evidence=`CHG-SCPT-2026-013`、`DEC-20260905-89511831`、`build_metadata.json`、`install_verification.json`
- 2026-09-05 | skill=fullstack-engineer + pm-workflow | mode=NG-WP-10 | result=Gate 1 整改复跑全绿：import provenance、pytest 全量 1900 passed/16 skipped、Ruff check/format、Mypy strict、doc check、spec check（project scope + 主工作区只读 registry）、死链/dynamic smoke、CLI 注册、git diff --check 共 10 项 Exit 0；candidate 262 处变更逐一比对全部位于 `auto_pm/**`、`tests/**`、`.gitignore`、单一用户指南白名单内；首轮 NO-GO 的 17 failed/54 errors、153 ruff、226 格式、51 mypy、SHC-000 全部消除 | evidence=`CHG-SCPT-2026-012`、`DEC-20260905-B95B7ABB`、`CHG-DOCU-2026-005`、`DEC-20260905-EA9B1159`、`NG-WP-10_Gate1_remedy_report_2026-09-05.md`
- 2026-09-05 | skill=fullstack-engineer + pm-workflow | mode=NG-WP-09 | result=安全 archive/restore/archive-list CLI、真实 DEC/CHG 策略适配器及两项精确依赖恢复完成；119 passed、2 Windows 权限 skip、0 failed；候选提交 `8bbda79`，无硬删除/force，未触及稳定部署、真实项目或主 index | evidence=`CHG-SCPT-2026-009/010/011`、`DEC-20260905-A094BAEF/5A97778D/21FDB937`
- 2026-09-05 | skill=fullstack-engineer + pm-workflow | mode=NG-WP-08 | result=可恢复 archive/restore 核心、全局锁、锁后复核与严格补偿落地；140 passed、2 Windows 权限 skip、0 failed；候选提交 `036685c`，无真实项目操作 | evidence=`CHG-SCPT-2026-008`、`DEC-20260905-ACE2F65D`
- 2026-09-05 | skill=fullstack-engineer + pm-workflow | mode=NG-WP-07 | result=候选归档领域契约只暴露 archive/restore，默认无 hard-delete；37 项专项测试和静态门禁全绿；候选提交 `ca09431`，未移动真实项目、未合并或部署 | evidence=`CHG-SCPT-2026-007`、`DEC-20260905-A7DE4108`
- 2026-09-05 | skill=fullstack-engineer + pm-workflow | mode=NG-WP-06 | result=候选编排器完成 canonical 白名单、verify-only 零写、拒绝隐式 Git/任意 callback、禁止 partial verification；22 项专项测试和静态门禁全绿；候选提交 `31da305`，未合并或部署 | evidence=`CHG-SCPT-2026-006`、`DEC-20260905-5AF88A4F`
- 2026-09-05 | skill=fullstack-engineer + pm-workflow | mode=NG-WP-05 | result=候选决策契约强制消费 blocked/superseded disposition，验证 SHA-256、白名单与审批元数据；16 项专项测试和静态门禁全绿；候选提交 `67697c1`，未合并或部署 | evidence=`CHG-SCPT-2026-005`、`DEC-20260905-7D85019F`
- 2026-09-05 | skill=fullstack-engineer + pm-workflow | mode=NG-WP-04 | result=候选 transaction 建立 canonical containment 与 fail-closed 故障恢复；19 项专项测试、Ruff、Mypy、`python -S` provenance 全绿；候选提交 `5b4b56f`，未合并或部署 | evidence=`CHG-SCPT-2026-004`、`DEC-20260905-F41AC539`
- 2026-09-05 | skill=pm-workflow | mode=NG-WP-03 | result=以稳定部署冻结源 SHA-256 为依据，在 detached candidate 仅新增 workflow DTO 与对应测试；17 项 pytest、Ruff、Mypy 和 `python -S` provenance 全绿；候选提交 `f0899ab`，未合并或部署 | evidence=`CHG-SCPT-2026-003`、`DEC-20260905-74C2F7A1`
- 2026-09-05 | skill=pm-workflow | mode=NG-WP-01/NG-WP-02 | result=`CHG-DOCU-2026-003` 与 `DEC-20260905-A646F158` 建立旧方案 `HISTORICAL_SUPERSEDED` 治理索引；固定 `313d60f` detached candidate 成功且源码 provenance 指向母体；candidate 无项目内解释器/依赖锁，现有 `.venv` 的 `_editable_impl_auto_pm.pth` 指向稳定部署，故 NG-WP-02 标记 `BLOCKED_PORTABLE_INTERPRETER`；未修改源码、入口、稳定部署、运行状态或 Git index | evidence=`NG-WP-00_RECOVERY_SUMMARY.md`、`NG-WP-02_ISOLATION_EVIDENCE.md`
- 2026-09-04 | skill=fullstack-engineer + pm-workflow | mode=WBS-1/WBS-1D | result=941 条文件级事实独立复核；`DISP-20260904-3362BFFF-01` 以目标哈希和 8 项 basis evidence 前向阻断冲突 DEC；两份 handoff 均正式 consumed；`CHG-DOCU-2026-001/002` closed；未修改源码或入口 | evidence=`DEC-20260904-94CCE59D`、`DEC-20260904-C1F94B77`、disposition SHA-256 `c380c4c7ee18e2e0ff4125e4ce5b270310a8c5235fa6b78fbf0a19aff96f6091`
- 2026-09-04 | skill=pm-workflow | mode=SW-2026-008 单向发布架构规划 | result=User 批准目标架构与四份规划产物；工程 NO-GO，不授权 WBS-3、文件/入口操作、提交或发布 | evidence=`RESUME-8A40C46458D08312`、`FACT-CA141A67B032FDFA`、`GO-NOGO-SW008-20260904-001`
- 2026-09-04 | skill=pm-workflow | mode=W2 PM closure
  - request_id: `AI-20260904-025057-B2D157BC`
  - result: fullstack execution 已通过 preflight 并消费为 `consumed`；CHG-SCPT-2026-172 已闭环流转至 closed；PmClosureSagaCoordinator 落地，8 步顺序事务日志、失败注入与 checkpoint 恢复验证全绿。
  - evidence: `DEC-20260904-AE50166C`、`AI-20260904-025057-B2D157BC.result.json`
- 2026-09-04 | skill=pm-workflow | mode=W1-2 PM closure
  - request_id: `AI-20260904-015823-38A19B9C`
  - result: fullstack execution 已通过 preflight 并消费为 `consumed`；CHG-SCPT-2026-171 已闭环流转至 closed；Scope Gating 与跨资产真实性门禁落地，全量回归全绿。
  - evidence: `DEC-20260904-77ED7B63`、`AI-20260904-015823-38A19B9C.result.json`
- 2026-09-03 | skill=pm-workflow | mode=RC1-11 PM closure
  - request_ids: `AI-20260903-C1R-C1S-EXEC`、`AI-20260903-C2A-EXEC`、`AI-20260902-WBSC1-EXEC`、`AI-20260902-WBSC1-BASELINE-EXEC`
  - result: 四份 completed execution result 已通过 preflight 并消费为 `consumed`；CHG、PM_SESSION、feedback 与 ledger 进入同批收口。
  - evidence: `RESUME-108D88689450E861`、四份 handoff closure fingerprint、`14_SW-2026-008_RC1-0至RC1-4_跨Agent执行Checkpoint.md`
- 2026-09-02 | skill=pm-workflow | mode=强制闭环增强阶段 0
  - request_id: `AI-20260902-140735-8DB7AB48`
  - result: Fullstack Grooming 已由 PM 消费；形成 WBS-C1 至 C7 差距和阶段 1 决策包，本轮未修改驾驶舱源码
  - artifact: `01_项目文档/12_SW-2026-008_PM驾驶舱强制闭环_对话交接_PM.md`

## 8. Handoff Notes
- 2026-09-05 | from=fullstack-engineer | mode=NG-WP-12 | status=`completed / skeleton-only` | decision=`DEC-20260905-3DB6BE6C` | gate=NG-WP-13（根入口与环境解耦）需独立 CHG/DEC；git_hook.py 母体回收待后续回收包；治理落账提交待用户授权
- 2026-09-05 | from=fullstack-engineer | mode=NG-WP-11 | status=`completed / candidate-frozen + artifact built` | decision=`DEC-20260905-89511831` | gate=NG-WP-12（稳定部署双槽骨架）需独立 CHG/DEC 且不继承本批准；本包 PM 落账后的台账/PM_SESSION 提交需下一次提交授权（本次授权仅一次提交）
- 2026-09-05 | from=fullstack-engineer | mode=NG-WP-10 | status=`completed / gates green` | decision=`DEC-20260905-B95B7ABB`+`DEC-20260905-EA9B1159` | gate=独立 AI 复核仍待安排；candidate 冻结提交属 NG-WP-11，需 User 单独批准（本条落账时 User 已口头批准 NG-WP-11，见 CHG-SCPT-2026-013）
- 2026-09-05 | from=fullstack-engineer | mode=NG-WP-04 | status=`completed / candidate-only` | decision=`DEC-20260905-F41AC539` | gate=NG-WP-05 必须创建独立精确 CHG/DEC；稳定部署继续只读
- 2026-09-05 | from=pm-workflow | mode=NG-WP-02/NG-WP-03 | status=`completed / candidate-only` | decision=`DEC-20260905-32CE308F` 完成受控依赖闭包，`DEC-20260905-74C2F7A1` 完成 workflow DTO 契约回收 | gate=NG-WP-04 必须获得独立 CHG、DEC 和 User 明示批准；稳定部署继续只读
- 2026-09-05 | from=pm-workflow | mode=NG-WP-01/NG-WP-02 | status=`implementing / BLOCKED_PORTABLE_INTERPRETER` | decision=旧方案仅作历史证据；candidate 只能在新环境门禁解除后用于 NG-WP-03 前的验证 | gate=新 CHG/DEC、锁定依赖、candidate-local interpreter、stable editable `.pth` 处置与隔离复核
- 2026-09-04 | from=fullstack-engineer | mode=WBS-1/WBS-1D | request_ids=`AI-20260904-WBS1-FACT`,`AI-20260904-WBS1D-DISP` | status=`consumed` | gate=冲突 DEC 已阻断未来消费；supersession 与 R1/R2/R3 仍未授权
- 2026-09-04 | from=pm-workflow | mode=SW-2026-008 architecture baseline | status=planning approved / engineering frozen | decision=SW 母体、infra stable、`.auto-pm` 状态、Obsidian 规范 | gate=WBS-3 后续须 User 再批准
- 2026-09-04 | from=pm-workflow | mode=W2 closure
  - request_id: `AI-20260904-025057-B2D157BC`
  - status: `consumed`
  - decision: W2 C6 可恢复 PM Saga 事务日志完成消费并落账闭环。
- 2026-09-04 | from=pm-workflow | mode=W1-2 closure
  - request_id: `AI-20260904-015823-38A19B9C`
  - status: `consumed`
  - decision: W1-2 证据门禁扩展（Scope Gating、变更单存在性、交付物真实性）完成消费并落账闭环。
- 2026-09-03 | from=pm-workflow | mode=RC1-11/RC1-12 closure
  - request_ids: `AI-20260903-C1R-C1S-EXEC`、`AI-20260903-C2A-EXEC`、`AI-20260902-WBSC1-EXEC`、`AI-20260902-WBSC1-BASELINE-EXEC`
  - status: `consumed` (all four)
  - decision: RC1 仅关闭 C1 与 C2a 已批准交付；C3 至 C7 仍不得因本次收口自动启动。
  - gate: 全量 pytest、Ruff、Mypy、`git diff --check` 与 ledger reconcile 必须全部通过，随后仅等待用户验收和提交决策。
- archive: 2026-09-01 历史交接记录已完整保存至 `05_收尾/PM_SESSION归档/Handoff_Notes_SYS-2026-001_20260901.md`
- current_state: 当前工作空间级控制面为 `00_Infrastructure/auto_pm`，旧 SW 母体保留产品文档、变更历史和回退参考。
- historical_focus_superseded: 旧口径曾记录“基础设施位作为代码真源且 Dogfooding WBS 0-9 完成”；该口径已被 2026-09-04 的单向发布架构决策取代，仅保留为历史证据。
- handoff_gap: handoff.v1 已具备预检、原子消费、失败证据、重试和只读队列快照；PM_SESSION、CHG、台账和反馈的业务落账仍保持 PM 单一 owner。
- gate: 候选版本必须通过自身测试和稳定版外部复核，PM_SESSION、CHG、台账和反馈完成对账后才可收口。
- watchouts: PLC 技能只做域验收；不得将 `DJ-2026-005` 未全绿研发现场混入驾驶舱治理提交。
- 代码基线 V1.2.3
- status: [已验证] WBS 0/1/2/3/4/5/6/7/8/9 完成；代码单轨成立；旧母体回退保留；工作树在每个提交门前保持可解释

## 9. Next Actions
- [完成] NG-WP-02 候选环境闭包 | result=受控离线轮子、94 项 lock、`pip check`、离线 dry-run 与 `python -S` 候选 provenance 已复核；候选提交 `6241f934`
- [完成] NG-WP-03 workflow DTO 契约层 | result=冻结源哈希一致、17 项契约测试及专项 Ruff/Mypy 全绿；候选提交 `f0899ab`；未合并、未部署
- [完成] NG-WP-04 事务边界和失败恢复 | result=fail-closed containment 与故障恢复通过 19 项专项测试；候选提交 `5b4b56f`；未合并、未部署
- [完成] NG-WP-05 至 NG-WP-09 | result=决策强化、编排器加固、归档契约/核心/CLI 逐包收口（明细见 §6 日志）
- [完成] NG-WP-10 母体全量 Gate 1 | result=整改复跑 10 项门禁 Exit 0；candidate 提交仍为 `8bbda79`+工作树修改，冻结提交移交 NG-WP-11
- [进行中] NG-WP-11 冻结候选提交与制品构建 | approval=User 2026-09-05 “批准，可以git提交一次，然后进行NG-WP-11”；授权注册见 `CHG-SCPT-2026-013`/对应 DEC | gate=候选提交仅含逐包已验收 pathspec；制品、manifest、依赖锁与空目录安装验证证据完整
- [未授权] NG-WP-12 至 NG-WP-17 | gate=每批必须新的 CHG、DEC 和 User 明示批准；不得部署、切流、回退或物理归档
- [已完成] 批准 SW-2026-008 研发母体 + 稳定部署单向发布架构 | result=ADR、差异回收方案、WBS 与验收标准已编制；不代表实施授权
- [已完成] WBS-1/WBS-1D 全量差异事实包与不可变 disposition | result=941 条矩阵、目标 DEC 哈希及 8 项证据完成独立复核；冲突 DEC 不再可作为未来动作授权；supersession 延后
- [待报批] R1：CHG-174 最小母体回收批次 | precondition=User 明文批准 `change_transaction.py` 与对应测试的精确母体 pathspec | done_when=独立 CHG/DEC、源哈希、母体门禁与阶段提交证据成立
- [未授权] WBS-3 至 WBS-8 | gate=不得移动、覆盖、删除、修复、提交、Tag、部署、切流或回退
- [已完成] SW-2026-008 W2 C6 可恢复 PM Saga 事务日志 | result=AI-20260904-025057-B2D157BC 已消费；CHG-SCPT-2026-172 已 closed；Saga 事务日志与补偿全绿
- [已完成] SW-2026-008 W1-2 证据门禁扩展：跨资产与决策包预检 | result=AI-20260904-015823-38A19B9C 已消费；CHG-SCPT-2026-171 已 closed；Scope Gating 与真实证据门禁全绿
- [已完成] SW-2026-008 RC1（C1 与 C2a 已批准范围） | result=四份 execution handoff 已消费；PM 收口与独立门禁验收已完成；不代表 C3 至 C7 完成
- [后续] SW-2026-008 强制闭环增强 WBS-C3 至 C7 | precondition=新的阶段 0 与阶段 1 用户批准 | done_when=决策包、Quick/Full、领域证据、PM Saga 和完整 Dogfood 逐批闭环
- [已验证] SW-2026-008 文档资产第一轮治理 | precondition=旧母体文档资产完成分类 | done_when=完成验证、台账对账和治理提交；变更管理资产保持 archive-only
- [后续] SW-2026-008 活跃文档迁移评估 | precondition=本批验证通过且唯一真源/同步策略明确 | done_when=决定是否迁移活跃规划/交付文档，不自动迁移历史变更档案
- [完成] SW-2026-008 驾驶舱 Dogfooding WBS 0 | result=规划前变更已分组裁决；未验证漂移恢复；未验证 PLC 现场文件可逆停放；备份与证据已保留；工作树干净
- [完成] SW-2026-008 驾驶舱 Dogfooding WBS 1 | result=形成 infra/SW/SYS 唯一真源矩阵、入口版本指纹和双轨退出条件；旧母体代码冻结
- [完成] SW-2026-008 驾驶舱 Dogfooding WBS 2 | result=实现 handoff.v1 create/list/show/close、request_id 幂等定位、证据和 CHG 前置校验；技能命令已对齐；运行态已忽略
- [完成] SW-2026-008 驾驶舱 Dogfooding WBS 3 | result=预检、文件锁、原子替换、幂等指纹、失败事件和 retry_close 已完成；故障注入后 pending 可恢复，重复关闭无重复状态
- [完成] SW-2026-008 驾驶舱 Dogfooding WBS 4 | result=prepare/inspect/review 隔离 runner 已完成；候选只能位于 `.auto-pm/worktrees/`；稳定脏树拒绝创建候选；外部复核报告可留存
- [完成] SW-2026-008 驾驶舱 Dogfooding WBS 5 | result=实际创建 `AI-20260901-WBS5` 只读请求；preflight 与 PM close 均成功；changed_files 为空；未产生产品变更
- [完成] SW-2026-008 驾驶舱 Dogfooding WBS 6 | result=doctor 版本来自当前基础设施包 `__version__`，实机显示 1.2.3；回归测试与 ruff 通过
- [完成] SW-2026-008 驾驶舱 Dogfooding WBS 7 | result=DJ-2026-005 PLC 结构 51/0/0；实质文档 14/2/0；变量表 119 点；HTML 原型函数完整性通过；CHG-HMI-2026-001 已关闭；矩阵已落账
- [完成] SW-2026-008 驾驶舱 Dogfooding WBS 8 | result=只读 handoff 工作队列快照已合并；候选测试 5 passed；Ruff/Mypy/隔离复核/变更台账对账通过；CHG-SCPT-2026-169 已关闭；矩阵已落账
- [完成] SW-2026-008 驾驶舱 Dogfooding WBS 9 | result=根入口和安装入口优先基础设施位；两批稳定版本门禁通过；旧母体代码冻结并保留回退；迁移收口报告已落账；本轮未删除旧母体

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

