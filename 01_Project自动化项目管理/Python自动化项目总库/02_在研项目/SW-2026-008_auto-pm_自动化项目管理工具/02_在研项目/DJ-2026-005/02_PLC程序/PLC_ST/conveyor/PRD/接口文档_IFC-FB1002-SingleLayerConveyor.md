# 接口文档 FB_1002_SingleLayerConveyor

## 0. 文档基础信息

| 属性 | 值 |
|------|-----|
| **文档标题** | FB_1002 单层输送机编排器接口定义 |
| **文档版本** | V7.0.0 |
| **关联源码** | conveyor/FB_1002_SingleLayerConveyor_BufferFraming.scl |
| **编制日期** | 2026-05-18 |
| **编制人** | Trae |
| **审核人** | 人工 |
| **遵循规范** | LSP-905_SCL编程规范 |
| **重构背景** | 高内聚低耦合重写：取消 FB_1001 容器，FB_1002 瘦身为纯编排器，气缸/电机逻辑下沉到 FB_1011/FB_1012 |

## 1. 功能概述

**单层输送机编排器**，负责单层输送的工艺调度。本身不包含执行器控制细节，而是通过委托子功能块完成：

- **电梯气缸** → 委托 `FB_1011_CylinderControl` (实例 `fbBlock`)
- **分料气缸** → 委托 `FB_1011_CylinderControl` (实例 `fbSeparate`)
- **输送电机** → 委托 `FB_1012_ConveyorMotor` (实例 `fbMotor`)

编排器唯一职责：决定 **何时** 做什么（9步状态机 + 手动模式），子FB负责 **如何** 做。

### 1.1 职责边界

| 做什么 | 不做什么 |
|--------|----------|
| 9步 Step_S 状态机调度 | 不控制电磁阀输出时序（委托 FB_1011） |
| 手动/自动模式分发 | 不处理安全门互锁（委托 FB_1012） |
| 报警码编码（含层号） | 不管理定时器超时（委托 FB_1011） |
| 执行器输出收集 | 不检测气缸到位（委托 FB_1011） |
| 故障汇总 | 不管 VFD 故障切断（委托 FB_1012） |

### 1.2 调用关系

```
OB1 (FOR i:=1 TO 4)
  └─ fbConveyor[i] : FB_1002_SingleLayerConveyor
       ├─ fbBlock    : FB_1011_CylinderControl   (阻挡气缸)
       ├─ fbSeparate : FB_1011_CylinderControl   (分料气缸)
       └─ fbMotor    : FB_1012_ConveyorMotor      (输送电机)
```

> **FB_1001 已取消**。OB1 直接用 FOR 循环实例化4个 FB_1002，汇总逻辑（OR/优先级/MIN）在 OB1 完成。

## 2. 状态机步序常量

| 常量名 | 值 | 步骤名 | 说明 |
|--------|-----|--------|------|
| STEP_INIT | 0 | 初始化反转 | 输送反转复位到初始位 |
| STEP_WAIT_MATERIAL | 1 | 等待来料 | 等待分料前感应器ON |
| STEP_BLOCK_DOWN | 2 | 阻挡下降 | 阻挡气缸下降 |
| STEP_CONVEYOR_FWD | 10 | 输送正转 | 输送带正向运转 |
| STEP_POSITION_CHECK_BLOCK_UP | 20 | 到位检测+阻挡上升 | 双传感器检测+阻挡释放 |
| STEP_SEPARATE_PUSH | 30 | 分料推出 | 分料气缸推出分离边框 |
| STEP_CONVEYOR_SLOW | 50 | 慢速送出 | 慢速精确送出到取料位 |
| STEP_REQUEST_PICKUP | 60 | 请求取料 | 等待取放料取走 |
| STEP_SEPARATE_RETURN | 70 | 分料复位 | 分料气缸复位 |

## 3. 接口定义

### 3.1 VAR_INPUT

#### 3.1.1 模式与控制 (4)

