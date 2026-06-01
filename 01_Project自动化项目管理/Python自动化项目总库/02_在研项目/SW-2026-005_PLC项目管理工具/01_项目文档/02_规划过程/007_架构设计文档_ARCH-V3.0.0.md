# 架构设计文档 ARCH-V4.0.0

> **项目**: SW-2026-005 PLC项目管理工具
> **版本**: V4.0.0
> **日期**: 2026-06-01
> **状态**: 当前主线架构文档
> **适用范围**: PyWebView前端架构 + IPCBridge桥接 + 工作空间治理 + Trae伴生工具化

---

## 1. 架构定位

### 1.1 产品定位

`SW-2026-005` 的当前主线定位是：

**Trae伴生式 PLC 工作空间治理工具**

其职责不是替代 Trae 作为 PLC 主开发环境，而是围绕工作空间提供：
- 项目库挂载
- 子项目识别与聚合
- 共享库/规范目录治理
- 规范检查与聚合汇总
- 文档生成与工作空间概览

### 1.2 技术栈

当前主线技术栈已从 PyQt5 GUI 迁移到 **PyWebView(Chromium) 前端 + IPCBridge 后端桥接**：

| 层 | 技术 |
|---|---|
| 前端 | HTML + CSS + JavaScript（Chromium/WebView2 Runtime 渲染） |
| 桥接 | pywebview 6.x + IPCBridge（Python↔JS 双向通信） |
| 后端 | Python 3.9+ / Service 层 |
| 回退 | PyQt5（环境变量 `PLC_GUI_MODE=pyqt` 触发） |

### 1.3 职责边界

| 角色 | 主要职责 |
|---|---|
| Trae | PLC代码与文档主编辑、AI协同开发、文件级修改 |
| SW-2026-005 | 工作空间挂载、树形浏览、治理、检查、文档生成、聚合视图 |
| PLC Workspace | 真实资产根目录，承载多个项目、共享库和规范目录 |

### 1.4 非目标

- 不将产品扩展为独立于 Trae 的主开发平台
- 不在本轮引入 SCL 语言服务器、TIA Portal 网关等未来能力
- 不将工作空间支持做成重型平台化重构
- 不在前端HTML中直接import Python模块
- 不绕过IPCBridge直接调用Service层

---

## 2. 核心概念模型

### 2.1 工作空间模型

```text
Workspace
├── Child Project (DJ / Generic .plc.json 项目)
├── Shared Library (如 SysLib)
├── Spec Directory (如 PLC编程规范目录)
└── Aggregated Views
```

### 2.2 核心对象

| 对象 | 说明 |
|---|---|
| `Workspace` | 工作空间根目录，代表整个 PLC 项目库 |
| `Child Project` | 工作空间下可独立治理的子项目 |
| `Shared Library` | 跨项目复用的共享函数库或公共资产 |
| `Spec Directory` | 工作空间级规范目录 |
| `Workspace View` | 面向用户的树视图、概览面板与汇总结果 |

---

## 3. 分层架构

### 3.1 总览

```text
Presentation Layer (V4.0新增)
  └─ index.html (~2100行) — 五区IDE布局 + 7视图 + CSS Design Tokens
IPC Bridge Layer (V4.0新增)
  └─ IPCBridge类 — 38个API端点 + _emit事件推送 + _safe_call异常包装
Service Layer (UNCHANGED)
  └─ ProjectService / DocumentService / ChangeService / SpecCheckerService
     DiagnosticService / TemplateService / AutoFixService / ExcelExporter
     LibraryService / WorkspaceService / CompanionService / ArtifactRegistryService
Core Layer (UNCHANGED)
  └─ constants.py / event_bus.py / config.py / settings.py / project.py
Workspace Assets (UNCHANGED)
  └─ DJ projects / shared libraries / spec dirs
Trae (UNCHANGED)
  └─ 主编辑与AI开发环境
```

### 3.2 分层原则

- **高内聚**: 工作空间识别、扫描、聚合都集中在 Service 层
- **低耦合**: IPCBridge 只做参数转换和异常包装，不承载业务逻辑
- **文档同步**: 架构变化必须同步更新 `006~011`
- **可扩展**: 后续共享库治理、全库检查基于同一 Workspace 模型扩展
- **桥接隔离**: 前端与后端通过 IPCBridge 严格隔离，禁止跨层直接调用

