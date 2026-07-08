---
title: auto-pm CLI 测试计划
version: V0.9.1
date: 2026-07-08
scope: CLI 命令全量测试矩阵
baseline: pyproject=0.9.1 / 1115 passed
---

# auto-pm CLI 测试计划

## 1. 测试目标与范围

### 1.1 测试目标

本计划对 auto-pm V0.9.1 的 CLI 命令层进行系统性测试，目标如下：

1. **全命令覆盖**：覆盖 `auto_pm/cli/` 下全部 10 个命令组（project / change / doc / plc / python / spec / template / vartable / pm-session / gui）的所有子命令，确保每个命令可被正确调用并返回预期结果。
2. **参数组合验证**：对每个子命令的必选参数、可选参数、标志（flag）、`--json`/`--dry-run`/`-w` 等通用选项进行组合验证，确保 Click 参数解析与业务逻辑一致。
3. **边界条件覆盖**：覆盖项目不存在、路径已存在、参数缺失、非法枚举值、空工作空间、破坏性操作未确认等边界场景，确保错误路径输出友好且退出码正确。
4. **退出码契约**：校验成功（exit_code=0）、业务错误（exit_code=1）、文件查找失败（exit_code=2）三类退出码契约，便于脚本化编排。
5. **输出格式契约**：校验 table 模式（rich 渲染）与 json 模式（stdout 纯 JSON）两种输出格式的正确性，确保 json 模式不污染 stdout。
6. **现有资产盘点**：映射现有 `tests/cli/` 测试资产覆盖范围，识别缺口，为后续补测提供基线。

### 1.2 测试范围

- **纳入范围**：
  - `auto_pm/cli/__main__.py` 顶层 group（`-w`/`--version`/`--help`）
  - 10 个子命令组的全部子命令及其参数
  - CLI 与 Service 层的集成（通过 `CliRunner` 端到端验证）
  - 退出码、stdout/stderr 分离、JSON 输出契约
- **不纳入范围**：
  - Service 层 / Repository 层的纯单元测试（已由 `tests/core/`、`tests/db/`、`tests/change/` 等覆盖）
  - GUI 桌面应用的交互测试（由 `tests/qml/` 覆盖，本计划仅验证 `gui` 命令的入口参数解析与崩溃捕获安装）
  - Copier 模板内容本身的正确性（由 `tests/plc/test_template_generation.py` 覆盖）

### 1.3 测试基线

| 项目 | 基线值 |
|------|--------|
| pyproject.toml 版本 | 0.9.1 |
| 全量回归用例数 | 1115 passed |
| pytest 标记数 | 6（gui/cli/smoke/unit/integration/slow）|
| CLI 测试文件数 | 9（tests/cli/test_*.py）|
| CLI 入口 | `python -m auto_pm` 或 `auto-pm`（click 框架）|

## 2. CLI 命令矩阵

顶层 CLI（`cli` group）通用选项：

| 选项 | 说明 |
|------|------|
| `-w/--workspace <PATH>` | 工作空间根目录（envvar: `AUTO_PM_WORKSPACE`），未指定时默认当前目录 |
| `--version/-v` | 输出版本号 |
| `-h/--help` | 帮助（`CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])`）|

### 2.1 project 命令组（`auto_pm/cli/project.py`）

| 子命令 | 参数/选项 | 测试类型 | 预期行为 | 现有测试定位 |
|--------|-----------|----------|----------|--------------|
| `project list` | `--business-line/-bl` `--stack` `--phase` `--search` `--json` | 冒烟/功能/边界 | 输出项目表格；`--json` 输出 JSON 数组；空工作空间输出"未发现项目"或 `[]` | tests/cli/test_project.py::test_project_list_via_main |
| `project create` | `--stack`(必) `--id`(必) `--name`(必) `--desc` `--business-line/-bl` `--mode` `--library-name` `--project-type` `--equipment-type` `--plc-vendor` `--plc-model` `--dry-run` | 功能/边界 | 调用 Copier 生成骨架；目标已存在 exit=1；`--dry-run` 仅预览；shared-library 缺 `--library-name` exit=1；业务线与编号前缀不一致输出警告 | tests/cli/test_project.py::test_project_create_dry_run_displays_v040_metadata、test_project_create_single_machine_generates_week2_template_assets |
| `project show <ID>` | `--json` | 冒烟/功能/边界 | 输出项目详情；`--json` 输出 model_dump；项目不存在 exit=1；渲染工程资产摘要 | tests/cli/test_project.py::test_project_show_via_main、test_project_show_not_found、test_project_show_displays_v040_metadata、test_project_show_displays_week3_asset_summary、test_project_show_json_contains_asset_summary |
| `project edit <ID>` | `--phase` `--desc` `--version` `--business-line/-bl` | 功能/边界 | 写入 .copier-answers.yml；未指定字段提示；项目不存在 exit=1 | （缺口） |
| `project delete <ID>` | `--confirm` | 功能/边界（破坏性）| 无 `--confirm` exit=1；`--confirm` 删除目录并审计；项目不存在 exit=1 | （缺口） |
| `project retrofit <ID>` | （无） | 功能 | 补全 .copier-answers.yml；PLC 项目补全标志文件；已有则跳过 | （缺口） |
| `project snapshot <ID>` | `--dry-run` `--json` | 功能/边界 | 对齐 PM_SESSION Spec Snapshot 版本号；无漂移输出"已是最新"；`--dry-run` 预览漂移；PM_SESSION 缺失 exit=1；spec_registry 缺失 exit=1 | tests/cli/test_project.py::TestProjectSnapshot（7 个用例）|
| `project import <PATH>` | `--move` `--force` `--business-line/-bl` | 功能/边界 | 复制/移动到 02_在研项目/；目标已存在无 `--force` exit=1；导入后补全元数据并同步 DB 缓存 | （缺口） |

