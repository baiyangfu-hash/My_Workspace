# 技能迭代建议清单 — 基于 auto-pm 项目迭代经验

> **来源**: SW-2026-008_auto-pm 项目 V0.3.0→V1.0.0 迭代经验（56 次 dogfooding 闭环）
> **产出形式**: 建议清单（经用户审核后再修改技能文件）
> **聚焦方向**: 防失真机制 / 变更管理闭环 / 测试质量保障 / PM 文件膨胀彻底解决
> **日期**: 2026-07-14

---

## 一、PM 文件膨胀彻底解决方案（用户重点诉求）

### 问题 1.1 [P0] PM_SESSION 从"日志型"改为"快照型"结构

**迭代证据**:
- V0.7.0（CHG-087/088/089 三连闭环）整个迭代专门处理膨胀：489KB/1542 行 → 62KB/170 行，耗费 3 个 CHG 闭环
- V0.9.2 Phase 4 又要归档 §6 早期 24 行（156.6KB→109.7KB）
- M5 迭代时 PM_SESSION 318>300 行超限，又要归档 CHG-119/120/121
- 当前 §5 change_log 单条记录 100-300 字，10 条就上千行

**根因分析**:
当前 PM_SESSION 是"日志型"结构——§5/§6/§8/§9 都在持续追加完整记录，"记录全部都要"的硬约束与"主文件保持精简"存在根本矛盾。§4.5 间歇精简规则是治标方案：阈值触发后才精简，精简前已经膨胀，且归档本身又要走 CHG 闭环增加开销。

**彻底解决方案: PM_SESSION 双层结构**

将 PM_SESSION 从"一个文件装所有"改为"主文件=活跃快照 + 历史目录=完整档案"：

```
PM_SESSION_<项目编号>.md          ← 主文件（快照型，≤150 行）
00_项目管理/06_PM_SESSION历史/     ← 历史目录（按版本归档）
  ├── 2026-07-04_V0.6.0.md
  ├── 2026-07-08_V0.9.2.md
  └── 2026-07-13_V1.0.0.md
```

**主文件结构（快照型，只保留当前状态）**:
- §0 Meta（不变）
- §1 Positioning（不变）
- §2 Current Focus（只保留 current_focus + milestone，不保留 previous_focus 链）
- §3 Status Summary（只保留 in_progress + 最近 3 条 completed 摘要 + open_questions，早期 completed 指向历史目录）
- §4 Artifacts Index（不变，但路径失效的条目即时清理）
- §5 Current Iteration Log（只保留本轮迭代的日志，上轮自动归档到历史目录）
- §6 Latest Implementation（只保留最近 3 条 Implementation Log，早期指向 CHG-*.md §9/§10）
- §8 Handoff Notes（只保留 current_state + 最新 1 条 skill_handoff + watchouts，早期归档）
- §9 Next Actions（只保留未完成的 Next Actions，已完成的自动删除或移到历史目录）

**归档触发机制（自动化，不走 CHG 闭环）**:
- **版本发布时**：每次版本号升级（pyproject.toml 版本号变化），自动将本轮迭代的 §5/§6/§8 完整记录归档到 `06_PM_SESSION历史/YYYY-MM-DD_Vx.x.x.md`
- **不创建 CHG**：归档是基础设施维护操作，不是功能变更，不需要走 dogfooding 闭环
- **主文件永远精简**：归档后主文件只保留"快照"，行数永远 ≤150 行

**影响的技能文件**: `pm-workflow/SKILL.md`（§4.5 替换为新的双层结构规则 + Step 4 回写规则更新）

---

### 问题 1.2 [P1] §5 change_log 和 §6 Implementation Log 职责重叠

**迭代证据**: 同一个 CHG 闭环事件，在 §5 change_log 和 §6 Implementation Log 都记录一遍，内容高度重叠。例如 2026-07-10 M4 项目管理补齐闭环在 §5 和 §6 都有详细记录。

**改进建议**: 明确职责分离：
- §5 change_log = 事件索引（一行摘要 + CHG 编号 + 日期），不记录详情
- §6 Implementation Log = 技术实施详情（changed_files + impact + risks），详情也可以只放在 CHG-*.md §9 中，§6 只保留"指向 CHG 编号 + 一句话摘要"

**影响的技能文件**: `pm-workflow/SKILL.md`（Step 4 回写规则 + §5/§6 职责定义）

