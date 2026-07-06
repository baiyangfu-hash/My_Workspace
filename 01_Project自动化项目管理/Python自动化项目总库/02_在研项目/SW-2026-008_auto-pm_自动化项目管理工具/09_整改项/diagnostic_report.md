---
title: auto-pm 项目全面诊断报告（2026-07-07 重新诊断）
date: 2026-07-07
reviewer: pm-workflow（代码层 + 文档层并行子代理 + 主代理实测验证）
scope: auto_pm/ 全部源码 + tests/ + 02_设计/ + 00_项目基础信息/ + 09_整改项/ + PM_SESSION
method: 只读审查 + 运行时验证（ruff/mypy/pytest/python -c 实测）
baseline: pyproject=0.9.0 / CHANGELOG=[0.9.0] / 设计文档=V3.0.0-draft
prior_report: archive/diagnostic_report_2026-07-06_V0.9.0.md（2026-07-06 创建）
---

# auto-pm 项目全面诊断报告（2026-07-07 重新诊断）

> [!CAUTION]
> 本次重新诊断发现 **PM_SESSION §3 spec_compliance 声称的"ruff 0 errors + mypy 0 errors + 999 passed"与实际状态严重不符**。实测 ruff 26 errors、mypy 34 errors、pytest 完全无法启动（PySide6 DLL 加载失败 + pytestqt 插件崩溃）。根因是 2026-07-06 M1 骨架实施未闭环（删除 `qml_bridge.py` 但未同步 `protocols.py` / 测试文件 / 方法名），且未运行全量回归就回写了 PM_SESSION §6。

---

## 一、执行摘要

### 1.1 核心数据（2026-07-07 实测）

| 维度 | 2026-07-06 旧报告声明 | 2026-07-07 实测 | 偏差 |
|------|----------------------|-----------------|------|
| ruff check auto_pm/ | 0 errors | **26 errors** | 🔴 严重回退 |
| mypy auto_pm/ | 0 errors（104 source files） | **34 errors in 12 files**（123 source files） | 🔴 严重回退 |
| pytest 全量回归 | 999 passed 1 skipped in 44.14s | **INTERNALERROR（无法启动）** | 🔴 完全阻断 |
| 源码文件数 | 117 | 123 | +6（M1 骨架新增） |
| 测试文件数 | 111 | 112 | +1 |
| 运行时导入 | 未验证 | `import auto_pm.core.protocols` 触发 ImportError | 🔴 阻断 |

### 1.2 根因分析

**M1 骨架实施未闭环**（2026-07-06 fullstack-engineer）引入了 3 类阻断性问题：

1. **断裂导入链**：`protocols.py` L15-20 仍从 `auto_pm.models` 导入 `ProjectCardDTO`，但该名字已改名为 `ProjectListItem`（`models/dto.py` L19）。新的 `ProjectCardDTO` 定义在 `ui/contracts/dto/workbench_dto.py` L19（dataclass）。这导致 `import auto_pm.core.protocols` 触发 `ImportError`，进而导致 `workbench_facade.py`、`change_facade.py`、`system_facade.py`、`workbench_bridge.py`、`qml_main_window.py` 全部无法导入。

2. **方法名不匹配**：`workbench_bridge.py` L49 调用 `self._facade.get_dashboard_summary()`，但 `WorkbenchFacade` 只有 `get_dashboard_snapshot()`（L33）。mypy 报 `attr-defined` 错误。

3. **测试未同步**：`tests/qml/test_qml_bridge_v08.py` L27 仍 `from auto_pm.ui.qml.qml_bridge import QmlBridge`，但 `qml_bridge.py` 已被删除（拆分为 5 个 Domain Bridge）。这导致测试收集时触发 ImportError。

**M1 骨架 verification 失真**：PM_SESSION §6 2026-07-06 fullstack-engineer M1 实施记录中 verification 写"已验证——`pytest tests/application/ -p no:pytestqt` 单测 3 passed 正常通过"，但**只验证了 tests/application/ 的 3 个测试，没有运行全量回归**，导致上述 3 类阻断性问题未被发现。

