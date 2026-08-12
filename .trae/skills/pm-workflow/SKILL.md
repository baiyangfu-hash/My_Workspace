---
name: pm-workflow
description: "统一产品/项目管理主入口。适用于需求澄清、PRD/REQ/DES、线框方案、任务拆解、迭代推进、变更/缺陷/发布管理，并以 PM_SESSION_<项目编号>.md 作为单一真源。"
---

# PM Workflow

统一 PM 入口：需求澄清 → PRD/REQ/DES → 方案/线框 → 任务拆解 → 迭代推进 → 变更/缺陷/发布。避免在多个 PM 子技能间切换。

## 适用范围

- **software** 项目：`pyproject.toml`、`src/`、`tests/`、`ui/`、`main.py`
- **plc** 项目：`02_PLC程序/`、`03_HMI设计/`、`04_现场调试/`
- 任务系统默认本地 Markdown，可选同步 GitHub

## 单一真源

- 每个项目根目录必须有 `PM_SESSION_<项目编号>.md`
- 项目编号优先从目录名解析（如 `SW-2026-005_xxx` → `SW-2026-005`）
- 若不存在：使用 `auto-pm project create` 或 `auto-pm project retrofit` 创建/补全
- 跨技能公共契约的单一真源位于 [../shared/refs/skill_coordination.md](../shared/refs/skill_coordination.md)
- `pm-workflow` 是 `PM_SESSION` 与 `.auto-pm/ai_feedback.json` 的唯一回写 owner

## 工具依赖

```powershell
# auto-pm：项目初始化、补完、健康检查、类型检测
python -m auto_pm -w "<工作空间根>" project create|show|edit|retrofit|delete ... [--stack <plc|python>] [--id <编号>] [--name <名称>]
python -m auto_pm -w "<工作空间根>" plc init|check|repair|standardize ...

# 通用原型管理（pm-workflow 独占原型设计、打包与归档）
python -m auto_pm -w "<工作空间根>" prototype bundle|check|archive|init --pid <编号> [--version <版本>]

# 工作空间治理与纯净度卡点（008 驾驶舱治理收拢）
python -m auto_pm -w "<工作空间根>" clean [--cache] [--dry-run]
python -m auto_pm doctor
```

- `-w` 必须放在子命令之前
- `project show` 自动通过多信号判据识别项目类型
- `project retrofit` 仅添加 hooks/handoffs/Spec Snapshot，不修改现有文件
- **工作空间治理硬约束**：
  - 严禁重定向测试日志（`mypy*.txt` / `pytest*.log`）或临时脚本（`.tmp_*.py`）到根目录。所有临时文件统一指定到 `.auto-pm/logs/` 或 `.auto-pm/scratch/`。
  - 在每个 PM 阶段收尾或交付时，必须自动触发 `python -m auto_pm clean` 和 `python -m auto_pm doctor`。

> 注意：pm-mgr（SW-2026-007）已被 auto-pm（SW-2026-008）取代；specmgr（SW-2026-006）已被 auto-pm 吸收为 `auto-pm spec` 子命令。旧命令仍可用但不再维护，建议所有新项目使用 auto-pm。

## 总控流程

### Step 0：进入项目并读取 PM_SESSION

1. **激活虚拟环境**（必须最先执行）：
   ```powershell
   # 从工作空间根目录查找 .venv
   & "<工作空间根>\.venv\Scripts\Activate.ps1"
   # 验证激活成功
   python --version; pip --version
   ```
   若激活失败，**立即报告用户**，说明 venv 缺失及影响（auto-pm/specmgr 不可用），不要跳过继续。

