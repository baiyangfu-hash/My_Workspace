# 详细设计说明书 FB_1013_NinetyDegreeTransfer

## 0. 文档基础信息

| 属性 | 值 |
|------|-----|
| **文档标题** | FB_1013 九十度转向机构详细设计 |
| **文档版本** | V7.0.0 |
| **关联源码** | actuator/FB_1013_NinetyDegreeTransfer.scl |
| **关联IFC** | 接口文档_IFC-FB1013-NinetyDegreeTransfer-V7.0.0.md |
| **编制日期** | 2026-05-29 |
| **编制人** | Trae |
| **遵循规范** | 801_DEV-V1.0.5, 905_DEV-V7.0.0, PLCopen MC Part 1 |

## 1. 设计原则

1. **13步顺序状态机(S30~S42)**：与源程序LD梯形图154网络完全对应，每步单一职责(检测/动作/等待/确认)，步进条件清晰可追溯
2. **VAR_IN_OUT结构体直连**：6个执行器(ST_Cylinder x5 + ST_ConveyorMotor x1)通过引用传递，FB内部直接读写命令/状态/报警字段，消除间接信号中转，降低OB1接线复杂度
3. **超时隔离不强制复位**：各动作超时仅锁存报警输出(q_bAlarmx)和错误标志(q_bError)，保持当前输出不变，由编排器决定后续策略（重试/跳过/急停）
4. **断电保持(NV)支持**：关键步进上下文通过q_bNV_Retain1~3持久化，上电后可在S30_IDLE阶段选择从断点恢复或全复位
5. **手动/自动双模式**：自动模式走完整状态机；手动模式下状态机暂停，各执行器独立响应手动命令，安全互锁始终生效
6. **PLCopen标准接口**：输出q_bDone/q_bBusy/q_bError/q_iErrorID四元组，与FB_2001报警管理块无缝对接

## 2. 状态定义表

### 2.1 主状态机状态

| 状态值 | 常量名 | 步骤名 | 入口动作 | 出口条件 | 出口目标 |
|:------:|--------|--------|----------|----------|----------|
| 0 | S30_IDLE | 待机等待 | 清残留/NV检查/回原点 | Start上升沿 | S31 |
| 1 | S31_FEED_CHECK | 入料检测 | 启动入料检测定时器 | 任一FeedDetect=TRUE | S32 |
| 2 | S32_LIFT_DOWN | 气缸下行 | MainCylinder.Extend:=TRUE | ExtendedPos=TRUE | S33 |
| 3 | S33_PICK_DOWN | 取物下降 | PickCylinder.Extend:=TRUE | ExtendedPos=TRUE | S34 |
| 4 | S34_PICK_CLAMP | 取物夹取 | 夹取电磁阀ON+启动确认定时器 | 确认时间到+到位OK | S35 |
| 5 | S35_PICK_UP | 取物上升 | PickCylinder.Retract:=TRUE | RetractedPos=TRUE | S36 |
| 6 | S36_MOTOR_FWD | 正转90度 | RotateMotor.FwdCmd:=TRUE | FwdArrived=TRUE | S37 |
| 7 | S37_PLACE_DOWN | 放物下降 | PlaceCylinder.Extend:=TRUE | ExtendedPos=TRUE | S38 |
| 8 | S38_PLACE_RELEASE | 放物释放 | 释放电磁阀ON+启动确认定时器 | 确认时间到 | S39 |
| 9 | S39_PLACE_UP | 放物上升 | PlaceCylinder.Retract:=TRUE | RetractedPos=TRUE | S40 |
| 10 | S40_MOTOR_REV | 反转90度 | RotateMotor.RevCmd:=TRUE | RevArrived=TRUE | S41 |
| 11 | S41_LIFT_UP | 气缸上行 | MainCylinder.Retract:=TRUE | RetractedPos=TRUE | S42 |
| 12 | S42_CYCLE_DONE | 周期完成 | Done脉冲+Busy清零 | 脉冲结束 | S30 |

### 2.2 物理状态跟踪（各气缸）

以主升降气缸为例，其余4组气缸同理：

| 物理状态 | 条件 | Extend | Retract |
|----------|------|:------:|:-------:|
| 上位(待机) | RetractedPos=TRUE, ExtendedPos=FALSE | FALSE | FALSE |
| 下位(工作) | ExtendedPos=TRUE, RetractedPos=FALSE | FALSE | FALSE |
| 下降中 | 两传感器FALSE, 命令=Extend | TRUE | FALSE |
| 上升中 | 两传感器FALSE, 命令=Retract | FALSE | TRUE |
| 传感器故障 | 两传感器TRUE | 保持上次 | 保持上次 |

## 3. 详细伪代码

### 3.0 前置处理：使能关闭 / 复位 / 停止

```pascal
(* ==================== 使能关闭处理 ==================== *)
IF NOT i_bAutoMode AND NOT i_bManualMode THEN
    (* 全部输出清零 *)
    q_bOutputReset := TRUE;
    q_bCylinderUp := FALSE;  q_bCylinderDown := FALSE;
    q_bPickUp := FALSE;      q_bPickDown := FALSE;
    q_bPlaceUp := FALSE;     q_bPlaceDown := FALSE;
    q_bSwingArmDown := FALSE;
    q_bPushPlateUp := FALSE; q_bPushPlateDown := FALSE;
    q_bMotorFwd := FALSE;    q_bMotorRev := FALSE;

    (* 6个结构体命令清除 *)
    io_stMainCylinder.Extend   := FALSE;  io_stMainCylinder.Retract   := FALSE;
    io_stPickCylinder.Extend  := FALSE;  io_stPickCylinder.Retract  := FALSE;
    io_stPlaceCylinder.Extend := FALSE;  io_stPlaceCylinder.Retract := FALSE;
    io_stSwingArmCyl.Extend  := FALSE;  io_stSwingArmCyl.Retract  := FALSE;
    io_stPushPlateCyl.Extend := FALSE;  io_stPushPlateCyl.Retract := FALSE;
    io_stRotateMotor.FwdCmd  := FALSE;  io_stRotateMotor.RevCmd   := FALSE;

    (* 报警/错误/状态清零 *)
    q_bAlarm0..q_bAlarm10 := FALSE;
    q_bError1..q_bError5  := FALSE;
    q_bError := FALSE;  q_iErrorID := 0;
    q_bBusy := FALSE;   q_bDone := FALSE;
    iCurrentStep := S30_IDLE;
    bRunning := FALSE;
    RETURN;
END_IF;


(* ==================== 复位处理 ==================== *)
IF i_bReset THEN
    q_bOutputReset := TRUE;
    (* 同使能关闭的全部清零逻辑 *)
    (* 额外: NV清除 *)
    q_bNV_Retain1 := FALSE;  q_bNV_Retain2 := FALSE;  q_bNV_Retain3 := FALSE;
    iCurrentStep := S30_IDLE;
    bRunning := FALSE;
    q_bBusy := FALSE;  q_bDone := FALSE;  q_bError := FALSE;
    RETURN;
END_IF;


(* ==================== 停止处理 ==================== *)
IF i_bStop AND bRunning THEN
    (* 所有气缸/电机命令立即清除 *)
    io_stMainCylinder.Extend  := FALSE;  io_stMainCylinder.Retract  := FALSE;
    io_stPickCylinder.Extend := FALSE;  io_stPickCylinder.Retract := FALSE;
    io_stPlaceCylinder.Extend := FALSE; io_stPlaceCylinder.Retract := FALSE;
    io_stSwingArmCyl.Extend := FALSE;  io_stSwingArmCyl.Retract := FALSE;
    io_stPushPlateCyl.Extend := FALSE; io_stPushPlateCyl.Retract := FALSE;
    io_stRotateMotor.FwdCmd := FALSE;  io_stRotateMotor.RevCmd  := FALSE;

    (* 记录当前步序到NV - 支持断点恢复 *)
    q_bNV_Retain1 := (iCurrentStep > S30_IDLE);
    q_bNV_Retain2 := BOOL_TO_BYTE(iCurrentStep).%X0;  (* 低字节存步序低4位 *)
    q_bNV_Retain3 := BOOL_TO_BYTE(iCurrentStep).%X1;  (* 高位存步序高4位 *)

    bRunning := FALSE;
    q_bBusy := FALSE;
    (* 注意: 停止≠错误, 不置 q_bError *)
END_IF;
```

