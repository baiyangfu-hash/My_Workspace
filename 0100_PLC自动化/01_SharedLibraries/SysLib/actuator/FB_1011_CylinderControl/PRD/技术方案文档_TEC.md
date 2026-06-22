---
spec_id: TEC-FB1011
title: "FB_1011_CylinderControl技术方案文档"
version: "V13.0.0"
domain: plc
lifecycle: stable
canonical_path: "0100_PLC自动化/01_SharedLibraries/SysLib/actuator/FB_1011_CylinderControl/PRD/技术方案文档_TEC.md"
tags: ["气缸控制", "执行器", "PLC功能块", "技术方案", "电磁阀", "结构体", "防呆锁存", "运行模式"]
---

# 技术方案文档 FB_1011_CylinderControl

## 1. 文档基础信息

**文档标题**：FB_1011_CylinderControl技术方案文档
**文档版本**：V13.0.0
**编制日期**：2026-06-18
**编制人**：Trae
**审核人**：人工
**遵循规范**：TECH-014, LSP-905-V1.0.2, LSP-904-V1.2.0, LSP-903-V2.1.0

## 2. 版本变更记录

| 版本号 | 变更内容 | 变更人 | 变更日期 | 详细说明 |
|--------|----------|--------|----------|----------|
| V13.0.0 | Breaking Change: 引脚重命名对齐LSP-905前缀规范; stCmd→i_stCmd, stSts→q_stSts | Trae | 2026-06-18 | 引脚名对齐LSP-905 V1.0.2 §3.1前缀规范; 调用方需迁移实例化引脚名; 内部逻辑不变 |
| V12.0.0 | 防呆锁存 + 手动/自动模式; 新增s_iLatchedSolenoidType/s_iLatchedMode; Mode=0手动跳过超时; 信号管线增加第5级防呆锁存层 | Trae | 2026-06-18 | 运动中参数锁存防止运行时SolenoidType/Mode跳变; CASE改用锁存值; 手动模式用于调试/维护场景 |
| V11.0.0 | Breaking Change: 扁平接口→结构体接口; i_stCmd:ST_CylinderCmd(CONSTANT)+q_stSts:ST_CylinderSts; q_aSolenoid[0..7]→SolenoidA/SolenoidB; FB引脚14→2; SolenoidType对齐实际场景; 真空阀纳入 | Trae | 2026-06-18 | 重构接口: 拆分为ST_CylinderCmd(输入)+ST_CylinderSts(输出)两个结构体; 删除ARRAY输出改为两个独立BOOL; SolenoidType注释: 0=两位三通单线圈弹簧复位(气缸阀/真空阀), 1=双线圈中封阀(失电中封保持); 结构体支持整体保存/传递/快照 |
| V9.2.0 | P0定时器修复: 定时器调用对齐LSP-903 V2.1.0三段式; 消抖关闭时设IN=FALSE让TON自然复位; 超时检测移入命令分支内加s_bMoving防误报 | Trae | 2026-06-17 | 定时器从条件内联调用改为顶部无条件批量调用; 消抖关闭时设IN=FALSE让TON自然复位Q=FALSE/ET=0; 超时检测从尾部独立检测移入Extend/Retract命令分支内，加s_bMoving条件防误报; 移除尾部独立fb_tTimeout()调用 |
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

| SolenoidType值 | 电磁阀类型 | 线圈数量 | 阀位数 | 输出信号 | 默认行为（无命令时） | 当前V10.0.0支持 |
|-----------|---------|---------|-------|---------|------------------|---------------|
| **0** | **单线圈两位阀** | 1个 | 2位 | q_aSolenoid[0] | 弹簧复位（收回） | ✅ **支持（默认）** |
| **1** | **双线圈两位阀** | 2个 | 2位 | q_aSolenoid[0..7] | 保持最后位置 | ✅ **支持** |
| 2 | 3位4通中封阀 | 2个 | 3位 | q_aSolenoid[0..7] | 保持位置（中封） | ⚠️ 预留扩展 |
| 3 | 3位4通中泄阀 | 2个 | 3位 | q_aSolenoid[0..7] | 泄压回油（中泄） | ⚠️ 预留扩展 |

### 4.2 单线圈两位阀（i_iSolenoidType=0，默认）

**FB_1011 V10.0.0 默认：单线圈两位阀**
- 线圈：1个
- 输出：q_aSolenoid[0] (BOOL)，q_aSolenoid[1]始终FALSE
- [0]=TRUE → 得电伸出（可通过i_bExtendPolarity取反）
- [0]=FALSE → 失电收回（弹簧复位）
- 安全性：失电后气缸自动收回（弹簧复位）

