# API接口文档 INT-V4.0.0

> **项目**: SW-2026-005 PLC项目管理工具  
> **版本**: V4.0.0  
> **日期**: 2026-06-01  
> **状态**: 当前主线接口文档  
> **适用范围**: 工作空间支持接口 + IPCBridge前端接口

---

## 1. 文档约定

- 类方法统一标记为 `@classmethod`
- 返回值优先采用 `(T, Optional[str])`
- 若返回列表，失败时返回 `(None, error)`，成功时返回 `(list, None)`
- 本文档只记录本轮工作空间主线必须关注的接口
- 标记 `✅ 已实现` 表示接口已完成编码并可通过调用验证

---

## 2. `ArtifactRegistryService`

**模块**: `src.services.artifact_registry_service.ArtifactRegistryService`

### 2.1 `detect_project_type()` ✅ 已实现

```python
@classmethod
def detect_project_type(cls, project_path: str) -> ProjectType:
    ...
```

用途：
- 根据目录结构识别目录类型，返回 `ProjectType` 枚举

5级识别优先级（从高到低）：

| 优先级 | 条件 | 返回值 |
|--------|------|--------|
| 1 | 存在 `workspace.json` | `ProjectType.PLC_WORKSPACE` |
| 2 | 同时存在 DJ 三标记（`00_项目管理`/`02_PLC程序`/`03_HMI设计`） | `ProjectType.DJ_SINGLE_MACHINE` |
| 3 | 存在 `.plc.json` 且包含共享库分类子目录 | `ProjectType.PLC_LIBRARY` |
| 4 | ≥2 个可识别子项目 | `ProjectType.PLC_WORKSPACE` |
| 5 | 其他 | `ProjectType.GENERIC` |

实现说明：
- 目录不存在或非目录时直接返回 `ProjectType.GENERIC`
- 优先级3中的"共享库分类子目录"由 `PLC_LIBRARY_CATEGORY_DIRS` 常量定义
- 优先级4中的"可识别子项目"包括：DJ项目、共享库、含 `project.json`/`.plc_project.json`/`.plc.json` 的目录
- 扫描子目录时排除 `WORKSPACE_IGNORED_DIRS` 中的目录

### 2.2 `scan_workspace_subprojects()` ✅ 已实现

```python
@classmethod
def scan_workspace_subprojects(cls, workspace_path: str) -> List[Dict[str, str]]:
    ...
```

用途：
- 扫描工作空间根目录下的可识别子项目，返回结构化信息列表

输入：
- `workspace_path`: 工作空间根目录路径

输出：
- 目录不存在时返回 `[]`
- 成功时返回 `List[Dict[str, str]]`，每项包含：

| 字段 | 类型 | 说明 |
|------|------|------|
| `path` | `str` | 子项目绝对路径 |
| `name` | `str` | 子项目目录名 |
| `type` | `str` | 子项目类型，值为 `ProjectType` 枚举的 `.value` |

`type` 字段取值：

| type 值 | 含义 | 判定条件 |
|---------|------|----------|
| `"dj_single_machine"` | DJ单机项目 | DJ三标记齐全 |
| `"plc_library"` | PLC共享库 | `.plc.json` + 分类子目录 |
| `"generic"` | 普通项目 | 含 `project.json`/`.plc_project.json`/`.plc.json` |

实现说明：
- 只遍历一层子目录
- 排除 `WORKSPACE_IGNORED_DIRS` 中的目录
- 不可识别的子目录（不满足上述任一条件）不会出现在返回列表中
- 内部通过 `_classify_subproject()` 方法逐个分类

---

## 3. `ProjectService`

**模块**: `src.services.project_service.ProjectService`

### 3.1 `load_project_from_path()`

```python
@classmethod
def load_project_from_path(cls, project_path: str) -> Tuple[Optional[Project], Optional[str]]:
    ...
```

用途：
- 加载单个项目
- 若识别为 DJ 项目，可转入 `import_dj_project()`

### 3.2 `load_workspace_from_path()` ✅ 已实现

```python
@classmethod
def load_workspace_from_path(
    cls,
    workspace_path: str,
) -> Tuple[Optional[List[Project]], Optional[str]]:
    ...
```

用途：
- 从工作空间根目录加载所有可识别子项目

输入：
- `workspace_path`: 工作空间根目录

输出：
- 成功: `(projects, None)`
- 失败: `(None, error_message)`

实现说明：
- **只接受 `PLC_WORKSPACE` 类型目录**，其他类型直接返回 `(None, error)`
- 先调用 `ArtifactRegistryService.detect_project_type()` 验证类型
- 再调用 `ArtifactRegistryService.scan_workspace_subprojects()` 获取子项目列表
- 逐个调用 `_load_subproject()` 加载子项目
- 所有子项目加载失败时返回 `(None, "未在工作空间中发现任何可管理的子项目")`
- 部分子项目加载失败不中断，成功加载的子项目仍会返回

### 3.3 `_load_subproject()` ✅ 已实现

```python
@classmethod
def _load_subproject(cls, sub_path: str, sub_type: str) -> Optional[Project]:
    ...
```

用途：
- 加载单个子项目，根据类型分发到不同的加载策略

输入：
- `sub_path`: 子项目绝对路径
- `sub_type`: 子项目类型字符串（`"dj_single_machine"` / `"plc_library"` / `"generic"`）

输出：
- 成功时返回 `Project` 对象
- 失败时返回 `None`（降级构造也失败的情况）

加载策略：

| sub_type | 加载方式 | 失败降级 |
|----------|----------|----------|
| `"dj_single_machine"` | 调用 `import_dj_project()` | `_create_fallback_project()` |
| `"plc_library"` | 调用 `load_project_from_path()`，成功后覆写 `project_type = PLC_LIBRARY` | `_create_library_project()` |
| `"generic"` | 调用 `load_project_from_path()` | `_create_fallback_project()` |

实现说明：
- 所有成功加载的子项目均标记 `project.extra["_workspace_child"] = True`
- 共享库类型加载成功后会显式覆写 `project_type` 为 `PLC_LIBRARY`
- 异常不外抛，内部捕获后走降级路径

### 3.4 `_create_library_project()` ✅ 已实现

```python
@classmethod
def _create_library_project(cls, lib_path: str) -> Project:
    ...
```

用途：
- 为缺少标准元数据文件的共享库构造降级 `Project` 对象

输入：
- `lib_path`: 共享库目录路径

输出：
- 返回手工构造的 `Project` 对象

降级构造字段：

