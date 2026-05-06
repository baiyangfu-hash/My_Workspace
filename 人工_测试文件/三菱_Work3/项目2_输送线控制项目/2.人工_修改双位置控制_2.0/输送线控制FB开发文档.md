# 输送线控制FB开发文档

## 1. 设计方案

### 1.1 总体设计

**FB名称**：FB_ConveyorLineControl_work3
**标准**：IEC 61131-3
**版本**：V2.0.0 [2026-01-16]
**设计理念**：模块化设计，状态机实现，安全优先，上下游交互

### 1.2 模块划分

| 模块名称 | 主要功能 | 实现文件 |
|----------|----------|----------|
| 初始化模块 | 系统复位处理，初始化所有变量 | FB_ConveyorLineControl_work3.st |
| 手动控制模块 | 手动模式下的气缸控制 | FB_ConveyorLineControl_work3.st |
| 自动控制模块 | 基于状态机的自动运行逻辑 | FB_ConveyorLineControl_work3.st |
| 报警处理模块 | 故障检测和报警逻辑 | FB_ConveyorLineControl_work3.st |
| 上下游交互模块 | 与主控系统和机械手的交互逻辑 | FB_ConveyorLineControl_work3.st |
| 定时器模块 | 定时器更新逻辑 | FB_ConveyorLineControl_work3.st |
| 状态更新模块 | 输出状态更新逻辑 | FB_ConveyorLineControl_work3.st |

### 1.3 状态机设计

**状态定义**：

| 状态码 | 状态名称 | 转换条件 |
|--------|----------|----------|
| 0 | 初始化状态 | 系统复位后进入，检查传感器状态后转换 |
| 1 | 等待产品状态 | 系统就绪，等待上游产品进入 |
| 2 | 一号位置有产品状态 | 一号位置传感器检测到产品 |
| 3 | 二号位置有产品状态 | 二号位置传感器检测到产品 |
| 4 | 两个位置都有产品状态 | 两个位置传感器都检测到产品 |

**状态转换图**：

```
初始化状态(0)
    └──> 等待产品状态(1)
        ├──> 一号位置有产品状态(2) ──> 两个位置都有产品状态(4)
        ├──> 二号位置有产品状态(3) ──> 两个位置都有产品状态(4)
        └──> 两个位置都有产品状态(4) ──> 等待产品状态(1)（当产品离开时）
```

### 1.4 关键算法设计

#### 1.4.1 状态机算法

