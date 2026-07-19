# SW-2026-008 Modbus 诊断/补单/测试 续作收口计划

## 摘要

本计划是上轮会话（已断上下文）的续作收口部分。上轮已完成 Phase A 项目诊断 / Phase B CHG-133 变更单补完 / Phase C 版本号一致性修复 / Phase D1 冒烟测试 / Phase D2.1 非 GUI 全量回归测试。本计划聚焦剩余 5 项收口工作：**D2.2 QML 可见模式回归 → D3 台账对账自愈 → D4 三轨门禁 → E PM_SESSION 真源同步+§7 归档 → 收尾验证与汇报**。

## 当前实际状态分析（基于 2026-07-19 实测）

### 已完成项 ✅

| 项 | 状态 | 证据 |
|----|------|------|
| Phase A 项目诊断 | ✅ 完成 | 详见上轮诊断报告 |
| Phase B CHG-SCPT-2026-133 补单 | ✅ 完成 | 文件存在 221 行，§1-§12 全部填写完整（§9 实施记录+§10 4 项验证+§11 5 条详细变更） |
| Phase C 版本号三件套一致 | ✅ 完成 | pyproject.toml=1.1.0 / CHANGELOG [1.1.0] / PM_SESSION §2 milestone=V1.1.0 |
| Phase D1 冒烟测试 | ✅ 完成 | 23 passed in 0.79s |
| Phase D2.1 非 GUI 全量回归 | ✅ 完成 | 1269 passed + 2 skipped + 4 failed（全在 test_pm_session_size.py） in 292.84s |

### 待处理项（7 项 P1-P7）

| # | 问题 | 根因 | 修复方案 |
|---|------|------|----------|
| P1 | PM_SESSION §7 回归 | L148 出现 "## 7. Verification Log（2026-07-19 Modbus 缺陷修复与功能码全量覆盖）"，CHG-087 Stage 1 已删除但本轮手工回写时引入 | `pm-session archive --section 7` 整章归档 |
| P2 | PM_SESSION 行数超阈 | 312 行 > 300 阈值；其中 §7 占 16 行（L148-L163），§9 占 126 行（L187-L312） | 归档 §7 后 312-16=296 ≤ 300 ✅ 无需归档 §6 |
| P3 | 台账滞后 26 条 | 台账最后一条是 040 CHG-107（2026-07-09），缺 CHG-108~CHG-133 共 26 条 | `ledger reconcile SW-2026-008 --auto-fix` 自动补建 |
| P4 | QML 可见模式回归未跑 | 上轮未执行 | `GUI_VISIBLE=1 pytest tests/qml/`（project-rule.md 硬约束：禁止 offscreen） |
| P5 | ruff/mypy 门禁未实测 | 上轮未执行 | `ruff check auto_pm/` + `mypy auto_pm/` |
| P6 | PM_SESSION §3/§8 真源未同步 | §3 completed 未追加 CHG-133 条目；§8 current_state 仍是 CHG-132 | Edit 工具回写 §3 + §8 |
| P7 | 元测试未通过 | test_pm_session_size.py 4 个失败（§7 回归 + 行数超阈） | P1+P2 修复后复测应全绿 |

### 关键约束

- **venv 强制激活**：`c:\Users\fubai\Desktop\My_Workspace\.venv\Scripts\Activate.ps1`
- **GUI 测试可见模式**：`$env:GUI_VISIBLE = "1"`，禁止 `QT_QPA_PLATFORM=offscreen`
- **`python -m auto_pm`** 而非 `auto-pm`（避免 PowerShell PATH 问题）
- **`-w` 必须在子命令之前**
- **禁止用 Python 脚本写磁盘修改 PM_SESSION**：必须用 Edit/Write 工具
- **后台任务监控纪律**：分段主动轮询（timeout=120s），禁止被动等待

## 建议变更（剩余 5 个 Phase）

### Phase D2.2：QML 可见模式回归

**目的**：验证 163 个 QML 测试在可见模式下通过（包含 ModbusDebuggerView 加载验证）。

**命令**：
```powershell
& "c:\Users\fubai\Desktop\My_Workspace\.venv\Scripts\Activate.ps1"
$env:GUI_VISIBLE = "1"  # 强制可见模式，不设置 QT_QPA_PLATFORM=offscreen
cd "c:\Users\fubai\Desktop\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\02_在研项目\SW-2026-008_auto-pm_自动化项目管理工具"
python -m pytest tests/qml/ --no-cov --timeout=60 -q --tb=short 2>&1 | Tee-Object -FilePath "coverage\d22_qml_regression.log"
```

