---
spec_id: INT-FB1011
title: "FB_1011 气缸控制接口定义"
version: "V10.0.0"
domain: plc
lifecycle: stable
canonical_path: "0100_PLC自动化/01_SharedLibraries/SysLib/actuator/FB_1011_CylinderControl/PRD/接口文档_INT.md"
tags: ["气缸控制", "执行器", "PLC功能块", "接口", "电磁阀"]
---
# 接口文档 FB_1011_CylinderControl

## 0. 文档基础信息

| 属性         | 值                                                                                       |
| ------------ | ---------------------------------------------------------------------------------------- |
| **文档标题** | FB_1011 气缸控制接口定义                                                                 |
| **文档版本** | V10.0.0                                                                                  |
| **关联源码** | actuator/FB_1011_CylinderControl/FB_1011_CylinderControl.scl                             |
| **编制日期** | 2026-06-17                                                                               |
| **编制人**   | Trae                                                                                     |
| **审核人**   | 人工                                                                                     |
| **遵循规范** | LSP-905-V1.0.2, LSP-904-V1.1.0, LSP-903-V2.1.0                                          |
| **变更记录** | V10.0.0: Breaking Change-新增双线圈两位阀支持(i_iSolenoidType=1); q_bSolenoid→q_aSolenoid[0..7] ARRAY输出; 新增i_bRetractPolarity参数; 命令处理从IF/ELSIF改为CASE i_iSolenoidType分支; 双线圈A/B互锁+无命令保持位+ELSE安全态 |
| **变更记录** | V9.2.0: P0定时器修复-三段式+顶部无条件批量调用; 消抖关闭时设IN=FALSE让TON自然复位; 超时检测移入命令分支内加s_bMoving防误报; 移除尾部独立fb_tTimeout()调用 |

## 0.1 电磁阀类型定义

| SolenoidType值 | 电磁阀类型     | 线圈数量 | 输出信号                              | 默认行为         | 当前支持       |
| -------------- | -------------- | -------- | ------------------------------------- | ---------------- | -------------- |
| **0**          | **单线圈两位阀** | 1个      | q_aSolenoid[0]                        | 弹簧复位(收回)   | 支持(默认)     |
| **1**          | **双线圈两位阀** | 2个      | q_aSolenoid[0..7]                     | 保持最后位置(失电保持位) | 支持     |
| 2              | 3位4通中封阀   | 2个      | q_aSolenoid[0..7]                     | 保持位置(中封)   | 预留扩展       |
| 3              | 3位4通中泄阀   | 2个      | q_aSolenoid[0..7]                     | 泄压回油(中泄)   | 预留扩展       |

> **双线圈两位阀说明**: SolenoidType=1为双作用气缸配置, 使用两个电磁线圈分别控制伸出(A线圈, q_aSolenoid[0])和收回(B线圈, q_aSolenoid[1]). 失电时气缸保持当前位置(非弹簧复位), A/B线圈互斥(任意时刻最多一个ON), 无命令时两个线圈均OFF(保持位). 需配合i_bRetractPolarity参数控制B线圈极性.

### 0.1.1 单线圈两位阀真值表(默认配置)

| i_bExtend | i_bRetract | i_bExtendPolarity | q_aSolenoid[0] | q_aSolenoid[1] | 气缸行为 |
| --------- | ---------- | ----------------- | --------------- | --------------- | -------- |
| TRUE      | FALSE      | FALSE             | TRUE            | FALSE           | 伸出     |
| FALSE     | TRUE       | FALSE             | FALSE           | FALSE           | 收回     |
| FALSE     | FALSE      | FALSE             | FALSE           | FALSE           | 弹簧复位 |
| TRUE      | FALSE      | TRUE              | FALSE           | FALSE           | 伸出     |
| FALSE     | TRUE       | TRUE              | TRUE            | FALSE           | 收回     |
| FALSE     | FALSE      | TRUE              | TRUE            | FALSE           | 弹簧复位 |

### 0.1.2 线圈极性取反说明

| i_bExtendPolarity | 说明     | q_aSolenoid[0]=TRUE | q_aSolenoid[0]=FALSE | 传感器映射                              | 适用场景                |
| ----------------- | -------- | ------------------- | -------------------- | --------------------------------------- | ----------------------- |
| FALSE (默认)      | 正常极性 | 伸出                | 收回                 | ExtendedPos->伸出位, RetractedPos->收回位 | 阻挡/夹紧等气缸         |
| TRUE              | 极性取反 | 收回                | 伸出                 | ExtendedPos->收回位, RetractedPos->伸出位 | 拍正/顶升等弹簧复位气缸 |

