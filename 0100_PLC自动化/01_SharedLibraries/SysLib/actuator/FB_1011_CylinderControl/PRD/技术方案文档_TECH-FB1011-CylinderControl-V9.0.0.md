---
spec_id: TECH-FB1011
title: "FB_1011_CylinderControl技术方案文档"
version: "V9.0.0"
domain: plc
lifecycle: stable
canonical_path: "0100_PLC自动化/01_SharedLibraries/SysLib/actuator/FB_1011_CylinderControl/PRD/技术方案文档_TECH-FB1011-CylinderControl-V9.0.0.md"
tags: ["气缸控制", "执行器", "PLC功能块", "技术方案", "电磁阀"]
---

# 技术方案文档 FB_1011_CylinderControl

## 1. 文档基础信息

**文档标题**：FB_1011_CylinderControl技术方案文档
**文档版本**：V9.0.0
**编制日期**：2026-05-30
**编制人**：Trae
**审核人**：人工
**遵循规范**：TECH-014, LSP-905-V1.0.2, LSP-904-V1.1.0, LSP-903-V2.1.0

## 2. 版本变更记录

| 版本号 | 变更内容 | 变更人 | 变更日期 | 详细说明 |
|--------|----------|--------|----------|----------|
| V9.0.0 | 移除VAR_IN_OUT ST_Cylinder，回归扁平接口；新增传感器TON消抖；完善极性取反映射层；变量命名对齐LSP-905 | Trae | 2026-05-30 | 移除ST_Cylinder结构体依赖，采用i_/q_/s_/fb_前缀命名，新增消抖和极性映射流水线 |
| V8.1.0 | 明确电磁阀类型定义，增加通用性设计 | Trae | 2026-05-30 | 新增SolenoidType和ExtendPolarity参数说明，明确当前为单线圈两位阀，预留双线圈/3位阀扩展 |
| V8.0.0 | 重构为VAR_IN_OUT ST_Cylinder结构，对齐SysLib规范 | Trae | 2026-05-30 | 参考FB_1003 VAR_IN_OUT io_stZAxis模式 |
| V7.0.0 | 从FB_1002中独立拆分，接口扁平化设计 | Trae | 2026-05-18 | 提高内聚性，降低耦合度 |

## 3. 概述

### 3.1 背景

输送机系统中多个执行器（阻挡气缸、分料气缸等）需要标准化的气缸控制功能。原有逻辑耦合在FB_1002中，可复用性差，接口数量多，维护困难。

### 3.2 目标

- **业务目标**：提供通用、高内聚、低耦合的气缸控制功能块
- **技术目标**：采用扁平VAR_INPUT/VAR_OUTPUT接口，变量命名对齐LSP-905规范，支持传感器消抖和极性取反
- **性能目标**：响应时间≤1个PLC扫描周期

### 3.3 V9.0.0重构动机

V8.x采用VAR_IN_OUT ST_Cylinder结构体封装接口，但对于简单执行机构而言：
- **结构体封装增加不必要的间接层**，调试时需展开结构体才能观察变量
- **扁平接口更直观**，在线监控时所有变量一目了然
- **减少依赖**，无需维护ST_Cylinder类型定义文件
- **对齐LSP-905命名规范**，i_/q_/s_/fb_前缀使变量角色一目了然

### 3.4 范围

**包含范围**：
- 单气缸伸出/收回控制
- 上下位传感器检测
- 传感器TON消抖
- 传感器冗余一致性检查
- 动作超时计时与报警
- 命令优先级处理
- 电磁阀类型参数化配置
- 线圈极性取反支持（含传感器互换）

**不包含范围**：
- 气缸动作时机编排
- 物理IO地址映射
- 报警码编码
- 多气缸协同逻辑

## 4. 电磁阀类型技术说明

### 4.1 电磁阀类型对照表（SolenoidType）

| SolenoidType值 | 电磁阀类型 | 线圈数量 | 阀位数 | 输出信号 | 默认行为（无命令时） | 当前V9.0.0支持 |
|-----------|---------|---------|-------|---------|------------------|---------------|
| **0** | **单线圈两位阀** | 1个 | 2位 | 1个BOOL | 弹簧复位（收回） | ✅ **支持（默认）** |
| 1 | 双线圈两位阀 | 2个 | 2位 | 2个BOOL | 保持最后位置 | ⚠️ 预留扩展 |
| 2 | 3位4通中封阀 | 2个 | 3位 | 2个BOOL | 保持位置（中封） | ⚠️ 预留扩展 |
| 3 | 3位4通中泄阀 | 2个 | 3位 | 2个BOOL | 泄压回油（中泄） | ⚠️ 预留扩展 |

