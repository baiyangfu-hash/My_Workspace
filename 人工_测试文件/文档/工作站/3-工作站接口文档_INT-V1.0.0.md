# 工作站接口文档

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
  - 创建工作站接口文档模板
  - 定义基本接口结构
  - 搭建文档框架
- **变更单关联**：
  - 变更单号：无
- **交付物**：
  - 3-工作站接口文档_INT-V1.0.0.md

### V1.0.1
- **更新时间**：2026-01-31
- **编译器**：Autoshop
- **编译器版本**：Vx.x.x
- **模板版本**：Autoshop 模板库V1.0
- **接口版本**：V1.0.0
- **需求版本**：REQ-V1.0.0
- **设计版本**：DES-V1.0.0
- **核心内容**：
  - 更新工作站接口文档：添加主控命令和控制参数的输入接口，以及命令执行状态和工作站状态的输出接口
  - 完善接口定义内容
  - 优化文档格式
- **变更单关联**：
  - 变更单号：无
- **交付物**：
  - 更新后的3-工作站接口文档_INT-V1.0.0.md

## 文档标识
- **文档类型**：接口文档
- **版本号**：V1.0.0
- **创建日期**：2026-01-29
- **最后更新**：2026-01-31
- **文档状态**：已完成

## 1. 接口概述

### 1.1 接口目的
本文档定义了工作站FB功能块的接口规范，包括输入/输出变量、数据类型、信号时序、错误处理等内容。该接口规范遵循IEC 61131-3标准，确保FB功能块能够与其他系统组件正确集成。

### 1.2 接口范围
本接口文档适用于工作站FB功能块与以下系统组件的交互：
- PLC主程序
- HMI人机界面
- 其他FB功能块
- 外部设备
- 上下游系统

### 1.3 术语定义
| 术语 | 解释 |
|------|------|
| FB | 功能块（Function Block），IEC 61131-3标准中的编程单元 |
| PLC | 可编程逻辑控制器（Programmable Logic Controller） |
| IEC 61131-3 | 国际电工委员会制定的可编程控制器编程语言标准 |
| SCL | 结构化文本（Structured Text），IEC 61131-3标准中的编程语言 |
| 输入变量 | FB功能块的输入参数，用于接收外部信号 |
| 输出变量 | FB功能块的输出参数，用于向外部发送信号 |
| 内部变量 | FB功能块内部使用的变量，不对外暴露 |
| 状态字 | 用于表示系统状态的二进制数据 |
| 工作站 | 自动化生产线上的独立工作单元 |

## 2. 功能块信息

### 2.1 功能块基本信息
| 项目 | 内容 |
|------|------|
| 功能块名称 | FB_WorkstationControl |
| 功能块类型 | 标准功能块 |
| 编程语言 | 结构化文本（SCL） |
| 版本号 | v1.0.0 |
| 描述 | 工作站控制功能块，具备主控命令执行、控制参数处理、状态报告、报警处理和状态监控功能，实现与主控站的高效通信和协作 |

### 2.2 功能块结构
```scl
FUNCTION_BLOCK FB_WorkstationControl
VAR_INPUT
    // 输入变量定义
END_VAR

VAR_OUTPUT
    // 输出变量定义
END_VAR

VAR
    // 内部变量定义
END_VAR

BEGIN
    // 主控制逻辑
END_BODY
END_FUNCTION_BLOCK
```

## 3. 输入接口

### 3.1 控制信号输入