**单线圈两位阀真值表**：

| i_bExtend | i_bRetract | i_bExtendPolarity | q_aSolenoid[0] | q_aSolenoid[1] | 气缸行为 |
|-----------|------------|-------------------|-----------------|-----------------|---------|
| TRUE      | FALSE      | FALSE             | TRUE            | FALSE           | 伸出    |
| FALSE     | TRUE       | FALSE             | FALSE           | FALSE           | 收回    |
| FALSE     | FALSE      | FALSE             | FALSE           | FALSE           | 弹簧复位 |
| TRUE      | FALSE      | TRUE              | FALSE           | FALSE           | 伸出    |
| FALSE     | TRUE       | TRUE              | TRUE            | FALSE           | 收回    |
| FALSE     | FALSE      | TRUE              | TRUE            | FALSE           | 弹簧复位 |

### 4.3 线圈极性取反（ExtendPolarity / RetractPolarity）

| 参数 | 极性值 | 说明 | 输出效果 | 适用场景 |
|------|--------|------|---------|---------|
| i_bExtendPolarity | FALSE (默认) | 正常极性 | 单线圈: [0]=TRUE→伸出; 双线圈: [0]=TRUE→伸出 | 阻挡/夹紧等气缸 |
| i_bExtendPolarity | TRUE | 伸出方向极性取反 | 单线圈: [0]=FALSE→伸出; 双线圈: [0]=FALSE→伸出 | 拍正/顶升等弹簧复位气缸 |
| i_bRetractPolarity | FALSE (默认) | 正常极性 | 双线圈: [1]=TRUE→收回 | 默认接线 |
| i_bRetractPolarity | TRUE | 收回方向极性取反 | 双线圈: [1]=FALSE→收回 | 原点方向接线取反 |

**注意**：i_bRetractPolarity仅在双线圈模式(i_iSolenoidType=1)下生效，单线圈模式下忽略。

### 4.4 双线圈两位阀（i_iSolenoidType=1）

**FB_1011 V10.0.0 新增：双线圈两位阀**
- 线圈：2个（线圈A=动点方向，线圈B=原点方向）
- 输出：q_aSolenoid[0..7] (ARRAY OF BOOL)
  - [0] = 线圈A（动点方向，伸出方向）
  - [1] = 线圈B（原点方向，收回方向）
- 互锁规则：[0]和[1]任意时刻最多一个ON，禁止同时ON
- 保持位特性：无命令时保持最后位置（非弹簧复位），双线圈两位阀无弹簧
- 安全性：失电后气缸保持当前位置，需E-STOP等外部安全机制确保安全

**双线圈两位阀与单线圈两位阀的核心差异**：

| 特性 | 单线圈两位阀 (Type=0) | 双线圈两位阀 (Type=1) |
|------|----------------------|----------------------|
| 线圈数量 | 1个 | 2个 |
| 失电行为 | 弹簧复位（收回） | 保持最后位置 |
| 无命令时 | 弹簧复位 | 保持位（不输出） |
| 输出使用 | 只用[0]，[1]始终FALSE | [0]和[1]互斥使用 |
| 极性参数 | i_bExtendPolarity | i_bExtendPolarity + i_bRetractPolarity |
| 安全特性 | 本质安全（失电收回） | 需外部安全机制 |

### 4.5 双线圈两位阀真值表

**正常极性（i_bExtendPolarity=FALSE, i_bRetractPolarity=FALSE）**：

| i_bExtend | i_bRetract | q_aSolenoid[0] (线圈A) | q_aSolenoid[1] (线圈B) | 气缸行为 |
|-----------|------------|------------------------|------------------------|---------|
| TRUE      | FALSE      | TRUE                   | FALSE                  | 伸出    |
| FALSE     | TRUE       | FALSE                  | TRUE                   | 收回    |
| FALSE     | FALSE      | FALSE                  | FALSE                  | 保持位  |

**伸出方向极性取反（i_bExtendPolarity=TRUE, i_bRetractPolarity=FALSE）**：

| i_bExtend | i_bRetract | q_aSolenoid[0] (线圈A) | q_aSolenoid[1] (线圈B) | 气缸行为 |
|-----------|------------|------------------------|------------------------|---------|
| TRUE      | FALSE      | FALSE                  | FALSE                  | 伸出(A取反) |
| FALSE     | TRUE       | FALSE                  | TRUE                   | 收回    |
| FALSE     | FALSE      | FALSE                  | FALSE                  | 保持位  |

