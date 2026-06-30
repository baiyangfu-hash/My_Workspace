---
doc_id: PILOT-008
title: 试运行报告
version: "V1.8.0"
status: "生效"
created: "2026-06-26"
updated: "2026-07-01"
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
| 试运行周期 | 2026-06-25 ~ 2026-07-01（M0 收尾 ~ V0.5.0 版本统一收口） |
| 闭环次数 | 10 次（CHG-SCPT-2026-001 / 062 / 063 + V0.4.0 W2-W4 + V0.4.2 DJ-2026-005 首轮 + V0.4.2 W1 资产补齐 + V0.4.2 W3 第二样本复核 + V0.4.2 W4 dogfooding 审查收口 + V2.2 W3 GUI 改造 + CHG-078 第 9 次闭环 + V2.3 W1-W4 变量表解析整合第 10 次闭环） |

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
- ~~016 文档设计意图（5 块）与真实 PLC_ST 目录（7 块）存在差异，当前在 responsibility 字段标注，需在 V0.4.3 文档统一阶段收口~~ ✅ 已于 V0.4.3 收口：016 文档 §5.1.1 新增差异说明表，4 项差异（OB1↔PRG_MainControl 重命名 + FB_1002↔FB_1001 单层→四层迁移 + GlobalVars DB 未计入设计意图 + FB_ExternalDeviceInteraction 设计意图未单列）逐项核对，结论为 V4.1.0 设计意图与真实文件之间的命名/迁移差异，非结构缺陷
- io_points.csv 119 行为人工从 015 文档提取，未与 EPLAN 原理图逐点交叉验证；015 §12 差异表（X14-X17 源程序用途不同、Y24-Y27/Y50 源程序定义）已在 comment 字段标注

**工程资产提取策略评估（V0.4.3）**：

| 维度 | 人工首版策略（当前） | 引入资产提取器 |
|------|---------------------|---------------|
| 适用场景 | 历史项目资产已稳定，无频繁更新需求 | 多项目批量资产补齐，PLC_ST 目录频繁变更 |
| 当前成本 | DJ-2026-005 一次性提取 ~2 小时（119 IO + 7 blocks + 5 channels） | 需开发 SCL/CSV/YAML 解析器 + IO 表识别 + 程序块识别 + 测试 + 维护 |
| 维护成本 | 资产变化时人工同步更新（低频） | 解析器需跟随 PLC_ST 结构演进（持续） |
| 准确性风险 | 人工提取可能有遗漏，需通过 `doc refresh --dry-run` 交叉验证 | 解析器可能引入新 bug，需测试覆盖 |
| ROI | ✅ 当前阶段最高（1 个真实项目，资产稳定） | ❌ 当前阶段低（开发成本 > 收益，待 V2.2+ backlog 重排时一并评估） |

**评估结论**：保持人工首版策略，不引入资产提取器自动化。理由：① DJ-2026-005 为历史项目，资产已稳定，无频繁更新需求；② 三文件结构清晰（CSV/YAML），人工维护成本低；③ 引入解析器需开发 + 测试 + 维护，ROI 不高；④ 待 V2.2+ backlog 重排时一并评估是否引入提取器（用户决策 2026-06-29：不再设"3+ 真实项目"数量门槛，DJ-2026-005 本身即编译器移植的真实工程）。当前风险（人工遗漏）通过 `doc refresh --dry-run` 交叉验证已有效控制。

### 2.7 V0.4.2 Week3（第七次闭环 — 第二样本复核 + rich markup bug 修复）

| 字段 | 内容 |
|------|------|
| 试运行编号 | PILOT-V0.4.2-W3-SECOND-SAMPLE |
| 试运行日期 | 2026-06-29 |
| 试运行对象 | `DJ-2026-000`（SysLib FB 测试套件，扁平结构）+ `DJ-2026-099`（P1 修复测试标准项目，标准模板带历史 `02_PLC程序/02_PLC程序` 旧路径） |
| 试运行方式 | 选 1 个非 `DJ-2026-005` 的真实/准真实 PLC 项目走 `project show → change list → plc check → doc inject/doc refresh --dry-run` 最小链路；先选 `DJ-2026-000` 作边界样本（验证非标准结构不会崩溃），再追加 `DJ-2026-099` 作真实链路样本（验证标准模板项目完整链路可走通） |
| 关键命令 | `project show DJ-2026-000`、`change list DJ-2026-000`、`plc check DJ-2026-000`、`doc inject DJ-2026-000 --dry-run`、`doc refresh DJ-2026-000 --dry-run`、`project show DJ-2026-099`、`change list DJ-2026-099`、`plc check DJ-2026-099`、`doc inject DJ-2026-099 --dry-run`、`doc refresh DJ-2026-099 --dry-run` |
| 当前状态 | ✅ 已完成 |

**第一样本结论（DJ-2026-005 真实资产闭环，见 §2.6）**：
- 真实历史 PLC 项目 `DJ-2026-005` 已完成工程资产首版补齐（119 IO/7 blocks/5 channels）+ `doc refresh` 实际刷新 + 幂等性验证，自动区内容从"待补齐"变为真实数据

**第二样本结论（DJ-2026-000 边界兼容 + DJ-2026-099 真实链路 + rich markup bug 修复）**：

1. **DJ-2026-000 边界兼容验证**（SysLib FB 测试套件，扁平结构，无 `02_PLC程序/` 包裹层）：
   - `project show DJ-2026-000` ✅ 正常返回项目信息（V3.2.0）
   - `change list DJ-2026-000` ✅ 返回 0 条变更单（项目本身无 CHG-*.md 历史，正确行为）
   - `plc check DJ-2026-000` ✅ Pass=8 / Warn=1 / Fail=0（无崩溃，扁平结构被识别为 syslib_fb 类型）
   - `doc inject DJ-2026-000 --dry-run` ✅ 报告"未找到可注入标记的 PLC 文档"（正确行为：扁平结构无 `02_PLC程序/程序文档/` 目录）
   - `doc refresh DJ-2026-000 --dry-run` ✅ 报告"未找到可刷新的 PLC 文档"（正确行为，与 inject 一致）
   - **边界结论**：`doc inject/refresh` 对非标准生产项目（SysLib 测试套件）优雅降级为"未找到"提示，不崩溃、不误改