| 字段 | 值 |
|------|----|
| `name` | 目录名 |
| `code` | 目录名 |
| `description` | `"PLC共享库: {name}"` |
| `business_line` | `BusinessLine.LIBRARY` |
| `status` | `ProjectStatus.ACTIVE` |
| `path` | 输入路径 |
| `template_id` | `""` |
| `project_type` | `ProjectType.PLC_LIBRARY` |
| `workflow_stage` | `WorkflowStage.DEVELOPMENT` |
| `extra["_workspace_child"]` | `True` |

实现说明：
- 构造后自动加入 `ProjectService._projects` 缓存
- 与 `_create_fallback_project()` 的区别：使用 `BusinessLine.LIBRARY` 而非 `DEVICE`，`WorkflowStage.DEVELOPMENT` 而非 `INITIATION`

---

## 4. `ProjectController`

**模块**: `src.ui.controllers.project_controller.ProjectController`

### 4.1 `on_project_opened()`

```python
def on_project_opened(self, path: str):
    ...
```

用途：
- 作为"打开项目/目录"的统一入口

主线行为：
- 目录无效 -> 弹错误框
- 目录有单项目配置 -> 走单项目加载
- 目录无配置但识别为 DJ 项目 -> 走单项目导入
- 目录识别为 `PLC_WORKSPACE` -> 转入 `_open_as_workspace()`
- 其他情况 -> 保留当前错误提示

### 4.2 `_open_as_workspace()` ✅ 已实现

```python
def _open_as_workspace(self, workspace_path: str):
    ...
```

用途：
- 以工作空间模式打开目录

输入：
- `workspace_path`: 工作空间根目录路径

主线行为：
- 调用 `ProjectService.load_workspace_from_path()` 获取子项目列表
- 无子项目 -> 弹"打开工作空间失败"警告框
- 有子项目 -> 调用 `ProjectTreeWidget.load_workspace()` 加载到项目树
- 状态栏显示：`"已加载工作空间: {name} | 子项目: {count} 个"`
- 异常时弹"错误"严重框

---

## 5. `ProjectTreeWidget`

**模块**: `src.ui.widgets.project_tree.ProjectTreeWidget`

### 5.1 `load_workspace()` ✅ 已实现

```python
def load_workspace(self, workspace_path: str, projects: list):
    ...
```

用途：
- 加载工作空间并显示多个子项目，构建工作空间根节点和子项目节点树

输入：
- `workspace_path`: 工作空间根目录路径
- `projects`: 子项目 `Project` 对象列表

实现说明：
- 清空当前树，`_current_project` 置为 `None`
- 创建工作空间根节点，文本格式：`"🏢 工作空间: {name}"`，`UserRole` 数据标记 `type: "workspace"`
- 根节点默认展开
- 遍历 `projects` 列表，为每个子项目创建子节点：
  - DJ项目图标：`📁`，共享库图标：`📚`，通用项目图标：`📄`
  - 每个子节点根据 `project_type` 分发到对应的节点构建方法
- 状态栏显示：`"🏢 工作空间: {name} ({count} 个子项目)"`

### 5.2 `_build_library_nodes()` ✅ 已实现

```python
def _build_library_nodes(self, root_item: QTreeWidgetItem, project):
    ...
```

用途：
- 构建共享库项目节点，展示库描述和库资产

输入：
- `root_item`: 父级树节点
- `project`: 共享库 `Project` 对象

实现说明：
- 若 `project.description` 非空，创建描述节点（图标 `📝`，`type: "workflow"`）
- 创建"📂 库资产"子节点，默认展开
- 遍历 `project.artifact_roots`，为每个资产生成子节点，显示 `artifact_type: relative_path`
- 每个资产节点的 `UserRole` 数据存储完整的 `artifact` 字典

---

## 6. 新增常量与枚举

**模块**: `src.core.constants`

### 6.1 `WORKSPACE_IGNORED_DIRS` ✅ 已实现

```python
WORKSPACE_IGNORED_DIRS = {
    ".trae",
    ".git",
    "__pycache__",
    "_archive",
    "node_modules",
    ".venvs",
    ".plc-out",
}
```

用途：
- 工作空间扫描时需要排除的目录名集合
- 被 `ArtifactRegistryService.scan_workspace_subprojects()` 和 `_count_identifiable_subprojects()` 使用

### 6.2 `PLC_LIBRARY_CATEGORY_DIRS` ✅ 已实现

```python
PLC_LIBRARY_CATEGORY_DIRS = {
    "actuator",
    "timer",
    "counter",
    "edge",
    "convert",
    "analog",
    "motion",
    "communication",
    "safety",
}
```

用途：
- PLC共享库典型分类子目录名集合（小写）
- 被 `ArtifactRegistryService._is_plc_library()` 用于判定目录是否为共享库
- 判定逻辑：目录存在 `.plc.json` 且子目录名与该集合有交集

### 6.3 `BusinessLine.LIBRARY` ✅ 已实现

```python
class BusinessLine(Enum):
    ...
    LIBRARY = "LIB"       # 共享库
```

用途：
- 新增业务线枚举值，标识共享库项目
- 被 `ProjectService._create_library_project()` 使用
- 对应描述映射：`BusinessLine.LIBRARY: "共享库"`

### 6.4 `ProjectType.PLC_LIBRARY` / `ProjectType.PLC_WORKSPACE` ✅ 已实现

```python
class ProjectType(Enum):
    ...
    PLC_LIBRARY = "plc_library"
    PLC_WORKSPACE = "plc_workspace"
```

用途：
- `PLC_LIBRARY`：标识PLC共享库项目，由 `detect_project_type()` 优先级3返回
- `PLC_WORKSPACE`：标识PLC工作空间，由 `detect_project_type()` 优先级1/4返回
- 对应描述映射：
  - `PLC_LIBRARY: "PLC共享库"`
  - `PLC_WORKSPACE: "PLC工作空间"`

---

## 7. 内部标记说明

| 字段 | 位置 | 说明 |
|---|---|---|
| `project.project_type` | `Project` | 标识项目/共享库/工作空间类型 |
| `project.extra["_workspace_child"]` | `Project.extra` | 标记该项目来自工作空间聚合加载 |
| `error_message` | 返回值第二项 | 统一作为用户提示和日志信息 |
| `COMPANION_ROLE` | `constants` | 伴生角色标识，值为 `"governance"` |
| `COMPANION_PRIMARY_IDE` | `constants` | 主 IDE 名称，值为 `"Trae"` |

---

## 8. 错误语义约定