> **极性取反完整行为**: 当 i_bExtendPolarity=TRUE 时, 不仅电磁阀输出反转, 传感器映射也互换(物理伸出位视为逻辑收回位, 物理收回位视为逻辑伸出位), 状态输出 q_bIsExtended/q_bIsRetracted 随之反转.

### 0.1.3 双线圈两位阀真值表(i_iSolenoidType=1)

> 双线圈两位阀使用A/B两个线圈互斥控制, q_aSolenoid[0]=线圈A(动点方向), q_aSolenoid[1]=线圈B(原点方向). 任意时刻最多一个线圈ON, 无命令时两个线圈均OFF(气缸保持位).

| i_bExtend | i_bRetract | i_bExtendPolarity | i_bRetractPolarity | q_aSolenoid[0] | q_aSolenoid[1] | 气缸行为     |
| --------- | ---------- | ----------------- | ------------------- | -------------- | -------------- | ------------ |
| TRUE      | FALSE      | FALSE             | FALSE               | TRUE           | FALSE          | A线圈驱动伸出 |
| TRUE      | FALSE      | TRUE              | FALSE               | FALSE          | FALSE          | A线圈极性取反驱动伸出 |
| FALSE     | TRUE       | FALSE             | FALSE               | FALSE          | TRUE           | B线圈驱动收回 |
| FALSE     | TRUE       | FALSE             | TRUE                | FALSE          | FALSE          | B线圈极性取反驱动收回 |
| TRUE      | TRUE       | -                 | -                   | TRUE           | FALSE          | 伸出优先(A线圈ON) |
| FALSE     | FALSE      | -                 | -                   | FALSE          | FALSE          | 保持位(双线圈均OFF) |

> **i_bRetractPolarity说明**: 当i_bRetractPolarity=TRUE时, B线圈(原点方向)极性取反, 即收回命令不再驱动B线圈, 而是驱动A线圈. 此参数仅对双线圈模式(i_iSolenoidType=1)有效, 单线圈模式忽略.

## 1. 功能概述

**单一气缸执行控制块**, 封装 推力/拉力命令 -> 传感器消抖 -> 极性映射 -> 电磁阀输出 -> 到位检测 -> 超时保护 -> 传感器冗余一致性检查 的完整闭环.

支持多种电磁阀类型配置(单线圈两位阀/双线圈两位阀), 支持线圈极性取反(含传感器映射反转), 支持磁环传感器TON消抖.

适用于输送机系统中任何需要伸出/收回动作的气动执行器(阻挡气缸, 分料气缸, 双作用顶升气缸等).

### 1.1 职责边界

| 做什么                               | 不做什么                             |
| ------------------------------------ | ------------------------------------ |
| 接收伸出/收回命令                    | 不关心什么时候该伸出(由编排器决定)   |
| 输出电磁阀信号(支持多种类型配置)     | 不直接操作物理IO(由OB1映射)          |
| 磁环传感器TON消抖                    | 不关心传感器的物理地址               |
| 极性映射(传感器+输出反转)            | 不参与其他气缸的逻辑                 |
| 上下位同时ON冲突诊断                 | 不处理非本气缸的报警                 |
| 动作超时计时与报警                   | 不处理多气缸协调                     |

### 1.2 实例化场景

| 场景         | 实例名               | 配置                                      | 说明                                              |
| ------------ | -------------------- | ----------------------------------------- | ------------------------------------------------- |
| 阻挡气缸     | fbBlock : FB_1011    | i_iSolenoidType=0, i_bExtendPolarity=FALSE | i_bExtend=阻挡下降, i_bRetract=阻挡上升           |
| 分料气缸     | fbSeparate : FB_1011 | i_iSolenoidType=0, i_bExtendPolarity=FALSE | i_bExtend=分料推出, i_bRetract=分料复位           |
| 拍正气缸     | fbAlign : FB_1011    | i_iSolenoidType=0, i_bExtendPolarity=TRUE  | i_bExtend=拍正伸出, i_bRetract=拍正收回(极性取反) |
| 双作用顶升气缸 | fbLift : FB_1011   | i_iSolenoidType=1, i_bExtendPolarity=FALSE, i_bRetractPolarity=FALSE | 双线圈A/B互锁, 失电保持位, i_bExtend=A线圈伸出, i_bRetract=B线圈收回 |
| 双作用夹紧气缸 | fbClamp : FB_1011  | i_iSolenoidType=1, i_bExtendPolarity=FALSE, i_bRetractPolarity=TRUE | 双线圈B极性取反, i_bExtend=A线圈夹紧, i_bRetract=B线圈极性取反松开 |

