# 架构设计文档 — V8.0.0 基于V9.0代码诊断的架构状态标注版

> **版本**: ARCH-V8.0.0
> **上一版本**: ARCH-V7.0.0 (全栈重构版)
> **最后更新**: 2026-06-03
> **变更摘要**: 基于V9.0代码诊断，标注48个IPC端点可用性矩阵、绘制实际数据流图、记录6项已知架构缺陷、更新Service/Model层实际状态

---

## 版本历史

| 版本 | 日期 | 变更摘要 |
|------|------|----------|
| V7.0.0 | 2026-06-02 | 全栈重构版：异常层次、枚举元数据、Repository层、APIGateway、前端模块化 |
| V8.0.0 | 2026-06-03 | 基于V9.0代码诊断的架构状态标注版：IPC可用性矩阵、数据流图、已知缺陷、Service/Model层实际状态更新 |

---

## 1. 架构重构动机

### 1.1 现有架构问题诊断

基于 2026-06-02 深度审查（后端 3.4/5、前端 2.7/5），识别出以下系统性架构缺陷：

| 维度 | 问题 | 严重度 | 根因 |
|------|------|--------|------|
| **后端-异常** | `except Exception: pass` 88处，异常静默吞没 | CRITICAL | 无项目级异常层次结构 |
| **后端-DRY** | 枚举备用定义60行重复、描述映射3处重复 | HIGH | 缺乏枚举元数据机制 |
| **后端-封装** | 直接访问其他类私有方法、getattr反射滥用 | HIGH | Service接口边界模糊 |
| **后端-性能** | `rglob("*")` 全目录扫描2处、无缓存策略 | HIGH | 无数据访问抽象层 |
| **后端-数据** | Markdown文件作数据库，查询能力有限 | MEDIUM | 无索引/缓存层 |
| **前端-架构** | 50+全局函数、无模块隔离、innerHTML拼接 | CRITICAL | 原型阶段过程式代码 |
| **前端-死代码** | layout.js全文件死代码、5个CSS文件未使用 | HIGH | IDE→管理器迁移不彻底 |
| **前端-CSS** | 9个变量未定义、570行内联CSS与外部冲突 | HIGH | CSS体系无设计 |
| **前端-IPC** | 事件处理被monkey-patch、调试日志残留 | HIGH | IPC层缺乏统一规范 |
| **IPC桥接** | 35+API未精简、Mock数据混入生产代码 | HIGH | 无API版本管理 |

### 1.2 重构目标

1. **可维护性**: 消除全局函数污染，建立模块化边界
2. **可测试性**: 核心基础设施100%可单元测试
3. **DRY合规**: 枚举/映射/描述单一定义源
4. **异常可追踪**: 建立项目级异常层次，零 `except: pass`
5. **性能可控**: 数据访问层统一缓存策略
6. **前端工程化**: CSS变量体系完整、模块化加载、状态管理统一

### 1.3 不可破坏行为（回归清单）

| # | 行为 | 验证方式 |
|---|------|----------|
| R1 | CLI 13个子命令全部可用 | `pytest tests/test_cli.py` |
| R2 | PyWebView启动后IPCBridge对接正常 | 手工启动验证 |
| R3 | 规范检查6检查器结果不变 | `pytest tests/test_*_checker.py` |
| R4 | 变更单V2 CRUD + 12态状态机正确 | `pytest tests/test_change_service_v2.py` |
| R5 | Excel导出功能正常 | `pytest tests/test_*exporter*.py` |
| R6 | 工作空间挂载后项目列表正确显示 | 手工验证 |
| R7 | 自动修复扫描/预览/修复/回滚流程 | `pytest tests/test_auto_fix*.py` |

---

## 2. 架构总览

### 2.1 分层架构图

```
┌──────────────────────────────────────────────────────────────────┐
│                     Presentation Layer                            │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌───────────┐ │
│  │ Dashboard   │  │ ChangeCenter│  │ ProjectDetail│  │ Settings │ │
│  │ View        │  │ View        │  │ View         │  │ View     │ │
│  └──────┬─────┘  └──────┬─────┘  └──────┬──────┘  └─────┬────┘ │
│         │               │               │                │       │
│  ┌──────┴───────────────┴───────────────┴────────────────┴────┐ │
│  │                    View Router (navigation.js)              │ │
│  └──────────────────────────┬─────────────────────────────────┘ │
│                             │                                     │
│  ┌──────────────────────────┴─────────────────────────────────┐ │
│  │                  State Store (store.js)                      │ │
│  │  • 集中状态管理  • 变更通知  • 持久化接口                      │ │
│  └──────────────────────────┬─────────────────────────────────┘ │
│                             │                                     │
│  ┌──────────────────────────┴─────────────────────────────────┐ │
│  │                   IPC Client (ipc.js)                        │ │
│  │  • 统一API调用  • 超时重试  • 错误处理  • 事件监听            │ │
│  └──────────────────────────┬─────────────────────────────────┘ │
└─────────────────────────────┼───────────────────────────────────┘
                              │ window.pywebview.api
┌─────────────────────────────┼───────────────────────────────────┐
│                     IPC Bridge Layer                             │
│  ┌──────────────────────────┴─────────────────────────────────┐ │
│  │                   API Gateway (api_gateway.py)               │ │
│  │  • 请求路由  • 参数校验  • 响应标准化  • Mock模式切换         │ │
│  └──────────────────────────┬─────────────────────────────────┘ │
│                             │                                     │
│  ┌──────────────────────────┴─────────────────────────────────┐ │
│  │                  Event Dispatcher (event_bus.py)             │ │
│  │  • 异常日志  • 异步发射  • 事件命名空间                       │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│                      Service Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Core Services │  │ Change Domain│  │ Workspace Domain     │  │
│  │              │  │ Services     │  │ Services             │  │
│  │ • Project    │  │              │  │                      │  │
│  │ • Document   │  │ • ChangeV2   │  │ • WorkspaceDashboard │  │
│  │ • Diagnostic │  │ • NumberGen  │  │ • WorkspaceGovern    │  │
│  │ • Template   │  │ • TemplateRdr│  │ • Library            │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │                 │                      │              │
│  ┌──────┴─────────────────┴──────────────────────┴───────────┐ │
│  │                 Data Access Layer (repository.py)            │ │
│  │  • 文件系统抽象  • 缓存策略  • 查询索引  • 事务性写入        │ │
│  └──────────────────────────┬─────────────────────────────────┘ │
└─────────────────────────────┼───────────────────────────────────┘
┌─────────────────────────────┼───────────────────────────────────┐
│                       Core Layer                                 │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌───────────┐ │
│  │ constants   │  │ exceptions │  │ config     │  │ models    │ │
│  │ (枚举+元数据)│  │ (异常层次)  │  │ (配置加载) │  │ (数据模型)│ │
│  └────────────┘  └────────────┘  └────────────┘  └───────────┘ │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                │
│  │ validators  │  │ logger     │  │ path_resolver│               │
│  └────────────┘  └────────────┘  └────────────┘                │
└─────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                           │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌───────────┐ │
│  │ checkers/   │  │ fixers/    │  │ parsers/   │  │ exporters/│ │
│  │ scanners/   │  │ sync/      │  │            │  │           │ │
│  └────────────┘  └────────────┘  └────────────┘  └───────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 核心设计原则

| 原则 | 说明 | 约束 |
|------|------|------|
| **单向依赖** | 上层依赖下层，下层不感知上层 | Service → Core → Infrastructure，禁止反向 |
| **接口隔离** | Service对外暴露方法签名，内部实现可替换 | 其他Service通过公开方法调用，禁止访问私有成员 |
| **单一真源** | 枚举定义、描述映射、异常类型各只有一个来源 | 禁止 `except ImportError` 备用定义 |
| **异常必追踪** | 所有 `except` 必须记录日志或重新抛出 | 禁止 `except Exception: pass` |
| **数据访问抽象** | Service不直接操作文件系统，通过Repository层 | 文件路径构造、读写、缓存统一在Repository |
| **前端模块化** | 每个JS文件一个职责，通过Store通信 | 禁止全局函数、禁止跨模块直接DOM操作 |

---

## 3. 后端架构设计

### 3.1 异常层次结构

**新增文件**: `src/core/exceptions.py`

```
PLCToolError (基类)
├── StorageError
│   ├── FileNotFoundError
│   ├── FileParseError
│   └── FileWriteError
├── ChangeManagementError
│   ├── ChangeNotFoundError
│   ├── InvalidTransitionError
│   ├── DuplicateChangeNumberError
│   └── ChangeValidationError
├── WorkspaceError
│   ├── WorkspaceNotMountedException
│   ├── ProjectNotFoundError
│   └── InvalidWorkspaceStructureError
├── SpecCheckError
│   ├── CheckerNotFoundError
│   └── CheckerExecutionError
└── ConfigError
    ├── ConfigLoadError
    └── ConfigValidationError
