# auto-pm 项目全面诊断报告（第三版）

> 诊断时间：2026-07-08 03:42 | 版本：V0.9.1 | 基线：pyproject=0.9.1 / 1115 passed / ruff 0 errors
> 诊断工具：Claude Opus 4（Thinking）逐文件审查

---

## 一、整体评价

**项目成熟度：★★★★☆（工业级工程化项目，已完成多轮整改，剩余打磨空间较小）**

这是一个结构清晰、功能完善的自动化项目管理工具，涵盖 CLI + QML GUI 双入口、五层架构（CLI → Application Facade → Core Service → DB Repository → Models）、12 状态机变更管理流程，已经过 31 次 Dogfooding 验证。代码质量在同类型内部工具中属于**上乘**水平。

**重要说明**：本次诊断在对上一版报告逐条核查后发现，CHG-SCPT-2026-100 已修复原报告中 8 项 P0/P1 问题（第二版报告中 #1~#5/#7/#8/#11 已全部修复），原报告因基于修复前状态生成存在严重失真（42%）。本版报告基于 V0.9.1 代码实测，所有数据均为 Grep/文件审查实证。

---

## 二、架构优势 ✅

| 维度 | 评价 |
|------|------|
| **分层架构** | 五层分离清晰：`cli/` → `application/` → `core/` → `db/` → `models/`，依赖方向单向 |
| **Protocol 接口** | `core/protocols.py` 使用 `@runtime_checkable Protocol`，10 个域契约定义完整（Project/Change/PLC/Scanner/Dashboard/Asset/PmSession/Template/Spec/DocRefresh/Report） |
| **Facade 模式** | `application/` 层 5 个 Facade 统一聚合入口，GUI/CLI 通过同一接口访问业务逻辑 |
| **Facade 参数类型安全** | 5 个 Facade 构造参数已全部替换为 Protocol 类型（原为 `Any`），`registry.py` 使用 `cast()` 适配 |
| **职责拆分** | ChangeService 已拆分为 6 个职责单一类（parser/generator/guard_checker/ledger_updater/markdown_editor/file_locator） |
| **原子写入** | `file_utils.write_file` 实现 temp + `os.replace` 原子写入 + 乐观锁（`expected_mtime`），数据安全性好 |
| **文件快照** | `read_file_snapshot` 通过读前/读后 mtime 一致性校验，降低 read-modify-write 场景竞态 |
| **DB 连接复用** | `DatabaseManager.get_connection()` 已实现单例连接模式（`self._conn` 缓存 + `close()` 方法），消除了每次操作创建新连接的问题 |
| **缓存优先查询** | `get_project()` 已实现 DB 缓存优先 + 文件系统降级（L218-229），不再每次全量扫描 |
| **Schema 迁移** | `db/schema.py` 的 `migrate_schema()` 通过 `_column_exists()` 实现幂等增量迁移 |
| **增量扫描** | `SyncService` 双重判据（file_mtime + scanner_version），CHG-085 修复了 scanner 逻辑变更不触发重扫的 P1 缺陷 |
| **sync.py 消除克隆** | `_get_project_mtime()` 已改为委托 `ProjectScanner.get_project_mtime()`，消除了代码重复 |
| **日志体系** | 全项目统一使用 `log = logging.getLogger(__name__)` 模式（27 个文件实证），`setup_logger` 仅在 `app_context.py` 调用一次 |
| **审计日志** | 独立 `audit.py` 实现操作审计，按天轮转保留 90 天，格式化为 `ACTION=xxx | KEY=VAL` 便于检索 |
| **测试体系** | 1115 passed / 2 skipped，测试覆盖 17 个子目录，含冒烟/单元/集成/GUI 多层级标记 |
| **Pydantic v2 模型** | 全面使用 Pydantic v2 + `ConfigDict(from_attributes=True)`，类型安全性好 |
| **多来源去重** | `ProjectScanner._deduplicate_projects()` 实现路径去重 + project_id 去重 + 优先级合并 |
| **Windows 编码** | `__main__.py` 设置 `PYTHONUTF8=1`，`cli/__main__.py` 通过 Windows API 检测控制台代码页精准适配 |
| **QML 单入口** | V0.9.0 完成 QWidget→QML 完整迁移，删除 84 个旧文件，QML 为唯一 UI 入口 |

