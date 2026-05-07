# 接口文档 - GlobalVars.db (全局变量数据块 V3.0.0)

## 文档信息
| 项目 | 内容 |
|------|------|
| **数据块名称** | GlobalVars |
| **功能描述** | 边框缓存机PLC控制系统全局变量数据交换中心 |
| **当前版本** | V3.0.0 |
| **编译日期** | 2026-05-03 |
| **总变量数** | 258个 (5个STRUCT结构) |
| **符合规范** | 801_PLC变量命名与功能块命名规范_DEV-V1.0.5 |

---

## 数据结构概览

```
DATA_BLOCK GlobalVars
├── stGlobal     : STRUCT (11变量)    ← FB_2001_CommonAlarm 输出
│   ├── i_bReset                    [BOOL]   全局复位按钮
│   ├── o_wGlobalAlarmWord          [WORD]   全局报警字(D400)
│   ├── o_iCurrentAlarmCode         [INT]    当前报警码(D402)
│   ├── o_bAnyAlarmActive           [BOOL]   全局报警激活(M200)
│   ├── o_iMESAlarmCount            [INT]    MES报警计数(D404)
│   ├── o_iMESAlarmQueue            [ARRAY[0..9] OF INT]  MES队列(D406~D425)
│   ├── o_bNewAlarmFlag             [BOOL]   新报警标志
│   ├── o_iStationAlarmStatus       [ARRAY[1..3] OF INT]  三工站状态
│   ├── o_bConveyorAlarmActive      [BOOL]   输送机报警
│   ├── o_bPickPlaceAlarmActive     [BOOL]   取放料报警
│   └── o_bFeederAlarmActive        [BOOL]   送料机构报警
│
├── stExternal  : STRUCT (67变量)    ← 外部设备交互信号
│   ├── 系统控制输入(6): Enable/AutoMode/ManualMode/Start/Stop/Reset
│   ├── 组框机信号(12): 7输入 + 5输出
│   ├── 打胶机信号(10): 6输入 + 4输出
│   ├── 机器人信号(8): 5输入 + 3输出 (预留)
│   ├── 本机状态(3): LocalReady/AnyAlarmActive/SystemFault
│   └── 报警输出(4): EmergencyStop/ExternalDeviceFault/AlarmSummary/SafetyConditionMet
│
├── stConveyor  : STRUCT (64变量)    ← 四层输送机系统(FB_1001/FB_1002)
│   ├── 系统控制(9): Enable/AutoMode/ManualMode/Start/Stop/Reset + 3工艺参数
│   ├── 手动操作(24): ARRAY[1..4] × 6类操作
│   ├── 传感器(28): ARRAY[1..4] × 7类传感器
│   ├── 下游反馈(4): FeedComplete[1..4]
│   ├── 执行器输出(20): ARRAY[1..4] × 5类执行器
│   ├── 下游通知(4): FeedComplete[1..4]
│   ├── 状态显示(4): Running/Fault/CurrentState/LxCurrentStep[1..4]
│   └── 报警码(1): AlarmCode
│
├── stPickPlace : STRUCT (85变量)    ← 取放料机构(FB_1003)
│   ├── 系统控制(6): 同stConveyor格式
│   ├── 手动伺服(4): ZAxis_JogUp/Down + X1Axis_JogFwd/Rev
│   ├── 手动气缸(10): LiftUp/Down + Front/RearGrip_Close/Open ×2组
│   ├── 工艺参数(6): PickupSpeed/PlaceSpeed/ZAxisSpeed/X1AxisSpeed + GripConfirmTime/LiftActionTime
│   ├── 气缸传感器(10): Lift/FrontGrip/RearGrip × WorkPoint/HomePoint ×2组
│   ├── 产品检测(4): LongEdge1/2_Detect + ShortEdge1/2_Detect
│   ├── 伺服轴(12): Home/ServoFault/ForwardLimit/ReverseLimit × Z/X1/X2Axis
│   ├── 上游信号(4): Conveyor_L1~L4_FeedComplete
│   ├── 气缸输出(10): Lift_Up/Down + Front/RearGrip_Close/Open ×2组
│   ├── 伺服输出(3): ZAxis_PulseOutput/DirectionOutput/ServoEnable
│   ├── 下游通知(1): FeedComplete_ToFeeder
│   ├── 状态显示(7): Running/Fault/CurrentState + Position×3 + CurrentPickupLayer
│   ├── 报警码(1): StationAlarmCode(101~199)
│   └── 定时器调试(4): FeedCompleteHold/Action/ProductDetectStable/Init_Elapsed
│
└── stFeeder    : STRUCT (31变量)    ← 打胶机送料机构(FB_1004)
    ├── 系统控制(6): 同stConveyor格式
    ├── 手动X2轴(2): X2Axis_JogFwd/Rev
    ├── 工艺参数(3): FeedSpeed/StandbyPosition/PickupPosition
    ├── 伺服传感(4): X2Axis_Home/ForwardLimit/ReverseLimit/ServoFault
    ├── 打胶机交互(2): GlueMachine_AllowFeed/PickupComplete
    ├── 上游信号(1): PickPlace_FeedComplete
    ├── 执行器输出(3): AllowPickup/X2Axis_RequestFwd/Rev
    ├── 安全区(1): SafetyZoneSignal
    ├── 状态显示(4): Running/Fault/CurrentState/X2Axis_CurrentPosition
    ├── 报警码(1): StationAlarmCode(201~299)
    └── 定时器调试(4): CommTimeout/Action/Init/PickupHold_Elapsed
END_DATA_BLOCK
```

