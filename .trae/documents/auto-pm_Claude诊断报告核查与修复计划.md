# auto-pm Claude 诊断报告核查与修复计划（续作版）

> 基于已有进度（T1-T6 已完成 + P1 门禁通过）的剩余工作修复计划
> 创建时间：2026-07-08 | 关联变更单：CHG-SCPT-2026-100（状态 implementing）
> 项目：SW-2026-008 auto-pm | 当前版本：0.9.0

---

## 一、摘要

本计划承接前序会话已完成的 T1-T6 整改工作，聚焦剩余的 T7（Optional 统一）、T8（Facade Any 替换 Protocol）、P2 门禁验证和 S-final 收尾闭环。报告核查结论：Claude 第二版诊断报告（19 项问题）整体失真度低，可作为修复基础；T1-T6 已通过 P1 门禁验证（ruff 0 + mypy 8 非阻断 + pytest 1260 passed 2 skipped），剩余 T7/T8 为 P1 级代码质量整改，不涉及运行时阻断。

---

## 二、诊断报告核查结论（报告失真度评估）

### 2.1 报告概况

- **报告位置**：`09_整改项/Claude-result/#auto-pm 项目全面诊断报告（第二版）`
- **诊断时间**：2026-07-08
- **报告版本**：V2 第二版，539 行
- **问题项总数**：19 项（高优先级 6 + 中优先级 8 + 低优先级 5）

### 2.2 失真度分级

| 失真级别 | 数量 | 说明 |
|----------|------|------|
| ✅ 完全真实 | 10 项 | 问题描述与代码实际状态完全一致 |
| ⚠️ 方向真实，数字偏差 | 5 项 | 问题方向正确，但量化数字有偏差 |
| ❌ 细节描述有误 | 1 项 | 具体代码描述与实际不符 |
| 💡 风格建议 | 3 项 | 非问题，仅为改进建议 |

### 2.3 关键数字校正

| 报告项 | 报告数字 | 实际数字 | 偏差说明 |
|--------|----------|----------|----------|
| #3 except Exception | 31 处 / 15 文件 | **69 处 / 22 文件** | 报告低估，实际更严重 |
| #5 setup_logger 硬编码 | 18 处 | **21 处**（含 8 处 `as get_logger` 别名） | 报告低估 |
| #6 parser.py 行数 | 837 行 | **716 行** | 报告高估 |
| #6 change_service.py 行数 | 887 行 | **723 行** | 报告高估 |
| #7 Optional 使用 | 48+ 处 | **50 处 / 12 文件** | 方向真实 |
| #8 Facade Any 参数 | 11 处 | **14 处 / 5 Facade** | 报告低估 |

### 2.4 细节描述有误项

**#frontmatter_svc.py 静默 except**：报告称"完全无异常记录"，实际 L91/L146 已有 `log.warning(..., exc_info=True)`。但其他文件（workbench_facade、system_facade、project_service）确实存在静默 except，方向真实。

### 2.5 核查总结

报告整体可信度高，可作为修复计划基础。数字偏差不影响修复方向，但需以实际 Grep 结果为准。本计划基于实际量化数据制定 T7/T8 范围。

---

## 三、当前状态分析

### 3.1 已完成整改（T1-T6 + P1 门禁）

通过源码验证，以下任务已在前序会话完成：

