# 技能迭代实施计划 — 基于 auto-pm 项目迭代经验

> **分析文档**: `技能迭代建议清单_auto-pm项目经验.md`（已审核，13 个改进点）
> **本计划**: 决策完整的实施步骤，executor 可直接按此修改技能文件
> **日期**: 2026-07-14

---

## 一、Summary（摘要）

基于 SW-2026-008_auto-pm 项目 56 次 dogfooding 闭环经验，对工作空间技能文件进行 13 项改进：
- **P0（4 项）**: PM_SESSION 双层结构、门禁实测强制检查、台账对账检查点、GUI 测试隔离检查清单
- **P1（8 项）**: §5/§6 职责分离、审查报告验证模式、未验证禁止回写双向检查、retrofit 模式文档化、fixture 健康检查清单、工具引用更新、§8 skill_handoff 严格化、CHG 闭环门禁强化
- **P2（1 项）**: 后台任务监控全局化

**修改文件清单**:
1. `.trae/skills/pm-workflow/SKILL.md`（主要修改，9 处变更）
2. `.trae/skills/fullstack-engineer/SKILL.md`（3 处变更）
3. `.trae/rules/project-rule.md`（2 处变更）
4. `.trae/skills/plc-electrical-engineer/SKILL.md`（1 处小修改，仅工具引用）

---

## 二、Current State Analysis（现状分析）

### pm-workflow/SKILL.md（255 行）
- §4.5 PM_SESSION 间歇精简规则（行 178-192）→ 治标方案，需替换为双层结构
- Step 3.5 Bug 诊断（行 110-131）→ 缺 fixture 健康检查引用
- Step 3.6 dogfooding 闭环质量门禁（行 133-151）→ 12 章节检查为人工，需强化
- Step 3.7 真源一致性前置校验（行 153-172）→ 缺"读取时双向校验"
- Step 4 同步回 PM_SESSION（行 174-176）→ 未适配双层结构
- 行 29-31 工具引用 `specmgr -w` → 需更新为 `auto-pm spec`
- §8 标准化结构（行 233-249）→ skill_handoff 已定义 1 条但执行不严
- 缺：门禁实测检查点、台账对账检查点、retrofit 模式、审查报告验证模式

### fullstack-engineer/SKILL.md（233 行）
- Bug 诊断前置纪律（行 116-131）→ 缺 fixture 健康检查清单
- GUI 测试基础设施规范（行 142-163）→ 缺测试隔离检查清单
- Step 4 回写 PM_SESSION（行 112-113）→ 缺门禁实测前置检查
- 行 55-56 工具参考表仍列 `specmgr` 和 `pm-mgr` → 需更新

### project-rule.md（127 行）
- "迭代文档同步规则"（行 103-113）→ 缺台账对账要求
- "三、编码后验证"（行 81-85）→ 缺后台任务监控要求
- 行 31 仍单独引用 `specmgr -w` → 需更新为 `auto-pm spec`

### plc-electrical-engineer/SKILL.md（135 行）
- 已正确使用 `auto-pm plc check`（行 51, 70-77）✓
- 无 specmgr 引用 ✓
- 仅需小修：确认无遗漏的过时工具引用

---

## 三、Proposed Changes（具体修改方案）

### 修改 1: pm-workflow/SKILL.md — 工具引用更新（问题 5.1）

**位置**: 行 29-31

**替换前**:
```
# SpecMgr：规范健康检查
specmgr -w "<工作空间根>" check|index|frontmatter|report
```

**替换后**:
```
# 规范健康检查（auto-pm spec 子命令，吸收原 specmgr 功能）
auto-pm -w "<工作空间根>" spec check|index|frontmatter|report [--auto-fix] [--dry-run]
```

**位置**: 行 37

**替换前**:
```
> 注意：pm-mgr（SW-2026-007）已被auto-pm（SW-2026-008）取代。pm-mgr命令仍可用但不再维护，建议所有新项目使用auto-pm。
```