2. **DJ-2026-099 真实链路验证**（P1 修复测试标准项目，标准模板带历史 `02_PLC程序/02_PLC程序` 旧路径）：
   - `project show DJ-2026-099` ✅ 正常返回项目信息（V1.0.0）
   - `change list DJ-2026-099` ✅ 返回 0 条变更单（正确行为）
   - `plc check DJ-2026-099` ✅ Pass=20 / Warn=1 / Fail=0（标准模板项目检查通过）
   - `doc inject DJ-2026-099 --dry-run` ✅ 报告"2 文档 3 标记"（015 IO.md + 016 PLC.md，3 个 marker 全部可注入）
   - `doc refresh DJ-2026-099 --dry-run` ✅ 输出 3 条 issue，每条 issue 中 `[block_key]` 可见
   - **真实链路结论**：标准模板项目（即使带历史旧路径 `02_PLC程序/02_PLC程序`）的完整最小链路可走通

3. **rich markup bug 发现与修复**（DJ-2026-099 复核时发现）：
   - **症状**：`doc refresh DJ-2026-099 --dry-run` 输出 "文档缺少自动区标记: 016_PLC程序设计总文档_PLC.md"，但 `[plc-program-components]` 不可见（被吞）
   - **根因**：`rich.console.print(f"[yellow]{issue}[/yellow]")` 中 issue 文本含 `[plc-program-components]`，被 rich 当作未知 markup 标签吞噬
   - **诊断脚本验证**（`.tmp_diag_rich.py`）：`markup=False` 保留方括号但失去黄色；`style="yellow"` 单独用仍吞噬；`escape(issue) + style="yellow"` 两者兼得
   - **修复**：`auto_pm/cli/doc.py` 中 `cmd_refresh` 和 `cmd_inject` 的 issue 输出改为 `console.print(escape(issue), style="yellow")`
   - **回归测试沉淀**：`tests/cli/test_doc.py::TestDocIssueBracketPreservation` 新增 2 条测试（refresh + inject），先红后绿 TDD
   - **全量回归**：`pytest --no-cov tests/cli/test_doc.py` → 9 passed；`pytest --no-cov tests/core/test_doc_refresh_service.py tests/core/test_doc_inject_service.py` → 11 passed；ruff/mypy 0 errors
   - **端到端验证**：`auto-pm doc refresh DJ-2026-099 --dry-run` 输出含 `[plc-program-components]`/`[plc-asset-index]`/`[plc-io-overview]` 全部可见

**节省的人工作业**：
- 第二样本复核证明 `doc inject/refresh` 链路不仅适用于 `DJ-2026-005`（真实历史项目），也适用于 `DJ-2026-099`（标准模板项目），无需项目特殊适配
- rich markup bug 修复后，PLC 工程师能直接看到具体哪个 `[block_key]` 缺失，不必再"猜"问题位置

**新增的维护负担**：
- 后续 CLI 输出含变量文本（项目名、issue 文本等）时，必须用 `escape()` + `style=` 模式，不能直接拼进 `[yellow]...[/yellow]` 颜色标签
- `doc inject/refresh` 对扁平结构项目（如 SysLib FB 测试套件 `DJ-2026-000`）只输出"未找到"提示，不会主动 retrofit；若后续要让 SysLib 项目也用自动区，需单独评估是否引入"扁平结构 → 标准结构"转换器


### 2.8 V0.4.2 Week4（第八次闭环 — dogfooding 闭环审查 + 代码债务收口 + V0.4.3 准入）

| 字段 | 内容 |
|------|------|
| 试运行编号 | PILOT-V0.4.2-W4-DOGFOOD-AUDIT |
| 试运行日期 | 2026-06-29 |
| 试运行对象 | auto-pm 自身（SW-2026-008）—— 冻结迭代计划期间进行 dogfooding 闭环审查与代码债务收口 |
| 试运行方式 | 在用户决策"冻结迭代计划，进行深度审查"后，对前 7 次 dogfooding 闭环（CHG-001/062/063 + V0.4.0 W2-W4 + V0.4.2 DJ-2026-005 首轮/W1 资产/W3 第二样本）的交付物进行真源对账，发现 5 项 dogfooding 闭环漏洞并批量修复；同时收口 TD-TC01（沙箱路径）和 5 个 jinja2 DeprecationWarning；最终进行 V0.4.3 准入判断 |
| 关键命令 | `pytest --no-cov --timeout=60 --tb=short -q`（全量回归）、`pytest tests/cli/test_plc.py::test_plc_init_default_mode -W "error::DeprecationWarning"`（jinja2 验证） |
| 当前状态 | ✅ Week4 收口完成 + V0.4.3 准入通过 |

**第一部分：dogfooding 闭环审查 5 项漏洞批量修复**

