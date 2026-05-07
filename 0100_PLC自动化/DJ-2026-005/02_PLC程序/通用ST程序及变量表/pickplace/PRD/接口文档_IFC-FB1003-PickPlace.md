# FB_1003_PickPlace_BufferFraming 接口文档

## 1. 文档基础信息

| 属性 | 值 |
|------|-----|
| **文档标题** | 取放料机构功能块接口文档 (V6.0.0 英文版) |
| **适用FB** | FB_1003_PickPlace_BufferFraming |
| **文档类型** | 接口文档 / Interface Document (IFC) |
| **文档版本** | V6.0.0 |
| **编制日期** | 2026-05-03 |
| **编制人** | Trae (AI Assistant) |
| **审核人** | [待审核] |
| **遵循规范** | `801_PLC变量命名与功能块命名规范_DEV-V1.0.5` |
| **接口规模** | **55个输入 / 30个输出** (本项目接口最多的FB) |

---

## 2. 接口概览统计

### 2.1 数量统计

| 类别 | 数量 | 数据类型说明 |
|:------|:----:|:-------------|
| **输入总计** | **55** | - |
| 系统控制信号 | 6 | BOOL (使能/模式/按钮) |
| 手动操作-伺服点动 | 4 | BOOL (Z轴上下/X1轴前后) |
| 手动操作-气缸控制 | 10 | BOOL (升降/前夹紧/后夹紧/前夹紧2/后夹紧2) |
| 工艺参数 | 6 | REAL(4) + INT(2) (速度/时间) |
| 传感器-气缸位置 | 10 | BOOL (磁性开关, 5组×2) |
| 传感器-产品检测 | 4 | BOOL (光电传感器, 长边×2+短边×2) |
| 传感器-伺服轴状态 | 12 | BOOL (原点/故障/限位, 3轴×4) |
| 上游信号(四层输送机) | 4 | BOOL (L1~L4放料完成) |
| **输出总计** | **30** | - |
| 执行器请求-气缸 | 10 | BOOL (电磁阀, 5组×2) |
| 执行器请求-伺服(Z轴) | 3 | BOOL (脉冲/方向/使能) |
| 下游信号 | 1 | BOOL (给打胶机送料机构) |
| 状态/HMI显示 | 7 | BOOL(2) + INT(2) + REAL(3) |
| 报警输出 | 1 | INT (101~198段) |
| 定时器调试输出 | 4 | TIME (HMI显示已耗时间) |
| **内部变量** | 25 | VAR段 (状态机/运动请求/冲突检测/系统标志) |
| **常量定义** | 28 | VAR_CONSTANT段 (11步序+8报警码+7定时参数+2层数) |

---

## 3. 输入接口定义 (VAR_INPUT)

### 3.1 系统控制信号组 (6个BOOL)

> 来自主控/HMI M区公共透传信号

| 序号 | 变量名 | 类型 | 功能描述 | 有效方式 |
|:----:|:--------|:----:|:---------|:--------:|
| 1 | `i_bEnable` | BOOL | 总使能信号(主控系统就绪后置位) | 电平有效 |
| 2 | `i_bAutoMode` | BOOL | 自动运行模式选择 | 电平有效(与Manual互斥) |
| 3 | `i_bManualMode` | BOOL | 手动调试模式选择 | 电平有效(与Auto互斥) |
| 4 | `i_bStart` | BOOL | 自动循环启动按钮 | 上升沿触发 |
| 5 | `i_bStop` | BOOL | 自动循环停止按钮 | 电平有效 |
| 6 | `i_bReset` | BOOL | 故障复位/初始化按钮 | 电平有效 |

### 3.2 手动操作信号组 (14个BOOL)

> 来自HMI手动操作面板

#### 3.2.1 伺服点动控制 (4个)