| 场景 | 错误信息 |
|---|---|
| 工作空间目录不存在 | `工作空间目录不存在: {path}` |
| 目录不是有效的PLC工作空间 | `目录不是有效的PLC工作空间: {path}` |
| 工作空间下无可管理子项目 | `未在工作空间中发现任何可管理的子项目` |
| 共享库加载失败但可降级 | 不直接中断，转 `_create_library_project()` 降级构造 |
| 子项目加载异常 | 不直接中断，转 `_create_fallback_project()` 降级构造 |
| 单项目目录无配置且非 DJ/Workspace | 保留当前"未找到项目配置文件"提示 |
| 跳转目标文件不存在 | `文件不存在: {file_path}` |
| Trae CLI 未安装 | `Trae CLI未安装或不在PATH中` |
| Trae CLI 跳转超时 | `Trae跳转超时` |
| Trae CLI 返回非零退出码 | `Trae返回非零退出码: {code}` |
| 系统默认程序打开失败 | `系统打开失败: {e}` |

---

## 9. Trae伴生约束

本轮接口设计遵守以下原则：
- 工具负责工作空间识别、聚合与治理
- 文件编辑仍以 Trae 为主
- 不在接口层引入新的复杂编辑状态管理
- 源码文件(.scl/.st/.plc)优先跳转 Trae，失败后降级到系统默认程序
- 伴生能力边界通过 `COMPANION_CAPABILITIES` / `COMPANION_NON_CAPABILITIES` 显式声明

---

## 10. `CompanionService`

**模块**: `src.services.companion_service.CompanionService`

伴生跳转服务，集中管理本工具与 Trae IDE 之间的交互边界。本工具定位为 Trae 伴生式治理工具，职责范围：挂载(mount)、索引(index)、检查(check)、汇总(summarize)、导出(export)；不负责：源码编辑(edit_source)、编译(compile)、部署(deploy)、运行时调试(debug_runtime)。

### 10.1 `can_handle()` ✅已实现

```python
@classmethod
def can_handle(cls, capability: str) -> bool:
    ...
```

用途：
- 判断本工具是否具备指定能力

输入：
- `capability`: 能力标识，如 `"edit_source"`、`"check"` 等

输出：
- `True`: 能力在 `COMPANION_CAPABILITIES` 中
- `False`: 能力在 `COMPANION_NON_CAPABILITIES` 中或为未知能力

判定逻辑：

| 条件 | 返回值 |
|------|--------|
| `capability ∈ COMPANION_CAPABILITIES` | `True` |
| `capability ∈ COMPANION_NON_CAPABILITIES` | `False` |
| 其他（未知能力） | `False` |

### 10.2 `should_jump_to_ide()` ✅已实现

```python
@classmethod
def should_jump_to_ide(cls, file_path: str) -> bool:
    ...
```

用途：
- 判断文件是否应跳转到 Trae IDE 处理

输入：
- `file_path`: 文件路径

输出：
- `True`: 文件扩展名在 `TRAJUMP_SUPPORTED_EXTENSIONS` 中
- `False`: 文件扩展名不在支持列表中（如二进制文件 `.exe`、`.dll` 等）

跳转规则：

| 文件类型 | 扩展名示例 | 是否跳转 |
|----------|-----------|---------|
| 源码文件 | `.scl`、`.st`、`.plc` | ✅ 跳转 |
| 配置文件 | `.xml`、`.json`、`.yaml`、`.yml` | ✅ 跳转 |
| 文档文件 | `.md`、`.txt`、`.csv` | ✅ 跳转 |
| 表格文件 | `.xlsx`、`.xls` | ✅ 跳转（系统默认打开） |
| 二进制文件 | `.exe`、`.dll`、`.bin`、`.zip`、`.pdf` | ❌ 不跳转 |

实现说明：
- 通过 `Path(file_path).suffix.lower()` 提取扩展名，与 `TRAJUMP_SUPPORTED_EXTENSIONS` 集合匹配

### 10.3 `jump_to_file()` ✅已实现

```python
@classmethod
def jump_to_file(
    cls, file_path: str, line_number: int = 0
) -> Tuple[bool, Optional[str]]:
    ...
```

用途：
- 执行跳转到 Trae 或系统默认程序打开文件

输入：
- `file_path`: 目标文件路径
- `line_number`: 目标行号（0 表示不指定）

输出：
- 成功: `(True, None)`
- 失败: `(False, error_message)`

分发逻辑：

| 文件扩展名 | 跳转策略 | 失败降级 |
|-----------|---------|---------|
| `.scl` / `.st` / `.plc` | 优先 `_open_in_trae()` | 失败后降级到 `_open_with_system()` |
| `.xlsx` / `.xls` | 直接 `_open_with_system()` | 无降级 |
| 其他支持扩展名 | `_open_with_system()` | 无降级 |

前置检查：
- 文件不存在时直接返回 `(False, "文件不存在: {file_path}")`

### 10.4 `_open_in_trae()` ✅已实现

```python
@classmethod
def _open_in_trae(
    cls, file_path: str, line_number: int = 0
) -> Tuple[bool, Optional[str]]:
    ...
```

用途：
- 尝试通过 Trae CLI 打开文件

输入：
- `file_path`: 文件路径
- `line_number`: 行号

输出：
- 成功: `(True, None)`
- 失败: `(False, error_message)`

CLI 调用方式：

```bash
# 不带行号
trae <file_path>

# 带行号
trae <file_path> --goto <line_number>
```

错误场景：

| 异常类型 | 错误信息 |
|---------|---------|
| `FileNotFoundError` | `"Trae CLI未安装或不在PATH中"` |
| `subprocess.TimeoutExpired` | `"Trae跳转超时"` |
| `returncode != 0` | `"Trae返回非零退出码: {code}"` |
| 其他异常 | `"Trae跳转异常: {e}"` |

实现说明：
- 使用 `subprocess.run()` 执行 CLI 命令，超时阈值 5 秒
- `line_number > 0` 时追加 `--goto` 参数
- 成功时记录日志 `"Trae跳转成功: {file_path}:{line_number}"`

### 10.5 `_open_with_system()` ✅已实现

```python
@classmethod
def _open_with_system(cls, file_path: str) -> Tuple[bool, Optional[str]]:
    ...
```

用途：
- 使用系统默认程序打开文件

输入：
- `file_path`: 文件路径

输出：
- 成功: `(True, None)`
- 失败: `(False, error_message)`

平台适配：

| 平台 | 调用方式 |
|------|---------|
| Windows | `os.startfile(file_path)` |
| macOS | `subprocess.run(["open", file_path])` |
| Linux | `subprocess.run(["xdg-open", file_path])` |

