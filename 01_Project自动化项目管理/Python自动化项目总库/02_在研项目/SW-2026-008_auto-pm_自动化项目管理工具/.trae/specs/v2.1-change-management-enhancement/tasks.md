# V2.1 变更管理增强 - 任务拆解

> 关联 spec.md
> 共 4 个里程碑、17 个任务

## M0：基座清理（V2.0.1 剩余 + 技术债）

### M0-1：V2.0.1-D PLC 规范矛盾代码修复
- [ ] T1: 查阅 906/905/023 规范，定位 41 个矛盾代码片段
- [ ] T2: 逐片段修复 905 §4.3 TIME→DINT 等矛盾
- [ ] T3: 逐片段修复 023 §6.4.2/§6.5.2 TIME→DINT 等矛盾
- [ ] T4: 逐片段修复 906 §3.1 libraryDirectories→libraries 等
- [ ] T5: specmgr check 验证无矛盾告警
- [ ] T6: 更新 005_变更记录_CHG.md

### M0-2：V2.0.1-E spec_registry.json 同步
- [ ] T7: SW-2026-008 注册到 registry（domain: cross-domain, lifecycle: stable）
- [ ] T8: SW-2026-007 标记 deprecated + replaced_by: ["SW-2026-008"]
- [ ] T9: last_updated 更新
- [ ] T10: specmgr check 验证

### M0-3：list_view.py mypy 修复
- [ ] T11: Qt 枚举简写改为限定形式（Qt.AlignTop → Qt.AlignmentFlag.AlignTop 等 8 处）
- [ ] T12: ruff-format 合规
- [ ] T13: mypy auto_pm/ 全绿验证

### M0-4：test_project_list.py flaky 修复
- [ ] T14: isVisible() 改用 isVisibleTo(parent)
- [ ] T15: 纳入 git 跟踪
- [ ] T16: pytest 连续 3 次无 flaky 验证

### M0-5：6 个 UI 测试 QMessageBox 阻塞修复
- [ ] T17: CreateChangeDialog._load_projects 使用 QTimer.singleShot 自动关闭消息框
- [ ] T18: 或注入 mock ProjectService 避免实际加载
- [ ] T19: 6 个测试文件独立运行无阻塞验证

## M1：变更单章节结构修正

### M1-1：§6.1 增加"风险等级"和"缓解措施"字段
- [ ] T20: generator.py §6.1 表格增加"风险等级"和"缓解措施"两列
- [ ] T21: models.py ChangeRequest 增加 risk_level/mitigation 字段
- [ ] T22: parser.py _parse_constraint_impact 解析新增字段
- [ ] T23: 新增单元测试 tests/change/test_generator.py::test_section_6_1_fields
- [ ] T24: 新增单元测试 tests/change/test_parser.py::test_parse_risk_level_mitigation

### M1-2：§10 改为三节结构
- [ ] T25: generator.py §10 增加 §10.2 跨领域联动验证子节，§10.2 验证结论改为 §10.3
- [ ] T26: markdown_editor.py append_to_verification_table 适配 §10.3
- [ ] T27: markdown_editor.py update_verification_conclusion 适配 §10.3
- [ ] T28: parser.py 解析 §10.2 跨领域联动验证
- [ ] T29: 新增单元测试 tests/change/test_generator.py::test_section_10_three_subsections
- [ ] T30: 新增单元测试 tests/change/test_markdown_editor.py::test_append_to_verification_table_v2

### M1-3：§11 版本详细变更说明补全
- [ ] T31: generator.py §11 改为"版本详细变更说明"（含版本号/变更类型/变更内容/影响评估表格）
- [ ] T32: generator.py 原 §11 附录改为 §12
- [ ] T33: parser.py 适配 §11/§12 新结构
- [ ] T34: 新增单元测试 tests/change/test_generator.py::test_section_11_version_details

### M1-4：文档版本号对齐 040 模板
- [ ] T35: 查阅 040 模板当前版本号
- [ ] T36: generator.py 渲染的"文档版本"对齐 040 模板版本
- [ ] T37: 新增单元测试验证版本号一致

### M1-5：040 §3.4 变更状态字段定义
- [ ] T38: 040 V2.2.0 规范 §3.4 申请信息表增加"变更状态"字段定义
- [ ] T39: 更新 040 规范 frontmatter 版本号
- [ ] T40: specmgr check 验证

## M2：影响分析与审批记录持久化

### M2-1：DB schema 扩展
- [ ] T41: schema.py 新增 impact_analysis 表定义
- [ ] T42: schema.py 新增 approval_history 表定义
- [ ] T43: repository.py 新增 ImpactAnalysisRepository 类
- [ ] T44: repository.py 新增 ApprovalHistoryRepository 类
- [ ] T45: 新增单元测试 tests/db/test_repository.py::test_impact_analysis_repo
- [ ] T46: 新增单元测试 tests/db/test_repository.py::test_approval_history_repo

### M2-2：ChangeRequestRepository 扩展
- [ ] T47: 新增 save_impact_analysis(change_number, analysis) 方法
- [ ] T48: 新增 get_impact_analysis(change_number) 方法
- [ ] T49: 新增 save_approval_record(change_number, status, approver, comment) 方法
- [ ] T50: 新增 list_approval_history(change_number) 方法
- [ ] T51: 新增单元测试覆盖 4 个方法