2. 运行 `auto-pm -w "<工作空间根>" project show <项目ID>` 检测项目类型
3. 查找 `PM_SESSION_<项目编号>.md`，若不存在则 `auto-pm project create`（新项目）或 `auto-pm project retrofit`（已有项目）
4. 输出 8-12 行状态摘要：项目定位、当前焦点、里程碑、进行中/下一步、未决问题、风险
5. 做轻量健康检查：`auto-pm -w "<工作空间根>" plc check <项目ID>`
6. **硬约束入口检测**：检测项目 `project_memory.md` 是否存在，若存在则读取 Hard Constraints 并在状态摘要中提示"关键约束已加载：N 条"。特别提示：
   - 禁止用 Python 脚本直接写磁盘修改项目文件（用 Edit/Write 工具）
   - 文件命名规范禁止版本号后缀（见下方"文件命名规范"）
   - GUI 测试默认可见模式（禁止默认 offscreen）
7. **BOM 预检**（在修改任何文件前执行）：
   - 对即将修改的文件，先运行 `auto-pm -w "<工作空间根>" constraint heal --file <文件路径>` 剥离多余 BOM
   - 若文件 BOM 数量 > 1，必须 heal 后再使用 Edit/Write 工具，否则会导致缓冲区陈旧
   - 对技能文件（`.trae/skills/*/SKILL.md`）和 PM_SESSION 文件尤其重要
   - 修改完成后，运行 `auto-pm -w "<工作空间根>" constraint check --file <文件路径>` 确认编码健康

### Step 0.5：检查 cockpit AI 上下文（若存在则跳过 Step 0-1，直接分发到子技能）

1. 检查 `<工作空间根>/.auto-pm/ai_context.json` 是否存在
2. **若存在**：
   - 读取 JSON，提取 `active_project`、`active_change`、`active_page`
   - 从 `active_project` 获取：项目 ID、名称、技术栈、阶段
   - 从 `active_change` 获取：变更单号、标题、领域、性质、状态
   - **跳过 Step 0**（venv 激活、`project show`、PM_SESSION 读取、健康检查）
   - **跳过 Step 1**（模式选择），模式由 `active_page` 推断：
     - `changeCenter` → 变更/缺陷/发布模式
     - `workspace` → 项目推进模式
     - `specCenter` → 规范模式
   - **跳过 Step 2**（最小提问），上下文已包含变更单详情
   - 在状态摘要中标注"上下文来源: cockpit AI 辅助"
   - **域判断 + 技能分发**：
     - `domain == "PLC"` → 构建 skill_context，调用 `Skill: plc-electrical-engineer`
     - `domain == "SCPT"` / `"PYTHON"` → 构建 skill_context，调用 `Skill: fullstack-engineer`
   - **skill_context 结构**（传递给子技能的 prompt 摘要）：
     ```json
     {
       "source": "pm-workflow",
       "project_id": "DJ-2026-005",
       "project_name": "周单机模板",
       "stack": "plc",
       "change_number": "CHG-PLC-2026-001",
       "change_title": "修复阀门控制时序错误",
       "change_domain": "PLC",
       "change_nature": "DEF",
       "change_status": "draft",
       "mode": "变更/缺陷/发布",
       "pm_summary": "上下文已通过 cockpit AI 辅助恢复，跳过项目识别、PM_SESSION 读取、模式选择。"
     }
     ```
  - **子技能返回后**：
    - 解析子技能返回的结构化 `handoff_result`（至少包含 `summary`、`changed_files`、`verification`、`risks`、`next_actions`、`watchouts`、`read_first`、`artifacts`、`chg_updates`）
    - 继续执行 Step 4（由 `pm-workflow` 统一回写 PM_SESSION §6-§9）
    - 由 `pm-workflow` 写入 cockpit 反馈：`.auto-pm/ai_feedback.json`
    - 输出摘要给用户
- **禁止**：`GUI原型设计-V2.0.md`、`V2.0-全功能自动化测试计划.md`、`PRD_V0.5.0.md`
- **正确**：`GUI原型设计.md`（版本通过 frontmatter 或正文标题标识）、`PRD.md`
- 版本演进通过文档头部 frontmatter（`version: "V2.1"`）或正文标题（`# GUI 原型设计 V2.1`）标识，文件名本身保持稳定