### 3.1 模式分发

```pascal
(* ==================== 模式分发 ==================== *)
IF i_bAutoMode THEN
    CASE iCurrentState OF
        S30_IDLE:           (* 3.2 *)
        S31_FEED_CHECK:     (* 3.3 *)
        S32_LIFT_DOWN:      (* 3.4 *)
        S33_PICK_DOWN:      (* 3.5 *)
        S34_PICK_CLAMP:     (* 3.6 *)
        S35_PICK_UP:        (* 3.7 *)
        S36_MOTOR_FWD:      (* 3.8 *)
        S37_PLACE_DOWN:     (* 3.9 *)
        S38_PLACE_RELEASE:  (* 3.10 *)
        S39_PLACE_UP:       (* 3.11 *)
        S40_MOTOR_REV:      (* 3.12 *)
        S41_LIFT_UP:        (* 3.13 *)
        S42_CYCLE_DONE:     (* 3.14 *)
    END_CASE;

ELSIF i_bManualMode THEN
    (* ---- 手动模式: 直接映射按钮→ST_Cylinder/ST_ConveyorMotor ---- *)
    bRunning := FALSE;
    q_bBusy := FALSE;

    (* 手动升降气缸控制 *)
    IF i_bLx_CylUp AND NOT i_bLx_CylDown THEN
        io_stMainCylinder.Retract := TRUE;  io_stMainCylinder.Extend := FALSE;
    ELSIF i_bLx_CylDown AND NOT i_bLx_CylUp THEN
        io_stMainCylinder.Extend := TRUE;   io_stMainCylinder.Retract := FALSE;
    ELSE
        io_stMainCylinder.Extend := FALSE;  io_stMainCylinder.Retract := FALSE;
    END_IF;

    (* 手动取物机构控制 - 同理... *)
    (* 手动放物机构控制 - 同理... *)
    (* 手动摆臂/推板控制 - 同理... *)

    (* 手动电机控制 *)
    IF i_bLx_MotorFwd THEN
        io_stRotateMotor.FwdCmd := TRUE;  io_stRotateMotor.RevCmd := FALSE;
    ELSIF i_bLx_MotorRev THEN
        io_stRotateMotor.RevCmd := TRUE;  io_stRotateMotor.FwdCmd := FALSE;
    ELSE
        io_stRotateMotor.FwdCmd := FALSE; io_stRotateMotor.RevCmd := FALSE;
    END_IF;

ELSE
    (* 关闭模式已在3.0前置处理中RETURN *)
END_IF;
```

### 3.2 S30_IDLE -- 待机等待

```pascal
S30_IDLE:  (* 0 - 待机等待 *)
    IF bStepEntry THEN
        (* 清除所有残留命令和脉冲输出 *)
        io_stMainCylinder.Extend  := FALSE;  io_stMainCylinder.Retract  := FALSE;
        io_stPickCylinder.Extend := FALSE;  io_stPickCylinder.Retract := FALSE;
        io_stPlaceCylinder.Extend := FALSE; io_stPlaceCylinder.Retract := FALSE;
        io_stSwingArmCyl.Extend := FALSE;  io_stSwingArmCyl.Retract := FALSE;
        io_stPushPlateCyl.Extend := FALSE; io_stPushPlateCyl.Retract := FALSE;
        io_stRotateMotor.FwdCmd := FALSE;  io_stRotateMotor.RevCmd  := FALSE;
        q_bDone := FALSE;
        q_bPickDone := FALSE;
        q_bPlaceDone := FALSE;
        q_bWaitState1 := FALSE;
        q_bTrayIn := FALSE;
        q_bOutputReset := FALSE;
        bStepEntry := FALSE;
    END_IF;

    (* NV恢复检查: 若断电时正在运行, 提示操作员 *)
    IF q_bNV_Retain1 OR q_bNV_Retain2 OR q_bNV_Retain3 THEN
        (* NV有效 → 可选: 自动恢复到S41_LIFT_UP(安全回原点序列)
           或等待人工确认后再决定 *)
        (* 此处默认行为: 不自动恢复, 等待新Start命令从头开始 *)
        (* NV标志在i_bReset时清除, 或在首次成功周期完成后清除 *)
    END_IF;

    (* 安全回原点检查: 确保气缸在上位才能开始新周期 *)
    IF NOT i_bLiftUpPos THEN
        (* 气缸不在上位 → 先执行回原点(可选自动回原点或报警) *)
        (* 方案A: 自动回原点 *)
        io_stMainCylinder.Retract := TRUE;
        IF i_bLiftUpPos THEN
            io_stMainCylinder.Retract := FALSE;
        END_IF;
        (* 方案B: 报警等待人工干预 (更安全的默认策略) *)
        (* q_bAlarm0 := TRUE;  q_iErrorID := 144;  RETURN; *)
    END_IF;

    (* VFD/电机预检 *)
    IF io_stRotateMotor.VfdFault THEN
        q_bAlarm9  := TRUE;
        q_bError3  := TRUE;
        q_bError   := TRUE;
        q_iErrorID := 142;                    (* 报警142: VFD故障 *)
    END_IF;

    (* 安全门预检 *)
    IF NOT io_stRotateMotor.SafetyDoorOk THEN
        q_bAlarm10 := TRUE;
        q_bError5  := TRUE;
        q_bError   := TRUE;
        q_iErrorID := 143;                    (* 报警143: 安全门打开 *)
    END_IF;

    (* 启动触发: 上升沿 + 无报警 + 使能有效 *)
    IF bStartTriggered AND i_bEnable
       AND NOT q_bError THEN
        bRunning := TRUE;
        q_bBusy := TRUE;
        bStepEntry := TRUE;
        iCurrentStep := S31_FEED_CHECK;
    END_IF;
```

### 3.3 S31_FEED_CHECK -- 入料检测

