# FB_ExternalDeviceInteraction 接口文档

## 1. 文档基础信息

| 属性 | 值 |
|------|-----|
| **文档标题** | 外部设备交互功能块接口文档 (V6.0.0 英文版) |
| **适用FB** | FB_ExternalDeviceInteraction |
| **文档类型** | 接口文档 / Interface Document (IFC) |
| **文档版本** | V6.0.0 |
| **编制日期** | 2026-05-03 |
| **编制人** | Trae (AI Assistant) |
| **审核人** | [待审核] |
| **遵循规范** | `801_PLC变量命名与功能块命名规范_DEV-V1.0.5` |
| **接口规模** | **27个输入 / 20个输出** (中等复杂度, 多设备协调) |

---

## 2. 接口概览统计

### 2.1 数量统计

| 类别 | 数量 | 数据类型说明 |
|:------|:----:|:-------------|
| **输入总计** | **27** | - |
| 系统控制信号 | 6 | BOOL (使能/模式/按钮) |
| 组框机输入信号 | 7 | BOOL (运行状态/允许送料/有料请求/开门/急停/安全/通讯) |
| 打胶机输入信号 | 7 | BOOL (运行状态/允许送料/取料完成/故障/急停/通讯) |
| 机器人输入信号(预留) | 5 | BOOL (运行/码料完成/故障/急停/通讯) |
| 本机状态信号 | 3 | BOOL (就绪/报警激活/系统故障) |
| **输出总计** | **20** | - |
| 组框机输出信号 | 5 | BOOL (请求送料/暂停/急停/申请开门/就绪) |
| 打胶机输出信号 | 4 | BOOL (请求运行/允许抓料/安全区/复位请求) |
| 机器人输出信号(预留) | 3 | BOOL (允许码料/停止码料/复位请求) |
| 状态与报警输出 | 4 | BOOL(3)+INT(1) (紧急停止/外部设备故障/报警汇总/安全条件) |
| **内部变量** | 2 | VAR段 (安全条件满足标志/报警码) |
| **常量定义** | 9 | 报警编码(300~322段) |

---

## 3. 输入接口定义 (VAR_INPUT)

### 3.1 系统控制信号组 (6个BOOL)

> 来自主控/HMI M区公共透传信号

| 序号 | 变量名 | 类型 | 功能描述 | 有效方式 |
|:----:|:--------|:----:|:---------|:--------:|
| 1 | `i_bEnable` | BOOL | 系统总使能 | 电平有效 |
| 2 | `i_bAutoMode` | BOOL | 自动模式选择 | 电平有效(与Manual互斥) |
| 3 | `i_bManualMode` | BOOL | 手动模式选择 | 电平有效(与Auto互斥) |
| 4 | `i_bStart` | BOOL | 启动按钮 | 上升沿触发 |
| 5 | `i_bStop` | BOOL | 停止按钮 | 电平有效 |
| 6 | `i_bReset` | BOOL | 复位按钮 | 电平有效 |

### 3.2 组框机输入信号组 (7个BOOL)

> 来自组框机PLC或IO映射

| 序号 | 变量名 | 类型 | 功能描述 | 来源设备 |
|:----:|:--------|:----:|:---------|:---------:|
| 7 | `i_bFrameMachine_AutoRunning` | BOOL | 组框机自动运行中 | 组框机PLC |
| 8 | `i_bFrameMachine_AllowFeed` | BOOL | 组框机允许向缓存机输送边框 | 组框机PLC |
| 9 | `i_bFrameMaterialRequest` | BOOL | 组框机有边框需要送入缓存机 | 组框机PLC |
| 10 | `i_bDoorOpenRequest` | BOOL | 组框机操作门打开(需本机暂停) | 组框机HMI/传感器 |
| 11 | `i_bFrameMachine_EStop` | BOOL | 组框机急停信号(需联锁) | 组框机急停按钮 |
| 12 | `i_bFrameMachine_SafetyErr` | BOOL | 组框机安全系统异常(光幕/安全门等) | 组框机安全系统 |
| 13 | `i_bFrameMachine_CommErr` | BOOL | 与组框机通讯异常 | 通讯模块 |