### 2.2 change 命令组（`auto_pm/cli/change.py`）

| 子命令 | 参数/选项 | 测试类型 | 预期行为 | 现有测试定位 |
|--------|-----------|----------|----------|--------------|
| `change list <PID>` | `--status` `--domain` `--full` | 冒烟/功能/边界 | 输出变更单表格；`--status`/`--domain` 筛选；`--full` 标题列自动换行；空列表输出"未发现变更单" | tests/cli/test_change.py::test_change_list_empty、test_change_list_with_changes、test_change_list_filter_by_status、test_change_list_filter_by_domain、test_change_list_full_mode |
| `change show <CHG>` | （无） | 功能/边界 | 输出变更单详情 + §6/§8/§9/§10 章节；变更单不存在 exit=1 | tests/cli/test_change.py::test_change_show_normal、test_change_show_not_found |
| `change create` | `--pid`(必) `--domain`(必) `--nature`(必) `--scope`(必,可多次) `--applicant`(必) `--background`(必) `--necessity`(必) `--references` `--planned-date` `--urgency` | 功能/边界 | 生成 CHG-*.md 并更新台帐；缺必选参数 exit=2（Click）；项目不存在 exit=1 | tests/cli/test_change.py::test_change_create_normal、test_change_create_missing_required_option、test_change_create_nonexistent_project |
| `change transition <CHG>` | `--to`(必) `--approver` `--comment` `--verification-conclusion` `--allow-partial-verification` | 功能/边界 | 状态流转并审计；非法状态 exit=1；变更单不存在 exit=1；不可达状态 exit=1 | tests/cli/test_change.py::test_change_transition_draft_to_submitted、test_change_transition_invalid_status、test_change_transition_nonexistent_change、test_change_transition_unreachable_status |
| `change edit <CHG>` | `--background` `--necessity` `--references` `--planned-date` `--urgency` `--risk-level` `--mitigation` `--propagation-chain` | 功能/边界 | 更新 §4/§6 字段；未指定字段 exit=1；变更单不存在 exit=1 | tests/cli/test_change.py::test_change_edit_normal、test_change_edit_nonexistent_change、test_change_edit_no_fields_specified |

### 2.3 spec 命令组（`auto_pm/cli/spec.py`）

| 子命令 | 参数/选项 | 测试类型 | 预期行为 | 现有测试定位 |
|--------|-----------|----------|----------|--------------|
| `spec check` | `-w/--workspace` `--fix` `--dry-run` `--format`(table/json) `--check-id/-c`(可多次) `--severity` `--scope` `--project-root` `--config` `--quiet` | 功能/边界 | 运行 SHC-001~010；`scope=project` 缺 `--project-root` 报错；项目根不在工作空间内报错；`--quiet` 仅输出 ERROR；退出码取自 `output.exit_code` | tests/cli/test_spec.py::TestSpecCLIBoundary |
| `spec index` | `-w` `--domain`(pm/plc/python/all) `--config` `--quiet` | 功能 | 生成规范索引文件；`--quiet` 仅输出错误 | （缺口） |
| `spec frontmatter` | `-w` `--fix` `--spec-id` `--config` `--quiet` | 功能/边界 | 默认 DRY-RUN 预览；`--fix` 实际写入；统计 pending/skipped/error | （缺口） |
| `spec report` | `-w` `--output/-o` `--format`(markdown/json) `--config` `--quiet` | 功能 | 生成元数据汇总报告；`--quiet` 成功无输出 | （缺口） |

> 注：spec 子命令的 `-w` 支持回退全局 `auto-pm -w`（`_resolve_workspace` 实现），未指定任何 `-w` 时 exit=1。

### 2.4 template 命令组（`auto_pm/cli/template.py`）

| 子命令 | 参数/选项 | 测试类型 | 预期行为 | 现有测试定位 |
|--------|-----------|----------|----------|--------------|
| `template list` | （无） | 冒烟/功能 | 输出可用模板表格；空目录输出"未发现模板" | tests/cli/test_template.py::test_template_list |
| `template update <ID>` | `--overwrite` | 功能/边界 | Copier 增量更新；项目不存在 exit=1；缺 .copier-answers.yml exit=1 | tests/cli/test_template.py::test_template_update_nonexistent_project、test_template_update_missing_copier_answers |

> 注：template 组实际为 `list`/`update`（任务书所列 `apply/show` 不存在于代码，以代码为准）。

### 2.5 plc 命令组（`auto_pm/cli/plc/__init__.py`）

