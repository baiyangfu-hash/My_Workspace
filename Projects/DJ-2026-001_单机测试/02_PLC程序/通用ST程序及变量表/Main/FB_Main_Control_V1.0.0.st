//==============================================================================
// 单机测试 PLC程序 - 主控层功能块集合
// 版本: V1.0.0
// 遵循规范: IEC 61131-3
// 说明: 主控层 - 系统协调与调度(系统状态机/安全管理/报警管理)
//==============================================================================

//==============================================================================
// 功能块: FB_Main_SystemControl - 系统主控 (7态状态机)
// 状态: IDLE→HOME_RETURN→READY→AUTO/MANUAL→STOP→FAULT
//==============================================================================
FUNCTION_BLOCK FB_Main_SystemControl
VAR_INPUT
    i_bEnable            : BOOL;   // 系统使能
    i_bManualMode        : BOOL;   // 手动模式
    i_bAutoMode          : BOOL;   // 自动模式
    i_bStartButton       : BOOL;   // 启动按钮
    i_bStopButton        : BOOL;   // 停止按钮
    i_bResetButton       : BOOL;   // 复位按钮
    i_bSystemFault       : BOOL;   // 系统故障
    i_bHomeReturnDone    : BOOL;   // 回原点完成
END_VAR

VAR_OUTPUT
    o_bSystemRunning     : BOOL;   // 系统运行中
    o_bAutoRunning       : BOOL;   // 自动运行中
    o_bManualRunning     : BOOL;   // 手动运行中
    o_bHomeReturnRequest : BOOL;   // 回原点请求
    o_iDeviceStatus      : INT;    // 设备状态码
END_VAR

VAR
    s_eSystemState       : INT;    // 系统状态
END_VAR

VAR CONSTANT
    SYS_IDLE             : INT := 0;
    SYS_HOME_RETURN      : INT := 1;
    SYS_READY            : INT := 2;
    SYS_AUTO_RUNNING     : INT := 3;
    SYS_MANUAL_RUNNING   : INT := 4;
    SYS_STOP             : INT := 5;
    SYS_FAULT            : INT := 6;
END_VAR

// 故障优先处理
IF i_bSystemFault THEN s_eSystemState := SYS_FAULT; o_iDeviceStatus := 6; RETURN; END_IF;

CASE s_eSystemState OF
    SYS_IDLE:
        o_bSystemRunning := FALSE; o_iDeviceStatus := 0;
        IF i_bEnable THEN s_eSystemState := SYS_HOME_RETURN; END_IF;
    SYS_HOME_RETURN:
        o_bHomeReturnRequest := TRUE; o_iDeviceStatus := 1;
        IF i_bHomeReturnDone THEN o_bHomeReturnRequest := FALSE; s_eSystemState := SYS_READY; END_IF;
    SYS_READY:
        o_bSystemRunning := TRUE; o_iDeviceStatus := 2;
        IF i_bManualMode THEN s_eSystemState := SYS_MANUAL_RUNNING;
        ELSIF i_bAutoMode AND i_bStartButton THEN s_eSystemState := SYS_AUTO_RUNNING; END_IF;
    SYS_AUTO_RUNNING:
        o_bSystemRunning := TRUE; o_bAutoRunning := TRUE; o_iDeviceStatus := 3;
        // 此处添加自动运行序列逻辑
    SYS_MANUAL_RUNNING:
        o_bSystemRunning := TRUE; o_bManualRunning := TRUE; o_iDeviceStatus := 4;
        // 手动模式下由HMI直接控制各机构
    SYS_STOP:
        o_bSystemRunning := FALSE; o_iDeviceStatus := 5;
        IF NOT i_bStopButton THEN s_eSystemState := SYS_IDLE; END_IF;
    SYS_FAULT:
        o_bSystemRunning := FALSE; o_iDeviceStatus := 6;
        IF i_bResetButton AND NOT i_bSystemFault THEN s_eSystemState := SYS_IDLE; END_IF;
