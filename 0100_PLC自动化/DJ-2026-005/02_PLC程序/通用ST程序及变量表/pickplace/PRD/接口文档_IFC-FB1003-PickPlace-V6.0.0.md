# 接口文档 FB_1003_PickPlace_BufferFraming

## 0. 文档基础信息

| 属性 | 值 |
|------|-----|
| **文档标题** | FB_1003 取放料机构接口定义 |
| **文档版本** | V6.0.0 |
| **关联源码** | pickplace/FB_1003_PickPlace_BufferFraming.scl |
| **编制日期** | 2026-05-17 |
| **编制人** | Trae |
| **遵循规范** | 801_DEV-V1.0.5, 810_DEV-V1.0.2 |
| **数据来源** | 源程序功能基线_SRC-DJ-2026-005-V1.0.0 |

## 1. 功能概述

取放料机构控制块。Z轴升降 + X1轴横移 + 4组夹爪(前/后/前2/后2)控制。6步状态机(S20~S25)，一次取两根边框。产品检测在S22步内完成。

## 2. 状态机步序常量

| 常量名 | 值 | 步骤名 | 说明 |
|--------|---|--------|------|
| S20_IDLE | 0 | 待机等待 | Z待机位，等取料请求 |
| S21_UP_TO_PICK | 1 | 上升到取料高度 | Z→D514取片教点 |
| S22_CLAMP_AND_DETECT | 2 | 夹紧与检测 | 4夹紧+4光电+确认时间 |
| S23_MOVE_TO_PLACE | 3 | 移动到放料位置 | L1/L3→D520, L2/L4→D540 |
| S24_DOWN_TO_PLACE | 4 | 下降到放料高度 | Z→D524放片教点 |
| S25_UNCLAMP_AND_NOTIFY | 5 | 松开与通知 | 4松开+发信号给FB_1004 |

## 3. VAR_INPUT

| 名称 | 类型 | 默认值 | 说明 | 来源 |
|------|------|--------|------|------|
| i_bAutoMode | BOOL | FALSE | 自动模式 | OB1←HMI |
| i_bManualMode | BOOL | FALSE | 手动模式 | OB1←HMI |
| i_bStart | BOOL | FALSE | 启动 | OB1←HMI(M2) |
| i_bStop | BOOL | FALSE | 停止 | OB1←HMI(M3) |
| i_bLx_FrontClamp | BOOL | FALSE | 手动:前夹紧 | OB1←HMI |
| i_bLx_RearClamp | BOOL | FALSE | 手动:后夹紧 | OB1←HMI |
| i_bLx_FrontClamp2 | BOOL | FALSE | 手动:前夹紧2 | OB1←HMI |
| i_bLx_RearClamp2 | BOOL | FALSE | 手动:后夹紧2 | OB1←HMI |
| i_bLx_LiftUp | BOOL | FALSE | 手动:升降上升 | OB1←HMI |
| i_bLx_LiftDown | BOOL | FALSE | 手动:升降下降 | OB1←HMI |
| i_iPickLayer | INT | 0 | 1~4:当前取料层号 | OB1←HMI |
| i_rZSpeed | REAL | 0.0 | Z轴速度 | OB1←HMI(D102) |
| i_rX1Speed | REAL | 0.0 | X1轴速度 | OB1←HMI(D103) |
| i_iClampConfirmTime | INT | 0 | 夹紧确认时间(ms) | OB1←HMI(D104) |
| i_iLiftActionTime | INT | 0 | 升降动作超时(ms) | OB1←HMI(D105) |
| i_bLayerFeedDone[1..4] | BOOL[1..4] | FALSE | L1~L4各层放料完成 | OB1←FB_1002 |
| i_bLongEdge1Detect | BOOL | FALSE | 长边1光电(X60) | OB1←IO |
| i_bLongEdge2Detect | BOOL | FALSE | 长边2光电(X61) | OB1←IO |
| i_bShortEdge1Detect | BOOL | FALSE | 短边1光电(X62) | OB1←IO |
| i_bShortEdge2Detect | BOOL | FALSE | 短边2光电(X63) | OB1←IO |
| i_bFrontClampClosed | BOOL | FALSE | 前夹紧位1(X66) | OB1←IO |
| i_bFrontClampOpened | BOOL | FALSE | 前松开位1(X67) | OB1←IO |
| i_bRearClampClosed | BOOL | FALSE | 后夹紧位1(X64) | OB1←IO |
| i_bRearClampOpened | BOOL | FALSE | 后松开位1(X65) | OB1←IO |
| i_bFrontClamp2Closed | BOOL | FALSE | 前夹紧位2(X126) | OB1←IO |
| i_bFrontClamp2Opened | BOOL | FALSE | 前松开位2(X127) | OB1←IO |
| i_bRearClamp2Closed | BOOL | FALSE | 后夹紧位2(X124) | OB1←IO |
| i_bRearClamp2Opened | BOOL | FALSE | 后松开位2(X125) | OB1←IO |
| i_bLiftHomePos | BOOL | FALSE | 升降上位(X70) | OB1←IO |
| i_bLiftWorkPoint | BOOL | FALSE | 升降下位(X71) | OB1←IO |
| i_bFrameDetect1 | BOOL | FALSE | 边框检测1(X154) | OB1←IO |
| i_bFrameDetect2 | BOOL | FALSE | 边框检测2(X155) | OB1←IO |
| i_bFullMaterialDetect1 | BOOL | FALSE | 满料检测1(X156) | OB1←IO |
| i_bFullMaterialDetect2 | BOOL | FALSE | 满料检测2(X157) | OB1←IO |