```pascal
S31_FEED_CHECK:  (* 1 - 入料检测 *)
    IF bStepEntry THEN
        (* 启动入料检测超时定时器 *)
        tFeedTimeout.PT := INT_TO_DINT(i_iFeedTimeoutMs);   (* 默认3000ms, 0=无限等待 *)
        tFeedTimeout.IN := TRUE;
        bStepEntry := FALSE;
    END_IF;

    (* 5路入料传感器任一检测到物料 → 有料 *)
    IF i_bFeedDetect0 OR i_bFeedDetect1 OR i_bFeedDetect2
       OR i_bFeedDetect3 OR i_bFeedDetect4 THEN
        tFeedTimeout.IN := FALSE;
        (* 更新有料指示 *)
        q_bA_InputHasMaterial  := i_bFeedDetect0 OR i_bFeedDetect1;
        q_bInputA_HasMaterial := i_bFeedDetect2 OR i_bFeedDetect3;
        q_bCPortIn_HasMaterial := i_bFeedDetect4;
        bStepEntry := TRUE;
        iCurrentStep := S32_LIFT_DOWN;

    (* 超时: 全部传感器无信号 *)
    ELSIF tFeedTimeout.Q AND (i_iFeedTimeoutMs > 0) THEN
        tFeedTimeout.IN := FALSE;
        q_bAlarm7  := TRUE;                   (* 报警140: 入料无料 *)
        q_bError5  := TRUE;
        q_bError   := TRUE;
        q_iErrorID := 140;
        (* 选择: 停在S31等待来料 或 回退到S30 *)
        (* 默认: 停在S31, 不归零, 来料后继续 *)
    END_IF;
```

### 3.4 S32_LIFT_DOWN -- 气缸下行

```pascal
S32_LIFT_DOWN:  (* 2 - 升降气缸下降到工作位 *)
    IF bStepEntry THEN
        (* 通过ST_Cylinder发伸出(下降)命令 *)
        io_stMainCylinder.Extend  := TRUE;
        io_stMainCylinder.Retract := FALSE;

        (* 映射到直接输出 *)
        q_bCylinderDown := TRUE;
        q_bCylinderUp   := FALSE;

        (* 设置超时参数 *)
        io_stMainCylinder.TimeoutMs := i_iLiftTimeoutMs;

        (* 启动超时定时器 *)
        tLiftDownTimeout.PT := INT_TO_DINT(i_iLiftTimeoutMs);  (* 默认5000ms *)
        tLiftDownTimeout.IN := TRUE;
        bStepEntry := FALSE;
    END_IF;

    (* 到位判断: 下限位传感器=TRUE *)
    IF io_stMainCylinder.ExtendedPos OR i_bLiftDownPos THEN
        tLiftDownTimeout.IN := FALSE;
        io_stMainCylinder.Extend := FALSE;
        q_bCylinderDown := FALSE;
        q_bCylinderAtBottom := TRUE;
        q_bCylinderAtTop   := FALSE;
        io_stMainCylinder.IsExtended  := TRUE;
        io_stMainCylinder.IsRetracted := FALSE;
        bStepEntry := TRUE;
        iCurrentStep := S33_PICK_DOWN;

    (* 超时判断 *)
    ELSIF tLiftDownTimeout.Q AND (i_iLiftTimeoutMs > 0) THEN
        tLiftDownTimeout.IN := FALSE;
        io_stMainCylinder.Extend := FALSE;
        q_bCylinderDown := FALSE;
        q_bAlarm0  := TRUE;                     (* 报警130: 升降下行超时 *)
        q_bError1  := TRUE;
        q_bError   := TRUE;
        q_iErrorID := 130;
        (* 停在当前步, 等待复位或人工干预 *)
    END_IF;
```

### 3.5 S33_PICK_DOWN -- 取物下降

```pascal
S33_PICK_DOWN:  (* 3 - 取物机构下降 *)
    IF bStepEntry THEN
        io_stPickCylinder.Extend  := TRUE;
        io_stPickCylinder.Retract := FALSE;
        q_bPickDown := TRUE;
        q_bPickUp   := FALSE;
        io_stPickCylinder.TimeoutMs := i_iPickTimeoutMs;

        tPickDownTimeout.PT := INT_TO_DINT(i_iPickTimeoutMs);  (* 默认3000ms *)
        tPickDownTimeout.IN := TRUE;
        bStepEntry := FALSE;
    END_IF;

    IF io_stPickCylinder.ExtendedPos THEN
        tPickDownTimeout.IN := FALSE;
        io_stPickCylinder.Extend := FALSE;
        q_bPickDown := FALSE;
        q_bPickAtBottom := TRUE;
        q_bPickAtTop   := FALSE;
        io_stPickCylinder.IsExtended  := TRUE;
        io_stPickCylinder.IsRetracted := FALSE;
        bStepEntry := TRUE;
        iCurrentStep := S34_PICK_CLAMP;

    ELSIF tPickDownTimeout.Q AND (i_iPickTimeoutMs > 0) THEN
        tPickDownTimeout.IN := FALSE;
        io_stPickCylinder.Extend := FALSE;
        q_bPickDown := FALSE;
        q_bAlarm2  := TRUE;                     (* 报警132: 取物下降超时 *)
        q_bError2  := TRUE;
        q_bError   := TRUE;
        q_iErrorID := 132;
    END_IF;
```

### 3.6 S34_PICK_CLAMP -- 取物夹取

```pascal
S34_PICK_CLAMP:  (* 4 - 夹取物料+确认 *)
    IF bStepEntry THEN
        (* 执行夹取动作 - 输出夹取电磁阀 *)
        (* 注: 具体夹取输出取决于机械设计(气动夹爪/真空吸盘等)
           此处以通用布尔输出表示 *)
        q_bPickDone := FALSE;                   (* 先清零 *)

        (* 启动夹紧确认定时器 *)
        tClampPickConfirm.PT := INT_TO_DINT(i_iClampConfirmMs);  (* 默认500ms *)
        tClampPickConfirm.IN := TRUE;
        bStepEntry := FALSE;
    END_IF;

    IF tClampPickConfirm.Q THEN                              (* 确认时间到 *)
        tClampPickConfirm.IN := FALSE;

        (* 检查夹取确认信号 (外部传感器或压力开关等) *)
        IF i_bPickPlaceDone THEN
            q_bPickDone := TRUE;               (* 取物完成 *)
            bStepEntry := TRUE;
            iCurrentStep := S35_PICK_UP;
        ELSE
            (* 夹取未确认 → 可能无料或夹具异常 *)
            q_bAlarm3  := TRUE;                (* 报警134: 夹取失败 *)
            q_bError2  := TRUE;
            q_bError   := TRUE;
            q_iErrorID := 134;
            (* 选项: 重试 / 跳到松开退出(S25风格) / 停住报警 *)
            iCurrentStep := S35_PICK_UP;       (* 默认: 继续上升再处理 *)
        END_IF;
    END_IF;
```

### 3.7 S35_PICK_UP -- 取物上升