**状态机实现**：
```st
// 自动运行模块：状态机控制
IF i_AutoMode THEN
    CASE tmp_nState OF
        // 初始化状态
        0:
        q_CylinderExtend := FALSE;
        q_CylinderRetract := TRUE;
        q_FeedBlock := FALSE;
        q_IsReady := FALSE;
        q_HasPart := FALSE;
        q_SysConveyorReady := TRUE;
        q_ConveyorReady := TRUE;
        
        // 初始化上下游交互状态
        q_RequestPick := FALSE;
        q_RequestPlace := FALSE;
        
        // 检查传感器状态，进入相应状态
        IF i_Sensor1 AND i_Sensor2 THEN
            tmp_nState := 4; // 两个位置都有产品
            ELSIF i_Sensor1 THEN
            tmp_nState := 2; // 一号位置有产品
            ELSIF i_Sensor2 THEN
            tmp_nState := 3; // 二号位置有产品
            ELSE
            tmp_nState := 1; // 进入等待产品状态
        END_IF;
                
        // 等待产品状态
        1:
        q_IsReady := TRUE;
        q_HasPart := FALSE;
        q_SysConveyorReady := TRUE;
        q_ConveyorReady := TRUE;
        
        // 初始化上下游交互状态
        q_RequestPick := FALSE;
        q_RequestPlace := FALSE;
        
        // 当一号位置有产品时
        IF i_Sensor1 THEN
            tmp_nState := 2;
            // 当二号位置有产品时
            ELSIF i_Sensor2 THEN
            tmp_nState := 3;
            ELSE
            // 两个位置都没有产品，气缸伸出
            q_CylinderExtend := TRUE;
            q_CylinderRetract := FALSE;
            // 根据主控允许进料信号控制
            q_FeedBlock := NOT i_AllowIn;
        END_IF;
                
        // 一号位置有产品状态
        2:
        // 气缸收回
        q_CylinderExtend := FALSE;
        q_CylinderRetract := TRUE;
        q_HasPart := TRUE;
        q_SysConveyorReady := TRUE;
        q_ConveyorReady := TRUE;
        
        // 请求机械手取料
        q_RequestPick := TRUE;
        q_RequestPlace := FALSE;
        
        // 检查二号位置是否有产品
        IF i_Sensor2 THEN
            tmp_nState := 4;  // 进入两个位置都有产品状态
            // 如果一号位置产品离开
            ELSIF NOT i_Sensor1 THEN
            tmp_nState := 1;  // 回到等待产品状态
            // 机械手取料完成后状态更新
            ELSIF i_Robot_CurrentStation = 1 AND i_Robot_Carrying AND i_Robot_TaskAck THEN
            tmp_nState := 1;  // 回到等待产品状态
            q_RequestPick := FALSE;
        END_IF;
                
        // 二号位置有产品状态
        3:
        q_HasPart := TRUE;
        q_SysConveyorReady := TRUE;
        q_ConveyorReady := TRUE;
        
        // 请求机械手取料
        q_RequestPick := TRUE;
        q_RequestPlace := FALSE;
        
        // 检查一号位置是否有产品
        IF i_Sensor1 THEN
            tmp_nState := 4;  // 进入两个位置都有产品状态
            // 如果二号位置产品离开
            ELSIF NOT i_Sensor2 THEN
            tmp_nState := 1;  // 回到等待产品状态
            // 机械手取料完成后状态更新
            ELSIF i_Robot_CurrentStation = 2 AND i_Robot_Carrying AND i_Robot_TaskAck THEN
            tmp_nState := 1;  // 回到等待产品状态
            q_RequestPick := FALSE;
        END_IF;
                
        // 两个位置都有产品状态
        4:
        // 气缸收回
        q_CylinderExtend := FALSE;
        q_CylinderRetract := TRUE;
        // 禁止上游进料
        q_FeedBlock := TRUE;
        q_HasPart := TRUE;
        q_SysConveyorReady := TRUE;
        q_ConveyorReady := TRUE;
        
        // 请求机械手取料
        q_RequestPick := TRUE;
        q_RequestPlace := FALSE;
        
        // 检查是否有产品离开
        IF NOT i_Sensor1 THEN
            tmp_nState := 3;  // 回到只有二号位置有产品状态
            // 更新取料请求
            q_RequestPick := TRUE;
            ELSIF NOT i_Sensor2 THEN
            tmp_nState := 2;  // 回到只有一号位置有产品状态
            // 更新取料请求
            q_RequestPick := TRUE;
        END_IF;
    END_CASE;
END_IF;
```

#### 1.4.2 上下游交互算法

**主控系统交互**：
```st
// 主控→工位信号处理
// 系统自动模式使能
IF i_SysAutoMode THEN
    // 自动模式下的额外处理
    q_SysConveyorReady := TRUE;
    ELSE
    q_SysConveyorReady := FALSE;
END_IF;

// 系统复位请求处理
IF i_SysResetRequest THEN
    // 系统复位逻辑
    q_ErrorActive := FALSE;
    q_ErrorCode := 0;
    q_ProcessDone := FALSE;
END_IF;
```

**机械手交互**：
```st
// 工位→主控信号处理
// 更新工位就绪状态
q_IsReady := (i_Sensor1 OR i_Sensor2) AND NOT q_ErrorActive;

// 更新加工完成状态
// 当产品在工位上且没有错误时，加工完成
IF q_HasPart AND NOT q_ErrorActive THEN
    q_ProcessDone := TRUE;
    ELSE
    q_ProcessDone := FALSE;
END_IF;

// 当机械手到达当前工位且携带产品时，请求放料
IF i_Robot_CurrentStation = 1 AND i_Robot_Carrying AND NOT i_Sensor1 THEN
    q_RequestPlace := TRUE;
    q_RequestPick := FALSE;
    ELSIF i_Robot_CurrentStation = 2 AND i_Robot_Carrying AND NOT i_Sensor2 THEN
    q_RequestPlace := TRUE;
    q_RequestPick := FALSE;
END_IF;
```

## 2. 实现细节

### 2.1 代码结构

**代码文件**：`FB_ConveyorLineControl_work3.st`
**文件结构**：

```
// 文件头部注释
// 输入输出变量定义
// 程序主体
// 初始化模块：复位处理
// 手动控制模块
// 自动运行模块（状态机）
// 非自动非手动模式
// 报警处理模块
// 更新上一次传感器状态
// 定时器更新
// 上下游交互逻辑模块
```

