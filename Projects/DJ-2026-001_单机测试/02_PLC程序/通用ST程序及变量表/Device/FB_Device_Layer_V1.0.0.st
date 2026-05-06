//==============================================================================
// 单机测试 PLC程序 - 设备层功能块集合
// 版本: V1.0.0
// 遵循规范: IEC 61131-3
// 说明: 设备层 - 直接与硬件交互的功能块(伺服轴/输送线/气缸/安全/传感器)
//==============================================================================

//==============================================================================
// 功能块: FB_Device_ServoAxis - 伺服轴设备控制
// 功能: 单个伺服轴的底层控制(回原点/定位/JOG)
//==============================================================================
FUNCTION_BLOCK FB_Device_ServoAxis
VAR_INPUT
    i_bEnable            : BOOL;   // 轴使能
    i_bHomeReturn        : BOOL;   // 回原点请求
    i_bPositioning       : BOOL;   // 定位请求
    i_bJogPlus           : BOOL;   // JOG+
    i_bJogMinus          : BOOL;   // JOG-
    i_rTargetPosition    : REAL;   // 目标位置(脉冲)
    i_rJogSpeed          : REAL;   // JOG速度
    i_rMaxSpeed          : REAL;   // 最高速度
    i_rHomeSpeed         : REAL;   // 回原点速度
    i_bAxisFault         : BOOL;   // 轴故障
    i_bAxisDone          : BOOL;   // 轴完成信号
    i_bHomeSensor        : BOOL;   // 原点传感器
    i_bLimitFwd          : BOOL;   // 正向限位
    i_bLimitRev          : BOOL;   // 反向限位
END_VAR

VAR_OUTPUT
    o_bServoOn           : BOOL;   // 伺服使能输出
    o_bPulseOutput       : BOOL;   // 脉冲输出
    o_bDirectionOutput   : BOOL;   // 方向输出
    o_bAxisRunning       : BOOL;   // 轴运行中
    o_bHomeReturnDone    : BOOL;   // 回原点完成
    o_bPositioningDone   : BOOL;   // 定位完成
    o_rCurrentSpeed      : REAL;   // 当前速度
    o_rCurrentPosition   : REAL;   // 当前位置
    o_bFault             : BOOL;   // 轴故障
END_VAR

VAR
    s_eAxisState         : INT;    // 轴状态
    s_rSpeedRef          : REAL;   // 速度参考值
    s_bHomeComplete      : BOOL;   // 回原点完成标志
    s_tmrHomeDelay       : TON;    // 回原点延时
END_VAR

VAR CONSTANT
    AXIS_IDLE            : INT := 0;   // 空闲
    AXIS_HOMING          : INT := 1;   // 回原点中
    AXIS_POSITIONING     : INT := 2;   // 定位中
    AXIS_JOGGING         : INT := 3;   // JOG中
    AXIS_FAULT           : INT := 4;   // 故障
END_VAR

// 主逻辑: 4态状态机(IDLE/HOMING/POSITIONING/JOGGING/FAULT)
IF i_bAxisFault OR i_bLimitFwd OR i_bLimitRev THEN
    s_eAxisState := AXIS_FAULT;
    o_bFault := TRUE;
    o_bServoOn := FALSE;
    RETURN;
END_IF;

