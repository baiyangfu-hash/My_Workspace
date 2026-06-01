---
spec_id: PRD-FB1014
title: "FB_1014 工站输送机需求定义"
version: "V6.0.0"
domain: plc
lifecycle: stable
canonical_path: "0100_PLC自动化/01_SharedLibraries/SysLib/actuator/FB_1014_StationConveyor/PRD/需求文档_PRD-FB1014-StationConveyor-V6.0.0.md"
tags: ["工站输送机", "编排器", "PLC功能块", "需求", "Breaking Change", "运行模式"]
---
# 需求文档 FB_1014_StationConveyor

## 0. 文档基础信息

| 属性 | 值 |
|------|-----|
| **文档标题** | FB_1014 工站输送机需求定义 |
| **文档版本** | V6.0.0 |
| **关联源码** | actuator/FB_1014_StationConveyor/FB_1014_StationConveyor.scl |
| **关联IFC** | 接口文档_IFC-FB1014-StationConveyor-V6.0.0.md |
| **关联DSN** | 详细设计说明书_DSN-FB1014-StationConveyor-V6.0.0.md |
| **关联PFL** | 工艺流程_PFL-FB1014-StationConveyor-V6.0.0.md |
| **编制日期** | 2026-05-31 |
| **编制人** | Trae |
| **遵循规范** | LSP-905 V1.0.2, LSP-904 V1.2.0, LSP-903 V1.0.0, LSP-906 V1.0.0 |

### V5.0.0 变更摘要 (Breaking Change)

重构动机: V4.3.0的FB_1011/FB_1012内部实例导致FB_1014职责膨胀, 违反单一职责原则. V5.0.0将FB_1014重构为纯编排器, FB_1011/FB_1012实例移至OB1, FB_1014仅输出命令和输入状态.

| 变更项 | V4.3.0 | V5.0.0 | 理由 |
|--------|:------:|:------:|------|
| 架构角色 | 编排器+执行器混合 | **纯编排器** | 单一职责, FB_1014只决定"做什么", 不直接驱动硬件 |
| FB_1011实例 | 内部实例(fbInfeedCyl/fbAlignCyl/fbDischargeCyl) | **移至OB1** | 气缸执行逻辑与输送编排解耦 |
| FB_1012实例 | 无(裸BOOL直接驱动) | **移至OB1** | 电机执行逻辑与输送编排解耦 |
| ST_Cylinder VAR_IN_OUT | 3个(io_stInfeedCyl/io_stAlignCyl/io_stDischargeCyl) | **删除** | ST_Cylinder结构体已废弃, FB_1011 V9.0.0回归扁平接口 |
| 气缸接口 | VAR_IN_OUT ST_Cylinder(读写混合) | **输入状态+输出命令(分离)** | 编排器只读状态/只写命令, 职责清晰 |
| 电磁阀输出 | q_yInfeedSolenoid/q_yAlignSolenoid/q_yDischargeSolenoid | **删除** | 电磁阀由OB1中FB_1011直接输出 |
| 拍正取反逻辑 | FB_1014内部NOT fbAlignCyl.q_bSolenoid | **删除** | FB_1011 V9.0.0 i_bExtendPolarity=TRUE在OB1中处理 |
| 马达输出 | q_yFwdCmd/q_yRevCmd/q_ySlowCmd(直接硬件) | **q_bFwdCmd/q_bRevCmd/q_bSlowCmd(命令到FB_1012)** | 电机驱动由FB_1012接管 |
| VFD故障检测 | 无 | **新增i_bVfdAlarm输入** | FB_1012 V9.0.0 q_bVfdAlarm反馈到编排器 |
| VFD故障响应 | 无 | **状态机进入FAULT** | VFD故障时输送机必须停机 |

### V6.0.0 变更摘要 (Breaking Change)

变更动机: V5.0.0仅支持A进B出单向模式, 无法适配B侧双向进出料的主流产线布局. V6.0.0引入i_iMode运行模式接口(基于PFL V6.0.0), 支持3种运行模式, 同时将拍正气缸(弹簧复位型)的默认安全态从"收回"改为"伸出", 以匹配物理弹簧复位特性. 工艺阶段S2/S2b/S3/S4均新增拍正/阻挡协作行为.

| 变更项 | V5.0.0 | V6.0.0 | 理由 |
|--------|:------:|:------:|------|
| 运行模式接口 | 无 | **新增i_iMode(INT)**: 0=A进B出/1=B进B出(默认)/2=A侧双向预留 | 适配不同产线布局, 一套代码覆盖多种场景 |
| 默认运行模式 | 隐含A进B出(无选择) | **Mode=1(B进B出)** | 适配主流B侧双向进出料产线 |
| S2进料-拍正参与 | 拍正气缸不参与进料 | **拍正气缸伸出配合阻挡防超位** | 防止物料高速进料时冲出工位 |
| S2b拍正-ALIGN行为 | 拍正确认后阻挡下降 | **B侧阻挡升起三面围住, 拍正后两侧下降不干涉** | 提高拍正精度, 三面围住确保对齐准确 |
| S3加工-气缸状态 | 无特殊处理 | **两侧阻挡下降不干涉工件** | 避免阻挡气缸干涉加工动作 |
| S4出料前-预动作 | 直接B侧出料 | **拍正先伸出就位+A侧阻挡升起屏障, 再B侧出料** | 出料前拍正预定位, A侧阻挡防工件反向偏移 |
| IDLE态拍正 | q_bAlignRetract=TRUE(收回) | **q_bAlignExtend=TRUE(伸出就绪)** | 弹簧复位气缸默认伸出=物理安全态 |
| READY态拍正 | q_bAlignRetract=TRUE(收回) | **q_bAlignExtend=TRUE(伸出就绪)** | 同上, 准备进料时拍正已就位 |
| COMPLETE态拍正 | q_bAlignRetract=TRUE(收回) | **q_bAlignExtend=TRUE(伸出就绪)** | 循环结束后拍正复位到默认伸出态 |
| FAULT态拍正 | q_bAlignRetract=TRUE(收回) | **q_bAlignExtend=TRUE(伸出)** | 故障时弹簧复位气缸失电=默认伸出=安全态 |
| Stop安全态拍正 | q_bAlignRetract=TRUE(收回) | **q_bAlignExtend=TRUE(伸出)** | 停止时弹簧复位气缸失电=默认伸出=安全态 |
| VFD故障安全态拍正 | q_bAlignRetract=TRUE(收回) | **q_bAlignExtend=TRUE(伸出)** | VFD故障时弹簧复位气缸失电=默认伸出=安全态 |
| 手动模式拍正 | q_bAlignExtend=FALSE, q_bAlignRetract=TRUE | **q_bAlignExtend=TRUE, q_bAlignRetract=FALSE** | 手动模式拍正默认伸出就绪 |
| FR-09停止行为 | 全部气缸收回(含拍正) | **拍正伸出**, 其余气缸收回 | 拍正=弹簧复位, 失电伸出是安全态 |
| FR-11故障恢复 | q_bAlignRetract=TRUE(收回) | **q_bAlignExtend=TRUE(伸出)** | 故障恢复后拍正回到默认伸出态 |
| NFR-04安全默认态 | 全部气缸收回(含拍正) | **拍正伸出(弹簧复位默认)**, 其余气缸收回 | 弹簧复位气缸失电默认伸出, 物理安全态 |
| 接口新增 | - | **i_iMode (INT)** | 运行模式选择输入 |
| PFL版本 | V4.2.0 | **V6.0.0** | 同步PFL工艺流程版本 |

