# 接口文档 FB_1004_GlueMachineFeeder_BufferFraming

## 0. 文档基础信息

| 属性 | 值 |
|------|-----|
| **文档标题** | FB_1004 打胶机送料接口定义 |
| **文档版本** | V8.1.0 |
| **关联源码** | 04_打胶机送料/FB_1004_GlueMachineFeeder_BufferFraming.scl |
| **编制日期** | 2026-05-17 |
| **编制人** | Trae |
| **遵循规范** | LSP-905 |
| **数据来源** | 源程序功能基线_SRC-DJ-2026-005-V1.0.0 |

## 1. 功能概述

X2轴横移+打胶机交互控制。4步D760状态机，收到取放料放料完成后直接去取料位取边框，再送料到打胶机位置交互。

## 2. 状态机步序常量(D760)

| 常量名 | 值 | 步骤名 | 说明 |
|--------|---|--------|------|
| D760_IDLE | 0 | 空闲待机 | 等待FB_1003放料完成 |
| D760_MOVE_TO_PICKUP | 1 | X2→取料位 | 移动到取料点D620 |
| D760_MOVE_TO_GLUE | 2 | X2→打胶机送料 | 到D630,关Y47,等X76发Y44,等X102 |
| D760_RETURN_STANDBY | 3 | X2→待机位 | 返回D610,开Y47 |

## 3. VAR_INPUT

| 名称 | 类型 | 默认值 | 说明 | 来源 |
|------|------|--------|------|------|
| i_bAutoMode | BOOL | FALSE | 自动模式 | OB1←HMI |
| i_bManualMode | BOOL | FALSE | 手动模式 | OB1←HMI |
| i_bStart | BOOL | FALSE | 启动 | OB1←HMI(M2) |
| i_bStop | BOOL | FALSE | 停止 | OB1←HMI(M3) |
| i_bLx_X2JogPos | BOOL | FALSE | 手动:X2正向点动 | OB1←HMI |
| i_bLx_X2JogNeg | BOOL | FALSE | 手动:X2反向点动 | OB1←HMI |
| i_bPlaceDone | BOOL | FALSE | FB_1003放料完成脉冲 | OB1←FB_1003 |
| i_rX2Speed | REAL | 0.0 | X2轴速度 | OB1←HMI |
| i_bGlueMachineAllowFeed | BOOL | FALSE | 打胶机允许送料(X76) | OB1←IO |
| i_bGlueMachinePickupComplete | BOOL | FALSE | 打胶机取料完成(X102) | OB1←IO |
| i_bX2ZoneSensor1 | BOOL | FALSE | X2区域前传感器1(X72) | OB1←IO |
| i_bX2ZoneSensor2 | BOOL | FALSE | X2区域前传感器2(X73) | OB1←IO |
| i_bX2ZoneSensor3 | BOOL | FALSE | X2区域后传感器1(X74) | OB1←IO |
| i_bX2ZoneSensor4 | BOOL | FALSE | X2区域后传感器2(X75) | OB1←IO |

## 4. VAR_OUTPUT

| 名称 | 类型 | 默认值 | 说明 | 去向 |
|------|------|--------|------|------|
| q_bX2AxisHomeRequest | BOOL | FALSE | X2回原点请求 | OB1→轴FB |
| q_bX2AxisMoveAbsReq | BOOL | FALSE | X2绝对定位请求 | OB1→轴FB |
| q_rX2AxisTargetPos | REAL | 0.0 | X2目标位置 | OB1→轴FB |
| q_bAllowPickup | BOOL | FALSE | 允许打胶机抓料(Y44) | OB1→IO |
| q_bSafetyZoneSignal | BOOL | FALSE | 打胶机安全区(Y47) | OB1→IO |
| q_iCurrentState | INT | 0 | 当前D760值(0~3) | OB1→HMI |
| q_iAlarmCode | INT | 0 | 当前报警码 | OB1→FB_2001 |
| q_bFrameOnFeedPlatform | BOOL | FALSE | 送料平台有边框(阻塞回原点F81) | OB1→FB_2001 |
| q_bRunning | BOOL | FALSE | 运行中 | OB1→HMI |

## 5. 状态机伪代码

```
CASE q_iCurrentState OF
  D760_IDLE: (* 0 *)
    q_bX2AxisMoveAbsReq := FALSE;
    q_bAllowPickup := FALSE;
    q_bSafetyZoneSignal := FALSE;  (* 安全区开放 *)
    IF i_bPlaceDone THEN
      q_iCurrentState := D760_MOVE_TO_PICKUP;
    END_IF;

  D760_MOVE_TO_PICKUP: (* 1: X2→取料点D620 *)
    q_rX2AxisTargetPos := rPickupPos;       (* D620 *)
    q_bX2AxisMoveAbsReq := TRUE;
    IF i_bX2AxisInPos THEN
      q_iCurrentState := D760_MOVE_TO_GLUE;
    END_IF;

  D760_MOVE_TO_GLUE: (* 2: X2→放料点D630，交互 *)
    q_rX2AxisTargetPos := rGluePlacePos;    (* D630 *)
    q_bX2AxisMoveAbsReq := TRUE;
    IF i_bX2AxisInPos THEN
      q_bSafetyZoneSignal := TRUE;           (* 关安全区Y47 *)
      IF i_bGlueMachineAllowFeed THEN
        q_bAllowPickup := TRUE;              (* 发Y44 *)
      END_IF;
      IF i_bGlueMachinePickupComplete THEN
        q_bAllowPickup := FALSE;
        q_iCurrentState := D760_RETURN_STANDBY;
      END_IF;
    END_IF;

  D760_RETURN_STANDBY: (* 3: X2→待机位D610 *)
    q_rX2AxisTargetPos := rStandbyPos;      (* D610 *)
    q_bX2AxisMoveAbsReq := TRUE;
    IF i_bX2AxisInPos THEN
      q_bSafetyZoneSignal := FALSE;          (* 开安全区 *)
      q_iCurrentState := D760_IDLE;
    END_IF;
END_CASE;
```

## 6. 报警码

| 码 | 含义 |
|:--:|------|
| 201 | X2轴伺服故障 |
| 202 | X2轴限位触发 |
| 203 | X2轴移动超时 |
| 204 | 安全区传感器异常 |
| 205 | 送料平台有边框(回原点阻塞) |

## 7. 关联文档

| 文档 | 路径 |
|------|------|
| DSN | 详细设计说明书_DSN-FB1004-GlueMachineFeeder-V6.0.0.md |
| CHG | 变更记录_CHG-FB1004-GlueMachineFeeder-V6.0.0.md |
| UM | 使用说明_UM-FB1004-GlueMachineFeeder-V6.0.0.md |