## 2. 接口定义

### 2.1 VAR_INPUT

| 名称               | 类型 | 默认值 | 有效值域    | 说明                                                              | 来源           |
| ------------------ | ---- | ------ | ----------- | ----------------------------------------------------------------- | -------------- |
| i_bExtend          | BOOL | -      | TRUE/FALSE  | 伸出命令 (推/降/夹紧)                                            | 编排器         |
| i_bRetract         | BOOL | -      | TRUE/FALSE  | 收回命令 (拉/升/松开)                                            | 编排器         |
| i_bExtendedPos     | BOOL | -      | TRUE/FALSE  | 伸出位传感器 (下位/降位/夹紧位/工作点)                           | OB1->IO映射    |
| i_bRetractedPos    | BOOL | -      | TRUE/FALSE  | 收回位传感器 (上位/升位/松开位/原点)                             | OB1->IO映射    |
| i_dTimeoutMs       | DINT | 5000   | 0~60000     | 动作超时时间(ms), 0=关闭超时检测                                 | 编排器         |
| i_dDebounceMs      | DINT | 0      | 0~1000      | 传感器消抖时间(扫描周期), 0=关闭消抖(设IN=FALSE让TON自然复位), >0=TON确认稳定后输出 | 编排器         |
| i_iSolenoidType    | INT  | 0      | 0~3         | 电磁阀类型: 0=单线圈两位阀(默认), 1=双线圈两位阀(双作用,失电保持位), 2=3位4通中封阀, 3=3位4通中泄阀 (预留) | 编排器 |
| i_bExtendPolarity  | BOOL | FALSE  | TRUE/FALSE  | 线圈A极性取反: FALSE=正常, TRUE=取反(电磁阀+传感器映射均反转)     | 编排器         |
| i_bRetractPolarity | BOOL | FALSE  | TRUE/FALSE  | 线圈B极性取反(仅双线圈模式有效): FALSE=正常, TRUE=取反(原点方向线圈极性反转); 单线圈模式忽略 | 编排器         |

> **命令优先级**: 当 i_bExtend 和 i_bRetract 同时为 TRUE 时, i_bExtend(伸出)优先.

### 2.2 VAR_OUTPUT

| 名称            | 类型                | 默认值      | 有效值域         | 说明                            | 去向           |
| --------------- | ------------------- | ----------- | ---------------- | ------------------------------- | -------------- |
| q_aSolenoid     | ARRAY[0..7] OF BOOL | [FALSE,FALSE] | TRUE/FALSE    | 电磁阀输出: [0]=线圈A(动点方向), [1]=线圈B(原点方向); 单线圈只用[0], [1]始终FALSE; 双线圈[0]/[1]互斥 | OB1->IO映射 |
| q_bIsExtended   | BOOL                | FALSE       | TRUE/FALSE       | 已伸出到位 (极性映射后)         | 编排器         |
| q_bIsRetracted  | BOOL                | FALSE       | TRUE/FALSE       | 已收回到位 (极性映射后)         | 编排器         |
| q_bTimeout      | BOOL                | FALSE       | TRUE/FALSE       | 动作超时 (伸出或收回未在时间内到位) | 编排器->报警 |
| q_bSensorFault  | BOOL                | FALSE       | TRUE/FALSE       | 传感器冗余故障 (上下位同时ON, 消抖后检测) | 编排器->报警 |

### 2.3 VAR (内部变量)

| 名称              | 类型    | 默认值 | 说明                              |
| ----------------- | ------- | ------ | --------------------------------- |
| fb_tDebounceExt   | FB_TON  | -      | ExtendedPos消抖定时器             |
| fb_tDebounceRet   | FB_TON  | -      | RetractedPos消抖定时器            |
| fb_tTimeout       | FB_TONR | -      | 超时定时器                        |
| s_bExtDebounced   | BOOL    | FALSE  | ExtendedPos消抖后信号             |
| s_bRetDebounced   | BOOL    | FALSE  | RetractedPos消抖后信号            |
| s_dExtDebounceEt  | DINT    | 0      | ExtendedPos消抖ET接收             |
| s_dRetDebounceEt  | DINT    | 0      | RetractedPos消抖ET接收            |
| s_bLogicExtPos    | BOOL    | FALSE  | 逻辑伸出位 (极性映射后)           |
| s_bLogicRetPos    | BOOL    | FALSE  | 逻辑收回位/原点方向逻辑位 (极性映射后, 双线圈模式用于B线圈极性映射) |
| s_bMoving         | BOOL    | FALSE  | 正在执行动作中                    |