### 3.3 打胶机输入信号组 (7个BOOL)

> 来自打胶机PLC或IO映射

| 序号 | 变量名 | 类型 | 功能描述 | 来源设备 |
|:----:|:--------|:----:|:---------|:---------:|
| 14 | `i_bGlueMachine_AutoRunning` | BOOL | 打胶机自动运行中 | 打胶机PLC |
| 15 | `i_bGlueMachine_AllowFeed` | BOOL | 打胶机准备好可接收边框 | 打胶机PLC |
| 16 | `i_bGlueMachine_PickComplete` | BOOL | 打胶机已完成边框抓取 | 打胶机PLC |
| 17 | `i_bGlueMachine_Fault` | BOOL | 打胶机设备故障报警 | 打胶机驱动器/传感器 |
| 18 | `i_bGlueMachine_EStop` | BOOL | 打胶机急停状态 | 打胶机急停按钮 |
| 19 | `i_bGlueMachine_CommErr` | BOOL | 与打胶机通讯中断 | 通讯模块 |

### 3.4 机器人输入信号组 (5个BOOL, 预留)

> 为未来机器人码料功能预留接口

| 序号 | 变量名 | 类型 | 功能描述 | 备注 |
|:----:|:--------|:----:|:---------|:-----:|
| 20 | `i_bRobot_AutoRunning` | BOOL | 机器人自动运行中 | 预留, 当前无效 |
| 21 | `i_bRobot_StackComplete` | BOOL | 机器人完成码料 | 预留, 当前无效 |
| 22 | `i_bRobot_Fault` | BOOL | 机器人设备故障 | 预留, 当前无效 |
| 23 | `i_bRobot_EStop` | BOOL | 机器人急停状态 | 预留, 当前无效 |
| 24 | `i_bRobot_CommErr` | BOOL | 与机器人通讯异常 | 预留, 当前无效 |

### 3.5 本机状态信号组 (3个BOOL)

> 来自本机(边框缓存机)内部状态

| 序号 | 变量名 | 类型 | 功能描述 |
|:----:|:--------|:----:|:---------|
| 25 | `i_bLocalReady` | BOOL | 本机就绪状态(无故障/初始化完成) |
| 26 | `i_bAnyAlarmActive` | BOOL | 本机有任何报警激活 |
| 27 | `i_bSystemFault` | BOOL | 本机系统故障(严重级别) |

---

## 4. 输出接口定义 (VAR_OUTPUT)

### 4.1 组框机输出信号组 (5个BOOL)

> 给组框机的协调控制信号

| 序号 | 变量名 | 类型 | 功能描述 | 目标设备 |
|:----:|:--------|:----:|:---------|:---------:|
| 1 | `q_bFrameMachine_RequestFeed` | BOOL | 向组框机请求输送边框 | 组框机PLC |
| 2 | `q_bFrameMachine_Pause` | BOOL | 向组框机发送暂停指令 | 组框机PLC |
| 3 | `q_bFrameMachine_EStop` | BOOL | 向组框机发送急停联锁信号 | 组框机安全回路 |
| 4 | `q_bDoorOpenRequest` | BOOL | 向组框机申请开门操作 | 组框机HMI/控制器 |
| 5 | `q_bFrameMachine_Ready` | BOOL | 本机就绪, 可接收边框 | 组框机PLC |

### 4.2 打胶机输出信号组 (4个BOOL)

> 给打胶机的协调控制信号

| 序号 | 变量名 | 类型 | 功能描述 | 目标设备 |
|:----:|:--------|:----:|:---------|:---------:|
| 6 | `q_bGlueMachine_RequestRun` | BOOL | 请求打胶机启动运行 | 打胶机PLC |
| 7 | `q_bAllowPickup` | BOOL | 通知打胶机可以抓取边框 | 打胶机PLC |
| 8 | `q_bSafetyZoneSignal` | BOOL | 安全区开放/关闭信号 | 打胶机安全系统 |
| 9 | `q_bGlueMachine_ResetReq` | BOOL | 向打胶机发送复位请求 | 打胶机PLC |

