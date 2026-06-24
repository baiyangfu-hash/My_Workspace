# 计划：auto-pm 规范漂移检测能力缺口分析与补齐方案

## 摘要

DJ-2026-005 项目审查发现 PM_SESSION 中的 Spec Snapshot 与 spec_registry.json 存在版本漂移（LSP-906 V1→V2, LSP-907 V1→V1.2.1），但 auto-pm `plc check --fix` 未自动检测和修复。本计划分析缺口根因并提出补齐方案。

## 现状分析

### auto-pm 当前能力边界

| 子命令 | 检查项 | 自动修复 | 规范漂移 |
|--------|--------|---------|---------|
| `plc check --fix` | .plc.json / PM_SESSION / PRD / 目录结构 | 创建缺失文件/目录/字段 | **不支持** |
| `plc repair` | 同上 + 文件命名不匹配 | 重命名(需--rename) | **不支持** |
| `plc standardize` | PRD 文档命名标准化 | 重命名+引用更新 | **不支持** |

### PRD 规划 vs 实际实现

| 功能 | PRD 规划版本 | 当前实现状态 |
|------|-------------|-------------|
| 项目结构检查 (LSP-907) | V2.0 | 已实现 |
| 自动修复结构问题 | V2.0 | 已实现 (`--fix`) |
| 文档实质化检查 | V2.0.1 | 已实现 (`--substance`) |
| 规范漂移检测 | **V2.2** | **未实现** |
| 吸收 specmgr | **V2.2** | **未实现** |
| DEV-801 drift_warning 修复 | **V2.2** (P1-036) | **未实现** |

### 缺口根因

1. **PRD 将规范漂移检测排在 V2.2**，当前 V2.0.x 版本未实现
2. **specmgr (SW-2026-006) 未安装**在虚拟环境中，无法作为外部工具调用
3. **PlcChecker** (`auto_pm/plc/checker.py`) 的检查项硬编码为结构检查，无 spec_registry.json 对比逻辑
4. **PM_SESSION Spec Snapshot** 格式是自由文本 Markdown，无结构化解析器

### 影响范围

- 所有使用 auto-pm 管理的 PLC 项目，PM_SESSION 中的 Spec Snapshot 可能与 spec_registry.json 不同步
- 工程师无法通过 `plc check` 发现规范版本漂移，可能导致代码不合规但未被检出

## 方案选择

### 方案 A：在 PlcChecker 中新增规范漂移检查项（推荐）

在 `plc check` 中新增 `Spec Snapshot` 检查项：
1. 解析 PM_SESSION 中的 Spec Snapshot 表格（正则提取规范ID+版本号）
2. 读取 spec_registry.json 获取当前版本
3. 对比并报告漂移
4. `--fix` 模式下自动更新 PM_SESSION 中的 Spec Snapshot

**优点**：最小改动，复用现有 PlcChecker/PlcRepairer 架构，不依赖 specmgr
**缺点**：PM_SESSION Markdown 解析脆弱，specmgr 的 10 项健康检查(SHC-001~010)仍不可用

### 方案 B：安装 specmgr 并在 plc check 中集成调用

1. 安装 specmgr 到虚拟环境
2. 在 PlcChecker 中调用 specmgr 的检查能力
3. `--fix` 模式下调用 specmgr 的 `--auto-fix`

**优点**：获得 specmgr 完整的规范健康检查能力
**缺点**：引入外部依赖，与 PRD V2.2 吸收 specmgr 的计划重叠

### 方案 C：仅安装 specmgr，手动调用

1. 安装 specmgr 到虚拟环境
2. 本次手动运行 `specmgr check --auto-fix` 修复 DJ-2026-005 的漂移
3. V2.2 再正式集成到 auto-pm

**优点**：最快解决当前问题，不改动 auto-pm 代码
**缺点**：不解决根本问题，下次仍需手动

## 推荐方案：A（PlcChecker 新增漂移检查）

### 实施步骤

#### Step 1：新增 SpecSnapshot 解析器

- 文件：`auto_pm/plc/spec_snapshot.py`（新建）
- 功能：
  - `parse_spec_snapshot(pm_session_path)` → `dict[str, str]`（规范ID→版本号）
  - `load_spec_registry(registry_path)` → `dict[str, str]`（规范ID→当前版本号）
  - `compare_versions(snapshot, registry)` → `list[DriftItem]`（漂移项列表）

#### Step 2：PlcChecker 新增检查项

- 文件：`auto_pm/plc/checker.py`（修改）
- 在 `check_project()` 中新增 `Spec Snapshot` 检查项：
  - PASS：Snapshot 与 Registry 一致
  - WARN：小版本漂移（如 V1.0.2→V1.0.3）
  - FAIL：主版本漂移（如 V1.0.0→V2.0.0）或 Snapshot 缺失

#### Step 3：PlcRepairer 新增修复逻辑

- 文件：`auto_pm/plc/repairer.py`（修改）
- 在 `repair_project()` 中新增 Spec Snapshot 修复：
  - 从 spec_registry.json 读取最新版本
  - 更新 PM_SESSION 中的 Spec Snapshot 表格
  - 仅在 `--fix` 模式下执行

#### Step 4：更新 CLI 和模型

- 文件：`auto_pm/plc/models.py`（修改）— 新增漂移相关常量
- 文件：`auto_pm/cli/plc/__init__.py`（修改）— 无需改动，`--fix` 已有

#### Step 5：测试验证

- 对 DJ-2026-005 运行 `plc check`，确认检测到漂移
- 运行 `plc check --fix`，确认自动修复 PM_SESSION Spec Snapshot
- 运行 `plc check` 再次检查，确认 PASS

### 涉及文件

| 文件 | 操作 | 说明 |
|------|------|------|
| `auto_pm/plc/spec_snapshot.py` | 新建 | Spec Snapshot 解析器 |
| `auto_pm/plc/checker.py` | 修改 | 新增 Spec Snapshot 检查项 |
| `auto_pm/plc/repairer.py` | 修改 | 新增 Spec Snapshot 修复逻辑 |
| `auto_pm/plc/models.py` | 修改 | 新增漂移相关常量/数据类 |

### 假设与决策

1. **PM_SESSION Spec Snapshot 格式**：假设为 Markdown 表格，列名为 `规范编号`/`版本号`/`状态`，需正则解析
2. **spec_registry.json 路径**：假设在工作空间根目录下 `00_Obsidian_Base全局规范文件仓库/spec_registry.json`
3. **漂移严重级别**：主版本漂移=FAIL，次版本漂移=WARN，补丁漂移=WARN
4. **修复范围**：仅更新 PM_SESSION 中的 Spec Snapshot 版本号，不修改源码
5. **不引入 specmgr 依赖**：V2.2 再正式吸收 specmgr

### 验证步骤

1. `python -m auto_pm -w "<工作空间>" plc check DJ-2026-005` → 应显示 Spec Snapshot WARN/FAIL
2. `python -m auto_pm -w "<工作空间>" plc check DJ-2026-005 --fix` → 应自动更新 PM_SESSION
3. 再次 `plc check` → Spec Snapshot 应 PASS
4. `python -m auto_pm -w "<工作空间>" plc check --all` → 所有项目漂移检测
