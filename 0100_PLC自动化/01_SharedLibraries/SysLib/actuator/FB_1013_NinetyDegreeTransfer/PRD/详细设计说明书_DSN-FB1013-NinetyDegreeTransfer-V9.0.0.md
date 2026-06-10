# 详细设计说明书 FB_1013_NinetyDegreeTransfer

## 0. 文档基础信息

| 属性 | 值 |
|------|-----|
| **文档标题** | FB_1013 九十度转向机构详细设计 |
| **文档版本** | V9.0.0 |
| **关联源码** | actuator/FB_1013_NinetyDegreeTransfer.scl |
| **关联IFC** | 接口文档_IFC-FB1013-NinetyDegreeTransfer-V9.0.0.md |
| **编制日期** | 2026-05-29 |
| **编制人** | Trae |
| **遵循规范** | 801_DEV-V1.0.5, 905_DEV-V7.0.0, PLCopen MC Part 1 |

## 1. 设计原则

1. **13步顺序状态机(S30~S42)**：与源程序完全对应，每步单一职责(检测/动作/等待/确认)，步进条件清晰可追溯
2. **VAR_IN_OUT结构体直连**：6个执行器(ST_Cylinder x5 + ST_ConveyorMotor x1)通过引用传递，FB内部直接读写命令/状态/报警字段，消除间接信号中转，降低OB1接线复杂度
3. **超时隔离不强制复位**：各动作超时仅锁存报警输出(q_wAlarm对应位)和错误标志(q_bError)，保持当前输出不变，由编排器决定后续策略（重试/跳过/急停）
4. **断电保持(NV)支持**：关键步进上下文通过q_byNVState(BYTE)持久化，上电后可在S30_IDLE阶段选择从断点恢复或全复位
5. **手动/自动双模式**：自动模式走完整状态机；手动模式下状态机暂停，各执行器独立响应手动命令，安全互锁始终生效
6. **PLCopen标准接口**：输出q_bDone/q_bBusy/q_bErrorStatus/q_wErrorIDPLCopen四元组，与FB_2001报警管理块无缝对接
7. **V9.0精简原则**：删除冗余状态BOOL(32→3个)，报警合并为WORD类型(18→4个)，NV合并为BYTE(3→1个)，HMI/编排器可直接通过q_iCurrentStep和位访问获取设备状态

## 2. 状态定义表

### 2.1 主状态机状态

| 状态值 | 常量名 | 步骤名 | 入口动作 | 出口条件 | 出口目标 |
|:------:|--------|--------|----------|----------|----------|
| 0 | S30_IDLE | 待机等待 | 清残留/NV检查/回原点 | Start上升沿 | S31 |
| 1 | S31_FEED_CHECK | 入料检测 | 启动入料检测定时器 | 任一FeedDetect=TRUE | S32 |
| 2 | S32_LIFT_DOWN | 气缸下行 | MainCylinder.Extend:=TRUE | i_bLiftDownPos=TRUE | S33 |
| 3 | S33_PICK_DOWN | 取物下降 | PickCylinder.Extend:=TRUE | ExtendedPos=TRUE | S34 |
| 4 | S34_PICK_CLAMP | 取物夹取 | 夹取电磁阀ON+启动确认定时器 | 确认时间到+到位OK | S35 |
| 5 | S35_PICK_UP | 取物上升 | PickCylinder.Retract:=TRUE | RetractedPos=TRUE | S36 |
| 6 | S36_MOTOR_FWD | 正转90度 | RotateMotor.FwdCmd:=TRUE | i_bFwdArrived=TRUE | S37 |
| 7 | S37_PLACE_DOWN | 放物下降 | PlaceCylinder.Extend:=TRUE | ExtendedPos=TRUE | S38 |
| 8 | S38_PLACE_RELEASE | 放物释放 | 释放电磁阀ON+启动确认定时器 | 确认时间到 | S39 |
| 9 | S39_PLACE_UP | 放物上升 | PlaceCylinder.Retract:=TRUE | RetractedPos=TRUE | S40 |
| 10 | S40_MOTOR_REV | 反转90度 | RotateMotor.RevCmd:=TRUE | i_bRevArrived=TRUE | S41 |
| 11 | S41_LIFT_UP | 气缸上行 | MainCylinder.Retract:=TRUE | i_bLiftUpPos=TRUE | S42 |
| 12 | S42_CYCLE_DONE | 周期完成 | Done脉冲+Busy清零 | 脉冲结束 | S30 |

### 2.2 台面位置枚举 (q_iTablePosition)

| 值 | 含义 | 设置时机 |
|:--:|------|----------|
| 0 | 未知/待机 | S30_IDLE、复位后 |
| 1 | A位置(入料侧) | S31有料检测后、S40反转到位后 |
| 2 | AO位置(正转经过) | S36正转开始 |
| 3 | O位置(到达D侧) | S36正转到位 |
| 4 | OD位置(放物下降经过) | S37放物下降开始 |
| 5 | D位置(放料位) | S37放物下降到位 |

