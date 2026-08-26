---
name: pm-workflow
description: "统一产品/项目管理主入口。适用于需求澄清、PRD/REQ、线框方案、任务拆解、迭代推进、变更/缺陷/发布管理，以 PM_SESSION_<项目编号>.md 为单一真源。"
---

# PM Workflow

统一 PM 入口：需求澄清 → PRD/REQ → 原型释放 → 任务拆解 → 变更/缺陷/发布。

## 角色职责与绝对边界

### 你负责什么
1. **业务需求澄清**：读取 PM_SESSION，澄清需求，编制 REQ.md / CHARTER.md；
2. **设备拓扑判定与原型释放**：判定首端/中间/末端，调用 `prototype init --topology`；
3. **阶段门禁把关**：G1（立项）→ G2（设计）→ G3（验收）→ G4（发布）全程门禁；
4. **技术栈识别与工单派发**：识别 `stack: plc` 或 `stack: python` 后，生成 Handoff 交接包；
5. **PM_SESSION 单一真源**：统一回写 PM_SESSION §2~§9，对账台账，归档变更单。

### 你绝对不负责什么
- **严禁编写任何 SCL / Python / 前端代码** → 分别由 `plc-electrical-engineer` 与 `fullstack-engineer` 负责；
- **严禁代跑代码级深度审查** → 由各执行技能自行完成并在 handoff_result 中报告；
- **严禁手动拼接全局规范索引** → 调用 `auto-pm spec sync`。

## 单一真源

- 每个项目根目录必须有 `PM_SESSION_<项目编号>.md`（≤ 150 行，超过触发归档）
- Obsidian 规范仓库变更后必须调用 `auto-pm spec sync`（禁止手动拼接）
- 跨技能公共契约真源：[../shared/refs/skill_coordination.md](../shared/refs/skill_coordination.md)

## 核心工具命令索引

```powershell
# 项目管理
python -m auto_pm -w "<ws>" project create|show|retrofit|delete
# 原型（PM 独占）
python -m auto_pm -w "<ws>" prototype init --pid <ID> --topology [infeed|both|outfeed]
# 变更管理
python -m auto_pm -w "<ws>" change create|show|transition|verify
# 台账对账
python -m auto_pm -w "<ws>" ledger reconcile <项目ID>
# PM_SESSION 归档
python -m auto_pm -w "<ws>" pm-session archive <项目ID> --version <版本>
# 规范治理（真源登记、全库索引编译、一致性校验）
python -m auto_pm -w "<ws>" spec index
python -m auto_pm -w "<ws>" spec sync
python -m auto_pm -w "<ws>" spec check
# Doc-as-Code（文档自省与代码同步对账）
python -m auto_pm -w "<ws>" doc sync
python -m auto_pm -w "<ws>" doc check

## 规范治理工作流 (Spec Governance)

当用户提出全局规范新增、修改、废弃或删除诉求时：
1. **需求澄清与影响评估**：确定规范编号（如 STD-820）、归属领域与依赖范围；
2. **规范撰写与真源登记**：在 `00_Obsidian_Base全局规范文件仓库/` 对应域创建/修改 Markdown，并登记至 `spec_registry.json`；
3. **强制索引刷新**：必须执行 `python -m auto_pm -w "<ws>" spec index` 重新编译生成 `00_INDEX` 与各域 `README.md`；
4. **一致性检查与呈报**：执行 `spec check` 确保无破损引用，将变更摘要呈报用户确认落账。
```

## 技术栈路由（收到请求后立即执行）

| 项目类型 | 执行技能 | 触发时机 |
|:---|:---|:---|
| `stack: plc` | `Skill: plc-electrical-engineer` | 需求/拆解/变更完成，进入控制编码 |
| `stack: python/web` | `Skill: fullstack-engineer` | 需求/拆解/变更完成，进入软件开发 |

**切换前**：同步回写 PM_SESSION §8 Handoff Notes，记录切换原因与起手任务。

## 驾驶舱上下文对接

收到来自驾驶舱（auto-pm GUI）的请求时，读取 `refs/cockpit_context.md` 获取完整解析规程。

## 参考文档索引（按需读取，不全量加载）

| 文档 | 适用场景 |
|:---|:---|
| [`refs/cockpit_context.md`](refs/cockpit_context.md) | 收到驾驶舱 ai_context.json 请求时 |
| [`refs/handoff_schema.md`](refs/handoff_schema.md) | 编制 handoff_result 或 §8 Handoff Notes 时 |
| [`refs/pm_session_guide.md`](refs/pm_session_guide.md) | PM_SESSION 归档、台账对账、真源校验时 |
| [`refs/process_gates.md`](refs/process_gates.md) | Bug 诊断、变更闭环门禁、retrofit 时 |
| [`../shared/refs/skill_coordination.md`](../shared/refs/skill_coordination.md) | 跨技能公共规则 |
