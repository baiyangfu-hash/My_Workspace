# 详细设计说明书 FB_1003_PickPlace_BufferFraming

## 0. 文档基础信息

| 属性 | 值 |
|------|-----|
| **文档标题** | FB_1003 取放料机构详细设计 |
| **文档版本** | V7.0.0 |
| **关联源码** | pickplace/FB_1003_PickPlace_BufferFraming.scl |
| **编制日期** | 2026-05-20 |
| **编制人** | Trae |
| **遵循规范** | 801_DEV-V1.0.5, 810_DEV-V1.0.2, ST_ServoAxis V3.0(PLCopen MC Part 1) |

## 1. 设计原则

1. **6步STL S20~S25**：与源程序完全一致，产品检测在S22步内完成
2. **按层选择放料点**：L1/L3→前放料点D520，L2/L4→后放料点D540
3. **4组夹爪同时动作**：前夹紧/后夹紧/前夹紧2/后夹紧2，全部确认后跳步
4. **V7.0核心变更 - 轴控制直连**：不再通过q_bXxxRequest/q_rTargetPos间接请求轴FB执行，而是通过 `VAR_IN_OUT io_stZAxis/io_stXAxis:ST_ServoAxis` 直接操作 PLCopen MC 标准接口（stPower/stAbs/stStop/stSensor）

## 2. 状态机伪代码 (V7.0.0)

### 2.0 前置处理：使能关闭 / 停止

```
(* 使能关闭: 非自动且非手动 → 全部输出清零 + 轴命令清除 *)
IF NOT i_bAutoMode AND NOT i_bManualMode THEN
    q_bFrontClamp := FALSE; q_bRearClamp := FALSE;     (* 气缸清零 *)
    q_bFrontClamp2 := FALSE; q_bRearClamp2 := FALSE;
    q_bLiftUp := FALSE; q_bLiftDown := FALSE;
    io_stZAxis.stAbs.Execute  := FALSE;                (* V7.0: 轴命令清除 *)
    io_stX1Axis.stAbs.Execute := FALSE;
    io_stZAxis.stStop.Execute  := FALSE;
    io_stX1Axis.stStop.Execute := FALSE;
    q_iAlarmCode := 0; q_bSensorFault := FALSE;       (* 诊断清零 *)
    iCurrentState := S20_IDLE; bRunning := FALSE;
    RETURN;
END_IF;

(* 停止处理: 急停两轴 *)
IF i_bStop AND bRunning THEN
    iCurrentState := S20_IDLE; bRunning := FALSE;
    q_bFrontClamp := FALSE; q_bRearClamp := FALSE;     (* 气缸停止 *)
    ... (* 其余气缸清零 *)
    io_stZAxis.stStop.Execute  := TRUE;               (* V7.0: SV_Stop *)
    io_stX1Axis.stStop.Execute := TRUE;
    io_stZAxis.stAbs.Execute  := FALSE;
    io_stX1Axis.stAbs.Execute := FALSE;
END_IF;
```

### 2.1 模式分发

```
IF i_bAutoMode THEN
    CASE iCurrentState OF        (* 自动模式状态机 *)
        ...
    END_CASE;
ELSIF i_bManualMode THEN
    (* 手动模式: 直接映射按钮→输出，清除轴命令 *)
    ...
ELSE
    (* 关闭模式: 全部清零 *)
END_IF;
```

### 2.2 S20_IDLE — 待机等待

```
S20_IDLE: (* 0 - 待机等待 *)
    IF bStepEntry THEN
        io_stZAxis.stAbs.Execute  := FALSE;          (* 清除残留定位命令 *)
        io_stX1Axis.stAbs.Execute := FALSE;
        q_bPlaceDoneToFeeder := FALSE;
        bStepEntry := FALSE;
    END_IF;

    (* V7.0: SV_Power — 自动模式下确保轴已使能 *)
    IF NOT io_stZAxis.stPower.Status THEN
        io_stZAxis.stPower.Enable := TRUE;            (* Z轴使能 *)
    END_IF;
    IF NOT io_stX1Axis.stPower.Status THEN
        io_stX1Axis.stPower.Enable := TRUE;           (* X1轴使能 *)
    END_IF;

    (* V7.0: 伺服报警检查 (ST_Sensor.ServoAlarm) *)
    IF io_stZAxis.stSensor.ServoAlarm OR io_stX1Axis.stSensor.ServoAlarm THEN
        iAlarmCode := 73;                             (* 报警73: 伺服报警 *)
    END_IF;

    (* 取料平台残留边框检测 → 阻塞启动 *)
    IF i_bFrameDetect1 OR i_bFrameDetect2 THEN
        q_bFrameOnPickupPlatform := TRUE;
        iAlarmCode := 80;                             (* 报警80: 平台有边框 *)
    END_IF;

    (* 启动触发: 上升沿 + 层号有效(1~4) *)
    IF bStartTriggered AND i_iPickLayer > 0 AND i_iPickLayer <= 4 THEN
        iPickLayer := i_iPickLayer;
        bStepEntry := TRUE;
        iCurrentState := S21_UP_TO_PICK;
    END_IF;
```

