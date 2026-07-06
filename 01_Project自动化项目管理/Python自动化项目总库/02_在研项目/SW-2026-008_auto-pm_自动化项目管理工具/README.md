# auto-pm

统一 CLI 管理 PLC/Python 多技术栈项目的脚手架工具。

## 功能特性

- **项目 CRUD** - 新建/列表/查看/编辑/删除/补全项目元数据；自动从 PM_SESSION 推导项目阶段（developing/commissioning/production/archived）
- **PLC 项目管理** - 初始化/规范检查(LSP-907)/自动修复/文档命名标准化/Spec Snapshot 漂移检测
- **Python 项目管理** - 初始化（规范检查计划 V2.5 实现）
- **变更管理** - 变更单创建/查询/状态流转/编辑（CLI+GUI）；完整 12 状态机 + 门禁校验 + §6/§8/§9/§10 章节渲染；CLI 表格 `--full` 不截断选项
- **模板管理** - Copier 模板列表/增量更新
- **桌面 GUI** - PySide6 原生桌面应用，项目中心式导航 + 项目 CRUD + 多角色适配 + 缓存同步；变更中心含 QWizard 分步创建向导 + StatusMachineView 可视化状态机 + ApprovalTimeline 审批时间线 + PropagationView 传播链可视化 + 4 维度列表筛选（状态/领域/紧急程度/项目）
- **SQLite 索引缓存** - 增量扫描（file_mtime 判据），加速查询；变更单影响分析与审批记录持久化（impact_analysis + approval_history 两张表）
- **Dogfooding** - auto-pm 自身使用 CHG-*.md 变更单流程（已闭环 3 次：CHG-SCPT-2026-001/062/063）

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

> **注意**: `python init`/`python check` 当前为占位实现，计划 V2.5 版本交付（见 PRD 路线图）。

```bash
# 创建 Python 项目骨架（V2.5 实现）
auto-pm python init SW-2026-009 --name 数据分析工具

# 检查 Python 项目规范（V2.5 实现）
auto-pm python check SW-2026-009
```

### change - 变更管理

