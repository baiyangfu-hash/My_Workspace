---
version: V0.9.1
status: 实测版
date: 2026-07-08
baseline: pyproject=0.9.1 / 1115 passed / ruff 0 errors
source: 对 Claude-result V3 报告（2026-07-08 03:42）12 项残留问题的逐项实测复核
verifier: GLM-5.2（Grep/Read/mypy 实证）
---

# auto-pm V0.9.1 残留问题实测诊断报告

> 本报告针对 `09_整改项/Claude-result`（V3 第三版诊断报告）中"四、当前仍存在的问题"列出的 12 项残留问题，使用 Grep / Read / mypy 工具逐项实测复核，标注每项的**实测状态**并与原报告声明对照。
>
> 实测基线：`pyproject.toml` version=0.9.1，源码目录 `auto_pm/`（不含 tests/），mypy 实际运行于 V0.9.1 代码。

---

## 实测状态说明

| 标记 | 含义 |
|------|------|
| **存在** | 问题确实存在，且与原报告声明一致 |
| **已修复** | 问题已不存在 |
| **部分修复** | 问题部分存在，部分已修复 |
| **失真** | 问题存在但原报告的关键声明（数量/性质/位置）与实测不符 |

---

## 一、逐项实测结果

### 问题 1：`except Exception` 70+ 处（含 frontmatter_svc.py 2 处静默）

**问题描述**：源码中广泛使用 `except Exception`，其中 `spec/services/frontmatter_svc.py` 有 2 处仅 `except Exception:` 无变量绑定、无日志记录的"静默吞没"。

**实测方法**：
- `Grep "except Exception" auto_pm/ --count`（不含 tests/）
- `Read auto_pm/spec/services/frontmatter_svc.py:80-156`

**实测证据**：

Grep 统计：**70 处，分布在 22 个文件**（auto_pm/ 源码，不含 tests/），逐文件分布：

| 文件 | 数量 | 文件 | 数量 |
|------|------|------|------|
| system_facade.py | 9 | delivery_facade.py | 8 |
| ui/factories.py | 8 | workbench_facade.py | 7 |
| cli/project.py | 5 | core/project_service.py | 5 |
| cli/change.py | 3 | spec_facade.py | 3 |
| db/sync.py | 2 | spec/services/frontmatter_svc.py | 2 |
| ui/qml/bridges/change_bridge.py | 2 | change_facade.py | 6 |
| 其余 10 个文件各 1 处 | 10 | — | — |

frontmatter_svc.py L89-92 / L140-147 实测代码：
```python
# L89-92
try:
    content = file_path.read_text(encoding="utf-8")
except Exception:                                    # ← 无 as e 绑定
    log.warning("读取规范文件 frontmatter 失败: %s", file_path, exc_info=True)  # ← 有日志！
    ...

# L140-147
try:
    content = item.file_path.read_text(encoding="utf-8")
    ...
except Exception:                                    # ← 无 as e 绑定
    log.warning("应用 frontmatter 失败: %s", item.file_path, exc_info=True)    # ← 有日志！
    ...
```

**实测状态**：**失真**

**与 Claude-result 声明的对照**：
- ✅ "70+ 处"：实测正好 70 处，符合"70+"声明。
- ✅ 文件分布大体一致（Facade ~33 / CLI ~11 / Core-DB ~9 / Spec 2 / factories 8）。
- ❌ **"frontmatter_svc.py 2 处无日志记录的静默捕获"严重失真**：L91/L146 两处 `except Exception:` 确实无 `as e` 变量绑定，但**紧接着都有 `log.warning(..., exc_info=True)` 日志记录**，并非"静默吞没"。原报告"真正需要修复的仅 frontmatter_svc.py 2 处无日志记录的静默捕获"这一结论不成立。
- 实际需要修复的仅是"缺少 `as e` 绑定"的代码风格问题，非性质问题。

---

### 问题 2：`_get_project_info()` 两处克隆

**问题描述**：`system_facade.py` 与 `delivery_facade.py` 各有一个完全相同的 `_get_project_info()` 方法（约 18 行），实现"DB 缓存优先 + 文件系统降级"逻辑。