| 任务 | 验证位置 | 状态 |
|------|----------|------|
| T1 get_project 缓存优先 | [project_service.py](file:///c:\Users\fubai\Desktop\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\02_在研项目\SW-2026-008_auto-pm_自动化项目管理工具\auto_pm\core\project_service.py#L209-L229) L209-229 | ✅ DB 缓存优先降级 |
| T2 DatabaseManager 连接复用 | [connection.py](file:///c:\Users\fubai\Desktop\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\02_在研项目\SW-2026-008_auto-pm_自动化项目管理工具\auto_pm\db\connection.py#L29-L57) L29-57 | ✅ 单例连接 + close() |
| T3 sync.py 委托 | [sync.py](file:///c:\Users\fubai\Desktop\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\02_在研项目\SW-2026-008_auto-pm_自动化项目管理工具\auto_pm\db\sync.py#L239-L248) L239-248 | ✅ 委托 ProjectScanner |
| T4 临时文件清理 + .gitignore | .gitignore | ✅ git rm --cached + 规则补充 |
| T5 setup_logger 标准化 | 21 个模块文件 | ✅ logging.getLogger(__name__) |
| T6 静默 except 整改 | system_facade L75 / workbench_facade L156 / project_service L193,L198 | ✅ 添加 log.warning exc_info=True |

**P1 门禁结果**：ruff check 0 errors + mypy 8 errors（P1/P2 非阻断）+ pytest 1260 passed 2 skipped

### 3.2 CHG-100 状态

- 变更单路径：`00_项目管理/04_变更管理/01_变更单/CHG-SCPT/CHG-SCPT-2026-100.md`
- 当前状态：`implementing`
- §10 实施记录：S0 标 ✅，S1-S10 仍标 ⏳（**实际 S1-S7 已完成，需回填**）
- §11 验证记录：空（待 P2 门禁后填写）
- §12 关闭确认：空（待全部完成后流转 closed）

### 3.3 PM_SESSION 状态

- §3 spec_compliance：停留在 2026-07-07 M5 + CHG-099 QML 编码修复，**未同步 CHG-100**
- §6 Implementation Log：未追加 2026-07-08 CHG-100 条目
- §8 Handoff Notes：未追加 CHG-100 移交条目
- dogfooding 闭环数：当前 29 次，CHG-100 完成后为 30 次

### 3.4 版本号状态

- pyproject.toml：`version = "0.9.0"`
- CHANGELOG：最新条目 [0.9.0]
- 本次为技术债清理（非功能性变更），建议升级 patch 到 **0.9.1**

---

## 四、剩余任务

### T7: 统一 Optional[X] → X | None

**范围**：50 处 / 12 文件（已通过 Grep 验证）

| 文件 | 处数 |
|------|------|
| auto_pm/core/protocols.py | 12 |
| auto_pm/core/project_service.py | 10 |
| auto_pm/change/change_service.py | 6 |
| auto_pm/core/project_scanner.py | 6 |
| auto_pm/change/file_locator.py | 4 |
| auto_pm/spec/core/registry.py | 3 |
| auto_pm/spec/core/scanner.py | 3 |
| auto_pm/logging/logging.py | 2 |
| auto_pm/application/system_facade.py | 1 |
| auto_pm/application/delivery_facade.py | 1 |
| auto_pm/core/report_service.py | 1 |
| auto_pm/cli/gui.py | 1 |

**方案**：
1. 用 Edit `replace_all` 逐文件替换 `Optional[X]` → `X | None`
2. 删除 `from typing import Optional` 导入（如不再使用）
3. 保留 `from __future__ import annotations`（已在大部分文件中）
4. 跑 `ruff check . --fix` 自动整理 import 排序

**注意**：
- system_facade.py L11 `from typing import Any, Optional` → 改为 `from typing import Any`（T8 后 Any 也会被替换）
- protocols.py L13 `from typing import Any, Optional, Protocol, runtime_checkable` → 改为 `from typing import Any, Protocol, runtime_checkable`

**验证**：ruff check 0 errors + mypy 不新增错误 + pytest 全绿

### T8: Facade Any 参数替换为 Protocol

**范围**：14 处 / 5 Facade（已通过 Grep 验证，比报告的 11 处多 3 处）

| Facade 文件 | Any 参数位置 | 建议替换类型 |
|-------------|--------------|--------------|
| workbench_facade.py L25 | `dashboard_service: Any` | `DashboardServiceProtocol` |
| workbench_facade.py L27 | `asset_summary_service: Any` | `AssetSummaryServiceProtocol` |
| system_facade.py L32 | `pm_session_service: Any` | `PmSessionServiceProtocol` |
| system_facade.py L33 | `template_service: Any = None` | `TemplateServiceProtocol \| None = None` |
| spec_facade.py L21 | `spec_check_service: Any = None` | `SpecCheckServiceProtocol \| None = None` |
| spec_facade.py L22 | `spec_center_service: Any = None` | `SpecCenterServiceProtocol \| None = None` |
| delivery_facade.py L29 | `doc_refresh_service: Any = None` | `DocRefreshServiceProtocol \| None = None` |
| delivery_facade.py L30 | `report_service: Any = None` | `ReportServiceProtocol \| None = None` |
| delivery_facade.py L31 | `asset_summary_service: Any = None` | `AssetSummaryServiceProtocol \| None = None` |
| delivery_facade.py L32 | `project_service: Any = None` | `ProjectServiceProtocol \| None = None`（已存在） |
| change_facade.py L29 | `_summary_to_dto(summary: Any)` | `ChangeSummary`（具体类型） |
| change_facade.py L44 | `_request_to_dto(cr: Any)` | `ChangeRequest`（具体类型） |

**方案**：
1. 在 `auto_pm/core/protocols.py` 新增 7 个 Protocol 定义：
   - `DashboardServiceProtocol`
   - `AssetSummaryServiceProtocol`
   - `PmSessionServiceProtocol`
   - `TemplateServiceProtocol`
   - `SpecCheckServiceProtocol`
   - `SpecCenterServiceProtocol`
   - `DocRefreshServiceProtocol`
   - `ReportServiceProtocol`（如已存在则复用）
2. 5 个 Facade 的 `__init__` 参数类型替换
3. change_facade.py 私有方法参数改为具体类型 `ChangeSummary` / `ChangeRequest`
4. 检查 delivery_facade.py L32 `project_service` 是否可复用已存在的 `ProjectServiceProtocol`

**验证**：
- ruff check 0 errors
- mypy 不新增错误（Protocol 是结构性类型，现有 Service 实现无需显式继承）
- pytest 全绿（Protocol `@runtime_checkable` 支持 isinstance 检查，但不影响运行时）

### P2 门禁

```powershell
# 激活虚拟环境
& "c:\Users\fubai\Desktop\My_Workspace\.venv\Scripts\Activate.ps1"

# 三轨门禁
ruff check .                    # 期望: 0 errors
mypy auto_pm/                   # 期望: ≤ 8 errors（目标 ≤ 3）
pytest --no-cov -x              # 期望: ≥ 1260 passed 2 skipped
```

**门禁标准**：
- ruff 必须 0 errors
- mypy ≤ 8 errors（P1/P2 非阻断，与 P1 门禁基线一致）
- pytest ≥ 1260 passed（不低于基线）

### S-final: 收尾闭环

#### S1: 回填 CHG-100 实施记录

更新 `CHG-SCPT-2026-100.md`：

- §10 实施记录：S1-S7 标 ✅（T4/T3/T5/T1/T2/P1门禁/T6）+ S8-S10 实施后标 ✅（T7/T8/P2门禁）
- §11 验证记录：填写 P2 门禁三轨结果
- §12 关闭确认：填关闭日期、关闭人、关闭理由、后续行动
- §3.4 变更状态：`implementing` → `closed`

#### S2: PM_SESSION 同步

更新 `PM_SESSION_SW-2026-008.md`：

- §3 spec_compliance：追加 CHG-100 闭环条目（dogfooding 29→30 次闭环）
- §6 Implementation Log：追加 2026-07-08 CHG-100 条目（T1-T8 整改 + 三轨门禁结果）
- §8 Handoff Notes：追加 `skill_handoff_20260708_chg100`（版本号、剩余 TODO、下一步建议）

#### S3: 版本号同步（推荐升级到 0.9.1）

- `pyproject.toml`：`version = "0.9.0"` → `"0.9.1"`
- `CHANGELOG.md`：新增 `[0.9.1]` 条目（技术债清理：DB 连接复用 + get_project 缓存优先 + setup_logger 标准化 + Optional 统一 + Facade Any 替换 Protocol）

---

## 五、可选任务（T9-T12，需用户批准）

以下任务为报告中的低优先级建议，**不在本次闭环范围内**，如需纳入请单独批准：

- **T9**: ServiceContainer 重构（FacadeRegistry.initialize 改用类型安全容器，对应报告 #9）
- **T10**: TODO 登记（散落的 # TODO M3/M4/M5 集中到 issue tracker）
- **T11**: model_copy 替换深拷贝（Pydantic v2 推荐）
- **T12**: .gitignore 完善（补充 IDE 配置、缓存文件等）

---

## 六、执行顺序

```
Phase 2 (P1 剩余):
  T7 Optional 统一 (50 处/12 文件) ──┐
                                    ├─ 并行（独立文件）
  T8 Facade Any 替换 (14 处/5 Facade) ┘
  ↓
  P2 门禁 (ruff + mypy + pytest)
  ↓
Phase 3 (收尾):
  S-final: CHG-100 closed + PM_SESSION 同步 + CHANGELOG + pyproject 版本号
```

**关键依赖**：
- T7 和 T8 可并行（修改不同文件，唯一交叉点是 protocols.py：T7 删 Optional，T8 新增 Protocol 定义）
- 若并行，建议先做 T8 的 protocols.py 新增 Protocol，再做 T7 的 Optional 删除，避免 import 冲突
- P2 门禁必须在 T7+T8 都完成后执行
- S-final 必须在 P2 门禁通过后执行

---

## 七、验证步骤

### 7.1 T7 验证

```powershell
# 替换后验证
ruff check .                          # 期望 0 errors（含 F401 未使用导入）
grep -r "Optional\[" auto_pm/         # 期望 0 处
grep -r "from typing import.*Optional" auto_pm/  # 期望 0 处（或仅在兼容场景）
```

### 7.2 T8 验证

```powershell
# 替换后验证
ruff check .                          # 期望 0 errors
mypy auto_pm/application/             # 期望不新增错误
grep -n ": Any" auto_pm/application/*_facade.py  # 期望 0 处（change_facade 私有方法除外）
```

### 7.3 P2 门禁

```powershell
ruff check .                          # 期望 0 errors
mypy auto_pm/                         # 期望 ≤ 8 errors
pytest --no-cov -x                    # 期望 ≥ 1260 passed 2 skipped
```

### 7.4 S-final 验证

- CHG-100 §10 全部 ✅，§11 填写完整，§12 关闭确认，§3.4 状态为 closed
- PM_SESSION §3 spec_compliance 包含 CHG-100 条目，dogfooding 30 次闭环
- PM_SESSION §6 包含 2026-07-08 CHG-100 条目
- PM_SESSION §8 包含 skill_handoff_20260708_chg100
- pyproject.toml version = "0.9.1"
- CHANGELOG.md 包含 [0.9.1] 条目

---

## 八、假设与决策

### 8.1 假设

1. **P1 门禁基线可信**：前序会话 P1 门禁结果（ruff 0 + mypy 8 + pytest 1260 passed 2 skipped）真实有效，本计划基于此基线推进
2. **T1-T6 改动已持久化**：通过源码验证（connection.py / project_service.py / sync.py / system_facade.py / workbench_facade.py），改动已在磁盘上
3. **Protocol 结构性类型兼容**：现有 Service 实现无需显式继承 Protocol，T8 替换后运行时行为不变
4. **`from __future__ import annotations` 已存在**：T7 替换 `Optional[X]` → `X | None` 在运行时不会触发 TypeError

### 8.2 决策

| 决策项 | 选择 | 理由 |
|--------|------|------|
| T7/T8 执行顺序 | 并行（protocols.py 先 T8 后 T7） | 独立文件可并行，protocols.py 交叉点先加 Protocol 再删 Optional |
| 版本号升级 | 0.9.0 → 0.9.1 | 技术债清理属于 patch 级别，符合 SemVer |
| T9-T12 纳入 | 不纳入 | 低优先级，避免范围蔓延，留待后续迭代 |
| mypy 目标 | ≤ 8 errors（与 P1 基线一致） | P1/P2 非阻断，不强制降至 0 |
| 批量替换工具 | Edit replace_all + ruff --fix | 避免引入 Python 脚本写磁盘（项目规则禁止） |

### 8.3 风险

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| T7 替换遗漏 Optional 导入导致 F401 | 中 | 低 | ruff check 自动捕获 + --fix |
| T8 Protocol 定义不全（方法签名不匹配） | 中 | 中 | 优先复用已存在 Protocol，新增 Protocol 仅定义 Facade 实际调用的方法 |
| T8 后 mypy 新增 attr-defined 错误 | 中 | 低 | Protocol 方法签名必须与 Service 实现一致，不一致时补充方法到 Protocol |
| 并行执行导致 protocols.py 冲突 | 低 | 低 | 先做 T8 新增 Protocol，再做 T7 删 Optional |
| CHG-100 回填遗漏 | 低 | 低 | 按 §10/§11/§12/§3.4 清单逐项核对 |

---

## 九、文件清单

### 9.1 待修改文件（T7 + T8）

**T7（12 文件）**：
- auto_pm/core/protocols.py
- auto_pm/core/project_service.py
- auto_pm/change/change_service.py
- auto_pm/core/project_scanner.py
- auto_pm/change/file_locator.py
- auto_pm/spec/core/registry.py
- auto_pm/spec/core/scanner.py
- auto_pm/logging/logging.py
- auto_pm/application/system_facade.py
- auto_pm/application/delivery_facade.py
- auto_pm/core/report_service.py
- auto_pm/cli/gui.py

**T8（6 文件，protocols.py 与 T7 重叠）**：
- auto_pm/core/protocols.py（新增 7 个 Protocol 定义）
- auto_pm/application/workbench_facade.py
- auto_pm/application/system_facade.py（与 T7 重叠）
- auto_pm/application/spec_facade.py
- auto_pm/application/delivery_facade.py（与 T7 重叠）
- auto_pm/application/change_facade.py

### 9.2 待修改文件（S-final）

- 00_项目管理/04_变更管理/01_变更单/CHG-SCPT/CHG-SCPT-2026-100.md
- PM_SESSION_SW-2026-008.md
- pyproject.toml
- CHANGELOG.md

---

## 十、TodoList

执行阶段将按以下 TodoList 推进：

- [ ] T7: 统一 Optional[X] → X | None (50 处/12 文件)
- [ ] T8: Facade Any 参数替换为 Protocol (14 处/5 Facade + protocols.py 新增 7 Protocol)
- [ ] P2 门禁: ruff + mypy + pytest 回归验证
- [ ] S-final: CHG-100 closed + PM_SESSION §3/§6/§8 同步 + CHANGELOG + pyproject 0.9.1