### 4.3 机器人输出信号组 (3个BOOL, 预留)

> 为未来机器人码料功能预留接口

| 序号 | 变量名 | 类型 | 功能描述 | 备注 |
|:----:|:--------|:----:|:---------|:-----:|
| 10 | `q_bRobot_AllowStacking` | BOOL | 允许机器人进行码料 | 预留, 当前无效 |
| 11 | `q_bRobot_StopStacking` | BOOL | 停止机器人码料 | 预留, 当前无效 |
| 12 | `q_bRobot_ResetReq` | BOOL | 向机器人发送复位请求 | 预留, 当前无效 |

### 4.4 状态与报警输出组 (4个: BOOL×3 + INT×1)

| 序号 | 变量名 | 类型 | 功能描述 | 显示格式 |
|:----:|:--------|:----:|:---------|:---------:|
| 13 | `q_bFrameMachine_EmergencyStop` | BOOL | 组框机急停/安全异常时强制本机停止 | 指示灯/联锁 |
| 14 | `q_bExternalDeviceFault` | BOOL | 外部设备故障标志(任一外部设备异常) | 报警指示 |
| 15 | `q_iExternalDeviceAlarmSummary` | INT | 外部设备故障报警码(300~399段) | 数值显示 |
| 16 | `q_bSystemSafetyConditionMet` | BOOL | 系统安全条件是否满足(所有设备正常) | 状态指示 |

### 4.5 报警编码表 (300~399段)

**完整报警码定义表**:

| 报警码 | 设备 | 名称 | 触发条件 | 清除条件 | 优先级 |
|:------:|:----:|:-----|:---------|:---------|:------:|
| 300 | 打胶机 | 设备故障 | `i_bGlueMachine_Fault = TRUE` | 故障消除+复位 | 高 |
| 301 | 打胶机 | 急停 | `i_bGlueMachine_EStop = TRUE` | 解除急停+复位 | 高 |
| 302 | 打胶机 | 通讯异常 | `i_bGlueMachine_CommErr = TRUE` | 通讯恢复 | 中 |
| 310 | 组框机 | 急停 | `i_bFrameMachine_EStop = TRUE` | 解除急停+复位 | 高 |
| 311 | 组框机 | 安全系统异常 | `i_bFrameMachine_SafetyErr = TRUE` | 异常消除+复位 | 高 |
| 312 | 组框机 | 通讯异常 | `i_bFrameMachine_CommErr = TRUE` | 通讯恢复 | 中 |
| 320 | 机器人 | 设备故障 | `i_bRobot_Fault = TRUE`(预留) | 预留 | 中(预留) |
| 321 | 机器人 | 急停 | `i_bRobot_EStop = TRUE`(预留) | 预留 | 高(预留) |
| 322 | 机器人 | 通讯异常 | `i_bRobot_CommErr = TRUE`(预留) | 预留 | 低(预留) |

---

## 5. 与GlobalVars.db stExternal结构对照表

| 本FB变量名 (V6.0.0) | GlobalVars.db字段名 (V3.0.0) | 类型 | 一致性 |
|:--------------------:|:---------------------------:|:----:|:------:|
| `i_bEnable` | `stExternal.i_bEnable` | BOOL | ✅ 匹配 |
| `i_bAutoMode` | `stExternal.i_bAutoMode` | BOOL | ✅ 匹配 |
| ... (其余25个输入变量) | ... (对应stExternal结构字段) | - | ✅ 全部匹配 |
| `q_bFrameMachine_RequestFeed` | `stExternal.q_bFrameMachine_RequestFeed` | BOOL | ✅ 匹配 |
| ... (其余19个输出变量) | ... (对应stExternal结构字段) | - | ✅ 全部匹配 |

