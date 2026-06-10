---
spec_id: DSN-FB1011
title: "FB_1011 气缸控制详细设计"
version: "V9.0.0"
domain: plc
lifecycle: stable
canonical_path: "0100_PLC自动化/01_SharedLibraries/SysLib/actuator/FB_1011_CylinderControl/PRD/详细设计说明书_DSN-FB1011-CylinderControl-V9.0.0.md"
tags: ["气缸控制", "执行器", "PLC功能块", "详细设计", "电磁阀"]
---

# 详细设计说明书 FB_1011_CylinderControl

## 0. 文档基础信息

| 属性 | 值 |
|------|-----|
| **文档标题** | FB_1011 气缸控制详细设计 |
| **文档版本** | V9.0.0 |
| **关联源码** | actuator/FB_1011_CylinderControl/FB_1011_CylinderControl.scl |
| **关联IFC** | 接口文档_IFC-FB1011-CylinderControl-V9.0.0.md |
| **关联REQ** | 需求分析文档_REQ-FB1011-CylinderControl-V8.1.0.md |
| **关联TECH** | 技术方案文档_TECH-FB1011-CylinderControl-V8.1.0.md |
| **编制日期** | 2026-05-30 |
| **编制人** | Trae |
| **遵循规范** | LSP-905-V1.0.2, LSP-904-V1.1.0, LSP-903-V2.1.0 |

## 0.1 版本变更摘要（V7.1.0 → V9.0.0）

| 变更项 | V7.1.0 | V9.0.0 |
|--------|--------|--------|
| 接口方式 | VAR_IN_OUT ST_Cylinder | 扁平 VAR_INPUT / VAR_OUTPUT |
| 变量命名 | io_stCyl.Xxx | i_bXxx / q_bXxx / s_bXxx / fb_tXxx |
| 传感器消抖 | 无 | TON消抖（i_dDebounceMs控制） |
| 极性取反 | 仅电磁阀输出取反 | 完整极性映射层（传感器互换+输出取反） |
| 信号流水线 | 传感器→故障检测→命令处理 | 物理传感器→TON消抖→故障检测→极性映射→命令处理 |
| 规范引用 | 801_DEV, 810_DEV, 904_LSP | LSP-905, LSP-904, LSP-903 |

## 0.2 电磁阀类型说明

| SolenoidType值 | 电磁阀类型 | 线圈数量 | 输出信号 | 默认行为 | 当前支持 |
|-----------|---------|---------|---------|------------------|---------------|
| **0** | **单线圈两位阀** | 1个 | q_bSolenoid | 弹簧复位（收回） | ✅ **支持（默认）** |
| 1 | 双线圈两位阀 | 2个 | q_bExtendSolenoid, q_bRetractSolenoid | 保持最后位置 | ⚠️ 预留扩展 |
| 2 | 3位4通中封阀 | 2个 | q_bExtendSolenoid, q_bRetractSolenoid | 保持位置（中封） | ⚠️ 预留扩展 |
| 3 | 3位4通中泄阀 | 2个 | q_bExtendSolenoid, q_bRetractSolenoid | 泄压回油（中泄） | ⚠️ 预留扩展 |

### 0.2.1 单线圈两位阀真值表（默认配置）

| i_bExtend | i_bRetract | i_bExtendPolarity | q_bSolenoid | 气缸行为 |
|-----------|------------|-------------------|-------------|---------|
| TRUE      | FALSE      | FALSE             | TRUE        | 伸出    |
| FALSE     | TRUE       | FALSE             | FALSE       | 收回    |
| FALSE     | FALSE      | FALSE             | FALSE       | 弹簧复位 |
| TRUE      | FALSE      | TRUE              | FALSE       | 伸出    |
| FALSE     | TRUE       | TRUE              | TRUE        | 收回    |
| FALSE     | FALSE      | TRUE              | TRUE        | 弹簧复位 |

## 1. 设计原则

1. **命令驱动**: 气缸只响应伸出/收回命令，不自行决定何时动作
2. **输出保持**: 无新命令时保持电磁阀状态为弹簧复位（单线圈两位阀安全特性）
3. **超时隔离**: 超时仅报警不强制复位，编排器决定后续策略
4. **传感器故障实时诊断**: 上下位冲突检测为纯组合逻辑，无延时
5. **传感器消抖**: 物理传感器信号经TON定时器消抖后参与逻辑判断，消除抖动误触发
6. **极性映射完整**: 极性取反不仅翻转电磁阀输出，同时互换逻辑传感器映射，确保逻辑层与物理层一致
7. **可复用**: 同一FB可实例化为阻挡气缸、分料气缸或任何二位置气动执行器
8. **通用性**: 支持多种电磁阀类型配置，支持线圈极性取反

