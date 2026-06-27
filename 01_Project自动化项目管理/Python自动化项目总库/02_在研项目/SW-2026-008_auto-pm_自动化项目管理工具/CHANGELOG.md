# Changelog

本文件记录 auto-pm (SW-2026-008) 的所有变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased] - 2026-06-27

### Added - V0.4.0 Week 3 PLC 工程资产能力

- 新增 `auto_pm/core/asset_summary_service.py`，统一读取 `02_PLC程序/工程资产/` 下 `io_points.csv`、`program_blocks.yml`、`communications.yml` 三类结构化资产
- 新增 `tests/core/test_asset_summary_service.py`，覆盖健康摘要、缺列/缺文件、非 PLC 不适用三类场景

### Changed - Week 3 扫描与 CLI 消费面

- `auto_pm/core/project_scanner.py` 扫描 PLC 项目时自动写入 `extra.asset_summary`
- `auto_pm/cli/project.py` 的 `project show` 新增工程资产摘要输出，展示健康状态、目录状态、IO 点数、程序块数、通讯对象数与问题摘要
- `tests/core/test_project_scanner.py`、`tests/cli/test_project.py` 新增工程资产摘要相关断言

### Verified - Week 3 聚焦回归

- `pytest --no-cov tests/core/test_asset_summary_service.py tests/core/test_project_scanner.py tests/cli/test_project.py tests/plc/test_template_generation.py tests/plc/test_repairer.py tests/plc/test_e2e_plc_workflow.py` → 68 passed
- 真实命令验证：`auto-pm project create --stack plc ...` + `auto-pm project show DJ-2026-333` 可输出“工程资产: 健康 / IO点表: 4 条 / 程序块: 3 个 / 通讯对象: 3 个”

## [0.3.8] - 2026-06-27

### Added - V0.3.8 技术债偿还批次（TD-T10 + TD-T08）

- **T86 TD-T10 台帐脏数据根因修复**：auto_pm/change/ledger_updater.py 新增 `update_status(ledger_path, change_number, status)` 方法（更新台帐状态行）+ `remove(ledger_path, change_number)` 方法（删除台帐行）；auto_pm/change/change_service.py 新增 `_LEDGER_STATUS_MAP`（12 状态→文案映射，含 closed）+ `_find_project_root_from_path` 静态方法（从 CHG 文件路径向上查找项目根目录）+ `transition_status` 方法新增台帐状态回写调用（transition 流转后自动同步台帐状态行）；tests/gui/test_17_edit_change_dialog.py `_cleanup_test_changes` fixture 扩展（删除 CHG 文件后同时调用 `LedgerUpdater.remove` 清理台帐条目）；tests/change/test_ledger_updater.py 新增 8 个单元测试（TestLedgerUpdaterUpdateStatus 4 + TestLedgerUpdaterRemove 4）
- **T87 TD-T08 测试并行化评估**：pyproject.toml dev 依赖新增 `pytest-xdist>=3,<4`；tests/conftest.py `pytest_collection_modifyitems` 改用固定 seed `random.Random(20260627)` 确保 xdist 多 worker 收集一致性
- **T89 CHG-SCPT-2026-072 dogfooding 第五次闭环**：创建 CHG-SCPT-2026-072 + 8 步状态流转 draft→submitted→under_review→approved→implementing→pending_acceptance→accepting→completed→closed 全部成功；transition 自动回写台帐状态验证通过（台帐从🔄实施中→✅已关闭）；填充 §5/§6/§7/§8/§9/§10/§11 真实内容

### Changed - V0.3.8 版本号升级
- pyproject.toml version 0.3.7 → 0.3.8

### Fixed - V0.3.8 根因修复 + 历史脏数据清理

- **TD-T10 台帐脏数据根因修复**：transition 命令流转状态后自动回写台帐状态行（之前需手动更新）；GUI 测试 fixture 清理台帐条目（之前仅删除 CHG 文件不清理台帐）
- **_LEDGER_STATUS_MAP 补充 closed 映射**：T89 dogfooding 流转时发现 `closed` 状态缺少映射（回退为"🔄进行中"），补充 `closed→✅已关闭`
- **台帐历史脏数据清理**：清理 7 条 GUI 测试历史残留脏数据（CHG-065~071 序号 005~011，文件已删除但台帐行残留）；修复 CHG-064 状态为 ✅已关闭