### 1.3 优先级建议

| 优先级 | 行动 | 影响 |
|--------|------|------|
| **P0 阻断** | 修复 `protocols.py` 断裂导入（ProjectCardDTO → ProjectListItem 或修正导入路径） | 解除 Facade/Bridge 链路阻断 |
| **P0 阻断** | 修复 `workbench_bridge.py` 方法名（get_dashboard_summary → get_dashboard_snapshot） | 解除 Bridge 调用阻断 |
| **P0 阻断** | 同步 `tests/qml/test_qml_bridge_v08.py` 等测试文件（删除或改为测试 5 个 Domain Bridge） | 解除测试收集阻断 |
| **P0 阻断** | 修复 `project_service.py` 重复定义（get_last_sync_time L178/L514、is_cache_available L187/L538） | 消除 mypy no-redef |
| **P0 阻断** | 修复 `project_service.py` L163 用旧字段构造新 ProjectCardDTO（change_count/file_mtime/description → health_status/open_change_count/last_activity_at） | 消除 mypy call-arg |
| **P1 短期** | 修复 PySide6 DLL 加载失败环境问题 | 恢复 pytest 可启动 |
| **P1 短期** | 清理 `clean_bridge.py` 项目根目录临时文件 | 仓库整洁 |
| **P1 短期** | 同步 PM_SESSION §2/§3 PRD 版本号（V2.2.0 → V3.0.0-draft） | 真源一致性 |
| **P1 短期** | 清理 `qml/__init__.py` 断裂导入 + 多处 docstring 幽灵引用 | 代码整洁 |
| **P2 中期** | 清理 3 个 .bak 备份文件 | 仓库整洁 |
| **P2 中期** | 修复 ruff I001（24 处 import 排序，可 --fix 自动修复） | 静态门禁 |

---

## 二、原诊断报告问题核对（2026-07-06 → 2026-07-07）

### 2.1 架构问题（A1-A5）

#### A1：QmlBridge 仍是 933 行的上帝类 — ✅ 已修复（有副作用）

**证据**：
- `auto_pm/ui/qml/qml_bridge.py` **已删除**（Glob 全局搜索无结果）
- 5 个 Domain Bridge 真实存在且为轻量实现：
  - `workbench_bridge.py`（70 行）
  - `change_bridge.py`（49 行）
  - `delivery_bridge.py`（47 行）
  - `system_bridge.py`（47 行）
  - `spec_bridge.py`（41 行）
- 新装配入口 `auto_pm/ui/qml_main_window.py` 导入 5 个 Bridge + FacadeRegistry 装配

**⚠️ 副作用（新问题 N1/N5）**：
- `auto_pm/ui/qml/__init__.py` L12 仍残留 `from auto_pm.ui.qml.qml_bridge import QmlBridge` —— **断裂导入**
- 多处 docstring 仍引用 `QmlBridge`（`ui/__init__.py` L7、`qml/__init__.py` L4/L7、`factories.py` L76、`global_pages/__init__.py` L9、`qml_main_window.py` L5）
- `tests/qml/test_qml_bridge_v08.py` L27 仍导入 `QmlBridge` —— 测试收集触发 ImportError

#### A2：DTO 体系双源并存 — ⚠️ 部分修复

**证据**：
- `auto_pm/models/dto.py`（Pydantic）仍存在，包含 `ProjectListItem`（原 `ProjectCardDTO` 改名，L19）
- `auto_pm/ui/contracts/dto/workbench_dto.py`（dataclass）仍存在，包含新的 `ProjectCardDTO`（L19，字段：health_status/open_change_count/last_activity_at）
- **同名冲突已消除**：`ProjectCardDTO` 仅在 `workbench_dto.py` 定义
- **概念重叠仍在**：`DashboardSummaryDTO`（Pydantic）vs `DashboardSnapshotDTO`（dataclass）字段高度重叠
- **新问题**：`protocols.py` L18 仍从 `models` 导入 `ProjectCardDTO`，但已改名 —— 断裂导入