### 2.3 S21_UP_TO_PICK — Z轴上升到取料高度 (PLCopen MC_MoveAbsolute)

```
S21_UP_TO_PICK: (* 1 - Z→取片教点D514 [SV_Abs] *)
    IF bStepEntry THEN
        (* V7.0: 安全互锁 — 限位检查 (ST_Sensor) *)
        IF io_stZAxis.stSensor.FwdLimit OR io_stZAxis.stSensor.RevLimit THEN
            iAlarmCode := 74;                         (* 报警74: 轴限位 *)
            iCurrentState := S20_IDLE;
            bRunning := FALSE;
        ELSE
            (* V7.0: 绝对定位 — 直接写入轴结构体 *)
            io_stZAxis.stAbs.Position  := rPickHeight;   (* D514 *)
            io_stZAxis.stAbs.Velocity  := i_rZSpeed;     (* 用户设定速度 *)
            io_stZAxis.stAbs.Execute   := TRUE;           (* 启动MC_MoveAbsolute *)

            (* 启动升降超时定时器 *)
            tPt[0] := INT_TO_DINT(i_iLiftActionTime);   (* 或默认3000ms *)
            tIn[0] := TRUE; tR[0] := FALSE;
            bStepEntry := FALSE;
        END_IF;
    END_IF;

    (* 到位判断: 传感器信号 OR PLCopen Done *)
    IF i_bLiftHomePos OR io_stZAxis.stAbs.Done THEN
        tIn[0] := FALSE; tR[0] := TRUE;
        io_stZAxis.stAbs.Execute := FALSE;              (* 停止定位 *)
        bStepEntry := TRUE;
        iCurrentState := S22_CLAMP_AND_DETECT;

    (* 错误判断: 超时 OR 轴错误 *)
    ELSIF tQ[0] OR io_stZAxis.stAbs.Error THEN
        tIn[0] := FALSE; tR[0] := TRUE;
        io_stZAxis.stAbs.Execute := FALSE;
        io_stZAxis.stStop.Execute := TRUE;              (* V7.0: 出错急停 *)
        IF io_stZAxis.stAbs.Error THEN
            iAlarmCode := 75;                           (* 报警75: 轴错误 *)
        ELSE
            iAlarmCode := 71;                           (* 报警71: 升降超时 *)
        END_IF;
        iCurrentState := S20_IDLE;
        bRunning := FALSE;
    END_IF;
```

### 2.4 S22_CLAMP_AND_DETECT — 夹紧与检测

```
S22_CLAMP_AND_DETECT: (* 2 - 四夹紧+四光电检测 *)
    IF bStepEntry THEN
        q_bFrontClamp := TRUE;                         (* 4夹紧同时动作 *)
        q_bRearClamp := TRUE;
        q_bFrontClamp2 := TRUE;
        q_bRearClamp2 := TRUE;
        (* 启动夹紧确认定时器 *)
        tPt[1] := INT_TO_DINT(i_iClampConfirmTime);
        tIn[1] := TRUE; tR[1] := FALSE;
        bStepEntry := FALSE;
    END_IF;

    IF tQ[1] THEN                                      (* 夹紧确认时间到 *)
        tIn[1] := FALSE; tR[1] := TRUE;
        (* 4夹紧全到位? *)
        IF i_bFrontClampClosed AND i_bRearClampClosed
           AND i_bFrontClamp2Closed AND i_bRearClamp2Closed THEN
            (* 4光电全检到? *)
            IF i_bLongEdge1Detect AND i_bLongEdge2Detect
               AND i_bShortEdge1Detect AND i_bShortEdge2Detect THEN
                bStepEntry := TRUE;
                iCurrentState := S23_MOVE_TO_PLACE;      (* → 放料位置 *)
            ELSE
                q_bProductMissing := TRUE;              (* 产品缺失 *)
                iAlarmCode := 72;                        (* 报警72: 检测失败 *)
                iCurrentState := S25_UNCLAMP_AND_NOTIFY;   (* → 松开退出 *)
            END_IF;
        ELSE
            q_bSensorFault := TRUE;                    (* 传感器不一致 *)
            iAlarmCode := 101;                          (* 报警101: 夹紧传感器异常 *)
            iCurrentState := S25_UNCLAMP_AND_NOTIFY;
        END_IF;
    END_IF;
```

