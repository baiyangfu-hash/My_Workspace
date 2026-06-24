# Changelog

本文件记录 auto-pm (SW-2026-008) 的所有变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [0.2.3] - 2026-06-24

### Added - V2.0.3: 规范漂移检测能力补齐
- auto_pm/plc/spec_snapshot.py（新增：Spec Snapshot 解析器，提供 `parse_spec_snapshot`/`load_spec_registry`/`compare_versions` 三个函数 + `DriftItem` dataclass，正则解析 PM_SESSION 中的 Spec Snapshot 表格，对比 spec_registry.json，判定 major/minor/patch 漂移级别）
- auto_pm/plc/checker.py（新增第 5 项检查 `Spec Snapshot`：在 PM_SESSION 检查通过后调用 `_check_spec_snapshot`，major 漂移=FAIL，minor/patch 漂移=WARN，无漂移=PASS；边界处理：PM_SESSION 缺失跳过、registry 缺失 WARN、Spec Snapshot 表格缺失 WARN）
- auto_pm/plc/repairer.py（新增 Spec Snapshot 自动修复：在 PM_SESSION 修复后调用 `_repair_spec_snapshot`，从 spec_registry.json 读取最新版本，正则替换 PM_SESSION 中 Spec Snapshot 表格的版本号列；dry_run 模式仅输出预览不修改文件）
- tests/plc/test_spec_snapshot.py（新增：18 个单元测试，覆盖标准表格解析/非标准格式/registry 加载/版本对比）
- tests/plc/test_checker_spec_snapshot.py（新增：5 个单元测试，覆盖无漂移 PASS/主版本 FAIL/次版本 WARN/Spec Snapshot 缺失 WARN/registry 缺失 WARN）
- tests/plc/test_repairer_spec_snapshot.py（新增：4 个单元测试，覆盖自动修复/dry-run 预览/无漂移跳过/Spec Snapshot 缺失跳过）

### Changed - V2.0.3: 版本号统一
- pyproject.toml version 0.2.1 → 0.2.3（跳过 0.2.2，因 CHANGELOG 已记录；与 CHANGELOG 最新条目一致）
- PRD 文档版本 V2.0.2 → V2.0.3（新增 V2.0.3 路线图章节）
- PM_SESSION §2 Current Focus 与 §8 Handoff Notes 版本号统一为 V0.2.3（原 §2=V2.0.1、§8=V0.2.2 矛盾）

### Added - V2.0.3: 文档同步
- 00_项目基础信息/005_变更记录_CHG.md（新增：V2.0.3 变更记录文件，记录本次迭代所有变更条目）
- .trae/rules/project-rule.md（新增"迭代文档同步规则（强制）"章节：进度基线强制/迭代后同步/版本号一致性/里程碑核查/变更记录 5 条强制规则）

### Fixed - V2.0.3: 工具能力缺口
- 修复 auto-pm `plc check` 无法检测规范版本漂移的问题（原仅检查项目结构，不对比 PM_SESSION Spec Snapshot 与 spec_registry.json）
- 修复 auto-pm `plc check --fix` 无法自动修复规范版本漂移的问题（原仅修复项目结构问题，不更新 Spec Snapshot 版本号）

## [0.2.2] - 2026-06-23

### Added - V0.2.2 Phase 3: P1 模板重构（3 套 PLC 模板）
- templates/plc-shared-library/（新增：公共库模板，对应 `--mode shared-library`，按功能块类型分目录 actuator/communication/convert/counter/edge/log/pulse/timer/types）
- templates/plc-test-suite/（新增：公共库验证模板，对应 `--mode test-suite`，精简结构 OB1/DB1/FB_/Test）
- templates/plc-standard-project/（重命名自 plc-standard，扩展目录结构，对应 `--mode standard-project`，含 LSP-907 标准目录 + 程序文档）
- auto_pm/core/constants.py（新增：集中定义 STACK_TEMPLATE_MAP/PLC_MODE_TEMPLATE_MAP/get_template_name/get_plc_template_name/业务线选项/技术栈选项/项目阶段选项，消除散落常量）

