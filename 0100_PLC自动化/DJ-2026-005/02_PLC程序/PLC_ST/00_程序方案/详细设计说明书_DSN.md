---
spec_id: DSN-DJ-2026-005-PLC_ST
title: "DJ-2026-005 边框缓存机 PLC 程序详细设计说明书"
version: "V7.1.1"
domain: plc
lifecycle: active
tags: ["详细设计", "PLC程序"]
---

# 详细设计说明书 DJ-2026-005 边框缓存机 PLC 程序

## 1. 文档基础信息

**文档标题**：DJ-2026-005 边框缓存机 PLC 程序详细设计说明书
**文档版本**：V7.1.1
**编制日期**：2026-06-23
**编制人**：Trae
**审核人**：[待审核]
**遵循规范**：LSP-905, PLC-023, LSP-904, LSP-903

## 2. 版本变更记录

| 版本号 | 变更内容 | 变更人 | 变更日期 |
|--------|----------|--------|----------|
| V7.1.1 | 填写实际内容 | Trae | 2026-06-23 | 从各模块PRD汇总详细设计，对齐V7.1.1代码版本 |
| V1.0.0 | 初始创建 | auto-pm | 2026-06-19 | 项目初始化自动生成空模板 |

## 3. 架构设计

### 3.1 系统架构

采用"主控 + 功能块"扁平化组件架构，OB1 作为调度中心，不含业务逻辑。所有 I/O 通过 GlobalVars 数据块映射。

详见各模块架构文档：
- 输送机子系统架构：`conveyor/PRD/Conveyor子系统架构总览_ARC-Conveyor.md`
- OB1 接口与架构：`OB1/PRD/接口文档_IFC-OB1.md`
- GlobalVars 接口：`DB1/PRD/接口文档_IFC-GlobalVars.md`

### 3.2 模块划分

| 模块 | 源文件 | 类型 | 实例数 | 接口(in+out) | 核心职责 |
|------|--------|------|--------|-------------|----------|
| OB1 | `OB1/OB1.scl` | PROGRAM | 1 | - | FB调度、I/O映射、汇总逻辑、工站间信号转发 |
| FB_1002 | `conveyor/FB_1002_*.scl` | FUNCTION_BLOCK | 4 | 22+11=33 | 9步状态机、报警编码、手动模式分发 |
| FB_1003 | `pickplace/FB_1003_*.scl` | FUNCTION_BLOCK | 1 | 42+14=56 | 6步状态机、伺服轴直控、双夹爪取放 |
| FB_1004 | `feeder/FB_1004_*.scl` | FUNCTION_BLOCK | 1 | 14+9=23 | 4步状态机、安全区管理、打胶机协作 |
| FB_2001 | `common/FB_2001_*.scl` | FUNCTION_BLOCK | 1 | 3+10=13 | ~50类报警汇总、MES队列、指示灯控制 |
| FB_3001 | `external/FB_ExternalDeviceInteraction.scl` | FUNCTION_BLOCK | 1 | 27+20=47 | 安全门/急停/外设交互/总线健康位（DJ005 基准实现文件；模板归一命名：FB_3001_ExternalInteraction） |
| GlobalVars | `DB1/GlobalVars.db` | DATA_BLOCK | 1 | - | I/O映射中心(~220+变量, 5个STRUCT+3轴数组) |

### 3.3 调用关系