## 3. 详细伪代码

### 3.0 前置处理

```pascal
(* ==================== 使能关闭处理 ==================== *)
IF NOT i_bEnable THEN
    q_bOutputReset := TRUE;
    (* 全部驱动输出清零 *)
    q_bCylinderUp..q_bMotorRev := FALSE;

    (* 状态清零 *)
    q_bPickDone := FALSE;  q_bPlaceDone := FALSE;
    q_iTablePosition := 0;

    (* 报警清零: WORD整体赋值 *)
    q_wAlarm := 0;  q_wErrorClass := 0;
    q_wErrorID := 0;  q_bError := FALSE;

    (* PLCopen输出清零 *)
    q_bDone := FALSE;  q_bBusy := FALSE;
    q_bErrorStatus := FALSE;  q_wErrorIDPLCopen := 0;
    q_iCurrentStep := 0;

    (* NV清零 *)
    q_byNVState := 0;

    (* 内部状态清零 *)
    bRunning := FALSE;  iCurrentStep := 0;  bStepEntry := FALSE;

    (* 12个定时器复位 *)
    tFeedTimeout.IN := FALSE; ... tDonePulse.IN := FALSE;

    (* 6个结构体命令清除 *)
    io_stMainCylinder.Extend := FALSE; ... io_stRotateMotor.SlowCmd := FALSE;
    RETURN;
END_IF;

(* ==================== 复位处理 ==================== *)
IF i_bReset THEN
    (* 同使能关闭的全面清零逻辑 + q_byNVState := 0 *)
    RETURN;
END_IF;

(* ==================== 停止处理 ==================== *)
IF i_bStop THEN
    (* 所有气缸/电机命令立即清除 *)
    (* NV记录: q_byNVState.%X0 := bRunning; .%X1 := (iCurrentStep>0); .%X2 := q_bError *)
    bRunning := FALSE;  q_bBusy := FALSE;
END_IF;
```

### 3.1 模式分发

```pascal
IF i_bAutoMode THEN
    CASE iCurrentStep OF
        0: (* S30_IDLE *)
        1: (* S31_FEED_CHECK *)
        ...
        12: (* S42_CYCLE_DONE *)
    END_CASE;

ELSIF i_bManualMode THEN
    (* 手动模式: 直接映射按钮 -> ST_Cylinder/ST_ConveyorMotor *)
    io_stMainCylinder.Extend := q_bCylinderDown;
    io_stMainCylinder.Retract := q_bCylinderUp;
    ...
END_IF;
```

### 3.2 S30_IDLE -- 待机等待

```pascal
S30_IDLE:  (* 0 - 待机等待 *)
    (* 清除步完成标志 *)
    q_bPickDone := FALSE;
    q_bPlaceDone := FALSE;
    q_iTablePosition := 0;

    (* NV恢复检查 *)
    IF q_byNVState.%X0 OR q_byNVState.%X1 THEN
        q_byNVState.%X0 := FALSE;
        q_byNVState.%X1 := FALSE;
    END_IF;

    (* 安全回原点检查 *)
    IF NOT i_bLiftUpPos THEN
        io_stMainCylinder.Retract := TRUE;
    END_IF;

    (* VFD/安全门预检 *)
    IF io_stRotateMotor.VfdFault THEN
        q_bError := TRUE;  q_wErrorID := 143;
        q_wAlarm.%X13 := TRUE;  q_wErrorClass.%X2 := TRUE;
    END_IF;
    IF NOT io_stRotateMotor.SafetyDoorOk THEN
        q_bError := TRUE;  q_wErrorID := 142;
        q_wAlarm.%X12 := TRUE;  q_wErrorClass.%X4 := TRUE;
    END_IF;

    (* 启动触发 *)
    IF bStartTriggered AND NOT bRunning THEN
        bRunning := TRUE;  q_bBusy := TRUE;
        bStepEntry := TRUE;
        iCurrentStep := S31_FEED_CHECK;
    END_IF;
```

### 3.3 S31_FEED_CHECK -- 入料检测

```pascal
S31_FEED_CHECK:  (* 1 - 入料检测 *)
    IF bStepEntry THEN
        tFeedTimeout.IN := TRUE;
        tFeedTimeout.PT := INT_TO_DINT(i_iFeedTimeoutMs);
        bStepEntry := FALSE;
    END_IF;

    (* 5路入料传感器任一检测到物料 *)
    IF i_bFeedDetect0 OR i_bFeedDetect1 OR i_bFeedDetect2
       OR i_bFeedDetect3 OR i_bFeedDetect4 THEN
        tFeedTimeout.IN := FALSE;
        q_iTablePosition := 1;  (* A位置 *)
        bStepEntry := TRUE;
        iCurrentStep := S32_LIFT_DOWN;

    (* 超时 -> Alarm140 *)
    ELSIF tFeedTimeout.Q THEN
        q_wAlarm.%X10 := TRUE;  q_wErrorClass.%X4 := TRUE;
        q_bError := TRUE;  q_wErrorID := 140;
        tFeedTimeout.IN := FALSE;
    END_IF;
```

