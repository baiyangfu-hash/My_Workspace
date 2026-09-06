# MATRIX-SW008-P0-001：基础设施位与研发母体差异回收方案

> 状态：**ARCHITECTURE APPROVED / RECOVERY EXECUTION PENDING USER APPROVAL**
> 快照基准：分支 `feature/trae-pro-20260509`；HEAD `1b53f38993be6322732d711fac135c64db6a3976`
> PM 恢复证据：`RESUME-8A40C46458D08312` / `FACT-CA141A67B032FDFA`
> 本表是治理候选稿，不是复制、提交、删除或发布授权。

## 1. 判定规则

母体是唯一目标真源；基础设施位仅作为候选证据来源。任何文件回收都必须经过逐文件哈希、来源 Commit/CHG、依赖检查、母体测试、静态门禁及 User 批准。不得根据本表自动复制、格式化、删除、暂存或提交。

| 状态 | 含义 |
| --- | --- |
| `PENDING_REVIEW` | 已识别，等待独立审查与逐文件验证。 |
| `BLOCKED` | 存在门禁、证据或环境阻塞。 |
| `BLOCKED_DEC_CONFLICT` | 关联 DEC 的索引与工作树冲突，等待 User 裁决。 |
| `HISTORICAL_ONLY` | 只作历史证据，不参与当前回收。 |
| `DO_NOT_RECOVER` | 明确不回收；任何清理另需独立申请。 |

## 2. 当前 Git 事实

| 项目 | 当前事实 | 处置 |
| --- | --- | --- |
| 暂存区 | 26 个文件 | `BLOCKED`：格式门禁未通过。 |
| 工作树 | 4 个未跟踪规划文件 | `PENDING_REVIEW`：本轮草案尚未纳入版本控制。 |
| WBS-2 证据 | 成功恢复锚点与 `.incomplete` 失败证据均存在 | 保留现场，不自动清理。 |
| 决策证据 | `DEC-20260904-3362BFFF.json` 声称批准 CHG-177，但法证批准原文仅授权 WBS-2 | `BLOCKED_DEC_SEMANTIC_CONFLICT`：保留旧证据，只能用新 disposition/supersession 纠偏。 |
| Mypy | 2 个 `no-any-return` 错误 | `BLOCKED`。 |
| 暂存差异检查 | `git diff --cached --check` 失败 | `BLOCKED`。 |

## 3. 已知待审候选

| CHG | 基础设施候选文件 | 母体目标 | 当前状态 | 最低验证 |
| --- | --- | --- | --- | --- |
| CHG-174 | `auto_pm/application/core/change_transaction.py`；`tests/application/test_change_transaction.py` | 母体对应相对路径 | `PENDING_REVIEW` | SHA-256、来源、针对性测试、Ruff、Mypy。 |
| CHG-175 | `auto_pm/application/core/workflow_orchestrator.py`；`tests/application/test_workflow_orchestrator.py` | 母体对应相对路径 | `PENDING_REVIEW` | SHA-256、来源、计划路径测试、Ruff、Mypy。 |
| CHG-176 | `auto_pm/application/core/workflow_orchestrator.py`；`tests/application/test_workflow_orchestrator.py` | 母体对应相对路径 | `PENDING_REVIEW` | SHA-256、来源、执行路径测试、Ruff、Mypy。 |
| CHG-177 | `project_archive_service.py`、`project_scanner.py`、`project_service.py`、`ui/cli/project.py` 及对应测试 | 母体对应相对路径 | `BLOCKED_DEC_SEMANTIC_CONFLICT` | 隔离候选；必须新建 CHG/DEC，不复用 DEC-3362BFFF。 |

CHG 与 DEC 的已知绑定为：CHG-174 → DEC-7FDDADE8；CHG-175 → DEC-0B5D9631；CHG-176 → DEC-EFEB1DDA；CHG-177 当前声称绑定 DEC-3362BFFF。本次架构批准不追认 CHG-177，也不改写历史决策证据。

## 4. 定向候选哈希快照

| 相对路径 | 基础设施位 | 母体 | 基础设施位 SHA-256 | 裁决 |
| --- | --- | --- | --- | --- |
| `auto_pm/application/core/change_transaction.py` | 10887 B | 缺失 | `73D024BF...B71D68` | CHG-174 待批 |
| `tests/application/test_change_transaction.py` | 14637 B | 缺失 | `F28E1C75...698D6C0` | CHG-174 待批 |
| `auto_pm/application/core/workflow_orchestrator.py` | 30233 B | 缺失 | `2185E00E...0B3815` | CHG-175/176 待批 |
| `tests/application/test_workflow_orchestrator.py` | 25756 B | 缺失 | `40CDAECF...8D6147` | CHG-175/176 待批 |
| `auto_pm/application/core/project_archive_service.py` | 23324 B | 缺失 | `D4450691...EA3DCE` | CHG-177 隔离 |
| `tests/core/test_project_archive.py` | 20614 B | 缺失 | `8B76386D...5D9CE` | CHG-177 隔离 |
| `auto_pm/application/core/project_scanner.py` | 29810 B | 27102 B，哈希不同 | `5BF3E9BC...B2B5E10` | CHG-177 隔离 |
| `auto_pm/application/core/project_service.py` | 50698 B | 47662 B，哈希不同 | `3600FBA3...30AD4` | CHG-177 隔离 |
| `auto_pm/ui/cli/project.py` | 39804 B | 34408 B，哈希不同 | `521AA526...EE739` | CHG-177 隔离 |
| `tests/core/test_project_service.py` | 14264 B | 13150 B，哈希不同 | `9F786923...ED9600` | CHG-177 隔离 |

## 5. 回收批次

| 批次 | 范围 | 强制前置 | 完成定义 |
| --- | --- | --- | --- |
| R0 治理纠偏 | 全量差异事实包、DEC/CHG/PM_SESSION 冲突矩阵 | 独立报批 | 用新记录纠偏，不篡改旧证据 |
| R1 / CHG-174 | 事务沙箱与测试 | 新 DEC + 精确 pathspec | 母体针对测试、Ruff、Mypy 全绿 |
| R2 / CHG-175/176 | plan/execute 编排内核与测试 | R1 通过；独立批准 | 消除 `git add .` 等越界风险，母体门禁全绿 |
| R3 / CHG-177 | 归档/恢复引擎重新设计与回收 | 新 CHG/DEC | 门禁 fail-closed、事务可恢复、默认无硬删除 |
| R4 环境解耦 | 移除 auto-pm editable/`.pth` 挂接 | 首个候选制品 Gate 2 通过 | 研发与 stable import 物理隔离 |

每个批次都是独立 User 批准边界。

## 6. 需要重新生成的事实包

此前广泛差异数量、换行符等价性和“全量扫描”结论均为历史数据，未作为当前结论采用。进入 WBS-3 前，必须由独立只读任务重新生成带时间戳的差异事实包，至少包括：

- 两侧文件清单、二进制 SHA-256、文件大小和相对路径；
- Git 追踪、暂存、未暂存、未跟踪状态；
- 每项候选的来源 Commit/CHG 与关联 DEC；
- 母体/基础设施目录差异；
- 生成命令、解释器路径、时间戳和证据哈希。

测试日志、`.coverage`、Mypy 输出等运行产物只能标记 `DO_NOT_RECOVER`。是否删除、归档或更新 `.gitignore` 是独立变更，不能由本矩阵授权。

## 7. 退出条件

本矩阵只有在事实包重建、决策链纠偏方案批准、候选逐项审查、Codex 独立复核并获得 User 对具体回收批次的新批准后，才能作为 WBS-3 输入；在此之前不得进入回收。
