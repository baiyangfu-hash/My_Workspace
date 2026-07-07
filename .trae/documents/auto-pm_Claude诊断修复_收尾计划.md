# auto-pm Claude 诊断修复 - 收尾计划

> 承接前序会话：T1-T8 已全部落盘，聚焦 P2 门禁验证 + S-final 闭环
> 创建时间：2026-07-08 | 关联变更单：CHG-SCPT-2026-100（状态 implementing）
> 项目：SW-2026-008 auto-pm | 当前版本：0.9.0 → 目标 0.9.1

---

## 一、当前状态基线（已通过源码 + Grep 验证）

### 1.1 Claude 诊断报告失真度评估

Claude 第二版诊断报告（19 项问题，2026-07-08）基于**修复前**状态生成。经源码核查，**8 项 P0/P1 高优先级问题已全部修复**，报告整体失真度高（与当前状态不符）。

#### 已修复（报告未更新，实际已解决）

| 报告编号 | 问题 | 报告状态 | 实际状态 | 验证方法 |
|----------|------|----------|----------|----------|
| #1 | `get_project()` O(n) 全量扫描 | 未修复 | ✅ 已修复 | `project_service.py` L209-229 已实现 DB 优先 + 文件扫描降级 |
| #2 | `DatabaseManager` 每次创建新连接 | 未修复 | ✅ 已修复 | `connection.py` L39-51 已实现单例连接复用 |
| #4 | `_get_project_mtime` 三处重复 | 未修复 | ✅ 已修复 | `sync.py` L239-248 已委托给 `ProjectScanner.get_project_mtime` |
| #5 | `setup_logger` 硬编码 18 处 | 未修复 | ✅ 已修复 | Grep `setup_logger\(log_level` = 0 matches |
| #7 | `Optional[X]` 混用 48+ 处 | 未修复 | ✅ 已修复 | Grep `Optional\[` = 0 matches |
| #8 | Facade `Any` 参数 11 处 | 未修复 | ✅ 已修复 | 5 Facade 已使用 Protocol 类型 |
| #11 | 5 个临时文件已入库 | 未修复 | ✅ 已修复 | `git ls-files` 筛选 bak_v060/claude_plan/pytest_nongui_result = 空 |
| #17 | `.gitignore` 缺规则 | 未修复 | ✅ 已修复 | `.gitignore` L73-75 已有 `*.bak_`/`pytest_*.txt`/`claude_plan` |

#### 部分修复

| 报告编号 | 问题 | 报告状态 | 实际状态 | 说明 |
|----------|------|----------|----------|------|
| #3 | `except Exception` 31 处/15 文件 | 未修复 | 部分修复 | T6 仅处理了静默吞错（return 0/pass），宽泛 except 仍 70 处/22 文件 |

#### 仍未修复（低优先级，不在本次 CHG-100 范围）

| 报告编号 | 问题 | 实际状态 | 优先级 |
|----------|------|----------|--------|
| #6 | `parser.py` 过大 | 716 行（报告说 837 行，偏低 121 行） | P3 |
| #12 | `ProjectInfo` 原地修改属性 | 9 处仍存在（L100/102/106/108/117/118/199/455/456） | P2 |
| #18 | `change_service.py` 偏大 | 723 行（报告说 887 行，偏低 164 行） | P3 |
| #19 | 7 个冗余向后兼容委托方法 | 需验证 | P4 |

#### 数字偏差汇总

| 报告项 | 报告数字 | 实际数字 | 失真方向 |
|--------|----------|----------|----------|
| except Exception | 31 处/15 文件 | 70 处/22 文件 | 严重偏低 |
| setup_logger | 18 处 | 0 处 | 已修复 |
| parser.py 行数 | 837 行 | 716 行 | 偏低 121 行 |
| Optional | 48+ 处 | 0 处 | 已修复 |
| Facade Any | 11 处 | 0 处 | 已修复 |
| change_service.py 行数 | 887 行 | 723 行 | 偏低 164 行 |

