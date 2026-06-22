# auto-pm

统一 CLI 管理 PLC/Python 多技术栈项目的脚手架工具。

## 功能特性

- **项目 CRUD** - 新建/列表/查看/编辑/删除/补全项目元数据
- **PLC 项目管理** - 初始化/规范检查(LSP-907)/自动修复/文档命名标准化
- **Python 项目管理** - 初始化（规范检查占位，V1.2.0 实现）
- **变更管理** - 变更单创建/查询/状态流转（完整状态机+门禁校验）
- **模板管理** - Copier 模板列表/增量更新
- **桌面 GUI** - PySide6 原生桌面应用，项目中心式导航 + 项目 CRUD + 多角色适配 + 缓存同步
- **SQLite 索引缓存** - 增量扫描（file_mtime 判据），加速查询

## 安装

### 开发模式安装

```bash
# 克隆仓库
git clone <repo-url>
cd SW-2026-008_auto-pm_自动化项目管理工具

# 激活工作空间虚拟环境
& "<工作空间根>\.venv\Scripts\Activate.ps1"

# 安装为可编辑模式
pip install -e .
```

### 依赖

- Python >= 3.11
- Click >= 8.1.7
- Rich >= 14
- Pydantic >= 2.10.6
- pydantic-settings >= 2.6.1
- PyYAML >= 6.0
- Copier >= 9.7.1,<10
- PySide6 >= 6.8,<7

## CLI 使用

### 全局选项

```bash
auto-pm -w <workspace> <command>   # 指定工作空间根目录
auto-pm -v, --version              # 显示版本号
auto-pm -h, --help                 # 显示帮助
```

`-w` 必须放在子命令之前。也可通过环境变量 `AUTO_PM_WORKSPACE` 指定。

### project - 项目管理

```bash
# 列出工作空间内所有项目（支持业务线/技术栈筛选）
auto-pm project list
auto-pm project list --business-line SW       # 按业务线筛选（SW/DJ/ZD/XT/WX）
auto-pm project list --stack plc              # 按技术栈筛选（plc/python）

# 创建新项目（调用 Copier 模板生成骨架）
auto-pm project create --stack plc --id DJ-2026-010 --name 边框缓存机
auto-pm project create --stack python --id SW-2026-009 --name 数据分析工具
auto-pm project create --stack plc --id DJ-2026-010 --name 边框缓存机 --dry-run  # 预览模式

# 查看项目详情（支持 JSON 输出）
auto-pm project show DJ-2026-010
auto-pm project show DJ-2026-010 --json

# 编辑项目元数据（写入 .copier-answers.yml）
auto-pm project edit DJ-2026-010 --phase 调试中
auto-pm project edit DJ-2026-010 --desc "新描述" --version V1.1.0

# 删除项目（破坏性操作，需 --confirm）
auto-pm project delete DJ-2026-010 --confirm

# 为已有项目补全 .copier-answers.yml 元数据文件
auto-pm project retrofit DJ-2026-010

# 导入已有项目目录（复制到 02_在研项目/ 并补全元数据）
auto-pm project import /path/to/existing/project
auto-pm project import /path/to/existing/project --move         # 移动而非复制
auto-pm project import /path/to/existing/project --business-line SW  # 指定业务线
```

### plc - PLC 项目管理（LSP-907）

```bash
# 创建 PLC 项目骨架（调用 Copier plc-standard 模板）
auto-pm plc init DJ-2026-010 --name 边框缓存机

# 检查项目结构是否符合 LSP-907 规范
auto-pm plc check DJ-2026-010
auto-pm plc check DJ-2026-010 --json
auto-pm plc check --all              # 检查工作空间所有 PLC 项目

# 自动修复项目结构问题
auto-pm plc repair DJ-2026-010
auto-pm plc repair DJ-2026-010 --rename    # 确认文件重命名（破坏性操作）
auto-pm plc repair DJ-2026-010 --dry-run   # 仅预览不执行

# 文档命名标准化（默认仅预览，--apply 执行重命名）
auto-pm plc standardize DJ-2026-010
auto-pm plc standardize DJ-2026-010 --apply
```

