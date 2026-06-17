---
spec_id: DSN-FB1011
title: "FB_1011 气缸控制详细设计"
version: "V10.0.0"
domain: plc
lifecycle: stable
canonical_path: "0100_PLC自动化/01_SharedLibraries/SysLib/actuator/FB_1011_CylinderControl/PRD/详细设计说明书_DSN.md"
tags: ["气缸控制", "执行器", "PLC功能块", "详细设计", "电磁阀"]
---

# 详细设计说明书 FB_1011_CylinderControl

## 0. 文档基础信息

| 属性 | 值 |
|------|-----|
| **文档标题** | FB_1011 气缸控制详细设计 |
| **文档版本** | V10.0.0 |
| **关联源码** | actuator/FB_1011_CylinderControl/FB_1011_CylinderControl.scl |
| **关联IFC** | 接口文档_INT.md |
| **关联REQ** | 需求分析文档_REQ.md |
| **关联TECH** | 技术方案文档_TEC.md |
| **编制日期** | 2026-06-17 |
| **编制人** | Trae |
| **遵循规范** | LSP-905-V1.0.2, LSP-904-V1.1.0, LSP-903-V2.1.0 |

## 0.1 版本变更摘要（V7.1.0 → V10.0.0）

| 变更项 | V7.1.0 | V9.0.0 | V9.2.0 | V10.0.0 |
|--------|--------|--------|--------|---------|
| 接口方式 | VAR_IN_OUT ST_Cylinder | 扁平 VAR_INPUT / VAR_OUTPUT | ← 同V9.0.0 | ← 同V9.0.0 |
| 变量命名 | io_stCyl.Xxx | i_bXxx / q_bXxx / s_bXxx / fb_tXxx | ← 同V9.0.0 | q_bSolenoid → q_aSolenoid[0..7] |
| 传感器消抖 | 无 | TON消抖（i_dDebounceMs控制） | ← 同V9.0.0 | ← 同V9.0.0 |
| 极性取反 | 仅电磁阀输出取反 | 完整极性映射层（传感器互换+输出取反） | ← 同V9.0.0 | 新增i_bRetractPolarity（双线圈原点方向极性） |
| 信号流水线 | 传感器→故障检测→命令处理 | 物理传感器→TON消抖→故障检测→极性映射→命令处理 | ← 同V9.0.0 | 命令处理从IF/ELSIF改为CASE i_iSolenoidType分支 |
| 规范引用 | 801_DEV, 810_DEV, 904_LSP | LSP-905, LSP-904, LSP-903 | ← 同V9.0.0 | ← 同V9.0.0 |
| 定时器调用方式 | — | 条件内联调用 | 三段式+顶部无条件批量调用（LSP-903 V2.1.0） | ← 同V9.2.0 |
| 消抖关闭时行为 | — | 跳过定时器调用 | 设IN=FALSE让TON自然复位Q=FALSE/ET=0 | ← 同V9.2.0 |
| 超时检测位置 | — | 尾部独立检测 | 移入命令分支内+s_bMoving条件防误报 | ← 同V9.2.0 |
| 电磁阀类型 | — | 仅单线圈两位阀 | ← 同V9.0.0 | 新增双线圈两位阀(i_iSolenoidType=1) |
| 命令处理结构 | — | IF/ELSIF | ← 同V9.0.0 | CASE i_iSolenoidType OF 分支隔离 |
| 双线圈输出 | — | — | — | q_aSolenoid[0]=线圈A(动点), [1]=线圈B(原点) |
| 双线圈互锁 | — | — | — | A/B互斥, 任意时刻最多一个ON |
| 双线圈保持位 | — | — | — | 无命令时保持位(非弹簧复位) |
| 非法类型兜底 | — | — | — | CASE ELSE 安全态(全OFF) |

## 0.2 电磁阀类型说明

| SolenoidType值 | 电磁阀类型 | 线圈数量 | 输出信号 | 默认行为 | 当前支持 |
|-----------|---------|---------|---------|------------------|---------------|
| **0** | **单线圈两位阀** | 1个 | q_aSolenoid[0] | 弹簧复位（收回） | ✅ **支持（默认）** |
| **1** | **双线圈两位阀** | 2个 | q_aSolenoid[0..7] | 失电保持位（双作用） | ✅ **支持** |
| 2 | 3位4通中封阀 | 2个 | q_aSolenoid[0..7] | 保持位置（中封） | ⚠️ 预留扩展 |
| 3 | 3位4通中泄阀 | 2个 | q_aSolenoid[0..7] | 泄压回油（中泄） | ⚠️ 预留扩展 |