```pascal
S35_PICK_UP:  (* 5 - 取物机构上升收回 *)
    IF bStepEntry THEN
        io_stPickCylinder.Retract := TRUE;
        io_stPickCylinder.Extend  := FALSE;
        q_bPickUp   := TRUE;
        q_bPickDown := FALSE;

        tPickUpTimeout.PT := INT_TO_DINT(i_iPickTimeoutMs);
        tPickUpTimeout.IN := TRUE;
        bStepEntry := FALSE;
    END_IF;

    IF io_stPickCylinder.RetractedPos THEN
        tPickUpTimeout.IN := FALSE;
        io_stPickCylinder.Retract := FALSE;
        q_bPickUp := FALSE;
        q_bPickAtTop     := TRUE;
        q_bPickAtBottom  := FALSE;
        q_bPickUpDone    := TRUE;              (* 取物上升完成信号 *)
        io_stPickCylinder.IsExtended  := FALSE;
        io_stPickCylinder.IsRetracted := TRUE;
        bStepEntry := TRUE;
        iCurrentStep := S36_MOTOR_FWD;

    ELSIF tPickUpTimeout.Q AND (i_iPickTimeoutMs > 0) THEN
        tPickUpTimeout.IN := FALSE;
        io_stPickCylinder.Retract := FALSE;
        q_bPickUp := FALSE;
        q_bAlarm2  := TRUE;                    (* 报警133: 取物上升超时 *)
        q_bError2  := TRUE;
        q_bError   := TRUE;
        q_iErrorID := 133;
    END_IF;
```

### 3.8 S36_MOTOR_FWD -- 电机正转90度

```pascal
S36_MOTOR_FWD:  (* 6 - 旋转电机正向90度(A位置→D位置) *)
    IF bStepEntry THEN
        (* VFD预检 *)
        IF io_stRotateMotor.VfdFault THEN
            q_bAlarm9  := TRUE;
            q_bError3  := TRUE;
            q_bError   := TRUE;
            q_iErrorID := 142;                 (* VFD故障 *)
            iCurrentStep := S30_IDLE;
            bRunning := FALSE;
            RETURN;
        END_IF;

        (* 安全门互锁 *)
        IF NOT io_stRotateMotor.SafetyDoorOk THEN
            q_bAlarm10 := TRUE;
            q_bError5  := TRUE;
            q_bError   := TRUE;
            q_iErrorID := 143;
            iCurrentStep := S30_IDLE;
            bRunning := FALSE;
            RETURN;
        END_IF;

        (* 发正转命令 *)
        io_stRotateMotor.FwdCmd := TRUE;
        io_stRotateMotor.RevCmd := FALSE;
        q_bMotorFwd := TRUE;
        q_bMotorRev := FALSE;

        (* 位置指示更新 *)
        q_bPosA_Picker := FALSE;               (* 离开A位置 *)
        q_bPosA_Feeder := FALSE;
        q_bPosA        := FALSE;
        q_bPosAO       := TRUE;                (* 经过AO位置 *)
        q_bPosO        := FALSE;
        q_bPosOD       := FALSE;
        q_bPosD        := FALSE;

        tMotorFwdTimeout.PT := INT_TO_DINT(i_iMotorTimeoutMs);  (* 默认5000ms *)
        tMotorFwdTimeout.IN := TRUE;
        bStepEntry := FALSE;
    END_IF;

    (* 到位: 正转到位传感器=TRUE *)
    IF i_bFwdArrived THEN
        tMotorFwdTimeout.IN := FALSE;
        io_stRotateMotor.FwdCmd := FALSE;
        q_bMotorFwd := FALSE;
        q_bPosO     := TRUE;                (* 到达D位置 *)
        q_bPosOD       := TRUE;
        q_bPosAO       := FALSE;
        q_bPosO        := FALSE;
        io_stRotateMotor.FwdOut := FALSE;
        io_stRotateMotor.Running := FALSE;
        bStepEntry := TRUE;
        iCurrentStep := S37_PLACE_DOWN;

    (* 超时 *)
    ELSIF tMotorFwdTimeout.Q AND (i_iMotorTimeoutMs > 0) THEN
        tMotorFwdTimeout.IN := FALSE;
        io_stRotateMotor.FwdCmd := FALSE;
        q_bMotorFwd := FALSE;
        q_bAlarm4  := TRUE;                    (* 报警135: 正转超时 *)
        q_bError3  := TRUE;
        q_bError   := TRUE;
        q_iErrorID := 135;
    END_IF;
```

### 3.9 S37_PLACE_DOWN -- 放物下降

```pascal
S37_PLACE_DOWN:  (* 7 - 放物机构下降 *)
    IF bStepEntry THEN
        io_stPlaceCylinder.Extend  := TRUE;
        io_stPlaceCylinder.Retract := FALSE;
        q_bPlaceDown := TRUE;
        q_bPlaceUp   := FALSE;
        io_stPlaceCylinder.TimeoutMs := i_iPlaceTimeoutMs;

        tPlaceDownTimeout.PT := INT_TO_DINT(i_iPlaceTimeoutMs);  (* 默认3000ms *)
        tPlaceDownTimeout.IN := TRUE;
        bStepEntry := FALSE;
    END_IF;

    IF io_stPlaceCylinder.ExtendedPos THEN
        tPlaceDownTimeout.IN := FALSE;
        io_stPlaceCylinder.Extend := FALSE;
        q_bPlaceDown := FALSE;
        io_stPlaceCylinder.IsExtended  := TRUE;
        io_stPlaceCylinder.IsRetracted := FALSE;
        bStepEntry := TRUE;
        iCurrentStep := S38_PLACE_RELEASE;

    ELSIF tPlaceDownTimeout.Q AND (i_iPlaceTimeoutMs > 0) THEN
        tPlaceDownTimeout.IN := FALSE;
        io_stPlaceCylinder.Extend := FALSE;
        q_bPlaceDown := FALSE;
        q_bAlarm5  := TRUE;                    (* 报警137: 放物下降超时 *)
        q_bError4  := TRUE;
        q_bError   := TRUE;
        q_iErrorID := 137;
    END_IF;
```

### 3.10 S38_PLACE_RELEASE -- 放物释放

```pascal
S38_PLACE_RELEASE:  (* 8 - 释放物料+确认 *)
    IF bStepEntry THEN
        (* 执行释放动作 *)
        q_bPlaceDone := FALSE;                 (* 先清零 *)

        (* 出盘进入信号 *)
        q_bTrayIn := TRUE;

        (* 启动释放确认定时器 *)
        tClampPlaceConfirm.PT := INT_TO_DINT(i_iClampConfirmMs);  (* 默认500ms *)
        tClampPlaceConfirm.IN := TRUE;
        bStepEntry := FALSE;
    END_IF;

    IF tClampPlaceConfirm.Q THEN                              (* 确认时间到 *)
        tClampPlaceConfirm.IN := FALSE;
        q_bTrayIn   := FALSE;
        q_bPlaceDone := TRUE;                  (* 放物完成信号 *)
        bStepEntry := TRUE;
        iCurrentStep := S39_PLACE_UP;
    END_IF;
```