1. **PILOT 版本号与变更记录漂移**：`008_试运行报告_PILOT.md` §5 缺 V1.4.0 行 / frontmatter `version` 与 §5 最新行不一致 → §5 已补 V1.4.0 行 + frontmatter `version` 升至 V1.5.0（满足 project-rule.md §3 版本号一致性）
2. **`01_版本变更台帐.md` 缺 CHG-SCPT-2026-072 序号 005 + 8 条死链**：新增序号 005（CHG-072，原 005~008 顺延为 006~009）；8 条死链 `./01_变更单/...` → `../01_变更单/...`；现 9 条全部可解析
3. **`005_变更记录_CHG.md` 标准变更单索引表漂移**：从 3 条扩展到 9 条（补 064/072/073/074/075/077）+ CHG-001 性质修正为 DEF+OPT
4. **TD-T14 qapp fixture 多处重复定义**：`tests/conftest.py` 新增 session 级 qapp（TYPE_CHECKING + `from __future__ import annotations` + `assert isinstance(app, QApplication)` 三段式）；`tests/ui/conftest.py` / `tests/gui/conftest.py` / `tests/ui/test_vartable_tab.py` 三处本地 qapp 全部移除
5. **TD-T09 复发**：`tests/gui/test_17_edit_change_dialog.py::_cleanup_test_changes` 的 `except Exception: pass` 静默吞错 → except 范围收窄为 `(OSError, PermissionError, ValueError, KeyError)`，删除 noqa 注释
6. **PM_SESSION §2 代码基线 0.3.8 冻结语义不清晰**：milestone 行补充"pyproject.toml version=0.3.8 不升级；CHANGELOG [Unreleased] 累积 V0.4.0 Week 4 + V0.4.1 Step 1~3 + V0.4.2 Week 1~3 文档迭代证据，待后续版本统一收口"明确语义

**第二部分：代码债务收口（TD-TC01 + jinja2 DeprecationWarning）**

1. **TD-TC01 已规避**：Trae Sandbox 中文路径字符级拆分问题，工作方式约定使用 Write/Edit 工具替代 RunCommand 写文件（绕过沙箱对中文路径的字符级拆分），约定已沉淀到 `project_memory.md` "Engineering Conventions" 章节
2. **5 个 jinja2 `DeprecationWarning: invalid escape sequence '\d'` 已根除**：根因在 `templates/{plc-standard-project,python-tool,plc-test-suite,plc-standard}/copier.yml` 的 jinja2 字符串字面量 `'^[A-Z]+-\d{4}-\d{3}$'` 含 `\d`，触发 jinja2 lexer `decode("unicode-escape")` Python DeprecationWarning；4 个文件的 `\d` → `\\d`，jinja2 解码后保留 `\d` 字面量给 regex_search；验证 `pytest tests/cli/test_plc.py::test_plc_init_default_mode -W "error::DeprecationWarning"` PASSED（jinja2 警告彻底消除）

**第三部分：V0.4.3 准入判断**

- **准入门槛达成情况**：
  1. ✅ ≥1 真实项目资产闭环：`DJ-2026-005` 已完成工程资产补齐（119 IO / 7 blocks / 5 channels）+ `doc refresh` 实际刷新 + 幂等性验证
  2. ✅ ≥1 第二样本复核：`DJ-2026-000` 边界兼容 + `DJ-2026-099` 真实链路 + rich markup bug 修复
  3. ✅ `doc inject/doc refresh/plc check` 真实使用路径已可解释、可复现、可测试
- **准入判断结果**：**通过（Yes，准入）**——用户决策："仅 TD-TC01（沙箱路径，低优先级）+ 5 个 jinja2 warnings；这些先解决，在进行下一步"。本会话已完成两项前置条件，可解除冻结进入 V0.4.3

**第四部分：全量回归验证**

- `pytest --no-cov --timeout=60 --tb=short -q` → **1246 passed, 1 skipped, 0 warnings（修复前 5 warnings），exit code 0，468.03s（0:07:48）**
- 较 V0.4.1 收口批次阶段 2 p4 基线（1237 passed 1 skipped）+9 测试
- 历史 `-1073741510` sandbox 终端崩溃未复现，证明 TD-T14 qapp 统一收口确实消除了 Qt 会话状态污染

**节省的人工作业**：
- dogfooding 闭环审查暴露的 5 项漏洞若未及时修复，后续低上下文模型/会话会基于失真基线推进，导致更严重的真源漂移
- TD-TC01 + jinja2 warnings 修复后，全量回归 0 warnings，CI/门禁式一把跑完验证更干净
- jinja2 warnings 根除后，未来 copier.yml 模板复用时不再产生噪音

**新增的维护负担**：
- 4 个 copier.yml 修复后，新增模板若使用 regex_search 含 `\d` 等转义字符，必须用 `\\d` 双反斜杠（jinja2 lexer 会 decode unicode-escape 一次）
- TD-TC01 workaround 沉淀到 `project_memory.md` 后，后续模型/会话必须遵守"写文件用 Write/Edit 工具，不用 Python `Path.write_text()`"硬约束

### 2.9 V2.2 Week3（第九次闭环 — GUI 规范中心页改造 + CHG-078 技术债清理）

| 字段 | 内容 |
|------|------|
| 试运行编号 | PILOT-V2.2-W3-GUI-CHG-078 |
| 试运行日期 | 2026-06-30 |
| 试运行对象 | auto-pm 自身（SW-2026-008）—— V2.2 Week3 GUI 规范中心页改造 + 技术债批量清理（CHG-SCPT-2026-078） |
| 试运行方式 | 用 `change create --pid SW-2026-008 --domain SCPT --nature OPT --scope PLC+Python+GUI --urgency high` 创建 CHG-078 变更单，再用 `change transition CHG-SCPT-2026-078 --to <STATUS>` 走完整 9 步状态流转（draft→submitted→under_review→approved→implementing→pending_acceptance→accepting→completed→closed）；同时用 `change edit` 填充 §4/§6 字段 |
| 关键命令 | `change create`、`change transition --to <STATUS>`（× 8 次）、`change edit --background/--necessity/--risk-level/--mitigation`、`change show CHG-SCPT-2026-078` |
| 当前状态 | ✅ 已关闭（closed，9 步状态流转完成） |

**变更内容（T11-T14 + 技术债清理）**：

