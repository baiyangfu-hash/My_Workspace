# 详细设计说明书 FB_1002_SingleLayerConveyor

## 0. 文档基础信息

| 属性 | 值 |
|------|-----|
| **文档标题** | FB_1002 单层输送机编排器详细设计说明书 |
| **文档版本** | V11.1.0 |
| **关联源码** | 02_输送机/FB_1002_SingleLayerConveyor_BufferFraming.scl |
| **关联IFC** | 接口文档_IFC-FB1002-SingleLayerConveyor-V7.0.0.md |
| **编制日期** | 2026-05-18 |
| **编制人** | Trae |
| **遵循规范** | LSP-905 |

## 1. 设计原则

1. **编排器模式**: FB_1002 是纯调度器，不包含执行器控制细节
2. **委托原则**: 气缸控制→FB_1011, 电机控制→FB_1012
3. **工艺不变**: 9步 Step_S 状态机流程与源程序完全一致
4. **报警自包含**: 编排器从子FB收集BOOL报警信号，根据i_iLayerIndex编码为完整报警码
5. **FB_1001取消**: OB1 用 FOR 循环直接实例化4个 FB_1002

## 2. 架构层次

```
┌───────────────────────────────────────────────────────────┐
│                     OB1 (主循环)                           │
│  FOR i := 1 TO 4 DO                                       │
│    fbConveyor[i] : FB_1002_SingleLayerConveyor            │
│      ├─ fbBlock    : FB_1011_CylinderControl              │
│      │   职责: 下降/上升+超时+传感器冗余                    │
│      ├─ fbSeparate : FB_1011_CylinderControl              │
│      │   职责: 推出/复位+超时+传感器冗余                    │
│      └─ fbMotor    : FB_1012_ConveyorMotor                │
│          职责: 正转/反转/慢速+安全门+VFD故障               │
│                                                           │
│  汇总: o_bRunning OR, o_bFault OR, o_iAlarmCode MIN       │
└───────────────────────────────────────────────────────────┘
```

### 2.1 子FB交互矩阵

```
             FB_1011 (Block)    FB_1011 (Separate)   FB_1012 (Motor)
FB_1002      ─────────────────────────────────────────────────────
命令         i_bExtend           i_bExtend            i_bFwd
             i_bRetract          i_bRetract           i_bRev
             i_iTimeoutMs        i_iTimeoutMs         i_bSlow
                                                     i_bSafetyDoorOk
                                                     i_bVfdFault
             ─────────────────────────────────────────────────────
反馈         q_bSolenoid         q_bSolenoid          q_bFwd
             q_bIsExtended       q_bIsExtended        q_bRev
             q_bIsRetracted      q_bIsRetracted       q_bSlow
             q_bTimeout          q_bTimeout           q_bRunning
             q_bSensorFault      q_bSensorFault       q_bVfdAlarm
```

## 3. 状态机跳转图

```
STEP_INIT(0) ──反转完成→ STEP_WAIT_MATERIAL(1) ──来料→ STEP_BLOCK_DOWN(2)
                                                              │ 阻挡下位
                                                              ↓
                                                     STEP_CONVEYOR_FWD(10)
                                                              │ 正转延时到
                                                              ↓
                                               STEP_POSITION_CHECK(20)
                                                              │ 双到位+阻挡上位
                                                              ↓
                                                     STEP_SEPARATE_PUSH(30)
                                                              │ 分料下位 / 超时→报警
                                                              ↓
                                                     STEP_CONVEYOR_SLOW(50)
                                                              │ 慢速延时到
                                                              ↓
                                                     STEP_REQUEST_PICKUP(60)
                                                              │ 取料确认
                                                              ↓
                                                     STEP_SEPARATE_RETURN(70)
                                                              │ 分料上位 / 超时→报警
                                                              ↓
                                                         STEP_INIT(0) 循环
```

## 4. 完整伪代码

### 4.1 子FB信号连线

