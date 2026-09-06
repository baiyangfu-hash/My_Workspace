# TEC-SW008-P0-001：单向发布、双槽运行与回退 WBS

> 状态：**PLANNING BASELINE APPROVED / EXECUTION NO-GO**
> 依据：ADR-SW008-001、PM-033、PM-042、PM-046
> 阶段门禁：每个 WBS 独立报批；本文件不是实施、提交、发布、切流、回退或清理授权。

## 1. 通用控制规则

每个 WBS 都是独立的 User 批准边界。执行团队完成自检只能生成 `handoff_result.json`，不得自动推进到下一 WBS、不得提交、打 Tag、部署、切流、回退或清理。

执行命令必须先解析工作区和获批解释器；缺失即停止：

```powershell
$workspace = (git rev-parse --show-toplevel).Trim()
if ($LASTEXITCODE -ne 0 -or -not $workspace) {
    throw "FATAL: Git workspace root cannot be resolved."
}
$py = Join-Path $workspace ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $py -PathType Leaf)) {
    throw "FATAL: Approved workspace interpreter is unavailable."
}
```

质量工具只允许以该解释器调用，例如 `& $py -m pytest`、`& $py -m ruff`、`& $py -m mypy`。禁止裸可执行文件回退。所有验证应避免写入工作区；如必须生成可持久证据，输出到 `.auto-pm/reports/`，并在任务书中明确获批。

发现 editable install 或 auto-pm `.pth` 污染时，只读记录并停止；不得卸载、删除或修改宿主环境。

## 2. WBS-0/WBS-1：架构与治理基线

| WBS | 目标 | 交付物 | 状态 |
| --- | --- | --- | --- |
| WBS-0 | 确立研发母体、稳定部署、运行状态和规范真源的物理边界 | ADR-SW008-001 | **架构已批准** |
| WBS-1 | 建立全量差异事实包及 DEC/CHG/handoff/PM_SESSION 纠偏方案 | 不可变事实包、disposition/supersession 方案 | **仅规划授权** |

## 3. WBS-2：Bootstrap R0 法证冻结

前置条件：Phase 0 已被 Codex 复核并获 User 明确批准。

执行目标：对当时的稳定容器建立不可覆盖的法证恢复锚点，不改变运行位。

证据必须包含唯一 release-id、容器文件清单、每文件 SHA-256、归档自身 SHA-256、HEAD/index/工作树状态、创建时间、实际解包验证结果和 manifest。归档文件名必须包含 UTC 时间戳与短 HEAD。失败产物标记 `.incomplete`，保存现场并停止，不得删除或覆盖既有备份。

磁盘空间检查必须以解析出的工作区卷为准，不得写死盘符。WBS-2 不创建 Git Tag。

执行记录（2026-09-04）：User 明文批准本 WBS 后，已生成 `bootstrap-r0-20260904T204302Z-1b53f38`。归档、修正 manifest 与独立解包验证均已完成；1698 个文件、79,454,227 字节的路径集合、大小和 SHA-256 全部一致，源目录与 Git index 前后不变。有效证据为 `.auto-pm/reports/bootstrap-r0-20260904T204302Z-1b53f38_verification.corrected.json`。早先由 Antigravity 生成的 `.incomplete` 归档及错误计数报告仅保留为失败证据，不是恢复锚点。

## 4. WBS-3：按 CHG 分批候选回收

前置条件：WBS-2 完成、差异事实包重建、每批候选获得 User 批准。

每批只能处理矩阵中明确列出的文件；先在母体隔离副本审查来源、哈希、依赖与测试影响，再由批准的执行任务实施。每批结束仅输出差异、验证结果和 `handoff_result.json`。失败时停止、保存现场、输出差异，等待 Codex 和 User 决定；禁止自动覆盖、反转、提交或回滚。

## 5. WBS-4：母体独立工程门禁

前置条件：批准的回收批次已经完成且母体可独立构建。

验收：包解析物理指向母体；全量测试、Ruff、Mypy 与文档门禁退出码均为 0。任何非零结果均阻止后续 WBS；缺陷只能在母体修复并附测试，稳定容器不得被用于修补。

## 6. WBS-4.5：根入口与初始化脚本硬化

目标：根入口只解析稳定容器的 active 指针。active 失效时只能验证 previous 指针；两者无效立即非零退出，绝不导入母体。

`setup_env.bat` 不得含 editable install，也不得写入永久 `PYTHONPATH`。开发测试使用工作区 `.venv` 的进程级母体路径；生产启动只解析 active release 的进程级路径。需要新增动态测试覆盖 active 正常、active 损坏且 previous 正常、双指针均损坏、JSON 损坏和越界 release id；每一场景都必须断言不导入母体。

## 7. WBS-5：稳定容器双槽骨架

