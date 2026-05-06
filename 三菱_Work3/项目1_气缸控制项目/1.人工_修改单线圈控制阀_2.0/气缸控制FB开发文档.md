# 气缸控制FB开发文档

## 1. 设计方案

### 1.1 总体设计

**FB名称**：FB_CylinderControl_work3
**标准**：IEC 61131-3
**版本**：V2.0.0 [2026-01-16]
**设计理念**：模块化设计，状态机实现，安全优先

### 1.2 模块划分

| 模块名称 | 主要功能 | 实现文件 |
|----------|----------|----------|
| 初始化模块 | 系统复位处理，初始化所有变量 | FB_CylinderControl_work3.st |
| 模式切换模块 | 处理手动/自动模式切换 | FB_CylinderControl_work3.st |
| 传感器防抖模块 | 实现传感器信号的防抖处理 | FB_CylinderControl_work3.st |
| 状态机模块 | 基于状态机的气缸控制逻辑 | FB_CylinderControl_work3.st |
| 报警处理模块 | 故障检测和报警逻辑 | FB_CylinderControl_work3.st |
| 阀门卡死检测模块 | 检测电磁阀卡死故障 | FB_CylinderControl_work3.st |
| 输出状态更新模块 | 更新所有输出变量状态 | FB_CylinderControl_work3.st |
| 定时器模块 | 定时器更新逻辑 | FB_CylinderControl_work3.st |

### 1.3 状态机设计

**状态定义**：

| 状态码 | 状态名称 | 转换条件 |
|--------|----------|----------|
| 0 | 空闲状态 | 系统复位后进入，检查传感器状态后转换 |
| 1 | 正在伸出状态 | 收到伸出命令或自动模式启动 |
| 2 | 伸出到位状态 | 终点传感器触发 |
| 3 | 正在缩回状态 | 收到缩回命令或自动模式完成 |
| 4 | 缩回到位状态 | 原点传感器触发 |
| 5 | 报警状态 | 检测到故障 |

**状态转换图**：

```
初始化状态
    └──> 空闲状态(0)
        ├──> 正在伸出状态(1) ──> 伸出到位状态(2) ──> 正在缩回状态(3) ──> 缩回到位状态(4) ──> 空闲状态(0)
        └──> 正在缩回状态(3) ──> 缩回到位状态(4) ──> 空闲状态(0)
        
        任何状态都可能进入报警状态(5) ──> 空闲状态(0)（通过复位）
```

### 1.4 关键算法设计

#### 1.4.1 传感器防抖算法

**防抖逻辑**：
```st
// 传感器防抖定时器 - 直接使用外部输入作为触发信号
_tOriginDebounce(IN:=i_OriginSensor, PT:=i_SensorDebounceTime, Q=> Q_tOriginDebounce, ET=> _tOriginDebounceET);
_tEndDebounce(IN:=i_EndSensor, PT:=i_SensorDebounceTime, Q=> Q_tEndDebounce, ET=> _tEndDebounceET);

// 根据防抖定时器输出更新防抖后的传感器状态
_bDebouncedOrigin := Q_tOriginDebounce;
_bDebouncedEnd := Q_tEndDebounce;
```

#### 1.4.2 状态机算法

**状态机实现**：
```st
// 状态机处理
IF _bStateIdle THEN
    // 空闲状态处理
    ELSIF _bStateExtending THEN
    // 正在伸出状态处理
    ELSIF _bStateExtended THEN
    // 伸出到位状态处理
    ELSIF _bStateRetracting THEN
    // 正在缩回状态处理
    ELSIF _bStateRetracted THEN
    // 缩回到位状态处理
    ELSIF _bStateAlarm THEN
    // 报警状态处理
END_IF;
```

#### 1.4.3 故障检测算法

**传感器冲突检测**：
```st
IF _bDebouncedOrigin AND _bDebouncedEnd THEN
    _bSensorConflictAlarmReq := TRUE;
    IF _bAlarmDelayQ THEN
        _bAlarmLatch := TRUE;
        _bAlarmSensorConflict := TRUE;
        // 进入报警状态
        _bStateIdle := FALSE;
        _bStateExtending := FALSE;
        _bStateExtended := FALSE;
        _bStateRetracting := FALSE;
        _bStateRetracted := FALSE;
        _bStateAlarm := TRUE;
    END_IF;
    ELSE
    _bSensorConflictAlarmReq := FALSE;
END_IF;
```

**阀门卡死检测**：
```st
IF (q_SolenoidOutput XOR _bLastSolenoidState) THEN
    // 电磁阀状态改变，重置相关定时器
    _bExtendingTimeoutReq := FALSE;
    _bRetractingTimeoutReq := FALSE;
END_IF;
_bLastSolenoidState := q_SolenoidOutput;
```

## 2. 实现细节

### 2.1 代码结构

**代码文件**：`FB_CylinderControl_work3.st`
**文件结构**：

```
// 文件头部注释
// 输入输出变量定义
// 程序主体
// 初始化模块：复位处理
// 模式切换处理
// 定时器更新
// 传感器防抖处理
// 报警输出处理
// 传感器冲突检测
// 状态机处理
// 阀门卡死检测
// 输出状态更新
// 状态位数组更新
```

