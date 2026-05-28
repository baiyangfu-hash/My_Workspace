# 架构设计文档 ARCH-V3.0.0

> **项目**: SW-2026-005 PLC项目管理工具
> **版本**: V3.0.0 | **日期**: 2026-05-23
> **状态**: 当前运行版本
> **变更**: V3.0深度对齐 — 修正模块计数、接口描述、EventBus信号、与实际代码完全同步；新增§8 V3.0+架构演进（⚠️未来迭代方向）

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
│  │ (薄壳)   │  │          │  │ (7个Widget + 5个Dialog) │   │
│  └────┬─────┘  └────┬─────┘  └────────────┬─────────┘   │
│       │             │                      │               │
│  ┌────▼─────────────▼──────────────────────▼─────────┐   │
│  │  managers/ (MenuManager/ToolbarManager)            │   │
│  │  + controllers/ (4个Controller: Project/Sync/      │   │
│  │                   Dashboard/Navigation)             │   │
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
│  │  services/ (共11个业务服务)                           │   │
│  │  + SyncEngine + ChangeService (sync/)                │   │
│  └──────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                    核心层 (Core)                             │
│                                                             │
│  ┌────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐    │
│  │SettingsMgr│ │ConfigLoad│ │ EventBus │ │ constants    │    │
│  │(配置持久化)│ │(配置加载)│ │(事件总线)│ │(枚举/常量)   │    │
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
│  ├────────┤ ├──────────┤ ├──────────┤ ├──────────────┤    │
│  │ChangeReq│ │CheckResult│ │ProjectArt│ │WorkflowChkPt│    │
│  │ Model  │ │ Model    │ │ Model    │ │ Model        │    │
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

### 2.2 Controller模式架构（V2.0-R2 新增，V3.0 更新）

MainWindow采用薄壳架构，业务逻辑委托给4个Controller：

```
┌─────────────────────────────────────────────────────────────┐
│              MainWindow (薄壳)                               │
│  - 布局构建（委托给Builder）                                   │
│  - closeEvent → _cleanup_resources()                        │
├──────────┬──────────┬────────────────┬─────────────────────┤
│ Project  │  Sync    │  Dashboard     │  Navigation         │
│Controller│Controller│  Controller    │  Controller         │
│          │          │                │                     │
│ 新建/打开 │ 版本检查 │ 统计卡片更新   │ ToolBox↔Tab同步     │
│ 项目树   │ CHG/IFC  │ 最近项目刷新   │ 侧边栏动作分发      │
│ 信息更新 │ 同步报告 │ 快捷操作       │ 项目树导航          │
└──────────┴──────────┴────────────────┴─────────────────────┘
```

### 2.3 资源清理架构（V2.0-R2 新增，V3.0 更新）

窗口关闭时统一清理后台资源，防止COM异常：

```
MainWindow.closeEvent
  └── _cleanup_resources()
       ├── DiagnosticPanel.cleanup()
       │    ├── Worker: cancel → disconnect → wait(2s) → None
       │    ├── ScoreRingWidget.cleanup(): _animation_timer.stop()
       │    └── BarChartWidget.cleanup(): _anim_timer.stop()
       ├── SpecCheckPanel (Dock).cleanup()
       ├── SpecCheckPanel (Tab).cleanup()
       └── ChangeManagementPanel.cleanup()
```

### 2.4 模块清单（V3.0 更新）

| 目录 | 模块列表 | 变更说明 |
|------|----------|----------|
| services/ | project_service, template_service, document_service, diagnostic_service, spec_checker_service, variable_service, spec_service, artifact_registry_service, change_service, workflow_service | 11个服务（V2.0为9个，新增WorkflowService+ChangeService） |
| ui/controllers/ | \_\_init\_\_, dashboard_controller, project_controller, sync_controller, navigation_controller | 4个Controller（V2.0为3个，新增NavigationController） |
| sync/ | version_extractor, version_checker, db_parser, session_parser, ifc_generator, chg_generator, sync_engine, sync_cli, sync_report, fb_registry | 10个模块 |
| ui/widgets/ | diagnostic_panel, spec_check_panel, st_editor, project_tree, document_editor, change_management_panel | 7个Widget（V2.0为5个，新增ChangeManagementPanel+SpecCheckTabPanel引导页） |
| ui/dialogs/ | new_project_dialog, new_document_dialog, settings_dialog, fb_document_dialog, sync_result_dialog | 5个Dialog（V2.0为4个，新增SyncResultDialog） |
| models/ | project, document, template, variable, test_case, test_result, diagnostic_report, health_metrics, change_request, check_result, project_artifact, workflow_checkpoint | 13个Model（V2.0为8个） |