### 0.2.1 单线圈两位阀真值表（默认配置, i_iSolenoidType=0）

| i_bExtend | i_bRetract | i_bExtendPolarity | q_aSolenoid[0] | q_aSolenoid[1] | 气缸行为 |
|-----------|------------|-------------------|-----------------|-----------------|---------|
| TRUE      | FALSE      | FALSE             | TRUE            | FALSE           | 伸出    |
| FALSE     | TRUE       | FALSE             | FALSE           | FALSE           | 收回    |
| FALSE     | FALSE      | FALSE             | FALSE           | FALSE           | 弹簧复位 |
| TRUE      | FALSE      | TRUE              | FALSE           | FALSE           | 伸出    |
| FALSE     | TRUE       | TRUE              | TRUE            | FALSE           | 收回    |
| FALSE     | FALSE      | TRUE              | TRUE            | FALSE           | 弹簧复位 |

> **注**: 单线圈模式下 q_aSolenoid[1] 始终为 FALSE，仅 [0] 参与控制。

### 0.2.2 双线圈两位阀真值表（i_iSolenoidType=1）

| i_bExtend | i_bRetract | i_bExtendPolarity | i_bRetractPolarity | q_aSolenoid[0] | q_aSolenoid[1] | 气缸行为 |
|-----------|------------|-------------------|---------------------|-----------------|-----------------|---------|
| TRUE      | FALSE      | FALSE             | FALSE               | TRUE            | FALSE           | 伸出（线圈A驱动） |
| FALSE     | TRUE       | FALSE             | FALSE               | FALSE           | TRUE            | 收回（线圈B驱动） |
| FALSE     | FALSE      | FALSE             | FALSE               | FALSE           | FALSE           | 保持位（失电保持） |
| TRUE      | FALSE      | TRUE              | FALSE               | FALSE           | FALSE           | 伸出（极性取反） |
| FALSE     | TRUE       | TRUE              | FALSE               | TRUE            | FALSE           | 收回（极性取反） |
| FALSE     | FALSE      | TRUE              | FALSE               | FALSE           | FALSE           | 保持位 |
| TRUE      | FALSE      | FALSE             | TRUE                | TRUE            | FALSE           | 伸出 |
| FALSE     | TRUE       | FALSE             | TRUE                | FALSE           | TRUE            | 收回（原点极性取反） |
| FALSE     | FALSE      | FALSE             | TRUE                | FALSE           | FALSE           | 保持位 |

> **互锁规则**: q_aSolenoid[0] 与 q_aSolenoid[1] 任意时刻最多一个为 TRUE，禁止同时 ON。

> **保持位说明**: 双线圈两位阀为双作用气缸，无弹簧复位，断电时气缸保持在当前位置（保持位）。无命令时两个线圈均 OFF，气缸不动作。

## 1. 设计原则

1. **命令驱动**: 气缸只响应伸出/收回命令，不自行决定何时动作
2. **输出保持**: 无新命令时保持电磁阀状态为弹簧复位（单线圈两位阀安全特性）
3. **超时隔离**: 超时仅报警不强制复位，编排器决定后续策略
4. **传感器故障实时诊断**: 上下位冲突检测为纯组合逻辑，无延时
5. **传感器消抖**: 物理传感器信号经TON定时器消抖后参与逻辑判断，消除抖动误触发
6. **极性映射完整**: 极性取反不仅翻转电磁阀输出，同时互换逻辑传感器映射，确保逻辑层与物理层一致
7. **可复用**: 同一FB可实例化为阻挡气缸、分料气缸或任何二位置气动执行器
8. **通用性**: 支持多种电磁阀类型配置，支持线圈极性取反
9. **定时器规范调用**: 所有定时器实例每周期无条件调用(), 业务逻辑只设参数只读输出, 遵循LSP-903 V2.1.0 §3.4
10. **CASE分支按类型隔离**: 命令处理按 i_iSolenoidType 使用 CASE 分支隔离，不同电磁阀类型的逻辑互不干扰，CASE ELSE 提供安全兜底

