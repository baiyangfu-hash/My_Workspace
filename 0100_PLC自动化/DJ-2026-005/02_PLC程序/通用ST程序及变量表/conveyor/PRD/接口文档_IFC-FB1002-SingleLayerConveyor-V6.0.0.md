# 接口文档 FB_1002_SingleLayerConveyor_BufferFraming

## 0. 文档基础信息

| 属性 | 值 |
|------|-----|
| **文档标题** | FB_1002 单层输送机接口定义 |
| **文档版本** | V6.0.0 |
| **关联源码** | conveyor/FB_1002_SingleLayerConveyor_BufferFraming.scl |
| **编制日期** | 2026-05-17 |
| **编制人** | Trae |
| **审核人** | 人工 |
| **遵循规范** | 801_PLC变量命名与功能块命名规范_DEV-V1.0.5, 810_PLC编程规范_DEV-V1.0.2 |
| **数据来源** | 源程序功能基线_SRC-DJ-2026-005-V1.0.0 |

## 1. 功能概述

单层输送机控制功能块，实现边框缓存机单层物料输送的完整工艺流程。每层独立运行9步 Step_S 状态机（先输送再分料），含传感器双通道冗余一致性检查和分料超时报警。

> **架构说明**：FB_1002 被 FB_1001 容器块实例化4次（L1~L4），不直接由 OB1 调用。

## 2. 状态机步序常量

| 常量名 | 值 | 步骤名 | 说明 |
|--------|-----|--------|------|
| STEP_INIT | 0 | 初始化 | 输送反转复位到初始位 |
| STEP_WAIT_MATERIAL | 1 | 等待来料 | 等待分料前感应器ON |
| STEP_BLOCK_DOWN | 2 | 阻挡下降 | 阻挡气缸下降 |
| STEP_CONVEYOR_FWD | 10 | 输送正转 | 输送带正向运转 |
| STEP_POSITION_CHECK_BLOCK_UP | 20 | 到位检测与阻挡上升 | 双传感器检测+阻挡释放 |
| STEP_SEPARATE_PUSH | 30 | 分料推出 | 分料气缸推出分离边框 |
| STEP_CONVEYOR_SLOW | 50 | 慢速送出 | 慢速精确送出到取料位 |
| STEP_REQUEST_PICKUP | 60 | 请求取料 | 等待取放料取走 |
| STEP_SEPARATE_RETURN | 70 | 分料复位 | 分料气缸复位 |

## 3. 接口定义

### 3.1 VAR_INPUT

| 名称 | 类型 | 默认值 | 有效值域 | 说明 | 来源 |
|------|------|--------|----------|------|------|
| i_bAutoMode | BOOL | FALSE | TRUE/FALSE | 自动运行模式 | OB1→HMI |
| i_bManualMode | BOOL | FALSE | TRUE/FALSE | 手动调试模式 | OB1→HMI |
| i_bStart | BOOL | FALSE | TRUE/FALSE | 启动信号 | OB1→HMI(M2) |
| i_bStop | BOOL | FALSE | TRUE/FALSE | 停止信号 | OB1→HMI(M3) |
| i_bLx_BlockDown | BOOL | FALSE | TRUE/FALSE | 手动:阻挡下降 | OB1←HMI(Mx) |
| i_bLx_SeparatePush | BOOL | FALSE | TRUE/FALSE | 手动:分料推出 | OB1←HMI(Mx) |
| i_bLx_ConveyorFwd | BOOL | FALSE | TRUE/FALSE | 手动:输送正转 | OB1←HMI(Mx) |
| i_bLx_ConveyorRev | BOOL | FALSE | TRUE/FALSE | 手动:输送反转 | OB1←HMI(Mx) |
| i_bLx_ConveyorSlow | BOOL | FALSE | TRUE/FALSE | 手动:输送慢速 | OB1←HMI(Mx) |
| i_bLx_BlockUp | BOOL | FALSE | TRUE/FALSE | 手动:阻挡上升 | OB1←HMI(Mx) |
| i_rConveyorSpeed | REAL | 100.0 | 0.0~300.0 | 输送自动速度(mm/s) | OB1→HMI(D100) |
| i_iSeparateTime | INT | 0 | 0~60000 | 分料动作超时时间(ms) | OB1→HMI(D101) |
| i_iBlockWaitTime | INT | 0 | 0~60000 | 阻挡等待时间(ms) | OB1→HMI(D108) |
| i_bSafetyDoorOk | BOOL | TRUE | TRUE/FALSE | 安全门状态(取反:M8) | OB1→External |
| i_bPickPlaceSafeZone | BOOL | TRUE | TRUE/FALSE | 取料机构在安全区(M515) | OB1→PickPlace |
| i_iLayerIndex | INT | 0 | 1~4 | 当前层编号(用于数组索引) | OB1 |
| i_bPreSeparateSensor | BOOL | FALSE | TRUE/FALSE | 分料前接近开关 | OB1→IO(X21/31/41/51) |
| i_bPositionSensor1 | BOOL | FALSE | TRUE/FALSE | 到位传感器1 | OB1→IO(X22/32/42/52) |
| i_bPositionSensor2 | BOOL | FALSE | TRUE/FALSE | 到位传感器2(冗余) | OB1→IO(X23/33/43/53) |
| i_bBlockCylinderUp | BOOL | FALSE | TRUE/FALSE | 阻挡气缸上位 | OB1→IO(X24/34/44/54) |
| i_bBlockCylinderDown | BOOL | FALSE | TRUE/FALSE | 阻挡气缸下位 | OB1→IO(X25/35/45/55) |
| i_bSeparateCylinderUp | BOOL | FALSE | TRUE/FALSE | 分料气缸上位 | OB1→IO(X26/36/46/56) |
| i_bSeparateCylinderDown | BOOL | FALSE | TRUE/FALSE | 分料气缸下位 | OB1→IO(X27/37/47/57) |
| i_bVfdFault | BOOL | FALSE | TRUE/FALSE | 变频器异常 | OB1→IO(X14~X17) |

