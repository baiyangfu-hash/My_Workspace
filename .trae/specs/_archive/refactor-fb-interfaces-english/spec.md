# FB接口变量名英文化重构 Spec

## Why
在V5.0.0全面重写过程中，OB1.scl已将所有调用参数改为英文变量名（匹配GlobalVars.db V3.0.0），但 **FB_ExternalDeviceInteraction** 和 **FB_1003_PickPlace** 两个功能块的**接口定义（VAR_INPUT/VAR_OUTPUT）仍使用中文变量名**，导致编译错误：
- `Unknown pin "i_bGlueMachine_AutoRunning" on call to "FB_External..."`
- TC001/TC002 编译错误

## What Changes
- **BREAKING**: 重写 FB_ExternalDeviceInteraction 接口变量名（27输入 + 20输出 = 47个）
- **BREAKING**: 重写 FB_1003_PickPlace 接口变量名（55输入 + 30输出 = 85个）
- 同步修改两个FB的**内部实现代码**中引用这些变量的地方
- 更新版本号和变更记录
- 创建/更新变更记录文档

## Impact
- Affected code:
  - `external/FB_ExternalDeviceInteraction.scl` (V4.1.0 → V5.0.0)
  - `pickplace/FB_1003_PickPlace_BufferFraming.scl` (V4.2.0 → V5.0.0)
  - `OB1/OB1.scl` (V5.0.0, 已完成，无需修改)
- Affected docs: 变更记录文档（每个FB一份）

---

## ADDED Requirements

### Requirement: FB_ExternalDeviceInteraction 英文接口
系统 SHALL 将 FB_ExternalDeviceInteraction 的所有接口变量名从中文改为英文，符合801规范V1.0.5。

#### Scenario: 编译通过
- **WHEN** OB1.scl 调用 `fbExternalDevice(i_bGlueMachine_AutoRunning := ...)`
- **THEN** 不再报 "Unknown pin" 错误，编译成功

#### 变量映射表 (VAR_INPUT - 27个)

| 原变量名(中文) | 新变量名(英文) | 类型 | 说明 |
|:---|:---|:---|:---|
| i_b使能 | i_bEnable | BOOL | 系统总使能 |
| i_b自动模式 | i_bAutoMode | BOOL | 自动模式选择 |
| i_b手动模式 | i_bManualMode | BOOL | 手动模式选择 |
| i_b启动 | i_bStart | BOOL | 启动按钮 |
| i_b停止 | i_bStop | BOOL | 停止按钮 |
| i_b复位 | i_bReset | BOOL | 复位按钮 |
| i_b组框机_自动中 | i_bFrameMachine_AutoRunning | BOOL | 组框机自动运行中 |
| i_b组框机_允许送料 | i_bFrameMachine_AllowFeed | BOOL | 组框机允许送料 |
| i_b组框机_有料请求 | i_bFrameMaterialRequest | BOOL | 组框机有料请求 |
| i_b组框机_开门请求 | i_bDoorOpenRequest | BOOL | 组框机开门请求 |
| i_b组框机_急停 | i_bFrameMachine_EStop | BOOL | 组框机急停 |
| i_b组框机_安全异常 | i_bFrameMachine_SafetyErr | BOOL | 组框机安全异常 |
| i_b组框机_通讯异常 | i_bFrameMachine_CommErr | BOOL | 组框机通讯异常 |
| i_b打胶机_自动中 | i_bGlueMachine_AutoRunning | BOOL | 打胶机自动运行中 |
| i_b打胶机_允许送料 | i_bGlueMachine_AllowFeed | BOOL | 打胶机允许送料 |
| i_b打胶机_取料完成 | i_bGlueMachine_PickComplete | BOOL | 打胶机取料完成 |
| i_b打胶机_故障 | i_bGlueMachine_Fault | BOOL | 打胶机故障 |
| i_b打胶机_急停 | i_bGlueMachine_EStop | BOOL | 打胶机急停 |
| i_b打胶机_通讯异常 | i_bGlueMachine_CommErr | BOOL | 打胶机通讯异常 |
| i_b机器人_自动中 | i_bRobot_AutoRunning | BOOL | 机器人自动运行中 |
| i_b机器人_码料完成 | i_bRobot_StackComplete | BOOL | 机器人码料完成 |
| i_b机器人_故障 | i_bRobot_Fault | BOOL | 机器人故障 |
| i_b机器人_急停 | i_bRobot_EStop | BOOL | 机器人急停 |
| i_b机器人_通讯异常 | i_bRobot_CommErr | BOOL | 机器人通讯异常 |
| i_b本机就绪 | i_bLocalReady | BOOL | 本机就绪 |
| i_b任何报警激活 | i_bAnyAlarmActive | BOOL | 任何报警激活 |
| i_b系统故障 | i_bSystemFault | BOOL | 系统故障 |

