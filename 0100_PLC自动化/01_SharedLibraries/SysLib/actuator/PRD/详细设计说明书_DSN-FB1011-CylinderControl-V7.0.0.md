# 详细设计说明书 FB_1011_CylinderControl

## 0. 文档基础信息

| 属性 | 值 |
|------|-----|
| **文档标题** | FB_1011 气缸控制详细设计 |
| **文档版本** | V7.0.0 |
| **关联源码** | conveyor/FB_1011_CylinderControl.scl |
| **关联IFC** | 接口文档_IFC-FB1011-CylinderControl-V7.0.0.md |
| **编制日期** | 2026-05-18 |
| **编制人** | Trae |
| **遵循规范** | 801_DEV-V1.0.5, 810_DEV-V1.0.2 |

## 1. 设计原则

1. **命令驱动**: 气缸只响应伸出/收回命令，不自行决定何时动作
2. **输出保持**: 无新命令时保持电磁阀状态不变（双线圈自保持阀兼容）
3. **超时隔离**: 超时仅报警不强制复位，编排器决定后续策略
4. **传感器故障实时诊断**: 上下位冲突检测为纯组合逻辑，无延时
5. **可复用**: 同一FB可实例化为阻挡气缸、分料气缸或任何二位置气动执行器

## 2. 状态定义

本FB不维护业务流程状态，仅跟踪物理状态：

| 物理状态 | 条件 | 电磁阀输出 |
|----------|------|:---------:|
| 收回位置 | i_bUpSensor=TRUE, i_bDownSensor=FALSE | 保持OFF |
| 伸出位置 | i_bDownSensor=TRUE, i_bUpSensor=FALSE | 保持ON |
| 运动中(伸出) | 两传感器都FALSE, 命令=Extend | ON |
| 运动中(收回) | 两传感器都FALSE, 命令=Retract | OFF |
| 传感器故障 | 两传感器都TRUE | 保持上次 |

## 3. 详细伪代码

```pascal
(* ==================== 传感器冗余一致性检查（持续运行）==================== *)
IF i_bUpSensor AND i_bDownSensor THEN
    q_bSensorFault := TRUE;
ELSE
    q_bSensorFault := FALSE;
END_IF;

(* ==================== 气缸命令处理 ==================== *)

(* 命令优先级: Extend > Retract *)
IF i_bExtend THEN
    (* ---- 伸出命令 ----
       启动伸出,开始超时计时 *)
    q_bSolenoid := TRUE;
    
    IF NOT bMoving THEN
        bMoving := TRUE;
        IF i_iTimeoutMs > 0 THEN
            tTimeout.IN := TRUE;
            tTimeout.R := FALSE;
            tTimeout.PT := INT_TO_DINT(i_iTimeoutMs);
        END_IF;
    END_IF;
    
    (* 到位检测 *)
    IF i_bDownSensor THEN
        q_bIsExtended := TRUE;
        q_bIsRetracted := FALSE;
        bMoving := FALSE;
        q_bTimeout := FALSE;
        tTimeout.IN := FALSE;
        tTimeout.R := TRUE;
    END_IF;
    
    (* 超时检测 *)
    IF tTimeout.Q THEN
        q_bTimeout := TRUE;
    END_IF;

ELSIF i_bRetract THEN
    (* ---- 收回命令 ----
       启动收回,开始超时计时 *)
    q_bSolenoid := FALSE;
    
    IF NOT bMoving THEN
        bMoving := TRUE;
        IF i_iTimeoutMs > 0 THEN
            tTimeout.IN := TRUE;
            tTimeout.R := FALSE;
            tTimeout.PT := INT_TO_DINT(i_iTimeoutMs);
        END_IF;
    END_IF;
    
    (* 到位检测 *)
    IF i_bUpSensor THEN
        q_bIsRetracted := TRUE;
        q_bIsExtended := FALSE;
        bMoving := FALSE;
        q_bTimeout := FALSE;
        tTimeout.IN := FALSE;
        tTimeout.R := TRUE;
    END_IF;
    
    (* 超时检测 *)
    IF tTimeout.Q THEN
        q_bTimeout := TRUE;
    END_IF;

ELSE
    (* ---- 无命令：空闲 ----
       保持电磁阀当前状态
       清除运动标志和超时 *)
    bMoving := FALSE;
    q_bTimeout := FALSE;
    tTimeout.IN := FALSE;
    tTimeout.R := TRUE;
    
    (* 更新到位状态 *)
    q_bIsExtended := i_bDownSensor;
    q_bIsRetracted := i_bUpSensor;
END_IF;

(* ==================== 定时器实例 ==================== *)
tTimeout(IN := tTimeout.IN, R := tTimeout.R, PT := tTimeout.PT,
         Q => tTimeout.Q, ET => tTimeout.ET);
```