实现说明：
- 通过 `platform.system()` 判断操作系统
- 成功时记录日志 `"系统默认打开: {file_path}"`
- 异常时返回 `(False, "系统打开失败: {e}")`

### 10.6 `get_role_description()` ✅已实现

```python
@classmethod
def get_role_description(cls) -> str:
    ...
```

用途：
- 获取伴生角色描述文本，用于"关于"对话框等信息展示

输出：
- 返回格式化字符串，示例：`"本工具是Trae的伴生式治理工具, 角色: governance, 能力: mount, index, check, summarize, export, 不负责: edit_source, compile, deploy, debug_runtime"`

实现说明：
- 内容由 `COMPANION_PRIMARY_IDE`、`COMPANION_ROLE`、`COMPANION_CAPABILITIES`、`COMPANION_NON_CAPABILITIES` 常量组合生成

### 10.7 `get_jump_summary()` ✅已实现

```python
@classmethod
def get_jump_summary(cls) -> dict:
    ...
```

用途：
- 获取跳转统计摘要，用于 Dashboard 展示

输出：
- 返回字典结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| `role` | `str` | 伴生角色，值来自 `COMPANION_ROLE` |
| `primary_ide` | `str` | 主 IDE 名称，值来自 `COMPANION_PRIMARY_IDE` |
| `capabilities` | `list[str]` | 能力列表，值来自 `COMPANION_CAPABILITIES` |
| `non_capabilities` | `list[str]` | 非能力列表，值来自 `COMPANION_NON_CAPABILITIES` |
| `supported_extensions` | `list[str]` | 支持跳转的扩展名列表（已排序），值来自 `TRAJUMP_SUPPORTED_EXTENSIONS` |

---

## 11. 伴生常量（Companion Constants）

**模块**: `src.core.constants`

### 11.1 `COMPANION_ROLE` ✅已实现

```python
COMPANION_ROLE = "governance"
```

用途：
- 定义本工具的伴生角色标识
- 被 `CompanionService.get_role_description()` 和 `get_jump_summary()` 使用
- 在"关于"对话框中展示为 `"Trae伴生式governance工具"`

### 11.2 `COMPANION_PRIMARY_IDE` ✅已实现

```python
COMPANION_PRIMARY_IDE = "Trae"
```

用途：
- 定义本工具伴生的主 IDE 名称
- 被 `CompanionService` 和 `MenuManager._on_about()` 使用
- 决定跳转优先尝试的目标编辑器

### 11.3 `COMPANION_CAPABILITIES` ✅已实现

```python
COMPANION_CAPABILITIES = ["mount", "index", "check", "summarize", "export"]
```

用途：
- 定义本工具具备的能力标识列表
- 被 `CompanionService.can_handle()` 用于判定能力边界

各能力含义：

| 能力 | 说明 |
|------|------|
| `mount` | 挂载：加载工作空间与子项目 |
| `index` | 索引：扫描资产与构建目录 |
| `check` | 检查：规范检查与诊断 |
| `summarize` | 汇总：聚合报告与统计 |
| `export` | 导出：Excel/报告输出 |

### 11.4 `COMPANION_NON_CAPABILITIES` ✅已实现

```python
COMPANION_NON_CAPABILITIES = ["edit_source", "compile", "deploy", "debug_runtime"]
```

用途：
- 定义本工具明确不具备的能力标识列表
- 被 `CompanionService.can_handle()` 用于判定能力边界
- 这些能力应跳转到 Trae IDE 处理

各非能力含义：

| 非能力 | 说明 |
|--------|------|
| `edit_source` | 源码编辑 |
| `compile` | 编译 |
| `deploy` | 部署 |
| `debug_runtime` | 运行时调试 |

### 11.5 `TRAJUMP_SUPPORTED_EXTENSIONS` ✅已实现

```python
TRAJUMP_SUPPORTED_EXTENSIONS = {
    ".scl", ".st", ".plc", ".xml", ".json", ".md", ".yaml", ".yml",
    ".txt", ".csv", ".xlsx", ".xls",
}
```

用途：
- 定义支持跳转到 IDE 的文件扩展名集合
- 被 `CompanionService.should_jump_to_ide()` 用于判定文件是否应跳转
- 被 `CompanionService.get_jump_summary()` 用于展示支持的扩展名列表

分类说明：

| 类别 | 扩展名 |
|------|--------|
| PLC源码 | `.scl`、`.st`、`.plc` |
| 配置文件 | `.xml`、`.json`、`.yaml`、`.yml` |
| 文档文件 | `.md`、`.txt`、`.csv` |
| 表格文件 | `.xlsx`、`.xls` |

---

## 12. `LibraryService`

**模块**: `src.services.library_service.LibraryService`

共享库治理服务，负责扫描、分类、统计共享库目录，识别分类子目录和规范目录，统计ST源码/规范文件，识别孤立文件，提供库资产汇总。

### 12.1 `scan_library()` ✅已实现

```python
@classmethod
def scan_library(cls, library_path: str) -> Optional[LibraryScanResult]:
    ...
```

用途：
- 扫描共享库目录，返回完整的扫描结果

输入：
- `library_path`: 共享库根目录路径

输出：
- 目录不存在时返回 `None`
- 成功时返回 `LibraryScanResult` 对象

扫描流程：

| 步骤 | 处理逻辑 |
|------|---------|
| 1 | 校验目录存在性 |
| 2 | 遍历一层子目录，排除 `IGNORED_PROJECT_DIRS` |
| 3 | 规范目录（命中 `SPEC_DIR_MARKERS`）→ `_scan_spec_dir()` |
| 4 | 分类目录（命中 `PLC_LIBRARY_CATEGORY_DIRS`）→ `_scan_category_dir()` |
| 5 | 其他目录 → `_scan_unknown_dir()`，仅含ST/规范文件时纳入 |
| 6 | 根目录孤立文件 → `_scan_orphan_files()` |
| 7 | 汇总统计，返回 `LibraryScanResult` |

### 12.2 `identify_spec_dirs()` ✅已实现

```python
@classmethod
def identify_spec_dirs(cls, library_path: str) -> List[Dict]:
    ...
```

用途：
- 识别共享库中的规范目录

输入：
- `library_path`: 共享库根目录路径

输出：
- 目录不存在时返回 `[]`
- 成功时返回 `List[Dict]`，每项包含：

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | `str` | 目录名 |
| `path` | `str` | 绝对路径 |
| `relative_path` | `str` | 相对于库根目录的路径 |