---

## 二、防失真机制

### 问题 2.1 [P0] PM_SESSION §3 spec_compliance 声明反复失真

**迭代证据**:
- 2026-07-07 重新诊断发现 §3 声明"ruff/mypy 0 errors + 999 passed"，实测 ruff 26 errors + mypy 34 errors + pytest INTERNALERROR
- 2026-07-11 审查报告声称"mypy 0 errors"，2026-07-13 实测有 1 个 error
- V0.9.1 Claude 诊断报告失真度 42% 严重失真 + 16% 部分失真
- V0.9.2 Phase 1 专门修正 §2/§8 失真声明

**根因分析**: 技能虽有"未验证禁止回写"规则，但缺少"回写前必须运行时实测"的强制检查点。AI 容易基于上次的声明或代码阅读推断门禁状态，而非实际运行 ruff/mypy/pytest。

**改进建议**: 在 pm-workflow Step 4（同步回 PM_SESSION）之前，增加**门禁实测强制检查点**：

```
### Step 3.8: 门禁实测强制检查（回写 PM_SESSION §3 前必做）

回写 §3 spec_compliance 或 §6 声明门禁状态前，必须实际运行以下命令并记录真实输出：
1. `ruff check auto_pm/` — 记录 error 数
2. `mypy auto_pm/` — 记录 error 数和 source files 数
3. `pytest --no-cov -q` — 记录 passed/failed/skipped 数

禁止基于以下来源声明门禁状态：
- 上次审查报告的声明
- 代码阅读推断（"只改了注释，应该不影响测试"）
- AI 记忆中的历史数据

若门禁未通过，§3 必须如实记录失败状态，禁止声明"全绿"。
```

**影响的技能文件**: `pm-workflow/SKILL.md`（新增 Step 3.8）+ `fullstack-engineer/SKILL.md`（Step 4 回写前检查）

---

### 问题 2.2 [P1] 外部审查报告（Claude/deepseek）失真度未校验

**迭代证据**:
- V0.9.1 Claude v3 诊断报告 P2-P4 项 7/7 严重失真
- V0.9.2 Claude 诊断报告 #6 pywebview 依赖声明失真（dependencies 中无 pywebview）
- 2026-07-12 deepseek V0.9.2 深度审查报告整体准确性高，但仍有 5 项数值性偏差

**根因分析**: 外部 AI 产出的审查报告常含失真声明（基于过时信息或推断），pm-workflow 当前没有"审查报告验证"模式的强制流程。

**改进建议**: 在 pm-workflow 增加**审查报告验证模式**：

```
### 审查报告验证模式（当收到外部 AI 审查报告时触发）

外部审查报告（Claude/deepseek/其他 AI 产出）中的每一项声明，必须按以下分类验证：

1. **门禁声明**（ruff/mypy/pytest 结果）→ 必须运行时实测
2. **文件存在性声明**（"文件 X 不存在"/"文件 Y 有 Z 行"）→ 必须用 Glob/Read 验证
3. **代码行为声明**（"函数 X 做了 Y"）→ 必须用 Read 验证
4. **依赖声明**（"pyproject.toml 包含 X 依赖"）→ 必须 Read pyproject.toml 验证

验证结果标注：
- ✅ 已验证为真
- ❌ 已验证为假（失真）
- ⚠️ 部分失真（声明部分正确）

禁止直接采信外部审查报告的结论进行修复，必须先完成验证。
```

**影响的技能文件**: `pm-workflow/SKILL.md`（新增审查报告验证模式）

---

### 问题 2.3 [P1] "未验证禁止回写"规则执行不到位

**迭代证据**: 虽然规则已写入技能（§8 中的诊断结论必须标注 [已验证]/[待验证]），但 2026-07-07 诊断发现 §3 spec_compliance 仍有未验证就回写的声明。

**改进建议**: 强化规则为**双向检查**：
- 回写前：必须标注验证状态
- 读取时：若发现未标注验证状态的声明，视为"待验证"，不得作为决策依据

**影响的技能文件**: `pm-workflow/SKILL.md`（Step 3.7 真源一致性前置校验 + Step 4 回写规则）

---

## 三、变更管理闭环

### 问题 3.1 [P0] 变更单台账与文件对不上反复出现