### Verified - V0.3.8 回归测试

- 全量回归：✅ 1163 passed, 1 skipped, 3 warnings in 388.84s（较 V0.3.7 基线 1155 + 8 新增 LedgerUpdater 测试，无回归；3 warnings 为 jinja2 第三方库 DeprecationWarning）
- ruff 0 errors, mypy 0 errors
- T86 单元测试：tests/change/test_ledger_updater.py 19 passed ✅
- T86 GUI 测试：tests/gui/test_17_edit_change_dialog.py 7 passed 1 skipped ✅
- T87 xdist 实测：tests/change/ 串行 158 passed in 39.62s vs 并行 -n 2 158 passed in 492.75s（**xdist 反优化 12 倍**，不采用并行化，改用 --no-cov 加速方案）
- dogfooding: CHG-SCPT-2026-072 完整 8 步生命周期闭环 ✅；change list SW-2026-008 返回 5 条记录（001/062/063/064/072 全 closed）✅；台帐 5 条正确记录全 ✅已关闭/已归档 ✅
- 技术债：20/22 项已偿还，剩余 2 项（TD-A02/TD-TC01）

## [0.3.7] - 2026-06-27

### Added - V0.3.0 Phase 6 发布收口：落地发布 + 证据归档 + 版本切换

- **T80 README 重写**：README.md 8 项更新（功能特性补 M3-2/M3-3/M3-4/M3.5 新能力 + python 命令注释 V1.2.0→V2.5 + change 命令补 edit/--full/show 增强 + GUI 功能补 6 项新功能 + 项目结构 plc-standard→plc-standard-project + 文档导航修正 + 新增 Dogfooding 证据章节 + 工具链关系补充 V2.2/V2.3 吸收计划）
- **T81 CHANGELOG 整理**：CHANGELOG.md [0.3.6] 条目下新增 Fixed 子章节（phase 修复 + ruff 清零 + 台帐重复追加 bug 修复 + 台帐数据清理 185→3 条）；Verified 部分追加 glm5.2 收口后全量回归证据（1155 passed 1 skipped 3 warnings 320s 无回归）
- **T82 发布门禁规范**：新建 `00_项目基础信息/007_发布门禁规范_REL.md` V1.0.0（G1-G5 五项门禁定义：ruff 0 / mypy 0 / pytest 全绿 / 元测试 0 violations / dogfooding CHG 闭环；触发条件 + 标准执行顺序 + 门禁失败处理 + 版本号与门禁关系 + 例外与豁免）
- **T83 试运行证据归档**：新建 `00_项目基础信息/008_试运行报告_PILOT.md` V1.0.0（3 次 Dogfooding 闭环证据 CHG-001/062/063 + 4 项已修复问题 BUG-001/002 + 台帐去重 + CHG-001 内容空白 + 4 项已知限制 + 试运行结论通过 + 后续建议）
- **T84 CHG-SCPT-2026-064 完整生命周期**：创建 CHG-SCPT-2026-064（Phase 6 发布收口）+ 走完整 8 步生命周期（draft→submitted→under_review→approved→implementing→pending_acceptance→accepting→completed→closed）；台帐清理 7 条 GUI 测试残留脏数据（CHG-064~070 序号 004~010）；change list SW-2026-008 返回 4 条 closed 记录；dogfooding 第四次闭环完成

### Changed - V0.3.0 版本号升级
- pyproject.toml version 0.3.6 → 0.3.7

### Fixed - V0.3.7 台帐脏数据复发清理
- 台帐 GUI 测试残留复发：glm5.2 修复后台帐曾清理为 3 条，但全量回归测试时 GUI 测试再次写入 7 条脏数据（CHG-064~070 序号 004~010，无对应文件）；本轮再次清理为 4 条正确记录（001/062/063/064）
- **已知限制记录**：transition 命令不自动更新台帐状态行（仍为"待处理"），需手动更新台帐；GUI 测试 fixture 仅删除 CHG 文件不清理台帐条目，需后续修复（建议新增 TD 项）