### Added - V0.2.2 Phase 2: P0 架构合规（PlcService 统一入口）
- auto_pm/plc/service.py（新增：PlcService 类，封装 PlcChecker/PlcRepairer/SubstanceChecker，提供 check/repair/standardize/check_substance/check_workspace 统一入口）
- CLI/UI 层通过 PlcService 操作 PLC 项目，不再直接访问 PlcChecker/PlcRepairer/SubstanceChecker（C-2/C-3 架构合规修复）

### Added - V0.2.2 Phase 5: P2 检查器增强（CLI 选项）
- cli/plc/__init__.py: `plc check` 新增 `--substance` 选项（文档实质化检查，V2.0.1-B）
- cli/plc/__init__.py: `plc check` 新增 `--fix` 选项（检查后自动修复非破坏性问题）
- cli/plc/__init__.py: `plc init` 新增 `--mode` 选项（shared-library/test-suite/standard-project）
- cli/project.py: `project create --stack plc` 新增 `--mode` 选项

### Added - V0.2.2 Phase 6: P2 测试补全
- tests/plc/test_cli.py: CLI 测试从 4 个扩展到 19 个（覆盖 --substance/--fix/--mode 选项 + retrofit PLC 标志文件补全 + 各命令正常/异常路径）（C-6）
- tests/plc/test_e2e.py: 新增端到端测试 3 个（plc init → check → repair 全流程，覆盖三种 mode）（H-9）
- tests/plc/test_templates.py: 新增模板测试 5 个（三套模板 copier copy 渲染验证 + 目录结构断言 + .plc.json 配置验证）

### Changed
- CLI 层 PLC 操作统一通过 PlcService 入口（原直接访问 PlcChecker/PlcRepairer）
- `project retrofit` 命令增强：对 PLC 项目自动补全 .plc.json/PM_SESSION/PRD 标志文件（通过 PlcService.repair 实现）（H-4/H-10）
- 模板映射从散落常量集中到 core/constants.py（STACK_TEMPLATE_MAP + PLC_MODE_TEMPLATE_MAP）
- STACK_TEMPLATE_MAP["plc"] 从 "plc-standard" 改为 "plc-standard-project"（模板重命名）
- PlcChecker.resolve_project_id 从私有方法 `_resolve_project_id` 提升为公共方法（H-1/H-2）
- PlcChecker 新增 syslib_fb 项目类型识别（目录名以 FB_ 开头且路径含 SysLib）

### Fixed - V0.2.2 Phase 1: Git 环境修复
- C-1: .gitignore 未排除 .auto-pm/ 缓存目录，导致 SQLite 缓存文件被误提交

### Fixed - V0.2.2 Phase 4: P1 SubstanceChecker 修复
- C-4: SubstanceChecker 字数统计语义错误（中英文混合统计，阈值不合理）→ 中文按字符数 ≥ 800，英文按词数 ≥ 1000，任一达标即 PASS
- H-6: SubstanceChecker 章节正则 `^##\s*` 误匹配 `###` 三级标题 → 改为 `^##(?!\s*#)\s*`（负向前瞻，排除 ### 及以上）
- H-7: SubstanceChecker 占位符检查仅计数无严重程度分级 → 密度 > 70% FAIL，30-70% WARN，≤ 30% PASS

### Fixed - V0.2.2 Phase 5: P2 检查器增强
- H-8: PlcChecker libraries 路径仅检查目录存在，未校验关键文件 → 新增深度校验（检查 timer/FB_TON.scl、counter/FB_CTD.scl、counter/FB_CTU.scl 等关键文件）
- H-1/H-2: PlcRepairer 访问 PlcChecker 私有方法 `_resolve_project_id` → 改为公共方法 `resolve_project_id`

## [0.2.1] - 2026-06-22

### Added - V2.0.1-A: 修复 site 模块 GBK 编码崩溃
- auto_pm/__main__.py（新增：设置 PYTHONUTF8=1 环境变量，防止子进程 site 模块 GBK 解码崩溃）
- auto_pm/cli/__main__.py（Windows GBK 终端编码兼容：sys.stdout 重新包装为 UTF-8）

