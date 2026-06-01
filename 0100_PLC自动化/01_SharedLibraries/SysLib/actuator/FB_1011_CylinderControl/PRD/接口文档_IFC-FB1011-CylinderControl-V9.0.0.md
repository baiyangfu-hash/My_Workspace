---
spec_id: IFC-FB1011
title: "FB_1011 气缸控制接口定义"
version: "V9.0.0"
domain: plc
lifecycle: stable
canonical_path: "0100_PLC自动化/01_SharedLibraries/SysLib/actuator/FB_1011_CylinderControl/PRD/接口文档_IFC-FB1011-CylinderControl-V9.0.0.md"
tags: ["气缸控制", "执行器", "PLC功能块", "接口", "电磁阀"]
---
# 接口文档 FB_1011_CylinderControl

## 0. 文档基础信息

| 属性         | 值                                                                                       |
| ------------ | ---------------------------------------------------------------------------------------- |
| **文档标题** | FB_1011 气缸控制接口定义                                                                 |
| **文档版本** | V9.0.0                                                                                   |
| **关联源码** | actuator/FB_1011_CylinderControl/FB_1011_CylinderControl.scl                             |
| **编制日期** | 2026-05-30                                                                               |
| **编制人**   | Trae                                                                                     |
| **审核人**   | 人工                                                                                     |
| **遵循规范** | LSP-905-V1.0.2, LSP-904-V1.1.0, LSP-903-V2.1.0                                          |
| **变更记录** | V9.0.0: 移除ST_Cylinder VAR_IN_OUT, 回归扁平VAR_INPUT/OUTPUT; 新增传感器消抖; 完整实现极性取反 |

## 0.1 电磁阀类型定义

| SolenoidType值 | 电磁阀类型     | 线圈数量 | 输出信号                              | 默认行为         | 当前支持       |
| -------------- | -------------- | -------- | ------------------------------------- | ---------------- | -------------- |
| **0**          | **单线圈两位阀** | 1个      | q_bSolenoid                           | 弹簧复位(收回)   | 支持(默认)     |
| 1              | 双线圈两位阀   | 2个      | q_bExtendSolenoid, q_bRetractSolenoid | 保持最后位置     | 预留扩展       |
| 2              | 3位4通中封阀   | 2个      | q_bExtendSolenoid, q_bRetractSolenoid | 保持位置(中封)   | 预留扩展       |
| 3              | 3位4通中泄阀   | 2个      | q_bExtendSolenoid, q_bRetractSolenoid | 泄压回油(中泄)   | 预留扩展       |

### 0.1.1 单线圈两位阀真值表(默认配置)

| i_bExtend | i_bRetract | i_bExtendPolarity | q_bSolenoid | 气缸行为 |
| --------- | ---------- | ----------------- | ----------- | -------- |
| TRUE      | FALSE      | FALSE             | TRUE        | 伸出     |
| FALSE     | TRUE       | FALSE             | FALSE       | 收回     |
| FALSE     | FALSE      | FALSE             | FALSE       | 弹簧复位 |
| TRUE      | FALSE      | TRUE              | FALSE       | 伸出     |
| FALSE     | TRUE       | TRUE              | TRUE        | 收回     |
| FALSE     | FALSE      | TRUE              | TRUE        | 弹簧复位 |

### 0.1.2 线圈极性取反说明

| i_bExtendPolarity | 说明     | q_bSolenoid=TRUE | q_bSolenoid=FALSE | 传感器映射                              | 适用场景                |
| ----------------- | -------- | ---------------- | ----------------- | --------------------------------------- | ----------------------- |
| FALSE (默认)      | 正常极性 | 伸出             | 收回              | ExtendedPos->伸出位, RetractedPos->收回位 | 阻挡/夹紧等气缸         |
| TRUE              | 极性取反 | 收回             | 伸出              | ExtendedPos->收回位, RetractedPos->伸出位 | 拍正/顶升等弹簧复位气缸 |

> **极性取反完整行为**: 当 i_bExtendPolarity=TRUE 时, 不仅电磁阀输出反转, 传感器映射也互换(物理伸出位视为逻辑收回位, 物理收回位视为逻辑伸出位), 状态输出 q_bIsExtended/q_bIsRetracted 随之反转.

## 1. 功能概述

**单一气缸执行控制块**, 封装 推力/拉力命令 -> 传感器消抖 -> 极性映射 -> 电磁阀输出 -> 到位检测 -> 超时保护 -> 传感器冗余一致性检查 的完整闭环.