| 变量名 | 数据类型 | 描述 | 初始值 | 范围 | 单位 | 优先级 |
|--------|----------|------|--------|------|------|--------|
| i_WSManualStart | BOOL | 工作站手动启动信号，上升沿触发 | FALSE | TRUE/FALSE | - | 中 |
| i_WSManualStop | BOOL | 工作站手动停止信号，上升沿触发 | FALSE | TRUE/FALSE | - | 中 |
| i_WSAutoStart | BOOL | 工作站自动启动信号，上升沿触发 | FALSE | TRUE/FALSE | - | 中 |
| i_WSAutoStop | BOOL | 工作站自动停止信号，上升沿触发 | FALSE | TRUE/FALSE | - | 中 |
| i_WSAlarm | BOOL | 工作站报警信号，高电平有效 | FALSE | TRUE/FALSE | - | 高 |
| i_WSReset | BOOL | 工作站复位信号，上升沿触发 | FALSE | TRUE/FALSE | - | 高 |
| i_WSMasterCommand | INT | 主控命令：0=无命令,1=启动,2=急停,3=暂停,4=初始化 | 0 | 0-4 | - | 高 |
| i_WSMasterCommandEnable | BOOL | 主控命令使能信号，上升沿触发 | FALSE | TRUE/FALSE | - | 高 |
| i_WSControlParams | INT | 控制参数：运行模式(0=自动,1=手动,2=半自动) | 0 | 0-2 | - | 中 |
| i_WSParamUpdate | BOOL | 参数更新标志，上升沿触发 | FALSE | TRUE/FALSE | - | 中 |

### 3.2 输入信号时序
| 信号名称 | 时序要求 | 详细说明 |
|----------|----------|----------|
| i_WSManualStart | 上升沿触发 | 信号从FALSE变为TRUE时触发手动启动 |
| i_WSManualStop | 上升沿触发 | 信号从FALSE变为TRUE时触发手动停止 |
| i_WSAutoStart | 上升沿触发 | 信号从FALSE变为TRUE时触发自动启动 |
| i_WSAutoStop | 上升沿触发 | 信号从FALSE变为TRUE时触发自动停止 |
| i_WSAlarm | 高电平有效 | 信号为TRUE时表示系统报警 |
| i_WSReset | 上升沿触发 | 信号从FALSE变为TRUE时触发系统复位 |
| i_WSMasterCommand | 电平有效 | 信号值表示命令类型，需与i_WSMasterCommandEnable配合使用 |
| i_WSMasterCommandEnable | 上升沿触发 | 信号从FALSE变为TRUE时触发命令执行 |
| i_WSControlParams | 电平有效 | 信号值表示控制参数，需与i_WSParamUpdate配合使用 |
| i_WSParamUpdate | 上升沿触发 | 信号从FALSE变为TRUE时触发参数更新 |

### 3.3 输入信号约束
| 约束类型 | 详细说明 | 违反后果 |
|----------|----------|----------|
| 信号冲突 | 手动和自动信号不能同时激活 | 系统优先处理手动信号 |
| 主控命令优先级 | 主控命令优先级高于手动/自动信号 | 主控命令执行时忽略手动/自动信号 |
| 信号持续时间 | 触发信号应保持至少1个扫描周期 | 信号可能不被识别 |
| 信号频率 | 输入信号变化频率不应超过PLC扫描频率 | 信号可能丢失 |
| 命令有效性 | 主控命令值应在有效范围内(0-4) | 无效命令将被忽略 |
| 参数有效性 | 控制参数值应在有效范围内(0-2) | 无效参数将被忽略 |

## 4. 输出接口

### 4.1 输出变量列表

| 变量名 | 数据类型 | 描述 | 初始值 | 范围 | 单位 | 优先级 |
|--------|----------|------|--------|------|------|--------|
| q_WSOutput | BOOL | 工作站控制输出信号，高电平有效 | FALSE | TRUE/FALSE | - | 高 |
| q_WSAlarmStatus | BOOL | 工作站报警状态输出，高电平有效 | FALSE | TRUE/FALSE | - | 高 |
| q_WSStatusWord | DWORD | 工作站状态字，位0-7表示不同状态 | 0 | 0-4294967295 | - | 高 |
| q_WSCommandStatus | INT | 命令执行状态：0=空闲,1=执行中,2=执行完成,3=不予执行 | 0 | 0-3 | - | 高 |
| q_WSWorkstationStatus | INT | 工作站状态：0=待料中,1=堵料中,2=工作中,3=报警中 | 0 | 0-3 | - | 高 |

### 4.2 输出信号时序
| 信号名称 | 时序特性 | 详细说明 |
|----------|----------|----------|
| q_WSOutput | 实时响应 | 输入信号变化后1个扫描周期内响应 |
| q_WSAlarmStatus | 实时响应 | 报警信号变化后1个扫描周期内响应 |
| q_WSStatusWord | 实时更新 | 系统状态变化后1个扫描周期内更新 |
| q_WSCommandStatus | 实时更新 | 命令执行状态变化后1个扫描周期内更新 |
| q_WSWorkstationStatus | 实时更新 | 工作站状态变化后1个扫描周期内更新 |