**收回方向极性取反（i_bExtendPolarity=FALSE, i_bRetractPolarity=TRUE）**：

| i_bExtend | i_bRetract | q_aSolenoid[0] (线圈A) | q_aSolenoid[1] (线圈B) | 气缸行为 |
|-----------|------------|------------------------|------------------------|---------|
| TRUE      | FALSE      | TRUE                   | FALSE                  | 伸出    |
| FALSE     | TRUE       | FALSE                  | FALSE                  | 收回(B取反) |
| FALSE     | FALSE      | FALSE                  | FALSE                  | 保持位  |

**双方向极性取反（i_bExtendPolarity=TRUE, i_bRetractPolarity=TRUE）**：

| i_bExtend | i_bRetract | q_aSolenoid[0] (线圈A) | q_aSolenoid[1] (线圈B) | 气缸行为 |
|-----------|------------|------------------------|------------------------|---------|
| TRUE      | FALSE      | FALSE                  | FALSE                  | 伸出(A取反) |
| FALSE     | TRUE       | FALSE                  | FALSE                  | 收回(B取反) |
| FALSE     | FALSE      | FALSE                  | FALSE                  | 保持位  |

## 5. 技术选型

### 5.1 技术栈

| 层次 | 技术/工具 | 版本 | 选型理由 | 替代方案 |
|------|-----------|------|----------|---------|
| 开发语言 | Structured Control Language (SCL) | Siemens TIA Portal | 工业标准，广泛使用 | Ladder Logic (LAD), Function Block Diagram (FBD) |
| 消抖定时器 | FB_TON | Siemens TIA Portal | 接通延时定时器，适用于传感器消抖 | 自定义消抖逻辑 |
| 超时定时器 | FB_TONR | Siemens TIA Portal | 累积定时器，保持Q直到显式复位 | FB_TON |
| 命令分支 | CASE i_iSolenoidType | SCL标准语法 | 多类型电磁阀分支清晰，ELSE兜底安全态，可扩展 | IF/ELSIF嵌套（分支多时难维护） |
| 输出接口 | ARRAY OF BOOL | SCL标准类型 | 统一单/双线圈输出接口，[0]线圈A/[1]线圈B语义明确 | 多个独立BOOL输出（单/双线圈接口不一致） |

### 5.2 依赖管理

#### 5.2.1 PLC依赖

| 依赖项 | 类型 | 用途 | 风险评估 |
|--------|------|------|---------|
| FB_TON | 原生功能块 | 传感器消抖 | 低，Siemens标准功能块 |
| FB_TONR | 原生功能块 | 超时计时 | 低，Siemens标准功能块 |
| LSP-905-V1.0.2 | 规范 | 变量命名规范 | 低，稳定规范 |
| LSP-904-V1.1.0 | 规范 | 注释规范 | 低，稳定规范 |
| LSP-903-V2.1.0 | 规范 | 编程规范 | 低，稳定规范 |

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

### 6.2 架构图（V10.0.0 支持单/双线圈两位阀）

```
┌──────────────────────────────────────────────────────────────┐
│               FB_1011_CylinderControl                        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  ⓪ 定时器批量调用区 (3个定时器无条件调用)             │   │
│  │  fb_tDebounceExt, fb_tDebounceRet, fb_tTimeout       │   │
│  └──────────────────────────────────────────────────────┘   │
│                          ↓                                   │
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
│  │  ⑤ CASE i_iSolenoidType 命令处理                      │   │
│  │  0: 单线圈命令处理 (IF/ELSIF/ELSE)                   │   │
│  │  1: 双线圈命令处理 (A/B互锁, 保持位)                 │   │
│  │  ELSE: 安全态 (全OFF)                                │   │
│  │  i_bExtend > i_bRetract → 电磁阀控制                 │   │
│  │  到位检测 → 状态更新 → 定时器控制                     │   │
│  │  i_iSolenoidType + i_bExtendPolarity                 │   │
│  │  + i_bRetractPolarity → 输出逻辑                     │   │
│  └──────────────────────────────────────────────────────┘   │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  ⑥ 超时定时器 (fb_tTimeout, FB_TONR)                │   │
│  │  IN/PT/Q/ET → q_bTimeout                             │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
         ↑                                  ↓
  VAR_INPUT (9个)                    VAR_OUTPUT (5个)
```

