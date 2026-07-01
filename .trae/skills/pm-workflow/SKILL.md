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

## 工具依赖

```powershell
# auto-pm：项目初始化、补完、健康检查、类型检测
auto-pm -w "<工作空间根>" project create|show|edit|retrofit|delete ... [--stack <plc|python>] [--id <编号>] [--name <名称>]
auto-pm -w "<工作空间根>" plc init|check|repair|standardize ...

# SpecMgr：规范健康检查
specmgr -w "<工作空间根>" check|index|frontmatter|report
```

- `-w` 必须放在子命令之前
- `project show` 自动通过多信号判据识别项目类型
- `project retrofit` 仅添加 hooks/handoffs/Spec Snapshot，不修改现有文件

> 注意：pm-mgr（SW-2026-007）已被auto-pm（SW-2026-008）取代。pm-mgr命令仍可用但不再维护，建议所有新项目使用auto-pm。

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

### Step 1：判定本轮模式（必须用 AskUserQuestion 呈现选项）

| 模式 | 用途 |
|------|------|
| 需求 | 新需求、需求澄清、范围界定 |
| PRD | PRD/REQ/需求规格说明书 |
| 方案/线框 | 页面结构、交互流、状态覆盖、原型说明 |
| 拆解 | Epic/Feature/Story/Test、里程碑、依赖 |
| 项目推进 | 迭代规划、里程碑推进、状态同步 |
| 变更/缺陷/发布 | 变更单、Bug、发布准备、交付清单 |
| 规范 | 规范引用/升级/漂移检查 |
| 项目初始化 | 空文件夹 → 完整项目骨架 |
| 旧项目补完 | 已有项目注入连续性机制（hooks+handoffs+Spec Snapshot）|

### Step 2：最小提问（每模式 2-3 个高价值问题）

- **需求**：为什么现在做？解决谁的问题？成功标准？
- **PRD**：给谁看？MVP 边界？哪些明确不做？
- **方案**：低保真还是可点击原型？覆盖哪些页面/状态？
- **拆解**：拆到什么级别？是否带优先级/依赖？是否同步 GitHub？
- **变更/Bug**：触发原因？影响范围？哪些行为不能被破坏？
- **初始化**：项目类型？编号？一句话定位？

### Step 3：按模式产出

| 模式 | 最少产出 |
|------|---------|
| 需求 | 问题定义、用户/角色、业务价值、成功指标、非目标、风险 |
| PRD | Executive Summary、Problem/Solution、Personas、Stories、Acceptance Criteria、Non-Goals、Technical Constraints |
| 方案 | 页面清单、主流程、状态覆盖（空/错/加载/权限）、差异说明 |
| 拆解 | Epic→Feature→Story→Test、优先级、依赖、DoR/DoD；结果必须写入 `01_项目文档/03_执行过程/` 并更新 PM_SESSION §4 |
| 变更/Bug | 触发原因、影响范围、回归清单、验收清单 |
| 初始化 | 调用 `auto-pm project create` 自动生成目录结构+文档模板+hooks+handoffs+Spec Snapshot |
| 补完 | 调用 `auto-pm project retrofit` 注入 hooks+handoffs+Spec Snapshot（不修改现有文件） |

### 文件命名规范（强制）

项目文档文件名（.md/.html 等）**禁止**追加版本号后缀：

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

4. **未验证禁止回写**：
   - 诊断结论未经运行时验证，**禁止**写入 PM_SESSION §8/§9
   - 必须标注"已验证"或"待验证"，未验证的结论只能放在 `open_questions`

### Step 3.6：dogfooding 闭环质量门禁（变更/缺陷模式专用）

当走 dogfooding 闭环（CHG-*.md 状态流转到 closed）时，**必须**校验以下质量门禁：

1. **CHG 章节完整性校验**：
   - 12 章节非空：§5 变更前后 / §6.1 五大约束 / §6.2 跨领域 / §6.3 传播链 / §7 实施计划 / §8.1 审批流程 / §8.2 审批结论 / §9 实施记录 / §10.1 验证项清单 / §10.2 跨领域联动验证 / §10.3 验证结论 / §11 版本详细变更说明 / §12 附录
   - **禁止**只填 §10.1/§10.3 就流转到 closed（早期 CHG-001/075 的教训）
   - `change transition` 流转到 closed 前，逐章节检查非空

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

### Step 4：同步回 PM_SESSION

每次事件处理完更新：`current_focus`、`status_summary`、`artifacts_index`、对应日志（change/iteration/bug/refactor/release/spec_change）、`open_questions`。只追加，不覆盖历史。

### Step 4.5：PM_SESSION 间歇精简触发规则（防膨胀）

PM_SESSION 随迭代推进持续膨胀，需定期精简以保持可读性：

| 章节 | 触发阈值 | 精简方式 |
|------|----------|----------|
| §5 change_log | 条目数 > 40 | 折叠早期已完成里程碑记录为摘要（每条摘要末尾标注"详情见 §3 Status Summary 第 N 行"） |
| §3 Status Summary completed | 条目数 > 30 | 早期里程碑折叠为摘要，详情指向 §5 或技术债报告 |
| §6 Implementation Log | 条目数 > 20 | 早期记录折叠为摘要 |
| §8 skill_handoff | 条目数 > 3 | 超过 3 条的早期 skill_handoff 标记为 `skill_handoff_archived`（保留为历史参考，从主交接包移除） |

**精简原则**：
- 只折叠已完成里程碑，不删除信息源
- 保留最新 2 个迭代的完整记录
- 精简后必须验证：§4 Artifacts Index 路径有效性 + §2/§8 版本号一致性

### Step 5：执行技能必须回写 PM_SESSION

`fullstack-engineer` 和 `plc-electrical-engineer` 结束时必须在 PM_SESSION 中回写 §6-§9：
- **§6 Implementation Log**：日期、skill、mode、goal、changed_files、impact、risks
- **§7 Verification Log**：verified、not_verified、method、blocker
- **§8 Handoff Notes**：current_state、next_focus、watchouts、read_first
- **§9 Next Actions**：≥3 条，带 precondition + done_when

不允许只改代码不留交接摘要；不允许新建独立状态文件替代 PM_SESSION。

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
| `skill_handoff`（最新 1 条） | 切换原因 + 目标技能 + 起手任务 + 关键约束 | 1 条 |
| `skill_handoff_archived` | 超过 3 条的早期交接记录归档 | 保留为历史参考 |
| `watchouts` | 分类管理（测试约束 / 代码约束 / 流程约束 / 环境约束） | 每类 ≤5 条 |
| `read_first` | 文件路径，按优先级排序 | ≤5 个 |

**禁止**：
- §8 中存在未标注验证状态的诊断结论
- watchouts 列表膨胀超过 20 条未分类
- 新建独立状态文件替代 PM_SESSION

## 成功标准

- 同一项目沿 PM_SESSION 持续推进，不用反复重建上下文
- 下次会话通过 PM_SESSION 快速恢复当前项目状态
- 需求→线框→拆解→推进→变更→发布形成统一闭环