## 4. VAR_OUTPUT

| 名称 | 类型 | 默认值 | 说明 | 去向 |
|------|------|--------|------|------|
| q_bFrontClamp | BOOL | FALSE | 前夹紧输出(Y41) | OB1→IO |
| q_bRearClamp | BOOL | FALSE | 后夹紧输出(Y40) | OB1→IO |
| q_bFrontClamp2 | BOOL | FALSE | 前夹紧2输出 | OB1→IO |
| q_bRearClamp2 | BOOL | FALSE | 后夹紧2输出 | OB1→IO |
| q_bLiftUp | BOOL | FALSE | 上升(Y42) | OB1→IO |
| q_bLiftDown | BOOL | FALSE | 下降(Y43) | OB1→IO |
| q_bZAxisHomeRequest | BOOL | FALSE | Z轴回原点请求 | OB1→轴FB |
| q_bZAxisMoveAbsReq | BOOL | FALSE | Z轴绝对定位请求 | OB1→轴FB |
| q_rZAxisTargetPos | REAL | 0.0 | Z轴目标位置 | OB1→轴FB |
| q_bX1AxisHomeRequest | BOOL | FALSE | X1轴回原点请求 | OB1→轴FB |
| q_bX1AxisMoveAbsReq | BOOL | FALSE | X1轴绝对定位请求 | OB1→轴FB |
| q_rX1AxisTargetPos | REAL | 0.0 | X1轴目标位置 | OB1→轴FB |
| q_iCurrentState | INT | 0 | 当前步序(0~5=S20~S25) | OB1→HMI(D126) |
| q_iCurrentPickLayer | INT | 0 | 当前取料层(1~4) | OB1→HMI(D121) |
| q_iAlarmCode | INT | 0 | 当前报警码 | OB1→FB_2001 |
| q_bPlaceDoneToFeeder | BOOL | FALSE | 放料完成通知FB_1004 | OB1→FB_1004 |
| q_bSensorFault | BOOL | FALSE | 夹紧/升降传感器冗余不一致 | OB1→FB_2001 |
| q_bProductMissing | BOOL | FALSE | 4光电未全检到(取料失败) | OB1→FB_2001 |
| q_bFrameOnPickupPlatform | BOOL | FALSE | 取料平台有边框(阻塞回原点F80) | OB1→FB_2001 |
| q_bRunning | BOOL | FALSE | 运行中 | OB1→HMI |

## 5. 关联文档

| 文档 | 路径 |
|------|------|
| DSN | 详细设计说明书_DSN-FB1003-PickPlace-V6.0.0.md |
| CHG | 变更记录_CHG-FB1003-PickPlace-V6.0.0.md |
| UM | 使用说明_UM-FB1003-PickPlace-V6.0.0.md |
