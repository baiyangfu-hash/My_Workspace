# SW-2026-008 WBS8 handoff 工作队列验收矩阵

## 1. 验收范围

- 工作包：WBS8 中风险 Dogfood
- 目标：为驾驶舱提供只读 handoff 工作队列快照
- 运行真源：`00_Infrastructure/auto_pm`
- 稳定基线：`b603bd4`
- 合并提交：`f73f5eb`
- 交接请求：`AI-20260902-WBS8`
- 变更单：`CHG-SCPT-2026-169`

## 2. 实现内容

| 层级 | 交付内容 | 只读边界 |
|---|---|---|
| 服务层 | `AiHandoffService.queue_snapshot` 聚合固定生命周期状态、失败事件和最近请求 | 只读 `.auto-pm/handoffs` 与失败证据，不消费、不写回 |
| CLI 层 | `handoff queue` 支持项目过滤、最近请求数量限制和 JSON 输出 | 不改变任何 handoff 状态 |
| 测试层 | 覆盖 pending/consumed 统计、限制数量和查询后状态保持 | 使用临时目录，不污染工作空间运行态 |

## 3. 双钥匙验证

| 验证项 | 结果 | 证据 |
|---|---|---|
| 候选 handoff 测试 | 通过 | `5 passed` |
| 候选 Ruff | 通过 | `All checks passed` |
| 候选 Mypy | 通过 | `Success: no issues found in 2 source files` |
| 差异格式检查 | 通过 | `git diff --check` |
| 稳定版外部隔离复核 | 通过 | `passed=true`；候选 3 文件均在基础设施白名单内 |
| 稳定基线清洁 | 通过 | stable `working_tree_clean=true` |
| 运行态污染检查 | 通过 | `candidate_runtime_changes=[]` |
| 变更台账对账 | 通过 | `change verify SW-2026-008 --ledger-check` |

## 4. PM 收口

- `CHG-SCPT-2026-169` 已按 `draft → submitted → under_review → approved → implementing → pending_acceptance → accepting → completed → closed` 完成流转。
- 变更单明确本批不涉及 PLC、HMI、真实硬件和跨域接口。
- 旧 `SW-2026-008` 母体未被删除，继续作为历史文档和回退参考。
- `DJ-2026-005` 未被修改；真实 PLC、HMI、TIA、GX 和现场部署仍属于外部验证边界。

## 5. 结论

WBS8 验收通过。驾驶舱已具备第二批真实 Dogfood 的只读队列观察能力；稳定版和候选版隔离有效，PM 变更、台账和治理记录闭环。下一步进入 WBS9，评估旧母体代码回退的单轨退出条件，不自动删除回退路径。
