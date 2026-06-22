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

### Step 4：同步回 PM_SESSION

每次事件处理完更新：`current_focus`、`status_summary`、`artifacts_index`、对应日志（change/iteration/bug/refactor/release/spec_change）、`open_questions`。只追加，不覆盖历史。

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

## 成功标准

- 同一项目沿 PM_SESSION 持续推进，不用反复重建上下文
- 下次会话通过 PM_SESSION 快速恢复当前项目状态
- 需求→线框→拆解→推进→变更→发布形成统一闭环