### 4.3 状态字定义
| 位 | 名称 | 描述 | 值 |
|------|------|------|------|
| 0 | 手动模式 | 工作站处于手动模式 | 1: 激活，0: 未激活 |
| 1 | 自动模式 | 工作站处于自动模式 | 1: 激活，0: 未激活 |
| 2 | 输出状态 | 输出信号状态 | 1: 打开，0: 关闭 |
| 3 | 报警状态 | 工作站报警状态 | 1: 报警，0: 正常 |
| 4 | 初始化完成 | 工作站初始化完成状态 | 1: 完成，0: 未完成 |
| 5 | 运行状态 | 工作站运行状态 | 1: 运行中，0: 停止 |
| 6 | 就绪状态 | 工作站就绪状态 | 1: 就绪，0: 未就绪 |
| 7 | 错误状态 | 工作站错误状态 | 1: 错误，0: 正常 |
| 8-9 | 命令执行状态 | 命令执行状态：00=空闲,01=执行中,10=执行完成,11=不予执行 | 二进制值 |
| 10-11 | 工作站状态 | 工作站状态：00=待料中,01=堵料中,10=工作中,11=报警中 | 二进制值 |
| 12 | 主控命令激活 | 主控命令正在执行 | 1: 激活，0: 未激活 |
| 13 | 参数更新中 | 控制参数正在更新 | 1: 激活，0: 未激活 |
| 14-31 | 保留 | 预留未来使用 | 0 |

## 5. 内部接口

### 5.1 内部变量列表

| 变量名 | 数据类型 | 描述 | 初始值 | 范围 | 访问权限 |
|--------|----------|------|--------|------|----------|
| tmp_bWSOutput | BOOL | 工作站输出状态内部变量 | FALSE | TRUE/FALSE | 内部 |
| tmp_bWSAlarmStatus | BOOL | 工作站报警状态内部变量 | FALSE | TRUE/FALSE | 内部 |
| tmp_nWSStatusWord | DWORD | 工作站状态字内部变量 | 0 | 0-4294967295 | 内部 |
| tmp_bWSManualMode | BOOL | 工作站手动模式标志 | FALSE | TRUE/FALSE | 内部 |
| tmp_bWSAutoMode | BOOL | 工作站自动模式标志 | FALSE | TRUE/FALSE | 内部 |
| tmp_bWSInitialized | BOOL | 工作站初始化标志 | FALSE | TRUE/FALSE | 内部 |
| tmp_bWSRunning | BOOL | 工作站运行状态标志 | FALSE | TRUE/FALSE | 内部 |
| tmp_bWSReady | BOOL | 工作站就绪状态标志 | FALSE | TRUE/FALSE | 内部 |
| tmp_nWSCommandStatus | INT | 命令执行状态内部变量 | 0 | 0-3 | 内部 |
| tmp_nWSWorkstationStatus | INT | 工作站状态内部变量 | 0 | 0-3 | 内部 |
| tmp_nWSControlParams | INT | 控制参数内部变量 | 0 | 0-2 | 内部 |
| tmp_bWSCommandExecuting | BOOL | 命令执行中标志 | FALSE | TRUE/FALSE | 内部 |

### 5.2 内部模块接口

| 模块名称 | 输入参数 | 输出参数 | 功能描述 |
|----------|----------|----------|----------|
| 初始化模块 | 无 | tmp_bWSInitialized, tmp_bWSReady | 初始化内部变量和状态 |
| 主控命令处理模块 | i_WSMasterCommand, i_WSMasterCommandEnable | tmp_nWSCommandStatus, tmp_bWSOutput, tmp_nWSWorkstationStatus | 处理主控命令的执行 |
| 参数处理模块 | i_WSControlParams, i_WSParamUpdate | tmp_nWSControlParams, tmp_bWSManualMode, tmp_bWSAutoMode | 处理控制参数的更新 |
| 手动控制模块 | i_WSManualStart, i_WSManualStop | tmp_bWSManualMode, tmp_bWSOutput | 处理手动模式下的控制逻辑 |
| 自动控制模块 | i_WSAutoStart, i_WSAutoStop | tmp_bWSAutoMode, tmp_bWSOutput | 处理自动模式下的控制逻辑 |
| 报警处理模块 | i_WSAlarm, i_WSReset | tmp_bWSAlarmStatus, tmp_bWSOutput, tmp_nWSWorkstationStatus | 处理系统报警信号 |
| 状态报告模块 | 内部变量状态 | q_WSCommandStatus, q_WSWorkstationStatus | 向主控报告执行状态和工作站状态 |
| 状态监控模块 | 内部变量状态 | tmp_nWSStatusWord | 监控系统运行状态 |