## 2. 信号处理流水线

V9.0.0 引入五级信号处理流水线，确保传感器信号可靠、逻辑一致：

```
物理传感器          TON消抖           传感器故障检测        极性映射              命令处理
─────────  ──→  ──────────  ──→  ──────────────  ──→  ──────────  ──→  ──────────
i_bExtendedPos      fb_tDebounceExt    s_bExtDebounced     s_bLogicExtPos       伸出/收回
i_bRetractedPos     fb_tDebounceRet    s_bRetDebounced     s_bLogicRetPos       到位检测
                                       ↓                   ↓                    超时检测
                                    q_bSensorFault      (极性互换)           q_bSolenoid
                                                                              q_bIsExtended
                                                                              q_bIsRetracted
```

### 2.1 各级说明

| 级别 | 名称 | 输入 | 输出 | 说明 |
|------|------|------|------|------|
| 1 | 物理传感器 | — | i_bExtendedPos, i_bRetractedPos | 来自DI模块的原始传感器信号 |
| 2 | TON消抖 | i_bExtendedPos, i_bRetractedPos, i_dDebounceMs | s_bExtDebounced, s_bRetDebounced | 消除传感器抖动，i_dDebounceMs=0时直通 |
| 3 | 传感器故障检测 | s_bExtDebounced, s_bRetDebounced | q_bSensorFault | 两信号同时为TRUE时判定冲突 |
| 4 | 极性映射 | s_bExtDebounced, s_bRetDebounced, i_bExtendPolarity | s_bLogicExtPos, s_bLogicRetPos | 极性取反时互换两个传感器映射 |
| 5 | 命令处理 | i_bExtend, i_bRetract, s_bLogicExtPos, s_bLogicRetPos | q_bSolenoid, q_bIsExtended, q_bIsRetracted, q_bTimeout | 伸出/收回命令驱动与到位检测 |

## 3. 状态定义

本FB不维护业务流程状态，仅跟踪物理状态（单线圈两位阀）：

| 物理状态 | 条件 | 电磁阀输出 |
|----------|------|:---------:|
| 收回位置 | s_bLogicRetPos=TRUE, s_bLogicExtPos=FALSE | 弹簧复位状态 |
| 伸出位置 | s_bLogicExtPos=TRUE, s_bLogicRetPos=FALSE | 伸出状态 |
| 运动中(伸出) | 两逻辑传感器都FALSE, 命令=i_bExtend | 伸出状态 |
| 运动中(收回) | 两逻辑传感器都FALSE, 命令=i_bRetract | 收回状态 |
| 传感器故障 | s_bExtDebounced=TRUE AND s_bRetDebounced=TRUE | 保持上次 |

## 4. 详细伪代码