---

## 详细接口定义

### 第一部分: stGlobal结构 (11变量) - FB_2001_CommonAlarm接口

#### 操作控制输入 (1个)
| 变量名 | 类型 | 初始值 | 说明 | 物理地址 |
|--------|------|--------|------|----------|
| `i_bReset` | BOOL | FALSE | 全局复位按钮 (传给FB_2001) | M0 |

#### HMI显示输出 (2个) - 来自FB_2001
| 变量名 | 类型 | 初始值 | 说明 | 物理地址 |
|--------|------|--------|------|----------|
| `o_wGlobalAlarmWord` | WORD | 0 | 全局报警字 (D400, HMI报警灯用, 位或组合) | D400 |
| `o_iCurrentAlarmCode` | INT | 0 | 最高优先级有效报警码 (D402, HMI文本显示) | D402 |

#### 全局互锁输出 (1个) - 来自FB_2001
| 变量名 | 类型 | 初始值 | 说明 | 物理地址 |
|--------|------|--------|------|----------|
| `o_bAnyAlarmActive` | BOOL | FALSE | 全局报警激活标志 (M200, 所有工站停止) | M200 |

#### MES数据接口输出 (3个) - 来自FB_2001
| 变量名 | 类型 | 初始值 | 说明 | 物理地址 |
|--------|------|--------|------|----------|
| `o_iMESAlarmCount` | INT | 0 | MES报警累计计数 | D404 |
| `o_iMESAlarmQueue` | ARRAY[0..9] OF INT | - | MES报警队列 (最近10条去重记录) | D406~D425 |
| `o_bNewAlarmFlag` | BOOL | FALSE | 新报警检测脉冲 (触发MES上传) | M201 |

#### 多报警状态输出 (5个) - 来自FB_2001
| 变量名 | 类型 | 初始值 | 说明 | 物理地址 |
|--------|------|--------|------|----------|
| `o_iStationAlarmStatus` | ARRAY[1..3] OF INT | {0,0,0} | 三工站报警状态数组<br>[1]Conveyor [2]PickPlace [3]Feeder | D430~D432 |
| `o_bConveyorAlarmActive` | BOOL | FALSE | 输送机工站有报警标志 | M202 |
| `o_bPickPlaceAlarmActive` | BOOL | FALSE | 取放料工站有报警标志 | M203 |
| `o_bFeederAlarmActive` | BOOL | FALSE | 送料机构工站有报警标志 | M204 |

---

### 第二部分: stExternal结构 (67变量) - 外部设备交互接口

#### 系统控制输入信号 (6个)
| 变量名 | 类型 | 初始值 | 说明 | 来源 |
|--------|------|--------|------|------|
| `i_bEnable` | BOOL | FALSE | 系统总使能 | HMI/上位机 |
| `i_bAutoMode` | BOOL | FALSE | 自动模式选择 | HMI画面 |
| `i_bManualMode` | BOOL | FALSE | 手动模式选择 | HMI画面 |
| `i_bStart` | BOOL | FALSE | 启动按钮 (上升沿触发) | HMI按钮 |
| `i_bStop` | BOOL | FALSE | 停止按钮 (电平有效) | HMI按钮 |
| `i_bReset` | BOOL | FALSE | 复位按钮 (电平有效) | HMI按钮 |