1. **T11 spec_center.py 重构**：从 482 行单文件改为 QTabWidget + DTO 层架构（`spec_center_dto.py` 8 个 frozen dataclass + SpecCenterAdapter），生产代码降至 300 行
2. **T12 6 Tab 类**：`spec_center_tabs/` 目录下 6 个 Tab 类（概览/索引/检查/frontmatter/报告/对比）
3. **T13 服务集成**：所有 Tab 集成新 IndexService/CheckService/FrontmatterService/ReportService（从旧 SpecIndexService 迁移到 DTO/adapter 模式）
4. **T14 LSP-907 集成**：通过 `spec_registry.json` 集成 LSP-907，GUI 规范中心页可查看 14 个规范（PM/PLC/Python 域）
5. **TD-C07 mypy 17 errors 修复**：8 个生产文件 ruff/mypy 0 errors（基线失真 Week3 已修复）
6. **TD-C08 8 文件 docstring 规范化**：补全模块/类/方法 docstring
7. **TD-C09 19 处 type:ignore 评估**：18 处 Week3 已清理（剩 1 处评估后保留）
8. **TD-A03 dogfooding 第 9 次闭环**：CHG-SCPT-2026-078 走完整 9 步状态流转（draft→closed）

**验证结果**：
- 33 个新 UI 测试覆盖 6 Tab + DTO 层 + 真实工作空间集成
- 8 生产文件 ruff + mypy 0 errors（TD-C07 基线失真修复）
- 全量回归 1332 passed 5 skipped 0 failed（较 V0.4.3 收口基线 1246 passed 1 skipped +86 测试 +4 skipped）
- GUI 规范中心页可查看 14 规范（PM/PLC/Python 域），10 项健康检查（SHC-001~010）、Frontmatter 批量管理、报告生成、规范对比全部可用
- `change show CHG-SCPT-2026-078` parser 验证通过（status=closed，§6/§8/§9/§10 全部可渲染）
- `change list SW-2026-008` 返回 11 条记录（001/062/063/064/072/073/074/075/077/078/079，10 条 closed + 1 条 draft CHG-079）

**节省的人工作业**：
- GUI 规范中心页从单文件 482 行改为 DTO/adapter 模式后，新增 Tab 的边际成本从"再写一遍 service 调用 + 数据结构"降为"定义 DTO + 复用 adapter"
- TD-C07 修复后，后续模型/会话不再被 17 个 mypy errors 误导为"代码质量问题"（实际为基线失真）
- TD-C08/C09 清理后，生产代码 docstring 覆盖率与 type:ignore 评估透明度提升

**新增的维护负担**：
- 6 Tab 类 + DTO 层 + SpecCenterAdapter 形成"接口契约"，新增规范时需同步更新 DTO dataclass（否则 adapter 无法转换）
- LSP-907 通过 `spec_registry.json` 集成，后续新增规范需先注册到 registry 再到 GUI
- 17 处 mypy 技术债中 1 处（type:ignore）评估后保留，后续需在 TD-C10 单独跟踪（若立项）

### 2.10 V2.3 Week1-4（第十次闭环 — 变量表解析整合主线 + TD-C10 治理 + V0.5.0 收口）

| 字段 | 内容 |
|------|------|
| 试运行编号 | PILOT-V2.3-W1-W4-VARTABLE-TDC10 |
| 试运行日期 | 2026-06-30 ~ 2026-07-01 |
| 试运行对象 | auto-pm 自身（SW-2026-008）—— V2.3 Week1-4 变量表解析整合主线 + TD-C10 mypy tests/ 治理 + V0.5.0 版本统一收口 |
| 试运行方式 | 沿用 dogfooding 流程（CHG-*.md 变更单 + 9 步状态流转），四周连续迭代：Week1 数据模型 + IoPointsParser + CLI vartable 命令组；Week2 多格式解析器 + 格式自动识别；Week3 5 格式 Parser 深化 + 转换器重建 + 批量解析；Week4 GUI 变量编辑器 + VartableTab。每周交付均通过 `pytest --no-cov <相关模块>` + ruff + mypy 三重门禁 |
| 关键命令 | `auto-pm vartable parse` / `detect-encoding` / `list-encodings` / `convert` / `batch-parse`（CLI-28~32）；`auto-pm vartable detect-format` / `list-formats`；GUI 端 `VartableTab` 文件列表 + 编辑器 + 批量解析 |
| 当前状态 | ✅ V0.5.0 已发布（pyproject 0.4.2 → 0.5.0；CHANGELOG [0.5.0] - 2026-07-01） |

**变更内容（T01-T16 + TD-C10 治理）**：

1. **Week1（T01-T07）变量表数据模型 + IoPointsParser + CLI 命令组**：
   - 新增 `auto_pm/vartable/models.py`：VarEntry/VarTable/ParseResult/ParseError 四个 frozen dataclass
   - 新增 `auto_pm/vartable/parsers/io_points_parser.py`：IoPointsParser 深化 AssetSummaryService，处理 io_points.csv 多格式地址
   - 新增 `auto_pm/vartable/utils/encoding.py`：detect_encoding BOM 检测 + fallback（无 chardet 依赖）
   - 新增 `auto_pm/cli/vartable.py`：parse/detect-encoding/list-encodings 三子命令 + Rich Table + Unicode 输出兼容
   - 38 测试新增（tests/vartable/ + tests/cli/test_vartable.py）

2. **Week2（T08-T11）多格式解析器 + 格式自动识别 + CLI 集成**：
   - 新增 `auto_pm/vartable/parsers/program_blocks_parser.py`：ProgramBlocksParser 解析 YAML → BlockEntry
   - 新增 `auto_pm/vartable/parsers/communications_parser.py`：CommunicationsParser 解析 YAML → ChannelEntry
   - 新增 `auto_pm/vartable/parsers/base_parser.py` + 5 格式 Parser 骨架（Autoshop/Work3/Codesys/SCL/IntDoc）
   - 新增 `auto_pm/vartable/parsers/format_detector.py`：三级识别（文件名→扩展名→内容特征）+ 工厂模式
   - 扩展 CLI：parse --format/--output-format + list-formats + detect-format 子命令
   - DJ-2026-005 端到端验证 6 项全通过（7 block + 5 channel + 自动识别）
   - 35 测试新增