**替换后**:
```
> 注意：pm-mgr（SW-2026-007）已被 auto-pm（SW-2026-008）取代；specmgr（SW-2026-006）已被 auto-pm 吸收为 `auto-pm spec` 子命令。旧命令仍可用但不再维护，建议所有新项目使用 auto-pm。
```

---

### 修改 2: pm-workflow/SKILL.md — Step 3.5 增加 fixture 健康检查引用（问题 4.2）

**位置**: 行 127-131（Step 3.5 第 3 点之后）

**在"4. 未验证禁止回写"之前插入新条目**:
```
4. **fixture 健康检查**（测试失败时优先排查）：
   - fixture 是否创建了项目标志文件？（PM_SESSION_*.md / .copier-answers.yml / .plc.json）
   - fixture 的 mock 配置是否返回非 None 值？（打印 mock.return_value 确认）
   - 测试中是否有 `if x is not None:` 类条件断言？（改为 `assert x is not None` + `assert x.字段 == 期望值`）
   - 详细的 fixture 健康检查清单见 `fullstack-engineer` 技能"Fixture 健康检查清单"章节
```

（原"4. 未验证禁止回写"改为"5. 未验证禁止回写"）

---

### 修改 3: pm-workflow/SKILL.md — Step 3.6 dogfooding 闭环质量门禁强化（问题 3.3）

**位置**: 行 133-151（Step 3.6 第 1 点末尾追加）

**在第 1 点"CHG 章节完整性校验"的末尾追加**:
```
   - **禁止**用 `--allow-partial-verification` 绕过章节完整性检查
   - 建议在 `change transition` 流转到 closed 前，由 CLI 自动校验 12 章节非空（当前为人工检查，后续 auto-pm 增强后改为自动）
```

---

### 修改 4: pm-workflow/SKILL.md — Step 3.7 增加双向校验（问题 2.3）

**位置**: 行 153-172（Step 3.7 第 4 点之后追加）

**在第 4 点"验证状态标注"之后追加新条目**:
```
5. **读取时双向校验**：
   - 读取 PM_SESSION §3/§8 中的声明时，若发现未标注验证状态（`[已验证]`/`[待验证]`），**视为"待验证"**
   - "待验证"的声明**不得作为决策依据**，必须先运行时验证
   - 回写前：必须标注验证状态
   - 读取时：未标注 = 待验证 = 不可作为决策依据
```

---

### 修改 5: pm-workflow/SKILL.md — 新增 Step 3.8 门禁实测强制检查（问题 2.1）

**位置**: Step 3.7 之后（行 172 之后），Step 4 之前（行 174 之前）

**插入新章节**:
```
### Step 3.8：门禁实测强制检查（回写 PM_SESSION §3 前必做）

回写 §3 spec_compliance 或 §6 声明门禁状态前，**必须**实际运行以下命令并记录真实输出：

1. `ruff check auto_pm/`（或对应项目源码目录）— 记录 error 数
2. `mypy auto_pm/` — 记录 error 数和 source files 数
3. `pytest --no-cov -q`（或对应测试目录）— 记录 passed/failed/skipped 数

**禁止**基于以下来源声明门禁状态：
- 上次审查报告的声明（审查报告可能失真，见"审查报告验证模式"）
- 代码阅读推断（"只改了注释，应该不影响测试"）
- AI 记忆中的历史数据

**若门禁未通过**：§3 必须如实记录失败状态，**禁止**声明"全绿"或"0 errors"。

**例外**：纯文档/注释改动且无代码逻辑变更时，可只运行 ruff（mypy/pytest 跳过），但必须在 §3 标注"本次为文档改动，仅运行 ruff"。
```

---

### 修改 6: pm-workflow/SKILL.md — Step 4 适配双层结构（问题 1.1）

**位置**: 行 174-176（Step 4 整体替换）

**替换前**:
```
### Step 4：同步回 PM_SESSION

每次事件处理完更新：`current_focus`、`status_summary`、`artifacts_index`、对应日志（change/iteration/bug/refactor/release/spec_change）、`open_questions`。只追加，不覆盖历史。
```