**迭代证据**:
- 2026-07-09 用户发现"变更台账和变更单对不上"（台账 28 条 vs 文件 40 个，缺失 12 条）
- 2026-07-14 用户又发现"有些提交没有变更单，需要补变更单"（2 个提交缺单）
- 根因：LedgerUpdater 只在 create_change_request 中调用，手工创建/retrofit 补单绕过台账更新

**根因分析**: pm-workflow 的 dogfooding 闭环流程依赖人工纪律维护台账一致性，没有自动对账检查点。虽然 CHG-108 已新增 `ledger reconcile` 命令，但技能流程中没有"何时执行对账"的规定。

**改进建议**: 在 pm-workflow Step 4（回写 PM_SESSION）之后，增加**台账对账检查点**：

```
### Step 4.1: 台账对账检查（每次 CHG 闭环后必做）

CHG 状态流转到 closed 后，必须执行台账对账：
  auto-pm -w "<工作空间根>" ledger reconcile <项目ID>

检查结果：
- 缺失 0 / 孤儿 0 / 状态不一致 0 → 正常，继续
- 有差异 → 必须修复后才能进入下一个 CHG

此外，每个迭代结束时（版本号升级前），执行全量对账：
  auto-pm -w "<工作空间根>" ledger reconcile <项目ID> --auto-fix

禁止在台账有差异的情况下升级版本号。
```

**影响的技能文件**: `pm-workflow/SKILL.md`（新增 Step 4.1）+ `project-rule.md`（迭代文档同步规则增加台账对账要求）

---

### 问题 3.2 [P1] retrofit 模式（先实施后补单）未在技能中文档化

**迭代证据**:
- CHG-108 新增 `change create --retrofit` 支持"先实施后补单"工作流
- 2026-07-14 使用 retrofit 模式补了 CHG-125/126 两个缺失变更单
- 但 pm-workflow 技能中没有描述这种工作流何时使用、如何操作

**改进建议**: 在 pm-workflow 变更/缺陷模式中增加 **retrofit 模式指引**：

```
### retrofit 模式（先实施后补单）

适用场景：
- 紧急修复（P0 Bug 需立即修复，来不及先走变更单流程）
- 历史遗漏（发现已有提交缺变更单）
- 架构文档化（零代码改动的文档/注释补单）

操作方式：
  auto-pm -w "<工作空间根>" change create --retrofit --pid <项目ID> ...

retrofit 模式特点：
- 变更单直接创建为 closed 状态（跳过 9 步状态流转）
- 台账自动补建
- 仍需填写 §5-§12 完整章节
- §9 实施记录填写实际已完成的变更内容

注意事项：
- retrofit 是例外流程，不应成为常态
- 每个 retrofit 补单后必须执行 ledger reconcile 确认台账一致
```

**影响的技能文件**: `pm-workflow/SKILL.md`（变更/缺陷模式章节）

---

### 问题 3.3 [P1] CHG 闭环质量门禁执行不到位（早期 CHG 内容不完整却 closed）

**迭代证据**:
- M4 CHG-075 内容不完整却 closed（12 章节仅 §10.1/§10.3 填写）
- 需要创建 CHG-077 重走闭环替换 dogfooding 证据

**根因分析**: 虽然 §3.6 dogfooding 闭环质量门禁已定义 12 章节非空检查，但执行时仍可能跳过。

**改进建议**: 强化 §3.6 为**自动检查**而非人工检查：
- 建议在 `change transition` 流转到 closed 前，由 CLI 自动校验 12 章节非空
- 技能中明确：禁止用 `--allow-partial-verification` 绕过章节完整性检查

**影响的技能文件**: `pm-workflow/SKILL.md`（§3.6 强化）+ 可能需要 auto-pm CLI 增强（非技能范畴）

---

## 四、测试质量保障

### 问题 4.1 [P0] GUI 测试污染反复出现

**迭代证据**:
- TD-T09 GUI 测试污染复发（2026-06-28 发现），CHG-076 残留证明 M3.5-1 修复不彻底
- 根因是 `_cleanup_test_changes` 的 `except Exception: pass` 静默吞错
- 2026-07-11 M5 全量回归时仍有"全量 pytest 含 GUI 时卡住"问题

**根因分析**: fullstack-engineer 已有"GUI 测试基础设施规范"和"禁止 except Exception: pass 静默吞错"规则，但缺少**测试隔离检查清单**，导致规则执行不到位。

