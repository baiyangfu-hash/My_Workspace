# OB1 主程序组织块变更记录

## 1. 文档基础信息

| 属性 | 值 |
|------|-----|
| **文档标题** | OB1主程序组织块变更记录 |
| **适用组件** | OB1 (主程序组织块) |
| **文档类型** | 变更记录 / Change Log (CHG) |
| **文档版本** | V7.0.0 |
| **编制日期** | 2026-05-18 |
| **编制人** | Trae |
| **审核人** | [待审核] |

---

## 2. 版本变更记录总表

| 版本号 | 发布日期 | 变更类型 | 业务性质 | 影响范围 | 变更内容摘要 |
|:------:|:--------:|:--------:|:--------:|:--------:|-------------|
| **V7.0.0** | 2026-05-18 | CHG-PLC | REQ | MODULE | Conveyor重构: 取消FB_1001, 展开调用4×FB_1002(L1~L4), 新增汇总逻辑(OR/MIN), 下游引用对齐stConveyor新变量名 |
| **V5.0.0** | 2026-05-04 | CHG-PLC | REQ | INTERFACE | 接口变量名100%英文化，与GlobalVars.db V3.0.0和各FB V5.0.0同步；修复变量路径错误(Conveyor.o_iAlarmCode) |
| **V4.0.0** | 2026-04-24 | CHG-PLC | REQ | MODULE | 初版创建：实现三工站流水线调度、安全系统判断、IO映射、HMI数据交互 |

---

## 3. V7.0.0 版本详细变更说明

### 3.1 变更基本信息

| 属性 | 值 |
|------|-----|
| **变更编号** | CHG-PLC-2026-V700-OB1 |
| **技术领域** | PLC (程序代码) |
| **业务性质** | REQ (必需改进) |
| **影响范围** | MODULE (模块级) |

### 3.2 变更背景与原因

Conveyor子系统从V6→V7重构: FB_1001容器取消, FB_1002瘦身为纯编排器。OB1需要从调用1个大容器改为展开调用4个FB_1002实例，并新增汇总逻辑。

### 3.3 变更内容

#### 3.3.1 输送机调用重写
- **删除**: `GlobalVars.fbConveyor4Layer(...)` 调用 (FB_1001容器)
- **新增**: `GlobalVars.fbConveyor_L1/L2/L3/L4(...)` 展开调用 (4×FB_1002)
- 每层调用传递标量信号，从 stConveyor 数组逐层索引
- 共享信号 (AutoMode/ManualMode/Start/Stop/SafetyDoorOk/VfdFault) 4层复用

#### 3.3.2 汇总逻辑新增
- `q_bRunning := L1.q_aLayerRunning OR L2 OR L3 OR L4`
- `q_bFault := L1.q_aLayerFault OR L2 OR L3 OR L4`  
- `q_iAlarmCode := MIN(4层非零报警码, 值越小优先级越高)`

#### 3.3.3 下游引用更新
- `i_iConveyorAlarm`: `stConveyor.o_iAlarmCode` → `stConveyor.q_iAlarmCode`
- `i_bLayerFeedDone`: `stConveyor.o_bFeedComplete` → `stConveyor.q_aLayerFeedDone`

### 3.4 兼容性与影响分析
- ✅ 与 GlobalVars.db V7.0.0 100%同步
- ✅ 与 FB_1002 V7.0.0 接口100%对齐
- ✅ FB_2001 报警输入路径不变(仍传汇总值)
- ⚠️ HMI变量名从 o_LxCurrentStep 变为 q_aLayerStep，HMI需同步更新

---

## 4. V5.0.0 版本详细变更说明

### 4.1 变更基本信息

| 属性 | 值 |
|------|-----|
| **变更编号** | CHG-PLC-2026-V500-OB1 |
| **技术领域** | PLC (程序代码) |
| **业务性质** | REQ (必需改进) |
| **影响范围** | INTERFACE (接口级) |

### 4.2 变更背景与原因

在V5.0.0全面重写过程中，发现OB1存在以下问题：
1. 变量名与GlobalVars.db V3.0.0不一致
2. 调用FB_2001时变量路径错误(使用了不存在的`o_iStationAlarmCode`)
3. 需要与所有FB的V5.0.0版本同步

### 4.3 变更内容

#### 4.3.1 变量名英文化

所有调用参数从中文更新为英文，与GlobalVars.db V3.0.0保持一致。

#### 4.3.2 变量路径修复

将 `GlobalVars.stConveyor.o_iStationAlarmCode` 修正为 `GlobalVars.stConveyor.o_iAlarmCode`

### 4.4 兼容性与影响分析
- ✅ 已与GlobalVars.db V3.0.0同步
- ✅ 已与所有FB V5.0.0版本同步
- ✅ 无编译错误

---

**文档版本**: V7.0.0  
**最后更新**: 2026-05-18