### 4.2 当前V9.0.0的默认配置（单线圈两位阀）

**FB_1011 V9.0.0 默认：单线圈两位阀**
- 线圈：1个
- 输出：q_bSolenoid (BOOL)
- TRUE = 得电伸出（可通过i_bExtendPolarity取反）
- FALSE = 失电收回（弹簧复位）
- 安全性：失电后气缸自动收回（弹簧复位）

**单线圈两位阀真值表**：

| i_bExtend | i_bRetract | i_bExtendPolarity | q_bSolenoid | 气缸行为 |
|-----------|------------|-------------------|-------------|---------|
| TRUE      | FALSE      | FALSE             | TRUE        | 伸出    |
| FALSE     | TRUE       | FALSE             | FALSE       | 收回    |
| FALSE     | FALSE      | FALSE             | FALSE       | 弹簧复位 |
| TRUE      | FALSE      | TRUE              | FALSE       | 伸出    |
| FALSE     | TRUE       | TRUE              | TRUE        | 收回    |
| FALSE     | FALSE      | TRUE              | TRUE        | 弹簧复位 |

### 4.3 线圈极性取反（ExtendPolarity）

| i_bExtendPolarity值 | 说明 | q_bSolenoid=TRUE | q_bSolenoid=FALSE | 适用场景 |
|---------------------|------|-----------------|-----------------|---------|
| FALSE (默认) | 正常极性 | 伸出 | 收回 | 阻挡/夹紧等气缸 |
| TRUE | 极性取反 | 收回 | 伸出 | 拍正/顶升等弹簧复位气缸 |

## 5. 技术选型

### 5.1 技术栈

| 层次 | 技术/工具 | 版本 | 选型理由 | 替代方案 |
|------|-----------|------|----------|---------|
| 开发语言 | Structured Control Language (SCL) | Siemens TIA Portal | 工业标准，广泛使用 | Ladder Logic (LAD), Function Block Diagram (FBD) |
| 消抖定时器 | FB_TON | Siemens TIA Portal | 接通延时定时器，适用于传感器消抖 | 自定义消抖逻辑 |
| 超时定时器 | FB_TONR | Siemens TIA Portal | 累积定时器，保持Q直到显式复位 | FB_TON |

### 5.2 依赖管理

#### 5.2.1 PLC依赖

| 依赖项 | 类型 | 用途 | 风险评估 |
|--------|------|------|---------|
| FB_TON | 原生功能块 | 传感器消抖 | 低，Siemens标准功能块 |
| FB_TONR | 原生功能块 | 超时计时 | 低，Siemens标准功能块 |
| LSP-905-V1.0.2 | 规范 | 变量命名规范 | 低，稳定规范 |
| LSP-904-V1.1.0 | 规范 | 注释规范 | 低，稳定规范 |
| LSP-903-V1.0.0 | 规范 | 编程规范 | 低，稳定规范 |

**依赖原则**：
- 优先使用PLC原生功能块
- 优先使用标准通信协议
- 避免使用非标或私有协议
- 避免过度复杂的嵌套调用

## 6. 系统架构设计

### 6.1 架构概述

本功能块采用单层架构，所有逻辑在单一FB内实现，不依赖其他自定义FB或自定义数据类型。

```
上级功能块 (FB_1002)
    ↓
FB_1011_CylinderControl
    ↓
OB1 IO映射
    ↓
物理设备 (电磁阀、传感器)
```

### 6.2 架构图（单线圈两位阀）

