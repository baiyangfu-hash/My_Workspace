# 接口文档 FB_1003 取放料机构

## 0. 文档基础信息

| 属性 | 值 |
|------|-----|
| **文档标题** | FB_1003 取放料机构 接口定义 |
| **文档版本** | V7.1.1 |
| **数据来源** | GlobalVars.db V7.1.1 |
| **编制日期** | 2026-05-21 |
| **生成方式** | 半自动(ifc_generator.py) — 需人工审核补充 |

## 1. 功能概述

> [待人工补充: 功能块总体描述]

## 2. stPickPlace 接口 (57输入 / 26输出)

### 2.1 VAR_INPUT (57个)

| 名称 | 类型 | 默认值 | 说明 | 来源 |
|------|------|--------|------|------|
| i_bEnable | BOOL | FALSE | 总使能信号 | [待补充] |
| i_bAutoMode | BOOL | FALSE | 自动运行模式选择 | [待补充] |
| i_bManualMode | BOOL | FALSE | 手动调试模式选择 | [待补充] |
| i_bStart | BOOL | FALSE | 自动循环启动按钮 (上升沿触发) | [待补充] |
| i_bStop | BOOL | FALSE | 自动循环停止按钮 (电平有效) | [待补充] |
| i_bReset | BOOL | FALSE | 故障复位/初始化按钮 (电平有效) | [待补充] |
| i_bLx_ZAxis_JogUp | BOOL | FALSE | 手动-Z轴点动上升 | [待补充] |
| i_bLx_ZAxis_JogDown | BOOL | FALSE | 手动-Z轴点动下降 | [待补充] |
| i_bLx_X1Axis_JogFwd | BOOL | FALSE | 手动-X1轴点动前进 (取料方向) | [待补充] |
| i_bLx_X1Axis_JogRev | BOOL | FALSE | 手动-X1轴点动后退 (放料方向) | [待补充] |
| i_bLx_Lift_Up | BOOL | FALSE | 手动-升降气缸上升 | [待补充] |
| i_bLx_Lift_Down | BOOL | FALSE | 手动-升降气缸下降 | [待补充] |
| i_bLx_FrontClamp | BOOL | FALSE | 手动-前夹爪夹紧 | [待补充] |
| i_bLx_FrontUnclamp | BOOL | FALSE | 手动-前夹爪松开 | [待补充] |
| i_bLx_RearClamp | BOOL | FALSE | 手动-后夹爪夹紧 | [待补充] |
| i_bLx_RearUnclamp | BOOL | FALSE | 手动-后夹爪松开 | [待补充] |
| i_bLx_FrontClamp2 | BOOL | FALSE | 手动-前夹爪2夹紧 (第二前夹爪) | [待补充] |
| i_bLx_FrontUnclamp2 | BOOL | FALSE | 手动-前夹爪2松开 | [待补充] |
| i_bLx_RearClamp2 | BOOL | FALSE | 手动-后夹爪2夹紧 (第二后夹爪) | [待补充] |
| i_bLx_RearUnclamp2 | BOOL | FALSE | 手动-后夹爪2松开 | [待补充] |
| i_rPickupSpeed | REAL | 100.0 | 取料过程Z轴升降速度 (mm/s 或 %) | [待补充] |
| i_rPlaceSpeed | REAL | 80.0 | 放料过程Z轴升降速度 (mm/s 或 %) | [待补充] |
| i_rZAxisSpeed | REAL | 100.0 | Z轴通用运动速度设定 (mm/s) | [待补充] |
| i_rX1AxisSpeed | REAL | 150.0 | X1轴通用运动速度设定 (mm/s) | [待补充] |
| i_iClampConfirmTime | INT | 500 | 夹爪夹紧确认等待时间 (ms) | [待补充] |
| i_iLiftActionTime | INT | 3000 | 升降气缸动作超时时间 (ms) | [待补充] |
| i_iPickLayer_Input | INT | 0 | 外部指定的当前取料层号(1~4), 0=无效 (HMI/上位机设置) | [待补充] |
| i_bLift_WorkPoint | BOOL | FALSE | 升降气缸下降位 (工作点) | [待补充] |
| i_bLift_HomePos | BOOL | FALSE | 升降气缸上升位 (原点) | [待补充] |
| i_bFrontClamp_Closed | BOOL | FALSE | 前夹爪夹紧位 (工作点) | [待补充] |
| i_bFrontClamp_Opened | BOOL | FALSE | 前夹爪松开位 (原点) | [待补充] |
| i_bRearClamp_Closed | BOOL | FALSE | 后夹爪夹紧位 (工作点) | [待补充] |
| i_bRearClamp_Opened | BOOL | FALSE | 后夹爪松开位 (原点) | [待补充] |
| i_bFrontClamp2_Closed | BOOL | FALSE | 前夹爪2夹紧位 (工作点) | [待补充] |
| i_bFrontClamp2_Opened | BOOL | FALSE | 前夹爪2松开位 (原点) | [待补充] |
| i_bRearClamp2_Closed | BOOL | FALSE | 后夹爪2夹紧位 (工作点) | [待补充] |
| i_bRearClamp2_Opened | BOOL | FALSE | 后夹爪2松开位 (原点) | [待补充] |
| i_bLongEdge1Detect | BOOL | FALSE | 长边1到位检测 (光电传感器) | [待补充] |
| i_bLongEdge2Detect | BOOL | FALSE | 长边2到位检测 (光电传感器) | [待补充] |
| i_bShortEdge1Detect | BOOL | FALSE | 短边1到位检测 (光电传感器) | [待补充] |
| i_bShortEdge2Detect | BOOL | FALSE | 短边2到位检测 (光电传感器) | [待补充] |
| i_bZAxis_HomePos | BOOL | FALSE | Z轴伺服原点信号 (Home/ORG) | [待补充] |
| i_bX1Axis_HomePos | BOOL | FALSE | X1轴伺服原点信号 | [待补充] |
| i_bX2Axis_HomePos | BOOL | FALSE | X2轴伺服原点信号 (预留) | [待补充] |
| i_bZAxis_ServoFault | BOOL | FALSE | Z轴伺服驱动器故障 (ALM输出) | [待补充] |
| i_bX1Axis_ServoFault | BOOL | FALSE | X1轴伺服驱动器故障 (ALM输出) | [待补充] |
| i_bX2Axis_ServoFault | BOOL | FALSE | X2轴伺服驱动器故障 (预留) | [待补充] |
| i_bZAxis_FwdLimit | BOOL | FALSE | Z轴正限位 (上限位) | [待补充] |
| i_bZAxis_RevLimit | BOOL | FALSE | Z轴负限位 (下限位) | [待补充] |
| i_bX1Axis_FwdLimit | BOOL | FALSE | X1轴正限位 (取料侧限位) | [待补充] |
| i_bX1Axis_RevLimit | BOOL | FALSE | X1轴负限位 (放料侧限位) | [待补充] |
| i_bX2Axis_FwdLimit | BOOL | FALSE | X2轴正限位 (预留) | [待补充] |
| i_bX2Axis_RevLimit | BOOL | FALSE | X2轴负限位 (预留) | [待补充] |
| i_bConveyor_L1_FeedComplete | BOOL | FALSE | 输送机第1层送料完成 | [待补充] |
| i_bConveyor_L2_FeedComplete | BOOL | FALSE | 输送机第2层送料完成 | [待补充] |
| i_bConveyor_L3_FeedComplete | BOOL | FALSE | 输送机第3层送料完成 | [待补充] |
| i_bConveyor_L4_FeedComplete | BOOL | FALSE | 输送机第4层送料完成 | [待补充] |

