# 主控站接口文档

## 文档标识
- **文档类型**：接口文档
- **版本号**：v1.0.0
- **创建日期**：2026-01-29
- **最后更新**：2026-01-31
- **文档状态**：已完成

## 变更记录
| 变更日期 | 变更原因 | 变更内容 | 变更人 |
|---------|---------|---------|--------|
| 2026-01-29 | 模板创建 | 创建交互接口文档模板 | 系统 |
| 2026-01-31 | 功能变更 | 将交互接口变更为主控站接口，添加工作站和外部通讯接口 | 系统 |

## 1. 接口概述

### 1.1 接口功能
FB_MainControlStation功能块提供主控站对各工作站的监控和控制接口，以及与外部系统的通讯对接接口，确保系统稳定运行，包含完整的错误处理和状态监控机制。

### 1.2 接口特性
- **标准化接口**：严格遵循IEC 61131-3标准
- **模块化设计**：采用六大模块结构
- **状态机管理**：使用状态机实现工作站和通讯的有序管理
- **错误处理**：包含完整的超时和报警处理机制
- **测试支持**：提供内置测试模式
- **可扩展性**：支持工作站数量和类型的灵活扩展

### 1.3 接口应用场景
- 自动化生产线的中央控制系统
- 多工作站协同工作的工业场景
- 需要与外部系统（MES/ERP/HMI）集成的系统
- 具备全面监控和控制需求的工业自动化系统
- 要求高可靠性和故障处理能力的生产环境

## 2. 输入接口

### 2.1 工作站信号输入

| 接口名称 | 变量名 | 数据类型 | 描述 | 连接说明 |
|----------|--------|----------|------|----------|
| 工作站准备好信号 | i_WorkstationReady[MAX_WORKSTATIONS] | BOOL[] | 各工作站准备就绪状态 | 连接到各工作站的准备好输出信号 |
| 工作站运行信号 | i_WorkstationRunning[MAX_WORKSTATIONS] | BOOL[] | 各工作站运行状态 | 连接到各工作站的运行状态信号 |
| 工作站错误信号 | i_WorkstationError[MAX_WORKSTATIONS] | BOOL[] | 各工作站错误状态 | 连接到各工作站的错误输出信号 |
| 工作站循环完成信号 | i_WorkstationCycleComplete[MAX_WORKSTATIONS] | BOOL[] | 各工作站循环完成信号 | 连接到各工作站的循环完成输出信号 |
| 工作站启动信号 | i_WorkstationStart[MAX_WORKSTATIONS] | BOOL[] | 各工作站启动控制信号 | 连接到HMI或控制面板的工作站启动按钮 |
| 工作站停止信号 | i_WorkstationStop[MAX_WORKSTATIONS] | BOOL[] | 各工作站停止控制信号 | 连接到HMI或控制面板的工作站停止按钮 |
| 工作站参数变更信号 | i_WorkstationParamChanged[MAX_WORKSTATIONS] | BOOL[] | 各工作站参数变更信号 | 连接到HMI或参数设置界面的参数变更确认按钮 |
| 工作站参数值 | i_WorkstationParam[MAX_WORKSTATIONS] | REAL[] | 各工作站参数设置值 | 连接到HMI或参数设置界面的参数输入 |

### 2.2 外部通讯输入

| 接口名称 | 变量名 | 数据类型 | 描述 | 连接说明 |
|----------|--------|----------|------|----------|
| MES系统连接信号 | i_MESConnect | BOOL | MES系统连接状态 | 连接到MES系统的连接状态信号 |
| ERP系统连接信号 | i_ERPConnect | BOOL | ERP系统连接状态 | 连接到ERP系统的连接状态信号 |
| HMI系统连接信号 | i_HMIConnect | BOOL | HMI系统连接状态 | 连接到HMI系统的连接状态信号 |

### 2.3 控制信号输入

| 接口名称 | 变量名 | 数据类型 | 描述 | 连接说明 |
|----------|--------|----------|------|----------|
| 开始生产信号 | i_StartProduction | BOOL | 开始生产控制信号 | 连接到HMI或控制面板的开始生产按钮 |
| 重置生产信号 | i_ResetProduction | BOOL | 重置生产控制信号 | 连接到HMI或控制面板的重置生产按钮 |
| 复位信号 | i_Reset | BOOL | 系统复位信号 | 连接到HMI或控制面板的复位按钮 |

