# 接口文档 FB_1011_CylinderControl

## 0. 文档基础信息

| 属性 | 值 |
|------|-----|
| **文档标题** | FB_1011 气缸控制接口定义 |
| **文档版本** | V7.0.0 |
| **关联源码** | conveyor/FB_1011_CylinderControl.scl |
| **编制日期** | 2026-05-18 |
| **编制人** | Trae |
| **审核人** | 人工 |
| **遵循规范** | 801_PLC变量命名与功能块命名规范_DEV-V1.0.5, 810_PLC编程规范_DEV-V1.0.2 |
| **重构背景** | 从 FB_1002 中拆出气缸控制逻辑，提高内聚性，降低接口数量 |

## 1. 功能概述

**单一气缸执行控制块**，封装推力/拉力命令 → 电磁阀输出 → 到位检测 → 超时保护 → 传感器冗余一致性检查 的完整闭环。

适用于输送机系统中任何需要伸出/收回动作的气动执行器（阻挡气缸、分料气缸等）。

### 1.1 职责边界

| 做什么 | 不做什么 |
|--------|----------|
| 接收伸出/收回命令 | 不关心什么时候该伸出（由编排器决定） |
| 输出电磁阀信号 | 不直接操作物理IO（由OB1映射） |
| 检测上下位传感器 | 不关心传感器的物理地址 |
| 上下位同时ON冲突诊断 | 不参与其他气缸的逻辑 |
| 动作超时计时与报警 | 不处理非本气缸的报警 |

### 1.2 实例化场景

| 场景 | 实例名 | 说明 |
|------|--------|------|
| 阻挡气缸 | fbBlock : FB_1011 | i_bExtend=阻挡下降, i_bRetract=阻挡上升 |
| 分料气缸 | fbSeparate : FB_1011 | i_bExtend=分料推出, i_bRetract=分料复位 |

## 2. 接口定义

### 2.1 VAR_INPUT

| 名称 | 类型 | 默认值 | 有效值域 | 说明 | 来源 |
|------|------|--------|----------|------|------|
| i_bExtend | BOOL | FALSE | TRUE/FALSE | 伸出命令 (TRUE=推/降) | 编排器 FB_1002 |
| i_bRetract | BOOL | FALSE | TRUE/FALSE | 收回命令 (TRUE=拉/升) | 编排器 FB_1002 |
| i_bUpSensor | BOOL | FALSE | TRUE/FALSE | 收回位传感器 (上位/升位) | OB1→IO 映射 |
| i_bDownSensor | BOOL | FALSE | TRUE/FALSE | 伸出位传感器 (下位/降位) | OB1→IO 映射 |
| i_iTimeoutMs | INT | 5000 | 0~60000 | 动作超时时间(ms)，0=关闭超时检测 | 编排器 FB_1002 |

> **命令优先级**: 当 `i_bExtend` 和 `i_bRetract` 同时为 TRUE 时，`i_bExtend`（伸出）优先。

### 2.2 VAR_OUTPUT

| 名称 | 类型 | 默认值 | 有效值域 | 说明 | 去向 |
|------|------|--------|----------|------|------|
| q_bSolenoid | BOOL | FALSE | TRUE/FALSE | 电磁阀输出 (TRUE=伸出, FALSE=收回) | OB1→IO 映射 |
| q_bIsExtended | BOOL | FALSE | TRUE/FALSE | 已伸出到位 (下位传感器=TRUE) | 编排器 FB_1002 |
| q_bIsRetracted | BOOL | FALSE | TRUE/FALSE | 已收回到位 (上位传感器=TRUE) | 编排器 FB_1002 |
| q_bTimeout | BOOL | FALSE | TRUE/FALSE | 动作超时 (伸出或收回未在时间内到位) | 编排器→FB_2001 |
| q_bSensorFault | BOOL | FALSE | TRUE/FALSE | 传感器冗余故障 (上下位同时ON) | 编排器→FB_2001 |

### 2.3 VAR (内部变量)