```

**使用规范**:
- Service层抛出具体异常类型，不抛通用 `Exception`
- IPCBridge捕获异常后转换为 `{success: false, error: str, error_code: str}` 响应
- EventBus `emit()` 中 `except Exception as e: logger.error(...)` 记录完整堆栈

### 3.2 枚举元数据机制（DRY消除）

**重构 `src/core/constants.py`**: 为每个枚举添加 `description` 属性，消除分离的描述映射表。

```python
class ChangeDomain(Enum):
    ELEC = "ELEC"
    MECH = "MECH"
    PLC = "PLC"
    HMI = "HMI"
    SCPT = "SCPT"
    DOCU = "DOCU"
    SAFE = "SAFE"

    def __init__(self, value):
        self._value_ = value
        self._descriptions = {
            "ELEC": "电气",
            "MECH": "机械",
            "PLC": "PLC程序",
            "HMI": "HMI界面",
            "SCPT": "脚本/SCADA",
            "DOCU": "文档",
            "SAFE": "安全",
        }

    @property
    def description(self) -> str:
        return self._descriptions.get(self.value, self.value)

    @property
    def icon(self) -> str:
        icons = {
            "ELEC": "⚡", "MECH": "⚙️", "PLC": "🔧",
            "HMI": "🖥️", "SCPT": "📜", "DOCU": "📄", "SAFE": "🛡️",
        }
        return icons.get(self.value, "📋")
```

**迁移策略**:
- 删除 `BUSINESS_LINE_DESC`/`PROJECT_STATUS_DESC`/`PROJECT_TYPE_DESC` 等所有分离映射表
- 删除 `change_request_v2.py` 中的 `except ImportError` 备用枚举定义（60行）
- 删除 `change_template_renderer.py` 中的 `_get_domain_description()`/`_get_nature_description()` 重复映射
- 统一使用 `ChangeDomain.ELEC.description` / `ChangeDomain.ELEC.icon` 访问

### 3.3 Service层重构

#### 3.3.1 Service分组与接口边界

**V8.0.0 实际状态**：当前代码库包含9个活跃Service（APIGateway注册8个 + WorkflowService骨架1个），另有4个辅助Service未注册到Gateway。

| 域 | Service | 代码行数 | 注册到Gateway | 公开接口 | 依赖 |
|----|---------|----------|---------------|----------|------|
| **Core** | ProjectService | ~1347 | ✅ | load_workspace, scan_project, get_project_detail, create_project | Repository |
| **Core** | DocumentService | ~486 | ✅ | create_document, list_documents, read_document, save_document, get_templates | Repository, TemplateService |
| **Core** | DiagnosticService | ~506 | ✅ | run_diagnosis, get_cached_result | SpecCheckerService, Repository |
| **Change** | ChangeServiceV2 | ~1015 | ✅ | create, transition, list, get, statistics, validate | Repository, ChangeNumberGenerator, ChangeTemplateRenderer |
| **Workspace** | WorkspaceService | ~484 | ✅ | mount, unmount, check, report | Repository |
| **Workspace** | WorkspaceDashboardService | ~638 | ✅ | get_overview, get_project_cards, refresh | ProjectService, DiagnosticService, Repository |
| **Infra** | SpecCheckerService | ~400 | ✅ | run_checks, get_checkers, run_single | checkers/*, Repository |
| **Infra** | AutoFixService | ~690 | ✅ | scan, preview, fix, rollback | fixers/*, Repository |
| **Workflow** | WorkflowService | ~50 | ❌ | 骨架级，无实质功能 | — |
| **辅助** | TemplateService | — | ❌ | get_templates, render_template | Repository |
| **辅助** | LibraryService | — | ❌ | get_library_summary, scan | Repository |
| **辅助** | ChangeNumberGenerator | — | ❌ | generate, parse, list_existing | Repository |
| **辅助** | ChangeTemplateRenderer | — | ❌ | render, render_section | constants (枚举元数据) |

> **注意**: V7.0.0文档中描述的15个Service为规划目标，实际V9.0代码中APIGateway仅注册8个域路由，WorkflowService为骨架级（~50行），4个辅助Service由主Service内部调用。

**接口规则**:
- Service之间通过公开方法调用，禁止 `obj._private_method()`
- Service不直接 `open()`/`write()` 文件，通过 Repository 操作
- Service方法签名必须包含类型注解和返回值类型

#### 3.3.2 WorkspaceDashboardService 重构

**问题**: 直接访问 `WorkspaceService._count_project_files()`、`rglob("*")` 全扫描

**重构方案**:

```python
class WorkspaceDashboardService:
    def __init__(self, repo: Repository, project_svc: ProjectService,
                 diagnostic_svc: DiagnosticService):
        self._repo = repo
        self._project_svc = project_svc
        self._diagnostic_svc = diagnostic_svc

    def get_project_cards(self, workspace_path: str,
                          filters: dict = None) -> list[ProjectCard]:
        projects = self._project_svc.list_projects(workspace_path)
        cards = [self._build_card(p) for p in projects]
        if filters:
            cards = self._apply_filters(cards, filters)
        return sorted(cards, key=lambda c: c.health_score, reverse=True)

    def _build_card(self, project: Project) -> ProjectCard:
        cached = self._repo.get_cached(f"card:{project.path}")
        if cached and not cached.is_expired(ttl=300):
            return cached.data
        card = ProjectCard(
            name=project.name,
            path=project.path,
            project_type=project.project_type,
            health_score=self._diagnostic_svc.get_cached_score(project.path),
            doc_coverage=self._repo.get_doc_coverage(project.path),
            spec_compliance=self._repo.get_spec_compliance(project.path),
            last_modified=self._repo.get_last_modified(project.path),
        )
        self._repo.set_cached(f"card:{project.path}", card)
        return card