### 2.5 模块依赖关系

```
                    ┌─────────────┐
                    │   main.py    │
                    └──────┬──────┘
                           │ 直接调用
                    ┌──────▼──────┐
                    │   run_gui() │
                    └──────┬──────┘
                           │ 创建
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │ConfigLoad│  │init_logger│  │QApplication│
        └──────────┘  └──────────┘  └─────┬────┘
                                           │ 创建
        ┌─────────────────────────────────▼──────────────────┐
        │                    MainWindow                       │
        │  ┌─────────────────────────────────────────────┐   │
        │  │ DashboardPage                                │◄──┐
        │  ├─────────────────────────────────────────────┤   │ 使用
        │  │ *Widget (x7)                                │   │
        │  ├─────────────────────────────────────────────┤   │
        │  │ *Dialog (x5)                                │   │
        │  ├─────────────────────────────────────────────┤   │
        │  │ *Controller (x4)                            │   │
        │  ├─────────────────────────────────────────────┤   │
        │  │ *Builder (x4)                               │   │
        │  └─────────────────────────────────────────────┘   │
        └──────────┬──────────────────────────────────────────┘
                   │ 调用
        ┌──────────▼────────────────┐
        │    *Service (x11)         │ ◄─── EventBus事件通知
        │    + SyncEngine           │
        │    + ChangeService        │
        └──────────┬────────────────┘
                   │ 操作
        ┌──────────▼────────────────┐
        │    *Model (x13)           │
        └───────────────────────────┘
```

---

## 3. 核心模块设计

### 3.1 应用核心层 (`src/core/`)

#### 3.1.1 SettingsManager 类

```python
class SettingsManager:
    """设置管理器 - JSON配置持久化"""
    
    - _settings_path: Path        # settings.json 文件位置
    - _data: dict                 # 内存中的配置缓存
    
    + initialize(settings_dir)    # 初始化设置目录（替代load）
    + save()                      # 持久化到文件
    + get(key, default) -> Any     # 读取配置项
    + set(key, value)              # 写入配置项
    + add_recent_project(path, name) # 添加最近项目（使用PathResolver规范化）
    + get_recent_projects() -> List # 获取最近项目列表（使用PathResolver解析）
    + reset_to_defaults()          # 重置为默认值
    + get_all() -> Dict            # 获取所有配置
```

**关键特性**: 集成了 `PathResolver` 策略模式，存储相对路径，读取时自动还原为绝对路径。

#### 3.1.2 EventBus 类

```python
class EventBus(QObject):
    """全局事件总线 (单例模式)"""
    
    # 项目事件
    project_selected = pyqtSignal(str)       # ⚠️ 未连接
    project_created = pyqtSignal(str)        # ✅ 已连接
    project_opened = pyqtSignal(str)         # ✅ 已连接
    
    # 文档事件
    document_open_request = pyqtSignal(str)  # ✅ 已连接(空处理)
    document_saved = pyqtSignal(str)         # ⚠️ 未发射
    document_created = pyqtSignal(str)       # ⚠️ 未发射
    
    # PLC/ST事件
    st_file_open_request = pyqtSignal(str)   # ⚠️ 未连接
    variable_check_request = pyqtSignal()    # ⚠️ 断路(发射但无处理)
    fb_doc_generate_request = pyqtSignal(str)# ⚠️ 未连接
    
    # 规范事件
    spec_check_request = pyqtSignal(dict)    # ⚠️ 断路(发射但无处理)
    
    # 系统事件
    theme_changed = pyqtSignal(str)          # ✅ 已连接
    settings_changed = pyqtSignal()          # ✅ 已连接
```

**设计决策**: 使用 Qt Signal/Slot 机制替代 Python callback，天然线程安全。

**信号状态说明**:
- ✅ 已连接: 信号已定义且已连接到处理函数
- ⚠️ 未连接: 信号已定义但未连接任何处理函数
- ⚠️ 未发射: 信号已定义但从未被发射
- ⚠️ 断路: 信号被发射但没有处理函数接收

#### 3.1.3 ConfigLoader 类