```bash
# 列出项目变更单（支持按状态/领域筛选；--full 标题列不截断）
auto-pm change list DJ-2026-010
auto-pm change list DJ-2026-010 --status implementing
auto-pm change list DJ-2026-010 --domain PLC
auto-pm change list DJ-2026-010 --full                # 标题列 fold 换行不截断

# 查看变更单详情（渲染 §6 影响分析 + §8 审批记录 + §9 实施记录 + §10 验证项共 10 张表）
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

# 编辑变更单（CLI 支持 8 个字符串/枚举字段；dict 字段 constraint_impacts/domain_impacts 留给 GUI）
auto-pm change edit CHG-PLC-2026-001 --background "更新的背景说明"
auto-pm change edit CHG-PLC-2026-001 --risk-level high --mitigation "增加联锁测试"
auto-pm change edit CHG-PLC-2026-001 --propagation-chain "PLC -> HMI -> DOCU"
auto-pm change edit CHG-PLC-2026-001 --urgency critical

# 状态流转（更新变更单章节并持久化状态 + DB 记录审批历史）
auto-pm change transition CHG-PLC-2026-001 --to submitted
auto-pm change transition CHG-PLC-2026-001 --to approved --approver fubai
auto-pm change transition CHG-PLC-2026-001 --to implementing --approver fubai
auto-pm change transition CHG-PLC-2026-001 --to completed --approver fubai \
  --verification-conclusion "全部通过：单元测试 + 集成测试 + 现场联调"
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

> V0.6.0 起 GUI 已迁移至 QML 运行时，V0.9.0 起引入 Facade 接口层。

- **项目中心式导航** - QML 主窗口 + 左侧侧边栏 + StackLayout 切换主区域
- **项目列表首页** - 项目卡片网格（编号/名称/技术栈徽标/版本/阶段/业务线），统计栏 + 搜索 + 筛选（ProjectListView.qml）
- **项目工作区** - Tab 容器（概览/变更/检查/文档），工程资产摘要（WorkspaceView.qml）
- **变更中心** - 变更列表 + 详情面板 + 创建/状态流转/编辑对话框（ChangeCenterView.qml）
- **变更创建向导** - 分步向导：基本信息 → 变更描述 → 提交确认（NewChangeDialog.qml）
- **StatusMachineView 可视化状态机** - 水平展示 12 状态节点 + 11 箭头；当前状态高亮 + 可达状态可点击（StatusMachineView.qml）
- **ApprovalTimeline 审批时间线** - 垂直展示审批历史：圆点+连接线+状态流转+审批人+意见+日期（ApprovalTimeline.qml）
- **PropagationView 传播链可视化** - 水平展示跨领域传播链：节点+箭头+领域中文名映射（PropagationView.qml）
- **4 维度列表筛选** - 状态 Tab + 领域 + 紧急程度 + 项目下拉筛选
- **全局功能页** - 规范中心（SpecCenterView.qml）/模板管理（TemplateView.qml）/报告中心（ReportView.qml）/系统设置（SettingsView.qml）
- **项目 CRUD 对话框** - 新建向导/编辑/导入对话框（qml/dialogs/）
- **变量表编辑器** - 8 列变量表展示 + UndoStack ≥20 步（VarTableEditorView.qml）
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
│   ├── application/                # 应用层 Facade（5 个用例编排入口）
│   │   ├── workbench_facade.py     # 驾驶舱 + 项目列表 + 项目工作台
│   │   ├── change_facade.py        # 变更创建/流转/列表/详情
│   │   ├── spec_facade.py          # 规范中心概览/检查
│   │   ├── delivery_facade.py      # 文档刷新/报告/资产摘要
│   │   └── system_facade.py        # PM_SESSION/模板/缓存管理
│   ├── cli/                        # Click CLI 入口
│   │   ├── __main__.py             # auto-pm 主入口
│   │   ├── project.py              # project 子命令组（CRUD + import）
│   │   ├── change.py               # change 子命令组（变更管理）
│   │   ├── gui.py                  # gui 命令（QML GUI 启动）
│   │   ├── plc/                    # PLC 技术栈插件
│   │   └── python/                 # Python 技术栈插件
│   ├── core/                       # 核心领域服务层
│   │   ├── project_service.py      # 项目 CRUD 服务 + 文件系统扫描
│   │   ├── dashboard_service.py    # 驾驶舱聚合服务
│   │   ├── protocols.py            # Service Protocol 接口定义
│   │   ├── paths.py                # 统一路径约定常量
│   │   └── constants.py            # 业务线/技术栈/阶段常量
│   ├── change/                     # 变更管理包（parser/generator/service 等 9 模块）
│   ├── models/                     # Pydantic v2 模型层（project/change/plc/dto/enums）
│   ├── db/                         # SQLite 索引缓存层（WAL 模式，5 张表）
│   ├── ui/                         # PySide6 QML GUI 层
│   │   ├── contracts/              # DTO/Command/Event 接口契约
│   │   ├── qml/                    # QML 视图/组件/对话框/主题/模型/桥接
│   │   ├── global_pages/           # 全局页面适配器
│   │   ├── models/                 # Qt 模型适配器
│   │   └── registry.py             # Facade 装配器
│   ├── spec/                       # 规范管理（core + services）
│   ├── plc/                        # PLC 检查/修复/标准化
│   ├── vartable/                   # 变量表解析
│   ├── config/                     # 配置（pydantic-settings）
│   ├── logging/                    # 日志 + 审计
│   └── utils/                      # 工具函数
├── templates/                      # Copier 模板仓库
│   ├── plc-standard-project/       # PLC 标准项目模板
│   ├── plc-shared-library/         # PLC 共享函数库模板
│   ├── plc-test-suite/             # PLC 测试套件模板
│   └── python-tool/                # Python 工具项目模板
├── tests/                          # 测试（111 文件，含 application/change/core/db/plc/spec 等）
├── 00_项目基础信息/                 # 项目治理文档（技术债/发布门禁/试运行）
├── 02_设计/                        # 设计真源（PRD/INT/DSN/TEC/里程碑/原型）
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
| GUI 框架 | PySide6 (QML 运行时) |
| 数据库 | SQLite3 (WAL 模式) |
| 构建 | hatchling |
| 代码质量 | ruff + mypy (strict) + pytest |

## 文档导航

> 详细索引见 [docs/归档索引.md](docs/归档索引.md)

### 设计文档（`02_设计/`，V3.0 设计真源）

| 文档 | 路径 | 说明 |
|------|------|------|
| PRD 产品需求文档 | `02_设计/001_产品需求文档_PRD.md` | 产品需求定义（V3.0.0-draft） |
| INT 接口文档 | `02_设计/002_接口文档_INT.md` | DTO/Command/Event 接口契约 |
| DSN 详细设计说明书 | `02_设计/003_详细设计说明书_DSN.md` | 五层架构详细设计 |
| TEC 技术方案文档 | `02_设计/004_技术方案文档_TEC.md` | 技术选型与方案（接口优先策略） |
| 里程碑与实施计划 | `02_设计/005_里程碑与实施计划.md` | 30 周滚动计划（M0-M9） |
| UI 架构原型 | `02_设计/006_UI架构原型.html` | HTML 交互原型（方案讨论用） |
| UI 原型说明 | `02_设计/007_UI架构原型说明.md` | 原型配套说明 |

### 项目治理文档（`00_项目基础信息/`）

| 文档 | 路径 | 说明 |
|------|------|------|
| 技术债评估报告 | `00_项目基础信息/006_技术债评估报告.md` | 技术债跟踪（34 项全部偿还） |
| 发布门禁规范 | `00_项目基础信息/007_发布门禁规范_REL.md` | 发布前质量门禁定义 |
| 试运行报告 | `00_项目基础信息/008_试运行报告_PILOT.md` | Dogfooding 试运行证据归档 |

### 项目管理文档

| 文档 | 路径 | 说明 |
|------|------|------|
| PM_SESSION | `PM_SESSION_SW-2026-008.md` | 项目会话文档（**单一状态真源**） |
| CHANGELOG | `CHANGELOG.md` | 变更日志 |

### 已废弃文档

以下文档已标记 `[DEPRECATED]`，仅供参考，请勿用于指导开发：

| 文档 | 废弃原因 | 替代文档 |
|------|----------|----------|
| `00_项目基础信息/001~005` | V2.1 设计文档，已迁移至 `02_设计/` | `02_设计/001~007` |
| `docs/example.md` | Copier 模板示例，非项目文档 | 无（可删除） |
| `docs/gui-prototype/` | V2.0 HTML 原型，已被 V3.0 原型替代 | `02_设计/006_UI架构原型.html` |
| `docs/里程碑迭代计划_V2.1.md` | V2.1 历史计划 | `02_设计/005_里程碑与实施计划.md` |
| `09_整改项/archive/` 下全部文档 | V2.0 整改/迭代报告 | `PM_SESSION_SW-2026-008.md` |

## Dogfooding 证据

auto-pm 自身使用 CHG-*.md 变更单流程管理迭代（M4 Dogfooding 持续化）。已完成的闭环：

| 变更单 | 内容 | 状态 |
|--------|------|------|
| CHG-SCPT-2026-001 | M0 基座清理（TD-T01~T04 修复 + ruff/mypy 清理 + 元测试升级） | ✅ 已归档 |
| CHG-SCPT-2026-062 | M3.5 真源收口 + TD-T04 复发修复 + CHG-001 内容补全 | ✅ 已关闭 |
| CHG-SCPT-2026-063 | phase 修复 + ruff 清零 + M4 Dogfooding 启动 | ✅ 已关闭 |

每个里程碑必须经过 CHG-*.md 流程（spec.md §9.1 固定模板 10 步：创建→submitted→under_review→approved→implementing→pending_acceptance→accepting→completed→closed→回写 PM_SESSION）。

## 工具链关系

| 工具 | 编号 | 与 auto-pm 关系 |
|------|------|----------------|
| pm-mgr | SW-2026-007 | **已取代** - auto-pm 完全替代 pm-mgr |
| plc-check | — | **已取代** - auto-pm plc check/repair/standardize 替代 |
| specmgr | SW-2026-006 | **独立** - 规范管理工具，与 auto-pm 互补；V2.2 规范中心整合后吸收 |
| plc-var-parser | SW-2026-001 | **独立** - 变量表解析工具；V2.3 变量表整合后吸收 |

## 版本管理

本项目遵循 [语义化版本](https://semver.org/)，使用 [Conventional Commits](https://www.conventionalcommits.org/) 自动生成变更日志。

提交信息规范见工作空间 `.trae/rules/git-commit-message.md`。