**实测方法**：
- `Read auto_pm/application/system_facade.py:56-80`
- `Read auto_pm/application/delivery_facade.py:64-88`

**实测证据**：

两处方法逐行对照（仅日志文案不同）：

| 行号 | system_facade.py L56-80 | delivery_facade.py L64-88 |
|------|-------------------------|---------------------------|
| 签名 | `def _get_project_info(self, project_id: str) -> ProjectInfo \| None:` | 完全相同 |
| 逻辑 | DB 缓存优先 → `RuntimeError` fallback → `list_projects()` 过滤 | 完全相同 |
| 唯一差异 | L79: `log.warning("get_project_by_id 文件系统扫描失败: %s", e, ...)` | L87: `log.warning("文件系统扫描失败，返回 None: %s", e, ...)` |

**实测状态**：**存在**

**与 Claude-result 声明的对照**：
- ✅ 两处克隆确认存在，逻辑完全相同（仅日志文案差异）。
- ✅ "约 18 行"：方法体含 docstring 共 25 行，纯逻辑约 18 行，符合声明。
- ✅ 与 `ProjectService.get_project()` (L209-229) 逻辑等价的判断成立。

---

### 问题 3：`FacadeRegistry.initialize()` 使用 `dict[str, Any]`

**问题描述**：`ui/registry.py` 的 `initialize()` 方法参数为 `dict[str, Any]`，字符串 key 拼写错误只能运行时发现。

**实测方法**：
- `Read auto_pm/ui/registry.py:1-70`

**实测证据**：

`auto_pm/ui/registry.py` L28-39：
```python
def initialize(self, services: dict[str, Any]) -> None:
    """根据传入的基础 Service 字典，装配 Facades"""
    dashboard_service = cast(DashboardServiceProtocol, services.get("dashboard_service"))
    project_service = cast(ProjectServiceProtocol, services.get("project_service"))
    asset_summary_service = cast(AssetSummaryServiceProtocol, services.get("asset_summary_service"))
    change_service = services.get("change_service")
    spec_check_service = services.get("spec_check_service")
    ...
```

**实测状态**：**存在**

**与 Claude-result 声明的对照**：
- ✅ `ui/registry.py` 文件确实存在（原 LS 因字符限制未列出，但 Grep 定位到 L18 `class FacadeRegistry` / L28 `def initialize`）。
- ✅ 参数确为 `dict[str, Any]`，内部用 `cast()` 适配 Protocol。
- ✅ 字符串 key 拼写错误只能运行时发现的风险成立。

---

### 问题 4：7 处 TODO 未闭环

**问题描述**：`auto_pm/` 下有 7 处 TODO 未闭环，分布在 workbench_facade / delivery_bridge / system_bridge / change_bridge / dto / substance_checker。

**实测方法**：
- `Grep "TODO" auto_pm/ --content -n`（不含 tests/）

**实测证据**：

Grep 实测共 **17 行命中**，剔除 1 处字符串字面量后，实际 TODO 注释 **16 处**：

| 文件 | 实测数量 | 原报告声明 | 内容 |
|------|----------|------------|------|
| `application/workbench_facade.py` | **7** | 4 | L83/L101 health_status、L85/L103 last_activity_at、L139 document_status、L140 vartable_status、L141 pending_actions |
| `ui/qml/bridges/delivery_bridge.py` | 3 | 3 | L4/L67/L77 资产刷新/汇总 QML 接入 |
| `ui/qml/bridges/system_bridge.py` | 2 | 2 | L5/L68 模板应用 QML 接入 |
| `ui/qml/bridges/change_bridge.py` | 1 | 1 | L67 创建/流转/编辑 QML UI |
| `ui/contracts/dto/delivery_dto.py` | 2 | 2（与 system_dto 合并计） | L4/L16 Service 结构细化 |
| `ui/contracts/dto/system_dto.py` | 1 | （含上面） | L6 Service 结构细化 |
| `plc/substance_checker.py` | **0**（字符串） | 1 | L28 `"TODO"` 是 `_PLACEHOLDER_KEYWORDS` 列表中的**字符串字面量**，非注释 |
| **合计** | **16** | 标题"7 处" / 表格求和 13 | — |