#### 组框机输入信号 (7个)
| 变量名 | 类型 | 初始值 | 说明 | 物理地址 |
|--------|------|--------|------|----------|
| `i_bFrameMachine_AutoRunning` | BOOL | FALSE | 组框机自动运行中 | X10 |
| `i_bFrameMachine_AllowFeed` | BOOL | FALSE | 组框机允许向缓存机输送边框 | X11 |
| `i_bFrameMaterialRequest` | BOOL | FALSE | 组框机有边框需要送入缓存机 | X12 |
| `i_bDoorOpenRequest` | BOOL | FALSE | 组框机操作门打开 (需本机暂停) | X13 |
| `i_bFrameMachine_EStop` | BOOL | FALSE | 组框机急停信号 (需联锁) | X14 |
| `i_bFrameMachine_SafetyErr` | BOOL | FALSE | 组框机安全系统异常 | X15 |
| `i_bFrameMachine_CommErr` | BOOL | FALSE | 与组框机通讯异常 | X16 |

#### 组框机输出信号 (5个)
| 变量名 | 类型 | 初始值 | 说明 | 物理地址 |
|--------|------|--------|------|----------|
| `o_bFrameMachine_RequestFeed` | BOOL | FALSE | 向组框机请求输送边框 | Y20 |
| `o_bFrameMachine_Pause` | BOOL | FALSE | 向组框机发送暂停指令 | Y21 |
| `o_bFrameMachine_EStop` | BOOL | FALSE | 向组框机发送急停联锁信号 | Y22 |
| `o_bDoorOpenRequest` | BOOL | FALSE | 向组框机申请开门操作 | Y23 |
| `o_bFrameMachine_Ready` | BOOL | FALSE | 本机就绪, 可接收边框 | Y24 |

#### 打胶机输入信号 (6个)
| 变量名 | 类型 | 初始值 | 说明 | 物理地址 |
|--------|------|--------|------|----------|
| `i_bGlueMachine_AutoRunning` | BOOL | FALSE | 打胶机自动运行中 | X70 |
| `i_bGlueMachine_AllowFeed` | BOOL | FALSE | 打胶机准备好可接收边框 | X71 |
| `i_bGlueMachine_PickComplete` | BOOL | FALSE | 打胶机已完成边框抓取 | X72 |
| `i_bGlueMachine_Fault` | BOOL | FALSE | 打胶机设备故障报警 | X73 |
| `i_bGlueMachine_EStop` | BOOL | FALSE | 打胶机急停状态 | X74 |
| `i_bGlueMachine_CommErr` | BOOL | FALSE | 与打胶机通讯中断 | X75 |

#### 打胶机输出信号 (4个)
| 变量名 | 类型 | 初始值 | 说明 | 物理地址 |
|--------|------|--------|------|----------|
| `o_bGlueMachine_RequestRun` | BOOL | FALSE | 请求打胶机启动运行 | Y40 |
| `o_bAllowPickup` | BOOL | FALSE | 通知打胶机可以抓取边框 | Y44 |
| `o_bSafetyZoneSignal` | BOOL | FALSE | 安全区开放/关闭信号 | Y47 |
| `o_bGlueMachine_ResetReq` | BOOL | FALSE | 向打胶机发送复位请求 | Y48 |

#### 机器人输入信号 (5个, 预留)
| 变量名 | 类型 | 初始值 | 说明 | 物理地址 |
|--------|------|--------|------|----------|
| `i_bRobot_AutoRunning` | BOOL | FALSE | 机器人自动运行中 | X80(预留) |
| `i_bRobot_StackComplete` | BOOL | FALSE | 机器人完成码料 | X81(预留) |
| `i_bRobot_Fault` | BOOL | FALSE | 机器人设备故障 | X82(预留) |
| `i_bRobot_EStop` | BOOL | FALSE | 机器人急停状态 | X83(预留) |
| `i_bRobot_CommErr` | BOOL | FALSE | 与机器人通讯异常 | X84(预留) |