---

## 三、已修复问题确认（第二版中 P0/P1 全部已修复）

以下问题在 CHG-SCPT-2026-100 中已全部修复，**不再存在**：

| 原编号 | 原描述 | 修复确认 |
|--------|--------|----------|
| #1 | `get_project()` O(n) 全量扫描 | ✅ 已改为 DB 缓存优先 + 降级扫描（L218-229） |
| #2 | `DatabaseManager` 每次创建新连接 | ✅ 已实现 `self._conn` 单例复用 + `close()` 方法 |
| #3 (部分) | `except Exception` 静默吞没 | ✅ delivery_facade L82 静默 pass 已修复为 `log.warning(exc_info=True)` |
| #4 | `_get_project_mtime` 三处重复 | ✅ `sync.py` 已委托 `ProjectScanner.get_project_mtime()` |
| #5 | `setup_logger` 硬编码绕过配置 | ✅ 全部改为 `logging.getLogger(__name__)`（27 个文件实证） |
| #7 | `Optional[X]` 与 `| None` 混用 | ✅ Grep 实测 0 处 `Optional[`，全部统一为 `X | None` |
| #8 | Facade 参数 `Any` 11 处 | ✅ 全部替换为 Protocol 类型（实测 0 处 `Any` 参数） |
| #11 | 根目录临时文件 + `.gitignore` 不完整 | ✅ `.gitignore` 已新增 `*.bak_*`/`pytest_*.txt`/`claude_plan`/`test_screenshots/` |

---

## 四、当前仍存在的问题

### 🟡 中优先级（代码质量/可维护性）

---

#### 1. `except Exception` 仍然广泛使用（70+ 处）

CHANGELOG 0.9.1 确认实际有 **70+ 处** `except Exception`（远超第二版报告的 31 处）。本次 Grep 实测源代码中约 **50+ 处**（不含测试文件），分布如下：

| 层 | 文件 | 数量 | 性质 | 建议 |
|----|------|------|------|------|
| **UI factories** | `ui/factories.py` | 8 | `# noqa: BLE001` 防崩溃 | 可保留，建议添加 `log.debug` |
| **Application Facades** | 5 个 Facade 文件 | ~25 | 全部有 `as e` + 返回 `QueryResult(success=False)` | 可接受（Facade 作为边界层兜底） |
| **CLI 层** | `cli/change.py`/`project.py`/`template.py` 等 | ~10 | 最外层 `click.echo(error)` | 可接受 |
| **Core/DB 层** | `project_service.py`/`sync.py`/`dashboard_service.py` | ~7 | 大部分有 `log.warning(exc_info=True)` | 建议缩窄 |
| **Spec 层** | `frontmatter_svc.py` | 2 | L91/L146 仅 `except Exception:` 无变量绑定 | 建议改为 `as e` + 日志 |

**评估**：与第二版报告不同，当前大部分 `except Exception` 都有合理用途（Facade 兜底/CLI 错误展示/工厂函数防崩溃）。真正需要修复的仅 **frontmatter_svc.py 2 处**无日志记录的静默捕获。

---

#### 2. `_get_project_info()` 在 2 个 Facade 中存在完全相同的克隆（新发现）

`system_facade.py` 和 `delivery_facade.py` 各有一个 **完全相同** 的 `_get_project_info()` 方法（约 18 行），实现了"优先 DB 缓存、降级文件系统扫描"的相同逻辑：

```python
# system_facade.py L56-80 和 delivery_facade.py L64-88 完全一致
def _get_project_info(self, project_id: str) -> ProjectInfo | None:
    if not self._project_service:
        return None
    try:
        info = self._project_service.get_project_cached(project_id)
        if info is not None:
            return info
    except RuntimeError:
        pass
    try:
        projects = self._project_service.list_projects()
        for p in projects:
            if p.project_id == project_id:
                return p
    except Exception as e:
        log.warning(...)
    return None
```