```
OB1 (主循环)
  ├── Step 1: fbExternalDevice (DJ005实现：FB_ExternalDeviceInteraction；模板归一命名：FB_3001_ExternalInteraction)
  │   ← stExternal.i_* (27输入) → stExternal.o_* (20输出)
  │
  ├── Step 2: fbConveyor_L1~L4 (4×FB_1002, FOR i:=1 TO 4)
  │   ← stConveyor.i_* → stConveyor.o_*
  │   + 汇总: q_bRunning(OR) / q_bFault(OR) / q_iAlarmCode(MIN)
  │   ├── fbBlock    : FB_1011_CylinderControl (阻挡气缸)
  │   ├── fbSeparate : FB_1011_CylinderControl (分料气缸)
  │   └── fbMotor    : FB_1012_ConveyorMotor (输送电机)
  │
  ├── Step 3: fbPickPlace (FB_1003)
  │   ← stPickPlace.i_* → stPickPlace.o_*
  │   + VAR_IN_OUT: io_stZAxis => astServoAxis[1]
  │   + VAR_IN_OUT: io_stX1Axis => astServoAxis[2]
  │   + 后处理: o_*_Release := NOT o_*_Action
  │
  ├── Step 4: 工站间信号转发
  │   Feeder.i_PickPlace_FeedComplete := PickPlace.o_PlaceComplete_ToFeeder
  │
  └── Step 5: fbAlarm (FB_2001)
      ← stGlobal.i_* (3个INT报警码) → stGlobal.o_* (10个输出)
```

## 4. 状态机设计

### 4.1 输送机状态机（FB_1002, 9步 Step_S）

| 步序 | 状态名称 | 动作描述 | 转移条件 |
|------|----------|----------|----------|
| 0 | STEP_INIT | 输送反转复位到初始位 | 限位或超时 → Step 1 |
| 1 | STEP_WAIT_MATERIAL | 等待分料前感应器 | 分料前感应器=ON → Step 2 |
| 2 | STEP_BLOCK_DOWN | 阻挡气缸下降 | 阻挡气缸下位=ON → Step 10 |
| 10 | STEP_CONVEYOR_FWD | 输送带正转 | (定时/到位) → Step 20 |
| 20 | STEP_POSITION_CHECK | 双传感器检测+阻挡上升 | 到位1 AND 到位2=ON; 阻挡上位=ON → Step 30 |
| 30 | STEP_SEPARATE_PUSH | 分料气缸推出 | 分料气缸下位=ON → Step 50 |
| 50 | STEP_CONVEYOR_SLOW | 慢速精确送出 | (定时) → Step 60 |
| 60 | STEP_REQUEST_PICKUP | 等待取放料取走 | 取放料取走确认 → Step 70 |
| 70 | STEP_SEPARATE_RETURN | 分料气缸复位 | 分料气缸上位=ON → Step 0 |

### 4.2 取放料状态机（FB_1003, 6步 S20~S25）

| 步序 | 状态名称 | 动作描述 | 转移条件 |
|------|----------|----------|----------|
| S20 | 待机等待 | Z轴待机位确认 | D116=K5(自动运行中) → S21 |
| S21 | 上升到取料高度 | Z轴移动到取片教点(D514) | Z轴到位 → S22 |
| S22 | 夹紧与检测 | 4组夹爪同时夹紧+4光电检测 | 4夹紧确认+4光电ON+确认时间 → S23 |
| S23 | 移动到放料位置 | X1轴移动到放料点(L1/L3→D520, L2/L4→D540) | X1轴到位 → S24 |
| S24 | 下降到放料高度 | Z轴移动到放片教点(D524) | Z轴到位 → S25 |
| S25 | 松开与通知 | 4组夹爪松开+发送放料完成信号 | 4松开确认 → S20 |

### 4.3 送料状态机（FB_1004, 4步 D760）

| 步序 | 状态名称 | 动作描述 | 转移条件 |
|------|----------|----------|----------|
| 0 | 空闲待机 | 等待取放料放料完成 | 接收放料完成 → 1 |
| 1 | 移动到取料位 | X2轴移动到取料点(D620) | X2轴到位 → 2 |
| 2 | 移动到放料位 | X2轴移动到放料点(D630), 输出Y47; 等待X76→输出Y44; 等待X102 | 收到X102 → 3 |
| 3 | 返回待机位 | X2轴返回待机位(D610), 输出Y47(安全区开放) | X2轴到位 → 0 |

## 5. 定时器设计