### 2.2 VAR_OUTPUT (26个)

| 名称 | 类型 | 默认值 | 说明 | 目标 |
|------|------|--------|------|------|
| o_bLift_Up | BOOL | FALSE | 升降气缸上升电磁阀 -> Y地址 | [待补充] |
| o_bLift_Down | BOOL | FALSE | 升降气缸下降电磁阀 -> Y地址 | [待补充] |
| o_bFrontClamp_Action | BOOL | FALSE | 前夹爪夹紧电磁阀 -> Y地址 | [待补充] |
| o_bFrontClamp_Release | BOOL | FALSE | 前夹爪松开电磁阀 -> Y地址 | [待补充] |
| o_bRearClamp_Action | BOOL | FALSE | 后夹爪夹紧电磁阀 -> Y地址 | [待补充] |
| o_bRearClamp_Release | BOOL | FALSE | 后夹爪松开电磁阀 -> Y地址 | [待补充] |
| o_bFrontClamp2_Action | BOOL | FALSE | 前夹爪2夹紧电磁阀 -> Y地址 | [待补充] |
| o_bFrontClamp2_Release | BOOL | FALSE | 前夹爪2松开电磁阀 -> Y地址 | [待补充] |
| o_bRearClamp2_Action | BOOL | FALSE | 后夹爪2夹紧电磁阀 -> Y地址 | [待补充] |
| o_bRearClamp2_Release | BOOL | FALSE | 后夹爪2松开电磁阀 -> Y地址 | [待补充] |
| o_bZAxis_PulseOutput | BOOL | FALSE | Z轴脉冲输出使能 -> Y0 (PULSE) | [待补充] |
| o_bZAxis_DirectionOutput | BOOL | FALSE | Z轴方向控制 -> Y4 (SIGN) | [待补充] |
| o_bZAxis_Enable | BOOL | FALSE | Z轴伺服使能 (SON) -> Y10 | [待补充] |
| o_bPlaceComplete_ToFeeder | BOOL | FALSE | 放料完成通知下游 (打胶机可取料) | [待补充] |
| o_bRunning | BOOL | FALSE | 本站当前自动运行中 | [待补充] |
| o_bFault | BOOL | FALSE | 本站有故障 (任意报警激活) | [待补充] |
| o_iCurrentState | INT | 0 | 当前状态机步骤 (0~10, 99=故障) | [待补充] |
| o_rZAxisCurrentPos | REAL | 0.0 | Z轴当前位置反馈 (mm, 来自主控映射) | [待补充] |
| o_rX1AxisCurrentPos | REAL | 0.0 | X1轴当前位置反馈 (mm, 来自主控映射) | [待补充] |
| o_rX2AxisCurrentPos | REAL | 0.0 | X2轴当前位置反馈 (mm, 预留, 来自主控映射) | [待补充] |
| o_iCurrentPickLayer | INT | 0 | 当前取料层号 (0=空闲, 1~4=层号) | [待补充] |
| o_iStationAlarmCode | INT | 0 | 本站当前有效报警代码 (0=无报警, 101~199=报警类型) | [待补充] |
| q_ePlaceCompleteHold_Elapsed | DINT | - | 放料完成保持定时器已耗时间 (ms) | [待补充] |
| q_eAction_Elapsed | DINT | - | 通用动作定时器已耗时间 (ms) | [待补充] |
| q_eProductDetectStable_Elapsed | DINT | - | 产品检测稳定定时器已耗时间 (ms) | [待补充] |
| q_eInit_Elapsed | DINT | - | 初始化定时器已耗时间 (ms) | [待补充] |

---

> **接口统计**: 57输入 + 26输出
> **数据来源**: GlobalVars.db V7.1.1 → ifc_generator.py 自动生成
> **⚠ 本文件由 IFC 生成器自动生成，请人工审核后替换正式文档**

**人工审核清单**:
- [ ] 补充 §1 功能概述
- [ ] 补全所有 [待补充] 来源/目标列
- [ ] 添加状态机步序常量表 (如有)
- [ ] 添加地址映射信息 (D寄存器/Y地址)
- [ ] 确认变量分类正确 (输入/输出)
- [ ] 确认版本号与代码一致