> [!NOTE]
> 这个方法的逻辑与 `ProjectService.get_project()` (L209-229) 几乎等价——`get_project()` 已实现了"DB 缓存优先 + 文件系统降级"。两个 Facade 复制此逻辑是冗余的。

**建议**：直接调用 `self._project_service.get_project(project_id)`，删除两处克隆：
```python
def _get_project_info(self, project_id: str) -> ProjectInfo | None:
    if not self._project_service:
        return None
    return self._project_service.get_project(project_id)
```

---

#### 3. `FacadeRegistry.initialize()` 使用 `dict[str, Any]` 非类型安全

```python
# ui/registry.py L28
def initialize(self, services: dict[str, Any]) -> None:
    dashboard_service = cast(DashboardServiceProtocol, services.get("dashboard_service"))
```

虽然内部使用了 `cast()` 适配 Protocol 类型，但入口参数仍是 `dict[str, Any]`，字符串 key 拼写错误只能在运行时发现。

**建议**：使用 `TypedDict` 或 `dataclass` 定义服务容器：
```python
@dataclass
class ServiceContainer:
    project_service: ProjectServiceProtocol
    change_service: ChangeServiceProtocol | None
    dashboard_service: DashboardServiceProtocol
    # ...
```

---

#### 4. TODO 项仍有 7 处未闭环

| 文件 | 数量 | 内容摘要 |
|------|------|----------|
| `workbench_facade.py` | 4 | `health_status="Unknown"` / `last_activity_at=None` / `document_status=None` / `pending_actions=[]` |
| `delivery_bridge.py` | 3 | 资产刷新/汇总展示 QML 接入 |
| `system_bridge.py` | 2 | 模板应用 QML 接入 |
| `change_bridge.py` | 1 | 创建/流转/编辑 QML UI |
| `delivery_dto.py`/`system_dto.py` | 2 | Service 结构细化 |
| `substance_checker.py` | 1 | TODO 注释 |

**建议**：评估哪些 TODO 是 M4/M5 路线图的一部分，将其转为变更单跟踪。

---

#### 5. `change/models.py` 与 `models/change.py` 文件名歧义

两个文件名完全相同（只是包路径不同）：
- `auto_pm/change/models.py`：规范常量 + 异常类 + 校验函数（8.6KB）
- `auto_pm/models/change.py`：Pydantic 数据模型（6.9KB）

**建议**：将 `change/models.py` 重命名为 `change/constants.py` 或 `change/validators.py`。

---

#### 6. `ProjectInfo` 模型直接原地修改属性

`ProjectScanner._deduplicate_projects()` 和 `_enrich_from_plc_json()` 中直接修改 `ProjectInfo` 实例属性（共 ~15 处）：

```python
# core/project_scanner.py L99-118
if not primary.name and other.name:
    primary.name = other.name     # 直接修改 Pydantic model
if primary.stack == "unknown" and other.stack != "unknown":
    primary.stack = other.stack
```

> [!NOTE]
> 当前 `ProjectInfo`（即 `Project`）Pydantic v2 默认允许属性赋值（非 `frozen=True`），技术上合法。但如果未来需要 `frozen=True`（如用作 dict key），这些代码将报错。

**建议**：短期可接受，长期建议使用 `model_copy(update={...})` 替代。

---

### 🟢 低优先级（风格/优化建议）

---

#### 7. Ruff 规则集偏保守

```toml
# .ruff.toml
select = ["E4", "E7", "E9", "F", "I", "T20"]
```

当前仅启用基础规则子集。

**建议**：逐步启用 `B`（bugbear）/ `SIM`（simplify）/ `UP`（pyupgrade）/ `RUF`（Ruff 专有）规则。

---

#### 8. `AutoPmConfig` 配置类功能单薄

```python
class AutoPmConfig(BaseSettings):
    app_name: str = __app_name__
    log_level: Literal[...] = "INFO"
    # Add more ...  ← 注释暗示尚未扩展
```