---

## 1. 需求概述

### 1.1 应用场景

工站输送机是自动化产线中的核心执行单元, 用于在工站间输送物料(如玻璃基板). 典型应用场景:

- **LCD/OLED面板产线**: 玻璃基板在各加工工站(清洗/涂布/曝光/蚀刻等)之间流转
- **半导体封装产线**: 晶圆载具在检测/包装工站之间输送
- **精密加工产线**: 工件在加工/检测/上下料工位之间传递

### 1.2 核心业务问题

传统双口输送机需要两个独立端口(入料口+出料口), 占用更多空间且成本更高. **单口双向输送**方案通过同一端口实现进出料, 解决以下问题:

1. **空间受限**: 工站布局紧凑, 无法容纳双端口
2. **成本优化**: 减少传感器/气缸/皮带数量
3. **灵活部署**: 同一设备可适配不同产线布局

V6.0.0新增**运行模式(i_iMode)**接口, 支持3种产线布局:
- **Mode 0**: A进B出 — 传统单向流水线
- **Mode 1**: B进B出 — B侧双向进出料(默认, 主流场景)
- **Mode 2**: A侧双向 — 预留, A侧既是进料口也是出料口

### 1.3 物理布局说明

工站输送机采用A/B双侧布局:

- **A侧**: 阻挡气缸装在拍正气缸上, 可独立升降; 拍正气缸为底座, **弹簧复位型**, 默认伸出
- **B侧**: 出料/阻挡气缸, 独立安装
- **传感器**: 3个光电传感器(X420/X421/X422), X420始终为入料开始检测, X421/X422功能随方向和模式切换
- **拍正气缸极性**: 弹簧复位单作用气缸, OB1中FB_1011实例配置i_bExtendPolarity=TRUE, 由FB_1011内部处理电磁阀取反. **失电时弹簧复位伸出, 这是物理安全态**

### 1.4 架构变更说明

V5.0.0的核心架构变更是将FB_1014从"编排器+执行器混合"重构为"纯编排器". V6.0.0在此架构基础上新增运行模式接口, 架构不变:

```
V5.0.0/V6.0.0 架构(纯编排器):
  OB1 --> FB_1014(纯编排: 输出命令, 输入状态, 运行模式选择)
  OB1 --> FB_1011 x3(气缸执行: 接收命令, 输出电磁阀, 反馈状态)
  OB1 --> FB_1012 x1(电机执行: 接收命令, 输出VFD, 反馈状态)
  OB1负责: 实例化+信号连线+物理IO映射
```

**纯编排器职责**:
- 决定"什么时候做什么"(状态机逻辑, 含运行模式分支)
- 输出命令信号给FB_1011/FB_1012(不直接驱动硬件)
- 读取FB_1011/FB_1012的状态反馈(不直接读取传感器)
- 不包含任何FB_1011/FB_1012内部实例
- 根据i_iMode选择合适的输送方向和气缸协作策略

### 1.5 运行模式定义

| Mode | i_iMode值 | 进料方向 | 出料方向 | 适用场景 | 状态 |
|------|:--------:|---------|---------|---------|:----:|
| A进B出 | 0 | A侧 → | → B侧 | 传统单向流水线 | 支持 |
| B进B出 | **1** | **B侧 ←** | **→ B侧** | **B侧双向进出料(主流)** | **默认** |
| A侧双向 | 2 | A侧 → | ← A侧 | 预留, A侧双向进出料 | 预留 |

**默认模式**: i_iMode=1(B进B出), 适配主流B侧双向产线布局.

### 1.6 用户画像

| 用户 | 使用方式 | 关注点 |
|------|---------|--------|
| PLC程序员 | 在OB1中实例化FB_1014/FB_1011/FB_1012, 连接信号, 配置i_iMode | 接口简洁, 职责清晰, 模式可配, 易调试 |
| 产线工程师 | 配置延时参数和运行模式, 监控运行状态 | 参数可调, 模式可切换, 状态可观测, 故障可诊断 |
| 设备维护人员 | 排查故障, 恢复生产 | 报警信息明确, 恢复操作简单 |

---

## 2. 功能需求

### 2.1 控制需求

#### FR-01: 单口双向输送(含运行模式)

| 属性 | 值 |
|------|-----|
| **需求ID** | FR-01 |
| **优先级** | P0-必须 |
| **描述** | 输送机通过运行模式(i_iMode)选择进出料方向: Mode 0=A进B出(皮带反转进料正转出料), Mode 1=B进B出默认(皮带正转进料反转出料), Mode 2=A侧双向预留. 马达命令输出至FB_1012 |
| **验收标准** | 1. Mode 0: 进料q_bRevCmd=TRUE, 出料q_bFwdCmd=TRUE; 2. Mode 1: 进料q_bFwdCmd=TRUE, 出料q_bRevCmd=TRUE; 3. Mode 2: 预留, 行为与Mode 1对称(A侧); 4. 同一时刻正反转互斥; 5. 默认i_iMode=1时按B进B出运行 |
| **关联状态** | ST_INFEED, ST_DISCHARGE |

#### FR-02: 方向切换功能复用(含模式适配)

| 属性 | 值 |
|------|-----|
| **需求ID** | FR-02 |
| **优先级** | P0-必须 |
| **描述** | 传感器(X421/X422)和气缸的物理位置固定, 但逻辑功能随i_iMode和物料方向切换. 气缸功能通过不同的命令输出组合实现, Mode决定哪侧气缸承担进料/出料角色 |
| **验收标准** | 1. Mode 0(A进B出): INFEED态q_bDischargeExtend=TRUE(B侧放下作入料), DISCHARGE态q_bInfeedExtend=TRUE(A侧放下作出料); 2. Mode 1(B进B出默认): INFEED态q_bDischargeExtend=TRUE(B侧放下作入料), DISCHARGE态q_bDischargeExtend=TRUE(B侧放下作出料); 3. Mode 2(A侧双向预留): INFEED态q_bInfeedExtend=TRUE(A侧放下作入料), DISCHARGE态q_bInfeedExtend=TRUE(A侧放下作出料); 4. X421/X422检测逻辑随Mode和方向切换 |
| **关联状态** | ST_INFEED, ST_DISCHARGE |

