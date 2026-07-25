# 接口文档 FB_3001_ExternalDeviceInteraction

## 0. 文档基础信息

| 属性 | 值 |
|------|-----|
| **文档标题** | FB_3001 外部设备交互接口定义 |
| **文档版本** | V6.0.0 |
| **关联源码** | external/FB_ExternalDeviceInteraction.scl |
| **编制日期** | 2026-05-17 |
| **编制人** | Trae |
| **遵循规范** | 801_DEV-V1.0.5, 810_DEV-V1.0.2 |
| **数据来源** | 源程序功能基线_SRC-DJ-2026-005-V1.0.0 |

## 1. 功能概述

管理所有与外部设备/安全相关的信号：
- 组框机交互（原CC-Link R5000~R5011，通用化后BOOL）
- 打胶机硬接线信号（X76/X102/Y44/Y47 已在FB_1004中处理）
- 机器人交互
- **8路安全门检测** (X140~X147，新增)
- **急停检测** (X101，新增)
- **HMI STOP** (X77，新增)
- **总线/外设健康位占位**（取消CC-Link后可替换）
- **复位按钮** (X100)

## 2. VAR_INPUT

### 2.1 组框机（原CC-Link）
| 名称 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| i_bFrameMachineAutoRunning | BOOL | FALSE | 组框机自动运行中 |
| i_bFrameMachineStackingDone | BOOL | FALSE | 组框机码料完成 |
| i_bFrameMachineFault | BOOL | FALSE | 组框机故障 |
| i_bFrameMachineEStop | BOOL | FALSE | 组框机急停 |

### 2.2 机器人
| 名称 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| i_bRobotAutoRunning | BOOL | FALSE | 机器人自动中 |
| i_bRobotPickupDone | BOOL | FALSE | 机器人码料完成 |
| i_bRobotFault | BOOL | FALSE | 机器人故障 |
| i_bRobotEStop | BOOL | FALSE | 机器人急停 |

### 2.3 安全/复位
| 名称 | 类型 | 默认值 | 说明 | 来源地址 |
|------|------|--------|------|----------|
| i_bEStop | BOOL | FALSE | 急停按钮(常闭,OFF=按下) | X101 |
| i_bSafetyDoor[1..8] | BOOL[1..8] | TRUE | 8路安全门(常闭,OFF=开) | X140~X147 |
| i_bHmiStop | BOOL | FALSE | HMI STOP按钮 | X77 |
| i_bResetButton | BOOL | FALSE | 物理复位按钮 | X100 |
| i_bBusHealthy | BOOL | TRUE | 总线/外设健康位占位 | 平台适配 |

## 3. VAR_OUTPUT

### 3.1 组框机
| 名称 | 类型 | 默认值 | 说明 | 去向地址 |
|------|------|--------|------|----------|
| q_bPauseFrameMachine | BOOL | FALSE | 暂停组框机 | Y45 |
| q_bEStopFrameMachine | BOOL | FALSE | 组框机急停 | Y46 |

### 3.2 机器人
| 名称 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| q_bAllowRobotStacking | BOOL | FALSE | 允许机器人码料 |
| q_bStopRobotStacking | BOOL | FALSE | 停止机器人码料 |

### 3.3 安全状态输出（到OB1/FB_2001）
| 名称 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| q_bEStopActive | BOOL | FALSE | 急停激活(→FB_2001) |
| q_bSafetyDoorFault[1..8] | BOOL[1..8] | FALSE | 各安全门异常(→FB_2001) |
| q_bHmiStopActive | BOOL | FALSE | HMI停止有效(→FB_2001) |
| q_bAnyDoorOpen | BOOL | FALSE | 任意安全门开(→互锁M200) |
| q_bBusUnhealthy | BOOL | FALSE | 总线不健康(→FB_2001) |
| q_bResetActive | BOOL | FALSE | 复位有效(→OB1联动) |

## 4. 关联文档

| 文档 | 路径 |
|------|------|
| CHG | 变更记录_CHG-FB3001-ExternalDeviceInteraction-V6.0.0.md |
| UM | 使用说明_UM-FB3001-ExternalDeviceInteraction-V6.0.0.md |