判定规则：目录名（大小写不敏感）命中 `SPEC_DIR_MARKERS` 集合时识别为规范目录。

### 12.3 `get_library_summary()` ✅已实现

```python
@classmethod
def get_library_summary(cls, library_path: str) -> Optional[Dict]:
    ...
```

用途：
- 获取共享库摘要信息

输入：
- `library_path`: 共享库根目录路径

输出：
- 目录不存在时返回 `None`
- 成功时返回字典：

| 字段 | 类型 | 说明 |
|------|------|------|
| `library_name` | `str` | 库名称 |
| `total_categories` | `int` | 分类+规范目录总数 |
| `total_st_files` | `int` | ST源码文件总数 |
| `total_spec_files` | `int` | 规范文件总数 |
| `category_names` | `list[str]` | 分类目录名列表 |
| `spec_dir_names` | `list[str]` | 规范目录名列表 |
| `has_orphan_files` | `bool` | 是否存在孤立文件 |

### 12.4 `_scan_category_dir()` ✅已实现

```python
@classmethod
def _scan_category_dir(
    cls, category_path: Path, library_root: Path
) -> LibraryArtifact:
    ...
```

用途：
- 扫描分类子目录，统计ST源码和规范文件数量

输入：
- `category_path`: 分类子目录路径
- `library_root`: 共享库根目录路径

输出：
- `LibraryArtifact` 对象，包含 `name`/`artifact_type`/`relative_path`/`absolute_path`/`category`/`file_count`/`spec_count`

实现说明：
- 递归遍历目录（`rglob`）
- `.scl`/`.st`/`.plc` 文件计入 `file_count`
- `.md`/`.yaml`/`.yml`/`.json` 文件计入 `spec_count`
- 通过 `_infer_artifact_type()` 推断资产类型

### 12.5 `_scan_spec_dir()` ✅已实现

```python
@classmethod
def _scan_spec_dir(
    cls, spec_path: Path, library_root: Path
) -> Dict:
    ...
```

用途：
- 扫描规范目录，收集规范文件

输入：
- `spec_path`: 规范目录路径
- `library_root`: 共享库根目录路径

输出：
- 字典结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | `str` | 目录名 |
| `relative_path` | `str` | 相对路径 |
| `absolute_path` | `str` | 绝对路径 |
| `file_count` | `int` | 规范文件数量 |
| `files` | `list[dict]` | 文件列表（每项含 `name`/`relative_path`） |

### 12.6 `_scan_orphan_files()` ✅已实现

```python
@classmethod
def _scan_orphan_files(cls, library_root: Path) -> List[Dict]:
    ...
```

用途：
- 扫描根目录下的孤立文件（不在分类目录中的源码/规范文件）

输入：
- `library_root`: 共享库根目录路径

输出：
- `List[Dict]`，每项包含：

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | `str` | 文件名 |
| `path` | `str` | 文件绝对路径 |
| `type` | `str` | 文件类型：`"st"` 或 `"spec"` |

实现说明：
- 仅遍历根目录下文件（非递归）
- 扩展名命中 `LIBRARY_ST_EXTENSIONS` 时 `type` 为 `"st"`
- 扩展名命中 `LIBRARY_SPEC_EXTENSIONS` 时 `type` 为 `"spec"`

### 12.7 `_infer_artifact_type()` ✅已实现

```python
@classmethod
def _infer_artifact_type(cls, category_name: str) -> LibraryArtifactType:
    ...
```

用途：
- 根据分类目录名推断资产类型

输入：
- `category_name`: 分类目录名

输出：
- `LibraryArtifactType` 枚举值

推断映射：

| category_name | 返回值 |
|---------------|--------|
| `actuator` | `LibraryArtifactType.FB` |
| `timer` | `LibraryArtifactType.FB` |
| `counter` | `LibraryArtifactType.FB` |
| `edge` | `LibraryArtifactType.FB` |
| `convert` | `LibraryArtifactType.FC` |
| `analog` | `LibraryArtifactType.FB` |
| `motion` | `LibraryArtifactType.FB` |
| `communication` | `LibraryArtifactType.FC` |
| `safety` | `LibraryArtifactType.FB` |
| 其他 | `LibraryArtifactType.DOC`（默认） |

---

## 13. `LibraryArtifactType` 枚举与共享库常量

**模块**: `src.core.constants`

### 13.1 `LibraryArtifactType` ✅已实现

```python
class LibraryArtifactType(Enum):
    FB = "fb"
    FC = "fc"
    DB = "db"
    UDT = "udt"
    GVL = "gvl"
    PROGRAM = "program"
    SPEC = "spec"
    DOC = "doc"
    TEST = "test"
```

用途：
- 定义共享库资产类型枚举
- 被 `LibraryService._infer_artifact_type()` 返回
- 被 `LibraryArtifact.artifact_type` 字段使用

各类型含义：

| 枚举值 | 值 | 说明 |
|--------|----|------|
| `FB` | `"fb"` | 功能块 |
| `FC` | `"fc"` | 函数 |
| `DB` | `"db"` | 数据块 |
| `UDT` | `"udt"` | 用户自定义类型 |
| `GVL` | `"gvl"` | 全局变量表 |
| `PROGRAM` | `"program"` | 程序 |
| `SPEC` | `"spec"` | 规范文档 |
| `DOC` | `"doc"` | 说明文档 |
| `TEST` | `"test"` | 测试 |

配套描述映射 `LIBRARY_ARTIFACT_TYPE_DESC` 同步定义。

### 13.2 `SPEC_DIR_MARKERS` ✅已实现

```python
SPEC_DIR_MARKERS = {
    "00_通用规范",
    "01_编程规范",
    "02_设计规范",
    "00_规范",
    "spec",
    "specs",
    "standards",
}
```

用途：
- 规范目录标识名集合
- 被 `LibraryService.scan_library()` 和 `ArtifactRegistryService.scan_library_artifacts()` 用于区分规范目录与分类子目录
- 判定逻辑：目录名（大小写不敏感）命中该集合时识别为规范目录

### 13.3 `LIBRARY_ST_EXTENSIONS` ✅已实现

```python
LIBRARY_ST_EXTENSIONS = {
    ".scl",
    ".st",
    ".plc",
}
```

用途：
- 共享库ST源码文件扩展名集合
- 被 `LibraryService._scan_category_dir()`/`_scan_unknown_dir()`/`_scan_orphan_files()` 用于统计ST源码文件

### 13.4 `LIBRARY_SPEC_EXTENSIONS` ✅已实现