**例外**：
- `00_项目管理/03_执行过程/` 下的历史执行过程文件可保留日期前缀（如 `2026-06-29_V0.4.2-未来6周滚动计划.md`），因其本身就是按日期归档的历史快照
- `09_整改项/archive/` 下的归档文件保留原名

**理由**：版本号后缀导致 PM_SESSION/索引文件中的引用频繁失效（每次升级都要删除旧后缀文件）。

### Step 3.5：Bug 诊断强制流程（变更/缺陷模式专用，禁止跳过）

当模式为"变更/缺陷/发布"且涉及 Bug 修复时，**必须**按以下顺序执行，禁止凭代码阅读直接下结论：

1. **完整证据获取**：
   - 测试失败必须用 `--tb=long`（或至少 `--tb=short`）获取完整 traceback
   - **禁止**用 `--tb=no` 隐藏错误详情
   - 必须读取完整的 WARNING/ERROR 日志行，不可只看断言失败信息

2. **诊断脚本先行**：
   - 读代码形成的假设，**必须**用最小诊断脚本（`python -c "..."`）验证后才能下结论
   - 诊断脚本应直接调用被测函数，打印实际返回值
   - 禁止"读了代码 → 推测根因 → 直接输出修复计划"的跳跃

3. **测试问题 vs 生产问题分离**：
   - 测试失败时，**先检查 fixture 是否完整**（项目标志文件、路径结构、mock 配置）
   - 再怀疑生产代码
   - 特别警惕"假通过"：`if cr is not None:` 类条件断言会掩盖 fixture 缺陷

4. **fixture 健康检查**（测试失败时优先排查）：
   - fixture 是否创建了项目标志文件？（PM_SESSION_*.md / .copier-answers.yml / .plc.json）
   - fixture 的 mock 配置是否返回非 None 值？（打印 mock.return_value 确认）
   - 测试中是否有 `if x is not None:` 类条件断言？（改为 `assert x is not None` + `assert x.字段 == 期望值`）
   - 详细的 fixture 健康检查清单见 `fullstack-engineer` 技能"Fixture 健康检查清单"章节

5. **未验证禁止回写**：
   - 诊断结论未经运行时验证，**禁止**写入 PM_SESSION §8/§9
   - 必须标注"已验证"或"待验证"，未验证的结论只能放在 `open_questions`

### Step 3.6：dogfooding 闭环质量门禁（变更/缺陷模式专用）

当走 dogfooding 闭环（CHG-*.md 状态流转到 closed）时，**必须**校验以下质量门禁：

1. **CHG 章节完整性校验**：
   - 12 章节非空：§5 变更前后 / §6.1 五大约束 / §6.2 跨领域 / §6.3 传播链 / §7 实施计划 / §8.1 审批流程 / §8.2 审批结论 / §9 实施记录 / §10.1 验证项清单 / §10.2 跨领域联动验证 / §10.3 验证结论 / §11 版本详细变更说明 / §12 附录
   - **禁止**只填 §10.1/§10.3 就流转到 closed（早期 CHG-001/075 的教训）
   - `change transition` 流转到 closed 前，逐章节检查非空
   - **禁止**用 `--allow-partial-verification` 绕过章节完整性检查
   - 建议在 `change transition` 流转到 closed 前，由 CLI 自动校验 12 章节非空（当前为人工检查，后续 auto-pm 增强后改为自动）

2. **闭环证据完整性**：
   - 代码 commit hash（或明确标注无代码变更）
   - 测试通过数（如 `1477 passed 6 skipped 0 failed`）
   - 静态门禁结果（ruff 0 errors + mypy 0 errors）
   - 真实端到端验证（如 DJ-2026-005 端到端）

