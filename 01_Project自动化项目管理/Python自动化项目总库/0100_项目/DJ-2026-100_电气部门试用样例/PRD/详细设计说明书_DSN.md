# 详细设计说明书（DSN）- DJ-2026-100 电气部门试用样例

> **项目编号**: DJ-2026-100
> **项目名称**: 电气部门试用样例
> **文档版本**: V1.0.0
> **编制日期**: 2026-07-02
> **适用范围**: 电气部门试用样例 项目 (DJ-2026-100)
> **遵循规范**: IEC 61131-3, LSP-905 SCL编程规范, LSP-907 项目结构规范

## 1. 设计概述

### 1.1 设计目标

V0.5.2发布前冒烟测试项目

本详细设计说明书描述 电气部门试用样例 项目的 PLC 程序详细设计，作为编程实现的依据。设计遵循 LSP-905 SCL 编程规范和 LSP-907 项目结构规范，采用扁平化组件架构。

### 1.2 设计原则

- **模块化设计**: 遵循 LSP-905 编程规范，功能块单一职责
- **高内聚低耦合**: 工站 FB 为纯逻辑块，I/O 集中映射
- **统一命名规范**: 遵循匈牙利命名法 + 业务语义
- **可测试性**: 关键逻辑可独立测试，避免全局状态依赖
- **可维护性**: 函数/功能块单一职责，命名清晰，注释充分
- **可扩展性**: 避免硬编码，使用配置/常量，预留扩展接口

## 2. 系统架构

### 2.1 整体架构

采用扁平化组件架构，OB1 作为唯一协调层，直接调用各工站功能块。所有 I/O 映射通过 GlobalVars 数据块集中管理，工站功能块为纯逻辑块，不直接依赖物理地址。

```
  OB1 (主循环)
  ├── 初始化 (FirstScan)
  ├── fbExternal    (外部设备交互) → 安全联锁判断
  ├── fbConveyor    (输送机控制)
  ├── fbPickPlace   (取放料控制)
  ├── fbFeeder      (送料控制)
  └── fbCommonAlarm (公共报警)
```

### 2.2 模块划分

| 模块编号 | 模块名称 | 功能描述 | 依赖模块 | 文件路径 |
|---------|---------|---------|---------|---------|
| M-001 | OB1 | 主循环、FB 调用顺序管理 | 所有 FB | `OB1/OB1.scl` |
| M-002 | GlobalVars | 全局变量、I/O 映射 | 无 | `DB1/GlobalVars.db` |
| M-003 | conveyor | 输送机控制 | GlobalVars | `conveyor/` |
| M-004 | pickplace | 取放料控制 | GlobalVars | `pickplace/` |
| M-005 | feeder | 送料控制 | GlobalVars | `feeder/` |
| M-006 | external | 外部设备交互 | GlobalVars | `external/` |
| M-007 | common | 公共报警管理 | GlobalVars | `common/` |

## 3. 功能块设计

### 3.1 功能块清单

| FB编号 | FB名称 | 功能描述 | 输入参数 | 输出参数 | 文件路径 |
|--------|--------|---------|---------|---------|---------|
| FB-1002 | FB_1002_SingleLayerConveyor | 输送机控制 | i_bAutoMode, i_bStart... | q_bRunning, q_iAlarmCode... | `conveyor/` |
| FB-1003 | FB_1003_PickPlace | 取放料控制 | i_bAutoMode, i_iPickLayer... | q_iCurrentState, q_bRunning... | `pickplace/` |
| FB-1004 | FB_1004_GlueMachineFeeder | 送料控制 | i_bAutoMode, i_bPlaceDone... | q_bAllowPickup, q_bRunning... | `feeder/` |
| FB-External | FB_ExternalDeviceInteraction | 外部设备交互 | i_bEnable, i_bAutoMode... | q_bSystemSafetyConditionMet... | `external/` |
| FB-2001 | FB_2001_CommonAlarm | 公共报警 | i_iConveyorAlarm... | o_wGlobalAlarmWord... | `common/` |

### 3.2 功能块详细设计