```
┌──────────────────────────────────────────────────────────────┐
│               FB_1011_CylinderControl                        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  ① 物理传感器输入                                     │   │
│  │  i_bExtendedPos, i_bRetractedPos                     │   │
│  └──────────────────────────────────────────────────────┘   │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  ② TON消抖层 (fb_tDebounceExt, fb_tDebounceRet)     │   │
│  │  i_dDebounceMs > 0 时启用，0 = 直通                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  ③ 传感器故障检测 (组合逻辑)                          │   │
│  │  s_bExtDebounced AND s_bRetDebounced → SensorFault  │   │
│  └──────────────────────────────────────────────────────┘   │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  ④ 极性映射层                                         │   │
│  │  i_bExtendPolarity=TRUE → 物理传感器互换             │   │
│  │  s_bLogicExtPos, s_bLogicRetPos                      │   │
│  └──────────────────────────────────────────────────────┘   │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  ⑤ 命令处理状态机                                     │   │
│  │  i_bExtend > i_bRetract → 电磁阀控制                 │   │
│  │  到位检测 → 状态更新 → 定时器控制                     │   │
│  │  i_iSolenoidType + i_bExtendPolarity → 输出逻辑      │   │
│  └──────────────────────────────────────────────────────┘   │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  ⑥ 超时定时器 (fb_tTimeout, FB_TONR)                │   │
│  │  IN/PT/Q/ET → q_bTimeout                             │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
         ↑                                  ↓
  VAR_INPUT (8个)                    VAR_OUTPUT (5个)
```

### 6.3 信号处理流水线

V9.0.0采用明确的5级信号处理流水线，每级职责单一：

```
物理传感器 → TON消抖 → 传感器故障检测 → 极性映射 → 命令处理
```

| 流水线阶段 | 输入 | 输出 | 实现方式 |
|-----------|------|------|---------|
| ① 物理传感器 | i_bExtendedPos, i_bRetractedPos | 原始信号 | 直接读取 |
| ② TON消抖 | 原始信号, i_dDebounceMs | s_bExtDebounced, s_bRetDebounced | FB_TON × 2 |
| ③ 传感器故障检测 | s_bExtDebounced, s_bRetDebounced | q_bSensorFault | 组合逻辑 |
| ④ 极性映射 | s_bExtDebounced, s_bRetDebounced, i_bExtendPolarity | s_bLogicExtPos, s_bLogicRetPos | 条件互换 |
| ⑤ 命令处理 | i_bExtend, i_bRetract, s_bLogicExtPos, s_bLogicRetPos | q_bSolenoid, q_bIsExtended, q_bIsRetracted, q_bTimeout | 状态机 |

### 6.4 模块划分

| 模块名称 | 功能描述 | 技术实现 | 负责人 | 优先级 |
|---------|---------|----------|--------|--------|
| TON消抖 | 传感器信号消抖，滤除短暂抖动 | FB_TON × 2 | Trae | P0 |
| 传感器故障检测 | 上下位同时ON检测 | 纯组合逻辑 | Trae | P0 |
| 极性映射 | 极性取反时互换传感器逻辑含义 | 条件赋值 | Trae | P0 |
| 命令处理 | 伸出/收回控制，命令优先级 | 状态机逻辑 | Trae | P0 |
| 电磁阀输出逻辑 | 根据i_iSolenoidType+i_bExtendPolarity输出 | 条件分支 | Trae | P0 |
| 超时计时 | 动作超时检测 | FB_TONR | Trae | P1 |
| 状态更新 | 到位状态、超时状态更新 | 逻辑赋值 | Trae | P1 |

### 6.5 数据流设计（单线圈两位阀）

```
┌──────────────────────────────────────────────────────────────┐
│  VAR_INPUT (8个)                                             │
├──────────────────────────────────────────────────────────────┤
│  i_bExtend (BOOL)       ────┐                                │
│  i_bRetract (BOOL)      ────┼─→ 命令处理模块                 │
│  i_bExtendedPos (BOOL)  ────┤                                │
│  i_bRetractedPos (BOOL) ────┼─→ TON消抖 → 故障检测 → 极性映射│
│  i_dTimeoutMs (DINT)     ────┼─→ 超时定时器                   │
│  i_dDebounceMs (DINT)    ────┼─→ 消抖定时器PT                 │
│  i_iSolenoidType (INT)  ────┼─→ 电磁阀输出逻辑               │
│  i_bExtendPolarity (BOOL)───┘─→ 极性映射 + 电磁阀输出逻辑    │
└──────────────────────────────────────────────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────────────┐
│  VAR_OUTPUT (5个)                                            │
├──────────────────────────────────────────────────────────────┤
│  q_bSolenoid (BOOL)     ←─── 电磁阀输出逻辑                  │
│  q_bIsExtended (BOOL)   ←─── 状态更新模块                    │
│  q_bIsRetracted (BOOL)  ←─── 状态更新模块                    │
│  q_bTimeout (BOOL)      ←─── 超时定时器                      │
│  q_bSensorFault (BOOL)  ←─── 传感器故障检测模块              │
└──────────────────────────────────────────────────────────────┘
```