### Verified - V0.3.7 Phase 6 回归测试
- 复用 V0.3.6 glm5.2 收口后全量回归基线：✅ 1155 passed, 1 skipped, 3 warnings（无回归，320s；3 warnings 为 jinja2 第三方库 DeprecationWarning）
- ruff 0 errors, mypy 0 errors
- dogfooding: CHG-SCPT-2026-064 完整 8 步生命周期闭环 ✅；change list SW-2026-008 返回 4 条 closed 记录 ✅；台帐 4 条正确记录 ✅

## [0.3.6] - 2026-06-26

### Added - V0.3.0 M3-4 T77-T79: 状态机可视化 + 列表筛选增强 + UI 测试

- **T77 状态机可视化**：auto_pm/ui/dialogs/status_machine_view.py（新增 StatusMachineView QWidget：水平展示 12 状态节点 + 11 箭头；当前状态蓝色边框 + 目标状态绿色填充 + 可达状态可点击 + 不可达状态灰色禁用；节点点击发射 target_selected 信号）；auto_pm/ui/dialogs/transition_dialog.py（集成 StatusMachineView + _on_target_selected 联动更新目标状态/标签/验证结论显隐）
- **T78 列表筛选增强**：auto_pm/models/change.py（ChangeSummary 增加 urgency 字段）；auto_pm/change/parser.py（to_summary 填充 urgency）；auto_pm/change/change_service.py（list_all_changes 增加 urgency 和 project_id 参数，内存筛选）；auto_pm/ui/change_center/change_list_panel.py（新增筛选行：领域下拉 + 紧急程度下拉 + 项目下拉；项目下拉选项从变更单列表动态提取；set_urgency_filter/set_project_filter 方法；blockSignals 防递归）
- **T79 UI 测试**：tests/ui/test_status_machine_view.py（19 测试：渲染 4 + 状态高亮 9 + 信号 3 + 动态更新 3）；tests/ui/test_change_list_panel_filters.py（22 测试：初始加载 4 + 领域 4 + 紧急程度 4 + 项目 4 + 组合 5 + 状态共存 1）；tests/ui/test_change_dialogs.py（新增 TestTransitionDialogStateMachine 7 测试：集成/当前高亮/目标高亮/目标联动/验证结论显隐/可达状态一致性）

### Fixed - V0.3.6-glm5.1/glm5.2 收口（2026-06-26）

- **phase 修复**：auto_pm/core/project_scanner.py（新增 _derive_phase_from_pm_session_content 方法，从 PM_SESSION §2/§8 关键词推导阶段 developing/commissioning/production/archived；`project show` phase 字段从 `-` 恢复为 `developing`）
- **ruff 清零**：scripts/gui_plc_full_test.py（文件级 `# ruff: noqa: E402, T201` + 删除 7 个未使用 import）；scripts/run_tests.py（文件级 `# ruff: noqa: T201`）；tests/gui/test_17_edit_change_dialog.py（2 处 `view = ...` 改为 `_view = ...`）；ruff 34 errors → 0
- **台帐重复追加 bug 修复**：auto_pm/change/ledger_updater.py（update() 添加 `change_number in content` 去重检查，防止重复追加）；auto_pm/change/file_locator.py（generate_change_number() 添加台帐序号 re 扫描，防止文件删除后编号回退）
- **台帐数据清理**：01_版本变更台帐.md 从 185 条脏数据重建为 3 条正确记录（001 archived / 062 closed / 063 closed）

### Verified
- 48 passed（test_status_machine_view + test_change_list_panel_filters + test_change_dialogs，2.17s）
- ruff 0 errors, mypy 0 errors
- 全量回归：✅ 1155 passed, 1 skipped（较 0.3.5 基线 1107 + 48 新增测试，无回归，164s）
- glm5.2 收口后全量回归：✅ 1155 passed, 1 skipped, 3 warnings（无回归，320s；3 warnings 为 jinja2 第三方库 DeprecationWarning）