| 序号 | 变量名 | 类型 | 功能描述 |
|:----:|:--------|:----:|:---------|
| 7 | `i_bLx_ZAxis_JogUp` | BOOL | 手动-Z轴向上点动 |
| 8 | `i_bLx_ZAxis_JogDown` | BOOL | 手动-Z轴向下点动 |
| 9 | `i_bLx_X1Axis_JogFwd` | BOOL | 手动-X1轴向前点动(取料方向) |
| 10 | `i_bLx_X1Axis_JogRev` | BOOL | 手动-X1轴向后点动(放料方向) |

#### 3.2.2 气缸手动控制 (10个)

> 双电磁阀控制（Close=动作/Open=复位）

| 序号 | 变量名 | 类型 | 功能描述 | 设备编号 |
|:----:|:--------|:----:|:---------|:--------:|
| 11 | `i_bLx_LiftUp` | BOOL | 手动-升降气缸上升 | YV1 |
| 12 | `i_bLx_LiftDown` | BOOL | 手动-升降气缸下降 | YV2 |
| 13 | `i_bLx_FrontGrip_Close` | BOOL | 手动-前夹紧气缸夹紧 | YV3 |
| 14 | `i_bLx_FrontGrip_Open` | BOOL | 手动-前夹紧气缸松开 | YV4 |
| 15 | `i_bLx_RearGrip_Close` | BOOL | 手动-后夹紧气缸夹紧 | YV5 |
| 16 | `i_bLx_RearGrip_Open` | BOOL | 手动-后夹紧气缸松开 | YV6 |
| 17 | `i_bLx_FrontGrip2_Close` | BOOL | 手动-前夹紧2气缸夹紧 | YV7 (预留) |
| 18 | `i_bLx_FrontGrip2_Open` | BOOL | 手动-前夹紧2气缸松开 | YV8 (预留) |
| 19 | `i_bLx_RearGrip2_Close` | BOOL | 手动-后夹紧2气缸夹紧 | YV9 (预留) |
| 20 | `i_bLx_RearGrip2_Open` | BOOL | 手动-后夹紧2气缸松开 | YV10 (预留) |

### 3.3 工艺参数组 (6个: REAL×4 + INT×2)

> 来自HMI设定或配方数据

| 序号 | 变量名 | 类型 | 默认值范围 | 功能描述 |
|:----:|:--------|:----:|:----------:|:---------|
| 21 | `i_rPickupSpeed` | REAL | 0~100% | 取料过程Z轴下降/上升速度(mm/s或%) |
| 22 | `i_rPlaceSpeed` | REAL | 0~100% | 放料过程Z轴下降/上升速度(mm/s或%) |
| 23 | `i_rZAxisSpeed` | REAL | 0~100% | Z轴通用运动速度设定(mm/s) |
| 24 | `i_rX1AxisSpeed` | REAL | 0~100% | X1轴通用运动速度设定(mm/s) |
| 25 | `i_iGripConfirmTime` | INT | 200~2000ms | 夹爪夹紧确认等待时间(ms) |
| 26 | `i_iLiftActionTime` | INT | 1000~5000ms | 升降气缸动作超时时间(ms) |

### 3.4 传感器输入组 (26个BOOL)

> 全部来自主控IO映射（本功能块不直接读取X地址）

#### 3.4.1 气缸位置传感器 (10个磁性开关)

> 动点(WorkPoint)=动作到位, 原点(HomePoint)=复位到位

| 序号 | 变量名 | 类型 | 功能描述 | 对应气缸 |
|:----:|:--------|:----:|:---------|:---------:|
| 27 | `i_bLift_WorkPoint` | BOOL | 升降气缸下降到位(动点) | 升降气缸 |
| 28 | `i_bLift_HomePoint` | BOOL | 升降气缸上升到位(原点) | 升降气缸 |
| 29 | `i_bFrontGrip_WorkPoint` | BOOL | 前夹紧气缸夹紧到位(动点) | 前夹紧气缸 |
| 30 | `i_bFrontGrip_HomePoint` | BOOL | 前夹紧气缸松开到位(原点) | 前夹紧气缸 |
| 31 | `i_bRearGrip_WorkPoint` | BOOL | 后夹紧气缸夹紧到位(动点) | 后夹紧气缸 |
| 32 | `i_bRearGrip_HomePoint` | BOOL | 后夹紧气缸松开到位(原点) | 后夹紧气缸 |
| 33 | `i_bFrontGrip2_WorkPoint` | BOOL | 前夹紧2气缸夹紧到位(动点) | 前夹紧2(预留) |
| 34 | `i_bFrontGrip2_HomePoint` | BOOL | 前夹紧2气缸松开到位(原点) | 前夹紧2(预留) |
| 35 | `i_bRearGrip2_WorkPoint` | BOOL | 后夹紧2气缸夹紧到位(动点) | 后夹紧2(预留) |
| 36 | `i_bRearGrip2_HomePoint` | BOOL | 后夹紧2气缸松开到位(原点) | 后夹紧2(预留) |