支持多种电磁阀类型配置(当前默认单线圈两位阀), 支持线圈极性取反(含传感器映射反转), 支持磁环传感器TON消抖.

适用于输送机系统中任何需要伸出/收回动作的气动执行器(阻挡气缸, 分料气缸等).

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

| 场景     | 实例名               | 配置                                      | 说明                                              |
| -------- | -------------------- | ----------------------------------------- | ------------------------------------------------- |
| 阻挡气缸 | fbBlock : FB_1011    | i_iSolenoidType=0, i_bExtendPolarity=FALSE | i_bExtend=阻挡下降, i_bRetract=阻挡上升           |
| 分料气缸 | fbSeparate : FB_1011 | i_iSolenoidType=0, i_bExtendPolarity=FALSE | i_bExtend=分料推出, i_bRetract=分料复位           |
| 拍正气缸 | fbAlign : FB_1011    | i_iSolenoidType=0, i_bExtendPolarity=TRUE  | i_bExtend=拍正伸出, i_bRetract=拍正收回(极性取反) |

## 2. 接口定义

### 2.1 VAR_INPUT

| 名称               | 类型 | 默认值 | 有效值域    | 说明                                                              | 来源           |
| ------------------ | ---- | ------ | ----------- | ----------------------------------------------------------------- | -------------- |
| i_bExtend          | BOOL | -      | TRUE/FALSE  | 伸出命令 (推/降/夹紧)                                            | 编排器         |
| i_bRetract         | BOOL | -      | TRUE/FALSE  | 收回命令 (拉/升/松开)                                            | 编排器         |
| i_bExtendedPos     | BOOL | -      | TRUE/FALSE  | 伸出位传感器 (下位/降位/夹紧位/工作点)                           | OB1->IO映射    |
| i_bRetractedPos    | BOOL | -      | TRUE/FALSE  | 收回位传感器 (上位/升位/松开位/原点)                             | OB1->IO映射    |
| i_dTimeoutMs       | DINT | 5000   | 0~60000     | 动作超时时间(ms), 0=关闭超时检测                                 | 编排器         |
| i_dDebounceMs      | DINT | 0      | 0~1000      | 传感器消抖时间(扫描周期), 0=关闭消抖, >0=TON确认稳定后输出       | 编排器         |
| i_iSolenoidType    | INT  | 0      | 0~3         | 电磁阀类型: 0=单线圈两位阀(默认), 1=双线圈两位阀, 2=3位4通中封阀, 3=3位4通中泄阀 (预留) | 编排器 |
| i_bExtendPolarity  | BOOL | FALSE  | TRUE/FALSE  | 线圈极性取反: FALSE=正常, TRUE=取反(电磁阀+传感器映射均反转)     | 编排器         |

> **命令优先级**: 当 i_bExtend 和 i_bRetract 同时为 TRUE 时, i_bExtend(伸出)优先.

### 2.2 VAR_OUTPUT

| 名称            | 类型 | 默认值 | 有效值域    | 说明                            | 去向           |
| --------------- | ---- | ------ | ----------- | ------------------------------- | -------------- |
| q_bSolenoid     | BOOL | FALSE  | TRUE/FALSE  | 电磁阀输出 (单线圈两位阀用)     | OB1->IO映射    |
| q_bIsExtended   | BOOL | FALSE  | TRUE/FALSE  | 已伸出到位 (极性映射后)         | 编排器         |
| q_bIsRetracted  | BOOL | FALSE  | TRUE/FALSE  | 已收回到位 (极性映射后)         | 编排器         |
| q_bTimeout      | BOOL | FALSE  | TRUE/FALSE  | 动作超时 (伸出或收回未在时间内到位) | 编排器->报警 |
| q_bSensorFault  | BOOL | FALSE  | TRUE/FALSE  | 传感器冗余故障 (上下位同时ON, 消抖后检测) | 编排器->报警 |

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
| s_bLogicRetPos    | BOOL    | FALSE  | 逻辑收回位 (极性映射后)           |
| s_bMoving         | BOOL    | FALSE  | 正在执行动作中                    |

## 3. 信号处理流水线

```
物理传感器       TON消抖           传感器故障检测       极性映射            命令处理
i_bExtendedPos ─→ fb_tDebounceExt ─→ s_bExtDebounced ─┬─→ SensorFault  ─→ s_bLogicExtPos ─→ 到位判断
i_bRetractedPos ─→ fb_tDebounceRet ─→ s_bRetDebounced ─┤                  ─→ s_bLogicRetPos ─→ 到位判断
                                                         │
i_dDebounceMs ──→ PT参数(0=直通)                        └─→ i_bExtendPolarity
                                                              FALSE: 正常映射
                                                              TRUE:  互换映射
```

