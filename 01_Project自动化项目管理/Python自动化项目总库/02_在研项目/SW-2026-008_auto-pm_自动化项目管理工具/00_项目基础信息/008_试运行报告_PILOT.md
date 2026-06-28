---
doc_id: PILOT-008
title: 试运行报告
version: "V1.4.0"
status: "生效"
created: "2026-06-26"
updated: "2026-06-29"
owner: "fubai"
project_id: "SW-2026-008"
---

# 试运行报告

> 本文件归档 auto-pm (SW-2026-008) 自身使用 CHG-*.md 变更单流程的 Dogfooding 试运行证据。
> 试运行目的：验证 auto-pm 的变更管理能力能否支撑真实项目迭代，发现并修复产品缺陷。
> 适用阶段：V0.3.0 M4 Dogfooding 持续化（每个里程碑必经 CHG-*.md 流程）

## 1. 试运行概述

### 1.1 试运行范围

| 维度 | 范围 |
|------|------|
| 试运行对象 | auto-pm 自身（SW-2026-008） |
| 试运行方式 | auto-pm 使用自己的 `change create/list/show/transition/edit` 命令管理自身迭代 |
| 试运行周期 | 2026-06-25 ~ 2026-06-26（M0 收尾 ~ M4 启动） |
| 闭环次数 | 3 次（CHG-SCPT-2026-001 / 062 / 063） |

### 1.2 试运行目标

1. 验证 `change create` 能正确生成 CHG-*.md 文件并更新台帐
2. 验证 `change transition` 能正确推进 12 状态机（draft→closed 完整流转）
3. 验证 `change show` 能正确渲染 §6/§8/§9/§10 章节内容
4. 验证 `change edit` 能正确更新 §4/§6 字段
5. 验证 `change list` 能正确列出项目变更单
6. 发现产品缺陷并通过真实使用反馈改进

## 2. Dogfooding 闭环证据

### 2.1 CHG-SCPT-2026-001（第一次闭环 — M0 基座清理）

| 字段 | 内容 |
|------|------|
| 变更编号 | CHG-SCPT-2026-001 |
| 申请日期 | 2026-06-25 |
| 完成日期 | 2026-06-25 |
| 变更内容 | M0 基座清理：TD-T01~T04 修复 + ruff/mypy 清理 + 元测试升级（19 项技术债偿还 16 项） |
| 状态流转 | draft→submitted→under_review→approved→implementing→pending_acceptance→accepting→completed→closed→archived |
| 当前状态 | ✅ 已归档 |
| 文档版本 | V1.0.0 → V2.1.0（M3.5-4 补全内容后升级） |

**发现的产品缺陷**：
- BUG-001：`verification_conclusion` 门禁过硬编码（必须字面量"全部通过"），已修复为规则校验
- BUG-002：台帐更新路径解析错误（中文路径被字符级拆分），已修复

**验证结果**：
- 1019 测试通过 + ruff 0 errors + mypy 0 errors + 元测试 0 violations
- `change show CHG-SCPT-2026-001` parser 验证通过（M3.5-4 补全内容后）

### 2.2 CHG-SCPT-2026-062（第二次闭环 — M3.5 真源收口）

| 字段 | 内容 |
|------|------|
| 变更编号 | CHG-SCPT-2026-062 |
| 申请日期 | 2026-06-26 |
| 完成日期 | 2026-06-26 |
| 变更内容 | M3.5 真源收口 + TD-T04 复发修复 + CHG-001 内容补全（8 项任务） |
| 状态流转 | draft→submitted→under_review→approved→implementing→pending_acceptance→accepting→completed→closed（8 步） |
| 当前状态 | ✅ 已关闭 |
| 文档版本 | V2.1.0 |

**验证结果**：
- `change show CHG-SCPT-2026-062` parser 验证通过（status=closed）
- `change list SW-2026-008` 返回 2 条记录（001+062）
- `change show` 增强（M3.5-6）正确渲染 §6/§8/§9/§10 共 10 张 rich.Table

### 2.3 CHG-SCPT-2026-063（第三次闭环 — M4 Dogfooding 启动）

| 字段 | 内容 |
|------|------|
| 变更编号 | CHG-SCPT-2026-063 |
| 申请日期 | 2026-06-26 |
| 完成日期 | 2026-06-26 |
| 变更内容 | phase 修复 + ruff 清零 + M4 Dogfooding 启动 |
| 状态流转 | draft→submitted→under_review→approved→implementing→pending_acceptance→accepting→completed→closed（8 步） |
| 当前状态 | ✅ 已关闭 |
| 文档版本 | V2.1.0 |