### 3.4 S32_LIFT_DOWN -- 气缸下行

```pascal
S32_LIFT_DOWN:  (* 2 - 升降气缸下降到工作位 *)
    IF bStepEntry THEN
        io_stMainCylinder.Extend := TRUE;
        io_stMainCylinder.Retract := FALSE;
        q_bCylinderDown := TRUE;  q_bCylinderUp := FALSE;
        tLiftDownTimeout.IN := TRUE;
        tLiftDownTimeout.PT := INT_TO_DINT(i_iLiftTimeoutMs);
        bStepEntry := FALSE;
    END_IF;

    IF i_bLiftDownPos THEN
        tLiftDownTimeout.IN := FALSE;
        io_stMainCylinder.IsExtended := TRUE;
        bStepEntry := TRUE;
        iCurrentStep := S33_PICK_DOWN;

    ELSIF tLiftDownTimeout.Q THEN
        q_wAlarm.%X0 := TRUE;  q_wErrorClass.%X0 := TRUE;
        q_bError := TRUE;  q_wErrorID := 130;
        tLiftDownTimeout.IN := FALSE;
        io_stMainCylinder.Timeout := TRUE;
    END_IF;
```

### 3.5 S33_PICK_DOWN -- 取物下降

```pascal
S33_PICK_DOWN:  (* 3 - 取物机构下降 *)
    IF bStepEntry THEN
        io_stPickCylinder.Extend := TRUE;
        q_bPickDown := TRUE;  q_bPickUp := FALSE;
        tPickDownTimeout.IN := TRUE;
        tPickDownTimeout.PT := INT_TO_DINT(i_iPickTimeoutMs);
        bStepEntry := FALSE;
    END_IF;

    IF io_stPickCylinder.ExtendedPos THEN
        tPickDownTimeout.IN := FALSE;
        io_stPickCylinder.IsExtended := TRUE;
        bStepEntry := TRUE;
        iCurrentStep := S34_PICK_CLAMP;

    ELSIF tPickDownTimeout.Q THEN
        q_wAlarm.%X2 := TRUE;  q_wErrorClass.%X1 := TRUE;
        q_bError := TRUE;  q_wErrorID := 132;
        tPickDownTimeout.IN := FALSE;
    END_IF;
```

### 3.6 S34_PICK_CLAMP -- 取物夹取

```pascal
S34_PICK_CLAMP:  (* 4 - 夹取物料+确认 *)
    IF bStepEntry THEN
        (* 摆臂下降 + 推板下降 = 夹取动作 *)
        io_stSwingArmCyl.Extend := TRUE;
        io_stPushPlateCyl.Extend := TRUE;
        q_bSwingArmDown := TRUE;  q_bPushPlateDown := TRUE;
        tClampPickConfirm.IN := TRUE;
        tClampPickConfirm.PT := INT_TO_DINT(i_iClampConfirmMs);
        bStepEntry := FALSE;
    END_IF;

    IF tClampPickConfirm.Q AND i_bPickPlaceDone THEN
        q_bPickDone := TRUE;
        tClampPickConfirm.IN := FALSE;
        bStepEntry := TRUE;
        iCurrentStep := S35_PICK_UP;

    (* 夹取确认失败 -> Alarm134 *)
    IF tClampPickConfirm.Q AND NOT i_bPickPlaceDone THEN
        q_wAlarm.%X4 := TRUE;  q_wErrorClass.%X1 := TRUE;
        q_bError := TRUE;  q_wErrorID := 134;
        tClampPickConfirm.IN := FALSE;
    END_IF;
```

### 3.7 S35_PICK_UP -- 取物上升

```pascal
S35_PICK_UP:  (* 5 - 取物机构上升收回 *)
    IF bStepEntry THEN
        io_stPickCylinder.Retract := TRUE;
        q_bPickUp := TRUE;  q_bPickDown := FALSE;
        (* 保持夹取状态 *)
        q_bSwingArmDown := TRUE;  q_bPushPlateDown := TRUE;
        tPickUpTimeout.IN := TRUE;
        tPickUpTimeout.PT := INT_TO_DINT(i_iPickTimeoutMs);
        bStepEntry := FALSE;
    END_IF;

    IF io_stPickCylinder.RetractedPos THEN
        tPickUpTimeout.IN := FALSE;
        io_stPickCylinder.IsRetracted := TRUE;
        bStepEntry := TRUE;
        iCurrentStep := S36_MOTOR_FWD;

    ELSIF tPickUpTimeout.Q THEN
        q_wAlarm.%X3 := TRUE;  q_wErrorClass.%X1 := TRUE;
        q_bError := TRUE;  q_wErrorID := 133;
        tPickUpTimeout.IN := FALSE;
    END_IF;
```

### 3.8 S36_MOTOR_FWD -- 电机正转90度

