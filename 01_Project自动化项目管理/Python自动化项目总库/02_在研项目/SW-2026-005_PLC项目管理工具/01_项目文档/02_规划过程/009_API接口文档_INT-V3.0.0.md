# API接口文档 INT-V3.0.0

> **项目**: SW-2026-005 PLC项目管理工具
> **版本**: V3.0.0 | **日期**: 2026-05-23
> **变更**: 基于深度审查，全面对齐实际代码接口，修正V2.0.0中22处不匹配

---

## 文档约定

- `@classmethod` 标记表示类方法，无需实例化即可调用
- `实例方法` 标记表示需要先创建实例
- 返回值格式 `(T, Optional[str])` 中第二个元素为错误信息
- 信号格式 `pyqtSignal(类型)` 表示Qt信号

---

## 1. 核心层 API (`src/core/`)

### 1.1 SettingsManager

**模块**: `src.core.settings.SettingsManager`
**类型**: 类方法服务（全 `@classmethod`）
**用途**: 应用级配置的读写、最近项目管理、路径规范化

#### 1.1.1 初始化

```python
from src.core.settings import SettingsManager

SettingsManager.initialize(settings_dir=None)
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| settings_dir | Optional[Path] | None | 自定义设置目录，默认使用ConfigLoader.get_data_dir() |

**说明**: 必须在首次使用前调用。加载 `data/settings.json`，不存在则使用默认值。

#### 1.1.2 配置读写

```python
value = SettingsManager.get("theme", "light")
SettingsManager.set("theme", "material_dark")
SettingsManager.save()
all_settings = SettingsManager.get_all()
SettingsManager.reset_to_defaults()
```

| 方法 | 签名 | 返回值 | 说明 |
|------|------|--------|------|
| get | `get(key: str, default: Any = None) -> Any` | 配置值 | 读取配置项，default优先使用DEFAULTS中的值 |
| set | `set(key: str, value: Any) -> None` | — | 写入配置（仅内存） |
| save | `save() -> None` | — | 持久化到settings.json |
| get_all | `get_all() -> Dict[str, Any]` | 合并后的完整配置 | 合并DEFAULTS和用户设置 |
| reset_to_defaults | `reset_to_defaults() -> None` | — | 重置所有设置为默认值并保存 |

#### 1.1.3 默认配置项

| 键名 | 默认值 | 说明 |
|------|--------|------|
| theme | "light" | 主题: "light" / "dark" |
| language | "zh-CN" | 语言 |
| recent_projects | [] | 最近项目列表 |
| max_recent_projects | 10 | 最近项目最大数量 |
| editor_font_family | "Consolas" | 编辑器字体 |
| editor_font_size | 12 | 编辑器字号 |
| editor_tab_width | 4 | 制表符宽度 |
| auto_backup | True | 自动备份 |
| auto_save_interval | 300 | 自动保存间隔(秒) |
| sidebar_width | 220 | 侧边栏宽度 |
| plc_default_brand | "Codesys" | 默认PLC品牌 |
| hmi_default_brand | "Weinview" | 默认HMI品牌 |

#### 1.1.4 最近项目管理

```python
SettingsManager.add_recent_project(
    project_path="D:/Projects/DJ-2026-005",
    project_name="DJ-2026-005_边框缓存机"
)

projects = SettingsManager.get_recent_projects()
# 返回: [{"path": "D:/Projects/DJ-2026-005", "name": "..."}, ...]
```

| 方法 | 签名 | 返回值 | 说明 |
|------|------|--------|------|
| add_recent_project | `add_recent_project(project_path: str, project_name: str) -> None` | — | 添加最近项目，路径自动通过PathResolver规范化为相对路径存储，自动去重和截断 |
| get_recent_projects | `get_recent_projects() -> List[Dict[str, str]]` | 最近项目列表 | 路径已通过PathResolver解析为绝对路径 |

---

### 1.2 ConfigLoader

**模块**: `src.core.config.ConfigLoader`
**类型**: 类方法工具（全 `@classmethod`）
**用途**: 全局配置加载器，管理应用元信息和数据目录

```python
from src.core.config import ConfigLoader

ConfigLoader.load()

app_name = ConfigLoader.get("app_name", "PLC项目管理工具")
version = ConfigLoader.get("version", "1.0.0")
data_dir = ConfigLoader.get_data_dir()
```

| 方法 | 签名 | 返回值 | 说明 |
|------|------|--------|------|
| load | `load() -> None` | — | 从config.py加载全局配置，必须首次使用前调用 |
| get | `get(key: str, default: Any = None) -> Any` | 配置值 | 读取全局配置项 |
| set | `set(key: str, value: Any) -> None` | — | 修改运行时配置 |
| get_data_dir | `get_data_dir() -> Path` | 数据目录路径 | 获取data/目录的绝对路径 |

---

### 1.3 EventBus

**模块**: `src.core.event_bus.EventBus`
**类型**: 单例QObject
**用途**: 跨组件松耦合通信，基于Qt Signal/Slot机制

#### 1.3.1 获取实例

```python
from src.core.event_bus import EventBus

bus = EventBus.get_instance()
```

#### 1.3.2 信号清单

| 信号 | 类型 | 发射方 | 连接方 | 状态 |
|------|------|--------|--------|------|
| `project_selected(str)` | 项目选中 | — | — | ⚠️ 未使用 |
| `project_created(str)` | 项目创建 | MenuManager | MainWindow._on_project_created | ✅ 正常 |
| `project_opened(str)` | 项目打开 | MenuManager, ToolBarManager | MainWindow._on_project_opened | ✅ 正常 |
| `document_open_request(str)` | 文档打开请求 | — | MainWindow._on_document_open | ⚠️ 空处理 |
| `document_saved(str)` | 文档保存 | — | — | ⚠️ 未使用 |
| `document_created(str)` | 文档创建 | — | — | ⚠️ 未使用 |
| `st_file_open_request(str)` | ST文件打开 | — | — | ⚠️ 未使用 |
| `variable_check_request()` | 变量检查 | MenuManager | — | ⚠️ 断路 |
| `fb_doc_generate_request(str)` | FB文档生成 | — | — | ⚠️ 未使用 |
| `spec_check_request(dict)` | 规范检查 | ToolBarManager | — | ⚠️ 断路 |
| `theme_changed(str)` | 主题切换 | MenuManager | MainWindow._on_theme_changed | ✅ 正常 |
| `settings_changed()` | 设置变更 | MenuManager | MainWindow._on_settings_changed | ✅ 正常 |

#### 1.3.3 订阅示例

```python
bus = EventBus.get_instance()

