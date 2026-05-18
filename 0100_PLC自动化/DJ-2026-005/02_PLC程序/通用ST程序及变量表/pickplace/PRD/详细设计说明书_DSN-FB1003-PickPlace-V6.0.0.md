# 详细设计说明书 FB_1003_PickPlace_BufferFraming

## 0. 文档基础信息

| 属性 | 值 |
|------|-----|
| **文档标题** | FB_1003 取放料机构详细设计 |
| **文档版本** | V6.0.0 |
| **关联源码** | pickplace/FB_1003_PickPlace_BufferFraming.scl |
| **编制日期** | 2026-05-17 |
| **编制人** | Trae |
| **遵循规范** | 801_DEV-V1.0.5, 810_DEV-V1.0.2 |
| **数据来源** | 源程序功能基线_SRC-DJ-2026-005-V1.0.0 |

## 1. 设计原则

1. **6步STL S20~S25**：与源程序完全一致，产品检测在S22步内完成
2. **按层选择放料点**：L1/L3→前放料点D520，L2/L4→后放料点D540
3. **4组夹爪同时动作**：前夹紧/后夹紧/前夹紧2/后夹紧2，全部确认后跳步
4. **轴命令通过接口发出**：Z轴/X1轴的MoveAbs/Home命令通过q_bXxxRequest/q_rTargetPos输出，由外部轴FB执行

## 2. 状态机伪代码

```
CASE q_iCurrentState OF

  S20_IDLE: (* 0 - 待机 *)
    q_bZAxisMoveAbsReq := FALSE;
    q_bX1AxisMoveAbsReq := FALSE;
    IF bPickupRequested THEN
      bPickupRequested := FALSE;
      q_iCurrentState := S21_UP_TO_PICK;
    END_IF;

  S21_UP_TO_PICK: (* 1 - Z→取片教点D514 *)
    IF NOT bStep21Armed THEN
      q_rZAxisTargetPos := rPickupTeachPos;   (* D514 *)
      q_bZAxisMoveAbsReq := TRUE;
      bStep21Armed := TRUE;
    END_IF;
    IF i_bZAxisInPos THEN
      bStep21Armed := FALSE;
      q_iCurrentState := S22_CLAMP_AND_DETECT;
    END_IF;

  S22_CLAMP_AND_DETECT: (* 2 - 夹紧+产品检测 *)
    IF NOT bStep22Armed THEN
      q_bFrontClamp := TRUE;      (* 前+后+前2+后2同时夹紧 *)
      q_bRearClamp := TRUE;
      q_bFrontClamp2 := TRUE;
      q_bRearClamp2 := TRUE;
      tClampConfirm(IN := TRUE, PT := INT_TO_TIME(i_iClampConfirmTime));
      bStep22Armed := TRUE;
    END_IF;
    (* 4夹紧全确认 + 4光电全ON *)
    IF i_bFrontClampClosed AND i_bRearClampClosed
       AND i_bFrontClamp2Closed AND i_bRearClamp2Closed
       AND i_bLongEdge1Detect AND i_bLongEdge2Detect
       AND i_bShortEdge1Detect AND i_bShortEdge2Detect THEN
      bStep22Armed := FALSE;
      q_iCurrentState := S23_MOVE_TO_PLACE;
    END_IF;
    (* 夹紧确认超时？*)
    IF tClampConfirm.Q THEN
      q_iAlarmCode := 101;  (* 夹紧超时 *)
    END_IF;

  S23_MOVE_TO_PLACE: (* 3 - X1→放料点 *)
    IF NOT bStep23Armed THEN
      q_bZAxisMoveAbsReq := FALSE;
      (* 按层选放料点: L1/L3→前D520, L2/L4→后D540 *)
      IF (i_iPickLayer = 1) OR (i_iPickLayer = 3) THEN
        q_rX1AxisTargetPos := rFrontPlacePos;  (* D520 *)
      ELSE
        q_rX1AxisTargetPos := rRearPlacePos;   (* D540 *)
      END_IF;
      q_bX1AxisMoveAbsReq := TRUE;
      bStep23Armed := TRUE;
    END_IF;
    IF i_bX1AxisInPos THEN
      bStep23Armed := FALSE;
      q_iCurrentState := S24_DOWN_TO_PLACE;
    END_IF;

  S24_DOWN_TO_PLACE: (* 4 - Z→放片教点D524 *)
    IF NOT bStep24Armed THEN
      q_rZAxisTargetPos := rPlaceTeachPos;     (* D524 *)
      q_bZAxisMoveAbsReq := TRUE;
      bStep24Armed := TRUE;
    END_IF;
    IF i_bZAxisInPos THEN
      bStep24Armed := FALSE;
      q_iCurrentState := S25_UNCLAMP_AND_NOTIFY;
    END_IF;

  S25_UNCLAMP_AND_NOTIFY: (* 5 - 松开+通知 *)
    q_bFrontClamp := FALSE;
    q_bRearClamp := FALSE;
    q_bFrontClamp2 := FALSE;
    q_bRearClamp2 := FALSE;
    IF i_bFrontClampOpened AND i_bRearClampOpened
       AND i_bFrontClamp2Opened AND i_bRearClamp2Opened THEN
      q_bPlaceDoneToFeeder := TRUE;  (* 放料完成脉冲→FB_1004 *)
      q_iCurrentState := S20_IDLE;
    END_IF;

END_CASE;
```

## 3. 报警码

| 码 | 含义 |
|:--:|------|
| 101 | 夹紧确认超时 |
| 102 | 升降动作超时 |
| 103 | 产品检测失败(取料空) |
| 104 | Z轴限位触发 |
| 105 | X1轴限位触发 |
| 106 | Z轴伺服故障 |
| 107 | X1轴伺服故障 |
| 108 | 夹紧传感器冗余不一致 |
| 109 | 升降传感器冗余不一致 |

## 4. 关联文档

| 文档 | 路径 |
|------|------|
| IFC | 接口文档_IFC-FB1003-PickPlace-V6.0.0.md |
| CHG | 变更记录_CHG-FB1003-PickPlace-V6.0.0.md |
| UM | 使用说明_UM-FB1003-PickPlace-V6.0.0.md |