```python
class ConfigLoader:
    """全局配置加载器"""
    
    + load()                       # 从config.py加载配置
    + get(key, default) -> Any     # 读取全局配置
    + set(key, value)              # 修改全局配置（运行时）
    + get_data_dir() -> Path       # 获取数据目录路径
```

**数据来源**: `config.py` 中定义的 APP_NAME, VERSION, DEFAULT_PATH 等常量。

---

### 3.2 表现层 (`src/ui/`)

#### 3.2.1 MainWindow 主窗口

```python
class MainWindow(QMainWindow):
    """主窗口 - 薄壳架构，委托构建和业务逻辑"""
    
    属性:
    - _event_bus: EventBus
    - _menu_manager: MenuManager
    - _toolbar_manager: ToolBarManager
    - _tool_box: QToolBox
    - _tab_widget: QTabWidget
    - _nav_ctrl: NavigationController
    - _project_ctrl: ProjectController
    - _sync_ctrl: SyncController
    - _dashboard_ctrl: DashboardController
    
    方法:
    - _build_central_widget()     # 中央Splitter
    - _build_left_panel()         # 委托LeftPanelBuilder
    - _build_right_panel()        # 委托RightPanelBuilder
    - _build_managers()           # 构建MenuManager/ToolBarManager
    - _build_dock_panels()        # 委托DockPanelBuilder
    - _connect_events()           # 连接EventBus信号槽
    - _cleanup_resources()        # 统一资源清理
    - closeEvent()                # 调用_cleanup_resources()
    
    公开方法:
    - get_dashboard_page()
    - get_menu_manager()
    - get_project_tree_widget()
    - get_project_info_labels()
```

#### 3.2.2 DashboardPage 仪表盘

```python
class DashboardPage(QWidget):
    """仪表盘首页 - 项目概览与快捷操作"""
    
    组件:
    - 统计卡片组 (项目总数/进行中/已完成/已归档)
    - 最近项目列表 (QListWidget)
    - 快捷操作按钮组
    
    信号:
    - action_triggered = pyqtSignal(str)  # 快捷操作触发
```

#### 3.2.3 Widget 组件清单 (7个)

| Widget | 文件 | 功能 |
|--------|------|------|
| DiagnosticPanel | diagnostic_panel.py | 七维度深度诊断 |
| SpecCheckPanel | spec_check_panel.py | 六维规范检查 |
| STEditor | st_editor.py | SCL代码编辑器 |
| ProjectTree | project_tree.py | 项目目录树 |
| DocumentEditor | document_editor.py | Markdown文档预览编辑 |
| ChangeManagementPanel | change_management_panel.py | 变更单列表/创建/审核/状态流转 |
| SpecCheckTabPanel | spec_check_panel.py | 规范检查引导页（Tab内占位） |

#### 3.2.4 Dialog 对话框 (5个)

| Dialog | 文件 | 触发场景 |
|--------|------|----------|
| NewProjectDialog | new_project_dialog.py | 新建项目向导 |
| NewDocumentDialog | new_document_dialog.py | 通用文档生成 |
| SettingsDialog | settings_dialog.py | 应用设置 |
| SyncResultDialog | sync_result_dialog.py | CHG/IFC生成结果展示 |
| FBDocumentDialog | fb_document_dialog.py | FB文档生成（预留占位） |

#### 3.2.5 Controller 组件 (4个)

| Controller | 文件 | 职责 |
|------------|------|------|
| ProjectController | project_controller.py | 新建/打开项目、项目树管理、项目信息更新 |
| SyncController | sync_controller.py | 版本检查、CHG/IFC生成、同步报告 |
| DashboardController | dashboard_controller.py | 统计卡片更新、最近项目刷新、快捷操作分发 |
| NavigationController | navigation_controller.py | ToolBox↔TabWidget双向同步、侧边栏动作分发 |

#### 3.2.6 Builder 组件 (4个)

| Builder | 文件 | 职责 |
|---------|------|------|
| LeftPanelBuilder | left_panel_builder.py | 构建左侧ToolBox（6页） |
| RightPanelBuilder | right_panel_builder.py | 构建右侧TabWidget（6 Tab） |
| DockPanelBuilder | dock_panel_builder.py | 构建右侧Dock面板（诊断/规范检查） |
| StyleBuilder | style_builder.py | 主题样式应用、中文字体解析 |

---

### 3.3 业务服务层 (`src/services/`)