```pascal
S36_MOTOR_FWD:  (* 6 - 旋转电机正向90度(A位置→D位置) *)
    IF bStepEntry THEN
        (* VFD/安全门预检 *)
        IF io_stRotateMotor.VfdFault THEN
            q_wAlarm.%X13 := TRUE;  q_wErrorClass.%X2 := TRUE;
            q_bError := TRUE;  q_wErrorID := 143;  RETURN;
        END_IF;
        IF NOT io_stRotateMotor.SafetyDoorOk THEN
            q_wAlarm.%X12 := TRUE;  q_wErrorClass.%X4 := TRUE;
            q_bError := TRUE;  q_wErrorID := 142;  RETURN;
        END_IF;

        io_stRotateMotor.FwdCmd := TRUE;
        q_bMotorFwd := TRUE;  q_bMotorRev := FALSE;
        q_iTablePosition := 2;  (* AO位置 *)
        tMotorFwdTimeout.IN := TRUE;
        tMotorFwdTimeout.PT := INT_TO_DINT(i_iMotorTimeoutMs);
        bStepEntry := FALSE;
    END_IF;

    IF i_bFwdArrived THEN
        q_iTablePosition := 3;  (* O位置 *)
        io_stRotateMotor.FwdCmd := FALSE;  q_bMotorFwd := FALSE;
        tMotorFwdTimeout.IN := FALSE;
        bStepEntry := TRUE;
        iCurrentStep := S37_PLACE_DOWN;

    ELSIF tMotorFwdTimeout.Q THEN
        q_wAlarm.%X5 := TRUE;  q_wErrorClass.%X2 := TRUE;
        q_bError := TRUE;  q_wErrorID := 135;
        io_stRotateMotor.FwdCmd := FALSE;  q_bMotorFwd := FALSE;
        tMotorFwdTimeout.IN := FALSE;
    END_IF;
```

### 3.9 S37_PLACE_DOWN -- 放物下降

```pascal
S37_PLACE_DOWN:  (* 7 - 放物机构下降 *)
    IF bStepEntry THEN
        io_stPlaceCylinder.Extend := TRUE;
        q_bPlaceDown := TRUE;  q_bPlaceUp := FALSE;
        q_iTablePosition := 4;  (* OD位置 *)
        tPlaceDownTimeout.IN := TRUE;
        tPlaceDownTimeout.PT := INT_TO_DINT(i_iPlaceTimeoutMs);
        bStepEntry := FALSE;
    END_IF;

    IF io_stPlaceCylinder.ExtendedPos THEN
        io_stPlaceCylinder.IsExtended := TRUE;
        q_iTablePosition := 5;  (* D位置 *)
        tPlaceDownTimeout.IN := FALSE;
        bStepEntry := TRUE;
        iCurrentStep := S38_PLACE_RELEASE;

    ELSIF tPlaceDownTimeout.Q THEN
        q_wAlarm.%X7 := TRUE;  q_wErrorClass.%X3 := TRUE;
        q_bError := TRUE;  q_wErrorID := 137;
        tPlaceDownTimeout.IN := FALSE;
    END_IF;
```

### 3.10 S38_PLACE_RELEASE -- 放物释放

```pascal
S38_PLACE_RELEASE:  (* 8 - 释放物料+确认 *)
    IF bStepEntry THEN
        (* 摆臂上升 + 推板上升 = 释放动作 *)
        io_stSwingArmCyl.Retract := TRUE;
        io_stPushPlateCyl.Retract := TRUE;
        q_bSwingArmDown := FALSE;  q_bPushPlateUp := TRUE;
        tClampPlaceConfirm.IN := TRUE;
        tClampPlaceConfirm.PT := INT_TO_DINT(i_iClampConfirmMs);
        bStepEntry := FALSE;
    END_IF;

    IF tClampPlaceConfirm.Q THEN
        q_bPlaceDone := TRUE;
        tClampPlaceConfirm.IN := FALSE;
        bStepEntry := TRUE;
        iCurrentStep := S39_PLACE_UP;
    END_IF;
```

### 3.11 S39_PLACE_UP -- 放物上升

```pascal
S39_PLACE_UP:  (* 9 - 放物机构上升收回 *)
    IF bStepEntry THEN
        io_stPlaceCylinder.Retract := TRUE;
        q_bPlaceUp := TRUE;  q_bPlaceDown := FALSE;
        tPlaceUpTimeout.IN := TRUE;
        tPlaceUpTimeout.PT := INT_TO_DINT(i_iPlaceTimeoutMs);
        bStepEntry := FALSE;
    END_IF;

    IF io_stPlaceCylinder.RetractedPos THEN
        io_stPlaceCylinder.IsRetracted := TRUE;
        tPlaceUpTimeout.IN := FALSE;
        bStepEntry := TRUE;
        iCurrentStep := S40_MOTOR_REV;

    ELSIF tPlaceUpTimeout.Q THEN
        q_wAlarm.%X8 := TRUE;  q_wErrorClass.%X3 := TRUE;
        q_bError := TRUE;  q_wErrorID := 138;
        tPlaceUpTimeout.IN := FALSE;
    END_IF;
```