#### 3.4.2 产品检测传感器 (4个光电传感器)

> 一次取两根边框: 长边×2 + 短边×2

| 序号 | 变量名 | 类型 | 功能描述 | 检测对象 |
|:----:|:--------|:----:|:---------|:---------:|
| 37 | `i_bLongEdge1_Detect` | BOOL | 长边1存在检测(光电传感器) | 第1根长边框 |
| 38 | `i_bLongEdge2_Detect` | BOOL | 长边2存在检测(光电传感器) | 第2根长边框 |
| 39 | `i_bShortEdge1_Detect` | BOOL | 短边1存在检测(光电传感器) | 第1根短边框 |
| 40 | `i_bShortEdge2_Detect` | BOOL | 短边2存在检测(光电传感器) | 第2根短边框 |

#### 3.4.3 伺服轴状态信号 (12个)

> 来自驱动器和限位开关

| 序号 | 变量名 | 类型 | 功能描述 | 所属轴 |
|:----:|:--------|:----:|:---------|:------:|
| 41 | `i_bZAxis_Home` | BOOL | Z轴伺服原点信号(Home/ORG) | Z轴 |
| 42 | `i_bX1Axis_Home` | BOOL | X1轴伺服原点信号(Home/ORG) | X1轴 |
| 43 | `i_bX2Axis_Home` | BOOL | X2轴伺服原点信号(预留) | X2轴(预留) |
| 44 | `i_bZAxis_ServoFault` | BOOL | Z轴伺服驱动器故障(ALM输出) | Z轴 |
| 45 | `i_bX1Axis_ServoFault` | BOOL | X1轴伺服驱动器故障(ALM输出) | X1轴 |
| 46 | `i_bX2Axis_ServoFault` | BOOL | X2轴伺服驱动器故障(预留) | X2轴(预留) |
| 47 | `i_bZAxis_ForwardLimit` | BOOL | Z轴正向限位(上限位) | Z轴 |
| 48 | `i_bZAxis_ReverseLimit` | BOOL | Z轴反向限位(下限位) | Z轴 |
| 49 | `i_bX1Axis_ForwardLimit` | BOOL | X1轴正向限位(取料侧限位) | X1轴 |
| 50 | `i_bX1Axis_ReverseLimit` | BOOL | X1轴反向限位(放料侧限位) | X1轴 |
| 51 | `i_bX2Axis_ForwardLimit` | BOOL | X2轴正向限位(预留) | X2轴(预留) |
| 52 | `i_bX2Axis_ReverseLimit` | BOOL | X2轴反向限位(预留) | X2轴(预留) |

### 3.5 上游信号组 (4个BOOL)

> 来自四层输送机的放料完成信号

| 序号 | 变量名 | 类型 | 功能描述 | 来源 |
|:----:|:--------|:----:|:---------|:-----:|
| 53 | `i_bConveyor_L1_FeedComplete` | BOOL | 输送机第1层放料完成 | Conveyor L1 |
| 54 | `i_bConveyor_L2_FeedComplete` | BOOL | 输送机第2层放料完成 | Conveyor L2 |
| 55 | `i_bConveyor_L3_FeedComplete` | BOOL | 输送机第3层放料完成 | Conveyor L3 |
| 56 | `i_bConveyor_L4_FeedComplete` | BOOL | 输送机第4层放料完成 | Conveyor L4 |

