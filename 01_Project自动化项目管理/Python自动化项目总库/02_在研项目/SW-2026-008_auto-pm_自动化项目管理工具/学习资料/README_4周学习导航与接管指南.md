---
version: "V2.0.0"
status: "正式发布"
created: "2026-09-07"
updated: "2026-09-07"
spec_id: "GUIDE_4W"
project_id: "SW-2026-008"
title: "auto-pm 工业驾驶舱接管与实战【4周电气工程师实战手册 V2.0.0】"
---

# auto-pm 工业驾驶舱接管与实战【4周电气工程师实战手册 V2.0.0】

> 🎯 **手册定位**：专为**兼任项目管理的电气自动化工程师**量身定制。以工控人最直观的“PLC/HMI/继电器/点表/出厂固件”物理心智模型为桥梁，用 4 周时间（每天 45~60 分钟）帮助你全面接管基于 **Release 1.2.4-6699a5b 稳定部署双槽架构**与 **Cockpit OS 编排内核** 的全新 `auto-pm` 桌面驾驶舱。
> 
> 💡 **核心主旨**：告别盲目改代码，掌握双槽防篡改机制、事务沙箱原子回滚、多 Agent 契约协同与 40 组 CLI 极客实战，实现从“传统电气工程师”向“一人全栈超级个体”的工程跨越。

---

## 🗺️ 4 周接管阶梯路线图 (V2.0.0)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 📅 第 1 周：【工业安全防线与双槽部署】（会用、懂部署、绝不改崩）            │
│    • Day 01：Git 救命防线与工控概念类比（工作区 vs 内存镜像，Commit vs 固件快照）│
│    • Day 02：Release 双槽稳定部署与不可变制品（双槽指针、manifest 防篡改校验）  │
│    • Day 03：GUI 深色驾驶舱与 Headless 双模启动（PySide6 磨砂桌面与探针启动）   │
│    • Day 04：项目全生命周期与 Copier 标准立项（auto-pm project 家族与 PM_SESSION）│
│    • Day 05：PLC 53 项硬门禁与 SCL 语法体检（auto-pm plc check、STD 状态机检查）│
├─────────────────────────────────────────────────────────────────────────────┤
│ 📅 第 2 周：【Cockpit OS 编排内核与整洁架构】（看懂内核、事务保障、可逆归档）│
│    • Day 06：Clean Architecture 5 层架构与工控解耦（Domain/Application/Contracts）│
│    • Day 07：Workflow 方案规划与结构化决策包（WorkflowOrchestrator.plan 与 DEC）│
│    • Day 08：ChangeTransaction 事务沙箱与原子回滚（快照隔离、自动回滚与防雪崩） │
│    • Day 09：ProjectArchive 全生命周期归档与恢复（三道硬门禁与 ARC 流水号还原） │
│    • Day 10：PM Saga 事务日志 WAL 与故障恢复（PmClosureSagaCoordinator 检查点） │
├─────────────────────────────────────────────────────────────────────────────┤
│ 📅 第 3 周：【多 Agent 协同与工控 OT-IT 闭环】（指挥 AI、点表转译、通信桥接）│
│    • Day 11：Handoff 契约化移交总线与物理隔离（skill_context 与 handoff_result）│
│    • Day 12：阶段 0 预研探路模式 Grooming 实战（只读代码勘测与零代码盲问红线） │
│    • Day 13：阶段 2 执行交付模式 Execution 填空（物理 TODO 陷阱与机器无情判卷）│
│    • Day 14：OT-IT 变量表异构转译与 3 安全列规范（AutoShop/CodeSys 嗅探与映射） │
│    • Day 15：Modbus TCP 与 OPC UA 工业通信桥接（modbus_bridge 与 DTO 序列化）   │
├─────────────────────────────────────────────────────────────────────────────┤
│ 📅 第 4 周：【40 组 CLI 极客实战与 SRE 零负担交付】（全指令实战、无感切流） │
│    • Day 16：工业变更单 12 态全流程与台账对账（auto-pm change 与 ledger 对账） │
│    • Day 17：Doc-as-Code 活文档自省与严格门禁（doc sync 自动重注与 doc check） │
│    • Day 18：双槽无感切流与日常运维 CheckList（原子指针翻转与系统接管清单）    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ 学习与实操前置环境

在动手操作任何教程中的命令前，请确保在终端（PowerShell）中完成运行环境装配：

```powershell
# 1. 打开 PowerShell 并进入工作空间根目录
cd c:\Users\fubai\Documents\My_Workspace

# 2. 注入全局 Python 路径（指向生产稳定发布位容器）
$env:PYTHONPATH = "00_Infrastructure/auto_pm"

# 3. 验证稳定发布位与活动指针
python -m auto_pm --version
# 正确回显应包含：1.2.4-6699a5b
```

