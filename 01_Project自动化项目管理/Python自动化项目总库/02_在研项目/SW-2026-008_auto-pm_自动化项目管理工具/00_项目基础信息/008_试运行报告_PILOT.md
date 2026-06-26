---
doc_id: PILOT-008
title: 试运行报告
version: "V1.0.0"
status: "生效"
created: "2026-06-26"
updated: "2026-06-26"
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

## 3. 试运行发现的问题与修复

### 3.1 已修复（4 项）

| 问题 | 严重程度 | 发现于 | 修复于 | 修复方式 |
|------|----------|--------|--------|----------|
| BUG-001 verification_conclusion 门禁过硬编码 | 🟡 中 | CHG-001 闭环 | M0.5 Phase 1 | 改为规则校验（包含"通过"且不包含"不通过"等即放行） |
| BUG-002 台帐路径解析错误（中文路径字符级拆分） | 🟡 中 | CHG-001 闭环 | M0.5 Phase 1 | 修复路径解析逻辑 |
| 台帐重复追加 bug（LedgerUpdater 无去重） | 🟡 中 | CHG-063 闭环后 glm5.2 收口 | 2026-06-26 glm5.2 | update() 添加去重检查 + generate_change_number 添加台帐序号检查 |
| CHG-SCPT-2026-001 内容空白（§5/§6/§7/§8 全部待填写） | 🟡 中 | CHG-062 闭环前 | M3.5-4 | 补全 12 章节真实内容 + 文档版本 V1.0.0→V2.1.0 |

### 3.2 已知限制（不视为缺陷）

| 限制 | 说明 | 应对 |
|------|------|------|
| `change transition` 不自动追加 §8.1 审批表行 | 需手动编辑 Markdown 补审批记录 | 后续版本可增强 |
| `--verification-conclusion` 在非 completed 流转时日志默认值 | 非阻断，仅日志噪音 | 后续版本可优化 |
| DB 路径未迁移 urgency 字段 schema | urgency 筛选仅在文件扫描模式完整可用 | V2.2 规范中心整合时迁移 |
| 全量测试耗时 320s（无 coverage） | GUI 测试 Qt 环境初始化开销 | TD-T08 pytest-xdist 并行化待偿还 |

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

### 4.2 试运行结论

**通过**。auto-pm 的变更管理能力能够支撑真实项目迭代，3 次 Dogfooding 闭环全部成功，发现的产品缺陷已全部修复。M4 Dogfooding 持续化机制已建立（spec.md §9.1 固定模板 10 步），每个里程碑必经 CHG-*.md 流程。

### 4.3 后续建议

1. **M4 持续化**：每个里程碑（M5+/V2.2+）必须创建 CHG-*.md 走完整流程
2. **台帐健康检查**：定期用 `change list` 核对台帐记录数，防止再次出现脏数据
3. **TD-T08 偿还**：引入 pytest-xdist 并行化，解决全量测试 320s 耗时问题
4. **urgency 字段 DB 迁移**：V2.2 规范中心整合时，将 urgency 字段加入 change_requests 表 schema

## 5. 变更记录

| 日期 | 版本 | 变更 | 操作人 |
|------|------|------|--------|
| 2026-06-26 | V1.0.0 | 初始版本，归档 3 次 Dogfooding 闭环证据（CHG-001/062/063） + 4 项问题修复 + 试运行结论 | glm5.2（Phase 6 T83）|

---

> **维护规则**：
> - 每次 Dogfooding 闭环完成后，在本文件追加证据
> - 试运行发现的问题修复后，从"3.1 已修复"移至历史归档
> - 已知限制修复后，从"3.2 已知限制"移除并记录到变更记录