### 6.3 信号处理流水线

V10.0.0采用明确的6级信号处理流水线，每级职责单一：

```
定时器批量调用 → 物理传感器 → TON消抖 → 传感器故障检测 → 极性映射 → CASE命令处理
```

| 流水线阶段 | 输入 | 输出 | 实现方式 |
|-----------|------|------|---------|
| ⓪ 定时器批量调用 | fb_tDebounceExt/Ret/Timeout的IN/PT/R | Q, ET | 无条件调用3个定时器 (LSP-903 V2.1.0 §3.4) |
| ① 物理传感器 | i_bExtendedPos, i_bRetractedPos | 原始信号 | 直接读取 |
| ② TON消抖 | 原始信号, i_dDebounceMs | s_bExtDebounced, s_bRetDebounced | FB_TON × 2 |
| ③ 传感器故障检测 | s_bExtDebounced, s_bRetDebounced | q_bSensorFault | 组合逻辑 |
| ④ 极性映射 | s_bExtDebounced, s_bRetDebounced, i_bExtendPolarity | s_bLogicExtPos, s_bLogicRetPos | 条件互换 |
| ⑤ CASE命令处理 | i_bExtend, i_bRetract, s_bLogicExtPos, s_bLogicRetPos, i_iSolenoidType, i_bExtendPolarity, i_bRetractPolarity | q_aSolenoid[0..7], q_bIsExtended, q_bIsRetracted, q_bTimeout | CASE i_iSolenoidType分支: 0=单线圈, 1=双线圈, ELSE=安全态 |

### 6.4 模块划分

| 模块名称 | 功能描述 | 技术实现 | 负责人 | 优先级 |
|---------|---------|----------|--------|--------|
| TON消抖 | 传感器信号消抖，滤除短暂抖动 | FB_TON × 2 | Trae | P0 |
| 传感器故障检测 | 上下位同时ON检测 | 纯组合逻辑 | Trae | P0 |
| 极性映射 | 极性取反时互换传感器逻辑含义 | 条件赋值 | Trae | P0 |
| 单线圈命令处理 | i_iSolenoidType=0时的伸出/收回控制 | IF/ELSIF/ELSE状态机 | Trae | P0 |
| 双线圈命令处理 | i_iSolenoidType=1时的A/B互锁控制 | A/B互锁+保持位逻辑 | Trae | P0 |
| 电磁阀输出逻辑 | 根据i_iSolenoidType+极性参数输出到q_aSolenoid | CASE分支+极性映射 | Trae | P0 |
| 超时计时 | 动作超时检测 | FB_TONR | Trae | P1 |
| 状态更新 | 到位状态、超时状态更新 | 逻辑赋值 | Trae | P1 |

### 6.5 数据流设计（V10.0.0 单/双线圈两位阀）

```
┌──────────────────────────────────────────────────────────────┐
│  VAR_INPUT (9个)                                             │
├──────────────────────────────────────────────────────────────┤
│  i_bExtend (BOOL)          ────┐                              │
│  i_bRetract (BOOL)         ────┼─→ CASE命令处理模块            │
│  i_bExtendedPos (BOOL)     ────┤                              │
│  i_bRetractedPos (BOOL)    ────┼─→ TON消抖 → 故障检测 → 极性映射│
│  i_dTimeoutMs (DINT)       ────┼─→ 超时定时器                  │
│  i_dDebounceMs (DINT)      ────┼─→ 消抖定时器PT                │
│  i_iSolenoidType (INT)     ────┼─→ CASE分支选择                │
│  i_bExtendPolarity (BOOL)  ────┼─→ 极性映射 + 电磁阀输出逻辑   │
│  i_bRetractPolarity (BOOL) ────┘─→ 双线圈原点方向极性 + 输出逻辑│
└──────────────────────────────────────────────────────────────┘
                               ↓
┌──────────────────────────────────────────────────────────────┐
│  VAR_OUTPUT (5个)                                            │
├──────────────────────────────────────────────────────────────┤
│  q_aSolenoid[0..7] (ARRAY) ←─── 电磁阀输出逻辑               │
│    [0]=线圈A(动点方向)                                       │
│    [1]=线圈B(原点方向)                                       │
│  q_bIsExtended (BOOL)     ←─── 状态更新模块                   │
│  q_bIsRetracted (BOOL)    ←─── 状态更新模块                   │
│  q_bTimeout (BOOL)        ←─── 超时定时器                     │
│  q_bSensorFault (BOOL)    ←─── 传感器故障检测模块             │
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
│   │   ├── ST_Cylinder.scl
│   │   └── PRD/
│   │       ├── 需求分析文档_REQ.md
│   │       ├── 技术方案文档_TEC.md
│   │       ├── 接口文档_INT.md
│   │       └── 详细设计说明书_DSN.md
│   ├── FB_1012_ConveyorMotor/
│   ├── FB_1013_NinetyDegreeTransfer/
│   └── FB_1014_StationConveyor/
```