#### 3.2.1 FB_1002_SingleLayerConveyor (输送机控制)

**功能**: 控制单层输送线的分料和输送功能，包含 9 步自动状态机和手动控制逻辑。

**输入参数**:
- `i_bAutoMode` (BOOL): 自动模式
- `i_bManualMode` (BOOL): 手动模式
- `i_bStart` (BOOL): 启动
- `i_bStop` (BOOL): 停止
- `i_iLayerIndex` (INT): 层号
- `i_bPreSeparateSensor` (BOOL): 分料前传感器
- `i_bPositionSensor1` (BOOL): 到位传感器1
- `i_bPositionSensor2` (BOOL): 到位传感器2
- `i_bBlockCylinderUp` (BOOL): 阻挡气缸上位
- `i_bBlockCylinderDown` (BOOL): 阻挡气缸下位
- `i_bSeparateCylinderUp` (BOOL): 分料气缸上位
- `i_bSeparateCylinderDown` (BOOL): 分料气缸下位
- `i_bSafetyDoorOk` (BOOL): 安全门正常
- `i_bVfdFault` (BOOL): 变频器故障
- `i_bPickupConfirmed` (BOOL): 取料确认

**输出参数**:
- `q_bBlockSolenoid` (BOOL): 阻挡电磁阀
- `q_bSeparateSolenoid` (BOOL): 分料电磁阀
- `q_bConveyorFwd` (BOOL): 输送带正转
- `q_bConveyorRev` (BOOL): 输送带反转
- `q_bConveyorSlow` (BOOL): 输送带慢速
- `q_iCurrentState` (INT): 当前状态
- `q_iAlarmCode` (INT): 报警码
- `q_bRunning` (BOOL): 运行中
- `q_bFault` (BOOL): 故障
- `q_bLayerFeedDone` (BOOL): 放料完成
- `q_bAnySensorFault` (BOOL): 传感器故障

#### 3.2.2 FB_1003_PickPlace (取放料控制)

**功能**: 控制Z轴升降、X1轴横移和4组夹爪的协同工作，实现取放料循环。6步状态机S20~S25，一次取两根边框，4层循环2次完成全部取料。

**关键输入参数**:
- `i_iPickLayer` (INT): 取料层号
- `i_bLayerFeedDone` (BOOL): 输送机放料完成
- `i_bLx_FrontClamp` (BOOL): 前夹紧原点
- `i_bLx_RearClamp` (BOOL): 后夹紧原点
- `i_bLx_LiftUp` (BOOL): 升降原点
- `i_bLx_LiftDown` (BOOL): 升降动点
- `i_bLiftHomePos` (BOOL): 升降原点位置
- `i_bLiftWorkPoint` (BOOL): 升降工作位置

**VAR_IN_OUT 参数** (V7.0.0+):
- `io_stZAxis` (ST_ServoAxis): Z轴伺服引用
- `io_stX1Axis` (ST_ServoAxis): X1轴伺服引用

## 4. 数据块设计

### 4.1 全局数据块

| DB编号 | DB名称 | 用途 | 主要变量 |
|--------|--------|------|---------|
| DB1 | GlobalVars | 全局变量、I/O 映射 | stConveyor, stPickPlace, stFeeder, stExternal, stGlobal |

### 4.2 GlobalVars 结构定义

```
DATA_BLOCK GlobalVars
STRUCT
    // 各工站变量结构体
    stConveyor   : ST_Conveyor;     // 输送机变量
    stPickPlace  : ST_PickPlace;    // 取放料变量
    stFeeder     : ST_Feeder;       // 送料变量
    stExternal   : ST_External;     // 外部设备变量
    stGlobal     : ST_Global;       // 全局变量
    
    // 伺服轴数组
    astServoAxis : ARRAY[1..3] OF ST_ServoAxis;
    
    // 功能块实例
    fbConveyor    : FB_1002_SingleLayerConveyor;
    fbPickPlace   : FB_1003_PickPlace;
    fbFeeder      : FB_1004_GlueMachineFeeder;
    fbExternal    : FB_ExternalDeviceInteraction;
    fbCommonAlarm : FB_2001_CommonAlarm;
END_STRUCT
```

