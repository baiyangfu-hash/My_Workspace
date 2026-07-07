# auto-pm Claude 诊断修复 - 剩余执行计划

> 承接前序会话：T1-T6 + P1 门禁 + T8-step1 已完成，聚焦 T7/T8-step2/P2/S-final
> 创建时间：2026-07-08 | 关联变更单：CHG-SCPT-2026-100（状态 implementing）
> 项目：SW-2026-008 auto-pm | 当前版本：0.9.0 → 目标 0.9.1

---

## 一、当前状态基线（已通过源码验证）

### 1.1 已完成（前序会话）

| 任务 | 验证结果 |
|------|----------|
| T1-T6 整改（缓存优先/连接复用/sync 委托/临时文件/setup_logger/静默 except） | ✅ 已落盘 |
| P1 门禁（ruff 0 + mypy 8 非阻断 + pytest 1260 passed 2 skipped） | ✅ 通过 |
| T8-step1：protocols.py 新增 8 个 Protocol + 删除 Optional | ✅ 完成 |

**protocols.py 当前状态**：13 个 Protocol 类（原 5 + 新 8），无 Optional 导入，使用 `X | None` 语法。

### 1.2 剩余工作（本计划范围）

| 任务 | 范围 | 状态 |
|------|------|------|
| T7：Optional[X] → X \| None | 38 处 / 11 文件 | ⏳ 待执行 |
| T8-step2：Facade Any → Protocol/具体类型 | 14 处 / 5 Facade | ⏳ 待执行 |
| P2 门禁 | ruff + mypy + pytest | ⏳ 待执行 |
| S-final：CHG-100 closed + PM_SESSION 同步 + 版本号 | 4 文件 | ⏳ 待执行 |

---

## 二、诊断报告核查结论（失真度评估）

Claude 第二版诊断报告（19 项问题）整体失真度低，可作为修复基础：

| 失真级别 | 数量 | 说明 |
|----------|------|------|
| ✅ 完全真实 | 10 项 | 描述与代码一致 |
| ⚠️ 方向真实，数字偏差 | 5 项 | 方向对，数字有偏差（见下表） |
| ❌ 细节描述有误 | 1 项 | frontmatter_svc.py 实际已有 exc_info=True |
| 💡 风格建议 | 3 项 | 非问题 |

**关键数字校正**（以实际 Grep 为准）：

| 报告项 | 报告数字 | 实际数字 |
|--------|----------|----------|
| except Exception | 31 处/15 文件 | **69 处/22 文件** |
| setup_logger 硬编码 | 18 处 | **21 处** |
| parser.py 行数 | 837 行 | **716 行** |
| Optional 使用 | 48+ 处 | **50 处/12 文件**（protocols.py 12 处已清除，剩 38 处/11 文件） |
| Facade Any 参数 | 11 处 | **14 处/5 Facade** |

**核查总结**：报告可信度高，数字偏差不影响修复方向。T7/T8 范围以实际 Grep 结果为准。

---

## 三、T7：Optional[X] → X | None（38 处 / 11 文件）

### 3.1 范围（已通过 Grep 验证）

