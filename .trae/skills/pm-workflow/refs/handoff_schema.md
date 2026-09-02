# handoff_schema.md - handoff.v1 交接结构规范

> 本文档是 pm-workflow 与执行技能之间的交接参考。交接包是一次性消息，不是第二套项目账本。

变更单编号格式：`CHG-{DOMAIN}-{YYYY}-{XXX}`（DOMAIN ∈ ELEC/MECH/PLC/HMI/SCPT/DOCU/SAFE）。

## 1. 生命周期与文件

- 请求文件：`.auto-pm/handoffs/<request_id>.json`
- 结果可以通过 `--result-file` 提供给 `handoff close`，也可以由 PM 组装为关闭结果。
- 状态：`pending` -> `consumed`；`in_progress`、`completed`、`failed` 仅用于执行侧过程状态。
- `request_id` 是安全文件名和幂等定位键，禁止使用路径穿越字符。
- PM 消费成功后，才允许把结果回写 `PM_SESSION`、`.auto-pm/ai_feedback.json`、变更单和台账。

## 2. 请求与结果结构

```json
{
  "schema_version": "handoff.v1",
  "request_id": "AI-20260901-001",
  "project_id": "DJ-2026-005",
  "executor_skill": "plc-electrical-engineer",
  "summary": "完成 PLC 静态规范检查",
  "status": "pending",
  "mode": "execution",
  "goal": "说明目标和验收边界",
  "skill_context": {
    "injected_specs": ["LSP-905", "STD-840"],
    "baseline_documents": ["TEC.md", "VAR.md"]
  },
  "changed_files": [],
  "verification": {
    "lint_result": "auto-pm plc check PASS",
    "test_result": "pytest PASS",
    "other_checks": [],
    "not_run": ["TIA Portal 实机编译（无硬件环境）"]
  },
  "risks": [],
  "next_actions": [],
  "watchouts": [],
  "read_first": ["TEC.md"],
  "artifacts": [],
  "chg_updates": ["CHG-PLC-2026-001: verified"],
  "product_impact": {
    "hypothesis_id": "HYP-001",
    "impact_type": "safety_and_yield",
    "engineering_signal": "具体的可观测工程信号",
    "verification_mode": "code_static",
    "validation_stage": "静态验收",
    "needs_user_validation": true
  },
  "pm_closure": {
    "required": true,
    "suggested_event": "iteration",
    "suggested_status": "pending_review"
  }
}
```

## 3. 关闭门禁

`handoff close` 必须满足：

1. `summary` 非空。
2. `verification.lint_result`、`verification.test_result`、`verification.other_checks` 或 `artifacts` 至少一项有实际证据。
3. `changed_files` 非空时，`chg_updates` 也必须非空。
4. 相同幂等键和相同结果重复关闭返回原记录；不同结果禁止覆盖已消费记录。

## 4. PM_SESSION §8 字段

| 字段 | 说明 | 数量约束 |
|:---|:---|:---:|
| `current_state` | 1-2 句话 + 版本号 + 关键阻塞 | 1 条 |
| `next_focus` | 下一步行动，带 precondition + done_when | <= 5 条 |
| `skill_handoff` | 切换原因 + 目标技能 + 起手任务 | 严格 1 条（最新） |
| `watchouts` | 分类管理（测试/代码/流程/环境约束） | 每类 <= 5 条 |
| `read_first` | 文件路径，按优先级排序 | <= 5 个 |

禁止在 PM_SESSION §8 保留未标注 `[已验证]` / `[待验证]` 的诊断结论，或堆积历史 `skill_handoff`。