```python
LIBRARY_SPEC_EXTENSIONS = {
    ".md",
    ".yaml",
    ".yml",
    ".json",
}
```

用途：
- 共享库规范文件扩展名集合
- 被 `LibraryService._scan_category_dir()`/`_scan_spec_dir()`/`_scan_unknown_dir()`/`_scan_orphan_files()` 用于统计规范文件

---

## 14. `ArtifactRegistryService` 共享库扩展

**模块**: `src.services.artifact_registry_service.ArtifactRegistryService`

### 14.1 `scan_library_artifacts()` ✅已实现

```python
@classmethod
def scan_library_artifacts(cls, library_path: str) -> List[Dict]:
    ...
```

用途：
- 扫描共享库的资产目录结构，返回分类信息列表

输入：
- `library_path`: 共享库根目录路径

输出：
- 目录不存在时返回 `[]`
- 成功时返回 `List[Dict]`，每项包含：

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | `str` | 目录名 |
| `path` | `str` | 绝对路径 |
| `type` | `str` | 分类类型：分类目录名/`"spec_dir"`/`"other"` |
| `is_spec_dir` | `bool` | 是否为规范目录 |

分类规则：

| 条件 | type 值 | is_spec_dir |
|------|---------|-------------|
| 目录名命中 `SPEC_DIR_MARKERS` | `"spec_dir"` | `True` |
| 目录名命中 `PLC_LIBRARY_CATEGORY_DIRS` | 目录名（小写） | `False` |
| 其他 | `"other"` | `False` |

### 14.2 `identify_spec_dirs_in_library()` ✅已实现

```python
@classmethod
def identify_spec_dirs_in_library(cls, library_path: str) -> List[Dict]:
    ...
```

用途：
- 识别共享库中的规范目录

输入：
- `library_path`: 共享库根目录路径

输出：
- 目录不存在时返回 `[]`
- 成功时返回 `List[Dict]`，每项含 `name`/`path`/`relative_path`

判定规则：目录名（大小写不敏感）命中 `SPEC_DIR_MARKERS` 集合时识别为规范目录。

---

## 15. EventBus 伴生跳转信号

**模块**: `src.core.event_bus.EventBus`

### 15.1 `companion_jump_request` ✅已实现

```python
companion_jump_request = pyqtSignal(str, int)  # 参数: file_path, line_number
```

用途：
- 伴生跳转请求信号，用于 UI 组件向 `CompanionService` 发起文件跳转

信号参数：

| 参数 | 类型 | 说明 |
|------|------|------|
| `file_path` | `str` | 目标文件路径 |
| `line_number` | `int` | 目标行号（0 表示不指定） |

使用方式：

```python
from src.core.event_bus import EventBus

bus = EventBus.get_instance()

# 发射信号
bus.companion_jump_request.emit("/path/to/file.scl", 42)

# 连接槽函数
bus.companion_jump_request.connect(on_jump_request)

def on_jump_request(file_path: str, line_number: int):
    from src.services.companion_service import CompanionService
    success, error = CompanionService.jump_to_file(file_path, line_number)
```

实现说明：
- 信号定义在 `EventBus` 类中，与其他事件信号（`project_opened`、`document_open_request` 等）并列
- 遵循 EventBus 单例模式，通过 `EventBus.get_instance()` 获取实例
- 信号参数与 `CompanionService.jump_to_file()` 的输入参数对齐

---

## 16. `WorkspaceService`

**模块**: `src.services.workspace_service.WorkspaceService`

工作空间治理服务，负责跨项目规范检查、聚合报告生成、汇总统计和命名冲突检测。

### 16.1 `generate_report()` ✅已实现

```python
@classmethod
def generate_report(
    cls, workspace_path: str, projects: List[Any]
) -> Optional[WorkspaceReport]:
    ...
```

用途：
- 生成工作空间聚合报告，汇总各子项目的检查结果和统计信息

输入：
- `workspace_path`: 工作空间根目录路径
- `projects`: 子项目 `Project` 对象列表

输出：
- 目录不存在时返回 `None`
- 成功时返回 `WorkspaceReport` 对象

报告生成流程：

| 步骤 | 处理逻辑 |
|------|---------|
| 1 | 校验目录存在性 |
| 2 | 遍历子项目，按类型统计ST/规范文件数量 |
| 3 | 共享库类型子项目 → `LibraryService.get_library_summary()` |
| 4 | 其他类型子项目 → `_count_project_files()` |
| 5 | 共享库孤立文件 → 生成 `warning` 检查项 |
| 6 | `detect_naming_conflicts()` 检测命名冲突 |
| 7 | 命名冲突 → 生成 `warning` 检查项 |
| 8 | 汇总返回 `WorkspaceReport` |

### 16.2 `detect_naming_conflicts()` ✅已实现

```python
@classmethod
def detect_naming_conflicts(
    cls, projects: List[Any]
) -> List[NamingConflict]:
    ...
```

用途：
- 检测跨项目的FB/FC命名冲突

输入：
- `projects`: 子项目 `Project` 对象列表

输出：
- `List[NamingConflict]`：冲突列表，无冲突时返回空列表

检测规则：
- 递归扫描所有子项目的ST源码文件（扩展名在 `LIBRARY_ST_EXTENSIONS` 中）
- 筛选以 `FB_` 或 `FC_` 开头的文件名
- 同名文件出现在多个子项目中时判定为冲突
- 每个冲突条目包含冲突名称和出现位置列表（格式：`项目名/相对路径`）

### 16.3 `check_workspace()` ✅已实现

```python
@classmethod
def check_workspace(
    cls, workspace_path: str, projects: List[Any]
) -> List[WorkspaceCheckItem]:
    ...
```

用途：
- 对工作空间内所有子项目执行统一检查

输入：
- `workspace_path`: 工作空间根目录路径
- `projects`: 子项目 `Project` 对象列表

输出：
- `List[WorkspaceCheckItem]`：检查条目列表

检查项与严重级别：

| 检查项 | severity | status | 说明 |
|--------|----------|--------|------|
| 子项目目录不存在 | `error` | `error` | 项目路径无效或已被删除 |
| 子项目目录存在 | `info` | `ok` | 正常状态 |
| 共享库孤立文件 | `warning` | `warning` | 共享库根目录下存在未归类的源码/规范文件 |
| 跨项目命名冲突 | `warning` | `warning` | 同名FB/FC出现在多个子项目中 |

### 16.4 `get_workspace_statistics()` ✅已实现

```python
@classmethod
def get_workspace_statistics(
    cls, workspace_path: str, projects: List[Any]
) -> Dict:
    ...
```

