# handoff_schema.md — 交接结构规范

> 本文档是 pm-workflow / 执行技能的按需参考文档。

变更单编号格式：`CHG-{DOMAIN}-{YYYY}-{XXX}`（DOMAIN ∈ ELEC/MECH/PLC/HMI/SCPT/DOCU/SAFE）。

## 1. handoff_result 结构（执行技能返回给 PM 的标准结构）

```json
{
  "request_id": "AI-20260821-001",
  "executor_skill": "plc-electrical-engineer",
  "summary": "完成了 FB_1002 SCL 状态机重写与 plc check 全绿",
  "changed_files": ["02_PLC程序/PLC_ST/02_叠垛移载机械手/FB_1002.scl"],
  "verification": {
    "lint_result": "auto-pm plc check Pass=43 Warn=1 Fail=0",
    "test_result": "静态规范自检通过",
    "other_checks": [],
    "not_run": ["TIA Portal 实机编译（无硬件环境）"]
  },
  "risks": ["SCL 需现场 PLCSIM 编译验证"],
  "next_actions": [
    {
      "action": "TIA Portal 编译验证",
      "precondition": "具备现场 S7-1500 或 PLCSIM 环境",
      "done_when": "编译 0 error 0 warning"
    }
  ],
  "watchouts": ["FB_1002 VAR_IN_OUT 结构体版本须与 OB1 调用处保持一致"],
  "read_first": ["02_PLC程序/程序文档/PLC变量定义文档_VAR.md"],
  "chg_updates": "CHG-PLC-2026-001 已更新至 implementing 状态",
  "product_impact": {
    "hypothesis_id": "HYP-001",
    "impact_type": "safety_and_yield",
    "engineering_signal": "在 FB_1002 中增加了安全区极性校验，防止伺服在气缸未退回时提前使能",
    "verification_mode": "physical_hardware",
    "validation_stage": "现场上电打样时观测",
    "needs_user_validation": true
  },
  "pm_closure": "请 PM 执行 ledger reconcile 完成台账对账"
}
```

## 2. §8 Handoff Notes 标准字段（PM_SESSION 中）

| 字段 | 说明 | 数量约束 |
|:---|:---|:---:|
| `current_state` | 1-2 句话 + 版本号 + 关键阻塞 | 1 条 |
| `next_focus` | 下一步行动，带 precondition + done_when | ≤ 5 条 |
| `skill_handoff` | 切换原因 + 目标技能 + 起手任务 | 严格 1 条（最新） |
| `watchouts` | 分类管理（测试/代码/流程/环境约束） | 每类 ≤ 5 条 |
| `read_first` | 文件路径，按优先级排序 | ≤ 5 个 |

**禁止**：
- §8 中存在未标注 `[已验证]` / `[待验证]` 的诊断结论
- `skill_handoff` 保留超过 1 条（早期归档到历史目录）
- watchouts 总数超过 20 条未分类
