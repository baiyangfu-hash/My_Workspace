# 接口文档 FB_1013_NinetyDegreeTransfer

## 0. 文档基础信息

| 属性 | 值 |
|------|-----|
| **文档标题** | FB_1013 九十度转向机构接口定义 |
| **文档版本** | V7.0.0 |
| **关联源码** | actuator/FB_1013_NinetyDegreeTransfer.scl |
| **编制日期** | 2026-05-29 |
| **编制人** | Trae |
| **审核人** | 人工 |
| **遵循规范** | 801_PLC变量命名与功能块命名规范_DEV-V1.0.5, 905_SCL编程规范_DEV-V7.0.0, PLCopen MC Part 1 |
| **重构背景** | 从154网络LD梯形图重构为SCL结构化文本，采用VAR_IN_OUT结构体参数风格，封装升降气缸+旋转电机+取放料机构+多传感器检测的完整90度转角移载控制闭环 |

## 1. 功能概述

**九十度转角移载机构控制块**，封装入料检测 -> 气缸升降 -> 取物动作 -> 电机正转(90度) -> 放物动作 -> 电机反转(90度) -> 气回升 -> 完成通知 的完整多步状态机。

适用于需要将物料从A工位（入料方向）经90度旋转转移至D工位（出料方向）的自动化输送场景，包含5组气缸执行器、1组旋转电机、多路位置传感器和完整的超时/报警诊断体系。

### 1.1 职责边界

| 做什么 | 不做什么 |
|--------|----------|
| 管理11步主状态机(S30~S40)的步进顺序 | 不决定何时启动周期（由编排器/OB1决定） |
| 通过VAR_IN_OUT直连ST_Cylinder控制5组气缸 | 不直接操作物理IO（由OB1映射） |
| 通过VAR_IN_OUT直连ST_ConveyorMotor控制旋转电机 | 不处理变频器参数配置 |
| 监控入料传感器(5路)+到位信号(多路) | 不负责上游来料的节拍协调 |
| 各动作超时计时与报警输出 | 不处理非本机构的报警汇总 |
| 断电保持(NV)状态恢复 | 不管理全局断电保持策略 |

### 1.2 实例化场景

| 场景 | 实例名 | 说明 |
|------|--------|------|
| 主线九十度转向机构 | fbNinetyDeg : FB_1013 | A口入料->90度正转->D口出料->90度反转回原位 |
| 备用转向单元 | fbNinetyDegBackup : FB_1013 | 同构冗余实例，独立步进器 |

### 1.3 机械结构示意

```
          A侧(入料)                          D侧(出料)
    ┌──────────────┐                   ┌──────────────┐
    │  入料检测     │ ──入物机构──→      │              │
    │  (5个传感器)  │                  │  出盘机构      │
    └──────┬───────┘                   └──────┬───────┘
           │                                  │
    ┌──────┴───────┐    旋转台面(90度)   ┌──────┴───────┐
    │   取物机构    │ ←―――――――――――→     │   放物机构    │
    │ (升降+夹取)   │    电机正/反转     │ (升降+释放)   │
    └──────────────┘                   └──────────────┘
           │
    ┌──────┴───────┐
    │  升降气缸     │  (整体升降: 上位=待机/下位=工作)
    │  +摆臂/推板   │
    └──────────────┘
```

## 2. 状态机步序常量

| 常量名 | 值 | 步骤名 | 说明 |
|--------|---|--------|------|
| S30_IDLE | 0 | 待机等待 | 全部复位，等待启动。检查入料、NV恢复 |
| S31_FEED_CHECK | 1 | 入料检测 | 检测5路入料传感器，确认有料 |
| S32_LIFT_DOWN | 2 | 气缸下行 | 升降气缸下降到工作位 |
| S33_PICK_DOWN | 3 | 取物下降 | 取物机构下降到取料高度 |
| S34_PICK_CLAMP | 4 | 取物夹取 | 夹取物料+确认 |
| S35_PICK_UP | 5 | 取物上升 | 取物机构上升收回 |
| S36_MOTOR_FWD | 6 | 电机正转90度 | 旋转台面正向旋转90度(A->D) |
| S37_PLACE_DOWN | 7 | 放物下降 | 放物机构下降到放料高度 |
| S38_PLACE_RELEASE | 8 | 放物释放 | 释放物料+确认 |
| S39_PLACE_UP | 9 | 放物上升 | 放物机构上升收回 |
| S40_MOTOR_REV | 10 | 电机反转90度 | 旋转台面反向旋转90度(D->A回原位) |
| S41_LIFT_UP | 11 | 气缸上行 | 升降气缸上升到待机位 |
| S42_CYCLE_DONE | 12 | 周期完成 | 输出完成信号，等待下一周期 |