**实测状态**：**失真**

**与 Claude-result 声明的对照**：
- ❌ 标题"7 处 TODO 未闭环"严重低估：实测 16 处 TODO 注释。
- ❌ 表格求和（4+3+2+1+2+1=13）也低估。
- ❌ `workbench_facade.py` 实测 7 处（原报告 4 处），且原报告漏列 `vartable_status`（L140）。
- ❌ `substance_checker.py` L28 的 `"TODO"` 是占位符关键词列表中的字符串字面量（用于检测文档空壳），并非 TODO 注释，不应计入。
- ✅ delivery_bridge / system_bridge / change_bridge 数量一致。

---

### 问题 5：`change/models.py` 与 `models/change.py` 命名歧义

**问题描述**：两个文件名相同（仅包路径不同），职责易混淆。

**实测方法**：
- `Read auto_pm/change/models.py:1-40`
- `Read auto_pm/models/change.py:1-40`

**实测证据**：

| 文件 | 职责 | 内容 |
|------|------|------|
| `auto_pm/change/models.py` | 规范常量 + 异常类 + 校验函数 + re-export | `DOMAINS` dict、`SpecViolationError`/`TransitionGuardError`、`validate_*` 函数、`from auto_pm.models import ChangeRequest` re-export |
| `auto_pm/models/change.py` | Pydantic v2 数据模型 | `class ChangeRequest(BaseModel)`、`class ChangeSummary(BaseModel)` |

`change/models.py` L7-8 文档字符串已明确说明："数据模型已迁移至 auto_pm/models/change.py（Pydantic v2）。本文件保留规范常量、异常类和校验函数"。

**实测状态**：**存在**

**与 Claude-result 声明的对照**：
- ✅ 命名歧义确认存在。
- ✅ 职责划分与原报告声明一致（常量+异常 vs Pydantic 模型）。
- 注：文件已有文档字符串说明职责，命名歧义是历史包袱，影响可控。

---

### 问题 6：`ProjectInfo` 模型原地修改属性

**问题描述**：`ProjectScanner._deduplicate_projects()` 和 `_enrich_from_plc_json()` 中直接修改 `ProjectInfo` 实例属性（共 ~15 处）。

**实测方法**：
- `Grep "\w+\.\w+ = " auto_pm/core/project_scanner.py -n`

**实测证据**：

Grep 实测共 **25 处**属性赋值（剔除 `self.X = ` 的 2 处 __init__ 赋值）：

| 方法区域 | 行号 | 数量 | 模式 |
|----------|------|------|------|
| `_deduplicate_projects` | L100-118 | 10 | `primary.name/version/description/phase/business_line/project_type/equipment_type/plc_vendor/plc_model/stack = other.X` |
| `_enrich_from_plc_json` | L456-484 | 11 | `info.stack/version/description/project_type/equipment_type/plc_vendor/plc_model/name/extra = ...` |
| 其他（file_mtime 设置） | L161/L168/L175 | 3 | `info.file_mtime = self.get_project_mtime(...)` |
| 其他（stack fallback） | L199 | 1 | `info.stack = inferred` |
| **合计** | — | **25** | — |

**实测状态**：**失真**

**与 Claude-result 声明的对照**：
- ✅ 原地修改属性的问题确实存在。
- ❌ "共 ~15 处"低估：实测 25 处（_deduplicate 10 + _enrich 11 + 其他 4）。仅计原报告点名的两个方法也有 21 处，非 15 处。
- ✅ Pydantic v2 默认允许赋值（非 frozen），技术上合法的判断成立。

---

### 问题 7：Ruff 规则集偏保守

**问题描述**：`.ruff.toml` 仅启用基础规则子集 `["E4", "E7", "E9", "F", "I", "T20"]`。

**实测方法**：
- `Read .ruff.toml`

**实测证据**：

`.ruff.toml` L35-42：
```toml
[lint]
select = ["E4", "E7", "E9", "F", "I", "T20"]
ignore = []
fixable = ["ALL"]
```

**实测状态**：**存在**