| 子命令 | 参数/选项 | 测试类型 | 预期行为 | 现有测试定位 |
|--------|-----------|----------|----------|--------------|
| `plc init <ID>` | `--name`(必) `--desc` `--mode` | 功能/边界 | 调用 Copier 生成 PLC 骨架；目标已存在 exit=1；shared-library/test-suite/standard-project 三种模式；非法 mode exit=2 | tests/cli/test_plc.py::test_plc_init、test_plc_init_default_mode、test_plc_init_shared_library_fails、test_plc_init_invalid_mode、test_plc_init_existing_path |
| `plc check [ID]` | `--all` `--json` `--substance` `--fix` | 冒烟/功能/边界 | 单项目检查或 `--all` 批量；Python 项目输出"PLC 检查不适用"且不计入 FAIL；`--substance` 实质化检查；`--fix` 自动修复；未指定 ID 且无 `--all` exit=1；项目不存在 exit=1 | tests/cli/test_plc.py::test_plc_check_all、test_plc_check_project、test_plc_check_not_found、test_plc_check_substance、test_plc_check_fix、test_plc_check_python_project_friendly_output、test_plc_check_python_project_json、test_plc_check_all_skips_python_project、test_plc_check_python_project_does_not_pollute_dashboard |
| `plc repair <ID>` | `--rename` `--dry-run` | 功能/边界（破坏性）| 自动修复结构问题；`--rename` 确认重命名；`--dry-run` 仅预览；项目不存在 exit=1 | tests/cli/test_plc.py::test_plc_repair、test_plc_repair_dry_run、test_plc_repair_not_found |
| `plc standardize <ID>` | `--apply` | 功能/边界 | 检测并修正 PRD 文档命名；默认仅预览；`--apply` 执行重命名；无需标准化输出"已符合规范"；项目不存在 exit=1 | tests/cli/test_plc.py::test_plc_standardize_preview、test_plc_standardize_apply、test_plc_standardize_no_change、test_plc_standardize_not_found |

### 2.6 python 命令组（`auto_pm/cli/python/__init__.py`）

| 子命令 | 参数/选项 | 测试类型 | 预期行为 | 现有测试定位 |
|--------|-----------|----------|----------|--------------|
| `python init <ID>` | `--name`(必) `--desc` `--package` `--author` `--dry-run` | 功能/边界 | 调用 Copier python-tool 模板；目标已存在 exit=1；`--dry-run` 仅预览；自动推导 package_name/cli_command | tests/cli/test_python.py::test_python_init_dry_run、test_python_init_actual_create、test_python_init_existing_path |
| `python check [ID]` | `--all` `--json` | 功能/边界 | 检查 210/211/220 规范（必需文件/目录/pyproject 字段/PM_SESSION）；非 Python 项目 exit=1；未指定 ID 且无 `--all` exit=1；`--all` 无 Python 项目输出提示 | tests/cli/test_python.py::test_python_check_normal、test_python_check_json、test_python_check_nonexistent_project、test_python_check_non_python_project、test_python_check_all、test_python_check_all_no_python_projects、test_python_check_missing_argument |

### 2.7 doc 命令组（`auto_pm/cli/doc.py`）

| 子命令 | 参数/选项 | 测试类型 | 预期行为 | 现有测试定位 |
|--------|-----------|----------|----------|--------------|
| `doc refresh <ID>` | `--dry-run` `--json` | 功能/边界 | 刷新 PLC 文档自动区；`--dry-run` 预览；`--json` 输出 result.to_dict；项目不存在 exit=1；issue 文本保留 `[block_key]` 方括号 | tests/cli/test_project.py::TestDocRefresh（3 个用例）、tests/cli/test_doc.py::TestDocIssueBracketPreservation::test_doc_refresh_issue_preserves_brackets_around_block_key |
| `doc inject <ID>` | `--dry-run` `--json` | 功能/边界 | 为历史 PLC 文档注入 AUTO_PM 标记；`--dry-run` 不写入；`--json` 输出结构；项目不存在 exit=1；锚点缺失输出 issue；已存在标记跳过 | tests/cli/test_doc.py::TestDocInject（8 个用例：dry_run/writes/consistency/missing_anchor/json/not_found/skip_existing + bracket preservation）|

### 2.8 pm-session 命令组（`auto_pm/cli/session.py`）

> 注：命令组名为 `pm-session`（任务书所列 `session` 不准确，以代码为准）。

| 子命令 | 参数/选项 | 测试类型 | 预期行为 | 现有测试定位 |
|--------|-----------|----------|----------|--------------|
| `pm-session check` | `-w` `--project-root` `--project-id` `--quiet` | 功能/边界 | 检查规模门禁（150KB/300 行）+ 章节完整性；健康 exit=0，不健康 exit=1；未找到 PM_SESSION exit=2；多文件冲突 exit=2 | tests/cli/test_session.py::TestPmSessionCheck、TestPmSessionGroupRegistration |
| `pm-session archive` | `-w` `--project-root` `--project-id` `--section`(必) `--keep-recent` `--archive-file` `--dry-run` `--no-backup` | 功能/边界（破坏性）| 归档指定章节；`--dry-run` 预览；`--keep-recent` 保留最近 N 行；章节不存在 exit=2；自动生成归档路径 | tests/cli/test_session.py::TestPmSessionArchive |
| `pm-session view` | `-w` `--project-root` `--project-id` `--output/-o` | 功能 | 生成只读视图（§2+§3+§9）；`-o` 写文件，否则输出 stdout | tests/cli/test_session.py::TestPmSessionView |

### 2.9 vartable 命令组（`auto_pm/cli/vartable.py`）

| 子命令 | 参数/选项 | 测试类型 | 预期行为 | 现有测试定位 |
|--------|-----------|----------|----------|--------------|
| `vartable parse <FILE>` | `--format` `--output-format`(table/json) | 功能/边界 | 自动识别或显式指定格式解析；`--output-format json` 纯 JSON 到 stdout；解析失败 exit=1 | tests/cli/test_vartable.py::TestVartableParseCommand |
| `vartable detect-encoding <FILE>` | `--format`(text/json) | 功能/边界 | 检测文件编码；`--format json` 输出 JSON；文件不存在 exit=1 | tests/cli/test_vartable.py::TestVartableDetectEncodingCommand |
| `vartable list-encodings` | （无） | 冒烟 | 列出 SUPPORTED_ENCODINGS | tests/cli/test_vartable.py::TestVartableListEncodingsCommand |
| `vartable list-formats` | `--format`(text/json) | 冒烟 | 列出支持的解析格式 | （缺口） |
| `vartable detect-format <FILE>` | `--format`(text/json) | 功能 | 识别文件格式并输出 | （缺口） |
| `vartable convert <FILE>` | `--format` `--output-format`(csv/yaml/json) `--output` | 功能/边界 | 解析并导出；`--output` 写文件，否则 stdout；解析失败 exit=1 | （缺口） |
| `vartable batch-parse <DIR>` | `--recursive` `--output-format`(table/json) | 功能 | 批量解析目录；聚合成功/失败统计；无文件输出"未找到" | （缺口） |
| `vartable --help` | （无） | 冒烟 | group 帮助正常 | tests/cli/test_vartable.py::TestVartableHelpCommand |