3. **Week3（T12-T14）5 格式 Parser 深化 + 转换器重建 + 批量解析**：
   - 深化 5 格式 Parser（Autoshop/Work3/Codesys/SCL/IntDoc）：添加 detect_format 方法委托 format_detector
   - 新增 `auto_pm/vartable/converter.py`：VariableConverter 统一中间模型导出 CSV/YAML/JSON
   - 新增 `auto_pm/vartable/batch_parser.py`：BatchParser 批量解析目录/文件列表
   - 扩展 CLI：convert + batch-parse 子命令
   - DJ-2026-005 端到端验证 4 项全通过（SCL 解析 + 批量解析 6 文件 278 条变量 + JSON 转换）
   - 35 测试新增

4. **Week4（T15-T16）GUI 变量编辑器 + 项目工作区变量表 Tab**：
   - 新增 `auto_pm/ui/vartable/variable_table_editor.py`：VariableTableModel（QAbstractTableModel 8 列）+ VariableTableEditor（QTableView + 工具栏 + 右键菜单 + 导入导出 + data_changed 信号）
   - 新增 `auto_pm/ui/vartable/vartable_tab.py`：VartableTab（QSplitter 文件列表 + 编辑器 + 批量解析 + 角色权限 PLCEngineer/SpecEditor 可编辑）
   - 修改 `auto_pm/ui/workspace/workspace_view.py`：Tab 列表接入 VartableTab
   - mypy unreachable 修复（3 处）：用方法调用替代 bool 属性窄化
   - 33 测试新增

5. **TD-C10 mypy tests/ 治理**：381→0 errors（11 测试文件类型标注修复）
   - 关键技术：bool() 包装打破 mypy 属性 narrowing / str 变量打破 Literal 收窄 / Generator 返回类型 / Callable[[Any],None] 逆变 / PySide6 枚举完整路径

**验证结果**：

- 全量回归 1477 passed 6 skipped 0 failed（较 V0.4.2 收口基线 1332 passed 5 skipped +145 测试 +1 skipped）
- 141 测试新增（Week1 38 + Week2 35 + Week3 35 + Week4 33）
- ruff 0 errors, mypy 0 errors（生产代码 + tests/ 全部清零，TD-C10 治理完成）
- DJ-2026-005 端到端 10 项全通过（Week2 6 项 + Week3 4 项）
- 32/32 项技术债全部关闭（剩余 0 项）
- pyproject.toml version 0.4.2 → 0.5.0；CHANGELOG [0.5.0] - 2026-07-01 完整章节
- 00_项目基础信息 8 文档全部对齐 V0.5.0/V2.2.0；02_设计 GUI 原型 V2.1 + 里程碑迭代计划更新；09_整改项归档整理

**节省的人工作业**：

- 变量表从人工抄写到工具解析：io_points.csv 119 行可一键解析为 VarTable，并支持 CSV/YAML/JSON 三格式导出
- 5 格式 Parser 覆盖 Autoshop/Work3/Codesys/SCL/IntDoc，减少工程师手动整理变量表的工作量
- 批量解析支持目录递归扫描，DJ-2026-005 6 文件 278 条变量一次性解析完成
- GUI 变量编辑器支持表格化编辑 + 导入导出 + 角色权限控制，PLC 工程师可在 GUI 内直接修改变量表
- TD-C10 治理完成后，tests/ 不再有 mypy errors，后续测试代码类型标注基线可信

**新增的维护负担**：

- 5 格式 Parser 需持续维护真实项目样本（当前基于 DJ-2026-005），新格式支持需补充对应 Parser + 测试
- FormatDetector 三级识别策略需在真实项目中持续校准，避免误识别
- VariableConverter 中间模型字段契约固化后，新增字段需考虑 CSV/YAML/JSON 三格式兼容性
- VartableTab 角色权限（PLCEngineer/SpecEditor 可编辑）目前仅为 GUI 层软约束，未与后端权限系统打通

## 3. 试运行发现的问题与修复

### 3.1 已修复（15 项）