**改进建议**: 在 fullstack-engineer GUI 测试基础设施规范中增加**测试隔离检查清单**：

```
### GUI 测试隔离检查清单（编写/修改 GUI 测试前必查）

□ 是否使用 tmp_path 隔离？（禁止在真实工作空间创建项目）
□ autouse fixture 的 except 是否用 logging.warning 暴露失败？（禁止 except Exception: pass）
□ 是否有 session 级状态残留？（检查 conftest.py 中 session 级 fixture 的清理逻辑）
□ 测试结束后是否清理了创建的项目/变更单？（检查 _cleanup_test_changes 是否被调用）
□ 是否在测试专用工作空间（如 DJ-2026-998）中残留了数据？（测试后检查并清理）

### 全量回归卡住诊断流程

全量 pytest 卡住时（进度停滞 >2 分钟），按以下顺序诊断：
1. 是否是 GUI 测试卡住？（检查是否最后执行的 tests/qml/ 或 tests/gui/）
2. 是否是 session 级 fixture 污染？（检查 conftest.py session 级 fixture）
3. 是否是 Qt 事件循环阻塞？（检查是否有 QEventLoop.exec() 或 QTest.qWait 未超时）
4. 临时方案：分批执行 pytest（spec/change/app/core 一批 + qml 一批 + 其他一批）
```

**影响的技能文件**: `fullstack-engineer/SKILL.md`（GUI 测试基础设施规范章节）

---

### 问题 4.2 [P1] 测试 fixture 缺陷导致假通过

**迭代证据**:
- `if cr is not None:` 类条件断言掩盖 fixture 缺陷（TD-T04 复发）
- M1 元测试 false positive：`tests/ui/test_overview_tab_asset_summary.py:41,63` 的 `if asset_summary is not None:` 触发误判
- project_memory.md 已记录"测试失败时先检查 fixture 是否完整"

**根因分析**: 技能已有"测试问题 vs 生产问题分离"规则，但缺少具体的 fixture 健康检查方法。

**改进建议**: 在 fullstack-engineer Bug 诊断前置纪律中增加**fixture 健康检查清单**：

```
### Fixture 健康检查清单（测试失败时先查 fixture，再查生产代码）

□ fixture 是否创建了项目标志文件？（PM_SESSION_*.md / .copier-answers.yml / .plc.json）
□ fixture 的路径结构是否与生产环境一致？（如 02_PLC程序/PLC_ST/ 目录层级）
□ fixture 的 mock 配置是否返回非 None 值？（打印 mock.return_value 确认）
□ 测试中是否有 `if x is not None:` 类条件断言？（改为 `assert x is not None` + `assert x.字段 == 期望值`）
□ fixture 的 scope 是否合理？（session 级 fixture 修改后会影响后续测试）

### 条件断言检测规则

以下模式视为"假通过风险"，必须改为无条件断言：
- `if result is not None: assert ...`  →  `assert result is not None` + `assert result.xxx`
- `if cr: assert ...`  →  `assert cr is not None` + `assert cr.xxx`
- `try: assert ... except AssertionError: pass`  →  删除 try/except，直接 assert
```

**影响的技能文件**: `fullstack-engineer/SKILL.md`（Bug 诊断前置纪律章节）

---

### 问题 4.3 [P2] 后台任务监控规范已有但执行不到位

**迭代证据**: fullstack-engineer 已有"后台任务监控纪律"，但 PM_SESSION 中记录"全量 pytest 含 GUI 时卡住"问题反复出现，且每次卡住后都是被动发现而非主动监控。

**改进建议**: 规范已足够，建议在 project-rule.md 中增加**后台任务监控提醒**作为全局规则（当前只在 fullstack-engineer 技能中），确保所有技能都遵循。

**影响的技能文件**: `project-rule.md`（编码后验证章节增加后台任务监控要求）

---

## 五、跨技能问题

### 问题 5.1 [P1] 技能中工具引用过时

**迭代证据**:
- fullstack-engineer 仍引用独立的 `specmgr` 和 `pm-mgr`，但 specmgr 已被 auto-pm 吸收为规范中心功能，pm-mgr 已被 auto-pm 取代
- pm-workflow 仍提到 `specmgr -w` 命令，但实际应使用 `auto-pm -w ... spec check`