## 3. 输出接口

### 3.1 工作站控制输出

| 接口名称 | 变量名 | 数据类型 | 描述 | 连接说明 |
|----------|--------|----------|------|----------|
| 工作站启动控制信号 | q_WorkstationStart[MAX_WORKSTATIONS] | BOOL[] | 各工作站启动控制信号 | 连接到各工作站的启动控制输入 |
| 工作站参数输出 | q_WorkstationParam[MAX_WORKSTATIONS] | REAL[] | 各工作站参数设置值 | 连接到各工作站的参数输入 |
| 工作站参数更新信号 | q_WorkstationParamUpdate[MAX_WORKSTATIONS] | BOOL[] | 各工作站参数更新确认信号 | 连接到各工作站的参数更新确认输入 |

### 3.2 外部通讯输出

| 接口名称 | 变量名 | 数据类型 | 描述 | 连接说明 |
|----------|--------|----------|------|----------|
| MES数据上传信号 | q_MESDataUpload | BOOL | MES数据上传状态 | 连接到MES系统的数据上传确认输入 |
| MES生产数据 | q_MESProductionData | STRING | 上传到MES系统的生产数据 | 连接到MES系统的生产数据输入 |
| ERP数据同步信号 | q_ERPDataSync | BOOL | ERP数据同步状态 | 连接到ERP系统的数据同步确认输入 |
| ERP库存数据 | q_ERPInventoryData | STRING | 同步到ERP系统的库存数据 | 连接到ERP系统的库存数据输入 |
| HMI系统状态 | q_HMISystemStatus | DWORD | 发送到HMI系统的系统状态字 | 连接到HMI系统的系统状态输入 |
| HMI工作站状态 | q_HMIWorkstationStatus | INT[MAX_WORKSTATIONS] | 发送到HMI系统的工作站状态 | 连接到HMI系统的工作站状态输入 |

### 3.3 状态监控输出

| 接口名称 | 变量名 | 数据类型 | 描述 | 连接说明 |
|----------|--------|----------|------|----------|
| 系统准备好信号 | q_SystemReady | BOOL | 主控站系统准备就绪状态 | 连接到监控系统的系统准备好输入 |
| 报警激活信号 | q_AlarmActive | BOOL | 系统报警激活状态 | 连接到报警系统的报警输入 |
| 状态字 | q_StatusWord | DWORD | 主控站系统当前状态的二进制表示 | 连接到HMI或监控系统的状态显示 |

## 4. 状态字定义

### 4.1 状态字位定义

| 位 | 名称 | 描述 | 取值范围 |
|----|------|------|----------|
| 0 | 系统就绪 | 主控站系统准备就绪状态 | 0-未准备好，1-准备好 |
| 1 | 工作站就绪 | 所有工作站准备就绪状态 | 0-未就绪，1-就绪 |
| 2 | 生产中 | 系统处于生产运行状态 | 0-未运行，1-运行中 |
| 3 | 生产完成 | 系统处于生产完成状态 | 0-未完成，1-已完成 |
| 4 | MES连接 | MES系统连接状态 | 0-未连接，1-已连接 |
| 5 | ERP连接 | ERP系统连接状态 | 0-未连接，1-已连接 |
| 6 | HMI连接 | HMI系统连接状态 | 0-未连接，1-已连接 |
| 7 | 错误状态 | 系统错误状态 | 0-正常，1-错误 |
| 8-15 | 预留 | 预留未来使用 | 0 |
| 16-23 | 工作站错误 | 各工作站错误状态 | 0-正常，1-错误 |
| 24-31 | 预留 | 预留未来使用 | 0 |

### 4.2 状态字示例

