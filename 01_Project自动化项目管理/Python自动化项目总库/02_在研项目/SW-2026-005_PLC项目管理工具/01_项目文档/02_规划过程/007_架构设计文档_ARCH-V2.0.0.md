# 架构设计文档 ARCH-V2.0.0

> **项目**: SW-2026-005 PLC项目管理工具
> **版本**: V2.0.0 | **日期**: 2026-05-22
> **状态**: 当前运行版本
> **变更**: V2.0深度审查 — Controller模式+cleanup架构+EventBus统一+死代码清理

---

## 1. 系统概述

### 1.1 设计目标

构建一个**高内聚、低耦合、可扩展**的PLC项目管理桌面应用，支持：
- 项目全生命周期管理（创建→开发→诊断→交付）
- IEC 61131-3 SCL代码规范检查与编辑
- 标准化文档自动生成
- 项目健康度多维度诊断

### 1.2 架构原则

| 原则 | 实现方式 |
|------|----------|
| **单一职责** | 每个模块仅负责一个明确的功能域 |
| **开闭原则** | 通过策略模式/注册表模式实现扩展点 |
| **依赖倒置** | 上层依赖抽象接口，不依赖具体实现 |
| **事件驱动** | EventBus 实现模块间松耦合通信 |

---

## 2. 架构视图

### 2.1 分层架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    表现层 (Presentation)                    │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────┐   │
│  │MainWindow│  │Dashboard │  │ Dialogs / Widgets       │   │
│  │          │  │          │  │ (5个Widget + 4个Dialog)  │   │
│  └────┬─────┘  └────┬─────┘  └────────────┬─────────┘   │
│       │             │                      │               │
│  ┌────▼─────────────▼──────────────────────▼─────────┐   │
│  │  managers/ (MenuManager/ToolbarManager)            │   │
│  │  + controllers/ (3个Controller: Project/Sync/      │   │
│  │                   Dashboard)                        │   │
│  └───────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                    业务层 (Business)                         │
│                                                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │ProjectSvc│ │DiagnoSvc│ │DocService│ │SpecCheckSvc  │   │
│  │          │ │          │ │          │ │              │   │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────┬───────┘   │
│       │            │           │              │            │
│  ┌────▼────────────▼───────────▼──────────────▼────────┐   │
│  │  services/ (共9个业务服务)                            │   │
│  │  + SyncEngine + ChangeService (sync/)                │   │
│  └──────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                    核心层 (Core)                             │
│                                                             │
│  ┌────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐    │
│  │Application│ │SettingsMgr│ │ConfigLoad│ │ EventBus     │    │
│  │(生命周期)│ │(配置持久化)│ │(配置加载)│ │(事件总线)    │    │
│  └────────┘ └──────────┘ └──────────┘ └──────────────┘    │
├─────────────────────────────────────────────────────────────┤
│                    数据层 (Data)                             │
│                                                             │
│  ┌────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐    │
│  │ Project│ │ Document│ │ Template│ │ Variable     │    │
│  │ Model  │ │ Model    │ │ Model    │ │ Model        │    │
│  ├────────┤ ├──────────┤ ├──────────┤ ├──────────────┤    │
│  │TestCase│ │TestResult│ │Diagnostic│ │ HealthMetric │    │
│  │ Model  │ │ Model    │ │ Report   │ │ Model        │    │
│  └────────┘ └──────────┘ └──────────┘ └──────────────┘    │
├─────────────────────────────────────────────────────────────┤
│                  基础设施层 (Infrastructure)                   │
│                                                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐  │
│  │ parsers/     │ │ checkers/    │ │ diagnostics/          │  │
│  │ ST/Variable/ │ │ 6 Checkers   │ │ LSPCompat/HealthAnalyzer│  │
│  │ SpecDoc/Test│ │ + Registry  │ │                       │  │
│  ├──────────────┤ ├──────────────┤ ├──────────────────────┤  │
│  │ sync/        │ │              │ │                       │  │
│  │ VersionExtr  │ │              │ │                       │  │
│  │ VersionCheck │ │              │ │                       │  │
│  │ SyncEngine   │ │              │ │                       │  │
│  │ SyncCLI      │ │              │ │                       │  │
│  │ fb_registry  │ │              │ │                       │  │
│  ├──────────────┤ ├──────────────┤ ├──────────────────────┤  │
│  │ utils/       │ │              │ │                       │  │
│  │ Logger/File  │ │              │ │                       │  │
│  │ Utils/PathRes│ │              │ │                       │  │
│  │ olver/Valid.│ │              │ │                       │  │
│  └──────────────┘ └──────────────┘ └──────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Controller模式架构（V2.0-R2 新增）