#### 变量映射表 (VAR_OUTPUT - 20个)

| 原变量名(中文) | 新变量名(英文) | 类型 | 说明 |
|:---|:---|:---|:---|
| q_b组框机_请求送料 | q_bFrameMachine_RequestFeed | BOOL | 请求送料 |
| q_b组框机_暂停 | q_bFrameMachine_Pause | BOOL | 暂停指令 |
| q_b组框机_急停 | q_bFrameMachine_EStop | BOOL | 急停联锁 |
| q_b申请开门 | q_bDoorOpenRequest | BOOL | 申请开门 |
| q_b组框机_就绪 | q_bFrameMachine_Ready | BOOL | 本机就绪 |
| q_b打胶机_请求运行 | q_bGlueMachine_RequestRun | BOOL | 请求运行 |
| q_b允许抓料 | q_bAllowPickup | BOOL | 允许抓料 |
| q_b安全区信号 | q_bSafetyZoneSignal | BOOL | 安全区信号 |
| q_b打胶机_复位请求 | q_bGlueMachine_ResetReq | BOOL | 复位请求 |
| q_b机器人_允许码料 | q_bRobot_AllowStacking | BOOL | 允许码料 |
| q_b机器人_停止码料 | q_bRobot_StopStacking | BOOL | 停止码料 |
| q_b机器人_复位请求 | q_bRobot_ResetReq | BOOL | 复位请求 |
| q_b组框机紧急停止 | q_bFrameMachine_EmergencyStop | BOOL | 紧急停止 |
| q_b外部设备故障 | q_bExternalDeviceFault | BOOL | 外部设备故障 |
| q_i外部设备报警汇总 | q_iExternalDeviceAlarmSummary | INT | 报警汇总 |
| q_b系统安全条件满足 | q_bSystemSafetyConditionMet | BOOL | 安全条件满足 |

### Requirement: FB_1003_PickPlace 英文接口
系统 SHALL 将 FB_1003_PickPlace 的所有接口变量名从中文改为英文，符合801规范V1.0.5。

#### Scenario: 编译通过
- **WHEN** OB1.scl 调用 `fbPickPlace(i_bLx_ZAxis_JogUp := ...)`
- **THEN** 不再报 "Unknown pin" 错误，编译成功

#### 变量映射表 (VAR_INPUT - 55个)