## 3. 接口定义

### 3.1 VAR_INPUT (系统控制信号)

| 名称 | 类型 | 默认值 | 有效值域 | 说明 | 来源 |
|------|------|--------|----------|------|------|
| i_bReset | BOOL | FALSE | TRUE/FALSE | 系统复位命令 | OB1←HMI |
| i_bAutoMode | BOOL | FALSE | TRUE/FALSE | 自动模式选择 | OB1←HMI |
| i_bManualMode | BOOL | FALSE | TRUE/FALSE | 手动模式选择 | OB1←HMI |
| i_bStart | BOOL | FALSE | TRUE/FALSE | 启动信号(上升沿触发) | OB1←HMI |
| i_bStop | BOOL | FALSE | TRUE/FALSE | 停止信号(电平有效) | OB1←HMI |
| i_bEnable | BOOL | FALSE | TRUE/FALSE | 使能信号 | 编排器/OB1 |

### 3.2 VAR_INPUT (入料检测传感器)

| 名称 | 类型 | 默认值 | 有效值域 | 说明 | 来源 |
|------|------|--------|----------|------|------|
| i_bFeedDetect0 | BOOL | FALSE | TRUE/FALSE | 入料检测传感器0 | OB1←IO |
| i_bFeedDetect1 | BOOL | FALSE | TRUE/FALSE | 入料检测传感器1 | OB1←IO |
| i_bFeedDetect2 | BOOL | FALSE | TRUE/FALSE | 入料检测传感器2 | OB1←IO |
| i_bFeedDetect3 | BOOL | FALSE | TRUE/FALSE | 入料检测传感器3 | OB1←IO |
| i_bFeedDetect4 | BOOL | FALSE | TRUE/FALSE | 入料检测传感器4 | OB1←IO |

### 3.3 VAR_INPUT (到位/位置传感器)

| 名称 | 类型 | 默认值 | 有效值域 | 说明 | 来源 |
|------|------|--------|----------|------|------|
| i_bPickPlaceDone | BOOL | FALSE | TRUE/FALSE | 取放完成信号(外部确认) | OB1←FB_xxx |
| i_bLiftUpPos | BOOL | FALSE | TRUE/FALSE | 升降气缸上位/上限位 | OB1←IO |
| i_bLiftDownPos | BOOL | FALSE | TRUE/FALSE | 升降气缸下位/下限位 | OB1←IO |
| i_bFwdArrived | BOOL | FALSE | TRUE/FALSE | 正转到位信号 | OB1←IO |
| i_bRevArrived | BOOL | FALSE | TRUE/FALSE | 反转到位信号 | OB1←IO |

### 3.4 VAR_INPUT (工艺参数)

| 名称 | 类型 | 默认值 | 有效值域 | 说明 | 来源 |
|------|------|--------|----------|------|------|
| i_iLiftTimeoutMs | INT | 5000 | 0~60000 | 升降气缸动作超时(ms)，0=关闭 | OB1←HMI |
| i_iPickTimeoutMs | INT | 3000 | 0~60000 | 取物机构动作超时(ms) | OB1←HMI |
| i_iPlaceTimeoutMs | INT | 3000 | 0~60000 | 放物机构动作超时(ms) | OB1←HMI |
| i_iMotorTimeoutMs | INT | 5000 | 0~60000 | 电机旋转超时(ms) | OB1←HMI |
| i_iClampConfirmMs | INT | 500 | 0~5000 | 夹取/释放确认时间(ms) | OB1←HMI |
| i_iCycleDonePulseMs | INT | 500 | 0~2000 | 完成脉冲宽度(ms) | OB1←HMI |