## 6. 错误处理接口

### 6.1 错误类型

| 错误代码 | 错误名称 | 错误描述 | 处理方式 |
|----------|----------|----------|----------|
| 1 | 输入信号冲突 | 手动和自动信号同时激活 | 优先处理手动信号 |
| 2 | 输出异常 | 输出信号与预期状态不符 | 触发报警 |
| 3 | 运行超时 | 运行时间超过设定值 | 自动停止并报警 |
| 4 | 初始化失败 | 系统初始化未完成 | 保持初始状态 |
| 5 | 工作站未就绪 | 工作站未达到就绪状态 | 停止操作并报警 |
| 6 | 主控命令执行失败 | 主控命令执行过程中发生异常 | 向主控报告执行失败状态 |
| 7 | 状态报告失败 | 状态报告过程中发生异常 | 重试状态报告，必要时触发报警 |
| 8 | 无效命令 | 主控命令值不在有效范围内 | 忽略无效命令并向主控报告 |
| 9 | 无效参数 | 控制参数值不在有效范围内 | 忽略无效参数并向主控报告 |

### 6.2 错误检测与响应

| 错误检测点 | 检测方法 | 响应时间 | 处理措施 |
|----------|----------|----------|----------|
| 输入信号检测 | 实时检测输入信号状态 | 1个扫描周期 | 检测信号冲突 |
| 输出状态检测 | 实时检测输出信号状态 | 1个扫描周期 | 检测输出异常 |
| 运行时间检测 | 定期检测运行时间 | 1个扫描周期 | 检测运行超时 |
| 初始化状态检测 | 系统启动时检测 | 系统启动时 | 检测初始化状态 |
| 就绪状态检测 | 实时检测就绪状态 | 1个扫描周期 | 检测工作站就绪状态 |
| 主控命令检测 | 实时检测主控命令执行状态 | 1个扫描周期 | 检测命令执行失败 |
| 状态报告检测 | 实时检测状态报告过程 | 1个扫描周期 | 检测状态报告失败 |
| 命令有效性检测 | 实时检测命令值范围 | 1个扫描周期 | 检测无效命令 |
| 参数有效性检测 | 实时检测参数值范围 | 1个扫描周期 | 检测无效参数 |

### 6.3 错误恢复

| 错误类型 | 恢复条件 | 恢复方式 | 恢复时间 |
|----------|----------|----------|----------|
| 输入信号冲突 | 冲突信号消失 | 自动恢复 | 1个扫描周期 |
| 输出异常 | 异常消除 | 手动复位 | 1个扫描周期 |
| 运行超时 | 超时条件消除 | 手动复位 | 1个扫描周期 |
| 初始化失败 | 系统重启 | 自动重试 | 系统启动时间 |
| 工作站未就绪 | 就绪条件满足 | 自动恢复 | 1个扫描周期 |
| 主控命令执行失败 | 异常条件消除 | 手动重试命令 | 1个扫描周期 |
| 状态报告失败 | 通信恢复 | 自动重试报告 | 1个扫描周期 |
| 无效命令 | 命令值修正 | 自动恢复 | 1个扫描周期 |
| 无效参数 | 参数值修正 | 自动恢复 | 1个扫描周期 |

## 7. 通信接口

### 7.1 通信协议