### 3.2 VAR_OUTPUT

| 名称 | 类型 | 默认值 | 有效值域 | 说明 | 去向 |
|------|------|--------|----------|------|------|
| q_bBlockSolenoid | BOOL | FALSE | TRUE/FALSE | 阻挡气缸输出(ON=下降) | OB1→IO(Y30~Y37) |
| q_bSeparateSolenoid | BOOL | FALSE | TRUE/FALSE | 分料气缸输出(ON=推出) | OB1→IO(Y30~Y37) |
| q_bConveyorFwd | BOOL | FALSE | TRUE/FALSE | 输送带正转 | OB1→IO(Y10~Y23) |
| q_bConveyorRev | BOOL | FALSE | TRUE/FALSE | 输送带反转 | OB1→IO(Y10~Y23) |
| q_bConveyorSlow | BOOL | FALSE | TRUE/FALSE | 输送带慢速 | OB1→IO(Y10~Y23) |
| q_iCurrentState | INT | 0 | 0~70, 99 | 当前步序值 | OB1→HMI(D122) |
| q_iAlarmCode | INT | 0 | 0~9999 | 当前报警码(0=正常) | OB1→FB_2001 |
| q_bLayerFeedDone | BOOL | FALSE | TRUE/FALSE | 本层放料完成脉冲 | OB1→FB_1003 |
| q_bSensorFaultBlockUp | BOOL | FALSE | TRUE/FALSE | 阻挡上位传感器冗余不一致 | OB1→FB_2001 |
| q_bSensorFaultBlockDown | BOOL | FALSE | TRUE/FALSE | 阻挡下位传感器冗余不一致 | OB1→FB_2001 |
| q_bSensorFaultSeparateUp | BOOL | FALSE | TRUE/FALSE | 分料上位传感器冗余不一致 | OB1→FB_2001 |
| q_bSensorFaultSeparateDown | BOOL | FALSE | TRUE/FALSE | 分料下位传感器冗余不一致 | OB1→FB_2001 |
| q_bSeparateTimeout | BOOL | FALSE | TRUE/FALSE | 分料动作超时 | OB1→FB_2001 |
| q_bRunning | BOOL | FALSE | TRUE/FALSE | 运行中状态 | OB1→HMI |

### 3.3 VAR (内部变量)

| 名称 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| bStepEntry | BOOL | TRUE | 新步入口标志 |
| bPickupConfirmed | BOOL | FALSE | 取料确认(来自FB_1003) |
| tSeparateTimer | TON | — | 分料超时定时器 |
| tSlowTimer | TON | — | 慢速送出定时器 |
| tConvFwdTimer | TON | — | 输送正转定时器 |
| tInitTimer | TON | — | 初始化反转定时器 |

## 4. 互锁规则

| 互锁信号 | 条件 | 影响 |
|----------|------|------|
| i_bSafetyDoorOk = FALSE | M8取反门控 | 禁止输送正转/反转输出 |
| i_bPickPlaceSafeZone = FALSE | M515 | 暂停当前层输送，等待取料机构离开 |
| i_bVfdFault = TRUE | 变频器故障 | 立即停止所有输送输出，置报警 |

## 5. 关联文档

| 文档 | 路径 |
|------|------|
| DSN | 详细设计说明书_DSN-FB1002-SingleLayerConveyor-V6.0.0.md |
| CHG | 变更记录_CHG-FB1002-SingleLayerConveyor-V6.0.0.md |
| UM | 使用说明_UM-FB1002-SingleLayerConveyor-V6.0.0.md |
| 源程序基线 | ../../PRD-SRC/源程序功能基线_SRC-DJ-2026-005-V1.0.0.md |