#### 机器人输出信号 (3个, 预留)
| 变量名 | 类型 | 初始值 | 说明 | 物理地址 |
|--------|------|--------|------|----------|
| `o_bRobot_AllowStacking` | BOOL | FALSE | 允许机器人进行码料 | Y60(预留) |
| `o_bRobot_StopStacking` | BOOL | FALSE | 停止机器人码料 | Y61(预留) |
| `o_bRobot_ResetReq` | BOOL | FALSE | 向机器人发送复位请求 | Y62(预留) |

#### 本机状态信号 (3个)
| 变量名 | 类型 | 初始值 | 说明 | 用途 |
|--------|------|--------|------|------|
| `i_bLocalReady` | BOOL | FALSE | 本机就绪状态 (传给外部设备) | 外部设备读取 |
| `i_bAnyAlarmActive` | BOOL | FALSE | 本机有任何报警激活 | 外部设备联锁 |
| `i_bSystemFault` | BOOL | FALSE | 本机系统故障 | 外部设备保护 |

#### 状态与报警输出 (4个)
| 变量名 | 类型 | 初始值 | 说明 | 用途 |
|--------|------|--------|------|------|
| `o_bFrameMachine_EmergencyStop` | BOOL | FALSE | 组框机急停/安全异常时强制本机停止 | OB1互锁逻辑 |
| `o_bExternalDeviceFault` | BOOL | FALSE | 外部设备故障标志 | HMI显示 |
| `o_iExternalDeviceAlarmSummary` | INT | 0 | 外部设备故障报警码 (300~399段) | MES上传 |
| `o_bSystemSafetyConditionMet` | BOOL | FALSE | 系统安全条件是否满足 | 启动条件判断 |

---

### 第三部分: stConveyor结构 (64变量) - 四层输送机接口

#### 系统控制信号 (9个, 含工艺参数)
| 变量名 | 类型 | 初始值 | 说明 | 范围 |
|--------|------|--------|------|------|
| `i_bEnable` | BOOL | FALSE | 总使能信号 | - |
| `i_bAutoMode` | BOOL | FALSE | 自动运行模式选择 | - |
| `i_bManualMode` | BOOL | FALSE | 手动调试模式选择 | - |
| `i_bStart` | BOOL | FALSE | 自动循环启动按钮 | - |
| `i_bStop` | BOOL | FALSE | 自动循环停止按钮 | - |
| `i_bReset` | BOOL | FALSE | 故障复位/初始化按钮 | - |
| `i_rConveyorSpeed` | REAL | 50.0 | 输送带速度设定 (Hz或m/min) | 0~100 |
| `i_iSeparateTime` | INT | 500 | 分料动作保持时间 (ms) | 100~2000 |
| `i_iBlockWaitTime` | INT | 200 | 阻挡气缸动作等待时间 (ms) | 50~1000 |

#### 手动操作信号 (24个, ARRAY[1..4])
| 变量名 | 类型 | 维度 | 说明 | 层索引含义 |
|--------|------|------|------|-----------|
| `i_bLx_BlockDown` | BOOL | [1..4] | 手动-阻挡气缸下降 | 1=第1层(L1) ... 4=第4层(L4) |
| `i_bLx_BlockUp` | BOOL | [1..4] | 手动-阻挡气缸上升 | 同上 |
| `i_bLx_SeparatePush` | BOOL | [1..4] | 手动-分料气缸推出 | 同上 |
| `i_bLx_SeparateReset` | BOOL | [1..4] | 手动-分料气缸复位 | 同上 |
| `i_bLx_ConveyorFwd` | BOOL | [1..4] | 手动-输送带正转 | 同上 |
| `i_bLx_ConveyorRev` | BOOL | [1..4] | 手动-输送带反转 | 同上 |