### 2.10 gui 命令（`auto_pm/cli/gui.py`）

> 注：`gui` 是单命令（`@click.command`），非命令组。

| 子命令 | 参数/选项 | 测试类型 | 预期行为 | 现有测试定位 |
|--------|-----------|----------|----------|--------------|
| `gui` | `--debug` | 冒烟（入口参数解析）| 启动 QML 桌面应用；安装崩溃捕获（`~/.auto-pm/logs/crash.log`）；PySide6 缺失抛 ClickException | （缺口，GUI 交互测试在 tests/qml/，CLI 入口未单独测试）|

## 3. 测试执行方式

### 3.1 命令分类执行

| 测试类型 | 执行命令 | 预期耗时 | 用途 |
|----------|----------|----------|------|
| 冒烟测试 | `pytest -m smoke --no-cov -q` | < 30s | CI 门禁 / 发布前快速回归（含 CLI `--help` 入口）|
| CLI 单元测试 | `pytest -m cli --no-cov -q` | ~10s | CLI 命令层端到端验证（CliRunner）|
| 集成测试 | `pytest -m integration --no-cov -q` | ~15s | 跨层集成（Service + DB + 文件系统）|
| GUI 测试 | `pytest -m gui --no-cov -q` | ~60s | QML 桌面应用（可见窗口模式，遵循 GUI 测试规则）|
| 慢速测试 | `pytest -m slow --no-cov -q` | > 5s/用例 | 标记长耗时用例 |
| 全量回归 | `pytest --no-cov -q` | ~45s | 1115 passed 基线验证 |
| 全量带覆盖率 | `pytest -q` | ~60s | 默认 addopts 含 coverage + junit xml |

### 3.2 Taskfile 任务（`Taskfile.yml`）

| Task 命令 | 等价 pytest | 说明 |
|-----------|-------------|------|
| `task test` | `python -m pytest -vv` | 带覆盖率全量 |
| `task test-fast` | `python -m pytest -vv --no-cov` | 不带覆盖率全量 |
| `task test-unit` | `pytest tests/{change,cli,core,db,models,plc,utils,logging,config}/` | 单元测试（含 CLI，排除 GUI）|
| `task test-gui` | `pytest tests/qml/` | GUI 专项 |
| `task smoke` | `python -m auto_pm --help` 等 5 条 | CLI `--help` 冒烟（非 pytest，直接调 CLI）|

### 3.3 标记使用约定

- `@pytest.mark.smoke`：核心功能快速验证，< 30s，不依赖外部环境
- `@pytest.mark.cli`：CLI 命令测试（使用 `CliRunner`）
- `@pytest.mark.integration`：跨层集成测试
- `@pytest.mark.gui`：GUI 全功能自动化测试
- `@pytest.mark.unit`：纯单元测试
- `@pytest.mark.slow`：运行时间 > 5s 的慢速测试

### 3.4 GUI 测试模式规则（强制）

- 正常 GUI 测试禁止使用 offscreen 模式，必须使用可见窗口（`GUI_VISIBLE=1` 或不设置 `QT_QPA_PLATFORM=offscreen`）
- 仅 CI 无显示器环境或批量回归时使用 offscreen
- `gui` CLI 命令的入口测试如需触发真实窗口，须标记 `@pytest.mark.gui` 并在可见模式下执行

## 4. 测试用例清单

> 用例 ID 规则：`CLI-<组缩写>-<三位序号>`。优先级：P0=冒烟必过 / P1=核心功能 / P2=边界/异常。

### 4.1 顶层 CLI（CLI-TOP）

| 用例 ID | 命令 | 预期结果 | 优先级 |
|---------|------|----------|--------|
| CLI-TOP-001 | `auto-pm --help` | exit=0，输出含所有 10 个命令组 | P0 |
| CLI-TOP-002 | `auto-pm --version` | exit=0，输出版本号 | P0 |
| CLI-TOP-003 | `auto-pm -h` | exit=0（`-h` 等价 `--help`）| P0 |
| CLI-TOP-004 | `auto-pm -w <不存在路径> project list` | exit≠0，输出路径错误 | P1 |
| CLI-TOP-005 | `AUTO_PM_WORKSPACE=<path> auto-pm project list` | exit=0，envvar 生效 | P1 |
| CLI-TOP-006 | `auto-pm 未知命令` | exit=2（Click NoSuchCommand）| P2 |

### 4.2 project（CLI-PRJ）

