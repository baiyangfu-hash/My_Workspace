# SW-2026-008 Modbus 诊断 / 补单 / 三层测试 执行计划（续作版）

> 创建时间：2026-07-19
> 续作时间：2026-07-19（上下文丢失后基于实际状态重写）
> 项目路径：`01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具`
> 工作空间根：`c:\Users\fubai\Desktop\My_Workspace`
> venv 路径：`c:\Users\fubai\Desktop\My_Workspace\.venv\`

---

## 一、摘要 (Summary)

针对 SW-2026-008 auto-pm 项目执行四阶段闭环：① **项目诊断 + Modbus 影响审查**；② **使用 auto-pm 工具补完 CHG-SCPT-2026-133 变更单**（Modbus 缺陷修复与功能码全量覆盖）；③ **修复版本号一致性**（pyproject.toml 1.0.0 → 1.1.0）；④ **三层完整测试**（冒烟 + 全量回归 + 全量对账），并同步回写 PM_SESSION 真源。

**续作背景**：上一轮上下文丢失前已完成 Phase A（诊断报告）与 Phase B（CHG-133 CLI 创建）。本轮基于实际文件状态重写计划，处理 Phase B 遗留内容补完 + Phase C/D/E 全部待办项。

---

## 二、当前实际状态分析 (Current State Analysis - 已验证)

### 2.1 已完成项（验证通过）

| 项目 | 状态 | 证据 |
|------|------|------|
| Phase A 诊断报告 | ✅ 已创建 | `09_整改项/2026-07-19_项目诊断报告.md` 文件存在 |
| Phase B CHG-133 文件 | ✅ 已创建 | `00_项目管理/04_变更管理/01_变更单/CHG-SCPT/CHG-SCPT-2026-133.md`（8779 字节，2026-07-19 6:15 创建） |
| CHG-133 基本字段 | ✅ 已填充 | §3 编号/领域/性质/范围/状态=closed + §4 变更背景/必要性 已填写 |

### 2.2 待处理项（本轮要完成）

| 编号 | 问题 | 严重度 | 处理方案 |
|------|------|--------|----------|
| P1-续 | CHG-133 §5-§10 内容为模板默认值（CLI 只填 §3+§4，对比 CHG-132 全填写） | 高 | Phase B-续：用 Edit 工具补完 §5/§6/§7/§8/§9/§10/§11 |
| P2-台账 | 台账 `01_版本变更台帐.md` 滞后至 040 CHG-107（2026-07-09），缺 CHG-108~CHG-133 共 26 条 | 高 | Phase D3：`ledger reconcile --auto-fix` 自动补建 |
| P3-版本 | pyproject.toml = 1.0.0 / CHANGELOG = 1.1.0 / PM_SESSION §2 = V0.9.3 三者不一致 | 高 | Phase C：同步三者到 1.1.0 |
| P4-PM-§0 | PM_SESSION §0 last_updated = 2026-07-16 滞后 | 中 | Phase C：更新到 2026-07-19 |
| P5-PM-§2 | PM_SESSION §2 milestone = "V0.9.3" 失真 | 中 | Phase C/E：更新到 V1.1.0 |
| P6-PM-行数 | PM_SESSION 312 行略超 300 行上限 | 低 | Phase E：若元测试失败则 `pm-session archive --section 6 --keep-recent 15` |
| P7-测试 | 全量 1443 测试未跑（仅跑 modbus 25 + QML 13 聚焦测试） | 中 | Phase D：三层完整测试 |

### 2.3 Modbus 功能对项目影响审查（核心结论，已通过代码核查）

| 维度 | 状态 | 说明 |
|------|------|------|
| 核心代码 | 3 文件 | `auto_pm/modbus/{modbus_service.py, modbus_bridge.py, __init__.py}` |
| QML 视图 | 4 文件 | `ModbusDebuggerView.qml` + 3 子组件（BitExpander/ScannerGrid/TrendCanvas） |
| 集成点 | 2 文件 | `main.qml`（侧边栏轨道3 + StackLayout 索引8）+ `qml_main_window.py`（modbusBridge 上下文） |
| 测试 | 1 文件 25 测试 | `tests/modbus/test_modbus_service.py` |
| 数据隔离 | 良好 | 不写入 SQLite DB，不引入第三方运行时依赖（pymodbus 仅注释提及，未实际 import） |
| 模块耦合 | 低 | 独立模块，与其他 Service/Facade/Bridge 无交叉引用 |
| 功能码覆盖 | 完整 | 读 11 个（FC01/02/03/04/07/17/20/22/23/24/43）+ 写 6 个（FC05/06/15/16/21/22），见 modbus_service.py 文件头 docstring |

**风险点**：
- CHG-132 仅覆盖 Modbus 联调工坊初始集成（FC01-FC06）；P0 修复（currentValue FINAL 冲突）+ 功能码补齐由 CHG-133 单独承载
- pymodbus v3.14.0 仅在注释/文档中提及，未在 pyproject.toml 声明，**未实际 import**（modbus_service.py 是纯仿真实现）。属文档/代码一致性瑕疵，非阻断，登记为长期建议。

---

## 三、建议变更 (Proposed Changes)

### Phase A：项目诊断报告 ✅ 已完成（无需再动）

**输出文件**：`09_整改项/2026-07-19_项目诊断报告.md`（已存在）

### Phase B-续：补完 CHG-SCPT-2026-133 变更单内容（§5-§11）

**目标**：CLI 已创建 CHG-133 骨架（§3+§4），但 §5-§11 仍是模板默认值。对比 CHG-132 全填写状态，需用 Edit 工具补完。

**改动文件**：`00_项目管理/04_变更管理/01_变更单/CHG-SCPT/CHG-SCPT-2026-133.md`（使用 Edit 工具）

**补完内容**（参考 CHG-132 同结构）：

1. **§5.1 变更前**：填入"涉及文件/交付物"和"关键参数/配置"
   - 涉及文件：`ModbusDebuggerView.qml`（4 处 currentValue → _comboValue）+ `modbus_service.py`（新增 FC07/20/22/23/24/43 读 + FC21/22 写 + _MockModbusClient 7 个 mock 方法）+ `tests/modbus/test_modbus_service.py`（新增 11 测试覆盖新功能码）
   - 关键参数：fcCombo 4→11 选项 / writeFcCombo 4→6 选项

2. **§5.2 变更后**：填入目标状态

3. **§6.1 PMBOK 五大约束**：勾选影响程度（参照 CHG-132：范围/进度/成本/质量/风险均无影响，因属补单）

4. **§6.2 技术领域影响**：勾选 SCPT 受影响（关联 CHG-SCPT-2026-133）

5. **§6.3 变更传播链**：填"无跨领域影响"

6. **§7 变更实施计划**：填入任务表（5 行：P0 修复 + 功能码补齐 + mock 补齐 + QML 选项扩展 + 测试补充）

7. **§8.1 审批流程**：填入"系统级变更审批 / fubai / 补单流程，直接关闭 / 2026-07-19 / 电子签名"

8. **§8.2 审批结论**：勾选"通过"

9. **§9 变更实施记录**：填入实施摘要（参照 CHG-132 第 9 章格式）

10. **§10.1 验证项清单**：填入 4 项验证（单元测试 / ruff / mypy / GUI 加载）

11. **§10.3 验证结论**：勾选"全部通过,可关闭"

12. **§11 版本详细变更说明**：替换占位文本，填入实际变更明细（V1.0.0 详细变更 1-N 条）

**验证**：
- 文件存在 ✅（已验证）
- 状态 = closed ✅（已验证）
- §5-§11 内容完整填写（Phase B-续完成后通过 Read 工具自检）

### Phase C：修复版本号一致性

**目标**：让 pyproject.toml / CHANGELOG.md / PM_SESSION 三者版本号一致为 1.1.0

**改动文件**（使用 Edit 工具）：

1. **pyproject.toml** L7
   - 改动：`version = "1.0.0"` → `version = "1.1.0"`
   - 理由：CHANGELOG 已升级到 [1.1.0]，pyproject 必须同步

2. **PM_SESSION_SW-2026-008.md** §0 Meta
   - 改动：`- last_updated: 2026-07-16` → `- last_updated: 2026-07-19`

3. **PM_SESSION_SW-2026-008.md** §2 Current Focus milestone
   - 改动：`代码基线 **V0.9.3 变更中心已闭环**` → `代码基线 **V1.1.0 Modbus 联调工坊 + 缺陷修复已闭环**`
   - 理由：消除 §2 失真声明（§3 已写 V1.0.0，本次升级到 V1.1.0）

**验证**（三件套一致性）：
- `pyproject.toml` version = "1.1.0" ✅
- `CHANGELOG.md` 最新章节 = [1.1.0] ✅
- `PM_SESSION §2` milestone = V1.1.0 ✅

### Phase D：三层完整测试

#### D1：冒烟测试（预期 < 30s）

```powershell
& "c:\Users\fubai\Desktop\My_Workspace\.venv\Scripts\Activate.ps1"
cd "c:\Users\fubai\Desktop\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\02_在研项目\SW-2026-008_auto-pm_自动化项目管理工具"
python -m pytest tests/test_smoke.py -v --tb=short --no-cov -m smoke
```

**预期**：~28 测试全通过（覆盖核心模块导入 + 状态流转合法性 + Service/DB/CLI 基础功能）

#### D2：全量回归测试（分批策略，避免单次卡住）

**步骤 D2.1：非 GUI 部分（核心 + change + application + spec + plc + cli + db + modbus 等）**

```powershell
python -m pytest tests/ --ignore=tests/qml/ --no-cov --timeout=60 -q --tb=short
```

**预期**：~1280 测试通过，0 失败（modbus 25 + 其他 ~1255）

**步骤 D2.2：QML 部分（GUI 默认可见模式，符合 project-rule.md 硬约束）**

```powershell
$env:GUI_VISIBLE = "1"  # 不设置 QT_QPA_PLATFORM=offscreen，强制可见模式
python -m pytest tests/qml/ --no-cov --timeout=60 -q --tb=short
```

**预期**：~163 QML 测试通过（包含 ModbusDebuggerView 加载验证）

**步骤 D2.3：合并结果**

预期总数：~1443 测试（与 PM_SESSION §7 声明一致）

**后台任务监控纪律**（来自 project-rule.md §7）：
- 设置预期完成时间：非 GUI ~3 分钟 / QML ~30 秒
- 用 `run_in_background: true` 启动后，用 `TaskOutput(block=true, timeout=120000)` 分段主动轮询
- 超过预期时间未完成时立即读日志看进度，进度停滞即 `TaskStop` 停止并诊断根因
- 给用户明确时间预期

#### D3：全量对账（ledger reconcile --auto-fix）⭐ 重点修复台账滞后

```powershell
python -m auto_pm -w "c:\Users\fubai\Desktop\My_Workspace" ledger reconcile SW-2026-008 --auto-fix
```

**预期**：自动补建 CHG-108~CHG-133 共 26 条缺失台账记录；is_clean=true / 缺失 0 / 孤儿 0 / 状态不一致 0

**验证**：
- 台账文件 `01_版本变更台帐.md` 末尾出现 041~066 条新记录
- CLI 输出 `is_clean: true`

#### D4：补充门禁检查

```powershell
# G1: ruff
python -m ruff check auto_pm/
# G2: mypy
python -m mypy auto_pm/
# G3: PM_SESSION 元测试（验证行数/大小/必需章节）
python -m pytest tests/test_pm_session_size.py -v --no-cov
```

**预期**：ruff 0 errors / mypy 0 errors / PM_SESSION 元测试 9 passed

### Phase E：PM_SESSION 真源同步回写

**目标**：将本轮所有变更同步到 PM_SESSION，确保下次会话基于真源推进

**改动文件**：`PM_SESSION_SW-2026-008.md`（使用 Edit 工具，禁止 Python 脚本写入）

**前置条件**（强制）：Phase D 全量测试通过后才能回写 §7 verified 字段（"未验证禁止回写"硬约束）

**改动点**：
1. §0 last_updated：2026-07-16 → 2026-07-19（Phase C 已改）
2. §2 Current Focus：更新为 "CHG-SCPT-2026-133 Modbus 缺陷修复与功能码全量覆盖已闭环（第 64 次 dogfooding），版本号三件套同步至 V1.1.0"
3. §3 Status Summary in_progress：dogfooding 63 → 64 次；completed 追加 CHG-133 条目
4. §3 spec_compliance last_check：2026-07-16 → 2026-07-19；dogfooding 计数 63 → 64
5. §5 change_log：追加 "2026-07-19 CHG-SCPT-2026-133 Modbus 缺陷修复与功能码全量覆盖补单 + 内容补完 + 全量回归 1443 passed"
6. §6 Implementation Log：CHG-133 条目已存在，追加 "本轮回写：CHG-133 已通过 auto-pm CLI 补单 + §5-§11 内容补完 + 全量回归 1443 passed + ledger reconcile 修复 26 条滞后台账"
7. §7 Verification Log：更新 verified 字段（ruff 0 / mypy 0 / pytest 1443 passed / ledger reconcile 0 差异）
8. §8 Handoff Notes current_state：更新到 V1.1.0 + CHG-133 闭环 + 全量回归通过
9. §9 Next Actions：标记 CHG-133 完成

**元测试应对策略**（PM_SESSION 当前 312 行，略超 300 上限）：
- 优先尝试直接 Edit，若元测试失败则用 `python -m auto_pm -w "..." pm-session archive --section 6 --keep-recent 15` 归档早期条目
- 归档后重跑元测试，必须 9 passed

**验证**：
- `python -m auto_pm -w "..." pm-session check` 通过（0 缺失 0 回归）
- `python -m pytest tests/test_pm_session_size.py -v --no-cov` 通过（≤150KB / ≤300 行）
- PM_SESSION §7 verified 字段更新为全量 1443 passed
- PM_SESSION §8 current_state 更新到 V1.1.0 + CHG-133 闭环

---

## 四、假设与决策 (Assumptions & Decisions)

### 4.1 关键假设
1. venv 内 auto-pm 已可执行（PM_SESSION 历史记录显示已多次成功调用，Phase B 已实证 CLI 可用）
2. 全量 1443 测试基线来自 PM_SESSION §7（modbus 25 + 其他 ~1418）
3. PM_SESSION 主文件 105KB（≤150KB ✅），312 行（>300 ⚠️），可能触发元测试失败，需准备归档预案
4. CHG-133 §5-§11 内容补完不违反"必须用 CLI 创建变更单"约束（CLI 已完成创建，Edit 工具仅补完模板内容，类似 CHG-132 的填写流程）

### 4.2 关键决策
- **决策 1**：CHG-133 单独补单，不合并其他提交（用户已确认）
- **决策 2**：版本号升级方向为 1.0.0 → 1.1.0（保留 CHANGELOG 已有 [1.1.0] 章节，同步 pyproject）（用户已确认）
- **决策 3**：三层完整测试含 GUI 可见模式（用户已确认，符合 project-rule.md 硬约束）
- **决策 4**：所有项目文件修改使用 Edit/Write 工具（禁止 Python 脚本写入，避免 VS Code 缓冲区陈旧）
- **决策 5**：变更单必须用 `auto-pm change create` CLI 创建（已完成 ✅）；创建后的内容补完用 Edit 工具（符合 project-rule.md 硬约束）
- **决策 6**：台账滞后 26 条通过 `ledger reconcile --auto-fix` 自动修复（不手工编辑台账）

### 4.3 风险与应对
| 风险 | 概率 | 应对 |
|------|------|------|
| 全量 pytest 卡住（历史曾出现卡在 95%） | 中 | 分批策略：非 GUI + QML 分两次跑，每批设置 timeout，用 TaskOutput 分段轮询 |
| PM_SESSION 行数 312 超阈触发元测试失败 | 中 | Phase E 先尝试直接 Edit，若失败用 `pm-session archive --section 6 --keep-recent 15` 归档 |
| QML 可见模式在无显示器环境失败 | 低 | 项目规则要求默认可见模式，若环境无显示器再降级 offscreen 并报告用户 |
| `ledger reconcile --auto-fix` 不能补建历史缺失记录 | 低 | 若自动修复失败，则需评估是否手工补建或登记为已知问题 |

---

## 五、验证步骤 (Verification Steps)

### 5.1 Phase A 验证 ✅
- [x] `09_整改项/2026-07-19_项目诊断报告.md` 文件存在
- [x] 报告包含 Modbus 影响分析章节
- [x] 报告包含问题清单

### 5.2 Phase B 验证（含 B-续）
- [x] `00_项目管理/04_变更管理/01_变更单/CHG-SCPT/CHG-SCPT-2026-133.md` 文件存在
- [x] 状态：closed
- [ ] §5/§6/§7/§8/§9/§10/§11 内容已补完（Phase B-续完成后通过 Read 工具自检）

### 5.3 Phase C 验证
- [ ] `pyproject.toml` L7 = `version = "1.1.0"`
- [ ] `CHANGELOG.md` 最新章节 = `## [1.1.0] - 2026-07-19`
- [ ] `PM_SESSION_SW-2026-008.md` §0 last_updated = 2026-07-19
- [ ] `PM_SESSION_SW-2026-008.md` §2 milestone 含 "V1.1.0"