**验证结果**：
- `project show SW-2026-008` phase 字段从 `-` 恢复为 `developing`
- `ruff check .` 从 34 errors 降至 0 errors
- `change list SW-2026-008` 返回 3 条记录（001+062+063 全部 closed）
- glm5.2 修复台帐重复追加 bug（LedgerUpdater 去重 + generate_change_number 编号回退防护）

### 2.4 V0.4.0 Week 2~4（第四次闭环 — 单机模板 + 资产台帐 + 文档刷新）

| 字段 | 内容 |
|------|------|
| 试运行编号 | PILOT-V0.4.0-W2-W4 |
| 试运行日期 | 2026-06-27 ~ 2026-06-28 |
| 试运行对象 | `plc-standard-project` 单机设备模板 PoC + `asset_summary` + `doc refresh` |
| 试运行方式 | 用 `project create` 创建准真实单机 PLC 项目，再用 `project show` / `doc refresh --dry-run` / `doc refresh` 验证模板、资产、文档三段闭环 |
| 关键命令 | `project create --stack plc --project-type single_machine ...`、`project show <pid>`、`doc refresh <pid> --dry-run`、`doc refresh <pid>` |
| 当前状态 | ✅ Week 4 已完成 |

**验证结果**：
- Week 2：`project_type/equipment_type/plc_vendor/plc_model` 四个元数据字段已通过 `project create -> project show` 准真实验证，`project show` 可正确显示“单机设备 / 输送设备 / Siemens / S7-1200”
- Week 2：`plc-standard-project` 已补齐 `001_单机设备项目概览_OVW.md` 和 `02_PLC程序/工程资产/{io_points.csv,program_blocks.yml,communications.yml}`，证明“先扩现有模板”可以支撑单机设备 PoC
- Week 3：`ProjectScanner + AssetSummaryService` 已能读取三类资产文件，并在 `project show` 中输出“工程资产健康状态 / IO点表数量 / 程序块数量 / 通讯对象数量 / 问题摘要”
- Week 4：`doc refresh --dry-run` 可预览 2 份 PLC 程序文档中的 3 个自动区变更，`doc refresh` 实际执行时仅替换 `AUTO_PM:BEGIN/END` 标记区块，不覆盖人工内容
- 聚焦回归：Week 4 收口时执行 `pytest --no-cov tests/core/test_doc_refresh_service.py tests/core/test_project_scanner.py tests/cli/test_project.py tests/plc/test_template_generation.py tests/plc/test_repairer.py tests/plc/test_e2e_plc_workflow.py` → `70 passed`

**节省的人工作业**：
- 不再需要手工把 `program_blocks.yml`、`communications.yml`、`io_points.csv` 中的信息重复抄写到 PLC 程序文档的组件清单、资产索引和 IO 概览
- 新建单机项目后，模板、资产样例、概览文档和 CLI 展示口径保持一致，减少了“模板有字段但工具不认识”的人工核对成本

**新增的维护负担**：
- 历史 PLC 项目若文档中没有 `AUTO_PM:BEGIN/END` 标记，当前不会自动刷新，只会返回 issue
- 资产文件字段契约目前只固化到第一版，真实项目落地时还需要继续收敛空值策略、工站命名和字段必填级别
- 首页驾驶舱仍不消费工程资产摘要，单项目层面的价值已经具备，但跨项目可视化仍需后续 GUI 接入

### 2.5 V0.4.2（第五次闭环 — 真实历史 PLC 项目兼容）

| 字段 | 内容 |
|------|------|
| 试运行编号 | PILOT-V0.4.2-DJ-2026-005 |
| 试运行日期 | 2026-06-29 |
| 试运行对象 | `DJ-2026-005` 边框缓存机 PLC 项目（真实历史项目） |
| 试运行方式 | 不要求 PLC 工程师先手工重排历史文档结构，直接对真实项目执行 `project show` / `change list` / `plc check` / `doc inject` / `doc refresh --dry-run`，验证 auto-pm 是否能兼容真实章节编号与历史文档口径 |
| 关键命令 | `project show DJ-2026-005 --json`、`change list DJ-2026-005`、`plc check DJ-2026-005`、`doc inject DJ-2026-005 --json`、`doc refresh DJ-2026-005 --dry-run --json` |
| 当前状态 | ✅ 第二轮验证完成 |