| 服务类 | 文件 | 核心方法 | 类型 |
|--------|------|----------|------|
| **ProjectService** | project_service.py | `create_project()`, `load_project_from_path()`, `create_new_project()`, `import_dj_project()` | @classmethod |
| **TemplateService** | template_service.py | `initialize_builtin_templates()`, `get_template()`, `get_all_templates()`, `apply_template()` | @classmethod |
| **DocumentService** | document_service.py | `create_document()`, `create_or_update_document()`, `find_authoritative_document()`, `read_document()`, `save_document()` | @classmethod |
| **DiagnosticService** | diagnostic_service.py | `run_full_diagnostic()`, `get_last_diagnostics()`, `is_healthy()`, `reset()` | 实例方法 |
| **SpecCheckerService** | spec_checker_service.py | `check_project()`, `check_file()`, `get_enabled_checkers()`, `load_project_rules()` | 实例方法 |
| **VariableService** | variable_service.py | `parse_st_variables()`, `validate_naming()` | 预留空实现 |
| **SpecService** | spec_service.py | `initialize_builtin_specs()`, `check_document_spec()`, `get_available_specs()` | 预留空实现 |
| **ArtifactRegistryService** | artifact_registry_service.py | `detect_project_type()`, `scan_project_assets()`, `summarize_assets()`, `get_artifact_roots()` | @classmethod |
| **ChangeService** | change_service.py | `list_change_requests()`, `create_change_request()`, `update_status()`, `approve_change_request()` | @classmethod |
| **WorkflowService** | workflow_service.py | `build_checkpoints()` | @classmethod |

> **V3.0 变更**: 新增 ChangeService 和 WorkflowService；修正各服务方法名与实际代码一致

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
| **ChangeRequest** | change_request.py | change_id, title, category, status, description, approver | 变更单 |
| **CheckResult** | check_result.py | rule_id, file_path, line, message, severity | 检查结果 |
| **ProjectArtifact** | project_artifact.py | artifact_type, path, category, metadata | 项目资产 |
| **WorkflowCheckpoint** | workflow_checkpoint.py | stage, passed, missing_assets | 工作流检查点 |

---

### 3.5 同步引擎层 (`src/sync/`)

#### 3.5.1 设计动机

PLC项目开发中，代码迭代速度远快于文档更新速度。一个 FB 的 `.scl` 代码升至 V7.0.0，但其 IFC/DSN/CHG 文档可能仍停留在 V6.0.0。`sync/` 模块提供**自动化版本一致性检查**和**半自动化文档同步生成**能力。

#### 3.5.2 模块架构

```
src/sync/
├── __init__.py
├── version_extractor.py    # 00-版本号提取器
├── version_checker.py      # 01-版本差异检查器
├── db_parser.py            # 02-GlobalVars.db解析器
├── session_parser.py       # 03-PM_SESSION解析器
├── ifc_generator.py        # 04-IFC半自动生成器
├── chg_generator.py        # 05-CHG半自动生成器
├── sync_engine.py          # 06-同步编排引擎
├── sync_cli.py             # 07-CLI命令行入口
├── sync_report.py          # 08-全量同步报告生成器
└── fb_registry.py          # 09-FB标识符映射注册表
```

#### 3.5.3 核心类设计

**SyncEngine** — 同步编排引擎
```
+ run_check(project_path: str) -> VersionGapReport
+ run_full_report(project_path: str, output_dir: str) -> str
+ run_generate_chg(project_path: str, output_dir: str) -> str
+ run_generate_ifc(project_path: str, output_dir: str) -> str
+ writeback_to_project(source_path, project_path, doc_type) -> List[str]
+ format_version_report_html(report) -> str
```

**FbRegistry** — FB标识符映射注册表
```
+ get_fb_aliases(fb_name: str) -> List[str]
+ resolve_fb_id(fb_name: str) -> str
+ register_alias(fb_name: str, alias: str) -> None
```

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

**解决方案**: PathResolver

```
存储时: absolute_path → normalize() → relative_path (存入JSON)
读取时: relative_path → resolve() → absolute_path (返回给UI)
```

**扩展性**: 未来可切换为 EnvVarPathStrategy（`${WORKSPACE}/project`格式）。

### 4.3 为什么使用注册表模式管理检查器

**问题**: 检查器种类会持续增加（当前6种），硬编码 if-else 难以维护。

**解决方案**: RuleRegistry