### 2.2 变量定义

**输入变量**：13个，包括传感器信号、控制命令、时间参数等
**输出变量**：9个，包括控制信号、状态反馈、报警信号等
**内部变量**：30个，包括状态变量、定时器变量、中间变量等

### 2.3 关键实现

#### 2.3.1 定时器实现

使用标准定时器，配置如下：
```st
// 传感器防抖定时器
_tOriginDebounce(IN:=i_OriginSensor, PT:=i_SensorDebounceTime, Q=> Q_tOriginDebounce, ET=> _tOriginDebounceET);
_tEndDebounce(IN:=i_EndSensor, PT:=i_SensorDebounceTime, Q=> Q_tEndDebounce, ET=> _tEndDebounceET);

// 报警延迟定时器
_tAlarmDelay(IN:=_bSensorConflictAlarmReq, PT:=i_AlarmDelay, Q=> Q_tAlarmDelay, ET=> _tAlarmDelayET);

// 伸出超时定时器
_tExtendTimeout(IN:=_bExtendingTimeoutReq, PT:=i_ExtendTimeout, Q=> Q_tExtendTimeout, ET=> _tExtendTimeoutET);

// 缩回超时定时器
_tRetractTimeout(IN:=_bRetractingTimeoutReq, PT:=i_RetractTimeout, Q=> Q_tRetractTimeout, ET=> _tRetractTimeoutET);
```

#### 2.3.2 状态机实现

使用标志位实现状态机，每个状态对应一个标志位，包含该状态下的逻辑和状态转换条件。

#### 2.3.3 安全保护实现

- **传感器冲突检测**：检测原点和终点传感器同时触发的情况
- **超时检测**：检测气缸伸出/缩回超时
- **阀门卡死检测**：检测电磁阀状态改变但气缸未动作的情况
- **模式互锁**：手动模式和自动模式互斥

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
| V2.0.0 | 2026-01-16 | 完善传感器防抖、超时报警、阀门卡死检测等功能 | 人工编辑 |

## 5. 测试计划

### 5.1 测试目标

- 验证所有功能模块正常工作
- 验证状态机逻辑正确
- 验证安全保护机制有效
- 验证故障检测和报警功能正常
- 验证传感器防抖功能有效
- 验证阀门卡死检测功能有效

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
| 手动气缸伸出 | 1. 设置i_ManualMode=TRUE<br>2. 设置i_ExtendCmd=TRUE | 气缸伸出，q_Extending=TRUE |
| 手动气缸缩回 | 1. 设置i_ManualMode=TRUE<br>2. 设置i_RetractCmd=TRUE | 气缸缩回，q_Retracting=TRUE |

#### 5.3.2 自动模式测试

| 测试用例 | 测试步骤 | 预期结果 |
|----------|----------|----------|
| 自动运行 | 1. 设置i_AutoMode=TRUE<br>2. 设置i_Start=TRUE | 气缸先伸出后缩回，完成一个循环 |
| 自动停止 | 1. 设置i_AutoMode=TRUE<br>2. 设置i_Start=TRUE<br>3. 设置i_Stop=TRUE | 气缸停止当前动作，进入空闲状态 |

#### 5.3.3 故障检测测试

| 测试用例 | 测试步骤 | 预期结果 |
|----------|----------|----------|
| 传感器冲突 | 1. 同时触发i_OriginSensor和i_EndSensor | q_Alarm=TRUE，进入报警状态 |
| 伸出超时 | 1. 设置i_AutoMode=TRUE<br>2. 设置i_Start=TRUE<br>3. 模拟终点传感器不触发 | 超时后q_Alarm=TRUE，进入报警状态 |
| 阀门卡死 | 1. 模拟电磁阀状态改变但气缸未动作 | 检测到阀门卡死，q_Alarm=TRUE |

## 6. 部署与维护

### 6.1 部署方式

1. 将FB块导入到GX Works3项目中
2. 配置变量映射关系
3. 在主程序中实例化FB块
4. 下载到PLC设备中运行

### 6.2 维护注意事项

1. 定期检查传感器状态，确保信号正常
2. 定期检查气缸动作是否顺畅，必要时添加润滑油
3. 定期检查电磁阀是否正常工作，避免卡死
4. 定期备份PLC程序和变量表
5. 记录故障信息，便于分析和改进
6. 根据实际情况调整超时时间和防抖时间参数

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
| 单线圈控制 | 一种控制方式，通过单个输出线圈控制执行机构的动作 |
| 传感器防抖 | 消除传感器信号抖动的技术，确保信号稳定可靠 |
| 超时检测 | 检测执行机构动作超时的功能，用于故障诊断 |
| 阀门卡死 | 电磁阀因故障无法正常动作的现象 |
| 状态机 | 一种数学模型，用于描述对象在不同状态之间的转换 |

### 8.2 代码规范

- 符合IEC 61131-3标准
- 变量命名规范：输入变量i_前缀，输出变量q_前缀，内部变量_前缀
- 代码注释完整，包含功能描述、变量说明、状态转换条件等
- 模块化设计，每个模块功能清晰，逻辑独立
- 安全优先，实现完善的安全保护机制
- 性能优化，确保响应时间和状态切换时间符合要求