## 2. 信号处理流水线

V9.0.0 引入五级信号处理流水线，V10.0.0 将命令处理升级为 CASE 分支，确保传感器信号可靠、逻辑一致：

```
物理传感器          TON消抖           传感器故障检测        极性映射              命令处理(CASE分支)
─────────  ──→  ──────────  ──→  ──────────────  ──→  ──────────  ──→  ──────────────────
i_bExtendedPos      fb_tDebounceExt    s_bExtDebounced     s_bLogicExtPos       CASE i_iSolenoidType
i_bRetractedPos     fb_tDebounceRet    s_bRetDebounced     s_bLogicRetPos         0: 单线圈逻辑
                                       ↓                   ↓                      1: 双线圈逻辑(A/B互锁)
                                    q_bSensorFault      (极性互换)               ELSE: 安全态(全OFF)
                                                                              q_aSolenoid[0..7]
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
| 5 | 命令处理 | i_bExtend, i_bRetract, s_bLogicExtPos, s_bLogicRetPos, i_iSolenoidType, i_bExtendPolarity, i_bRetractPolarity | q_aSolenoid[0..7], q_bIsExtended, q_bIsRetracted, q_bTimeout | CASE i_iSolenoidType分支: 0=单线圈, 1=双线圈(A/B互锁), ELSE=安全态 |

## 3. 状态定义

本FB不维护业务流程状态，仅跟踪物理状态：

### 3.1 单线圈两位阀（i_iSolenoidType=0）

| 物理状态 | 条件 | 电磁阀输出 |
|----------|------|:---------:|
| 收回位置 | s_bLogicRetPos=TRUE, s_bLogicExtPos=FALSE | 弹簧复位状态 |
| 伸出位置 | s_bLogicExtPos=TRUE, s_bLogicRetPos=FALSE | 伸出状态 |
| 运动中(伸出) | 两逻辑传感器都FALSE, 命令=i_bExtend | 伸出状态 |
| 运动中(收回) | 两逻辑传感器都FALSE, 命令=i_bRetract | 收回状态 |
| 传感器故障 | s_bExtDebounced=TRUE AND s_bRetDebounced=TRUE | 保持上次 |

### 3.2 双线圈两位阀（i_iSolenoidType=1）

| 物理状态 | 条件 | 电磁阀输出 q_aSolenoid[0..7] |
|----------|------|:---------------------------:|
| 收回位置 | s_bLogicRetPos=TRUE, s_bLogicExtPos=FALSE | [0]=OFF, [1]=OFF（保持位） |
| 伸出位置 | s_bLogicExtPos=TRUE, s_bLogicRetPos=FALSE | [0]=OFF, [1]=OFF（保持位） |
| 运动中(伸出) | 两逻辑传感器都FALSE, 命令=i_bExtend | [0]=ON, [1]=OFF（线圈A驱动） |
| 运动中(收回) | 两逻辑传感器都FALSE, 命令=i_bRetract | [0]=OFF, [1]=ON（线圈B驱动） |
| 双线圈保持位 | 两逻辑传感器都FALSE, 无命令 | [0]=OFF, [1]=OFF（失电保持） |
| 传感器故障 | s_bExtDebounced=TRUE AND s_bRetDebounced=TRUE | [0]=OFF, [1]=OFF（安全态） |

> **保持位说明**: 双线圈两位阀无弹簧复位，失电时气缸保持在当前位置。到位后两个线圈均 OFF，气缸靠气路保持位置。

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
    fb_tDebounceExt.IN := FALSE;
    fb_tDebounceRet.IN := FALSE;
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

(* ==================== 第5级: 命令处理（CASE i_iSolenoidType 分支隔离）==================== *)

CASE i_iSolenoidType OF

(* ===== 0: 单线圈两位阀 ===== *)
0:
    (* 命令优先级: Extend > Retract *)
    IF i_bExtend THEN
        (* ---- 伸出命令 ---- *)
        IF i_bExtendPolarity THEN
            q_aSolenoid[0] := FALSE;
        ELSE
            q_aSolenoid[0] := TRUE;
        END_IF;
        q_aSolenoid[1] := FALSE;  (* 单线圈: [1]始终FALSE *)

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
        IF fb_tTimeout.Q AND s_bMoving THEN
            q_bTimeout := TRUE;
        END_IF;

    ELSIF i_bRetract THEN
        (* ---- 收回命令 ---- *)
        IF i_bExtendPolarity THEN
            q_aSolenoid[0] := TRUE;
        ELSE
            q_aSolenoid[0] := FALSE;
        END_IF;
        q_aSolenoid[1] := FALSE;  (* 单线圈: [1]始终FALSE *)

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
        IF fb_tTimeout.Q AND s_bMoving THEN
            q_bTimeout := TRUE;
        END_IF;

    ELSE
        (* ---- 无命令：空闲（弹簧复位） ---- *)
        IF i_bExtendPolarity THEN
            q_aSolenoid[0] := TRUE;
        ELSE
            q_aSolenoid[0] := FALSE;
        END_IF;
        q_aSolenoid[1] := FALSE;  (* 单线圈: [1]始终FALSE *)

        s_bMoving := FALSE;
        q_bTimeout := FALSE;
        fb_tTimeout.IN := FALSE;
        fb_tTimeout.R := TRUE;

        q_bIsExtended := s_bLogicExtPos;
        q_bIsRetracted := s_bLogicRetPos;
    END_IF;

(* ===== 1: 双线圈两位阀 ===== *)
1:
    (* 命令优先级: Extend > Retract *)
    IF i_bExtend THEN
        (* ---- 伸出命令（线圈A驱动） ---- *)
        IF i_bExtendPolarity THEN
            q_aSolenoid[0] := FALSE;  (* 动点方向极性取反 *)
        ELSE
            q_aSolenoid[0] := TRUE;   (* 线圈A ON *)
        END_IF;
        q_aSolenoid[1] := FALSE;      (* 互锁: 线圈B OFF *)

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
            q_aSolenoid[0] := FALSE;  (* 到位后线圈A OFF, 保持位 *)
            q_aSolenoid[1] := FALSE;
            q_bIsExtended := TRUE;
            q_bIsRetracted := FALSE;
            s_bMoving := FALSE;
            q_bTimeout := FALSE;
            fb_tTimeout.IN := FALSE;
            fb_tTimeout.R := TRUE;
        END_IF;

        (* 超时检测 *)
        IF fb_tTimeout.Q AND s_bMoving THEN
            q_bTimeout := TRUE;
        END_IF;

    ELSIF i_bRetract THEN
        (* ---- 收回命令（线圈B驱动） ---- *)
        q_aSolenoid[0] := FALSE;      (* 互锁: 线圈A OFF *)
        IF i_bRetractPolarity THEN
            q_aSolenoid[1] := FALSE;   (* 原点方向极性取反 *)
        ELSE
            q_aSolenoid[1] := TRUE;    (* 线圈B ON *)
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
            q_aSolenoid[0] := FALSE;  (* 到位后线圈B OFF, 保持位 *)
            q_aSolenoid[1] := FALSE;
            q_bIsRetracted := TRUE;
            q_bIsExtended := FALSE;
            s_bMoving := FALSE;
            q_bTimeout := FALSE;
            fb_tTimeout.IN := FALSE;
            fb_tTimeout.R := TRUE;
        END_IF;

        (* 超时检测 *)
        IF fb_tTimeout.Q AND s_bMoving THEN
            q_bTimeout := TRUE;
        END_IF;

    ELSE
        (* ---- 无命令：保持位（双线圈失电保持，非弹簧复位） ---- *)
        q_aSolenoid[0] := FALSE;  (* 线圈A OFF *)
        q_aSolenoid[1] := FALSE;  (* 线圈B OFF, 气缸保持当前位置 *)

        s_bMoving := FALSE;
        q_bTimeout := FALSE;
        fb_tTimeout.IN := FALSE;
        fb_tTimeout.R := TRUE;

        q_bIsExtended := s_bLogicExtPos;
        q_bIsRetracted := s_bLogicRetPos;
    END_IF;

(* ===== ELSE: 非法类型安全兜底 ===== *)
ELSE
    q_aSolenoid[0] := FALSE;  (* 全OFF安全态 *)
    q_aSolenoid[1] := FALSE;
    q_bIsExtended := FALSE;
    q_bIsRetracted := FALSE;
    q_bTimeout := FALSE;
    s_bMoving := FALSE;
    fb_tTimeout.IN := FALSE;
    fb_tTimeout.R := TRUE;

END_CASE;
```

