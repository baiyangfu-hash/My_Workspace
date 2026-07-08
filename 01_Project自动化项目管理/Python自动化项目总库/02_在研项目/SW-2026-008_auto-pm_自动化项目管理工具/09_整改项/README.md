# 09_整改项 索引

> **项目**: SW-2026-008 auto-pm 自动化项目管理工具
> **维护规则**: 历史整改文件归档到 `archive/` 子目录；当前活跃整改文件保留在根目录
> **最近整理**: 2026-07-08（V0.9.1 实测诊断 + 测试计划 + 归档整理）

## 当前活跃文件（3 个 + README）

| 文件 | 用途 | 状态 |
|------|------|------|
| [diagnostic_report.md](diagnostic_report.md) | 2026-07-08 V0.9.1 实测诊断报告（对 Claude-result 12 项残留问题逐项 Grep/Read/mypy 实证，8 存在 + 4 失真） | ✅ 当前真源 |
| [CLI测试计划.md](CLI测试计划.md) | V0.9.1 CLI 测试计划（10 子命令组矩阵 + 153 用例 + 执行命令） | ✅ 当前真源 |
| [GUI测试计划.md](GUI测试计划.md) | V0.9.1 GUI 测试计划（8 QML 页面矩阵 + 6 状态覆盖 + 可见模式约束 + 89 用例） | ✅ 当前真源 |
| [README.md](README.md) | 09_整改项索引（本文件） | ✅ 当前真源 |

## 归档文件（archive/）

### 2026-07-08 归档（6 个）

| 文件 | 原活跃期 | 归档原因 |
|------|----------|----------|
| [archive/Claude-result_V0.9.1_原始报告.md](archive/Claude-result_V0.9.1_原始报告.md) | 2026-07-08 | 被 diagnostic_report.md（实测版）替代 |
| [archive/remediation_plan.md](archive/remediation_plan.md) | 2026-07-07 | 7 项 P0 阻断性问题修复方案，状态=已完成 |
| [archive/landing_plans/M2_workbench_landing_plan.md](archive/landing_plans/M2_workbench_landing_plan.md) | M2 | M2 里程碑已完成（WorkbenchFacade + WorkbenchBridge 落地） |
| [archive/landing_plans/M3_change_landing_plan.md](archive/landing_plans/M3_change_landing_plan.md) | M3 | M3 里程碑已完成（ChangeFacade + ChangeBridge 落地） |
| [archive/landing_plans/M4_delivery_system_landing_plan.md](archive/landing_plans/M4_delivery_system_landing_plan.md) | M4 | M4 里程碑已完成（DeliveryFacade 落地） |
| [archive/landing_plans/M4_spec_landing_plan.md](archive/landing_plans/M4_spec_landing_plan.md) | M4 | M4 里程碑已完成（SpecFacade 落地） |

### 2026-07-07 重新诊断时归档（5 个）

| 文件 | 原活跃期 | 归档原因 |
|------|----------|----------|
| [archive/diagnostic_report_2026-07-06_V0.9.0.md](archive/diagnostic_report_2026-07-06_V0.9.0.md) | 2026-07-06 | 被 2026-07-07 重新诊断报告替代（旧报告声明 ruff/mypy 0 errors 与实测不符） |
| [archive/2026-06-30_项目全量审查报告.md](archive/2026-06-30_项目全量审查报告.md) | V0.4.1 | 审查的是 V2.1 设计文档（已迁移到 02_设计/），9 Critical/20 Major 问题大多已修复 |
| [archive/GUI-UI对比度问题清单.md](archive/GUI-UI对比度问题清单.md) | V0.5.x | 基于 QWidget 截图，引用 `scripts/gui_plc_full_test.py`（V0.9.0 已删除） |
| [archive/GUI测试整改报告.md](archive/GUI测试整改报告.md) | V0.5.0 | 自标 "已过时"，引用 `02_设计/GUI测试计划-V0.5.0.md`（不存在）等已删除文件 |
| [archive/V0.4.2-glm执行输入清单.md](archive/V0.4.2-glm执行输入清单.md) | V0.4.2 | 引用 `00_项目基础信息/005_变更记录_CHG.md`（已归档不存在），主线已到 V0.9.0 |

### V0.5.0 收口时归档（7 个，2026-07-01）