| 状态描述 | 状态字值 | 二进制表示 |
|----------|----------|------------|
| 初始状态 | 0x1000 | 0001000000000000 |
| 系统就绪 | 0x1001 | 0001000000000001 |
| 工作站就绪 | 0x1003 | 0001000000000011 |
| 生产运行 | 0x1007 | 0001000000000111 |
| 生产完成 | 0x100F | 0001000000001111 |
| 外部系统连接 | 0x107F | 0001000001111111 |
| 工作站错误 | 0x1F7F | 0001111101111111 |
| 系统错误 | 0x3F7F | 0011111101111111 |

## 5. 内部接口

### 5.1 内部变量

| 变量名 | 数据类型 | 描述 | 作用范围 |
|--------|----------|------|----------|
| b_FirstScan | BOOL | 首次扫描标志 | 功能块内部 |
| b_SystemReady | BOOL | 系统准备好状态 | 功能块内部 |
| b_Error | BOOL | 错误状态 | 功能块内部 |
| b_AllWorkstationsReady | BOOL | 所有工作站准备就绪 | 功能块内部 |
| b_AllWorkstationsCompleted | BOOL | 所有工作站完成 | 功能块内部 |
| b_MESConnected | BOOL | MES系统连接状态 | 功能块内部 |
| b_ERPConnected | BOOL | ERP系统连接状态 | 功能块内部 |
| b_HMIConnected | BOOL | HMI系统连接状态 | 功能块内部 |
| b_WorkstationReady[MAX_WORKSTATIONS] | BOOL[] | 工作站准备好内部状态 | 功能块内部 |
| b_WorkstationRunning[MAX_WORKSTATIONS] | BOOL[] | 工作站运行内部状态 | 功能块内部 |
| b_WorkstationError[MAX_WORKSTATIONS] | BOOL[] | 工作站错误内部状态 | 功能块内部 |
| n_WorkstationStatus[MAX_WORKSTATIONS] | INT[] | 工作站状态码 | 功能块内部 |
| n_WorkstationCycleCount[MAX_WORKSTATIONS] | INT[] | 工作站循环计数 | 功能块内部 |
| n_CurrentState | INT | 当前状态机状态 | 功能块内部 |
| n_ProductionPhase | INT | 生产阶段 | 功能块内部 |
| s_AlarmMessage | STRING | 报警消息 | 功能块内部 |
| s_ProductionData | STRING | 生产数据 | 功能块内部 |
| s_InventoryData | STRING | 库存数据 | 功能块内部 |
| i | INT | 循环计数器 | 功能块内部 |
| In_tTimer1 | BOOL[6] | 计时器输入数组 | 功能块内部 |
| ET_tTimer1 | TIME[6] | 计时器输出数组 | 功能块内部 |

### 5.2 计时器接口

| 计时器索引 | 输入变量 | 输出变量 | 预设时间 | 用途 |
|------------|----------|----------|----------|------|
| 0 | In_tTimer1[0] | ET_tTimer1[0] | T#30s | 系统初始化超时 |
| 1 | In_tTimer1[1] | ET_tTimer1[1] | T#10s | 工作站连接超时 |
| 2 | In_tTimer1[2] | ET_tTimer1[2] | T#15s | MES系统连接超时 |
| 3 | In_tTimer1[3] | ET_tTimer1[3] | T#15s | ERP系统连接超时 |
| 4 | In_tTimer1[4] | ET_tTimer1[4] | T#5s | HMI系统连接超时 |
| 5 | In_tTimer1[5] | ET_tTimer1[5] | T#60s | 生产周期超时 |

## 6. 接口交互流程

### 6.1 正常交互流程

1. **初始化阶段**：
   - 主控站系统启动并初始化
   - 建立与各工作站的连接
   - 连接外部通讯系统
   - 系统进入待机状态

2. **生产准备阶段**：
   - 主控站检查各工作站准备状态
   - 确认所有工作站准备就绪
   - 接收并处理外部系统（MES/ERP）的生产计划
   - 系统进入生产准备完成状态

3. **生产运行阶段**：
   - 主控站发送启动指令到各工作站
   - 实时监控各工作站运行状态
   - 与外部系统同步生产数据
   - 处理生产过程中的异常情况
   - 系统进入生产运行状态

4. **生产完成阶段**：
   - 主控站确认所有工作站任务完成
   - 收集生产数据和报表
   - 与外部系统同步生产完成信息
   - 清理生产现场状态
   - 系统进入生产完成状态

