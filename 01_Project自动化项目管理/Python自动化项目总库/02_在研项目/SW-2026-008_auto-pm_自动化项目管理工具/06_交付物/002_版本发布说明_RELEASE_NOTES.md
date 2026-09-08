---
version: "V1.2.4"
status: "正式发布"
created: "2026-09-07"
updated: "2026-09-07"
spec_id: "RELEASE_NOTES"
project_id: "SW-2026-008"
---

# auto-pm 自动化项目管理工具 - 版本发布说明 (RELEASE_NOTES)

> **当前版本**：`V1.2.4-6699a5b`  
> **发布日期**：`2026-09-07`  
> **适用平台**：Windows 10/11 x64 (免安装稳定运行槽 / Python 3.11+)  
> **稳定运行槽位**：`00_Infrastructure/auto_pm/releases/1.2.4-6699a5b` (active)

---

## 1. 版本概述

`auto-pm` V1.2.4 是项目架构演进与稳定生产的重要里程碑版本。本版本完成了稳定部署双槽架构落地与原子切流（`1.2.4-6699a5b` active），闭环了全生命周期工作流编排内核 Cockpit OS（Phase 0~3）、全链台账「台帐→台账」规范化对账，以及 SRE 零崩溃质量门禁硬核加固，实现项目管理工具的高可靠无感运行。

---

## 2. 核心特性与架构演进

- **双槽稳定部署与不可变制品 (CHG-SCPT-2026-184 / CHG-SCPT-2026-187)**：
  - 落地 `00_Infrastructure/auto_pm` 稳定运行容器，引入双槽指针原子切流（active/previous）与 465 文件 manifest 完整性硬校验；
  - 消除 editable 依赖，启动脚本注入 `PYTHONDONTWRITEBYTECODE=1`，彻底杜绝 `__pycache__` 漂移污染。
- **全链台账规范化与对账引擎闭环 (CHG-SCPT-2026-187)**：
  - 彻底清理工作区错别字，完成活体项目、规范索引与模板库「台帐→台账」全链改名；
  - 生产对账实现 0 缺失、0 孤儿、0 状态差异，台账自动入账。
- **Cockpit OS 工作流编排与事务沙箱 (CHG-SCPT-2026-171~177)**：
  - 落地 `WorkflowOrchestrator`（方案规划与流水线执行）、`ChangeTransactionManager`（快照隔离与原子回滚）、`ProjectArchiveService`（可逆归档恢复）与 PM Saga WAL 事务日志引擎。
- **CLI 命令矩阵与活文档自动化自省 (CHG-SCPT-2026-186)**：
  - 全面支持 22 个 CLI 业务命令组，下沉 `doc check --strict` 与 `doc sync`，实现代码 AST 元数据无损反向注回活文档；
  - 修复 `plc check` 退出码缺陷（FAIL 坚决返回 Exit 1，杜绝假绿）。

---

## 3. 发布放行签署

- **自动化测试回归**：全量单测与回归用例 **1928+ passed / 100% 绿灯** ✅
- **Doc-as-Code 文档门禁**：`auto-pm doc check --strict` **DOC-001~DOC-004 ALL PASS** ✅
- **台账一致性对账**：`auto-pm ledger reconcile SW-2026-008` **0 差异 ALL PASS** ✅
- **SRE 运行时校验**：launcher resolve-only 与 `--help` **Exit 0 通过** ✅