### M2-3：ChangeService 集成
- [ ] T52: transition_status 时同步写入 approval_history 表
- [ ] T53: create_change_request 时同步写入 impact_analysis 表
- [ ] T54: update_change_request 时同步更新 impact_analysis 表
- [ ] T55: 新增集成测试 tests/change/test_change_service_db.py

### M2-4：parser.py 解析增强
- [ ] T56: parser.py 解析 §6.1 风险等级和缓解措施字段（与 M1-1 T22 协同）
- [ ] T57: parser.py 解析 §10.2 跨领域联动验证章节（与 M1-2 T28 协同）
- [ ] T58: parser.py 增加 to_impact_analysis(cr) 方法输出持久化结构
- [ ] T59: 新增单元测试 tests/change/test_parser.py::test_to_impact_analysis

## M3：GUI 变更管理增强

### M3-1：变更单编辑表单
- [ ] T60: 新增 auto_pm/ui/dialogs/edit_change_dialog.py
- [ ] T61: EditChangeDialog 支持修改 background/necessity/references/planned_date/urgency
- [ ] T62: EditChangeDialog 支持修改 §6 影响分析（风险等级/缓解措施/传播链）
- [ ] T63: change_detail_panel.py 集成 EditChangeDialog
- [ ] T64: 新增 UI 测试 tests/ui/test_edit_change_dialog.py

### M3-2：传播链可视化
- [ ] T65: 新增 auto_pm/ui/change_center/propagation_view.py
- [ ] T66: QGraphicsView + 节点连线展示传播链
- [ ] T67: 节点显示领域名称，连线显示传播方向
- [ ] T68: 空传播链显示"无跨领域影响"
- [ ] T69: change_detail_panel.py 集成传播链视图
- [ ] T70: 新增 UI 测试 tests/ui/test_propagation_view.py

### M3-3：审批时间线
- [ ] T71: 新增 auto_pm/ui/change_center/approval_timeline.py
- [ ] T72: 自定义 QWidget 时间线展示（审批环节/审批人/审批意见/审批日期）
- [ ] T73: 从 DB approval_history 表读取审批历史
- [ ] T74: change_detail_panel.py 集成审批时间线
- [ ] T75: 新增 UI 测试 tests/ui/test_approval_timeline.py

### M3-4：变更管理增强
- [ ] T76: create_change_dialog.py 改为分步向导（基本信息 → 影响分析 → 提交）
- [ ] T77: transition_dialog.py 可视化状态机 + 一键流转按钮
- [ ] T78: change_list_panel.py 列表筛选增强（按状态/领域/紧急程度/项目）
- [ ] T79: 新增 UI 测试覆盖向导/流转/筛选

## M4：Dogfooding — auto-pm 自身使用 CHG-*.md 变更单流程

### M4-1：迭代启动 — 创建正式变更单
- [ ] T80: 使用 `auto-pm change create` 创建 CHG-SW-2026-008.md 变更单（domain=SW, project_id=SW-2026-008）
- [ ] T81: 变更单走审批流程 draft → submitted → under_review → approved → implementing
- [ ] T82: 验证 parser 可正确解析新生成的变更单

### M4-2：迭代实施 — 同步实施记录
- [ ] T83: M0 完成后在变更单 §9 追加实施记录条目
- [ ] T84: M1/M2/M3 完成后分别追加实施记录条目
- [ ] T85: 使用 `auto-pm change transition` 流转 implementing → pending_acceptance

### M4-3：迭代验收 — 验证+归档
- [ ] T86: 在变更单 §10 追加验证记录（单元测试/集成测试/端到端/版本号一致性）
- [ ] T87: 走 pending_acceptance → accepting → completed → archived 流程

### M4-4：版本变更台帐
- [ ] T88: 使用 `auto-pm change ledger` 创建版本变更台帐
- [ ] T89: 台帐记录 V0.3.0 迭代全部变更条目
- [ ] T90: 验证 `auto-pm change list` 和 `auto-pm change show` 可正确操作

## 执行顺序

```
M0（基座清理）→ M1（章节结构修正）→ M2（持久化）+ M3（GUI 增强）并行 → M4（Dogfooding）
```

- M0 必须先完成（消除基座问题）
- M1 必须在 M2 之前（章节结构变更影响 parser 输出）
- M2 和 M3 可并行（数据层与 UI 层独立）
- M3-1 依赖 M2-1（EditChangeDialog 需要读取 DB 影响分析）
- M3-3 依赖 M2-2（审批时间线需要读取 DB 审批历史）
- **M4 与 M0-M3 并行推进**：M4-1 在迭代启动时执行；M4-2 随每个里程碑完成同步更新；M4-3/M4-4 在迭代收尾时执行

## 依赖关系图

```
M0-1 ─┐
M0-2 ─┤
M0-3 ─┼─→ M0 出口 → M1-1 ──→ M1-2 ──→ M1-3 ──→ M1-4 ──→ M1-5 ──→ M1 出口
M0-4 ─┤                                                              │
M0-5 ─┘                                                              ↓
                                              ┌─→ M2-1 ──→ M2-2 ──→ M2-3 ──→ M2-4 ──→ M2 出口
                                              │                    │
                                              │                    ↓
                                              └─→ M3-1 ←───────────┘
                                                  M3-2
                                                  M3-3 ←─── M2-2
                                                  M3-4
                                                    │
                                                    ↓
                                                  M3 出口
                                                    │
                                                    ↓
                              M4-1（迭代启动）→ M4-2（随 M0-M3 同步）→ M4-3 + M4-4（迭代收尾）
```