| 原变量名(中文) | 新变量名(英文) | 类型 | 说明 |
|:---|:---|:---|:---|
| i_b使能 | i_bEnable | BOOL | 总使能 |
| i_b自动模式 | i_bAutoMode | BOOL | 自动模式 |
| i_b手动模式 | i_bManualMode | BOOL | 手动模式 |
| i_b启动 | i_bStart | BOOL | 启动 |
| i_b停止 | i_bStop | BOOL | 停止 |
| i_b复位 | i_bReset | BOOL | 复位 |
| i_bZ轴点动上 | i_bLx_ZAxis_JogUp | BOOL | Z轴点动上 |
| i_bZ轴点动下 | i_bLx_ZAxis_JogDown | BOOL | Z轴点动下 |
| i_bX1轴点动前 | i_bLx_X1Axis_JogFwd | BOOL | X1轴点动前 |
| i_bX1轴点动后 | i_bLx_X1Axis_JogRev | BOOL | X1轴点动后 |
| i_b升降上升 | i_bLx_LiftUp | BOOL | 升降上升 |
| i_b升降下降 | i_bLx_LiftDown | BOOL | 升降下降 |
| i_b前夹紧夹紧 | i_bLx_FrontGrip_Close | BOOL | 前夹紧夹紧 |
| i_b前夹紧松开 | i_bLx_FrontGrip_Open | BOOL | 前夹紧松开 |
| i_b后夹紧夹紧 | i_bLx_RearGrip_Close | BOOL | 后夹紧夹紧 |
| i_b后夹紧松开 | i_bLx_RearGrip_Open | BOOL | 后夹紧松开 |
| i_b前夹紧2夹紧 | i_bLx_FrontGrip2_Close | BOOL | 前夹紧2夹紧 |
| i_b前夹紧2松开 | i_bLx_FrontGrip2_Open | BOOL | 前夹紧2松开 |
| i_b后夹紧2夹紧 | i_bLx_RearGrip2_Close | BOOL | 后夹紧2夹紧 |
| i_b后夹紧2松开 | i_bLx_RearGrip2_Open | BOOL | 后夹紧2松开 |
| i_r取料速度 | i_rPickupSpeed | REAL | 取料速度 |
| i_r放料速度 | i_rPlaceSpeed | REAL | 放料速度 |
| i_rZ轴速度 | i_rZAxisSpeed | REAL | Z轴速度 |
| i_rX1轴速度 | i_rX1AxisSpeed | REAL | X1轴速度 |
| i_i夹紧确认时间 | i_iGripConfirmTime | INT | 夹紧确认时间 |
| i_i升降动作时间 | i_iLiftActionTime | INT | 升降动作时间 |
| i_b升降_动点 | i_bLift_WorkPoint | BOOL | 升降动点 |
| i_b升降_原点 | i_bLift_HomePoint | BOOL | 升降原点 |
| i_b前夹紧_动点 | i_bFrontGrip_WorkPoint | BOOL | 前夹紧动点 |
| i_b前夹紧_原点 | i_bFrontGrip_HomePoint | BOOL | 前夹紧原点 |
| i_b后夹紧_动点 | i_bRearGrip_WorkPoint | BOOL | 后夹紧动点 |
| i_b后夹紧_原点 | i_bRearGrip_HomePoint | BOOL | 后夹紧原点 |
| i_b前夹紧2_动点 | i_bFrontGrip2_WorkPoint | BOOL | 前夹紧2动点 |
| i_b前夹紧2_原点 | i_bFrontGrip2_HomePoint | BOOL | 前夹紧2原点 |
| i_b后夹紧2_动点 | i_bRearGrip2_WorkPoint | BOOL | 后夹紧2动点 |
| i_b后夹紧2_原点 | i_bRearGrip2_HomePoint | BOOL | 后夹紧2原点 |
| i_b长边1检测 | i_bLongEdge1_Detect | BOOL | 长边1检测 |
| i_b长边2检测 | i_bLongEdge2_Detect | BOOL | 长边2检测 |
| i_b短边1检测 | i_bShortEdge1_Detect | BOOL | 短边1检测 |
| i_b短边2检测 | i_bShortEdge2_Detect | BOOL | 短边2检测 |
| i_bZ轴_原点 | i_bZAxis_Home | BOOL | Z轴原点 |
| i_bX1轴_原点 | i_bX1Axis_Home | BOOL | X1轴原点 |
| i_bX2轴_原点 | i_bX2Axis_Home | BOOL | X2轴原点 |
| i_bZ轴_伺服故障 | i_bZAxis_ServoFault | BOOL | Z轴伺服故障 |
| i_bX1轴_伺服故障 | i_bX1Axis_ServoFault | BOOL | X1轴伺服故障 |
| i_bX2轴_伺服故障 | i_bX2Axis_ServoFault | BOOL | X2轴伺服故障 |
| i_bZ轴_正向限位 | i_bZAxis_ForwardLimit | BOOL | Z轴正向限位 |
| i_bZ轴_反向限位 | i_bZAxis_ReverseLimit | BOOL | Z轴反向限位 |
| i_bX1轴_正向限位 | i_bX1Axis_ForwardLimit | BOOL | X1轴正向限位 |
| i_bX1轴_反向限位 | i_bX1Axis_ReverseLimit | BOOL | X1轴反向限位 |
| i_bX2轴_正向限位 | i_bX2Axis_ForwardLimit | BOOL | X2轴正向限位 |
| i_bX2轴_反向限位 | i_bX2Axis_ReverseLimit | BOOL | X2轴反向限位 |
| i_b输送机_L1_放料完成 | i_bConveyor_L1_FeedComplete | BOOL | L1放料完成 |
| i_b输送机_L2_放料完成 | i_bConveyor_L2_FeedComplete | BOOL | L2放料完成 |
| i_b输送机_L3_放料完成 | i_bConveyor_L3_FeedComplete | BOOL | L3放料完成 |
| i_b输送机_L4_放料完成 | i_bConveyor_L4_FeedComplete | BOOL | L4放料完成 |