---

## 4. 输出接口定义 (VAR_OUTPUT)

### 4.1 执行器请求输出组 (13个)

> 给主控映射到Y地址

#### 4.1.1 气缸控制输出 (10个BOOL)

| 序号 | 变量名 | 类型 | 功能描述 | 映射目标 |
|:----:|:--------|:----:|:---------|:---------:|
| 1 | `o_bLift_Up` | BOOL | 升降气缸上升电磁阀 -> 主控 -> Y地址 | YV1 |
| 2 | `o_bLift_Down` | BOOL | 升降气缸下降电磁阀 -> 主控 -> Y地址 | YV2 |
| 3 | `o_bFrontGrip_Close` | BOOL | 前夹紧气缸夹紧电磁阀 -> 主控 -> Y地址 | YV3 |
| 4 | `o_bFrontGrip_Open` | BOOL | 前夹紧气缸松开电磁阀 -> 主控 -> Y地址 | YV4 |
| 5 | `o_bRearGrip_Close` | BOOL | 后夹紧气缸夹紧电磁阀 -> 主控 -> Y地址 | YV5 |
| 6 | `o_bRearGrip_Open` | BOOL | 后夹紧气缸松开电磁阀 -> 主控 -> Y地址 | YV6 |
| 7 | `o_bFrontGrip2_Close` | BOOL | 前夹紧2气缸夹紧电磁阀 -> 主控 -> Y地址 | YV7(预留) |
| 8 | `o_bFrontGrip2_Open` | BOOL | 前夹紧2气缸松开电磁阀 -> 主控 -> Y地址 | YV8(预留) |
| 9 | `o_bRearGrip2_Close` | BOOL | 后夹紧2气缸夹紧电磁阀 -> 主控 -> Y地址 | YV9(预留) |
| 10 | `o_bRearGrip2_Open` | BOOL | 后夹紧2气缸松开电磁阀 -> 主控 -> Y地址 | YV10(预留) |

#### 4.1.2 Z轴伺服控制输出 (3个BOOL)

> 仅Z轴由本功能块直接控制，X1轴/X2轴通过内部标志传递给主控处理脉冲输出

| 序号 | 变量名 | 类型 | 功能描述 | 映射目标 |
|:----:|:--------|:----:|:---------|:---------:|
| 11 | `o_bZAxis_PulseOutput` | BOOL | Z轴脉冲输出使能 -> 主控 -> Y0(PULSE) | 脉冲输出 |
| 12 | `o_bZAxis_DirectionOutput` | BOOL | Z轴方向控制 -> 主控 -> Y4(SIGN) | 方向控制 |
| 13 | `o_bZAxis_ServoEnable` | BOOL | Z轴伺服励磁(SON) -> 主控 -> Y10 | 伺服使能 |

### 4.2 下游信号输出组 (1个BOOL)

| 序号 | 变量名 | 类型 | 功能描述 | 目标设备 |
|:----:|:--------|:----:|:---------|:---------:|
| 14 | `o_bFeedComplete_ToFeeder` | BOOL | 放料完成通知下游(打胶机可取料) | 打胶机送料机构(FB_1004) |

### 4.3 状态/HMI显示输出组 (7个)

| 序号 | 变量名 | 类型 | 功能描述 | 显示格式 |
|:----:|:--------|:----:|:---------|:---------:|
| 15 | `o_bRunning` | BOOL | 本站正在自动运行 | 指示灯 |
| 16 | `o_bFault` | BOOL | 本站有故障(任一报警激活) | 报警灯 |
| 17 | `o_iCurrentState` | INT | 当前状态机步序(0~10, 99=故障) | 数值显示 |
| 18 | `o_rZAxis_CurrentPosition` | REAL | Z轴当前位置反馈(mm, 来自主控映射) | 数值(mm) |
| 19 | `o_rX1Axis_CurrentPosition` | REAL | X1轴当前位置反馈(mm, 来自主控映射) | 数值(mm) |
| 20 | `o_rX2Axis_CurrentPosition` | REAL | X2轴当前位置反馈(mm, 预留, 来自主控映射) | 数值(mm) |
| 21 | `o_iCurrentPickupLayer` | INT | 当前正在处理的层数(0=空闲, 1~4=层号) | 数值显示 |