**验证结果**：
- 真实项目基础链路可读：`project show DJ-2026-005 --json` 可正常返回项目描述、库依赖与资产摘要，`change list DJ-2026-005` 可列出 8 条历史变更单
- 首轮只读验证暴露真实问题：`plc check DJ-2026-005` 报 4 个 fail，原因不是项目没有设计文档，而是当前检查仅认 root `PRD/` 标准文档，不识别该真实项目分散在 `00_项目管理/`、`01_需求与设计/`、`02_PLC程序/PLC_ST/PRD/` 的历史口径
- `doc inject DJ-2026-005 --dry-run --json` 初始无法落地，暴露锚点匹配过严问题：真实文档使用 `### 5.1 组件清单与职责`、`## 13. 关联文档索引`、`## 2. 系统硬件配置总览`，而不是模板默认的 `4.1/8/2 IO总览`
- 修复后定向回归 `pytest --no-cov tests/core/test_doc_inject_service.py tests/cli/test_doc.py -q` → `15 passed in 3.27s`
- 修复后实际执行 `doc inject DJ-2026-005 --json` 已成功向 2 份真实程序文档注入 3 个自动区：`plc-program-components`、`plc-asset-index`、`plc-io-overview`
- 注入后 `doc refresh DJ-2026-005 --dry-run --json` 已能无 issue 识别并刷新这 3 个自动区，说明“历史文档 retrofit → 自动区刷新”这条链路在真实项目上可落地
- 第二轮兼容收口后，`plc check DJ-2026-005 --json` 已从 `pass=17 warn=0 fail=4` 变为 `pass=17 warn=4 fail=0`；4 份标准 PRD 文档不再被误判为缺失，而是被识别为落在受控历史目录中的等价文档，并提示“建议后续收口到 PRD/”
- 针对 `plc check` 的历史路径兼容已沉淀为回归资产：`pytest --no-cov tests/plc/test_checker.py -q` → `21 passed in 3.26s`

**节省的人工作业**：
- PLC 工程师不需要先手工把真实历史文档重排成模板编号，工具可以直接识别常见章节变体并完成自动区注入
- 对已有项目启用自动区时，不必整份文档推倒重写，只需要一次 `doc inject` 即可为后续 `doc refresh` 建立入口

**新增的维护负担**：
- `plc check` 现已兼容受控历史路径，但仍会以 `warn` 明确提示“建议后续收口到 PRD/”；这意味着工具从“直接误判 fail”改进为“兼容使用 + 保留标准化压力”，后续仍需持续维护兼容目录白名单
- 当前真实项目 `DJ-2026-005` 仍缺 `02_PLC程序/工程资产`，因此自动区可注入、可刷新，但内容仍以“待补齐/自动统计为空”为主，后续还需评估如何从真实项目资料提取首版资产数据

### 2.6 V0.4.2 Week1（第六次闭环 — 真实项目首版资产补齐）

| 字段 | 内容 |
|------|------|
| 试运行编号 | PILOT-V0.4.2-W1-DJ-2026-005-ASSET |
| 试运行日期 | 2026-06-29 |
| 试运行对象 | `DJ-2026-005` 边框缓存机 PLC 项目（真实历史项目） |
| 试运行方式 | 围绕真实 PLC 项目 `DJ-2026-005`，从 015 IO 分配表 + 016 PLC 程序设计总文档 + 真实 PLC_ST 目录提取首版工程资产，落地 `02_PLC程序/工程资产/` 三文件，验证 `doc refresh` 能否输出真实内容而非“待补齐”占位符 |
| 关键命令 | `project show DJ-2026-005`、`doc refresh DJ-2026-005 --dry-run`、`doc refresh DJ-2026-005` |
| 当前状态 | ✅ 已完成 |

**验证结果**：
- 工程资产三文件首版落地：`io_points.csv` 119 行（CPU DI 21 + CPU DO 18 + DI扩展 36 + DO扩展 24 + 远程IO 20），`program_blocks.yml` 7 块（对齐真实 PLC_ST 目录：OB1/GlobalVars/FB_2001/FB_1002/FB_ExternalDeviceInteraction/FB_1004/FB_1003），`communications.yml` 5 通道（HMI/Upstream/Downstream/RemoteIO/MES）
- `project show DJ-2026-005` 工程资产状态 healthy，IO点表 119 条，程序块 7 个，通讯对象 5 个
- `doc refresh DJ-2026-005 --dry-run`（首次）→ 2 文档 3 自动区全部标记“有变更”
- `doc refresh DJ-2026-005`（实际刷新）→ 2 文档已刷新成功（015 plc-io-overview + 016 plc-program-components + plc-asset-index），自动区内容从“待补齐”变为真实数据
- `doc refresh DJ-2026-005 --dry-run`（二次，幂等性）→ 2 文档 3 自动区全部标记“无变更”，证明刷新幂等
- 回归测试：`pytest tests/core/test_doc_refresh_service.py` → 3 passed（含新增 `test_refresh_with_realistic_assets_emits_real_content_and_idempotent`，覆盖 19 IO/7 blocks/5 channels 真实规模 + 幂等性 + “待补齐”不出现断言）；ruff/mypy 0 errors