**替换后**:
```
### Step 4：同步回 PM_SESSION（双层结构）

PM_SESSION 采用**双层结构**：主文件 = 活跃快照（≤150 行）+ 历史目录 = 完整档案。

**主文件结构（快照型，只保留当前状态）**：
- §0 Meta / §1 Positioning（不变）
- §2 Current Focus（只保留 current_focus + milestone，不保留 previous_focus 链）
- §3 Status Summary（只保留 in_progress + 最近 3 条 completed 摘要 + open_questions，早期 completed 指向历史目录）
- §4 Artifacts Index（路径失效的条目即时清理）
- §5 Current Iteration Log（只保留本轮迭代的日志，上轮自动归档到历史目录）
- §6 Latest Implementation（只保留最近 3 条 Implementation Log，早期指向 CHG-*.md §9/§10）
- §8 Handoff Notes（只保留 current_state + 最新 1 条 skill_handoff + watchouts，早期归档）
- §9 Next Actions（只保留未完成的 Next Actions，已完成的自动删除或移到历史目录）

**每次事件处理完更新**：`current_focus`、`status_summary`、`artifacts_index`、对应日志（change/iteration/bug/refactor/release/spec_change）、`open_questions`。只追加，不覆盖历史；主文件超 150 行时触发归档（见 Step 4.5）。
```

---

### 修改 7: pm-workflow/SKILL.md — Step 4.5 替换为双层结构归档规则（问题 1.1，核心改动）

**位置**: 行 178-192（Step 4.5 整体替换）

**替换前**（旧 §4.5 间歇精简触发规则，治标方案）

**替换后**:
```
### Step 4.5：PM_SESSION 双层结构归档规则（防膨胀彻底方案）

PM_SESSION 主文件保持 ≤150 行，超过即触发归档到历史目录。

**历史目录结构**:
```
00_项目管理/06_PM_SESSION历史/
  ├── 2026-07-04_V0.6.0.md
  ├── 2026-07-08_V0.9.2.md
  └── 2026-07-13_V1.0.0.md
```

**归档触发机制（自动化，不走 CHG 闭环）**:
- **版本发布时归档**：每次版本号升级（pyproject.toml 版本号变化），将本轮迭代的 §5/§6/§8 完整记录归档到 `06_PM_SESSION历史/YYYY-MM-DD_Vx.x.x.md`
- **主文件超 150 行时归档**：主文件行数超过 150 行时，将早期 §3 completed/§5/§6/§8 条目归档到历史目录，主文件只保留快照
- **不创建 CHG**：归档是基础设施维护操作，不是功能变更，**不需要**走 dogfooding 闭环

**归档操作**:
```powershell
auto-pm -w "<工作空间根>" pm-session archive <项目ID> --version <版本号>
```
（若 auto-pm 未支持此命令，用 Edit 工具手工归档：① 创建历史目录文件，剪切早期条目；② 主文件只保留快照）

**归档后校验**:
- §4 Artifacts Index 路径有效性（归档文件路径正确）
- §2/§8 版本号一致性
- 历史目录文件命名格式：`YYYY-MM-DD_Vx.x.x.md`（禁止版本号后缀，见"文件命名规范"例外）

**与旧 §4.5 间歇精简规则的区别**:
- 旧规则：阈值触发后才精简（治标，精简前已膨胀）
- 新规则：双层结构，主文件永远 ≤150 行（治本，归档自动化）
```

---

### 修改 8: pm-workflow/SKILL.md — 新增 Step 4.1 台账对账检查点（问题 3.1）

**位置**: Step 4.5 之后（行 192 之后），Step 5 之前（行 194 之前）

**插入新章节**:
```
### Step 4.1：台账对账检查（每次 CHG 闭环后必做）

CHG 状态流转到 closed 后，**必须**执行台账对账：

```powershell
auto-pm -w "<工作空间根>" ledger reconcile <项目ID>
```

**检查结果处理**:
- 缺失 0 / 孤儿 0 / 状态不一致 0 → 正常，继续
- 有差异 → **必须修复后才能进入下一个 CHG**

**全量对账时机**：每个迭代结束时（版本号升级前），执行全量对账：
```powershell
auto-pm -w "<工作空间根>" ledger reconcile <项目ID> --auto-fix
```

**禁止**：在台账有差异的情况下升级版本号或开始新 CHG。
```