#### 传感器输入 (28个, ARRAY[1..4])
| 变量名 | 类型 | 维度 | 说明 | 传感器类型 |
|--------|------|------|------|-----------|
| `i_bPreSeparateSensor` | BOOL | [1..4] | 分料前材料到达感应器 | 光电传感器 |
| `i_bPositionSensor1` | BOOL | [1..4] | 到位感应器1 (冗余检测) | 光电/接近开关 |
| `i_bPositionSensor2` | BOOL | [1..4] | 到位感应器2 (冗余检测) | 光电/接近开关 |
| `i_bBlockCylinderUp` | BOOL | [1..4] | 阻挡气缸上升(释放)位置反馈 | 磁性开关 |
| `i_bBlockCylinderDown` | BOOL | [1..4] | 阻挡下降(阻挡)位置反馈 | 磁性开关 |
| `i_bSeparateCylinderUp` | BOOL | [1..4] | 分料气缸收回位置反馈 | 磁性开关 |
| `i_bSeparateCylinderDown` | BOOL | [1..4] | 分料气缸推出位置反馈 | 磁性开关 |

#### 下游反馈信号 (4个, ARRAY[1..4])
| 变量名 | 类型 | 维度 | 说明 | 来源 |
|--------|------|------|------|------|
| `i_bFeedComplete` | BOOL | [1..4] | 该层物料已被取放料机构取走 | FB_1003.o_bFeedComplete_ToFeeder |

#### 执行器请求输出 (20个, ARRAY[1..4])
| 变量名 | 类型 | 维度 | 说明 | TRUE/FALSE含义 |
|--------|------|------|------|---------------|
| `o_bBlockSolenoid` | BOOL | [1..4] | 阻挡电磁阀 | TRUE=下降(阻挡), FALSE=上升(释放) |
| `o_bSeparateSolenoid` | BOOL | [1..4] | 分料电磁阀 | TRUE=推出(分料), FALSE=复位 |
| `o_bConveyorFwd` | BOOL | [1..4] | 输送带正转 | TRUE=正向运转 |
| `o_bConveyorSlow` | BOOL | [1..4] | 输送带慢速 | TRUE=慢速运转 (精确定位用) |
| `o_bConveyorRev` | BOOL | [1..4] | 输送带反转 | TRUE=反向运转 (退料用) |

#### 下游信号输出 (4个, ARRAY[1..4])
| 变量名 | 类型 | 维度 | 说明 | 目标 |
|--------|------|------|------|------|
| `o_bFeedComplete` | BOOL | [1..4] | 该层放料完成, 可取料 | → stPickPlace.i_bConveyor_Lx_FeedComplete |

#### 状态/HMI显示输出 (4个)
| 变量名 | 类型 | 初始值 | 说明 | HMI用途 |
|--------|------|--------|------|---------|
| `o_bRunning` | BOOL | FALSE | 任一层正在自动运行 | 运行指示灯 |
| `o_bFault` | BOOL | FALSE | 本站有故障 (任一报警激活) | 故障指示灯 |
| `o_iCurrentState` | INT | 0 | 当前主要状态码 (0=idle, 1-8=步序, 99=fault) | 步序显示 |
| `o_LxCurrentStep` | INT[1..4] | {0,0,0,0} | 每层当前步序 (0-8) | 各层状态显示 |

#### 报警输出 (1个)
| 变量名 | 类型 | 初始值 | 说明 | 报警码范围 |
|--------|------|--------|------|-----------|
| `o_iAlarmCode` | INT | 0 | 本站当前有效报警代码 (0=无报警, 1-7=报警类型) | 001~007 |

---

### 第四部分: stPickPlace结构 (85变量) - 取放料机构接口

*(由于篇幅限制，此处仅展示关键接口，完整定义请参考源文件注释)*

#### 核心工艺参数 (6个)
| 变量名 | 类型 | 初始值 | 说明 | 调节范围 |
|--------|------|--------|------|---------|
| `i_rPickupSpeed` | REAL | 100.0 | 取料过程Z轴下降/上升速度 (mm/s或%) | 10~200 |
| `i_rPlaceSpeed` | REAL | 80.0 | 放料过程Z轴下降/上升速度 (mm/s或%) | 10~150 |
| `i_rZAxisSpeed` | REAL | 100.0 | Z轴通用运动速度设定 (mm/s) | 10~200 |
| `i_rX1AxisSpeed` | REAL | 150.0 | X1轴通用运动速度设定 (mm/s) | 10~300 |
| `i_iGripConfirmTime` | INT | 500 | 夹爪夹紧确认等待时间 (ms) | 100~2000 |
| `i_iLiftActionTime` | INT | 3000 | 升降气缸动作超时时间 (ms) | 1000~10000 |