## 5. 时序图

### 5.1 正常伸出→收回周期（单线圈两位阀, i_iSolenoidType=0）

```
i_bExtend         ──────┐                     ┌──────
                         └─────────────────────┘
i_bRetract        ─────────────────┐          ┌──────
                                  └──────────┘
q_aSolenoid[0]    ──────┐                     │
                       └─────────────────────┘
q_aSolenoid[1]    ──────────────────────────────────── (始终FALSE)
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

### 5.2 超时场景（单线圈两位阀）

```
i_bExtend         ──────┐
                         └────────────────────────── ...
q_aSolenoid[0]    ──────┐
                         └────────────────────────── ...
q_aSolenoid[1]    ─────────────────────────────────── ... (始终FALSE)
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

### 5.4 极性取反时序（i_bExtendPolarity=TRUE, 单线圈两位阀）

```
i_bExtendedPos    ─────────┐          ┌────────────────
                            └──────────┘
i_bRetractedPos   ──────┐                     ┌──────
                         └─────────────────────┘
s_bLogicExtPos    ──────┐                     ┌──────  (←映射自RetDebounced)
                         └─────────────────────┘
s_bLogicRetPos    ─────────┐          ┌────────────────  (←映射自ExtDebounced)
                            └──────────┘
q_aSolenoid[0]    ──────┐                     │  (伸出=FALSE, 收回=TRUE)
                       └─────────────────────┘
q_aSolenoid[1]    ──────────────────────────────────── (始终FALSE)
```