### 6.2 错误处理流程

1. **工作站错误**：
   - 收到工作站错误信号（i_WorkstationError[i] = TRUE）
   - 主控站设置错误状态（b_Error = TRUE）
   - 状态字错误位设置（q_StatusWord.7 = TRUE）
   - 状态字相应工作站错误位设置（q_StatusWord[i+16] = TRUE）
   - 生成报警信息（s_AlarmMessage）
   - 激活报警信号（q_AlarmActive = TRUE）

2. **通讯错误**：
   - 外部系统通讯超时或失败
   - 主控站设置错误状态（b_Error = TRUE）
   - 状态字错误位设置（q_StatusWord.7 = TRUE）
   - 状态字相应通讯错误位设置
   - 生成报警信息（s_AlarmMessage）
   - 激活报警信号（q_AlarmActive = TRUE）

3. **故障恢复**：
   - 收到复位信号（i_Reset = TRUE）
   - 主控站清除错误状态（b_Error = FALSE）
   - 状态字错误位清除（q_StatusWord.7 = FALSE）
   - 清除所有工作站错误状态位
   - 清除报警信息和信号
   - 系统恢复正常运行

## 7. 测试接口

### 7.1 测试模式接口

| 测试模式 | 功能描述 | 测试步骤 |
|----------|----------|----------|
| 0 | 完整流程测试 | 测试主控站完整工作流程 |
| 1 | 工作站监控测试 | 测试工作站状态监控功能 |
| 2 | 工作站控制测试 | 测试工作站控制功能 |
| 3 | MES系统通讯测试 | 测试与MES系统的通讯功能 |
| 4 | ERP系统通讯测试 | 测试与ERP系统的通讯功能 |
| 5 | 报警处理测试 | 测试报警和故障处理功能 |

### 7.2 测试接口使用

1. **设置测试模式**：通过i_TestMode变量设置测试模式
2. **启动测试**：功能块自动开始测试流程
3. **监控测试状态**：通过状态字和输出变量监控测试状态
4. **测试完成**：测试完成后，功能块返回测试结果

## 8. 接口配置与集成

### 8.1 Autoshop集成步骤

1. **导入变量表格**：
   - 在Autoshop中导入FB_导入PLC变量_项目名称_autoshop_vX.Y.Z.csv
   - 确认无乱码和格式错误

2. **导入FB功能块**：
   - 在Autoshop中导入FB_主控站功能块.scl
   - 确认编译通过

3. **实例化FB**：
   - 在程序中实例化FB_MainControlStation
   - 为实例分配符号名，如FB_MainControlStationInstance

4. **配置工作站参数**：
   - 根据实际工作站数量设置MAX_WORKSTATIONS参数
   - 根据实际系统需求调整计时器预设值

5. **连接输入输出变量**：
   - 连接输入变量到实际设备信号
   - 连接输出变量到实际设备或其他功能块

6. **配置外部通讯参数**：
   - 根据实际外部系统配置通讯参数
   - 设置适当的通讯超时时间

### 8.2 与其他系统集成

| 系统类型 | 集成方式 | 连接说明 |
|----------|----------|----------|
| HMI系统 | 通过状态字和输出变量 | 连接q_StatusWord到HMI状态显示，连接q_HMIWorkstationStatus到HMI工作站状态显示 |
| MES系统 | 通过数据上传接口 | 连接q_MESDataUpload和q_MESProductionData到MES系统的数据输入 |
| ERP系统 | 通过数据同步接口 | 连接q_ERPDataSync和q_ERPInventoryData到ERP系统的数据输入 |
| 监控系统 | 通过状态字和报警信号 | 连接q_StatusWord到监控系统的状态输入，连接q_AlarmActive到报警系统 |
| 工作站系统 | 通过工作站控制接口 | 连接工作站输入输出变量到各工作站的相应接口 |

## 9. 接口性能与可靠性

### 9.1 性能指标

