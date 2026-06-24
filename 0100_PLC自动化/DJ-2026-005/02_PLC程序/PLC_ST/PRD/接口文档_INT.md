---
spec_id: INT-DJ-2026-005-PLC_ST
title: "DJ-2026-005 边框缓存机 PLC 程序接口文档"
version: "V7.1.1"
domain: plc
lifecycle: active
tags: ["接口文档", "PLC程序"]
---

# 接口文档 DJ-2026-005 边框缓存机 PLC 程序

## 1. 文档基础信息

**文档标题**：DJ-2026-005 边框缓存机 PLC 程序接口文档
**文档版本**：V7.1.1
**编制日期**：2026-06-23
**编制人**：Trae
**审核人**：[待审核]
**遵循规范**：INT-815, LSP-905

## 2. 版本变更记录

| 版本号 | 变更内容 | 变更人 | 变更日期 |
|--------|----------|--------|----------|
| V7.1.1 | 填写实际内容 | Trae | 2026-06-23 | 从GlobalVars和各FB接口汇总程序级接口 |
| V1.0.0 | 初始创建 | auto-pm | 2026-06-19 | 项目初始化自动生成空模板 |

## 3. 接口概述

本文档为 PLC 程序级接口总览，汇总各功能块的接口签名和 GlobalVars 数据块的结构体定义。各模块的详细接口文档见 §6 接口文档索引。

## 4. 功能块接口

### 4.1 FB_1002_SingleLayerConveyor（单层输送机编排器）

| 方向 | 参数数 | 说明 |
|------|--------|------|
| VAR_INPUT | 22 | 自动/手动控制+7组传感器(ARRAY[1..4])+6组手动操作(ARRAY[1..4])+取料确认 |
| VAR_OUTPUT | 11 | 5组执行器(ARRAY[1..4])+HMI状态(ARRAY[1..4])+汇总(Running/Fault/Alarm) |

**关键接口**：
- `i_bAutoMode`, `i_bManualMode`, `i_bStart`, `i_bStop` - 模式控制
- `i_aPreSeparateSensor[1..4]` - 分料前接近开关
- `q_aBlockSolenoid[1..4]` - 阻挡电磁阀
- `q_aSeparateSolenoid[1..4]` - 分料电磁阀
- `q_bRunning`, `q_bFault`, `q_iAlarmCode` - 汇总输出

详见：`conveyor/PRD/接口文档_IFC-FB1002-SingleLayerConveyor.md`

### 4.2 FB_1003_PickPlace（取放料机构）

| 方向 | 参数数 | 说明 |
|------|--------|------|
| VAR_INPUT | 42 | 系统/手动/工艺参数+上游信号+传感器(夹爪/升降/边框检测) |
| VAR_OUTPUT | 14 | 夹爪电磁阀+升降+状态+报警+运行 |
| VAR_IN_OUT | 2 | io_stZAxis, io_stX1Axis (ST_ServoAxis 直连) |

**关键接口**：
- `i_iPickLayer_Input` - 外部指定取料层号(1~4, V7.1.1新增)
- `io_stZAxis` / `io_stX1Axis` - 伺服轴直控(VAR_IN_OUT, PLCopen MC Part 1)
- `o_PlaceComplete_ToFeeder` - 放料完成通知送料机构

详见：`pickplace/PRD/接口文档_IFC-FB1003-PickPlace.md`

### 4.3 FB_1004_GlueMachineFeeder（打胶机送料）

| 方向 | 参数数 | 说明 |
|------|--------|------|
| VAR_INPUT | 14 | 系统/手动/伺服信号+打胶机交互(X76/X102)+取放料完成 |
| VAR_OUTPUT | 9 | 执行器+打胶机信号(Y44/Y47)+状态+报警 |

**关键接口**：
- `i_bGlueMachineAllowFeed` (X76) - 打胶机允许送料
- `i_bGlueMachinePickComplete` (X102) - 打胶机取料完成
- `q_bAllowCatch` (Y44) - 允许打胶机抓料
- `q_bSafeArea` (Y47) - 安全区信号

