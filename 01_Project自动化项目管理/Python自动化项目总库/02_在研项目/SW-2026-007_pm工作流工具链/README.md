# pm-mgr — pm-workflow 项目工作流工具链

> **归档通知**: 本项目（SW-2026-007 pm-mgr）已被 SW-2026-008 auto-pm 取代。
> 所有 pm-mgr 功能已迁移至 auto-pm，pm-workflow 技能已更新为调用 auto-pm。
> 本项目不再维护，仅供历史参考。

纯 Python CLI 工具，为 pm-workflow 技能提供项目初始化、旧项目补完、健康检查、类型检测和 Spec Snapshot 管理能力。

- **项目编号**：SW-2026-007
- **版本**：0.1.0
- **依赖**：Python ≥ 3.11 + click ≥ 8.0（无数据库、无 GUI）
- **模板源**：`.trae/project-bootstrap/`

## 安装

```powershell
cd SW-2026-007_pm工作流工具链
pip install -e .
```

安装后 `pm-mgr` 命令全局可用。

## 命令接口

所有命令共享全局选项 `-w / --workspace <工作空间根目录>`，也可通过环境变量 `PM_MGR_WORKSPACE` 设置。若两者均未指定，自动向上查找包含 `.trae/` 的目录。

---

### `pm-mgr init` — 初始化新项目

从 `.trae/project-bootstrap/` 模板创建完整项目骨架。

```
pm-mgr init <项目目录> -t <software|plc> -i <项目编号> -n <项目名称> [选项]
```

| 参数 | 必填 | 说明 |
|------|------|------|
| `PROJECT_DIR` | 是 | 项目根目录路径 |
| `-t, --type` | 是 | 项目类型：`software` 或 `plc` |
| `-i, --id` | 是 | 项目编号，如 `SW-2026-001` |
| `-n, --name` | 是 | 项目名称 |
| `-o, --owner` | 否 | 项目负责人（默认 `Pending`） |
| `-l, --oneliner` | 否 | 项目一句话描述（默认 `Pending`） |
| `-f, --force` | 否 | 目录非空时仍强制执行（不覆盖已有文件） |

**创建的产物**：

| 项目类型 | 目录数 | 文档模板 | 骨架文件 | 其他 |
|---------|--------|---------|---------|------|
| software | 9 个目录 | 立项表、PRD、测试计划 | README、pyproject.toml、`__init__.py` ×2 | `.gitkeep` ×2 |
| plc | 24 个目录 | 立项表、需求分析、IO分配表、PLC设计总文档、调试计划、问题跟踪 | README、.plc.json、版本变更台帐 | — |

两种类型都会自动创建 `.github/hooks/`（4 个协作脚本）和 `.trae/handoffs/`，并在 PM_SESSION 中自动填充 Spec Snapshot（版本号从 `spec_registry.json` 读取）。

**示例**：

```powershell
pm-mgr -w "C:\Workspace" init ".\MyProject" -t software -i SW-2026-008 -n "我的工具" -l "一个CLI工具"
pm-mgr -w "C:\Workspace" init ".\DJ-2026-010" -t plc -i DJ-2026-010 -n "某产线PLC" --force
```

---

### `pm-mgr retrofit` — 旧项目补完

为已有项目注入连续性机制，**仅添加文件，不修改现有内容**。

```
pm-mgr retrofit <项目目录> [-f]
```

| 参数 | 必填 | 说明 |
|------|------|------|
| `PROJECT_DIR` | 是 | 项目根目录路径（必须存在） |
| `-f, --force` | 否 | 跳过生命周期检查（archived 项目也强制执行） |

**注入内容**：

1. `.github/hooks/` — 4 个 hooks 脚本 + hooks.json（若不存在）
2. `.trae/handoffs/` — 交接目录（若不存在）
3. PM_SESSION 中的 Spec Snapshot 区块（若缺失）

**行为**：
- 已存在的 hooks 和 handoffs 自动跳过（幂等）
- 项目 lifecycle 为 `archived` 时默认跳过，需 `--force` 强制执行
- 对现有文件零侵入

**示例**：