MainWindow采用薄壳架构，业务逻辑委托给3个Controller：

```
┌─────────────────────────────────────────────┐
│              MainWindow (薄壳)               │
│  - 布局构建                                   │
│  - closeEvent → _cleanup_resources()         │
├──────────┬──────────┬───────────────────────┤
│ Project  │  Sync    │  Dashboard            │
│Controller│Controller│  Controller           │
│          │          │                       │
│ 新建/打开 │ 版本检查 │ 统计卡片更新          │
│ 项目树   │ CHG/IFC  │ 最近项目刷新          │
│ 保存     │ 同步报告 │ 快捷操作              │
└──────────┴──────────┴───────────────────────┘
```

### 2.3 资源清理架构（V2.0-R2 新增）

窗口关闭时统一清理后台资源，防止COM异常：

```
MainWindow.closeEvent
  └── _cleanup_resources()
       ├── DiagnosticPanel.cleanup()
       │    ├── Worker: cancel → disconnect → wait(2s) → None
       │    ├── ScoreRingWidget.cleanup(): _animation_timer.stop()
       │    └── BarChartWidget.cleanup(): _anim_timer.stop()
       ├── SpecCheckPanel (Dock).cleanup()
       └── SpecCheckPanel (Tab).cleanup()
```

### 2.4 模块清单（V2.0 更新）

| 目录 | 模块列表 | 变更说明 |
|------|----------|----------|
| services/ | project_service, template_service, document_service, diagnostic_service, spec_checker_service, variable_service, spec_service, artifact_registry_service, change_service | 删除 hmi_service/plc_service/test_management_service，保留9个 |
| ui/controllers/ | \_\_init\_\_, dashboard_controller, project_controller, sync_controller | V2.0-R2 新增 |
| sync/ | version_extractor, version_checker, db_parser, session_parser, ifc_generator, chg_generator, sync_engine, sync_cli, sync_report, fb_registry | V2.0-R1 新增 fb_registry |
| ui/widgets/ | diagnostic_panel, spec_check_panel, st_editor, project_tree, document_editor | 删除 hmi_mapper/io_table/test_runner_panel/variable_checker，保留5个 |

### 2.5 模块依赖关系

```
                    ┌─────────────┐
                    │   main.py    │
                    └──────┬──────┘
                           │ 调用
                    ┌──────▼──────┐
                    │ Application  │
                    │  .run()     │
                    └──────┬──────┘
                           │ 委托
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │ run_gui()│  │load_config│  │init_logger│
        └─────┬────┘  └──────────┘  └──────────┘
              │ 创建
        ┌─────▼──────────────────────┐
        │      MainWindow            │
        │  ┌─────────────────────┐   │
        │  │ DashboardPage        │◄──┐
        │  ├─────────────────────┤   │ 使用
        │  │ *Widget (x5)        │   │
        │  ├─────────────────────┤   │
        │  │ *Dialog (x4)        │   │
        │  ├─────────────────────┤   │
        │  │ *Controller (x3)    │   │
        │  └─────────────────────┘   │
        └──────────┬────────────────┘
                   │ 调用
        ┌──────────▼────────────────┐
        │    *Service (x9)          │ ◄─── EventBus事件通知
        │    + SyncEngine           │
        │    + ChangeService        │
        └──────────┬────────────────┘
                   │ 操作
        ┌──────────▼────────────────┐
        │    *Model (x8)            │
        └───────────────────────────┘
```

---

## 3. 核心模块设计

### 3.1 应用核心层 (`src/core/`)

#### 3.1.1 Application 类