### 3.12 S40_MOTOR_REV -- 电机反转90度

```pascal
S40_MOTOR_REV:  (* 10 - 旋转电机反向90度(D位置→A位置回原位) *)
    IF bStepEntry THEN
        (* VFD/安全门预检 — 与S36相同 *)
        IF io_stRotateMotor.VfdFault THEN ... END_IF;
        IF NOT io_stRotateMotor.SafetyDoorOk THEN ... END_IF;

        io_stRotateMotor.RevCmd := TRUE;
        q_bMotorRev := TRUE;  q_bMotorFwd := FALSE;
        tMotorRevTimeout.IN := TRUE;
        tMotorRevTimeout.PT := INT_TO_DINT(i_iMotorTimeoutMs);
        bStepEntry := FALSE;
    END_IF;

    IF i_bRevArrived THEN
        q_iTablePosition := 1;  (* A位置 *)
        io_stRotateMotor.RevCmd := FALSE;  q_bMotorRev := FALSE;
        tMotorRevTimeout.IN := FALSE;
        bStepEntry := TRUE;
        iCurrentStep := S41_LIFT_UP;

    ELSIF tMotorRevTimeout.Q THEN
        q_wAlarm.%X6 := TRUE;  q_wErrorClass.%X2 := TRUE;
        q_bError := TRUE;  q_wErrorID := 136;
        io_stRotateMotor.RevCmd := FALSE;  q_bMotorRev := FALSE;
        tMotorRevTimeout.IN := FALSE;
    END_IF;
```

### 3.13 S41_LIFT_UP -- 气缸上行

```pascal
S41_LIFT_UP:  (* 11 - 升降气缸上升到待机位 *)
    IF bStepEntry THEN
        io_stMainCylinder.Retract := TRUE;
        q_bCylinderUp := TRUE;  q_bCylinderDown := FALSE;
        tLiftUpTimeout.IN := TRUE;
        tLiftUpTimeout.PT := INT_TO_DINT(i_iLiftTimeoutMs);
        bStepEntry := FALSE;
    END_IF;

    IF i_bLiftUpPos THEN
        io_stMainCylinder.IsRetracted := TRUE;
        tLiftUpTimeout.IN := FALSE;
        bStepEntry := TRUE;
        iCurrentStep := S42_CYCLE_DONE;

    ELSIF tLiftUpTimeout.Q THEN
        q_wAlarm.%X1 := TRUE;  q_wErrorClass.%X0 := TRUE;
        q_bError := TRUE;  q_wErrorID := 131;
        tLiftUpTimeout.IN := FALSE;
    END_IF;
```

### 3.14 S42_CYCLE_DONE -- 周期完成

```pascal
S42_CYCLE_DONE:  (* 12 - 周期完成, 输出Done脉冲 *)
    IF bStepEntry THEN
        tDonePulse.IN := TRUE;
        tDonePulse.PT := INT_TO_DINT(i_iCycleDonePulseMs);

        q_bDone := TRUE;
        q_bBusy := FALSE;
        bRunning := FALSE;

        (* 清除断电保持 *)
        q_byNVState := 0;
        bStepEntry := FALSE;
    END_IF;

    IF tDonePulse.Q THEN
        q_bDone := FALSE;
        tDonePulse.IN := FALSE;
        iCurrentStep := S30_IDLE;
        bStepEntry := TRUE;
    END_IF;
```

### 3.15 后处理

```pascal
(* === 逐个调用12个FB_TON定时器实例 === *)
tFeedTimeout(IN := ..., Q => ...);
tLiftDownTimeout(...);
... (* 12个定时器调用 *)

(* === Start上升沿检测 === *)
bStartTriggered := i_bStart AND NOT i_bStartLast;
i_bStartLast := i_bStart;

(* === 传感器冗余一致性检查 === *)
IF i_bLiftUpPos AND i_bLiftDownPos THEN
    q_wAlarm.%X11 := TRUE;  q_wErrorClass.%X4 := TRUE;
    q_bError := TRUE;  q_wErrorID := 141;
END_IF;
(* 取物/放物/正反转传感器冲突同理 *)

(* === PLCopen输出同步 === *)
q_bBusy := bRunning AND (iCurrentStep > 0 AND iCurrentStep < 12);
q_bErrorStatus := q_bError;
q_wErrorIDPLCopen := q_wErrorID;

(* === 结构体参数同步到物理输出(双重映射) === *)
q_bCylinderUp := io_stMainCylinder.Retract;
q_bCylinderDown := io_stMainCylinder.Extend;
... (* 各气缸/电机同步 *)
```

## 4. 时序图

### 4.1 正常完整周期 (S30 -> S42)