#### FR-03: 自动模式状态机

| 属性 | 值 |
|------|-----|
| **需求ID** | FR-03 |
| **优先级** | P0-必须 |
| **描述** | 自动模式下按9态状态机运行: IDLE->READY->INFEED->ALIGN->PROCESSING->DISCHARGE->COMPLETE->IDLE, 异常进入PAUSE/FAULT. VFD故障(i_bVfdAlarm=TRUE)触发进入FAULT态. 各状态内行为受i_iMode影响(进出料方向, 气缸协作策略) |
| **验收标准** | 1. 正常循环: 0->1->2->3->4->5->6->0; 2. 暂停: 任意态->7; 3. 停止: 任意态->8; 4. VFD故障: 任意运行态->8; 5. 状态值通过q_iState输出; 6. INFEED完成后进入ALIGN而非直接进入PROCESSING; 7. Mode切换影响INFEED和DISCHARGE态的马达方向及气缸角色 |
| **关联状态** | 全部 |

#### FR-09: 安全优先级链

| 属性 | 值 |
|------|-----|
| **需求ID** | FR-09 |
| **优先级** | P0-必须 |
| **描述** | 停止(i_bStop) > VFD故障(i_bVfdAlarm) > 暂停(i_bPause) > 正常运行, 高优先级信号立即中断当前操作. 停止/VFD故障时: 马达命令清零, 阻挡/出料气缸收回, **拍正气缸伸出(弹簧复位默认安全态)** |
| **验收标准** | 1. i_bStop=TRUE: 所有驱动命令清零, q_bInfeedRetract=TRUE, q_bDischargeRetract=TRUE, q_bAlignExtend=TRUE(伸出), 进入ST_FAULT; 2. i_bVfdAlarm=TRUE: 马达命令清零, q_bAlignExtend=TRUE(伸出), 进入ST_FAULT; 3. i_bPause=TRUE: 马达命令清零, 进入ST_PAUSE, 记录暂停前状态; 4. 停止/暂停/VFD故障期间不执行状态机逻辑 |
| **关联状态** | 全部 |

#### FR-10: 暂停恢复

| 属性 | 值 |
|------|-----|
| **需求ID** | FR-10 |
| **优先级** | P1-重要 |
| **描述** | 暂停取消后恢复到暂停前的状态继续运行 |
| **验收标准** | 1. 暂停时保存m_iPauseState; 2. 暂停取消后iState恢复为m_iPauseState; 3. 恢复后继续执行对应状态逻辑 |
| **关联状态** | ST_PAUSE |

#### FR-11: 故障恢复

| 属性 | 值 |
|------|-----|
| **需求ID** | FR-11 |
| **优先级** | P1-重要 |
| **描述** | 停止信号取消且VFD故障解除后, 从IDLE状态重新开始(不复位产量计数). 故障恢复后拍正气缸伸出(弹簧复位默认安全态) |
| **验收标准** | 1. i_bStop=FALSE AND i_bVfdAlarm=FALSE后iState->ST_IDLE; 2. q_dwProductionCount保持不变; 3. 所有驱动命令清零, q_bInfeedRetract=TRUE, q_bDischargeRetract=TRUE, q_bAlignExtend=TRUE(伸出), q_bAlignRetract=FALSE |
| **关联状态** | ST_FAULT |

#### FR-12: 手动模式

| 属性 | 值 |
|------|-----|
| **需求ID** | FR-12 |
| **优先级** | P0-必须 |
| **描述** | 自动模式未使能时, 所有驱动命令清零, 阻挡/出料气缸收回, **拍正气缸伸出(弹簧复位默认就绪)**, 状态归IDLE, 定时器复位 |
| **验收标准** | 1. i_bAutoMode=FALSE: 所有命令输出FALSE; 2. q_iState=0; 3. 定时器IN=FALSE; 4. 确认标志清零; 5. q_bAlignExtend=TRUE(伸出), q_bAlignRetract=FALSE; 6. q_bInfeedRetract=TRUE, q_bDischargeRetract=TRUE |
| **关联状态** | ST_IDLE |

#### FR-13: 工站选中

| 属性 | 值 |
|------|-----|
| **需求ID** | FR-13 |
| **优先级** | P1-重要 |
| **描述** | 仅当选中信号(i_bSelected)有效时, 才从IDLE进入READY, 允许进料 |
| **验收标准** | 1. i_bSelected=FALSE: 保持IDLE; 2. i_bSelected=TRUE AND i_bAutoMode=TRUE: IDLE->READY |
| **关联状态** | ST_IDLE, ST_READY |

#### FR-20: VFD故障响应

| 属性 | 值 |
|------|-----|
| **需求ID** | FR-20 |
| **优先级** | P0-必须 |
| **描述** | 当FB_1012反馈VFD故障(i_bVfdAlarm=TRUE)时, 状态机立即进入FAULT态, 马达命令清零, 拍正气缸伸出(弹簧复位安全态). VFD故障由FB_1012 V9.0.0检测并通过q_bVfdAlarm输出, OB1将其连接到FB_1014的i_bVfdAlarm输入 |
| **验收标准** | 1. i_bVfdAlarm=TRUE: 立即进入ST_FAULT; 2. q_bFwdCmd=FALSE, q_bRevCmd=FALSE, q_bSlowCmd=FALSE; 3. q_bAlignExtend=TRUE(伸出), q_bAlignRetract=FALSE; 4. 阻挡/出料气缸命令保持当前状态(不强制收回); 5. i_bVfdAlarm=FALSE AND i_bStop=FALSE后可恢复至IDLE |
| **关联状态** | 全部运行态 |

#### FR-22: 运行模式接口

| 属性 | 值 |
|------|-----|
| **需求ID** | FR-22 |
| **优先级** | P0-必须 |
| **描述** | 通过i_iMode(INT)输入选择输送机运行模式: 0=A进B出(传统单向), 1=B进B出(B侧双向, 默认), 2=A侧双向(预留). 模式决定进料/出料方向, 马达正反转映射, 气缸角色分配, 以及各工艺阶段的协作行为. 非法值(>2或<0)时行为等同于Mode 1(默认) |
| **验收标准** | 1. i_iMode=0: 按A进B出运行; 2. i_iMode=1(默认值): 按B进B出运行; 3. i_iMode=2: 预留, 按A侧双向运行; 4. i_iMode非法值: 等同于Mode 1; 5. 模式在IDLE态切换生效, 运行中切换不改变当前循环 |
| **关联状态** | 全部(影响INFEED/DISCHARGE/ALIGN态行为) |

### 2.2 气缸需求

#### FR-17: 拍正对齐功能(S2b ALIGN)