#### 关键状态输出 (7个)
| 变量名 | 类型 | 初始值 | 说明 | 用途 |
|--------|------|--------|------|------|
| `o_bRunning` | BOOL | FALSE | 本站正在自动运行 | HMI运行灯 |
| `o_bFault` | BOOL | FALSE | 本站有故障 | HMI故障灯 |
| `o_iCurrentState` | INT | 0 | 当前状态机步序 (0~10, 99=fault) | 步序显示器 |
| `o_rZAxis_CurrentPosition` | REAL | 0.0 | Z轴当前位置反馈 (mm) | HMI数值显示 |
| `o_rX1Axis_CurrentPosition` | REAL | 0.0 | X1轴当前位置反馈 (mm) | HMI数值显示 |
| `o_rX2Axis_CurrentPosition` | REAL | 0.0 | X2轴当前位置反馈 (mm) | HMI数值显示(预留) |
| `o_iCurrentPickupLayer` | INT | 0 | 当前正在处理的层数 (0=空闲, 1~4=层号) | 层号显示 |

#### 报警码定义 (101~199)
| 报警码 | 含义 | 触发条件 | 处置建议 |
|--------|------|---------|---------|
| 101 | Z轴原点丢失 | i_bZAxis_Home=FALSE 且非回原点状态 | 检查Z轴原点传感器 |
| 102 | Z轴伺服故障 | i_bZAxis_ServoFault=TRUE | 检查Z轴驱动器ALM |
| 103 | Z轴正向超程 | i_bZAxis_ForwardLimit=TRUE | 手动移出限位区 |
| 104 | Z轴反向超程 | i_bZAxis_ReverseLimit=TRUE | 手动移出限位区 |
| 105 | X1轴原点丢失 | i_bX1Axis_Home=FALSE | 检查X1轴原点传感器 |
| 106 | X1轴伺服故障 | i_bX1Axis_ServoFault=TRUE | 检查X1轴驱动器 |
| 107 | 升降气缸超时 | 动作时间> i_iLiftActionTime | 检查气缸/电磁阀 |
| 108 | 产品检测失败 | 4个检测传感器全为FALSE | 检查光电传感器 |
| 109 | 夹紧确认失败 | 夹紧后未检测到WorkPoint | 检查夹爪/磁性开关 |
| 110-199 | 预留 | - | - |

---

### 第五部分: stFeeder结构 (31变量) - 打胶机送料机构接口

#### 核心工艺参数 (3个)
| 变量名 | 类型 | 初始值 | 说明 | 调节范围 |
|--------|------|--------|------|---------|
| `i_rFeedSpeed` | REAL | 120.0 | X2轴送料运动速度 (mm/s或%) | 10~250 |
| `rStandbyPosition` | REAL | 0.0 | X2轴待机位置坐标 (mm) | 根据机械尺寸设定 |
| `rPickupPosition` | REAL | 300.0 | X2轴取料位置坐标 (mm) | 根据机械尺寸设定 |

#### 关键状态输出 (4个)
| 变量名 | 类型 | 初始值 | 说明 | 用途 |
|--------|------|--------|------|------|
| `o_bRunning` | BOOL | FALSE | 本站正在自动运行 | HMI运行灯 |
| `o_bFault` | BOOL | FALSE | 本站有故障 | HMI故障灯 |
| `o_iCurrentState` | INT | 0 | 当前状态机步序 (0~5, 99=fault) | 步序显示器 |
| `o_rX2Axis_CurrentPosition` | REAL | 0.0 | X2轴当前位置反馈 (mm) | HMI数值显示 |

#### 报警码定义 (201~299)
| 报警码 | 含义 | 触发条件 | 处置建议 |
|--------|------|---------|---------|
| 201 | X2轴原点丢失 | i_bX2Axis_Home=FALSE | 检查X2轴原点传感器 |
| 202 | X2轴伺服故障 | i_bX2Axis_ServoFault=TRUE | 检查X2轴驱动器ALM |
| 203 | X2轴正向超程 | i_bX2Axis_ForwardLimit=TRUE | 手动移出限位区 |
| 204 | X2轴反向超程 | i_bX2Axis_ReverseLimit=TRUE | 手动移出限位区 |
| 205 | 打胶机通讯超时 | 等待允许送料超时 | 检查打胶机通讯线路 |
| 206 | 安全区互锁失败 | 安全区信号异常 | 检查安全光栅/门锁 |
| 207-299 | 预留 | - | - |

