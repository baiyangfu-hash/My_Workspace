# 工作站详细设计说明书

## 版本管理规范

- **版本号格式**：主版本.次版本.修订版本（如 V1.0.0）
  - 主版本：重大功能变更或架构调整
  - 次版本：新增功能或较大改进
  - 修订版本：bug修复或小的改进
- **版本日志必须包含**：更新时间、编译器、编译器版本、模板版本、接口版本、需求版本、设计版本、核心内容、变更单关联、交付物

## 变更记录

### V1.0.0
- **更新时间**：2026-01-29
- **编译器**：Autoshop
- **编译器版本**：Vx.x.x
- **模板版本**：Autoshop 模板库V1.0
- **接口版本**：V1.0.0
- **需求版本**：REQ-V1.0.0
- **设计版本**：DES-V1.0.0
- **核心内容**：
  - 创建工作站详细设计说明书模板
  - 定义基本设计结构
  - 搭建文档框架
- **变更单关联**：
  - 变更单号：无
- **交付物**：
  - 2-工作站详细设计说明书_DES-V1.0.0.md

### V1.0.1
- **更新时间**：2026-01-31
- **编译器**：Autoshop
- **编译器版本**：Vx.x.x
- **模板版本**：Autoshop 模板库V1.0
- **接口版本**：V1.0.0
- **需求版本**：REQ-V1.0.0
- **设计版本**：DES-V1.0.0
- **核心内容**：
  - 更新工作站功能设计：添加主控命令接收模块，更新功能模块划分、变量定义、控制逻辑和状态机设计
  - 完善详细设计内容
  - 优化文档格式
- **变更单关联**：
  - 变更单号：无
- **交付物**：
  - 更新后的2-工作站详细设计说明书_DES-V1.0.0.md

## 文档标识
- **文档类型**：详细设计说明书
- **版本号**：V1.0.0
- **创建日期**：2026-01-29
- **最后更新**：2026-01-31
- **文档状态**：已完成

## 1. 设计概述

### 1.1 设计目标
本设计说明书描述了工作站FB功能块的详细设计方案，包括系统架构、控制逻辑、状态机设计等内容。该FB功能块遵循IEC 61131-3标准，采用结构化文本（SCL）语言编写，具备主控命令执行、控制参数处理、状态报告、报警处理和状态监控等功能，实现与主控站的高效通信和协作。

### 1.2 设计原则
- **模块化设计**：将功能分解为独立的模块，便于维护和扩展
- **结构化编程**：采用结构化文本语言，代码清晰易读
- **状态机设计**：使用状态机管理工作站状态，避免状态振荡
- **错误处理**：完善的错误检测和处理机制
- **可配置性**：支持参数配置，适应不同应用场景

## 2. 系统架构

### 2.1 功能模块划分
| 模块名称 | 功能描述 | 输入/输出 | 详细说明 |
|----------|----------|----------|----------|
| 初始化模块 | 初始化工作站内部变量和状态 | 无 | 系统启动时执行，设置默认值 |
| 主控命令处理模块 | 接收并执行主控命令 | i_MasterCommand, i_MasterCommandEnable | 解析并执行启动、急停、暂停、初始化命令 |
| 参数处理模块 | 处理主控发送的控制参数 | i_ControlParams, i_ParamUpdate | 接收并应用运行模式等控制参数 |
| 手动控制模块 | 处理工作站手动模式下的控制逻辑 | i_ManualStart, i_ManualStop | 响应手动操作指令 |
| 自动控制模块 | 处理工作站自动模式下的控制逻辑 | i_AutoStart, i_AutoStop | 执行预设的自动控制流程 |
| 报警处理模块 | 处理工作站报警信号 | i_Alarm | 检测和响应报警状态 |
| 状态报告模块 | 向主控报告执行状态和工作站状态 | q_CommandStatus, q_WorkstationStatus | 生成并发送状态信息 |