### 5.5 双线圈两位阀正常伸出→收回周期（i_iSolenoidType=1）

```
i_bExtend         ──────┐                     ┌──────
                         └─────────────────────┘
i_bRetract        ─────────────────┐          ┌──────
                                  └──────────┘
q_aSolenoid[0]    ──────┐                     │  (线圈A: 伸出ON, 收回OFF)
                       └─────────────────────┘
q_aSolenoid[1]    ─────────────────┐          │  (线圈B: 收回ON, 伸出OFF)
                                  └──────────┘
i_bExtendedPos    ─────────┐          ┌────────────────
                            └──────────┘
i_bRetractedPos   ──────┐                     ┌──────
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

> **双线圈时序要点**: 到位后 q_aSolenoid[0] 和 q_aSolenoid[1] 均 OFF，气缸靠气路保持位。A/B 互锁，任意时刻最多一个 ON。

### 5.6 双线圈两位阀超时场景（i_iSolenoidType=1）

```
i_bExtend         ──────┐
                         └────────────────────────── ...
q_aSolenoid[0]    ──────┐
                         └────────────────────────── ... (线圈A持续ON)
q_aSolenoid[1]    ─────────────────────────────────── ... (互锁: 始终OFF)
i_bExtendedPos    ─────────────────────────────────── ... (始终未到位)
fb_tTimeout.Q     ──────────────────┐
                                   └────────────── ... (超时到达)
q_bTimeout        ──────────────────┐
                                   └────────────── ... (锁存, 线圈A仍ON等待编排器决策)
