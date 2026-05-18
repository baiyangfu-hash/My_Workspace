# 详细设计说明书 FB_1002_SingleLayerConveyor_BufferFraming

## 0. 文档基础信息

| 属性 | 值 |
|------|-----|
| **文档标题** | FB_1002 单层输送机详细设计 |
| **文档版本** | V6.0.0 |
| **关联源码** | conveyor/FB_1002_SingleLayerConveyor_BufferFraming.scl |
| **编制日期** | 2026-05-17 |
| **编制人** | Trae |
| **遵循规范** | 801_DEV-V1.0.5, 810_DEV-V1.0.2 |
| **数据来源** | 源程序功能基线_SRC-DJ-2026-005-V1.0.0 |

## 1. 设计原则

1. **先输送再分料**：源程序 Step_S 状态机真实流程，与当前旧版代码完全相反
2. **无物理地址依赖**：所有 I/O 通过主控程序 OB1 映射后以接口变量传入
3. **双通道冗余一致性检查**：阻挡/分料气缸的上下位传感器做双通道一致性诊断
4. **分料超时保护**：分料推出/复位步均有独立超时定时器

## 2. 状态机跳转图

```
Step0(初始化反转)
  → 反转超时/限位 → Step1
Step1(等待来料)
  → 分料前感应器ON → Step2
Step2(阻挡下降)
  → 阻挡下位ON → Step10
Step10(输送正转)
  → 正转延时到 → Step20
Step20(到位检测+阻挡上升)
  → 到位1&到位2=ON + 阻挡上位ON → Step30
Step30(分料推出)
  → 分料下位ON → Step50
Step50(慢速送出)
  → 慢速延时到 → Step60
Step60(请求取料)
  → 取料确认 → Step70
Step70(分料复位)
  → 分料上位ON → Step0
```

## 3. 状态机伪代码

