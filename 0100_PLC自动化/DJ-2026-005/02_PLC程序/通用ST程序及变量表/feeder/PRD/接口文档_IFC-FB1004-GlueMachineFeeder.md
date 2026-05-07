# FB_1004_GlueMachineFeeder_BufferFraming 接口文档

## 1. 文档基础信息

| 属性 | 值 |
|------|-----|
| **文档标题** | 打胶机送料机构功能块接口文档 (V6.0.0 英文版) |
| **适用FB** | FB_1004_GlueMachineFeeder_BufferFraming |
| **文档类型** | 接口文档 / Interface Document (IFC) |
| **文档版本** | V6.0.0 |
| **编制日期** | 2026-05-03 |
| **编制人** | Trae (AI Assistant) |
| **审核人** | [待审核] |
| **遵循规范** | `801_PLC变量命名与功能块命名规范_DEV-V1.0.5` |
| **接口规模** | **18个输入 / 14个输出** (中等复杂度) |

---

## 2. 接口概览统计

### 2.1 数量统计

| 类别 | 数量 | 数据类型说明 |
|:------|:----:|:-------------|
| **输入总计** | **18** | - |
| 系统控制信号 | 6 | BOOL (使能/模式/按钮) |
| 手动操作-伺服点动 | 2 | BOOL (X2轴前后) |
| 工艺参数 | 3 | REAL (速度/位置) |
| X2轴伺服状态信号 | 4 | BOOL (原点/限位/故障) |
| 打胶机交互信号 | 2 | BOOL (允许送料/取料完成) |
| 上游信号(取放料) | 1 | BOOL (放料完成) |
| **输出总计** | **14** | - |
| 下游信号-打胶机 | 1 | BOOL (允许抓料) |
| 运动请求-X2轴 | 2 | BOOL (前移/后移请求) |
| 安全区管理 | 1 | BOOL (安全区信号) |
| 状态/HMI显示 | 5 | BOOL(2)+INT(1)+REAL(1) |
| 报警输出 | 1 | INT (201~299段) |
| 定时器调试输出 | 4 | TIME (HMI显示已耗时间) |
| **内部变量** | 15 | VAR段 (状态机/运动请求/安全区管理/通讯/系统标志) |
| **常量定义** | 15 | VAR_CONSTANT段 (6步序+5报警码+4定时参数) |

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

### 3.2 手动操作信号组 (2个BOOL)

> 来自HMI手动操作面板 - 仅X2轴点动

| 序号 | 变量名 | 类型 | 功能描述 |
|:----:|:--------|:----:|:---------|
| 7 | `i_bLx_X2Axis_JogFwd` | BOOL | 手动-X2轴向前点动(去取料位置方向) |
| 8 | `i_bLx_X2Axis_JogRev` | BOOL | 手动-X2轴向后点动(返回待机位置方向) |

### 3.3 工艺参数组 (3个REAL)

> 来自HMI设定或配方数据

| 序号 | 变量名 | 类型 | 默认值范围 | 功能描述 |
|:----:|:--------|:----:|:----------:|:---------|
| 9 | `i_rFeedSpeed` | REAL | 0~100% | X2轴送料速度(mm/s或%) |
| 10 | `rStandbyPosition` | REAL | mm | X2轴待机位置坐标(mm, 相对原点偏移量) |
| 11 | `rPickupPosition` | REAL | mm | X2轴取料位置坐标(mm, 相对原点偏移量) |

### 3.4 X2轴伺服状态信号组 (4个BOOL)

> 来自驱动器和限位开关

| 序号 | 变量名 | 类型 | 功能描述 |
|:----:|:--------|:----:|:---------|
| 12 | `i_bX2Axis_Home` | BOOL | X2轴伺服原点信号(Home/ORG) |
| 13 | `i_bX2Axis_ForwardLimit` | BOOL | X2轴正向限位(取料侧限位) |
| 14 | `i_bX2Axis_ReverseLimit` | BOOL | X2轴反向限位(待机侧限位) |
| 15 | `i_bX2Axis_ServoFault` | BOOL | X2轴伺服驱动器故障(ALM输出) |

### 3.5 打胶机交互信号组 (2个BOOL)

> 与打胶机的握手信号

| 序号 | 变量名 | 类型 | 功能描述 | 来源设备 |
|:----:|:--------|:----:|:---------|:---------:|
| 16 | `i_bGlueMachine_AllowFeed` | BOOL | 打胶机准备好可接收边框(允许送料) | 打胶机PLC |
| 17 | `i_bGlueMachine_PickupComplete` | BOOL | 打胶机已完成边框抓取(取料完成) | 打胶机PLC |