| 通信类型 | 协议 | 速率 | 详细说明 |
|----------|------|------|----------|
| PLC内部通信 | IEC 61131-3变量传递 | 扫描周期 | FB与主程序间的变量传递 |
| HMI通信 | Modbus TCP | 100Mbps | HMI与PLC间的通信 |
| 外部设备通信 | Modbus RTU | 9600bps | 与外部设备的通信 |
| 上下游通信 | Profinet | 1Gbps | 与上下游工作站的通信 |

### 7.2 通信数据格式

| 数据类型 | 字节数 | 格式 | 详细说明 |
|----------|----------|------|----------|
| BOOL | 1位 | 二进制 | 布尔值，0=False, 1=True |
| INT | 2字节 | 整数 | 16位有符号整数 |
| DINT | 4字节 | 整数 | 32位有符号整数 |
| REAL | 4字节 | 浮点数 | IEEE 754标准浮点数 |
| DWORD | 4字节 | 双字 | 32位无符号整数 |

### 7.3 通信错误处理

| 错误类型 | 检测方法 | 处理方式 | 优先级 |
|----------|----------|----------|--------|
| 通信超时 | 检测通信响应时间 | 重试机制 | 高 |
| 数据错误 | 检测数据校验和 | 丢弃错误数据 | 高 |
| 连接断开 | 检测连接状态 | 重连机制 | 高 |
| 通信冲突 | 检测通信总线状态 | 优先级仲裁 | 高 |

## 8. 集成指南

### 8.1 功能块实例化

```scl
// 实例化工作站FB功能块
FB_WorkstationControlInstance : FB_WorkstationControl;

// 连接输入变量
FB_WorkstationControlInstance.i_WSManualStart := i_WSStartButton;
FB_WorkstationControlInstance.i_WSManualStop := i_WSStopButton;
FB_WorkstationControlInstance.i_WSAutoStart := i_WSAutoMode;
FB_WorkstationControlInstance.i_WSAutoStop := i_WSAutoStop;
FB_WorkstationControlInstance.i_WSAlarm := i_WSSystemAlarm;
FB_WorkstationControlInstance.i_WSReset := i_WSResetButton;
FB_WorkstationControlInstance.i_WSMasterCommand := i_WSMasterCommand;
FB_WorkstationControlInstance.i_WSMasterCommandEnable := i_WSMasterCommandEnable;
FB_WorkstationControlInstance.i_WSControlParams := i_WSControlParams;
FB_WorkstationControlInstance.i_WSParamUpdate := i_WSParamUpdate;

// 使用输出变量
q_WSControlOutput := FB_WorkstationControlInstance.q_WSOutput;
q_WSAlarmStatus := FB_WorkstationControlInstance.q_WSAlarmStatus;
q_WSSystemStatus := FB_WorkstationControlInstance.q_WSStatusWord;
q_WSCommandStatus := FB_WorkstationControlInstance.q_WSCommandStatus;
q_WSWorkstationStatus := FB_WorkstationControlInstance.q_WSWorkstationStatus;
```

### 8.2 配置参数

| 参数名称 | 数据类型 | 默认值 | 范围 | 配置方法 |
|----------|----------|--------|------|----------|
| 运行超时时间 | INT | 30000 | 1000-3600000 | 通过PLC参数配置 |
| 报警延迟时间 | INT | 1000 | 0-10000 | 通过PLC参数配置 |
| 复位延迟时间 | INT | 500 | 0-5000 | 通过PLC参数配置 |
| 就绪检查时间 | INT | 5000 | 1000-60000 | 通过PLC参数配置 |

### 8.3 集成测试

| 测试项 | 测试目的 | 测试方法 | 判定标准 |
|--------|----------|----------|----------|
| 输入信号测试 | 验证输入信号接收 | 发送输入信号，检查内部状态 | 信号正确接收 |
| 输出信号测试 | 验证输出信号发送 | 触发输出，检查外部设备响应 | 信号正确发送 |
| 状态字测试 | 验证状态字更新 | 改变系统状态，检查状态字 | 状态字正确更新 |
| 错误处理测试 | 验证错误检测与处理 | 模拟错误情况，检查系统响应 | 错误正确处理 |
| 通信测试 | 验证通信功能 | 测试通信连接，检查数据传输 | 通信正常 |
| 就绪状态测试 | 验证就绪状态检测 | 模拟就绪条件，检查系统响应 | 就绪状态正确检测 |