### Added - V2.0.1-C: 042/016 规范对齐代码实施（19 项冲突修复）
- enums.py: ChangeStatus Literal 新增 `archived` 状态（C-01）
- models.py: STATUS_FLOW 新增 `completed→archived` 流转 + `archived` 终态；STATUS_LABELS 新增 `archived: "已归档"`（C-02/C-03）
- change_service.py: 5 处修改
  - `_check_transition_guards` 新增 `archived` 门禁（仅 completed 可归档）（C-05）
  - `transition_status` 新增 `archived` 分支（C-07）
  - `rejected→draft` 门禁要求附 comment（C-08）
  - `conditionally_approved→implementing` 门禁要求附 comment（C-10）
  - 审批环节名称从英文大写改为中文语义化标签（对齐 STATUS_LABELS）（C-11）
  - `_get_change_file_path` / `_find_change_file` 支持 PLC + Python 双路径搜索（C-15/C-16）
- parser.py: `_infer_status_from_approval` 新增 `conditionally_approved` 推断路径（☑有条件通过）+ archived 说明注释（C-18/C-19）
- path_resolver.py: `find_ledger_file` 支持 PLC + Python 双路径台帐搜索（C-17）

### Changed
- 状态机从 11 状态扩展为 12 状态（对齐 PM-042 V2.3.0 §5.2）
- 变更管理路径解析从 PLC 单路径改为 PLC/Python 双路径优先匹配
- 审批环节名称从 APPROVED/REJECTED 等英文改为已批准/已驳回等中文

### Fixed
- Windows 下 `python -m auto_pm` 因 .pth 文件 UTF-8 路径触发 GBK 解码崩溃
- `cli/__main__.py` 模块级替换 `sys.stdout` 导致 pytest capture 崩溃（改为 `_fix_windows_encoding()` 函数，仅在 `__main__` 直接执行时调用）
- `archived` 状态无法流转到（缺少状态定义和门禁）
- `rejected→draft` 重新起草无需说明原因
- `conditionally_approved→implementing` 无需确认条件已满足
- Python 项目变更单路径无法识别（仅支持 PLC 路径）
- 台帐文件仅搜索 PLC 项目目录

## [0.2.0] - 2026-06-21

### Added - V2.0: PySide6 项目中心式 UI 基座
- PySide6 主框架（QMainWindow + 侧边栏 + 工具栏 + 状态栏 + QStackedWidget）
- 项目列表首页（卡片网格 + 统计栏 + 筛选栏 + 四态切换）
- 项目工作区（Tab 容器 + 概览/变更/检查/文档 Tab）
- 全局功能页骨架（规范中心/模板管理/报告中心/系统设置）
- 项目 CRUD 对话框（新建/编辑/删除/导入）
- 变更中心（变更列表 + 详情面板 + 创建对话框 + 状态流转）
- 导航树（项目列表/全局功能页切换）
- 多角色适配（PM/PLC/Python/SpecEditor 角色-Tab 映射）
- 总库管理（项目导入 + 多业务线分类 SW/DJ/ZD/XT/WX + 搜索）
- business_line 字段（DB 迁移 + extract_business_line 函数）
- Bug-1~5 修复（路径匹配/扫描路径/枚举对齐/模板推断/扫描深度）
- 接口文档 (INT) - 覆盖 CLI/Service/JS Bridge 三部分接口
- 详细设计说明书 (DSN) - 数据库设计/状态机设计/模板设计/GUI原型设计
- 技术方案文档 (TEC) - 技术选型论证/增量扫描策略/数据真源策略
- GUI 文档 Tab - 项目文档状态查看
- GUI 规范检查 Tab - LSP-907 检查/修复
- GUI 变更单创建功能
- GUI 概览 Tab 增强 - 变更概览统计和最近活动

### Changed
- UI 技术栈从 pywebview 迁移到 PySide6
- 移除 auto_pm/gui/ pywebview 层
- cli/gui.py 启动入口改为 PySide6
- README.md 完全重写，反映实际 CLI 命令和功能
- PRD 补充 frontmatter、文档基础信息表、版本变更记录表
- PM_SESSION 更新 P5 完成状态

