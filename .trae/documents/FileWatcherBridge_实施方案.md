注意必须走变更流程，dogfood。

# FileWatcherBridge 实施方案：CLI 写文件后 GUI 自动刷新缓存

## Context（背景与动机）

auto-pm 有两条使用路径共享同一套 Service + 文件系统 + SQLite DB 缓存：

* **GUI 路径**（电气工程师日常操作）：QML 驾驶舱 → Bridge → Facade → Service → **DB 缓存**

* **CLI 路径**（AI 技能执行）：`auto-pm` 命令 → Service → **文件系统**（不碰 DB）

**核心矛盾**：DB 是缓存、文件是真源（[sync.py:16](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/db/sync.py#L16)），但 CLI 写文件不通知 DB 刷新。证据：[app\_context.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/app_context.py) 不持有 DB，cli/change.py 5 处、cli/project.py 12/13 处 Service 构造均无 db 参数。

**后果**：AI 技能 CLI 创建/流转变更单后，GUI Dashboard（依赖 DB）看不到最新状态，必须手动 sync 或重启 GUI。相当于 HMI 画面没接 PLC 变量变化信号——工程师现场改了程序，操作员画面还是旧值。

**本方案目标**：在 GUI 层新增 FileWatcherBridge，监听业务文件变化 → 1s 去抖 → 后台子线程 sync → Signal 通知 QML 刷新。后端 Service/CLI 零改动。

## 设计决策（已与用户敲定）

| 决策         | 结论                                                                                                                                                                                                                        |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 监听范围       | 业务文件全监听，排除纯噪声目录（.git/.venv/__pycache__/各类 cache/编译产物等）                                                                                                                                                                    |
| 去抖         | 1s QTimer singleShot                                                                                                                                                                                                      |
| 触发         | 启动 GUI 时启动 Watcher + sync 一次（复用现有 [qml\_main\_window.py:99](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/ui/qml_main_window.py#L99) 启动 sync） |
| 同步按钮       | 全局工具栏常驻（main.qml header L82-188），每页可点，可手动开关 Watcher，带完成反馈                                                                                                                                                                 |
| sync 线程    | QRunnable + QThreadPool 子线程（复用 [modbus\_bridge.py:37-53](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/modbus/modbus_bridge.py#L37-L53) 先例）   |
| refresh 策略 | sync 后全部 Bridge refresh（changeBridge + workbenchBridge）                                                                                                                                                                   |
| 兜底         | 本地为主；网盘轮询后续迭代再加                                                                                                                                                                                                           |

## 架构设计

```
QFileSystemWatcher（监听业务目录）
   ↓ fileChanged / directoryChanged
QTimer 1s singleShot 去抖（restart 合并多次变化）
   ↓ timeout
SyncWorker(QRunnable) → QThreadPool 后台
   ↓ 自建 DatabaseManager + ProjectService（线程亲和性隔离）
   ↓ project_service.sync_to_cache()
   ↓ emit syncFinished(projects, changes, ms)
主线程 _on_sync_finished()
   ↓ changeBridge.refreshChanges() + workbenchBridge.refreshProjects()
   ↓ refreshPaths() diff 补 addPath（捕获新建子目录）
   ↓ Signal → QML 画面自动刷新
```

## 关键技术风险与缓解

### 风险 1：SQLite 线程亲和性（SHOWSTOPPER，已确认）

* **问题**：[connection.py:54](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/db/connection.py#L54) `sqlite3.connect()` 默认 `check_same_thread=True`，主线程连接不能在 worker 线程用

* **缓解**：SyncWorker 在 worker 线程内自建 `DatabaseManager(workspace_root)` + `ProjectService`，完成后 `db.close()`。WAL 模式（[connection.py:56](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/db/connection.py#L56)）支持多连接并发，主线程下次查询能读到 worker 写入的数据

### 风险 2：QFileSystemWatcher 不自动监听新建子目录

* **问题**：Qt 后端非递归，新建子目录不会自动纳入监听

* **缓解**：`directoryChanged` 信号也触发去抖 → sync 完成后调 `refreshPaths()` 做 diff（新扫描集 vs `watcher.directories()`），增量 addPath 新目录、removePath 消失目录

### 风险 3：sync 期间文件持续变化导致重复触发

* **缓解**：`_sync_in_progress` 标志位 + `_pending_sync` 累积标志。sync 进行中收到新变化设 `_pending_sync=True`，sync 完成后检查并补一次

### 风险 4：reload\_workspace 时旧 Watcher 信号泄漏

* **缓解**：清理顺序 `prepareForReload()`（removePaths + 停定时器 + `_reload_pending=True` 拒绝新 sync）→ 重建 Services → `rebuild(new_path)` 重新扫描 + `_reload_pending=False`

### 风险 5：大工作空间 addPath 阻塞

* **缓解**：`MAX_DIRECTORIES=5000` 硬上限，超限降级为精简模式（仅监听项目标志目录 + 变更单目录）。当前工作空间实测约 883 业务目录，远低于上限

## 文件清单

### 新增文件

1. **`auto_pm/ui/qml/bridges/file_watcher_bridge.py`** — FileWatcherBridge(QObject) + \_SyncWorker(QRunnable) + \_SyncWorkerSignals(QObject)

   * 核心类：`FileWatcherBridge`，持有 QFileSystemWatcher + QTimer(1s) + QThreadPool

   * Signals: `syncStarted()`, `syncFinished(int, int, int)`, `syncError(str)`, `watcherToggled(bool)`, `pathsRefreshed(int)`

   * Slots: `syncNow()`, `toggleWatcher(bool)`, `refreshPaths()`, `watchedDirectoryCount()`, `isWatcherEnabled()`, `lastSyncTime()`

   * 内部: `_scan_business_dirs()`（递归扫描+排除噪声）、`_refresh_paths_impl()`（diff 算法）、`_on_debounce_timeout()`（并发控制）、`prepareForReload()`/`rebuild(new_root)`

   * `_SyncWorker`: worker 线程内自建 DatabaseManager + ProjectService，调 `sync_to_cache()`，emit syncFinished

   * 噪声目录常量 `NOISE_DIRS`：.git/.venv/venv/__pycache__/.ruff\_cache/.mypy\_cache/.pytest\_cache/.hypothesis/node\_modules/.idea/.vscode/06\_交付物/06\_交付物打包/output/test\_screenshots/.auto-pm/dist/build/reports/htmlcov/coverage

2. **`tests/qml/test_file_watcher_bridge.py`** — 单元测试（\~8 用例）

   * test\_sync\_worker\_creates\_own\_db（线程亲和性验证）

   * test\_debounce\_coalesces\_events（去抖合并）

   * test\_concurrent\_sync\_blocked（并发控制）

   * test\_toggle\_watcher（开关）

   * test\_prepare\_for\_reload（reload 隔离）

   * test\_refresh\_paths\_diff（增量 addPath）

   * test\_noise\_dir\_excluded（噪声过滤）

   * test\_sync\_finished\_emits\_counts（结果信号）

3. **`scripts/gui_file_watcher_test.py`** — GUI 可见模式集成测试（参考 gui\_smoke\_test.py，禁用 offscreen）

### 修改文件

1. **`auto_pm/ui/qml_main_window.py`**

   * L94 后实例化 `FileWatcherBridge(workspace_root)`

   * L99 启动 sync 后调 `file_watcher_bridge.refreshPaths()` + `toggleWatcher(True)`

   * L293 后 `setContextProperty("fileWatcherBridge", file_watcher_bridge)`

   * reload\_workspace 回调(L188-268)：开头调 `fileWatcherBridge.prepareForReload()`，重建 Services 后调 `fileWatcherBridge.rebuild(new_path)` + `syncNow()`

2. **`auto_pm/ui/qml/main.qml`** — header(L82-188) 的"🔄 刷新"按钮(L158)旁新增：

   * "🔄 同步" PrimaryButton → `fileWatcherBridge.syncNow()`

   * Switch "自动同步" → `fileWatcherBridge.toggleWatcher(checked)`

   * 同步状态文字（常驻）：`fileWatcherBridge.isWatcherEnabled ? "监听中 (N 目录)" : "已暂停"` + lastSyncTime

   * LoadingOverlay（全屏覆盖，syncStarted 显示/syncFinished 隐藏）

   * Connections：`onSyncFinished` → `changeBridge.refreshChanges()` + `workbenchBridge.refreshProjects()` + 更新状态文字

3. **`auto_pm/ui/qml/bridges/workbench_bridge.py`** — createProject/importProject(L157-175) 成功后 emit 新信号 `projectCreated(str)`，QML 层 Connections 转发调 `fileWatcherBridge.refreshPaths()` + `syncNow()`（信号解耦，Bridge 间无直接依赖）

## 复用机制（零改动）

* `project_service.sync_to_cache()` → `SyncService.sync()` 增量同步（[sync.py](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/db/sync.py)）

* `changeBridge.refreshChanges()` / `workbenchBridge.refreshProjects()` refresh Signal

* `QRunnable + QThreadPool` 模式（[modbus\_bridge.py:37-53](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/modbus/modbus_bridge.py#L37-L53)）

* `QTimer` singleShot（[modbus\_bridge.py:259-266](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/modbus/modbus_bridge.py#L259-L266) 轮询定时器参考）

* `LoadingOverlay.qml`（active/message 属性，[components/LoadingOverlay.qml](file:///c:/Users/fubai/Desktop/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-008_auto-pm_自动化项目管理工具/auto_pm/ui/qml/components/LoadingOverlay.qml)）

* `PrimaryButton.qml` 按钮样式

## 实施步骤（4 个原子提交）

1. `feat(FileWatcherBridge): 新增 FileWatcherBridge 与 SyncWorker 实现文件监听同步`

   * 新增 file\_watcher\_bridge.py + tests/qml/test\_file\_watcher\_bridge.py
2. `feat(qml_main_window): 集成 FileWatcherBridge 注入与 reload 回调`

   * 修改 qml\_main\_window\.py
3. `feat(main.qml): header 新增同步按钮 Watcher 开关与状态反馈`

   * 修改 main.qml + workbench\_bridge.py（projectCreated 信号）
4. `test(FileWatcherBridge): 新增 GUI 可见模式集成测试脚本`

   * 新增 scripts/gui\_file\_watcher\_test.py

## 变更流程（CHG 单，auto-pm 自身 dogfooding）

按项目硬约束，auto-pm 自身代码修改必须走 CHG 流程：

* **单号**：CHG-SCPT-2026-141（接续最新 140，实际以 `auto-pm change create` 生成为准）

* **domain**：SCPT（Python 脚本）

* **nature**：OPT（优化改进）

* **impact\_scope**：SYSTEM（UI Bridge + DB + QML + Service 多模块联动）

* **创建命令**：

  ```powershell
  auto-pm -w "c:\Users\fubai\Desktop\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\02_在研项目\SW-2026-008_auto-pm_自动化项目管理工具" change create --project-id SW-2026-008 --title "新增 FileWatcherBridge 实现 CLI 写文件后 GUI 自动刷新缓存" --domain SCPT --nature OPT --background "CLI 写文件不通知 DB 刷新，GUI Dashboard 依赖 DB 缓存导致状态不一致" --necessity "消除 CLI 与 GUI 缓存鸿沟" --impact_scope SYSTEM --applicant "fubai"
  ```

* **闭环门禁**：ruff 0 + mypy 0 + pytest 全通（禁止 --allow-partial-verification）

* **闭环后**：`auto-pm -w "..." ledger reconcile SW-2026-008 --auto-fix` 台账对账

* **版本同步**：pyproject.toml 1.1.0→1.2.0 + CHANGELOG + PRD 路线图 + PM\_SESSION §2/§8

## 验证计划

### 单元测试

```powershell
# 激活 venv 后
python -m pytest tests/qml/test_file_watcher_bridge.py -v --tb=long
```

关键用例：SyncWorker 自建 DB 不抛线程异常、去抖合并多次事件、并发控制、reload 隔离。

### 回归测试

```powershell
python -m pytest tests/qml/ tests/db/test_sync.py -m "not slow" --tb=short
```

现有 138+ QML 测试不加载 main.qml（用 QQmlComponent 加载单组件），预期零影响。

### 三轨门禁

```powershell
ruff check auto_pm/ ; mypy auto_pm/ ; python -m pytest --no-cov -q
```

### GUI 可见模式集成测试（用户硬约束：禁用 offscreen）

```powershell
GUI_VISIBLE=1 python scripts/gui_file_watcher_test.py
```

步骤：启动 GUI 截图 → CLI 创建项目文件 → 等 2s → 截图验证 Dashboard 自动刷新 → 测试同步按钮反馈 → 测试 Watcher 开关。

### 端到端验证场景

1. GUI 启动，Dashboard 显示当前状态
2. 在 VS Code / 终端用 `auto-pm change create` 创建一个变更单（CLI 只写文件）
3. 等 2s（1s 去抖 + sync）
4. GUI Dashboard 自动显示新变更单，状态机更新——无需手动刷新
5. 点击"🔄 同步"按钮，观察 LoadingOverlay + 完成反馈
6. 关闭 Watcher 开关，CLI 再创建变更单，GUI 不自动刷新（验证开关生效）