### 3.5 VAR_OUTPUT (气缸/电机直接输出)

| 名称 | 类型 | 默认值 | 有效值域 | 说明 | 去向 |
|------|------|--------|----------|------|------|
| q_bOutputReset | BOOL | FALSE | TRUE/FALSE | 复位输出(全部清零) | OB1→IO |
| q_bCylinderUp | BOOL | FALSE | TRUE/FALSE | 升降气缸-上升 | OB1→IO |
| q_bCylinderDown | BOOL | FALSE | TRUE/FALSE | 升降气缸-下降 | OB1→IO |
| q_bPickUp | BOOL | FALSE | TRUE/FALSE | 取物机构-上升 | OB1→IO |
| q_bPickDown | BOOL | FALSE | TRUE/FALSE | 取物机构-下降 | OB1→IO |
| q_bPlaceUp | BOOL | FALSE | TRUE/FALSE | 入物/放物机构-上升 | OB1→IO |
| q_bPlaceDown | BOOL | FALSE | TRUE/FALSE | 入物/放物机构-下降 | OB1→IO |
| q_bSwingArmDown | BOOL | FALSE | TRUE/FALSE | 摆臂下降 | OB1→IO |
| q_bPushPlateUp | BOOL | FALSE | TRUE/FALSE | 推板上升 | OB1→IO |
| q_bPushPlateDown | BOOL | FALSE | TRUE/FALSE | 推板下降 | OB1→IO |
| q_bMotorFwd | BOOL | FALSE | TRUE/FALSE | 旋转电机-正向 | OB1→IO |
| q_bMotorRev | BOOL | FALSE | TRUE/FALSE | 旋转电机-反向 | OB1→IO |

### 3.6 VAR_OUTPUT (状态指示输出)

| 名称 | 类型 | 默认值 | 有效值域 | 说明 | 去向 |
|------|------|--------|----------|------|------|
| q_bPickDone | BOOL | FALSE | TRUE/FALSE | 取物完成信号 | 编排器/HMI |
| q_bPlaceDone | BOOL | FALSE | TRUE/FALSE | 放物完成信号 | 编排器/HMI |
| q_bWaitState1 | BOOL | FALSE | TRUE/FALSE | 等待状态1 | HMI |
| q_bTrayIn | BOOL | FALSE | TRUE/FALSE | 出盘进入信号 | 编排器 |
| q_bCylinderAtTop | BOOL | FALSE | TRUE/FALSE | 气缸在上位 | 编排器/HMI |
| q_bCylinderAtBottom | BOOL | FALSE | TRUE/FALSE | 气缸在下位 | 编排器/HMI |
| q_bPickAtTop | BOOL | FALSE | TRUE/FALSE | 取物机构在上位 | 编排器/HMI |
| q_bPickAtBottom | BOOL | FALSE | TRUE/FALSE | 取物机构在下位 | 编排器/HMI |
| q_bPickUpDone | BOOL | FALSE | TRUE/FALSE | 取物上升完成 | 编排器 |
| q_bSwingArmUpDone | BOOL | FALSE | TRUE/FALSE | 摆臂上升完成 | 编排器 |
| q_bPosA_Picker | BOOL | FALSE | TRUE/FALSE | A位置-取物者 | HMI |
| q_bPosA_Feeder | BOOL | FALSE | TRUE/FALSE | A位置-入物者 | HMI |
| q_bPosA | BOOL | FALSE | TRUE/FALSE | A位置信号 | HMI |
| q_bPosAO | BOOL | FALSE | TRUE/FALSE | AO位置信号 | HMI |
| q_bPosO | BOOL | FALSE | TRUE/FALSE | O位置信号 | HMI |
| q_bPosOD | BOOL | FALSE | TRUE/FALSE | OD位置信号 | HMI |
| q_bPosD | BOOL | FALSE | TRUE/FALSE | D位置信号 | HMI |
| q_bA_InputHasMaterial | BOOL | FALSE | TRUE/FALSE | A输入有否(有料) | HMI |
| q_bInputA_HasMaterial | BOOL | FALSE | TRUE/FALSE | 输入A有否(有料) | HMI |
| q_bCPortIn_HasMaterial | BOOL | FALSE | TRUE/FALSE | C口入有否(有料) | HMI |