### 2.2 数据流图
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ 输入信号   │     │ 工作站FB   │     │ 输出信号   │
│            │     │ 功能块     │     │            │
│ i_MasterCommand │───→│ 主控命令   │───→│ q_CommandStatus │
│ i_ControlParams │───→│ 参数处理   │───→│ q_WorkstationStatus │
│ i_ManualStart   │───→│ 手动控制   │───→│ q_Output    │
│ i_ManualStop    │───→│ 自动控制   │───→│ q_AlarmStatus │
│ i_AutoStart     │───→│ 报警处理   │───→│ q_StatusWord │
│ i_AutoStop      │───→│ 状态报告   │     │            │
│ i_Alarm         │     │            │     │            │
│ i_Reset         │     │            │     │            │
└─────────────┘     └─────────────┘     └─────────────┘
```

## 3. 详细设计

### 3.1 变量定义

#### 3.1.1 输入变量
| 变量名 | 数据类型 | 描述 | 初始值 | 范围 |
|--------|----------|------|--------|------|
| i_MasterCommand | INT | 主控命令：0=无命令,1=启动,2=急停,3=暂停,4=初始化 | 0 | 0-4 |
| i_MasterCommandEnable | BOOL | 主控命令使能 | FALSE | TRUE/FALSE |
| i_ControlParams | INT | 控制参数：运行模式(0=自动,1=手动,2=半自动) | 0 | 0-2 |
| i_ParamUpdate | BOOL | 参数更新标志 | FALSE | TRUE/FALSE |
| i_ManualStart | BOOL | 手动启动信号 | FALSE | TRUE/FALSE |
| i_ManualStop | BOOL | 手动停止信号 | FALSE | TRUE/FALSE |
| i_AutoStart | BOOL | 自动启动信号 | FALSE | TRUE/FALSE |
| i_AutoStop | BOOL | 自动停止信号 | FALSE | TRUE/FALSE |
| i_Alarm | BOOL | 报警信号 | FALSE | TRUE/FALSE |
| i_Reset | BOOL | 复位信号 | FALSE | TRUE/FALSE |

#### 3.1.2 输出变量
| 变量名 | 数据类型 | 描述 | 初始值 | 范围 |
|--------|----------|------|--------|------|
| q_CommandStatus | INT | 命令执行状态：0=空闲,1=执行中,2=执行完成,3=不予执行 | 0 | 0-3 |
| q_WorkstationStatus | INT | 工作站状态：0=待料中,1=堵料中,2=工作中,3=报警中 | 0 | 0-3 |
| q_Output | BOOL | 工作站控制输出信号 | FALSE | TRUE/FALSE |
| q_AlarmStatus | BOOL | 工作站报警状态输出 | FALSE | TRUE/FALSE |
| q_StatusWord | INT | 工作站状态字 | 0 | 0-255 |

#### 3.1.3 内部变量
| 变量名 | 数据类型 | 描述 | 初始值 | 范围 |
|--------|----------|------|--------|------|
| tmp_bOutput | BOOL | 工作站输出状态内部变量 | FALSE | TRUE/FALSE |
| tmp_bAlarmStatus | BOOL | 工作站报警状态内部变量 | FALSE | TRUE/FALSE |
| tmp_nStatusWord | INT | 工作站状态字内部变量 | 0 | 0-255 |
| tmp_bManualMode | BOOL | 工作站手动模式标志 | FALSE | TRUE/FALSE |
| tmp_bAutoMode | BOOL | 工作站自动模式标志 | FALSE | TRUE/FALSE |
| tmp_nCommandStatus | INT | 命令执行状态内部变量 | 0 | 0-3 |
| tmp_nWorkstationStatus | INT | 工作站状态内部变量 | 0 | 0-3 |
| tmp_nControlParams | INT | 控制参数内部变量 | 0 | 0-2 |
| tmp_bCommandExecuting | BOOL | 命令执行中标志 | FALSE | TRUE/FALSE |

### 3.2 控制逻辑设计

#### 3.2.1 初始化模块
```scl
// 工作站初始化模块
IF NOT tmp_bInitialized THEN
    tmp_bOutput := FALSE;
    tmp_bAlarmStatus := FALSE;
    tmp_nStatusWord := 0;
    tmp_bManualMode := FALSE;
    tmp_bAutoMode := FALSE;
    tmp_nCommandStatus := 0;
    tmp_nWorkstationStatus := 0;
    tmp_nControlParams := 0;
    tmp_bCommandExecuting := FALSE;
    tmp_bInitialized := TRUE;