## 7. 程序框架设计

### 7.1 PLC程序框架

#### 7.1.1 程序结构

```
SysLib/
├── actuator/
│   ├── FB_1011_CylinderControl/
│   │   ├── FB_1011_CylinderControl.scl
│   │   └── PRD/
│   │       ├── 需求分析文档_REQ-FB1011-CylinderControl-V9.0.0.md
│   │       ├── 技术方案文档_TECH-FB1011-CylinderControl-V9.0.0.md
│   │       ├── 接口文档_IFC-FB1011-CylinderControl-V9.0.0.md
│   │       └── 详细设计说明书_DSN-FB1011-CylinderControl-V9.0.0.md
│   ├── FB_1012_ConveyorMotor/
│   ├── FB_1013_NinetyDegreeTransfer/
│   └── FB_1014_StationConveyor/
```

#### 7.1.2 功能块设计

| 功能块名称 | 功能描述 | 输入参数 | 输出参数 | 调用关系 |
|---------|---------|---------|---------|---------|
| FB_1011_CylinderControl | 气缸控制 | 8个VAR_INPUT | 5个VAR_OUTPUT | 被上级FB调用 |

### 7.2 核心代码结构（单线圈两位阀）

#### 7.2.1 FB声明

```scl
FUNCTION_BLOCK FB_1011_CylinderControl

VAR_INPUT
    i_bExtend         : BOOL := FALSE;   // 伸出命令 (推/降/夹紧)
    i_bRetract        : BOOL := FALSE;   // 收回命令 (拉/升/松开)
    i_bExtendedPos    : BOOL := FALSE;   // 伸出位传感器 (物理)
    i_bRetractedPos   : BOOL := FALSE;   // 收回位传感器 (物理)
    i_dTimeoutMs      : DINT := 5000;    // 动作超时时间 (ms), 0=关闭
    i_dDebounceMs     : DINT := 0;       // 传感器消抖时间 (ms), 0=关闭消抖
    i_iSolenoidType   : INT  := 0;       // 电磁阀类型: 0=单线圈两位阀(默认)
    i_bExtendPolarity : BOOL := FALSE;   // 线圈极性取反: FALSE=正常, TRUE=取反
END_VAR

VAR_OUTPUT
    q_bSolenoid    : BOOL := FALSE;  // 电磁阀输出 TRUE=得电(可通过i_bExtendPolarity取反)
    q_bIsExtended  : BOOL := FALSE;  // 已伸出到位
    q_bIsRetracted : BOOL := FALSE;  // 已收回到位
    q_bTimeout     : BOOL := FALSE;  // 动作超时报警
    q_bSensorFault : BOOL := FALSE;  // 传感器冲突 (上下位同时ON)
END_VAR

VAR
    fb_tDebounceExt  : FB_TON;       // 伸出位传感器消抖定时器
    fb_tDebounceRet  : FB_TON;       // 收回位传感器消抖定时器
    fb_tTimeout      : FB_TONR;      // 超时定时器
    s_bExtDebounced  : BOOL := FALSE; // 伸出位消抖后信号
    s_bRetDebounced  : BOOL := FALSE; // 收回位消抖后信号
    s_dExtDebounceEt : DINT := 0;     // 伸出位消抖已延时时间
    s_dRetDebounceEt : DINT := 0;     // 收回位消抖已延时时间
    s_bLogicExtPos   : BOOL := FALSE; // 极性映射后的逻辑伸出位
    s_bLogicRetPos   : BOOL := FALSE; // 极性映射后的逻辑收回位
    s_bMoving        : BOOL := FALSE; // 正在执行动作中
END_VAR
```

#### 7.2.2 传感器TON消抖