bus.project_created.connect(self._on_project_created)
bus.project_opened.connect(self._on_project_opened)
bus.theme_changed.connect(self._on_theme_changed)
bus.settings_changed.connect(self._on_settings_changed)
```

#### 1.3.4 发射示例

```python
bus.project_created.emit(project_path)
bus.project_opened.emit(project_path)
bus.theme_changed.emit("dark")
bus.settings_changed.emit()
```

#### 1.3.5 测试重置

```python
EventBus.reset_instance()
```

**警告**: 仅用于测试环境，生产环境不应调用。

---

## 2. 业务服务层 API (`src/services/`)

### 2.1 ProjectService

**模块**: `src.services.project_service.ProjectService`
**类型**: 类方法服务（全 `@classmethod`）
**用途**: 项目CRUD操作、模板应用、项目导入

#### 2.1.1 创建项目

```python
from src.services.project_service import ProjectService
from src.core.constants import BusinessLine

project, error = ProjectService.create_project(
    name="DJ-2026-006_贴标机",
    business_line=BusinessLine.DEVICE,
    template_id="M001",
    manager="张三",
    description="全自动贴标生产线"
)

if project:
    print(f"项目创建成功: {project.path}")
else:
    print(f"创建失败: {error}")
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| name | str | 必填 | 项目名称 |
| business_line | BusinessLine | 必填 | 业务线类型 |
| template_id | str | 必填 | 模板ID ("M001" / "S001") |
| manager | str | "" | 负责人 |
| description | str | "" | 项目描述 |
| plc_brand | PLCBrand | None | PLC品牌 |
| hmi_brand | HMIBrand | None | HMI品牌 |
| custom_path | str | None | 自定义项目路径 |

**返回**: `Tuple[Optional[Project], Optional[str]]` — (项目实例, 错误信息)

#### 2.1.2 向导创建项目

```python
path, error = ProjectService.create_new_project({
    "project_name": "贴标机",
    "business_line": "DJ",
    "template_id": "M001",
    "manager": "张三",
    "parent_dir": "D:/Projects",
    "description": "全自动贴标生产线",
    "plc_brand": "Siemens",
    "hmi_brand": "Weinview",
    "io_scale": "medium",
})
```

**说明**: 8步完整流程 — 验证→构建路径→模板初始化→模板加载→目录创建→文档占位→元数据生成→缓存注册

**返回**: `Tuple[Optional[Path], Optional[str]]` — (项目路径, 错误信息)

#### 2.1.3 加载/查询项目

```python
project, error = ProjectService.load_project_from_path("D:/Projects/DJ-2026-005")
project = ProjectService.get_project("DJ-2026-005")
all_projects = ProjectService.get_all_projects()
projects = ProjectService.scan_projects_directory("D:/Projects")
```

| 方法 | 签名 | 返回值 | 说明 |
|------|------|--------|------|
| load_project_from_path | `load_project_from_path(project_path: str) -> Tuple[Optional[Project], Optional[str]]` | (项目, 错误) | 从路径加载项目，自动识别DJ单机项目类型 |
| get_project | `get_project(project_id: str) -> Optional[Project]` | 项目实例 | 从内存缓存获取项目 |
| get_all_projects | `get_all_projects() -> List[Project]` | 项目列表 | 获取所有已加载项目 |
| scan_projects_directory | `scan_projects_directory(directory: str = None) -> List[Project]` | 项目列表 | 扫描目录下所有项目 |
| delete_project | `delete_project(project_id: str) -> Tuple[bool, Optional[str]]` | (成功, 错误) | 从缓存中删除项目（不删除文件） |
| import_dj_project | `import_dj_project(project_path: str) -> Tuple[Optional[Project], Optional[str]]` | (项目, 错误) | 导入现有DJ单机项目 |

---

### 2.2 DocumentService

**模块**: `src.services.document_service.DocumentService`
**类型**: 类方法服务（全 `@classmethod`）
**用途**: 标准文档创建、读取、保存、列表

#### 2.2.1 创建文档

```python
from src.services.document_service import DocumentService
from src.core.constants import DocumentType

doc_path, error = DocumentService.create_document(
    project_path="D:/Projects/DJ-2026-005",
    doc_type=DocumentType.REQ,
    doc_name="REQ-DJ-2026-006-V1.0.0",
    version="V1.0.0",
    author="张三"
)
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| project_path | str | 必填 | 项目根目录 |
| doc_type | DocumentType | 必填 | 文档类型枚举 |
| doc_name | str | None | 文档名称，为空时自动生成 |
| version | str | "V1.0.0" | 版本号 |
| author | str | "" | 作者 |
| content | str | None | 自定义内容，为空时使用模板 |

**返回**: `Tuple[Optional[str], Optional[str]]` — (文件路径, 错误信息)

#### 2.2.2 创建或更新文档

```python
doc_path, error = DocumentService.create_or_update_document(
    project_path="D:/Projects/DJ-2026-005",
    doc_type=DocumentType.IFC,
    doc_name="IFC-DJ-2026-006-V1.0.0",
    version="V1.0.0",
    author="张三"
)
```

**说明**: 优先查找同类型权威文档进行更新，不存在则创建新文档。

#### 2.2.3 查询/读取/保存文档

```python
existing = DocumentService.find_authoritative_document(
    project_path, DocumentType.REQ
)

content, error = DocumentService.read_document(file_path)

success, error = DocumentService.save_document(file_path, content)

docs = DocumentService.list_documents(project_path)
```

| 方法 | 签名 | 返回值 | 说明 |
|------|------|--------|------|
| find_authoritative_document | `find_authoritative_document(project_path: str, doc_type: DocumentType) -> Optional[str]` | 文件路径或None | 查找同类型权威文档，避免重复创建 |
| read_document | `read_document(file_path: str) -> Tuple[Optional[str], Optional[str]]` | (内容, 错误) | 读取文档内容 |
| save_document | `save_document(file_path: str, content: str) -> Tuple[bool, Optional[str]]` | (成功, 错误) | 保存文档内容 |
| list_documents | `list_documents(project_path: str) -> List[Dict]` | 文档信息列表 | 列出项目下所有Markdown文档 |

#### 2.2.4 支持的文档类型

| 枚举值 | 中文名 | 模板可用 |
|--------|--------|---------|
| DocumentType.REQ | 需求规格说明书 | ✅ |
| DocumentType.DSN | 详细设计文档 | ✅ |
| DocumentType.IFC | 接口文档 | ✅ |
| DocumentType.UM | 用户操作手册 | ✅ |
| DocumentType.CHG | 变更记录 | ✅ |
| DocumentType.ALM | 报警码定义 | ✅ |
| DocumentType.VAR | 变量清单 | ✅ |
| DocumentType.IO | IO分配表 | ✅ |
| DocumentType.ARC | 架构设计文档 | ✅ |
| DocumentType.TEST | 测试报告 | ✅ |
| DocumentType.SUM | 项目总结 | ✅ |

---

### 2.3 ChangeService

**模块**: `src.services.change_service.ChangeService`
**类型**: 类方法服务（全 `@classmethod`）
**用途**: 变更单扫描、创建、状态流转、审核

#### 2.3.1 列出变更单

```python
from src.services.change_service import ChangeService

requests = ChangeService.list_change_requests("D:/Projects/DJ-2026-005")
for req in requests:
    print(f"{req.change_id}: {req.title} [{req.status}]")