### Fixed
- Bug-1: _get_project_path 按 {project_id}_{project_name} 模式匹配
- Bug-2: _sync_changes 在 00_项目管理/04_变更管理/01_变更单/CHG-*/ 路径扫描
- Bug-3: GUI 变更单弹窗枚举对齐 _change_constants.py
- Bug-4: retrofit 命令 _src_path 推断逻辑修正
- Bug-5: 扫描深度统一为 depth=4

## [0.1.0] - 2026-06-19

### Added - P5: SQLite 索引缓存 + Pydantic v2 模型 + pywebview GUI
- SQLite 索引缓存层（3 表：projects / change_requests / scan_log）
- 增量扫描策略（file_mtime 判据，SyncService）
- Pydantic v2 模型层（Project / ProjectRecord / ChangeRequest / ChangeSummary / DTO）
- pywebview 桌面 GUI 应用
- GUI JS Bridge API（GuiApi 类，8 个方法）
- GUI 前端（项目列表/详情/新建/编辑/删除/变更单查看/缓存同步）
- DatabaseManager（WAL 模式，连接池）
- ProjectRepository / ChangeRequestRepository / ScanLogRepository
- ApiResponse[T] 统一返回格式

### Added - P4: python-tool Copier 模板
- templates/python-tool/ Copier 模板
- copier.yml 问题定义（7 个字段 + validator）
- pyproject.toml.jinja（hatchling + 标准化依赖）
- 完整包结构模板（cli/core/config/logging/utils 五层）
- tests/ 模板（conftest + test_import）
- .ruff.toml / .pre-commit-config.yaml / Taskfile.yml 模板
- PM_SESSION / PRD / README Jinja2 模板

### Added - P3: 变更管理迁移
- auto_pm/change/ 包（7 模块）
- change/models.py - 变更单模型 + 规范常量
- change/path_resolver.py - 路径解析 + 安全校验
- change/parser.py - 变更单 Markdown 解析器
- change/generator.py - 变更单 Markdown 生成器
- change/ledger_updater.py - 版本变更台帐更新器
- change/change_service.py - 变更管理 Service
- cli/change.py - change 命令组（list/show/create/transition）
- 完整状态机实现（PM-042 V2.2.0）
- 门禁校验（draft→submitted / under_review→approved / 等）
- 19 个测试用例全部通过

### Added - P2: Click 插件架构 + Service 层迁移
- Click 插件架构（cli/__main__.py 主入口）
- cli/project.py - project 命令组（list/create/show/edit/delete/retrofit）
- cli/plc/ - plc 命令组（init/check/repair/standardize）
- cli/python/ - python 命令组（占位）
- cli/template.py - template 命令组（list/update）
- cli/gui.py - gui 命令
- core/project_service.py - 项目 CRUD Service + 文件系统扫描
- core/template_service.py - Copier 模板调度 Service
- plc/checker.py - LSP-907 检查器
- plc/repairer.py - 自动修复器
- app_context.py - AppContext 全局上下文
- config/app_config.py - pydantic-settings 配置
- logging/logging.py - 幂等 Logger
- utils/file_utils.py - 文件读写工具

### Added - P1: Copier 模板 PoC 验证
- templates/plc-standard/ Copier 模板
- copier.yml 问题定义
- .plc.json.jinja / .copier-answers.yml.jinja
- PM_SESSION / PRD / DSN / TEC / INT 文档模板
- 标准目录结构（02_PLC程序 / 03_HMI设计 / 04_变更管理 / 04_现场调试）
- PoC 验证通过：copier copy 生成符合 LSP-907 的项目骨架

### Technical Decisions
- 技术栈选型: Click + Rich + Pydantic v2 + Copier + pywebview + SQLite(WAL)
- 构建系统: hatchling
- 代码质量: ruff + mypy (strict) + pytest
- 数据真源策略: .copier-answers.yml / PM_SESSION / index.db 三源并存
- 增量扫描: file_mtime 判据，避免全量扫描开销
- CLI 插件架构: Click 子命令组 + 延迟导入避免循环依赖
- GUI 模式: pywebview JS Bridge + ApiResponse[T] 统一格式

### Toolchain
- 取代 pm-mgr (SW-2026-007)
- 取代 plc-check
- 与 specmgr (SW-2026-006) 互补