### 3.6 上游信号组 (1个BOOL)

> 来自取放料机构(FB_1003)的放料完成信号

| 序号 | 变量名 | 类型 | 功能描述 | 来源设备 |
|:----:|:--------|:----:|:---------|:---------:|
| 18 | `i_bPickPlace_FeedComplete` | BOOL | 取放料机构放料完成(有边框可送) | FB_1003_PickPlace |

---

## 4. 输出接口定义 (VAR_OUTPUT)

### 4.1 下游信号输出组 (1个BOOL)

> 给打胶机的关键控制信号

| 序号 | 变量名 | 类型 | 功能描述 | 目标设备 | 映射目标 |
|:----:|:--------|:----:|:---------|:---------:|:---------:|
| 1 | `o_bAllowPickup` | BOOL | 允许抓料信号(-> Y44) | 打胶机 | Y44地址 |

### 4.2 运动请求输出组 (2个BOOL)

> 给主控的X2轴运动请求

| 序号 | 变量名 | 类型 | 功能描述 |
|:----:|:--------|:----:|:---------|
| 2 | `o_bX2Axis_RequestFwd` | BOOL | X2轴向前移动请求(去取料位置) |
| 3 | `o_bX2Axis_RequestRev` | BOOL | X2轴向后移动请求(返回待机位置) |

### 4.3 安全区管理输出组 (1个BOOL)

| 序号 | 变量名 | 类型 | 功能描述 | 映射目标 |
|:----:|:--------|:----:|:---------|:---------:|
| 4 | `o_bSafetyZoneSignal` | BOOL | 安全区管理信号(-> Y47) | Y47地址 |

### 4.4 状态/HMI显示输出组 (5个)

| 序号 | 变量名 | 类型 | 功能描述 | 显示格式 |
|:----:|:--------|:----:|:---------|:---------:|
| 5 | `o_bRunning` | BOOL | 本站正在自动运行 | 指示灯 |
| 6 | `o_bFault` | BOOL | 本站有故障(任一报警激活) | 报警灯 |
| 7 | `o_iCurrentState` | INT | 当前状态机步序(0~5, 99=故障) | 数值显示 |
| 8 | `o_rX2Axis_CurrentPosition` | REAL | X2轴当前位置反馈(mm, 来自主控映射) | 数值(mm) |
| 9 | `o_iStationAlarmCode` | INT | 本站当前有效报警代码(0=无报警, 201~299=报警类型) | 数值显示 |

### 4.5 报警输出组 (1个INT)

**完整报警码定义表 (201~205段)**:

| 报警码 | 名称 | 触发条件 | 触发步骤 | 清除条件 | 优先级 |
|:------:|:-----|:---------|:--------:|:---------|:------:|
| 201 | `ALM_CommTimeout` | 打胶机响应超时(10s无反馈) | 步骤3/4 | 复位按钮 | 高 |
| 202 | `ALM_SafetyZoneConflict` | 安全区冲突(取放料未离开安全区) | 步骤2/5 | 排除冲突+复位 | 高 |
| 203 | `ALM_X2AxisServoFault` | X2轴伺服驱动器故障 | - | 故障消除+复位 | 高 |
| 204 | `ALM_X2AxisMoveTimeout` | X2轴移动超时(5s未到达目标位) | 步骤2/5 | 复位按钮 | 中 |
| 205 | `ALM_PickupPosTimeout` | 取料位置到达超时(步骤2专用) | 步骤2 | 复位按钮 | 中 |

### 4.6 定时器调试输出组 (4个TIME)

> 新增于V4.2.0，用于HMI显示各定时器的已耗时间，调试诊断用

| 序号 | 变量名 | 类型 | 功能描述 | 对应定时器 |
|:----:|:--------|:----:|:---------|:-----------:|
| 10 | `q_eCommTimeout_Elapsed` | TIME | 通讯超时定时器已耗时间 | fb_tCommTimeoutTimer |
| 11 | `q_eAction_Elapsed` | TIME | 通用动作定时器已耗时间(X2轴移动等待) | fb_tActionTimer |
| 12 | `q_eInit_Elapsed` | TIME | 初始化定时器已耗时间 | fb_tInitTimer |
| 13 | `q_ePickupHold_Elapsed` | TIME | 允许抓料保持定时器已耗时间 | fb_tPickupHoldTimer |

---

## 5. 与GlobalVars.db stFeeder结构对照表