END_IF;
```

#### 3.2.2 主控命令处理模块
```scl
// 工作站主控命令处理模块
IF i_MasterCommandEnable THEN
    CASE i_MasterCommand OF
        1: // 启动命令
            tmp_nCommandStatus := 1; // 执行中
            tmp_bCommandExecuting := TRUE;
            tmp_bOutput := TRUE;
            tmp_nWorkstationStatus := 2; // 工作中
            // 启动逻辑
            tmp_nCommandStatus := 2; // 执行完成
        2: // 急停命令
            tmp_nCommandStatus := 1; // 执行中
            tmp_bCommandExecuting := TRUE;
            tmp_bOutput := FALSE;
            tmp_bManualMode := FALSE;
            tmp_bAutoMode := FALSE;
            tmp_nWorkstationStatus := 0; // 待料中
            // 急停逻辑
            tmp_nCommandStatus := 2; // 执行完成
        3: // 暂停命令
            tmp_nCommandStatus := 1; // 执行中
            tmp_bCommandExecuting := TRUE;
            tmp_bOutput := FALSE;
            // 暂停逻辑
            tmp_nCommandStatus := 2; // 执行完成
        4: // 初始化命令
            tmp_nCommandStatus := 1; // 执行中
            tmp_bCommandExecuting := TRUE;
            // 初始化逻辑
            tmp_bOutput := FALSE;
            tmp_bManualMode := FALSE;
            tmp_bAutoMode := FALSE;
            tmp_nWorkstationStatus := 0; // 待料中
            tmp_nCommandStatus := 2; // 执行完成
        ELSE // 无命令或无效命令
            tmp_nCommandStatus := 3; // 不予执行
    END_CASE;
    tmp_bCommandExecuting := FALSE;
END_IF;
```

#### 3.2.3 参数处理模块
```scl
// 工作站参数处理模块
IF i_ParamUpdate THEN
    tmp_nControlParams := i_ControlParams;
    
    // 根据运行模式设置相应标志
    CASE i_ControlParams OF
        0: // 自动运行
            tmp_bAutoMode := TRUE;
            tmp_bManualMode := FALSE;
        1: // 手动运行
            tmp_bManualMode := TRUE;
            tmp_bAutoMode := FALSE;
        2: // 半自动运行
            // 半自动运行逻辑
    END_CASE;
END_IF;
```

#### 3.2.4 手动控制模块
```scl
// 工作站手动控制模块
IF i_ManualStart AND NOT tmp_bManualMode THEN
    tmp_bManualMode := TRUE;
    tmp_bAutoMode := FALSE;
    tmp_bOutput := TRUE;
    tmp_nWorkstationStatus := 2; // 工作中
END_IF;

IF i_ManualStop THEN
    tmp_bManualMode := FALSE;
    tmp_bOutput := FALSE;
    tmp_nWorkstationStatus := 0; // 待料中
END_IF;
```

#### 3.2.5 自动控制模块
```scl
// 工作站自动控制模块
IF i_AutoStart AND NOT tmp_bAutoMode THEN
    tmp_bAutoMode := TRUE;
    tmp_bManualMode := FALSE;
    tmp_bOutput := TRUE;
    tmp_nWorkstationStatus := 2; // 工作中
END_IF;

IF i_AutoStop THEN
    tmp_bAutoMode := FALSE;
    tmp_bOutput := FALSE;
    tmp_nWorkstationStatus := 0; // 待料中
END_IF;
```

#### 3.2.6 报警处理模块
```scl
// 工作站报警处理模块
IF i_Alarm THEN
    tmp_bAlarmStatus := TRUE;
    tmp_bOutput := FALSE;
    tmp_bManualMode := FALSE;
    tmp_bAutoMode := FALSE;
    tmp_nWorkstationStatus := 3; // 报警中
    tmp_nCommandStatus := 2; // 执行完成（如果有命令正在执行）
END_IF;

IF i_Reset THEN
    tmp_bAlarmStatus := FALSE;
    tmp_nWorkstationStatus := 0; // 待料中
    tmp_nCommandStatus := 0; // 空闲
END_IF;
```

#### 3.2.7 状态监控模块
```scl
// 工作站状态监控模块
tmp_nStatusWord := 0;

// 位0: 工作站手动模式
IF tmp_bManualMode THEN
    tmp_nStatusWord := tmp_nStatusWord OR 1;
END_IF;

// 位1: 工作站自动模式
IF tmp_bAutoMode THEN
    tmp_nStatusWord := tmp_nStatusWord OR 2;
END_IF;