3. **状态流转合法性**：
   - 9 步状态流转顺序：`draft → submitted → under_review → approved → implementing → pending_acceptance → accepting → completed → closed`
   - `accepting → closed` **非法**，必须经 `completed`（状态机不允许跳过）
   - `--verification-conclusion` **必须**包含"通过"且**不包含**"不通过"，否则流转到 completed 失败

### Step 3.7：真源一致性前置校验（同步回 PM_SESSION 前必做）

在 Step 4 同步回 PM_SESSION **之前**，必须校验以下一致性，不一致则**禁止**同步：

**首选方式：自动检查（CHG-SCPT-2026-145 新增，强制）**

```powershell
auto-pm -w "<工作空间根>" spec check --check-id SHC-011,SHC-012,SHC-013,SHC-014
```

| 检查器 | 检查项 | 对应人工校验点 |
|--------|--------|----------------|
| SHC-011 | 版本号四件套一致性（pyproject.toml / CHANGELOG.md / PM_SESSION §2·§8） | 第 1 点 |
| SHC-012 | 测试数一致性（PM_SESSION §3 / 实际 pytest 结果） | 第 2 点 |
| SHC-013 | 验证状态标注（§8 Handoff Notes / §9 Next Actions 未验证结论处理） | 第 4、5 点 |
| SHC-014 | 文档索引有效性（§4 Artifacts Index 路径有效 + PRD/INT/DSN/TEC 齐全） | 第 3 点 |

- **ERROR 级问题必须修复后才能同步回 PM_SESSION**；INFO/WARNING 可记录后继续
- 该命令同时会在 `change transition --done`（CHG 闭环门禁）中自动执行 SHC-011 和 SHC-014，详见 Step 3.6
- 若 CLI 不可用或检查器未覆盖项目场景，按以下细则人工校验：

1. **版本号一致性**：
   - `pyproject.toml` 版本号 == `CHANGELOG.md` 最新条目版本号
   - `PM_SESSION §2` Current Focus 中的版本号 == `PM_SESSION §8` Handoff Notes 中的版本号
   - 006 技术债报告 frontmatter `version` == pyproject.toml 版本号

2. **测试数一致性**：
   - `PM_SESSION §3` Status Summary 测试通过数 == 006 技术债报告 §0.2 关键指标 == 实际 `pytest` 结果

3. **文档索引有效性**：
   - `PM_SESSION §4` Artifacts Index 中所有路径实际存在
   - 无带版本号后缀的文件引用（见"文件命名规范"）

4. **验证状态标注**：
   - §8 Handoff Notes 中的诊断结论必须标注 `[已验证]` 或 `[待验证]`
   - §9 Next Actions 中的 precondition 必须明确依赖的验证状态
   - 未验证的结论只能放在 `open_questions`

5. **读取时双向校验**：
   - 读取 PM_SESSION §3/§8 中的声明时，若发现未标注验证状态（`[已验证]`/`[待验证]`），**视为"待验证"**
   - "待验证"的声明**不得作为决策依据**，必须先运行时验证
   - 回写前：必须标注验证状态
   - 读取时：未标注 = 待验证 = 不可作为决策依据

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

**门禁实测后复检（CHG-SCPT-2026-145 新增，强制）**：

门禁实测完成后，必须重新运行 SHC-012 确认 PM_SESSION §3 测试通过数与实际 pytest 结果一致：

```powershell
auto-pm -w "<工作空间根>" spec check --check-id SHC-012
```

- 若 pytest 实际通过数与 PM_SESSION §3 声明不一致，必须先更新 §3 再同步回 PM_SESSION
- 该复检确保 Step 3.8 的实测结果被准确回写，避免"声明 1500 passed，实际 1477 passed"的失真

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

**§5/§6 职责分离**（避免重复记录）:
- §5 change_log = 事件索引（一行摘要 + CHG 编号 + 日期），不记录详情
- §6 Implementation Log = 技术实施详情（changed_files + impact + risks），详情也可只放在 CHG-*.md §9 中，§6 只保留"指向 CHG 编号 + 一句话摘要"

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