用途：
- 获取工作空间汇总统计信息

输入：
- `workspace_path`: 工作空间根目录路径
- `projects`: 子项目 `Project` 对象列表

输出：
- 返回字典：

| 字段 | 类型 | 说明 |
|------|------|------|
| `workspace_name` | `str` | 工作空间名称 |
| `total_projects` | `int` | 子项目总数 |
| `project_type_distribution` | `Dict[str, int]` | 项目类型分布（键为 `ProjectType.value`，值为数量） |
| `total_st_files` | `int` | ST源码文件总数 |
| `total_spec_files` | `int` | 规范文件总数 |
| `naming_conflicts` | `int` | 命名冲突数量 |
| `has_issues` | `bool` | 是否存在问题（命名冲突数 > 0 时为 `True`） |

### 16.5 `_count_project_files()` ✅已实现

```python
@classmethod
def _count_project_files(cls, project_path: str) -> Tuple[int, int]:
    ...
```

用途：
- 统计项目目录下的ST文件和规范文件数量

输入：
- `project_path`: 项目路径

输出：
- `Tuple[int, int]`：(ST文件数, 规范文件数)

统计规则：
- ST文件：扩展名在 `LIBRARY_ST_EXTENSIONS` 中（`.scl`/`.st`/`.plc`）
- 规范文件：扩展名为 `.md`/`.yaml`/`.yml`/`.json`，但排除 `.plc.json` 和 `project.json`
- 递归遍历目录（`rglob`）
- 路径不存在或为空时返回 `(0, 0)`

---

## 17. 工作空间治理数据模型

**模块**: `src.services.workspace_service`

### 17.1 `WorkspaceCheckItem` ✅已实现

```python
@dataclass
class WorkspaceCheckItem:
    project_name: str
    project_path: str
    project_type: str
    status: str
    message: str
    severity: str = "info"
```

用途：
- 工作空间检查条目，记录单个检查项的结果

字段说明：

| 字段 | 类型 | 说明 |
|------|------|------|
| `project_name` | `str` | 项目名称，跨项目检查项使用 `"*"` |
| `project_path` | `str` | 项目路径，跨项目检查项使用 `""` |
| `project_type` | `str` | 项目类型（`ProjectType.value`），跨项目检查项使用 `"workspace"` |
| `status` | `str` | 检查状态：`"ok"` / `"warning"` / `"error"` |
| `message` | `str` | 检查消息描述 |
| `severity` | `str` | 严重级别：`"info"` / `"warning"` / `"error"`，默认 `"info"` |

提供 `to_dict()` 方法用于序列化。

### 17.2 `NamingConflict` ✅已实现

```python
@dataclass
class NamingConflict:
    name: str
    locations: List[str] = field(default_factory=list)
```

用途：
- 命名冲突条目，记录跨项目重复的FB/FC名称

字段说明：

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | `str` | 冲突的FB/FC名称（如 `"FB_Valve"`） |
| `locations` | `List[str]` | 出现位置列表，格式为 `"项目名/相对路径"` |

提供 `to_dict()` 方法用于序列化。

### 17.3 `WorkspaceReport` ✅已实现

```python
@dataclass
class WorkspaceReport:
    workspace_path: str
    workspace_name: str
    generated_at: str = ""
    total_projects: int = 0
    total_st_files: int = 0
    total_spec_files: int = 0
    project_summaries: List[Dict] = field(default_factory=list)
    check_items: List[WorkspaceCheckItem] = field(default_factory=list)
    naming_conflicts: List[NamingConflict] = field(default_factory=list)
    library_summaries: List[Dict] = field(default_factory=list)
```

用途：
- 工作空间聚合报告，汇总所有子项目的检查结果和统计信息

字段说明：

| 字段 | 类型 | 说明 |
|------|------|------|
| `workspace_path` | `str` | 工作空间根目录路径 |
| `workspace_name` | `str` | 工作空间名称 |
| `generated_at` | `str` | 报告生成时间，`__post_init__` 自动填充为当前时间 |
| `total_projects` | `int` | 子项目总数 |
| `total_st_files` | `int` | ST源码文件总数 |
| `total_spec_files` | `int` | 规范文件总数 |
| `project_summaries` | `List[Dict]` | 各子项目摘要列表 |
| `check_items` | `List[WorkspaceCheckItem]` | 检查条目列表 |
| `naming_conflicts` | `List[NamingConflict]` | 命名冲突列表 |
| `library_summaries` | `List[Dict]` | 共享库摘要列表 |

提供 `to_dict()` 方法用于序列化，其中 `check_items` 和 `naming_conflicts` 会递归调用各自的 `to_dict()`。

---

## 18. IPCBridge API 完整清单

**模块**: `src.ui.webview_window.IPCBridge`

**实例化**: 由 `create_window()` 函数内部创建，绑定到 `webview.create_window(js_api=bridge)`

**调用方式**: 前端JS通过 `window.pywebview.api.method_name(args)` 调用

V4.0引入 **IPCBridge** 作为前后端通信桥梁。所有前端可调用的API都定义在 IPCBridge 类中。原有的 Service 层 API 不变，但前端不再直接调用它们。

### 18.1 应用信息 API

#### `get_app_info()` ✅ 已实现

```python
def get_app_info(self) -> dict
```

返回: `{"name": APP_NAME, "version": VERSION}`

#### `ipc_ping()` ✅ 已实现

```python
def ipc_ping(self) -> dict
```

返回: `{"status": "ok", "message": "pong", "mock_mode": bool}`

### 18.2 设置管理 API

#### `get_settings()` ✅ 已实现

```python
def get_settings(self) -> dict
```

返回: SettingsManager.get_all() 的结果

#### `update_setting(key: str, value)` ✅ 已实现

```python
def update_setting(self, key: str, value) -> bool
```

行为: 设置值 + 保存 + emit("setting_changed")

返回: True

#### `reset_settings()` ✅ 已实现

```python
def reset_settings(self) -> bool
```

行为: 重置为默认值 + emit("settings_reset")

返回: True

### 18.3 项目管理 API

#### `create_project(project_info: str)` ✅ 已实现

```python
def create_project(self, project_info: str) -> dict
```

输入: JSON字符串，包含name/business_line/template_id等字段

输出: `{"success": bool, "path": str或None, "error": str或None}`

副作用: emit("project_created")

#### `open_project(path: str)` ✅ 已实现

```python
def open_project(self, path: str) -> dict
```

输出: `{"success": bool, "project": {project_id, name, path, business_line}, "error": ...}`

副作用: emit("project_opened")