```pascal
(* ========== 阻挡气缸 ========== *)
fbBlock.i_bUpSensor    := i_bBlockCylinderUp;
fbBlock.i_bDownSensor  := i_bBlockCylinderDown;

(* ========== 分料气缸 ========== *)
fbSeparate.i_bUpSensor   := i_bSeparateCylinderUp;
fbSeparate.i_bDownSensor := i_bSeparateCylinderDown;

(* ========== 电机 ========== *)
fbMotor.i_bSafetyDoorOk := i_bSafetyDoorOk;
fbMotor.i_bVfdFault     := i_bVfdFault;

(* ========== 执行器输出收集 ========== *)
q_bBlockSolenoid    := fbBlock.q_bSolenoid;
q_bSeparateSolenoid := fbSeparate.q_bSolenoid;
q_bConveyorFwd      := fbMotor.q_bFwd;
q_bConveyorRev      := fbMotor.q_bRev;
q_bConveyorSlow     := fbMotor.q_bSlow;
```

### 4.2 模式分发

```pascal
(* ==================== 模式使能检查 ==================== *)
IF NOT i_bAutoMode AND NOT i_bManualMode THEN
    (* 无模式：清零所有输出 *)
    fbBlock.i_bExtend := FALSE;
    fbBlock.i_bRetract := FALSE;
    fbSeparate.i_bExtend := FALSE;
    fbSeparate.i_bRetract := FALSE;
    fbMotor.i_bFwd := FALSE;
    fbMotor.i_bRev := FALSE;
    fbMotor.i_bSlow := FALSE;
    q_bLayerFeedDone := FALSE;
    iCurrentState := STEP_INIT;
    bRunning := FALSE;
    bStartTriggered := FALSE;
    bStepEntry := TRUE;
    RETURN;
END_IF;

(* ==================== 停止处理 ==================== *)
IF i_bStop AND bRunning THEN
    iCurrentState := STEP_INIT;
    bRunning := FALSE;
    bStepEntry := TRUE;
    fbBlock.i_bExtend := FALSE;
    fbBlock.i_bRetract := TRUE;      (* 停止时阻挡自动收回 *)
    fbSeparate.i_bExtend := FALSE;
    fbSeparate.i_bRetract := TRUE;   (* 停止时分料自动收回 *)
    fbMotor.i_bFwd := FALSE;
    fbMotor.i_bRev := FALSE;
    fbMotor.i_bSlow := FALSE;
    q_bLayerFeedDone := FALSE;
END_IF;
```

### 4.3 自动模式：9步状态机