## [0.3.5] - 2026-06-26

### Added - V0.3.0 M3-4: 创建变更单 QWizard 分步向导

- auto_pm/ui/dialogs/create_change_dialog.py（重写为 QWizard 分步向导：BasicInfoPage 基本信息 7 字段 + DescriptionPage 变更描述 2 字段 + ConfirmPage 提交确认汇总展示；isComplete 联动 Next 按钮；validatePage 触发创建；兼容性保留 CreateChangeDialog 别名 + 构造签名 + change_created 信号 + get_change_data + 内部控件 property + 虚拟 _button_box）
- auto_pm/ui/dialogs/__init__.py（导出 CreateChangeWizard）
- tests/ui/test_change_dialogs.py（新增 TestCreateChangeWizard 5 项测试：3 页面结构 + BasicInfoPage isComplete + DescriptionPage isComplete + ConfirmPage 汇总展示 + validatePage 创建信号；修复预存 mypy 错误：qapp/_patch_message_boxes 返回类型 + type: ignore 错误码）

### Verified
- 16 passed（test_change_dialogs.py，无 coverage 3.09s）
- ruff 0 errors, mypy 0 errors
- 全量回归：✅ 1107 passed, 1 skipped（较 0.3.4 基线 1102 + 5 新增 QWizard 测试，无回归，158s）

## [0.3.4] - 2026-06-26

### Added - V0.3.0 M3-2: 传播链可视化

- auto_pm/ui/change_center/propagation_view.py（新增 PropagationView QGraphicsView：水平展示传播链，圆角矩形节点+箭头连线；_parse_chain 解析 `->`/`→` 分隔符为节点+边；节点显示领域中文名 via DOMAINS 映射；空链"无跨领域影响"提示；DEBUG 级别 tracing 覆盖解析/渲染全过程）
- auto_pm/ui/change_center/change_detail_panel.py（集成传播链视图：在"参考依据"与"审批记录"之间插入"传播链"章节）
- tests/ui/test_propagation_view.py（新增 8 UI 测试：空链/None/单节点/多节点/中文名/Unicode箭头/水平方向/无箭头格式）

### Verified
- 1102 passed, 1 skipped, 3 warnings（较 0.3.3 基线 1094 增加 8 个新测试，无回归）
- ruff 0 errors, mypy 0 errors

## [0.3.3] - 2026-06-26

### Added - V0.3.0 M3-3: 审批时间线

- auto_pm/ui/change_center/approval_timeline.py（新增 ApprovalTimeline 自定义 QWidget：垂直展示变更单状态流转历史，圆点+连接线+状态流转+审批人+意见+日期；12 状态颜色映射；空历史"暂无审批记录"提示）
- auto_pm/change/change_service.py（新增 list_approval_history 方法：委托 ChangeRequestRepository.list_approval_history → ApprovalHistoryRepository.list_by_change，按 id 升序返回审批记录；无 DB 时返回空列表）
- auto_pm/ui/change_center/change_detail_panel.py（集成审批时间线：在"参考依据"与"状态流转按钮"之间插入"审批记录"章节）
- tests/ui/test_approval_timeline.py（新增 7 UI 测试：空历史提示 + 单条/多条记录节点数与连接线 + 状态流转文案 + 审批人意见 + 圆点颜色 + 无 DB 不崩溃）

### Verified
- 1094 passed, 1 skipped, 3 warnings（较 0.3.2 基线 1087 增加 7 个新测试，无回归）
- ruff 0 errors, mypy 0 errors

## [0.3.2] - 2026-06-26

### Added - V0.3.0 M3.5: 真源收口 Round 2 + 产品自洽 Round 2

#### M3.5-1~3: GUI 测试污染清理 + TD-T04 复发修复 + 真源收口 R2
- tests/gui/test_17_edit_change_dialog.py（新增 _cleanup_test_changes autouse fixture，模块级跟踪 + os.remove 删除残留变更单）
- 删除 60 个 GUI 测试残留变更单 CHG-SCPT-2026-002~061
- tests/gui/test_17_edit_change_dialog.py（修复 TD-T04 复发：4 处 `if dlg is not None:` → `assert dlg is not None`）
- spec.md/tasks.md/006_技术债评估报告.md/001_PRD.md/PM_SESSION 五端对齐 1087 passed