---

## 🛠️ 每日四段式标准学习法

1. **💡 一、工控视角看核心技术**：用你最熟悉的 PLC 梯形图、FB 封装、伺服通讯或 HMI 组态逻辑做类比（5 分钟）；
2. **⚙️ 二、系统机制与底层原理**：透视当前系统的具体工作流，看清数据与代码在底层是如何流转的（10 分钟）；
3. **🧪 三、5~10 分钟动手实操实验**：提供保姆级的可复制命令行或微调操作，验证真实控制台输出（15~20 分钟）；
4. **🛡️ 四、改崩恢复法与今日自测打卡**：万一改崩了怎么 1 秒恢复出厂？并回答 3 道核心思考题固化知识（5 分钟）。

---

## 📚 章节快速导航

- **第 1 周：工业安全防线与双槽部署**
  - [Day 01：Git 救命防线与工控概念类比](./第1周_工业安全防线与双槽部署/Day01_Git救命防线与工控概念类比.md)
  - [Day 02：Release 双槽稳定部署与不可变制品](./第1周_工业安全防线与双槽部署/Day02_Release双槽稳定部署与不可变制品.md)
  - [Day 03：GUI 深色驾驶舱与 Headless 双模启动](./第1周_工业安全防线与双槽部署/Day03_GUI深色驾驶舱与Headless双模启动.md)
  - [Day 04：项目全生命周期与 Copier 标准立项](./第1周_工业安全防线与双槽部署/Day04_项目全生命周期与Copier标准立项.md)
  - [Day 05：PLC 53 项硬门禁与 SCL 语法体检](./第1周_工业安全防线与双槽部署/Day05_PLC53项硬门禁与SCL语法体检.md)
- **第 2 周：Cockpit OS 编排内核与整洁架构**
  - [Day 06：Clean Architecture 5 层架构与工控解耦](./第2周_CockpitOS编排内核与整洁架构/Day06_CleanArchitecture5层架构与工控解耦.md)
  - [Day 07：Workflow 方案规划与结构化决策包](./第2周_CockpitOS编排内核与整洁架构/Day07_Workflow方案规划与结构化决策包.md)
  - [Day 08：ChangeTransaction 事务沙箱与原子回滚](./第2周_CockpitOS编排内核与整洁架构/Day08_ChangeTransaction事务沙箱与原子回滚.md)
  - [Day 09：ProjectArchive 全生命周期归档与恢复](./第2周_CockpitOS编排内核与整洁架构/Day09_ProjectArchive全生命周期归档与恢复.md)
  - [Day 10：PM Saga 事务日志 WAL 与故障恢复](./第2周_CockpitOS编排内核与整洁架构/Day10_PMSaga事务日志WAL与故障恢复.md)
- **第 3 周：多 Agent 协同与工控 OT-IT 闭环**
  - [Day 11：Handoff 契约化移交总线与物理隔离](./第3周_多Agent协同与工控OTIT闭环/Day11_Handoff契约化移交总线与物理隔离.md)
  - [Day 12：阶段 0 预研探路模式 Grooming 实战](./第3周_多Agent协同与工控OTIT闭环/Day12_阶段0预研探路模式Grooming实战.md)
  - [Day 13：阶段 2 执行交付模式 Execution 填空](./第3周_多Agent协同与工控OTIT闭环/Day13_阶段2执行交付模式Execution填空.md)
  - [Day 14：OT-IT 变量表异构转译与 3 安全列规范](./第3周_多Agent协同与工控OTIT闭环/Day14_OTIT变量表异构转译与3安全列规范.md)
  - [Day 15：Modbus TCP 与 OPC UA 工业通信桥接](./第3周_多Agent协同与工控OTIT闭环/Day15_ModbusTCP与OPCUA工业通信桥接诊断.md)
- **第 4 周：40 组 CLI 极客实战与 SRE 零负担交付**
  - [Day 16：工业变更单 12 态全流程与台账对账](./第4周_40组CLI极客实战与SRE零负担交付/Day16_工业变更单12态全流程与台账对账.md)
  - [Day 17：Doc-as-Code 活文档自省与严格门禁](./第4周_40组CLI极客实战与SRE零负担交付/Day17_DocAsCode活文档自省与严格门禁.md)
  - [Day 18：双槽无感切流与日常运维 CheckList](./第4周_40组CLI极客实战与SRE零负担交付/Day18_双槽无感切流与日常运维CheckList.md)