### 3.11 S39_PLACE_UP -- 放物上升

```pascal
S39_PLACE_UP:  (* 9 - 放物机构上升收回 *)
    IF bStepEntry THEN
        io_stPlaceCylinder.Retract := TRUE;
        io_stPlaceCylinder.Extend  := FALSE;
        q_bPlaceUp   := TRUE;
        q_bPlaceDown := FALSE;

        tPlaceUpTimeout.PT := INT_TO_DINT(i_iPlaceTimeoutMs);
        tPlaceUpTimeout.IN := TRUE;
        bStepEntry := FALSE;
    END_IF;

    IF io_stPlaceCylinder.RetractedPos THEN
        tPlaceUpTimeout.IN := FALSE;
        io_stPlaceCylinder.Retract := FALSE;
        q_bPlaceUp := FALSE;
        io_stPlaceCylinder.IsExtended  := FALSE;
        io_stPlaceCylinder.IsRetracted := TRUE;
        bStepEntry := TRUE;
        iCurrentStep := S40_MOTOR_REV;

    ELSIF tPlaceUpTimeout.Q AND (i_iPlaceTimeoutMs > 0) THEN
        tPlaceUpTimeout.IN := FALSE;
        io_stPlaceCylinder.Retract := FALSE;
        q_bPlaceUp := FALSE;
        q_bAlarm5  := TRUE;                    (* 报警138: 放物上升超时 *)
        q_bError4  := TRUE;
        q_bError   := TRUE;
        q_iErrorID := 138;
    END_IF;
```

### 3.12 S40_MOTOR_REV -- 电机反转90度

```pascal
S40_MOTOR_REV:  (* 10 - 旋转电机反向90度(D位置→A位置回原位) *)
    IF bStepEntry THEN
        (* VFD预检 + 安全门互锁 — 与S36相同模式 *)
        IF io_stRotateMotor.VfdFault THEN
            q_bAlarm9 := TRUE;  q_bError3 := TRUE;
            q_bError := TRUE;  q_iErrorID := 142;
            iCurrentStep := S30_IDLE;  bRunning := FALSE;
            RETURN;
        END_IF;
        IF NOT io_stRotateMotor.SafetyDoorOk THEN
            q_bAlarm10 := TRUE;  q_bError5 := TRUE;
            q_bError := TRUE;  q_iErrorID := 143;
            iCurrentStep := S30_IDLE;  bRunning := FALSE;
            RETURN;
        END_IF;

        (* 发反转命令 *)
        io_stRotateMotor.RevCmd := TRUE;
        io_stRotateMotor.FwdCmd := FALSE;
        q_bMotorRev := TRUE;
        q_bMotorFwd := FALSE;

        (* 位置指示更新 *)
        q_bPosD  := FALSE;                     (* 离开D位置 *)
        q_bPosOD := TRUE;                      (* 经过OD位置 *)
        q_bPosO  := TRUE;                      (* 经过O位置 *)
        q_bPosAO := TRUE;                      (* 经过AO位置 *)

        tMotorRevTimeout.PT := INT_TO_DINT(i_iMotorTimeoutMs);
        tMotorRevTimeout.IN := TRUE;
        bStepEntry := FALSE;
    END_IF;

    (* 到位: 反转到位传感器=TRUE *)
    IF i_bRevArrived THEN
        tMotorRevTimeout.IN := FALSE;
        io_stRotateMotor.RevCmd := FALSE;
        q_bMotorRev := FALSE;
        q_bPosA     := TRUE;                (* 回到A位置 *)
        q_bPosAO       := FALSE;
        q_bPosO        := FALSE;
        q_bPosOD       := FALSE;
        q_bPosD        := FALSE;
        q_bPosA_Picker := TRUE;                (* A侧取物者就绪 *)
        q_bPosA_Feeder := TRUE;                (* A侧入物者就绪 *)
        io_stRotateMotor.RevOut := FALSE;
        io_stRotateMotor.Running := FALSE;
        bStepEntry := TRUE;
        iCurrentStep := S41_LIFT_UP;

    (* 超时 *)
    ELSIF tMotorRevTimeout.Q AND (i_iMotorTimeoutMs > 0) THEN
        tMotorRevTimeout.IN := FALSE;
        io_stRotateMotor.RevCmd := FALSE;
        q_bMotorRev := FALSE;
        q_bAlarm4  := TRUE;                    (* 报警136: 反转超时 *)
        q_bError3  := TRUE;
        q_bError   := TRUE;
        q_iErrorID := 136;
    END_IF;
```

### 3.13 S41_LIFT_UP -- 气缸上行

```pascal
S41_LIFT_UP:  (* 11 - 升降气缸上升到待机位 *)
    IF bStepEntry THEN
        io_stMainCylinder.Retract := TRUE;
        io_stMainCylinder.Extend  := FALSE;
        q_bCylinderUp   := TRUE;
        q_bCylinderDown := FALSE;

        tLiftUpTimeout.PT := INT_TO_DINT(i_iLiftTimeoutMs);
        tLiftUpTimeout.IN := TRUE;
        bStepEntry := FALSE;
    END_IF;

    IF io_stMainCylinder.RetractedPos OR i_bLiftUpPos THEN
        tLiftUpTimeout.IN := FALSE;
        io_stMainCylinder.Retract := FALSE;
        q_bCylinderUp := FALSE;
        q_bCylinderAtTop     := TRUE;
        q_bCylinderAtBottom  := FALSE;
        io_stMainCylinder.IsExtended  := FALSE;
        io_stMainCylinder.IsRetracted := TRUE;
        bStepEntry := TRUE;
        iCurrentStep := S42_CYCLE_DONE;

    ELSIF tLiftUpTimeout.Q AND (i_iLiftTimeoutMs > 0) THEN
        tLiftUpTimeout.IN := FALSE;
        io_stMainCylinder.Retract := FALSE;
        q_bCylinderUp := FALSE;
        q_bAlarm1  := TRUE;                    (* 报警131: 升降上行超时 *)
        q_bError1  := TRUE;
        q_bError   := TRUE;
        q_iErrorID := 131;
    END_IF;
```

### 3.14 S42_CYCLE_DONE -- 周期完成

```pascal
S42_CYCLE_DONE:  (* 12 - 周期完成, 输出Done脉冲 *)
    IF bStepEntry THEN
        (* 输出完成脉冲 *)
        q_bDone := TRUE;
        q_bBusy := FALSE;
        bRunning := FALSE;

        (* 清除断电保持 (本次周期正常完成) *)
        q_bNV_Retain1 := FALSE;
        q_bNV_Retain2 := FALSE;
        q_bNV_Retain3 := FALSE;

        (* 启动Done脉冲定时器 *)
        tDonePulse.PT := INT_TO_DINT(i_iCycleDonePulseMs);  (* 默认500ms *)
        tDonePulse.IN := TRUE;
        bStepEntry := FALSE;
    END_IF;

    IF tDonePulse.Q THEN                            (* 脉冲宽度结束 *)
        tDonePulse.IN := FALSE;
        q_bDone := FALSE;
        q_bWaitState1 := TRUE;                 (* 等待状态指示 *)
        bStepEntry := TRUE;
        iCurrentStep := S30_IDLE;              (* 返回待机, 等待下一周期 *)
    END_IF;
```