### 2.2 变量定义

**输入变量**：14个，包括传感器信号、控制命令、状态反馈等
**输出变量**：12个，包括控制信号、状态反馈、交互信号等
**内部变量**：18个，包括状态变量、定时器变量、中间变量等

### 2.3 关键实现

#### 2.3.1 初始化模块

**初始化逻辑**：
```st
// 初始化模块：复位处理
IF i_Reset THEN
    tmp_nState := 0;
    q_CylinderExtend := FALSE;
    q_CylinderRetract := TRUE; // 复位时气缸缩回
    q_FeedBlock := FALSE;
    q_IsReady := FALSE;
    q_HasPart := FALSE;
    q_ErrorActive := FALSE;
    q_ErrorCode := 0;
    tmp_bLastSensor1 := i_Sensor1;
    tmp_bLastSensor2 := i_Sensor2;
    // 添加：上下游交互变量初始化
    q_RequestPick := FALSE;
    q_RequestPlace := FALSE;
    q_ProcessDone := FALSE;
    q_SysConveyorReady := FALSE;
    q_ConveyorReady := FALSE;
    tmp_nProcessStep := 0;
    tmp_bProductID := '';
    RETURN;
END_IF;
```

#### 2.3.2 手动控制模块

**手动控制逻辑**：
```st
// 手动控制模块
IF i_ManualMode THEN
    
    // 手动模式下的气缸控制
    IF i_CylinderExtendCmd AND NOT i_CylinderRetractCmd THEN
        q_CylinderExtend := TRUE;
        q_CylinderRetract := FALSE;
        ELSIF i_CylinderRetractCmd AND NOT i_CylinderExtendCmd THEN
        q_CylinderExtend := FALSE;
        q_CylinderRetract := TRUE;
        
    END_IF;
            
    // 手动模式下，进料禁止由两个传感器状态决定
    q_FeedBlock := i_Sensor1 AND i_Sensor2;
            
    // 更新状态输出
    q_IsReady := TRUE;
    q_HasPart := i_Sensor1 OR i_Sensor2;
    q_ErrorActive := FALSE;
    q_ErrorCode := 0;
    
    // 添加：上下游交互状态更新
    q_SysConveyorReady := TRUE;
    q_ConveyorReady := TRUE;
    q_RequestPick := FALSE;
    q_RequestPlace := FALSE;
    q_ProcessDone := FALSE;
    
END_IF;
```

#### 2.3.3 报警处理模块

**报警处理逻辑**：
```st
// 报警处理模块
// 更新报警处理逻辑
q_ErrorActive := FALSE;
q_ErrorCode := 0;

// 检查系统急停
IF tmp_bSysEmergencyStop THEN
    q_ErrorActive := TRUE;
    q_ErrorCode := 1001; // 系统急停错误代码
END_IF;
```

#### 2.3.4 定时器实现

**定时器更新**：
```st
// 定时器更新（单独模块）
// 计时器1：未使用，保持默认状态
tmp_Timer1(IN:=In_tmp_Timer1, PT:=PT_tmp_Timer1, Q=> Q_tmp_Timer1, ET=> ET_tmp_Timer1);
// 计时器2：未使用，保持默认状态
tmp_Timer2(IN:=In_tmp_Timer2, PT:=PT_tmp_Timer2, Q=> Q_tmp_Timer2, ET=> ET_tmp_Timer2);
```

## 3. 开发环境与工具

| 工具名称 | 版本 | 用途 | 备注 |
|----------|------|------|------|
| GX Works3 | V1.0及以上 | 编程软件 | 三菱电机工业自动化编程软件 |
| PLC仿真软件 | V1.0 | 模拟测试 | 用于离线仿真测试 |
| 文本编辑器 | VS Code | 代码编辑 | 辅助代码编辑 |

## 4. 版本历史

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| V1.0.0 | 2026-01-15 | 初始版本，实现基本功能 | 人工编辑 |
| V2.0.0 | 2026-01-16 | 完善上下游交互逻辑，添加完整的主控系统和机械手交互功能 | 人工编辑 |

## 5. 测试计划

### 5.1 测试目标

- 验证所有功能模块正常工作
- 验证状态机逻辑正确
- 验证安全保护机制有效
- 验证故障检测和报警功能正常
- 验证上下游交互逻辑正确
- 验证双位置检测功能有效

### 5.2 测试方法