| 属性 | 值 |
|------|-----|
| **需求ID** | FR-17 |
| **优先级** | P0-必须 |
| **描述** | 入料完成后进入ALIGN状态, 执行拍正对齐步骤(S2b): (1)拍正气缸保持伸出(已在S2进料时伸出), B侧阻挡升起形成三面围住工件; (2)等待对齐延时+伸出到位确认; (3)拍正确认后**两侧阻挡均下降**(不干涉后续加工); (4)拍正气缸保持伸出(弹簧复位默认). 全部确认后进入PROCESSING. 拍正气缸的电磁阀取反由OB1中FB_1011的i_bExtendPolarity=TRUE处理, FB_1014无需NOT操作 |
| **验收标准** | 1. INFEED完成后进入ALIGN而非直接进入PROCESSING; 2. ALIGN态: B侧阻挡升起(q_bDischargeRetract=TRUE), 形成三面围住; 3. 拍正确认条件: i_bAlignIsExtended=TRUE AND tAlignDelay.Q=TRUE; 4. 拍正确认后: 两侧阻挡下降(q_bInfeedExtend=TRUE, q_bDischargeExtend=TRUE), 不干涉工件; 5. 拍正气缸保持伸出不收回(q_bAlignExtend=TRUE); 6. 全部确认后ALIGN->PROCESSING; 7. 任意到位信号丢失时停留在ALIGN态; 8. FB_1014不包含拍正电磁阀取反逻辑 |
| **关联状态** | ST_ALIGN |

#### FR-18: 气缸状态输入

| 属性 | 值 |
|------|-----|
| **需求ID** | FR-18 |
| **优先级** | P0-必须 |
| **描述** | FB_1014通过6个BOOL输入读取3个气缸的到位状态, 这些状态来自OB1中FB_1011实例的q_bIsExtended/q_bIsRetracted输出. 编排器依赖到位信号确认气缸动作完成, 消除盲操 |
| **验收标准** | 1. i_bInfeedIsExtended/i_bInfeedIsRetracted反映A侧阻挡气缸到位状态; 2. i_bAlignIsExtended/i_bAlignIsRetracted反映拍正气缸到位状态; 3. i_bDischargeIsExtended/i_bDischargeIsRetracted反映B侧出料气缸到位状态; 4. 气缸动作不依赖延时假设, 而依赖到位输入确认; 5. 超时检测由FB_1011内部处理, FB_1014不重复实现 |
| **关联状态** | ST_ALIGN, ST_INFEED, ST_DISCHARGE |

#### FR-19: 气缸命令输出

| 属性 | 值 |
|------|-----|
| **需求ID** | FR-19 |
| **优先级** | P0-必须 |
| **描述** | FB_1014通过6个BOOL输出向OB1中FB_1011实例发送伸出/收回命令. 这些命令连接到FB_1011的i_bExtend/i_bRetract输入. 编排器只决定"什么时候伸出/收回", 不关心电磁阀如何驱动. 拍正气缸(弹簧复位型)在IDLE/READY/COMPLETE/FAULT/Stop时默认伸出 |
| **验收标准** | 1. q_bInfeedExtend/q_bInfeedRetract控制A侧阻挡气缸; 2. q_bAlignExtend/q_bAlignRetract控制拍正气缸; 3. q_bDischargeExtend/q_bDischargeRetract控制B侧出料气缸; 4. 同一气缸的Extend和Retract不同时为TRUE; 5. 停止/故障/手动模式时: 阻挡/出料收回(q_bXxxRetract=TRUE), 拍正伸出(q_bAlignExtend=TRUE); 6. IDLE/READY/COMPLETE态拍正伸出就绪 |
| **关联状态** | 全部 |

### 2.3 马达需求

#### FR-06: 入料慢速控制

| 属性 | 值 |
|------|-----|
| **需求ID** | FR-06 |
| **优先级** | P1-重要 |
| **描述** | 入料过程中, 物料触达入料开始光电(X420)后切换为慢速, 避免物料冲击. 慢速命令输出至FB_1012. 拍正气缸在S2进料阶段保持伸出, 配合阻挡防止物料超位 |
| **验收标准** | 1. m_bStartConfirmed=FALSE时全速(方向命令=TRUE, q_bSlowCmd=FALSE); 2. m_bStartConfirmed=TRUE时慢速(方向命令=TRUE, q_bSlowCmd=TRUE); 3. 进入ALIGN态后复位慢速(q_bSlowCmd=FALSE); 4. 进料全程拍正气缸保持伸出(q_bAlignExtend=TRUE)防超位 |
| **关联状态** | ST_INFEED |

#### FR-07: 出料慢速模式

| 属性 | 值 |
|------|-----|
| **需求ID** | FR-07 |
| **优先级** | P1-重要 |
| **描述** | 出料过程中支持外部慢速模式控制(i_bSlowMode), 用于精确定位或易碎物料保护. 慢速命令输出至FB_1012. S4出料前拍正先伸出就位+A侧阻挡升起屏障 |
| **验收标准** | 1. i_bSlowMode=TRUE时q_bSlowCmd=TRUE; 2. i_bSlowMode=FALSE时全速出料(q_bSlowCmd=FALSE); 3. 出料前拍正已伸出就位且A侧阻挡已升起 |
| **关联状态** | ST_DISCHARGE |

#### FR-21: 马达命令输出

| 属性 | 值 |
|------|-----|
| **需求ID** | FR-21 |
| **优先级** | P0-必须 |
| **描述** | FB_1014通过3个BOOL输出向OB1中FB_1012实例发送方向和速度命令. 这些命令连接到FB_1012的i_bFwdCmd/i_bRevCmd/i_bSlowCmd输入. FB_1012负责方向互锁和VFD故障检测, FB_1014只决定运行方向和速度. 正反转语义随i_iMode变化: Mode 0反转=进料正转=出料, Mode 1正转=进料反转=出料 |
| **验收标准** | 1. q_bFwdCmd连接到FB_1012.i_bFwdCmd; 2. q_bRevCmd连接到FB_1012.i_bRevCmd; 3. q_bSlowCmd连接到FB_1012.i_bSlowCmd; 4. FB_1014不直接驱动物理IO; 5. 方向互锁由FB_1012保证, FB_1014逻辑上保证不同时输出正转和反转; 6. 正反转语义与i_iMode对应 |
| **关联状态** | ST_INFEED, ST_DISCHARGE |

### 2.4 握手需求

#### FR-04: 上下游握手

| 属性 | 值 |
|------|-----|
| **需求ID** | FR-04 |
| **优先级** | P0-必须 |
| **描述** | 与上下游设备通过握手信号协调物料流转: 回应上游可进料(q_yReplyUpstream), 回应下游可出料(q_yReplyDownstream). 握手方向语义与i_iMode无关, 始终表示"可进料/可出料" |
| **验收标准** | 1. IDLE/READY态且传感器确认后, q_yReplyUpstream=TRUE; 2. 加工完成后, q_yReplyDownstream=TRUE; 3. COMPLETE态复位q_yReplyDownstream |
| **关联状态** | ST_IDLE, ST_READY, ST_PROCESSING, ST_DISCHARGE, ST_COMPLETE |

