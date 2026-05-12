# 自动化交付物整理 + 打包方案

## Why

### 当前痛点（已实际发生的问题）

| # | 问题 | 发生版本 | 原因 |
|---|------|---------|------|
| 1 | **分类项目数全显示0** | V2.5.9 | 交付物 DB 的 categories/library_projects 表为空，与源码DB不同步 |
| 2 | **标题栏版本号错误** | V2.5.7~V2.5.9 | app_config.json 版本未同步 version.py |
| 3 | **root_path 含旧绝对路径** | V2.5.7~V2.5.8 | DB 清理脚本只清理了源码库，未清理交付物库 |
| 4 | **路径仍指向 D 盘** | V2.5.7~V2.5.8 | 多次修复但每次手动打包都可能遗漏步骤 |

**根因**: 当前没有统一的自动化打包脚本。每次发布依赖人工执行 6-7 个离散步骤，任何一步遗漏都会导致交付物缺陷。

### 现有工具分析

| 工具 | 能力 | 缺失能力 |
|------|------|---------|
| `build.py` | PyInstaller 调用 + config/plugins 复制 | ❌ 不处理 data/、❌ 不组织交付物目录、❌ 不打ZIP、❌ 不验证 |
| `Python项目管理工具.spec` | 定义 EXE 打包配置 | ❌ datas 中无 data/ 目录、❌ 无后处理钩子 |

## What Changes — 设计一个全自动化的 `package.py`

### 一键命令目标

```bash
# 在项目根目录或 03_主程序/01_主程序核心代码 下执行：
python package.py                    # 完整打包（默认读取 version.py 版本号）
python package.py --version 2.6.0     # 指定版本号
python package.py --dry-run           # 试运行（只检查不执行）
python package.py --clean             # 清理后重新打包
```

### 完整自动化流程（10步）

```
┌─────────────────────────────────────────────────────────────┐
│                    package.py 全流程                          │
├─────────────────────────────────────────────────────────────┤
│ Phase 1: 准备与校验                                           │
│   Step 1  读取 version.py → 解析 VERSION                      │
│   Step 2  三处版本一致性校验 (version.py + app_config.json×2) │
│            → 不一致则报错终止                                   │
│                                                              │
│ Phase 2: 数据库预处理                                          │
│   Step 3  复制源码 data/project_manager.db → 交付物/data/      │
│   Step 4  清理交付物DB中的绝对路径 (root_path含盘符→清空)        │
│   Step 5  验证交付物DB数据完整性 (categories≥5, projects≥1)    │
│                                                              │
│ Phase 3: PyInstaller 打包                                      │
│   Step 6  执行 pyinstaller --noconfirm Python项目管理工具.spec  │
│   Step 7  验证 EXE 生成成功 + 文件大小检查                       │
│                                                              │
│ Phase 4: 交付物组装                                             │
│   Step 8  整理 06_交付物/01_可执行文件/ 目录                     │
│            ├── Python项目管理工具.exe (从 dist/ 复制)          │
│            ├── config/ (4个JSON文件)                           │
│            ├── data/project_manager.db (已清理+验证)           │
│            └── Projects/.gitkeep                               │
│                                                              │
│ Phase 5: 归档与记录                                            │
│   Step 9  创建 ZIP → 06_交付物打包/V{x.y.z}_{YYYYMMDD}.zip    │
│   Step 10 更新 打包版本记录.md                                  │
└─────────────────────────────────────────────────────────────┘
```

### 关键设计决策

#### 决策 1: data/ 目录不在 spec 的 datas 中

**原因**: `data/project_manager.db` 是运行时数据（会随用户使用增长），不应打包进 EXE 内部。应作为外部文件随交付物一起分发。

**实现**: 在 Step 3 中显式复制到交付物目录。

#### 决策 2: 版本校验前置失败即终止

**原因**: 历史上多次因版本号不一致导致返工。在打包最早期就强制校验三处一致。

**实现**: Step 2 读取三个文件比对，不一致则 `sys.exit(1)` 并打印差异。

#### 决策 3: DB 清理作为必经步骤

**原因**: 每次打包都必须确保交付物 DB 无旧机器的绝对路径。不能依赖"之前清理过"。

**实现**: Step 4 对交付物 DB 执行 SQL `UPDATE libraries SET root_path='' WHERE root_path LIKE '%:%'`。

#### 决策 4: dry-run 模式

**原因**: 方便在正式打包前验证所有前置条件是否满足。

**实现**: `--dry-run` 参数执行所有检查和预览但不实际修改文件或执行打包。

## Impact

### 新增文件
- `03_主程序/01_主程序核心代码/package.py` — 主打包脚本（~200行）

### 修改文件
- `Python项目管理工具.spec` — 可能微调（如需添加 data/ 到 datas）

### 不影响的文件
- `build.py` — 保留不变（底层 PyInstaller 封装）
- 所有业务代码 — 零修改

### 目录结构变化（运行时生成，非代码变更）
```
06_交付物/
  01_可执行文件/          ← package.py 自动整理
    Python项目管理工具.exe
    config/*.json
    data/project_manager.db ← 自动同步+清理
    Projects/.gitkeep
  02_发布说明/            ← 手动维护（文档不由脚本自动生成）
06_交付物打包/
  Python自动化项目管理系统_V2.5.9_20260417.zip  ← 自动创建
  打包版本记录.md         ← 自动追加记录
```

## Tasks

- [ ] Task 1: 创建 `package.py` 主脚本框架（参数解析、日志、Phase划分）
- [ ] Task 2: 实现 Phase 1 — 版本读取与一致性校验
- [ ] Task 3: 实现 Phase 2 — 数据库同步、清理、完整性验证
- [ ] Task 4: 实现 Phase 3 — PyInstaller 打包调用与结果验证
- [ ] Task 5: 实现 Phase 4 — 交付物目录整理（EXE+config+data+Projects 组装）
- [ ] Task 6: 实现 Phase 5 — ZIP归档 + 打包版本记录自动更新
- [ ] Task 7: 实现 --dry-run 模式和 --clean 模式
- [ ] Task 8: 编写使用说明并测试一次完整流程