## 3. 信号处理流水线

> **定时器批量调用区**: 遵循LSP-903 V2.1.0三段式规范, 所有定时器(fb_tDebounceExt, fb_tDebounceRet, fb_tTimeout)在代码顶部无条件批量调用, 不在条件分支内联调用. 消抖定时器通过IN引脚控制启停, 超时定时器通过IN/R引脚控制启停/复位.

```
物理传感器       TON消抖           传感器故障检测       极性映射            命令处理(CASE)
i_bExtendedPos ─→ fb_tDebounceExt ─→ s_bExtDebounced ─┬─→ SensorFault  ─→ s_bLogicExtPos ─→ CASE i_iSolenoidType
i_bRetractedPos ─→ fb_tDebounceRet ─→ s_bRetDebounced ─┤                  ─→ s_bLogicRetPos ─→   0: 单线圈 → q_aSolenoid[0]
                                                         │                                       1: 双线圈 → q_aSolenoid[0..7]互锁
i_dDebounceMs ──→ PT参数(0=直通)                        └─→ i_bExtendPolarity                   ELSE: 安全态(全OFF)
                                                              FALSE: 正常映射
                                                              TRUE:  互换映射
```

## 4. 行为逻辑

### 4.1 命令处理(CASE i_iSolenoidType分支)

```
CASE i_iSolenoidType OF
    0:  // 单线圈两位阀 (见4.2~4.6)
        q_aSolenoid[1] := FALSE;  // 单线圈[1]始终FALSE
        // 命令处理逻辑见4.4

    1:  // 双线圈两位阀 (见4.7)
        // A/B互锁, 无命令保持位, ELSE全OFF

ELSE
    // 非法类型兜底: 安全态
    q_aSolenoid[0] := FALSE;
    q_aSolenoid[1] := FALSE;
END_CASE;
```

### 4.2 传感器消抖

```
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
    // 消抖关闭: 设IN=FALSE让TON自然复位Q=FALSE/ET=0, 信号直通
    fb_tDebounceExt.IN := FALSE;
    fb_tDebounceRet.IN := FALSE;
    s_bExtDebounced := i_bExtendedPos;
    s_bRetDebounced := i_bRetractedPos;
END_IF;
```

### 4.3 传感器冗余一致性检查(消抖后, 极性映射前)

```
IF s_bExtDebounced AND s_bRetDebounced THEN
    q_bSensorFault := TRUE;   (* 上下位同时ON, 物理上不可能 *)
ELSE
    q_bSensorFault := FALSE;
END_IF;
```

### 4.4 极性映射

```
IF i_bExtendPolarity THEN
    s_bLogicExtPos := s_bRetDebounced;   (* 物理收回位 -> 逻辑伸出位 *)
    s_bLogicRetPos := s_bExtDebounced;   (* 物理伸出位 -> 逻辑收回位 *)
ELSE
    s_bLogicExtPos := s_bExtDebounced;   (* 正常映射 *)
    s_bLogicRetPos := s_bRetDebounced;
END_IF;
// 注: i_bRetractPolarity 不影响传感器极性映射, 仅影响双线圈B线圈输出极性(见4.7)
```

### 4.5 单线圈正常运行(i_iSolenoidType=0)

```
伸出流程:  i_bExtend=TRUE
  -> q_aSolenoid[0] := NOT i_bExtendPolarity
  -> q_aSolenoid[1] := FALSE  (单线圈[1]始终FALSE)
  -> 启动超时计时 (如果i_dTimeoutMs>0)
  -> 等待 s_bLogicExtPos=TRUE
  -> q_bIsExtended := TRUE, q_bIsRetracted := FALSE
  -> 取消超时计时, 清除q_bTimeout
  -> 超时检测在命令分支内, 仅当s_bMoving=TRUE且fb_tTimeout.Q=TRUE时触发

收回流程:  i_bRetract=TRUE
  -> q_aSolenoid[0] := i_bExtendPolarity
  -> q_aSolenoid[1] := FALSE  (单线圈[1]始终FALSE)
  -> 启动超时计时 (如果i_dTimeoutMs>0)
  -> 等待 s_bLogicRetPos=TRUE
  -> q_bIsRetracted := TRUE, q_bIsExtended := FALSE
  -> 取消超时计时, 清除q_bTimeout
  -> 超时检测在命令分支内, 仅当s_bMoving=TRUE且fb_tTimeout.Q=TRUE时触发
```