### 2.5 诊断需求

#### FR-05: 光电位置检测与去抖

| 属性 | 值 |
|------|-----|
| **需求ID** | FR-05 |
| **优先级** | P0-必须 |
| **描述** | 3个光电传感器(X420/X421/X422)通过FB_TON去抖后确认物料位置, 去抖时间可配置(i_dDebounceMs). FB_TON的PT参数为DINT类型(扫描周期数), 补全Q/ET参数输出(LSP-903/LSP-906合规) |
| **验收标准** | 1. 传感器信号持续i_dDebounceMs后确认; 2. 3个传感器全部确认后m_bAllConfirmed=TRUE; 3. 去抖时间默认200ms; 4. 定时器调用不含DINT_TO_TIME, PT直传DINT, Q/ET通过=>接收 |
| **关联状态** | ST_INFEED, ST_READY |

#### FR-08: 入料/出料/对齐延时

| 属性 | 值 |
|------|-----|
| **需求ID** | FR-08 |
| **优先级** | P0-必须 |
| **描述** | 入料, 出料和对齐各有一个可配置延时定时器, 确保物料到位稳定后再切换状态. 定时器PT参数为DINT类型, 补全Q/ET参数输出(LSP-903/LSP-906合规) |
| **验收标准** | 1. 入料延时: m_bAllConfirmed AND tInfeedDelay.Q -> ALIGN; 2. 对齐延时: tAlignDelay.Q作为拍正确认条件之一; 3. 出料延时: tDischargeDelay.Q -> COMPLETE; 4. 延时参数i_dInfeedDelayMs/i_dDischargeDelayMs/i_dAlignDelayMs可配, 默认1000/1000/500ms; 5. 定时器调用不含DINT_TO_TIME, PT直传DINT, Q/ET通过=>接收 |
| **关联状态** | ST_INFEED, ST_ALIGN, ST_DISCHARGE |

#### FR-14: 加工完成信号(S3加工)

| 属性 | 值 |
|------|-----|
| **需求ID** | FR-14 |
| **优先级** | P0-必须 |
| **描述** | PROCESSING态等待外部加工完成信号(i_bProcessDone), 收到后切换到DISCHARGE态. S3加工阶段两侧阻挡气缸均下降(q_bInfeedExtend=TRUE, q_bDischargeExtend=TRUE), 不干涉工件加工动作. 拍正气缸保持伸出(弹簧复位默认态) |
| **验收标准** | 1. i_bProcessDone=FALSE: 保持PROCESSING; 2. i_bProcessDone=TRUE: PROCESSING->DISCHARGE, q_yReplyDownstream=TRUE; 3. PROCESSING态全程: 两侧阻挡下降(q_bInfeedExtend=TRUE, q_bDischargeExtend=TRUE), 拍正保持伸出(q_bAlignExtend=TRUE) |
| **关联状态** | ST_PROCESSING |

#### FR-15: 产量计数

| 属性 | 值 |
|------|-----|
| **需求ID** | FR-15 |
| **优先级** | P2-一般 |
| **描述** | 每完成一次完整循环(进料->对齐->加工->出料), 累计产量计数加1 |
| **验收标准** | 1. ST_COMPLETE态: q_dwProductionCount+1; 2. 计数器类型DWORD, 支持大产量; 3. 手动模式/故障不复位计数 |
| **关联状态** | ST_COMPLETE |

#### FR-16: 下游中断报警

| 属性 | 值 |
|------|-----|
| **需求ID** | FR-16 |
| **优先级** | P1-重要 |
| **描述** | 进料过程中若下游请求信号消失, 置位中断报警暂存标志, 下游请求恢复后自动清除 |
| **验收标准** | 1. 进料中(i_xInfeedStart=TRUE, q_bInfeedActive=TRUE)且i_bDownstreamReq=FALSE: q_bIntAlarmMem=TRUE; 2. i_bDownstreamReq=TRUE: q_bIntAlarmMem=FALSE; 3. PROCESSING态也清除报警 |
| **关联状态** | ST_INFEED, ST_PROCESSING |

---

## 3. 接口需求汇总

### 3.1 输入信号需求

| 类别 | 数量 | 信号列表 |
|------|:----:|---------|
| 控制信号 | 10 | i_bAutoMode, i_bUpstreamReq, i_bDownstreamReq, i_bSelected, i_bProcessDone, i_bStop, i_bPause, i_bSlowMode, i_bVfdAlarm, **i_iMode** |
| 延时参数 | 4 | i_dInfeedDelayMs, i_dDischargeDelayMs, i_dAlignDelayMs, i_dDebounceMs |
| 传感器信号 | 3 | i_xInfeedStart, i_xPos1, i_xPos2 |
| 气缸状态输入 | 6 | i_bInfeedIsExtended, i_bInfeedIsRetracted, i_bAlignIsExtended, i_bAlignIsRetracted, i_bDischargeIsExtended, i_bDischargeIsRetracted |

### 3.2 输出信号需求

| 类别 | 数量 | 信号列表 |
|------|:----:|---------|
| 气缸命令输出 | 6 | q_bInfeedExtend, q_bInfeedRetract, q_bAlignExtend, q_bAlignRetract, q_bDischargeExtend, q_bDischargeRetract |
| 马达命令输出 | 3 | q_bFwdCmd, q_bRevCmd, q_bSlowCmd |
| 握手输出 | 2 | q_yReplyUpstream, q_yReplyDownstream |
| 诊断输出 | 4 | q_iState, q_dwProductionCount, q_bInfeedActive, q_bIntAlarmMem |

### 3.3 接口统计对比

| 项目 | V5.0.0 | V6.0.0 | 变化 |
|------|:------:|:------:|:----:|
| VAR_INPUT (控制) | 9 | 10 | +1(i_iMode) |
| VAR_INPUT (参数) | 4 | 4 | 不变 |
| VAR_INPUT (传感器) | 3 | 3 | 不变 |
| VAR_INPUT (气缸状态) | 6 | 6 | 不变 |
| VAR_IN_OUT (气缸结构体) | 0 | 0 | 不变 |
| VAR_OUTPUT (气缸命令) | 6 | 6 | 不变 |
| VAR_OUTPUT (马达) | 3 | 3 | 不变 |
| VAR_OUTPUT (握手) | 2 | 2 | 不变 |
| VAR_OUTPUT (诊断) | 4 | 4 | 不变 |
| **总计** | **37** | **38** | **+1** |

### 3.4 i_iMode接口详细定义

| 属性 | 值 |
|------|-----|
| **信号名** | i_iMode |
| **类型** | INT |
| **方向** | VAR_INPUT |
| **默认值** | 1 |
| **取值范围** | 0, 1, 2 |