---

### 修改 9: pm-workflow/SKILL.md — 新增 retrofit 模式文档化（问题 3.2）

**位置**: Step 4.1 之后

**插入新章节**:
```
### retrofit 模式（先实施后补单）

**适用场景**:
- 紧急修复（P0 Bug 需立即修复，来不及先走变更单流程）
- 历史遗漏（发现已有提交缺变更单）
- 架构文档化（零代码改动的文档/注释补单）

**操作方式**:
```powershell
auto-pm -w "<工作空间根>" change create --retrofit --pid <项目ID> --domain <D> --nature <N> --scope <S> --applicant <A> --background <B> --necessity <N>
```

**retrofit 模式特点**:
- 变更单直接创建为 closed 状态（跳过 9 步状态流转）
- 台账自动补建
- 仍需填写 §5-§12 完整章节
- §9 实施记录填写实际已完成的变更内容

**注意事项**:
- retrofit 是**例外流程**，不应成为常态
- 每个 retrofit 补单后必须执行 `ledger reconcile` 确认台账一致
- 若 retrofit 补单数量超过总 CHG 的 20%，需反思流程是否前置不足
```

---

### 修改 10: pm-workflow/SKILL.md — 新增审查报告验证模式（问题 2.2）

**位置**: retrofit 模式之后

**插入新章节**:
```
### 审查报告验证模式（收到外部 AI 审查报告时触发）

外部审查报告（Claude/deepseek/其他 AI 产出）中的每一项声明，**必须**按以下分类验证：

| 声明类型 | 验证方式 |
|----------|----------|
| 门禁声明（ruff/mypy/pytest 结果） | 必须运行时实测（见 Step 3.8） |
| 文件存在性声明（"文件 X 不存在"/"文件 Y 有 Z 行"） | 必须用 Glob/Read 验证 |
| 代码行为声明（"函数 X 做了 Y"） | 必须 Read 源码验证 |
| 依赖声明（"pyproject.toml 包含 X 依赖"） | 必须 Read pyproject.toml 验证 |

**验证结果标注**:
- ✅ 已验证为真
- ❌ 已验证为假（失真）
- ⚠️ 部分失真（声明部分正确）

**禁止**直接采信外部审查报告的结论进行修复，必须先完成验证。

**失真度记录**：验证完成后，在 PM_SESSION §6 记录审查报告失真度（严重失真 X% + 部分失真 Y% + 仍真实存在 Z%），作为后续使用该 AI 报告的参考。

**历史数据参考**（auto-pm 项目经验）:
- V0.9.1 Claude v3 诊断报告：严重失真 42% + 部分失真 16% + 仍真实存在 42%
- V0.9.2 Claude 诊断报告：P2-P4 项 7/7 严重失真
- 2026-07-12 deepseek V0.9.2 深度审查：整体准确性高，但仍有 5 项数值性偏差
```

---

### 修改 11: pm-workflow/SKILL.md — §8 标准化结构强化 skill_handoff 严格 1 条（问题 5.2）

**位置**: 行 233-249（§8 Handoff Notes 标准化结构）

**修改表格中 `skill_handoff` 行**:

**替换前**:
```
| `skill_handoff`（最新 1 条） | 切换原因 + 目标技能 + 起手任务 + 关键约束 | 1 条 |
| `skill_handoff_archived` | 超过 3 条的早期交接记录归档 | 保留为历史参考 |
```

**替换后**:
```
| `skill_handoff` | 切换原因 + 目标技能 + 起手任务 + 关键约束 | **严格 1 条**（最新） |
| `skill_handoff_archived` | 早期交接记录归档到 `06_PM_SESSION历史/`（见 Step 4.5） | 历史目录 |
```

**并在"禁止"列表中追加**:
```
- §8 skill_handoff 保留超过 1 条（早期必须归档到历史目录，不保留在主文件）
```

---

### 修改 12: pm-workflow/SKILL.md — §5/§6 职责分离说明（问题 1.2）