### 5.4 Phase D 验证
- [ ] D1 冒烟测试：~28 passed，0 failed
- [ ] D2.1 非 GUI 全量：~1280 passed，0 failed
- [ ] D2.2 QML 可见模式：~163 passed，0 failed
- [ ] D2.3 合计：~1443 passed，0 failed（与 PM_SESSION §7 声明一致）
- [ ] D3 ledger reconcile：台账补建 26 条 CHG-108~133 记录；is_clean=true / 缺失 0 / 孤儿 0 / 状态不一致 0
- [ ] D4 ruff 0 errors / mypy 0 errors / PM_SESSION 元测试 9 passed

### 5.5 Phase E 验证
- [ ] `python -m auto_pm -w "..." pm-session check` 通过
- [ ] `python -m pytest tests/test_pm_session_size.py -v --no-cov` 9 passed
- [ ] PM_SESSION §7 verified 字段更新为全量 1443 passed
- [ ] PM_SESSION §8 current_state 更新到 V1.1.0 + CHG-133 闭环

---

## 六、执行顺序与时间预估

| 阶段 | 任务 | 预估时间 | 备注 |
|------|------|----------|------|
| ✅ Phase A | 写诊断报告 | 已完成 | 上轮已完成 |
| ✅ Phase B 骨架 | 补 CHG-133 变更单 CLI | 已完成 | 上轮已完成 |
| 🔄 Phase B-续 | 补完 CHG-133 §5-§11 内容 | 5 分钟 | Edit 工具，参考 CHG-132 结构 |
| ⏳ Phase C | 修复版本号一致性 | 2 分钟 | Edit 工具改 3 处 |
| ⏳ Phase D1 | 冒烟测试 | 30 秒 | pytest tests/test_smoke.py |
| ⏳ Phase D2.1 | 非 GUI 全量回归 | 3 分钟 | 后台任务 + 主动轮询 |
| ⏳ Phase D2.2 | QML 可见模式回归 | 30 秒 | GUI_VISIBLE=1 |
| ⏳ Phase D3 | ledger reconcile --auto-fix | 30 秒 | auto-pm CLI，重点修复 26 条滞后 |
| ⏳ Phase D4 | ruff + mypy + 元测试 | 1 分钟 | 三轨门禁 |
| ⏳ Phase E | PM_SESSION 回写 | 5 分钟 | Edit 工具改 §0/§2/§3/§5/§6/§7/§8/§9 |
| ⏳ 收尾 | pm-session check + 元测试复测 | 30 秒 | 验证回写无破坏 |
| **剩余总计** | | **~18 分钟** | |