```scl
(* ===== 定时器批量调用 (无条件, 每周期执行, LSP-903 V2.1.0 §3.4) ===== *)
fb_tDebounceExt(IN := fb_tDebounceExt.IN, PT := fb_tDebounceExt.PT,
                 Q => fb_tDebounceExt.Q, ET => fb_tDebounceExt.ET);
fb_tDebounceRet(IN := fb_tDebounceRet.IN, PT := fb_tDebounceRet.PT,
                 Q => fb_tDebounceRet.Q, ET => fb_tDebounceRet.ET);
fb_tTimeout(IN := fb_tTimeout.IN, R := fb_tTimeout.R, PT := fb_tTimeout.PT,
             Q => fb_tTimeout.Q, ET => fb_tTimeout.ET);

(* ===== TON消抖 (只设参数, 只读输出) ===== *)
// i_dDebounceMs > 0 时启用消抖，= 0 时信号直通
fb_tDebounceExt.IN := i_bExtendedPos;
fb_tDebounceExt.PT := i_dDebounceMs;
s_bExtDebounced := fb_tDebounceExt.Q;
s_dExtDebounceEt := fb_tDebounceExt.ET;

fb_tDebounceRet.IN := i_bRetractedPos;
fb_tDebounceRet.PT := i_dDebounceMs;
s_bRetDebounced := fb_tDebounceRet.Q;
s_dRetDebounceEt := fb_tDebounceRet.ET;
```

#### 7.2.3 传感器故障检测

```scl
// ==================== 传感器冗余一致性检查 ====================
IF s_bExtDebounced AND s_bRetDebounced THEN
    q_bSensorFault := TRUE;
ELSE
    q_bSensorFault := FALSE;
END_IF;
```

#### 7.2.4 极性映射层

```scl
// ==================== 极性映射 ====================
// i_bExtendPolarity=TRUE 时，物理传感器互换逻辑含义
// 正常极性: 物理伸出位 = 逻辑伸出位
// 取反极性: 物理伸出位 = 逻辑收回位（因为气缸动作方向反转）
IF i_bExtendPolarity THEN
    s_bLogicExtPos := s_bRetDebounced;
    s_bLogicRetPos := s_bExtDebounced;
ELSE
    s_bLogicExtPos := s_bExtDebounced;
    s_bLogicRetPos := s_bRetDebounced;
END_IF;
```

#### 7.2.5 命令处理（单线圈两位阀）

```scl
// ==================== 命令处理与电磁阀输出 ====================
IF i_bExtend THEN
    // Extend优先，根据极性输出
    IF i_bExtendPolarity THEN
        q_bSolenoid := FALSE;  // 取反：FALSE=伸出
    ELSE
        q_bSolenoid := TRUE;   // 正常：TRUE=伸出
    END_IF;

    IF NOT s_bMoving THEN
        s_bMoving := TRUE;
        IF i_dTimeoutMs > 0 THEN
            fb_tTimeout.IN := TRUE;
            fb_tTimeout.R := FALSE;
            fb_tTimeout.PT := i_dTimeoutMs;
        END_IF;
    END_IF;

    IF s_bLogicExtPos THEN
        q_bIsExtended := TRUE;
        q_bIsRetracted := FALSE;
        s_bMoving := FALSE;
        q_bTimeout := FALSE;
        fb_tTimeout.IN := FALSE;
        fb_tTimeout.R := TRUE;
    END_IF;

    IF fb_tTimeout.Q THEN
        q_bTimeout := TRUE;
    END_IF;

ELSIF i_bRetract THEN
    // Retract，根据极性输出
    IF i_bExtendPolarity THEN
        q_bSolenoid := TRUE;   // 取反：TRUE=收回
    ELSE
        q_bSolenoid := FALSE;  // 正常：FALSE=收回
    END_IF;

    IF NOT s_bMoving THEN
        s_bMoving := TRUE;
        IF i_dTimeoutMs > 0 THEN
            fb_tTimeout.IN := TRUE;
            fb_tTimeout.R := FALSE;
            fb_tTimeout.PT := i_dTimeoutMs;
        END_IF;
    END_IF;

    IF s_bLogicRetPos THEN
        q_bIsRetracted := TRUE;
        q_bIsExtended := FALSE;
        s_bMoving := FALSE;
        q_bTimeout := FALSE;
        fb_tTimeout.IN := FALSE;
        fb_tTimeout.R := TRUE;
    END_IF;

    IF fb_tTimeout.Q THEN
        q_bTimeout := TRUE;
    END_IF;

ELSE
    // 无命令，弹簧复位
    IF i_bExtendPolarity THEN
        q_bSolenoid := TRUE;   // 取反：TRUE=弹簧复位（伸出方向）
    ELSE
        q_bSolenoid := FALSE;  // 正常：FALSE=弹簧复位（收回方向）
    END_IF;

    s_bMoving := FALSE;
    q_bTimeout := FALSE;
    fb_tTimeout.IN := FALSE;
    fb_tTimeout.R := TRUE;

    q_bIsExtended := s_bLogicExtPos;
    q_bIsRetracted := s_bLogicRetPos;
END_IF;
```

