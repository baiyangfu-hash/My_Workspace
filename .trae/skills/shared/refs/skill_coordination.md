# 技能协同通用规则（pm-workflow / fullstack-engineer / plc-electrical-engineer 共享）

> **来源**：CHG-SCPT-2026-152（2026-07-31）。本文件是三技能跨技能公共契约的单一真源；`fullstack-engineer` 与 `plc-electrical-engineer` 仅保留各自领域附加规则。

## 0. 跨技能公共契约（CHG-SCPT-2026-152 升级版）

### 0.1 职责边界

1. **`pm-workflow` 是唯一落账 owner**：
   - 唯一负责读取并回写 `PM_SESSION_<项目编号>.md`
   - 唯一负责写入 cockpit 反馈文件 `.auto-pm/ai_feedback.json`
   - 唯一负责把执行结果整理进 PM_SESSION §6-§9 / §8 skill_handoff / §9 next actions
   - **唯一负责维护 Obsidian 全局规范仓库（`00_Obsidian_Base全局规范文件仓库/`）**：凡增删改规范文件，必须同步更新 `spec_registry.json`，并自动触发运行 `auto-pm spec index`（自动重新生成 `00_INDEX_全局规范索引.md`）与 `auto-pm spec check`，确保全局索引即时联动。

2. **`fullstack-engineer` / `plc-electrical-engineer` 支持预研与执行双模式**：
   - **预研模式 (`mode: grooming`)**：接收 `skill_context`，只读检索项目代码库与规范，提取变量/逻辑/接口/约束事实，返回结构化 `handoff_result` 事实摘要，严禁修改业务代码；
   - **执行模式 (`mode: execution`)**：接收 `skill_context`，执行代码填空、文档、测试、门禁自检，返回全绿 `handoff_result`；
   - 结束时**只**向 `pm-workflow` 返回结构化 `handoff_result`；
   - **不得**直接回写 `PM_SESSION`；
   - **不得**直接写入 `.auto-pm/ai_feedback.json`。

3. **强制协同铁律（澄清-报批-执行-验收 四阶段）**：
   - **阶段 0【需求澄清与代码基优先门禁 (Codebase-First Gating)】**：
     - **严禁代码盲问 (Zero-Stupid-Questions Redline)**：严禁在未检索代码库的情况下直接向用户提问。任何可在项目源码、配置文件（`.plc.json` / `pyproject.toml`）、接口文档（`INT.md` / `VAR.md`）、数据结构（DTO / UDT）或规范库中读取到的参数、变量名、调用关系与目录路径，**绝对禁止向用户发问**；
     - **二分法处理原则 (Greenfield vs Brownfield)**：
       - **全新建仓 (Greenfield)**：审查 CAD/轴系/动作时序 3 要素。若缺失，先检索 Obsidian 规范库与模板库；仍缺失物理硬件事实时方可向用户提问；
       - **在研迭代/缺陷变更 (Brownfield)**：**强制执行代码基逆向与上下文探路 (Codebase Reconnaissance)**。PM 必须优先调用工具（`grep_search` / `find_by_name` / `view_file`）或派发 Grooming 预研子代理（`python -m auto_pm handoff --to <plc|fullstack> --pid <PID> --mode grooming`）勘测已有逻辑；
     - **有效提问门槛**：只有当代码库探路完毕，且发现涉及无法推导的真实业务决策抉择（Trade-off）、新增未接线硬件定义或客户冲突诉求时，方可发起《高质量澄清提问清单》；
   - **阶段 1【报批】**：PM 角色输出《需求分析与技术实施计划》（含 HTML 交互原型与架构设计），由 Copier 脚手架就绪 `TEC.md`/`USAGE.md` 文档骨架，**必须显式停下来等待用户审批确认**；
   - **阶段 2【执行】**：只有在用户明确批准后，方可派发给执行技能（PLC / 全栈）修改代码与测试。**严禁在对话框要求或输出长篇说明书草稿**，所有非功能性文档直接在物理文件中填空；
   - **阶段 3【验收】**：必须运行驾驶舱静态门禁（`auto-pm plc check` / `auto-pm doc check [--strict]` / `pytest`），门禁全绿后呈报交付清单由用户最终验收结项。

4. **AI 工程师主动担当与零负担法则边界**：
   - AI 必须独立消化全部代码编写、语法白名单、死链扫描、自动化测试与 `doc check` 注释率/文档完整性校验的重体力活；
   - **严禁借“主动提问”推卸代码调研责任**：专业系统工程师的第一职责是**自己阅读代码与工程资产**。严禁借“主动提问”之名掩盖偷懒不读代码的行为。只有在彻底查阅代码库后仍存在不可推断的物理/业务边界时，向用户发起的提问才具有专业担当！

5. **独立触发降级路径**：
   - 若执行技能被用户独立触发，可读取 PM_SESSION 恢复上下文
   - 结束时写入同一份临时交接包 `.auto-pm/handoffs/<request_id>.json`
   - 需要落账时，转由 `pm-workflow` 统一消费并回写；不得新建平行状态文件替代 PM_SESSION

### 0.2 三类数据边界

| 数据 | 路径 | 写入者 | 用途 |
|------|------|--------|------|
| 项目事实源 | `PM_SESSION_<项目编号>.md` | `pm-workflow` | 项目状态、决策、执行与验证记录 |
| 当前操作上下文 | `.auto-pm/ai_context.json` | cockpit / `pm-workflow` | 传递 request_id、入口模式、页面、意图与建议技能 |
| 临时交接包 | `.auto-pm/handoffs/<request_id>.json` | `fullstack-engineer` / `plc-electrical-engineer` | 提交给 PM 收口的一次性执行结果 |

交接包是一次性消息，不是第二套项目账本。`pm-workflow` 成功处理后，再把结果写回 `PM_SESSION` 与 `.auto-pm/ai_feedback.json`。
