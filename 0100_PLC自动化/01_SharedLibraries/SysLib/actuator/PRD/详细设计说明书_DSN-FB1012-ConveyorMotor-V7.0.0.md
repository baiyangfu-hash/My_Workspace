# 详细设计说明书 FB_1012_ConveyorMotor

## 0. 文档基础信息

| 属性 | 值 |
|------|-----|
| **文档标题** | FB_1012 输送电机控制详细设计 |
| **文档版本** | V7.0.0 |
| **关联源码** | conveyor/FB_1012_ConveyorMotor.scl |
| **关联IFC** | 接口文档_IFC-FB1012-ConveyorMotor-V7.0.0.md |
| **编制日期** | 2026-05-18 |
| **编制人** | Trae |
| **遵循规范** | 801_DEV-V1.0.5, 810_DEV-V1.0.2 |

## 1. 设计原则

1. **命令透传+互锁**: 接收方向命令，通过安全互锁后输出，不自行产生命令
2. **故障优先**: VFD故障时无条件切断所有输出（最高优先级）
3. **安全优先**: 安全门打开时封锁所有运动输出
4. **方向互斥**: 同一时刻只有一个方向有效（Fwd > Rev > Slow）
5. **无时序依赖**: 纯组合+锁存逻辑，无定时器

## 2. 互锁优先级链

```
优先级从高到低:
┌───────────────────┐
│  1. VFD故障       │ → 所有输出 := FALSE, q_bVfdAlarm := TRUE
├───────────────────┤
│  2. 安全门打开     │ → 所有输出 := FALSE
├───────────────────┤
│  3. 方向命令仲裁   │ → Fwd > Rev > Slow (只有一个生效)
├───────────────────┤
│  4. 正常输出       │ → q_bXxx := i_bXxx (经上述过滤后)
└───────────────────┘
```

## 3. 详细伪代码

```pascal
(* ==================== VFD 故障检测 ==================== *)
IF i_bVfdFault THEN
    q_bVfdAlarm := TRUE;
    q_bFwd := FALSE;
    q_bRev := FALSE;
    q_bSlow := FALSE;
    q_bRunning := FALSE;
    RETURN;
ELSE
    q_bVfdAlarm := FALSE;
END_IF;

(* ==================== 安全门互锁 ==================== *)
IF NOT i_bSafetyDoorOk THEN
    q_bFwd := FALSE;
    q_bRev := FALSE;
    q_bSlow := FALSE;
    q_bRunning := FALSE;
    RETURN;
END_IF;

(* ==================== 方向命令仲裁 ==================== *)
(* 优先级: Fwd > Rev > Slow *)

IF i_bFwd THEN
    q_bFwd := TRUE;
    q_bRev := FALSE;
    q_bSlow := FALSE;
    q_bRunning := TRUE;
ELSIF i_bRev THEN
    q_bFwd := FALSE;
    q_bRev := TRUE;
    q_bSlow := FALSE;
    q_bRunning := TRUE;
ELSIF i_bSlow THEN
    q_bFwd := FALSE;
    q_bRev := FALSE;
    q_bSlow := TRUE;
    q_bRunning := TRUE;
ELSE
    q_bFwd := FALSE;
    q_bRev := FALSE;
    q_bSlow := FALSE;
    q_bRunning := FALSE;
END_IF;
```

## 4. 命令真值表

| i_bFwd | i_bRev | i_bSlow | 安全门 | VFD | q_bFwd | q_bRev | q_bSlow | q_bRunning |
|:------:|:------:|:-------:|:------:|:---:|:------:|:------:|:-------:|:----------:|
| 0 | 0 | 0 | OK | OK | 0 | 0 | 0 | 0 |
| 1 | 0 | 0 | OK | OK | 1 | 0 | 0 | 1 |
| 0 | 1 | 0 | OK | OK | 0 | 1 | 0 | 1 |
| 0 | 0 | 1 | OK | OK | 0 | 0 | 1 | 1 |
| 1 | 1 | 0 | OK | OK | 1 | 0 | 0 | 1 |
| 1 | 1 | 1 | OK | OK | 1 | 0 | 0 | 1 |
| x | x | x | 开 | OK | 0 | 0 | 0 | 0 |
| x | x | x | x | 故障 | 0 | 0 | 0 | 0 |

## 5. 速度参考值

`i_rSpeed` 作为透传参数，本 FB 不处理速度闭环。编排器 FB_1002 或 OB1 负责将其写入对应的模拟量输出或通过总线传给变频器。

```
(* 速度值仅透传，不作为本FB的输出 *)
(* 使用方通过读取 i_rSpeed 或从编排器/OB1获取 *)
```

## 6. 关联文档

| 文档 | 路径 |
|------|------|
| IFC | 接口文档_IFC-FB1012-ConveyorMotor-V7.0.0.md |
| 气缸控制 DSN | 详细设计说明书_DSN-FB1011-CylinderControl-V7.0.0.md |
| 编排器 DSN | ../../../../DJ-2026-005/02_PLC程序/通用ST程序及变量表/conveyor/PRD/详细设计说明书_DSN-FB1002-SingleLayerConveyor-V7.0.0.md |