### 3.15 定时器实例调用与边沿检测

```pascal
(* ==================== 逐个调用12个FB_TON定时器实例 ==================== *)

(* S31 入料检测超时 *)
tFeedTimeout(IN := tFeedTimeout.IN, PT := tFeedTimeout.PT,
             Q => tFeedTimeout.Q, ET => tFeedTimeout.ET);

(* S32 主升降下降超时 *)
tLiftDownTimeout(IN := tLiftDownTimeout.IN, PT := tLiftDownTimeout.PT,
                 Q => tLiftDownTimeout.Q, ET => tLiftDownTimeout.ET);

(* S33 取物下降超时 *)
tPickDownTimeout(IN := tPickDownTimeout.IN, PT := tPickDownTimeout.PT,
                 Q => tPickDownTimeout.Q, ET => tPickDownTimeout.ET);

(* S34 夹取确认等待 *)
tClampPickConfirm(IN := tClampPickConfirm.IN, PT := tClampPickConfirm.PT,
                  Q => tClampPickConfirm.Q, ET => tClampPickConfirm.ET);

(* S35 取物上升超时 *)
tPickUpTimeout(IN := tPickUpTimeout.IN, PT := tPickUpTimeout.PT,
               Q => tPickUpTimeout.Q, ET => tPickUpTimeout.ET);

(* S36 电机正转超时 *)
tMotorFwdTimeout(IN := tMotorFwdTimeout.IN, PT := tMotorFwdTimeout.PT,
                 Q => tMotorFwdTimeout.Q, ET => tMotorFwdTimeout.ET);

(* S37 放物下降超时 *)
tPlaceDownTimeout(IN := tPlaceDownTimeout.IN, PT := tPlaceDownTimeout.PT,
                  Q => tPlaceDownTimeout.Q, ET => tPlaceDownTimeout.ET);

(* S38 释放确认等待 *)
tClampPlaceConfirm(IN := tClampPlaceConfirm.IN, PT := tClampPlaceConfirm.PT,
                   Q => tClampPlaceConfirm.Q, ET => tClampPlaceConfirm.ET);

(* S39 放物上升超时 *)
tPlaceUpTimeout(IN := tPlaceUpTimeout.IN, PT := tPlaceUpTimeout.PT,
                Q => tPlaceUpTimeout.Q, ET => tPlaceUpTimeout.ET);

(* S40 电机反转超时 *)
tMotorRevTimeout(IN := tMotorRevTimeout.IN, PT := tMotorRevTimeout.PT,
                 Q => tMotorRevTimeout.Q, ET => tMotorRevTimeout.ET);

(* S41 主升降上升超时 *)
tLiftUpTimeout(IN := tLiftUpTimeout.IN, PT := tLiftUpTimeout.PT,
               Q => tLiftUpTimeout.Q, ET => tLiftUpTimeout.ET);

(* S42 Done脉冲宽度 *)
tDonePulse(IN := tDonePulse.IN, PT := tDonePulse.PT,
           Q => tDonePulse.Q, ET => tDonePulse.ET);


(* ==================== 上升沿检测 ==================== *)
(* Start信号上升沿检测 *)
bStartTriggered := i_bStart AND NOT i_bStartLast;
i_bStartLast := i_bStart;


(* ==================== 传感器冗余一致性检查 (持续运行) ==================== *)
(* 各ST_Cylinder内部的SensorFault由结构体自身维护,
   此处做跨气缸的附加一致性检查 *)

(* 主升降气缸上下位冲突 *)
IF i_bLiftUpPos AND i_bLiftDownPos THEN
    q_bAlarm8  := TRUE;                       (* 报警141: 传感器冲突 *)
    q_bError   := TRUE;
    q_iErrorID := 141;
ELSE
    (* 仅当无其他报警时才清除传感器冲突标志 *)
    IF q_iErrorID = 141 THEN
        q_bAlarm8 := FALSE;
        q_bError  := FALSE;
        q_iErrorID := 0;
    END_IF;
END_IF;


(* ==================== 中间状态M0~M10更新 ==================== *)
(* M0: 步进器运行中标志 *)
q_bM0 := bRunning;

(* M1: 气缸运动中标志 *)
q_bM1 := io_stMainCylinder.Extend OR io_stMainCylinder.Retract;

(* M2: 取物机构运动中 *)
q_bM2 := io_stPickCylinder.Extend OR io_stPickCylinder.Retract;

(* M3: 放物机构运动中 *)
q_bM3 := io_stPlaceCylinder.Extend OR io_stPlaceCylinder.Retract;

(* M4: 电机运行中 *)
q_bM4 := io_stRotateMotor.FwdCmd OR io_stRotateMotor.RevCmd;

(* M5: 任意报警活跃 *)
q_bM5 := q_bAlarm0 OR q_bAlarm1 OR q_bAlarm2 OR q_bAlarm3
      OR q_bAlarm4 OR q_bAlarm5 OR q_bAlarm6 OR q_bAlarm7
      OR q_bAlarm8 OR q_bAlarm9 OR q_bAlarm10;

(* M6~M10: 预留给扩展/子步骤暂存 *)
q_bM6 := FALSE;
q_bM7 := FALSE;
q_bM8 := FALSE;
q_bM9 := FALSE;
q_bM10 := FALSE;


(* ==================== PLCopen标准输出更新 ==================== *)
q_iCurrentStep := iCurrentStep;
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
气缸下行         ─────┐    ┌────────────────────────────────────────────────────┐
                    └────┘                                                    │
                                                                              │
取物下降              ──────────┐    ┌───────────────────────────────────────┐
                               └────┘                                       │
                                                                            │
取物上升                        ───────────────┐    ┌───────────────────────┐
                                               └────┘                      │
                                                                    │
电机正转                                   ────────────────────┐  ┌─────────┐
                                                              └──┘         │
                                                                           │
放物下降                                                       ──────────┐┌─────────┐
                                                                     └────┘│         │
                                                                           │
放物上升                                                                  ────┐┌─────┐
                                                                               └┘     │
                                                                                      │
电机反转                                                                         ────┐┌───┐
                                                                                    └┘   │
                                                                                         │
气缸上行                                                                                  ──┐┌─┘
                                                                                            └┘
q_bDone                                                                                        ─┐
                                                                                               └┘
```

### 4.2 超时场景 (S32气缸下行超时)

```
时间轴 →

S32进入         ─────────────────────────────────────────> (停在S32)

气缸下行(Extend) ─┐                                        (保持或由编排器决定)
                  └────────────────────────────────────── ... (超时后仍ON)

下位传感器       ───────────────────────────────── ... (始终FALSE, 未到位)

tLiftDownTimeout.Q ─────────────────────────┐
                                      └─────── ... (超时到达)

q_bAlarm0        ─────────────────────────┐
                                      └─────── ... (锁存)

q_bError         ─────────────────────────┐
                                      └─────── ... (锁存)

q_iErrorID       ─────────────────────────┐
                                      └─────── = 130

q_bBusy          ────────────────────────────────────── ... (仍为TRUE, 未清零)

步序             S32 ────────────────────────────────────── S32 (不跳步)
```