| 名称 | 类型 | 默认值 | 说明 | 来源 |
|------|------|--------|------|------|
| i_bAutoMode | BOOL | FALSE | 自动运行模式 | OB1→HMI |
| i_bManualMode | BOOL | FALSE | 手动调试模式 | OB1→HMI |
| i_bStart | BOOL | FALSE | 自动循环启动 (上升沿) | OB1→HMI (M2) |
| i_bStop | BOOL | FALSE | 停止 (电平有效) | OB1→HMI (M3) |

#### 3.1.2 配置参数 (2)

| 名称 | 类型 | 默认值 | 有效值域 | 说明 | 来源 |
|------|------|--------|----------|------|------|
| i_iLayerIndex | INT | 0 | 1~4 | 层编号 (报警码编码用) | OB1 |
| i_iSeparateTimeoutMs | INT | 5000 | 0~60000 | 分料超时时间(ms) | OB1→HMI (D101) |

#### 3.1.3 传感器输入 (7)

| 名称 | 类型 | 默认值 | 说明 | 来源 |
|------|------|--------|------|------|
| i_bPreSeparateSensor | BOOL | FALSE | 分料前接近开关 | OB1→IO |
| i_bPositionSensor1 | BOOL | FALSE | 到位传感器1 | OB1→IO |
| i_bPositionSensor2 | BOOL | FALSE | 到位传感器2 (冗余) | OB1→IO |
| i_bBlockCylinderUp | BOOL | FALSE | 阻挡气缸上位 | OB1→IO |
| i_bBlockCylinderDown | BOOL | FALSE | 阻挡气缸下位 | OB1→IO |
| i_bSeparateCylinderUp | BOOL | FALSE | 分料气缸上位 | OB1→IO |
| i_bSeparateCylinderDown | BOOL | FALSE | 分料气缸下位 | OB1→IO |

#### 3.1.4 安全与外部联锁 (3)

| 名称 | 类型 | 默认值 | 说明 | 来源 |
|------|------|--------|------|------|
| i_bSafetyDoorOk | BOOL | TRUE | 安全门状态 (取反M8) | OB1→External FB |
| i_bVfdFault | BOOL | FALSE | 变频器故障 | OB1→IO |
| i_bPickupConfirmed | BOOL | FALSE | 取料机构已取走物料 | OB1←FB_1003 |

#### 3.1.5 手动操作命令 (6)

| 名称 | 类型 | 默认值 | 说明 | 来源 |
|------|------|--------|------|------|
| i_bManBlockExtend | BOOL | FALSE | 手动:阻挡下降 | OB1←HMI |
| i_bManBlockRetract | BOOL | FALSE | 手动:阻挡上升 | OB1←HMI |
| i_bManSeparatePush | BOOL | FALSE | 手动:分料推出 (TRUE=推出,FALSE=复位) | OB1←HMI |
| i_bManConveyorFwd | BOOL | FALSE | 手动:输送正转 | OB1←HMI |
| i_bManConveyorRev | BOOL | FALSE | 手动:输送反转 | OB1←HMI |
| i_bManConveyorSlow | BOOL | FALSE | 手动:输送慢速 | OB1←HMI |

> **接口变化说明**: 去掉了旧版中未使用的 `i_rConveyorSpeed`、`i_iBlockWaitTime`、`i_bPickPlaceSafeZone`。手动按钮从 Lx_ 前缀改为 Man 前缀，语义更清晰。

### 3.2 VAR_OUTPUT

#### 3.2.1 执行器输出 (5)

| 名称 | 类型 | 默认值 | 说明 | 去向 |
|------|------|--------|------|------|
| q_bBlockSolenoid | BOOL | FALSE | 阻挡电磁阀 (TRUE=下降) | OB1→IO (Y30~Y37) |
| q_bSeparateSolenoid | BOOL | FALSE | 分料电磁阀 (TRUE=推出) | OB1→IO (Y30~Y37) |
| q_bConveyorFwd | BOOL | FALSE | 输送带正转 | OB1→IO (Y10~Y23) |
| q_bConveyorRev | BOOL | FALSE | 输送带反转 | OB1→IO (Y10~Y23) |
| q_bConveyorSlow | BOOL | FALSE | 输送带慢速 | OB1→IO (Y10~Y23) |