## 5. 状态机设计

### 5.1 输送机状态机 (9步)

| 步骤 | 状态名称 | 转移条件 | 动作 | 超时报警 |
|------|---------|---------|------|---------|
| 0 | 待机 | i_bStart AND i_bAutoMode | 无 | 无 |
| 1 | 材料到达检测 | i_bPreSeparateSensor | 无 | A-001 |
| 2 | 阻挡气缸下降 | i_bBlockCylinderDown | q_bBlockSolenoid := TRUE | A-002 |
| 3 | 输送带正转 | i_bPositionSensor1 AND i_bPositionSensor2 | q_bConveyorFwd := TRUE | A-003 |
| 4 | 到位检测 | (自动转移) | 无 | A-004 |
| 5 | 阻挡气缸上升 | i_bBlockCylinderUp | q_bBlockSolenoid := FALSE | A-005 |
| 6 | 分料气缸推出 | i_bSeparateCylinderDown | q_bSeparateSolenoid := TRUE | A-006 |
| 7 | 慢速送出 | i_bPickupConfirmed | q_bConveyorSlow := TRUE | A-007 |
| 8 | 放料完成 | (自动返回0) | q_bLayerFeedDone := TRUE | 无 |

### 5.2 取放料状态机 (6步 S20~S25)

| 步骤 | 状态名称 | 转移条件 | 动作 |
|------|---------|---------|------|
| S20 | 等待放料完成 | i_bLayerFeedDone | 无 |
| S21 | Z轴下降+夹紧 | i_bLiftWorkPoint AND 夹紧确认 | q_bLiftDown, q_bFrontClamp |
| S22 | 产品检测 | 4传感器确认 | 无 |
| S23 | Z轴上升+X1横移 | i_bLiftHomePos AND X1到位 | q_bLiftUp, X1轴移动 |
| S24 | Z轴下降+松开 | i_bLiftWorkPoint | q_bLiftDown, 夹爪松开 |
| S25 | Z轴上升+通知 | i_bLiftHomePos | q_bLiftUp, q_bPlaceDoneToFeeder |

## 6. 报警设计

| 报警码段 | 报警类别 | 触发条件 | 处理方式 |
|---------|---------|---------|---------|
| 1~7 | 输送机报警 | 传感器故障/超时 | 停止运行，HMI 显示 |
| 101~108 | 取放料报警 | 夹紧失败/超时/轴故障 | 停止运行，HMI 显示 |
| 201~205 | 送料报警 | 交互超时/故障 | 停止运行，HMI 显示 |
| 300~312 | 外部设备报警 | 急停/故障/通讯异常 | 停止本机，HMI 显示 |

报警处理流程：
1. 各工站 FB 检测异常 → 置位 q_iAlarmCode
2. fbCommonAlarm 汇总各工站报警码
3. 计算全局报警字 (o_wGlobalAlarmWord)
4. 选取最高优先级报警 (o_iCurrentAlarmCode)
5. 写入 MES 报警队列 (去重)
6. 置位新报警脉冲标志 (o_bNewAlarmFlag)

## 7. 安全设计

### 7.1 系统使能逻辑

```
系统使能 = TRUE 需同时满足:
1. 急停按钮未按下 (NOT stExternal.i_bEStop)
2. 前安全门已锁定 (stExternal.i_bFrontDoorLocked)
3. 后安全门已锁定 (stExternal.i_bRearDoorLocked)
4. 外部设备无急停 (NOT 外部设备急停)
5. 外部设备无故障 (NOT 外部设备故障)
```

### 7.2 工站间互锁

- 取放料需等待输送机放料完成 (i_bLayerFeedDone)
- 送料需等待取放料放料完成 (i_bPlaceDone)
- 外部设备交互失败时停止本机

## 8. 变更记录

| 日期 | 版本 | 变更内容 | 变更人 |
|------|------|---------|--------|
| 2026-07-02 | V1.0.0 | 初始版本 | auto-pm |
