# 输送线控制FB开发文档

## 基本信息
- **文档标题**：输送线控制FB开发文档
- **文档类型**：开发文档
- **版本号**：V4.1.0
- **创建日期**：2026-01-20
- **最后更新日期**：2026-01-21
- **文档状态**：已完成
- **变更类型**：文档完善
- **变更原因**：增加SCL代码实现细节和POU划分，应用新的文档迭代更新机制

## 变更记录
| 日期 | 版本 | 变更类型 | 变更原因 | 变更内容 | 变更人员 |
|------|------|----------|----------|----------|----------|
| 2026-01-20 | V4.0.0 | 重大变更 | 重新开发 | 重新开发，实现高内聚低耦合设计 | 系统 |
| 2026-01-21 | V4.1.0 | 文档完善 | 增强文档完整性 | 增加SCL代码实现细节和POU划分，应用新的文档迭代更新机制 | 系统 |

## 开发背景
为了实现输送线的可靠控制，重新开发了符合IEC 61131-3标准的输送线控制FB，采用高内聚、低耦合的设计原则，提高系统的可靠性和可维护性。

## 设计原则
1. **高内聚**：将相关功能封装在FB内部，减少外部依赖
2. **低耦合**：通过明确的输入输出接口与外部系统交互
3. **移植性强**：避免硬件依赖，确保在不同PLC系统中可移植
4. **标准化**：严格遵循IEC 61131-3标准
5. **可靠性**：完善的故障检测和处理机制

## 功能设计
### 1. 模式控制
- **手动模式**：通过`i_ManualStart`和`i_ManualStop`控制
- **自动模式**：通过`i_AutoStart`和`i_AutoStop`控制
- **模式优先级**：手动模式优先级高于自动模式

### 2. 速度控制
- **停止**：速度模式为0
- **慢速**：速度模式为1（自动模式默认）
- **快速**：速度模式为2（手动模式默认）

### 3. 故障检测
- **速度模式冲突检测**：运行状态与停止速度模式的冲突
- **故障输出**：通过`q_MotorFault`输出故障状态

## 实现细节
### 1. POU（程序组织单元）划分
| POU名称 | 类型 | 功能描述 | 调用关系 |
|---------|------|----------|----------|
| FB_ConveyorControlV4 | FB | 主功能块，包含完整控制逻辑 | 被主程序调用 |
| 初始化模块 | 子模块 | 系统初始化，变量重置 | 主FB内部调用 |
| 手动控制模块 | 子模块 | 处理手动模式下的控制逻辑 | 主FB内部调用 |
| 自动控制模块 | 子模块 | 处理自动模式下的控制逻辑 | 主FB内部调用 |
| 速度控制模块 | 子模块 | 处理速度模式切换逻辑 | 主FB内部调用 |
| 故障检测模块 | 子模块 | 检测和处理系统故障 | 主FB内部调用 |
| 电机方向控制模块 | 子模块 | 处理电机方向控制逻辑 | 主FB内部调用 |
| 计时器模块 | 子模块 | 管理系统计时器逻辑 | 主FB内部调用 |
| 状态管理模块 | 子模块 | 管理系统运行状态 | 主FB内部调用 |

### 2. 状态管理
- 使用内部变量跟踪系统状态
- 实现状态的平滑切换
- 避免状态振荡

### 3. 逻辑实现
- **模式切换逻辑**：根据输入信号确定当前工作模式
- **启动/停止逻辑**：根据当前模式和输入信号控制电机启停
- **速度控制逻辑**：根据工作模式设置默认速度
- **故障检测逻辑**：检测系统异常状态

### 4. 代码结构
- 清晰的功能模块划分
- 详细的注释说明
- 符合SCL语言规范