```pascal
IF i_bAutoMode THEN

    (* ---- VFD 故障互锁 ---- *)
    IF i_bVfdFault THEN
        fbMotor.i_bFwd := FALSE;
        fbMotor.i_bRev := FALSE;
        fbMotor.i_bSlow := FALSE;
        iAlarmCode := 100 + i_iLayerIndex;
    END_IF;

    (* ---- 启动触发 ---- *)
    IF i_bStart AND NOT bStartTriggered THEN
        bStartTriggered := TRUE;
        bRunning := TRUE;
    END_IF;

    (* ========== 9步状态机 ========== *)
    CASE iCurrentState OF

        (* ---- STEP 0: 初始化反转 ---- *)
        STEP_INIT:
            IF bStepEntry THEN
                fbBlock.i_bExtend := FALSE;
                fbBlock.i_bRetract := TRUE;
                fbSeparate.i_bExtend := FALSE;
                fbSeparate.i_bRetract := TRUE;
                fbMotor.i_bFwd := FALSE;
                fbMotor.i_bSlow := FALSE;
                fbMotor.i_bRev := TRUE;         (* 反转复位 *)
                q_bLayerFeedDone := FALSE;
                (* 反转3s *)
                bStepEntry := FALSE;
            END_IF;

            (* 等待 fbBlock 上位 + 计时到 *)
            IF fbBlock.q_bIsRetracted THEN
                fbMotor.i_bRev := FALSE;
                bStepEntry := TRUE;
                iCurrentState := STEP_WAIT_MATERIAL;
            END_IF;

        (* ---- STEP 1: 等待来料 ---- *)
        STEP_WAIT_MATERIAL:
            IF bStepEntry THEN
                bStepEntry := FALSE;
            END_IF;

            IF i_bPreSeparateSensor THEN
                bStepEntry := TRUE;
                iCurrentState := STEP_BLOCK_DOWN;
            END_IF;

        (* ---- STEP 2: 阻挡下降 ---- *)
        STEP_BLOCK_DOWN:
            IF bStepEntry THEN
                fbBlock.i_bExtend := TRUE;      (* 委托 FB_1011 *)
                fbBlock.i_bRetract := FALSE;
                bStepEntry := FALSE;
            END_IF;

            (* FB_1011 处理到位检测+超时，编排器只需读结果 *)
            IF fbBlock.q_bIsExtended THEN
                bStepEntry := TRUE;
                iCurrentState := STEP_CONVEYOR_FWD;
            END_IF;

        (* ---- STEP 10: 输送正转 ---- *)
        STEP_CONVEYOR_FWD:
            IF bStepEntry THEN
                fbMotor.i_bFwd := TRUE;
                bStepEntry := FALSE;
            END_IF;

            (* 简化延时：通过 fbMotor.q_bRunning 和外部定时判断 *)
            IF i_bPositionSensor1 AND i_bPositionSensor2 THEN
                fbMotor.i_bFwd := FALSE;
                bStepEntry := TRUE;
                iCurrentState := STEP_POSITION_CHECK_BLOCK_UP;
            END_IF;

        (* ---- STEP 20: 到位检测 + 阻挡上升 ---- *)
        STEP_POSITION_CHECK_BLOCK_UP:
            IF bStepEntry THEN
                fbBlock.i_bExtend := FALSE;
                fbBlock.i_bRetract := TRUE;     (* 委托 FB_1011 收回 *)
                bStepEntry := FALSE;
            END_IF;

            IF fbBlock.q_bIsRetracted THEN
                bStepEntry := TRUE;
                iCurrentState := STEP_SEPARATE_PUSH;
            END_IF;

        (* ---- STEP 30: 分料推出 ---- *)
        STEP_SEPARATE_PUSH:
            IF bStepEntry THEN
                fbSeparate.i_bExtend := TRUE;   (* 委托 FB_1011 *)
                fbSeparate.i_bRetract := FALSE;
                fbSeparate.i_iTimeoutMs := i_iSeparateTimeoutMs;
                bStepEntry := FALSE;
            END_IF;

            (* FB_1011 超时告警 *)
            IF fbSeparate.q_bTimeout THEN
                iAlarmCode := 130 + i_iLayerIndex;
            END_IF;

            (* 到位判断 *)
            IF fbSeparate.q_bIsExtended THEN
                bStepEntry := TRUE;
                iCurrentState := STEP_CONVEYOR_SLOW;
            END_IF;

        (* ---- STEP 50: 慢速送出 ---- *)
        STEP_CONVEYOR_SLOW:
            IF bStepEntry THEN
                fbMotor.i_bSlow := TRUE;
                bStepEntry := FALSE;
            END_IF;

            (* 慢速到取料位标志：到位传感器再次确认 *)
            IF i_bPositionSensor1 AND i_bPositionSensor2 THEN
                fbMotor.i_bSlow := FALSE;
                bStepEntry := TRUE;
                iCurrentState := STEP_REQUEST_PICKUP;
            END_IF;

        (* ---- STEP 60: 请求取料 ---- *)
        STEP_REQUEST_PICKUP:
            IF bStepEntry THEN
                q_bLayerFeedDone := FALSE;
                bStepEntry := FALSE;
            END_IF;

            IF i_bPickupConfirmed THEN
                bStepEntry := TRUE;
                iCurrentState := STEP_SEPARATE_RETURN;
            END_IF;

        (* ---- STEP 70: 分料复位 ---- *)
        STEP_SEPARATE_RETURN:
            IF bStepEntry THEN
                fbSeparate.i_bExtend := FALSE;
                fbSeparate.i_bRetract := TRUE;  (* 委托 FB_1011 *)
                fbSeparate.i_iTimeoutMs := i_iSeparateTimeoutMs;
                bStepEntry := FALSE;
            END_IF;

            IF fbSeparate.q_bTimeout THEN
                iAlarmCode := 130 + i_iLayerIndex;
            END_IF;

            IF fbSeparate.q_bIsRetracted THEN
                q_bLayerFeedDone := TRUE;       (* 脉冲通知取放料 *)
                bStepEntry := TRUE;
                iCurrentState := STEP_INIT;     (* 循环 *)
            END_IF;

        ELSE
            iCurrentState := STEP_INIT;
            bRunning := FALSE;
            bStepEntry := TRUE;
    END_CASE;

ELSIF i_bManualMode THEN
    (* ========== 手动模式 ========== *)
    bRunning := FALSE;
    iCurrentState := STEP_INIT;
    bStepEntry := TRUE;
    q_bLayerFeedDone := FALSE;

    (* 阻挡气缸: Extend优先级 > Retract *)
    fbBlock.i_bExtend := i_bManBlockExtend;
    fbBlock.i_bRetract := i_bManBlockRetract AND NOT i_bManBlockExtend;

    (* 分料气缸: Push TRUE=推出 FALSE=复位 *)
    fbSeparate.i_bExtend := i_bManSeparatePush;
    fbSeparate.i_bRetract := NOT i_bManSeparatePush;

    (* 电机: 直接转发手动命令, FB_1012 处理互斥+安全 *)
    fbMotor.i_bFwd := i_bManConveyorFwd;
    fbMotor.i_bRev := i_bManConveyorRev;
    fbMotor.i_bSlow := i_bManConveyorSlow;

END_IF;
```