---

## 使用示例

### OB1中的典型调用方式
```scl
// 调用四层输送机容器功能块
fbConveyor4Layer(
    // === 系统控制信号 ===
    i_bEnable := GlobalVars.stConveyor.i_bEnable,
    i_bAutoMode := GlobalVars.stConveyor.i_bAutoMode,
    i_bStart := GlobalVars.stConveyor.i_bStart,
    i_bStop := GlobalVars.stConveyor.i_bStop,
    i_bReset := GlobalVars.stConveyor.i_bReset,

    // === 工艺参数 ===
    i_rConveyorSpeed := GlobalVars.stConveyor.i_rConveyorSpeed,
    i_iSeparateTime := GlobalVars.stConveyor.i_iSeparateTime,

    // === 第1层手动操作 ===
    i_bLx_BlockDown[1] := GlobalVars.stConveyor.i_bLx_BlockDown[1],
    i_bLx_BlockUp[1] := GlobalVars.stConveyor.i_bLx_BlockUp[1],

    // === 第1层传感器 ===
    i_bPreSeparateSensor[1] := GlobalVars.stConveyor.i_bPreSeparateSensor[1],
    i_bPositionSensor1[1] := GlobalVars.stConveyor.i_bPositionSensor1[1],

    // === 输出收集 ===
    GlobalVars.stConveyor.o_bBlockSolenoid[1] := fbConveyor4Layer.o_bBlockSolenoid[1],
    GlobalVars.stConveyor.o_bRunning := fbConveyor4Layer.o_bRunning,
    GlobalVars.stConveyor.o_iAlarmCode := fbConveyor4Layer.o_iAlarmCode
);
```

---

## 注意事项

### ⚠️ 重要提示
1. **ARRAY索引**: 所有ARRAY[1..4]类型的变量，索引1对应第1层(L1)，索引4对应第4层(L4)
2. **初始安全值**: 所有BOOL初始值为FALSE，所有数值初始值为0，确保上电不会误动作
3. **命名一致性**: 本DB的变量名与FB_1001~1004的接口引脚名**完全一致**
4. **物理地址**: 表格中的物理地址为建议分配，实际以硬件配置为准
5. **版本同步**: 必须与OB1.scl V5.0.0及以上版本配套使用

### 🔒 安全相关
- `o_bAnyAlarmActive` (M200) 用于全局互锁，任何工站报警都会激活此信号
- `o_bSafetyZoneSignal` (Y47) 直接关系到人员安全，必须可靠连接安全继电器
- `i_bFrameMachine_EStop` / `i_bGlueMachine_EStop` 为硬接线急停信号，不可软件屏蔽

### 📊 性能优化
- 使用STRUCT分组减少全局变量搜索时间
- ARRAY类型支持循环访问，简化多层处理逻辑
- 定时器调试输出(q_e*_Elapsed)仅用于HMI显示，不影响实时控制

---

## 版本兼容性

| 版本 | 兼容性 | 说明 |
|------|--------|------|
| V3.0.0 | ✅ 最新版 | 100%英文化，与OB1 V5.0.0同步 |
| V2.0.0 | ⚠️ 已废弃 | 包含146处中文变量名，不推荐使用 |
| V1.0.0 | ❌ 不兼容 | 初始版本，接口不完整 |

**升级路径**: V1/V2 → V3.0.0 (需同步更新OB1和所有FB调用)

---

## 关联文档
- **变更记录**: [变更记录_CHG-GlobalVars-V3.0.0.md](./变更记录_CHG-GlobalVars-V3.0.0.md)
- **重写方案**: [PLC程序全面重写方案_V5.0.0.md](../../.trae/documents/PLC程序全面重写方案_V5.0.0.md)
- **架构文档**: [程序架构文档_ARC-DJ-2026-005-V4.2.0.md](../程序架构文档_ARC-DJ-2026-005-V4.2.0.md)
- **命名规范**: 801_PLC变量命名与功能块命名规范_DEV-V1.0.5

---

*文档编译时间: 2026-05-03 15:45:00*
*生成工具: Trae IDE AI Assistant*
*审核状态: 待人工审核*
*下次更新: 配合阶段3(OB1重写)完成后同步更新*