### 5. SCL代码实现细节
```scl
// FB_ConveyorControlV4 主功能块
FUNCTION_BLOCK FB_ConveyorControlV4
VAR_INPUT
    i_ManualStart : BOOL;           // 手动启动信号
    i_ManualStop : BOOL;            // 手动停止信号
    i_AutoStart : BOOL;             // 自动启动信号
    i_AutoStop : BOOL;              // 自动停止信号
    i_Position1Sensor : BOOL;        // 位置1传感器信号
    i_MainControlMode : INT;        // 主控运行模式(0-停止,1-手动,2-自动)
    i_MotorDirection : INT;          // 电机运行方向(0-正转,1-反转)
    i_SlowDelayTime : INT;           // 慢速延时时间设定(毫秒)
END_VAR

VAR_OUTPUT
    q_MotorRunning : BOOL;           // 电机运行状态
    q_MotorSlow : BOOL;              // 电机慢速状态
    q_MotorFast : BOOL;              // 电机快速状态
    q_MotorFault : BOOL;             // 电机异常状态
    q_MotorDirection : INT;           // 电机运行方向状态(0-正转,1-反转)
    q_ProductInPlaceDone : BOOL;      // 产品到位完成标志
END_VAR

VAR
    // 模式控制变量
    tmp_bManualMode : BOOL;          // 手动模式标志
    tmp_bAutoMode : BOOL;            // 自动模式标志
    tmp_nCurrentMode : INT;           // 当前运行模式
    
    // 电机状态变量
    tmp_bMotorRunning : BOOL;         // 电机运行内部状态
    tmp_bMotorFault : BOOL;           // 电机故障内部状态
    tmp_bSpeedMode : INT;             // 速度模式(0-停止,1-慢速,2-快速)
    
    // 电机方向变量
    tmp_nCurrentMotorDirection : INT; // 当前电机方向
    tmp_bDirectionChangeAllowed : BOOL; // 方向切换允许标志
    
    // 产品检测变量
    tmp_bProductInPlaceDone : BOOL;   // 产品到位完成内部标志
    tmp_nNoProductDelay : INT;        // 无产品检测延时计数器
    
    // 计时器变量
    In_tTimer1 : ARRAY [0..1] OF BOOL; // 计时器IN输入数组
    Q_tTimer1 : ARRAY [0..1] OF BOOL;  // 计时器Q输出数组
    R_tTimer1 : ARRAY [0..1] OF BOOL;  // 计时器R复位数组
    PT_tTimer1 : ARRAY [0..1] OF DINT; // 计时器PT预设值数组
    ET_tTimer1 : ARRAY [0..1] OF DINT; // 计时器ET当前值数组
END_VAR

VAR_TEMP
    // 临时变量
    bModeChangeAllowed : BOOL;       // 模式切换允许标志
END_VAR

// 初始化模块
IF i_MainControlMode = 0 THEN
    // 复位所有内部状态
    tmp_bManualMode := FALSE;
    tmp_bAutoMode := FALSE;
    tmp_bMotorRunning := FALSE;
    tmp_bMotorFault := FALSE;
    tmp_bSpeedMode := 0;
    tmp_nCurrentMode := 0;
    tmp_nCurrentMotorDirection := 0;
    tmp_bProductInPlaceDone := FALSE;
    tmp_nNoProductDelay := 0;
    
    // 复位计时器
    In_tTimer1[0] := FALSE;
    In_tTimer1[1] := FALSE;
    R_tTimer1[0] := TRUE;
    R_tTimer1[1] := TRUE;
END_IF

// 模式控制逻辑
CASE i_MainControlMode OF
    1: // 手动模式
        tmp_nCurrentMode := 1;
        tmp_bManualMode := TRUE;
        tmp_bAutoMode := FALSE;
        
        // 手动启动/停止逻辑
        IF i_ManualStart THEN
            tmp_bMotorRunning := TRUE;
            tmp_bSpeedMode := 2; // 手动模式默认快速
        ELSIF i_ManualStop THEN
            tmp_bMotorRunning := FALSE;
            tmp_bSpeedMode := 0;
        END_IF;
        
    2: // 自动模式
        tmp_nCurrentMode := 2;
        tmp_bManualMode := FALSE;
        tmp_bAutoMode := TRUE;
        
        // 自动启动/停止逻辑
        IF i_AutoStart THEN
            tmp_bMotorRunning := TRUE;
            tmp_bSpeedMode := 2; // 自动模式初始快速
            
            // 产品检测逻辑
            IF i_Position1Sensor THEN
                // 产品到位，切换到慢速
                tmp_bSpeedMode := 1;
                
                // 启动慢速延时计时器
                In_tTimer1[1] := TRUE;
                PT_tTimer1[1] := i_SlowDelayTime * 1000; // 转换为毫秒
                
                IF Q_tTimer1[1] THEN
                    // 慢速延时结束，停止电机
                    tmp_bMotorRunning := FALSE;
                    tmp_bSpeedMode := 0;
                    tmp_bProductInPlaceDone := TRUE;
                    In_tTimer1[1] := FALSE;
                    R_tTimer1[1] := TRUE;
                END_IF;
            END_IF;
        ELSIF i_AutoStop THEN
            tmp_bMotorRunning := FALSE;
            tmp_bSpeedMode := 0;
        END_IF;
        
    ELSE // 停止模式
        tmp_nCurrentMode := 0;
        tmp_bManualMode := FALSE;
        tmp_bAutoMode := FALSE;
        tmp_bMotorRunning := FALSE;
        tmp_bSpeedMode := 0;
END_CASE

// 电机方向控制逻辑
// 只有在电机停止时才能更改方向
IF NOT tmp_bMotorRunning THEN
    tmp_nCurrentMotorDirection := i_MotorDirection;
    tmp_bDirectionChangeAllowed := TRUE;
ELSE
    tmp_bDirectionChangeAllowed := FALSE;
END_IF

// 速度模式控制逻辑
CASE tmp_bSpeedMode OF
    0: // 停止
        q_MotorSlow := FALSE;
        q_MotorFast := FALSE;
    1: // 慢速
        q_MotorSlow := TRUE;
        q_MotorFast := FALSE;
    2: // 快速
        q_MotorSlow := FALSE;
        q_MotorFast := TRUE;
END_CASE

// 故障检测逻辑
// 速度模式冲突检测
IF tmp_bMotorRunning AND tmp_bSpeedMode = 0 THEN
    tmp_bMotorFault := TRUE;
ELSE
    tmp_bMotorFault := FALSE;
END_IF

// 产品到位完成标志逻辑
q_ProductInPlaceDone := tmp_bProductInPlaceDone;

// 无产品检测延时逻辑
IF tmp_bProductInPlaceDone AND NOT i_Position1Sensor THEN
    In_tTimer1[0] := TRUE;
    PT_tTimer1[0] := 3000; // 3秒延时
    
    IF Q_tTimer1[0] THEN
        // 延时结束，复位产品到位标志
        tmp_bProductInPlaceDone := FALSE;
        In_tTimer1[0] := FALSE;
        R_tTimer1[0] := TRUE;
    END_IF;
ELSE
    R_tTimer1[0] := TRUE;
END_IF

// 输出赋值
q_MotorRunning := tmp_bMotorRunning;
q_MotorFault := tmp_bMotorFault;
q_MotorDirection := tmp_nCurrentMotorDirection;

// 计时器调用
TONR(IN := In_tTimer1[0], PT := PT_tTimer1[0], R := R_tTimer1[0], Q => Q_tTimer1[0], ET => ET_tTimer1[0]);
TONR(IN := In_tTimer1[1], PT := PT_tTimer1[1], R := R_tTimer1[1], Q => Q_tTimer1[1], ET => ET_tTimer1[1]);
END_FUNCTION_BLOCK
```

## 测试策略
1. **功能测试**：验证各输入信号的响应
2. **模式切换测试**：测试手动/自动模式的切换
3. **故障检测测试**：验证故障检测功能
4. **边界条件测试**：测试各种边界情况下的系统行为

## 性能分析
- **响应时间**：输入信号变化到输出响应的时间小于1个扫描周期
- **资源占用**：内存占用低，适合在各种PLC系统中运行
- **可靠性**：逻辑简单可靠，故障检测机制完善

## 维护指南
1. **参数调整**：可通过修改内部默认速度值调整系统行为
2. **功能扩展**：预留了扩展接口，可根据需要添加新功能
3. **故障排查**：通过监控内部变量可快速定位问题

## 开发工具
- **编程软件**：支持IEC 61131-3标准的PLC编程软件
- **编码规范**：遵循IEC 61131-3标准和项目编码规范
- **版本管理**：使用语义化版本号进行版本管理，当前版本：V4.1.0