```

**关键改进**:
- 通过 `ProjectService.list_projects()` 公开接口获取项目列表
- 健康度/合规率通过缓存获取，避免重复计算
- 文档覆盖率/最后修改时间通过 Repository 统一查询

### 3.4 数据访问层 (Repository)

**新增文件**: `src/core/repository.py`

```python
class Repository:
    """文件系统数据访问层 - 统一缓存/索引/查询"""

    def __init__(self, cache_ttl: int = 300):
        self._cache: dict[str, CacheEntry] = {}
        self._cache_ttl = cache_ttl
        self._index: dict[str, ProjectIndex] = {}

    def read_file(self, path: str) -> str: ...
    def write_file(self, path: str, content: str) -> None: ...
    def list_files(self, dir_path: str, pattern: str = "*",
                   exclude: list[str] = None) -> list[Path]: ...
    def get_cached(self, key: str) -> Optional[CacheEntry]: ...
    def set_cached(self, key: str, data: Any, ttl: int = None) -> None: ...
    def invalidate(self, key: str) -> None: ...
    def get_doc_coverage(self, project_path: str) -> float: ...
    def get_spec_compliance(self, project_path: str) -> float: ...
    def get_last_modified(self, project_path: str) -> str: ...
    def build_index(self, workspace_path: str) -> None: ...