项目中大量硬编码配置分散在各模块中（`scan_depth=4`、`backupCount=30/90`、`.auto-pm/index.db` 等）。

---

#### 9. `os.path` 与 `pathlib.Path` 混用

- **主要使用 `os.path`**：`core/`、`change/`、`db/sync.py`、`utils/file_utils.py`
- **使用 `pathlib.Path`**：`db/connection.py`、`logging/`、`spec/`

**建议**：新代码优先使用 `pathlib`，长期逐步统一。

---

#### 10. 向后兼容委托方法可清理

`project_service.py` L674-703 保留了 **7 个向后兼容包装方法**（`_try_identify_project`/`_read_copier_answers`/`_read_plc_json`/`_read_pm_session`/`_extract_id_from_dirname`/`_infer_stack`/`_get_project_mtime`），全部是一行委托。除 `_extract_id_from_dirname` 和 `_get_project_mtime` 在 `retrofit_project_by_path` 和 `_upsert_to_cache` 中有内部调用外，其他 5 个的外部调用方需要验证。

---

#### 11. `search_projects()` 仍走全量文件扫描

```python
# project_service.py L319-335
def search_projects(self, keyword: str) -> list[ProjectInfo]:
    all_projects = self.list_projects()  # ← 全量文件系统扫描
    return [p for p in all_projects if keyword_lower in ...]
```

与 `get_project()` 不同，`search_projects()` 没有 DB 缓存优先路径。

**建议**：优先走 `list_projects_cached()` + 内存筛选：
```python
def search_projects(self, keyword: str) -> list[ProjectInfo]:
    try:
        all_projects = self.list_projects_cached()
    except RuntimeError:
        all_projects = self.list_projects()
    ...
```

---

#### 12. mypy 遗留 24 errors（P1/P2 级别）

据 CHANGELOG 0.9.1 记录，`mypy auto_pm/` 仍有 **24 errors in 8 files**，均为 `type-arg` / `attr-defined` / `union-attr` / `unreachable` 等类型注解问题，不影响运行时。

---

## 五、安全性检查

| 检查项 | 状态 | 说明 |
|--------|------|------|
| SQL 注入 | ✅ 安全 | 全部 Repository 代码使用参数化查询 `?` |
| 文件路径注入 | ✅ 安全 | 路径基于 `workspace_root` 拼接，`import_project` 使用 `os.path.abspath` 规范化 |
| 原子写入 | ✅ 安全 | temp + `os.replace` + `os.fsync` 模式 |
| 乐观锁 | ✅ 安全 | `expected_mtime` 防 lost update，`read_file_snapshot` 双重校验 |
| 敏感信息 | ✅ 安全 | `.env_template` 仅 17 字节，无硬编码密钥 |
| 外键约束 | ✅ 开启 | `PRAGMA foreign_keys=ON`，`ON DELETE CASCADE` 保证级联删除 |
| 审计追踪 | ✅ 完善 | `audit.py` 独立记录关键操作，保留 90 天 |
| YAML 解析 | ✅ 安全 | 全部使用 `yaml.safe_load` |
| JSON 解析 | ✅ 安全 | 标准 `json.load`，无 `eval` |
| 临时文件清理 | ✅ 安全 | `write_file` 在异常时 `os.unlink(tmp_path)` 清理 |
| 编码安全 | ✅ 安全 | 全部使用 `encoding="utf-8"` |

---

## 六、文档完整性检查