```
CASE q_iCurrentState OF

  STEP_INIT: (* 0 - 初始化 *)
    IF bStepEntry THEN
      q_bBlockSolenoid := FALSE;
      q_bSeparateSolenoid := FALSE;
      q_bConveyorFwd := FALSE;
      q_bConveyorSlow := FALSE;
      q_bConveyorRev := TRUE;     (* 反转复位 *)
      tInitTimer(IN := TRUE, PT := T#3S);
      bStepEntry := FALSE;
    END_IF;

    IF tInitTimer.Q THEN
      q_bConveyorRev := FALSE;
      bStepEntry := TRUE;
      q_iCurrentState := STEP_WAIT_MATERIAL;
    END_IF;

  STEP_WAIT_MATERIAL: (* 1 - 等待来料 *)
    IF bStepEntry THEN
      q_bConveyorRev := FALSE;
      bStepEntry := FALSE;
    END_IF;

    IF i_bPreSeparateSensor THEN
      bStepEntry := TRUE;
      q_iCurrentState := STEP_BLOCK_DOWN;
    END_IF;

  STEP_BLOCK_DOWN: (* 2 - 阻挡下降 *)
    IF bStepEntry THEN
      q_bBlockSolenoid := TRUE;
      bStepEntry := FALSE;
    END_IF;

    IF i_bBlockCylinderDown THEN
      bStepEntry := TRUE;
      q_iCurrentState := STEP_CONVEYOR_FWD;
    END_IF;

  STEP_CONVEYOR_FWD: (* 10 - 输送正转 *)
    IF bStepEntry THEN
      IF i_bSafetyDoorOk THEN
        q_bConveyorFwd := TRUE;
      END_IF;
      tConvFwdTimer(IN := TRUE, PT := T#5S);
      bStepEntry := FALSE;
    END_IF;

    IF tConvFwdTimer.Q THEN
      q_bConveyorFwd := FALSE;
      bStepEntry := TRUE;
      q_iCurrentState := STEP_POSITION_CHECK_BLOCK_UP;
    END_IF;

  STEP_POSITION_CHECK_BLOCK_UP: (* 20 - 到位检测+阻挡上升 *)
    IF bStepEntry THEN
      q_bBlockSolenoid := FALSE;
      bStepEntry := FALSE;
    END_IF;

    IF i_bPositionSensor1 AND i_bPositionSensor2 AND i_bBlockCylinderUp THEN
      bStepEntry := TRUE;
      q_iCurrentState := STEP_SEPARATE_PUSH;
    END_IF;

  STEP_SEPARATE_PUSH: (* 30 - 分料推出 *)
    IF bStepEntry THEN
      q_bSeparateSolenoid := TRUE;
      tSeparateTimer(IN := TRUE, PT := INT_TO_TIME(i_iSeparateTime));
      bStepEntry := FALSE;
    END_IF;

    IF tSeparateTimer.Q THEN
      (* 超时 *)
      q_iAlarmCode := 100 + i_iLayerIndex;  (* 100~103 对应L1~L4 *)
      q_bSeparateTimeout := TRUE;
    END_IF;

    IF i_bSeparateCylinderDown THEN
      tSeparateTimer(IN := FALSE);
      bStepEntry := TRUE;
      q_iCurrentState := STEP_CONVEYOR_SLOW;
    END_IF;

  STEP_CONVEYOR_SLOW: (* 50 - 慢速送出 *)
    IF bStepEntry THEN
      IF i_bSafetyDoorOk THEN
        q_bConveyorSlow := TRUE;
      END_IF;
      tSlowTimer(IN := TRUE, PT := T#2S);
      bStepEntry := FALSE;
    END_IF;

    IF tSlowTimer.Q THEN
      q_bConveyorSlow := FALSE;
      bStepEntry := TRUE;
      q_iCurrentState := STEP_REQUEST_PICKUP;
    END_IF;

  STEP_REQUEST_PICKUP: (* 60 - 请求取料 *)
    IF bStepEntry THEN
      q_bLayerFeedDone := FALSE;  (* 清除上次脉冲 *)
      bStepEntry := FALSE;
    END_IF;

    IF bPickupConfirmed THEN
      bPickupConfirmed := FALSE;
      bStepEntry := TRUE;
      q_iCurrentState := STEP_SEPARATE_RETURN;
    END_IF;

  STEP_SEPARATE_RETURN: (* 70 - 分料复位 *)
    IF bStepEntry THEN
      q_bSeparateSolenoid := FALSE;
      tSeparateTimer(IN := TRUE, PT := INT_TO_TIME(i_iSeparateTime));
      bStepEntry := FALSE;
    END_IF;

    IF tSeparateTimer.Q THEN
      q_iAlarmCode := 100 + i_iLayerIndex;
      q_bSeparateTimeout := TRUE;
    END_IF;

    IF i_bSeparateCylinderUp THEN
      tSeparateTimer(IN := FALSE);
      q_bLayerFeedDone := TRUE;   (* 脉冲通知取放料 *)
      bStepEntry := TRUE;
      q_iCurrentState := STEP_INIT;
    END_IF;

END_CASE;
```

## 4. 报警逻辑

### 4.1 传感器冗余一致性检查（持续运行）

```
(* 阻挡上位双通道一致？*)
q_bSensorFaultBlockUp :=
  NOT (i_bBlockCylinderUp = i_bBlockCylinderUp_Redundant);

(* 分料下位双通道一致？*)
q_bSensorFaultSeparateDown :=
  NOT (i_bSeparateCylinderDown = i_bSeparateCylinderDown_Redundant);
(* 其余F3x~F6x报警同理 *)
```

### 4.2 报警码分配

| 报警码 | 含义 | 层 |
|:------:|------|:--:|
| 100 | 分料推出/复位超时 | L1 |
| 101 | 分料推出/复位超时 | L2 |
| 102 | 分料推出/复位超时 | L3 |
| 103 | 分料推出/复位超时 | L4 |
| 130 | 阻挡上位传感器冗余不一致 | L1 |
| 131 | 阻挡下位传感器冗余不一致 | L1 |
| 132 | 分料上位传感器冗余不一致 | L1 |
| 133 | 分料下位传感器冗余不一致 | L1 |
| 140~143 | 同上 | L2 |
| 150~153 | 同上 | L3 |
| 160~163 | 同上 | L4 |

## 5. 关联文档

| 文档 | 路径 |
|------|------|
| IFC | 接口文档_IFC-FB1002-SingleLayerConveyor-V6.0.0.md |
| CHG | 变更记录_CHG-FB1002-SingleLayerConveyor-V6.0.0.md |
| UM | 使用说明_UM-FB1002-SingleLayerConveyor-V6.0.0.md |