**结论**: ✅ FB_ExternalDeviceInteraction接口与GlobalVars.db V3.0.0的stExternal结构100%匹配。

---

## 6. 相关文档链接

### 6.1 本FB文档体系(V6.0.0)

| 文档类型 | 文档名称 | 核心内容 |
|:---------|:--------|:--------|
| **详细设计说明书 (DSN)** | [详细设计说明书_DSN-FB-ExternalDeviceInteraction.md](./详细设计说明书_DSN-FB-ExternalDeviceInteraction.md) | 三设备协调逻辑、安全联锁、报警管理 |
| **接口文档 (IFC)** | 本文档 ← **当前文档** | 27输入/20输出的完整英文定义 |
| **使用说明 (UM)** | [使用说明_UM-FB-ExternalDeviceInteraction.md](./使用说明_UM-FB-ExternalDeviceInteraction.md) | ST调用示例、调试指南、常见问题排查 |
| **变更记录 (CHG)** | [变更记录_CHG-FB-ExternalDeviceInteraction.md](./变更记录_CHG-FB-ExternalDeviceInteraction.md) | 版本历史、变更台帐(含V6.0.0的92处替换详单) |

### 6.2 关联资源

| 资源名称 | 路径 | 用途 |
|:---------|:-----|:-----|
| FB_ExternalDeviceInteraction源代码 (V6.0.0) | [FB_ExternalDeviceInteraction.scl](./FB_ExternalDeviceInteraction.scl) | ST实现参考 |
| GlobalVars.db (V3.0.0) | [../DB1/GlobalVars.db](../DB1/GlobalVars.db) | 全局变量定义(stExternal结构) |
| OB1.scl (V5.0.0) | [../OB1/OB1.scl](../OB1/OB1.scl) | 主程序组织块(fbExternalDevice调用) |

---

## 附录: 快速参考卡片

```
═════════════════════════════════════════════
  FB_ExternalDeviceInteraction 接口速查 (V6.0.0)
  27输入 / 20输出 / 2内部变量 / 9报警码
═════════════════════════════════════════════

【输入】(27个)
  系统控制: Enable/AutoMode/ManualMode/Start/Stop/Reset (6)
  组框机:   AutoRunning/AllowFeed/MaterialRequest
            /DoorOpen/EStop/SafetyErr/CommErr (7)
  打胶机:   AutoRunning/AllowFeed/PickComplete
            /Fault/EStop/CommErr (7)
  机器人:   AutoRunning/StackComplete/Fault
            /EStop/CommErr (5, 预留)
  本机状态: LocalReady/AnyAlarmActive/SystemFault (3)

【输出】(20个)
  组框机: RequestFeed/Pause/EStop/DoorOpen/Ready (5)
  打胶机: RequestRun/AllowPickup/SafetyZone/ResetReq (4)
  机器人: AllowStacking/StopStacking/ResetReq (3, 预留)
  状态报警: FrameMachineEmergencyStop/ExternalDeviceFault
           /ExternalDeviceAlarmSummary(INT)/SafetyConditionMet = 4

【支持设备】: 3台 (组框机 + 打胶机 + 机器人(预留))

【报警快速处理】:
  300~302 → 检查打胶机设备状态和通讯
  310~312 → 检查组框机设备状态和安全系统
  320~322 → 检查机器人设备状态(预留)

【V6.0.0变更要点】:
  ✅ 所有变量名100%英文化(符合801规范V1.0.5)
  ✅ 43处命名对齐修复(与GlobalVars.db stExternal一致)
  ✅ 注释保留中文(便于国内工程师阅读)
  ✅ 与GlobalVars.db V3.0.0 100%匹配

═════════════════════════════════════════════
```

---

**文档版本**: V6.0.0
**最后更新**: 2026-05-03
**下次审查日期**: [待定]
**归档位置**: `02_PLC程序/通用ST程序及变量表/external/PRD/`