### 2.5 S23_MOVE_TO_PLACE — X1轴移动到放料位置 (PLCopen MC_MoveAbsolute)

```
S23_MOVE_TO_PLACE: (* 3 - X1→放料点 [SV_Abs] *)
    IF bStepEntry THEN
        (* V7.0: X1轴限位互锁 (ST_Sensor) *)
        IF io_stX1Axis.stSensor.FwdLimit OR io_stX1Axis.stSensor.RevLimit THEN
            iAlarmCode := 74;
            iCurrentState := S20_IDLE;
        ELSE
            (* V7.0: 按层选放料点 — 直接写io_stX1Axis.stAbs *)
            IF (iPickLayer = 1) OR (iPickLayer = 3) THEN
                io_stX1Axis.stAbs.Position := rPlaceHeightL1;  (* D520 *)
            ELSE
                io_stX1Axis.stAbs.Position := rPlaceHeightL2;  (* D540 *)
            END_IF;
            io_stX1Axis.stAbs.Velocity := i_rX1Speed;
            io_stX1Axis.stAbs.Execute  := TRUE;
            bStepEntry := FALSE;
        END_IF;
    END_IF;

    (* X1到位: 满料检测 OR Done *)
    IF i_bFullMaterialDetect1 OR i_bFullMaterialDetect2 OR io_stX1Axis.stAbs.Done THEN
        io_stX1Axis.stAbs.Execute := FALSE;
        bStepEntry := TRUE;
        iCurrentState := S24_DOWN_TO_PLACE;
    END_IF;
```

### 2.6 S24_DOWN_TO_PLACE — Z轴下降到放料高度 (PLCopen MC_MoveAbsolute)

```
S24_DOWN_TO_PLACE: (* 4 - Z→放片教点D524 [SV_Abs] *)
    IF bStepEntry THEN
        (* V7.0: Z轴限位互锁 *)
        IF io_stZAxis.stSensor.FwdLimit OR io_stZAxis.stSensor.RevLimit THEN
            iAlarmCode := 74;
            iCurrentState := S20_IDLE;
        ELSE
            io_stZAxis.stAbs.Position  := rPlaceDownHeight;  (* D524 *)
            io_stZAxis.stAbs.Velocity  := i_rZSpeed;
            io_stZAxis.stAbs.Execute   := TRUE;
            q_bLiftDown := TRUE;                            (* 下降电磁阀 *)
            q_bLiftUp := FALSE;
            (* 启动超时定时器 *)
            ...
            bStepEntry := FALSE;
        END_IF;
    END_IF;

    (* 到位: 工作点传感器 OR Done *)
    IF i_bLiftWorkPoint OR io_stZAxis.stAbs.Done THEN
        tIn[0] := FALSE; tR[0] := TRUE;
        io_stZAxis.stAbs.Execute := FALSE;
        q_bLiftDown := FALSE;
        bStepEntry := TRUE;
        iCurrentState := S25_UNCLAMP_AND_NOTIFY;

    (* 超时或轴错误 *)
    ELSIF tQ[0] OR io_stZAxis.stAbs.Error THEN
        io_stZAxis.stAbs.Execute := FALSE;
        q_bLiftDown := FALSE;
        io_stZAxis.stStop.Execute := TRUE;                 (* V7.0: 出错急停 *)
        (* 报警71超时 / 75轴错误 *)
        iCurrentState := S20_IDLE;
    END_IF;
```

### 2.7 S25_UNCLAMP_AND_NOTIFY — 松开与通知

```
S25_UNCLAMP_AND_NOTIFY: (* 5 - 四松开+通知FB_1004 *)
    IF bStepEntry THEN
        q_bFrontClamp := FALSE;                        (* 4松开同时动作 *)
        q_bRearClamp := FALSE;
        q_bFrontClamp2 := FALSE;
        q_bRearClamp2 := FALSE;
        tPt[2] := T_PLACE_DONE_PULSE;                   (* 500ms脉冲 *)
        tIn[2] := TRUE; tR[2] := FALSE;
        bStepEntry := FALSE;
    END_IF;

    IF tQ[2] THEN
        tIn[2] := FALSE; tR[2] := TRUE;
        q_bPlaceDoneToFeeder := TRUE;                   (* → FB_1004 *)
        bStepEntry := TRUE;
        iCurrentState := S20_IDLE;
        bRunning := FALSE;
    END_IF;
```

## 3. 手动模式逻辑