```

**返回**: `List[ChangeRequest]` — 按change_id排序的变更单列表

#### 2.3.2 创建变更单

```python
from src.core.constants import ChangeCategory

request, error = ChangeService.create_change_request(
    project_path="D:/Projects/DJ-2026-005",
    category=ChangeCategory.PLC,
    title="修改取放料机构逻辑",
    description="增加安全互锁条件"
)
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| project_path | str | 必填 | 项目根目录 |
| category | ChangeCategory | 必填 | 变更分类(DOCU/PLC/HMI/ELEC/SAFE/MECH/SCPT) |
| title | str | 必填 | 变更标题 |
| description | str | "" | 变更描述 |

**返回**: `Tuple[Optional[ChangeRequest], Optional[str]]`

**编号规则**: `CHG-{类别}-2026-{3位序号}`，序号自动递增

#### 2.3.3 状态流转

```python
from src.core.constants import ChangeStatus

success = ChangeService.update_status(
    project_path="D:/Projects/DJ-2026-005",
    change_id="CHG-PLC-2026-001",
    new_status=ChangeStatus.IN_PROGRESS
)
```

**状态机转换规则**:

```
DRAFT ──→ REVIEW ──→ APPROVED ──→ IN_PROGRESS ──→ IMPLEMENTED ──→ VERIFYING ──→ COMPLETED
  │          │          │              │                               │
  └→CANCELLED └→DRAFT   └→ANALYZING    └→CANCELLED                     └→IN_PROGRESS
                        └→CANCELLED
                        └→IN_PROGRESS
```

| 当前状态 | 允许转换到 |
|---------|-----------|
| DRAFT | REVIEW, CANCELLED |
| REVIEW | APPROVED, DRAFT, CANCELLED |
| APPROVED | ANALYZING, IN_PROGRESS, CANCELLED |
| ANALYZING | IN_PROGRESS, CANCELLED |
| IN_PROGRESS | IMPLEMENTED, CANCELLED |
| IMPLEMENTED | VERIFYING |
| VERIFYING | COMPLETED, IN_PROGRESS |
| COMPLETED | (终态) |
| CANCELLED | (终态) |

#### 2.3.4 审核通过

```python
success = ChangeService.approve_change_request(
    project_path="D:/Projects/DJ-2026-005",
    change_id="CHG-PLC-2026-001",
    approver="张三"
)
```

**说明**: 仅当当前状态为REVIEW时可以审核通过。审核后在Markdown文件末尾追加审核人、审核时间、审核结果。

**返回**: `bool` — True=审核成功

---

### 2.4 DiagnosticService

**模块**: `src.services.diagnostic_service.DiagnosticService`
**类型**: 实例方法服务（需实例化）
**用途**: 编排规范检查→LSP诊断→健康度分析的完整诊断流程

#### 2.4.1 初始化与执行

```python
from src.services.diagnostic_service import DiagnosticService

service = DiagnosticService(config=None)
report, metrics = service.run_full_diagnostic("D:/Projects/DJ-2026-005")
```

| 方法 | 签名 | 返回值 | 说明 |
|------|------|--------|------|
| __init__ | `__init__(config: Optional[Dict] = None)` | — | 初始化，可传入自定义配置 |
| run_full_diagnostic | `run_full_diagnostic(project_path: str) -> Tuple[Any, Any]` | (DiagnosticReport, HealthMetrics) | 执行完整诊断（规范检查→LSP诊断→健康度分析），单步失败不中断整体 |
| get_last_diagnostics | `get_last_diagnostics() -> Tuple[Optional[Any], Optional[Any]]` | 最近一次诊断结果 | 获取缓存结果 |
| get_timing_statistics | `get_timing_statistics() -> Dict[str, float]` | 各步骤耗时 | 获取性能计时统计 |
| is_healthy | `is_healthy() -> bool` | 健康状态 | 综合评分>=70且等级A/B |
| reset | `reset() -> None` | — | 重置服务状态和缓存 |

**诊断流程**:
1. `_run_spec_check(project_path)` — 规范检查（延迟导入SpecCheckerService）
2. `_run_lsp_diagnostic(project_path)` — LSP兼容性诊断（延迟导入LSPCompatibilityChecker）
3. `_run_health_analysis(project_path, check_report)` — 健康度分析（延迟导入ProjectHealthAnalyzer）

---

### 2.5 SpecCheckerService

**模块**: `src.services.spec_checker_service.SpecCheckerService`
**类型**: 实例方法服务（需实例化，含缓存和状态）
**用途**: ST源码规范检查，支持并行检查和智能缓存

#### 2.5.1 初始化与检查

```python
from src.services.spec_checker_service import SpecCheckerService

service = SpecCheckerService(config=None)

report = service.check_project("D:/Projects/DJ-2026-005")
result = service.check_file("D:/Projects/DJ-2026-005/fb_valve.st")
```

| 方法 | 签名 | 返回值 | 说明 |
|------|------|--------|------|
| __init__ | `__init__(config: Optional[Dict] = None)` | — | 初始化，加载配置 |
| check_project | `check_project(project_path: str) -> CheckReport` | 检查报告 | 项目级批量检查（并行/串行） |
| check_file | `check_file(file_path: str) -> CheckResult` | 检查结果 | 单文件检查（含缓存） |
| get_enabled_checkers | `get_enabled_checkers() -> List[Any]` | 检查器列表 | 获取所有已启用的检查器实例 |
| load_project_rules | `load_project_rules(project_path: str) -> bool` | 是否成功 | 加载项目级.rules.json规则覆盖 |
| clear_cache | `clear_cache() -> None` | — | 清空所有缓存 |
| get_statistics | `get_statistics() -> Dict[str, int]` | 统计信息 | 获取运行统计 |
| reset_statistics | `reset_statistics() -> None` | — | 重置统计计数器 |

#### 2.5.2 缓存机制

- **缓存键**: 文件路径 + 修改时间
- **TTL**: 默认300秒
- **容量**: 达到上限时LRU淘汰最旧1/4
- **并行**: ThreadPoolExecutor，默认4线程

#### 2.5.3 已注册检查器（6种）

| 规则ID | 检查器 | 说明 |
|--------|--------|------|
| NAM-001 | NamingChecker | 命名规范检查 |
| SYN-001 | SyntaxChecker | 语法结构检查 |
| COM-001 | CommentChecker | 注释完整性检查 |
| CFG-001 | ConfigChecker | 配置文件检查 |
| TMR-001 | TimerChecker | 定时器使用检查 |
| VAR-001 | VariableChecker | 变量声明检查 |

---

### 2.6 TemplateService

**模块**: `src.services.template_service.TemplateService`
**类型**: 类方法服务（全 `@classmethod`）
**用途**: 项目模板加载、查询、应用

```python
from src.services.template_service import TemplateService

TemplateService.initialize_builtin_templates()

template = TemplateService.get_template("TPL-SINGLE-PLC-M001")
all_templates = TemplateService.get_all_templates()
metadata = TemplateService.get_template_metadata()

TemplateService.apply_template(
    template_id="TPL-SINGLE-PLC-M001",
    target_path="D:/Projects/NewProject",
    variables={"PROJECT_NAME": "贴标机"}
)
```