// 位2: 工作站输出状态
IF tmp_bOutput THEN
    tmp_nStatusWord := tmp_nStatusWord OR 4;
END_IF;

// 位3: 工作站报警状态
IF tmp_bAlarmStatus THEN
    tmp_nStatusWord := tmp_nStatusWord OR 8;
END_IF;

// 位4-5: 命令执行状态
CASE tmp_nCommandStatus OF
    1: // 执行中
        tmp_nStatusWord := tmp_nStatusWord OR 16;
    2: // 执行完成
        tmp_nStatusWord := tmp_nStatusWord OR 32;
    3: // 不予执行
        tmp_nStatusWord := tmp_nStatusWord OR 48;
END_CASE;

// 位6-7: 工作站状态
CASE tmp_nWorkstationStatus OF
    1: // 堵料中
        tmp_nStatusWord := tmp_nStatusWord OR 64;
    2: // 工作中
        tmp_nStatusWord := tmp_nStatusWord OR 128;
    3: // 报警中
        tmp_nStatusWord := tmp_nStatusWord OR 192;
END_CASE;
```

### 3.3 状态机设计

#### 3.3.1 状态定义
| 状态名称 | 状态值 | 描述 | 输入条件 | 输出动作 |
|----------|--------|------|----------|----------|
| 初始化状态 | 0 | 工作站初始化 | 系统启动或初始化命令 | 设置初始值，向主控报告初始化完成 |
| 待料状态 | 1 | 工作站等待物料 | 初始化完成或急停命令 | 输出关闭，向主控报告待料中 |
| 堵料状态 | 2 | 工作站物料堵塞 | 物料检测信号 | 输出关闭，向主控报告堵料中 |
| 工作状态 | 3 | 工作站正常工作 | 启动命令或手动/自动启动 | 输出打开，向主控报告工作中 |
| 报警状态 | 4 | 工作站报警 | 报警信号 | 输出关闭，向主控报告报警中 |

#### 3.3.2 状态转移图
```
┌─────────────┐     启动命令     ┌─────────────┐
│ 初始化状态 │──────────────────→│ 工作状态   │
└─────────────┘                   └─────────────┘
       │                                   │
       │ 完成初始化                       │ 急停命令/暂停命令
       ▼                                   ▼
┌─────────────┐     物料检测     ┌─────────────┐
│ 待料状态   │──────────────────→│ 堵料状态   │
└─────────────┘                   └─────────────┘
       │                                   │
       │ 物料到位                         │ 物料清除
       ▼                                   ▼
┌─────────────┐     启动命令     ┌─────────────┐
│ 待料状态   │──────────────────→│ 工作状态   │
└─────────────┘                   └─────────────┘
       │                                   │
       │ 报警信号                         │ 报警信号
       ▼                                   ▼