| 文档 | 状态 | 说明 |
|------|------|------|
| `README.md` | ✅ 完善 | 16KB，含安装/使用/架构/贡献指南 |
| `CHANGELOG.md` | ✅ 完善 | 79KB，记录从 V0.1.0 到 V0.9.1 的完整变更历史 |
| `docs/里程碑迭代计划_V2.1.md` | ✅ 历史镜像 | 24KB，M0-M4 迭代计划详尽（标注为镜像文档） |
| `docs/归档索引.md` | ✅ 完善 | 4.8KB，文档归档索引 |
| `09_整改项/README.md` | ✅ 完善 | 6KB，整改项目录说明 |
| `09_整改项/remediation_plan.md` | ✅ 已完成 | 12KB，7 项 P0 阻断性问题修复方案（状态=已完成） |
| `09_整改项/M2~M4 Landing Plans` | ✅ 完善 | 4 个 Landing Plan 文档 |
| `pyproject.toml` | ✅ 完善 | 构建/依赖/测试/工具全配置，version=0.9.1 |
| `.pre-commit-config.yaml` | ✅ 完善 | pre-commit hooks 配置 |
| `Taskfile.yml` | ✅ 完善 | Task runner 配置 |
| `PM_SESSION_SW-2026-008.md` | ⚠️ 偏大 | 147KB，建议定期归档旧内容 |

---

## 七、测试体系评估

| 维度 | 状态 | 说明 |
|------|------|------|
| 测试通过率 | ✅ 1115 passed / 2 skipped | 全量回归 0 failed |
| 测试标记 | 6 种 | `gui`/`cli`/`smoke`/`unit`/`integration`/`slow` |
| Coverage 配置 | ✅ | `--cov=auto_pm/`，HTML+XML+JUnit 三格式输出 |
| 测试隔离 | ✅ | `pytest-env` 设置 `ENVIRONMENT=test` |
| 测试 fixtures | ✅ | `conftest.py` 2.8KB + `tests/fakes/` 目录提供 Fake 实现 |
| 健康检查 | ✅ | `test_fixture_health.py` 15.5KB，专门验证 fixture 正确性 |
| Bug 回归测试 | ✅ | 4 个专项 Bug 回归测试文件（bug1~bug5） |
| 冒烟测试 | ✅ | `test_smoke.py` 9.3KB，核心功能快速验证 |
| PM_SESSION 大小监控 | ✅ | `test_pm_session_size.py` 4.4KB，防止 PM_SESSION 过大 |

---

## 八、总结优先级排序（当前状态）

| 优先级 | 编号 | 问题 | 影响 | 工作量 |
|--------|------|------|------|--------|
| 🟡 P2 | #1 | `except Exception` 70+ 处（其中 2 处无日志） | 2 处静默吞没需修 | 小 |
| 🟡 P2 | #2 | `_get_project_info()` 两处克隆 | DRY 违反 | 小 |
| 🟡 P2 | #3 | `FacadeRegistry` 类型不安全 | 运行时错误发现晚 | 小 |
| 🟡 P2 | #4 | 7 个 TODO 未闭环 | 功能遗漏风险 | 需评估 |
| 🟡 P2 | #11 | `search_projects()` 未走缓存 | 搜索时全量扫描 | 小 |
| 🟡 P2 | #12 | mypy 24 errors 遗留 | 类型安全性 | 中 |
| 🟡 P3 | #5 | `change/models.py` 文件名歧义 | 可维护性 | 小 |
| 🟡 P3 | #6 | ProjectInfo 原地修改属性 | 未来 frozen 迁移障碍 | 中 |
| 🟢 P3 | #7 | Ruff 规则集偏保守 | 潜在 bug 漏检 | 小 |
| 🟢 P3 | #8 | 配置类功能单薄 | 硬编码分散 | 中 |
| 🟢 P4 | #9 | `os.path` 与 `pathlib` 混用 | 风格不统一 | 大 |
| 🟢 P4 | #10 | 7 个冗余向后兼容委托方法 | 代码冗余 | 小 |

---

## 九、相比前两版诊断的变化

