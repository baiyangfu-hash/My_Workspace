# 架构设计文档 ARCH-V1.0.0

> **项目**: SW-2026-005 PLC项目管理工具
> **版本**: V1.0.0 | **日期**: 2026-05-08
> **状态**: 当前运行版本
> **来源**: 从 `05_docs/02_技术文档/` 迁移至标准位置

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
│  │          │  │          │  │ (9个Widget + 4个Dialog)  │   │
│  └────┬─────┘  └────┬─────┘  └────────────┬─────────┘   │
│       │             │                      │               │
│  ┌────▼─────────────▼──────────────────────▼─────────┐   │
│  │              managers/ (MenuManager/ToolbarManager)    │   │
│  └───────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                    业务层 (Business)                         │
│                                                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │ProjectSvc│ │DiagnoSvc│ │DocService│ │SpecCheckSvc  │   │
│  │          │ │          │ │          │ │              │   │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────┬───────┘   │
│       │            │           │              │            │
│  ┌────▼────────────▼───────────▼──────────────▼────────┐   │
│  │         services/ (共11个业务服务)                     │   │
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
│  │ utils/       │ │              │ │                       │  │
│  │ Logger/File  │ │              │ │                       │  │
│  │ Utils/PathRes│ │              │ │                       │  │
│  │ olver/Valid.│ │              │ │                       │  │
│  └──────────────┘ └──────────────┘ └──────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 模块依赖关系

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
        │  │ *Widget (x9)        │   │
        │  ├─────────────────────┤   │
        │  │ *Dialog (x4)        │   │
        │  └─────────────────────┘   │
        └──────────┬────────────────┘
                   │ 调用
        ┌──────────▼────────────────┐
        │    *Service (x11)         │ ◄─── EventBus事件通知
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

#### 3.2.3 Widget 组件清单 (9个)

| Widget | 文件 | 功能 |
|--------|------|------|
| DiagnosticPanel | diagnostic_panel.py | 七维度深度诊断 |
| SpecCheckPanel | spec_check_panel.py | 六维规范检查 |
| TestRunnerPanel | test_runner_panel.py | SCLTest执行器 |
| STEditor | st_editor.py | SCL代码编辑器 |
| HMIMapper | hmi_mapper.py | HMI变量映射表 |
| ProjectTree | project_tree.py | 项目目录树 |
| DocumentEditor | document_editor.py | Markdown文档预览编辑 |
| IOTable | io_table.py | IO信号分配表格 |
| VariableChecker | variable_checker.py | 变量规范性检查 |

#### 3.2.4 Dialog 对话框 (4个)

| Dialog | 文件 | 触发场景 |
|--------|------|----------|
| NewProjectDialog | new_project_dialog.py | 新建项目向导 |
| FBDocumentDialog | fb_document_dialog.py | FB文档生成 |
| NewDocumentDialog | new_document_dialog.py | 通用文档生成 |
| SettingsDialog | settings_dialog.py | 应用设置 |

---

### 3.3 业务服务层 (`src/services/`)

| 服务类 | 文件 | 核心方法 | 依赖 |
|--------|------|----------|------|
| **ProjectService** | project_service.py | `create_project()`, `open_project()`, `close_project()` | TemplateService, SettingsManager |
| **TemplateService** | template_service.py | `get_template_list()`, `apply_template()` | json模板文件 |
| **DocumentService** | document_service.py | `generate_document()`, `get_template_types()` | Jinja2/Mako, templates/*.md |
| **DiagnosticService** | diagnostic_service.py | `run_diagnosis()`, `run_lsp_check()` | ProjectHealthAnalyzer, LSPCompatibilityChecker |
| **SpecCheckerService** | spec_checker_service.py | `run_checks()`, `get_available_rules()` | RuleRegistry, 各Checker |
| **PLCService** | plc_service.py | `read_plc_json()`, `validate_config()` | json |
| **HMIService** | hmi_service.py | `save_mapping()`, `import_from_excel()` | openpyxl |
| **VariableService** | variable_service.py | `analyze_variables()`, `check_naming()` | VariableParser, VariableChecker |
| **TestManagementService** | test_management_service.py | `load_tests()`, `run_test()` | SCLTestParser |
| **SpecService** | spec_service.py | `load_spec_doc()`, `validate_spec()` | SpecDocParser |

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
MainWindow._on_project_create_requested(path, info)
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

*文档版本: ARCH-V1.0.0 | 最后更新: 2026-05-08*
*迁移记录: 2026-05-08 从 `05_docs/02_技术文档/` 迁移至本标准位置*