#### A3：Facade 构造函数缺乏类型约束 — ⚠️ 部分修复

**证据**（5 个 Facade 当前构造函数签名）：

| Facade | 签名 | 评价 |
|---|---|---|
| `change_facade.py:15` | `change_service: ChangeServiceProtocol \| None = None` | ✅ 全 Protocol |
| `workbench_facade.py:15-20` | `dashboard_service: Any, project_service: ProjectServiceProtocol, asset_summary_service: Any` | ⚠️ 1/3 Protocol |
| `system_facade.py:10-15` | `pm_session_service: Any, template_service: Any = None, project_service: ProjectServiceProtocol \| None = None` | ⚠️ 1/3 Protocol |
| `spec_facade.py:12-16` | `spec_check_service: Any = None, spec_center_service: Any = None` | ❌ 全 Any |
| `delivery_facade.py:10-15` | `doc_refresh_service: Any = None, report_service: Any = None, asset_summary_service: Any = None` | ❌ 全 Any |

**根因**：`protocols.py` 仅定义了 `ProjectServiceProtocol`、`ChangeServiceProtocol`、`PlcServiceProtocol`、`ProjectScannerProtocol`，未定义 Dashboard/AssetSummary/SpecCheck/SpecCenter/Report/DocRefresh/Template/PmSession 等服务的 Protocol。

#### A4：gui/ 目录为空，flet_app/ 遗留 — ⚠️ 部分修复

**证据**：
- `auto_pm/gui/`：✅ **已完全删除**
- `auto_pm/flet_app/`：❌ **目录仍存在**，源码 `.py` 已删但 `__pycache__/` 残留 4 个 `.pyc` 编译缓存

#### A5：CLI 和 GUI 共用 Service 但装配路径不同 — ℹ️ 已变化

**证据**：
- `auto_pm/app_context.py` 已简化为 29 行，仅持有 `app_config`/`logger`/`workspace_root`/`templates_dir`，**不再创建任何 Service 或 Facade**（退化为纯配置容器）
- `auto_pm/ui/registry.py`（FacadeRegistry，61 行）仍是独立的 Facade 装配器
- 两路径仍分离，但冲突已降低
- **新问题**：`registry.py` L58-60 装配 `SystemFacade` 时未传 `project_service` 参数，导致 SystemFacade 通过 Registry 装配时永远拿不到 project_service

### 2.2 代码级问题（C1-C5）

#### C1：Facade 层 getattr 防御性编程过重 — ⚠️ 部分修复

**证据**（`workbench_facade.py`）：
- `list_project_cards` L61-62：✅ 已清理（改用 `str(p.stack)`、`str(p.phase)`）
- `get_project_workspace` L83-85：❌ 仍有 `if hasattr(v, "value"): summary[k] = str(v.value)`
- `clear_cache` L150-151：❌ 仍有 `getattr(self._project_service, "db", None)` + `if hasattr(db, "init_schema")`

#### C2：ChangeFacade.create_change_request 遗留注释 — ⚠️ 部分修复

**证据**（`change_facade.py` L89-100）：
- 旧的"思考过程"注释（`Wait, CreateChangeCommand does not have impact_scope...`）✅ 已清理
- 替换为规范说明 + TODO：`# TODO: CreateChangeCommand 暂未携带 impact_scope，待 GUI 支持后补齐`
- 但 `impact_scope=[]` 硬编码功能缺口仍存在

#### C3：SystemFacade 中存在内联 import — ❌ 未修复

**证据**（`system_facade.py` L73-74，在 `get_template_detail` 方法内）：
```python
from pathlib import Path
import yaml
```
ruff 也报告了此处的 I001（import 排序）问题。

#### C4：WorkbenchFacade.get_settings_summary 直接访问 Service 内部 — ⚠️ 部分修复（问题转移）

