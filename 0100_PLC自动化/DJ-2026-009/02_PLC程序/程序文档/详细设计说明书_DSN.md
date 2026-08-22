# 详细设计说明书 - DJ-2026-009 长边框堆垛机

> **项目编号**: DJ-2026-009
> **项目名称**: 长边框堆垛机
> **文档版本**: V1.0.0
> **编制日期**: 2026-08-21
> **适用范围**: 长边框堆垛机 项目 (DJ-2026-009)
> **遵循规范**: IEC 61131-3, LSP-905 SCL编程规范, LSP-907 项目结构规范

## 1. 设计概述

### 1.1 设计目标

长边框堆垛机

本设计说明书描述 长边框堆垛机 项目的 PLC 程序详细设计，包括系统架构、功能块设计、数据块设计、状态机设计、报警设计等内容。

### 1.2 设计原则

- **模块化设计**: 遵循 LSP-905 编程规范，功能块单一职责
- **高内聚低耦合**: 工站 FB 为纯逻辑块，I/O 集中映射
- **统一命名规范**: 遵循匈牙利命名法 + 业务语义
- **可测试性**: 关键逻辑可独立测试，避免全局状态依赖
- **可维护性**: 函数/功能块单一职责，命名清晰，注释充分

## 2. 系统架构

### 2.1 整体架构

采用扁平化组件架构，OB1 作为唯一协调层，直接调用各工站功能块。所有 I/O 映射通过 GlobalVars 数据块集中管理。

```
  OB1 (主循环)
  ├── fbConveyor    (输送机控制)
  ├── fbPickPlace   (取放料控制)
  ├── fbFeeder      (送料控制)
  ├── fbExternal    (外部设备交互)
  └── fbCommonAlarm (公共报警)
```

### 2.2 模块划分

| 模块编号 | 模块名称 | 功能描述 | 依赖模块 |
|---------|---------|---------|---------|
| M-001 | OB1 | 主循环、FB 调用顺序管理 | 所有 FB |
| M-002 | GlobalVars | 全局变量、I/O 映射 | 无 |
| M-003 | conveyor | 输送机控制 | GlobalVars |
| M-004 | pickplace | 取放料控制 | GlobalVars |
| M-005 | feeder | 送料控制 | GlobalVars |
| M-006 | external | 外部设备交互 | GlobalVars |
| M-007 | common | 公共报警管理 | GlobalVars |

## 3. 功能块设计

### 3.1 功能块清单

| FB编号 | FB名称 | 功能描述 | 输入参数 | 输出参数 |
|--------|--------|---------|---------|---------|
| FB-1002 | FB_1002_SingleLayerConveyor | 输送机控制 | i_bAutoMode, i_bStart... | q_bRunning, q_iAlarmCode... |
| FB-1003 | FB_1003_PickPlace | 取放料控制 | i_bAutoMode, i_iPickLayer... | q_iCurrentState, q_bRunning... |
| FB-1004 | FB_1004_GlueMachineFeeder | 送料控制 | i_bAutoMode, i_bPlaceDone... | q_bAllowPickup, q_bRunning... |
| FB-External | FB_ExternalDeviceInteraction | 外部设备交互 | i_bEnable, i_bAutoMode... | q_bSystemSafetyConditionMet... |
| FB-2001 | FB_2001_CommonAlarm | 公共报警 | i_iConveyorAlarm... | o_wGlobalAlarmWord... |

### 3.2 功能块详细设计

#### 3.2.1 FB_1002_SingleLayerConveyor (输送机控制)

**功能**: 控制单层输送线的分料和输送功能，包含 9 步自动状态机和手动控制逻辑。

**输入参数**:
- `i_bAutoMode` (BOOL): 自动模式
- `i_bManualMode` (BOOL): 手动模式
- `i_bStart` (BOOL): 启动
- `i_bStop` (BOOL): 停止
- `i_bPreSeparateSensor` (BOOL): 分料前传感器
- `i_bPositionSensor1` (BOOL): 到位传感器1
- `i_bPositionSensor2` (BOOL): 到位传感器2

**输出参数**:
- `q_bBlockSolenoid` (BOOL): 阻挡电磁阀
- `q_bSeparateSolenoid` (BOOL): 分料电磁阀
- `q_bConveyorFwd` (BOOL): 输送带正转
- `q_iCurrentState` (INT): 当前状态
- `q_iAlarmCode` (INT): 报警码
- `q_bRunning` (BOOL): 运行中
- `q_bFault` (BOOL): 故障

## 4. 数据块设计

### 4.1 全局数据块

| DB编号 | DB名称 | 用途 | 主要变量 |
|--------|--------|------|---------|
| DB1 | GlobalVars | 全局变量、I/O 映射 | stConveyor, stPickPlace, stFeeder, stExternal, stGlobal |

### 4.2 GlobalVars 结构

```
DATA_BLOCK GlobalVars
STRUCT
    stConveyor   : ST_Conveyor;     // 输送机变量
    stPickPlace  : ST_PickPlace;    // 取放料变量
    stFeeder     : ST_Feeder;       // 送料变量
    stExternal   : ST_External;     // 外部设备变量
    stGlobal     : ST_Global;       // 全局变量
    
    fbConveyor    : FB_1002_SingleLayerConveyor;
    fbPickPlace   : FB_1003_PickPlace;
    fbFeeder      : FB_1004_GlueMachineFeeder;
    fbExternal    : FB_ExternalDeviceInteraction;
    fbCommonAlarm : FB_2001_CommonAlarm;
END_STRUCT
```

## 5. 状态机设计

### 5.1 输送机状态机 (9步)

| 步骤 | 状态名称 | 转移条件 | 动作 |
|------|---------|---------|------|
| 0 | 待机 | i_bStart | 无 |
| 1 | 材料到达检测 | i_bPreSeparateSensor | 无 |
| 2 | 阻挡气缸下降 | 阻挡下位 | q_bBlockSolenoid := TRUE |
| 3 | 输送带正转 | 到位检测 | q_bConveyorFwd := TRUE |
| 4 | 到位检测 | i_bPositionSensor1 AND i_bPositionSensor2 | 无 |
| 5 | 阻挡气缸上升 | 阻挡上位 | q_bBlockSolenoid := FALSE |
| 6 | 分料气缸推出 | 分料前位 | q_bSeparateSolenoid := TRUE |
| 7 | 慢速送出 | 放料完成 | q_bConveyorSlow := TRUE |
| 8 | 放料完成 | i_bPickupConfirmed | 无 |

## 6. 报警设计

| 报警码 | 报警描述 | 触发条件 | 处理方式 |
|--------|---------|---------|---------|
| 1~7 | 输送机报警 | 传感器故障/超时 | 停止运行，HMI 显示 |
| 101~108 | 取放料报警 | 夹紧失败/超时 | 停止运行，HMI 显示 |
| 201~205 | 送料报警 | 交互超时/故障 | 停止运行，HMI 显示 |
| 300~312 | 外部设备报警 | 急停/故障/通讯异常 | 停止本机，HMI 显示 |

## 7. 版本更新记录

| 版本 | 日期 | 更新内容 | 编制人 |
|------|------|----------|--------|
| V1.0.0 | 2026-08-21 | 初始版本 | auto-pm |
