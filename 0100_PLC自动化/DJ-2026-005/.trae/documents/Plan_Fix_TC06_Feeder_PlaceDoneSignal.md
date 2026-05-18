# 计划：修复 TC06_Feeder_PlaceDoneSignal 断言失败问题

## 目标
确保 `TC06_Feeder_PlaceDoneSignal` 测试用例能够成功触发 `GlobalVars.stFeeder.q_bRunning = TRUE`，并在运行后通过 `ASSERT`。

## 当前已知信息
- **测试用例位置**：`c:\Users\fubai\Desktop\My_Workspace\0100_PLC自动化\DJ-2026-005\02_PLC程序\通用ST程序及变量表\Test\basic_test.scltest`，第 147 行。
- **关键赋值**：
  ```st
  SET GlobalVars.stFeeder.i_bAutoMode      := TRUE;
  SET GlobalVars.stFeeder.i_bManualMode    := FALSE;
  SET GlobalVars.stFeeder.i_bPlaceDone     := TRUE;
  SET GlobalVars.stFeeder.i_bGlueMachineAllowFeed := TRUE;
  WAIT_CYCLES 10;
  ASSERT GlobalVars.stFeeder.q_bRunning = TRUE;
  ```
- **失败表现**：`q_bRunning` 始终为 `FALSE`，导致 `ASSERT` 失败。
- **最近变更**：项目在 V6.0.0 标准化期间统一了变量前缀（`i_` → `q_`），并对轴抽象层（AxisControl）做了占位改造，导致部分输入变量映射错位或未正确同步。

## 可能的根本原因
| 类别 | 具体表现 | 涉及文件/变量 |
|------|----------|--------------|
| 变量映射不完整 | `i_bPlaceDone`、`i_bGlueMachineAllowFeed` 未在 `FB_1004` 或 `GlobalVars.stFeeder` 中正确读取 | `DB1\GlobalVars.db`, `.plc.json` |
| FB_1004 状态机逻辑缺陷 | `q_bRunning` 的赋值依赖于内部状态（如 X2 轴使能、速度）未满足 | `FB_1004_GlueMachineFeeder_BufferFraming.scl` |
| 轴抽象占位未完成 | 占位 FB 没有及时返回请求状态，影响上层逻辑 | `refactor_plan_v2.md`, `variable-alarm-fix_plan_v2.md` |
| 编译/下载不对齐 | 编译后的 `.scl` 未成功下载到 PLC/模拟器 | `OB1.scl`, `FB_1004_GlueMachineFeeder_BufferFraming.scl` |
| 文档同步不完整 | `fb_interfaces_and_documentation_improvement_plan.md` 对触发条件描述不全 | 文档层面 |

## 解决方案总览
1. **确认变量映射**  
   - 检查 `DB1\GlobalVars.db` 中 `stFeeder` 的输入字段是否完整且名称匹配。  
   - 若缺失，使用 `SearchReplace` 或手动编辑 `.plc.json` 补全映射。  
2. **审查并修复 FB_1004 状态逻辑**  
   - 在 `FB_1004_GlueMachineFeeder_BufferFraming.scl` 中定位 `q_bRunning` 的赋值语句。  
   - 确保所有必要条件（`i_bAutoMode = TRUE`、`i_bManualMode = FALSE`、`i_bPlaceDone = TRUE`、`i_bGlueMachineAllowFeed = TRUE` 以及 X2 轴状态）均已满足后才将 `q_bRunning` 设为 `TRUE`。  
   - 如有缺失，使用 `SearchReplace` 添加对应的 `IF` 判定块。  
3. **完成轴抽象占位实现**  
   - 查看 `refactor_plan_v2.md` 中关于 AxisControl 的描述，实现最小化的状态回传（如直接映射一个 `BOOL` 表示轴已请求）。  
   - 确保该状态在 `FB_1004` 中被正确读取并纳入 `q_bRunning` 的计算。  
4. **本地编译与下载验证**  
   - 使用合适的命令（如 `rebuild` 或 `download`）重新编译所有 `.scl` 文件并下载到目标 PLC或模拟器。  
   - 通过 VS Code 的 **Diagnostics** 窗口确认 `q_bRunning` 已变为 `TRUE`。  
5. **临时调试信息（可选）**  
   - 在 `basic_test.scltest` 中插入 `WRITE` 语句打印 `i_bPlaceDone`、`i_bGlueMachineAllowFeed`、`q_bRunning` 的实际值，以便实时观察。  
6. **更新文档与 Bug 记录**  
   - 在 `PM_SESSION_DJ-2026-005.md` 的 `bug_log` 中添加一条新的记录，描述本次根因和修复。  
   - 同步更新 `fb_interfaces_and_documentation_improvement_plan.md`，确保触发条件描述完整。  

## 具体实施步骤（按优先级排序）
| 步骤 | 操作 | 文件/工具 | 备注 |
|------|------|-----------|------|
| 1 | 检查 `GlobalVars.db` 中 `stFeeder` 的输入字段 | Read | 确认 `i_bPlaceDone`、`i_bGlueMachineAllowFeed` 存在且拼写正确 |
| 2 | 若缺失，使用 `SearchReplace` 补全映射 | SearchReplace | 目标文件：`.plc.json` 或 `GlobalVars.db` |
| 3 | 打开 `FB_1004_GlueMachineFeeder_BufferFraming.scl` 检查 `q_bRunning` 赋值逻辑 | Read & SearchReplace | 需要确保所有条件都在同一 `IF` 块中 |
| 4 | 在 `refactor_plan_v2.md` 中确认 AxisControl 占位状态已实现 | Read | 如未实现，手动实现最小化映射 |
| 5 | 重新编译并下载全部 `.scl` 文件 | RunCommand (rebuild/download) | 需要新建终端，稍后再执行 |
| 6 | 在 `basic_test.scltest` 添加 `WRITE` 调试语句 | Write | 仅用于观察变量实时值 |
| 7 | 验证 `TC06_Feeder_PlaceDoneSignal` 通过 | RunCommand (execute test) | 观察 `ASSERT` 是否通过 |
| 8 | 在 `PM_SESSION_DJ-2026-005.md` 添加 bug_log 记录 | Write | 记录本次根因与解决方案 |
| 9 | 更新 `fb_interfaces_and_documentation_improvement_plan.md` | Write | 完善触发条件描述 |

## 风险与注意事项
- **映射错误**：错误的 `SearchReplace` 可能导致其他全局变量错位，使用前请再次核对变量名。  
- **多文件同步**：修改 `.scl` 后必须重新编译并下载，否则旧逻辑仍然占用运行内存。  
- **占位 FB**：若占位实现不完整，可能导致后续依赖的多个 FB 行为异常，建议先在 **AxisControl** 上实现最小化的状态回传。  
- **调试信息**：`WRITE` 语句会增加运行时开销，完成排查后请及时删除或注释掉。

## 交付物
1. 更新后的 `FB_1004_GlueMachineFeeder_BufferFraming.scl`（若需要修改）。  
2. 确认的变量映射文件 `.plc.json`（已补全）。  
3. 新增的调试信息（可选）。  
4. 更新的 `PM_SESSION_DJ-2026-005.md`（bug_log 记录）。  
5. 完善后的 `fb_interfaces_and_documentation_improvement_plan.md`。

---

**下一步**：在用户确认此计划后，立即执行步骤 1‑3（检查映射、修复 FB 逻辑），随后进行编译和验证。