**改进建议**: 更新所有技能文件中的工具引用：
- `specmgr -w ... check` → `auto-pm -w ... spec check`
- `pm-mgr` → `auto-pm`（已取代）
- 保留 specmgr 作为历史参考但标注"已被 auto-pm 吸收"

**影响的技能文件**: `pm-workflow/SKILL.md` + `fullstack-engineer/SKILL.md` + `plc-electrical-engineer/SKILL.md`

---

### 问题 5.2 [P2] §8 skill_handoff 膨胀导致 CHG-109 专门改造

**迭代证据**:
- §8 skill_handoff 每次技能切换都追加一条，膨胀到 Edit 工具无法处理超长单行
- CHG-109 专门改造 `pm-session archive` 支持 §8 条目级归档
- 技能中 §8 标准化结构已定义 skill_handoff 保留最新 1 条，但实际执行中常保留 3+ 条

**改进建议**: 
- 若问题 1.1 的双层结构方案落地，§8 skill_handoff 自然只保留最新 1 条（早期自动归档到历史目录）
- 强化技能规则：§8 skill_handoff 严格只保留最新 1 条，超过即归档（不需要 CHG-109 的条目级归档工具，直接整文件归档）

**影响的技能文件**: `pm-workflow/SKILL.md`（§8 标准化结构）

---

## 改进优先级总览

| 优先级 | 问题编号 | 改进点 | 影响技能 | 复杂度 |
|:---:|:---:|---|---|:---:|
| P0 | 1.1 | PM_SESSION 双层结构（快照+历史目录） | pm-workflow | 高 |
| P0 | 2.1 | 门禁实测强制检查点 | pm-workflow + fullstack-engineer | 中 |
| P0 | 3.1 | 台账对账检查点 | pm-workflow + project-rule | 中 |
| P0 | 4.1 | GUI 测试隔离检查清单 | fullstack-engineer | 中 |
| P1 | 1.2 | §5/§6 职责分离 | pm-workflow | 低 |
| P1 | 2.2 | 审查报告验证模式 | pm-workflow | 中 |
| P1 | 2.3 | "未验证禁止回写"双向检查 | pm-workflow | 低 |
| P1 | 3.2 | retrofit 模式文档化 | pm-workflow | 低 |
| P1 | 4.2 | fixture 健康检查清单 | fullstack-engineer | 中 |
| P1 | 5.1 | 工具引用更新 | 全部技能 | 低 |
| P1 | 5.2 | §8 skill_handoff 严格 1 条 | pm-workflow | 低 |
| P1 | 3.3 | CHG 闭环质量门禁自动检查 | pm-workflow | 中 |
| P2 | 4.3 | 后台任务监控全局化 | project-rule | 低 |

---

## 实施建议

### 阶段 1（P0 改进，建议优先）
1. **PM_SESSION 双层结构**（问题 1.1）— 影响最大，彻底解决膨胀问题
2. **门禁实测强制检查点**（问题 2.1）— 防失真最关键
3. **台账对账检查点**（问题 3.1）— 变更管理闭环核心
4. **GUI 测试隔离检查清单**（问题 4.1）— 测试质量保障

### 阶段 2（P1 改进，P0 落地后）
5. §5/§6 职责分离 + retrofit 模式文档化 + 审查报告验证模式
6. fixture 健康检查清单 + 工具引用更新 + §8 skill_handoff 严格化

### 阶段 3（P2 改进，按需）
7. 后台任务监控全局化 + CHG 闭环质量门禁自动检查

---

## 假设与决策

1. **假设**: 用户审核通过后，会按阶段顺序修改技能文件
2. **假设**: PM_SESSION 双层结构方案（问题 1.1）需要用户确认是否符合预期
3. **决策**: 改进建议清单先输出，不直接修改技能文件（用户已确认产出形式为"先出建议清单"）
4. **决策**: PM_SESSION 膨胀方案选择"双层结构"（快照+历史目录）而非"自动滚动归档"或"去中心化记录"，因为双层结构最简单且彻底
5. **待用户确认**: 归档操作不走 CHG dogfooding 闭环（视为基础设施维护），是否符合用户期望

---

## 验证步骤

用户审核建议清单后：
1. 确认哪些改进点采纳
2. 确认 PM_SESSION 双层结构方案是否符合预期
3. 确认归档不走 CHG 闭环是否符合期望
4. 确认实施顺序（阶段 1→2→3）
5. 审核通过后，按阶段修改对应的技能文件