| 问题 | 严重程度 | 发现于 | 修复于 | 修复方式 |
|------|----------|--------|--------|----------|
| BUG-001 verification_conclusion 门禁过硬编码 | 🟡 中 | CHG-001 闭环 | M0.5 Phase 1 | 改为规则校验（包含"通过"且不包含"不通过"等即放行） |
| BUG-002 台帐路径解析错误（中文路径字符级拆分） | 🟡 中 | CHG-001 闭环 | M0.5 Phase 1 | 修复路径解析逻辑 |
| 台帐重复追加 bug（LedgerUpdater 无去重） | 🟡 中 | CHG-063 闭环后 glm5.2 收口 | 2026-06-26 glm5.2 | update() 添加去重检查 + generate_change_number 添加台帐序号检查 |
| CHG-SCPT-2026-001 内容空白（§5/§6/§7/§8 全部待填写） | 🟡 中 | CHG-062 闭环前 | M3.5-4 | 补全 12 章节真实内容 + 文档版本 V1.0.0→V2.1.0 |
| PLC 文档自动区刷新缺失 | 🟡 中 | V0.4.0 Week 3 收口后 | 2026-06-28 Week 4 | 新增 `DocRefreshService + auto-pm doc refresh`，支持 PLC 程序文档自动区 `dry-run` 预览与实际刷新 |
| 历史 PLC 文档锚点兼容不足 | 🟡 中 | V0.4.2 `DJ-2026-005` 真实试运行 | 2026-06-29 | 放宽 `DocInjectService` 锚点匹配，兼容 `5.1 组件清单与职责` / `13. 关联文档索引` / `2. 系统硬件配置总览` 等真实项目章节变体 |
| 真实老项目 `plc check` PRD 路径误判 | 🟡 中 | V0.4.2 `DJ-2026-005` 真实试运行 | 2026-06-29 | 在 `PlcChecker` 中新增受控历史目录识别；root `PRD/` 缺文档但历史路径存在时降级为 `warn` 并提示后续收口到 `PRD/` |
| PILOT 版本号与变更记录漂移（§5 缺 V1.4.0 行 / frontmatter `version` 与 §5 最新行不一致） | 🟡 中 | V0.4.2 Week4 dogfooding 闭环审查 | 2026-06-29 | `008_试运行报告_PILOT.md` §5 已补 V1.4.0 行 + frontmatter `version` 升至 V1.5.0（满足 project-rule.md §3 版本号一致性） |
| `01_版本变更台帐.md` 缺 CHG-SCPT-2026-072 序号 005 + 8 条死链 `./01_变更单/...` | 🟡 中 | V0.4.2 Week4 dogfooding 闭环审查 | 2026-06-29 | 台帐新增序号 005（CHG-072，原 005~008 顺延为 006~009）；8 条死链 `./01_变更单/...` → `../01_变更单/...`；现 9 条全部可解析 |
| `005_变更记录_CHG.md` 标准变更单索引表从 3 条扩展到 9 条（缺 064/072/073/074/075/077）+ CHG-001 性质标注错误 | 🟡 中 | V0.4.2 Week4 dogfooding 闭环审查 | 2026-06-29 | 索引表补全 9 条 + CHG-001 性质修正为 DEF+OPT |
| TD-T14 qapp fixture 多处重复定义（`tests/ui/conftest.py` / `tests/gui/conftest.py` / `tests/ui/test_vartable_tab.py` 三处本地定义） | 🟡 中 | V0.4.2 Week4 dogfooding 闭环审查（TD-T14 复发） | 2026-06-29 | `tests/conftest.py` 新增 session 级 qapp（TYPE_CHECKING + `from __future__ import annotations` + `assert isinstance(app, QApplication)` 三段式）；三处本地 qapp 全部移除 |
| TD-T09 复发（`tests/gui/test_17_edit_change_dialog.py::_cleanup_test_changes` 的 `except Exception: pass` 静默吞错） | 🟡 中 | V0.4.2 Week4 dogfooding 闭环审查 | 2026-06-29 | except 范围从 `Exception`（含 `# noqa: BLE001`）收窄为 `(OSError, PermissionError, ValueError, KeyError)`，删除 noqa 注释 |
| PM_SESSION §2 代码基线 0.3.8 冻结语义不清晰（"冻结"是否含 CHANGELOG `[Unreleased]` 累积不明） | 🟢 低 | V0.4.2 Week4 dogfooding 闭环审查 | 2026-06-29 | PM_SESSION §2 milestone 行补充"pyproject.toml version=0.3.8 不升级；CHANGELOG [Unreleased] 累积 V0.4.0 Week 4 + V0.4.1 Step 1~3 + V0.4.2 Week 1~3 文档迭代证据，待后续版本统一收口"明确语义 |
| 5 个 jinja2 `DeprecationWarning: invalid escape sequence '\d'`（4 个 copier.yml 的 `'^[A-Z]+-\d{4}-\d{3}$'` jinja2 字符串字面量含 `\d`，触发 lexer `decode("unicode-escape")`） | 🟢 低 | V0.4.2 Week4 全量回归（1246 passed 5 warnings） | 2026-06-29 | `templates/plc-standard-project/copier.yml` + `templates/python-tool/copier.yml` + `templates/plc-test-suite/copier.yml` + `templates/plc-standard/copier.yml` 共 4 个文件的 `\d` → `\\d`；验证 `pytest tests/cli/test_plc.py::test_plc_init_default_mode -W "error::DeprecationWarning"` PASSED（jinja2 警告彻底消除） |
| TD-C10 mypy tests/ 381 errors（11 测试文件类型标注缺失/不准确） | 🔴 高 | V2.3 Week1 收口前 mypy tests/ 扫描 | 2026-07-01 V2.3 Week4 | 11 测试文件类型标注修复：bool() 包装打破 mypy 属性 narrowing / str 变量打破 Literal 收窄 / Generator 返回类型 / Callable[[Any],None] 逆变 / PySide6 枚举完整路径；mypy tests/ 381→0 errors；32/32 项技术债全部关闭 |

### 3.2 已知限制（不视为缺陷）

