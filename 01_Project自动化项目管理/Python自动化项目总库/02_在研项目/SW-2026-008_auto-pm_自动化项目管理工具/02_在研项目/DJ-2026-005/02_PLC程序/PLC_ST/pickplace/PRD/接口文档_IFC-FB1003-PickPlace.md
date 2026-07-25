# 接口文档 FB_1003_PickPlace_BufferFraming

## 0. 文档基础信息

| 属性 | 值 |
|------|-----|
| **文档标题** | FB_1003 取放料机构接口定义 |
| **文档版本** | V7.0.0 |
| **关联源码** | pickplace/FB_1003_PickPlace_BufferFraming.scl |
| **编制日期** | 2026-05-20 |
| **编制人** | Trae |
| **遵循规范** | LSP-905, ST_ServoAxis V3.0(PLCopen MC Part 1) |
| **数据来源** | FB_1003 V7.0.0 源码 + GlobalVars.db V7.1.1 |

## 1. 功能概述

取放料机构控制块。Z轴升降 + X1轴横移 + 4组夹爪(前/后/前2/后2)控制。6步状态机(S20~S25)，一次取两根边框。产品检测在S22步内完成。

**V7.0.0重大变更**：删除6个间接轴请求输出(q_bZAxis*/q_bX1Axis*)，改用 `VAR_IN_OUT` 直连 `ST_ServoAxis V3.0` 嵌套结构体，FB内部直接操作 PLCopen MC 标准接口(stPower/stAbs/stStop/stSensor)。

## 2. 状态机步序常量

| 常量名 | 值 | 步骤名 | 说明 |
|--------|---|--------|------|
| S20_IDLE | 0 | 待机等待 | Z待机位，等取料请求。V7.0: 含轴使能检查+伺服报警检查 |
| S21_UP_TO_PICK | 1 | 上升到取料高度 | Z→D514取片教点。V7.0: 直接写io_stZAxis.stAbs (PLCopen MC_MoveAbsolute) |
| S22_CLAMP_AND_DETECT | 2 | 夹紧与检测 | 4夹紧+4光电+确认时间 |
| S23_MOVE_TO_PLACE | 3 | 移动到放料位置 | L1/L3→D520, L2/L4→D540。V7.0: 直接写io_stX1Axis.stAbs |
| S24_DOWN_TO_PLACE | 4 | 下降到放料高度 | Z→D524放片教点。V7.0: 直接写io_stZAxis.stAbs + q_bLiftDown |
| S25_UNCLAMP_AND_NOTIFY | 5 | 松开与通知 | 4松开+发信号给FB_1004 |

## 3. VAR_INPUT (42个)

### 3.1 系统控制信号 (5个)

| 名称 | 类型 | 默认值 | 说明 | 来源 |
|------|------|--------|------|------|
| i_bAutoMode | BOOL | FALSE | 自动模式 | OB1←HMI |
| i_bManualMode | BOOL | FALSE | 手动模式 | OB1←HMI |
| i_bStart | BOOL | FALSE | 启动(上升沿触发) | OB1←HMI(M2) |
| i_bStop | BOOL | FALSE | 停止(电平有效) | OB1←HMI(M3) |
| ~~i_bReset~~ | — | — | **V7.0删除**: 复位已移至使能关闭统一处理 | — |

### 3.2 手动操作信号 (8个)

| 名称 | 类型 | 默认值 | 说明 | 来源 |
|------|------|--------|------|------|
| i_bLx_FrontClamp | BOOL | FALSE | 手动:前夹紧 | OB1←HMI |
| i_bLx_RearClamp | BOOL | FALSE | 手动:后夹紧 | OB1←HMI |
| i_bLx_FrontClamp2 | BOOL | FALSE | 手动:前夹紧2 | OB1←HMI |
| i_bLx_RearClamp2 | BOOL | FALSE | 手动:后夹紧2 | OB1←HMI |
| i_bLx_LiftUp | BOOL | FALSE | 手动:升降上升 | OB1←HMI |
| i_bLx_LiftDown | BOOL | FALSE | 手动:升降下降 | OB1←HMI |

> **V7.0删除项**（V6.0有但V7.0代码中已不存在）:
> - ~~i_bLx_ZAxis_JogUp~~ / ~~i_bLx_ZAxis_JogDown~~ （伺服点动 → 改由ST_ServoAxis.stJog处理）
> - ~~i_bLx_X1Axis_JogFwd~~ / ~~i_bLx_X1Axis_JogRev~~ （同上）