### Step 5：执行技能必须返回结构化交接结果

`fullstack-engineer` 和 `plc-electrical-engineer` 结束时必须返回结构化 `handoff_result` 给 `pm-workflow`，至少包含：
- `summary`
- `changed_files`
- `verification`（`lint_result` / `test_result` / `other_checks` / `not_run`）
- `risks`
- `next_actions`（带 `precondition` + `done_when`）
- `watchouts`
- `read_first`
- `artifacts`
- `chg_updates`

`pm-workflow` 收到 `handoff_result` 后，统一回写 PM_SESSION §6-§9，并统一写入 `.auto-pm/ai_feedback.json`。

不允许只改代码不留交接摘要；不允许执行技能直接回写 PM_SESSION；不允许新建独立状态文件替代 PM_SESSION。

## 与其他技能的边界与跨技能切换（强制）

- 本技能负责：需求、PRD、线框方案、任务拆解、迭代变更推进、发布交付
- 软件实现与联调 → `fullstack-engineer`
- PLC 编码与电气文档 → `plc-electrical-engineer`
- 安装外部技能 → `find-skills`

**跨技能切换规则（强制）**：
当 PM 流程推进到需要其他技能执行的阶段时，**必须立即调用目标技能**，不要询问用户是否切换：

| PM 阶段完成 | 下一步属于 | 必须调用 |
|-------------|-----------|---------|
| 需求澄清完成，进入技术方案 | PLC 域 | `Skill: plc-electrical-engineer` |
| 需求澄清完成，进入技术方案 | 软件域 | `Skill: fullstack-engineer` |
| PRD/拆解完成，进入编码 | PLC 域 | `Skill: plc-electrical-engineer` |
| PRD/拆解完成，进入编码 | 软件域 | `Skill: fullstack-engineer` |
| 变更/Bug 分析完成，进入修复 | PLC 域 | `Skill: plc-electrical-engineer` |
| 变更/Bug 分析完成，进入修复 | 软件域 | `Skill: fullstack-engineer` |

判断域的规则：
- 项目类型为 `plc` → 默认切换到 `plc-electrical-engineer`
- 项目类型为 `software` → 默认切换到 `fullstack-engineer`
- 跨域项目 → 根据当前任务性质判断

切换前必须：
1. 同步回写 PM_SESSION（Step 4）
2. 在 §8 Handoff Notes 中记录切换原因和目标技能
3. 调用 `Skill: <目标技能名>`

### §8 Handoff Notes 标准化结构

跨技能交接时，§8 Handoff Notes 必须包含以下字段（按优先级排序）：

| 字段 | 说明 | 数量约束 |
|------|------|----------|
| `current_state` | 1-2 句话当前状态 + 版本号 + 关键阻塞 | 1 条 |
| `next_focus` | 下一步行动，带 precondition + done_when | ≤5 条 |
| `skill_handoff` | 切换原因 + 目标技能 + 起手任务 + 关键约束 | **严格 1 条**（最新） |
| `skill_handoff_archived` | 早期交接记录归档到 `06_PM_SESSION历史/`（见 Step 4.5） | 历史目录 |
| `watchouts` | 分类管理（测试约束 / 代码约束 / 流程约束 / 环境约束） | 每类 ≤5 条 |
| `read_first` | 文件路径，按优先级排序 | ≤5 个 |

**禁止**：
- §8 中存在未标注验证状态的诊断结论
- watchouts 列表膨胀超过 20 条未分类
- 新建独立状态文件替代 PM_SESSION
- §8 skill_handoff 保留超过 1 条（早期必须归档到历史目录，不保留在主文件）

## 成功标准

- 同一项目沿 PM_SESSION 持续推进，不用反复重建上下文
- 下次会话通过 PM_SESSION 快速恢复当前项目状态
- 需求→线框→拆解→推进→变更→发布形成统一闭环