**预期结果**：~163 passed in <30s。若失败立即用 `--tb=long` 重跑获取完整 traceback。

**执行方式**：前台同步执行（预期 < 30s）。

### Phase D3：台账对账自愈

**目的**：补建 26 条滞后台账记录（CHG-108~CHG-133）。

**命令**：
```powershell
python -m auto_pm -w "c:\Users\fubai\Desktop\My_Workspace" ledger reconcile SW-2026-008 --auto-fix
```

**预期结果**：
- 对账前：缺失 26 条 / 孤儿 0 / 状态不一致 0
- 对账后：缺失 0 / 孤儿 0 / 状态不一致 0
- 台账文件 `00_项目管理\04_变更管理\04_变更记录\01_版本变更台帐.md` 从 104 行增长到约 130 行

**验证**：再次运行 `ledger reconcile SW-2026-008`（不带 --auto-fix）应输出 "台账一致，无差异"。

### Phase D4：三轨门禁实测

**目的**：实测 ruff/mypy/pytest 三轨门禁全绿（不含 PM_SESSION 元测试，元测试在 Phase E 后复测）。

**命令**（并行执行）：
```powershell
# 轨 1：ruff
python -m ruff check auto_pm/ 2>&1 | Tee-Object -FilePath "coverage\d4_ruff.log"

# 轨 2：mypy
python -m mypy auto_pm/ 2>&1 | Tee-Object -FilePath "coverage\d4_mypy.log"

# 轨 3：PM_SESSION 元测试（此时应仍失败，验证 Phase E 修复目标）
python -m pytest tests/test_pm_session_size.py -v --no-cov --tb=short 2>&1 | Tee-Object -FilePath "coverage\d4_meta.log"
```

**预期结果**：
- ruff：0 errors
- mypy：0 errors in N source files
- 元测试：4 failed（与 D2.1 一致，等 Phase E 修复）

### Phase E：PM_SESSION 真源同步回写 + §7 归档

**目的**：归档 §7 降行数到 ≤300；同步 §3/§8 真源；让元测试全绿。

#### E.1 归档 §7（CLI 命令）

```powershell
python -m auto_pm -w "c:\Users\fubai\Desktop\My_Workspace" pm-session archive --section 7 --project-id SW-2026-008
```

**预期**：
- PM_SESSION 主文件从 312 行降至约 296 行
- §7 内容归档到 `00_项目管理\05_PM_SESSION归档\PM_SESSION_SW-2026-008_archive_V1.1.0.md`（或追加到现有归档文件）
- 主文件不再包含 §7 标题

#### E.2 回写 §3 completed（追加 CHG-133 条目）

**目标位置**：PM_SESSION §3 completed 列表，在 CHG-132 条目之后追加 CHG-133 条目。

**操作**：用 Edit 工具在 CHG-132 条目下方插入：
```markdown
  - **CHG-SCPT-2026-133 Modbus 缺陷修复与功能码全量覆盖**（2026-07-19，第 64 次 dogfooding 闭环 closed）：修复 P0 阻断（ModbusDebuggerView.qml 4 处 ComboBox `currentValue` 与 Qt Quick Controls FINAL 属性冲突，重命名为 `_comboValue`）+ 补齐所有缺失功能码（读 FC07/20/22/23/24/43 + 写 FC21/22，共 8 个）+ _MockModbusClient 同步补齐 7 个 mock 方法 + fcCombo 4→11 选项 + writeFcCombo 4→6 选项 + 11 新测试。门禁全绿：ruff 0 + mypy 0 + pytest 36 passed（modbus）。
```

#### E.3 回写 §3 spec_compliance（更新 dogfooding 计数和 last_check）

**操作**：用 Edit 工具更新 §3 spec_compliance：
- `last_check: 2026-07-16` → `last_check: 2026-07-19`
- `dogfooding 61 次闭环` → `dogfooding 64 次闭环`
- 在 CHG-130 后追加 `CHG-131/132/133`

#### E.4 回写 §8 current_state（替换为 CHG-133 状态）

**操作**：用 Edit 工具：
- 现有 `current_state` 行内容 → 改为 2026-07-19 CHG-133 闭环状态描述
- 现有 `current_state_prev` 行 → 改为原 `current_state` 内容（CHG-132 状态）

#### E.5 回写 §0 last_updated（已是 2026-07-19，确认无需修改）

#### E.6 元测试复测

