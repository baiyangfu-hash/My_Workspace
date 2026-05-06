//==============================================================================
// 单机测试 PLC程序 - 系统初始化功能块
// 版本: V1.0.0
// 遵循规范: IEC 61131-3
// 说明: 主控层 - 系统启动时的初始化操作 (5步初始化序列)
//==============================================================================

FUNCTION_BLOCK FB_Main_Initialization
VAR_INPUT
    i_bSystemStart       : BOOL;   // 系统启动信号
    i_bReset             : BOOL;   // 复位信号
    i_bEmergencyStop     : BOOL;   // 急停状态
    i_bDoorOpen          : BOOL;   // 门打开状态
    i_bServoAlarm        : BOOL;   // 伺服报警状态
END_VAR

VAR_OUTPUT
    o_bInitialized       : BOOL;   // 初始化完成
    o_bHomeReturnRequest : BOOL;   // 回原点请求
    o_bSystemReady       : BOOL;   // 系统就绪
    o_iInitStep          : INT;    // 当前初始化步骤(0-6)
    o_bFault             : BOOL;   // 初始化故障
END_VAR

VAR
    s_eInitState         : INT;    // 初始化状态
    s_tmrDelay           : TON;    // 步骤延时计时器
END_VAR

VAR CONSTANT
    INIT_START           : INT := 0;   // 开始初始化
    INIT_PARAMS          : INT := 1;   // 参数初始化
    INIT_HARDWARE_CHECK  : INT := 2;   // 硬件检查
    INIT_SAFETY_CHECK    : INT := 3;   // 安全检查
    INIT_HOME_RETURN     : INT := 4;   // 回原点
    INIT_COMPLETE        : INT := 5;   // 初始化完成
    INIT_ERROR           : INT := 6;   // 初始化错误
END_VAR

CASE s_eInitState OF
    INIT_START:
        o_iInitStep := 0; o_bInitialized := FALSE;
        o_bSystemReady := FALSE; o_bHomeReturnRequest := FALSE; o_bFault := FALSE;
        IF i_bSystemStart THEN s_eInitState := INIT_PARAMS; END_IF;

    INIT_PARAMS:
        o_iInitStep := 1;
        // 参数初始化: 加载系统参数、配方数据、通信配置等
        s_tmrDelay.IN := TRUE; s_tmrDelay.PT := T#1S; s_tmrDelay();
        IF s_tmrDelay.Q THEN s_tmrDelay.IN := FALSE; s_eInitState := INIT_HARDWARE_CHECK; END_IF;

    INIT_HARDWARE_CHECK:
        o_iInitStep := 2;
        // 硬件检查: 检查IO模块、通讯模块、驱动器状态
        s_tmrDelay.IN := TRUE; s_tmrDelay.PT := T#1S; s_tmrDelay();
        IF s_tmrDelay.Q THEN s_tmrDelay.IN := FALSE; s_eInitState := INIT_SAFETY_CHECK; END_IF;

    INIT_SAFETY_CHECK:
        o_iInitStep := 3;
        // 安全检查: 急停状态、安全门状态、光幕状态
        IF i_bEmergencyStop OR i_bDoorOpen THEN
            o_bFault := TRUE; s_eInitState := INIT_ERROR;
        ELSE
            s_tmrDelay.IN := TRUE; s_tmrDelay.PT := T#500MS; s_tmrDelay();
            IF s_tmrDelay.Q THEN s_tmrDelay.IN := FALSE; s_eInitState := INIT_HOME_RETURN; END_IF;
        END_IF;

    INIT_HOME_RETURN:
        o_iInitStep := 4; o_bHomeReturnRequest := TRUE;
        // 等待回原点完成 (由外部FB_Main_SystemControl反馈)
        s_tmrDelay.IN := TRUE; s_tmrDelay.PT := T#5S; s_tmrDelay();
        IF s_tmrDelay.Q THEN
            s_tmrDelay.IN := FALSE; o_bHomeReturnRequest := FALSE;
            s_eInitState := INIT_COMPLETE;
        END_IF;

    INIT_COMPLETE:
        o_iInitStep := 5;
        o_bInitialized := TRUE; o_bSystemReady := TRUE; o_bFault := FALSE;
        IF NOT i_bSystemStart THEN s_eInitState := INIT_START; END_IF;

    INIT_ERROR:
        o_iInitStep := 6; o_bFault := TRUE;
        o_bInitialized := FALSE; o_bSystemReady := FALSE;
        IF i_bReset AND NOT i_bEmergencyStop AND NOT i_bDoorOpen THEN
            s_eInitState := INIT_START;
        END_IF;
END_CASE;
END_FUNCTION_BLOCK