详见：`feeder/PRD/接口文档_IFC-FB1004-GlueMachineFeeder.md`

### 4.4 FB_2001_CommonAlarm（公共报警管理）

| 方向 | 参数数 | 说明 |
|------|--------|------|
| VAR_INPUT | 3 | 三站报警码(INT): 输送机/取放料/送料 |
| VAR_OUTPUT | 10 | 全局报警字+当前报警码+MES计数+指示灯(绿/红/黄/蜂鸣器/复位)+运行 |

详见：`common/PRD/接口文档_IFC-FB2001-CommonAlarm.md`

### 4.5 FB_ExternalDeviceInteraction（外部设备交互）

| 方向 | 参数数 | 说明 |
|------|--------|------|
| VAR_INPUT | 27 | 急停+8安全门+HMI停止+总线健康+组框机+打胶机+机器人 |
| VAR_OUTPUT | 20 | 安全输出+组框机+打胶机+机器人+指示 |

详见：`external/PRD/接口文档_IFC-FB3001-ExternalDeviceInteraction.md`

## 5. 结构体定义

### 5.1 GlobalVars 数据块结构

```
DATA_BLOCK GlobalVars
├── stExternal  : STRUCT          ← FB_ExternalDeviceInteraction
├── stConveyor  : STRUCT          ← 4×FB_1002 (展开调用)
├── stPickPlace : STRUCT          ← FB_1003_PickPlace
├── stFeeder    : STRUCT          ← FB_1004_GlueMachineFeeder
├── stGlobal    : STRUCT          ← FB_2001_CommonAlarm
└── astServoAxis: ARRAY[1..3] OF ST_ServoAxis  ← FB_1003 VAR_IN_OUT
```

### 5.2 ST_ServoAxis（伺服轴结构体, V3.0, PLCopen MC Part 1）

| 子结构体 | 字段数 | 说明 |
|----------|--------|------|
| stPower | ~5 | 使能控制(Execute/Status/Error) |
| stHome | ~5 | 回原点(Execute/Done/Busy/Error) |
| stStop | ~3 | 急停(Execute/Done) |
| stAbs | ~6 | 绝对定位(Execute/Position/Velocity/Done/Busy/Error) |
| stJog | ~4 | 点动(Forward/Reverse/Velocity) |
| stSensor | ~8 | 限位+报警(HomePos/FwdLimit/RevLimit/ServoFault) |
| **合计** | ~74 | 每轴74字段 × 3轴 = 222字段 |

### 5.3 各 STRUCT 变量统计

| 结构体 | 变量数 | 关键字段示例 |
|--------|--------|-------------|
| stExternal | ~22 | i_bEStop, i_aSafetyDoor[8], i_bHmiStop, i_bBusHealthy |
| stConveyor | ~33 | i_bAutoMode, i_aPreSeparateSensor[4], q_aBlockSolenoid[4] |
| stPickPlace | ~53 | i_bAutoMode, i_iPickLayer_Input, io_stZAxis, io_stX1Axis |
| stFeeder | ~14 | i_bAutoMode, i_bGlueMachineAllowFeed, q_bAllowCatch |
| stGlobal | ~10 | i_iConveyorAlarm, i_iPickPlaceAlarm, q_wGlobalAlarmWord |

详见：`DB1/PRD/接口文档_IFC-GlobalVars.md`

## 6. 接口文档索引

| 模块 | 文档路径 |
|------|----------|
| GlobalVars | `DB1/PRD/接口文档_IFC-GlobalVars.md` |
| OB1 | `OB1/PRD/接口文档_IFC-OB1.md` |
| FB_1002 | `conveyor/PRD/接口文档_IFC-FB1002-SingleLayerConveyor.md` |
| FB_1003 | `pickplace/PRD/接口文档_IFC-FB1003-PickPlace.md` |
| FB_1004 | `feeder/PRD/接口文档_IFC-FB1004-GlueMachineFeeder.md` |
| FB_2001 | `common/PRD/接口文档_IFC-FB2001-CommonAlarm.md` |
| FB_External | `external/PRD/接口文档_IFC-FB3001-ExternalDeviceInteraction.md` |