**位置**: Step 4 回写规则中（修改 6 已重写 Step 4，在其中追加职责说明）

**在 Step 4 的"每次事件处理完更新"之后追加**:
```
**§5/§6 职责分离**（避免重复记录）:
- §5 change_log = 事件索引（一行摘要 + CHG 编号 + 日期），不记录详情
- §6 Implementation Log = 技术实施详情（changed_files + impact + risks），详情也可只放在 CHG-*.md §9 中，§6 只保留"指向 CHG 编号 + 一句话摘要"
```

---

### 修改 13: fullstack-engineer/SKILL.md — 工具参考表更新（问题 5.1）

**位置**: 行 52-57（工具参考表）

**替换前**:
```
| 工具 | 用途 |
|------|------|
| auto-pm（SW-2026-008） | 自动化项目管理工具，支持项目CRUD、PLC检查/修复、变更管理、模板管理 |
| specmgr（SW-2026-006） | 规范管理工具，check/index/frontmatter/report |
| pm-mgr（SW-2026-007） | 项目结构初始化与检查工具 |
```

**替换后**:
```
| 工具 | 用途 |
|------|------|
| auto-pm（SW-2026-008） | 自动化项目管理工具，支持项目CRUD、PLC检查/修复、变更管理、模板管理、规范检查（吸收原 specmgr）、台账对账 |
```

---

### 修改 14: fullstack-engineer/SKILL.md — 增加 fixture 健康检查清单（问题 4.2）

**位置**: 行 131（Bug 诊断前置纪律第 3 点之后）

**在第 3 点"测试问题 vs 生产问题分离"之后，第 4 点之前插入新章节**:
```
4. **fixture 健康检查清单**（测试失败时先查 fixture，再查生产代码）：
   - fixture 是否创建了项目标志文件？（PM_SESSION_*.md / .copier-answers.yml / .plc.json）
   - fixture 的路径结构是否与生产环境一致？（如 02_PLC程序/PLC_ST/ 目录层级）
   - fixture 的 mock 配置是否返回非 None 值？（打印 mock.return_value 确认）
   - 测试中是否有 `if x is not None:` 类条件断言？（改为 `assert x is not None` + `assert x.字段 == 期望值`）
   - fixture 的 scope 是否合理？（session 级 fixture 修改后会影响后续测试）

   **条件断言检测规则**（以下模式视为"假通过风险"，必须改为无条件断言）：
   - `if result is not None: assert ...` → `assert result is not None` + `assert result.xxx`
   - `if cr: assert ...` → `assert cr is not None` + `assert cr.xxx`
   - `try: assert ... except AssertionError: pass` → 删除 try/except，直接 assert
```

（原"4. 未验证禁止回写"改为"5. 未验证禁止回写"）

---

### 修改 15: fullstack-engineer/SKILL.md — 增加 GUI 测试隔离检查清单（问题 4.1）

**位置**: 行 163（GUI 测试基础设施规范第 4 点之后）

**在第 4 点"flaky test 诊断顺序"之后追加新章节**:
```
5. **GUI 测试隔离检查清单**（编写/修改 GUI 测试前必查）：
   - □ 是否使用 tmp_path 隔离？（禁止在真实工作空间创建项目）
   - □ autouse fixture 的 except 是否用 logging.warning 暴露失败？（禁止 except Exception: pass）
   - □ 是否有 session 级状态残留？（检查 conftest.py 中 session 级 fixture 的清理逻辑）
   - □ 测试结束后是否清理了创建的项目/变更单？（检查 _cleanup_test_changes 是否被调用）
   - □ 是否在测试专用工作空间（如 DJ-2026-998）中残留了数据？（测试后检查并清理）

6. **全量回归卡住诊断流程**（全量 pytest 卡住时，进度停滞 >2 分钟）：
   1. 是否是 GUI 测试卡住？（检查是否最后执行的 tests/qml/ 或 tests/gui/）
   2. 是否是 session 级 fixture 污染？（检查 conftest.py session 级 fixture）
   3. 是否是 Qt 事件循环阻塞？（检查是否有 QEventLoop.exec() 或 QTest.qWait 未超时）
   4. 临时方案：分批执行 pytest（spec/change/app/core 一批 + qml 一批 + 其他一批）
```