#### M3.5-4~5: CHG-SCPT-2026-001 内容补全 + CHG-SCPT-2026-062 完整生命周期
- CHG-SCPT-2026-001.md（§5/§6/§7/§8/§9/§10/§11/§12 全部填充真实内容 + 文档版本 V1.0.0→V2.1.0）
- CHG-SCPT-2026-062.md（V2.1.0 模板创建 + 8 次状态流转走完完整生命周期 draft→submitted→under_review→approved→implementing→pending_acceptance→accepting→completed→closed）

#### M3.5-6: change show 命令增强
- auto_pm/models/change.py（ChangeRequest 新增 `sections: dict[str, str]` 字段，存储按章节号拆分的原始 Markdown 文本）
- auto_pm/change/parser.py（解析时保存 `cr.sections = sections`）
- auto_pm/cli/change.py（新增 `_display_section_6/8/9/10` 四个渲染函数 + `_parse_md_table`/`_extract_subsection`/`_truncate` 辅助函数；cmd_show 调用渲染 §6.1/§6.2/§6.3 + §8.1/§8.2 + §9 + §10.1/§10.2/§10.3 共 10 张 rich.Table）

#### M3.5-7: CLI 表格不截断
- auto_pm/cli/change.py（cmd_list 所有短列 min_width+no_wrap=True + 标题列 ratio=1 吸收剩余空间 + 新增 `--full` 选项标题列 overflow="fold" 自动换行；120 宽度下 8 列完整显示）

#### M3.5-8: 新增 change edit CLI 命令
- auto_pm/cli/change.py（新增 cmd_edit 命令，8 个字符串/枚举字段：§4 background/necessity/references/planned_date/urgency + §6 risk_level/mitigation/propagation_chain；复用 ChangeService.update_change_request；dict 字段 constraint_impacts/domain_impacts 留 GUI EditChangeDialog）
- auto_pm/cli/change.py（修复 _display_section_6 中 risk_level/mitigation 误被 has_constraint 门控的显示 bug + click.exceptions.Exit 误捕获）

### Changed - V0.3.0 版本号升级
- pyproject.toml version 0.3.1 → 0.3.2

### Verified - V0.3.0 M3.5 回归测试
- 全量测试：1087 passed, 1 skipped, 3 warnings（与 M3.5-3 一致，M3.5-6/7/8 为 CLI 增强 + bug 修复，未新增测试文件）

## [0.3.1] - 2026-06-25

### Added - V0.3.0 M2: 影响分析与审批记录持久化

#### M2-1: DB schema 扩展（impact_analysis + approval_history 两张表）
- auto_pm/db/schema.py（新增 DDL_IMPACT_ANALYSIS 和 DDL_APPROVAL_HISTORY 两张表定义 + approval_history 索引；TABLE_DDL/INDEX_DDL 列表更新）
- auto_pm/db/connection.py（drop_all 方法新增 DROP TABLE IF EXISTS approval_history/impact_analysis）
- auto_pm/models/change.py（新增 ImpactAnalysis 和 ApprovalRecord 两个 Pydantic v2 持久化模型）
- auto_pm/models/__init__.py（导出 ImpactAnalysis 和 ApprovalRecord）
- auto_pm/db/repository.py（新增 ImpactAnalysisRepository 类：upsert/get_by_change_number/delete；新增 ApprovalHistoryRepository 类：insert/list_by_change/delete_by_change）
- tests/db/test_repository.py（新增：3 个测试类 19 个测试，覆盖 ImpactAnalysisRepository/ApprovalHistoryRepository/ChangeRequestRepositoryExtension）

#### M2-2: ChangeRequestRepository 扩展（4 个委托方法）
- auto_pm/db/repository.py（ChangeRequestRepository.__init__ 组合 ImpactAnalysisRepository + ApprovalHistoryRepository；新增 4 个委托方法：save_impact_analysis/get_impact_analysis/save_approval_record/list_approval_history）

