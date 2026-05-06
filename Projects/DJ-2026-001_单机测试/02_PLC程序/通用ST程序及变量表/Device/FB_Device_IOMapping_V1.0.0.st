//==============================================================================
// 单机测试 PLC程序 - IO映射功能块
// 版本: V1.0.0
// 遵循规范: IEC 61131-3
// 说明: 设备层 - 物理IO与符号变量的映射管理
//==============================================================================

FUNCTION_BLOCK FB_Device_IOMapping
VAR_INPUT
    // ===== CPU本体输入 (X0-X17) =====
    i_X0                : BOOL;   // 原点传感器1(如Z轴)
    i_X1                : BOOL;   // 原点传感器2(如X1轴)
    i_X2                : BOOL;   // 原点传感器3(如X2轴)
    i_X3                : BOOL;   // 正向限位1
    i_X4                : BOOL;   // 反向限位1
    i_X5                : BOOL;   // 正向限位2
    i_X6                : BOOL;   // 反向限位2
    i_X7                : BOOL;   // 正向限位3
    i_X10               : BOOL;   // 反向限位3
    i_X11               : BOOL;   // 伺服故障报警1
    i_X12               : BOOL;   // 伺服故障报警2
    i_X13               : BOOL;   // 伺服故障报警3
    i_X14               : BOOL;   // 安全门/安全传感器1
    i_X15               : BOOL;   // 安全门/安全传感器2
    i_X16               : BOOL;   // 急停按钮(常闭)
    i_X17               : BOOL;   // 复位按钮
    
    // ===== DI扩展模块1输入 (预留) =====
    i_DI1_X10           : BOOL;   // 扩展DI1-信号10
    i_DI1_X11           : BOOL;   // 扩展DI1-信号11
    i_DI1_X12           : BOOL;   // 扩展DI1-信号12
    i_DI1_X13           : BOOL;   // 扩展DI1-信号13
    
    // ===== DI扩展模块2输入 (预留) =====
    i_DI2_X0            : BOOL;   // 扩展DI2-信号0
    i_DI2_X1            : BOOL;   // 扩展DI2-信号1
    
    // ===== 远程IO输入 (预留) =====
    i_Remote_X0         : BOOL;   // 远程IO-信号0
    i_Remote_X1         : BOOL;   // 远程IO-信号1
    i_Remote_X2         : BOOL;   // 远程IO-信号2
    i_Remote_X3         : BOOL;   // 远程IO-信号3
END_VAR

VAR_OUTPUT
    // ===== 伺服系统映射 =====
    o_HomeSensor1       : BOOL;   // 原点传感器1状态
    o_HomeSensor2       : BOOL;   // 原点传感器2状态
    o_HomeSensor3       : BOOL;   // 原点传感器3状态
    o_LimitFwd1         : BOOL;   // 正向限位1状态
    o_LimitRev1         : BOOL;   // 反向限位1状态
    o_LimitFwd2         : BOOL;   // 正向限位2状态
    o_LimitRev2         : BOOL;   // 反向限位2状态
    o_ServoALM1         : BOOL;   // 伺服故障1
    o_ServoALM2         : BOOL;   // 伺服故障2
    o_ServoALM3         : BOOL;   // 伺服故障3
    
    // ===== 安全系统映射 =====
    o_SafetySensor1     : BOOL;   // 安全传感器1状态
    o_SafetySensor2     : BOOL;   // 安全传感器2状态
    o_EStop_Button      : BOOL;   // 急停按钮状态
    o_Reset_Button      : BOOL;   // 复位按钮状态
    
    // ===== 扩展模块映射 (预留) =====
    o_DI1_Signal1       : BOOL;   // 扩展DI1信号1
    o_DI1_Signal2       : BOOL;   // 扩展DI1信号2
    
    // ===== 远程IO映射 (预留) =====
    o_Remote_Sensor1    : BOOL;   // 远程传感器1
    o_Remote_Sensor2    : BOOL;   // 远程传感器2
END_VAR

//==============================================================================
// 主逻辑 - IO映射
//==============================================================================

// 伺服系统输入映射
o_HomeSensor1 := i_X0;
o_HomeSensor2 := i_X1;
o_HomeSensor3 := i_X2;
o_LimitFwd1 := i_X3;
o_LimitRev1 := i_X4;
o_LimitFwd2 := i_X5;
o_LimitRev2 := i_X6;
o_ServoALM1 := i_X11;
o_ServoALM2 := i_X12;
o_ServoALM3 := i_X13;

// 安全系统输入映射
o_SafetySensor1 := i_X14;
o_SafetySensor2 := i_X15;
o_EStop_Button := i_X16;
o_Reset_Button := i_X17;

// 扩展模块输入映射(根据实际配置添加)
o_DI1_Signal1 := i_DI1_X10;
o_DI1_Signal2 := i_DI1_X11;

// 远程IO输入映射(根据实际配置添加)
o_Remote_Sensor1 := i_Remote_X0;
o_Remote_Sensor2 := i_Remote_X1;

END_FUNCTION_BLOCK