---
id: STD-909
name: PLC上位机与人机交互规范
version: 1.0.0
domain: PLC自动化域
type: STD
status: active
author: Antigravity
created_at: 2026-08-17
updated_at: 2026-08-17
description: 规范 PLC 工程中下位机触摸屏 HMI 与 PC 端上位机/中控系统的交互原型选型标准、通信分工与协同规程。
---

# 909 PLC 上位机与人机交互规范 (STD-909)

## 1. 概述

在自动化工程中，人机交互（HMI/SCADA/上位机）是设备操作与中控管理的核心入口。为确保交互体验统一、开发高效且与 PLC 程序严格对齐，本规范制定了 PLC 工程中的人机交互选型标准与开发分工。

---

## 2. 交互系统选型与分工矩阵

| 交互层级 | 典型载体 | 适用规范与脚手架 | 核心定位与职责 |
| :--- | :--- | :--- | :--- |
| **下位机现场 HMI (触摸屏)** | 10~15寸 工业触摸屏<br>(如西门子 Smart/Comfort 屏、威纶通) | **[STD-910 HMI 原型规范](../04_驾驶舱与全栈域/910_HMI_HTML原型脚手架与点表规范_STD.md)**<br>`template: industrial-hmi` | • 单机动作手动/自动控制<br>• 工步状态机 (`S0~S23`) 现场走查<br>• 现场报警与 IO 点位直接监控 |
| **PC 端上位机 / 中控驾驶舱** | 工程师工控机 / 产线中控大屏<br>(Python PySide6 / Web SCADA) | **[STD-911 桌面驾驶舱规范](../04_驾驶舱与全栈域/911_Python桌面驾驶舱_HTML原型脚手架规范_STD.md)**<br>`template: python-cockpit` | • 产线级数据采集与趋势图表<br>• Modbus/TCP / S7 通信调试台<br>• 配方数据库管理与质量追溯<br>• 多机协同状态看板 |

---

## 3. 点位与通信契约规范

### 3.1 现场触摸屏 HMI (STD-910 契约)
- 必须维护 `03_HMI设计/hmi_tag_mapping.json`；
- PLC 程序中的 `DB_HMI`（如 `DB_HMI.ActualPos_X1`）变量命名与数据类型必须与 HTML 原型 100% 对应；
- 原型采用 1280×800 分辨率，归档于 `03_HMI设计/原型/files/`。

### 3.2 PC 端上位机驾驶舱 (STD-911 契约)
- 必须维护 `app_bridge_mapping.json`；
- 上位机 Python 业务服务（如 `ModbusService`、`PlcChecker`）通过 Bridge 槽函数提供通信接口；
- 原型采用流式弹性全屏布局，归档于 `02_规划/Html原型预览/`。

### 3.3 外部设备握手通用拓扑契约 (Upstream / Downstream)
- **拓扑语义标准**：通用流水线单机设备统一抽象为 **`上游设备交互 (Upstream Handshake)`** 与 **`下游设备交互 (Downstream Handshake)`**；
- **标准 4 步握手时序**：`请求 (Req)` $\rightarrow$ `允许 (Allow)` $\rightarrow$ `执行中 (Busy)` $\rightarrow$ `完成应答 (DoneAck)`；
- **自适应规则**：
  - 首端单机（如上料机）：仅配置下游主工艺交互；
  - 中间单机（如缓存机）：配置上游来料与下游送出双通道；
  - 末端单机（如码垛机）：仅配置上游进料交互，下游标记为人工/叉车接驳，严禁捏造下游假设备。


---

## 4. 脚手架快速释放指引

```powershell
# 1. 为单机项目初始化现场触摸屏 HMI 原型
python -m auto_pm prototype init --pid <项目ID> --template industrial-hmi

# 2. 为含有上位机/中控的项目初始化 Python 驾驶舱原型
python -m auto_pm prototype init --pid <项目ID> --template python-cockpit
```