### 4.3 停止场景 (运行中途停止)

```
时间轴 →

Stop            ─────────────────┐
                                └───────>

当前步(如S36)   S36 ──────────── S36 (停在S36, 不归零)

电机正转(Fwd)   ─┐              (立即清除)
                 └─

气缸命令        ─┐              (全部立即清除)
                 └─

q_bBusy         ────────────────┘ (FALSE)

q_bError        ──────────────── (FALSE, 停止!=错误)

NV_Retain1~3   ────────────────┐ (记录步序上下文)
                                └─────── (保持TRUE直到Reset)
```

## 5. 边界条件处理

| 场景 | 行为 |
|------|------|
| Start时已在S42(Done态) | 忽略，等Done脉冲结束后自动回到S30方可重新触发 |
| Start时报警活跃(q_bError=TRUE) | 拒绝启动，需先Reset清除报警 |
| Enable=FALSE时收到Start | 忽略启动请求 |
| S32下降时已在下位 | 立即置ExtendedPos=TRUE，不启动超时计时，直接跳S33 |
| S41上升时已在上位 | 立即置RetractedPos=TRUE，直接跳S42 |
| S36/S40运行中VFD故障 | 立即停电机+报警142+回退S30 |
| S36/S40运行中安全门打开 | 立即停电机+报警143+回退S30 |
| 运动中命令翻转(如手动切自动) | 当前步正常完成后再响应新模式 |
| 所有超时参数=0 | 关闭该类超时检测，对应Alarm永不触发 |
| 上下位传感器同时ON | SensorFault=TRUE(Alarm141)，步序暂停 |
| 断电后上电(NV有效) | S30_IDLE检测NV标志，提示操作员，不自动恢复 |
| Stop后立即Start | 从停止时的步序继续(若气缸位置合理)或要求先Reset |
| 连续快速Start(防重入) | bRunning标志防重入，必须等S42完成后方可下一周期 |
| 手动模式切回自动 | 从当前iCurrentStep继续(若在S30则正常待机) |
| 夹取确认时无料(S34) | 报警134，可选择继续上升(S35)或回退 |

## 6. 变量定义详情

### 6.1 VAR (内部变量)

| 变量 | 类型 | 初始值 | 保持性 | 说明 |
|------|------|:------:|:------:|------|
| iCurrentStep | INT | 0 | 非保持 | 当前状态机步序(0~12) |
| bStepEntry | BOOL | FALSE | 非保持 | 步进入口标志(每步首扫描=TRUE) |
| bRunning | BOOL | FALSE | 非保持 | 周期运行中标志 |
| bStartTriggered | BOOL | FALSE | 非保持 | Start上升沿检测结果 |
| i_bStartLast | BOOL | FALSE | 非保持 | Start上一周期值(沿检测用) |
| iPickLayer | INT | 0 | 非保持 | 当前行号/工位号(预留扩展) |
| tFeedTimeout | FB_TON | -- | 非保持 | S31 入料检测超时, PT=i_iFeedTimeoutMs |
| tLiftDownTimeout | FB_TON | -- | 非保持 | S32 主升降下降超时, PT=i_iLiftTimeoutMs |
| tPickDownTimeout | FB_TON | -- | 非保持 | S33 取物下降超时, PT=i_iPickTimeoutMs |
| tClampPickConfirm | FB_TON | -- | 非保持 | S34 夹取确认等待, PT=i_iClampConfirmMs |
| tPickUpTimeout | FB_TON | -- | 非保持 | S35 取物上升超时, PT=i_iPickTimeoutMs |
| tMotorFwdTimeout | FB_TON | -- | 非保持 | S36 电机正转超时, PT=i_iMotorTimeoutMs |
| tPlaceDownTimeout | FB_TON | -- | 非保持 | S37 放物下降超时, PT=i_iPlaceTimeoutMs |
| tClampPlaceConfirm | FB_TON | -- | 非保持 | S38 释放确认等待, PT=i_iClampConfirmMs |
| tPlaceUpTimeout | FB_TON | -- | 非保持 | S39 放物上升超时, PT=i_iPlaceTimeoutMs |
| tMotorRevTimeout | FB_TON | -- | 非保持 | S40 电机反转超时, PT=i_iMotorTimeoutMs |
| tLiftUpTimeout | FB_TON | -- | 非保持 | S41 主升降上升超时, PT=i_iLiftTimeoutMs |
| tDonePulse | FB_TON | -- | 非保持 | S42 Done脉冲宽度, PT=i_iCycleDonePulseMs |

### 6.2 定时器配置总表

| 变量名 | 类型 | 用途 | 默认PT(ms) | 参数来源 | 触发步骤 |
|--------|------|------|-----------|---------|:-------:|
| tFeedTimeout | FB_TON | 入料检测超时 | 3000 | i_iFeedTimeoutMs | S31 |
| tLiftDownTimeout | FB_TON | 气缸下行超时 | 5000 | i_iLiftTimeoutMs | S32 |
| tPickDownTimeout | FB_TON | 取物下降超时 | 3000 | i_iPickTimeoutMs | S33 |
| tClampPickConfirm | FB_TON | 夹取确认等待 | 500 | i_iClampConfirmMs | S34 |
| tPickUpTimeout | FB_TON | 取物上升超时 | 3000 | i_iPickTimeoutMs | S35 |
| tMotorFwdTimeout | FB_TON | 电机正转超时 | 5000 | i_iMotorTimeoutMs | S36 |
| tPlaceDownTimeout | FB_TON | 放物下降超时 | 3000 | i_iPlaceTimeoutMs | S37 |
| tClampPlaceConfirm | FB_TON | 释放确认等待 | 500 | i_iClampConfirmMs | S38 |
| tPlaceUpTimeout | FB_TON | 放物上升超时 | 3000 | i_iPlaceTimeoutMs | S39 |
| tMotorRevTimeout | FB_TON | 电机反转超时 | 5000 | i_iMotorTimeoutMs | S40 |
| tLiftUpTimeout | FB_TON | 气缸上行超时 | 5000 | i_iLiftTimeoutMs | S41 |
| tDonePulse | FB_TON | Done脉冲宽度 | 500 | i_iCycleDonePulseMs | S42 |

> **TON选择理由**: 动作超时需要在到达时产生单次脉冲(Q自动清零前由代码读取并锁存到q_bAlarmx)，TON的自动复位特性适合此场景。TONR仅在需要超时到达后持续保持Q=TRUE的场景使用。

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

## 7. 报警码完整映射表