| 定时器用途 | FB实例 | PT参数类型 | 说明 |
|-----------|--------|-----------|------|
| 分料超时 | FB_TON (FB_1002内) | DINT(ms) | 默认5000ms, 可通过HMI调整 |
| 夹紧确认时间 | FB_TON (FB_1003内) | DINT(ms) | HMI设定 |
| 升降动作时间 | FB_TON (FB_1003内) | DINT(ms) | HMI设定 |
| 气缸超时 | FB_TON (FB_1011内) | DINT(ms) | SysLib共享库 |
| 新报警脉冲 | FB_TON (FB_2001内) | DINT(ms) | 指示灯蜂鸣器控制 |

> 所有定时器使用 SysLib 的 FB_TON，PT/ET 为 DINT 类型（毫秒值），禁止使用 TIME 类型（LSP-903）。

## 6. 报警设计

### 6.1 报警编码策略

| 工站 | 报警码段 | 编码规则 | 示例 |
|------|----------|----------|------|
| 输送机 | 10x~14x | 层号×100+故障类型 | 1010=Layer1阻挡超时, 1110=Layer2分料超时 |
| 取放料 | 20x~29x | 2xx系列 | 2001=Z轴伺服报警, 2010=夹紧超时 |
| 送料 | 30x~39x | 3xx系列 | 3001=X2轴伺服报警, 3010=安全区异常 |
| 安全系统 | 90x~99x | 9xx系列 | 9001=急停触发, 9010=安全门1打开 |

### 6.2 报警处理逻辑

- **汇总**：FB_2001 接收各工站报警码(INT)，计算全局报警字(WORD)
- **优先级**：q_iAlarmCode := MIN(各站非零报警码)，值越小优先级越高
- **MES队列**：10条去重报警记录，存入 D406-D425
- **指示灯**：绿灯=自动无故障, 红灯=任何故障, 黄灯=暂停/等待/回原点, 蜂鸣器=新报警脉冲

### 6.3 详细报警码

详见各模块变更记录和接口文档中的报警码定义。

## 7. 变量设计

### 7.1 命名规范

- 遵循 LSP-905 §3 小驼峰风格
- 前缀体系：`i_`(输入), `o_`/`q_`(输出，`q_` 为兼容旧项目), `io_`(输入输出), `s_`(FB内部静态变量), `fb_`(FB实例), `arr`(数组类型标识)

### 7.2 GlobalVars 数据块结构

| 结构体 | 变量数 | 说明 |
|--------|--------|------|
| stExternal | ~22 | 安全信号+组框机+打胶机+机器人交互 |
| stConveyor | ~33 | 4层输送机(含ARRAY[1..4]) |
| stPickPlace | ~53 | 取放料+伺服轴(VAR_IN_OUT) |
| stFeeder | ~14 | 送料机构 |
| stGlobal | ~10 | 全局报警+指示灯 |
| astServoAxis[1..3] | 74×3=222 | ST_ServoAxis V3.0 伺服轴数组 |

详见 `DB1/PRD/接口文档_IFC-GlobalVars.md`。

## 8. 详细设计文档索引

各模块的详细设计文档分布在对应模块的 PRD 目录下：

| 模块 | 文档路径 |
|------|----------|
| OB1 | `OB1/PRD/详细设计说明书_DSN-OB1.md` |
| 输送机 | `conveyor/PRD/详细设计说明书_DSN-FB1002-SingleLayerConveyor.md` |
| 取放料 | `pickplace/PRD/详细设计说明书_DSN-FB1003-PickPlace.md` |
| 送料 | `feeder/PRD/详细设计说明书_DSN-FB1004-GlueMachineFeeder.md` |
| 公共报警 | `common/PRD/详细设计说明书_DSN-FB2001-CommonAlarm.md` |
| 外部设备 | `external/PRD/详细设计说明书_DSN-FB-ExternalDeviceInteraction.md`（DJ005 基准实现；模板归一命名：FB_3001_ExternalInteraction） |
| GlobalVars | `DB1/PRD/接口文档_IFC-GlobalVars.md` |