#### 7.2.6 超时定时器调用

```scl
// ==================== 超时定时器 ====================
fb_tTimeout(IN := fb_tTimeout.IN, R := fb_tTimeout.R, PT := fb_tTimeout.PT,
            Q => fb_tTimeout.Q, ET => fb_tTimeout.ET);
```

## 8. 接口设计

### 8.1 内部接口

| 接口名称 | 调用方 | 被调用方 | 参数 | 返回值 | 说明 |
|---------|--------|---------|------|--------|------|
| FB_1011_CylinderControl | 上级FB | FB_1011 | 8个VAR_INPUT | 5个VAR_OUTPUT | 核心接口 |

### 8.2 外部接口

| 接口名称 | 协议 | 方向 | 数据格式 | 频率 | 说明 |
|---------|------|------|---------|------|------|
| OB1 IO映射 | 硬件IO | 双向 | BOOL | 每扫描周期 | 物理传感器输入，电磁阀输出 |
| 上级编排器 | 内部调用 | 双向 | 扁平变量 | 每扫描周期 | 如FB_1002 |
| 报警管理 | 内部调用 | 输出 | BOOL, BOOL | 每扫描周期 | q_bTimeout和q_bSensorFault信号 |

## 9. 数据结构设计

### 9.1 扁平变量说明

V9.0.0移除ST_Cylinder结构体，采用扁平VAR_INPUT/VAR_OUTPUT接口。变量命名遵循LSP-905规范：

**前缀约定**：

| 前缀 | 含义 | 作用域 |
|------|------|--------|
| i_ | 输入变量 | VAR_INPUT |
| q_ | 输出变量 | VAR_OUTPUT |
| s_ | 内部静态变量 | VAR |
| fb_ | FB实例 | VAR |

**VAR_INPUT（8个）**：

| 变量名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| i_bExtend | BOOL | FALSE | 伸出命令 (推/降/夹紧) |
| i_bRetract | BOOL | FALSE | 收回命令 (拉/升/松开) |
| i_bExtendedPos | BOOL | FALSE | 伸出位传感器 (物理) |
| i_bRetractedPos | BOOL | FALSE | 收回位传感器 (物理) |
| i_dTimeoutMs | DINT | 5000 | 动作超时时间 (ms), 0=关闭 |
| i_dDebounceMs | DINT | 0 | 传感器消抖时间 (ms), 0=关闭消抖 |
| i_iSolenoidType | INT | 0 | 电磁阀类型: 0=单线圈两位阀(默认) |
| i_bExtendPolarity | BOOL | FALSE | 线圈极性取反: FALSE=正常, TRUE=取反 |

**VAR_OUTPUT（5个）**：

| 变量名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| q_bSolenoid | BOOL | FALSE | 电磁阀输出 |
| q_bIsExtended | BOOL | FALSE | 已伸出到位 |
| q_bIsRetracted | BOOL | FALSE | 已收回到位 |
| q_bTimeout | BOOL | FALSE | 动作超时报警 |
| q_bSensorFault | BOOL | FALSE | 传感器冲突 (上下位同时ON) |

**VAR（内部变量，10个）**：

| 变量名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| fb_tDebounceExt | FB_TON | - | 伸出位传感器消抖定时器 |
| fb_tDebounceRet | FB_TON | - | 收回位传感器消抖定时器 |
| fb_tTimeout | FB_TONR | - | 超时定时器 |
| s_bExtDebounced | BOOL | FALSE | 伸出位消抖后信号 |
| s_bRetDebounced | BOOL | FALSE | 收回位消抖后信号 |
| s_dExtDebounceEt | DINT | 0 | 伸出位消抖已延时时间 |
| s_dRetDebounceEt | DINT | 0 | 收回位消抖已延时时间 |
| s_bLogicExtPos | BOOL | FALSE | 极性映射后的逻辑伸出位 |
| s_bLogicRetPos | BOOL | FALSE | 极性映射后的逻辑收回位 |
| s_bMoving | BOOL | FALSE | 正在执行动作中 |

### 9.2 存储策略

- **数据存储**：所有状态在FB实例内部维护
- **备份策略**：不需要备份，状态由输入重新生成
- **清理策略**：不需要清理，FB实例随程序清除