| 文件 | 原活跃期 | 归档原因 |
|------|----------|----------|
| [archive/GUI-V2.0-测试执行报告.md](archive/GUI-V2.0-测试执行报告.md) | V2.0 GUI 测试 | V2.0 GUI 已被 V2.2/V2.3 GUI 改造取代 |
| [archive/V0.2.1-电气工程师评估整改清单.md](archive/V0.2.1-电气工程师评估整改清单.md) | V0.2.1 | 评估项已在 V0.3.0+ 全部落地 |
| [archive/V0.3.0-项目深度诊断与Dogfood专项报告.md](archive/V0.3.0-项目深度诊断与Dogfood专项报告.md) | V0.3.0 | Dogfood 已 25 次闭环，诊断结论已沉淀 |
| [archive/V0.3.0-项目落地执行总计划_重规划版.md](archive/V0.3.0-项目落地执行总计划_重规划版.md) | V0.3.0 | 计划已被 V0.5.0+ 长期路线图取代 |
| [archive/V0.3.6-glm5.1执行输入清单.md](archive/V0.3.6-glm5.1执行输入清单.md) | V0.3.6 | 执行清单已全部完成 |
| [archive/V0.4.0-Codex_GPT产品与工程建议.md](archive/V0.4.0-Codex_GPT产品与工程建议.md) | V0.4.0 | 建议已在 V0.4.0~V0.5.0 评估落地 |
| [archive/V0.4.0-glm5.2执行输入清单.md](archive/V0.4.0-glm5.2执行输入清单.md) | V0.4.0 | 执行清单已全部完成 |

### V0.4.2 收口时归档（2 个，2026-06-29）

| 文件 | 原活跃期 | 归档原因 |
|------|----------|----------|
| [archive/V2.0-GUI-验证整改清单.md](archive/V2.0-GUI-验证整改清单.md) | V2.0 | V2.0 GUI 验证已完成 |
| [archive/V2.0-测试执行检查清单.md](archive/V2.0-测试执行检查清单.md) | V2.0 | V2.0 测试执行已完成 |

### V0.4.0 收口时归档（1 个，2026-06-28）

| 文件 | 原活跃期 | 归档原因 |
|------|----------|----------|
| [archive/V2.0-全功能自动化测试计划.md](archive/V2.0-全功能自动化测试计划.md) | V2.0 | V2.0 全功能测试计划已执行完毕 |

### 迭代测试报告（archive/iterations/，4 个）

| 文件 | 用途 |
|------|------|
| [archive/iterations/迭代1-测试报告.md](archive/iterations/迭代1-测试报告.md) | M1 迭代 1 测试报告 |
| [archive/iterations/迭代2-测试报告.md](archive/iterations/迭代2-测试报告.md) | M1 迭代 2 测试报告 |
| [archive/iterations/迭代3-测试报告.md](archive/iterations/迭代3-测试报告.md) | M1 迭代 3 测试报告 |
| [archive/iterations/迭代4-测试报告.md](archive/iterations/迭代4-测试报告.md) | M1 迭代 4 测试报告 |

## 整理规则

1. **归档时机**：每个版本收口时（如 V0.5.0/V0.6.0/V0.9.0），将已完成的历史整改文件移动到 `archive/`
2. **保留原则**：当前活跃的诊断报告和执行清单保留在根目录，便于快速访问
3. **索引维护**：每次归档操作后更新本 README 索引
4. **历史追溯**：归档文件不删除，保留完整历史链路
5. **命名规范**：归档文件保留原名，不追加版本号后缀（例外：`diagnostic_report_2026-07-06_V0.9.0.md` 因同名文件需区分，添加日期前缀；`Claude-result_V0.9.1_原始报告.md` 同理添加版本前缀）

## 2026-07-08 整理关键发现摘要

**V0.9.1 实测诊断**：对 Claude-result V3 诊断报告的 12 项残留问题逐项用 Grep/Read/mypy 实证复核，结论为 **8 项存在 + 4 项失真**。最严重失真项为 mypy 实测仅 5 errors（非报告声称的 24 errors）。详见 [diagnostic_report.md](diagnostic_report.md)。

**CLI/GUI 测试计划建立**：
- CLI 测试计划：10 子命令组矩阵 + 153 用例 + 执行命令（详见 [CLI测试计划.md](CLI测试计划.md)）
- GUI 测试计划：8 QML 页面矩阵 + 6 状态覆盖 + 可见模式约束 + 89 用例（详见 [GUI测试计划.md](GUI测试计划.md)）

**设计文档同步**：`02_设计/` 下 5 份设计文档已更新至 V3.1.0 已实现状态，与代码现状对齐。

**本次归档动作**：将已被替代的 Claude-result V3 报告、已完成的 remediation_plan（7 项 P0 修复方案）、4 份 M2/M3/M4 Landing Plan（里程碑已完成）共 6 个文件归档到 `archive/`，其中 Landing Plan 统一归入 `archive/landing_plans/` 子目录。
