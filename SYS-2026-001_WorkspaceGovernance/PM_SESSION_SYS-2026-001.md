# PM_SESSION_SYS-2026-001

## 0. Meta
- project_id: SYS-2026-001
- project_name: WorkspaceGovernance
- project_root: c:\Users\fubai\Documents\My_Workspace\SYS-2026-001_WorkspaceGovernance
- last_updated: 2026-09-06
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

- 2026-09-06 [已验收] NG-WP-16：User 已验收 `CHG-DOCU-2026-004` / `DEC-20260906-6D16E016` 的临时容器回退与观察证据；7 个场景、5/5 短观察和 `ledger reconcile SW-2026-008` Exit 0 已闭环。证据=`.auto-pm/reports/NG-WP-16_rollback_observation_2026-09-06.md`；本次未批准生产长时 soak、真实 active/previous 指针切换或最终 GO。
- 2026-09-06 [已执行] NG-WP-15 真实切流：CHG-SCPT-2026-184 / DEC-20260906-3FC9EC2D 已将 active 原子切至 1.2.3-f950525，previous=null；tag sw-2026-008-1.2.3-f950525 指向 f950525；verify_release 465/465、root resolve-only 与 --help Exit 0。报告=.auto-pm/reports/NG-WP-15_switchover_f950525_2026-09-06.md；handoff AI-20260906-NGWP15-SWITCHOVER-F950525 已 completed/consumed；CHG 当前 pending_acceptance，生产长时 soak 未运行。
- 2026-09-06 [已执行] NG-WP-17 历史规划归档：CHG-DOCU-2026-005 / DEC-20260906-C1CFB37C 已可逆归档 4 个历史规划文件，4/4 SHA-256 与字节数匹配，git diff --check Exit 0；报告=.auto-pm/reports/NG-WP-17_archive_2026-09-06.md；handoff AI-20260906-NGWP17-HISTORICAL-ARCHIVE 已 consumed。研发母体源码、stable flat auto_pm、templates、release 均未移动；setup_env.bat 依赖使 stable flat 源归档延期；CHG 保持 pending_acceptance。
- 2026-09-06 [已执行] NG-WP-17 入口脱钩：CHG-SCPT-2026-185 / DEC-20260906-510CE559 已使 setup_env.bat 不再 editable 安装 stable flat source；verify_release 465/465、resolve-only/--help Exit 0。完整 startup guard 为 13 passed、1 项 Windows cmd.exe timeout（Exit 1），stable flat archive 继续延期；handoff AI-20260906-NGWP17-ENTRY-DECOUPLING 已 consumed。拓扑报告=.auto-pm/reports/SW-2026-008_workflow_topology_2026-09-06.md。
- 2026-09-06 [已执行] NG-WP-18 CHG-SPEC-2026-001 Obsidian 规范库 P0 治理修补：依据 DEC-20260906-1AB177AF（39 文件 pathspec/9 条件），实改 29 文件（frontmatter A 型统一×8、registry 同步 6 处、905 纯调序、CHK/OPS/045/042/041 死链修复、INDEX 四域真链接化、活跃区死链清扫），10 文件 verified-no-op。六门禁全绿：spec check Exit 0、活跃区死链=0（冷区 28 登记）、INDEX 覆盖率 67/67=100%、doc check Exit 0、CHK A 类全过、scoped diff --check 全过。CHG 转 pending_acceptance；冷区引用 7 项与驾驶舱拆单 6 项已登记移交。报告=.auto-pm/reports/CHG-SPEC-2026-001_执行报告_2026-09-06.md。
- 2026-09-06 [已复核] CHG-SPEC-2026-001 PM 验收复核：六门禁独立复跑全绿、33 改动文件 ⊆ 39 白名单∪落账件（越界 0）、905 行多重集相等复算成立、事故 README 字节还原属实；SHA 证据链冻结后 2 文件漂移已补记入 CHG §9（PM_SESSION_SYS=PM 收口写入；00_INDEX=补全注记追加，门禁复验绿）。架构师裁决落地：D-1 结案 TOOL-906 保留 number=9060（spec check 9060 豁免列入 SW 拆单）；"台帐"认定错别字——SYS 台账改名 `01_版本变更台账.md`（031 行字段补全）+ 驾驶舱 dev 源码 8 文件清零（路径常量 7 处，py_compile 绿，dev reconcile SYS Exit 0），release f950525 冻结未动。双索引疑云澄清：第二份索引与图谱散装节点均为 Archive_Cold 冷区 v2 幽灵（Obsidian 图谱默认绘制冷区），活跃区索引唯一。
- 2026-09-06 [已结项] CHG-SPEC-2026-001：架构师批准结项。CHG §3.4 置 closed 终态、台账 031 行 ✅已关闭（完成日期 2026-09-06）；handoff AI-20260906-P0-SPEC-001-R3 已由 PM close 为 consumed（Exit 0）；证据归档 `.auto-pm/reports/CHG-SPEC-2026-001_P0_evidence/`，99_P0工作区 已按 DEV-TMP-001 清理（回滚移交 git HEAD）；ledger reconcile SYS（dev 源码）结项复验 Exit 0。遗留移交：驾驶舱拆单 8 项（SW-2026-008）+ 冷区引用处置 7 项（待独立批准）。
- 2026-09-06 [已立项] CHG-SPEC-2026-002/003/004 三单同批立项（架构师指示"p0遗留项，p1，P2做变更单，可以划分多个变更单；p4暂停"）：002=P0 遗留收尾（F19 语义互链/编号宪章/043+040 SPEC 分类）；003=P1 PLC 吸收增强（F07/F08/F15 + B3–B8，新增 SW 拆单 #9=auto_pm io_points 解析器扩列）；004=P2 PM 域模板包（903 立项表补立/URT/TDR/F21 评估）。三单均 V1.0.0 草案、状态 draft、台账 032–034 行 🔄待处理，等待架构师批准；执行顺序 002→003→004（002 的编号宪章是 004 新模板编号的输入）。**P4（STD-817）架构师指示暂停**，恢复另批；P3（816 测试与上机）未提及，维持未立项。
- 2026-09-06 [已执行] CHG-SPEC-2026-002 P0 遗留收尾（架构师对话指令批准）：003 新增 §13 编号段位宪章（V1.2.0，7 段位表+跨段占用登记不迁移）；040/043 增 SPEC 法典类分类（V2.3.0，8 领域补齐）；00_INDEX 挂载 6 组语义互链（12 链接全解析）并修复 OPS/CHK 版本单元格漂移（V1.0.0→V1.1.0，P0.3 残留）；registry 三条同步。六门禁全绿：spec check 0 错误、活跃区死链 0、覆盖率 67/67、doc check 100%、reconcile 无差异、scoped diff 5/5。CHG 转 pending_acceptance；证据=.auto-pm/reports/CHG-SPEC-2026-002_evidence/。
- 2026-09-06 [已执行] CHG-SPEC-2026-003 P1 PLC 吸收增强（架构师对话指令"继续"批准）：023 V2.2.0（I/O 表 9 列三安全列、§5.4.3 OB 调度表、状态机表超时→报警号、§8.1 四位报警分段+禁字母前缀、§8.2 B6 三列、§10.1 八列安全矩阵、DJ-005 基因通用化+§14.4 存档）；815 V1.2.0（§4.1 io_points.csv 12 列唯一 schema、§4.2 接口登记册+超时两段式）；909 V1.1.0（F07：交握真源=820，四步降为呈现层视图）；906 V2.1.0（去基因）。六门禁全绿（死链活跃 0/覆盖率 67-67/scoped diff 6-6）。F07/F08/F15 闭环；SW 拆单 #9 在途。证据=.auto-pm/reports/CHG-SPEC-2026-003_evidence/。
- 2026-09-06 [已结项] CHG-SPEC-2026-002/003 双单验收关闭（架构师对话指令"验收+提交+开工 004 一起来"）：002=P0 遗留三项闭环（编号宪章随即作为 004 新模板编号分配依据生效）；003=F07/F08/F15 闭环（交握真源=820、四位报警分段、io_points 三安全列 schema 生效）。台账 032/033 ✅已关闭；CHG 均置 closed 终态。004（P2）获批开工。
- 2026-09-06 [已执行] CHG-SPEC-2026-004 P2 PM 域模板包（架构师对话指令批准）：新增 3 部规范 PM-053 立项表（五块信息模型+A0 并入，收编 903 幽灵引用）/URT-054（九列单表贯通+追溯六态）/TDR-055（A3 简化十列）；DJ-005 立项表 903 引用改写收编（归档侧 1 处登记不改）；F21 评估报告落 reports（保留 9/合并候选 2/归冷候选 3，未动存量）。registry 67→70，INDEX 覆盖 70/70。六门禁全绿（首扫抓到 053 一条 stale-path 当场修复归零）。CHG 转 pending_acceptance；证据=.auto-pm/reports/CHG-SPEC-2026-004_evidence/。
- 2026-09-06 [已结项] CHG-SPEC-2026-004 验收关闭（架构师对话指令"继续下一个"）：3 部新规范 PM-053/URT-054/TDR-055 生效（法典 70 条），903 幽灵收编，F21 评估报告在档（保留 9/合并候选 2/归冷候选 3）。台账 034 ✅已关闭；CHG 置 closed。90_方案 P0/P1/P2 三包全部交付闭环。
- 2026-09-06 [已执行] CHG-SPEC-2026-005 F21 处置（架构师队列指令"按照顺序全部做"批准，含冷区迁移独立批准）：006/007/051/044/029 五文件 git mv 迁入 Archive_Cold（保留相对结构）；DEV-004 V1.2.0 吸收记录（044 严格子集并入、029 走 CHG-040）；registry 移除五条 70→65；INDEX 归档节建立五条冷链接+统计同步（活跃 38/合计 65/已归档 5）。六门禁全绿（死链活跃 0/覆盖率 65-65/scoped diff 全 PASS；执行中自查修复两处：INDEX 误删五行当场恢复、DEV-004 registry 版本漂移补同步）。CHG 转 pending_acceptance；证据=.auto-pm/reports/CHG-SPEC-2026-005_evidence/。
- 2026-09-06 [已执行并结项] CHG-SPEC-2026-006 冷区引用处置（架构师队列指令批准）：普查修正预期——真实活体死链仅 3 处 5 行（FB_1013 IFC/DSN 801 引用、0100 README 903 旧路径），行级修复完成；#6 迁籍改判（DJ-2026-005 自有 11 份 CHG-PLC 活体系列，冷区件为游离副本维持登记）；#5/#7 维持 SW 拆单 #5 与 .trae 配合项。冷区登记表追加 §5 结算，冷区治理法典侧收口。法典门禁回归全绿。台账 036 已关闭。
- 2026-09-06 [已执行并结项] CHG-SPEC-2026-007 P3 测试与上机包（架构师队列指令批准，P3 转立项执行）：新增 STD-816《PLC测试与上机复核模板》V1.0.0（六节：scltest 登记/三强制约定[RESET 防污染/WAIT_CYCLES/断言语义]/fail_safe 打点闭环/两区制上机复核/安全功能验证×3/竣工四节清单；031 绑定不重复定义）。registry 65→66、INDEX PLC 域 15 部。六门禁全绿。台账 037 已关闭。
- 2026-09-06 [已执行并结项] CHG-SPEC-2026-008 P4 恢复执行（架构师队列指令批准，暂停解除）：新增 STD-817《移植一致性核查规范》V1.0.0（五维判定口径[模块/IO/步序/报警/互锁，不要求地址等价]、地址→语义映射表强制产出、历史模块标注规则[禁止进入交付主控调用链]、核查报告模板；实战来源 DJ-2026-005 一致性报告 V2.0.0）。registry 66→67、INDEX PLC 域 16 部。六门禁全绿。台账 038 已关闭。90_方案 P0–P4 五包全部交付。

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
- current_state: [已验证] 90_方案 V3.1 P0–P4 五包全部交付闭环（CHG-SPEC-2026-001~008 全部 closed，法典 67 活跃 + 5 归档）；SW 拆单 9 项已整合立单 CHG-SCPT-2026-186（draft 待排期，含 handoff 租约第 10 项候选）；冷区外部线=拆单 #5 与 .trae 配合项。SYS 侧无未竟动作。
- latest_handoff: 2026-09-06 | from=fullstack-engineer | mode=CHG-SPEC-2026-001 P0 execution | request_id=AI-20260906-P0-SPEC-001-R3（R1 租约过期未及时心跳作废；R2 因 change-id 校验不识别 SYS 户籍 CHG-SPEC 目录废弃；R3 为正式回执，待 PM close 为 consumed） | decision=DEC-20260906-1AB177AF | change=CHG-SPEC-2026-001-pending_acceptance | gates: spec_check=Exit 0, deadlinks_active=0, index_coverage=67/67, doc_check=Exit 0, scoped_diff_check=ALL PASS | evidence=.auto-pm/reports/CHG-SPEC-2026-001_执行报告_2026-09-06.md.
- archive: historical §8 handoff evidence (including prior current-state snapshots) preserved in 05_收尾/PM_SESSION归档/PM_SESSION_SYS-2026-001_archive_auto.md; section append=NG-WP-16 history retention archive; SHA-256=e4a1f4fc1b0a7eb923fcf8d8d3d7ac4675483d3a514e5f91cf292e3e04e2e18e.
## 9. Next Actions
- [已结项] CHG-SPEC-2026-002 P0 遗留收尾 | result=5 文件实改（003 §13 编号宪章 V1.2.0、040/043 SPEC 分类 V2.3.0、INDEX 6 组互链+OPS/CHK 版本对齐、registry 同步）、六门禁全绿；gate=2026-09-06 架构师验收关闭（closed）；编号宪章已生效为 004 编号输入
- [已结项] CHG-SPEC-2026-003 P1 PLC 吸收增强 | result=6 文件实改（023 V2.2.0 五处增强+四位分段+基因存档、815 V1.2.0 io_points schema+接口登记册、909 V1.1.0 F07 真源裁决、906 V2.1.0 去基因、INDEX/registry 同步）、六门禁全绿；gate=2026-09-06 架构师验收关闭（closed）；F07/F08/F15 闭环；SW 拆单 #9 在途
- [已结项] CHG-SPEC-2026-004 P2 PM 域模板包 | result=新增 3 部规范（PM-053/URT-054/TDR-055，编号按宪章）+903 幽灵收编+F21 评估报告（保留 9/合并 2/归冷 3，未动存量）、registry 70 条、六门禁全绿；gate=2026-09-06 架构师验收关闭（closed）；F06/F14 闭环
- [暂停] P4 STD-817 移植一致性核查规范 | 架构师 2026-09-06 指示暂停，恢复另批；DJ-2026-005 TIA Portal 编译验证阶段的移植口径暂按项目内一致性报告执行
- [未立项] P3 测试与上机（816 模板） | 未列入本批，维持未立项
- [已结项] CHG-SPEC-2026-001 NG-WP-18 规范库 P0 治理修补 | result=29 文件实改、六门禁经 PM 独立复跑全绿、活跃区死链 0、INDEX 67/67、冷区零接触仅登记；架构师裁决已落地（TOOL-906 保留 9060、SYS 台账改名 + dev 源码 8 文件同步）；gate=2026-09-06 架构师批准结项（closed），handoff R3 consumed，证据归档 CHG-SPEC-2026-001_P0_evidence/；拆单移交 8 项=①change SPEC 域 ②spec index 域覆盖与越权写 ③doc check --strict 语义 ④PATH auto-pm 版本 ⑤冷区汇总报告消费依赖 ⑥手工户籍 CHG 台账回写 ⑦release 重切携带台帐→台账全链改名（SYS 已改、SW/041 模板/.jinja/各项目随重切）⑧spec check 编号唯一性 9060 豁免；另有冷区引用处置 7 项待独立批准。
- [待验收] CHG-SCPT-2026-185 NG-WP-17 入口脱钩 | result=setup_env 不再绑定 stable flat source、verify_release 465/465 与 resolve-only/--help Exit 0；blocker=完整 startup guard 仍有 1 项 Windows cmd.exe timeout（Exit 1）；gate=stable flat archive 延期。
- [待验收] CHG-DOCU-2026-005 NG-WP-17 历史规划归档 | result=4/4 SHA-256 匹配、git diff --check Exit 0、handoff 已 consumed；gate=CHG 保持 pending_acceptance，stable flat auto_pm 因 setup_env.bat 依赖延期，未移动研发母体源码、templates 或 release。
- [待验收] CHG-SCPT-2026-184 真实切流 | result=active=1.2.3-f950525、previous=null、tag 已核验、verify_release 465/465 及 resolve-only/--help Exit 0；handoff 已 consumed；gate=CHG 保持 pending_acceptance，生产长时 soak 未运行。
- [完成] NG-WP-02 候选环境闭包 | result=受控离线轮子、94 项 lock、`pip check`、离线 dry-run 与 `python -S` 候选 provenance 已复核；候选提交 `6241f934`
- [完成] NG-WP-03 workflow DTO 契约层 | result=冻结源哈希一致、17 项契约测试及专项 Ruff/Mypy 全绿；候选提交 `f0899ab`；未合并、未部署
- [完成] NG-WP-04 事务边界和失败恢复 | result=fail-closed containment 与故障恢复通过 19 项专项测试；候选提交 `5b4b56f`；未合并、未部署
- [完成] NG-WP-05 至 NG-WP-09 | result=决策强化、编排器加固、归档契约/核心/CLI 逐包收口（明细见 §6 日志）
- [完成] NG-WP-10 母体全量 Gate 1 | result=整改复跑 10 项门禁 Exit 0；candidate 提交仍为 `8bbda79`+工作树修改，冻结提交移交 NG-WP-11
- [进行中] NG-WP-11 冻结候选提交与制品构建 | approval=User 2026-09-05 “批准，可以git提交一次，然后进行NG-WP-11”；授权注册见 `CHG-SCPT-2026-013`/对应 DEC | gate=候选提交仅含逐包已验收 pathspec；制品、manifest、依赖锁与空目录安装验证证据完整
- [后续] NG-WP-17 stable flat 源归档评估 | precondition=独立 CHG/DEC 先解除 setup_env.bat 依赖；本次仅四个历史规划文件已可逆归档，CHG-DOCU-2026-005 保持 pending_acceptance。
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