| 方法 | 签名 | 返回值 | 说明 |
|------|------|--------|------|
| initialize_builtin_templates | `initialize_builtin_templates() -> None` | — | 从templates/project_structures/*.json加载内置模板 |
| get_template | `get_template(template_id: str) -> Optional[Dict]` | 模板定义 | 按ID获取模板，首次调用自动初始化 |
| get_all_templates | `get_all_templates() -> List[Dict]` | 模板列表 | 获取所有可用模板 |
| get_template_metadata | `get_template_metadata() -> List[Dict]` | 元数据列表 | 获取id/name/version/description等摘要 |
| apply_template | `apply_template(template_id: str, target_path: str, variables: Dict = None) -> tuple` | (成功, 错误) | 应用模板到目标路径，支持{{变量名}}替换 |

**内置模板**:

| ID | 名称 | 适用业务线 |
|----|------|-----------|
| TPL-SINGLE-PLC-M001 | 标准单机PLC项目(完整版) | DJ, ZD |
| TPL-SINGLE-PLC-S001 | 标准单机PLC项目(精简版) | DJ |
| TPL-DJ-SINGLE-MACHINE | DJ单机项目 | DJ |

---

### 2.7 ArtifactRegistryService

**模块**: `src.services.artifact_registry_service.ArtifactRegistryService`
**类型**: 类方法服务（全 `@classmethod`）
**用途**: 项目资产扫描、分类、汇总

```python
from src.services.artifact_registry_service import ArtifactRegistryService

project_type = ArtifactRegistryService.detect_project_type("D:/Projects/DJ-2026-005")
assets = ArtifactRegistryService.scan_project_assets("D:/Projects/DJ-2026-005")
summary = ArtifactRegistryService.summarize_assets(assets)
roots = ArtifactRegistryService.get_artifact_roots(assets)
```

| 方法 | 签名 | 返回值 | 说明 |
|------|------|--------|------|
| detect_project_type | `detect_project_type(project_path: str) -> ProjectType` | 项目类型 | 检查标记目录判断DJ单机/通用 |
| scan_project_assets | `scan_project_assets(project_path: str) -> List[ProjectArtifact]` | 资产列表 | 递归扫描，识别24种资产类型 |
| summarize_assets | `summarize_assets(assets: List[ProjectArtifact]) -> Dict[str, int]` | 类型→数量 | 按资产类型汇总数量 |
| get_artifact_roots | `get_artifact_roots(assets: List[ProjectArtifact]) -> List[Dict[str, str]]` | 根目录列表 | 提取核心根目录资产 |

**资产分类**: 目录按路径精确匹配（变更管理根/PLC根/HMI源等），文件按后缀和文件名关键词分类（.plc.json/.scl/.st/.db/.scltest/.md），Markdown文档按文件名关键词细分为12种子类型。

---

### 2.8 WorkflowService

**模块**: `src.services.workflow_service.WorkflowService`
**类型**: 类方法服务（全 `@classmethod`）
**用途**: 工作流检查点构建

```python
from src.services.workflow_service import WorkflowService

checkpoints = WorkflowService.build_checkpoints(artifact_summary)
for cp in checkpoints:
    print(f"{cp.stage}: {'通过' if cp.passed else '缺失'} {cp.missing_assets}")
```

| 方法 | 签名 | 返回值 | 说明 |
|------|------|--------|------|
| build_checkpoints | `build_checkpoints(artifact_summary: dict) -> List[WorkflowCheckpoint]` | 检查点列表 | 按7阶段模型检查资产完备性 |

**7阶段模型**: 启动(INITIATION) → 设计(DESIGN) → 开发(DEVELOPMENT) → 调试(COMMISSIONING) → 测试(TESTING) → 交付(DELIVERY) → 维护(MAINTENANCE)

---

### 2.9 SpecService（预留）

**模块**: `src.services.spec_service.SpecService`
**类型**: 预留接口，全部空实现

| 方法 | 签名 | 当前返回 | 说明 |
|------|------|---------|------|
| initialize_builtin_specs | `initialize_builtin_specs() -> None` | — | 预留 |
| check_document_spec | `check_document_spec(document_path: str, spec_rules: dict) -> dict` | `{"passed": True}` | 预留 |
| get_available_specs | `get_available_specs() -> list` | `[]` | 预留 |

---

### 2.10 VariableService（预留）

**模块**: `src.services.variable_service.VariableService`
**类型**: 预留接口，全部空实现

| 方法 | 签名 | 当前返回 | 说明 |
|------|------|---------|------|
| parse_st_variables | `parse_st_variables(st_source: str) -> list` | `[]` | 预留 |
| validate_naming | `validate_naming(variable_name: str, rules: dict = None) -> tuple` | `(True, [])` | 预留 |

---

## 3. 同步引擎层 API (`src/sync/`)

### 3.1 SyncEngine

**模块**: `src.sync.sync_engine.SyncEngine`
**类型**: 类方法服务（全 `@classmethod`）
**用途**: 变更管理同步编排，版本检查/CHG生成/IFC生成/回写

#### 3.1.1 版本一致性检查

```python
from src.sync.sync_engine import SyncEngine

report = SyncEngine.run_check("D:/Projects/DJ-2026-005")
print(f"滞后模块: {report.lagging_count}")
```

| 方法 | 签名 | 返回值 | 说明 |
|------|------|--------|------|
| run_check | `run_check(project_path: str) -> VersionGapReport` | 版本差距报告 | L0全自动版本一致性检查 |

#### 3.1.2 文档生成

```python
chg_dir = SyncEngine.run_generate_chg("D:/Projects/DJ-2026-005")
ifc_dir = SyncEngine.run_generate_ifc("D:/Projects/DJ-2026-005")
```

| 方法 | 签名 | 返回值 | 说明 |
|------|------|--------|------|
| run_generate_chg | `run_generate_chg(project_path: str, output_dir: str = None) -> str` | 输出目录路径 | 扫描.scl文件为每个FB生成CHG文档 |
| run_generate_ifc | `run_generate_ifc(project_path: str, output_dir: str = None) -> str` | 输出目录路径 | 扫描.db文件为每个DB生成IFC文档 |

#### 3.1.3 全量同步报告

```python
report_path = SyncEngine.run_full_report("D:/Projects/DJ-2026-005")
```

| 方法 | 签名 | 返回值 | 说明 |
|------|------|--------|------|
| run_full_report | `run_full_report(project_path: str, output_dir: str = None) -> str` | 报告文件路径 | L0+L1+L2全量同步报告（5段式Markdown） |

#### 3.1.4 回写到项目

```python
written = SyncEngine.writeback_to_project(
    source_path="D:/Projects/DJ-2026-005/07_CHG",
    project_path="D:/Projects/DJ-2026-005",
    doc_type="chg"
)
```

| 参数 | 类型 | 说明 |
|------|------|------|
| source_path | str | 生成文件所在目录路径 |
| project_path | str | 项目根目录路径 |
| doc_type | str | "chg" 或 "ifc" |

**返回**: `List[str]` — 回写后的文件路径列表

**回写目录映射**:
- `chg` → `00_项目管理/04_变更管理/01_变更单`
- `ifc` → `00_项目管理/03_接口文档`

**说明**: 已有文件自动备份为 `.md.bak`

#### 3.1.5 HTML报告格式化

```python
html = SyncEngine.format_version_report_html(report)
```

| 方法 | 签名 | 返回值 | 说明 |
|------|------|--------|------|
| format_version_report_html | `format_version_report_html(report: VersionGapReport) -> str` | HTML字符串 | 生成HTML格式的版本检查报告 |

---

## 4. Controller 层 API (`src/ui/controllers/`)

### 4.1 ProjectController

**模块**: `src.ui.controllers.project_controller.ProjectController`
**用途**: 项目创建/打开事件处理、项目信息面板更新

```python
from src.ui.controllers.project_controller import ProjectController

controller = ProjectController(main_window)
```

| 方法 | 签名 | 说明 |
|------|------|------|
| __init__ | `__init__(main_window)` | 持有主窗口引用 |
| on_project_created | `on_project_created(path: str) -> None` | 项目创建后刷新项目树 |
| on_project_opened | `on_project_opened(path: str) -> None` | 项目打开：验证路径、加载项目到树、更新状态栏 |
| update_project_info | `update_project_info(context: dict) -> None` | 更新右侧项目信息面板标签(name/id/type/stage/path/desc) |

**内部属性访问**:
- `_project_tree_widget` — 通过 `main_window.get_project_tree_widget()` 获取
- `_labels` — 通过 `main_window.get_project_info_labels()` 获取

---

### 4.2 SyncController

**模块**: `src.ui.controllers.sync_controller.SyncController`
**用途**: 版本检查/CHG/IFC异步生成、回写工作流

```python
from src.ui.controllers.sync_controller import SyncController

controller = SyncController(main_window)
```

| 方法 | 签名 | 说明 |
|------|------|------|
| __init__ | `__init__(main_window)` | 持有主窗口引用 |
| on_sync_version_check | `on_sync_version_check() -> None` | 异步执行版本一致性检查，显示进度对话框，完成后弹出HTML报告 |
| on_sync_generate_chg | `on_sync_generate_chg() -> None` | 异步生成CHG文档，完成后展示SyncResultDialog |
| on_sync_generate_ifc | `on_sync_generate_ifc() -> None` | 异步生成IFC文档，完成后展示SyncResultDialog |

**内部Worker线程**:

| Worker | 继承 | 信号 | 用途 |
|--------|------|------|------|
| _VersionCheckWorker | QThread | `finished(object)`, `error(str)` | 后台版本检查 |
| _GenerateDocWorker | QThread | `finished(str, str)`, `error(str, str)` | 后台CHG/IFC生成 |

**回写流程**: SyncResultDialog用户选择"回写到项目" → `_do_writeback()` → `SyncEngine.writeback_to_project()` → 刷新项目树

---

### 4.3 DashboardController

**模块**: `src.ui.controllers.dashboard_controller.DashboardController`
**用途**: 仪表盘快捷操作分发、统计数据刷新

```python
from src.ui.controllers.dashboard_controller import DashboardController

controller = DashboardController(main_window)
```

| 方法 | 签名 | 说明 |
|------|------|------|
| __init__ | `__init__(main_window)` | 持有主窗口引用 |
| on_dashboard_action | `on_dashboard_action(action_id: str) -> None` | 分发快捷操作(new_project/open_project/new_document/spec_check/variable_check/generate_report) |
| refresh_dashboard_data | `refresh_dashboard_data() -> None` | 刷新仪表盘统计(项目总数/活跃/已完成/已归档)和最近项目列表 |

**action_id映射**:

| action_id | 处理方式 |
|-----------|---------|
| new_project | MenuManager._on_new_project() |
| open_project | MenuManager._on_open_project() |
| new_document | NavigationController.navigate_to_tab(TAB_DOCUMENT) |
| spec_check | NavigationController.navigate_to_tab(TAB_SPEC_CHECK) |
| variable_check | NavigationController.navigate_to_tab(TAB_SPEC_CHECK) |
| generate_report | 状态栏提示"开发中" |

---

### 4.4 NavigationController

**模块**: `src.ui.controllers.navigation_controller.NavigationController`
**用途**: 左侧ToolBox与右侧TabWidget双向同步、侧边栏动作分发

```python
from src.ui.controllers.navigation_controller import NavigationController

controller = NavigationController(
    tool_box, tab_widget,
    menu_manager=menu_manager,
    sync_handler=on_sync_action,
    project_info_handler=project_ctrl.update_project_info
)
controller.connect()
```

| 方法 | 签名 | 说明 |
|------|------|------|
| __init__ | `__init__(tool_box: QToolBox, tab_widget: QTabWidget, menu_manager=None, sync_handler: callable = None, project_info_handler: callable = None)` | 初始化映射表 |
| connect | `connect() -> None` | 连接QToolBox和QTabWidget的currentChanged信号 |
| navigate_to_tab | `navigate_to_tab(tab_index: int) -> None` | 同步设置Tab和ToolBox当前索引（使用blockSignals防循环） |
| on_sidebar_action | `on_sidebar_action(action_text: str) -> None` | 分发侧边栏动作(open_settings/toggle_theme/show_about/version_check/generate_chg/generate_ifc) |
| on_project_tree_navigate | `on_project_tree_navigate(tab_index: int, context: dict = None) -> None` | 项目树导航，跳转Tab并可选传递上下文 |

**Tab索引常量**:

| 常量 | 值 | Tab页面 |
|------|-----|---------|
| TAB_DASHBOARD | 0 | 仪表盘 |
| TAB_PROJECT | 1 | 项目信息 |
| TAB_DOCUMENT | 2 | 文档编辑 |
| TAB_CHANGE_MGMT | 3 | 变更管理 |
| TAB_PLC_TOOLS | 4 | PLC工具 |
| TAB_SPEC_CHECK | 5 | 规范检查 |

**ToolBox→Tab映射**:

| ToolBox页面 | 索引 | 映射到Tab索引 |
|------------|------|-------------|
| 项目管理 | 0 | 0 (仪表盘) |
| 文档管理 | 1 | 2 (文档) |
| PLC工具 | 2 | 4 (PLC工具) |
| HMI工具 | 3 | 5 (规范检查) |
| 规范中心 | 4 | 5 (规范检查) |
| 系统设置 | 5 | 字符串动作分发 |

---

## 5. UI 组件 API (`src/ui/`)

### 5.1 MainWindow

**模块**: `src.ui.main_window.MainWindow`
**继承**: QMainWindow
**用途**: 薄壳架构主窗口，布局构建+资源清理

#### 5.1.1 公开方法

| 方法 | 签名 | 说明 |
|------|------|------|
| get_dashboard_page | `get_dashboard_page() -> DashboardPage` | 获取仪表盘页面引用 |
| get_menu_manager | `get_menu_manager() -> MenuManager` | 获取菜单管理器 |
| get_project_tree_widget | `get_project_tree_widget() -> ProjectTreeWidget` | 获取项目树控件 |
| get_project_info_labels | `get_project_info_labels() -> Dict` | 获取项目信息标签字典 |

#### 5.1.2 Tab索引常量

| 常量 | 值 |
|------|-----|
| TAB_DASHBOARD | 0 |
| TAB_PROJECT | 1 |
| TAB_DOCUMENT | 2 |
| TAB_CHANGE_MGMT | 3 |
| TAB_PLC_TOOLS | 4 |
| TAB_SPEC_CHECK | 5 |

#### 5.1.3 资源清理

```python
main_window._cleanup_resources()
```

遍历 DiagnosticPanel / SpecCheckPanel / SpecCheckTabPanel / ChangeManagementPanel 调用各自的 `cleanup()` 方法。

---

### 5.2 DashboardPage

**模块**: `src.ui.dashboard.DashboardPage`
**继承**: QWidget
**用途**: 仪表盘首页，项目概览与快捷操作

**自定义信号**:
- `action_triggered = pyqtSignal(str)` — 快捷操作触发(action_id)

| 方法 | 签名 | 说明 |
|------|------|------|
| update_health_metrics | `update_health_metrics(compliance, issues, libraries, structure, overall) -> None` | 更新5项健康度指标 |
| refresh_statistics | `refresh_statistics(total: int, active: int, completed: int, archived: int) -> None` | 刷新4张统计卡片 |
| refresh_recent_projects | `refresh_recent_projects(recent_projects: list) -> None` | 刷新最近项目列表 |

**统计卡片**: 项目总数 / 进行中 / 已完成 / 已归档

**快捷操作**: new_project / open_project / new_document / spec_check / variable_check / generate_report

---

### 5.3 ChangeManagementPanel

**模块**: `src.ui.widgets.change_management_panel.ChangeManagementPanel`
**继承**: QWidget
**用途**: 变更单列表/创建/审核/状态流转

**自定义信号**:
- `change_request_selected = pyqtSignal(str, str)` — (change_id, project_path)
- `status_changed = pyqtSignal()` — 状态变更通知

| 方法 | 签名 | 说明 |
|------|------|------|
| set_project_path | `set_project_path(project_path: str) -> None` | 设置项目路径并刷新列表 |
| refresh | `refresh() -> None` | 从ChangeService重新加载变更单列表 |
| cleanup | `cleanup() -> None` | 清理方法 |

**GUI布局**: 工具栏(新建+刷新) + QSplitter(表格5列 + 详情区 + 状态操作按钮组)

---

### 5.4 SpecCheckPanel

**模块**: `src.ui.widgets.spec_check_panel.SpecCheckPanel`
**继承**: QWidget
**用途**: 六维规范检查面板

**自定义信号**:
- `check_started = pyqtSignal()`
- `check_finished = pyqtSignal(object)` — CheckReport
- `source_jump_requested = pyqtSignal(str, int)` — (file_path, line_number)

| 方法 | 签名 | 说明 |
|------|------|------|
| start_check | `start_check(project_path: str, file_path: Optional[str] = None) -> None` | 启动后台检查线程 |
| on_check_finished | `on_check_finished(report: CheckReport) -> None` | 检查完成回调 |
| apply_filter | `apply_filter() -> None` | 应用过滤条件(搜索+严重级别+类别) |
| get_current_report | `get_current_report() -> Optional[CheckReport]` | 获取当前检查报告 |
| clear_all | `clear_all() -> None` | 清空所有数据和UI状态 |
| cleanup | `cleanup() -> None` | 停止CheckWorker线程 |

---

### 5.5 DiagnosticPanel

**模块**: `src.ui.widgets.diagnostic_panel.DiagnosticPanel`
**继承**: QWidget
**用途**: 七维度深度诊断面板

**自定义信号**:
- `diagnostic_started = pyqtSignal()`
- `diagnostic_finished = pyqtSignal(object)` — DiagnosticReport
- `health_analysis_finished = pyqtSignal(object)` — HealthMetrics
- `source_jump_requested = pyqtSignal(str, int)` — (file_path, line_number)

| 方法 | 签名 | 说明 |
|------|------|------|
| set_project_path | `set_project_path(project_path: str) -> None` | 设置项目路径 |
| set_check_report | `set_check_report(check_report: CheckReport) -> None` | 设置规范检查报告 |
| run_diagnostic | `run_diagnostic(diagnostic_type: str = 'full') -> None` | 异步运行诊断(后台线程) |
| run_lsp_diagnostic | `run_lsp_diagnostic(project_path: str = '') -> Optional[DiagnosticReport]` | 同步运行LSP诊断 |
| run_health_analysis | `run_health_analysis(project_path: str = '', check_report: Optional[CheckReport] = None) -> Optional[HealthMetrics]` | 同步运行健康度分析 |
| update_all_tabs | `update_all_tabs(report: DiagnosticReport) -> None` | 更新所有标签页数据 |
| update_health_dashboard | `update_health_dashboard(metrics: HealthMetrics) -> None` | 更新健康度仪表盘 |
| export_report | `export_report(format: str = 'markdown') -> None` | 导出报告(Markdown/JSON) |
| cleanup | `cleanup() -> None` | 停止Worker线程+动画定时器 |

**4个Tab页**: 问题列表 / 根因分析 / 健康度仪表盘(圆环图+柱状图+Top5+建议) / OB→FB调用链视图

---

### 5.6 DocumentEditor

**模块**: `src.ui.widgets.document_editor.DocumentEditor`
**继承**: QWidget
**用途**: Markdown文档编辑器（含预览）

| 方法 | 签名 | 说明 |
|------|------|------|
| open_file | `open_file(file_path: str) -> None` | 打开文件进行编辑 |
| save_file | `save_file() -> bool` | 保存当前文件(无路径时弹出另存为) |
| save_file_as | `save_file_as() -> bool` | 另存为 |
| get_content | `get_content() -> str` | 获取编辑器文本内容 |
| set_content | `set_content(text: str) -> None` | 设置编辑器文本内容 |
| is_modified | `is_modified -> bool` (property) | 检查是否有未保存修改 |

**工具栏**: B/I/H1/H2/列表/代码/引用/链接 + 预览切换

---

### 5.7 STEditor

**模块**: `src.ui.widgets.st_editor.STEditor`
**继承**: QWidget
**用途**: IEC 61131-3 ST/SCL代码编辑器

| 方法 | 签名 | 说明 |
|------|------|------|
| open_file | `open_file(file_path: str, line_number: int = None) -> None` | 打开文件并定位到行号 |
| get_text | `get_text() -> str` | 获取编辑器代码文本 |
| set_text | `set_text(code: str) -> None` | 设置编辑器代码文本 |
| has_full_features | `has_full_features -> bool` (property) | 检查是否具备QScintilla+ST语法高亮 |

**说明**: 优先使用QScintilla（行号/括号匹配/代码折叠/自动缩进/ST语法高亮），不可用时回退到QPlainTextEdit。

---

### 5.8 ProjectTreeWidget

**模块**: `src.ui.widgets.project_tree.ProjectTreeWidget`
**继承**: QWidget
**用途**: 项目目录树浏览器

**自定义信号**:
- `navigation_requested = pyqtSignal(int, dict)` — (tab_index, context)

| 方法 | 签名 | 说明 |
|------|------|------|
| load_project | `load_project(project) -> None` | 加载并显示项目目录结构 |
| current_project | `current_project -> object` (property) | 获取当前加载的项目对象 |

**右键菜单**: 新建文件夹/新建文档/重命名/删除/刷新/展开全部/折叠全部

---

### 5.9 Dialog 对话框

#### 5.9.1 NewProjectDialog

**模块**: `src.ui.dialogs.new_project_dialog.NewProjectDialog`
**继承**: QDialog
**用途**: 4步向导式新建项目对话框

| 方法 | 签名 | 说明 |
|------|------|------|
| get_project_data | `get_project_data() -> dict` | 获取完整项目数据 |
| get_created_project_path | `get_created_project_path() -> str` | 获取创建后的项目路径 |

**4步流程**: 选择目录 → 基本信息(编号/名称/设备类型/PLC/HMI/IO规模/负责人/描述) → 选择模板(M001/S001) → 确认创建

#### 5.9.2 NewDocumentDialog

**模块**: `src.ui.dialogs.new_document_dialog.NewDocumentDialog`
**继承**: QDialog
**用途**: 通用文档创建对话框

| 方法 | 签名 | 说明 |
|------|------|------|
| get_document_data | `get_document_data() -> dict` | 获取文档数据{doc_type, doc_name, version, author, remarks} |

#### 5.9.3 SettingsDialog

**模块**: `src.ui.dialogs.settings_dialog.SettingsDialog`
**继承**: QDialog
**用途**: 应用设置对话框

**2个Tab**: 常规设置(项目路径/自动保存/日志级别) + 编辑器设置(字体/字号/制表符宽度)

**保存6项设置**: default_project_root / auto_backup / log_level / editor_font_family / editor_font_size / editor_tab_width

#### 5.9.4 SyncResultDialog

**模块**: `src.ui.dialogs.sync_result_dialog.SyncResultDialog`
**继承**: QDialog
**用途**: CHG/IFC生成结果对话框

| 方法 | 签名 | 说明 |
|------|------|------|
| get_action | `get_action() -> str` | 获取用户操作选择 |
| get_file_path | `get_file_path() -> str` | 获取文件路径 |
| get_doc_type | `get_doc_type() -> str` | 获取文档类型 |

**操作选项**:
- `ACTION_OPEN_DIR = "open_dir"` — 打开所在目录
- `ACTION_WRITEBACK = "writeback"` — 回写到项目
- `ACTION_SAVE_ONLY = "save_only"` — 仅保存到输出目录

#### 5.9.5 FBDocumentDialog（预留）

**模块**: `src.ui.dialogs.fb_document_dialog.FBDocumentDialog`
**继承**: QDialog
**用途**: FB文档生成对话框（预留，仅占位标签+关闭按钮）

---

## 6. Builder 层 API (`src/ui/builders/`)

### 6.1 LeftPanelBuilder

**模块**: `src.ui.builders.left_panel_builder.LeftPanelBuilder`
**类型**: 静态工厂方法

```python
tool_box = LeftPanelBuilder.build(parent, action_handler)
```

| 参数 | 类型 | 说明 |
|------|------|------|
| parent | QMainWindow | 父窗口 |
| action_handler | callable | 动作回调，接收int(Tab索引)或str(动作文本) |

**返回**: `QToolBox` — 包含6个页面的工具箱

### 6.2 RightPanelBuilder

**模块**: `src.ui.builders.right_panel_builder.RightPanelBuilder`
**类型**: 静态工厂方法

```python
result = RightPanelBuilder.build(parent, jump_handler=None)
```

| 参数 | 类型 | 说明 |
|------|------|------|
| parent | QMainWindow | 父窗口 |
| jump_handler | callable | 源码跳转回调(file_path, line_number) |

**返回**: `dict` — 包含9个键:

| 键 | 类型 | 说明 |
|----|------|------|
| tab_widget | QTabWidget | 主Tab容器(6个Tab) |
| dashboard_page | DashboardPage | 仪表盘页面 |
| project_info_widget | QWidget | 项目信息页面 |
| document_editor | DocumentEditor | 文档编辑器 |
| change_mgmt_panel | ChangeManagementPanel | 变更管理面板 |
| plc_tools_tabs | QTabWidget | PLC工具子Tab容器 |
| st_editor | STEditor | ST编辑器实例 |
| spec_check_tab_panel | QWidget | 规范检查引导页 |
| project_info_labels | dict | 项目信息标签字典{name/id/type/stage/path/desc→QLabel/QTextEdit} |

### 6.3 DockPanelBuilder

**模块**: `src.ui.builders.dock_panel_builder.DockPanelBuilder`
**类型**: 静态工厂方法

```python
result = DockPanelBuilder.build(main_window)
```

**返回**: `dict` — 包含4个键:

| 键 | 类型 | 说明 |
|----|------|------|
| diagnostic_panel | DiagnosticPanel | 深度诊断面板组件 |
| diagnostic_dock | QDockWidget | 深度诊断Dock容器 |
| spec_check_panel | SpecCheckPanel | 规范检查面板组件 |
| spec_check_dock | QDockWidget | 规范检查Dock容器 |

**信号连接**: diagnostic_panel.source_jump_requested / spec_check_panel.source_jump_requested → main_window._jump_to_source

### 6.4 StyleBuilder

**模块**: `src.ui.builders.style_builder.StyleBuilder`
**类型**: 静态工具方法

```python
StyleBuilder.apply(widget, "light")
font = StyleBuilder._resolve_chinese_font(10)
default_qss = StyleBuilder.get_default_stylesheet()
```

| 方法 | 签名 | 说明 |
|------|------|------|
| apply | `apply(widget: QWidget, theme: str) -> None` | 应用主题样式(设置中文字体+加载QSS) |
| get_default_stylesheet | `get_default_stylesheet() -> str` | 返回内置默认QSS |
| _resolve_chinese_font | `_resolve_chinese_font(size: int = 10) -> QFont` | 按优先级查找系统中文字体 |

**QSS查找**: 从当前文件向上遍历5级父目录，查找 `resources/styles/material_{theme}.qss`

---

## 7. Manager 层 API (`src/ui/managers/`)

### 7.1 MenuManager

**模块**: `src.ui.managers.menu_manager.MenuManager`
**用途**: 菜单栏构建与事件处理

```python
from src.ui.managers.menu_manager import MenuManager

manager = MenuManager(main_window, event_bus)
menu_bar = manager.build()
```

**菜单结构**:

| 菜单 | 项 | 快捷键 | EventBus信号 |
|------|-----|--------|-------------|
| 文件 | 新建项目 | Ctrl+N | project_created |
| | 打开项目 | Ctrl+O | project_opened |
| | 最近打开(子菜单) | — | project_opened |
| | 保存 | Ctrl+S | — |
| | 设置 | Ctrl+, | settings_changed |
| | 退出 | Ctrl+Q | — |
| 编辑 | 撤销/重做 | Ctrl+Z/Y | (禁用) |
| | 查找/替换 | Ctrl+F/H | (开发中) |
| 工具 | 规范检查 | F5 | — |
| | 深度诊断 | F6 | — |
| | 运行测试 | F7 | (开发中) |
| | 变量检查 | — | variable_check_request |
| | 生成报告 | — | (开发中) |
| 视图 | 诊断面板切换 | Ctrl+D | — |
| | 主题(浅色/深色) | — | theme_changed |
| 帮助 | 关于 | — | — |

### 7.2 ToolBarManager

**模块**: `src.ui.managers.toolbar_manager.ToolBarManager`
**用途**: 主工具栏构建

```python
from src.ui.managers.toolbar_manager import ToolBarManager

manager = ToolBarManager(main_window, event_bus)
toolbar = manager.build()
```

**工具栏按钮**: 新建项目 / 打开项目 / 保存 / 规范检查

---

## 8. 工具层 API (`src/utils/`)

### 8.1 PathResolver

**模块**: `src.utils.path_resolver.PathResolver`
**用途**: 路径规范化与解析（策略模式）

```python
from src.utils.path_resolver import PathResolver, RelativePathStrategy, get_default_resolver

resolver = PathResolver(RelativePathStrategy())

relative = resolver.normalize(
    raw_path="D:/Projects/DJ-2026-005",
    base_path=Path("data/")
)

absolute = resolver.resolve(
    stored_path="../../../Projects/DJ-2026-005",
    base_path=Path("data/")
)

default_resolver = get_default_resolver()
```

### 8.2 Logger

**模块**: `src.utils.logger`
**用途**: 统一日志管理

```python
from src.utils.logger import setup_logger

logger = setup_logger(__name__)
logger.info("信息")
logger.warning("警告")
logger.error("错误")
```

### 8.3 FileUtils

**模块**: `src.utils.file_utils`
**用途**: 文件操作工具集

### 8.4 Validators

**模块**: `src.utils.validators`
**用途**: 输入验证工具集

---

## 9. 资源清理 API

### 9.1 清理链

```
MainWindow.closeEvent
  └── _cleanup_resources()
       ├── DiagnosticPanel.cleanup()
       │    ├── DiagnosticWorker: cancel → disconnect → wait(2s) → None
       │    └── ScoreRingWidget.cleanup(): _animation_timer.stop()
       ├── SpecCheckPanel.cleanup()
       │    └── CheckWorker: cancel → disconnect → wait → None
       ├── SpecCheckTabPanel.cleanup()
       └── ChangeManagementPanel.cleanup()
```

### 9.2 各组件cleanup方法

| 组件 | cleanup()行为 |
|------|-------------|
| DiagnosticPanel | 停止Worker线程 + 停止ScoreRingWidget动画定时器 |
| SpecCheckPanel | 停止CheckWorker线程 |
| ChangeManagementPanel | 当前为空实现（预留） |

---

## 10. 废弃 API 清单

| API | 原模块 | 删除原因 | 替代方案 |
|-----|--------|---------|---------|
| HMIService.* | hmi_service | 纯占位符 | — |
| PLCService.* | plc_service | 已废弃兼容层 | DiagnosticService |
| TestManagementService.* | test_management_service | 无UI接入点 | — |
| Application._run_cli() | core.app | 未实现 | — |
| Application.shutdown() | core.app | 未实现 | MainWindow.closeEvent |

---

## 11. V2.0.0 → V3.0.0 变更记录

| 章节 | 变更内容 |
|------|---------|
| 1.1 SettingsManager | `load(path)` → `initialize(settings_dir)`；新增 `reset_to_defaults()` / `get_all()`；新增默认配置项完整列表 |
| 1.3 EventBus | 删除虚构信号(project_closed/check_started/check_completed/diagnostic_started/diagnostic_completed/sync_*_requested)；新增实际信号(document_created/st_file_open_request/variable_check_request/fb_doc_generate_request/spec_check_request)；标注信号连接状态 |
| 2.1 ProjectService | `open_project()` → `load_project_from_path()`；删除 `close_project()`；新增 `create_new_project()` / `import_dj_project()` / `delete_project()` / `scan_projects_directory()` |
| 2.2 DocumentService | 删除 `get_template_types()` / `generate_document()`；新增 `create_document()` / `create_or_update_document()` / `find_authoritative_document()`；新增11种文档类型表 |
| 2.3 ChangeService | **新增章节** — 完整记录4个API方法+状态机转换规则 |
| 2.4 DiagnosticService | `run_diagnosis()` → `run_full_diagnostic()`；删除 `run_lsp_check()`；改为实例方法；新增 `is_healthy()` / `reset()` / `get_timing_statistics()` |
| 2.5 SpecCheckerService | `get_available_rules()` → `get_enabled_checkers()`；`run_checks()` → `check_project()` / `check_file()`；改为实例方法；新增缓存/统计API |
| 2.6 TemplateService | 新增完整API记录(5个方法) |
| 2.7 ArtifactRegistryService | **新增章节** — 完整记录4个API方法 |
| 2.8 WorkflowService | **新增章节** — 记录 `build_checkpoints()` |
| 2.9 SpecService | **新增章节** — 标注为预留空实现 |
| 2.10 VariableService | **新增章节** — 标注为预留空实现 |
| 3.1 SyncEngine | `run_version_check()` → `run_check()`；新增 `run_full_report()` / `run_generate_chg()` / `run_generate_ifc()` / `writeback_to_project()` / `format_version_report_html()` |
| 4.1 ProjectController | 删除虚构方法(create_project/open_project/save_project/load_project_to_tree)；记录实际3个方法 |
| 4.2 SyncController | `run_version_check(path)` → `on_sync_version_check()`；新增Worker线程说明 |
| 4.3 DashboardController | `update_stats()` → `refresh_dashboard_data()`；删除虚构方法；新增action_id映射表 |
| 4.4 NavigationController | **新增章节** — 完整记录4个方法+Tab索引常量+映射表 |
| 5.x UI组件 | 新增ChangeManagementPanel / SyncResultDialog / FBDocumentDialog完整API；修正DashboardPage统计项 |
| 6.x Builder层 | **新增章节** — 记录4个Builder的工厂方法和返回值结构 |
| 7.x Manager层 | **新增章节** — 记录MenuManager/ToolBarManager完整菜单/工具栏结构 |
| 9.x 资源清理 | 新增ChangeManagementPanel.cleanup()到清理链 |

---

*文档版本: INT-V3.0.0 | 最后更新: 2026-05-23*
*变更记录: 基于深度审查全面对齐实际代码接口，修正V2.0.0中22处不匹配*