```powershell
# 补完活跃项目
pm-mgr -w "C:\Workspace" retrofit ".\0100_PLC自动化\DJ-2026-000"

# 强制补完已归档项目
pm-mgr -w "C:\Workspace" retrofit ".\0100_PLC自动化\DJ-2026-000" --force
```

---

### `pm-mgr check` — 健康检查

检查项目连续性机制是否完整。

```
pm-mgr check <项目目录> [--fix]
```

| 参数 | 必填 | 说明 |
|------|------|------|
| `PROJECT_DIR` | 是 | 项目根目录路径 |
| `--fix` | 否 | 自动修复缺失项（内部调用 retrofit 逻辑） |

**检查项**：

| 检查项 | 判定标准 |
|--------|---------|
| PM_SESSION | `PM_SESSION*.md` 文件存在 |
| hooks | `.github/hooks/hooks.json` + 4 个脚本全部存在 |
| handoffs | `.trae/handoffs/` 目录存在 |
| Spec Snapshot | PM_SESSION 中含 `## Spec Snapshot` 区块 |

**输出示例**：

```
项目健康检查: C:\Workspace\0100_PLC自动化\DJ-2026-000
==================================================
  [PASS] PM_SESSION
         找到: PM_SESSION_DJ-2026-000.md
  [PASS] hooks
         所有 4 个 hooks 脚本就绪
  [PASS] handoffs
         handoffs 目录就绪
  [PASS] Spec Snapshop
         Spec Snapshot 区块存在
==================================================
结果: 全部通过
```

---

### `pm-mgr detect` — 项目类型检测

通过多信号判据自动识别项目类型。

```
pm-mgr detect <项目目录>
```

**输出**：`software` / `plc` / `unknown`

**检测优先级（从高到低）**：

| 优先级 | 信号 | 结果 |
|--------|------|------|
| 1 | `.plc.json` 存在（递归搜索） | `plc` |
| 2 | `pyproject.toml` 存在（递归搜索子目录） | `software` |
| 3 | `*.scl` / `*.db` 文件存在 | `plc` |
| 4 | `main.py` / `package.json` 存在 | `software` |
| 5 | PM_SESSION 上下文推断 | 按内容判定 |

**示例**：

```powershell
pm-mgr -w "C:\Workspace" detect ".\0100_PLC自动化\01_SharedLibraries"
# → plc

pm-mgr -w "C:\Workspace" detect ".\01_Project自动化项目管理\...\SW-2026-005_PLC项目管理工具"
# → software
```

---

### `pm-mgr snapshot` — 刷新 Spec Snapshot

独立更新项目的 Spec Snapshot，从 `spec_registry.json` 读取最新版本号写入 PM_SESSION。

```
pm-mgr snapshot <项目目录>
```

- 若 PM_SESSION 已含 Spec Snapshot → 替换 `(待填充)` 为实际版本号
- 若 PM_SESSION 缺失 Spec Snapshot → 在末尾追加完整区块
- 不影响 PM_SESSION 其他内容

---

## 规范引用

| spec_id | 说明 |
|---------|------|
| PROJ-016 | 通用项目结构模板 |
| PRD-001 | 产品需求文档模板 |
| DEV-031 | 通用测试规范 |
| DEV-032 | GUI测试方案标准 |
| REQ-020 | 通用需求分析文档模板 |
| LSP-905 | SCL编程规范 |

以上规范版本号在 init/retrofit 时从 `00_Obsidian_Base全局规范文件仓库/spec_registry.json` 自动读取。

## 目录结构

```
SW-2026-007_pm工作流工具链/
├── pm_mgr/
│   ├── __init__.py         # 版本号
│   ├── __main__.py         # python -m pm_mgr 入口
│   ├── cli.py              # Click CLI 主入口，5个子命令注册
│   ├── bootstrap.py        # 模板渲染 + 目录生成
│   ├── detect.py           # 项目类型多信号检测
│   ├── retrofit.py         # 旧项目补完逻辑
│   ├── snapshot.py         # Spec Snapshot 读写
│   └── check.py            # 健康检查
├── pyproject.toml           # 项目配置 + 依赖声明
└── README.md                # 本文件
```
