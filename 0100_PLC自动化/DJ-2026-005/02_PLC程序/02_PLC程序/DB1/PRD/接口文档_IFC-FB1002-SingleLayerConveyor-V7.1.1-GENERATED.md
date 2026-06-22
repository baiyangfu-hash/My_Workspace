# 接口文档 FB_1002 四层输送机系统

## 0. 文档基础信息

| 属性 | 值 |
|------|-----|
| **文档标题** | FB_1002 四层输送机系统 接口定义 |
| **文档版本** | V7.1.1 |
| **数据来源** | GlobalVars.db V7.1.1 |
| **编制日期** | 2026-05-21 |
| **生成方式** | 半自动(ifc_generator.py) — 需人工审核补充 |

## 1. 功能概述

> [待人工补充: 功能块总体描述]

## 2. stConveyor 接口 (21输入 / 14输出)

### 2.1 VAR_INPUT (21个)

| 名称 | 类型 | 默认值 | 说明 | 来源 |
|------|------|--------|------|------|
| i_bAutoMode | BOOL | FALSE | 自动运行模式 | [待补充] |
| i_bManualMode | BOOL | FALSE | 手动调试模式 | [待补充] |
| i_bStart | BOOL | FALSE | 自动循环启动 (上升沿) | [待补充] |
| i_bStop | BOOL | FALSE | 停止 (电平有效) | [待补充] |
| i_iSeparateTimeoutMs | INT | 5000 | 分料超时时间 (ms) | [待补充] |
| i_bSafetyDoorOk | BOOL | TRUE | 安全门状态 (TRUE=关闭OK) | [待补充] |
| i_bVfdFault | BOOL | FALSE | 变频器故障 | [待补充] |
| i_aPreSeparateSensor | ARRAY[1..4] OF BOOL | - | 分料前接近开关 | [待补充] |
| i_aPositionSensor1 | ARRAY[1..4] OF BOOL | - | 到位传感器1 | [待补充] |
| i_aPositionSensor2 | ARRAY[1..4] OF BOOL | - | 到位传感器2 (冗余) | [待补充] |
| i_aBlockCylinderUp | ARRAY[1..4] OF BOOL | - | 阻挡气缸上位 | [待补充] |
| i_aBlockCylinderDown | ARRAY[1..4] OF BOOL | - | 阻挡气缸下位 | [待补充] |
| i_aSeparateCylinderUp | ARRAY[1..4] OF BOOL | - | 分料气缸上位 | [待补充] |
| i_aSeparateCylinderDown | ARRAY[1..4] OF BOOL | - | 分料气缸下位 | [待补充] |
| i_aPickupConfirmed | ARRAY[1..4] OF BOOL | - | 取料机构已取走物料 (←FB_1003) | [待补充] |
| i_aManBlockExtend | ARRAY[1..4] OF BOOL | - | 手动: 阻挡下降 | [待补充] |
| i_aManBlockRetract | ARRAY[1..4] OF BOOL | - | 手动: 阻挡上升 | [待补充] |
| i_aManSeparatePush | ARRAY[1..4] OF BOOL | - | 手动: 分料推出 | [待补充] |
| i_aManConveyorFwd | ARRAY[1..4] OF BOOL | - | 手动: 输送正转 | [待补充] |
| i_aManConveyorRev | ARRAY[1..4] OF BOOL | - | 手动: 输送反转 | [待补充] |
| i_aManConveyorSlow | ARRAY[1..4] OF BOOL | - | 手动: 输送慢速 | [待补充] |

### 2.2 VAR_OUTPUT (14个)

| 名称 | 类型 | 默认值 | 说明 | 目标 |
|------|------|--------|------|------|
| q_aBlockSolenoid | ARRAY[1..4] OF BOOL | - | 阻挡电磁阀 (TRUE=下降) | [待补充] |
| q_aSeparateSolenoid | ARRAY[1..4] OF BOOL | - | 分料电磁阀 (TRUE=推出) | [待补充] |
| q_aConveyorFwd | ARRAY[1..4] OF BOOL | - | 输送带正转 | [待补充] |
| q_aConveyorRev | ARRAY[1..4] OF BOOL | - | 输送带反转 | [待补充] |
| q_aConveyorSlow | ARRAY[1..4] OF BOOL | - | 输送带慢速 | [待补充] |
| q_aLayerStep | ARRAY[1..4] OF INT | - | 各层当前步序 0~70 (HMI) | [待补充] |
| q_aLayerAlarmCode | ARRAY[1..4] OF INT | - | 各层报警码 0=正常 (HMI) | [待补充] |
| q_aLayerRunning | ARRAY[1..4] OF BOOL | - | 各层运行中 (HMI) | [待补充] |
| q_aLayerFault | ARRAY[1..4] OF BOOL | - | 各层故障 (HMI) | [待补充] |
| q_aLayerFeedDone | ARRAY[1..4] OF BOOL | - | 各层放料完成 脉冲 (→FB_1003) | [待补充] |
| q_aLayerSensorFault | ARRAY[1..4] OF BOOL | - | 各层传感器故障 (→FB_2001) | [待补充] |
| q_bRunning | BOOL | FALSE | 4层 OR → HMI "输送机运行中" | [待补充] |
| q_bFault | BOOL | FALSE | 4层 OR → HMI + 全局互锁 | [待补充] |
| q_iAlarmCode | INT | 0 | 4层报警码优先级 MIN → HMI + FB_2001 | [待补充] |

---

> **接口统计**: 21输入 + 14输出
> **数据来源**: GlobalVars.db V7.1.1 → ifc_generator.py 自动生成
> **⚠ 本文件由 IFC 生成器自动生成，请人工审核后替换正式文档**

**人工审核清单**:
- [ ] 补充 §1 功能概述
- [ ] 补全所有 [待补充] 来源/目标列
- [ ] 添加状态机步序常量表 (如有)
- [ ] 添加地址映射信息 (D寄存器/Y地址)
- [ ] 确认变量分类正确 (输入/输出)
- [ ] 确认版本号与代码一致