#### 7.1.2 功能块设计

| 功能块名称 | 功能描述 | 输入参数 | 输出参数 | 调用关系 |
|---------|---------|---------|---------|---------|
| FB_1011_CylinderControl | 气缸控制（支持单/双线圈中封阀 + 防呆锁存 + 手动/自动模式） | i_stCmd: ST_CylinderCmd (1个结构体) | q_stSts: ST_CylinderSts (1个结构体) | 被上级FB调用 |

### 7.2 核心代码结构（V13.0.0）

#### 7.2.1 FB声明

```scl
FUNCTION_BLOCK FB_1011_CylinderControl

VAR_INPUT CONSTANT
    i_stCmd : ST_CylinderCmd;  // 命令+参数结构体, CONSTANT禁止FB内部篡改
END_VAR

VAR_OUTPUT
    q_stSts : ST_CylinderSts;  // 状态输出结构体
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
    s_iLatchedSolenoidType : INT := 0; // ★ 防呆: 运动中锁存的SolenoidType
    s_iLatchedMode         : INT := 1; // ★ 防呆: 运动中锁存的Mode, 默认自动安全态
END_VAR
```

#### 7.2.2 防呆锁存代码（V12.0.0）★

```scl
(* ==================== 防呆: 参数锁存 (运动中不可变, 空闲时刷新) ==================== *)
(* 目的: 防止运行时 SolenoidType/Mode 跳变导致 CASE 分支错乱 *)
(* 规则: s_bMoving=FALSE 时刷新锁存值; s_bMoving=TRUE 时保持上次锁存值不变 *)
IF NOT s_bMoving THEN
    s_iLatchedSolenoidType := i_stCmd.SolenoidType;
    s_iLatchedMode := i_stCmd.Mode;
END_IF;
```

#### 7.2.3 命令处理（CASE s_iLatchedSolenoidType + Mode判断）★

```scl
(* ==================== 命令处理: CASE按锁存的电磁阀类型分支 ==================== *)

CASE s_iLatchedSolenoidType OF

    0:  (* ---- 两位三通单线圈弹簧复位 (气缸阀/真空阀) ---- *)
        IF i_stCmd.Extend THEN
            (* Extend优先，根据极性输出 *)
            IF i_stCmd.ExtendPolarity THEN
                q_stSts.SolenoidA := FALSE;
            ELSE
                q_stSts.SolenoidA := TRUE;
            END_IF;
            q_stSts.SolenoidB := FALSE;

            (* 自动模式: 启动超时计时 *)
            IF NOT s_bMoving THEN
                s_bMoving := TRUE;
                IF s_iLatchedMode = 1 AND i_stCmd.TimeoutMs > 0 THEN
                    fb_tTimeout.IN := TRUE;
                    fb_tTimeout.R := FALSE;
                    fb_tTimeout.PT := i_stCmd.TimeoutMs;
                END_IF;
            END_IF;

            IF s_bLogicExtPos THEN
                q_stSts.IsExtended := TRUE;
                q_stSts.IsRetracted := FALSE;
                s_bMoving := FALSE;
                q_stSts.Timeout := FALSE;
                fb_tTimeout.IN := FALSE;
                fb_tTimeout.R := TRUE;
            END_IF;

            (* 自动模式: 超时检测 *)
            IF s_iLatchedMode = 1 AND fb_tTimeout.Q AND s_bMoving THEN
                q_stSts.Timeout := TRUE;
            END_IF;

        ELSIF i_stCmd.Retract THEN
            (* ... 收回逻辑 *)
        ELSE
            (* ... 空闲逻辑 *)
        END_IF;

    1:  (* ---- 双线圈中封阀 ---- *)
        (* ... A/B互锁 + 中封保持逻辑 *)

    ELSE
        (* 非法类型安全兜底 *)
        q_stSts.SolenoidA := FALSE;
        q_stSts.SolenoidB := FALSE;
        (* ... 全部复位 *)
END_CASE;
```

