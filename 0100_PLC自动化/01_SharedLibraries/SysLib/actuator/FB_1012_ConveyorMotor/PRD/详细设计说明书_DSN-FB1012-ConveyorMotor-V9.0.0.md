---
spec_id: DSN-FB1012
title: "FB_1012 输送电机控制详细设计"
version: "V9.0.0"
domain: plc
lifecycle: stable
canonical_path: "0100_PLC自动化/01_SharedLibraries/SysLib/actuator/FB_1012_ConveyorMotor/PRD/详细设计说明书_DSN-FB1012-ConveyorMotor-V9.0.0.md"
tags: ["输送电机", "执行器", "PLC功能块", "详细设计"]
---
# 详细设计说明书 FB_1012_ConveyorMotor

## 0. 文档基础信息

| 属性         | 值                                                                               |
| ------------ | -------------------------------------------------------------------------------- |
| **文档标题** | FB_1012 输送电机控制详细设计                                                     |
| **文档版本** | V9.0.0                                                                           |
| **关联源码** | actuator/FB_1012_ConveyorMotor/FB_1012_ConveyorMotor.scl                         |
| **关联IFC**  | 接口文档_IFC-FB1012-ConveyorMotor-V9.0.0.md                                      |
| **编制日期** | 2026-05-30                                                                       |
| **编制人**   | Trae                                                                             |
| **审核人**   | 人工                                                                             |
| **遵循规范** | LSP-905-V1.0.2, LSP-904-V1.2.0, LSP-903-V1.0.0                                  |

## 1. 设计原则

1. **执行器职责**: 只负责执行命令和反馈执行结果, 不处理安全互锁(由编排器/上层处理)
2. **故障优先**: VFD故障时无条件切断所有输出 (最高优先级)
3. **方向互斥**: 同一时刻只有一个方向有效 (Fwd > Rev)
4. **慢速修饰**: 慢速是方向命令的修饰符, 不能独立运行, 必须与方向命令组合
5. **控制模式**: 端子控制为默认模式, 通讯控制预留接口
6. **无时序依赖**: 纯组合逻辑, 无定时器
7. **扁平接口**: 简单执行机构使用扁平VAR_INPUT/VAR_OUTPUT, 无需结构体封装

## 2. 互锁优先级链

```
优先级从高到低:
+-------------------+
|  1. VFD故障       | -> 所有输出 := FALSE, q_bVfdAlarm := TRUE
+-------------------+
|  2. 方向命令仲裁   | -> Fwd > Rev, 慢速修饰方向输出
+-------------------+
```

## 3. 详细伪代码

```pascal
(* ==================== VFD故障检测 - 最高优先级 ==================== *)
IF i_bVfdFault THEN
    q_bVfdAlarm := TRUE;
    q_bFwdOut := FALSE;
    q_bRevOut := FALSE;
    q_bSlowOut := FALSE;
    q_bRunning := FALSE;
ELSE
    q_bVfdAlarm := FALSE;

    (* ==================== 方向命令仲裁 Fwd > Rev ==================== *)
    IF i_bFwdCmd THEN
        q_bFwdOut := TRUE;
        q_bRevOut := FALSE;
        q_bSlowOut := i_bSlowCmd;   (* 慢速修饰正转 *)
        q_bRunning := TRUE;
    ELSIF i_bRevCmd THEN
        q_bFwdOut := FALSE;
        q_bRevOut := TRUE;
        q_bSlowOut := i_bSlowCmd;   (* 慢速修饰反转 *)
        q_bRunning := TRUE;
    ELSE
        q_bFwdOut := FALSE;
        q_bRevOut := FALSE;
        q_bSlowOut := FALSE;        (* 无方向命令时慢速无效 *)
        q_bRunning := FALSE;
    END_IF;
END_IF;
```

## 4. 命令真值表

| i_bFwdCmd | i_bRevCmd | i_bSlowCmd | VFD  | q_bFwdOut | q_bRevOut | q_bSlowOut | q_bRunning | 说明         |
|:---------:|:---------:|:----------:|:----:|:---------:|:---------:|:----------:|:----------:|--------------|
| 0         | 0         | 0          | OK   | 0         | 0         | 0          | 0          | 停止         |
| 0         | 0         | 1          | OK   | 0         | 0         | 0          | 0          | 慢速无效     |
| 1         | 0         | 0          | OK   | 1         | 0         | 0          | 1          | 高速正转     |
| 1         | 0         | 1          | OK   | 1         | 0         | 1          | 1          | 慢速正转     |
| 0         | 1         | 0          | OK   | 0         | 1         | 0          | 1          | 高速反转     |
| 0         | 1         | 1          | OK   | 0         | 1         | 1          | 1          | 慢速反转     |
| 1         | 1         | 0          | OK   | 1         | 0         | 0          | 1          | Fwd优先      |
| 1         | 1         | 1          | OK   | 1         | 0         | 1          | 1          | Fwd优先+慢速 |
| x         | x         | x          | 故障 | 0         | 0         | 0          | 0          | VFD封锁      |

## 5. 控制模式说明

### 5.1 端子控制模式 (i_iCtrlMode=0, 默认)

VFD通过数字端子接收Fwd/Rev/Slow信号:
- q_bFwdOut -> VFD正转端子
- q_bRevOut -> VFD反转端子
- q_bSlowOut -> VFD慢速端子
- i_rSpeed参数无效, 速度由VFD内部参数设定

### 5.2 通讯控制模式 (i_iCtrlMode=1, 预留)

VFD通过通讯总线接收控制指令:
- i_rSpeed -> 速度设定值写入VFD
- 方向仍通过数字端子或通讯控制
- 现阶段未实现, 仅预留接口

## 6. 关联文档

| 文档        | 路径                                                                             |
| ----------- | -------------------------------------------------------------------------------- |
| IFC         | 接口文档_IFC-FB1012-ConveyorMotor-V9.0.0.md                                      |
| FB_1011 IFC | ../FB_1011_CylinderControl/PRD/接口文档_IFC-FB1011-CylinderControl-V9.0.0.md      |