#### `close_project()` ✅ 已实现

```python
def close_project(self) -> dict
```

副作用: emit("project_closed")

#### `get_project_detail(path: str)` ✅ 已实现

```python
def get_project_detail(self, path: str) -> dict
```

输出: 完整项目信息字典（15+字段）

#### `save_project_info(info_json: str)` ✅ 已实现

```python
def save_project_info(self, info_json: str) -> dict
```

输入: JSON字符串

#### `get_recent_projects()` ✅ 已实现

```python
def get_recent_projects(self) -> list
```

输出: 最近项目列表（Mock模式下返回MOCK_PROJECTS）

### 18.4 文档管理 API

#### `create_document(params: str)` ✅ 已实现

```python
def create_document(self, params: str) -> dict
```

输入: JSON字符串{project_path, doc_type, doc_name, version, author, content}

副作用: emit("document_created")

#### `list_documents(project_path: str)` ✅ 已实现

```python
def list_documents(self, project_path: str) -> list
```

#### `read_document(file_path: str)` ✅ 已实现

```python
def read_document(self, file_path: str) -> dict
```

输出: `{"success": bool, "content": str或None, "error": ...}`

#### `save_document(params: str)` ✅ 已实现

```python
def save_document(self, params: str) -> dict
```

输入: JSON字符串{file_path, content}

### 18.5 变更管理 API

#### `list_change_requests(project_path: str)` ✅ 已实现

```python
def list_change_requests(self, project_path: str) -> list
```

#### `create_change_request(params: str)` ✅ 已实现

```python
def create_change_request(self, params: str) -> dict
```

输入: JSON字符串{project_path, category, title, description}

#### `update_change_status(params: str)` ✅ 已实现

```python
def update_change_status(self, params: str) -> dict
```

输入: JSON字符串{project_path, change_id, new_status}

#### `approve_change_request(params: str)` ✅ 已实现

```python
def approve_change_request(self, params: str) -> dict
```

输入: JSON字符串{project_path, change_id, approver}

### 18.6 版本同步 API

#### `run_version_check(project_path: str)` ✅ 已实现

```python
def run_version_check(self, project_path: str) -> dict
```

输出: `{is_consistent: bool, gaps: [...], summary: {...}}`

#### `generate_chg(project_path: str, output_dir: str="")` ✅ 已实现

```python
def generate_chg(self, project_path: str, output_dir: str = "") -> dict
```

#### `generate_ifc(project_path: str, output_dir: str="")` ✅ 已实现

```python
def generate_ifc(self, project_path: str, output_dir: str = "") -> dict
```

### 18.7 规范检查 API

#### `get_checkers()` ✅ 已实现

```python
def get_checkers(self) -> list
```

输出: 检查器列表[{id, name, engine, enabled}]

#### `run_spec_check(project_path: str, checker_ids: str="")` ✅ 已实现

```python
def run_spec_check(self, project_path: str, checker_ids: str = "") -> dict
```

输出: `{total_issues: int, results: [...], summary: {...}}`

### 18.8 诊断分析 API

#### `run_diagnosis(project_path: str)` ✅ 已实现

```python
def run_diagnosis(self, project_path: str) -> dict
```

输出: `{report: ..., metrics: ...}`

### 18.9 自动修复 API

#### `get_available_fixers()` ✅ 已实现

```python
def get_available_fixers(self) -> list
```

#### `scan_fixes(params: str)` ✅ 已实现

```python
def scan_fixes(self, params: str) -> dict
```

输出: `{total_issues, files_scanned, fixable_issues}`

#### `fix_project(params: str)` ✅ 已实现

```python
def fix_project(self, params: str) -> dict
```

输入: JSON字符串{project_path, fixer_ids, dry_run}

输出: `{success, total_fixed, total_rolled_back}`

### 18.10 Excel导出 API

#### `export_excel_single(params: str)` ✅ 已实现

```python
def export_excel_single(self, params: str) -> dict
```

#### `export_excel_batch(project_path: str)` ✅ 已实现

```python
def export_excel_batch(self, project_path: str) -> dict
```

### 18.11 仪表盘 API

#### `get_dashboard_stats()` ✅ 已实现

```python
def get_dashboard_stats(self) -> dict
```

输出: `{project_count, template_count, recent_projects: [...]}`

### 18.12 模板 API

#### `get_templates()` ✅ 已实现

```python
def get_templates(self) -> list
```

输出: [{id, name}]

### 18.13 文件对话框 API

#### `browse_directory(title: str="选择目录")` ✅ 已实现

```python
def browse_directory(self, title: str = "选择目录") -> str
```

#### `browse_file(title: str="选择文件", file_filter: str="All files (*.*)")` ✅ 已实现

```python
def browse_file(self, title: str, file_filter: str) -> str
```

#### `save_file_dialog(title: str="保存文件", file_filter: str="All files (*.*)")` ✅ 已实现

```python
def save_file_dialog(self, title: str, file_filter: str) -> str
```

### 18.14 系统操作 API

#### `open_in_explorer(path: str)` ✅ 已实现

```python
def open_in_explorer(self, path: str) -> bool
```

#### `open_url(url: str)` ✅ 已实现

```python
def open_url(self, url: str) -> bool
```

### 18.15 窗口控制 API

#### `window_minimize()` ✅ 已实现

```python
def window_minimize(self) -> bool
```

#### `window_maximize()` ✅ 已实现

```python
def window_maximize(self) -> bool
```

注意: 使用toggle_fullscreen()

#### `window_close()` ✅ 已实现

```python
def window_close(self) -> bool
```

### 18.16 Mock数据 API

#### `get_mock_data(data_type: str)` ✅ 已实现

```python
def get_mock_data(self, data_type: str) -> dict
```

支持的data_type: "projects", "checkers", "spec_result", "diagnostic"

### 18.17 IPCBridge 内部方法

#### `_emit(event: str, data=None)`

事件推送: 将payload序列化为JSON，通过window.evaluate_js推送到前端window.__ipc_recv()

#### `_safe_call(name: str, fn, *args, **kwargs)`

统一异常包装: 记录日志→执行→捕获异常→返回错误字典

### 18.18 create_window() 工厂函数

```python
def create_window(
    html_path: str = None,
    title: str = "",
    width: int = 1280,
    height: int = 800
) -> Window
```

- html_path默认: BASE_DIR/ui_prototype/index.html
- 创建IPCBridge实例→创建webview窗口→绑定js_api→设置最小尺寸960x600

---

*文档版本: INT-V4.0.0 | 最后更新: 2026-06-01*