| 用例 ID | 命令 | 预期结果 | 优先级 |
|---------|------|----------|--------|
| CLI-PRJ-001 | `project list`（空工作空间）| exit=0，输出"未发现项目" | P0 |
| CLI-PRJ-002 | `project list --json`（空）| exit=0，stdout=`[]` | P1 |
| CLI-PRJ-003 | `project list --business-line DJ` | exit=0，仅 DJ 前缀项目 | P1 |
| CLI-PRJ-004 | `project list --stack plc --phase developing` | exit=0，组合筛选生效 | P1 |
| CLI-PRJ-005 | `project list --search 关键字` | exit=0，匹配 id/name/desc | P2 |
| CLI-PRJ-006 | `project create --stack plc --id DJ-2026-010 --name 边框缓存机 --dry-run` | exit=0，输出预览不创建 | P0 |
| CLI-PRJ-007 | `project create --stack plc --id DJ-2026-010 --name X`（已存在）| exit=1，"目标路径已存在" | P1 |
| CLI-PRJ-008 | `project create --stack plc --id DJ-2026-010 --name X --mode shared-library`（无 library-name 且名称非英文）| exit=1 | P2 |
| CLI-PRJ-009 | `project create --stack python --id SW-2026-008 --name auto-pm` | exit=0，生成骨架 | P1 |
| CLI-PRJ-010 | `project create --business-line DJ --id SW-2026-009 --name X`（前缀不一致）| exit=0，输出业务线不一致警告 | P2 |
| CLI-PRJ-011 | `project show DJ-2026-010` | exit=0，输出详情含资产摘要 | P0 |
| CLI-PRJ-012 | `project show DJ-2026-010 --json` | exit=0，stdout 为合法 JSON | P1 |
| CLI-PRJ-013 | `project show NOT-EXIST` | exit=1，"项目不存在" | P1 |
| CLI-PRJ-014 | `project edit DJ-2026-010 --phase production` | exit=0，写入 .copier-answers.yml | P1 |
| CLI-PRJ-015 | `project edit DJ-2026-010`（无字段）| exit=0，提示"未指定更新字段" | P2 |
| CLI-PRJ-016 | `project edit NOT-EXIST --phase production` | exit=1 | P2 |
| CLI-PRJ-017 | `project delete DJ-2026-010`（无 --confirm）| exit=1，警告 | P1 |
| CLI-PRJ-018 | `project delete DJ-2026-010 --confirm` | exit=0，目录删除并审计 | P1 |
| CLI-PRJ-019 | `project delete NOT-EXIST --confirm` | exit=1 | P2 |
| CLI-PRJ-020 | `project retrofit DJ-2026-010` | exit=0，补全 .copier-answers.yml | P1 |
| CLI-PRJ-021 | `project retrofit DJ-2026-010`（已有）| exit=0，输出"跳过" | P2 |
| CLI-PRJ-022 | `project snapshot DJ-2026-010`（有漂移）| exit=0，更新版本号 | P1 |
| CLI-PRJ-023 | `project snapshot DJ-2026-010 --dry-run` | exit=0，预览不修改 | P1 |
| CLI-PRJ-024 | `project snapshot DJ-2026-010 --json` | exit=0，stdout 合法 JSON | P1 |
| CLI-PRJ-025 | `project snapshot DJ-2026-010`（无漂移）| exit=0，"已是最新" | P2 |
| CLI-PRJ-026 | `project snapshot NOT-EXIST` | exit=1 | P2 |
| CLI-PRJ-027 | `project snapshot DJ-2026-010`（无 PM_SESSION）| exit=1 | P2 |
| CLI-PRJ-028 | `project snapshot DJ-2026-010`（无 spec_registry）| exit=1 | P2 |
| CLI-PRJ-029 | `project import <PATH>` | exit=0，复制并补全元数据 | P1 |
| CLI-PRJ-030 | `project import <PATH> --move --force` | exit=0，移动并覆盖 | P2 |
| CLI-PRJ-031 | `project import <PATH>`（目标已存在无 --force）| exit=1 | P2 |

### 4.3 change（CLI-CHG）

| 用例 ID | 命令 | 预期结果 | 优先级 |
|---------|------|----------|--------|
| CLI-CHG-001 | `change list DJ-2026-010`（空）| exit=0，"未发现变更单" | P0 |
| CLI-CHG-002 | `change list DJ-2026-010 --status draft --domain plc` | exit=0，筛选生效 | P1 |
| CLI-CHG-003 | `change list DJ-2026-010 --full` | exit=0，标题列换行 | P2 |
| CLI-CHG-004 | `change show CHG-DOCU-2026-001` | exit=0，输出详情含 §6/§8/§9/§10 | P0 |
| CLI-CHG-005 | `change show NOT-EXIST` | exit=1 | P1 |
| CLI-CHG-006 | `change create --pid DJ-2026-010 --domain plc --nature new --scope doc --applicant 张三 --background 背景 --necessity 必要` | exit=0，生成 CHG-*.md | P0 |
| CLI-CHG-007 | `change create`（缺必选参数）| exit=2（Click）| P1 |
| CLI-CHG-008 | `change create --pid NOT-EXIST ...` | exit=1 | P2 |
| CLI-CHG-009 | `change transition CHG-DOCU-2026-001 --to submitted` | exit=0，状态流转+审计 | P0 |
| CLI-CHG-010 | `change transition CHG-DOCU-2026-001 --to archived`（不可达）| exit=1 | P1 |
| CLI-CHG-011 | `change transition CHG-DOCU-2026-001 --to invalid` | exit=2（Click Choice）| P2 |
| CLI-CHG-012 | `change transition NOT-EXIST --to submitted` | exit=1 | P2 |
| CLI-CHG-013 | `change transition CHG-DOCU-2026-001 --to completed --allow-partial-verification` | exit=0，部分验证闭环 | P2 |
| CLI-CHG-014 | `change edit CHG-DOCU-2026-001 --background 新背景 --risk-level high` | exit=0 | P1 |
| CLI-CHG-015 | `change edit CHG-DOCU-2026-001`（无字段）| exit=1 | P2 |
| CLI-CHG-016 | `change edit NOT-EXIST --background X` | exit=1 | P2 |

