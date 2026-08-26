# 接口文档 FB_3001_ExternalInteraction

## 1. 文档基础信息

| 属性 | 值 |
|------|-----|
| **文档标题** | FB_3001_ExternalInteraction 外部设备交互接口定义（DJ005实现名：FB_ExternalDeviceInteraction） |
| **文档版本** | V9.1.0 |
| **关联源码** | 01_外部设备交互/FB_ExternalDeviceInteraction.scl |
| **编制日期** | 2026-04-27 |
| **编制人** | Trae |
| **遵循规范** | LSP-905 |

## 2. 功能概述

外部设备交互功能块。与组框机(4信号)、打胶机(3信号)、机器人(2信号)交互。安全门/急停/故障汇总。报警码300~399。

## 3. VAR_INPUT (27个)

### 3.1 系统控制 (5个)

| 名称 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| i_bEnable | BOOL | FALSE | 系统使能 |
| i_bAutoMode | BOOL | FALSE | 自动模式 |
| i_bManualMode | BOOL | FALSE | 手动模式 |
| i_bReset | BOOL | FALSE | 复位 |
| i_bAnyAlarmActive | BOOL | FALSE | 全局有报警(来自FB_2001) |

### 3.2 组框机交互 (4个)

| 名称 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| i_bFrameMachine_EStop | BOOL | FALSE | 组框机急停 |
| i_bFrameMachine_Fault | BOOL | FALSE | 组框机故障 |
| i_bDoorOpenRequest | BOOL | FALSE | 开门请求 |
| i_bDoorClosedConfirm | BOOL | FALSE | 门关闭确认 |

### 3.3 打胶机交互 (3个)

| 名称 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| i_bGlueMachine_Fault | BOOL | FALSE | 打胶机故障 |
| i_bGlueMachine_MaintenanceMode | BOOL | FALSE | 打胶机维护模式 |
| i_bRobotReady | BOOL | FALSE | 机器人就绪 |

### 3.4 安全条件 (2个)

| 名称 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| i_bSafetyGateClosed | BOOL | FALSE | 安全门关闭 |
| i_bEmergencyStop | BOOL | FALSE | 急停按钮 |

### 3.5 其他 (13个)

| 名称 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| i_bOperatorPresent | BOOL | FALSE | 操作员在场 |
| i_bSystemReady | BOOL | FALSE | 系统就绪 |
| i_bProductionRunning | BOOL | FALSE | 生产运行中 |
| i_iExternalAlarmCode | INT | 0 | 外部报警码 |
| i_bMaterialLow | BOOL | FALSE | 材料不足 |
| i_bMaterialEmpty | BOOL | FALSE | 材料耗尽 |
| i_bTemperatureWarning | BOOL | FALSE | 温度警告 |
| i_bPressureWarning | BOOL | FALSE | 压力警告 |
| i_bCycleComplete | BOOL | FALSE | 循环完成 |
| i_bQualityCheckOK | BOOL | FALSE | 质量检测通过 |
| i_bMaintenanceRequired | BOOL | FALSE | 需要维护 |
| i_rProductionSpeed | REAL | 0.0 | 生产速度 |
| i_iProductionCount | INT | 0 | 生产计数 |

## 4. VAR_OUTPUT (20个)

### 4.1 本机状态输出 (5个)

| 名称 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| o_bFrameMachine_Ready | BOOL | FALSE | 本机就绪, 可接收边框 |
| o_bFrameMachine_Pause | BOOL | FALSE | 向组框机发送暂停命令 |
| o_bFrameMachine_EmergencyStop | BOOL | FALSE | 组框机急停/安全错误时强制本机停止 |
| o_bDoorOpenRequest | BOOL | FALSE | 向组框机请求开门操作 |
| o_bSystemSafetyConditionMet | BOOL | FALSE | 系统安全条件满足 |

### 4.2 报警输出 (3个)

| 名称 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| o_iExternalDeviceAlarmSummary | INT | 0 | 外部设备故障报警代码(300~399范围) |
| o_bExternalDeviceFault | BOOL | FALSE | 外部设备有故障标志 |
| o_bEmergencyStopActive | BOOL | FALSE | 急停激活标志 |

### 4.2 状态指示 (12个)

| 名称 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| o_bSystemEnabled | BOOL | FALSE | 系统已使能 |
| o_bAutoModeActive | BOOL | FALSE | 自动模式激活 |
| o_bManualModeActive | BOOL | FALSE | 手动模式激活 |
| o_bProductionStatus | BOOL | FALSE | 生产状态 |
| o_bSafetyStatus | BOOL | FALSE | 安全状态 |
| o_bCommunicationOK | BOOL | FALSE | 通信正常 |
| o_bWarningActive | BOOL | FALSE | 警告激活 |
| o_bErrorActive | BOOL | FALSE | 错误激活 |
| o_bMaintenanceMode | BOOL | FALSE | 维护模式 |
| o_bIdleState | BOOL | FALSE | 空闲状态 |
| o_bRunningState | BOOL | FALSE | 运行状态 |
| o_bFaultState | BOOL | FALSE | 故障状态 |

## 5. 报警码 (FB_3001内部产生)

| 码 | 含义 |
|:--:|------|
| 301 | 组框机急停 |
| 302 | 组框机故障 |
| 303 | 打胶机故障 |
| 304 | 安全门打开 |
| 305 | 急停按钮按下 |
| 306 | 操作员不在场 |
| 307 | 材料不足 |
| 308 | 材料耗尽 |
| 309 | 温度异常 |
| 310 | 压力异常 |
| 311 | 质量检测失败 |
| 312 | 需要维护 |
| 320 | 通信故障 |

## 6. 关联文档

| 文档 | 路径 | 版本 |
|------|------|:----:|
| DSN | 详细设计说明书_DSN-FB-ExternalDeviceInteraction.md | V4.1.0 |
| CHG | 变更记录_CHG-FB3001-ExternalDeviceInteraction-V4.1.0.md | V4.1.0 |