### 4.6 超时处理

```
如果 fb_tTimeout.Q=TRUE 且 s_bMoving=TRUE (超时到达且正在执行动作):
  -> q_bTimeout := TRUE  (锁存, 直到下次到位或命令变化时清除)
  -> q_aSolenoid 保持当前输出  (不强制改变, 由编排器决策)
```

### 4.7 单线圈安全回零(空闲状态, i_iSolenoidType=0)

```
当 i_bExtend=FALSE AND i_bRetract=FALSE 时 (空闲):
  -> q_aSolenoid[0] = i_bExtendPolarity (弹簧复位状态)
  -> q_aSolenoid[1] = FALSE  (单线圈[1]始终FALSE)
  -> fb_tTimeout.IN := FALSE; fb_tTimeout.R := TRUE
  -> 超时故障自动清除 (q_bTimeout := FALSE)
  -> q_bIsExtended := s_bLogicExtPos
  -> q_bIsRetracted := s_bLogicRetPos
```

### 4.8 双线圈两位阀行为逻辑(i_iSolenoidType=1)

#### 4.8.1 A/B互锁规则

```
双线圈核心约束:
  1. q_aSolenoid[0] 和 q_aSolenoid[1] 互斥, 任意时刻最多一个ON
  2. 无命令时两个线圈均OFF, 气缸保持当前位置(非弹簧复位)
  3. i_bExtend优先: 同时命令时A线圈ON, B线圈OFF
```

#### 4.8.2 伸出流程

```
伸出流程:  i_bExtend=TRUE
  -> q_aSolenoid[0] := NOT i_bExtendPolarity  (A线圈驱动, 受i_bExtendPolarity控制)
  -> q_aSolenoid[1] := FALSE                  (B线圈互锁OFF)
  -> 启动超时计时 (如果i_dTimeoutMs>0)
  -> 等待 s_bLogicExtPos=TRUE
  -> q_bIsExtended := TRUE, q_bIsRetracted := FALSE
  -> 取消超时计时, 清除q_bTimeout
```

#### 4.8.3 收回流程

```
收回流程:  i_bRetract=TRUE (且i_bExtend=FALSE)
  -> q_aSolenoid[0] := FALSE                  (A线圈互锁OFF)
  -> q_aSolenoid[1] := NOT i_bRetractPolarity (B线圈驱动, 受i_bRetractPolarity控制)
  -> 启动超时计时 (如果i_dTimeoutMs>0)
  -> 等待 s_bLogicRetPos=TRUE
  -> q_bIsRetracted := TRUE, q_bIsExtended := FALSE
  -> 取消超时计时, 清除q_bTimeout
```

#### 4.8.4 保持位(空闲状态)

```
当 i_bExtend=FALSE AND i_bRetract=FALSE 时 (空闲):
  -> q_aSolenoid[0] := FALSE  (A线圈OFF)
  -> q_aSolenoid[1] := FALSE  (B线圈OFF)
  -> 气缸保持当前位置(双线圈均失电, 非弹簧复位)
  -> fb_tTimeout.IN := FALSE; fb_tTimeout.R := TRUE
  -> 超时故障自动清除 (q_bTimeout := FALSE)
  -> q_bIsExtended := s_bLogicExtPos
  -> q_bIsRetracted := s_bLogicRetPos
```

#### 4.8.5 超时处理

```
如果 fb_tTimeout.Q=TRUE 且 s_bMoving=TRUE (超时到达且正在执行动作):
  -> q_bTimeout := TRUE  (锁存, 直到下次到位或命令变化时清除)
  -> q_aSolenoid 保持当前输出  (不强制改变, 由编排器决策)
```

#### 4.8.6 CASE ELSE安全态(非法i_iSolenoidType)

```
当 i_iSolenoidType 不在 0~1 范围内时:
  -> q_aSolenoid[0] := FALSE
  -> q_aSolenoid[1] := FALSE
  -> 所有输出置为安全态, 禁止任何线圈驱动
```