---

## 七、执行约束（来自 project-rule.md 与 project_memory）

1. **必须先激活 venv**：所有 Python 命令前执行 `& "c:\Users\fubai\Desktop\My_Workspace\.venv\Scripts\Activate.ps1"`
2. **使用 `python -m auto_pm`**：不直接用 `auto-pm`（避免 PowerShell PATH 问题）
3. **`-w` 必须在子命令之前**：`python -m auto_pm -w "<工作空间根>" <子命令>`
4. **禁止 Python 脚本写磁盘修改项目文件**：PM_SESSION/CHG-*.md/代码文件等必须用 Edit/Write 工具
5. **变更单必须用 CLI 创建**：禁止 Write 工具手工创建 CHG-*.md（Phase B 已合规；Phase B-续 仅补完内容用 Edit）
6. **GUI 测试默认可见模式**：不设置 `QT_QPA_PLATFORM=offscreen`，设置 `GUI_VISIBLE=1`
7. **后台任务监控纪律**：分段主动轮询（timeout=120s），不被动等待通知
8. **CHG 闭环后必须 ledger reconcile**：每次 CHG 闭环后执行对账检查
9. **门禁实测强制**：回写 §3/§7 前必须运行 ruff/mypy/pytest
10. **未验证禁止回写**：诊断结论未经运行时验证，禁止写入 PM_SESSION §8/§9
11. **PowerShell 语法**：用 `;` 分号链接命令，不用 `&&`；中文文本用单引号包裹