---

## 4. 关键架构流

### 4.1 启动流程 ✅ 已实现

```text
main.py → USE_WEBVIEW判断
  ├─ True → run_webview() → ConfigLoader.load() → create_window() → webview.start(debug=True)
  │   └─ create_window: new IPCBridge() → webview.create_window(js_api=bridge) → bridge.set_window(window)
  └─ False → run_pyqt() → QApplication → MainWindow().show()
```

> **实现说明**: `main.py` 通过环境变量 `PLC_GUI_MODE` 控制启动模式，默认值 `"webview"` 启动 PyWebView 模式；设为 `"pyqt"` 时启动 PyQt5 回退模式。当 PyWebView 不可用时，`ImportError` 自动回退到 PyQt5。`create_window(html_path, title, width, height)` 创建 webview window 并绑定 IPCBridge 实例为 `js_api`，默认加载 `ui_prototype/index.html`。

### 4.2 前后端通信 ✅ 已实现

```text
前端JS → window.pywebview.api.xxx() → IPCBridge.xxx() → _safe_call() → Service层
后端Python → _emit(event,data) → window.evaluate_js("window.__ipc_recv(payload)") → 前端__ipc_recv事件处理
```

> **实现说明**: 前端通过 `window.pywebview.api.xxx()` 调用 IPCBridge 暴露的 API 端点，每个端点内部通过 `_safe_call(name, fn, *args)` 统一异常包装。后端通过 `_emit(event, data)` 使用 `window.evaluate_js()` 将事件推送到前端，前端通过 `window.__ipc_recv(payload)` 接收并分发处理。

### 4.3 打开工作空间 ✅ 已实现（通过IPCBridge）

```text
用户点击"打开目录" → JS调用ipcOpenProject(path) → IPCBridge.open_project(path)
  → ProjectService.load_project_from_path(path) → 返回project info JSON
  → _emit("project_created"/"project_opened") → 前端接收并更新UI
```

> **实现说明**: 前端通过 `ipcOpenProject(path)` 便捷函数发起调用，IPCBridge 的 `open_project()` 方法委托 `ProjectService.load_project_from_path()` 加载项目，加载完成后通过 `_emit()` 推送事件通知前端更新 UI。

### 4.4 子项目聚合 ✅ 已实现

```text
遍历 Workspace 根目录
  -> 过滤 WORKSPACE_IGNORED_DIRS 中的忽略目录
  -> 逐个识别 Child Project / Shared Library / Generic .plc.json
  -> ArtifactRegistryService.scan_workspace_subprojects() 分类
  -> ProjectService._load_subproject() 按类型加载（DJ/共享库/通用）
  -> 加载失败时降级构造 Project 对象
  -> 统一返回给 UI 层展示
```

> **实现说明**: `ArtifactRegistryService.scan_workspace_subprojects()` 遍历根目录并通过 `_classify_subproject()` 分类；`ProjectService._load_subproject()` 按子项目类型分别调用 `import_dj_project()`、`_create_library_project()` 或 `load_project_from_path()`，加载失败时通过 `_create_fallback_project()` 降级构造。

### 4.5 Trae伴生流 ✅ 已实现

```text
用户在 SW-2026-005 中查看工作空间结构
  -> 选中子项目/共享库/规范目录
  -> 工具提供治理、检查、汇总能力
  -> 需要实际编辑源码或文档时回到 Trae 完成
```

这条数据流明确了：
- 工具负责"看全局、做治理、出汇总"
- Trae负责"写内容、改代码、做AI开发"

> **实现说明**: `CompanionService` 作为伴生跳转的中央服务，集中管理本工具与 Trae IDE 之间的交互边界。跳转逻辑按文件类型分发：SCL/ST/PLC 源码文件优先尝试 Trae CLI（`trae <file> [--goto <line>]`），失败时降级到系统默认打开方式；Excel 文件（.xlsx/.xls）直接使用系统默认打开。`MainWindow._jump_to_source()` 将跳转请求委托给 `CompanionService.jump_to_file()`，跳转失败时降级到内嵌 ST 编辑器。`ProjectTree` 双击 document/code 类型节点时，通过 `CompanionService.should_jump_to_ide()` 判定是否跳转，若可跳转则调用 `CompanionService.jump_to_file()` 执行。编辑菜单已将 undo/redo 替换为"在Trae中打开"（Ctrl+E），由 `MenuManager._on_open_in_trae()` 委托 `CompanionService.jump_to_file()` 实现。