```python
class Application:
    """应用主类 - 管理完整生命周期"""
    
    - __init__(mode, debug)     # 初始化运行模式和调试标志
    - run() -> int                # 主循环入口，返回退出码
    - _run_gui()                 # GUI模式: 创建QApplication + MainWindow
    - _run_cli()                 # CLI模式: 命令行接口（预留）
    - shutdown()                 # 优雅关闭，保存状态
```

**职责**: 应用启动/停止的唯一入口，环境初始化（路径/日志/配置）

#### 3.1.2 SettingsManager 类

```python
class SettingsManager:
    """设置管理器 - JSON配置持久化"""
    
    - _settings_path: Path        # settings.json 文件位置
    - _data: dict                 # 内存中的配置缓存
    
    + load(path)                  # 从文件加载配置
    + save()                      # 持久化到文件
    + get(key, default) -> Any     # 读取配置项
    + set(key, value)              # 写入配置项
    + add_recent_project(path, name) # 添加最近项目（使用PathResolver规范化）
    + get_recent_projects() -> List # 获取最近项目列表（使用PathResolver解析）
    + _get_base_path() -> Path    # 获取路径规范化的基准路径
```

**关键特性**: 集成了 `PathResolver` 策略模式，存储相对路径，读取时自动还原为绝对路径。

#### 3.1.3 EventBus 类

```python
class EventBus(QObject):
    """全局事件总线 (单例模式)"""
    
    # 项目事件
    project_selected = pyqtSignal(str)
    project_created = pyqtSignal(str)
    project_opened = pyqtSignal(str)
    project_closed = pyqtSignal()
    
    # 文档事件
    document_open_request = pyqtSignal(str)
    document_saved = pyqtSignal(str)
    
    # 检查/诊断事件
    check_started = pyqtSignal()
    check_completed = pyqtSignal(object)  # CheckResult
    diagnostic_started = pyqtSignal()
    diagnostic_completed = pyqtSignal(object)  # DiagnosticReport
```

**设计决策**: 使用 Qt Signal/Slot 机制替代 Python callback，天然线程安全。

#### 3.1.4 ConfigLoader 类

```python
class ConfigLoader:
    """全局配置加载器"""
    
    + get(key, default) -> Any     # 读取全局配置
    + set(key, value)              # 修改全局配置（运行时）
    + reload()                     # 从config.py重新加载
```

**数据来源**: `config.py` 中定义的 APP_NAME, VERSION, DEFAULT_PATH 等常量。

---

### 3.2 表现层 (`src/ui/`)

#### 3.2.1 MainWindow 主窗口

```python
class MainWindow(QMainWindow):
    """主窗口 - 整合所有UI组件"""
    
    属性:
    - _project_service: ProjectService
    - _dashboard_page: DashboardPage
    - _dock_widgets: Dict[str, QDockWidget]  # 右侧面板
    
    方法:
    - _build_menu_bar()           # 构建菜单栏
    - _build_toolbar()            # 构建工具栏
    - _build_central_widget()     # 中央TabWidget
    - _build_left_panel()         # 左侧项目树 Dock
    - _build_right_panels()       # 右侧诊断/检查/测试 Dock
    - _connect_events()           # 连接EventBus信号槽
    - _cleanup_resources()        # V2.0: 统一资源清理
    - closeEvent()                # V2.0: 调用_cleanup_resources()
```

#### 3.2.2 DashboardPage 仪表盘

```python
class DashboardPage(QWidget):
    """仪表盘首页 - 项目概览与快捷操作"""
    
    组件:
    - 统计卡片组 (FB数/变量数/文档数/测试数)
    - 健康度环形图 (QProgressBar 或自定义绘制)
    - 最近项目列表 (QListWidget)
    - 快捷操作按钮组
```

#### 3.2.3 Widget 组件清单 (5个)

| Widget | 文件 | 功能 |
|--------|------|------|
| DiagnosticPanel | diagnostic_panel.py | 七维度深度诊断 |
| SpecCheckPanel | spec_check_panel.py | 六维规范检查 |
| STEditor | st_editor.py | SCL代码编辑器 |
| ProjectTree | project_tree.py | 项目目录树 |
| DocumentEditor | document_editor.py | Markdown文档预览编辑 |

#### 3.2.4 Dialog 对话框 (4个)

