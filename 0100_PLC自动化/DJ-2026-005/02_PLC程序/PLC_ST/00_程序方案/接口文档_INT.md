---
spec_id: INT-DJ-2026-005-PLC_ST
title: "DJ-2026-005 边框缓存机 PLC 程序接口文档"
version: "V9.0.0"
domain: plc
lifecycle: active
tags: ["接口文档", "PLC程序"]
---

# 接口文档 DJ-2026-005 边框缓存机 PLC 程序

## 1. 文档基础信息

**文档标题**：DJ-2026-005 边框缓存机 PLC 程序接口文档
**文档版本**：V9.0.0
**编制日期**：2026-07-26
**编制人**：Trae
**审核人**：[待审核]
**遵循规范**：INT-815, LSP-905

## 2. 版本变更记录

| 版本号 | 变更内容 | 变更人 | 变更日期 |
|--------|----------|--------|----------|
| V9.0.0 | 全工站 5 大 FB 升级结构体整块传递模式 (VAR_IN_OUT)，OB1 瘦身至 5 行顶级调度器 | Trae | 2026-07-26 |
| V7.1.1 | 填写实际内容 | Trae | 2026-06-23 |
| V1.0.0 | 初始创建 | auto-pm | 2026-06-19 |

## 3. 接口概述

本文档为 PLC 程序级接口总览，汇总各功能块的接口签名和 GlobalVars 数据块的结构体定义。各模块的详细接口文档见 §6 接口文档索引。

## 4. 功能块接口

### 4.1 FB_1002_SingleLayerConveyor（单层输送机编排器）

| 方向 | 参数数 | 说明 |
|------|--------|------|
| VAR_IN_OUT | 1 | io_stLayer : ST_SingleLayerConveyor (结构体整块传递) |

### 4.2 FB_1003_PickPlace（取放料机构）

| 方向 | 参数数 | 说明 |
|------|--------|------|
| VAR_IN_OUT | 3 | io_stPickPlace: ST_PickPlace, io_stZAxis/io_stX1Axis: ST_ServoAxis |

### 4.3 FB_1004_GlueMachineFeeder（打胶机送料）

| 方向 | 参数数 | 说明 |
|------|--------|------|
| VAR_IN_OUT | 2 | io_stFeeder: ST_GlueFeeder, io_stX2Axis: ST_ServoAxis |

### 4.4 FB_2001_CommonAlarm（公共报警管理）

| 方向 | 参数数 | 说明 |
|------|--------|------|
| VAR_IN_OUT | 1 | io_stGlobal: ST_CommonAlarm |

### 4.5 FB_ExternalDeviceInteraction（外部设备交互）

| 方向 | 参数数 | 说明 |
|------|--------|------|
| VAR_IN_OUT | 1 | io_stExternal: ST_ExternalDevice |

## 5. 结构体定义

### 5.1 GlobalVars 数据块结构

```
DATA_BLOCK GlobalVars
├── stExternal  : ST_ExternalDevice         ← FB_ExternalDeviceInteraction
├── stConveyor  : ST_SingleLayerConveyor    ← 4×FB_1002 (展开调用)
├── stPickPlace : ST_PickPlace              ← FB_1003_PickPlace
├── stFeeder    : ST_GlueFeeder             ← FB_1004_GlueMachineFeeder
├── stGlobal    : ST_CommonAlarm            ← FB_2001_CommonAlarm
└── astServoAxis: ARRAY[1..3] OF ST_ServoAxis
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