| 指标名称 | 性能值 | 测试条件 |
|----------|--------|----------|
| 信号响应时间 | <10ms | 标准PLC扫描周期 |
| 状态切换时间 | <50ms | 正常运行条件 |
| 错误检测时间 | <100ms | 超时或报警触发 |
| 故障恢复时间 | <200ms | 复位信号触发 |
| 最大工作站数量 | 16 | 标准配置 |
| 通讯响应时间 | <100ms | 正常网络条件 |
| 数据处理能力 | 1000条/分钟 | 生产数据处理 |

### 9.2 可靠性设计

| 可靠性措施 | 描述 | 实现方式 |
|------------|------|----------|
| 超时保护 | 所有操作设置超时计时器 | 使用TON计时器和时间比较 |
| 错误检测 | 全面的错误检测机制 | 状态监控和逻辑判断 |
| 故障隔离 | 单个工作站错误不影响整个系统 | 模块化设计和错误处理 |
| 冗余设计 | 关键信号和通讯有冗余处理 | 状态机和多重验证 |
| 状态监控 | 实时监控所有工作站和通讯状态 | 状态字和输出变量 |
| 数据备份 | 定期备份生产数据 | 与外部系统同步和本地存储 |

### 9.3 故障排查

| 故障现象 | 可能原因 | 排查方法 |
|----------|----------|----------|
| 工作站通讯失败 | 网络连接问题或工作站故障 | 检查网络连接和工作站状态 |
| 外部系统连接异常 | 通讯配置错误或外部系统故障 | 检查通讯配置和外部系统状态 |
| 状态显示异常 | 内部状态错误或数据传输问题 | 检查状态机逻辑和数据传输 |
| 超时错误 | 设备响应时间过长或通讯延迟 | 检查设备状态，调整超时设置 |
| 编译错误 | 变量未定义或格式错误 | 检查变量表和FB代码，确保一致 |
| 运行不稳定 | 信号冲突或时序错误 | 检查信号顺序，使用状态机管理 |

## 10. 接口版本管理

### 10.1 版本历史

| 版本号 | 发布日期 | 变更内容 | 兼容性 |
|--------|----------|----------|----------|
| v1.0.0 | 2026-01-29 | 初始版本，实现基本功能 | 完全兼容 |
| v1.0.1 | 2026-01-31 | 功能扩展，增加工作站和外部通讯接口 | 向下兼容 |

### 10.2 版本兼容性
- **向下兼容**：新版本保持对旧版本的接口兼容
- **变量兼容性**：变量名和数据类型保持不变
- **功能兼容性**：基本功能保持不变，仅增加新功能
- **错误处理兼容性**：错误处理机制保持一致
- **扩展兼容性**：支持工作站数量和类型的扩展

### 10.3 版本升级指南

1. **备份旧版本**：备份旧版本的FB和变量表文件
2. **导入新版本**：导入新版本的FB和变量表文件
3. **更新实例**：更新程序中的FB实例
4. **配置扩展参数**：根据实际需求配置工作站数量和外部通讯参数
5. **验证功能**：验证系统功能是否正常
6. **测试运行**：进行测试运行，确保系统稳定

## 11. 接口使用示例

### 11.1 基本使用示例