#### M2-3: ChangeService 集成（DB 持久化同步）
- auto_pm/change/change_service.py（__init__ 新增 ProjectRepository 组合，用于满足 change_requests 表外键约束；create_change_request 同步写入 projects + change_requests + impact_analysis；transition_status 同步写入 approval_history；update_change_request 同步更新 impact_analysis）
- tests/change/test_change_service_db.py（新增：5 个集成测试，覆盖 create/transition/update 的 DB 持久化 + 未注入 DB 向后兼容）

#### M2-4: parser.py 解析增强
- auto_pm/change/parser.py（新增 to_impact_analysis(cr) 方法，将 ChangeRequest 的 §6 影响分析字段转换为 ImpactAnalysis 持久化模型）
- tests/change/test_parser.py（新增：test_to_impact_analysis 和 test_to_impact_analysis_empty_fields 2 个测试）

### Changed - V0.3.0 版本号升级
- pyproject.toml version 0.3.0 → 0.3.1

### Verified - V0.3.0 M2 回归测试
- 全量测试：1055 passed, 3 warnings（较 M1 的 1029 增加 26 个测试）
- tests/db/：19 passed（M2-1 + M2-2 新增）
- tests/change/：含 M2-3 5 个集成测试 + M2-4 2 个解析测试

## [0.3.0] - 2026-06-25

### Added - V0.3.0 M1: 变更单章节结构对齐 040 模板 V2.2.0

#### M1-1: §6.1 风险等级+缓解措施字段（PMBOK 风险评估）
- auto_pm/models/change.py（新增 risk_level 和 mitigation 字段，PMBOK 风险评估）
- auto_pm/change/generator.py（新增 _render_risk_level 方法，§6.1 表格下方渲染风险等级和缓解措施）
- auto_pm/change/parser.py（新增 _parse_risk_level 和 _parse_mitigation 方法）
- tests/change/test_generator.py（新增 test_section_6_1_fields 和 test_section_6_1_fields_default）
- tests/change/test_parser.py（新增 test_parse_risk_level_mitigation 和 test_parse_risk_level_none）

#### M1-2: §10 改为三节结构
- auto_pm/change/generator.py（§10 从 2 节改为 3 节：§10.1 验证项清单 | §10.2 跨领域联动验证 | §10.3 验证结论）
- auto_pm/change/markdown_editor.py（update_verification_conclusion 适配 §10.3，兼容旧 §10.2；append_to_verification_table docstring 更新）
- auto_pm/change/parser.py（_extract_verification_conclusion 适配 §10.3；新增 _extract_conclusion_section_text 和 _parse_cross_domain_verification 方法）
- tests/change/test_generator.py（新增 test_section_10_three_subsections）
- tests/change/test_markdown_editor.py（新增：3 个测试覆盖三节结构下追加验证项、更新 §10.3 结论、向后兼容旧 §10.2）

#### M1-3: §11 版本详细变更说明 + §12 附录
- auto_pm/change/generator.py（§11 从"附录"改为"版本详细变更说明"，新增 §12 附录含填写指南和参考资料）

#### M1-4: 文档版本号对齐 040 模板
- auto_pm/change/generator.py（§1 和文档末尾"文档版本"从 V1.0.0 升级为 V2.1.0，表示基于 V2.1.0 模板生成）
- tests/change/test_generator.py（新增 test_document_version_aligned_with_template）

#### M1-5: 040 §3.4 变更状态字段定义
- 040_通用变更单模板_CHG.md（§3.4 新增"变更状态"字段；frontmatter/§1/文档末尾版本号 V2.1.0→V2.2.0；§2 添加 V2.2.0 条目；§11 添加 V2.2.0 详细变更说明）

### Changed - V0.3.0 版本号升级
- pyproject.toml version 0.2.3 → 0.3.0
- 040 规范模板版本 V2.1.0 → V2.2.0（§3.4 新增变更状态字段）

### Verified - V0.3.0 M1 回归测试
- 全量测试：1029 passed, 3 warnings（较 M0.5 的 1019 增加 10 个测试）
- tests/change/：143 passed（含 M1 新增 10 个测试）

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
