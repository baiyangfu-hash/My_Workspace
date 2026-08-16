---
version: "V1.2.0"
status: "ACTIVE"
created: "2026-08-16"
updated: "2026-08-16"
project_id: "SW-2026-008"
title: "auto-pm 核心模块版本演进与 Breaking Changes 矩阵 (MATRIX)"
author: "Lead Full-stack Engineer"
---

# auto-pm 核心模块版本演进与 Breaking Changes 矩阵 (MATRIX)

> **所属过程组**：`03_执行 (Executing)`  
> **项目编号**：`SW-2026-008`  
> **单一真源索引**：`PM_SESSION_SW-2026-008.md`

---

## 1. 核心架构组件版本演进矩阵

| 系统主版本 | 关键变更单 (CHG) | `WorkbenchFacade` 外观层 | `QML Bridges` 桥接层 | `StageGateEngine` 门禁引擎 | `PLC SCL Linter` 规范排查器 | 核心架构特征 / 破坏性变更 (Breaking Changes) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **V0.9.0** | CHG-SCPT-101 | V1.0.0 | V1.0.0 | - | - | 基础脚手架生成与 SQLite 扫描缓存落地 |
| **V1.0.0** | CHG-SCPT-140 | V2.0.0 | V2.0.0 | - | - | QML 玻璃拟态深色驾驶舱与三轨道 View 架构建立 |
| **V1.1.0** | CHG-SCPT-152 | V2.1.0 | V2.2.0 | - | - | 跨技能协同公共契约 (`skill_coordination.md`) 确立 |
| **V1.1.1** | CHG-SCPT-156 | V2.2.0 | V2.3.0 (`AiContextV2`) | - | - | `ai_context.json` V2 升级，PM 成为唯一回写 owner |
| **V1.1.2** | CHG-SCPT-157 | V2.3.0 | V2.4.0 (`SpecBridge`) | - | V1.0.0 (`LSP-905`) | 引入 SCL 工艺状态机离线生成器与 LSP-905 规范排查器 |
| **V1.2.0 (当前)** | **CHG-SCPT-158** | **V3.0.0** | **V3.0.0** | **V1.0.0 (`G1~G4`)** | **V1.1.0** | **5 大过程组 Stage-Gate 阶段门禁规则引擎与 DTO 契约构建** |

---

## 2. 各子领域模块成熟度一览

| 子领域包 | 当前版本 | 职责定义 | 单元测试覆盖 |
| :--- | :--- | :--- | :--- |
| `auto_pm.contracts` | V1.0.0 | 强类型 DTO 契约 (`gate_dtos`, `dto.py`) | 94% |
| `auto_pm.core.gates` | V1.0.0 | 5 大过程组 G1~G4 规则评估器与卡点阻断 | 97% |
| `auto_pm.plc` | V1.2.0 | 西门子 S7 SCL 生成、Linter 规范检查、UDT 结构体分析 | 92% |
| `auto_pm.change` | V2.0.0 | 9 步状态流转机、12 章节解析器、台账自动对账 | 95% |
| `auto_pm.vartable` | V1.5.0 | 多厂商变量表（Inovance, CoDeSys, Work3）解析与转换 | 90% |
| `auto_pm.modbus` | V1.1.0 | 异步 Modbus TCP 轮询、环形缓冲数据管道与 Sim 仿真 | 88% |
| `auto_pm.ui.qml` | V2.0.0 | 11 大 QML 视图组件与 5 大 Bridge 桥接通信 | 100% (138 QML tests) |