| 码 | 含义 | 类别 | 触发步骤 | 触发条件 | Alarm位 | Error位 | 恢复方式 |
|:--:|------|:----:|:-------:|----------|:-------:|:-------:|---------|
| 130 | 升降气缸下行超时 | 超时 | S32 | tLiftDownTimer.Q | Alarm0 | Error1 | Reset/手动排除 |
| 131 | 升降气缸上行超时 | 超时 | S41 | tLiftUpTimer.Q | Alarm1 | Error1 | Reset/手动排除 |
| 132 | 取物机构下降超时 | 超时 | S33 | tPickDownTimer.Q | Alarm2 | Error2 | Reset/手动排除 |
| 133 | 取物机构上升超时 | 超时 | S35 | tPickUpTimer.Q | Alarm2 | Error2 | Reset/手动排除 |
| 134 | 取物夹取失败/超时 | 确认 | S34 | tClampPickTimer.Q OR 无确认 | Alarm3 | Error2 | Reset/检查夹具 |
| 135 | 电机正转90度超时 | 超时 | S36 | tMotorFwdTimer.Q | Alarm4 | Error3 | Reset/检查电机 |
| 136 | 电机反转90度超时 | 超时 | S40 | tMotorRevTimer.Q | Alarm4 | Error3 | Reset/检查电机 |
| 137 | 放物机构下降超时 | 超时 | S37 | tPlaceDownTimer.Q | Alarm5 | Error4 | Reset/手动排除 |
| 138 | 放物机构上升超时 | 超时 | S39 | tPlaceUpTimer.Q | Alarm5 | Error4 | Reset/手动排除 |
| 139 | 放物释放失败/超时 | 确认 | S38 | tClampPlaceTimer.Q OR 无确认 | Alarm6 | Error4 | Reset/检查放具 |
| 140 | 入料检测无料/超时 | 检测 | S31 | tFeedTimer.Q + 全部FeedDetect=FALSE | Alarm7 | Error5 | 来料后自动/Reset |
| 141 | 传感器冲突(气缸) | 诊断 | 任意 | ST_Cylinder.SensorFault=ANY | Alarm8 | Error汇总 | 检修传感器 |
| 142 | 电机/VFD故障 | 设备 | S36/S40 | ST_ConveyorMotor.VfdFault=TRUE | Alarm9 | Error3 | 检修VFD/电机 |
| 143 | 急停/安全门触发 | 安全 | 任意 | SafetyDoorOk=FALSE 且 Running | Alarm10 | Error5 | 关安全门/复位 |
| 144 | 上电时气缸非上位 | 预检 | S30 | LiftUpPos=FALSE 且 Idle | 预留 | 预留 | 手动回原点/自动回原 |

## 8. VAR_IN_OUT 结构体使用约定

### 8.1 ST_Cylinder 字段读写权限矩阵

| 字段 | S30 | S32 | S33 | S35 | S37 | S39 | S41 | 手动 |
|------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:----:|
| .Extend (写) | 清 | W | W | - | W | - | - | W |
| .Retract (写) | 清 | - | - | W | - | W | W | W |
| .ExtendedPos (读) | R | R | R | R | R | R | R | R |
| .RetractedPos (读) | R | R | R | R | R | R | R | R |
| .TimeoutMs (写) | - | W | W | W | W | W | W | - |
| .IsExtended (写) | W | W | W | W | W | W | W | - |
| .IsRetracted (写) | W | W | W | W | W | W | W | - |
| .Timeout (读) | R | R | R | R | R | R | R | R |
| .SensorFault (读) | R | R | R | R | R | R | R | R |

> 图例: W=写入, R=只读, -=不访问, 清=强制清零

### 8.2 ST_ConveyorMotor 字段读写权限矩阵

| 字段 | S30 | S36 | S40 | 手动 |
|------|:---:|:---:|:---:|:----:|
| .FwdCmd (写) | 清 | W | - | W |
| .RevCmd (写) | 清 | - | W | W |
| .SafetyDoorOk (读) | R | R | R | R |
| .VfdFault (读) | R | R | R | R |
| .Speed (读) | R | R | R | R |
| .FwdOut (写) | - | W | - | - |
| .RevOut (写) | - | - | W | - |
| .Running (写) | - | W | W | - |
| .VfdAlarm (读) | R | R | R | R |

## 9. LD源程序->SCL重构对照要点

| LD原始特征 | SCL实现方案 | 说明 |
|------------|------------|------|
| 154网络梯形图 | CASE语句13分支+前置处理 | 每个网络对应一个状态的处理逻辑 |
| M0~M10中间位 | q_bM0~q_bM10输出变量 | 作为调试/联锁可见中间状态 |
| NV断电保持位 | q_bNV_Retain1~3输出变量 | OB1负责将此映射到实际NV存储区 |
| 步进器(计数器) | iCurrentStep:INT变量 | INT类型足够覆盖0~12范围 |
| 多个TON定时器 | 12个独立命名FB_TON实例(各自注释应用场景) | 每个定时器独立命名+独立调用+独立注释，语义清晰 |
| 气缸输出(Y线圈) | ST_Cylinder.Extend/Retract + q_bXxx双重输出 | 结构体用于逻辑互锁,q_bXxx用于OB1→IO映射 |
| 电机输出(Y线圈) | ST_ConveyorMotor.FwdCmd/RevCmd + q_bMotorFwd/Rev | 同上 |
| 传感器输入(X触点) | i_bXxx输入变量 + ST_Xxx.ExtendedPos/RetractedPos | 双通道：直接输入+结构体封装 |
| Alarm/Error输出 | q_bAlarm0~10 + q_bError1~5 + q_bError/q_iErrorID | 三层: 原始位/分类汇总/标准PLCopen |

## 10. 关联文档

| 文档 | 路径 | 版本 |
|------|------|:----:|
| IFC | 接口文档_IFC-FB1013-NinetyDegreeTransfer-V7.0.0.md | V7.0.0 |
| 气缸控制 IFC | 接口文档_IFC-FB1011-CylinderControl-V7.0.0.md | V7.0.0 |
| 气缸控制 DSN | 详细设计说明书_DSN-FB1011-CylinderControl-V7.0.0.md | V7.0.0 |
| 电机控制 IFC | 接口文档_IFC-FB1012-ConveyorMotor-V7.0.0.md | V7.0.0 |
| 电机控制 DSN | 详细设计说明书_DSN-FB1012-ConveyorMotor-V7.0.0.md | V7.0.0 |
| 取放料机构 IFC | ../../../../DJ-2026-005/02_PLC程序/通用ST程序及变量表/pickplace/PRD/接口文档_IFC-FB1003-PickPlace-V7.0.0.md | V7.0.0 |
| 取放料机构 DSN | ../../../../DJ-2026-005/02_PLC程序/通用ST程序及变量表/pickplace/PRD/详细设计说明书_DSN-FB1003-PickPlace-V7.0.0.md | V7.0.0 |
| ST_Cylinder类型 | ../../types/ST_Cylinder.scl | V1.1.0 |
| ST_ConveyorMotor类型 | ../../types/ST_ConveyorMotor.scl | V1.1.0 |
| 规范801 | ../../../../../01_需求与设计/10_编程及变量规范/801_PLC变量命名与功能块命名规范_DEV-V1.0.5.md | V1.0.5 |
| 规范905 | ../../../../../01_需求与设计/10_编程及变量规范/905_SCL编程规范_DEV-V7.0.0.md | V7.0.0 |