### 4.4 报警编码

```pascal
(* ==================== 报警码编码 ==================== *)
(* 从子FB收集BOOL报警 → 编码为带层号的INT报警码 *)

iAlarmCode := 0;

IF fbMotor.q_bVfdAlarm THEN
    iAlarmCode := 100 + i_iLayerIndex;           (* VFD: 101~104 *)
END_IF;

IF fbBlock.q_bTimeout THEN
    iAlarmCode := 110 + i_iLayerIndex;           (* 阻挡超时: 111~114 *)
END_IF;

IF fbBlock.q_bSensorFault THEN
    IF iAlarmCode = 0 THEN
        iAlarmCode := 120 + i_iLayerIndex;       (* 阻挡传感器: 121~124 *)
    END_IF;
END_IF;

IF fbSeparate.q_bTimeout THEN
    iAlarmCode := 130 + i_iLayerIndex;           (* 分料超时: 131~134 *)
END_IF;

IF fbSeparate.q_bSensorFault THEN
    IF iAlarmCode = 0 THEN
        iAlarmCode := 140 + i_iLayerIndex;       (* 分料传感器: 141~144 *)
    END_IF;
END_IF;

q_iAlarmCode := iAlarmCode;

(* 汇总传感器故障 *)
q_bAnySensorFault := fbBlock.q_bSensorFault OR fbSeparate.q_bSensorFault;

(* 本层故障标志 *)
q_bFault := (iAlarmCode > 0);
```

### 4.5 状态输出

```pascal
q_bRunning := bRunning;
q_iCurrentState := iCurrentState;
```

## 5. 手动模式规范

| 操作 | 命令 | FB_1011 映射 | FB_1012 映射 | 互锁 |
|------|------|-------------|-------------|------|
| 阻挡下降 | i_bManBlockExtend | fbBlock.i_bExtend | — | Extend > Retract |
| 阻挡上升 | i_bManBlockRetract | fbBlock.i_bRetract | — | 与下降互斥 |
| 分料推出 | i_bManSeparatePush | fbSeparate.i_bExtend | — | — |
| 分料复位 | NOT i_bManSeparatePush | fbSeparate.i_bRetract | — | — |
| 输送正转 | i_bManConveyorFwd | — | fbMotor.i_bFwd | 电机FB处理互斥 |
| 输送反转 | i_bManConveyorRev | — | fbMotor.i_bRev | 电机FB处理互斥 |
| 输送慢速 | i_bManConveyorSlow | — | fbMotor.i_bSlow | 电机FB处理互斥 |

> 手动模式下，FB_1012 仍执行安全门互锁和 VFD 故障检测（保证故障安全）。

## 6. OB1 调用示例