```python
# 新增检查器只需:
class MyNewChecker(BaseChecker):
    rule_info = RuleInfo("MY-001", "我的规则", Severity.HIGH)
    def check(self, context) -> CheckResult: ...

# 注册
RuleRegistry.instance().register(MyNewChecker())
# 无需修改任何现有代码
```

### 4.4 为什么采用 Controller 模式

**问题**: MainWindow 承载过多业务逻辑（项目操作、同步、仪表盘更新），代码臃肿且难以测试。

**方案对比**:

| 方案 | MainWindow职责 | 可测试性 | 可维护性 |
|------|---------------|---------|---------|
| 全部在MainWindow | 🔴 重(800+行) | ❌ 需GUI环境 | ❌ 改动影响大 |
| **Controller委托** | ✅ 轻壳(布局+cleanup) | ✅ Controller可单元测试 | ✅ 隔离变更 |

**结论**: MainWindow 仅负责布局构建和资源清理，业务逻辑委托给4个Controller。

### 4.5 为什么需要统一资源清理架构

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
ProjectService.create_new_project(project_info)
    │
    ├── TemplateService.apply_template(template_id, path)
    │   └── 读取 M001_full.json → 创建目录结构
    ├── 创建 .plc_project.json 元数据
    └── return (project_path, None)
    │
    ▼ EventBus.project_created.emit(path)
    │
    ▼ MainWindow._on_project_created(path)
    │
    ▼ ProjectController.on_project_created(path)
    │   └── ProjectTreeWidget.load_project(project)
    │
    ▼ SettingsManager.add_recent_project(path, name)
    │   └── PathResolver.normalize() → 存储相对路径
    │
    ▼ StatusBar.show_message("项目创建成功")
```

### 5.2 规范检查执行流程

```
用户点击[开始检查]
    │
    ▼ SpecCheckPanel.start_check(project_path)
    │
    ▼ SpecCheckerService.check_project(project_path)
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

### 5.3 变更管理流程

```
用户点击[版本检查]
    │
    ▼ SyncController.on_sync_version_check()
    │
    ▼ _VersionCheckWorker.run()
    │   └── SyncEngine.run_check(project_path)
    │       └── VersionGapReport
    │
    ▼ 显示HTML报告对话框

用户点击[生成CHG]
    │
    ▼ SyncController.on_sync_generate_chg()
    │
    ▼ _GenerateDocWorker.run()
    │   └── SyncEngine.run_generate_chg(project_path)
    │
    ▼ SyncResultDialog.show()
    │   ├── 用户选择"回写到项目"
    │   │   └── SyncEngine.writeback_to_project()
    │   └── 用户选择"打开目录"
    │       └── 打开文件管理器
```

### 5.4 窗口关闭资源清理流程

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
    └── ChangeManagementPanel.cleanup()
```

---

## 6. 扩展机制

### 6.1 新增功能模块

```
步骤:
1. 在 src/ui/widgets/ 下创建新 Widget 类
2. 在 RightPanelBuilder.build() 中注册
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

## 8. V3.0+ 架构演进：SCL 语言服务层

> ⚠️ **本章节为未来迭代方向规划，不属于当前工作范围。当前工作焦点为 V2.5 缺陷修复和 V3.0-RC 发布候选。**

> **战略方向**：在现有分层架构中新增"语言服务层"，将 SW-2026-005 从项目管理工具升级为 PLC 开发工具链。

### 8.1 演进后的分层架构