---

### 修改 16: fullstack-engineer/SKILL.md — Step 4 增加门禁实测前置检查（问题 2.1）

**位置**: 行 112-113（Step 4 回写 PM_SESSION §6-§9）

**替换前**:
```
### Step 4：回写 PM_SESSION §6-§9
```

**替换后**:
```
### Step 4：回写 PM_SESSION §6-§9（含门禁实测前置检查）

**回写前必做**（若本轮有代码改动）：实际运行 ruff/mypy/pytest 并记录真实输出，禁止基于推断声明门禁状态。详见 `pm-workflow` Step 3.8 门禁实测强制检查。
```

---

### 修改 17: project-rule.md — 迭代文档同步规则增加台账对账（问题 3.1）

**位置**: 行 103-113（迭代文档同步规则）

**在第 5 点"变更记录"之后追加**:
```
6. **台账对账强制**：每次 CHG 闭环后必须执行 `auto-pm -w "<工作空间根>" ledger reconcile <项目ID>`，台账有差异时禁止升级版本号或开始新 CHG。每个迭代结束（版本号升级前）执行全量对账 `ledger reconcile <项目ID> --auto-fix`
```

---

### 修改 18: project-rule.md — 工具引用更新 + 后台任务监控全局化（问题 5.1 + 4.3）

**位置**: 行 31（规范管理工具章节）

**替换前**:
```
- **SpecMgr**（SW-2026-006）：全局可用 `specmgr -w "<工作空间根>" check|index|frontmatter|report [--auto-fix] [--dry-run]`
- **auto-pm**（SW-2026-008）：`auto-pm -w "<工作空间根>" project create|show|edit|retrofit|delete ...` 和 `auto-pm -w "<工作空间根>" plc init|check|repair|standardize ...`
- pm-mgr（SW-2026-007）已被 auto-pm（SW-2026-008）取代
```

**替换后**:
```
- **auto-pm**（SW-2026-008）：统一项目管理工具，吸收原 specmgr 和 pm-mgr 功能
  - 项目管理：`auto-pm -w "<工作空间根>" project create|show|edit|retrofit|delete ...`
  - PLC 管理：`auto-pm -w "<工作空间根>" plc init|check|repair|standardize ...`
  - 规范检查：`auto-pm -w "<工作空间根>" spec check|index|frontmatter|report [--auto-fix] [--dry-run]`
  - 变更管理：`auto-pm -w "<工作空间根>" change create|list|show|transition ...`
  - 台账对账：`auto-pm -w "<工作空间根>" ledger reconcile <项目ID> [--auto-fix]`
- specmgr（SW-2026-006）已被 auto-pm 吸收为 `auto-pm spec` 子命令
- pm-mgr（SW-2026-007）已被 auto-pm 取代
```

**位置**: 行 85（三、编码后验证 第 6 点之后）

**在第 6 点"Bug修复"之后追加**:
```
7. **后台任务监控**：启动后台测试/构建任务后，禁止被动等待通知。必须：①设置预期完成时间；②分段主动轮询（timeout=120s）；③超过预期时间未完成时立即读日志看进度，进度停滞即停止并诊断根因；④给用户明确时间预期。详见 `fullstack-engineer` 技能"后台任务监控纪律"章节
```

---

### 修改 19: plc-electrical-engineer/SKILL.md — 工具引用确认（问题 5.1）

**位置**: 全文检查

**当前状态**: 已正确使用 `auto-pm plc check`（行 51, 70-77），无 specmgr 引用。

**操作**: 无需修改（已是最新的）。仅在计划中记录已确认。

---

## 四、Assumptions & Decisions（假设与决策）