**证据**（`workbench_facade.py`）：
- `get_settings_summary` L108-132：✅ **已修复**。改用公开方法 `get_db_path()`、`is_cache_available()`、`get_project_count()`、`get_last_sync_time()`、`workspace_root` 属性
- `clear_cache` L150-152：❌ **同反模式仍存在**：`getattr(self._project_service, "db", None)` + `if hasattr(db, "init_schema")`

#### C5：CommandResult 和 QueryResult 几乎完全相同 — ❌ 未修复

**证据**（`auto_pm/ui/contracts/result.py`，22 行）：
```python
@dataclass(frozen=True)
class CommandResult(Generic[T]):
    success: bool
    message: str
    payload: T | None = None
    errors: list[str] = field(default_factory=list)

@dataclass(frozen=True)
class QueryResult(Generic[T]):
    success: bool
    message: str
    payload: T | None = None
    errors: list[str] = field(default_factory=list)
```
两类字段仍完全相同，仅 docstring 不同。ruff 还发现 L4 `typing.Any` 未使用（F401）。

### 2.3 测试体系问题（T1）

#### T1：Facade 测试全部使用 MagicMock — ⚠️ 部分修复

**证据**：
- `tests/application/` 共 7 个测试文件：
  - `test_workbench_facade_int.py`：✅ **新增的真实集成测试**，使用 `ProjectService` + `DatabaseManager` + `tmp_path`，0 处 MagicMock
  - `test_facade_registry.py`：新增，测试 Registry 装配（仍用 10 处 MagicMock）
  - 其余 5 个文件仍全部使用 MagicMock，共 37 处
- `tests/fakes/` 目录已创建但**仅有空 `__init__.py`**，无实际 Fake Service 实现

### 2.4 文档矛盾问题（U1-U5, D1-D6）

| 编号 | 矛盾描述 | 2026-07-06 状态 | 2026-07-07 状态 | 证据 |
|------|----------|-----------------|-----------------|------|
| U1/D1 | README 项目结构与实际代码不符 | ❌ | ✅ 已修复 | README L251-256 已对齐 |
| U2/D2 | 归档索引指向已不存在的文件 | ❌ | ✅ 已修复 | docs/归档索引.md 已重写 |
| U3/D4 | 文档存放位置有三套体系 | ❌ | ✅ 已修复 | 001-004 已迁移到 02_设计/ |
| U4/D5 | README GUI 功能描述使用 QWidget 术语 | ❌ | ⚠️ 部分修复 | L178-194 已用 QML，L12 仍有 "QWizard" |
| U5 | pyproject 0.9.0 vs 设计文档 V3.0.0-draft | ❌ | ❌ 未修复（加重） | PM_SESSION §2/§3 仍标 "PRD V2.2.0" |
| D3 | README 文档导航表指向 001~004 | ❌ | ✅ 已修复 | README L292-310 已修正 |
| D6 | ui/__init__.py 提到 qml_bridge.py 旧路径 | ❌ | ℹ️ 已变化（更严重） | qml_bridge.py 已删，但 qml/__init__.py L12 断裂导入 |

---

## 三、本次诊断新发现问题

### 3.1 🔴 P0 阻断性问题（运行时阻断）

#### N1：protocols.py 断裂导入（运行时阻断）

- **位置**：`auto_pm/core/protocols.py` L15-20
- **问题**：`from auto_pm.models import (..., ProjectCardDTO, ...)` —— 但 `models/__init__.py` 已不再导出 `ProjectCardDTO`（改名为 `ProjectListItem`）
- **实测证据**：
  ```
  >>> from auto_pm.core.protocols import ProjectServiceProtocol
  ImportError: cannot import name 'ProjectCardDTO' from 'auto_pm.models'
  ```
- **影响链**：`protocols.py` → `workbench_facade.py` L4 → `workbench_bridge.py` L4 → `qml_main_window.py` —— 全部无法导入
- **修复建议**：将 `protocols.py` L18 的 `ProjectCardDTO` 改为 `ProjectListItem`，或修正导入路径为 `from auto_pm.ui.contracts.dto.workbench_dto import ProjectCardDTO`