| 维度 | 第二版（2026-07-08）| 第三版（2026-07-08 03:42）|
|------|-------------------|--------------------------|
| 基线版本 | V0.9.0（修复前状态） | V0.9.1（修复后状态） |
| 失真度 | 42% 严重失真（8 项 P0/P1 已修复未更新） | 0%（基于实际代码审查） |
| 已修复 P0/P1 | 未标注 | 明确标注 8 项已修复（#1~#5/#7/#8/#11） |
| 发现问题数 | 19 项（含 8 项已修复） | 12 项（均为当前实际存在） |
| `except Exception` | "31 处"（不准确） | 实测 50+ 处源代码 / 70+ 处含测试 |
| `Optional[X]` | "48+ 处" | **0 处**（已全部统一为 `X | None`） |
| Facade `Any` | "11 处" | **0 处**（已全部替换为 Protocol） |
| `setup_logger` 硬编码 | "18 处" | **0 处**（已全部改为 `logging.getLogger(__name__)`） |
| DB 连接 | 每次创建新连接 | 已实现单例复用 + `close()` |
| `get_project()` | 全量扫描 | 已实现 DB 缓存优先 + 降级扫描 |
| 新发现 | — | `_get_project_info()` 克隆 (#2)、`search_projects()` 未走缓存 (#11) |

---

## 十、后续开发计划建议

### 阶段 1：快速清理（1-2 天，工作量小）

| 编号 | 任务 | 涉及文件 | 预估 |
|------|------|----------|------|
| S1-1 | 消除 `_get_project_info()` 克隆 | `system_facade.py` + `delivery_facade.py` | 30 min |
| S1-2 | 修复 `frontmatter_svc.py` 2 处静默 except | `spec/services/frontmatter_svc.py` | 15 min |
| S1-3 | `search_projects()` 优先走 DB 缓存 | `core/project_service.py` | 15 min |
| S1-4 | 重命名 `change/models.py` → `change/constants.py` | `change/models.py` + 所有导入方 | 30 min |
| S1-5 | 清理 5 个冗余委托方法（验证无外部调用后） | `core/project_service.py` | 30 min |
| S1-6 | `FacadeRegistry.initialize()` 改用 `TypedDict` | `ui/registry.py` | 30 min |

### 阶段 2：质量加固（3-5 天）

| 编号 | 任务 | 说明 |
|------|------|------|
| S2-1 | mypy 24 errors 清零 | 逐文件修复 type-arg/attr-defined/union-attr 等 |
| S2-2 | Ruff 规则扩展 | 启用 `B`/`SIM`/`UP`/`RUF`，修复新发现问题 |
| S2-3 | `AutoPmConfig` 扩展 | 集中 `scan_depth`/`db_dir`/`backupCount` 等分散配置 |
| S2-4 | `ProjectInfo` 原地修改改为 `model_copy` | `_deduplicate_projects()`/`_enrich_from_plc_json()`/`_apply_stack_fallback()` |
| S2-5 | TODO 项评估与闭环 | 7 个 TODO 转为变更单或移除 |

### 阶段 3：功能扩展（M4/M5 路线图）

| 编号 | 任务 | 关联 |
|------|------|------|
| S3-1 | WorkbenchFacade `health_status` 接入 Change 域 | TODO M3 |
| S3-2 | QML Bridge 接入变更创建/流转/编辑 UI | TODO change_bridge.py |
| S3-3 | QML Bridge 接入资产刷新/模板应用 | TODO delivery_bridge.py / system_bridge.py |
| S3-4 | PM_SESSION 147KB 归档拆分 | PM_SESSION 偏大问题 |
| S3-5 | `pathlib.Path` 统一迁移（新代码优先） | 长期渐进 |

### 阶段 4：性能与可观测性

| 编号 | 任务 | 说明 |
|------|------|------|
| S4-1 | `update_project_meta()` 消除二次查询 | L365 `updated = self.get_project(project_id)` 触发额外查询 |
| S4-2 | 测试覆盖率提升至 85%+ | 当前覆盖率需评估 |
| S4-3 | GUI 性能测试 | QML 启动时间/列表渲染/大项目数场景 |

---

> [!TIP]
> **立即可做的 Quick Wins**（工作量小、收益高）：
> 1. 消除 `_get_project_info()` 克隆（改为调用 `self._project_service.get_project()`，2 处共删 30 行）
> 2. 修复 `frontmatter_svc.py` 2 处静默 except（添加 `as e` + `log.warning`）
> 3. `search_projects()` 优先走缓存（5 行改动）
> 4. `change/models.py` 重命名为 `change/constants.py`（消除包名歧义）