```
时间轴 →

Start          ────┐                                       ┌─────>
                   └───────────────────────────────────────┘

q_bBusy         ────┐                                     │
                   └─────────────────────────────────────┘

步序(S30~S42)   S30  S31  S32  S33  S34  S35  S36  S37  S38  S39  S40  S41  S42  S30
                 │    │    │    │    │    │    │    │    │    │    │    │    │    │

q_iTablePosition  0    1    1    1    1    1    2    4    5    5    5    1    1    0
                                          →    →3   →5

q_bPickDone                             ┌┐                    │
                                        └┘──────────────────────>

q_bPlaceDone                                          ┌┐          │
                                                      └┘──────────>

q_bDone                                                                                  ┌┐
                                                                                         └┘
```

### 4.2 超时场景 (S32气缸下行超时)

```
时间轴 →

S32进入         ─────────────────────────────────────────> (停在S32)

q_wAlarm        ─────────────────────────┐
                                    %X0 ──┘─────────── (bit0=130锁存)

q_bError        ─────────────────────────┐
                                    └─────── ... (锁存)

q_wErrorID      ─────────────────────────┐
                                    └─────── = 130

步序             S32 ────────────────────────────────────── S32 (不跳步)
```

## 5. 报警码完整映射表 (V9.0 WORD格式)

| 码 | 含义 | Alarm位 | ErrorClass位 | 触发步骤 | 触发条件 | 恢复方式 |
|:--:|------|:-------:|:-----------:|:-------:|----------|---------|
| 130 | 升降气缸下行超时 | %X0 | %X0(主升降) | S32 | tLiftDownTimeout.Q | Reset/手动排除 |
| 131 | 升降气缸上行超时 | %X1 | %X0(主升降) | S41 | tLiftUpTimeout.Q | Reset/手动排除 |
| 132 | 取物机构下降超时 | %X2 | %X1(取物) | S33 | tPickDownTimeout.Q | Reset/手动排除 |
| 133 | 取物机构上升超时 | %X3 | %X1(取物) | S35 | tPickUpTimeout.Q | Reset/手动排除 |
| 134 | 取物夹取失败/超时 | %X4 | %X1(取物) | S34 | 确认时间到+无确认 | Reset/检查夹具 |
| 135 | 电机正转90度超时 | %X5 | %X2(电机) | S36 | tMotorFwdTimeout.Q | Reset/检查电机 |
| 136 | 电机反转90度超时 | %X6 | %X2(电机) | S40 | tMotorRevTimeout.Q | Reset/检查电机 |
| 137 | 放物机构下降超时 | %X7 | %X3(放物) | S37 | tPlaceDownTimeout.Q | Reset/手动排除 |
| 138 | 放物机构上升超时 | %X8 | %X3(放物) | S39 | tPlaceUpTimeout.Q | Reset/手动排除 |
| 139 | 放物释放失败/超时 | %X9 | %X3(放物) | S38 | 确认时间到+无确认 | Reset/检查放具 |
| 140 | 入料检测无料/超时 | %X10 | %X4(安全/入料) | S31 | tFeedTimeout.Q | 来料后自动/Reset |
| 141 | 传感器冲突 | %X11 | %X4(安全/入料) | 任意 | 上下位同时ON | 检修传感器 |
| 142 | 安全门未关闭 | %X12 | %X4(安全/入料) | S30/S36/S40 | SafetyDoorOk=FALSE | 关安全门/复位 |
| 143 | 电机/VFD故障 | %X13 | %X2(电机) | S30/S36/S40 | VfdFault=TRUE | 检修VFD/电机 |

> **HMI/编排器访问方式**：
> - 检查单个报警: `q_wAlarm.%X0` (报警130)
> - 检查某类报警: `q_wErrorClass.%X1` (取物机构类)
> - 获取错误码: `q_wErrorID` (130~143)
> - 错误汇总: `q_bError`

## 6. 变量定义详情

### 6.1 VAR (内部变量)

| 变量 | 类型 | 初始值 | 保持性 | 说明 |
|------|------|:------:|:------:|------|
| iCurrentStep | INT | 0 | 非保持 | 当前状态机步序(0~12) |
| bStepEntry | BOOL | FALSE | 非保持 | 步进入口标志(每步首扫描=TRUE) |
| bRunning | BOOL | FALSE | 非保持 | 周期运行中标志 |
| bStartTriggered | BOOL | FALSE | 非保持 | Start上升沿检测结果 |
| i_bStartLast | BOOL | FALSE | 非保持 | Start上一周期值(沿检测用) |
| tFeedTimeout | FB_TON | -- | 非保持 | S31 入料检测超时 |
| tLiftDownTimeout | FB_TON | -- | 非保持 | S32 主升降下降超时 |
| tPickDownTimeout | FB_TON | -- | 非保持 | S33 取物下降超时 |
| tClampPickConfirm | FB_TON | -- | 非保持 | S34 夹取确认等待 |
| tPickUpTimeout | FB_TON | -- | 非保持 | S35 取物上升超时 |
| tMotorFwdTimeout | FB_TON | -- | 非保持 | S36 电机正转超时 |
| tPlaceDownTimeout | FB_TON | -- | 非保持 | S37 放物下降超时 |
| tClampPlaceConfirm | FB_TON | -- | 非保持 | S38 释放确认等待 |
| tPlaceUpTimeout | FB_TON | -- | 非保持 | S39 放物上升超时 |
| tMotorRevTimeout | FB_TON | -- | 非保持 | S40 电机反转超时 |
| tLiftUpTimeout | FB_TON | -- | 非保持 | S41 主升降上升超时 |
| tDonePulse | FB_TON | -- | 非保持 | S42 Done脉冲宽度 |