| 值 | 名称 | 进料方向 | 出料方向 | 进料马达 | 出料马达 | 状态 |
|:--:|------|---------|---------|:-------:|:-------:|:----:|
| 0 | A进B出 | A→B | A→B | 反转(Rev) | 正转(Fwd) | 支持 |
| 1 | B进B出 | B→A | A→B | 正转(Fwd) | 反转(Rev) | **默认** |
| 2 | A侧双向 | A→B | B→A | 反转(Rev) | 正转(Fwd) | 预留 |

---

## 4. 组件复用需求

### 4.1 必须复用组件

| 组件 | 最低版本 | 复用方式 | 说明 |
|------|:-------:|---------|------|
| **FB_1011_CylinderControl** | **V9.0.0** | OB1实例化, 3个实例 | 气缸执行控制: 伸出/收回命令->传感器消抖->极性映射->电磁阀输出->到位检测->超时保护. V9.0.0回归扁平BOOL接口, 移除ST_Cylinder依赖, 支持i_bExtendPolarity极性取反 |
| **FB_1012_ConveyorMotor** | **V9.0.0** | OB1实例化, 1个实例 | 电机执行控制: 方向命令->VFD故障检测->方向互锁->慢速修饰->实际输出. V9.0.0回归扁平BOOL接口, q_bVfdAlarm反馈VFD故障状态 |
| **FB_TON** | - | FB_1014内部实例 | 定时延时和传感器去抖, PT为DINT类型, Q/ET通过=>接收 |

### 4.2 OB1实例化要求

OB1中必须实例化以下组件并完成信号连线:

| 实例 | 类型 | 数量 | 关键配置 |
|------|------|:----:|---------|
| fbInfeedCyl | FB_1011 V9.0.0 | 1 | i_bExtendPolarity=FALSE(阻挡气缸, 正常极性) |
| fbAlignCyl | FB_1011 V9.0.0 | 1 | i_bExtendPolarity=TRUE(拍正气缸, 弹簧复位, 极性取反, 内部处理电磁阀NOT) |
| fbDischargeCyl | FB_1011 V9.0.0 | 1 | i_bExtendPolarity=FALSE(出料气缸, 正常极性) |
| fbConveyorMotor | FB_1012 V9.0.0 | 1 | i_iCtrlMode=0(端子控制模式) |

### 4.3 信号连线协议

```
OB1信号连线:

FB_1014输出 --> FB_1011输入:
  fbStationConv.q_bInfeedExtend    --> fbInfeedCyl.i_bExtend
  fbStationConv.q_bInfeedRetract   --> fbInfeedCyl.i_bRetract
  fbStationConv.q_bAlignExtend     --> fbAlignCyl.i_bExtend
  fbStationConv.q_bAlignRetract    --> fbAlignCyl.i_bRetract
  fbStationConv.q_bDischargeExtend --> fbDischargeCyl.i_bExtend
  fbStationConv.q_bDischargeRetract--> fbDischargeCyl.i_bRetract

FB_1011输出 --> FB_1014输入:
  fbInfeedCyl.q_bIsExtended    --> fbStationConv.i_bInfeedIsExtended
  fbInfeedCyl.q_bIsRetracted   --> fbStationConv.i_bInfeedIsRetracted
  fbAlignCyl.q_bIsExtended     --> fbStationConv.i_bAlignIsExtended
  fbAlignCyl.q_bIsRetracted    --> fbStationConv.i_bAlignIsRetracted
  fbDischargeCyl.q_bIsExtended --> fbStationConv.i_bDischargeIsExtended
  fbDischargeCyl.q_bIsRetracted--> fbStationConv.i_bDischargeIsRetracted

FB_1014输出 --> FB_1012输入:
  fbStationConv.q_bFwdCmd  --> fbConveyorMotor.i_bFwdCmd
  fbStationConv.q_bRevCmd  --> fbConveyorMotor.i_bRevCmd
  fbStationConv.q_bSlowCmd --> fbConveyorMotor.i_bSlowCmd

FB_1012输出 --> FB_1014输入:
  fbConveyorMotor.q_bVfdAlarm --> fbStationConv.i_bVfdAlarm

运行模式配置(OB1):
  fbStationConv.i_iMode := 1   (* 默认B进B出模式 *)

FB_1011输出 --> 物理IO(OB1映射):
  fbInfeedCyl.q_bSolenoid    --> A侧阻挡气缸电磁阀
  fbAlignCyl.q_bSolenoid     --> 拍正气缸电磁阀(极性已取反, 无需NOT)
  fbDischargeCyl.q_bSolenoid --> B侧出料气缸电磁阀

FB_1012输出 --> 物理IO(OB1映射):
  fbConveyorMotor.q_bFwdOut  --> VFD正转端子
  fbConveyorMotor.q_bRevOut  --> VFD反转端子
  fbConveyorMotor.q_bSlowOut --> VFD慢速端子

物理IO --> FB_1011输入(OB1映射):
  A侧阻挡气缸伸出位磁环 --> fbInfeedCyl.i_bExtendedPos
  A侧阻挡气缸收回位磁环 --> fbInfeedCyl.i_bRetractedPos
  拍正气缸物理伸出位磁环 --> fbAlignCyl.i_bExtendedPos
  拍正气缸物理收回位磁环 --> fbAlignCyl.i_bRetractedPos
  B侧出料气缸伸出位磁环 --> fbDischargeCyl.i_bExtendedPos
  B侧出料气缸收回位磁环 --> fbDischargeCyl.i_bRetractedPos

物理IO --> FB_1012输入(OB1映射):
  VFD故障信号 --> fbConveyorMotor.i_bVfdFault
```

### 4.4 禁止复用组件

| 组件 | 原因 |
|------|------|
| ST_Cylinder | V9.0.0已废弃, FB_1011回归扁平BOOL接口 |
| ST_ConveyorMotor | V9.0.0已废弃, FB_1012回归扁平BOOL接口 |

---

## 5. 非功能需求

### NFR-01: 响应时间

| 属性 | 值 |
|------|-----|
| **需求ID** | NFR-01 |
| **描述** | 状态切换在1个PLC扫描周期内完成, 无累积延时 |
| **验收标准** | 状态机CASE分支执行时间 < 1ms (典型PLC周期10ms) |

### NFR-02: 信号去抖可靠性

| 属性 | 值 |
|------|-----|
| **需求ID** | NFR-02 |
| **描述** | 光电传感器去抖延时可配置, 默认200ms, 防止误触发. FB_TON的PT参数为DINT类型(扫描周期数), Q/ET参数完整输出 |
| **验收标准** | 信号持续 < i_dDebounceMs 不触发确认; 持续 >= i_dDebounceMs 触发确认 |

### NFR-03: 正反转互锁