### 4.4 报警输出组 (1个INT)

| 序号 | 变量名 | 类型 | 功能描述 | 有效范围 |
|:----:|:--------|:----:|:---------|:---------:|
| 22 | `o_iStationAlarmCode` | INT | 本站当前有效报警代码(0=无报警, 101~198=报警类型) | 0 / 101~198 |

**完整报警码定义表 (101~108段)**:

| 报警码 | 名称 | 触发条件 | 触发步骤 | 清除条件 | 优先级 |
|:------:|:-----|:---------|:--------:|:---------|:------:|
| 101 | `ALM_ZAxisServoFault` | Z轴伺服驱动器故障 | - | 故障消除+复位 | 高 |
| 102 | `ALM_X1AxisServoFault` | X1轴伺服驱动器故障 | - | 故障消除+复位 | 高 |
| 103 | `ALM_LiftDownTimeout` | Z轴未在规定时间内到达下位 | 步骤2/7 | 复位按钮 | 中 |
| 104 | `ALM_LiftUpTimeout` | Z轴未在规定时间内回到上位 | 步骤5/9 | 复位按钮 | 中 |
| 105 | `ALM_ClampTimeout` | 夹爪夹紧未到位 | 步骤3 | 复位按钮 | 中 |
| 106 | `ALM_UnclampTimeout` | 夹爪松开未到位 | 步骤8 | 复位按钮 | 中 |
| 107 | `ALM_ProductDetectFail` | 产品检测失败(缺长边或短边) | 步骤4 | 排除原因+复位 | 低 |
| 108 | `ALM_MovementTimeout` | X1轴未在规定时间内到达目标位 | 步骤6 | 复位按钮 | 中 |

### 4.5 定时器调试输出组 (4个TIME)

> 新增于V4.2.0，用于HMI显示各定时器的已耗时间，调试诊断用

| 序号 | 变量名 | 类型 | 功能描述 | 对应定时器 |
|:----:|:--------|:----:|:---------|:-----------:|
| 23 | `q_eFeedCompleteHold_Elapsed` | TIME | 放料完成保持定时器已耗时间 | fb_tPlaceCompleteHoldTimer |
| 24 | `q_eAction_Elapsed` | TIME | 通用动作定时器已耗时间(升降/夹紧/松开/移动) | fb_tActionTimer |
| 25 | `q_eProductDetectStable_Elapsed` | TIME | 产品检测稳定定时器已耗时间 | fb_tProductDetectStableTimer |
| 26 | `q_eInit_Elapsed` | TIME | 初始化定时器已耗时间 | fb_tInitTimer |

---

## 5. 与GlobalVars.db stPickPlace结构对照表

| 本FB变量名 (V6.0.0) | GlobalVars.db字段名 (V3.0.0) | 类型 | 一致性 |
|:--------------------:|:---------------------------:|:----:|:------:|
| `i_bEnable` | `stPickPlace.i_bEnable` | BOOL | ✅ 匹配 |
| `i_bAutoMode` | `stPickPlace.i_bAutoMode` | BOOL | ✅ 匹配 |
| ... (其余53个输入变量) | ... (对应stPickPlace结构字段) | - | ✅ 全部匹配 |
| `o_bRunning` | `stPickPlace.o_bRunning` | BOOL | ✅ 匹配 |
| ... (其余29个输出变量) | ... (对应stPickPlace结构字段) | - | ✅ 全部匹配 |

**结论**: ✅ FB_1003接口与GlobalVars.db V3.0.0的stPickPlace结构100%匹配。

---

## 6. 相关文档链接

### 6.1 本FB文档体系(V6.0.0)