### 6.2 V9.0输出变量总览

| 分类 | 变量 | 类型 | 说明 |
|------|------|------|------|
| 驱动 | q_bOutputReset | BOOL | 输出总复位 |
| 驱动 | q_bCylinderUp/Down | BOOL | 主升降方向 |
| 驱动 | q_bPickUp/Down | BOOL | 取物升降方向 |
| 驱动 | q_bPlaceUp/Down | BOOL | 放物升降方向 |
| 驱动 | q_bSwingArmDown | BOOL | 摆臂下降 |
| 驱动 | q_bPushPlateUp/Down | BOOL | 推板方向 |
| 驱动 | q_bMotorFwd/Rev | BOOL | 电机方向 |
| 状态 | q_bPickDone | BOOL | 取物完成 |
| 状态 | q_bPlaceDone | BOOL | 放物完成 |
| 状态 | q_iTablePosition | INT | 台面位置枚举(0~5) |
| 报警 | q_wAlarm | WORD | 报警位(14位) |
| 报警 | q_wErrorClass | WORD | 错误分类(5类) |
| 报警 | q_wErrorID | WORD | 当前错误编号 |
| 报警 | q_bError | BOOL | 错误汇总 |
| PLCopen | q_bDone | BOOL | 完成脉冲 |
| PLCopen | q_bBusy | BOOL | 运行中 |
| PLCopen | q_bErrorStatus | BOOL | 错误标志 |
| PLCopen | q_wErrorIDPLCopen | WORD | 错误号 |
| PLCopen | q_iCurrentStep | INT | 当前步序(0~12) |
| NV | q_byNVState | BYTE | 断电保持状态 |

### 6.3 步序常量定义

```pascal
(* 步序常量 - 对应IFC文档第2节 *)
CONSTANT
    S30_IDLE           : INT := 0;    (* 待机等待 *)
    S31_FEED_CHECK     : INT := 1;    (* 入料检测 *)
    S32_LIFT_DOWN      : INT := 2;    (* 气缸下行 *)
    S33_PICK_DOWN      : INT := 3;    (* 取物下降 *)
    S34_PICK_CLAMP     : INT := 4;    (* 取物夹取 *)
    S35_PICK_UP        : INT := 5;    (* 取物上升 *)
    S36_MOTOR_FWD      : INT := 6;    (* 电机正转90度 *)
    S37_PLACE_DOWN     : INT := 7;    (* 放物下降 *)
    S38_PLACE_RELEASE  : INT := 8;    (* 放物释放 *)
    S39_PLACE_UP       : INT := 9;    (* 放物上升 *)
    S40_MOTOR_REV      : INT := 10;   (* 电机反转90度 *)
    S41_LIFT_UP        : INT := 11;   (* 气缸上行 *)
    S42_CYCLE_DONE     : INT := 12;   (* 周期完成 *)
END_CONSTANT
```

## 7. VAR_IN_OUT 结构体使用约定

### 7.1 ST_Cylinder 字段读写权限矩阵

| 字段 | S30 | S32 | S33 | S35 | S37 | S39 | S41 | 手动 |
|------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:----:|
| .Extend (写) | 清 | W | W | - | W | - | - | W |
| .Retract (写) | 清 | - | - | W | - | W | W | W |
| .ExtendedPos (读) | R | R | R | R | R | R | R | R |
| .RetractedPos (读) | R | R | R | R | R | R | R | R |
| .TimeoutMs (写) | - | W | W | W | W | W | W | - |
| .IsExtended (写) | - | W | W | W | W | W | W | - |
| .IsRetracted (写) | - | - | - | W | - | W | W | - |
| .Timeout (读) | R | R | R | R | R | R | R | R |
| .SensorFault (读/写) | R/W | R | R | R | R | R | R | R |

### 7.2 ST_ConveyorMotor 字段读写权限矩阵

| 字段 | S30 | S36 | S40 | 手动 |
|------|:---:|:---:|:---:|:----:|
| .FwdCmd (写) | 清 | W | - | W |
| .RevCmd (写) | 清 | - | W | W |
| .SafetyDoorOk (读) | R | R | R | R |
| .VfdFault (读) | R | R | R | R |
| .Speed (读) | R | R | R | R |
| .FwdOut (读) | R | R | R | R |
| .RevOut (读) | R | R | R | R |
| .Running (读) | R | R | R | R |
| .VfdAlarm (读) | R | R | R | R |