### 4.4 spec（CLI-SPEC）

| 用例 ID | 命令 | 预期结果 | 优先级 |
|---------|------|----------|--------|
| CLI-SPEC-001 | `spec check -w <ws>` | exit 取决于检查结果，输出 table | P0 |
| CLI-SPEC-002 | `spec check -w <ws> --format json` | stdout 合法 JSON 含 check_results | P1 |
| CLI-SPEC-003 | `spec check -w <ws> --fix --dry-run` | exit=0，预览修复不写入 | P1 |
| CLI-SPEC-004 | `spec check -w <ws> --check-id SHC-001 --severity error` | exit=0，仅运行指定检查 | P2 |
| CLI-SPEC-005 | `spec check -w <ws> --scope project --project-root <子目录>` | exit=0 | P2 |
| CLI-SPEC-006 | `spec check -w <ws> --scope project`（无 --project-root）| exit=1 | P2 |
| CLI-SPEC-007 | `spec check -w <ws> --scope project --project-root <工作空间外>` | exit=1，"必须位于工作空间内部" | P2 |
| CLI-SPEC-008 | `spec check`（无 -w）| exit=1，"必须通过 -w 指定" | P2 |
| CLI-SPEC-009 | `spec check -w <ws> --quiet` | 仅输出 ERROR 级别 | P2 |
| CLI-SPEC-010 | `spec index -w <ws> --domain plc` | exit=0，生成索引 | P1 |
| CLI-SPEC-011 | `spec index -w <ws> --quiet` | 仅输出错误 | P2 |
| CLI-SPEC-012 | `spec frontmatter -w <ws>` | exit=0，DRY-RUN 预览 | P1 |
| CLI-SPEC-013 | `spec frontmatter -w <ws> --fix` | exit=0，实际写入 | P1 |
| CLI-SPEC-014 | `spec frontmatter -w <ws> --spec-id SW-2026-006` | exit=0，仅处理指定规范 | P2 |
| CLI-SPEC-015 | `spec report -w <ws>` | exit=0，生成 markdown 报告 | P1 |
| CLI-SPEC-016 | `spec report -w <ws> --format json --output report.json` | exit=0，写文件 | P2 |
| CLI-SPEC-017 | `spec report -w <ws> --quiet` | 成功无输出 | P2 |

### 4.5 template（CLI-TPL）

| 用例 ID | 命令 | 预期结果 | 优先级 |
|---------|------|----------|--------|
| CLI-TPL-001 | `template list` | exit=0，输出模板表格 | P0 |
| CLI-TPL-002 | `template list`（空模板目录）| exit=0，"未发现模板" | P2 |
| CLI-TPL-003 | `template update DJ-2026-010` | exit=0，增量更新 | P1 |
| CLI-TPL-004 | `template update DJ-2026-010 --overwrite` | exit=0，覆盖冲突 | P2 |
| CLI-TPL-005 | `template update NOT-EXIST` | exit=1 | P1 |
| CLI-TPL-006 | `template update DJ-2026-010`（无 .copier-answers.yml）| exit=1 | P2 |

### 4.6 plc（CLI-PLC）

| 用例 ID | 命令 | 预期结果 | 优先级 |
|---------|------|----------|--------|
| CLI-PLC-001 | `plc init DJ-2026-010 --name 边框缓存机` | exit=0，生成骨架 | P0 |
| CLI-PLC-002 | `plc init DJ-2026-010 --name X --mode shared-library` | exit=0/1 视 library-name 推断 | P1 |
| CLI-PLC-003 | `plc init DJ-2026-010 --name X --mode invalid` | exit=2（Click Choice）| P2 |
| CLI-PLC-004 | `plc init DJ-2026-010 --name X`（已存在）| exit=1 | P1 |
| CLI-PLC-005 | `plc check DJ-2026-010` | exit=0/1 视检查结果 | P0 |
| CLI-PLC-006 | `plc check --all` | exit=0，批量摘要 | P0 |
| CLI-PLC-007 | `plc check DJ-2026-010 --json` | stdout 合法 JSON | P1 |
| CLI-PLC-008 | `plc check DJ-2026-010 --substance` | exit=0，实质化检查 | P2 |
| CLI-PLC-009 | `plc check DJ-2026-010 --fix` | exit=0，自动修复 | P2 |
| CLI-PLC-010 | `plc check SW-2026-008`（Python 项目）| exit=0，"PLC 检查不适用" | P1 |
| CLI-PLC-011 | `plc check`（无 ID 无 --all）| exit=1 | P2 |
| CLI-PLC-012 | `plc check NOT-EXIST` | exit=1 | P2 |
| CLI-PLC-013 | `plc repair DJ-2026-010` | exit=0，输出修复结果 | P1 |
| CLI-PLC-014 | `plc repair DJ-2026-010 --rename --dry-run` | exit=0，预览 | P2 |
| CLI-PLC-015 | `plc repair NOT-EXIST` | exit=1 | P2 |
| CLI-PLC-016 | `plc standardize DJ-2026-010` | exit=0，预览命名计划 | P1 |
| CLI-PLC-017 | `plc standardize DJ-2026-010 --apply` | exit=0，执行重命名 | P1 |
| CLI-PLC-018 | `plc standardize DJ-2026-010`（无需标准化）| exit=0，"已符合规范" | P2 |
| CLI-PLC-019 | `plc standardize NOT-EXIST` | exit=1 | P2 |

### 4.7 python（CLI-PY）