```pascal
(* ==================== 第1级: 物理传感器 (直接读取VAR_INPUT) ==================== *)
(* i_bExtendedPos, i_bRetractedPos 已在接口定义 *)

(* ===== 定时器批量调用 (无条件, 每周期执行, LSP-903 V2.1.0 §3.4) ===== *)
fb_tDebounceExt(IN := fb_tDebounceExt.IN, PT := fb_tDebounceExt.PT,
                 Q => fb_tDebounceExt.Q, ET => fb_tDebounceExt.ET);
fb_tDebounceRet(IN := fb_tDebounceRet.IN, PT := fb_tDebounceRet.PT,
                 Q => fb_tDebounceRet.Q, ET => fb_tDebounceRet.ET);
fb_tTimeout(IN := fb_tTimeout.IN, R := fb_tTimeout.R, PT := fb_tTimeout.PT,
             Q => fb_tTimeout.Q, ET => fb_tTimeout.ET);

(* ===== 第2级: TON消抖 (只设参数, 只读输出, 不调用定时器) ===== *)
IF i_dDebounceMs > 0 THEN
    fb_tDebounceExt.IN := i_bExtendedPos;
    fb_tDebounceExt.PT := i_dDebounceMs;
    s_bExtDebounced := fb_tDebounceExt.Q;
    s_dExtDebounceEt := fb_tDebounceExt.ET;

    fb_tDebounceRet.IN := i_bRetractedPos;
    fb_tDebounceRet.PT := i_dDebounceMs;
    s_bRetDebounced := fb_tDebounceRet.Q;
    s_dRetDebounceEt := fb_tDebounceRet.ET;
ELSE
    s_bExtDebounced := i_bExtendedPos;
    s_bRetDebounced := i_bRetractedPos;
END_IF;

(* ==================== 第3级: 传感器故障检测 ==================== *)
IF s_bExtDebounced AND s_bRetDebounced THEN
    q_bSensorFault := TRUE;
ELSE
    q_bSensorFault := FALSE;
END_IF;

(* ==================== 第4级: 极性映射 ==================== *)
IF i_bExtendPolarity THEN
    s_bLogicExtPos := s_bRetDebounced;
    s_bLogicRetPos := s_bExtDebounced;
ELSE
    s_bLogicExtPos := s_bExtDebounced;
    s_bLogicRetPos := s_bRetDebounced;
END_IF;

(* ==================== 第5级: 命令处理（单线圈两位阀默认配置）==================== *)

(* 命令优先级: Extend > Retract *)
IF i_bExtend THEN
    (* ---- 伸出命令 ---- *)
    IF i_bExtendPolarity THEN
        q_bSolenoid := FALSE;
    ELSE
        q_bSolenoid := TRUE;
    END_IF;

    IF NOT s_bMoving THEN
        s_bMoving := TRUE;
        IF i_dTimeoutMs > 0 THEN
            fb_tTimeout.IN := TRUE;
            fb_tTimeout.R := FALSE;
            fb_tTimeout.PT := i_dTimeoutMs;
        END_IF;
    END_IF;

    (* 到位检测 *)
    IF s_bLogicExtPos THEN
        q_bIsExtended := TRUE;
        q_bIsRetracted := FALSE;
        s_bMoving := FALSE;
        q_bTimeout := FALSE;
        fb_tTimeout.IN := FALSE;
        fb_tTimeout.R := TRUE;
    END_IF;

    (* 超时检测 *)
    IF fb_tTimeout.Q THEN
        q_bTimeout := TRUE;
    END_IF;

ELSIF i_bRetract THEN
    (* ---- 收回命令 ---- *)
    IF i_bExtendPolarity THEN
        q_bSolenoid := TRUE;
    ELSE
        q_bSolenoid := FALSE;
    END_IF;

    IF NOT s_bMoving THEN
        s_bMoving := TRUE;
        IF i_dTimeoutMs > 0 THEN
            fb_tTimeout.IN := TRUE;
            fb_tTimeout.R := FALSE;
            fb_tTimeout.PT := i_dTimeoutMs;
        END_IF;
    END_IF;

    (* 到位检测 *)
    IF s_bLogicRetPos THEN
        q_bIsRetracted := TRUE;
        q_bIsExtended := FALSE;
        s_bMoving := FALSE;
        q_bTimeout := FALSE;
        fb_tTimeout.IN := FALSE;
        fb_tTimeout.R := TRUE;
    END_IF;

    (* 超时检测 *)
    IF fb_tTimeout.Q THEN
        q_bTimeout := TRUE;
    END_IF;

ELSE
    (* ---- 无命令：空闲 ---- *)
    IF i_bExtendPolarity THEN
        q_bSolenoid := TRUE;
    ELSE
        q_bSolenoid := FALSE;
    END_IF;

    s_bMoving := FALSE;
    q_bTimeout := FALSE;
    fb_tTimeout.IN := FALSE;
    fb_tTimeout.R := TRUE;

    q_bIsExtended := s_bLogicExtPos;
    q_bIsRetracted := s_bLogicRetPos;
END_IF;
```

## 5. 时序图

### 5.1 正常伸出→收回周期（单线圈两位阀）