## 5. 接口交互协议

```
编排器(FB_1002)                     FB_1011_CylinderControl
     |                                      |
     |-- i_bExtend := TRUE --------------->|  (命令: 伸出)
     |  i_bExtendPolarity := FALSE          |
     |  i_dDebounceMs := 50                 |
     |                                      |  q_aSolenoid[0] := TRUE
     |                                      |  q_aSolenoid[1] := FALSE
     |                                      |  消抖+极性映射...
     |                                      |  s_bLogicExtPos=TRUE
     |<-- q_bIsExtended := TRUE ------------|  (反馈: 已伸出)
     |                                      |
     |-- i_bExtend := FALSE --------------->|  (撤销命令)
     |                                      |  弹簧复位 (保持原位安全)
```

## 6. 报警码

本 FB 不直接输出报警码. 报警信号通过 q_bTimeout 和 q_bSensorFault 两个 BOOL 输出给编排器, 由编排器根据本层编号(1~4)编码为带层号的完整报警码:

| 信号             | 层号编码规则 | 层L1 | 层L2 | 层L3 | 层L4 |
| ---------------- | :----------: | :--: | :--: | :--: | :--: |
| 阻挡 Timeout     |     1x0     | 110 | 120 | 130 | 140 |
| 阻挡 SensorFault |     1x2     | 112 | 122 | 132 | 142 |
| 分料 Timeout     |     1x1     | 111 | 121 | 131 | 141 |
| 分料 SensorFault |     1x3     | 113 | 123 | 133 | 143 |

## 7. 接口版本兼容性说明

### V9.x → V10.0.0 迁移指南

> **Breaking Change**: V10.0.0 变更了输出接口, 现有调用方必须修改.

| 变更项 | V9.x (旧) | V10.0.0 (新) | 迁移操作 |
| ------ | --------- | ------------ | -------- |
| 电磁阀输出 | q_bSolenoid : BOOL | q_aSolenoid : ARRAY[0..7] OF BOOL | `q_bSolenoid` → `q_aSolenoid[0]` |
| 单线圈[1]输出 | 不存在 | q_aSolenoid[1] 始终 FALSE | 无需处理, 忽略即可 |
| 新增输入参数 | 不存在 | i_bRetractPolarity : BOOL := FALSE | 单线圈模式忽略, 无需修改; 双线圈模式按需配置 |
| 命令处理结构 | IF/ELSIF | CASE i_iSolenoidType | 行为等价, 无需修改调用方 |

**OB1 IO映射迁移示例**:

```
// V9.x (旧)
fbBlock.q_bSolenoid => %Q0.0;

// V10.0.0 (新)
fbBlock.q_aSolenoid[0] => %Q0.0;  // 线圈A (原q_bSolenoid)
fbBlock.q_aSolenoid[1] => %Q0.1;  // 线圈B (单线圈模式不使用, 可不映射)
```

**双线圈模式新增配置**:

```
// V10.0.0 新增: 双作用气缸
fbLift : FB_1011_CylinderControl;
fbLift(i_iSolenoidType := 1,
       i_bExtendPolarity := FALSE,
       i_bRetractPolarity := FALSE,
       ...);
fbLift.q_aSolenoid[0] => %Q0.2;  // A线圈-伸出方向
fbLift.q_aSolenoid[1] => %Q0.3;  // B线圈-收回方向
```

## 8. 关联文档

| 文档        | 路径                                                                                                  |
| ----------- | ----------------------------------------------------------------------------------------------------- |
| REQ         | 需求分析文档_REQ.md                                                                                     |
| TEC         | 技术方案文档_TEC.md                                                                                    |
| DSN         | 详细设计说明书_DSN.md                                                                                   |
| INT(V10.0.0) | 接口文档_INT.md                                                                                         |
| FB_TON      | ../../timer/FB_TON.scl                                                                                |
| FB_TONR     | ../../timer/FB_TONR.scl                                                                               |
| 规范        | ../../../../../0100_PLC自动化/00_通用规范/PLC编程/905_SCL编程规范_LSP.md                        |
| 规范        | ../../../../../0100_PLC自动化/00_通用规范/PLC编程/904_SCL注释规范_LSP.md                        |
| 规范        | ../../../../../0100_PLC自动化/00_通用规范/PLC编程/903_定时器使用规范_LSP.md                      |