## 8. 接口设计

### 8.1 内部接口

| 接口名称 | 调用方 | 被调用方 | 参数 | 返回值 | 说明 |
|---------|--------|---------|------|--------|------|
| FB_1011_CylinderControl | 上级FB | FB_1011 | i_stCmd: ST_CylinderCmd (1个结构体) | q_stSts: ST_CylinderSts (1个结构体) | 核心接口 |

### 8.2 外部接口

| 接口名称 | 协议 | 方向 | 数据格式 | 频率 | 说明 |
|---------|------|------|---------|------|------|
| OB1 IO映射 | 硬件IO | 双向 | ST_CylinderCmd.ExtendedPos/RetractedPos, ST_CylinderSts.SolenoidA/SolenoidB | 每扫描周期 | 物理传感器输入，电磁阀BOOL输出 |
| 上级编排器 | 内部调用 | 双向 | 结构体 | 每扫描周期 | 如FB_1002，通过i_stCmd/q_stSts交互 |
| 报警管理 | 内部调用 | 输出 | BOOL, BOOL | 每扫描周期 | q_stSts.Timeout和q_stSts.SensorFault信号 |

## 9. 数据结构设计

### 9.1 结构体接口说明

V11.0.0引入结构体接口，替代V9.x-V10.x的扁平接口。接口引脚数从14→2。结构体定义详见 `ST_Cylinder.scl` V3.1.0。

**ST_CylinderCmd（输入结构体）**：

| 字段 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| Extend | BOOL | FALSE | 动点命令: 伸出/真空ON/夹紧/下降 |
| Retract | BOOL | FALSE | 原点命令: 收回/破真空/松开/上升 |
| ExtendedPos | BOOL | FALSE | 动点到位: 伸出位传感器/真空表 |
| RetractedPos | BOOL | FALSE | 原点到位: 收回位传感器/大气压力 |
| TimeoutMs | DINT | 5000 | 动作超时时间 ms, 0=关闭 |
| DebounceMs | DINT | 0 | 传感器消抖时间 ms, 0=关闭 |
| SolenoidType | INT | 0 | 电磁阀类型: 0=两位三通单线圈弹簧复位, 1=双线圈中封阀 |
| ExtendPolarity | BOOL | FALSE | 线圈A极性: FALSE=正常, TRUE=取反 |
| RetractPolarity | BOOL | FALSE | 线圈B极性: FALSE=正常, TRUE=取反; 仅双线圈模式生效 |
| Mode | INT | 1 | 运行模式: 0=手动(跳过超时), 1=自动(全保护); 默认自动安全态 ★ |
| ModeStatus | WORD | 16#0000 | 模式状态字: 上层传递的状态标志, 预留 ★ |

**ST_CylinderSts（输出结构体）**：

| 字段 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| SolenoidA | BOOL | FALSE | 线圈A输出: 动点方向 |
| SolenoidB | BOOL | FALSE | 线圈B输出: 原点方向; 单线圈时始终FALSE |
| IsExtended | BOOL | FALSE | 已到动点（极性映射后） |
| IsRetracted | BOOL | FALSE | 已到原点（极性映射后） |
| Timeout | BOOL | FALSE | 动作超时报警 |
| SensorFault | BOOL | FALSE | 传感器冲突: 两点同时ON, 消抖后检测 |

**VAR（内部变量，12个）**：

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
| s_iLatchedSolenoidType | INT | 0 | ★ 防呆: 运动中锁存的SolenoidType, 空闲时刷新 |
| s_iLatchedMode | INT | 1 | ★ 防呆: 运动中锁存的Mode, 空闲时刷新; 默认自动安全态 |

### 9.2 存储策略

- **数据存储**：所有状态在FB实例内部维护
- **备份策略**：结构体支持整体保存/传递/快照
- **清理策略**：不需要清理，FB实例随程序清除

## 10. 安全设计

### 10.1 安全需求

- 超时仅报警不强制复位，保持输出状态
- 传感器故障实时检测
- 命令优先级防止冲突
- 失电自动弹簧复位（单线圈弹簧复位阀安全特性）
- 双线圈A/B互锁，任意时刻最多一个ON（双线圈中封阀安全特性）
- 双线圈无命令时中封保持，需E-STOP等外部安全机制确保安全
- 传感器消抖防止误触发
- 非法SolenoidType值时进入安全态（全OFF）
- 运动中参数防呆锁存，防止运行时SolenoidType/Mode跳变 ★
- 手动模式(Mode=0)跳过超时检测，仅用于调试/维护场景 ★