### python - Python 项目管理

> **注意**: `python init`/`python check` 当前为占位实现，计划 V1.2.0 版本交付。

```bash
# 创建 Python 项目骨架（V1.2.0 实现）
auto-pm python init SW-2026-009 --name 数据分析工具

# 检查 Python 项目规范（V1.2.0 实现）
auto-pm python check SW-2026-009
```

### change - 变更管理

```bash
# 列出项目变更单（支持按状态/领域筛选）
auto-pm change list DJ-2026-010
auto-pm change list DJ-2026-010 --status implementing
auto-pm change list DJ-2026-010 --domain PLC

# 查看变更单详情
auto-pm change show CHG-PLC-2026-001

# 创建变更单（生成 CHG-*.md 文件并更新台帐）
auto-pm change create \
  --pid DJ-2026-010 \
  --domain PLC \
  --nature REQ \
  --scope PLC \
  --applicant fubai \
  --background "新增输送线急停逻辑" \
  --necessity "安全规范要求"

# 状态流转（更新变更单章节并持久化状态）
auto-pm change transition CHG-PLC-2026-001 --to submitted
auto-pm change transition CHG-PLC-2026-001 --to approved --approver fubai
auto-pm change transition CHG-PLC-2026-001 --to implementing --approver fubai
auto-pm change transition CHG-PLC-2026-001 --to completed --approver fubai
```

### template - 模板管理

```bash
# 列出可用 Copier 模板
auto-pm template list

# 对已有项目执行 Copier 模板增量更新
auto-pm template update DJ-2026-010
auto-pm template update DJ-2026-010 --overwrite
```

### gui - 桌面 GUI

```bash
# 启动 GUI 桌面应用
auto-pm gui
auto-pm gui --debug    # 调试模式（开启日志详细输出）
```

## GUI 功能

- **项目中心式导航** - QMainWindow + 左侧侧边栏 + QStackedWidget 切换主区域
- **项目列表首页** - 项目卡片网格（编号/名称/技术栈徽标/版本/阶段/业务线），统计栏 + 搜索 + 筛选
- **项目工作区** - Tab 容器（概览/变更/检查/文档 四 Tab）
- **变更中心** - 变更列表 + 详情面板 + 创建对话框 + 状态流转对话框
- **全局功能页** - 规范中心/模板管理/报告中心/系统设置骨架页
- **项目 CRUD 对话框** - 新建/编辑/删除/导入四个对话框（ui/dialogs/）
- **多角色适配** - 角色切换菜单（项目经理/PLC工程师/Python工程师/规范编辑），角色-Tab 映射
- **DB 缓存优先** - 优先读 SQLite 索引缓存，缺失时回退文件系统扫描
- **缓存同步** - 工具栏同步按钮，调用 SyncService 增量扫描（file_mtime 判据）

## 开发指南

### 测试

```bash
# 运行测试
task test

# 运行测试并查看覆盖率
task test
task coverage
```

### 代码质量

```bash
# 格式化代码
task lint-fix

# Lint 检查
task qa

# 类型检查
mypy auto_pm

# 运行 pre-commit
uv run pre-commit run --all-files
```

### 项目结构