| 名称 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| tTimeout | FB_TONR | — | 超时定时器 |
| bMoving | BOOL | FALSE | 正在执行动作中 |

## 3. 行为逻辑

### 3.1 正常运行

```
伸出流程:  i_bExtend=TRUE
  → q_bSolenoid := TRUE          (开始伸出)
  → tTimeout.IN := TRUE           (启动超时计时)
  → 等待 i_bDownSensor=TRUE
  → q_bIsExtended := TRUE         (到位)
  → tTimeout.IN := FALSE          (取消计时)

收回流程:  i_bRetract=TRUE
  → q_bSolenoid := FALSE          (开始收回)
  → tTimeout.IN := TRUE           (启动超时计时)
  → 等待 i_bUpSensor=TRUE
  → q_bIsRetracted := TRUE        (到位)
  → tTimeout.IN := FALSE          (取消计时)
```

### 3.2 超时处理

```
如果 tTimeout.Q=TRUE (超时到达) 且尚未到位:
  → q_bTimeout := TRUE         (锁存,直到下次命令变化时清除)
  → q_bSolenoid 保持当前输出   (不强制改变,由编排器决策)
```

### 3.3 传感器冗余一致性检查（持续运行）

```
IF i_bUpSensor AND i_bDownSensor THEN
  q_bSensorFault := TRUE;     (* 上下位同时ON,物理上不可能 *)
ELSE
  q_bSensorFault := FALSE;
END_IF;
```

> **说明**: 实际冗余双通道一致性比对（如两个上位传感器是否一致）由 DB1 在信号接入前完成，此处仅做上下位冲突判断。

### 3.4 安全回零

```
当 i_bExtend=FALSE AND i_bRetract=FALSE 时 (空闲):
  → q_bSolenoid 保持上次状态不变
  → tTimeout.IN := FALSE; tTimeout.R := TRUE
  → 超时故障自动清除 (q_bTimeout := FALSE)
```

## 4. 接口交互协议

```
编排器(FB_1002)                     FB_1011_CylinderControl
     │                                      │
     │── i_bExtend := TRUE ─────────────────→│  (命令: 伸出)
     │                                      │  q_bSolenoid := TRUE
     │                                      │  启动超时计时...
     │                                      │  i_bDownSensor=TRUE
     │←── q_bIsExtended := TRUE ──────────│  (反馈: 已伸出)
     │                                      │
     │── i_bExtend := FALSE ────────────────→│  (撤销命令)
     │                                      │  保持原位 (无动作)
```

## 5. 报警码

本 FB 不直接输出报警码。报警信号通过 `q_bTimeout` 和 `q_bSensorFault` 两个 BOOL 输出给编排器 FB_1002，由编排器根据本层编号 (1~4) 编码为带层号的完整报警码：

| 信号 | 层号编码规则 | 层L1 | 层L2 | 层L3 | 层L4 |
|------|:-----------:|:----:|:----:|:----:|:----:|
| 阻挡 q_bTimeout | 1x0 | 110 | 120 | 130 | 140 |
| 阻挡 q_bSensorFault | 1x2 | 112 | 122 | 132 | 142 |
| 分料 q_bTimeout | 1x1 | 111 | 121 | 131 | 141 |
| 分料 q_bSensorFault | 1x3 | 113 | 123 | 133 | 143 |

## 6. 关联文档

| 文档 | 路径 |
|------|------|
| DSN | 详细设计说明书_DSN-FB1011-CylinderControl-V7.0.0.md |
| 子系统架构 | ../../../../DJ-2026-005/02_PLC程序/通用ST程序及变量表/conveyor/PRD/Conveyor子系统架构总览_ARC-Conveyor-V7.0.0.md |
| 编排器 IFC | ../../../../DJ-2026-005/02_PLC程序/通用ST程序及变量表/conveyor/PRD/接口文档_IFC-FB1002-SingleLayerConveyor-V7.0.0.md |
| 规范 | ../../../../../01_需求与设计/10_编程及变量规范/801_PLC变量命名与功能块命名规范_DEV-V1.0.5.md |