CASE s_eAxisState OF
    AXIS_IDLE:
        o_bAxisRunning := FALSE;
        o_bHomeReturnDone := s_bHomeComplete;
        o_bServoOn := i_bEnable;
        IF i_bEnable THEN
            IF i_bHomeReturn THEN s_eAxisState := AXIS_HOMING;
            ELSIF i_bPositioning THEN s_eAxisState := AXIS_POSITIONING;
            ELSIF i_bJogPlus OR i_bJogMinus THEN s_eAxisState := AXIS_JOGGING;
            END_IF;
        END_IF;
    AXIS_HOMING:
        o_bAxisRunning := TRUE;
        o_bServoOn := TRUE;
        IF i_bHomeSensor THEN
            s_bHomeComplete := TRUE;
            o_bHomeReturnDone := TRUE;
            s_eAxisState := AXIS_IDLE;
        END_IF;
    AXIS_POSITIONING:
        o_bAxisRunning := TRUE;
        o_bServoOn := TRUE;
        IF i_bAxisDone THEN
            o_bPositioningDone := TRUE;
            s_eAxisState := AXIS_IDLE;
        END_IF;
    AXIS_JOGGING:
        o_bAxisRunning := TRUE;
        o_bServoOn := TRUE;
        IF i_bJogPlus THEN s_rSpeedRef := i_rJogSpeed;
        ELSIF i_bJogMinus THEN s_rSpeedRef := -i_rJogSpeed;
        ELSE s_eAxisState := AXIS_IDLE;
        END_IF;
    AXIS_FAULT:
        o_bAxisRunning := FALSE;
        o_bServoOn := FALSE;
        IF NOT i_bAxisFault AND NOT i_bLimitFwd AND NOT i_bLimitRev THEN
            o_bFault := FALSE;
            s_eAxisState := AXIS_IDLE;
        END_IF;
END_CASE;

o_rCurrentSpeed := s_rSpeedRef;
END_FUNCTION_BLOCK

//==============================================================================
// 功能块: FB_Device_Conveyor - 输送线设备控制
// 功能: 单个输送线的底层控制(正转/反转/慢速)
//==============================================================================
FUNCTION_BLOCK FB_Device_Conveyor
VAR_INPUT
    i_bEnable            : BOOL;   // 使能信号
    i_bStart             : BOOL;   // 启动信号
    i_bStop              : BOOL;   // 停止信号
    i_bFaultReset        : BOOL;   // 故障复位
    i_bForward           : BOOL;   // 正转请求
    i_bReverse           : BOOL;   // 反转请求
    i_bSlow              : BOOL;   // 慢速请求
    i_bVFD_Fault         : BOOL;   // 变频器故障
END_VAR

VAR_OUTPUT
    o_bForwardOutput     : BOOL;   // 正转输出
    o_bReverseOutput     : BOOL;   // 反转输出
    o_bSlowOutput        : BOOL;   // 慢速输出
    o_bResetOutput       : BOOL;   // 复位输出
    o_bConveyorRunning   : BOOL;   // 输送线运行中
    o_bFault             : BOOL;   // 故障状态
END_VAR

VAR
    s_eConveyorState     : INT;    // 输送线状态
    s_tmrReset           : TON;    // 复位计时器
END_VAR

VAR CONSTANT
    CONV_STOP            : INT := 0;
    CONV_FORWARD         : INT := 1;
    CONV_REVERSE         : INT := 2;
END_VAR

IF i_bVFD_Fault THEN s_eConveyorState := CONV_STOP; o_bFault := TRUE; END_IF;
CASE s_eConveyorState OF
    CONV_STOP:
        o_bConveyorRunning := FALSE;
        IF i_bEnable AND NOT o_bFault AND i_bStart THEN
            s_eConveyorState := CONV_FORWARD IF i_bForward ELSE CONV_REVERSE;
        END_IF;
    CONV_FORWARD:
        o_bConveyorRunning := TRUE;
        o_bForwardOutput := TRUE; o_bSlowOutput := i_bSlow;
        IF i_bStop OR NOT i_bEnable OR o_bFault THEN s_eConveyorState := CONV_STOP; END_IF;
    CONV_REVERSE:
        o_bConveyorRunning := TRUE;
        o_bReverseOutput := TRUE; o_bSlowOutput := i_bSlow;
        IF i_bStop OR NOT i_bEnable OR o_bFault THEN s_eConveyorState := CONV_STOP; END_IF;
END_CASE;
END_FUNCTION_BLOCK

//==============================================================================
// 功能块: FB_Device_Cylinder - 气缸设备控制
// 功能: 单个气缸的底层控制(伸出/缩回/超时保护)
//==============================================================================
FUNCTION_BLOCK FB_Device_Cylinder
VAR_INPUT
    i_bEnable            : BOOL;   // 使能信号
    i_bExtend            : BOOL;   // 伸出请求
    i_bRetract           : BOOL;   // 缩回请求
    i_bExtendSensor      : BOOL;   // 伸出限位传感器
    i_bRetractSensor     : BOOL;   // 缩回限位传感器