**与 Claude-result 声明的对照**：
- ✅ 规则集与原报告完全一致。
- ✅ 确实仅启用基础子集（pycodestyle E4/E7/E9 + Pyflakes F + Isort I + flake8-print T20），未启用 B/SIM/UP/RUF。

---

### 问题 8：`AutoPmConfig` 配置类功能单薄

**问题描述**：配置类仅 2 个字段，注释 `# Add more ...` 暗示尚未扩展，大量硬编码配置分散各模块。

**实测方法**：
- `Read auto_pm/config/app_config.py`

**实测证据**：

`auto_pm/config/app_config.py` 全文（仅 23 行）：
```python
class AutoPmConfig(BaseSettings):
    app_name: str = __app_name__
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    # Add more ...
```

仅 2 个业务字段（`app_name` / `log_level`），L11 `# Add more ...` 注释确认。

**实测状态**：**存在**

**与 Claude-result 声明的对照**：
- ✅ 字段数量（2 个）与原报告一致。
- ✅ `# Add more ...` 注释确认。
- ✅ 硬编码分散（scan_depth=4 / backupCount=30/90 / .auto-pm/index.db 等）的判断成立。

---

### 问题 9：`os.path` 与 `pathlib.Path` 混用

**问题描述**：core/change/db/utils 主要用 `os.path`，db/connection/logging/spec 主要用 `pathlib`。

**实测方法**：
- `Grep "os\.path" auto_pm/ --files-with-matches`
- `Grep "from pathlib" auto_pm/ --files-with-matches`

**实测证据**：

| 模式 | 命中文件数 | 主要分布 |
|------|-----------|----------|
| `os.path` | **28** | core/（6）、change/（4）、plc/（5）、cli/（5）、db/sync.py、utils/file_utils.py、app_context.py 等 |
| `from pathlib` | **34** | spec/（8）、vartable/parsers/（10）、ui/（3）、db/connection.py、logging/、cli/ 等 |

注意：部分文件**同时使用**两种模式（如 `db/connection.py`、`cli/` 部分文件）。

**实测状态**：**存在**

**与 Claude-result 声明的对照**：
- ✅ 混用现象确认存在。
- ✅ 分布大体符合（core/change/utils 偏 os.path；spec/logging 偏 pathlib）。
- 补充：vartable/parsers/ 大量使用 pathlib（原报告未提及）。

---

### 问题 10：7 个向后兼容委托方法

**问题描述**：`project_service.py` L674-703 保留 7 个一行委托的向后兼容包装方法。

**实测方法**：
- `Read auto_pm/core/project_service.py:670-703`

**实测证据**：

L672-703 实测 7 个方法，全部一行委托：

| 行号 | 方法 | 委托目标 |
|------|------|----------|
| L674 | `_try_identify_project` | `self._scanner.try_identify_project` |
| L678 | `_read_copier_answers` | `self._scanner.read_copier_answers` |
| L682 | `_read_plc_json` | `self._scanner.read_plc_json` |
| L686 | `_read_pm_session` | `self._scanner.read_pm_session` |
| L691 | `_extract_id_from_dirname`（static） | `ProjectScanner.extract_id_from_dirname` |
| L696 | `_infer_stack`（static） | `ProjectScanner.infer_stack` |
| L701 | `_get_project_mtime`（static） | `ProjectScanner.get_project_mtime` |

**实测状态**：**存在**

**与 Claude-result 声明的对照**：
- ✅ 7 个方法确认存在，全部一行委托。
- ✅ 行号范围 L674-703 准确。

---

### 问题 11：`search_projects()` 未走缓存

**问题描述**：`search_projects()` 直接调 `list_projects()` 全量文件系统扫描，无 DB 缓存优先路径。

**实测方法**：
- `Read auto_pm/core/project_service.py:319-335`

**实测证据**：

`auto_pm/core/project_service.py` L319-335：
```python
def search_projects(self, keyword: str) -> list[ProjectInfo]:
    """关键字搜索项目（匹配项目编号/名称/描述）..."""
    keyword_lower = keyword.lower()
    all_projects = self.list_projects()   # ← 全量文件系统扫描，无缓存优先
    return [
        p for p in all_projects
        if keyword_lower in p.project_id.lower()
        or keyword_lower in p.name.lower()
        or keyword_lower in p.description.lower()
    ]
```