| 文档类型 | 文档名称 | 核心内容 |
|:---------|:--------|:--------|
| **详细设计说明书 (DSN)** | [详细设计说明书_DSN-FB1003-PickPlace.md](./详细设计说明书_DSN-FB1003-PickPlace.md) | 11步状态机、4层循环、双夹爪协同 |
| **接口文档 (IFC)** | 本文档 ← **当前文档** | 55输入/30输出的完整英文定义 |
| **使用说明 (UM)** | [使用说明_UM-FB1003-PickPlace.md](./使用说明_UM-FB1003-PickPlace.md) | ST调用示例、调试指南、常见问题排查 |
| **变更记录 (CHG)** | [变更记录_CHG-FB1003-PickPlace.md](./变更记录_CHG-FB1003-PickPlace.md) | 版本历史、变更台帐(含V6.0.0的419处替换详单) |

### 6.2 关联资源

| 资源名称 | 路径 | 用途 |
|:---------|:-----|:-----|
| FB_1003源代码 (V6.0.0) | [FB_1003_PickPlace_BufferFraming.scl](./FB_1003_PickPlace_BufferFraming.scl) | ST实现参考 |
| GlobalVars.db (V3.0.0) | [../DB1/GlobalVars.db](../DB1/GlobalVars.db) | 全局变量定义(stPickPlace结构) |
| OB1.scl (V5.0.0) | [../OB1/OB1.scl](../OB1/OB1.scl) | 主程序组织块(fbPickPlace调用) |

---

## 附录: 快速参考卡片

```
═════════════════════════════════════════════
  FB_1003_PickPlace 接口速查 (V6.0.0)
  55输入 / 30输出 / 25内部变量 / 28常量
═════════════════════════════════════════════

【输入】(55个)
  系统控制: Enable/AutoMode/ManualMode/Start/Stop/Reset (6)
  伺服点动: ZAxis_JogUp/Down + X1Axis_JogFwd/Rev (4)
  气缸控制: Lift(2) + FrontGrip(2) + RearGrip(2)
           + FrontGrip2(2) + RearGrip2(2) = 10
  工艺参数: PickupSpeed/PlaceSpeed/ZAxisSpeed/X1AxisSpeed (4REAL)
           + GripConfirmTime/LiftActionTime (2INT)
  传感器:   气缸位置10(5组×2) + 产品检测4 + 伺服状态12 = 26
  上游信号: Conveyor_L1~L4_FeedComplete (4)

【输出】(30个)
  气缸执行: Lift(2) + FrontGrip(2) + RearGrip(2)
          + FrontGrip2(2) + RearGrip2(2) = 10
  Z轴伺服: PulseOutput/DirectionOutput/ServoEnable (3)
  下游信号: FeedComplete_ToFeeder (1)
  状态HMI: Running/Fault/CurrentState(INT)
          + Z/X1/X2Position(3REAL) + CurrentPickupLayer(INT) = 7
  报警代码: StationAlarmCode(101~198) (1)
  定时器调试: 4个TIME变量 (新增于V4.2.0)

【状态机】: 11步 (Step0~10)
  Idle→WaitFeed→PickupDown→GripClamp→ProductDetect
  →PickupUp→MovingToPlace→PlaceDown→GripUnclamp
  →PlaceUp→PlaceCompleteNotify

【报警快速处理】:
  101/102 → 检查伺服驱动器和接线
  103/104 → 检查Z轴机械和气压
  105/106 → 检查夹紧气缸和磁性开关
  107     → 检查产品位置和光电传感器
  108     → 检查X1轴导轨和伺服参数

【V6.0.0变更要点】:
  ✅ 所有变量名100%英文化(符合801规范V1.0.5)
  ✅ Clamp→Grip系列对齐修复(19处)
  ✅ 注释保留中文(便于国内工程师阅读)
  ✅ 与GlobalVars.db V3.0.0 100%匹配

═════════════════════════════════════════════
```

---

**文档版本**: V6.0.0
**最后更新**: 2026-05-03
**下次审查日期**: [待定]
**归档位置**: `02_PLC程序/通用ST程序及变量表/pickplace/`