| Dialog | 文件 | 触发场景 |
|--------|------|----------|
| NewProjectDialog | new_project_dialog.py | 新建项目向导 |
| FBDocumentDialog | fb_document_dialog.py | FB文档生成 |
| NewDocumentDialog | new_document_dialog.py | 通用文档生成 |
| SettingsDialog | settings_dialog.py | 应用设置 |

#### 3.2.5 Controller 组件 (3个) — V2.0-R2 新增

| Controller | 文件 | 职责 |
|------------|------|------|
| ProjectController | project_controller.py | 新建/打开项目、项目树管理、保存 |
| SyncController | sync_controller.py | 版本检查、CHG/IFC生成、同步报告 |
| DashboardController | dashboard_controller.py | 统计卡片更新、最近项目刷新、快捷操作 |

---

### 3.3 业务服务层 (`src/services/`)

| 服务类 | 文件 | 核心方法 | 依赖 |
|--------|------|----------|------|
| **ProjectService** | project_service.py | `create_project()`, `open_project()`, `close_project()` | TemplateService, SettingsManager |
| **TemplateService** | template_service.py | `get_template_list()`, `apply_template()` | json模板文件 |
| **DocumentService** | document_service.py | `generate_document()`, `get_template_types()` | Jinja2/Mako, templates/*.md |
| **DiagnosticService** | diagnostic_service.py | `run_diagnosis()`, `run_lsp_check()` | ProjectHealthAnalyzer, LSPCompatibilityChecker |
| **SpecCheckerService** | spec_checker_service.py | `run_checks()`, `get_available_rules()` | RuleRegistry, 各Checker |
| **VariableService** | variable_service.py | `analyze_variables()`, `check_naming()` | VariableParser, VariableChecker |
| **SpecService** | spec_service.py | `load_spec_doc()`, `validate_spec()` | SpecDocParser |
| **ArtifactRegistryService** | artifact_registry_service.py | `scan_project_assets()`, `classify_artifacts()` | ProjectArtifactType |
| **ChangeService** | change_service.py | `track_changes()`, `get_change_log()` | SessionParser |

> **V2.0 变更**: 删除 PLCService/HMIService/TestManagementService（死代码），新增 ChangeService

---

### 3.4 数据模型层 (`src/models/`)

| 模型类 | 文件 | 字段 | 用途 |
|--------|------|------|------|
| **Project** | project.py | name, path, business_line, template_id, manager, created_at | 项目实体 |
| **Document** | document.py | doc_type, doc_number, version, author, content, path | 文档实例 |
| **Template** | template.py | template_id, name, category, file_path, variables | 模板定义 |
| **Variable** | variable.py | address, name, data_type, comment, hmi_tag | PLC变量 |
| **TestCase** | test_case.py | case_id, name, priority, steps, expected_result | 测试用例 |
| **TestResult** | test_result.py | case_id, status(PASS/FAIL/ERROR), output, duration | 测试结果 |
| **DiagnosticReport** | diagnostic_report.py | overall_score, dimension_scores, issues[] | 诊断报告 |
| **HealthMetrics** | health_metrics.py | structure_score, naming_score, doc_coverage... | 健康度指标 |

---

### 3.5 同步引擎层 (`src/sync/`) — V1.1.0 新增

#### 3.5.1 设计动机

PLC项目开发中，代码迭代速度远快于文档更新速度。一个 FB 的 `.scl` 代码升至 V7.0.0，但其 IFC/DSN/CHG 文档可能仍停留在 V6.0.0。`sync/` 模块提供**自动化版本一致性检查**和**半自动化文档同步生成**能力。

#### 3.5.2 模块架构

```
src/sync/
├── __init__.py
├── version_extractor.py    # 00-版本号提取器 ✅ Phase A
├── version_checker.py      # 01-版本差异检查器 ✅ Phase A
├── db_parser.py            # 02-GlobalVars.db解析器 ✅ Phase B
├── session_parser.py       # 03-PM_SESSION解析器 ✅ Phase C
├── ifc_generator.py        # 04-IFC半自动生成器 ✅ Phase B
├── chg_generator.py        # 05-CHG半自动生成器 ✅ Phase C
├── sync_engine.py          # 06-同步编排引擎 ✅ Phase A
├── sync_cli.py             # 07-CLI命令行入口 ✅ Phase A (Phase B+C扩展)
├── sync_report.py          # 08-全量同步报告生成器 ✅ Phase D
└── fb_registry.py          # 09-FB标识符映射注册表 ✅ V2.0-R1
```

#### 3.5.3 三层同步模型

sync 模块实现了改进方案中的**分层同步策略**：

| 层级 | 触发时机 | 自动化程度 | 模块 |
|------|---------|-----------|------|
| **L0 实时层** | 每次代码修改 | 全自动 | `version_checker` → 版本一致性报告 |
| **L1 里程碑层** | FB接口变更 / 迭代结束 | 半自动(生成→人审) | `ifc_generator` + `chg_generator` |
| **L2 按需层** | 交付/验收前 | 半自动(报告→手动) | `sync_report` → 全量对齐清单 |

#### 3.5.4 核心类设计

**VersionExtractor** — 版本号提取器
```
+ extract_scl_version(file_path: str) -> Optional[str]
+ extract_prd_version(file_path: str) -> Optional[str]
+ extract_prd_version_from_filename(file_name: str) -> Optional[str]
```

**VersionChecker** — 版本差异检查器
```
+ check_project(project_path: str) -> VersionGapReport
+ check_fb(project_path: str, fb_name: str) -> FbVersionGap
```

**SyncEngine** — 同步编排引擎
```
+ run_check(project_path: str) -> VersionGapReport
+ run_full_report(project_path: str) -> str  (Markdown报告路径)
```

**FbRegistry** — FB标识符映射注册表（V2.0-R1 新增）
```
+ get_fb_aliases(fb_name: str) -> List[str]
+ resolve_fb_id(fb_name: str) -> str
+ register_alias(fb_name: str, alias: str) -> None
```

#### 3.5.5 利旧设计

sync 模块非侵入式挂载在现有 SW-2026-005 代码树上，复用以下现有能力：

| sync 子模块 | 复用的现有模块 | 复用方式 |
|------------|--------------|---------|
| `version_checker` | `ArtifactRegistryService` | 资产扫描+分类→定位.scl/.md文件 |
| `version_checker` | `ProjectArtifactType` 枚举 | PLC_SOURCE/DOC_IFC/DOC_DSN等类型标识 |
| `ifc_generator`(未来) | `VariableParser` | 解析GVL/ST变量声明→提取接口表格 |
| `ifc_generator`(未来) | `DocumentService` | 模板填充+Markdown写入 |
| `chg_generator`(未来) | `DocumentService` + `chg_template.md` | 变更记录文档模板 |
| `sync_engine` | `ProjectService` | 项目加载+路径解析 |
| `sync_cli` | `config.py` + `logger.py` | 配置+日志基础设施 |
| `fb_registry` | `version_checker` | FB标识符→文档类型统一映射 |

---

## 4. 关键设计决策

### 4.1 为什么选择 EventBus 而非直接调用

**问题**: Widget之间需要通信（如：选择项目后刷新多个面板），直接引用导致紧耦合。

**方案对比**:

| 方案 | 耦合度 | 扩展性 | 线程安全 |
|------|--------|--------|----------|
| 直接函数调用 | 🔴 高 | 🔴 差 | ⚠️ 需手动同步 |
| 回调函数注册 | 🟡 中 | 🟡 中 | ❌ 不安全 |
| **Qt Signal/Slot (EventBus)** | ✅ 低 | ✅ 好 | ✅ 天然安全 |

**结论**: 选择 Qt Signal/Slot 机制，通过单例 EventBus 集中管理所有跨组件信号。

### 4.2 为什么使用策略模式处理路径

**问题**: settings.json 存储硬编码绝对路径，导致不可移植。

**解决方案**: [PathResolver](../../../../03_主程序/01_主程序核心代码/src/utils/path_resolver.py)

```
存储时: absolute_path → normalize() → relative_path (存入JSON)
读取时: relative_path → resolve() → absolute_path (返回给UI)
```

**扩展性**: 未来可切换为 EnvVarPathStrategy（`${WORKSPACE}/project`格式）。

### 4.3 为什么使用注册表模式管理检查器

**问题**: 检查器种类会持续增加（当前6种），硬编码 if-else 难以维护。

**解决方案**: [RuleRegistry](../../../../03_主程序/01_主程序核心代码/src/checkers/rule_registry.py)

```python
# 新增检查器只需:
class MyNewChecker(BaseChecker):
    rule_info = RuleInfo("MY-001", "我的规则", Severity.HIGH)
    def check(self, context) -> CheckResult: ...

# 注册
RuleRegistry.instance().register(MyNewChecker())
# 无需修改任何现有代码
```

### 4.4 为什么采用 Controller 模式（V2.0-R2 新增）

**问题**: MainWindow 承载过多业务逻辑（项目操作、同步、仪表盘更新），代码臃肿且难以测试。

**方案对比**:

| 方案 | MainWindow职责 | 可测试性 | 可维护性 |
|------|---------------|---------|---------|
| 全部在MainWindow | 🔴 重(800+行) | ❌ 需GUI环境 | ❌ 改动影响大 |
| **Controller委托** | ✅ 轻壳(布局+cleanup) | ✅ Controller可单元测试 | ✅ 隔离变更 |

**结论**: MainWindow 仅负责布局构建和资源清理，业务逻辑委托给3个Controller。

### 4.5 为什么需要统一资源清理架构（V2.0-R2 新增）

**问题**: 窗口关闭时后台Worker/动画定时器未停止，导致COM异常和进程残留。

**解决方案**: `_cleanup_resources()` 统一清理链

```
closeEvent → _cleanup_resources()
  ├── Worker线程: cancel → disconnect → wait(2s) → None
  ├── 动画定时器: stop()
  └── Dock/Tab面板: cleanup()
```

**关键**: 使用 `sip.delete()` 替代 `del` 消除退出时COM异常。

---

## 5. 数据流设计

### 5.1 用户操作"新建项目"流程

```
用户点击[新建]
    │
    ▼
NewProjectDialog.show()
    │ 用户填写信息并确认
    ▼
ProjectController._on_project_create_requested(path, info)
    │
    ▼ EventBus.project_created.emit(path)
    │
    ▼ MainWindow._handle_project_created(path)
    │
    ▼ ProjectService.create_project(name, template, ...)
    │   ├── TemplateService.apply_template(template_id, path)
    │   │   └── 读取 M001_full.json → 创建目录结构
    │   ├── Project(path=path).save()
    │   └── return Project instance
    │
    ▼ SettingsManager.add_recent_project(path, name)
    │   └── PathResolver.normalize() → 存储相对路径
    │
    ▼ ProjectTree.refresh()
    ▼ Dashboard.update_stats()
    ▼ StatusBar.show_message("项目创建成功")
```

### 5.2 规范检查执行流程

```
用户点击[开始检查]
    │
    ▼ SpecCheckPanel._on_check_started()
    │
    ▼ SpecCheckerService.run_checks(project_path, selected_rules)
    │   ├── RuleRegistry.get_checkers(rule_ids)
    │   │   └── 返回 [NamingChecker, SyntaxChecker, ...]
    │   ├── for each checker:
    │   │   ├── scanner.scan(project_path)  # 收集目标文件
    │   │   │   └── glob("**/*.scl", "**/*.st")
    │   │   └── checker.check(file_content)
    │   │       └── 返回 List[CheckResult]
    │   └── aggregate all results
    │
    ▼ 返回 CheckReport (summary + details[])
    │
    ▼ UI更新结果列表 (✅/❌/⚠️ 标记)
```

### 5.3 版本同步检查流程 (V1.1.0 新增)

```
用户运行 CLI:
    │
    ▼
python -m src.sync.sync_cli check <project_path>
    │
    ▼ SyncEngine.run_check(project_path)
    │
    ├── ArtifactRegistryService.scan_project_assets()
    │   └── 定位所有 .scl 文件和 IFC/DSN/CHG .md 文件
    │
    ├── VersionExtractor.extract_scl_version(each_scl_file)
    │   └── 正则提取文件头 "(* Vx.y.z *)" 版本注释
    │
    ├── VersionExtractor.extract_prd_version(each_prd_file)
    │   └── 正则提取文件名/内容中的 "Vx.y.z" 版本号
    │
    ├── VersionChecker._build_gap_matrix()
    │   └── 匹配代码版本 vs 文档版本 → 生成差距矩阵
    │
    └── VersionGapReport 输出
        ├── 终端 Markdown 表格 (stdout)
        └── 退出码: 0=全部一致, 1=存在版本滞后
```

### 5.4 IFC 半自动生成流程 (Phase B)

```
用户运行 CLI:
    │
    ▼
python -m src.sync.sync_cli generate-ifc pickplace <project_path>
    │
    ▼ 自动查找 GlobalVars.db
    │
    ├── DbParser.parse_db_file(db_path)
    │   ├── 解析 DATA_BLOCK → VAR → stXxx:STRUCT 区块
    │   ├── 提取每个 STRUCT 的所有变量声明
    │   ├── 分类输入 (i_前缀) vs 输出 (o_/q_前缀)
    │   └── 保留行内注释作为变量说明
    │
    ├── IfcGenerator._match_groups() → 按FB名匹配StructGroup
    │
    ├── IfcGenerator._render_document()
    │   ├── §0 文档基础信息 (版本号/日期/数据来源)
    │   ├── §1 功能概述 (提示人工填写)
    │   ├── §2 STRUCT接口 (输入表 + 输出表)
    │   └── 审核清单(来源列/状态机/地址映射)
    │
    └── 输出: 接口文档_IFC-{FB}-{VERSION}-GENERATED.md
         └── 用户审核 → 补充[待补充]项 → 重命名替换正式文档

### 5.5 CHG 半自动生成流程 (Phase C)

```
用户运行 CLI:
    │
    ▼
python -m src.sync.sync_cli generate-chg ob1 <project_path>
    │
    ▼ 自动查找 .scl 文件
    │
    ├── 读取 .scl changelog 区域
    │   ├── 匹配 "(*  Vx.y.z (YYYY-MM-DD) Content *)" 格式
    │   └── 匹配 "//   Vx.y.z (YYYY-MM-DD): Content" 格式
    │
    ├── ChgGenerator.generate_from_scl()
    │   ├── 提取 版本号 / 日期 / 变更内容
    │   ├── 类型推断 (修复→Bug, 重构→重构, 集成→功能)
    │   └── 渲染标准 CHG 表格
    │
    └── 输出: 变更记录_CHG-{FB}-{VERSION}-GENERATED.md
         └── 用户审核 → 补充详细说明 → 替换正式文档

备选路径:
    python -m src.sync.sync_cli generate-chg ... --source session
    │
    └── SessionParser.parse_change_logs(PM_SESSION.md)
         └── 从 PM_SESSION change_log 聚合变更条目
```

### 5.6 全量同步报告生成流程 (Phase D)

```
用户运行 CLI:
    │
    ▼
python -m src.sync.sync_cli full-report <project_path> [--output <dir>]
    │
    ▼ SyncEngine.run_full_report(project_path, output_dir)
    │
    ├── SyncReport.generate_full_report(project_path)
    │   │
    │   ├── VersionChecker.check_project() → VersionGapReport
    │   │   └── L0 版本差距矩阵 (7 FBs × 2~3 docs)
    │   │
    │   ├── _check_documents(project_root, "DSN", fb_gaps)
    │   │   ├── rglob("*.md") 过滤含 "DSN" 的文档 (排除archive)
    │   │   ├── _extract_fb_id() 从 gap.fb_name 提取短标识符 (如 "fb_1003")
    │   │   ├── _match_fb_to_doc() 增强匹配:
    │   │   │   ├── 直接子串匹配 (含下划线)
    │   │   │   ├── 去分隔符匹配 (下划线/连字符均移除)
    │   │   │   └── 别名匹配 (fb_external→fb3001/external)
    │   │   ├── 已匹配 → DocStatus(状态=[OK]/[X])
    │   │   ├── 未匹配 → DocStatus(状态=[MISSING])
    │   │   └── 孤本文档 → DocStatus(状态=[?] 无对应代码)
    │   │
    │   ├── _check_documents(project_root, "UM", fb_gaps)
    │   │   └── 同上流程, 过滤含 "UM" 的文档
    │   │
    │   ├── _find_session() → PM_SESSION*.md
    │   │   └── SessionParser.parse_change_logs() → change_ledger
    │   │
    │   └── _generate_action_items() → 优先级行动清单
    │       ├── [P0] 缺少 DSN → 需新建
    │       ├── [P1] 缺少 UM / DSN版本滞后 / IFC/CHG版本不一致
    │       └── [P2] UM版本滞后 / 文件无版本号
    │
    ├── SyncReport.render_markdown(report) → Markdown字符串
    │   ├── §1 版本差距矩阵 (复用 VersionChecker.format_report)
    │   ├── §2 DSN 详细设计文档覆盖度 (FB级表格)
    │   ├── §3 UM 使用手册覆盖度 (FB级表格)
    │   ├── §4 变更台帐聚合 (PM_SESSION change_log)
    │   └── §5 同步行动建议 (优先级排序)
    │
    └── 写入 {project_path}/sync_full_report.md
         └── 终端打印摘要 (模块数/DSN覆盖/UM覆盖/行动项)
```

### 5.7 窗口关闭资源清理流程 (V2.0-R2 新增)

```
用户关闭窗口
    │
    ▼ MainWindow.closeEvent(event)
    │
    ▼ _cleanup_resources()
    │
    ├── DiagnosticPanel.cleanup()
    │   ├── Worker: cancel() → disconnect() → wait(2000) → None
    │   ├── ScoreRingWidget.cleanup(): _animation_timer.stop()
    │   └── BarChartWidget.cleanup(): _anim_timer.stop()
    │
    ├── SpecCheckPanel (Dock).cleanup()
    │
    ├── SpecCheckPanel (Tab).cleanup()
    │
    └── sip.delete() 清理残留COM引用
```

---

## 6. 扩展机制

### 6.1 新增功能模块

```
步骤:
1. 在 src/ui/widgets/ 下创建新 Widget 类
2. 在 MainWindow._build_right_panels() 中注册
3. 连接所需 EventBus 信号
4. 如需新服务 → 在 src/services/ 下创建
5. 如需新模型 → 在 src/models/ 下创建
6. 如需新Controller → 在 src/ui/controllers/ 下创建
```

### 6.2 新增检查规则

```python
# 1. 继承 BaseChecker
class CustomChecker(BaseChecker):
    rule_info = RuleInfo("CUS-001", "自定义规则", Severity.MEDIUM)
    
    def check(self, context: CheckContext) -> List[CheckResult]:
        results = []
        for file in context.files:
            if self._detect_issue(file.content):
                results.append(CheckResult(
                    rule_id="CUS-001",
                    file=str(file.path),
                    line=lineno,
                    message="发现自定义问题",
                    suggestion="修复建议"
                ))
        return results

# 2. 注册到全局注册表
RuleRegistry.instance().register(CustomChecker())

# 3. 自动出现在检查面板选项中
```

### 6.3 新增文档模板

```
步骤:
1. 在 src/templates/documents/ 下创建 xxx_template.md
2. 在 config.py 的 DOCUMENT_TEMPLATES 字典中注册
3. 自动出现在文档生成对话框中
```

---

## 7. 配置体系

### 7.1 配置层级

| 层级 | 文件 | 作用域 | 示例 |
|------|------|--------|------|
| **全局常量** | `config.py` | 应用元信息 | APP_NAME, VERSION |
| **运行配置** | `data/settings.json` | 用户偏好 | recent_projects, theme |
| **项目配置** | `{project}/.plc.json` | PLC工程属性 | libraries, device_type |

### 7.2 settings.json 结构

```json
{
    "recent_projects": [
        {
            "path": "../../../../0100_PLC自动化/DJ-2026-005",
            "name": "DJ-2026-005_边框缓存机"
        }
    ],
    "max_recent_projects": 10,
    "theme": "material_dark",
    "last_opened_project": null,
    "window_geometry": { "width": 1280, "height": 800 }
}
```

> **注意**: `path` 字段存储的是相对于 settings.json 位置的相对路径（由 PathResolver 处理）。

---

*文档版本: ARCH-V2.0.0 | 最后更新: 2026-05-22*
*变更记录: V2.0 深度审查 — Controller模式+cleanup架构+EventBus统一+死代码清理*