**核查结论**：Claude 报告基于修复前状态生成，P0/P1 高优先级问题已全部解决。本次仅需完成 P2 门禁验证 + S-final 闭环即可关闭 CHG-100。剩余未修复项（#3 剩余部分、#6、#12、#18、#19）属低优先级，建议列入后续迭代，不在本次范围。

### 1.2 已落盘代码改动（T1-T8，前序会话完成）

| 任务 | 文件 | 验证结果 |
|------|------|----------|
| T1: get_project 缓存优先 | `auto_pm/core/project_service.py` L209-229 | ✅ DB 优先 + 文件扫描降级 |
| T2: DB 连接复用 | `auto_pm/db/connection.py` L39-51 | ✅ 单例连接 + close() 方法 |
| T3: sync 委托 | `auto_pm/db/sync.py` L239-248 | ✅ 委托 ProjectScanner.get_project_mtime |
| T4: 临时文件清理 + .gitignore | `.gitignore` L73-75 | ✅ 3 条规则 + git ls-files 空 |
| T5: setup_logger 标准化 | 13+ 模块文件 | ✅ Grep 0 matches |
| T6: 静默 except 整改 | workbench/system/project_service/frontmatter_svc | ✅ 已添加 log.warning |
| T7: Optional 统一 | 11 文件 38 处 | ✅ Grep 0 matches |
| T8: Facade Any → Protocol | 5 Facade + protocols.py + registry.py | ✅ 已使用 Protocol 类型 |

**Protocol 扩展**（protocols.py）：
- ProjectServiceProtocol 新增 `get_project_cached`/`workspace_root`/`clear_cache`
- ChangeServiceProtocol.transition_status 新增 `allow_partial_verification`
- ChangeServiceProtocol.list_all_changes 新增 `urgency`/`project_id`
- 新增 8 个 Protocol：DashboardService/AssetSummaryService/PmSessionService/Template/SpecCheck/SpecCenter/DocRefresh/Report

**registry.py 类型修复**：
- 4 处 `services.get(...)` 包裹 `cast()` 转换为 Protocol 类型
- `__init__(self)` → `__init__(self) -> None`

### 1.3 待完成工作

| 任务 | 范围 | 状态 |
|------|------|------|
| **P2 门禁验证** | ruff + mypy + pytest 三轨 | ⏳ 待执行（前序会话修复完成但未验证） |
| **S-final 闭环** | CHG-100 回填 + PM_SESSION 同步 + 版本号 | ⏳ 待执行 |

---

## 二、P2 门禁验证

### 2.1 执行命令

```powershell
# 激活虚拟环境（强制）
& "c:\Users\fubai\Desktop\My_Workspace\.venv\Scripts\Activate.ps1"

cd "c:\Users\fubai\Desktop\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\02_在研项目\SW-2026-008_auto-pm_自动化项目管理工具"

# 三轨门禁
ruff check .                    # 期望: 0 errors
mypy auto_pm/                   # 期望: ≤ 8 errors（P1/P2 非阻断，与基线一致）
pytest --no-cov -x              # 期望: ≥ 1260 passed 2 skipped
```

### 2.2 门禁标准

- **ruff**: 必须 0 errors（含 F401 未使用导入自动捕获）
- **mypy**: ≤ 8 errors（不强制降至 0，与 P1 基线一致；前序会话已修复 Protocol 不完整和 registry.py 类型问题）
- **pytest**: ≥ 1260 passed 2 skipped（不低于 P1 基线）

### 2.3 失败处理策略

| 失败场景 | 处理方法 |
|----------|----------|
| ruff 失败 | `ruff check . --fix` 自动整理 import，再重跑 |
| mypy 新增错误 | 检查 Protocol 方法签名是否与 Service 实现一致，不一致则补充方法到 Protocol |
| pytest 失败 | 用 `--tb=long` 获取完整 traceback，定位是 T7/T8 引入的回归还是 fixture 问题 |
| pytest 污染 | 参考 §8 skill_handoff_20260708_qml_fix 记录的 7 个 CLI JSON 失败（预先存在，非本次回归） |

