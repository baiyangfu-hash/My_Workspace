//==============================================================================
// 单机测试 PLC程序 - 主程序 (OB1)
// 版本: V1.0.0
// 遵循规范: IEC 61131-3
// 说明: Device-Logic-Main三层架构主程序 - 系统集成与协调
//==============================================================================

PROGRAM MainProgram

// ===== 功能块实例声明 =====
VAR
    // 设备层功能块实例
    fbIOMapping         : FB_Device_IOMapping;      // IO映射
    fbServoAxis1        : FB_Device_ServoAxis;       // 伺服轴1(预留)
    fbServoAxis2        : FB_Device_ServoAxis;       // 伺服轴2(预留)
    fbConveyor1         : FB_Device_Conveyor;        // 输送线1(预留)
    fbCylinder1         : FB_Device_Cylinder;        // 气缸1(预留)
    fbSafety            : FB_Device_Safety;          // 安全系统
    
    // 逻辑层功能块实例
    fbServoControl1     : FB_Logic_ServoControl;     // 伺服控制1(封装)
    fbConveyorControl1  : FB_Logic_ConveyorControl;  // 输送线控制1(封装)
    
    // 主控层功能块实例
    fbSystemControl     : FB_Main_SystemControl;     // 系统主控
    fbSafetyManager     : FB_Main_SafetyManager;     // 安全管理
    fbAlarmManager      : FB_Main_AlarmManager;      // 报警管理
    fbInitialization    : FB_Main_Initialization;   // 初始化
END_VAR

// ===== 中间变量 =====
VAR
    // IO映射中间变量
    HomeSensor1         : BOOL;
    HomeSensor2         : BOOL;
    LimitFwd1           : BOOL;
    EStop_Button        : BOOL;
    Reset_Button_Input  : BOOL;
    SafetyFault         : BOOL;
    EmergencyStop       : BOOL;
    
    // 系统状态中间变量
    SystemReady         : BOOL;
    SystemRunning       : BOOL;
    AutoRunning         : BOOL;
    ManualRunning       : BOOL;
    SystemFault         : BOOL;
    AlarmActive         : BOOL;
    DeviceStatus        : INT;
    HomeReturnDone      : BOOL;
    HomeReturnRequest   : BOOL;
    
    // 初始化状态
    Initialized         : BOOL;
    InitStep            : INT;
    InitFault           : BOOL;
END_VAR

//==============================================================================
// 主程序逻辑 (OB1 - 每扫描周期执行)
//==============================================================================

// Step 1: IO映射 (设备层)
fbIOMapping(
    i_X0 := X0, i_X1 := X1, i_X2 := X2, i_X3 := X3,
    i_X14 := X14, i_X15 := X15, i_X16 := X16, i_X17 := X17,
    o_HomeSensor1 => HomeSensor1, o_HomeSensor2 => HomeSensor2,
    o_LimitFwd1 => LimitFwd1, o_EStop_Button => EStop_Button,
    o_Reset_Button => Reset_Button_Input, o_SafetyFault => SafetyFault
);

// Step 2: 系统初始化 (主控层 - 首次启动或复位时执行)
fbInitialization(
    i_bSystemStart := TRUE,
    i_bReset := Reset_Button_Input,
    i_bEmergencyStop := EStop_Button,
    i_bDoorOpen := ,  // 连接安全门状态
    i_bServoAlarm := ,  // 连接伺服报警
    o_bInitialized => Initialized,
    o_bHomeReturnRequest => HomeReturnRequest,
    o_bSystemReady => SystemReady,
    o_iInitStep => InitStep,
    o_bFault => InitFault
);

// Step 3: 安全管理 (主控层 - 最高优先级)
fbSafetyManager(
    i_bEmergencyStop := EStop_Button,
    i_bResetButton := Reset_Button_Input,
    i_bFrontDoorLock := ,  // 前安全门锁定信号
    i_bRearDoorLock := ,   // 后安全门锁定信号
    i_bServoAlarm := ,     // 伺服报警综合
    o_bSystemFault => SystemFault,
    o_bEmergencyStop => EmergencyStop
);

// Step 4: 报警管理 (主控层)
fbAlarmManager(
    i_bSystemFault := SystemFault,
    i_bEmergencyStop := EmergencyStop,
    i_bDoorOpen := ,  // 门打开状态
    i_bServoAlarm := ,
    i_bVFD_Fault := FALSE,
    i_bResetButton := Reset_Button_Input
);

// Step 5: 系统主控 (主控层 - 7态状态机)
fbSystemControl(
    i_bEnable := SystemReady,
    i_bManualMode := ManualMode,    // 来自HMI/按钮
    i_bAutoMode := AutoMode,        // 来自HMI/按钮
    i_bStartButton := StartButton,
    i_bStopButton := StopButton,
    i_bResetButton := Reset_Button_Input,
    i_bSystemFault := SystemFault,
    i_bHomeReturnDone := HomeReturnDone,
    o_bSystemRunning => SystemRunning,
    o_bAutoRunning => AutoRunning,
    o_bManualRunning => ManualRunning,
    o_bHomeReturnRequest => HomeReturnRequest,
    o_iDeviceStatus => DeviceStatus
);

// Step 6: 状态输出到物理输出
Y0 := SystemRunning;          // 运行指示灯(绿)
Y1 := SystemFault OR AlarmActive; // 故障指示灯(红)
Y2 := SystemRunning;          // 系统运行输出

// Step 7: 伺服轴控制示例 (根据实际设备添加)
(*
fbServoControl1(
    i_bEnable := SystemReady,
    i_bHomeReturn := HomeReturnRequest,
    ...
);
*)

END_PROGRAM