**实测状态**：**存在**

**与 Claude-result 声明的对照**：
- ✅ 直接调 `list_projects()`（L329）确认，无 `list_projects_cached()` 优先路径。
- ✅ 行号 L319-335 准确。
- ✅ 与 `get_project()` 已实现 DB 缓存优先形成对比的判断成立。

---

### 问题 12：mypy 遗留 24 errors

**问题描述**：据 CHANGELOG 0.9.1，`mypy auto_pm/` 仍有 24 errors in 8 files，为 type-arg/attr-defined/union-attr/unreachable 等类型注解问题。

**实测方法**：
- 激活 venv：`& "c:\Users\fubai\Desktop\My_Workspace\.venv\Scripts\Activate.ps1"`
- 运行：`mypy auto_pm/`

**实测证据**：

mypy 实际输出（exit code 1）：
```
auto_pm\ui\qml\models\change_list_model.py:71:13: error: Statement is unreachable  [unreachable]
auto_pm\application\delivery_facade.py:124:17: error: Statement is unreachable  [unreachable]
auto_pm\application\delivery_facade.py:141:17: error: Statement is unreachable  [unreachable]
auto_pm\application\delivery_facade.py:157:17: error: Statement is unreachable  [unreachable]
auto_pm\application\delivery_facade.py:175:17: error: Statement is unreachable  [unreachable]
Found 5 errors in 2 files (checked 125 source files)
```

**实测状态**：**失真**

**与 Claude-result 声明的对照**：
- ❌ **"24 errors in 8 files"严重高估**：实测仅 **5 errors in 2 files**（高估约 5 倍）。
- ❌ 错误类型声明不准确：实测全部为 `unreachable` 一种类型，原报告声称的 `type-arg` / `attr-defined` / `union-attr` 实际未出现。
- ✅ "不影响运行时"判断成立（unreachable 是死代码警告）。
- 错误分布：`change_list_model.py` 1 处 + `delivery_facade.py` 4 处（均为 `data = {"raw": data}` 死分支）。

---

## 二、总结优先级排序

| 编号 | 问题 | 实测状态 | 原报告声明准确性 | 优先级 | 工作量 |
|------|------|----------|------------------|--------|--------|
| #1 | `except Exception` 70 处（frontmatter_svc 非静默） | **失真** | 数量准确，"静默吞没"定性错误 | 🟡 P3 | 小（仅 2 处补 `as e`） |
| #2 | `_get_project_info()` 两处克隆 | **存在** | 准确 | 🟡 P2 | 小（30 min） |
| #3 | `FacadeRegistry` `dict[str, Any]` | **存在** | 准确 | 🟡 P2 | 小（30 min） |
| #4 | TODO 未闭环（实测 16 处非 7 处） | **失真** | 数量低估，substance_checker 误判 | 🟡 P3 | 中（需评估） |
| #5 | `change/models.py` 命名歧义 | **存在** | 准确 | 🟢 P3 | 小（30 min） |
| #6 | ProjectInfo 原地修改（实测 25 处非 15 处） | **失真** | 数量低估 | 🟡 P3 | 中 |
| #7 | Ruff 规则集偏保守 | **存在** | 准确 | 🟢 P3 | 小 |
| #8 | `AutoPmConfig` 功能单薄 | **存在** | 准确 | 🟢 P3 | 中 |
| #9 | `os.path`/`pathlib` 混用 | **存在** | 准确（分布略有补充） | 🟢 P4 | 大 |
| #10 | 7 个向后兼容委托方法 | **存在** | 准确 | 🟢 P4 | 小 |
| #11 | `search_projects()` 未走缓存 | **存在** | 准确 | 🟡 P2 | 小（15 min） |
| #12 | mypy errors（实测 5 处非 24 处） | **失真** | 严重高估约 5 倍 | 🟢 P4 | 小（5 处 unreachable） |

---

## 三、实测状态统计

| 实测状态 | 数量 | 编号 |
|----------|------|------|
| **存在**（与原报告一致） | 7 | #2 #3 #5 #7 #8 #9 #10 #11 |
| **失真**（数量/性质与实测不符） | 4 | #1 #4 #6 #12 |
| **已修复** | 0 | — |
| **部分修复** | 0 | — |