---

## 5. 关键模块职责

### 5.1 模块职责表

| 模块 | 职责 | 实现状态 | 架构归属 |
|---|---|---|---|
| `src/ui/webview_window.py` | PyWebView窗口创建 + IPCBridge桥接(38 API) + 事件推送 | ✅ V4.0新增 | IPC Bridge层 |
| `ui_prototype/index.html` | HTML/CSS/JS前端: 五区IDE布局 + 7视图 + 状态管理 + 30个ipc便捷函数 | ✅ V4.0新增 | Presentation层 |
| `main.py` | 双模式入口: PyWebView(默认)/PyQt5(回退) | ✅ V4.0重写 | 入口 |
| `lib/` | pywebview运行时依赖(bottle/cffi/pythonnet等) | ✅ V4.0新增 | 运行时 |
| `src/core/constants.py` | 定义 `ProjectType`、业务线、忽略规则；`ProjectType.PLC_WORKSPACE`、`ProjectType.PLC_LIBRARY`、`BusinessLine.LIBRARY`、`WORKSPACE_IGNORED_DIRS`、`PLC_LIBRARY_CATEGORY_DIRS` | ✅ 已实现 | Core层 |
| `src/services/artifact_registry_service.py` | 工作空间/项目/共享库识别；`detect_project_type()` 四级识别；`scan_workspace_subprojects()` 扫描并分类子项目 | ✅ 已实现 | Service层 |
| `src/services/project_service.py` | 单项目与工作空间加载编排；`load_workspace_from_path()` 编排工作空间子项目加载 | ✅ 已实现 | Service层 |
| `src/ui/controllers/project_controller.py` | 打开目录入口与 UI 分支分发；`_open_as_workspace()` 在 `on_project_opened()` 中根据识别结果分发 | ✅ 已实现 | Service层(PyQt) |
| `src/ui/widgets/project_tree.py` | 工作空间树形承载与子节点展示；`load_workspace()` 支持工作空间根节点 + 多子项目节点渲染 | ✅ 已实现 | Service层(PyQt) |
| `src/services/companion_service.py` | 伴生跳转服务 - 集中管理Trae IDE交互边界，能力判定/跳转执行/降级策略 | ✅ 已实现 | Service层 |
| `src/services/library_service.py` | 共享库治理服务 - 扫描共享库目录，识别分类子目录和规范目录，统计ST源码/规范文件 | ✅ 已实现 | Service层 |
| `src/services/workspace_service.py` | 工作空间治理服务 - 跨项目规范检查、聚合报告生成、汇总统计、命名冲突检测 | ✅ 已实现 | Service层 |
| `tests/` | 工作空间识别、加载、UI分支、伴生跳转、共享库治理、工作空间治理验证 | 待补充 | 测试 |

### 5.2 IPCBridge API端点清单 ✅ V4.0新增

IPCBridge 类（`src/ui/webview_window.py`）暴露 38 个 API 端点给前端调用：