END_CASE;
END_FUNCTION_BLOCK

//==============================================================================
// 功能块: FB_Main_SafetyManager - 安全管理
//==============================================================================
FUNCTION_BLOCK FB_Main_SafetyManager
VAR_INPUT
    i_bEmergencyStop     : BOOL; i_bResetButton : BOOL;
    i_bFrontDoorLock     : BOOL; i_bRearDoorLock : BOOL;
    i_bServoAlarm        : BOOL;
END_VAR
VAR_OUTPUT
    o_bSystemFault       : BOOL; o_bEmergencyStop : BOOL;
    o_bServoAlarm        : BOOL;
END_VAR
VAR fbSafety : FB_Device_Safety; s_tmrResetDelay : TON; END_VAR

fbSafety(i_bEmergencyStop:=i_bEmergencyStop, i_bFrontDoorLock:=i_bFrontDoorLock,
         i_bRearDoorLock:=i_bRearDoorLock, o_bEmergencyStop=>o_bEmergencyStop,
         o_bSafetyFault=>o_bSystemFault);
o_bServoAlarm := i_bServoAlarm;
o_bSystemFault := o_bSystemFault OR o_bServoAlarm;

IF i_bResetButton THEN
    s_tmrResetDelay.IN := TRUE; s_tmrResetDelay.PT := T#2S; s_tmrResetDelay();
    IF s_tmrResetDelay.Q THEN
        IF NOT o_bEmergencyStop AND NOT o_bServoAlarm THEN o_bSystemFault := FALSE; END_IF
        s_tmrResetDelay.IN := FALSE;
    END_IF;
END_IF;
END_FUNCTION_BLOCK

//==============================================================================
// 功能块: FB_Main_AlarmManager - 报警管理
//==============================================================================
FUNCTION_BLOCK FB_Main_AlarmManager
VAR_INPUT
    i_bSystemFault : BOOL; i_bEmergencyStop : BOOL; i_bDoorOpen : BOOL;
    i_bServoAlarm : BOOL; i_bVFD_Fault : BOOL; i_bResetButton : BOOL;
END_VAR
VAR_OUTPUT
    o_iAlarmCode : INT; o_bAlarmActive : BOOL;
    o_bBuzzerOutput : BOOL; o_bRedIndicator : BOOL; o_bGreenIndicator : BOOL;
END_VAR
VAR s_tmrBuzzer : TON; END_VAR

IF i_bEmergencyStop THEN o_iAlarmCode := 1000;
ELSIF i_bDoorOpen THEN o_iAlarmCode := 1001;
ELSIF i_bServoAlarm THEN o_iAlarmCode := 2001;
ELSIF i_bVFD_Fault THEN o_iAlarmCode := 2004;
ELSE o_iAlarmCode := 0; END_IF;

o_bAlarmActive := (o_iAlarmCode <> 0);
IF o_bAlarmActive THEN o_bRedIndicator := TRUE; o_bGreenIndicator := FALSE;
ELSE o_bRedIndicator := FALSE; o_bGreenIndicator := TRUE; END_IF;

IF o_bAlarmActive THEN s_tmrBuzzer.IN := TRUE; s_tmrBuzzer.PT := T#1S; s_tmrBuzzer();
    IF s_tmrBuzzer.Q THEN o_bBuzzerOutput := NOT o_bBuzzerOutput; s_tmrBuzzer.IN := FALSE; END_IF;
ELSE o_bBuzzerOutput := FALSE; END_IF

IF i_bResetButton AND o_bAlarmActive THEN
    IF NOT i_bEmergencyStop AND NOT i_bDoorOpen AND NOT i_bServoAlarm THEN
        o_iAlarmCode := 0; o_bAlarmActive := FALSE;
    END_IF;
END_IF;
END_FUNCTION_BLOCK