**节省的人工作业**：
- PLC 工程师不需要手工维护 015/016 文档中的 IO 概览表和程序块清单表——`doc refresh` 可基于工程资产自动生成，资产变更后一次刷新即可同步
- 016 文档 §5.1 组件清单和 §8 关联文档索引无需手工核对 IO 点数/块数/通道数，自动区会实时统计

**新增的维护负担**：
- 工程资产三文件为半自动首版（从 015/016 文档人工提取），后续若 PLC_ST 目录结构或 IO 分配变化，需同步更新资产文件
- 016 文档设计意图（5 块：PRG_MainControl/FB_1001/FB_1003/FB_1004/FB_2001）与真实 PLC_ST 目录（7 块：OB1/GlobalVars/FB_2001/FB_1002/FB_ExternalDeviceInteraction/FB_1004/FB_1003）存在差异，当前在 responsibility 字段标注，需在 V0.4.3 文档统一阶段收口
- io_points.csv 119 行为人工从 015 文档提取，未与 EPLAN 原理图逐点交叉验证；015 §12 差异表（X14-X17 源程序用途不同、Y24-Y27/Y50 源程序定义）已在 comment 字段标注

## 3. 试运行发现的问题与修复

### 3.1 已修复（4 项）

| 问题 | 严重程度 | 发现于 | 修复于 | 修复方式 |
|------|----------|--------|--------|----------|
| BUG-001 verification_conclusion 门禁过硬编码 | 🟡 中 | CHG-001 闭环 | M0.5 Phase 1 | 改为规则校验（包含"通过"且不包含"不通过"等即放行） |
| BUG-002 台帐路径解析错误（中文路径字符级拆分） | 🟡 中 | CHG-001 闭环 | M0.5 Phase 1 | 修复路径解析逻辑 |
| 台帐重复追加 bug（LedgerUpdater 无去重） | 🟡 中 | CHG-063 闭环后 glm5.2 收口 | 2026-06-26 glm5.2 | update() 添加去重检查 + generate_change_number 添加台帐序号检查 |
| CHG-SCPT-2026-001 内容空白（§5/§6/§7/§8 全部待填写） | 🟡 中 | CHG-062 闭环前 | M3.5-4 | 补全 12 章节真实内容 + 文档版本 V1.0.0→V2.1.0 |
| PLC 文档自动区刷新缺失 | 🟡 中 | V0.4.0 Week 3 收口后 | 2026-06-28 Week 4 | 新增 `DocRefreshService + auto-pm doc refresh`，支持 PLC 程序文档自动区 `dry-run` 预览与实际刷新 |
| 历史 PLC 文档锚点兼容不足 | 🟡 中 | V0.4.2 `DJ-2026-005` 真实试运行 | 2026-06-29 | 放宽 `DocInjectService` 锚点匹配，兼容 `5.1 组件清单与职责` / `13. 关联文档索引` / `2. 系统硬件配置总览` 等真实项目章节变体 |
| 真实老项目 `plc check` PRD 路径误判 | 🟡 中 | V0.4.2 `DJ-2026-005` 真实试运行 | 2026-06-29 | 在 `PlcChecker` 中新增受控历史目录识别；root `PRD/` 缺文档但历史路径存在时降级为 `warn` 并提示后续收口到 `PRD/` |

### 3.2 已知限制（不视为缺陷）

| 限制 | 说明 | 应对 |
|------|------|------|
| `change transition` 不自动追加 §8.1 审批表行 | 需手动编辑 Markdown 补审批记录 | 后续版本可增强 |
| `--verification-conclusion` 在非 completed 流转时日志默认值 | 非阻断，仅日志噪音 | 后续版本可优化 |
| DB 路径未迁移 urgency 字段 schema | urgency 筛选仅在文件扫描模式完整可用 | V2.2 规范中心整合时迁移 |
| 全量测试耗时 320s（无 coverage） | GUI 测试 Qt 环境初始化开销 | TD-T08 pytest-xdist 并行化待偿还 |
| 工程资产摘要尚未进入 GUI | 当前价值主要停留在 CLI/模板/文档刷新 | V0.4.1 优先接入项目概览页，不先扩首页驾驶舱 |

