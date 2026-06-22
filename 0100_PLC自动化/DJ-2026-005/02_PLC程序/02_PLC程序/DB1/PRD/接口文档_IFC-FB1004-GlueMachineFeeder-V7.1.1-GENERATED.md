# 接口文档 FB_1004 打胶机送料机构

## 0. 文档基础信息

| 属性 | 值 |
|------|-----|
| **文档标题** | FB_1004 打胶机送料机构 接口定义 |
| **文档版本** | V7.1.1 |
| **数据来源** | GlobalVars.db V7.1.1 |
| **编制日期** | 2026-05-21 |
| **生成方式** | 半自动(ifc_generator.py) — 需人工审核补充 |

## 1. 功能概述

> [待人工补充: 功能块总体描述]

## 2. stFeeder 接口 (16输入 / 13输出)

### 2.1 VAR_INPUT (16个)

| 名称 | 类型 | 默认值 | 说明 | 来源 |
|------|------|--------|------|------|
| i_bEnable | BOOL | FALSE | 总使能信号 | [待补充] |
| i_bAutoMode | BOOL | FALSE | 自动运行模式选择 | [待补充] |
| i_bManualMode | BOOL | FALSE | 手动调试模式选择 | [待补充] |
| i_bStart | BOOL | FALSE | 自动循环启动按钮 (上升沿触发) | [待补充] |
| i_bStop | BOOL | FALSE | 自动循环停止按钮 (电平有效) | [待补充] |
| i_bReset | BOOL | FALSE | 故障复位/初始化按钮 (电平有效) | [待补充] |
| i_bLx_X2Axis_JogFwd | BOOL | FALSE | 手动-X2轴点动前进 (至打胶机取料位置) | [待补充] |
| i_bLx_X2Axis_JogRev | BOOL | FALSE | 手动-X2轴点动后退 (返回待机位置) | [待补充] |
| i_rFeedSpeed | REAL | 120.0 | X2轴送料运动速度 (mm/s 或 %) | [待补充] |
| i_bX2Axis_Home | BOOL | FALSE | X2轴伺服原点信号 (Home/ORG) | [待补充] |
| i_bX2Axis_ForwardLimit | BOOL | FALSE | X2轴正限位 (向打胶机侧限位) | [待补充] |
| i_bX2Axis_ReverseLimit | BOOL | FALSE | X2轴负限位 (待机位置侧限位) | [待补充] |
| i_bX2Axis_ServoFault | BOOL | FALSE | X2轴伺服驱动器故障 (ALM输出) | [待补充] |
| i_bGlueMachine_AllowFeed | BOOL | FALSE | 打胶机允许送料信号 (对应物理地址 X76) | [待补充] |
| i_bGlueMachine_PickupComplete | BOOL | FALSE | 打胶机取料完成信号 (对应物理地址 X102) | [待补充] |
| i_bPickPlace_FeedComplete | BOOL | FALSE | 取放料机构送料完成信号 | [待补充] |

### 2.2 VAR_OUTPUT (13个)

| 名称 | 类型 | 默认值 | 说明 | 目标 |
|------|------|--------|------|------|
| o_bAllowPickup | BOOL | FALSE | 允许取料信号 -> 主控映射至 Y44 | [待补充] |
| o_bX2Axis_RequestFwd | BOOL | FALSE | X2轴正转移动请求 (至打胶机取料位置) | [待补充] |
| o_bX2Axis_RequestRev | BOOL | FALSE | X2轴反转移动请求 (返回待机位置) | [待补充] |
| o_bSafetyZoneSignal | BOOL | FALSE | 安全区信号 -> 主控映射至 Y47 | [待补充] |
| o_bRunning | BOOL | FALSE | 本站当前自动运行中 | [待补充] |
| o_bFault | BOOL | FALSE | 本站有故障 (任意报警激活) | [待补充] |
| o_iCurrentState | INT | 0 | 当前状态机步骤 (0~5, 99=故障) | [待补充] |
| o_rX2Axis_CurrentPosition | REAL | 0.0 | X2轴当前位置反馈 (mm, 来自主控映射) | [待补充] |
| o_iStationAlarmCode | INT | 0 | 本站当前有效报警代码 (0=无报警, 201~299=报警类型) | [待补充] |
| q_eCommTimeout_Elapsed | DINT | - | 通信超时定时器已耗时间 (ms) | [待补充] |
| q_eAction_Elapsed | DINT | - | 动作定时器已耗时间 (ms) | [待补充] |
| q_eInit_Elapsed | DINT | - | 初始化定时器已耗时间 (ms) | [待补充] |
| q_ePickupHold_Elapsed | DINT | - | 取料保持定时器已耗时间 (ms) | [待补充] |

---

> **接口统计**: 16输入 + 13输出
> **数据来源**: GlobalVars.db V7.1.1 → ifc_generator.py 自动生成
> **⚠ 本文件由 IFC 生成器自动生成，请人工审核后替换正式文档**

**人工审核清单**:
- [ ] 补充 §1 功能概述
- [ ] 补全所有 [待补充] 来源/目标列
- [ ] 添加状态机步序常量表 (如有)
- [ ] 添加地址映射信息 (D寄存器/Y地址)
- [ ] 确认变量分类正确 (输入/输出)
- [ ] 确认版本号与代码一致