| 分类 | 端点 | 说明 |
|---|---|---|
| 应用信息 | `get_app_info()` | 获取应用版本等信息 |
| 设置管理 | `get_settings()` | 获取全部设置 |
| | `update_setting(key, value)` | 更新单项设置 |
| | `reset_settings()` | 重置为默认设置 |
| 项目管理 | `create_project(info)` | 创建新项目 |
| | `open_project(path)` | 打开项目 |
| | `close_project()` | 关闭当前项目 |
| | `get_project_detail(path)` | 获取项目详情 |
| | `save_project_info(info)` | 保存项目信息 |
| | `get_recent_projects()` | 获取最近打开的项目列表 |
| 文档管理 | `create_document(params)` | 创建文档 |
| | `list_documents(project_path)` | 列出项目文档 |
| | `read_document(file_path)` | 读取文档内容 |
| | `save_document(params)` | 保存文档 |
| 变更管理 | `list_change_requests(project_path)` | 列出变更请求 |
| | `create_change_request(params)` | 创建变更请求 |
| | `update_change_status(params)` | 更新变更状态 |
| | `approve_change_request(params)` | 审批变更请求 |
| 版本同步 | `run_version_check(project_path)` | 运行版本检查 |
| | `generate_chg(project_path, output_dir)` | 生成CHG文档 |
| | `generate_ifc(project_path, output_dir)` | 生成IFC文档 |
| 规范检查 | `run_spec_check(project_path, checker_ids)` | 运行规范检查 |
| | `get_checkers()` | 获取可用检查器列表 |
| 诊断分析 | `run_diagnosis(project_path)` | 运行诊断分析 |
| 自动修复 | `get_available_fixers()` | 获取可用修复器 |
| | `scan_fixes(params)` | 扫描可修复项 |
| | `fix_project(params)` | 执行修复 |
| Excel导出 | `export_excel_single(params)` | 单项导出Excel |
| | `export_excel_batch(project_path)` | 批量导出Excel |
| 仪表盘 | `get_dashboard_stats()` | 获取仪表盘统计数据 |
| 文件对话框 | `browse_directory(title)` | 浏览目录对话框 |
| | `browse_file(title, filter)` | 浏览文件对话框 |
| | `save_file_dialog(title, filter)` | 保存文件对话框 |
| 系统操作 | `open_in_explorer(path)` | 在资源管理器中打开 |
| | `open_url(url)` | 在浏览器中打开URL |
| | `ipc_ping()` | IPC连通性测试 |
| | `get_mock_data(type)` | 获取Mock数据 |
| 窗口控制 | `window_minimize()` | 最小化窗口 |
| | `window_maximize()` | 最大化窗口 |
| | `window_close()` | 关闭窗口 |
| 模板 | `get_templates()` | 获取模板列表 |

### 5.3 工作空间相关常量 ✅ 已实现

以下常量已在 `src/core/constants.py` 中定义，支撑工作空间识别与子项目分类：

| 常量/枚举值 | 类型 | 说明 |
|---|---|---|
| `ProjectType.PLC_WORKSPACE` | 枚举值 | PLC工作空间类型，用于标识包含多个子项目的根目录 |
| `ProjectType.PLC_LIBRARY` | 枚举值 | PLC共享库类型，用于标识跨项目复用的函数库目录 |
| `BusinessLine.LIBRARY` | 枚举值 | 共享库业务线，共享库降级构造 Project 时使用 |
| `WORKSPACE_IGNORED_DIRS` | `set` | 工作空间扫描时忽略的目录名集合：`.trae`, `.git`, `__pycache__`, `_archive`, `node_modules`, `.venvs`, `.plc-out` |
| `PLC_LIBRARY_CATEGORY_DIRS` | `set` | 共享库典型分类子目录名集合：`actuator`, `timer`, `counter`, `edge`, `convert`, `analog`, `motion`, `communication`, `safety` |
| `COMPANION_ROLE` | `str` | 伴生角色标识：`governance`，表示本工具定位为治理工具 |
| `COMPANION_PRIMARY_IDE` | `str` | 主开发环境标识：`Trae`，明确伴生对象 |
| `COMPANION_CAPABILITIES` | `list` | 本工具具备的能力列表：`mount`, `index`, `check`, `summarize`, `export` |
| `COMPANION_NON_CAPABILITIES` | `list` | 本工具不具备的能力列表：`edit_source`, `compile`, `deploy`, `debug_runtime` |
| `TRAJUMP_SUPPORTED_EXTENSIONS` | `set` | 支持伴生跳转的文件扩展名集合：`.scl`, `.st`, `.plc`, `.xml`, `.json`, `.md`, `.yaml`, `.yml`, `.txt`, `.csv`, `.xlsx`, `.xls` |
| `LibraryArtifactType` | `Enum` | 共享库资产类型枚举：`FB`(功能块)/`FC`(函数)/`DB`(数据块)/`UDT`(用户自定义类型)/`GVL`(全局变量表)/`PROGRAM`(程序)/`SPEC`(规范文档)/`DOC`(说明文档)/`TEST`(测试) |
| `SPEC_DIR_MARKERS` | `set` | 规范目录标识名集合：`00_通用规范`, `01_编程规范`, `02_设计规范`, `00_规范`, `spec`, `specs`, `standards` |
| `LIBRARY_ST_EXTENSIONS` | `set` | 共享库ST源码文件扩展名集合：`.scl`, `.st`, `.plc` |
| `LIBRARY_SPEC_EXTENSIONS` | `set` | 共享库规范文件扩展名集合：`.md`, `.yaml`, `.yml`, `.json` |