#### 变量映射表 (VAR_OUTPUT - 30个)

| 原变量名(中文) | 新变量名(英文) | 类型 | 说明 |
|:---|:---|:---|:---|
| o_b升降_上升 | o_bLift_Up | BOOL | 升降上升 |
| o_b升降_下降 | o_bLift_Down | BOOL | 升降下降 |
| o_b前夹紧_夹紧 | o_bFrontGrip_Close | BOOL | 前夹紧夹紧 |
| o_b前夹紧_松开 | o_bFrontGrip_Open | BOOL | 前夹紧松开 |
| o_b后夹紧_夹紧 | o_bRearGrip_Close | BOOL | 后夹紧夹紧 |
| o_b后夹紧_松开 | o_bRearGrip_Open | BOOL | 后夹紧松开 |
| o_b前夹紧2_夹紧 | o_bFrontGrip2_Close | BOOL | 前夹紧2夹紧 |
| o_b前夹紧2_松开 | o_bFrontGrip2_Open | BOOL | 前夹紧2松开 |
| o_b后夹紧2_夹紧 | o_bRearGrip2_Close | BOOL | 后夹紧2夹紧 |
| o_b后夹紧2_松开 | o_bRearGrip2_Open | BOOL | 后夹紧2松开 |
| o_bZ轴_脉冲输出 | o_bZAxis_PulseOutput | BOOL | Z轴脉冲 |
| o_bZ轴_方向输出 | o_bZAxis_DirectionOutput | BOOL | Z轴方向 |
| o_bZ轴_伺服使能 | o_bZAxis_ServoEnable | BOOL | Z轴伺服使能 |
| o_bX1轴_脉冲输出 | o_bX1Axis_PulseOutput | BOOL | X1轴脉冲 |
| o_bX1轴_方向输出 | o_bX1Axis_DirectionOutput | BOOL | X1轴方向 |
| o_bX1轴_伺服使能 | o_bX1Axis_ServoEnable | BOOL | X1轴伺服使能 |
| o_b放料完成信号 | o_bFeedCompleteSignal | BOOL | 放料完成 |
| o_b安全区进入许可 | o_bSafetyZoneEntryAllow | BOOL | 安全区许可 |
| o_b运行中 | o_bRunning | BOOL | 运行中 |
| o_b故障 | o_bFault | BOOL | 故障 |
| o_i当前状态 | o_iCurrentState | INT | 当前状态 |
| o_rZ轴当前位置 | o_rZAxis_CurrentPosition | REAL | Z轴位置 |
| o_rX1轴当前位置 | o_rX1Axis_CurrentPosition | REAL | X1轴位置 |
| o_i本站报警代码 | o_iStationAlarmCode | INT | 报警代码 |
| q_e取料定时器_ET | q_ePickupTimer_ET | TIME | 取料定时器 |
| q_e放料定时器_ET | q_ePlaceTimer_ET | TIME | 放料定时器 |
| q_e升降定时器_ET | q_eLiftTimer_ET | TIME | 升降定时器 |
| q_e夹紧定时器_ET | q_eGripTimer_ET | TIME | 夹紧定时器 |

---

## MODIFIED Requirements

### Requirement: 三层架构一致性
修改后的 FB_ExternalDeviceInteraction 和 FB_1003_PickPlace SHALL 与以下组件100%一致：
- GlobalVars.db V3.0.0 的变量定义
- OB1.scl V5.0.0 的功能块调用参数
- 符合 801_PLC变量命名与功能块规范_DEV-V1.0.5

### Requirement: 内部代码同步
两个FB的**内部实现代码**中所有引用接口变量的地方 SHALL 同步替换为新变量名，确保：
- 无 TC001 (未声明符号) 错误
- 无 TC002 (类型不匹配) 错误
- 业务逻辑 100% 不变