## 8. 边界条件处理

| 场景 | 行为 |
|------|------|
| Start时已在S42(Done态) | 忽略，等Done脉冲结束后自动回到S30方可重新触发 |
| Start时报警活跃(q_bError=TRUE) | 拒绝启动，需先Reset清除报警 |
| Enable=FALSE时收到Start | 忽略启动请求 |
| S32下降时已在下位 | 立即置位，不启动超时计时，直接跳S33 |
| S41上升时已在上位 | 直接跳S42 |
| S36/S40运行中VFD故障 | 立即停电机+报警143(q_wAlarm.%X13)+回退S30 |
| S36/S40运行中安全门打开 | 立即停电机+报警142(q_wAlarm.%X12)+回退S30 |
| 运动中命令翻转(如手动切自动) | 当前步正常完成后再响应新模式 |
| 所有超时参数=0 | 关闭该类超时检测，对应Alarm永不触发 |
| 上下位传感器同时ON | SensorFault=TRUE(报警141/q_wAlarm.%X11)，步序暂停 |
| 断电后上电(NV有效) | S30_IDLE检测q_byNVState，提示操作员，不自动恢复 |
| Stop后立即Start | 从停止时的步序继续(若气缸位置合理)或要求先Reset |
| 手动模式切回自动 | 从当前iCurrentStep继续(若在S30则正常待机) |

## 9. V9.0 vs V7.0 变更要点

| V7.0 (旧) | V9.0 (新) | 说明 |
|-----------|-----------|------|
| q_bM0~q_bM10 (11 BOOL) | 删除 | q_iCurrentStep已表达步序，无需额外中间标志 |
| q_bPosA/AO/O/OD/D (5 BOOL) | q_iTablePosition (1 INT) | 合并为枚举值 0~5 |
| q_bPosA_Picker/Feeder (2 BOOL) | 删除 | 通过q_iCurrentStep与q_bPickDone/PlaceDone推导 |
| q_bFwdArrived/RevArrived (2 BOOL) | 删除 | 外部直接读i_bFwdArrived/i_bRevArrived |
| q_bCylinderAtTop/Bottom等 (4 BOOL) | 删除 | 外部直接读i_bLiftUpPos等传感器输入 |
| q_bWaitState1/TrayIn等 (6 BOOL) | 删除 | 内部信号，外部无需感知 |
| q_bA_InputHasMaterial等 (3 BOOL) | 删除 | 外部可直接读i_bFeedDetect0~4 |
| q_bAlarm0~10 (11 BOOL) | q_wAlarm (1 WORD) | 位映射: %X0=130, ..., %X13=143 |
| q_bError1~5 (5 BOOL) | q_wErrorClass (1 WORD) | 位映射: %X0=主升降, %X1=取物, ... |
| q_bNV_Retain1~3 (3 BOOL) | q_byNVState (1 BYTE) | %X0=Running, %X1=步序>0, %X2=Error |
| q_iErrorID (INT) | q_wErrorID (WORD) | 类型改为WORD |
| q_iErrorIDPLCopen (INT) | q_wErrorIDPLCopen (WORD) | 类型改为WORD |
| **VAR_OUTPUT: 70个** | **VAR_OUTPUT: 25个** | **精简45个** |

## 10. 关联文档

| 文档 | 路径 | 版本 |
|------|------|:----:|
| IFC | 接口文档_IFC-FB1013-NinetyDegreeTransfer-V9.0.0.md | V9.0.0 |
| 气缸控制 IFC | 接口文档_IFC-FB1011-CylinderControl-V7.0.0.md | V7.0.0 |
| 气缸控制 DSN | 详细设计说明书_DSN-FB1011-CylinderControl-V7.0.0.md | V7.0.0 |
| 电机控制 IFC | 接口文档_IFC-FB1012-ConveyorMotor-V7.0.0.md | V7.0.0 |
| 电机控制 DSN | 详细设计说明书_DSN-FB1012-ConveyorMotor-V7.0.0.md | V7.0.0 |
| 取放料机构 IFC | ../../../../DJ-2026-005/02_PLC程序/通用ST程序及变量表/pickplace/PRD/接口文档_IFC-FB1003-PickPlace-V7.0.0.md | V7.0.0 |
| 取放料机构 DSN | ../../../../DJ-2026-005/02_PLC程序/通用ST程序及变量表/pickplace/PRD/详细设计说明书_DSN-FB1003-PickPlace-V7.0.0.md | V7.0.0 |
| ST_Cylinder类型 | ../../types/ST_Cylinder.scl | V1.1.0 |
| ST_ConveyorMotor类型 | ../../types/ST_ConveyorMotor.scl | V1.1.0 |
| 规范801 | ../../../../../01_需求与设计/10_编程及变量规范/801_PLC变量命名与功能块命名规范_DEV.md | V1.0.5 |
| 规范905 | ../../../../../01_需求与设计/10_编程及变量规范/905_SCL编程规范_DEV.md | V7.0.0 |