> **设计说明**: `WORKSPACE_IGNORED_DIRS` 与 `IGNORED_PROJECT_DIRS` 分离——前者用于工作空间级扫描（范围更广，包含 `_archive` 等），后者用于单项目资产扫描。`PLC_LIBRARY_CATEGORY_DIRS` 用于 `_is_plc_library()` 判定：目录含 `.plc.json` 且子目录与该集合有交集时识别为共享库。`SPEC_DIR_MARKERS` 用于区分共享库中的规范目录与分类子目录，目录名（大小写不敏感）命中该集合时识别为规范目录。`LibraryArtifactType` 通过 `_infer_artifact_type()` 将分类目录名映射到资产类型（如 `actuator`→`FB`、`convert`→`FC`），未知分类默认为 `DOC`。

---

## 6. 设计决策

### 6.1 为什么要引入 Workspace 层

因为当前问题不是"某个项目打不开"，而是产品模型缺失：
- 真实使用场景是一个 PLC 项目库下包含多个设备项目、共享库与规范目录
- 只保留单项目模型，会持续制造误判、补丁和分支堆积

### 6.2 为什么采用 Trae伴生而非独立主工具

因为用户真实工作流已经形成：
- Trae 提供更强的 AI 开发能力
- PLC代码主编辑不应迁回工具内部
- SW-2026-005 的价值在于工作空间治理与聚合能力，而不是重复造一个编辑器

### 6.3 为什么工作空间识别优先在 Service 层实现

为了避免：
- UI 控制器逻辑膨胀
- 树组件耦合识别细节
- 后续测试困难和文档失真

### 6.4 为什么从PyQt5迁移到PyWebView ✅ V4.0新增

V3.2 阶段 PyQt5 路线遇到系统性瓶颈：
- **FramelessWindow回归问题**: 系统标题栏未去除、DPI缩放问题反复出现
- **QSS系统性限制**: QSS无法还原HTML原型的视觉效果（渐变、阴影、动画、flex布局等）
- **双线维护成本**: 同时维护 PyQt5 控件代码和 HTML 原型，两者视觉一致性难以保证

决策：放弃 PyQt GUI 重写路线，改用 pywebview 6.x 直接运行 `index.html` 原型作为生产前端。PyQt5 保留为回退路径（环境变量 `PLC_GUI_MODE=pyqt` 触发）。

### 6.5 IPCBridge设计原则 ✅ V4.0新增

- **异常包装**: 每个API方法遵循 `_safe_call(name, fn, *args)` 模式，统一捕获异常并返回结构化错误信息
- **Mock模式支持**: 环境变量 `PLC_MOCK_DATA=1` 启用Mock数据（默认关闭），前端开发无需后端即可调试
- **事件推送**: `_emit(event, data)` 通过 `window.evaluate_js()` 将后端事件推送到前端
- **统一序列化**: 所有返回值统一JSON序列化，前端无需关心Python类型转换
- **职责边界**: IPCBridge 只做参数转换和异常包装，不承载业务逻辑

### 6.6 前端设计原则 ✅ V4.0新增

- **单文件HTML**: 当前 `index.html` 约2100行，后续需模块化拆分
- **CSS Design Tokens体系**: 色彩/间距/圆角/字体通过CSS变量统一管理
- **集中状态管理**: `state` 对象集中管理所有视图数据，避免分散状态
- **ipc便捷函数**: 30个 `ipc*` 便捷函数封装异步调用，简化前端调用链

---

## 7. 扩展约束

后续若继续演进以下能力，必须沿用当前 Workspace 架构：
- 共享库索引与版本治理
- 规范目录聚合与跨项目检查
- 工作空间级概览面板
- 聚合统计与导出

不允许：
- 直接在 Controller 中堆叠识别规则
- 在 UI 层新建大量独立状态副本
- 以未来方向文档替代当前主线文档
- 在前端HTML中直接import Python模块
- 绕过IPCBridge直接调用Service层
- 在IPCBridge中承载业务逻辑（只做参数转换和异常包装）

---

## 8. 与未来方向的关系

`012_V3.0开发规划_DEV-PLAN-V3.0.0.md` 仍可保留作为未来储备，但不属于当前工作空间支持主线。