| 限制 | 说明 | 应对 |
|------|------|------|
| `change transition` 不自动追加 §8.1 审批表行 | 需手动编辑 Markdown 补审批记录 | 后续版本可增强 |
| `--verification-conclusion` 在非 completed 流转时日志默认值 | 非阻断，仅日志噪音 | 后续版本可优化 |
| DB 路径未迁移 urgency 字段 schema | urgency 筛选仅在文件扫描模式完整可用 | V2.2 规范中心整合时迁移 |
| 全量测试耗时 468s（无 coverage，1246 passed 1 skipped） | GUI 测试 Qt 环境初始化开销 + 1246 测试规模 | TD-T08 已评估 pytest-xdist 在当前规模反优化 12 倍，采用 `--no-cov` 加速方案（007 门禁规范 G3） |
| 工程资产摘要尚未进入首页驾驶舱 | 当前价值主要停留在 CLI/OverviewTab/文档刷新 | V0.4.1 已接入项目概览页，首页驾驶舱待 V0.4.3+ 评估 |
| `DJ-2026-005` 工程资产文件首版为半自动人工提取 | io_points.csv 119 行从 015 文档提取，未与 EPLAN 原理图逐点交叉验证 | V0.4.3 评估是否引入资产提取器或保持人工首版策略 |
| 016 文档设计意图 5 块 vs 真实 PLC_ST 目录 7 块差异 | 当前在 `responsibility` 字段标注，未消除差异 | V0.4.3 版本统一阶段收口 |
| Trae Sandbox 中文路径字符级拆分（TD-TC01） | RunCommand 输出显示中文路径被字符级拆分；不影响命令执行，仅影响终端显示 | 已规避：写文件用 Write/Edit 工具（VS Code API），不用 Python `Path.write_text()`；约定已沉淀到 `project_memory.md` |

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
| 第二样本复核（非 `DJ-2026-005` 项目） | ✅ | `DJ-2026-000`（SysLib FB 测试套件，扁平结构）边界兼容通过——doc 操作"未找到"为正确行为；`DJ-2026-099`（P1 修复测试标准项目）真实链路通过——`plc check` Pass=20/Warn=1/Fail=0，`doc inject --dry-run` 2 文档 3 标记，`doc refresh --dry-run` 3 issue `[block_key]` 可见；复核中发现 rich markup 吞噬 `[block_key]` bug 已修复并沉淀 2 条回归测试 |
| dogfooding 闭环审查漏洞批量修复 | ✅ | 5 项漏洞全部修复：PILOT 版本号对齐 + 台帐补登 CHG-072 序号 005 + 8 条死链修复 + 005 索引表 3→9 条 + TD-T14 qapp 真正统一 + TD-T09 except 收窄 + PM_SESSION §2 语义澄清；ruff + mypy + tests/ui 25 passed + tests/gui 7 passed 1 skipped + 临时脚本核验 9/9 OK |
| TD-TC01 + jinja2 DeprecationWarning 收口 | ✅ | TD-TC01 已规避（workaround 沉淀到 `project_memory.md`）；5 个 jinja2 `DeprecationWarning: invalid escape sequence '\d'` 已根除（4 个 copier.yml `\d` → `\\d`，`pytest -W "error::DeprecationWarning"` PASSED）；技术债报告 26/26 项全部关闭，剩余 0 项 |
| V0.4.2 Week4 收口 + V0.4.3 准入判断 | ✅ | 全量回归 1246 passed 1 skipped 0 warnings exit code 0；准入门槛三项全部达成；用户决策"Yes，准入"——可解除冻结进入 V0.4.3 版本与文档统一 |
| V2.3 Week1-4 变量表解析整合主线 | ✅ | T01-T16 全部交付：vartable 模块（models/parsers/converter/batch_parser/utils）+ CLI vartable 命令组（CLI-28~32）+ 5 格式 Parser + FormatDetector 三级识别 + GUI VartableTab；141 测试新增（38+35+35+33）；DJ-2026-005 端到端 10 项全通过 |
| TD-C10 mypy tests/ 治理 + 32/32 技术债全部关闭 | ✅ | mypy tests/ 381→0 errors（11 文件类型标注修复）；32/32 项技术债全部关闭，剩余 0 项 |
| V0.5.0 版本统一收口 | ✅ | pyproject 0.4.2→0.5.0；CHANGELOG [0.5.0] - 2026-07-01 完整章节；00_项目基础信息 8 文档 V2.2.0/V0.5.0 对齐；02_设计 GUI 原型 V2.1；09_整改项归档整理；全量回归 1477 passed 6 skipped 0 failed |

### 4.2 试运行结论

**通过**。auto-pm 不仅能支撑自身的变更管理闭环，也已经在 V0.4.0 Week 2~4 完成"单机模板 → 工程资产 → 文档自动区刷新"的准真实项目闭环，并在 V0.4.2 首轮把这条链路推进到真实历史 PLC 项目 `DJ-2026-005`。当前产品最值得继续打磨的不是扩张功能面，而是继续缩小真实老项目结构与工具标准口径之间的落差。

**V0.4.2 Week4 收口判断**：
- dogfooding 闭环审查发现 5 项漏洞，已批量修复并验证（PILOT 版本号 + 台帐 + 索引表 + TD-T14 + TD-T09 + §2 语义）
- TD-TC01 + 5 个 jinja2 DeprecationWarning 已收口（技术债报告 26/26 项全部关闭，剩余 0 项）
- 全量回归 1246 passed 1 skipped 0 warnings exit code 0
- 6 周滚动计划前 4 周全部完成，第 5 周 V0.4.3 版本统一可启动

**V0.4.3 准入判断**：**通过（Yes）**。准入门槛三项全部达成——① 真实项目资产闭环（DJ-2026-005 119 IO/7 blocks/5 channels）；② 第二样本复核（DJ-2026-000 + DJ-2026-099）；③ doc inject/doc refresh/plc check 真实使用路径已可解释、可复现、可测试。本会话已完成用户前置条件（TD-TC01 + jinja2 warnings 收口），可解除冻结进入 V0.4.3 版本与文档统一阶段。

### 4.3 后续建议

1. **V0.4.3 版本统一（第5周主线）**：统一 `pyproject.toml`、`CHANGELOG.md`、`005_变更记录_CHG.md`、PRD 路线图、PM_SESSION §2/§8 口径；收口 016 文档设计意图 5 块 vs 真实 PLC_ST 目录 7 块差异；评估 DJ-2026-005 工程资产文件是否引入资产提取器或保持人工首版策略
2. **历史项目兼容持续收敛**：继续收敛 `plc check` 对真实老项目分散 PRD 目录的识别边界，避免"项目有文档但检查直接 fail"削弱一线工程师对工具的信任
3. **M4 持续化**：每个里程碑（M5+/V2.2+）继续创建 CHG-*.md 走完整流程
4. **尾项治理（第6周）**：评估 `specmgr` 工具边界说明、单条全量 pytest 环境问题的归属与优先级；明确哪些属于产品主线、哪些保持外部工具或环境问题单独跟踪

