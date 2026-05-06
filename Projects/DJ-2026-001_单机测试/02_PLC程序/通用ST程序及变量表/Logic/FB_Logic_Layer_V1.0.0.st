//==============================================================================
// 单机测试 PLC程序 - 业务逻辑层功能块集合
// 版本: V1.0.0
// 遵循规范: IEC 61131-3
// 说明: 逻辑层 - 处理具体工艺逻辑(调用设备层FB,被主控层调用)
//==============================================================================

//==============================================================================
// 功能块: FB_Logic_ServoControl - 伺服控制逻辑(封装设备层)
//==============================================================================
FUNCTION_BLOCK FB_Logic_ServoControl
VAR_INPUT
    i_bEnable : BOOL; i_bHomeReturn : BOOL; i_bPositioning : BOOL;
    i_bJogPlus : BOOL; i_bJogMinus : BOOL; i_rTargetPosition : REAL;
    i_rJogSpeed : REAL; i_rMaxSpeed : REAL; i_rHomeSpeed : REAL;
    i_bAxisFault : BOOL; i_bAxisDone : BOOL;
    i_bHomeSensor : BOOL; i_bLimitFwd : BOOL; i_bLimitRev : BOOL;
END_VAR
VAR_OUTPUT
    o_bServoOn : BOOL; o_bPulseOutput : BOOL; o_bDirectionOutput : BOOL;
    o_bAxisRunning : BOOL; o_bHomeReturnDone : BOOL; o_bPositioningDone : BOOL;
    o_rCurrentSpeed : REAL; o_rCurrentPosition : REAL; o_bFault : BOOL;
END_VAR
VAR fbServoAxis : FB_Device_ServoAxis; END_VAR

fbServoAxis(
    i_bEnable:=i_bEnable, i_bHomeReturn:=i_bHomeReturn, i_bPositioning:=i_bPositioning,
    i_bJogPlus:=i_bJogPlus, i_bJogMinus:=i_bJogMinus, i_rTargetPosition:=i_rTargetPosition,
    i_rJogSpeed:=i_rJogSpeed, i_rMaxSpeed:=i_rMaxSpeed, i_rHomeSpeed:=i_rHomeSpeed,
    i_bAxisFault:=i_bAxisFault, i_bAxisDone:=i_bAxisDone, i_bHomeSensor:=i_bHomeSensor,
    i_bLimitFwd:=i_bLimitFwd, i_bLimitRev:=i_bLimitRev,
    o_bServoOn=>o_bServoOn, o_bPulseOutput=>o_bPulseOutput, o_bDirectionOutput=>o_bDirectionOutput,
    o_bAxisRunning=>o_bAxisRunning, o_bHomeReturnDone=>o_bHomeReturnDone,
    o_bPositioningDone=>o_bPositioningDone, o_rCurrentSpeed=>o_rCurrentSpeed,
    o_rCurrentPosition=>o_rCurrentPosition, o_bFault=>o_bFault);
END_FUNCTION_BLOCK

//==============================================================================
// 功能块: FB_Logic_ConveyorControl - 输送线控制逻辑(封装设备层)
//==============================================================================
FUNCTION_BLOCK FB_Logic_ConveyorControl
VAR_INPUT
    i_bEnable : BOOL; i_bStart : BOOL; i_bStop : BOOL;
    i_bFaultReset : BOOL; i_bForward : BOOL; i_bReverse : BOOL;
    i_bSlow : BOOL; i_bVFD_Fault : BOOL;
END_VAR
VAR_OUTPUT
    o_bForwardOutput : BOOL; o_bReverseOutput : BOOL; o_bSlowOutput : BOOL;
    o_bResetOutput : BOOL; o_bConveyorRunning : BOOL; o_bFault : BOOL;
END_VAR
VAR fbConveyor : FB_Device_Conveyor; END_VAR

fbConveyor(
    i_bEnable:=i_bEnable, i_bStart:=i_bStart, i_bStop:=i_bStop,
    i_bFaultReset:=i_bFaultReset, i_bForward:=i_bForward, i_bReverse:=i_bReverse,
    i_bSlow:=i_bSlow, i_bVFD_Fault:=i_bVFD_Fault,
    o_bForwardOutput=>o_bForwardOutput, o_bReverseOutput=>o_bReverseOutput,
    o_bSlowOutput=>o_bSlowOutput, o_bResetOutput=>o_bResetOutput,
    o_bConveyorRunning=>o_bConveyorRunning, o_bFault=>o_bFault);
END_FUNCTION_BLOCK

//==============================================================================
// 功能块: FB_Logic_SequenceStep - 通用顺序步进逻辑
// 功能: N步顺序控制状态机 (IDLE→STEP1→STEP2→...→STEPN→COMPLETE)
//==============================================================================
FUNCTION_BLOCK FB_Logic_SequenceStep
VAR_INPUT
    i_bEnable        : BOOL;   // 使能
    i_bStart         : BOOL;   // 启动序列
    i_nTotalSteps    : INT;    // 总步数
    i_bStepCondition : BOOL;   // 当前步完成条件
END_VAR
VAR_OUTPUT
    o_nCurrentStep   : INT;    // 当前步骤(0=IDLE, 1-N=执行中, N+1=COMPLETE)
    o_bSequenceDone  : BOOL;   // 序列完成
    o_bBusy          : BOOL;   // 序列运行中
END_VAR
VAR s_eState : INT; END_VAR

CASE s_eState OF
    0: // IDLE
        o_nCurrentStep := 0; o_bSequenceDone := FALSE; o_bBusy := FALSE;
        IF i_bEnable AND i_bStart THEN s_eState := 1; o_bBusy := TRUE; END_IF;
    1..100: // 动态步骤范围
        o_nCurrentStep := s_eState;
        IF i_bStepCondition THEN
            IF s_eState >= i_nTotalSteps THEN
                s_eState := i_nTotalSteps + 1; // 跳到COMPLETE
            ELSE
                s_eState := s_eState + 1;
            END_IF;
        END_IF;
    101: // COMPLETE (最大步数+1)
        o_nCurrentStep := i_nTotalSteps + 1;
        o_bSequenceDone := TRUE; o_bBusy := FALSE;
        IF NOT i_bStart THEN s_eState := 0; END_IF;
END_CASE;
END_FUNCTION_BLOCK