```

**设计要点**:
- 所有文件操作通过 Repository，Service 不直接 `open()`/`Path.glob()`
- 内置内存缓存（TTL 5分钟），避免重复计算
- `list_files()` 支持 exclude 规则（`.git`/`__pycache__`/`node_modules`）
- `build_index()` 首次挂载工作空间时构建索引，后续查询走索引

### 3.5 EventBus 重构

```python
class EventBus:
    def emit(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        handlers = self._handlers.get(event_name, [])
        if not handlers:
            return
        for handler in handlers:
            try:
                handler(*args, **kwargs)
            except Exception as e:
                self._logger.error(
                    "Event handler error for '%s': %s",
                    event_name, e, exc_info=True
                )
```

**改进点**:
- `except Exception: pass` → `except Exception as e: logger.error(..., exc_info=True)`
- 添加 `logger` 成员
- 添加事件命名空间: `workspace:mounted`、`change:created`、`project:opened`

### 3.6 ConfigLoader 线程安全

```python
class ConfigLoader:
    _lock = threading.Lock()

    @classmethod
    def load(cls, config_dir: str = None) -> dict:
        with cls._lock:
            ...

    @classmethod
    def set(cls, key: str, value: Any) -> None:
        with cls._lock:
            ...

    @classmethod
    def save(cls) -> None:
        with cls._lock:
            ...
```

---

## 4. IPC桥接层设计

### 4.1 API Gateway 模式

**重构 `src/ui/webview_window.py`**: 将 IPCBridge 拆分为 APIGateway + MockDataProvider。

**新增文件**: `src/ui/api_gateway.py`

```python
class APIGateway:
    """统一API网关 - 请求路由/参数校验/响应标准化"""

    def __init__(self):
        self._repo = Repository()
        self._services: dict[str, Any] = {}
        self._mock_provider = MockDataProvider()
        self._use_mock = os.environ.get("PLC_MOCK_DATA", "0") == "1"

    def _register_services(self):
        self._services = {
            "project": ProjectService(self._repo),
            "change": ChangeServiceV2(self._repo, ...),
            "workspace_dashboard": WorkspaceDashboardService(self._repo, ...),
            "spec_checker": SpecCheckerService(self._repo),
            ...
        }

    def _dispatch(self, domain: str, method: str, **kwargs) -> dict:
        service = self._services.get(domain)
        if not service:
            raise ServiceNotFoundError(domain)
        handler = getattr(service, method)
        result = handler(**kwargs)
        return {"success": True, "data": result}
```

**新增文件**: `src/ui/mock_data.py`

```python
class MockDataProvider:
    """Mock数据提供者 - 独立于生产代码"""

    PROJECTS = [...]
    CHECKERS = [...]
    SPEC_RESULT = {...}
    DIAGNOSTIC = {...}
```

### 4.2 IPCBridge API 可用性矩阵

**V8.0.0 诊断结果**：当前代码库共暴露48个IPC端点，其中14个为WebViewBridge直接方法、34个通过APIGateway路由。

| # | WebViewBridge方法 | 路由域 | 路由方法 | 可用性 | 备注 |
|---|-------------------|--------|----------|--------|------|
| 1 | ipc_ping | 直接 | — | ✅可用 | |
| 2 | get_app_info | 直接 | — | ✅可用 | |
| 3 | get_settings | 直接 | — | ✅可用 | |
| 4 | update_setting | 直接 | — | ✅可用 | |
| 5 | reset_settings | 直接 | — | ✅可用 | |
| 6 | browse_directory | 直接 | — | ✅可用 | |
| 7 | browse_file | 直接 | — | ✅可用 | |
| 8 | save_file_dialog | 直接 | — | ✅可用 | |
| 9 | open_in_explorer | 直接 | — | ✅可用 | |
| 10 | open_url | 直接 | — | ✅可用 | |
| 11 | window_minimize | 直接 | — | ✅可用 | |
| 12 | window_maximize | 直接 | — | ✅可用 | |
| 13 | window_close | 直接 | — | ✅可用 | |
| 14 | get_mock_data | 直接 | — | ✅可用 | |
| 15 | get_project_overview | project | get_project_overview | ✅可用 | |
| 16 | get_project_detail | project | get_project_detail | ✅可用 | |
| 17 | create_project | project | create_project | ✅可用 | |
| 18 | open_project | project | open_project | ✅可用 | |
| 19 | close_project | project | close_project | ✅可用 | |
| 20 | save_project_info | project | save_project_info | ✅可用 | |
| 21 | list_directory_tree | project | list_directory_tree | ✅可用 | |
| 22 | get_recent_projects | project | get_recent_projects | ✅可用 | |
| 23 | run_version_check | project | run_version_check | ⚠️部分可用 | 依赖SyncEngine |
| 24 | generate_chg | project | generate_chg | ⚠️部分可用 | 依赖SyncEngine |
| 25 | generate_ifc | project | generate_ifc | ⚠️部分可用 | 依赖SyncEngine |
| 26 | export_excel_single | project | export_excel_single | ⚠️部分可用 | 依赖ExcelExporter |
| 27 | export_excel_batch | project | export_excel_batch | ⚠️部分可用 | 依赖ExcelExporter |
| 28 | run_spec_check | spec_checker | run_spec_check | ✅可用 | |
| 29 | get_checkers | spec_checker | get_checkers | ✅可用 | |
| 30 | run_diagnosis | diagnostic | run_diagnosis | ✅可用 | |
| 31 | list_change_requests | change | list_change_requests | ✅可用 | |
| 32 | create_change_request | change | create_change_request | ✅可用 | 旧版API |
| 33 | update_change_status | change | update_change_status | ✅可用 | 旧版API |
| 34 | approve_change_request | change | approve_change_request | ✅可用 | 旧版API |
| 35 | transition_change_status_v2 | change | transition_change_status_v2 | ✅可用 | |
| 36 | create_change_request_v2 | change | create_change_request_v2 | ✅后端可用 | ❌前端IPC链路断裂 |
| 37 | get_change_statistics | change | get_change_statistics | ✅可用 | |
| 38 | export_change_report | change | export_change_report | ✅可用 | |
| 39 | get_dashboard_data | workspace_dashboard | get_dashboard_data | ✅可用 | 无缓存 |
| 40 | get_dashboard_stats | workspace_dashboard | get_dashboard_stats | ✅可用 | 无缓存 |
| 41 | mount_workspace | workspace | mount_workspace | ✅可用 | |
| 42 | get_workspace_summary | workspace | get_workspace_summary | ✅可用 | |
| 43 | check_workspace | workspace | check_workspace | ✅可用 | |
| 44 | generate_workspace_report | workspace | generate_workspace_report | ✅可用 | |
| 45 | get_available_fixers | auto_fix | get_available_fixers | ✅可用 | |
| 46 | scan_fixes | auto_fix | scan_fixes | ✅可用 | |
| 47 | fix_project | auto_fix | fix_project | ✅可用 | |
| 48 | get_templates | document | get_templates | ❌不可用 | WebViewBridge未暴露 |

**可用性统计**:
- ✅可用: 41个 (85.4%)
- ⚠️部分可用: 5个 (10.4%) — 依赖外部组件(SyncEngine/ExcelExporter)
- ❌不可用: 1个 (2.1%) — get_templates
- ✅后端可用但❌前端断裂: 1个 (2.1%) — create_change_request_v2

### 4.3 API精简方案

**V8.0.0 自动事件推送**: `WebViewBridge._route()` 在方法返回 `success=True` 时，自动查找 `_EVENT_MAP` 并推送对应事件到前端：

```python
# webview_window.py V8.0.0 新增
_EVENT_MAP = {
    ("workspace", "mount_workspace"): "workspace_opened",
    ("project", "open_project"): "project_opened",
    ("project", "close_project"): "project_closed",
    ("project", "create_project"): "project_created",
    ("document", "create_document"): "document_created",
}
```

前端 `navigation.js` 通过 `__ipc_recv` 包装器接收事件，自动触发 UI 更新（侧边栏、状态栏、视图切换）。

### 4.4 API精简方案

**现状**: 48个IPC端点，命名不统一

**目标**: 15个核心API，按域分组

| 域 | API方法 | 对应Service方法 |
|----|---------|----------------|
| **workspace** | `mount_workspace(path)` | WorkspaceService.mount |
| **workspace** | `get_workspace_overview()` | WorkspaceDashboardService.get_overview |
| **workspace** | `get_project_cards(filters)` | WorkspaceDashboardService.get_project_cards |
| **project** | `get_project_detail(path)` | ProjectService.get_project_detail |
| **project** | `list_directory_tree(path)` | Repository.list_files |
| **change** | `create_change_request(params)` | ChangeServiceV2.create |
| **change** | `list_change_requests(filters)` | ChangeServiceV2.list |
| **change** | `transition_change_status(id, target, reason)` | ChangeServiceV2.transition |
| **change** | `get_change_statistics(path)` | ChangeServiceV2.statistics |
| **check** | `run_spec_check(path, checkers)` | SpecCheckerService.run_checks |
| **check** | `run_diagnosis(path)` | DiagnosticService.run_diagnosis |
| **doc** | `create_document(params)` | DocumentService.create |
| **doc** | `list_documents(path)` | DocumentService.list |
| **fix** | `scan_fixes(path, fixer_id)` | AutoFixService.scan |
| **fix** | `apply_fix(path, fixer_id, items)` | AutoFixService.fix |
| **export** | `export_excel(path, mode)` | ExcelExporter.export |
| **system** | `get_app_info()` | constants |
| **system** | `get_settings()` | SettingsManager |
| **system** | `update_setting(key, value)` | SettingsManager |
| **system** | `browse_directory()` | webview dialog |
| **system** | `window_action(action)` | window minimize/maximize/close |

**命名规范**:
- 格式: `{域}_{动作}` (snake_case)
- 前端调用: `ipc.call('workspace.mount', {path: '...'})`
- 响应格式: `{success: bool, data?: any, error?: string, error_code?: string}`

### 4.5 前端IPC Client重构

**重构 `ui_prototype/js/ipc.js`**:

```javascript
const IPC = {
    _api: () => window.pywebview?.api,

    async call(domain_method, params = {}) {
        const api = this._api();
        if (!api) {
            return {success: false, error: "IPC不可用", error_code: "IPC_UNAVAILABLE"};
        }
        const [domain, method] = domain_method.split(".");
        const apiMethod = `${domain}_${method}`;
        try {
            const result = await api[apiMethod](params);
            return result || {success: true};
        } catch (e) {
            console.error(`[IPC] ${apiMethod} failed:`, e);
            return {success: false, error: e.message, error_code: "IPC_ERROR"};
        }
    },

    on(event, handler) {
        if (!this._listeners[event]) this._listeners[event] = [];
        this._listeners[event].push(handler);
    },

    _handleMessage(payload) {
        const {event, data} = JSON.parse(payload);
        (this._listeners[event] || []).forEach(h => {
            try { h(data); } catch(e) { console.error(`[IPC] event handler error:`, e); }
        });
    }
};

window.__ipc_recv = (payload) => IPC._handleMessage(payload);
```

**改进点**:
- 统一 `IPC.call('domain.method', params)` 调用方式
- 单一 `__ipc_recv` 事件处理入口，消除 monkey-patch
- 内置错误处理和日志
- 删除 `ipcCall()`/`_pyapi()` 别名冗余

---

## 5. 数据流图

**V8.0.0 新增**：基于V9.0代码实际调用链路绘制。

```
前端 JS Layer
    │
    ├── ipc.js (_pyapi) ─── window.pywebview.api.{method}()
    │
    ▼
WebViewBridge Layer (webview_window.py)
    │
    ├── 直接方法 (ping/get_app_info/settings/browse/window_*)
    │
    ├── APIGateway._dispatch(domain, method, *args)
    │   │
    │   ▼
    │   APIGateway Layer (api_gateway.py)
    │   │
    │   ├── 域路由: project/change/workspace/workspace_dashboard/
    │   │             spec_checker/diagnostic/document/auto_fix
    │   │
    │   ├── ⚠️ BUG: 每次dispatch都 new Service()
    │   │
    │   ▼
    │   Service Layer
    │   │
    │   ├── ProjectService (~1347行)
    │   ├── ChangeServiceV2 (~1015行)
    │   ├── WorkspaceService (~484行)
    │   ├── WorkspaceDashboardService (~638行)
    │   ├── SpecCheckerService (~400行)
    │   ├── DiagnosticService (~506行)
    │   ├── DocumentService (~486行)
    │   ├── AutoFixService (~690行)
    │   └── WorkflowService (~50行, 骨架级)
    │   │
    │   ▼
    │   Core Layer
    │   │
    │   ├── Repository (文件读写/缓存/原子写入)
    │   ├── EventBus (事件订阅/发射)
    │   ├── Constants (20+枚举)
    │   └── Config/Settings
    │   │
    │   ▼
    │   文件系统
    │   ├── .plc_project.json (项目元数据)
    │   ├── project.json (项目配置)
    │   ├── CHG-*.md (变更单)
    │   └── 版本变更台帐.md
```

**关键数据流路径**:

| 路径 | 调用链 | 备注 |
|------|--------|------|
| 工作空间挂载 | 前端→mount_workspace→WorkspaceService.mount→Repository.read_file→.plc_project.json | 触发workspace_opened事件 |
| 项目详情 | 前端→get_project_detail→ProjectService.get_project_detail→Repository.read_file→project.json | |
| 变更单创建 | 前端→create_change_request→ChangeServiceV2.create→Repository.write_file→CHG-*.md | 触发project_created事件 |
| 规范检查 | 前端→run_spec_check→SpecCheckerService.run_checks→checkers/*→Repository | |
| 诊断 | 前端→run_diagnosis→DiagnosticService.run_diagnosis→SpecCheckerService+Repository | |
| 自动修复 | 前端→scan_fixes→AutoFixService.scan→fixers/*→Repository | |

---

## 6. 已知架构缺陷

**V8.0.0 新增**：基于V9.0代码诊断发现的架构级缺陷，按严重度排序。

| # | 缺陷 | 严重度 | 当前代码位置 | 修复方案 |
|---|------|--------|-------------|----------|
| AD-1 | APIGateway每次请求新建Service实例 | 致命 | api_gateway.py `_dispatch()` L64-67: `if isinstance(service, type): instance = service()` | 改为注册单例实例，`_register_services()`中直接实例化 |
| AD-2 | IPC调用链路命名不一致 | 致命 | 前端ipc.js + WebViewBridge | 统一命名或添加别名映射表 |
| AD-3 | get_templates方法缺失 | 严重 | WebViewBridge未暴露document域get_templates | 添加方法路由到DocumentService |
| AD-4 | Mock数据格式不一致 | 严重 | mock_data.py | 对齐真实Service返回格式，添加格式校验 |
| AD-5 | Dashboard无缓存 | 中等 | WorkspaceDashboardService | 添加TTL+mtime缓存策略 |
| AD-6 | WorkflowService过于简陋 | 低 | workflow_service.py (~50行) | 后续迭代完善，当前不影响功能 |

**缺陷详情**:

#### AD-1: APIGateway每次请求新建Service实例

```python
# api_gateway.py L64-67 — 当前问题代码
if isinstance(service, type):
    instance = service()          # 每次dispatch都new一个实例
    handler = getattr(instance, method)
```

**影响**:
- Service内部状态无法保持（如缓存、已挂载的工作空间路径）
- 每次请求重复初始化，性能浪费
- `ProjectService.open_project()` 设置的当前项目状态在下次调用时丢失

**修复方案**:
```python
def _register_services(self):
    self._services = {
        "project": ProjectService(),          # 直接实例化
        "change": ChangeServiceV2(),
        "workspace": WorkspaceService(),
        ...
    }
```

#### AD-2: IPC调用链路命名不一致

前端 `ipc.js` 使用 `_pyapi('method_name')` 调用，而 `WebViewBridge` 方法名与 `APIGateway` 路由方法名存在映射差异，导致 `create_change_request_v2` 等方法前端IPC链路断裂。

#### AD-3: get_templates方法缺失

`WebViewBridge` 中 `get_templates()` 调用 `self._route("document", "get_templates")`，但 `DocumentService` 中该方法可能未实现或签名不匹配，导致前端无法获取文档模板列表。

---

## 7. 前端架构设计

### 7.1 模块化结构

**重构后的文件结构**:

```
ui_prototype/
├── index.html              (仅HTML骨架，零内联CSS/JS)
├── css/
│   ├── variables.css       (设计令牌：颜色/字体/间距/圆角/阴影)
│   ├── reset.css           (CSS重置)
│   ├── layout.css          (管理器布局：左面板+右内容+状态栏)
│   ├── components.css      (通用组件：按钮/卡片/表单/Toast/对话框)
│   ├── dashboard.css       (项目总览视图)
│   ├── project-detail.css  (项目详情视图)
│   ├── change-center.css   (变更管理中心)
│   ├── change-wizard.css   (变更单向导)
│   └── settings.css        (设置视图)
├── js/
│   ├── app.js              (应用入口：初始化Store/IPC/Router)
│   ├── store.js            (集中状态管理)
│   ├── ipc.js              (IPC Client)
│   ├── router.js           (视图路由)
│   ├── components/
│   │   ├── toast.js        (Toast通知组件)
│   │   ├── dialog.js       (对话框组件，替代alert/prompt)
│   │   ├── sidebar.js      (左侧面板组件)
│   │   └── statusbar.js    (底部状态栏组件)
│   └── views/
│       ├── dashboard.js    (项目总览视图)
│       ├── project-detail.js (项目详情视图)
│       ├── change-center.js  (变更管理中心)
│       ├── change-wizard.js  (变更单创建向导)
│       └── settings.js     (设置视图)
```

**删除的文件**:
- `js/layout.js` (IDE布局死代码)
- `js/handlers.js` (功能合并到各View)
- `js/navigation.js` (功能合并到router.js)
- `js/sidebar-templates.js` (功能合并到components/sidebar.js)
- `js/checkers.js` (功能合并到dashboard视图)
- `js/utils.js` (功能合并到store.js)
- `css/activity-bar.css` (IDE残留)
- `css/bottom-panel.css` (IDE残留)
- `css/content-area.css` (IDE残留)
- `css/placeholder.css` (未使用)
- `css/responsive.css` (未使用)
- `css/spec-check.css` (合并到project-detail)
- `css/document.css` (合并到project-detail)
- `css/change.css` (合并到change-center)
- `css/change-list.css` (合并到change-center)
- `css/auto-fix.js` (合并到project-detail)
- `css/excel-export.js` (合并到project-detail)
- `css/workspace.js` (合并到dashboard)

### 7.2 集中状态管理 (Store)

**新增 `js/store.js`**:

```javascript
const Store = {
    _state: {
        workspace: null,
        projects: [],
        currentProject: null,
        currentView: "dashboard",
        dashboardStats: null,
        changeRequests: [],
        settings: {},
        appInfo: null,
    },

    _subscribers: {},

    get(key) {
        return this._state[key];
    },

    set(key, value) {
        const old = this._state[key];
        this._state[key] = value;
        if (old !== value) {
            this._emit(`${key}:changed`, value, old);
        }
    },

    on(event, handler) {
        if (!this._subscribers[event]) this._subscribers[event] = [];
        this._subscribers[event].push(handler);
    },

    off(event, handler) {
        this._subscribers[event] = (this._subscribers[event] || [])
            .filter(h => h !== handler);
    },

    _emit(event, ...args) {
        (this._subscribers[event] || []).forEach(h => {
            try { h(...args); } catch(e) { console.error(`[Store] ${event} handler error:`, e); }
        });
    },

    async loadWorkspace(path) {
        const result = await IPC.call("workspace.mount", {path});
        if (result.success) {
            this.set("workspace", result.data.workspace);
            this.set("projects", result.data.projects);
            this.set("dashboardStats", result.data.stats);
        }
        return result;
    },

    async selectProject(projectPath) {
        const result = await IPC.call("project.get_detail", {path: projectPath});
        if (result.success) {
            this.set("currentProject", result.data);
        }
        return result;
    },
};
```

**设计要点**:
- 所有状态通过 `Store.get()`/`Store.set()` 访问，禁止直接操作全局变量
- 状态变更自动通知订阅者（观察者模式）
- 异步操作封装在 Store 方法中，View 只需调用 `Store.loadWorkspace()` 然后监听 `workspace:changed`
- 消除 `state.js` + `navigation.js currentView` + `change-wizard.js _wizardState` 三处状态分散

**V8.0.0 向后兼容桥接 (Proxy)**:

由于现有 `ipc.js`、`navigation.js`、`dashboard.js` 等文件使用 `state.xxx = value` 直接赋值语法，V8.0.0 通过 ES6 Proxy 实现 Store ↔ state 双向桥接：

```javascript
// store.js V8.0.0 新增
window.state = new Proxy({}, {
    get(target, prop)  { return Store.get(prop); },
    set(target, prop, value) { Store.set(prop, value); return true; },
    deleteProperty(target, prop) { Store.set(prop, undefined); return true; },
    has(target, prop)  { return Store.get(prop) !== undefined; },
    ownKeys(target)    { return Object.keys(Store.snapshot()); },
    getOwnPropertyDescriptor(target, prop) { /* ... */ },
});
```

**效果**: 所有 `state.workspaceProjects = [...]` 自动转换为 `Store.set('workspaceProjects', [...])`，所有 `state.workspaceProjects` 自动转换为 `Store.get('workspaceProjects')`。无需修改任何现有 JS 文件。

### 7.3 视图路由 (Router)

**新增 `js/router.js`**:

```javascript
const Router = {
    _views: {},
    _currentView: null,
    _container: null,

    register(name, viewModule) {
        this._views[name] = viewModule;
    },

    async navigate(viewName, params = {}) {
        if (this._currentView?.name === viewName) return;
        if (this._currentView?.destroy) {
            this._currentView.destroy();
        }
        const view = this._views[viewName];
        if (!view) {
            console.error(`[Router] View not found: ${viewName}`);
            return;
        }
        this._currentView = {name: viewName, ...view};
        const container = this._container || document.getElementById("main-content");
        container.innerHTML = "";
        const el = await view.render(params);
        container.appendChild(el);
        if (view.mount) view.mount(params);
        Store.set("currentView", viewName);
    },

    init(containerId) {
        this._container = document.getElementById(containerId);
    }
};
```

**改进点**:
- 替代 `switchView()` 的 `innerHTML = renderXxx()` 模式
- View 生命周期: `render()` → `mount()` → `destroy()`
- 切换视图时先 `destroy()` 旧视图（清理事件监听/定时器）
- 支持 `params` 传递（如项目路径）

### 7.4 View 模块规范

每个 View 模块遵循统一接口:

```javascript
const DashboardView = {
    name: "dashboard",

    async render(params) {
        const el = document.createElement("div");
        el.className = "dashboard-view";
        el.innerHTML = this._buildHTML();
        return el;
    },

    mount(params) {
        this._bindEvents();
        this._loadData();
    },

    destroy() {
        this._unbindEvents();
    },

    _buildHTML() { ... },
    _bindEvents() { ... },
    _unbindEvents() { ... },
    _loadData() { ... },
};
```

### 7.5 CSS设计令牌体系

**重构 `css/variables.css`**: 补全所有缺失变量，建立完整设计令牌。

```css
:root {
    /* ─── 颜色体系 ─── */
    --bg-primary: #1e1e2e;
    --bg-secondary: #2a2a3e;
    --bg-tertiary: #353550;
    --bg-hover: #3d3d5c;
    --bg-active: #4a4a6a;
    --bg-status: #2a2a3e;
    --bg-titlebar: #181825;
    --bg-statusbar: #181825;
    --bg-card: #2a2a3e;
    --bg-input: #1e1e2e;

    --text-primary: #cdd6f4;
    --text-secondary: #a6adc8;
    --text-muted: #6c7086;
    --text-inverse: #1e1e2e;

    --accent: #89b4fa;
    --accent-hover: #74c7ec;
    --primary: #89b4fa;
    --primary-light: rgba(137, 180, 250, 0.15);
    --primary-rgb: 137, 180, 250;

    --success: #a6e3a1;
    --warning: #f9e2af;
    --error: #f38ba8;
    --info: #89dceb;

    --border-primary: #45475a;
    --border-secondary: #313244;
    --border-focus: #89b4fa;

    /* ─── 字体体系 ─── */
    --font-sans: "Microsoft YaHei UI", "Segoe UI", sans-serif;
    --font-mono: "Cascadia Code", "Consolas", monospace;
    --font-family: var(--font-sans);

    /* ─── 间距体系 ─── */
    --space-xs: 4px;
    --space-sm: 8px;
    --space-md: 12px;
    --space-lg: 16px;
    --space-xl: 24px;
    --space-2xl: 32px;

    /* ─── 圆角 ─── */
    --radius-sm: 4px;
    --radius-md: 6px;
    --radius-lg: 8px;

    /* ─── 阴影 ─── */
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
    --shadow-md: 0 2px 8px rgba(0, 0, 0, 0.4);
    --shadow-lg: 0 4px 16px rgba(0, 0, 0, 0.5);

    /* ─── 布局 ─── */
    --sidebar-width: 260px;
    --titlebar-height: 36px;
    --statusbar-height: 28px;
}
```

**CSS文件职责划分**:

| 文件 | 职责 | 依赖 |
|------|------|------|
| `variables.css` | 设计令牌（颜色/字体/间距/圆角/阴影/布局） | 无 |
| `reset.css` | CSS重置 + 基础元素样式 | variables.css |
| `layout.css` | 管理器三区布局（左面板/右内容/状态栏） | variables.css |
| `components.css` | 通用组件（按钮/卡片/表单/Toast/对话框/标签页） | variables.css |
| `dashboard.css` | 项目总览卡片网格 | components.css |
| `project-detail.css` | 项目详情（目录树/文档列表/结果面板） | components.css |
| `change-center.css` | 变更列表/统计 | components.css |
| `change-wizard.css` | 变更单向导表单 | components.css |
| `settings.css` | 设置页面 | components.css |

**关键规则**:
- `index.html` 零内联CSS，所有样式通过外部文件
- 组件样式使用 BEM 命名: `.card`/`.card__title`/`.card--highlight`
- 禁止 `!important`
- 变量引用必须存在（lint规则校验）

### 7.6 对话框组件（替代 alert/prompt）

**新增 `js/components/dialog.js`**:

```javascript
const Dialog = {
    async confirm(title, message) {
        return new Promise((resolve) => {
            const el = this._createDialog(title, message, [
                {text: "取消", value: false, class: "btn-secondary"},
                {text: "确认", value: true, class: "btn-primary"},
            ]);
            el.addEventListener("dialog:close", (e) => resolve(e.detail));
            document.body.appendChild(el);
        });
    },

    async prompt(title, message, defaultValue = "") {
        return new Promise((resolve) => {
            const input = `<input type="text" class="dialog-input" value="${this._esc(defaultValue)}">`;
            const el = this._createDialog(title, message + input, [
                {text: "取消", value: null, class: "btn-secondary"},
                {text: "确定", value: "input", class: "btn-primary"},
            ]);
            el.addEventListener("dialog:close", (e) => {
                resolve(e.detail === null ? null : el.querySelector(".dialog-input").value);
            });
            document.body.appendChild(el);
        });
    },

    alert(title, message) {
        return new Promise((resolve) => {
            const el = this._createDialog(title, message, [
                {text: "知道了", value: true, class: "btn-primary"},
            ]);
            el.addEventListener("dialog:close", () => resolve(true));
            document.body.appendChild(el);
        });
    },
};
```

---

## 8. 数据模型设计

### 8.1 模型统一方案

**V8.0.0 实际状态**：当前代码库包含14个模型文件（含 `__init__.py`），13个业务模型。

| # | 模型文件 | 用途 | 状态 |
|---|----------|------|------|
| 1 | `project.py` | 项目元数据 | ✅活跃 |
| 2 | `change_request.py` | 变更单V1模型 | ⚠️@deprecated |
| 3 | `change_request_v2.py` | 变更单V2模型 | ✅活跃 |
| 4 | `document.py` | 文档模型 | ✅活跃 |
| 5 | `template.py` | 模板模型 | ✅活跃 |
| 6 | `diagnostic_report.py` | 诊断报告 | ✅活跃 |
| 7 | `check_result.py` | 检查结果 | ✅活跃 |
| 8 | `health_metrics.py` | 健康指标 | ✅活跃 |
| 9 | `test_case.py` | 测试用例 | ✅活跃 |
| 10 | `test_result.py` | 测试结果 | ✅活跃 |
| 11 | `variable.py` | 变量模型 | ✅活跃 |
| 12 | `project_artifact.py` | 项目制品 | ✅活跃 |
| 13 | `workflow_checkpoint.py` | 工作流检查点 | ✅活跃 |
| 14 | `__init__.py` | 模块导出 | — |

**问题**: `change_request.py` (V1) 和 `change_request_v2.py` (V2) 并存，V2 中有60行备用枚举

**方案**:
1. V2 模型直接 `from src.core.constants import ChangeDomain, ChangeNature, ...`
2. 删除 `change_request_v2.py` 中的 `except ImportError` 备用块
3. V1 `change_request.py` 标记 `@deprecated`，保留6个月后删除
4. 考虑迁移到 Pydantic V2（V7.1迭代），获得自动校验+序列化

### 8.2 新增数据模型

```python
@dataclass
class ProjectCard:
    """项目卡片 - Dashboard展示用"""
    name: str
    path: str
    project_type: ProjectType
    business_line: BusinessLine
    status: ProjectStatus
    health_score: int
    doc_coverage: float
    spec_compliance: float
    last_modified: str
    change_count: int
    naming_conflicts: int

@dataclass
class WorkspaceOverview:
    """工作空间总览"""
    workspace_path: str
    workspace_name: str
    total_projects: int
    avg_health_score: float
    avg_doc_coverage: float
    avg_spec_compliance: float
    pending_changes: int
    naming_conflicts: int
    projects: list[ProjectCard]

@dataclass
class CacheEntry:
    """缓存条目"""
    data: Any
    created_at: float
    ttl: int

    def is_expired(self) -> bool:
        return time.time() - self.created_at > self.ttl
```

---

## 9. 迁移策略

### 9.1 分阶段迁移计划

| Phase | 范围 | 风险 | 回归验证 |
|-------|------|------|----------|
| **Phase 0** | Core层修复: exceptions.py + constants.py枚举元数据 + event_bus.py异常日志 + config.py线程安全 | 低 | R1-R7 |
| **Phase 1** | Repository层 + Service接口边界修复 | 中 | R1-R7 |
| **Phase 2** | IPC层重构: APIGateway + MockData分离 + API精简 | 中 | R2, R6 |
| **Phase 3** | 前端重构: Store + Router + CSS体系 + 删除死代码 | 高 | R2, R6 |
| **Phase 4** | 前端View模块化 + 对话框组件 | 中 | R2, R6 |

### 9.2 向后兼容策略

- IPCBridge 旧API保留3个月，内部转发到APIGateway
- 旧API调用时输出 `DeprecationWarning` 日志
- 前端迁移期间，旧JS文件和新JS文件共存，通过 `index.html` 的 `<script>` 加载顺序控制

### 9.3 文件变更清单

**新增文件** (6个):
| 文件 | 说明 |
|------|------|
| `src/core/exceptions.py` | 项目级异常层次结构 |
| `src/core/repository.py` | 数据访问层（缓存/索引/查询） |
| `src/ui/api_gateway.py` | API网关（请求路由/参数校验/响应标准化） |
| `src/ui/mock_data.py` | Mock数据提供者（从IPCBridge分离） |
| `ui_prototype/js/store.js` | 集中状态管理 |
| `ui_prototype/js/router.js` | 视图路由 |

**重构文件** (8个):
| 文件 | 变更 |
|------|------|
| `src/core/constants.py` | 枚举添加description/icon属性，删除分离映射表 |
| `src/core/event_bus.py` | 异常日志，事件命名空间 |
| `src/core/config.py` | 线程安全锁 |
| `src/ui/webview_window.py` | 拆分出api_gateway + mock_data，精简API |
| `src/services/workspace_dashboard_service.py` | 通过Repository/公开接口访问，消除私有方法调用 |
| `src/models/change_request_v2.py` | 删除备用枚举，直接import constants |
| `src/services/change_template_renderer.py` | 使用枚举元数据，删除重复映射 |
| `ui_prototype/index.html` | 零内联CSS，新模块加载 |

**删除文件** (12个):
| 文件 | 原因 |
|------|------|
| `ui_prototype/js/layout.js` | IDE布局死代码 |
| `ui_prototype/js/handlers.js` | 功能合并到View |
| `ui_prototype/js/navigation.js` | 功能合并到Router |
| `ui_prototype/js/sidebar-templates.js` | 功能合并到Sidebar组件 |
| `ui_prototype/js/checkers.js` | 功能合并到Dashboard |
| `ui_prototype/js/utils.js` | 功能合并到Store |
| `ui_prototype/css/activity-bar.css` | IDE残留 |
| `ui_prototype/css/bottom-panel.css` | IDE残留 |
| `ui_prototype/css/content-area.css` | IDE残留 |
| `ui_prototype/css/placeholder.css` | 未使用 |
| `ui_prototype/css/responsive.css` | 未使用 |
| `ui_prototype/css/sidebar.css` | 类名体系未使用 |

---

## 10. 质量保障

### 10.1 测试策略

| 层 | 测试类型 | 覆盖目标 | 工具 |
|----|----------|----------|------|
| Core | 单元测试 | exceptions/constants/event_bus/config/repository | pytest |
| Service | 单元测试 | 公开接口/异常路径/缓存行为 | pytest + tmp_path |
| IPC | 集成测试 | APIGateway路由/参数校验/响应格式 | pytest + mock |
| 前端 | 手工验证 | View渲染/交互/IPC通信 | 启动验证 |

### 10.2 新增测试文件

| 文件 | 覆盖模块 |
|------|----------|
| `tests/test_exceptions.py` | 异常层次结构 |
| `tests/test_repository.py` | 缓存/索引/文件操作 |
| `tests/test_api_gateway.py` | API路由/参数校验/Mock切换 |

### 10.3 代码规范合规

- 所有Python文件通过 `ruff check` (210规范)
- 类型注解覆盖率 > 90%
- `except Exception: pass` 数量 = 0
- 前端零 `alert()`/`prompt()`/`console.log` 调试输出