```scl
// 实例化主控站功能块
FB_MainControlStationInstance: FB_MainControlStation;

// 主程序
NETWORK
// 连接工作站输入变量
FOR i := 0 TO MAX_WORKSTATIONS - 1 DO
    FB_MainControlStationInstance.i_WorkstationReady[i] := Sensor_WorkstationReady[i];
    FB_MainControlStationInstance.i_WorkstationRunning[i] := Sensor_WorkstationRunning[i];
    FB_MainControlStationInstance.i_WorkstationError[i] := Sensor_WorkstationError[i];
    FB_MainControlStationInstance.i_WorkstationCycleComplete[i] := Sensor_WorkstationCycleComplete[i];
    FB_MainControlStationInstance.i_WorkstationStart[i] := HMI_WorkstationStart[i];
    FB_MainControlStationInstance.i_WorkstationStop[i] := HMI_WorkstationStop[i];
    FB_MainControlStationInstance.i_WorkstationParam[i] := HMI_WorkstationParam[i];
    FB_MainControlStationInstance.i_WorkstationParamChanged[i] := HMI_WorkstationParamChanged[i];
END_FOR;

// 连接外部通讯输入变量
FB_MainControlStationInstance.i_MESConnect := MES_Connect;
FB_MainControlStationInstance.i_ERPConnect := ERP_Connect;
FB_MainControlStationInstance.i_HMIConnect := HMI_Connect;

// 连接控制输入变量
FB_MainControlStationInstance.i_StartProduction := HMI_StartProduction;
FB_MainControlStationInstance.i_ResetProduction := HMI_ResetProduction;
FB_MainControlStationInstance.i_Reset := HMI_Reset;

// 调用功能块
FB_MainControlStationInstance();

// 连接工作站输出变量
FOR i := 0 TO MAX_WORKSTATIONS - 1 DO
    Output_WorkstationStart[i] := FB_MainControlStationInstance.q_WorkstationStart[i];
    Output_WorkstationParam[i] := FB_MainControlStationInstance.q_WorkstationParam[i];
    Output_WorkstationParamUpdate[i] := FB_MainControlStationInstance.q_WorkstationParamUpdate[i];
END_FOR;

// 连接外部通讯输出变量
Output_MESDataUpload := FB_MainControlStationInstance.q_MESDataUpload;
Output_MESProductionData := FB_MainControlStationInstance.q_MESProductionData;
Output_ERPDataSync := FB_MainControlStationInstance.q_ERPDataSync;
Output_ERPInventoryData := FB_MainControlStationInstance.q_ERPInventoryData;
Output_HMISystemStatus := FB_MainControlStationInstance.q_HMISystemStatus;
Output_HMIWorkstationStatus := FB_MainControlStationInstance.q_HMIWorkstationStatus;

// 连接状态监控输出变量
Output_SystemReady := FB_MainControlStationInstance.q_SystemReady;
Output_AlarmActive := FB_MainControlStationInstance.q_AlarmActive;
HMI_StatusWord := FB_MainControlStationInstance.q_StatusWord;
```

### 11.2 测试使用示例

```scl
// 实例化测试功能块
Test_FB_MainControlStation: Test_FB_MainControlStation;

// 测试程序
NETWORK
// 设置测试模式
Test_FB_MainControlStation.i_TestMode := 0; // 完整流程测试

// 调用测试功能块
Test_FB_MainControlStation();

// 监控测试状态
HMI_TestStatus := Test_FB_MainControlStation.q_TestStatus;
HMI_TestStep := Test_FB_MainControlStation.q_TestStep;
HMI_TestCompleted := Test_FB_MainControlStation.q_TestCompleted;
HMI_TestMessage := Test_FB_MainControlStation.q_TestMessage;
```

## 12. 总结

### 12.1 接口优势
- **标准化设计**：严格遵循IEC 61131-3标准
- **模块化结构**：六大模块清晰分离，便于维护和扩展
- **全面监控**：实时监控所有工作站和通讯状态
- **强大控制**：灵活控制各工作站运行和参数调整
- **外部集成**：完善的外部系统通讯接口
- **错误处理**：完整的错误检测和恢复机制
- **测试支持**：内置测试模式，便于调试和验证
- **易于集成**：标准化接口，易于与其他系统集成
- **可扩展性**：支持工作站数量和类型的灵活扩展

### 12.2 应用建议
- **工作站配置**：根据实际生产需求配置工作站数量和类型
- **超时设置**：根据实际设备响应时间和通讯延迟调整超时值
- **错误处理**：合理配置错误处理参数和报警级别
- **测试验证**：在实际应用前进行充分的功能测试和负载测试
- **定期维护**：定期检查信号连接、系统状态和通讯配置
- **参数优化**：根据生产实际情况优化工作站运行参数
- **数据管理**：合理配置数据采集和存储策略

### 12.3 未来扩展
- **增加通信协议**：支持更多工业通信协议，如Modbus、Profinet、EtherCAT等
- **增强诊断功能**：提供更详细的故障诊断和预测性维护信息
- **优化性能**：进一步提高信号处理速度和系统响应时间
- **扩展测试功能**：增加更多测试模式和场景
- **支持远程监控**：增加远程监控和调试能力
- **集成人工智能**：引入AI技术进行生产优化和故障预测
- **增强安全性**：增加 cybersecurity 功能，保护系统安全