## 4. 行为逻辑(单线圈两位阀)

### 4.1 传感器消抖

```
IF i_dDebounceMs > 0 THEN
    fb_tDebounceExt(IN := i_bExtendedPos, PT := i_dDebounceMs,
                    Q => s_bExtDebounced, ET => s_dExtDebounceEt);
    fb_tDebounceRet(IN := i_bRetractedPos, PT := i_dDebounceMs,
                    Q => s_bRetDebounced, ET => s_dRetDebounceEt);
ELSE
    s_bExtDebounced := i_bExtendedPos;    (* 0=直通, 不消抖 *)
    s_bRetDebounced := i_bRetractedPos;
END_IF;
```

### 4.2 传感器冗余一致性检查(消抖后, 极性映射前)

```
IF s_bExtDebounced AND s_bRetDebounced THEN
    q_bSensorFault := TRUE;   (* 上下位同时ON, 物理上不可能 *)
ELSE
    q_bSensorFault := FALSE;
END_IF;
```

### 4.3 极性映射

```
IF i_bExtendPolarity THEN
    s_bLogicExtPos := s_bRetDebounced;   (* 物理收回位 -> 逻辑伸出位 *)
    s_bLogicRetPos := s_bExtDebounced;   (* 物理伸出位 -> 逻辑收回位 *)
ELSE
    s_bLogicExtPos := s_bExtDebounced;   (* 正常映射 *)
    s_bLogicRetPos := s_bRetDebounced;
END_IF;
```

### 4.4 正常运行

```
伸出流程:  i_bExtend=TRUE
  -> q_bSolenoid := NOT i_bExtendPolarity
  -> 启动超时计时 (如果i_dTimeoutMs>0)
  -> 等待 s_bLogicExtPos=TRUE
  -> q_bIsExtended := TRUE, q_bIsRetracted := FALSE
  -> 取消超时计时, 清除q_bTimeout

收回流程:  i_bRetract=TRUE
  -> q_bSolenoid := i_bExtendPolarity
  -> 启动超时计时 (如果i_dTimeoutMs>0)
  -> 等待 s_bLogicRetPos=TRUE
  -> q_bIsRetracted := TRUE, q_bIsExtended := FALSE
  -> 取消超时计时, 清除q_bTimeout
```

### 4.5 超时处理

```
如果 fb_tTimeout.Q=TRUE (超时到达) 且尚未到位:
  -> q_bTimeout := TRUE  (锁存, 直到下次命令变化时清除)
  -> q_bSolenoid 保持当前输出  (不强制改变, 由编排器决策)
```

### 4.6 安全回零(空闲状态)

```
当 i_bExtend=FALSE AND i_bRetract=FALSE 时 (空闲):
  -> q_bSolenoid = i_bExtendPolarity (弹簧复位状态)
  -> fb_tTimeout.IN := FALSE; fb_tTimeout.R := TRUE
  -> 超时故障自动清除 (q_bTimeout := FALSE)
  -> q_bIsExtended := s_bLogicExtPos
  -> q_bIsRetracted := s_bLogicRetPos
```

## 5. 接口交互协议

```
编排器(FB_1002)                     FB_1011_CylinderControl
     |                                      |
     |-- i_bExtend := TRUE --------------->|  (命令: 伸出)
     |  i_bExtendPolarity := FALSE          |
     |  i_dDebounceMs := 50                 |
     |                                      |  q_bSolenoid := TRUE
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

## 7. 关联文档

| 文档        | 路径                                                                                                  |
| ----------- | ----------------------------------------------------------------------------------------------------- |
| REQ         | 需求分析文档_REQ-FB1011-CylinderControl-V8.1.0.md                                                     |
| TECH        | 技术方案文档_TECH-FB1011-CylinderControl-V8.1.0.md                                                    |
| DSN         | 详细设计说明书_DSN-FB1011-CylinderControl-V7.1.0.md                                                   |
| FB_TON      | ../../timer/FB_TON.scl                                                                                |
| FB_TONR     | ../../timer/FB_TONR.scl                                                                               |
| 规范        | ../../../../../0100_PLC自动化/00_通用规范/PLC编程/905_SCL编程规范_LSP-V1.0.2.md                        |
| 规范        | ../../../../../0100_PLC自动化/00_通用规范/PLC编程/904_SCL注释规范_LSP-V1.1.0.md                        |
| 规范        | ../../../../../0100_PLC自动化/00_通用规范/PLC编程/903_定时器使用规范_LSP-V1.0.0.md                      |