## 4. 时序图

### 4.1 正常伸出→收回周期

```
i_bExtend      ──────┐                     ┌──────
                     └─────────────────────┘
i_bRetract     ─────────────────┐          ┌──────
                                └──────────┘
q_bSolenoid    ──────┐                     │
                     └─────────────────────┘
i_bDownSensor  ─────────┐          ┌────────────────
                        └──────────┘
i_bUpSensor    ──────┐                     ┌──────
                     └─────────────────────┘
q_bIsExtended  ─────────┐          ┌────────────────
                        └──────────┘
q_bIsRetracted ──────┐                     ┌──────
                     └─────────────────────┘
bMoving        ────────┐          ┌─────────────
                       └──────────┘
tTimeout.IN    ──────┐  ┌────────┐  ┌─────────────
                     └──┘        └──┘
```

### 4.2 超时场景

```
i_bExtend      ──────┐
                     └────────────────────────── ... (超时后仍为TRUE)
q_bSolenoid    ──────┐
                     └────────────────────────── ...
i_bDownSensor  ───────────────────────────────── ... (始终未到位)
tTimeout.Q     ──────────────────┐
                                 └────────────── ... (超时到达)
q_bTimeout     ──────────────────┐
                                 └────────────── ... (锁存)
```

## 5. 边界条件处理

| 场景 | 行为 |
|------|------|
| Extend=TRUE 时已在下位 | 立即置 q_bIsExtended=TRUE，不启动计时 |
| Retract=TRUE 时已在上位 | 立即置 q_bIsRetracted=TRUE，不启动计时 |
| Extend+Retract 同时TRUE | Extend 优先，电磁阀=ON |
| 运动中命令翻转 | 立即切换方向，重新启动超时计时 |
| i_iTimeoutMs=0 | 关闭超时检测，q_bTimeout 始终 FALSE |
| 上下位同时ON | q_bSensorFault=TRUE，到位状态两者都 TRUE |
| 使能丢失 (编排器侧) | 编排器负责在使能丢失时将 Extend/Retract 都置 FALSE |

## 6. 变量定义

### 6.1 VAR

| 变量 | 类型 | 初始值 | 保持性 | 说明 |
|------|------|:------:|:------:|------|
| tTimeout | FB_TONR | — | 非保持 | 超时累积定时器 |
| bMoving | BOOL | FALSE | 非保持 | 动作进行中，用于边沿触发计时 |

### 6.2 定时器

| 定时器 | 类型 | PT来源 | 用途 |
|--------|------|--------|------|
| tTimeout | TONR | i_iTimeoutMs (INT→DINT) | 伸出/收回共用，命令切换时自动复位 |

> **TONR 选择理由**: 需要在超时到达后保持 Q=TRUE 直到显式复位（而非自动清零），以便编排器可靠读取。

## 7. 关联文档

| 文档 | 路径 |
|------|------|
| IFC | 接口文档_IFC-FB1011-CylinderControl-V7.0.0.md |
| 电机控制 IFC | 接口文档_IFC-FB1012-ConveyorMotor-V7.0.0.md |
| 编排器 DSN | ../../../../DJ-2026-005/02_PLC程序/通用ST程序及变量表/conveyor/PRD/详细设计说明书_DSN-FB1002-SingleLayerConveyor-V7.0.0.md |
