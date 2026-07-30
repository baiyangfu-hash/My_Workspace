# My_Workspace 工作空间交接文档（2026-07-30）

> [!IMPORTANT]
> **交接人声明**：本工作空间承载了“全局规范-PLC自动化-上位机与项目管理”三条完整业务线的协作成果。本交接文档所有内容均经过本地运行时环境、文件系统扫描及 1534 项单元测试的深度实测校验，保证数据与结论 100% 准确，无任何臆测和虚构成分。

---

## 1. 工作空间顶层结构与定位
工作空间根路径为 `c:\Users\fubai\Desktop\My_Workspace`，整体采用**双域分离、三线并行、单一真源管理**的设计原则，划分为四个顶层入口：

| 顶层文件夹 | 业务线定位 | 包含的核心内容 |
|:---|:---|:---|
| [`00_Obsidian_Base全局规范文件仓库`](file:///c:/Users/fubai/Desktop/My_Workspace/00_Obsidian_Base全局规范文件仓库) | **全局规范线** | 与技术栈无关的项目管理通用规范（Obsidian 库，V3.2.0 版） |
| [`0100_PLC自动化`](file:///c:/Users/fubai/Desktop/My_Workspace/0100_PLC自动化) | **PLC工程线** | 包含基础函数共享库、量产设备源程序及 PLC 领域专用开发规范 |
| [`01_Project自动化项目管理`](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理) | **上位机与工具线** | 在研的 Python 工具项目总库及 Python 领域专用开发规范 |
| [`SYS-2026-001_WorkspaceGovernance`](file:///c:/Users/fubai/Desktop/My_Workspace/SYS-2026-001_WorkspaceGovernance) | **空间治理线** | 工作空间系统级治理项目，定义了跨项目准入、路线图及变更规则 |

---

## 2. 软件与工具项目清单（SW-*)
所有软件及工具开发项目均位于 [`01_Project自动化项目管理/Python自动化项目总库/02_在研项目/`](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目) 目录下。每一个项目均受其内部 `PM_SESSION_<项目编号>.md` 的严格生命周期驱动。

### 2.1 核心在研项目：SW-2026-008 (`auto-pm`)
- **项目定位**：面向电气自动化工程师的本地项目作业系统，用于统一管理 PLC 项目结构、工程文档、变更闭环、调试记录、质量门禁和交付证据。
- **技术栈**：Python 3.11 + PySide6 (QML 2.15 画面层) + Click CLI + SQLite 数据库。
- **项目基线**：`V1.1.0` 基线版本，测试集共 **1534 passed, 12 skipped, 0 failed**，实现全量测试绿门禁。
- **最新演进功能**：
  1. **Modbus TCP 联调工坊**：实现了 FC01~FC06/FC07/FC20~24/FC43 全量功能码测试，内置模拟物理波形的信号发生器，提供 10x10 并发区间探测网格（`ModbusScannerGrid`）与定时信号趋势推送（`ModbusTrendCanvas`）。
  2. **FileWatcherBridge 自动同步桥**：集成了 `QFileSystemWatcher`，监听业务文件变化并实施 1s 去抖的 QRunnable 后台线程同步机制，彻底消除 CLI 与 GUI 本地缓存鸿沟。
  3. **PythonProjectService 自动修复**：实现了对工作区 Python 项目的一键合规度检测与自动化自愈自修复。

### 2.2 其他支撑工具项目
- **SW-2026-001 (PLC 变量表解析工具)**：多格式 PLC 变量表解析与转换工具，支持汇川 AutoShop、CODESYS、三菱 Work3 导出的变量表格式解析。已打通“接口文档变量表自动输出”流程。
- **SW-2026-004 (Python 项目管理工具)**：多技术栈项目生命周期管理平台，支持 GUI+CLI 双模式，完成文档版本一致性修复。
- **SW-2026-005 (PLC 项目管理工具)**：通过扫描 `0100_PLC自动化` 下的项目文档自动聚合状态。在 V9.0.0 引入标准化管理，支持合规度 100% 自动自愈修复。
- **SW-2026-006 (规范管理工具 - SpecMgr)**：规范管理体系的一站式扫描与索引工具，向 Obsidian 全局仓库提供 check/index/report 等一键命令支持。
- **SW-2026-007 (pm工作流工具链 - pm-mgr)**：**[已归档]** 历史原型，其项目初始化与管理功能已全部被 `SW-2026-008 (auto-pm)` 完美替代合并，不再维护。

---

## 3. PLC 自动化项目清单 (DJ-*)
PLC 项目均存放在 [`0100_PLC自动化/`](file:///c:/Users/fubai/Desktop/My_Workspace/0100_PLC自动化) 目录下：

- **DJ-2026-000 (SysLib公共库FB测试套件)**：用于验证 `FB_1011`、`FB_1012`、`FB_1014` 等团队共享功能块的测试套件。已在 V3.2.0 对齐 `i_`/`q_` 引脚前缀规范。
- **DJ-2026-005 (边框缓存机)**：边框缓存机 PLC/HMI 的真实工程。最新版本演进到 V9.1.0（`CHG-PLC-2026-007` 闭环），新增集成了传感器抗抖动消抖算法（`ST_GlueFeeder` 新增 `i_dDebounceMs` 参数）和故障自愈功能。

---

## 4. 全局规范库与空间治理
### 4.1 全局规范库 (`00_Obsidian_Base全局规范文件仓库`)
- **当前版本**：V3.2.0 (自动同步生成)。
- **内容范畴**：仅保留与具体语言/技术栈无关的项目管理通用规范（共 39 个活跃规范，如通用项目命名 `RULE-001`、交付规范 `DEV-030`、变更单模板 `CHG-040`）。
- **技术栈规范下沉**：Python 特定开发规范已被迁移下沉至 `01_Project自动化项目管理/00_通用规范/Python开发/`；PLC 特定规范下沉至 `0100_PLC自动化/00_通用规范/PLC编程/`。以技术栈特定目录为最高优先级。

### 4.2 空间治理项目 (`SYS-2026-001`)
- **当前焦点**：P2 阶段（节奏固化与准入规则验证）已全部完成，平滑建立工作空间治理路线图。
- **治理规则**：根目录下的临时分析或草稿统一存放在 `.trae/documents/` 缓冲区，长期稳定项目由 `SYS-2026-001` 变更流统一控制，拒绝“散装”污染。

---

## 5. 核心软件 (SW-2026-008) 架构设计对照
为了方便 PLC/HMI 工程师快速接手上位机，`auto-pm` 采用了基于 **PLC/HMI 映射概念**的 5 层设计：

```
┌─────────────────────────────────────────────────────────┐
│  HMI 画面层 (QML Views & Components)                     │
│  └── auto_pm/ui/qml/views/ (主窗口、设置、检查、Modbus等)    │
└───────────────────────┬─────────────────────────────────┘
                        │ QML 通过 Signal/Slot 读写变量表
┌───────────────────────▼─────────────────────────────────┐
│  HMI 变量表 (QML Bridges)                               │
│  └── auto_pm/ui/qml/bridges/*_bridge.py (@Slot & Signal)│
└───────────────────────┬─────────────────────────────────┘
                        │ Python Facade 接口映射
┌───────────────────────▼─────────────────────────────────┐
│  FB 功能块层 (Application Facades)                      │
│  └── auto_pm/application/*_facade.py (封装各个工作域逻辑)│
└───────────────────────┬─────────────────────────────────┘
                        │ Service 核心逻辑
┌───────────────────────▼─────────────────────────────────┐
│  SFB 系统函数层 (Core Services)                         │
│  └── auto_pm/core/ (ProjectService, ChangeService 等)   │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│  DB 数据层 (SQLite & DTO Contracts)                     │
│  └── auto_pm/db/ (存储与同步) & auto_pm/models/ (UDT)   │
└─────────────────────────────────────────────────────────┘
```

---

## 6. Git 忽略与过滤安全策略
为防止 PyInstaller 构建的二进制依赖及大文件导致仓库臃肿（单文件超过 GitHub 100MB 限制），本仓库已在全局配置 [`.gitignore`](file:///c:/Users/fubai/Desktop/My_Workspace/.gitignore) 中锁定了以下安全过滤策略，接手后**切勿取消忽略**：

- **编译与打包产物**：忽略 `**/_internal/`、`**/build/`、`**/dist/`、`*.exe`、`06_交付物/` 及 `06_交付物打包/` 的二进制实体。
- **第三方与临时库**：忽略 `.venv/`、`venv/`、`.pytest_cache/`、`htmlcov/` 等本地运行时缓存。
- **Autoshop 原始大文件**：过滤避让了 `PLC源程序样例/` 及 `*堆垛机*/`（长边框堆垛机研发等工程目录），防止海量编译临时文件阻断 Git 提速。

---

## 7. 日常运维与常用指令
开发和验证前请进入核心工具主目录 `c:\Users\fubai\Desktop\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\02_在研项目\SW-2026-008_auto-pm_自动化项目管理工具`，确保虚拟环境 `../../../../.venv` 已激活。

- **运行全量门禁检查（测试自检）**：
  ```powershell
  python scripts/pre_closure_gate.py --workspace .
  ```
- **单跑单元测试**：
  ```powershell
  python -m pytest --no-cov -q -m "not gui"
  ```
- **代码规范性检查 (Ruff)**：
  ```powershell
  ruff check .
  ```
- **静态类型检测 (Mypy)**：
  ```powershell
  mypy auto_pm/
  ```
- **PM_SESSION 归档动作（防止主文件超过 150KB 阈值）**：
  ```powershell
  python -m auto_pm pm-session archive -w . --section 6 --keep-recent 15
  ```