```
┌─────────────────────────────────────────────────────────────┐
│                    表现层 (Presentation)                    │
│  MainWindow / Dashboard / Dialogs / Widgets                │
│  (保持不变，新增 FBDPreview / TagTableEditor)               │
├─────────────────────────────────────────────────────────────┤
│                    业务层 (Business)                         │
│  11个Service + SyncEngine + ChangeService (保持不变)        │
├─────────────────────────────────────────────────────────────┤
│              ★ 语言服务层 (Language Service) ★  ← V3.0新增  │
│                                                             │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────┐     │
│  │ SCL Parser   │  │ Type Checker  │  │ Symbol Index │     │
│  │ Lexer + AST  │  │ Diagnostics   │  │ Scope Manager│     │
│  └──────────────┘  └───────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────┐     │
│  │ S7DCL Parser │  │ S7RES Parser  │  │ TagTable XML │     │
│  └──────────────┘  └───────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌───────────────┐                        │
│  │ LibraryResolver│ │ .plc.json    │                        │
│  │ (.liblink/GUID)│ │ Scope Mgr   │                        │
│  └──────────────┘  └───────────────┘                        │
├─────────────────────────────────────────────────────────────┤
│                    核心层 (Core) — 保持不变                   │
├─────────────────────────────────────────────────────────────┤
│                    数据层 (Data) — 保持不变                   │
├─────────────────────────────────────────────────────────────┤
│                  基础设施层 (Infrastructure)                   │
│  parsers/ + checkers/ + diagnostics/ + sync/ + utils/      │
│  (现有模块保持不变，STParser 逐步迁移到 SCL Parser)          │
├─────────────────────────────────────────────────────────────┤
│              ★ LSP 适配层 ★  ← V3.1新增                     │
│  pygls Server / Document Sync / Completion / Hover /        │
│  Definition / References / Inlay Hints / Diagnostics        │
├─────────────────────────────────────────────────────────────┤
│              ★ TIA Portal 网关 ★  ← V4.0可选                │
│  C# Openness API / HTTP REST / 项目创建 / 编译下载           │
└─────────────────────────────────────────────────────────────┘
```

### 8.2 语言服务层模块设计

#### 8.2.1 新增目录结构

```
src/
├── scl/                                # SCL 语言核心模块
│   ├── __init__.py
│   ├── lexer.py                        # 词法分析器
│   ├── tokens.py                       # Token 类型定义
│   ├── ast_nodes.py                    # AST 节点定义
│   ├── parser.py                       # 递归下降语法分析器
│   ├── visitor.py                      # AST 访问者模式基类
│   └── formatter.py                    # 代码格式化
│
├── checker/                            # 类型检查与语义分析
│   ├── __init__.py
│   ├── type_system.py                  # SCL 类型系统
│   ├── type_checker.py                 # 类型检查器
│   ├── semantic_analyzer.py            # 语义分析器
│   ├── scope.py                        # 作用域管理
│   └── diagnostics.py                  # 诊断消息定义
│
├── language_server/                    # LSP 服务器模块
│   ├── __init__.py
│   ├── server.py                       # pygls 服务器入口
│   ├── features/                       # LSP 功能实现
│   │   ├── completion.py               # textDocument/completion
│   │   ├── hover.py                    # textDocument/hover
│   │   ├── definition.py               # textDocument/definition
│   │   ├── references.py               # textDocument/references
│   │   ├── diagnostics.py              # textDocument/publishDiagnostics
│   │   ├── inlay_hints.py              # textDocument/inlayHint
│   │   └── document_sync.py            # didOpen/didChange/didClose
│   └── protocol/                       # 自定义协议扩展
│
├── project/                            # 扩展：项目管理
│   ├── plc_config.py                   # .plc.json 解析与作用域
│   ├── library_resolver.py             # 库引用解析 (.liblink/.libinfo)
│   ├── s7dcl_parser.py                 # .s7dcl 文件解析
│   ├── s7res_parser.py                 # .s7res 文件解析
│   └── tag_table_parser.py             # 标签表 XML 解析
│
└── ui/widgets/                         # 扩展：UI 组件
    ├── fbd_preview.py                  # FBD 功能块预览
    └── tag_table_editor.py             # 标签表编辑器
```

#### 8.2.2 核心类设计

**SCL Lexer** — 词法分析器
```
class SclLexer:
    + tokenize(source: str) -> List[Token]
    + tokenize_line(source: str) -> List[Token]
    - _scan_token() -> Token
    - _scan_string() -> Token
    - _scan_number() -> Token
    - _scan_identifier() -> Token
    - _scan_comment() -> Token
```

**SCL Parser** — 递归下降语法分析器
```
class SclParser:
    + parse(source: str) -> ProgramNode
    + parse_expression(source: str) -> ExpressionNode
    - _parse_function_block() -> FunctionBlockNode
    - _parse_organization_block() -> OrgBlockNode
    - _parse_data_block() -> DataBlockNode
    - _parse_var_section() -> VarSectionNode
    - _parse_statement() -> StatementNode
    - _parse_if_statement() -> IfNode
    - _parse_case_statement() -> CaseNode
    - _parse_for_statement() -> ForNode
    - _parse_assignment() -> AssignmentNode
    - _parse_fb_call() -> FBCallNode
```