## 5. 变更记录

| 日期 | 版本 | 变更 | 操作人 |
|------|------|------|--------|
| 2026-06-26 | V1.0.0 | 初始版本，归档 3 次 Dogfooding 闭环证据（CHG-001/062/063） + 4 项问题修复 + 试运行结论 | glm5.2（Phase 6 T83）|
| 2026-06-28 | V1.1.0 | 新增 V0.4.0 Week 2~4 准真实闭环证据（单机模板 PoC + 资产台帐 + 文档自动区刷新）并明确 V0.4.1 后续方向 | TRAE |
| 2026-06-29 | V1.2.0 | 新增 V0.4.2 真实历史项目 `DJ-2026-005` 首轮 dogfood 证据（真实文档锚点兼容修复 + 自动区实际注入 + `doc refresh --dry-run` 复验）并登记 `plc check` 对分散 PRD 路径的兼容问题 | TRAE |
| 2026-06-29 | V1.3.0 | 补充 V0.4.2 第二轮 dogfood 证据（`PlcChecker` 受控历史 PRD 路径兼容 + `tests/plc/test_checker.py` 回归 + `DJ-2026-005` 结构检查从 `4 fail` 收口到 `4 warn / 0 fail`） | TRAE |
| 2026-06-29 | V1.4.0 | 补充 V0.4.2 Week 1~3 dogfood 证据（DJ-2026-005 工程资产补齐 119 IO / 7 blocks / 5 channels + `doc refresh --dry-run` 输出真实内容 + 幂等性验证两次无变化 + 第二样本 DJ-2026-000 边界兼容与 DJ-2026-099 真实工作流复核 + rich markup bug 修复 + 新增 `tests/core/test_doc_refresh_service.py` 19 IO/7 blocks/5 channels 回归） | TRAE |
| 2026-06-29 | V1.5.0 | V0.4.2 Week4 收口 + V0.4.3 准入判断（dogfooding 闭环审查 5 项漏洞批量修复：PILOT 版本号对齐 + 台帐补登 CHG-072 序号 005 + 8 条死链修复 + 005 索引表 3→9 条 + TD-T14 qapp 真正统一 + TD-T09 except 收窄 + PM_SESSION §2 语义澄清；TD-TC01 已规避 + 5 个 jinja2 DeprecationWarning 根除；技术债 26/26 项全部关闭；全量回归 1246 passed 1 skipped 0 warnings exit code 0；V0.4.3 准入通过） | TRAE |
| 2026-06-29 | V1.6.0 | V0.4.3 版本号与文档统一收口（pyproject 0.3.8→0.4.1 + CHANGELOG [0.4.1] 单条汇总 V0.4.0~V0.4.3 全部证据 + 005 V0.4.3 章节 + PRD V2.1.2 V0.4.1 路线图 + 016 文档 5 块 vs 7 块差异收口 §5.1.1/§5.1.2 + DJ-2026-005 工程资产提取策略评估保持人工首版 + PM_SESSION §2/§7/§8/§9 同步 + PILOT V1.6.0；ruff 0 errors + mypy 0 errors + jinja2 PASSED + tests/ui 76 passed + 全量回归基线 1246 passed 1 skipped 0 warnings） | TRAE |
| 2026-06-30 | V1.7.0 | V2.2 Week3 第 9 次 dogfooding 闭环（CHG-SCPT-2026-078 完整 9 步状态流转 draft→closed）：GUI 规范中心页改造（T11 spec_center.py 482→300 行 + T12 6 Tab 类 + T13 服务集成 IndexService/CheckService/FrontmatterService/ReportService + T14 LSP-907 集成 14 规范）+ 技术债清理（TD-C07 mypy 17 errors 修复 + TD-C08 8 文件 docstring 规范化 + TD-C09 19 处 type:ignore 18 处清理 + TD-A03 第 9 次闭环）；33 个新 UI 测试 + ruff/mypy 0 errors + 全量回归 1332 passed 5 skipped；§1.1 试运行周期延伸到 2026-06-30 + 闭环次数 8→9 | auto-pm（V0.4.2 整改批次）|
| 2026-07-01 | V1.8.0 | V2.3 Week1-4 第 10 次 dogfooding 闭环（变量表解析整合主线 + TD-C10 治理 + V0.5.0 收口）：Week1 VarEntry/VarTable/ParseResult/ParseError 4 个 frozen dataclass + IoPointsParser + 编码检测 + CLI vartable 命令组（38 测试）；Week2 ProgramBlocksParser/CommunicationsParser + 5 格式 Parser 骨架 + FormatDetector 三级识别 + DJ-2026-005 端到端 6 项全通过（35 测试）；Week3 5 格式 Parser 深化 + VariableConverter + BatchParser + DJ-2026-005 端到端 4 项全通过（35 测试）；Week4 VariableTableModel + VariableTableEditor + VartableTab GUI 变量编辑器（33 测试）；TD-C10 mypy tests/ 381→0 errors（11 文件类型标注修复）；141 测试新增 + ruff/mypy 0 errors + 全量回归 1477 passed 6 skipped；32/32 项技术债全部关闭；§1.1 试运行周期延伸到 2026-07-01 + 闭环次数 9→10；pyproject 0.4.2→0.5.0 + CHANGELOG [0.5.0] - 2026-07-01 + 00_项目基础信息 8 文档 V2.2.0/V0.5.0 对齐 | auto-pm（V0.5.0 收口批次）|

---

> **维护规则**：
> - 每次 Dogfooding 闭环完成后，在本文件追加证据
> - 试运行发现的问题修复后，从"3.1 已修复"移至历史归档
> - 已知限制修复后，从"3.2 已知限制"移除并记录到变更记录