#### 3.2.2 状态与报警 (6)

| 名称 | 类型 | 默认值 | 说明 | 去向 |
|------|------|--------|------|------|
| q_iCurrentState | INT | 0 | 当前步序 (0~70) | OB1→HMI (D122) |
| q_iAlarmCode | INT | 0 | 本层报警码 (0=正常) | OB1→FB_2001 |
| q_bRunning | BOOL | FALSE | 自动运行中 | OB1→HMI |
| q_bFault | BOOL | FALSE | 本层有故障 | OB1 汇总 |
| q_bLayerFeedDone | BOOL | FALSE | 本层放料完成 (脉冲) | OB1→FB_1003 |
| q_bAnySensorFault | BOOL | FALSE | 任一气缸传感器故障 (汇总) | OB1→FB_2001 |

### 3.3 VAR (内部变量)

| 名称 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| fbBlock | FB_1011_CylinderControl | — | 阻挡气缸实例 |
| fbSeparate | FB_1011_CylinderControl | — | 分料气缸实例 |
| fbMotor | FB_1012_ConveyorMotor | — | 输送电机实例 |
| bStepEntry | BOOL | TRUE | 新步入口标志 |
| bRunning | BOOL | FALSE | 运行标志 (内部) |
| bStartTriggered | BOOL | FALSE | 启动上升沿锁存 |
| iCurrentState | INT | 0 | 当前步序 (内部) |
| iAlarmCode | INT | 0 | 报警码 (内部) |

## 4. 报警码体系（自包含编码）

FB_1002 根据本层 `i_iLayerIndex` 对所有子FB的报警信号进行编码，输出带层号的完整报警码。不需要外部参与计算。

| 报警码 | 含义 | 来源 |
|:------:|------|------|
| 4x | (保留: 复位超时) | — |
| 10x | 本层 VFD 故障 | fbMotor.q_bVfdAlarm |
| 11x | 本层阻挡超时 | fbBlock.q_bTimeout |
| 12x | 本层阻挡传感器故障 | fbBlock.q_bSensorFault |
| 13x | 本层分料超时 | fbSeparate.q_bTimeout |
| 14x | 本层分料传感器故障 | fbSeparate.q_bSensorFault |

其中 `x` = `i_iLayerIndex` (1~4)。

示例:
| 层 | VFD故障 | 阻挡超时 | 分料超时 |
|:--:|:-------:|:-------:|:-------:|
| L1 | 101 | 111 | 131 |
| L2 | 102 | 112 | 132 |
| L3 | 103 | 113 | 133 |
| L4 | 104 | 114 | 134 |

> **变化说明**: 旧版 100~103 / 130~163 编码被统一为 10x/11x/12x/13x/14x 规则化编码。每个子FB仅输出 BOOL 报警信号，由编排器统一编码。

## 5. 接口精简量化对比

| 维度 | 旧版 V6.0.0 | 新版 V7.0.0 | 变化 |
|------|:---------:|:---------:|:----:|
| FB_1002 VAR_INPUT | 25 | 22 | -3 |
| FB_1002 VAR_OUTPUT | 14 | 11 | -3 |
| FB_1002 总接口 | **39** | **33** | **-15%** |
| FB_1001 | 87 | **0 (取消)** | **-100%** |
| 系统总外部接口 | **126** | **33** | **-74%** |
| 子FB (内聚) | 0 | FB_1011×2 + FB_1012 | 3个独立可复用单元 |

## 6. 关联文档

| 文档 | 路径 |
|------|------|
| DSN | 详细设计说明书_DSN-FB1002-SingleLayerConveyor-V7.0.0.md |
| FB_1011 IFC | ../../../../../../01_SharedLibraries/SysLib/actuator/PRD/接口文档_IFC-FB1011-CylinderControl-V7.0.0.md |
| FB_1012 IFC | ../../../../../../01_SharedLibraries/SysLib/actuator/PRD/接口文档_IFC-FB1012-ConveyorMotor-V7.0.0.md |
| 子系统架构 | Conveyor子系统架构总览_ARC-Conveyor-V7.0.0.md |