当前主线优先级：
1. ~~先建立 Workspace 模型~~ ✅ Phase 1 已实现（常量、枚举、识别规则）
2. ~~再完成工作空间加载与治理~~ ✅ Phase 2 已实现（Controller 分支、Service 编排、Tree 渲染）
3. ~~固化 Trae 伴生工作流与跳转边界~~ ✅ Phase 3 已实现（CompanionService、伴生常量、跳转委托、编辑菜单）
4. ~~共享库与规范目录识别治理~~ ✅ Phase 4 已实现（LibraryService、LibraryArtifactType、规范目录标识、资产类型推断）
5. ~~工作空间治理与聚合报告~~ ✅ Phase 5 已实现（WorkspaceService、命名冲突检测、跨项目检查、聚合报告、汇总统计）
6. ~~PyWebView架构迁移~~ ✅ Phase 6 已实现（main.py双模式入口、create_window()、IPCBridge基础框架）
7. ~~IPCBridge API补全~~ ✅ Phase 7 已实现（38个API端点、_safe_call异常包装、_emit事件推送）
8. ~~前端全量对接~~ ✅ Phase 8 已实现（100%按钮绑定、30个ipc便捷函数、7视图状态管理）

### 8.1 实施阶段追踪

| 阶段 | 内容 | 状态 |
|---|---|---|
| Phase 1: Workspace Core | `ProjectType.PLC_WORKSPACE`/`PLC_LIBRARY`、`BusinessLine.LIBRARY`、`WORKSPACE_IGNORED_DIRS`、`PLC_LIBRARY_CATEGORY_DIRS`、`detect_project_type()` 四级识别 | ✅ 已实现 |
| Phase 2: Workspace Load | `load_workspace_from_path()`、`_open_as_workspace()`、`load_workspace()`、子项目加载与降级构造 | ✅ 已实现 |
| Phase 3: Companion Flow | `CompanionService`伴生跳转服务、`COMPANION_ROLE`/`COMPANION_PRIMARY_IDE`/`COMPANION_CAPABILITIES`/`COMPANION_NON_CAPABILITIES`/`TRAJUMP_SUPPORTED_EXTENSIONS`常量、`_jump_to_source()`委托跳转、ProjectTree双击跳转、编辑菜单"在Trae中打开" | ✅ 已实现 |
| Phase 4: Library Governance | `LibraryService`共享库治理服务、`LibraryArtifactType`/`SPEC_DIR_MARKERS`/`LIBRARY_ST_EXTENSIONS`/`LIBRARY_SPEC_EXTENSIONS`常量、`scan_library()`/`identify_spec_dirs()`/`get_library_summary()`/`_infer_artifact_type()`方法、`LibraryArtifact`/`LibraryScanResult`数据类、`ArtifactRegistryService.scan_library_artifacts()`/`identify_spec_dirs_in_library()` | ✅ 已实现 |
| Phase 5: Workspace Governance | `WorkspaceService`工作空间治理服务、`generate_report()`聚合报告、`detect_naming_conflicts()`命名冲突检测、`check_workspace()`跨项目检查、`get_workspace_statistics()`汇总统计、`_count_project_files()`项目文件统计、`WorkspaceCheckItem`/`NamingConflict`/`WorkspaceReport`数据类、`ProjectService.get_workspace_summary()`/`generate_workspace_report()`编排方法、`ProjectController.check_workspace()`/`generate_workspace_report()`UI入口、`ProjectTree`工作空间统计展示 | ✅ 已实现 |
| Phase 6: PyWebView Migration | `main.py`双模式入口（`PLC_GUI_MODE`环境变量控制）、`run_webview()`/`run_pyqt()`函数、`ImportError`自动回退机制、`create_window()`窗口创建函数、IPCBridge基础框架 | ✅ V4.0已实现 |
| Phase 7: IPCBridge API | IPCBridge 38个API端点、`_safe_call()`异常包装模式、`_emit()`事件推送机制、Mock模式支持（`PLC_MOCK_DATA`环境变量）、统一JSON序列化 | ✅ V4.0已实现 |
| Phase 8: Frontend Integration | `index.html`五区IDE布局、7视图（仪表盘/项目/文档/变更/检查/诊断/设置）、30个`ipc*`便捷函数、CSS Design Tokens体系、`state`集中状态管理、100%按钮绑定 | ✅ V4.0已实现 |

---

*文档版本: ARCH-V4.0.0 | 最后更新: 2026-06-01*