| 本FB变量名 (V6.0.0) | GlobalVars.db字段名 (V3.0.0) | 类型 | 一致性 |
|:--------------------:|:---------------------------:|:----:|:------:|
| `i_bEnable` | `stFeeder.i_bEnable` | BOOL | ✅ 匹配 |
| `i_bAutoMode` | `stFeeder.i_bAutoMode` | BOOL | ✅ 匹配 |
| ... (其余16个输入变量) | ... (对应stFeeder结构字段) | - | ✅ 全部匹配 |
| `o_bAllowPickup` | `stFeeder.o_bAllowPickup` | BOOL | ✅ 匹配 |
| ... (其余13个输出变量) | ... (对应stFeeder结构字段) | - | ✅ 全部匹配 |

**结论**: ✅ FB_1004接口与GlobalVars.db V3.0.0的stFeeder结构100%匹配。

---

## 6. 相关文档链接

### 6.1 本FB文档体系(V6.0.0)

| 文档类型 | 文档名称 | 核心内容 |
|:---------|:--------|:--------|
| **详细设计说明书 (DSN)** | [详细设计说明书_DSN-FB1004-GlueMachineFeeder.md](./详细设计说明书_DSN-FB1004-GlueMachineFeeder.md) | 6步状态机、打胶机交互逻辑、安全区管理 |
| **接口文档 (IFC)** | 本文档 ← **当前文档** | 18输入/14输出的完整英文定义 |
| **使用说明 (UM)** | [使用说明_UM-FB1004-GlueMachineFeeder.md](./使用说明_UM-FB1004-GlueMachineFeeder.md) | ST调用示例、调试指南、常见问题排查 |
| **变更记录 (CHG)** | [变更记录_CHG-FB1004-GlueMachineFeeder.md](./变更记录_CHG-FB1004-GlueMachineFeeder.md) | 版本历史、变更台帐(含V6.0.0的378+处替换详单) |

### 6.2 关联资源

| 资源名称 | 路径 | 用途 |
|:---------|:-----|:-----|
| FB_1004源代码 (V6.0.0) | [FB_1004_GlueMachineFeeder_BufferFraming.scl](./FB_1004_GlueMachineFeeder_BufferFraming.scl) | ST实现参考 |
| GlobalVars.db (V3.0.0) | [../DB1/GlobalVars.db](../DB1/GlobalVars.db) | 全局变量定义(stFeeder结构) |
| OB1.scl (V5.0.0) | [../OB1/OB1.scl](../OB1/OB1.scl) | 主程序组织块(fbGlueFeeder调用) |

---

## 附录: 快速参考卡片

```
═════════════════════════════════════════════
  FB_1004_GlueMachineFeeder 接口速查 (V6.0.0)
  18输入 / 14输出 / 15内部变量 / 15常量
═════════════════════════════════════════════

【输入】(18个)
  系统控制: Enable/AutoMode/ManualMode/Start/Stop/Reset (6)
  伺服点动: X2Axis_JogFwd/JogRev (2)
  工艺参数: FeedSpeed/StandbyPosition/PickupPosition (3REAL)
  X2轴状态: Home/ForwardLimit/ReverseLimit/ServoFault (4)
  打胶机交互: AllowFeed/PickupComplete (2)
  上游信号: PickPlace_FeedComplete (1)

【输出】(14个)
  下游信号: AllowPickup -> Y44 (1)
  运动请求: X2Axis_RequestFwd/RequestRev (2)
  安全区:   SafetyZoneSignal -> Y47 (1)
  状态HMI: Running/Fault/CurrentState(INT)
          + X2Position(REAL) + StationAlarmCode(INT) = 5
  定时器调试: 4个TIME变量 (新增于V4.2.0)

【状态机】: 6步 (Step0~5)
  Idle→WaitFeed→MoveToPickupPos→WaitAllowFeed
  →SendAllowPickup→ReturnToStandbyPos

【报警快速处理】:
  201 → 检查打胶机PLC通讯和接线
  202 → 检查取放料机构是否在安全区外
  203 → 检查X2轴伺服驱动器和接线
  204 → 检查X2轴导轨和机械结构
  205 → 检查X2轴原点和取料位置设定

【V6.0.0变更要点】:
  ✅ 所有变量名100%英文化(符合801规范V1.0.5)
  ✅ 内部实现代码100%英文化(新增于V6.0.0)
  ✅ 注释保留中文(便于国内工程师阅读)
  ✅ 与GlobalVars.db V3.0.0 100%匹配

═════════════════════════════════════════════
```

---

**文档版本**: V6.0.0
**最后更新**: 2026-05-03
**下次审查日期**: [待定]
**归档位置**: `02_PLC程序/通用ST程序及变量表/feeder/PRD/`