```
auto-pm/
├── auto_pm/                        # 主包
│   ├── cli/                        # Click CLI 入口
│   │   ├── __main__.py             # auto-pm 主入口
│   │   ├── project.py              # project 子命令组（CRUD + import）
│   │   ├── change.py               # change 子命令组（变更管理）
│   │   ├── gui.py                  # gui 命令（PySide6 启动）
│   │   ├── template.py             # template 子命令组（模板管理）
│   │   ├── plc/                    # PLC 技术栈插件
│   │   └── python/                 # Python 技术栈插件
│   ├── core/                       # 核心共享层
│   │   ├── project_service.py      # 项目 CRUD 服务 + 文件系统扫描
│   │   └── template_service.py     # Copier 模板调度
│   ├── change/                     # 变更管理包（7 模块）
│   ├── models/                     # Pydantic v2 模型层
│   ├── db/                         # SQLite 索引缓存层
│   ├── ui/                         # PySide6 GUI 层（8 子模块：workspace/global_pages/widgets/dialogs/models/navigation/project_list/change_center）
│   ├── plc/                        # PLC 检查/修复
│   ├── config/                     # 配置
│   ├── logging/                    # 日志
│   └── utils/                      # 工具函数
├── templates/                      # Copier 模板仓库
│   ├── plc-standard/               # PLC 标准项目模板
│   └── python-tool/                # Python 工具项目模板
├── tests/                          # 测试
├── 00_项目基础信息/                 # 项目自身文档
└── pyproject.toml                  # hatchling 构建配置
```

### 技术栈

| 类别 | 技术 |
|------|------|
| CLI 框架 | Click |
| 终端输出 | Rich |
| 数据模型 | Pydantic v2 |
| 配置管理 | pydantic-settings |
| 模板引擎 | Copier + Jinja2 |
| GUI 框架 | PySide6 |
| 数据库 | SQLite3 (WAL 模式) |
| 构建 | hatchling |
| 代码质量 | ruff + mypy (strict) + pytest |

## 文档导航

> 详细索引见 [docs/归档索引.md](docs/归档索引.md)

### 当前有效文档

| 文档 | 路径 | 说明 |
|------|------|------|
| PRD 产品需求文档 | `00_项目基础信息/001_产品需求文档_PRD.md` | 产品需求定义 |
| INT 接口文档 | `00_项目基础信息/002_接口文档_INT.md` | CLI/Service/Model 接口声明 |
| DSN 详细设计说明书 | `00_项目基础信息/003_详细设计说明书_DSN.md` | 模块详细设计 |
| TEC 技术方案文档 | `00_项目基础信息/004_技术方案文档_TEC.md` | 技术选型与方案 |
| PM_SESSION | `PM_SESSION_SW-2026-008.md` | 项目会话文档（单一真源） |
| 里程碑迭代计划 | `docs/里程碑迭代计划_V2.1.md` | V2.1 里程碑计划与执行记录 |
| CHANGELOG | `CHANGELOG.md` | 变更日志 |

### 已废弃文档

以下文档已标记 `[DEPRECATED]`，仅供参考，请勿用于指导开发：

| 文档 | 废弃原因 | 替代文档 |
|------|----------|----------|
| `docs/example.md` | Copier 模板示例，非项目文档 | 无（可删除） |
| `docs/gui-prototype/` | V2.0 HTML 原型，已被实际 UI 替代 | `auto_pm/ui/` |
| `09_整改项/V2.0-全功能自动化测试计划.md` | 含已删除的角色系统用例 | `docs/里程碑迭代计划_V2.1.md` |
| `09_整改项/GUI-V2.0-测试执行报告.md` | V2.0 测试结果，不再反映当前状态 | `docs/里程碑迭代计划_V2.1.md` |
| `09_整改项/archive/` 下全部文档 | V2.0 整改/迭代报告，问题已修复 | `docs/里程碑迭代计划_V2.1.md` |

## 工具链关系

| 工具 | 编号 | 与 auto-pm 关系 |
|------|------|----------------|
| pm-mgr | SW-2026-007 | **已取代** - auto-pm 完全替代 pm-mgr |
| plc-check | — | **已取代** - auto-pm plc check/repair/standardize 替代 |
| specmgr | SW-2026-006 | **独立** - 规范管理工具，与 auto-pm 互补 |

## 版本管理

本项目遵循 [语义化版本](https://semver.org/)，使用 [Conventional Commits](https://www.conventionalcommits.org/) 自动生成变更日志。

提交信息规范见工作空间 `.trae/rules/git-commit-message.md`。