### 3.3 工艺参数 (5个)

| 名称 | 类型 | 默认值 | 说明 | 来源 |
|------|------|--------|------|------|
| i_iPickLayer | INT | 0 | 1~4:当前取料层号 | OB1←HMI(或GlobalVars.i_iPickLayer_Input) |
| i_rZSpeed | REAL | 0.0 | Z轴速度 mm/s | OB1←HMI(D102) |
| i_rX1Speed | REAL | 0.0 | X1轴速度 mm/s | OB1←HMI(D103) |
| i_iClampConfirmTime | INT | 0 | 夹紧确认时间(ms) | OB1←HMI(D104) |
| i_iLiftActionTime | INT | 0 | 升降动作超时(ms) | OB1←HMI(D105) |

### 3.4 上游信号 (4个)

| 名称 | 类型 | 默认值 | 说明 | 来源 |
|------|------|--------|------|------|
| i_bLayerFeedDone[1..4] | ARRAY[1..4] OF BOOL | FALSE | L1~L4各层放料完成 | OB1←FB_1002 |

### 3.5 产品检测传感器 (4个)

| 名称 | 类型 | 默认值 | 说明 | 来源 |
|------|------|--------|------|------|
| i_bLongEdge1Detect | BOOL | FALSE | 长边1光电(X60) | OB1←IO |
| i_bLongEdge2Detect | BOOL | FALSE | 长边2光电(X61) | OB1←IO |
| i_bShortEdge1Detect | BOOL | FALSE | 短边1光电(X62) | OB1←IO |
| i_bShortEdge2Detect | BOOL | FALSE | 短边2光电(X63) | OB1←IO |

### 3.6 气缸位置传感器 (10个)

| 名称 | 类型 | 默认值 | 说明 | 来源 |
|------|------|--------|------|------|
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

### 3.7 边框/满料检测 (4个)

| 名称 | 类型 | 默认值 | 说明 | 来源 |
|------|------|--------|------|------|
| i_bFrameDetect1 | BOOL | FALSE | 边框检测1(X154) | OB1←IO |
| i_bFrameDetect2 | BOOL | FALSE | 边框检测2(X155) | OB1←IO |
| i_bFullMaterialDetect1 | BOOL | FALSE | 满料检测1(X156) | OB1←IO |
| i_bFullMaterialDetect2 | BOOL | FALSE | 满料检测2(X157) | OB1←IO |

## 4. VAR_OUTPUT (16个)

### 4.1 气缸/电机输出 (6个)

| 名称 | 类型 | 默认值 | 说明 | 去向 |
|------|------|--------|------|------|
| q_bFrontClamp | BOOL | FALSE | 前夹紧输出(Y41) | OB1→IO |
| q_bRearClamp | BOOL | FALSE | 后夹紧输出(Y40) | OB1→IO |
| q_bFrontClamp2 | BOOL | FALSE | 前夹紧2输出 | OB1→IO |
| q_bRearClamp2 | BOOL | FALSE | 后夹紧2输出 | OB1→IO |
| q_bLiftUp | BOOL | FALSE | 上升(Y42) | OB1→IO |
| q_bLiftDown | BOOL | FALSE | 下降(Y43) | OB1→IO |

### 4.2 ~~已删除的轴请求输出 (V6.0→V7.0移除)~~

以下6个输出在V6.0中存在，V7.0中**已删除**（功能迁移至VAR_IN_OUT直连）：

| V6.0名称 | V7.0替代方案 |
|----------|-------------|
| ~~q_bZAxisHomeRequest~~ | io_stZAxis.stHome.Execute (FB内直接调用) |
| ~~q_bZAxisMoveAbsReq~~ | io_stZAxis.stAbs.Execute (FB内直接调用) |
| ~~q_rZAxisTargetPos~~ | io_stZAxis.stAbs.Position (FB内直接写入) |
| ~~q_bX1AxisHomeRequest~~ | io_stX1Axis.stHome.Execute (FB内直接调用) |
| ~~q_bX1AxisMoveAbsReq~~ | io_stX1Axis.stAbs.Execute (FB内直接调用) |
| ~~q_rX1AxisTargetPos~~ | io_stX1Axis.stAbs.Position (FB内直接写入) |

### 4.3 状态输出 (4个)