```powershell
python -m pytest tests/test_pm_session_size.py -v --no-cov --tb=short
```

**预期**：9 passed（全绿）。

### 收尾：pm-session check + 最终汇报

**命令**：
```powershell
python -m auto_pm -w "c:\Users\fubai\Desktop\My_Workspace" pm-session check --project-id SW-2026-008
```

**预期**：✅ healthy（无 deprecated_present，无 is_oversized，无 missing_required）。

**最终汇报内容**：
- Phase D2.2 QML 回归结果
- Phase D3 台账对账结果
- Phase D4 三轨门禁结果
- Phase E PM_SESSION 同步+归档结果
- 收尾 pm-session check 结果
- 项目最终健康度评分

## 假设与决策

### 假设
1. 上轮已完成的 Phase A/B/C/D1/D2.1 产出无需返工（已通过实测验证）
2. CHG-133 §1-§12 内容完整无需补充（已实测 221 行）
3. pyproject.toml=1.1.0、CHANGELOG [1.1.0]、PM_SESSION §2 milestone=V1.1.0 三件套已一致
4. 后台任务 job-0cecff30fbef44b4b711d2a3d84040bc 已完成（D21_DONE 标记已出现）

### 决策
1. **不归档 §6**：§6 当前仅 4 条主要记录（10 行），归档收益小；归档 §7（16 行）即可使总行数 312→296 ≤ 300
2. **不归档 §9**：§9 虽占 126 行，但都是 Next Actions 待办，归档会丢失未来工作指引；行数已通过 §7 归档达标
3. **GUI 测试用可见模式**：遵循 project-rule.md 硬约束，设置 `GUI_VISIBLE=1`，不设置 `QT_QPA_PLATFORM=offscreen`
4. **Phase D4 元测试允许失败**：D4 在 Phase E 之前执行，元测试 4 failed 是预期；Phase E 修复后复测应全绿
5. **台账补建用 --auto-fix**：26 条滞后台账已通过 CHG-108 引入的 `LedgerReconciler.auto_fix()` 机制自动补建，无需手工编辑

## 验证步骤

| 步骤 | 命令 | 预期 | 实际 |
|------|------|------|------|
| V1 | `pytest tests/qml/ --no-cov` | ~163 passed | 待执行 |
| V2 | `ledger reconcile SW-2026-008` | 0 差异 | 待执行 |
| V3 | `ruff check auto_pm/` | 0 errors | 待执行 |
| V4 | `mypy auto_pm/` | 0 errors | 待执行 |
| V5 | `pytest tests/test_pm_session_size.py` | 9 passed | 待执行（Phase E 后） |
| V6 | `pm-session check` | healthy | 待执行 |
| V7 | PM_SESSION 行数 | ≤ 300 | 待执行（Phase E 后） |
| V8 | PM_SESSION §7 | 不存在 | 待执行（Phase E 后） |

## 执行顺序与时间预估

| Phase | 预估时间 | 累计 |
|-------|----------|------|
| D2.2 QML 回归 | 1 分钟 | 1 分钟 |
| D3 台账对账 | 30 秒 | 1.5 分钟 |
| D4 三轨门禁 | 2 分钟（ruff 10s + mypy 30s + 元测试 5s + 日志分析） | 3.5 分钟 |
| E PM_SESSION 同步+归档 | 3 分钟（CLI 30s + 4 处 Edit + 元测试复测 5s） | 6.5 分钟 |
| 收尾 pm-session check + 汇报 | 30 秒 | 7 分钟 |

**总预估**：约 7 分钟。

## 执行约束

1. **venv 激活**：每个 PowerShell 会话开始前必须 `& "c:\Users\fubai\Desktop\My_Workspace\.venv\Scripts\Activate.ps1"`
2. **工作目录**：执行 pytest 命令前必须 cd 到项目根目录
3. **Edit 工具使用**：PM_SESSION 修改必须用 Edit 工具，禁止 Python 脚本写磁盘；若 Edit 失败先 Read 再重试，仍失败用 Write 整体覆盖
4. **后台任务监控**：D2.2 QML 测试若超过 60s 未完成，立即读日志诊断；D4 mypy 若超过 90s 未完成，立即读日志
5. **失败处理**：任何 Phase 失败立即用 `--tb=long` 重跑获取完整 traceback，禁止 `--tb=no` 隐藏错误详情
6. **不返工已完成项**：Phase A/B/C/D1/D2.1 已完成且经实测验证，本计划不返工