```

> **超时后行为**: 双线圈模式下超时仅报警不强制复位，线圈A保持 ON 直到编排器撤销 i_bExtend 命令。编排器负责决定后续策略（重试/报警/切换方向）。

## 6. 边界条件处理

| 场景 | 行为 |
|------|------|
| i_bExtend=TRUE 时已在收回位 | 立即置 q_bIsExtended=TRUE，不启动计时 |
| i_bRetract=TRUE 时已在伸出位 | 立即置 q_bIsRetracted=TRUE，不启动计时 |
| i_bExtend+i_bRetract 同时TRUE | i_bExtend 优先，电磁阀=伸出状态 |
| 运动中命令翻转 | 立即切换方向，重新启动超时计时 |
| i_dTimeoutMs=0 | 关闭超时检测，q_bTimeout 始终 FALSE |
| i_dDebounceMs=0 | 关闭消抖，传感器信号直通 |
| 消抖关闭时TON自然复位 | i_dDebounceMs=0时设IN=FALSE, TON的Q=FALSE/ET=0, 不会残留僵尸值 |
| 消抖期间到位信号抖动 | TON确保信号稳定i_dDebounceMs后才生效 |
| 上下位同时ON（消抖后） | q_bSensorFault=TRUE，到位状态保持上次 |
| 使能丢失（编排器侧） | 编排器负责在使能丢失时将 i_bExtend/i_bRetract 都置 FALSE |
| i_bExtendPolarity=TRUE | 传感器互换+电磁阀输出逻辑取反（拍正气缸适用） |
| 双线圈无命令 | 两个线圈均OFF，气缸保持当前位置（失电保持位） |
| 双线圈到位后 | 驱动线圈OFF，气缸靠气路保持位，q_bIsExtended/q_bIsRetracted 反映到位状态 |
| 双线圈A/B互锁 | 任意时刻 q_aSolenoid[0] 与 q_aSolenoid[1] 最多一个ON，禁止同时ON |
| i_bRetractPolarity=TRUE | 双线圈原点方向（线圈B）极性取反，收回时 q_aSolenoid[1]=FALSE |
| i_iSolenoidType 为非法值 | CASE ELSE 安全兜底：q_aSolenoid 全OFF，所有输出复位 |
| 双线圈超时 | 仅报警不强制复位，驱动线圈保持ON直到编排器撤销命令 |

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
| i_iSolenoidType | INT | 0 | 电磁阀类型: 0=单线圈两位阀, 1=双线圈两位阀 |
| i_bExtendPolarity | BOOL | FALSE | 动点方向（伸出）极性取反 |
| i_bRetractPolarity | BOOL | FALSE | 原点方向（收回）极性取反（仅双线圈有效） |

### 7.2 VAR_OUTPUT

| 变量 | 类型 | 初始值 | 说明 |
|------|------|:------:|------|
| q_aSolenoid | ARRAY[0..7] OF BOOL | [FALSE,FALSE] | 电磁阀输出: [0]=线圈A(动点方向), [1]=线圈B(原点方向) |
| q_bIsExtended | BOOL | FALSE | 已伸出到位 |
| q_bIsRetracted | BOOL | FALSE | 已收回到位 |
| q_bTimeout | BOOL | FALSE | 超时报警 |
| q_bSensorFault | BOOL | FALSE | 传感器冲突 |

> **q_aSolenoid 数组说明**:
> - 单线圈模式(i_iSolenoidType=0): 只使用 [0]，[1] 始终 FALSE
> - 双线圈模式(i_iSolenoidType=1): [0]=线圈A(动点方向), [1]=线圈B(原点方向)，A/B互锁
> - **Breaking Change**: V9.2.0 的 `q_bSolenoid`(BOOL) 已替换为 `q_aSolenoid`(ARRAY[0..7] OF BOOL)

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

### 8.1 传感器极性映射（单线圈/双线圈通用）

当 `i_bExtendPolarity = TRUE` 时，物理传感器与逻辑位置互换：

| 物理信号 | 正常极性(i_bExtendPolarity=FALSE) | 取反极性(i_bExtendPolarity=TRUE) |
|----------|:----------------------------------:|:---------------------------------:|
| s_bExtDebounced | → s_bLogicExtPos | → s_bLogicRetPos |
| s_bRetDebounced | → s_bLogicRetPos | → s_bLogicExtPos |

### 8.2 单线圈电磁阀输出映射（i_iSolenoidType=0）

| 命令 | 正常极性 q_aSolenoid[0] | 取反极性 q_aSolenoid[0] | q_aSolenoid[1] |
|------|:--------------------:|:--------------------:|:--------------:|
| 伸出 | TRUE | FALSE | FALSE |
| 收回 | FALSE | TRUE | FALSE |
| 空闲 | FALSE | TRUE | FALSE |

### 8.3 双线圈电磁阀输出映射（i_iSolenoidType=1）

双线圈模式下，线圈A（动点方向）和线圈B（原点方向）各自独立极性映射：

| 命令 | i_bExtendPolarity | i_bRetractPolarity | q_aSolenoid[0] (线圈A) | q_aSolenoid[1] (线圈B) |
|------|:-----------------:|:------------------:|:----------------------:|:----------------------:|
| 伸出 | FALSE | — | TRUE | FALSE |
| 伸出 | TRUE | — | FALSE | FALSE |
| 收回 | — | FALSE | FALSE | TRUE |
| 收回 | — | TRUE | FALSE | FALSE |
| 无命令 | — | — | FALSE | FALSE |

> **双线圈极性映射规则**:
> - **线圈A（动点方向）**: 受 `i_bExtendPolarity` 控制，伸出时生效
> - **线圈B（原点方向）**: 受 `i_bRetractPolarity` 控制，收回时生效
> - 两个极性参数独立控制，允许仅取反其中一个方向
> - 极性取反时对应线圈 OFF（而非驱动对侧线圈），保持互锁安全

### 8.4 设计意图

极性取反适用于"拍正气缸"场景：气缸的物理伸出方向与工艺定义的"伸出"方向相反。通过极性映射层，上层编排器无需关心物理安装方向，始终使用统一的逻辑语义（i_bExtend=伸出），FB内部自动完成物理层与逻辑层的转换。

双线圈新增 `i_bRetractPolarity` 是因为双线圈两位阀的两个线圈物理安装可能独立反向，需要分别控制极性映射。单线圈模式下 `i_bRetractPolarity` 无效（收回靠弹簧复位）。

## 9. 版本详细变更说明

### V10.0.0（Breaking Change: 双线圈两位阀扩展）

**变更类型**: feat(FB_1011_CylinderControl) — Breaking Change

**变更内容**:

1. **输出接口变更（Breaking Change）**: `q_bSolenoid`(BOOL) → `q_aSolenoid`(ARRAY[0..7] OF BOOL)
   - [0] = 线圈A（动点方向/伸出方向）
   - [1] = 线圈B（原点方向/收回方向）
   - 单线圈模式: 只使用 [0]，[1] 始终 FALSE
   - 双线圈模式: [0]/[1] 互斥，任意时刻最多一个 ON

2. **新增双线圈两位阀支持**（i_iSolenoidType=1）:
   - 双作用气缸，失电保持位（非弹簧复位）
   - 线圈A/B 互锁，禁止同时 ON
   - 到位后两个线圈均 OFF，气缸靠气路保持位置
   - 无命令时保持位（两个线圈均 OFF）

3. **新增参数**: `i_bRetractPolarity`(BOOL) — 双线圈原点方向极性取反
   - 仅双线圈模式有效
   - 与 `i_bExtendPolarity` 独立控制
   - 单线圈模式下无效（收回靠弹簧复位）

4. **命令处理结构重构**: IF/ELSIF → CASE i_iSolenoidType OF
   - 0: 单线圈逻辑（保持 V9.2.0 行为不变）
   - 1: 双线圈逻辑（A/B互锁, 保持位, 独立极性）
   - ELSE: 非法类型安全兜底（全OFF）

5. **新增设计原则**: 第10条"CASE分支按类型隔离"

6. **新增时序图**: 5.5 双线圈正常周期、5.6 双线圈超时场景

**向后兼容性**:
- ❌ `q_bSolenoid` 接口变更，调用方需适配为 `q_aSolenoid[0]`
- ✅ 单线圈逻辑行为完全不变（仅输出变量名变更）
- ✅ 新增参数 `i_bRetractPolarity` 默认 FALSE，不影响现有实例

## 10. 关联文档

| 文档 | 路径 |
|------|------|
| REQ | 需求分析文档_REQ.md |
| TECH | 技术方案文档_TEC.md |
| IFC | 接口文档_INT.md |
| 电机控制 IFC | ../../../actuator/FB_1012_ConveyorMotor/PRD/接口文档_IFC-FB1012-ConveyorMotor-V7.0.0.md |
| 编排器 DSN | ../../../conveyor/PRD/详细设计说明书_DSN-FB1002-SingleLayerConveyor-V7.0.0.md |
| 规范 LSP-905 | ../../../../../0100_PLC自动化/00_通用规范/PLC编程/905_SCL编程规范_LSP.md |
| 规范 LSP-904 | ../../../../../0100_PLC自动化/00_通用规范/PLC编程/904_SCL注释规范_LSP.md |
| 规范 LSP-903 | ../../../../../0100_PLC自动化/00_通用规范/PLC编程/903_定时器使用规范_LSP.md |