| 属性 | 值 |
|------|-----|
| **需求ID** | NFR-03 |
| **描述** | 正转和反转命令不可同时为TRUE, 防止电机损坏. 逻辑互锁由FB_1014保证(不同时输出), 物理互锁由FB_1012保证(Fwd优先) |
| **验收标准** | 任意时刻 q_bFwdCmd AND q_bRevCmd = FALSE |

### NFR-04: 气缸安全默认态

| 属性 | 值 |
|------|-----|
| **需求ID** | NFR-04 |
| **描述** | 阻挡/出料气缸默认抬起(阻挡), 仅在需要放行时放下. **拍正气缸为弹簧复位单作用气缸, 失电默认伸出(物理安全态)**, 因此IDLE/READY/COMPLETE态拍正伸出就绪, FAULT/Stop/VFD故障时拍正伸出. 仅在ALIGN拍正确认后两侧阻挡升降等特定工艺步骤中短暂收回拍正 |
| **验收标准** | IDLE/READY/COMPLETE态: q_bInfeedRetract=TRUE(抬起), q_bDischargeRetract=TRUE(抬起), q_bAlignExtend=TRUE(伸出就绪); FAULT/Stop/VFD故障态: q_bAlignExtend=TRUE(伸出, 弹簧复位安全态); 仅ALIGN和DISCHARGE特定子步骤中拍正可能收回 |
| **关联变更** | V5.0.0拍正默认收回 → V6.0.0拍正默认伸出(匹配弹簧复位物理特性) |

### NFR-05: 可配置性

| 属性 | 值 |
|------|-----|
| **需求ID** | NFR-05 |
| **描述** | 关键延时参数通过VAR_INPUT配置, 无硬编码延时值. 运行模式通过i_iMode配置. 气缸超时参数通过FB_1011的i_iTimeoutMs配置(在OB1中设置) |
| **验收标准** | i_dInfeedDelayMs, i_dDischargeDelayMs, i_dAlignDelayMs, i_dDebounceMs 均为VAR_INPUT, 有合理默认值; i_iMode为VAR_INPUT, 默认值1; FB_1011的i_iTimeoutMs在OB1中配置 |

### NFR-06: LSP-905合规

| 属性 | 值 |
|------|-----|
| **需求ID** | NFR-06 |
| **描述** | 代码结构遵循LSP-905 SCL编程规范: 命名规范, 代码结构, 无METHOD语法 |
| **验收标准** | 1. 变量命名符合i_/q_/m_/s_/fb_/t_前缀规范; 2. 无METHOD语法(Siemens LSP插件限制); 3. 状态机使用CASE结构 |

### NFR-07: LSP-904合规

| 属性 | 值 |
|------|-----|
| **需求ID** | NFR-07 |
| **描述** | 注释遵循LSP-904 SCL注释规范: 英文半角标点, 禁止中文标点, 禁止嵌套注释 |
| **验收标准** | 1. 注释使用英文半角标点; 2. 无中文逗号/句号/冒号等; 3. 无嵌套(* (* *) *)注释 |

### NFR-08: LSP-903合规

| 属性 | 值 |
|------|-----|
| **需求ID** | NFR-08 |
| **描述** | 定时器使用遵循LSP-903定时器使用规范: PT为DINT类型, 禁止DINT_TO_TIME转换, Q/ET通过=>参数接收 |
| **验收标准** | 1. FB_TON调用: PT直传DINT, 无DINT_TO_TIME; 2. Q/ET通过=>接收, 不省略; 3. 定时器IN在状态退出时复位 |

### NFR-09: LSP-906合规

| 属性 | 值 |
|------|-----|
| **需求ID** | NFR-09 |
| **描述** | 错误预防遵循LSP-906规则: 完整的参数传递, 无隐式类型转换, 防御性编程 |
| **验收标准** | 1. 无隐式类型转换; 2. 定时器参数完整传递; 3. 状态机default分支处理未知状态; 4. i_iMode非法值回退到默认Mode 1 |

---

## 6. Breaking Change影响分析

### 6.1 V5.0.0接口破坏性变更(历史)

| 变更类型 | V4.3.0接口 | V5.0.0接口 | 迁移动作 |
|---------|-----------|-----------|---------|
| 删除 | io_stInfeedCyl (VAR_IN_OUT ST_Cylinder) | - | 删除VAR_IN_OUT, 改用i_bInfeedIsExtended等6个BOOL输入 |
| 删除 | io_stAlignCyl (VAR_IN_OUT ST_Cylinder) | - | 删除VAR_IN_OUT, 改用i_bAlignIsExtended等6个BOOL输入 |
| 删除 | io_stDischargeCyl (VAR_IN_OUT ST_Cylinder) | - | 删除VAR_IN_OUT, 改用i_bDischargeIsExtended等6个BOOL输入 |
| 删除 | q_yInfeedSolenoid (BOOL) | - | 电磁阀由OB1中FB_1011.q_bSolenoid直接输出 |
| 删除 | q_yAlignSolenoid (BOOL) | - | 电磁阀由OB1中FB_1011.q_bSolenoid直接输出(极性取反由FB_1011处理) |
| 删除 | q_yDischargeSolenoid (BOOL) | - | 电磁阀由OB1中FB_1011.q_bSolenoid直接输出 |
| 重命名 | q_yFwdCmd (BOOL) | q_bFwdCmd (BOOL) | 从直接硬件输出改为命令到FB_1012 |
| 重命名 | q_yRevCmd (BOOL) | q_bRevCmd (BOOL) | 从直接硬件输出改为命令到FB_1012 |
| 重命名 | q_ySlowCmd (BOOL) | q_bSlowCmd (BOOL) | 从直接硬件输出改为命令到FB_1012 |
| 新增 | - | i_bVfdAlarm (BOOL) | 从FB_1012 q_bVfdAlarm连接 |
| 新增 | - | i_bInfeedIsExtended等6个BOOL | 从FB_1011 q_bIsExtended/q_bIsRetracted连接 |
| 新增 | - | q_bInfeedExtend等6个BOOL | 连接到FB_1011 i_bExtend/i_bRetract |

### 6.2 V6.0.0接口破坏性变更

| 变更类型 | V5.0.0接口 | V6.0.0接口 | 迁移动作 |
|---------|-----------|-----------|---------|
| 新增 | - | i_iMode (INT) | OB1中配置: fbStationConv.i_iMode := 1(默认B进B出) |

### 6.3 V6.0.0行为变更