### 2.4 预期 mypy 剩余 errors（基线 8 个）

前序会话修复了 11 个新增 errors（Protocol 补充方法 + registry.py cast），预期剩余 ≤ 8 个 pre-existing：
- change_list_model unreachable
- delivery_facade 4 unreachable
- qml_main_window untyped call
- 其他 P1/P2 类型注解问题

---

## 三、S-final：CHG-100 闭环收尾

### 3.1 S1: 回填 CHG-100 §10 实施记录

**文件**：`00_项目管理/04_变更管理/01_变更单/CHG-SCPT/CHG-SCPT-2026-100.md`

**当前状态**（失真）：§10 表格 S1-S10 全部标 ⏳，与实际 T1-T8 已完成不符。

**回填内容**：

| 步骤 | 任务 | 开始时间 | 完成时间 | 状态 | 备注 |
|------|------|----------|----------|------|------|
| S0 | 创建 CHG-100 + 基线测试 | 2026-07-08 | 2026-07-08 | ✅ | 基线: ruff 0 + mypy 8 (非阻断) + pytest 待测 |
| S1 | T4 清理临时文件 + .gitignore | 2026-07-08 | 2026-07-08 | ✅ | git ls-files 筛选 bak_v060/claude_plan/pytest_nongui_result = 空 |
| S2 | T3 sync 委托 | 2026-07-08 | 2026-07-08 | ✅ | sync.py L239-248 委托 ProjectScanner.get_project_mtime |
| S3 | T5 setup_logger 标准化 | 2026-07-08 | 2026-07-08 | ✅ | Grep setup_logger(log_level = 0 matches |
| S4 | T1 get_project 缓存优先 | 2026-07-08 | 2026-07-08 | ✅ | project_service.py L209-229 DB 优先 + 文件扫描降级 |
| S5 | T2 DB 连接复用 | 2026-07-08 | 2026-07-08 | ✅ | connection.py L39-51 单例连接 + close() |
| S6 | P1 门禁 (ruff + mypy + pytest) | 2026-07-08 | 2026-07-08 | ✅ | ruff 0 + mypy 8 + pytest 1260 passed 2 skipped |
| S7 | T6 静默 except 整改 | 2026-07-08 | 2026-07-08 | ✅ | workbench/system/project_service/frontmatter_svc 已添加 log.warning |
| S8 | T7 Optional 统一 | 2026-07-08 | 2026-07-08 | ✅ | Grep Optional[ = 0 matches（11 文件 38 处替换） |
| S9 | T8 Facade Any 替换 | 2026-07-08 | 2026-07-08 | ✅ | 5 Facade + protocols.py 扩展 + registry.py cast |
| S10 | P2 门禁 + 最终回归 | 2026-07-08 | 2026-07-08 | ✅ | 填写实际三轨数字 |

### 3.2 S2: 回填 CHG-100 §11 验证记录

填写 P2 门禁三轨实际结果（从 §二 执行后获取）：

```markdown
## 11. 验证记录

### 11.1 P1 门禁（T1-T6 完成后）
- ruff check .: 0 errors ✅
- mypy auto_pm/: 8 errors in 5 files（P1/P2 非阻断，与基线一致）✅
- pytest --no-cov -x: 1260 passed, 2 skipped ✅

### 11.2 P2 门禁（T7-T8 完成后）
- ruff check .: 0 errors ✅（填写实际数字）
- mypy auto_pm/: X errors（填写实际数字）✅
- pytest --no-cov -x: X passed, 2 skipped ✅（填写实际数字）

### 11.3 修复项验证
- get_project 缓存优先：✅ project_service.py L218-222 DB 优先分支
- DB 连接复用：✅ connection.py L45-51 单例连接
- sync 委托：✅ sync.py L246-248 委托 ProjectScanner
- setup_logger 标准化：✅ Grep 0 matches
- 临时文件清理：✅ git ls-files 空
- .gitignore 规则：✅ L73-75 三条规则
- Optional 统一：✅ Grep 0 matches
- Facade Any 替换：✅ 5 Facade 使用 Protocol
```

### 3.3 S3: 回填 CHG-100 §12 关闭确认

```markdown
## 12. 关闭确认

| 项目 | 内容 |
|------|------|
| 关闭日期 | 2026-07-08 |
| 关闭人 | TraeAI (GLM-5.2) |
| 关闭理由 | T1-T8 全部完成 + P2 门禁通过（ruff 0 + mypy ≤8 + pytest ≥1260）+ 8 项 P0/P1 问题已修复 |
| 后续行动 | ① 剩余 except Exception 70 处的进一步缩窄（#3 剩余部分）；② ProjectInfo 原地修改改用 model_copy (#12)；③ parser.py 拆分 (#6, P3)；④ change_service.py 拆分 (#18, P3)；⑤ 冗余委托方法清理 (#19, P4) |
```

### 3.4 S4: CHG-100 §3.4 状态流转

将 §3.4 变更状态从 `implementing` 改为 `closed`。

### 3.5 S5: PM_SESSION §3 spec_compliance 同步

**文件**：`PM_SESSION_SW-2026-008.md`

在 §3 spec_compliance 的 dogfooding 计数处更新：`29 次闭环` → `30 次闭环`，追加 CHG-100 条目：

```markdown
- CHG-SCPT-2026-100（第 30 次闭环，2026-07-08 closed）：Claude 诊断报告核查 + P0/P1 技术债清理（T1-T8）：DB 连接复用 + get_project 缓存优先 + sync 委托 + setup_logger 标准化 + 临时文件清理 + 静默 except 整改 + Optional 统一 + Facade Any 替换 Protocol。三轨门禁：ruff 0 + mypy X + pytest X passed。
```

### 3.6 S6: PM_SESSION §6 Implementation Log 同步

在 §6 顶部追加 2026-07-08 条目：

```markdown
- 2026-07-08 | skill=pm-workflow | mode=CHG-100 Claude 诊断修复闭环（T1-T8 + P2 门禁 + S-final） | goal=用户指令核查 Claude 诊断报告并基于现状给修复计划。核查结论：报告基于修复前状态生成，8 项 P0/P1 已全部修复。执行 T1-T8 全部落盘 + P2 门禁验证 + CHG-100 闭环。 | changed_files: ① `auto_pm/core/project_service.py`（T1 get_project 缓存优先 L209-229）；② `auto_pm/db/connection.py`（T2 单例连接 L39-51）；③ `auto_pm/db/sync.py`（T3 委托 ProjectScanner L239-248）；④ `.gitignore`（T4 追加 *.bak_/pytest_*.txt/claude_plan）；⑤ 13+ 模块（T5 setup_logger 标准化）；⑥ workbench/system/project_service/frontmatter_svc（T6 静默 except 添加 log.warning）；⑦ 11 文件 38 处（T7 Optional→X|None）；⑧ 5 Facade + protocols.py + registry.py（T8 Any→Protocol + cast）；⑨ `00_项目管理/04_变更管理/01_变更单/CHG-SCPT/CHG-SCPT-2026-100.md`（§10/§11/§12 回填 + 状态 closed）；⑩ `PM_SESSION_SW-2026-008.md`（§3/§6/§8 同步）；⑪ `pyproject.toml`（0.9.0→0.9.1）；⑫ `CHANGELOG.md`（[0.9.1] 条目） | impact: ① 8 项 P0/P1 问题全部修复；② 三轨门禁通过；③ dogfooding 第 30 次闭环；④ 版本号三件套一致 | risks: 低——① 剩余 70 处 except Exception 属宽泛捕获非静默吞错，后续迭代处理；② ProjectInfo 原地修改 9 处后续迭代改 model_copy；③ parser.py/change_service.py 拆分属 P3 大工作量 | verification: 已验证——① ruff 0 errors；② mypy X errors（≤8）；③ pytest X passed 2 skipped（≥1260）；④ Grep Optional[=0；⑤ Grep setup_logger(log_level=0；⑥ git ls-files 临时文件空 |
```

### 3.7 S7: PM_SESSION §8 Handoff Notes 同步

在 §8 顶部追加：

```markdown
- skill_handoff_20260708_chg100: 2026-07-08 pm-workflow 完成 CHG-100 Claude 诊断修复闭环（dogfooding 第 30 次闭环 closed）。**current_state**: 代码基线 V0.9.1（pyproject 0.9.1 + CHANGELOG [0.9.1]），8 项 P0/P1 问题全部修复——T1 get_project 缓存优先 + T2 DB 连接复用 + T3 sync 委托 + T4 临时文件清理 + T5 setup_logger 标准化 + T6 静默 except 整改 + T7 Optional 统一（38 处/11 文件）+ T8 Facade Any 替换 Protocol（14 处/5 Facade）。三轨门禁: ruff 0 errors + mypy X errors + pytest X passed 2 skipped。**next_focus**: ① 剩余 except Exception 70 处的进一步缩窄（#3 剩余部分，非静默吞错）；② ProjectInfo 原地修改 9 处改用 model_copy (#12)；③ parser.py 拆分 (#6, P3 大工作量)；④ change_service.py 拆分 (#18, P3)；⑤ 冗余委托方法清理 (#19, P4)；⑥ 性能 FPS 实测；⑦ 电气部门真实试用反馈；⑧ V1.0.0 发布评估。**watchouts**: a) Claude 第二版诊断报告基于修复前状态生成，P0/P1 已全部解决，剩余项为低优先级；b) 前序会话发现 Edit replace_all 对 Optional 模式不可靠，已改用 Write 整体重写；c) Protocol 结构性子类型兼容，Service 无需显式继承；d) registry.py 使用 cast() 解决依赖注入容器的类型转换。**read_first**: `00_项目管理/04_变更管理/01_变更单/CHG-SCPT/CHG-SCPT-2026-100.md`, `09_整改项/Claude-result`, `PM_SESSION_SW-2026-008.md` §3 spec_compliance + §6 2026-07-08 条目
```

### 3.8 S8: pyproject.toml 版本号升级

**文件**：`pyproject.toml` L7

```toml
version = "0.9.0"  →  version = "0.9.1"
```

### 3.9 S9: CHANGELOG.md 新增 [0.9.1] 条目

**文件**：`CHANGELOG.md`

在 `## [Unreleased]` 下方插入：

```markdown
## [0.9.1] - 2026-07-08

### Changed - CHG-SCPT-2026-100 Claude 诊断报告核查 + P0/P1 技术债清理

- **T1 get_project 缓存优先**：`auto_pm/core/project_service.py` L209-229 改为优先走 `get_project_cached()` DB 缓存，DB 不可用时降级到文件系统扫描，消除每次单项目查询触发全量扫描的性能问题（Claude #1）
- **T2 DB 连接复用**：`auto_pm/db/connection.py` L39-51 改为单例连接复用模式，避免每次操作创建新 sqlite3 连接 + 重新设置 PRAGMA，新增 `close()` 方法用于显式释放（Claude #2）
- **T3 sync 委托消除克隆**：`auto_pm/db/sync.py` L239-248 `_get_project_mtime()` 改为委托 `ProjectScanner.get_project_mtime()`，消除 24 行代码克隆（Claude #4）
- **T5 setup_logger 标准化**：13+ 模块从 `log = setup_logger(log_level="INFO", app_name="auto_pm")` 硬编码改为 `log = logging.getLogger(__name__)` 标准模式，用户 `.env` LOG_LEVEL=DEBUG 配置生效（Claude #5）

### Fixed - CHG-SCPT-2026-100 静默异常吞没整改

- **T6 静默 except 整改**：workbench_facade/system_facade/project_service/frontmatter_svc 中约 15-20 处静默 `except Exception: pass`/`return 0` 添加 `log.warning(exc_info=True)` 日志记录（Claude #3 部分）

### Removed - CHG-SCPT-2026-100 临时文件清理

- **T4 临时文件清理**：从 git 索引移除 5 个临时文件（PM_SESSION_SW-2026-008.md.bak_v060_combined/s9/split + claude_plan + pytest_nongui_result.txt），`.gitignore` 追加 `*.bak_*`/`pytest_*.txt`/`claude_plan` 规则（Claude #11/#17）

### Style - CHG-SCPT-2026-100 类型注解统一

- **T7 Optional 统一**：11 文件 38 处 `Optional[X]` → `X | None`（Python 3.11+ 语法），删除 `from typing import Optional` 导入（Claude #7）
- **T8 Facade Any 替换 Protocol**：5 个 Facade 的 14 处 `Any` 参数替换为具体 Protocol 类型，`protocols.py` 新增 8 个 Protocol（DashboardService/AssetSummaryService/PmSessionService/Template/SpecCheck/SpecCenter/DocRefresh/Report），`registry.py` 使用 `cast()` 解决依赖注入类型转换（Claude #8/#9）

### Verified - V0.9.1 回归

- ruff check .: 0 errors
- mypy auto_pm/: X errors（≤8，P1/P2 非阻断，与基线一致）
- pytest --no-cov -x: X passed, 2 skipped（≥1260）
- Grep `Optional\[`: 0 matches
- Grep `setup_logger\(log_level`: 0 matches
- git ls-files 临时文件: 空
- dogfooding: CHG-SCPT-2026-100 第 30 次闭环

### Notes - V0.9.1 Claude 诊断报告核查说明

- Claude 第二版诊断报告（19 项问题）基于修复前状态生成，8 项 P0/P1 已全部修复
- 剩余低优先级项：#3 剩余 70 处宽泛 except（非静默吞错）/ #6 parser.py 716 行拆分（P3）/ #12 ProjectInfo 原地修改 9 处（P2）/ #18 change_service.py 723 行拆分（P3）/ #19 冗余委托方法（P4），列入后续迭代
```

---

## 四、执行顺序

```
Step 1: P2 门禁验证
  ├─ ruff check .                    # 期望 0 errors
  ├─ mypy auto_pm/                   # 期望 ≤ 8 errors
  └─ pytest --no-cov -x              # 期望 ≥ 1260 passed 2 skipped
  ↓
Step 2: CHG-100 回填（基于 P2 实际数字）
  ├─ §10 实施记录 S1-S10 全部标 ✅ + 填完成时间
  ├─ §11 验证记录 填写 P1/P2 门禁实际数字
  ├─ §12 关闭确认 填关闭日期/人/理由/后续行动
  └─ §3.4 状态 implementing → closed
  ↓
Step 3: PM_SESSION 同步
  ├─ §3 spec_compliance dogfooding 29→30 + CHG-100 条目
  ├─ §6 Implementation Log 追加 2026-07-08 条目
  └─ §8 Handoff Notes 追加 skill_handoff_20260708_chg100
  ↓
Step 4: 版本号同步
  ├─ pyproject.toml version 0.9.0 → 0.9.1
  └─ CHANGELOG.md 新增 [0.9.1] 条目（从 §三.9 模板填入实际门禁数字）
```

**执行顺序说明**：
- Step 1 必须先执行，获取实际门禁数字
- Step 2-4 依赖 Step 1 的实际数字
- Step 2/3/4 可顺序执行（每个文件独立）

---

## 五、假设与决策

### 5.1 假设

1. **T1-T8 改动已持久化**：通过源码验证（Grep + Read 确认）
2. **P1 门禁基线可信**：ruff 0 + mypy 8 + pytest 1260 passed 2 skipped
3. **Protocol 结构性类型兼容**：Service 无需显式继承，T8 替换后运行时行为不变
4. **`from __future__ import annotations` 已存在**：T7 替换 `X | None` 运行时安全
5. **pytest 失败可能为预先存在的污染**：§8 skill_handoff_20260708_qml_fix 记录的 7 个 CLI JSON 失败属测试污染非回归

### 5.2 决策

| 决策项 | 选择 | 理由 |
|--------|------|------|
| 范围 | 仅 P2 门禁 + S-final 闭环 | T1-T8 已完成，不重复执行 |
| mypy 目标 | ≤ 8 errors | 与 P1 基线一致，不强制降至 0 |
| 版本号升级 | 0.9.0 → 0.9.1 | 技术债清理属 patch 级别 |
| 剩余低优先级项 | 不纳入本次 | #3/#6/#12/#18/#19 列入后续迭代 |
| CHG-100 §10 回填 | 全部标 ✅ | 实际 T1-T8 已完成，原 ⏳ 状态失真 |

### 5.3 风险

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| P2 门禁 mypy 新增错误 | 低 | 低 | 前序会话已修复 Protocol 不完整 + registry cast |
| P2 门禁 pytest 失败 | 中 | 中 | 先排除 §8 记录的 7 个预先存在污染，再用 --tb=long 定位 |
| CHG-100 §10 回填遗漏 | 低 | 低 | 按 S1-S10 清单逐项核对 |
| PM_SESSION §8 条目过长 | 低 | 低 | 沿用前条 skill_handoff 格式，保持简洁 |
| Write 工具损坏中文全角括号 | 中 | 低 | §8 skill_handoff_20260708_qml_fix 已记录此问题，改用半角括号 |

---

## 六、文件清单

### 6.1 待修改文件（S-final，共 4 文件）

- `00_项目管理/04_变更管理/01_变更单/CHG-SCPT/CHG-SCPT-2026-100.md`（§10/§11/§12/§3.4）
- `PM_SESSION_SW-2026-008.md`（§3/§6/§8）
- `pyproject.toml`（L7 version）
- `CHANGELOG.md`（[0.9.1] 条目）

### 6.2 不修改文件（已落盘，仅验证）

- `auto_pm/core/project_service.py`（T1 已完成）
- `auto_pm/db/connection.py`（T2 已完成）
- `auto_pm/db/sync.py`（T3 已完成）
- `.gitignore`（T4 已完成）
- 13+ 模块文件（T5 已完成）
- workbench/system/project_service/frontmatter_svc（T6 已完成）
- 11 文件 Optional 替换（T7 已完成）
- 5 Facade + protocols.py + registry.py（T8 已完成）

---

## 七、TodoList

执行阶段将按以下 TodoList 推进：

- [ ] **P2 门禁验证**: ruff check + mypy + pytest 三轨回归
- [ ] **CHG-100 回填**: §10 实施记录 + §11 验证记录 + §12 关闭确认 + §3.4 状态 closed
- [ ] **PM_SESSION 同步**: §3 spec_compliance + §6 Implementation Log + §8 Handoff Notes
- [ ] **版本号同步**: pyproject.toml 0.9.0→0.9.1 + CHANGELOG.md [0.9.1] 条目

---

## 八、后续迭代建议（不在本次范围）

基于 Claude 报告核查结果，以下低优先级项建议列入后续迭代：

| 优先级 | 编号 | 问题 | 工作量 | 建议迭代 |
|--------|------|------|--------|----------|
| P2 | #3 剩余 | except Exception 70 处（非静默吞错） | 中 | V0.9.2 |
| P2 | #12 | ProjectInfo 原地修改 9 处 → model_copy | 小 | V0.9.2 |
| P3 | #6 | parser.py 716 行拆分 | 大 | V1.0.0 |
| P3 | #18 | change_service.py 723 行拆分 | 大 | V1.0.0 |
| P4 | #19 | 7 个冗余委托方法清理 | 小 | V1.0.0 |
| P3 | #13 | Ruff 规则集扩展（B/BLE/SIM/UP/RUF） | 小 | V1.0.0 |
| P3 | #14 | AutoPmConfig 配置类扩展 | 中 | V1.0.0 |
| P4 | #15 | os.path → pathlib 统一 | 大 | V2.0.0 |
| P4 | #16 | change/models.py 重命名为 constants.py | 小 | V1.0.0 |