1. **假设**: 用户已审核通过 `技能迭代建议清单_auto-pm项目经验.md` 中的 13 个改进点（前序会话已确认）
2. **假设**: PM_SESSION 双层结构方案符合用户预期（"彻底解决"诉求）
3. **决策**: 归档操作不走 CHG dogfooding 闭环（视为基础设施维护），这是治本方案的关键
4. **决策**: 修改顺序为 pm-workflow → fullstack-engineer → project-rule → plc-electrical-engineer（按改动量降序）
5. **决策**: 所有修改用 Edit 工具（通过 VS Code API 同步缓冲区），禁止用 Python 脚本写磁盘
6. **决策**: §5/§6 职责分离说明合并到 Step 4 中（修改 6 + 修改 12 合并执行），不单独成章节
7. **决策**: plc-electrical-engineer 无需修改（已确认工具引用正确）

---

## 五、Implementation Order（实施顺序）

### 阶段 1: pm-workflow/SKILL.md（修改 1-12，9 处变更）

按文件位置从上到下顺序执行，避免行号偏移：
1. 修改 1: 行 29-31 + 行 37 工具引用更新
2. 修改 2: Step 3.5 增加 fixture 健康检查引用
3. 修改 3: Step 3.6 强化
4. 修改 4: Step 3.7 增加双向校验
5. 修改 5: 新增 Step 3.8 门禁实测强制检查
6. 修改 6 + 12: Step 4 适配双层结构 + §5/§6 职责分离（合并）
7. 修改 7: Step 4.5 替换为双层结构归档规则（核心改动）
8. 修改 8: 新增 Step 4.1 台账对账检查点
9. 修改 9: 新增 retrofit 模式文档化
10. 修改 10: 新增审查报告验证模式
11. 修改 11: §8 标准化结构强化

### 阶段 2: fullstack-engineer/SKILL.md（修改 13-16，3 处变更）

1. 修改 13: 工具参考表更新
2. 修改 14: 增加 fixture 健康检查清单
3. 修改 15: 增加 GUI 测试隔离检查清单
4. 修改 16: Step 4 增加门禁实测前置检查

### 阶段 3: project-rule.md（修改 17-18，2 处变更）

1. 修改 17: 迭代文档同步规则增加台账对账
2. 修改 18: 工具引用更新 + 后台任务监控全局化

### 阶段 4: plc-electrical-engineer/SKILL.md（修改 19，无变更）

确认无需修改。

---

## 六、Verification Steps（验证步骤）

1. **语法检查**：修改后用 Read 工具读取每个修改的文件，确认 Markdown 格式正确（无破损的代码块、表格、列表）
2. **行数对比**：pm-workflow/SKILL.md 从 255 行预计增加到 ~400 行（新增 4 个章节）；fullstack-engineer/SKILL.md 从 233 行预计增加到 ~290 行；project-rule.md 从 127 行预计增加到 ~150 行
3. **交叉引用检查**：
   - pm-workflow 中引用的 `fullstack-engineer` 章节（fixture 健康检查清单）确实存在于 fullstack-engineer 中
   - fullstack-engineer 中引用的 `pm-workflow` Step 3.8 确实存在于 pm-workflow 中
4. **工具引用一致性**：所有技能文件中 `specmgr` → `auto-pm spec`、`pm-mgr` → `auto-pm` 更新一致
5. **规则一致性**：project-rule.md 的台账对账要求与 pm-workflow Step 4.1 一致
6. **不创建新文件**：所有修改都是 Edit 现有文件，不创建新的 SKILL.md 或规则文件

---

## 七、Risk & Mitigation（风险与缓解）

| 风险 | 缓解措施 |
|------|----------|
| PM_SESSION 双层结构需要 auto-pm 支持 `pm-session archive` 命令 | 计划中已注明"若 auto-pm 未支持此命令，用 Edit 工具手工归档"作为降级方案 |
| 新增章节较多，pm-workflow 行数膨胀 | 双层结构本身是解决膨胀的方案；新增章节是规则沉淀，不会无限增长 |
| 归档不走 CHG 闭环可能与用户 dogfooding 习惯冲突 | 已在决策中说明归档是基础设施维护操作；若用户反对可调整 |
| 工具引用更新后旧命令仍可用 | 保留"旧命令仍可用但不再维护"的说明，不删除旧命令 |