┌─────────────┐     复位命令     ┌─────────────┐
│ 报警状态   │──────────────────→│ 待料状态   │
└─────────────┘                   └─────────────┘
```

## 4. 故障处理设计

### 4.1 故障检测
| 故障类型 | 检测方法 | 处理方式 | 优先级 |
|----------|----------|----------|--------|
| 输入信号冲突 | 检测手动和自动信号同时激活 | 优先处理手动信号 | 高 |
| 输出异常 | 检测输出信号与预期状态不符 | 触发报警并向主控报告 | 高 |
| 运行超时 | 检测运行时间超过设定值 | 自动停止并报警，向主控报告 | 中 |
| 主控命令执行失败 | 检测命令执行过程中的异常 | 向主控报告执行失败状态 | 高 |
| 状态报告失败 | 检测状态报告过程中的异常 | 重试状态报告，必要时触发报警 | 中 |

### 4.2 故障处理流程
1. **故障检测**：实时检测系统状态，识别故障类型
2. **故障分类**：根据故障类型进行分类处理
3. **故障响应**：采取相应的处理措施，如停止输出、触发报警等
4. **故障报告**：向主控报告故障状态和故障类型
5. **故障记录**：记录故障信息，便于后续分析
6. **故障恢复**：在故障消除后，通过复位信号恢复系统
7. **恢复报告**：向主控报告故障恢复状态

## 5. 性能指标

| 指标名称 | 目标值 | 测试方法 | 详细说明 |
|----------|--------|----------|----------|
| 响应时间 | ≤10ms | 信号触发测试 | 从输入信号变化到输出响应的时间 |
| 可靠性 | ≥99.9% | 长时间运行测试 | 系统连续运行24小时无故障 |
| 稳定性 | 无状态振荡 | 状态切换测试 | 系统状态切换平稳，无振荡 |
| 可维护性 | ≤4小时/年 | 维护测试 | 平均维护时间不超过4小时/年 |

## 6. 测试计划

### 6.1 测试内容
| 测试项 | 测试目的 | 测试方法 | 判定标准 |
|--------|----------|----------|----------|
| 初始化测试 | 验证系统初始化功能 | 启动系统，检查初始状态和初始化完成报告 | 初始状态正确，初始化完成报告准确 |
| 主控命令测试 | 验证主控命令执行功能 | 发送启动、急停、暂停、初始化命令 | 命令执行正确，状态报告准确 |
| 参数处理测试 | 验证控制参数处理功能 | 设置不同运行模式参数 | 参数处理正确，模式切换成功 |
| 手动控制测试 | 验证手动控制功能 | 操作手动启动/停止按钮 | 系统响应正确 |
| 自动控制测试 | 验证自动控制功能 | 激活自动启动/停止信号 | 系统响应正确 |
| 报警处理测试 | 验证报警处理功能 | 触发报警信号，检查报警状态报告 | 系统正确响应，报警状态报告准确 |
| 状态报告测试 | 验证状态报告功能 | 检查命令执行状态和工作站状态报告 | 状态报告准确反映系统状态 |
| 故障恢复测试 | 验证故障恢复功能 | 触发故障后复位，检查恢复状态报告 | 系统正常恢复，恢复状态报告准确 |

### 6.2 测试环境
| 环境参数 | 要求 | 详细说明 |
|----------|------|----------|
| PLC型号 | 汇川Autoshop支持的PLC | 确保测试环境与实际应用环境一致 |
| 软件版本 | Autoshop最新版本 | 确保使用最新的编程软件 |
| 测试工具 | 信号发生器、万用表 | 用于模拟输入信号和测量输出信号 |

## 7. 安全注意事项

| 注意事项 | 风险后果 | 规避措施 | 优先级 |
|----------|----------|----------|--------|
| 输入信号冲突 | 系统误动作 | 实现信号优先级机制 | 高 |
| 输出短路 | 设备损坏 | 添加短路保护逻辑 | 高 |
| 运行模式切换 | 系统不稳定 | 确保在停止状态下切换模式 | 高 |
| 报警处理延迟 | 事故扩大 | 实时响应报警信号 | 高 |

## 8. 部署与维护

### 8.1 部署步骤
1. **导入变量表**：在Autoshop中导入FB的变量表
2. **导入FB功能块**：在Autoshop中导入编译好的FB功能块
3. **实例化FB**：在程序中实例化FB，连接输入输出变量
4. **配置参数**：根据实际应用场景配置FB参数
5. **编译下载**：编译程序并下载到PLC中
6. **测试验证**：运行系统，验证功能是否正常

### 8.2 维护指南
| 维护项目 | 维护周期 | 维护方法 | 详细说明 |
|----------|----------|----------|----------|
| 代码检查 | 每季度 | 检查代码逻辑是否正确 | 确保代码无逻辑错误 |
| 变量表检查 | 每季度 | 检查变量表是否与程序一致 | 确保变量定义完整 |
| 性能测试 | 每半年 | 测试系统性能指标 | 确保系统性能满足要求 |
| 故障分析 | 故障后 | 分析故障原因，优化系统 | 防止类似故障再次发生 |

## 9. 附录

### 9.1 术语定义
| 术语 | 解释 |
|------|------|
| FB | 功能块（Function Block），IEC 61131-3标准中的编程单元 |
| PLC | 可编程逻辑控制器（Programmable Logic Controller） |
| IEC 61131-3 | 国际电工委员会制定的可编程控制器编程语言标准 |
| SCL | 结构化文本（Structured Text），IEC 61131-3标准中的编程语言 |
| 状态机 | 一种数学模型，用于描述系统的状态及其转换 |

### 9.2 参考资料
| 资料名称 | 版本 | 来源 |
|----------|------|------|
| IEC 61131-3标准 | 2013 | 国际电工委员会 |
| 汇川Autoshop编程手册 | V1.0 | 汇川技术 |
| 可编程控制器原理与应用 | 第3版 | 机械工业出版社 |