### 3.7 VAR_OUTPUT (中间状态/断电保持)

| 名称 | 类型 | 默认值 | 有效值域 | 说明 | 去向 |
|------|------|--------|----------|------|------|
| q_bM0 ~ q_bM10 | BOOL | FALSE | TRUE/FALSE | 中间状态M0~M10(步进暂存/互锁标志) | 编排器/调试 |
| q_bNV_Retain1 | BOOL | FALSE | TRUE/FALSE | 断电保持状态1(保留步进上下文) | 内部/NV区 |
| q_bNV_Retain2 | BOOL | FALSE | TRUE/FALSE | 断电保持状态2 | 内部/NV区 |
| q_bNV_Retain3 | BOOL | FALSE | TRUE/FALSE | 断电保持状态3 | 内部/NV区 |

### 3.8 VAR_OUTPUT (报警/错误输出)

| 名称 | 类型 | 默认值 | 有效值域 | 说明 | 去向 |
|------|------|--------|----------|------|------|
| q_bAlarm0 ~ q_bAlarm10 | BOOL | FALSE | TRUE/FALSE | 报警输出0~10 | OB1→FB_2001/HMI |
| q_bError1 ~ q_bError5 | BOOL | FALSE | TRUE/FALSE | 错误输出1~5 | OB1→FB_2001/HMI |

### 3.9 VAR_OUTPUT (PLCopen标准状态)

| 名称 | 类型 | 默认值 | 有效值域 | 说明 | 去向 |
|------|------|--------|----------|------|------|
| q_iCurrentStep | INT | 0 | 0~12 | 当前步序号(S30~S42对应0~12) | OB1→HMI |
| q_bBusy | BOOL | FALSE | TRUE/FALSE | 功能块忙(运行中) | 编排器 |
| q_bDone | BOOL | FALSE | TRUE/FALSE | 单周期完成(脉冲) | 编排器 |
| q_bError | BOOL | FALSE | TRUE/FALSE | 错误发生 | 编排器→FB_2001 |
| q_iErrorID | INT | 0 | 报警码 | 当前错误ID(见报警码表) | OB1→FB_2001 |

### 3.10 VAR_IN_OUT (结构体参数, V7.0核心)

| 名称 | 类型 | 说明 | OB1接线 |
|------|------|------|---------|
| io_stMainCylinder | ST_Cylinder | 主升降气缸结构体 - 直读直写 | => astCylinder[1] |
| io_stPickCylinder | ST_Cylinder | 取物升降气缸结构体 - 直读直写 | => astCylinder[2] |
| io_stPlaceCylinder | ST_Cylinder | 放物升降气缸结构体 - 直读直写 | => astCylinder[3] |
| io_stSwingArmCyl | ST_Cylinder | 摆臂气缸结构体 - 直读直写 | => astCylinder[4] |
| io_stPushPlateCyl | ST_Cylinder | 推板气缸结构体 - 直读直写 | => astCylinder[5] |
| io_stRotateMotor | ST_ConveyorMotor | 旋转电机结构体 - 直读直写 | => astMotor[1] |

**ST_Cylinder 子字段访问路径 (V1.1.0)**:

| 子字段 | FB内用途 | 语义映射 |
|--------|---------|---------|
| `.Extend` | 伸出命令写入 | 升降→下降 / 取物→下降 / 放物→下降 / 摆臂→下 / 推板→降 |
| `.Retract` | 收回命令写入 | 升降→上升 / 取物→上升 / 放物→上升 / 摆臂→上 / 推板→升 |
| `.ExtendedPos` | 伸出位读取 | 下位 / 工作点 / 夹紧位 |
| `.RetractedPos` | 收回位读取 | 上位 / 原点 / 松开位 |
| `.TimeoutMs` | 超时参数读写 | 各气缸独立超时 |
| `.IsExtended` | 已伸出到位输出 | → 对应q_bXxxAtBottom等 |
| `.IsRetracted` | 已收回到位输出 | → 对应q_bXxxAtTop等 |
| `.Timeout` | 超时报警输出 | → 汇总至q_bError |
| `.SensorFault` | 传感器冲突输出 | → 汇总至q_bError |

**ST_ConveyorMotor 子字段访问路径 (V1.1.0)**:

| 子字段 | FB内用途 | 语义映射 |
|--------|---------|---------|
| `.FwdCmd` | 正转命令写入 | 90度正转(A→D) |
| `.RevCmd` | 反转命令写入 | 90度反转(D→A) |
| `.SafetyDoorOk` | 安全门状态读取 | 旋转安全互锁 |
| `.VfdFault` | 变频器故障读取 | 电机故障检测 |
| `.Speed` | 速度设定读写 | 旋转速度 |
| `.FwdOut` | 正转实际输出 | → q_bMotorFwd |
| `.RevOut` | 反转实际输出 | → q_bMotorRev |
| `.Running` | 运行中状态 | → 状态指示 |
| `.VfdAlarm` | VFD报警输出 | → q_bError |

## 4. 行为逻辑

### 4.1 正常运行周期

```
完整周期流程 (S30 → S42):

S30_IDLE (待机)
  ├── 检查NV恢复断电前状态
  ├── 检查气缸在上位? 否则先回原点
  ├── 等待 i_bStart 上升沿
  └── [启动] → S31

S31_FEED_CHECK (入料检测)
  ├── 检测 i_bFeedDetect0~4 任一ON?
  ├── 有料 → S32
  └── 无料 → 等待(可配超时) 或 报警

S32_LIFT_DOWN (气缸下行)
  ├── io_stMainCylinder.Extend := TRUE   (* 下降 *)
  ├── 等待 ExtendedPos=TRUE (下位到位)
  ├── 超时 → Alarm(升降超时)
  └── 到位 → S33

S33_PICK_DOWN (取物下降)
  ├── io_stPickCylinder.Extend := TRUE    (* 下降 *)
  ├── 等待 ExtendedPos=TRUE
  ├── 超时 → Alarm(取物超时)
  └── 到位 → S34

S34_PICK_CLAMP (取物夹取)
  ├── 执行夹取动作 (电磁阀输出)
  ├── 等待 i_iClampConfirmMs 确认时间
  ├── 确认到位 → S35
  └── 失败 → Alarm(夹取失败)

S35_PICK_UP (取物上升)
  ├── io_stPickCylinder.Retract := TRUE   (* 上升 *)
  ├── 等待 RetractedPos=TRUE
  ├── q_bPickUpDone := TRUE
  └── 到位 → S36

S36_MOTOR_FWD (电机正转90度)
  ├── io_stRotateMotor.FwdCmd := TRUE
  ├── 等待 i_bFwdArrived=TRUE OR FwdOut持续+到位判断
  ├── 超时 → Alarm(正转超时)
  └── 到位 → S37

S37_PLACE_DOWN (放物下降)
  ├── io_stPlaceCylinder.Extend := TRUE   (* 下降 *)
  ├── 等待 ExtendedPos=TRUE
  └── 到位 → S38

S38_PLACE_RELEASE (放物释放)
  ├── 执行释放动作 (电磁阀输出)
  ├── 等待 i_iClampConfirmMs 确认时间
  ├── q_bPlaceDone := TRUE
  └── 确认到位 → S39

S39_PLACE_UP (放物上升)
  ├── io_stPlaceCylinder.Retract := TRUE   (* 上升 *)
  ├── 等待 RetractedPos=TRUE
  └── 到位 → S40

S40_MOTOR_REV (电机反转90度)
  ├── io_stRotateMotor.RevCmd := TRUE
  ├── 等待 i_bRevArrived=TRUE
  ├── 超时 → Alarm(反转超时)
  └── 到位 → S41

S41_LIFT_UP (气缸上行)
  ├── io_stMainCylinder.Retract := TRUE   (* 上升 *)
  ├── 等待 RetractedPos=TRUE (上位到位)
  └── 到位 → S42

S42_CYCLE_DONE (周期完成)
  ├── q_bDone := TRUE  (脉冲输出)
  ├── q_bBusy := FALSE
  └── → S30_IDLE (等待下一周期)
```