#### N2：workbench_bridge.py 方法名不匹配

- **位置**：`auto_pm/ui/qml/bridges/workbench_bridge.py` L49
- **问题**：调用 `self._facade.get_dashboard_summary()`，但 `WorkbenchFacade` 只有 `get_dashboard_snapshot()`（L33）
- **实测证据**：mypy 报 `attr-defined: "WorkbenchFacade" has no attribute "get_dashboard_summary"`
- **修复建议**：将 L49 的 `get_dashboard_summary()` 改为 `get_dashboard_snapshot()`

#### N3：tests/qml/test_qml_bridge_v08.py 测试收集阻断

- **位置**：`tests/qml/test_qml_bridge_v08.py` L27
- **问题**：`from auto_pm.ui.qml.qml_bridge import QmlBridge` —— 但 `qml_bridge.py` 已被删除
- **影响**：测试收集时触发 ImportError，可能导致整个 tests/qml/ 目录无法收集
- **修复建议**：删除该文件（V0.8.0 时代的 QmlBridge 测试已过时），或改为测试 5 个 Domain Bridge

#### N4：project_service.py 重复定义（未完成重构）

- **位置**：`auto_pm/core/project_service.py`
- **问题**：
  - `get_last_sync_time`：L178（旧版，调用 `self._repo.get_last_sync_time()` 但 ProjectRepository 无此方法）与 L514（M3-Iter5 新版，用 ScanLogRepository）重复
  - `is_cache_available`：L187（`return self._repo is not None`）与 L538（`return self.db is not None`）重复，语义不同
- **实测证据**：mypy 报 `no-redef` 2 处 + `attr-defined` 1 处（L182）
- **修复建议**：删除 L178-185 和 L187-189 的旧版定义，保留 L514/L538 的新版

#### N5：project_service.py 用旧字段构造新 ProjectCardDTO

- **位置**：`auto_pm/core/project_service.py` L163-174
- **问题**：传入 `change_count`、`file_mtime`、`description`，但新 `ProjectCardDTO`（workbench_dto.py L19）字段为 `health_status`、`open_change_count`、`last_activity_at`
- **实测证据**：mypy 报 `call-arg` 3 处
- **修复建议**：更新 L163-174 的字段名，或保留旧字段并改用 `ProjectListItem`

### 3.2 🟡 P1 短期问题

#### N6：qml/__init__.py 断裂导入 + 多处 docstring 幽灵引用

- **位置**：`auto_pm/ui/qml/__init__.py` L12
- **问题**：`from auto_pm.ui.qml.qml_bridge import QmlBridge` —— qml_bridge.py 已删除
- **多处 docstring 幽灵引用**：
  - `auto_pm/ui/__init__.py` L7
  - `auto_pm/ui/qml/__init__.py` L4/L7
  - `auto_pm/ui/factories.py` L76
  - `auto_pm/ui/global_pages/__init__.py` L9
  - `auto_pm/ui/qml_main_window.py` L5（"通过 rootContext() 注入 QmlBridge"）
- **修复建议**：删除 `qml/__init__.py` L12 的断裂导入，清理所有 docstring 中的 QmlBridge 引用

#### N7：qml_main_window.py docstring 4 处过时引用

- **位置**：`auto_pm/ui/qml_main_window.py`
- **问题**：
  - L4：`不修改现有 main_window.py` —— main_window.py 已在 V0.9.0 删除
  - L5：`QmlBridge` —— 已替换为 5 个 Domain Bridge
  - L14：`python -m auto_pm gui --qml` —— --qml 标志已在 V0.9.0 移除
  - L18：`02_设计/GUI原型设计.md §15.4` —— 该文件不存在
- **修复建议**：重写 docstring 反映 V0.9.0 + M1 骨架实际状态

#### N8：PM_SESSION §2/§3 PRD 版本号未同步