## 10. 安全设计

### 10.1 安全需求

- 超时仅报警不强制复位，保持输出状态
- 传感器故障实时检测
- 命令优先级防止冲突
- 失电自动弹簧复位（单线圈两位阀安全特性）
- 传感器消抖防止误触发

### 10.2 安全措施

| 风险点 | 风险等级 | 应对措施 | 责任人 |
|---------|---------|---------|--------|
| 超时后气缸继续动作 | 中 | 超时仅报警，不强制改变电磁阀，由上级决定策略 | Trae |
| 传感器故障未发现 | 中 | 实时检测上下位同时ON状态，立即报警 | Trae |
| 命令冲突 | 低 | i_bExtend优先于i_bRetract，防止电磁阀频繁切换 | Trae |
| 失电安全 | 高 | 单线圈两位阀，失电自动弹簧复位收回 | Trae |
| 电磁阀选型错误 | 中 | 提供i_iSolenoidType参数，明确文档说明 | Trae |
| 传感器抖动误触发 | 中 | TON消抖层，i_dDebounceMs可配置 | Trae |
| 极性接线错误 | 中 | i_bExtendPolarity极性映射层，传感器同步互换 | Trae |

## 11. 性能设计

### 11.1 性能指标

| 指标项 | 目标值 | 测试方法 | 验收标准 |
|-------|--------|---------|---------|
| 响应时间 | ≤1个PLC扫描周期 | 示波器测量 | 输入变化后，输出在下一扫描周期更新 |
| 扫描周期增量 | ≤1ms | 性能分析 | 相比无FB时，扫描周期增加≤1ms |
| 内存占用 | ≤1KB | 资源分析 | 每个FB实例内存占用≤1KB |
| 消抖响应 | ≤i_dDebounceMs+1周期 | 定时测量 | 消抖时间到达后1周期内输出更新 |

### 11.2 优化策略

- 传感器消抖使用FB_TON，消抖时间=0时信号直通，无额外开销
- 传感器一致性检查使用纯组合逻辑，无延时
- 定时器仅在需要时启动，空闲时复位
- 使用TONR而非多个TON做超时计时，减少资源占用
- 极性映射使用简单条件赋值，不增加额外延时
- 电磁阀输出逻辑条件判断，不增加额外延时

## 12. 风险评估

### 12.1 技术风险

| 风险项 | 可能性 | 影响程度 | 风险等级 | 应对措施 | 责任人 |
|---------|---------|---------|---------|---------|--------|
| 扁平接口参数数量多 | 低 | 低 | 低 | 8个输入在可接受范围内，调试时一目了然 | Trae |
| 超时策略争议 | 中 | 中 | 低 | 保持当前策略，记录设计决策 | Trae |
| 传感器类型差异 | 中 | 低 | 低 | OB1处理传感器类型，本FB仅接收BOOL | Trae |
| 电磁阀选型变更 | 中 | 中 | 中 | 提供参数配置，支持取反和类型选择 | Trae |
| 消抖时间设置不当 | 中 | 中 | 中 | 默认0=关闭，文档明确推荐值范围 | Trae |
| 极性映射逻辑复杂 | 低 | 中 | 低 | 极性映射层独立，可单独测试验证 | Trae |

### 12.2 依赖风险

| 依赖项 | 风险描述 | 应对措施 | 备选方案 |
|--------|---------|---------|---------|
| FB_TON | Siemens标准功能块，风险低 | 无需特殊措施 | 自定义消抖逻辑 |
| FB_TONR | Siemens标准功能块，风险低 | 无需特殊措施 | 使用TON+保持逻辑 |

## 13. 实施计划

### 13.1 里程碑

| 里程碑 | 交付物 | 负责人 | 计划日期 | 状态 |
|--------|--------|--------|---------|------|
| 需求分析 | 需求分析文档 | Trae | 2026-05-30 | 完成 |
| 技术方案 | 技术方案文档 | Trae | 2026-05-30 | 完成 |
| 代码实现 | FB_1011_CylinderControl.scl | Trae | 2026-05-30 | 进行中 |
| 单元测试 | 测试报告 | Trae | 2026-05-30 | 待开始 |
| 文档完善 | 所有文档 | Trae | 2026-05-30 | 进行中 |

### 13.2 资源需求