**失真项明细**：
- #1：`except Exception` 数量准确，但 frontmatter_svc.py 2 处被误判为"静默吞没"（实际有 `log.warning`）。
- #4：TODO 实测 16 处（原报告标题"7 处"，表格求和 13），且 substance_checker.py 的 `"TODO"` 是字符串字面量非注释。
- #6：ProjectInfo 原地修改实测 25 处（原报告"~15 处"）。
- #12：mypy 实测 5 errors in 2 files（原报告"24 errors in 8 files"，高估约 5 倍）。

---

## 四、后续建议

### 阶段 1：快速清理（1-2 天，工作量小，收益高）

| 任务 | 编号 | 涉及文件 | 预估 |
|------|------|----------|------|
| 消除 `_get_project_info()` 两处克隆，改为调 `get_project()` | #2 | system_facade.py + delivery_facade.py | 30 min |
| `search_projects()` 优先走 `list_projects_cached()` | #11 | core/project_service.py | 15 min |
| `FacadeRegistry.initialize()` 改用 `TypedDict` | #3 | ui/registry.py | 30 min |
| frontmatter_svc.py 2 处 `except Exception:` 补 `as e` 绑定 | #1 | spec/services/frontmatter_svc.py | 10 min |
| 重命名 `change/models.py` → `change/constants.py` | #5 | change/models.py + 导入方 | 30 min |
| mypy 5 处 unreachable 死分支清理（delivery_facade 4 处 + change_list_model 1 处） | #12 | delivery_facade.py + change_list_model.py | 30 min |

### 阶段 2：质量加固（3-5 天）

| 任务 | 编号 | 说明 |
|------|------|------|
| TODO 项盘点与闭环（16 处逐一评估，转变更单或移除） | #4 | 区分 M3/M4/M5 路线图项与废弃项 |
| Ruff 规则扩展（逐步启用 B/SIM/UP/RUF） | #7 | 修复新发现的问题 |
| `AutoPmConfig` 扩展（集中 scan_depth/db_dir/backupCount） | #8 | 替换分散硬编码 |
| `ProjectInfo` 原地修改改为 `model_copy(update={...})`（25 处） | #6 | 为未来 frozen=True 铺路 |

### 阶段 3：功能扩展（M4/M5 路线图）

| 任务 | 关联 |
|------|------|
| WorkbenchFacade health_status/document_status/vartable_status/pending_actions 接入 | TODO #4 |
| QML Bridge 接入变更创建/流转/编辑 UI | TODO #4 |
| QML Bridge 接入资产刷新/模板应用 | TODO #4 |
| 评估并清理 5 个无外部调用的向后兼容委托方法 | #10 |

### 阶段 4：长期渐进

| 任务 | 编号 | 说明 |
|------|------|------|
| `pathlib.Path` 统一迁移（新代码优先，旧代码逐步） | #9 | 风格统一，工作量大 |
| PM_SESSION 147KB 归档拆分 | — | 偏大问题 |

---

## 五、关键结论

1. **原报告整体可信度**：12 项中 7 项与实测一致，4 项失真，失真率 33%。失真项集中在"数量统计"（#4 TODO、#6 原地修改、#12 mypy）和"性质判断"（#1 静默吞没）。

2. **最严重失真**：#12 mypy errors（声称 24 实测 5，高估 5 倍）和 #1 frontmatter_svc"静默吞没"（实际有日志记录）。

3. **真正需立即修复的 Quick Wins**（4 项，共约 1.5 小时）：
   - #2 消除 `_get_project_info()` 克隆（30 min）
   - #11 `search_projects()` 走缓存（15 min）
   - #12 mypy 5 处 unreachable 清理（30 min）
   - #1 frontmatter_svc 补 `as e` 绑定（10 min）

4. **项目健康度**：V0.9.1 代码质量良好，1115 passed / ruff 0 errors / mypy 仅 5 处 unreachable（非类型错误），剩余问题多为代码风格与可维护性优化，无阻断性缺陷。