## 9. 版本兼容性

### 9.1 版本历史

| 版本号 | 发布日期 | 主要变更 | 兼容性 |
|--------|----------|----------|----------|
| v1.0.0 | 2026-01-29 | 初始版本 | 完全兼容 |

### 9.2 兼容性说明
| 兼容性类型 | 详细说明 | 影响范围 |
|----------|----------|----------|
| 向前兼容 | 新版本兼容旧版本的输入/输出接口 | 无影响 |
| 向后兼容 | 旧版本不兼容新版本的新增功能 | 可能影响新功能使用 |
| 变量兼容性 | 变量名和数据类型保持一致 | 无影响 |
| 功能兼容性 | 核心功能保持一致 | 无影响 |

### 9.3 升级指南

| 升级步骤 | 详细说明 | 注意事项 |
|----------|----------|----------|
| 备份旧版本 | 备份旧版本的FB功能块和变量表 | 确保可回滚 |
| 导入新版本 | 导入新版本的FB功能块和变量表 | 确保变量名一致 |
| 测试验证 | 测试新版本的功能 | 确保功能正常 |
| 部署使用 | 部署新版本到生产环境 | 监控系统运行 |

## 10. 附录

### 10.1 接口示例代码

```scl
// 工作站FB功能块调用示例
PROGRAM Main
VAR
    // 输入变量
    i_WSStartButton : BOOL;
    i_WSStopButton : BOOL;
    i_WSAutoMode : BOOL;
    i_WSAutoStop : BOOL;
    i_WSSystemAlarm : BOOL;
    i_WSResetButton : BOOL;
    i_WSMasterCommand : INT;
    i_WSMasterCommandEnable : BOOL;
    i_WSControlParams : INT;
    i_WSParamUpdate : BOOL;
    
    // 输出变量
    q_WSControlOutput : BOOL;
    q_WSAlarmStatus : BOOL;
    q_WSSystemStatus : DWORD;
    q_WSCommandStatus : INT;
    q_WSWorkstationStatus : INT;
    
    // FB实例
    FB_WorkstationControlInstance : FB_WorkstationControl;
END_VAR

// 主程序
FB_WorkstationControlInstance(i_WSManualStart:=i_WSStartButton,
                             i_WSManualStop:=i_WSStopButton,
                             i_WSAutoStart:=i_WSAutoMode,
                             i_WSAutoStop:=i_WSAutoStop,
                             i_WSAlarm:=i_WSSystemAlarm,
                             i_WSReset:=i_WSResetButton,
                             i_WSMasterCommand:=i_WSMasterCommand,
                             i_WSMasterCommandEnable:=i_WSMasterCommandEnable,
                             i_WSControlParams:=i_WSControlParams,
                             i_WSParamUpdate:=i_WSParamUpdate);

q_WSControlOutput := FB_WorkstationControlInstance.q_WSOutput;
q_WSAlarmStatus := FB_WorkstationControlInstance.q_WSAlarmStatus;
q_WSSystemStatus := FB_WorkstationControlInstance.q_WSStatusWord;
q_WSCommandStatus := FB_WorkstationControlInstance.q_WSCommandStatus;
q_WSWorkstationStatus := FB_WorkstationControlInstance.q_WSWorkstationStatus;
END_PROGRAM
```

### 10.2 常见问题与解决方案

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 输入信号不响应 | 信号类型不匹配 | 检查信号类型和连接 |
| 输出信号异常 | 输出参数配置错误 | 检查输出参数配置 |
| 状态字更新异常 | 内部状态管理错误 | 检查状态机逻辑 |
| 通信连接失败 | 通信参数配置错误 | 检查通信参数配置 |
| 系统初始化失败 | 初始化条件不满足 | 检查初始化条件 |
| 工作站未就绪 | 就绪条件不满足 | 检查工作站硬件状态 |

### 10.3 参考资料

| 资料名称 | 版本 | 来源 |
|----------|------|------|
| IEC 61131-3标准 | 2013 | 国际电工委员会 |
| 汇川Autoshop编程手册 | V1.0 | 汇川技术 |
| PLC通信协议手册 | V1.0 | 设备制造商 |
| 工作站设计规范 | V1.0 | 内部文档 |