### 10.2 安全措施

| 风险点 | 风险等级 | 应对措施 | 责任人 |
|---------|---------|---------|--------|
| 超时后气缸继续动作 | 中 | 超时仅报警，不强制改变电磁阀，由上级决定策略 | Trae |
| 传感器故障未发现 | 中 | 实时检测上下位同时ON状态，立即报警 | Trae |
| 命令冲突 | 低 | i_stCmd.Extend优先于i_stCmd.Retract，防止电磁阀频繁切换 | Trae |
| 失电安全（单线圈） | 高 | 单线圈两位阀，失电自动弹簧复位收回 | Trae |
| 电磁阀选型错误 | 中 | 提供SolenoidType参数，明确文档说明 | Trae |
| 传感器抖动误触发 | 中 | TON消抖层，DebounceMs可配置 | Trae |
| 极性接线错误 | 中 | ExtendPolarity/RetractPolarity极性映射层，传感器同步互换 | Trae |
| 双线圈A/B同时ON | 高 | 硬互锁：A ON时B强制OFF，B ON时A强制OFF，代码级保证 | Trae |
| 双线圈中封保持安全 | 高 | 无命令时全OFF（中封保持），到位后驱动线圈OFF，需E-STOP外部回路切断供电 | Trae |
| 双线圈E-STOP策略 | 高 | E-STOP回路应直接切断双线圈阀供电，不依赖PLC程序 | Trae |
| 非法SolenoidType | 中 | CASE ELSE分支进入安全态，全OFF+状态清零 | Trae |
| 运动中参数跳变 ★ | 高 | 防呆锁存: s_bMoving=TRUE时锁存SolenoidType/Mode; 空闲时自动刷新 | Trae |
| 手动模式安全 ★ | 高 | Mode=0仅用于调试/维护; 默认Mode=1自动全保护; 手动模式文档明确标注安全警告 | Trae |

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
- 定时器每周期无条件调用，业务逻辑只设参数只读输出
- 使用TONR而非多个TON做超时计时，减少资源占用
- 极性映射使用简单条件赋值，不增加额外延时
- 电磁阀输出逻辑条件判断，不增加额外延时

## 12. 风险评估

### 12.1 技术风险

| 风险项 | 可能性 | 影响程度 | 风险等级 | 应对措施 | 责任人 |
|---------|---------|---------|---------|---------|--------|
| 结构体接口复杂性 | 低 | 低 | 低 | 仅2个引脚，结构体字段清晰 | Trae |
| 超时策略争议 | 中 | 中 | 低 | 保持当前策略，记录设计决策 | Trae |
| 传感器类型差异 | 中 | 低 | 低 | OB1处理传感器类型，本FB仅接收BOOL | Trae |
| 电磁阀选型变更 | 中 | 中 | 中 | 提供参数配置，支持取反和类型选择 | Trae |
| 消抖时间设置不当 | 中 | 中 | 中 | 默认0=关闭，文档明确推荐值范围 | Trae |
| 极性映射逻辑复杂 | 低 | 中 | 低 | 极性映射层独立，可单独测试验证 | Trae |
| Breaking Change迁移风险 | 高 | 高 | 高 | V11.0.0扁平→结构体; V13.0.0 stCmd→i_stCmd; 所有调用方需修改; 提供迁移指南 | Trae |
| 双线圈极性语义风险 | 中 | 高 | 高 | RetractPolarity仅在双线圈生效，单线圈下忽略；文档明确说明适用范围 | Trae |
| 防呆锁存失效风险 ★ | 中 | 高 | 高 | s_bMoving状态机正确性需充分测试；锁存值初始默认值安全 | Trae |
| 手动模式误用风险 ★ | 中 | 高 | 高 | Mode默认1(自动安全态); 手动模式使用需授权; 文档明确标注安全警告 | Trae |

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

**单线圈两位阀（i_iSolenoidType=0）**：