- **位置**：`PM_SESSION_SW-2026-008.md`
- **问题**：
  - L23 §2 milestone：仍标 "PRD V2.2.0"（实际 V3.0.0-draft）
  - L74 §3 spec_compliance：仍标 "PRD=V2.2.0"
  - L10 last_updated：2026-07-05（但 §6 有 2026-07-06 条目）
- **修复建议**：更新为 "PRD V3.0.0-draft"，last_updated 更新为 2026-07-07

#### N9：PM_SESSION §3 spec_compliance 声明严重失真

- **位置**：`PM_SESSION_SW-2026-008.md` L74
- **问题**：声称 "ruff check 0 errors；mypy auto_pm 0 errors（104 source files）；全量回归 999 passed 1 skipped in 44.14s（0 failed）"
- **实测对比**：
  - ruff：26 errors（非 0）
  - mypy：34 errors in 12 files（非 0，123 source files 非 104）
  - pytest：INTERNALERROR（非 999 passed）
- **根因**：2026-07-06 M1 骨架实施后未运行全量回归就回写 PM_SESSION §6
- **修复建议**：修正 §3 spec_compliance 为实际状态，或修复代码后重新验证

#### N10：PM_SESSION §4 引用不存在的 005

- **位置**：`PM_SESSION_SW-2026-008.md` L82
- **问题**：`chg: 00_项目基础信息/005_变更记录_CHG.md` —— 文件已删除/归档
- **修复建议**：更新 §4 Artifacts Index，移除或修正 005 引用

#### N11：PySide6 DLL 加载失败（环境问题）

- **位置**：`.venv/` 环境
- **问题**：`ImportError: DLL load failed while importing QtCore: 找不到指定的模块`
- **影响**：pytestqt 插件无法初始化，导致 pytest 完全无法启动（INTERNALERROR）
- **修复建议**：重装 PySide6（`pip install --force-reinstall PySide6`），或检查 Windows 系统 VC++ 运行库

#### N12：clean_bridge.py 项目根目录临时文件

- **位置**：项目根目录 `clean_bridge.py`（249+ 行）
- **问题**：这是一个完整的旧 QmlBridge 实现（V0.6.0/V0.8.0 时代），显然是 M1 骨架实施时的临时备份文件
- **修复建议**：删除（已被 5 个 Domain Bridge 替代）

### 3.3 🟢 P2 中期问题

#### N13：3 个 .bak 备份文件未清理

- **位置**：项目根目录
- **文件**：
  - `PM_SESSION_SW-2026-008.md.bak_v060_combined`（~464 KB）
  - `PM_SESSION_SW-2026-008.md.bak_v060_s9`（~121 KB）
  - `PM_SESSION_SW-2026-008.md.bak_v060_split`（~478 KB）
- **来源**：CHG-087 Stage 1 PM_SESSION 拆分操作备份（2026-07-06）
- **修复建议**：删除（正式归档已在 `00_项目管理/05_PM_SESSION归档/PM_SESSION_SW-2026-008_archive_V0.6.0.md`）

#### N14：flet_app/ 残留 __pycache__

- **位置**：`auto_pm/flet_app/__pycache__/`（4 个 .pyc 文件）
- **修复建议**：删除整个 `auto_pm/flet_app/` 目录

#### N15：ruff I001 import 排序（24 处）

- **位置**：几乎所有 Facade、Bridge、DTO、Registry、qml_main_window
- **修复建议**：`ruff check auto_pm/ --fix` 可自动修复

---

## 四、09_整改项目录整理

### 4.1 已归档文件（2026-07-07 归档）

| 文件 | 原活跃期 | 归档原因 |
|------|----------|----------|
| `archive/diagnostic_report_2026-07-06_V0.9.0.md` | 2026-07-06 | 被 2026-07-07 重新诊断报告替代 |
| `archive/2026-06-30_项目全量审查报告.md` | V0.4.1 | 审查的是 V2.1 设计文档（已迁移），9 Critical/20 Major 问题大多已修复 |
| `archive/GUI-UI对比度问题清单.md` | V0.5.x | 基于 QWidget 截图，引用 `scripts/gui_plc_full_test.py`（V0.9.0 已删除） |
| `archive/GUI测试整改报告.md` | V0.5.0 | 自标 "已过时"，引用已删除文件 |
| `archive/V0.4.2-glm执行输入清单.md` | V0.4.2 | 引用 `00_项目基础信息/005_变更记录_CHG.md`（已不存在） |