| 测试类型 | 测试方法 | 测试工具 |
|----------|----------|----------|
| 功能测试 | 手动测试和自动测试结合 | PLC仿真软件 |
| 性能测试 | 测量响应时间和状态切换时间 | 示波器、计时器 |
| 安全测试 | 模拟故障场景，验证故障检测功能 | 手动模拟故障 |
| 兼容性测试 | 在不同PLC型号上测试 | 实际PLC设备 |
| 可靠性测试 | 连续运行测试 | PLC设备 |

### 5.3 测试用例

#### 5.3.1 手动模式测试

| 测试用例 | 测试步骤 | 预期结果 |
|----------|----------|----------|
| 手动气缸控制 | 1. 设置i_ManualMode=TRUE<br>2. 设置i_CylinderExtendCmd=TRUE<br>3. 设置i_CylinderRetractCmd=TRUE | 气缸先伸出，后缩回 |
| 手动进料禁止 | 1. 设置i_ManualMode=TRUE<br>2. 同时触发i_Sensor1和i_Sensor2 | q_FeedBlock=TRUE |

#### 5.3.2 自动模式测试

| 测试用例 | 测试步骤 | 预期结果 |
|----------|----------|----------|
| 自动状态转换 | 1. 设置i_AutoMode=TRUE<br>2. 触发i_Sensor1<br>3. 触发i_Sensor2<br>4. 释放i_Sensor1 | 状态从1→2→4→3→1转换 |
| 主控系统交互 | 1. 设置i_AutoMode=TRUE<br>2. 设置i_AllowIn=TRUE<br>3. 设置i_AllowOut=TRUE | q_FeedBlock=FALSE，系统正常运行 |
| 机械手交互 | 1. 设置i_AutoMode=TRUE<br>2. 触发i_Sensor1<br>3. 设置i_Robot_CurrentStation=1<br>4. 设置i_Robot_Carrying=TRUE<br>5. 设置i_Robot_TaskAck=TRUE | q_RequestPick=TRUE，机械手取料完成后状态转换 |

#### 5.3.3 故障检测测试

| 测试用例 | 测试步骤 | 预期结果 |
|----------|----------|----------|
| 系统急停 | 1. 设置tmp_bSysEmergencyStop=TRUE | q_ErrorActive=TRUE，q_ErrorCode=1001 |

## 6. 部署与维护

### 6.1 部署方式

1. 将FB块导入到GX Works3项目中
2. 配置变量映射关系
3. 在主程序中实例化FB块
4. 下载到PLC设备中运行

### 6.2 维护注意事项

1. 定期检查传感器状态，确保信号正常
2. 定期检查气缸动作是否顺畅，必要时添加润滑油
3. 定期检查与上下游设备的通信状态
4. 定期备份PLC程序和变量表
5. 记录故障信息，便于分析和改进
6. 根据实际运行情况调整系统参数

## 7. 技术支持

| 支持方式 | 联系方式 |
|----------|----------|
| 技术文档 | 项目文档目录 |
| 邮件支持 | support@example.com |
| 电话支持 | 400-123-4567 |

## 8. 附录

### 8.1 术语定义

| 术语 | 定义 |
|------|------|
| FB | Function Block，功能块，IEC 61131-3标准中的功能模块 |
| IEC 61131-3 | 国际电工委员会制定的工业控制系统编程语言标准 |
| GX Works3 | 三菱电机开发的工业自动化编程软件 |
| PLC | Programmable Logic Controller，可编程逻辑控制器 |
| 双位置检测 | 基于两个位置传感器的产品位置检测方式 |
| 状态机 | 一种数学模型，用于描述对象在不同状态之间的转换 |
| 上下游交互 | 与上游设备和下游设备的数据交换和控制信号传递 |
| 进料禁止 | 控制上游设备停止进料的信号 |
| 机械手 | 自动执行取料、放料等操作的自动化设备 |
| 主控系统 | 控制整个生产线的中央控制系统 |

### 8.2 代码规范

- 符合IEC 61131-3标准
- 变量命名规范：输入变量i_前缀，输出变量q_前缀，内部变量tmp_前缀
- 代码注释完整，包含功能描述、变量说明、状态转换条件等
- 模块化设计，每个模块功能清晰，逻辑独立
- 安全优先，实现完善的安全保护机制
- 性能优化，确保响应时间和状态切换时间符合要求
- 上下游交互逻辑清晰，确保与其他设备的正常通信