创建 `releases/<release-id>`、`active_release.json`、`previous_release.json` 和锁定协议的实现与测试。此阶段仅构建骨架和测试，不写入生产 active 槽，不迁移业务代码。

## 8. WBS-6：候选制品与非活动槽预检

从经 Gate 1 验证的母体 Commit 构建候选制品、SHA-256 manifest 和隔离暂存槽。隔离子进程只注入候选 release 路径并进行 doctor、版本和 dry-run 验证。完成 Gate 2 后生成发布申请、manifest 哈希、验证结果和 `handoff_result.json`，立即停机等待批准。

## 9. WBS-6.5：批准后的正式发布与切流

唯一前置条件是 User 在控制台提供明确“批准切流 / APPROVED”证据，且 Gate 1、Gate 2 与发布申请完整。

获得批准后才允许签发正式 Tag、部署获批候选到非活动槽、获取锁、通过同卷 `os.replace` 更新 active/previous 指针，并执行 Launcher 冒烟验证。任何失败不得自动回退或清理，必须保存现场并报告。

## 10. WBS-7：双槽验证与故障演练

在隔离且获批的条件下验证 active、previous 和损坏指针行为。自动降级仅限 active 到已批准 previous，必须产生审计告警；不得指向母体。

## 11. WBS-8：观察期与历史归档申请

在稳定运行观察期结束、User 验收后，才可提交历史平铺代码的归档或清理申请。任何删除需独立批准、明确目标、备份与可恢复性验证；本 WBS 不授权自动删除。

## 12. 计划中的发布/回退命令契约

下列均为待实现接口，当前不得宣称可用：

| 命令 | 职责 | 强制输入 | 禁止副作用 |
| --- | --- | --- | --- |
| `auto-pm release build` | 从 source commit 构建不可变候选制品 | PID、CHG、source_commit、version | 不部署、不切流 |
| `auto-pm release verify` | 在隔离非活动槽执行 Gate 2 | artifact_hash、manifest_hash、target_slot | 不修改 active/previous |
| `auto-pm release activate` | 原子更新 active/previous | User 批准、已验证 manifest | 不接受脏 commit 或候选自批 |
| `auto-pm release rollback` | 切回已批准 previous | User 回退批准、故障证据 | 不回退到母体，不删除失败版 |
| `auto-pm release status` | 只读返回 active/previous、哈希、门禁和健康状态 | workspace | 不修改任何状态 |

## 13. 验收标准

| AC | 验收项 | 通过标准 | 必需证据 |
| --- | --- | --- | --- |
| AC-01 | 真源唯一性 | 只识别 SW-2026-008 为可编辑源 | 路径/哈希矩阵 |
| AC-02 | 无链接/双向同步 | 不存在 Junction、软/硬链接或反向同步脚本 | 只读扫描报告 |
| AC-03 | 研发/运行解耦 | stable 不通过 editable、`.pth` 或永久 `PYTHONPATH` 导入母体 | import provenance |
| AC-04 | 差异回收 | 每个文件都有 CHG、新 DEC、原/目标哈希和精确 pathspec | recovery manifest + handoff_result |
| AC-05 | 母体 Gate 1 | pytest、Ruff、Mypy、doctor、spec/doc/专项门禁全部 Exit Code 0 | 不可变 Gate 1 报告 |
| AC-06 | 制品完整性 | artifact 和 deployment manifest 全文件 SHA-256 匹配 | artifact/deployment manifest |
| AC-07 | 非活动槽 Gate 2 | import、CLI、doctor、spec、dry-run、GUI smoke 全绿 | 隔离验证报告 |
| AC-08 | 原子切流 | 仅在 User 批准后使用锁 + 同卷 `os.replace` | 批准证据 + 切流日志 |
| AC-09 | 回退能力 | active 损坏可回到已批准 previous；双槽失效 Fail-Closed | 故障演练报告 |
| AC-10 | 禁止回退母体 | 指针损坏、路径越界等场景均不导入研发源 | 动态测试 + import provenance |
| AC-11 | PM 闭环 | source_commit、version、artifact_hash、Gate 1/2 和部署证据在 SW 真源一致，SYS 有治理落账 | ledger reconcile + PM_SESSION check |
| AC-12 | 可恢复性 | Bootstrap R0、active、previous 和已批准 source commit 可独立验证 | 解包/重建/回退证据 |

## 14. 当前阻塞与停止线

WBS-0 架构基线已获批准，WBS-2 法证冻结已 PASS；但 WBS-1 只获得规划文档授权，WBS-3 至 WBS-8 均未获执行批准。

当前 26 个 staged 文件、DEC 语义冲突、Mypy 2 项错误、根入口架构漂移和暂存差异检查失败必须保留为可解释现场。下一合法动作是单独报批 WBS-1 的“全量差异事实包 + 决策链纠偏记录”，未获新批准前不得修复、reset、覆盖、移动、删除、提交或发布。