| 文件 | Optional[ 处数 | from typing 行 |
|------|----------------|----------------|
| auto_pm/core/project_service.py | 10 | L19: `from typing import Any, Optional, cast` |
| auto_pm/change/change_service.py | 6 | L18: `from typing import TYPE_CHECKING, Any, Optional` |
| auto_pm/core/project_scanner.py | 6 | L17: `from typing import Optional` |
| auto_pm/change/file_locator.py | 4 | L23: `from typing import Optional` |
| auto_pm/spec/core/registry.py | 3 | L6: `from typing import Any, Optional` |
| auto_pm/spec/core/scanner.py | 3 | L5: `from typing import Any, Optional` |
| auto_pm/logging/logging.py | 2 | L5: `from typing import Optional` |
| auto_pm/application/system_facade.py | 1 | L11: `from typing import Any, Optional` |
| auto_pm/application/delivery_facade.py | 1 | L10: `from typing import Any, Optional` |
| auto_pm/core/report_service.py | 1 | L22: `from typing import Any, Optional` |
| auto_pm/cli/gui.py | 1 | L18: `from typing import Optional` |

### 3.2 执行方案

**关键策略调整（基于前序会话教训）**：
- ❌ 不用 Edit `replace_all`（前序会话验证发现对 `Optional[X]` 模式不可靠，反馈成功但实际未替换）
- ✅ 用 Write 工具逐文件整体重写（可靠，且能同步 VS Code 缓冲区）
- ✅ 大文件（project_service 703 行 / change_service 843 行 / project_scanner 623 行）也用 Write 重写

**替换规则**：
1. `Optional[X]` → `X | None`
2. 删除 `from typing import` 中的 `Optional`（如该行还有其他导入，仅删 Optional）
3. 如 `Optional` 是该行唯一导入，删除整行
4. 保留 `from __future__ import annotations`（所有 11 文件均已存在，运行时安全）

**特殊文件处理**：
- `auto_pm/cli/gui.py` L? `Optional[TracebackType]` → `TracebackType | None`（需确认 `types` 模块导入）
- `auto_pm/change/file_locator.py` 4 处需逐一确认上下文

### 3.3 T7 + T8 合并文件

以下 2 个 Facade 文件同时有 T7（Optional）和 T8（Any）工作，**一次性合并处理**：

- **system_facade.py**：1 Optional + 2 Any（pm_session_service, template_service）
- **delivery_facade.py**：1 Optional + 4 Any（doc_refresh, report, asset_summary, project_service）

---

## 四、T8-step2：Facade Any → Protocol/具体类型（14 处 / 5 Facade）

### 4.1 范围（已通过 Grep 验证）

| Facade 文件 | Any 位置 | 替换为 |
|-------------|----------|--------|
| workbench_facade.py L25 | `dashboard_service: Any` | `DashboardServiceProtocol` |
| workbench_facade.py L27 | `asset_summary_service: Any` | `AssetSummaryServiceProtocol` |
| system_facade.py L32 | `pm_session_service: Any` | `PmSessionServiceProtocol` |
| system_facade.py L33 | `template_service: Any = None` | `TemplateServiceProtocol \| None = None` |
| system_facade.py L52 | `-> Optional[Any]` | `-> ProjectInfo \| None` |
| spec_facade.py L21 | `spec_check_service: Any = None` | `SpecCheckServiceProtocol \| None = None` |
| spec_facade.py L22 | `spec_center_service: Any = None` | `SpecCenterServiceProtocol \| None = None` |
| delivery_facade.py L29 | `doc_refresh_service: Any = None` | `DocRefreshServiceProtocol \| None = None` |
| delivery_facade.py L30 | `report_service: Any = None` | `ReportServiceProtocol \| None = None` |
| delivery_facade.py L31 | `asset_summary_service: Any = None` | `AssetSummaryServiceProtocol \| None = None` |
| delivery_facade.py L32 | `project_service: Any = None` | `ProjectServiceProtocol \| None = None` |
| delivery_facade.py L55 | `-> Optional[Any]` | `-> ProjectInfo \| None` |
| change_facade.py L29 | `_summary_to_dto(summary: Any)` | `summary: ChangeSummary` |
| change_facade.py L44 | `_request_to_dto(cr: Any)` | `cr: ChangeRequest` |

### 4.2 执行方案

**Protocol 定义已在 T8-step1 完成**（protocols.py 已有 13 个 Protocol，含所需的 8 个新 Protocol）。

**每个 Facade 的改动**：

1. **workbench_facade.py**：
   - L4 `from typing import Any` → 删除整行
   - L6 扩展导入：`from auto_pm.core.protocols import AssetSummaryServiceProtocol, DashboardServiceProtocol, ProjectServiceProtocol`
   - L25/L27 替换 Any

2. **system_facade.py**（T7+T8 合并）：
   - L11 删除 `from typing import Any, Optional` 整行
   - L15 扩展导入：新增 `PmSessionServiceProtocol, TemplateServiceProtocol`
   - L32/L33 替换 Any
   - L52 `Optional[Any]` → `ProjectInfo | None`（需新增 `from auto_pm.models import ProjectInfo`）

3. **spec_facade.py**：
   - L6 删除 `from typing import Any` 整行
   - 新增 `from auto_pm.core.protocols import SpecCheckServiceProtocol, SpecCenterServiceProtocol`
   - L21/L22 替换 Any

4. **delivery_facade.py**（T7+T8 合并）：
   - L10 删除 `from typing import Any, Optional` 整行
   - 新增 Protocol 和 ProjectInfo 导入
   - L29-32 替换 4 个 Any
   - L55 `Optional[Any]` → `ProjectInfo | None`

5. **change_facade.py**：
   - L3 删除 `from typing import Any` 整行
   - L5 已有 `from auto_pm.core.protocols import ChangeServiceProtocol`
   - 新增 `from auto_pm.models import ChangeRequest, ChangeSummary`（或从 `auto_pm.change.models` 导入）
   - L29/L44 私有方法参数 Any → 具体类型

---

## 五、P2 门禁

### 5.1 执行命令

```powershell
# 激活虚拟环境（强制）
& "c:\Users\fubai\Desktop\My_Workspace\.venv\Scripts\Activate.ps1"

# 三轨门禁
ruff check .                    # 期望: 0 errors
mypy auto_pm/                   # 期望: ≤ 8 errors（P1/P2 非阻断，与 P1 基线一致）
pytest --no-cov -x              # 期望: ≥ 1260 passed 2 skipped
```

### 5.2 门禁标准

- ruff 必须 0 errors（含 F401 未使用导入自动捕获）
- mypy ≤ 8 errors（不强制降至 0，与 P1 基线一致）
- pytest ≥ 1260 passed（不低于 P1 基线）

### 5.3 失败处理

- ruff 失败：跑 `ruff check . --fix` 自动整理 import，再重跑
- mypy 新增错误：检查 Protocol 方法签名是否与 Service 实现一致，不一致则补充方法到 Protocol
- pytest 失败：用 `--tb=long` 获取完整 traceback，定位是替换引入的回归还是 fixture 问题

---

## 六、S-final：收尾闭环

### 6.1 S1: 回填 CHG-100

更新 `00_项目管理/04_变更管理/01_变更单/CHG-SCPT/CHG-SCPT-2026-100.md`：

- §10 实施记录：S1-S7 标 ✅（T4/T3/T5/T1/T2/P1门禁/T6）+ S8-S10 标 ✅（T7/T8/P2门禁）
- §11 验证记录：填写 P2 门禁三轨结果（ruff/mypy/pytest 实际数字）
- §12 关闭确认：填关闭日期 2026-07-08、关闭人、关闭理由、后续行动
- §3.4 变更状态：`implementing` → `closed`

### 6.2 S2: PM_SESSION 同步

更新 `PM_SESSION_SW-2026-008.md`：

- §3 spec_compliance：追加 CHG-100 闭环条目（dogfooding 29→30 次闭环）
- §6 Implementation Log：追加 2026-07-08 CHG-100 条目（T1-T8 整改 + 三轨门禁结果）
- §8 Handoff Notes：追加 `skill_handoff_20260708_chg100`（版本号 0.9.1、剩余 TODO、下一步建议）

### 6.3 S3: 版本号同步

- `pyproject.toml`：`version = "0.9.0"` → `"0.9.1"`
- `CHANGELOG.md`：新增 `[0.9.1]` 条目（技术债清理：DB 连接复用 + get_project 缓存优先 + setup_logger 标准化 + Optional 统一 + Facade Any 替换 Protocol）

---

## 七、执行顺序

```
Step 1: T7 纯 Optional 文件（9 个，无 T8 交叉）
  - project_service.py (10处)
  - change_service.py (6处)
  - project_scanner.py (6处)
  - file_locator.py (4处)
  - registry.py (3处)
  - scanner.py (3处)
  - logging.py (2处)
  - report_service.py (1处)
  - gui.py (1处)
  ↓
Step 2: T7+T8 合并文件（2 个 Facade）
  - system_facade.py (1 Optional + 2 Any)
  - delivery_facade.py (1 Optional + 4 Any)
  ↓
Step 3: T8 纯 Any 文件（3 个 Facade）
  - workbench_facade.py (2 Any)
  - spec_facade.py (2 Any)
  - change_facade.py (2 Any)
  ↓
Step 4: ruff check . --fix（自动整理 import 排序）
  ↓
Step 5: P2 门禁（ruff + mypy + pytest）
  ↓
Step 6: S-final（CHG-100 closed + PM_SESSION + CHANGELOG + pyproject）
```

**执行顺序说明**：
- Step 1-3 可顺序执行（每个文件独立，避免并行冲突）
- Step 4 必须在 Step 1-3 全部完成后执行
- Step 5 必须在 Step 4 后执行
- Step 6 必须在 Step 5 门禁通过后执行

---

## 八、假设与决策

### 8.1 假设

1. **P1 门禁基线可信**：ruff 0 + mypy 8 + pytest 1260 passed 2 skipped
2. **T1-T6 + T8-step1 改动已持久化**：通过源码验证（protocols.py 已有 13 Protocol，无 Optional）
3. **Protocol 结构性类型兼容**：Service 无需显式继承，T8 替换后运行时行为不变
4. **`from __future__ import annotations` 已存在**：T7 替换 `X | None` 运行时安全

### 8.2 决策

| 决策项 | 选择 | 理由 |
|--------|------|------|
| 替换工具 | Write 整体重写 | Edit replace_all 对 Optional 模式不可靠（前序会话验证） |
| 版本号升级 | 0.9.0 → 0.9.1 | 技术债清理属 patch 级别 |
| T9-T12 纳入 | 不纳入 | 低优先级，避免范围蔓延 |
| mypy 目标 | ≤ 8 errors | 与 P1 基线一致，不强制降至 0 |
| T7+T8 合并文件 | 一次性处理 | system_facade/delivery_facade 同时有 Optional 和 Any，合并避免重复读写 |

### 8.3 风险

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| Write 重写遗漏 Optional 导入导致 F401 | 中 | 低 | ruff check 自动捕获 + --fix |
| T8 Protocol 方法签名不匹配 Service | 中 | 中 | 优先复用已存在 Protocol，新增 Protocol 仅定义 Facade 实际调用的方法 |
| T8 后 mypy 新增 attr-defined 错误 | 中 | 低 | Protocol 方法签名必须与 Service 一致，不一致时补充方法 |
| gui.py TracebackType 导入问题 | 低 | 低 | 替换前确认 `from types import TracebackType` 已存在 |
| CHG-100 回填遗漏 | 低 | 低 | 按 §10/§11/§12/§3.4 清单逐项核对 |

---

## 九、文件清单

### 9.1 待修改文件（T7 + T8-step2，共 14 文件）

**T7 纯 Optional（9 文件）**：
- auto_pm/core/project_service.py
- auto_pm/change/change_service.py
- auto_pm/core/project_scanner.py
- auto_pm/change/file_locator.py
- auto_pm/spec/core/registry.py
- auto_pm/spec/core/scanner.py
- auto_pm/logging/logging.py
- auto_pm/core/report_service.py
- auto_pm/cli/gui.py

**T7+T8 合并（2 文件）**：
- auto_pm/application/system_facade.py
- auto_pm/application/delivery_facade.py

**T8 纯 Any（3 文件）**：
- auto_pm/application/workbench_facade.py
- auto_pm/application/spec_facade.py
- auto_pm/application/change_facade.py

### 9.2 待修改文件（S-final，4 文件）

- 00_项目管理/04_变更管理/01_变更单/CHG-SCPT/CHG-SCPT-2026-100.md
- PM_SESSION_SW-2026-008.md
- pyproject.toml
- CHANGELOG.md

---

## 十、TodoList

执行阶段将按以下 TodoList 推进：

- [ ] T7-step1: 9 个纯 Optional 文件替换（Write 整体重写）
- [ ] T7-step2: 2 个 T7+T8 合并 Facade 文件（system_facade + delivery_facade）
- [ ] T8-step3: 3 个纯 Any Facade 文件（workbench + spec + change）
- [ ] P2 门禁: ruff check + mypy + pytest 回归验证
- [ ] S-final: CHG-100 closed + PM_SESSION §3/§6/§8 同步 + CHANGELOG + pyproject 0.9.1