**TypeChecker** — 类型检查器
```
class TypeChecker:
    + check(program: ProgramNode) -> List[Diagnostic]
    + check_expression(expr: ExpressionNode, expected: SclType) -> TypeCheckResult
    - _resolve_type(type_name: str) -> SclType
    - _check_assignment(target: ExpressionNode, value: ExpressionNode) -> Diagnostic?
    - _check_fb_call(call: FBCallNode) -> List[Diagnostic]
    - _build_symbol_table(program: ProgramNode) -> SymbolTable
```

**LanguageServer** — LSP 服务器（pygls）
```
class SclLanguageServer(LanguageServer):
    + __init__()
    - _language_service: LanguageService
    # LSP 特性注册:
    - @feature(TEXT_DOCUMENT_COMPLETION)
    - @feature(TEXT_DOCUMENT_HOVER)
    - @feature(TEXT_DOCUMENT_DEFINITION)
    - @feature(TEXT_DOCUMENT_REFERENCES)
    - @feature(TEXT_DOCUMENT_PUBLISH_DIAGNOSTICS)
    - @feature(TEXT_DOCUMENT_INLAY_HINT)
```

### 8.3 与现有模块的集成方式

| 现有模块 | 集成方式 | 说明 |
|---------|---------|------|
| **STParser** (正则版) | 保留并存，逐步迁移 | 简单场景(变量提取/命名检查)仍用正则版，复杂场景(类型检查/补全)用新 AST 版 |
| **STLexer** (QScintilla) | 扩展 Token 类型 | 新增 .s7dcl/.s7res 语法高亮支持 |
| **SpecCheckerService** | 承载新诊断规则 | TypeChecker 的诊断结果通过 SpecCheckerService 推送到 UI |
| **DiagnosticService** | 新增第四阶段 | 现有三阶段(规范+LSP+健康度) → 四阶段(+SCL类型检查) |
| **EventBus** | 新增信号 | `diagnostics_updated(List[Diagnostic])` / `symbol_index_ready()` |
| **ProjectService** | 扩展 .plc.json 管理 | 新增 plc_config.py 解析 .plc.json 作用域 |

### 8.4 关键设计决策

#### 8.4.1 为什么选择混合模式而非纯 LSP

| 方案 | PyQt5 集成 | VS Code 可用 | 性能 | 复杂度 |
|------|-----------|-------------|------|--------|
| 纯 LSP（独立进程） | ❌ 需 IPC | ✅ | 中（IPC 开销） | 低 |
| 内嵌式（不走 LSP） | ✅ 同进程 | ❌ | 高 | 低 |
| **混合模式** | ✅ 同进程 API | ✅ pygls | 高（同进程）/中（LSP） | 中 |

**结论**：混合模式兼顾 PyQt5 深度集成和 VS Code 生态兼容。

#### 8.4.2 为什么手写递归下降而非 ANTLR4/Tree-sitter

| 方案 | 依赖 | 代码量 | 可控性 | 增量解析 |
|------|------|--------|--------|---------|
| **手写递归下降** | 无 | ~2000行 | ✅ 完全可控 | ✅ 可实现 |
| ANTLR4 | Java 运行时 | ~500行(语法文件) | ❌ 生成代码难调试 | ❌ 全量重解析 |
| Tree-sitter | C 编译 | ~800行(语法文件) | ❌ C 依赖 | ✅ 天然增量 |

**结论**：手写解析器零外部依赖，完全可控，Go 插件也是手写。

#### 8.4.3 为什么不实现 SCL 编译器

Go 插件的 SCL→Go 编译器是最复杂模块（★★★★★），但存在根本性语义差异：
- VAR_IN_OUT 值拷贝导致 FB 内部修改不回写
- IEC 定时器(TON/TOF/TP)无法映射为通用语言语义
- 生成的代码只能做有限功能测试，无法替代 TIA Portal 真实编译

**替代路径**：V4.0 通过 C# Openness 网关调用 TIA Portal 原生编译和仿真。

---

## 9. V2.0.0 → V3.0.0 变更记录

| 章节 | 变更内容 |
|------|---------|
| §8 | **新增章节** — V3.0+ 架构演进：SCL 语言服务层，包含演进后分层架构图、模块设计、核心类设计、集成方式、关键设计决策（⚠️未来迭代方向，非当前工作范围） |

*文档版本: ARCH-V3.0.0 | 最后更新: 2026-05-28*
*变更记录: V3.0+新增§8 SCL语言服务层架构演进规划*