| 资源类型 | 需求描述 | 数量 | 获取方式 |
|---------|---------|------|---------|
| PLC开发环境 | Siemens TIA Portal | 1套 | 现有 |
| 测试PLC | S7-1200/1500 | 1台 | 现有 |
| 气缸测试台 | 带电磁阀和传感器的气缸 | 1套 | 现有 |
| 不同类型电磁阀样品 | 单线圈、双线圈、3位阀 | 各1个 | 需准备 |

## 14. 验收标准

### 14.1 功能验收

- [x] 伸出控制：i_bExtend=TRUE时，电磁阀=伸出，s_bLogicExtPos=TRUE后q_bIsExtended=TRUE
- [x] 收回控制：i_bRetract=TRUE时，电磁阀=收回，s_bLogicRetPos=TRUE后q_bIsRetracted=TRUE
- [x] 命令优先级：i_bExtend和i_bRetract同时TRUE，电磁阀=伸出
- [x] 传感器一致性检查：两传感器同时ON，q_bSensorFault=TRUE
- [x] 超时保护：i_dTimeoutMs=5000，动作5秒未到位，q_bTimeout=TRUE
- [x] 超时关闭：i_dTimeoutMs=0，不触发超时
- [x] 单线圈两位阀默认配置：i_iSolenoidType=0时，工作正常
- [ ] 线圈极性取反：i_bExtendPolarity=TRUE时，线圈输出取反，传感器逻辑互换
- [ ] 传感器消抖：i_dDebounceMs>0时，传感器信号消抖后输出
- [ ] 消抖关闭：i_dDebounceMs=0时，传感器信号直通

### 14.2 性能验收

- [ ] 响应时间：输入变化后，输出在1个扫描周期内更新
- [ ] 扫描周期增量：相比无FB时，扫描周期增加≤1ms
- [ ] 内存占用：每个FB实例内存占用≤1KB
- [ ] 消抖响应：消抖时间到达后1周期内输出更新

### 14.3 文档验收

- [x] 需求分析文档
- [x] 技术方案文档
- [x] 接口文档
- [x] 详细设计说明书

## 15. 附录

### 15.1 参考资料

| 资料名称 | 版本 | 来源 |
|----------|------|------|
| 需求分析文档_REQ-FB1011-CylinderControl-V9.0.0.md | V9.0.0 | 本目录 |
| 接口文档_IFC-FB1011-CylinderControl-V9.0.0.md | V9.0.0 | 本目录 |
| 详细设计说明书_DSN-FB1011-CylinderControl-V9.0.0.md | V9.0.0 | 本目录 |
| LSP-905_PLC变量命名规范_V1.0.2.md | V1.0.2 | 0100_PLC自动化/00_通用规范/PLC编程/ |
| LSP-904_SCL注释规范_V1.1.0.md | V1.1.0 | 0100_PLC自动化/00_通用规范/PLC编程/ |
| 903_定时器使用规范_LSP-V2.1.0.md | V2.1.0 | 0100_PLC自动化/00_通用规范/PLC编程/ |

### 15.2 术语定义

| 术语 | 定义 |
|------|------|
| VAR_INPUT | 输入变量，由调用方提供 |
| VAR_OUTPUT | 输出变量，由FB产生 |
| FB_TON | 接通延时定时器，IN=TRUE并持续PT时间后Q=TRUE |
| FB_TONR | 累积定时器，保持Q直到显式复位 |
| TON消抖 | 使用FB_TON过滤传感器短暂抖动，信号持续PT时间后才认为有效 |
| 极性映射 | i_bExtendPolarity=TRUE时互换物理传感器逻辑含义，使状态输出与命令语义一致 |
| 单线圈两位阀 | 1个线圈，2个位置，弹簧复位，失电自动收回 |
| 双线圈两位阀 | 2个线圈，2个位置，保持最后位置 |
| 3位4通中封阀 | 2个线圈，3个位置，中位时保持气缸位置 |
| 3位4通中泄阀 | 2个线圈，3个位置，中位时泄压回油 |
| 上位传感器 | 气缸收回位置传感器 |
| 下位传感器 | 气缸伸出位置传感器 |
| 线圈极性取反 | 调整线圈输出逻辑以适应不同接线方式 |
| 信号处理流水线 | 物理传感器→TON消抖→传感器故障检测→极性映射→命令处理 |

---

**文档状态**: 审核中
**下次评审日期**: 2026-06-06
**编制人**: Trae
**审核人**: 人工