### 4.2 停止处理

```
当 i_bStop=TRUE 且 q_bBusy=TRUE 时:
  → 当前步骤立即停止所有输出
  → 气缸命令全部清除 (Extend:=FALSE, Retract:=FALSE)
  → 电机命令清除 (FwdCmd:=FALSE, RevCmd:=FALSE)
  → 记录当前步序到NV(断电保持)
  → q_bBusy := FALSE
  → q_bError := FALSE  (停止≠错误, 可恢复)
  → 步序不归零 (支持从断点恢复)
```

### 4.3 复位处理

```
当 i_bReset=TRUE 时:
  → 所有输出强制清零 (q_bOutputReset := TRUE)
  → 6个ST_Cylinder/ST_ConveyorMotor内部状态清除
  → 步进器归零 (iCurrentStep := S30_IDLE)
  → 所有报警/错误清零
  → NV状态清除
  → q_bBusy := FALSE; q_bDone := FALSE; q_bError := FALSE
```

### 4.4 超时处理

```
每个动作步骤配有独立超时定时器:
  → 超时到达且尚未到位:
    - 对应 Alarmx := TRUE (锁存)
    - q_bError := TRUE
    - q_iErrorID := 对应报警码
    - 当前动作输出保持(不强制改变,由编排器决策)
    - 步序暂停(停在当前步,等待人工干预或复位)
```

### 4.5 手动模式

```
i_bManualMode=TRUE 时:
  → 状态机暂停 (iCurrentStep 保持不变, q_bBusy:=FALSE)
  → 各气缸/电机响应独立手动命令
  → 直接映射手动按钮→输出 (通过ST_Cylinder/ST_ConveyorMotor)
  → 安全互锁仍然生效
```

## 5. 接口交互协议

```
编排器/OB1                         FB_1013_NinetyDegreeTransfer
     │                                      │
     │── i_bStart := TRUE(沿) ──────────────→│  触发新周期
     │                                      │  S30→S31→...→S42
     │                                      │  (自动步进)
     │                                      │
     │←── q_bBusy := TRUE ─────────────────│  (运行中)
     │                                      │
     │←── q_bDone := TRUE(脉冲) ───────────│  (周期完成)
     │                                      │
     │── i_bStart := TRUE(沿) ──────────────→│  下一周期...
     │                                      │
     │── i_bStop := TRUE ──────────────────→│  停止
     │←── q_bBusy := FALSE ────────────────│
     │                                      │
     │── i_bReset := TRUE ─────────────────→│  复位
     │←── q_bOutputReset := TRUE ──────────│  全部清零
     │                                      │
     │  [io_stMainCylinder] ─── VAR_IN_OUT ──│  气缸直连
     │  [io_stRotateMotor]  ─── VAR_IN_OUT ──│  电机直连
```

## 6. 报警码定义