| 用例 ID | 命令 | 预期结果 | 优先级 |
|---------|------|----------|--------|
| CLI-PY-001 | `python init SW-2026-008 --name auto-pm --dry-run` | exit=0，预览 | P0 |
| CLI-PY-002 | `python init SW-2026-008 --name auto-pm` | exit=0，生成骨架 | P1 |
| CLI-PY-003 | `python init SW-2026-008 --name X --package my_pkg --author fubai` | exit=0，自定义包名/作者 | P2 |
| CLI-PY-004 | `python init SW-2026-008 --name X`（已存在）| exit=1 | P1 |
| CLI-PY-005 | `python check SW-2026-008` | exit=0，输出检查表 | P0 |
| CLI-PY-006 | `python check SW-2026-008 --json` | stdout 合法 JSON | P1 |
| CLI-PY-007 | `python check --all` | exit=0，批量 | P1 |
| CLI-PY-008 | `python check --all`（无 Python 项目）| exit=0，"未发现 Python 项目" | P2 |
| CLI-PY-009 | `python check DJ-2026-010`（非 Python 项目）| exit=1 | P1 |
| CLI-PY-010 | `python check NOT-EXIST` | exit=1 | P2 |
| CLI-PY-011 | `python check`（无 ID 无 --all）| exit=1 | P2 |

### 4.8 doc（CLI-DOC）

| 用例 ID | 命令 | 预期结果 | 优先级 |
|---------|------|----------|--------|
| CLI-DOC-001 | `doc refresh DJ-2026-010` | exit=0，刷新自动区 | P0 |
| CLI-DOC-002 | `doc refresh DJ-2026-010 --dry-run` | exit=0，预览不写入 | P1 |
| CLI-DOC-003 | `doc refresh DJ-2026-010 --json` | stdout 合法 JSON | P1 |
| CLI-DOC-004 | `doc refresh DJ-2026-010`（无可刷新文档）| exit=0，"没有可刷新" | P2 |
| CLI-DOC-005 | `doc refresh DJ-2026-010`（issue 含 `[block_key]`）| exit=0，方括号保留 | P2 |
| CLI-DOC-006 | `doc refresh NOT-EXIST` | exit=1 | P2 |
| CLI-DOC-007 | `doc inject DJ-2026-051` | exit=0，注入标记 | P0 |
| CLI-DOC-008 | `doc inject DJ-2026-051 --dry-run` | exit=0，不写入 | P1 |
| CLI-DOC-009 | `doc inject DJ-2026-051 --json` | stdout 合法 JSON | P1 |
| CLI-DOC-010 | `doc inject DJ-2026-051`（锚点缺失）| exit=0，输出 issue | P2 |
| CLI-DOC-011 | `doc inject DJ-2026-051`（已存在标记）| exit=0，跳过 | P2 |
| CLI-DOC-012 | `doc inject NOT-EXIST` | exit=1 | P2 |
| CLI-DOC-013 | `doc inject DJ-2026-051` 后 `doc refresh DJ-2026-051` | 一致性：注入后可刷新 | P2 |

### 4.9 pm-session（CLI-SES）

| 用例 ID | 命令 | 预期结果 | 优先级 |
|---------|------|----------|--------|
| CLI-SES-001 | `pm-session check -w <ws>` | 健康时 exit=0 | P0 |
| CLI-SES-002 | `pm-session check -w <ws>`（超阈值/缺章节）| exit=1，输出 warnings | P1 |
| CLI-SES-003 | `pm-session check -w <ws> --quiet`（健康）| exit=0，无输出 | P2 |
| CLI-SES-004 | `pm-session check -w <ws> --project-id SW-2026-008` | exit=0 | P2 |
| CLI-SES-005 | `pm-session check`（无 PM_SESSION 文件）| exit=2 | P2 |
| CLI-SES-006 | `pm-session check`（多 PM_SESSION 冲突）| exit=2 | P2 |
| CLI-SES-007 | `pm-session archive -w <ws> --section 7` | exit=0，归档 | P1 |
| CLI-SES-008 | `pm-session archive -w <ws> --section 6 --keep-recent 20` | exit=0，保留最近 20 行 | P2 |
| CLI-SES-009 | `pm-session archive -w <ws> --section 7 --dry-run` | exit=0，预览不修改 | P2 |
| CLI-SES-010 | `pm-session archive -w <ws> --section 99`（不存在）| exit=2 | P2 |
| CLI-SES-011 | `pm-session archive -w <ws> --section 7 --no-backup` | exit=0，不创建备份 | P2 |
| CLI-SES-012 | `pm-session view -w <ws>` | exit=0，stdout 输出视图 | P1 |
| CLI-SES-013 | `pm-session view -w <ws> -o view.md` | exit=0，写文件 | P2 |

### 4.10 vartable（CLI-VAR）