| 行为 | V5.0.0 | V6.0.0 | 影响 |
|------|:------:|:------:|------|
| 运行模式 | 无选择, 固定A进B出 | i_iMode可选, 默认B进B出 | OB1需配置i_iMode, 马达方向语义随Mode改变 |
| IDLE态拍正 | 收回(q_bAlignRetract=TRUE) | 伸出(q_bAlignExtend=TRUE) | 拍正气缸失电默认伸出=物理安全态 |
| READY态拍正 | 收回(q_bAlignRetract=TRUE) | 伸出(q_bAlignExtend=TRUE) | 准备进料时拍正已就位 |
| COMPLETE态拍正 | 收回(q_bAlignRetract=TRUE) | 伸出(q_bAlignExtend=TRUE) | 循环结束回到默认安全态 |
| FAULT态拍正 | 收回(q_bAlignRetract=TRUE) | 伸出(q_bAlignExtend=TRUE) | 故障时弹簧复位=默认伸出 |
| Stop态拍正 | 收回(q_bAlignRetract=TRUE) | 伸出(q_bAlignExtend=TRUE) | 停止时弹簧复位=默认伸出 |
| VFD故障态拍正 | 收回(q_bAlignRetract=TRUE) | 伸出(q_bAlignExtend=TRUE) | VFD故障时弹簧复位=默认伸出 |
| S2进料拍正 | 不参与 | 伸出配合阻挡防超位 | 进料更安全, 防止物料冲出 |
| S2b ALIGN阻挡 | 仅A侧阻挡下降 | B侧阻挡升起三面围住, 拍正后两侧均下降 | 拍正精度提高, 三面围住确保对齐 |
| S3加工气缸 | 气缸状态不变 | 两侧阻挡下降不干涉工件 | 避免阻挡干涉加工动作 |
| S4出料前 | 直接出料 | 拍正先伸出+A侧阻挡升起屏障, 再出料 | 出料前预定位, 防止工件偏移 |
| 手动模式拍正 | q_bAlignExtend=FALSE | q_bAlignExtend=TRUE | 手动模式拍正默认伸出就绪 |

### 6.4 V5.0.0→V6.0.0 OB1迁移清单

从V5.0.0升级到V6.0.0时, OB1调用代码必须进行以下修改:

1. **新增i_iMode配置**: 在OB1中为fbStationConv实例添加 `fbStationConv.i_iMode := 1` (默认B进B出模式)
2. **确认拍正气缸极性**: fbAlignCyl的i_bExtendPolarity=TRUE不变, 弹簧复位取反逻辑由FB_1011内部处理
3. **无需修改信号连线**: V5.0.0→V6.0.0的FB_1014<->FB_1011/FB_1012信号连线无变化, 仅新增i_iMode输入
4. **无需修改物理IO映射**: 物理IO映射无变化
5. **行为验证**: 确认IDLE/READY/COMPLETE态拍正伸出, FAULT/Stop态拍正伸出

### 6.5 V5.0.0→V6.0.0 OB1迁移清单(从V4.3.0升级者)

从V4.3.0升级到V6.0.0时, 需同时完成V5.0.0和V6.0.0的迁移动作:

1. **完成V5.0.0迁移**: 按照V5.0.0迁移清单完成FB_1011/FB_1012实例化, 删除ST_Cylinder, 完成信号连线
2. **新增i_iMode配置**: `fbStationConv.i_iMode := 1`
3. **行为验证**: 确认V6.0.0新增的拍正安全态和工艺阶段行为

---

## 7. 工艺阶段行为总结

### 7.1 各阶段气缸状态(默认Mode 1: B进B出)

| 阶段 | A侧阻挡 | 拍正气缸 | B侧出料气缸 | 马达方向 |
|------|:------:|:------:|:---------:|:-------:|
| IDLE | 收回(抬起) | **伸出(就绪)** | 收回(抬起) | 停止 |
| READY | 收回(抬起) | **伸出(就绪)** | 收回(抬起) | 停止 |
| INFEED(S2) | 收回(抬起) | **伸出(防超位)** | 放下(进料通道) | 正转(Fwd) |
| ALIGN(S2b) | 放下(围住)→放下(不干涉) | **伸出(拍正)**→伸出 | 收回(抬起,围住)→放下(不干涉) | 停止 |
| PROCESSING(S3) | 放下(不干涉) | **伸出(默认)** | 放下(不干涉) | 停止 |
| DISCHARGE(S4) | 收回(抬起,屏障)→放下(出料通道) | **伸出(预就位)**→伸出 | 收回(抬起)→放下(出料通道) | 反转(Rev) |
| COMPLETE | 收回(抬起) | **伸出(就绪)** | 收回(抬起) | 停止 |
| FAULT/Stop | 收回(抬起) | **伸出(安全态)** | 收回(抬起) | 停止 |

### 7.2 各阶段气缸状态(Mode 0: A进B出)

| 阶段 | A侧阻挡 | 拍正气缸 | B侧出料气缸 | 马达方向 |
|------|:------:|:------:|:---------:|:-------:|
| IDLE | 收回(抬起) | **伸出(就绪)** | 收回(抬起) | 停止 |
| READY | 收回(抬起) | **伸出(就绪)** | 收回(抬起) | 停止 |
| INFEED(S2) | 收回(抬起) | **伸出(防超位)** | 放下(进料通道) | 反转(Rev) |
| ALIGN(S2b) | 放下(围住)→放下(不干涉) | **伸出(拍正)**→伸出 | 收回(抬起,围住)→放下(不干涉) | 停止 |
| PROCESSING(S3) | 放下(不干涉) | **伸出(默认)** | 放下(不干涉) | 停止 |
| DISCHARGE(S4) | 放下(出料通道) | **伸出(预就位)**→伸出 | 收回(抬起) | 正转(Fwd) |
| COMPLETE | 收回(抬起) | **伸出(就绪)** | 收回(抬起) | 停止 |
| FAULT/Stop | 收回(抬起) | **伸出(安全态)** | 收回(抬起) | 停止 |

---

## 8. 关联文档

| 文档 | 路径 | 版本 |
|------|------|:----:|
| IFC | 接口文档_IFC-FB1014-StationConveyor-V6.0.0.md | V6.0.0 |
| DSN | 详细设计说明书_DSN-FB1014-StationConveyor-V6.0.0.md | V6.0.0 |
| PFL | 工艺流程_PFL-FB1014-StationConveyor-V6.0.0.md | V6.0.0 |
| FB_1011 IFC | ../FB_1011_CylinderControl/PRD/接口文档_IFC-FB1011-CylinderControl-V9.0.0.md | V9.0.0 |
| FB_1012 IFC | ../FB_1012_ConveyorMotor/PRD/接口文档_IFC-FB1012-ConveyorMotor-V9.0.0.md | V9.0.0 |
| FB_TON | ../../timer/FB_TON.scl | - |
| LSP-905 | 905_SCL编程规范_LSP-V1.0.2.md | V1.0.2 |
| LSP-904 | 904_SCL注释规范_LSP-V1.2.0.md | V1.2.0 |
| LSP-903 | 903_定时器使用规范_LSP-V1.0.0.md | V1.0.0 |
| LSP-906 | 906_错误预防规则_LSP-V1.0.0.md | V1.0.0 |