## 4. 试运行结论

### 4.1 达成情况

| 试运行目标 | 达成 | 证据 |
|-----------|------|------|
| `change create` 生成 CHG-*.md + 更新台帐 | ✅ | 3 次创建全部成功，台帐自动追加（glm5.2 修复去重后） |
| `change transition` 12 状态机流转 | ✅ | 3 次完整 draft→closed 流转（CHG-001 额外 archived） |
| `change show` 渲染 §6/§8/§9/§10 | ✅ | M3.5-6 增强后正确渲染 10 张 rich.Table |
| `change edit` 更新 §4/§6 字段 | ✅ | M3.5-8 新增 CLI edit 命令，8 字符串/枚举字段可编辑 |
| `change list` 列出项目变更单 | ✅ | 3 次验证全部返回正确数量（1→2→3 条） |
| 发现产品缺陷并改进 | ✅ | 发现 4 项问题全部修复（BUG-001/002 + 台帐去重 + CHG-001 内容空白） |
| 单机设备模板 PoC 可创建并展示关键元数据 | ✅ | `project create --stack plc --project-type single_machine` + `project show` 验证通过 |
| PLC 工程资产可读取并摘要展示 | ✅ | `asset_summary` 已接入 `ProjectScanner` 和 `project show` |
| PLC 文档自动区可预览并刷新 | ✅ | `doc refresh --dry-run` 与 `doc refresh` 已完成真实命令验证 |
| 真实历史 PLC 文档可 retrofit 自动区 | ✅ | `DJ-2026-005` 已完成 `doc inject --json` 实际注入 3 个自动区，随后 `doc refresh --dry-run --json` 无 issue |
| 真实历史 PLC 项目结构检查可兼容落地 | ✅ | `DJ-2026-005` 的 `plc check --json` 已从 `4 fail` 收口到 `4 warn / 0 fail`，并保留“建议后续收口到 PRD/”提示 |

### 4.2 试运行结论

**通过**。auto-pm 不仅能支撑自身的变更管理闭环，也已经在 V0.4.0 Week 2~4 完成“单机模板 → 工程资产 → 文档自动区刷新”的准真实项目闭环，并在 V0.4.2 首轮把这条链路推进到真实历史 PLC 项目 `DJ-2026-005`。当前产品最值得继续打磨的不是扩张功能面，而是继续缩小真实老项目结构与工具标准口径之间的落差。

### 4.3 后续建议

1. **V0.4.1 主线方向**：优先把工程资产摘要接入 `OverviewTab` 项目概览页，而不是继续扩首页驾驶舱
2. **历史项目兼容**：继续收敛 `plc check` 对真实老项目分散 PRD 目录的识别边界，避免“项目有文档但检查直接 fail”削弱一线工程师对工具的信任
3. **Python 口径补齐**：补 `plc check` 的“不适用”语义，避免驾驶舱把非 PLC 项目误判为失败项
4. **M4 持续化**：每个里程碑（M5+/V2.2+）继续创建 CHG-*.md 走完整流程

## 5. 变更记录

| 日期 | 版本 | 变更 | 操作人 |
|------|------|------|--------|
| 2026-06-26 | V1.0.0 | 初始版本，归档 3 次 Dogfooding 闭环证据（CHG-001/062/063） + 4 项问题修复 + 试运行结论 | glm5.2（Phase 6 T83）|
| 2026-06-28 | V1.1.0 | 新增 V0.4.0 Week 2~4 准真实闭环证据（单机模板 PoC + 资产台帐 + 文档自动区刷新）并明确 V0.4.1 后续方向 | TRAE |
| 2026-06-29 | V1.2.0 | 新增 V0.4.2 真实历史项目 `DJ-2026-005` 首轮 dogfood 证据（真实文档锚点兼容修复 + 自动区实际注入 + `doc refresh --dry-run` 复验）并登记 `plc check` 对分散 PRD 路径的兼容问题 | TRAE |
| 2026-06-29 | V1.3.0 | 补充 V0.4.2 第二轮 dogfood 证据（`PlcChecker` 受控历史 PRD 路径兼容 + `tests/plc/test_checker.py` 回归 + `DJ-2026-005` 结构检查从 `4 fail` 收口到 `4 warn / 0 fail`） | TRAE |

---

> **维护规则**：
> - 每次 Dogfooding 闭环完成后，在本文件追加证据
> - 试运行发现的问题修复后，从"3.1 已修复"移至历史归档
> - 已知限制修复后，从"3.2 已知限制"移除并记录到变更记录