### 4.2 当前活跃文件

| 文件 | 用途 | 状态 |
|------|------|------|
| `diagnostic_report.md` | 2026-07-07 重新诊断报告（本文件） | ✅ 当前真源 |
| `README.md` | 09_整改项索引（待更新） | ⚠️ 需更新 |

---

## 五、综合建议

### 5.1 立即修复（P0 阻断，0-1 天）

1. **修复 protocols.py 断裂导入**（N1）—— 解除 Facade/Bridge 链路阻断
2. **修复 workbench_bridge.py 方法名**（N2）—— 解除 Bridge 调用阻断
3. **同步 tests/qml/test_qml_bridge_v08.py**（N3）—— 解除测试收集阻断
4. **修复 project_service.py 重复定义**（N4）—— 消除 mypy no-redef
5. **修复 project_service.py ProjectCardDTO 字段**（N5）—— 消除 mypy call-arg
6. **重装 PySide6**（N11）—— 恢复 pytest 可启动
7. **删除 clean_bridge.py**（N12）—— 仓库整洁

### 5.2 短期优化（P1，1-2 周）

1. **清理 qml/__init__.py 断裂导入 + 多处 docstring 幽灵引用**（N6/N7）
2. **同步 PM_SESSION §2/§3 PRD 版本号**（N8）—— V2.2.0 → V3.0.0-draft
3. **修正 PM_SESSION §3 spec_compliance 失真声明**（N9）—— 反映实际状态
4. **修正 PM_SESSION §4 引用不存在的 005**（N10）
5. **统一 DTO 体系**（A2）—— 消除 models/dto.py 与 contracts/dto/ 双源
6. **为 Facade 构造函数添加类型注解**（A3）—— 补齐 Protocol 定义
7. **清理 system_facade.py 内联 import**（C3）
8. **清理 WorkbenchFacade.clear_cache 的 getattr 反模式**（C4）

### 5.3 中期推进（P2，2-4 周）

1. **清理 3 个 .bak 备份文件**（N13）
2. **删除 flet_app/ 残留目录**（N14）
3. **运行 ruff --fix 自动修复 24 处 import 排序**（N15）
4. **统一 CLI 和 GUI 的 Service 装配路径**（A5）
5. **补充 Facade 集成测试**（T1）—— 用真实 Fake Service 替代 MagicMock
6. **README L12 "QWizard" 术语修正**（U4/D5）
7. **明确 pyproject 版本与设计文档版本对应关系**（U5）

---

## 六、项目亮点（仍值得肯定）

尽管本次诊断发现严重问题，项目仍有以下特质：

1. **架构演进方向正确**：QmlBridge 上帝类已拆分为 5 个轻量 Domain Bridge（41-70 行），Facade 接口层已建立，DTO 同名冲突已消除
2. **文档真源收口完成**：PRD/INT/DSN/TEC 已迁移到 `02_设计/`，治理类文档留 `00_项目基础信息/`，README 项目结构已对齐实际代码
3. **Dogfooding 纪律**：25 次 CHG 闭环（CHG-001~094 全 closed），项目自己吃自己的狗粮
4. **技术债零剩余**：34/34 项全部偿还
5. **Windows 工程实践扎实**：UTF-8 处理、控制台编码修复、跨平台路径

> [!IMPORTANT]
> 当前项目的主要短板是 **M1 骨架实施未闭环**导致的运行时阻断（断裂导入 + 方法名不匹配 + 测试未同步）和 **PM_SESSION 真源失真**（§3 spec_compliance 声明与实际状态严重不符）。建议优先修复 P0 阻断性问题，恢复 ruff/mypy/pytest 三轨门禁通过，再推进后续迭代。
