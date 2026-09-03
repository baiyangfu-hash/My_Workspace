# cockpit_context.md — 驾驶舱上下文对接规程

> 本文档是 pm-workflow 的按需参考文档，仅在收到驾驶舱（auto-pm GUI/CLI）请求时读取。

## 1. ai_context.json 读取规则

当 `<工作空间根>/.auto-pm/ai_context.json` 存在时：

1. 提取字段：`request_id`、`entry_mode`、`intent`、`target_skill`、`active_project`、`active_change`、`active_page`、`product_context`
2. `entry_mode` 仅允许：`cockpit` / `pm` / `direct`
3. `active_page` 推断模式：
   - `changeCenter` → 变更/缺陷/发布模式
   - `workspace` → 项目推进模式
   - `specCenter` → 规范模式
4. 跳过 Step 0（venv/project show/PM_SESSION 读取）和 Step 1（模式选择）
5. 若 `intent == "close_handoff"`，先消费 `.auto-pm/handoffs/<request_id>.json`，由 pm-workflow 统一落账

当用户直接从已有项目恢复工作、且没有有效 cockpit 请求时：

1. 必须先运行 `auto_pm pm resume <PID> --json`；`pm-resume.v1` 是冷启动索引，不是第二套台账。
2. 只读取 `read_set`；`expansion_triggers` 未命中时不得全仓搜索或打开模型专用交接文档。
3. 方案和 handoff 必须保留 `evidence_id`；事实变更时重新 resume。

## 2. 技能路由规则

| 条件 | 派发目标 |
|:---|:---|
| `target_skill == "plc-electrical-engineer"` 或 `domain == "PLC"` | `Skill: plc-electrical-engineer` |
| `target_skill == "fullstack-engineer"` 或 `domain == "SCPT"/"PYTHON"` | `Skill: fullstack-engineer` |
| 其他需求/变更/发布类 | pm-workflow 自行处理 |

## 2.1 Intent 与 PM 剧本对应表

| intent 值 | PM 应执行的剧本 |
|:---|:---|
| `initiate_project` | 阶段0门禁：核查3必备要素。若缺失，**严禁直接提问**，必须先检索 Obsidian 规范库（`00_Obsidian_Base全局规范文件仓库`）**与目标项目代码基 (Codebase)**。若查到标准或代码事实则直接套用；若查不到且确实缺失物理硬件事实时方可向用户发起《需求澄清提问清单》 |
| `plan_documents`   | 由 Copier 脚手架模板初始化 6 件套骨架 → 针对性填空 → doc check 校验通过 → 呈报用户审批 |
| `spec_check`       | 进入规范治理模式：执行规范巡检/索引/同步相关剧本，按 `specCenter` 上下文优先处理 Obsidian 真源与注册表一致性 |
| `implement_change` | 阶段0探路：**代码基优先 (Codebase First)**。通过工具直接检索代码或派发 Grooming 预研子代理（`--mode grooming`）获取受影响文件与符号事实；严禁向用户询问代码中已有的参数；基于事实输出变更计划等待审批 |
| `plc_review`       | 已有流程：PLC 项目推进（不变） |
| `project_followup` | 已有流程：默认兜底（不变） |

## 3. skill_context 传递结构（传给子技能的标准 JSON）

```json
{
  "source": "pm-workflow",
  "request_id": "AI-20260821-001",
  "project_id": "DJ-2026-009",
  "stack": "plc",
  "change_number": "CHG-PLC-2026-001",
  "change_domain": "PLC",
  "change_nature": "DEF",
  "mode": "变更/缺陷/发布",
  "pm_summary": "上下文已通过 cockpit AI 辅助恢复，跳过项目识别。"
}
```

## 4. 子技能返回处理

1. 解析子技能返回的 `handoff_result`（见 `refs/handoff_schema.md`）
2. 由 pm-workflow 统一回写 PM_SESSION §6-§9
3. 写入 `.auto-pm/ai_feedback.json`