END_VAR

VAR_OUTPUT
    o_bExtendOutput      : BOOL;   // 伸出输出
    o_bRetractOutput     : BOOL;   // 缩回输出
    o_bExtendDone        : BOOL;   // 伸出完成
    o_bRetractDone       : BOOL;   // 缩回完成
    o_bFault             : BOOL;   // 故障(超时)
END_VAR

VAR
    s_eCylinderState     : INT;    // 气缸状态(5态:IDLE/EXTENDING/EXTENDED/RETRACTING/RETRACTED/FAULT)
    s_tmrTimeout         : TON;    // 超时计时器(默认5S)
END_VAR

// 5态状态机 + 超时保护逻辑
CASE s_eCylinderState OF
    0: // IDLE
        IF i_bEnable AND (i_bExtend OR i_bRetract) THEN
            s_eCylinderState := 1 IF i_bExtend ELSE 3;
            s_tmrTimeout.IN := TRUE; s_tmrTimeout.PT := T#5S;
        END_IF;
    1: // EXTENDING
        o_bExtendOutput := TRUE;
        IF i_bExtendSensor THEN o_bExtendDone := TRUE; s_eCylinderState := 2;
        ELSIF s_tmrTimeout.Q THEN o_bFault := TRUE; s_eCylinderState := 5;
        END_IF;
    2: // EXTENDED
        o_bExtendOutput := TRUE;
        IF i_bRetract THEN s_eCylinderState := 3; s_tmrTimeout.IN := TRUE; s_tmrTimeout.PT := T#5S; END_IF;
    3: // RETRACTING
        o_bRetractOutput := TRUE;
        IF i_bRetractSensor THEN o_bRetractDone := TRUE; s_eCylinderState := 4;
        ELSIF s_tmrTimeout.Q THEN o_bFault := TRUE; s_eCylinderState := 5;
        END_IF;
    4: // RETRACTED
        o_bRetractOutput := TRUE;
        IF i_bExtend THEN s_eCylinderState := 1; s_tmrTimeout.IN := TRUE; s_tmrTimeout.PT := T#5S; END_IF;
    5: // FAULT
        IF NOT i_bEnable THEN o_bFault := FALSE; s_eCylinderState := 0; END_IF;
END_CASE;
END_FUNCTION_BLOCK

//==============================================================================
// 功能块: FB_Device_Safety - 安全设备控制
// 功能: 安全系统的底层控制(急停/安全门/安全继电器)
//==============================================================================
FUNCTION_BLOCK FB_Device_Safety
VAR_INPUT
    i_bEmergencyStop     : BOOL;   // 急停按钮(常闭)
    i_bFrontDoorLock     : BOOL;   // 前安全门锁定
    i_bRearDoorLock      : BOOL;   // 后安全门锁定
    i_bLeftDoor1Status   : BOOL;   // 左侧门1状态
    i_bLeftDoor2Status   : BOOL;   // 左侧门2状态
    i_bRightDoor1Status  : BOOL;   // 右侧门1状态
    i_bRightDoor2Status  : BOOL;   // 右侧门2状态
END_VAR

VAR_OUTPUT
    o_bSafetyRelayStart  : BOOL;   // 安全继电器启动
    o_bEmergencyStop     : BOOL;   // 急停状态(有效=TRUE)
    o_bDoorOpen          : BOOL;   // 门打开状态
    o_bSafetyFault       : BOOL;   // 安全故障
END_VAR

o_bEmergencyStop := NOT i_bEmergencyStop;
o_bDoorOpen := NOT (i_bFrontDoorLock AND i_bRearDoorLock AND i_bLeftDoor1Status AND i_bLeftDoor2Status AND i_bRightDoor1Status AND i_bRightDoor2Status);
o_bSafetyFault := o_bEmergencyStop OR o_bDoorOpen;
o_bSafetyRelayStart := NOT o_bSafetyFault;
END_FUNCTION_BLOCK