```
i_bExtend         ──────┐                     ┌──────
                         └─────────────────────┘
i_bRetract        ─────────────────┐          ┌──────
                                  └──────────┘
q_bSolenoid       ──────┐                     │
                       └─────────────────────┘
i_bExtendedPos    ─────────┐          ┌────────────────
                            └──────────┘
s_bExtDebounced   ─────────┐          ┌────────────────
                            └──────────┘
i_bRetractedPos   ──────┐                     ┌──────
                         └─────────────────────┘
s_bRetDebounced   ──────┐                     ┌──────
                         └─────────────────────┘
s_bLogicExtPos    ─────────┐          ┌────────────────
                            └──────────┘
s_bLogicRetPos    ──────┐                     ┌──────
                         └─────────────────────┘
q_bIsExtended     ─────────┐          ┌────────────────
                           └──────────┘
q_bIsRetracted    ──────┐                     ┌──────
                           └─────────────────────┘
s_bMoving         ────────┐          ┌─────────────
                         └──────────┘
fb_tTimeout.IN    ──────┐  ┌────────┐  ┌─────────────
                       └──┘        └──┘
```

### 5.2 超时场景

```
i_bExtend         ──────┐
                         └────────────────────────── ...
q_bSolenoid       ──────┐
                         └────────────────────────── ...
i_bExtendedPos    ─────────────────────────────────── ... (始终未到位)
s_bExtDebounced   ─────────────────────────────────── ... (始终未到位)
fb_tTimeout.Q     ──────────────────┐
                                   └────────────── ... (超时到达)
q_bTimeout        ──────────────────┐
                                   └────────────── ... (锁存)
```

### 5.3 传感器消抖时序

```
i_bExtendedPos    ──┐ ┌─┐    ┌────────────────
                    └─┘ └────┘  (物理抖动)
                     ← i_dDebounceMs →
s_bExtDebounced   ───────────────┐─────────────
                                └───────────── (消抖后稳定)
```

### 5.4 极性取反时序（i_bExtendPolarity=TRUE）

```
i_bExtendedPos    ─────────┐          ┌────────────────
                            └──────────┘
i_bRetractedPos   ──────┐                     ┌──────
                         └─────────────────────┘
s_bLogicExtPos    ──────┐                     ┌──────  (←映射自RetDebounced)
                         └─────────────────────┘
s_bLogicRetPos    ─────────┐          ┌────────────────  (←映射自ExtDebounced)
                            └──────────┘
q_bSolenoid       ──────┐                     │  (伸出=FALSE, 收回=TRUE)
                       └─────────────────────┘
```

## 6. 边界条件处理

| 场景 | 行为 |
|------|------|
| i_bExtend=TRUE 时已在收回位 | 立即置 q_bIsExtended=TRUE，不启动计时 |
| i_bRetract=TRUE 时已在伸出位 | 立即置 q_bIsRetracted=TRUE，不启动计时 |
| i_bExtend+i_bRetract 同时TRUE | i_bExtend 优先，电磁阀=伸出状态 |
| 运动中命令翻转 | 立即切换方向，重新启动超时计时 |
| i_dTimeoutMs=0 | 关闭超时检测，q_bTimeout 始终 FALSE |
| i_dDebounceMs=0 | 关闭消抖，传感器信号直通 |
| 消抖期间到位信号抖动 | TON确保信号稳定i_dDebounceMs后才生效 |
| 上下位同时ON（消抖后） | q_bSensorFault=TRUE，到位状态保持上次 |
| 使能丢失（编排器侧） | 编排器负责在使能丢失时将 i_bExtend/i_bRetract 都置 FALSE |
| i_bExtendPolarity=TRUE | 传感器互换+电磁阀输出逻辑取反（拍正气缸适用） |

## 7. 变量定义

### 7.1 VAR_INPUT

| 变量 | 类型 | 初始值 | 说明 |
|------|------|:------:|------|
| i_bExtend | BOOL | FALSE | 伸出命令 |
| i_bRetract | BOOL | FALSE | 收回命令 |
| i_bExtendedPos | BOOL | FALSE | 伸出位传感器 |
| i_bRetractedPos | BOOL | FALSE | 收回位传感器 |
| i_dTimeoutMs | DINT | 5000 | 超时(ms), 0=关闭 |
| i_dDebounceMs | DINT | 0 | 消抖(ms), 0=关闭 |
| i_iSolenoidType | INT | 0 | 电磁阀类型(预留) |
| i_bExtendPolarity | BOOL | FALSE | 极性取反 |

### 7.2 VAR_OUTPUT