```
ELSIF i_bManualMode THEN
    bRunning := FALSE; iCurrentState := S20_IDLE;

    (* 直接映射: 按钮→输出 *)
    IF i_bLx_FrontClamp THEN q_bFrontClamp := TRUE;
    ELSE q_bFrontClamp := FALSE; END_IF;
    (* 后夹紧/前2/后2 同理... *)

    (* 升降互锁 *)
    IF i_bLx_LiftUp AND NOT i_bLx_LiftDown THEN
        q_bLiftUp := TRUE; q_bLiftDown := FALSE;
    ELSIF i_bLx_LiftDown AND NOT i_bLx_LiftUp THEN
        q_bLiftDown := TRUE; q_bLiftUp := FALSE;
    ELSE
        q_bLiftUp := FALSE; q_bLiftDown := FALSE;
    END_IF;

    (* V7.0: 手动模式下也清除轴命令 *)
    io_stZAxis.stAbs.Execute  := FALSE;
    io_stX1Axis.stAbs.Execute := FALSE;
END_IF;
```

## 4. 报警码完整表

| 码 | 含义 | 触发步骤 | 触发条件 |
|:--:|------|:-------:|----------|
| 71 | 升降动作超时 | S21/S24 | tLiftTimer.Q |
| 72 | 产品检测失败(取料空) | S22 | 4光电未全ON(夹紧确认后) |
| 73 | 伺服驱动器报警 | S20 | stSensor.ServoAlarm=TRUE(Z或X1) |
| 74 | 轴限位触发 | S21/S23/S24 | FwdLimit OR RevLimit |
| 75 | 轴定位错误(MC_Error) | S21/S24 | stAbs.Error=TRUE |
| 80 | 取料平台有边框(阻塞) | S20 | FrameDetect1 OR FrameDetect2 |
| 101 | 夹紧传感器冗余不一致 | S22 | 夹紧位信号矛盾 |

## 5. 定时器配置

| 定时器 | 用途 | 默认值(ms) | 参数来源 |
|--------|------|-----------|---------|
| tLiftTimer (TONR) | 升降动作超时 | 3000 | i_iLiftActionTime 或 T_LIFT_DEFAULT |
| tClampTimer (TONR) | 夹紧确认等待 | 800 | i_iClampConfirmTime 或 T_CLAMP_DEFAULT |
| tPlaceDoneTimer (TONR) | 放料完成脉冲宽度 | 500 | T_PLACE_DONE_PULSE (常量) |

## 6. 教点参数表

| 参数名 | 值(mm) | 说明 |
|--------|:-----:|------|
| rPickHeight | 514.0 | D514 取片教点(Z轴上升目标) |
| rPlaceHeightL1 | 520.0 | D520 L1/L3放片教点(X1轴横移目标) |
| rPlaceHeightL2 | 540.0 | D540 L2/L4放片教点(X1轴横移目标) |
| rPlaceDownHeight | 524.0 | D524 放片教点(Z轴下降目标) |

## 7. V6.0→V7.0 架构差异对照

| 维度 | V6.0 (间接请求模式) | V7.0 (VAR_IN_OUT直连模式) |
|------|---------------------|----------------------------|
| **轴控制方式** | FB输出q_bZxxReq → OB1转发→外部轴FB执行 | FB内直接写io_stZAxis.stAbs.Execute |
| **轴状态读取** | 通过输入i_bZxxxInPos等传感器信号 | 直接读io_stZAxis.stAbs.Done/.Error/.Busy |
| **使能控制** | 外部轴FB管理 | FB内写io_stZAxis.stPower.Enable |
| **急停控制** | 外部轴FB管理 | FB内写io_stZAxis.stStop.Execute |
| **限位互锁** | OB1层面检查 | FB内检查io_stZAxis.stSensor.FwdLimit/.RevLimit |
| **接口数量** | VAR_IN:42 + VAR_OUT:22 = 64 | VAR_IN:38 + VAR_OUT:16 + VAR_IN_OUT:2 = 56 |
| **OB1复杂度** | 高(需处理6个轴请求信号的转发) | 低(VAR_IN_OUT直接传引用) |
| **可测试性** | 低(LSP值拷贝限制) | 中(轴结构体仍为值拷贝，但可通过o_iCurrentState间接验证) |

## 8. 关联文档

| 文档 | 路径 | 版本 |
|------|------|:----:|
| IFC | 接口文档_IFC-FB1003-PickPlace-V7.0.0.md | V7.0.0 |
| CHG | 变更记录_CHG-FB1003-PickPlace-V7.0.0.md | V7.0.0 |
| UM | 使用说明_UM-FB1003-PickPlace-V6.0.0.md | V6.0.0 |
| DB1 | GlobalVars.db (stPickPlace结构体) | V7.1.1 |
