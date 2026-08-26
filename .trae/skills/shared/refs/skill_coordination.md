# 技能协同通用规则（pm-workflow / fullstack-engineer / plc-electrical-engineer 共享）

> **来源**：CHG-SCPT-2026-152（2026-07-31）。本文件是三技能跨技能公共契约的单一真源；`fullstack-engineer` 与 `plc-electrical-engineer` 仅保留各自领域附加规则。

## 0. 跨技能公共契约（CHG-SCPT-2026-152 升级版）

### 0.1 职责边界

1. **`pm-workflow` 是唯一落账 owner**：
   - 唯一负责读取并回写 `PM_SESSION_<项目编号>.md`
   - 唯一负责写入 cockpit 反馈文件 `.auto-pm/ai_feedback.json`
   - 唯一负责把执行结果整理进 PM_SESSION §6-§9 / §8 skill_handoff / §9 next actions
   - **唯一负责维护 Obsidian 全局规范仓库（`00_Obsidian_Base全局规范文件仓库/`）**：凡增删改规范文件，必须同步更新 `spec_registry.json`，并自动触发运行 `auto-pm spec index`（自动重新生成 `00_INDEX_全局规范索引.md`）与 `auto-pm spec check`，确保全局索引即时联动。

2. **`fullstack-engineer` / `plc-electrical-engineer` 是纯执行者**：
   - 接收 `pm-workflow` 下发的 `skill_context`
   - 执行代码、文档、测试、CHG 等本领域工作
   - 结束时**只**向 `pm-workflow` 返回结构化 `handoff_result`
   - **不得**直接回写 `PM_SESSION`
   - **不得**直接写入 `.auto-pm/ai_feedback.json`

3. **强制协同铁律（澄清-报批-执行-验收 四阶段）**：
   - **阶段 0【需求澄清与输入门禁】**：新项目或重大变更起手时，PM 必须先审查输入。若缺少 **机械CAD/3D/实机图、轴系动力源、动作工艺时序** 之一，**严禁脑补出计划，必须先向用户发起《需求澄清提问清单》**；澄清完毕方可进入阶段 1；
   - **阶段 1【报批】**：PM 角色输出《需求分析与技术实施计划》（含 HTML 交互原型与架构设计），**必须显式停下来等待用户审批确认**；
   - **阶段 2【执行】**：只有在用户明确批准后，方可派发给执行技能（PLC / 全栈）修改代码与测试；
   - **阶段 3【验收】**：运行驾驶舱静态门禁（`auto-pm check` / `doc check` / `pytest`），呈报交付清单由用户最终验收结项。

4. **AI 工程师主动担当与零负担法则边界**：
   - AI 必须独立消化全部代码语法、死链扫描、自动化测试与门禁验证的重体力活；
   - **严禁借“零负担”之名在业务与物理事实不清时擅自硬猜**。前置主动提问是专业工程师的底线担当！

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