| 用例 ID | 命令 | 预期结果 | 优先级 |
|---------|------|----------|--------|
| CLI-VAR-001 | `vartable parse io_points.csv` | exit=0，输出变量条目 | P0 |
| CLI-VAR-002 | `vartable parse io_points.csv --output-format json` | stdout 合法 JSON | P1 |
| CLI-VAR-003 | `vartable parse file.scl --format scl` | exit=0，显式格式 | P2 |
| CLI-VAR-004 | `vartable parse` 不支持格式 | exit=1 | P2 |
| CLI-VAR-005 | `vartable detect-encoding io_points.csv` | exit=0，输出编码 | P1 |
| CLI-VAR-006 | `vartable detect-encoding io_points.csv --format json` | stdout 合法 JSON | P2 |
| CLI-VAR-007 | `vartable detect-encoding NOT-EXIST` | exit=1 | P2 |
| CLI-VAR-008 | `vartable list-encodings` | exit=0，列出编码 | P0 |
| CLI-VAR-009 | `vartable list-formats` | exit=0，列出格式 | P0 |
| CLI-VAR-010 | `vartable list-formats --format json` | stdout 合法 JSON | P2 |
| CLI-VAR-011 | `vartable detect-format io_points.csv` | exit=0，输出格式 | P1 |
| CLI-VAR-012 | `vartable detect-format io_points.csv --format json` | stdout 合法 JSON | P2 |
| CLI-VAR-013 | `vartable convert io_points.csv --output-format csv` | exit=0，stdout CSV | P1 |
| CLI-VAR-014 | `vartable convert file.scl --output-format yaml --output out.yaml` | exit=0，写文件 | P2 |
| CLI-VAR-015 | `vartable convert io_points.csv --output-format json` | exit=0，stdout JSON | P2 |
| CLI-VAR-016 | `vartable convert` 解析失败 | exit=1 | P2 |
| CLI-VAR-017 | `vartable batch-parse <dir>` | exit=0，聚合统计 | P1 |
| CLI-VAR-018 | `vartable batch-parse <dir> --recursive --output-format json` | stdout 合法 JSON | P2 |
| CLI-VAR-019 | `vartable batch-parse <dir>`（无文件）| exit=0，"未找到" | P2 |
| CLI-VAR-020 | `vartable --help` | exit=0，列出子命令 | P0 |

### 4.11 gui（CLI-GUI）

| 用例 ID | 命令 | 预期结果 | 优先级 |
|---------|------|----------|--------|
| CLI-GUI-001 | `auto-pm gui --help` | exit=0，输出 `--debug` 选项 | P0 |
| CLI-GUI-002 | `auto-pm gui --debug -w <ws>` | 启动 QML（需可见窗口，标记 `@pytest.mark.gui`）| P1 |
| CLI-GUI-003 | `auto-pm gui`（PySide6 未安装模拟）| 抛 ClickException "QML 模块加载失败" | P2 |
| CLI-GUI-004 | 崩溃捕获安装验证 | `sys.excepthook` 被替换，crash.log 路径就绪 | P2 |

## 5. 现有测试资产映射

| 测试文件 | 覆盖命令组 | 覆盖子命令 | 用例数（approx）| 标记 |
|----------|-----------|-----------|-----------------|------|
| tests/test_smoke.py | 顶层 + Service 层 | CLI `--help`/`--version` 入口、核心模块导入、状态流转合法性 | TestCLIEntry 2 个 + 其他 smoke | smoke |
| tests/cli/conftest.py | （公共 fixture）| cli_runner / cli_env / plc_project_factory / python_project_factory | - | - |
| tests/cli/test_project.py | project + doc.refresh | list / show / create(dry-run) / snapshot(7) / doc refresh(3) | 21 | cli（部分）|
| tests/cli/test_change.py | change | list / show / create / transition / edit | 17 | cli |
| tests/cli/test_doc.py | doc | inject(8) + bracket preservation(2) | 10 | cli/integration |
| tests/cli/test_plc.py | plc | check(9) / init(6) / repair(3) / standardize(4) | 22 | cli |
| tests/cli/test_python.py | python | init(3) / check(7) | 10 | cli |
| tests/cli/test_spec.py | spec | check（边界 TestSpecCLIBoundary）| 1 class | cli |
| tests/cli/test_template.py | template | list(1) / update(2) | 3 | cli |
| tests/cli/test_session.py | pm-session | check / archive / view + group registration | 4 class | cli |
| tests/cli/test_vartable.py | vartable | parse / detect-encoding / list-encodings / help | 4 class | cli |

### 5.1 覆盖缺口识别

| 命令组 | 子命令 | 现有覆盖 | 缺口 |
|--------|--------|----------|------|
| project | edit / delete / retrofit / import | 无 | 全部为缺口（P1/P2）|
| spec | index / frontmatter / report | 仅 check 边界 | index/frontmatter/report 全缺口 |
| vartable | list-formats / detect-format / convert / batch-parse | 仅 parse/detect-encoding/list-encodings | 4 个子命令缺口 |
| gui | gui | 无 CLI 入口测试 | 入口参数解析 + 崩溃捕获缺口 |
| 顶层 | `--version` / envvar / 未知命令 | 仅 `--help` | `--version`/envvar/错误命令缺口 |

### 5.2 测试基础设施

- **CliRunner**：`tests/cli/conftest.py::cli_runner` 提供 `CliRunner(env={})`
- **cli_env**：patch `auto_pm.app_context.setup_logger` 避免日志副作用
- **plc_project_factory**：绕过 Copier 快速创建轻量 PLC 项目（识别标志 `.plc.json`）
- **python_project_factory**：快速创建轻量 Python 项目（识别标志 `.copier-answers.yml` 含 `stack: python`）
- **tmp_workspace**：临时工作空间 fixture（部分测试使用 `tmp_path`）

## 6. 验收标准

1. **P0 用例 100% 通过**：所有冒烟级（P0）用例在 `pytest -m "smoke or cli" --no-cov -q` 下通过
2. **全量回归不退化**：`pytest --no-cov -q` 维持 1115 passed 基线，新增用例不引入失败
3. **退出码契约一致**：成功=0 / 业务错误=1 / 文件查找失败=2 / Click 参数错误=2
4. **JSON 输出纯净**：所有 `--json` 选项的 stdout 为合法 JSON，无非 JSON 文本污染
5. **缺口补测**：第 5.1 节识别的缺口在后续迭代补测，优先级 P1 的子命令（project edit/delete/retrofit、spec index/frontmatter/report、vartable convert/batch-parse）优先补齐
