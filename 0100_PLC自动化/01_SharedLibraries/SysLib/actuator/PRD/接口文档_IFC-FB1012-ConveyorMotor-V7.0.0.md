# 接口文档 FB_1012_ConveyorMotor

## 0. 文档基础信息

| 属性 | 值 |
|------|-----|
| **文档标题** | FB_1012 输送电机控制接口定义 |
| **文档版本** | V7.0.0 |
| **关联源码** | conveyor/FB_1012_ConveyorMotor.scl |
| **编制日期** | 2026-05-18 |
| **编制人** | Trae |
| **审核人** | 人工 |
| **遵循规范** | 801_PLC变量命名与功能块命名规范_DEV-V1.0.5, 810_PLC编程规范_DEV-V1.0.2 |
| **重构背景** | 从 FB_1002 中拆出电机控制逻辑，消除与气缸/传感器/状态机的耦合 |

## 1. 功能概述

**输送电机控制块**，封装方向命令 → 安全互锁 → 方向互斥 → VFD故障检测 → 实际输出 的完整链路。

适用于通过变频器驱动的输送带电机，支持正转、反转、慢速三种运行模式。

### 1.1 职责边界

| 做什么 | 不做什么 |
|--------|----------|
| 方向命令冲突解决 (Fwd优先) | 不决定何时启动/停止（编排器决定） |
| 安全门状态封锁输出 | 不读取安全门物理地址（由OB1传入） |
| VFD故障检测与报警 | 不处理VFD复位（编排器决定） |
| 速度参考值透传 | 不执行PID或速度闭环 |

## 2. 接口定义

### 2.1 VAR_INPUT

| 名称 | 类型 | 默认值 | 有效值域 | 说明 | 来源 |
|------|------|--------|----------|------|------|
| i_bFwd | BOOL | FALSE | TRUE/FALSE | 正转命令 | 编排器 FB_1002 |
| i_bRev | BOOL | FALSE | TRUE/FALSE | 反转命令 | 编排器 FB_1002 |
| i_bSlow | BOOL | FALSE | TRUE/FALSE | 慢速命令 | 编排器 FB_1002 |
| i_bSafetyDoorOk | BOOL | TRUE | TRUE/FALSE | 安全门状态 (TRUE=关闭OK) | OB1→External FB |
| i_bVfdFault | BOOL | FALSE | TRUE/FALSE | 变频器故障信号 | OB1→IO 映射 |
| i_rSpeed | REAL | 100.0 | 0.0~300.0 | 速度设定值 (mm/s) | OB1→HMI (D100) |

> **命令优先级**: `i_bFwd` > `i_bRev` > `i_bSlow`。即正转和反转同时为 TRUE 时，正转优先；慢速仅在无正转/反转命令时生效。

### 2.2 VAR_OUTPUT

| 名称 | 类型 | 默认值 | 有效值域 | 说明 | 去向 |
|------|------|--------|----------|------|------|
| q_bFwd | BOOL | FALSE | TRUE/FALSE | 正转实际输出 (经互锁后) | OB1→IO (Y10~Y23) |
| q_bRev | BOOL | FALSE | TRUE/FALSE | 反转实际输出 (经互锁后) | OB1→IO (Y10~Y23) |
| q_bSlow | BOOL | FALSE | TRUE/FALSE | 慢速实际输出 (经互锁后) | OB1→IO (Y10~Y23) |
| q_bRunning | BOOL | FALSE | TRUE/FALSE | 任一方向正在运行 | 编排器→HMI |
| q_bVfdAlarm | BOOL | FALSE | TRUE/FALSE | VFD故障报警 | 编排器→FB_2001 |

## 3. 行为逻辑

### 3.1 正常运转

```
i_bFwd=TRUE:
  → 安全门检查: IF i_bSafetyDoorOk THEN q_bFwd := TRUE
  → q_bRev := FALSE; q_bSlow := FALSE
  → q_bRunning := TRUE

i_bRev=TRUE:
  → 安全门检查: IF i_bSafetyDoorOk THEN q_bRev := TRUE
  → q_bFwd := FALSE; q_bSlow := FALSE
  → q_bRunning := TRUE

i_bSlow=TRUE (且 Fwd+Rev 都为 FALSE):
  → 安全门检查: IF i_bSafetyDoorOk THEN q_bSlow := TRUE
  → q_bFwd := FALSE; q_bRev := FALSE
  → q_bRunning := TRUE

所有命令=FALSE:
  → q_bFwd := FALSE; q_bRev := FALSE; q_bSlow := FALSE
  → q_bRunning := FALSE
```

### 3.2 安全门互锁

```
IF NOT i_bSafetyDoorOk THEN
  q_bFwd := FALSE;
  q_bRev := FALSE;
  q_bSlow := FALSE;
  (* 安全门打开时，所有运动输出强制清零 *)
  (* 命令信号保持，安全门恢复后立即响应 *)
END_IF;
```

### 3.3 VFD 故障检测

```
IF i_bVfdFault THEN
  q_bVfdAlarm := TRUE;
  q_bFwd := FALSE;
  q_bRev := FALSE;
  q_bSlow := FALSE;
  (* VFD故障时立即停止所有输出，无论安全门状态 *)
ELSE
  q_bVfdAlarm := FALSE;
END_IF;
```

> **优先级**: VFD故障 > 安全门互锁 > 方向命令。故障时优先切断输出。

## 4. 接口交互协议

```
编排器(FB_1002)                   FB_1012_ConveyorMotor
     │                                      │
     │── i_bFwd := TRUE ────────────────────→│
     │                                      │ 检查 i_bSafetyDoorOk
     │                                      │ 检查 i_bVfdFault
     │←── q_bFwd := TRUE ──────────────────│
     │←── q_bRunning := TRUE ──────────────│
     │                                      │
     │── i_bFwd := FALSE ───────────────────→│  (停止)
     │←── q_bFwd := FALSE ─────────────────│
     │←── q_bRunning := FALSE ─────────────│
```

## 5. 报警码

本 FB 不直接输出报警码。VFD 故障通过 `q_bVfdAlarm` 输出给编排器 FB_1002，由编排器编码为带层号的报警码：

| 信号 | 层L1 | 层L2 | 层L3 | 层L4 |
|------|:----:|:----:|:----:|:----:|
| VFD故障 | 105 | 106 | 107 | 108 |

> 注：VFD 故障也触发 `i_bVfdFault` 的互锁停止，但在报警汇总时体现为独立的 VFD 报警码。

## 6. 关联文档

| 文档 | 路径 |
|------|------|
| DSN | 详细设计说明书_DSN-FB1012-ConveyorMotor-V7.0.0.md |
| 气缸控制 IFC | 接口文档_IFC-FB1011-CylinderControl-V7.0.0.md |
| 编排器 IFC | ../../../../DJ-2026-005/02_PLC程序/通用ST程序及变量表/conveyor/PRD/接口文档_IFC-FB1002-SingleLayerConveyor-V7.0.0.md |
| 子系统架构 | ../../../../DJ-2026-005/02_PLC程序/通用ST程序及变量表/conveyor/PRD/Conveyor子系统架构总览_ARC-Conveyor-V7.0.0.md |