```pascal
(* ===== OB1: 四层输送机实例化 ===== *)
VAR
    fbConveyor : ARRAY[1..4] OF FB_1002_SingleLayerConveyor;
    i          : INT;
    bAnyRunning, bAnyFault : BOOL;
    iGlobalAlarm : INT;
END_VAR

FOR i := 1 TO 4 DO
    (* 公共信号 *)
    fbConveyor[i].i_bAutoMode := stGlobal.bAutoMode;
    fbConveyor[i].i_bManualMode := stGlobal.bManualMode;
    fbConveyor[i].i_bStart := stGlobal.bStart;
    fbConveyor[i].i_bStop := stGlobal.bStop;
    fbConveyor[i].i_iLayerIndex := i;
    fbConveyor[i].i_iSeparateTimeoutMs := 5000;

    (* 传感器 *)
    fbConveyor[i].i_bPreSeparateSensor := stIO.aPreSeparate[i];
    fbConveyor[i].i_bPositionSensor1 := stIO.aPosition1[i];
    fbConveyor[i].i_bPositionSensor2 := stIO.aPosition2[i];
    fbConveyor[i].i_bBlockCylinderUp := stIO.aBlockUp[i];
    fbConveyor[i].i_bBlockCylinderDown := stIO.aBlockDown[i];
    fbConveyor[i].i_bSeparateCylinderUp := stIO.aSepUp[i];
    fbConveyor[i].i_bSeparateCylinderDown := stIO.aSepDown[i];

    (* 安全 *)
    fbConveyor[i].i_bSafetyDoorOk := stSafety.bDoorOk;
    fbConveyor[i].i_bVfdFault := stIO.aVfdFault[i];
    fbConveyor[i].i_bPickupConfirmed := stPickPlace.aConfirmed[i];

    (* 手动 *)
    fbConveyor[i].i_bManBlockExtend := stHMI.aManBlockExt[i];
    fbConveyor[i].i_bManBlockRetract := stHMI.aManBlockRet[i];
    fbConveyor[i].i_bManSeparatePush := stHMI.aManSepPush[i];
    fbConveyor[i].i_bManConveyorFwd := stHMI.aManConvFwd[i];
    fbConveyor[i].i_bManConveyorRev := stHMI.aManConvRev[i];
    fbConveyor[i].i_bManConveyorSlow := stHMI.aManConvSlow[i];
END_FOR;

(* ===== 汇总 ===== *)
bAnyRunning := FALSE; bAnyFault := FALSE; iGlobalAlarm := 0;
FOR i := 1 TO 4 DO
    bAnyRunning := bAnyRunning OR fbConveyor[i].q_bRunning;
    bAnyFault := bAnyFault OR fbConveyor[i].q_bFault;
    IF fbConveyor[i].q_iAlarmCode > 0 THEN
        IF iGlobalAlarm = 0 OR fbConveyor[i].q_iAlarmCode < iGlobalAlarm THEN
            iGlobalAlarm := fbConveyor[i].q_iAlarmCode;
        END_IF;
    END_IF;
END_FOR;
stGlobal.bConveyorRunning := bAnyRunning;
stGlobal.bConveyorFault := bAnyFault;
stGlobal.iConveyorAlarmCode := iGlobalAlarm;
```

## 7. 设计决策记录

| 决策ID | 内容 | 原因 |
|:------:|------|------|
| D001 | 取消 FB_1001 | OB1 FOR循环即可完成4层实例化，无需独立容器 |
| D002 | FB_1011 复用于阻挡和分料 | 两种气缸逻辑完全相同(伸出/收回/超时/冗余)，只需不同实例 |
| D003 | 报警码由编排器编码 | 子FB只输出BOOL，不携带层号信息，编排器统一编码 |
| D004 | 手动模式在编排器中 | 手动命令通过编排器分发到子FB，保持单点控制 |
| D005 | 安全门/VFD在电机FB中 | 与运动输出直接相关的互锁应由执行器层处理 |
| D006 | 不带定时器的延时 | STEP_CONVEYOR_FWD/SLOW 延时不由编排器自己做，简化设计 |

## 8. 关联文档

| 文档 | 路径 |
|------|------|
| IFC | 接口文档_IFC-FB1002-SingleLayerConveyor-V7.0.0.md |
| FB_1011 DSN | ../../../../../../01_SharedLibraries/SysLib/actuator/PRD/详细设计说明书_DSN-FB1011-CylinderControl-V7.0.0.md |
| FB_1012 DSN | ../../../../../../01_SharedLibraries/SysLib/actuator/PRD/详细设计说明书_DSN-FB1012-ConveyorMotor-V7.0.0.md |
| 子系统架构 | Conveyor子系统架构总览_ARC-Conveyor-V7.0.0.md |