- [x] 伸出控制：i_bExtend=TRUE时，q_aSolenoid[0]=伸出极性，q_aSolenoid[1]=FALSE，s_bLogicExtPos=TRUE后q_bIsExtended=TRUE
- [x] 收回控制：i_bRetract=TRUE时，q_aSolenoid[0]=收回极性，q_aSolenoid[1]=FALSE，s_bLogicRetPos=TRUE后q_bIsRetracted=TRUE
- [x] 命令优先级：i_bExtend和i_bRetract同时TRUE，q_aSolenoid[0]=伸出极性
- [x] 传感器一致性检查：两传感器同时ON，q_bSensorFault=TRUE
- [x] 超时保护：i_dTimeoutMs=5000，动作5秒未到位，q_bTimeout=TRUE
- [x] 超时关闭：i_dTimeoutMs=0，不触发超时
- [x] 单线圈两位阀默认配置：i_iSolenoidType=0时，工作正常
- [ ] 线圈极性取反：i_bExtendPolarity=TRUE时，线圈输出取反，传感器逻辑互换
- [ ] 传感器消抖：i_dDebounceMs>0时，传感器信号消抖后输出
- [ ] 消抖关闭：i_dDebounceMs=0时，传感器信号直通

**双线圈两位阀（i_iSolenoidType=1）**：

- [ ] 双线圈伸出：i_bExtend=TRUE时，q_aSolenoid[0]=伸出极性，q_aSolenoid[1]=FALSE
- [ ] 双线圈收回：i_bRetract=TRUE时，q_aSolenoid[0]=FALSE，q_aSolenoid[1]=收回极性
- [ ] 双线圈A/B互锁：任意时刻q_aSolenoid[0]和q_aSolenoid[1]最多一个ON
- [ ] 双线圈保持位：i_bExtend=FALSE且i_bRetract=FALSE时，q_aSolenoid[0]=FALSE，q_aSolenoid[1]=FALSE，气缸保持当前位置
- [ ] 双线圈收回极性取反：i_bRetractPolarity=TRUE时，q_aSolenoid[1]极性取反
- [ ] 双线圈伸出极性取反：i_bExtendPolarity=TRUE时，q_aSolenoid[0]极性取反
- [ ] 双线圈超时保护：i_dTimeoutMs=5000，动作5秒未到位，q_bTimeout=TRUE
- [ ] 双线圈到位检测：伸出到位q_bIsExtended=TRUE，收回到位q_bIsRetracted=TRUE

**非法类型兜底**：

- [ ] 非法SolenoidType：i_iSolenoidType=99时，q_aSolenoid[0]=FALSE，q_aSolenoid[1]=FALSE，q_bIsExtended=FALSE，q_bIsRetracted=FALSE

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
| 需求分析文档_REQ.md | V10.0.0 | 本目录 |
| 接口文档_INT.md | V10.0.0 | 本目录 |
| 详细设计说明书_DSN.md | V10.0.0 | 本目录 |
| LSP-905_PLC变量命名规范_V1.0.2.md | V1.0.2 | 0100_PLC自动化/00_通用规范/PLC编程/ |
| LSP-904_SCL注释规范_V1.1.0.md | V1.1.0 | 0100_PLC自动化/00_通用规范/PLC编程/ |
| 903_定时器使用规范_LSP.md | V2.1.0 | 0100_PLC自动化/00_通用规范/PLC编程/ |

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
| 双线圈两位阀 | 2个线圈，2个位置，保持最后位置，A/B互锁，无命令时保持位 |
| 线圈A | 双线圈两位阀的动点方向线圈，对应q_aSolenoid[0] |
| 线圈B | 双线圈两位阀的原点方向线圈，对应q_aSolenoid[1] |
| A/B互锁 | 双线圈两位阀安全约束，任意时刻最多一个线圈ON，禁止同时ON |
| 保持位 | 双线圈两位阀无命令时气缸保持当前位置的特性（非弹簧复位） |
| i_bRetractPolarity | 收回方向极性取反参数，仅双线圈模式下生效，控制线圈B极性 |
| q_aSolenoid | 电磁阀ARRAY输出，[0]=线圈A(动点方向)，[1]=线圈B(原点方向) |
| CASE ELSE安全态 | i_iSolenoidType为非法值时，所有输出OFF，状态清零 |
| 3位4通中封阀 | 2个线圈，3个位置，中位时保持气缸位置 |
| 3位4通中泄阀 | 2个线圈，3个位置，中位时泄压回油 |
| 上位传感器 | 气缸收回位置传感器 |
| 下位传感器 | 气缸伸出位置传感器 |
| 线圈极性取反 | 调整线圈输出逻辑以适应不同接线方式 |
| 信号处理流水线 | 定时器批量调用→物理传感器→TON消抖→传感器故障检测→极性映射→CASE命令处理 |

---

**文档状态**: 审核中
**下次评审日期**: 2026-06-24
**编制人**: Trae
**审核人**: 人工