| 变量 | 类型 | 初始值 | 说明 |
|------|------|:------:|------|
| q_bSolenoid | BOOL | FALSE | 电磁阀输出 |
| q_bIsExtended | BOOL | FALSE | 已伸出到位 |
| q_bIsRetracted | BOOL | FALSE | 已收回到位 |
| q_bTimeout | BOOL | FALSE | 超时报警 |
| q_bSensorFault | BOOL | FALSE | 传感器冲突 |

### 7.3 VAR

| 变量 | 类型 | 初始值 | 说明 |
|------|------|:------:|------|
| fb_tDebounceExt | FB_TON | — | ExtendedPos消抖定时器 |
| fb_tDebounceRet | FB_TON | — | RetractedPos消抖定时器 |
| fb_tTimeout | FB_TONR | — | 超时累积定时器 |
| s_bExtDebounced | BOOL | FALSE | ExtendedPos消抖后信号 |
| s_bRetDebounced | BOOL | FALSE | RetractedPos消抖后信号 |
| s_dExtDebounceEt | DINT | 0 | ExtendedPos消抖ET接收 |
| s_dRetDebounceEt | DINT | 0 | RetractedPos消抖ET接收 |
| s_bLogicExtPos | BOOL | FALSE | 逻辑伸出位(极性映射后) |
| s_bLogicRetPos | BOOL | FALSE | 逻辑收回位(极性映射后) |
| s_bMoving | BOOL | FALSE | 正在执行动作中 |

### 7.4 定时器

| 定时器 | 类型 | PT来源 | 用途 |
|--------|------|--------|------|
| fb_tDebounceExt | TON | i_dDebounceMs (DINT) | 伸出位传感器消抖 |
| fb_tDebounceRet | TON | i_dDebounceMs (DINT) | 收回位传感器消抖 |
| fb_tTimeout | TONR | i_dTimeoutMs (DINT) | 伸出/收回共用，命令切换时自动复位 |

> **TONR 选择理由**: 需要在超时到达后保持 Q=TRUE 直到显式复位（而非自动清零），以便编排器可靠读取。

> **消抖TON选择理由**: 使用TON（延时接通）而非TOF，确保传感器信号稳定持续i_dDebounceMs后才认为有效，过滤短暂的抖动脉冲。

## 8. 极性映射详解

### 8.1 映射规则

当 `i_bExtendPolarity = TRUE` 时，物理传感器与逻辑位置互换：

| 物理信号 | 正常极性(i_bExtendPolarity=FALSE) | 取反极性(i_bExtendPolarity=TRUE) |
|----------|:----------------------------------:|:---------------------------------:|
| s_bExtDebounced | → s_bLogicExtPos | → s_bLogicRetPos |
| s_bRetDebounced | → s_bLogicRetPos | → s_bLogicExtPos |

### 8.2 电磁阀输出映射

| 命令 | 正常极性 q_bSolenoid | 取反极性 q_bSolenoid |
|------|:--------------------:|:--------------------:|
| 伸出 | TRUE | FALSE |
| 收回 | FALSE | TRUE |
| 空闲 | FALSE | TRUE |

### 8.3 设计意图

极性取反适用于"拍正气缸"场景：气缸的物理伸出方向与工艺定义的"伸出"方向相反。通过极性映射层，上层编排器无需关心物理安装方向，始终使用统一的逻辑语义（i_bExtend=伸出），FB内部自动完成物理层与逻辑层的转换。

## 9. 关联文档

| 文档 | 路径 |
|------|------|
| REQ | 需求分析文档_REQ-FB1011-CylinderControl-V8.1.0.md |
| TECH | 技术方案文档_TECH-FB1011-CylinderControl-V8.1.0.md |
| IFC | 接口文档_IFC-FB1011-CylinderControl-V9.0.0.md |
| 电机控制 IFC | ../../../actuator/FB_1012_ConveyorMotor/PRD/接口文档_IFC-FB1012-ConveyorMotor-V7.0.0.md |
| 编排器 DSN | ../../../conveyor/PRD/详细设计说明书_DSN-FB1002-SingleLayerConveyor-V7.0.0.md |
| 规范 LSP-905 | ../../../../../0100_PLC自动化/00_通用规范/PLC编程/905_SCL编程规范_LSP.md |
| 规范 LSP-904 | ../../../../../0100_PLC自动化/00_通用规范/PLC编程/904_SCL注释规范_LSP.md |
| 规范 LSP-903 | ../../../../../0100_PLC自动化/00_通用规范/PLC编程/903_定时器使用规范_LSP.md |