| 名称 | 类型 | 默认值 | 说明 | 去向 |
|------|------|--------|------|------|
| q_iCurrentState | INT | 0 | 当前步序(0~5=S20~S25) | OB1→HMI(D126) |
| q_iCurrentPickLayer | INT | 0 | 当前取料层(1~4) | OB1→HMI(D121) |
| q_iAlarmCode | INT | 0 | 当前报警码 | OB1→FB_2001 |
| q_bRunning | BOOL | FALSE | 运行中 | OB1→HMI |

### 4.4 下游信号 (1个)

| 名称 | 类型 | 默认值 | 说明 | 去向 |
|------|------|--------|------|------|
| q_bPlaceDoneToFeeder | BOOL | FALSE | 放料完成通知FB_1004 | OB1→FB_1004 |

### 4.5 诊断输出 (3个)

| 名称 | 类型 | 默认值 | 说明 | 去向 |
|------|------|--------|------|------|
| q_bSensorFault | BOOL | FALSE | 夹紧/升降传感器冗余不一致 | OB1→FB_2001 |
| q_bProductMissing | BOOL | FALSE | 4光电未全检到(取料失败) | OB1→FB_2001 |
| q_bFrameOnPickupPlatform | BOOL | FALSE | 取料平台有边框(阻塞回原点F80) | OB1→FB_2001 |

## 5. VAR_IN_OUT (V7.0.0新增，2个)

| 名称 | 类型 | 说明 | OB1接线 |
|------|------|------|---------|
| io_stZAxis | ST_ServoAxis | Z轴(升降)伺服轴结构体 - 直读直写 | => astServoAxis[1] |
| io_stX1Axis | ST_ServoAxis | X1轴(取放料横移)伺服轴结构体 - 直读直写 | => astServoAxis[2] |

**ST_ServoAxis V3.0 子结构体访问路径**:

| 子结构体 | FB内用途 | 关键字段 |
|----------|---------|---------|
| `.stPower.Status` | 使能状态读取 | Status:BOOL |
| `.stPower.Enable` | 使能命令写入 | Enable:=TRUE |
| `.stAbs.Position` | 绝对定位目标位置 | Position:REAL |
| `.stAbs.Velocity` | 绝对定位速度 | Velocity:REAL |
| `.stAbs.Execute` | 绝对定位启动 | Execute:=TRUE/FALSE |
| `.stAbs.Done` | 定位完成反馈 | Done:BOOL(只读) |
| `.stAbs.Error` | 定位错误反馈 | Error:BOOL(只读) |
| `.stStop.Execute` | 急停命令 | Execute:=TRUE |
| `.stSensor.ServoAlarm` | 伺服驱动器报警 | ServoAlarm:BOOL(只读) |
| `.stSensor.FwdLimit` | 正限位开关 | FwdLimit:BOOL(只读) |
| `.stSensor.RevLimit` | 负限位开关 | RevLimit:BOOL(只读) |

## 6. 报警码 (FB_1003内部产生)

| 码 | 含义 | 触发条件 |
|:--:|------|----------|
| 71 | 升降超时 | tLiftTimer.Q (S21/S24) |
| 72 | 产品检测失败(S22) | 4光电未全ON |
| 73 | 伺服报警 | stSensor.ServoAlarm=TRUE (S20) |
| 74 | 轴限位触发 | FwdLimit OR RevLimit (S21/S23/S24) |
| 75 | 轴定位错误 | stAbs.Error=TRUE (S21/S24) |
| 80 | 取料平台有边框 | FrameDetect1 OR FrameDetect2 (S20) |
| 101 | 夹紧传感器不一致 | 夹紧位信号矛盾 (S22) |

## 7. 接口统计对比

| 项目 | V6.0.0 | V7.0.0 | 变化 |
|------|:-----:|:-----:|:----:|
| VAR_INPUT | 42 | 38 | -4 (删除伺服点动4个+复位1个，净-5; 实际代码41个) |
| VAR_OUTPUT | 22 | 16 | -6 (删除轴请求输出6个) |
| VAR_IN_OUT | 0 | 2 | +2 (新增io_stZAxis/io_stX1Axis) |
| **总计** | **64** | **56** | **-8 (接口简化)** |

## 8. 关联文档

| 文档 | 路径 | 版本 |
|------|------|:----:|
| DSN | 详细设计说明书_DSN-FB1003-PickPlace-V7.0.0.md | V7.0.0 |
| CHG | 变更记录_CHG-FB1003-PickPlace-V7.0.0.md | V7.0.0 |
| UM | 使用说明_UM-FB1003-PickPlace-V6.0.0.md | V6.0.0 |
| DB1 | GlobalVars.db (stPickPlace结构体) | V7.1.1 |