| 码 | 含义 | 触发步骤 | 触发条件 | 输出映射 |
|:--:|------|:-------:|----------|---------|
| 130 | 升降气缸下行超时 | S32 | tLiftDownTimeout.Q AND NOT ExtendedPos | q_bAlarm0, q_bError1 |
| 131 | 升降气缸上行超时 | S41 | tLiftUpTimeout.Q AND NOT RetractedPos | q_bAlarm1, q_bError1 |
| 132 | 取物下降超时 | S33 | tPickDownTimeout.Q AND NOT ExtendedPos | q_bAlarm2, q_bError2 |
| 133 | 取物上升超时 | S35 | tPickUpTimeout.Q AND NOT RetractedPos | q_bAlarm2, q_bError2 |
| 134 | 取物夹取失败/超时 | S34 | tClampPickConfirm.Q OR 确认信号未到 | q_bAlarm3, q_bError2 |
| 135 | 电机正转超时(90度) | S36 | tMotorFwdTimeout.Q AND NOT FwdArrived | q_bAlarm4, q_bError3 |
| 136 | 电机反转超时(90度) | S40 | tMotorRevTimeout.Q AND NOT RevArrived | q_bAlarm4, q_bError3 |
| 137 | 放物下降超时 | S37 | tPlaceDownTimeout.Q AND NOT ExtendedPos | q_bAlarm5, q_bError4 |
| 138 | 放物上升超时 | S39 | tPlaceUpTimeout.Q AND NOT RetractedPos | q_bAlarm5, q_bError4 |
| 139 | 放物释放失败/超时 | S38 | tClampPlaceConfirm.Q OR 确认信号未到 | q_bAlarm6, q_bError4 |
| 140 | 入料检测超时/无料 | S31 | tFeedTimeout.Q AND 全部FeedDetect=FALSE | q_bAlarm7, q_bError5 |
| 141 | 传感器冲突(气缸) | 任意 | ST_Cylinder.SensorFault=ANY | q_bAlarm8, Error汇总 |
| 142 | 电机/VFD故障 | S36/S40 | ST_ConveyorMotor.VfdFault=TRUE | q_bAlarm9, q_bError3 |
| 143 | 急停/安全门触发 | 任意 | SafetyDoorOk=FALSE 且运行中 | q_bAlarm10, q_bError5 |

> **说明**: Alarm0~Alarm10 为原始报警位输出，Error1~Error5 为分类错误汇总。`q_iErrorID` 输出最新报警码数值供FB_2001统一采集。

## 7. 接口统计

| 项目 | 数量 | 说明 |
|------|:----:|------|
| VAR_INPUT (系统控制) | 6 | Reset/Auto/Manual/Start/Stop/Enable |
| VAR_INPUT (传感器) | 8 | 5路入料+3路到位 |
| VAR_INPUT (工艺参数) | 6 | 5个超时+1个确认时间 |
| **VAR_INPUT 合计** | **20** | |
| VAR_OUTPUT (驱动输出) | 12 | 气缸11+电机2(共享计数) |
| VAR_OUTPUT (状态指示) | 26 | 位置/中间/NV状态 |
| VAR_OUTPUT (报警错误) | 16 | Alarm0-10 + Error1-5 |
| VAR_OUTPUT (PLCopen) | 5 | Step/Busy/Done/Error/ErrorID |
| **VAR_OUTPUT 合计** | **59** | |
| VAR_IN_OUT (结构体) | **6** | 5xST_Cylinder + 1xST_ConveyorMotor |
| **总计** | **85** | |

## 8. 关联文档

| 文档 | 路径 | 版本 |
|------|------|:----:|
| DSN | 详细设计说明书_DSN-FB1013-NinetyDegreeTransfer-V7.0.0.md | V7.0.0 |
| 气缸控制 IFC | 接口文档_IFC-FB1011-CylinderControl-V7.0.0.md | V7.0.0 |
| 电机控制 IFC | 接口文档_IFC-FB1012-ConveyorMotor-V7.0.0.md | V7.0.0 |
| ST_Cylinder类型 | ../../types/ST_Cylinder.scl | V1.1.0 |
| ST_ConveyorMotor类型 | ../../types/ST_ConveyorMotor.scl | V1.1.0 |
| 取放料机构 IFC | ../../../../DJ-2026-005/02_PLC程序/通用ST程序及变量表/pickplace/PRD/接口文档_IFC-FB1003-PickPlace-V7.0.0.md | V7.0.0 |
| 规范 | ../../../../../01_需求与设计/10_编程及变量规范/801_PLC变量命名与功能块命名规范_DEV-V1.0.5.md | V1.0.5 |
| 905规范 | ../../../../../01_需求与设计/10_编程及变量规范/905_SCL编程规范_DEV-V7.0.0.md | V7.0.0 |
